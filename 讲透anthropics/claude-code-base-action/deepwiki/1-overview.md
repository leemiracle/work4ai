<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-base-action · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MIRROR_DISCLAIMER.md](MIRROR_DISCLAIMER.md)
- [README.md](README.md)
- [action.yml](action.yml)

</details>



This document provides a high-level overview of the `claude-code-base-action` GitHub Action, which enables integration of Anthropic's Claude AI into GitHub Actions workflows. The action serves as a wrapper that orchestrates the execution of Claude Code within the GitHub Actions environment, handling authentication, configuration management, and output processing.

For detailed configuration options, see [Action Configuration](#3). For implementation specifics, see [Implementation Details](#4). For practical examples, see [Usage Examples](#5).

## Purpose and Architecture

The `claude-code-base-action` is a composite GitHub Action that provides a bridge between GitHub's workflow automation platform and Claude Code's AI capabilities. The action handles the complete lifecycle from environment setup to result processing, supporting multiple authentication providers and extensive configuration options.

### System Architecture

The action follows a multi-stage composite pattern that orchestrates several distinct phases:

```mermaid
graph TB
    subgraph "GitHub Actions Runtime"
        GW["GitHub Workflow"] --> CBA["claude-code-base-action"]
    end
    
    subgraph "Composite Action Steps"
        CBA --> SETUP_NODE["actions/setup-node@49933ea"]
        SETUP_NODE --> SETUP_BUN["oven-sh/setup-bun@735343b"]
        SETUP_BUN --> INSTALL_DEPS["bun install"]
        INSTALL_DEPS --> INSTALL_CLAUDE["npm install -g @anthropic-ai/claude-code@1.0.56"]
        INSTALL_CLAUDE --> RUN_ACTION["bun run src/index.ts"]
    end
    
    subgraph "Core Execution Components"
        RUN_ACTION --> ENV_VALIDATION["validateEnvironment"]
        ENV_VALIDATION --> SETUP_SETTINGS["setupClaudeCodeSettings"]
        SETUP_SETTINGS --> PREPARE_CONFIG["prepareRunConfig"]
        PREPARE_CONFIG --> RUN_CLAUDE["runClaude"]
    end
    
    subgraph "Output Processing"
        RUN_CLAUDE --> EXECUTION_FILE["execution_file.json"]
        RUN_CLAUDE --> CONCLUSION["conclusion: success|failure"]
    end
    
    style CBA fill:#f9f9f9
    style RUN_CLAUDE fill:#f0f0f0
```

**Sources:** [action.yml:96-167](), [README.md:12-16]()

### Authentication Provider Architecture

The action supports multiple authentication mechanisms with mutual exclusion validation:

```mermaid
graph LR
    subgraph "Authentication Inputs"
        API_KEY["anthropic_api_key"]
        OAUTH["claude_code_oauth_token"] 
        USE_BEDROCK["use_bedrock"]
        USE_VERTEX["use_vertex"]
    end
    
    subgraph "Provider Selection Logic"
        API_KEY --> DIRECT["Direct Anthropic API"]
        OAUTH --> DIRECT
        USE_BEDROCK --> BEDROCK["AWS Bedrock OIDC"]
        USE_VERTEX --> VERTEX["Google Vertex AI OIDC"]
    end
    
    subgraph "Environment Variables"
        DIRECT --> ANTHROPIC_API_KEY["ANTHROPIC_API_KEY"]
        DIRECT --> CLAUDE_CODE_OAUTH_TOKEN["CLAUDE_CODE_OAUTH_TOKEN"]
        BEDROCK --> AWS_VARS["AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"]
        VERTEX --> GCP_VARS["ANTHROPIC_VERTEX_PROJECT_ID, CLOUD_ML_REGION"]
    end
    
    subgraph "Provider Endpoints"
        ANTHROPIC_API_KEY --> ANTHROPIC_BASE_URL["ANTHROPIC_BASE_URL"]
        AWS_VARS --> ANTHROPIC_BEDROCK_BASE_URL["ANTHROPIC_BEDROCK_BASE_URL"]
        GCP_VARS --> ANTHROPIC_VERTEX_BASE_URL["ANTHROPIC_VERTEX_BASE_URL"]
    end
    
    subgraph "Mutual Exclusion"
        MUTEX["Cannot use both Bedrock and Vertex"]
        USE_BEDROCK -.->|"conflicts"| MUTEX
        USE_VERTEX -.->|"conflicts"| MUTEX
    end
```

**Sources:** [action.yml:65-81](), [action.yml:147-166](), [README.md:398-454]()

## Core Execution Flow

The action's main execution occurs through the `src/index.ts` entry point, which coordinates several key processes:

### Configuration Management

The action processes multiple configuration sources in a specific order:

| Configuration Type | Input Parameter | Environment Variable | Processing Function |
|-------------------|----------------|---------------------|-------------------|
| Claude Settings | `settings` | `INPUT_SETTINGS` | `setupClaudeCodeSettings` |
| MCP Configuration | `mcp_config` | `INPUT_MCP_CONFIG` | (processed in settings) |
| Environment Variables | `claude_env` | `INPUT_CLAUDE_ENV` | YAML parsing |
| System Prompts | `system_prompt`, `append_system_prompt` | `INPUT_SYSTEM_PROMPT`, `INPUT_APPEND_SYSTEM_PROMPT` | Direct assignment |

**Sources:** [action.yml:29-57](), [action.yml:130-145]()

### Key Components and Their Roles

The action architecture centers around several core functions that map to specific responsibilities:

```mermaid
graph TD
    subgraph "Input Processing"
        INPUT_PROMPT["INPUT_PROMPT / INPUT_PROMPT_FILE"]
        INPUT_TOOLS["INPUT_ALLOWED_TOOLS / INPUT_DISALLOWED_TOOLS"]
        INPUT_CONFIG["INPUT_SETTINGS / INPUT_MCP_CONFIG"]
    end
    
    subgraph "Core Functions"
        VALIDATE_ENV["validateEnvironment()"]
        SETUP_SETTINGS["setupClaudeCodeSettings()"]
        PREPARE_CONFIG["prepareRunConfig()"]
        RUN_CLAUDE_FUNC["runClaude()"]
    end
    
    subgraph "External Dependencies"
        CLAUDE_CODE_CLI["@anthropic-ai/claude-code@1.0.56"]
        NODE_RUNTIME["Node.js runtime"]
        BUN_RUNTIME["Bun runtime"]
    end
    
    subgraph "Output Generation"
        EXECUTION_LOG["execution_file.json"]
        STATUS_OUTPUT["conclusion output"]
    end
    
    INPUT_PROMPT --> VALIDATE_ENV
    INPUT_TOOLS --> VALIDATE_ENV
    INPUT_CONFIG --> SETUP_SETTINGS
    VALIDATE_ENV --> PREPARE_CONFIG
    SETUP_SETTINGS --> PREPARE_CONFIG
    PREPARE_CONFIG --> RUN_CLAUDE_FUNC
    
    RUN_CLAUDE_FUNC --> CLAUDE_CODE_CLI
    CLAUDE_CODE_CLI --> EXECUTION_LOG
    CLAUDE_CODE_CLI --> STATUS_OUTPUT
    
    NODE_RUNTIME --> RUN_CLAUDE_FUNC
    BUN_RUNTIME --> RUN_CLAUDE_FUNC
```

**Sources:** [action.yml:116-129](), [action.yml:88-94]()

### Environment Variable Processing

The action implements a comprehensive environment variable system that bridges GitHub Actions inputs to Claude Code execution context:

| Category | Key Variables | Purpose |
|----------|--------------|---------|
| Model Configuration | `ANTHROPIC_MODEL`, `INPUT_FALLBACK_MODEL` | Claude model selection |
| Tool Control | `INPUT_ALLOWED_TOOLS`, `INPUT_DISALLOWED_TOOLS` | Tool permission management |
| Execution Control | `INPUT_MAX_TURNS`, `INPUT_TIMEOUT_MINUTES` | Runtime constraints |
| Provider Flags | `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX` | Authentication provider selection |

**Sources:** [action.yml:131-154]()

### Runtime Dependencies

The action orchestrates several runtime dependencies through its composite structure:

- **Node.js Runtime**: Managed via `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`
- **Bun Runtime**: Managed via `oven-sh/setup-bun@735343b667d3e6f658f44d0eca948eb6282f2b76`  
- **Claude Code CLI**: Installed as `@anthropic-ai/claude-code@1.0.56`
- **Action Dependencies**: Installed via `bun install` from the action's directory

**Sources:** [action.yml:99-118]()

This architecture enables the action to serve as a robust integration point between GitHub's automation platform and Claude's AI capabilities, while maintaining security, configurability, and extensibility across multiple cloud providers.

---

