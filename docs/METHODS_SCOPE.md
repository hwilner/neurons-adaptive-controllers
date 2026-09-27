# Methods Scope

## Purpose

The retained utilities provide compact computational building blocks for exploring controller-style descriptions of a one-dimensional time series. They are intended for code review, synthetic examples, and method development within an independent research setting.

## Retained components

`OptimalController` fits a linear history-based predictor. `AutoregressiveModel` exposes a comparison wrapper with the same fitting form. `PIDController` supplies a simple proportional-integral-derivative simulation with fitted gains, and `StaticBaseline` provides a mean-value baseline. `preprocess_spike_train` bins event times and applies Gaussian smoothing. `compare_models` runs the retained model interfaces against an in-memory series.

## Assumptions and limits

Retained series inputs must be numeric, one-dimensional, and finite: a shared validation helper rejects higher-dimensional inputs and inputs containing non-finite values. The minimum acceptable length is not fixed once for the module; it depends on the selected model or helper, and each public callable documents its own requirement in its docstring, so a series long enough for one utility may still be too short for another. Event times used by the preprocessing helper are expected to fall within the stated duration. The utilities make no claim that any controller family is an appropriate description of a particular system, and their returned scores or parameters require context-specific evaluation outside this public tree.

The code does not load data, query services, save figures, or write analysis outputs. It should therefore be treated as method-oriented software rather than evidence for a scientific conclusion.
