# Introduction: Prediction, Feedback, and Neural Time Series

## The starting question

Neural activity changes over time. A signal can reflect its own recent history, activity elsewhere in a network, sensory input, movement, and experimental context. This repository asks a modest methods question: can simple history-based and feedback-style models serve as transparent comparison tools for a one-dimensional time series?

In sensory neurophysiology, **system identification** is one approach to building quantitative functional models from explicitly defined observations and experimental conditions, then comparing how well those models predict responses under those conditions.[8] Here, that framing is deliberately narrow: it motivates clear model inputs, outputs, and evaluation criteria, rather than a claim about what a neuron or circuit literally is.

It does **not** begin by assuming that a neuron is literally a controller. That is a scientific claim requiring an explicit feedback loop, a target or setpoint, an error signal, an action pathway, and empirical tests of their relationships.

## Prediction and control are different

An **autoregressive** model predicts the next value from weighted earlier values. This can be a useful descriptive baseline for a changing signal. More complete neural models may also include ensemble activity, stimuli, or behavior as separate covariates.[1] A fitted autoregressive model describes a chosen statistical relationship; it does not identify synapses, causation, or a feedback loop.[2]

History models are only one family of time-series models. State-space approaches specify assumptions about latent time-varying states and how observations arise, whereas Gaussian-process factor analysis combines smooth latent trajectories with a probabilistic observation model for population activity.[9] [10] In recordings from many neurons, a model may also represent stimulus dependence and correlations across units; that is a different data and modeling setting from the single-trace prototype here.[15] Dimensionality-reduction methods can provide compact descriptions of large neural recordings, but their outputs remain method-dependent summaries rather than direct readouts of a circuit's mechanism.[11]

A **feedback controller** compares a measured quantity with a goal and changes an output in response. A familiar engineering example is the proportional–integral–derivative (PID) controller. Its proportional term responds to current error, its integral term accumulates past error, and its derivative term responds to changing error. Its behavior depends on system dynamics, delays, disturbances, sampling, gain tuning, and stability.[3]

## Why these ideas appear in neuroscience

Control theory and predictive-processing frameworks can generate useful hypotheses about predictions, errors, goals, actions, and circuits.[4] [5] They are not interchangeable with a time-series fit. A model that predicts a signal from its past does not demonstrate that the recorded system has a setpoint, computes an error, or implements PID control.

For example, Rao and Ballard described a hierarchical visual model in which feedback carries predictions and feedforward connections carry residual errors.[12] Friston developed a related theoretical account in terms of hierarchical generative models and statistical inference.[13] These are explicit computational proposals, not consequences of fitting a one-dimensional autoregression. Likewise, optimal feedback control has been formulated as a theory of goal-directed motor coordination; it supplies a control-theoretic model with task goals and feedback, not a generic interpretation of a neural time series.[14]

This distinction matters because computational metaphors can be productive while also becoming misleading if they are treated as literal descriptions of a distributed, dynamic biological system.[6] Linking an algorithmic idea to a neural mechanism requires behaviorally meaningful tasks, appropriate measurements, interventions, and tests beyond a model fit.[7]

## What this repository contains

The repository is a **working synthetic methods prototype**. It implements a linear history-based predictor, an autoregressive wrapper, a PID-style reference simulation, a mean baseline, event-time binning, Gaussian smoothing, and deterministic synthetic tests. No neural dataset, empirical benchmark, figure, statistical comparison, or observed neural result is included.

The software tests show that specified interfaces behave as expected on in-memory inputs. They do not establish that neurons or neural systems behave as adaptive controllers. A future empirical extension would need a pre-specified target, explicit definitions of feedback and setpoint, suitable baselines, held-out evaluation, uncertainty analysis, and an interpretation boundary.

That extension would also need to state which variables are observed, which are treated as inputs or outputs, and what prediction or validation criterion is being used. Such choices are part of a system-identification study; they cannot be recovered from a fitted coefficient alone.[8]

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
[8]: https://doi.org/10.1146/annurev.neuro.29.051605.113024 "Wu, David, and Gallant (2006), Complete functional characterization of sensory neurons by system identification"
[9]: https://doi.org/10.1152/jn.90941.2008 "Yu et al. (2009), Gaussian-process factor analysis for low-dimensional single-trial analysis of neural population activity"
[10]: https://doi.org/10.1007/s10827-009-0179-x "Paninski et al. (2010), A new look at state-space models for neural data"
[11]: https://doi.org/10.1038/nn.3776 "Cunningham and Yu (2014), Dimensionality reduction for large-scale neural recordings"
[12]: https://doi.org/10.1038/4580 "Rao and Ballard (1999), Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects"
[13]: https://doi.org/10.1098/rstb.2005.1622 "Friston (2005), A theory of cortical responses"
[14]: https://doi.org/10.1038/nn963 "Todorov and Jordan (2002), Optimal feedback control as a theory of motor coordination"
[15]: https://doi.org/10.1038/nature07140 "Pillow et al. (2008), Spatio-temporal correlations and visual signalling in a complete neuronal population"
