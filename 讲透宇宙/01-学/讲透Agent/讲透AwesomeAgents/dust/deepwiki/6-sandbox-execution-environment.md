<!-- source: DeepWiki mcp.deepwiki.com · repo dust-tt/dust · page 6 Sandbox Execution Environment · fetched 2026-10-26 -->

# 6. Sandbox Execution Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/dust-sandbox/Cargo.lock](cli/dust-sandbox/Cargo.lock)
- [cli/dust-sandbox/Cargo.toml](cli/dust-sandbox/Cargo.toml)
- [front-api/routes/w/[wId]/assistant/conversations/[cId]/sandbox/index.ts](front-api/routes/w/[wId]/assistant/conversations/[cId]/sandbox/index.ts)
- [front/lib/api/actions/servers/sandbox/metadata.ts](front/lib/api/actions/servers/sandbox/metadata.ts)
- [front/lib/api/actions/servers/sandbox/tools/index.test.ts](front/lib/api/actions/servers/sandbox/tools/index.test.ts)
- [front/lib/api/actions/servers/sandbox/tools/index.ts](front/lib/api/actions/servers/sandbox/tools/index.ts)
- [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.test.ts](front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.test.ts)
- [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts](front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts)
- [front/lib/api/sandbox/egress.test.ts](front/lib/api/sandbox/egress.test.ts)
- [front/lib/api/sandbox/egress.ts](front/lib/api/sandbox/egress.ts)
- [front/lib/api/sandbox/gcs/token.test.ts](front/lib/api/sandbox/gcs/token.test.ts)
- [front/lib/api/sandbox/gcs/token.ts](front/lib/api/sandbox/gcs/token.ts)
- [front/lib/api/sandbox/hardening.ts](front/lib/api/sandbox/hardening.ts)
- [front/lib/api/sandbox/image/egress/dust-egress-nftables.service](front/lib/api/sandbox/image/egress/dust-egress-nftables.service)
- [front/lib/api/sandbox/image/egress/dust-egress-resolver.service](front/lib/api/sandbox/image/egress/dust-egress-resolver.service)
- [front/lib/api/sandbox/image/egress/egress-nftables.sh](front/lib/api/sandbox/image/egress/egress-nftables.sh)
- [front/lib/api/sandbox/image/profile/soffice/pdf_text.py](front/lib/api/sandbox/image/profile/soffice/pdf_text.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_audit.py](front/lib/api/sandbox/image/profile/soffice/pptx_audit.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_contrast.py](front/lib/api/sandbox/image/profile/soffice/pptx_contrast.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_fontmetrics.py](front/lib/api/sandbox/image/profile/soffice/pptx_fontmetrics.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_geometry.py](front/lib/api/sandbox/image/profile/soffice/pptx_geometry.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_inspect.py](front/lib/api/sandbox/image/profile/soffice/pptx_inspect.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_render_boxes.py](front/lib/api/sandbox/image/profile/soffice/pptx_render_boxes.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_slides.py](front/lib/api/sandbox/image/profile/soffice/pptx_slides.py)
- [front/lib/api/sandbox/image/profile/soffice/pptx_typography.py](front/lib/api/sandbox/image/profile/soffice/pptx_typography.py)
- [front/lib/api/sandbox/image/profile/soffice/render.py](front/lib/api/sandbox/image/profile/soffice/render.py)
- [front/lib/api/sandbox/image/profile/soffice/render_publish.py](front/lib/api/sandbox/image/profile/soffice/render_publish.py)
- [front/lib/api/sandbox/image/profile/soffice/tests/test_audit.py](front/lib/api/sandbox/image/profile/soffice/tests/test_audit.py)
- [front/lib/api/sandbox/image/profile/soffice/tests/test_contrast.py](front/lib/api/sandbox/image/profile/soffice/tests/test_contrast.py)
- [front/lib/api/sandbox/image/profile/soffice/tests/test_geometry.py](front/lib/api/sandbox/image/profile/soffice/tests/test_geometry.py)
- [front/lib/api/sandbox/image/profile/soffice/tests/test_render.py](front/lib/api/sandbox/image/profile/soffice/tests/test_render.py)
- [front/lib/api/sandbox/image/profile/soffice/tests/test_slides.py](front/lib/api/sandbox/image/profile/soffice/tests/test_slides.py)
- [front/lib/api/sandbox/image/registry.test.ts](front/lib/api/sandbox/image/registry.test.ts)
- [front/lib/api/sandbox/image/registry.ts](front/lib/api/sandbox/image/registry.ts)
- [front/lib/api/sandbox/image/token/dust-gcs-token-firewall.sh](front/lib/api/sandbox/image/token/dust-gcs-token-firewall.sh)
- [front/lib/api/sandbox/instrumentation.ts](front/lib/api/sandbox/instrumentation.ts)
- [front/lib/api/sandbox/lifecycle.test.ts](front/lib/api/sandbox/lifecycle.test.ts)
- [front/lib/api/sandbox/lifecycle.ts](front/lib/api/sandbox/lifecycle.ts)
- [front/lib/api/sandbox/provider.ts](front/lib/api/sandbox/provider.ts)
- [front/lib/api/sandbox/providers/e2b.test.ts](front/lib/api/sandbox/providers/e2b.test.ts)
- [front/lib/api/sandbox/providers/e2b.ts](front/lib/api/sandbox/providers/e2b.ts)
- [front/lib/api/sandbox/sandbox_child_block.test.ts](front/lib/api/sandbox/sandbox_child_block.test.ts)
- [front/lib/api/sandbox/sandbox_child_block.ts](front/lib/api/sandbox/sandbox_child_block.ts)
- [front/lib/resources/conversation_sandbox_adapter.ts](front/lib/resources/conversation_sandbox_adapter.ts)
- [front/lib/resources/pod_sandbox_adapter.ts](front/lib/resources/pod_sandbox_adapter.ts)
- [front/lib/resources/sandbox_resource.test.ts](front/lib/resources/sandbox_resource.test.ts)
- [front/lib/resources/sandbox_resource.ts](front/lib/resources/sandbox_resource.ts)
- [front/lib/resources/skill/code_defined/global/pptx.ts](front/lib/resources/skill/code_defined/global/pptx.ts)
- [front/lib/resources/storage/models/sandbox.ts](front/lib/resources/storage/models/sandbox.ts)
- [front/migrations/pre-deploy/20260724155601_add_sandbox_reaper_indexes.sql](front/migrations/pre-deploy/20260724155601_add_sandbox_reaper_indexes.sql)
- [front/migrations/pre-deploy/20260730131801_add_sandbox_reaper_kill_requested_sleeping_index.sql](front/migrations/pre-deploy/20260730131801_add_sandbox_reaper_kill_requested_sleeping_index.sql)
- [front/migrations/pre-deploy/20260826122416_prepare_frames_v2_schema.sql](front/migrations/pre-deploy/20260826122416_prepare_frames_v2_schema.sql)
- [front/scripts/sandbox_security_check.test.ts](front/scripts/sandbox_security_check.test.ts)
- [front/scripts/sandbox_security_check.ts](front/scripts/sandbox_security_check.ts)
- [front/temporal/sandbox_reaper/activities.test.ts](front/temporal/sandbox_reaper/activities.test.ts)
- [front/temporal/sandbox_reaper/activities.ts](front/temporal/sandbox_reaper/activities.ts)
- [front/temporal/sandbox_reaper/config.ts](front/temporal/sandbox_reaper/config.ts)
- [front/temporal/sandbox_reaper/kill_requester/activities.test.ts](front/temporal/sandbox_reaper/kill_requester/activities.test.ts)
- [front/temporal/sandbox_reaper/kill_requester/activities.ts](front/temporal/sandbox_reaper/kill_requester/activities.ts)
- [front/temporal/sandbox_reaper/kill_requester/client.test.ts](front/temporal/sandbox_reaper/kill_requester/client.test.ts)
- [front/temporal/sandbox_reaper/kill_requester/client.ts](front/temporal/sandbox_reaper/kill_requester/client.ts)
- [front/temporal/sandbox_reaper/kill_requester/helpers.ts](front/temporal/sandbox_reaper/kill_requester/helpers.ts)
- [front/temporal/sandbox_reaper/kill_requester/workflows.ts](front/temporal/sandbox_reaper/kill_requester/workflows.ts)
- [front/temporal/sandbox_reaper/worker.ts](front/temporal/sandbox_reaper/worker.ts)
- [front/temporal/sandbox_reaper/workflows.test.ts](front/temporal/sandbox_reaper/workflows.test.ts)
- [front/temporal/sandbox_reaper/workflows.ts](front/temporal/sandbox_reaper/workflows.ts)
- [front/tests/utils/SandboxFactory.ts](front/tests/utils/SandboxFactory.ts)

</details>



The Sandbox Execution Environment provides a secure and isolated system for executing untrusted code, primarily for Dust's AI agents. This environment is critical for enabling agents to run custom code, interact with external services, and process data without compromising the integrity or security of the main Dust platform.

The system leverages E2B as its primary sandbox provider, managing the lifecycle of sandboxes from creation to destruction. It incorporates robust security hardening measures, including network egress control and file system isolation, to ensure that code execution is contained. A dedicated CLI tool, `dsbx`, facilitates interaction with the sandbox environment.

This page offers a high-level overview of the sandbox system. For detailed information on specific components, refer to the linked child pages.

## Sandbox Infrastructure

The sandbox infrastructure is responsible for the provisioning, management, and security of the execution environments. It defines the lifecycle of a `SandboxResource` [front/lib/resources/sandbox_resource.ts:155-156](), integrating with the E2B provider to create and manage isolated virtual machines. Key aspects include the sandbox image registry, which defines the base environment for execution, and the egress proxy, which strictly controls outbound network access. Security hardening is a continuous process, with measures like `nftables` for network control and file system isolation. The `sandbox_reaper` Temporal workflow [front/temporal/sandbox_reaper/workflows.ts:1-10]() ensures that inactive or problematic sandboxes are properly terminated and cleaned up.

For details, see [Sandbox Infrastructure](#6.1).

Sources:
- [front/lib/resources/sandbox_resource.ts:155-156]()
- [front/temporal/sandbox_reaper/workflows.ts:1-10]()

## Sandbox Functions (Pod Functions)

Sandbox Functions, also known as Pod Functions, are the specific units of code executed within the sandboxed environment. This system manages the lifecycle of `SandboxFunctionResource` and `SandboxFunctionInvocationResource`, from their initial publishing through a dedicated pipeline to their execution. It supports both fast and durable execution modes, catering to different performance and reliability requirements. Integration with the MCP (Model Context Protocol) tool system allows these functions to interact with external services in a controlled manner. The `functions-runner` protocol defines how these functions are invoked and how their results are communicated back to the Dust platform.

For details, see [Sandbox Functions (Pod Functions)](#6.2).

Sources:
- [front/lib/resources/sandbox_resource.ts]()

## Sandbox Lifecycle and E2B Provider

The `SandboxResource` [front/lib/resources/sandbox_resource.ts:155-156]() is the central abstraction for managing sandboxes. Its lifecycle is orchestrated through methods like `ensureActive` [front/lib/resources/sandbox_resource.ts:290-290]() and `destroy` [front/lib/resources/sandbox_resource.ts:499-499](), which interact with the underlying `E2BSandboxProvider` [front/lib/api/sandbox/providers/e2b.ts:1-1](). The `ensureActive` method handles the creation or waking of a sandbox, while `destroy` is responsible for its termination.

The `E2BSandboxProvider` [front/lib/api/sandbox/providers/e2b.ts:1-1]() implements the `SandboxProvider` [front/lib/api/sandbox/provider.ts:14-20]() interface, abstracting the specifics of E2B's API. This provider handles the actual VM provisioning, command execution (`exec` [front/lib/api/sandbox/provider.ts:11-11]()), and file system operations, including mounting GCS buckets via the `GCSMountAdapter` [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts:1-1]().

```mermaid
graph TD
    A[Dust Platform] --> B{SandboxResource.ensureActive()};
    B --> C{executeWithLock()};
    C --> D{SandboxResource.fetchSandbox()};
    D -- "Sandbox exists and is running" --> E[SandboxResource.wake()];
    D -- "Sandbox exists but is sleeping" --> E;
    D -- "No sandbox" --> F[SandboxResource.create()];
    E --> G[E2BSandboxProvider.wake()];
    F --> H[E2BSandboxProvider.create()];
    G --> I[Sandbox Ready];
    H --> I;
    I --> J[SandboxResource.exec()];
    J --> K[E2BSandboxProvider.exec()];
    K --> L[Command Execution Result];
    L --> M[SandboxResource.updateStatus()];
    M --> N[SandboxResource.destroy()];
    N --> O[E2BSandboxProvider.destroy()];
    O --> P[Sandbox Terminated];

    subgraph "Sandbox Lifecycle"
        B
        C
        D
        E
        F
        G
        H
        I
        J
        K
        L
        M
        N
        O
        P
    end

    subgraph "E2B Provider"
        G
        H
        K
        O
    end

    subgraph "Database"
        D -- "Read SandboxModel" --> Q[SandboxModel];
        F -- "Create SandboxModel" --> Q;
        M -- "Update SandboxModel" --> Q;
        N -- "Delete SandboxModel" --> Q;
    end

    subgraph "Locking"
        C -- "Acquires lockKey" --> R[Redis Lock];
        C -- "Releases lockKey" --> R;
    end

    subgraph "GCS Integration"
        K -- "Mount GCS" --> S[GCSMountAdapter];
    end
```
**Diagram: Sandbox Lifecycle and E2B Provider Interaction**

Sources:
- [front/lib/resources/sandbox_resource.ts:155-156]()
- [front/lib/resources/sandbox_resource.ts:290-290]()
- [front/lib/resources/sandbox_resource.ts:499-499]()
- [front/lib/api/sandbox/providers/e2b.ts:1-1]()
- [front/lib/api/sandbox/provider.ts:14-20]()
- [front/lib/api/sandbox/provider.ts:11-11]()
- [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts:1-1]()

## Sandbox Image Registry

The sandbox image registry [front/lib/api/sandbox/image/registry.ts:1-1]() defines the various base images used for sandboxes, such as `dust-base` [front/lib/api/sandbox/image/registry.ts:29-29]() and `dust-bedrock` [front/lib/api/sandbox/image/registry.ts:28-28](). These images are pre-configured with essential tools and libraries, including Python packages [front/lib/api/sandbox/image/registry.ts:71-129]() like `pandas`, `numpy`, and `scikit-learn`, as well as CLI tools like `dsbx` [front/lib/api/sandbox/image/registry.ts:30-30](), `dbt` [front/lib/api/sandbox/image/registry.ts:41-41](), and `snow` (Snowflake CLI) [front/lib/api/sandbox/image/registry.ts:43-43](). The registry also specifies security hardening commands [front/lib/api/sandbox/image/registry.ts:3-5]() that are applied during image build to restrict privileges and access.

```mermaid
graph TD
    A[Sandbox Image Registry] --> B{getSandboxImageFromRegistry()};
    B --> C{SandboxImage: "dust-base"};
    B --> D{SandboxImage: "dust-bedrock"};

    C --> C1[Base OS: Ubuntu 24.04];
    C --> C2[Python Libraries: pandas, numpy, scikit-learn, etc.];
    C --> C3[CLI Tools: dsbx, dbt, snow, etc.];
    C --> C4[Security Hardening Commands];

    D --> D1[Base OS: Ubuntu 24.04];
    D --> D2[Minimal Toolset];
    D --> D3[Security Hardening Commands];

    subgraph "Image Build Process"
        C4 --> E[getLocalAccountPrivilegeHardeningCommand()];
        C4 --> F[getRootConsumedPathHardeningCommand()];
        C4 --> G[getSandboxServicePathHardeningCommand()];
    end

    subgraph "Python Environment"
        C2 --> H[PYTHON_LIBRARIES];
        C2 --> I[getPythonInstallCmd()];
    end

    subgraph "dsbx CLI"
        C3 --> J[DSBX_CLI_VERSION];
    end
```
**Diagram: Sandbox Image Registry Overview**

Sources:
- [front/lib/api/sandbox/image/registry.ts:1-1]()
- [front/lib/api/sandbox/image/registry.ts:29-29]()
- [front/lib/api/sandbox/image/registry.ts:28-28]()
- [front/lib/api/sandbox/image/registry.ts:71-129]()
- [front/lib/api/sandbox/image/registry.ts:30-30]()
- [front/lib/api/sandbox/image/registry.ts:41-41]()
- [front/lib/api/sandbox/image/registry.ts:43-43]()
- [front/lib/api/sandbox/image/registry.ts:3-5]()

## Security Hardening and Egress Control

Security is paramount in the sandbox environment. Hardening measures are applied at multiple layers:

*   **Image Level**: During image creation, commands are executed to restrict user privileges, lock down sensitive paths, and remove unnecessary software like `sudo` [front/lib/api/sandbox/image/registry.test.ts:174-199]().
*   **Network Egress**: All outbound network traffic from the sandbox is routed through a Rust-based `egress-proxy` [front/lib/api/sandbox/egress.ts:65-68](). This proxy enforces a strict allowlist policy, controlled by `nftables` [front/lib/api/sandbox/image/egress/egress-nftables.sh:1-1](). The `mintEgressJwt` [front/lib/api/sandbox/egress.ts:118-144]() function generates JWTs for authentication with the proxy, ensuring that only authorized traffic reaches external services. The `add_egress_domain` [front/lib/api/actions/servers/sandbox/tools/index.ts:73-73]() and `request_egress_domain` [front/lib/api/actions/servers/sandbox/tools/index.ts:74-74]() tools allow agents to dynamically manage their allowed egress domains, subject to workspace policies.
*   **File System**: The `GCSMountAdapter` [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts:1-1]() securely mounts Google Cloud Storage buckets into the sandbox, providing isolated and persistent storage for agent data.

```mermaid
graph TD
    A[Sandbox VM] --> B{Egress Proxy};
    B --> C[External Services];

    subgraph "Sandbox Environment"
        A1[Agent Code Execution] --> A2[Network Request];
        A2 --> B;
        A3[File System Access] --> A4[GCSMountAdapter];
        A4 --> A5[Google Cloud Storage];
    end

    subgraph "Egress Proxy"
        B1[JWT Validation] --> B2[Policy Enforcement];
        B2 --> B3[nftables Rules];
        B3 --> C;
    end

    subgraph "Security Hardening"
        H1[Image Build] --> H2[Privilege Restriction];
        H1 --> H3[Path Hardening];
        H1 --> H4[Sudo Removal];
    end

    A1 -- "Uses" --> H1;
    A2 -- "Authenticated by" --> D[mintEgressJwt()];
    D --> B1;
    A2 -- "Managed by" --> E[add_egress_domain()];
    A2 -- "Managed by" --> F[request_egress_domain()];
    E --> B2;
    F --> B2;
```
**Diagram: Sandbox Security and Egress Control**

Sources:
- [front/lib/api/sandbox/image/registry.test.ts:174-199]()
- [front/lib/api/sandbox/egress.ts:65-68]()
- [front/lib/api/sandbox/image/egress/egress-nftables.sh:1-1]()
- [front/lib/api/sandbox/egress.ts:118-144]()
- [front/lib/api/actions/servers/sandbox/tools/index.ts:73-73]()
- [front/lib/api/actions/servers/sandbox/tools/index.ts:74-74]()
- [front/lib/api/file_system/sandbox/gcs_sandbox_mount_adapter.ts:1-1]()

## The `dsbx` CLI

The `dsbx` CLI [cli/dust-sandbox/Cargo.toml:3-4]() is a Rust-based command-line tool [cli/dust-sandbox/Cargo.toml:1-1]() that provides an interface for interacting with the sandbox environment. It is built with `clap` [cli/dust-sandbox/Cargo.toml:11-11]() for argument parsing and `tokio` [cli/dust-sandbox/Cargo.toml:12-12]() for asynchronous operations. This tool is instrumental for debugging, testing, and managing sandboxes directly, offering functionalities such as executing commands, managing files, and inspecting sandbox state.

Sources:
- [cli/dust-sandbox/Cargo.toml:3-4]()
- [cli/dust-sandbox/Cargo.toml:1-1]()
- [cli/dust-sandbox/Cargo.toml:11-11]()
- [cli/dust-sandbox/Cargo.toml:12-12]()

---

