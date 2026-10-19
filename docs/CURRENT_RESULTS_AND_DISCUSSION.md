# Current Results and Discussion

## Current Result

The current result is a working synthetic methods prototype. The repository contains software utilities for history-based prediction, an autoregressive comparison interface, a PID-style reference simulation, a simple baseline, and preprocessing helpers. Its deterministic synthetic checks support a limited software conclusion: the retained interfaces are intended to behave consistently for their defined in-memory inputs and specified invalid cases.

This is supportive evidence for the clarity and basic operation of the software components. It is not supportive evidence for a biological account. No neural recordings, empirical benchmark, statistical comparison, figure, or observed neural outcome is present in this repository.

## Software-Level Result of the Latest Correction

Two defects in the retained utilities were found by reading the code against its own documented contracts and were confirmed by execution before anything was changed. The result of that work is a statement about this repository's software only.

- The preprocessing helper previously asked `np.histogram` for a fixed bin count over the stated duration, which lays the bins out with width `duration / n_bins` rather than the requested `bin_size`; it then divided the counts by `bin_size` and reported bin starts spaced `bin_size` apart. A single synthetic event at `0.9` under `duration=1.0` and `bin_size=0.4` was therefore reported at time `0.4` with rate `2.5`, although that event belongs to the bin covering `[0.8, 1.0]`, whose `0.2` second interval gives a rate of `5.0`. The bin count was truncated as well, so `duration=0.3` with `bin_size=0.1` produced two bins rather than three. The bins now tile the duration, each rate is measured over the interval its own bin covers, and the returned times are the true bin starts.
- The history model previously accepted a series too short to identify the least-squares solve. At its then-documented minimum length the design matrix had three rows for six parameters, so the training rows were satisfied exactly and the reported held-out score was settled by a minimum-norm convention rather than by the data. A ten-value synthetic sinusoid returned a held-out R-squared of exactly `1.0` with a mean squared error of about `6e-32` on values the model was never fitted on, while a ten-value series outside that model class returned a held-out R-squared of about `-2.5` from the same number of samples. The minimum length is now derived from the parameter count, and a series that cannot identify the fit is rejected with `ValueError` instead of being scored.

**What this result rests on.** The committed suite contains 18 tests and passes in a fresh clone of this repository's `main` branch, and the seven tests added for these two contracts were confirmed to fail against the pre-correction source. The repository now also commits a CI workflow that runs the test suite and the public boundary scanner on every push to `main` and on every pull request targeting it, so both documented commands are enforced rather than only advised.

**What this result does not cover.** It adds no empirical evidence and does not move the research question. No neural recording, benchmark, statistical comparison, or observed neural outcome is present in this repository, and none was produced by this work. The gated evaluation plan in issue #17 is unchanged, and the criteria it will set for a future empirical evaluation remain pending until a Scientific Owner approves that plan and an appropriate data boundary exists. Every number above is a software output measured on an in-memory synthetic input, not a scientific result.

## Interpretation

The prototype makes it possible to discuss several transparent ways of describing a changing signal. A history-based model asks whether recent values are useful for predicting a later value. A PID-style simulation provides a familiar feedback-control reference. A baseline provides a simple point of comparison. These are useful method ingredients because they make their inputs and roles explicit.

The current evidence supports only that these ingredients have been implemented and checked in a synthetic setting. It does not show that any retained model is useful for a particular neural signal, that one model would outperform another in an empirical setting, or that a fitted pattern has a biological mechanism. The empirical research question is therefore untested, rather than answered positively or negatively.

## What the Result Does Not Show

The result does not show that neurons are adaptive controllers. In particular, it does not establish a biological goal, setpoint, error signal, feedback pathway, action pathway, or causal relationship among those elements. It also does not establish predictive usefulness on neural data, generalization beyond synthetic inputs, robustness to different recording conditions, or an advantage over suitable alternatives.

No empirical evaluation has been run in this public project. Work not run includes selecting an appropriate data boundary, defining an observation and prediction target, choosing comparison methods, separating fitting from held-out evaluation, assessing uncertainty, and determining how any outcome should be interpreted. The absence of such work is not a failure result; it is an important limit on what can be concluded.

## Discussion and Future Testing

Future work can ask testable questions without assuming their answers. For an approved and appropriately bounded empirical study, a first question is whether a history-based model improves held-out prediction relative to a clearly defined simple comparison for a specified neural signal and task. A second question is whether the variables needed for a control interpretation can be measured or manipulated: a goal, a measured quantity, an error, an output, and a feedback route. A third question is whether any apparent model benefit remains when plausible non-control explanations and relevant external influences are included in the comparison.

Any such evaluation should be planned before outcomes are inspected. The plan should define the allowed data boundary, prediction target, fitting and held-out partitions, comparison methods, handling of missing or unsuitable inputs, uncertainty assessment, and rules for interpreting both supportive and non-supportive outcomes. It should also state in advance that predictive performance alone is not evidence of a biological feedback mechanism. Maintainer approval and an appropriate data boundary are necessary before research-facing testing begins; no empirical work is carried out or reported here.
