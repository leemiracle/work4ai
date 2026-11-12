<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/IsaacCapture · page 5 Teleoperation, Retargeting and Session Management · fetched 2026-10-26 -->

# Teleoperation, Retargeting and Session Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/AGENTS.md](docs/AGENTS.md)
- [docs/source/references/migration.rst](docs/source/references/migration.rst)
- [examples/robot_viz/README.md](examples/robot_viz/README.md)
- [src/core/deviceio_trackers/trackers.toml](src/core/deviceio_trackers/trackers.toml)
- [src/core/schema/python/CMakeLists.txt](src/core/schema/python/CMakeLists.txt)
- [src/core/schema/python/schema_module.cpp](src/core/schema/python/schema_module.cpp)
- [src/python/isaaccapture/retargeters/__init__.py](src/python/isaaccapture/retargeters/__init__.py)
- [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py](src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py)
- [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/deviceio_tensor_types.py](src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/deviceio_tensor_types.py)
- [src/python/isaaccapture/retargeting_engine/tensor_types/__init__.py](src/python/isaaccapture/retargeting_engine/tensor_types/__init__.py)
- [src/python/isaaccapture/retargeting_engine/tensor_types/indices.py](src/python/isaaccapture/retargeting_engine/tensor_types/indices.py)
- [src/python/isaaccapture/retargeting_engine/tensor_types/standard_types.py](src/python/isaaccapture/retargeting_engine/tensor_types/standard_types.py)
- [src/python/isaaccapture/schema/__init__.py](src/python/isaaccapture/schema/__init__.py)
- [src/python/isaaccapture/teleop_session_manager/config.py](src/python/isaaccapture/teleop_session_manager/config.py)
- [src/python/isaaccapture/teleop_session_manager/teleop_session.py](src/python/isaaccapture/teleop_session_manager/teleop_session.py)
- [src/python/isaaccapture/viz/robot/assets.py](src/python/isaaccapture/viz/robot/assets.py)
- [tests/cpp/core/schema/CMakeLists.txt](tests/cpp/core/schema/CMakeLists.txt)
- [tests/python/core/cloudxr/conftest.py](tests/python/core/cloudxr/conftest.py)
- [tests/python/core/schema/test_vehicle_io.py](tests/python/core/schema/test_vehicle_io.py)

</details>



## Purpose and Scope

The Python teleoperation layer in `isaaccapture` bridges raw OpenXR / CloudXR tracker data streams with downstream robotic controllers, simulators, and haptic feedback sinks. This parent wiki page outlines the high-level architecture governing session management, the tensor-based retargeting engine, and the catalog of available retargeters. 

For complete technical specifications, configuration parameters, and implementation details, refer to the child pages:
- [Teleop Session Manager](#5.1)
- [Retargeting Engine](#5.2)
- [Retargeter Catalog](#5.3)

Sources: `src/python/isaaccapture/retargeters/__init__.py:1-44` [src/python/isaaccapture/retargeters/__init__.py:1-44](), `src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py:1-40` [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py:1-40]().

---

## High-Level Teleoperation Architecture

The teleoperation subsystem orchestrates data from hardware input sources, passes them through stateless conversion nodes, processes them via retargeting pipelines, and routes commands to robot hardware or visualization twins.

Diagram 1: Natural Language Space to Code Entity Space — Teleoperation Stack
```mermaid
graph TD
    sub5[""XR Headset & Trackers""] -->|OpenXR/CloudXR| code5_io[""DeviceIOSession / DeviceIOReplaySession""]
    code5_io -->|DeviceIO Tracker Payloads| code5_src[""DeviceIO Source Nodes (src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/)""]
    code5_src -->|TensorGroups & Payloads| code5_eng[""Retargeting Engine & Graph (src/python/isaaccapture/retargeting_engine/)""]
    code5_eng -->|Retargeters (src/python/isaaccapture/retargeters/)"| code5_ret[""BaseRetargeter Implementations""]
    code5_ret -->|Command Tensors / Sinks| code5_sink[""Robot Driver / Haptic Sink / Simulation""]
```
Sources: `src/python/isaaccapture/retargeters/__init__.py:1-44` [src/python/isaaccapture/retargeters/__init__.py:1-44](), `src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py:1-40` [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py:1-40]().

---

## 5.1 Teleop Session Manager

The `TeleopSession` class orchestrates the execution loop, initialization parameters (`TeleopSessionConfig`), and resource management for both `LIVE` capture sessions and `REPLAY` pipelines [examples/robot_viz/README.md:1-15](). It manages status monitoring, thread execution boundaries, and safety state machines reacting to clutch triggers and external inputs.

For deep technical details, configuration parameters, and graph execution mechanics, see [Teleop Session Manager](#5.1).

Sources: `examples/robot_viz/README.md:1-15` [examples/robot_viz/README.md:1-15]().

---

## 5.2 Retargeting Engine

The retargeting engine establishes type-safe tensor specifications (`TensorGroupType`, `NDArrayType`) corresponding to FlatBuffer schemas [src/python/isaaccapture/retargeting_engine/tensor_types/standard_types.py:1-58](). Stateless `DeviceIO` source nodes (`HeadSource`, `HandsSource`, `ControllersSource`, etc.) ingest tracker payloads and expose them to graph wiring utilities [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/__init__.py:1-40]().

Diagram 2: Natural Language Space to Code Entity Space — Retargeting Pipeline Data Flow
```mermaid
graph LR
    sub6[""Tracker FlatBuffers""] -->|Payload View| code6_dt[""DeviceIO Tensor Types (deviceio_tensor_types.py)""]
    code6_dt -->|TensorGroupType| code6_st[""Standard Tensor Types (standard_types.py)""]
    code6_st -->|Inputs| code6_ret[""Retargeters (src/python/isaaccapture/retargeters/)""]
    code6_ret -->|Rate-Limited Actions| code6_sink[""HapticSink / Robot Sinks""]
```
Sources: `src/python/isaaccapture/retargeting_engine/tensor_types/standard_types.py:1-58` [src/python/isaaccapture/retargeting_engine/tensor_types/standard_types.py:1-58](), `src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/deviceio_tensor_types.py:1-33` [src/python/isaaccapture/retargeting_engine/deviceio_source_nodes/deviceio_tensor_types.py:1-33]().

For tensor indexing conventions, node wiring, and pipeline design, see [Retargeting Engine](#5.2).

---

## 5.3 Retargeter Catalog

The `isaaccapture.retargeters` package provides a modular catalog of lazy-loaded retargeting classes [src/python/isaaccapture/retargeters/__init__.py:1-44](). These components map human tracking inputs to robot joint commands, end-effector poses, or velocity profiles.

| Category | Representative Classes | Target Devices / Use Cases |
| :--- | :--- | :--- |
| **Dexterous Hands** | `DexHandRetargeter`, `WujiHandRetargeter`, `SharpaHandRetargeter` | Multi-fingered robotic hands (Dex, Wuji SDK, Pinocchio/Pink IK) [src/python/isaaccapture/retargeters/__init__.py:1-44]() |
| **SE(3) & Arms** | `Se3RelRetargeter`, `Se3AbsRetargeter`, `SO101ClutchRetargeter` | Cartesian pose control, absolute/relative deltas, leader arms [src/python/isaaccapture/retargeters/__init__.py:1-44]() |
| **Locomotion & Base** | `LocomotionRootCmdRetargeter`, `FootPedalRootCmdRetargeter`, `SpaceMouseToSe2Retargeter` | Mobile base velocity commands from VR controllers, foot pedals, SpaceMouse [src/python/isaaccapture/retargeters/__init__.py:1-44]() |
| **Safety & Utility** | `EePoseRateLimiter`, `JointRateLimiter`, `TensorReorderer` | Velocity bounds enforcement, safety clamps, tensor flattening [src/python/isaaccapture/retargeters/__init__.py:1-44]() |

For complete implementation details, jump guards, rate-limiting configs, and calibration guides, see [Retargeter Catalog](#5.3).

Sources: `src/python/isaaccapture/retargeters/__init__.py:1-44` [src/python/isaaccapture/retargeters/__init__.py:1-44]().

---

