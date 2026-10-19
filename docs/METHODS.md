# Methods: Design Decisions, Current State, and Contributor Guide

This document is for **new contributors, including those new to data science**. It explains what is implemented and why, what is only planned, how to choose between parametric and non-parametric approaches for future work, and the hygiene rules that keep this repository trustworthy. Read it alongside [METHODS_SCOPE.md](METHODS_SCOPE.md) (the formal scope statement) and [STATUS_AND_PLAN.md](STATUS_AND_PLAN.md).

## Done

Everything below exists in the code and is covered (directly or through the shared validation path) by `tests/test_control_models.py`.

### Retained models and helpers (`src/control_models.py`)

- **`OptimalController`** — a linear history-based predictor. Prediction = weighted sum of the last `history_length` values plus a bias, fit by ordinary least squares (`np.linalg.lstsq`) with an intercept column. The constructor takes `history_length` (default 5) and `learning_rate` (default 0.001). **Design note:** `learning_rate` is retained only for interface compatibility — no iterative optimization happens; the fit is a closed-form least-squares solve. This is deliberate: a deterministic, one-shot solve cannot diverge, needs no convergence checks, and gives bit-reproducible results in tests. **Identifiability requirement:** the model has `history_length + 1` free parameters, so the chronological training split must hold at least that many rows. A shorter split leaves the least-squares system rank-deficient, and the resulting coefficients and scores are then fixed by a minimum-norm convention rather than by the data. The minimum series length is derived from that requirement, not stated as a constant.
- **`AutoregressiveModel`** — a thin wrapper that fits an `OptimalController` with `history_length=order` and copies its parameters. **Why a wrapper at all:** it lets comparisons name the same method by its standard statistical label ("AR model") without duplicating fitting code. It inherits the identifiability requirement above.
- **`PIDController`** — a proportional–integral–derivative reference. `fit` simulates one-step responses on the training portion for every gain combination on a coarse grid (`kp` ∈ 0–10, `ki`/`kd` ∈ 0–1, 6 points each, 216 combinations), keeps the lowest-error triple, then scores once on held-out data. If `setpoint` is omitted, the training mean is used; a non-finite setpoint is rejected. **Why grid search:** it is deterministic and inspectable; there is no optimizer state to debug.
- **`StaticBaseline`** — always predicts the training mean. **Why it exists:** any history-based model must beat this trivial yardstick before its complexity is justified. It has `n_params = 1`.
- **`preprocess_spike_train`** — bins event times so that the bins tile the stated duration exactly, converts each bin's count to a rate measured over the interval that bin actually covers, and convolves with a normalized Gaussian window of width `sigma` bins (window half-width capped at `min(10, (n_bins-1)//2)` so `mode="same"` convolution preserves length). The final bin is narrower than `bin_size` when the duration is not a multiple of it, and the returned times are the true bin starts. Empty event sequences are valid and return an all-zero rate.
- **`compare_models`** — fits all four retained models on one series and returns a result mapping per model. A model-level `ValueError`, `FloatingPointError`, or `numpy.linalg.LinAlgError` becomes an `{"error": ...}` entry rather than aborting the comparison; common input validation happens before any model runs and still raises. The required length is the one the strictest retained model needs, because a series short enough for one model can still be too short for another.
- **`_as_finite_series`** — the single validation funnel: every public entry point requires a one-dimensional, finite, numeric series of sufficient length, and raises `ValueError` otherwise.
- **`_minimum_series_length`** — derives the shortest series that supports an identified fit for a given history length, by searching for the smallest number of lagged pairs whose chronological training split holds at least `history_length + 1` rows and still leaves two held-out values.
- **`_r2_score`** — dependency-free R²; returns `nan` when target variance is zero (constant target), because the coefficient of determination is undefined there. This is a documented contract, not a bug.
- **`_estimate_decay_scale` / `compute_control_params`** — descriptive summaries of fitted lag weights (decay time constant, total gain, dominant lag, weight dispersion). These are descriptions of a fitted model, not stability proofs or biological quantities.

### Tests

`tests/test_control_models.py` currently verifies, using only in-memory synthetic series (a `linspace` ramp, a sine wave, a mixed incommensurate-frequency series, short event-time lists):

- preprocessing returns aligned time/rate arrays of the expected length with finite values;
- preprocessing measures each rate over the width of the bin that holds the event, keeps every bin when the duration divides evenly by the bin width, and counts an event in the final partial bin;
- a fitted `OptimalController` predicts a finite value from a correctly sized history;
- a too-short history raises `ValueError`;
- a history fit whose training split cannot identify the least-squares solve raises `ValueError` instead of returning a score, and the shortest identifying series is accepted while one value fewer is rejected;
- the derived minimum series length always leaves an identified training split with at least two held-out values;
- `compare_models` returns exactly the four retained model names, each with `n_params` or `error`, and rejects a series too short for every model it fits;
- the baseline rejects non-finite input;
- the constant-target R² contract returns `nan`.

### Tooling

`tools/check_public_boundary.py` scans tracked files for prohibited path categories and unsupported public-claim markers. It is a guardrail, not a substitute for review.

The same two commands the documentation prescribes — `python -m unittest discover -s tests -v` and `python tools/check_public_boundary.py` — run in the CI workflow on every push to `main` and every pull request targeting `main`, so the stated gate is enforced rather than only advised. The workflow installs only the declared runtime requirement, needs no secret, and grants read-only repository permissions.

## Intended

Nothing below is implemented. Items come from the open issue backlog; each entry is a task card with acceptance criteria.

- **Edge-case test cards (ready, good first issue):** none are currently open. Cards #8–#14 — the one-dimensional finite-series contract, the per-model comparison failure handling, the empty event sequence, the event-duration validation, prediction before fitting, the non-finite PID setpoint, and the constant-target R² — are all closed, implemented, and covered by the suite described above. Do not re-file them.
- **Documentation cards (ready):** none are currently open. Card #8 (clarify the finite 1-D series contract in `METHODS_SCOPE.md`) and card #9 (document per-model failure handling in the `compare_models` docstring) are closed.
- **Blocked integration cards:** #15 (review the validation contract once the validation cards land) and #16 (integrate the new tests once the edge-case cards land) remain open and are now reviewable, because the cards they were waiting on are closed.
- **Gated research planning:** #17 — a Scientific-Owner-approved plan for any future empirical evaluation. **No dataset, derived output, figure, or empirical claim may enter the public tree**; the card exists to define the boundary *before* any research-facing work. Closed issue #5 shows an earlier version of this gate, superseded by #17. The supporting drafting cards #18 (data-boundary statement), #19 (Scientific Owner approval statement), and #20 (evaluation planning template) remain open, as does #21 (a continuous-time state-space reformulation proposal).

The deferred/dropped table in [DEFERRED_AND_DROPPED_DIRECTIONS.md](DEFERRED_AND_DROPPED_DIRECTIONS.md) records what will not be added publicly: data acquisition, data-dependent workflows, figures, notebooks, archives, and empirical interpretation.

## Design decisions and their reasons

1. **Closed-form least squares instead of gradient descent.** Deterministic, reproducible, no convergence failures in CI. Cost: `learning_rate` is inert configuration. If a future model genuinely needs iterative fitting, that model — not `OptimalController` — should introduce it, with a fixed seed and an iteration cap.
2. **Chronological 70/30 split, not random shuffling.** For time series, shuffling leaks future information into training. The split is `n_train = max(2, int(0.7 * n))` (models) and requires at least 2–3 held-out points, raising `ValueError` otherwise. Rule: **never random-split a time series** in this repository.
3. **Reject a fit that the data cannot identify.** The history model has `history_length + 1` free parameters, so the training split must hold at least that many rows. A rank-deficient solve is not a weak fit, it is an unidentified one: the training rows are satisfied exactly and the remaining freedom is settled by a minimum-norm convention, so the reported held-out score describes the convention rather than the data. The minimum series length is therefore derived from the parameter count instead of being a fixed constant. Rule: **a fit that cannot be identified must raise, not report a score.**
4. **Coarse bounded grid for PID gains.** Deterministic and inspectable. The grid bounds (kp ≤ 10, ki/kd ≤ 1) are a pragmatic choice, not a theoretical optimum; a fit that selects a boundary value should be read as "the true optimum may lie outside the grid."
5. **Failures become `error` entries in `compare_models`.** One bad model must not hide the results of the others, and the comparison must remain callable in tests on awkward synthetic inputs.
6. **`nan` for undefined R².** Silently returning 0 or 1 for constant targets would fabricate a score. `nan` propagates honestly.
7. **Mean baseline included in every comparison.** A complex model that cannot beat the training mean has negative justification.
8. **Pure NumPy, no frameworks.** `requirements.txt` declares only NumPy, so the boundary scanner and tests run anywhere without data-adjacent dependencies.

### Undecided choices (with a rule for each)

- **How a future empirical evaluation would handle uncertainty** (bootstrap resampling vs. analytic intervals). *Rule:* choose only inside the gated plan (#17); prefer the option whose assumptions are stated and testable on synthetic data first.
- **Whether future preprocessing needs alternatives to Gaussian smoothing** (e.g., adaptive bandwidths). *Rule:* add a second smoother only if a synthetic test demonstrates a failure mode of the current one (e.g., very sparse bins); keep both deterministic.
- **History length / AR order selection** (fixed at 5 today). *Rule:* never tune on the held-out split; if selection is ever added, it must use a nested training-only criterion.

## Parametric vs. non-parametric: a decision guide

**Parametric methods** assume the data follow a specific form described by a fixed, small set of parameters. All retained models are parametric: the history model has `history_length + 1` parameters, the PID has 4, the baseline 1. *Assumptions:* linearity (history model), a fixed setpoint-and-error structure (PID), or constancy (baseline). *Advantages:* few parameters means little data needed, exact reproducibility, and interpretable weights. *Cost:* if the true relationship is not of the assumed form, the model is wrong no matter how much data you have.

**Non-parametric methods** let the effective complexity grow with the data (nearest neighbors, kernel smoothers, Gaussian processes). *Assumptions:* weaker but not absent — e.g., smoothness. *Advantages:* flexibility. *Costs:* more data needed, harder interpretation, more hyperparameters, and easier overfitting.

```mermaid
flowchart TD
    A["New analysis question"] --> B{"Is there a stated,<br/>pre-registered form?<br/>(linear history, PID, mean)"}
    B -- Yes --> C["Parametric:<br/>fit the stated model,<br/>report held-out R2/MSE/MAE"]
    B -- No --> D{"Enough data to support<br/>growing complexity AND a<br/>synthetic validation first?"}
    D -- No --> E["Stay parametric;<br/>a flexible model you cannot<br/>validate is worse than a<br/>simple one you can"]
    D -- Yes --> F["Consider non-parametric,<br/>but ONLY inside the gated<br/>empirical plan (#17)"]
    C --> G["Always compare against<br/>StaticBaseline on held-out data"]
    E --> G
    F --> G
```

Concrete rules for this repository:

1. Every retained and proposed model must state its parameter count (`n_params`) — comparison across models must weigh complexity, not just score.
2. The public tree currently contains **only parametric models**, and new public models should be parametric unless a gated plan argues otherwise.
3. Any non-parametric proposal belongs in the gated empirical plan (#17), must run on synthetic data first, and must include a parametric baseline.
4. A parametric model that does not beat `StaticBaseline` on held-out data is evidence *against* its assumptions, and that outcome must be reportable — non-supportive results are results.

## Data-science hygiene rules

1. **Determinism and seeds.** The current code path contains no randomness at all — splits are chronological, the grid is fixed, least squares is exact. If randomness is ever introduced (e.g., synthetic noise in a test), seed it explicitly (`np.random.default_rng(seed)`) and state the seed in the test name or docstring.
2. **Synthetic ground truth first.** Every behavior must be demonstrable on an in-memory synthetic input where the correct outcome is known by construction (wrong-length history → `ValueError`; constant target → `nan` R²; empty events → zero rate). A method that cannot pass a synthetic check is not ready for any data.
3. **Null models.** `StaticBaseline` is the built-in null: the hypothesis "history helps" is only meaningful against "the mean is enough." Any future empirical plan must name its null models in advance, including non-control explanations.
4. **Test discipline.** Tests are file-free, network-free, deterministic, and test one contract each (mirroring the one-method-per-card pattern in issues #10–#14). Run the full suite and the boundary check before proposing any change; CI runs the same two commands on every push to `main` and on every pull request targeting `main`:

```bash
python -m unittest discover -s tests -v
python tools/check_public_boundary.py
```

5. **Boundary discipline.** No datasets, outputs, figures, notebooks, caches, downloads, or external metadata in the public tree — see [RELEASE_BOUNDARY.md](RELEASE_BOUNDARY.md). Tests must not write files. Documentation must not contain empirical claims.
6. **Honest reporting.** Scores from this code are software outputs, not scientific evidence. Prediction alone cannot establish a feedback mechanism; say so wherever scores are shown.

## Where to start

Pick an open card from the backlog above — #15 and #16 are reviewable now that the cards they were waiting on are closed, and #18–#21 cover the gated evaluation planning and a reformulation proposal. Read the card's acceptance criteria carefully, follow them exactly, and keep the change inside its stated boundary. The cards are written so that a correct change is small, reviewable, and checkable with the two commands above.
