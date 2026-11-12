<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/OpenShell-Community · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



OpenShell-Community serves as the ecosystem hub for the OpenShell core runtime, hosting contributed sandbox images, agent skills, and workflow integrations [README.md:1-10](). While the core engine provides the runtime environment, policy enforcement, privacy router, and CLI [README.md:8](), this repository acts as a collaborative space for domain-specific environments and extensibility [README.md:10]().

## Relationship to OpenShell Core Runtime

[OpenShell](https://github.com/NVIDIA/OpenShell) provides the underlying infrastructure and execution runtime for autonomous agents [README.md:8](). The core engine handles sandbox isolation, network gateways, and host integration [README.md:8](). The `OpenShell-Community` repository builds upon this foundation by defining specialized container environments (such as Ollama, Android automation, and GPU-accelerated environments) and reusable agent capabilities [README.md:8-30]().

```mermaid
graph TD
    title "Core Runtime to Community Ecosystem Mapping"
    OpenShellCore["OpenShell Core Runtime Engine"] -->|Provides CLI & Runtime| OpenShellCLI["openshell CLI"]
    OpenShellCLI -->|Reads Sandbox Definitions| CommunityRepo["OpenShell-Community Repository"]
    CommunityRepo --> BaseImg["sandboxes/base/Dockerfile"]
    CommunityRepo --> OllamaImg["sandboxes/ollama/Dockerfile"]
    CommunityRepo --> DroidImg["sandboxes/droid/Dockerfile"]
    CommunityRepo --> GPUImg["sandboxes/nvidia-gpu/Dockerfile"]
```
Sources: [README.md:8-30]()

## Repository Structure Overview

The repository is organized around domain-specific sandboxes, supporting skills, and community contributions [README.md:14-30](). Each sandbox container image bundles required runtime dependencies, pre-installed toolchains, and security policy templates [README.md:18-30]().

```mermaid
graph LR
    title "Community Repository Entity Mapping"
    User["Developer / Agent"] -->|Runs Command| CLI["openshell sandbox create"]
    CLI -->|Discovers Image| SandboxDir["sandboxes/ Directory"]
    SandboxDir --> Dockerfile["Dockerfile"]
    SandboxDir --> Policy["policy.yaml Configuration"]
    SandboxDir --> Skills["skills/ SKILL.md"]
```
Sources: [README.md:40-46](), [CONTRIBUTING.md:43-64]()

## Child Pages

For detailed information on getting started and repository conventions, refer to the child pages:

- **[Getting Started](#1.1)** — Instructions for installing the `openshell` CLI, launching sandboxes with `openshell sandbox create --from <sandbox>`, and building images locally with Docker [README.md:32-60]().
- **[Repository Layout and Conventions](#1.2)** — Directory structure breakdowns (`sandboxes/`, `skills/`, `.github/`) and per-sandbox file layout guidelines (`Dockerfile`, `policy.yaml`, `README.md`) [README.md:14-30](), [CONTRIBUTING.md:43-65]().

Sources: [README.md:1-72](), [CONTRIBUTING.md:1-90]()

---

