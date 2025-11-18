"""
Control Theory Models for Neural Data Analysis
Enhanced version for Paper 1 upgrade

Author: Harel Joseph Wilner
Date: November 2024
"""

import numpy as np
from scipy import signal, optimize, stats
from sklearn.metrics import r2_score
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')


class OptimalController:
    """
    Optimal Controller model for single neuron dynamics.
    Uses recent firing history to predict and regulate future activity.
    """
    
    def __init__(self, history_length: int = 5, learning_rate: float = 0.001):
        """
        Initialize Optimal Controller.
        
        Parameters:
        -----------
        history_length : int
            Number of past time steps to use for prediction
        learning_rate : float
            Learning rate for optimization
        """
        self.history_length = history_length
        self.learning_rate = learning_rate
        self.weights = None
        self.bias = None
        self.fitted = False
        
    def fit(self, firing_rate: np.ndarray, verbose: bool = False) -> Dict:
        """
        Fit the controller to firing rate data.
        
        Parameters:
        -----------
        firing_rate : np.ndarray
            Smoothed firing rate time series
        verbose : bool
            Print optimization progress
            
        Returns:
        --------
        results : dict
            Fitting results including parameters and performance
        """
        n_samples = len(firing_rate) - self.history_length
        
        # Create input-output pairs
        X = np.zeros((n_samples, self.history_length))
        y = np.zeros(n_samples)
        
        for i in range(n_samples):
            X[i] = firing_rate[i:i+self.history_length]
            y[i] = firing_rate[i+self.history_length]
        
        # Split into train/test
        n_train = int(0.7 * n_samples)
        X_train, X_test = X[:n_train], X[n_train:]
        y_train, y_test = y[:n_train], y[n_train:]
        
        # Define loss function
        def loss_fn(params):
            weights = params[:-1]
            bias = params[-1]
            predictions = X_train @ weights + bias
            mse = np.mean((predictions - y_train) ** 2)
            return mse
        
        # Initialize parameters
        init_params = np.random.randn(self.history_length + 1) * 0.1
        
        # Optimize
        result = optimize.minimize(
            loss_fn,
            init_params,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'disp': verbose}
        )
        
        # Store fitted parameters
        self.weights = result.x[:-1]
        self.bias = result.x[-1]
        self.fitted = True
        
        # Evaluate on test set
        y_pred_test = X_test @ self.weights + self.bias
        r2_test = r2_score(y_test, y_pred_test)
        
        # Compute error signal (for Paper 2)
        error_signal = y_test - y_pred_test
        
        # Compute additional metrics
        mse_test = np.mean((y_pred_test - y_test) ** 2)
        mae_test = np.mean(np.abs(y_pred_test - y_test))
        correlation = np.corrcoef(y_pred_test, y_test)[0, 1]
        
        results = {
            'r2': r2_test,
            'mse': mse_test,
            'mae': mae_test,
            'correlation': correlation,
            'weights': self.weights.copy(),
            'bias': self.bias,
            'error_signal': error_signal,
            'predictions': y_pred_test,
            'targets': y_test,
            'n_params': self.history_length + 1
        }
        
        return results
    
    def predict(self, firing_rate_history: np.ndarray) -> float:
        """
        Predict next firing rate given history.
        
        Parameters:
        -----------
        firing_rate_history : np.ndarray
            Recent firing rate history (length = history_length)
            
        Returns:
        --------
        prediction : float
            Predicted firing rate at next time step
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        if len(firing_rate_history) != self.history_length:
            raise ValueError(f"History must have length {self.history_length}")
        
        prediction = firing_rate_history @ self.weights + self.bias
        return prediction
    
    def compute_control_params(self) -> Dict:
        """
        Extract interpretable control parameters from the fitted model.
        
        Returns:
        --------
        params : dict
            Control parameters (gain, time constant, etc.)
        """
        if not self.fitted:
            raise ValueError("Model must be fitted first")
        
        # Estimate time constant from weights decay
        weights_abs = np.abs(self.weights)
        if np.max(weights_abs) > 0:
            # Fit exponential decay to weights
            try:
                popt, _ = optimize.curve_fit(
                    lambda t, tau: np.exp(-t/tau),
                    np.arange(len(self.weights)),
                    weights_abs / np.max(weights_abs),
                    p0=[2.0],
                    bounds=(0.1, 100)
                )
                time_constant = popt[0]
            except:
                time_constant = np.nan
        else:
            time_constant = np.nan
        
        # Overall gain (how strongly past influences future)
        gain = np.sum(np.abs(self.weights))
        
        params = {
            'time_constant': time_constant,
            'gain': gain,
            'dominant_lag': np.argmax(np.abs(self.weights)) + 1,
            'weights_std': np.std(self.weights)
        }
        
        return params


class AutoregressiveModel:
    """
    Standard Autoregressive (AR) model for comparison.
    """
    
    def __init__(self, order: int = 5):
        self.order = order
        self.weights = None
        self.bias = None
        self.fitted = False
    
    def fit(self, firing_rate: np.ndarray) -> Dict:
        """Fit AR model - identical to OptimalController for comparison."""
        controller = OptimalController(history_length=self.order)
        results = controller.fit(firing_rate)
        
        self.weights = controller.weights
        self.bias = controller.bias
        self.fitted = True
        
        return results


class PIDController:
    """
    PID (Proportional-Integral-Derivative) Controller.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.fitted = False
    
    def fit(self, firing_rate: np.ndarray, setpoint: Optional[float] = None) -> Dict:
        """
        Fit PID controller to data.
        
        Parameters:
        -----------
        firing_rate : np.ndarray
            Firing rate time series
        setpoint : float, optional
            Target firing rate (default: mean of data)
        """
        if setpoint is None:
            setpoint = np.mean(firing_rate)
        
        # Split train/test
        n_train = int(0.7 * len(firing_rate))
        train_data = firing_rate[:n_train]
        test_data = firing_rate[n_train:]
        
        # Optimize PID parameters on training data
        def loss_fn(params):
            kp, ki, kd = params
            predictions = self._simulate(train_data, setpoint, kp, ki, kd)
            mse = np.mean((predictions - train_data[1:]) ** 2)
            return mse
        
        result = optimize.minimize(
            loss_fn,
            [self.kp, self.ki, self.kd],
            method='L-BFGS-B',
            bounds=[(0, 10), (0, 1), (0, 1)]
        )
        
        self.kp, self.ki, self.kd = result.x
        self.fitted = True
        
        # Evaluate on test data
        predictions = self._simulate(test_data, setpoint, self.kp, self.ki, self.kd)
        r2_test = r2_score(test_data[1:], predictions)
        
        results = {
            'r2': r2_test,
            'kp': self.kp,
            'ki': self.ki,
            'kd': self.kd,
            'setpoint': setpoint,
            'n_params': 4
        }
        
        return results
    
    def _simulate(self, data: np.ndarray, setpoint: float, 
                  kp: float, ki: float, kd: float) -> np.ndarray:
        """Simulate PID control."""
        predictions = []
        integral = 0
        prev_error = data[0] - setpoint
        
        for i in range(1, len(data)):
            error = data[i-1] - setpoint
            integral += error
            derivative = error - prev_error
            
            control = kp * error + ki * integral + kd * derivative
            prediction = setpoint + control
            predictions.append(prediction)
            
            prev_error = error
        
        return np.array(predictions)


class StaticBaseline:
    """
    Static baseline model (predicts mean firing rate).
    """
    
    def __init__(self):
        self.mean_rate = None
        self.fitted = False
    
    def fit(self, firing_rate: np.ndarray) -> Dict:
        """Fit static baseline."""
        n_train = int(0.7 * len(firing_rate))
        train_data = firing_rate[:n_train]
        test_data = firing_rate[n_train:]
        
        self.mean_rate = np.mean(train_data)
        self.fitted = True
        
        predictions = np.full_like(test_data, self.mean_rate)
        r2_test = r2_score(test_data, predictions)
        
        results = {
            'r2': r2_test,
            'mean_rate': self.mean_rate,
            'n_params': 1
        }
        
        return results


def preprocess_spike_train(spike_times: np.ndarray, 
                           duration: float,
                           bin_size: float = 0.1,
                           sigma: float = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert spike times to smoothed firing rate.
    
    Parameters:
    -----------
    spike_times : np.ndarray
        Spike times in seconds
    duration : float
        Total recording duration in seconds
    bin_size : float
        Bin size in seconds (default: 100ms)
    sigma : float
        Gaussian smoothing kernel width in bins
        
    Returns:
    --------
    time : np.ndarray
        Time vector
    firing_rate : np.ndarray
        Smoothed firing rate in Hz
    """
    # Create time bins
    n_bins = int(duration / bin_size)
    time = np.arange(n_bins) * bin_size
    
    # Histogram spikes
    counts, _ = np.histogram(spike_times, bins=n_bins, range=(0, duration))
    
    # Convert to Hz
    firing_rate = counts / bin_size
    
    # Smooth with Gaussian
    window = signal.windows.gaussian(21, sigma)
    window = window / window.sum()
    firing_rate_smooth = signal.convolve(firing_rate, window, mode='same')
    
    return time, firing_rate_smooth


def compare_models(firing_rate: np.ndarray, verbose: bool = False) -> Dict:
    """
    Compare all control models on a single neuron.
    
    Parameters:
    -----------
    firing_rate : np.ndarray
        Smoothed firing rate time series
    verbose : bool
        Print progress
        
    Returns:
    --------
    results : dict
        Comparison results for all models
    """
    models = {
        'Optimal Controller': OptimalController(history_length=5),
        'AR Model': AutoregressiveModel(order=5),
        'PID Controller': PIDController(),
        'Static Baseline': StaticBaseline()
    }
    
    results = {}
    
    for name, model in models.items():
        if verbose:
            print(f"Fitting {name}...")
        
        try:
            model_results = model.fit(firing_rate)
            results[name] = model_results
        except Exception as e:
            if verbose:
                print(f"  Failed: {e}")
            results[name] = {'r2': np.nan, 'error': str(e)}
    
    return results


# For backward compatibility with existing code
def fit_control_model(firing_rate: np.ndarray) -> Dict:
    """
    Simple wrapper for fitting optimal controller.
    """
    model = OptimalController()
    return model.fit(firing_rate)


if __name__ == "__main__":
    # Test with synthetic data
    print("Testing control models with synthetic data...")
    
    # Generate synthetic firing rate
    t = np.linspace(0, 100, 1000)
    firing_rate = 10 + 5*np.sin(2*np.pi*0.1*t) + np.random.randn(1000)*2
    firing_rate = np.maximum(firing_rate, 0)  # No negative rates
    
    # Test all models
    results = compare_models(firing_rate, verbose=True)
    
    print("\nResults:")
    for model_name, model_results in results.items():
        if 'r2' in model_results:
            print(f"  {model_name}: R² = {model_results['r2']:.3f}")
    
    print("\nControl models module ready!")
