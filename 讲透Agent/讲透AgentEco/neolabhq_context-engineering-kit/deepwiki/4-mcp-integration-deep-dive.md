<!-- source: DeepWiki mcp.deepwiki.com · repo neolabhq/context-engineering-kit · page 4 MCP Integration Deep Dive · fetched 2026-10-27 -->

# MCP Integration Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guides/README.md](docs/guides/README.md)
- [docs/plugins/mcp/README.md](docs/plugins/mcp/README.md)
- [docs/plugins/mcp/recommended-mcp.md](docs/plugins/mcp/recommended-mcp.md)
- [docs/plugins/mcp/usage-examples.md](docs/plugins/mcp/usage-examples.md)
- [plugins/mcp/.claude-plugin/plugin.json](plugins/mcp/.claude-plugin/plugin.json)
- [plugins/mcp/README.md](plugins/mcp/README.md)

</details>



## Purpose and Scope

This document provides comprehensive technical documentation for Model Context Protocol (MCP) integration within the Context Engineering Kit. It covers the architecture of the MCP plugin, the five setup commands, configuration management, and integration patterns with other CEK plugins.

For basic MCP plugin usage and command reference, see [MCP Plugin Overview](#3.3.2). For practical workflow examples combining MCP with other plugins, see [Development Guides](#5).

**Sources:** [plugins/mcp/README.md:1-10](), [docs/plugins/mcp/README.md:1-10]()

---

## MCP Protocol Overview

Model Context Protocol is a standardized interface that enables LLMs to interact with external services, databases, and tools. MCP servers expose three types of capabilities to Claude:

| Capability | Purpose | Example Use Cases |
|------------|---------|-------------------|
| **Resources** | External data Claude can read | Documentation files, API responses, database records |
| **Tools** | Actions Claude can execute | Search operations, data transformations, API calls |
| **Prompts** | Reusable templates with dynamic inputs | Formatted queries, structured analysis requests |

MCP eliminates the need to load all external context upfront. Instead, Claude requests specific information on-demand, reducing token consumption while expanding available knowledge.

**Sources:** [docs/plugins/mcp/recommended-mcp.md:6-13]()

---

## MCP Plugin Architecture

```mermaid
graph TB
    subgraph "Command Layer"
        SetupContext7["/mcp:setup-context7-mcp"]
        SetupSerena["/mcp:setup-serena-mcp"]
        SetupCodemap["/mcp:setup-codemap-cli"]
        SetupArxiv["/mcp:setup-arxiv-mcp"]
        BuildMCP["/mcp:build-mcp"]
    end
    
    subgraph "MCP Servers"
        Context7["Context7 MCP<br/>fetch_docs tool"]
        Serena["Serena MCP<br/>find_symbol, list_symbols"]
        Codemap["Codemap CLI<br/>Shell commands"]
        PaperSearch["Paper Search MCP<br/>search_arxiv, download_arxiv"]
        CustomMCP["Custom MCP Servers<br/>User-defined tools"]
    end
    
    subgraph "Configuration Files"
        CLAUDEmd["./CLAUDE.md<br/>Project shared"]
        CLAUDElocal["./CLAUDE.local.md<br/>Project personal"]
        CLAUDEglobal["~/.claude/CLAUDE.md<br/>User global"]
    end
    
    subgraph "Enhanced Plugins"
        SDD["SDD Plugin<br/>+ Current API docs<br/>+ Symbol navigation"]
        TDD["TDD Plugin<br/>+ Symbol-based tests"]
        Kaizen["Kaizen Plugin<br/>+ Research papers<br/>+ Code visualization"]
        Docs["Docs Plugin<br/>+ Framework docs"]
    end
    
    SetupContext7 -->|configures| Context7
    SetupSerena -->|configures| Serena
    SetupCodemap -->|installs| Codemap
    SetupArxiv -->|configures| PaperSearch
    BuildMCP -->|creates| CustomMCP
    
    Context7 -.updates.-> CLAUDEmd
    Serena -.updates.-> CLAUDEmd
    Codemap -.updates.-> CLAUDEmd
    PaperSearch -.updates.-> CLAUDEmd
    
    CLAUDEmd -->|informs| SDD
    CLAUDEmd -->|informs| TDD
    CLAUDEmd -->|informs| Kaizen
    CLAUDEmd -->|informs| Docs
    
    Context7 -.enhances.-> SDD
    Context7 -.enhances.-> Docs
    Serena -.enhances.-> SDD
    Serena -.enhances.-> TDD
    Codemap -.enhances.-> Kaizen
    PaperSearch -.enhances.-> Kaizen
```

**MCP Plugin Architecture Diagram** - The MCP plugin provides five setup commands that configure external MCP servers. Each command updates configuration files (CLAUDE.md) with usage instructions. MCP servers then enhance other CEK plugins by providing specialized capabilities.

**Sources:** [plugins/mcp/README.md:13-20](), [docs/plugins/mcp/README.md:13-20]()

---

## Three-Tier Configuration System

The MCP plugin uses Claude's hierarchical configuration system to manage MCP server settings at three levels:

### Configuration Hierarchy

```mermaid
graph LR
    UserGlobal["~/.claude/CLAUDE.md<br/>User Global"]
    ProjectShared["./CLAUDE.md<br/>Project Shared<br/>(Git tracked)"]
    ProjectPersonal["./CLAUDE.local.md<br/>Project Personal<br/>(Git ignored)"]
    
    UserGlobal -->|defaults for| ProjectShared
    ProjectShared -->|overridden by| ProjectPersonal
    
    ProjectShared -->|shared with| Team["Team Members"]
    ProjectPersonal -->|private to| Developer["Individual Developer"]
```

**Configuration Hierarchy Diagram** - User-global settings provide defaults, project-shared settings establish team standards, and project-personal settings allow individual customization.

| Configuration Level | File Path | Git Tracked | Use Case |
|---------------------|-----------|-------------|----------|
| User Global | `~/.claude/CLAUDE.md` | No | Personal defaults across all projects |
| Project Shared | `./CLAUDE.md` | Yes | Team-wide MCP server configuration |
| Project Personal | `./CLAUDE.local.md` | No | Individual overrides, API keys |

### Configuration Selection Process

Each setup command prompts for configuration level:

```
Where should this configuration be saved?
1. Project level (shared) - ./CLAUDE.md (tracked in git)
2. Project level (personal) - ./CLAUDE.local.md (not tracked)
3. User level (global) - ~/.claude/CLAUDE.md (applies to all projects)
```

**Sources:** [plugins/mcp/README.md:21-27](), [docs/plugins/mcp/README.md:21-27]()

---

## Setup Commands Reference

### Command Mapping to MCP Servers

| Command | MCP Server | Primary Capability | Configuration Output |
|---------|------------|-------------------|---------------------|
| `/mcp:setup-context7-mcp` | Context7 | Documentation fetching | Library IDs in CLAUDE.md |
| `/mcp:setup-serena-mcp` | Serena | Semantic code analysis | Usage guidelines in CLAUDE.md |
| `/mcp:setup-codemap-cli` | Codemap | Codebase visualization | Session hooks in `.claude/settings.json` |
| `/mcp:setup-arxiv-mcp` | Paper Search | Academic paper search | Docker MCP configuration |
| `/mcp:build-mcp` | Custom | User-defined tools | Four-phase development guide |

### Setup Command Workflow

```mermaid
sequenceDiagram
    participant User
    participant SetupCommand as "Setup Command"
    participant MCPServer as "MCP Server"
    participant CLAUDEmd as "CLAUDE.md"
    
    User->>SetupCommand: Execute /mcp:setup-*
    SetupCommand->>MCPServer: Check availability
    
    alt MCP Server Not Available
        SetupCommand->>User: Provide installation instructions
        User->>MCPServer: Install/Configure
    end
    
    SetupCommand->>MCPServer: Load documentation
    SetupCommand->>MCPServer: Test connection
    SetupCommand->>User: Prompt for config level
    User->>SetupCommand: Select level (shared/personal/global)
    SetupCommand->>CLAUDEmd: Write configuration
    SetupCommand->>User: Confirm setup complete
```

**Setup Command Workflow Diagram** - Standard flow for all MCP setup commands: availability check, installation guidance, connection testing, configuration level selection, and CLAUDE.md update.

**Sources:** [plugins/mcp/README.md:80-88](), [docs/plugins/mcp/README.md:80-88]()

---

## Context7 MCP Integration

Context7 provides real-time access to library and framework documentation, eliminating hallucinations from outdated training data. For details, see [Context7 MCP Setup](#4.2).

### Technology Detection Flow

```mermaid
graph TD
    Start["User: /mcp:setup-context7-mcp<br/>with optional tech list"]
    
    HasArgs{Arguments<br/>provided?}
    Start --> HasArgs
    
    HasArgs -->|Yes| ParseArgs["Parse technology names<br/>from user input"]
    HasArgs -->|No| ScanProject["Scan project files:<br/>package.json<br/>requirements.txt<br/>go.mod"]
    
    ParseArgs --> QueryContext7["Query Context7:<br/>search_docs for each tech"]
    ScanProject --> QueryContext7
    
    QueryContext7 --> BuildLibList["Build library ID list:<br/>react -> react<br/>@tanstack/query -> tanstack-query"]
    
    BuildLibList --> UpdateCLAUDE["Write to CLAUDE.md:<br/>### Use Context7 MCP<br/>Library IDs list<br/>Usage instructions"]
    
    UpdateCLAUDE --> Complete["Setup complete"]
```

**Context7 Setup Flow Diagram** - The command either parses provided technology names or auto-detects from project files, queries Context7 for documentation IDs, and updates CLAUDE.md with the configuration.

**Sources:** [docs/plugins/mcp/usage-examples.md:50-80](), [docs/plugins/mcp/README.md:51]()

---

## Serena MCP Integration

Serena provides semantic understanding of codebases through symbol-based operations, enabling precise code navigation and refactoring. For details, see [Serena MCP Setup](#4.3).

### Serena Tool Mapping

| Serena Tool | Purpose | Use Case |
|-------------|---------|----------|
| `find_symbol` | Locate functions, classes, types by name | Finding function definitions across large codebases |
| `list_symbols` | List available symbols in file/module | Exploring module structure before editing |
| `read_file` | Read file contents with semantic context | Understanding code in context of symbols |

### Serena Setup Prerequisites

```mermaid
graph TD
    Start["User: /mcp:setup-serena-mcp"]
    
    CheckSerena["Check Serena tools:<br/>find_symbol<br/>list_symbols"]
    Start --> CheckSerena
    
    Available{Tools<br/>available?}
    CheckSerena --> Available
    
    Available -->|Yes| IndexProject["Index project:<br/>Parse source files<br/>Build symbol database"]
    Available -->|No| CheckUV["Check prerequisite:<br/>uv package manager"]
    
    CheckUV --> DetectClient["Detect MCP client:<br/>Claude Code<br/>Claude Desktop<br/>Cursor"]
    
    DetectClient --> GuideInstall["Provide client-specific<br/>installation instructions"]
    
    GuideInstall --> WaitRestart["Wait for user to:<br/>1. Configure MCP<br/>2. Restart client"]
    
    WaitRestart --> IndexProject
    
    IndexProject --> TestTools["Test connection:<br/>find_symbol test<br/>list_symbols test"]
    
    TestTools --> UpdateCLAUDE["Write to CLAUDE.md:<br/>### Use Serena MCP<br/>Usage guidelines<br/>Symbol-based patterns"]
```

**Serena Setup Flow Diagram** - Complex setup process involving prerequisite checks, client-specific configuration, project indexing, and connection testing.

**Sources:** [docs/plugins/mcp/usage-examples.md:146-208](), [docs/plugins/mcp/README.md:52]()

---

## Codemap CLI Integration

Codemap provides intelligent codebase visualization through tree views, dependency analysis, and change tracking. Unlike other MCP servers, Codemap is a CLI tool that integrates via session hooks. For details, see [Codemap CLI Setup](#4.4).

### Codemap Integration Architecture

```mermaid
graph TB
    subgraph "Setup Phase"
        SetupCmd["/mcp:setup-codemap-cli"]
        CheckInstall["Check: codemap --version"]
        InstallGuide["Provide OS-specific install:<br/>brew install codemap (macOS)<br/>scoop install codemap (Windows)"]
        SetupCmd --> CheckInstall
        CheckInstall -->|Not installed| InstallGuide
    end
    
    subgraph "Configuration Phase"
        WriteCLAUDE["Update CLAUDE.md:<br/>Usage instructions<br/>Common commands"]
        WriteHooks["Update .claude/settings.json:<br/>SessionStart hook<br/>PreToolUse hook"]
        WriteGitignore["Update .gitignore:<br/>.codemap/"]
        
        InstallGuide --> WriteCLAUDE
        CheckInstall -->|Installed| WriteCLAUDE
        WriteCLAUDE --> WriteHooks
        WriteHooks --> WriteGitignore
    end
    
    subgraph "Runtime Phase"
        SessionStart["SessionStart hook:<br/>codemap --diff --ref master"]
        PreToolUse["PreToolUse hook:<br/>codemap . (on file edits)"]
        
        WriteHooks -.triggers.-> SessionStart
        WriteHooks -.triggers.-> PreToolUse
    end
```

**Codemap Integration Architecture Diagram** - Codemap setup installs the CLI, configures session hooks in `.claude/settings.json`, and updates CLAUDE.md with usage patterns.

**Sources:** [docs/plugins/mcp/usage-examples.md:82-143](), [docs/plugins/mcp/README.md:53]()

---

## Paper Search MCP Integration

Paper Search MCP provides access to academic literature across multiple sources via Docker MCP. For details, see [Paper Search MCP Setup](#4.5).

### Paper Search Architecture

```mermaid
graph TB
    SetupCmd["/mcp:setup-arxiv-mcp"]
    
    CheckDocker["Check Docker MCP:<br/>mcp-find paper-search"]
    SetupCmd --> CheckDocker
    
    Available{Docker MCP<br/>available?}
    CheckDocker --> Available
    
    Available -->|No| InstallDocker["Guide Docker Desktop<br/>+ Docker MCP Toolkit install"]
    Available -->|Yes| AddServer["Add server:<br/>mcp-add paper-search<br/>activate: true"]
    
    InstallDocker --> AddServer
    
    AddServer --> TestSearch["Test connection:<br/>search_arxiv test query"]
    
    TestSearch --> UpdateCLAUDE["Write to CLAUDE.md:<br/>Available search tools<br/>Usage examples"]
    
    subgraph "Available Tools"
        SearchTools["search_arxiv<br/>search_pubmed<br/>search_semantic<br/>search_biorxiv<br/>search_medrxiv<br/>search_iacr<br/>search_crossref<br/>search_google_scholar"]
        DownloadTools["download_arxiv<br/>read_arxiv_paper<br/>download_biorxiv<br/>read_biorxiv_paper<br/>download_semantic<br/>read_semantic_paper"]
    end
    
    UpdateCLAUDE --> SearchTools
    UpdateCLAUDE --> DownloadTools
```

**Paper Search MCP Architecture Diagram** - Docker MCP-based setup that provides comprehensive academic paper search and download capabilities across 8 sources.

**Sources:** [docs/plugins/mcp/README.md:54](), [docs/plugins/mcp/recommended-mcp.md:28]()

---

## Building Custom MCP Servers

The `/mcp:build-mcp` command guides users through a four-phase process for creating production-ready MCP servers. For details, see [Building Custom MCP Servers](#4.6).

### Four-Phase Development Process

```mermaid
graph TD
    Start["/mcp:build-mcp"]
    
    subgraph "Phase 1: Research & Planning"
        Principles["Agent-Centric Design:<br/>- Workflow tools not API wrappers<br/>- Optimize for limited context<br/>- Actionable error messages<br/>- Natural task subdivisions"]
        LoadSpec["Load MCP spec from<br/>modelcontextprotocol.io"]
        Framework["Select framework:<br/>FastMCP (Python)<br/>MCP SDK (TypeScript)"]
        APIResearch["Exhaustive API research:<br/>Study target API docs"]
        Plan["Implementation plan:<br/>Tool selection<br/>Shared utilities<br/>Schema design<br/>Error handling"]
        
        Start --> Principles
        Principles --> LoadSpec
        LoadSpec --> Framework
        Framework --> APIResearch
        APIResearch --> Plan
    end
    
    subgraph "Phase 2: Implementation"
        Structure["Project structure:<br/>Language-specific best practices"]
        Infrastructure["Core infrastructure:<br/>API helpers<br/>Error handling<br/>Formatting utilities"]
        Tools["Implement tools:<br/>Systematic implementation<br/>Proper annotations"]
        
        Plan --> Structure
        Structure --> Infrastructure
        Infrastructure --> Tools
    end
    
    subgraph "Phase 3: Review & Refine"
        CodeReview["Code quality review:<br/>DRY principle<br/>Composability<br/>Consistency"]
        Testing["Testing:<br/>Syntax verification<br/>Import checks<br/>Use evaluation harness"]
        Checklist["Language-specific<br/>quality checklist"]
        
        Tools --> CodeReview
        CodeReview --> Testing
        Testing --> Checklist
    end
    
    subgraph "Phase 4: Create Evaluations"
        Inspect["Tool inspection:<br/>Understand capabilities"]
        Explore["Content exploration:<br/>Read-only operations"]
        Questions["Generate 10 complex<br/>evaluation questions"]
        Verify["Verify answers:<br/>Correctness & stability"]
        
        Checklist --> Inspect
        Inspect --> Explore
        Explore --> Questions
        Questions --> Verify
    end
```

**Custom MCP Server Development Process Diagram** - Four phases ensure high-quality MCP servers: research and planning, implementation, review and refinement, and evaluation creation.

**Sources:** [docs/plugins/mcp/README.md:55](), [docs/plugins/mcp/usage-examples.md:327-503]()

---

## MCP Enhancement Patterns

MCP servers enhance other CEK plugins by providing external capabilities. This section maps enhancement patterns across the plugin ecosystem.

### Integration Flow Example: SDD + Context7 + Serena

```mermaid
sequenceDiagram
    participant User
    participant SDD as "SDD Plugin"
    participant Context7 as "Context7 MCP"
    participant Serena as "Serena MCP"
    participant CLAUDEmd as "CLAUDE.md"
    
    User->>SDD: /sdd:01-research
    SDD->>CLAUDEmd: Read Context7 config:<br/>Library IDs list
    SDD->>Context7: fetch_docs(react, typescript)
    Context7-->>SDD: Current API documentation
    SDD->>User: Research with real-time docs
    
    User->>SDD: /sdd:04-implement
    SDD->>CLAUDEmd: Read Serena config:<br/>Usage guidelines
    SDD->>Serena: find_symbol(UserService)
    Serena-->>SDD: Symbol location + definition
    SDD->>Serena: list_symbols(user-service.ts)
    Serena-->>SDD: Available methods + types
    SDD->>User: Implementation with semantic understanding
```

**SDD Enhanced by MCP Servers** - Spec-Driven Development workflow benefits from Context7 during research (current docs) and Serena during implementation (semantic code navigation).

**Sources:** [docs/plugins/mcp/usage-examples.md:211-254](), [docs/plugins/mcp/recommended-mcp.md:15-22]()

---

