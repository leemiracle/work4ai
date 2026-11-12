<!-- source: DeepWiki mcp.deepwiki.com · repo voltagent/voltagent · page 7 Development Tools · fetched 2026-10-27 -->

# Development Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/prerelease.yml](.github/workflows/prerelease.yml)
- [.github/workflows/pull-request.yml](.github/workflows/pull-request.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [changelog.sh](changelog.sh)
- [examples/base/src/index.ts](examples/base/src/index.ts)
- [examples/with-jwt-auth/src/index.ts](examples/with-jwt-auth/src/index.ts)
- [examples/with-playwright/src/index.ts](examples/with-playwright/src/index.ts)
- [package.json](package.json)
- [packages/cli/package.json](packages/cli/package.json)
- [packages/core/src/utils/message-helpers.spec.ts](packages/core/src/utils/message-helpers.spec.ts)
- [packages/core/src/utils/message-helpers.ts](packages/core/src/utils/message-helpers.ts)
- [packages/create-voltagent-app/CHANGELOG.md](packages/create-voltagent-app/CHANGELOG.md)
- [packages/create-voltagent-app/package.json](packages/create-voltagent-app/package.json)
- [packages/voice/package.json](packages/voice/package.json)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [website/docs/utils/message-helpers.md](website/docs/utils/message-helpers.md)

</details>



This page provides an overview of the development tools available in the VoltAgent ecosystem that help developers build, debug, monitor, and manage their AI agent applications. These tools are designed to streamline the development workflow and provide insights into agent behavior.

For information about specific integrations like voice or database capabilities, see [Extensions and Integrations](#4).

## Overview of Development Tools

The VoltAgent framework provides several key development tools that work together to support the agent development lifecycle:

```mermaid
graph TD
    subgraph "Development Ecosystem"
        CreateApp["create-voltagent-app"]
        CLI["@voltagent/cli"]
        Console["Developer Console"]
        LocalServer["Local Server :3141"]
    end
    
    Developer -->|"uses to create projects"| CreateApp
    Developer -->|"uses to manage projects"| CLI
    Developer -->|"monitors agents through"| Console
    
    CreateApp -->|"generates"| VoltProject["VoltAgent Project"]
    
    VoltProject -->|"runs with"| LocalServer
    Console -->|"connects to"| LocalServer
    
    subgraph "Project Components"
        Agents["Agent Definitions"]
        Tools["Tool Implementations"]
        Models["LLM Provider Config"]
    end
    
    VoltProject --> Agents
    VoltProject --> Tools
    VoltProject --> Models
```

Sources: [README.md:85-95](), [CONSOLE.md:20-26](), [packages/create-voltagent-app/package.json:1-10](), [packages/cli/package.json:1-14]()

## Project Creation with `create-voltagent-app`

The `create-voltagent-app` tool allows developers to quickly bootstrap new VoltAgent projects with the necessary structure and dependencies.

### Features and Usage

- **Command:** `npm create voltagent-app@latest [project-name]`
- **Interactive Setup:** Guides developers through configuration options
- **Template Selection:** Provides starter templates for different use cases
- **Environment Configuration:** Helps set up necessary API keys and environment variables

```mermaid
sequenceDiagram
    participant Developer
    participant CreateApp as "create-voltagent-app"
    participant NPM as "npm registry"
    participant FileSystem as "File System"
    
    Developer->>CreateApp: Execute "npm create voltagent-app@latest"
    CreateApp->>NPM: Fetch latest version
    CreateApp->>Developer: Prompt for project name & options
    Developer->>CreateApp: Provide configuration
    CreateApp->>NPM: Install dependencies
    CreateApp->>FileSystem: Generate project structure
    CreateApp->>FileSystem: Create starter files
    CreateApp->>FileSystem: Configure package.json
    CreateApp->>Developer: Display success message & next steps
```

Sources: [README.md:87-95](), [packages/create-voltagent-app/package.json:1-54]()

### Project Structure

A typical project created with `create-voltagent-app` includes:

- Core configuration files (`package.json`, `tsconfig.json`)
- Source directory with example agent implementation
- Environment variables configuration (`.env`, `.env.example`)
- Development scripts for building and running the application

## VoltAgent CLI

The VoltAgent CLI (`@voltagent/cli`) provides command-line utilities for managing VoltAgent projects.

### Commands

| Command | Description | Status |
|---------|-------------|--------|
| `volt init` | Initialize a new or existing VoltAgent project | Available |
| `volt update` | Check for updates to VoltAgent packages | Available |
| `volt whoami` | Display current user identity information | Available |
| `volt add <agent-slug>` | Add an agent from the marketplace | Coming Soon |

Sources: [packages/cli/src/index.ts:15-26](), [packages/cli/src/commands/add.ts:5-43](), [packages/cli/package.json:1-55]()

## Developer Console

The VoltAgent Developer Console is a web-based tool for monitoring and debugging AI agents during development and execution.

### Key Features

#### 1. Real-Time Agent Visualization

The console provides visual representations of agent execution flow, allowing developers to understand how their agents process requests.

```mermaid
graph TD
    subgraph "Agent Execution Flow"
        UserInput["User Input"]
        AgentProcessing["Agent Processing"]
        ToolCall["Tool Call"]
        ToolExecution["Tool Execution"]
        ToolResult["Tool Result"]
        ResponseGeneration["Response Generation"]
        UserResponse["User Response"]
    end
    
    UserInput -->|"triggers"| AgentProcessing
    AgentProcessing -->|"may include"| ToolCall
    ToolCall -->|"executes"| ToolExecution
    ToolExecution -->|"returns"| ToolResult
    ToolResult -->|"informs"| ResponseGeneration
    AgentProcessing -->|"directly or after tools"| ResponseGeneration
    ResponseGeneration -->|"delivers"| UserResponse
```

Sources: [CONSOLE.md:31-36]()

#### 2. Agent Chat Interface

The console provides an interactive chat interface for directly communicating with agents, making it easy to test and debug agent behavior.

Sources: [CONSOLE.md:38-43]()

#### 3. Granular Visibility into Agent Runs

Developers can inspect detailed information about each agent run, including:

- Input messages and parameters
- Internal processing steps
- Tool invocations and their results
- Response generation details
- Memory usage and context

Sources: [CONSOLE.md:45-50]()

#### 4. Agent List View

The console provides an overview of all active and recent agent sessions, making it easy to monitor multiple agents.

Sources: [CONSOLE.md:52-57]()

### Connection and Usage

```mermaid
flowchart LR
    subgraph "Local Development Environment"
        VoltProject["VoltAgent Project"]
        LocalServer["Local Server :3141"]
    end
    
    subgraph "Browser"
        DevConsole["Developer Console\nconsole.voltagent.dev"]
    end
    
    VoltProject -->|"starts"| LocalServer
    DevConsole -->|"connects to"| LocalServer
    Developer -->|"interacts with"| DevConsole
    Developer -->|"modifies"| VoltProject
```

The Developer Console connects to a local agent server, usually running on port 3141, which is automatically started when running a VoltAgent project in development mode.

To use the console:
1. Start your VoltAgent project with `npm run dev`
2. Open the Developer Console at https://console.voltagent.dev
3. The console automatically connects to the local server
4. Browse and interact with your agents through the console interface

Sources: [CONSOLE.md:59-97](), [README.md:125-144]()

## Development Workflow

The typical workflow for developing agents with VoltAgent involves using these tools together:

```mermaid
graph LR
    subgraph "Project Creation"
        CreateApp["create-voltagent-app"]
        ProjectStructure["Project Structure"]
    end
    
    subgraph "Development"
        CodeEditor["Code Editor/IDE"]
        CLI["CLI Commands"]
        DevServer["Development Server"]
    end
    
    subgraph "Testing & Debugging"
        Console["Developer Console"]
        Chat["Agent Chat"]
        Visualization["Flow Visualization"]
        Inspection["Message Inspection"]
    end
    
    subgraph "Refinement"
        Analysis["Performance Analysis"]
        Improvement["Agent Improvement"]
    end
    
    CreateApp -->|"generates"| ProjectStructure
    ProjectStructure -->|"edit in"| CodeEditor
    CodeEditor -->|"run with"| DevServer
    CLI -->|"manage"| DevServer
    DevServer -->|"observed in"| Console
    Console --> Chat
    Console --> Visualization
    Console --> Inspection
    Chat -->|"leads to"| Analysis
    Visualization -->|"leads to"| Analysis
    Inspection -->|"leads to"| Analysis
    Analysis -->|"informs"| Improvement
    Improvement -->|"implemented in"| CodeEditor
```

Sources: [README.md:85-144](), [CONSOLE.md:20-97]()

## Integration with Core Framework

The development tools are designed to work seamlessly with the VoltAgent core framework, providing visibility into agent operations, tool usage, and model interactions.

```mermaid
graph TD
    subgraph "Development Tools"
        CreateApp["create-voltagent-app"]
        CLI["@voltagent/cli"]
        Console["Developer Console"]
    end
    
    subgraph "Core Framework"
        Core["@voltagent/core"]
        Agent["Agent"]
        VoltAgentClass["VoltAgent"]
        LLM["LLM Providers"]
        Tools["Tools"]
        Memory["Memory"]
    end
    
    CreateApp -->|"generates projects using"| Core
    CLI -->|"manages projects using"| Core
    VoltAgentClass -->|"exposes server for"| Console
    Agent -->|"observable by"| Console
    LLM -->|"monitored by"| Console
    Tools -->|"tracked by"| Console
    Memory -->|"inspectable by"| Console
```

Sources: [README.md:45-63](), [CONSOLE.md:20-26]()

## Key Benefits

The VoltAgent development tools offer several advantages:

1. **Streamlined Setup:** Quick project creation and initialization
2. **Real-time Debugging:** Visual insights into agent behavior as it happens
3. **Transparent Operation:** Clear visibility into agent processing steps
4. **Interactive Testing:** Direct communication with agents through the console
5. **Efficient Workflow:** Tools designed to work together throughout the development lifecycle

Sources: [README.md:66-82](), [CONSOLE.md:9-10](), [CONSOLE.md:28-29]()

## Future Development

The VoltAgent team is actively developing additional development tools:

- **Agent Marketplace Integration:** The `volt add` command will allow importing pre-built agents from a marketplace (coming soon)
- **Enhanced Visualization:** Additional views and metrics in the Developer Console
- **Deployment Tools:** Simplified deployment workflows for production environments

Sources: [packages/cli/src/commands/add.ts:5-43]()

---

