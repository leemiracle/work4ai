# Subassembly Map (Onshape -> Repo STL Groups)

This map aligns Onshape assembly naming to the current STL folder structure.

## Left leg

- `hipx_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/hipx/`
- `hipy_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/hipz/`
- `thigh_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/thigh/`
- `shin_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/shin/`
- `ankle_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/ankle/`
- ankle transmission parts -> `hardware/cad/stl/biped_platform/left_leg/ankle_mechanism/`
- `foot_subassembly <1>` -> `hardware/cad/stl/biped_platform/left_leg/foot/`

## Right leg

Onshape often uses mirrored names (`*_sym`) and/or second instances (`<2>`).
All right-leg exports map to canonical right-leg folders:

- `hipx_subassembly_sym <1>` / `hipx_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/hipx/`
- `hipy_subassembly_sym <2>` / `hipy_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/hipz/`
- `thigh_subassembly_sym <1>` / `thigh_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/thigh/`
- `shin_subassembly_sym <1>` / `shin_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/shin/`
- `ankle_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/ankle/`
- ankle transmission parts -> `hardware/cad/stl/biped_platform/right_leg/ankle_mechanism/`
- `foot_subassembly <2>` -> `hardware/cad/stl/biped_platform/right_leg/foot/`

## Torso

- torso and upper-body base elements -> `hardware/cad/stl/biped_platform/torso/`
