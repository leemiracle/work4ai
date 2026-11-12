# AGENT.md

## Remote Reference

- Remote repository: <https://github.com/Virgileboat/lerobot-humanoid-model>
- Default branch: <https://github.com/Virgileboat/lerobot-humanoid-model/tree/main>
- Current tracked upstream branch: `origin/main` (local branch currently `master`)

## Full Project Context

This repository is the shared model layer in the LeRobot humanoid stack:

1. `lerobot-humanoid-design`: generates design assumptions and geometry updates
2. `lerobot-humanoid-hardware`: build-source reference for physical parts
3. `lerobot-humanoid-model`: versioned robot model assets + Python helpers (this repo)
4. `lerobot-humanoid-runtime`: consumes models for sim/real runtime
5. `lerobot-humanoid-identification`: consumes models for MJWarp replay/identification

Changes here propagate directly to runtime and identification behavior.

## Mission Of This Repo

Provide stable, reusable robot model assets and helper APIs:

- MJCF/URDF files for robot variants
- Python package `lerobot_humanoid_models`
- path/spec helpers (`ROBOT_XML`, `get_spec`, constants)

## Critical Files And APIs

- `models/`: model assets by family and format
- `src/lerobot_humanoid_models/_common.py`: path/spec resolution logic
- `src/lerobot_humanoid_models/*/constants.py`: exported constants
- public package imports from `src/lerobot_humanoid_models/*/__init__.py`

## Non-Negotiables

1. Keep existing model family names and import paths stable.
2. Do not break runtime/identification file-path assumptions without coordinated updates.
3. Keep package metadata and included assets consistent (`MANIFEST.in`, package data).
4. If assets move, update helper constants and all references in one change.
5. Prefer additive compatibility when introducing new model variants.

## Validation Before Merge

- `pip install -e .` succeeds.
- Minimal import/use check succeeds:
  - import one family module
  - read `ROBOT_XML`
  - call `get_spec()` in an environment that has optional sim deps.
