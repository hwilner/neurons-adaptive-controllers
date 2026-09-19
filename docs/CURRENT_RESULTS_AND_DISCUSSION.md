# Current Results and Discussion

## Current Result

The current result is a working synthetic methods prototype. The repository contains software utilities for history-based prediction, an autoregressive comparison interface, a PID-style reference simulation, a simple baseline, and preprocessing helpers. Its deterministic synthetic checks support a limited software conclusion: the retained interfaces are intended to behave consistently for their defined in-memory inputs and specified invalid cases.

This is supportive evidence for the clarity and basic operation of the software components. It is not supportive evidence for a biological account. No neural recordings, empirical benchmark, statistical comparison, figure, or observed neural outcome is present in this repository.

## Interpretation

The prototype makes it possible to discuss several transparent ways of describing a changing signal. A history-based model asks whether recent values are useful for predicting a later value. A PID-style simulation provides a familiar feedback-control reference. A baseline provides a simple point of comparison. These are useful method ingredients because they make their inputs and roles explicit.

The current evidence supports only that these ingredients have been implemented and checked in a synthetic setting. It does not show that any retained model is useful for a particular neural signal, that one model would outperform another in an empirical setting, or that a fitted pattern has a biological mechanism. The empirical research question is therefore untested, rather than answered positively or negatively.

## What the Result Does Not Show

The result does not show that neurons are adaptive controllers. In particular, it does not establish a biological goal, setpoint, error signal, feedback pathway, action pathway, or causal relationship among those elements. It also does not establish predictive usefulness on neural data, generalization beyond synthetic inputs, robustness to different recording conditions, or an advantage over suitable alternatives.

No empirical evaluation has been run in this public project. Work not run includes selecting an appropriate data boundary, defining an observation and prediction target, choosing comparison methods, separating fitting from held-out evaluation, assessing uncertainty, and determining how any outcome should be interpreted. The absence of such work is not a failure result; it is an important limit on what can be concluded.

## Discussion and Future Testing

Future work can ask testable questions without assuming their answers. For an approved and appropriately bounded empirical study, a first question is whether a history-based model improves held-out prediction relative to a clearly defined simple comparison for a specified neural signal and task. A second question is whether the variables needed for a control interpretation can be measured or manipulated: a goal, a measured quantity, an error, an output, and a feedback route. A third question is whether any apparent model benefit remains when plausible non-control explanations and relevant external influences are included in the comparison.

Any such evaluation should be planned before outcomes are inspected. The plan should define the allowed data boundary, prediction target, fitting and held-out partitions, comparison methods, handling of missing or unsuitable inputs, uncertainty assessment, and rules for interpreting both supportive and non-supportive outcomes. It should also state in advance that predictive performance alone is not evidence of a biological feedback mechanism. Maintainer approval and an appropriate data boundary are necessary before research-facing testing begins; no empirical work is carried out or reported here.
