# Assembly

This directory contains step-by-step assembly instructions for biped-platform subassemblies.

Inputs used for assembly writing:
- STL layout: `hardware/cad/stl/biped_platform/`
- Total BOM (includes STL): `hardware/bom/bom.csv`
- Buy BOM (no STL): `hardware/bom/bom_buy.csv`
- Main assembly guide: `docs/assembly/assembly_guide.md`
- Motor commissioning workflow: `docs/electronics/motor_commissioning.md`
- Printing list: `docs/manufacturing/printing_guide.md`
- Assembly photos: `docs/assembly/photos/`

Recommended structure per assembly doc:
- prerequisites (printed parts, hardware, tools)
- step-by-step operations
- fastener callouts per step
- quality checks at the end of each step

Current mapping:
- `docs/assembly/subassembly_map.md`

Guide set:
- `assembly_guide.md`: ordered build sequence + per-subassembly components + key assembly constraints
- `assembly_guide_outline.md`: compact sequence reference
