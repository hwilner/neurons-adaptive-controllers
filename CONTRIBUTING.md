# Contributing

Contributions to this independent research repository are welcome. The public project is intentionally limited to data-free model code, synthetic tests, boundary checks, and documentation that does not report empirical outcomes.

## Suitable contributions

Suitable changes include clearer API documentation, input validation, deterministic synthetic tests, maintainable numerical implementations, and improvements to the public-boundary scanner. Keep changes self-contained and explain the behavior they add or clarify without asserting study findings.

## Contributions outside the public boundary

Do not add datasets, downloaded material, access records, source-specific metadata, notebooks, figures, raw or derived outputs, result summaries, or tests that write into repository data or output paths. Work that depends on such material belongs outside this public tree.

## Local checks

Before proposing a change, run the following commands from the repository root:

```bash
python -m unittest discover -s tests -v
python tools/check_public_boundary.py
```

The tests must use synthetic in-memory inputs and must not create repository data, result, figure, download, archive, or cache paths. The scanner examines tracked paths and tracked text only; it does not inspect local untracked material.

## Documentation

Use conservative language. Public documentation should describe scope, assumptions, and limitations, not numerical outcomes, target venues, submission plans, citations, identifiers, or contact details. Public callables should use Google-style docstrings with `Args`, `Returns`, and `Raises` sections where applicable.
