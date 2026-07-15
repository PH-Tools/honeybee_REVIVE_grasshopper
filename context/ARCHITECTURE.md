---
DATE: 2026-07-15
STATUS: CANONICAL
---

# honeybee_REVIVE_grasshopper — Architecture

## Two layers (same pattern as honeybee_grasshopper_ph)

```
honeybee_revive_grasshopper/   ← GH-facing package
  src/<Name>.py                ← thin canvas wrapper (no logic), compiled into…
  user_objects/<Name>.ghuser   ← installable binary (regenerated in Grasshopper)
  icons/

honeybee_revive_rhino/         ← backend logic
  gh_compo_io/<subcat>/<name>.py   ← GHCompo_* classes (the work)
  gh_compo_io/run_subprocess.py    ← bridge to CPython for heavy compute
  _component_info_.py              ← registry: RELEASE_VERSION, CATEGORY, SUB_CATEGORIES, COMPONENT_PARAMS
```

Wrapper builds the GH interface, instantiates the matching `GHCompo_*`, calls `.run()`. A new/renamed component needs a `_component_info_.py` entry, and the display name must match across the wrapper, `ghenv.Component.Name`, and the registry.

## `gh_compo_io/` subcategories

`adorb/` · `envelope/` · `equipment/` · `model/` · `resiliency/` · `standards/`.

## The CPython subprocess bridge (the key difference from base HBPH)

ADORB and the pandas-based resilience calcs cannot run in IronPython 2.7. So the relevant `GHCompo_*` classes don't compute in-process — they marshal inputs and call **`run_subprocess.py`**, which invokes a CPython interpreter (where `ph-adorb` / `honeybee-revive` output code run), then read the results back. Keep pandas/numpy/heavy logic on the CPython side of that boundary.

## `.ghuser` regeneration

Same as the sibling repo: `.ghuser` are regenerated inside Grasshopper, not editable here; commit the regenerated `src/*.py` + `user_objects/*.ghuser` together. `scripts/update_installer_ghx.py` maintains the installer.

## Validation

`tests/resilience/comparison/` and `tests/adorb/comparison/` compare component output against Phius reference models — the correctness backbone for this UI repo.
