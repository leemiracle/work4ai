<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-docker · page 5 Multi-Architecture Support · fetched 2026-10-26 -->

# Multi-Architecture Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docker_build.yml](.github/workflows/docker_build.yml)
- [Dockerfile](Dockerfile)
- [build-all.sh](build-all.sh)
- [entrypoint_root.sh](entrypoint_root.sh)

</details>



## Purpose and Scope

This document provides an overview of how termux-docker supports multiple CPU architectures (aarch64, arm, i686, x86_64) through a dual-classification system and matrix-based build strategy. It covers the architecture selection logic, bootstrap archive selection, and image tagging conventions used throughout the build process.

For details on the internal organization of architecture-specific binaries within the container image, see [Architecture-Specific Binaries](#5.1). For information about cross-platform execution using QEMU emulation, see [Cross-Platform Execution](#5.2).

---

## Supported Architectures

The project supports four CPU architectures, each requiring a specific Termux bootstrap archive and Docker platform tag:

| Architecture | Description | Bits | System Type | Docker Platform |
|-------------|-------------|------|-------------|-----------------|
| `aarch64` | ARM 64-bit | 64 | `arm` | `linux/arm64` |
| `arm` | ARM 32-bit (ARMv7) | 32 | `arm` | `linux/arm/v7` |
| `i686` | Intel/AMD 32-bit | 32 | `x86` | `linux/386` |
| `x86_64` | Intel/AMD 64-bit | 64 | `x86` | `linux/amd64` |

The `i686` architecture receives the special `latest` tag, making it the default image when users do not specify an architecture.

**Sources:** [.github/workflows/docker_build.yml:21-25](), [.github/workflows/docker_build.yml:37-42](), [.github/workflows/docker_build.yml:61-64]()

---

## Architecture Classification System

### Dual-Layer Architecture Model

The system uses two distinct architecture identifiers that serve different purposes:

```mermaid
graph LR
    subgraph "Bootstrap Archive Layer"
        ARCH_AARCH64["BOOTSTRAP_ARCH<br/>aarch64"]
        ARCH_ARM["BOOTSTRAP_ARCH<br/>arm"]
        ARCH_I686["BOOTSTRAP_ARCH<br/>i686"]
        ARCH_X86_64["BOOTSTRAP_ARCH<br/>x86_64"]
    end
    
    subgraph "System Binary Layer"
        SYS_ARM["SYSTEM_TYPE<br/>arm"]
        SYS_X86["SYSTEM_TYPE<br/>x86"]
    end
    
    ARCH_AARCH64 --> SYS_ARM
    ARCH_ARM --> SYS_ARM
    ARCH_I686 --> SYS_X86
    ARCH_X86_64 --> SYS_X86
    
    SYS_ARM --> ARM_DIR["/system/arm/<br/>bin/, lib/, etc/"]
    SYS_X86 --> X86_DIR["/system/x86/<br/>bin/, lib/, etc/"]
```

**BOOTSTRAP_ARCH** determines which Termux package bootstrap archive is downloaded from GitHub releases. This must match exactly with the target CPU architecture because these archives contain compiled binaries specific to that instruction set.

**SYSTEM_TYPE** determines which `/system/` directory tree is copied into the image. Only two variants exist because the system-level utilities (shell, dnsmasq, libraries) can be shared between 32-bit and 64-bit variants of the same instruction set family.

**Sources:** [Dockerfile:5-7](), [Dockerfile:14](), [.github/workflows/docker_build.yml:37-42]()

---

## Build-Time Architecture Selection

### CI/CD Matrix Build Strategy

The GitHub Actions workflow uses a matrix strategy to build all four architectures in parallel:

```mermaid
graph TB
    WORKFLOW["docker_build.yml<br/>Workflow Trigger"]
    
    subgraph "Build Matrix"
        direction TB
        MATRIX["strategy.matrix.CPU_ARCH"]
        
        JOB_AARCH64["Build Job<br/>CPU_ARCH=aarch64"]
        JOB_ARM["Build Job<br/>CPU_ARCH=arm"]
        JOB_I686["Build Job<br/>CPU_ARCH=i686"]
        JOB_X86_64["Build Job<br/>CPU_ARCH=x86_64"]
    end
    
    subgraph "Architecture Mapping"
        MAP["Case Statement<br/>lines 37-42"]
    end
    
    subgraph "Build Arguments"
        ARG_BOOTSTRAP["--build-arg<br/>BOOTSTRAP_ARCH"]
        ARG_SYSTEM["--build-arg<br/>SYSTEM_TYPE"]
        ARG_PLATFORM["--platform<br/>PLATFORM_TAG"]
    end
    
    subgraph "Docker Build"
        BUILDX["docker buildx build"]
    end
    
    WORKFLOW --> MATRIX
    MATRIX --> JOB_AARCH64
    MATRIX --> JOB_ARM
    MATRIX --> JOB_I686
    MATRIX --> JOB_X86_64
    
    JOB_AARCH64 --> MAP
    JOB_ARM --> MAP
    JOB_I686 --> MAP
    JOB_X86_64 --> MAP
    
    MAP --> ARG_BOOTSTRAP
    MAP --> ARG_SYSTEM
    MAP --> ARG_PLATFORM
    
    ARG_BOOTSTRAP --> BUILDX
    ARG_SYSTEM --> BUILDX
    ARG_PLATFORM --> BUILDX
```

Each matrix job executes independently with its CPU_ARCH value, then determines the corresponding SYSTEM_TYPE and PLATFORM_TAG through a case statement at [.github/workflows/docker_build.yml:37-42]().

**Sources:** [.github/workflows/docker_build.yml:19-25](), [.github/workflows/docker_build.yml:35-48]()

---

## Architecture Detection in Build Script

The `build-all.sh` script provides local build capability with automatic architecture detection:

```mermaid
graph TD
    START["build-all.sh<br/>Script Start"]
    
    UNAME["uname -m<br/>Host Architecture"]
    
    subgraph "Architecture Detection Logic"
        CASE["Case Statement<br/>lines 17-26"]
        
        DETECT_AARCH64["aarch64<br/>SYSTEM_TYPE=arm<br/>ARCHITECTURES=(aarch64 arm)"]
        DETECT_ARM["armv7l/armv8l<br/>SYSTEM_TYPE=arm<br/>ARCHITECTURES=(arm)"]
        DETECT_I686["i686<br/>SYSTEM_TYPE=x86<br/>ARCHITECTURES=(i686)"]
        DETECT_X86_64["x86_64<br/>SYSTEM_TYPE=x86<br/>ARCHITECTURES=(i686 x86_64)"]
    end
    
    subgraph "Build Loop"
        LOOP["for arch in ARCHITECTURES"]
        BUILD["docker/podman build<br/>--build-arg BOOTSTRAP_ARCH<br/>--build-arg SYSTEM_TYPE"]
    end
    
    START --> UNAME
    UNAME --> CASE
    CASE --> DETECT_AARCH64
    CASE --> DETECT_ARM
    CASE --> DETECT_I686
    CASE --> DETECT_X86_64
    
    DETECT_AARCH64 --> LOOP
    DETECT_ARM --> LOOP
    DETECT_I686 --> LOOP
    DETECT_X86_64 --> LOOP
    
    LOOP --> BUILD
```

The script automatically builds compatible architectures for the host system:
- **x86_64 hosts** can build both i686 and x86_64 images natively
- **aarch64 hosts** can build both arm and aarch64 images natively  
- **i686 hosts** can only build i686 images
- **ARM 32-bit hosts** can only build arm images

**Sources:** [build-all.sh:17-26](), [build-all.sh:28-35]()

---

## Architecture-to-Platform Mapping Table

The complete mapping between architecture identifiers used throughout the system:

| CPU_ARCH | BOOTSTRAP_ARCH | SYSTEM_TYPE | PLATFORM_TAG | Bootstrap URL Pattern |
|----------|----------------|-------------|--------------|----------------------|
| aarch64 | aarch64 | arm | linux/arm64 | `bootstrap-aarch64.zip` |
| arm | arm | arm | linux/arm/v7 | `bootstrap-arm.zip` |
| i686 | i686 | x86 | linux/386 | `bootstrap-i686.zip` |
| x86_64 | x86_64 | x86 | linux/amd64 | `bootstrap-x86_64.zip` |

The `PLATFORM_TAG` is passed to Docker's `--platform` flag to ensure the image metadata correctly identifies its target architecture. This enables Docker to pull the correct image variant on multi-architecture systems.

**Sources:** [.github/workflows/docker_build.yml:37-48](), [Dockerfile:5-7]()

---

## Bootstrap Archive Selection

### Download Process

The Dockerfile uses the BOOTSTRAP_ARCH build argument to construct the download URL:

```dockerfile
ARG BOOTSTRAP_ARCH=i686
ADD https://github.com/termux/termux-packages/releases/download/bootstrap-$BOOTSTRAP_VERSION/bootstrap-$BOOTSTRAP_ARCH.zip /bootstrap.zip
```

This downloads architecture-specific compiled packages from the termux-packages repository. Each bootstrap archive contains:
- Package manager binaries (apt, dpkg) compiled for the target architecture
- Core system utilities compiled for the target architecture
- Architecture-specific shared libraries
- Package database and configuration files

**Sources:** [Dockerfile:5-6](), [Dockerfile:21]()

---

## Image Tagging Strategy

### Tag Assignment Logic

```mermaid
graph TB
    subgraph "Build Process Output"
        BUILD_AARCH64["Image<br/>termux/termux-docker:aarch64"]
        BUILD_ARM["Image<br/>termux/termux-docker:arm"]
        BUILD_I686["Image<br/>termux/termux-docker:i686"]
        BUILD_X86_64["Image<br/>termux/termux-docker:x86_64"]
    end
    
    subgraph "Tag Assignment"
        CHECK{"CPU_ARCH == i686?"}
        TAG_LATEST["docker tag<br/>i686 → latest"]
    end
    
    subgraph "Docker Hub"
        HUB_AARCH64["termux/termux-docker:aarch64"]
        HUB_ARM["termux/termux-docker:arm"]
        HUB_I686["termux/termux-docker:i686"]
        HUB_X86_64["termux/termux-docker:x86_64"]
        HUB_LATEST["termux/termux-docker:latest"]
    end
    
    BUILD_I686 --> CHECK
    CHECK -->|Yes| TAG_LATEST
    CHECK -->|No| HUB_AARCH64
    CHECK -->|No| HUB_ARM
    CHECK -->|No| HUB_X86_64
    
    TAG_LATEST --> HUB_LATEST
    TAG_LATEST --> HUB_I686
    
    BUILD_AARCH64 --> HUB_AARCH64
    BUILD_ARM --> HUB_ARM
    BUILD_X86_64 --> HUB_X86_64
```

The `i686` architecture receives the `latest` tag because:
1. It provides the widest compatibility across systems
2. x86_64 hosts can run i686 containers natively with minimal overhead
3. It serves as a sensible default for users not specifying an architecture

**Sources:** [.github/workflows/docker_build.yml:61-64](), [build-all.sh:41-46]()

---

## Build Argument Flow Through System

The following diagram traces how architecture parameters flow from build invocation through to the final image:

```mermaid
graph TB
    subgraph "Build Invocation"
        CLI["docker buildx build<br/>--build-arg BOOTSTRAP_ARCH=aarch64<br/>--build-arg SYSTEM_TYPE=arm"]
    end
    
    subgraph "Dockerfile Processing"
        ARG_DECL["ARG BOOTSTRAP_ARCH=i686<br/>ARG SYSTEM_TYPE=x86<br/>lines 5-7"]
        
        COPY_SYS["COPY /system/$SYSTEM_TYPE /system<br/>line 14"]
        
        DOWNLOAD["ADD https://.../bootstrap-$BOOTSTRAP_ARCH.zip<br/>line 21"]
    end
    
    subgraph "Image Filesystem"
        FS_SYS["/system/<br/>Contains arm/ or x86/"]
        
        FS_DATA["/data/data/com.termux/<br/>Contains arch-specific packages"]
    end
    
    subgraph "Runtime"
        EXEC["Binary Execution<br/>Native or QEMU"]
    end
    
    CLI --> ARG_DECL
    ARG_DECL --> COPY_SYS
    ARG_DECL --> DOWNLOAD
    
    COPY_SYS --> FS_SYS
    DOWNLOAD --> FS_DATA
    
    FS_SYS --> EXEC
    FS_DATA --> EXEC
```

**Sources:** [Dockerfile:5-7](), [Dockerfile:14](), [Dockerfile:21]()

---

## Architecture Compatibility Matrix

This table shows which architectures can run on which hosts natively versus requiring emulation:

| Host Architecture | aarch64 Image | arm Image | i686 Image | x86_64 Image |
|-------------------|---------------|-----------|------------|--------------|
| **x86_64** | QEMU | QEMU | Native | Native |
| **i686** | QEMU | QEMU | Native | ❌ |
| **aarch64** | Native | Native | QEMU | QEMU |
| **armv7l** | ❌ | Native | QEMU | QEMU |

- **Native**: Binary execution using host CPU directly
- **QEMU**: Requires QEMU user-mode emulation via binfmt_misc
- **❌**: Not supported (32-bit host cannot run 64-bit binaries)

For details on QEMU setup and emulation mechanics, see [Cross-Platform Execution](#5.2).

**Sources:** [.github/workflows/docker_build.yml:31-33]()

---

