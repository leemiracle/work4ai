<!-- source: DeepWiki mcp.deepwiki.com · repo openai/codex-action · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [action.yml](action.yml)

</details>





This document provides a comprehensive overview of the `codex-action` repository, which implements a GitHub Action for safely executing OpenAI's Codex CLI within GitHub Actions workflows. This page covers the system's purpose, high-level architecture, and key components.

## Purpose and Scope

The `codex-action` repository implements a GitHub Action that enables users to run `codex exec` commands directly from GitHub Actions workflows while maintaining strict control over execution privileges and security. The action handles the complex infrastructure setup required for Codex execution, including CLI installation, OpenAI API proxy management, and privilege isolation, allowing users to focus on crafting effective prompts.

**Sources:** [README.md:1-3](), [action.yml:1-3]()

## What is codex-action

The `codex-action` system is a composite GitHub Action that orchestrates the execution of OpenAI's Codex CLI in a controlled environment. At its core, it provides:

- **Automated Infrastructure Setup**: Installs `@openai/codex` CLI and `@openai/codex-responses-api-proxy` packages [action.yml:144-154]().
- **Security-First Design**: Implements multiple safety strategies (e.g., `drop-sudo`, `read-only`, `unprivileged-user`) to restrict Codex privileges [action.yml:74-106]().
- **Seamless Integration**: Exposes a simple interface through `action.yml` while handling complex orchestration internally [action.yml:4-122]().
- **Cross-Platform Support**: Works on Linux, macOS, and Windows with appropriate safety constraints [action.yml:74-77](), [action.yml:131-140]().

The action accepts either inline prompts via the `prompt` input or file-based prompts via `prompt-file`, executes them through the Codex CLI, and returns the results as the `final-message` output for downstream workflow steps [action.yml:5-12](), [action.yml:124-126]().

**Sources:** [README.md:1-6](), [action.yml:4-152]()

## High-Level System Architecture

The following diagram shows the major system components and their relationships, using the actual code entities from the repository:

**Figure 1: High-Level System Architecture**
```mermaid
graph TB
    subgraph "GitHub Actions Runtime"
        GHWorkflow["GitHub Workflow"]
        GHRunner["actions/setup-node@53b83947a5a98c8d113130e565377fae1a50d02f"]
        GHInputs["action.yml inputs<br/>prompt, openai-api-key, safety-strategy"]
        GHOutputs["steps.run_codex.outputs.final-message"]
    end
    
    subgraph "Codex Action System"
        ActionYml["action.yml<br/>Composite Action Definition"]
        MainJs["dist/main.js<br/>Compiled CLI Tool"]
        ValidationStep["Validate Windows safety strategy"]
        WriteAccessStep["Check repository write access"]
        NodeSetupStep["Ensure Node.js available"]
    end
    
    subgraph "CLI Command Interface"
        ReadServerInfo["read-server-info command"]
        DropSudo["drop-sudo command"]
        RunCodexExec["run-codex-exec command"]
        CheckWriteAccessCmd["check-write-access command"]
        ResolveCodexHome["resolve-codex-home command"]
        WriteProxyConfig["write-proxy-config command"]
    end
    
    subgraph "External Dependencies"
        OpenAICodex["@openai/codex CLI"]
        ProxyPackage["@openai/codex-responses-api-proxy"]
        OpenAIAPI["OpenAI Responses API"]
        GitHubAPI["GitHub REST/GraphQL APIs"]
    end
    
    subgraph "Safety Strategy Engine"
        DropSudoStrategy["drop-sudo strategy"]
        UnprivilegedUser["unprivileged-user strategy"]
        ReadOnly["read-only strategy"]
        Unsafe["unsafe strategy"]
    end
    
    GHWorkflow --> ActionYml
    GHInputs --> ActionYml
    ActionYml --> ValidationStep
    ActionYml --> NodeSetupStep
    ActionYml --> WriteAccessStep
    ActionYml --> MainJs
    
    MainJs --> ReadServerInfo
    MainJs --> DropSudo
    MainJs --> RunCodexExec
    MainJs --> CheckWriteAccessCmd
    MainJs --> ResolveCodexHome
    MainJs --> WriteProxyConfig
    
    WriteAccessStep --> CheckWriteAccessCmd
    CheckWriteAccessCmd --> GitHubAPI
    
    RunCodexExec --> OpenAICodex
    WriteProxyConfig --> ProxyPackage
    ProxyPackage --> OpenAIAPI
    
    RunCodexExec --> DropSudoStrategy
    RunCodexExec --> UnprivilegedUser
    RunCodexExec --> ReadOnly
    RunCodexExec --> Unsafe
    
    RunCodexExec --> GHOutputs
```

**Sources:** [action.yml:1-152](), [README.md:95-117]()

## Action Execution Flow

The following sequence diagram illustrates the step-by-step execution flow using the actual step names and commands from the action definition:

**Figure 2: Action Execution Sequence**
```mermaid
sequenceDiagram
    participant User as "GitHub Workflow"
    participant Action as "action.yml"
    participant CLI as "dist/main.js"
    participant Proxy as "codex-responses-api-proxy"
    participant Codex as "@openai/codex"
    participant OpenAI as "OpenAI API"
    participant GitHub as "GitHub API"
    
    User->>Action: "Trigger with inputs"
    Action->>Action: "Validate Windows safety strategy (line 131-140)"
    Action->>Action: "Ensure Node.js available (line 142-147)"
    Action->>CLI: "Check repository write access (line 149-152)"
    CLI->>GitHub: "Verify repository write permissions"
    GitHub-->>CLI: "Permission response"
    
    Action->>CLI: "resolve-codex-home"
    CLI-->>Action: "Return CODEX_HOME"

    Action->>CLI: "write-proxy-config"
    CLI->>Proxy: "Start proxy with --server-info"
    Proxy->>CLI: "Write server info to tmpfile"
    
    Action->>CLI: "read-server-info tmpfile"
    CLI-->>Action: "Return proxy port"
    
    alt "safety-strategy == drop-sudo"
        Action->>CLI: "drop-sudo"
        CLI->>CLI: "Remove sudo privileges"
        Action->>Action: "Verify sudo removed"
    end
    
    Action->>CLI: "run-codex-exec"
    CLI->>Codex: "Execute codex exec command"
    Codex->>Proxy: "API requests via proxy port"
    Proxy->>OpenAI: "Forward to OpenAI API"
    OpenAI-->>Proxy: "Codex responses"
    Proxy-->>Codex: "Return responses"
    Codex-->>CLI: "Final execution result"
    CLI->>Action: "Output final-message"
    
    Action->>Proxy: "curl shutdown endpoint"
```

**Sources:** [action.yml:131-152]()

## Key System Components

### Action Definition Layer
- **`action.yml`**: The composite action definition that orchestrates the entire execution pipeline.
- **Input validation**: Platform-specific safety strategy validation (e.g., ensuring `unsafe` on Windows) [action.yml:131-140]().
- **Dependency management**: Node.js setup [action.yml:142-147]().

### CLI Tool Layer
- **`dist/main.js`**: Compiled TypeScript application that implements core commands used within the composite action steps.
- **Command interface**: Five main commands exposed through the CLI tool:

| Command | Purpose | Reference |
|---------|---------|----------|
| `check-write-access` | Verify repository write permissions for the actor | [action.yml:149-152]() |
| `resolve-codex-home` | Determine the directory for Codex config/cache | N/A |
| `read-server-info` | Parse proxy server information (port/PID) | N/A |
| `drop-sudo` | Remove sudo privileges from the current user | N/A |
| `run-codex-exec` | Execute Codex CLI with security constraints | N/A |
| `write-proxy-config` | Configure and start the Responses API proxy | N/A |

### Safety Strategy System
The action implements four distinct safety strategies to control Codex execution privileges:

**Figure 3: Safety Strategy Decision Tree**
```mermaid
graph TD
    Input["safety-strategy input"] --> Decision{"Platform Check"}
    
    Decision -->|"Windows + !unsafe"| WindowsError["Exit with error<br/>Windows only supports unsafe"]
    Decision -->|"Windows + unsafe"| WindowsUnsafe["Execute without restrictions"]
    
    Decision -->|"Unix + drop-sudo"| DropSudoFlow["drop-sudo command<br/>Remove from sudo group"]
    Decision -->|"Unix + unprivileged-user"| UnprivFlow["Run as codex-user<br/>Validate user exists"]
    Decision -->|"Unix + read-only"| ReadOnlyFlow["Sandbox execution<br/>Filesystem/network restrictions"]
    Decision -->|"Unix + unsafe"| UnixUnsafeFlow["No privilege restrictions"]
    
    DropSudoFlow --> Verify["Verify sudo removal<br/>Test sudo -n true"]
    UnprivFlow --> Execute["run-codex-exec execution"]
    ReadOnlyFlow --> Execute
    UnixUnsafeFlow --> Execute
    WindowsUnsafe --> Execute
    Verify --> Execute
```

**Sources:** [action.yml:74-106](), [action.yml:131-140](), [README.md:113-114]()

### External Integration Layer
- **`@openai/codex`**: The official Codex CLI package installed at runtime.
- **`@openai/codex-responses-api-proxy`**: Proxy service for OpenAI API communication, protecting the API key.
- **GitHub APIs**: Used for permission checking via `check-write-access` [action.yml:149-152]().
- **OpenAI API**: Target API for Codex execution requests [action.yml:21-22]().

**Sources:** [action.yml:149-152](), [action.yml:21-22]()

## Data Flow Architecture

The action processes data through a structured pipeline from workflow inputs to final outputs:

**Figure 4: Data Flow Architecture**
```mermaid
graph LR
    subgraph "Input Processing"
        WorkflowInputs["prompt/prompt-file<br/>openai-api-key<br/>safety-strategy"]
        EnvVars["GITHUB_TOKEN<br/>GITHUB_ACTOR<br/>RUNNER_OS"]
        FileInputs["Repository checkout<br/>working-directory"]
    end
    
    subgraph "Validation & Setup"
        PlatformValidation["Windows safety validation"]
        PermissionCheck["check-write-access command"]
        ProxySetup["write-proxy-config command"]
        PrivilegeManagement["Safety strategy application"]
    end
    
    subgraph "Execution Engine"
        CodexExecution["run-codex-exec command"]
        CLIOrchestration["@openai/codex CLI invocation"]
        APIProxy["Proxy communication"]
    end
    
    subgraph "Output Generation"
        FinalMessage["steps.run_codex.outputs.final-message"]
        OutputFile["Optional file output"]
        WorkflowLogs["GitHub Actions logs"]
    end
    
    WorkflowInputs --> PlatformValidation
    EnvVars --> PermissionCheck
    FileInputs --> CodexExecution
    
    PlatformValidation --> ProxySetup
    PermissionCheck --> ProxySetup
    ProxySetup --> PrivilegeManagement
    PrivilegeManagement --> CodexExecution
    
    CodexExecution --> CLIOrchestration
    CLIOrchestration --> APIProxy
    APIProxy --> FinalMessage
    
    FinalMessage --> OutputFile
    CodexExecution --> WorkflowLogs
```

**Sources:** [action.yml:4-122](), [action.yml:124-126]()

This architecture enables the action to provide a secure, controlled environment for Codex execution while maintaining ease of use for end users through a well-defined GitHub Actions interface.

## Next Steps

- [Getting Started](2) — Practical examples and basic usage patterns.
- [Configuration Reference](3) — Detailed documentation for all action inputs and outputs.
- [Security and Safety Strategies](4) — Deep dive into privilege isolation and safety mechanisms.
- [Internal Architecture](5) — Details on the CLI tool and build system.
- [Development Guide](6) — How to contribute and understand the CI pipeline.
- [Legal and Licensing](7) — Licensing and copyright information.
- [Glossary](8) — Definitions of codebase-specific terms.

---

