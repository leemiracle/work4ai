# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



## Purpose and Scope

AWS Skills for Claude Code is a plugin marketplace system that extends Claude Code with specialized AWS development capabilities. The system provides five domain-specific plugins built on a common foundation, enabling infrastructure as code development, cost optimization, event-driven architecture design, and AI agent deployment through a unified skill-based interface backed by Model Context Protocol (MCP) servers.

This document provides a high-level overview of the marketplace architecture, plugin ecosystem, MCP server integration, and skill execution model. For detailed installation instructions, see [Getting Started](#2). For plugin-specific documentation, see [Plugins](#4). For contribution guidelines, see [Development Guide](#5).

Sources: [README.md:1-3](), [.claude-plugin/marketplace.json:1-152]()

## Marketplace Architecture

The marketplace is defined in `.claude-plugin/marketplace.json` as a central registry at version 2.2.0, managing all plugin metadata, versioning, and MCP server configurations. Claude Code loads plugins from this registry when users add the marketplace via `/plugin marketplace add zxkane/aws-skills`.

```mermaid
graph TB
    subgraph "Marketplace Registry"
        MarketplaceJSON["marketplace.json<br/>version: 2.2.0<br/>name: aws-skills<br/>owner: Kane Zhu"]
        
        PluginsArray["plugins: Array[5]"]
    end
    
    subgraph "Foundation Plugin"
        AWSCommon["aws-common@1.0.0<br/>category: development<br/>source: ./plugins/aws-common<br/>skills: [aws-mcp-setup]"]
    end
    
    subgraph "Development Plugins"
        AWSCDK["aws-cdk@1.2.0<br/>category: development<br/>source: ./plugins/aws-cdk<br/>skills: [aws-cdk-development]<br/>mcpServers: {cdk}"]
        
        ServerlessEDA["serverless-eda@1.2.0<br/>category: development<br/>source: ./plugins/serverless-eda<br/>skills: [aws-serverless-eda]<br/>mcpServers: {}"]
        
        AgenticAI["aws-agentic-ai@1.2.0<br/>category: development<br/>source: ./plugins/aws-agentic-ai<br/>skills: [aws-agentic-ai]<br/>mcpServers: {}"]
    end
    
    subgraph "Operations Plugin"
        CostOps["aws-cost-ops@1.2.0<br/>category: operations<br/>source: ./plugins/aws-cost-ops<br/>skills: [aws-cost-operations]<br/>mcpServers: {pricing, costexp, cw}"]
    end
    
    MarketplaceJSON --> PluginsArray
    PluginsArray --> AWSCommon
    PluginsArray --> AWSCDK
    PluginsArray --> ServerlessEDA
    PluginsArray --> AgenticAI
    PluginsArray --> CostOps
    
    AWSCDK -.depends on.-> AWSCommon
    ServerlessEDA -.depends on.-> AWSCommon
    AgenticAI -.depends on.-> AWSCommon
    CostOps -.depends on.-> AWSCommon
```

**Marketplace Structure**: The registry defines plugin metadata including `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `category`, `source` directory, `strict` mode, `skills` array, and optional `mcpServers` configuration. Each plugin's `source` points to a directory under `./plugins/`.

Sources: [.claude-plugin/marketplace.json:1-152]()

## Plugin Ecosystem

The system consists of five plugins organized in a layered dependency model with `aws-common` as the foundation:

| Plugin | Version | Category | Skills | MCP Servers | Purpose |
|--------|---------|----------|--------|-------------|---------|
| `aws-common` | 1.0.0 | development | `aws-mcp-setup` | 0 | Foundation dependency providing MCP configuration guidance |
| `aws-cdk` | 1.2.0 | development | `aws-cdk-development` | 1 (cdk) | Infrastructure as code with CDK best practices |
| `aws-cost-ops` | 1.2.0 | operations | `aws-cost-operations` | 3 (pricing, costexp, cw) | Cost optimization and operational monitoring |
| `serverless-eda` | 1.2.0 | development | `aws-serverless-eda` | 0 | Event-driven architecture patterns |
| `aws-agentic-ai` | 1.2.0 | development | `aws-agentic-ai` | 0 | Bedrock AgentCore deployment |

**Version Strategy**: `aws-common` at v1.0.0 represents a stable foundation, while domain plugins at v1.2.0 evolve more rapidly with new features and patterns.

**Installation Order**: Users must install `aws-common` first, then install domain plugins as needed. The marketplace enforces this dependency through the skill auto-loading mechanism described in [Skill Execution Model](#skill-execution-model).

Sources: [.claude-plugin/marketplace.json:11-151](), [README.md:7-66]()

### aws-common Plugin (Foundation)

Provides the `aws-mcp-setup` skill that guides users through MCP server configuration. All domain plugins depend on this skill to ensure access to up-to-date AWS documentation and services.

Sources: [.claude-plugin/marketplace.json:12-30](), [README.md:7-16]()

### aws-cdk Plugin (Infrastructure)

Implements AWS CDK development patterns with integrated CDK MCP server. Provides best practices for resource naming, Lambda function bundling (`NodejsFunction`, `PythonFunction`), and pre-deployment validation scripts.

Sources: [.claude-plugin/marketplace.json:31-61](), [README.md:18-26]()

### aws-cost-ops Plugin (Operations)

Integrates three MCP servers (`pricing`, `costexp`, `cw`) for comprehensive cost optimization, monitoring, and operational excellence. Enables pre-deployment cost estimation and post-deployment analysis.

Sources: [.claude-plugin/marketplace.json:62-112](), [README.md:30-42]()

### serverless-eda Plugin (Event-Driven)

Provides serverless and event-driven architecture patterns based on AWS Well-Architected Framework. Covers orchestration, saga patterns, and event sourcing without dedicated MCP servers, relying on CDK skill dependency.

Sources: [.claude-plugin/marketplace.json:113-131](), [README.md:44-53]()

### aws-agentic-ai Plugin (AI Agents)

Comprehensive expert for Bedrock AgentCore covering seven services: Gateway, Runtime, Memory, Identity, Code Interpreter, Browser, and Observability. Focuses on architectural guidance rather than MCP integration.

Sources: [.claude-plugin/marketplace.json:132-150](), [README.md:55-66]()

## MCP Server Integration

MCP (Model Context Protocol) servers bridge Claude Code to AWS services through a standardized `stdio` protocol. Plugins declare MCP servers in their `mcpServers` configuration, specifying the launcher command, arguments, and environment variables.

```mermaid
graph LR
    subgraph "Plugin MCP Configuration"
        CDKPlugin["aws-cdk Plugin<br/>marketplace.json:49-60"]
        CostPlugin["aws-cost-ops Plugin<br/>marketplace.json:80-111"]
    end
    
    subgraph "MCP Server Definitions"
        CDKServer["cdk:<br/>type: stdio<br/>command: uvx<br/>args: [awslabs.cdk-mcp-server@latest]<br/>env: {FASTMCP_LOG_LEVEL: ERROR}"]
        
        PricingServer["pricing:<br/>type: stdio<br/>command: uvx<br/>args: [awslabs.aws-pricing-mcp-server@latest]<br/>env: {FASTMCP_LOG_LEVEL: ERROR}"]
        
        CostexpServer["costexp:<br/>type: stdio<br/>command: uvx<br/>args: [awslabs.cost-explorer-mcp-server@latest]<br/>env: {FASTMCP_LOG_LEVEL: ERROR}"]
        
        CWServer["cw:<br/>type: stdio<br/>command: uvx<br/>args: [awslabs.cloudwatch-mcp-server@latest]<br/>env: {FASTMCP_LOG_LEVEL: ERROR}"]
    end
    
    subgraph "AWS Services"
        CDKService["AWS CDK/<br/>CloudFormation"]
        PricingAPI["AWS Pricing API"]
        CostExplorer["AWS Cost Explorer"]
        CloudWatch["Amazon CloudWatch"]
    end
    
    CDKPlugin --> CDKServer
    CostPlugin --> PricingServer
    CostPlugin --> CostexpServer
    CostPlugin --> CWServer
    
    CDKServer --> CDKService
    PricingServer --> PricingAPI
    CostexpServer --> CostExplorer
    CWServer --> CloudWatch
```

**MCP Server Naming**: Servers use short identifiers (`cdk`, `cw`, `pricing`, `costexp`) to comply with Bedrock's 64-character tool name limit. The runtime generates tool names following the pattern: `mcp__plugin_{plugin}_{server}__{tool}`.

**Launch Mechanism**: All MCP servers use `uvx` (Python package launcher) to execute `awslabs.*-mcp-server@latest` packages, ensuring users always get the latest AWS service integrations. The `FASTMCP_LOG_LEVEL: ERROR` setting minimizes log noise during normal operations.

**Integration Patterns**:
- **aws-cdk**: 1 server for CDK operations
- **aws-cost-ops**: 3 servers for comprehensive cost/monitoring coverage
- **aws-common, serverless-eda, aws-agentic-ai**: 0 dedicated servers, rely on shared `aws-common` documentation MCP or transitive dependencies

Sources: [.claude-plugin/marketplace.json:49-111](), [README.md:267-271]()

## Skill Execution Model

Skills are defined through `SKILL.md` files with YAML frontmatter controlling execution context, dependencies, tool permissions, and lifecycle hooks. When a skill is invoked, Claude Code forks an isolated sub-agent context with the specified configuration.

```mermaid
graph TB
    subgraph "Skill Definition Layer"
        SkillMD["skills/{skill}/SKILL.md<br/>plugins/aws-cdk/skills/aws-cdk-development/"]
        
        Frontmatter["YAML Frontmatter:<br/>name: aws-cdk-development<br/>description: ...<br/>context: fork<br/>model: sonnet<br/>skills: [aws-mcp-setup]<br/>allowed-tools: [...]<br/>hooks: {...}"]
        
        Content["Markdown Content:<br/>Instructions<br/>Best Practices<br/>Patterns"]
        
        References["references/*.md<br/>cdk-patterns.md<br/>operations-patterns.md"]
    end
    
    subgraph "Execution Context"
        ForkContext["Fork Context<br/>Isolated Sub-Agent"]
        ModelSelection["Model: sonnet"]
        DependencyLoad["Auto-load:<br/>aws-mcp-setup skill"]
        ToolPermissions["Allowed Tools:<br/>mcp__plugin_aws_cdk_cdk__*<br/>Bash(aws *)<br/>Bash(cdk *)"]
        PreToolUse["PreToolUse Hook:<br/>aws sts get-caller-identity<br/>once: true"]
    end
    
    subgraph "Tool Invocation"
        MCPTools["MCP Tools:<br/>mcp__plugin_aws_cdk_cdk__list_constructs<br/>mcp__plugin_aws_cdk_cdk__recommend_construct"]
        BashTools["Bash Commands:<br/>Bash(cdk synth)<br/>Bash(cdk deploy)<br/>Bash(aws sts get-caller-identity)"]
    end
    
    subgraph "AWS Integration"
        MCPServers["MCP Servers:<br/>awslabs.cdk-mcp-server<br/>awslabs.aws-pricing-mcp-server<br/>awslabs.cost-explorer-mcp-server"]
        AWSAPIs["AWS APIs:<br/>CloudFormation<br/>Pricing<br/>Cost Explorer<br/>CloudWatch"]
    end
    
    SkillMD --> Frontmatter
    SkillMD --> Content
    Content --> References
    
    Frontmatter --> ForkContext
    Frontmatter --> ModelSelection
    Frontmatter --> DependencyLoad
    Frontmatter --> ToolPermissions
    Frontmatter --> PreToolUse
    
    ForkContext --> MCPTools
    ForkContext --> BashTools
    ToolPermissions --> MCPTools
    ToolPermissions --> BashTools
    
    MCPTools --> MCPServers
    BashTools --> AWSAPIs
    MCPServers --> AWSAPIs
```

**Skill Structure**: Each skill follows a standardized directory structure:
- `SKILL.md`: Main skill definition with frontmatter and instructions
- `references/`: Optional detailed pattern documentation
- `scripts/`: Optional utility scripts (e.g., `validate-stack.sh`)
- `services/`: Optional service-specific code

**Frontmatter Configuration**:
- `name`, `description`: Skill metadata
- `context: fork`: Execute in isolated sub-agent
- `model: sonnet`: Model selection (e.g., Claude 3.5 Sonnet)
- `skills: [aws-mcp-setup]`: Auto-loaded skill dependencies
- `allowed-tools`: Whitelist of MCP servers and bash command patterns
- `hooks`: Lifecycle hooks (e.g., `PreToolUse` for account verification)

**Dependency Auto-Loading**: When `aws-cdk-development` skill is invoked, it automatically loads `aws-mcp-setup` skill. When `aws-serverless-eda` is invoked, it loads both `aws-mcp-setup` and `aws-cdk-development`, creating a dependency chain.

**Tool Naming Convention**: MCP tools follow the pattern `mcp__plugin_{plugin}_{server}__{tool}`, where `{plugin}` is the plugin name, `{server}` is the MCP server identifier, and `{tool}` is the specific tool name. For example: `mcp__plugin_aws_cdk_cdk__list_constructs`.

Sources: [README.md:227-265](), [README.md:267-271](), [.claude-plugin/marketplace.json:27-29](), [.claude-plugin/marketplace.json:46-48]()

## System Integration Flow

The complete flow from user interaction to AWS service invocation demonstrates how the marketplace, plugins, skills, and MCP servers integrate:

```mermaid
graph TB
    subgraph "User Layer"
        User["Developer"]
        CLI["Claude Code CLI<br/>claude -p 'Create CDK stack...'"]
        IDE["Claude Code IDE<br/>/skills aws-cdk-development"]
    end
    
    subgraph "Marketplace Layer"
        Marketplace["marketplace.json<br/>Loads plugin definitions"]
        PluginInstall["Plugin Installation:<br/>/plugin install aws-cdk@aws-skills"]
    end
    
    subgraph "Plugin Layer"
        CDKPluginDir["plugins/aws-cdk/<br/>Plugin directory structure"]
        SkillFile["skills/aws-cdk-development/SKILL.md<br/>Skill definition + frontmatter"]
        ReferenceDocs["references/cdk-patterns.md<br/>Pattern documentation"]
        ValidateScript["scripts/validate-stack.sh<br/>Pre-deployment validation"]
    end
    
    subgraph "Execution Layer"
        ForkAgent["Fork Context<br/>Isolated sub-agent with model: sonnet"]
        LoadDeps["Auto-load:<br/>aws-mcp-setup skill"]
        RunHook["Execute PreToolUse Hook:<br/>Bash(aws sts get-caller-identity)"]
    end
    
    subgraph "Tool Layer"
        MCPTool["MCP Tool Invocation:<br/>mcp__plugin_aws_cdk_cdk__recommend_construct"]
        BashTool["Bash Tool Invocation:<br/>Bash(cdk synth)<br/>Bash(cdk deploy)"]
    end
    
    subgraph "Integration Layer"
        MCPServerLaunch["MCP Server Launch:<br/>uvx awslabs.cdk-mcp-server@latest"]
        StdioProtocol["stdio Communication Protocol"]
        AWSCredentials["AWS Credentials<br/>from local environment"]
    end
    
    subgraph "AWS Layer"
        CloudFormation["AWS CloudFormation<br/>Stack deployment"]
        IAM["AWS IAM<br/>Role/Policy management"]
        Lambda["AWS Lambda<br/>Function deployment"]
    end
    
    User --> CLI
    User --> IDE
    CLI --> Marketplace
    IDE --> Marketplace
    Marketplace --> PluginInstall
    PluginInstall --> CDKPluginDir
    CDKPluginDir --> SkillFile
    SkillFile --> ReferenceDocs
    SkillFile --> ValidateScript
    SkillFile --> ForkAgent
    ForkAgent --> LoadDeps
    LoadDeps --> RunHook
    RunHook --> MCPTool
    RunHook --> BashTool
    MCPTool --> MCPServerLaunch
    MCPServerLaunch --> StdioProtocol
    StdioProtocol --> AWSCredentials
    BashTool --> AWSCredentials
    AWSCredentials --> CloudFormation
    AWSCredentials --> IAM
    AWSCredentials --> Lambda
```

**Flow Stages**:

1. **User Interaction**: Developer invokes skill via CLI (`claude -p`) or IDE (`/skills` command)
2. **Marketplace Loading**: Claude Code reads `marketplace.json` and resolves plugin definitions
3. **Plugin Discovery**: Locates plugin directory (`./plugins/aws-cdk`) and skill file (`./skills/aws-cdk-development/SKILL.md`)
4. **Execution Setup**: Creates fork context with specified model, auto-loads dependency skills, validates tool permissions
5. **Hook Execution**: Runs `PreToolUse` hook (e.g., account verification via `aws sts get-caller-identity`) before tool invocation
6. **Tool Invocation**: Executes MCP tools or bash commands based on `allowed-tools` whitelist
7. **MCP Launch**: On-demand launch of MCP server via `uvx`, establishing `stdio` communication channel
8. **AWS Integration**: MCP servers and bash commands interact with AWS services using local credentials

**Critical Bootstrap**: Before any AWS-related question is answered, skills check for MCP tool availability. If unavailable, the auto-loaded `aws-mcp-setup` skill guides users through configuration, ensuring no outdated AWS information is provided.

Sources: [.claude-plugin/marketplace.json:1-152](), [README.md:68-87](), [README.md:127-142]()

## Version Management

The system uses semantic versioning with distinct strategies for the marketplace versus individual plugins:

| Component | Current Version | Bump Trigger | Example |
|-----------|----------------|--------------|---------|
| Marketplace (`marketplace.json`) | 2.2.0 | New plugin added | 2.1.0 → 2.2.0 |
| `aws-common` plugin | 1.0.0 | Structural changes to foundation | 1.0.0 (stable) |
| Development plugins | 1.2.0 | New skills, dependencies, features | 1.1.0 → 1.2.0 |

**Version Differential**: The version gap (marketplace at 2.2.0 vs plugins at 1.0.0-1.2.0) reflects that the marketplace tracks plugin additions while individual plugins track their own evolution independently.

**Minor vs Patch Bumps**:
- **Minor (x.Y.0)**: New skill, new MCP server, new dependency, new plugin
- **Patch (x.y.Z)**: Bug fixes, documentation updates, configuration tweaks, typo corrections

For detailed version management rules, see [Version Management](#5.2).

Sources: [.claude-plugin/marketplace.json:9](), [.claude-plugin/marketplace.json:15](), [.claude-plugin/marketplace.json:34]()

## Directory Structure

The repository follows a standardized structure enabling plugin discovery, skill loading, and local development:

```
aws-skills/
├── .claude-plugin/
│   └── marketplace.json              # Central registry (v2.2.0)
├── plugins/                          # Plugin isolation
│   ├── aws-common/
│   │   └── skills/
│   │       └── aws-mcp-setup/        # Foundation skill
│   ├── aws-cdk/
│   │   └── skills/
│   │       └── aws-cdk-development/  # CDK skill with references, scripts
│   ├── aws-cost-ops/
│   │   └── skills/
│   │       └── aws-cost-operations/  # Cost/ops skill with patterns
│   ├── serverless-eda/
│   │   └── skills/
│   │       └── aws-serverless-eda/   # EDA skill with patterns
│   └── aws-agentic-ai/
│       └── skills/
│           └── aws-agentic-ai/       # AgentCore skill with services/
└── README.md                         # User documentation
```

**Key Locations**:
- [.claude-plugin/marketplace.json:1-152](): Central registry defining all plugins
- `plugins/{plugin}/skills/{skill}/SKILL.md`: Skill definition with frontmatter
- `plugins/{plugin}/skills/{skill}/references/*.md`: Pattern documentation
- `plugins/{plugin}/skills/{skill}/scripts/*.sh`: Utility scripts
- `plugins/{plugin}/skills/{skill}/services/`: Service-specific documentation

**Local Development**: Developers symlink `plugins/{plugin}/skills/` to `.claude/skills/` for rapid iteration without reinstallation. See [Local Development Setup](#5.1) for details.

Sources: [README.md:225-265]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



This document guides you through the initial setup of AWS Skills for Claude Code, from adding the marketplace to installing plugins and configuring AWS MCP tools. By the end of this guide, you will have a working development environment with access to AWS development capabilities through Claude Code.

For detailed installation instructions, see [Installation](#2.1). For comprehensive MCP server configuration, see [MCP Setup](#2.2).

## Prerequisites

Before installing AWS Skills, ensure you have:

- **Claude Code** installed and running (CLI or IDE)
- **Python 3.10+** with `uvx` (for MCP servers that provide AWS API access)
- **AWS credentials** configured locally (optional, required only for MCP servers that access AWS APIs)
- **Node.js 18+** (for CDK-based development)

Some plugins can function with documentation-only access if AWS credentials are not configured. The `aws-mcp-setup` skill will guide you through configuration options when first invoked.

Sources: [README.md:68-87]()

## Installation Overview

The AWS Skills system follows a strict installation order due to plugin dependencies. All domain plugins (`aws-cdk`, `aws-cost-ops`, `serverless-eda`, `aws-agentic-ai`) depend on the foundational `aws-common` plugin.

### Installation Flow

```mermaid
graph TB
    Start["User starts installation"]
    
    Step1["Execute: /plugin marketplace add<br/>zxkane/aws-skills"]
    Step2["Execute: /plugin install<br/>aws-common@aws-skills"]
    Step3["Execute: /plugin install<br/>{domain-plugin}@aws-skills"]
    
    Registry["marketplace.json loaded<br/>5 plugins registered<br/>Version 2.2.0"]
    
    CommonPlugin["aws-common v1.0.0 installed<br/>Source: ./plugins/aws-common<br/>Skill: aws-mcp-setup"]
    
    DomainPlugins["Domain plugins installed:<br/>- aws-cdk v1.2.0<br/>- aws-cost-ops v1.2.0<br/>- serverless-eda v1.2.0<br/>- aws-agentic-ai v1.2.0"]
    
    MCPCheck{"MCP tools<br/>configured?"}
    
    SetupGuide["aws-mcp-setup skill<br/>auto-loads to guide<br/>configuration"]
    
    Ready["Ready for development"]
    
    Start --> Step1
    Step1 --> Registry
    Registry --> Step2
    Step2 --> CommonPlugin
    CommonPlugin --> Step3
    Step3 --> DomainPlugins
    DomainPlugins --> MCPCheck
    MCPCheck -->|"No"| SetupGuide
    MCPCheck -->|"Yes"| Ready
    SetupGuide --> Ready
```

**Diagram: Plugin Installation Sequence and Dependency Flow**

Sources: [.claude-plugin/marketplace.json:1-152](), [README.md:68-87]()

## Quick Start Commands

Execute these commands in Claude Code to install the complete AWS Skills ecosystem:

```bash
# Step 1: Add the marketplace registry
/plugin marketplace add zxkane/aws-skills

# Step 2: Install the foundational plugin (REQUIRED FIRST)
/plugin install aws-common@aws-skills

# Step 3: Install domain plugins as needed
/plugin install aws-cdk@aws-skills           # Infrastructure as Code
/plugin install aws-cost-ops@aws-skills      # Cost & Operations
/plugin install serverless-eda@aws-skills    # Event-Driven Architecture
/plugin install aws-agentic-ai@aws-skills    # Bedrock AgentCore
```

Each `/plugin install` command loads the plugin definition from [.claude-plugin/marketplace.json]() and symlinks the skill directories into Claude Code's runtime environment.

Sources: [README.md:70-87](), [.claude-plugin/marketplace.json:11-151]()

## Plugin Registry Structure

The marketplace registry at [.claude-plugin/marketplace.json]() defines all available plugins:

| Plugin | Version | Category | Skills | MCP Servers | Dependencies |
|--------|---------|----------|--------|-------------|--------------|
| `aws-common` | 1.0.0 | development | `aws-mcp-setup` | 0 | None (foundation) |
| `aws-cdk` | 1.2.0 | development | `aws-cdk-development` | 1 (`cdk`) | `aws-common` |
| `aws-cost-ops` | 1.2.0 | operations | `aws-cost-operations` | 3 (`pricing`, `costexp`, `cw`) | `aws-common` |
| `serverless-eda` | 1.2.0 | development | `aws-serverless-eda` | 0 | `aws-common`, `aws-cdk` |
| `aws-agentic-ai` | 1.2.0 | development | `aws-agentic-ai` | 0 | `aws-common` |

The `source` field in each plugin definition points to the local directory containing the skill implementation (e.g., `./plugins/aws-common`).

Sources: [.claude-plugin/marketplace.json:11-151]()

## Dependency Resolution

When a domain plugin is loaded, Claude Code automatically resolves and loads its dependencies through the `skills` field in the skill frontmatter. This creates a dependency chain that ensures required capabilities are always available.

```mermaid
graph TB
    subgraph "Automatic Dependency Loading"
        User["User invokes skill"]
        
        SkillCDK["aws-cdk-development skill<br/>File: plugins/aws-cdk/skills/aws-cdk-development/SKILL.md<br/>Frontmatter: skills: [aws-mcp-setup]"]
        
        SkillServerless["aws-serverless-eda skill<br/>File: plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md<br/>Frontmatter: skills: [aws-mcp-setup, aws-cdk-development]"]
        
        SkillCost["aws-cost-operations skill<br/>File: plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md<br/>Frontmatter: skills: [aws-mcp-setup]"]
        
        SkillAgentic["aws-agentic-ai skill<br/>File: plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md<br/>Frontmatter: skills: [aws-mcp-setup]"]
        
        SkillCommon["aws-mcp-setup skill<br/>File: plugins/aws-common/skills/aws-mcp-setup/SKILL.md<br/>MCP configuration and documentation access"]
    end
    
    User -->|"Invoke CDK skill"| SkillCDK
    User -->|"Invoke EDA skill"| SkillServerless
    User -->|"Invoke Cost skill"| SkillCost
    User -->|"Invoke Agentic skill"| SkillAgentic
    
    SkillCDK -.->|"Auto-load dependency"| SkillCommon
    SkillServerless -.->|"Auto-load dependency"| SkillCommon
    SkillServerless -.->|"Auto-load dependency"| SkillCDK
    SkillCost -.->|"Auto-load dependency"| SkillCommon
    SkillAgentic -.->|"Auto-load dependency"| SkillCommon
```

**Diagram: Skill Dependency Chain with File Paths**

The frontmatter `skills` array in each `SKILL.md` file declares dependencies that Claude Code automatically loads before executing the skill. This ensures that `aws-mcp-setup` is always available when needed, without requiring manual invocation.

Sources: [.claude-plugin/marketplace.json:27-29](), [.claude-plugin/marketplace.json:46-47](), [.claude-plugin/marketplace.json:77-78](), [.claude-plugin/marketplace.json:128-129](), [.claude-plugin/marketplace.json:147-148]()

## MCP Server Configuration

Plugins that integrate AWS services through MCP servers define them in the `mcpServers` field of [.claude-plugin/marketplace.json](). These servers launch on-demand via the `uvx` command with the `stdio` protocol.

### MCP Server Definitions

```mermaid
graph LR
    subgraph "Plugin MCP Server Configuration"
        CDKPlugin["aws-cdk plugin<br/>marketplace.json:49-60"]
        CostPlugin["aws-cost-ops plugin<br/>marketplace.json:80-111"]
        
        CDKServer["cdk server<br/>Command: uvx awslabs.cdk-mcp-server@latest<br/>Protocol: stdio<br/>Env: FASTMCP_LOG_LEVEL=ERROR"]
        
        PricingServer["pricing server<br/>Command: uvx awslabs.aws-pricing-mcp-server@latest<br/>Protocol: stdio"]
        
        CostExpServer["costexp server<br/>Command: uvx awslabs.cost-explorer-mcp-server@latest<br/>Protocol: stdio"]
        
        CWServer["cw server<br/>Command: uvx awslabs.cloudwatch-mcp-server@latest<br/>Protocol: stdio"]
    end
    
    subgraph "AWS Services"
        CDKAPI["AWS CDK/<br/>CloudFormation"]
        PricingAPI["AWS Pricing API"]
        CostAPI["AWS Cost Explorer"]
        CWAPI["Amazon CloudWatch"]
    end
    
    CDKPlugin --> CDKServer
    CostPlugin --> PricingServer
    CostPlugin --> CostExpServer
    CostPlugin --> CWServer
    
    CDKServer --> CDKAPI
    PricingServer --> PricingAPI
    CostExpServer --> CostAPI
    CWServer --> CWAPI
```

**Diagram: MCP Server Deployment and AWS Service Mapping**

Each MCP server is launched with:
- `type: stdio` - standard input/output communication protocol
- `command: uvx` - Python package executor
- `args: ["awslabs.{server}-mcp-server@latest"]` - MCP server package at latest version
- `env: {FASTMCP_LOG_LEVEL: "ERROR"}` - logging configuration

Sources: [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111]()

## Initial Configuration Check

When a skill is first invoked, it performs an availability check for MCP tools. If MCP servers are not configured, the `aws-mcp-setup` skill automatically loads to guide configuration.

### Configuration Options

The `aws-mcp-setup` skill offers two configuration paths:

| Option | Requirements | Capabilities |
|--------|-------------|-------------|
| **Full AWS MCP Server** | Python 3.10+, `uvx`, AWS credentials | Full AWS API access + documentation search |
| **AWS Documentation MCP** | None (uses public endpoints) | Documentation search only |

Users without AWS credentials or Python can still access AWS documentation through the documentation-only MCP server. This enables architectural guidance and best practices without requiring AWS account access.

Sources: [README.md:9-16]()

## Verification Steps

After installation, verify the setup:

1. **Check installed plugins**:
   ```bash
   /plugin list
   ```
   Expected output should show `aws-common` and any domain plugins installed.

2. **Verify skill availability**:
   ```bash
   /skills
   ```
   Should list available skills including `aws-mcp-setup` and any domain skills.

3. **Test MCP connectivity** (if configured):
   Invoke any domain skill. If MCP tools are not configured, the `aws-mcp-setup` skill will automatically guide you through setup.

4. **Confirm AWS credentials** (for full MCP access):
   ```bash
   aws sts get-caller-identity
   ```
   This command verifies AWS CLI configuration. Some skills use `PreToolUse` hooks to run this check automatically before AWS operations.

Sources: [README.md:68-87]()

## Next Steps

- For detailed installation procedures and troubleshooting, see [Installation](#2.1)
- For comprehensive MCP server configuration including credential setup and server selection, see [MCP Setup](#2.2)
- For understanding the plugin architecture and skill execution model, see [Architecture](#3)
- For guidance on using specific plugins, see [Plugins](#4)

Sources: [README.md:1-284](), [.claude-plugin/marketplace.json:1-152]()

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



This document provides step-by-step instructions for installing plugins from the AWS Skills marketplace. Installation must follow a specific dependency order to ensure proper plugin functionality.

**Scope**: This page covers marketplace registration, plugin installation commands, and dependency verification. For configuring AWS MCP tools after installation, see [MCP Setup](#2.2). For modifying or developing plugins locally, see [Local Development Setup](#5.1).

## Prerequisites

Before installing plugins, ensure the following requirements are met:

| Requirement | Description |
|-------------|-------------|
| Claude Code | Claude Code IDE or CLI must be installed and authenticated |
| Marketplace Support | Claude Code version must support plugin marketplace functionality |
| Network Access | Internet connection to download plugins from GitHub repository |

## Installation Sequence

The installation process follows a mandatory three-step sequence. Deviating from this order will cause dependency resolution failures.

### Installation Flow

```mermaid
graph TB
    Start["User initiates installation"]
    
    AddMarket["Step 1: Add Marketplace<br/>/plugin marketplace add zxkane/aws-skills"]
    
    CheckMarket{"Marketplace<br/>registry<br/>loaded?"}
    
    InstallCommon["Step 2: Install aws-common<br/>/plugin install aws-common@aws-skills"]
    
    CheckCommon{"aws-common<br/>v1.0.0<br/>installed?"}
    
    InstallDomain["Step 3: Install Domain Plugins<br/>/plugin install aws-cdk@aws-skills<br/>/plugin install aws-cost-ops@aws-skills<br/>/plugin install serverless-eda@aws-skills<br/>/plugin install aws-agentic-ai@aws-skills"]
    
    Verify["Verify Installation<br/>/plugin list"]
    
    Complete["Installation Complete"]
    
    ErrorMarket["Error: Cannot load plugins<br/>without marketplace"]
    ErrorCommon["Error: Missing aws-common dependency"]
    
    Start --> AddMarket
    AddMarket --> CheckMarket
    CheckMarket -->|No| ErrorMarket
    CheckMarket -->|Yes| InstallCommon
    InstallCommon --> CheckCommon
    CheckCommon -->|No| ErrorCommon
    CheckCommon -->|Yes| InstallDomain
    InstallDomain --> Verify
    Verify --> Complete
```

**Sources**: [.claude-plugin/marketplace.json:1-152](), [README.md:68-87]()

## Step 1: Add Marketplace

The marketplace registry must be added before any plugins can be installed. This registers the remote repository containing plugin definitions.

```bash
/plugin marketplace add zxkane/aws-skills
```

This command performs the following operations:

1. Fetches `marketplace.json` from `https://github.com/zxkane/aws-skills`
2. Validates the marketplace metadata version (currently `2.2.0`)
3. Registers 5 available plugins in the Claude Code registry
4. Makes plugins available for installation via `@aws-skills` suffix

### Marketplace Structure

```mermaid
graph LR
    Marketplace["marketplace.json<br/>version: 2.2.0"]
    
    Owner["owner<br/>name: Kane Zhu<br/>email: me@kane.mx"]
    
    Meta["metadata<br/>description: AWS development skills<br/>version: 2.2.0"]
    
    PluginArray["plugins array<br/>5 registered plugins"]
    
    Common["aws-common<br/>v1.0.0<br/>source: ./plugins/aws-common"]
    CDK["aws-cdk<br/>v1.2.0<br/>source: ./plugins/aws-cdk"]
    Cost["aws-cost-ops<br/>v1.2.0<br/>source: ./plugins/aws-cost-ops"]
    Serverless["serverless-eda<br/>v1.2.0<br/>source: ./plugins/serverless-eda"]
    Agentic["aws-agentic-ai<br/>v1.2.0<br/>source: ./plugins/aws-agentic-ai"]
    
    Marketplace --> Owner
    Marketplace --> Meta
    Marketplace --> PluginArray
    
    PluginArray --> Common
    PluginArray --> CDK
    PluginArray --> Cost
    PluginArray --> Serverless
    PluginArray --> Agentic
```

**Sources**: [.claude-plugin/marketplace.json:1-10](), [.claude-plugin/marketplace.json:11-151]()

## Step 2: Install Foundation Plugin (aws-common)

The `aws-common` plugin **must be installed first** as it provides the `aws-mcp-setup` skill that all other plugins depend on.

```bash
/plugin install aws-common@aws-skills
```

### Why aws-common is Required First

| Aspect | Details |
|--------|---------|
| Version | `1.0.0` (stable foundation, lower version than domain plugins) |
| Category | `development` |
| Provides | `aws-mcp-setup` skill for MCP server configuration |
| Source Path | `./plugins/aws-common` |
| Skills Registered | `./skills/aws-mcp-setup` |
| Strict Mode | `false` (allows flexible skill invocation) |

The plugin installs from the source directory defined in the marketplace entry at [.claude-plugin/marketplace.json:25](). When installed, Claude Code:

1. Downloads files from `plugins/aws-common/` directory
2. Registers the `aws-mcp-setup` skill defined at [.claude-plugin/marketplace.json:28]()
3. Makes the skill available for dependency auto-loading by other plugins

**Sources**: [.claude-plugin/marketplace.json:11-30](), [README.md:79-80]()

## Step 3: Install Domain Plugins

After `aws-common` is installed, domain plugins can be installed in any order. Each plugin automatically resolves its dependency on `aws-common`.

### Individual Plugin Installation

```bash
# Infrastructure as Code
/plugin install aws-cdk@aws-skills

# Cost Optimization and Operations
/plugin install aws-cost-ops@aws-skills

# Serverless and Event-Driven Architecture
/plugin install serverless-eda@aws-skills

# AI Agent Development with Bedrock AgentCore
/plugin install aws-agentic-ai@aws-skills
```

### Plugin Comparison

| Plugin Name | Version | MCP Servers | Primary Skills | Source Path |
|-------------|---------|-------------|----------------|-------------|
| `aws-cdk` | 1.2.0 | 1 (`cdk`) | `aws-cdk-development` | `./plugins/aws-cdk` |
| `aws-cost-ops` | 1.2.0 | 3 (`pricing`, `costexp`, `cw`) | `aws-cost-operations` | `./plugins/aws-cost-ops` |
| `serverless-eda` | 1.2.0 | 0 (pattern-based) | `aws-serverless-eda` | `./plugins/serverless-eda` |
| `aws-agentic-ai` | 1.2.0 | 0 (pattern-based) | `aws-agentic-ai` | `./plugins/aws-agentic-ai` |

**Sources**: [.claude-plugin/marketplace.json:31-61](), [.claude-plugin/marketplace.json:62-112](), [.claude-plugin/marketplace.json:113-131](), [.claude-plugin/marketplace.json:132-150]()

### MCP Server Provisioning

Plugins with `mcpServers` configuration automatically provision MCP server integrations during installation:

```mermaid
graph TB
    subgraph "aws-cdk Plugin"
        CDKPlugin["aws-cdk plugin<br/>source: ./plugins/aws-cdk"]
        CDKServer["mcpServers.cdk<br/>type: stdio<br/>command: uvx<br/>args: awslabs.cdk-mcp-server@latest"]
    end
    
    subgraph "aws-cost-ops Plugin"
        CostPlugin["aws-cost-ops plugin<br/>source: ./plugins/aws-cost-ops"]
        PriceServer["mcpServers.pricing<br/>type: stdio<br/>command: uvx<br/>args: awslabs.aws-pricing-mcp-server@latest"]
        CostExpServer["mcpServers.costexp<br/>type: stdio<br/>command: uvx<br/>args: awslabs.cost-explorer-mcp-server@latest"]
        CWServer["mcpServers.cw<br/>type: stdio<br/>command: uvx<br/>args: awslabs.cloudwatch-mcp-server@latest"]
    end
    
    CDKPlugin --> CDKServer
    CostPlugin --> PriceServer
    CostPlugin --> CostExpServer
    CostPlugin --> CWServer
    
    CDKServer --> Env1["env.FASTMCP_LOG_LEVEL: ERROR"]
    PriceServer --> Env2["env.FASTMCP_LOG_LEVEL: ERROR"]
    CostExpServer --> Env3["env.FASTMCP_LOG_LEVEL: ERROR"]
    CWServer --> Env4["env.FASTMCP_LOG_LEVEL: ERROR"]
```

All MCP servers use the `stdio` protocol type and are launched with `uvx` pointing to `@latest` versions from the `awslabs` namespace. The `FASTMCP_LOG_LEVEL` is set to `ERROR` to minimize log verbosity.

**Sources**: [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111]()

## Dependency Resolution

Claude Code automatically resolves skill dependencies when a plugin is installed or invoked. The dependency graph ensures `aws-common` is loaded before any domain plugin functionality.

### Skill Dependency Chain

```mermaid
graph TB
    CommonSkill["aws-mcp-setup skill<br/>from aws-common plugin"]
    
    CDKSkill["aws-cdk-development skill<br/>skills: [aws-mcp-setup]"]
    
    CostSkill["aws-cost-operations skill<br/>skills: [aws-mcp-setup]"]
    
    ServerlessSkill["aws-serverless-eda skill<br/>skills: [aws-mcp-setup, aws-cdk-development]"]
    
    AgenticSkill["aws-agentic-ai skill<br/>skills: [aws-mcp-setup]"]
    
    CDKSkill -.depends on.-> CommonSkill
    CostSkill -.depends on.-> CommonSkill
    ServerlessSkill -.depends on.-> CommonSkill
    ServerlessSkill -.depends on.-> CDKSkill
    AgenticSkill -.depends on.-> CommonSkill
    
    CDKSkill -.also depends on.-> CommonSkill
```

The `serverless-eda` plugin has a dual dependency: it depends on both `aws-mcp-setup` (from `aws-common`) and `aws-cdk-development` (from `aws-cdk`). This allows it to leverage both documentation access and CDK infrastructure patterns.

**Sources**: [.claude-plugin/marketplace.json:27-29](), [.claude-plugin/marketplace.json:46-48](), [.claude-plugin/marketplace.json:77-79](), [.claude-plugin/marketplace.json:128-130](), [.claude-plugin/marketplace.json:147-149]()

## Installation Verification

After installing plugins, verify the installation using Claude Code commands.

### List Installed Plugins

```bash
/plugin list
```

Expected output should include:

| Plugin Name | Version | Status | Skills Loaded |
|-------------|---------|--------|---------------|
| `aws-common` | 1.0.0 | Installed | `aws-mcp-setup` |
| `aws-cdk` | 1.2.0 | Installed | `aws-cdk-development` |
| `aws-cost-ops` | 1.2.0 | Installed | `aws-cost-operations` |
| `serverless-eda` | 1.2.0 | Installed | `aws-serverless-eda` |
| `aws-agentic-ai` | 1.2.0 | Installed | `aws-agentic-ai` |

### List Available Skills

```bash
/skills
```

This command displays all skills from installed plugins. Each skill should appear with its description from the skill frontmatter metadata.

### Test Skill Invocation

Verify skill functionality by invoking a skill:

```
Use the aws-mcp-setup skill to check MCP server configuration
```

If the skill is properly installed, Claude Code will load it and execute according to its SKILL.md definition.

**Sources**: [README.md:68-87]()

## Troubleshooting

### Common Installation Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Plugin not found" | Marketplace not added | Run `/plugin marketplace add zxkane/aws-skills` first |
| "Dependency not met" | `aws-common` not installed | Install `aws-common` before domain plugins |
| "MCP server failed to start" | Missing `uvx` or Python | Install prerequisites (see [MCP Setup](#2.2)) |
| "Permission denied" | Network restrictions | Check firewall and GitHub access |
| "Version conflict" | Outdated marketplace cache | Remove and re-add marketplace |

### Dependency Error Example

If attempting to install `aws-cdk` before `aws-common`:

```
Error: Cannot resolve skill dependency 'aws-mcp-setup'
Required by: aws-cdk-development skill
Install aws-common plugin first
```

This error occurs because the skill definition at the plugin source references `aws-mcp-setup` in its frontmatter `skills:` array, but the skill is not available in Claude Code's registry.

### MCP Server Launch Issues

If MCP servers fail to launch (e.g., for `aws-cdk` or `aws-cost-ops` plugins), the error typically indicates missing prerequisites:

```
Error: MCP server 'cdk' failed to start
Command: uvx awslabs.cdk-mcp-server@latest
Check if uvx is installed and accessible
```

MCP server issues should be resolved by following [MCP Setup](#2.2) to install required tools like `uvx`, Python, and AWS credentials.

**Sources**: [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111]()

## Plugin Categories

The marketplace organizes plugins into categories for easier discovery:

```mermaid
graph LR
    Marketplace["marketplace.json<br/>5 plugins"]
    
    DevCategory["category: development<br/>4 plugins"]
    OpsCategory["category: operations<br/>1 plugin"]
    
    Common["aws-common"]
    CDK["aws-cdk"]
    Serverless["serverless-eda"]
    Agentic["aws-agentic-ai"]
    Cost["aws-cost-ops"]
    
    Marketplace --> DevCategory
    Marketplace --> OpsCategory
    
    DevCategory --> Common
    DevCategory --> CDK
    DevCategory --> Serverless
    DevCategory --> Agentic
    
    OpsCategory --> Cost
```

- **Development**: Plugins focused on building and deploying AWS applications (`aws-common`, `aws-cdk`, `serverless-eda`, `aws-agentic-ai`)
- **Operations**: Plugins focused on operating and monitoring AWS resources (`aws-cost-ops`)

**Sources**: [.claude-plugin/marketplace.json:24](), [.claude-plugin/marketplace.json:43](), [.claude-plugin/marketplace.json:74](), [.claude-plugin/marketplace.json:125](), [.claude-plugin/marketplace.json:144]()

## Next Steps

After successfully installing plugins:

1. **Configure MCP Tools**: Follow [MCP Setup](#2.2) to configure AWS MCP servers for live AWS data access
2. **Explore Plugin Capabilities**: Review plugin documentation at [Plugins](#4)
3. **Start Development**: Begin using skills through Claude Code IDE or CLI

Installation is complete when all required plugins are listed in `/plugin list` and their skills appear in `/skills`. MCP server configuration is the next critical step for enabling full AWS integration functionality.

---

# Page: MCP Setup

# MCP Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/aws-mcp-setup.md](docs/aws-mcp-setup.md)
- [plugins/aws-common/skills/aws-mcp-setup/SKILL.md](plugins/aws-common/skills/aws-mcp-setup/SKILL.md)

</details>



This document provides a detailed guide for configuring AWS MCP (Model Context Protocol) tools that enable AWS Skills to query up-to-date AWS documentation and APIs. Configuration involves adding MCP server entries to Claude Code's configuration files and verifying that the required tools are available.

**Scope**: This page covers MCP server configuration only. For plugin installation, see [Installation](#2.1). For information about how skills use MCP tools internally, see [MCP Server Integration](#3.3).

## Configuration Architecture

Claude Code uses a hierarchical configuration system where MCP servers can be defined at multiple scopes. Configuration files are merged with local settings taking precedence over broader scopes.

### Configuration File Hierarchy

```mermaid
graph TB
    Request["Claude Code Skill Invocation"]
    
    subgraph "Configuration Resolution (Precedence Order)"
        Local[".claude.json<br/>(Project Directory)<br/>Scope: Local/Personal"]
        Project[".mcp.json<br/>(Project Root)<br/>Scope: Team-Shared"]
        User["~/.claude.json<br/>(Home Directory)<br/>Scope: Cross-Project"]
        Enterprise["System Directories<br/>Scope: Organization-Wide"]
    end
    
    subgraph "MCP Server Registry"
        MCPServers["mcpServers: {<br/>  'aws-mcp': {...},<br/>  'awsdocs': {...}<br/>}"]
    end
    
    subgraph "Tool Availability"
        Tools["Available Tools:<br/>mcp__aws-mcp__aws___*<br/>mcp__awsdocs__aws___*"]
    end
    
    Request --> Local
    Local -->|"if not found"| Project
    Project -->|"if not found"| User
    User -->|"if not found"| Enterprise
    
    Local --> MCPServers
    Project --> MCPServers
    User --> MCPServers
    Enterprise --> MCPServers
    
    MCPServers --> Tools
    Tools --> Request
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:31-38](), [docs/aws-mcp-setup.md:26-33]()

| Scope | File Path | Use Case | Priority |
|-------|-----------|----------|----------|
| Local | `.claude.json` in project directory | Experimentation, temporary overrides | 1 (highest) |
| Project | `.mcp.json` in project root | Team-shared configuration | 2 |
| User | `~/.claude.json` in home directory | Personal defaults across projects | 3 |
| Enterprise | System-managed directories | Organization-wide policies | 4 (lowest) |

## Checking Existing Configuration

Before adding new MCP server configuration, verify whether AWS MCP tools are already available.

### Method A: Check Available Tools (Recommended)

Run the `/mcp` command in Claude Code to list active MCP servers. Look for tool name patterns:

| Pattern | Indicates | Capabilities |
|---------|-----------|--------------|
| `mcp__aws-mcp__*` or `mcp__aws__*` | Full AWS MCP Server configured | API calls + documentation search |
| `mcp__*awsdocs*__aws___*` | AWS Documentation MCP configured | Documentation search only |

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:17-27]()

### Method B: Check Configuration Files

```bash
# Check project configuration
cat .mcp.json 2>/dev/null | grep -E '"(aws-mcp|aws|awsdocs)"'

# Check user configuration
cat ~/.claude.json 2>/dev/null | grep -E '"(aws-mcp|aws|awsdocs)"'

# List all MCP servers
claude mcp list
```

If AWS MCP servers are already configured, no further setup is required.

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:40-51](), [docs/aws-mcp-setup.md:35-46]()

## Configuration Options

Two MCP server options are available, each with different prerequisites and capabilities:

### Decision Tree

```mermaid
graph TB
    Start["Need AWS MCP Setup"]
    
    CheckUVX{"uvx command<br/>available?"}
    CheckCreds{"AWS credentials<br/>configured?"}
    
    FullMCP["Option A:<br/>Full AWS MCP Server<br/><br/>Command: uvx<br/>Package: mcp-proxy-for-aws@latest<br/>Protocol: stdio"]
    
    DocMCP["Option B:<br/>AWS Documentation MCP<br/><br/>Type: http<br/>URL: knowledge-mcp.global.api.aws<br/>Protocol: HTTP"]
    
    VerifyUVX["Verify: which uvx"]
    VerifyCreds["Verify: aws sts get-caller-identity"]
    
    ToolsA["Tools Available:<br/>mcp__aws-mcp__aws___search_documentation<br/>mcp__aws-mcp__aws___call_aws<br/>mcp__aws-mcp__aws___read_documentation"]
    
    ToolsB["Tools Available:<br/>mcp__awsdocs__aws___search_documentation<br/>mcp__awsdocs__aws___read_documentation"]
    
    Start --> CheckUVX
    CheckUVX -->|"Yes"| CheckCreds
    CheckUVX -->|"No"| DocMCP
    
    CheckCreds -->|"Yes"| FullMCP
    CheckCreds -->|"No"| DocMCP
    
    FullMCP -.->|"requires"| VerifyUVX
    FullMCP -.->|"requires"| VerifyCreds
    
    FullMCP --> ToolsA
    DocMCP --> ToolsB
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:55-67](), [docs/aws-mcp-setup.md:50-62]()

### Option Comparison

| Feature | Full AWS MCP Server | AWS Documentation MCP |
|---------|-------------------|---------------------|
| **Requirements** | Python 3.10+, uvx, AWS credentials | None |
| **IAM Permissions** | `aws-mcp:InvokeMCP`, `aws-mcp:CallReadOnlyTool`, `aws-mcp:CallReadWriteTool` | None |
| **Documentation Search** | ✓ | ✓ |
| **API Execution** | ✓ | ✗ |
| **Configuration File** | `.claude.json` or `.mcp.json` | `.claude.json` or `.mcp.json` |
| **Launch Method** | stdio via uvx | HTTP endpoint |

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:10-15](), [docs/aws-mcp-setup.md:6-10]()

## Option A: Full AWS MCP Server Setup

This option provides complete AWS API access plus documentation search capabilities.

### Prerequisites

```bash
# Verify Python 3.10+
python3 --version

# Install uv if not present
pip install uv

# Verify uvx is available
which uvx

# Verify AWS credentials
aws sts get-caller-identity
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:55-67](), [docs/aws-mcp-setup.md:50-62]()

### IAM Permissions

The AWS IAM principal used must have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "aws-mcp:InvokeMCP",
      "aws-mcp:CallReadOnlyTool",
      "aws-mcp:CallReadWriteTool"
    ],
    "Resource": "*"
  }]
}
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:77-91](), [docs/aws-mcp-setup.md:72-86]()

### Configuration

Add the following to your chosen configuration file (`.claude.json`, `.mcp.json`, or `~/.claude.json`):

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=us-west-2"
      ]
    }
  }
}
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:93-107](), [docs/aws-mcp-setup.md:88-102]()

### Credential Configuration Methods

#### Method 1: AWS Profile (Recommended for Development)

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--profile", "my-profile",
        "--metadata", "AWS_REGION=us-west-2"
      ]
    }
  }
}
```

#### Method 2: Environment Variables

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=us-west-2"
      ],
      "env": {
        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
        "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

#### Method 3: IAM Role (EC2/ECS/Lambda)

No additional configuration required. The MCP server automatically uses instance credentials.

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:109-130](), [docs/aws-mcp-setup.md:104-126]()

### Additional Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--region <region>` | Override AWS region | `--region us-east-1` |
| `--read-only` | Restrict to read-only tools | `--read-only` |
| `--log-level <level>` | Set logging verbosity | `--log-level debug` |

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:132-135](), [docs/aws-mcp-setup.md:127-130]()

### MCP Server Launch Sequence

```mermaid
graph LR
    Claude["Claude Code<br/>Skill Invocation"]
    
    Config["Configuration File<br/>.claude.json or .mcp.json<br/><br/>mcpServers.aws-mcp"]
    
    UVX["uvx launcher<br/>(uv package executor)"]
    
    Package["mcp-proxy-for-aws@latest<br/>(PyPI package)"]
    
    Server["MCP Server Process<br/>stdio protocol<br/>Args: region, profile, etc."]
    
    Tools["Available Tools:<br/>mcp__aws-mcp__aws___search_documentation<br/>mcp__aws-mcp__aws___read_documentation<br/>mcp__aws-mcp__aws___call_aws<br/>mcp__aws-mcp__aws___get_regional_availability"]
    
    AWS["AWS Services<br/>(via boto3/AWS SDK)"]
    
    Claude --> Config
    Config -->|"command: uvx"| UVX
    UVX -->|"downloads/executes"| Package
    Package --> Server
    Server --> Tools
    Tools --> Claude
    Server <-->|"API calls"| AWS
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:93-107]()

## Option B: AWS Documentation MCP Setup

This option provides documentation search capabilities without requiring AWS credentials or Python.

### Prerequisites

No prerequisites required. This option works with any Claude Code installation.

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:139-144](), [docs/aws-mcp-setup.md:134-139]()

### Configuration

Add the following to your chosen configuration file:

```json
{
  "mcpServers": {
    "awsdocs": {
      "type": "http",
      "url": "https://knowledge-mcp.global.api.aws"
    }
  }
}
```

The `awsdocs` key can be any name, but must match the pattern expected by tool name lookups (`mcp__*awsdocs*__aws___*`).

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:146-156](), [docs/aws-mcp-setup.md:141-151]()

### HTTP MCP Server Connection Flow

```mermaid
graph LR
    Claude["Claude Code<br/>Skill Invocation"]
    
    Config["Configuration File<br/><br/>mcpServers.awsdocs:<br/>  type: http<br/>  url: knowledge-mcp..."]
    
    HTTP["HTTP MCP Client<br/>(built-in to Claude Code)"]
    
    Endpoint["AWS Knowledge MCP<br/>knowledge-mcp.global.api.aws<br/><br/>Global HTTP endpoint"]
    
    Tools["Available Tools:<br/>mcp__awsdocs__aws___search_documentation<br/>mcp__awsdocs__aws___read_documentation<br/>mcp__awsdocs__aws___get_regional_availability"]
    
    Docs["AWS Documentation<br/>Service docs, API references,<br/>best practices"]
    
    Claude --> Config
    Config -->|"type: http"| HTTP
    HTTP <-->|"HTTPS requests"| Endpoint
    Endpoint --> Tools
    Tools --> Claude
    Endpoint <-->|"queries"| Docs
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:146-156]()

## Verification

After adding MCP server configuration, restart Claude Code and verify that tools are available.

### Tool Name Patterns

The MCP tool naming follows a standardized pattern: `mcp__<server-key>__<namespace>___<tool-name>`

#### Full AWS MCP Server Tools

Expected tool names:
- `mcp__aws-mcp__aws___search_documentation` - Search AWS documentation
- `mcp__aws-mcp__aws___read_documentation` - Read specific documentation pages
- `mcp__aws-mcp__aws___call_aws` - Execute AWS API calls
- `mcp__aws-mcp__aws___get_regional_availability` - Check service availability by region

#### AWS Documentation MCP Tools

Expected tool names:
- `mcp__awsdocs__aws___search_documentation` - Search AWS documentation
- `mcp__awsdocs__aws___read_documentation` - Read specific documentation pages
- `mcp__awsdocs__aws___get_regional_availability` - Check service availability by region

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:158-167](), [docs/aws-mcp-setup.md:153-161]()

### Verification Commands

```bash
# List all active MCP servers
claude mcp list

# Check for AWS MCP tools in available tools
# (Run in Claude Code IDE)
/mcp
```

### Integration with Skills

All AWS Skills automatically check for MCP tool availability through the `aws-mcp-setup` skill dependency:

```mermaid
graph TB
    UserSkill["User Invokes Skill<br/>(e.g., aws-cdk-development)"]
    
    Frontmatter["SKILL.md Frontmatter:<br/>skills: [aws-mcp-setup]"]
    
    AutoLoad["Auto-load Dependency:<br/>aws-mcp-setup skill<br/>(from aws-common plugin)"]
    
    Check{"MCP Tools<br/>Available?"}
    
    Use["Use MCP Tools:<br/>- search_documentation<br/>- read_documentation<br/>- call_aws (if Full MCP)"]
    
    Guide["Guide User:<br/>Show aws-mcp-setup skill<br/>instructions for configuration"]
    
    UserSkill --> Frontmatter
    Frontmatter --> AutoLoad
    AutoLoad --> Check
    
    Check -->|"Yes"| Use
    Check -->|"No"| Guide
    
    Use --> UserSkill
    Guide --> UserSkill
```

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:1-4]()

## Troubleshooting

### Common Issues

| Issue | Cause | Solution | Verification |
|-------|-------|----------|--------------|
| `uvx: command not found` | uv package manager not installed | Install with `pip install uv` or use Option B (AWS Documentation MCP) | Run `which uvx` |
| `AccessDenied` error | Missing IAM permissions | Add `aws-mcp:*` permissions to IAM policy | Check IAM policy document |
| `InvalidSignatureException` | AWS credential configuration issue | Verify credentials with `aws sts get-caller-identity` | Should return account/user info |
| Tools not appearing | MCP server not started | Restart Claude Code after configuration change | Run `/mcp` to list servers |
| Connection timeout | Network/proxy issue | Check network connectivity to `aws-mcp.us-east-1.api.aws` | Use `curl` to test endpoint |
| Wrong region tools | Region not specified | Add `--metadata "AWS_REGION=<region>"` to args | Check MCP server args in config |

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:169-176](), [docs/aws-mcp-setup.md:163-170]()

### Configuration File Validation

```bash
# Validate JSON syntax
jq . .mcp.json

# Check mcpServers key exists
jq '.mcpServers' .mcp.json

# List configured MCP servers
jq '.mcpServers | keys' .mcp.json
```

### Debug Mode

Enable detailed logging for the Full AWS MCP Server:

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--log-level", "debug",
        "--metadata", "AWS_REGION=us-west-2"
      ]
    }
  }
}
```

Logs will appear in Claude Code's MCP server output panel.

**Sources**: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:132-136]()

## Reference

- Full AWS MCP Server: https://github.com/aws/mcp-proxy-for-aws
- AWS Documentation MCP: https://knowledge-mcp.global.api.aws
- Configuration file format: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:93-156]()
- Skill dependency mechanism: See [Skills and Execution Model](#3.2)
- MCP server integration patterns: See [MCP Server Integration](#3.3)

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)

</details>



This document explains the internal architecture of the AWS Skills for Claude Code system. It covers the marketplace registry mechanism, standardized plugin structure, skill execution model with fork contexts and dependency resolution, and MCP server integration patterns.

For step-by-step installation instructions, see [Getting Started](#2). For detailed information about individual plugins, see [Plugins](#4). For contribution guidelines and local development, see [Development Guide](#5).

## System Overview

The AWS Skills system is a marketplace-based plugin architecture for Claude Code that extends the IDE with AWS development capabilities. The architecture consists of four primary layers:

1. **Marketplace Registry Layer** - Central registry defined in `marketplace.json` that manages plugin metadata, versions, and MCP server configurations
2. **Plugin Layer** - Five distinct plugins (`aws-common`, `aws-cdk`, `aws-cost-ops`, `serverless-eda`, `aws-agentic-ai`) following a standardized directory structure
3. **Skill Execution Layer** - Fork-based sub-agent execution with frontmatter-driven configuration, dependency auto-loading, and lifecycle hooks
4. **MCP Integration Layer** - Model Context Protocol servers providing real-time AWS service access via stdio communication

### Marketplace Registry Architecture

```mermaid
graph TB
    Registry["marketplace.json<br/>version: 2.2.0"]
    
    subgraph "Plugin Metadata Structure"
        Meta1["name: 'aws-common'<br/>version: '1.0.0'<br/>category: 'development'<br/>source: './plugins/aws-common'"]
        Meta2["name: 'aws-cdk'<br/>version: '1.2.0'<br/>mcpServers: {...}"]
        Meta3["name: 'aws-cost-ops'<br/>version: '1.2.0'<br/>mcpServers: {...}"]
        Meta4["name: 'serverless-eda'<br/>version: '1.2.0'"]
        Meta5["name: 'aws-agentic-ai'<br/>version: '1.2.0'"]
    end
    
    subgraph "MCP Server Configurations"
        MCP1["cdk: stdio + uvx<br/>awslabs.cdk-mcp-server"]
        MCP2["pricing: stdio + uvx<br/>awslabs.aws-pricing-mcp-server"]
        MCP3["costexp: stdio + uvx<br/>awslabs.cost-explorer-mcp-server"]
        MCP4["cw: stdio + uvx<br/>awslabs.cloudwatch-mcp-server"]
    end
    
    subgraph "Plugin Source Directories"
        Dir1["./plugins/aws-common/"]
        Dir2["./plugins/aws-cdk/"]
        Dir3["./plugins/aws-cost-ops/"]
        Dir4["./plugins/serverless-eda/"]
        Dir5["./plugins/aws-agentic-ai/"]
    end
    
    Registry --> Meta1
    Registry --> Meta2
    Registry --> Meta3
    Registry --> Meta4
    Registry --> Meta5
    
    Meta2 --> MCP1
    Meta3 --> MCP2
    Meta3 --> MCP3
    Meta3 --> MCP4
    
    Meta1 --> Dir1
    Meta2 --> Dir2
    Meta3 --> Dir3
    Meta4 --> Dir4
    Meta5 --> Dir5
```

**Marketplace Registry Architecture** - The `marketplace.json` file serves as the central registry, defining plugin metadata and MCP server configurations. Each plugin entry includes name, version, category, source path, and optional `mcpServers` object.

Sources: [.claude-plugin/marketplace.json:1-152](), [README.md:227-264]()

## Plugin Structure

Each plugin follows a standardized directory structure with required and optional components:

| Component | Required | Purpose |
|-----------|----------|---------|
| `skills/<skill-name>/SKILL.md` | Yes | Main skill definition with frontmatter configuration |
| `skills/<skill-name>/references/*.md` | No | Detailed reference documentation and patterns |
| `scripts/*.sh` | No | Utility scripts (e.g., validation, deployment) |
| `services/` | No | Service-specific documentation (used by `aws-agentic-ai`) |
| `cross-service/` | No | Cross-service integration patterns |

### Plugin Directory Layout

```mermaid
graph TB
    subgraph "Plugin Root: plugins/{plugin-name}/"
        Skills["skills/{skill-name}/"]
        
        subgraph "Required Components"
            SkillMD["SKILL.md<br/>Frontmatter + Content"]
        end
        
        subgraph "Optional Components"
            Refs["references/<br/>*.md files"]
            Scripts["scripts/<br/>*.sh files"]
            Services["services/<br/>Service docs"]
            Cross["cross-service/<br/>Integration patterns"]
        end
    end
    
    subgraph "SKILL.md Structure"
        FM["Frontmatter (YAML)<br/>---<br/>name, description, context,<br/>model, skills, allowed-tools, hooks<br/>---"]
        Content["Markdown Content<br/>Instructions and guidance"]
    end
    
    subgraph "Real Plugin Examples"
        Ex1["aws-cdk:<br/>references/cdk-patterns.md<br/>scripts/validate-stack.sh"]
        Ex2["aws-cost-ops:<br/>references/operations-patterns.md<br/>references/cloudwatch-alarms.md"]
        Ex3["aws-agentic-ai:<br/>services/{gateway,runtime,memory,...}<br/>cross-service/"]
    end
    
    Skills --> SkillMD
    Skills --> Refs
    Skills --> Scripts
    Skills --> Services
    Skills --> Cross
    
    SkillMD --> FM
    SkillMD --> Content
```

**Plugin Directory Layout** - Each plugin's `skills/` directory contains at least one skill with a `SKILL.md` file. The frontmatter section configures execution parameters, while the markdown content provides instructions. Optional directories contain supporting materials.

Sources: [README.md:227-264](), [CLAUDE.md:21-24]()

## Skill Execution Model

Skills execute in isolated fork contexts (sub-agents) with declarative configuration via YAML frontmatter. The execution model includes dependency resolution, tool permissions, model selection, and lifecycle hooks.

### Frontmatter Configuration Schema

```mermaid
graph LR
    subgraph "SKILL.md Frontmatter Fields"
        Name["name<br/>Skill identifier"]
        Desc["description<br/>Purpose statement"]
        Context["context: fork<br/>Isolated execution"]
        Model["model: sonnet<br/>Model selection"]
        
        subgraph "Dependency Management"
            SkillsDeps["skills: []<br/>Auto-load sub-skills"]
        end
        
        subgraph "Permission Control"
            Tools["allowed-tools: []<br/>MCP/Bash whitelist"]
        end
        
        subgraph "Lifecycle Management"
            Hooks["hooks:<br/>PreToolUse, etc."]
        end
    end
    
    subgraph "Execution Flow"
        Fork["Fork Context<br/>Sub-agent isolation"]
        AutoLoad["Dependency Auto-loading<br/>Recursive resolution"]
        ToolCheck["Tool Permission Validation<br/>Wildcard matching"]
        HookExec["Hook Execution<br/>once: true support"]
    end
    
    Context --> Fork
    SkillsDeps --> AutoLoad
    Tools --> ToolCheck
    Hooks --> HookExec
```

**Frontmatter Configuration Schema** - The YAML frontmatter defines seven key configuration areas: name/description metadata, fork execution context, model selection, recursive skill dependencies, tool permissions with wildcard support, and lifecycle hooks with execution control.

Sources: [CLAUDE.md:56-77]()

### Skill Dependency Resolution

The `skills:` frontmatter field creates an auto-loading dependency chain. When a skill is invoked, Claude Code automatically loads all declared dependencies recursively:

```mermaid
graph TB
    User["User Invokes Skill"]
    
    subgraph "Dependency Graph"
        Common["aws-mcp-setup<br/>aws-common plugin<br/>No dependencies"]
        
        CDK["aws-cdk-development<br/>aws-cdk plugin<br/>skills: [aws-mcp-setup]"]
        
        Cost["aws-cost-operations<br/>aws-cost-ops plugin<br/>skills: [aws-mcp-setup]"]
        
        Serverless["aws-serverless-eda<br/>serverless-eda plugin<br/>skills: [aws-mcp-setup,<br/>aws-cdk-development]"]
        
        Agentic["aws-agentic-ai<br/>aws-agentic-ai plugin<br/>skills: [aws-mcp-setup]"]
    end
    
    subgraph "Auto-Loading Sequence"
        Seq1["1. Load requested skill"]
        Seq2["2. Parse skills: [] frontmatter"]
        Seq3["3. Recursively load dependencies"]
        Seq4["4. Verify all skills loaded"]
        Seq5["5. Execute skill in fork context"]
    end
    
    User --> CDK
    User --> Cost
    User --> Serverless
    User --> Agentic
    
    CDK -.auto-loads.-> Common
    Cost -.auto-loads.-> Common
    Serverless -.auto-loads.-> Common
    Serverless -.auto-loads.-> CDK
    Agentic -.auto-loads.-> Common
    
    User --> Seq1
    Seq1 --> Seq2
    Seq2 --> Seq3
    Seq3 --> Seq4
    Seq4 --> Seq5
```

**Skill Dependency Resolution** - All domain plugins depend on `aws-mcp-setup` from the `aws-common` plugin. The `serverless-eda` plugin has a two-level dependency chain, auto-loading both `aws-mcp-setup` and `aws-cdk-development`.

Sources: [.claude-plugin/marketplace.json:11-150](), [README.md:16]()

### Tool Permission Model

The `allowed-tools` frontmatter field controls which MCP tools and bash commands can be invoked during skill execution. Wildcard patterns enable flexible permission grants:

| Pattern Type | Example | Grants Access To |
|--------------|---------|------------------|
| MCP Wildcard | `mcp__plugin_aws-cdk_cdk__*` | All tools from CDK MCP server |
| MCP Specific | `mcp__plugin_aws-cost-ops_pricing__get_pricing` | Single pricing tool |
| Bash Wildcard | `Bash(aws *)` | All AWS CLI commands |
| Bash Specific | `Bash(cdk synth)` | Single CDK command |

Tool names follow the pattern: `mcp__plugin_{plugin}_{server}__{tool}`

For example, `mcp__plugin_aws-cdk_cdk__synthesize_stack` breaks down as:
- `plugin_aws-cdk` - The `aws-cdk` plugin
- `cdk` - The `cdk` MCP server
- `synthesize_stack` - The specific tool name

Sources: [README.md:267-271](), [CLAUDE.md:68-70](), [CLAUDE.md:80-87]()

### Lifecycle Hooks

The `hooks` frontmatter field defines lifecycle actions that execute at specific points in the skill execution flow:

```yaml
hooks:
  PreToolUse:
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```

**Hook Configuration:**
- `matcher` - Pattern matching the tool about to be invoked
- `command` - Shell command to execute before the matched tool
- `once: true` - Execute hook only once per session (prevents redundant checks)

This example verifies AWS account identity before any `cdk deploy` command executes, preventing accidental cross-account deployments.

Sources: [CLAUDE.md:72-76]()

## MCP Server Integration

MCP (Model Context Protocol) servers provide real-time AWS service access through a standardized stdio communication protocol. The system uses five MCP servers across three plugins:

### MCP Server Configuration

```mermaid
graph TB
    subgraph "Plugin-to-Server Mapping"
        P1["aws-common"]
        P2["aws-cdk"]
        P3["aws-cost-ops"]
    end
    
    subgraph "MCP Server Instances"
        S1["awsdocs<br/>AWS Documentation"]
        S2["cdk<br/>CDK Operations"]
        S3["pricing<br/>AWS Pricing"]
        S4["costexp<br/>Cost Explorer"]
        S5["cw<br/>CloudWatch"]
    end
    
    subgraph "Launch Configuration"
        LC["type: stdio<br/>command: uvx<br/>args: [awslabs.*-mcp-server@latest]<br/>env: {FASTMCP_LOG_LEVEL: ERROR}"]
    end
    
    subgraph "AWS Service APIs"
        API1["AWS Documentation Service"]
        API2["AWS CloudFormation/CDK"]
        API3["AWS Pricing API"]
        API4["AWS Cost Explorer API"]
        API5["Amazon CloudWatch API"]
    end
    
    P1 --> S1
    P2 --> S2
    P3 --> S3
    P3 --> S4
    P3 --> S5
    
    S1 --> LC
    S2 --> LC
    S3 --> LC
    S4 --> LC
    S5 --> LC
    
    S1 --> API1
    S2 --> API2
    S3 --> API3
    S4 --> API4
    S5 --> API5
```

**MCP Server Configuration** - Each MCP server uses stdio protocol with uvx launcher, executing the latest version of AWS Labs packages. The `FASTMCP_LOG_LEVEL: ERROR` environment variable suppresses verbose logging.

Sources: [.claude-plugin/marketplace.json:49-111]()

### Server Configuration Details

**aws-cdk plugin:**
```json
"mcpServers": {
  "cdk": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cdk-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  }
}
```

**aws-cost-ops plugin:**
```json
"mcpServers": {
  "pricing": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.aws-pricing-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "costexp": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cost-explorer-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "cw": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cloudwatch-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  }
}
```

Sources: [.claude-plugin/marketplace.json:49-111]()

### MCP Tool Naming Convention

MCP server tools use abbreviated server names to comply with Amazon Bedrock's 64-character tool name limit. The naming pattern is:

```
mcp__plugin_{plugin}_{server}__{tool}
```

**Server Name Abbreviations:**

| Full Server Name | Abbreviated Name | Purpose |
|-----------------|------------------|---------|
| awsdocs | `awsdocs` | AWS Documentation search |
| cdk | `cdk` | CDK operations |
| pricing | `pricing` | Cost estimation |
| costexp | `costexp` | Cost Explorer analysis |
| cw | `cw` | CloudWatch metrics |

**Example Tool Names:**
- `mcp__plugin_aws-cdk_cdk__synthesize_stack`
- `mcp__plugin_aws-cost-ops_pricing__get_pricing`
- `mcp__plugin_aws-cost-ops_cw__get_metric_statistics`

This naming scheme enables consistent tool discovery while maintaining compatibility with Bedrock's naming constraints.

Sources: [README.md:267-271](), [CLAUDE.md:80-87]()

## Version Management

The system maintains two version types: marketplace version and plugin versions. Version numbers follow semantic versioning with specific bump rules:

**Version Types:**

| Version Type | Location | Purpose |
|--------------|----------|---------|
| Marketplace Version | `metadata.version` | Overall marketplace version (currently 2.2.0) |
| Plugin Version | `plugins[].version` | Individual plugin versions (1.0.0 or 1.2.0) |

**Version Bump Rules:**

| Change Type | Bump | Examples |
|-------------|------|----------|
| Minor (x.Y.0) | Structural changes | New skill, new `skills:` dependency, new MCP server, new plugin |
| Patch (x.y.Z) | Content changes | Bug fixes, documentation updates, configuration tweaks, typo fixes |

**Current Version State:**
- `marketplace.json` version: 2.2.0
- `aws-common` version: 1.0.0 (stable foundation)
- All domain plugins: 1.2.0 (`aws-cdk`, `aws-cost-ops`, `serverless-eda`, `aws-agentic-ai`)

The version differential (1.0.0 vs 1.2.0) reflects that `aws-common` is a stable dependency layer while domain plugins evolve more rapidly with new features.

Sources: [CLAUDE.md:89-108](), [.claude-plugin/marketplace.json:9-150]()

## Local Development Architecture

For contributors, the system supports local development through symlinks that enable real-time skill testing without plugin reinstallation:

```mermaid
graph LR
    subgraph "Development Workspace"
        Dev["plugins/{plugin}/skills/{skill}/"]
    end
    
    subgraph "Claude Code Discovery"
        Symlink[".claude/skills/{skill}/<br/>Symlink to plugins/"]
    end
    
    subgraph "Testing Commands"
        CLI["claude -p 'prompt'"]
        IDE["/skills, /plugin, /context"]
    end
    
    Dev -.symlink.-> Symlink
    Symlink --> CLI
    Symlink --> IDE
```

**Local Development Architecture** - Symlinks from `.claude/skills/` to `plugins/*/skills/*` enable Claude Code to discover skill changes instantly during development.

**Symlink Creation:**
```bash
cd .claude && rm -rf skills && mkdir skills
ln -s ../../plugins/aws-common/skills/aws-mcp-setup skills/
ln -s ../../plugins/aws-cdk/skills/aws-cdk-development skills/
ln -s ../../plugins/serverless-eda/skills/aws-serverless-eda skills/
ln -s ../../plugins/aws-agentic-ai/skills/aws-agentic-ai skills/
ln -s ../../plugins/aws-cost-ops/skills/aws-cost-operations skills/
```

Sources: [CLAUDE.md:26-54]()

## Summary

The AWS Skills architecture is a layered system with clear separation of concerns:

1. **Marketplace Layer** - `marketplace.json` defines plugins, versions, and MCP servers
2. **Plugin Layer** - Standardized directory structure with required SKILL.md and optional references
3. **Execution Layer** - Fork-based isolation with frontmatter configuration, dependency auto-loading, and lifecycle hooks
4. **Integration Layer** - MCP servers via stdio protocol with abbreviated naming for Bedrock compatibility

The architecture prioritizes modularity (plugins as independent units), declarative configuration (frontmatter-driven execution), and real-time AWS knowledge (MCP server integration). For detailed information on specific components, see [Marketplace and Plugin System](#3.1), [Skills and Execution Model](#3.2), and [MCP Server Integration](#3.3).

---

# Page: Marketplace and Plugin System

# Marketplace and Plugin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)

</details>



This document covers the central marketplace registry (`marketplace.json`), plugin registration structure, version management strategy, and the standardized plugin directory layout. For information about how skills are executed and dependencies are loaded, see [Skills and Execution Model](#3.2). For details on MCP server configuration and the stdio protocol, see [MCP Server Integration](#3.3).

## Marketplace Registry

The marketplace is defined by a single JSON file at `.claude-plugin/marketplace.json` that serves as the central registry for all plugins in the AWS Skills ecosystem.

### Registry Structure

```mermaid
graph TB
    Registry["marketplace.json"]
    
    subgraph "Top-Level Metadata"
        Name["name: 'aws-skills'"]
        Owner["owner.name<br/>owner.email"]
        Meta["metadata.description<br/>metadata.version: '2.2.0'"]
    end
    
    subgraph "Plugins Array"
        Plugin1["plugins[0]<br/>aws-common<br/>v1.0.0"]
        Plugin2["plugins[1]<br/>aws-cdk<br/>v1.2.0"]
        Plugin3["plugins[2]<br/>aws-cost-ops<br/>v1.2.0"]
        Plugin4["plugins[3]<br/>serverless-eda<br/>v1.2.0"]
        Plugin5["plugins[4]<br/>aws-agentic-ai<br/>v1.2.0"]
    end
    
    Registry --> Name
    Registry --> Owner
    Registry --> Meta
    Registry --> Plugin1
    Registry --> Plugin2
    Registry --> Plugin3
    Registry --> Plugin4
    Registry --> Plugin5
    
    Plugin1 --> Source1["source: './plugins/aws-common'"]
    Plugin1 --> Skills1["skills[0]: './skills/aws-mcp-setup'"]
    
    Plugin2 --> Source2["source: './plugins/aws-cdk'"]
    Plugin2 --> Skills2["skills[0]: './skills/aws-cdk-development'"]
    Plugin2 --> MCP2["mcpServers.cdk"]
    
    Plugin3 --> Source3["source: './plugins/aws-cost-ops'"]
    Plugin3 --> Skills3["skills[0]: './skills/aws-cost-operations'"]
    Plugin3 --> MCP3["mcpServers.pricing<br/>mcpServers.costexp<br/>mcpServers.cw"]
```

**Marketplace Registry Structure**

The registry contains marketplace-level metadata and an ordered array of plugin definitions. Each plugin specifies its source directory and exposed skills.

Sources: [.claude-plugin/marketplace.json:1-11]()

### Marketplace Metadata

The top-level `metadata` object defines the overall marketplace identity:

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"aws-skills"` | Marketplace identifier used in commands like `/plugin marketplace add zxkane/aws-skills` |
| `owner.name` | `"Kane Zhu"` | Marketplace maintainer |
| `owner.email` | `"me@kane.mx"` | Contact information |
| `metadata.description` | Long description | Marketplace description shown in plugin browser |
| `metadata.version` | `"2.2.0"` | Marketplace version, bumped when new plugins are added |

Sources: [.claude-plugin/marketplace.json:2-10]()

## Plugin Registration

Each plugin in the `plugins` array follows a standardized registration structure with required and optional fields.

### Required Fields

Every plugin must define these fields:

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `name` | string | `"aws-cdk"` | Unique plugin identifier |
| `description` | string | `"Comprehensive AWS development skills..."` | Plugin description for UI display |
| `version` | string | `"1.2.0"` | Semantic version (major.minor.patch) |
| `author.name` | string | `"Kane Zhu"` | Plugin author |
| `author.email` | string | `"me@kane.mx"` | Author contact |
| `homepage` | string | `"https://github.com/zxkane/aws-skills"` | Plugin homepage URL |
| `repository` | string | `"https://github.com/zxkane/aws-skills"` | Source code repository |
| `license` | string | `"MIT"` | License identifier |
| `keywords` | string[] | `["aws", "cdk", "lambda"]` | Searchable keywords |
| `category` | string | `"development"` or `"operations"` | Plugin category |
| `source` | string | `"./plugins/aws-cdk"` | Relative path to plugin directory |
| `strict` | boolean | `false` | Strict mode flag (currently unused) |
| `skills` | string[] | `["./skills/aws-cdk-development"]` | Paths to skill directories relative to `source` |

Sources: [.claude-plugin/marketplace.json:32-48](), [.claude-plugin/marketplace.json:63-79]()

### MCP Server Configuration

Plugins optionally define MCP servers in the `mcpServers` object. Each server is keyed by a short name (to satisfy Bedrock's 64-character tool name limit):

```mermaid
graph LR
    subgraph "aws-cdk Plugin"
        CDK_MCP["mcpServers.cdk"]
    end
    
    subgraph "MCP Server Definition"
        Type["type: 'stdio'"]
        Command["command: 'uvx'"]
        Args["args: ['awslabs.cdk-mcp-server@latest']"]
        Env["env.FASTMCP_LOG_LEVEL: 'ERROR'"]
    end
    
    subgraph "aws-cost-ops Plugin"
        CO_MCP1["mcpServers.pricing"]
        CO_MCP2["mcpServers.costexp"]
        CO_MCP3["mcpServers.cw"]
    end
    
    CDK_MCP --> Type
    CDK_MCP --> Command
    CDK_MCP --> Args
    CDK_MCP --> Env
    
    CO_MCP1 --> Pricing["awslabs.aws-pricing-mcp-server@latest"]
    CO_MCP2 --> CostExp["awslabs.cost-explorer-mcp-server@latest"]
    CO_MCP3 --> CloudWatch["awslabs.cloudwatch-mcp-server@latest"]
```

**MCP Server Configuration Structure**

Each MCP server is defined with `type: "stdio"`, launched via `uvx` with a specific `awslabs.*-mcp-server@latest` package, and configured with `FASTMCP_LOG_LEVEL: "ERROR"`.

The server key (e.g., `cdk`, `pricing`) becomes part of the tool naming pattern: `mcp__plugin_{plugin}_{server}__{tool}`. For example, the CDK server's tools are named `mcp__plugin_aws-cdk_cdk__*`.

Sources: [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111](), [CLAUDE.md:79-87]()

### Plugin Categories

Plugins are categorized as:

| Category | Plugins | Purpose |
|----------|---------|---------|
| `"development"` | `aws-common`, `aws-cdk`, `serverless-eda`, `aws-agentic-ai` | Infrastructure and application development |
| `"operations"` | `aws-cost-ops` | Post-deployment operations and monitoring |

Sources: [.claude-plugin/marketplace.json:24](), [.claude-plugin/marketplace.json:43](), [.claude-plugin/marketplace.json:74]()

## Version Management

The system uses semantic versioning with distinct version numbers for the marketplace and individual plugins.

### Version Hierarchy

```mermaid
graph TB
    Market["marketplace.json<br/>metadata.version: 2.2.0"]
    
    Common["aws-common<br/>version: 1.0.0"]
    CDK["aws-cdk<br/>version: 1.2.0"]
    Cost["aws-cost-ops<br/>version: 1.2.0"]
    Serverless["serverless-eda<br/>version: 1.2.0"]
    Agentic["aws-agentic-ai<br/>version: 1.2.0"]
    
    Market --> Common
    Market --> CDK
    Market --> Cost
    Market --> Serverless
    Market --> Agentic
    
    Common -.->|"Stable foundation<br/>v1.0.0"| Foundation["Rarely changes"]
    CDK -.->|"Active development<br/>v1.2.0"| Active["Frequent updates"]
    Cost -.->|"Active development<br/>v1.2.0"| Active
    Serverless -.->|"Active development<br/>v1.2.0"| Active
    Agentic -.->|"Active development<br/>v1.2.0"| Active
```

**Version Hierarchy**

The marketplace version (2.2.0) is independent of plugin versions. The foundational `aws-common` plugin remains at v1.0.0 while domain plugins evolve at v1.2.0.

Sources: [.claude-plugin/marketplace.json:9](), [.claude-plugin/marketplace.json:15](), [.claude-plugin/marketplace.json:34]()

### Version Bump Rules

The system follows these rules for version increments:

| Change Type | Version Bump | When to Apply |
|-------------|--------------|---------------|
| **Minor** (x.Y.0) | Increment minor version | New skill added, new `skills:` dependency in frontmatter, new MCP server added, new plugin added |
| **Patch** (x.y.Z) | Increment patch version | Bug fixes, documentation updates, configuration tweaks, typo fixes, content updates without structural changes |

**Marketplace Version Bumps:**
- Add new plugin to `plugins` array → Minor bump `metadata.version`
- Modify existing plugin metadata only → Patch bump `metadata.version`

**Plugin Version Bumps:**
- Add new skill to `skills` array → Minor bump plugin `version`
- Add `skills:` dependency in SKILL.md frontmatter → Minor bump plugin `version`
- Add MCP server to `mcpServers` → Minor bump plugin `version`
- Update skill content without frontmatter changes → Patch bump plugin `version`
- Fix documentation or configuration → Patch bump plugin `version`

**Mandatory Bump Policy:** All content modifications must include a version bump before committing.

Sources: [CLAUDE.md:89-108]()

### Version Comparison Table

| Plugin | Current Version | Last Minor Bump | Reason for Version Gap |
|--------|----------------|-----------------|------------------------|
| `aws-common` | 1.0.0 | Initial release | Stable foundation, minimal changes needed |
| `aws-cdk` | 1.2.0 | Added features | Active development of CDK patterns |
| `aws-cost-ops` | 1.2.0 | Added MCP servers | Evolved from basic to three-server integration |
| `serverless-eda` | 1.2.0 | Added patterns | Expanded event-driven architecture coverage |
| `aws-agentic-ai` | 1.2.0 | Added services | Growth of AgentCore service coverage |

Sources: [.claude-plugin/marketplace.json:15](), [.claude-plugin/marketplace.json:34](), [.claude-plugin/marketplace.json:65](), [.claude-plugin/marketplace.json:116](), [.claude-plugin/marketplace.json:135]()

## Plugin Directory Structure

All plugins follow a standardized directory layout to ensure consistency and predictability.

### Standard Layout

```mermaid
graph TB
    Root["plugins/{plugin-name}/"]
    
    subgraph "Required Directories"
        Skills["skills/"]
        SkillDir["{skill-name}/"]
        SkillMD["SKILL.md<br/>(frontmatter + content)"]
        
        Skills --> SkillDir
        SkillDir --> SkillMD
    end
    
    subgraph "Optional Directories"
        Refs["references/"]
        Scripts["scripts/"]
        Services["services/"]
        CrossSvc["cross-service/"]
        
        RefMD1["pattern-docs.md"]
        RefMD2["api-reference.md"]
        
        ScriptSH["utility-scripts.sh"]
        SvcCode["service-code.py"]
        
        Refs --> RefMD1
        Refs --> RefMD2
        Scripts --> ScriptSH
        Services --> SvcCode
    end
    
    Root --> Skills
    Root -.optional.-> Refs
    Root -.optional.-> Scripts
    Root -.optional.-> Services
    Root -.optional.-> CrossSvc
    
    SkillDir -.may contain.-> Refs
```

**Plugin Directory Structure**

Every plugin must have a `skills/` directory containing skill subdirectories with SKILL.md files. Optional directories include `references/`, `scripts/`, `services/`, and `cross-service/`.

Sources: [CLAUDE.md:20-24]()

### Directory Purposes

| Directory | Required | Purpose | Example Content |
|-----------|----------|---------|-----------------|
| `skills/` | Yes | Contains skill subdirectories with SKILL.md definitions | `aws-cdk-development/`, `aws-mcp-setup/` |
| `skills/{skill}/SKILL.md` | Yes | Skill definition with frontmatter and markdown content | Frontmatter configuration + guidance text |
| `skills/{skill}/references/` | No | Detailed reference documentation for the skill | `cdk-patterns.md`, `lambda-best-practices.md` |
| `references/` | No | Plugin-wide reference documentation | Cross-cutting patterns and guides |
| `scripts/` | No | Utility scripts for automation or validation | `validate-stack.sh`, `setup.sh` |
| `services/` | No | Service-specific implementation code | AWS service integration code |
| `cross-service/` | No | Multi-service orchestration code | Cross-service patterns and workflows |

Sources: [CLAUDE.md:20-24]()

### Real Plugin Examples

**aws-common Plugin Structure:**
```
plugins/aws-common/
└── skills/
    └── aws-mcp-setup/
        └── SKILL.md
```

**aws-cdk Plugin Structure:**
```
plugins/aws-cdk/
└── skills/
    └── aws-cdk-development/
        ├── SKILL.md
        └── references/
            ├── cdk-patterns.md
            ├── lambda-nodejs.md
            └── lambda-python.md
```

**aws-cost-ops Plugin Structure:**
```
plugins/aws-cost-ops/
└── skills/
    └── aws-cost-operations/
        ├── SKILL.md
        └── references/
            └── operations-patterns.md
```

Sources: [.claude-plugin/marketplace.json:25-29](), [.claude-plugin/marketplace.json:44-48](), [.claude-plugin/marketplace.json:75-79]()

## Plugin Discovery and Loading

Claude Code discovers plugins through the marketplace registry and loads them based on the `source` and `skills` paths.

### Discovery Mechanism

```mermaid
graph TB
    User["User executes:<br/>/plugin marketplace add zxkane/aws-skills"]
    
    Fetch["Claude Code fetches:<br/>github.com/zxkane/aws-skills/.claude-plugin/marketplace.json"]
    
    Parse["Parse marketplace.json<br/>Extract plugins[] array"]
    
    Display["Display plugins in browser:<br/>- aws-common v1.0.0<br/>- aws-cdk v1.2.0<br/>- aws-cost-ops v1.2.0<br/>- serverless-eda v1.2.0<br/>- aws-agentic-ai v1.2.0"]
    
    Install["User executes:<br/>/plugin install aws-cdk@aws-skills"]
    
    Clone["Clone repository<br/>to plugin cache"]
    
    LoadPlugin["Read plugin source:<br/>./plugins/aws-cdk/"]
    
    LoadSkills["Load skills[] paths:<br/>./skills/aws-cdk-development/"]
    
    LoadMCP["Configure mcpServers:<br/>cdk server via uvx"]
    
    Ready["Plugin ready:<br/>/skill aws-cdk-development"]
    
    User --> Fetch
    Fetch --> Parse
    Parse --> Display
    Display --> Install
    Install --> Clone
    Clone --> LoadPlugin
    LoadPlugin --> LoadSkills
    LoadPlugin --> LoadMCP
    LoadSkills --> Ready
    LoadMCP --> Ready
```

**Plugin Discovery and Loading Flow**

Claude Code fetches the marketplace registry from GitHub, parses the `plugins` array, and loads plugin content from the specified `source` paths. Skills are loaded from the paths in the `skills` array, and MCP servers are configured from the `mcpServers` object.

Sources: [.claude-plugin/marketplace.json:1-152](), [CLAUDE.md:7-8]()

### Local Development Discovery

For local development, plugins are discovered via symlinks in `.claude/skills/`:

```mermaid
graph LR
    DevDir["Development Directory:<br/>plugins/aws-cdk/skills/aws-cdk-development/"]
    
    Symlink[".claude/skills/aws-cdk-development<br/>(symlink)"]
    
    Claude["Claude Code<br/>discovers skills"]
    
    DevDir -.symlink.-> Symlink
    Symlink --> Claude
    
    Create["Create symlink:<br/>ln -s ../../plugins/aws-cdk/skills/aws-cdk-development<br/>.claude/skills/aws-cdk-development"]
    
    Verify["Verify with:<br/>/skills<br/>/context"]
```

**Local Development Discovery**

During development, symlinks in `.claude/skills/` point to plugin directories in `plugins/`, enabling immediate skill updates without reinstallation. Changes to SKILL.md files are detected immediately by Claude Code.

Sources: [CLAUDE.md:26-54]()

### Path Resolution

The system resolves paths using these rules:

1. **Plugin Source Path:** Resolved from marketplace root
   - `marketplace.json` at `.claude-plugin/marketplace.json`
   - Plugin source at `.claude-plugin/` + `plugins[].source`
   - Example: `.claude-plugin/` + `"./plugins/aws-cdk"` = `.claude-plugin/plugins/aws-cdk/`

2. **Skill Path:** Resolved from plugin source
   - Plugin source: `.claude-plugin/plugins/aws-cdk/`
   - Skill path: `"./skills/aws-cdk-development"`
   - Full path: `.claude-plugin/plugins/aws-cdk/skills/aws-cdk-development/SKILL.md`

3. **Reference Path:** Resolved from skill directory
   - Skill directory: `.claude-plugin/plugins/aws-cdk/skills/aws-cdk-development/`
   - Reference: `references/cdk-patterns.md`
   - Full path: `.claude-plugin/plugins/aws-cdk/skills/aws-cdk-development/references/cdk-patterns.md`

Sources: [.claude-plugin/marketplace.json:44](), [.claude-plugin/marketplace.json:46-48]()

### Skill Registration

When a plugin is installed, Claude Code registers skills by:

1. Reading the `skills` array from the plugin definition
2. Loading each `SKILL.md` file from the resolved path
3. Parsing the YAML frontmatter for skill metadata
4. Making the skill available via `/skill {skill-name}` command
5. Auto-loading dependencies specified in the `skills:` frontmatter field

The skill name used in commands is derived from the frontmatter `name:` field, not the directory name.

Sources: [CLAUDE.md:20-24](), [CLAUDE.md:56-77]()

---

# Page: Skills and Execution Model

# Skills and Execution Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)
- [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md](plugins/aws-cdk/skills/aws-cdk-development/SKILL.md)

</details>



This page documents how skills are defined, configured, and executed within the AWS Skills system. It covers the SKILL.md frontmatter format, fork execution context, dependency resolution, tool permission system, and lifecycle hooks that control skill behavior.

For information about plugin-level configuration and marketplace registration, see [Marketplace and Plugin System](#3.1). For MCP server integration details, see [MCP Server Integration](#3.3).

## Skill Definition Structure

Skills are defined in `SKILL.md` files within each plugin's `skills/<skill-name>/` directory. Each skill uses YAML frontmatter to declare metadata, dependencies, permissions, and execution context.

### SKILL.md Frontmatter Format

The frontmatter follows this structure:

```yaml
---
name: skill-name
description: detailed description with usage triggers
context: fork
model: sonnet
skills:
  - dependency-skill-1
  - dependency-skill-2
allowed-tools:
  - mcp__server__*
  - Bash(command pattern)
hooks:
  PreToolUse:
    - matcher: Bash(pattern)
      command: command to execute
      once: true
---
```

**Field Definitions:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `name` | string | Unique skill identifier | `aws-cdk-development` |
| `description` | string | Usage guidance, trigger keywords | "Use when user mentions CDK, cdk synth, IaC..." |
| `context` | string | Execution isolation level | `fork` |
| `model` | string | Model selection for execution | `sonnet` |
| `skills` | array | Auto-loaded skill dependencies | `[aws-mcp-setup]` |
| `allowed-tools` | array | Permitted tool invocations | `[mcp__cdk__*, Bash(aws *)]` |
| `hooks` | object | Lifecycle event handlers | `PreToolUse: [...]` |

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21](), [CLAUDE.md:56-77]()

### Skill Discovery and Registration

The marketplace defines which skills are included in each plugin:

```mermaid
graph TB
    Marketplace["marketplace.json<br/>.claude-plugin/marketplace.json"]
    
    PluginEntry["Plugin Entry<br/>plugins[].skills"]
    SkillPath["Skill Path<br/>./skills/skill-name"]
    SkillFile["SKILL.md<br/>plugins/&lt;plugin&gt;/skills/&lt;skill-name&gt;/SKILL.md"]
    
    Frontmatter["Frontmatter Block<br/>---<br/>name: skill-name<br/>context: fork<br/>skills: [deps]<br/>---"]
    Content["Markdown Content<br/>Skill instructions and guidance"]
    
    Marketplace --> PluginEntry
    PluginEntry --> SkillPath
    SkillPath --> SkillFile
    SkillFile --> Frontmatter
    SkillFile --> Content
    
    style Marketplace fill:#f9f9f9
    style Frontmatter fill:#f0f0f0
```

**Skill Discovery Flow:**
1. Claude Code reads `.claude-plugin/marketplace.json`
2. For each plugin entry, reads `plugins[].skills` array
3. Resolves skill paths relative to plugin `source` directory
4. Loads each `SKILL.md` file and parses frontmatter

Sources: [.claude-plugin/marketplace.json:11-151](), [CLAUDE.md:21-24]()

## Execution Context

### Fork Context Model

Skills execute in a **fork context**, creating an isolated sub-agent for each skill invocation:

```mermaid
graph TB
    User["User Interaction<br/>CLI or IDE command"]
    MainAgent["Main Claude Agent<br/>Base context"]
    
    ForkDecision{"Skill has<br/>context: fork?"}
    
    SubAgent["Fork Context<br/>Isolated sub-agent"]
    DirectExec["Direct Execution<br/>Same agent context"]
    
    SkillFrontmatter["Skill Frontmatter<br/>- model: sonnet<br/>- skills: [deps]<br/>- allowed-tools: [...]"]
    
    ModelSelect["Model Selection<br/>Use specified model"]
    DepsLoad["Dependency Loading<br/>Auto-load sub-skills"]
    ToolFilter["Tool Filtering<br/>Restrict to allowed-tools"]
    
    Execution["Skill Execution<br/>With isolated context"]
    
    User --> MainAgent
    MainAgent --> ForkDecision
    ForkDecision -->|Yes| SubAgent
    ForkDecision -->|No| DirectExec
    
    SubAgent --> SkillFrontmatter
    SkillFrontmatter --> ModelSelect
    SkillFrontmatter --> DepsLoad
    SkillFrontmatter --> ToolFilter
    
    ModelSelect --> Execution
    DepsLoad --> Execution
    ToolFilter --> Execution
    DirectExec --> Execution
    
    style SubAgent fill:#f0f0f0
    style SkillFrontmatter fill:#f9f9f9
```

**Fork Context Benefits:**
- **Isolation**: Each skill runs with its own context boundary
- **Model Selection**: Skills can specify optimal models for their domain
- **Permission Scoping**: Tool access is restricted per skill
- **Dependency Encapsulation**: Sub-skills load with their own contexts

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:4](), [CLAUDE.md:64]()

### Model Selection

The `model` field specifies which Claude model executes the skill:

| Model Value | Description | Use Case |
|-------------|-------------|----------|
| `sonnet` | Claude Sonnet | Default for most skills, balanced performance |
| (unspecified) | System default | Uses Claude Code's configured model |

All current skills use `context: fork` without explicit `model` specification, defaulting to system configuration.

Sources: [CLAUDE.md:65]()

## Dependency Resolution

### Auto-Loading Mechanism

The `skills:` frontmatter field declares skill dependencies that are automatically loaded before the parent skill executes:

```mermaid
graph TB
    UserInvokes["User Invokes Skill<br/>aws-serverless-eda"]
    
    LoadSkill["Load Skill<br/>aws-serverless-eda"]
    ParseFrontmatter["Parse Frontmatter<br/>skills: [aws-mcp-setup,<br/>aws-cdk-development]"]
    
    CheckDep1{"aws-mcp-setup<br/>loaded?"}
    CheckDep2{"aws-cdk-development<br/>loaded?"}
    
    LoadDep1["Load aws-mcp-setup<br/>from aws-common plugin"]
    LoadDep2["Load aws-cdk-development<br/>from aws-cdk plugin"]
    
    CheckTransitive{"aws-cdk-development<br/>has skills: [aws-mcp-setup]"}
    
    SkipDep1["Skip<br/>Already loaded"]
    SkipDep2["Skip<br/>Already loaded"]
    
    ExecuteParent["Execute<br/>aws-serverless-eda"]
    
    UserInvokes --> LoadSkill
    LoadSkill --> ParseFrontmatter
    ParseFrontmatter --> CheckDep1
    ParseFrontmatter --> CheckDep2
    
    CheckDep1 -->|No| LoadDep1
    CheckDep1 -->|Yes| SkipDep1
    CheckDep2 -->|No| LoadDep2
    CheckDep2 -->|Yes| SkipDep2
    
    LoadDep2 --> CheckTransitive
    CheckTransitive --> SkipDep1
    
    LoadDep1 --> ExecuteParent
    SkipDep1 --> ExecuteParent
    SkipDep2 --> ExecuteParent
    
    style ParseFrontmatter fill:#f9f9f9
    style CheckTransitive fill:#f0f0f0
```

**Dependency Resolution Rules:**
1. Dependencies are loaded in declaration order
2. Already-loaded skills are skipped (no duplicate loading)
3. Transitive dependencies are resolved automatically
4. All skills ultimately depend on `aws-mcp-setup` from `aws-common` plugin

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:5-6](), [CLAUDE.md:66-67]()

### Dependency Graph

The complete dependency graph across all plugins:

| Skill | Plugin | Dependencies |
|-------|--------|--------------|
| `aws-mcp-setup` | aws-common | *(none - root dependency)* |
| `aws-cdk-development` | aws-cdk | `[aws-mcp-setup]` |
| `aws-cost-operations` | aws-cost-ops | `[aws-mcp-setup]` |
| `aws-serverless-eda` | serverless-eda | `[aws-mcp-setup, aws-cdk-development]` |
| `aws-agentic-ai` | aws-agentic-ai | `[aws-mcp-setup]` |

**Key Insight:** Every skill in the system depends on `aws-mcp-setup`, either directly or transitively through `aws-cdk-development`. This ensures all AWS-related skills have access to AWS documentation lookup capabilities.

Sources: [.claude-plugin/marketplace.json:27-149](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:5-6]()

## Tool Permissions

### Allowed-Tools Declaration

The `allowed-tools:` field restricts which tools and commands a skill can invoke. This implements a permission boundary for fork contexts.

```yaml
allowed-tools:
  - mcp__cdk__*                    # All tools from CDK MCP server
  - mcp__aws-mcp__*                # All tools from AWS MCP server
  - mcp__awsdocs__*                # All tools from AWS Docs server
  - Bash(cdk *)                    # CDK CLI commands
  - Bash(npm *)                    # npm commands
  - Bash(npx *)                    # npx commands
  - Bash(aws cloudformation *)     # CloudFormation CLI
  - Bash(aws sts get-caller-identity) # Account identity check
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:7-15]()

### Tool Permission Patterns

```mermaid
graph LR
    SkillFrontmatter["allowed-tools:<br/>- mcp__cdk__*<br/>- Bash(cdk *)"]
    
    MCPPattern["MCP Server Pattern<br/>mcp__plugin_{plugin}_{server}__{tool}"]
    BashPattern["Bash Command Pattern<br/>Bash(command pattern)"]
    
    MCPWildcard["Wildcard Matching<br/>mcp__cdk__* matches<br/>mcp__plugin_aws-cdk_cdk__*"]
    BashWildcard["Wildcard Matching<br/>Bash(cdk *) matches<br/>Bash(cdk synth)<br/>Bash(cdk deploy)"]
    
    PermissionCheck{"Tool invocation<br/>matches pattern?"}
    
    Allow["Tool Execution<br/>Allowed"]
    Deny["Tool Execution<br/>Blocked"]
    
    SkillFrontmatter --> MCPPattern
    SkillFrontmatter --> BashPattern
    
    MCPPattern --> MCPWildcard
    BashPattern --> BashWildcard
    
    MCPWildcard --> PermissionCheck
    BashWildcard --> PermissionCheck
    
    PermissionCheck -->|Match| Allow
    PermissionCheck -->|No Match| Deny
    
    style PermissionCheck fill:#f9f9f9
    style Allow fill:#f0f0f0
```

**Permission Model:**
- **MCP Tools**: Pattern `mcp__<server>__*` matches all tools from specified server
- **Bash Commands**: Pattern `Bash(command pattern)` uses wildcard matching
- **Wildcard Support**: `*` matches any characters in tool/command names
- **Explicit Permissions**: Each command must be explicitly allowed or wildcarded

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:7-15](), [CLAUDE.md:68-70]()

### Tool Permission Scope by Skill

| Skill | MCP Servers | Bash Commands |
|-------|-------------|---------------|
| `aws-cdk-development` | `cdk`, `aws-mcp`, `awsdocs` | `cdk *`, `npm *`, `npx *`, `aws cloudformation *`, `aws sts get-caller-identity` |
| `aws-mcp-setup` | `aws-mcp`, `awsdocs` | (MCP configuration commands) |
| `aws-cost-operations` | `pricing`, `costexp`, `cw`, `aws-mcp`, `awsdocs` | (Cost analysis commands) |
| `aws-serverless-eda` | (inherits from `aws-cdk-development`) | (inherits from dependencies) |
| `aws-agentic-ai` | `aws-mcp`, `awsdocs` | (AgentCore deployment commands) |

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:7-15]()

## Hooks and Lifecycle Events

### PreToolUse Hooks

The `hooks.PreToolUse` field defines commands that execute before specific tool invocations:

```yaml
hooks:
  PreToolUse:
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```

**Hook Configuration:**

| Field | Type | Purpose |
|-------|------|---------|
| `matcher` | string | Tool pattern to trigger hook | 
| `command` | string | Command to execute before matched tool |
| `once` | boolean | Execute only once per session (prevents duplicates) |

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21](), [CLAUDE.md:71-76]()

### Hook Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Skill as "Skill Execution Context"
    participant Hook as "PreToolUse Hook"
    participant Tool as "Target Tool"
    
    User->>Skill: "Invokes skill"
    Skill->>Skill: "Parse frontmatter"
    Skill->>Skill: "Load dependencies"
    Skill->>Skill: "Execute skill logic"
    
    Skill->>Tool: "Attempt tool invocation<br/>Bash(cdk deploy)"
    Tool->>Hook: "Check for PreToolUse hooks"
    Hook->>Hook: "Match pattern: Bash(cdk deploy*)"
    
    alt Hook once: true AND already executed
        Hook->>Tool: "Skip hook (already ran)"
    else Hook not executed OR once: false
        Hook->>Hook: "Execute hook command<br/>aws sts get-caller-identity"
        Hook->>User: "Display account info"
        Hook->>Tool: "Proceed with tool"
    end
    
    Tool->>Tool: "Execute tool<br/>cdk deploy"
    Tool->>User: "Tool output"
```

**Hook Use Cases:**

1. **Account Verification**: Verify AWS account before deployments
   - Hook: `aws sts get-caller-identity` before `cdk deploy*`
   - Prevents accidental cross-account deployments

2. **Prerequisite Checks**: Validate environment setup
   - Check credentials, CLI installations, configuration

3. **Audit Trails**: Log tool invocations for compliance
   - Record what operations are about to execute

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21]()

## Complete Execution Flow

### User to AWS Execution Path

```mermaid
graph TB
    User["User Input<br/>CLI: claude -p 'prompt'<br/>IDE: /skills command"]
    
    LoadPlugin["Load Plugin<br/>From marketplace.json"]
    LoadSkill["Load Skill<br/>Read SKILL.md"]
    
    ParseFront["Parse Frontmatter<br/>Extract configuration"]
    
    CreateFork["Create Fork Context<br/>context: fork"]
    SelectModel["Select Model<br/>model: sonnet (if specified)"]
    
    LoadDeps["Load Dependencies<br/>skills: [aws-mcp-setup, ...]"]
    SetPerms["Set Permissions<br/>allowed-tools: [...]"]
    RegisterHooks["Register Hooks<br/>hooks: {PreToolUse: [...]}"]
    
    ExecuteSkill["Execute Skill<br/>Process markdown content"]
    
    ToolInvoke{"Tool<br/>Invocation?"}
    CheckPerms{"Permission<br/>check"}
    CheckHook{"PreToolUse<br/>hook?"}
    
    RunHook["Execute Hook<br/>once: true logic"]
    ExecuteTool["Execute Tool<br/>MCP or Bash"]
    
    MCPServer["MCP Server<br/>uvx launcher"]
    BashCommand["Bash Command<br/>aws CLI, cdk CLI"]
    
    AWSServices["AWS Services<br/>API calls"]
    
    Result["Return Result<br/>To user"]
    
    User --> LoadPlugin
    LoadPlugin --> LoadSkill
    LoadSkill --> ParseFront
    
    ParseFront --> CreateFork
    ParseFront --> SelectModel
    ParseFront --> LoadDeps
    ParseFront --> SetPerms
    ParseFront --> RegisterHooks
    
    CreateFork --> ExecuteSkill
    SelectModel --> ExecuteSkill
    LoadDeps --> ExecuteSkill
    SetPerms --> ExecuteSkill
    RegisterHooks --> ExecuteSkill
    
    ExecuteSkill --> ToolInvoke
    
    ToolInvoke -->|Yes| CheckPerms
    ToolInvoke -->|No| Result
    
    CheckPerms -->|Allowed| CheckHook
    CheckPerms -->|Denied| Result
    
    CheckHook -->|Hook exists| RunHook
    CheckHook -->|No hook| ExecuteTool
    RunHook --> ExecuteTool
    
    ExecuteTool --> MCPServer
    ExecuteTool --> BashCommand
    
    MCPServer --> AWSServices
    BashCommand --> AWSServices
    
    AWSServices --> Result
    Result --> User
    
    style ParseFront fill:#f9f9f9
    style CreateFork fill:#f0f0f0
    style CheckPerms fill:#f9f9f9
```

**Execution Stages:**

1. **Initialization**: Load plugin and skill from marketplace
2. **Parsing**: Extract frontmatter configuration
3. **Context Setup**: Create fork, select model, load dependencies
4. **Permission Setup**: Configure allowed-tools and register hooks
5. **Execution**: Process skill content and handle tool invocations
6. **Tool Invocation**: Check permissions, run hooks, execute tools
7. **AWS Integration**: Route through MCP servers or Bash commands
8. **Result Handling**: Return output to user

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21](), [CLAUDE.md:56-77](), [.claude-plugin/marketplace.json:1-152]()

### Skill Lifecycle Events

```mermaid
stateDiagram-v2
    [*] --> SkillLoaded: "Load SKILL.md"
    
    SkillLoaded --> FrontmatterParsed: "Parse YAML frontmatter"
    FrontmatterParsed --> ContextCreated: "Create fork context"
    
    ContextCreated --> DependenciesLoaded: "Auto-load skills: [deps]"
    DependenciesLoaded --> PermissionsSet: "Configure allowed-tools"
    PermissionsSet --> HooksRegistered: "Register lifecycle hooks"
    
    HooksRegistered --> Executing: "Process skill content"
    
    Executing --> ToolInvoked: "Tool requested"
    ToolInvoked --> PreToolUse: "Trigger PreToolUse hook"
    PreToolUse --> ToolExecuted: "Execute tool"
    ToolExecuted --> Executing: "Continue execution"
    
    Executing --> [*]: "Complete"
```

**State Transitions:**

1. **SkillLoaded → FrontmatterParsed**: YAML block extracted and validated
2. **FrontmatterParsed → ContextCreated**: Fork context instantiated with isolated scope
3. **ContextCreated → DependenciesLoaded**: Recursive dependency loading
4. **DependenciesLoaded → PermissionsSet**: Tool permission boundary established
5. **PermissionsSet → HooksRegistered**: Lifecycle hooks attached to tool matchers
6. **Executing → ToolInvoked**: Skill logic requests tool execution
7. **ToolInvoked → PreToolUse**: Hook matcher fires (if configured)
8. **PreToolUse → ToolExecuted**: Tool proceeds after hook completion

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21](), [CLAUDE.md:56-77]()

## Frontmatter Best Practices

### Dependency Management

**Minimal Dependencies**: Only declare direct dependencies. Transitive dependencies load automatically.

```yaml
# ✅ GOOD - Minimal, explicit dependencies
skills:
  - aws-mcp-setup

# ❌ BAD - Redundant transitive dependency
skills:
  - aws-cdk-development  # This already loads aws-mcp-setup
  - aws-mcp-setup        # Redundant
```

### Tool Permission Patterns

**Use Wildcards Strategically**: Balance between security and usability.

```yaml
# ✅ GOOD - Scope to specific MCP servers
allowed-tools:
  - mcp__cdk__*            # All CDK server tools
  - mcp__aws-mcp__*        # All AWS MCP tools
  - Bash(cdk *)            # CDK CLI only
  - Bash(aws sts get-caller-identity)  # Specific command

# ❌ BAD - Overly permissive
allowed-tools:
  - mcp__*__*              # All MCP servers (too broad)
  - Bash(*)                # All bash commands (insecure)
```

### Hook Configuration

**Use once: true for Idempotent Operations**: Prevent duplicate executions of expensive or side-effecting commands.

```yaml
hooks:
  PreToolUse:
    # ✅ GOOD - Account check runs once per session
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
    
    # ❌ BAD - Would run on every deployment
    # - matcher: Bash(cdk deploy*)
    #   command: aws sts get-caller-identity
    #   once: false  # Wastes API calls
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:5-21](), [CLAUDE.md:66-76]()

## Reference Implementation

The `aws-cdk-development` skill demonstrates all frontmatter features:

**File:** [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21]()

- **Context Isolation**: `context: fork`
- **Dependency Loading**: `skills: [aws-mcp-setup]`
- **MCP Permissions**: `mcp__cdk__*`, `mcp__aws-mcp__*`, `mcp__awsdocs__*`
- **Bash Permissions**: `Bash(cdk *)`, `Bash(npm *)`, `Bash(aws cloudformation *)`
- **Lifecycle Hook**: PreToolUse hook for `aws sts get-caller-identity` before `cdk deploy*`

This frontmatter configuration ensures the skill has:
1. Isolated execution context
2. Access to AWS documentation through auto-loaded `aws-mcp-setup`
3. Controlled tool permissions for CDK operations
4. Account verification before deployments

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21]()

---

# Page: MCP Server Integration

# MCP Server Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [plugins/aws-common/skills/aws-mcp-setup/SKILL.md](plugins/aws-common/skills/aws-mcp-setup/SKILL.md)
- [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md](plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md)

</details>



This document describes how Model Context Protocol (MCP) servers are integrated into the AWS Skills plugin system. It covers the `mcpServers` configuration structure, server lifecycle management via `uvx`, the standardized tool naming convention, and how plugins declare tool permissions through `allowed-tools` frontmatter. For information about the marketplace and plugin structure, see [Marketplace and Plugin System](#3.1). For information about how skills consume MCP tools during execution, see [Skills and Execution Model](#3.2).

## Overview

MCP servers provide the bridge between Claude Code and AWS services. Plugins declare their required MCP servers in the `marketplace.json` configuration using the `mcpServers` object. Each server is launched as a separate process via the `uvx` package runner, communicates using the `stdio` protocol, and exposes tools following the naming pattern `mcp__plugin_{plugin}_{server}__{tool}`. Skills control which MCP tools they can invoke through the `allowed-tools` frontmatter field.

## mcpServers Configuration Schema

### Plugin-Level Declaration

Plugins declare MCP servers in their `marketplace.json` entry using the `mcpServers` object:

```mermaid
graph TB
    Plugin["Plugin Entry<br/>marketplace.json"]
    McpServers["mcpServers: {}<br/>Server Definitions"]
    ServerKey["Server Key<br/>e.g., 'cdk', 'pricing'"]
    ServerConfig["Server Configuration"]
    Type["type: 'stdio'<br/>Communication Protocol"]
    Command["command: 'uvx'<br/>Launcher Executable"]
    Args["args: []<br/>Package Specification"]
    Env["env: {}<br/>Environment Variables"]
    
    Plugin --> McpServers
    McpServers --> ServerKey
    ServerKey --> ServerConfig
    ServerConfig --> Type
    ServerConfig --> Command
    ServerConfig --> Args
    ServerConfig --> Env
    
    Args --> Package["awslabs.{service}-mcp-server@latest"]
    Env --> LogLevel["FASTMCP_LOG_LEVEL: 'ERROR'"]
```

**Configuration Structure**

Sources: [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111]()

The schema for each MCP server definition:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"stdio"` | Yes | Communication protocol (always stdio) |
| `command` | `"uvx"` | Yes | Launcher command (always uvx) |
| `args` | `string[]` | Yes | Package name and optional arguments |
| `env` | `object` | No | Environment variables for server process |

### Example Configurations

**aws-cdk Plugin - Single Server**

```json
"mcpServers": {
  "cdk": {
    "type": "stdio",
    "command": "uvx",
    "args": [
      "awslabs.cdk-mcp-server@latest"
    ],
    "env": {
      "FASTMCP_LOG_LEVEL": "ERROR"
    }
  }
}
```

Sources: [.claude-plugin/marketplace.json:49-60]()

**aws-cost-ops Plugin - Multiple Servers**

```json
"mcpServers": {
  "pricing": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.aws-pricing-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "costexp": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cost-explorer-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "cw": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cloudwatch-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  }
}
```

Sources: [.claude-plugin/marketplace.json:80-111]()

## Server Naming and Registration

### Server Key Conventions

Each server is identified by a short key in the `mcpServers` object:

| Plugin | Server Key | Package Name | Purpose |
|--------|-----------|--------------|---------|
| aws-cdk | `cdk` | `awslabs.cdk-mcp-server` | CDK construct recommendations |
| aws-cost-ops | `pricing` | `awslabs.aws-pricing-mcp-server` | Service pricing queries |
| aws-cost-ops | `costexp` | `awslabs.cost-explorer-mcp-server` | Historical cost analysis |
| aws-cost-ops | `cw` | `awslabs.cloudwatch-mcp-server` | Metrics and logs queries |
| aws-common | `aws-mcp` or `awsdocs` | Various | Documentation search |

Sources: [.claude-plugin/marketplace.json:11-151]()

### Package Naming Pattern

All AWS MCP servers follow the naming pattern: `awslabs.{service}-mcp-server@latest`

The `@latest` version specification ensures plugins always use the most recent server implementation.

Sources: [.claude-plugin/marketplace.json:54](), [.claude-plugin/marketplace.json:85]()

## Tool Naming Convention

### Pattern Structure

MCP tools exposed to Claude Code follow this naming convention:

```
mcp__plugin_{plugin}_{server}__{tool}
```

```mermaid
graph LR
    Pattern["mcp__plugin_{plugin}_{server}__{tool}"]
    
    Prefix["Prefix: 'mcp__plugin_'<br/>Identifies MCP tool"]
    PluginID["{plugin}<br/>Plugin name"]
    ServerID["{server}<br/>Server key"]
    ToolName["{tool}<br/>Tool function"]
    
    Pattern --> Prefix
    Pattern --> PluginID
    Pattern --> ServerID
    Pattern --> ToolName
    
    PluginID --> Ex1["'aws-cdk'"]
    ServerID --> Ex2["'cdk'"]
    ToolName --> Ex3["'get_construct_info'"]
    
    Ex1 --> Final["mcp__plugin_aws-cdk_cdk__get_construct_info"]
    Ex2 --> Final
    Ex3 --> Final
```

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-10]()

### Real Examples

**aws-cdk Plugin Tools**

- `mcp__plugin_aws-cdk_cdk__get_construct_info`
- `mcp__plugin_aws-cdk_cdk__search_constructs`
- `mcp__plugin_aws-cdk_cdk__recommend_construct`

**aws-cost-ops Plugin Tools**

```
# Pricing server tools
mcp__pricing__get_service_pricing
mcp__pricing__compare_region_pricing
mcp__pricing__estimate_monthly_cost

# Cost Explorer server tools
mcp__costexp__get_cost_and_usage
mcp__costexp__get_cost_forecast
mcp__costexp__get_cost_anomalies

# CloudWatch server tools
mcp__cw__get_metric_statistics
mcp__cw__describe_alarms
mcp__cw__query_logs
```

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-10]()

### Wildcard Pattern Matching

Skills use wildcard patterns in `allowed-tools` to grant access to entire server namespaces:

| Pattern | Matches | Use Case |
|---------|---------|----------|
| `mcp__pricing__*` | All pricing server tools | Grant full pricing access |
| `mcp__costexp__*` | All cost explorer tools | Grant full cost analysis |
| `mcp__cw__*` | All CloudWatch tools | Grant full monitoring access |
| `mcp__aws-mcp__*` | All aws-mcp server tools | Grant documentation + API access |
| `mcp__awsdocs__*` | All awsdocs server tools | Grant documentation-only access |

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-11]()

## Server Lifecycle

### Launch Process

```mermaid
sequenceDiagram
    participant Claude as "Claude Code"
    participant Plugin as "Plugin System"
    participant UVX as "uvx Process"
    participant Server as "MCP Server"
    participant AWS as "AWS Services"
    
    Claude->>Plugin: Load plugin from marketplace
    Plugin->>Plugin: Parse mcpServers config
    Plugin->>UVX: Spawn: uvx awslabs.{service}-mcp-server@latest
    UVX->>UVX: Download package (if needed)
    UVX->>Server: Execute server process
    Server->>Server: Initialize with env vars
    Server->>Plugin: Register tools via stdio
    Plugin->>Claude: Tools available
    
    Claude->>Plugin: Invoke mcp__plugin_{plugin}_{server}__{tool}
    Plugin->>Server: Forward request (stdio)
    Server->>AWS: Execute AWS API call
    AWS->>Server: Return response
    Server->>Plugin: Return result (stdio)
    Plugin->>Claude: Tool result
```

Sources: [.claude-plugin/marketplace.json:49-60]()

### Process Management

**Server Initialization**

1. Plugin installation triggers server registration
2. `uvx` downloads package from PyPI (first run only)
3. Server process spawns with configured environment
4. Server initializes and exposes tools via `stdio`
5. Tools become available to Claude Code session

**Communication Protocol**

- **Protocol**: `stdio` (standard input/output streams)
- **Format**: JSON-RPC 2.0 messages
- **Transport**: Bidirectional pipe between Claude Code and server process
- **Lifecycle**: Server runs for duration of Claude Code session

Sources: [.claude-plugin/marketplace.json:51]()

### Environment Configuration

**Standard Environment Variables**

All MCP servers in the marketplace use consistent environment configuration:

```json
"env": {
  "FASTMCP_LOG_LEVEL": "ERROR"
}
```

| Variable | Value | Purpose |
|----------|-------|---------|
| `FASTMCP_LOG_LEVEL` | `"ERROR"` | Suppress informational logs, show only errors |

This configuration reduces noise in Claude Code output by limiting server logs to critical errors.

Sources: [.claude-plugin/marketplace.json:57-58](), [.claude-plugin/marketplace.json:88-89]()

## Plugin-to-Server Mapping

### Integration Patterns

```mermaid
graph TB
    subgraph "aws-common Plugin"
        AC["aws-common"]
        AC_Server["aws-mcp or awsdocs<br/>(1 server)"]
    end
    
    subgraph "aws-cdk Plugin"
        CDK["aws-cdk"]
        CDK_Server["cdk<br/>(1 server)"]
    end
    
    subgraph "aws-cost-ops Plugin"
        CO["aws-cost-ops"]
        CO_S1["pricing<br/>(1 server)"]
        CO_S2["costexp<br/>(1 server)"]
        CO_S3["cw<br/>(1 server)"]
    end
    
    subgraph "serverless-eda Plugin"
        SE["serverless-eda"]
        SE_None["No MCP servers<br/>(0 servers)"]
    end
    
    subgraph "aws-agentic-ai Plugin"
        AG["aws-agentic-ai"]
        AG_None["No MCP servers<br/>(0 servers)"]
    end
    
    AC --> AC_Server
    CDK --> CDK_Server
    CO --> CO_S1
    CO --> CO_S2
    CO --> CO_S3
    SE --> SE_None
    AG --> AG_None
    
    SE_None -.depends on.-> CDK_Server
    SE_None -.depends on.-> AC_Server
    AG_None -.depends on.-> AC_Server
```

Sources: [.claude-plugin/marketplace.json:11-151]()

### Server Distribution

| Plugin | Servers | Integration Strategy |
|--------|---------|---------------------|
| `aws-common` | 1 | Foundation - documentation access for all plugins |
| `aws-cdk` | 1 | Focused - CDK-specific operations |
| `aws-cost-ops` | 3 | Comprehensive - full cost/monitoring stack |
| `serverless-eda` | 0 | Transitive - uses `aws-cdk` and `aws-common` servers |
| `aws-agentic-ai` | 0 | Transitive - uses `aws-common` documentation |

Plugins without dedicated servers rely on skill dependencies to access MCP tools from foundation plugins.

Sources: [.claude-plugin/marketplace.json:27-29](), [.claude-plugin/marketplace.json:46-48](), [.claude-plugin/marketplace.json:77-79](), [.claude-plugin/marketplace.json:128-130](), [.claude-plugin/marketplace.json:147-149]()

## Tool Permission Model

### allowed-tools Frontmatter

Skills declare which MCP tools they can invoke using the `allowed-tools` field in SKILL.md frontmatter:

```yaml
---
name: aws-cost-operations
allowed-tools:
  - mcp__pricing__*
  - mcp__costexp__*
  - mcp__cw__*
  - mcp__aws-mcp__*
  - mcp__awsdocs__*
  - Bash(aws ce *)
  - Bash(aws cloudwatch *)
---
```

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:1-17]()

### Permission Categories

```mermaid
graph TB
    AllowedTools["allowed-tools:<br/>Tool Permission List"]
    
    MCPWildcard["MCP Server Wildcards<br/>mcp__{server}__*"]
    BashCmds["Bash Command Patterns<br/>Bash(aws {service} *)"]
    SpecificTools["Specific Tools<br/>Full tool names"]
    
    AllowedTools --> MCPWildcard
    AllowedTools --> BashCmds
    AllowedTools --> SpecificTools
    
    MCPWildcard --> Ex1["mcp__pricing__*<br/>All pricing tools"]
    MCPWildcard --> Ex2["mcp__costexp__*<br/>All cost explorer tools"]
    
    BashCmds --> Ex3["Bash(aws ce *)<br/>Cost Explorer CLI"]
    BashCmds --> Ex4["Bash(aws cloudwatch *)<br/>CloudWatch CLI"]
    
    SpecificTools --> Ex5["Bash(aws sts get-caller-identity)<br/>Single command"]
```

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-17]()

### Permission Scope

**MCP Tool Permissions**

- `mcp__pricing__*` - All tools from pricing server
- `mcp__costexp__*` - All tools from cost explorer server
- `mcp__cw__*` - All tools from CloudWatch server
- `mcp__aws-mcp__*` - All tools from full AWS MCP server
- `mcp__awsdocs__*` - All tools from documentation-only server

**Bash Command Permissions**

- `Bash(aws ce *)` - All AWS Cost Explorer CLI commands
- `Bash(aws cloudwatch *)` - All CloudWatch CLI commands
- `Bash(aws logs *)` - All CloudWatch Logs CLI commands
- `Bash(aws budgets *)` - All AWS Budgets CLI commands
- `Bash(aws sts get-caller-identity)` - Single specific command

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-17]()

## AWS MCP Server Setup

### Configuration Options

The `aws-common` plugin provides two MCP server configuration options through the `aws-mcp-setup` skill:

```mermaid
graph TB
    User["User Needs AWS Integration"]
    Check{Has uvx +<br/>AWS credentials?}
    
    FullMCP["Full AWS MCP Server<br/>mcp-proxy-for-aws@latest"]
    DocsMCP["AWS Documentation MCP<br/>knowledge-mcp.global.api.aws"]
    
    FullCapabilities["Capabilities:<br/>- Execute AWS API calls<br/>- Documentation search<br/>- Regional availability"]
    DocsCapabilities["Capabilities:<br/>- Documentation search<br/>- No AWS credentials needed<br/>- Read-only access"]
    
    User --> Check
    Check -->|Yes| FullMCP
    Check -->|No| DocsMCP
    
    FullMCP --> FullCapabilities
    DocsMCP --> DocsCapabilities
    
    FullCapabilities --> Tools1["Tools:<br/>mcp__aws-mcp__aws___search_documentation<br/>mcp__aws-mcp__aws___call_aws"]
    DocsCapabilities --> Tools2["Tools:<br/>mcp__awsdocs__aws___search_documentation<br/>mcp__awsdocs__aws___read_documentation"]
```

Sources: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:12-15]()

### Full AWS MCP Server Configuration

**Configuration Structure**

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=us-west-2"
      ]
    }
  }
}
```

**Credential Options**

| Method | Configuration | Use Case |
|--------|---------------|----------|
| AWS Profile | `--profile my-profile` | Development with named profiles |
| Environment Variables | `env: {AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY}` | CI/CD pipelines |
| IAM Role | No additional config | EC2/ECS/Lambda execution |

Sources: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:94-131]()

### Documentation-Only MCP Configuration

**Configuration Structure**

```json
{
  "mcpServers": {
    "awsdocs": {
      "type": "http",
      "url": "https://knowledge-mcp.global.api.aws"
    }
  }
}
```

**Characteristics**

- No prerequisites (no Python, uvx, or AWS credentials)
- HTTP protocol instead of stdio
- Read-only documentation access
- No AWS API execution capability

Sources: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:141-157]()

## Tool Availability Detection

### Runtime Verification

Skills automatically check for MCP tool availability before executing AWS operations:

```mermaid
graph TB
    SkillInvoke["Skill Invoked<br/>(e.g., aws-cost-operations)"]
    CheckTools{MCP Tools<br/>Available?}
    
    AutoLoad["Auto-load aws-mcp-setup<br/>(skill dependency)"]
    GuidePath{User Has<br/>uvx + credentials?}
    
    FullSetup["Guide: Full AWS MCP Setup<br/>uvx + mcp-proxy-for-aws"]
    DocsSetup["Guide: Documentation MCP<br/>HTTP endpoint only"]
    
    UseMCP["Use MCP Tools<br/>Execute AWS operations"]
    
    SkillInvoke --> CheckTools
    CheckTools -->|No| AutoLoad
    CheckTools -->|Yes| UseMCP
    
    AutoLoad --> GuidePath
    GuidePath -->|Yes| FullSetup
    GuidePath -->|No| DocsSetup
    GuidePath -->|Unknown| Ask["Ask User<br/>Which option?"]
    
    FullSetup --> Verify["Verify Installation<br/>Check for mcp__aws-mcp__*"]
    DocsSetup --> Verify
    Ask --> FullSetup
    Ask --> DocsSetup
    
    Verify --> UseMCP
```

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:29-45]()

### Tool Name Patterns

Skills check for these tool patterns to determine MCP server type:

| Pattern | Server Type | Capabilities |
|---------|------------|--------------|
| `mcp__aws-mcp__*` or `mcp__aws__*` | Full AWS MCP Server | API execution + documentation |
| `mcp__*awsdocs*__aws___*` | Documentation MCP | Documentation only |

Skills use the `/mcp` command to list available MCP servers and verify tool presence.

Sources: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:24-26](), [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:35-38]()

## Error Handling and Logging

### Log Level Configuration

All marketplace-registered MCP servers use `ERROR` log level to minimize output noise:

```json
"env": {
  "FASTMCP_LOG_LEVEL": "ERROR"
}
```

This configuration ensures only critical errors appear in Claude Code output, suppressing informational and debug messages.

Sources: [.claude-plugin/marketplace.json:57-58](), [.claude-plugin/marketplace.json:88-89](), [.claude-plugin/marketplace.json:98-99](), [.claude-plugin/marketplace.json:107-108]()

### Troubleshooting

**Common Issues**

| Issue | Cause | Resolution |
|-------|-------|-----------|
| `uvx: command not found` | uv package manager not installed | Install via `pip install uv` |
| Tools not appearing | Server failed to start | Check server logs, verify package name |
| `AccessDenied` errors | Missing IAM permissions | Add required permissions to IAM policy |
| `InvalidSignatureException` | AWS credential issue | Verify credentials with `aws sts get-caller-identity` |

Sources: [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:170-175]()

---

# Page: Plugins

# Plugins

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



## Purpose and Scope

This page provides an overview of the five plugins available in the AWS Skills marketplace. Each plugin provides specialized AWS development capabilities through Claude Code skills and integrated MCP servers. The page covers plugin categories, versioning, dependency relationships, and MCP server integration patterns.

For detailed documentation on individual plugins, see:
- [aws-common Plugin](#4.1) - Foundational dependency
- [aws-cdk Plugin](#4.2) - Infrastructure as Code
- [aws-cost-ops Plugin](#4.3) - Cost optimization and operations
- [serverless-eda Plugin](#4.4) - Serverless and event-driven architecture
- [aws-agentic-ai Plugin](#4.5) - Bedrock AgentCore for AI agents

For installation instructions, see [Installation](#2.1). For MCP setup, see [MCP Setup](#2.2).

## Plugin Registry Structure

The marketplace registry at [.claude-plugin/marketplace.json:1-152]() defines all five plugins with standardized metadata. The registry operates at version `2.2.0` and is owned by Kane Zhu. Each plugin entry contains:

- `name` - Plugin identifier used in installation commands
- `description` - Brief summary of plugin capabilities
- `version` - Semantic version (either `1.0.0` or `1.2.0`)
- `category` - Either `"development"` or `"operations"`
- `source` - Relative path to plugin directory (e.g., `"./plugins/aws-common"`)
- `skills` - Array of skill paths (e.g., `["./skills/aws-mcp-setup"]`)
- `mcpServers` - Optional object mapping server names to stdio configurations
- `strict` - Boolean flag (set to `false` for all plugins)

### Plugin Registry Overview

```mermaid
graph TB
    subgraph Registry["marketplace.json v2.2.0"]
        direction TB
        Meta["metadata.version: 2.2.0<br/>metadata.description<br/>owner.name/email"]
        
        Plugins["plugins[] array<br/>5 entries"]
    end
    
    subgraph Foundation["Foundation Layer"]
        P0["aws-common<br/>version: 1.0.0<br/>category: development<br/>skills: [aws-mcp-setup]<br/>mcpServers: none"]
    end
    
    subgraph DevPlugins["Development Plugins (v1.2.0)"]
        P1["aws-cdk<br/>version: 1.2.0<br/>skills: [aws-cdk-development]<br/>mcpServers: {cdk}"]
        
        P3["serverless-eda<br/>version: 1.2.0<br/>skills: [aws-serverless-eda]<br/>mcpServers: none"]
        
        P4["aws-agentic-ai<br/>version: 1.2.0<br/>skills: [aws-agentic-ai]<br/>mcpServers: none"]
    end
    
    subgraph OpsPlugins["Operations Plugins (v1.2.0)"]
        P2["aws-cost-ops<br/>version: 1.2.0<br/>skills: [aws-cost-operations]<br/>mcpServers: {pricing, costexp, cw}"]
    end
    
    Registry --> Plugins
    Plugins --> P0
    Plugins --> P1
    Plugins --> P2
    Plugins --> P3
    Plugins --> P4
    
    P1 -.depends on.-> P0
    P2 -.depends on.-> P0
    P3 -.depends on.-> P0
    P4 -.depends on.-> P0
```

**Sources:** [.claude-plugin/marketplace.json:1-152]()

## Plugin Comparison

| Plugin | Version | Category | Skills | MCP Servers | Dependencies | Primary Use Case |
|--------|---------|----------|--------|-------------|--------------|------------------|
| `aws-common` | 1.0.0 | development | 1 | 0 | none | MCP configuration for all plugins |
| `aws-cdk` | 1.2.0 | development | 1 | 1 (cdk) | aws-common | Infrastructure as Code with CDK |
| `aws-cost-ops` | 1.2.0 | operations | 1 | 3 (pricing, costexp, cw) | aws-common | Cost optimization and monitoring |
| `serverless-eda` | 1.2.0 | development | 1 | 0 | aws-common, aws-cdk | Serverless and event-driven architecture |
| `aws-agentic-ai` | 1.2.0 | development | 1 | 0 | aws-common | Bedrock AgentCore for AI agents |

**Sources:** [.claude-plugin/marketplace.json:11-151](), [README.md:5-67]()

## Version Strategy

The marketplace employs a two-tier versioning strategy:

### Foundation Layer (v1.0.0)
The `aws-common` plugin remains at version `1.0.0` [.claude-plugin/marketplace.json:15](), indicating a stable, mature foundation. This lower version number reflects its role as a dependency that rarely changes.

### Domain Plugins (v1.2.0)
All four domain-specific plugins (`aws-cdk`, `aws-cost-ops`, `serverless-eda`, `aws-agentic-ai`) share version `1.2.0` [.claude-plugin/marketplace.json:34,65,116,135](). The higher minor version indicates active development and feature additions.

### Marketplace Version (v2.2.0)
The overall marketplace version `2.2.0` [.claude-plugin/marketplace.json:9]() tracks structural changes to the plugin ecosystem itself, such as adding new plugins to the registry.

**Sources:** [.claude-plugin/marketplace.json:9,15,34,65,116,135]()

## Dependency Architecture

All domain plugins declare a transitive dependency on `aws-common` through their skill frontmatter configurations. The `serverless-eda` plugin additionally depends on `aws-cdk` skills.

### Plugin Dependency Graph

```mermaid
graph TB
    subgraph Users["User Installation"]
        U1["Install aws-common first"]
        U2["Install domain plugins"]
    end
    
    subgraph Plugins["Plugin Layer"]
        Common["aws-common@1.0.0<br/>./plugins/aws-common<br/>skills: [./skills/aws-mcp-setup]"]
        
        CDK["aws-cdk@1.2.0<br/>./plugins/aws-cdk<br/>skills: [./skills/aws-cdk-development]"]
        
        Cost["aws-cost-ops@1.2.0<br/>./plugins/aws-cost-ops<br/>skills: [./skills/aws-cost-operations]"]
        
        Serverless["serverless-eda@1.2.0<br/>./plugins/serverless-eda<br/>skills: [./skills/aws-serverless-eda]"]
        
        Agentic["aws-agentic-ai@1.2.0<br/>./plugins/aws-agentic-ai<br/>skills: [./skills/aws-agentic-ai]"]
    end
    
    subgraph Skills["Skill Layer (Frontmatter Dependencies)"]
        SkillCommon["aws-mcp-setup skill<br/>No dependencies"]
        
        SkillCDK["aws-cdk-development skill<br/>skills: [aws-mcp-setup]"]
        
        SkillCost["aws-cost-operations skill<br/>skills: [aws-mcp-setup]"]
        
        SkillServerless["aws-serverless-eda skill<br/>skills: [aws-mcp-setup,<br/>aws-cdk-development]"]
        
        SkillAgentic["aws-agentic-ai skill<br/>skills: [aws-mcp-setup]"]
    end
    
    U1 --> Common
    U2 --> CDK
    U2 --> Cost
    U2 --> Serverless
    U2 --> Agentic
    
    Common --> SkillCommon
    CDK --> SkillCDK
    Cost --> SkillCost
    Serverless --> SkillServerless
    Agentic --> SkillAgentic
    
    SkillCDK -.auto-loads.-> SkillCommon
    SkillCost -.auto-loads.-> SkillCommon
    SkillServerless -.auto-loads.-> SkillCommon
    SkillServerless -.auto-loads.-> SkillCDK
    SkillAgentic -.auto-loads.-> SkillCommon
```

**Installation Requirement:** Users must install `aws-common` before any domain plugin [.claude-plugin/marketplace.json:11-30](), as documented in [README.md:77-87](). The skill dependency chain automatically loads required skills at runtime through the frontmatter `skills:` field.

**Sources:** [.claude-plugin/marketplace.json:11-151](), [README.md:77-87]()

## MCP Server Integration

Plugins vary significantly in their MCP server integration complexity. The `mcpServers` object in each plugin definition configures stdio-based MCP servers launched via `uvx`.

### MCP Server Configuration Pattern

All MCP servers follow the standardized configuration pattern defined in [.claude-plugin/marketplace.json:49-60,80-111]():

```json
"mcpServers": {
  "<server-name>": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.<package>-mcp-server@latest"],
    "env": {
      "FASTMCP_LOG_LEVEL": "ERROR"
    }
  }
}
```

### MCP Server Distribution

```mermaid
graph LR
    subgraph NoServers["Pattern-Based Plugins (0 servers)"]
        NoneCommon["aws-common<br/>mcpServers: undefined"]
        NoneServerless["serverless-eda<br/>mcpServers: undefined"]
        NoneAgentic["aws-agentic-ai<br/>mcpServers: undefined"]
    end
    
    subgraph OneServer["Single-Server Plugins (1 server)"]
        OneCDK["aws-cdk<br/>mcpServers.cdk"]
    end
    
    subgraph ThreeServers["Multi-Server Plugins (3 servers)"]
        ThreeCost["aws-cost-ops<br/>mcpServers.pricing<br/>mcpServers.costexp<br/>mcpServers.cw"]
    end
    
    subgraph MCPPackages["AWS Labs MCP Packages"]
        PKG1["awslabs.cdk-mcp-server@latest"]
        PKG2["awslabs.aws-pricing-mcp-server@latest"]
        PKG3["awslabs.cost-explorer-mcp-server@latest"]
        PKG4["awslabs.cloudwatch-mcp-server@latest"]
    end
    
    OneCDK -->|uvx stdio| PKG1
    ThreeCost -->|uvx stdio| PKG2
    ThreeCost -->|uvx stdio| PKG3
    ThreeCost -->|uvx stdio| PKG4
    
    NoneCommon -.references.-> PKG1
    NoneServerless -.uses CDK skill.-> OneCDK
    NoneAgentic -.uses common skill.-> NoneCommon
```

**Integration Strategy:**
- **Zero Integration**: `aws-common`, `serverless-eda`, and `aws-agentic-ai` define no `mcpServers` [.claude-plugin/marketplace.json:11-30,113-131,132-150](). These plugins rely on pattern libraries, documentation, and transitive dependencies.
- **Single Integration**: `aws-cdk` integrates one server named `cdk` for CDK construct operations [.claude-plugin/marketplace.json:49-60]()
- **Multi Integration**: `aws-cost-ops` integrates three servers for comprehensive cost/monitoring [.claude-plugin/marketplace.json:80-111]():
  - `pricing` - AWS Pricing API access
  - `costexp` - Cost Explorer analysis
  - `cw` - CloudWatch metrics and logs

**Sources:** [.claude-plugin/marketplace.json:49-111]()

## Plugin Categories and Use Cases

### Development Plugins (category: "development")

Four plugins target the development phase with `"category": "development"` [.claude-plugin/marketplace.json:24,43,125,144]():

**aws-common** [.claude-plugin/marketplace.json:13-30]()
- **Primary Purpose**: MCP configuration and AWS documentation access
- **Key Skill**: `aws-mcp-setup` for setting up AWS MCP tools
- **Usage**: Automatically loaded by all other plugins as a dependency
- **When to Use**: Required for all AWS development in Claude Code

**aws-cdk** [.claude-plugin/marketplace.json:32-61]()
- **Primary Purpose**: Infrastructure as Code with AWS CDK
- **Key Features**: CDK best practices, resource naming conventions, Lambda bundling
- **MCP Server**: CDK MCP for construct recommendations
- **When to Use**: Building and deploying AWS infrastructure with CDK

**serverless-eda** [.claude-plugin/marketplace.json:113-131]()
- **Primary Purpose**: Serverless and event-driven architecture patterns
- **Key Features**: 7 Well-Architected design principles, event-driven patterns, Step Functions orchestration
- **Dependencies**: `aws-common` + `aws-cdk` (transitive)
- **When to Use**: Designing serverless applications or event-driven systems

**aws-agentic-ai** [.claude-plugin/marketplace.json:132-150]()
- **Primary Purpose**: Bedrock AgentCore for AI agent deployment
- **Key Features**: 7 AgentCore services (Gateway, Runtime, Memory, Identity, Code Interpreter, Browser, Observability)
- **When to Use**: Building and deploying AI agents with Bedrock AgentCore

### Operations Plugins (category: "operations")

One plugin targets post-deployment operations with `"category": "operations"` [.claude-plugin/marketplace.json:74]():

**aws-cost-ops** [.claude-plugin/marketplace.json:63-112]()
- **Primary Purpose**: Cost optimization, monitoring, and operational excellence
- **MCP Servers**: 3 servers for pricing, cost analysis, and CloudWatch
- **Key Features**: Pre-deployment cost estimation, post-deployment analysis, monitoring patterns
- **When to Use**: Optimizing costs, setting up monitoring, or investigating operational issues

**Sources:** [.claude-plugin/marketplace.json:13-150](), [README.md:7-67]()

## Plugin Selection Guide

```mermaid
graph TB
    Start{What is your<br/>use case?}
    
    Start -->|Infrastructure as Code| CDK
    Start -->|Serverless Applications| ServerlessQ{Need CDK<br/>integration?}
    Start -->|AI Agent Development| Agentic
    Start -->|Cost Management| Cost
    Start -->|Monitoring Setup| Cost
    
    ServerlessQ -->|Yes| ServerlessCDK[Install serverless-eda<br/>Auto-loads: aws-cdk, aws-common]
    ServerlessQ -->|No| ServerlessOnly[Install serverless-eda<br/>Auto-loads: aws-common]
    
    CDK[Install aws-cdk<br/>Auto-loads: aws-common<br/>MCP: 1 server]
    
    Cost[Install aws-cost-ops<br/>Auto-loads: aws-common<br/>MCP: 3 servers]
    
    Agentic[Install aws-agentic-ai<br/>Auto-loads: aws-common<br/>MCP: 0 servers]
    
    subgraph Prerequisites["Prerequisites"]
        P1[1. /plugin marketplace add zxkane/aws-skills]
        P2[2. /plugin install aws-common@aws-skills]
    end
    
    Prerequisites -.must install first.-> CDK
    Prerequisites -.must install first.-> Cost
    Prerequisites -.must install first.-> ServerlessCDK
    Prerequisites -.must install first.-> ServerlessOnly
    Prerequisites -.must install first.-> Agentic
```

**Decision Criteria:**

| If you need to... | Install | Rationale |
|-------------------|---------|-----------|
| Build CDK infrastructure | `aws-cdk` | Provides CDK patterns, validation, and MCP server |
| Design serverless systems | `serverless-eda` | Provides 7 Well-Architected principles and event patterns |
| Deploy AI agents | `aws-agentic-ai` | Comprehensive AgentCore service coverage |
| Estimate costs before deployment | `aws-cost-ops` | Pricing MCP server for cost estimation |
| Monitor existing resources | `aws-cost-ops` | CloudWatch MCP server for metrics and logs |
| Analyze spending patterns | `aws-cost-ops` | Cost Explorer MCP server for analysis |
| Query AWS documentation | Already included | `aws-common` auto-loads with any plugin |

**Sources:** [.claude-plugin/marketplace.json:11-151](), [README.md:69-87]()

## Plugin Metadata Fields

Each plugin entry in [.claude-plugin/marketplace.json:11-151]() contains the following standardized fields:

### Required Fields
- `name` - String identifier (e.g., `"aws-common"`, `"aws-cdk"`)
- `description` - Brief summary of capabilities
- `version` - Semantic version string
- `author.name` - Author name (all plugins: `"Kane Zhu"`)
- `author.email` - Author email (all plugins: `"me@kane.mx"`)
- `homepage` - GitHub repository URL
- `repository` - GitHub repository URL (same as homepage)
- `license` - License type (all plugins: `"MIT"`)
- `keywords` - Array of searchable keywords
- `category` - Either `"development"` or `"operations"`
- `source` - Relative path to plugin directory
- `strict` - Boolean flag (all plugins: `false`)
- `skills` - Array of skill paths

### Optional Fields
- `mcpServers` - Object mapping server names to stdio configurations (only present in `aws-cdk` and `aws-cost-ops`)

**Sources:** [.claude-plugin/marketplace.json:11-151]()

---

# Page: aws-common Plugin

# aws-common Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [docs/aws-mcp-setup.md](docs/aws-mcp-setup.md)
- [plugins/aws-common/skills/aws-mcp-setup/SKILL.md](plugins/aws-common/skills/aws-mcp-setup/SKILL.md)

</details>



## Purpose and Scope

The `aws-common` plugin provides foundational AWS integration capabilities that all other plugins in the marketplace depend on. It contains the `aws-mcp-setup` skill, which guides users through configuring AWS MCP (Model Context Protocol) tools for accessing up-to-date AWS documentation and APIs. This plugin must be installed before any domain-specific plugins (`aws-cdk`, `aws-cost-ops`, `serverless-eda`, `aws-agentic-ai`) can function properly.

For installation procedures and dependency order, see [Installation](#2.1). For broader marketplace architecture, see [Marketplace and Plugin System](#3.1).

## Plugin Registration and Metadata

The `aws-common` plugin is registered in the marketplace with stable foundational status:

| Property | Value |
|----------|-------|
| Name | `aws-common` |
| Version | `1.0.0` |
| Category | `development` |
| Source | `./plugins/aws-common` |
| Strict Mode | `false` |
| Skills | `aws-mcp-setup` |
| MCP Servers | None (guides configuration only) |

The plugin's stability is reflected in its v1.0.0 version, while domain plugins evolve more rapidly at v1.2.0. This version differential indicates `aws-common` serves as a stable dependency foundation.

**Plugin Registration Structure**

```mermaid
graph TB
    subgraph "Marketplace Registry"
        Marketplace["marketplace.json<br/>version: 2.2.0"]
    end
    
    subgraph "aws-common Plugin v1.0.0"
        PluginMeta["Plugin Metadata<br/>name: aws-common<br/>category: development<br/>strict: false"]
        Skill["Skills Array<br/>./skills/aws-mcp-setup"]
        NoServers["mcpServers: undefined<br/>(Configuration only)"]
    end
    
    subgraph "Dependent Plugins"
        CDK["aws-cdk v1.2.0<br/>skills: [aws-mcp-setup]"]
        Cost["aws-cost-ops v1.2.0<br/>skills: [aws-mcp-setup]"]
        Serverless["serverless-eda v1.2.0<br/>skills: [aws-mcp-setup, aws-cdk-development]"]
        Agentic["aws-agentic-ai v1.2.0<br/>skills: [aws-mcp-setup]"]
    end
    
    Marketplace --> PluginMeta
    PluginMeta --> Skill
    PluginMeta --> NoServers
    
    CDK -.depends on.-> Skill
    Cost -.depends on.-> Skill
    Serverless -.depends on.-> Skill
    Agentic -.depends on.-> Skill
```

**Sources:** [.claude-plugin/marketplace.json:11-30]()

## Architecture and Dependency Model

Unlike other plugins that bundle MCP servers, `aws-common` provides a configuration skill that guides users to set up external AWS MCP infrastructure. This architectural choice enables centralized MCP configuration that all plugins can reference.

**Dependency Resolution Flow**

```mermaid
graph TB
    subgraph "User Installation"
        Install1["Install aws-common<br/>(Required First)"]
        Install2["Install domain plugins<br/>(CDK, Cost, etc)"]
    end
    
    subgraph "Skill Auto-Loading"
        DomainSkill["Domain Skill Invoked<br/>(e.g., aws-cdk-development)"]
        CheckDeps["Check skills: array<br/>in frontmatter"]
        LoadCommon["Auto-load aws-mcp-setup"]
    end
    
    subgraph "MCP Availability Check"
        CheckTools{"MCP Tools<br/>Available?"}
        GuideSetup["Guide through<br/>MCP configuration"]
        UseTools["Use MCP tools<br/>for AWS queries"]
    end
    
    subgraph "Configuration Locations"
        ProjectConfig[".mcp.json<br/>(project scope)"]
        UserConfig["~/.claude.json<br/>(user scope)"]
        LocalConfig[".claude.json<br/>(local scope)"]
    end
    
    Install1 --> Install2
    Install2 --> DomainSkill
    DomainSkill --> CheckDeps
    CheckDeps --> LoadCommon
    LoadCommon --> CheckTools
    
    CheckTools -->|No| GuideSetup
    CheckTools -->|Yes| UseTools
    
    GuideSetup --> ProjectConfig
    GuideSetup --> UserConfig
    GuideSetup --> LocalConfig
```

**Sources:** [.claude-plugin/marketplace.json:11-30](), [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:1-20]()

## aws-mcp-setup Skill

The `aws-mcp-setup` skill is the only skill provided by this plugin. It serves as a gatekeeper that ensures AWS MCP tools are configured before any domain plugin can provide AWS-specific guidance.

**Skill Configuration**

```yaml
name: aws-mcp-setup
description: Configure AWS Documentation MCP server to query up-to-date AWS knowledge, APIs, and best practices
```

The skill operates through an interactive configuration guide rather than executable tools, distinguishing it from typical skills that perform operations.

**MCP Configuration Architecture**

```mermaid
graph TB
    subgraph "Skill Entry Point"
        SkillMD["SKILL.md<br/>plugins/aws-common/skills/aws-mcp-setup/"]
        Frontmatter["Frontmatter:<br/>name, description"]
        Content["Markdown Content:<br/>Configuration Guide"]
    end
    
    subgraph "Configuration Discovery"
        CheckMethod1["Method A: Check Tools<br/>/mcp command"]
        CheckMethod2["Method B: Check Files<br/>.mcp.json, ~/.claude.json"]
        ToolPatterns["Tool Name Patterns:<br/>mcp__aws-mcp__*<br/>mcp__*awsdocs*__*"]
    end
    
    subgraph "Hierarchical Config System"
        Enterprise["Enterprise Config<br/>(system managed)"]
        User["User Config<br/>~/.claude.json"]
        Project["Project Config<br/>.mcp.json"]
        Local["Local Config<br/>.claude.json"]
        
        Enterprise --> User
        User --> Project
        Project --> Local
    end
    
    subgraph "Detection Commands"
        CheckUVX["which uvx"]
        CheckAWS["aws sts get-caller-identity"]
    end
    
    SkillMD --> Frontmatter
    SkillMD --> Content
    Content --> CheckMethod1
    Content --> CheckMethod2
    
    CheckMethod1 --> ToolPatterns
    CheckMethod2 --> Enterprise
    
    Content --> CheckUVX
    Content --> CheckAWS
```

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:1-68]()

## MCP Configuration Options

The skill guides users through two distinct MCP server configurations based on their environment and requirements.

### Option A: Full AWS MCP Server

The Full AWS MCP Server provides comprehensive AWS integration including API execution and documentation search.

**Prerequisites and Detection**

| Requirement | Detection Command | Purpose |
|-------------|------------------|---------|
| Python 3.10+ | `which uvx` | MCP server launcher |
| uvx package manager | `uvx --version` | Package execution |
| AWS credentials | `aws sts get-caller-identity` | API authentication |

**IAM Permissions Required**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "aws-mcp:InvokeMCP",
      "aws-mcp:CallReadOnlyTool",
      "aws-mcp:CallReadWriteTool"
    ],
    "Resource": "*"
  }]
}
```

**Configuration Structure**

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=us-west-2"
      ]
    }
  }
}
```

**Credential Configuration Variants**

```mermaid
graph TB
    subgraph "Full AWS MCP Configuration"
        BaseConfig["Base Configuration<br/>command: uvx<br/>args: [mcp-proxy-for-aws@latest]"]
    end
    
    subgraph "Credential Options"
        Profile["AWS Profile<br/>--profile my-profile<br/>(Recommended for dev)"]
        EnvVars["Environment Variables<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY"]
        IAMRole["IAM Role<br/>EC2/ECS/Lambda<br/>(No additional config)"]
    end
    
    subgraph "Additional Parameters"
        Region["--region us-west-2"]
        ReadOnly["--read-only<br/>(Restrict permissions)"]
        LogLevel["--log-level ERROR"]
    end
    
    subgraph "Resulting Tools"
        SearchDoc["mcp__aws-mcp__aws___search_documentation"]
        CallAWS["mcp__aws-mcp__aws___call_aws"]
        ReadDoc["mcp__aws-mcp__aws___read_documentation"]
    end
    
    BaseConfig --> Profile
    BaseConfig --> EnvVars
    BaseConfig --> IAMRole
    
    Profile --> Region
    EnvVars --> Region
    IAMRole --> Region
    
    Region --> ReadOnly
    ReadOnly --> LogLevel
    
    LogLevel --> SearchDoc
    LogLevel --> CallAWS
    LogLevel --> ReadDoc
```

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:64-137](), [docs/aws-mcp-setup.md:64-132]()

### Option B: AWS Documentation MCP

The AWS Documentation MCP provides documentation search without requiring AWS credentials or local Python environment.

**Use Cases**

- No Python/uvx installation available
- No AWS credentials configured
- Documentation-only requirements
- Public/read-only environments

**Configuration Structure**

```json
{
  "mcpServers": {
    "awsdocs": {
      "type": "http",
      "url": "https://knowledge-mcp.global.api.aws"
    }
  }
}
```

**Tool Availability Comparison**

| Capability | Full AWS MCP | Documentation MCP |
|------------|-------------|-------------------|
| Documentation Search | `mcp__aws-mcp__aws___search_documentation` | `mcp__awsdocs__aws___search_documentation` |
| Documentation Read | `mcp__aws-mcp__aws___read_documentation` | `mcp__awsdocs__aws___read_documentation` |
| Regional Availability | `mcp__aws-mcp__aws___get_regional_availability` | `mcp__awsdocs__aws___get_regional_availability` |
| AWS API Calls | `mcp__aws-mcp__aws___call_aws` | ❌ Not Available |
| Authentication | AWS credentials required | None required |
| Network | Outbound to aws-mcp endpoint | Outbound to knowledge-mcp endpoint |

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:139-167](), [docs/aws-mcp-setup.md:134-161]()

## Configuration File Hierarchy

The MCP server configuration follows a hierarchical precedence model where more specific scopes override broader ones.

**Configuration Precedence Flow**

```mermaid
graph LR
    subgraph "Precedence Order (Left = Lowest, Right = Highest)"
        Enterprise["Enterprise<br/>(System Managed)<br/>Lowest Priority"]
        User["User<br/>~/.claude.json<br/>Cross-Project"]
        Project["Project<br/>.mcp.json<br/>Team Shared"]
        Local["Local<br/>.claude.json<br/>Experimental"]
    end
    
    Enterprise -->|overridden by| User
    User -->|overridden by| Project
    Project -->|overridden by| Local
```

**Configuration Check Commands**

```bash
# Check project configuration
cat .mcp.json 2>/dev/null | grep -E '"(aws-mcp|aws|awsdocs)"'

# Check user configuration
cat ~/.claude.json 2>/dev/null | grep -E '"(aws-mcp|aws|awsdocs)"'

# List all MCP servers
claude mcp list
```

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:29-51](), [docs/aws-mcp-setup.md:24-46]()

## Verification and Validation

After configuration, the skill provides verification steps to confirm MCP tools are accessible.

**Tool Name Pattern Detection**

```mermaid
graph TB
    subgraph "Verification Entry"
        RunMCP["/mcp command<br/>List active servers"]
    end
    
    subgraph "Full AWS MCP Detection"
        Pattern1["mcp__aws-mcp__*"]
        Pattern2["mcp__aws__*"]
        FullTools["Expected Tools:<br/>aws___search_documentation<br/>aws___call_aws<br/>aws___read_documentation"]
    end
    
    subgraph "Documentation MCP Detection"
        Pattern3["mcp__*awsdocs*__*"]
        DocTools["Expected Tools:<br/>aws___search_documentation<br/>aws___read_documentation<br/>aws___get_regional_availability"]
    end
    
    subgraph "Configuration Valid"
        Success["MCP Tools Available<br/>Proceed with domain plugins"]
    end
    
    RunMCP --> Pattern1
    RunMCP --> Pattern2
    RunMCP --> Pattern3
    
    Pattern1 --> FullTools
    Pattern2 --> FullTools
    Pattern3 --> DocTools
    
    FullTools --> Success
    DocTools --> Success
```

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:158-167](), [docs/aws-mcp-setup.md:153-161]()

## Troubleshooting

Common issues and resolutions for MCP configuration:

| Issue | Cause | Solution |
|-------|-------|----------|
| `uvx: command not found` | uv not installed | Install with `pip install uv` or use Documentation MCP (Option B) |
| `AccessDenied` error | Missing IAM permissions | Add `aws-mcp:*` permissions to IAM policy |
| `InvalidSignatureException` | Credential misconfiguration | Verify with `aws sts get-caller-identity` |
| Tools not appearing | MCP not started | Restart Claude Code after configuration change |
| Wrong tools available | Configuration scope conflict | Check hierarchical config with `claude mcp list` |

**Diagnostic Command Flow**

```mermaid
graph TB
    Issue["MCP Tools Not Working"]
    
    CheckInstall{"uvx installed?"}
    CheckCreds{"AWS credentials<br/>valid?"}
    CheckConfig{"Configuration<br/>file correct?"}
    CheckRestart{"Claude Code<br/>restarted?"}
    
    FixInstall["Install uv:<br/>pip install uv"]
    FixCreds["Configure AWS:<br/>aws configure<br/>OR use Documentation MCP"]
    FixConfig["Review config hierarchy:<br/>claude mcp list<br/>Check .mcp.json syntax"]
    FixRestart["Restart Claude Code<br/>to reload MCP servers"]
    
    Success["MCP Tools Available"]
    
    Issue --> CheckInstall
    CheckInstall -->|No| FixInstall
    CheckInstall -->|Yes| CheckCreds
    
    CheckCreds -->|No| FixCreds
    CheckCreds -->|Yes| CheckConfig
    
    CheckConfig -->|No| FixConfig
    CheckConfig -->|Yes| CheckRestart
    
    CheckRestart -->|No| FixRestart
    CheckRestart -->|Yes| Success
    
    FixInstall --> CheckCreds
    FixCreds --> CheckConfig
    FixConfig --> CheckRestart
    FixRestart --> Success
```

**Sources:** [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:169-176](), [docs/aws-mcp-setup.md:163-170]()

## Integration with Domain Plugins

All domain plugins in the marketplace declare `aws-mcp-setup` as a required skill dependency, creating an automatic bootstrap mechanism.

**Dependency Declaration Pattern**

When a domain plugin skill is invoked, its frontmatter `skills:` array triggers automatic loading:

```yaml
# Example from aws-cdk-development skill
skills: [aws-mcp-setup]

# Example from aws-serverless-eda skill  
skills: [aws-mcp-setup, aws-cdk-development]
```

This ensures that before any AWS-specific guidance is provided, the MCP configuration check occurs automatically. If tools are unavailable, users are guided through setup before proceeding.

**Auto-Loading Mechanism**

```mermaid
graph TB
    subgraph "User Action"
        UserPrompt["User invokes domain skill<br/>e.g., aws-cdk-development"]
    end
    
    subgraph "Dependency Resolution"
        CheckFrontmatter["Parse SKILL.md frontmatter<br/>skills: [aws-mcp-setup]"]
        LoadDeps["Auto-load dependent skills<br/>in declaration order"]
    end
    
    subgraph "MCP Verification"
        MCPCheck{"MCP tools<br/>available?"}
        ShowGuide["Present aws-mcp-setup<br/>configuration guide"]
        Proceed["Proceed with<br/>domain skill execution"]
    end
    
    subgraph "Tool Usage"
        SearchDocs["Use mcp__*__aws___search_documentation<br/>for current AWS info"]
        ExecuteOps["Execute domain-specific<br/>operations with validated context"]
    end
    
    UserPrompt --> CheckFrontmatter
    CheckFrontmatter --> LoadDeps
    LoadDeps --> MCPCheck
    
    MCPCheck -->|No| ShowGuide
    MCPCheck -->|Yes| Proceed
    
    ShowGuide -.user configures.-> MCPCheck
    Proceed --> SearchDocs
    SearchDocs --> ExecuteOps
```

**Sources:** [.claude-plugin/marketplace.json:46-48](), [.claude-plugin/marketplace.json:77-78](), [.claude-plugin/marketplace.json:128-129](), [.claude-plugin/marketplace.json:147-148]()

## Design Rationale

The `aws-common` plugin's architecture reflects several key design decisions:

1. **Separation of Concerns**: Configuration guidance is separated from MCP server implementation, allowing external AWS MCP infrastructure to evolve independently.

2. **Zero MCP Servers**: Unlike domain plugins, `aws-common` bundles no MCP servers. This prevents version conflicts and allows users to configure the AWS MCP version that matches their requirements.

3. **Bootstrap Pattern**: By being a required dependency for all domain plugins, it creates a centralized entry point for AWS infrastructure configuration verification.

4. **Version Stability**: The v1.0.0 version signals API stability—domain plugins can safely depend on `aws-mcp-setup` without frequent breaking changes.

5. **Hierarchical Configuration**: Supporting multiple configuration scopes (enterprise → user → project → local) enables both organizational standards and individual experimentation.

**Sources:** [.claude-plugin/marketplace.json:11-30](), [plugins/aws-common/skills/aws-mcp-setup/SKILL.md:1-176]()

---

# Page: aws-cdk Plugin

# aws-cdk Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md](plugins/aws-cdk/skills/aws-cdk-development/SKILL.md)

</details>



The `aws-cdk` plugin provides comprehensive AWS Cloud Development Kit (CDK) development capabilities for Claude Code, enabling infrastructure-as-code development with TypeScript and Python. This plugin includes the `aws-cdk-development` skill, integrated CDK MCP server, validation scripts, and a comprehensive patterns library. It enforces AWS best practices including automatic resource naming, appropriate Lambda construct usage, and multi-layer pre-deployment validation.

This page covers the CDK plugin's structure, skill configuration, validation strategies, and MCP integration. For foundational MCP setup that this plugin depends on, see [aws-common Plugin](#4.1). For serverless patterns that build upon CDK infrastructure, see [serverless-eda Plugin](#4.4). For the complete plugin installation sequence, see [Installation](#2.1).

## Plugin Overview

The `aws-cdk` plugin is one of three development-focused plugins (alongside `serverless-eda` and `aws-agentic-ai`) at version 1.2.0. It provides a single skill (`aws-cdk-development`) with integrated tooling for CDK stack development, synthesis, and deployment.

**Key Characteristics**:
- **Version**: 1.2.0 (development plugin tier)
- **Dependencies**: `aws-common` v1.0.0 (required)
- **MCP Servers**: 1 server (CDK MCP)
- **Primary Skill**: `aws-cdk-development`
- **Execution Context**: Fork (isolated sub-agent)

Sources: [README.md:18-29](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-6]()

## Plugin Directory Structure

The plugin follows the standardized AWS Skills directory pattern with skills, references, and scripts:

```mermaid
graph TB
    subgraph "Plugin Root: plugins/aws-cdk/"
        SkillDir["skills/"]
        
        subgraph "Skill: aws-cdk-development/"
            SkillMD["SKILL.md<br/>(Frontmatter + Content)"]
            RefDir["references/"]
            ScriptDir["scripts/"]
            
            subgraph "References"
                CDKPatterns["cdk-patterns.md<br/>(Pattern Library)"]
            end
            
            subgraph "Scripts"
                ValidateScript["validate-stack.sh<br/>(Pre-deployment checks)"]
            end
        end
    end
    
    subgraph "Frontmatter Configuration"
        Name["name: aws-cdk-development"]
        Context["context: fork"]
        SkillDeps["skills: [aws-mcp-setup]"]
        Tools["allowed-tools:<br/>- mcp__cdk__*<br/>- mcp__aws-mcp__*<br/>- mcp__awsdocs__*<br/>- Bash(cdk *)<br/>- Bash(npm *)<br/>- Bash(aws cloudformation *)"]
        Hooks["hooks:<br/>PreToolUse: aws sts get-caller-identity"]
    end
    
    SkillDir --> SkillMD
    SkillDir --> RefDir
    SkillDir --> ScriptDir
    RefDir --> CDKPatterns
    ScriptDir --> ValidateScript
    
    SkillMD --> Name
    SkillMD --> Context
    SkillMD --> SkillDeps
    SkillMD --> Tools
    SkillMD --> Hooks
```

**Directory Mapping**:

| Path | Purpose | Key Content |
|------|---------|-------------|
| `plugins/aws-cdk/skills/aws-cdk-development/` | Skill root directory | All skill components |
| `SKILL.md` | Skill definition with frontmatter | Configuration + guidance content |
| `references/cdk-patterns.md` | Pattern library | Detailed CDK patterns, anti-patterns |
| `scripts/validate-stack.sh` | Validation script | Pre-deployment safety checks |

Sources: [README.md:227-243](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21]()

## The aws-cdk-development Skill

The `aws-cdk-development` skill is the core component of this plugin, configured through frontmatter metadata in `SKILL.md`.

### Skill Metadata Configuration

```mermaid
graph LR
    subgraph "SKILL.md Frontmatter"
        Name["name:<br/>aws-cdk-development"]
        Desc["description:<br/>CDK expert for TypeScript/Python"]
        Context["context: fork"]
        
        subgraph "Dependency Chain"
            SkillDep["skills:<br/>- aws-mcp-setup"]
        end
        
        subgraph "Tool Permissions"
            MCPTools["mcp__cdk__*<br/>mcp__aws-mcp__*<br/>mcp__awsdocs__*"]
            BashTools["Bash(cdk *)<br/>Bash(npm *)<br/>Bash(npx *)<br/>Bash(aws cloudformation *)<br/>Bash(aws sts get-caller-identity)"]
        end
        
        subgraph "Lifecycle Hooks"
            PreHook["PreToolUse:<br/>matcher: Bash(cdk deploy*)<br/>command: aws sts get-caller-identity<br/>once: true"]
        end
    end
    
    subgraph "Runtime Behavior"
        Fork["Fork Context<br/>(Isolated Sub-Agent)"]
        AutoLoad["Auto-load aws-mcp-setup"]
        AccountCheck["Account Verification<br/>Before Deploy"]
    end
    
    Context --> Fork
    SkillDep --> AutoLoad
    PreHook --> AccountCheck
    MCPTools --> Fork
    BashTools --> Fork
```

**Frontmatter Fields**:

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `aws-cdk-development` | Skill identifier |
| `description` | CDK expert for TypeScript/Python | Invocation trigger keywords |
| `context` | `fork` | Execute in isolated sub-agent |
| `skills` | `[aws-mcp-setup]` | Auto-load dependency |
| `allowed-tools` | MCP servers + bash commands | Tool permission whitelist |
| `hooks.PreToolUse` | Account verification | Pre-deployment safety check |

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:1-21]()

### Invocation Triggers

The skill activates when users mention CDK-related keywords in prompts. From the description field:

**Trigger Keywords**: "CDK", "CloudFormation", "IaC", "cdk synth", "cdk deploy", "CDK stacks", "CDK constructs", "infrastructure as code", "define AWS infrastructure programmatically"

**Usage Scenarios**:
- Creating new CDK stacks or constructs
- Refactoring existing CDK infrastructure
- Implementing Lambda functions within CDK
- Validating CDK stack configurations
- Synthesizing and deploying CloudFormation templates

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:3](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:59-68]()

## Core CDK Principles

The plugin enforces two critical CDK principles through skill guidance and validation.

### Resource Naming Convention

**Principle**: Do NOT explicitly specify resource names when optional in CDK constructs.

**Implementation Pattern**:

```mermaid
graph TB
    subgraph "Resource Naming Pattern"
        Decision{Resource Name<br/>Optional?}
        
        Bad["❌ BAD Pattern:<br/>functionName: 'my-lambda'"]
        Good["✅ GOOD Pattern:<br/>No functionName specified"]
        
        Decision -->|Yes| Good
        Decision -->|Specified anyway| Bad
        
        subgraph "Bad Pattern Consequences"
            Conflict["Name Conflicts"]
            NoReuse["Cannot Reuse Pattern"]
            NoParallel["No Parallel Deployment"]
            NoIsolation["No Stack Isolation"]
        end
        
        subgraph "Good Pattern Benefits"
            UniqueNames["CDK Generates:<br/>StackName-MyFunctionXXXXXX"]
            Reuse["Deploy Pattern Multiple Times"]
            Parallel["Parallel Stack Deployment"]
            Isolation["Automatic Stack Isolation"]
        end
        
        Bad --> Conflict
        Bad --> NoReuse
        Bad --> NoParallel
        Bad --> NoIsolation
        
        Good --> UniqueNames
        Good --> Reuse
        Good --> Parallel
        Good --> Isolation
    end
```

**Code Example from Skill**:

The skill provides explicit guidance at [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:83-95]():

```typescript
// ❌ BAD - Explicit naming prevents reusability and parallel deployments
new lambda.Function(this, 'MyFunction', {
  functionName: 'my-lambda',  // Avoid this
});

// ✅ GOOD - Let CDK generate unique names
new lambda.Function(this, 'MyFunction', {
  // No functionName specified - CDK generates: StackName-MyFunctionXXXXXX
});
```

**Rationale** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:75-79]()):
- **Reusable patterns**: Deploy same construct/pattern multiple times without conflicts
- **Parallel deployments**: Multiple stacks can deploy simultaneously in same region
- **Cleaner shared logic**: Patterns and shared code can initialize multiple times
- **Stack isolation**: Each stack gets uniquely identified resources automatically

**Security Best Practice**: For environment separation (dev/staging/prod), use separate AWS accounts rather than resource naming within a single account. Account-level isolation provides stronger security boundaries.

Sources: [README.md:89-105](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:71-97]()

### Lambda Function Constructs

**Principle**: Use specialized constructs for automatic bundling based on runtime.

```mermaid
graph LR
    subgraph "Lambda Construct Selection"
        Runtime{Lambda Runtime?}
        
        TypeScript["TypeScript/JavaScript"]
        Python["Python"]
        
        Runtime --> TypeScript
        Runtime --> Python
        
        subgraph "TypeScript Implementation"
            NodejsFunc["NodejsFunction<br/>from aws-cdk-lib/aws-lambda-nodejs"]
            TSFeatures["Features:<br/>- Auto bundling<br/>- Auto transpilation<br/>- Dependency management<br/>- No manual packaging"]
        end
        
        subgraph "Python Implementation"
            PythonFunc["PythonFunction<br/>from @aws-cdk/aws-lambda-python-alpha"]
            PyFeatures["Features:<br/>- Auto dependency handling<br/>- Auto packaging<br/>- Requirements.txt support<br/>- No manual bundling"]
        end
        
        TypeScript --> NodejsFunc
        NodejsFunc --> TSFeatures
        
        Python --> PythonFunc
        PythonFunc --> PyFeatures
    end
```

**TypeScript/JavaScript Pattern**:

From [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:104-111]():

```typescript
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';

new NodejsFunction(this, 'MyFunction', {
  entry: 'lambda/handler.ts',
  handler: 'handler',
  // Automatically handles bundling, dependencies, and transpilation
});
```

**Python Pattern**:

From [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:114-123]():

```typescript
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';

new PythonFunction(this, 'MyFunction', {
  entry: 'lambda',
  index: 'handler.py',
  handler: 'handler',
  // Automatically handles dependencies and packaging
});
```

**Benefits** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:126-130]()):
- Automatic bundling and dependency management
- Transpilation handled automatically
- No manual packaging required
- Consistent deployment patterns

Sources: [README.md:107-113](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:99-130]()

## Multi-Layer Validation Strategy

The plugin implements a three-layer validation approach for comprehensive quality assurance before deployment.

```mermaid
graph TB
    subgraph "Layer 1: Real-Time IDE Feedback"
        L1Install["npm install --save-dev cdk-nag"]
        L1Code["Add to CDK app:<br/>Aspects.of(app).add(new AwsSolutionsChecks())"]
        L1Optional["Optional: VS Code Extension<br/>cdk-nag-validator"]
        L1Timing["Timing: File save / Synthesis"]
        
        L1Install --> L1Code
        L1Code --> L1Optional
        L1Code --> L1Timing
    end
    
    subgraph "Layer 2: Synthesis-Time Validation"
        L2Synth["cdk synth"]
        L2Nag["cdk-nag runs via Aspects<br/>AwsSolutionsChecks"]
        L2Suppress["NagSuppressions for exceptions<br/>with documented reasons"]
        L2Output["CloudFormation template<br/>+ validation results"]
        
        L2Synth --> L2Nag
        L2Nag --> L2Suppress
        L2Nag --> L2Output
    end
    
    subgraph "Layer 3: Pre-Commit Safety Net"
        L3Build["npm run build<br/>(compilation check)"]
        L3Test["npm test<br/>(unit + integration)"]
        L3Script["./scripts/validate-stack.sh<br/>(meta-level checks)"]
        
        L3Build --> L3Test
        L3Test --> L3Script
    end
    
    subgraph "Validation Script Checks"
        VSLang["Language Detection"]
        VSSize["Template Size Analysis"]
        VSResources["Resource Count Check"]
        VSSynth["Synthesis Success Verification"]
        
        L3Script --> VSLang
        L3Script --> VSSize
        L3Script --> VSResources
        L3Script --> VSSynth
    end
    
    L1Timing -->|Issues found| L2Synth
    L2Output -->|Ready for commit| L3Build
    L3Script -->|All checks pass| Deploy["Ready for Deployment"]
```

### Layer 1: Real-Time IDE Feedback

**Purpose**: Catch issues during development before synthesis.

**Implementation** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:136-154]()):

1. Install `cdk-nag` as dev dependency
2. Add to CDK app initialization:
   ```typescript
   import { Aspects } from 'aws-cdk-lib';
   import { AwsSolutionsChecks } from 'cdk-nag';
   
   const app = new App();
   Aspects.of(app).add(new AwsSolutionsChecks());
   ```
3. Optional: Install VS Code extension `cdk-nag-validator` for faster feedback on file save

**Supported Languages**: TypeScript, JavaScript, Python, Java, C#, Go (all CDK languages)

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:136-157]()

### Layer 2: Synthesis-Time Validation

**Purpose**: Comprehensive rule validation during template generation.

**Process** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:159-177]()):

1. **Run synthesis**: `cdk synth` (cdk-nag runs automatically via Aspects)
2. **Suppress legitimate exceptions** with documented reasons:
   ```typescript
   import { NagSuppressions } from 'cdk-nag';
   
   NagSuppressions.addResourceSuppressions(resource, [
     {
       id: 'AwsSolutions-L1',
       reason: 'Lambda@Edge requires specific runtime for CloudFront compatibility'
     }
   ]);
   ```

**Key Principle**: Document WHY each exception is needed, not just suppress warnings.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:159-177]()

### Layer 3: Pre-Commit Safety Net

**Purpose**: Meta-level checks and comprehensive validation before committing code.

**Commands** (from [README.md:116-124]() and [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:179-199]()):

```bash
npm run build  # Ensure compilation succeeds
npm test       # Run unit and integration tests
./scripts/validate-stack.sh  # Meta-level validation
```

**Validation Script Focus** (`scripts/validate-stack.sh`):
- Language detection (TypeScript/Python/etc.)
- Template size analysis (CloudFormation limits)
- Resource count verification
- Synthesis success confirmation
- Note: Detailed anti-pattern checks delegated to cdk-nag

**Integration**: When GitHub Actions workflows exist in `.github/workflows/`, ensure all CI checks pass before committing (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:293-295]()).

Sources: [README.md:115-124](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:179-199](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:293-296]()

## MCP Server Integration

The plugin integrates with two MCP server types for comprehensive AWS knowledge and CDK-specific guidance.

```mermaid
graph TB
    subgraph "MCP Server Ecosystem"
        subgraph "Plugin-Integrated: CDK MCP"
            CDKServer["awslabs.cdk-mcp-server@latest<br/>Protocol: stdio<br/>Launcher: uvx"]
            CDKTools["Tools:<br/>mcp__cdk__*"]
        end
        
        subgraph "Dependency: AWS Documentation MCP"
            DocsServer["aws-mcp or awsdocs<br/>(from aws-common plugin)"]
            DocsTools["Tools:<br/>mcp__aws-mcp__aws___search_documentation<br/>mcp__aws-mcp__aws___read_documentation<br/>mcp__aws-mcp__aws___get_regional_availability<br/>mcp__awsdocs__aws___search_documentation<br/>mcp__awsdocs__aws___read_documentation"]
        end
    end
    
    subgraph "Tool Permission Allowlist"
        AllowedMCP["allowed-tools in SKILL.md:<br/>- mcp__cdk__*<br/>- mcp__aws-mcp__*<br/>- mcp__awsdocs__*"]
        AllowedBash["allowed-tools in SKILL.md:<br/>- Bash(cdk *)<br/>- Bash(npm *)<br/>- Bash(npx *)<br/>- Bash(aws cloudformation *)<br/>- Bash(aws sts get-caller-identity)"]
    end
    
    subgraph "Skill Execution Flow"
        SkillInvoke["aws-cdk-development invoked"]
        CheckMCP["Check MCP tools available"]
        UseMCP["Use MCP servers"]
        GuideMCP["Guide user to aws-mcp-setup"]
        
        SkillInvoke --> CheckMCP
        CheckMCP -->|Available| UseMCP
        CheckMCP -->|Not Available| GuideMCP
    end
    
    CDKServer --> CDKTools
    DocsServer --> DocsTools
    CDKTools --> AllowedMCP
    DocsTools --> AllowedMCP
    AllowedMCP --> UseMCP
    AllowedBash --> UseMCP
    
    GuideMCP -.auto-loads.-> DocsServer
```

### CDK MCP Server

**Configuration**: Automatically configured with the plugin (no manual setup required).

**Server Details**:
- **Package**: `awslabs.cdk-mcp-server@latest`
- **Protocol**: stdio
- **Launcher**: `uvx`
- **Tool Pattern**: `mcp__cdk__*`

**Capabilities** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:48-57]()):
- Get CDK construct recommendations
- Retrieve CDK best practices
- Access CDK pattern suggestions
- Validate CDK configurations
- Get help with CDK-specific APIs

**When to Use** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:250-264]()):
- CDK construct selection and usage
- CDK API parameter options
- CDK best practice patterns
- Construct property configurations
- CDK-specific optimizations

**Example Scenarios**:
- "What's the recommended CDK construct for API Gateway REST API?"
- "How to configure NodejsFunction bundling options?"
- "Best practices for CDK stack organization"
- "CDK construct for DynamoDB with auto-scaling"

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:45-57](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:250-264]()

### AWS Documentation MCP (Dependency)

**Source**: Inherited from `aws-common` plugin via `skills: [aws-mcp-setup]` dependency.

**Tool Naming Patterns**:
- `mcp__aws-mcp__aws___search_documentation`
- `mcp__aws-mcp__aws___read_documentation`
- `mcp__aws-mcp__aws___get_regional_availability`
- `mcp__awsdocs__aws___search_documentation`
- `mcp__awsdocs__aws___read_documentation`

**When to Use** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:235-248]()):
- New AWS service features or configurations
- Service availability in target regions
- API parameter specifications
- Service limits and quotas
- Security best practices for AWS services

**Example Scenarios**:
- "Check if Lambda supports Python 3.13 runtime"
- "Verify DynamoDB is available in eu-south-2"
- "What are the current Lambda timeout limits?"
- "Get latest S3 encryption options"

**Critical Requirement** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:27-43]()):

The skill REQUIRES AWS MCP tools for accurate information. Before answering AWS questions:

1. **Verify** using AWS MCP tools if available
2. **If unavailable**: Guide user to `aws-mcp-setup` skill (auto-loaded as dependency)
3. **Setup options**:
   - Has uvx + AWS credentials → Full AWS MCP Server
   - No Python/credentials → AWS Documentation MCP (no auth)

This ensures no skill provides outdated AWS information.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:27-43](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:235-248]()

### MCP Usage Best Practices

From [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:265-272]():

1. **Verify First**: Always check AWS Documentation MCP before implementing new features
2. **Regional Validation**: Check service availability in target deployment regions
3. **CDK Guidance**: Use CDK MCP for construct-specific recommendations
4. **Stay Current**: MCP servers provide latest information beyond knowledge cutoff
5. **Combine Sources**: Use both skill patterns and MCP servers for comprehensive guidance

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:265-272]()

## CDK Patterns and References

The plugin provides a comprehensive pattern library through `references/cdk-patterns.md`.

**File Location**: `plugins/aws-cdk/skills/aws-cdk-development/references/cdk-patterns.md`

**Content Coverage** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:273-285]()):
- Common CDK patterns and their use cases
- Anti-patterns to avoid
- Security best practices
- Cost optimization strategies
- Performance considerations

**Reference from Skill**: The skill explicitly directs users to this file for detailed architectural guidance beyond the core principles covered in `SKILL.md`.

**Related Files**:
- `scripts/validate-stack.sh` - Pre-deployment validation script
- `SKILL.md` - Core skill definition and guidance

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:273-291]()

## Workflow Integration

### Development Workflow

The skill prescribes a structured development process (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:202-218]()):

```mermaid
graph TB
    Design["1. Design<br/>Plan infrastructure resources"]
    Verify["2. Verify AWS Services<br/>Use AWS Documentation MCP"]
    Implement["3. Implement<br/>Write CDK constructs"]
    Validate["4. Validate<br/>Run pre-deployment checks"]
    Synthesize["5. Synthesize<br/>cdk synth"]
    Review["6. Review<br/>Examine templates"]
    Deploy["7. Deploy<br/>cdk deploy"]
    VerifyDeploy["8. Verify<br/>Confirm resources"]
    
    Design --> Verify
    
    subgraph "Verify Phase Details"
        CheckRegion["Check regional availability"]
        CheckLimits["Verify service limits/quotas"]
        CheckAPI["Confirm latest API specs"]
    end
    
    Verify --> CheckRegion
    Verify --> CheckLimits
    Verify --> CheckAPI
    
    CheckAPI --> Implement
    
    subgraph "Implement Phase Details"
        UseCDKMCP["Use CDK MCP for recommendations"]
        RefBestPractices["Reference best practices via MCP"]
    end
    
    Implement --> UseCDKMCP
    Implement --> RefBestPractices
    
    RefBestPractices --> Validate
    Validate --> Synthesize
    Synthesize --> Review
    Review --> Deploy
    Deploy --> VerifyDeploy
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:202-218]()

### Pre-Deployment Hook

The skill implements a critical safety mechanism through the `PreToolUse` hook.

**Hook Configuration** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21]()):

```yaml
hooks:
  PreToolUse:
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```

**Behavior**:
- **Trigger**: Before any `cdk deploy*` command executes
- **Action**: Runs `aws sts get-caller-identity` to verify AWS account context
- **Frequency**: Once per session (`once: true`)
- **Purpose**: Prevents accidental cross-account deployments

This hook demonstrates the lifecycle mechanism available in skill frontmatter for enforcing safety checks.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21]()

### Stack Organization and Testing

**Stack Organization** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:219-225]()):
- Use nested stacks for complex applications
- Separate concerns into logical construct boundaries
- Export values that other stacks may need
- Use CDK context for environment-specific configuration

**Testing Strategy** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:227-232]()):
- Unit test individual constructs
- Integration test stack synthesis
- Snapshot test CloudFormation templates
- Validate resource properties and relationships

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:219-232]()

## Tool Permissions and Bash Integration

The skill defines explicit tool permissions in its frontmatter, enabling both MCP server tools and specific bash commands.

**MCP Tool Permissions** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:7-10]()):
- `mcp__cdk__*` - All CDK MCP server tools
- `mcp__aws-mcp__*` - AWS Documentation MCP tools (full version)
- `mcp__awsdocs__*` - AWS Documentation MCP tools (alternative naming)

**Bash Command Permissions** (from [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:11-15]()):
- `Bash(cdk *)` - All CDK CLI commands
- `Bash(npm *)` - npm package management
- `Bash(npx *)` - npx command execution
- `Bash(aws cloudformation *)` - CloudFormation CLI commands
- `Bash(aws sts get-caller-identity)` - Account identity verification

This permission model ensures the skill can execute CDK workflows (build, synth, deploy) while maintaining security boundaries through explicit allowlisting.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:7-15]()

## Additional Resources and Files

**Build Artifacts** (from [.gitignore:34-37]()):
- `cdk.out/` - CDK synthesis output directory
- `cdk.context.json` - CDK context cache
- `.cdk.staging/` - Staging directory for assets

**Testing and Coverage** (from [.gitignore:67-70]()):
- `coverage/` - Test coverage reports
- `.nyc_output` - NYC (Istanbul) coverage data
- `.pytest_cache/` - Pytest cache for Python tests

**Ignored Files**: AWS credentials, environment variables, temporary files are explicitly excluded from version control to prevent accidental credential exposure.

Sources: [.gitignore:34-37](), [.gitignore:67-70](), [.gitignore:88-91]()

---

# Page: aws-cost-ops Plugin

# aws-cost-ops Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md](plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md)

</details>



The `aws-cost-ops` plugin provides AWS cost optimization, monitoring, and operational excellence capabilities for Claude Code. It integrates three AWS MCP servers (Pricing, Cost Explorer, CloudWatch) to enable pre-deployment cost estimation, post-deployment cost analysis, and comprehensive monitoring of AWS resources. This plugin is designed for post-deployment operational concerns including cost tracking, performance monitoring, observability, and audit analysis.

For infrastructure development and deployment, see [aws-cdk Plugin](#4.2). For foundational AWS MCP configuration, see [aws-common Plugin](#4.1).

## Overview

The `aws-cost-ops` plugin is categorized as an operations plugin (version 1.2.0) and provides a single skill named `aws-cost-operations`. Unlike development-focused plugins, this plugin emphasizes post-deployment operational concerns aligned with the AWS Well-Architected Framework's operational excellence and cost optimization pillars.

**Key Characteristics:**
- **Version**: 1.2.0
- **Category**: operations
- **MCP Server Count**: 3 (highest among all plugins)
- **Primary Skill**: `aws-cost-operations`
- **Dependencies**: `aws-common` plugin (for `aws-mcp-setup` skill)

Sources: [.claude-plugin/marketplace.json:63-111](), [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:1-23]()

## MCP Server Architecture

### Three-Server Integration Model

The `aws-cost-ops` plugin demonstrates the most comprehensive MCP server integration in the ecosystem, utilizing three distinct servers for specialized operational capabilities:

```mermaid
graph TB
    subgraph Plugin["aws-cost-ops Plugin v1.2.0"]
        Skill["aws-cost-operations skill<br/>SKILL.md"]
        ToolPerms["allowed-tools configuration"]
    end
    
    subgraph MCPServers["MCP Server Configuration"]
        PricingServer["pricing MCP server<br/>uvx awslabs.aws-pricing-mcp-server@latest"]
        CostExpServer["costexp MCP server<br/>uvx awslabs.cost-explorer-mcp-server@latest"]
        CWServer["cw MCP server<br/>uvx awslabs.cloudwatch-mcp-server@latest"]
    end
    
    subgraph ToolNamespace["MCP Tool Naming Pattern"]
        PricingTools["mcp__pricing__*"]
        CostExpTools["mcp__costexp__*"]
        CWTools["mcp__cw__*"]
        AWSTools["mcp__aws-mcp__*<br/>mcp__awsdocs__*"]
    end
    
    subgraph BashCommands["Bash Tool Permissions"]
        BashCE["Bash(aws ce *)"]
        BashCW["Bash(aws cloudwatch *)"]
        BashLogs["Bash(aws logs *)"]
        BashBudgets["Bash(aws budgets *)"]
        BashTrail["Bash(aws cloudtrail *)"]
        BashSTS["Bash(aws sts get-caller-identity)"]
    end
    
    subgraph AWSServices["AWS Service APIs"]
        PricingAPI["AWS Pricing API"]
        CostExplorerAPI["AWS Cost Explorer API"]
        CloudWatchAPI["CloudWatch API<br/>Metrics, Alarms, Logs"]
    end
    
    Skill --> ToolPerms
    ToolPerms --> PricingTools
    ToolPerms --> CostExpTools
    ToolPerms --> CWTools
    ToolPerms --> AWSTools
    ToolPerms --> BashCE
    ToolPerms --> BashCW
    ToolPerms --> BashLogs
    ToolPerms --> BashBudgets
    ToolPerms --> BashTrail
    ToolPerms --> BashSTS
    
    PricingServer --> PricingTools
    CostExpServer --> CostExpTools
    CWServer --> CWTools
    
    PricingServer --> PricingAPI
    CostExpServer --> CostExplorerAPI
    CWServer --> CloudWatchAPI
    
    BashCE --> CostExplorerAPI
    BashCW --> CloudWatchAPI
    BashLogs --> CloudWatchAPI
```

**MCP Server Configuration and Tool Namespace Mapping**

Sources: [.claude-plugin/marketplace.json:80-111](), [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-17]()

### Server Configuration Details

Each MCP server follows a consistent configuration pattern defined in the plugin's marketplace entry:

| Server Name | Package | Tool Pattern | Purpose |
|------------|---------|--------------|---------|
| `pricing` | `awslabs.aws-pricing-mcp-server@latest` | `mcp__pricing__*` | Pre-deployment cost estimation |
| `costexp` | `awslabs.cost-explorer-mcp-server@latest` | `mcp__costexp__*` | Post-deployment cost analysis |
| `cw` | `awslabs.cloudwatch-mcp-server@latest` | `mcp__cw__*` | Metrics, alarms, and log analysis |

**Common Configuration Parameters:**
- **Type**: `stdio` (standard input/output protocol)
- **Command**: `uvx` (UV package runner)
- **Environment**: `FASTMCP_LOG_LEVEL=ERROR` (minimal logging)

Sources: [.claude-plugin/marketplace.json:81-110]()

## Skill Structure and Configuration

### aws-cost-operations Skill

The plugin provides a single comprehensive skill located at [plugins/aws-cost-ops/skills/aws-cost-operations/]().

```mermaid
graph TB
    subgraph SkillDefinition["aws-cost-operations Skill Structure"]
        SKILL["SKILL.md<br/>Frontmatter + Content"]
        References["references/ directory"]
        OpsPatterns["operations-patterns.md"]
        CWAlarms["cloudwatch-alarms.md"]
    end
    
    subgraph Frontmatter["SKILL.md Frontmatter Configuration"]
        Name["name: aws-cost-operations"]
        Description["description: Cost optimization<br/>and operational best practices"]
        SkillDeps["skills: [aws-mcp-setup]"]
        AllowedTools["allowed-tools:<br/>mcp__pricing__*<br/>mcp__costexp__*<br/>mcp__cw__*<br/>Bash(aws ce *)<br/>Bash(aws cloudwatch *)<br/>..."]
        Hooks["hooks:<br/>PreToolUse:<br/>matcher: Bash(aws ce *)<br/>command: aws sts get-caller-identity<br/>once: true"]
    end
    
    subgraph Execution["Execution Behavior"]
        AutoLoad["Auto-load aws-mcp-setup skill"]
        VerifyTools["Verify MCP tools available"]
        PreHook["Execute PreToolUse hook<br/>before cost commands"]
        MCPCalls["Execute MCP tool calls"]
    end
    
    SKILL --> Name
    SKILL --> Description
    SKILL --> SkillDeps
    SKILL --> AllowedTools
    SKILL --> Hooks
    SKILL --> References
    
    References --> OpsPatterns
    References --> CWAlarms
    
    SkillDeps --> AutoLoad
    AutoLoad --> VerifyTools
    Hooks --> PreHook
    AllowedTools --> MCPCalls
```

**Skill Definition and Execution Flow**

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:1-23]()

### Frontmatter Configuration

The skill's frontmatter defines critical execution parameters:

**Dependency Management:**
```yaml
skills:
  - aws-mcp-setup
```
This creates an auto-loading dependency on the `aws-mcp-setup` skill from the `aws-common` plugin, ensuring MCP tools are configured before any cost operations are performed.

**Tool Permissions:**
```yaml
allowed-tools:
  - mcp__pricing__*
  - mcp__costexp__*
  - mcp__cw__*
  - mcp__aws-mcp__*
  - mcp__awsdocs__*
  - Bash(aws ce *)
  - Bash(aws cloudwatch *)
  - Bash(aws logs *)
  - Bash(aws budgets *)
  - Bash(aws cloudtrail *)
  - Bash(aws sts get-caller-identity)
```
The wildcard patterns (`*`) allow access to all tools provided by each MCP server, while specific Bash commands enable direct AWS CLI access for operations not covered by MCP servers.

**PreToolUse Hook:**
```yaml
hooks:
  PreToolUse:
    - matcher: Bash(aws ce *)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```
This hook ensures account context verification before executing Cost Explorer commands, preventing accidental cross-account operations. The `once: true` flag ensures the verification runs only once per session.

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:1-23]()

### Reference Documentation

The skill includes two reference documents located in the `references/` directory:

| File | Purpose | Content |
|------|---------|---------|
| `operations-patterns.md` | Operational patterns | Cost optimization strategies, monitoring patterns, observability best practices |
| `cloudwatch-alarms.md` | Alarm configurations | Common alarm configurations for Lambda, EC2, RDS, DynamoDB, API Gateway, ECS, ALB |

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:314-337]()

## Operational Capabilities

### Cost Management

The plugin provides three-phase cost management through its MCP servers:

```mermaid
graph LR
    subgraph PreDeployment["Pre-Deployment Phase"]
        Estimate["Cost Estimation<br/>pricing MCP server"]
        Compare["Compare regions<br/>Compare options"]
        Calculate["Calculate TCO"]
    end
    
    subgraph PostDeployment["Post-Deployment Phase"]
        Track["Track Actual Spending<br/>Cost Explorer MCP"]
        Monitor["Monitor Budget<br/>costexp MCP server"]
        Alert["Budget Alerts"]
    end
    
    subgraph Analysis["Analysis Phase"]
        Trends["Analyze Trends<br/>costexp MCP server"]
        Anomalies["Identify Anomalies"]
        Recommendations["Generate Recommendations"]
        Optimize["Implement Optimizations"]
    end
    
    Estimate --> Compare
    Compare --> Calculate
    Calculate --> Track
    
    Track --> Monitor
    Monitor --> Alert
    Alert --> Trends
    
    Trends --> Anomalies
    Anomalies --> Recommendations
    Recommendations --> Optimize
    Optimize --> Estimate
```

**Cost Management Workflow Through MCP Servers**

**Pre-Deployment Estimation:**
The `pricing` MCP server enables cost estimation before resources are deployed:
- Query current AWS service pricing
- Compare costs across regions
- Calculate Total Cost of Ownership (TCO)
- Evaluate alternative service configurations

**Post-Deployment Tracking:**
The `costexp` MCP server provides real-time cost tracking:
- Monitor actual spending vs. estimates
- Track budget utilization
- Set up cost allocation tags
- Review consolidated billing for organizations

**Analysis and Optimization:**
The `costexp` MCP server enables detailed analysis:
- Analyze historical spending patterns
- Identify cost anomalies and unexpected charges
- Forecast future costs
- Generate cost optimization recommendations

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:139-169]()

### Monitoring and Observability

The `cw` MCP server provides comprehensive CloudWatch integration:

**Metrics and Alarms:**
- Query CloudWatch metrics for resource utilization
- Create and manage CloudWatch alarms for threshold monitoring
- Set up custom dashboards for visualization
- Monitor critical metrics (CPU, memory, errors, latency)

**Log Analysis:**
- Query CloudWatch Logs for troubleshooting
- Use CloudWatch Logs Insights for complex queries
- Track application errors and warnings
- Analyze log patterns for operational issues

**Common Alarm Scenarios:**
| Resource Type | Metric | Threshold Example |
|--------------|--------|-------------------|
| Lambda | Error rate | > 1% |
| EC2 | CPU utilization | > 80% |
| API Gateway | 4xx/5xx errors | Spike detection |
| DynamoDB | Throttled requests | > 0 |
| ECS | Task failures | > 0 |

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:182-219]()

### Audit and Security

While the marketplace configuration defines three MCP servers, the skill documentation mentions additional capabilities:

**CloudTrail Activity Analysis:**
The skill supports AWS CloudTrail analysis through Bash commands:
- Track API activity and resource changes
- Investigate security incidents
- Audit compliance with policies
- Monitor for suspicious activity patterns

**Security Assessment:**
The skill references Well-Architected Security Assessment capabilities:
- Assess security posture against AWS best practices
- Identify security gaps and vulnerabilities
- Review security pillar compliance
- Generate security assessment reports

**Note:** The marketplace configuration [.claude-plugin/marketplace.json:80-111]() defines only three MCP servers (pricing, costexp, cw), but the skill documentation [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:49-122]() mentions eight MCP servers total. The additional servers (CloudTrail, Well-Architected Security, etc.) may be accessed through the `aws-mcp` or `awsdocs` tool patterns allowed in the skill configuration.

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:221-253](), [.claude-plugin/marketplace.json:80-111]()

## Integration with Other Plugins

### Dependency on aws-common

The `aws-cost-operations` skill declares a dependency on `aws-mcp-setup`:

```mermaid
graph TB
    subgraph User["User Interaction"]
        InvokeSkill["Invoke aws-cost-operations skill"]
    end
    
    subgraph SkillLoading["Skill Dependency Resolution"]
        CostOps["aws-cost-operations skill"]
        MCPSetup["aws-mcp-setup skill<br/>(auto-loaded)"]
    end
    
    subgraph MCPVerification["MCP Tool Availability Check"]
        CheckTools{"MCP Tools<br/>Available?"}
        GuideSetup["Guide user through<br/>AWS MCP setup"]
        UseTools["Proceed with<br/>MCP tool calls"]
    end
    
    subgraph MCPServers["MCP Servers"]
        Pricing["pricing server"]
        CostExp["costexp server"]
        CW["cw server"]
    end
    
    InvokeSkill --> CostOps
    CostOps --> MCPSetup
    MCPSetup --> CheckTools
    
    CheckTools -->|No| GuideSetup
    CheckTools -->|Yes| UseTools
    
    GuideSetup --> UseTools
    
    UseTools --> Pricing
    UseTools --> CostExp
    UseTools --> CW
```

**Skill Dependency and MCP Tool Verification Flow**

This dependency ensures that:
1. MCP tools are configured before answering AWS questions
2. Users are guided through MCP setup if tools are unavailable
3. The skill never provides outdated AWS information

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:4-5](), [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:29-45]()

### Tool Permission Model

The skill's `allowed-tools` configuration defines a comprehensive permission model:

| Tool Pattern | Purpose | Examples |
|-------------|---------|----------|
| `mcp__pricing__*` | Access all pricing MCP tools | Cost estimation, regional pricing comparison |
| `mcp__costexp__*` | Access all Cost Explorer tools | Spending analysis, anomaly detection, forecasting |
| `mcp__cw__*` | Access all CloudWatch tools | Metrics queries, alarm management, log analysis |
| `mcp__aws-mcp__*` | Access AWS Documentation MCP | Documentation search, regional availability checks |
| `mcp__awsdocs__*` | Alternative AWS docs pattern | Same as aws-mcp, different naming convention |
| `Bash(aws ce *)` | Direct Cost Explorer CLI access | Commands not covered by MCP server |
| `Bash(aws cloudwatch *)` | Direct CloudWatch CLI access | Advanced CloudWatch operations |
| `Bash(aws logs *)` | CloudWatch Logs CLI access | Log group/stream management |
| `Bash(aws budgets *)` | AWS Budgets CLI access | Budget creation and management |
| `Bash(aws cloudtrail *)` | CloudTrail CLI access | Audit log queries |
| `Bash(aws sts get-caller-identity)` | Account verification | Used by PreToolUse hook |

This dual-mode access (MCP tools + Bash CLI) provides flexibility: MCP servers offer simplified, aggregated interfaces for common operations, while Bash commands enable direct AWS CLI access for advanced or edge-case scenarios.

Sources: [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:6-17]()

## Usage Patterns

### Cost Estimation Workflow

**Example: Pre-Deployment Cost Estimation**

1. User invokes skill: "Estimate the monthly cost of running 10 Lambda functions with 1M invocations each"
2. Skill auto-loads `aws-mcp-setup` dependency
3. MCP tool availability verified
4. Skill uses `mcp__pricing__*` tools to query AWS Pricing API
5. Results returned with cost breakdown by service and region

### Cost Analysis Workflow

**Example: Post-Deployment Cost Review**

1. User invokes skill: "Show me my AWS costs for the last 30 days broken down by service"
2. PreToolUse hook executes (if using `Bash(aws ce *)` commands): `aws sts get-caller-identity`
3. Account context verified
4. Skill uses `mcp__costexp__*` tools to query Cost Explorer API
5. Results returned with spending trends and anomaly detection

### Monitoring Workflow

**Example: CloudWatch Alarm Setup**

1. User invokes skill: "Create CloudWatch alarms for my Lambda functions to alert on errors and high duration"
2. Skill uses `mcp__cw__*` tools to:
   - List Lambda functions in the account
   - Retrieve current error rates and duration metrics
   - Create alarms with appropriate thresholds
3. Alarms configured with SNS notifications

Sources: [README.md:144-183]()

## Version Management

The `aws-cost-ops` plugin follows the version management strategy outlined in section [5.2](#5.2):

**Current Version**: 1.2.0

**Version Bump Triggers:**
- **Minor (1.Y.0)**: New MCP server integration, new skill, new dependency, structural changes
- **Patch (1.2.Z)**: Bug fixes, documentation updates, configuration tweaks, typo fixes

The plugin is currently at v1.2.0, indicating it has undergone at least two minor version increments since initial release (assumed 1.0.0). The `aws-common` plugin remains at v1.0.0, reflecting its role as a stable foundation.

Sources: [.claude-plugin/marketplace.json:65]()

## File Structure

```
plugins/aws-cost-ops/
├── skills/
│   └── aws-cost-operations/
│       ├── SKILL.md                      # Skill definition with frontmatter
│       └── references/
│           ├── operations-patterns.md    # Operational best practices
│           └── cloudwatch-alarms.md      # Alarm configurations
```

**Key Files:**
- **SKILL.md**: Contains frontmatter configuration (name, description, dependencies, allowed-tools, hooks) and skill guidance content
- **operations-patterns.md**: Comprehensive reference for cost optimization, monitoring, observability, and security patterns
- **cloudwatch-alarms.md**: Pre-configured alarm templates for common AWS services

Sources: [README.md:227-250](), [plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md:314-337]()

## Installation

The `aws-cost-ops` plugin requires the `aws-common` plugin as a dependency:

```bash
# 1. Add marketplace (if not already added)
/plugin marketplace add zxkane/aws-skills

# 2. Install aws-common first (required dependency)
/plugin install aws-common@aws-skills

# 3. Install aws-cost-ops
/plugin install aws-cost-ops@aws-skills
```

Upon installation, the three MCP servers (pricing, costexp, cw) are automatically configured and launched via `uvx` when the skill is invoked.

For detailed installation instructions and MCP setup, see [Installation](#2.1) and [MCP Setup](#2.2).

Sources: [README.md:68-87]()

---

# Page: serverless-eda Plugin

# serverless-eda Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md](plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md)

</details>



## Purpose and Scope

This document covers the **serverless-eda plugin** (version 1.2.0), which provides comprehensive guidance for building serverless applications and event-driven architectures on AWS based on the Well-Architected Framework. The plugin includes seven design principles for serverless applications and five event-driven architecture patterns.

For CDK infrastructure implementation details, see [aws-cdk Plugin](#4.2). For AWS MCP setup and foundational capabilities, see [aws-common Plugin](#4.1). For operational concerns like cost and monitoring, see [aws-cost-ops Plugin](#4.3).

**Sources:** [.claude-plugin/marketplace.json:113-130](), [README.md:44-53]()

## Overview

The serverless-eda plugin is a **pattern-based** plugin that provides architectural guidance without dedicated MCP servers. It differs from other plugins in the marketplace by focusing on design principles and reference patterns rather than tool integrations.

| Property | Value |
|----------|-------|
| Plugin Name | `serverless-eda` |
| Version | `1.2.0` |
| Category | `development` |
| Source Path | `./plugins/serverless-eda` |
| Primary Skill | `aws-serverless-eda` |
| MCP Servers | **0** (pattern-based approach) |
| Dependencies | `aws-mcp-setup`, `aws-cdk-development` |
| Keywords | `aws`, `serverless`, `lambda`, `event-driven`, `eda`, `step-functions`, `eventbridge`, `sqs`, `sns` |

**Key Characteristics:**
- **No dedicated MCP servers**: Unlike `aws-cost-ops` (3 servers) or `aws-cdk` (1 server), this plugin operates purely on guidance patterns
- **Dual dependency**: Requires both `aws-mcp-setup` and `aws-cdk-development` to leverage documentation and infrastructure capabilities
- **Comprehensive coverage**: Spans Lambda, API Gateway, DynamoDB, Step Functions, EventBridge, SQS, SNS, and Kinesis
- **Well-Architected alignment**: All guidance derives from AWS Well-Architected Serverless Lens

**Sources:** [.claude-plugin/marketplace.json:113-130](), [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:1-27]()

## Plugin Architecture and Dependencies

```mermaid
graph TB
    subgraph "serverless-eda Plugin Structure"
        Plugin["serverless-eda Plugin<br/>v1.2.0<br/>No MCP Servers"]
        Skill["aws-serverless-eda skill<br/>SKILL.md + References"]
        
        Plugin --> Skill
    end
    
    subgraph "Skill Configuration"
        Meta["name: aws-serverless-eda<br/>context: fork<br/>model: (default)"]
        Deps["skills:<br/>- aws-mcp-setup<br/>- aws-cdk-development"]
        Tools["allowed-tools:<br/>- mcp__aws-mcp__*<br/>- mcp__awsdocs__*<br/>- mcp__cdk__*<br/>- Bash(sam *)<br/>- Bash(aws lambda *)<br/>- Bash(aws stepfunctions *)<br/>- Bash(aws events *)<br/>- Bash(aws sqs *)<br/>- Bash(aws sns *)"]
        Hooks["PreToolUse:<br/>Bash(sam deploy*)<br/>→ aws sts get-caller-identity<br/>once: true"]
        
        Skill --> Meta
        Skill --> Deps
        Skill --> Tools
        Skill --> Hooks
    end
    
    subgraph "Dependency Resolution"
        Common["aws-mcp-setup skill<br/>(aws-common plugin)<br/>AWS Documentation MCP"]
        CDK["aws-cdk-development skill<br/>(aws-cdk plugin)<br/>CDK MCP + Patterns"]
        
        Deps -.auto-loads.-> Common
        Deps -.auto-loads.-> CDK
    end
    
    subgraph "Transitive MCP Access"
        AWSDocs["mcp__aws-mcp__aws___*<br/>mcp__awsdocs__aws___*<br/>Documentation Search/Read"]
        CDKTools["mcp__cdk__*<br/>CDK Recommendations"]
        
        Common --> AWSDocs
        CDK --> CDKTools
    end
    
    subgraph "Reference Documentation"
        Refs["references/<br/>- serverless-patterns.md<br/>- eda-patterns.md<br/>- security-best-practices.md<br/>- observability-best-practices.md<br/>- performance-optimization.md<br/>- deployment-best-practices.md"]
        
        Skill --> Refs
    end
    
    Tools --> AWSDocs
    Tools --> CDKTools
```

**Architecture Notes:**

1. **Zero MCP Servers**: The plugin registers no MCP servers in `marketplace.json`, distinguishing it from `aws-cdk` (1 server) and `aws-cost-ops` (3 servers)
2. **Skill Auto-Loading**: Invoking `aws-serverless-eda` automatically loads `aws-mcp-setup` and `aws-cdk-development`, creating a three-skill execution context
3. **Transitive Tool Access**: Through dependencies, gains access to AWS Documentation MCP and CDK MCP without declaring its own servers
4. **Fork Context**: Executes in isolated sub-agent with full tool permissions inherited from skill configuration
5. **Hook Validation**: Before any `sam deploy*` command, automatically verifies AWS account context using `aws sts get-caller-identity` (once per session)

**Sources:** [.claude-plugin/marketplace.json:113-130](), [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:1-27]()

## When to Use This Skill

The `aws-serverless-eda` skill is invoked automatically by Claude Code when user prompts contain specific keywords or architectural patterns:

| Trigger Category | Keywords/Patterns |
|------------------|-------------------|
| **Serverless Basics** | `serverless`, `Lambda`, `Lambda function`, `API Gateway`, `REST API`, `HTTP API` |
| **Event-Driven** | `event-driven`, `EventBridge`, `SQS`, `SNS`, `async processing`, `queues`, `pub/sub` |
| **Orchestration** | `Step Functions`, `state machine`, `workflow`, `saga pattern`, `distributed transaction` |
| **Data Processing** | `Kinesis`, `stream processing`, `DynamoDB Streams`, `event sourcing` |
| **Microservices** | `microservices`, `API-driven`, `service mesh`, `async communication` |
| **Architecture** | "build scalable serverless", "design event-driven system", "implement saga" |

**Skill Selection Logic** (from description in [SKILL.md:3]()):
> Use when building serverless APIs, Lambda functions, REST APIs, microservices, or async workflows. Essential when user mentions serverless, Lambda, API Gateway, event-driven, async processing, queues, pub/sub, or wants to build scalable serverless applications with AWS best practices.

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:1-97]()

## Seven Well-Architected Design Principles

The plugin enforces seven core design principles from the AWS Well-Architected Serverless Lens. Each principle maps to specific code patterns:

```mermaid
graph TB
    subgraph "Principle 1: Speedy, Simple, Singular"
        P1["Single-purpose functions<br/>Minimize cold starts<br/>Optimize memory"]
        P1Code["Code Pattern:<br/>export const processOrder<br/>export const validateOrder<br/>export const publishEvent"]
        P1 --> P1Code
    end
    
    subgraph "Principle 2: Think Concurrent Requests"
        P2["Design for concurrency<br/>Not total volume<br/>Control throttling"]
        P2Code["Code Pattern:<br/>table.autoScaleReadCapacity()<br/>table.autoScaleWriteCapacity()<br/>reservedConcurrentExecutions"]
        P2 --> P2Code
    end
    
    subgraph "Principle 3: Share Nothing"
        P3["No local state<br/>Use persistent storage<br/>Stateless functions"]
        P3Code["Code Pattern:<br/>s3.putObject()<br/>dynamodb.putItem()<br/>elasticache.set()"]
        P3 --> P3Code
    end
    
    subgraph "Principle 4: Assume No Hardware Affinity"
        P4["Hardware-agnostic<br/>Environment variables<br/>Portable design"]
        P4Code["Code Pattern:<br/>process.env.BUCKET_NAME<br/>process.env.TABLE_NAME<br/>process.env.QUEUE_URL"]
        P4 --> P4Code
    end
    
    subgraph "Principle 5: Orchestrate with State Machines"
        P5["Use Step Functions<br/>Not function chaining<br/>Visual workflows"]
        P5Code["Code Pattern:<br/>stepfunctions.StateMachine<br/>stepfunctions.Chain.start()<br/>tasks.LambdaInvoke"]
        P5 --> P5Code
    end
    
    subgraph "Principle 6: Use Events to Trigger"
        P6["Event-driven<br/>Not synchronous<br/>Loose coupling"]
        P6Code["Code Pattern:<br/>s3.addEventNotification<br/>events.Rule<br/>eventPattern"]
        P6 --> P6Code
    end
    
    subgraph "Principle 7: Design for Failures"
        P7["Idempotent operations<br/>Retry logic<br/>Exponential backoff"]
        P7Code["Code Pattern:<br/>dynamodb.getItem(orderId)<br/>await withRetry(fn)<br/>reportBatchItemFailures"]
        P7 --> P7Code
    end
```

### Principle 1: Speedy, Simple, Singular

**Concept**: Functions should be concise, single-purpose, and environmentally efficient.

**Code Implementation** [SKILL.md:104-119]():
- ✅ **Good**: `export const processOrder = async (event: OrderEvent)` - single responsibility
- ❌ **Bad**: `export const handleEverything = async (event: any)` - multiple concerns

**Optimization Checklist**:
- Minimize cold start times
- Optimize memory allocation (128MB-10GB range)
- Use provisioned concurrency only when needed
- Leverage connection reuse (database pools)

### Principle 2: Think Concurrent Requests, Not Total Requests

**Concept**: Lambda scales horizontally; design for concurrent execution limits, not total volume.

**Code Implementation** [SKILL.md:137-152]():
```typescript
// Auto-scales with concurrent load
const table = new dynamodb.Table(this, 'Table', {
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
});

// Or with auto-scaling
table.autoScaleReadCapacity({ minCapacity: 5, maxCapacity: 100 });
table.autoScaleWriteCapacity({ minCapacity: 5, maxCapacity: 100 });
```

**Design Considerations**:
- Concurrent execution limits (account-level, function-level)
- Downstream service throttling (DynamoDB, RDS)
- Shared resource contention (VPC ENIs)
- Connection pool sizing (database connections)

### Principle 3: Share Nothing

**Concept**: Function runtime environments are ephemeral; state must be externalized.

**Code Implementation** [SKILL.md:159-179]():
- ❌ **Bad**: `fs.writeFileSync('/tmp/data.json')` - lost after execution
- ✅ **Good**: `s3.putObject({ Bucket, Key, Body })` - persistent storage

**State Management Options**:
- **DynamoDB**: Persistent application state
- **Step Functions**: Workflow state and orchestration
- **ElastiCache**: Session state and caching
- **S3**: File storage and archives

### Principle 4: Assume No Hardware Affinity

**Concept**: Applications must be hardware-agnostic; infrastructure can change without notice.

**Design Pattern** [SKILL.md:181-194]():
- Use environment variables for configuration
- Avoid hardware-specific optimizations
- Test across different environments
- No assumptions about underlying infrastructure

### Principle 5: Orchestrate with State Machines, Not Function Chaining

**Concept**: Use Step Functions for orchestration instead of Lambda-to-Lambda invocations.

**Code Comparison** [SKILL.md:199-225]():

❌ **Anti-Pattern**: Lambda chaining
```typescript
export const handler1 = async (event: any) => {
  const result = await processStep1(event);
  await lambda.invoke({
    FunctionName: 'handler2',
    Payload: JSON.stringify(result),
  });
};
```

✅ **Best Practice**: Step Functions orchestration
```typescript
const stateMachine = new stepfunctions.StateMachine(this, 'OrderWorkflow', {
  definition: stepfunctions.Chain
    .start(validateOrder)
    .next(processPayment)
    .next(shipOrder)
    .next(sendConfirmation),
});
```

**Step Functions Benefits**:
- Visual workflow representation
- Built-in error handling and retries
- Execution history and debugging
- Parallel and sequential execution
- Service integrations without code

### Principle 6: Use Events to Trigger Transactions

**Concept**: Favor event-driven patterns over synchronous request/response.

**Code Implementation** [SKILL.md:231-255]():

**S3 Event Notification**:
```typescript
bucket.addEventNotification(
  s3.EventType.OBJECT_CREATED,
  new s3n.LambdaDestination(processFunction),
  { prefix: 'uploads/' }
);
```

**EventBridge Integration**:
```typescript
const rule = new events.Rule(this, 'OrderRule', {
  eventPattern: {
    source: ['orders'],
    detailType: ['OrderPlaced'],
  },
});
rule.addTarget(new targets.LambdaFunction(processOrderFunction));
```

**Benefits**: Loose coupling, asynchronous processing, fault tolerance, independent scaling

### Principle 7: Design for Failures and Duplicates

**Concept**: Operations must be idempotent with retry logic and exponential backoff.

**Idempotency Pattern** [SKILL.md:262-302]():
```typescript
export const handler = async (event: SQSEvent) => {
  for (const record of event.Records) {
    const orderId = JSON.parse(record.body).orderId;
    
    // Check if already processed (idempotency)
    const existing = await dynamodb.getItem({
      TableName: process.env.TABLE_NAME,
      Key: { orderId },
    });
    
    if (existing.Item) {
      console.log('Order already processed:', orderId);
      continue; // Skip duplicate
    }
    
    await processOrder(orderId);
    await dynamodb.putItem({ /* mark as processed */ });
  }
};
```

**Retry with Exponential Backoff** [SKILL.md:291-302]():
```typescript
async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:98-304]()

## Five Event-Driven Architecture Patterns

The plugin provides five canonical EDA patterns that map directly to AWS services:

```mermaid
graph TB
    subgraph "Pattern 1: Event Router"
        ER["EventBridge Custom Bus<br/>events.EventBus<br/>events.Rule<br/>eventPattern matching"]
        ER1["Use Case:<br/>Route events to multiple consumers<br/>Content-based routing<br/>Schema validation"]
    end
    
    subgraph "Pattern 2: Queue-Based Processing"
        QP["SQS Queue + Lambda Consumer<br/>sqs.Queue<br/>lambda.EventSourceMapping<br/>batchSize + maxBatchingWindow"]
        QP1["Use Case:<br/>At-least-once delivery<br/>Async processing<br/>Load leveling"]
    end
    
    subgraph "Pattern 3: Pub/Sub Fan-Out"
        PS["SNS Topic + SQS Subscriptions<br/>sns.Topic<br/>subscriptions.SqsSubscription<br/>Multiple consumers"]
        PS1["Use Case:<br/>Broadcast to multiple services<br/>Parallel processing<br/>Service decoupling"]
    end
    
    subgraph "Pattern 4: Saga Pattern"
        SP["Step Functions + Compensation<br/>stepfunctions.StateMachine<br/>tasks.LambdaInvoke<br/>addCatch(compensate)"]
        SP1["Use Case:<br/>Distributed transactions<br/>Long-running workflows<br/>Rollback on failure"]
    end
    
    subgraph "Pattern 5: Event Sourcing"
        ES["DynamoDB Event Store<br/>partitionKey: aggregateId<br/>sortKey: version<br/>stream: NEW_IMAGE"]
        ES1["Use Case:<br/>Audit trail<br/>Temporal queries<br/>Event replay"]
    end
    
    ER --> ER1
    QP --> QP1
    PS --> PS1
    SP --> SP1
    ES --> ES1
```

### Pattern 1: Event Router (EventBridge)

**Architecture**: Central event bus with content-based routing using EventBridge rules.

**Core Components** [SKILL.md:311-357]():

| Component | CDK Construct | Purpose |
|-----------|--------------|---------|
| Event Bus | `events.EventBus` | Custom namespace for events |
| Schema | `events.Schema` | Event contract definition |
| Rules | `events.Rule` | Pattern-based routing |
| Targets | `targets.LambdaFunction` | Event consumers |

**Implementation Example**:
```typescript
// Custom event bus
const eventBus = new events.EventBus(this, 'AppEventBus', {
  eventBusName: 'application-events',
});

// Multiple rules for different consumers
new events.Rule(this, 'ProcessOrderRule', {
  eventBus,
  eventPattern: {
    source: ['orders'],
    detailType: ['OrderPlaced'],
  },
  targets: [new targets.LambdaFunction(processOrderFunction)],
});

new events.Rule(this, 'NotifyCustomerRule', {
  eventBus,
  eventPattern: {
    source: ['orders'],
    detailType: ['OrderPlaced'],
  },
  targets: [new targets.LambdaFunction(notifyCustomerFunction)],
});
```

**Use Cases**: Microservices communication, event-driven workflows, service decoupling

### Pattern 2: Queue-Based Processing (SQS)

**Architecture**: SQS queues with Lambda consumers for reliable asynchronous processing.

**Queue Types** [SKILL.md:362-388]():

| Queue Type | Use Case | Code Pattern |
|------------|----------|--------------|
| **Standard** | At-least-once delivery, high throughput | `new sqs.Queue()` |
| **FIFO** | Exactly-once, ordered processing | `fifo: true, contentBasedDeduplication: true` |

**Implementation with DLQ** [SKILL.md:364-387]():
```typescript
// Standard queue with DLQ
const queue = new sqs.Queue(this, 'ProcessingQueue', {
  visibilityTimeout: Duration.seconds(300),
  retentionPeriod: Duration.days(14),
  deadLetterQueue: {
    queue: dlq,
    maxReceiveCount: 3,
  },
});

// Lambda consumer with batching
new lambda.EventSourceMapping(this, 'QueueConsumer', {
  target: processingFunction,
  eventSourceArn: queue.queueArn,
  batchSize: 10,
  maxBatchingWindow: Duration.seconds(5),
});
```

**Use Cases**: Background job processing, load leveling, retry semantics, decoupling producers/consumers

### Pattern 3: Pub/Sub (SNS + SQS Fan-Out)

**Architecture**: SNS topic broadcasts to multiple SQS queues, each with dedicated Lambda consumer.

**Fan-Out Pattern** [SKILL.md:393-414]():
```typescript
// SNS topic
const topic = new sns.Topic(this, 'OrderTopic', {
  displayName: 'Order Events',
});

// Multiple SQS subscriptions
const inventoryQueue = new sqs.Queue(this, 'InventoryQueue');
const shippingQueue = new sqs.Queue(this, 'ShippingQueue');
const analyticsQueue = new sqs.Queue(this, 'AnalyticsQueue');

topic.addSubscription(new subscriptions.SqsSubscription(inventoryQueue));
topic.addSubscription(new subscriptions.SqsSubscription(shippingQueue));
topic.addSubscription(new subscriptions.SqsSubscription(analyticsQueue));

// Each queue has independent consumer
new lambda.EventSourceMapping(this, 'InventoryConsumer', {
  target: inventoryFunction,
  eventSourceArn: inventoryQueue.queueArn,
});
```

**Benefits**: Broadcast events, parallel processing, service independence, buffering

### Pattern 4: Saga Pattern with Step Functions

**Architecture**: Distributed transactions with compensating actions for rollback.

**Saga Implementation** [SKILL.md:419-456]():

```mermaid
graph LR
    Start["Start"] --> Reserve["ReserveFlight<br/>tasks.LambdaInvoke"]
    Reserve --> Hotel["ReserveHotel<br/>tasks.LambdaInvoke"]
    Hotel --> Payment["ProcessPayment<br/>tasks.LambdaInvoke"]
    Payment --> Success["Success"]
    
    Reserve -.error.-> CancelFlight["CancelFlight<br/>Compensation"]
    Hotel -.error.-> CancelHotel["CancelHotel<br/>Compensation"]
    CancelHotel --> CancelFlight
    CancelFlight --> Failed["Failed"]
    
    Payment -.error.-> CancelHotel
```

**Code Pattern**:
```typescript
const definition = reserveFlight
  .next(reserveHotel)
  .next(processPayment)
  .addCatch(cancelHotel.next(cancelFlight), {
    resultPath: '$.error',
  });

new stepfunctions.StateMachine(this, 'BookingStateMachine', {
  definition,
  timeout: Duration.minutes(5),
});
```

**Use Cases**: Multi-service transactions (booking systems), long-running workflows, eventual consistency

### Pattern 5: Event Sourcing

**Architecture**: DynamoDB streams as append-only event store with projection functions.

**Event Store Schema** [SKILL.md:462-501]():

| Column | Type | Purpose |
|--------|------|---------|
| `aggregateId` | STRING (PK) | Entity identifier |
| `version` | NUMBER (SK) | Event sequence number |
| `eventType` | STRING | Event classification |
| `eventData` | MAP | Event payload |
| `timestamp` | NUMBER | Event creation time |

**Implementation**:
```typescript
const eventStore = new dynamodb.Table(this, 'EventStore', {
  partitionKey: { name: 'aggregateId', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'version', type: dynamodb.AttributeType.NUMBER },
  stream: dynamodb.StreamViewType.NEW_IMAGE,
});

// Lambda appends events
export const handleCommand = async (event: any) => {
  const { aggregateId, eventType, eventData } = event;
  
  // Get current version
  const items = await dynamodb.query({
    KeyConditionExpression: 'aggregateId = :id',
    Limit: 1,
  });
  
  const nextVersion = items.Items?.[0]?.version + 1 || 1;
  
  // Append event
  await dynamodb.putItem({
    Item: { aggregateId, version: nextVersion, eventType, eventData, timestamp: Date.now() },
  });
};

// Projections read from stream
eventStore.grantStreamRead(projectionFunction);
```

**Use Cases**: Audit trails, temporal queries, event replay, CQRS architectures

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:305-501]()

## Serverless Architecture Patterns

Five additional patterns for common serverless use cases:

```mermaid
graph TB
    subgraph "Serverless Patterns"
        P1["Pattern 1: API-Driven Microservices<br/>apigateway.RestApi<br/>apigateway.LambdaIntegration<br/>Throttling + Tracing"]
        
        P2["Pattern 2: Stream Processing<br/>kinesis.Stream<br/>lambda.EventSourceMapping<br/>parallelizationFactor + bisectBatchOnError"]
        
        P3["Pattern 3: Async Task Processing<br/>sqs.Queue + Lambda Worker<br/>Long polling + DLQ<br/>reservedConcurrentExecutions"]
        
        P4["Pattern 4: Scheduled Jobs<br/>events.Rule<br/>Schedule.cron / Schedule.rate<br/>Periodic Lambda invocation"]
        
        P5["Pattern 5: Webhook Processing<br/>API Gateway + SQS Queue<br/>Validate signature<br/>Async processing"]
    end
    
    P1 --> UC1["Use Case: REST APIs<br/>Microservices<br/>CRUD operations"]
    P2 --> UC2["Use Case: Real-time analytics<br/>Log processing<br/>IoT data streams"]
    P3 --> UC3["Use Case: Background jobs<br/>Image processing<br/>Report generation"]
    P4 --> UC4["Use Case: Cleanup tasks<br/>Data aggregation<br/>Scheduled reports"]
    P5 --> UC5["Use Case: Third-party webhooks<br/>Payment callbacks<br/>External integrations"]
```

### Pattern 1: API-Driven Microservices

**Components**: REST API with Lambda backend, throttling, and X-Ray tracing.

**Implementation** [SKILL.md:508-528]():
```typescript
const api = new apigateway.RestApi(this, 'Api', {
  restApiName: 'microservices-api',
  deployOptions: {
    throttlingRateLimit: 1000,
    throttlingBurstLimit: 2000,
    tracingEnabled: true,
  },
});

// User service
const users = api.root.addResource('users');
users.addMethod('GET', new apigateway.LambdaIntegration(getUsersFunction));
users.addMethod('POST', new apigateway.LambdaIntegration(createUserFunction));

// Order service
const orders = api.root.addResource('orders');
orders.addMethod('GET', new apigateway.LambdaIntegration(getOrdersFunction));
orders.addMethod('POST', new apigateway.LambdaIntegration(createOrderFunction));
```

### Pattern 2: Stream Processing

**Components**: Kinesis stream with Lambda consumer, parallel processing, and error handling.

**Configuration** [SKILL.md:533-552]():
```typescript
const stream = new kinesis.Stream(this, 'DataStream', {
  shardCount: 2,
  retentionPeriod: Duration.days(7),
});

new lambda.EventSourceMapping(this, 'StreamProcessor', {
  target: processFunction,
  eventSourceArn: stream.streamArn,
  batchSize: 100,
  maxBatchingWindow: Duration.seconds(5),
  parallelizationFactor: 10,
  startingPosition: lambda.StartingPosition.LATEST,
  retryAttempts: 3,
  bisectBatchOnError: true,
  onFailure: new lambdaDestinations.SqsDestination(dlq),
});
```

### Pattern 3: Async Task Processing

**Components**: SQS queue with Lambda worker, concurrency control, and partial batch failures.

**Implementation** [SKILL.md:557-581]():
```typescript
const taskQueue = new sqs.Queue(this, 'TaskQueue', {
  visibilityTimeout: Duration.minutes(5),
  receiveMessageWaitTime: Duration.seconds(20), // Long polling
  deadLetterQueue: { queue: dlq, maxReceiveCount: 3 },
});

const worker = new lambda.Function(this, 'TaskWorker', {
  reservedConcurrentExecutions: 10, // Control concurrency
});

new lambda.EventSourceMapping(this, 'TaskConsumer', {
  target: worker,
  eventSourceArn: taskQueue.queueArn,
  batchSize: 10,
  reportBatchItemFailures: true, // Partial batch failure handling
});
```

### Pattern 4: Scheduled Jobs

**Components**: EventBridge rules with cron/rate expressions for periodic Lambda invocations.

**Examples** [SKILL.md:586-599]():
```typescript
// Daily cleanup job at 2 AM
new events.Rule(this, 'DailyCleanup', {
  schedule: events.Schedule.cron({ hour: '2', minute: '0' }),
  targets: [new targets.LambdaFunction(cleanupFunction)],
});

// Process every 5 minutes
new events.Rule(this, 'FrequentProcessing', {
  schedule: events.Schedule.rate(Duration.minutes(5)),
  targets: [new targets.LambdaFunction(processFunction)],
});
```

### Pattern 5: Webhook Processing

**Components**: API Gateway endpoint with signature validation and asynchronous SQS queuing.

**Pattern** [SKILL.md:604-634]():
```typescript
const webhookApi = new apigateway.RestApi(this, 'WebhookApi', {
  restApiName: 'webhooks',
});

const webhook = webhookApi.root.addResource('webhook');
webhook.addMethod('POST', new apigateway.LambdaIntegration(webhookFunction, {
  proxy: true,
  timeout: Duration.seconds(29), // API Gateway max
}));

// Handler validates and queues
export const handler = async (event: APIGatewayProxyEvent) => {
  // Validate webhook signature
  const isValid = validateSignature(event.headers, event.body);
  if (!isValid) {
    return { statusCode: 401, body: 'Invalid signature' };
  }
  
  // Queue for async processing
  await sqs.sendMessage({
    QueueUrl: process.env.QUEUE_URL,
    MessageBody: event.body,
  });
  
  // Return immediately
  return { statusCode: 202, body: 'Accepted' };
};
```

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:503-635]()

## Best Practices and Observability

### Error Handling and Dead Letter Queues

**Partial Batch Failures** [SKILL.md:642-658]():
```typescript
export const handler = async (event: SQSEvent) => {
  const failures: SQSBatchItemFailure[] = [];
  
  for (const record of event.Records) {
    try {
      await processRecord(record);
    } catch (error) {
      console.error('Failed to process record:', record.messageId, error);
      failures.push({ itemIdentifier: record.messageId });
    }
  }
  
  // Return partial batch failures for retry
  return { batchItemFailures: failures };
};
```

**Dead Letter Queue Configuration** [SKILL.md:664-683]():
```typescript
const dlq = new sqs.Queue(this, 'DLQ', {
  retentionPeriod: Duration.days(14),
});

const queue = new sqs.Queue(this, 'Queue', {
  deadLetterQueue: {
    queue: dlq,
    maxReceiveCount: 3,
  },
});

// Monitor DLQ depth
new cloudwatch.Alarm(this, 'DLQAlarm', {
  metric: dlq.metricApproximateNumberOfMessagesVisible(),
  threshold: 1,
  evaluationPeriods: 1,
  alarmDescription: 'Messages in DLQ require attention',
});
```

### Observability Configuration

**X-Ray Tracing and Powertools** [SKILL.md:689-699]():
```typescript
new NodejsFunction(this, 'Function', {
  entry: 'src/handler.ts',
  tracing: lambda.Tracing.ACTIVE, // X-Ray tracing
  environment: {
    POWERTOOLS_SERVICE_NAME: 'order-service',
    POWERTOOLS_METRICS_NAMESPACE: 'MyApp',
    LOG_LEVEL: 'INFO',
  },
});
```

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:636-699]()

## MCP Server Integration Strategy

Unlike `aws-cdk` (1 MCP server) and `aws-cost-ops` (3 MCP servers), the serverless-eda plugin does **not register dedicated MCP servers**. Instead, it leverages a hybrid approach:

```mermaid
graph TB
    subgraph "serverless-eda Plugin"
        NoServers["No Dedicated MCP Servers<br/>marketplace.json: mcpServers = undefined"]
    end
    
    subgraph "Transitive MCP Access (via Dependencies)"
        AWSMCP["aws-mcp-setup skill<br/>mcp__aws-mcp__aws___*<br/>mcp__awsdocs__aws___*"]
        CDKMCP["aws-cdk-development skill<br/>mcp__cdk__*"]
        
        NoServers -.depends on.-> AWSMCP
        NoServers -.depends on.-> CDKMCP
    end
    
    subgraph "Allowed Tool Patterns"
        MCPTools["MCP Tools:<br/>mcp__aws-mcp__*<br/>mcp__awsdocs__*<br/>mcp__cdk__*"]
        BashTools["Bash Commands:<br/>sam *<br/>aws lambda *<br/>aws stepfunctions *<br/>aws events *<br/>aws sqs *<br/>aws sns *"]
    end
    
    subgraph "Optional Serverless MCP Servers (Not Integrated)"
        SAM["AWS Serverless MCP<br/>SAM CLI lifecycle<br/>NOT in marketplace"]
        LambdaTool["AWS Lambda Tool MCP<br/>Invoke functions<br/>NOT in marketplace"]
        SFN["AWS Step Functions MCP<br/>Execute workflows<br/>NOT in marketplace"]
        SNSSQS["AWS SNS/SQS MCP<br/>Messaging operations<br/>NOT in marketplace"]
        
        SAM -.user can add.-> NoServers
        LambdaTool -.user can add.-> NoServers
        SFN -.user can add.-> NoServers
        SNSSQS -.user can add.-> NoServers
    end
    
    NoServers --> MCPTools
    NoServers --> BashTools
```

### Transitive MCP Access

The plugin gains MCP capabilities through auto-loaded dependencies:

1. **AWS Documentation MCP** (via `aws-mcp-setup`):
   - `mcp__aws-mcp__aws___search_documentation` - Search AWS docs
   - `mcp__aws-mcp__aws___read_documentation` - Read specific pages
   - `mcp__aws-mcp__aws___get_regional_availability` - Check service availability

2. **CDK MCP** (via `aws-cdk-development`):
   - `mcp__cdk__*` - CDK construct recommendations and infrastructure patterns

### Direct AWS CLI Access

The skill configuration allows direct AWS CLI invocations [SKILL.md:12-20]():
- `Bash(sam *)` - SAM CLI for serverless deployments
- `Bash(aws lambda *)` - Lambda function management
- `Bash(aws apigateway *)` - REST API operations
- `Bash(aws apigatewayv2 *)` - HTTP API operations
- `Bash(aws dynamodb *)` - DynamoDB operations
- `Bash(aws stepfunctions *)` - Step Functions orchestration
- `Bash(aws events *)` - EventBridge event management
- `Bash(aws sqs *)` - SQS queue operations
- `Bash(aws sns *)` - SNS topic operations

### Optional MCP Servers

The skill documentation mentions four optional serverless MCP servers [SKILL.md:51-84]() that users can add manually (not included in marketplace):

| MCP Server | Purpose | Tools Provided |
|------------|---------|----------------|
| **AWS Serverless MCP** | SAM application lifecycle | Initialize, deploy, test locally, generate templates |
| **AWS Lambda Tool MCP** | Execute Lambda as tools | Invoke functions, test integrations, private resource access |
| **AWS Step Functions MCP** | Workflow orchestration | Create state machines, execute workflows, saga patterns |
| **AWS SNS/SQS MCP** | Event-driven messaging | Publish to SNS, send/receive SQS, pub/sub patterns |

**Integration Status**: These servers are **not registered** in `.claude-plugin/marketplace.json`. Users must add them separately if desired.

**Sources:** [.claude-plugin/marketplace.json:113-130](), [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:8-27](), [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:51-84]()

## Reference Documentation

The plugin includes six comprehensive reference files in the `references/` directory:

| Reference File | Coverage | Lines |
|----------------|----------|-------|
| **serverless-patterns.md** | Core serverless architectures, API patterns, data processing, Step Functions orchestration, anti-patterns | [SKILL.md:739-743]() |
| **eda-patterns.md** | Event routing and processing, event sourcing, saga patterns, idempotency, message ordering | [SKILL.md:745-749]() |
| **security-best-practices.md** | Shared responsibility model, IAM least privilege, data protection and encryption, VPC network security | [SKILL.md:751-755]() |
| **observability-best-practices.md** | Three pillars (metrics, logs, traces), structured logging with Powertools, X-Ray distributed tracing, CloudWatch dashboards | [SKILL.md:757-761]() |
| **performance-optimization.md** | Cold start optimization, memory and CPU tuning, package size reduction, provisioned concurrency | [SKILL.md:763-767]() |
| **deployment-best-practices.md** | CI/CD pipeline design, testing strategies (unit, integration, load), deployment strategies (canary, blue/green), rollback mechanisms | [SKILL.md:769-773]() |

### External Resources

The skill also references AWS documentation and learning resources:

- **AWS Well-Architected Serverless Lens**: https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/
- **ServerlessLand.com**: Pre-built serverless patterns and examples
- **AWS Serverless Workshops**: https://serverlessland.com/learn?type=Workshops

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:736-780]()

## Hook Configuration and Account Validation

The plugin implements a `PreToolUse` hook to validate AWS account context before deployments:

```mermaid
graph LR
    User["User Command:<br/>sam deploy ..."] --> Hook{PreToolUse Hook:<br/>Matcher}
    Hook -->|Matches<br/>'Bash(sam deploy*)'| Validate["Execute:<br/>aws sts get-caller-identity<br/>--query Account<br/>--output text"]
    Hook -->|Does not match| Continue["Continue execution"]
    Validate --> CheckOnce{once: true<br/>executed?}
    CheckOnce -->|No| Execute["Run validation<br/>Display account info<br/>Mark as executed"]
    CheckOnce -->|Yes| Skip["Skip validation<br/>Already run this session"]
    Execute --> Continue
    Skip --> Continue
    Continue --> Deploy["Execute:<br/>sam deploy"]
```

**Hook Configuration** [SKILL.md:22-26]():
```yaml
hooks:
  PreToolUse:
    - matcher: Bash(sam deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```

**Behavior**:
- **Trigger**: Before any command matching `Bash(sam deploy*)`
- **Action**: Execute `aws sts get-caller-identity` to display current AWS account
- **Frequency**: Once per session (`once: true`)
- **Purpose**: Prevent accidental cross-account deployments

**Sources:** [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:22-26]()

## Usage Examples

### Creating a Serverless API

**User Prompt**: "Create a serverless API with Lambda and API Gateway for user management"

**Expected Behavior**:
1. Auto-loads `aws-mcp-setup` and `aws-cdk-development` skills
2. Uses `mcp__cdk__*` tools for CDK construct recommendations
3. Applies principle #1 (Speedy, Simple, Singular) - separate Lambda for each operation
4. Applies principle #4 (No Hardware Affinity) - uses environment variables
5. Generates CDK code with `NodejsFunction` for automatic bundling

### Implementing Event-Driven Workflow

**User Prompt**: "Create an event-driven order processing system with EventBridge and Step Functions"

**Expected Behavior**:
1. Applies Pattern #1 (Event Router) - EventBridge for event routing
2. Applies principle #5 (Orchestrate with State Machines) - Step Functions for workflow
3. Applies principle #6 (Use Events to Trigger) - event-driven design
4. Applies principle #7 (Design for Failures) - idempotent operations with retries

### Implementing Saga Pattern

**User Prompt**: "Implement a saga pattern for booking flights, hotels, and car rentals with compensation logic"

**Expected Behavior**:
1. Uses Pattern #4 (Saga Pattern with Step Functions)
2. Defines forward transactions: reserve flight → reserve hotel → reserve car → process payment
3. Defines compensating transactions: cancel car → cancel hotel → cancel flight
4. Adds `.addCatch()` handlers for rollback on failures

**Sources:** [README.md:186-203](), [plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md:86-97]()

---

# Page: aws-agentic-ai Plugin

# aws-agentic-ai Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md](plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md)

</details>



The `aws-agentic-ai` plugin provides comprehensive guidance for deploying and managing AWS Bedrock AgentCore, a platform for building scalable AI agent applications. This plugin covers seven core AgentCore services (Gateway, Runtime, Memory, Identity, Code Interpreter, Browser, Observability) and their integration patterns. Unlike the `aws-cdk` [4.2](#4.2) and `aws-cost-ops` [4.3](#4.3) plugins, this plugin does not provide dedicated MCP servers but instead focuses on architectural patterns and AWS CLI workflows for AgentCore deployment.

For initial marketplace setup and installation, see [Getting Started](#2). For the foundational `aws-common` plugin that this plugin depends on, see [aws-common Plugin](#4.1).

## Plugin Overview

The plugin is registered in [.claude-plugin/marketplace.json:132-150]() at version 1.2.0 as part of the development category. It provides a single skill (`aws-agentic-ai`) that acts as a comprehensive guide for all AgentCore services.

**Key Characteristics**:
- **Version**: 1.2.0 (matching other domain plugins)
- **Category**: development
- **MCP Servers**: None (relies on `aws-common` for AWS documentation access)
- **Dependencies**: `aws-common` plugin for `aws-mcp-setup` skill
- **Primary Interface**: AWS CLI (`aws bedrock-agentcore-control` and `aws bedrock-agentcore-runtime` commands)

Sources: [.claude-plugin/marketplace.json:132-150](), [README.md:55-67]()

## Seven AgentCore Services

The plugin organizes guidance around seven core AgentCore services, each addressing a specific aspect of AI agent deployment and operation.

### Service Capabilities Matrix

```mermaid
graph TB
    subgraph "AgentCore Service Ecosystem"
        Gateway["Gateway Service<br/>REST APIs → MCP Tools<br/>services/gateway/README.md"]
        Runtime["Runtime Service<br/>Agent Deployment & Scaling<br/>services/runtime/README.md"]
        Memory["Memory Service<br/>Conversation State<br/>services/memory/README.md"]
        Identity["Identity Service<br/>Credential Management<br/>services/identity/README.md"]
        CodeInterp["Code Interpreter<br/>Secure Code Execution<br/>services/code-interpreter/README.md"]
        Browser["Browser Service<br/>Web Automation<br/>services/browser/README.md"]
        Observability["Observability<br/>Tracing & Monitoring<br/>services/observability/README.md"]
    end
    
    subgraph "Cross-Service Patterns"
        CredMgmt["Credential Management<br/>cross-service/credential-management.md"]
    end
    
    subgraph "AWS Backend Services"
        S3["Amazon S3<br/>Schema Storage"]
        Secrets["AWS Secrets Manager<br/>API Key Storage"]
        Lambda["AWS Lambda<br/>Custom Targets"]
        CW["CloudWatch<br/>Metrics & Logs"]
        XRay["AWS X-Ray<br/>Distributed Tracing"]
    end
    
    Gateway -->|stores schemas| S3
    Gateway -->|retrieves credentials| Identity
    Identity -->|stores API keys| Secrets
    Runtime -->|executes| Lambda
    Memory -->|stores conversations| S3
    Observability -->|publishes metrics| CW
    Observability -->|traces requests| XRay
    
    Gateway -.uses pattern.-> CredMgmt
    Identity -.defines pattern.-> CredMgmt
```

**Service Breakdown**:

| Service | Primary Use Case | Documentation Path |
|---------|------------------|-------------------|
| **Gateway** | Converting REST APIs to MCP tools for agent consumption | `services/gateway/README.md` |
| **Runtime** | Deploying and auto-scaling agent execution environments | `services/runtime/README.md` |
| **Memory** | Persisting conversation history and context across sessions | `services/memory/README.md` |
| **Identity** | Managing API credentials, authentication, and authorization | `services/identity/README.md` |
| **Code Interpreter** | Executing user-provided code in isolated sandboxes | `services/code-interpreter/README.md` |
| **Browser** | Automating web interactions and scraping for agents | `services/browser/README.md` |
| **Observability** | Monitoring agent performance and debugging issues | `services/observability/README.md` |

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:62-72](), [README.md:55-67]()

## Skill Configuration

The plugin's single skill is defined in [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md]() with comprehensive frontmatter configuration that controls execution context, dependencies, and tool permissions.

### Skill Metadata and Execution Context

```mermaid
graph LR
    subgraph "Skill Definition: aws-agentic-ai"
        Meta["Skill Metadata<br/>name: aws-agentic-ai<br/>aliases: bedrock-agentcore<br/>context: fork<br/>model: sonnet"]
        
        Deps["Skill Dependencies<br/>skills:<br/>  - aws-mcp-setup"]
        
        Tools["Tool Permissions<br/>allowed-tools:<br/>  - mcp__aws-mcp__*<br/>  - mcp__awsdocs__*<br/>  - Bash(aws bedrock-agentcore-control *)<br/>  - Bash(aws bedrock-agentcore-runtime *)<br/>  - Bash(aws bedrock *)<br/>  - Bash(aws s3 cp *)<br/>  - Bash(aws s3 ls *)<br/>  - Bash(aws secretsmanager *)<br/>  - Bash(aws sts get-caller-identity)"]
        
        Hooks["PreToolUse Hook<br/>matcher: Bash(aws bedrock-agentcore-control create-*)<br/>command: aws sts get-caller-identity<br/>once: true"]
    end
    
    subgraph "Execution Environment"
        Fork["Fork Context<br/>Isolated Sub-Agent"]
        Model["Model: sonnet<br/>Claude 3.5 Sonnet"]
        AWSCmds["AWS CLI Commands<br/>bedrock-agentcore-control<br/>bedrock-agentcore-runtime"]
    end
    
    subgraph "Auto-Loaded Dependencies"
        MCPSetup["aws-mcp-setup skill<br/>from aws-common plugin"]
        MCPTools["MCP Tools<br/>mcp__aws-mcp__aws___search_documentation<br/>mcp__awsdocs__aws___search_documentation"]
    end
    
    Meta --> Fork
    Meta --> Model
    Deps --> MCPSetup
    Tools --> AWSCmds
    Tools --> MCPTools
    Hooks --> AWSCmds
```

**Configuration Details**:

1. **Execution Context** [SKILL.md:7-8]():
   - `context: fork` - Executes in isolated sub-agent for focused AgentCore guidance
   - `model: sonnet` - Uses Claude 3.5 Sonnet for complex architectural decisions

2. **Dependency Chain** [SKILL.md:9-10]():
   - Depends on `aws-mcp-setup` skill from `aws-common` plugin
   - Auto-loads MCP documentation tools before answering AWS questions
   - Ensures all guidance is based on current AWS documentation

3. **Tool Permissions** [SKILL.md:11-20]():
   - **MCP Tools**: `mcp__aws-mcp__*` and `mcp__awsdocs__*` patterns allow access to AWS documentation search and retrieval
   - **Bedrock Commands**: `aws bedrock-agentcore-control` for service management, `aws bedrock-agentcore-runtime` for agent execution
   - **Supporting Commands**: `aws s3`, `aws secretsmanager`, `aws bedrock` for schema upload, credential storage, and model access
   - **Validation**: `aws sts get-caller-identity` for account verification

4. **Pre-Tool Hook** [SKILL.md:21-26]():
   - Matches any `create-*` operation in `bedrock-agentcore-control`
   - Automatically executes `aws sts get-caller-identity` to verify AWS account
   - Runs once per session to prevent accidental cross-account deployments
   - Displays account ID before creating AgentCore resources

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:1-26]()

## Documentation Structure

The plugin organizes documentation into two primary categories: service-specific guides and cross-service patterns. This structure reflects the modular nature of AgentCore where services can be used independently or combined for comprehensive agent applications.

### Documentation Organization Diagram

```mermaid
graph TB
    subgraph "Plugin Root: plugins/aws-agentic-ai/skills/aws-agentic-ai/"
        SkillMD["SKILL.md<br/>Skill definition + quickstart"]
        
        subgraph "services/ Directory"
            GatewayDir["gateway/<br/>REST API → MCP conversion"]
            RuntimeDir["runtime/<br/>Agent deployment"]
            MemoryDir["memory/<br/>Conversation state"]
            IdentityDir["identity/<br/>Credential management"]
            CodeInterpDir["code-interpreter/<br/>Code execution"]
            BrowserDir["browser/<br/>Web automation"]
            ObsDir["observability/<br/>Monitoring & tracing"]
        end
        
        subgraph "cross-service/ Directory"
            CredMgmt["credential-management.md<br/>Unified credential patterns"]
        end
        
        subgraph "Gateway Service Details"
            GatewayReadme["gateway/README.md<br/>Overview & quickstart"]
            DeployStrat["gateway/deployment-strategies.md<br/>Deployment patterns"]
            Troubleshoot["gateway/troubleshooting-guide.md<br/>Common issues & solutions"]
        end
    end
    
    subgraph "Referenced by SKILL.md"
        ServiceTable["Service Selection Table<br/>Lines 62-72"]
        Workflows["Common Workflows<br/>Lines 73-106"]
        Resources["Service-Specific Docs<br/>Lines 107-124"]
        CrossService["Cross-Service Patterns<br/>Lines 125-130"]
    end
    
    SkillMD --> ServiceTable
    SkillMD --> Workflows
    SkillMD --> Resources
    SkillMD --> CrossService
    
    ServiceTable --> GatewayDir
    ServiceTable --> RuntimeDir
    ServiceTable --> MemoryDir
    ServiceTable --> IdentityDir
    ServiceTable --> CodeInterpDir
    ServiceTable --> BrowserDir
    ServiceTable --> ObsDir
    
    Workflows --> GatewayReadme
    Workflows --> CredMgmt
    Workflows --> ObsDir
    
    Resources --> GatewayReadme
    Resources --> DeployStrat
    Resources --> Troubleshoot
    
    CrossService --> CredMgmt
```

**Documentation Hierarchy**:

1. **Entry Point** [SKILL.md:28-136]():
   - `SKILL.md` provides skill configuration, service overview, and common workflows
   - Links to detailed documentation with `MANDATORY - READ DETAILED DOCUMENTATION` directives
   - Ensures users access comprehensive guides before implementation

2. **Service-Specific Documentation**:
   - Each service has a dedicated subdirectory under `services/`
   - Minimum: `README.md` with overview, setup, and CLI examples
   - Gateway service includes additional specialized guides:
     - `deployment-strategies.md` - Architecture patterns for different use cases
     - `troubleshooting-guide.md` - Common errors and resolution steps

3. **Cross-Service Patterns** [SKILL.md:125-130]():
   - `cross-service/credential-management.md` - Unified credential patterns used across Gateway, Identity, and other services
   - Provides security best practices, rotation procedures, and monitoring strategies
   - Single source of truth for credential handling across all AgentCore services

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:62-130](), [README.md:258-264]()

## Common Workflows

The skill defines three primary workflows that represent the most frequent AgentCore use cases. Each workflow includes a quick reference in `SKILL.md` and links to comprehensive documentation.

### Gateway Target Deployment Workflow

```mermaid
sequenceDiagram
    participant User
    participant Skill as "aws-agentic-ai Skill"
    participant S3 as "Amazon S3"
    participant Identity as "Identity Service"
    participant Gateway as "Gateway Service"
    participant Target as "Gateway Target"
    
    Note over User,Target: Deploying REST API as MCP Tool
    
    User->>Skill: Request Gateway deployment
    Skill->>Skill: Read services/gateway/README.md
    
    Skill->>User: Guide: Upload OpenAPI schema
    User->>S3: aws s3 cp openapi.json s3://bucket/schema.json
    
    alt API Key Authentication
        Skill->>User: Guide: Create credential provider
        User->>Identity: aws bedrock-agentcore-control create-credential-provider
        User->>S3: Store API key in Secrets Manager
        Note over User,Identity: credential-provider-arn returned
    end
    
    Skill->>User: Guide: Create gateway target
    User->>Gateway: aws bedrock-agentcore-control create-gateway-target<br/>--schema-location s3://bucket/schema.json<br/>--credential-provider-arn (if API key)
    
    Gateway->>Target: Deploy target
    Target-->>User: target-arn and status
    
    Skill->>User: Guide: Verify target
    User->>Gateway: aws bedrock-agentcore-control get-gateway-target
    Gateway-->>User: status: ACTIVE
```

**Workflow Steps** [SKILL.md:75-85]():

1. **Upload OpenAPI Schema** - Store API specification in S3 for Gateway to reference
2. **Create Credential Provider** (API key auth only) - Use Identity service to store API key in Secrets Manager
3. **Create Gateway Target** - Link schema and credentials (if applicable) via `create-gateway-target` command
4. **Verify Target** - Check status transitions from CREATING → ACTIVE

**Authentication Options**:
- **API Key**: Requires credential provider ARN reference
- **Lambda**: Uses IAM roles (no credential provider needed)
- **MCP Servers**: Uses OAuth flows (handled by Runtime service)

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:75-85]()

### Credential Management Workflow

```mermaid
graph LR
    subgraph "Credential Lifecycle"
        Create["Create Provider<br/>aws bedrock-agentcore-control<br/>create-credential-provider"]
        Store["Store Secret<br/>aws secretsmanager put-secret-value"]
        Link["Link to Target<br/>--credential-provider-arn"]
        Monitor["Monitor Usage<br/>CloudWatch metrics"]
        Rotate["Rotate Quarterly<br/>update-credential-provider"]
    end
    
    Create --> Store
    Store --> Link
    Link --> Monitor
    Monitor --> Rotate
    Rotate --> Store
    
    subgraph "Cross-Service Pattern"
        Pattern["cross-service/credential-management.md<br/>Unified credential patterns<br/>Security best practices<br/>Rotation procedures"]
    end
    
    subgraph "Services Using Pattern"
        GatewayService["Gateway Service<br/>API key authentication"]
        IdentityService["Identity Service<br/>Credential provider management"]
        RuntimeService["Runtime Service<br/>OAuth token handling"]
    end
    
    Pattern -.guides.-> Create
    Pattern -.guides.-> Monitor
    Pattern -.guides.-> Rotate
    
    GatewayService -.uses.-> Create
    IdentityService -.manages.-> Create
    RuntimeService -.consumes.-> Create
```

**Workflow Steps** [SKILL.md:87-96]():

1. **Use Identity Service** - All API keys managed through credential providers (not direct Secrets Manager)
2. **Link Providers** - Reference provider ARN in gateway targets for automatic credential injection
3. **Rotate Quarterly** - Update credential provider with new secrets following documented rotation procedures
4. **Monitor Usage** - Track credential access via CloudWatch metrics for anomaly detection

**Key Principle**: The `cross-service/credential-management.md` document provides a single source of truth for credential handling across all AgentCore services, ensuring consistent security practices.

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:87-96]()

### Observability Workflow

```mermaid
graph TB
    subgraph "Agent Execution"
        Agent["AI Agent<br/>Bedrock Runtime"]
        Gateway["Gateway Targets<br/>MCP Tool Calls"]
        Memory["Memory Service<br/>State Management"]
    end
    
    subgraph "Observability Components"
        Enable["Enable Observability<br/>--observability-configuration"]
        Metrics["CloudWatch Metrics<br/>Invocation count, latency, errors"]
        Logs["CloudWatch Logs<br/>Request/response traces"]
        XRay["AWS X-Ray<br/>Distributed tracing"]
        Dashboard["CloudWatch Dashboards<br/>Unified monitoring view"]
        Alarms["CloudWatch Alarms<br/>Error rate, latency thresholds"]
    end
    
    subgraph "Monitoring Setup"
        ObsDoc["services/observability/README.md<br/>Comprehensive monitoring guide"]
    end
    
    Agent --> Enable
    Gateway --> Enable
    Memory --> Enable
    
    Enable --> Metrics
    Enable --> Logs
    Enable --> XRay
    
    Metrics --> Dashboard
    Metrics --> Alarms
    Logs --> Dashboard
    XRay --> Dashboard
    
    ObsDoc -.guides.-> Enable
    ObsDoc -.guides.-> Dashboard
    ObsDoc -.guides.-> Alarms
```

**Workflow Steps** [SKILL.md:98-106]():

1. **Enable Observability** - Configure observability settings when creating agents or targets
2. **Configure Dashboards** - Set up CloudWatch dashboards aggregating metrics across services
3. **Set Up Alarms** - Create alarms for error rates, latency percentiles, and throughput thresholds
4. **Use X-Ray** - Enable distributed tracing for end-to-end request visibility across gateway, runtime, and memory services

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:98-106]()

## AWS Documentation Requirement

Like all domain plugins, `aws-agentic-ai` enforces a strict policy of consulting live AWS documentation before providing guidance. This prevents outdated information and ensures recommendations align with current AWS service capabilities.

### Documentation Access Flow

```mermaid
graph TB
    User["User asks AgentCore question"]
    Check{AWS MCP<br/>tools available?}
    Search["mcp__aws-mcp__aws___search_documentation<br/>or<br/>mcp__awsdocs__aws___search_documentation"]
    Read["mcp__aws-mcp__aws___read_documentation<br/>or<br/>mcp__awsdocs__aws___read_documentation"]
    Regional["mcp__aws-mcp__aws___get_regional_availability"]
    
    GuideMCP["Guide user to aws-mcp-setup skill<br/>Auto-loaded as dependency"]
    DetermineEnv{User environment?}
    FullMCP["Full AWS MCP Server<br/>Requires: uvx + AWS credentials<br/>Provides: Full API + Docs"]
    DocsMCP["AWS Documentation MCP<br/>Requires: None<br/>Provides: Docs only"]
    
    AnswerQuestion["Provide guidance using<br/>current AWS documentation"]
    
    User --> Check
    Check -->|Yes| Search
    Search --> Read
    Read --> Regional
    Regional --> AnswerQuestion
    
    Check -->|No| GuideMCP
    GuideMCP --> DetermineEnv
    DetermineEnv -->|Has uvx + creds| FullMCP
    DetermineEnv -->|No Python/creds| DocsMCP
    DetermineEnv -->|Unknown| DetermineEnv
    
    FullMCP --> Search
    DocsMCP --> Search
```

**Implementation Details** [SKILL.md:32-48]():

1. **CRITICAL Policy**: Skill must verify AWS information using MCP tools before answering
2. **MCP Tool Pattern**: Supports both `mcp__aws-mcp__aws___*` (full server) and `mcp__awsdocs__aws___*` (docs-only server)
3. **Auto-Loaded Dependency**: `aws-mcp-setup` skill (from `aws-common` plugin) is automatically loaded via `skills:` frontmatter
4. **Setup Guidance**: If MCP tools unavailable, guide user through configuration options:
   - Full AWS MCP Server: Requires `uvx` and AWS credentials, provides full API + documentation access
   - AWS Documentation MCP: No prerequisites, provides documentation-only access
5. **Environment Detection**: Help user determine which option fits their setup, or ask if unable to determine

This architecture ensures no AgentCore guidance is provided without consulting current AWS documentation, preventing the skill from providing stale or incorrect information about rapidly evolving services.

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:32-48]()

## Integration with AWS Services

The plugin enables interaction with AgentCore services through AWS CLI commands, complemented by supporting AWS services for storage, credentials, and monitoring.

### AWS CLI Command Structure

```mermaid
graph LR
    subgraph "Control Plane Commands"
        CreateGW["aws bedrock-agentcore-control<br/>create-gateway-target"]
        CreateCP["aws bedrock-agentcore-control<br/>create-credential-provider"]
        CreateAgent["aws bedrock-agentcore-control<br/>create-agent"]
        GetStatus["aws bedrock-agentcore-control<br/>get-gateway-target<br/>get-agent"]
        Update["aws bedrock-agentcore-control<br/>update-*"]
        Delete["aws bedrock-agentcore-control<br/>delete-*"]
    end
    
    subgraph "Runtime Commands"
        InvokeAgent["aws bedrock-agentcore-runtime<br/>invoke-agent"]
        InvokeFlow["aws bedrock-agentcore-runtime<br/>invoke-flow"]
    end
    
    subgraph "Supporting Services"
        S3Ops["aws s3 cp<br/>aws s3 ls<br/>Schema upload"]
        SecretOps["aws secretsmanager<br/>put-secret-value<br/>Credential storage"]
        STSOps["aws sts get-caller-identity<br/>Account verification"]
        BedrockOps["aws bedrock<br/>Model access"]
    end
    
    subgraph "Hook Integration"
        PreHook["PreToolUse Hook<br/>matcher: create-*<br/>command: aws sts get-caller-identity<br/>once: true"]
    end
    
    PreHook -.triggers before.-> CreateGW
    PreHook -.triggers before.-> CreateCP
    PreHook -.triggers before.-> CreateAgent
    
    CreateGW --> S3Ops
    CreateCP --> SecretOps
    InvokeAgent --> BedrockOps
```

**Command Categories**:

1. **Control Plane** [SKILL.md:14]():
   - `aws bedrock-agentcore-control create-*` - Create AgentCore resources (gateway targets, agents, credential providers)
   - `aws bedrock-agentcore-control get-*` - Retrieve resource status and configuration
   - `aws bedrock-agentcore-control update-*` - Modify existing resources
   - `aws bedrock-agentcore-control delete-*` - Remove resources

2. **Runtime** [SKILL.md:15]():
   - `aws bedrock-agentcore-runtime invoke-agent` - Execute agents with user input
   - `aws bedrock-agentcore-runtime invoke-flow` - Execute predefined workflows

3. **Supporting Commands** [SKILL.md:16-20]():
   - `aws s3 cp` / `aws s3 ls` - Upload/list OpenAPI schemas
   - `aws secretsmanager *` - Store and retrieve API keys
   - `aws sts get-caller-identity` - Verify AWS account (used by PreToolUse hook)
   - `aws bedrock *` - Access foundation models

4. **Pre-Tool Hook** [SKILL.md:21-26]():
   - Automatically runs `aws sts get-caller-identity` before any `create-*` operation
   - Displays AWS account ID for verification
   - Executes once per session to prevent repeated prompts
   - Prevents accidental cross-account resource creation

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:11-26]()

## Usage Patterns

The plugin guides users through AgentCore deployment using natural language prompts that trigger skill-guided workflows.

**Example Prompts** [README.md:206-224]():

```
# Gateway Service
Deploy a REST API as an MCP tool using AgentCore Gateway

# Memory Service  
Set up conversation memory for my AI agent with DynamoDB backend

# Observability
Configure observability for my AgentCore runtime with CloudWatch dashboards
```

**Execution Flow**:
1. User provides natural language description of desired AgentCore functionality
2. Skill identifies relevant service(s) from the seven AgentCore services
3. Skill reads detailed documentation from `services/` or `cross-service/` directories
4. Skill guides user through AWS CLI commands with parameter explanations
5. PreToolUse hook verifies account before any `create-*` operations
6. Skill validates resource creation and provides next steps

**Multi-Service Scenarios**:
- Gateway + Identity: API deployment with credential management
- Runtime + Memory: Agent execution with conversation persistence
- Gateway + Observability: API deployment with monitoring
- All Services: Comprehensive agent application with full observability

Sources: [README.md:206-224](), [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:50-72]()

## Dependency on aws-common Plugin

The `aws-agentic-ai` plugin has a mandatory dependency on the `aws-common` plugin, specifically its `aws-mcp-setup` skill for AWS documentation access.

### Dependency Chain

```mermaid
graph TB
    subgraph "Plugin Installation Order"
        InstallCommon["1. /plugin install aws-common@aws-skills<br/>Required first"]
        InstallAgentic["2. /plugin install aws-agentic-ai@aws-skills<br/>Depends on aws-common"]
    end
    
    subgraph "Skill Dependency Resolution"
        AgenticSkill["aws-agentic-ai skill<br/>SKILL.md frontmatter"]
        SkillsDep["skills:<br/>  - aws-mcp-setup"]
        MCPSetup["aws-mcp-setup skill<br/>from aws-common plugin"]
    end
    
    subgraph "Runtime Auto-Loading"
        UserPrompt["User asks AgentCore question"]
        LoadAgentic["Load aws-agentic-ai skill<br/>context: fork"]
        AutoLoadMCP["Auto-load aws-mcp-setup<br/>Before skill execution"]
        CheckMCP["Check AWS MCP tools availability"]
        GuidanceFlow["Provide guidance or setup MCP"]
    end
    
    InstallCommon --> InstallAgentic
    
    AgenticSkill --> SkillsDep
    SkillsDep --> MCPSetup
    
    UserPrompt --> LoadAgentic
    LoadAgentic --> AutoLoadMCP
    AutoLoadMCP --> CheckMCP
    CheckMCP --> GuidanceFlow
```

**Dependency Mechanism** [SKILL.md:9-10]():

1. **Installation Requirement**: `aws-common` must be installed before `aws-agentic-ai`
2. **Skill Frontmatter Declaration**: `skills: [aws-mcp-setup]` declares the dependency
3. **Auto-Loading**: When `aws-agentic-ai` skill executes, `aws-mcp-setup` is automatically loaded first
4. **MCP Tool Access**: Provides `mcp__aws-mcp__aws___*` or `mcp__awsdocs__aws___*` tools for documentation search

**Why This Dependency Exists**:
- AgentCore services evolve rapidly with new features and API changes
- Live documentation access ensures guidance remains accurate
- Prevents skill from providing outdated deployment patterns
- Enables verification of service availability in specific AWS regions

Without this dependency, the skill would be limited to static documentation that could quickly become obsolete as AWS updates AgentCore services.

Sources: [plugins/aws-agentic-ai/skills/aws-agentic-ai/SKILL.md:9-10](), [.claude-plugin/marketplace.json:132-150](), [README.md:78-87]()

## Version and Maintenance

The plugin follows the version management strategy defined for all AWS Skills plugins.

**Current Version**: 1.2.0 [.claude-plugin/marketplace.json:135]()

**Version Bump Policy** (see [Version Management](#5.2) for details):
- **Minor Bump** (x.Y.0): New AgentCore service coverage, new dependencies, structural changes to documentation
- **Patch Bump** (x.y.Z): Bug fixes, documentation updates, typo corrections in service guides

**Marketplace Version**: Independent from plugin version; only bumps when new plugins are added to marketplace (currently 2.2.0)

Sources: [.claude-plugin/marketplace.json:9](), [.claude-plugin/marketplace.json:135]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)

</details>



This document provides technical guidance for contributors who want to modify existing plugins, add new skills, create new plugins, or enhance the AWS Skills marketplace. It covers the plugin development workflow, directory structure conventions, skill configuration syntax, MCP server integration patterns, and testing strategies.

For step-by-step instructions on setting up your local development environment, see [Local Development Setup](#5.1). For rules on version bumping and release management, see [Version Management](#5.2). For validation strategies and quality gates, see [Validation and Quality Assurance](#5.3).

## Repository Architecture

The repository follows a marketplace-plugin-skill hierarchy with standardized directory structures and configuration files.

**Repository Structure Overview**

```mermaid
graph TB
    subgraph "Repository Root"
        Marketplace[".claude-plugin/marketplace.json<br/>Central Registry"]
        Claude["CLAUDE.md<br/>Development Guidelines"]
        SkillsDir[".claude/skills/<br/>Symlinked Skills"]
    end
    
    subgraph "Plugin Directory Structure"
        PluginRoot["plugins/{plugin-name}/"]
        SkillsFolder["skills/{skill-name}/"]
        SkillFile["SKILL.md<br/>Frontmatter + Content"]
        References["references/*.md<br/>Pattern Documentation"]
        Scripts["scripts/*.sh<br/>Optional Utilities"]
        Services["services/<br/>Optional Code"]
    end
    
    subgraph "Configuration Flow"
        MarketplaceDef["marketplace.json<br/>plugins[] array"]
        PluginMeta["name, version, mcpServers"]
        SkillMeta["skills[] paths"]
        FrontmatterConfig["---<br/>name, context, model<br/>skills[], allowed-tools[]<br/>---"]
    end
    
    Marketplace --> MarketplaceDef
    MarketplaceDef --> PluginMeta
    PluginMeta --> SkillMeta
    PluginRoot --> SkillsFolder
    SkillsFolder --> SkillFile
    SkillFile --> FrontmatterConfig
    SkillsFolder --> References
    PluginRoot -.optional.-> Scripts
    PluginRoot -.optional.-> Services
    
    SkillsFolder -.symlinked to.-> SkillsDir
```

**Sources:** [.claude-plugin/marketplace.json:1-152](), [CLAUDE.md:9-24]()

The marketplace uses a three-tier architecture:
1. **Marketplace Registry** - `.claude-plugin/marketplace.json` defines all plugins, versions, and MCP server configurations
2. **Plugin Layer** - Each plugin in `plugins/` contains one or more skills with metadata
3. **Skill Layer** - Skills in `skills/{skill-name}/` directories contain SKILL.md with frontmatter configuration and markdown content

## Plugin Development Workflow

The typical workflow for plugin development involves local changes, symlink testing, version bumping, and marketplace updates.

**Development Workflow Diagram**

```mermaid
graph LR
    subgraph "Local Development"
        EditSkill["Edit plugins/{plugin}/skills/{skill}/SKILL.md"]
        EditRefs["Edit plugins/{plugin}/skills/{skill}/references/*.md"]
        EditConfig["Edit .claude-plugin/marketplace.json"]
    end
    
    subgraph "Testing"
        Symlinks[".claude/skills/ symlinks<br/>point to plugins/"]
        ClaudeCLI["claude -p 'test prompt'"]
        SkillsCmd["/skills command<br/>in Claude IDE"]
    end
    
    subgraph "Validation"
        VersionBump["Bump version in<br/>marketplace.json<br/>plugins[].version"]
        TypeCheck["Minor vs Patch<br/>See Version Management"]
        CommitChanges["git commit"]
    end
    
    EditSkill --> Symlinks
    EditRefs --> Symlinks
    EditConfig --> VersionBump
    Symlinks --> ClaudeCLI
    Symlinks --> SkillsCmd
    ClaudeCLI --> TypeCheck
    SkillsCmd --> TypeCheck
    TypeCheck --> VersionBump
    VersionBump --> CommitChanges
```

**Sources:** [CLAUDE.md:26-54](), [CLAUDE.md:89-108]()

### Development Steps

1. **Make Changes** - Edit skill files in `plugins/{plugin-name}/skills/`
2. **Test Locally** - Skills are automatically available via symlinks in `.claude/skills/`
3. **Determine Version Bump** - Classify change as Minor (structural) or Patch (content)
4. **Update Version** - Modify version in `.claude-plugin/marketplace.json`
5. **Commit** - All changes must include version bump before committing

## Plugin Directory Structure

Each plugin follows a standardized directory structure with required and optional components.

| Component | Location | Required | Purpose |
|-----------|----------|----------|---------|
| Skill Definition | `skills/{skill-name}/SKILL.md` | ✓ | Frontmatter configuration + skill content |
| Reference Docs | `skills/{skill-name}/references/*.md` | Optional | Detailed pattern documentation |
| Utility Scripts | `scripts/*.sh` | Optional | Helper scripts (e.g., validation) |
| Service Code | `services/` | Optional | Service-specific implementations |
| Cross-Service Code | `cross-service/` | Optional | Shared code across services |

**Sources:** [CLAUDE.md:21-24](), [.claude-plugin/marketplace.json:25-29]()

### Plugin Metadata in Marketplace

Each plugin entry in `.claude-plugin/marketplace.json` requires:

```yaml
{
  "name": "plugin-name",           # Unique identifier
  "description": "...",            # Plugin purpose
  "version": "x.y.z",              # Semantic version
  "author": {...},                 # Contact information
  "category": "development",       # Category classification
  "source": "./plugins/plugin-name", # Relative path
  "strict": false,                 # Error handling mode
  "skills": ["./skills/skill-name"], # Skill paths
  "mcpServers": {...}              # Optional MCP configuration
}
```

**Sources:** [.claude-plugin/marketplace.json:12-30](), [.claude-plugin/marketplace.json:31-61]()

## Skill Frontmatter Configuration

Skills use YAML frontmatter in `SKILL.md` to configure execution behavior. This is the primary mechanism for defining skill metadata, dependencies, tool permissions, and lifecycle hooks.

### Frontmatter Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `name` | string | Skill identifier | `aws-cdk-development` |
| `description` | string | Brief purpose statement | `AWS CDK infrastructure...` |
| `context` | string | Execution context | `fork` (run in sub-agent) |
| `model` | string | Model to use | `sonnet` |
| `skills` | array | Auto-loaded dependencies | `["aws-mcp-setup"]` |
| `allowed-tools` | array | Tool permission patterns | `["mcp__plugin_*"]` |
| `hooks` | object | Lifecycle hooks | `PreToolUse: [{...}]` |

**Sources:** [CLAUDE.md:56-77]()

### Frontmatter Example with All Features

```yaml
---
name: aws-cdk-development
description: Expert AWS CDK development assistance
context: fork
model: sonnet
skills:
  - aws-mcp-setup
allowed-tools:
  - mcp__plugin_aws_cdk_cdk__*
  - Bash(aws *)
  - Bash(cdk *)
  - Bash(npm *)
hooks:
  PreToolUse:
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
---
```

**Sources:** [CLAUDE.md:60-76]()

### Dependency Auto-Loading

The `skills:` frontmatter field creates automatic dependency chains:
- When a skill is invoked, all listed sub-skills are automatically loaded
- This enables hierarchical skill composition
- Example: `aws-serverless-eda` skill lists both `aws-mcp-setup` and `aws-cdk-development`, so both are auto-loaded

### Tool Permission Patterns

The `allowed-tools:` field uses wildcard patterns for flexible permission grants:
- `mcp__plugin_aws_cdk_cdk__*` - All tools from the `cdk` MCP server in `aws-cdk` plugin
- `Bash(aws *)` - All AWS CLI commands
- `Bash(cdk *)` - All CDK CLI commands

### Lifecycle Hooks

Hooks execute commands at specific lifecycle points:
- `PreToolUse` - Runs before a tool matching `matcher` pattern executes
- `once: true` - Hook executes only once per session (useful for account verification)
- Example use case: Verify AWS account identity before `cdk deploy` to prevent cross-account mistakes

**Sources:** [CLAUDE.md:71-76]()

## MCP Server Integration

MCP (Model Context Protocol) servers provide AWS service integrations. Plugins can declare MCP servers in the marketplace configuration.

**MCP Server Configuration Flow**

```mermaid
graph TB
    subgraph "marketplace.json Configuration"
        PluginEntry["plugins[] entry"]
        MCPServers["mcpServers: {}<br/>Server definitions"]
        ServerConfig["server-name: {<br/>  type: 'stdio'<br/>  command: 'uvx'<br/>  args: ['package@latest']<br/>  env: {}<br/>}"]
    end
    
    subgraph "Runtime Execution"
        UVX["uvx command<br/>Python package launcher"]
        Package["awslabs.*-mcp-server@latest<br/>PyPI package"]
        StdioProtocol["stdio communication<br/>JSON-RPC messages"]
        ToolNaming["Tool naming:<br/>mcp__plugin_{plugin}_{server}__{tool}"]
    end
    
    subgraph "Example: aws-cdk Plugin"
        CDKConfig["mcpServers.cdk"]
        CDKCommand["command: 'uvx'<br/>args: ['awslabs.cdk-mcp-server@latest']"]
        CDKEnv["env.FASTMCP_LOG_LEVEL: 'ERROR'"]
        CDKTools["mcp__plugin_aws_cdk_cdk__list_constructs<br/>mcp__plugin_aws_cdk_cdk__search_constructs"]
    end
    
    PluginEntry --> MCPServers
    MCPServers --> ServerConfig
    ServerConfig --> UVX
    UVX --> Package
    Package --> StdioProtocol
    StdioProtocol --> ToolNaming
    
    CDKConfig --> CDKCommand
    CDKCommand --> CDKEnv
    CDKEnv --> CDKTools
```

**Sources:** [.claude-plugin/marketplace.json:49-60](), [.claude-plugin/marketplace.json:80-111](), [CLAUDE.md:79-87]()

### MCP Server Configuration Schema

Add MCP servers to a plugin in `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "mcpServers": {
        "server-short-name": {
          "type": "stdio",
          "command": "uvx",
          "args": ["awslabs.package-name@latest"],
          "env": {
            "FASTMCP_LOG_LEVEL": "ERROR"
          }
        }
      }
    }
  ]
}
```

**Sources:** [.claude-plugin/marketplace.json:49-60]()

### MCP Server Naming Conventions

| Component | Constraint | Rationale |
|-----------|------------|-----------|
| Server Short Name | Brief (e.g., `cdk`, `pricing`, `costexp`, `cw`) | Bedrock 64-char tool name limit |
| Tool Name Pattern | `mcp__plugin_{plugin}_{server}__{tool}` | Namespace isolation between plugins |
| Package Name | `awslabs.*-mcp-server@latest` | Official AWS Labs packages |
| Log Level | `FASTMCP_LOG_LEVEL: "ERROR"` | Reduce noise in Claude Code logs |

**Sources:** [CLAUDE.md:79-87]()

### Example: aws-cost-ops Multi-Server Configuration

The `aws-cost-ops` plugin demonstrates complex MCP integration with three servers:

```json
"mcpServers": {
  "pricing": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.aws-pricing-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "costexp": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cost-explorer-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  },
  "cw": {
    "type": "stdio",
    "command": "uvx",
    "args": ["awslabs.cloudwatch-mcp-server@latest"],
    "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
  }
}
```

**Sources:** [.claude-plugin/marketplace.json:80-111]()

## Creating a New Skill

To add a new skill to an existing plugin:

1. **Create Skill Directory** - `plugins/{plugin}/skills/{skill-name}/`
2. **Create SKILL.md** - Main skill file with frontmatter and content
3. **Add Reference Docs** (optional) - `references/` subdirectory with pattern documentation
4. **Update marketplace.json** - Add skill path to plugin's `skills[]` array
5. **Bump Plugin Version** - Increment minor version (x.Y.0) for new skills
6. **Test Locally** - Create symlink in `.claude/skills/` if needed
7. **Commit Changes** - Include version bump

**Sources:** [CLAUDE.md:89-108](), [CLAUDE.md:110-117]()

## Creating a New Plugin

To create an entirely new plugin:

1. **Create Plugin Directory** - `plugins/{new-plugin-name}/`
2. **Create Skill Structure** - Follow standard skill directory layout
3. **Add Plugin Entry** - Add to `.claude-plugin/marketplace.json` plugins array
4. **Configure MCP Servers** (if needed) - Add `mcpServers` configuration
5. **Set Dependencies** - Typically depend on `aws-common` via `skills: ["aws-mcp-setup"]`
6. **Bump Marketplace Version** - Increment marketplace minor version (x.Y.0)
7. **Create Symlinks** - Add symlinks to `.claude/skills/` for testing
8. **Document Plugin** - Update documentation and README

**Sources:** [.claude-plugin/marketplace.json:1-152](), [CLAUDE.md:89-108]()

## Version Management Overview

Version management follows semantic versioning with specific rules for different change types. For complete version management guidelines, see [Version Management](#5.2).

| Change Type | Version Bump | Scope | Examples |
|-------------|--------------|-------|----------|
| **Minor** (x.Y.0) | Plugin or Marketplace | Structural changes | New skill, new dependency, new MCP server, new plugin |
| **Patch** (x.y.Z) | Plugin only | Content changes | Bug fixes, doc updates, typo fixes, description updates |

**Important Rules:**
- Adding/modifying `skills:` dependencies → Minor bump for affected plugins
- Adding new plugin → Minor bump for marketplace `metadata.version`
- All changes must include version bump before commit
- Version locations: `.claude-plugin/marketplace.json` at `metadata.version` and `plugins[].version`

**Sources:** [CLAUDE.md:89-108]()

## Testing and Validation Overview

The repository uses symlink-based local testing and multi-layer validation. For complete validation strategies, see [Validation and Quality Assurance](#5.3).

### Local Testing Approach

**Symlink Testing Architecture**

```mermaid
graph LR
    subgraph "Development Files"
        PluginSkills["plugins/aws-cdk/skills/aws-cdk-development/"]
        SkillMD["SKILL.md"]
        RefDocs["references/cdk-patterns.md"]
    end
    
    subgraph "Claude Code Discovery"
        ClaudeSkills[".claude/skills/"]
        Symlink["aws-cdk-development → symlink"]
        ClaudeLoad["Claude Code loads skills<br/>from .claude/skills/"]
    end
    
    subgraph "Testing Commands"
        CLI["claude -p 'prompt'<br/>Non-interactive"]
        IDE["/skills, /context<br/>Interactive IDE"]
        Verify["Test skill execution<br/>with real AWS calls"]
    end
    
    PluginSkills --> SkillMD
    PluginSkills --> RefDocs
    SkillMD -.symlinked to.-> Symlink
    Symlink --> ClaudeSkills
    ClaudeSkills --> ClaudeLoad
    ClaudeLoad --> CLI
    ClaudeLoad --> IDE
    CLI --> Verify
    IDE --> Verify
```

**Sources:** [CLAUDE.md:26-54]()

### Testing Commands

```bash
# Start Claude Code in repository root
cd /path/to/aws-skills
claude

# Interactive testing
/skills                    # List all available skills
/context                   # Show loaded context

# Non-interactive testing
claude -p "List all available skills in this project"
claude -p "Read the frontmatter of aws-cdk-development skill"
```

**Sources:** [CLAUDE.md:30-44]()

### Recreating Symlinks

If symlinks break during development:

```bash
cd .claude && rm -rf skills && mkdir skills
ln -s ../../plugins/aws-common/skills/aws-mcp-setup skills/
ln -s ../../plugins/aws-cdk/skills/aws-cdk-development skills/
ln -s ../../plugins/serverless-eda/skills/aws-serverless-eda skills/
ln -s ../../plugins/aws-agentic-ai/skills/aws-agentic-ai skills/
ln -s ../../plugins/aws-cost-ops/skills/aws-cost-operations skills/
```

**Sources:** [CLAUDE.md:46-54]()

## Key Files for Common Tasks

This table provides quick reference for common development tasks:

| Task | Files to Modify |
|------|-----------------|
| Add/update skill content | `plugins/{plugin}/skills/{skill}/SKILL.md` |
| Add reference documentation | `plugins/{plugin}/skills/{skill}/references/*.md` |
| Add MCP server to plugin | `.claude-plugin/marketplace.json` → `plugins[].mcpServers` |
| Change plugin metadata | `.claude-plugin/marketplace.json` → `plugins[]` properties |
| Update marketplace version | `.claude-plugin/marketplace.json` → `metadata.version` |
| Update plugin version | `.claude-plugin/marketplace.json` → `plugins[].version` |
| Add skill dependency | `plugins/{plugin}/skills/{skill}/SKILL.md` → `skills:` frontmatter |
| Configure tool permissions | `plugins/{plugin}/skills/{skill}/SKILL.md` → `allowed-tools:` frontmatter |
| Add lifecycle hooks | `plugins/{plugin}/skills/{skill}/SKILL.md` → `hooks:` frontmatter |

**Sources:** [CLAUDE.md:110-117](), [.claude-plugin/marketplace.json:1-152]()

## Contribution Workflow Summary

1. **Setup** - Fork repository, clone locally, verify symlinks in `.claude/skills/`
2. **Develop** - Make changes to plugin files, test with Claude Code CLI/IDE
3. **Validate** - Run any validation scripts, verify skill execution
4. **Version** - Determine change type (Minor/Patch), bump appropriate version
5. **Commit** - Commit with descriptive message including version bump
6. **Pull Request** - Submit PR with clear description of changes and rationale

For detailed development environment setup, see [Local Development Setup](#5.1). For version bump decision trees, see [Version Management](#5.2). For validation requirements, see [Validation and Quality Assurance](#5.3).

**Sources:** [CLAUDE.md:1-118](), [.claude-plugin/marketplace.json:1-152]()

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CLAUDE.md](CLAUDE.md)

</details>



This document provides instructions for setting up a local development environment to modify plugins, add new skills, or contribute to the AWS Skills marketplace. It covers the symlink-based development workflow that enables rapid iteration without requiring plugin reinstallation.

For information about version management when making changes, see [Version Management](#5.2). For validation and testing strategies, see [Validation and Quality Assurance](#5.3). For installing plugins as an end user, see [Installation](#2.1).

## Purpose and Scope

Local development uses symlinks from `.claude/skills/` to individual plugin skill directories in `plugins/*/skills/`. This architecture allows Claude Code to discover and load skills directly from the working tree, enabling contributors to test changes immediately without packaging or reinstalling plugins. The workflow supports both interactive testing (launching Claude Code CLI/IDE) and non-interactive testing (using `claude -p` commands).

Sources: [CLAUDE.md:26-54]()

## Symlink Architecture

### Directory Structure

The repository uses a dual-directory structure where plugin source files reside in `plugins/` but are exposed to Claude Code through `.claude/skills/` symlinks:

```mermaid
graph TB
    subgraph "Repository Root"
        Plugins["plugins/"]
        Claude[".claude/"]
    end
    
    subgraph "Plugin Source Directories"
        Common["plugins/aws-common/skills/aws-mcp-setup/"]
        CDK["plugins/aws-cdk/skills/aws-cdk-development/"]
        Cost["plugins/aws-cost-ops/skills/aws-cost-operations/"]
        Serverless["plugins/serverless-eda/skills/aws-serverless-eda/"]
        Agentic["plugins/aws-agentic-ai/skills/aws-agentic-ai/"]
    end
    
    subgraph "Claude Code Discovery Path"
        ClaudeSkills[".claude/skills/"]
        
        CommonLink[".claude/skills/aws-mcp-setup → symlink"]
        CDKLink[".claude/skills/aws-cdk-development → symlink"]
        CostLink[".claude/skills/aws-cost-operations → symlink"]
        ServerlessLink[".claude/skills/aws-serverless-eda → symlink"]
        AgenticLink[".claude/skills/aws-agentic-ai → symlink"]
    end
    
    subgraph "Claude Code Runtime"
        Claude_Code["Claude Code CLI/IDE"]
        SkillLoader["Skill Discovery Engine"]
    end
    
    Plugins --> Common
    Plugins --> CDK
    Plugins --> Cost
    Plugins --> Serverless
    Plugins --> Agentic
    
    Claude --> ClaudeSkills
    ClaudeSkills --> CommonLink
    ClaudeSkills --> CDKLink
    ClaudeSkills --> CostLink
    ClaudeSkills --> ServerlessLink
    ClaudeSkills --> AgenticLink
    
    CommonLink -.symlink.-> Common
    CDKLink -.symlink.-> CDK
    CostLink -.symlink.-> Cost
    ServerlessLink -.symlink.-> Serverless
    AgenticLink -.symlink.-> Agentic
    
    Claude_Code --> SkillLoader
    SkillLoader --> ClaudeSkills
```

**Directory Structure: Symlink-Based Local Development**

Each skill directory contains a `SKILL.md` file with frontmatter configuration and optional `references/*.md` documentation. Claude Code reads from `.claude/skills/` which symlinks to the actual source files in `plugins/*/skills/`, allowing changes to be reflected immediately without reinstalling.

Sources: [CLAUDE.md:11-24](), [CLAUDE.md:46-54]()

### How Symlinks Enable Local Development

The symlink approach provides several benefits:

| Benefit | Explanation |
|---------|-------------|
| **Instant Reflection** | Changes to `plugins/*/skills/*/SKILL.md` are immediately visible to Claude Code without plugin reinstallation |
| **Version Control** | Source files remain in `plugins/` where they're tracked by git, while `.claude/` is used only for discovery |
| **Multi-Skill Development** | All five plugins' skills are simultaneously available for testing dependencies and interactions |
| **Isolation** | `.claude/settings.local.json` and `CLAUDE.local.md` are gitignored, allowing developer-specific configurations |

Sources: [CLAUDE.md:26-38](), [.gitignore:102-103]()

## Setting Up Local Development

### Prerequisites

Before setting up local development, ensure you have:

- Claude Code CLI or IDE installed
- Git repository cloned to a local directory
- Bash or compatible shell (for symlink commands)
- Optional: AWS credentials configured (for testing AWS MCP tools)

### Creating the Symlink Structure

The `.claude/skills/` directory must contain symlinks to each plugin's skill directory. Use the following commands to create the structure:

```bash
# Navigate to repository root
cd /path/to/aws-skills

# Create .claude/skills directory (if it doesn't exist)
mkdir -p .claude/skills

# Create symlinks for all five plugins
cd .claude/skills
ln -s ../../plugins/aws-common/skills/aws-mcp-setup .
ln -s ../../plugins/aws-cdk/skills/aws-cdk-development .
ln -s ../../plugins/aws-cost-ops/skills/aws-cost-operations .
ln -s ../../plugins/serverless-eda/skills/aws-serverless-eda .
ln -s ../../plugins/aws-agentic-ai/skills/aws-agentic-ai .
```

Sources: [CLAUDE.md:46-54]()

### Verifying Symlink Creation

After creating symlinks, verify they point to valid directories:

```bash
cd .claude/skills
ls -lah

# Expected output:
# aws-mcp-setup -> ../../plugins/aws-common/skills/aws-mcp-setup
# aws-cdk-development -> ../../plugins/aws-cdk/skills/aws-cdk-development
# aws-cost-operations -> ../../plugins/aws-cost-ops/skills/aws-cost-operations
# aws-serverless-eda -> ../../plugins/serverless-eda/skills/aws-serverless-eda
# aws-agentic-ai -> ../../plugins/aws-agentic-ai/skills/aws-agentic-ai
```

Each symlink should point to a directory containing a `SKILL.md` file.

Sources: [CLAUDE.md:46-54]()

## Development Workflow

### Skill Loading and Execution Flow

```mermaid
graph TB
    subgraph "Developer Actions"
        Dev["Developer"]
        Edit["Edit plugins/*/skills/*/SKILL.md"]
        EditRef["Edit plugins/*/skills/*/references/*.md"]
        Launch["Launch: claude or claude -p"]
    end
    
    subgraph "File System"
        SourceSKILL["plugins/{plugin}/skills/{skill}/SKILL.md"]
        SourceRefs["plugins/{plugin}/skills/{skill}/references/*.md"]
        Symlink[".claude/skills/{skill} → symlink"]
    end
    
    subgraph "Claude Code Runtime"
        Discovery["Skill Discovery<br/>Scan .claude/skills/"]
        Parser["SKILL.md Parser<br/>Read frontmatter + content"]
        Context["Execution Context<br/>Fork: true, Model: sonnet"]
        Deps["Dependency Resolution<br/>Auto-load skills: [...]"]
    end
    
    subgraph "Skill Components"
        Frontmatter["Frontmatter Config<br/>name, description, context,<br/>model, skills, allowed-tools, hooks"]
        Content["Skill Content<br/>Instructions for Claude"]
        References["Reference Docs<br/>Detailed patterns/guides"]
    end
    
    subgraph "Verification Commands"
        VerifySkills["/skills command<br/>List available skills"]
        VerifyContext["/context command<br/>Show loaded context"]
        NonInteractive["claude -p 'List all available skills'"]
    end
    
    Dev --> Edit
    Dev --> EditRef
    Dev --> Launch
    
    Edit --> SourceSKILL
    EditRef --> SourceRefs
    
    SourceSKILL -.symlinked via.-> Symlink
    SourceRefs -.accessible via.-> Symlink
    
    Launch --> Discovery
    Discovery --> Symlink
    Symlink --> Parser
    
    Parser --> Frontmatter
    Parser --> Content
    Parser --> References
    
    Frontmatter --> Context
    Frontmatter --> Deps
    
    Context --> VerifySkills
    Context --> VerifyContext
    Launch --> NonInteractive
```

**Development Workflow: Edit-Launch-Verify Cycle**

This diagram shows the complete cycle from editing source files to verifying they load correctly in Claude Code. Changes to files in `plugins/` are immediately visible through symlinks in `.claude/skills/`, where Claude Code discovers and parses them.

Sources: [CLAUDE.md:26-44]()

### Starting Claude Code

To begin local development, launch Claude Code from the repository root:

```bash
# Navigate to repository root
cd /path/to/aws-skills

# Launch Claude Code CLI (interactive mode)
claude

# Skills automatically load from .claude/skills/
```

When Claude Code starts, it automatically discovers and loads all skills from `.claude/skills/`. The symlink structure ensures it reads the latest versions from `plugins/`.

Sources: [CLAUDE.md:30-33]()

### Verifying Skills Load

After launching Claude Code, verify skills loaded correctly:

**Interactive verification:**
```bash
# Inside Claude Code CLI/IDE:
/skills           # Lists all available skills
/context          # Shows loaded context including skills
```

**Non-interactive verification:**
```bash
# From terminal (without launching interactive session):
claude -p "List all available skills in this project"
claude -p "Read the frontmatter of aws-cdk-development skill"
```

Sources: [CLAUDE.md:36-44]()

### Making and Testing Changes

The typical development cycle:

1. **Edit skill content:** Modify `plugins/{plugin}/skills/{skill}/SKILL.md`
2. **Edit references (optional):** Add/update `plugins/{plugin}/skills/{skill}/references/*.md`
3. **Restart Claude Code:** Exit and relaunch to reload changed skills
4. **Test skill behavior:** Use `/skills {skill-name}` or `claude -p` commands
5. **Iterate:** Repeat steps 1-4 until desired behavior achieved

Example workflow:
```bash
# 1. Edit skill file
vim plugins/aws-cdk/skills/aws-cdk-development/SKILL.md

# 2. Test non-interactively
claude -p "Using aws-cdk-development skill, explain CDK best practices"

# 3. Test interactively
claude
> /skills aws-cdk-development
> Ask me about CDK best practices
```

Sources: [CLAUDE.md:26-44]()

## Testing Skills Locally

### Interactive Testing

Launch Claude Code in interactive mode for conversational testing:

```bash
cd /path/to/aws-skills
claude

# Test skill loading
> /skills

# Test specific skill
> /skills aws-cdk-development

# Test skill with conversation
> I need to create a Lambda function using CDK. What are the best practices?
```

Interactive mode is ideal for:
- Testing skill responses to varied prompts
- Verifying dependency auto-loading (`skills:` frontmatter field)
- Testing hook execution (`PreToolUse` hooks)
- Observing fork context behavior (`context: fork`)

Sources: [CLAUDE.md:30-38]()

### Non-Interactive Testing

Use `claude -p` for automated or scripted testing:

```bash
# Test skill availability
claude -p "List all available skills in this project"

# Test skill metadata parsing
claude -p "Read the frontmatter of aws-cdk-development skill"

# Test skill content
claude -p "Using aws-mcp-setup skill, explain MCP configuration options"

# Test skill with specific question
claude -p "Using aws-cdk-development, show me Lambda function best practices"
```

Non-interactive mode is ideal for:
- Automated testing in CI/CD pipelines
- Quick verification after changes
- Regression testing skill responses
- Documentation generation from skill content

Sources: [CLAUDE.md:40-44]()

### Testing Skill Dependencies

When testing skills that declare dependencies in the `skills:` frontmatter field, verify auto-loading works:

```bash
# Test serverless-eda (depends on aws-mcp-setup and aws-cdk-development)
claude -p "Using aws-serverless-eda skill, explain event-driven patterns"

# Verify both dependencies loaded automatically:
# 1. aws-mcp-setup should provide MCP tools
# 2. aws-cdk-development should provide CDK patterns
```

The skill loader automatically includes dependencies before executing the requested skill, creating a complete context.

Sources: [CLAUDE.md:56-77]()

## Troubleshooting

### Recreating Broken Symlinks

If symlinks become broken (e.g., after directory reorganization or repository clone), recreate them:

```bash
cd /path/to/aws-skills/.claude

# Remove broken symlinks
rm -rf skills

# Recreate directory and symlinks
mkdir skills
cd skills
ln -s ../../plugins/aws-common/skills/aws-mcp-setup .
ln -s ../../plugins/aws-cdk/skills/aws-cdk-development .
ln -s ../../plugins/aws-cost-ops/skills/aws-cost-operations .
ln -s ../../plugins/serverless-eda/skills/aws-serverless-eda .
ln -s ../../plugins/aws-agentic-ai/skills/aws-agentic-ai .

# Verify recreation
ls -lah
```

Sources: [CLAUDE.md:46-54]()

### Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| **Skills not loading** | `/skills` shows empty list | Verify symlinks exist and point to valid directories |
| **Stale skill content** | Changes not reflected | Restart Claude Code to reload skills |
| **Missing dependencies** | Skill references unavailable dependency | Ensure all five plugin symlinks are created |
| **Permission errors** | Cannot read skill files | Check file permissions on `plugins/*/skills/*/SKILL.md` |

### Verifying Symlink Integrity

```bash
# Check if symlinks point to actual files
cd .claude/skills
for skill in *; do
    if [ -L "$skill" ]; then
        target=$(readlink "$skill")
        if [ -f "$skill/SKILL.md" ]; then
            echo "✓ $skill -> $target (valid)"
        else
            echo "✗ $skill -> $target (broken: SKILL.md missing)"
        fi
    fi
done
```

This script verifies each symlink points to a directory containing `SKILL.md`.

Sources: [CLAUDE.md:46-54]()

## File Structure Reference

### Skill Directory Layout

Each plugin skill directory follows this structure:

```
plugins/{plugin}/skills/{skill}/
├── SKILL.md                      # Main skill file (required)
├── references/                   # Optional documentation
│   ├── pattern-guide.md
│   ├── best-practices.md
│   └── examples.md
└── README.md                     # Optional skill overview
```

### Key Files for Local Development

| File Path | Purpose | Edit Frequency |
|-----------|---------|----------------|
| `plugins/*/skills/*/SKILL.md` | Skill definition and frontmatter | High |
| `plugins/*/skills/*/references/*.md` | Detailed reference documentation | Medium |
| `.claude/skills/*` | Symlinks (read-only, regenerate if broken) | Low |
| `.claude/settings.local.json` | Developer-specific settings (gitignored) | Low |
| `CLAUDE.md` | Repository guidance for Claude Code | Medium |

Sources: [CLAUDE.md:21-24](), [.gitignore:102-103]()

## Next Steps

After setting up local development:

1. **Understand version management:** See [Version Management](#5.2) for rules on bumping versions when making changes
2. **Learn validation:** See [Validation and Quality Assurance](#5.3) for multi-layer validation strategy
3. **Explore plugin structure:** See [Marketplace and Plugin System](#3.1) for plugin architecture details
4. **Study skill frontmatter:** See [Skills and Execution Model](#3.2) for frontmatter configuration options

Sources: [CLAUDE.md:1-118]()

---

# Page: Version Management

# Version Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)

</details>



This document defines the version management strategy for the AWS Skills marketplace and its constituent plugins. It covers the two-level versioning system (marketplace-level and plugin-level), rules for determining Minor vs Patch version bumps, and the mandatory version bump policy for all content modifications. For instructions on setting up local development with symlinks, see [Local Development Setup](#5.1). For quality gates that trigger before version releases, see [Validation and Quality Assurance](#5.3).

## Two-Level Versioning System

The AWS Skills system employs a two-level versioning hierarchy: the marketplace itself has a version, and each plugin within the marketplace maintains its own independent version.

### Marketplace Version Structure

```mermaid
graph TB
    subgraph "marketplace.json Structure"
        Root["marketplace.json<br/>(Root)"]
        Metadata["metadata.version<br/>Current: 2.2.0"]
        Plugins["plugins[]<br/>(Array of 5 plugins)"]
        
        Root --> Metadata
        Root --> Plugins
    end
    
    subgraph "Plugin Version Fields"
        Common["aws-common<br/>version: 1.0.0"]
        CDK["aws-cdk<br/>version: 1.2.0"]
        CostOps["aws-cost-ops<br/>version: 1.2.0"]
        Serverless["serverless-eda<br/>version: 1.2.0"]
        Agentic["aws-agentic-ai<br/>version: 1.2.0"]
        
        Plugins --> Common
        Plugins --> CDK
        Plugins --> CostOps
        Plugins --> Serverless
        Plugins --> Agentic
    end
    
    Note1["marketplace.version bumps<br/>when plugins[] array changes<br/>(new plugin added/removed)"]
    Note2["plugin.version bumps<br/>when plugin content changes<br/>(skills, docs, config)"]
    
    Metadata -.-> Note1
    Common -.-> Note2
    CDK -.-> Note2
```

**Two-Level Versioning System**

The marketplace version at `metadata.version` (currently `2.2.0`) tracks structural changes to the plugin registry, while individual `plugins[].version` fields track content changes within each plugin. The version differential pattern is evident: `aws-common` remains at `1.0.0` indicating foundational stability, while domain plugins have evolved to `1.2.0`.

**Sources:** [.claude-plugin/marketplace.json:1-152]()

### Version Location in Code

| Version Type | JSON Path | Current Value | Purpose |
|--------------|-----------|---------------|---------|
| Marketplace | `metadata.version` | `2.2.0` | Tracks plugin registry changes |
| aws-common | `plugins[0].version` | `1.0.0` | Foundational plugin versioning |
| aws-cdk | `plugins[1].version` | `1.2.0` | CDK plugin versioning |
| aws-cost-ops | `plugins[2].version` | `1.2.0` | Cost operations plugin versioning |
| serverless-eda | `plugins[3].version` | `1.2.0` | Serverless plugin versioning |
| aws-agentic-ai | `plugins[4].version` | `1.2.0` | Agentic AI plugin versioning |

**Sources:** [.claude-plugin/marketplace.json:9](), [.claude-plugin/marketplace.json:15](), [.claude-plugin/marketplace.json:34](), [.claude-plugin/marketplace.json:65](), [.claude-plugin/marketplace.json:116](), [.claude-plugin/marketplace.json:135]()

## Version Bump Rules

The system follows semantic versioning principles with two bump categories: Minor (x.Y.0) for structural changes and Patch (x.y.Z) for content changes.

```mermaid
graph TD
    Change{"Change Type?"}
    
    Structural["Structural Change"]
    Content["Content Change"]
    
    Change --> Structural
    Change --> Content
    
    subgraph "Minor Bump (x.Y.0)"
        NewSkill["New skill added<br/>Add to plugins[].skills[]"]
        NewDep["New skill dependency<br/>Add to SKILL.md skills:"]
        NewMCP["New MCP server<br/>Add to plugins[].mcpServers"]
        NewPlugin["New plugin added<br/>Add to plugins[]"]
        NewHook["New hook added<br/>Add to SKILL.md hooks:"]
        
        Structural --> NewSkill
        Structural --> NewDep
        Structural --> NewMCP
        Structural --> NewPlugin
        Structural --> NewHook
    end
    
    subgraph "Patch Bump (x.y.Z)"
        BugFix["Bug fixes<br/>Logic corrections"]
        DocUpdate["Documentation updates<br/>SKILL.md content, references/*.md"]
        ConfigTweak["Configuration tweaks<br/>Metadata changes"]
        Typo["Typo fixes<br/>Text corrections"]
        
        Content --> BugFix
        Content --> DocUpdate
        Content --> ConfigTweak
        Content --> Typo
    end
    
    BumpPlugin["Bump plugins[n].version"]
    BumpMarket["Bump metadata.version"]
    
    NewSkill --> BumpPlugin
    NewDep --> BumpPlugin
    NewMCP --> BumpPlugin
    NewHook --> BumpPlugin
    NewPlugin --> BumpMarket
    
    BugFix --> BumpPlugin
    DocUpdate --> BumpPlugin
    ConfigTweak --> BumpPlugin
    Typo --> BumpPlugin
```

**Version Bump Decision Tree**

This diagram maps change types to version bump actions. Structural changes (new skills, dependencies, MCP servers, hooks) trigger Minor bumps. Content changes (bug fixes, documentation, configuration, typos) trigger Patch bumps. Only adding a new plugin triggers a marketplace version bump.

**Sources:** [CLAUDE.md:89-108]()

### Minor Bump Triggers (x.Y.0)

Minor version bumps occur when plugin capabilities expand or structural configuration changes:

| Trigger | Affected File | Example |
|---------|---------------|---------|
| **New skill added** | `plugins[].skills[]` array | Adding `./skills/new-skill` to aws-cdk plugin |
| **New skill dependency** | `skills/<skill>/SKILL.md` frontmatter | Adding `aws-cdk-development` to `skills:` list |
| **New MCP server** | `plugins[].mcpServers` object | Adding `stepfunctions` server to aws-cdk plugin |
| **New hook configuration** | `skills/<skill>/SKILL.md` frontmatter | Adding `PreToolUse` hook with matcher |
| **New plugin** | `plugins[]` array | Adding sixth plugin to marketplace |

**Examples of Minor Bump Changes:**

```yaml
# Adding skill dependency in SKILL.md frontmatter → Minor bump
---
name: aws-serverless-eda
skills:
  - aws-mcp-setup           # Existing
  - aws-cdk-development     # NEW → Triggers minor bump
---
```

```json
// Adding MCP server in marketplace.json → Minor bump
{
  "name": "aws-cdk",
  "version": "1.3.0",  // Bumped from 1.2.0
  "mcpServers": {
    "cdk": { ... },
    "stepfunctions": { ... }  // NEW server
  }
}
```

**Sources:** [CLAUDE.md:99-100](), [.claude-plugin/marketplace.json:49-60]()

### Patch Bump Triggers (x.y.Z)

Patch version bumps occur when content improves without structural changes:

| Trigger | Affected Files | Example |
|---------|----------------|---------|
| **Bug fixes** | Any plugin code/scripts | Fixing broken validation logic |
| **Documentation updates** | `SKILL.md`, `references/*.md` | Updating best practices content |
| **Configuration tweaks** | `marketplace.json` metadata | Updating description text |
| **Typo fixes** | Any text content | Correcting spelling errors |

**Examples of Patch Bump Changes:**

```markdown
<!-- Updating SKILL.md content → Patch bump -->
## CDK Best Practices

- Use `NodejsFunction` for TypeScript/JavaScript Lambdas
- Use `PythonFunction` for Python Lambdas (UPDATED TEXT)
```

```json
// Updating plugin metadata → Patch bump
{
  "name": "aws-cdk",
  "version": "1.2.1",  // Bumped from 1.2.0
  "description": "Comprehensive AWS development skills including CDK best practices...",
  // Description text updated, no structural changes
}
```

**Sources:** [CLAUDE.md:100]()

## When to Bump Which Version

```mermaid
graph TB
    ModType{"Modification Type?"}
    
    PluginContent["Plugin Content Modified<br/>(skills, docs, config)"]
    RegistryStructure["Plugin Registry Modified<br/>(plugins[] array)"]
    
    ModType --> PluginContent
    ModType --> RegistryStructure
    
    PluginContent --> ChangeType{"Change Type?"}
    
    Structural["Structural:<br/>New skill/dependency/MCP/hook"]
    Content["Content:<br/>Bug fix/doc/config/typo"]
    
    ChangeType --> Structural
    ChangeType --> Content
    
    Structural --> MinorPlugin["Bump plugins[n].version<br/>x.Y.0 → x.(Y+1).0<br/>Reset Z to 0"]
    Content --> PatchPlugin["Bump plugins[n].version<br/>x.y.Z → x.y.(Z+1)"]
    
    RegistryStructure --> AddPlugin{"Plugin Added?"}
    AddPlugin -->|Yes| MinorMarket["Bump metadata.version<br/>x.Y.0 → x.(Y+1).0"]
    AddPlugin -->|No Remove| MajorMarket["Bump metadata.version<br/>(Major change)"]
    
    Example1["Example: Add aws-cdk-development<br/>to serverless-eda skills:<br/>serverless-eda 1.2.0 → 1.3.0<br/>marketplace stays 2.2.0"]
    
    Example2["Example: Fix typo in aws-cdk SKILL.md:<br/>aws-cdk 1.2.0 → 1.2.1<br/>marketplace stays 2.2.0"]
    
    Example3["Example: Add aws-database plugin:<br/>marketplace 2.2.0 → 2.3.0<br/>aws-database starts at 1.0.0"]
    
    MinorPlugin -.-> Example1
    PatchPlugin -.-> Example2
    MinorMarket -.-> Example3
```

**Version Bump Target Decision Tree**

This diagram determines which version field to bump based on modification scope. Plugin content changes affect only that plugin's version. Adding a new plugin to the registry bumps the marketplace version while the new plugin starts at `1.0.0`.

**Sources:** [CLAUDE.md:102-108](), [.claude-plugin/marketplace.json:9]()

### Plugin Version Bumping

**Rule:** Bump `plugins[n].version` whenever content within that plugin changes.

**Affected Files Mapping:**

| Modified File Pattern | Bump Target | Bump Type |
|----------------------|-------------|-----------|
| `plugins/<plugin>/skills/<skill>/SKILL.md` (frontmatter) | `plugins[n].version` | Minor |
| `plugins/<plugin>/skills/<skill>/SKILL.md` (content) | `plugins[n].version` | Patch |
| `plugins/<plugin>/skills/<skill>/references/*.md` | `plugins[n].version` | Patch |
| `plugins/<plugin>/scripts/*.sh` | `plugins[n].version` | Patch |
| `.claude-plugin/marketplace.json` (plugin's `mcpServers`) | `plugins[n].version` | Minor |
| `.claude-plugin/marketplace.json` (plugin's `description`) | `plugins[n].version` | Patch |

**Sources:** [CLAUDE.md:113-117](), [.claude-plugin/marketplace.json:11-150]()

### Marketplace Version Bumping

**Rule:** Bump `metadata.version` only when the `plugins[]` array structure changes.

**Triggers:**
- **Adding new plugin:** Minor bump `2.2.0` → `2.3.0`
- **Removing plugin:** Major bump `2.2.0` → `3.0.0` (breaking change)
- **Reordering plugins:** No version change (non-functional change)

**Plugin Content Changes Do NOT Affect Marketplace Version:**

```json
// This change bumps aws-cdk from 1.2.0 → 1.2.1
// Marketplace version stays 2.2.0
{
  "metadata": {
    "version": "2.2.0"  // UNCHANGED
  },
  "plugins": [
    {
      "name": "aws-cdk",
      "version": "1.2.1"  // BUMPED
    }
  ]
}
```

**Sources:** [CLAUDE.md:105-106](), [.claude-plugin/marketplace.json:8-10]()

## Mandatory Version Bump Policy

```mermaid
graph LR
    Dev["Developer Makes Changes"]
    Check{"Modified Plugin Content?"}
    Bump["Bump Appropriate Version<br/>Before Committing"]
    Commit["git commit"]
    
    Dev --> Check
    Check -->|Yes| Bump
    Check -->|No| Commit
    Bump --> Commit
    
    Policy["POLICY: Always bump versions<br/>when modifying plugin content<br/>before committing"]
    
    Bump -.follows.-> Policy
```

**Mandatory Version Bump Workflow**

All plugin content modifications require a version bump before committing. This ensures version numbers accurately reflect the state of the codebase.

**Policy Statement:** "Always bump versions when modifying plugin content before committing." [CLAUDE.md:108]()

### Pre-Commit Checklist

Before committing changes to any plugin:

1. **Identify modified files:**
   ```bash
   git status | grep "plugins/"
   ```

2. **Determine bump type:**
   - Modified `SKILL.md` frontmatter (`skills:`, `hooks:`, `allowed-tools:`) → Minor
   - Modified `SKILL.md` content or `references/*.md` → Patch
   - Added MCP server to `marketplace.json` → Minor
   - Fixed bugs or typos → Patch

3. **Update version in `.claude-plugin/marketplace.json`:**
   ```json
   {
     "plugins": [
       {
         "name": "affected-plugin",
         "version": "x.y.z"  // Update this field
       }
     ]
   }
   ```

4. **Commit with descriptive message:**
   ```bash
   git commit -m "feat(aws-cdk): add Step Functions MCP server
   
   Bump aws-cdk version 1.2.0 → 1.3.0 (minor)"
   ```

**Sources:** [CLAUDE.md:108]()

## Version Differential Strategy

The current version distribution reveals a deliberate stability strategy:

| Plugin | Version | Rationale |
|--------|---------|-----------|
| aws-common | `1.0.0` | Foundational dependency - kept stable to minimize downstream impact |
| aws-cdk | `1.2.0` | Domain plugin - evolves with CDK best practices |
| aws-cost-ops | `1.2.0` | Domain plugin - evolves with operational patterns |
| serverless-eda | `1.2.0` | Domain plugin - evolves with architectural patterns |
| aws-agentic-ai | `1.2.0` | Domain plugin - evolves with Bedrock capabilities |

**Strategy Rationale:**

The `aws-common` plugin at `1.0.0` provides the foundational `aws-mcp-setup` skill that all other plugins depend on via the `skills:` frontmatter field. Keeping this plugin at `1.0.0` signals API stability - changes to `aws-common` would force all dependent plugins to update their dependency declarations. Domain plugins at `1.2.0` indicate they have evolved through two minor releases (adding features, dependencies, or MCP servers) without requiring breaking changes to the foundation.

**Sources:** [.claude-plugin/marketplace.json:15](), [.claude-plugin/marketplace.json:34](), [.claude-plugin/marketplace.json:65](), [.claude-plugin/marketplace.json:116](), [.claude-plugin/marketplace.json:135]()

## Common Version Bump Scenarios

### Scenario 1: Adding Skill Dependency

**Change:** Add `aws-cdk-development` to `serverless-eda` skill's dependencies.

```yaml
# plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md
---
name: aws-serverless-eda
skills:
  - aws-mcp-setup           # Existing
  - aws-cdk-development     # NEW
---
```

**Version Impact:**
- Bump `plugins[3].version` (serverless-eda): `1.2.0` → `1.3.0` (Minor)
- Marketplace version: `2.2.0` (unchanged)

**Rationale:** Adding a skill dependency is a structural change that expands the skill's capabilities.

**Sources:** [CLAUDE.md:99]()

### Scenario 2: Updating Documentation Content

**Change:** Update CDK best practices documentation.

```markdown
<!-- plugins/aws-cdk/skills/aws-cdk-development/references/cdk-patterns.md -->
## Lambda Development

Updated guidance on NodejsFunction construct...
```

**Version Impact:**
- Bump `plugins[1].version` (aws-cdk): `1.2.0` → `1.2.1` (Patch)
- Marketplace version: `2.2.0` (unchanged)

**Rationale:** Documentation content updates are non-structural changes.

**Sources:** [CLAUDE.md:100]()

### Scenario 3: Adding New Plugin

**Change:** Add `aws-database` plugin for RDS/DynamoDB expertise.

```json
// .claude-plugin/marketplace.json
{
  "metadata": {
    "version": "2.3.0"  // Bumped from 2.2.0
  },
  "plugins": [
    // ... existing 5 plugins ...
    {
      "name": "aws-database",
      "version": "1.0.0",  // New plugin starts at 1.0.0
      "source": "./plugins/aws-database"
    }
  ]
}
```

**Version Impact:**
- Bump `metadata.version`: `2.2.0` → `2.3.0` (Minor)
- New plugin starts at: `1.0.0`

**Rationale:** Adding a plugin is a marketplace-level structural change.

**Sources:** [CLAUDE.md:105]()

### Scenario 4: Adding MCP Server to Existing Plugin

**Change:** Add Step Functions MCP server to `aws-cdk` plugin.

```json
// .claude-plugin/marketplace.json
{
  "name": "aws-cdk",
  "version": "1.3.0",  // Bumped from 1.2.0
  "mcpServers": {
    "cdk": { ... },
    "sfn": {  // NEW
      "type": "stdio",
      "command": "uvx",
      "args": ["awslabs.step-functions-mcp-server@latest"]
    }
  }
}
```

**Version Impact:**
- Bump `plugins[1].version` (aws-cdk): `1.2.0` → `1.3.0` (Minor)
- Marketplace version: `2.2.0` (unchanged)

**Rationale:** Adding an MCP server expands plugin capabilities through new tool integrations.

**Sources:** [CLAUDE.md:99](), [.claude-plugin/marketplace.json:49-60]()

## Version Verification

After bumping versions, verify consistency:

```bash
# Check marketplace version
jq '.metadata.version' .claude-plugin/marketplace.json

# Check all plugin versions
jq '.plugins[] | {name: .name, version: .version}' .claude-plugin/marketplace.json

# Verify specific plugin version
jq '.plugins[] | select(.name=="aws-cdk") | .version' .claude-plugin/marketplace.json
```

**Expected Output for Current State:**
```
Marketplace: 2.2.0
aws-common: 1.0.0
aws-cdk: 1.2.0
aws-cost-ops: 1.2.0
serverless-eda: 1.2.0
aws-agentic-ai: 1.2.0
```

**Sources:** [.claude-plugin/marketplace.json:1-152]()

---

# Page: Validation and Quality Assurance

# Validation and Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CLAUDE.md](CLAUDE.md)
- [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md](plugins/aws-cdk/skills/aws-cdk-development/SKILL.md)

</details>



This document describes the validation and quality assurance mechanisms used throughout the AWS Skills for Claude Code system. It covers the three-layer validation strategy for infrastructure code, lifecycle hooks for runtime safety, testing infrastructure, and quality gates that prevent defects from reaching production.

For information about local development workflows, see [Local Development Setup](#5.1). For version management policies, see [Version Management](#5.2).

## Purpose and Scope

The validation system enforces quality through multiple checkpoints:
- **Multi-layer validation** that catches issues at different stages (IDE → synthesis → pre-commit)
- **Lifecycle hooks** that verify execution context before destructive operations
- **Testing infrastructure** for unit and integration tests
- **Quality gates** that enforce mandatory checks before commits

This system is primarily implemented in the `aws-cdk` plugin but serves as a reference pattern for all plugins.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:132-200](), [CLAUDE.md:56-109]()

## Multi-Layer Validation Strategy

The system employs a progressive validation approach with three distinct layers, each catching different categories of issues:

### Validation Flow Diagram

```mermaid
graph TB
    subgraph "Developer Workspace"
        Code["Developer writes<br/>CDK code"]
        Save["File save"]
    end
    
    subgraph "Layer 1: IDE Feedback"
        VSCode["VS Code<br/>cdk-nag-validator extension"]
        RealTime["Real-time validation<br/>on file save"]
    end
    
    subgraph "Layer 2: Synthesis-Time"
        CDKSynth["cdk synth command"]
        Aspects["cdk-nag Aspects<br/>AwsSolutionsChecks"]
        SynthOutput["CloudFormation template<br/>+ validation report"]
    end
    
    subgraph "Layer 3: Pre-Commit"
        Build["npm run build<br/>or language build"]
        Test["npm test<br/>or pytest/mvn test"]
        ValidateScript["scripts/validate-stack.sh"]
        PreCommit["Pre-commit checks pass"]
    end
    
    subgraph "Deployment Gate"
        Hook["PreToolUse hook:<br/>aws sts get-caller-identity"]
        Deploy["cdk deploy"]
    end
    
    Code --> Save
    Save --> VSCode
    VSCode --> RealTime
    RealTime -.feedback loop.-> Code
    
    Code --> CDKSynth
    CDKSynth --> Aspects
    Aspects --> SynthOutput
    SynthOutput -.issues found.-> Code
    
    SynthOutput --> Build
    Build --> Test
    Test --> ValidateScript
    ValidateScript --> PreCommit
    PreCommit -.failures.-> Code
    
    PreCommit --> Hook
    Hook --> Deploy
    
    style RealTime fill:#f9f9f9
    style Aspects fill:#f9f9f9
    style PreCommit fill:#f9f9f9
    style Hook fill:#f9f9f9
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:132-200]()

### Validation Layer Comparison

| Layer | Stage | Scope | Tools | Speed | Mandatory |
|-------|-------|-------|-------|-------|-----------|
| **Layer 1** | IDE | Single file | cdk-nag extension | Instant | Optional |
| **Layer 2** | Synthesis | Full stack | cdk-nag Aspects | Seconds | Required |
| **Layer 3** | Pre-commit | Full project | build + test + scripts | Minutes | Required |

Each layer provides progressively broader coverage with increasing execution time.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:136-200]()

## Layer 1: Real-Time IDE Feedback

Layer 1 provides immediate feedback during code authorship through IDE integration.

### cdk-nag Installation

```bash
npm install --save-dev cdk-nag
```

The `cdk-nag` package provides synthesis-time validation rules that check for AWS best practices, security issues, and common misconfigurations.

### VS Code Extension

For TypeScript/JavaScript CDK projects, developers can install the optional CDK NAG Validator extension:
- **Extension ID**: `alphacrack.cdk-nag-validator`
- **Trigger**: Validates on file save
- **Benefit**: Catches issues without running `cdk synth`

This extension is optional but recommended for faster feedback loops.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:136-157]()

## Layer 2: Synthesis-Time Validation

Layer 2 is the mandatory validation checkpoint that all CDK code must pass.

### Aspects Integration

```typescript
import { Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks } from 'cdk-nag';

const app = new App();
Aspects.of(app).add(new AwsSolutionsChecks());
```

This integration runs automatically during `cdk synth` and validates the entire stack against `AwsSolutionsChecks` rules.

### Synthesis Execution

```bash
cdk synth  # cdk-nag runs automatically via Aspects
```

The synthesis process:
1. Constructs the CDK application
2. Applies all registered Aspects
3. Executes cdk-nag validation rules
4. Generates CloudFormation template
5. Reports any violations

### Suppression Rules

When specific violations are legitimate, they can be suppressed with documented justification:

```typescript
import { NagSuppressions } from 'cdk-nag';

NagSuppressions.addResourceSuppressions(resource, [
  {
    id: 'AwsSolutions-L1',
    reason: 'Lambda@Edge requires specific runtime for CloudFront compatibility'
  }
]);
```

**Critical**: Every suppression must include a `reason` field explaining why the exception is necessary.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:159-177]()

## Layer 3: Pre-Commit Checks

Layer 3 provides comprehensive project-level validation before code is committed.

### Validation Sequence

```mermaid
graph LR
    subgraph "Build Phase"
        Compile["npm run build<br/>TypeScript compilation<br/>or language-specific build"]
    end
    
    subgraph "Test Phase"
        Unit["Unit tests<br/>npm test"]
        Integration["Integration tests"]
        Coverage["Coverage tracking<br/>.nyc_output/"]
    end
    
    subgraph "Validation Phase"
        Script["scripts/validate-stack.sh"]
        LangDetect["Language detection"]
        TemplateAnalysis["Template size analysis"]
        ResourceCount["Resource count check"]
        SynthVerify["Synthesis verification"]
    end
    
    subgraph "Quality Gate"
        Pass["All checks passed"]
        Commit["Ready for commit"]
    end
    
    Compile --> Unit
    Unit --> Integration
    Integration --> Coverage
    Coverage --> Script
    
    Script --> LangDetect
    LangDetect --> TemplateAnalysis
    TemplateAnalysis --> ResourceCount
    ResourceCount --> SynthVerify
    
    SynthVerify --> Pass
    Pass --> Commit
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:179-200]()

### Build Verification

The build phase ensures code compiles successfully:

```bash
npm run build  # TypeScript/JavaScript
# or
pytest         # Python
mvn test       # Java
dotnet build   # C#
go build       # Go
```

Build failures prevent further validation steps.

### Test Execution

Testing infrastructure includes:
- **Unit tests**: Test individual constructs in isolation
- **Integration tests**: Test stack synthesis and resource relationships
- **Snapshot tests**: Validate CloudFormation template structure

Test artifacts are stored in:
- `coverage/` - Code coverage reports
- `.nyc_output` - NYC coverage data
- `.pytest_cache/` - Python test cache

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:186-189](), [.gitignore:68-70]()

### Validation Script

The `scripts/validate-stack.sh` script performs meta-level checks:

1. **Language Detection**: Identifies the CDK project language
2. **Template Analysis**: Checks CloudFormation template size limits
3. **Resource Count**: Validates resource count within AWS limits
4. **Synthesis Verification**: Confirms `cdk synth` succeeds

**Note**: Detailed anti-pattern checks are delegated to cdk-nag in Layer 2, keeping this script focused on structural validation.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:191-200]()

## Lifecycle Hooks for Runtime Safety

The hook system provides runtime safety checks before executing potentially destructive operations.

### Hook Architecture

```mermaid
graph TB
    subgraph "Hook Definition in SKILL.md"
        Frontmatter["hooks:<br/>  PreToolUse:"]
        Matcher["matcher: Bash(cdk deploy*)"]
        Command["command: aws sts get-caller-identity"]
        Once["once: true"]
    end
    
    subgraph "Runtime Execution"
        UserAction["User runs:<br/>/skill aws-cdk-development"]
        ToolCall["Bash(cdk deploy ...) invoked"]
        HookTrigger["PreToolUse hook triggered"]
        HookExec["Execute:<br/>aws sts get-caller-identity"]
        Verify["Verify AWS account"]
    end
    
    subgraph "Hook Behavior"
        FirstRun["First invocation:<br/>Hook executes"]
        Cache["Hook result cached"]
        SubsequentRuns["Subsequent invocations:<br/>Hook skipped (once: true)"]
    end
    
    subgraph "Safety Outcome"
        Display["Display account info<br/>to user"]
        Confirm["User confirms correct account"]
        Proceed["cdk deploy proceeds"]
    end
    
    Frontmatter --> Matcher
    Matcher --> Command
    Command --> Once
    
    UserAction --> ToolCall
    ToolCall --> HookTrigger
    HookTrigger --> HookExec
    HookExec --> Verify
    
    Verify --> FirstRun
    FirstRun --> Cache
    Cache --> SubsequentRuns
    
    Verify --> Display
    Display --> Confirm
    Confirm --> Proceed
```

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21](), [CLAUDE.md:71-76]()

### PreToolUse Hook Configuration

The hook is defined in the skill frontmatter:

```yaml
hooks:
  PreToolUse:
    - matcher: Bash(cdk deploy*)
      command: aws sts get-caller-identity --query Account --output text
      once: true
```

**Components**:
- `matcher`: Pattern matching tool invocations (wildcard `*` supported)
- `command`: Shell command to execute before the tool
- `once`: Boolean flag to execute hook only once per session

### Account Verification Workflow

The `aws sts get-caller-identity` command displays:
- AWS Account ID
- User/Role ARN
- User ID

This prevents accidental deployments to wrong AWS accounts by making the execution context explicit before each deployment session.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:16-21]()

## Testing Infrastructure

The testing infrastructure spans multiple languages and frameworks, with standardized artifact locations.

### Testing Artifacts and Locations

```mermaid
graph TB
    subgraph "Test Execution"
        NPM["npm test<br/>JavaScript/TypeScript"]
        Pytest["pytest<br/>Python"]
        Maven["mvn test<br/>Java"]
        DotNet["dotnet test<br/>C#"]
    end
    
    subgraph "Coverage Generation"
        NYC[".nyc_output/<br/>NYC coverage data"]
        CovDir["coverage/<br/>HTML reports<br/>JSON data"]
        PytestCache[".pytest_cache/<br/>Python test cache"]
    end
    
    subgraph "Test Types"
        UnitTests["Unit Tests:<br/>Individual constructs"]
        IntegrationTests["Integration Tests:<br/>Stack synthesis"]
        SnapshotTests["Snapshot Tests:<br/>CloudFormation templates"]
    end
    
    NPM --> NYC
    NPM --> CovDir
    Pytest --> PytestCache
    
    NYC --> UnitTests
    CovDir --> IntegrationTests
    PytestCache --> SnapshotTests
    
    style NYC fill:#f9f9f9
    style CovDir fill:#f9f9f9
    style PytestCache fill:#f9f9f9
```

Sources: [.gitignore:68-70](), [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:226-232]()

### Test Strategy

The testing approach follows CDK best practices:

| Test Type | Purpose | Scope | Tools |
|-----------|---------|-------|-------|
| **Unit Tests** | Validate individual constructs | Single construct | Jest, pytest, JUnit |
| **Integration Tests** | Validate stack synthesis | Full stack | CDK test utilities |
| **Snapshot Tests** | Validate CloudFormation templates | Template structure | Jest snapshots, approval tests |

**Key testing patterns**:
- Test construct properties and relationships
- Verify resource creation and configuration
- Validate IAM policies and permissions
- Check resource naming and tagging

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:226-232]()

### Coverage Tracking

Coverage artifacts are generated but ignored from version control:

```
coverage/           # HTML and JSON coverage reports
.nyc_output/        # NYC coverage data for JavaScript
.pytest_cache/      # Python test cache and results
```

These directories are listed in `.gitignore` to prevent committing generated artifacts.

Sources: [.gitignore:68-70]()

## Quality Gates and Pre-Commit Requirements

Quality gates ensure no code is committed without passing validation.

### Mandatory Version Bumping

Before committing any plugin modifications, version bumps are **mandatory**:

```json
{
  "plugins": [
    {
      "id": "aws-cdk@aws-skills",
      "version": "1.2.0"  // Must be bumped
    }
  ]
}
```

**Version bump decision tree**:

```mermaid
graph TB
    Change{"What changed?"}
    
    NewSkill["New skill added"]
    NewDep["New skills: dependency"]
    NewMCP["New MCP server"]
    NewPlugin["New plugin"]
    
    BugFix["Bug fix"]
    DocUpdate["Documentation update"]
    ConfigTweak["Config tweak"]
    TypoFix["Typo fix"]
    
    MinorBump["Minor bump x.Y.0"]
    PatchBump["Patch bump x.y.Z"]
    MarketplaceBump["Marketplace version bump"]
    
    Change -->|Structural| NewSkill
    Change -->|Structural| NewDep
    Change -->|Structural| NewMCP
    Change -->|Structural| NewPlugin
    
    Change -->|Content| BugFix
    Change -->|Content| DocUpdate
    Change -->|Content| ConfigTweak
    Change -->|Content| TypoFix
    
    NewSkill --> MinorBump
    NewDep --> MinorBump
    NewMCP --> MinorBump
    NewPlugin --> MinorBump
    NewPlugin --> MarketplaceBump
    
    BugFix --> PatchBump
    DocUpdate --> PatchBump
    ConfigTweak --> PatchBump
    TypoFix --> PatchBump
```

Sources: [CLAUDE.md:89-109]()

### Version Bump Rules

| Change Type | Version Component | Examples |
|-------------|------------------|----------|
| **Minor (x.Y.0)** | Structural changes | New skill, new `skills:` dependency, new MCP server, new plugin |
| **Patch (x.y.Z)** | Content changes | Bug fixes, doc updates, config tweaks, typo fixes |

**Locations to update**:
- `.claude-plugin/marketplace.json` - `plugins[].version` field
- `.claude-plugin/marketplace.json` - `metadata.version` (only for new plugins)

Sources: [CLAUDE.md:96-109]()

### GitHub Actions Integration

When GitHub Actions workflow files exist in `.github/workflows/`, all defined checks must pass before committing:

```
.github/workflows/
├── build.yml
├── test.yml
└── validate.yml
```

This ensures CI/CD pipeline compatibility and prevents pipeline failures after merge.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:294-296]()

## Local Testing Workflow

The local testing workflow uses symlinks for rapid iteration without plugin reinstallation.

### Symlink Structure

```mermaid
graph LR
    subgraph "Plugin Source"
        PluginDir["plugins/aws-cdk/<br/>skills/aws-cdk-development/"]
    end
    
    subgraph "Claude Code Discovery"
        ClaudeSkills[".claude/skills/<br/>aws-cdk-development/"]
    end
    
    subgraph "Testing"
        CLI["claude -p 'prompt'"]
        IDE["Claude Code IDE<br/>/skills command"]
        Context["/context command"]
    end
    
    PluginDir -.symlink.-> ClaudeSkills
    ClaudeSkills --> CLI
    ClaudeSkills --> IDE
    ClaudeSkills --> Context
    
    style ClaudeSkills fill:#f9f9f9
```

Sources: [CLAUDE.md:26-54]()

### Creating Symlinks

If symlinks break, recreate them:

```bash
cd .claude && rm -rf skills && mkdir skills
ln -s ../../plugins/aws-common/skills/aws-mcp-setup skills/
ln -s ../../plugins/aws-cdk/skills/aws-cdk-development skills/
ln -s ../../plugins/serverless-eda/skills/aws-serverless-eda skills/
ln -s ../../plugins/aws-agentic-ai/skills/aws-agentic-ai skills/
ln -s ../../plugins/aws-cost-ops/skills/aws-cost-operations skills/
```

### Verification Commands

**Interactive testing**:
```bash
cd /data/git/agentic/aws-skills
claude
/skills    # List all loaded skills
/context   # Show execution context
```

**Non-interactive testing**:
```bash
claude -p "List all available skills in this project"
claude -p "Read the frontmatter of aws-cdk-development skill"
```

Sources: [CLAUDE.md:26-54]()

## Summary

The validation and quality assurance system provides defense in depth through:

1. **Multi-layer validation**: Progressive quality gates from IDE to pre-commit
2. **Lifecycle hooks**: Runtime safety checks before destructive operations
3. **Testing infrastructure**: Comprehensive unit, integration, and snapshot tests
4. **Quality gates**: Mandatory version bumping and CI/CD integration
5. **Local testing**: Rapid iteration through symlink-based development

This system ensures that infrastructure code meets AWS best practices, passes security checks, and maintains high quality standards before reaching production environments.

Sources: [plugins/aws-cdk/skills/aws-cdk-development/SKILL.md:132-296](), [CLAUDE.md:26-109]()