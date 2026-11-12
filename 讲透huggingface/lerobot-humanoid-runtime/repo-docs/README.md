# lerobot_humanoid_runtime

Runtime and calibration stack for a 12-DOF bipedal humanoid (no arms), with:
- simulation control (MuJoCo),
- real robot control (CAN + IMU),
- LeRobot integration controller.

This repository is meant to be used by anyone building this robot. Calibration is mandatory before deployment.

## Safety First

This robot can hurt people and damage itself.

- Always start in `state_only` and check state validity before enabling control.
- Keep a clear physical area around the robot.
- Keep a hardware-level power cutoff ready.
- Do not disable controller safety checks.
- If E-STOP triggers, inspect the reason before retrying.

## Supported Platform

- Raspberry Pi 5
- Ubuntu
- Python 3.13
- `uv` for environment management

## Hardware Reference

Bill of materials / hardware repository:
- <https://github.com/Virgileboat/lerobot-humanoid-hardware>

## What Is In This Repo

- `robot/sim_robot.py`: MuJoCo simulation controller.
- `robot/bipedal_robot.py`: real robot controller (CAN MIT protocol + safety).
- `control/rl_agent.py`: policy inference runner (ONNX/Torch).
- `imu/IMU_integration.py`: IMU backends (`bno055`, `bno085`, `jy901`, `mock`).
- `apps/gamepad_controller.py`: gamepad command source.
- `lerobot_humanoid_lerobot_integration/`: LeRobot robot implementation for this humanoid.
- `tools/scan_motors.py`: CAN bus motor scanner and ID verifier for `can0` and `can1`.
- `tools/interactive_zeroing.py`: interactive manual joint zeroing wizard.
- `tools/imu_calibration_tool.py`: IMU diagnostic & zero-bias calibration tool.
- `tools/joint_nudge_tester.py`: single-joint nudge and motion direction verifier.
- `tools/log_visualizer.py`: controller CSV log visualizer & HTML diagnostic generator.
- `tools/data_acquisition.py`: dataset generation for identification workflows.
- `ipython_helper.py`: practical copy/paste snippets for sim/real operation.

## Setup

1. Clone and init submodules:
```bash
git clone <your-repo-url>
cd lerobot_humanoid_runtime
git submodule update --init --recursive
```

2. Install dependencies with `uv`:
```bash
uv sync
```

3. Install profile by workflow:
```bash
# simulation only
uv sync --extra sim

# real robot runtime (policy + imu + meshcat + gamepad)
uv sync --extra policy --extra imu --extra viz --extra gamepad

# plotting/analysis tools
uv sync --extra tools

# everything
uv sync --extra full
```

## Quick Smoke Test (Simulation)

Use this to validate installation without hardware:

```bash
uv run python - <<'PY'
from robot.sim_robot import SimBipedalRobotController

robot = SimBipedalRobotController(control_hz=200.0, fixed_base=False)
robot.start(mode="control", auto_enable=True)
robot.start_viewer()
print("Simulation started. Close viewer / Ctrl+C to stop.")
PY
```

## Real Robot Bring-Up

### Power and CAN sequence

1. Power robot.
2. Power Raspberry Pi.
3. Bring up CAN if not auto-started:
```bash
sudo ip link set can0 up type can bitrate 1000000 dbitrate 5000000 fd on
sudo ip link set can1 up type can bitrate 1000000 dbitrate 5000000 fd on
```
4. Optionally start MeshCat server (if your setup requires separate server):
```bash
meshcat-server
```
5. Note about startup automation:
   - use custom `systemd` services to auto-start CAN + MeshCat at boot,
   - enable them:
```bash
sudo systemctl enable --now <can-service-name>
sudo systemctl enable --now <meshcat-service-name>
```

### Recommended staged runner

The staged runner enforces pause points:

```bash
uv run python deploy/run_real_policy_sequential.py --policy-dir control/policy/codex_iteration_6
```

Stages:
1. Create robot in `state_only`.
2. Check MeshCat / limits / IMU.
3. Switch to `control`, enable motors, send zero pose.
4. Apply gains and start policy.

### Mock dry-run (no hardware CAN)

Use this to validate controller/policy wiring without a real robot:

```bash
uv run python deploy/run_real_policy_sequential.py \
  --policy-dir control/policy/codex_iteration_6 \
  --use-mock-bus \
  --no-with-imu \
  --no-with-meshcat \
  --no-with-gamepad \
  --no-pause-between-stages
```

Notes:
- This uses in-repo Robstride mock CAN buses for IDs `1..12`.
- Use `--imu-sensor mock` if you want to test IMU plumbing without hardware.
- Replace `--policy-dir` with your own policy folder (`config.yaml` + `policy.onnx`).
- Stop with `Ctrl+C`.

### MeshCat over SSH (remote laptop)

If the robot runs on Pi and you view from another computer, use SSH port forwarding.
Author command:

```bash
ssh -L 7000:localhost:7000 lerobot@172.18.133.90
```

Then open:
- `http://localhost:7000` (MeshCat web UI in this setup).

### IPython workflow (from `ipython_helper.py`)

Use `uv run ipython`, then paste the snippets in [`ipython_helper.py`](./ipython_helper.py).

Key flow:
1. Create IMU + `BipedalRobotController`.
2. `robot.start(mode="state_only", auto_enable=False)`.
3. Validate MeshCat and orientation.
4. `robot.set_mode("control")`, `robot.enable_all()`.
5. Start `RLAgent`.

## LeRobot Integration Mode

In-repo integration module:
- [`lerobot_humanoid_lerobot_integration/lerobot_humanoid.py`](./lerobot_humanoid_lerobot_integration/lerobot_humanoid.py)
- [`lerobot_humanoid_lerobot_integration/config_lerobot_humanoid.py`](./lerobot_humanoid_lerobot_integration/config_lerobot_humanoid.py)

Minimal usage pattern:

```python
from lerobot_humanoid_lerobot_integration import LeRobotHumanoid, LeRobotHumanoidConfig

cfg = LeRobotHumanoidConfig()
robot = LeRobotHumanoid(cfg)
robot.connect()

obs = robot.get_observation()
zero = {name: 0.0 for name in robot.action_features}
robot.send_action(zero)
```

Important:
- Start the robot near its reference posture.
- Current LeRobot controller is less permissive than the classical controller.

### Data Acquisition Script

The identification data acquisition workflow is now included in this repo:
- [`tools/data_acquisition.py`](./tools/data_acquisition.py)

Example:

```bash
uv run python tools/data_acquisition.py \
  --fps 100 \
  --total-duration-s 5.0 \
  --command-mode step \
  --amplitudes-deg 0 -5 5 \
  --experiment-name experiment_5s_A
```

## Calibration Guide (Mandatory)

Goal: align internal robot state estimation with real hardware state.

Detailed step-by-step guide:
- [`CALIBRATION.md`](./CALIBRATION.md)

### 1) Verify wiring and motor IDs

- Confirm all 12 motors respond on expected bus:
  - `can0`: IDs 1..6
  - `can1`: IDs 7..12
- If one side looks mirrored or swapped in visualization, check wiring first.

### 2) Start in read-only mode

- Use `state_only` mode first.
- Inspect joint states in MeshCat before enabling torque.

### 3) Validate signs and offsets

Primary calibration tables:
- [`robot/root_constant.py`](./robot/root_constant.py)
  - `MOTOR_SIGN`
  - `MOTOR_OFFSET_DEG`
  - `JOINT_LIMITS_DEG`
- LeRobot-side constants in [`lerobot_humanoid_lerobot_integration/lerobot_humanoid.py`](./lerobot_humanoid_lerobot_integration/lerobot_humanoid.py)

If estimated pose does not match real pose, this is usually wiring/sign/offset mismatch.

### 4) Enable control only after checks

- Switch to `control`.
- Enable motors.
- Send zero pose.
- Command very small joint motion and verify correct direction.

### 5) Keep safety constraints active

Do not remove:
- state bounds checks,
- command jump guards,
- ankle guards,
- E-STOP logic.

## Policy Directory Layout

Each policy directory under `control/policy/<name>/` should contain:
- `policy.onnx` (required),
- one config file among:
  - `config.yaml`
  - `config.yml`
  - `model_25000_env.yaml`
  - `config.json`

Note:
- Absolute paths found inside some policy config files are training artifacts.
- Runtime deploy uses the local `--policy-dir` files from this repository.

## Logging and Debugging

- Robot controller and RL agent can both produce CSV logs.
- Common log locations:
  - policy folder debug CSV (`--log-name`, `--log-path`),
  - custom paths passed to `RLAgent.from_files(...)`.

Use logs to inspect:
- command vs observed joints,
- control loop timing,
- E-STOP events.

## Common Failures

1. Internal state does not match real pose.
   - Usually wiring/sign/offset mismatch.
   - Re-check CAN routing and calibration tables.

2. No motor feedback.
   - CAN interfaces not up.
   - Bring up `can0` / `can1` and retry.

3. E-STOP triggers at startup.
   - Robot out of safe bounds or ankle guard violation.
   - Place robot closer to neutral and retry in `state_only`.

4. MeshCat not updating.
   - Missing visualization dependencies or server not reachable.
   - Check `meshcat` install and `tcp://127.0.0.1:6000` path.

5. LeRobot startup timeout on connect.
   - Controller now waits for first state response from all motors.
   - If connect fails with missing motor IDs, check CAN bring-up, wiring, and motor power.
