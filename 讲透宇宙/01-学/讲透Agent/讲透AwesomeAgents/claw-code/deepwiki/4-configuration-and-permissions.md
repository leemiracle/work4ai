<!-- source: DeepWiki mcp.deepwiki.com · repo ultraworkers/claw-code · page 4 Configuration and Permissions · fetched 2026-10-26 -->

# Configuration and Permissions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rust/crates/runtime/src/approval_tokens.rs](rust/crates/runtime/src/approval_tokens.rs)
- [rust/crates/runtime/src/config.rs](rust/crates/runtime/src/config.rs)
- [rust/crates/runtime/src/config_validate.rs](rust/crates/runtime/src/config_validate.rs)
- [rust/crates/runtime/src/g004_conformance.rs](rust/crates/runtime/src/g004_conformance.rs)
- [rust/crates/runtime/src/lib.rs](rust/crates/runtime/src/lib.rs)
- [rust/crates/runtime/src/permissions.rs](rust/crates/runtime/src/permissions.rs)
- [rust/crates/runtime/tests/fixtures/g004_contract_bundle.valid.json](rust/crates/runtime/tests/fixtures/g004_contract_bundle.valid.json)
- [rust/crates/runtime/tests/g004_conformance.rs](rust/crates/runtime/tests/g004_conformance.rs)
- [rust/crates/rusty-claude-cli/src/setup_wizard.rs](rust/crates/rusty-claude-cli/src/setup_wizard.rs)

</details>



This page provides a high-level overview of the configuration and security systems within Claw Code. The codebase utilizes a hierarchical configuration system to manage runtime behavior and a strict permission-gating model to ensure safe tool execution. These systems are shared across the production Rust implementation and the Python porting workspace to maintain behavioral parity.

## System Architecture Overview

The configuration system bridges user-defined settings with the internal execution engine. It handles everything from API credentials and OAuth flows to the fine-grained enabling of features like MCP (Model Context Protocol) servers and sandboxing.

### Data Flow and Configuration Hierarchy
The system resolves settings from multiple sources, following a `ConfigSource` hierarchy of `User`, `Project`, and `Local` [rust/crates/runtime/src/config.rs:44-48](). This allows for global defaults that can be overridden by specific project requirements. The `ConfigLoader` handles discovery across these scopes [rust/crates/runtime/src/config.rs:70]().

Title: Configuration Resolution and Permission Gating
```mermaid
graph TD
    subgraph "Natural Language Space"
        "User Intent" --> "CLI Flags"
        "User Intent" --> "settings.json"
        "User Intent" --> "CLAW.md"
    end

    subgraph "Code Entity Space"
        "CLI Flags" --> ["args::Cli"]
        "settings.json" --> ["runtime::ConfigLoader"]
        "CLAW.md" --> ["runtime::ProjectContext"]
        
        ["args::Cli"] --> ["runtime::RuntimeConfig"]
        ["runtime::ConfigLoader"] --> ["runtime::RuntimeConfig"]
        
        ["runtime::RuntimeConfig"] --> ["runtime::ConversationRuntime"]
        ["runtime::ProjectContext"] --> ["runtime::SystemPromptBuilder"]
        
        ["runtime::RuntimeConfig"] -- "contains" --> ["runtime::ResolvedPermissionMode"]
        ["runtime::ResolvedPermissionMode"] --> ["runtime::PermissionPolicy"]
        
        ["runtime::ConversationRuntime"] -- "Gated By" --> ["runtime::PermissionPolicy"]
    end
```
Sources: [rust/crates/runtime/src/config.rs:44-48](), [rust/crates/runtime/src/config.rs:66-71](), [rust/crates/runtime/src/config.rs:151-166](), [rust/crates/runtime/src/prompt.rs:146-150](), [rust/crates/runtime/src/permissions.rs:98-109]()

---

## Runtime Configuration (Rust)

The Rust implementation centers around the `RuntimeConfig` struct [rust/crates/runtime/src/config.rs:66-71](), which aggregates all operational parameters for a session. This includes feature flags, plugin settings, and the configuration for external MCP servers.

Key components include:
*   **ConfigLoader**: Manages the discovery and merging of configuration files from the current working directory and the user's config home [rust/crates/runtime/src/config.rs:70]().
*   **RuntimeFeatureConfig**: A structured view of enabled features, including `hooks`, `plugins`, `mcp`, `oauth`, and `sandbox` settings [rust/crates/runtime/src/config.rs:150-166]().
*   **McpConfigCollection**: Defines the set of Model Context Protocol servers the runtime should connect to, supporting various transport types such as `Stdio`, `SSE`, and `WebSocket` [rust/crates/runtime/src/config.rs:71-73]().
*   **Validation**: The `ConfigDiagnostic` system ensures `settings.json` adheres to the expected schema (advertised as `CLAW_SETTINGS_SCHEMA_NAME`) [rust/crates/runtime/src/config.rs:40](), providing warnings for unknown keys, wrong types, or deprecated fields [rust/crates/runtime/src/config_validate.rs:9-29]().
*   **Setup Wizard**: The `run_setup_wizard` function provides an interactive CLI flow to configure providers (Anthropic, OpenAI, xAI, DashScope), API keys, and models, persisting them to `~/.claw/settings.json` [rust/crates/rusty-claude-cli/src/setup_wizard.rs:39-72]().

For details on schema definitions and the config source hierarchy, see [Runtime Configuration (Rust)](#4.1).

**Sources:** [rust/crates/runtime/src/config.rs:40-166](), [rust/crates/runtime/src/config_validate.rs:9-29](), [rust/crates/rusty-claude-cli/src/setup_wizard.rs:39-72]()

---

## Permission Modes and OAuth

Claw Code implements a "Safety First" approach to tool execution. Every tool call requested by the LLM is passed through a `PermissionPolicy` which evaluates the request against the active `PermissionMode` [rust/crates/runtime/src/permissions.rs:98-109]().

### Permission Modes and Policies
The system supports several levels of access via the `PermissionMode` enum [rust/crates/runtime/src/permissions.rs:8-15]():
1.  **ReadOnly**: Only allows tools that do not modify state.
2.  **WorkspaceWrite**: Allows modifications within the project workspace.
3.  **DangerFullAccess**: Allows unrestricted execution.
4.  **Prompt**: Requires interactive approval via a `PermissionPrompter` [rust/crates/runtime/src/permissions.rs:86-88]().
5.  **Allow**: Unconditional access (used for internal/safe tools).

Configuration can define granular `allow`, `deny`, and `ask` rules through the `RuntimePermissionRuleConfig` [rust/crates/runtime/src/permissions.rs:136-159](). Tools can also be explicitly blocked using the `denied_tools` list, which is checked before rule-based evaluation [rust/crates/runtime/src/permissions.rs:105-108](), [rust/crates/runtime/src/permissions.rs:196-200]().

### Authentication and OAuth
Claw Code supports the **OAuth2 PKCE flow** for secure provider authentication. The system manages `OAuthTokenSet` (access/refresh tokens) [rust/crates/runtime/src/oauth.rs:130](), PKCE challenge generation using S256 [rust/crates/runtime/src/oauth.rs:127-131](), and secure storage of credentials [rust/crates/runtime/src/oauth.rs:129]().

Title: Authentication and Tool Permission Flow
```mermaid
graph LR
    subgraph "Auth Flow"
        ["config::OAuthConfig"] --> ["oauth::PkceCodePair"]
        ["oauth::PkceCodePair"] --> ["oauth::OAuthAuthorizationRequest"]
        ["oauth::OAuthTokenSet"] -- "Refresh" --> ["oauth::OAuthRefreshRequest"]
    end

    subgraph "Permission Gating"
        ["runtime::RuntimeFeatureConfig"] --> ["runtime::ResolvedPermissionMode"]
        ["runtime::RuntimeFeatureConfig"] --> ["runtime::RuntimePermissionRuleConfig"]
        ["runtime::ResolvedPermissionMode"] --> ["permissions::PermissionPolicy"]
        ["runtime::RuntimePermissionRuleConfig"] --> ["permissions::PermissionPolicy"]
        ["permissions::PermissionPolicy"] -- "Consults" --> ["permissions::PermissionPrompter"]
    end
```
Sources: [rust/crates/runtime/src/oauth.rs:126-132](), [rust/crates/runtime/src/config.rs:150-166](), [rust/crates/runtime/src/permissions.rs:8-15](), [rust/crates/runtime/src/permissions.rs:98-109]()

For details on credential storage, the `PermissionPrompter` trait, and PKCE implementation, see [Permission Modes and OAuth](#4.2).

---

## System Prompt Context Integration

The configuration system influences the `SystemPromptBuilder`. It injects `ProjectContext` (including `CLAW.md` instructions and `GitContext`) and the `RuntimeConfig` directly into the instructions provided to the LLM [rust/crates/runtime/src/prompt.rs:146-150]().

### Policy Exceptions and G004 Conformance
The system includes advanced policy management features:
*   **Approval Tokens**: The `ApprovalTokenLedger` manages machine-readable policy exception scopes (`ApprovalScope`), allowing for auditable delegations of authority and replay protection [rust/crates/runtime/src/approval_tokens.rs:3-10](), [rust/crates/runtime/src/approval_tokens.rs:207-210]().
*   **G004 Conformance**: A machine-checkable harness validates event/report contract bundles (`validate_g004_contract_bundle`) to ensure they meet strict schema and provenance requirements, including sequence validation and terminal event fingerprints [rust/crates/runtime/src/g004_conformance.rs:42-51](), [rust/crates/runtime/src/g004_conformance.rs:106-114]().

| Entity | Responsibility | Source |
| :--- | :--- | :--- |
| `RuntimeConfig` | Fully merged settings including plugins, MCP, and model aliases. | [rust/crates/runtime/src/config.rs:66-71]() |
| `PermissionMode` | Enum defining the strictness of tool execution gating. | [rust/crates/runtime/src/permissions.rs:8-15]() |
| `RuntimeHookConfig` | Lists of commands to run at specific tool lifecycle stages. | [rust/crates/runtime/src/lib.rs:74]() |
| `ApprovalTokenGrant` | Auditable record of a policy exception granted to an actor. | [rust/crates/runtime/src/approval_tokens.rs:118-129]() |
| `ProjectContext` | Discovered workspace state (Git, instruction files, date). | [rust/crates/runtime/src/prompt.rs:148]() |

**Sources:** [rust/crates/runtime/src/config.rs:66-71](), [rust/crates/runtime/src/permissions.rs:8-15](), [rust/crates/runtime/src/approval_tokens.rs:118-210](), [rust/crates/runtime/src/g004_conformance.rs:42-51](), [rust/crates/runtime/src/prompt.rs:146-150]()

---

