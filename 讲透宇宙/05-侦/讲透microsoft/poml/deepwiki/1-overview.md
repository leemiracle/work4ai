<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/poml · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CITATION.cff](CITATION.cff)
- [README.md](README.md)
- [docs/index.md](docs/index.md)
- [docs/vscode/index.md](docs/vscode/index.md)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



## Purpose and Scope

This document provides an architectural overview of POML (Prompt Orchestration Markup Language), a comprehensive system for structured prompt engineering with Large Language Models. POML addresses common challenges in prompt development through a markup language with HTML-like syntax, integrated development tools, and multi-language SDK support.

For specific implementation details of individual components, see [Core Architecture](#3). For getting started with POML usage, see [Getting Started](#2). For language model provider configuration, see [Provider Configuration](#6.1).

## System Architecture

POML consists of four main subsystems: the VS Code extension ecosystem, core processing engine, multi-language SDKs, and build/distribution infrastructure.

```mermaid
graph TB
    subgraph "VS Code Extension Ecosystem"
        VSCodeExt["vscode-extension<br/>(package.json)"]
        LSP["Language Server<br/>(lsp)"]
        WebviewPanel["Webview Panel<br/>(webview)"]
        ChatParticipant["Chat Participant<br/>(chat)"]
    end
    
    subgraph "Core Processing Engine"
        PomlFile["PomlFile<br/>(packages/core/pomlFile.ts)"]
        Parser["XML Parser<br/>(@xml-tools/parser)"]
        ComponentSystem["Component Registry<br/>(packages/core/components)"]
        Writer["Writer System<br/>(packages/core/writer)"]
    end
    
    subgraph "Multi-Language SDKs"
        PythonSDK["Python Package<br/>(python)"]
        JSSDKCore["pomljs Core<br/>(packages/core)"]
        CLI["CLI Tools<br/>(packages/cli)"]
    end
    
    subgraph "Language Model Integration"
        Providers["LM Providers<br/>(packages/core/providers)"]
        AISDKs["AI SDKs<br/>(@ai-sdk/*)"]
    end
    
    VSCodeExt --> LSP
    VSCodeExt --> WebviewPanel
    VSCodeExt --> ChatParticipant
    
    LSP --> PomlFile
    WebviewPanel --> PomlFile
    ChatParticipant --> PomlFile
    
    PomlFile --> Parser
    PomlFile --> ComponentSystem
    PomlFile --> Writer
    
    PythonSDK --> PomlFile
    JSSDKCore --> PomlFile
    CLI --> PomlFile
    
    PomlFile --> Providers
    Providers --> AISDKs
```

**Sources:** [package.json:1-493](), [README.md:1-131](), [docs/index.md:1-38]()

## Core Processing Pipeline

The POML processing engine transforms markup documents through a multi-stage pipeline, handling XML parsing, component rendering, and output generation.

```mermaid
graph LR
    subgraph "Input Stage"
        PomlMarkup["POML Markup<br/>(.poml files)"]
        ContextFiles["Context Files<br/>(documents, images)"]
        Stylesheets["Stylesheets<br/>(CSS-like styling)"]
    end
    
    subgraph "Parsing Stage"
        XMLParser["@xml-tools/parser<br/>(parseXml)"]
        ASTBuilder["AST Builder<br/>(buildElementTree)"]
    end
    
    subgraph "Component Stage"
        ComponentRegistry["Component Registry<br/>(registerComponent)"]
        ReactRenderer["React Renderer<br/>(renderToElements)"]
        ElementTree["React Element Tree"]
    end
    
    subgraph "Output Stage"
        WriterSystem["Writer System<br/>(Writer class)"]
        MessageArrays["Message Arrays<br/>(ChatMessage[])"]
        RichContent["Rich Content<br/>(RichContent)"]
        SourceMaps["Source Maps<br/>(SourceMap)"]
    end
    
    PomlMarkup --> XMLParser
    ContextFiles --> ASTBuilder
    Stylesheets --> ASTBuilder
    
    XMLParser --> ASTBuilder
    ASTBuilder --> ComponentRegistry
    ComponentRegistry --> ReactRenderer
    ReactRenderer --> ElementTree
    
    ElementTree --> WriterSystem
    WriterSystem --> MessageArrays
    WriterSystem --> RichContent
    WriterSystem --> SourceMaps
```

**Sources:** [package.json:458-461](), [package.json:473-476]()

## VS Code Extension Architecture

The VS Code extension serves as the primary development interface, integrating language server capabilities, preview functionality, and direct language model testing.

```mermaid
graph TB
    subgraph "Extension Activation"
        ExtensionMain["extension.js<br/>(main entry point)"]
        ActivationEvents["Activation Events<br/>(onWebviewPanel, onChatParticipant)"]
    end
    
    subgraph "Language Server Protocol"
        LSPClient["Language Client<br/>(vscode-languageclient)"]
        LSPServer["Language Server<br/>(vscode-languageserver)"]
        DiagnosticsEngine["Diagnostics<br/>(publishDiagnostics)"]
        CompletionProvider["Completion<br/>(onCompletion)"]
        HoverProvider["Hover Info<br/>(onHover)"]
    end
    
    subgraph "User Interface"
        CommandPalette["Commands<br/>(poml.test, poml.showPreview)"]
        WebviewPreview["Preview Panel<br/>(poml.preview)"]
        PromptGallery["Prompt Gallery<br/>(pomlPromptGallery)"]
        ChatRunner["Chat Participant<br/>(poml.runner)"]
    end
    
    subgraph "Testing Infrastructure"
        TestCommands["Test Commands<br/>(poml.test, poml.testNonChat)"]
        ModelProviders["Model Providers<br/>(openai, anthropic, vscode)"]
        StreamingOutput["Streaming Response<br/>(SSE handling)"]
    end
    
    ExtensionMain --> ActivationEvents
    ActivationEvents --> LSPClient
    ActivationEvents --> CommandPalette
    
    LSPClient --> LSPServer
    LSPServer --> DiagnosticsEngine
    LSPServer --> CompletionProvider
    LSPServer --> HoverProvider
    
    CommandPalette --> WebviewPreview
    CommandPalette --> PromptGallery
    CommandPalette --> ChatRunner
    CommandPalette --> TestCommands
    
    TestCommands --> ModelProviders
    ModelProviders --> StreamingOutput
```

**Sources:** [package.json:18-24](), [package.json:71-174](), [package.json:176-183](), [package.json:245-369]()

## Language Model Provider Integration

POML integrates with multiple language model providers through a unified interface, supporting both streaming and structured outputs.

| Provider | Configuration Key | SDK Package | API Support |
|----------|------------------|-------------|-------------|
| OpenAI | `openai` | `@ai-sdk/openai` | Chat Completion, Response API |
| Anthropic | `anthropic` | `@ai-sdk/anthropic` | Messages API |
| Google | `google` | `@ai-sdk/google` | Gemini API |
| Azure OpenAI | `microsoft` | `@ai-sdk/azure` | Chat Completion |
| VS Code LM | `vscode` | VS Code LM API | Copilot Integration |

```mermaid
graph LR
    subgraph "POML Document Processing"
        PomlDoc["POML Document"]
        MessageGen["Message Generation<br/>(toMessages)"]
        SchemaGen["Schema Generation<br/>(responseSchema)"]
    end
    
    subgraph "Provider Configuration"
        ConfigManager["Config Manager<br/>(poml.languageModel.*)"]
        ProviderRouter["Provider Router<br/>(getProvider)"]
    end
    
    subgraph "AI SDK Integration"
        OpenAIProvider["@ai-sdk/openai<br/>(openai)"]
        AnthropicProvider["@ai-sdk/anthropic<br/>(anthropic)"]
        GoogleProvider["@ai-sdk/google<br/>(google)"]
        AzureProvider["@ai-sdk/azure<br/>(azure)"]
        VSCodeProvider["VS Code LM API<br/>(vscode.lm)"]
    end
    
    subgraph "Response Processing"
        StreamHandler["Stream Handler<br/>(streamText)"]
        StructuredOutput["Structured Output<br/>(generateObject)"]
        ErrorHandler["Error Handler<br/>(LanguageModelError)"]
    end
    
    PomlDoc --> MessageGen
    PomlDoc --> SchemaGen
    MessageGen --> ConfigManager
    
    ConfigManager --> ProviderRouter
    ProviderRouter --> OpenAIProvider
    ProviderRouter --> AnthropicProvider
    ProviderRouter --> GoogleProvider
    ProviderRouter --> AzureProvider
    ProviderRouter --> VSCodeProvider
    
    OpenAIProvider --> StreamHandler
    AnthropicProvider --> StreamHandler
    GoogleProvider --> StreamHandler
    AzureProvider --> StreamHandler
    VSCodeProvider --> StreamHandler
    
    StreamHandler --> StructuredOutput
    StreamHandler --> ErrorHandler
```

**Sources:** [package.json:245-328](), [package.json:450-461]()

## Multi-Language SDK Architecture

POML provides synchronized APIs across Python and JavaScript/TypeScript environments, with shared component definitions and identical processing logic.

```mermaid
graph TB
    subgraph "Shared Specifications"
        ComponentSpec["Component Specs<br/>(component-spec.json)"]
        PomlGrammar["POML Grammar<br/>(poml.tmLanguage.json)"]
        TypeDefinitions["Type Definitions<br/>(packages/core/types)"]
    end
    
    subgraph "JavaScript/TypeScript SDK"
        CorePackage["@pomljs/core<br/>(packages/core)"]
        ReactComponents["React Components<br/>(packages/core/components)"]
        CLIPackage["CLI Package<br/>(packages/cli)"]
        WebpackConfig["Webpack Config<br/>(webpack.config.*.js)"]
    end
    
    subgraph "Python SDK"
        PythonCore["poml Package<br/>(python/poml)"]
        AutoGenTags["Generated Tags<br/>(python/poml/_tags.py)"]
        PythonCLI["poml-cli<br/>(python/poml/cli)"]
        SetupPy["Setup Configuration<br/>(python/setup.py)"]
    end
    
    subgraph "Build Pipeline"
        ComponentParser["Component Parser<br/>(parseComments.js)"]
        CodeGeneration["Code Generation<br/>(generate-component-spec)"]
        CrossSync["Cross-Language Sync<br/>(CI/CD pipeline)"]
    end
    
    ComponentSpec --> ReactComponents
    ComponentSpec --> AutoGenTags
    PomlGrammar --> CorePackage
    PomlGrammar --> PythonCore
    
    CorePackage --> CLIPackage
    PythonCore --> PythonCLI
    
    ComponentParser --> CodeGeneration
    CodeGeneration --> ComponentSpec
    CodeGeneration --> CrossSync
    
    CrossSync --> ReactComponents
    CrossSync --> AutoGenTags
```

**Sources:** [package.json:378-379](), [package.json:41-63](), [package.json:371-394]()

## Build and Distribution System

The project uses a sophisticated multi-platform build system with GitHub Actions for continuous integration and deployment across VS Code Marketplace, PyPI, and NPM.

```mermaid
graph TB
    subgraph "Source Code"
        TypeScriptSrc["TypeScript Source<br/>(packages/, poml-vscode)"]
        PythonSrc["Python Source<br/>(python)"]
        ConfigFiles["Configuration<br/>(package.json, setup.py)"]
        DocsSource["Documentation<br/>(docs/, mkdocs.yml)"]
    end
    
    subgraph "Build Tools"
        WebpackBuild["Webpack<br/>(webpack.config.*.js)"]
        TypeScriptBuild["TypeScript Compiler<br/>(tspc)"]
        PythonBuild["Python Build<br/>(pip, wheel)"]
        DocsBuild["MkDocs<br/>(mkdocs build)"]
    end
    
    subgraph "Quality Gates"
        ESLintCheck["ESLint<br/>(eslint packages)"]
        PrettierCheck["Prettier<br/>(prettier --check)"]
        JestTests["Jest Tests<br/>(jest)"]
        HuskyHooks["Husky Hooks<br/>(lint-staged)"]
    end
    
    subgraph "Artifacts"
        VSIXPackage["VS Code Extension<br/>(.vsix)"]
        NPMPackage["NPM Package<br/>(pomljs)"]
        PythonWheel["Python Wheel<br/>(poml)"]
        DocsStaticSite["Documentation Site<br/>(GitHub Pages)"]
    end
    
    subgraph "Distribution"
        VSCodeMarketplace["VS Code Marketplace<br/>(poml-team.poml)"]
        NPMRegistry["NPM Registry<br/>(npmjs.com)"]
        PyPIRegistry["PyPI Registry<br/>(pypi.org)"]
        GitHubPages["GitHub Pages<br/>(microsoft.github.io/poml)"]
    end
    
    TypeScriptSrc --> WebpackBuild
    TypeScriptSrc --> TypeScriptBuild
    PythonSrc --> PythonBuild
    DocsSource --> DocsBuild
    
    WebpackBuild --> ESLintCheck
    TypeScriptBuild --> PrettierCheck
    PythonBuild --> JestTests
    
    ESLintCheck --> VSIXPackage
    PrettierCheck --> NPMPackage
    JestTests --> PythonWheel
    DocsBuild --> DocsStaticSite
    
    VSIXPackage --> VSCodeMarketplace
    NPMPackage --> NPMRegistry
    PythonWheel --> PyPIRegistry
    DocsStaticSite --> GitHubPages
```

**Sources:** [package.json:371-394](), [package.json:396-407](), [package.json:408-493]()

---

