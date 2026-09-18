# Introduction: Prediction, Feedback, and Neural Time Series

## The starting question

Neural activity changes over time. A signal can reflect its own recent history, activity elsewhere in a network, sensory input, movement, and experimental context. This repository asks a modest methods question: can simple history-based and feedback-style models serve as transparent comparison tools for a one-dimensional time series?

It does **not** begin by assuming that a neuron is literally a controller. That is a scientific claim requiring an explicit feedback loop, a target or setpoint, an error signal, an action pathway, and empirical tests of their relationships.

## Prediction and control are different

An **autoregressive** model predicts the next value from weighted earlier values. This can be a useful descriptive baseline for a changing signal. More complete neural models may also include ensemble activity, stimuli, or behavior as separate covariates.[1] A fitted autoregressive model describes a chosen statistical relationship; it does not identify synapses, causation, or a feedback loop.[2]

A **feedback controller** compares a measured quantity with a goal and changes an output in response. A familiar engineering example is the proportional–integral–derivative (PID) controller. Its proportional term responds to current error, its integral term accumulates past error, and its derivative term responds to changing error. Its behavior depends on system dynamics, delays, disturbances, sampling, gain tuning, and stability.[3]

## Why these ideas appear in neuroscience

Control theory and predictive-processing frameworks can generate useful hypotheses about predictions, errors, goals, actions, and circuits.[4] [5] They are not interchangeable with a time-series fit. A model that predicts a signal from its past does not demonstrate that the recorded system has a setpoint, computes an error, or implements PID control.

This distinction matters because computational metaphors can be productive while also becoming misleading if they are treated as literal descriptions of a distributed, dynamic biological system.[6] Linking an algorithmic idea to a neural mechanism requires behaviorally meaningful tasks, appropriate measurements, interventions, and tests beyond a model fit.[7]

## What this repository contains

The repository is a **working synthetic methods prototype**. It implements a linear history-based predictor, an autoregressive wrapper, a PID-style reference simulation, a mean baseline, event-time binning, Gaussian smoothing, and deterministic synthetic tests. No neural dataset, empirical benchmark, figure, statistical comparison, or observed neural result is included.

The software tests show that specified interfaces behave as expected on in-memory inputs. They do not establish that neurons or neural systems behave as adaptive controllers. A future empirical extension would need a pre-specified target, explicit definitions of feedback and setpoint, suitable baselines, held-out evaluation, uncertainty analysis, and an interpretation boundary.

## Citation provenance

No valid prior GenSpark citation was found. A historical placeholder paper citation lacked authors, year, and DOI, so it is not presented as a scholarly reference. The verified references below were added for this introduction.

## References

[1]: https://doi.org/10.1152/jn.00697.2004 "Truccolo et al. (2005), A point process framework for relating neural spiking activity to spiking history, neural ensemble, and extrinsic covariate effects"
[2]: https://doi.org/10.1523/JNEUROSCI.4399-14.2015 "Seth, Barrett, and Barnett (2015), Granger causality analysis in neuroscience and neuroimaging"
[3]: https://doi.org/10.1016/S0967-0661(01)00062-4 "Åström and Hägglund (2001), The future of PID control"
[4]: https://doi.org/10.1038/nn1309 "Todorov (2004), Optimality principles in sensorimotor control"
[5]: https://doi.org/10.1016/j.neuron.2018.10.003 "Keller and Mrsic-Flogel (2018), Predictive processing: A canonical cortical computation"
[6]: https://doi.org/10.1017/S0140525X19000049 "Brette (2019), Is coding a relevant metaphor for the brain?"
[7]: https://doi.org/10.1016/j.neuron.2016.12.041 "Krakauer et al. (2017), Neuroscience needs behavior: Correcting a reductionist bias"
