# Config

This folder is for pre-assembly motor commissioning only.

Tool:
- `commission_motor.py`

Typical use:

```bash
python hardware/config/commission_motor.py scan --channel can0
python hardware/config/commission_motor.py wizard --channel can0
python hardware/config/commission_motor.py wizard --channel can0 --motor-model o3 --new-id 4 --yes
```

Scope boundary:
- robot model and runtime control are maintained in https://github.com/Virgileboat/lerobot-humanoid-runtime
