# Getting Started

## 1. Clone repository

```bash
git clone <repo-url>
cd lerobot-humanoid-hardware
```

## 2. Read scope and safety first

- `README.md`
- `docs/overview.md`
- `docs/safety.md`

## 3. Preferred startup order (new build)

1. Order buy parts from `hardware/bom/bom_buy.csv`.
2. Print all STL parts from `docs/manufacturing/printing_guide.md`.
3. Commission and check all motors before assembly (`docs/electronics/motor_commissioning.md`).
4. Assemble the robot (`docs/assembly/assembly_guide.md`).
5. Run wiring checks and first power-on runbook (`docs/electronics/check_wiring.md`, `docs/electronics/first_power_on.md`).

## 4. Pick your task flow

- Assembly work: start with `docs/assembly/`
- Manufacturing work: start with `docs/manufacturing/`
- Electronics work: start with `docs/electronics/`

## 5. Runtime dependency

Full robot runtime and model live at:
- https://github.com/Virgileboat/lerobot-humanoid-runtime

`commission_motor.py` in this repo is self-contained and does not require runtime/toolkit imports.

## 6. Commission motors before assembly (required before mechanical assembly)

Detailed procedure: `docs/electronics/motor_commissioning.md`

Guided flow:

```bash
python hardware/config/commission_motor.py wizard --channel can0
```

This wizard can:
- detect motor protocol and ID
- switch to MIT protocol with reboot checkpoints
- assign final motor ID from model ID map
- run motor motion check (`0 deg -> 90 deg for 1 s -> 0 deg -> disable`)

## 7. Before first power-on

Follow both runbooks:
- `docs/electronics/check_wiring.md`
- `docs/electronics/first_power_on.md`

## 8. Support

If you are blocked:
- `virgilebatto@gmail.com`
