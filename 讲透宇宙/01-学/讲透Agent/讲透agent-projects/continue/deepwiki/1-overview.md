<!-- source: DeepWiki mcp.deepwiki.com · repo continuedev/continue · page 1 Overview · fetched 2026-10-29 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.continue/environment.json](.continue/environment.json)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.gitignore](.gitignore)
- [.husky/pre-commit](.husky/pre-commit)
- [.prettierignore](.prettierignore)
- [.prettierrc](.prettierrc)
- [README.md](README.md)
- [binary/package-lock.json](binary/package-lock.json)
- [core/package-lock.json](core/package-lock.json)
- [core/package.json](core/package.json)
- [core/protocol/coreWebview.ts](core/protocol/coreWebview.ts)
- [extensions/intellij/README.md](extensions/intellij/README.md)
- [extensions/vscode/README.md](extensions/vscode/README.md)
- [extensions/vscode/package-lock.json](extensions/vscode/package-lock.json)
- [extensions/vscode/package.json](extensions/vscode/package.json)
- [gui/package-lock.json](gui/package-lock.json)
- [gui/package.json](gui/package.json)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [packages/config-yaml/package.json](packages/config-yaml/package.json)

</details>



## Purpose and Scope

This document provides a high-level introduction to the Continue codebase architecture, explaining how the major components fit together to deliver AI-powered coding assistance across multiple IDE platforms. It covers the core architectural patterns, key subsystems, and their interactions.

For detailed information about specific subsystems:
- For setup instructions, see [Getting Started](#1.1)
- For core concepts like the IDE abstraction and LLM providers, see [Key Concepts](#1.2)
- For IDE-specific implementation details, see [VS Code Extension](#6) and [IntelliJ Plugin](#7)
- For the user interface implementation, see [User Interface](#8)

## What is Continue?

Continue is an open-source AI code assistant that provides chat, autocomplete, and inline editing capabilities within development environments. The project is structured as a cross-platform system with the following characteristics:

- **Multi-IDE Support**: Native extensions for VS Code, IntelliJ IDEA, and a CLI interface. [extensions/vscode/package.json:1-58](), [README.md:21-22]()
- **Provider Agnostic**: Supports a wide range of LLM providers (OpenAI, Anthropic, Ollama, Bedrock, etc.) through a unified abstraction layer. [core/package.json:57-66](), [core/package.json:99-101]()
- **Modular Architecture**: Shared core business logic with platform-specific IDE adapters. [core/package.json:4-4]()
- **Configuration Flexibility**: Supports both JSON and YAML configuration formats with local and remote sync. [extensions/vscode/package.json:136-150](), [packages/config-yaml/package.json:1-17]()

**Primary Distribution Artifacts**:
- **VS Code Extension**: Published to VS Code Marketplace and Open VSX. [extensions/vscode/package.json:1-24]()
- **IntelliJ Plugin**: Published to JetBrains Marketplace. [README.md:41-45]()
- **CLI Tool (`@continuedev/cli`)**: Distributed as an npm package or standalone binary for terminal-based AI assistance. [README.md:37-39](), [binary/package-lock.json:27-29]()

Sources: [extensions/vscode/package.json:1-152](), [core/package.json:1-135](), [gui/package.json:1-121](), [README.md:1-64](), [binary/package-lock.json:1-44]()

## System Architecture

### High-Level Component Structure

```mermaid
graph TB
    subgraph "IDE_Layer"
        ["VsCodeExtension"]
        ["ContinuePluginService"]
        ["CLITool"]
    end
    
    subgraph "Core_Layer"
        ["Core"]
        ["ConfigHandler"]
        ["CodebaseIndexer"]
        ["CompletionProvider"]
    end
    
    subgraph "GUI_Layer"
        ["ReactApp"]
        ["ReduxStore"]
    end
    
    subgraph "LLM_Abstraction"
        ["ILLM_Interface"]
        ["BaseLLM"]
        ["LLM_Provider_Implementations"]
    end
    
    ["VsCodeExtension"] -->|"InProcessMessenger"| ["Core"]
    ["ContinuePluginService"] -->|"CoreMessenger"| ["Core"]
    ["CLITool"] -->|"DirectInstantiation"| ["Core"]
    
    ["VsCodeExtension"] -->|embeds| ["ReactApp"]
    ["ContinuePluginService"] -->|"JCEF_Browser"| ["ReactApp"]
    
    ["Core"] --> ["ConfigHandler"]
    ["Core"] --> ["CodebaseIndexer"]
    ["Core"] --> ["CompletionProvider"]
    
    ["ReactApp"] --> ["ReduxStore"]
    
    ["Core"] -->|instantiates| ["ILLM_Interface"]
    ["ILLM_Interface"] <|-- ["BaseLLM"]
    ["BaseLLM"] <|-- ["LLM_Provider_Implementations"]
```

Sources: [core/package.json:1-135](), [gui/package.json:1-121](), [extensions/vscode/package.json:1-60](), [core/package.json:4-4]()

### Core Orchestration and IDE Adapters

The system bridges "Natural Language Space" (user intent) to "Code Entity Space" (files, symbols, diffs) through the `Core` orchestrator and platform-specific `IDE` interface implementations.

```mermaid
graph LR
    subgraph "Natural_Language_Space"
        ["Chat_Component"]
        ["ContinueInputBox_TipTap"]
    end

    subgraph "Core_Logic"
        ["Core_Class"]
        ["ConfigHandler_Service"]
        ["CodebaseIndexer_Service"]
    end

    subgraph "Code_Entity_Space"
        ["VsCodeIde_Implementation"]
        ["IntelliJIde_Implementation"]
        ["ripgrep_Service"]
        ["LanceDB_VectorStore"]
    end

    ["Chat_Component"] --> ["Core_Class"]
    ["Core_Class"] --> ["ConfigHandler_Service"]
    ["Core_Class"] --> ["VsCodeIde_Implementation"]
    ["Core_Class"] --> ["IntelliJIde_Implementation"]
    ["CodebaseIndexer_Service"] --> ["LanceDB_VectorStore"]
    ["VsCodeIde_Implementation"] --> ["ripgrep_Service"]
```

**Core Orchestration**:
- **VS Code**: The extension process instantiates `Core` as the main logic provider. [extensions/vscode/package.json:58-58]()
- **IntelliJ**: Communicates with the core logic, often via a separate process handled by the plugin service. [README.md:43-45]()
- **CLI**: Runs logic directly via commander-based commands. [binary/package-lock.json:14-14]()

Sources: [core/package.json:1-135](), [extensions/vscode/package.json:1-152](), [README.md:1-64]()

## Message-Passing Architecture

Continue uses a type-safe message-passing system to enable communication between the GUI, the IDE, and the Core logic.

### Protocol Boundaries
The system defines primary protocol boundaries to maintain strict typing:
1. **Core Protocols**: Communication between IDE extensions and Core logic. [core/package.json:1-15]()
2. **Webview Protocols**: Communication between the IDE host and the React-based GUI. [extensions/vscode/package.json:56-56]()
3. **Pass-Through**: Direct GUI-to-Core messages for performance-sensitive operations like LLM streaming. [gui/package-lock.json:67-67]()

Sources: [core/package.json:1-135](), [gui/package.json:1-121](), [extensions/vscode/package.json:1-152]()

## Key Subsystems

### ConfigHandler
Manages configuration loading and profile selection. It supports modern YAML (`@continuedev/config-yaml`) and legacy JSON formats (`config.json`). [packages/config-yaml/package.json:1-47](), [extensions/vscode/package.json:62-65]()

### CodebaseIndexer
Provides semantic search over the codebase.
- **Storage**: Uses `LanceDB` (`vectordb` package) for local vector storage. [core/package-lock.json:74-74](), [binary/package-lock.json:24-24]()
- **Process**: Chunks documents and generates embeddings. [core/package-lock.json:25-25]()

### Autocomplete System
Provides inline code completions and "Next Edit" predictions. [extensions/vscode/package.json:111-120]()
- **Context**: Integrates with Language Server Protocols (LSP) and local file history. [extensions/vscode/package-lock.json:56-56]()

Sources: [core/package.json:1-135](), [extensions/vscode/package.json:1-152](), [packages/config-yaml/package.json:1-47]()

## GUI Architecture

The GUI is a React application using Redux for state management, built with Vite. [gui/package.json:1-10](), [gui/package.json:105-105]()

- **State Management**: Uses `@reduxjs/toolkit` to manage chat sessions and UI state. [gui/package.json:25-25]()
- **Rich Input**: Uses `TipTap` for the rich-text input box supporting context items and slash commands. [gui/package.json:26-38]()
- **Rendering**: Supports Markdown, LaTeX, and Mermaid diagrams in the chat. [gui/package.json:51-59](), [gui/package.json:48-48]()

Sources: [gui/package.json:1-121](), [gui/package-lock.json:1-111]()

## Build System

Continue uses a monorepo structure with specialized build pipelines for different components.

| Component | Tool | Key Scripts |
|-----------|------|-------------|
| **Core** | `tsc` | `npm run build` [core/package.json:10-10]() |
| **GUI** | `vite` | `npm run build` [gui/package.json:10-10]() |
| **VS Code** | `esbuild` | `npm run build` (via extension scripts) [extensions/vscode/package-lock.json:80-80]() |
| **CLI / Binary** | `pkg` / `esbuild` | `npm run build` [binary/package-lock.json:37-39]() |

Sources: [core/package.json:1-15](), [gui/package.json:1-17](), [binary/package-lock.json:30-43]()

---

