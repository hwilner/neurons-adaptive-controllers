"""Data-free controller-style models for one-dimensional time series.

The module contains reusable numerical utilities only. It performs no data
loading, network access, or output-file creation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float64]


def _as_finite_series(
    values: NDArray[np.floating[Any]] | list[float],
    *,
    minimum_length: int,
    name: str,
) -> FloatArray:
    """Validate and normalize a one-dimensional numeric series.

    Args:
        values: Values to validate.
        minimum_length: Smallest acceptable number of values.
        name: Name used in validation messages.

    Returns:
        A one-dimensional floating-point array.

    Raises:
        ValueError: If the input is not one-dimensional, is too short, or has
            non-finite values.
    """
    series = np.asarray(values, dtype=float)
    if series.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if series.size < minimum_length:
        raise ValueError(f"{name} must contain at least {minimum_length} values.")
    if not np.all(np.isfinite(series)):
        raise ValueError(f"{name} must contain only finite values.")
    return series


def _r2_score(targets: FloatArray, predictions: FloatArray) -> float:
    """Calculate a coefficient of determination without external dependencies.

    Args:
        targets: Observed values.
        predictions: Values predicted for the same positions.

    Returns:
        The coefficient of determination, or `nan` when it is undefined.
    """
    residual_sum = float(np.sum((targets - predictions) ** 2))
    total_sum = float(np.sum((targets - np.mean(targets)) ** 2))
    if total_sum == 0.0:
        return float("nan")
    return 1.0 - residual_sum / total_sum


def _estimate_decay_scale(weights: FloatArray) -> float:
    """Estimate a descriptive exponential scale from positive lag weights.

    Args:
        weights: Fitted lag weights.

    Returns:
        A positive decay-scale estimate, or `nan` if a stable estimate is not
        available.
    """
    magnitude = np.abs(weights)
    positive = magnitude > 0
    if np.count_nonzero(positive) < 2:
        return float("nan")
    lags = np.arange(len(weights), dtype=float)[positive]
    log_magnitude = np.log(magnitude[positive] / np.max(magnitude))
    slope, _ = np.polyfit(lags, log_magnitude, deg=1)
    if not np.isfinite(slope) or slope >= 0:
        return float("nan")
    return float(-1.0 / slope)


class OptimalController:
    """Fit a linear history-based predictor as a controller-style reference model."""

    def __init__(self, history_length: int = 5, learning_rate: float = 0.001) -> None:
        """Initialize the model configuration.

        Args:
            history_length: Number of preceding values used for each prediction.
            learning_rate: Retained configuration value for interface compatibility.

        Raises:
            ValueError: If `history_length` is less than one or `learning_rate`
                is not positive.
        """
        if history_length < 1:
            raise ValueError("history_length must be at least 1.")
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive.")
        self.history_length = history_length
        self.learning_rate = learning_rate
        self.weights: FloatArray | None = None
        self.bias: float | None = None
        self.fitted = False

    def fit(
        self,
        firing_rate: NDArray[np.floating[Any]] | list[float],
        verbose: bool = False,
    ) -> dict[str, Any]:
        """Fit the history-based predictor to an in-memory time series.

        Args:
            firing_rate: Finite one-dimensional series used to form history and
                next-value pairs.
            verbose: Whether to print a concise fitting message.

        Returns:
            A mapping containing fitted parameters, held-out predictions, and
            descriptive fit metrics.

        Raises:
            ValueError: If the series is too short or invalid for the split.
        """
        series = _as_finite_series(
            firing_rate,
            minimum_length=self.history_length + 5,
            name="firing_rate",
        )
        inputs, targets = self._make_pairs(series)
        n_train = max(2, int(0.7 * len(inputs)))
        if len(inputs) - n_train < 2:
            raise ValueError("firing_rate does not leave enough held-out values.")
        train_inputs, test_inputs = inputs[:n_train], inputs[n_train:]
        train_targets, test_targets = targets[:n_train], targets[n_train:]
        if verbose:
            print("Fitting linear history-based model...")

        # An intercept column gives a deterministic least-squares fit.
        design_matrix = np.column_stack((train_inputs, np.ones(len(train_inputs))))
        parameters, _, _, _ = np.linalg.lstsq(design_matrix, train_targets, rcond=None)
        self.weights = parameters[:-1].astype(float, copy=True)
        self.bias = float(parameters[-1])
        self.fitted = True
        predictions = test_inputs @ self.weights + self.bias
        error_signal = test_targets - predictions
        correlation = float("nan")
        if np.std(predictions) > 0 and np.std(test_targets) > 0:
            correlation = float(np.corrcoef(predictions, test_targets)[0, 1])

        return {
            "r2": _r2_score(test_targets, predictions),
            "mse": float(np.mean(error_signal**2)),
            "mae": float(np.mean(np.abs(error_signal))),
            "correlation": correlation,
            "weights": self.weights.copy(),
            "bias": self.bias,
            "error_signal": error_signal,
            "predictions": predictions,
            "targets": test_targets,
            "n_params": self.history_length + 1,
        }

    def predict(self, firing_rate_history: NDArray[np.floating[Any]] | list[float]) -> float:
        """Predict the next value from a fitted model and a fixed-length history.

        Args:
            firing_rate_history: Most recent values, with length equal to
                `history_length`.

        Returns:
            The next-value prediction.

        Raises:
            ValueError: If the model is unfitted or the history is invalid.
        """
        if not self.fitted or self.weights is None or self.bias is None:
            raise ValueError("Model must be fitted before prediction.")
        history = _as_finite_series(
            firing_rate_history,
            minimum_length=self.history_length,
            name="firing_rate_history",
        )
        if len(history) != self.history_length:
            raise ValueError(f"History must have length {self.history_length}.")
        return float(history @ self.weights + self.bias)

    def compute_control_params(self) -> dict[str, float | int]:
        """Summarize fitted lag weights with simple descriptive quantities.

        Returns:
            A mapping with estimated decay scale, aggregate gain, dominant lag,
            and lag-weight dispersion.

        Raises:
            ValueError: If the model has not been fitted.
        """
        if not self.fitted or self.weights is None:
            raise ValueError("Model must be fitted first.")
        weights_abs = np.abs(self.weights)
        return {
            "time_constant": _estimate_decay_scale(self.weights),
            "gain": float(np.sum(weights_abs)),
            "dominant_lag": int(np.argmax(weights_abs) + 1),
            "weights_std": float(np.std(self.weights)),
        }

    def _make_pairs(self, series: FloatArray) -> tuple[FloatArray, FloatArray]:
        """Create lagged input rows and next-value targets.

        Args:
            series: Validated one-dimensional series.

        Returns:
            A tuple of lagged input rows and their corresponding targets.
        """
        n_samples = len(series) - self.history_length
        inputs = np.empty((n_samples, self.history_length), dtype=float)
        for index in range(n_samples):
            inputs[index] = series[index : index + self.history_length]
        return inputs, series[self.history_length :]


class AutoregressiveModel:
    """Expose a history-based autoregressive comparison model."""

    def __init__(self, order: int = 5) -> None:
        """Initialize the autoregressive order.

        Args:
            order: Number of preceding values included in each prediction.

        Raises:
            ValueError: If `order` is less than one.
        """
        if order < 1:
            raise ValueError("order must be at least 1.")
        self.order = order
        self.weights: FloatArray | None = None
        self.bias: float | None = None
        self.fitted = False

    def fit(self, firing_rate: NDArray[np.floating[Any]] | list[float]) -> dict[str, Any]:
        """Fit the autoregressive comparison model.

        Args:
            firing_rate: Finite one-dimensional series to model.

        Returns:
            A mapping returned by the underlying history-based fit.

        Raises:
            ValueError: If the input series is invalid or too short.
        """
        controller = OptimalController(history_length=self.order)
        results = controller.fit(firing_rate)
        self.weights = controller.weights
        self.bias = controller.bias
        self.fitted = True
        return results


class PIDController:
    """Fit a simple proportional-integral-derivative reference controller."""

    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.1) -> None:
        """Initialize proportional, integral, and derivative gains.

        Args:
            kp: Initial proportional gain.
            ki: Initial integral gain.
            kd: Initial derivative gain.
        """
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.fitted = False

    def fit(
        self,
        firing_rate: NDArray[np.floating[Any]] | list[float],
        setpoint: float | None = None,
    ) -> dict[str, float | int]:
        """Choose bounded PID gains using a deterministic coarse grid.

        Args:
            firing_rate: Finite one-dimensional series to simulate against.
            setpoint: Optional fixed target value; the training mean is used when
                omitted.

        Returns:
            A mapping with held-out score, selected gains, and setpoint.

        Raises:
            ValueError: If the series is invalid, too short, or the setpoint is
                not finite.
        """
        series = _as_finite_series(firing_rate, minimum_length=8, name="firing_rate")
        n_train = max(3, int(0.7 * len(series)))
        if len(series) - n_train < 3:
            raise ValueError("firing_rate does not leave enough held-out values.")
        train_data, test_data = series[:n_train], series[n_train:]
        if setpoint is None:
            setpoint = float(np.mean(train_data))
        elif not np.isfinite(setpoint):
            raise ValueError("setpoint must be finite.")

        candidates = (
            np.linspace(0.0, 10.0, 6),
            np.linspace(0.0, 1.0, 6),
            np.linspace(0.0, 1.0, 6),
        )
        best_error = float("inf")
        best_gains = (self.kp, self.ki, self.kd)
        for kp in candidates[0]:
            for ki in candidates[1]:
                for kd in candidates[2]:
                    predictions = self._simulate(train_data, setpoint, kp, ki, kd)
                    error = float(np.mean((predictions - train_data[1:]) ** 2))
                    if error < best_error:
                        best_error = error
                        best_gains = (float(kp), float(ki), float(kd))
        self.kp, self.ki, self.kd = best_gains
        self.fitted = True
        predictions = self._simulate(test_data, setpoint, self.kp, self.ki, self.kd)
        return {
            "r2": _r2_score(test_data[1:], predictions),
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "setpoint": setpoint,
            "n_params": 4,
        }

    def _simulate(
        self,
        series: FloatArray,
        setpoint: float,
        kp: float,
        ki: float,
        kd: float,
    ) -> FloatArray:
        """Simulate one-step PID responses for a series.

        Args:
            series: One-dimensional values used to form consecutive errors.
            setpoint: Target value for the controller.
            kp: Proportional gain.
            ki: Integral gain.
            kd: Derivative gain.

        Returns:
            Simulated one-step predictions, one shorter than `series`.
        """
        predictions = np.empty(len(series) - 1, dtype=float)
        integral = 0.0
        previous_error = float(series[0] - setpoint)
        for index in range(1, len(series)):
            error = float(series[index - 1] - setpoint)
            integral += error
            derivative = error - previous_error
            predictions[index - 1] = setpoint + kp * error + ki * integral + kd * derivative
            previous_error = error
        return predictions


class StaticBaseline:
    """Fit a constant mean-value baseline for model comparison."""

    def __init__(self) -> None:
        """Initialize an unfitted baseline."""
        self.mean_rate: float | None = None
        self.fitted = False

    def fit(self, firing_rate: NDArray[np.floating[Any]] | list[float]) -> dict[str, float | int]:
        """Fit the baseline using the training portion of a series.

        Args:
            firing_rate: Finite one-dimensional series to summarize.

        Returns:
            A mapping with held-out score, fitted mean, and parameter count.

        Raises:
            ValueError: If the series is invalid or too short.
        """
        series = _as_finite_series(firing_rate, minimum_length=5, name="firing_rate")
        n_train = max(2, int(0.7 * len(series)))
        if len(series) - n_train < 2:
            raise ValueError("firing_rate does not leave enough held-out values.")
        train_data, test_data = series[:n_train], series[n_train:]
        self.mean_rate = float(np.mean(train_data))
        self.fitted = True
        predictions = np.full(test_data.shape, self.mean_rate, dtype=float)
        return {
            "r2": _r2_score(test_data, predictions),
            "mean_rate": self.mean_rate,
            "n_params": 1,
        }


def preprocess_spike_train(
    spike_times: NDArray[np.floating[Any]] | list[float],
    duration: float,
    bin_size: float = 0.1,
    sigma: float = 3.0,
) -> tuple[FloatArray, FloatArray]:
    """Bin event times and apply Gaussian smoothing to form a rate series.

    Args:
        spike_times: Finite one-dimensional event times in the interval from zero
            through `duration`.
        duration: Positive span covered by the event times.
        bin_size: Positive width of each time bin.
        sigma: Positive Gaussian window width in bins.

    Returns:
        A tuple containing bin start times and a smoothed rate series.

    Raises:
        ValueError: If inputs are not finite, dimensions are invalid, or an event
            lies outside the stated duration.
    """
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be positive and finite.")
    if not np.isfinite(bin_size) or bin_size <= 0:
        raise ValueError("bin_size must be positive and finite.")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be positive and finite.")
    events = _as_finite_series(spike_times, minimum_length=0, name="spike_times")
    if np.any(events < 0) or np.any(events > duration):
        raise ValueError("spike_times must fall within the stated duration.")
    n_bins = int(duration / bin_size)
    if n_bins < 1:
        raise ValueError("duration must contain at least one bin.")
    time = np.arange(n_bins, dtype=float) * bin_size
    counts, _ = np.histogram(events, bins=n_bins, range=(0, duration))
    firing_rate = counts.astype(float) / bin_size
    # Limit the window so same-mode convolution preserves input length.
    half_width = min(10, max(0, (n_bins - 1) // 2))
    offsets = np.arange(-half_width, half_width + 1, dtype=float)
    window = np.exp(-0.5 * (offsets / sigma) ** 2)
    window /= window.sum()
    return time, np.convolve(firing_rate, window, mode="same")


def compare_models(
    firing_rate: NDArray[np.floating[Any]] | list[float],
    verbose: bool = False,
) -> dict[str, dict[str, Any]]:
    """Fit each retained model to a single in-memory series.

    Args:
        firing_rate: Finite one-dimensional series used by every model.
        verbose: Whether to print model-progress and failure messages.

    Returns:
        A mapping from model name to its result mapping. A model-level failure is
        represented by a mapping containing the error message.

    Raises:
        ValueError: If the common input is invalid for all models.
    """
    series = _as_finite_series(firing_rate, minimum_length=10, name="firing_rate")
    models: dict[str, Any] = {
        "Optimal Controller": OptimalController(history_length=5),
        "AR Model": AutoregressiveModel(order=5),
        "PID Controller": PIDController(),
        "Static Baseline": StaticBaseline(),
    }
    results: dict[str, dict[str, Any]] = {}
    for name, model in models.items():
        if verbose:
            print(f"Fitting {name}...")
        try:
            results[name] = model.fit(series)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            if verbose:
                print(f"  Failed: {error}")
            results[name] = {"error": str(error)}
    return results


def fit_control_model(firing_rate: NDArray[np.floating[Any]] | list[float]) -> dict[str, Any]:
    """Fit the default history-based model through the legacy convenience API.

    Args:
        firing_rate: Finite one-dimensional series to model.

    Returns:
        The result mapping from `OptimalController.fit`.

    Raises:
        ValueError: If the input series is invalid or too short.
    """
    return OptimalController().fit(firing_rate)
