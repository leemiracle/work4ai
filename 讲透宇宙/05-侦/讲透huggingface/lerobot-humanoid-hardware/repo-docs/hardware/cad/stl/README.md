# STL Exports

Store manufacturing meshes (`.stl`) here.

Split exports by assembly hierarchy:
- `biped_platform/left_leg/<group>/...`
- `biped_platform/right_leg/<group>/...`
- `biped_platform/torso/...`

Current leg groups:
- `ankle`
- `ankle_mechanism`
- `foot`
- `hipx`
- `hipz`
- `knee_mechanism`
- `shin`
- `thigh`

Filename convention:
- ASCII lowercase snake_case.
- No spaces.
- No parentheses, so no `(1)`, `(2)`, etc.
- Repeated physical instances keep explicit numeric indices in the name (example: `...14...`, `...24...`, `...34...`, `...44...`).

Example:
`right_leg/shin/tibias2_tibias22.stl`
