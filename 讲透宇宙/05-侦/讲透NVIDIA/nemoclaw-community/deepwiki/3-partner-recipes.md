<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nemoclaw-community · page 3 Partner Recipes · fetched 2026-10-26 -->

# Partner Recipes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/recipes/partners/bluetier/x402-payment-gate/README.md](examples/recipes/partners/bluetier/x402-payment-gate/README.md)
- [examples/recipes/partners/shrike/shrike-security/.env.example](examples/recipes/partners/shrike/shrike-security/.env.example)
- [examples/recipes/partners/shrike/shrike-security/.gitignore](examples/recipes/partners/shrike/shrike-security/.gitignore)
- [examples/recipes/partners/shrike/shrike-security/README.md](examples/recipes/partners/shrike/shrike-security/README.md)
- [examples/recipes/partners/shrike/shrike-security/agents.yaml](examples/recipes/partners/shrike/shrike-security/agents.yaml)
- [examples/recipes/partners/shrike/shrike-security/docs/verify-functionality.md](examples/recipes/partners/shrike/shrike-security/docs/verify-functionality.md)
- [examples/recipes/partners/shrike/shrike-security/plugin/.gitignore](examples/recipes/partners/shrike/shrike-security/plugin/.gitignore)
- [examples/recipes/partners/shrike/shrike-security/plugin/openclaw.plugin.json](examples/recipes/partners/shrike/shrike-security/plugin/openclaw.plugin.json)
- [examples/recipes/partners/shrike/shrike-security/plugin/package-lock.json](examples/recipes/partners/shrike/shrike-security/plugin/package-lock.json)
- [examples/recipes/partners/shrike/shrike-security/plugin/package.json](examples/recipes/partners/shrike/shrike-security/plugin/package.json)

</details>



Partner recipes represent contributions from the NemoClaw ecosystem that extend the core architecture with specialized security, financial, and operational patterns. These recipes leverage the **OpenShell v2 provider** model and the `before_tool_call` plugin architecture to enforce domain-specific constraints.

The primary patterns shared across these recipes include:
*   **Maker/Checker Boundaries**: Separating the intent generation (agent) from the execution/signing (host-side service).
*   **Interception Plugins**: Using `before_tool_call` to evaluate agent actions against external policy engines before execution.
*   **Scoped Egress**: Strict network policies that limit the agent's reach to specific partner APIs and internal relays.

### System Interconnectivity

The following diagram illustrates how partner-contributed components integrate with the NemoClaw sandbox and the OpenShell gateway.

**Partner Integration Architecture**
```mermaid
graph TD
    subgraph "Natural Language Space (Agent)"
        "AgentPersona"["Agent Persona (e.g., Retail Assistant)"]
    end

    subgraph "Code Entity Space (Sandbox)"
        "OpenShellPlugin"["before_tool_call Plugin"]
        "AgentSkill"["Skill (e.g., blackwall-payment-gate)"]
    end

    subgraph "Control Plane (Host)"
        "OpenShellGateway"["OpenShell Gateway"]
        "PartnerService"["Partner Verdict Service (e.g., Shrike Enforce Plane)"]
        "HumanRelease"["Human Approval Loopback"]
    end

    "AgentPersona" --> "AgentSkill"
    "AgentSkill" -- "Intercepted by" --> "OpenShellPlugin"
    "OpenShellPlugin" -- "Request Verdict" --> "PartnerService"
    "PartnerService" -- "ALLOW/BLOCK/WARN" --> "OpenShellPlugin"
    "OpenShellPlugin" -- "If approved" --> "OpenShellGateway"
    "OpenShellGateway" -- "External API Call" --> "Internet"
    "PartnerService" -- "Escalate" --> "HumanRelease"
```
**Sources:** [examples/recipes/partners/shrike/shrike-security/README.md:69-74](), [examples/recipes/partners/bluetier/x402-payment-gate/README.md:46-82]()

---

## BlueTier x402 Payment Gate

The **BlueTier x402 Payment Gate** recipe implements a financial "Maker/Checker" architecture. In this model, the sandboxed agent (the "Maker") is prohibited from signing or settling transactions directly. Instead, it can only submit payment intents to a host-side service (the "Checker") [examples/recipes/partners/bluetier/x402-payment-gate/README.md:5-9]().

Key features include:
*   **Blackwall Verdict Service**: Evaluates intents for counterparty reputation, price anomalies, and OFAC sanctions, returning `GO`, `HOLD`, or `STOP` verdicts [examples/recipes/partners/bluetier/x402-payment-gate/README.md:10-12]().
*   **Denied-Edge Network Policy**: The sandbox is restricted from accessing any payment rails directly; it can only communicate with the Blackwall relay via `host.openshell.internal` [examples/recipes/partners/bluetier/x402-payment-gate/README.md:84-92]().
*   **Human Approval Loopback**: A state machine that allows a named human operator to release `HELD` intents using a host-side token [examples/recipes/partners/bluetier/x402-payment-gate/README.md:119-122]().

For details, see [BlueTier x402 Payment Gate](#3.1).

**Sources:** [examples/recipes/partners/bluetier/x402-payment-gate/README.md:1-22](), [examples/recipes/partners/bluetier/x402-payment-gate/README.md:104-129]()

---

## Shrike Security Action Governance

The **Shrike Security** recipe focuses on fine-grained action governance using a `before_tool_call` interception plugin [examples/recipes/partners/shrike/shrike-security/README.md:7-10](). This allows the system to evaluate every tool call against the **Shrike Enforce Plane** before the tool is executed.

Key features include:
*   **Verdict Lifecycle**: Maps server-side verdicts (`allow`, `warn`, `require_approval`, `block`) to OpenClaw decisions [examples/recipes/partners/shrike/shrike-security/README.md:76-81]().
*   **Credential Injection**: Uses the `providers/shrike.yaml` OpenShell v2 provider to resolve the `SHRIKE_API_KEY` placeholder on egress [examples/recipes/partners/shrike/shrike-security/README.md:82-84]().
*   **Config-Integrity Shield**: Recommends the `image` install path to bake the plugin into the sandbox at build time, avoiding conflicts with the gateway's `.config-hash` integrity guard [examples/recipes/partners/shrike/shrike-security/README.md:103-119]().

For details, see [Shrike Security Action Governance](#3.2).

**Sources:** [examples/recipes/partners/shrike/shrike-security/README.md:5-23](), [examples/recipes/partners/shrike/shrike-security/README.md:76-89](), [examples/recipes/partners/shrike/shrike-security/plugin/openclaw.plugin.json:1-14]()

---

## HPE Retail Assistant and Tavily Watchtower

These recipes focus on operational automation and scheduled information gathering, demonstrating how NemoClaw can be integrated into existing enterprise infrastructure and cron-based workflows.

### HPE Retail Assistant
A Telegram-native, role-aware retail operations assistant. It utilizes a full-stack deployment including **FastAPI**, **PostgreSQL**, and **Docker Compose/Helm** to provide a production-ready interface for retail staff.

### Tavily Watchtower
A monitoring tool that runs scheduled, cited web searches. It features persistent deduplication to ensure the agent only reports new information and uses the **Tavily Search/Extract** API for high-fidelity data retrieval.

For details, see [HPE Retail Assistant and Tavily Watchtower](#3.3).

**Sources:** [examples/README.md:23-25]()

---

## Shared Patterns Table

| Pattern | BlueTier | Shrike | HPE/Tavily |
| :--- | :--- | :--- | :--- |
| **Interception** | Intent-based (Skill level) | Tool-call based (Plugin level) | Event-based (API level) |
| **Policy Enforcement** | External Verdict Service | 9-Layer Enforce Plane | Role-aware RBAC |
| **Persistence** | Transaction Ledger | Audit Logs | PostgreSQL / Dedupe Store |
| **Deployment** | Docker Compose | OpenShell Plugin | Helm / Docker Compose |

**Sources:** [examples/recipes/partners/shrike/shrike-security/README.md:76-89](), [examples/recipes/partners/bluetier/x402-payment-gate/README.md:46-82]()

---

