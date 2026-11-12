<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/edk2-nvidia · page 2 Build System and Configuration · fetched 2026-10-26 -->

# Build System and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/release-drafter.yml](.github/release-drafter.yml)
- [.github/workflows/build.yml](.github/workflows/build.yml)
- [Platform/NVIDIA/Kconfig](Platform/NVIDIA/Kconfig)
- [Platform/NVIDIA/L4TLauncher/PlatformBuild.py](Platform/NVIDIA/L4TLauncher/PlatformBuild.py)
- [Platform/NVIDIA/L4TLauncher/build.sh](Platform/NVIDIA/L4TLauncher/build.sh)
- [Platform/NVIDIA/NVIDIA.common.dsc.inc](Platform/NVIDIA/NVIDIA.common.dsc.inc)
- [Platform/NVIDIA/NVIDIA.defconfig](Platform/NVIDIA/NVIDIA.defconfig)
- [Platform/NVIDIA/NVIDIA.fvmain.fdf.inc](Platform/NVIDIA/NVIDIA.fvmain.fdf.inc)
- [Silicon/NVIDIA/edk2nv/stuart/builder.py](Silicon/NVIDIA/edk2nv/stuart/builder.py)
- [Silicon/NVIDIA/edk2nv/stuart/settings.py](Silicon/NVIDIA/edk2nv/stuart/settings.py)

</details>



This document covers the build system architecture used to construct NVIDIA UEFI firmware images, including the Stuart build framework, platform configuration files, and Kconfig-based configuration management. The build system orchestrates compilation, linking, and firmware image generation across multiple platforms and build variants.

For information about platform-specific boot management, see [Platform Definitions and Boot Management](#3.1). For details about hardware-specific drivers built by this system, see [Hardware Drivers](#4).

## Build System Architecture

The NVIDIA UEFI build system consists of three main components that work together to produce firmware images:

```mermaid
graph TB
    subgraph "Configuration Layer"
        KC[Kconfig System]
        PlatDSC[Platform DSC Files]
        DefConfig[defconfig Files]
    end
    
    subgraph "Build Orchestration Layer"  
        Stuart[Stuart Framework]
        Settings[NVIDIASettingsManager]
        Builder[NVIDIAPlatformBuilder]
    end
    
    subgraph "EDK2 Build Layer"
        BaseTools[EDK2 BaseTools]
        Build[build.py]
        GenFds[GenFds]
    end
    
    subgraph "Output"
        FV[Firmware Volume]
        IMG[UEFI Binary Image]
    end

    KC --> PlatDSC
    DefConfig --> KC
    PlatDSC --> Stuart
    Settings --> Stuart
    Builder --> Stuart
    Stuart --> BaseTools
    BaseTools --> Build
    Build --> GenFds
    GenFds --> FV
    FV --> IMG
```

Sources: [Platform/NVIDIA/NVIDIA.common.dsc.inc:1-50](), [Silicon/NVIDIA/edk2nv/stuart/settings.py:35-85](), [Silicon/NVIDIA/edk2nv/stuart/builder.py:34-51]()

## Stuart Build Framework

The Stuart framework provides the foundation for NVIDIA's build system, handling workspace management, dependency resolution, and build orchestration through two key classes:

### Core Stuart Components

```mermaid
graph LR
    subgraph "Settings Management"
        NSM[NVIDIASettingsManager]
        ANSM[AbstractNVIDIASettingsManager]
        NCiSM[NVIDIACiSettingsManager]
    end
    
    subgraph "Build Execution"
        NPB[NVIDIAPlatformBuilder]
        UB[UefiBuilder]
    end
    
    subgraph "Configuration"
        WS[GetWorkspaceRoot]
        PP[GetPackagesPath] 
        CF[GetConfigFiles]
        KC[BuildConfigFile]
    end

    ANSM --> NSM
    ANSM --> NCiSM
    NSM --> NPB
    UB --> NPB
    NSM --> WS
    NSM --> PP
    NSM --> CF
    NPB --> KC
```

The `NVIDIASettingsManager` class extends Stuart's base settings interfaces to provide platform-specific configuration:

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `GetWorkspaceRoot()` | Workspace location | Uses `WORKSPACE` environment variable |
| `GetPackagesPath()` | Package search paths | Includes edk2, edk2-platforms, edk2-nvidia |  
| `GetConfigFiles()` | Kconfig files list | Platform-specific defconfig files |
| `GetDscName()` | Main DSC file | Returns `NVIDIA.common.dsc` path |

Sources: [Silicon/NVIDIA/edk2nv/stuart/settings.py:57-131](), [Silicon/NVIDIA/edk2nv/stuart/builder.py:34-51]()

### Build Process Flow

The `NVIDIAPlatformBuilder` orchestrates the complete build process:

```mermaid
sequenceDiagram
    participant CLI as Command Line
    participant NPB as NVIDIAPlatformBuilder  
    participant KC as Kconfig System
    participant Stuart as Stuart Framework
    participant EDK2 as EDK2 BaseTools

    CLI->>NPB: stuart_build --target DEBUG
    NPB->>NPB: SetPlatformEnv()
    NPB->>KC: BuildConfigFile()
    KC->>KC: Parse Kconfig + defconfig
    KC->>NPB: Generate .config
    NPB->>Stuart: Setup build environment
    Stuart->>EDK2: Invoke build.py
    EDK2->>NPB: Build complete
    NPB->>NPB: PlatformPostBuild()
    NPB->>NPB: Generate firmware image
```

Sources: [Silicon/NVIDIA/edk2nv/stuart/builder.py:290-331](), [Silicon/NVIDIA/edk2nv/stuart/builder.py:435-499]()

## Platform Configuration Files

Platform configuration is managed through a hierarchy of DSC (Description) and FDF (Flash Description File) includes that define build settings, library mappings, and firmware layout.

### DSC Configuration Hierarchy

```mermaid
graph TB
    subgraph "Platform DSC Structure"
        Common[NVIDIA.common.dsc.inc]
        Global[NVIDIA.global.dsc.inc]
        Config[config.dsc.inc]
        
        Common --> Global
        Common --> Config
    end
    
    subgraph "Configuration Sections"
        Defines[Defines Section]
        LibClasses[LibraryClasses]
        BuildOpts[BuildOptions]  
        PCDs[PCDs]
        
        Common --> Defines
        Common --> LibClasses
        Common --> BuildOpts
        Common --> PCDs
    end
    
    subgraph "Generated Files"
        KConfig[Kconfig Processing]
        ConfigDsc[config.dsc.inc]
        
        KConfig --> ConfigDsc
        ConfigDsc --> Config
    end
```

The main platform configuration is defined in `NVIDIA.common.dsc.inc`, which includes:

| Section | Purpose | Key Settings |
|---------|---------|--------------|
| `[Defines]` | Platform metadata | `PLATFORM_NAME`, `BUILD_TARGETS`, `OUTPUT_DIRECTORY` |
| `[LibraryClasses]` | Library mappings | Debug, crypto, platform-specific libraries |
| `[BuildOptions]` | Compiler flags | GCC flags, ASL options, security options |
| `[PcdsFeatureFlag]` | Feature toggles | Secure boot, TPM, network features |

Sources: [Platform/NVIDIA/NVIDIA.common.dsc.inc:9-50](), [Platform/NVIDIA/NVIDIA.common.dsc.inc:98-250]()

### Firmware Volume Definition

The `NVIDIA.fvmain.fdf.inc` file defines how firmware components are packaged:

```mermaid
graph LR
    subgraph "FV.FvMain Structure"
        APRIORI[APRIORI DXE Drivers]
        Core[DXE Core Drivers] 
        Platform[Platform Drivers]
        Apps[Applications]
        
        APRIORI --> Core
        Core --> Platform  
        Platform --> Apps
    end
    
    subgraph "Driver Categories"
        Arch[Architectural Protocols]
        HW[Hardware Drivers]
        Boot[Boot Services]
        Runtime[Runtime Services]
        
        Core --> Arch
        Platform --> HW
        Platform --> Boot
        Platform --> Runtime
    end
```

The APRIORI section ensures critical drivers load first:

- PCD services (`MdeModulePkg/Universal/PCD/Dxe/Pcd.inf`)
- Status code routing (`ReportStatusCodeRouterRuntimeDxe`)
- Platform initialization (`TegraPlatformInitDxe`)
- Interrupt controller (`ArmGicDxe`)

Sources: [Platform/NVIDIA/NVIDIA.fvmain.fdf.inc:39-73](), [Platform/NVIDIA/NVIDIA.fvmain.fdf.inc:75-120]()

## Kconfig System

The Kconfig system provides build-time configuration through a hierarchical menu system that generates configuration files consumed by the EDK2 build.

### Kconfig Structure

```mermaid
graph TB
    subgraph "Kconfig Hierarchy"
        MainKC[Platform/NVIDIA/Kconfig]
        SocKC[KconfigIncludes/Soc*.conf]
        BuildKC[KconfigIncludes/Build*.conf]
        CommonKC[KconfigIncludes/Common*.conf]
        
        MainKC --> SocKC
        MainKC --> BuildKC
        MainKC --> CommonKC
    end
    
    subgraph "Configuration Categories"
        Security[Security Options]
        Hardware[Hardware Support]
        Boot[Boot Options]
        Debug[Debug Options]
        FW[Firmware Management]
        
        MainKC --> Security
        MainKC --> Hardware
        MainKC --> Boot
        MainKC --> Debug
        MainKC --> FW
    end
    
    subgraph "Generated Output"
        DotConfig[.config]
        Defconfig[defconfig]
        ConfigDscInc[config.dsc.inc]
        
        MainKC --> DotConfig
        DotConfig --> ConfigDscInc
        DotConfig --> Defconfig
    end
```

Key configuration categories include:

| Category | Configuration Options | Impact |
|----------|----------------------|--------|
| Security | TPM type, Secure Boot, MM type | Security drivers, authentication |
| Hardware | PCIe, USB, networking, display | Hardware driver inclusion |
| Boot Options | Android, L4T, RCM boot | Boot flow and applications |
| Debug | Print levels, memory tests | Debug capabilities |

Sources: [Platform/NVIDIA/Kconfig:93-270](), [Platform/NVIDIA/Kconfig:824-986]()

### Configuration Processing

The `BuildConfigFile()` method in `NVIDIAPlatformBuilder` processes Kconfig:

```mermaid
sequenceDiagram
    participant NPB as NVIDIAPlatformBuilder
    participant KC as kconfiglib.Kconfig
    participant Files as Config Files
    participant Output as Generated Files

    NPB->>KC: Load Platform/NVIDIA/Kconfig
    NPB->>Files: Read NVIDIA.defconfig
    NPB->>Files: Read platform defconfig files
    NPB->>Files: Read existing .config (if present)
    KC->>KC: Merge configurations
    KC->>KC: Validate dependencies
    KC->>Output: Write .config
    KC->>Output: Write minimal defconfig  
    KC->>Output: Write config.dsc.inc
    NPB->>NPB: Store kconf_syms for build
```

The generated `config.dsc.inc` translates Kconfig symbols to EDK2 DEFINE statements:
- `CONFIG_VARIABLE=value` becomes `DEFINE VARIABLE value`
- Empty values are commented out as EDK2 cannot define empty values
- String values have quotes stripped for EDK2 compatibility

Sources: [Silicon/NVIDIA/edk2nv/stuart/builder.py:193-288]()

## Build Environment Setup

The build system establishes the compilation environment through environment variables and build settings managed by the Stuart framework.

### Environment Configuration

```mermaid
graph LR
    subgraph "Environment Sources"
        CLI[Command Line Args]
        Settings[SettingsManager]
        Kconfig[Kconfig Values]
        Defaults[Build Defaults]
    end
    
    subgraph "Environment Variables"
        BuildVars[Build Environment]
        ShellVars[Shell Environment]
        EDK2Vars[EDK2 Variables]
    end
    
    subgraph "Build Tools"
        Toolchain[Cross Compiler]
        BaseTools[EDK2 BaseTools]
        Stuart[Stuart Framework]
    end

    CLI --> BuildVars
    Settings --> BuildVars
    Kconfig --> BuildVars
    Defaults --> BuildVars
    
    BuildVars --> ShellVars
    BuildVars --> EDK2Vars
    
    ShellVars --> Toolchain
    EDK2Vars --> BaseTools
    BaseTools --> Stuart
```

Key environment variables set by `SetPlatformEnv()`:

| Variable | Source | Purpose |
|----------|---------|---------|
| `ACTIVE_PLATFORM` | `GetDscName()` | Main platform DSC file |
| `TARGET` | `--target` argument | Build target (DEBUG/RELEASE) |
| `TARGET_ARCH` | Fixed | Always AARCH64 for NVIDIA |
| `TOOL_CHAIN_TAG` | `GetToolchainTag()` | Toolchain identifier (GCC) |
| `BLD_*_BUILD_NAME` | `GetName()` | Platform name |
| `BLD_*_BUILD_GUID` | Kconfig/`GetGuid()` | Platform GUID |

Sources: [Silicon/NVIDIA/edk2nv/stuart/builder.py:349-430](), [Silicon/NVIDIA/edk2nv/stuart/settings.py:239-251]()

---

