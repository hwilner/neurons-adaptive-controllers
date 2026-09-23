# Contributing

Contributions to this independent research repository are welcome. The public project is intentionally limited to data-free model code, synthetic tests, boundary checks, and documentation that does not report empirical outcomes.

## Suitable contributions

Suitable changes include clearer API documentation, input validation, deterministic synthetic tests, maintainable numerical implementations, and improvements to the public-boundary scanner. Keep changes self-contained and explain the behavior they add or clarify without asserting study findings.

## Contributions outside the public boundary

Do not add datasets, downloaded material, access records, source-specific metadata, notebooks, figures, raw or derived outputs, result summaries, or tests that write into repository data or output paths. Work that depends on such material belongs outside this public tree.

## Project task workflow

Each atomic task is tracked by a GitHub issue and its matching Project card. When a pull request fully addresses one of those tasks, include `Fixes #<issue-number>`, `Closes #<issue-number>`, or `Resolves #<issue-number>` in the pull-request description. Use a closing keyword only for work that is genuinely complete; use ordinary discussion or a non-closing reference for proposals and partial work. This link gives reviewers a visible relationship between the change and its task, and supports the documented Project-status automation when it is enabled.

## Local checks

Before proposing a change, run the following commands from the repository root:

```bash
python -m unittest discover -s tests -v
python tools/check_public_boundary.py
```

The tests must use synthetic in-memory inputs and must not create repository data, result, figure, download, archive, or cache paths. The scanner examines tracked paths and tracked text only; it does not inspect local untracked material.

## Documentation

Use conservative language. Public documentation should describe scope, assumptions, and limitations, not numerical outcomes, unsupported scope claims, citations, identifiers, or contact details. Public callables should use Google-style docstrings with `Args`, `Returns`, and `Raises` sections where applicable.

## Future Testing Opportunities

### Data-free software or documentation tests contributors can work on now

- Review the documented input assumptions against the existing public interfaces and propose wording that makes the accepted series shape, finiteness requirement, and history requirement easier to understand.
- Add or improve data-free documentation examples that explain the role and limitation of the history-based, PID-style, and baseline utilities without presenting a research outcome.
- Propose synthetic edge-case coverage for existing validation behavior, such as unsuitable histories or non-finite inputs, while keeping any proposed test in memory and free of research outputs.
- Check that README and documentation statements consistently distinguish interface-level synthetic checks from empirical evidence, and submit focused clarification edits where needed.

### Research-facing tests requiring maintainer approval and an appropriate data boundary

- Draft a maintainer-reviewed evaluation plan that defines a neural observation, prediction target, comparison methods, held-out evaluation, uncertainty handling, and an interpretation boundary before any outcomes are examined.
- Propose a bounded test of whether the retained history-based approach provides useful held-out prediction relative to suitable alternatives for a clearly specified setting.
- Propose a test of whether the variables required for a control interpretation, including a goal, measured quantity, error, output, and feedback route, can be explicitly identified or examined.
- Propose safeguards that test whether an apparent model advantage remains after plausible non-control explanations and relevant external influences are considered.

Research-facing proposals must remain outside the public tree until maintainers approve both the work and its data boundary. They should state in advance how supportive and non-supportive outcomes would be interpreted and must not treat prediction alone as evidence of a biological feedback mechanism.
