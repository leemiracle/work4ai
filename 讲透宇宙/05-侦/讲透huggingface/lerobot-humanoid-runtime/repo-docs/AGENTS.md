# AGENT.md

## Remote Reference

- Remote repository: <https://github.com/Virgileboat/lerobot-humanoid-runtime>
- Repository main branch: <https://github.com/Virgileboat/lerobot-humanoid-runtime/tree/main>
- Current tracked upstream branch: `origin/robot_pi_bundle_lerobot_submodule_test`
- Current working branch URL: <https://github.com/Virgileboat/lerobot-humanoid-runtime/tree/robot_pi_bundle_lerobot_submodule_test>

## Full Project Context

This repository is the execution stack in the LeRobot humanoid project:

1. `lerobot-humanoid-design`: design assumptions and feasibility
2. `lerobot-humanoid-hardware`: build/BOM/wiring/commissioning procedures
3. `lerobot-humanoid-model`: shared model assets consumed by runtime
4. `lerobot-humanoid-runtime`: sim + real control, calibration, deployment (this repo)
5. `lerobot-humanoid-identification`: replay + parameter tuning from collected logs

This repo is where software decisions become physical motion, so safety and compatibility are critical.

## Mission Of This Repo

- run MuJoCo simulation controller
- run real robot controller over CAN + IMU
- execute policy inference
- provide staged deployment and data acquisition flows
- integrate with LeRobot APIs

## Safety-Critical Rules

1. Keep safety checks enabled in controllers.
2. Keep staged startup flow (`state_only` -> checks -> `control`).
3. Do not bypass controller public APIs for direct unsafe writes.
4. Preserve E-stop and limit-protection behavior.
5. Real-hardware changes require mock/sim validation first.

## Critical Paths

- `robot/bipedal_robot.py`: real controller and safety behavior
- `robot/sim_robot.py`: simulation control path
- `control/rl_agent.py`: policy runner
- `deploy/run_real_policy_sequential.py`: staged real deploy sequence
- `imu/IMU_integration.py`: IMU backends and integration
- `tools/data_acquisition.py`: dataset generation for identification workflows
- `lerobot_humanoid_lerobot_integration/`: LeRobot-facing adapter layer

## Cross-Repo Interfaces

- Consumes model assets from `robot/lerobot-humanoid-model`.
- Must remain mechanically consistent with hardware repo conventions.
- Provides logs/datasets consumed by identification workflows.
- Uses design/model assumptions that should stay aligned after updates.

## Validation Before Merge

1. Import/syntax checks pass.
2. Mock staged deploy path runs.
3. Simulation smoke path runs.
4. If data tooling changed, run a short acquisition smoke path.
5. Update docs when behavior/CLI changes (`README.md`, `CALIBRATION.md`, this file).
