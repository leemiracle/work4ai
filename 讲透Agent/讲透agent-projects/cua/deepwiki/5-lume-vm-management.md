<!-- source: DeepWiki mcp.deepwiki.com · repo trycua/cua · page 5 Lume VM Management · fetched 2026-10-29 -->

# Lume VM Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/cd-swift-lume.yml](.github/workflows/cd-swift-lume.yml)
- [libs/lume/CHANGELOG.md](libs/lume/CHANGELOG.md)
- [libs/lume/VERSION](libs/lume/VERSION)
- [libs/lume/resources/Info.plist](libs/lume/resources/Info.plist)
- [libs/lume/resources/lume.entitlements](libs/lume/resources/lume.entitlements)
- [libs/lume/scripts/build/build-debug.sh](libs/lume/scripts/build/build-debug.sh)
- [libs/lume/scripts/build/build-release-notarized.sh](libs/lume/scripts/build/build-release-notarized.sh)
- [libs/lume/scripts/build/build-release.sh](libs/lume/scripts/build/build-release.sh)
- [libs/lume/scripts/install-local.sh](libs/lume/scripts/install-local.sh)
- [libs/lume/scripts/install.sh](libs/lume/scripts/install.sh)
- [libs/lume/scripts/uninstall.sh](libs/lume/scripts/uninstall.sh)
- [libs/lume/src/Main.swift](libs/lume/src/Main.swift)
- [libs/lume/src/Unattended/ResourceBundle.swift](libs/lume/src/Unattended/ResourceBundle.swift)
- [libs/lume/tests/Mocks/MockVM.swift](libs/lume/tests/Mocks/MockVM.swift)
- [libs/lume/tests/VM/VMDetailsPrinterTests.swift](libs/lume/tests/VM/VMDetailsPrinterTests.swift)
- [libs/lume/tests/VMTests.swift](libs/lume/tests/VMTests.swift)

</details>



Lume is a Swift-based VM management tool for macOS that enables the creation, configuration, and operation of macOS virtual machines on Apple Silicon hardware. It serves as a local provider for the Computer SDK, allowing agent code to run in isolated macOS VMs without requiring cloud infrastructure.

This section covers Lume's architecture, image registry integration, HTTP API, and image management capabilities. For information about using Lume as a provider in the Computer SDK, see [Provider Architecture](#4.1) and [Lume Provider (macOS VMs)](#4.3).

## Purpose and Scope

Lume provides:
- VM lifecycle management (create, start, stop, delete) [docs/content/docs/reference/lume/cli-reference.mdx:19-180]()
- Image distribution via GitHub Container Registry (ghcr.io) [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:161-166]()
- HTTP API for programmatic VM control [docs/content/docs/reference/lume/http-api.mdx:27-28]()
- MCP (Model Context Protocol) server for LLM-driven management [libs/lume/src/Server/MCPServer.swift:7-24]()
- Command-line interface for manual operations [libs/lume/src/Main.swift:7-17]()
- Integration with macOS `Virtualization.framework` [libs/lume/src/VM/VM.swift:3-4]()

Lume is specifically designed for Apple Silicon Macs running macOS 15+ and cannot be used on Intel Macs or other operating systems. The tool is implemented as a Swift package with a command-line entry point in [libs/lume/src/Main.swift:6-17]().

**Sources:** [libs/lume/src/Main.swift:6-17](), [libs/lume/VERSION:1-1](), [libs/lume/src/Server/MCPServer.swift:7-24](), [libs/lume/src/VM/VM.swift:3-4](), [docs/content/docs/reference/lume/cli-reference.mdx:19-180](), [docs/content/docs/reference/lume/http-api.mdx:27-28]()

---

## Lume in the Cua Ecosystem

Lume bridges high-level agent requests to low-level macOS virtualization primitives through a multi-layered interface.

"Natural Language / Intent" -> "Code Entity Space"

```mermaid
graph TB
    subgraph "User Code"
        ["Agent Code"]
    end
    
    subgraph "Computer SDK"
        ["Computer class"]
        ["VMProviderFactory"]
        ["LumeProvider"]
    end
    
    subgraph "Lume System"
        ["Lume (CLI entry)"] -- "libs/lume/src/Main.swift" --> ["LumeController"]
        ["Server (HTTP)"] -- "libs/lume/src/Server/Server.swift" --> ["LumeController"]
        ["LumeMCPServer"] -- "libs/lume/src/Server/MCPServer.swift" --> ["LumeController"]
    end
    
    subgraph "Execution Layer"
        ["LumeController"] -- "list/run/pull" --> ["VM class"]
        ["VM class"] -- "Virtualization" --> ["VZVirtualMachine"]
    end
    
    subgraph "Registry"
        ["ghcr.io/trycua"]
    end
    
    ["Agent Code"] --> ["Computer class"]
    ["Computer class"] --> ["VMProviderFactory"]
    ["VMProviderFactory"] --> ["LumeProvider"]
    ["LumeProvider"] --> ["Server (HTTP)"]
    ["LumeController"] --> ["ghcr.io/trycua"]
```

When the Computer SDK is initialized with `provider_type="lume"`, the `LumeProvider` communicates with the local Lume HTTP server (port 7777). The server must be running (`lume serve`) to accept requests. Commands can also be invoked directly via the Lume CLI or via the integrated `LumeMCPServer` which provides tools like `lume_create_vm` and `lume_run_vm` to agents [libs/lume/src/Server/MCPServer.swift:130-166](). The `LumeController` acts as the central bridge between external interfaces (CLI/API/MCP) and the underlying VM logic [libs/lume/src/LumeController.swift:66-86]().

**Sources:** [libs/lume/src/LumeController.swift:66-86](), [libs/lume/src/Main.swift:61-81](), [libs/lume/src/VM/VM.swift:44-73](), [libs/lume/src/Server/MCPServer.swift:130-166]()

---

## Core Components

Lume is composed of several specialized classes and structs that handle virtualization, storage, and networking.

"Lume Internals" -> "Code Entity Space"

```mermaid
graph TB
    subgraph "Interface"
        ["CommandRegistry"]
        ["Server"]
        ["LumeMCPServer"]
    end
    
    subgraph "Controller"
        ["LumeController"]
        ["SharedVM (Cache)"]
        ["PullProgressTracker"]
    end
    
    subgraph "VM Runtime"
        ["VM class"]
        ["VMDirContext"]
        ["VNCService"]
    end
    
    subgraph "Storage & Registry"
        ["Home (Paths)"]
        ["VMDirectory"]
        ["ImageContainerRegistry"]
    end
    
    ["CommandRegistry"] --> ["LumeController"]
    ["Server"] --> ["LumeController"]
    ["LumeMCPServer"] --> ["LumeController"]
    ["LumeController"] --> ["SharedVM (Cache)"]
    ["LumeController"] --> ["VM class"]
    ["LumeController"] --> ["Home (Paths)"]
    ["LumeController"] --> ["ImageContainerRegistry"]
    ["VM class"] --> ["VNCService"]
```

| Component | File | Responsibility |
|-----------|------|----------------|
| `Lume` | [libs/lume/src/Main.swift]() | Entry point for the CLI using `ArgumentParser` [libs/lume/src/Main.swift:7-17](). |
| `LumeController` | [libs/lume/src/LumeController.swift]() | Orchestrates high-level VM operations like `list`, `pullImage`, and `createAsync` [libs/lume/src/LumeController.swift:93-171](). |
| `SharedVM` | [libs/lume/src/LumeController.swift]() | `MainActor`-isolated singleton managing the cache of active `VM` instances [libs/lume/src/LumeController.swift:8-25](). |
| `VM` | [libs/lume/src/VM/VM.swift]() | Manages the lifecycle of a specific Virtualization.framework instance and attached services like VNC [libs/lume/src/VM/VM.swift:44-93](). |
| `ImageContainerRegistry` | [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift]() | Logic for hashing files (SHA256) and grouping OCI chunks for distribution [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:21-41](), [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:180-197](). |
| `PullProgressTracker` | [libs/lume/src/LumeController.swift]() | Thread-safe actor for tracking background image download percentages [libs/lume/src/LumeController.swift:31-63](). |

**Sources:** [libs/lume/src/Main.swift:7-17](), [libs/lume/src/LumeController.swift:8-171](), [libs/lume/src/VM/VM.swift:44-93](), [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:21-197]()

---

## VM Lifecycle Operations

Lume implements a state machine where VMs move between stopped, provisioning, pulling, and running states.

| Operation | CLI Command | HTTP Handler | Description |
|-----------|-------------|---------------|-------------|
| Create | `lume create` [docs/content/docs/reference/lume/cli-reference.mdx:21]() | `handleCreateVM` | Provisions a new VM from IPSW; returns 202 Accepted while provisioning [libs/lume/src/Server/Handlers.swift:128-174](). |
| Pull | `lume pull` [docs/content/docs/reference/lume/cli-reference.mdx:250]() | `handlePullStart` | Downloads an OCI image from registry asynchronously [libs/lume/src/Server/Handlers.swift:62-126](). |
| Run | `lume run` [docs/content/docs/reference/lume/cli-reference.mdx:53]() | `handleRunVM` | Starts the VM; supports shared directories, display modes, and VNC [libs/lume/src/VM/VM.swift:174-180](). |
| List | `lume ls` [docs/content/docs/reference/lume/cli-reference.mdx:201]() | `handleListVMs` | Returns `VMDetails` for all local VMs found in Lume home [libs/lume/src/LumeController.swift:93-157](). |
| Delete | `lume delete` [docs/content/docs/reference/lume/cli-reference.mdx:159]() | `handleDeleteVM` | Removes VM files and configuration from storage [libs/lume/src/Server/Handlers.swift:195-238](). |

**Sources:** [libs/lume/src/Server/Handlers.swift:62-238](), [libs/lume/src/LumeController.swift:93-157](), [libs/lume/src/VM/VM.swift:174-180](), [docs/content/docs/reference/lume/cli-reference.mdx:21-250]()

---

## HTTP API Overview

The Lume HTTP server (port 7777) allows for remote and automated management of VMs.

- **Status Polling**: Because operations like `pull` and `create` are asynchronous, the API returns 202 Accepted [libs/lume/src/Server/Handlers.swift:117-126](). Clients use the `name` to poll `GET /lume/vms/:name` to see progress updates from the `PullProgressTracker` [libs/lume/src/Server/Handlers.swift:30-50]().
- **VM Details**: The `VMDetails` structure provided by `handleGetVM` includes status, IP address, VNC URL, and hardware specs [libs/lume/src/VM/VM.swift:123-161]().
- **Unattended Setup**: The API supports the `unattended` parameter for macOS VMs, enabling automatic user creation and SSH setup during provisioning [docs/content/docs/reference/lume/cli-reference.mdx:41-42]().

**Sources:** [libs/lume/src/Server/Handlers.swift:30-126](), [libs/lume/src/VM/VM.swift:123-161](), [docs/content/docs/reference/lume/http-api.mdx:27-28](), [docs/content/docs/reference/lume/cli-reference.mdx:41-42]()

---

## Image Management and Registry

Lume uses an OCI-compliant registry integration primarily focused on `ghcr.io/trycua`.

- **Sparse File Reassembly**: To minimize disk usage and transfer time, Lume's `gunzipChunkAndWriteSparse` function detects 4MiB zero-filled blocks during decompression and creates holes in the destination file instead of writing zeros [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:43-97]().
- **Layer Checksums**: All downloaded layers undergo streaming SHA256 verification to ensure integrity [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:22-41]().
- **Metadata Annotations**: Lume uses OCI annotations like `com.trycua.lume.disk.uncompressed_size` to manage VM disk expansion [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:151-157]().

**Sources:** [libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift:22-157]()

---

## Subsections

For detailed information on specific aspects of Lume:

- **[Lume Architecture](#5.1)** — Internal architecture of Lume: Swift implementation, `LumeController`, VM lifecycle management, error model, unattended setup presets, and integration with macOS `Virtualization.framework`
- **[Image Registry Integration](#5.2)** — How Lume integrates with ghcr.io and GCS registries: authentication, manifest fetching, OCI image format, RegistryFactory, and multi-architecture support
- **[HTTP API Reference](#5.3)** — Complete HTTP API reference for Lume server (port 7777): VM management endpoints, configuration endpoints, logging endpoints, MCP server, and request/response schemas
- **[Image Pull and Cache System](#5.4)** — Deep dive into image pulling: concurrent layer downloads, progress tracking, disk image reassembly with zero-skipping, cache validation, and performance optimizations
- **[Image Push and Distribution](#5.5)** — Publishing VMs to registry: chunking strategy, LZ4 compression, blob upload, manifest generation, multi-tag support, the push CLI command, and Lume build/notarization scripts
- **[Lume Metal Capability Shim](#5.6)** — Document the experimental Metal capability shim for macOS VMs: process-scoped DYLD_INSERT_LIBRARIES shim raising reported Apple GPU family support and threadgroup memory limits, build process, LUME_METAL_APPLE_FAMILY_MAX/LUME_METAL_MAX_THREADGROUP_MEMORY env vars, caveats, and the evidence/ validation runs on M1 Ultra

---

