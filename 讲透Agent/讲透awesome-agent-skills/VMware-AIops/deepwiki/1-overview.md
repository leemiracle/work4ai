<!-- source: DeepWiki mcp.deepwiki.com · repo zw008/VMware-AIops · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-CN.md](README-CN.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This document introduces the VMware AIops system, its architectural design, and core components. For installation instructions, see [Getting Started](#2). For detailed operational guides, see [Operations Guide](#7).

## Purpose and Scope

VMware AIops is an AI-powered automation framework for VMware vSphere infrastructure management. It enables AI coding assistants and agents to perform monitoring and operational tasks on vCenter Server and ESXi hosts through natural language instructions. The system provides both read-only monitoring capabilities and full lifecycle management of virtual machines, with built-in safety mechanisms including double confirmation, dry-run preview, and comprehensive audit logging.

The system solves the token efficiency problem for local AI models while maintaining structured automation capabilities for cloud-based agents through a dual-mode architecture (CLI and MCP), and addresses production safety concerns through a dual-skill architecture (monitor and aiops).

Sources: [README.md:1-967](), [README-CN.md:1-617]()

## System Architecture Overview

VMware AIops operates as a Python-based middleware layer between AI agents and VMware infrastructure, exposing operations through two distinct interfaces optimized for different use cases.

```mermaid
graph TB
    subgraph "AI Agent Layer"
        NL["Natural Language Input<br/>from User"]
        Claude["Claude Code<br/>Anthropic Claude"]
        Gemini["Gemini CLI<br/>Google Gemini"]
        Aider["Aider<br/>Any LLM"]
        Ollama["Local Models<br/>Ollama/Qwen"]
    end
    
    subgraph "Integration Layer"
        SKILL["SKILL.md<br/>plugins/vmware-ops/skills/"]
        AGENTS["AGENTS.md<br/>codex-skill/"]
        MCPClient["MCP Client Config<br/>claude_desktop_config.json"]
    end
    
    subgraph "VMware AIops Core"
        CLIEntry["cli.py<br/>typer.Typer app<br/>Entry: vmware-aiops"]
        MCPEntry["mcp_server/server.py<br/>FastMCP server<br/>Entry: vmware-aiops-mcp"]
    end
    
    subgraph "Operations Layer"
        ConnMgr["connection.py<br/>ConnectionManager<br/>Multi-target session pool"]
        Config["config.py<br/>load_config()<br/>~/.vmware-aiops/config.yaml"]
        Audit["notify/audit.py<br/>AuditLogger.log()<br/>~/.vmware-aiops/audit.log"]
    end
    
    subgraph "Ops Modules - vmware_aiops/ops/"
        Inventory["inventory.py<br/>list_vms()<br/>list_hosts()"]
        Health["health.py<br/>get_active_alarms()<br/>get_recent_events()"]
        Lifecycle["vm_lifecycle.py<br/>power_on_vm()<br/>create_vm()<br/>delete_vm()"]
        Deploy["vm_deploy.py<br/>deploy_from_ova()<br/>deploy_from_template()"]
    end
    
    subgraph "VMware Infrastructure"
        PyVmomi["pyVmomi Library<br/>ServiceInstance<br/>vim.VirtualMachine<br/>vim.HostSystem"]
        vCenter["vCenter Server<br/>SOAP API<br/>Port 443"]
        ESXi["ESXi Hosts<br/>SOAP API"]
    end
    
    NL --> Claude
    NL --> Gemini
    NL --> Aider
    NL --> Ollama
    
    Claude --> SKILL
    Gemini --> SKILL
    Aider --> AGENTS
    Ollama --> AGENTS
    
    SKILL --> CLIEntry
    AGENTS --> CLIEntry
    MCPClient --> MCPEntry
    
    CLIEntry --> ConnMgr
    MCPEntry --> ConnMgr
    CLIEntry --> Audit
    MCPEntry --> Audit
    
    ConnMgr --> Config
    ConnMgr --> PyVmomi
    
    CLIEntry --> Inventory
    CLIEntry --> Health
    CLIEntry --> Lifecycle
    CLIEntry --> Deploy
    
    MCPEntry --> Inventory
    MCPEntry --> Health
    MCPEntry --> Lifecycle
    MCPEntry --> Deploy
    
    Inventory --> ConnMgr
    Health --> ConnMgr
    Lifecycle --> ConnMgr
    Deploy --> ConnMgr
    
    PyVmomi --> vCenter
    PyVmomi --> ESXi
```

**System Architecture: Natural Language to vSphere API**

The architecture consists of five layers:

1. **AI Agent Layer**: Natural language input processed by various AI platforms (Claude, Gemini, Aider, local models)
2. **Integration Layer**: Platform-specific documentation files that teach AI agents how to invoke VMware AIops
3. **Core Layer**: Dual entry points - `cli.py` for shell-based invocation (~2K token context) and `mcp_server/server.py` for structured tool calling (~10K token context)
4. **Operations Layer**: Shared infrastructure including `ConnectionManager` for pyVmomi session pooling, configuration management, and audit logging
5. **VMware Infrastructure**: Direct SOAP API communication via pyVmomi to vCenter Server or standalone ESXi hosts

Sources: [README.md:68-82](), [vmware_aiops/cli.py](), [vmware_aiops/connection.py](), [vmware_aiops/config.py](), [mcp_server/server.py]()

## Dual-Mode Architecture: CLI vs MCP

VMware AIops provides two operational modes with different token efficiency and automation trade-offs.

```mermaid
graph LR
    subgraph "CLI Mode - Token Efficient"
        CLIDoc["SKILL.md<br/>2,095 tokens"]
        CLIInvoke["Bash Tool<br/>Execute: vmware-aiops"]
        CLIParse["Parse stdout<br/>Human-readable text"]
    end
    
    subgraph "MCP Mode - Structured Automation"
        MCPDoc["43 Tool Schemas<br/>~10,000 tokens"]
        MCPInvoke["MCP Protocol<br/>JSON-RPC 2.0"]
        MCPParse["Structured JSON<br/>Type-safe response"]
    end
    
    subgraph "Shared Backend"
        OpsModules["ops/ modules<br/>inventory.py<br/>health.py<br/>vm_lifecycle.py<br/>vm_deploy.py"]
    end
    
    CLIDoc --> CLIInvoke
    CLIInvoke --> OpsModules
    OpsModules --> CLIParse
    
    MCPDoc --> MCPInvoke
    MCPInvoke --> OpsModules
    OpsModules --> MCPParse
```

**CLI vs MCP Mode Comparison**

| Aspect | CLI Mode | MCP Mode |
|--------|----------|----------|
| **Context Size** | ~2K tokens (SKILL.md) | ~10K tokens (43 tool schemas) |
| **Entry Point** | `vmware_aiops/cli.py:app` | `mcp_server/server.py:main()` |
| **Invocation** | Shell command execution | JSON-RPC tool calls |
| **Best For** | Local models <32B params, cost optimization | Cloud LLMs, automated pipelines |
| **Output Format** | Human-readable text (stdout) | Structured JSON objects |
| **Documentation** | `plugins/vmware-ops/skills/vmware-aiops/SKILL.md`, `codex-skill/AGENTS.md` | MCP tool definitions in `mcp_server/server.py` |
| **Integration** | Claude Code, Gemini, Codex, Aider, Continue, Trae, Kimi | Claude Desktop, Cursor, VS Code Copilot, Goose, LocalCowork |

The CLI mode minimizes token consumption by providing a single Bash execution tool with comprehensive Markdown documentation. AI agents read the documentation once and invoke shell commands. This is critical for local models like Qwen 2.5 Coder 7B-32B which struggle with large context windows.

The MCP mode provides 43 individual tools with JSON schema definitions, enabling type-safe parameter passing and structured responses. This eliminates shell parsing ambiguity and enables reliable agent chaining in automated workflows.

Sources: [README.md:57-66](), [plugins/vmware-ops/skills/vmware-aiops/SKILL.md](), [mcp_server/server.py]()

## Dual-Skill Architecture: Safety Through Code Separation

VMware AIops provides two skill variants with different operational capabilities and safety guarantees.

```mermaid
graph TB
    subgraph "vmware-monitor Skill"
        MonitorSkill["plugins/vmware-ops/skills/<br/>vmware-monitor/SKILL.md"]
        MonitorOps["Read-Only Operations"]
        MonitorFuncs["list_vms()<br/>list_hosts()<br/>get_active_alarms()<br/>get_recent_events()"]
        MonitorSafety["Code-level Safety:<br/>No delete_vm()<br/>No power_off_vm()<br/>No reconfigure_vm()"]
    end
    
    subgraph "vmware-aiops Skill"
        AiopsSkill["plugins/vmware-ops/skills/<br/>vmware-aiops/SKILL.md"]
        AiopsOps["Full Operations"]
        AiopsFuncs["All monitor functions +<br/>power_on_vm()<br/>delete_vm()<br/>create_vm()<br/>snapshot operations"]
        AiopsSafety["Runtime Safety:<br/>double_confirm()<br/>dry_run mode<br/>audit.log()"]
    end
    
    subgraph "Shared Implementation"
        OpsInventory["ops/inventory.py"]
        OpsHealth["ops/health.py"]
        OpsLifecycle["ops/vm_lifecycle.py"]
    end
    
    MonitorSkill --> MonitorOps
    MonitorOps --> MonitorFuncs
    MonitorFuncs --> MonitorSafety
    
    AiopsSkill --> AiopsOps
    AiopsOps --> AiopsFuncs
    AiopsFuncs --> AiopsSafety
    
    MonitorFuncs --> OpsInventory
    MonitorFuncs --> OpsHealth
    
    AiopsFuncs --> OpsInventory
    AiopsFuncs --> OpsHealth
    AiopsFuncs --> OpsLifecycle
```

**Dual-Skill Safety Architecture**

The system provides defense-in-depth safety through two distinct skill definitions:

**vmware-monitor**: Achieves safety through code-level enforcement. The SKILL.md documentation only exposes read-only commands like `inventory vms`, `health alarms`, and `health events`. Destructive operations like `vm delete` or `vm power-off` are documented as unavailable. This prevents AI agents from even attempting destructive operations.

**vmware-aiops**: Provides full operational capabilities including VM lifecycle management (`vm_lifecycle.py:create_vm()`, `vm_lifecycle.py:delete_vm()`, `vm_lifecycle.py:power_off_vm()`), but enforces safety through runtime controls:

- **Double Confirmation**: All destructive operations call `cli.py:double_confirm()` which requires two sequential user confirmations with no bypass flags
- **Dry-Run Preview**: `--dry-run` flag on destructive commands shows exact pyVmomi API calls without execution
- **Input Validation**: Parameter range checking in `vm_lifecycle.py` (CPU: 1-128, Memory: 128-1048576 MB, Disk: 1-65536 GB)
- **Audit Logging**: Every operation logged to `~/.vmware-aiops/audit.log` via `notify/audit.py:AuditLogger.log()` including before/after state and rejection reasons

Deployment strategy: Use **vmware-monitor** skill in production environments where only observability is needed. Use **vmware-aiops** skill in development/test environments where full automation is required with audit trails.

Sources: [README.md:8-8](), [README-CN.md:8-13](), [plugins/vmware-ops/skills/vmware-monitor/SKILL.md](), [plugins/vmware-ops/skills/vmware-aiops/SKILL.md](), [vmware_aiops/cli.py](), [vmware_aiops/ops/vm_lifecycle.py]()

## Core Components and Code Structure

The system follows a layered architecture with clear separation between entry points, business logic, and infrastructure access.

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["cli.py<br/>@app.command()<br/>typer decorators"]
        MCP["mcp_server/server.py<br/>@mcp.tool()<br/>FastMCP decorators"]
    end
    
    subgraph "Configuration Management"
        ConfigLoader["config.py<br/>load_config()<br/>ConfigManager"]
        ConfigFile["~/.vmware-aiops/<br/>config.yaml"]
        EnvFile["~/.vmware-aiops/<br/>.env"]
    end
    
    subgraph "Connection Management"
        ConnMgr["connection.py<br/>ConnectionManager"]
        ConnGet["get_connection()<br/>target_name"]
        ConnCache["_connections: dict<br/>session pool"]
    end
    
    subgraph "Operations Modules"
        Inv["inventory.py<br/>list_vms()<br/>list_hosts()<br/>list_datastores()"]
        Hlth["health.py<br/>get_active_alarms()<br/>get_recent_events()<br/>get_host_sensors()"]
        Life["vm_lifecycle.py<br/>power_on_vm()<br/>create_vm()<br/>delete_vm()<br/>snapshot_create()"]
        Depl["vm_deploy.py<br/>deploy_from_ova()<br/>deploy_from_template()<br/>deploy_linked_clone()"]
        Guest["guest_ops.py<br/>guest_execute()<br/>guest_upload()<br/>guest_download()"]
        Browser["datastore_browser.py<br/>browse_datastore()<br/>scan_for_images()"]
    end
    
    subgraph "Background Services"
        Scanner["scanner/scanner.py<br/>scan_targets()<br/>APScheduler"]
        Notifier["notify/notifier.py<br/>NotificationManager<br/>send_webhook()"]
        Audit["notify/audit.py<br/>AuditLogger<br/>log()"]
    end
    
    subgraph "VMware API"
        PyVmomi["pyVmomi<br/>ServiceInstance<br/>vim objects"]
        SOAP["vSphere SOAP API<br/>Port 443"]
    end
    
    CLI --> ConfigLoader
    MCP --> ConfigLoader
    
    ConfigLoader --> ConfigFile
    ConfigLoader --> EnvFile
    
    CLI --> ConnMgr
    MCP --> ConnMgr
    
    ConnMgr --> ConnGet
    ConnGet --> ConnCache
    ConnMgr --> ConfigLoader
    
    CLI --> Inv
    CLI --> Hlth
    CLI --> Life
    CLI --> Depl
    CLI --> Guest
    CLI --> Browser
    
    MCP --> Inv
    MCP --> Hlth
    MCP --> Life
    MCP --> Depl
    MCP --> Guest
    MCP --> Browser
    
    Inv --> ConnMgr
    Hlth --> ConnMgr
    Life --> ConnMgr
    Depl --> ConnMgr
    Guest --> ConnMgr
    Browser --> ConnMgr
    
    Scanner --> ConnMgr
    Scanner --> Notifier
    Scanner --> Audit
    
    Life --> Audit
    Depl --> Audit
    
    ConnMgr --> PyVmomi
    PyVmomi --> SOAP
```

**Component Hierarchy and Dependencies**

### Entry Points

Two independent entry points share the same backend:

- **CLI Mode**: `vmware_aiops/cli.py` - Typer-based command-line application, entry point `vmware-aiops` defined in `pyproject.toml:32`
- **MCP Mode**: `mcp_server/server.py` - FastMCP server using stdio transport, entry point `vmware-aiops-mcp` defined in `pyproject.toml:33`

### Configuration and Connection Management

- **config.py**: `load_config()` reads `~/.vmware-aiops/config.yaml` and `~/.vmware-aiops/.env`, returns `ConfigManager` object with target definitions
- **connection.py**: `ConnectionManager` maintains a session pool (`_connections` dictionary) to avoid repeated authentication. `get_connection(target_name)` returns a pyVmomi `ServiceInstance` for the specified target

### Operations Modules (vmware_aiops/ops/)

All operations modules are stateless functions that accept a `ServiceInstance` and return results:

- **inventory.py**: `list_vms(si, filters)`, `list_hosts(si)`, `list_datastores(si)`, `list_clusters(si)` - Query vSphere inventory
- **health.py**: `get_active_alarms(si)`, `get_recent_events(si, hours, severity)`, `get_host_sensors(si, host)` - Monitoring and health checks
- **vm_lifecycle.py**: `power_on_vm(si, vm_name)`, `create_vm(si, name, cpu, memory, disk)`, `delete_vm(si, vm_name)`, `snapshot_create(si, vm_name, snapshot_name)` - VM lifecycle operations
- **vm_deploy.py**: `deploy_from_ova(si, ova_path, vm_name)`, `deploy_from_template(si, template_name, vm_name)`, `deploy_linked_clone(si, source_vm, snapshot, new_name)` - Deployment operations
- **guest_ops.py**: `guest_execute(si, vm_name, cmd, args, user, password)`, `guest_upload(si, vm_name, local_path, guest_path)` - Guest OS operations (requires VMware Tools)
- **datastore_browser.py**: `browse_datastore(si, datastore_name, path)`, `scan_for_images(si)` - Datastore file browsing

### Background Services

- **scanner/scanner.py**: APScheduler-based daemon that periodically calls `scan_targets()` to check alarms, events, and host logs across all configured targets
- **notify/notifier.py**: `NotificationManager.send_webhook()` sends JSON payloads to configured webhook URLs
- **notify/audit.py**: `AuditLogger.log(operation, resource, params, result)` writes JSONL entries to `~/.vmware-aiops/audit.log`

Sources: [vmware_aiops/cli.py](), [mcp_server/server.py](), [vmware_aiops/config.py](), [vmware_aiops/connection.py](), [vmware_aiops/ops/inventory.py](), [vmware_aiops/ops/health.py](), [vmware_aiops/ops/vm_lifecycle.py](), [vmware_aiops/ops/vm_deploy.py](), [vmware_aiops/ops/guest_ops.py](), [vmware_aiops/ops/datastore_browser.py](), [vmware_aiops/scanner/scanner.py](), [vmware_aiops/notify/notifier.py](), [vmware_aiops/notify/audit.py](), [pyproject.toml:31-33]()

## AI Platform Integration Ecosystem

VMware AIops integrates with 10+ AI platforms through four distinct integration patterns.

```mermaid
graph TB
    subgraph "Pattern 1: Native Plugin System"
        ClaudeCode["Claude Code"]
        ClaudeMarket[".claude-plugin/marketplace.json"]
        ClaudePlugin["plugins/vmware-ops/<br/>.claude-plugin/plugin.json"]
        ClaudeSkills["skills/vmware-aiops/SKILL.md<br/>skills/vmware-monitor/SKILL.md"]
    end
    
    subgraph "Pattern 2: Extension System"
        GeminiCLI["Gemini CLI"]
        GeminiExt["gemini-extension/<br/>gemini-extension.json"]
        GeminiDoc["gemini-extension/GEMINI.md"]
    end
    
    subgraph "Pattern 3: Convention Files"
        Codex["OpenAI Codex CLI"]
        Aider["Aider"]
        Continue["Continue CLI"]
        Trae["Trae IDE"]
        Kimi["Kimi Code CLI"]
        ConvFile["codex-skill/AGENTS.md<br/>trae-rules/project_rules.md<br/>kimi-skill/SKILL.md"]
    end
    
    subgraph "Pattern 4: MCP Protocol"
        ClaudeDesktop["Claude Desktop"]
        Cursor["Cursor"]
        VSCode["VS Code Copilot"]
        Goose["Goose"]
        LocalCowork["LocalCowork"]
        MCPConfig["claude_desktop_config.json<br/>examples/mcp-configs/"]
        MCPServer["mcp_server/server.py<br/>stdio transport"]
    end
    
    subgraph "Shared Backend"
        CLIBackend["vmware_aiops/cli.py"]
        MCPBackend["mcp_server/server.py"]
        OpsLayer["ops/ modules"]
    end
    
    ClaudeCode --> ClaudeMarket
    ClaudeMarket --> ClaudePlugin
    ClaudePlugin --> ClaudeSkills
    ClaudeSkills --> CLIBackend
    
    GeminiCLI --> GeminiExt
    GeminiExt --> GeminiDoc
    GeminiDoc --> CLIBackend
    
    Codex --> ConvFile
    Aider --> ConvFile
    Continue --> ConvFile
    Trae --> ConvFile
    Kimi --> ConvFile
    ConvFile --> CLIBackend
    
    ClaudeDesktop --> MCPConfig
    Cursor --> MCPConfig
    VSCode --> MCPConfig
    Goose --> MCPConfig
    LocalCowork --> MCPConfig
    MCPConfig --> MCPServer
    
    CLIBackend --> OpsLayer
    MCPBackend --> OpsLayer
```

**Four Integration Patterns**

### Pattern 1: Native Plugin System (Claude Code)

Claude Code discovers plugins through `.claude-plugin/marketplace.json` which points to `plugins/vmware-ops/.claude-plugin/plugin.json`. This plugin manifest defines two skills accessible via `/vmware-ops:vmware-aiops` and `/vmware-ops:vmware-monitor`. Each skill references a SKILL.md file in `plugins/vmware-ops/skills/` that provides comprehensive command documentation.

Installation: `/plugin marketplace add zw008/VMware-AIops` followed by `/plugin install vmware-ops`

### Pattern 2: Extension System (Gemini CLI)

Gemini CLI uses an extension manifest `gemini-extension/gemini-extension.json` that points to `gemini-extension/GEMINI.md`. The extension is installed via `gemini extensions install ./gemini-extension`.

### Pattern 3: Convention/Rule Files

Multiple AI tools (Codex, Aider, Continue, Trae, Kimi) support loading project-specific documentation files:

- **Codex/Aider/Continue**: Load `codex-skill/AGENTS.md` via `--conventions` flag or `~/.aider.conf.yml`
- **Trae IDE**: Reads `.trae/rules/project_rules.md` from `trae-rules/project_rules.md` template
- **Kimi Code CLI**: Loads `kimi-skill/SKILL.md` from `~/.kimi/skills/vmware-aiops/`

These files contain identical operational documentation but formatted for each platform's conventions system.

### Pattern 4: MCP Protocol

MCP-compatible clients (Claude Desktop, Cursor, VS Code Copilot, Goose, LocalCowork) connect to the MCP server via JSON-RPC over stdio. Configuration examples are in `examples/mcp-configs/` for each client. The server is started via `python -m mcp_server` or the `vmware-aiops-mcp` entry point.

MCP server configuration typically specifies:
```json
{
  "mcpServers": {
    "vmware-aiops": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "VMWARE_AIOPS_CONFIG": "/path/to/config.yaml"
      }
    }
  }
}
```

Sources: [.claude-plugin/marketplace.json](), [plugins/vmware-ops/.claude-plugin/plugin.json](), [plugins/vmware-ops/skills/vmware-aiops/SKILL.md](), [plugins/vmware-ops/skills/vmware-monitor/SKILL.md](), [gemini-extension/gemini-extension.json](), [gemini-extension/GEMINI.md](), [codex-skill/AGENTS.md](), [trae-rules/project_rules.md](), [kimi-skill/SKILL.md](), [examples/mcp-configs/](), [mcp_server/server.py](), [README.md:268-314]()

## Technology Stack and Dependencies

The system is built on Python 3.10+ with minimal external dependencies for maximum compatibility.

| Component | Technology | Purpose | Defined In |
|-----------|------------|---------|------------|
| **Core Language** | Python 3.10+ | System implementation | `pyproject.toml:11` |
| **vSphere API Client** | pyVmomi >=8.0.3.0 | SOAP API communication with vCenter/ESXi | `pyproject.toml:14` |
| **CLI Framework** | Typer >=0.12 | Command-line interface with double confirmation | `pyproject.toml:16` |
| **Terminal Output** | Rich >=13.0 | Formatted tables and progress indicators | `pyproject.toml:17` |
| **Configuration** | PyYAML >=24.0 | Parse config.yaml | `pyproject.toml:15` |
| **Environment Variables** | python-dotenv >=1.0 | Load .env credentials | `pyproject.toml:20` |
| **Task Scheduling** | APScheduler >=3.10 | Background scanning daemon | `pyproject.toml:18` |
| **HTTP Client** | httpx >=0.27 | Webhook notifications | `pyproject.toml:19` |
| **MCP Server** | mcp[cli] >=1.0 | Model Context Protocol implementation | `pyproject.toml:21` |
| **Build System** | Hatchling | PEP 517 build backend | `pyproject.toml:2` |
| **Testing** | pytest >=8.0, pytest-cov >=5.0 | Unit and integration tests | `pyproject.toml:26-27` |
| **Linting** | Ruff >=0.5 | Code formatting and linting | `pyproject.toml:28` |

### VMware API Coverage

The system interacts with VMware infrastructure exclusively through pyVmomi, which wraps the vSphere SOAP API:

- `vim.VirtualMachine` - VM lifecycle operations in `vm_lifecycle.py`
- `vim.HostSystem` - ESXi host information in `inventory.py` and `health.py`
- `vim.Datastore` - Storage management in `inventory.py` and `datastore_browser.py`
- `vim.host.DatastoreBrowser` - File browsing in `datastore_browser.py`
- `vim.OvfManager` - OVA deployment in `vm_deploy.py`
- `vim.ClusterComputeResource` - Cluster management in `inventory.py`
- `vim.alarm.AlarmManager` - Alarm retrieval in `health.py`
- `vim.event.EventManager` - Event queries in `health.py`

### Version Compatibility

pyVmomi performs automatic API version negotiation during SOAP handshake. The same codebase supports vSphere 6.5, 6.7, 7.0, and 8.0+ without modification. For vSphere 8.0, deprecated APIs like `CreateSnapshot_Task` are replaced with `CreateSnapshotEx_Task` in `vm_lifecycle.py`.

Sources: [pyproject.toml:1-48](), [README.md:84-93](), [README.md:934-949]()

## Safety and Audit Mechanisms

VMware AIops implements defense-in-depth safety through six layers of controls.

```mermaid
graph TB
    subgraph "User Request"
        Input["AI Agent Request<br/>e.g. delete-vm prod-db-01"]
    end
    
    subgraph "Layer 1: Input Validation"
        Validate["vm_lifecycle.py<br/>validate_vm_name()<br/>validate_cpu_count()<br/>validate_memory_mb()"]
        Ranges["CPU: 1-128<br/>Memory: 128-1048576 MB<br/>Disk: 1-65536 GB"]
    end
    
    subgraph "Layer 2: Pre-operation State Check"
        StateCheck["vm_lifecycle.py<br/>get_vm_by_name()<br/>Check power state"]
        Fail["Operation rejected<br/>if VM not found"]
    end
    
    subgraph "Layer 3: Dry-Run Mode"
        DryRun["--dry-run flag<br/>Print pyVmomi calls<br/>No execution"]
    end
    
    subgraph "Layer 4: Double Confirmation"
        Confirm1["cli.py:double_confirm()<br/>First prompt"]
        Confirm2["Second prompt<br/>No bypass flags"]
        Reject["Log rejection to<br/>audit.log"]
    end
    
    subgraph "Layer 5: Execution with State Capture"
        PreState["Capture before_state<br/>JSON snapshot"]
        Execute["Execute pyVmomi API<br/>wait_for_task()"]
        PostState["Capture after_state<br/>JSON snapshot"]
    end
    
    subgraph "Layer 6: Audit Logging"
        AuditLog["notify/audit.py<br/>AuditLogger.log()"]
        AuditFile["~/.vmware-aiops/audit.log<br/>JSONL format"]
        AuditFields["timestamp, target, operation<br/>resource, parameters<br/>before_state, after_state<br/>result, user, rejection_reason"]
    end
    
    Input --> Validate
    Validate --> Ranges
    Ranges --> StateCheck
    StateCheck --> Fail
    StateCheck --> DryRun
    
    DryRun --> Confirm1
    Confirm1 --> Confirm2
    Confirm2 --> Reject
    Confirm2 --> PreState
    
    PreState --> Execute
    Execute --> PostState
    PostState --> AuditLog
    
    Reject --> AuditLog
    Fail --> AuditLog
    
    AuditLog --> AuditFile
    AuditFile --> AuditFields
```

**Six-Layer Safety Architecture**

### Layer 1: Input Validation

All parameters are validated in `vmware_aiops/ops/vm_lifecycle.py` before vSphere API calls:
- VM name length and character restrictions
- CPU count: 1-128 cores
- Memory: 128 MB - 1,048,576 MB (1 TB)
- Disk size: 1-65,536 GB (64 TB)

Invalid inputs are rejected immediately with error messages.

### Layer 2: Pre-operation State Validation

Operations check resource existence and current state via `get_vm_by_name(si, vm_name)`. Power state is validated before operations (cannot delete a powered-on VM without `--force`, cannot power on an already running VM).

### Layer 3: Dry-Run Preview

The `--dry-run` flag on any destructive command shows the exact pyVmomi API calls that would be executed without making any changes. Example: `vmware-aiops vm delete my-vm --dry-run` displays the `vim.VirtualMachine.Destroy_Task()` call with target VM details.

### Layer 4: Double Confirmation

Destructive operations in `vmware_aiops/cli.py` call `double_confirm(operation_name)` which requires two sequential user confirmations:

1. First prompt: "Are you sure you want to {operation}? (yes/no)"
2. Second prompt: "Please confirm again: {operation} (yes/no)"

There are no bypass flags like `--force-confirm` or `--yes`. All rejections are logged to `audit.log` with `rejection_reason` field.

### Layer 5: State Capture and Task Synchronization

Before execution:
- Current VM state captured as JSON (power state, CPU, memory, disk, network)
- Stored in `before_state` field

After execution:
- pyVmomi tasks are awaited via `wait_for_task(task)` for synchronous completion
- New VM state captured in `after_state` field
- Task result (success/failure) recorded

### Layer 6: Comprehensive Audit Logging

Every operation is logged via `vmware_aiops/notify/audit.py:AuditLogger.log()` to `~/.vmware-aiops/audit.log` in JSONL format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "target": "prod-vcenter",
  "operation": "vm_delete",
  "resource": "test-vm-01",
  "parameters": {"vm_name": "test-vm-01", "force": false},
  "before_state": {"power_state": "poweredOff", "cpu": 2, "memory_mb": 4096},
  "after_state": null,
  "result": "success",
  "user": "admin",
  "rejection_reason": null
}
```

Rejected operations are also logged:
```json
{
  "timestamp": "2024-01-15T10:32:18.456Z",
  "operation": "vm_power_off",
  "resource": "prod-db-01",
  "rejection_reason": "User declined second confirmation",
  "result": "rejected"
}
```

This audit trail is tamper-evident (append-only JSONL), provides complete operation history for security review and compliance, and enables rollback planning for multi-step operations.

Sources: [vmware_aiops/cli.py](), [vmware_aiops/ops/vm_lifecycle.py](), [vmware_aiops/notify/audit.py](), [README.md:199-214]()

## Related Pages

- For installation instructions and initial setup, see [Getting Started](#2)
- For detailed configuration options, see [Configuration](#2.2)
- For complete CLI command reference, see [CLI Command Reference](#4.1)
- For MCP server setup and tool definitions, see [MCP Mode Usage](#5)
- For AI platform integration guides, see [AI Agent Integration](#6)
- For operational procedures, see [Operations Guide](#7)
- For safety features and best practices, see [Security and Safety](#10)

---

