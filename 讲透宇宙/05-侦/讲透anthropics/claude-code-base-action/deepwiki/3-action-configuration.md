<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-base-action · page 3 Action Configuration · fetched 2026-10-26 -->

# Action Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [action.yml](action.yml)

</details>



This document provides a comprehensive guide to configuring the `claude-code-base-action` GitHub Action. It covers all available inputs, outputs, and configuration options, showing how to customize the action's behavior for different use cases and authentication methods.

For specific details about individual inputs and outputs, see [Inputs and Outputs](#3.1). For authentication setup, see [Authentication Methods](#3.2). For advanced configuration including Claude Code settings and MCP servers, see [Settings and MCP Configuration](#3.3).

## Configuration Overview

The action accepts configuration through GitHub Action inputs defined in `action.yml`, which are then mapped to environment variables and passed to the underlying Claude Code execution system. The configuration system supports multiple authentication providers, flexible prompt handling, tool restrictions, and custom environment setup.

## Configuration Flow

The following diagram shows how configuration flows from GitHub workflow inputs through the action's internal systems:

```mermaid
graph TB
    subgraph "GitHub Workflow"
        WORKFLOW_INPUTS["workflow inputs<br/>- with: prompt<br/>- with: model<br/>- with: settings"]
    end
    
    subgraph "action.yml Processing"
        ACTION_INPUTS["action inputs<br/>prompt, model, settings<br/>anthropic_api_key, use_bedrock<br/>mcp_config, claude_env"]
        ENV_MAPPING["environment mapping<br/>INPUT_PROMPT, ANTHROPIC_MODEL<br/>ANTHROPIC_API_KEY<br/>CLAUDE_CODE_USE_BEDROCK"]
    end
    
    subgraph "src/index.ts Execution"
        VALIDATION["validateEnvironment()<br/>checkAuthProvider()"]
        SETUP_SETTINGS["setupClaudeCodeSettings()<br/>parseClaudeEnv()"]
        PREPARE_CONFIG["prepareRunConfig()<br/>buildClaudeArgs()"]
    end
    
    subgraph "Claude Code Process"
        CLAUDE_EXECUTION["claude-code execution<br/>with merged configuration"]
    end
    
    WORKFLOW_INPUTS --> ACTION_INPUTS
    ACTION_INPUTS --> ENV_MAPPING
    ENV_MAPPING --> VALIDATION
    VALIDATION --> SETUP_SETTINGS  
    SETUP_SETTINGS --> PREPARE_CONFIG
    PREPARE_CONFIG --> CLAUDE_EXECUTION
```

**Sources:** [action.yml:7-167]()

## Configuration Categories

The action's configuration is organized into several categories, each serving different aspects of the execution:

| Category | Purpose | Key Inputs |
|----------|---------|------------|
| **Prompt Configuration** | Define the task for Claude | `prompt`, `prompt_file`, `system_prompt`, `append_system_prompt` |
| **Model Configuration** | Control which AI model to use | `model`, `fallback_model` |
| **Tool Configuration** | Control Claude's available capabilities | `allowed_tools`, `disallowed_tools` |
| **Authentication** | Configure API access | `anthropic_api_key`, `use_bedrock`, `use_vertex` |
| **Execution Control** | Control runtime behavior | `timeout_minutes`, `max_turns` |
| **Advanced Configuration** | Custom settings and environment | `settings`, `mcp_config`, `claude_env` |

**Sources:** [action.yml:8-86]()

## Input Processing Architecture

This diagram shows how the action processes and validates different types of configuration inputs:

```mermaid
graph TB
    subgraph "Input Types"
        TEXT_INPUTS["Direct Text Inputs<br/>prompt, system_prompt<br/>anthropic_api_key"]
        FILE_INPUTS["File Path Inputs<br/>prompt_file, settings<br/>mcp_config"]  
        FLAG_INPUTS["Boolean Flags<br/>use_bedrock, use_vertex<br/>use_node_cache"]
        YAML_INPUTS["YAML Format<br/>claude_env"]
    end
    
    subgraph "Input Validation"
        MUTUAL_EXCLUSIVE["Mutual Exclusivity Checks<br/>prompt vs prompt_file<br/>use_bedrock vs use_vertex"]
        FILE_RESOLUTION["File Path Resolution<br/>JSON.parse() or fs.readFileSync()"]
        YAML_PARSING["YAML Parsing<br/>with GitHub secrets resolution"]
        AUTH_VALIDATION["Authentication Validation<br/>per provider requirements"]
    end
    
    subgraph "Configuration Merging"
        SETTINGS_MERGE["Settings Configuration<br/>~/.claude/settings.json"]
        ENV_SETUP["Environment Variables<br/>process.env setup"]
        FINAL_CONFIG["Final Configuration<br/>passed to runClaude()"]
    end
    
    TEXT_INPUTS --> MUTUAL_EXCLUSIVE
    FILE_INPUTS --> FILE_RESOLUTION
    FLAG_INPUTS --> AUTH_VALIDATION
    YAML_INPUTS --> YAML_PARSING
    
    MUTUAL_EXCLUSIVE --> SETTINGS_MERGE
    FILE_RESOLUTION --> SETTINGS_MERGE
    YAML_PARSING --> ENV_SETUP
    AUTH_VALIDATION --> ENV_SETUP
    
    SETTINGS_MERGE --> FINAL_CONFIG
    ENV_SETUP --> FINAL_CONFIG
```

**Sources:** [action.yml:8-86]()

## Action Outputs

The action provides two primary outputs that workflows can access:

| Output | Description | Value Source |
|--------|-------------|--------------|
| `conclusion` | Execution status | `${{ steps.run_claude.outputs.conclusion }}` - either `'success'` or `'failure'` |
| `execution_file` | Path to execution log | `${{ steps.run_claude.outputs.execution_file }}` - JSON file with detailed execution data |

These outputs are generated by the `run_claude` step and can be used by subsequent workflow steps for conditional logic or artifact collection.

**Sources:** [action.yml:88-94]()

## Composite Action Structure  

The action uses GitHub's composite action pattern with the following execution steps:

```mermaid
graph TD
    subgraph "Composite Action Steps"
        SETUP_NODE["Setup Node.js<br/>actions/setup-node@v4.4.0<br/>node-version: 18.x"]
        INSTALL_BUN["Install Bun<br/>oven-sh/setup-bun@v2.0.2<br/>bun-version: 1.2.11"]
        INSTALL_DEPS["Install Dependencies<br/>cd ${GITHUB_ACTION_PATH}<br/>bun install"]
        INSTALL_CLAUDE["Install Claude Code<br/>npm install -g @anthropic-ai/claude-code@1.0.56"]
        RUN_CLAUDE["Run Claude Code Action<br/>bun run ${GITHUB_ACTION_PATH}/src/index.ts"]
    end
    
    subgraph "Environment Setup"
        NODE_CACHE["Node.js Caching<br/>cache: inputs.use_node_cache"]
        WORKING_DIR["Working Directory<br/>cd $CLAUDE_WORKING_DIR"]
        ENV_VARS["Environment Variables<br/>INPUT_*, ANTHROPIC_*, AWS_*, etc."]
    end
    
    SETUP_NODE --> INSTALL_BUN
    INSTALL_BUN --> INSTALL_DEPS
    INSTALL_DEPS --> INSTALL_CLAUDE
    INSTALL_CLAUDE --> RUN_CLAUDE
    
    SETUP_NODE -.-> NODE_CACHE
    RUN_CLAUDE -.-> WORKING_DIR
    RUN_CLAUDE -.-> ENV_VARS
```

**Sources:** [action.yml:96-167]()

## Environment Variable Mapping

The action maps GitHub Action inputs to environment variables that the TypeScript execution code can access:

| Input Category | GitHub Input | Environment Variable |
|----------------|--------------|---------------------|
| **Prompt Configuration** | `prompt` | `INPUT_PROMPT` |
| **Model Configuration** | `model` | `ANTHROPIC_MODEL` |
| **Authentication** | `anthropic_api_key` | `ANTHROPIC_API_KEY` |
| **Provider Flags** | `use_bedrock` | `CLAUDE_CODE_USE_BEDROCK` |
| **Advanced Config** | `settings` | `INPUT_SETTINGS` |
| **Custom Environment** | `claude_env` | `INPUT_CLAUDE_ENV` |

The environment variable mapping follows a consistent pattern where action inputs are prefixed with `INPUT_` while provider-specific variables use their standard names (e.g., `ANTHROPIC_API_KEY`, `AWS_REGION`).

**Sources:** [action.yml:130-167]()

---

