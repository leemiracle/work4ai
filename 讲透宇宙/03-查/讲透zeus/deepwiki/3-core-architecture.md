<!-- source: DeepWiki mcp.deepwiki.com · repo ml-energy/zeus · page 3 Core Architecture · fetched 2026-10-21 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/getting_started/index.md](docs/getting_started/index.md)
- [docs/index.md](docs/index.md)
- [zeus/__init__.py](zeus/__init__.py)

</details>



## Purpose and Scope

This document explains Zeus's high-level system architecture and how its major components are organized. It covers the layered architecture of the Zeus Python package, the role of the Zeus daemon (`zeusd`), and how these components interact to provide energy measurement and optimization capabilities for deep learning workloads.

For detailed information about the directory structure and module contents, see [Module Organization](#3.1). For information about how Zeus handles privileged operations, see [Privilege Management](#3.2).

---

## Architectural Overview

Zeus follows a layered architecture with three primary layers: the **User API Layer**, the **Device Abstraction Layer**, and the **Hardware Layer**. A separate **Privileged Service Layer** (`zeusd`) handles operations requiring elevated permissions.

```mermaid
graph TB
    subgraph "User API Layer"
        MON["zeus.monitor<br/>ZeusMonitor, PowerMonitor<br/>CarbonEmissionMonitor"]
        OPT["zeus.optimizer<br/>GlobalPowerLimitOptimizer<br/>PipelineFrequencyOptimizer<br/>BatchSizeOptimizer"]
        CLI["zeus.monitor CLI<br/>Command line tools"]
        CB["zeus.callback<br/>Callback base class"]
        METRIC["zeus.metric<br/>Prometheus metrics"]
    end
    
    subgraph "Device Abstraction Layer"
        GPU_MGR["zeus.device.gpu.GPUs<br/>get_gpus()"]
        CPU_MGR["zeus.device.cpu.CPUs<br/>get_cpus()"]
        SOC_MGR["zeus.device.soc.SoC<br/>get_soc()"]
    end
    
    subgraph "Vendor Implementations"
        NVML["NVIDIAGPUs<br/>pynvml"]
        AMD["AMDGPUs<br/>amdsmi"]
        RAPL["RAPLCPUs<br/>sysfs"]
        APPLE["AppleSiliconSoC<br/>IOKit"]
        JETSON["JetsonSoC<br/>I2C rails"]
    end
    
    subgraph "Privileged Service Layer"
        ZEUSD["zeusd daemon<br/>Rust HTTP server<br/>Unix domain socket"]
        ZEUSD_IMPL["ZeusdNVIDIAGPUs<br/>ZeusdRAPLCPUs<br/>Client implementations"]
    end
    
    subgraph "Hardware Layer"
        HW["NVIDIA GPUs | AMD GPUs<br/>Intel/AMD CPUs<br/>Apple Silicon | Jetson SoCs"]
    end
    
    MON --> GPU_MGR
    MON --> CPU_MGR
    MON --> SOC_MGR
    OPT --> GPU_MGR
    OPT --> MON
    CB --> MON
    CB --> OPT
    METRIC --> MON
    
    GPU_MGR --> NVML
    GPU_MGR --> AMD
    GPU_MGR --> ZEUSD_IMPL
    CPU_MGR --> RAPL
    CPU_MGR --> ZEUSD_IMPL
    SOC_MGR --> APPLE
    SOC_MGR --> JETSON
    
    NVML --> HW
    AMD --> HW
    RAPL --> HW
    APPLE --> HW
    JETSON --> HW
    
    ZEUSD_IMPL -.HTTP over socket.-> ZEUSD
    ZEUSD --> HW
```

**Diagram 1: Zeus Layered Architecture**

Sources: [README.md:29-48](), [zeus/__init__.py:1-14](), [docs/getting_started/index.md:132-199]()

---

## Core Subsystems

Zeus is organized into distinct subsystems, each with a well-defined responsibility. The primary subsystems reside in the `zeus/` Python package directory.

### Measurement Subsystem

The `zeus.monitor` module provides programmatic and CLI-based energy and power measurement capabilities.

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `zeus.monitor.energy` | Window-based energy measurement | `ZeusMonitor` |
| `zeus.monitor.power` | Continuous power polling | `PowerMonitor` |
| `zeus.monitor.carbon` | Carbon emission tracking | `CarbonEmissionMonitor` |
| `zeus.monitor.cost` | Energy cost tracking | `EnergyCostMonitor` |
| `zeus.monitor.temperature` | GPU temperature monitoring | `TemperatureMonitor` |

Detailed documentation of these components is in [Energy Measurement](#4).

### Optimization Subsystem

The `zeus.optimizer` module contains algorithms for reducing energy consumption during training.

| Optimizer | Strategy | Target |
|-----------|----------|--------|
| `GlobalPowerLimitOptimizer` | JIT profiling with state machine | GPU power caps |
| `PipelineFrequencyOptimizer` | Graph-cut algorithm | Pipeline stage frequencies |
| `BatchSizeOptimizer` | Multi-armed bandit | Training batch size |

Detailed documentation of these components is in [Energy Optimization](#5).

### Device Abstraction Subsystem

The `zeus.device` module provides a unified interface to heterogeneous hardware.

```mermaid
graph LR
    APP["Application Code"]
    
    subgraph "zeus.device"
        GPU["GPUs interface<br/>get_gpus()"]
        CPU["CPUs interface<br/>get_cpus()"]
        SOC["SoC interface<br/>get_soc()"]
    end
    
    subgraph "Implementations"
        NVML["NVIDIAGPUs"]
        AMD["AMDGPUs"]
        RAPL["RAPLCPUs"]
        APPLE["AppleSiliconSoC"]
        JETSON["JetsonSoC"]
        EMPTY["Empty* fallbacks"]
    end
    
    APP --> GPU
    APP --> CPU
    APP --> SOC
    
    GPU --> NVML
    GPU --> AMD
    GPU --> EMPTY
    CPU --> RAPL
    CPU --> EMPTY
    SOC --> APPLE
    SOC --> JETSON
    SOC --> EMPTY
```

**Diagram 2: Device Abstraction Layer**

The device abstraction layer uses factory functions (`get_gpus()`, `get_cpus()`, `get_soc()`) to instantiate the appropriate implementation based on runtime hardware detection. When hardware is unavailable, the layer falls back to no-op `Empty*` implementations that implement the same interfaces.

Detailed documentation is in [Hardware Abstraction Layer](#6).

Sources: [zeus/__init__.py:1-14](), [README.md:32-41]()

---

## Component Interaction Patterns

Zeus components interact through well-defined interfaces and patterns.

### Measurement Flow

```mermaid
graph TB
    USER["User Application"]
    
    subgraph "zeus.monitor.energy"
        ZM["ZeusMonitor"]
        MW["Measurement Window<br/>begin_window()<br/>end_window()"]
    end
    
    subgraph "zeus.device.gpu"
        GPUS["GPUs instance"]
        ENERGY_API["getTotalEnergyConsumption()"]
        POWER_API["getInstantPowerUsage()"]
    end
    
    subgraph "zeus.device.cpu"
        CPUS["CPUs instance"]
        CPU_ENERGY["getTotalEnergyConsumption()"]
    end
    
    subgraph "Vendor Libraries"
        NVML_LIB["pynvml<br/>nvmlDeviceGetTotalEnergyConsumption"]
        AMDSMI_LIB["amdsmi<br/>amdsmi_get_energy_count"]
        RAPL_FS["sysfs<br/>/sys/class/powercap/intel-rapl"]
    end
    
    USER --> ZM
    ZM --> MW
    MW --> GPUS
    MW --> CPUS
    GPUS --> ENERGY_API
    GPUS --> POWER_API
    CPUS --> CPU_ENERGY
    
    ENERGY_API --> NVML_LIB
    ENERGY_API --> AMDSMI_LIB
    POWER_API --> NVML_LIB
    CPU_ENERGY --> RAPL_FS
```

**Diagram 3: Energy Measurement Data Flow**

The measurement flow follows this pattern:

1. User creates a `ZeusMonitor` instance targeting specific GPU and CPU indices
2. User calls `begin_window()` to start a measurement window
3. `ZeusMonitor` queries `GPUs` and `CPUs` for baseline energy counters
4. Device managers call vendor-specific APIs (NVML, AMDSMI, RAPL)
5. User calls `end_window()` to complete the measurement
6. `ZeusMonitor` calculates energy delta and returns `Measurement` object

### Optimization Flow

```mermaid
graph TB
    USER["Training Loop"]
    
    subgraph "zeus.optimizer.power_limit"
        GPLO["GlobalPowerLimitOptimizer"]
        SM["State Machine<br/>Ready→Warmup→Profiling→Done"]
        PROF["Profile Cache<br/>JSON persistence"]
    end
    
    subgraph "zeus.callback"
        CB_BASE["Callback"]
        ON_BEGIN["on_step_begin()"]
        ON_END["on_step_end()"]
    end
    
    subgraph "zeus.monitor.energy"
        MON["ZeusMonitor<br/>measurement windows"]
    end
    
    subgraph "zeus.device.gpu"
        GPUS["GPUs"]
        SET_PL["setPowerManagementLimit()"]
    end
    
    USER --> GPLO
    GPLO --> CB_BASE
    CB_BASE --> ON_BEGIN
    CB_BASE --> ON_END
    ON_BEGIN --> MON
    ON_BEGIN --> SET_PL
    ON_END --> MON
    MON --> GPUS
    SET_PL --> GPUS
    ON_END --> SM
    SM --> PROF
```

**Diagram 4: Power Limit Optimization Flow**

The optimization flow uses the callback pattern:

1. User instantiates an optimizer (e.g., `GlobalPowerLimitOptimizer`)
2. Optimizer implements the `Callback` interface
3. Training loop invokes `on_step_begin()` before each iteration
4. Optimizer sets GPU power limits via `GPUs.setPowerManagementLimit()`
5. Optimizer starts energy measurement via `ZeusMonitor`
6. Training loop invokes `on_step_end()` after each iteration
7. Optimizer ends measurement and updates state machine
8. After profiling completes, optimizer persists profile to disk

Sources: [zeus/__init__.py:1-14](), [README.md:32-41]()

---

## Privileged Operations Architecture

Zeus handles privileged hardware operations (GPU power/frequency configuration, CPU energy reading) through three deployment patterns. The architecture supports both privileged direct access and unprivileged access via the Zeus daemon.

```mermaid
graph TB
    APP["User Application<br/>Unprivileged process"]
    
    subgraph "zeus.device Implementation Selection"
        DIRECT["Direct Access<br/>NVIDIAGPUs<br/>RAPLCPUs"]
        DAEMON["Daemon Access<br/>ZeusdNVIDIAGPUs<br/>ZeusdRAPLCPUs"]
    end
    
    subgraph "Access Mechanism"
        PYNVML["pynvml library<br/>NVML API calls"]
        SYSFS["sysfs reads<br/>/sys/class/powercap"]
        SOCKET["Unix domain socket<br/>ZEUSD_SOCK_PATH"]
    end
    
    subgraph "Privileged Layer"
        ZEUSD["zeusd daemon<br/>Runs as root<br/>HTTP server"]
    end
    
    subgraph "Hardware"
        GPU["GPU power/freq"]
        CPU["CPU/DRAM energy"]
    end
    
    APP --> DIRECT
    APP --> DAEMON
    
    DIRECT --> PYNVML
    DIRECT --> SYSFS
    DAEMON --> SOCKET
    
    PYNVML --> GPU
    SYSFS --> CPU
    SOCKET --> ZEUSD
    ZEUSD --> GPU
    ZEUSD --> CPU
```

**Diagram 5: Privileged Operations Handling**

The selection between direct and daemon access is automatic:

- If `ZEUSD_SOCK_PATH` environment variable is set, Zeus instantiates `ZeusdNVIDIAGPUs` and `ZeusdRAPLCPUs`
- Otherwise, Zeus attempts direct access via `NVIDIAGPUs` and `RAPLCPUs`
- If direct access fails due to permissions, appropriate exceptions are raised

This architecture is detailed in [Privilege Management](#3.2) and [Zeus Daemon (zeusd)](#7).

Sources: [docs/getting_started/index.md:132-199](), [README.md:43]()

---

## External Integrations

Zeus integrates with external services and frameworks to provide enhanced functionality.

### Framework Integration

```mermaid
graph LR
    subgraph "ML Frameworks"
        PYTORCH["PyTorch<br/>torch.cuda.synchronize()"]
        JAX["JAX<br/>device.synchronize_all_activity()"]
        HF["HuggingFace Transformers<br/>Trainer"]
    end
    
    subgraph "Zeus Integration"
        SYNC["Framework sync<br/>zeus.utils.framework"]
        CB["Callback API<br/>zeus.callback"]
        HF_OPT["HFGlobalPowerLimitOptimizer<br/>TrainerCallback"]
    end
    
    subgraph "Measurement"
        ZM["ZeusMonitor"]
    end
    
    PYTORCH --> SYNC
    JAX --> SYNC
    SYNC --> ZM
    
    HF --> HF_OPT
    HF_OPT --> CB
    CB --> ZM
```

**Diagram 6: Framework Integration Points**

Zeus provides framework-specific adapters:

- **Framework synchronization**: `zeus.utils.framework` provides `sync_execution()` to ensure accurate measurements in async execution environments
- **HuggingFace Trainer**: `HFGlobalPowerLimitOptimizer` implements `TrainerCallback` for seamless integration
- **Generic callbacks**: `zeus.callback.Callback` base class for custom integrations

### External Services

```mermaid
graph LR
    subgraph "zeus.monitor"
        CARBON["CarbonEmissionMonitor"]
        COST["EnergyCostMonitor"]
        METRIC["zeus.metric<br/>Prometheus export"]
    end
    
    subgraph "External APIs"
        ELEC["ElectricityMaps API<br/>Carbon intensity data"]
        OPENI["OpenEI API<br/>Electricity pricing"]
        PROM["Prometheus<br/>Metrics collection"]
    end
    
    CARBON --> ELEC
    COST --> OPENI
    METRIC --> PROM
```

**Diagram 7: External Service Integrations**

- **Carbon tracking**: `CarbonEmissionMonitor` queries ElectricityMaps API for real-time carbon intensity
- **Cost tracking**: `EnergyCostMonitor` queries OpenEI API for electricity pricing data
- **Metrics export**: `zeus.metric` exports power and energy metrics to Prometheus

Sources: [zeus/__init__.py:1-14](), [README.md:32-41]()

---

## Module Structure Summary

The Zeus codebase is organized into these primary modules:

| Module Path | Purpose | Key Entry Points |
|-------------|---------|------------------|
| `zeus.monitor` | Energy/power measurement | `ZeusMonitor`, `PowerMonitor` |
| `zeus.optimizer` | Energy optimization algorithms | `GlobalPowerLimitOptimizer`, `PipelineFrequencyOptimizer` |
| `zeus.device` | Hardware abstraction | `get_gpus()`, `get_cpus()`, `get_soc()` |
| `zeus.callback` | Training integration | `Callback` base class |
| `zeus.metric` | Metrics export | Prometheus integration |
| `zeus.utils` | Utility functions | Framework sync, logging |
| `zeus._legacy` | Legacy code | Research reproducibility |
| `zeus.show_env` | Environment verification | `python -m zeus.show_env` |
| `zeusd/` (Rust) | Privileged daemon | HTTP server |

For a detailed walkthrough of the directory structure and module contents, see [Module Organization](#3.1).

Sources: [README.md:29-48](), [zeus/__init__.py:1-14]()

---

## Design Principles

Zeus's architecture follows these core design principles:

1. **Hardware abstraction**: Unified interfaces hide vendor-specific details
2. **Least privilege**: Privileged operations isolated in optional daemon
3. **Fail-safe defaults**: Graceful degradation via `Empty*` implementations
4. **Extensibility**: Callback and plugin patterns for custom integrations
5. **Zero-overhead**: Measurement uses hardware counters when available
6. **Framework agnostic**: Compatible with PyTorch, JAX, and other frameworks

These principles enable Zeus to run on diverse hardware configurations while maintaining a simple, consistent API for end users.

Sources: [README.md:1-95](), [docs/getting_started/index.md:1-204](), [docs/index.md:1-54]()

---

