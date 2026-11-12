<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DCGM · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [common/ThreeWayCmpDefault.hpp](common/ThreeWayCmpDefault.hpp)
- [modules/nvswitch/DcgmModuleNvSwitch.cpp](modules/nvswitch/DcgmModuleNvSwitch.cpp)
- [nvvs/include/NvvsJsonStrings.h](nvvs/include/NvvsJsonStrings.h)
- [testing/python3/tests/test_dcgm_collectd_plugin.py](testing/python3/tests/test_dcgm_collectd_plugin.py)

</details>



## Purpose and Scope

This document provides an overview of NVIDIA Data Center GPU Manager (DCGM), explaining its purpose, architecture, and key components. For detailed information about specific subsystems, refer to:
- Architecture details: [Architecture](#1.1)
- Installation and setup: [Installation](#1.2)
- Core components and internal APIs: [Core Components](#2)
- Individual modules: [Modules](#3)
- Diagnostic capabilities: [NVVS](#4)
- Building from source: [Building and Development](#5)

Sources: [README.md:1-147]()

## What is DCGM

DCGM is a daemon-based system for monitoring, managing, and diagnosing NVIDIA datacenter GPUs in cluster environments. It provides active health monitoring, comprehensive diagnostics, system alerts, and governance policies including power and clock management. The system is designed to simplify GPU administration, improve resource reliability and uptime, automate administrative tasks, and drive overall infrastructure efficiency.

DCGM supports Linux operating systems on x86_64, Arm (aarch64), and POWER (ppc64le) platforms. The software distribution includes:
- `libdcgm.so` - Core API library
- `nv-hostengine` - Host engine daemon
- `dcgmi` - Command-line interface
- NVVS (NVIDIA Validation Suite) - Diagnostic tool suite
- API bindings for C, Python (`pydcgm`), and Go

Sources: [README.md:1-24]()

## Deployment Models

DCGM supports two deployment models, both using the same `libdcgm.so` library:

```mermaid
graph TB
    subgraph "Standalone Mode"
        CLI1["dcgmi CLI"]
        EXPORTER1["dcgm-exporter"]
        APP1["Custom Application"]
        
        DAEMON["nv-hostengine daemon<br/>TCP/Unix Socket"]
        
        CLI1 -->|"dcgmConnect()<br/>TCP:5555"| DAEMON
        EXPORTER1 -->|"dcgmConnect()<br/>Unix socket"| DAEMON
        APP1 -->|"dcgmConnect()"| DAEMON
        
        DAEMON -->|"NVML API"| GPU1["GPUs"]
    end
    
    subgraph "Embedded Mode"
        APP2["Application"]
        LIB["libdcgm.so<br/>in-process"]
        
        APP2 -->|"dcgmStartEmbedded()"| LIB
        LIB -->|"NVML API"| GPU2["GPUs"]
    end
```

**Standalone Mode**: The `nv-hostengine` daemon runs as a separate process. Client applications connect via TCP (default port 5555) or Unix domain sockets using `dcgmConnect()`. This is the recommended deployment for production environments as it provides isolation, persistence, and allows multiple clients to share a single DCGM instance.

**Embedded Mode**: Applications directly link against `libdcgm.so` and call `dcgmStartEmbedded()` to run the host engine in-process. This mode is useful for testing, development, or single-application deployments.

Sources: [README.md:6-24]()

## Core Architecture

The following diagram shows DCGM's primary components and their relationships with specific code entities:

```mermaid
graph TB
    subgraph "Client Layer"
        DCGMI["dcgmi<br/>CLI Tool"]
        EXPORTER["dcgm-exporter<br/>Prometheus Metrics"]
        COLLECTD["dcgm_collectd_plugin"]
        PYDCGM["pydcgm<br/>Python Bindings"]
    end
    
    subgraph "DCGM API dcgm.so"
        API_FUNCS["Public API Functions<br/>dcgmActionValidate_v2()<br/>dcgmGroupCreate()<br/>dcgmFieldGroupCreate()<br/>dcgmWatchFields()"]
    end
    
    subgraph "Host Engine nv-hostengine"
        ROUTER["Message Router<br/>processModuleCommand()"]
        
        CORE_MOD["Core Module<br/>DCGM_MODULE_ID_CORE<br/>Group management<br/>Field watches"]
        
        CACHE["DcgmCacheManager<br/>m_entityWatchHashTable<br/>m_gpus array<br/>Field data storage"]
        
        subgraph "Module System .so files"
            DIAG_MOD["dcgmmodulediag.so<br/>DcgmDiagManager<br/>DCGM_MODULE_ID_DIAG"]
            
            NVSWITCH_MOD["dcgmmodulenvswitch.so<br/>DcgmModuleNvSwitch<br/>DCGM_MODULE_ID_NVSWITCH"]
            
            SYSMON_MOD["dcgmmodulesysmon.so<br/>DcgmModuleSysmon<br/>DCGM_MODULE_ID_SYSMON"]
            
            HEALTH_MOD["dcgmmodulehealth.so<br/>DCGM_MODULE_ID_HEALTH"]
            
            POLICY_MOD["dcgmmodulepolicy.so<br/>DCGM_MODULE_ID_POLICY"]
            
            PROF_MOD["dcgmmoduleprofiling.so<br/>DCGM_MODULE_ID_PROFILING"]
        end
    end
    
    subgraph "NVVS Diagnostic Suite"
        NVVS_BIN["nvvs executable<br/>Spawned by DcgmDiagManager"]
        PLUGINS["Plugin Libraries<br/>Diagnostic_*.so<br/>MemTest_*.so<br/>TargetedStress_*.so"]
        DIAG_SKUS["diag-skus.yaml<br/>Per-SKU Configuration"]
    end
    
    subgraph "Hardware Interfaces"
        NVML["NVML nvmlDeviceGet*()"]
        NSCQ["NSCQ/NVSDM<br/>NVSwitch Interface"]
        SYSFS["sysfs/procfs<br/>/proc/stat<br/>/sys/class/hwmon"]
    end
    
    DCGMI --> API_FUNCS
    EXPORTER --> API_FUNCS
    COLLECTD --> API_FUNCS
    PYDCGM --> API_FUNCS
    
    API_FUNCS --> ROUTER
    ROUTER --> CORE_MOD
    ROUTER --> DIAG_MOD
    ROUTER --> NVSWITCH_MOD
    ROUTER --> SYSMON_MOD
    ROUTER --> HEALTH_MOD
    ROUTER --> POLICY_MOD
    ROUTER --> PROF_MOD
    
    CORE_MOD <--> CACHE
    DIAG_MOD --> CACHE
    NVSWITCH_MOD --> CACHE
    SYSMON_MOD --> CACHE
    HEALTH_MOD --> CACHE
    POLICY_MOD --> CACHE
    PROF_MOD --> CACHE
    
    DIAG_MOD -->|"fork/exec"| NVVS_BIN
    NVVS_BIN --> PLUGINS
    NVVS_BIN --> DIAG_SKUS
    
    CACHE --> NVML
    NVSWITCH_MOD --> NSCQ
    SYSMON_MOD --> SYSFS
    PLUGINS --> NVML
```

The architecture follows a modular design with clear separation of concerns:

**API Layer (`libdcgm.so`)**: Provides the public C API including functions like `dcgmActionValidate_v2()`, `dcgmGroupCreate()`, and `dcgmWatchFields()`. This layer handles both embedded and remote connections.

**Message Router**: The `processModuleCommand()` function routes API calls to appropriate modules based on `moduleId` and `subCommand` fields in the message header.

**Core Module**: Manages fundamental operations including group management, field watch registration, and client connection handling. It coordinates with `DcgmCacheManager` for data operations.

**Cache Manager (`DcgmCacheManager`)**: Central data repository that maintains `m_entityWatchHashTable` for field watches and `m_gpus` array for GPU information. Collects metrics from hardware via NVML and system interfaces, implements the field watch system, and stores time-series data.

**Specialized Modules**: Each module provides domain-specific functionality:
- **Diag Module** (`dcgmmodulediag.so`): Orchestrates diagnostic runs through NVVS
- **NVSwitch Module** (`dcgmmodulenvswitch.so`): Manages NVSwitch devices via NSCQ/NVSDM
- **Sysmon Module** (`dcgmmodulesysmon.so`): Monitors CPU metrics via sysfs/procfs
- **Health Module**: Performs health checks
- **Policy Module**: Enforces policies
- **Profiling Module**: Collects profiling metrics

**NVVS Suite**: Separate process (`nvvs`) spawned by the Diag module for running diagnostic tests. Uses plugin architecture with per-CUDA-version builds. Configuration comes from `diag-skus.yaml`.

Sources: [README.md:1-147](), [modules/nvswitch/DcgmModuleNvSwitch.cpp:1-580]()

## Entity Hierarchy and Hardware Support

DCGM provides unified monitoring across heterogeneous hardware through its entity system:

```mermaid
graph TB
    subgraph "Entity Types dcgm_field_entity_group_t"
        GPU_ENT["DCGM_FE_GPU<br/>Physical GPUs"]
        GPU_I["DCGM_FE_GPU_I<br/>GPU Instances<br/>MIG"]
        GPU_CI["DCGM_FE_GPU_CI<br/>Compute Instances<br/>MIG"]
        VGPU["DCGM_FE_VGPU<br/>vGPUs"]
        SWITCH["DCGM_FE_SWITCH<br/>NVSwitch Devices"]
        LINK["DCGM_FE_LINK<br/>NVLink Links"]
        CPU["DCGM_FE_CPU<br/>CPU Sockets"]
        CPU_CORE["DCGM_FE_CPU_CORE<br/>CPU Cores"]
    end
    
    subgraph "Cache Manager Storage"
        HASH_TABLE["m_entityWatchHashTable<br/>key: groupId + entityId<br/>value: dcgmcm_watch_info_t"]
        
        GPU_ARRAY["m_gpus[DCGM_MAX_NUM_DEVICES]<br/>dcgmcm_gpu_info_t"]
        
        MIG_MGR["DcgmMigManager<br/>Instance mappings<br/>Profile cache"]
    end
    
    subgraph "Data Sources"
        NVML_SRC["NVML Library<br/>nvmlDeviceGetFieldValues()"]
        NSCQ_SRC["NSCQ Backend<br/>nscq_nvswitch_*()"]
        NVSDM_SRC["NVSDM Backend<br/>Newer NVSwitch API"]
        SYSFS_SRC["System Files<br/>/proc/stat<br/>/sys/class/hwmon<br/>/sys/class/thermal"]
    end
    
    GPU_ENT --> HASH_TABLE
    GPU_I --> HASH_TABLE
    GPU_CI --> HASH_TABLE
    VGPU --> HASH_TABLE
    SWITCH --> HASH_TABLE
    LINK --> HASH_TABLE
    CPU --> HASH_TABLE
    CPU_CORE --> HASH_TABLE
    
    GPU_ENT --> GPU_ARRAY
    GPU_I --> MIG_MGR
    GPU_CI --> MIG_MGR
    
    GPU_ARRAY --> NVML_SRC
    MIG_MGR --> NVML_SRC
    SWITCH --> NSCQ_SRC
    SWITCH --> NVSDM_SRC
    LINK --> NSCQ_SRC
    LINK --> NVSDM_SRC
    CPU --> SYSFS_SRC
    CPU_CORE --> SYSFS_SRC
```

The `DcgmCacheManager` maintains a unified view of all monitored entities through `m_entityWatchHashTable`, keyed by entity group ID and entity ID. Each entity type uses appropriate backend interfaces:

- **GPUs and MIG Instances**: Monitored via NVML (`nvmlDeviceGetFieldValues()`). The `DcgmMigManager` handles bidirectional mapping between DCGM entity IDs and NVML instance IDs
- **NVSwitch Devices and Links**: Accessed through NSCQ (legacy) or NVSDM (newer) backends, selected at runtime by `DcgmModuleNvSwitch`
- **CPUs and CPU Cores**: Monitored by `DcgmModuleSysmon` reading from `/proc/stat`, `/sys/class/hwmon`, and `/sys/class/thermal`

This design allows applications to monitor mixed environments (MIG-enabled and non-MIG GPUs, multi-socket CPUs, NVSwitch fabrics) through a unified API.

Sources: [modules/nvswitch/DcgmModuleNvSwitch.cpp:1-580]()

## Key Capabilities

### GPU Monitoring and Management
- Real-time field monitoring via the watch system with configurable update intervals
- Support for 1000+ fields including clocks, temperatures, power, utilization, memory, PCIe, NVLink
- Historical data retention with time-series storage in `DcgmCacheManager`
- Group-based operations for managing multiple GPUs
- MIG (Multi-Instance GPU) awareness with per-instance metrics

### Diagnostics (NVVS)
Comprehensive GPU validation through `nvvs` executable and plugin suite:
- **Diagnostic Plugin** (`Diagnostic_*.so`): GPU stress testing with GEMM operations
- **Memory Plugin** (`MemTest_*.so`): Memory subsystem validation
- **Targeted Stress** (`TargetedStress_*.so`): Sustained performance testing
- **PCIe Plugin**: Bandwidth and connectivity tests
- **EUD Plugin**: Extended Unit Diagnostics
- Per-GPU-SKU configuration via `diag-skus.yaml`
- Multi-CUDA-version support (11/12/13) for compatibility

### System Monitoring
The Sysmon module (`DcgmModuleSysmon`) provides CPU-level telemetry:
- Per-socket and per-core CPU utilization
- CPU temperatures from hwmon sensors
- CPU power consumption where available
- Integration with GPU metrics for holistic system view

### Health and Policy Management
- Active health monitoring via Health module
- Policy-based governance via Policy module
- Automated violation detection and reporting
- Event subscription for real-time notifications

### External Integrations
- **Kubernetes**: `dcgm-exporter` exports metrics as Prometheus endpoints
- **Collectd**: `dcgm_collectd_plugin` integrates with Collectd daemon
- **Python**: `pydcgm` bindings for Python applications
- **Go**: Go language bindings available

Sources: [README.md:1-147](), [testing/python3/tests/test_dcgm_collectd_plugin.py:1-200]()

## Data Flow and Field Watch System

The field watch system is DCGM's core mechanism for efficient metric collection:

```mermaid
graph LR
    subgraph "Client API Calls"
        WATCH_API["dcgmWatchFields()<br/>dcgmUpdateAllFields()"]
        GET_API["dcgmGetLatestValues()<br/>dcgmGetValuesSince()"]
    end
    
    subgraph "Watch Management"
        ADD_WATCH["AddFieldWatch()<br/>entityGroupId<br/>entityId<br/>fieldId"]
        
        WATCH_INFO["dcgmcm_watch_info_t<br/>monitorIntervalUsec<br/>maxAgeUsec<br/>watchers vector<br/>timeSeries storage"]
    end
    
    subgraph "Data Collection Threads"
        UPDATE_THREAD["Cache Update Thread<br/>ActuallyUpdateAllFields()<br/>nvmlDeviceGetFieldValues()"]
        
        NVSWITCH_TASK["NVSwitch TaskRunner<br/>UpdateField()<br/>AppendSamples()"]
        
        SYSMON_TASK["Sysmon TaskRunner<br/>RecordMetrics()<br/>AppendSamples()"]
    end
    
    subgraph "Storage and Retrieval"
        APPEND["AppendEntityDouble()<br/>AppendEntityInt64()<br/>AppendEntityString()"]
        
        RETRIEVE["GetLatestSample()<br/>GetSamples()<br/>GetInt64Summary()"]
    end
    
    WATCH_API --> ADD_WATCH
    ADD_WATCH --> WATCH_INFO
    
    WATCH_INFO -->|"Calculate min interval"| UPDATE_THREAD
    WATCH_INFO -->|"Field requirements"| NVSWITCH_TASK
    WATCH_INFO -->|"Field requirements"| SYSMON_TASK
    
    UPDATE_THREAD --> APPEND
    NVSWITCH_TASK --> APPEND
    SYSMON_TASK --> APPEND
    
    APPEND --> WATCH_INFO
    WATCH_INFO --> RETRIEVE
    
    GET_API --> RETRIEVE
```

**Watch Registration**: Clients call `dcgmWatchFields()` which creates or updates `dcgmcm_watch_info_t` entries in `m_entityWatchHashTable`. Each watch info tracks multiple watchers with potentially different intervals and retention policies.

**Interval Calculation**: The cache manager calculates the minimum required polling interval across all watchers for each field, optimizing data collection frequency.

**Data Collection**: Three primary collection mechanisms:
- **Pull Model (GPUs)**: Update thread periodically calls `nvmlDeviceGetFieldValues()` based on watch intervals
- **Push Model (NVSwitch)**: `DcgmModuleNvSwitch::UpdateField()` writes samples via `AppendSamples()`
- **Push Model (Sysmon)**: `DcgmModuleSysmon::RecordMetrics()` writes CPU metrics via `AppendSamples()`

**Storage**: Samples are stored in time-series format within each `dcgmcm_watch_info_t`, with automatic retention management based on `maxAgeUsec`.

**Retrieval**: Clients retrieve data via `dcgmGetLatestValues()` or `dcgmGetValuesSince()`, which internally call `GetLatestSample()` or `GetSamples()`.

Sources: [README.md:1-147]()

## Security and Reporting

For security vulnerability reporting, DCGM follows NVIDIA's standard security process. Security issues should be reported through the [NVIDIA Product Security](https://www.nvidia.com/en-us/security) website, not via GitHub issues. This ensures proper CVE creation and community notification.

For non-security bugs and feature requests, use the [GitHub issue tracker](https://github.com/NVIDIA/DCGM/issues).

Sources: [README.md:125-131]()

---

