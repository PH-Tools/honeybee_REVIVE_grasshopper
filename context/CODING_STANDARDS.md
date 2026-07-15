---
DATE: 2026-07-15
STATUS: CANONICAL ENGINEERING STANDARD
---

# honeybee_REVIVE_grasshopper — Coding Standards

## 1. IronPython 2.7 for canvas code

Everything in `honeybee_revive_rhino/` that runs on the Grasshopper canvas must be Python-2.7 / IronPython-2.7 safe. (`scripts/` is CPython.)

- No f-strings/`pathlib`/modern stdlib; comment-style type hints; guard `typing` imports.
- Wrap third-party imports in `try/except` that re-raises a helpful `ImportError`.
- **No pandas/numpy on the canvas.**

## 2. The subprocess boundary

Heavy compute — ADORB, pandas-based resilience graphs — runs in **CPython**, invoked from the IPy2.7 side via `honeybee_revive_rhino/gh_compo_io/run_subprocess.py`. A `GHCompo_*` class that needs heavy compute marshals its inputs, calls the subprocess, and reads results back. Do not try to run pandas/`ph-adorb` heavy paths in-process.

## 3. The component contract

- Logic in `gh_compo_io/<subcat>/<name>.py` (`GHCompo_*`); thin wrapper in `honeybee_revive_grasshopper/src/<Name>.py`.
- **Registry entry mandatory** in `_component_info_.py` for any new/renamed component; names match across wrapper, `ghenv.Component.Name`, and registry key.
- `.ghuser` regenerated inside Grasshopper; commit regenerated `src/*.py` + `user_objects/*.ghuser` together.

## 4. Formatting

- **Black** + **isort**.

## 5. Verification

- Run the **validation comparisons** in `tests/` (`resilience/comparison/`, `adorb/comparison/`) against the Phius reference models. That is the correctness check here; there is no separate unit-test suite.

## Closeout checklist

- [ ] Canvas code is IPy2.7-safe (no f-strings/pathlib; guarded `typing`; comment hints; wrapped 3rd-party imports; **no pandas/numpy**).
- [ ] Heavy compute routed through `run_subprocess.py` to CPython.
- [ ] Registry entry added/updated; names consistent; `.ghuser` regenerated + committed.
- [ ] Relevant `tests/…/comparison/` still match the Phius references.
- [ ] black + isort clean; version not hand-edited.
