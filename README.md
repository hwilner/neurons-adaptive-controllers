# Neurons as Adaptive Controllers

## Scope

This repository is an **independent research** software workspace for small, controller-style models and time-series preprocessing relevant to adaptive-control questions. The public tree deliberately contains only data-free implementation and synthetic test coverage; it does not include datasets, analysis outputs, figures, external material, or empirical findings.

## Current status

A public release boundary has been established for the current working tree. The repository provides reusable, data-free model utilities and tests only. This status note supersedes earlier wording in the repository history and prior working tree that described data acquisition, analysis outputs, unsupported research claims or empirical conclusions; those statements are not represented or supported by this public tree.

## Contents

| Path | Contents |
|---|---|
| `src/control_models.py` | Data-free controller-style models, preprocessing, and comparison helpers. |
| `tests/` | Synthetic, file-free unit tests. |
| `tools/check_public_boundary.py` | A tracked-file scanner for the public release boundary. |
| `docs/` | Scope, boundary, status, and contribution guidance. |
| `requirements.txt` | Runtime requirements for the retained model utilities. |

## Getting started

Install the declared runtime requirements in an isolated environment, then run the data-free checks:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/check_public_boundary.py
```

The model utilities can be imported from `src.control_models`. They do not fetch data, read repository data directories, or write outputs.

## Keywords

**adaptive control**, **control theory**, **time-series modeling**, **autoregression**, **PID control**, **synthetic testing**, **independent research**

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and keep proposed changes within the [release boundary](docs/RELEASE_BOUNDARY.md). In particular, submit data-free code, tests, and documentation rather than datasets, outputs, figures, downloads, archives, or external-source metadata.

## Public documentation

- [Current status and plan](docs/STATUS_AND_PLAN.md)
- [Methods scope](docs/METHODS_SCOPE.md)
- [Deferred and dropped directions](docs/DEFERRED_AND_DROPPED_DIRECTIONS.md)
- [Release boundary](docs/RELEASE_BOUNDARY.md)

## License

See [LICENSE](LICENSE).
