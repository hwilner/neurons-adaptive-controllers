# Deferred and Dropped Directions

This document records public-scope decisions without retaining private research details or outcome values.

| Direction or material | Public-tree decision | Reason |
|---|---|---|
| Data acquisition and download helpers | Dropped from the public tree | Public code must not fetch, organize, or depend on external material. |
| Data-dependent analysis workflows | Dropped from the public tree | They require inputs and derived outputs that are outside the release boundary. |
| Figure generation and specifications | Dropped from the public tree | Figures and their supporting outputs are not part of this data-free release. |
| Archive indexes, access records, and source metadata | Dropped from the public tree | They do not belong in a minimal public software workspace. |
| Empirical comparison or interpretation | Deferred | This tree does not contain the materials needed to support such claims. |
| Notebook-based workflows | Deferred | Notebooks are excluded to keep the public surface reviewable and data-free. |

The retained direction is limited to transparent, reusable computational utilities and synthetic tests. Deferred work is not an implied commitment or release plan.
