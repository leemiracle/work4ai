<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nemoclaw-community · extra page Hermes Agent Sandbox · fetched 2026-10-26 -->

# Hermes Agent Sandbox

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/outlook/outlook-bridge.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/outlook/outlook-bridge.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/manifest.yaml](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/manifest.yaml)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/nemo-relay/hermes-cli-shim](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/nemo-relay/hermes-cli-shim)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/sitecustomize.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/sitecustomize.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/slack_diagnostic.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/slack_diagnostic.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_slack_interactive_compat.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_slack_interactive_compat.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_tui_runtime_contract.py](examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_tui_runtime_contract.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/docs/set-up-slack.md](examples/recipes/nvidia/developer-community-chief-of-staff/docs/set-up-slack.md)
- [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py](examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py)
- [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/tests/test_slack_delivery_diagnostic.py](examples/recipes/nvidia/developer-community-chief-of-staff/scripts/tests/test_slack_delivery_diagnostic.py)

</details>



The Hermes Agent Sandbox is a hardened, containerized execution environment designed for the **Developer Community Chief of Staff** recipe. It integrates the [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent) with NVIDIA's **NeMo Relay** and **OpenShell** security primitives. The sandbox enforces a "shared-nothing" isolation model where the agent's runtime state is separated from its immutable configuration, and all egress is mediated by an L7 proxy with credential substitution.

## Architecture and Data Flow

The sandbox operates as a multi-process container. The primary agent process communicates with messaging platforms (Slack, Outlook) and inference endpoints through specialized sidecars and shims that bridge the gap between Hermes's native capabilities and the OpenShell security architecture.

### Sandbox Component Interaction
"Natural Language Space" to "Code Entity Space" Bridge:
```mermaid
graph TD
    subgraph "Sandbox Container (hermes-direct)"
        [Entrypoint] -- "starts" --> [nemoclaw-start]
        [nemoclaw-start] -- "spawns" --> [hermes-gateway]
        [nemoclaw-start] -- "spawns" --> [atif-bridge.py]
        [nemoclaw-start] -- "spawns" --> [outlook-bridge.py]
        
        subgraph "Hermes Runtime"
            [hermes-gateway] -- "loads" --> [nemo-relay-plugin]
            [nemo-relay-plugin] -- "exports" --> [atif-bridge.py]
        end
        
        subgraph "Bridges & Shims"
            [atif-bridge.py] -- "HTTPS (L7 Proxy)" --> [Host-Relay]
            [outlook-bridge.py] -- "HTTPS (L7 Proxy)" --> [MS-Graph]
            [hermes-cli-shim] -- "intercepts" --> [hermes-cli]
        end
    end

    subgraph "Host Services"
        [Host-Relay] -- "S3/MinIO" --> [Storage]
    end

    style [nemoclaw-start] stroke-dasharray: 5 5
    style [hermes-gateway] stroke-width: 2px
```
**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile` [1-100](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh` [105-200](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/manifest.yaml` [20-28]()

## Container Lifecycle and Entrypoint

The sandbox lifecycle is managed by `start.sh`, which serves as the `nemoclaw-start` entrypoint. It performs critical security initialization before launching the agent.

### Initialization Sequence
1.  **Security Hardening:** The script drops unnecessary Linux capabilities using `drop_capabilities` from the shared `sandbox-init.sh` library and sets process limits (`ulimit -u 512`) to prevent fork bombs [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:30-36, 78-80]().
2.  **Config Integrity Verification:** It verifies the HMAC-SHA256 hash of the immutable configuration directory (`/sandbox/.hermes`) against a pre-calculated hash file [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:119-124]().
3.  **Writable Overlay:** Verified config is copied to `/sandbox/.hermes-data`, a writable directory where Hermes stores its `state.db`, `memories`, and `sessions` [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:7-10, 127-132]().
4.  **Placeholder Refresh:** The `refresh-placeholders.py` utility replaces `openshell:resolve:env:*` strings in the `.env` file with actual credentials provided by the OpenShell runtime environment [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:134-158]().

**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh` [1-160](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/manifest.yaml` [38-62]()

## Multi-Stage Build and Runtime Contract

The `Dockerfile` uses a multi-stage build to ensure a minimal, hardened production image.

| Stage | Purpose | Key Actions |
| :--- | :--- | :--- |
| `hermes-builder` | Build native runtime | Pins Hermes to `0.20.0`, applies `hermes-dependencies.patch` to force `nemo-relay==0.7.2`, and builds TUI/Web assets [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile:21-84](). |
| `Main Sandbox` | Hardened runtime | Copies `/opt/hermes` from builder, removes build tools (gcc, make), and registers trusted CA certificates [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile:86-118](). |

### TUI Runtime Contract
The sandbox is optimized for a headless environment but retains a TUI (Terminal User Interface) bundle at `/opt/hermes/ui-tui/dist/entry.js`. The `start.sh` script exports `HERMES_TUI_DIR` and `HERMES_DISABLE_LAZY_INSTALLS=1` to ensure all required components are available offline within the sandbox [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_tui_runtime_contract.py:12-24]().

**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/Dockerfile` [1-100](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/tests/test_tui_runtime_contract.py` [1-25]()

## Sidecar Bridges and Integrations

### ATIF Bridge (`atif-bridge.py`)
The `atif-bridge.py` sidecar is a protocol shim that enables the agent to export trajectories to the host-side relay.
*   **Purpose:** Works around a `rustls` limitation in the native NeMo Relay where it cannot validate OpenShell's L7 proxy MITM certificates due to missing `serverAuth` EKU [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py:4-15]().
*   **Security:** The bridge is credential-opaque; it does not read the `ATIF_RELAY_AUTH_TOKEN`. Instead, it forwards the placeholder header, which is resolved by the OpenShell gateway during egress [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py:17-23]().

### Outlook Bridge (`outlook-bridge.py`)
Enables the agent to interact with Microsoft Graph API for email search and replies. It handles the specific communication between the agent and the Graph API [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/manifest.yaml:79]().

### NeMo Relay Plugin
Hermes integrates NeMo Relay as an in-process plugin. The `plugins.toml` configuration defines the `atif` storage component, which targets the local `atif-bridge` at `http://127.0.0.1:18444/atif` [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:44-47]().

**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py` [1-130](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh` [41-47]()

## Slack Compatibility and Diagnostics

The sandbox includes narrow compatibility patches for the Slack runtime, located in `sitecustomize.py`. These patches add two features:
1.  **Slash Command Support:** A catch-all slash-command reply for workspace-specific command names [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/sitecustomize.py:5-9]().
2.  **Interactive Choices:** One-tap Block Kit choices for Hermes clarification prompts [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/sitecustomize.py:61-118]().

### Slack Delivery Diagnostic
The `slack_delivery_diagnostic.py` script provides a guided, operator-originated diagnostic to verify the full Slack delivery path, from Socket Mode connection to outbound response [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:4-43]().

| Stage | Description |
| :--- | :--- |
| `socket_mode_connection` | Verifies the WebSocket connection to Slack [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:30](). |
| `inbound_event_receipt` | Confirms receipt of events from Slack [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:31](). |
| `hermes_dispatch` | Verifies the message reached the Hermes core [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:32](). |
| `inference` | Monitors LLM generation for the response [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:33](). |
| `outbound_response` | Confirms the response was sent back to Slack [examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py:34](). |

**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/patches/sitecustomize.py` [1-118](), `examples/recipes/nvidia/developer-community-chief-of-staff/scripts/slack_delivery_diagnostic.py` [1-66]()

## Security Implementation

The sandbox utilizes several layers of security:
1.  **Landlock:** The agent's file system access is restricted via Landlock (inherited from the OpenShell base image), making the root filesystem and `/sandbox/.hermes` read-only [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:7-15]().
2.  **L7 Proxy Egress:** All network traffic is forced through the OpenShell gateway. The `atif-bridge` uses `trust_env=True` to respect the `HTTPS_PROXY` injected by OpenShell [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py:109-115]().
3.  **Credential Isolation:** Real API keys for GitHub, Slack, and Outlook never enter the sandbox environment variables. They are stored as placeholders and substituted by the host-side gateway [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh:134-158]().
4.  **Leak Guard:** The `atif-bridge` includes a trip-wire check that fails the process if real ATIF credentials (`ATIF_RELAY_AUTH_TOKEN`) are found in the environment [examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py:82-94]().

**Sources:** `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/start.sh` [38-40](), `examples/recipes/nvidia/developer-community-chief-of-staff/agents/hermes/bridges/atif/atif-bridge.py` [82-123]()

---

