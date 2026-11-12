<!-- source: DeepWiki mcp.deepwiki.com · repo openai/tart · page 8 Integrations and Ecosystem · fetched 2026-10-26 -->

# Integrations and Ecosystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/faq.md](docs/faq.md)
- [docs/integrations/buildkite.md](docs/integrations/buildkite.md)
- [docs/integrations/cirrus-cli.md](docs/integrations/cirrus-cli.md)
- [docs/integrations/gitlab-runner.md](docs/integrations/gitlab-runner.md)
- [docs/integrations/packer.md](docs/integrations/packer.md)
- [docs/orchard/architecture-and-security.md](docs/orchard/architecture-and-security.md)
- [docs/orchard/deploying-controller.md](docs/orchard/deploying-controller.md)
- [docs/orchard/deploying-workers.md](docs/orchard/deploying-workers.md)
- [docs/orchard/integration-guide.md](docs/orchard/integration-guide.md)
- [docs/orchard/quick-start.md](docs/orchard/quick-start.md)
- [docs/orchard/using-orchard-cli.md](docs/orchard/using-orchard-cli.md)
- [mkdocs.yml](mkdocs.yml)

</details>



Tart is designed to be a modular component within a larger automation ecosystem. While the core `tart` CLI manages the lifecycle of individual virtual machines on a single host, it integrates with a variety of external tools for CI/CD, image automation, and multi-node orchestration.

### Ecosystem Overview

The Tart ecosystem bridges the gap between local VM management and distributed cloud infrastructure. It leverages standard protocols like OCI for image distribution and SSH/VNC for guest access, allowing it to plug into existing DevOps workflows.

**Conceptual Mapping: Tooling to Code Entities**

```mermaid
graph TD
    subgraph "External Ecosystem"
        [Packer] --> |"uses"| [PackerPluginTart]
        [GitLabRunner] --> |"calls"| [GitLabTartExecutor]
        [CirrusCLI] --> |"parses"| [CirrusYML]
    end

    subgraph "Tart Codebase"
        [PackerPluginTart] --> |"executes"| [TartCLI]
        [GitLabTartExecutor] --> |"executes"| [TartCLI]
        [TartCLI] --> [VMConfig]
        [VMConfig] --> [Virtualization.Framework]
    end

    subgraph "Orchestration Space"
        [OrchardCLI] --> |"gRPC/REST"| [OrchardController]
        [OrchardController] --> |"manages"| [OrchardWorker]
        [OrchardWorker] --> |"wraps"| [TartCLI]
    end
```
**Sources:** [docs/integrations/packer.md:19-28](), [docs/integrations/gitlab-runner.md:8-16](), [docs/orchard/quick-start.md:1-14]()

---

### CI/CD Integrations

Tart is frequently used as a backend for ephemeral CI workers. These integrations typically handle the lifecycle of pulling a base image, running a build script, and cleaning up the VM.

*   **Cirrus CLI:** A tool for running reproducible tasks locally or in CI. It uses a `.cirrus.yml` file to define `macos_instance` tasks that run inside Tart VMs [docs/integrations/cirrus-cli.md:8-27]().
*   **GitLab Runner:** Utilizes a custom executor (`gitlab-tart-executor`) to run GitLab jobs in isolated, ephemeral Tart environments [docs/integrations/gitlab-runner.md:8-10]().
*   **Buildkite:** Uses the `tart-buildkite-plugin` to spin up VMs for pipeline steps [docs/integrations/buildkite.md:8-10]().
*   **Packer:** The `packer-plugin-tart` allows for automated VM image creation, enabling "Infrastructure as Code" for macOS and Linux images [docs/integrations/packer.md:6-16]().

For detailed configuration examples and setup guides, see **[CI/CD Integrations](#8.1)**.

**Sources:** [docs/integrations/cirrus-cli.md:1-40](), [docs/integrations/gitlab-runner.md:1-20](), [docs/integrations/packer.md:1-17]()

---

### Orchard Cluster Orchestration

When scaling beyond a single host, the **Orchard** system provides a controller-worker architecture for managing a fleet of Tart-enabled machines.

*   **Controller:** A central API server responsible for scheduling and resource management. It can be deployed via Docker or Kubernetes [docs/orchard/deploying-controller.md:3-7](), [docs/orchard/architecture-and-security.md:5-7]().
*   **Worker:** A daemon running on macOS hosts that executes Tart commands. Workers automatically report hardware resources like `org.cirruslabs.logical-cores` and `org.cirruslabs.memory-mib` to the controller [docs/orchard/using-orchard-cli.md:81-86](), [docs/orchard/architecture-and-security.md:6-6]().
*   **Security:** Uses a hybrid PKI security model. It defaults to automatic PKI verification for publicly valid certificates but allows manual fingerprint trust for self-signed certificates [docs/orchard/architecture-and-security.md:15-26]().

**System Interaction: Orchard to Tart**

| Orchard Entity | Code/System Equivalent | Role |
| :--- | :--- | :--- |
| `orchard dev` | `OrchardController` + `OrchardWorker` | Local development mode for testing API/CLI [docs/orchard/quick-start.md:9-14]() |
| `org.cirruslabs.tart-vms` | Resource Slot | Scheduling unit for VM capacity (defaults to 2 per worker) [docs/orchard/integration-guide.md:184-187]() |
| `orchard vnc` | `ScreenSharingVNC` | Proxied VNC connection to guest via Controller [docs/orchard/quick-start.md:71-77]() |
| `Bootstrap Token` | `ServiceAccount` Token | Encapsulates Controller trust for non-interactive worker deployment [docs/orchard/architecture-and-security.md:45-51]() |

For details on deploying and managing clusters, see **[Orchard Cluster Orchestration](#8.2)**.

**Sources:** [docs/orchard/quick-start.md:1-80](), [docs/orchard/integration-guide.md:180-187](), [docs/orchard/architecture-and-security.md:1-67]()

---

### FAQ and Troubleshooting

Running Tart in production environments (especially headless ones) introduces specific OS-level requirements and networking challenges.

*   **Headless Mode:** macOS 15 (Sequoia) requires an unlocked `login.keychain` for `Virtualization.Framework` to initialize VMs. Failure results in `SecKeyCreateRandomKey_ios` errors [docs/faq.md:8-17]().
*   **Networking:** Common tasks include changing the default NAT subnet via `com.apple.vmnet.plist` [docs/faq.md:95-103](), managing DHCP lease exhaustion [docs/faq.md:111-120](), and bypassing "Local Network" permission pop-ups [docs/faq.md:80-91]().
*   **Nested Virtualization:** Supported on M3/M4 chips for Linux guests using the `--nested` flag in `tart run` [docs/faq.md:59-63]().
*   **Storage Layout:** Tart stores local VMs in `~/.tart/vms/` and remote OCI cache in `~/.tart/cache/OCIs/` [docs/faq.md:54-58]().

For a list of common issues and their resolutions, see **[FAQ and Troubleshooting](#8.3)**.

**Sources:** [docs/faq.md:8-32](), [docs/faq.md:54-63](), [docs/faq.md:80-120]()

---

