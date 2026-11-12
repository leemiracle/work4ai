<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/go-gpuallocator · page 3 NVIDIA Integration Layer · fetched 2026-10-26 -->

# NVIDIA Integration Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go](vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go)
- [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go](vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go)
- [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_device.go](vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_device.go)
- [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_profile.go](vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_profile.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go)
- [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go](vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go)

</details>



The NVIDIA Integration Layer provides the essential bridge between the go-gpuallocator system and NVIDIA's hardware management libraries. This layer abstracts NVIDIA's low-level NVML (NVIDIA Management Library) and provides high-level device interfaces for GPU enumeration, topology discovery, and Multi-Instance GPU (MIG) management.

For information about how devices are discovered and managed by the allocator, see [Device Discovery and Management](#2.1). For details about the testing infrastructure that mocks these interfaces, see [Mock System](#3.4).

## Architecture Overview

The NVIDIA Integration Layer consists of two primary abstraction levels that work together to provide seamless hardware interaction:

**Integration Layer Architecture**

```mermaid
graph TB
    subgraph "Hardware Layer"
        HW["NVIDIA GPU Hardware"]
        NVML_LIB["libnvidia-ml.so.1<br/>NVIDIA Management Library"]
    end
    
    subgraph "Go Bindings Layer"
        NVML_PKG["go-nvml Package<br/>vendor/github.com/NVIDIA/go-nvml"]
        LIB_GO["lib.go<br/>Library loading & versioning"]
        DEVICE_GO["device.go<br/>Device operations"]
        INTERFACE["nvml.Interface<br/>Main NVML interface"]
    end
    
    subgraph "High-Level Device Layer"
        NVLIB_PKG["go-nvlib Package<br/>vendor/github.com/NVIDIA/go-nvlib"]
        API_GO["api.go<br/>Interface definitions"]
        DEVICE_LIB["device.go<br/>Device wrapper"]
        MIG_DEVICE["mig_device.go<br/>MIG support"]
        MIG_PROFILE["mig_profile.go<br/>Profile management"]
    end
    
    subgraph "Allocator Integration"
        GPU_ALLOC["GPU Allocator<br/>Core System"]
    end
    
    HW --> NVML_LIB
    NVML_LIB --> NVML_PKG
    NVML_PKG --> LIB_GO
    NVML_PKG --> DEVICE_GO
    LIB_GO --> INTERFACE
    DEVICE_GO --> INTERFACE
    
    INTERFACE --> NVLIB_PKG
    NVLIB_PKG --> API_GO
    NVLIB_PKG --> DEVICE_LIB
    NVLIB_PKG --> MIG_DEVICE
    NVLIB_PKG --> MIG_PROFILE
    
    API_GO --> GPU_ALLOC
    DEVICE_LIB --> GPU_ALLOC
    MIG_DEVICE --> GPU_ALLOC
```

Sources: [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go:1-297](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/device.go:1-100](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go:1-91]()

## Core Interface Hierarchy

The integration layer exposes device functionality through a well-defined interface hierarchy that progressively adds capabilities:

**Device Interface Relationships**

```mermaid
graph TB
    subgraph "NVML Layer Interfaces"
        NVML_DEVICE["nvml.Device<br/>Basic NVML operations"]
        NVML_LIB["nvml.Interface<br/>Library management"]
    end
    
    subgraph "NVLIB Device Interfaces"
        DEVICE_IFACE["device.Interface<br/>Main device API"]
        DEVICE_IMPL["device.Device<br/>Extended device ops"]
        MIG_DEVICE_IFACE["MigDevice<br/>MIG-specific interface"]
        MIG_PROFILE_IFACE["MigProfile<br/>Profile management"]
    end
    
    subgraph "Core Operations"
        GET_DEVICES["GetDevices()<br/>Enumerate all GPUs"]
        GET_MIG_DEVICES["GetMigDevices()<br/>Get MIG instances"]
        NEW_DEVICE["NewDevice()<br/>Create device wrapper"]
        VISIT_DEVICES["VisitDevices()<br/>Iterate devices"]
    end
    
    NVML_LIB --> NVML_DEVICE
    NVML_DEVICE --> DEVICE_IMPL
    DEVICE_IFACE --> DEVICE_IMPL
    DEVICE_IMPL --> MIG_DEVICE_IFACE
    DEVICE_IMPL --> MIG_PROFILE_IFACE
    
    DEVICE_IFACE --> GET_DEVICES
    DEVICE_IFACE --> GET_MIG_DEVICES
    DEVICE_IFACE --> NEW_DEVICE
    DEVICE_IFACE --> VISIT_DEVICES
    
    GET_DEVICES --> NEW_DEVICE
    GET_MIG_DEVICES --> MIG_DEVICE_IFACE
    VISIT_DEVICES --> DEVICE_IMPL
```

Sources: [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go:23-38](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:26-40](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_device.go:25-29]()

## Library Loading and Version Management

The NVML library loading system handles dynamic library management and API versioning through a sophisticated abstraction:

| Component | Responsibility | Key Types |
|-----------|---------------|-----------|
| `library` struct | Library lifecycle management | `path`, `refcount`, `dl` |
| `dynamicLibrary` interface | Library loading abstraction | `Open()`, `Close()`, `Lookup()` |
| Version symbol resolution | API compatibility | `updateVersionedSymbols()` |

**Library Loading Flow**

```mermaid
graph LR
    INIT["libnvml = newLibrary()"] --> LOAD["load()"]
    LOAD --> OPEN["dl.Open()"]
    OPEN --> UPDATE["updateVersionedSymbols()"]
    UPDATE --> READY["Library Ready"]
    
    subgraph "Version Resolution"
        V1["nvmlInit = nvmlInit_v1"]
        V2["Check nvmlInit_v2"]
        V2_UPDATE["nvmlInit = nvmlInit_v2"]
        V1 --> V2
        V2 --> V2_UPDATE
    end
    
    UPDATE --> V1
    READY --> CLOSE["close()"]
    CLOSE --> DL_CLOSE["dl.Close()"]
```

Sources: [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go:58-86](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go:103-123](), [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go:201-296]()

## Device Abstraction and Enhancement

The `nvlib` layer wraps NVML devices with additional functionality for GPU allocation use cases:

**Device Wrapper Architecture**

```mermaid
graph TB
    subgraph "NVML Device Operations"
        NVML_DEV["nvml.Device<br/>Basic device handle"]
        GET_NAME["GetName()"]
        GET_UUID["GetUUID()"]
        GET_PCI["GetPciInfo()"]
        GET_MEMORY["GetMemoryInfo()"]
    end
    
    subgraph "Enhanced Device Operations"
        DEVICE["device.Device<br/>Enhanced wrapper"]
        GET_ARCH["GetArchitectureAsString()<br/>Pascal, Volta, Ampere, etc"]
        GET_BRAND["GetBrandAsString()<br/>Tesla, GeForce, Quadro, etc"]
        GET_PCI_BUS["GetPCIBusID()<br/>Formatted bus ID"]
        GET_CUDA_CAP["GetCudaComputeCapabilityAsString()"]
        IS_MIG_CAPABLE["IsMigCapable()"]
        IS_MIG_ENABLED["IsMigEnabled()"]
        IS_FABRIC["IsFabricAttached()"]
    end
    
    subgraph "MIG Operations"
        VISIT_MIG["VisitMigDevices()"]
        VISIT_PROFILES["VisitMigProfiles()"]
        GET_MIG_DEVS["GetMigDevices()"]
        GET_MIG_PROFS["GetMigProfiles()"]
    end
    
    NVML_DEV --> GET_NAME
    NVML_DEV --> GET_UUID
    NVML_DEV --> GET_PCI
    NVML_DEV --> GET_MEMORY
    
    DEVICE --> GET_ARCH
    DEVICE --> GET_BRAND
    DEVICE --> GET_PCI_BUS
    DEVICE --> GET_CUDA_CAP
    DEVICE --> IS_MIG_CAPABLE
    DEVICE --> IS_MIG_ENABLED
    DEVICE --> IS_FABRIC
    
    DEVICE --> VISIT_MIG
    DEVICE --> VISIT_PROFILES
    DEVICE --> GET_MIG_DEVS
    DEVICE --> GET_MIG_PROFS
    
    NVML_DEV --> DEVICE
```

Sources: [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:42-66](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:69-100](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:182-261]()

## MIG (Multi-Instance GPU) Support

The integration layer provides comprehensive MIG support through specialized interfaces for managing GPU partitioning:

| MIG Component | Purpose | Key Methods |
|--------------|---------|-------------|
| `MigDevice` | Individual MIG instance management | `GetProfile()`, NVML device operations |
| `MigProfile` | MIG configuration profiles | `String()`, `Matches()`, `GetInfo()` |
| `MigProfileInfo` | Profile specifications | `C`, `G`, `GB`, `Attributes` |

**MIG Profile Resolution Process**

```mermaid
graph TD
    START["MigDevice.GetProfile()"] --> GET_PARENT["GetDeviceHandleFromMigDeviceHandle()"]
    GET_PARENT --> GET_ATTRS["GetAttributes()"]
    GET_ATTRS --> GET_IDS["GetGpuInstanceId()<br/>GetComputeInstanceId()"]
    GET_IDS --> GET_INSTANCES["parent.GetGpuInstanceById()<br/>gi.GetComputeInstanceById()"]
    GET_INSTANCES --> GET_INFO["gi.GetInfo()<br/>ci.GetInfo()"]
    GET_INFO --> ITERATE_PROFILES["Iterate GPU_INSTANCE_PROFILE_COUNT"]
    
    subgraph "Profile Matching"
        CHECK_GI["Check giProfileInfo.Id == giInfo.ProfileId"]
        CHECK_CI["Check ciProfileInfo.Id == ciInfo.ProfileId"]
        CREATE_PROFILE["lib.NewMigProfile(i, j, k, memoryMB, totalMemory)"]
        CHECK_GI --> CHECK_CI
        CHECK_CI --> CREATE_PROFILE
    end
    
    ITERATE_PROFILES --> CHECK_GI
    CREATE_PROFILE --> CACHE["m.profile = p"]
    CACHE --> RETURN["return profile"]
```

Sources: [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_device.go:60-157](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_profile.go:34-41](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/mig_profile.go:57-120]()

## Device Discovery and Enumeration

The integration layer provides multiple patterns for device access, supporting both individual device operations and bulk enumeration:

**Device Enumeration Patterns**

```mermaid
graph TB
    subgraph "Device Library Interface"
        DEVICELIB["devicelib struct<br/>nvmllib: nvml.Interface<br/>skippedDevices: map[string]struct<br/>verifySymbols: *bool"]
    end
    
    subgraph "Enumeration Methods"
        GET_DEVICES["GetDevices()<br/>[]Device"]
        VISIT_DEVICES["VisitDevices(visit func(int, Device) error)"]
        GET_MIG_DEVICES["GetMigDevices()<br/>[]MigDevice"]
        VISIT_MIG_DEVICES["VisitMigDevices(visit func(...) error)"]
        GET_MIG_PROFILES["GetMigProfiles()<br/>[]MigProfile"]
        VISIT_MIG_PROFILES["VisitMigProfiles(visit func(...) error)"]
    end
    
    subgraph "Device Creation"
        NEW_DEVICE["NewDevice(nvml.Device)"]
        NEW_BY_UUID["NewDeviceByUUID(uuid)"]
        NEW_MIG_DEVICE["NewMigDevice(nvml.Device)"]
        NEW_MIG_BY_UUID["NewMigDeviceByUUID(uuid)"]
    end
    
    subgraph "Device Filtering"
        IS_SKIPPED["isSkipped()<br/>Check skippedDevices map"]
        SKIP_CONFIG["WithSkippedDevices()<br/>DGX Display, NVIDIA DGX Display"]
    end
    
    DEVICELIB --> GET_DEVICES
    DEVICELIB --> VISIT_DEVICES
    DEVICELIB --> GET_MIG_DEVICES
    DEVICELIB --> VISIT_MIG_DEVICES
    DEVICELIB --> GET_MIG_PROFILES
    DEVICELIB --> VISIT_MIG_PROFILES
    
    DEVICELIB --> NEW_DEVICE
    DEVICELIB --> NEW_BY_UUID
    DEVICELIB --> NEW_MIG_DEVICE
    DEVICELIB --> NEW_MIG_BY_UUID
    
    VISIT_DEVICES --> IS_SKIPPED
    IS_SKIPPED --> SKIP_CONFIG
    
    GET_DEVICES --> VISIT_DEVICES
    GET_MIG_DEVICES --> VISIT_MIG_DEVICES
    GET_MIG_PROFILES --> VISIT_MIG_PROFILES
```

Sources: [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go:40-68](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:412-505](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:398-410]()

## Symbol Verification and Error Handling

The integration layer includes robust error handling and optional symbol verification for improved compatibility across different NVIDIA driver versions:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Symbol lookup | `LookupSymbol(name string)` | Verify API availability before use |
| Symbol verification | `hasSymbol(symbol string)` | Check function existence |
| Error handling | NVML return codes | Consistent error propagation |
| Version handling | `updateVersionedSymbols()` | API version compatibility |

The `devicelib` can be configured with `WithVerifySymbols(false)` to skip symbol verification in environments where all symbols are assumed to exist.

Sources: [vendor/github.com/NVIDIA/go-nvml/pkg/nvml/lib.go:92-99](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/device.go:542-551](), [vendor/github.com/NVIDIA/go-nvlib/pkg/nvlib/device/api.go:70-75]()

---

