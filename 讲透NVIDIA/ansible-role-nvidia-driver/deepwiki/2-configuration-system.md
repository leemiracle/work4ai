<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ansible-role-nvidia-driver · page 2 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [defaults/main.yml](defaults/main.yml)
- [files/nvidia-persistenced-override.conf](files/nvidia-persistenced-override.conf)
- [vars/main.yml](vars/main.yml)

</details>



## Purpose and Scope

The configuration system controls the behavior of the NVIDIA driver installation role through a hierarchical variable system with default values, OS-specific overrides, and computed runtime variables. This system enables the role to adapt to different Linux distributions, package sources, and installation requirements while maintaining consistent defaults.

For information about how these configurations are used during installation, see [Installation Systems](#3). For testing configuration scenarios, see [Testing Framework](#4).

## Configuration Architecture Overview

The configuration system operates through a three-layer hierarchy that progressively specializes from global defaults to OS-specific parameters to runtime-computed values.

### Configuration Layer Architecture

```mermaid
graph TB
    subgraph "Layer1[Default Configuration Layer]"
        DEFAULTS["defaults/main.yml"]
        GLOBAL_PARAMS["Global Parameters<br/>• nvidia_driver_branch<br/>• nvidia_driver_package_state<br/>• nvidia_driver_persistence_mode_on<br/>• nvidia_driver_skip_reboot"]
    end
    
    subgraph "Layer2[OS-Specific Configuration Layer]"
        REDHAT_CONFIG["RedHat Configuration<br/>• epel_package<br/>• nvidia_driver_rhel_cuda_repo_baseurl<br/>• nvidia_driver_rhel_cuda_repo_gpgkey"]
        UBUNTU_CONFIG["Ubuntu Configuration<br/>• nvidia_driver_ubuntu_install_from_cuda_repo<br/>• nvidia_driver_ubuntu_packages<br/>• nvidia_driver_ubuntu_cuda_keyring_url"]
    end
    
    subgraph "Layer3[Runtime Variables Layer]"
        VARS["vars/main.yml"]
        COMPUTED_VARS["Computed Variables<br/>• _ubuntu_repo_dir<br/>• _rhel_repo_dir"]
    end
    
    DEFAULTS --> GLOBAL_PARAMS
    GLOBAL_PARAMS --> REDHAT_CONFIG
    GLOBAL_PARAMS --> UBUNTU_CONFIG
    VARS --> COMPUTED_VARS
    COMPUTED_VARS --> REDHAT_CONFIG
    COMPUTED_VARS --> UBUNTU_CONFIG
```

Sources: [defaults/main.yml:1-47](), [vars/main.yml:1-3]()

## Global Configuration Parameters

The global configuration parameters control role behavior across all operating systems and are defined in the defaults layer.

### Core Driver Parameters

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `nvidia_driver_package_state` | `"present"` | Controls package installation state |
| `nvidia_driver_package_version` | `""` | Specific version constraint (empty = latest) |
| `nvidia_driver_branch` | `"515"` | Driver branch/series to install |
| `nvidia_driver_skip_reboot` | `no` | Whether to skip automatic reboots |

### Service and Module Configuration

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `nvidia_driver_persistence_mode_on` | `yes` | Enable nvidia-persistenced service |
| `nvidia_driver_module_file` | `"/etc/modprobe.d/nvidia.conf"` | Kernel module configuration file |
| `nvidia_driver_module_params` | `""` | Additional kernel module parameters |
| `nvidia_driver_add_repos` | `yes` | Whether to add NVIDIA repositories |

Sources: [defaults/main.yml:1-9](), [README.md:26-34]()

## OS-Specific Configuration Systems

The role implements specialized configuration branches for RedHat and Ubuntu families, each with distinct repository management and package selection strategies.

### RedHat Family Configuration

```mermaid
graph LR
    subgraph "RedHat_Config[RedHat Configuration System]"
        EPEL_CONFIG["EPEL Repository<br/>epel_package<br/>epel_repo_key"]
        CUDA_REPO_CONFIG["CUDA Repository<br/>nvidia_driver_rhel_cuda_repo_baseurl<br/>nvidia_driver_rhel_cuda_repo_gpgkey"]
        BRANCH_CONFIG["Branch Configuration<br/>nvidia_driver_rhel_branch"]
    end
    
    subgraph "Runtime_Vars[Runtime Variables]"
        RHEL_DIR["_rhel_repo_dir<br/>rhel{major_version}/{arch}"]
    end
    
    RHEL_DIR --> CUDA_REPO_CONFIG
    BRANCH_CONFIG --> EPEL_CONFIG
```

The RedHat configuration system manages EPEL repository installation and NVIDIA CUDA repository setup:

- **EPEL Repository**: [defaults/main.yml:14-15]() defines `epel_package` and `epel_repo_key` with version-specific URLs using `ansible_distribution_major_version`.
- **CUDA Repository**: [defaults/main.yml:16-17]() configures `nvidia_driver_rhel_cuda_repo_baseurl` and `nvidia_driver_rhel_cuda_repo_gpgkey`.
- **Branch Inheritance**: [defaults/main.yml:19]() sets `nvidia_driver_rhel_branch` from global `nvidia_driver_branch`.

### Ubuntu Configuration System

```mermaid
graph TB
    subgraph "Ubuntu_Branch_Decision[Ubuntu Installation Path Decision]"
        INSTALL_FROM_CUDA["nvidia_driver_ubuntu_install_from_cuda_repo"]
    end
    
    subgraph "Canonical_Path[Canonical Repository Path]"
        UBUNTU_PACKAGES["nvidia_driver_ubuntu_packages<br/>• nvidia-headless-{branch}{suffix}<br/>• nvidia-utils-{branch}{suffix}<br/>• nvidia-headless-no-dkms-{branch}{suffix}<br/>• nvidia-kernel-source-{branch}{suffix}"]
        PACKAGES_SUFFIX["nvidia_driver_ubuntu_packages_suffix<br/>-server"]
    end
    
    subgraph "CUDA_Path[CUDA Repository Path]"
        CUDA_KEYRING["nvidia_driver_ubuntu_cuda_keyring_url"]
        CUDA_PACKAGE["nvidia_driver_ubuntu_cuda_package<br/>cuda-drivers-{branch}"]
        OLD_KEY_REMOVAL["old_nvidia_driver_ubuntu_cuda_repo_gpgkey_id<br/>7fa2af80"]
    end
    
    INSTALL_FROM_CUDA -->|"no"| Canonical_Path
    INSTALL_FROM_CUDA -->|"yes"| CUDA_Path
    PACKAGES_SUFFIX --> UBUNTU_PACKAGES
```

The Ubuntu configuration provides two distinct installation paths:

**Canonical Repository Path** [defaults/main.yml:32-39]():
- `nvidia_driver_ubuntu_packages_suffix`: Controls server vs desktop packages (defaults to `"-server"`).
- `nvidia_driver_ubuntu_packages`: Array of specific package names with branch/suffix interpolation.

**CUDA Repository Path** [defaults/main.yml:42-46]():
- `nvidia_driver_ubuntu_cuda_keyring_url`: Keyring package URL for repository authentication.
- `nvidia_driver_ubuntu_cuda_package`: Single meta-package for driver installation (`cuda-drivers-{{ nvidia_driver_ubuntu_branch }}`).
- `old_nvidia_driver_ubuntu_cuda_repo_gpgkey_id`: Legacy key ID (`7fa2af80`) for cleanup.

Sources: [defaults/main.yml:22-47](), [README.md:45-56]()

## Variable Inheritance and Resolution

The configuration system implements a resolution mechanism that combines static defaults with runtime-computed values.

### Runtime Variable Computation

```mermaid
graph LR
    subgraph "Ansible_Facts[Ansible System Facts]"
        DISTRO["ansible_distribution<br/>Ubuntu, CentOS, etc."]
        VERSION["ansible_distribution_version<br/>20.04, 8, etc."]
        MAJOR_VERSION["ansible_distribution_major_version<br/>20, 8, etc."]
        ARCH["ansible_architecture<br/>x86_64, aarch64, etc."]
    end
    
    subgraph "Computed_Variables[Computed Repository Paths]"
        UBUNTU_DIR["_ubuntu_repo_dir<br/>ubuntu2004/x86_64"]
        RHEL_DIR["_rhel_repo_dir<br/>rhel8/x86_64"]
    end
    
    DISTRO --> UBUNTU_DIR
    VERSION --> UBUNTU_DIR
    ARCH --> UBUNTU_DIR
    MAJOR_VERSION --> RHEL_DIR
    ARCH --> RHEL_DIR
```

The [vars/main.yml:1-2]() file computes repository directory paths using Ansible facts:

- `_ubuntu_repo_dir`: Combines lowercase distribution name, version (dots removed), and architecture (normalizing `aarch64` to `sbsa`).
- `_rhel_repo_dir`: Combines "rhel" prefix, major version, and architecture (normalizing `aarch64` to `sbsa`).

### Configuration Precedence Chain

```mermaid
graph TD
    PLAYBOOK_VARS["Playbook Variables<br/>Highest Priority"]
    HOST_GROUP_VARS["Host/Group Variables"]
    ROLE_VARS["Role vars/main.yml<br/>_ubuntu_repo_dir<br/>_rhel_repo_dir"]
    ROLE_DEFAULTS["Role defaults/main.yml<br/>All configuration parameters"]
    ANSIBLE_FACTS["Ansible Facts<br/>Lowest Priority"]
    
    PLAYBOOK_VARS --> HOST_GROUP_VARS
    HOST_GROUP_VARS --> ROLE_VARS  
    ROLE_VARS --> ROLE_DEFAULTS
    ROLE_DEFAULTS --> ANSIBLE_FACTS
```

Variable resolution follows Ansible's standard precedence rules, allowing users to override any default configuration at the playbook or inventory level.

Sources: [vars/main.yml:1-3](), [defaults/main.yml:1-47]()

## Configuration Validation and Dependencies

The configuration system includes implicit validation through variable dependencies and conditional logic.

### Inter-Variable Dependencies

| Primary Variable | Dependent Variables | Relationship |
|------------------|-------------------|--------------|
| `nvidia_driver_branch` | `nvidia_driver_rhel_branch`, `nvidia_driver_ubuntu_branch` | Branch inheritance |
| `nvidia_driver_ubuntu_branch` | `nvidia_driver_ubuntu_packages`, `nvidia_driver_ubuntu_cuda_package` | Package name interpolation |
| `_ubuntu_repo_dir`, `_rhel_repo_dir` | Repository URL construction | Path component injection |
| `nvidia_driver_ubuntu_install_from_cuda_repo` | Installation task selection | Conditional execution control |

### Configuration Constraints

The configuration system enforces several implicit constraints:

- **Branch Format**: Must be numeric string (e.g., `"515"`) for package name interpolation [defaults/main.yml:34]().
- **Persistence Mode**: Controlled via `nvidia_driver_persistence_mode_on` [defaults/main.yml:3](), implemented using a systemd override [files/nvidia-persistenced-override.conf:1-4]().
- **Package Version**: If `nvidia_driver_package_version` is provided, it must match the specific version of the deb or RPM package [README.md:29]().

Sources: [defaults/main.yml:1-47](), [vars/main.yml:1-3](), [files/nvidia-persistenced-override.conf:1-4](), [README.md:26-56]()

---

