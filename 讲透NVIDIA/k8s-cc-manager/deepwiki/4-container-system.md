<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/k8s-cc-manager · page 4 Container System · fetched 2026-10-26 -->

# Container System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/container/Dockerfile.ubi8](deployments/container/Dockerfile.ubi8)
- [deployments/container/Makefile](deployments/container/Makefile)

</details>



The Container System encompasses the containerization infrastructure for the k8s-cc-manager application, including Docker image definitions, multi-architecture build processes, and registry distribution mechanisms. This system packages the Go application, shell scripts, and supporting tools into deployable container images that can run across different architectures and Kubernetes environments.

For detailed information about the specific container images and their contents, see [Container Images](#4.1). For build system mechanics and multi-architecture support, see [Build System](#4.2).

## Container Build Architecture

The container system uses a multi-stage build process to create optimized images that include all necessary components for GPU confidential computing management.

### Multi-Stage Build Process

```mermaid
graph TD
    subgraph "Build Stage"
        GOLANG_BASE["golang:${GOLANG_VERSION}"]
        SRC_COPY["Copy source code"]
        GO_BUILD["CGO_ENABLED=0 go build"]
        SCRIPT_COPY["Copy cc-manager.sh"]
        KUBECTL_DL["Download kubectl binary"]
        ARTIFACTS["/artifacts/\nk8s-cc-manager\ncc-manager.sh\nkubectl"]
    end
    
    subgraph "Runtime Stage"
        CUDA_BASE["nvidia/cuda:${CUDA_VERSION}-base-${BASE_DIST}"]
        PYTHON_INSTALL["Install python38, git, numpy"]
        GPU_TOOLS_CLONE["Clone gpu-admin-tools"]
        BINARY_COPY["Copy artifacts from build stage"]
        LABELS["Set container labels"]
        FINAL_IMAGE["k8s-cc-manager:${IMAGE_TAG}"]
    end
    
    GOLANG_BASE --> SRC_COPY
    SRC_COPY --> GO_BUILD
    SRC_COPY --> SCRIPT_COPY
    GO_BUILD --> ARTIFACTS
    SCRIPT_COPY --> ARTIFACTS
    KUBECTL_DL --> ARTIFACTS
    
    CUDA_BASE --> PYTHON_INSTALL
    PYTHON_INSTALL --> GPU_TOOLS_CLONE
    GPU_TOOLS_CLONE --> BINARY_COPY
    ARTIFACTS --> BINARY_COPY
    BINARY_COPY --> LABELS
    LABELS --> FINAL_IMAGE
```

Sources: [deployments/container/Dockerfile.ubi8:19-66]()

### Final Container Image Structure

The resulting container includes multiple components organized in the filesystem:

```mermaid
graph TB
    subgraph "Container Image: k8s-cc-manager"
        subgraph "/usr/bin/"
            K8S_CC_MANAGER["/usr/bin/k8s-cc-manager"]
            KUBECTL_BIN["/usr/bin/kubectl"]
            CC_MANAGER_SCRIPT["/usr/bin/cc-manager.sh"]
            GPU_ADMIN_TOOLS["/usr/bin/gpu-admin-tools/"]
        end
        
        subgraph "Python Environment"
            PYTHON38["python38"]
            NUMPY["numpy package"]
        end
        
        subgraph "Base System"
            UBI8_BASE["Red Hat UBI8"]
            CUDA_RUNTIME["NVIDIA CUDA runtime"]
            LICENSES["/licenses/NGC-DL-CONTAINER-LICENSE"]
        end
        
        ENTRYPOINT["ENTRYPOINT: k8s-cc-manager"]
    end
    
    K8S_CC_MANAGER --> CC_MANAGER_SCRIPT
    CC_MANAGER_SCRIPT --> KUBECTL_BIN
    CC_MANAGER_SCRIPT --> GPU_ADMIN_TOOLS
    GPU_ADMIN_TOOLS --> PYTHON38
    GPU_ADMIN_TOOLS --> NUMPY
```

Sources: [deployments/container/Dockerfile.ubi8:51-66]()

## Build System Architecture

The build system supports multiple architectures and distributions through a flexible Makefile-based approach.

### Build Target Structure

```mermaid
graph TD
    subgraph "Make Targets"
        DISTRIBUTIONS["DISTRIBUTIONS := ubi8"]
        BUILD_TARGETS["BUILD_TARGETS := build-ubi8"]
        PUSH_TARGETS["PUSH_TARGETS := push-ubi8"]
        DEFAULT_PUSH["DEFAULT_PUSH_TARGET := ubi8"]
    end
    
    subgraph "Build Configuration"
        VERSIONS_MK["versions.mk"]
        MULTI_ARCH_FLAG["BUILD_MULTI_ARCH_IMAGES"]
        NATIVE_MK["native-only.mk"]
        MULTI_ARCH_MK["multi-arch.mk"]
    end
    
    subgraph "Docker Build Process"
        BUILDKIT["DOCKER_BUILDKIT=1"]
        BUILDX["docker buildx build"]
        BUILD_ARGS["--build-arg BASE_DIST\n--build-arg CUDA_VERSION\n--build-arg GOLANG_VERSION\n--build-arg VERSION\n--build-arg CVE_UPDATES\n--build-arg GPU_ADMIN_TOOLS_VERSION"]
        DOCKERFILE_UBI8["Dockerfile.ubi8"]
    end
    
    DISTRIBUTIONS --> BUILD_TARGETS
    BUILD_TARGETS --> PUSH_TARGETS
    VERSIONS_MK --> BUILD_ARGS
    MULTI_ARCH_FLAG --> NATIVE_MK
    MULTI_ARCH_FLAG --> MULTI_ARCH_MK
    BUILD_TARGETS --> BUILDKIT
    BUILDKIT --> BUILDX
    BUILDX --> BUILD_ARGS
    BUILD_ARGS --> DOCKERFILE_UBI8
```

Sources: [deployments/container/Makefile:22-90]()

### Image Tagging and Registry Strategy

The build system implements a comprehensive tagging strategy for different environments and architectures:

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `IMAGE_NAME` | Base image name | `nvidia/k8s-cc-manager` |
| `IMAGE_VERSION` | Version from versions.mk | `v0.1.0` |
| `DIST` | Distribution suffix | `ubi8` |
| `IMAGE_TAG` | Full image tag | `v0.1.0-ubi8` |
| `OUT_IMAGE_NAME` | Output registry name | `nvidia/k8s-cc-manager` |

Sources: [deployments/container/Makefile:25-38]()

## Multi-Architecture Support

The container system supports building for multiple architectures using Docker Buildx:

```mermaid
graph LR
    subgraph "Architecture Detection"
        TARGETARCH["ARG TARGETARCH"]
        X86_64["x86_64 → amd64"]
        AARCH64["aarch64 → arm64"]
    end
    
    subgraph "Build Process"
        BUILDX_FLAG["BUILD_MULTI_ARCH_IMAGES=true"]
        DOCKER_BUILDX["docker buildx build"]
        PLATFORM_OPTIONS["DOCKER_BUILD_PLATFORM_OPTIONS"]
    end
    
    subgraph "Binary Downloads"
        KUBECTL_AMD64["kubectl linux/amd64"]
        KUBECTL_ARM64["kubectl linux/arm64"]
        OS_ARCH_CONVERT["OS_ARCH=${TARGETARCH/x86_64/amd64}"]
    end
    
    TARGETARCH --> X86_64
    TARGETARCH --> AARCH64
    BUILDX_FLAG --> DOCKER_BUILDX
    DOCKER_BUILDX --> PLATFORM_OPTIONS
    X86_64 --> OS_ARCH_CONVERT
    AARCH64 --> OS_ARCH_CONVERT
    OS_ARCH_CONVERT --> KUBECTL_AMD64
    OS_ARCH_CONVERT --> KUBECTL_ARM64
```

Sources: [deployments/container/Dockerfile.ubi8:23-34](), [deployments/container/Makefile:15-54]()

## Build Arguments and Customization

The Dockerfile accepts multiple build arguments for customization:

| Build Argument | Purpose | Used For |
|----------------|---------|----------|
| `CUDA_VERSION` | CUDA base image version | Runtime environment |
| `BASE_DIST` | Base distribution (ubi8) | OS selection |
| `GOLANG_VERSION` | Go compiler version | Build stage |
| `VERSION` | Application version | Image labeling |
| `GIT_COMMIT` | Git commit hash | Build metadata |
| `GPU_ADMIN_TOOLS_VERSION` | gpu-admin-tools branch/tag | Python tools |
| `CVE_UPDATES` | Security updates | Vulnerability patching |

Sources: [deployments/container/Dockerfile.ubi8:15-88]()

## Security and Compliance Features

The container includes security scanning integration and license compliance:

```mermaid
graph TD
    subgraph "Security Measures"
        CGO_DISABLED["CGO_ENABLED=0"]
        CVE_UPDATES_ARG["CVE_UPDATES build arg"]
        YUM_UPDATE["yum update -y ${CVE_UPDATES}"]
        CACHE_CLEANUP["rm -rf /var/cache/yum/*"]
    end
    
    subgraph "License Compliance"
        NGC_LICENSE["/NGC-DL-CONTAINER-LICENSE"]
        LICENSES_DIR["/licenses/"]
        CONTAINER_LABELS["Container metadata labels"]
    end
    
    subgraph "Image Metadata"
        DISPLAY_NAME["io.k8s.display-name"]
        VENDOR_LABEL["vendor=NVIDIA"]
        VERSION_LABEL["version=${VERSION}"]
        SUMMARY_LABEL["summary=Manages CC mode"]
    end
    
    CGO_DISABLED --> CVE_UPDATES_ARG
    CVE_UPDATES_ARG --> YUM_UPDATE
    YUM_UPDATE --> CACHE_CLEANUP
    NGC_LICENSE --> LICENSES_DIR
    LICENSES_DIR --> CONTAINER_LABELS
    CONTAINER_LABELS --> DISPLAY_NAME
    CONTAINER_LABELS --> VENDOR_LABEL
    CONTAINER_LABELS --> VERSION_LABEL
    CONTAINER_LABELS --> SUMMARY_LABEL
```

Sources: [deployments/container/Dockerfile.ubi8:30-64]()

The container system provides a complete packaging solution for the k8s-cc-manager application, supporting multiple architectures while maintaining security best practices and license compliance requirements for enterprise Kubernetes deployments.

---

