<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-docker · page 1 Home · fetched 2026-10-26 -->

# Home

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [entrypoint_root.sh](entrypoint_root.sh)

</details>



## Purpose and Scope

This documentation covers **termux-docker**, a project that packages the [Termux](https://termux.com) Android terminal environment as Docker container images. This page provides an architectural overview of the system, explaining how the build process, multi-architecture support, and runtime initialization work together.

For quick start instructions on running containers, see [Getting Started](#2). For build system details, see [Building Images](#3). For runtime behavior specifics, see [Container Runtime](#4).

## What is Termux Docker?

Termux Docker is a containerized version of Termux, the Android terminal emulator and Linux environment. The project creates Docker images that replicate Termux's filesystem structure, package management system, and user environment without Android runtime components (DalvikVM, OpenSLES).

**Key Characteristics:**
- Multi-architecture support: `aarch64`, `arm`, `i686`, `x86_64`
- Android-style filesystem layout under `/data/data/com.termux/`
- Complete Termux package ecosystem via `apt`/`dpkg`
- Privilege-aware initialization supporting both root and non-root startup modes
- Published to Docker Hub as `termux/termux-docker` with architecture-specific tags

Sources: [README.md:1-6](), [README.md:26-32]()

## System Architecture Overview

The system consists of three major phases: **build-time preparation**, **image construction**, and **runtime initialization**.

```mermaid
graph TB
    subgraph "Build Phase"
        GHACTIONS["GitHub Actions<br/>.github/workflows/docker_build.yml"]
        BUILDSCRIPT["build-all.sh"]
        DOCKERFILE["Dockerfile"]
        BOOTSTRAP["Termux Bootstrap Archive<br/>bootstrap-{arch}.zip"]
    end
    
    subgraph "Image Structure"
        SYSBIN["/system/{x86,arm}/<br/>Shell, dnsmasq, libraries"]
        TERMUXDATA["/data/data/com.termux/<br/>Termux environment"]
        ENTRYPOINTS["/entrypoint.sh<br/>/entrypoint_root.sh"]
    end
    
    subgraph "Runtime Phase"
        INIT["Container Start"]
        DNSMASQ["dnsmasq Service<br/>DNS resolution"]
        USERPROC["User Processes<br/>login shell or command"]
    end
    
    GHACTIONS -->|"triggers"| BUILDSCRIPT
    BUILDSCRIPT -->|"executes"| DOCKERFILE
    DOCKERFILE -->|"downloads"| BOOTSTRAP
    DOCKERFILE -->|"creates"| SYSBIN
    DOCKERFILE -->|"extracts to"| TERMUXDATA
    DOCKERFILE -->|"installs"| ENTRYPOINTS
    
    SYSBIN -.->|"used by"| INIT
    ENTRYPOINTS -.->|"executed at"| INIT
    INIT -->|"starts"| DNSMASQ
    INIT -->|"spawns"| USERPROC
    TERMUXDATA -.->|"environment for"| USERPROC
```

**Architecture Phases:**

| Phase | Components | Purpose |
|-------|-----------|---------|
| **Build** | GitHub Actions, `build-all.sh`, `Dockerfile` | Automate multi-arch image creation |
| **Image** | `/system/`, `/data/`, entrypoints | Provide filesystem structure and binaries |
| **Runtime** | Entrypoint scripts, `dnsmasq`, user shell | Initialize services and user environment |

Sources: [Dockerfile:1-92](), [README.md:97-109]()

## Core Components

### Build System Components

```mermaid
graph LR
    subgraph "CI/CD"
        WORKFLOW[".github/workflows/<br/>docker_build.yml"]
    end
    
    subgraph "Build Scripts"
        BUILDALL["build-all.sh"]
    end
    
    subgraph "Image Definition"
        DF["Dockerfile"]
        BOOTSTRAP["bootstrap stage<br/>lines 3-70"]
        FINAL["final stage<br/>lines 74-92"]
    end
    
    subgraph "System Binaries"
        SYSTEMX86["system/x86/<br/>bin/, lib/, etc/"]
        SYSTEMARM["system/arm/<br/>bin/, lib/, etc/"]
    end
    
    WORKFLOW -->|"executes matrix builds"| BUILDALL
    BUILDALL -->|"docker build"| DF
    DF -->|"stage 1"| BOOTSTRAP
    DF -->|"stage 2"| FINAL
    BOOTSTRAP -->|"COPY from"| SYSTEMX86
    BOOTSTRAP -->|"COPY from"| SYSTEMARM
    BOOTSTRAP -->|"ADD from GitHub"| TERMUXBS["Termux Bootstrap<br/>releases"]
```

The build system has three layers:

1. **CI/CD Layer**: `.github/workflows/docker_build.yml` orchestrates automated builds with matrix strategy for all architectures (see [CI/CD Pipeline](#3.3))
2. **Script Layer**: `build-all.sh` handles local builds with Docker/Podman detection (see [Build Scripts](#3.2))
3. **Dockerfile Layer**: Multi-stage Dockerfile downloads bootstrap archives and assembles the final image (see [The Dockerfile](#3.1))

Sources: [Dockerfile:1-92](), [README.md:97-109]()

### Runtime Components

```mermaid
graph TB
    subgraph "Entrypoint Scripts"
        EP["entrypoint.sh"]
        EPROOT["entrypoint_root.sh"]
    end
    
    subgraph "System Services"
        MKSH["/system/bin/mksh<br/>MirBSD Korn Shell"]
        DNS["/system/bin/dnsmasq<br/>DNS/DHCP server"]
        BUSYBOX["/system/bin/busybox<br/>Unix utilities"]
    end
    
    subgraph "Termux Environment"
        LOGIN["/data/.../usr/bin/login<br/>Login shell"]
        APT["/data/.../usr/bin/apt<br/>Package manager"]
        USERBIN["/data/.../usr/bin/*<br/>User packages"]
    end
    
    EP -->|"starts as root"| DNS
    EP -->|"su to system user"| LOGIN
    EPROOT -->|"stays as root"| DNS
    EPROOT -->|"no privilege drop"| LOGIN
    
    DNS -.->|"forked by"| MKSH
    LOGIN -->|"spawns"| USERBIN
    APT -.->|"requires"| DNS
```

**Runtime Component Roles:**

| Component | File Path | Role |
|-----------|-----------|------|
| `entrypoint.sh` | `/entrypoint.sh` | Standard entrypoint: starts services, drops to UID 1000 |
| `entrypoint_root.sh` | `/entrypoint_root.sh` | Root entrypoint: starts services, maintains root privileges |
| `mksh` | `/system/bin/mksh` | Shell used for PTY-based dnsmasq startup |
| `dnsmasq` | `/system/bin/dnsmasq` | DNS resolver required for package management |
| `login` | `/data/data/com.termux/files/usr/bin/login` | Default command: interactive login shell |

Sources: [Dockerfile:16-18](), [Dockerfile:90-91](), [entrypoint_root.sh:1-21]()

## Build vs Runtime Architecture

The system uses a **multi-stage Dockerfile** with distinct build-time and runtime environments:

### Build-Time Environment

```mermaid
graph TB
    subgraph "Bootstrap Stage FROM scratch"
        SHELL["/system/bin/sh<br/>SHELL directive"]
        PATH["PATH=/system/bin"]
        COPY["COPY /system/$SYSTEM_TYPE"]
        ADD["ADD bootstrap archive"]
        RUN["RUN busybox commands"]
    end
    
    subgraph "Bootstrap Operations"
        EXTRACT["Extract bootstrap.zip<br/>to /data/.../usr"]
        SYMLINKS["Process SYMLINKS.txt<br/>create symlinks"]
        COMPAT["Create compatibility links<br/>/usr, /bin, /tmp"]
        PERMS["Set ownership<br/>root:0, system:1000"]
        UPDATE["apt update && upgrade"]
    end
    
    SHELL --> RUN
    PATH --> RUN
    COPY --> RUN
    ADD --> RUN
    
    RUN --> EXTRACT
    EXTRACT --> SYMLINKS
    SYMLINKS --> COMPAT
    COMPAT --> PERMS
    PERMS --> UPDATE
```

**Bootstrap Stage Operations** [Dockerfile:3-70]():

1. **Base Setup**: `FROM scratch` with `/system/bin/sh` as shell [Dockerfile:3-11]()
2. **System Files**: Copy architecture-specific binaries from `system/{x86,arm}/` [Dockerfile:14]()
3. **Bootstrap Extraction**: Download and unzip Termux bootstrap archive [Dockerfile:21-26]()
4. **Symlink Creation**: Process `SYMLINKS.txt` for Termux package symlinks [Dockerfile:28-33]()
5. **Compatibility Links**: Create `/usr`, `/bin`, `/tmp` pointing to Termux paths [Dockerfile:34-36]()
6. **Permission Setup**: Set ownership (root:0 for `/system`, 1000:1000 for `/data`) [Dockerfile:49-59]()
7. **Package Updates**: Run `apt update && upgrade` for non-ARM architectures [Dockerfile:63-70]()

Sources: [Dockerfile:3-70]()

### Runtime Environment

**Final Stage** [Dockerfile:74-92]():

```mermaid
graph LR
    subgraph "FROM scratch"
        ENV["Environment Variables<br/>ANDROID_DATA, HOME, PATH, etc"]
        COPY2["COPY --from=bootstrap / /"]
        ENTRY["ENTRYPOINT /entrypoint.sh"]
        CMD["CMD /data/.../usr/bin/login"]
    end
    
    subgraph "Environment Setup"
        ANDROIDDATA["ANDROID_DATA=/data"]
        ANDROIDROOT["ANDROID_ROOT=/system"]
        HOME2["HOME=/data/.../home"]
        PREFIX["PREFIX=/data/.../usr"]
        PATH2["PATH=/data/.../usr/bin"]
    end
    
    ENV --> ANDROIDDATA
    ENV --> ANDROIDROOT
    ENV --> HOME2
    ENV --> PREFIX
    ENV --> PATH2
    
    COPY2 -.-> ENTRY
    ENTRY --> CMD
```

**Key Environment Variables** [Dockerfile:76-83]():

| Variable | Value | Purpose |
|----------|-------|---------|
| `ANDROID_DATA` | `/data` | Android data directory root |
| `ANDROID_ROOT` | `/system` | Android system directory root |
| `HOME` | `/data/data/com.termux/files/home` | User home directory |
| `PATH` | `/data/data/com.termux/files/usr/bin` | Default executable search path |
| `PREFIX` | `/data/data/com.termux/files/usr` | Termux installation prefix |
| `TMPDIR` | `/data/data/com.termux/files/usr/tmp` | Temporary directory |

Sources: [Dockerfile:74-92]()

## Multi-Architecture Support

The project supports four CPU architectures through **architecture-specific builds** and **parallel system directories**:

```mermaid
graph TB
    subgraph "Build Arguments"
        BARCH["BOOTSTRAP_ARCH<br/>aarch64, arm, i686, x86_64"]
        STYPE["SYSTEM_TYPE<br/>x86, arm"]
    end
    
    subgraph "System Binaries"
        SYSX86["/system/x86/<br/>x86 & x86_64 binaries"]
        SYSARM["/system/arm/<br/>arm & aarch64 binaries"]
    end
    
    subgraph "Bootstrap Archives"
        BS_AARCH64["bootstrap-aarch64.zip"]
        BS_ARM["bootstrap-arm.zip"]
        BS_I686["bootstrap-i686.zip"]
        BS_X86_64["bootstrap-x86_64.zip"]
    end
    
    subgraph "Published Images"
        IMG_AARCH64["termux/termux-docker:aarch64"]
        IMG_ARM["termux/termux-docker:arm"]
        IMG_I686["termux/termux-docker:i686"]
        IMG_X86_64["termux/termux-docker:x86_64"]
        IMG_LATEST["termux/termux-docker:latest"]
    end
    
    BARCH -->|"aarch64"| BS_AARCH64
    BARCH -->|"arm"| BS_ARM
    BARCH -->|"i686"| BS_I686
    BARCH -->|"x86_64"| BS_X86_64
    
    STYPE -->|"arm"| SYSARM
    STYPE -->|"x86"| SYSX86
    
    BS_AARCH64 --> IMG_AARCH64
    BS_ARM --> IMG_ARM
    BS_I686 --> IMG_I686
    BS_X86_64 --> IMG_X86_64
    
    IMG_I686 -.->|"tagged as"| IMG_LATEST
```

**Architecture Mapping** [Dockerfile:5-7]():

| BOOTSTRAP_ARCH | SYSTEM_TYPE | Published Tag | Notes |
|----------------|-------------|---------------|-------|
| `aarch64` | `arm` | `aarch64` | 64-bit ARM |
| `arm` | `arm` | `arm` | 32-bit ARM |
| `i686` | `x86` | `i686`, `latest` | 32-bit x86 (default) |
| `x86_64` | `x86` | `x86_64` | 64-bit x86 |

The `SYSTEM_TYPE` argument determines which `/system/{x86,arm}` directory is copied, providing the appropriate system binaries for the target architecture. For cross-architecture execution (e.g., ARM on x86 hosts), QEMU emulation must be configured via `binfmt_misc` (see [Cross-Platform Execution](#5.2)).

Sources: [Dockerfile:5-7](), [Dockerfile:14](), [README.md:26-36](), [README.md:42-66]()

## Key Files and Their Roles

### Primary System Files

```mermaid
graph TB
    subgraph "Build Definition"
        DF["Dockerfile<br/>Multi-stage build definition"]
        BUILDSH["build-all.sh<br/>Local build automation"]
        GHWF[".github/workflows/docker_build.yml<br/>CI/CD automation"]
    end
    
    subgraph "Runtime Entry Points"
        EP["entrypoint.sh<br/>Standard: drops to UID 1000"]
        EPROOT["entrypoint_root.sh<br/>Alternate: maintains root"]
    end
    
    subgraph "System Binaries by Arch"
        X86_SH["system/x86/bin/sh"]
        X86_MKSH["system/x86/bin/mksh"]
        X86_DNS["system/x86/bin/dnsmasq"]
        X86_BB["system/x86/bin/busybox"]
        ARM_SH["system/arm/bin/sh"]
        ARM_MKSH["system/arm/bin/mksh"]
        ARM_DNS["system/arm/bin/dnsmasq"]
        ARM_BB["system/arm/bin/busybox"]
    end
    
    subgraph "Configuration Files"
        PASSWD["system/{x86,arm}/etc/passwd<br/>User database"]
        GROUP["system/{x86,arm}/etc/group<br/>Group database"]
        MKSHRC["system/{x86,arm}/etc/mkshrc<br/>Shell configuration"]
        LDCONF["system/{x86,arm}/etc/ld.config.28.txt<br/>Linker configuration"]
    end
    
    DF -.->|"installs"| EP
    DF -.->|"installs"| EPROOT
    DF -.->|"copies"| X86_SH
    DF -.->|"copies"| ARM_SH
    
    EP -.->|"uses"| X86_MKSH
    EP -.->|"uses"| X86_DNS
    EPROOT -.->|"uses"| ARM_MKSH
    EPROOT -.->|"uses"| ARM_DNS
```

**File Reference Table:**

| File Path | Purpose | Referenced In |
|-----------|---------|---------------|
| `Dockerfile` | Multi-stage image build definition | [The Dockerfile](#3.1) |
| `build-all.sh` | Local build script with Docker/Podman support | [Build Scripts](#3.2) |
| `.github/workflows/docker_build.yml` | CI/CD automation | [CI/CD Pipeline](#3.3) |
| `entrypoint.sh` | Standard entrypoint with privilege drop | [Entrypoint System](#4.1) |
| `entrypoint_root.sh` | Root-mode entrypoint | [Entrypoint System](#4.1) |
| `system/{x86,arm}/bin/sh` | POSIX shell | [Shell Environment](#6.1) |
| `system/{x86,arm}/bin/mksh` | MirBSD Korn Shell | [Shell Environment](#6.1) |
| `system/{x86,arm}/bin/dnsmasq` | DNS/DHCP server | [Network Services](#6.2) |
| `system/{x86,arm}/bin/busybox` | Unix utilities collection | [Architecture-Specific Binaries](#5.1) |
| `system/{x86,arm}/etc/passwd` | User/group definitions | [User and Group Configuration](#6.4) |
| `system/{x86,arm}/etc/mkshrc` | Shell startup script | [Shell Environment](#6.1) |
| `system/{x86,arm}/etc/ld.config.28.txt` | Dynamic linker configuration | [Linker Configuration](#8.1) |

Sources: [Dockerfile:1-92](), [entrypoint_root.sh:1-21](), [README.md:1-121]()

## Filesystem Layout Overview

The container filesystem follows **Android's directory structure** with compatibility symlinks for standard Linux paths:

```mermaid
graph TB
    subgraph "Root Filesystem /"
        SYSTEM["/system/<br/>System binaries (root:root, 755/644)"]
        DATA["/data/<br/>Application data (1000:1000, 700)"]
        COMPAT["/usr, /bin, /tmp<br/>Symlinks to Termux paths"]
    end
    
    subgraph "/system Structure"
        SYSARCH["/system/{x86,arm}/<br/>Architecture-specific"]
        SYSBIN["/system/bin/<br/>Shells, dnsmasq, busybox"]
        SYSLIB["/system/lib/<br/>libcutils.so, ld-android.so"]
        SYSETC["/system/etc/<br/>passwd, group, mkshrc"]
    end
    
    subgraph "/data Structure"
        TERMUX["/data/data/com.termux/"]
        CACHE["/data/data/com.termux/cache/"]
        FILES["/data/data/com.termux/files/"]
        USR["/data/data/com.termux/files/usr/<br/>Termux packages (PREFIX)"]
        HOME["/data/data/com.termux/files/home/<br/>User home directory"]
    end
    
    SYSTEM --> SYSARCH
    SYSARCH --> SYSBIN
    SYSARCH --> SYSLIB
    SYSARCH --> SYSETC
    
    DATA --> TERMUX
    TERMUX --> CACHE
    TERMUX --> FILES
    FILES --> USR
    FILES --> HOME
    
    COMPAT -.->|"symlinks to"| USR
```

**Directory Ownership and Permissions:**

| Path | Owner:Group | Permissions | Purpose |
|------|-------------|-------------|---------|
| `/system/` | `root:root` | 755 (dirs), 755 (executables), 644 (files) | Immutable system binaries |
| `/data/data/com.termux/` | `1000:1000` | 700 | Mutable Termux environment |
| `/data/data/com.termux/files/usr/` | `1000:1000` | 700 | Installed packages (PREFIX) |
| `/data/data/com.termux/files/home/` | `1000:1000` | 700 | User home directory |

For complete filesystem structure details, see [Filesystem Layout](#7).

Sources: [Dockerfile:22-36](), [Dockerfile:49-59]()

## Next Steps

- **Running containers**: See [Getting Started](#2) for usage examples
- **Building locally**: See [Building Images](#3) for build instructions
- **Understanding initialization**: See [Container Runtime](#4) for startup sequence details
- **Troubleshooting**: See [Known Issues and Troubleshooting](#8.3) for common problems

---

