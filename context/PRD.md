---
DATE: 2026-07-15
STATUS: CANONICAL PRD
---

# honeybee_REVIVE_grasshopper — Product Requirements

## 1. Goal

Give practitioners the Grasshopper components to add Phius-REVIVE data to Honeybee models and compute the ADORB cost directly on the canvas. This repo is the **UI layer only**; the model and the ADORB math are upstream.

## 2. Who uses it

REVIVE practitioners/researchers modeling in Rhino/Grasshopper. They install via `hb_revive_installer.ghx` (which also pulls `honeybee-revive` and `ph-adorb`) and wire the components on the canvas.

## 3. What belongs here

- GH component **wrappers** (`honeybee_revive_grasshopper/src/`) + compiled `.ghuser` + icons.
- Backend `GHCompo_*` logic (`honeybee_revive_rhino/gh_compo_io/`: `adorb/`, `envelope/`, `equipment/`, `model/`, `resiliency/`, `standards/`).
- The `run_subprocess.py` bridge that runs CPython-only compute (ADORB, pandas resilience) out of the IPy2.7 canvas.
- Validation test cases (`tests/`) comparing to Phius reference models.

## 4. Non-goals

- **No model logic or ADORB math** — those are `honeybee-revive` and `ph-adorb` (both required).
- **No pandas/heavy compute inside the canvas process** — it shells out to CPython.

## 5. Success criteria

- Components load and run in Rhino's IronPython 2.7.
- ADORB / resilience results match the Phius reference comparisons in `tests/`.
- Component I/O + metadata stay in sync across wrapper, registry, and regenerated `.ghuser`.

## 6. Direction

- Active work in `planning/STATUS.md`.
