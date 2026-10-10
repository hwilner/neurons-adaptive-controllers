"""Synthetic, file-free tests for the retained model utilities."""

import unittest

import numpy as np

from src.control_models import (
    OptimalController,
    StaticBaseline,
    compare_models,
    preprocess_spike_train,
)
from tools.check_public_boundary import DOI_PATTERN


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

    def test_doi_pattern_avoids_common_word_false_positive(self) -> None:
        """The public-boundary pattern matches identifiers, not ordinary words."""
        self.assertIsNone(DOI_PATTERN.search("undoing a calculation"))
        identifier = "10." + "1234/example.identifier"
        self.assertIsNotNone(DOI_PATTERN.search(identifier))


if __name__ == "__main__":
    unittest.main()
