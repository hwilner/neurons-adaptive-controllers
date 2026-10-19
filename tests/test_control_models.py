"""Synthetic, file-free tests for the retained model utilities."""

import unittest

import numpy as np
from numpy.typing import NDArray

from src import control_models
from src.control_models import (
    OptimalController,
    PIDController,
    StaticBaseline,
    _r2_score,
    compare_models,
    preprocess_spike_train,
)
from tools.check_public_boundary import DOI_PATTERN


# A Gaussian window this narrow underflows to a single unit bin, so the
# smoothing step becomes the identity. Using it lets a test inspect the binning
# on its own instead of the binned rate smeared across neighbouring bins.
DELTA_SIGMA = 0.01


def _mixed_series(length: int) -> NDArray[np.float64]:
    """Return a deterministic series without an exact low-order recurrence.

    A single sinusoid satisfies a second-order linear recurrence, so its lagged
    design matrix stays low-rank however many values are supplied. Combining
    incommensurate frequencies with a ramp keeps the design matrix full rank,
    which is what an identifiability test needs.

    Args:
        length: Number of values to generate.

    Returns:
        A one-dimensional array of `length` values.
    """
    index = np.linspace(0.0, 1.0, length)
    return np.sin(index * 4.0 * np.pi) + 0.5 * np.cos(index * 9.0 * np.pi) + index


class ControlModelsTest(unittest.TestCase):
    """Verify public behavior using only in-memory synthetic inputs."""

    def test_preprocess_returns_matching_time_and_rate_arrays(self) -> None:
        """Binning a synthetic event sequence returns aligned arrays."""
        time, rate = preprocess_spike_train([0.05, 0.15, 0.45], duration=1.0, bin_size=0.1)
        self.assertEqual(time.shape, rate.shape)
        self.assertEqual(len(time), 10)
        self.assertTrue(np.all(np.isfinite(rate)))

    def test_preprocess_empty_event_sequence_returns_zero_rate(self) -> None:
        """An empty synthetic event sequence bins to a finite zero rate series."""
        duration, bin_size, sigma = 2.0, 0.2, 1.5
        time, rate = preprocess_spike_train([], duration=duration, bin_size=bin_size, sigma=sigma)
        self.assertEqual(time.shape, rate.shape)
        self.assertEqual(len(time), int(duration / bin_size))
        self.assertTrue(np.all(np.isfinite(rate)))
        self.assertTrue(np.all(rate == 0.0))

    def test_preprocess_rejects_events_outside_duration(self) -> None:
        """Synthetic events outside the stated duration are rejected."""
        with self.assertRaises(ValueError):
            preprocess_spike_train([-0.1, 0.5], duration=1.0, bin_size=0.1)
        with self.assertRaises(ValueError):
            preprocess_spike_train([0.5, 1.1], duration=1.0, bin_size=0.1)

    def test_preprocess_rate_uses_the_width_of_the_bin_holding_the_event(self) -> None:
        """A rate is measured over the interval its own bin actually covers."""
        # The bins tile [0, 1.0] with widths 0.4, 0.4, and 0.2, so an event at
        # 0.9 belongs to the third bin, whose interval is 0.2 s wide. Dividing
        # by the requested width instead would report 2.5 rather than 5.0.
        time, rate = preprocess_spike_train(
            [0.9], duration=1.0, bin_size=0.4, sigma=DELTA_SIGMA
        )
        self.assertEqual(len(time), 3)
        self.assertAlmostEqual(time[2], 0.8)
        self.assertAlmostEqual(rate[2], 1.0 / 0.2)
        self.assertAlmostEqual(rate[0], 0.0)
        self.assertAlmostEqual(rate[1], 0.0)

    def test_preprocess_keeps_every_bin_when_the_duration_divides_evenly(self) -> None:
        """A duration that is a multiple of the bin width keeps all of its bins."""
        # 0.3 / 0.1 evaluates to 2.9999999999999996 in binary floating point, so
        # truncating that count would silently drop the third bin.
        time, rate = preprocess_spike_train(
            [0.25], duration=0.3, bin_size=0.1, sigma=DELTA_SIGMA
        )
        self.assertEqual(len(time), 3)
        self.assertAlmostEqual(rate[2], 1.0 / 0.1)

    def test_preprocess_counts_an_event_in_the_final_partial_bin(self) -> None:
        """An event near the duration is counted in the bin that contains it."""
        # The bins tile [0, 1.0] with widths 0.6 and 0.4, so an event at 0.99
        # belongs to the second bin, whose interval is 0.4 s wide.
        time, rate = preprocess_spike_train(
            [0.99], duration=1.0, bin_size=0.6, sigma=DELTA_SIGMA
        )
        self.assertEqual(len(time), 2)
        self.assertAlmostEqual(time[1], 0.6)
        self.assertAlmostEqual(rate[1], 1.0 / 0.4)

    def test_history_model_predicts_after_fit(self) -> None:
        """A fitted model accepts a history with the configured length."""
        series = np.linspace(0.0, 1.0, 40)
        model = OptimalController(history_length=4)
        model.fit(series)
        prediction = model.predict(series[-4:])
        self.assertTrue(np.isfinite(prediction))

    def test_short_history_is_rejected(self) -> None:
        """Prediction rejects histories that do not match the configured length."""
        model = OptimalController(history_length=3)
        model.fit(np.linspace(0.0, 1.0, 24))
        with self.assertRaises(ValueError):
            model.predict([0.0, 1.0])

    def test_unfitted_model_prediction_is_rejected(self) -> None:
        """Prediction before fitting is rejected at the configured history length."""
        model = OptimalController(history_length=4)
        with self.assertRaises(ValueError):
            model.predict([0.5, 0.6, 0.7, 0.8])

    def test_history_fit_rejects_a_series_too_short_to_identify_the_solve(self) -> None:
        """A rank-deficient fit is rejected instead of reported as a perfect score."""
        # Five lags and an intercept need six training rows, and the
        # chronological split keeps two values aside, so ten values cannot
        # identify the solve. The rank-deficient solve used to return a
        # held-out R-squared of exactly 1.0, which was an artifact of the
        # minimum-norm convention rather than a property of the model.
        model = OptimalController(history_length=5)
        with self.assertRaises(ValueError):
            model.fit(_mixed_series(10))

    def test_history_fit_accepts_the_shortest_series_that_identifies_the_solve(self) -> None:
        """The shortest identifying series fits, and one value fewer is rejected."""
        for history_length in range(1, 13):
            minimum_length = control_models._minimum_series_length(history_length)
            series = _mixed_series(minimum_length)
            result = OptimalController(history_length=history_length).fit(series)
            self.assertEqual(len(result["weights"]), history_length)
            self.assertTrue(np.all(np.isfinite(result["weights"])))
            with self.assertRaises(ValueError):
                OptimalController(history_length=history_length).fit(series[:-1])

    def test_minimum_series_length_always_identifies_the_training_split(self) -> None:
        """The shortest series always leaves enough training rows for the fit."""
        for history_length in range(1, 13):
            n_pairs = control_models._minimum_series_length(history_length) - history_length
            n_train = max(2, int(control_models.TRAINING_FRACTION * n_pairs))
            self.assertGreaterEqual(n_train, history_length + 1)
            self.assertGreaterEqual(n_pairs - n_train, 2)

    def test_comparison_rejects_a_series_too_short_for_every_model(self) -> None:
        """The comparison helper rejects a series shorter than its models need."""
        with self.assertRaises(ValueError):
            compare_models(np.linspace(0.0, 1.0, 10))

    def test_pid_rejects_nonfinite_setpoint(self) -> None:
        """PID fitting rejects a non-finite setpoint on a finite synthetic series."""
        series = np.linspace(0.0, 1.0, 12)
        with self.assertRaises(ValueError):
            PIDController().fit(series, setpoint=np.nan)

    def test_comparison_returns_all_retained_models(self) -> None:
        """The comparison helper produces a result mapping for each model."""
        series = np.sin(np.linspace(0.0, 4.0 * np.pi, 80)) + 1.0
        results = compare_models(series)
        self.assertEqual(
            set(results),
            {"Optimal Controller", "AR Model", "PID Controller", "Static Baseline"},
        )
        self.assertTrue(all("n_params" in result or "error" in result for result in results.values()))

    def test_baseline_rejects_nonfinite_input(self) -> None:
        """The baseline validates non-finite synthetic inputs."""
        with self.assertRaises(ValueError):
            StaticBaseline().fit([0.0, 1.0, np.nan, 2.0, 3.0])

    def test_r2_score_is_nan_for_constant_target(self) -> None:
        """A constant target series makes the score undefined, reported as nan."""
        # Constant targets have zero variance, so the total sum of squares is
        # zero and the coefficient of determination is undefined; predictions
        # are constant at a different level so the residual sum is non-zero and
        # the nan cannot arise from a perfect fit.
        targets = np.full(6, 2.5)
        predictions = np.full(6, 1.0)
        self.assertTrue(np.isnan(_r2_score(targets, predictions)))

    def test_doi_pattern_avoids_common_word_false_positive(self) -> None:
        """The public-boundary pattern matches identifiers, not ordinary words."""
        self.assertIsNone(DOI_PATTERN.search("undoing a calculation"))
        identifier = "10." + "1234/example.identifier"
        self.assertIsNotNone(DOI_PATTERN.search(identifier))


if __name__ == "__main__":
    unittest.main()
