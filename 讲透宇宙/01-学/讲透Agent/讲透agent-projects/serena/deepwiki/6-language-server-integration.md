<!-- source: DeepWiki mcp.deepwiki.com · repo oraios/serena · page 6 Language Server Integration · fetched 2026-10-29 -->

# Language Server Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pytest.yml](.github/workflows/pytest.yml)
- [.gitignore](.gitignore)
- [.serena/memories/adding_new_language_support_guide.md](.serena/memories/adding_new_language_support_guide.md)
- [README.md](README.md)
- [docs/01-about/020_programming-languages.md](docs/01-about/020_programming-languages.md)
- [scripts/update_downloaded_dependency_hashes.py](scripts/update_downloaded_dependency_hashes.py)
- [src/solidlsp/dependency_provider.py](src/solidlsp/dependency_provider.py)
- [src/solidlsp/language_servers/common.py](src/solidlsp/language_servers/common.py)
- [src/solidlsp/language_servers/erlang_language_server.py](src/solidlsp/language_servers/erlang_language_server.py)
- [src/solidlsp/language_servers/groovy_language_server.py](src/solidlsp/language_servers/groovy_language_server.py)
- [src/solidlsp/ls.py](src/solidlsp/ls.py)
- [src/solidlsp/ls_config.py](src/solidlsp/ls_config.py)
- [src/solidlsp/ls_types.py](src/solidlsp/ls_types.py)
- [src/solidlsp/ls_utils.py](src/solidlsp/ls_utils.py)
- [src/solidlsp/lsp_protocol_handler/lsp_constants.py](src/solidlsp/lsp_protocol_handler/lsp_constants.py)
- [src/solidlsp/lsp_protocol_handler/lsp_types.py](src/solidlsp/lsp_protocol_handler/lsp_types.py)
- [src/solidlsp/resources/downloaded_dependency_hashes.json](src/solidlsp/resources/downloaded_dependency_hashes.json)
- [src/solidlsp/settings.py](src/solidlsp/settings.py)
- [src/solidlsp/util/cache.py](src/solidlsp/util/cache.py)
- [test/conftest.py](test/conftest.py)
- [test/serena/test_serena_agent.py](test/serena/test_serena_agent.py)
- [test/solidlsp/erlang/test_erlang_symbol_names.py](test/solidlsp/erlang/test_erlang_symbol_names.py)
- [test/solidlsp/test_text_utils.py](test/solidlsp/test_text_utils.py)

</details>



This page provides an overview of how Serena integrates with language servers to enable semantic, symbol-level code understanding and editing across 30+ programming languages. It describes the two available backends, the architecture of the `solidlsp` library, and how the system is structured to be language-agnostic.

For details on individual components, see the child pages:
- The `SolidLanguageServer` base class and LSP request methods: [SolidLanguageServer Framework](#6.1)
- Managing multiple servers per project: [Language Server Manager](#6.2)
- All concrete language server implementations: [Language Server Implementations](#6.3)
- Runtime dependency installation: [Runtime Dependencies](#6.4)
- Symbol caching: [Caching System](#6.5)
- In-memory file tracking: [File Buffer Management](#6.6)
- Symbol data model: [Symbol Abstraction](#6.7)
- Code editing operations: [Code Editor Operations](#6.8)
- JetBrains alternative backend: [JetBrains Integration](#6.9)
- Low-level LSP communication: [LSP Protocol Handler](#6.10)

For how the Project class uses the Language Server Manager, see [Project Lifecycle](#5.1).

---

## Purpose

Serena's tool system exposes IDE-like capabilities — finding symbols, resolving references, navigating definitions, renaming, and editing — to an LLM agent. These capabilities require deep semantic analysis of source code, which is provided by one of two backends:

| Backend | Implementation | Source |
|---|---|---|
| **LSP** | `solidlsp` library wrapping external language server processes | `src/solidlsp/` |
| **JetBrains** | HTTP client communicating with a JetBrains IDE plugin | `src/serena/jetbrains/` |

The LSP backend is the primary, fully open-source option. The JetBrains backend is an alternative that delegates analysis to a running JetBrains IDE instance. Serena supports specialized servers like **GDScript** (Godot), **CUE**, and **Svelte**.

Sources: [README.md:98-105](), [docs/01-about/020_programming-languages.md:10-16](), [src/solidlsp/ls.py:24-32]()

---

## The Two Backends

**Diagram: Serena's Two Language Analysis Backends**

```mermaid
graph TD
    subgraph "NaturalLanguageSpace" ["Natural Language Space (LLM/Agent)"]
        [SerenaAgent] --> [SymbolTools]
        [SymbolTools] -- "FindSymbolTool" --> [LSM]
        [SymbolTools] -- "FindReferencingSymbolsTool" --> [LSM]
    end

    subgraph "CodeEntitySpace" ["Code Entity Space (Implementation)"]
        [LSM] ["LanguageServerManager"]
        [SLS] ["SolidLanguageServer"]
        [JB] ["JetBrainsPluginClientManager"]
        
        [LSProc] ["LanguageServerProcess"]
        [JBPlugin] ["JetBrainsPluginClient"]
    end
    
    [LSM] --> [SLS]
    [SLS] --> [LSProc]
    [LSM] --> [JB]
    [JB] --> [JBPlugin]
```

Sources: [README.md:68-81](), [src/solidlsp/ls.py:88-118](), [src/solidlsp/ls_config.py:90-180](), [test/serena/test_serena_agent.py:15-36]()

---

## solidlsp — The LSP Abstraction Library

`solidlsp` is a synchronous LSP client library located at `src/solidlsp/`. It provides symbolic reasoning, two-tier caching, file buffer management, and synchronous operation.

The library's core components are:

| Class / Module | File | Role |
|---|---|---|
| `SolidLanguageServer` | `src/solidlsp/ls.py` | Abstract base class for all LS implementations [src/solidlsp/ls.py:9-16]() |
| `LSPFileBuffer` | `src/solidlsp/ls.py` | In-memory file content tracking and LS notification [src/solidlsp/ls.py:90-118]() |
| `LanguageServerDependencyProvider` | `src/solidlsp/ls.py` | Manages binary download and launch command creation [src/solidlsp/ls.py:27-32]() |
| `LanguageServerProcess` | `src/solidlsp/ls_process.py` | JSON-RPC I/O to the subprocess [src/solidlsp/ls.py:36-36]() |
| `LanguageServerId` | `src/solidlsp/ls_config.py` | Enum of all supported language identifiers [src/solidlsp/ls_config.py:90-180]() |
| `LanguageServerConfig` | `src/solidlsp/ls_config.py` | Per-session LS configuration [src/solidlsp/ls_config.py:26-26]() |
| `SolidLSPSettings` | `src/solidlsp/settings.py` | Global solidlsp directory and per-LS custom settings |

Sources: [src/solidlsp/ls.py:1-55](), [src/solidlsp/ls_config.py:1-180]()

---

## Supported Languages

The `LanguageServerId` enum in `src/solidlsp/ls_config.py` defines all supported language identifiers. Each maps to a concrete `SolidLanguageServer` subclass.

**Standard (auto-detected) languages:**

| Language | Enum Value | LS Class / Server Type |
|---|---|---|
| Python | `python` | `PyrightServer` (Default) |
| JavaScript/TypeScript | `typescript` | `TypeScriptLanguageServer` |
| Java | `java` | `EclipseJDTLS` |
| Go | `go` | `Gopls` |
| Rust | `rust` | `RustAnalyzer` |
| C# | `csharp` | `CSharpLanguageServer` (Roslyn) |
| C/C++ | `cpp` | `ClangdLanguageServer` |
| Ruby | `ruby` | `RubyLsp` |
| Kotlin | `kotlin` | `KotlinLanguageServer` |
| Dart | `dart` | `DartLanguageServer` |
| PHP | `php` | `Intelephense` |
| Elixir | `elixir` | `NextLS` |
| Swift | `swift` | `SourcekitLsp` |
| GDScript | `gdscript` | Godot Built-in LSP (TCP) |
| Svelte | `svelte` | `svelte-language-server` |
| CUE | `cue` | `cue lsp` |

Sources: [src/solidlsp/ls_config.py:90-180](), [docs/01-about/020_programming-languages.md:19-122](), [test/serena/test_serena_agent.py:46-50]()

---

## Architecture Overview

**Diagram: solidlsp Component Architecture**

```mermaid
graph TD
    subgraph "ConfigurationAndFactory"
        [CONF] ["LanguageServerConfig"]
        [SETTINGS] ["SolidLSPSettings"]
        [LANG] ["LanguageServerId"]
        [CREATE] ["SolidLanguageServer.create()"]
    end

    subgraph "RuntimeInstances"
        [SLS] ["SolidLanguageServer"]
        [DEP] ["LanguageServerDependencyProvider"]
        [PROC] ["LanguageServerProcess"]
        [BUF] ["LSPFileBuffer"]
        [CACHE] ["DocumentSymbolsCache"]
    end

    [CONF] --> [CREATE]
    [SETTINGS] --> [CREATE]
    [LANG] --> [CREATE]
    [CREATE] --> [SLS]
    [SLS] --> [DEP]
    [DEP] --> [PROC]
    [SLS] --> [BUF]
    [SLS] --> [CACHE]
```

Sources: [src/solidlsp/ls.py:88-118](), [src/solidlsp/ls_config.py:90-180]()

---

## Language Server Lifecycle

A language server instance is created via a factory method `SolidLanguageServer.create()` that reads the `LanguageServerId` enum to resolve the concrete class [src/solidlsp/ls.py:91-92]().

The server startup typically involves:
1. `LanguageServerDependencyProvider` resolving or installing core dependencies [src/solidlsp/dependency_provider.py:1-50]().
2. Launching the `LanguageServerProcess` subprocess [src/solidlsp/ls_process.py:36-36]().
3. Establishing communication (Stdio or TCP).

The system avoids temporary file clutter by using OS-specific temporary directories for internal operations.

Sources: [src/solidlsp/ls.py:91-92](), [test/conftest.py:66-99]()

---

## Dependency Management

Each language server implementation provides a `LanguageServerDependencyProvider` that handles:

1. Checking whether a required binary/JAR/npm package is already installed.
2. Downloading and installing it into `ls_resources_dir` if not present [src/solidlsp/language_servers/common.py:84-101]().
3. Returning the launch command and any required environment variables.

For example, **Java** support can use an upstream `jdtls` if `jdtls_path` is configured, and **Go** support relies on `gopls` being available on the system path [docs/01-about/020_programming-languages.md:81-82]().

Sources: [src/solidlsp/language_servers/common.py:19-101](), [docs/01-about/020_programming-languages.md:31-122](), [.github/workflows/pytest.yml:69-86]()

---

## File Buffer Management

Before making any LSP request against a file, the file must be opened in the language server via `SolidLanguageServer.open_file()`. The `LSPFileBuffer` class:

1. Creates (or reuses) an `LSPFileBuffer` instance, tracked in `open_file_buffers` [src/solidlsp/ls.py:90-118]().
2. Sends a `didOpen` notification to the language server subprocess [src/solidlsp/ls.py:121-139]().
3. Reads file content lazily and invalidates the in-memory cache if the file's modification time changes [src/solidlsp/ls.py:177-186]().
4. Sends a `didClose` notification when the buffer is closed [src/solidlsp/ls.py:159-167]().

Sources: [src/solidlsp/ls.py:90-170]()

---

## Symbol Caching

`SolidLanguageServer` maintains a persistent cache for document symbols. Cache entries are keyed by content hash (`LSPFileBuffer._content_hash`), so edits automatically invalidate the relevant entry [src/solidlsp/ls.py:116-116]().

The caching system uses `load_cache` and `save_cache` utilities to persist symbol data across sessions, verifying version consistency to prevent loading stale data [src/solidlsp/util/cache.py:9-23]().

Sources: [src/solidlsp/ls.py:116-116](), [src/solidlsp/util/cache.py:9-23]()

---

## JetBrains Backend

As an alternative to `solidlsp`, Serena supports a JetBrains backend where code analysis is delegated to a running JetBrains IDE with the Serena plugin installed. The plugin exposes an HTTP API. This backend naturally supports all languages supported by JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.).

Sources: [README.md:115-125](), [docs/01-about/020_programming-languages.md:13-16]()

---

## Relationship to the Rest of Serena

**Diagram: solidlsp in the Serena System**

```mermaid
graph LR
    subgraph "AgentAndTools" ["Agent and Tools"]
        [SerenaAgent] --> [SymbolTools]
        [SymbolTools] -- "ReplaceSymbolBodyTool" --> [EDITOR]
        [SymbolTools] -- "FindSymbolTool" --> [RETRIEVER]
    end

    subgraph "ProjectAndLSManagement" ["Project and LS Management"]
        [PROJECT] ["Project"]
        [LSM] ["LanguageServerManager"]
        [SLS] ["SolidLanguageServer"]
    end

    subgraph "AbstractionsAndSubprocesses" ["Abstractions and Subprocesses"]
        [RETRIEVER] ["LanguageServerSymbolRetriever"]
        [EDITOR] ["LanguageServerCodeEditor"]
        [LSProc] ["LanguageServerProcess"]
    end

    [SerenaAgent] --> [PROJECT]
    [PROJECT] --> [LSM]
    [LSM] --> [SLS]
    [RETRIEVER] --> [SLS]
    [EDITOR] --> [SLS]
    [SLS] --> [LSProc]
```

Sources: [README.md:68-81](), [src/solidlsp/ls.py:88-118](), [test/serena/test_serena_agent.py:15-32]()

The `LanguageServerManager` holds one `SolidLanguageServer` instance per language configured in the project. Symbol tools call into `LanguageServerSymbolRetriever` and `LanguageServerCodeEditor`, which in turn issue LSP requests through the `SolidLanguageServer` API. All of this operates synchronously in a thread dedicated to task execution.

---

