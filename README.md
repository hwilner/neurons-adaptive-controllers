# Neurons as Adaptive Controllers

This independent research repository contains controller-style time-series utilities and synthetic tests. It is an early methods prototype, not a completed empirical neuroscience study.

## Research status

| Completed work | Outcome |
|---|---|
| History-based predictor, autoregressive wrapper, PID-style reference, and mean baseline | Implemented as in-memory software utilities for caller-supplied one-dimensional series. |
| Event-time binning and Gaussian smoothing utility | Implemented and covered by deterministic synthetic tests. |
| Synthetic model-interface tests | Passed for defined valid inputs, invalid histories, non-finite values, and returned comparison structures. |
| Empirical neural-data evaluation | Not implemented; no dataset, benchmark, figure, or observed result is included. |

**Current conclusion:** the repository has a working **synthetic methods prototype**. It has not established that neurons or neural systems behave as adaptive controllers, and it has no empirical success or failure result to report.

## Contents

| Path | Contents |
|---|---|
| `src/control_models.py` | Controller-style models, preprocessing, and comparison helpers. |
| `tests/` | Synthetic, file-free unit tests. |
| `tools/check_public_boundary.py` | Tracked-file release-boundary scanner. |
| `docs/` | Research status, methods scope, deferred directions, and contribution guidance. |
| `requirements.txt` | Runtime requirement for retained model utilities. |

## Getting started

Install the declared runtime requirement in an isolated environment, then run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/check_public_boundary.py
```

## Keywords

Adaptive control, control theory, time-series modeling, autoregression, PID control, synthetic testing, independent research.

## Contributing

Contributions are welcome. Useful work includes test coverage, numerical validation of the data-free utilities, documentation, interface design, and carefully scoped empirical-evaluation proposals. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the [research status](docs/STATUS_AND_PLAN.md).

## Documentation

- [Introduction for new readers](docs/INTRODUCTION.md)
- [Current results and discussion](docs/CURRENT_RESULTS_AND_DISCUSSION.md)
- [Research status and plan](docs/STATUS_AND_PLAN.md)
- [Methods scope](docs/METHODS_SCOPE.md)
- [Deferred and dropped directions](docs/DEFERRED_AND_DROPPED_DIRECTIONS.md)
- [Release boundary](docs/RELEASE_BOUNDARY.md)

## License

See [LICENSE](LICENSE).
