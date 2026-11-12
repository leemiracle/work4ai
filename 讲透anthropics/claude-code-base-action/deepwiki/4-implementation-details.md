<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-base-action · page 4 Implementation Details · fetched 2026-10-26 -->

# Implementation Details

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [action.yml](action.yml)
- [src/index.ts](src/index.ts)

</details>



This document provides a deep dive into the internal architecture, execution flow, and technical implementation of the claude-code-base-action GitHub Action. It covers the composite action pattern, runtime environment setup, main execution flow, and key architectural decisions that enable AI integration in GitHub workflows.

For high-level system architecture and component relationships, see [Architecture Overview](#4.1). For detailed information about specific subsystems, see [Claude Execution Engine](#4.2), [Settings Management System](#4.3), and [Environment Validation](#4.4).

## Composite Action Architecture

The action is implemented as a GitHub composite action, defined in `action.yml`, which orchestrates multiple steps in sequence. This pattern provides better control over the execution environment and dependency management compared to container-based actions.

### Action Execution Flow

```mermaid
flowchart TD
    START["GitHub Workflow Trigger"] --> SETUP_NODE["Setup Node.js"]
    SETUP_NODE --> INSTALL_BUN["Install Bun"]
    INSTALL_BUN --> INSTALL_DEPS["Install Dependencies"]
    INSTALL_DEPS --> INSTALL_CLAUDE["Install Claude Code"]
    INSTALL_CLAUDE --> RUN_ACTION["Run Claude Code Action"]
    
    subgraph "Runtime Environment Setup"
        SETUP_NODE --> NODE_VERSION["node-version: 18.x"]
        SETUP_NODE --> NODE_CACHE["cache: npm (optional)"]
        INSTALL_BUN --> BUN_VERSION["bun-version: 1.2.11"]
        INSTALL_DEPS --> BUN_INSTALL["bun install"]
        INSTALL_CLAUDE --> NPM_GLOBAL["npm install -g @anthropic-ai/claude-code@1.0.56"]
    end
    
    subgraph "Action Execution"
        RUN_ACTION --> CHECK_WORKING_DIR["Check CLAUDE_WORKING_DIR"]
        CHECK_WORKING_DIR --> CHANGE_DIR["cd $CLAUDE_WORKING_DIR"]
        CHANGE_DIR --> EXECUTE_TS["bun run src/index.ts"]
    end
    
    subgraph "Environment Variables"
        RUN_ACTION --> ENV_INPUTS["INPUT_* variables"]
        RUN_ACTION --> ENV_AUTH["Authentication variables"]
        RUN_ACTION --> ENV_PROVIDERS["Provider configuration"]
    end
    
    EXECUTE_TS --> SET_OUTPUTS["Set conclusion and execution_file outputs"]
```

The composite action pattern ensures consistent runtime environment setup across different GitHub Actions runners, with specific pinned versions for Node.js (18.x), Bun (1.2.11), and Claude Code (1.0.56).

**Sources:** [action.yml:96-167]()

## Main Execution Entry Point

The core logic is implemented in TypeScript with `src/index.ts` serving as the main entry point. The execution follows a strict sequence with proper error handling and GitHub Actions output management.

### Core Function Flow

```mermaid
flowchart TD
    MAIN_ENTRY["run()"] --> VALIDATE["validateEnvironmentVariables()"]
    VALIDATE --> SETUP_SETTINGS["setupClaudeCodeSettings()"]
    SETUP_SETTINGS --> PREPARE_PROMPT["preparePrompt()"]
    PREPARE_PROMPT --> RUN_CLAUDE["runClaude()"]
    
    subgraph "Error Handling"
        ERROR_CATCH["catch(error)"] --> CORE_SET_FAILED["core.setFailed()"]
        CORE_SET_FAILED --> SET_CONCLUSION["core.setOutput('conclusion', 'failure')"]
        SET_CONCLUSION --> PROCESS_EXIT["process.exit(1)"]
    end
    
    subgraph "Input Processing"
        VALIDATE --> ENV_VALIDATION["Environment variable validation"]
        SETUP_SETTINGS --> SETTINGS_INPUT["process.env.INPUT_SETTINGS"]
        PREPARE_PROMPT --> PROMPT_CONFIG["promptConfig.path"]
        PREPARE_PROMPT --> PROMPT_ENV["process.env.INPUT_PROMPT"]
        PREPARE_PROMPT --> PROMPT_FILE_ENV["process.env.INPUT_PROMPT_FILE"]
    end
    
    subgraph "Claude Execution Config"
        RUN_CLAUDE --> ALLOWED_TOOLS["process.env.INPUT_ALLOWED_TOOLS"]
        RUN_CLAUDE --> DISALLOWED_TOOLS["process.env.INPUT_DISALLOWED_TOOLS"]
        RUN_CLAUDE --> MAX_TURNS["process.env.INPUT_MAX_TURNS"]
        RUN_CLAUDE --> MCP_CONFIG["process.env.INPUT_MCP_CONFIG"]
        RUN_CLAUDE --> SYSTEM_PROMPT["process.env.INPUT_SYSTEM_PROMPT"]
        RUN_CLAUDE --> APPEND_SYSTEM_PROMPT["process.env.INPUT_APPEND_SYSTEM_PROMPT"]
        RUN_CLAUDE --> CLAUDE_ENV["process.env.INPUT_CLAUDE_ENV"]
        RUN_CLAUDE --> FALLBACK_MODEL["process.env.INPUT_FALLBACK_MODEL"]
    end
    
    VALIDATE -.->|"validation fails"| ERROR_CATCH
    SETUP_SETTINGS -.->|"setup fails"| ERROR_CATCH
    PREPARE_PROMPT -.->|"prompt preparation fails"| ERROR_CATCH
    RUN_CLAUDE -.->|"claude execution fails"| ERROR_CATCH
```

The implementation uses a straightforward sequential execution model with comprehensive error handling. Each step must complete successfully before proceeding to the next, and any failure triggers the error handling flow that sets appropriate GitHub Actions outputs.

**Sources:** [src/index.ts:9-35]()

## Runtime Environment Configuration

The action's runtime environment is carefully configured to ensure consistent execution across different GitHub Actions runners. The setup process handles multiple package managers and specific version requirements.

### Environment Setup Strategy

| Component | Version/Configuration | Purpose |
|-----------|----------------------|---------|
| Node.js | 18.x (configurable via `NODE_VERSION`) | Base JavaScript runtime |
| Bun | 1.2.11 (pinned) | Fast package manager and TypeScript executor |
| npm cache | Optional (controlled by `use_node_cache` input) | Dependency caching for Node.js projects |
| Claude Code | 1.0.56 (pinned globally) | AI execution engine |

The action uses Bun for TypeScript execution and dependency management while maintaining compatibility with npm-based caching for performance optimization in Node.js projects.

**Sources:** [action.yml:99-119]()

## Input Processing Architecture

The action processes a wide variety of inputs through environment variables, following GitHub Actions conventions. All inputs are prefixed with `INPUT_` when converted to environment variables.

### Input Categories

```mermaid
graph TB
    subgraph "Core Claude Inputs"
        INPUT_PROMPT["INPUT_PROMPT"]
        INPUT_PROMPT_FILE["INPUT_PROMPT_FILE"]
        INPUT_ALLOWED_TOOLS["INPUT_ALLOWED_TOOLS"]
        INPUT_DISALLOWED_TOOLS["INPUT_DISALLOWED_TOOLS"]
        INPUT_MAX_TURNS["INPUT_MAX_TURNS"]
    end
    
    subgraph "Configuration Inputs"
        INPUT_MCP_CONFIG["INPUT_MCP_CONFIG"]
        INPUT_SETTINGS["INPUT_SETTINGS"]
        INPUT_SYSTEM_PROMPT["INPUT_SYSTEM_PROMPT"]
        INPUT_APPEND_SYSTEM_PROMPT["INPUT_APPEND_SYSTEM_PROMPT"]
        INPUT_CLAUDE_ENV["INPUT_CLAUDE_ENV"]
        INPUT_FALLBACK_MODEL["INPUT_FALLBACK_MODEL"]
    end
    
    subgraph "Authentication Inputs"
        ANTHROPIC_API_KEY["ANTHROPIC_API_KEY"]
        CLAUDE_CODE_OAUTH_TOKEN["CLAUDE_CODE_OAUTH_TOKEN"]
        CLAUDE_CODE_USE_BEDROCK["CLAUDE_CODE_USE_BEDROCK"]
        CLAUDE_CODE_USE_VERTEX["CLAUDE_CODE_USE_VERTEX"]
    end
    
    subgraph "Provider-Specific Inputs"
        AWS_REGION["AWS_REGION"]
        AWS_ACCESS_KEY_ID["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY["AWS_SECRET_ACCESS_KEY"]
        ANTHROPIC_VERTEX_PROJECT_ID["ANTHROPIC_VERTEX_PROJECT_ID"]
        CLOUD_ML_REGION["CLOUD_ML_REGION"]
    end
    
    INPUT_PROMPT --> PROMPT_PROCESSING["Prompt Processing Logic"]
    INPUT_MCP_CONFIG --> CONFIG_PROCESSING["Configuration Processing Logic"]
    ANTHROPIC_API_KEY --> AUTH_PROCESSING["Authentication Processing Logic"]
    AWS_REGION --> PROVIDER_PROCESSING["Provider Processing Logic"]
```

The input processing architecture separates concerns into distinct categories, each handled by specialized functions within the TypeScript implementation.

**Sources:** [action.yml:132-166](), [src/index.ts:15-29]()

## Output Management

The action produces two primary outputs that integrate with GitHub Actions workflows:

### Output Structure

| Output | Type | Source | Purpose |
|--------|------|--------|---------|
| `conclusion` | String (`success`/`failure`) | `steps.run_claude.outputs.conclusion` | Workflow decision making |
| `execution_file` | Path | `steps.run_claude.outputs.execution_file` | JSON execution log access |

The outputs are set through the `@actions/core` library's `setOutput` function, ensuring proper integration with GitHub Actions workflow syntax for conditional logic and artifact handling.

**Sources:** [action.yml:88-94](), [src/index.ts:31-32]()

## Modular Function Architecture

The implementation is structured as a collection of focused modules, each responsible for a specific aspect of the execution flow:

### Module Responsibilities

| Module | Function | Purpose |
|--------|----------|---------|
| `validate-env.ts` | `validateEnvironmentVariables()` | Authentication and provider validation |
| `setup-claude-code-settings.ts` | `setupClaudeCodeSettings()` | Configuration file management |
| `prepare-prompt.ts` | `preparePrompt()` | Prompt processing and file handling |
| `run-claude.ts` | `runClaude()` | Claude Code process execution |

This modular design enables focused testing, clear separation of concerns, and easier maintenance of complex authentication and configuration logic.

**Sources:** [src/index.ts:3-7](), [src/index.ts:11-29]()

---

