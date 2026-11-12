<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/go-nvlib · page 7 System Information Package · fetched 2026-10-26 -->

# System Information Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pkg/nvlib/device/api.go](pkg/nvlib/device/api.go)
- [pkg/nvlib/device/device.go](pkg/nvlib/device/device.go)
- [pkg/nvlib/info/options.go](pkg/nvlib/info/options.go)

</details>



## Purpose and Scope

The `pkg/nvlib/info` package provides a high-level interface for gathering comprehensive GPU system information. It aggregates data from multiple sources including NVML, the device management layer, and platform-specific property extractors to deliver a unified view of the GPU environment.

This package is distinct from the lower-level components it depends on:
- For GPU device discovery and management, see [GPU Device Management](#3)
- For NVML bindings reference, see [NVML Bindings Reference](#6)
- For hardware topology discovery, see [Hardware Topology Discovery](#5)

The info package sits at the highest abstraction layer, orchestrating these components to provide system-wide GPU information suitable for configuration generation, system validation, and runtime environment discovery.

---

## Package Architecture

The info package implements a modular architecture that separates concerns between configuration, property extraction, and platform detection.

### Component Structure

```mermaid
graph TB
    subgraph "info Package Interface"
        INFO_IFACE["info.Interface"]
        OPTIONS["options struct<br/>- devicelib<br/>- nvmllib<br/>- logger<br/>- root<br/>- propertyExtractor<br/>- platform"]
    end
    
    subgraph "Core Components"
        PROP_EXT["PropertyExtractor<br/>interface"]
        PLATFORM["Platform<br/>type"]
        ROOT["root<br/>type"]
        LOGGER["basicLogger<br/>interface"]
    end
    
    subgraph "Dependencies"
        DEVICE_LIB["device.Interface<br/>Device management"]
        NVML_LIB["nvml.Interface<br/>NVML operations"]
    end
    
    INFO_IFACE --> OPTIONS
    OPTIONS --> PROP_EXT
    OPTIONS --> PLATFORM
    OPTIONS --> ROOT
    OPTIONS --> LOGGER
    OPTIONS --> DEVICE_LIB
    OPTIONS --> NVML_LIB
    
    PROP_EXT -.implemented by.-> PLATFORM_IMPL["Platform-specific<br/>implementations"]
```

**Sources:** [pkg/nvlib/info/options.go:1-71]()

### Interface Design

The info package follows the same interface-driven design pattern used throughout go-nvlib, allowing for dependency injection and testing with mock implementations.

```mermaid
graph LR
    subgraph "Construction"
        NEW["New(opts ...Option)<br/>info.Interface"]
    end
    
    subgraph "Option Functions"
        OPT_DEVICE["WithDeviceLib(devicelib)"]
        OPT_NVML["WithNvmlLib(nvmllib)"]
        OPT_LOGGER["WithLogger(logger)"]
        OPT_ROOT["WithRoot(root)"]
        OPT_EXTRACTOR["WithPropertyExtractor(extractor)"]
        OPT_PLATFORM["WithPlatform(platform)"]
    end
    
    subgraph "Resulting Interface"
        INFO_IF["info.Interface<br/>System info methods"]
    end
    
    NEW --> OPT_DEVICE
    NEW --> OPT_NVML
    NEW --> OPT_LOGGER
    NEW --> OPT_ROOT
    NEW --> OPT_EXTRACTOR
    NEW --> OPT_PLATFORM
    
    OPT_DEVICE --> INFO_IF
    OPT_NVML --> INFO_IF
    OPT_LOGGER --> INFO_IF
    OPT_ROOT --> INFO_IF
    OPT_EXTRACTOR --> INFO_IF
    OPT_PLATFORM --> INFO_IF
```

**Sources:** [pkg/nvlib/info/options.go:25-71]()

---

## Configuration Options

The info package provides several configuration options through functional option pattern. Each option is defined as a function that modifies the internal `options` struct.

### Available Options

| Option Function | Purpose | Parameter Type |
|----------------|---------|----------------|
| `WithDeviceLib` | Sets the device library for GPU enumeration | `device.Interface` |
| `WithNvmlLib` | Sets the NVML library for low-level operations | `nvml.Interface` |
| `WithLogger` | Configures logging output | `basicLogger` |
| `WithRoot` | Sets filesystem root for property extraction | `string` |
| `WithPropertyExtractor` | Sets custom property extraction implementation | `PropertyExtractor` |
| `WithPlatform` | Explicitly sets the platform type | `Platform` |

**Sources:** [pkg/nvlib/info/options.go:28-70]()

### Option Implementation Pattern

```mermaid
graph TB
    subgraph "Option Type Definition"
        OPT_TYPE["type Option func(*options)"]
    end
    
    subgraph "Example: WithDeviceLib"
        WDL_FUNC["WithDeviceLib(devicelib device.Interface)<br/>returns Option"]
        WDL_IMPL["func(i *options) {<br/>  i.devicelib = devicelib<br/>}"]
    end
    
    subgraph "Example: WithRoot"
        WR_FUNC["WithRoot(r string)<br/>returns Option"]
        WR_IMPL["func(i *options) {<br/>  i.root = root(r)<br/>}"]
    end
    
    OPT_TYPE -.defines.-> WDL_FUNC
    OPT_TYPE -.defines.-> WR_FUNC
    
    WDL_FUNC --> WDL_IMPL
    WR_FUNC --> WR_IMPL
```

**Sources:** [pkg/nvlib/info/options.go:26-54]()

---

## Property Extraction System

The `PropertyExtractor` interface provides an abstraction for retrieving system properties that may vary by platform or deployment environment. This design allows the info package to adapt to different GPU platforms (e.g., bare metal, containerized, virtualized) without changing its core logic.

### PropertyExtractor Interface

The `PropertyExtractor` interface is referenced in the options as a pluggable component that can be swapped for testing or to support different environments.

```mermaid
graph TB
    subgraph "PropertyExtractor Interface"
        PE_IF["PropertyExtractor<br/>interface"]
    end
    
    subgraph "Usage in Options"
        OPT_STRUCT["options struct"]
        PE_FIELD["propertyExtractor PropertyExtractor"]
        WITH_PE["WithPropertyExtractor(propertyExtractor)"]
    end
    
    subgraph "Purpose"
        TEST["Testing with mocks"]
        ENV["Environment-specific<br/>property extraction"]
        FS["Filesystem-based<br/>property reading"]
    end
    
    PE_IF --> PE_FIELD
    PE_FIELD --> OPT_STRUCT
    WITH_PE --> OPT_STRUCT
    
    PE_IF --> TEST
    PE_IF --> ENV
    PE_IF --> FS
```

**Sources:** [pkg/nvlib/info/options.go:56-63]()

### Root Filesystem Configuration

The `root` type represents the filesystem root for property extraction, allowing the info package to read system properties from non-standard locations (useful in containerized environments or for testing).

```mermaid
graph LR
    subgraph "Root Configuration"
        ROOT_TYPE["root type"]
        WITH_ROOT["WithRoot(r string) Option"]
    end
    
    subgraph "Common Use Cases"
        CONTAINER["Container environments<br/>/host filesystem mounts"]
        TEST_FS["Testing<br/>/tmp/test-sysfs"]
        CHROOT["Chroot environments"]
    end
    
    WITH_ROOT --> ROOT_TYPE
    ROOT_TYPE --> CONTAINER
    ROOT_TYPE --> TEST_FS
    ROOT_TYPE --> CHROOT
```

**Sources:** [pkg/nvlib/info/options.go:49-54]()

---

## Platform Detection

The `Platform` type allows the info package to adapt its behavior based on the deployment platform. This is particularly important for distinguishing between different GPU virtualization technologies and bare-metal deployments.

### Platform Types

The `Platform` type can be explicitly set via `WithPlatform` option, allowing applications to override automatic detection or specify platform-specific behavior.

```mermaid
graph TB
    subgraph "Platform Configuration"
        PLATFORM_TYPE["Platform type"]
        WITH_PLATFORM["WithPlatform(platform Platform)"]
    end
    
    subgraph "Potential Platform Values"
        BARE_METAL["Bare Metal<br/>Direct hardware access"]
        VGPU["vGPU<br/>Virtual GPU via MDEV"]
        PASS_THROUGH["GPU Passthrough<br/>VM with dedicated GPU"]
        MIG["MIG<br/>Multi-Instance GPU"]
    end
    
    WITH_PLATFORM --> PLATFORM_TYPE
    PLATFORM_TYPE -.may represent.-> BARE_METAL
    PLATFORM_TYPE -.may represent.-> VGPU
    PLATFORM_TYPE -.may represent.-> PASS_THROUGH
    PLATFORM_TYPE -.may represent.-> MIG
```

**Sources:** [pkg/nvlib/info/options.go:65-70]()

---

## Integration with Device Library

The info package heavily relies on the device library to enumerate and query GPUs. This integration provides access to high-level device abstractions while maintaining separation of concerns.

### Device Library Integration Flow

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Info as "info.Interface"
    participant Options as "options struct"
    participant DevLib as "device.Interface"
    participant Device as "device.Device"
    
    Note over App,Device: Initialization Phase
    App->>Info: New(WithDeviceLib(devicelib))
    Info->>Options: Store devicelib
    
    Note over App,Device: Information Gathering Phase
    App->>Info: GatherSystemInfo()
    Info->>DevLib: GetDevices()
    DevLib-->>Info: []Device
    
    loop For each device
        Info->>Device: GetArchitectureAsString()
        Device-->>Info: "Ampere"
        Info->>Device: GetBrandAsString()
        Device-->>Info: "Tesla"
        Info->>Device: IsMigCapable()
        Device-->>Info: true
        Info->>Device: GetPCIBusID()
        Device-->>Info: "0000:3b:00.0"
    end
    
    Info-->>App: SystemInfo
```

**Sources:** [pkg/nvlib/info/options.go:28-32](), [pkg/nvlib/device/device.go:26-41]()

### Device Properties Accessible via Info Package

The info package can access all device properties through the `device.Interface`:

| Property Method | Return Type | Description |
|----------------|-------------|-------------|
| `GetArchitectureAsString()` | `string` | GPU architecture (Ampere, Hopper, etc.) |
| `GetBrandAsString()` | `string` | GPU brand (Tesla, Quadro, GeForce, etc.) |
| `GetCudaComputeCapabilityAsString()` | `string` | CUDA compute capability version |
| `GetMigDevices()` | `[]MigDevice` | MIG devices on this GPU |
| `GetMigProfiles()` | `[]MigProfile` | Available MIG profiles |
| `GetPCIBusID()` | `string` | PCI bus identifier |
| `IsCoherent()` | `bool` | Coherent memory access capability |
| `IsFabricAttached()` | `bool` | GPU fabric attachment status |
| `IsMigCapable()` | `bool` | MIG capability |
| `IsMigEnabled()` | `bool` | MIG enabled status |

**Sources:** [pkg/nvlib/device/device.go:26-41]()

---

## Integration with NVML

The info package can optionally use NVML directly for system-level queries that don't require device-specific context. This is configured through the `WithNvmlLib` option.

### NVML Integration Pattern

```mermaid
graph TB
    subgraph "info Package"
        INFO["info.Interface"]
        OPTS["options.nvmllib"]
    end
    
    subgraph "NVML Library"
        NVML_IF["nvml.Interface"]
        SYS_QUERY["System Queries<br/>- GetDriverVersion<br/>- GetCudaDriverVersion<br/>- GetProcessName"]
        DEV_QUERY["Device Queries<br/>- DeviceGetCount<br/>- DeviceGetHandleByIndex<br/>- DeviceGetHandleByUUID"]
    end
    
    subgraph "Use Cases"
        SYS_INFO["System-level info<br/>Driver versions, counts"]
        VALIDATION["Validation<br/>NVML availability check"]
        CROSS_REF["Cross-reference<br/>with device library data"]
    end
    
    INFO --> OPTS
    OPTS --> NVML_IF
    NVML_IF --> SYS_QUERY
    NVML_IF --> DEV_QUERY
    
    SYS_QUERY --> SYS_INFO
    DEV_QUERY --> VALIDATION
    DEV_QUERY --> CROSS_REF
```

**Sources:** [pkg/nvlib/info/options.go:42-47]()

---

## Logging Integration

The info package supports logging through the `basicLogger` interface, allowing applications to track information gathering operations and debug issues.

### Logger Interface Pattern

```mermaid
graph LR
    subgraph "Logger Configuration"
        BASIC_LOGGER["basicLogger<br/>interface"]
        WITH_LOGGER["WithLogger(logger basicLogger)"]
    end
    
    subgraph "Logger Storage"
        OPTIONS_LOGGER["options.logger"]
    end
    
    subgraph "Logging Use Cases"
        DEBUG["Debug property extraction"]
        ERROR["Error reporting"]
        TRACE["Trace device enumeration"]
    end
    
    WITH_LOGGER --> OPTIONS_LOGGER
    BASIC_LOGGER --> OPTIONS_LOGGER
    OPTIONS_LOGGER --> DEBUG
    OPTIONS_LOGGER --> ERROR
    OPTIONS_LOGGER --> TRACE
```

**Sources:** [pkg/nvlib/info/options.go:35-40]()

---

## Typical Usage Pattern

The info package is typically initialized with both device library and NVML library instances, allowing it to gather comprehensive system information from both sources.

### Complete Initialization Example

```mermaid
graph TB
    subgraph "Application Setup"
        APP_START["Application Start"]
    end
    
    subgraph "NVML Initialization"
        NVML_INIT["nvml.Init()"]
        NVML_LIB["nvml.Interface"]
    end
    
    subgraph "Device Library Initialization"
        DEV_NEW["device.New(nvmllib)"]
        DEV_LIB["device.Interface"]
    end
    
    subgraph "Info Package Initialization"
        INFO_NEW["info.New(<br/>  WithNvmlLib(nvmllib),<br/>  WithDeviceLib(devicelib),<br/>  WithLogger(logger)<br/>)"]
        INFO_IF["info.Interface"]
    end
    
    subgraph "Usage"
        GATHER["Gather system info"]
        QUERY["Query specific properties"]
        VALIDATE["Validate GPU environment"]
    end
    
    APP_START --> NVML_INIT
    NVML_INIT --> NVML_LIB
    NVML_LIB --> DEV_NEW
    DEV_NEW --> DEV_LIB
    
    NVML_LIB --> INFO_NEW
    DEV_LIB --> INFO_NEW
    INFO_NEW --> INFO_IF
    
    INFO_IF --> GATHER
    INFO_IF --> QUERY
    INFO_IF --> VALIDATE
```

**Sources:** [pkg/nvlib/info/options.go:1-71](), [pkg/nvlib/device/api.go:49-68]()

---

## Testing Support

The info package's design supports comprehensive testing through dependency injection. All major dependencies can be replaced with mock implementations.

### Testing Configuration

```mermaid
graph TB
    subgraph "Test Setup"
        TEST["Test Function"]
    end
    
    subgraph "Mock Dependencies"
        MOCK_NVML["Mock NVML<br/>Controlled responses"]
        MOCK_DEVICE["Mock Device Lib<br/>Synthetic devices"]
        MOCK_EXTRACTOR["Mock PropertyExtractor<br/>Test filesystem"]
        MOCK_LOGGER["Mock Logger<br/>Capture output"]
    end
    
    subgraph "Test Info Package"
        INFO_TEST["info.New(<br/>  WithNvmlLib(mockNvml),<br/>  WithDeviceLib(mockDevice),<br/>  WithPropertyExtractor(mockExt),<br/>  WithLogger(mockLogger),<br/>  WithRoot('/tmp/test-sysfs')<br/>)"]
    end
    
    subgraph "Test Scenarios"
        NO_GPU["No GPU present"]
        MULTI_GPU["Multiple GPUs"]
        MIG_ENABLED["MIG enabled"]
        ERROR_COND["Error conditions"]
    end
    
    TEST --> MOCK_NVML
    TEST --> MOCK_DEVICE
    TEST --> MOCK_EXTRACTOR
    TEST --> MOCK_LOGGER
    
    MOCK_NVML --> INFO_TEST
    MOCK_DEVICE --> INFO_TEST
    MOCK_EXTRACTOR --> INFO_TEST
    MOCK_LOGGER --> INFO_TEST
    
    INFO_TEST --> NO_GPU
    INFO_TEST --> MULTI_GPU
    INFO_TEST --> MIG_ENABLED
    INFO_TEST --> ERROR_COND
```

**Sources:** [pkg/nvlib/info/options.go:56-70]()

For more details on mock implementations, see [Mock Implementations](#8.2).

---

## Relationship to Other Packages

The info package serves as a high-level orchestrator that brings together multiple lower-level components.

### Package Dependency Graph

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application Code"]
    end
    
    subgraph "High-Level Abstractions"
        INFO["pkg/nvlib/info<br/>System information aggregation"]
    end
    
    subgraph "Mid-Level Abstractions"
        DEVICE["pkg/nvlib/device<br/>Device management"]
    end
    
    subgraph "Low-Level Components"
        NVML["pkg/nvml<br/>NVML bindings"]
        NVPCI["pkg/nvpci<br/>PCI discovery"]
    end
    
    subgraph "External Systems"
        NVML_C["libnvidia-ml.so<br/>NVML C library"]
        SYSFS["/sys filesystem"]
    end
    
    APP --> INFO
    
    INFO --> DEVICE
    INFO --> NVML
    
    DEVICE --> NVML
    DEVICE --> NVPCI
    
    NVPCI --> SYSFS
    NVML --> NVML_C
```

**Sources:** [pkg/nvlib/info/options.go:19-23](), [pkg/nvlib/device/api.go:19-21]()

---

## Summary

The `pkg/nvlib/info` package provides:

1. **Unified System Information**: Aggregates data from NVML, device library, and platform-specific sources
2. **Flexible Configuration**: Functional options pattern for customizing behavior
3. **Platform Awareness**: Supports different deployment scenarios through platform detection
4. **Testability**: All dependencies injectable via options, enabling comprehensive testing
5. **Logging Support**: Integrated logging for debugging and monitoring
6. **Property Extraction**: Pluggable property extraction system for environment-specific needs

The package sits at the highest abstraction layer in go-nvlib, making it ideal for applications that need comprehensive GPU system information without managing the complexity of multiple APIs directly.

---

