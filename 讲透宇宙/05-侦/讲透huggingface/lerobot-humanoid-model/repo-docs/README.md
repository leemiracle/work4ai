# lerobot-humanoid-models

Standalone model repository for LeRobot humanoid variants.

Included model families:
- `bipedal_plateform`
- `bipedal_plateform_no_arms`
- `lerobot_humanoide`

## Install

```bash
pip install -e .
```

## Python usage

```python
from lerobot_humanoid_models.bipedal_plateform_no_arms import get_spec, ROBOT_XML

print(ROBOT_XML)
spec = get_spec()
```

`get_spec()` requires `mujoco` and `mjlab`.

By default, model paths are resolved from the repository `models/` directory.
If needed, set `LEROBOT_HUMANOID_MODELS_DIR` to point to a different models path.
