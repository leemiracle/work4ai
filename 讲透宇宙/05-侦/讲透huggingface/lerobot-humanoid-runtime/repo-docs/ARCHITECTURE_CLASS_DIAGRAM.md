# Architecture Class Diagrams

This document covers the two runtime control paths in this repository:

1. Classical controller: `BipedalRobotController` + `RLAgent`
2. LeRobot integration: `LeRobotHumanoid`

Vector assets:
- [`docs/diagrams/classical_controller_architecture.svg`](./docs/diagrams/classical_controller_architecture.svg)
- [`docs/diagrams/lerobot_integration_architecture.svg`](./docs/diagrams/lerobot_integration_architecture.svg)

Rendered preview:

![Classical Controller Diagram](./docs/diagrams/classical_controller_architecture.svg)

![LeRobot Integration Diagram](./docs/diagrams/lerobot_integration_architecture.svg)

## 1) Classical Controller + RLAgent

```mermaid
classDiagram
direction LR

class BipedalRobotController {
  +mode: str
  +gains: Dict[int, JointGains]
  +action: Dict[int, MotorCommand]
  +state: Dict[int, MotorState]
  +start(mode, auto_enable)
  +stop(disable_motors)
  +set_mode(mode)
  +set_action(left, right, ...)
  +set_joint_gains(motor_id, kp, kd)
  +enable_all()
  +disable_all()
  +request_state_once()
  +get_combined_state_snapshot(include_joint_state)
  +attach_default_meshcat(zmq_url)
}

class JointGains {
  +kp: float
  +kd: float
}

class MotorCommand {
  +position_deg: float
  +velocity_deg_s: float
  +torque_nm: float
  +kp: float?
  +kd: float?
}

class MotorState

class AgentSpec {
  +action_keys: List[str]
  +history_len: int
  +inference_hz: float
  +action_scale: float
  +policy_terms: List[str]
  +joint_vel_source: str
}

class PolicyWrapper {
  +load(policy_path, cfg) PolicyWrapper
  +infer(obs) ndarray
  +expected_input_dim: int?
}

class RLAgent {
  +robot: BipedalRobotController
  +spec: AgentSpec
  +policy: PolicyWrapper
  +from_files(robot, config_path, policy_path, ...)
  +set_command_twist(lin_x, lin_y, yaw_rate)
  +set_command_source(source)
  +start()
  +stop()
  +configure_logging(...)
}

class GamepadController {
  +connect(device_path)
  +start()
  +stop()
  +get_command_twist() Tuple[float,float,float]
}

class IMU {
  +start()
  +stop()
  +read_dict() Dict[str,Any]
}

class BusCAN {
  <<python-can Bus>>
  can0
  can1
}

class PhysicalRobot {
  +contains BusCAN
  +contains IMU
}

BipedalRobotController *-- JointGains : per motor
BipedalRobotController *-- MotorCommand : per motor
BipedalRobotController *-- MotorState : state cache
BipedalRobotController --> PhysicalRobot : control / observe
PhysicalRobot *-- BusCAN
PhysicalRobot *-- IMU

RLAgent *-- AgentSpec
RLAgent *-- PolicyWrapper
RLAgent --> BipedalRobotController : send action
BipedalRobotController --> RLAgent : provide observation
RLAgent ..> GamepadController : optional command source
```

### Runtime behavior (classical path)
- `BipedalRobotController` runs its own control/state loop thread (`_run_loop`).
- `RLAgent` runs its own inference loop thread (`_run_loop`) and calls:
  - `robot.get_combined_state_snapshot(...)` (observation path)
  - `robot.set_action(...)` (action path)
- `GamepadController` is optional and provides command twist to `RLAgent`.

## 2) LeRobot Integration Path

```mermaid
classDiagram
direction LR

class RobotConfig {
  <<lerobot>>
}

class Robot {
  <<lerobot>>
  +connect()
  +disconnect()
  +send_action(action)
  +get_observation()
}

class LeRobotHumanoidConfig {
  +can0_port: str
  +can1_port: str
  +control_hz: float
  +position_kp: dict[int,float]
  +position_kd: dict[int,float]
  +joint_limits_deg: dict[int,tuple]
  +max_command_delta_deg: float
  +ankle_guard_enabled: bool
}

class Motor {
  <<lerobot.motors.Motor>>
}

class RobstrideMotorsBus {
  <<lerobot robstride>>
  +connect(handshake)
  +disconnect(disable_torque)
  +sync_read_all_states()
  +_mit_control_batch(commands)
  +enable_torque()
  +disable_torque()
}

class LeRobotHumanoid {
  +name: str
  +connect(calibrate=True)
  +configure()
  +get_observation() RobotObservation
  +send_action(action) RobotAction
  +disconnect()
  +get_estop_reason() str
  +clear_estop()
}

class BNO055IMU {
  <<IMU_BNO055 backend>>
  +start()
  +get_observation()
  +stop()
}

class PhysicalRobot {
  +contains RobstrideMotorsBus
  +contains BNO055IMU
}

class RobotAction {
  <<lerobot.processor>>
}

class RobotObservation {
  <<lerobot.processor>>
}

RobotConfig <|-- LeRobotHumanoidConfig
Robot <|-- LeRobotHumanoid

LeRobotHumanoid *-- LeRobotHumanoidConfig
LeRobotHumanoid --> PhysicalRobot : control / observe
PhysicalRobot *-- RobstrideMotorsBus : can0 + can1
PhysicalRobot *-- BNO055IMU
RobstrideMotorsBus *-- Motor : mapped motors
LeRobotHumanoid ..> RobotAction
LeRobotHumanoid ..> RobotObservation
```

### Runtime behavior (LeRobot path)
- `LeRobotHumanoid.connect()`:
  - connects both Robstride CAN buses,
  - writes gains (`configure()`),
  - optionally enables torque,
  - starts IMU thread,
  - starts control loop thread (`_run_control_loop`).
- In the diagram, these hardware interfaces are grouped under `PhysicalRobot` (CAN buses + IMU).
- `send_action(...)` updates desired raw targets with safety checks (bounds, jump guard, ankle guard, E-STOP).
- Control loop reads motor states and sends batched MIT commands on both buses in parallel.

## Script-level entry points using these classes
- Classical path:
  - `deploy/run_real_policy_sequential.py`
- LeRobot path:
  - `tools/data_acquisition.py`
  - direct usage via `lerobot_humanoid_lerobot_integration`
