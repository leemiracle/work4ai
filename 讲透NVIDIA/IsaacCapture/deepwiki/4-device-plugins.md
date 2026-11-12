<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/IsaacCapture · page 4 Device Plugins · fetched 2026-10-26 -->

# Device Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/_data/devices.yaml](docs/source/_data/devices.yaml)
- [docs/source/_ext/ecosystem_grid.py](docs/source/_ext/ecosystem_grid.py)
- [docs/source/_static/css/ecosystem.css](docs/source/_static/css/ecosystem.css)
- [docs/source/_static/logos/htc-vive-dark.png](docs/source/_static/logos/htc-vive-dark.png)
- [docs/source/_static/logos/htc-vive.png](docs/source/_static/logos/htc-vive.png)
- [docs/source/_static/logos/wuji-dark.svg](docs/source/_static/logos/wuji-dark.svg)
- [docs/source/_static/logos/wuji.svg](docs/source/_static/logos/wuji.svg)
- [docs/source/device/spacemouse.rst](docs/source/device/spacemouse.rst)
- [examples/teleop/python/spacemouse_printer_example.py](examples/teleop/python/spacemouse_printer_example.py)
- [src/core/schema/fbs/spacemouse.fbs](src/core/schema/fbs/spacemouse.fbs)
- [src/core/schema/golden/spacemouse.bfbs](src/core/schema/golden/spacemouse.bfbs)
- [src/plugins/CMakeLists.txt](src/plugins/CMakeLists.txt)
- [src/plugins/steering_wheel/CMakeLists.txt](src/plugins/steering_wheel/CMakeLists.txt)
- [src/plugins/steering_wheel/README.md](src/plugins/steering_wheel/README.md)
- [src/plugins/steering_wheel/main.cpp](src/plugins/steering_wheel/main.cpp)
- [src/plugins/steering_wheel/plugin.yaml](src/plugins/steering_wheel/plugin.yaml)
- [src/plugins/steering_wheel/steering_wheel_plugin.hpp](src/plugins/steering_wheel/steering_wheel_plugin.hpp)

</details>



This page provides a high-level overview of `src/plugins`, detailing how individual hardware device plugins are structured, built via CMake, and integrated into the core OpenXR session runtime using `core::SchemaPusher`. Device plugins bridge physical input mechanisms—such as gloves, cameras, pedals, and steering wheels—with the Isaac Teleop core data pipeline.

For detailed information on specific devices and implementations, refer to the child pages:
- **Glove and Hand Tracking Plugins**: [Glove and Hand Tracking Plugins](#4.1)
- **Camera, Pedal, Leader-Arm and Input Device Plugins**: [Camera, Pedal, Leader-Arm and Input Device Plugins](#4.2)
- **Device Documentation and Adding a New Device**: [Device Documentation and Adding a New Device](#4.3)

---

## Plugin Structure and Build Integration

Device plugins reside under `src/plugins/` and are conditionally or unconditionally included based on build configuration flags defined in `src/plugins/CMakeLists.txt` [src/plugins/CMakeLists.txt:7-44](). Each plugin is encapsulated in its own subdirectory containing a `CMakeLists.txt` file, source files, a `plugin.yaml` metadata manifest, and a usage README.

For instance, the steering wheel plugin organizes its build and configuration targets through its local manifest and source definitions:
- `src/plugins/steering_wheel/CMakeLists.txt` [src/plugins/steering_wheel/CMakeLists.txt:1-23]()
- `src/plugins/steering_wheel/plugin.yaml` [src/plugins/steering_wheel/plugin.yaml:1-11]()

Plugins that depend on third-party libraries use scoping macros (such as `isaac_teleop_third_party_scope_begin()`) to isolate compiler warning sets [src/plugins/CMakeLists.txt:7-11]().

```mermaid
graph TD
    subpair["CMake Build Configuration"]
    CMakeLists["src/plugins/CMakeLists.txt"] --> AddDir["add_subdirectory(steering_wheel)"]
    AddDir --> Executable["steering_wheel_plugin"]
    Executable --> Meta["plugin.yaml"]

    Sources: [src/plugins/CMakeLists.txt:7-44](), [src/plugins/steering_wheel/CMakeLists.txt:1-23](), [src/plugins/steering_wheel/plugin.yaml:1-11]()
```

---

## OpenXR Session Injection and Schema Pushing

Device plugins operate as independent processes or threads that sample low-level hardware (such as Linux joystick inputs via `/dev/input/js*`) [src/plugins/steering_wheel/README.md:1-8]() and translate them into strongly-typed data structures. 

Instead of writing directly to volatile memory, plugins link against `oxr::oxr_core` and `pusherio::pusherio` [src/plugins/steering_wheel/CMakeLists.txt:16-20]() to instantiate a `core::SchemaPusher` [src/plugins/steering_wheel/steering_wheel_plugin.hpp:35-61](). This component manages serializing device state through the FlatBuffers schema framework and pushing updates directly into the shared OpenXR session.

```mermaid
graph TD
    Hardware["LinuxJoystickDevice"] -->|read| Plugin["plugins::steering_wheel::SteeringWheelPlugin"]
    Plugin -->|update| Pusher["core::SchemaPusher"]
    Pusher -->|serialize & push| OXR["core::OpenXRSession"]

    Sources: [src/plugins/steering_wheel/steering_wheel_plugin.hpp:35-61](), [src/plugins/steering_wheel/CMakeLists.txt:16-20]()
```

---

## Child Pages Overview

- **4.1 Glove and Hand Tracking Plugins**: Covers MANUS, Sharpa Avatar, Wuji, Haptikos, OGLO tactile, and controller synthetic hands, focusing on SDK integration, hand injection mechanics, and haptics feedback.
- **4.2 Camera, Pedal, Leader-Arm and Input Device Plugins**: Details the OAK camera plugin, generic 3-axis pedals, steering wheels, SpaceMouse, SO-101 and Rebot leader arms, VIVE/controller SE3 trackers, and Noitom/Xsens body trackers.
- **4.3 Device Documentation and Adding a New Device**: Explores documentation pages under `docs/source/device`, the `devices.yaml` ecosystem grid (`docs/source/_data/devices.yaml`), body tracking standards, SOMA, joint-space devices, and instructions from the `add_device` guide.

---

