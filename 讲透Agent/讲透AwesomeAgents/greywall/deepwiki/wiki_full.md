# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [docs/index.md](docs/index.md)
- [docs/platform-support.md](docs/platform-support.md)
- [docs/why-greywall.md](docs/why-greywall.md)
- [install.sh](install.sh)

</details>



## Purpose and Scope

This page introduces greywall, a deny-by-default sandbox for running untrusted commands—specifically AI coding agents—with strict filesystem and network restrictions. It covers:

- What greywall is and its security model.
- High-level architecture and core components.
- Platform-specific implementations (Linux vs. macOS).
- Data flow from command execution to sandbox enforcement.

For installation and basic usage, see **Getting Started**. For detailed security concepts, see **Core Concepts**.

---

## What is Greywall

Greywall is a container-free sandboxing tool that wraps arbitrary commands in a deny-by-default security envelope. It restricts filesystem access, network connections, and system calls to only what is explicitly allowed. It is designed to prevent AI agents (like Claude Code, Cursor, or Aider) from accessing sensitive data like SSH keys, environment secrets, or system configuration files outside the working directory [README.md:9-11]().

**Key characteristics:**

| Aspect | Description |
|--------|-------------|
| **Security model** | Deny-by-default for filesystem reads/writes and network access [README.md:19-20](). |
| **Interfaces** | Command-line tool (`greywall`) and Go library API (`pkg/greywall`) [ARCHITECTURE.md:58-59](). |
| **Platform support** | Linux (bubblewrap + Landlock + seccomp) and macOS (sandbox-exec + Seatbelt) [docs/platform-support.md:12-29](). |
| **Network isolation** | Transparent proxying through `greyproxy` with domain-based filtering [README.md:11-11](). |
| **Learning mode** | Auto-generates least-privilege profiles by tracing command execution [README.md:23-23](). |

**Sources:** [README.md:1-26](), [ARCHITECTURE.md:1-9](), [docs/platform-support.md:1-30]()

---

## Security Model

Greywall implements a defense-in-depth approach by combining OS-level sandboxing with external network filtering.

### The Two-Layer Isolation Model

```mermaid
graph TB
    subgraph "Layer 1: OS Sandbox (Internal)"
        A["Process Isolation<br/>(Namespaces / Seatbelt)"]
        B["Filesystem Restrictions<br/>(Landlock / Mounts)"]
        C["Syscall Filtering<br/>(Seccomp / BPF)"]
    end
    
    subgraph "Layer 2: Network Filtering (External)"
        D["greyproxy Service"]
        E["Domain-based Allow/Deny"]
        F["Live Dashboard"]
    end
    
    G["User Command"] --> A
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> H["Internet"]
    
    E -.blocked.-> I["Denied Access"]
```
**Diagram 1: Two-Layer Security Architecture**

### Deny-by-Default Principles

*   **Filesystem**: Only the current working directory is accessible by default. Access to sensitive paths like `~/.ssh` or `.env` files is explicitly denied even if they are within allowed parent directories [README.md:19-19](), [README.md:192-198]().
*   **Network**: All outbound traffic is blocked or routed through `greyproxy`. On Linux, this is enforced via network namespaces (`unshare-net`) [ARCHITECTURE.md:164-165]().
*   **Command Blocking**: Dangerous commands (e.g., `rm -rf /`, `git push --force`) are intercepted and blocked before the sandbox is even initialized [README.md:21-21](), [ARCHITECTURE.md:112-120]().
*   **Environment Sanitization**: Dangerous variables like `LD_PRELOAD` or `DYLD_INSERT_LIBRARIES` are stripped to prevent library injection attacks [ARCHITECTURE.md:121-128]().

**Sources:** [README.md:17-26](), [ARCHITECTURE.md:3-8](), [ARCHITECTURE.md:112-128]()

---

## Architecture Overview

Greywall is structured to abstract platform-specific complexities behind a unified `Manager` interface.

```mermaid
graph TB
    CLI["greywall CLI<br/>cmd/greywall/"]
    LIB["Go Library API<br/>pkg/greywall/"]
    
    MGR["Manager<br/>internal/sandbox/manager.go"]
    CFG["Config System<br/>internal/config/"]
    PROF["Profile System<br/>internal/profiles/"]
    
    PLAT["Platform Detection<br/>internal/platform/"]
    
    LINUX["Linux Implementation<br/>internal/sandbox/linux.go"]
    MACOS["macOS Implementation<br/>internal/sandbox/macos.go"]
    
    BWRAP["bubblewrap<br/>(bwrap)"]
    SEATBELT["sandbox-exec<br/>(Seatbelt)"]
    
    GP["greyproxy Service<br/>(SOCKS5/DNS)"]
    
    CLI --> MGR
    LIB --> MGR
    
    MGR --> CFG
    MGR --> PROF
    MGR --> PLAT
    
    PLAT --> LINUX
    PLAT --> MACOS
    
    LINUX --> BWRAP
    MACOS --> SEATBELT
    
    LINUX --> GP
    MACOS --> GP
```
**Diagram 2: System Architecture and Code Entities**

### Core Components

1.  **CLI Entry Point**: The `cmd/greywall` directory contains the main application logic, handling flags like `--learning`, `--profile`, and `-m` (monitor) [README.md:93-127]().
2.  **Manager (`internal/sandbox/manager.go`)**: Orchestrates the sandbox lifecycle, including bridge setup, command wrapping, and cleanup [ARCHITECTURE.md:102-110]().
3.  **Config (`internal/config/`)**: Handles loading `greywall.json` and merging it with built-in agent profiles [ARCHITECTURE.md:64-80]().
4.  **Platform (`internal/platform/`)**: Detects the host OS to select the appropriate sandbox engine [ARCHITECTURE.md:81-88]().
5.  **Proxy (`internal/proxy/`)**: Manages the `greyproxy` lifecycle, ensuring the proxy is installed and running before the sandbox starts [ARCHITECTURE.md:90-98]().

**Sources:** [ARCHITECTURE.md:33-60](), [ARCHITECTURE.md:64-110]()

---

## Platform Implementations

Greywall uses native kernel features for zero-overhead isolation without requiring Docker or VMs.

### Linux Implementation
The Linux implementation relies on `bubblewrap` for namespace isolation and `Landlock` for fine-grained filesystem access control [ARCHITECTURE.md:162-165]().

*   **Networking**: Uses `unshare-net` to create a private network namespace. A `tun2socks` instance inside the sandbox routes traffic through a `socat` bridge to the host's `greyproxy` [ARCHITECTURE.md:166-189]().
*   **Filesystem**: Combines `bubblewrap` bind-mounts with `Landlock` (Linux 5.13+) to restrict file operations independently of the mount rules [docs/platform-support.md:33-37]().
*   **Security Layers**: Includes Seccomp BPF for syscall filtering and eBPF for real-time violation monitoring [README.md:24-24]().

### macOS Implementation
The macOS implementation uses Apple's `sandbox-exec` with dynamically generated Seatbelt profiles [ARCHITECTURE.md:130-133]().

*   **Networking**: Redirection is achieved via environment variables (`HTTP_PROXY`, `ALL_PROXY`). It does not support full transparent capture like the Linux TUN device [docs/platform-support.md:49-50]().
*   **Monitoring**: Uses the Endpoint Security framework via `eslogger` to trace filesystem access for learning mode [docs/platform-support.md:52-53]().

### Feature Comparison

| Feature | Linux | macOS |
|---------|:-----:|:-----:|
| **Sandbox Engine** | `bubblewrap` | `sandbox-exec` |
| **Filesystem Control** | Landlock + Bwrap | Seatbelt |
| **Syscall Filtering** | Seccomp BPF | Seatbelt |
| **Transparent Proxy** | ✅ (TUN/tun2socks) | ❌ (Env vars) |
| **Violation Monitoring** | ✅ (eBPF) | ✅ (Unified Log) |

**Sources:** [ARCHITECTURE.md:130-189](), [docs/platform-support.md:10-29]()

---

## Data Flow: Command Execution

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as greywall CLI
    participant MGR as Manager
    participant GP as greyproxy
    participant SB as OS Sandbox (bwrap/Seatbelt)

    U->>CLI: greywall -- curl example.com
    CLI->>MGR: Initialize()
    MGR->>GP: Ensure running
    CLI->>MGR: WrapCommand("curl example.com")
    MGR->>SB: Generate sandbox arguments
    SB-->>MGR: Sandboxed command string
    CLI->>SB: Execute sandboxed process
    SB->>GP: Network traffic (via bridge/env)
    GP-->>SB: Filtered Response
    SB-->>U: Output / Result
```
**Diagram 3: Command Lifecycle and Data Flow**

1.  **Initialization**: The `Manager` checks for `greyproxy` and sets up Unix socket bridges if on Linux [ARCHITECTURE.md:106-107]().
2.  **Wrapping**: The command is transformed into a platform-specific invocation (e.g., `bwrap ... -- curl` or `sandbox-exec -p ... curl`) [ARCHITECTURE.md:109-110]().
3.  **Execution**: The sandboxed process runs. On Linux, traffic is captured by a TUN device and sent to the proxy bridge [ARCHITECTURE.md:187-189]().
4.  **Monitoring**: If `-m` is passed, the `Manager` starts a background monitor to report violations from eBPF or macOS logs [ARCHITECTURE.md:49-52]().

**Sources:** [ARCHITECTURE.md:1-31](), [ARCHITECTURE.md:102-110](), [ARCHITECTURE.md:166-189]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/quickstart.md](docs/quickstart.md)
- [install.sh](install.sh)
- [internal/proxy/detect.go](internal/proxy/detect.go)
- [internal/proxy/install.go](internal/proxy/install.go)
- [internal/proxy/start.go](internal/proxy/start.go)
- [internal/sandbox/color.go](internal/sandbox/color.go)
- [internal/sandbox/linux_features_stub.go](internal/sandbox/linux_features_stub.go)

</details>



This page provides an overview of installing greywall, verifying the installation, and running your first sandboxed commands. For detailed installation instructions, see [Installation](#2.1). For comprehensive command examples and patterns, see [Quick Start Guide](#2.2).

## Prerequisites and Dependencies

Greywall requires platform-specific dependencies:

| Platform | Required Dependencies | Optional |
|----------|----------------------|----------|
| **macOS** | None (uses built-in `sandbox-exec`) | - |
| **Linux** | `bubblewrap`, `socat` | `xdg-dbus-proxy`, `libsecret-tools`, `bpftrace` |

On macOS, greywall uses the system's `sandbox-exec` command with Seatbelt profiles [internal/sandbox/linux_features_stub.go:66-71](). On Linux, it uses `bubblewrap` for process isolation and `socat` for network bridge setup [README.md:84-87]().

**Sources:** [README.md:84-91](), [internal/sandbox/linux_features_stub.go:63-76](), [docs/quickstart.md:51-67]()

## Installation Overview

### Installation Flow

```mermaid
graph TB
    subgraph "Installation Methods"
        BREW["brew install greywall<br/>(macOS recommended)"]
        CURL["curl install.sh | sh<br/>(Linux/macOS)"]
        GO["go install<br/>(from source)"]
    end
    
    subgraph "Installation Process"
        DL["Download greywall binary"]
        VERIFY["Verify checksum"]
        INSTALL["Install to ~/.local/bin<br/>or /opt/homebrew/bin"]
    end
    
    subgraph "Post-Install"
        SETUP["greywall setup<br/>Install greyproxy"]
        GP_DL["internal/proxy/install.go<br/>Install()"]
        GP_DET["internal/proxy/detect.go<br/>Detect()"]
        CHECK["greywall check<br/>Verify dependencies"]
    end
    
    BREW --> INSTALL
    CURL --> DL
    GO --> DL
    
    DL --> VERIFY
    VERIFY --> INSTALL
    
    INSTALL --> SETUP
    SETUP --> GP_DL
    GP_DL --> GP_DET
    GP_DET --> CHECK
```

**Diagram: Installation and Setup Process**

Greywall provides several installation methods:

1. **Homebrew (macOS)**: Installs both greywall and greyproxy automatically [README.md:43-50]().
2. **install.sh script**: Handles platform detection [install.sh:12-19](), architecture mapping [install.sh:21-25](), version resolution [install.sh:28-37](), and checksum verification [install.sh:89-106](). It automatically invokes `greywall setup` [install.sh:119]().
3. **Go install**: Places the binary on your `$PATH`. Requires manual `greywall setup` afterwards [docs/quickstart.md:27-34]().

**Sources:** [README.md:41-82](), [install.sh:1-145](), [docs/quickstart.md:9-50]()

### Quick Install Commands

```bash
# Homebrew (macOS)
brew tap greyhavenhq/tap
brew install greywall

# Linux or macOS - uses install.sh script
curl -fsSL https://raw.githubusercontent.com/GreyhavenHQ/greywall/main/install.sh | sh

# Using Go install
go install github.com/GreyhavenHQ/greywall/cmd/greywall@latest
greywall setup
```

**Sources:** [README.md:41-65](), [docs/quickstart.md:9-32]()

## Verifying Installation

### System Check

After installation, verify that all components are working:

```bash
greywall check
```

This command verifies binary versions, platform-specific dependencies, and the status of `greyproxy` [README.md:122-123](). On macOS, it checks for `sandbox-exec` [internal/sandbox/linux_features_stub.go:66-71]().

**Sources:** [README.md:91](), [README.md:123](), [internal/sandbox/linux_features_stub.go:61-76]()

### greyproxy Service

Greywall requires the `greyproxy` service for network filtering. The `greywall setup` command handles installation and service startup [internal/proxy/install.go:87-153]().

- **Detection**: `internal/proxy/detect.go` checks if `greyproxy` is on the `PATH` [internal/proxy/detect.go:66-72]() and hits the health endpoint at `http://localhost:43080/api/health` [internal/proxy/detect.go:16]().
- **Startup**: `internal/proxy/start.go` runs `greyproxy service start` [internal/proxy/start.go:22]().

**Sources:** [internal/proxy/detect.go:1-127](), [internal/proxy/install.go:87-153](), [internal/proxy/start.go:1-31]()

## Your First Sandboxed Command

### Deny-by-Default Model

Greywall uses a deny-by-default model for both network and filesystem access [README.md:9]().

```bash
# Network access blocked (default behavior)
greywall -- curl https://example.com

# Filesystem access limited (default deny)
greywall -- cat ~/.ssh/id_rsa # → Permission denied
```

**Sources:** [README.md:9-11](), [README.md:98-99](), [docs/quickstart.md:104-115]()

### Basic Usage Examples

```bash
# Run with shell expansion
greywall -c "echo hello && ls"

# Route through a specific SOCKS5 proxy
greywall --proxy socks5://localhost:1080 -- npm install

# Expose a port for inbound connections
greywall -p 3000 -c "npm run dev"

# Monitor sandbox violations (e.g. blocked files/network)
greywall -m -- npm install
```

**Sources:** [README.md:97-115](), [docs/quickstart.md:119-174]()

## Working with Profiles

### Built-in Agent Profiles

Greywall ships with built-in profiles for agents like Claude Code, Cursor, and Aider [README.md:131-132](). On first run, it prompts to apply recommended rules [README.md:133-148]().

```bash
# Combine agent and toolchain profiles
greywall --profile claude,python -- claude

# List all available profiles
greywall profiles list
```

**Sources:** [README.md:129-161]()

### Learning Mode

Learning mode traces a command's filesystem access to generate a least-privilege profile automatically [README.md:23]().

```bash
# Trace file access via strace (Linux) or eslogger (macOS)
greywall --learning -- opencode

# Show the generated profile
greywall profiles show opencode
```

**Sources:** [README.md:163-179]()

## Configuration

Greywall reads from `~/.config/greywall/greywall.json` (Linux) or `~/Library/Application Support/greywall/greywall.json` (macOS) [README.md:183-184]().

```jsonc
{
  "network": {
    "proxyUrl": "socks5://localhost:43052"
  },
  "filesystem": {
    "allowRead": ["~/.config/myapp"],
    "allowWrite": ["."]
  }
}
```

**Sources:** [README.md:181-206]()

## Next Steps

- **[Installation](#2.1)** — Detailed setup instructions for all platforms.
- **[Quick Start Guide](#2.2)** — Common usage patterns and agent examples.
- **[CLI Reference](#2.3)** — Full list of commands and flags.

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yaml](.goreleaser.yaml)
- [README.md](README.md)
- [install.sh](install.sh)
- [internal/proxy/brew.go](internal/proxy/brew.go)
- [internal/proxy/detect.go](internal/proxy/detect.go)
- [internal/proxy/install.go](internal/proxy/install.go)
- [internal/proxy/start.go](internal/proxy/start.go)
- [internal/sandbox/color.go](internal/sandbox/color.go)
- [internal/sandbox/linux_features_stub.go](internal/sandbox/linux_features_stub.go)

</details>



This page provides detailed instructions for installing greywall on Linux and macOS systems. Installation involves two components: the `greywall` binary itself and the `greyproxy` network filtering service.

---

## Installation Methods Overview

Greywall supports multiple installation methods depending on your platform and preferences. All methods ultimately install the `greywall` binary and then set up `greyproxy` as a dependency.

```mermaid
graph TB
    subgraph "Installation Entry Points"
        BREW["Homebrew<br/>brew install greywall"]
        INSTALLSH["install.sh Script<br/>curl | sh"]
        GOINSTALL["Go Install<br/>go install"]
        SOURCE["Build from Source<br/>make build"]
    end
    
    subgraph "Binary Installation"
        LOCALBIN["~/.local/bin/greywall"]
        BREWBIN["/opt/homebrew/bin/greywall<br/>(macOS ARM)"]
    end
    
    subgraph "Dependency Setup"
        SETUP["greywall setup<br/>cmd/greywall/main.go"]
        DETECT["proxy.Detect()<br/>internal/proxy/detect.go"]
        INSTALL["proxy.Install()<br/>internal/proxy/install.go"]
        GREYPROXY["greyproxy binary<br/>~/.local/bin/greyproxy"]
    end
    
    subgraph "Verification"
        CHECK["greywall check<br/>cmd/greywall/main.go"]
        HEALTH["Health Check<br/>GET localhost:43080/api/health"]
    end
    
    BREW --> BREWBIN
    INSTALLSH --> LOCALBIN
    GOINSTALL --> LOCALBIN
    SOURCE --> LOCALBIN
    
    BREWBIN --> SETUP
    LOCALBIN --> SETUP
    
    SETUP --> DETECT
    DETECT --> INSTALL
    INSTALL --> GREYPROXY
    
    GREYPROXY --> CHECK
    CHECK --> HEALTH
```

**Sources:** [README.md:41-82](), [install.sh:1-145](), [internal/proxy/install.go:87-153](), [internal/proxy/detect.go:43-63]()

---

## Platform Requirements

### Linux Requirements

| Component | Purpose | Detection |
|-----------|---------|-----------|
| `bubblewrap` | Container-free sandboxing, namespace isolation | `exec.LookPath("bwrap")` |
| `socat` | Network bridge relay between sandbox and greyproxy | `exec.LookPath("socat")` |
| `tun2socks` | Transparent proxying (optional/Linux) | `internal/sandbox/linux_features_stub.go:26` |
| Kernel ≥ 5.13 | Landlock LSM support (ABI v1) | `internal/sandbox/linux_features_stub.go:18-19` |

**Linux Distribution Installation:**

```bash
# Debian/Ubuntu
sudo apt install bubblewrap socat

# Fedora/RHEL
sudo dnf install bubblewrap socat
```

### macOS Requirements

macOS uses the built-in `sandbox-exec` (Seatbelt) facility.

| Component | Availability |
|-----------|--------------|
| `sandbox-exec` | Built-in on all macOS versions [internal/sandbox/linux_features_stub.go:66]() |
| `eslogger` (learning mode) | Requires `sudo` for system event monitoring |

**Sources:** [README.md:84-91](), [internal/sandbox/linux_features_stub.go:11-76]()

---

## Homebrew Installation (macOS)

The recommended installation method for macOS. This automatically handles `greyproxy` as a dependency.

```bash
brew tap greyhavenhq/tap
brew install greywall
```

The Homebrew formula ([.goreleaser.yaml:87-109]()) performs the following:
- Installs the `greywall` binary.
- Removes the macOS quarantine attribute (`com.apple.quarantine`) from the binary [.goreleaser.yaml:102]().
- Declares a dependency on the `greyproxy` cask [.goreleaser.yaml:105]().

**Sources:** [README.md:43-50](), [.goreleaser.yaml:87-109]()

---

## install.sh Script Installation

The `install.sh` script provides a cross-platform way to download pre-built binaries.

### Script Workflow

```mermaid
sequenceDiagram
    participant User
    participant InstallScript as "install.sh"
    participant GitHub as "GitHub Releases API"
    participant FileSystem as "~/.local/bin"
    participant GreywallBinary as "greywall binary"
    
    User->>InstallScript: curl | sh
    InstallScript->>InstallScript: Detect OS/ARCH<br/>install.sh:12-25
    InstallScript->>GitHub: Fetch latest release tag<br/>install.sh:30
    GitHub-->>InstallScript: v0.x.y
    InstallScript->>InstallScript: Build download URL<br/>install.sh:42
    InstallScript->>GitHub: Download archive + checksums
    InstallScript->>InstallScript: Verify SHA256<br/>install.sh:98-106
    InstallScript->>FileSystem: Extract to ~/.local/bin<br/>install.sh:108-113
    InstallScript->>GreywallBinary: Execute greywall setup<br/>install.sh:119
    GreywallBinary-->>User: greyproxy installed & service started
```

### Script Behavior

1. **Platform Detection** ([install.sh:12-25]()): Detects OS (`uname -s`) and Architecture (`uname -m`). Supports `Linux` and `Darwin` (macOS).
2. **Version Resolution** ([install.sh:28-33]()): Defaults to the latest GitHub release unless `GREYWALL_VERSION` is provided.
3. **Checksum Verification** ([install.sh:89-106]()): Downloads `checksums.txt` from the release and verifies the archive using `sha256sum` or `shasum`.
4. **Post-Install Setup** ([install.sh:119]()): Automatically executes `greywall setup` to ensure `greyproxy` is available.

**Sources:** [install.sh:1-145](), [README.md:52-56]()

---

## Alternative Installation Methods

### Go Install
```bash
go install github.com/GreyhavenHQ/greywall/cmd/greywall@latest
```
*Note: You must run `greywall setup` manually after this.*

### Build from Source
```bash
git clone https://github.com/GreyhavenHQ/greywall
cd greywall
make setup && make build
```
This uses the build configuration defined in [.goreleaser.yaml:7-22](), setting `CGO_ENABLED=0` and embedding version information via `ldflags`.

**Sources:** [README.md:61-80](), [.goreleaser.yaml:7-22]()

---

## greyproxy Setup

The `greywall setup` command (implemented via `internal/proxy/install.go`) manages the lifecycle of the `greyproxy` dependency.

### Setup Workflow

```mermaid
graph TB
    subgraph "Setup Execution"
        CMD["greywall setup"]
        DETECT["proxy.Detect()<br/>internal/proxy/detect.go"]
        INSTALL["proxy.Install()<br/>internal/proxy/install.go"]
    end
    
    subgraph "Logic: internal/proxy/install.go"
        FETCH["fetchLatestRelease()<br/>GitHub API"]
        RESOLVE["resolveAssetURL()<br/>Match OS/Arch"]
        DL["downloadAsset()<br/>Temp File"]
        EXTRACT["extractTarGz()"]
        RUNINST["runGreyproxyInstall()<br/>'greyproxy install'"]
    end

    CMD --> DETECT
    DETECT -->|"Not Installed / Outdated"| INSTALL
    INSTALL --> FETCH
    FETCH --> RESOLVE
    RESOLVE --> DL
    DL --> EXTRACT
    EXTRACT --> RUNINST
```

### Key Implementation Details

- **Detection**: `proxy.Detect()` [internal/proxy/detect.go:43-63]() checks if `greyproxy` is on the PATH and queries `http://localhost:43080/api/health` to see if it is already running.
- **Version Comparison**: `proxy.IsOlderVersion()` [internal/proxy/install.go:56-83]() compares semver strings to determine if an update is required.
- **Asset Matching**: `resolveAssetURL()` [internal/proxy/install.go:189-202]() constructs the expected filename based on `runtime.GOOS` and `runtime.GOARCH` (e.g., `greyproxy_0.1.0_linux_amd64.tar.gz`).
- **Service Management**: After extraction, `runGreyproxyInstall()` [internal/proxy/install.go:299-304]() executes the binary's own install command to register it as a system service (systemd/launchd).

**Sources:** [internal/proxy/install.go:1-305](), [internal/proxy/detect.go:1-127](), [internal/proxy/start.go:1-31]()

---

## Verification

Run `greywall check` [README.md:123]() to verify the installation status.

### Dependency Status Logic
On macOS, it checks for `sandbox-exec` [internal/sandbox/linux_features_stub.go:66](). On Linux, it checks for `bubblewrap`, `socat`, and kernel capabilities like Landlock [internal/sandbox/linux_features_stub.go:11-29]().

### Colorized Output
The CLI uses `internal/sandbox/color.go` to provide visual feedback:
- `CheckOK()`: Green checkmark for satisfied requirements [internal/sandbox/color.go:23-29]().
- `CheckFail()`: Red cross for missing dependencies [internal/sandbox/color.go:31-36]().

**Sources:** [README.md:91](), [internal/sandbox/linux_features_stub.go:62-76](), [internal/sandbox/color.go:1-37]()

---

# Page: Quick Start Guide

# Quick Start Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cmd/greywall/main.go](cmd/greywall/main.go)
- [docs/quickstart.md](docs/quickstart.md)
- [install.sh](install.sh)

</details>



This guide provides hands-on examples to get you started with greywall. You'll learn how to run sandboxed commands, work with profiles, and use learning mode to automatically generate security policies. For detailed CLI flag documentation, see [CLI Reference](#2.3). For configuration file format, see [Configuration Files](#6.1).

## Prerequisites and Verification

Before running sandboxed commands, verify your installation and dependencies:

```bash
greywall check
```

This command checks:
- greywall installation and version [cmd/greywall/main.go:149]()
- Platform-specific dependencies (bubblewrap and socat on Linux) [README.md:84-91]()
- Security feature availability (Landlock, seccomp, eBPF) [README.md:116-118]()
- greyproxy installation and running status [README.md:122-123]()

If greyproxy is not installed, run:

```bash
greywall setup
```

The setup command downloads and installs greyproxy, which provides the network proxy and domain filtering infrastructure [README.md:125-127](). After installation, greyproxy runs as a persistent background service.

**Verification Flow:**

```mermaid
flowchart TD
    Start["greywall check"] --> CheckVersion["Check greywall version<br/>(cmd/greywall/main.go:520-524)"]
    CheckVersion --> CheckDeps["sandbox.PrintDependencyStatus()<br/>Platform dependencies"]
    CheckDeps --> CheckProxy["proxy.Detect()<br/>Check greyproxy status"]
    
    CheckProxy --> IsInstalled{Installed?}
    IsInstalled -->|No| ShowInstallSteps["Display: greywall setup"]
    IsInstalled -->|Yes| CheckRunning{Running?}
    
    CheckRunning -->|No| ShowStartSteps["Display: greywall setup"]
    CheckRunning -->|Yes| CheckVersion2["proxy.CheckLatestVersion()"]
    
    CheckVersion2 --> IsUpToDate{Up to date?}
    IsUpToDate -->|No| ShowUpgrade["Display upgrade hint"]
    IsUpToDate -->|Yes| AllGood["All checks passed"]
    
    ShowInstallSteps --> End["Exit"]
    ShowStartSteps --> End
    ShowUpgrade --> End
    AllGood --> End
```

Sources: [cmd/greywall/main.go:520-585](), [cmd/greywall/main.go:149]()

## Your First Sandboxed Command

### Default Behavior: Network Blocked

By default, greywall denies all network access and restricts filesystem access to the current directory [README.md:19-20]():

```bash
greywall -- curl https://example.com
```

This command will fail because network access is blocked by default unless routed through a proxy [README.md:98-99](). Open the greyproxy dashboard to allow the domain:

```bash
# Dashboard URL (shown by greywall check)
http://localhost:43080
```

In the dashboard, add `example.com` to the allowlist, then retry the command.

### Using Shell Expansion

The `-c` flag runs commands with shell expansion, similar to `sh -c` [cmd/greywall/main.go:123]():

```bash
greywall -c "echo hello && ls"
```

This is useful for pipelines, variable substitution, and other shell features [README.md:101-102]().

**Command Execution Modes:**

| Syntax | Usage | Example | Shell Expansion |
|--------|-------|---------|-----------------|
| `greywall -- <args>` | Direct execution | `greywall -- curl https://example.com` | No |
| `greywall -c "<command>"` | Shell execution | `greywall -c "echo $HOME"` | Yes |

Sources: [cmd/greywall/main.go:123](), [README.md:98-102]()

### Enabling Debug Output

Enable debug logging to see sandbox configuration and execution details [cmd/greywall/main.go:117]():

```bash
greywall -d -- curl https://example.com
```

Debug output shows:
- Loaded configuration and profile resolution
- Sandbox implementation details (bubblewrap args, Seatbelt profile)
- Network proxy configuration
- Stripped environment variables

Sources: [cmd/greywall/main.go:117](), [README.md:110-111]()

## Basic Usage Patterns

### Port Exposure for Development Servers

Expose ports for inbound connections (e.g., running a web server inside the sandbox) [cmd/greywall/main.go:124]():

```bash
greywall -p 3000 -c "npm run dev"
```

Multiple ports can be exposed [cmd/greywall/main.go:124]():

```bash
greywall -p 3000 -p 5173 -- vite
```

On Linux, this creates a reverse SOCKS5 bridge that forwards connections from the host to the sandboxed network namespace. On macOS, it configures the Seatbelt profile to allow binding to the specified ports [cmd/greywall/main.go:81-90]().

Sources: [cmd/greywall/main.go:124](), [README.md:107-108]()

### Monitoring Sandbox Violations

The `-m` flag enables real-time monitoring of sandbox violations [cmd/greywall/main.go:118]():

```bash
greywall -m -- npm install
```

On Linux, this starts an eBPF monitor that traces blocked filesystem operations and syscalls. On macOS, it monitors the unified log for Seatbelt denial messages [README.md:24](). Violations are printed to stderr as they occur.

Sources: [cmd/greywall/main.go:118](), [README.md:113-114]()

### Custom Configuration Files

Override the default configuration file location [cmd/greywall/main.go:119]():

```bash
greywall --settings ./myconfig.json -- <command>
```

The configuration file supports:
- Network proxy settings (`network.proxyUrl`, `network.dnsAddr`)
- Filesystem access rules (`filesystem.allowRead`, `filesystem.denyWrite`)
- Command deny patterns (`command.deny`)

Sources: [cmd/greywall/main.go:119](), [README.md:185-204]()

## Working with Profiles

### Auto-Detection and First-Run Experience

When running a known command without a profile, greywall offers to apply its built-in profile [README.md:131-136]():

```bash
greywall -- claude
```

This triggers the first-run UX, showing what the profile allows and offering options [README.md:138-148]():
- **[Y]** Use profile (saves for future runs)
- **[e]** Edit first
- **[s]** Skip (use restrictive defaults)
- **[n]** Don't ask again

The profile is saved to the local configuration directory.

**Profile Resolution Flow:**

```mermaid
flowchart TD
    Start["runCommand()"] --> ExtractCmd["Extract base command name"]
    ExtractCmd --> LearningCheck{learning mode?}
    
    LearningCheck -->|Yes| SkipProfiles["Skip profile loading"]
    LearningCheck -->|No| HasProfile{--profile flag?}
    
    HasProfile -->|Yes| ExplicitResolve["resolveProfile(name)<br/>For each comma-separated name"]
    HasProfile -->|No| AutoDetect["Check saved profile"]
    
    ExplicitResolve --> TrySaved["config.Load(savedPath)"]
    TrySaved --> SavedExists{Exists?}
    SavedExists -->|Yes| MergeSaved["config.Merge(cfg, savedCfg)"]
    SavedExists -->|No| TryBuiltin["profiles.GetAgentProfile(canonical)"]
    
    TryBuiltin --> BuiltinExists{Exists?}
    BuiltinExists -->|Yes| MergeBuiltin["config.Merge(cfg, profile)"]
    BuiltinExists -->|No| ProfileError["Return error"]
    
    AutoDetect --> CheckSaved{Saved profile exists?}
    CheckSaved -->|Yes| MergeSaved
    CheckSaved -->|No| CheckAutoProfile{--auto-profile?}
    
    CheckAutoProfile -->|Yes| ApplyBuiltin["Auto-apply built-in"]
    CheckAutoProfile -->|No| FirstRun["ResolveFirstRun(cmdName)<br/>Interactive prompt"]
    
    FirstRun --> UserChoice{User choice}
    UserChoice -->|Use| SaveAndMerge["Save and Merge"]
    UserChoice -->|Skip| UseDefaults["Use default config"]
    UserChoice -->|Edit| OpenEditor["Open in $EDITOR"]
    
    MergeSaved --> ApplyCLI["Apply CLI overrides:<br/>--proxy, --dns"]
    MergeBuiltin --> ApplyCLI
    ApplyBuiltin --> ApplyCLI
    SaveAndMerge --> ApplyCLI
    UseDefaults --> ApplyCLI
    OpenEditor --> ApplyCLI
    SkipProfiles --> ApplyCLI
    
    ApplyCLI --> SetDefaults["Set greyproxy defaults"]
    SetDefaults --> InitManager["manager.Initialize()"]
```

Sources: [cmd/greywall/main.go:129](), [README.md:131-161]()

### Explicit Profile Loading

Load specific profiles by name [cmd/greywall/main.go:129]():

```bash
greywall --profile claude -- claude
```

Combine multiple profiles (agent + toolchains) [README.md:150-158]():

```bash
greywall --profile claude,python,node -- claude
```

Profiles are merged in order. Built-in profiles include AI Agents (claude, cursor, aider, etc.) and Toolchains (python, node, go, etc.) [README.md:131]().

Sources: [cmd/greywall/main.go:129](), [README.md:131-161]()

### Listing and Inspecting Profiles

List all available profiles (saved and built-in) [cmd/greywall/main.go:148]():

```bash
greywall profiles list
```

Show the contents of a specific profile [README.md:175]():

```bash
greywall profiles show opencode
```

Sources: [cmd/greywall/main.go:148](), [README.md:160-176]()

## Learning Mode Workflow

Learning mode traces a command's filesystem access and auto-generates a profile [cmd/greywall/main.go:128]():

### Step 1: Run in Learning Mode

```bash
greywall --learning -- opencode
```

**What happens:**
1. Command runs with relaxed filesystem sandbox [README.md:168-169]()
2. On Linux: `strace` traces system calls [README.md:168]()
3. On macOS: `eslogger` traces filesystem events [README.md:23]()
4. Trace data collected for analysis

**Warning:** Learning mode relaxes filesystem restrictions. Only use with trusted commands.

### Step 2: Profile Generation

After the command completes, greywall analyzes the trace and generates `allowRead` and `allowWrite` lists, saving the result as a learned profile [README.md:171-173]().

### Step 3: Auto-Loading on Next Run

```bash
greywall -- opencode
```

The learned profile is automatically loaded without prompting [README.md:177-179]().

**Learning Mode Architecture:**

```mermaid
flowchart LR
    subgraph "Learning Mode Setup"
        CheckLearning["Verify tracer availability"]
        SetLearning["Set learning mode flag"]
        RelaxedFS["Relaxed filesystem config"]
    end
    
    subgraph "Execution and Tracing"
        StartCmd["execCmd.Start()"]
        Tracing["Linux: strace<br/>macOS: eslogger"]
        CollectData["Write trace to temp file"]
    end
    
    subgraph "Profile Generation"
        CheckSuccess{Command succeeded?}
        Analyze["Analyze trace output"]
        Filter["Filter system/sensitive paths"]
        Collapse["Collapse to directories"]
        Generate["Build Config struct"]
        Save["Save learned profile"]
    end
    
    CheckLearning --> SetLearning
    SetLearning --> RelaxedFS
    RelaxedFS --> StartCmd
    StartCmd --> Tracing
    Tracing --> CollectData
    CollectData --> CheckSuccess
    
    CheckSuccess -->|Yes| Analyze
    CheckSuccess -->|No| Skip["Skip generation"]
    
    Analyze --> Filter
    Filter --> Collapse
    Collapse --> Generate
    Generate --> Save
```

Sources: [cmd/greywall/main.go:128](), [README.md:163-180]()

## Common Use Cases

### Running AI Coding Agents

```bash
# Use a built-in profile
greywall --profile claude -- claude
```

### Development Server with Port Exposure

```bash
greywall -p 3000 -c "npm run dev"
```

### Custom Network Routing

Route through an external SOCKS5 proxy [cmd/greywall/main.go:120]():

```bash
greywall --proxy socks5://localhost:1080 -- curl https://api.example.com
```

### Command Deny Rules

Block dangerous commands by configuring `command.deny` [README.md:201-203]():

```bash
greywall -c "rm -rf /"  # Blocked by command deny rules
```

Sources: [README.md:38](), [README.md:201-203]()

## Quick Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `greywall check` | Verify installation and dependencies [README.md:123]() |
| `greywall setup` | Install/start greyproxy [README.md:126]() |
| `greywall -- <cmd>` | Run sandboxed command [README.md:29]() |
| `greywall -c "<cmd>"` | Run with shell expansion [README.md:102]() |
| `greywall --learning -- <cmd>` | Generate profile from trace [README.md:169]() |

### Common Flags

| Flag | Short | Purpose |
|------|-------|---------|
| `--debug` | `-d` | Enable debug output [cmd/greywall/main.go:117]() |
| `--monitor` | `-m` | Monitor violations [cmd/greywall/main.go:118]() |
| `--port <n>` | `-p` | Expose port [cmd/greywall/main.go:124]() |
| `--profile <name>` | | Load profile(s) [cmd/greywall/main.go:129]() |
| `--proxy <url>` | | Override SOCKS5 proxy [cmd/greywall/main.go:120]() |

Sources: [cmd/greywall/main.go:117-139](), [README.md:93-127]()

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/greywall/main.go](cmd/greywall/main.go)
- [docs/agents.md](docs/agents.md)
- [docs/cli-reference.md](docs/cli-reference.md)
- [docs/templates.md](docs/templates.md)

</details>



This page provides a complete reference for all `greywall` command-line interface commands, flags, and options. For general usage patterns and examples, see [Quick Start Guide](#2.2). For configuration file formats, see [Configuration System](#6).

---

## Command Overview

The `greywall` CLI provides a root command for sandboxing processes and several subcommands for system management, profile inspection, and shell completion.

```mermaid
graph TB
    ROOT["greywall<br/>[flags] -- command"]
    CHECK["greywall check"]
    SETUP["greywall setup"]
    PROFILES["greywall profiles"]
    COMPLETION["greywall completion"]
    PLIST["greywall profiles list"]
    PSHOW["greywall profiles show &lt;name&gt;"]
    PEDIT["greywall profiles edit &lt;name&gt;"]
    
    ROOT --> CHECK
    ROOT --> SETUP
    ROOT --> PROFILES
    ROOT --> COMPLETION
    PROFILES --> PLIST
    PROFILES --> PSHOW
    PROFILES --> PEDIT
    
    ROOT -.executes.-> SANDBOX["Sandboxed Process"]
    CHECK -.verifies.-> DEPS["Dependencies & Status"]
    SETUP -.installs.-> PROXY["greyproxy Service"]
    PLIST -.displays.-> SAVED["Saved & Built-in Profiles"]
    PSHOW -.displays.-> CONFIG["Profile JSON Content"]
```

**Sources:** [cmd/greywall/main.go:67-150](), [cmd/greywall/main.go:704-711]()

---

## Root Command: `greywall`

### Syntax

```bash
greywall [flags] [--] <command> [args...]
greywall -c "<shell string>"
```

The root command executes a command inside a sandboxed environment with network and filesystem restrictions. Use `--` to separate greywall flags from the command being sandboxed.

### Global Flags

| Flag | Shorthand | Type | Default | Description |
|------|-----------|------|---------|-------------|
| `--debug` | `-d` | bool | `false` | Enable debug logging to stderr |
| `--monitor` | `-m` | bool | `false` | Monitor and log sandbox violations (eBPF on Linux, unified log on macOS) |
| `--settings` | `-s` | string | OS config dir | Path to configuration file (see [Configuration Files](#6.1)) |
| `--proxy` | | string | `socks5://localhost:43052` | External SOCKS5 proxy URL for network traffic |
| `--http-proxy` | | string | `http://localhost:43051` | HTTP CONNECT proxy URL for network traffic |
| `--dns` | | string | `localhost:43053` | DNS server address for name resolution |
| `-c` | `-c` | string | | Run command string with shell expansion (like `sh -c`) |
| `--port` | `-p` | []string | | Expose port for inbound connections (repeatable) |
| `--forward` | `-f` | []string | | Forward host localhost port into sandbox (Linux only, repeatable) |
| `--version` | `-v` | bool | `false` | Show version, build time, and commit information |
| `--linux-features` | | bool | `false` | Display available Linux security features and exit |
| `--learning` | | bool | `false` | Trace filesystem access and generate profile (see [Learning Mode](#6.3)) |
| `--profile` | | string | | Load profiles by name, comma-separated (e.g., `claude,python`) |
| `--auto-profile` | | bool | `false` | Automatically apply saved or built-in profile without user prompt |
| `--no-network-rules` | | bool | `false` | Skip applying profile network rules to greyproxy |
| `--no-credential-protection` | | bool | `false` | Disable credential substitution (real values visible in sandbox) |
| `--inject` | | []string | | Inject a global credential by label from proxy dashboard |
| `--secret` | | []string | | Protect an additional env var not in the default list |
| `--ignore-secret` | | []string | | Exclude an env var from credential detection |
| `--allow` | | []string | | Allow a network destination for this session (e.g. `api.example.com:443`) |
| `--blank` | | bool | `false` | With `--learning`, skip default profile network rules |

**Sources:** [cmd/greywall/main.go:117-145](), [docs/cli-reference.md:18-39]()

### Command Specification Methods

The CLI accepts commands in two forms:

1. **Positional arguments** (recommended):
   ```bash
   greywall -- curl https://example.com
   greywall --profile python -- python script.py
   ```
   Use `--` to prevent flag parsing confusion when the sandboxed command has its own flags. [cmd/greywall/main.go:85-87]()

2. **Shell string** with `-c`:
   ```bash
   greywall -c "echo hello && ls"
   greywall -c "npm install && npm run dev"
   ```
   Allows shell operators (`&&`, `||`, pipes, etc.). [cmd/greywall/main.go:88-90]()

---

## Command Execution Flow

This diagram shows how CLI flags are processed and how configuration is merged before sandbox execution:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "main.go:runCommand"
    participant Config as "config.Load"
    participant Profiles as "Profile Resolution"
    participant Manager as "sandbox.Manager"
    participant Sandbox as "Platform Sandbox"
    
    User->>CLI: "greywall --profile claude -- opencode"
    
    CLI->>CLI: "Parse flags (cobra)"
    CLI->>CLI: "extractCommandName<br/>(args, cmdString)"
    Note over CLI: Command name: 'opencode'
    
    CLI->>Config: "Load settings file"
    Config-->>CLI: "Base config or default"
    
    alt Explicit --profile flag
        CLI->>Profiles: "resolveProfile('claude')"
        Profiles->>Profiles: "Try saved profile"
        Profiles->>Profiles: "Fall back to built-in"
        Profiles-->>CLI: "Profile config"
        CLI->>CLI: "config.Merge(base, profile)"
    else No --profile (auto-detect)
        CLI->>Profiles: "Check saved profile for 'opencode'"
        alt Saved profile exists
            Profiles-->>CLI: "Saved profile"
        else Built-in available
            CLI->>Profiles: "ResolveFirstRun<br/>(interactive prompt)"
            Profiles-->>CLI: "User choice"
        end
    end
    
    CLI->>CLI: "Apply CLI flag overrides<br/>(--proxy, --dns, etc.)"
    CLI->>CLI: "Apply greyproxy defaults"
    CLI->>CLI: "Auto-inject proxy credentials"
    
    CLI->>Manager: "NewManager(merged_config)"
    CLI->>Manager: "Initialize()"
    Manager->>Sandbox: "Setup platform-specific sandbox"
    CLI->>Manager: "WrapCommand(command)"
    Manager-->>CLI: "Sandboxed command string"
    
    CLI->>CLI: "exec.Command('sh', '-c', sandboxed)"
```

**Sources:** [cmd/greywall/main.go:136-447]()

---

## Subcommands

### `greywall check`

Runs diagnostics to verify greywall installation, dependencies, security features, and greyproxy status.

**Syntax:**
```bash
greywall check
```

**Verifies:**
- Required binaries (`bwrap`, `socat` on Linux). [docs/cli-reference.md:88]()
- Linux kernel security features (Landlock, seccomp, eBPF). [docs/cli-reference.md:89]()
- Greyproxy installation and service status. [docs/cli-reference.md:90]()

**Sources:** [cmd/greywall/main.go:149](), [docs/cli-reference.md:79-91]()

---

### `greywall setup`

Downloads, installs, and starts the greyproxy service.

**Syntax:**
```bash
greywall setup
```

**Behavior:**
- Installs greyproxy to `~/.local/bin/greyproxy`. [docs/cli-reference.md:100]()
- Registers it as a systemd user service (Linux) or launchd agent (macOS). [docs/cli-reference.md:100]()

**Sources:** [cmd/greywall/main.go:150](), [docs/cli-reference.md:92-101]()

---

### `greywall profiles`

Manages sandbox configuration profiles. Alias: `templates`. [docs/cli-reference.md:130]()

#### `greywall profiles list`

Lists all available profiles, including saved learned profiles and built-in profiles.

**Syntax:**
```bash
greywall profiles list
```

**Sources:** [docs/cli-reference.md:128-134]()

#### `greywall profiles show <name>`

Displays the full JSON content of a profile.

**Syntax:**
```bash
greywall profiles show <name>
```

**Sources:** [docs/cli-reference.md:136-142]()

#### `greywall profiles edit <name>`

Open a saved profile in `$EDITOR` for direct editing.

**Syntax:**
```bash
greywall profiles edit <name>
```

**Sources:** [docs/cli-reference.md:144-150]()

---

## Flag Processing and Configuration Merging

This diagram shows the precedence order for configuration resolution:

```mermaid
graph TB
    subgraph "Configuration Sources (Lowest to Highest Priority)"
        DEFAULT["Default Config<br/>config.Default()"]
        CONFIGFILE["Settings File<br/>--settings or default path"]
        SAVEDPROFILE["Saved Profile<br/>~/.config/greywall/learned/"]
        BUILTINPROFILE["Built-in Profile<br/>--profile flag"]
        CLIFLAGS["CLI Flags<br/>--proxy, --dns, etc."]
        DEFAULTS["greyproxy Defaults<br/>localhost:43052/43051/43053"]
        CREDENTIALS["Proxy Credentials<br/>Auto-injected"]
    end
    
    DEFAULT --> MERGE1["config.Merge"]
    CONFIGFILE --> MERGE1
    MERGE1 --> MERGE2["config.Merge"]
    SAVEDPROFILE --> MERGE2
    MERGE2 --> MERGE3["config.Merge"]
    BUILTINPROFILE --> MERGE3
    MERGE3 --> OVERRIDE1["Override"]
    CLIFLAGS --> OVERRIDE1
    OVERRIDE1 --> OVERRIDE2["Apply if empty"]
    DEFAULTS --> OVERRIDE2
    OVERRIDE2 --> INJECT["URL credential injection"]
    CREDENTIALS --> INJECT
    INJECT --> FINAL["Final Config<br/>to sandbox.Manager"]
    
    style FINAL stroke-width:2px
```

**Sources:** [cmd/greywall/main.go:178-314]()

---

## Environment Variables

The following environment variables are used or set by greywall:

| Variable | Description |
|----------|-------------|
| `GREYWALL_SANDBOX` | Set to `1` inside sandboxed processes. [docs/cli-reference.md:156]() |
| `HTTP_PROXY` / `HTTPS_PROXY` | Set to point to the local HTTP proxy. [docs/cli-reference.md:158]() |
| `ALL_PROXY` | Set to point to the SOCKS5 proxy. [docs/cli-reference.md:159]() |
| `GIT_SSH_COMMAND` | Set on macOS to route SSH through the proxy. [docs/cli-reference.md:160]() |

**Sources:** [docs/cli-reference.md:152-161]()

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Greywall error (config invalid, dependency missing, command blocked by policy) |
| Other | The exit code of the sandboxed command itself |

**Sources:** [docs/cli-reference.md:163-169]()

---

## Command-to-Code Entity Mapping

This table maps CLI elements to their implementation in the codebase:

| CLI Element | Implementation | File Reference |
|-------------|----------------|----------------|
| `greywall` root command | `runCommand()` | [cmd/greywall/main.go:136-447]() |
| `--debug` flag | `debug` variable | [cmd/greywall/main.go:34]() |
| `--monitor` flag | `monitor` variable | [cmd/greywall/main.go:35]() |
| `--settings` flag | `settingsPath` variable | [cmd/greywall/main.go:36]() |
| `--proxy` flag | `proxyURL` variable | [cmd/greywall/main.go:120]() |
| `--learning` flag | `learning` variable | [cmd/greywall/main.go:128]() |
| `--profile` flag | `profileName` variable | [cmd/greywall/main.go:129]() |
| `greywall check` | `newCheckCmd()` | [cmd/greywall/main.go:149]() |
| `greywall setup` | `newSetupCmd()` | [cmd/greywall/main.go:150]() |
| `greywall profiles` | `newProfilesCmd()` | [cmd/greywall/main.go:148]() |
| `--landlock-apply` | `runLandlockWrapper()` | [cmd/greywall/main.go:63]() |

**Sources:** [cmd/greywall/main.go:1-868]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/benchmarking.md](docs/benchmarking.md)
- [docs/concepts.md](docs/concepts.md)
- [docs/library.md](docs/library.md)
- [docs/security-model.md](docs/security-model.md)
- [internal/sandbox/manager.go](internal/sandbox/manager.go)

</details>



This page explains the fundamental architecture and security model of greywall. It covers the deny-by-default security principle, the two-layer isolation architecture (OS sandbox + proxy filtering), and the sandbox lifecycle from initialization to cleanup.

For details on network isolation mechanisms, see [Network Isolation](#3.1). For filesystem access control details, see [Filesystem Isolation](#3.2). For the threat model and security guarantees, see [Security Model](#3.3).

---

## Deny-by-Default Security Model

Greywall implements a deny-by-default security model for both network and filesystem access. This means that **all operations are blocked unless explicitly allowed** in the configuration.

| Resource Type | Default Behavior | Allow Mechanism |
|---------------|------------------|-----------------|
| **Network** | All outbound traffic blocked | `Network.AllowedDomains` list in config |
| **Filesystem Reads** | Blocked except system paths + CWD | `Filesystem.AllowRead` list in config |
| **Filesystem Writes** | Blocked entirely | `Filesystem.AllowWrite` list in config |
| **Commands** | Allowed unless matched | `Command.Deny` patterns in config |

The default configuration creates a highly restrictive sandbox:

```go
// Default config blocks all network and enables deny-by-default reads
cfg := greywall.DefaultConfig()
// Equivalent to:
// - Network.AllowedDomains: [] (blocks all traffic)
// - Filesystem.DefaultDenyRead: true (when nil/unset)
// - Filesystem.AllowWrite: [] (must opt-in)
```

**Sources:** [docs/security-model.md:23-49](), [docs/library.md:77-84](), [docs/concepts.md:61-72]()

---

## Two-Layer Isolation Architecture

Greywall uses a **two-layer defense-in-depth architecture** to enforce isolation:

1.  **OS Sandbox Layer**: Process isolation via platform-specific sandboxing mechanisms (bubblewrap on Linux, sandbox-exec on macOS).
2.  **Proxy Filtering Layer**: Network filtering via an external SOCKS5 proxy (typically `greyproxy`), which provides domain-based allow/deny controls.

### Architecture Diagram: Natural Language to Code Entities

```mermaid
graph TB
    subgraph "User Space (Code: pkg/greywall)"
        APP["Application Process<br/>(Sandboxed Command)"]
        MGR["Manager struct<br/>(internal/sandbox/manager.go)"]
    end
    
    subgraph "Layer 1: OS Sandbox (Platform-Specific)"
        BWRAP["Linux: bubblewrap<br/>• internal/sandbox/linux.go<br/>• PID/Net Namespaces"]
        SBEXEC["macOS: sandbox-exec<br/>• internal/sandbox/macos.go<br/>• Seatbelt Profiles"]
        LANDLOCK["Linux: Landlock LSM<br/>• internal/sandbox/landlock.go"]
        SECCOMP["Linux: seccomp-bpf<br/>• internal/sandbox/seccomp.go"]
    end
    
    subgraph "Layer 2: Proxy Filtering (Network Isolation)"
        GREYPROXY["greyproxy Service<br/>(External SOCKS5/DNS)"]
        P_BRIDGE["ProxyBridge<br/>(internal/sandbox/bridge.go)"]
        TUN["tun2socks<br/>(internal/sandbox/linux_network.go)"]
    end
    
    subgraph "External Resources"
        NET["Network<br/>(Internet)"]
        FS["Filesystem<br/>(Host)"]
    end
    
    APP --> MGR
    MGR --> BWRAP
    MGR --> SBEXEC
    BWRAP --> LANDLOCK
    BWRAP --> SECCOMP
    BWRAP --> P_BRIDGE
    P_BRIDGE --> TUN
    TUN --> GREYPROXY
    SBEXEC --> GREYPROXY
    GREYPROXY --> NET
    BWRAP --> FS
    SBEXEC --> FS
```

**Layer 1 (OS Sandbox)** provides process and resource isolation:
*   **Linux**: Uses `bubblewrap` for namespace isolation, `Landlock` for filesystem ACLs, and `seccomp-bpf` for syscall filtering [docs/concepts.md:86-89]().
*   **macOS**: Uses `sandbox-exec` with Seatbelt profiles for combined process/filesystem/network restrictions [docs/concepts.md:85-86]().

**Layer 2 (Proxy Filtering)** provides network access control:
*   All network traffic routes through a SOCKS5 proxy (defaulting to `greyproxy`) [docs/concepts.md:13-17]().
*   On Linux, transparent proxying via a TUN device and `tun2socks` captures all traffic [internal/sandbox/manager.go:139-148]().
*   On macOS, proxy environment variables route traffic for applications that honor them; others are blocked by the sandbox [docs/concepts.md:21-24]().

**Sources:** [docs/concepts.md:8-24](), [docs/security-model.md:31-38](), [internal/sandbox/manager.go:13-34]()

---

## Sandbox Lifecycle

The sandbox follows a well-defined lifecycle managed by the `Manager` type [internal/sandbox/manager.go:14]().

### Lifecycle Phases Diagram

```mermaid
sequenceDiagram
    participant CLI as "CLI/Library User"
    participant MGR as "sandbox.Manager"
    participant PROXY as "External Proxy"
    participant PLATFORM as "Platform Sandbox"
    participant CMD as "Sandboxed Command"
    
    CLI->>MGR: NewManager(cfg, debug, monitor)
    
    CLI->>MGR: Initialize()
    Note over MGR: internal/sandbox/manager.go:71
    MGR->>MGR: Detect Platform
    alt Linux
        MGR->>MGR: Extract tun2socks
        MGR->>MGR: NewProxyBridge()
    else macOS Learning Mode
        MGR->>MGR: Start eslogger (via sudo)
    end
    
    CLI->>MGR: WrapCommand(userCmd)
    MGR->>PLATFORM: Generate sandboxed string
    PLATFORM-->>MGR: wrappedCommand
    MGR-->>CLI: wrappedCommand
    
    CLI->>CMD: Execute wrappedCommand
    Note over CMD: Runs with OS-level restrictions
    
    CMD-->>CLI: Exit
    CLI->>MGR: Cleanup()
    Note over MGR: internal/sandbox/manager.go:209 (truncated)
    MGR->>PLATFORM: Release Bridges/Temp Files
```

### Phase 1: Manager Initialization

The `Manager` is created and initialized via `NewManager` [internal/sandbox/manager.go:37-43](). During `Initialize()` [internal/sandbox/manager.go:71-137]():
*   **Platform Support Check**: Validates the OS is supported [internal/sandbox/manager.go:76-78]().
*   **Linux Setup**: Extracts `tun2socks` and initializes the `ProxyBridge` (socat) to connect the isolated network namespace to the external proxy [internal/sandbox/manager.go:139-158]().
*   **macOS Learning**: If learning mode is enabled, starts `eslogger` via sudo to trace filesystem access [internal/sandbox/manager.go:83-113]().

### Phase 2: Command Wrapping

The user command is wrapped with sandbox restrictions via `WrapCommand`.
*   **Linux**: Generates a `bubblewrap` invocation with namespace flags, bind mounts, and Landlock/Seccomp enforcement.
*   **macOS**: Generates a `sandbox-exec` invocation using a Seatbelt profile and sets proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) [docs/security-model.md:37]().

### Phase 3: Execution and Monitoring

The wrapped command runs as a subprocess.
*   **Environment Sanitization**: Dangerous variables like `LD_PRELOAD` (Linux) or `DYLD_INSERT_LIBRARIES` (macOS) are stripped [docs/security-model.md:59-67]().
*   **Monitoring**: If `-m/--monitor` is passed, violations are logged [docs/security-model.md:68-71]().
*   **Learning Mode**: If enabled, `strace` (Linux) or `eslogger` (macOS) records path access to generate a profile template [internal/sandbox/manager.go:26-32]().

### Phase 4: Cleanup

The `Cleanup()` method releases resources [docs/library.md:153-155]():
*   Stops proxy bridges and DNS bridges.
*   Removes extracted binaries and temporary log files.
*   **Note**: The external `greyproxy` service remains running as it is managed independently.

**Sources:** [internal/sandbox/manager.go:71-208](), [docs/security-model.md:59-71](), [docs/library.md:116-136]()

---

## Configuration System

Greywall uses a profile-based configuration system that supports inheritance via the `Extends` field [docs/library.md:166-174]().

### Configuration Components

| Component | Code Entity | Purpose |
|-----------|------------|---------|
| **Network** | `NetworkConfig` | Domain allowlists, local binding, and proxy ports [docs/library.md:178-188](). |
| **Filesystem** | `FilesystemConfig` | Read/Write allow/deny rules and Git config access [docs/library.md:193-202](). |
| **Command** | `CommandConfig` | Pattern-based command blocking [docs/library.md:206-211](). |
| **SSH** | `SSHConfig` | Restrictions for commands run over SSH [docs/library.md:215-224](). |

**Sources:** [docs/library.md:162-225](), [docs/concepts.md:61-72]()

---

## Summary

Greywall's core architecture consists of:

1.  **Deny-by-default security**: All resources (Network, Filesystem) are blocked unless explicitly opted-in.
2.  **Two-layer isolation**: Combines OS-level sandboxing (bubblewrap/Seatbelt) with application-level network filtering (greyproxy).
3.  **Unified Lifecycle**: Managed through the `Manager` struct which handles platform-specific initialization and command wrapping.
4.  **Defense-in-Depth**: Includes environment sanitization, credential protection, and D-Bus isolation to prevent common sandbox escapes [docs/security-model.md:51-67]().

For network isolation details, see [Network Isolation](#3.1).  
For filesystem isolation details, see [Filesystem Isolation](#3.2).  
For security guarantees and threat model, see [Security Model](#3.3).

---

# Page: Network Isolation

# Network Isolation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/config/config.go](internal/config/config.go)
- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)

</details>



## Purpose and Scope

This page explains how greywall controls network access for sandboxed processes. It covers the two-layer isolation model (OS-level sandbox + proxy-based filtering), platform-specific implementations (Linux transparent proxying vs macOS proxy environment variables), and the greyproxy service architecture.

For filesystem access control, see [Filesystem Isolation](#3.2). For the overall security model and threat coverage, see [Security Model](#3.3). For greyproxy installation, management, and dashboard usage, see [greyproxy Service](#5.1).

## Two-Layer Isolation Model

Greywall enforces network isolation through two independent layers:

1. **OS-level network blocking** — Prevents direct network access at the kernel level.
2. **Proxy-based domain filtering** — Allows selective outbound traffic through greyproxy.

The OS sandbox ensures processes cannot bypass the proxy, while greyproxy enforces domain-based allow/deny lists. This defense-in-depth approach prevents both direct network access and unauthorized domains from being reached through the proxy.

```mermaid
graph TB
    subgraph "Sandboxed Process"
        APP["Application<br/>(curl, npm, etc)"]
    end
    
    subgraph "OS Sandbox Layer"
        LINUX["Linux: Network Namespace<br/>--unshare-net<br/>No external routes"]
        MACOS["macOS: Seatbelt Profile<br/>network-outbound rules<br/>Only proxy allowed"]
    end
    
    subgraph "Proxy Filter Layer"
        GREYPROXY["greyproxy Service<br/>localhost:43052 (SOCKS5)<br/>localhost:43051 (HTTP)<br/>localhost:43053 (DNS)"]
        RULES["Domain Filter<br/>NetworkRule<br/>Action: allow/deny"]
    end
    
    subgraph "External Network"
        INTERNET["Internet"]
    end
    
    APP --> LINUX
    APP --> MACOS
    
    LINUX -->|"Only proxy reachable"| GREYPROXY
    MACOS -->|"Only proxy reachable"| GREYPROXY
    
    GREYPROXY --> RULES
    RULES -->|"Allowed domains"| INTERNET
    RULES -.X.-|"Denied/unlisted domains"| APP
```

**Sources:** [internal/config/config.go:51-58](), [internal/sandbox/macos.go:32-39](), [internal/sandbox/linux.go:638-643]()

## Platform-Specific Implementations

| Aspect | Linux | macOS |
|--------|-------|-------|
| **OS Mechanism** | Network namespace isolation (`--unshare-net`) | Seatbelt profile network rules |
| **Proxy Method** | Transparent proxying via TUN device | Environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) |
| **Network Stack** | Isolated network namespace with loopback only | Full host network stack with filtered outbound |
| **TUN Device** | `tun0` (198.18.0.1/15) via `tun2socks` | Not used |
| **Bridge Component** | `socat` Unix socket bridges | Not needed (direct TCP to proxy) |
| **DNS Override** | Custom `/etc/resolv.conf` (127.0.0.1 or TCP-based) | Proxy environment variables |
| **Requirements** | `bwrap`, `socat`, `tun2socks` | `sandbox-exec` (built-in) |

**Sources:** [internal/sandbox/linux.go:638-643](), [internal/sandbox/macos.go:576-619]()

## Linux: Transparent Proxying Architecture

### Network Namespace Isolation

Linux sandboxes use `bubblewrap --unshare-net` to create an isolated network namespace with no external connectivity. The namespace contains only a loopback interface and a TUN device.

```mermaid
graph LR
    subgraph "Host Network Namespace"
        HOST["Host Network Stack<br/>External routes"]
        GREYPROXY_HOST["greyproxy<br/>localhost:43052"]
        SOCAT["socat Bridges<br/>Unix sockets"]
    end
    
    subgraph "Sandbox Network Namespace"
        LO["lo interface<br/>127.0.0.1"]
        TUN["tun0 interface<br/>198.18.0.1/15<br/>default route"]
        TUN2SOCKS["tun2socks process<br/>gvisor netstack<br/>SOCKS5 client"]
        APP_LINUX["Application"]
    end
    
    APP_LINUX -->|"TCP/UDP packets"| TUN
    TUN --> TUN2SOCKS
    TUN2SOCKS -->|"TCP to 127.0.0.1:18321"| LO
    LO --> SOCAT
    SOCAT -->|"Unix socket"| GREYPROXY_HOST
```

The namespace setup is performed by `bwrap` with these flags:
- `--unshare-net` — Create isolated network namespace [internal/sandbox/linux.go:638-643]()
- `--cap-add CAP_NET_ADMIN` — Allow TUN device creation and network configuration [internal/sandbox/linux.go:905-916]()

**Sources:** [internal/sandbox/linux.go:638-643](), [internal/sandbox/linux.go:905-916]()

### TUN Device and tun2socks

The TUN device (`tun0`) is set up as the default route inside the sandbox network namespace. All network traffic from sandboxed processes is routed to `tun0`, where `tun2socks` intercepts it.

**Network setup script** (generated by [internal/sandbox/linux.go:1005-1025]()):

```bash
# Bring up loopback (needed for socat binding)
ip link set lo up

# Create and configure TUN device
ip tuntap add dev tun0 mode tun
ip addr add 198.18.0.1/15 dev tun0
ip link set dev tun0 up
ip route add default via 198.18.0.1 dev tun0

# Start tun2socks (gvisor netstack)
/tmp/greywall-tun2socks -device tun0 -proxy socks5://127.0.0.1:18321 &
```

`tun2socks` converts raw IP packets from the TUN device into SOCKS5 connections to `127.0.0.1:18321`, which is bridged via `socat` to the host's greyproxy service.

**Sources:** [internal/sandbox/linux.go:1005-1025](), [internal/sandbox/linux.go:905-916]()

### Unix Socket Bridges

Three types of bridges connect the isolated network namespace to the host:

#### ProxyBridge

Bridges SOCKS5 traffic from sandbox to greyproxy.

**Component:** `ProxyBridge` [internal/sandbox/linux.go:21-31]()

**Flow:**
1. Host side: `socat UNIX-LISTEN:/tmp/greywall-proxy-*.sock TCP:localhost:43052` [internal/sandbox/linux.go:175-179]()
2. Sandbox side: `socat TCP-LISTEN:18321 UNIX-CONNECT:/tmp/greywall-proxy-*.sock`
3. Application → tun2socks → 127.0.0.1:18321 → Unix socket → greyproxy:43052

```mermaid
sequenceDiagram
    participant App as "Sandboxed App"
    participant Tun as "tun2socks"
    participant Socat as "socat Bridge<br/>(sandbox)"
    participant Socket as "Unix Socket<br/>/tmp/greywall-proxy-*.sock"
    participant SocatHost as "socat Bridge<br/>(host)"
    participant Greyproxy as "greyproxy:43052"
    
    App->>Tun: TCP packet (any destination)
    Tun->>Socat: SOCKS5 to 127.0.0.1:18321
    Socat->>Socket: Forward via ProxyBridge.SocketPath
    Socket->>SocatHost: Cross namespace boundary
    SocatHost->>Greyproxy: TCP to ProxyHost:ProxyPort
    Greyproxy-->>SocatHost: Filtered response
    SocatHost-->>Socket: Return via Unix socket
    Socket-->>Socat: Cross namespace boundary
    Socat-->>Tun: SOCKS5 response
    Tun-->>App: TCP packet response
```

**Sources:** [internal/sandbox/linux.go:131-192](), [internal/sandbox/linux.go:1016-1020]()

#### DnsBridge

Bridges DNS queries from sandbox to greyproxy's DNS server.

**Component:** `DnsBridge` [internal/sandbox/linux.go:33-41]()

**Flow:**
1. Host side: `socat UNIX-LISTEN:/tmp/greywall-dns-*.sock UDP:localhost:43053` [internal/sandbox/linux.go:65-68]()
2. Sandbox side: `socat UDP4-RECVFROM:53 UNIX-CONNECT:/tmp/greywall-dns-*.sock`
3. Application DNS query → UDP :53 → Unix socket → greyproxy:43053

When `DnsBridge` is active, `/etc/resolv.conf` inside the sandbox is overridden to point to `127.0.0.1`.

**Sources:** [internal/sandbox/linux.go:43-90](), [internal/sandbox/linux.go:926-949]()

#### ReverseBridge

Bridges inbound connections from host to sandboxed dev servers.

**Component:** `ReverseBridge` [internal/sandbox/linux.go:105-111]()

**Flow (for exposed port 3000):**
1. Host side: `socat TCP-LISTEN:3000 UNIX-CONNECT:/tmp/greywall-rev-3000-*.sock`
2. Sandbox side: `socat UNIX-LISTEN:/tmp/greywall-rev-3000-*.sock TCP:127.0.0.1:3000`
3. External client → Host port 3000 → Unix socket → Sandbox 127.0.0.1:3000

This enables inbound access to sandboxed dev servers (started with `forwardPorts` config or CLI flag) while maintaining network isolation for outbound traffic.

**Sources:** [internal/sandbox/linux.go:222-272](), [internal/sandbox/linux.go:1055-1064](), [internal/config/config.go:69]()

### DNS Resolution

Linux sandboxes override `/etc/resolv.conf` to control DNS resolution:

**With DnsBridge** [internal/sandbox/linux.go:929-932]():
```
nameserver 127.0.0.1
```
Points to local socat relay (UDP :53 → Unix socket → greyproxy:43053).

**Without DnsBridge (tun2socks only)** [internal/sandbox/linux.go:933-938]():
```
nameserver 1.1.1.1
nameserver 8.8.8.8
options use-vc
```
Forces TCP-based DNS (RFC 1035 §4.2.2 "use-vc" flag), which `tun2socks` handles natively via SOCKS5 tunnel.

**Sources:** [internal/sandbox/linux.go:926-949]()

## macOS: Seatbelt Profile Network Rules

macOS sandboxes use Seatbelt profiles to enforce network restrictions. The profile allows outbound connections only to greyproxy's local ports and denies everything else.

### Profile Generation

Network rules are generated by `GenerateSandboxProfile()` [internal/sandbox/macos.go:422-644]() based on `MacOSSandboxParams.NeedsNetworkRestriction`.

**When network restriction is enabled** [internal/sandbox/macos.go:577-619]():

```scheme
; Always allow localhost binding (dev servers, OAuth callbacks)
(allow network-bind (local ip "localhost:*"))
(allow network-inbound (local ip "localhost:*"))

; Allow outbound to SOCKS5 proxy
(allow network-outbound (remote tcp "localhost:43052"))

; Allow outbound to HTTP CONNECT proxy
(allow network-outbound (remote tcp "localhost:43051"))

; Allow outbound to DNS proxy (TCP + UDP)
(allow network-outbound (remote tcp "localhost:43053"))
(allow network-outbound (remote udp "localhost:43053"))
```

**Sources:** [internal/sandbox/macos.go:576-619](), [internal/sandbox/macos_test.go:63-68]()

### Proxy Environment Variables

macOS sandboxes rely on applications respecting proxy environment variables:

**Generated by `GenerateProxyEnvVars()`** (referenced in [internal/sandbox/macos.go:738]()):

```bash
HTTP_PROXY=http://localhost:43051
HTTPS_PROXY=http://localhost:43051
ALL_PROXY=socks5://localhost:43052
NO_PROXY=localhost,127.0.0.1
```

These variables are set in the sandbox command wrapper.

**Limitation:** Applications that don't respect proxy environment variables (e.g., raw socket programming) cannot be network-isolated on macOS without additional kernel-level restrictions.

**Sources:** [internal/sandbox/macos.go:738-746]()

## greyproxy Service

The `greyproxy` service is the central filtering component that runs on the host system. It provides three network services:

| Service | Default Port | Protocol | Purpose |
|---------|--------------|----------|---------|
| **SOCKS5 Proxy** | 43052 | SOCKS5 | General-purpose proxy (supports TCP + UDP via SOCKS5) |
| **HTTP CONNECT Proxy** | 43051 | HTTP CONNECT | HTTP/HTTPS proxying for tools that don't support SOCKS5 |
| **DNS Server** | 43053 | DNS (UDP/TCP) | DNS resolution with domain filtering |
| **Dashboard** | 43080 | HTTP | Web UI for monitoring and configuration |

**Filtering logic:**
1. Extract destination domain from SOCKS5/HTTP CONNECT/DNS request.
2. Check against `NetworkRule` objects sent during session creation [internal/config/config.go:51-58]().
3. Reject if not explicitly allowed (deny-by-default).

**Sources:** [internal/config/config.go:70](), [internal/sandbox/macos.go:33-39]()

## Domain-Based Filtering

Domains are filtered at the proxy layer by matching against configured allow/deny lists.

### Configuration

**Network configuration structure** [internal/config/config.go:60-71]():

```go
type NetworkConfig struct {
    ProxyURL            string        `json:"proxyUrl,omitempty"`
    HTTPProxyURL        string        `json:"httpProxyUrl,omitempty"`
    DnsAddr             string        `json:"dnsAddr,omitempty"`
    AllowUnixSockets    []string      `json:"allowUnixSockets,omitempty"`
    AllowAllUnixSockets bool          `json:"allowAllUnixSockets,omitempty"`
    AllowLocalBinding   bool          `json:"allowLocalBinding,omitempty"`
    AllowLocalOutbound  *bool         `json:"allowLocalOutbound,omitempty"`
    ForwardPorts        []int         `json:"forwardPorts,omitempty"`
    Rules               []NetworkRule `json:"rules,omitempty"`
}
```

### Wildcard Matching

Allowed domain patterns in `NetworkRule.Destination` [internal/config/config.go:54]():
- Exact match: `api.openai.com`
- Wildcard subdomain: `**.openai.com`
- IP Range: `192.168.0.0/24`

**Sources:** [internal/config/config.go:51-58]()

## Localhost Controls

Greywall provides fine-grained control over localhost access, separating inbound (binding) from outbound (connecting):

### AllowLocalBinding

**Purpose:** Allows sandboxed processes to bind to localhost ports (e.g., dev servers, OAuth callbacks).

**macOS implementation** [internal/sandbox/macos.go:585-587]():
```scheme
(allow network-bind (local ip "localhost:*"))
(allow network-inbound (local ip "localhost:*"))
```

**Sources:** [internal/sandbox/macos.go:585-587](), [internal/config/config.go:67]()

### AllowLocalOutbound

**Purpose:** Allows sandboxed processes to connect to services running on localhost (e.g., Redis, PostgreSQL, Docker containers).

**Default behavior:** If `nil`, it defaults to the value of `AllowLocalBinding` [internal/config/config.go:68]().

**macOS implementation** [internal/sandbox/macos.go:589-592]():
```scheme
(allow network-outbound (local ip "localhost:*"))
```

**Sources:** [internal/sandbox/macos.go:589-592](), [internal/config/config.go:68]()

### Exposed Ports (ForwardPorts)

**Purpose:** Makes sandboxed dev servers accessible from outside the sandbox.

**Linux implementation:** `ReverseBridge` creates `socat` bridges for each port in `ForwardPorts` [internal/sandbox/linux.go:105-111]().

**Sources:** [internal/sandbox/linux.go:222-272](), [internal/config/config.go:69]()

## Network Isolation Flow Comparison

### Linux Transparent Proxy Flow

```mermaid
graph TB
    APP["Application Code<br/>(makes HTTP request)"]
    GETADDRINFO["getaddrinfo()<br/>(DNS resolution)"]
    DNS_RELAY["DnsBridge<br/>UDP :53 → Unix socket"]
    GREYPROXY_DNS["greyproxy DNS<br/>:43053"]
    CONNECT["connect()<br/>(TCP socket)"]
    TUN["TUN Device<br/>tun0"]
    TUN2SOCKS["tun2socks<br/>SOCKS5 client"]
    PROXY_RELAY["ProxyBridge<br/>TCP :18321 → Unix socket"]
    GREYPROXY_SOCKS["greyproxy SOCKS5<br/>:43052"]
    DOMAIN_FILTER["Domain Filter<br/>check NetworkRule"]
    INTERNET["External Server"]
    
    APP --> GETADDRINFO
    GETADDRINFO --> DNS_RELAY
    DNS_RELAY --> GREYPROXY_DNS
    GREYPROXY_DNS --> DOMAIN_FILTER
    DOMAIN_FILTER -->|"Allowed"| GETADDRINFO
    GETADDRINFO --> APP
    
    APP --> CONNECT
    CONNECT --> TUN
    TUN --> TUN2SOCKS
    TUN2SOCKS --> PROXY_RELAY
    PROXY_RELAY --> GREYPROXY_SOCKS
    GREYPROXY_SOCKS --> DOMAIN_FILTER
    DOMAIN_FILTER -->|"Allowed"| INTERNET
```

**Sources:** [internal/sandbox/linux.go:993-1054](), [internal/sandbox/linux.go:21-41]()

### macOS Environment Variable Flow

```mermaid
graph TB
    APP["Application Code<br/>(checks HTTP_PROXY env)"]
    ENV["HTTP_PROXY=localhost:43051<br/>ALL_PROXY=socks5://localhost:43052"]
    SEATBELT["Seatbelt Profile<br/>network-outbound filter"]
    GREYPROXY["greyproxy<br/>SOCKS5/HTTP/DNS"]
    DOMAIN_FILTER["Domain Filter<br/>check NetworkRule"]
    INTERNET["External Server"]
    
    APP --> ENV
    ENV -->|"Proxy-aware app"| GREYPROXY
    APP -.->|"Non-proxy-aware app"| SEATBELT
    SEATBELT -.X.-|"Blocked by Seatbelt"| APP
    
    GREYPROXY --> DOMAIN_FILTER
    DOMAIN_FILTER -->|"Allowed"| INTERNET
    DOMAIN_FILTER -.X.-|"Denied"| GREYPROXY
```

**Sources:** [internal/sandbox/macos.go:738-748](), [internal/sandbox/macos.go:576-619]()

---

# Page: Filesystem Isolation

# Filesystem Isolation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/config/config.go](internal/config/config.go)
- [internal/sandbox/dangerous.go](internal/sandbox/dangerous.go)
- [internal/sandbox/integration_linux_test.go](internal/sandbox/integration_linux_test.go)
- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/integration_test.go](internal/sandbox/integration_test.go)
- [internal/sandbox/linux_landlock.go](internal/sandbox/linux_landlock.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)

</details>



This page explains how greywall controls filesystem access through deny-by-default isolation, mount-based restrictions, and path-level access rules. For network access control, see [Network Isolation](). For the overall security architecture, see [Security Model](). Platform-specific implementation details are covered in [Linux Sandboxing]() and [macOS Sandboxing]().

## Deny-by-Default Security Model

Greywall implements deny-by-default filesystem isolation, where the sandbox starts with minimal filesystem access and selectively grants permissions. This inverts the traditional security model and reduces the attack surface for AI-generated commands.

When `DefaultDenyRead` mode is enabled (the default behavior), the sandbox:

1.  **Blocks all filesystem reads by default** (except metadata operations like `stat`, `readdir`) [internal/sandbox/macos.go:159-166]().
2.  **Allows only essential system paths** (`/usr`, `/lib`, `/etc`, etc.) for program execution [internal/sandbox/dangerous.go:95-134]().
3.  **Allows the current working directory** (project directory) for read/write [internal/sandbox/linux_landlock.go:84-89]().
4.  **Requires explicit allowlisting** for any additional paths via `allowRead` or `allowWrite` [internal/config/config.go:73-81]().

This prevents sandboxed processes from accessing sensitive files like SSH keys, browser credentials, or API tokens unless explicitly permitted.

**Configuration Example:**
```json
{
  "filesystem": {
    "defaultDenyRead": true,
    "allowRead": ["/home/user/.config/myapp"],
    "denyRead": ["/home/user/.ssh"],
    "allowWrite": ["/tmp/cache"],
    "denyWrite": [".git/hooks"]
  }
}
```

Sources: [internal/config/config.go:73-81](), [internal/sandbox/macos.go:156-213](), [internal/sandbox/linux_landlock.go:96-134]()

## Platform-Specific Implementations

### Linux: bubblewrap + Landlock

Linux filesystem isolation uses two complementary mechanisms: namespace isolation via bubblewrap and kernel-level access control via Landlock.

Title: Linux Filesystem Isolation Architecture
```mermaid
graph TB
    subgraph "bubblewrap Mount Namespace"
        TMPFS["--tmpfs /<br/>Empty root filesystem"]
        SYSTEM["--ro-bind /usr /usr<br/>--ro-bind /lib /lib<br/>System paths (read-only)"]
        CWD["--bind $CWD $CWD<br/>Project directory (read-write)"]
        MASK["--ro-bind empty .env<br/>Mask sensitive files"]
    end
    
    subgraph "Landlock LSM"
        RULESET["LandlockRuleset<br/>Kernel-enforced ACLs"]
        READRULE["AllowRead()<br/>READ_FILE + READ_DIR + EXECUTE"]
        WRITERULE["AllowReadWrite()<br/>WRITE_FILE + MAKE_* + REMOVE_*"]
    end
    
    CONFIG["config.Config"] --> TMPFS
    CONFIG --> SYSTEM
    CONFIG --> CWD
    CONFIG --> MASK
    
    CONFIG --> RULESET
    RULESET --> READRULE
    RULESET --> WRITERULE
    
    TMPFS -.mount isolation.-> SYSTEM
    SYSTEM -.mount isolation.-> CWD
    CWD -.mount isolation.-> MASK
    
    READRULE -.kernel enforcement.-> WRITERULE
```

**bubblewrap Mount Strategy:**
The sandbox constructs a private mount namespace using `bwrap`. In `DefaultDenyRead` mode, it starts with an empty root (`--tmpfs /`) and bind-mounts only required paths. It specifically masks sensitive files in the CWD (like `.env`) by bind-mounting an empty file over them [internal/sandbox/dangerous.go:33-40]().

**Landlock Kernel Enforcement:**
The `ApplyLandlockFromConfig` function provides kernel-level access control that survives process privileges [internal/sandbox/linux_landlock.go:18-21]().
- **ABI version detection**: Supports Landlock v1-v5 with graceful fallback [internal/sandbox/linux_landlock.go:22-29]().
- **Path-based rules**: Each path gets an `AllowRead()` or `AllowReadWrite()` rule [internal/sandbox/linux_landlock.go:156-191]().
- **Descendant coverage**: Landlock's `PATH_BENEATH` semantics automatically cover all descendants.

Sources: [internal/sandbox/linux_landlock.go:18-206](), [internal/sandbox/dangerous.go:33-53]()

### macOS: Seatbelt Profiles

macOS uses declarative Seatbelt profiles compiled by `sandbox-exec`.

Title: macOS Seatbelt Generation Flow
```mermaid
graph TB
    subgraph "Seatbelt Profile Generation"
        PARAMS["sandbox.MacOSSandboxParams<br/>DefaultDenyRead, Cwd, ReadAllowPaths, etc."]
        READRULES["generateReadRules()<br/>file-read-metadata, file-read-data"]
        WRITERULES["generateWriteRules()<br/>file-write*"]
        PROFILE["GenerateSandboxProfile()<br/>Scheme code"]
    end
    
    subgraph "Seatbelt Operations"
        METADATA["file-read-metadata<br/>stat, readdir (always allowed)"]
        READDATA["file-read-data<br/>Actual file content reads"]
        WRITESTAR["file-write*<br/>write, create, unlink"]
        DENYRULES["deny file-read-data<br/>deny file-write*<br/>Overrides allow rules"]
    end
    
    PARAMS --> READRULES
    PARAMS --> WRITERULES
    READRULES --> PROFILE
    WRITERULES --> PROFILE
    
    PROFILE --> METADATA
    PROFILE --> READDATA
    PROFILE --> WRITESTAR
    PROFILE --> DENYRULES
    
    READDATA -.subpath/regex/literal.-> DENYRULES
```

**Seatbelt Rule Hierarchy:**
In deny-by-default mode, `generateReadRules` creates a tiered access model:
1.  **Global metadata allow**: `(allow file-read-metadata)` enables directory traversal and `stat()` [internal/sandbox/macos.go:166]().
2.  **System path allows**: Essential paths like `/usr` and `/System` are granted `file-read-data` [internal/sandbox/macos.go:170-175]().
3.  **CWD allow**: The project directory gets full recursive read access [internal/sandbox/macos.go:178-182]().
4.  **Deny overrides**: Sensitive files are explicitly blocked via `(deny file-read-data)` [internal/sandbox/macos_test.go:185-189]().

**Important Seatbelt Quirk:**
Deny rules MUST use specific operations (`file-read-data`) rather than wildcards (`file-read*`). Seatbelt ignores wildcard denies when a specific allow covers the same path [internal/sandbox/macos_test.go:172-174]().

Sources: [internal/sandbox/macos.go:156-282](), [internal/sandbox/macos_test.go:170-195]()

## Path Rule Processing

Both platforms support glob patterns in path rules:

| Pattern | Meaning | Example |
| :--- | :--- | :--- |
| `*` | Matches any characters except `/` | `*.log` matches `app.log` |
| `**` | Matches any characters including `/` | `**/*.env` matches `.env` at any depth |
| `dir/**` | Matches directory and all descendants | `node_modules/**` |
| Absolute path | Literal path | `/etc/hosts` |

**Glob Expansion and Conversion:**
- **Linux**: `ExpandGlobPatterns` optimizes for Landlock's `PATH_BENEATH` semantics. For example, `dir/**` is simplified to just `dir` because Landlock rules are recursive by default [internal/sandbox/linux_landlock.go:157-172]().
- **macOS**: Globs are converted to regex patterns via `GlobToRegex` for use in the Seatbelt profile [internal/sandbox/macos.go:57-72]().

Sources: [internal/sandbox/linux_landlock.go:156-191](), [internal/sandbox/macos.go:56-72]()

## Default Readable and Writable Paths

Greywall provides sensible defaults via `GetDefaultReadablePaths` and `GetDefaultWritePaths` to ensure common development tools function correctly.

**Default Readable Paths (Read-Only):**
Essential for runtime execution, including core system paths (`/usr`, `/bin`), system config (`/etc`), and user-installed tooling like `.nvm`, `.pyenv`, and `.cargo/bin` [internal/sandbox/dangerous.go:95-188]().

**Default Writable Paths:**
Includes standard locations like `/tmp`, `/dev/stdout`, and `/dev/null` [internal/sandbox/dangerous.go:63-85]().

Sources: [internal/sandbox/dangerous.go:63-189]()

## Sensitive File Protection

Certain files are **always protected** regardless of project directory writability to prevent credential leakage or sandbox escape.

-   **SensitiveProjectFiles**: Masked in CWD (e.g., `.env`, `.env.local`) [internal/sandbox/dangerous.go:33-40]().
-   **DangerousFiles**: Protected from writes (e.g., `.gitconfig`, `.bashrc`, `.zshrc`) [internal/sandbox/dangerous.go:10-20]().
-   **DangerousDirectories**: Protected from writes (e.g., `.vscode`, `.claude/commands`, `.git/hooks`) [internal/sandbox/dangerous.go:24-29](), [internal/sandbox/dangerous.go:207-210]().

On Linux, `TestLinux_LandlockProtectsGitHooks` verifies that `.git/hooks` cannot be modified even if the workspace is writable [internal/sandbox/integration_linux_test.go:88-104](). On macOS, `TestMacOS_SeatbeltBlocksEnvFileRead` ensures `.env` files remain unreadable even if the workspace has broad read access [internal/sandbox/integration_macos_test.go:175-195]().

Sources: [internal/sandbox/dangerous.go:8-53](), [internal/sandbox/dangerous.go:192-218](), [internal/sandbox/integration_linux_test.go:88-104](), [internal/sandbox/integration_macos_test.go:175-195]()

## macOS-Specific Symlink Handling

On macOS, `/tmp` is a symlink to `/private/tmp`. If Seatbelt rules only mention one variant, resolution can fail if the path hasn't been created yet. The `expandMacOSTmpPaths` function automatically mirrors any `/tmp` or `/private/tmp` rules to both variants to ensure consistent kernel matching [internal/sandbox/macos.go:97-127]().

Sources: [internal/sandbox/macos.go:97-127]()

---

# Page: Security Model

# Security Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/credential-protection.md](docs/credential-protection.md)
- [docs/security-model.md](docs/security-model.md)
- [internal/sandbox/credentials.go](internal/sandbox/credentials.go)
- [internal/sandbox/credentials_test.go](internal/sandbox/credentials_test.go)
- [internal/sandbox/sanitize.go](internal/sandbox/sanitize.go)

</details>



Greywall is intended as a defense-in-depth tool for running semi-trusted commands with reduced side effects (e.g., package installs, build scripts, CI jobs, or exploring unfamiliar repositories) [docs/security-model.md:8-11](). It is not designed to be a strong isolation boundary against actively malicious code specifically engineered to escape OS sandboxes [docs/security-model.md:84-86]().

## Defense-in-Depth Architecture

Greywall implements security by combining multiple independent layers. If one layer is bypassed, other layers continue to provide protection.

### System Components and Enforcement Points

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserIntent["'Run npm install safely'"]
        Policy["'Block ~/.ssh and unknown domains'"]
    end

    subgraph "Code Entity Space: greywall"
        Manager["sandbox.Manager"]
        Creds["sandbox.DetectCredentials"]
        Sanitize["sandbox.FilterDangerousEnv"]
        
        subgraph "Linux Implementation"
            Bwrap["bubblewrap (bwrap)"]
            Seccomp["internal/sandbox/linux_seccomp.go"]
            Landlock["internal/sandbox/linux_landlock.go"]
            EBPF["internal/sandbox/linux_ebpf.go"]
        end

        subgraph "macOS Implementation"
            Seatbelt["internal/sandbox/mac_seatbelt.go"]
            LogMon["internal/sandbox/monitor.go"]
        end
    end

    subgraph "External Security Services"
        Proxy["greyproxy (SOCKS5/HTTP)"]
    end

    UserIntent --> Manager
    Policy --> Manager
    Manager --> Creds
    Manager --> Sanitize
    
    Manager --> Seccomp
    Manager --> Landlock
    Manager --> Bwrap
    Manager --> Seatbelt
    
    Bwrap --> Proxy
    Seatbelt --> Proxy
```
**Sources:** [internal/sandbox/credentials.go:136-179](), [internal/sandbox/sanitize.go:52-60](), [docs/security-model.md:31-38]()

## Threat Model

### Protected Threats
Greywall reduces risk from the following vectors [docs/security-model.md:14-20]():
*   **Supply-chain attacks:** Scripts that unexpectedly call out to the network or exfiltrate data.
*   **Filesystem sprawling:** Tools that write broadly across the filesystem or modify sensitive configs.
*   **Secret leakage:** Accidental "phone home" behavior that leaks environment variables.
*   **Persistence:** Unfamiliar repos running surprising commands to install backdoors or git hooks.

### Non-Protected Threats
Greywall does **not** solve for [docs/security-model.md:73-86]():
*   **Hostile code containment:** Assume determined attackers may escape via kernel vulnerabilities.
*   **Resource limits:** CPU, memory, disk space, or fork bombs are out of scope.
*   **Content-based controls:** It does not block data exfiltration to *allowed* destinations.
*   **Non-Proxy-Aware Tools (macOS):** On macOS, tools that ignore proxy environment variables may bypass network isolation if transparent proxying isn't available.

## Security Mechanisms

### 1. Network Isolation (Default Deny)
Outbound network access is blocked by default. Traffic must be routed through a proxy [docs/security-model.md:25-27]().
*   **Transparent Proxying (Linux):** Uses a TUN device inside the sandbox to route all traffic through `tun2socks`, forwarding to an external SOCKS5 proxy via a Unix socket bridge [docs/security-model.md:31-38]().
*   **Environment Fallback:** If TUN is unavailable, greywall sets `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` [docs/security-model.md:37-38]().
*   **Localhost Control:** Inbound binding and outbound connections to `127.0.0.1` are controlled via `allowLocalOutbound` [docs/security-model.md:39-42]().

### 2. Filesystem Isolation
*   **Deny-by-Default:** Reads and writes are denied unless explicitly allowed [docs/security-model.md:43-46]().
*   **Protected Targets:** Internal lists protect sensitive paths like shell configs, git hooks, and `.env` files [docs/security-model.md:49-50]().
*   **Linux Landlock:** Kernel-enforced filesystem ACLs using Landlock LSM [docs/security-model.md:51-53]().

### 3. Credential Protection
Greywall prevents sandboxed processes from seeing real secrets by using a "placeholder substitution" system [docs/credential-protection.md:6-10]().

| Stage | Action | Code Entity |
| :--- | :--- | :--- |
| **Detection** | Scans env for well-known keys (e.g., `AWS_SECRET_ACCESS_KEY`) or suffixes (e.g., `_TOKEN`). | `sandbox.DetectCredentials` [internal/sandbox/credentials.go:136-179]() |
| **Placeholder** | Generates a unique string: `greyproxy:credential:v1:gw-<id>:<digest>`. | `sandbox.generatePlaceholder` [internal/sandbox/credentials.go:192-199]() |
| **Registration** | Registers the mapping with `greyproxy` via its API. | `sandbox.RegisterSession` [internal/sandbox/credentials.go:275-300]() |
| **Substitution** | Rewrites the sandbox environment with placeholders. | `sandbox.SubstituteEnv` [internal/sandbox/credentials.go:214-245]() |
| **Proxy Swap** | `greyproxy` detects placeholders in HTTP headers/params and swaps them for real values. | External (greyproxy) |

**Sources:** [internal/sandbox/credentials.go:32-96](), [docs/credential-protection.md:12-21]()

### 4. Environment Sanitization
Greywall strips dangerous environment variables that could be used for library injection attacks [internal/sandbox/sanitize.go:43-49]().
*   **Linux:** Strips `LD_PRELOAD`, `LD_LIBRARY_PATH`, and other `LD_*` variables [internal/sandbox/sanitize.go:14-17]().
*   **macOS:** Strips `DYLD_INSERT_LIBRARIES`, `DYLD_LIBRARY_PATH`, and other `DYLD_*` variables [internal/sandbox/sanitize.go:14-17]().

**Sources:** [internal/sandbox/sanitize.go:19-41](), [docs/security-model.md:59-67]()

### 5. D-Bus and Socket Isolation (Linux)
The D-Bus session bus is blocked to prevent the sandbox from using host services like `gnome-keyring` or launching processes via Flatpak portals [docs/security-model.md:51-53](). Greywall overlays `/run/user` with a `tmpfs` to hide:
*   Wayland/X11 sockets
*   PipeWire/PulseAudio
*   SSH and GPG agent sockets (can be re-added selectively) [docs/security-model.md:53]().

## Implementation Flow

The following diagram maps the security initialization flow to specific code functions.

```mermaid
sequenceDiagram
    participant CLI as cmd/greywall
    participant M as sandbox.Manager
    participant S as sandbox.Sanitize
    participant C as sandbox.Credentials
    participant OS as OS Sandbox (bwrap/Seatbelt)

    CLI->>M: NewManager(config)
    M->>S: FilterDangerousEnv(os.Environ())
    Note over S: Strips LD_PRELOAD, DYLD_*
    S-->>M: Hardened Env
    
    M->>C: DetectCredentials(env)
    Note over C: Identifies API_KEY, TOKEN, etc.
    C-->>M: Credential Mappings
    
    M->>C: RegisterSession(mappings)
    Note over C: Sends mappings to greyproxy API
    
    M->>C: SubstituteEnv(env, mappings)
    Note over C: Replaces secrets with placeholders
    
    M->>OS: Start Sandbox
    Note over OS: Apply Seccomp, Landlock, or Seatbelt
```
**Sources:** [internal/sandbox/sanitize.go:52-60](), [internal/sandbox/credentials.go:136-179](), [internal/sandbox/credentials.go:214-245](), [docs/security-model.md:59-67]()

## Visibility and Auditing
Greywall provides tools to inspect what a sandboxed process is attempting to do without compromising the security boundary:
*   **`--monitor` (`-m`):** Real-time monitoring of blocked access attempts via eBPF (Linux) or Unified Log (macOS) [docs/security-model.md:70]().
*   **`--debug` (`-d`):** Detailed logs explaining why specific paths or network requests were blocked [docs/security-model.md:71]().

**Sources:** [docs/security-model.md:68-72]()

---

# Page: Platform Implementations

# Platform Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/platform-support.md](docs/platform-support.md)
- [internal/platform/platform.go](internal/platform/platform.go)
- [internal/sandbox/manager_darwin.go](internal/sandbox/manager_darwin.go)
- [internal/sandbox/manager_linux.go](internal/sandbox/manager_linux.go)

</details>



This page provides an overview of how greywall implements sandboxing on Linux versus macOS. The two platforms require fundamentally different approaches due to differences in their kernel architectures and available security primitives. For detailed technical documentation on each platform's implementation, see [Linux Sandboxing](#4.1) and [macOS Sandboxing](#4.2).

## Platform Architecture Differences

Linux and macOS provide different sets of security mechanisms, requiring platform-specific implementations that share common goals but use different techniques.

### High-Level Comparison

**Linux Implementation Strategy:**
- **Defense-in-depth:** Multiple independent security layers including namespaces, Landlock LSM, and seccomp syscall filtering [docs/platform-support.md:33-36]().
- **Transparent network proxying:** Full traffic capture using a network namespace, TUN device, and `tun2socks` [docs/platform-support.md:39]().
- **Kernel-level enforcement:** Landlock (Linux 5.13+) restricts filesystem operations independently of mount rules [docs/platform-support.md:36]().
- **Runtime monitoring:** eBPF allows real-time violation monitoring for blocked syscalls and file access [docs/platform-support.md:38]().

**macOS Implementation Strategy:**
- **Unified policy:** Uses `sandbox-exec` with dynamically generated Seatbelt profiles to control files, network, and IPC [docs/platform-support.md:48]().
- **Environment-based proxying:** Routes traffic via `ALL_PROXY` / `HTTP_PROXY` environment variables; no transparent capture [docs/platform-support.md:50]().
- **Application cooperation:** Only applications that honor standard proxy environment variables are redirected [docs/platform-support.md:50]().
- **Log-based monitoring:** Violation monitoring is achieved through macOS unified logging via `eslogger` [docs/platform-support.md:18](), [docs/platform-support.md:52]().

### Platform Comparison Table

| Feature | Linux | macOS |
|---------|-------|-------|
| **Sandbox Engine** | bubblewrap [docs/platform-support.md:14]() | sandbox-exec (Seatbelt) [docs/platform-support.md:14]() |
| **Filesystem Control** | Landlock + bubblewrap [docs/platform-support.md:17]() | Seatbelt rules [docs/platform-support.md:17]() |
| **Syscall Filtering** | seccomp [docs/platform-support.md:16]() | Seatbelt [docs/platform-support.md:16]() |
| **Network Isolation** | Network namespace [docs/platform-support.md:22]() | N/A (Env vars only) [docs/platform-support.md:22]() |
| **Transparent Proxy** | ✅ (tun2socks + TUN) [docs/platform-support.md:19]() | ❌ [docs/platform-support.md:19]() |
| **Violation Monitoring** | eBPF [docs/platform-support.md:18]() | Seatbelt denial logs [docs/platform-support.md:18]() |
| **Learning Mode** | strace [docs/platform-support.md:27]() | eslogger (requires sudo) [docs/platform-support.md:27]() |
| **External Deps** | bwrap, socat, xdg-dbus-proxy [docs/platform-support.md:29]() | None (native tools) [docs/platform-support.md:29]() |

Sources: [docs/platform-support.md:10-29](), [internal/platform/platform.go:9-28]()

## Command Wrapping Flow

The following diagram shows how each platform wraps a user command with sandbox restrictions. The `Manager` entity coordinates this by detecting the platform and calling the respective implementation.

```mermaid
flowchart TB
    subgraph "Linux Implementation"
        L1["Detect Features<br/>(LinuxFeatures)"]
        L2["Build bwrap args<br/>(--unshare-net, --unshare-pid)"]
        L3["Generate seccomp filter"]
        L4["Build mounts<br/>(buildDenyByDefaultMounts)"]
        L5["Setup ProxyBridge<br/>(NewProxyBridge)"]
        L6["Setup DnsBridge<br/>(NewDnsBridge)"]
        L7["Apply Landlock"]
    end
    
    subgraph "macOS Implementation"
        M1["Build MacOSSandboxParams"]
        M2["Generate Seatbelt profile<br/>(GenerateSandboxProfile)"]
        M3["Generate read rules<br/>(file-read-data)"]
        M4["Generate write rules<br/>(file-write*)"]
        M5["Generate network rules<br/>(network-outbound)"]
        M6["Set proxy env vars<br/>(HTTP_PROXY)"]
        M7["Invoke sandbox-exec"]
    end
    
    L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    M1 --> M2 --> M3 --> M4 --> M5 --> M6 --> M7
```

**Linux Path:** The implementation builds a shell command that starts `bubblewrap` with namespace isolation, applies `seccomp` filtering, mounts filesystems, starts `socat` bridges for proxy connectivity, and applies `Landlock` [docs/platform-support.md:33-40]().

**macOS Path:** The implementation generates a Seatbelt profile string, configures proxy environment variables, and invokes `sandbox-exec -p` [docs/platform-support.md:48-50]().

Sources: [docs/platform-support.md:31-65](), [internal/platform/platform.go:17-28]()

## Code Entity Mapping

This diagram maps high-level platform concepts to the specific code entities used in the `greywall` implementation.

```mermaid
graph TB
    subgraph "Platform Detection"
        Detect["platform.Detect()"]
        Type["platform.Type (MacOS/Linux)"]
    end

    subgraph "Linux Core Entities"
        PB["ProxyBridge struct"]
        DB["DnsBridge struct"]
        RB["ReverseBridge struct"]
        LMon["LinuxMonitors struct"]
        StraceLog["ParseStraceLog()"]
    end
    
    subgraph "macOS Core Entities"
        MSParams["MacOSSandboxParams struct"]
        EsLog["ParseEsloggerLog()"]
        GenProf["GenerateSandboxProfile()"]
    end
    
    subgraph "Manager Logic"
        MGR["sandbox.Manager struct"]
        LearnL["generateLearnedTemplatePlatform (Linux)"]
        LearnM["generateLearnedTemplatePlatform (macOS)"]
    end
    
    Detect --> Type
    Type --> MGR
    MGR --> LearnL
    MGR --> LearnM
    LearnL --> StraceLog
    LearnM --> EsLog
    PB -.-> LearnL
```

**Key Implementation Details:**
- **Platform Detection:** The `platform.Detect()` function uses `runtime.GOOS` to identify the operating system [internal/platform/platform.go:17-28]().
- **Learning Mode:** On Linux, learning mode parses logs from `strace` [internal/sandbox/manager_linux.go:11-21](). On macOS, it uses `eslogger` and requires PID-based process tree filtering [internal/sandbox/manager_darwin.go:13-29]().
- **Bridges:** Linux uses `ProxyBridge`, `DnsBridge`, and `ReverseBridge` to facilitate communication across namespace boundaries [docs/platform-support.md:40-44]().

Sources: [internal/platform/platform.go:1-35](), [internal/sandbox/manager_linux.go:11-31](), [internal/sandbox/manager_darwin.go:13-41]()

## Filesystem Isolation

### Linux: Mount Namespaces + Landlock
Linux uses `bubblewrap` to create a new mount namespace. It whitelists system paths and the current working directory while masking sensitive files like `.env` using `--ro-bind` to mount rewritten files containing placeholders [docs/platform-support.md:33-36](), [docs/platform-support.md:58]().

### macOS: Seatbelt Profiles
macOS uses `sandbox-exec` with Seatbelt rules. Unlike Linux, macOS cannot perform bind-mount redirection. Consequently, when credential substitution is active, `.env` files are **denied entirely** in the sandbox profile, resulting in a permission-denied error if the process attempts to read them [docs/platform-support.md:56-62]().

Sources: [docs/platform-support.md:33-38](), [docs/platform-support.md:56-65]()

## Network Isolation

### Linux: Transparent Proxying
Linux creates a full network namespace (`unshare-net`). All traffic is captured via a `TUN` device and routed through `tun2socks` into the SOCKS5 proxy. A `socat` relay (DNS bridge) captures DNS queries and forwards them to the configured DNS server [docs/platform-support.md:39-40]().

### macOS: Environment Variables
macOS lacks network namespaces. Isolation is achieved by setting `ALL_PROXY` and `HTTP_PROXY` environment variables. The Seatbelt profile then restricts network access to only the proxy address [docs/platform-support.md:50]().

Sources: [docs/platform-support.md:39-40](), [docs/platform-support.md:48-50]()

## Next Steps

For detailed implementation information:

- **Linux Implementation:** See [Linux Sandboxing](#4.1) for details on bubblewrap, Landlock, seccomp, and eBPF.
- **macOS Implementation:** See [macOS Sandboxing](#4.2) for details on Seatbelt profiles and `eslogger`.
- **Network Architecture:** See [Network Architecture](#5) for deep dives into `greyproxy` and proxy bridges.
- **Learning Mode:** See [Learning Mode](#6.3) for how `strace` and `eslogger` are used to generate profiles.

---

# Page: Linux Sandboxing

# Linux Sandboxing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/linux-security-features.md](docs/linux-security-features.md)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_features.go](internal/sandbox/linux_features.go)

</details>



This document provides an overview of greywall's Linux sandbox implementation, explaining how multiple security technologies are integrated into a cohesive defense-in-depth architecture. For platform comparison and feature differences, see [Platform Implementations](#4).

The Linux implementation combines several kernel security features:
- **Process isolation** via bubblewrap namespaces (see [bubblewrap and Namespaces](#4.1.1))
- **Filesystem access control** via Landlock LSM (see [Landlock Filesystem Control](#4.1.2))
- **Syscall filtering** via seccomp-bpf (see [Seccomp Syscall Filtering](#4.1.3))
- **Real-time monitoring** via eBPF tracing (see [eBPF Violation Monitoring](#4.1.4))
- **Network isolation** via transparent proxying with tun2socks (see [Transparent Network Proxying](#4.1.5))

Each layer provides independent security controls with graceful fallback when features are unavailable [docs/linux-security-features.md:56-102]().

## Multi-Layer Security Architecture

The Linux sandbox applies multiple independent security layers to defend against different attack vectors. This diagram shows how the layers interact during command execution:

```mermaid
graph TB
    Command["User Command"]
    WrapCommand["WrapCommandLinuxWithOptions()"]
    
    subgraph "Layer 1: Process Isolation"
        Bwrap["bubblewrap"]
        PidNS["--unshare-pid<br/>PID namespace"]
        NetNS["--unshare-net<br/>Network namespace"]
        DieParent["--die-with-parent<br/>Lifecycle control"]
    end
    
    subgraph "Layer 2: Filesystem Isolation"
        MountModel["Mount Strategy"]
        DenyDefault["Deny-by-default:<br/>--tmpfs / + selective mounts"]
        Legacy["Legacy:<br/>--ro-bind / /"]
        LandlockWrapper["Landlock Wrapper<br/>kernel-enforced ACLs"]
    end
    
    subgraph "Layer 3: Syscall Filtering"
        Seccomp["SeccompFilter"]
        BPFGen["GenerateBPFFilter()"]
        BPFFile["BPF program file"]
        SeccompArg["--seccomp 3"]
    end
    
    subgraph "Layer 4: Network Control"
        ProxyBridge["ProxyBridge<br/>Unix socket relay"]
        DnsBridge["DnsBridge<br/>DNS relay"]
        Tun2Socks["tun2socks<br/>Transparent proxy"]
        NetworkSetup["Network namespace setup<br/>TUN device + routing"]
    end
    
    subgraph "Layer 5: Monitoring"
        EBPFMon["EBPFMonitor"]
        Bpftrace["bpftrace script"]
        Violations["Violation reports"]
    end
    
    Command --> WrapCommand
    WrapCommand --> Bwrap
    
    Bwrap --> PidNS
    Bwrap --> NetNS
    Bwrap --> DieParent
    
    WrapCommand --> MountModel
    MountModel --> DenyDefault
    MountModel --> Legacy
    MountModel --> LandlockWrapper
    
    WrapCommand --> Seccomp
    Seccomp --> BPFGen
    BPFGen --> BPFFile
    BPFFile --> SeccompArg
    SeccompArg --> Bwrap
    
    WrapCommand --> ProxyBridge
    WrapCommand --> DnsBridge
    ProxyBridge --> NetworkSetup
    DnsBridge --> NetworkSetup
    NetworkSetup --> Tun2Socks
    
    WrapCommand --> EBPFMon
    EBPFMon --> Bpftrace
    Bpftrace --> Violations
```

**Sources:** [internal/sandbox/linux.go:595-1193](), [docs/linux-security-features.md:10-18]()

## Command Wrapping Flow

The `WrapCommandLinux` function orchestrates the multi-layer sandbox construction. This sequence shows how configuration is transformed into a sandboxed command:

```mermaid
sequenceDiagram
    participant Caller
    participant WrapCmd["WrapCommandLinuxWithOptions"]
    participant Features["DetectLinuxFeatures"]
    participant Seccomp["SeccompFilter"]
    participant Mounts["buildDenyByDefaultMounts"]
    participant Bridges["Bridge Setup"]
    participant Shell["Shell Script"]
    
    Caller->>WrapCmd: config, command, bridges, options
    WrapCmd->>Features: Check kernel capabilities
    Features-->>WrapCmd: LinuxFeatures struct
    
    alt seccomp enabled
        WrapCmd->>Seccomp: NewSeccompFilter(debug)
        Seccomp->>Seccomp: GenerateBPFFilter()
        Seccomp-->>WrapCmd: filter file path
    end
    
    alt deny-by-default mode
        WrapCmd->>Mounts: buildDenyByDefaultMounts(cfg, cwd)
        Mounts-->>WrapCmd: bwrap mount args
    else legacy mode
        WrapCmd->>WrapCmd: --ro-bind / /
    end
    
    WrapCmd->>WrapCmd: Add namespace args<br/>--unshare-pid, --unshare-net
    
    alt transparent proxy
        WrapCmd->>Bridges: Bind Unix sockets
        WrapCmd->>Shell: Generate network setup script
        Note over Shell: ip tuntap add<br/>tun2socks start<br/>socat bridges
    end
    
    WrapCmd->>WrapCmd: Build final bwrap command
    WrapCmd-->>Caller: sandboxed command string
```

**Sources:** [internal/sandbox/linux.go:595-1193]()

## Core Data Structures

### LinuxSandboxOptions

The `LinuxSandboxOptions` struct controls which security features are enabled:

```go
type LinuxSandboxOptions struct {
	UseLandlock bool
	UseSeccomp bool
	UseEBPF bool
	Monitor bool
	Debug bool
	Learning bool
	StraceLogPath string
	RewrittenEnvFiles map[string]string
	AllowAudio bool
}
```

**Sources:** [internal/sandbox/linux.go:114-137]()

### Bridge Components

Three bridge types facilitate communication between the isolated sandbox and the host:

| Bridge Type | Purpose | Implementation |
|------------|---------|----------------|
| `ProxyBridge` | SOCKS5 proxy access | socat relay: Unix socket ↔ TCP proxy [internal/sandbox/linux.go:21-31]() |
| `DnsBridge` | DNS resolution | socat relay: UDP :53 ↔ Unix socket ↔ host DNS [internal/sandbox/linux.go:36-41]() |
| `ReverseBridge` | Inbound connections | socat relay: host TCP port ↔ Unix socket [internal/sandbox/linux.go:106-111]() |

Each bridge uses a randomly-generated Unix socket path in `/tmp` to prevent collisions [internal/sandbox/linux.go:53-56](), [internal/sandbox/linux.go:155-158]().

**Sources:** [internal/sandbox/linux.go:21-291]()

## Feature Detection System

The `LinuxFeatures` struct captures system capabilities with graceful fallback:

```mermaid
graph LR
    Detect["DetectLinuxFeatures()"]
    
    subgraph "Core Dependencies"
        Bwrap["HasBwrap<br/>bubblewrap"]
        Socat["HasSocat<br/>socat"]
    end
    
    subgraph "Kernel Features"
        Seccomp["HasSeccomp<br/>SeccompLogLevel"]
        Landlock["HasLandlock<br/>LandlockABI"]
        Kernel["KernelMajor<br/>KernelMinor"]
    end
    
    subgraph "Capabilities"
        EBPF["HasEBPF<br/>HasCapBPF<br/>HasCapRoot"]
        NetNS["CanUnshareNet"]
    end
    
    subgraph "Network Stack"
        Ip["HasIpCommand<br/>iproute2"]
        Tun["HasDevNetTun<br/>/dev/net/tun"]
        T2S["HasTun2Socks<br/>embedded binary"]
    end
    
    Detect --> Bwrap
    Detect --> Socat
    Detect --> Seccomp
    Detect --> Landlock
    Detect --> Kernel
    Detect --> EBPF
    Detect --> NetNS
    Detect --> Ip
    Detect --> Tun
    Detect --> T2S
    
    Bwrap --> MinReq["MinimumViable()"]
    Socat --> MinReq
    
    Landlock --> CanLL["CanUseLandlock()"]
    Ip --> CanTP["CanUseTransparentProxy()"]
    Tun --> CanTP
    NetNS --> CanTP
```

**Sources:** [internal/sandbox/linux_features.go:17-46](), [docs/linux-security-features.md:20-44]()

### Detection Methods

Feature detection uses multiple techniques:

**Kernel Version:** Parse kernel release string via `unix.Uname()` [internal/sandbox/linux_features.go:90-104]().

**Seccomp:** Test with `unix.Syscall(unix.SYS_PRCTL, unix.PR_GET_SECCOMP, ...)` [internal/sandbox/linux_features.go:106-124]().

**Landlock:** Query ABI version via `unix.Syscall(unix.SYS_LANDLOCK_CREATE_RULESET, 0, 0, LANDLOCK_CREATE_RULESET_VERSION)` [internal/sandbox/linux_features.go:126-165]().

**Network Namespaces:** Probe with test command: `bwrap --unshare-net --ro-bind / / -- /bin/true` [internal/sandbox/linux_features.go:207-218]().

**eBPF:** Check effective capabilities for `CAP_BPF` (bit 39) in `/proc/self/status` [internal/sandbox/linux_features.go:167-202]().

**Sources:** [internal/sandbox/linux_features.go:63-218]()

## Filesystem Isolation Models

Linux supports two filesystem isolation modes that are selected based on configuration:

### Deny-by-Default Mode

When `DefaultDenyRead: true` is set in the configuration, the sandbox starts with an empty root filesystem and selectively mounts only necessary paths:

```mermaid
graph TB
    Root["--tmpfs /<br/>Empty root"]
    
    subgraph "System Mounts"
        Usr["/usr - RO"]
        Etc["/etc - RO"]
        Lib["/lib* - RO"]
        Sys["/sys - RO"]
        Symlinks["Symlinks<br/>/bin → usr/bin<br/>/lib64 → usr/lib"]
    end
    
    subgraph "Special Filesystems"
        Dev["--dev-bind /dev /dev"]
        Proc["--proc /proc"]
        Tmp["--tmpfs /tmp"]
    end
    
    subgraph "User Paths"
        CWD["CWD - RW<br/>Project directory"]
        Tools["Tool paths - RO<br/>~/.cargo, ~/.npm, etc"]
        AllowRead["AllowRead paths - RO<br/>User-specified"]
    end
    
    subgraph "Protected"
        Masked["Sensitive files masked<br/>.env → empty file"]
        Mandatory["Mandatory deny<br/>.bashrc, .ssh/config - RO"]
    end
    
    Root --> Usr
    Root --> Etc
    Root --> Lib
    Root --> Sys
    Root --> Symlinks
    Root --> Dev
    Root --> Proc
    Root --> Tmp
    Root --> CWD
    Root --> Tools
    Root --> AllowRead
    Root --> Masked
    Root --> Mandatory
```

The mount order matters: later mounts can override earlier ones. This is used to protect sensitive files by binding an empty file over them [internal/sandbox/linux.go:559-575]().

**Sources:** [internal/sandbox/linux.go:398-578](), [docs/linux-security-features.md:100-118]()

### Legacy Mode

When `DefaultDenyRead: false`, the entire root filesystem is bound read-only, then specific paths are made writable [internal/sandbox/linux.go:704-707]().

## Deny-by-Default Mount Construction

The `buildDenyByDefaultMounts` function implements the sophisticated mount logic [internal/sandbox/linux.go:398-578]().

**Key Implementation Details:**

**Symlink Handling:** System directories like `/bin → usr/bin` must be recreated as symlinks inside the sandbox [internal/sandbox/linux.go:440-452]().

**Intermediary Directories:** The function ensures parent directories exist before binding deep paths [internal/sandbox/linux.go:478-485]().

**Device Separation Check:** `sameDevice()` detects cross-filesystem mounts and handles them specially to ensure correct path visibility [internal/sandbox/linux.go:723-774]().

**Sources:** [internal/sandbox/linux.go:398-578]()

## Network Isolation Architecture

Network isolation on Linux uses a combination of network namespaces and transparent proxying [docs/linux-security-features.md:79-88]().

**Network Namespace Setup:**

Inside the sandbox, a shell script configures the isolated network [internal/sandbox/linux.go:989-1050]():
- `ip tuntap add dev tun0 mode tun`
- `ip addr add 198.18.0.1/15 dev tun0`
- `ip route add default via 198.18.0.1 dev tun0`
- Starts `tun2socks` and `socat` bridges to route traffic to the host-side `greyproxy`.

**Sources:** [internal/sandbox/linux.go:989-1050]()

## Security Layer Details

### Seccomp Syscall Filter

The `SeccompFilter` generates a BPF program that blocks dangerous syscalls like `ptrace`, `bpf`, and `mount` [docs/linux-security-features.md:152-169](). It also specifically blocks `TIOCSTI` to prevent terminal injection [internal/sandbox/linux_seccomp.go:28-216]().

### eBPF Monitoring

The `EBPFMonitor` uses bpftrace to trace syscall failures in real-time, filtering by PID to track the sandbox process tree [docs/linux-security-features.md:70-77]().

### Landlock Integration

When available (kernel 5.13+), greywall applies Landlock filesystem restrictions via an embedded wrapper approach [docs/linux-security-features.md:46-54]().

## Learning Mode

Learning mode runs a permissive sandbox with `strace` tracing to discover filesystem access patterns [internal/sandbox/linux.go:666-691]().

**Sources:** [internal/sandbox/linux.go:666-691](), [docs/experience.md:15-26]()

## Error Handling and Fallback

The sandbox implements graceful degradation when features like `Landlock` or `eBPF` are unavailable [docs/linux-security-features.md:56-88]().

**Sources:** [internal/sandbox/linux_features.go:274-277](), [docs/linux-security-features.md:56-102]()

---

# Page: bubblewrap and Namespaces

# bubblewrap and Namespaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_features.go](internal/sandbox/linux_features.go)
- [internal/sandbox/linux_stub.go](internal/sandbox/linux_stub.go)

</details>



## Purpose and Scope

This page explains how greywall uses bubblewrap (bwrap) to create isolated Linux namespaces for sandboxed processes. It covers namespace creation (PID, network, mount), the mount structure inside the sandbox, and how bwrap commands are constructed. For filesystem access control beyond mount-based restrictions, see [Landlock Filesystem Control](#4.1.2). For syscall filtering, see [Seccomp Syscall Filtering](#4.1.3). For network routing through the proxy, see [Transparent Network Proxying](#4.1.5).

## Overview of bubblewrap

Bubblewrap (bwrap) is a lightweight container runtime that creates isolated namespaces without requiring root privileges. Greywall uses bwrap as the foundation of its Linux sandbox implementation because it:

- Creates new PID, network, and mount namespaces without root
- Provides granular control over filesystem visibility through bind mounts
- Supports capability management (CAP_NET_ADMIN, CAP_NET_BIND_SERVICE)
- Works in unprivileged mode (no setuid binary required)
- Integrates cleanly with other security layers (seccomp, Landlock)

The `WrapCommandLinux` and `WrapCommandLinuxWithOptions` functions in [internal/sandbox/linux.go:595-1178]() construct bwrap commands that wrap user commands in an isolated environment.

**Sources:** [internal/sandbox/linux.go:595-610]()

## Namespace Isolation

### Namespace Types and Isolation Boundaries

Greywall creates three types of Linux namespaces to isolate sandboxed processes:

```mermaid
graph TB
    subgraph "Host System"
        HostPID["Host PID Namespace<br/>PID 1 = systemd"]
        HostNet["Host Network Namespace<br/>eth0, wlan0"]
        HostMount["Host Mount Namespace<br/>Real filesystem"]
    end
    
    subgraph "Sandbox Container"
        BwrapProcess["bwrap Process<br/>(PID 12345 on host)"]
        
        subgraph "PID Namespace"
            SandboxInit["PID 1 (init)<br/>bash -c script"]
            UserCmd["User Command<br/>PID 2+"]
        end
        
        subgraph "Network Namespace"
            LoopbackOnly["lo: 127.0.0.1<br/>tun0: 198.18.0.1"]
            NoExternal["No external interfaces"]
        end
        
        subgraph "Mount Namespace"
            TmpfsRoot["tmpfs /<br/>(empty root)"]
            SystemMounts["Selective bind mounts:<br/>/usr, /lib, /etc (RO)"]
            CWDMount["CWD (RW)"]
        end
    end
    
    BwrapProcess -->|"--unshare-pid"| SandboxInit
    BwrapProcess -->|"--unshare-net"| LoopbackOnly
    BwrapProcess -->|"--tmpfs /"| TmpfsRoot
    
    SandboxInit --> UserCmd
    TmpfsRoot --> SystemMounts
    SystemMounts --> CWDMount
```

**Sources:** [internal/sandbox/linux.go:626-645]()

### PID Namespace

The PID namespace isolates process identifiers, preventing sandboxed processes from discovering or interacting with processes on the host.

| Feature | Configuration | Effect |
|---------|--------------|--------|
| Namespace flag | `--unshare-pid` | Creates new PID namespace |
| Init process | bash shell | Becomes PID 1 in namespace |
| Child visibility | Isolated | Sandboxed processes cannot see host PIDs |
| Parent visibility | One-way | Host can see sandbox PIDs (as children of bwrap) |
| Process cleanup | `--die-with-parent` | Entire namespace dies when bwrap exits |

The `--unshare-pid` flag is unconditionally applied at [internal/sandbox/linux.go:645](). Inside the new PID namespace, the bash shell that runs the inner script becomes PID 1 (the init process), and the user's command becomes PID 2 or higher.

**Important:** Greywall does NOT use `--new-session` because it breaks terminal resize signals (SIGWINCH) for interactive applications. The TIOCSTI attack vector that `--new-session` would mitigate is instead blocked by the seccomp filter (see [Seccomp Syscall Filtering](#4.1.3)).

**Sources:** [internal/sandbox/linux.go:626-645]()

### Network Namespace

The network namespace creates a completely isolated network stack with no external connectivity by default.

```mermaid
graph LR
    subgraph "Host Network Namespace"
        HostInterfaces["eth0: 192.168.1.x<br/>wlan0: 10.0.0.x"]
    end
    
    subgraph "Sandbox Network Namespace"
        LoSetup["Loopback Setup<br/>ip link set lo up"]
        TunSetup["TUN Device<br/>tun0: 198.18.0.1/15"]
        DefaultRoute["Default Route<br/>via 198.18.0.1"]
        
        LoSetup --> TunSetup
        TunSetup --> DefaultRoute
    end
    
    HostInterfaces -.X Network isolated X.-> LoSetup
```

The network namespace is created with `--unshare-net` at [internal/sandbox/linux.go:640](). However, this feature is conditionally enabled because it can fail in containerized environments (Docker, GitHub Actions) that don't grant `CAP_NET_ADMIN`.

**Feature detection** happens in `detectNetworkNamespace()` at [internal/sandbox/linux_features.go:207-218](), which tests if `bwrap --unshare-net --ro-bind / / -- /bin/true` succeeds. The result is stored in `LinuxFeatures.CanUnshareNet`.

| Environment | CanUnshareNet | Behavior |
|-------------|---------------|----------|
| Native Linux | ✓ | Full network isolation + transparent proxy |
| Docker container | ✗ | Skips `--unshare-net`, uses proxy env vars |
| GitHub Actions | ✗ | Skips `--unshare-net`, uses proxy env vars |
| Ubuntu 24.04 (default) | ✗ | Needs `kernel.apparmor_restrict_unprivileged_userns=0` |

Inside the network namespace, the sandbox sets up:
1. Loopback interface (`ip link set lo up`)
2. TUN device for transparent proxying (when available)
3. Default route pointing to the TUN device

This configuration is built in the inner script at [internal/sandbox/linux.go:1004-1024]().

**Sources:** [internal/sandbox/linux.go:638-643](), [internal/sandbox/linux_features.go:207-218]()

### Mount Namespace

The mount namespace controls filesystem visibility inside the sandbox. Greywall supports two modes:

#### Deny-by-Default Mode (Recommended)

When `cfg.Filesystem.DefaultDenyRead` is true, the sandbox starts with an empty root and selectively mounts only necessary paths:

```mermaid
graph TB
    EmptyRoot["--tmpfs /<br/>(empty root filesystem)"]
    
    subgraph "System Paths (Read-Only)"
        UsrMount["/usr"]
        EtcMount["/etc"]
        LibMount["/lib, /lib64"]
        OptMount["/opt"]
        RunMount["/run"]
    end
    
    subgraph "Symlinks (Merged-usr)"
        BinLink["--symlink usr/bin /bin"]
        SbinLink["--symlink usr/sbin /sbin"]
        LibLink["--symlink usr/lib /lib"]
    end
    
    subgraph "Special Filesystems"
        DevMount["--dev-bind /dev /dev"]
        ProcMount["--proc /proc"]
        TmpMount["--tmpfs /tmp"]
    end
    
    subgraph "Working Directory"
        CWDMount["--bind <cwd> <cwd><br/>(read-write)"]
        MaskedFiles["Sensitive files masked:<br/>.env, .git/config"]
    end
    
    EmptyRoot --> UsrMount
    EmptyRoot --> EtcMount
    EmptyRoot --> BinLink
    EmptyRoot --> DevMount
    EmptyRoot --> CWDMount
    
    CWDMount --> MaskedFiles
```

The `buildDenyByDefaultMounts()` function at [internal/sandbox/linux.go:401-578]() constructs this structure:

1. **Empty root:** `--tmpfs /` creates an empty tmpfs at the root
2. **System paths:** Bind mount critical directories read-only (e.g., `/usr`, `/etc`)
3. **Symlink recreation:** Detect symlinks (e.g., `/bin -> usr/bin`) and recreate them with `--symlink`
4. **CWD mount:** Bind mount the current working directory read-write
5. **Tool paths:** Bind mount user tooling paths (e.g., `~/.cargo`, `~/.npm`) read-only
6. **User allowRead:** Bind mount paths from `cfg.Filesystem.AllowRead` read-only
7. **Sensitive file masking:** Overlay sensitive files (`.env`, `.git/config`) with empty files

**Symlink handling** is critical on modern distributions (Arch, Fedora, Ubuntu 22.04+) that use merged-usr, where `/bin`, `/sbin`, `/lib`, `/lib64` are symlinks to directories under `/usr`. The code checks each system path with `isSymlink()` at [internal/sandbox/linux.go:417-426]() and uses `--symlink` for symlinks or `--ro-bind` for real directories.

**Sources:** [internal/sandbox/linux.go:401-578](), [internal/sandbox/linux.go:698-707]()

#### Legacy Mode

When `DefaultDenyRead` is false, the sandbox binds the entire root filesystem read-only:

```mermaid
graph TB
    FullRoot["--ro-bind / /<br/>(entire root read-only)"]
    
    subgraph "Writable Overrides"
        WritePaths["--bind <path> <path><br/>for allowWrite paths"]
    end
    
    subgraph "Deny Overrides"
        DenyRead["--tmpfs <dir><br/>or --ro-bind /dev/null <file>"]
        DenyWrite["--ro-bind <path> <path>"]
    end
    
    FullRoot --> WritePaths
    FullRoot --> DenyRead
    FullRoot --> DenyWrite
```

This mode is simpler but less secure because it exposes the entire filesystem by default, then selectively hides paths. It's provided for backward compatibility and debugging.

**Sources:** [internal/sandbox/linux.go:706]()

## Mount Structure Implementation

### Intermediary Directory Creation

When mounting a path deep in the filesystem (e.g., `/home/user/.cargo/bin`), bwrap needs all parent directories to exist. The `intermediaryDirs()` function at [internal/sandbox/linux.go:342-355]() generates the chain of parent directories:

```go
intermediaryDirs("/", "/home/user/.cargo/bin")
// Returns: ["/home", "/home/user", "/home/user/.cargo", "/home/user/.cargo/bin"]
```

These directories are created with `--dir` flags before the final `--bind` mount.

**Sources:** [internal/sandbox/linux.go:342-355](), [internal/sandbox/linux.go:435-442]()

### Sensitive File Masking

In deny-by-default mode, sensitive files within the CWD are masked to prevent malicious code from exfiltrating credentials:

| File Pattern | Masking Method | Location |
|--------------|----------------|----------|
| `.env` | `--ro-bind /tmp/greywall/empty <cwd>/.env` | [internal/sandbox/linux.go:559-575]() |
| `.git/config` | Same as above | [internal/sandbox/linux.go:384]() |
| `.git/hooks` | Same as above | [internal/sandbox/linux.go:381]() |

The masking uses an empty regular file (`/tmp/greywall/empty`) instead of `/dev/null` because Landlock's `READ_FILE` permission doesn't cover character devices, causing "Permission denied" errors.

**Sources:** [internal/sandbox/linux.go:559-575](), [internal/sandbox/linux.go:359-396]()

### Special Filesystem Mounts

Three special filesystems are mounted after the basic directory structure:

```mermaid
graph LR
    DevMount["--dev-bind /dev /dev"]
    ProcMount["--proc /proc"]
    TmpMount["--tmpfs /tmp"]
    
    DevMount -->|"Preserves device permissions"| DeviceFiles["/dev/tty<br/>/dev/null<br/>/dev/random"]
    ProcMount -->|"Process information"| ProcFiles["/proc/self<br/>/proc/cpuinfo"]
    TmpMount -->|"Writable temp space"| TempFiles["Application temp files"]
```

**Device bind mount:** Uses `--dev-bind` instead of `--dev` (minimal devtmpfs) because the minimal devtmpfs has permission issues when bwrap is setuid. Mounted at [internal/sandbox/linux.go:712]().

**/proc mount:** Provides process information inside the PID namespace. Mounted at [internal/sandbox/linux.go:713]().

**/tmp mount:** Creates writable temporary storage. Must be mounted AFTER strace log bind-mount in learning mode. Mounted at [internal/sandbox/linux.go:716]().

**Sources:** [internal/sandbox/linux.go:710-721]()

### Resolv.conf Symlink Resolution

On some systems (e.g., WSL), `/etc/resolv.conf` is a symlink to a file on a different filesystem (e.g., `/mnt/wsl/resolv.conf`). The code detects this and creates intermediary directories to make the target reachable:

```mermaid
graph TB
    ResolvSymlink["/etc/resolv.conf<br/>(symlink)"]
    Target["/mnt/wsl/resolv.conf<br/>(on different device)"]
    
    MountBoundary["First parent on different device:<br/>--tmpfs /mnt"]
    SubDirs["Subdirectories:<br/>--dir /mnt/wsl"]
    BindTarget["--ro-bind /mnt/wsl/resolv.conf /mnt/wsl/resolv.conf"]
    
    ResolvSymlink -.-> Target
    Target --> MountBoundary
    MountBoundary --> SubDirs
    SubDirs --> BindTarget
```

The logic at [internal/sandbox/linux.go:725-774]() handles this by:
1. Detecting if `/etc/resolv.conf` is a symlink to a different filesystem
2. Creating intermediary directories between `/` and the target
3. Using `--tmpfs` at the mount boundary, `--dir` for subdirectories
4. Binding the real file at the target path

**Sources:** [internal/sandbox/linux.go:725-774]()

## Command Construction Process

### Argument Building Flow

```mermaid
graph TB
    Start["WrapCommandLinuxWithOptions"]
    
    CheckBwrap["Check bwrap availability"]
    Features["DetectLinuxFeatures()"]
    
    BaseArgs["Base args:<br/>--die-with-parent"]
    
    NamespaceArgs["Namespace args:<br/>--unshare-pid<br/>--unshare-net (conditional)"]
    
    SeccompFilter["Generate seccomp filter<br/>(if enabled)"]
    
    MountMode{{"DefaultDenyRead?"}}
    DenyMode["buildDenyByDefaultMounts()"]
    LegacyMode["--ro-bind / /"]
    
    SpecialFS["--dev-bind /dev /dev<br/>--proc /proc<br/>--tmpfs /tmp"]
    
    WritePaths["Writable paths:<br/>--bind <path> <path>"]
    
    DenyPaths["Deny paths:<br/>--tmpfs or --ro-bind /dev/null"]
    
    ProxyBridge["Proxy bridge socket:<br/>--bind <socket> <socket>"]
    
    InnerScript["Build inner script:<br/>network setup + user command"]
    
    FinalCmd["ShellQuote(bwrapArgs)"]
    
    Start --> CheckBwrap
    CheckBwrap --> Features
    Features --> BaseArgs
    BaseArgs --> NamespaceArgs
    NamespaceArgs --> SeccompFilter
    SeccompFilter --> MountMode
    MountMode -->|"true"| DenyMode
    MountMode -->|"false"| LegacyMode
    DenyMode --> SpecialFS
    LegacyMode --> SpecialFS
    SpecialFS --> WritePaths
    WritePaths --> DenyPaths
    DenyPaths --> ProxyBridge
    ProxyBridge --> InnerScript
    InnerScript --> FinalCmd
```

**Sources:** [internal/sandbox/linux.go:607-1178]()

### Inner Script Structure

The inner script runs inside the sandbox and sets up additional isolation layers:

```mermaid
graph TB
    ExportVar["export GREYWALL_SANDBOX=1"]
    
    NetworkSetup["Network setup:<br/>ip link set lo up<br/>ip tuntap add dev tun0<br/>socat bridges"]
    
    Cleanup["cleanup() function:<br/>kill background jobs"]
    TrapExit["trap cleanup EXIT"]
    
    Delay["sleep 0.3<br/>(wait for services)"]
    
    UserCmd["Run user command"]
    
    ExportVar --> NetworkSetup
    NetworkSetup --> Cleanup
    Cleanup --> TrapExit
    TrapExit --> Delay
    Delay --> UserCmd
```

The script is built at [internal/sandbox/linux.go:989-1133]() and includes:

1. **Environment marker:** `GREYWALL_SANDBOX=1` indicates running inside sandbox
2. **Network setup:** Configure loopback, TUN device, socat bridges (see [Transparent Network Proxying](#4.1.5))
3. **Cleanup handler:** Kill background processes (socat, tun2socks) on exit
4. **Delay:** Brief sleep to ensure network services are ready
5. **User command:** Execute the wrapped command

**Sources:** [internal/sandbox/linux.go:989-1133]()

### Final Command Assembly

The complete command structure looks like:

```bash
exec 3<$SECCOMP_FILTER_PATH; \
bwrap \
  --die-with-parent \
  --unshare-net \
  --unshare-pid \
  --seccomp 3 \
  --tmpfs / \
  --symlink usr/bin /bin \
  --ro-bind /usr /usr \
  --bind /home/user/project /home/user/project \
  --dev-bind /dev /dev \
  --proc /proc \
  --tmpfs /tmp \
  --bind /tmp/greywall-proxy-abc123.sock /tmp/greywall-proxy-abc123.sock \
  -- /bin/bash -c 'export GREYWALL_SANDBOX=1; ...'
```

The seccomp filter is passed via file descriptor 3, opened before bwrap execution. This is constructed at [internal/sandbox/linux.go:1170-1175]().

**Sources:** [internal/sandbox/linux.go:1167-1177]()

## Feature Detection and Fallbacks

### Capability Matrix

The `LinuxFeatures` struct tracks available capabilities:

| Feature | Detection Method | Fallback Behavior |
|---------|------------------|-------------------|
| `HasBwrap` | `exec.LookPath("bwrap")` | Return error (required) |
| `HasSocat` | `exec.LookPath("socat")` | Return error (required) |
| `CanUnshareNet` | Test `bwrap --unshare-net` | Skip `--unshare-net`, use proxy env vars |
| `HasSeccomp` | `prctl(PR_GET_SECCOMP)` | Skip seccomp filter |
| `HasLandlock` | `landlock_create_ruleset` syscall | Skip Landlock wrapper |
| `HasEBPF` | Check CAP_BPF or root | Skip eBPF monitoring |
| `HasIpCommand` | `exec.LookPath("ip")` | Skip transparent proxy |
| `HasDevNetTun` | `os.Stat("/dev/net/tun")` | Skip transparent proxy |

Detection happens once at [internal/sandbox/linux_features.go:55-61]() and results are cached in a global variable with `sync.Once`.

**Sources:** [internal/sandbox/linux_features.go:47-88]()

### Graceful Degradation

When features are unavailable, greywall degrades gracefully:

```mermaid
graph TB
    FullFeatures["All Features Available"]
    NoNetNS["No Network Namespace"]
    NoTUN["No TUN Device"]
    Minimal["Minimal: bwrap + socat"]
    
    FullFeatures -->|"CanUnshareNet=false"| NoNetNS
    FullFeatures -->|"HasDevNetTun=false"| NoTUN
    NoNetNS --> Minimal
    NoTUN --> Minimal
    
    FullFeatures -.->|"Isolation Level"| L1["Complete:<br/>PID + Network + Mount<br/>+ Transparent Proxy"]
    NoNetNS -.-> L2["Reduced:<br/>PID + Mount<br/>+ Proxy Env Vars"]
    NoTUN -.-> L3["Reduced:<br/>PID + Network + Mount<br/>+ Proxy Env Vars"]
    Minimal -.-> L4["Basic:<br/>PID + Mount<br/>+ Proxy Env Vars"]
```

The degradation logic is at [internal/sandbox/linux.go:638-643]() for network namespace and [internal/sandbox/linux.go:992-1057]() for transparent proxy setup.

**Sources:** [internal/sandbox/linux.go:638-643](), [internal/sandbox/linux.go:992-1057](), [internal/sandbox/linux_features.go:221-255]()

### Ubuntu 24.04 AppArmor Issue

Ubuntu 24.04 introduced `kernel.apparmor_restrict_unprivileged_userns` which prevents network namespace creation. The `PrintDependencyStatus()` function in `internal/sandbox/linux_features.go` detects this and provides remediation steps:

```bash
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
echo 'kernel.apparmor_restrict_unprivileged_userns=0' | sudo tee /etc/sysctl.d/99-greywall-userns.conf
```

**Sources:** [internal/sandbox/linux_features.go:207-218]()

---

# Page: Landlock Filesystem Control

# Landlock Filesystem Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/command.go](internal/sandbox/command.go)
- [internal/sandbox/command_test.go](internal/sandbox/command_test.go)
- [internal/sandbox/integration_linux_test.go](internal/sandbox/integration_linux_test.go)
- [internal/sandbox/integration_test.go](internal/sandbox/integration_test.go)
- [internal/sandbox/linux_landlock.go](internal/sandbox/linux_landlock.go)
- [internal/sandbox/linux_landlock_stub.go](internal/sandbox/linux_landlock_stub.go)

</details>



This page describes greywall's use of the Landlock LSM (Linux Security Module) for kernel-enforced filesystem access control on Linux. Landlock provides mandatory access control (MAC) at the kernel level, complementing the mount-based restrictions established by bubblewrap. For information about the overall Linux sandboxing architecture, see [Linux Sandboxing](4.1). For bubblewrap's mount namespace isolation, see [bubblewrap and Namespaces](4.1.1).

## Purpose and Scope

Landlock enforces filesystem access control policies at the kernel level, providing a second layer of defense beyond bubblewrap's mount-based isolation. While bubblewrap creates a restricted filesystem view using mount namespaces and bind mounts, Landlock enforces access rules that cannot be bypassed even if a process discovers paths outside the intended filesystem tree. This defense-in-depth approach ensures that filesystem restrictions remain effective even if mount-based isolation is circumvented.

Landlock is available on Linux kernel 5.13 and newer, with additional features added in later versions (ABI v1-v5). Greywall detects the available Landlock ABI version and gracefully falls back to mount-based isolation on older kernels.

## Landlock in the Linux Sandbox Stack

Landlock operates as a kernel-level access control layer that works alongside bubblewrap's namespace and mount isolation:

```mermaid
graph TB
    subgraph "Sandboxed_Process"
        APP["Application_attempting_filesystem_access"]
    end
    
    subgraph "Kernel_Enforcement_Layers"
        LANDLOCK["Landlock LSM<br/>SYS_LANDLOCK_RESTRICT_SELF<br/>kernel-enforced ACLs"]
        VFS["VFS Layer<br/>path resolution"]
        FS["Filesystem<br/>actual storage"]
    end
    
    subgraph "Namespace_Isolation"
        MNTNS["Mount Namespace<br/>bwrap --tmpfs /<br/>--ro-bind, --bind"]
        BWRAP["bubblewrap<br/>PID 1 in sandbox"]
    end
    
    subgraph "Configuration"
        CFG["config.FilesystemConfig<br/>AllowRead, AllowWrite<br/>DenyRead, DenyWrite"]
        RULESET["sandbox.LandlockRuleset<br/>fd from landlock_create_ruleset"]
    end
    
    APP --> LANDLOCK
    LANDLOCK --> VFS
    VFS --> MNTNS
    MNTNS --> FS
    
    BWRAP --> MNTNS
    
    CFG --> RULESET
    RULESET --> LANDLOCK
```

**Sources:** [internal/sandbox/linux_landlock.go:18-206](), [internal/sandbox/linux_landlock.go:21-46]()

The enforcement sequence works as follows:

1. **Configuration Phase**: The `config.FilesystemConfig` structure specifies allowed/denied paths [internal/sandbox/linux_landlock.go:156-191]().
2. **Ruleset Creation**: `LandlockRuleset` translates config into kernel rules via syscalls [internal/sandbox/linux_landlock.go:237-276]().
3. **Application Phase**: `SYS_LANDLOCK_RESTRICT_SELF` applies the ruleset to the process [internal/sandbox/linux_landlock.go:457-484]().
4. **Runtime Enforcement**: Every filesystem operation is checked by Landlock LSM before VFS access.
5. **Mount Namespace**: After passing Landlock checks, operations are constrained by bwrap's mount view.

This layered approach provides multiple independent security boundaries.

## LandlockRuleset Type and Lifecycle

The `LandlockRuleset` struct manages the lifecycle of a Landlock restriction policy:

```mermaid
stateDiagram-v2
    [*] --> Created: "NewLandlockRuleset()"
    Created --> Initialized: "Initialize()"
    Initialized --> Rules_Added: "AllowRead() / AllowWrite()"
    Rules_Added --> Rules_Added: "more path rules"
    Rules_Added --> Applied: "Apply()"
    Applied --> [*]: "process exec"
    
    note right of Created
        rulesetFd = -1
        abiVersion detected
    end note
    
    note right of Initialized
        SYS_LANDLOCK_CREATE_RULESET
        rulesetFd > 0
    end note
    
    note right of Rules_Added
        SYS_LANDLOCK_ADD_RULE
        LANDLOCK_RULE_PATH_BENEATH
    end note
    
    note right of Applied
        PR_SET_NO_NEW_PRIVS
        SYS_LANDLOCK_RESTRICT_SELF
    end note
```

**Sources:** [internal/sandbox/linux_landlock.go:208-235](), [internal/sandbox/linux_landlock.go:237-276](), [internal/sandbox/linux_landlock.go:457-484]()

### Key Fields and Methods

| Field/Method | Type | Purpose |
|--------------|------|---------|
| `rulesetFd` | `int` | File descriptor from `landlock_create_ruleset` syscall [internal/sandbox/linux_landlock.go:210-210]() |
| `abiVersion` | `int` | Detected Landlock ABI version (1-5) [internal/sandbox/linux_landlock.go:211-211]() |
| `initialized` | `bool` | Whether `Initialize()` has been called [internal/sandbox/linux_landlock.go:212-212]() |
| `Initialize()` | method | Creates ruleset via syscall, sets up access rights [internal/sandbox/linux_landlock.go:237-276]() |
| `AllowRead(path)` | method | Adds READ_FILE + READ_DIR + EXECUTE rights [internal/sandbox/linux_landlock.go:321-331]() |
| `AllowWrite(path)` | method | Adds WRITE_FILE + MAKE_* + REMOVE_* rights [internal/sandbox/linux_landlock.go:333-346]() |
| `Apply()` | method | Sets NO_NEW_PRIVS and restricts self [internal/sandbox/linux_landlock.go:457-484]() |

**Sources:** [internal/sandbox/linux_landlock.go:208-235](), [internal/sandbox/linux_landlock.go:321-354]()

The ruleset operates on a deny-by-default model: once applied with `Apply()`, all filesystem access is blocked except paths explicitly allowed.

## ABI Version Support and Access Rights

Landlock has evolved across kernel versions, adding new access rights in each ABI version. Greywall detects the available ABI and adjusts the `handledAccessFS` bitmask accordingly:

```mermaid
graph LR
    subgraph "Kernel_Version_Detection"
        DETECT["DetectLinuxFeatures()"]
        ABI["LandlockABI field (1-5)"]
    end
    
    subgraph "ABI_v1_5.13"
        V1_RIGHTS["EXECUTE<br/>READ_FILE, WRITE_FILE<br/>READ_DIR<br/>REMOVE_FILE, REMOVE_DIR<br/>MAKE_CHAR, MAKE_DIR, MAKE_REG<br/>MAKE_SOCK, MAKE_FIFO<br/>MAKE_BLOCK, MAKE_SYM"]
    end
    
    subgraph "ABI_v2_5.19"
        V2_RIGHTS["+ REFER<br/>cross-directory renames"]
    end
    
    subgraph "ABI_v3_6.2"
        V3_RIGHTS["+ TRUNCATE<br/>ftruncate operations"]
    end
    
    subgraph "ABI_v5_6.7"
        V5_RIGHTS["+ IOCTL_DEV<br/>ioctl on device files"]
    end
    
    DETECT --> ABI
    ABI --> V1_RIGHTS
    V1_RIGHTS --> V2_RIGHTS
    V2_RIGHTS --> V3_RIGHTS
    V3_RIGHTS --> V5_RIGHTS
```

**Sources:** [internal/sandbox/linux_landlock.go:278-313]()

### Access Rights Mapping

The `getHandledAccessFS()` method builds the access rights bitmask based on detected ABI version [internal/sandbox/linux_landlock.go:278-313]():

| Access Right | ABI Version | Purpose |
|--------------|-------------|---------|
| `EXECUTE` | v1 | Execute files |
| `WRITE_FILE` | v1 | Modify file contents |
| `READ_FILE` | v1 | Read file contents |
| `READ_DIR` | v1 | List directory entries |
| `REFER` | v2 | Rename/link across directories |
| `TRUNCATE` | v3 | Truncate files |
| `IOCTL_DEV` | v5 | ioctl on device files |

**Sources:** [internal/sandbox/linux_landlock.go:278-313]()

## Path Rule Semantics and PATH_BENEATH

Landlock uses the `LANDLOCK_RULE_PATH_BENEATH` rule type, which grants access to a path and all its descendants [internal/sandbox/linux_landlock.go:440-440]().

### Path Resolution Process

The `addPathRule()` method performs several steps to safely add a rule:

1. **Normalize**: Convert to absolute path [internal/sandbox/linux_landlock.go:374-374]()
2. **Resolve Symlinks**: Use `filepath.EvalSymlinks()` to follow symbolic links [internal/sandbox/linux_landlock.go:377-377]()
3. **Open with O_PATH**: Get a file descriptor without opening the file [internal/sandbox/linux_landlock.go:394-394]()
4. **fstat Check**: Determine if path is directory or file [internal/sandbox/linux_landlock.go:401-401]()
5. **Filter Rights**: Remove directory-only rights for non-directory paths [internal/sandbox/linux_landlock.go:406-426]()
6. **Add Rule**: Call `SYS_LANDLOCK_ADD_RULE` with the fd [internal/sandbox/linux_landlock.go:440-440]()

**Sources:** [internal/sandbox/linux_landlock.go:356-455]()

## Configuration to Rules Translation

`ApplyLandlockFromConfig()` is the main entry point that translates greywall's configuration into Landlock rules [internal/sandbox/linux_landlock.go:21-21]().

### Default System Paths

The following paths receive read+execute access by default:
`/usr`, `/lib`, `/lib64`, `/lib32`, `/bin`, `/sbin`, `/etc`, `/proc`, `/sys`, `/run`, `/var/lib`, `/var/cache`, `/opt` [internal/sandbox/linux_landlock.go:49-63]().

### Special Path Handling

| Path Type | Access Mode | Rationale |
|-----------|-------------|-----------|
| `/dev` | read+write | Character devices like `/dev/null`, `/dev/zero` [internal/sandbox/linux_landlock.go:143-145]() |
| `/tmp` | read+write | Temporary files needed by many programs [internal/sandbox/linux_landlock.go:137-139]() |
| CWD | read+write | Project workspace [internal/sandbox/linux_landlock.go:85-89]() |
| Sockets | read+write | Communication with proxy/DNS bridges [internal/sandbox/linux_landlock.go:148-153]() |

**Sources:** [internal/sandbox/linux_landlock.go:18-206]()

### Deny-by-Default Mode

When `config.FilesystemConfig.IsDefaultDenyRead()` is true, only specific tooling paths are allowed in the home directory, such as `~/.cache`, `~/.npm`, and shell configs like `~/.bashrc` [internal/sandbox/linux_landlock.go:96-134]().

## Glob Pattern Expansion

The `ExpandGlobPatterns()` function optimizes glob pattern expansion for Landlock's PATH_BENEATH semantics [internal/sandbox/linux_landlock.go:496-644]().

| Pattern | Optimization | Rationale |
|---------|--------------|-----------|
| `dir/**` | Just `dir` | PATH_BENEATH covers descendants [internal/sandbox/linux_landlock.go:547-557]() |
| `**/pattern` | Walk CWD | Scoped search to prevent massive expansion [internal/sandbox/linux_landlock.go:561-600]() |

**Sources:** [internal/sandbox/linux_landlock.go:496-644]()

## Graceful Fallback Behavior

Greywall follows a fail-open philosophy: if Landlock is unavailable or encounters errors, the sandbox continues with bubblewrap-only restrictions [internal/sandbox/linux_landlock.go:28-28](), [internal/sandbox/linux_landlock.go:36-36]().

Debug logging provides visibility into why Landlock was skipped without failing the sandbox creation [internal/sandbox/linux_landlock.go:24-27](), [internal/sandbox/linux_landlock.go:33-35]().

**Sources:** [internal/sandbox/linux_landlock.go:21-45](), [internal/sandbox/linux_landlock.go:194-199]()

## Testing and Verification

Integration tests in `internal/sandbox/integration_linux_test.go` verify that Landlock correctly blocks unauthorized access:

- `TestLinux_LandlockBlocksWriteOutsideWorkspace`: Verifies writes outside allowed paths fail [internal/sandbox/integration_linux_test.go:49-63]().
- `TestLinux_LandlockProtectsGitHooks`: Verifies `.git/hooks` cannot be written to [internal/sandbox/integration_linux_test.go:88-104]().
- `TestLinux_LandlockProtectsBashrc`: Verifies shell configs are protected from modification [internal/sandbox/integration_linux_test.go:157-175]().

**Sources:** [internal/sandbox/integration_linux_test.go:49-175]()

---

# Page: Seccomp Syscall Filtering

# Seccomp Syscall Filtering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/linux_ebpf.go](internal/sandbox/linux_ebpf.go)
- [internal/sandbox/linux_ebpf_stub.go](internal/sandbox/linux_ebpf_stub.go)
- [internal/sandbox/linux_seccomp.go](internal/sandbox/linux_seccomp.go)
- [internal/sandbox/linux_seccomp_stub.go](internal/sandbox/linux_seccomp_stub.go)
- [internal/sandbox/monitor.go](internal/sandbox/monitor.go)
- [internal/sandbox/shell.go](internal/sandbox/shell.go)

</details>



This page covers greywall's seccomp-bpf (Berkeley Packet Filter) implementation for Linux syscall filtering. Seccomp provides kernel-level enforcement that blocks dangerous system calls before they execute, adding a critical defense layer to the sandbox.

For information about the broader Linux sandboxing architecture, see [Linux Sandboxing](4.1). For filesystem access control, see [Landlock Filesystem Control](4.1.2). For violation monitoring, see [eBPF Violation Monitoring](4.1.4).

## Purpose and Scope

Seccomp filtering blocks dangerous syscalls at the kernel level using Berkeley Packet Filter (BPF) programs. This prevents sandboxed processes from performing operations like process injection (`ptrace`), kernel module loading, or terminal input injection (`TIOCSTI` ioctl). The filter runs in the kernel and cannot be bypassed by user-space code.

Key characteristics:
- **Kernel-enforced**: Syscalls are blocked before execution.
- **Zero overhead**: BPF programs execute with minimal performance impact.
- **Architecture-aware**: Syscall numbers differ between x86_64 and ARM64. [internal/sandbox/linux_seccomp.go:266-353]()
- **Silent blocking**: Uses `SECCOMP_RET_ERRNO` which returns `EPERM` without logging. [internal/sandbox/linux_seccomp.go:125-129]()

## Architecture Overview

The seccomp filter integrates into the Linux sandbox as one of multiple security layers. It works alongside bubblewrap, Landlock, and network isolation to provide defense-in-depth.

### Seccomp Integration Flow

```mermaid
graph TB
    subgraph "Sandbox Setup"
        CFG["Config with UseSeccomp=true"]
        DETECT["DetectLinuxFeatures()"]
        CREATE["NewSeccompFilter(debug)"]
    end
    
    subgraph "Filter Generation"
        GEN["GenerateBPFFilter()"]
        SYSCALLS["Build instruction list<br/>from DangerousSyscalls"]
        TIOCSTI_BLOCK["Add TIOCSTI ioctl blocking"]
        WRITE["writeBPFProgram(path)"]
        TMPFILE["Temp file:<br/>/tmp/greywall-seccomp/filter.bpf"]
    end
    
    subgraph "Bubblewrap Integration"
        FD3["Shell: exec 3&lt;$filterPath"]
        BWRAP["bwrap --seccomp 3"]
        KERNEL["Kernel seccomp subsystem"]
    end
    
    subgraph "Runtime Behavior"
        SYSCALL["Process makes syscall"]
        BPF["BPF program evaluates"]
        BLOCK["Match: Return EPERM"]
        ALLOW["No match: Allow"]
    end
    
    CFG --> DETECT
    DETECT --> CREATE
    CREATE --> GEN
    GEN --> SYSCALLS
    GEN --> TIOCSTI_BLOCK
    SYSCALLS --> WRITE
    TIOCSTI_BLOCK --> WRITE
    WRITE --> TMPFILE
    
    TMPFILE --> FD3
    FD3 --> BWRAP
    BWRAP --> KERNEL
    
    KERNEL --> SYSCALL
    SYSCALL --> BPF
    BPF --> BLOCK
    BPF --> ALLOW
    
    BLOCK -.silent EPERM.-> SYSCALL
```

**Sources**: [internal/sandbox/linux_seccomp.go:13-22](), [internal/sandbox/linux_seccomp.go:59-89](), [internal/sandbox/linux_seccomp.go:152-194]()

The filter is generated at sandbox creation time and passed to bubblewrap via file descriptor 3. The kernel attaches the BPF program to all processes in the sandbox.

## SeccompFilter Class

The `SeccompFilter` class manages BPF filter generation and lifecycle.

| Component | Type | Purpose |
|-----------|------|---------|
| `SeccompFilter` | struct | Filter generator with debug flag [internal/sandbox/linux_seccomp.go:14-16]() |
| `NewSeccompFilter(debug bool)` | constructor | Creates new filter instance [internal/sandbox/linux_seccomp.go:19-21]() |
| `GenerateBPFFilter()` | method | Generates BPF program, returns temp file path [internal/sandbox/linux_seccomp.go:61-89]() |
| `writeBPFProgram(path string)` | method | Writes BPF instructions to file [internal/sandbox/linux_seccomp.go:93-223]() |
| `CleanupFilter(path string)` | method | Removes temporary filter file [internal/sandbox/linux_seccomp_stub.go:21-21]() |

**Sources**: [internal/sandbox/linux_seccomp.go:13-22](), [internal/sandbox/linux_seccomp.go:61-89](), [internal/sandbox/linux_seccomp.go:93-223]()

## Blocked Syscalls

The `DangerousSyscalls` list defines syscalls that pose security risks to the sandbox. These are blocked regardless of process permissions.

### Syscall Categories

```mermaid
graph LR
    subgraph "DangerousSyscalls"
        PROC["Process Control<br/>ptrace<br/>process_vm_readv<br/>process_vm_writev"]
        KERN["Kernel Security<br/>keyctl<br/>add_key<br/>request_key<br/>personality"]
        SYS["System Operations<br/>mount, umount2<br/>reboot<br/>kexec_load<br/>pivot_root"]
        MOD["Module Management<br/>init_module<br/>finit_module<br/>delete_module"]
        IO["I/O Permissions<br/>ioperm<br/>iopl"]
        MISC["Miscellaneous<br/>userfaultfd<br/>perf_event_open<br/>bpf<br/>syslog"]
    end
    
    PROC -.EPERM.-> BLOCKED["Syscalls blocked<br/>with SECCOMP_RET_ERRNO"]
    KERN -.EPERM.-> BLOCKED
    SYS -.EPERM.-> BLOCKED
    MOD -.EPERM.-> BLOCKED
    IO -.EPERM.-> BLOCKED
    MISC -.EPERM.-> BLOCKED
```

**Sources**: [internal/sandbox/linux_seccomp.go:28-57]()

### Complete Blocked Syscalls List

| Syscall | Category | Threat |
|---------|----------|--------|
| `ptrace` | Process control | Process debugging/injection |
| `process_vm_readv` | Process control | Memory read from other processes |
| `process_vm_writev` | Process control | Memory write to other processes |
| `keyctl`, `add_key`, `request_key` | Kernel keyring | Kernel credential access |
| `personality` | Security bypass | Change execution domain, bypass ASLR |
| `userfaultfd` | Sandbox escape | User-space page fault handling |
| `perf_event_open` | Information leak | Performance monitoring data |
| `bpf` | Kernel access | eBPF operations without CAP_BPF |
| `kexec_load`, `kexec_file_load` | System control | Load new kernel |
| `reboot` | System control | System reboot |
| `syslog` | Information leak | Kernel log access |
| `acct` | System control | Process accounting |
| `mount`, `umount2` | Filesystem | Filesystem mount/unmount |
| `pivot_root` | Filesystem | Change root filesystem |
| `swapon`, `swapoff` | System control | Swap management |
| `sethostname`, `setdomainname` | System control | Hostname/domain changes |
| `init_module`, `finit_module` | Kernel | Kernel module loading |
| `delete_module` | Kernel | Kernel module unloading |
| `ioperm`, `iopl` | I/O | I/O port access (x86_64 only) |

**Sources**: [internal/sandbox/linux_seccomp.go:28-57]()

## TIOCSTI Terminal Injection Protection

The seccomp filter includes special logic to block the `TIOCSTI` ioctl, which allows processes to inject characters into the terminal input buffer. This attack vector was traditionally mitigated by bubblewrap's `--new-session` flag, but that flag breaks `SIGWINCH` delivery to interactive applications. [internal/sandbox/linux_seccomp.go:23-26]()

### Why TIOCSTI is Dangerous

A sandboxed process could use `ioctl(fd, TIOCSTI, &ch)` to inject keystrokes into the parent terminal session, potentially executing commands outside the sandbox after the sandbox exits.

### Implementation Details

The BPF filter checks both the syscall number (ioctl) and the ioctl command argument:

```mermaid
graph TB
    SYSCALL["Syscall made"]
    
    LOAD_NR["Load syscall number<br/>from seccomp_data.nr"]
    CHECK_IOCTL{"Syscall == ioctl?"}
    
    LOAD_ARG["Load args[1]<br/>(ioctl command)<br/>offset 24"]
    CHECK_TIOCSTI{"Command == TIOCSTI<br/>(0x5412)?"}
    
    BLOCK["Return SECCOMP_RET_ERRNO<br/>with EPERM"]
    ALLOW["Return SECCOMP_RET_ALLOW"]
    
    SYSCALL --> LOAD_NR
    LOAD_NR --> CHECK_IOCTL
    CHECK_IOCTL -->|Yes| LOAD_ARG
    CHECK_IOCTL -->|No| ALLOW
    LOAD_ARG --> CHECK_TIOCSTI
    CHECK_TIOCSTI -->|Yes| BLOCK
    CHECK_TIOCSTI -->|No| ALLOW
```

**Sources**: [internal/sandbox/linux_seccomp.go:23-26](), [internal/sandbox/linux_seccomp.go:152-194]()

The `seccomp_data` structure layout is critical for accessing syscall arguments:

| Offset | Field | Size | Content |
|--------|-------|------|---------|
| 0 | `nr` | u32 | Syscall number |
| 4 | `arch` | u32 | Architecture identifier |
| 8-12 | `instruction_pointer` | u64 | Instruction pointer (split) |
| 16-20 | `args[0]` | u64 | First argument (split) |
| 24-28 | `args[1]` | u64 | Second argument (split, ioctl command) |

**Sources**: [internal/sandbox/linux_seccomp.go:154-163]()

## BPF Program Generation

The BPF filter is generated as a sequence of `bpfInstruction` structures, each encoding a single BPF operation. [internal/sandbox/linux_seccomp.go:243-249]()

### BPF Instruction Structure

```mermaid
graph LR
    subgraph "bpfInstruction struct"
        CODE["code: uint16<br/>Operation type"]
        JT["jt: uint8<br/>Jump if true offset"]
        JF["jf: uint8<br/>Jump if false offset"]
        K["k: uint32<br/>Constant value"]
    end
    
    subgraph "Binary Encoding (8 bytes)"
        B0["byte 0: code[0:8]"]
        B1["byte 1: code[8:16]"]
        B2["byte 2: jt"]
        B3["byte 3: jf"]
        B4["byte 4: k[0:8]"]
        B5["byte 5: k[8:16]"]
        B6["byte 6: k[16:24]"]
        B7["byte 7: k[24:32]"]
    end
    
    CODE --> B0
    CODE --> B1
    JT --> B2
    JF --> B3
    K --> B4
    K --> B5
    K --> B6
    K --> B7
```

**Sources**: [internal/sandbox/linux_seccomp.go:243-249](), [internal/sandbox/linux_seccomp.go:251-264]()

### Program Structure

The complete BPF program follows this pattern:

```mermaid
graph TB
    START["Program Start"]
    
    LOAD["1. Load syscall number<br/>BPF_LD | BPF_W | BPF_ABS<br/>offset=0"]
    
    LOOP_START["For each dangerous syscall:"]
    CMP["Compare syscall number<br/>BPF_JMP | BPF_JEQ | BPF_K"]
    BLOCK["Return ERRNO(EPERM)<br/>BPF_RET | BPF_K<br/>k=SECCOMP_RET_ERRNO | EPERM"]
    
    IOCTL_LOAD["Reload syscall number"]
    IOCTL_CMP{"Check if ioctl?"}
    ARG_LOAD["Load args[1]<br/>(offset 24)"]
    TIOCSTI_CMP{"Check TIOCSTI?"}
    TIOCSTI_BLOCK["Return ERRNO(EPERM)"]
    
    DEFAULT["Default: Allow<br/>BPF_RET | BPF_K<br/>k=SECCOMP_RET_ALLOW"]
    
    START --> LOAD
    LOAD --> LOOP_START
    LOOP_START --> CMP
    CMP -->|Match| BLOCK
    CMP -->|No match| LOOP_START
    
    LOOP_START -->|Done| IOCTL_LOAD
    IOCTL_LOAD --> IOCTL_CMP
    IOCTL_CMP -->|Yes| ARG_LOAD
    IOCTL_CMP -->|No| DEFAULT
    ARG_LOAD --> TIOCSTI_CMP
    TIOCSTI_CMP -->|Yes| TIOCSTI_BLOCK
    TIOCSTI_CMP -->|No| DEFAULT
```

**Sources**: [internal/sandbox/linux_seccomp.go:115-216]()

### BPF Instruction Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `BPF_LD` | 0x00 | Load operation |
| `BPF_JMP` | 0x05 | Jump operation |
| `BPF_RET` | 0x06 | Return operation |
| `BPF_W` | 0x00 | Word (32-bit) |
| `BPF_ABS` | 0x20 | Absolute addressing |
| `BPF_JEQ` | 0x10 | Jump if equal |
| `BPF_K` | 0x00 | Constant source |

**Sources**: [internal/sandbox/linux_seccomp.go:225-241]()

## Architecture-Specific Syscall Numbers

Syscall numbers differ between x86_64 and ARM64 architectures. The `getSyscallNumber()` function detects the architecture and returns the correct number. [internal/sandbox/linux_seccomp.go:266-353]()

### Architecture Detection and Mapping

```mermaid
graph TB
    DETECT["Detect architecture<br/>via unix.Uname()"]
    
    X86{"machine == x86_64?"}
    ARM{"machine == aarch64<br/>or arm64?"}
    
    X86_MAP["Use x86_64 syscall map<br/>ptrace=101<br/>ioctl=16<br/>mount=165"]
    
    ARM_MAP["Use ARM64 syscall map<br/>ptrace=117<br/>ioctl=29<br/>mount=40"]
    
    RETURN["Return syscall number"]
    
    DETECT --> X86
    X86 -->|Yes| X86_MAP
    X86 -->|No| ARM
    ARM -->|Yes| ARM_MAP
    
    X86_MAP --> RETURN
    ARM_MAP --> RETURN
```

**Sources**: [internal/sandbox/linux_seccomp.go:266-353]()

### Example Syscall Number Differences

| Syscall | x86_64 | ARM64 | Notes |
|---------|--------|-------|-------|
| `ptrace` | 101 | 117 | Different on both architectures |
| `ioctl` | 16 | 29 | Used for TIOCSTI blocking |
| `mount` | 165 | 40 | Filesystem operations |
| `ioperm` | 173 | N/A | x86_64 only (I/O ports) |
| `iopl` | 172 | N/A | x86_64 only (I/O privilege) |

**Sources**: [internal/sandbox/linux_seccomp.go:286-349]()

Note that `ioperm` and `iopl` do not exist on ARM64 architecture, as ARM does not have the same I/O port model as x86.

## Monitoring and Logging Limitations

The seccomp filter uses `SECCOMP_RET_ERRNO` as its blocking action, which silently returns `EPERM` without generating any kernel logs. [internal/sandbox/linux_seccomp.go:128-129]()

### Detection via eBPF

Since seccomp violations are silent, greywall uses the `EBPFMonitor` to detect syscall failures (EPERM, EACCES) regardless of their source. The eBPF monitor can observe when syscalls return error codes, catching both seccomp-blocked calls and naturally-occurring permission errors. [internal/sandbox/linux_ebpf.go:179-204]()

For details on violation monitoring, see [eBPF Violation Monitoring](4.1.4).

**Sources**: [internal/sandbox/linux_ebpf.go:179-204](), [internal/sandbox/linux_seccomp.go:128-129]()

## Cleanup and Lifecycle

The seccomp filter file is temporary and cleaned up after use.

| Stage | Action | Location |
|-------|--------|----------|
| **Generation** | Create `/tmp/greywall-seccomp/filter-{pid}.bpf` | `GenerateBPFFilter()` [internal/sandbox/linux_seccomp.go:68-73]() |
| **Cleanup** | Remove filter file | `CleanupFilter(path)` [internal/sandbox/linux_seccomp_stub.go:21-21]() |

**Sources**: [internal/sandbox/linux_seccomp.go:68-73](), [internal/sandbox/linux_seccomp_stub.go:21-21]()

---

**Page Summary**: Greywall's seccomp implementation provides kernel-enforced syscall filtering using BPF programs. It blocks dangerous syscalls and includes special TIOCSTI protection to prevent terminal injection attacks. The filter is architecture-aware, generates compact BPF binary programs, and uses silent blocking (`SECCOMP_RET_ERRNO`) paired with eBPF monitoring for violation detection.

---

# Page: eBPF Violation Monitoring

# eBPF Violation Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_ebpf.go](internal/sandbox/linux_ebpf.go)
- [internal/sandbox/linux_seccomp.go](internal/sandbox/linux_seccomp.go)
- [internal/sandbox/monitor.go](internal/sandbox/monitor.go)

</details>



## Purpose and Scope

This page describes greywall's real-time violation monitoring system on Linux using eBPF (Extended Berkeley Packet Filter). The eBPF monitor tracks denied filesystem and network operations inside the sandbox, providing visibility into policy violations that would otherwise be silent.

For information about the overall Linux sandboxing architecture, see [Linux Sandboxing](). For details on seccomp syscall filtering that triggers many of these violations, see [Seccomp Syscall Filtering](). For macOS violation monitoring, which uses a different approach based on unified logging, see [Unified Log Monitoring]().

**Sources**: [internal/sandbox/linux_ebpf.go:1-27](), [internal/sandbox/linux.go:113-137]()

---

## Why eBPF Monitoring is Needed

The greywall Linux sandbox uses seccomp-bpf filters to block dangerous syscalls at the kernel level. When a seccomp filter blocks a syscall, it returns `SECCOMP_RET_ERRNO` with `EPERM`, causing the syscall to fail silently without any logging to dmesg, audit logs, or anywhere else. This is different from `SECCOMP_RET_LOG` (which logs but doesn't block) or `SECCOMP_RET_KILL` (which terminates the process).

Without eBPF monitoring, users would have no visibility into:
- Which operations the sandbox blocked [internal/sandbox/linux_ebpf.go:179-203]()
- Why an application isn't working correctly
- What permissions need to be added to the profile

The eBPF monitor solves this by tracing syscall exit points at the kernel level and detecting when operations fail with permission-related error codes (`EPERM`, `EACCES`, `EROFS`). This provides real-time feedback about sandbox violations regardless of whether they were caused by seccomp filters, Landlock LSM, or mount-based restrictions.

**Sources**: [internal/sandbox/linux_seccomp.go:128-130](), [internal/sandbox/linux_ebpf.go:179-182]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Sandboxed Process"
        APP["Application Code"]
        SYSCALL["Syscall Invocation<br/>(open, connect, etc.)"]
    end
    
    subgraph "Kernel Security Layers"
        SECCOMP["seccomp-bpf Filter<br/>Blocks dangerous syscalls<br/>Returns EPERM silently"]
        LANDLOCK["Landlock LSM<br/>Filesystem ACLs<br/>Returns EACCES/EPERM"]
        VFS["VFS Layer<br/>Mount restrictions<br/>Returns EROFS/EACCES"]
    end
    
    subgraph "eBPF Monitoring Infrastructure"
        TRACEPOINTS["Kernel Tracepoints<br/>sys_exit_openat<br/>sys_exit_connect<br/>sys_exit_unlinkat<br/>sys_exit_mkdirat"]
        BPFTRACE["bpftrace Process<br/>BPF program attached<br/>Event filtering"]
        SCRIPT["Generated .bt Script<br/>PID filtering<br/>Error code matching"]
    end
    
    subgraph "greywall Monitor"
        EBPFMON["EBPFMonitor struct<br/>internal/sandbox/linux_ebpf.go"]
        PARSER["Event Parser<br/>parseBpftraceOutput()"]
        FORMATTER["Violation Formatter<br/>getErrnoName()"]
        OUTPUT["stderr Output<br/>[greywall:ebpf] timestamp"]
    end
    
    APP --> SYSCALL
    SYSCALL --> SECCOMP
    SYSCALL --> LANDLOCK
    SYSCALL --> VFS
    
    SECCOMP -.EPERM.-> TRACEPOINTS
    LANDLOCK -.EACCES.-> TRACEPOINTS
    VFS -.EROFS.-> TRACEPOINTS
    
    TRACEPOINTS --> BPFTRACE
    SCRIPT --> BPFTRACE
    BPFTRACE --> EBPFMON
    EBPFMON --> PARSER
    PARSER --> FORMATTER
    FORMATTER --> OUTPUT
    
    EBPFMON -.generates.-> SCRIPT
```

**Diagram: eBPF monitoring architecture showing how kernel tracepoints capture syscall failures from multiple security layers**

The `EBPFMonitor` struct manages the lifecycle of the bpftrace monitoring process. It generates a custom bpftrace script targeting the specific sandbox PID, attaches to kernel tracepoints for syscall exit events, filters events by error codes, and formats violations for user consumption.

**Sources**: [internal/sandbox/linux_ebpf.go:20-35](), [internal/sandbox/linux_ebpf.go:163-205]()

---

## Feature Detection and Requirements

### Capability Requirements

eBPF tracing requires elevated privileges to attach to kernel tracepoints. The system checks for the `HasEBPF` feature which typically requires `CAP_BPF` or root privileges.

| Requirement | Description |
|------------|-------------|
| `CAP_BPF` | Modern capability for BPF operations (kernel 5.8+) |
| Root (UID 0) | Traditional superuser privileges |

The check is performed during `Start()` using `DetectLinuxFeatures()`.

**Sources**: [internal/sandbox/linux_ebpf.go:38-45]()

### Detection Flow

```mermaid
graph LR
    START["DetectLinuxFeatures()"]
    CHECK_EBPF{"features.HasEBPF<br/>set?"}
    SET_EBPF["Proceed with<br/>EBPFMonitor.Start()"]
    LOG_ERR["Log: need CAP_BPF<br/>or root"]
    DONE["Exit Start()"]
    
    START --> CHECK_EBPF
    CHECK_EBPF -->|yes| SET_EBPF
    CHECK_EBPF -->|no| LOG_ERR
    LOG_ERR --> DONE
    SET_EBPF --> DONE
```

**Diagram: Feature detection flow for eBPF capabilities**

**Sources**: [internal/sandbox/linux_ebpf.go:38-45]()

---

## EBPFMonitor Implementation

### Struct Definition and Lifecycle

```go
type EBPFMonitor struct {
    pid        int            // Sandbox PID for filtering
    debug      bool           // Enable debug output
    cancel     context.CancelFunc  // Context cancellation
    running    bool           // Monitor state
    cmd        *exec.Cmd      // bpftrace process
    scriptPath string         // Temp script path for cleanup
}
```

**Lifecycle Methods:**

| Method | Purpose | Key Actions |
|--------|---------|-------------|
| `NewEBPFMonitor(pid, debug)` | Constructor | Initialize struct with sandbox PID [internal/sandbox/linux_ebpf.go:30-35]() |
| `Start()` | Begin monitoring | Check features, generate script, start bpftrace, spawn parser goroutine [internal/sandbox/linux_ebpf.go:38-65]() |
| `Stop()` | Cleanup | Cancel context, kill bpftrace, remove temp script [internal/sandbox/linux_ebpf.go:68-91]() |

**Sources**: [internal/sandbox/linux_ebpf.go:20-91]()

### Bpftrace Integration

The monitor uses `bpftrace` to attach BPF programs to kernel tracepoints. The `tryBpftrace()` method:

1. Locates bpftrace binary with `exec.LookPath("bpftrace")` [internal/sandbox/linux_ebpf.go:95-98]()
2. Generates custom script via `generateBpftraceScript()` [internal/sandbox/linux_ebpf.go:101]()
3. Writes script to temp file [internal/sandbox/linux_ebpf.go:104-116]()
4. Executes `bpftrace` with context cancellation [internal/sandbox/linux_ebpf.go:118]()
5. Creates pipes for stdout/stderr [internal/sandbox/linux_ebpf.go:119-127]()
6. Spawns goroutine to parse output line-by-line [internal/sandbox/linux_ebpf.go:134-145]()

**Sources**: [internal/sandbox/linux_ebpf.go:94-159]()

---

## Bpftrace Script Generation

### Script Structure

The dynamically generated bpftrace script attaches to syscall exit tracepoints and filters events by PID and error codes:

```mermaid
graph TD
    BEGIN["BEGIN block<br/>Print startup message"]
    TP_OPENAT["tracepoint:syscalls:sys_exit_openat<br/>Filter: ret in {-13,-1,-30} AND pid >= SANDBOX_PID"]
    TP_UNLINK["tracepoint:syscalls:sys_exit_unlinkat<br/>Filter: ret in {-13,-1,-30} AND pid >= SANDBOX_PID"]
    TP_MKDIR["tracepoint:syscalls:sys_exit_mkdirat<br/>Filter: ret in {-13,-1,-30} AND pid >= SANDBOX_PID"]
    TP_CONNECT["tracepoint:syscalls:sys_exit_connect<br/>Filter: ret in {-13,-1,-111} AND pid >= SANDBOX_PID"]
    
    PRINT["printf()<br/>DENIED:syscall pid=X comm=Y ret=Z"]
    
    BEGIN --> TP_OPENAT
    BEGIN --> TP_UNLINK
    BEGIN --> TP_MKDIR
    BEGIN --> TP_CONNECT
    
    TP_OPENAT --> PRINT
    TP_UNLINK --> PRINT
    TP_MKDIR --> PRINT
    TP_CONNECT --> PRINT
```

**Diagram: Structure of generated bpftrace script showing tracepoint attachments**

### Error Code Filtering

The script filters syscall return values to detect permission-related failures:

| Error Code | Symbolic Name | Meaning | Typical Source |
|------------|---------------|---------|----------------|
| `-1` | `EPERM` | Operation not permitted | seccomp-bpf filter, Landlock [internal/sandbox/linux_ebpf.go:182]() |
| `-13` | `EACCES` | Permission denied | Landlock LSM, VFS permissions [internal/sandbox/linux_ebpf.go:182]() |
| `-30` | `EROFS` | Read-only file system | Mount restrictions [internal/sandbox/linux_ebpf.go:182]() |
| `-111` | `ECONNREFUSED` | Connection refused | Network isolation [internal/sandbox/linux_ebpf.go:200]() |

**Sources**: [internal/sandbox/linux_ebpf.go:163-205]()

### PID Filtering Strategy

The script uses `pid >= SANDBOX_PID` to filter events. This is a heuristic that excludes pre-existing system processes (which have lower PIDs) while capturing sandbox processes. 

**Limitation**: This approach doesn't track actual parent-child relationships via fork/clone events because bpftrace attaches after the command starts.

**Sources**: [internal/sandbox/linux_ebpf.go:163-173]()

---

## Monitored Syscalls and Operations

### Filesystem Operations

| Tracepoint | Syscall | Detects |
|------------|---------|---------|
| `sys_exit_openat` | `openat(2)` | File open failures [internal/sandbox/linux_ebpf.go:181]() |
| `sys_exit_unlinkat` | `unlinkat(2)` | File deletion failures [internal/sandbox/linux_ebpf.go:187]() |
| `sys_exit_mkdirat` | `mkdirat(2)` | Directory creation failures [internal/sandbox/linux_ebpf.go:193]() |

### Network Operations

| Tracepoint | Syscall | Detects |
|------------|---------|---------|
| `sys_exit_connect` | `connect(2)` | Connection failures [internal/sandbox/linux_ebpf.go:199]() |

**Sources**: [internal/sandbox/linux_ebpf.go:181-203]()

---

## Event Parsing and Output

### Parsing Flow

```mermaid
sequenceDiagram
    participant BPF as "bpftrace stdout"
    participant Scanner as "bufio.Scanner"
    participant Parser as "parseBpftraceOutput()"
    participant Stderr as "os.Stderr"
    
    BPF->>Scanner: "DENIED:open pid=12345 comm=bash ret=-13"
    Scanner->>Parser: Raw line
    Parser->>Parser: Regex match pattern
    Parser->>Parser: Extract syscall, pid, comm, ret
    Parser->>Parser: Format with timestamp
    Parser->>Stderr: "[greywall:ebpf] 15:04:05 ✗ open: Permission denied (bash, pid=12345)"
```

**Diagram: Event parsing and formatting pipeline**

### Output Format

The `parseBpftraceOutput()` method transforms bpftrace output into human-readable violations:

**Input (bpftrace):**
```
DENIED:open pid=12345 comm=bash ret=-13
```

**Output (formatted):**
```
[greywall:ebpf] 15:04:05 ✗ open: Permission denied (bash, pid=12345)
```

The format includes the timestamp, a cross mark (`✗`), the syscall, a mapped error name (via `getErrnoName`), the command name, and the PID.

**Sources**: [internal/sandbox/linux_ebpf.go:209-232]()

---

## Comparison with macOS Log Monitoring

While this page covers Linux eBPF monitoring, macOS uses a fundamentally different approach via the unified logging system. Key differences:

| Aspect | Linux (eBPF) | macOS (Unified Log) |
|--------|--------------|---------------------|
| Mechanism | Kernel tracepoints via bpftrace | System log stream filtering |
| Privileges | Requires CAP_BPF or root | No special privileges needed |
| Filtering | PID-based heuristic | Session suffix string matching |
| Implementation | [internal/sandbox/linux_ebpf.go]() | [internal/sandbox/monitor.go]() |

**Sources**: [internal/sandbox/linux_ebpf.go:1-27](), [internal/sandbox/monitor.go:16-33]()

---

# Page: Transparent Network Proxying

# Transparent Network Proxying

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/benchmark_test.go](internal/sandbox/benchmark_test.go)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/resolv_linux_test.go](internal/sandbox/resolv_linux_test.go)
- [internal/sandbox/tun2socks_embed.go](internal/sandbox/tun2socks_embed.go)

</details>



This page describes how greywall achieves transparent network proxying on Linux using TUN devices and `tun2socks`. This is a Linux-specific feature that captures all network traffic from sandboxed processes without requiring application cooperation. For information about the greyproxy service that receives this traffic, see [5.1 greyproxy Service](). For Unix socket bridging details, see [5.2 Proxy Bridges and Unix Sockets]().

## Purpose and Scope

Transparent network proxying allows greywall to intercept all TCP/UDP traffic from sandboxed applications, regardless of whether they respect proxy environment variables. This is critical for sandboxing applications that make direct network connections or use network libraries that ignore `HTTP_PROXY` settings.

On Linux, greywall implements transparent proxying by:
1. Creating an isolated network namespace with `--unshare-net` [internal/sandbox/linux.go:638-643]()
2. Setting up a TUN device as the default route [internal/sandbox/linux.go:1005-1013]()
3. Using `tun2socks` to convert raw IP packets to SOCKS5 [internal/sandbox/linux.go:994-1002]()
4. Bridging SOCKS5 connections to greyproxy via Unix sockets [internal/sandbox/linux.go:1016-1019]()

When transparent proxying is unavailable (e.g., restricted containerized environments), greywall falls back to proxy environment variables [internal/sandbox/linux.go:1039-1057]().

**Sources:** [internal/sandbox/linux.go:21-31](), [internal/sandbox/linux.go:638-643](), [internal/sandbox/linux.go:993-1024](), [internal/sandbox/linux.go:1039-1057]()

## Architecture Overview

The transparent proxy architecture creates a complete network isolation layer where all traffic flows through a controlled proxy pipeline.

### System to Code Entity Mapping

The following diagram maps high-level network components to the specific Go structs and shell commands used in the implementation.

```mermaid
graph TB
    subgraph "Code Entity Space"
        MGR["Manager [internal/sandbox/manager.go]"]
        PB["ProxyBridge [internal/sandbox/linux.go]"]
        DB["DnsBridge [internal/sandbox/linux.go]"]
        LSO["LinuxSandboxOptions [internal/sandbox/linux.go]"]
    end

    subgraph "Sandbox Network Namespace"
        APP["Application Process"]
        TUNDEV["TUN Device (tun0)"]
        T2S["tun2socks binary [internal/sandbox/tun2socks_embed.go]"]
        SOCAT_IN["socat TCP-LISTEN:18321"]
    end
    
    subgraph "Host Space"
        UNIX_SOCK["Unix Socket File (/tmp/greywall-proxy-*.sock)"]
        SOCAT_OUT["socat UNIX-LISTEN"]
        GREYPROXY["greyproxy service"]
    end
    
    MGR --> PB
    PB --> SOCAT_OUT
    PB --> UNIX_SOCK
    MGR --> DB
    DB --> SOCAT_OUT
    
    APP -->|"Raw IP Packets"| TUNDEV
    TUNDEV --> T2S
    T2S -->|"SOCKS5"| SOCAT_IN
    SOCAT_IN -->|"UNIX-CONNECT"| UNIX_SOCK
    UNIX_SOCK --> SOCAT_OUT
    SOCAT_OUT -->|"TCP"| GREYPROXY
```

**Network Flow Chain:**

| Stage | Component | Location | Purpose |
|-------|-----------|----------|---------|
| 1 | Application | Inside namespace | Makes normal TCP/UDP connections |
| 2 | TUN device `tun0` | Inside namespace | Captures all packets (default route) [internal/sandbox/linux.go:1012-1013]() |
| 3 | `tun2socks` | Inside namespace | Converts IP packets to SOCKS5 [internal/sandbox/linux.go:1020-1022]() |
| 4 | `socat` relay (inner) | Inside namespace | Forwards SOCKS5 to Unix socket [internal/sandbox/linux.go:1016-1019]() |
| 5 | Unix socket | Host filesystem | Crosses namespace boundary [internal/sandbox/linux.go:158-165]() |
| 6 | `socat` relay (outer) | Host system | Forwards Unix socket to TCP [internal/sandbox/linux.go:175-179]() |
| 7 | `greyproxy` | Host system | Domain filtering and routing |

**Sources:** [internal/sandbox/linux.go:21-41](), [internal/sandbox/linux.go:131-205](), [internal/sandbox/linux.go:993-1024](), [internal/sandbox/tun2socks_embed.go:1-53]()

## TUN Device Configuration

When transparent proxying is enabled, greywall configures a TUN device inside the network namespace. This setup occurs in the inner script executed by `bubblewrap`.

```mermaid
sequenceDiagram
    participant S as "Inner Shell Script [internal/sandbox/linux.go]"
    participant IP as "ip command"
    participant TUN as "tun0 Device"

    S->>IP: ip link set lo up
    S->>IP: ip tuntap add dev tun0 mode tun
    S->>IP: ip addr add 198.18.0.1/15 dev tun0
    S->>IP: ip link set dev tun0 up
    S->>IP: ip route add default via 198.18.0.1 dev tun0
    Note over TUN: Capturing all outbound traffic
```

**Network Parameters:**
- **Device Name:** `tun0` [internal/sandbox/linux.go:1005]()
- **IP Address:** `198.18.0.1/15` [internal/sandbox/linux.go:1008]()
- **Routing:** Set as the default gateway [internal/sandbox/linux.go:1012-1013]()

**Sources:** [internal/sandbox/linux.go:1005-1013]()

## tun2socks Integration

The `tun2socks` binary implements a userspace network stack that reads raw packets from the TUN device and converts them to SOCKS5 connections. Greywall embeds `tun2socks` as a binary asset and extracts it to a temporary file for use.

### Binary Extraction
The function `extractTun2Socks` handles platform-specific binary extraction:
- It supports `amd64` and `arm64` architectures [internal/sandbox/tun2socks_embed.go:20-27]().
- It writes the embedded data to a temporary file with `0755` permissions [internal/sandbox/tun2socks_embed.go:35-50]().

### Execution in Sandbox
Inside the sandbox, `tun2socks` is executed with the following parameters:
- `-device tun0`: Points to the capture interface [internal/sandbox/linux.go:1021]().
- `-proxy socks5://...`: Points to the local `socat` listener [internal/sandbox/linux.go:1021]().
- Credentials: If the `ProxyBridge` has `HasAuth` set to true, credentials are included in the proxy URL [internal/sandbox/linux.go:1020-1022]().

**Sources:** [internal/sandbox/linux.go:1020-1022](), [internal/sandbox/tun2socks_embed.go:13-53]()

## Bridge Implementation

Greywall uses two types of bridges to handle different traffic types.

### ProxyBridge
The `ProxyBridge` struct [internal/sandbox/linux.go:22-31]() manages the host-side `socat` process that forwards traffic from a Unix socket to the external SOCKS5 proxy (usually `greyproxy`).

- **NewProxyBridge**: Initializes the bridge, generates a random socket path in `os.TempDir()`, and starts the `socat` process [internal/sandbox/linux.go:141-186]().
- **Cleanup**: Kills the `socat` process and removes the socket file [internal/sandbox/linux.go:203-213]().

### DnsBridge
The `DnsBridge` struct [internal/sandbox/linux.go:36-41]() handles DNS traffic specifically.

- **NewDnsBridge**: Starts a `socat` relay from a Unix socket to a UDP DNS server [internal/sandbox/linux.go:44-75]().
- **Sandbox Configuration**: Inside the sandbox, `socat` listens on UDP port 53 and forwards to the `DnsBridge` Unix socket [internal/sandbox/linux.go:1031-1033]().

**Sources:** [internal/sandbox/linux.go:22-103](), [internal/sandbox/linux.go:141-213](), [internal/sandbox/linux.go:1031-1033]()

## DNS Resolution Strategies

Greywall provides two ways to handle DNS inside the isolated network namespace.

| Strategy | Mechanism | resolv.conf Content |
| :--- | :--- | :--- |
| **DNS Bridge** | `socat` UDP relay to host-side DNS | `nameserver 127.0.0.1` [internal/sandbox/linux.go:946]() |
| **TCP Fallback** | `tun2socks` handles DNS over TCP | `nameserver 1.1.1.1` + `options use-vc` [internal/sandbox/linux.go:933-938]() |

The `options use-vc` flag [internal/sandbox/linux.go:938]() is critical when using the TCP fallback; it forces the resolver to use TCP (Virtual Circuit) instead of UDP, allowing `tun2socks` to proxy the requests.

**Sources:** [internal/sandbox/linux.go:932-951](), [internal/sandbox/resolv_linux_test.go:99-115]()

## Lifecycle and Cleanup

The lifecycle of the transparent proxy is tied to the `Manager` and the specific bridge instances.

```mermaid
sequenceDiagram
    participant M as Manager
    participant PB as ProxyBridge
    participant S as Sandbox Process

    M->>PB: NewProxyBridge(url, debug)
    PB->>PB: Start socat (host-side)
    M->>S: Start bubblewrap (includes tun2socks/inner socat)
    Note over S: Application running...
    S-->>M: Process Exit
    M->>PB: Cleanup()
    PB->>PB: Kill socat
    PB->>PB: Remove socket file
```

**Sources:** [internal/sandbox/linux.go:88-103](), [internal/sandbox/linux.go:203-213](), [internal/sandbox/benchmark_test.go:82-96]()

---

# Page: macOS Sandboxing

# macOS Sandboxing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)
- [internal/sandbox/manager_darwin.go](internal/sandbox/manager_darwin.go)
- [internal/sandbox/manager_linux.go](internal/sandbox/manager_linux.go)

</details>



This page describes greywall's macOS sandbox implementation using Apple's `sandbox-exec` tool and Seatbelt profile language. This implementation provides process isolation and access control on macOS systems, with a fundamentally different architecture than the Linux implementation due to platform constraints.

For detailed information about Seatbelt profile generation, see [Seatbelt Profile Generation](#4.2.1). For monitoring sandbox violations, see [Unified Log Monitoring](#4.2.2). For comparison with the Linux implementation, see [Linux Sandboxing](#4.1).

## Architecture Overview

The macOS implementation uses a simpler architecture compared to Linux's multi-layer approach. All security enforcement happens through a single Seatbelt profile passed to `sandbox-exec`, which applies kernel-enforced restrictions to the sandboxed process and its children.

### Command Execution Flow
The `WrapCommandMacOS` function [internal/sandbox/macos.go:647-748]() acts as the primary orchestrator. It collects configuration into a `MacOSSandboxParams` struct [internal/sandbox/macos.go:29-54](), generates a Seatbelt profile via `GenerateSandboxProfile` [internal/sandbox/macos.go:422-645](), and constructs an `exec.Command` that invokes `sandbox-exec`.

### System Entity Mapping

The following diagram bridges the high-level components to the specific code entities that implement them.

**Diagram: macOS Sandbox Code Architecture**
```mermaid
graph TB
    subgraph "Entry Point"
        MGR["Manager.Run()"]
        WRAP["WrapCommandMacOS()"]
    end
    
    subgraph "Logic & Generation"
        PARAMS["MacOSSandboxParams (struct)"]
        GEN["GenerateSandboxProfile()"]
        READ["generateReadRules()"]
        WRITE["generateWriteRules()"]
        TMP["expandMacOSTmpPaths()"]
    end
    
    subgraph "OS Enforcement"
        SBEXEC["sandbox-exec (CLI)"]
        SEATBELT["Seatbelt (Kernel Module)"]
    end
    
    subgraph "Monitoring"
        MON["LogMonitor (struct)"]
        STREAM["log stream (CLI)"]
        PARSE["parseViolation()"]
    end
    
    MGR --> WRAP
    WRAP --> PARAMS
    PARAMS --> GEN
    GEN --> READ
    GEN --> WRITE
    GEN --> TMP
    
    WRAP --> SBEXEC
    SBEXEC --> SEATBELT
    
    MON --> STREAM
    STREAM -.-> PARSE
```
**Sources:** [internal/sandbox/macos.go:29-54](), [internal/sandbox/macos.go:422-645](), [internal/sandbox/macos.go:647-748](), [internal/sandbox/monitor.go:24-60]()

## Core Components

### MacOSSandboxParams
The `MacOSSandboxParams` struct [internal/sandbox/macos.go:29-54]() encapsulates the sandbox policy, including filesystem paths, network proxy details, and process capabilities like PTY support.

### Profile Generation Logic
Greywall dynamically builds S-expression based profiles.
- **Filesystem**: Handled by `generateReadRules` [internal/sandbox/macos.go:156-282]() and `generateWriteRules` [internal/sandbox/macos.go:284-361]().
- **Network**: The profile explicitly allows outbound connections to the proxy defined in `ProxyHost` and `ProxyPort` [internal/sandbox/macos.go:593-605]().
- **Path Handling**: Since `/tmp` is a symlink to `/private/tmp` on macOS, `expandMacOSTmpPaths` [internal/sandbox/macos.go:100-127]() ensures both paths are included in rules to prevent kernel resolution bypasses.

**Sources:** [internal/sandbox/macos.go:29-54](), [internal/sandbox/macos.go:100-127](), [internal/sandbox/macos.go:156-361](), [internal/sandbox/macos.go:593-605]()

## Network Isolation Strategy

Unlike Linux, macOS does not support network namespaces for unprivileged processes. Greywall employs a two-pronged approach:

1.  **Seatbelt Rules**: The profile denies all network access by default but explicitly allows `network-outbound` to the local `greyproxy` instance [internal/sandbox/macos.go:593-605]().
2.  **Environment Variables**: `WrapCommandMacOS` injects `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` into the process environment [internal/sandbox/macos.go:738-745]().

For details, see [Seatbelt Profile Generation](#4.2.1).

**Sources:** [internal/sandbox/macos.go:593-605](), [internal/sandbox/macos.go:738-745]()

## Filesystem Access Control

Greywall implements a "Deny-by-Default" read model on macOS. 
- **Metadata**: `file-read-metadata` is allowed globally so tools can perform `stat` or `ls` [internal/sandbox/macos.go:166]().
- **Data**: `file-read-data` is restricted to system paths, the current working directory, and user-defined allow-lists [internal/sandbox/macos.go:170-190]().

### Security Nuance: Operation Specificity
Seatbelt requires that `deny` rules match the specificity of `allow` rules. For example, if `file-read-data` is allowed for a directory, a `deny file-read*` for a sub-file will be ignored by the kernel. Greywall ensures consistency by using specific operation types in its generated rules [internal/sandbox/macos.go:233-242]().

**Sources:** [internal/sandbox/macos.go:159-190](), [internal/sandbox/macos.go:233-242]()

## Violation Monitoring

Monitoring on macOS relies on the Unified Logging System.

**Diagram: macOS Violation Monitoring Flow**
```mermaid
sequenceDiagram
    participant P as Sandboxed Process
    participant K as Seatbelt Kernel
    participant L as Unified Log (log stream)
    participant M as LogMonitor.Start()
    
    P->>K: Attempt unauthorized write
    K-->>P: EPERM (Operation Not Permitted)
    K->>L: Emit Sandbox Violation + sessionSuffix
    L->>M: Captured via stdout
    M->>M: parseViolation()
    M-->>M: Log to stderr
```
**Sources:** [internal/sandbox/monitor.go:35-60](), [internal/sandbox/monitor.go:104-144]()

Each session is assigned a unique `sessionSuffix` [internal/sandbox/macos.go:19-27]() which is included in the Seatbelt profile's `with message` clause [internal/sandbox/macos.go:424-431](). The `LogMonitor` uses a predicate to filter for this suffix [internal/sandbox/monitor.go:44-50]().

For details, see [Unified Log Monitoring](#4.2.2).

## Learning Mode
On macOS, greywall uses `eslogger` to record process activity and generate suggested profiles. The `generateLearnedTemplatePlatform` function [internal/sandbox/manager_darwin.go:13-41]() handles stopping the logger and invoking `ParseEsloggerLog` to analyze the results.

**Sources:** [internal/sandbox/manager_darwin.go:13-41]()

---

# Page: Seatbelt Profile Generation

# Seatbelt Profile Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)

</details>



This page documents how greywall generates Seatbelt profiles for macOS sandboxing. Seatbelt is macOS's sandbox policy language that defines what operations a process can perform. The profile generation system translates greywall's configuration into Seatbelt's S-expression-based policy format, implementing deny-by-default security, network restrictions, and filesystem access control.

For information about the broader macOS sandboxing architecture and how profiles are executed, see [macOS Sandboxing](#4.2). For details on monitoring violations in generated profiles, see [Unified Log Monitoring](#4.2.2).

## Overview

The profile generation process transforms greywall's configuration model into a Seatbelt profile that the macOS `sandbox-exec` utility can enforce. The system handles:

- **Network isolation**: Restricting outbound connections to specific proxy hosts while allowing localhost binding [internal/sandbox/macos.go:576-619]().
- **Filesystem access control**: Implementing deny-by-default reads and writes with path-based rules [internal/sandbox/macos.go:156-361]().
- **Essential permissions**: Providing minimal system access for process execution, IPC, and device I/O [internal/sandbox/macos.go:433-574]().
- **Violation tracking**: Embedding log tags for unified log monitoring [internal/sandbox/macos.go:424-431]().

The generation pipeline takes `MacOSSandboxParams` [internal/sandbox/macos.go:30-54]() as input and produces a complete Seatbelt profile string ready for execution.

**Sources**: [internal/sandbox/macos.go:422-645]()

## Profile Generation Pipeline

The following diagram maps the configuration flow from the Go `config` package through the macOS-specific sandbox parameters to the final Seatbelt profile string.

```mermaid
graph TB
    Config["config.Config<br/>internal/config/config.go"]
    WrapCommandMacOS["WrapCommandMacOS()<br/>internal/sandbox/macos.go:647"]
    MacOSSandboxParams["MacOSSandboxParams<br/>internal/sandbox/macos.go:30"]
    GenerateSandboxProfile["GenerateSandboxProfile()<br/>internal/sandbox/macos.go:422"]
    
    generateReadRules["generateReadRules()<br/>internal/sandbox/macos.go:156"]
    generateWriteRules["generateWriteRules()<br/>internal/sandbox/macos.go:286"]
    NetworkRules["Network Rules Section<br/>internal/sandbox/macos.go:576"]
    EssentialPerms["Essential Permissions Section<br/>internal/sandbox/macos.go:433"]
    
    Profile["Seatbelt Profile String"]
    sandboxexec["sandbox-exec -p"]
    
    Config --> WrapCommandMacOS
    WrapCommandMacOS --> MacOSSandboxParams
    MacOSSandboxParams --> GenerateSandboxProfile
    
    GenerateSandboxProfile --> EssentialPerms
    GenerateSandboxProfile --> NetworkRules
    GenerateSandboxProfile --> generateReadRules
    GenerateSandboxProfile --> generateWriteRules
    
    EssentialPerms --> Profile
    NetworkRules --> Profile
    generateReadRules --> Profile
    generateWriteRules --> Profile
    
    Profile --> sandboxexec
```

The `WrapCommandMacOS` [internal/sandbox/macos.go:647-748]() function orchestrates the generation process by extracting configuration parameters, parsing proxy URLs, and calling `GenerateSandboxProfile`. The resulting profile is passed directly to `sandbox-exec` via the `-p` flag.

**Sources**: [internal/sandbox/macos.go:647-748](), [internal/sandbox/macos.go:422-645]()

## Seatbelt Profile Structure

A generated Seatbelt profile follows this structure:

```
(version 1)
(deny default (with message "CMD64_<encoded-command>_END_<session>"))

; LogTag: CMD64_<encoded-command>_END_<session>

; Essential permissions - process, IPC, IOKit, sysctl
; Network restrictions
; File read rules
; File write rules
; PTY support (optional)
```

The profile uses S-expression syntax where each statement is a parenthesized list. The main statement types are:

| Statement Type | Purpose | Example |
|----------------|---------|---------|
| `(deny default ...)` | Sets default deny with log tag | `(deny default (with message "CMD64_..."))` [internal/sandbox/macos.go:426]() |
| `(allow operation)` | Grants blanket permission | `(allow file-read-metadata)` [internal/sandbox/macos.go:166]() |
| `(allow operation (filter))` | Conditional permission | `(allow file-read-data (subpath "/usr"))` [internal/sandbox/macos.go:173]() |
| `(deny operation (filter) (with message))` | Explicit denial with logging | `(deny file-read-data (literal "/home/user/.env"))` [internal/sandbox/macos.go:275]() |

**Sources**: [internal/sandbox/macos.go:426-431](), [internal/sandbox/macos.go:433-574]()

## Log Tag Embedding

Each profile embeds a unique log tag that identifies violations in the macOS unified log system. The tag encodes both the command being executed and a session identifier:

```
CMD64_<base64-encoded-command>_END_<session-suffix>_SBX
```

The tag generation process:

1. **Session suffix generation**: A 9-character hex string generated once per greywall process via `generateSessionSuffix` [internal/sandbox/macos.go:21-27]().
2. **Command encoding**: The command string is base64-encoded in `WrapCommandMacOS` [internal/sandbox/macos.go:653-655]() to handle special characters.
3. **Tag composition**: The components are concatenated with fixed delimiters in `GetLogTag` [internal/sandbox/sandbox.go:20-49]().

**Sources**: [internal/sandbox/macos.go:18-27](), [internal/sandbox/macos.go:424](), [internal/sandbox/sandbox.go:20-49]()

## Essential Permissions

The profile includes a comprehensive set of essential permissions required for basic process operation. These include:

### Process Permissions

```seatbelt
(allow process-exec)
(allow process-fork)
(allow process-info* (target same-sandbox))
(allow signal (target same-sandbox))
(allow mach-priv-task-port (target same-sandbox))
```

Allows process creation and signals, but only to processes within the same sandbox [internal/sandbox/macos.go:434-441]().

### Mach IPC Services

The profile allows connections to specific macOS system services via Mach IPC:

- `com.apple.logd` - logging service [internal/sandbox/macos.go:446]()
- `com.apple.system.opendirectoryd.*` - directory services [internal/sandbox/macos.go:452]()
- `com.apple.SecurityServer` - security operations [internal/sandbox/macos.go:456]()
- `com.apple.FSEvents` - filesystem event notifications [internal/sandbox/macos.go:460]()

**Sources**: [internal/sandbox/macos.go:434-465]()

### sysctl Access

Read access is granted to hardware and kernel information via `sysctl-read`:

```seatbelt
(allow sysctl-read
  (sysctl-name "hw.memsize")
  (sysctl-name "kern.version")
  (sysctl-name-prefix "machdep.cpu.")
)
```

**Sources**: [internal/sandbox/macos.go:482-542]()

### Device I/O

Terminal and random device access:

```seatbelt
(allow file-ioctl (literal "/dev/tty"))
(allow file-read-data file-write-data (regex #"^/dev/ttys"))
(allow file-read-data (literal "/dev/urandom"))
```

**Sources**: [internal/sandbox/macos.go:556-573]()

## Network Rule Generation

Network rules control outbound connections. The key insight is that **localhost binding is always allowed** to enable dev servers and OAuth callbacks, matching Linux behavior.

```mermaid
graph TB
    NeedsNetworkRestriction{"NeedsNetworkRestriction<br/>(MacOSSandboxParams)"}
    
    Unrestricted["(allow network*)<br/>internal/sandbox/macos.go:578"]
    
    LocalhostAlways["(allow network-bind<br/>(local ip 'localhost:*'))<br/>(allow network-inbound<br/>(local ip 'localhost:*'))<br/>internal/sandbox/macos.go:583"]
    
    AllowLocalOutbound{"AllowLocalOutbound<br/>(MacOSSandboxParams)"}
    LocalOutRule["(allow network-outbound<br/>(local ip 'localhost:*'))<br/>internal/sandbox/macos.go:593"]
    
    ProxyHost{"ProxyHost != ''<br/>internal/sandbox/macos.go:598"}
    SOCKS5Rule["(allow network-outbound<br/>(remote tcp 'host:port'))<br/>internal/sandbox/macos.go:600"]
    
    HTTPProxyHost{"HTTPProxyHost != ''<br/>internal/sandbox/macos.go:604"}
    HTTPRule["(allow network-outbound<br/>(remote tcp 'host:port'))<br/>internal/sandbox/macos.go:606"]
    
    DnsProxyHost{"DnsProxyHost != ''<br/>internal/sandbox/macos.go:610"}
    DNSRules["(allow network-outbound<br/>(remote tcp/udp 'host:port'))<br/>internal/sandbox/macos.go:612"]
    
    UnixSockets{"AllowAllUnixSockets or<br/>AllowUnixSockets list<br/>internal/sandbox/macos.go:616"}
    UnixRules["(allow network*<br/>(subpath 'path'))<br/>internal/sandbox/macos.go:618"]
    
    NeedsNetworkRestriction -->|false| Unrestricted
    NeedsNetworkRestriction -->|true| LocalhostAlways
    
    LocalhostAlways --> AllowLocalOutbound
    AllowLocalOutbound -->|true| LocalOutRule
    AllowLocalOutbound -->|false| ProxyHost
    LocalOutRule --> ProxyHost
    
    ProxyHost -->|true| SOCKS5Rule
    ProxyHost -->|false| HTTPProxyHost
    SOCKS5Rule --> HTTPProxyHost
    
    HTTPProxyHost -->|true| HTTPRule
    HTTPProxyHost -->|false| DnsProxyHost
    HTTPRule --> DnsProxyHost
    
    DnsProxyHost -->|true| DNSRules
    DnsProxyHost -->|false| UnixSockets
    DNSRules --> UnixSockets
    
    UnixSockets -->|configured| UnixRules
```

### Network Restriction Mode

When `NeedsNetworkRestriction` is true:

1. **Localhost binding**: Always allowed for inbound and binding operations [internal/sandbox/macos.go:583-591]().
2. **Proxy connections**: Allowed to specific proxy host:port combinations (SOCKS5, HTTP CONNECT, DNS) [internal/sandbox/macos.go:598-614]().
3. **Localhost outbound**: Optional (controlled by `AllowLocalOutbound`) [internal/sandbox/macos.go:593-596]().
4. **Unix sockets**: Either all paths or specific paths can be allowed [internal/sandbox/macos.go:616-619]().

**Sources**: [internal/sandbox/macos.go:576-619](), [internal/sandbox/macos_test.go:13-76]()

## Filesystem Read Rule Generation

The read rule generation implements deny-by-default security by distinguishing between metadata operations (which allow directory traversal and `stat` calls) and data operations (actual file content reads).

### Default Deny Read Mode

When `DefaultDenyRead` is true:

1. **Allow metadata globally**: `(allow file-read-metadata)` enables directory traversal [internal/sandbox/macos.go:166]().
2. **Allow data for root**: `(allow file-read-data (literal "/"))` enables path resolution [internal/sandbox/macos.go:167]().
3. **Allow system paths**: Paths from `GetDefaultReadablePaths()` are allowed via `subpath` rules [internal/sandbox/macos.go:170-175]().
4. **Allow CWD**: Current working directory gets full read access, plus ancestor directories for path resolution [internal/sandbox/macos.go:178-190]().
5. **Allow home caches**: Shell configs (`.bashrc`, `.zshrc`) and cache directories (`.cache`, `.npm`, `.cargo`) [internal/sandbox/macos.go:193-213]().
6. **Allow user paths**: Paths from `ReadAllowPaths` config field [internal/sandbox/macos.go:216-231]().
7. **Deny sensitive files**: `.env`, `.env.*`, and files from `SensitiveProjectFiles` are explicitly denied [internal/sandbox/macos.go:233-250]().

### Deny Rules Must Use Exact Operations

A critical implementation detail: deny rules **must use `file-read-data`**, not `file-read*`. Seatbelt ignores wildcard denies when a specific allow covers the same path. This is why the generated profile contains specific data denials [internal/sandbox/macos.go:275]().

**Sources**: [internal/sandbox/macos.go:154-282](), [internal/sandbox/macos_test.go:176-264]()

## Filesystem Write Rule Generation

Write rules are deny-by-default without needing explicit configuration. The system automatically allows:

1. **Current working directory**: Full write access to the project directory [internal/sandbox/macos.go:290-294]().
2. **TMPDIR parent**: For macOS's per-user temp directories (`/var/folders/XX/YYY/T/`) [internal/sandbox/macos.go:297-302]().
3. **User-specified paths**: From `WriteAllowPaths` config field [internal/sandbox/macos.go:305-320]().

Then applies deny rules for:

1. **Mandatory denies**: Shell startup files (`.bashrc`, `.zshrc`, etc.), git hooks, npm config [internal/sandbox/macos.go:329-336]().
2. **User denies**: Paths from `WriteDenyPaths` config field [internal/sandbox/macos.go:339-354]().

**Sources**: [internal/sandbox/macos.go:286-361](), [internal/sandbox/sandbox.go:78-127]()

## Path Handling and Normalization

Several helper functions handle path manipulation for Seatbelt profiles:

### Glob to Regex Conversion

`GlobToRegex` [internal/sandbox/macos.go:56-72]() converts shell-style glob patterns to regex patterns for Seatbelt's `(regex)` filter. It handles `**` before `*` to ensure correct precedence [internal/sandbox/macos.go:64-67]().

### Path Escaping

`escapePath` [internal/sandbox/macos.go:74-78]() uses Go's string quoting to escape paths for Seatbelt profiles, handling special characters like quotes and backslashes.

### macOS /tmp Symlink Handling

`expandMacOSTmpPaths` [internal/sandbox/macos.go:96-127]() mirrors paths between `/tmp` and `/private/tmp` because `/tmp` is a symlink to `/private/tmp` on macOS. The profile includes both variants to ensure rules match kernel-resolved paths.

**Sources**: [internal/sandbox/macos.go:96-127](), [internal/sandbox/macos_test.go:369-434]()

## Move Blocking Rules

To prevent bypassing deny rules via file moves, `generateMoveBlockingRules` [internal/sandbox/macos.go:363-420]() adds `file-write-unlink` denials for the denied path and its ancestors [internal/sandbox/macos.go:383-394](). This prevents moving a denied file or its parent directory to an allowed location.

**Sources**: [internal/sandbox/macos.go:363-420]()

## Profile Composition

The final profile assembly in `GenerateSandboxProfile` [internal/sandbox/macos.go:422-645]() builds the profile sequentially using a `strings.Builder`.

```mermaid
graph LR
    Header["Version + deny default<br/>+ log tag<br/>internal/sandbox/macos.go:423"]
    Essential["Essential permissions<br/>internal/sandbox/macos.go:433"]
    Network["Network rules<br/>internal/sandbox/macos.go:576"]
    Read["Read rules<br/>internal/sandbox/macos.go:622"]
    Write["Write rules<br/>internal/sandbox/macos.go:629"]
    PTY["PTY support (optional)<br/>internal/sandbox/macos.go:635"]
    
    Final["Complete Seatbelt Profile"]
    
    Header --> Essential
    Essential --> Network
    Network --> Read
    Read --> Write
    Write --> PTY
    PTY --> Final
```

**Sources**: [internal/sandbox/macos.go:422-645]()

## Testing

The test suite in `macos_test.go` verifies profile generation correctness, including network restrictions [internal/sandbox/macos_test.go:13-76](), default deny read logic [internal/sandbox/macos_test.go:176-264](), and path expansion [internal/sandbox/macos_test.go:369-434](). Integration tests in `integration_macos_test.go` verify that the generated profiles correctly block writes outside workspace [internal/sandbox/integration_macos_test.go:19-32]() and protect sensitive files like `.env` [internal/sandbox/integration_macos_test.go:175-195]().

**Sources**: [internal/sandbox/macos_test.go:1-434](), [internal/sandbox/integration_macos_test.go:1-210]()

---

# Page: Unified Log Monitoring

# Unified Log Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/learning_darwin.go](internal/sandbox/learning_darwin.go)
- [internal/sandbox/learning_darwin_test.go](internal/sandbox/learning_darwin_test.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)

</details>



This document describes macOS-specific sandbox violation monitoring through the unified logging system. Greywall on macOS uses the `log stream` command to monitor sandbox policy violations in real-time by filtering the system-wide unified log for violations tagged with a unique session identifier.

For Linux-based violation monitoring using eBPF, see [eBPF Violation Monitoring](). For details on how Seatbelt profiles are generated, see [Seatbelt Profile Generation]().

---

## Monitoring Architecture

macOS sandbox violations are reported through the unified logging subsystem whenever a sandboxed process attempts an operation denied by the Seatbelt profile. Greywall monitors these violations by:

1. Generating a unique session suffix for each sandbox invocation.
2. Embedding this suffix in all deny rules within the Seatbelt profile using the `(with message "...")` clause.
3. Streaming the unified log and filtering for messages containing the session suffix.
4. Parsing violation entries and displaying them to stderr.

```mermaid
graph TB
    subgraph "Sandbox Initialization"
        GEN["generateSessionSuffix()<br/>[internal/sandbox/macos.go:21-27]"]
        PROFILE["GenerateSandboxProfile()<br/>[internal/sandbox/macos.go:391-450]"]
        EXEC["sandbox-exec -p profile"]
    end
    
    subgraph "Sandboxed Process"
        APP["Application Code"]
        ATTEMPT["Denied Operation<br/>(file-read, file-write, network)"]
        KERNEL["macOS Kernel<br/>Sandbox enforcement"]
    end
    
    subgraph "Unified Log System"
        SYSLOG["Unified Log<br/>com.apple.sandbox.reporting"]
        STREAM["log stream --predicate<br/>eventMessage ENDSWITH suffix"]
    end
    
    subgraph "LogMonitor"
        MONITOR["LogMonitor.Start()<br/>[internal/sandbox/monitor.go:36-78]"]
        SCANNER["bufio.Scanner<br/>Reads log lines"]
        PARSER["parseViolation()<br/>[internal/sandbox/monitor.go:101-145]"]
        FILTER["Filtering Logic<br/>shouldShowViolation()<br/>isNoisyViolation()"]
        OUTPUT["stderr output<br/>Formatted violation"]
    end
    
    GEN --> PROFILE
    PROFILE --> EXEC
    EXEC --> APP
    APP --> ATTEMPT
    ATTEMPT --> KERNEL
    KERNEL -->|"Logs denial with<br/>session suffix"| SYSLOG
    
    MONITOR --> STREAM
    STREAM --> SYSLOG
    SYSLOG --> SCANNER
    SCANNER --> PARSER
    PARSER --> FILTER
    FILTER --> OUTPUT
```

**Diagram: macOS Unified Log Monitoring Flow**

Sources: [internal/sandbox/monitor.go:16-79](), [internal/sandbox/macos.go:18-27](), [internal/sandbox/macos.go:422-431]()

---

## Session Suffix Generation

Each sandbox invocation generates a unique session suffix to isolate its log entries from other concurrent greywall processes. The suffix is a 9-character hexadecimal string followed by `_SBX`.

### Generation Process

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Random bytes | `crypto/rand.Read(8 bytes)` | Cryptographic randomness |
| Encoding | `hex.EncodeToString()[:9]` | Human-readable identifier |
| Suffix format | `"_" + hex + "_SBX"` | Pattern: `_a1b2c3d4e_SBX` |

The session suffix is generated once per greywall process at package initialization:

[internal/sandbox/macos.go:18-27]()
```go
var sessionSuffix = generateSessionSuffix()

func generateSessionSuffix() string {
	bytes := make([]byte, 8)
	if _, err := rand.Read(bytes); err != nil {
		panic("failed to generate session suffix: " + err.Error())
	}
	return "_" + hex.EncodeToString(bytes)[:9] + "_SBX"
}
```

### Profile Integration

The session suffix is embedded in every deny rule within the Seatbelt profile using the `(with message "...")` clause. This tags all violations from this sandbox session:

[internal/sandbox/macos.go:422-431]()
```go
// Example of rule generation in GenerateSandboxProfile
rules = append(rules,
    "(deny file-read*",
    fmt.Sprintf("  (with message %q))", "CMD64_"+params.Command+"_END"+sessionSuffix),
)
```

Sources: [internal/sandbox/macos.go:18-27](), [internal/sandbox/macos.go:424](), [internal/sandbox/macos.go:430]()

---

## LogMonitor Implementation

The `LogMonitor` struct manages the lifecycle of the `log stream` process that monitors violations.

### Structure Definition

```mermaid
classDiagram
    class LogMonitor {
        -sessionSuffix string
        -cmd *exec.Cmd
        -cancel context.CancelFunc
        -running bool
        +NewLogMonitor(sessionSuffix) *LogMonitor
        +Start() error
        +Stop()
    }
    
    class exec_Cmd {
        Process *os.Process
        StdoutPipe io.ReadCloser
    }
    
    LogMonitor --> exec_Cmd : "manages [internal/sandbox/monitor.go:19]"
```

**Diagram: LogMonitor Class Structure**

| Field | Type | Purpose |
|-------|------|---------|
| `sessionSuffix` | `string` | Unique identifier for filtering this session's violations |
| `cmd` | `*exec.Cmd` | The running `log stream` process |
| `cancel` | `context.CancelFunc` | Context cancellation for stopping the monitor |
| `running` | `bool` | Tracks whether the monitor is active |

Sources: [internal/sandbox/monitor.go:17-22]()

### Start Method

The `Start` method spawns the `log stream` process with a predicate filter. It constructs a predicate using the `sessionSuffix` to ensure only relevant violations are captured.

[internal/sandbox/monitor.go:45-50]()
```go
predicate := fmt.Sprintf(`eventMessage ENDSWITH "%s"`, m.sessionSuffix)

m.cmd = exec.CommandContext(ctx, "log", "stream",
    "--predicate", predicate,
    "--style", "compact",
)
```

| Flag | Value | Purpose |
|------|-------|---------|
| `--predicate` | `eventMessage ENDSWITH "..."` | Filter for session violations only |
| `--style` | `compact` | Simplified output format (timestamp + message) |

Sources: [internal/sandbox/monitor.go:36-78]()

---

## Violation Parsing and Filtering

The `parseViolation` function extracts structured information from raw log entries and filters out noise.

### Parsing Pattern

[internal/sandbox/monitor.go:102]()
```go
var violationPattern = regexp.MustCompile(`Sandbox: (\w+)\((\d+)\) deny\(\d+\) (\S+)(.*)`)
```

| Capture Group | Content | Example |
|---------------|---------|---------|
| `\w+` | Process name | `python` |
| `\d+` | Process ID | `12345` |
| `\S+` | Operation type | `file-read-data` |
| `.*` | Details (path, address, etc.) | `/etc/passwd` |

Sources: [internal/sandbox/monitor.go:102-144]()

### Operation Type Filtering

The `shouldShowViolation` function determines which operation types are relevant. It specifically targets network and filesystem operations.

[internal/sandbox/monitor.go:147-159]()
```go
func shouldShowViolation(operation string) bool {
	if strings.HasPrefix(operation, "network-") {
		return true
	}
	if strings.HasPrefix(operation, "file-read") ||
		strings.HasPrefix(operation, "file-write") {
		return true
	}
	return false
}
```

Sources: [internal/sandbox/monitor.go:147-159]()

### Noise Filtering

The `isNoisyViolation` function filters system-level operations that generate excessive false positives, such as TTY access or system logging sockets.

[internal/sandbox/monitor.go:162-180]()
```go
func isNoisyViolation(details string) bool {
	if strings.HasPrefix(details, "/dev/tty") ||
		strings.HasPrefix(details, "/dev/pts") {
		return true
	}
	if strings.Contains(details, "mDNSResponder") {
		return true
	}
	if strings.HasPrefix(details, "/private/var/run/syslog") {
		return true
	}
	return false
}
```

Sources: [internal/sandbox/monitor.go:162-180]()

---

## Comparison with Learning Mode (eslogger)

While `LogMonitor` handles real-time violation reporting for security enforcement, Greywall also uses `eslogger` for its **Learning Mode** on macOS. 

| Aspect | Real-time Monitoring (`log stream`) | Learning Mode (`eslogger`) |
|--------|------------------------------------|----------------------------|
| **Primary File** | [internal/sandbox/monitor.go]() | [internal/sandbox/learning_darwin.go]() |
| **Purpose** | Security violation alerting | Profile generation via tracing |
| **Data Format** | Text-based Unified Log | JSON-based Endpoint Security events |
| **Parsing Logic** | `parseViolation` [internal/sandbox/monitor.go:101]() | `ParseEsloggerLog` [internal/sandbox/learning_darwin.go:129]() |
| **Event Types** | Sandbox denials | All successful file/fork operations |

`ParseEsloggerLog` implements a two-pass approach: 
1. **Pass 1**: Scans `fork` events to build a PID tree starting from the root process [internal/sandbox/learning_darwin.go:135-153]().
2. **Pass 2**: Filters filesystem events (open, create, write, etc.) by that PID set to generate path lists [internal/sandbox/learning_darwin.go:159-223]().

Sources: [internal/sandbox/learning_darwin.go:129-235](), [internal/sandbox/monitor.go:1-187]()

---

# Page: Network Architecture

# Network Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/proxy/detect.go](internal/proxy/detect.go)
- [internal/proxy/install.go](internal/proxy/install.go)
- [internal/proxy/start.go](internal/proxy/start.go)
- [internal/sandbox/color.go](internal/sandbox/color.go)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_features_stub.go](internal/sandbox/linux_features_stub.go)

</details>



This document provides a comprehensive overview of greywall's network isolation architecture. It explains how sandboxed processes are prevented from making unauthorized network connections, how traffic is routed through the greyproxy filtering proxy, and the platform-specific implementations on Linux and macOS.

For details on the greyproxy service itself (installation, configuration, dashboard), see [greyproxy Service](#5.1). For implementation details of Unix socket bridges on Linux, see [Proxy Bridges and Unix Sockets](#5.2). For domain-based filtering rules and allow/deny lists, see [Domain-Based Filtering](#5.3).

For the complete Linux sandboxing implementation including filesystem and syscall controls, see [Linux Sandboxing](#4.1). For macOS sandboxing details, see [macOS Sandboxing](#4.2).

## Overview

Greywall implements network isolation through a two-layer architecture:

1. **Sandbox Layer**: Platform-specific mechanisms (network namespaces on Linux, Seatbelt profiles on macOS) that isolate the sandboxed process from the host network stack.
2. **Proxy Layer**: The greyproxy service that provides centralized traffic filtering, domain-based allow/deny rules, and an optional upstream SOCKS5 proxy chain.

All network traffic from sandboxed processes is routed through greyproxy, which listens on localhost ports 43052 (SOCKS5), 43051 (HTTP CONNECT), and 43053 (DNS). The dashboard runs on port 43080.

**Key Design Principles:**

- **Deny-by-default**: Network access is blocked unless explicitly allowed via greyproxy's domain filtering rules.
- **Transparent on Linux**: Network redirection happens at the kernel level using TUN devices and network namespaces, requiring no application awareness.
- **Environment-based on macOS**: Applications must respect `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` environment variables.
- **Centralized filtering**: All traffic converges at greyproxy regardless of platform, enabling consistent policy enforcement.

Sources: [internal/sandbox/linux.go:21-41](), [internal/proxy/detect.go:15-18]()

## Two-Layer Network Isolation

```mermaid
graph TB
    subgraph "Sandboxed Process"
        APP["Application Code"]
        NETCALL["Network Request<br/>(connect/bind/socket)"]
    end
    
    subgraph "Layer 1: OS Sandbox Isolation"
        LINUX_NS["Linux: Network Namespace<br/>--unshare-net<br/>Isolated network stack"]
        MACOS_SEATBELT["macOS: Seatbelt Profile<br/>network-outbound rules<br/>Environment variables"]
    end
    
    subgraph "Layer 2: greyproxy Filtering"
        GP_SOCKS["SOCKS5 Server<br/>localhost:43052"]
        GP_HTTP["HTTP CONNECT<br/>localhost:43051"]
        GP_DNS["DNS Server<br/>localhost:43053"]
        GP_RULES["Domain Rules Engine<br/>allowedDomains<br/>deniedDomains"]
    end
    
    subgraph "External Network"
        INTERNET["Internet"]
        UPSTREAM["Optional Upstream SOCKS5<br/>(configured via --proxy)"]
    end
    
    APP --> NETCALL
    
    NETCALL -->|"Linux path"| LINUX_NS
    NETCALL -->|"macOS path"| MACOS_SEATBELT
    
    LINUX_NS --> GP_SOCKS
    LINUX_NS --> GP_DNS
    MACOS_SEATBELT --> GP_SOCKS
    MACOS_SEATBELT --> GP_HTTP
    
    GP_SOCKS --> GP_RULES
    GP_HTTP --> GP_RULES
    GP_DNS --> GP_RULES
    
    GP_RULES -->|"allowed"| INTERNET
    GP_RULES -->|"denied"| APP
    GP_RULES -.->|"optional chain"| UPSTREAM
    UPSTREAM --> INTERNET
```

**Layer 1** isolates the sandboxed process from the host network using platform-specific OS mechanisms. On Linux, this creates a completely separate network namespace with no connectivity except through controlled bridges. On macOS, Seatbelt profiles restrict network operations and environment variables point applications to the proxy.

**Layer 2** provides application-layer filtering through greyproxy. All traffic that escapes Layer 1 must pass through greyproxy's domain-based filtering, which maintains allow/deny lists and provides real-time traffic inspection via the dashboard.

Sources: [internal/sandbox/linux.go:21-41](), [internal/proxy/detect.go:30-36]()

## Platform-Specific Implementations

### Linux: Transparent Network Proxying

Linux achieves transparent network proxying through a sophisticated multi-component system that requires no application cooperation:

```mermaid
graph TB
    subgraph "Inside Network Namespace"
        APP["Sandboxed Process"]
        TUNDEV["TUN Device: tun0<br/>IP: 198.18.0.1/15<br/>Default gateway"]
        T2S["tun2socks Process<br/>gvisor netstack<br/>Packet -> SOCKS5 conversion"]
        SOCAT_PROXY["socat Process<br/>TCP :18321 -> Unix socket"]
        SOCAT_DNS["socat Process<br/>UDP :53 -> Unix socket"]
        SOCAT_REV["socat Processes<br/>Unix socket -> SOCKS5"]
    end
    
    subgraph "Host Side (Outside Namespace)"
        PROXY_SOCK["ProxyBridge Unix Socket<br/>/tmp/greywall-proxy-*.sock"]
        DNS_SOCK["DnsBridge Unix Socket<br/>/tmp/greywall-dns-*.sock"]
        REV_SOCK["ReverseBridge Unix Sockets<br/>/tmp/greywall-rev-*-*.sock"]
        GP["greyproxy Service<br/>localhost:43052/43051/43053"]
    end
    
    APP -->|"All network traffic"| TUNDEV
    TUNDEV -->|"Raw IP packets"| T2S
    T2S -->|"SOCKS5 to 127.0.0.1:18321"| SOCAT_PROXY
    APP -->|"DNS queries to :53"| SOCAT_DNS
    APP -->|"Inbound connections"| SOCAT_REV
    
    SOCAT_PROXY -.->|"Crosses namespace boundary"| PROXY_SOCK
    SOCAT_DNS -.->|"Crosses namespace boundary"| DNS_SOCK
    SOCAT_REV -.->|"Crosses namespace boundary"| REV_SOCK
    
    PROXY_SOCK --> GP
    DNS_SOCK --> GP
    REV_SOCK --> GP
```

**Component Breakdown:**

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| **Network Namespace** | Complete network isolation via `--unshare-net` | Created by bubblewrap, loopback-only by default |
| **TUN Device (tun0)** | Virtual network interface as default route | 198.18.0.1/15 address, created inside namespace |
| **tun2socks** | Converts raw IP packets to SOCKS5 proxy requests | Uses gvisor netstack, binds to SOCKS5 at 127.0.0.1:18321 |
| **ProxyBridge** | Bridges SOCKS5 traffic across namespace boundary | `socat` relay: TCP :18321 -> Unix socket -> greyproxy |
| **DnsBridge** | Bridges DNS queries across namespace boundary | `socat` relay: UDP :53 -> Unix socket -> greyproxy DNS |
| **ReverseBridge** | Enables inbound connections for dev servers | `socat` relay: Unix socket -> SOCKS5 for exposed ports |

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:36-41](), [internal/sandbox/linux.go:105-111](), [internal/sandbox/linux_features_stub.go:13-29]()

### macOS: Environment Variable Proxy Configuration

macOS uses a simpler approach based on proxy environment variables, as macOS `sandbox-exec` does not support network namespace isolation:

```mermaid
graph LR
    subgraph "Sandboxed Process"
        APP["Application"]
        ENV["Environment Variables:<br/>HTTP_PROXY=http://localhost:43051<br/>HTTPS_PROXY=http://localhost:43051<br/>ALL_PROXY=socks5://localhost:43052"]
    end
    
    subgraph "Host Network Stack"
        GP["greyproxy Service<br/>SOCKS5: :43052<br/>HTTP CONNECT: :43051"]
    end
    
    APP --> ENV
    ENV -->|"Application must<br/>respect proxy vars"| GP
```

**Key Differences from Linux:**

- No transparent proxying capability (applications must respect proxy environment variables).
- DNS queries cannot be reliably intercepted (no DNS bridge).
- No network namespace isolation (relies on Seatbelt `network-outbound` rules).

Sources: [internal/sandbox/linux_features_stub.go:63-71]()

## Network Traffic Flow

The following sequence diagram shows the complete flow of a network request from a sandboxed process to the external network on Linux:

```mermaid
sequenceDiagram
    participant App as "Sandboxed Process"
    participant Namespace as "Network Namespace"
    participant TUN as "TUN Device tun0"
    participant T2S as "tun2socks"
    participant Socat as "socat Bridge"
    participant UnixSock as "Unix Socket"
    participant Greyproxy as "greyproxy Service"
    
    App->>Namespace: connect("example.com", 443)
    Namespace->>TUN: Route via default gateway (198.18.0.1)
    TUN->>T2S: Raw IP packet
    T2S->>T2S: Parse packet, extract destination
    T2S->>Socat: SOCKS5 CONNECT example.com:443
    Socat->>UnixSock: Forward to Unix socket
    UnixSock->>Greyproxy: SOCKS5 request
    
    Note over Greyproxy: Apply Domain Rules
    
    Greyproxy->>Internet: Establish connection
```

Sources: [internal/sandbox/linux.go:65-69](), [internal/sandbox/linux.go:175-179]()

## Component Architecture

### ProxyBridge (Linux)

The `ProxyBridge` struct manages the Unix socket bridge between the network namespace and the host-side greyproxy service.

```mermaid
graph LR
    subgraph "ProxyBridge Creation"
        NEW["NewProxyBridge()"]
        PARSE["parseProxyURL()"]
        SOCK["Generate SocketPath"]
        SOCAT["exec.Command(socat)"]
    end
    
    subgraph "ProxyBridge Entity"
        SOCKET["SocketPath string"]
        HOST["ProxyHost string"]
        PORT["ProxyPort string"]
        PROC["process *exec.Cmd"]
    end
    
    NEW --> PARSE
    PARSE --> SOCK
    SOCK --> SOCAT
    SOCAT --> PROC
```

**Key Methods:**

- `NewProxyBridge()` - Creates bridge, starts `socat`, waits for socket file [internal/sandbox/linux.go:141-200]().
- `Cleanup()` - Kills `socat` process, removes socket file [internal/sandbox/linux.go:203-213]().
- `parseProxyURL()` - Validates and parses SOCKS5 URL [internal/sandbox/linux.go:216-224]().

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:141-213]()

### DnsBridge (Linux)

The `DnsBridge` provides DNS resolution inside the network namespace by bridging UDP DNS queries to the host-side greyproxy DNS server.

**Key Methods:**

- `NewDnsBridge()` - Creates a Unix socket bridge to a host-side DNS server [internal/sandbox/linux.go:44-90]().
- `Cleanup()` - Stops the DNS bridge and removes the socket file [internal/sandbox/linux.go:93-103]().

Sources: [internal/sandbox/linux.go:36-41](), [internal/sandbox/linux.go:44-103]()

### greyproxy Service Integration

The greyproxy service is a separate binary that greywall depends on. It is automatically installed and managed by greywall.

| Operation | Code Path | Description |
|-----------|-----------|-------------|
| **Detection** | `proxy.Detect()` | Checks if greyproxy is installed and running via health endpoint [internal/proxy/detect.go:43-63](). |
| **Installation** | `proxy.Install()` | Downloads latest release from GitHub, extracts, and installs [internal/proxy/install.go:87-153](). |
| **Starting** | `proxy.Start()` | Runs `greyproxy service start` [internal/proxy/start.go:11-30](). |
| **Health Check** | `proxy.checkRunning()` | Hits `http://localhost:43080/api/health` [internal/proxy/detect.go:95-126](). |

The greyproxy health endpoint returns a `healthResponse` struct [internal/proxy/detect.go:31-36]().

Sources: [internal/proxy/detect.go:1-127](), [internal/proxy/install.go:1-153](), [internal/proxy/start.go:1-30]()

## Network Configuration

### Default Ports and URLs

Greywall uses the following defaults for network monitoring and proxying:

- **Health URL**: `http://localhost:43080/api/health` [internal/proxy/detect.go:16]().
- **GitHub Repository**: `greyhavenhq/greyproxy` [internal/proxy/install.go:21-22]().

### Proxy URL Configuration

The `ProxyBridge` captures credentials from the proxy URL if provided:
- `ProxyUser`: Username from ProxyURL [internal/sandbox/linux.go:26]().
- `ProxyPass`: Password from ProxyURL [internal/sandbox/linux.go:27]().
- `HasAuth`: Boolean indicating if credentials were provided [internal/sandbox/linux.go:28]().

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:168-172]()

---

# Page: greyproxy Service

# greyproxy Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yaml](.goreleaser.yaml)
- [internal/proxy/brew.go](internal/proxy/brew.go)
- [internal/proxy/detect.go](internal/proxy/detect.go)
- [internal/proxy/install.go](internal/proxy/install.go)
- [internal/proxy/start.go](internal/proxy/start.go)
- [internal/sandbox/color.go](internal/sandbox/color.go)
- [internal/sandbox/linux_features_stub.go](internal/sandbox/linux_features_stub.go)

</details>



This page documents the `greyproxy` service component, which provides network isolation and domain-based filtering for `greywall`. For information about how `greywall` creates proxy bridges to connect to `greyproxy`, see [Proxy Bridges and Unix Sockets](#5.2). For details on domain filtering rules, see [Domain-Based Filtering](#5.3).

## Overview

`greyproxy` is a standalone service that implements deny-by-default network filtering for sandboxed processes. It is a separate binary developed in the `GreyhavenHQ/greyproxy` repository and is managed as a dependency of `greywall`.

`greyproxy` provides four network services on localhost:
- **SOCKS5 server** (port 43052) - Primary proxy endpoint
- **HTTP CONNECT proxy** (port 43051) - HTTP/HTTPS proxy endpoint
- **DNS server** (port 43053) - DNS resolution with domain filtering
- **Dashboard UI** (port 43080) - Web interface for monitoring and control

All network traffic from sandboxed processes is routed through `greyproxy`, which enforces domain-based allow/deny rules and provides visibility into network activity.

**Sources:** [internal/proxy/detect.go:16](), [.goreleaser.yaml:105-108]()

## Service Architecture

The following diagram illustrates how the `internal/proxy` package in `greywall` interacts with the `greyproxy` binary and its network services.

```mermaid
graph TB
    subgraph "greyproxy Service (localhost)"
        SOCKS5["SOCKS5 Server<br/>Port 43052"]
        HTTP["HTTP CONNECT Server<br/>Port 43051"]
        DNS["DNS Server<br/>Port 43053"]
        DASHBOARD["Dashboard UI<br/>Port 43080<br/>/api/health"]
        FILTER["Domain Filter<br/>Allow/Deny Rules"]
    end
    
    subgraph "greywall internal/proxy"
        DETECT["proxy.Detect()<br/>detect.go"]
        INSTALL["proxy.Install()<br/>install.go"]
        START["proxy.Start()<br/>start.go"]
    end
    
    subgraph "Sandboxed Process"
        APP["Application"]
    end
    
    APP --> SOCKS5
    APP --> HTTP
    APP --> DNS
    
    SOCKS5 --> FILTER
    HTTP --> FILTER
    DNS --> FILTER
    
    DETECT -->|"checkRunning()"| DASHBOARD
    DETECT -->|"checkInstalled()"| SOCKS5
    INSTALL -->|"runGreyproxyInstall()"| SOCKS5
    START -->|"greyproxy service start"| SOCKS5
    
    FILTER --> INTERNET["Internet"]
```

**Sources:** [internal/proxy/detect.go:1-127](), [internal/proxy/start.go:1-31](), [internal/proxy/install.go:1-153]()

## Installation and Management

### Automatic Installation via Homebrew

When `greywall` is installed via Homebrew, `greyproxy` is listed as a mandatory dependency [ .goreleaser.yaml:104-105 ](). The Homebrew formula includes caveats pointing users to the dashboard at `http://localhost:43080` [ .goreleaser.yaml:106-108 ]().

### Manual Installation Logic

The `proxy.Install()` function [ internal/proxy/install.go:87-153 ]() handles the lifecycle of fetching and setting up the binary:

1.  **Environment Check**: Installation can be skipped by setting `GREYWALL_NO_GREYPROXY_INSTALL=1` [ internal/proxy/install.go:88-90 ]().
2.  **Release Discovery**: `fetchLatestRelease()` queries the GitHub API [ internal/proxy/install.go:156-186 ]().
3.  **Asset Resolution**: `resolveAssetURL()` matches the current `runtime.GOOS` and `runtime.GOARCH` to the correct `.tar.gz` asset [ internal/proxy/install.go:188-202 ]().
4.  **Execution**: After downloading and extracting, it executes `greyproxy install` to place the binary in the system path (typically `~/.local/bin`) [ internal/proxy/install.go:135-137 ]().

```mermaid
sequenceDiagram
    participant G as greywall (proxy.Install)
    participant GH as GitHub API
    participant B as greyproxy Binary
    
    G->>GH: fetchLatestRelease()
    GH-->>G: Latest Tag & Assets
    G->>G: resolveAssetURL(runtime.GOOS, runtime.GOARCH)
    G->>GH: downloadAsset()
    G->>G: extractTarGz()
    G->>B: exec("greyproxy install")
    B-->>G: Success
    G->>G: Detect() verification
```

**Sources:** [internal/proxy/install.go:87-153](), [internal/proxy/install.go:188-202]()

## Service Detection and Health

### Detection Logic

The `Detect()` function in `internal/proxy/detect.go` provides a comprehensive status of the proxy service without returning errors, instead capturing failures in the `GreyproxyStatus` struct [ internal/proxy/detect.go:43-63 ]().

| Field | Description | Implementation |
| :--- | :--- | :--- |
| `Installed` | Binary exists on PATH | `exec.LookPath("greyproxy")` [ internal/proxy/detect.go:66-72 ]() |
| `Path` | Location of binary | Result of `LookPath` |
| `Version` | Semantic version string | Parsed from `greyproxy -V` [ internal/proxy/detect.go:76-90 ]() or health API |
| `Running` | Service is active | `GET /api/health` check [ internal/proxy/detect.go:95-126 ]() |

### Health Check Protocol

`greywall` verifies the service is actually `greyproxy` (and not another process occupying the port) by checking the `service` field in the JSON response from `http://localhost:43080/api/health` [ internal/proxy/detect.go:116-123 ]().

**Sources:** [internal/proxy/detect.go:21-36](), [internal/proxy/detect.go:95-126]()

## Version Management

`greywall` includes utilities to ensure the proxy dependency is up to date.

*   **`CheckLatestVersion()`**: Fetches the latest tag from GitHub and trims the "v" prefix [ internal/proxy/install.go:45-51 ]().
*   **`IsOlderVersion(current, latest)`**: Implements a semantic version comparison. It splits strings by `.` and compares major, minor, and patch integers [ internal/proxy/install.go:56-83 ](). If the current version is not a valid semver (e.g., "dev"), it is treated as older [ internal/proxy/install.go:63-65 ]().

**Sources:** [internal/proxy/install.go:43-83]()

## Platform Specifics

### Homebrew Management
The `IsBrewManaged()` function checks if the `greyproxy` binary resides within the Homebrew prefix (retrieved via `brew --prefix`) [ internal/proxy/brew.go:10-30 ](). This helps `greywall` decide whether to attempt an internal update or defer to the package manager.

### Linux vs macOS Capabilities
While `greyproxy` provides the network filtering layer, the ability to route traffic to it depends on platform-specific features described in `LinuxFeatures` [ internal/sandbox/linux_features_stub.go:13-29 ]():
*   **Linux**: Requires `HasSocat` for proxy bridges or `HasTun2Socks` for transparent proxying [ internal/sandbox/linux_features_stub.go:15-26 ]().
*   **macOS**: Relies on `sandbox-exec` (Seatbelt) which is verified during dependency checks [ internal/sandbox/linux_features_stub.go:66-71 ]().

**Sources:** [internal/proxy/brew.go:1-31](), [internal/sandbox/linux_features_stub.go:1-77]()

## Starting the Service

The `proxy.Start()` function [ internal/proxy/start.go:11-30 ]() triggers the service:
1.  Locates the binary using `checkInstalled()`.
2.  Runs `greyproxy service start`.
3.  Redirects `Stdout` and `Stderr` to the system standard streams to allow the user to see initialization logs.

**Sources:** [internal/proxy/start.go:11-30]()

---

# Page: Proxy Bridges and Unix Sockets

# Proxy Bridges and Unix Sockets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/manager.go](internal/sandbox/manager.go)

</details>



This page describes the Unix socket bridge architecture used on Linux to connect isolated network namespaces to the `greyproxy` service. The bridges use `socat` to relay traffic between Unix domain sockets (which can cross namespace boundaries) and TCP/UDP endpoints. This mechanism enables sandboxed processes in isolated network namespaces to access `greyproxy` for filtered internet access.

For information about the `greyproxy` service itself (SOCKS5/HTTP servers, dashboard), see [greyproxy Service](#5.1). For details on transparent proxying via TUN devices and `tun2socks`, see [Transparent Network Proxying](#4.1.5). For domain filtering rules, see [Domain-Based Filtering](#5.3).

## Bridge Architecture Overview

The Linux sandbox uses several types of Unix socket bridges to enable controlled network communication across namespace boundaries. These are managed by the `Manager` class during sandbox initialization.

| Bridge Type | Code Entity | Purpose | Direction | Socket Location |
|-------------|-------------|---------|-----------|-----------------|
| **ProxyBridge** | `ProxyBridge` | Relays SOCKS5 traffic to greyproxy | Outbound | `/tmp/greywall-proxy-{id}.sock` |
| **DnsBridge** | `DnsBridge` | Relays DNS queries to DNS server | Outbound | `/tmp/greywall-dns-{id}.sock` |
| **ReverseBridge** | `ReverseBridge` | Forwards inbound connections to sandbox | Inbound | `/tmp/greywall-rev-{port}-{id}.sock` |
| **ForwardBridge** | `ForwardBridge` | Sandbox access to host localhost ports | Outbound | `/tmp/greywall-fwd-{port}-{id}.sock` |

Each bridge consists of two `socat` processes: one on the host side (started by `Manager.Initialize()`) and one inside the sandbox (started by the inner setup script). Unix sockets are bind-mounted into the sandbox, allowing processes in different network namespaces to communicate.

**Sources:** [internal/sandbox/linux.go:21-111](), [internal/sandbox/manager.go:14-20](), [internal/sandbox/manager.go:71-210]()

### Complete Bridge Architecture

```mermaid
graph TB
    subgraph "Network Namespace (Sandbox)"
        APP["Application Process"]
        TUN["TUN Device<br/>tun0<br/>198.18.0.1/15"]
        T2S["tun2socks Process<br/>gvisor netstack"]
        SOCAT_P["socat Process<br/>TCP-LISTEN:18321"]
        SOCAT_D["socat Process<br/>UDP4-RECVFROM:53"]
        SOCAT_R["socat Process<br/>UNIX-LISTEN"]
    end
    
    subgraph "Unix Socket Bridge Layer"
        SOCK_P["ProxyBridge.SocketPath<br/>/tmp/greywall-proxy-*.sock"]
        SOCK_D["DnsBridge.SocketPath<br/>/tmp/greywall-dns-*.sock"]
        SOCK_R["ReverseBridge.SocketPaths<br/>/tmp/greywall-rev-*.sock"]
    end
    
    subgraph "Host Network Namespace"
        HOST_P["socat Process<br/>UNIX-LISTEN → TCP"]
        HOST_D["socat Process<br/>UNIX-LISTEN → UDP"]
        HOST_R["socat Process<br/>TCP-LISTEN → UNIX-CONNECT"]
        GP["greyproxy<br/>localhost:43052<br/>localhost:43053"]
        INET["Internet"]
    end
    
    APP --> TUN
    TUN --> T2S
    T2S --> SOCAT_P
    SOCAT_P --> SOCK_P
    APP --> SOCAT_D
    SOCAT_R --> SOCK_R
    
    SOCK_P --> HOST_P
    SOCK_D --> HOST_D
    SOCK_R --> HOST_R
    
    HOST_P --> GP
    HOST_D --> GP
    GP --> INET
    INET --> HOST_R
    HOST_R --> APP
```

**Sources:** [internal/sandbox/linux.go:21-291](), [internal/sandbox/linux.go:989-1048]()

## ProxyBridge (Outbound Traffic)

The `ProxyBridge` structure relays SOCKS5 traffic from the sandboxed network namespace to the `greyproxy` service on the host. It parses the proxy URL, extracts credentials, and creates a bidirectional socket relay.

### ProxyBridge Structure

```mermaid
classDiagram
    class ProxyBridge {
        +string SocketPath
        +string ProxyHost
        +string ProxyPort
        +string ProxyUser
        +string ProxyPass
        +bool HasAuth
        -exec.Cmd process
        -bool debug
        +NewProxyBridge(proxyURL, debug) ProxyBridge
        +Cleanup()
    }
```

**Sources:** [internal/sandbox/linux.go:22-31]()

### ProxyBridge Creation Flow

The `NewProxyBridge()` function creates a host-side `socat` relay that forwards traffic from a Unix socket to the `greyproxy` SOCKS5 server:

```mermaid
sequenceDiagram
    participant Manager as Manager.Initialize()
    participant NPB as NewProxyBridge()
    participant Socat as socat Process
    participant FS as Filesystem
    
    Manager->>NPB: NewProxyBridge(proxyURL, debug)
    NPB->>NPB: parseProxyURL()
    NPB->>NPB: Generate random socket ID
    NPB->>NPB: SocketPath = /tmp/greywall-proxy-{id}.sock
    NPB->>Socat: Start socat process
    Note over Socat: UNIX-LISTEN:{socket},fork,reuseaddr<br/>TCP:{host}:{port}
    Socat->>FS: Create Unix socket file
    loop Wait up to 5 seconds
        NPB->>FS: Check if socket exists
        FS-->>NPB: fileExists()
    end
    NPB-->>Manager: Return ProxyBridge
```

**Sources:** [internal/sandbox/linux.go:141-200](), [internal/sandbox/manager.go:151-158]()

### ProxyBridge socat Command

The host-side `socat` process is started with these arguments:

```
socat UNIX-LISTEN:/tmp/greywall-proxy-{id}.sock,fork,reuseaddr TCP:{ProxyHost}:{ProxyPort}
```

| Option | Purpose |
|--------|---------|
| `UNIX-LISTEN:{path}` | Create Unix domain socket and listen for connections |
| `fork` | Fork new process for each connection (concurrent handling) |
| `reuseaddr` | Allow immediate socket reuse after process termination |
| `TCP:{host}:{port}` | Connect to greyproxy SOCKS5 server |

**Sources:** [internal/sandbox/linux.go:175-179]()

### Credentials Handling

When the proxy URL contains authentication credentials (e.g., `socks5://user:pass@localhost:43052`), the `ProxyBridge` extracts them during construction in `NewProxyBridge`.

- **URL Parsing:** [internal/sandbox/linux.go:146-149]()
- **Credential Extraction:** [internal/sandbox/linux.go:168-172]()
- **tun2socks URL Construction:** [internal/sandbox/linux.go:996-1002]()

The credentials are later embedded in the `tun2socks` proxy URL within `WrapCommandLinux` so it can authenticate with `greyproxy` using SOCKS5 username/password authentication (RFC 1929).

**Sources:** [internal/sandbox/linux.go:168-172](), [internal/sandbox/linux.go:996-1002]()

## DnsBridge (DNS Resolution)

The `DnsBridge` structure relays DNS queries from the sandboxed network namespace to a host-side DNS server. This is used when `greyproxy` provides DNS services or when custom DNS servers are configured via `m.config.Network.DnsAddr`.

### DnsBridge Structure

```mermaid
classDiagram
    class DnsBridge {
        +string SocketPath
        +string DnsAddr
        -exec.Cmd process
        -bool debug
        +NewDnsBridge(dnsAddr, debug) DnsBridge
        +Cleanup()
    }
```

**Sources:** [internal/sandbox/linux.go:36-41]()

### DnsBridge Creation and socat Command

The `NewDnsBridge()` function creates a host-side relay from Unix socket to UDP DNS server:

```
socat UNIX-LISTEN:/tmp/greywall-dns-{id}.sock,fork,reuseaddr UDP:{DnsAddr}
```

The `DnsAddr` parameter is typically `localhost:43053` for `greyproxy`'s DNS server, or a custom DNS server address.

**Sources:** [internal/sandbox/linux.go:44-90](), [internal/sandbox/linux.go:65-68]()

### DNS Resolution Flow

Inside the sandbox, a custom `/etc/resolv.conf` points to `127.0.0.1`, and a `socat` relay forwards UDP DNS queries to the `DnsBridge` socket:

```mermaid
sequenceDiagram
    participant App as Application
    participant Resolver as DNS Resolver
    participant SocatIn as socat (sandbox)<br/>UDP4-RECVFROM:53
    participant Socket as Unix Socket<br/>(bind-mounted)
    participant SocatOut as socat (host)<br/>NewDnsBridge
    participant DNS as DNS Server<br/>e.g., localhost:43053
    
    App->>Resolver: DNS query (example.com)
    Note over Resolver: /etc/resolv.conf<br/>nameserver 127.0.0.1
    Resolver->>SocatIn: UDP to 127.0.0.1:53
    SocatIn->>Socket: Forward to Unix socket
    Note over Socket: Crosses namespace boundary
    Socket->>SocatOut: Unix socket data
    SocatOut->>DNS: UDP to DNS server
    DNS-->>SocatOut: DNS response
    SocatOut-->>Socket: Response data
    Socket-->>SocatIn: Response data
    SocatIn-->>Resolver: UDP response
    Resolver-->>App: Resolved IP address
```

**Sources:** [internal/sandbox/linux.go:1029-1036](), [internal/sandbox/linux.go:926-950]()

## ReverseBridge (Inbound Connections)

The `ReverseBridge` structure enables inbound network connections to reach processes inside the sandbox. This is used for development servers (e.g., web servers on port 3000) that need to accept external connections. It is initialized by `Manager.Initialize()` if `exposedPorts` are set and network namespaces are supported.

### ReverseBridge Architecture

Unlike `ProxyBridge` and `DnsBridge`, the `ReverseBridge` uses reverse directionality:

1. **Host-side socat:** Listens on a TCP port and connects to a Unix socket.
2. **Sandbox-side socat:** Listens on the Unix socket and forwards to the application.

```mermaid
graph LR
    EXT["External Client"] --> HOST["Host TCP Port<br/>e.g., :3000"]
    HOST --> SOCAT_H["socat (host)<br/>TCP-LISTEN → UNIX-CONNECT"]
    SOCAT_H --> SOCK["Unix Socket<br/>/tmp/greywall-rev-3000-*.sock"]
    SOCK --> SOCAT_S["socat (sandbox)<br/>UNIX-LISTEN → TCP"]
    SOCAT_S --> APP["Application<br/>listening on localhost:3000"]
```

**Sources:** [internal/sandbox/linux.go:222-272](), [internal/sandbox/manager.go:177-188]()

### ReverseBridge socat Commands

The host-side `socat` process (started by `NewReverseBridge()`) connects to the socket that will be created by the sandbox:

```
socat TCP-LISTEN:{port},fork,reuseaddr UNIX-CONNECT:{socketPath},retry=50,interval=0.1
```

The sandbox-side `socat` process (started by the inner script in `WrapCommandLinux`) accepts connections and forwards to `localhost`:

```
socat UNIX-LISTEN:{socketPath},fork,reuseaddr TCP:localhost:{port}
```

**Sources:** [internal/sandbox/linux.go:252-255](), [internal/sandbox/linux.go:1037-1042]()

## Socket Lifecycle and Management

All bridge types follow a consistent lifecycle pattern for Unix socket creation, validation, and cleanup.

### Socket Path Generation

Socket paths use cryptographically random IDs to avoid collisions, generated via `crypto/rand`.

```mermaid
graph LR
    RNG["crypto/rand.Read()"] --> HEX["hex.EncodeToString()"]
    HEX --> PATH["Socket Path"]
    
    PATH --> PROXY["/tmp/greywall-proxy-{id}.sock"]
    PATH --> DNS["/tmp/greywall-dns-{id}.sock"]
    PATH --> REV["/tmp/greywall-rev-{port}-{id}.sock"]
```

**Sources:** [internal/sandbox/linux.go:49-56](), [internal/sandbox/linux.go:151-158](), [internal/sandbox/linux.go:233-247]()

### Cleanup Implementation

All bridges implement `Cleanup()` methods that ensure resources are released when the sandbox exits. The `Manager` calls these in its own `Cleanup()` method.

1. Kill the `socat` process.
2. Wait for process termination.
3. Remove the socket file from `/tmp`.

**Sources:** [internal/sandbox/linux.go:92-103](), [internal/sandbox/linux.go:203-213](), [internal/sandbox/linux.go:274-291](), [internal/sandbox/manager.go:256-270]()

## Integration with Sandbox

The bridges are integrated into the `bubblewrap` sandbox through bind mounts and inner script commands generated in `WrapCommandLinux`.

### Bridge Initialization Sequence

```mermaid
sequenceDiagram
    participant Manager as Manager
    participant PB as NewProxyBridge()
    participant DB as NewDnsBridge()
    participant RB as NewReverseBridge()
    participant Wrap as WrapCommandLinux()
    participant Bwrap as bubblewrap
    
    Manager->>PB: Create ProxyBridge
    PB-->>Manager: ProxyBridge with socket
    Manager->>DB: Create DnsBridge (if needed)
    DB-->>Manager: DnsBridge with socket
    Manager->>RB: Create ReverseBridge (if ports configured)
    RB-->>Manager: ReverseBridge with sockets
    
    Manager->>Wrap: WrapCommandLinux(cfg, bridges...)
    Wrap->>Wrap: Build bwrap args
    Note over Wrap: Add --bind for each socket
    Wrap->>Wrap: Generate inner script
    Note over Wrap: socat commands for DNS/reverse/proxy
    Wrap-->>Manager: Sandboxed command string
    
    Manager->>Bwrap: Execute wrapped command
```

**Sources:** [internal/sandbox/linux.go:595-604](), [internal/sandbox/linux.go:899-959](), [internal/sandbox/manager.go:140-210]()

### Socket Bind Mounts

Bridge sockets are bind-mounted into the sandbox as writable paths using the `--bind` flag in `bubblewrap`.

| Bridge | Mount Type | bwrap Argument |
|--------|-----------|----------------|
| **ProxyBridge** | Single socket | `--bind {SocketPath} {SocketPath}` |
| **DnsBridge** | Single socket | `--bind {SocketPath} {SocketPath}` |
| **ReverseBridge** | Directory | `--bind {tmpDir} {tmpDir}` |

**Sources:** [internal/sandbox/linux.go:901-923](), [internal/sandbox/linux.go:954-959]()

### Inner Script Bridge Setup

The inner script (executed by `bash` inside the sandbox) sets up the sandbox-side `socat` relays in the background before launching the application:

```bash
# Proxy relay (sandbox side): localhost:18321 → Unix socket → host → greyproxy
socat TCP-LISTEN:18321,fork,reuseaddr,bind=127.0.0.1 UNIX-CONNECT:{ProxyBridge.SocketPath} &

# DNS relay (sandbox side): UDP :53 → Unix socket → host → DNS server
socat UDP4-RECVFROM:53,fork,reuseaddr UNIX-CONNECT:{DnsBridge.SocketPath} &

# Reverse relay (sandbox side): Unix socket → localhost:{port}
socat UNIX-LISTEN:{ReverseBridge.SocketPath},fork,reuseaddr TCP:localhost:{port} &
```

**Sources:** [internal/sandbox/linux.go:1014-1018](), [internal/sandbox/linux.go:1029-1036](), [internal/sandbox/linux.go:1037-1042]()

---

# Page: Domain-Based Filtering

# Domain-Based Filtering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/configuration.md](docs/configuration.md)
- [internal/config/config.go](internal/config/config.go)
- [internal/config/config_test.go](internal/config/config_test.go)

</details>



Domain-based filtering is greywall's mechanism for controlling network access through the `greyproxy` service. All network traffic from sandboxed processes is routed through `greyproxy`, which enforces a deny-by-default policy: connections are blocked unless the destination domain appears in the allow list. This page explains how domain filtering is implemented, how patterns are matched, and how to use the configuration system for runtime control.

For information about the `greyproxy` service architecture, see [greyproxy Service](#5.1). For details on how Linux bridges connect to `greyproxy`, see [Proxy Bridges and Unix Sockets](#5.2).

## Overview

Greyproxy implements a deny-by-default network filtering model where:

1.  **All outbound connections are blocked by default** — no network access is permitted unless explicitly allowed.
2.  **Domain-based filtering** — connections are allowed or denied based on the destination domain name.
3.  **Multiple protocol support** — filtering applies to SOCKS5, HTTP CONNECT, and DNS requests.
4.  **Wildcard patterns** — domain rules support wildcards like `**.openai.com`.
5.  **Session-Scoped Rules** — Rules can be defined per sandbox session and are automatically cleaned up.

The filtering occurs at the `greyproxy` service layer. On Linux, traffic is captured transparently via `tun2socks` and routed through Unix socket bridges to `greyproxy`. On macOS, applications use proxy environment variables to route traffic.

Sources: [internal/config/config.go:51-58](), [docs/configuration.md:93-96]()

## Configuration Model

Domain filtering is configured through the `NetworkConfig` structure [internal/config/config.go:61-71](), which specifies the proxy endpoints and the specific `NetworkRule` set for the session.

### Code Entity Mapping: Network Configuration

The following diagram bridges the configuration structure defined in Go to the logical filtering components.

```mermaid
classDiagram
    class Config {
        +NetworkConfig Network
    }
    class NetworkConfig {
        +string ProxyURL
        +string HTTPProxyURL
        +string DnsAddr
        +NetworkRule[] Rules
        +bool AllowLocalBinding
    }
    class NetworkRule {
        +string Destination
        +string Port
        +string Action
        +string Notes
    }
    Config *-- NetworkConfig
    NetworkConfig *-- NetworkRule
```

**Sources:** [internal/config/config.go:23-25](), [internal/config/config.go:53-58](), [internal/config/config.go:61-71]()

### Configuration Examples

**Allow specific domains with wildcards:**

```jsonc
{
  "network": {
    "rules": [
      {
        "destination": "api.openai.com",
        "port": "443",
        "action": "allow"
      },
      {
        "destination": "**.github.com",
        "port": "*",
        "action": "allow"
      }
    ]
  }
}
```

**Explicitly Deny specific subdomains:**

```jsonc
{
  "network": {
    "rules": [
      {
        "destination": "telemetry.example.com",
        "action": "deny"
      },
      {
        "destination": "**.example.com",
        "action": "allow"
      }
    ]
  }
}
```

Rules are processed in order; a "deny" rule for a specific subdomain should typically precede a wildcard "allow" rule for the parent domain.

**Sources:** [internal/config/config.go:53-58](), [docs/configuration.md:13-17]()

## Domain Matching Logic

### Filtering Decision Flow

When a network request enters `greyproxy`, it evaluates the `NetworkRule` slice provided during session initialization.

```mermaid
flowchart TD
    REQUEST["Network Request<br/>(SOCKS5/HTTP/DNS)"]
    EXTRACT["Extract destination domain/IP"]
    LOCALHOST{"Is localhost<br/>or 127.0.0.1?"}
    LOCALCHECK{"AllowLocalOutbound<br/>enabled?"}
    RULE_LOOP["Iterate through<br/>NetworkConfig.Rules"]
    MATCH{"Does destination<br/>match Rule?"}
    ACTION{"Action == 'allow'?"}
    BLOCK["Block connection<br/>(log violation)"]
    ALLOW["Allow connection"]
    DEFAULT_DENY["End of list:<br/>Default Deny"]
    
    REQUEST --> EXTRACT
    EXTRACT --> LOCALHOST
    LOCALHOST -->|yes| LOCALCHECK
    LOCALHOST -->|no| RULE_LOOP
    LOCALCHECK -->|yes| ALLOW
    LOCALCHECK -->|no| BLOCK
    
    RULE_LOOP --> MATCH
    MATCH -->|yes| ACTION
    MATCH -->|no| RULE_LOOP
    ACTION -->|yes| ALLOW
    ACTION -->|no| BLOCK
    
    RULE_LOOP -->|No matches| DEFAULT_DENY
    DEFAULT_DENY --> BLOCK
```

**Sources:** [internal/config/config.go:51-58](), [internal/config/config.go:61-71](), [docs/configuration.md:104-104]()

### Pattern Support

The `Destination` field in `NetworkRule` [internal/config/config.go:54-54]() supports the following patterns:

| Pattern | Type | Matches |
|---------|------|---------|
| `api.openai.com` | Exact | Only that specific domain |
| `**.openai.com` | Wildcard | `api.openai.com`, `v1.api.openai.com`, etc. |
| `192.168.0.0/24` | CIDR | Any IP in the subnet |
| `*` | Catch-all | All destinations (if used in an allow rule) |

**Sources:** [internal/config/config.go:54-54]()

## DNS Filtering

Greyproxy provides a DNS server (default `localhost:43053`) [docs/configuration.md:100-100]() that enforces domain filtering before a connection is even attempted:

1.  **DNS queries are intercepted** — the sandboxed process queries the `DnsAddr` defined in `NetworkConfig` [internal/config/config.go:64-64]().
2.  **Domain validation** — `greyproxy` checks the queried domain against the active `Rules`.
3.  **Conditional resolution** — if allowed, `greyproxy` resolves the domain; if denied, it returns an error or empty response, preventing the process from obtaining the IP.

On Linux, this is enforced transparently via the `DnsBridge`.

**Sources:** [internal/config/config.go:64-64](), [docs/configuration.md:100-100]()

## Integration with Sandbox Configuration

### Configuration Precedence

The final `NetworkConfig` used by a sandbox is determined by merging multiple sources.

```mermaid
flowchart LR
    subgraph Sources ["Configuration Sources"]
        CLI["CLI Flags<br/>--forward, --proxy"]
        FILE["greywall.json"]
        TEMPLATE["Built-in Templates<br/>(e.g., 'code')"]
    end
    
    subgraph Logic ["internal/config"]
        LOAD["Load()"]
        MERGE["Merge()"]
        VALIDATE["Validate()"]
    end
    
    subgraph Output ["Runtime Config"]
        NET["Final NetworkConfig"]
    end
    
    CLI --> LOAD
    FILE --> LOAD
    TEMPLATE --> LOAD
    LOAD --> MERGE
    MERGE --> VALIDATE
    VALIDATE --> NET
```

**Merge Behavior:**
- **Slice fields** (like `Rules` or `ForwardPorts`) are appended and deduplicated [docs/configuration.md:83-83]().
- **Boolean fields** use OR logic (true if either base or override enables it) [docs/configuration.md:84-84]().
- **String fields** (like `ProxyURL`) use override-wins semantics [docs/configuration.md:85-85]().

**Sources:** [internal/config/config.go:259-277](), [docs/configuration.md:81-85]()

## Platform-Specific Enforcement

### Linux: Transparent Interception
On Linux, the sandbox uses a network namespace and a TUN device. All traffic is forced through `tun2socks`, which converts packets into SOCKS5 requests sent to `greyproxy` via a Unix socket bridge. This prevents applications from bypassing filtering via `/etc/hosts` or hardcoded IPs.

### macOS: Environment Variables
On macOS, `greywall` sets standard environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) pointing to `greyproxy`.
- `HTTPProxyURL` (default `http://localhost:43051`) [docs/configuration.md:106-106]().
- `ProxyURL` (default `socks5://localhost:43052`) [docs/configuration.md:99-99]().

**Note:** Applications on macOS that do not respect environment variables or use low-level socket APIs may bypass these filters unless restricted by Seatbelt profiles.

**Sources:** [docs/configuration.md:99-106](), [internal/config/config.go:62-63]()

## Localhost and Local Binding

Access to the host machine is strictly controlled:

-   **`AllowLocalBinding`**: If true, allows the sandboxed process to listen on ports within the sandbox [internal/config/config.go:67-67]().
-   **`AllowLocalOutbound`**: Controls if the process can connect to services running on the host's `localhost`. On Linux, this is typically handled via `ForwardPorts` [internal/config/config.go:69-69](), which maps specific host ports into the sandbox. On macOS, this field directly enables/disables outbound localhost access [docs/configuration.md:104-104]().

**Sources:** [internal/config/config.go:67-69](), [docs/configuration.md:103-105]()

---

# Page: Configuration System

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/configuration.md](docs/configuration.md)
- [internal/config/config.go](internal/config/config.go)
- [internal/config/config_test.go](internal/config/config_test.go)

</details>



The Configuration System manages sandbox behavior through a layered approach that combines configuration files, profiles, and CLI flags. It handles loading, merging, and applying settings that control network access, filesystem restrictions, command filtering, and SSH policies.

For details on specific configuration file formats and options, see [Configuration Files](#6.1). For information about the profile system and template inheritance, see [Profile System](#6.2). For automatic profile generation via filesystem tracing, see [Learning Mode](#6.3).

---

## Configuration Loading Flow

The configuration system follows a strict precedence order, with later sources overriding earlier ones.

Title: Configuration Resolution Pipeline
```mermaid
flowchart TD
    Start["User invokes greywall"]
    CheckSettings["Check --settings flag"]
    LoadSettings["config.Load(path)"]
    CheckDefault["Check default path<br/>config.DefaultConfigPath()"]
    LoadDefault["config.Load(defaultPath)"]
    UseDefault["config.Default()"]
    
    CheckProfile["Check --profile flag"]
    ResolveProfile["resolveProfile(name)<br/>for each comma-separated name"]
    SavedProfile["Try saved profile<br/>sandbox.LearnedTemplatePath(name)"]
    BuiltinProfile["Try built-in profile<br/>profiles.GetAgentProfile()"]
    AutoDetect["Auto-detect by command name"]
    FirstRun["profiles.ResolveFirstRun()"]
    
    MergeProfile["config.Merge(cfg, profile)"]
    
    ApplyCLI["Apply CLI flag overrides<br/>--proxy, --dns, --http-proxy"]
    ApplyDefaults["Apply greyproxy defaults<br/>if not set"]
    InjectCreds["Auto-inject proxy credentials<br/>username = command name"]
    
    Final["Final merged config.Config"]
    
    Start --> CheckSettings
    CheckSettings -->|"settingsPath != ''"| LoadSettings
    CheckSettings -->|"settingsPath == ''"| CheckDefault
    CheckDefault -->|"file exists"| LoadDefault
    CheckDefault -->|"file not exists"| UseDefault
    LoadSettings --> CheckProfile
    LoadDefault --> CheckProfile
    UseDefault --> CheckProfile
    
    CheckProfile -->|"profileName != ''"| ResolveProfile
    CheckProfile -->|"profileName == '' && !learning"| AutoDetect
    CheckProfile -->|"learning mode"| ApplyCLI
    
    ResolveProfile --> SavedProfile
    SavedProfile -->|"found"| MergeProfile
    SavedProfile -->|"not found"| BuiltinProfile
    BuiltinProfile -->|"found"| MergeProfile
    BuiltinProfile -->|"not found"| ApplyCLI
    
    AutoDetect --> FirstRun
    FirstRun -->|"profile found"| MergeProfile
    FirstRun -->|"no profile"| ApplyCLI
    
    MergeProfile --> ApplyCLI
    ApplyCLI --> ApplyDefaults
    ApplyDefaults --> InjectCreds
    InjectCreds --> Final
```

**Sources:** [cmd/greywall/main.go:178-314](), [internal/config/config.go:176-180]()

---

## Configuration Loading Implementation

The configuration loading process is implemented in `main.go` with distinct stages:

### Stage 1: Base Configuration

The system first loads the base configuration from either an explicit path or the default location:

| Source | Code Path | Behavior |
|--------|-----------|----------|
| Explicit path (`--settings`) | [cmd/greywall/main.go:183-187]() | Load from specified file, error if missing |
| Default path | [cmd/greywall/main.go:189-199]() | Load from `config.DefaultConfigPath()`, use default if missing |
| Default config | [cmd/greywall/main.go:198]() | Created via `config.Default()` when no file exists |

### Stage 2: Profile Resolution

Profile resolution happens only when NOT in learning mode ([cmd/greywall/main.go:206-262]()):

Title: Profile Selection Logic
```mermaid
flowchart LR
    CheckFlag{"--profile flag<br/>provided?"}
    ExplicitProfile["Split by comma<br/>resolveProfile() for each"]
    CheckCmd{"Command name<br/>available?"}
    TrySaved["Try saved profile<br/>sandbox.LearnedTemplatePath(cmdName)"]
    CheckAuto{"--auto-profile<br/>flag set?"}
    ApplyBuiltin["Apply built-in silently<br/>profiles.GetAgentProfile()"]
    FirstRun["Interactive first-run UX<br/>profiles.ResolveFirstRun()"]
    Merge["Merge with config.Merge()"]
    
    CheckFlag -->|"yes"| ExplicitProfile
    CheckFlag -->|"no"| CheckCmd
    ExplicitProfile --> Merge
    CheckCmd -->|"yes"| TrySaved
    CheckCmd -->|"no"| Merge
    TrySaved -->|"found"| Merge
    TrySaved -->|"not found"| CheckAuto
    CheckAuto -->|"yes"| ApplyBuiltin
    CheckAuto -->|"no"| FirstRun
    ApplyBuiltin --> Merge
    FirstRun --> Merge
```

The `resolveProfile` function ([cmd/greywall/main.go:449-481]()) tries saved profiles first, then built-in profiles, returning an error if neither exists.

### Stage 3: CLI Flag Overrides

CLI flags always take precedence over configuration files ([cmd/greywall/main.go:264-273]()):

```go
// Overrides in order:
cfg.Network.ProxyURL      // --proxy flag
cfg.Network.HTTPProxyURL  // --http-proxy flag
cfg.Network.DnsAddr       // --dns flag
```

### Stage 4: Default Value Application

If proxy or DNS settings remain unset, greyproxy defaults are applied ([cmd/greywall/main.go:277-294]()):

| Field | Default Value | Port |
|-------|---------------|------|
| `ProxyURL` | `socks5://localhost:43052` | 43052 |
| `HTTPProxyURL` | `http://localhost:43051` | 43051 |
| `DnsAddr` | `localhost:43053` | 43053 |

### Stage 5: Proxy Credential Injection

The system automatically injects proxy credentials for identification ([cmd/greywall/main.go:296-314]()):

- Username: command name (e.g., `opencode`) or `"proxy"` if unavailable
- Password: always `"proxy"`
- Applied to both `ProxyURL` and `HTTPProxyURL` fields

**Sources:** [cmd/greywall/main.go:178-314](), [cmd/greywall/main.go:449-481]()

---

## Configuration Structure

The configuration is defined by the `Config` type in `internal/config/config.go`.

### Core Configuration Type

Title: Configuration Data Model
```mermaid
classDiagram
    class Config {
        +string Extends
        +NetworkConfig Network
        +FilesystemConfig Filesystem
        +CommandConfig Command
        +SSHConfig SSH
        +CredentialConfig Credentials
        +bool AllowPty
        +int SchemaVersion
    }
    
    class NetworkConfig {
        +string ProxyURL
        +string HTTPProxyURL
        +string DnsAddr
        +[]NetworkRule Rules
        +[]string AllowUnixSockets
        +bool AllowAllUnixSockets
        +bool AllowLocalBinding
        +*bool AllowLocalOutbound
    }
    
    class FilesystemConfig {
        +*bool DefaultDenyRead
        +[]string AllowRead
        +[]string DenyRead
        +[]string AllowWrite
        +[]string DenyWrite
        +bool AllowGitConfig
    }
    
    class CommandConfig {
        +[]string Deny
        +[]string Allow
        +*bool UseDefaults
    }
    
    class SSHConfig {
        +[]string AllowedHosts
        +[]string DeniedHosts
        +[]string AllowedCommands
        +[]string DeniedCommands
        +bool AllowAllCommands
        +bool InheritDeny
    }

    class NetworkRule {
        +string Destination
        +string Port
        +string Action
    }
    
    Config --> NetworkConfig
    Config --> FilesystemConfig
    Config --> CommandConfig
    Config --> SSHConfig
    NetworkConfig --> NetworkRule
```

### Field Semantics

| Field Type | Nil Behavior | Default When Nil |
|------------|--------------|------------------|
| `*bool` fields | `nil` = use default | `DefaultDenyRead`: `true`, `UseDefaults`: `true` |
| `[]string` fields | `nil` or `[]` | Empty list (no restrictions) |
| `string` fields | `""` | Greyproxy defaults applied after merge |

**Sources:** [internal/config/config.go:23-105](), [internal/config/config.go:151-171]()

---

## Profile Resolution System

Profiles provide reusable configuration bundles. The system recognizes three profile types with a clear resolution order:

Title: Profile Source Resolution
```mermaid
flowchart TD
    Input["Profile name requested<br/>(explicit or auto-detected)"]
    
    subgraph "Resolution Order"
        Saved["1. Saved Profile<br/>sandbox.LearnedTemplatePath(name)<br/>~/.config/greywall/learned/"]
        Builtin["2. Built-in Profile<br/>profiles.GetAgentProfile(canonical)<br/>internal/profiles/"]
        NotFound["Error: profile not found"]
    end
    
    subgraph "Built-in Categories"
        Agents["Agent Profiles<br/>internal/profiles/agents/<br/>claude, opencode, cursor, etc."]
        Toolchains["Toolchain Profiles<br/>internal/profiles/toolchains/<br/>python, node, uv, etc."]
    end
    
    Input --> Saved
    Saved -->|"exists"| Return["Return config"]
    Saved -->|"not found"| Builtin
    Builtin --> Agents
    Builtin --> Toolchains
    Agents -->|"found"| Return
    Toolchains -->|"found"| Return
    Agents -->|"not found"| NotFound
    Toolchains -->|"not found"| NotFound
```

### Resolution Implementation

The `resolveProfile` function implements this logic ([cmd/greywall/main.go:449-481]()):

1. **Saved profile lookup:** Uses `sandbox.LearnedTemplatePath(name)` to construct path.
2. **Config loading:** Calls `config.Load(savedPath)` to attempt load.
3. **Built-in fallback:** 
   - Calls `profiles.IsKnownAgent(name)` to get canonical name.
   - Retrieves via `profiles.GetAgentProfile(canonical)`.
4. **Error on miss:** Returns error if neither source has the profile.

**Sources:** [cmd/greywall/main.go:449-481](), [cmd/greywall/main.go:19-20]()

---

## Configuration Merging

The `config.Merge` function combines configurations with well-defined override semantics.

### Merge Semantics by Field Type

| Field Type | Merge Behavior |
|------------|----------------|
| String fields | Override: profile value replaces base if non-empty |
| `[]string` fields | Append: profile values added to base list and deduplicated |
| `*bool` fields | Override: profile value replaces base if non-nil |
| Boolean fields | OR logic: true if either base or override enables it |

### Multiple Profile Merging

The `--profile` flag accepts comma-separated names ([cmd/greywall/main.go:208-222]()):

```go
// Example: --profile claude,python
names := strings.Split(profileName, ",")
for _, name := range names {
    name = strings.TrimSpace(name)
    resolved, err := resolveProfile(name, debug)
    if resolved != nil {
        cfg = config.Merge(cfg, resolved)
    }
}
```

**Sources:** [internal/config/config.go:259-300](), [cmd/greywall/main.go:208-222]()

---

## Auto-Detection and First-Run UX

When no explicit profile is specified, the system attempts auto-detection based on command name.

### Command Name Extraction

The `extractCommandName` function ([cmd/greywall/main.go:483-504]()) extracts the base command:

- From args: `["opencode", "--flag"]` → `"opencode"`
- From `-c`: `"opencode --flag"` → `"opencode"` (first token)
- Strips path: `/usr/bin/opencode` → `"opencode"`

### Auto-Profile Mode

The `--auto-profile` flag ([cmd/greywall/main.go:237-250]()) silently applies built-in profiles without prompting. If not set, `profiles.ResolveFirstRun()` may prompt the user to adopt a built-in profile for a detected agent.

**Sources:** [cmd/greywall/main.go:223-262](), [cmd/greywall/main.go:483-504]()

---

## Default Values and Initialization

### Nil vs. Empty Semantics

Pointer fields (`*bool`) distinguish between "not set" and "explicitly false":

| Field | Nil Value | Meaning | Effective Value |
|-------|-----------|---------|-----------------|
| `DefaultDenyRead` | `nil` | Use secure default | `true` (deny by default) |
| `DefaultDenyRead` | `*false` | Explicitly allow all reads | `false` |
| `UseDefaults` | `nil` | Use default deny list | `true` |
| `AllowLocalOutbound` | `nil` | Inherit from `AllowLocalBinding` | Same as `AllowLocalBinding` |

### Default Denied Commands

When `CommandConfig.UseDefaults` is true, greywall blocks dangerous system commands like `shutdown`, `reboot`, `mkfs`, and `chroot` by default.

**Sources:** [internal/config/config.go:109-148](), [internal/config/config.go:85-87]()

---

## Configuration Precedence Summary

The complete precedence order from lowest to highest:

1. **Built-in Defaults:** `config.Default()` with deny-by-default filesystem.
2. **Configuration File:** Loaded via `--settings` or from default path.
3. **Extended Profile:** via `extends` field in the loaded config file.
4. **Saved Profiles:** Auto-detected by command name if no `--profile` flag.
5. **Explicit Profiles:** `--profile` flag (left to right merging).
6. **CLI Flags:** `--proxy`, `--dns`, `--http-proxy` direct overrides.
7. **Greyproxy Defaults:** Applied if fields are still empty.

**Sources:** [cmd/greywall/main.go:178-314](), [docs/configuration.md:33-91]()

---

# Page: Configuration Files

# Configuration Files

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/configuration.md](docs/configuration.md)
- [internal/config/config.go](internal/config/config.go)
- [internal/config/config_test.go](internal/config/config_test.go)

</details>



This page documents the structure and format of greywall configuration files. It covers file locations, the JSON schema, and all available configuration options. For information about profiles (built-in templates and learned profiles), see [Profile System](#6.2). For automatic configuration generation, see [Learning Mode](#6.3).

## File Format and Locations

Greywall configuration files use JSON or JSONC (JSON with Comments) format. The configuration system supports standard JSON comments (`//` and `/* */`) for documentation through the `github.com/tidwall/jsonc` parser [internal/config/config.go:14-15]().

**Default Configuration Paths**

| Platform | Default Path |
|----------|-------------|
| Linux | `~/.config/greywall/greywall.json` |
| macOS | `~/Library/Application Support/greywall/greywall.json` |
| Legacy (all) | `~/.greywall.json` (fallback) |

The default path is resolved by [internal/config/config.go:176-200]() in the `DefaultConfigPath` function. It prioritizes the OS-preferred config directory (XDG on Linux, Application Support on macOS) but falls back to the legacy `~/.greywall.json` if it exists [internal/config/config.go:176-186]().

**Custom Configuration Path**

Use the `--settings` / `-s` flag to specify a custom configuration file. When this flag is provided, greywall loads settings via `config.Load(path)` [internal/config/config.go:48-91]().

Sources: [internal/config/config.go:176-200](), [docs/configuration.md:1-9]()

## Configuration Loading Flow

The following diagram illustrates how the `config` package and CLI entry point resolve the final sandbox configuration.

```mermaid
flowchart TD
    Start["greywall command execution"]
    CheckSettings{"--settings flag<br/>provided?"}
    LoadCustom["Load from custom path<br/>config.Load(settingsPath)"]
    LoadDefault["Load from DefaultConfigPath()"]
    CheckExists{"Config file<br/>exists?"}
    UseDefault["Use config.Default()<br/>(deny-by-default)"]
    ResolveExtends["Resolve extends field<br/>(Template or File)"]
    MergeBase["config.Merge(base, override)"]
    ApplyCLI["Apply CLI flag overrides<br/>(--proxy, --dns)"]
    Final["Final Config Object"]
    
    Start --> CheckSettings
    CheckSettings -->|Yes| LoadCustom
    CheckSettings -->|No| LoadDefault
    LoadCustom --> ResolveExtends
    LoadDefault --> CheckExists
    CheckExists -->|No| UseDefault
    CheckExists -->|Yes| ResolveExtends
    UseDefault --> ResolveExtends
    ResolveExtends --> MergeBase
    MergeBase --> ApplyCLI
    ApplyCLI --> Final
```

Sources: [internal/config/config.go:48-91](), [internal/config/config.go:259-310](), [docs/configuration.md:33-91]()

## Configuration Structure

The `Config` struct in [internal/config/config.go:23-42]() defines the root configuration object.

```mermaid
classDiagram
    class Config {
        +string Extends
        +NetworkConfig Network
        +FilesystemConfig Filesystem
        +CommandConfig Command
        +SSHConfig SSH
        +CredentialConfig Credentials
        +bool AllowPty
        +bool AllowAudio
        +int SchemaVersion
    }
    
    class NetworkConfig {
        +string ProxyURL
        +string HTTPProxyURL
        +string DnsAddr
        +[]NetworkRule Rules
        +[]string AllowUnixSockets
        +bool AllowAllUnixSockets
        +bool AllowLocalBinding
        +*bool AllowLocalOutbound
        +[]int ForwardPorts
    }
    
    class FilesystemConfig {
        +*bool DefaultDenyRead
        +[]string AllowRead
        +[]string DenyRead
        +[]string AllowWrite
        +[]string DenyWrite
        +bool AllowGitConfig
    }
    
    class CommandConfig {
        +[]string Deny
        +[]string Allow
        +*bool UseDefaults
    }
    
    Config --> NetworkConfig
    Config --> FilesystemConfig
    Config --> CommandConfig
    Config --> SSHConfig
    Config --> CredentialConfig
```

Sources: [internal/config/config.go:23-42](), [internal/config/config.go:61-71](), [internal/config/config.go:74-81](), [internal/config/config.go:90-94](), [internal/config/config.go:98-105]()

### Extends Field

The `extends` field allows configuration inheritance. The logic treats the value as a file path if it contains path separators or starts with `.`, otherwise it is treated as a built-in template name [docs/configuration.md:77-80]().

- **Merge Logic**: Slices are appended and deduplicated; Booleans use OR logic; Integers use override-wins [docs/configuration.md:81-86]().
- **Chaining**: Supports up to 10 levels of inheritance with circular dependency detection [docs/configuration.md:88-90]().

Sources: [internal/config/config.go:24](), [docs/configuration.md:33-91]()

## Network Configuration

The `NetworkConfig` struct [internal/config/config.go:61-71]() manages connectivity. Unlike legacy versions, modern greywall uses `NetworkRule` objects for fine-grained control.

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `proxyUrl` | `string` | SOCKS5 proxy URL (e.g. `socks5://host:1080`) |
| `httpProxyUrl` | `string` | HTTP CONNECT proxy URL |
| `dnsAddr` | `string` | DNS server address on host |
| `rules` | `[]NetworkRule` | Session-scoped rules for greyproxy |
| `forwardPorts` | `[]int` | Host ports to forward into sandbox (Linux) |
| `allowLocalOutbound`| `*bool` | Allow access to host localhost (macOS) |

### Network Rules

Rules are defined in [internal/config/config.go:53-58]():
- **Destination**: Domain/IP pattern (e.g. `api.openai.com`, `**.openai.com`, `192.168.0.0/24`).
- **Port**: Supports exact ports, ranges (`8000-9000`), or comma-separated lists.
- **Action**: `"allow"` (default) or `"deny"`.

Sources: [internal/config/config.go:53-71](), [docs/configuration.md:94-107]()

## Filesystem Configuration

The `FilesystemConfig` struct [internal/config/config.go:74-81]() controls path access.

### Deny-by-Default Read Model

If `defaultDenyRead` is `nil` or `true`, the sandbox denies all reads except for system paths, the current working directory, and paths in `allowRead` [internal/config/config.go:75-76]().

### Hard-Coded Protections

Greywall blocks specific dangerous paths regardless of configuration to prevent credential theft and shell persistence. These include:
- **Credentials**: `~/.ssh/id_*`, `~/.aws/credentials`, `~/.config/gcloud/**` [docs/configuration.md:144-150]().
- **Shell Hooks**: `~/.bashrc`, `~/.zshrc`, `.git/hooks/*` [docs/configuration.md:144-150]().

Sources: [internal/config/config.go:74-87](), [docs/configuration.md:108-120]()

## Command Configuration

The `CommandConfig` struct [internal/config/config.go:90-94]() defines which binaries or command strings are blocked.

### Default Denied Commands

When `useDefaults` is true (the default), greywall blocks a list of system-critical commands defined in `DefaultDeniedCommands` [internal/config/config.go:109-148]():
- **System Control**: `shutdown`, `reboot`, `halt`, `systemctl poweroff`.
- **Kernel**: `insmod`, `modprobe`, `kexec`.
- **Disk**: `mkfs.*`, `fdisk`, `dd if=`.
- **Escape**: `docker run --privileged`, `chroot`, `unshare`.

### Command Detection

Detection is applied to direct commands, chains (`&&`, `;`), pipelines (`|`), and shell invocations (`bash -c`) [docs/configuration.md:156-162]().

Sources: [internal/config/config.go:90-94](), [internal/config/config.go:109-148](), [docs/configuration.md:121-162]()

## SSH Configuration

The `SSHConfig` struct [internal/config/config.go:98-105]() provides an allowlist-by-default model for remote execution.

- **AllowedHosts**: Supports wildcards like `*.example.com`.
- **InheritDeny**: If `true`, the global `command.deny` rules are also applied to commands executed over SSH [internal/config/config.go:104]().

Sources: [internal/config/config.go:98-105](), [docs/configuration.md:163-221]()

## Credential Configuration

Defined in [internal/config/config.go:45-49](), this section handles sensitive data injection.

- **Secrets**: Additional environment variables to treat as credentials.
- **Inject**: Global credential labels to pull from the proxy.
- **Ignore**: Environment variables to exclude from automated credential detection.

Sources: [internal/config/config.go:45-49]()

## Merging and Defaults

The `Merge` function [internal/config/config.go:259-310]() handles the combination of base and override configurations. 

- **Default State**: `config.Default()` returns a configuration with all network blocked (empty `NetworkConfig`) and default command restrictions enabled [internal/config/config.go:151-171]().
- **Validation**: `config.Validate()` ensures proxy URLs have valid schemes (e.g., `socks5://` or `socks5h://`) and that no empty paths are provided in filesystem rules [internal/config/config_test.go:9-110]().

Sources: [internal/config/config.go:151-171](), [internal/config/config.go:259-310](), [internal/config/config_test.go:9-110]()

---

# Page: Profile System

# Profile System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/agents.md](docs/agents.md)
- [docs/cli-reference.md](docs/cli-reference.md)
- [docs/templates.md](docs/templates.md)
- [internal/profiles/base.go](internal/profiles/base.go)
- [internal/profiles/keyring.go](internal/profiles/keyring.go)
- [internal/profiles/profiles_test.go](internal/profiles/profiles_test.go)
- [internal/profiles/prompt.go](internal/profiles/prompt.go)
- [internal/profiles/registry.go](internal/profiles/registry.go)
- [internal/profiles/resolve.go](internal/profiles/resolve.go)
- [internal/profiles/toolchains/scm.go](internal/profiles/toolchains/scm.go)

</details>



The Profile System provides pre-configured security policies for common tools and workflows, eliminating the need to manually configure filesystem and network restrictions for every command. Profiles can be built-in (shipped with greywall), saved/learned automatically, or custom-defined by users.

---

## Profile Types

Greywall supports three types of profiles, each serving different use cases:

| Profile Type | Source | Storage Location | Use Case |
|--------------|--------|------------------|----------|
| **Built-in** | Shipped with greywall | `internal/profiles/agents/` and `internal/profiles/toolchains/` | Pre-configured policies for popular AI agents and development tools. |
| **Saved/Learned** | Generated via `--learning` or saved from built-in | `~/.config/greywall/learned/` (or `~/Library/Application Support/greywall/learned/` on macOS) | Custom profiles learned from actual usage or modified from defaults. |
| **Explicit** | User-defined JSON/JSONC files | Any path | Custom security policies for specific workflows. |

**Sources:** [internal/profiles/registry.go:19-43](), [internal/profiles/resolve.go:169-180]()

---

## Profile Resolution and Precedence

When greywall runs a command, it resolves profiles in a specific priority order. Higher-priority sources override lower-priority ones through configuration merging.

```mermaid
graph TB
    CMD["greywall [flags] -- command"]
    
    subgraph Priority["Profile Resolution Priority (Highest to Lowest)"]
        P1["1. --profile flag<br/>(Explicit override)"]
        P2["2. Saved learned profile<br/>(Auto-detected by command name)"]
        P3["3. Built-in profile<br/>(Known agents/toolchains)"]
        P4["4. Default config<br/>(Network blocked, DefaultDenyRead)"]
    end
    
    CMD --> CHECK_PROFILE{"--profile<br/>specified?"}
    CHECK_PROFILE -->|Yes| P1
    CHECK_PROFILE -->|No| CHECK_SAVED{"Saved profile<br/>exists for<br/>command name?"}
    
    CHECK_SAVED -->|Yes| P2
    CHECK_SAVED -->|No| CHECK_AUTO{"--auto-profile<br/>flag set?"}
    
    CHECK_AUTO -->|Yes + Known| P3
    CHECK_AUTO -->|No| CHECK_BUILTIN{"Known agent<br/>without saved<br/>profile?"}
    
    CHECK_BUILTIN -->|Yes| PROMPT["First-run UX:<br/>Prompt to save<br/>built-in profile"]
    CHECK_BUILTIN -->|No| P4
    
    PROMPT --> P3
    
    P1 --> MERGE["config.Merge()"]
    P2 --> MERGE
    P3 --> MERGE
    P4 --> MERGE
    
    MERGE --> FINAL["Final Config"]
```

**Profile Resolution Flow**

The resolution logic is driven by the following components:

1. **Explicit `--profile` flag**: Resolves each comma-separated profile name. It tries saved profiles first via `sandbox.LearnedTemplatePath(name)` before falling back to built-in profiles [docs/templates.md:12-26]().
2. **Auto-detected saved profile**: If no profile is specified, greywall extracts the command name and checks `~/.config/greywall/learned/{cmdName}.json` [internal/profiles/resolve.go:180]().
3. **`--auto-profile` flag**: Silently applies a built-in profile if available for the command without triggering the interactive prompt [docs/cli-reference.md:22]().
4. **First-run UX**: For known agents without saved profiles, `profiles.ResolveFirstRun()` displays a summary and asks the user to apply, edit, or skip the profile [internal/profiles/resolve.go:17-27]().
5. **Default config**: Falls back to restrictive defaults if no other profiles apply.

**Sources:** [internal/profiles/resolve.go:17-104](), [docs/templates.md:12-26](), [docs/cli-reference.md:17-40]()

---

## Built-in Profiles and Inheritance

Built-in profiles are defined as `AgentDef` structs and registered via `init()` functions [internal/profiles/registry.go:23-43]().

### Base Profile
Most agent profiles inherit from `BaseProfile()`, which provides access to standard configuration like `.gitconfig`, SSH known hosts, and platform-specific paths like the macOS Keychain [internal/profiles/base.go:13-86]().

### Toolchains vs. Agents
- **Agents**: Merged on top of `BaseProfile()`. They represent high-level AI tools (e.g., Claude Code).
- **Toolchains**: (e.g., `npm`, `gh`, `cargo`) Do **not** inherit from `BaseProfile()` by default to maintain a smaller attack surface [internal/profiles/registry.go:28-34]().

### Keyring Secrets (Linux)
Profiles can define `KeyringSecrets` which map environment variables to system keyring lookups. On Linux, `ResolveKeyringSecrets` uses `secret-tool` to fetch these *before* sandboxing, injecting them as environment variables to avoid exposing the D-Bus session bus to the sandbox [internal/profiles/keyring.go:18-65](), [internal/profiles/toolchains/scm.go:30-32]().

```mermaid
graph LR
    subgraph CodeSpace["Code Entity Space"]
        AD["AgentDef (registry.go)"]
        BP["BaseProfile() (base.go)"]
        GAP["GetAgentProfile() (registry.go)"]
        RKS["ResolveKeyringSecrets() (keyring.go)"]
    end

    subgraph NL["Natural Language Space"]
        PROF["Profile System"]
        INH["Inheritance (extends)"]
        KEY["Keyring Injection"]
    end

    PROF -.-> AD
    INH -.-> BP
    INH -.-> GAP
    KEY -.-> RKS
```

**Sources:** [internal/profiles/registry.go:68-83](), [internal/profiles/base.go:13-86](), [internal/profiles/keyring.go:11-18]()

---

## Profile Management and First-Run UX

Greywall provides an interactive prompt when a known agent is run without a saved profile.

### First-Run Prompt
`PromptFirstRun()` displays a colorized summary of the profile's filesystem and network rules [internal/profiles/prompt.go:129-192]().

- **[Y] Use profile**: Saves the built-in profile to the learned directory so it auto-loads next time [internal/profiles/resolve.go:73-77]().
- **[e] Edit first**: Saves the profile and opens the user's `$EDITOR` for manual adjustment [internal/profiles/resolve.go:79-93]().
- **[s] Skip**: Runs with restrictive defaults for this session only [internal/profiles/resolve.go:101-103]().
- **[n] Don't ask again**: Suppresses future prompts for this command by updating `~/.config/greywall/preferences.json` [internal/profiles/resolve.go:95-99]().

### Ad-Hoc Commands
Basic Unix utilities (e.g., `ls`, `cat`, `grep`, `git`, `make`) are classified as "ad-hoc" and never trigger the first-run prompt, even if they lack a profile [internal/profiles/registry.go:120-152]().

```mermaid
graph TD
    subgraph UI["User Interaction (prompt.go)"]
        PFR["PromptFirstRun()"]
    end

    subgraph Logic["Resolution Logic (resolve.go)"]
        RFR["ResolveFirstRun()"]
        SAT["SaveAsTemplate()"]
        EAV["editAndValidate()"]
    end

    subgraph Registry["Registry (registry.go)"]
        IKA["IsKnownAgent()"]
        IAC["IsAdHocCommand()"]
    end

    IKA -->|Known| RFR
    IAC -->|Not AdHoc| RFR
    RFR --> PFR
    PFR -->|Yes| SAT
    PFR -->|Edit| EAV
```

**Sources:** [internal/profiles/prompt.go:129-192](), [internal/profiles/resolve.go:17-104](), [internal/profiles/registry.go:120-152]()

---

## Profile Inheritance (extends)

Profiles can extend other profiles or files using the `extends` field [docs/templates.md:32-41]().

### Merging Rules
When a profile extends another, settings are merged using specific logic:
- **Slices (paths, commands)**: Appended and deduplicated [docs/templates.md:45]().
- **Booleans**: OR logic (true if either enables the feature) [docs/templates.md:46]().
- **Integers/Ports**: The override (child) value wins [docs/templates.md:47]().

### Example: Customizing a Template
```json
{
  "extends": "code",
  "filesystem": {
    "allowWrite": [".", "/tmp"],
    "denyRead": ["~/.ssh/id_rsa"]
  }
}
```
This inherits the network rules and base filesystem protections of the `code` profile while adding custom paths [docs/templates.md:68-78]().

**Sources:** [docs/templates.md:30-64](), [internal/profiles/registry.go:72-83]()

---

## Network Rules Precedence

Profiles can declare network rules in the `network.rules` field. These are forwarded to `greyproxy` as session-scoped rules [docs/templates.md:87-89]().

### `--no-network-rules`
Users can apply a profile's filesystem and credential protections while ignoring its network allow-list by using the `--no-network-rules` flag [docs/templates.md:90-95]().
- **Effect**: Suppresses rules from the profile.
- **Exceptions**: CLI-provided `--allow` rules are still forwarded [docs/templates.md:99]().

**Sources:** [docs/templates.md:87-101](), [docs/cli-reference.md:36]()

---

# Page: Learning Mode

# Learning Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/learning-mode.md](docs/learning-mode.md)
- [internal/sandbox/learning.go](internal/sandbox/learning.go)
- [internal/sandbox/learning_darwin.go](internal/sandbox/learning_darwin.go)
- [internal/sandbox/learning_darwin_test.go](internal/sandbox/learning_darwin_test.go)
- [internal/sandbox/learning_linux.go](internal/sandbox/learning_linux.go)
- [internal/sandbox/learning_linux_test.go](internal/sandbox/learning_linux_test.go)
- [internal/sandbox/learning_stub.go](internal/sandbox/learning_stub.go)
- [internal/sandbox/learning_test.go](internal/sandbox/learning_test.go)

</details>



Learning Mode is greywall's automatic profile generation system. It traces a command's filesystem access using platform-specific tools (`strace` on Linux, `eslogger` on macOS), analyzes the observed paths, and generates a configuration profile that can be reused for subsequent runs.

This page covers the implementation details of learning mode. For configuration file structure, see [Configuration Files](#6.1). For how profiles are loaded and merged, see [Profile System](#6.2).

## System Overview

Learning mode operates as an optional execution path that relaxes filesystem restrictions while capturing access patterns. The captured data flows through a series of filtering and collapsing transformations before being serialized as a JSONC configuration profile.

**Core execution flow:**

```mermaid
graph TB
    CLI["CLI --learning flag"]
    RELAX["Relaxed sandbox<br/>(filesystem permissive)"]
    TRACE["Platform-specific tracer<br/>strace (Linux)<br/>eslogger (macOS)"]
    PARSE["ParseStraceLog() / ParseEsloggerLog()<br/>Extract read/write paths"]
    RESULT["TraceResult struct<br/>ReadPaths []string<br/>WritePaths []string"]
    FILTER["Filter paths<br/>Remove system defaults<br/>Remove sensitive paths"]
    COLLAPSE["CollapsePaths()<br/>Group into minimal directories"]
    TEMPLATE["buildTemplate()<br/>Generate JSONC profile"]
    SAVE["Save to<br/>LearnedTemplatePath()"]
    AUTOLOAD["Next run auto-loads<br/>profile if command matches"]
    
    CLI --> RELAX
    RELAX --> TRACE
    TRACE --> PARSE
    PARSE --> RESULT
    RESULT --> FILTER
    FILTER --> COLLAPSE
    COLLAPSE --> TEMPLATE
    TEMPLATE --> SAVE
    SAVE --> AUTOLOAD
```

Sources: [docs/learning-mode.md:10-15](), [internal/sandbox/learning.go:73-200]()

## Core Data Structures

### TraceResult

The `TraceResult` struct holds the parsed output from the system tracer before filtering and transformation.

```go
type TraceResult struct {
	WritePaths []string
	ReadPaths  []string
}
```

**Fields:**
- `WritePaths`: All file paths accessed for writing (create, write, mkdir, etc.) [internal/sandbox/learning.go:18-18]()
- `ReadPaths`: All file paths accessed for reading (openat O_RDONLY, etc.) [internal/sandbox/learning.go:19-19]()

Sources: [internal/sandbox/learning.go:17-20]()

### LearnedTemplateInfo

The `LearnedTemplateInfo` struct represents a stored learned profile.

```go
type LearnedTemplateInfo struct {
	Name string // profile name (without .json)
	Path string // full path to the profile file
}
```

Used by `ListLearnedTemplates()` to enumerate available profiles in the learned directory. [internal/sandbox/learning.go:343-347]()

Sources: [internal/sandbox/learning.go:343-347]()

## Template Storage

### Directory Structure

Learned profiles are stored in a platform-specific configuration directory determined by `LearnedTemplateDir()` [internal/sandbox/learning.go:34-45]():

| Platform | Path |
|----------|------|
| Linux (XDG) | `$XDG_CONFIG_HOME/greywall/learned/` |
| Linux (default) | `~/.config/greywall/learned/` |
| macOS | `~/Library/Application Support/greywall/learned/` |

**Key functions:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `LearnedTemplateDir()` | Get learned profile directory [internal/sandbox/learning.go:34-45]() | `string` |
| `LearnedTemplatePath(cmdName)` | Get path for specific profile [internal/sandbox/learning.go:48-50]() | `string` |
| `SanitizeTemplateName(name)` | Sanitize command name for filename [internal/sandbox/learning.go:54-71]() | `string` |

Sources: [internal/sandbox/learning.go:34-71]()

### Template Naming

Command names are sanitized for use as filenames using `SanitizeTemplateName()`. It forces lowercase to prevent case-insensitive filesystem collisions on macOS [internal/sandbox/learning.go:55-59]().

```mermaid
graph LR
    INPUT["Input command name"]
    LOWER["strings.ToLower()"]
    REGEX["regexp.MustCompile<br/>[^a-zA-Z0-9._-] → _"]
    COLLAPSE["Collapse __<br/>to single _"]
    TRIM["strings.Trim _ and ."]
    EMPTY["Check empty<br/>→ 'unknown'"]
    OUTPUT["Sanitized name"]
    
    INPUT --> LOWER
    LOWER --> REGEX
    REGEX --> COLLAPSE
    COLLAPSE --> TRIM
    TRIM --> EMPTY
    EMPTY --> OUTPUT
```

**Examples:**
- `Claude` → `claude` [internal/sandbox/learning_test.go:26-26]()
- `my app` → `my_app` [internal/sandbox/learning_test.go:20-20]()
- `/usr/bin/opencode` → `usr_bin_opencode` [internal/sandbox/learning_test.go:21-21]()

Sources: [internal/sandbox/learning.go:54-71](), [internal/sandbox/learning_test.go:11-38]()

## Path Filtering Pipeline

The `GenerateLearnedTemplate()` function processes raw trace results through multiple filtering stages [internal/sandbox/learning.go:73-200]():

```mermaid
graph TB
    TRACE["TraceResult<br/>Raw read/write paths"]
    
    subgraph "Write Path Processing"
        W1["Remove default writable<br/>isDefaultWritablePath()"]
        W2["Remove sensitive<br/>isSensitivePath()"]
        W3["CollapsePaths()<br/>Group to directories"]
        W4["toTildePath()"]
        W5["Add '.' (CWD)"]
    end
    
    subgraph "Read Path Processing"
        R1["Remove system defaults<br/>GetDefaultReadablePaths()"]
        R2["Remove CWD subtree<br/>(auto-included)"]
        R3["Remove sensitive<br/>isSensitivePath()"]
        R4["CollapsePaths()<br/>Group to directories"]
        R5["toTildePath()"]
    end
    
    TEMPLATE["buildTemplate()<br/>Generate JSONC"]
    
    TRACE --> W1
    W1 --> W2
    W2 --> W3
    W3 --> W4
    W4 --> W5
    W5 --> TEMPLATE
    
    TRACE --> R1
    R1 --> R2
    R2 --> R3
    R3 --> R4
    R4 --> R5
    R5 --> TEMPLATE
```

Sources: [internal/sandbox/learning.go:73-138]()

### Write Path Filtering

**Step 1: Remove default writable paths**

The `isDefaultWritablePath()` function checks if a path is already writable by default in the sandbox [internal/sandbox/learning.go:271-285](). It checks against paths like `/dev/null` and `/dev/stdout` [internal/sandbox/learning_test.go:183-184]().

**Step 2: Remove sensitive paths**

The `isSensitivePath()` function filters out dangerous targets [internal/sandbox/learning.go:287-316]():

| Pattern | Reason |
|---------|--------|
| `~/.bashrc`, `~/.zshrc`, etc. | Shell startup files [internal/sandbox/learning.go:292-292]() |
| `~/.ssh/**` | SSH keys and config [internal/sandbox/learning.go:303-303]() |
| `~/.gnupg/**` | GPG keys [internal/sandbox/learning.go:305-305]() |
| `.env`, `.env.*` | Environment secrets [internal/sandbox/learning.go:310-312]() |

Sources: [internal/sandbox/learning.go:271-316]()

### Read Path Filtering

**Step 1: Remove system defaults**

Paths under `GetDefaultReadablePaths()` are excluded as they're already accessible [internal/sandbox/learning.go:106-118]().

**Step 2: Remove CWD subtree**

The current working directory and all its descendants are excluded because the sandbox auto-includes CWD [internal/sandbox/learning.go:119-122]().

**Step 3: Remove sensitive paths**

Same logic as write path filtering using `isSensitivePath()` [internal/sandbox/learning.go:124-129]().

Sources: [internal/sandbox/learning.go:103-131]()

## Path Collapsing Algorithm

The `CollapsePaths()` function minimizes the number of paths by grouping related files into their parent directories [internal/sandbox/learning.go:204-246]().

### Application Directory Detection

The algorithm uses `findApplicationDirectory()` to identify well-known application-specific directories [internal/sandbox/learning.go:248-269]().

**Well-known parents:**
```go
var wellKnownParents = []string{
	".cache",
	".config",
	".local/share",
	".local/state",
	".local/lib",
	".data",
}
```
Sources: [internal/sandbox/learning.go:24-31]()

For paths under these parents (e.g., `~/.cache/opencode/db/main.sqlite`), the function extracts the first directory below the well-known parent (`~/.cache/opencode`) [internal/sandbox/learning.go:256-261]().

### Collapsing Logic

The logic differentiates between application directories and standalone files. For app dirs, it collapses if 2+ paths share the root. For standalone files directly under home, it keeps the exact path to avoid broad access [internal/sandbox/learning.go:228-241]().

Sources: [internal/sandbox/learning.go:204-246]()

### Deduplication

The `deduplicateSubPaths()` function removes paths that are sub-paths of other paths in the result [internal/sandbox/learning.go:374-399]().

**Example:**
- Input: `["/home/user/.cache", "/home/user/.cache/opencode"]`
- Output: `["/home/user/.cache"]` [internal/sandbox/learning_test.go:234-235]()

Sources: [internal/sandbox/learning.go:374-399]()

## Template Generation

The `buildTemplate()` function creates the JSONC profile content [internal/sandbox/learning.go:423-457]().

### Generated Sections

| Section | Content | Source |
|---------|---------|--------|
| `allowRead` | Collapsed read paths | `TraceResult.ReadPaths` |
| `allowWrite` | `"."` + collapsed write paths | `TraceResult.WritePaths` |
| `denyWrite` | Shell startup files | `getDangerousFilePatterns()` |
| `denyRead` | SSH, GPG, `.env` | `getSensitiveReadPatterns()` |

Sources: [internal/sandbox/learning.go:423-457]()

## Platform-Specific Implementation

### Linux: strace

On Linux, `ParseStraceLog` extracts paths from syscalls like `openat`, `mkdirat`, `unlinkat`, and `renameat2` [internal/sandbox/learning_linux.go:16-18](). It specifically checks for write flags (O_WRONLY, O_RDWR, etc.) in `openat` calls [internal/sandbox/learning_linux.go:21-21]().

### macOS: eslogger

On macOS, greywall uses `eslogger` to stream events from the Endpoint Security framework [docs/learning-mode.md:12-12]().

**Process Tree Tracking:**
Because `eslogger` is system-wide, `ParseEsloggerLog` performs a two-pass scan. Pass 1 builds a PID tree from `fork` events starting at the `rootPID` [internal/sandbox/learning_darwin.go:135-153](). Pass 2 filters filesystem events (`open`, `create`, `write`, `unlink`, `truncate`, `rename`, `link`) against this PID set [internal/sandbox/learning_darwin.go:159-223]().

**Event Classification:**
Events are classified into `opRead` or `opWrite` [internal/sandbox/learning_darwin.go:16-20](). For example, an `open` event is `opWrite` if the `fflag` contains `fwriteFlag` (0x0002) [internal/sandbox/learning_darwin.go:23-23]().

Sources: [internal/sandbox/learning_linux.go:1-163](), [internal/sandbox/learning_darwin.go:1-235]()

## Code Entity Reference

### Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `GenerateLearnedTemplate()` | [internal/sandbox/learning.go:75-200]() | Main template generation function |
| `CollapsePaths()` | [internal/sandbox/learning.go:204-246]() | Group paths into minimal directories |
| `findApplicationDirectory()` | [internal/sandbox/learning.go:248-269]() | Detect app-level directory for a path |
| `ParseStraceLog()` | [internal/sandbox/learning_linux.go:33-89]() | Parse Linux strace output |
| `ParseEsloggerLog()` | [internal/sandbox/learning_darwin.go:129-235]() | Parse macOS eslogger JSON output |
| `classifyEsloggerEvent()` | [internal/sandbox/learning_darwin.go:303-393]() | Categorize macOS ES events |
| `scanForkEvents()` | [internal/sandbox/learning_darwin.go:244-279]() | Build PID relationships for macOS |

Sources: [internal/sandbox/learning.go:1-458](), [internal/sandbox/learning_linux.go:1-245](), [internal/sandbox/learning_darwin.go:1-400]()

---

# Page: Go Library API

# Go Library API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/benchmarking.md](docs/benchmarking.md)
- [docs/concepts.md](docs/concepts.md)
- [docs/library.md](docs/library.md)
- [internal/sandbox/manager.go](internal/sandbox/manager.go)
- [pkg/greywall/greywall.go](pkg/greywall/greywall.go)

</details>



This document covers the programmatic API for using greywall from Go code. The Go library allows you to create and manage sandboxed command execution from your own Go applications.

For information about the CLI interface, see [CLI Reference](#2.3). For details on how the sandbox implementations work under the hood, see [Platform Implementations](#4).

## Purpose and Scope

The `pkg/greywall` package provides a public Go API for:
- Checking platform support
- Loading and creating configurations
- Creating and managing sandbox managers
- Wrapping commands with sandbox restrictions
- Controlling the sandbox lifecycle

The package wraps the internal implementation details (bubblewrap, sandbox-exec, greyproxy, etc.) behind a clean, platform-agnostic interface.

## Package Structure

```mermaid
graph TB
    subgraph "Public API (pkg/greywall)"
        API["pkg/greywall"]
        IsSupported["IsSupported()"]
        DefaultConfig["DefaultConfig()"]
        LoadConfig["LoadConfig(path)"]
        DefaultConfigPath["DefaultConfigPath()"]
        NewManager["NewManager(cfg, debug, monitor)"]
        Manager["Manager"]
        Config["Config"]
        NetworkConfig["NetworkConfig"]
        FilesystemConfig["FilesystemConfig"]
        CommandConfig["CommandConfig"]
        SSHConfig["SSHConfig"]
    end
    
    subgraph "Internal Implementation"
        ConfigPkg["internal/config"]
        SandboxPkg["internal/sandbox"]
        ProfilesPkg["internal/profiles"]
        ProxyPkg["internal/proxy"]
        PlatformPkg["internal/platform"]
    end
    
    API --> IsSupported
    API --> DefaultConfig
    API --> LoadConfig
    API --> DefaultConfigPath
    API --> NewManager
    NewManager --> Manager
    API --> Config
    Config --> NetworkConfig
    Config --> FilesystemConfig
    Config --> CommandConfig
    Config --> SSHConfig
    
    API -. "proxies to" .-> ConfigPkg
    API -. "proxies to" .-> SandboxPkg
    API -. "proxies to" .-> PlatformPkg
```

**Sources:** [pkg/greywall/greywall.go:1-47](), [internal/sandbox/manager.go:14-34]()

## Installation

Add greywall as a dependency to your Go project:

```bash
go get github.com/GreyhavenHQ/greywall
```

Then import the package:

```go
import "github.com/GreyhavenHQ/greywall/pkg/greywall"
```

**Sources:** [docs/library.md:10-14]()

## Quick Start Example

This minimal example shows the basic lifecycle: check support, create config, initialize manager, wrap command, execute, and cleanup.

```go
package main

import (
    "fmt"
    "os/exec"

    "github.com/GreyhavenHQ/greywall/pkg/greywall"
)

func main() {
    // Check platform support
    if !greywall.IsSupported() {
        fmt.Println("Sandboxing not supported on this platform")
        return
    }

    // Create config
    cfg := &greywall.Config{
        Network: greywall.NetworkConfig{
            AllowedDomains: []string{"api.example.com"},
        },
    }

    // Create and initialize manager
    manager := greywall.NewManager(cfg, false, false)
    defer manager.Cleanup()

    if err := manager.Initialize(); err != nil {
        panic(err)
    }

    // Wrap the command
    wrapped, err := manager.WrapCommand("curl https://api.example.com/data")
    if err != nil {
        panic(err)
    }

    // Execute it
    cmd := exec.Command("sh", "-c", wrapped)
    output, _ := cmd.CombinedOutput()
    fmt.Println(string(output))
}
```

**Sources:** [docs/library.md:18-60]()

## Manager Lifecycle

The `Manager` type in `internal/sandbox/manager.go` orchestrates the complete sandbox lifecycle.

### Manager Lifecycle Flow

```mermaid
sequenceDiagram
    participant App as "Your Application"
    participant Manager as "sandbox.Manager"
    participant Platform as "internal/platform"
    participant Proxy as "greyproxy Service"
    participant Bridge as "ProxyBridge/DnsBridge"
    
    App->>Manager: NewManager(cfg, debug, monitor)
    Manager->>Platform: IsSupported()
    Platform-->>Manager: bool
    
    App->>Manager: Initialize()
    
    alt Linux
        Manager->>Manager: extractTun2Socks()
        Manager->>Bridge: NewProxyBridge(ProxyURL)
        Manager->>Bridge: NewDnsBridge(DnsAddr)
    else macOS + Learning
        Manager->>Manager: sudo /usr/bin/eslogger
    end
    
    App->>Manager: WrapCommand(cmd)
    Manager->>Manager: buildPlatformArgs()
    Manager-->>App: sandboxed command string
    
    App->>App: Execute command (exec.Command)
    
    App->>Manager: Cleanup()
    Manager->>Bridge: Cleanup()
    Manager->>Manager: os.Remove(tun2socksPath)
```

**Sources:** [internal/sandbox/manager.go:71-137](), [internal/sandbox/manager.go:140-172](), [internal/sandbox/manager.go:211-236]()

### Manager Methods

| Method | Description | File Reference |
|--------|-------------|----------------|
| `Initialize()` | Sets up bridges, extracts `tun2socks`, and starts `eslogger` (macOS) | [internal/sandbox/manager.go:71-137]() |
| `WrapCommand(command)` | Returns the platform-specific sandboxed command string | [internal/sandbox/manager.go:239-258]() |
| `SetExposedPorts(ports)` | Configures ports for inbound connections (ReverseBridge) | [internal/sandbox/manager.go:46-48]() |
| `SetLearning(enabled)` | Enables filesystem tracing mode | [internal/sandbox/manager.go:51-53]() |
| `SetCommandName(name)` | Sets command name for learning mode profile generation | [internal/sandbox/manager.go:56-58]() |
| `Cleanup()` | Stops bridges and deletes temporary binaries/logs | [internal/sandbox/manager.go:211-236]() |

**Sources:** [internal/sandbox/manager.go:14-68](), [pkg/greywall/greywall.go:25-32]()

## Core Functions and Types

### Platform Detection

#### `IsSupported() bool`

Returns `true` if the current platform supports sandboxing (Linux or macOS).

```go
if !greywall.IsSupported() {
    log.Fatal("Platform not supported")
}
```

**Sources:** [pkg/greywall/greywall.go:11-13]()

### Configuration Functions

#### `DefaultConfig() *Config`

Returns a default configuration with all network blocked and deny-by-default filesystem reads enabled.

```go
cfg := greywall.DefaultConfig()
cfg.Network.AllowedDomains = []string{"example.com"}
```

**Sources:** [pkg/greywall/greywall.go:35-37]()

#### `LoadConfig(path string) (*Config, error)`

Loads configuration from a JSON file. Supports JSONC (comments allowed).

```go
cfg, err := greywall.LoadConfig(greywall.DefaultConfigPath())
```

**Sources:** [pkg/greywall/greywall.go:40-42]()

## Configuration Types

The configuration system is defined in `internal/config` and aliased in `pkg/greywall`.

### Config

The root configuration type.

```go
type Config struct {
    Extends    string           // Template to extend (e.g., "code")
    Network    NetworkConfig
    Filesystem FilesystemConfig
    Command    CommandConfig
    SSH        SSHConfig
    AllowPty   bool             // Allow PTY allocation
}
```

**Sources:** [docs/library.md:166-174]()

### NetworkConfig

Controls network access and proxying behavior.

```go
type NetworkConfig struct {
    AllowedDomains      []string // Domains to allow (supports *.example.com)
    DeniedDomains       []string // Domains to explicitly deny
    AllowUnixSockets    []string // Specific Unix socket paths to allow
    AllowAllUnixSockets bool     // Allow all Unix socket connections
    AllowLocalBinding   bool     // Allow binding to localhost ports
    AllowLocalOutbound  *bool    // Allow outbound to localhost (defaults to AllowLocalBinding)
    HTTPProxyPort       int      // Override HTTP proxy port (0 = auto)
    SOCKSProxyPort      int      // Override SOCKS proxy port (0 = auto)
}
```

**Sources:** [docs/library.md:179-190]()

### FilesystemConfig

Controls filesystem access using a deny-by-default model.

```go
type FilesystemConfig struct {
    DefaultDenyRead *bool    // Deny reads by default (true when nil)
    AllowRead       []string // Paths to allow reading
    DenyRead        []string // Paths to deny read access
    AllowWrite      []string // Paths to allow write access
    DenyWrite       []string // Paths to explicitly deny write access
    AllowGitConfig  bool     // Allow read access to ~/.gitconfig
}
```

**Sources:** [docs/library.md:193-201]()

## Platform Differences in Library Behavior

While the Go API is unified, the `Manager` performs different initialization steps based on `platform.Detect()`.

| Feature | Linux (`Manager.Initialize`) | macOS (`Manager.Initialize`) |
|---------|-----------------------------|------------------------------|
| **Network** | Extracts `tun2socks`, starts `ProxyBridge` (socat) | Sets `HTTP_PROXY` env vars |
| **Bridges** | Creates `ReverseBridge` and `ForwardBridge` if needed | Not required (shared stack) |
| **Learning** | Prepares `straceLogPath` | Starts `sudo /usr/bin/eslogger` |
| **Cleanup** | Removes `tun2socks` binary | Stops `eslogger` subprocess |

**Sources:** [internal/sandbox/manager.go:83-137](), [internal/sandbox/manager.go:140-208](), [docs/concepts.md:45-50]()

## Implementation Details

### Bridge Management

On Linux, the `Manager` maintains several bridge components to connect the isolated network namespace to the host:

```mermaid
graph LR
    subgraph "Manager (internal/sandbox)"
        PB["ProxyBridge"]
        DB["DnsBridge"]
        RB["ReverseBridge"]
        FB["ForwardBridge"]
        DBusB["DbusBridge"]
    end

    subgraph "Sandbox (Isolated Net NS)"
        App["Sandboxed Process"]
        Tun["tun2socks"]
    end

    App -- "DNS/TCP/UDP" --> Tun
    Tun -- "Unix Socket" --> PB
    Tun -- "Unix Socket" --> DB
    PB -- "TCP" --> ExternalProxy["SOCKS5 Proxy"]
```

**Sources:** [internal/sandbox/manager.go:14-20](), [internal/sandbox/manager.go:150-172](), [docs/concepts.md:21-22]()

### Resource Cleanup

The `Cleanup()` method is critical for preventing resource leaks, especially on Linux where `socat` processes and temporary binaries are used.

```go
func (m *Manager) Cleanup() {
    if m.proxyBridge != nil { m.proxyBridge.Cleanup() }
    if m.dnsBridge != nil { m.dnsBridge.Cleanup() }
    if m.reverseBridge != nil { m.reverseBridge.Cleanup() }
    if m.forwardBridge != nil { m.forwardBridge.Cleanup() }
    if m.dbusBridge != nil { m.dbusBridge.Cleanup() }
    if m.tun2socksPath != "" { os.Remove(m.tun2socksPath) }
    // ... macOS eslogger cleanup
}
```

**Sources:** [internal/sandbox/manager.go:211-236]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Makefile](Makefile)
- [docs/architecture.md](docs/architecture.md)
- [docs/contributing.md](docs/contributing.md)
- [docs/faq.md](docs/faq.md)
- [scripts/pre-commit](scripts/pre-commit)

</details>



This document provides an overview of the greywall development process, including setting up a development environment, building from source, running tests, and understanding the release workflow. It is intended for contributors and developers who want to work on greywall itself.

For detailed build instructions and dependency management, see [Building from Source](#8.1). For information about the CI/CD infrastructure, see [CI/CD Pipeline](#8.2). For the release and distribution process, see [Release Process](#8.3).

---

## Development Environment Prerequisites

Developing greywall requires platform-specific dependencies and tooling. The development environment differs significantly between Linux and macOS due to the platform-specific sandbox implementations.

### Common Requirements

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Go | 1.25+ | Primary language [CONTRIBUTING.md:10]() |
| Make | Any recent | Build orchestration [Makefile:1-11]() |
| Git | Any recent | Version control |

### Linux-Specific Requirements

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| `bubblewrap` | Process isolation | `sudo apt install bubblewrap` [CONTRIBUTING.md:82]() |
| `socat` | Unix socket bridges | `sudo apt install socat` [CONTRIBUTING.md:82]() |
| `xdg-dbus-proxy` | D-Bus isolation | `sudo apt install xdg-dbus-proxy` [CONTRIBUTING.md:82]() |

### macOS-Specific Requirements

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| `sandbox-exec` | Built-in sandboxing | System provided [ARCHITECTURE.md:7]() |

Sources: [CONTRIBUTING.md:9-12](), [CONTRIBUTING.md:76-86](), [ARCHITECTURE.md:45-46]()

---

## Development Workflow

The development lifecycle is managed through a comprehensive `Makefile`.

**Development Lifecycle Workflow**

```mermaid
graph TB
    subgraph "Local Development"
        CLONE["git clone"]
        SETUP["make setup"]
        CODE["Write Code"]
        FMT["make fmt"]
        LINT["make lint"]
        UNIT["make test"]
        BUILD["make build"]
    end
    
    subgraph "Verification"
        RUN["make run"]
        SMOKE["./scripts/smoke_test.sh"]
    end
    
    subgraph "Release Flow"
        REL_PATCH["make release"]
        REL_MINOR["make release-minor"]
        REL_BETA["make release-beta"]
    end
    
    CLONE --> SETUP
    SETUP --> CODE
    CODE --> FMT
    FMT --> LINT
    LINT --> UNIT
    UNIT --> BUILD
    BUILD --> RUN
    RUN --> SMOKE
    SMOKE --> REL_PATCH
```

Sources: [Makefile:11-148](), [CONTRIBUTING.md:16-38]()

---

## Build System

The greywall build system uses `make` for orchestration. A critical step in the build process is the embedding of `tun2socks` for Linux transparent proxying.

### Build Targets

| Target | Purpose | Usage |
|--------|---------|-------|
| `make setup` | Install deps, lint tools, and git hooks | Initial environment setup [Makefile:139]() |
| `make download-tun2socks` | Fetch `tun2socks` v2.5.2 binaries | Required for Linux builds [Makefile:15-32]() |
| `make build` | Standard development build | Local development [Makefile:34-36]() |
| `make build-ci` | Build with git version and build time ldflags | Used in CI pipelines [Makefile:38-43]() |
| `make build-linux` | Cross-compile for Linux (amd64) | Distribution [Makefile:66-68]() |
| `make build-darwin` | Cross-compile for macOS (arm64) | Distribution [Makefile:70-72]() |

### Code Entity Mapping: Build System

| Component | Code Entity | File Path |
|-----------|-------------|-----------|
| CLI Entry | `main.go` | [cmd/greywall/main.go:1-39]() |
| Version Info | `main.version`, `main.buildTime` | [Makefile:43]() |
| Embedded Binaries | `internal/sandbox/bin` | [Makefile:9]() |

Sources: [Makefile:1-148](), [ARCHITECTURE.md:37-38]()

---

## Testing Strategy

Greywall employs unit tests and platform-specific integration tests.

**Test Execution Architecture**

```mermaid
graph TB
    subgraph "Test Execution"
        T_UNIT["make test<br/>go test -v ./..."]
        T_CI["make test-ci<br/>go test -race -cover"]
    end
    
    subgraph "Manual Verification (macOS)"
        M_NET["./greywall curl https://example.com"]
        M_MON["./greywall -m -c 'touch /etc/test'"]
    end
    
    subgraph "Manual Verification (Linux)"
        L_NET["./greywall curl https://example.com"]
        L_INT["go test -run 'TestIntegration'"]
    end

    T_UNIT --> T_CI
    T_CI --> M_NET
    M_NET --> L_NET
```

### Running Tests Locally

```bash
# Standard test run
make test

# CI-style run with race detection and coverage
make test-ci

# Linux-specific integration tests
go test -v -run 'TestIntegration|TestLinux' ./internal/sandbox/...
```

Sources: [Makefile:45-52](), [CONTRIBUTING.md:49-80]()

---

## CI/CD and Quality Gates

Greywall enforces code quality through linting and automated formatting checks.

### Quality Gates

| Gate | Tool | Command |
|------|------|---------|
| Formatting | `gofumpt` | `make fmt-check` [Makefile:99-107]() |
| Linting | `golangci-lint` | `make lint` [Makefile:109-111]() |
| Git Hooks | `scripts/pre-commit` | Automatic on commit [scripts/pre-commit:1-33]() |

The project uses `gofumpt` for strict formatting and `golangci-lint` for static analysis. These tools are installed via `make install-lint-tools`.

Sources: [Makefile:74-85](), [scripts/pre-commit:1-33]()

---

## Release Process

Releases are triggered by scripts that handle version tagging and are then processed by GitHub Actions and GoReleaser.

### Release Commands

| Command | Action |
|---------|--------|
| `make release` | Create a patch release (v0.0.X) [Makefile:113-115]() |
| `make release-minor` | Create a minor release (v0.X.0) [Makefile:117-119]() |
| `make release-beta` | Create a beta release (v0.0.X-beta.N) [Makefile:121-123]() |

The underlying `scripts/release.sh` performs preflight checks and tags the repository. Once pushed, the CI pipeline builds for:
- **Linux**: amd64, arm64
- **macOS (darwin)**: amd64, arm64

Sources: [Makefile:113-124](), [CONTRIBUTING.md:120-161]()

---

# Page: Building from Source

# Building from Source

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.golangci.yml](.golangci.yml)
- [CLAUDE.md](CLAUDE.md)
- [Makefile](Makefile)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [scripts/pre-commit](scripts/pre-commit)

</details>



This page covers how to build `greywall` from source, including development prerequisites, build commands, testing procedures, and platform-specific dependency management. `greywall` uses a `Makefile` to orchestrate complex build steps such as downloading architecture-specific binaries for embedding.

## Prerequisites

### Go Version
`greywall` requires Go 1.25 or later. The minimum version is specified in the module definition [go.mod:3-3]().

### System Dependencies
`greywall` relies on several system-level utilities to implement its security model.

**Linux Requirements:**
- `bubblewrap` (executable `bwrap`): Core process isolation and namespace management [CLAUDE.md:68-68]().
- `socat`: Used to create Unix socket bridges for proxy relay [CLAUDE.md:68-68]().
- `tun2socks` v2.5.2: Embedded binary used for transparent TCP/UDP proxying [Makefile:8-9]().
- Kernel 5.13+: Required for Landlock LSM support.
- Kernel 5.7+: Required for BPF-based features.

**macOS Requirements:**
- `sandbox-exec`: Built-in macOS tool for Seatbelt profiles [CLAUDE.md:3-3]().

**Development Tools:**
- `gofumpt`: Enforced code formatter [Makefile:76-76]().
- `golangci-lint` v2: Static analysis and linting [Makefile:77-77]().

Sources: [go.mod:3-3](), [Makefile:8-9](), [Makefile:76-77](), [CLAUDE.md:3-3](), [CLAUDE.md:68-68]()

## Build Process

The build process is managed via `make`. A critical step is the `download-tun2socks` target, which fetches architecture-specific binaries (`amd64` and `arm64`) into `internal/sandbox/bin` for embedding into the final Go binary [Makefile:15-32]().

### Development Setup
To prepare a fresh environment, run the `setup` target. This downloads Go dependencies, installs linting tools, and configures git hooks [Makefile:86-87]().

```bash
make setup
```

### Compiling the Binary
The standard `build` command automatically ensures `tun2socks` is present before compiling the CLI entry point at `cmd/greywall` [Makefile:34-36]().

```bash
make build
```

For CI environments, `make build-ci` injects version metadata (git commit, build time, and version tags) using `-ldflags` [Makefile:38-43]().

### Platform-Specific Builds
You can cross-compile for specific targets using dedicated make targets:
- **Linux (AMD64):** `make build-linux` (sets `CGO_ENABLED=0`) [Makefile:66-68]().
- **macOS (ARM64):** `make build-darwin` [Makefile:70-72]().

Sources: [Makefile:15-43](), [Makefile:66-72](), [Makefile:86-87]()

## Build Pipeline Architecture

The following diagram illustrates the flow from source code and external assets to the final `greywall` binary.

```mermaid
graph TD
    subgraph "External Assets"
        T2S_DL["tun2socks GitHub Releases"]
    end

    subgraph "Source Code"
        CMD["cmd/greywall/main.go"]
        INT["internal/sandbox/*.go"]
        PKG["pkg/greywall/*.go"]
    end

    subgraph "Build Steps"
        DL["make download-tun2socks"]
        GO["go build"]
        LDF["-ldflags (version info)"]
    end

    T2S_DL -->|"curl/unzip"| DL
    DL -->|"internal/sandbox/bin/"| GO
    CMD --> GO
    INT --> GO
    PKG --> GO
    LDF --> GO
    GO -->|"Output"| BIN["greywall binary"]
```

**Build Dependency and Entity Association**

Sources: [Makefile:15-43](), [CLAUDE.md:33-51]()

## Dependency Management

### Go Modules
`greywall` maintains a minimal dependency footprint with 4 direct dependencies [CLAUDE.md:66-66]():
- `github.com/spf13/cobra`: CLI framework [go.mod:7-7]().
- `github.com/bmatcuk/doublestar/v4`: Path glob matching for sandbox rules [go.mod:6-6]().
- `github.com/tidwall/jsonc`: JSON with comments support for config files [go.mod:8-8]().
- `golang.org/x/sys`: Low-level OS primitives (Landlock, Seccomp) [go.mod:9-9]().

### Linting and Formatting
The project enforces strict code quality via `golangci-lint`. The configuration in `.golangci.yml` enables linters like `errcheck`, `gosec`, `govet`, and `staticcheck` [.golangci.yml:6-15](). Code must be formatted with `gofumpt` [.golangci.yml:32-32]().

The `make lint` target runs the linter with parallel execution enabled [Makefile:109-111]().

Sources: [go.mod:5-10](), [.golangci.yml:6-32](), [Makefile:109-111](), [CLAUDE.md:66-66]()

## Testing

### Unit and Integration Tests
Standard Go tests are executed via `make test` [Makefile:45-47](). For CI, race detection and coverage reporting are enabled [Makefile:49-51]().

```bash
make test-ci
```

### Smoke Tests
A dedicated shell script `scripts/smoke_test.sh` performs end-to-end verification of the sandbox's security boundaries [CLAUDE.md:19-19](). It requires the `GREYWALL_TEST_NETWORK=1` environment variable to verify proxy functionality [CLAUDE.md:19-19]().

### Logic Flow: Test to Binary Association

```mermaid
graph LR
    TEST["make test-ci"] -->|"Executes"| UNIT["Unit Tests (*_test.go)"]
    TEST -->|"Executes"| INTG["Integration Tests"]
    SMOKE["scripts/smoke_test.sh"] -->|"Wraps"| BIN["./greywall"]
    
    subgraph "Code Entities Tested"
        UNIT -->|"Validates"| CFG["internal/config"]
        UNIT -->|"Validates"| PLAT["internal/platform"]
        INTG -->|"Invokes"| MGR["internal/sandbox/manager.go"]
        SMOKE -->|"Tests"| LNX["internal/sandbox/linux.go"]
        SMOKE -->|"Tests"| MAC["internal/sandbox/macos.go"]
    end
```

**Testing Scope and Code Association**

Sources: [Makefile:45-51](), [CLAUDE.md:14-20](), [CLAUDE.md:33-45]()

## Git Hooks
To ensure quality before code reaches CI, `greywall` uses a pre-commit hook [scripts/pre-commit:1-3](). This hook runs `gofumpt` check and `golangci-lint` [scripts/pre-commit:21-30](). It can be installed using:

```bash
make install-hooks
```

Sources: [Makefile:80-84](), [scripts/pre-commit:1-32]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/main.yml](.github/workflows/main.yml)
- [docs/testing.md](docs/testing.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [scripts/smoke_test.sh](scripts/smoke_test.sh)

</details>



This document describes greywall's continuous integration and deployment pipeline implemented using GitHub Actions. The pipeline ensures code quality through automated building, linting, and multi-platform testing on every push and pull request. For information about the release process and distribution, see [8.3 Release Process]().

**Sources:** [.github/workflows/main.yml:1-171]()

---

## Workflow Structure

The CI/CD pipeline is defined in `.github/workflows/main.yml` and consists of four parallel jobs that validate code quality, build correctness, and platform compatibility.

### Pipeline Jobs Overview

```mermaid
graph TB
    Trigger["Push to main<br/>or Pull Request"]
    
    Build["build job<br/>ubuntu-latest"]
    Lint["lint job<br/>ubuntu-latest"]
    TestLinux["test-linux job<br/>ubuntu-latest"]
    TestMacOS["test-macos job<br/>ubuntu-latest"]
    
    Trigger --> Build
    Trigger --> Lint
    Trigger --> TestLinux
    Trigger --> TestMacOS
    
    Build --> BuildSteps["• Checkout code<br/>• Setup Go from go.mod<br/>• Download dependencies<br/>• make build-ci"]
    
    Lint --> LintSteps["• Checkout code<br/>• Setup Go from go.mod<br/>• Download dependencies<br/>• make download-tun2socks<br/>• make lint"]
    
    TestLinux --> LinuxSteps["• Setup Go/Python/Node<br/>• Install bubblewrap, socat<br/>• Configure user namespaces<br/>• make download-tun2socks<br/>• make test-ci<br/>• smoke_test.sh"]
    
    TestMacOS --> MacOSSteps["• Setup Go/Python/Node<br/>• Install ripgrep, coreutils<br/>• Verify sandbox-exec<br/>• make test-ci<br/>• smoke_test.sh"]
```

**Sources:** [.github/workflows/main.yml:1-133](), [.github/workflows/main.yml:134-177]()

---

## Trigger Configuration

The workflow triggers on:

| Event | Branches | Purpose |
|-------|----------|---------|
| `push` | `main` | Validate commits to main branch |
| `pull_request` | `main` | Validate PRs before merging |

The workflow runs with `contents: read` permissions for security.

**Sources:** [.github/workflows/main.yml:3-10]()

---

## Build Job

The build job verifies that the codebase compiles successfully on Linux.

```mermaid
flowchart LR
    Checkout["actions/checkout@v4"]
    SetupGo["actions/setup-go@v5<br/>go-version-file: go.mod<br/>cache: true"]
    Download["go mod download"]
    Build["make build-ci"]
    
    Checkout --> SetupGo
    SetupGo --> Download
    Download --> Build
```

### Build Steps

1. **Checkout**: Uses `actions/checkout@v4` to fetch the repository [[.github/workflows/main.yml:17-18]]().
2. **Go Setup**: Uses `actions/setup-go@v5` with Go version from `go.mod` and enabled build cache [[.github/workflows/main.yml:20-24]]().
3. **Dependencies**: Downloads Go modules with `go mod download` [[.github/workflows/main.yml:26-27]]().
4. **Build**: Executes `make build-ci` to compile the binary [[.github/workflows/main.yml:29-30]]().

The `build-ci` Make target compiles the greywall binary for the CI environment.

**Sources:** [.github/workflows/main.yml:13-31]()

---

## Lint Job

The lint job enforces code quality standards and formatting.

### Lint Steps

1. **Environment Setup**: Configures Go and downloads dependencies [[.github/workflows/main.yml:39-46]]().
2. **Asset Preparation**: Runs `make download-tun2socks` to ensure embedded assets are available for the linter [[.github/workflows/main.yml:48-49]]().
3. **Tool Installation**: Executes `make install-lint-tools` [[.github/workflows/main.yml:51-52]]().
4. **Validation**: Checks formatting via `make fmt-check` and runs the main linter via `make lint` [[.github/workflows/main.yml:54-58]]().

**Sources:** [.github/workflows/main.yml:32-59]()

---

## Test Jobs

Greywall runs comprehensive tests on both Linux and macOS to ensure cross-platform compatibility. Each platform has unique sandbox dependencies that must be installed and verified.

### Linux Test Job

The Linux test job validates greywall's primary platform with full sandbox feature support.

#### Linux Test Flow

```mermaid
flowchart TD
    Checkout["Checkout code"]
    SetupRuntime["Setup runtimes<br/>• Go from go.mod<br/>• Python 3.12<br/>• Node 20"]
    InstallDeps["Install sandbox dependencies<br/>• bubblewrap<br/>• socat<br/>• uidmap<br/>• curl<br/>• netcat-openbsd<br/>• ripgrep"]
    ConfigureNamespaces["Configure user namespaces<br/>• Add subuid/subgid entries<br/>• Disable AppArmor restriction"]
    VerifyDeps["Verify dependencies<br/>• bwrap --version<br/>• socat -V<br/>• Test basic bwrap<br/>• Test user namespace"]
    DownloadT2S["make download-tun2socks"]
    RunTests["make test-ci"]
    BuildBinary["make build-ci"]
    SmokeTests["./scripts/smoke_test.sh"]
    
    Checkout --> SetupRuntime
    SetupRuntime --> InstallDeps
    InstallDeps --> ConfigureNamespaces
    ConfigureNamespaces --> VerifyDeps
    VerifyDeps --> DownloadT2S
    DownloadT2S --> RunTests
    RunTests --> BuildBinary
    BuildBinary --> SmokeTests
```

#### Linux Dependency Installation

The test job installs Linux-specific sandbox dependencies via `apt-get` [[.github/workflows/main.yml:86-97]](). These include `bubblewrap` for namespaces, `socat` for proxy bridges, and `uidmap` for unprivileged user namespace support.

#### User Namespace Configuration

Ubuntu 24.04 requires special configuration for unprivileged user namespaces [[.github/workflows/main.yml:98-104]]():

1. **subuid/subgid setup**: Configures the runner user to allow mapping of UIDs/GIDs [[.github/workflows/main.yml:99-100]]().
2. **AppArmor restriction**: Disables the `kernel.apparmor_restrict_unprivileged_userns` restriction so `bwrap` can create namespaces without setuid [[.github/workflows/main.yml:104]](). This is critical for `greywall` to use `CAP_NET_ADMIN` for transparent proxying [[.github/workflows/main.yml:103]]().

#### Dependency Verification

The workflow includes extensive verification steps to diagnose sandbox issues [[.github/workflows/main.yml:106-120]]():
- Checks `bwrap` version and permissions.
- Verifies `socat` availability.
- Confirms kernel support for user namespaces.
- Executes basic `bwrap` commands to ensure the environment is capable of creating read-only binds and user namespaces [[.github/workflows/main.yml:116-119]]().

#### Linux Test Execution

After setup, the job runs:
1. **Unit and integration tests**: `make test-ci` [[.github/workflows/main.yml:124-125]]().
2. **Binary build**: `make build-ci` [[.github/workflows/main.yml:127-128]]().
3. **Smoke tests**: Executes `scripts/smoke_test.sh` with `GREYWALL_TEST_NETWORK=1` to verify the compiled binary end-to-end [[.github/workflows/main.yml:130-131]]().

**Sources:** [.github/workflows/main.yml:60-132](), [scripts/smoke_test.sh:1-131]()

---

### macOS Test Job

The macOS test job validates greywall's implementation using `sandbox-exec` and Seatbelt profiles.

#### macOS Dependencies

macOS has built-in `sandbox-exec`, so only utility packages like `ripgrep` and `coreutils` are installed via Homebrew [[.github/workflows/main.yml:159-161]]().

#### macOS Verification

The workflow verifies that `sandbox-exec` is functional by running a simple test profile:
```bash
sandbox-exec -p '(version 1)(allow default)' /bin/echo "sandbox-exec works"
```
**Sources:** [.github/workflows/main.yml:163-168]()

#### macOS Test Execution

Like Linux, macOS runs:
1. **Unit and integration tests**: `make test-ci` [[.github/workflows/main.yml:169-170]]().
2. **Binary build**: `make build-ci` [[.github/workflows/main.yml:172-173]]().
3. **Smoke tests**: `GREYWALL_TEST_NETWORK=1 ./scripts/smoke_test.sh ./greywall` [[.github/workflows/main.yml:175-176]]().

**Sources:** [.github/workflows/main.yml:133-177]()

---

## Smoke Test Suite

The `scripts/smoke_test.sh` script is the final quality gate, verifying the compiled binary behaves correctly in a real environment.

### Test Categories

| Category | Tests Performed | Code Entity |
|----------|-----------------|-------------|
| **Basic** | Version flag, echo, ls, pwd | `cmd/greywall` |
| **Filesystem** | Read/write restrictions, workspace isolation | `internal/sandbox` |
| **Command** | Deny-list blocking (e.g., `rm -rf`), chained commands | `internal/sandbox` |
| **Network** | Blocking by default, curl verification | `internal/proxy` |
| **Tools** | Compatibility with `python3`, `node`, `git` | Profile System |

The script uses a temporary workspace [[scripts/smoke_test.sh:46]]() and generates dynamic `greywall.json` configuration files to test specific restriction scenarios [[scripts/smoke_test.sh:124-131]]().

**Sources:** [scripts/smoke_test.sh:98-235]()

---

## Quality Gates

The pipeline enforces several quality gates before code can merge:

```mermaid
graph LR
    PR["Pull Request"]
    
    BuildPass["Build job passes"]
    LintPass["Lint job passes"]
    LinuxPass["test-linux passes"]
    MacOSPass["test-macos passes"]
    
    Merge["Merge to main"]
    
    PR --> BuildPass
    PR --> LintPass
    PR --> LinuxPass
    PR --> MacOSPass
    
    BuildPass --> Merge
    LintPass --> Merge
    LinuxPass --> Merge
    MacOSPass --> Merge
```

All four jobs must pass before a pull request can merge. This ensures:
1. **Code compiles** on standard Linux runners [[.github/workflows/main.yml:13-31]]().
2. **Code quality** meets standards (formatting and linting) [[.github/workflows/main.yml:32-59]]().
3. **Tests pass** on Linux with full namespace and capability support [[.github/workflows/main.yml:60-132]]().
4. **Tests pass** on macOS with Seatbelt sandboxing [[.github/workflows/main.yml:133-177]]().

---

## Troubleshooting CI Failures

Common CI failures and their causes:

| Failure Message | Cause | Resolution |
|-----------------|-------|------------|
| `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` | Missing `CAP_NET_ADMIN` or AppArmor restriction | Verify `sysctl` and `subuid` setup [[docs/troubleshooting.md:22-28]]() |
| `bwrap: setting up uid map: Permission denied` | Missing `uidmap` or `/etc/subuid` config | Ensure `uidmap` package is installed [[docs/troubleshooting.md:72-78]]() |
| `Sandbox: sandbox-exec(...) deny(1) forbidden-sandbox-reinit` | Attempting nested sandboxing on macOS | Avoid running greywall inside existing macOS sandboxes [[docs/troubleshooting.md:12-18]]() |

**Sources:** [docs/troubleshooting.md:8-97]()

---

# Page: Release Process

# Release Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/notify-docs.yml](.github/workflows/notify-docs.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yaml](.goreleaser.yaml)
- [internal/proxy/brew.go](internal/proxy/brew.go)
- [scripts/bump_version.sh](scripts/bump_version.sh)
- [scripts/release.sh](scripts/release.sh)
- [scripts/release_test.bats](scripts/release_test.bats)

</details>



This page documents how greywall releases are created, built, and distributed. It covers the automated release pipeline using `goreleaser`, multi-platform binary builds, versioning logic, and distribution through GitHub Releases and Homebrew.

## Release Trigger and Automation

Releases are managed through a combination of local scripts for versioning and GitHub Actions for CI/CD. The primary automation is triggered by pushing git tags matching the pattern `v*` (e.g., `v0.1.0`).

### Release Script Logic

The `scripts/release.sh` script automates the pre-release checks and tagging process. It ensures the environment is clean and the codebase is ready for a new version.

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant RS as "scripts/release.sh"
    participant BV as "scripts/bump_version.sh"
    participant Git as "Git CLI"
    participant GHA as "GitHub Actions"

    Dev->>RS: "./scripts/release.sh [patch|minor|beta]"
    RS->>Git: "Check branch (main) & status"
    RS->>Git: "Run 'make test-ci' & 'make lint'"
    RS->>BV: "bump_version(last_tag, type)"
    BV-->>RS: "New Version (e.g., v0.1.1)"
    RS->>Dev: "Confirm release?"
    Dev->>RS: "y"
    RS->>Git: "git tag -a v0.1.1"
    RS->>Git: "git push origin v0.1.1"
    Git->>GHA: "Trigger goreleaser workflow"
```

**Sources:** [scripts/release.sh:1-132](), [scripts/bump_version.sh:1-78]()

### Preflight Checks
Before a tag is created, `scripts/release.sh` performs several mandatory checks:
- **Branch Validation**: Ensures the user is on the `main` branch [scripts/release.sh:38-42]().
- **Worktree Status**: Verifies there are no uncommitted changes [scripts/release.sh:45-47]().
- **Sync Status**: Confirms the local branch is up to date with `origin/main` [scripts/release.sh:61-65]().
- **Quality Gates**: Executes `make test-ci` and `make lint` to ensure code quality [scripts/release.sh:78-87]().

### Version Bumping Logic
The `bump_version` function in `scripts/bump_version.sh` calculates the next semantic version:
- **Patch**: Increments the third digit (e.g., `v0.1.0` -> `v0.1.1`) [scripts/bump_version.sh:70]().
- **Minor**: Increments the second digit and resets patch to zero [scripts/bump_version.sh:71]().
- **Beta**: Calculates the next beta based on the latest stable tag (e.g., `v0.1.0` -> `v0.1.1-beta.1`) [scripts/bump_version.sh:35-57]().

---

## goreleaser Pipeline

Once a tag is pushed, the `.github/workflows/release.yml` workflow invokes `goreleaser`.

### Build Configuration
The build matrix in `.goreleaser.yaml` targets Linux and macOS (Darwin) for both `amd64` and `arm64` architectures [/.goreleaser.yaml:7-15]().

- **Linker Flags**: Injects versioning metadata into the binary [/.goreleaser.yaml:16-20]().
- **Static Linking**: `CGO_ENABLED=0` ensures the binary is portable across different glibc versions [/.goreleaser.yaml:9]().
- **Compression**: Linux binaries are compressed using UPX with `lzma` and `brute` settings to minimize download size [/.goreleaser.yaml:24-30]().

### Archive and Artifacts
The pipeline produces `.tar.gz` archives containing the `greywall` binary and essential documentation [/.goreleaser.yaml:32-46](). A `checksums.txt` is generated for security verification [/.goreleaser.yaml:48-49]().

### Changelog Generation
Changelogs are automatically generated and grouped based on commit message prefixes:
- **New Features**: `feat:`
- **Security updates**: `sec:`
- **Bug fixes**: `fix:` or `refactor:`
- **Documentation**: `docs:`

**Sources:** [/.goreleaser.yaml:71-85]()

---

## Distribution and Homebrew

greywall is distributed via GitHub Releases and the official Homebrew tap.

### Homebrew Tap Integration
The release process automatically updates the `GreyhavenHQ/homebrew-tap` repository [/.goreleaser.yaml:87-91]().

| Feature | Implementation |
| :--- | :--- |
| **Dependencies** | Declares `greyproxy` as a required cask [/.goreleaser.yaml:104-105](). |
| **Quarantine** | A `post_install` hook removes the `com.apple.quarantine` attribute on macOS [/.goreleaser.yaml:98-103](). |
| **Binary Mapping** | Symlinks the `greywall` binary into the user's PATH [/.goreleaser.yaml:96-97](). |

### greyproxy Synchronization
When a new release is published, a separate workflow `Notify docs repo` triggers a repository dispatch to sync documentation and potentially update downstream dependencies [/.github/workflows/notify-docs.yml:1-21]().

### Homebrew Management Detection
The codebase includes logic to detect if the running environment is managed by Homebrew, which influences how updates are handled.

```go
func IsBrewManaged(binaryPath string) bool {
    // ...
    brewPrefix := brewPrefixPath() // Calls 'brew --prefix'
    return strings.HasPrefix(binaryPath, brewPrefix)
}
```

**Sources:** [internal/proxy/brew.go:8-21]()

---

## Post-Release Notifications
The system dispatches a `sync-docs` event to the `GreyhavenHQ/docs` repository upon release publication. This payload includes the product name and the release tag, allowing the documentation site to update its version-specific content automatically [/.github/workflows/notify-docs.yml:11-20]().

---

# Page: Reference

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)
- [docs/security-model.md](docs/security-model.md)

</details>



This section provides essential reference material for the greywall project, including licensing terms and security policies. These documents establish the legal framework for using and contributing to greywall, as well as procedures for responsibly reporting security vulnerabilities.

For technical documentation about greywall's implementation, see pages [1]() through [8](). For specific security model documentation explaining greywall's protection mechanisms, see [3.3 Security Model]().

## Overview

The reference materials consist of two primary documents:

| Document | Purpose | Location |
|----------|---------|----------|
| Security Policy | Vulnerability reporting procedures and disclosure timeline | [Security Policy](#9.1) |
| License | Apache License 2.0 terms and copyright information | [License](#9.2) |

These documents are maintained in the repository root as `SECURITY.md` and `LICENSE` respectively, ensuring they are visible to all contributors and users.

## Security Vulnerability Reporting

The greywall project follows a responsible disclosure process for security vulnerabilities. This process balances the need to fix security issues promptly with giving users time to upgrade before public disclosure.

### Security Reporting Workflow

```mermaid
sequenceDiagram
    participant Reporter as "Vulnerability Reporter"
    participant Email as "support@greyhaven.co"
    participant Team as "Greywall Security Team"
    participant Users as "Greywall Users"
    participant Public as "Public Disclosure"
    
    Reporter->>Email: "Email vulnerability details"
    Email->>Team: "Forward to security team"
    Team->>Team: "Assess and validate issue"
    Team->>Team: "Develop and test fix"
    Team->>Users: "Release patched version"
    Note over Team,Users: "Users have time to upgrade"
    Team->>Public: "Public disclosure after 90 days"
    Note over Public: "Full details published"
```

**Sources:** [SECURITY.md:1-9]()

The security policy requires the following information when reporting vulnerabilities:

| Required Information | Purpose |
|---------------------|---------|
| Description of the issue | Understanding the vulnerability |
| Steps to reproduce | Validation and testing |
| Affected versions | Scope determination |
| Known mitigations | Immediate workarounds |

The 90-day disclosure timeline gives users sufficient time to upgrade after a patch is released, while ensuring vulnerabilities do not remain secret indefinitely.

### Policy Scope

The security policy applies specifically to the latest version on the `main` branch. This focuses security efforts on the current codebase rather than maintaining historical versions.

```mermaid
graph LR
    Main["main branch<br/>(latest version)"]
    Historic["Historical versions<br/>(previous releases)"]
    Policy["Security Policy<br/>SECURITY.md"]
    
    Main --> Policy
    Historic -.not covered.-> Policy
    
    Policy --> Email["support@greyhaven.co"]
    Policy --> Timeline["90-day disclosure"]
```

**Sources:** [SECURITY.md:7-8]()

## Licensing Structure

Greywall is licensed under the Apache License 2.0, a permissive open-source license that allows commercial use, modification, and distribution while providing patent protection.

### Copyright Holders

The project has multiple copyright holders representing its development history:

```mermaid
graph TB
    License["Apache License 2.0<br/>LICENSE file"]
    
    License --> Tusk["Tusk AI, Inc<br/>Copyright 2025"]
    License --> Greywall["The Greywall Authors<br/>Copyright 2026"]
    
    Tusk -.original development.-> Code["greywall codebase"]
    Greywall -.ongoing development.-> Code
```

**Sources:** [LICENSE:189-190]()

| Copyright Holder | Year | Role |
|-----------------|------|------|
| Tusk AI, Inc | 2025 | Original development organization |
| The Greywall Authors | 2026 | Ongoing contributor collective |

This dual copyright structure reflects greywall's transition from an initial development organization to a broader contributor base.

### License Key Terms

The Apache License 2.0 provides the following key permissions and requirements:

| Aspect | Terms |
|--------|-------|
| **Permissions** | Commercial use, modification, distribution, patent use, private use |
| **Conditions** | License and copyright notice, state changes |
| **Limitations** | No trademark use, no liability, no warranty |
| **Patent Grant** | Perpetual, worldwide, royalty-free patent license |
| **Patent Termination** | License terminates if you sue for patent infringement |

**Sources:** [LICENSE:1-176]()

### License Application in Codebase

Every source file in the greywall codebase should include the Apache License boilerplate notice:

```
Copyright 2025 Tusk AI, Inc
Copyright 2026 The Greywall Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

**Sources:** [LICENSE:178-196]()

## Reference Materials Relationship to Project Structure

The reference materials integrate with greywall's development and distribution infrastructure:

```mermaid
graph TB
    subgraph "Repository Root Files"
        License["LICENSE<br/>Apache 2.0 terms"]
        Security["SECURITY.md<br/>Reporting procedures"]
    end
    
    subgraph "Source Code"
        Cmd["cmd/greywall/<br/>CLI implementation"]
        Pkg["pkg/greywall/<br/>Library API"]
        Internal["internal/<br/>Platform implementations"]
    end
    
    subgraph "Distribution"
        GitHub["GitHub Releases<br/>Binary downloads"]
        Homebrew["Homebrew Tap<br/>Package distribution"]
        Docs["Documentation<br/>Wiki pages"]
    end
    
    License --> Cmd
    License --> Pkg
    License --> Internal
    
    License --> GitHub
    License --> Homebrew
    
    Security --> Docs
    Security --> GitHub
    
    GitHub -.includes.-> License
    GitHub -.includes.-> Security
```

**Sources:** [LICENSE:1-203](), [SECURITY.md:1-10]()

The `LICENSE` file is automatically included in:
- GitHub release archives generated by `goreleaser` (see [8.3 Release Process]())
- Homebrew cask installations
- Distribution via `install.sh` script (see [2.1 Installation]())

The `SECURITY.md` file is prominently displayed on the GitHub repository, providing immediate visibility to security researchers and users.

## Key Contacts and Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Security Contact | support@greyhaven.co | Vulnerability reporting |
| License Full Text | `LICENSE` in repository root | Legal terms reference |
| Security Policy | `SECURITY.md` in repository root | Reporting procedures |
| GitHub Repository | github.com/GreyhavenHQ/greywall | Source code and issues |

**Sources:** [SECURITY.md:5](), [LICENSE:1]()

For detailed information about each reference document, see the corresponding child pages:
- [Security Policy](#9.1) — How to report security vulnerabilities, disclosure timeline, and security contacts
- [License](#9.2) — Apache License 2.0 terms and conditions

---

# Page: Security Policy

# Security Policy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



This page documents greywall's security vulnerability reporting process and responsible disclosure policy. It outlines how to report security issues, the expected disclosure timeline, and which versions are covered by security support.

For information about greywall's security model and threat protection capabilities, see [Security Model](#3.3).

## Vulnerability Reporting Process

greywall follows a coordinated disclosure process for security vulnerabilities. The project maintains a formal security policy in `SECURITY.md` that defines the reporting procedures and expectations.

### Contact Information

Security issues should be reported via email to:

**Email**: support@greyhaven.co

Public disclosure (e.g., GitHub issues) should be avoided until the issue has been addressed according to the disclosure timeline.

### Required Information

When reporting a security vulnerability, include the following information in your report:

| Information Category | Description |
|---------------------|-------------|
| **Issue Description** | Clear explanation of the security vulnerability |
| **Reproduction Steps** | Detailed steps to reproduce the issue |
| **Affected Versions** | Which greywall versions are impacted |
| **Mitigations** | Known workarounds or mitigations (if any) |

Sources: [SECURITY.md:3-5]()

### Vulnerability Reporting Workflow

```mermaid
flowchart TD
    Reporter["Security Researcher / User"]
    Email["support@greyhaven.co"]
    SecurityMd["SECURITY.md"]
    Team["Greywall Maintainers"]
    Triage["Vulnerability Triage"]
    Fix["Develop Fix"]
    Timeline["90-Day Disclosure Timeline"]
    Disclosure["Coordinated Public Disclosure"]
    Release["Security Release"]
    
    Reporter -->|"1. Discover vulnerability"| SecurityMd
    SecurityMd -->|"2. Follow reporting guidelines"| Email
    Email -->|"3. Report received"| Team
    Team -->|"4. Acknowledge report"| Triage
    Triage -->|"5. Validate and assess"| Fix
    Fix -->|"6. Implement patch"| Timeline
    Timeline -->|"7. Within 90 days"| Release
    Release -->|"8. Public disclosure"| Disclosure
    Disclosure -->|"9. Security advisory"| Reporter
```

**Vulnerability Reporting Workflow Diagram**

This diagram shows the complete lifecycle from vulnerability discovery to public disclosure. The process begins when a security researcher discovers an issue and consults the `SECURITY.md` policy document, which directs them to report via email to `support@greyhaven.co`.

Sources: [SECURITY.md:1-10]()

## Disclosure Timeline

greywall follows a **90-day disclosure timeline** as specified in `SECURITY.md`. This means:

1. **Day 0**: Vulnerability report received.
2. **Day 1-7**: Initial triage and acknowledgment.
3. **Day 7-60**: Fix development and testing.
4. **Day 60-80**: Release preparation and validation.
5. **Day 80-90**: Coordinated disclosure and security release.
6. **Day 90+**: Public disclosure if not already released.

The 90-day timeline balances the need for timely fixes with the complexity of developing, testing, and releasing security patches across multiple platforms (Linux and macOS).

Sources: [SECURITY.md:5]()

## Security Support Scope

### Covered Versions

The security policy applies to:

- **Latest main branch**: The most recent commit on the main branch is always covered.
- **Latest release**: The most recently tagged release version.

As stated in `SECURITY.md`, "This security policy applies to the latest version of our main branch."

Sources: [SECURITY.md:7]()

### Version Support Matrix

```mermaid
flowchart TB
    subgraph "Supported_Versions"
        MainBranch["main branch (Latest commit)"]
        LatestRelease["Latest Tagged Release"]
    end
    
    subgraph "Not_Covered"
        OldReleases["Older Releases"]
        Forks["Third-party Forks"]
        DevBranches["Feature Branches"]
    end
    
    SecurityPolicy["SECURITY.md Policy Document"]
    
    SecurityPolicy -->|"Applies to"| MainBranch
    SecurityPolicy -->|"Applies to"| LatestRelease
    SecurityPolicy -.->|"Does not apply"| OldReleases
    SecurityPolicy -.->|"Does not apply"| Forks
    SecurityPolicy -.->|"Does not apply"| DevBranches
```

**Security Support Scope Diagram**

This diagram illustrates which versions and branches receive security support. Only the latest main branch and the most recent release are covered by the security policy.

Sources: [SECURITY.md:7]()

## Responsible Disclosure Philosophy

The greywall project prioritizes the security of its users. The coordinated disclosure process ensures:

1. **User Protection**: Vulnerabilities are fixed before public disclosure.
2. **Researcher Recognition**: Security researchers receive acknowledgment for responsible reporting.
3. **Transparency**: Public disclosure follows fixes to inform all users.
4. **Reasonable Timeline**: 90 days balances urgency with fix quality.

As stated in `SECURITY.md`, "Thank you for helping to keep our project and our users secure!"

Sources: [SECURITY.md:9]()

## License and Legal Framework

greywall is licensed under the **Apache License 2.0**. The license includes important disclaimers regarding liability and warranty:

- **No Warranty**: The software is provided "AS IS" without warranties of any kind [LICENSE:143-151]().
- **Limitation of Liability**: Contributors are not liable for any damages arising out of the use or inability to use the Work [LICENSE:153-163]().
- **Contributions**: Any Contribution intentionally submitted for inclusion in the Work shall be under the terms and conditions of the license [LICENSE:130-136]().

For complete license terms, see [License](#9.2).

Sources: [LICENSE:1-203]()

## Related Documentation

For information about greywall's security features and threat model, see:

- [Security Model](#3.3) - Defense-in-depth approach and threat protection
- [Linux Sandboxing](#4.1) - Platform-specific security implementations
- [macOS Sandboxing](#4.2) - macOS security mechanisms
- [Network Isolation](#3.1) - Network security architecture
- [Filesystem Isolation](#3.2) - Filesystem access controls

---

# Page: License

# License

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



This document describes the licensing terms for the greywall project, including copyright holders, permissions granted, and obligations for users and redistributors. For information about reporting security vulnerabilities, see [Security Policy](#9.1).

---

## License Overview

Greywall is released under the **Apache License, Version 2.0** (January 2004). This is a permissive open-source license that allows commercial use, modification, distribution, and private use, while requiring preservation of copyright and license notices.

The full license text is available at [LICENSE:1-203]() in the repository root.

**Sources:** [LICENSE:1-203]()

---

## Copyright Holders

The greywall project maintains the following copyright notices:

| Copyright Holder | Year | Context |
|-----------------|------|---------|
| Tusk AI, Inc | 2025 | Original copyright holder |
| The Greywall Authors | 2025 | Ongoing project copyright |

These copyright notices appear in [LICENSE:189-190]() and must be preserved in all copies and derivative works.

**Sources:** [LICENSE:189-190]()

---

## Key Permissions

### Rights Granted

The Apache License 2.0 grants users and contributors the following rights:

| Permission | Scope | Reference |
|-----------|-------|-----------|
| **Copyright License** | Reproduce, prepare derivative works, publicly display/perform, sublicense, and distribute | [LICENSE:66-71]() |
| **Patent License** | Make, use, sell, and import the work under contributor patent claims | [LICENSE:73-87]() |
| **Commercial Use** | Use in commercial products and services without fees | [LICENSE:66-71]() |
| **Modification** | Create and distribute modified versions | [LICENSE:66-71]() |
| **Private Use** | Use internally without distribution | [LICENSE:66-71]() |

### License Scope Diagram

```mermaid
graph TB
    subgraph "Greywall_Project_Entities"
        SOURCE["Source Code<br/>(.go, .c, .h)"]
        BINARY["Compiled Binaries<br/>(greywall, greyproxy)"]
        DOCS["Documentation<br/>(README.md, wiki)"]
        CONFIG["Configuration Files<br/>(greywall.json)"]
    end
    
    subgraph "Apache_2.0_Grants"
        COPYRIGHT["Copyright License<br/>LICENSE:66-71"]
        PATENT["Patent License<br/>LICENSE:73-87"]
    end
    
    subgraph "Permitted_Actions"
        COMMERCIAL["Commercial Use"]
        MODIFY["Modification"]
        DISTRIBUTE["Distribution"]
        PRIVATE["Private Use"]
        SUBLICENSE["Sublicensing"]
    end
    
    SOURCE --> COPYRIGHT
    BINARY --> COPYRIGHT
    DOCS --> COPYRIGHT
    CONFIG --> COPYRIGHT
    
    COPYRIGHT --> PATENT
    
    COPYRIGHT --> COMMERCIAL
    COPYRIGHT --> MODIFY
    COPYRIGHT --> DISTRIBUTE
    COPYRIGHT --> PRIVATE
    COPYRIGHT --> SUBLICENSE
    
    PATENT --> COMMERCIAL
    PATENT --> DISTRIBUTE
```

**Sources:** [LICENSE:66-87]()

---

## Redistribution Requirements

When redistributing greywall or derivative works, you must comply with the following requirements:

### Mandatory Inclusions

| Requirement | Description | Reference |
|------------|-------------|-----------|
| **License Copy** | Include a copy of the Apache License 2.0 | [LICENSE:94-95]() |
| **Modified File Notices** | Mark modified files with prominent change notices | [LICENSE:97-98]() |
| **Copyright Notices** | Retain all copyright, patent, trademark, and attribution notices | [LICENSE:100-104]() |
| **NOTICE File** | If present, include readable copy in derivative works | [LICENSE:106-121]() |

### Redistribution Flow Diagram

```mermaid
graph TB
    subgraph "Source_Repository"
        REPO["greywall Repo<br/>github.com/GreyhavenHQ/greywall"]
        LICENSE_FILE["LICENSE file<br/>LICENSE:1-203"]
        SOURCES["Source files with<br/>copyright headers"]
    end
    
    subgraph "Distribution_Artifacts"
        GHRELEASE["GitHub Releases<br/>(goreleaser artifacts)"]
        HOMEBREW["Homebrew Formula<br/>(Formula/greywall.rb)"]
        INSTALLSH["install.sh script<br/>(curl-pipe-bash)"]
    end
    
    subgraph "Legal_Compliance"
        COPY_LICENSE["Copy of LICENSE"]
        COPY_NOTICES["Copyright notices"]
        CHANGE_NOTICE["Modification notices<br/>(if changed)"]
    end
    
    subgraph "Target_Environment"
        USER_BIN["/usr/local/bin/greywall"]
        USER_FILES["Installation directory<br/>includes LICENSE"]
    end
    
    REPO --> GHRELEASE
    REPO --> HOMEBREW
    REPO --> INSTALLSH
    
    LICENSE_FILE --> COPY_LICENSE
    SOURCES --> COPY_NOTICES
    
    COPY_LICENSE --> GHRELEASE
    COPY_LICENSE --> HOMEBREW
    COPY_NOTICES --> GHRELEASE
    COPY_NOTICES --> HOMEBREW
    
    GHRELEASE --> USER_BIN
    HOMEBREW --> USER_BIN
    INSTALLSH --> GHRELEASE
    
    GHRELEASE --> USER_FILES
    HOMEBREW --> USER_FILES
```

**Sources:** [LICENSE:89-128]()

---

## Patent Grant and Termination

### Patent License Terms

The Apache License includes an explicit patent grant [LICENSE:73-87]():

- **Grant:** Contributors grant you a perpetual, royalty-free patent license for claims covered by their contributions.
- **Scope:** Applies to patent claims necessarily infringed by the contribution alone or in combination with the work.
- **Termination:** Patent license terminates if you initiate patent litigation alleging the work infringes your patents.

### Patent Litigation Termination Clause

If you file a lawsuit alleging that greywall or any contribution incorporated within the work constitutes direct or contributory patent infringement, then any patent licenses granted to you under this license for that work shall terminate as of the date such litigation is filed [LICENSE:82-87]().

**Sources:** [LICENSE:73-87]()

---

## Contribution Terms

### Default Contribution License

Unless explicitly stated otherwise, any contribution submitted to greywall for inclusion in the work by you to the licensor shall be under the terms and conditions of this license, without any additional terms or conditions [LICENSE:130-136]().

### Submission Channels

Contributions are typically accepted through:

- GitHub pull requests to the main branch.
- Issue reports and feature requests.
- Security vulnerability reports to [support@greyhaven.co](mailto:support@greyhaven.co) as per [SECURITY.md:5-5]().

**Sources:** [LICENSE:130-136](), [SECURITY.md:1-10]()

---

## Disclaimer and Limitation of Liability

### No Warranty

The Apache License provides software "AS IS" without warranties [LICENSE:143-151]():

| Disclaimer Type | Description |
|----------------|-------------|
| **Express Warranties** | No guarantees of fitness, merchantability, or non-infringement |
| **Implied Warranties** | No implied warranties of any kind |
| **Title** | No warranty of clear title |

### Limitation of Liability

Contributors have no liability for damages [LICENSE:153-163]():

- **No Liability:** Contributors are not liable for any damages (direct, indirect, special, incidental, consequential).
- **Types Covered:** Loss of goodwill, work stoppage, computer failure, or commercial damages.
- **Scope:** Applies even if the contributor was advised of potential damages.

**Sources:** [LICENSE:143-163]()

---

## Trademark Restrictions

The Apache License does **not** grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file [LICENSE:138-141]().

**Sources:** [LICENSE:138-141]()

---

## Full License Reference

| Section | Lines | Content |
|---------|-------|---------|
| Definitions | [LICENSE:7-64]() | Legal definitions of terms |
| Copyright Grant | [LICENSE:66-71]() | Rights to reproduce and modify |
| Patent Grant | [LICENSE:73-87]() | Patent license and termination |
| Redistribution | [LICENSE:89-128]() | Requirements for sharing the code |
| Contributions | [LICENSE:130-136]() | Terms for submitted code |
| Trademarks | [LICENSE:138-141]() | Restriction on brand usage |
| Disclaimer | [LICENSE:143-151]() | No warranty clause |
| Liability | [LICENSE:153-163]() | Limitation of liability |
| Additional Liability | [LICENSE:165-174]() | Optional support/warranty terms |

**Sources:** [LICENSE:1-203]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yaml](.goreleaser.yaml)
- [README.md](README.md)
- [install.sh](install.sh)
- [internal/config/config.go](internal/config/config.go)
- [internal/profiles/keyring.go](internal/profiles/keyring.go)
- [internal/profiles/profiles_test.go](internal/profiles/profiles_test.go)
- [internal/profiles/prompt.go](internal/profiles/prompt.go)
- [internal/profiles/registry.go](internal/profiles/registry.go)
- [internal/profiles/toolchains/scm.go](internal/profiles/toolchains/scm.go)
- [internal/proxy/brew.go](internal/proxy/brew.go)
- [internal/sandbox/integration_linux_test.go](internal/sandbox/integration_linux_test.go)
- [internal/sandbox/integration_macos_test.go](internal/sandbox/integration_macos_test.go)
- [internal/sandbox/integration_test.go](internal/sandbox/integration_test.go)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_ebpf.go](internal/sandbox/linux_ebpf.go)
- [internal/sandbox/linux_landlock.go](internal/sandbox/linux_landlock.go)
- [internal/sandbox/linux_seccomp.go](internal/sandbox/linux_seccomp.go)
- [internal/sandbox/macos.go](internal/sandbox/macos.go)
- [internal/sandbox/macos_test.go](internal/sandbox/macos_test.go)
- [internal/sandbox/manager.go](internal/sandbox/manager.go)
- [internal/sandbox/monitor.go](internal/sandbox/monitor.go)

</details>



This page defines codebase-specific terms, jargon, abbreviations, and domain concepts used throughout the Greywall project. It is intended for onboarding engineers to understand the underlying technologies and the specific abstractions used in the Go implementation.

## Security & Sandboxing Terms

### Deny-by-Default
The fundamental security posture of Greywall. Unless a resource (file, network destination, or syscall) is explicitly allowed in a profile or configuration, access is blocked by the kernel.
*   **Filesystem:** Controlled via `DefaultDenyRead` in `FilesystemConfig` [internal/config/config.go:75-75]().
*   **Network:** All outbound traffic is blocked unless routed through a configured proxy [internal/config/config.go:150-153]().

### Learning Mode
A permissive execution mode where Greywall traces the sandboxed process to identify required resources.
*   **Linux:** Uses `strace` to log filesystem and network syscalls [internal/sandbox/linux.go:125-126]().
*   **macOS:** Uses `eslogger` (Endpoint Security framework) to trace `open`, `create`, `write`, and `fork` events [internal/sandbox/manager.go:105-105]().
*   **Result:** Generates a least-privilege profile saved to the user's config directory [README.md:163-179]().

### Profile Drift
Occurs when a built-in agent profile (e.g., for `claude`) changes in a new Greywall release, but the user has a local override or has previously acknowledged an older version. Greywall tracks this using a `DriftAckHash` [internal/config/config.go:38-41]().

### Credential Substitution
A feature that prevents AI agents from reading sensitive environment variables (like `STRIPE_API_KEY`) from `.env` files. Greywall identifies secrets, replaces them with placeholders in a temporary file, and bind-mounts the "safe" file over the original inside the sandbox [internal/sandbox/linux.go:129-132](), [internal/sandbox/macos.go:53-53]().

---

## Platform-Specific Technologies

| Term | Platform | Description |
| :--- | :--- | :--- |
| **bubblewrap** | Linux | A low-level unprivileged sandboxing tool (`bwrap`) used to create namespaces (mount, user, network) [README.md:86-86](). |
| **Landlock** | Linux | A Linux Security Module (LSM) that allows unprivileged processes to restrict their own filesystem access [internal/sandbox/linux_landlock.go:18-21](). |
| **Seccomp** | Linux | Secure Computing mode. Used with BPF filters to restrict the system calls a process can make [internal/sandbox/linux.go:118-118](). |
| **eBPF** | Linux | Used for real-time monitoring of sandbox violations that bypass standard logging [internal/sandbox/linux.go:119-122](). |
| **Seatbelt** | macOS | The informal name for the macOS Sandbox profile language used by `sandbox-exec`. Greywall generates these `.sb` profiles dynamically [internal/sandbox/macos.go:156-160](). |
| **eslogger** | macOS | A system utility that taps into the Endpoint Security framework. Greywall uses it during Learning Mode to trace file operations [internal/sandbox/manager.go:80-83](). |

---

## Network Architecture Terms

### greyproxy
A companion service (installed via Homebrew or `greywall setup`) that acts as a deny-by-default SOCKS5/HTTP proxy. It provides a web dashboard for live traffic filtering [README.md:11-11](), [.goreleaser.yaml:105-108]().

### tun2socks
A utility embedded within Greywall that creates a TUN (network tunnel) device inside the Linux network namespace. It redirects all IP traffic to a SOCKS5 proxy, ensuring transparent proxying for tools that don't respect `HTTP_PROXY` env vars [internal/sandbox/manager.go:141-148]().

### Bridge Components
Greywall uses `socat` to bridge the isolated sandbox environment to the host machine via Unix domain sockets.

*   **ProxyBridge:** Forwards SOCKS5 traffic from a Unix socket inside the sandbox to the external `greyproxy` or other SOCKS5 server [internal/sandbox/linux.go:21-31]().
*   **DnsBridge:** Bridges DNS (UDP port 53) queries from the sandbox to a host-side DNS resolver [internal/sandbox/linux.go:33-41]().
*   **ReverseBridge:** Allows the host to connect to ports exposed inside the sandbox (e.g., a dev server) [internal/sandbox/linux.go:105-111]().
*   **ForwardBridge:** Allows the sandbox to connect to specific localhost ports on the host machine [internal/sandbox/manager.go:194-195]().
*   **DbusBridge:** Proxies filtered D-Bus messages to allow notifications (e.g., `notify-send`) [internal/sandbox/manager.go:20-20]().

### Identification Tokens
*   **SessionID:** A unique identifier for a specific sandbox execution, used to scope network rules in `greyproxy` [internal/config/config.go:51-53]().
*   **LogTag / SessionSuffix:** A random hex string appended to macOS sandbox profiles to filter unified logs for violations specific to one process [internal/sandbox/macos.go:18-27](), [internal/sandbox/monitor.go:17-22]().

---

## Implementation Diagrams

### Logic Flow: Linux Sandbox Initialization
The `Manager` class coordinates the setup of various bridges and the final execution environment.

```mermaid
graph TD
    M["Manager.Initialize()"] --> PB["NewProxyBridge()"]
    PB --> S1["socat (UNIX-LISTEN -> TCP)"]
    M --> DB["NewDnsBridge()"]
    DB --> S2["socat (UNIX-LISTEN -> UDP)"]
    M --> T2S["extractTun2Socks()"]
    
    subgraph "Execution: internal/sandbox/linux.go"
        BWRAP["exec.Command('bwrap', ...)"]
        LL["ApplyLandlockFromConfig()"]
        SC["ApplySeccomp()"]
    end
    
    M --> BWRAP
    BWRAP --> LL
    LL --> SC
```
**Sources:** [internal/sandbox/manager.go:71-137](), [internal/sandbox/linux.go:139-213](), [internal/sandbox/linux_landlock.go:21-45]()

### Data Flow: macOS Sandbox Monitoring
This diagram bridges the natural language concept of "Violation Monitoring" to the code entities that implement it.

```mermaid
graph LR
    subgraph "Code Entity Space"
        P["MacOSSandboxParams"] -- "defines" --> SS["sessionSuffix"]
        LM["LogMonitor.Start()"] -- "spawns" --> LOG["exec.Command('log stream')"]
        PV["parseViolation(line)"] -- "uses" --> RE["violationPattern"]
    end

    subgraph "Natural Language Space"
        EVENT["Kernel Sandbox Denial"] -- "Unified Log" --> STREAM["Log Stream"]
        STREAM --> LM
        PV -- "Filters" --> OUT["Stderr Output"]
    end

    SS -.->|Predicate| LOG
```
**Sources:** [internal/sandbox/macos.go:18-27](), [internal/sandbox/monitor.go:17-60](), [internal/sandbox/monitor.go:102-144]()

### Bridge Architecture (Linux)
How the isolated network namespace communicates with the outside world.

```mermaid
graph LR
    subgraph "Sandbox (Net Namespace)"
        APP["AI Agent / Tool"] -- "TCP/UDP" --> TUN["tun2socks (TUN Device)"]
        TUN -- "SOCKS5" --> US1["Unix Socket"]
    end

    subgraph "Host Space"
        US1 <--> SB["ProxyBridge (socat)"]
        SB <--> GP["greyproxy (SOCKS5:43052)"]
        GP <--> WEB["Internet"]
    end
```
**Sources:** [internal/sandbox/linux.go:21-31](), [internal/sandbox/manager.go:140-158](), [README.md:209-210]()