# Maintaining the repository

Keep one main demonstration notebook in `notebooks/`. It contains the search
implementation, and the tests read those functions directly. A separate copy
of the same implementation would make it easy for the two versions to drift.

Leave the existing research work in `Codes/` until you have a reason to move
it. This preserves links to those files. If you later reorganize that folder,
do it in a separate change and update links at the same time.

## Before merging a change

Run the unit tests and notebook checks from the repository root:

```bash
python -m unittest discover -s tests -v
python tools/check_notebook.py --all-cases
```

When changing the search logic, check both engines and the zero-solution and
all-solution cases. Keep the query-count convention explicit: each check adds
`g_j + 1` queries, and an unsuccessful attempt still has a cost.

If a change affects the demonstration output, run:

```bash
python tools/check_notebook.py --refresh-example
```

Review the notebook figures and the files under `examples/default_run/` before
committing them. The default configuration is ten total qubits, marked state
37, 10,000 attempts and seed 12345. Refresh the README values if they change.

## What to commit

Keep the notebook's small default output so GitHub visitors can read it without
running Python. Keep one reference run in `examples/default_run/`, including
its `run_config.json`. Let local experiments write to `notebook_results/`.

Do not commit virtual environments, downloaded packages, temporary notebooks,
personal file paths or large collections of repeated figures. The `.gitignore`
file covers the common generated files. Review the actual file list before
uploading from a working directory.

Use a branch for changes and merge through a pull request. The included GitHub
Actions workflow checks Python 3.10 and 3.11. Make those checks required for
merging once the first workflow run has succeeded.

## Releases and references

Tag a tested version when you want a stable reference for a paper or a demo.
Describe the algorithm version and the dependency versions in the release
notes. The paper is available as [arXiv:2608.29839](https://arxiv.org/pdf/2608.29839),
with [version history on arXiv](https://arxiv.org/abs/2608.29839).
Keep the paper links in the README and notebook in sync. Record the manuscript
version when equation numbering or the algorithm changes.
Add `CITATION.cff` after confirming the software author
list and citation details; do not infer software authorship from a paper's
author list.

Keep the existing MIT license. If a future addition has different terms, state
those terms for that file rather than silently replacing the repository license.
