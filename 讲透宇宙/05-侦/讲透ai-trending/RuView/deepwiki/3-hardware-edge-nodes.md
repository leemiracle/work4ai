<!-- source: DeepWiki mcp.deepwiki.com · repo ruvnet/RuView · page 3 Hardware & Edge Nodes · fetched 2026-10-30 -->

# Hardware & Edge Nodes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/firmware-ci.yml](.github/workflows/firmware-ci.yml)
- [docs/adr/ADR-363-native-macos-usb-node-onboarding.md](docs/adr/ADR-363-native-macos-usb-node-onboarding.md)
- [docs/adr/README.md](docs/adr/README.md)
- [docs/validation/2026-08-31-macos-usb-node-onboarding.md](docs/validation/2026-08-31-macos-usb-node-onboarding.md)
- [firmware/esp32-csi-node/README.md](firmware/esp32-csi-node/README.md)
- [firmware/esp32-csi-node/RUNBOOK.md](firmware/esp32-csi-node/RUNBOOK.md)
- [firmware/esp32-csi-node/main/CMakeLists.txt](firmware/esp32-csi-node/main/CMakeLists.txt)
- [firmware/esp32-csi-node/main/Kconfig.projbuild](firmware/esp32-csi-node/main/Kconfig.projbuild)
- [firmware/esp32-csi-node/main/adaptive_controller.c](firmware/esp32-csi-node/main/adaptive_controller.c)
- [firmware/esp32-csi-node/main/main.c](firmware/esp32-csi-node/main/main.c)
- [firmware/esp32-csi-node/main/nvs_config.c](firmware/esp32-csi-node/main/nvs_config.c)
- [firmware/esp32-csi-node/main/serial_onboarding.c](firmware/esp32-csi-node/main/serial_onboarding.c)
- [firmware/esp32-csi-node/main/serial_onboarding.h](firmware/esp32-csi-node/main/serial_onboarding.h)
- [firmware/esp32-csi-node/main/serial_onboarding_protocol.c](firmware/esp32-csi-node/main/serial_onboarding_protocol.c)
- [firmware/esp32-csi-node/main/thermal.c](firmware/esp32-csi-node/main/thermal.c)
- [firmware/esp32-csi-node/main/thermal.h](firmware/esp32-csi-node/main/thermal.h)
- [firmware/esp32-csi-node/test/Makefile](firmware/esp32-csi-node/test/Makefile)
- [firmware/esp32-csi-node/test/test_thermal_hysteresis.c](firmware/esp32-csi-node/test/test_thermal_hysteresis.c)
- [firmware/esp32-csi-node/version.txt](firmware/esp32-csi-node/version.txt)

</details>



## Purpose and Scope

This document provides a high-level overview of the ESP32-S3 and ESP32-C6 edge sensing hardware used to capture WiFi Channel State Information (CSI) and perform on-device signal processing. It outlines the node architecture, firmware components, provisioning workflows, edge intelligence tiers, multistatic mesh deployment, and non-ESP32 hardware adapters.

For granular technical details, refer to the respective child pages:
- Provisioning and flashing: [ESP32 Setup & Provisioning](#3.1)
- On-device processing tiers: [Edge Intelligence Tiers](#3.2)
- Mesh coordination and TDM: [Multistatic Mesh & TDM Protocol](#3.3)
- Alternate radios and Wi-Fi scanning: [Alternate Radio Hardware & WiFi Scanning](#3.4)

---

## Hardware Overview

RuView utilizes ESP32-S3 and ESP32-C6 development boards as low-cost CSI sensing nodes. Each node functions as a transmitter and receiver in a multistatic mesh, streaming raw or processed CSI telemetry over UDP.

- **Full CSI capture:** Serializes incoming WiFi CSI into the ADR-018 binary frame format. [firmware/esp32-csi-node/main/csi_collector.c:2-6]()
- **Thermal Monitoring:** On-chip temperature sensor tracking and power throttling via `thermal.c` to protect enclosures. [firmware/esp32-csi-node/main/thermal.c:1-27]()
- **Native USB Onboarding:** Protocol support for secure macOS and serial onboarding (ADR-363). [firmware/esp32-csi-node/README.md:22-35]()
- **Edge Intelligence:** Configurable tiers 0-2 for on-device presence, vitals, and fall detection. [firmware/esp32-csi-node/main/Kconfig.projbuild:77-87]()

Sources: [firmware/esp32-csi-node/README.md:1-36](), [firmware/esp32-csi-node/main/thermal.c:1-27]()

---

## Node Architecture & Code Mapping

The dual-core architecture of the ESP32-S3 separates high-frequency WiFi radio interrupts from heavy DSP calculations. Core 0 handles network stack operations, while Core 1 executes the `edge_processing` pipeline.

```mermaid
graph TB
    subgraph "ESP32_S3_Node [ESP32-S3 Node Architecture]"
        subgraph "Core0 [Core 0 - WiFi & Network]"
            "wifi_csi_cb [wifi_csi_callback]"
            "wifi_init_sta [wifi_init_sta]"
            "stream_sender [stream_sender_send]"
        end
        
        subgraph "Core1 [Core 1 - DSP & Edge Intelligence]"
            "edge_ring_buf [edge_ring_buf_t]"
            "edge_dsp_task [edge_processing_task]"
            "biquad_filter [biquad_process]"
            "welford_var [welford_variance]"
        end
        
        "nvs_config [nvs_config_load]"
        "thermal_mon [thermal_tick]"
    end
    
    "wifi_csi_cb" -->|ring_push| "edge_ring_buf"
    "edge_ring_buf" -->|ring_pop| "edge_dsp_task"
    "edge_dsp_task" --> "biquad_filter"
    "edge_dsp_task" --> "welford_var"
    
    "nvs_config" -.-> "Core0"
    "thermal_mon" -.-> "Core0"
```
*Figure 1: Task distribution across ESP32-S3 cores for network capture and DSP pipeline.*

Sources: [firmware/esp32-csi-node/main/main.c:1-50](), [firmware/esp32-csi-node/main/edge_processing.c:1-20]()

---

## 3.1. ESP32 Setup & Provisioning

Nodes are configured via Non-Volatile Storage (NVS) and provisioned using script tools or native USB workflows. Firmware release builds provide variants for 4MB, 8MB, and 16MB flash layouts across S3 and C6 chipsets.

- **USB Onboarding (ADR-363):** Allows attached serial devices to authenticate via a nonce-bound receipt, verify firmware versions, and update local NVS settings without exposing credentials in logs. [docs/adr/ADR-363-native-macos-usb-node-onboarding.md:21-38]()
- **NVS Configuration:** Managed through `nvs_config.c`, preserving network SSID, target IP, and node identifiers across updates. [firmware/esp32-csi-node/main/nvs_config.c:1-40]()

For complete details on flashing, partition maps, release binaries, and serial setup, see [ESP32 Setup & Provisioning](#3.1).

Sources: [docs/adr/ADR-363-native-macos-usb-node-onboarding.md:1-50](), [firmware/esp32-csi-node/main/nvs_config.c:1-40]()

---

## 3.2. Edge Intelligence Tiers

The firmware implements progressive edge processing tiers controlled by `EDGE_TIER` in `Kconfig.projbuild`:
- **Tier 0:** Raw ADR-018 frame passthrough over UDP. [firmware/esp32-csi-node/main/Kconfig.projbuild:79-84]()
- **Tier 1:** Basic presence and motion detection using local phase variance. [firmware/esp32-csi-node/main/Kconfig.projbuild:85]()
- **Tier 2:** Full vital signs pipeline (breathing/heart rate zero-crossing estimation) and fall detection. [firmware/esp32-csi-node/main/Kconfig.projbuild:86]()
- **Tier 3:** Sandboxed WebAssembly (WASM) runtime execution on Core 1 for hot-loadable custom sensing modules. [firmware/esp32-csi-node/main/main.c:32-34]()

For details on the dual-core DSP pipeline and rate-aware sensing (ADR-347), see [Edge Intelligence Tiers](#3.2).

Sources: [firmware/esp32-csi-node/main/Kconfig.projbuild:77-105]()

---

## 3.3. Multistatic Mesh & TDM Protocol

Multi-node deployments coordinate transmission timing via Time Division Multiplexing (TDM) and channel hopping:
- **TDM Slots:** Configured via `tdm_slot_index` and `tdm_node_count` to prevent packet collisions in multi-node environments. [firmware/esp32-csi-node/main/nvs_config.c:48-51]()
- **ESP-NOW Synchronization:** Epoch alignment (ADR-110) ensures deterministic timing across nodes. [firmware/esp32-csi-node/main/main.c:43]()
- **C6 Low-Power Core:** Leverages ESP32-C6 features for low-power motion gating and antenna selection. [firmware/esp32-csi-node/main/main.c:40-42]()

For details on epoch alignment, secure TDM, and QEMU swarm testing, see [Multistatic Mesh & TDM Protocol](#3.3).

Sources: [firmware/esp32-csi-node/main/main.c:36-45](), [firmware/esp32-csi-node/main/nvs_config.c:41-55]()

---

## 3.4. Alternate Radio Hardware & WiFi Scanning

Beyond ESP32 targets, the system supports alternate capture paths and platform adapters:
- **Realtek RTL8721DX Ameba:** CSI wire protocol support (ADR-323).
- **WiFi Scanning Adapters:** Host-side scanning via Windows WLANAPI, Linux, and macOS interfaces.
- **Hardware Abstraction:** Crate-level abstractions ensuring consistent normalization across chipsets.

For details on non-ESP32 capture protocols and hardware crate abstractions, see [Alternate Radio Hardware & WiFi Scanning](#3.4).

Sources: [.github/workflows/firmware-ci.yml:42-78]()

---

