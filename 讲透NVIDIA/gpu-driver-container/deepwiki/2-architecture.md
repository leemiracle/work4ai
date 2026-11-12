<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/gpu-driver-container · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.common-ci.yml](.common-ci.yml)
- [.github/workflows/image.yaml](.github/workflows/image.yaml)
- [.gitlab-ci.yml](.gitlab-ci.yml)
- [.nvidia-ci.yml](.nvidia-ci.yml)
- [Makefile](Makefile)
- [base/Dockerfile](base/Dockerfile)
- [base/generate-ci-config](base/generate-ci-config)
- [multi-arch.mk](multi-arch.mk)
- [native-only.mk](native-only.mk)
- [rhel8/Dockerfile](rhel8/Dockerfile)
- [rhel8/nvidia-driver](rhel8/nvidia-driver)
- [rhel9/Dockerfile](rhel9/Dockerfile)
- [rhel9/nvidia-driver](rhel9/nvidia-driver)
- [scripts/precompiled.sh](scripts/precompiled.sh)
- [ubuntu20.04/Dockerfile](ubuntu20.04/Dockerfile)
- [ubuntu20.04/nvidia-driver](ubuntu20.04/nvidia-driver)
- [ubuntu22.04/Dockerfile](ubuntu22.04/Dockerfile)
- [ubuntu22.04/nvidia-driver](ubuntu22.04/nvidia-driver)
- [versions.mk](versions.mk)

</details>



This page provides a high-level architectural overview of the NVIDIA GPU Driver Container build and delivery system. It describes the major components, their relationships, and the key design patterns that enable building and distributing containerized GPU drivers across multiple Linux distributions, driver versions, and hardware architectures.

For specific implementation details of the CI/CD pipeline, see [CI/CD Pipeline](#3). For runtime driver management details, see [Driver Management Scripts](#5). For build system configuration specifics, see [Build System Configuration](#6).

## System Overview

The gpu-driver-container repository implements an automated system for packaging NVIDIA GPU drivers as container images. The system supports three primary driver deployment modes:

| Deployment Mode | Description | Primary Use Case |
|----------------|-------------|------------------|
| **Passthrough/Baremetal** | Standard GPU drivers for bare-metal or VM passthrough | Kubernetes clusters, bare-metal systems |
| **vGPU Guest** | Virtual GPU drivers for guest VMs | Virtualized GPU workloads |
| **vGPU Host** | Hypervisor-level vGPU manager | Virtual GPU infrastructure |

The architecture separates concerns into three distinct layers: CI/CD automation, image build orchestration, and runtime driver management. This separation enables independent evolution of each layer while maintaining a cohesive delivery pipeline.

**Sources:** [.common-ci.yml:1-50](), [Makefile:1-84](), [rhel8/nvidia-driver:1-50]()

## Architectural Layers

```mermaid
graph TB
    subgraph "CI/CD Layer"
        GITLAB[".gitlab-ci.yml<br/>Primary Build Pipeline"]
        NVIDIA_CI[".nvidia-ci.yml<br/>Release Pipeline"]
        GITHUB[".github/workflows/image.yaml<br/>Precompiled Pipeline"]
        COMMON[".common-ci.yml<br/>Shared Configuration"]
    end
    
    subgraph "Build Layer"
        MAKEFILE["Makefile<br/>Build Orchestration"]
        VERSIONS["versions.mk<br/>DRIVER_VERSIONS"]
        DOCKERFILES["Distribution Dockerfiles<br/>rhel8/ ubuntu22.04/ etc"]
        INSTALL["install.sh<br/>Package Installation"]
        PRECOMPILED["scripts/precompiled.sh<br/>Precompiled Logic"]
    end
    
    subgraph "Runtime Layer"
        NVIDIA_DRIVER["nvidia-driver<br/>Driver Lifecycle Script"]
        COMMON_SH["common.sh<br/>Shared Functions"]
        OCP_ENTRY["ocp_dtk_entrypoint<br/>OpenShift Entry"]
    end
    
    subgraph "Artifact Registries"
        GHCR["ghcr.io/nvidia/driver<br/>Staging Registry"]
        NGC_STAGE["nvcr.io (staging)<br/>NGC Staging"]
        NGC_PROD["nvcr.io (prod)<br/>NGC Production"]
    end
    
    GITLAB --> COMMON
    NVIDIA_CI --> COMMON
    GITHUB --> COMMON
    
    COMMON --> MAKEFILE
    MAKEFILE --> VERSIONS
    MAKEFILE --> DOCKERFILES
    DOCKERFILES --> INSTALL
    DOCKERFILES --> NVIDIA_DRIVER
    DOCKERFILES --> COMMON_SH
    
    GITHUB --> PRECOMPILED
    PRECOMPILED --> MAKEFILE
    
    GITLAB --> GHCR
    GITHUB --> GHCR
    NVIDIA_CI --> NGC_STAGE
    NGC_STAGE --> NGC_PROD
```

**Sources:** [.gitlab-ci.yml:1-132](), [.nvidia-ci.yml:1-100](), [.github/workflows/image.yaml:1-194](), [Makefile:1-308](), [rhel8/nvidia-driver:1-30]()

### CI/CD Layer

The CI/CD layer consists of two parallel automation pipelines:

1. **GitLab CI Pipeline** ([.gitlab-ci.yml](), [.nvidia-ci.yml]()): Handles standard driver image builds for all distributions and performs release management to NGC registries. Executes on every merge request, commit to main, and tagged releases.

2. **GitHub Actions Pipeline** ([.github/workflows/image.yaml]()): Manages precompiled driver builds that include pre-built kernel modules for specific kernel versions. Runs on schedule (daily) and on pull requests.

Both pipelines share common configuration from [.common-ci.yml]() which defines:
- Driver version matrix: `DRIVER_VERSIONS ?= 535.274.02 570.195.03 580.95.05` ([versions.mk:16]())
- Distribution matrix: ubuntu20.04, ubuntu22.04, ubuntu24.04, rhel8, rhel9
- Architecture matrix: `linux/amd64`, `linux/arm64` ([.common-ci.yml:132-136]())
- Pipeline stages: `trigger`, `image-build`, `scan`, `release`, `ngc-publish` ([.common-ci.yml:25-31]())

**Sources:** [.common-ci.yml:1-367](), [.gitlab-ci.yml:1-132](), [.nvidia-ci.yml:1-533](), [.github/workflows/image.yaml:1-194]()

### Build Layer

The build layer orchestrates multi-distribution, multi-architecture image construction through a sophisticated Makefile-based system:

```mermaid
graph LR
    subgraph "Build Configuration"
        VERSIONS_MK["versions.mk<br/>DRIVER_VERSIONS<br/>GOLANG_VERSION"]
        MAKEFILE_VARS["Makefile Variables<br/>IMAGE_NAME<br/>DRIVER_TAG<br/>DIST"]
    end
    
    subgraph "Build Targets"
        BUILD_DIST["build-{dist}-{version}<br/>e.g. build-ubuntu22.04-535.274.02"]
        PUSH_DIST["push-{dist}-{version}<br/>e.g. push-rhel8-570.195.03"]
        BUILD_BASE["build-base-{target}<br/>e.g. build-base-jammy"]
    end
    
    subgraph "Distribution Dockerfiles"
        UBUNTU22["ubuntu22.04/Dockerfile<br/>TARGETARCH<br/>DRIVER_VERSION<br/>DRIVER_BRANCH"]
        RHEL8["rhel8/Dockerfile<br/>BASE_URL<br/>DRIVER_TYPE"]
        RHEL9["rhel9/Dockerfile"]
        PRECOMP["ubuntu22.04/precompiled/Dockerfile<br/>KERNEL_VERSION"]
    end
    
    subgraph "Helper Scripts"
        INSTALL_SH["install.sh<br/>depinstall<br/>extrapkgsinstall"]
        PRECOMP_SH["scripts/precompiled.sh<br/>buildBaseImage()<br/>sourceVersions()"]
    end
    
    VERSIONS_MK --> MAKEFILE_VARS
    MAKEFILE_VARS --> BUILD_DIST
    MAKEFILE_VARS --> PUSH_DIST
    MAKEFILE_VARS --> BUILD_BASE
    
    BUILD_DIST --> UBUNTU22
    BUILD_DIST --> RHEL8
    BUILD_DIST --> RHEL9
    BUILD_DIST --> PRECOMP
    
    UBUNTU22 --> INSTALL_SH
    RHEL8 --> INSTALL_SH
    RHEL9 --> INSTALL_SH
    PRECOMP --> PRECOMP_SH
    
    BUILD_BASE --> PRECOMP_SH
```

The Makefile implements a pattern-based target system where:
- `$(DRIVER_BUILD_TARGETS)` expands to all distribution-version combinations ([Makefile:64-65]())
- Each target parses its name to extract `DIST` and `DRIVER_VERSION` ([Makefile:152-154]())
- Distribution-specific rules override variables (e.g., `build-rhcos%: SUBDIR = rhel8` [Makefile:177]())
- Multi-arch builds conditionally use Docker Buildx based on `BUILD_MULTI_ARCH_IMAGES` ([Makefile:15-20]())

**Sources:** [Makefile:1-308](), [versions.mk:1-19](), [ubuntu22.04/Dockerfile:1-117](), [rhel8/Dockerfile:1-110](), [scripts/precompiled.sh:1-114]()

### Runtime Layer

The runtime layer manages driver installation, kernel module compilation, and daemon lifecycle through distribution-specific `nvidia-driver` scripts:

```mermaid
graph TB
    subgraph "Entry Points"
        DOCKERFILE_ENTRY["ENTRYPOINT: nvidia-driver init"]
        OCP_ENTRY["ocp_dtk_entrypoint<br/>OpenShift Driver Toolkit"]
    end
    
    subgraph "nvidia-driver Commands"
        INIT["init()<br/>Full initialization"]
        BUILD["build()<br/>Compile modules only"]
        LOAD["load()<br/>Load modules only"]
        UPDATE["update(kernel)<br/>Kernel update hook"]
    end
    
    subgraph "Core Functions"
        PREPARE["_prepare()<br/>Extract installer<br/>_resolve_kernel_type()"]
        INSTALL_PREREQ["_install_prerequisites()<br/>Install kernel headers<br/>Generate version string"]
        CREATE_PKG["_create_driver_package()<br/>Compile modules<br/>Sign modules<br/>mkprecompiled"]
        INSTALL_DRV["_install_driver()<br/>nvidia-installer<br/>--kernel-module-only"]
        LOAD_DRV["_load_driver()<br/>modprobe nvidia<br/>nvidia-persistenced<br/>nv-fabricmanager"]
        MOUNT_ROOT["_mount_rootfs()<br/>mount --rbind /<br/>/run/nvidia/driver"]
    end
    
    subgraph "Shared Utilities"
        COMMON_SH["common.sh<br/>_gpu_direct_rdma_enabled()<br/>_start_vgpu_topology_daemon()"]
    end
    
    DOCKERFILE_ENTRY --> INIT
    OCP_ENTRY --> BUILD
    
    INIT --> PREPARE
    PREPARE --> INSTALL_PREREQ
    INSTALL_PREREQ --> CREATE_PKG
    CREATE_PKG --> INSTALL_DRV
    INSTALL_DRV --> LOAD_DRV
    LOAD_DRV --> MOUNT_ROOT
    
    BUILD --> PREPARE
    UPDATE --> INSTALL_PREREQ
    LOAD --> LOAD_DRV
    
    LOAD_DRV --> COMMON_SH
```

Each `nvidia-driver` script implements a state machine with distinct phases:

1. **Preparation**: Extract NVIDIA installer `.run` file, install userspace components, determine kernel module type (open vs proprietary) via `_resolve_kernel_type()` ([rhel8/nvidia-driver:622-639]())

2. **Build**: Check if precompiled package exists with `_kernel_requires_package()` ([rhel8/nvidia-driver:176-193]()), compile modules if needed with `_create_driver_package()` ([rhel8/nvidia-driver:196-259]())

3. **Installation**: Run `nvidia-installer --kernel-module-only` to install compiled modules ([rhel8/nvidia-driver:525-557]())

4. **Loading**: Load kernel modules via `modprobe`, start `nvidia-persistenced`, conditionally start `nv-fabricmanager` for NVSwitch systems ([rhel8/nvidia-driver:344-422]())

5. **Mounting**: Bind-mount driver rootfs to `/run/nvidia/driver` for host access ([rhel8/nvidia-driver:560-575]())

**Sources:** [rhel8/nvidia-driver:1-850](), [rhel9/nvidia-driver:1-850](), [ubuntu22.04/nvidia-driver:1-800](), [ubuntu20.04/nvidia-driver:1-700]()

## Data Flow Architecture

The following diagram shows how artifacts flow through the system from source code to production registries, including the distinction between standard and precompiled build paths:

```mermaid
graph TB
    subgraph "Source Control"
        GIT_REPO["git repository<br/>github.com/NVIDIA/<br/>gpu-driver-container"]
        VERSIONS_FILE["versions.mk<br/>DRIVER_VERSIONS"]
    end
    
    subgraph "CI Triggers"
        MERGE_REQ["Merge Request<br/>trigger-pipeline job"]
        SCHEDULE["Scheduled Build<br/>Daily 09:00 UTC"]
        TAG_EVENT["Git Tag Event<br/>Release trigger"]
    end
    
    subgraph "Build Paths"
        STANDARD_BUILD["Standard Build Path<br/>make build-{dist}-{version}<br/>Runtime compilation"]
        PRECOMP_BUILD["Precompiled Build Path<br/>scripts/precompiled.sh build<br/>Per-kernel modules"]
    end
    
    subgraph "Base Images"
        BASE_JAMMY["base-jammy-{lts}-{flavor}<br/>base/Dockerfile<br/>generate-ci-config"]
        BASE_NOBLE["base-noble-{lts}-{flavor}<br/>Latest kernel detection"]
    end
    
    subgraph "Driver Sources"
        NVIDIA_DOWNLOAD["us.download.nvidia.com/tesla<br/>NVIDIA-Linux-*.run"]
        CUDA_REPOS["developer.download.nvidia.com<br/>fabricmanager<br/>libnvidia-nscq"]
    end
    
    subgraph "Container Images"
        STANDARD_IMG["Standard Images<br/>{version}-{dist}<br/>e.g. 535.274.02-ubuntu22.04"]
        PRECOMP_IMG["Precompiled Images<br/>{branch}-{kernel}-{dist}<br/>e.g. 535-5.15.0-124-ubuntu22.04"]
    end
    
    subgraph "Security & Validation"
        SCAN["pulse-cli scan<br/>SBOM generation<br/>CVE detection"]
        E2E["E2E Tests<br/>Holodeck provisioning<br/>GPU validation"]
    end
    
    subgraph "Registries"
        GHCR_REG["ghcr.io/nvidia/driver<br/>Staging & GitHub builds"]
        NGC_STAGING["nvcr.io (staging)<br/>Pre-release validation"]
        NGC_PROD["nvcr.io/nvidia/driver<br/>Production registry"]
    end
    
    GIT_REPO --> MERGE_REQ
    GIT_REPO --> TAG_EVENT
    VERSIONS_FILE --> STANDARD_BUILD
    SCHEDULE --> PRECOMP_BUILD
    
    MERGE_REQ --> STANDARD_BUILD
    TAG_EVENT --> STANDARD_BUILD
    
    PRECOMP_BUILD --> BASE_JAMMY
    PRECOMP_BUILD --> BASE_NOBLE
    BASE_JAMMY --> PRECOMP_IMG
    BASE_NOBLE --> PRECOMP_IMG
    
    STANDARD_BUILD --> NVIDIA_DOWNLOAD
    STANDARD_BUILD --> CUDA_REPOS
    NVIDIA_DOWNLOAD --> STANDARD_IMG
    CUDA_REPOS --> STANDARD_IMG
    
    STANDARD_IMG --> SCAN
    PRECOMP_IMG --> SCAN
    SCAN --> E2E
    E2E --> GHCR_REG
    E2E --> NGC_STAGING
    NGC_STAGING --> NGC_PROD
```

**Standard build path** ([.gitlab-ci.yml:19-99]()):
1. Trigger from merge request or tag
2. Execute `make build-${DIST}-${DRIVER_VERSION}` for each distribution-version pair
3. Download NVIDIA installer from `us.download.nvidia.com` during image build ([rhel8/Dockerfile:65-69]())
4. Run security scans via `pulse-cli` ([.nvidia-ci.yml:151-186]())
5. Push to staging registry `ghcr.io/nvidia/driver` ([.nvidia-ci.yml:45-69]())
6. Promote to NGC staging, then production ([.nvidia-ci.yml:336-419]())

**Precompiled build path** ([scripts/precompiled.sh:1-114]()):
1. Daily schedule triggers GitHub Actions workflow ([.github/workflows/image.yaml:18-24]())
2. Build base images with `build-base-{jammy|noble}` to detect latest kernel ([Makefile:206-222]())
3. Execute `scripts/precompiled.sh build` which sources kernel version from base image ([scripts/precompiled.sh:8-37]())
4. Build per-kernel images with pre-compiled modules ([.gitlab-ci.yml:103-132]())
5. Follow same scan and promotion path as standard builds

**Sources:** [.gitlab-ci.yml:1-132](), [.nvidia-ci.yml:1-533](), [.github/workflows/image.yaml:1-194](), [scripts/precompiled.sh:1-114](), [Makefile:206-230]()

## Build-Time Architecture

The build process uses multi-stage Dockerfiles to separate build dependencies from runtime artifacts:

```mermaid
graph TB
    subgraph "Stage 1: Build Tools"
        BUILD_BASE["FROM nvcr.io/nvidia/cuda:*-base<br/>Multi-arch base image"]
        GO_INSTALL["Install Go ${GOLANG_VERSION}<br/>Build vgpu-util"]
        VGPU_UTIL["git clone gpu-driver-container<br/>cd vgpu/src && go build"]
    end
    
    subgraph "Stage 2: Runtime Image"
        RUNTIME_BASE["FROM nvcr.io/nvidia/cuda:*-base<br/>TARGETARCH, DRIVER_VERSION"]
        REPO_SETUP["install.sh reposetup<br/>Add CUDA repos<br/>GPG key verification"]
        DEP_INSTALL["install.sh depinstall<br/>gcc, make, kmod<br/>linux-headers support"]
        DRIVER_DOWNLOAD["Download NVIDIA-Linux-*.run<br/>BASE_URL/DRIVER_VERSION"]
        EXTRA_PKGS["install.sh extrapkgsinstall<br/>nvidia-fabricmanager<br/>libnvidia-nscq"]
        COPY_SCRIPTS["COPY nvidia-driver<br/>COPY common.sh<br/>COPY --from=build vgpu-util"]
        CVE_UPDATES["Apply CVE_UPDATES<br/>Package upgrades"]
    end
    
    subgraph "Build Arguments"
        ARGS["ARG TARGETARCH<br/>ARG DRIVER_VERSION<br/>ARG DRIVER_BRANCH<br/>ARG DRIVER_TYPE<br/>ARG GOLANG_VERSION<br/>ARG CVE_UPDATES"]
    end
    
    subgraph "Entry Point"
        ENTRYPOINT["ENTRYPOINT: nvidia-driver init"]
    end
    
    ARGS --> BUILD_BASE
    ARGS --> RUNTIME_BASE
    
    BUILD_BASE --> GO_INSTALL
    GO_INSTALL --> VGPU_UTIL
    
    RUNTIME_BASE --> REPO_SETUP
    REPO_SETUP --> DEP_INSTALL
    DEP_INSTALL --> DRIVER_DOWNLOAD
    DRIVER_DOWNLOAD --> EXTRA_PKGS
    EXTRA_PKGS --> COPY_SCRIPTS
    VGPU_UTIL --> COPY_SCRIPTS
    COPY_SCRIPTS --> CVE_UPDATES
    CVE_UPDATES --> ENTRYPOINT
```

Key build-time patterns:

1. **Multi-architecture support**: Uses `TARGETARCH` ARG to download architecture-specific binaries ([rhel8/Dockerfile:26-27](), [ubuntu22.04/Dockerfile:45-46]())

2. **Late binding**: Driver `.run` file downloaded during build but not extracted ([rhel8/Dockerfile:65-69]()), actual installation happens at container runtime

3. **Conditional vGPU support**: vGPU utility only built when `DRIVER_TYPE=vgpu` ([ubuntu22.04/Dockerfile:34-38]())

4. **Security hardening**: CVE updates applied via `CVE_UPDATES` build arg ([.common-ci.yml:111](), [ubuntu22.04/Dockerfile:104-108]())

5. **Distribution abstraction**: `install.sh` script abstracts package manager differences between apt (Ubuntu) and dnf (RHEL) ([rhel8/Dockerfile:57](), [ubuntu22.04/Dockerfile:73]())

**Sources:** [rhel8/Dockerfile:1-110](), [ubuntu22.04/Dockerfile:1-117](), [rhel9/Dockerfile:1-115](), [ubuntu20.04/Dockerfile:1-106]()

## Runtime Architecture

At container startup, the `nvidia-driver init` command executes a carefully orchestrated sequence to install and load drivers on the host:

```mermaid
graph TB
    subgraph "Container Startup"
        START["Container starts<br/>ENTRYPOINT: nvidia-driver init"]
        LOCK["Acquire PID lock<br/>/run/nvidia/nvidia-driver.pid"]
    end
    
    subgraph "Driver Preparation Phase"
        EXTRACT["Extract NVIDIA-Linux-*.run<br/>nvidia-installer -x"]
        USERSPACE["Install userspace components<br/>Libraries to /usr/lib64<br/>Binaries to /usr/bin"]
        RESOLVE_TYPE["_resolve_kernel_type()<br/>nvidia-installer --print-recommended<br/>KERNEL_TYPE=kernel|kernel-open"]
        COPY_SOURCES["Copy kernel module sources<br/>/usr/src/nvidia-${DRIVER_VERSION}/<br/>kernel/ or kernel-open/"]
    end
    
    subgraph "Module Build Phase"
        CHECK_PKG["_kernel_requires_package()<br/>Check precompiled/*/"]
        GET_HEADERS["_install_prerequisites()<br/>dnf install kernel-headers<br/>kernel-devel kernel-core"]
        COMPILE["_create_driver_package()<br/>make nv-linux.o<br/>ld -r -o nvidia.ko<br/>mkprecompiled --pack"]
        INSTALLER["_install_driver()<br/>nvidia-installer<br/>--kernel-module-only<br/>--skip-module-load"]
    end
    
    subgraph "Module Load Phase"
        GET_PARAMS["_get_module_params()<br/>Parse /drivers/*.conf<br/>NVIDIA_MODULE_PARAMS"]
        LOAD_MODS["modprobe nvidia<br/>modprobe nvidia-uvm<br/>modprobe nvidia-modeset"]
        LOAD_PEERMEM["if GPU_DIRECT_RDMA_ENABLED<br/>modprobe nvidia-peermem"]
        START_PERSIST["nvidia-persistenced<br/>--persistence-mode"]
        START_GRIDD["if DRIVER_TYPE=vgpu<br/>nvidia-gridd"]
        START_FABRIC["if NVSwitch detected<br/>nv-fabricmanager"]
    end
    
    subgraph "Host Integration Phase"
        MOUNT["_mount_rootfs()<br/>mount --rbind /<br/>/run/nvidia/driver"]
        HOOK["_write_kernel_update_hook()<br/>/run/kernel/postinst.d/"]
        SELINUX["if SELinux enabled<br/>chcon -R -t container_file_t"]
    end
    
    subgraph "Steady State"
        WAIT["sleep infinity &<br/>trap signals for shutdown"]
    end
    
    START --> LOCK
    LOCK --> EXTRACT
    EXTRACT --> USERSPACE
    USERSPACE --> RESOLVE_TYPE
    RESOLVE_TYPE --> COPY_SOURCES
    
    COPY_SOURCES --> CHECK_PKG
    CHECK_PKG -->|"No precompiled package"| GET_HEADERS
    CHECK_PKG -->|"Precompiled exists"| INSTALLER
    GET_HEADERS --> COMPILE
    COMPILE --> INSTALLER
    
    INSTALLER --> GET_PARAMS
    GET_PARAMS --> LOAD_MODS
    LOAD_MODS --> LOAD_PEERMEM
    LOAD_PEERMEM --> START_PERSIST
    START_PERSIST --> START_GRIDD
    START_GRIDD --> START_FABRIC
    
    START_FABRIC --> MOUNT
    MOUNT --> HOOK
    HOOK --> SELINUX
    SELINUX --> WAIT
```

**Kernel module type resolution** ([rhel8/nvidia-driver:622-643]()):
- For driver branch >= 560: Defaults to open kernel modules (`kernel-open`)
- For driver branch < 560: Defaults to proprietary modules (`kernel`)
- Can be overridden via `KERNEL_MODULE_TYPE` environment variable
- Uses `nvidia-installer --print-recommended-kernel-module-type` to determine optimal choice

**Module parameter configuration** ([rhel8/nvidia-driver:305-341]()):
- Reads configuration files from `/drivers/*.conf`
- Supports: `nvidia.conf`, `nvidia-uvm.conf`, `nvidia-modeset.conf`, `nvidia-peermem.conf`
- Starting from driver 580, automatically adds `NVreg_CoherentGPUMemoryMode=driver` ([rhel8/nvidia-driver:311]())
- Parameters passed to `modprobe` during module loading

**Daemon management**:
- `nvidia-persistenced`: Always started for persistence mode ([rhel8/nvidia-driver:385]())
- `nvidia-gridd`: Started only when `DRIVER_TYPE=vgpu` ([rhel8/nvidia-driver:387-401]())
- `nv-fabricmanager`: Started when NVSwitch devices detected ([rhel8/nvidia-driver:418-421]())
- NVLink5+ systems: Both `nv-fabricmanager` and `nvlsm` started ([rhel8/nvidia-driver:403-416]())

**Host integration**:
- Driver files mounted to `/run/nvidia/driver` via bind mount ([rhel8/nvidia-driver:560-575]())
- SELinux contexts applied if enabled ([rhel8/nvidia-driver:567-574]())
- Kernel update hook installed to `/run/kernel/postinst.d/` for automatic recompilation ([rhel8/nvidia-driver:586-604]())

**Sources:** [rhel8/nvidia-driver:753-759](), [rhel8/nvidia-driver:622-643](), [rhel8/nvidia-driver:305-341](), [rhel8/nvidia-driver:344-422](), [rhel8/nvidia-driver:560-604](), [ubuntu22.04/nvidia-driver:564-750]()

## Key Design Patterns

### Late Binding Pattern

Driver kernel modules are compiled at container runtime rather than build time, enabling a single container image to support multiple kernel versions:

```
Image Build Time:
  - Include NVIDIA-Linux-*.run (installer)
  - Include kernel module source code
  - Include mkprecompiled tool

Container Runtime:
  - Detect host kernel version
  - Install kernel headers matching host
  - Compile modules against host kernel
  - Install and load modules
```

This pattern is implemented in `_kernel_requires_package()` ([rhel8/nvidia-driver:176-193]()), which checks if a precompiled package already exists for the current kernel before triggering compilation.

**Sources:** [rhel8/nvidia-driver:176-193](), [rhel8/nvidia-driver:196-259](), [ubuntu22.04/nvidia-driver:115-132]()

### Distribution Abstraction Pattern

Common driver logic is shared via `common.sh` while distribution-specific implementations handle package management differences:

| Function | Ubuntu Implementation | RHEL Implementation |
|----------|----------------------|---------------------|
| Package cache update | `apt-get -qq update` | `yum -q makecache` |
| Install headers | `apt-get install linux-headers-*` | `dnf install kernel-headers-*` |
| Resolve kernel version | Parse `apt-cache show` output | Parse `yum list available` output |
| Extract vmlinuz | Direct `strings` on decompressed kernel | `extract-vmlinux` then `strings` |

Each distribution's `nvidia-driver` script sources `common.sh` ([rhel8/nvidia-driver:26]()) and implements distribution-specific functions with the same interface.

**Sources:** [rhel8/nvidia-driver:28-45](), [ubuntu22.04/nvidia-driver:38-74](), [rhel9/nvidia-driver:29-88]()

### Matrix Build Pattern

The Makefile implements a matrix expansion pattern to generate all distribution-version-architecture combinations:

```makefile
DISTRIBUTIONS := ubuntu18.04 ubuntu20.04 ubuntu22.04 ubuntu24.04 rhel8 rhel9
DRIVER_VERSIONS := 535.274.02 570.195.03 580.95.05

# Generates: build-ubuntu22.04-535.274.02, build-ubuntu22.04-570.195.03, ...
BUILD_TARGETS := $(patsubst %, build-%, $(DISTRIBUTIONS))
DRIVER_BUILD_TARGETS := $(foreach build_target, $(BUILD_TARGETS), 
                        $(addprefix $(build_target)-, $(DRIVER_VERSIONS)))
```

Target names are parsed using Make's `subst` and `word` functions to extract variables ([Makefile:152-156]()):

```makefile
build-%: DIST = $(word 2,$(subst -, ,$@))
build-%: DRIVER_VERSION = $(word 3,$(subst -, ,$@))
build-%: DRIVER_BRANCH = $(word 1,$(subst ., ,${DRIVER_VERSION}))
```

**Sources:** [Makefile:57-77](), [Makefile:150-176](), [.common-ci.yml:81-99]()

### Precompiled Optimization Pattern

For production deployments with known kernel versions, precompiled images skip runtime compilation:

```
Base Image Build (daily):
  - Launch temporary container with target kernel flavor
  - Query package repositories for latest kernel
  - Write KERNEL_VERSION to /var/kernel_version.txt

Precompiled Image Build:
  - Source KERNEL_VERSION from base image
  - Install exact kernel headers at build time
  - Compile and sign modules during image build
  - Package modules in precompiled/ directory

Container Runtime:
  - Skip compilation (_kernel_requires_package returns false)
  - Directly install pre-built modules
  - Load modules and start daemons
```

This pattern reduces container startup time from ~5 minutes to ~30 seconds for kernel module installation.

**Implementation**: [scripts/precompiled.sh:8-37](), [base/generate-ci-config:1-34](), [.github/workflows/image.yaml:165-194]()

**Sources:** [scripts/precompiled.sh:1-114](), [base/generate-ci-config:1-34](), [base/Dockerfile:1-110](), [.github/workflows/image.yaml:93-194]()

### Security Scanning Pattern

Every image passes through automated security validation before promotion to production:

```mermaid
graph LR
    BUILD["Image Built<br/>CI_REGISTRY_IMAGE"]
    PULL["pull-{dist}-{version}<br/>Platform-specific pull"]
    ARCHIVE["archive-{dist}-{version}<br/>docker save archive.tar"]
    SCAN["pulse-cli scan<br/>-i archive.tar<br/>-p $CONTAINER_POLICY"]
    ARTIFACTS["Artifacts Generated<br/>sbom.json<br/>vulns.json<br/>policy_evaluation.json"]
    GATE["Policy Check<br/>Block if violations"]
    RELEASE["Release to Staging<br/>NGC_STAGING_REGISTRY"]
    
    BUILD --> PULL
    PULL --> ARCHIVE
    ARCHIVE --> SCAN
    SCAN --> ARTIFACTS
    ARTIFACTS --> GATE
    GATE -->|"Pass"| RELEASE
    GATE -->|"Fail"| BUILD
```

The scan stage runs for each platform (`linux/amd64`, `linux/arm64`) and generates:
- Software Bill of Materials (SBOM) in SPDX format
- Vulnerability scan results
- License compliance report
- Policy evaluation results

Scans can be skipped via commit message `[skip scans]` or environment variable `SKIP_SCANS=yes` ([.nvidia-ci.yml:158-161]()).

**Sources:** [.nvidia-ci.yml:151-253](), [.common-ci.yml:218-228]()

---

