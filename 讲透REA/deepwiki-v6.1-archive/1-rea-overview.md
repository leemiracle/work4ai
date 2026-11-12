<!-- source: DeepWiki mcp.deepwiki.com · repo morluto/rea · page 1 REA Overview · fetched 2026-10-09 -->

# REA Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [README_ar.md](README_ar.md)
- [README_ja.md](README_ja.md)
- [README_ko.md](README_ko.md)
- [README_zh.md](README_zh.md)
- [docs/architecture.mermaid](docs/architecture.mermaid)
- [docs/mcp-contracts.md](docs/mcp-contracts.md)
- [docs/product-catalog.json](docs/product-catalog.json)
- [docs/verification/managed-conformance-manifest.json](docs/verification/managed-conformance-manifest.json)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [skills/reverse-engineer-anything/SKILL.md](skills/reverse-engineer-anything/SKILL.md)
- [skills/reverse-engineer-anything/references/native-and-artifacts.md](skills/reverse-engineer-anything/references/native-and-artifacts.md)
- [src/generatedPackageMetadata.ts](src/generatedPackageMetadata.ts)
- [tests/boundary/filesystem/setupSkill.test.ts](tests/boundary/filesystem/setupSkill.test.ts)

</details>



REA (Reverse Engineer Anything) is a local-only CLI and Model Context Protocol (MCP) server designed to provide coding agents with advanced reverse engineering capabilities. It enables analysis of native binaries, managed assemblies, JavaScript/Electron applications, browsers, Android packages, and firmware. REA helps developers understand how features work at a low level and facilitates building interoperable implementations.

The project aims to bridge high-level agentic workflows with low-level static and dynamic analysis by integrating with various analysis providers like Hopper Disassembler, Ghidra, JADX, and Playwright [README.md:52]().

## Core Purpose

REA addresses the "black box" problem in software development, where source code is unavailable. It provides a systematic way for agents to:
1.  **Decompile**: Recover readable pseudo-code and assembly from binaries [README.md:66-68]().
2.  **Understand**: Trace execution flows, cross-references, and call graphs to explain how features or algorithms work [README.md:68-69]().
3.  **Recreate**: Translate observed logic into new code tailored to a different technology stack, UI, or requirements [README.md:69-70]().

## Architecture Layers

REA is structured as a layered ESM TypeScript application where dependencies flow inward from adapters to the core domain logic. This design ensures modularity and maintainability.

**Diagram: REA Layered Architecture**
```mermaid
graph TD
    A[CLI / MCP Adapters] --> B[Application Layer]
    B --> C[Contracts Layer]
    C --> D[Domain Layer]
    D --> E[Providers Layer]
    E --> F[External Tools / Systems]

    style A fill:#ace,stroke:#333,stroke-width:2px
    style B fill:#bce,stroke:#333,stroke-width:2px
    style C fill:#cde,stroke:#333,stroke-width:2px
    style D fill:#def,stroke:#333,stroke-width:2px
    style E fill:#efg,stroke:#333,stroke-width:2px
    style F fill:#fgh,stroke:#333,stroke-width:2px

    click A "2.1. Entry Points and Dispatching"
    click B "2.4. Application Layer"
    click C "2.3. Contracts and Tool Catalog"
    click D "2.2. Domain Layer"
    click E "4. Analysis Providers"
    click F "4. Analysis Providers"
```
Sources: [README.md:52](), [package.json:32-34]()

## Tool Catalog

REA exposes a comprehensive set of tools to agents and CLI users, categorized by their function and target. The `product-catalog.json` lists 133 tools across various families [docs/product-catalog.json:13-228]().

**Diagram: REA Tool Families and Counts**
```mermaid
pie title "REA Tool Families (Total: 133)"
    "direct (41)" : 41
    "enhanced (14)" : 14
    "native (7)" : 7
    "artifact (5)" : 5
    "managed (7)" : 7
    "firmware (2)" : 2
    "android (5)" : 5
    "browser (11)" : 11
    "electron (5)" : 5
    "javascript-runtime (2)" : 2
    "application (13)" : 13
    "session (21)" : 21
```
Sources: [docs/product-catalog.json:13-228]()

## Integration with Coding Agents

REA is designed to integrate seamlessly with various AI coding assistants, providing them with the ability to perform reverse engineering tasks. The `rea setup` command registers REA with supported agents and installs matching workflow instructions [README.md:53-55]().

**Diagram: Agent Integration and MCP Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Agent[("Coding Agent<br>(Claude Code, Cursor, VS Code, etc.)")]
    end

    subgraph "REA Code Entity Space"
        CLI_Entry["scripts/rea.mjs<br>(CLI Dispatcher)"]
        MCP_Server["src/main.ts<br>(MCP Server)"]
        ToolCatalog["docs/product-catalog.json<br>(Tool Definitions)"]
        AnalysisProviders["src/providers/*<br>(Hopper, Ghidra, JADX, etc.)"]
    end

    subgraph "External Analysis Systems"
        Hopper["Hopper Disassembler"]
        Ghidra["Ghidra"]
        JADX["JADX"]
        Playwright["Playwright (Browser/Electron)"]
        BinwalkUnblob["Binwalk/Unblob (Firmware)"]
    end

    Agent -- "User Prompt (e.g., 'Analyze app X')" --> CLI_Entry
    CLI_Entry -- "npx rea-agents setup" --> MCP_Server
    MCP_Server -- "Registers Tools" --> Agent
    Agent -- "MCP Tool Call (e.g., analyze_function)" --> MCP_Server
    MCP_Server -- "Dispatches to" --> AnalysisProviders
    AnalysisProviders -- "Interacts with" --> Hopper
    AnalysisProviders -- "Interacts with" --> Ghidra
    AnalysisProviders -- "Interacts with" --> JADX
    AnalysisProviders -- "Interacts with" --> Playwright
    AnalysisProviders -- "Interacts with" --> BinwalkUnblob
    AnalysisProviders -- "Returns Results" --> MCP_Server
    MCP_Server -- "Returns Evidence" --> Agent
    ToolCatalog -- "Informs" --> MCP_Server
```
Sources: [README.md:53-55](), [README.md:70-86](), [package.json:32-34](), [docs/product-catalog.json:13-228]()

## Navigation Guide

This wiki is organized to help you move from initial setup to deep architectural understanding.

### Getting Started
This page covers how to install REA via `npx` or `npm`, run `rea setup` to configure agents and analysis providers, and use `rea doctor` for diagnostics. It also details how to connect various coding agents like Claude Code, Codex, Cursor, Gemini, and VS Code. For details, see [Getting Started](#1.1).
Sources: [README.md:58-64](), [README.md:70-86](), [README.md:100-102]()

### Configuration Reference
This section provides a detailed reference for REA's configuration options, including environment variables, the `AppConfig` and `parseConfig` mechanisms, client configuration documents, identity and product catalog digests, and paths for cache and state management. For details, see [Configuration Reference](#1.2).
Sources: [skills/reverse-engineer-anything/SKILL.md:5-7]()

### Setup, Doctor and Uninstall Internals
This page delves into the internal workings of REA's setup, doctor, and uninstall processes. It explains the plan/apply state machine used by `runSetup`, the roles of `SetupHost` and `SetupSkill`, how `Doctor` performs diagnostics and checks client registration status, and the mechanics of `Uninstall`. For details, see [Setup, Doctor and Uninstall Internals](#1.3).
Sources: [README.md:100-102](), [README.md:160-162]()

---

