# Assembly Guide Outline

## Build Sequence
1. Configure all motors before assembly (see `docs/electronics/motor_commissioning.md`).
2. Print all STL parts (`docs/manufacturing/printing_guide.md`).
3. Build torso first.
4. Build upper leg modules in this strict order (same for left and right): `hipx -> hipy (hipz in repo naming) -> thigh`.
5. In parallel, build lower leg modules in this strict order (same for left and right): `foot -> ankle -> knee_mechanism -> shin -> ankle_mechanism`.
6. Assemble upper leg with lower leg for each side.
7. Integrate both legs with torso, then complete wiring checks and first power-on (`docs/electronics/check_wiring.md`, `docs/electronics/first_power_on.md`).

## Build Paradigm
- Default approach: screws are threaded directly into plastic (no insert) for most plastic threads.
- Exception: shin uses M3 threaded inserts (`4 per shin`, `8 total`), this area is structural.
- Insert bearings first in each subassembly (press or gentle hammer).
- Place motor goupille/pin during the same phase as bearing insertion.
- For subassembly goupilles: place them during assembly except on `thigh` to keep it demountable.
- Knee and ankle each keep one interface slightly loose, but still movable.
- Some fits are intentionally tight; if needed, gently ream/drill to final diameter with a metal drill bit at low speed.
- Applied reference torque: about `5 Nm` for screws into non-structural plastic.
- For motor threaded holes and structural insert areas, use higher torque appropriate for the thread/material.

## Per-Section Template
- Required printed parts (STL names).
- Required purchased parts from `hardware/bom/bom_buy.csv`.
- Assembly steps with photos and torque notes.
- Quality checks (free rotation, no cable pinch, screw length verification).
