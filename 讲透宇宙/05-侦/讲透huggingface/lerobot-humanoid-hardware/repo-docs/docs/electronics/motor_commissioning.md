# Motor Commissioning

Commission every motor before mechanical assembly.

## Preconditions
- Connect only one motor on the CAN bus during commissioning.
- Adapter: `SAVVYCANFD 2CH CANFD adapter` (currently the only proven one in this project).
- Linux CAN interface is up (example: `can0`).

## Recommended Command
```bash
python hardware/config/commission_motor.py wizard --channel can0
```

Non-interactive example:
```bash
python hardware/config/commission_motor.py wizard --channel can0 --motor-model o3 --new-id 4 --yes
```

## What the Wizard Does
1. Detects motor ID and active protocol (`CANopen`, `private`, or `MIT`).
2. Switches motor to `MIT` protocol (with required reboot checkpoints).
3. Applies final motor ID according to motor model mapping.
4. Reboots and verifies final ID and protocol (`MIT`).
5. Runs motion check: set zero, enable, move to `90 deg` for `1 s`, then back to `0 deg`, then disable motor.

## Final ID Map

- `RobStride O0`: IDs `1`, `7`
- `RobStride O2`: IDs `2`, `8`
- `RobStride O3`: IDs `3`, `4`, `9`, `10`
- `RobStride O5`: IDs `5`, `6`, `11`, `12`

Use one motor at a time and assign one of the allowed IDs for its model.

## Batch Policy for This Robot
- Repeat the same process for each motor individually.
- Keep a log table: `serial`, `final_id`, `final_protocol`, `commissioning_date`.
