# context/ — canonical repo documentation

Stable, ground-truth documentation for honeybee_REVIVE_grasshopper. Distinct from `planning/` (in-flight work). This repo has no `docs/` folder.

`CLAUDE.md` at the repo root is the dispatcher; this folder holds the docs it routes to.

## Index

| Doc | Read when you need… |
|-----|---------------------|
| [`PRD.md`](PRD.md) | What this repo is for and what lives upstream instead |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The two-layer component pattern, the CPython subprocess bridge, subpackage map |
| [`TECH_STACK.md`](TECH_STACK.md) | Dependencies, dev loop, installer, release |
| [`CODING_STANDARDS.md`](CODING_STANDARDS.md) | IPy2.7 rules, the subprocess boundary, formatting |

## Maintenance rule

When a decision changes how components are built or how heavy compute is dispatched, fold it into the relevant doc here.
