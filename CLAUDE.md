# honeybee_REVIVE_grasshopper

The **Grasshopper UI layer** for Honeybee-REVIVE — the Rhino/Grasshopper components that add Phius-REVIVE data to Honeybee models and run the ADORB cost calculation on the canvas. This repo contains *only* the components; the model and the ADORB math live upstream in `honeybee-revive` and `ph-adorb`.

> Research/testing only. Not affiliated with, reviewed, or approved by Phius.

> **Runtime constraint (critical):** the component code in `honeybee_revive_rhino/` runs under **IronPython 2.7** (Rhino's GHPython interpreter). Heavy compute (ADORB, pandas-based resilience) can't run in IPy2.7 — it is shelled out to CPython via `honeybee_revive_rhino/gh_compo_io/run_subprocess.py`. See `context/CODING_STANDARDS.md`.

## What this repo is

Two-package, two-layer architecture (mirrors `honeybee_grasshopper_ph`):

- `honeybee_revive_grasshopper/` — GH-facing: `src/` (thin component wrappers), `user_objects/` (compiled `.ghuser`), `icons/`.
- `honeybee_revive_rhino/` — backend logic: `gh_compo_io/` (`GHCompo_*` classes, grouped by subcategory: `adorb/`, `envelope/`, `equipment/`, `model/`, `resiliency/`, `standards/`), `run_subprocess.py`, `_component_info_.py` (registry).

## Where things live — read before working

| Working on… | Read |
|-------------|------|
| Scope, what belongs here | `context/PRD.md` |
| Component pattern, the CPython subprocess bridge, subpackage map | `context/ARCHITECTURE.md` |
| IPy2.7 rules, the subprocess boundary, formatting | `context/CODING_STANDARDS.md` |
| Deps, dev loop, installer, release | `context/TECH_STACK.md` |
| Current / in-flight work | `planning/STATUS.md` |

Full context index: `context/README.md`. (No `docs/` hub spoke.)

## Hard rules

1. **IronPython 2.7 in `honeybee_revive_rhino/`.** No f-strings/`pathlib`/modern stdlib; type comments; guard `typing`; wrap third-party imports in `try/except`. **No pandas/numpy in the canvas path** — route heavy compute (ADORB, resilience graphs) through `run_subprocess.py` to CPython.
2. **A component = thin GH wrapper + backend `GHCompo_*` class**, with a mandatory entry in `_component_info_.py` (or the component fails to style). Names must match across the `src/` wrapper, `ghenv.Component.Name`, and the registry.
3. **`.ghuser` files are regenerated inside Grasshopper**, not editable here. Commit the regenerated `src/*.py` + `user_objects/*.ghuser` together.
4. **Do not hand-edit versions.** `_component_info_.py` `RELEASE_VERSION` / installer are managed by `bump-my-version` + `.github/workflows/release.yml`.
5. **Validation lives in `tests/`.** `tests/resilience/comparison/` and `tests/adorb/comparison/` compare against Phius reference models — the primary correctness check for this repo.

## Related repos (all under `~/Dropbox/bldgtyp-00/00_PH_Tools/`)

`honeybee_REVIVE` (the model + analysis — **required**) · `PH_ADORB` (the ADORB cost math — **required**) · `honeybee_ph` / `honeybee_grasshopper_ph` (sibling toolchain).
