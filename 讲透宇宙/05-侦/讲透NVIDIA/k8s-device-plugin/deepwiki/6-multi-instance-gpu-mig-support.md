<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-device-plugin · page 6 Multi-Instance GPU (MIG) Support · fetched 2026-10-26 -->

# Multi-Instance GPU (MIG) Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/lm/machine-type.go](internal/lm/machine-type.go)
- [internal/lm/mig-strategy.go](internal/lm/mig-strategy.go)
- [internal/lm/mig-strategy_test.go](internal/lm/mig-strategy_test.go)
- [internal/lm/resource.go](internal/lm/resource.go)
- [internal/lm/resource_test.go](internal/lm/resource_test.go)
- [internal/mig/mig.go](internal/mig/mig.go)

</details>



## Purpose and Scope

This document describes how the NVIDIA Kubernetes Device Plugin discovers, manages, and exposes Multi-Instance GPU (MIG) devices to Kubernetes workloads. MIG is a feature available on certain NVIDIA GPU architectures (Ampere and later) that allows a single physical GPU to be partitioned into multiple isolated GPU instances, each with dedicated memory and compute resources.

For information about configuring MIG strategies, see [MIG Strategies](#6.1). For details on how MIG devices are discovered and mapped, see [MIG Device Discovery and Profiles](#6.2).

---

## MIG Device Hierarchy

MIG enables partitioning of a physical GPU into smaller, isolated instances. The partitioning follows a two-level hierarchy:

```mermaid
graph TB
    PhysGPU["Physical GPU<br/>(e.g., A100, H100)"]
    
    subgraph "GPU Instance Layer"
        GI1["GPU Instance (GI)<br/>Profile: 3g.20gb"]
        GI2["GPU Instance (GI)<br/>Profile: 2g.10gb"]
    end
    
    subgraph "Compute Instance Layer"
        CI1["Compute Instance (CI)<br/>Profile: 1g.10gb"]
        CI2["Compute Instance (CI)<br/>Profile: 1g.10gb"]
        CI3["Compute Instance (CI)<br/>Profile: 1g.5gb"]
    end
    
    MIG1["MIG Device 1<br/>GI 0, CI 0"]
    MIG2["MIG Device 2<br/>GI 0, CI 1"]
    MIG3["MIG Device 3<br/>GI 1, CI 0"]
    
    PhysGPU --> GI1
    PhysGPU --> GI2
    GI1 --> CI1
    GI1 --> CI2
    GI2 --> CI3
    CI1 --> MIG1
    CI2 --> MIG2
    CI3 --> MIG3
```

**GPU Instance (GI)**: The first level of partitioning that divides GPU memory slices, streaming multiprocessors (SMs), and other resources. Each GI has its own memory allocation and compute resources.

**Compute Instance (CI)**: The second level of partitioning within a GPU Instance. A GI can be further subdivided into one or more CIs, each with its own dedicated compute resources within the parent GI's allocation.

**MIG Device**: The final device handle that corresponds to a specific Compute Instance. This is what gets exposed to containers as a usable GPU resource.

Sources: [internal/mig/mig.go:23-124](), [internal/lm/resource.go:75-108]()

---

## MIG Strategies

The device plugin supports three MIG strategies that determine how MIG-enabled GPUs are exposed to Kubernetes. The strategy is configured via the `mig-strategy` field in the device plugin configuration.

### Strategy Comparison

| Strategy | Full GPUs Exposed | MIG Devices Exposed | Use Case |
|----------|------------------|---------------------|----------|
| `none` | Yes | No | No MIG support; expose only full GPUs regardless of MIG configuration |
| `single` | No | Yes (uniform types only) | All GPUs must have identical MIG configuration |
| `mixed` | Yes (if MIG-disabled) | Yes (if MIG-enabled) | Heterogeneous cluster with both MIG and non-MIG GPUs |

### MIG Strategy Flow

```mermaid
graph TB
    Start["NewResourceLabeler()"]
    CheckStrategy{"config.Flags.MigStrategy"}
    
    NoneStrategy["MigStrategyNone<br/>(internal/lm/mig-strategy.go:31)"]
    SingleStrategy["MigStrategySingle<br/>(internal/lm/mig-strategy.go:32)"]
    MixedStrategy["MigStrategyMixed<br/>(internal/lm/mig-strategy.go:33)"]
    
    DeviceInfo["mig.DeviceInfo.GetDevicesMap()"]
    
    GetMigSingle["newMigStrategySingleLabeler()"]
    GetMigMixed["newMigStrategyMixedLabeler()"]
    
    Merge["Merge() Labelers"]
    
    Start --> CheckStrategy
    CheckStrategy -->|"none"| NoneStrategy
    CheckStrategy -->|"single"| SingleStrategy
    CheckStrategy -->|"mixed"| MixedStrategy
    
    NoneStrategy --> Merge
    SingleStrategy --> DeviceInfo
    MixedStrategy --> DeviceInfo
    
    DeviceInfo --> GetMigSingle
    DeviceInfo --> GetMigMixed
    
    GetMigSingle --> Merge
    GetMigMixed --> Merge
```

Sources: [internal/lm/mig-strategy.go:29-111]()

For details, see [MIG Strategies](#6.1).

---

## MIG Device Discovery

The device plugin discovers MIG devices through a layered abstraction over NVML. The discovery process involves multiple components working together to enumerate and characterize MIG devices.

### Discovery Architecture

```mermaid
graph TB
    Manager["resource.Manager<br/>(interface)"]
    DI["mig.DeviceInfo<br/>(internal/mig/mig.go:24)"]
    Dev["resource.Device<br/>(interface)"]
    
    subgraph "Discovery Methods"
        GDM["GetDevicesMap()"]
        GAMD["GetAllMigDevices()"]
        IME["IsMigEnabled()"]
        GMD["GetMigDevices()"]
    end
    
    subgraph "NVML Abstraction"
        GDH["GetDeviceHandleFromMigDeviceHandle()"]
    end
    
    Manager --> DI
    DI --> GDM
    GDM --> Dev
    Dev --> IME
    DI --> GAMD
    GAMD --> GMD
    GMD --> Dev
    Dev --> GDH
```

Sources: [internal/mig/mig.go:23-124](), [internal/lm/resource.go:81-84]()

### DeviceInfo Component

The `DeviceInfo` struct in `internal/mig/mig.go` provides a high-level interface for querying MIG device information:

**Key Methods**:

| Method | Purpose | Returns |
|--------|---------|---------|
| `GetDevicesMap()` | Returns devices grouped by MIG enabled status | `map[bool][]resource.Device` |
| `AnyMigEnabledDeviceIsEmpty()` | Checks if any MIG GPU has no MIG devices configured | `bool, error` |
| `GetAllMigDevices()` | Returns all MIG devices across all GPUs | `[]resource.Device` |

Sources: [internal/mig/mig.go:41-124]()

For details, see [MIG Device Discovery and Profiles](#6.2).

---

## MIG Resource Naming and Labeling

The device plugin generates resource names and labels for MIG devices based on their profiles and configuration. The naming convention varies by MIG strategy.

### Resource Name Format

**Full GPU**: `nvidia.com/gpu` (defined as `fullGPUResourceName` in [internal/lm/resource.go:30]())

**MIG Device** (mixed strategy): `nvidia.com/mig-<profile>`
- Profile format: `<gi>g.<memory>gb`
- Examples: `nvidia.com/mig-3g.20gb`, `nvidia.com/mig-1g.5gb`

### MIG Label Generation

The `NewMIGResourceLabeler` function in `internal/lm/resource.go` creates a labeler that generates comprehensive labels for MIG devices, including parent device model and MIG attributes.

```mermaid
graph TB
    Input["MIG resource.Device"]
    Labeler["NewMIGResourceLabeler()"]
    
    GetParent["GetDeviceHandleFromMigDeviceHandle()"]
    GetProfile["GetName()"]
    GetAttrs["newMigAttributeLabels()"]
    
    Base["baseLabeler()"]
    
    Input --> Labeler
    Labeler --> GetParent
    Labeler --> GetProfile
    Labeler --> GetAttrs
    Labeler --> Base
```

Sources: [internal/lm/resource.go:75-108](), [internal/lm/resource.go:159-178]()

### Example MIG Labels

For a MIG device, the plugin generates several standard labels:

| Label Key | Value | Description |
|-----------|-------|-------------|
| `.../mig-<profile>.count` | `int` | Number of this MIG type |
| `.../mig-<profile>.product` | `string` | Full product identifier (e.g. `A100-SXM4-40GB-MIG-3g.20gb`) |
| `.../mig-<profile>.replicas` | `int` | Replicas (usually 1 for MIG) |
| `.../mig-<profile>.sharing-strategy` | `string` | Sharing strategy (usually `none` for MIG) |

Sources: [internal/lm/resource.go:159-178](), [internal/lm/resource_test.go:265-437]()

### Product Name Construction

The product name for MIG devices is constructed by combining the parent GPU model name with the MIG profile name. This is handled by `getProductName` in `internal/lm/resource.go`.

Sources: [internal/lm/resource.go:189-206]()

---

