# Release Boundary

## Purpose

The public boundary keeps this repository reviewable, data-free, and independent of external research materials. Only tracked files that satisfy the rules below belong in the public tree.

## Included

| Category | Permitted public content |
|---|---|
| Source code | Data-free model utilities and validation helpers that do not fetch data or write research outputs. |
| Tests | Synthetic, in-memory tests that do not create repository data or output paths. |
| Documentation | Scope, limitations, contribution guidance, and methods descriptions without empirical findings or claims beyond the documented scope. |
| Tooling | Checks that operate only on tracked paths and tracked text. |

## Excluded

The public tree excludes datasets; raw and derived outputs; results; figures and figure specifications; downloads; archives; notebooks; caches; external-source material and metadata; access logs; and data-dependent tests. These exclusions apply even when a file is small or generated locally.

## Boundary check

Run the following command from the repository root:

```bash
python tools/check_public_boundary.py
```

The scanner obtains the tracked-file list from Git and reads only those tracked files. It checks prohibited tracked path categories and a small set of unsupported public-claim markers. It neither traverses untracked paths nor reads local data directories.

The scanner is a guardrail, not a substitute for review. Contributors must still verify that a change contains no empirical claims, external identifiers, private details, or material outside this boundary.
