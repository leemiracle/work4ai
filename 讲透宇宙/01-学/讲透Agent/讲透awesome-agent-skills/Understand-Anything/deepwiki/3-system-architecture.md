<!-- source: DeepWiki mcp.deepwiki.com · repo Lum1104/Understand-Anything · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.npmrc](.npmrc)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [READMEs/README.es-ES.md](READMEs/README.es-ES.md)
- [READMEs/README.ja-JP.md](READMEs/README.ja-JP.md)
- [READMEs/README.ko-KR.md](READMEs/README.ko-KR.md)
- [READMEs/README.tr-TR.md](READMEs/README.tr-TR.md)
- [READMEs/README.zh-CN.md](READMEs/README.zh-CN.md)
- [READMEs/README.zh-TW.md](READMEs/README.zh-TW.md)
- [install.ps1](install.ps1)
- [install.sh](install.sh)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)
- [tsconfig.json](tsconfig.json)
- [understand-anything-plugin/agents/architecture-analyzer.md](understand-anything-plugin/agents/architecture-analyzer.md)
- [understand-anything-plugin/agents/article-analyzer.md](understand-anything-plugin/agents/article-analyzer.md)
- [understand-anything-plugin/agents/assemble-reviewer.md](understand-anything-plugin/agents/assemble-reviewer.md)
- [understand-anything-plugin/agents/domain-analyzer.md](understand-anything-plugin/agents/domain-analyzer.md)
- [understand-anything-plugin/agents/graph-reviewer.md](understand-anything-plugin/agents/graph-reviewer.md)
- [understand-anything-plugin/agents/knowledge-graph-guide.md](understand-anything-plugin/agents/knowledge-graph-guide.md)
- [understand-anything-plugin/agents/project-scanner.md](understand-anything-plugin/agents/project-scanner.md)
- [understand-anything-plugin/agents/tour-builder.md](understand-anything-plugin/agents/tour-builder.md)

</details>



This document explains the high-level architecture of Understand Anything, including the relationship between packages, the plugin structure, and how data flows through the system. For detailed information about the monorepo workspace configuration and package organization, see [Monorepo Structure](#3.1). For build pipeline and TypeScript compilation details, see [Build and TypeScript Configuration](#3.2).

## System Overview

Understand Anything is architected as a **Claude Code plugin** distributed via the Claude Code Marketplace. The system consists of three main software components organized as a pnpm monorepo using a workspace configuration [pnpm-workspace.yaml:1-5]().

| Component | Package Name | Purpose |
|-----------|--------------|---------|
| Analysis Engine | `@understand-anything/core` | Shared analysis engine (types, persistence, tree-sitter, search, schema, tours, plugins) [CLAUDE.md:13-13]() |
| Interactive Dashboard | `@understand-anything/dashboard` | React + TypeScript web application for graph visualization and exploration [CLAUDE.md:14-14]() |
| Plugin Package | `understand-anything-plugin` | Skill definitions and command implementations that orchestrate the other components [CLAUDE.md:12-12]() |

The system follows a **separation of concerns** between generation (analyzing codebases to produce knowledge graphs) and consumption (querying and visualizing existing graphs).

**Sources:** [pnpm-workspace.yaml:1-5](), [CLAUDE.md:10-18](), [README.md:44-47]()

## High-Level Component Architecture

The diagram below illustrates how user commands interact with the plugin runtime, specialized agents, and the local project filesystem.

Title: High-Level System Interactions
```mermaid
graph TB
    subgraph "Claude Code IDE"
        [User] --> [PluginRuntime]
    end
    
    subgraph "Understand Anything Plugin"
        subgraph "Skill Layer (understand-anything-plugin/src)"
            [UnderstandSkill]
            [ChatSkill]
            [DiffSkill]
            [ExplainSkill]
            [OnboardSkill]
            [DashboardSkill]
        end
        
        subgraph "Implementation Layer"
            [CorePackage]
            [DashboardPackage]
        end
        
        subgraph "Agent Layer"
            [Agents]
        end
    end
    
    subgraph "User's Project"
        [SourceCode]
        [UnderstandDir]
        [IntermediateDir]
    end
    
    subgraph "Runtime Environment"
        [ViteServer]
        [Browser]
    end
    
    [PluginRuntime] --> [UnderstandSkill]
    [PluginRuntime] --> [ChatSkill]
    [PluginRuntime] --> [DashboardSkill]
    
    [UnderstandSkill] --> [Agents]
    [UnderstandSkill] --> [CorePackage]
    
    [DashboardSkill] --> [ViteServer]
    [DashboardPackage] --> [CorePackage]
    
    [Agents] --> [SourceCode]
    [Agents] --> [IntermediateDir]
    [Agents] --> [UnderstandDir]
    
    [ViteServer] --> [DashboardPackage]
    [ViteServer] --> [UnderstandDir]
    [ViteServer] --> [Browser]
```

**Component Interaction Flow:**

1. **Plugin Registration**: The plugin is discovered via platform-specific manifests like `.claude-plugin/plugin.json` [CLAUDE.md:58-63]().
2. **Skill Execution**: User invokes a skill command (e.g., `/understand`, `/understand-chat`) implemented within the `understand-anything-plugin` package [CLAUDE.md:15-16]().
3. **Generation Path**: `/understand` orchestrates the multi-agent pipeline [CLAUDE.md:27-31](). Agents write intermediate results to `.understand-anything/intermediate/` before final assembly [CLAUDE.md:28-28]().
4. **Consumption Path**: Skills read the knowledge graph stored in the `.understand-anything/` directory [CLAUDE.md:47-47]().
5. **Visualization**: `/understand-dashboard` launches a Vite server that serves the `@understand-anything/dashboard` React application [CLAUDE.md:40-40]().

**Sources:** [CLAUDE.md:10-47](), [README.md:104-143](), [understand-anything-plugin/agents/project-scanner.md:51-60]()

## Package Architecture

The monorepo uses pnpm workspaces to manage internal dependencies [CLAUDE.md:11-11](). The root `tsconfig.json` provides base configurations, enforcing strict mode and ESM modules [CLAUDE.md:44-46]().

### Package Responsibilities

#### `@understand-anything/core`
The core package provides the foundational subsystems.
- **Analysis**: Uses `web-tree-sitter` (WASM) for structural analysis [CLAUDE.md:51-51]().
- **Search**: Implements fuzzy and semantic search engines [CLAUDE.md:13-13]().
- **Persistence**: Manages reading/writing the graph and metadata to the `.understand-anything/` directory [CLAUDE.md:47-47]().
- **Browser Safety**: Uses subpath exports (e.g., `./search`, `./schema`) to ensure the dashboard doesn't pull in Node.js modules [CLAUDE.md:48-48]().

#### `@understand-anything/dashboard`
A React application featuring a "dark luxury" theme [CLAUDE.md:20-20]().
- **Visualization**: Graph-first layout using React Flow [CLAUDE.md:21-21]().
- **State**: Managed via `zustand` [CLAUDE.md:14-14]().
- **Data Access**: Fetches code content via a gated `/file-content.json` endpoint on the dev server [CLAUDE.md:24-24]().

#### `understand-anything-plugin`
The main plugin package containing agent definitions and skill logic [CLAUDE.md:15-17]().

**Sources:** [CLAUDE.md:1-53](), [tsconfig.json:1-16]()

## Data Flow Architecture

The system follows a **write-once, read-many** data flow pattern centered around the local file system.

Title: Data Flow and Persistence
```mermaid
graph TB
    subgraph "Phase 1: Analysis"
        [Codebase] --> [UnderstandCmd]
        [UnderstandCmd] --> [AgentPipeline]
        [AgentPipeline] -->|"writes"| [IntermediateDir]
        [IntermediateDir] -->|"assembled into"| [KnowledgeGraph]
    end
    
    subgraph "Phase 2: Consumption"
        [KnowledgeGraph] -->|"read by"| [OtherSkills]
        [KnowledgeGraph] -->|"read by"| [DashboardCmd]
    end
    
    subgraph "Phase 3: Visualization"
        [DashboardCmd] --> [ViteServer]
        [ViteServer] --> [DashboardUI]
    end
```

**Sources:** [CLAUDE.md:27-31](), [CLAUDE.md:47-47](), [understand-anything-plugin/agents/project-scanner.md:51-82]()

## Component Dependency Graph

The following diagram maps high-level system commands to their underlying code implementations and data structures within the monorepo.

Title: Code Entity to System Mapping
```mermaid
graph LR
    subgraph "Core Logic (@understand-anything/core)"
        [Schema]
        [SearchEngine]
        [Persistence]
    end

    subgraph "System Commands (understand-anything-plugin)"
        [CmdUnderstand]
        [CmdDash]
    end

    subgraph "Dashboard UI (@understand-anything/dashboard)"
        [GraphView]
        [DashboardStore]
    end

    [CmdUnderstand] --> [Persistence]
    [CmdUnderstand] --> [Schema]
    [CmdDash] --> [GraphView]
    [GraphView] --> [DashboardStore]
    [DashboardStore] --> [SearchEngine]
```

**Sources:** [CLAUDE.md:10-53](), [pnpm-workspace.yaml:1-5](), [README.md:104-143]()

---

