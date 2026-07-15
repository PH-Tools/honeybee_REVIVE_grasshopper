---
DATE: 2026-07-15
STATUS: CANONICAL
---

# honeybee_REVIVE_grasshopper — Tech Stack

## Runtime

- **IronPython 2.7** for the canvas/component code (`honeybee_revive_rhino/`).
- **CPython** for the heavy compute invoked via `run_subprocess.py` (ADORB, pandas resilience) and for `scripts/`.

## Dependencies

- Runtime: `honeybee-revive`, `ph-adorb` (both **required**; resolved in the Rhino Python path, and installed by the `.ghuser` installer for the CPython side).
- Dev extras: `black`, `isort`, `Grasshopper-stubs`, `Rhino-stubs`, plus `pandas`, `plotly`, `kaleido` (for the CPython-side resilience output/graphs).

## Packaging & install

- Not a pip package — distribution is the `.ghuser` user objects, installed via `hb_revive_installer.ghx` (which also installs the upstream Python libs). `scripts/update_installer_ghx.py` maintains the installer.

## Testing

- Primary tests are **validation comparisons** in `tests/` (`resilience/comparison/`, `adorb/comparison/`) against Phius reference models. `sample_models/` holds inputs. There is no unit-test config block; correctness is checked against references.

## Formatting

- **Black** + **isort** (line length per config).

## Versioning & release

- `bump-my-version` updates `RELEASE_VERSION` in `_component_info_.py` (`[tool.bumpversion]` tracks the current version there). `.github/workflows/release.yml` handles release. Do not hand-edit versions.

## Docs

- No `docs/` folder / docs-hub spoke in this repo.
