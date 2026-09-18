# Research Status and Plan

## Answer to the current research question

The repository does not yet answer whether neural systems are adaptive controllers. It contains implemented controller-style software and synthetic tests, but no empirical neural dataset, benchmark, or observed outcome.

## Completed work

A linear history-based predictor, an autoregressive wrapper, a PID-style reference simulation, a mean baseline, event-time binning, Gaussian smoothing, and a common comparison helper are implemented. Deterministic synthetic tests cover valid predictions, invalid histories, finite-input validation, preprocessing shape, and returned comparison structures.

## Successful and failed work

The successful work is software-level: the retained interfaces behave as specified on synthetic inputs and reject the specified invalid cases. The empirical research question remains untested rather than supported or refuted. No observed accuracy, model superiority, biological interpretation, or neural-controller conclusion has been established.

## What remains unimplemented

The repository does not include data acquisition, empirical evaluation, statistical comparison, result reporting, figure generation, or independent reproduction on neural recordings. Those steps are required before any biological or predictive claim can be considered.

## Next research decision

A future empirical extension should predefine the dataset, prediction target, baselines, held-out evaluation, statistical comparison, and interpretation boundary before results are generated. Public contributions are welcome for the data-free methods, tests, documentation, and design of that evaluation plan.
