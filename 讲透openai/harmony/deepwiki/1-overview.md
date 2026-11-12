<!-- source: DeepWiki mcp.deepwiki.com · repo openai/harmony · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [run_checks.sh](run_checks.sh)

</details>



This document provides a comprehensive overview of the `openai-harmony` repository, a multi-platform library implementing OpenAI's harmony response format for the gpt-oss model series. The harmony format defines conversation structures, reasoning output channels, and function calling mechanisms specifically designed for open-weight models [README.md:1-13]().

For detailed information about the library's internal Rust structure, see [Core Library Architecture](#1.1). For information on how the Rust core is exposed to other environments, see [Language Bindings](#1.2).

## System Purpose and Architecture

The `openai-harmony` library serves as the canonical implementation for parsing and rendering conversations in the harmony format [README.md:48-53](). The system is architected as a high-performance Rust core with language bindings for Python and WebAssembly environments [README.md:132-141]().

### Core System Architecture

```mermaid
graph TB
    subgraph "Rust Core Library [src/]"
        chat["chat.rs<br/>'Role', 'Message', 'Conversation'"]
        encoding["encoding.rs<br/>'HarmonyEncoding', render/parse logic"]
        registry["registry.rs<br/>'HarmonyEncodingName' variants"]
    end
    
    subgraph "Language Bindings"
        py_module["py_module.rs<br/>'pyo3' FFI bindings"]
        wasm_bindings["'wasm-bindgen'<br/>JS/TS interface"]
    end
    
    subgraph "Platform Targets"
        rlib["rlib<br/>Rust applications"]
        cdylib["cdylib<br/>C FFI / Shared Lib"]
        python_ext["Python Extension<br/>'openai_harmony.*.so'"]
        wasm["WebAssembly<br/>'harmony-demo' integration"]
    end
    
    subgraph "External Dependencies [Cargo.toml]"
        reqwest["'reqwest'<br/>HTTP client"]
        serde["'serde'<br/>serialization"]
        tiktoken["'tiktoken' integration<br/>tokenization"]
    end
    
    chat --> encoding
    encoding --> registry
    
    encoding --> py_module
    encoding --> wasm_bindings
    
    py_module --> python_ext
    wasm_bindings --> wasm
    
    chat --> rlib
    encoding --> cdylib
    
    encoding --> reqwest
    encoding --> serde
    encoding --> tiktoken
```

**Sources:** [Cargo.toml:9-16](), [README.md:144-159](), [AGENTS.md:1-5]()

### Multi-Platform Compilation Strategy

The library uses Cargo's `crate-type` configuration and feature flags to generate multiple compilation targets from a single Rust codebase [Cargo.toml:9-16]().

*   **Rust Native**: Compiled as an `rlib` for use in other Rust projects [Cargo.toml:11]().
*   **Python**: Uses the `python-binding` feature and `pyo3` to create a native extension [Cargo.toml:15](), [Cargo.toml:45-48]().
*   **WebAssembly**: Uses the `wasm-binding` feature and `wasm-bindgen` for browser-based environments like the harmony-demo [Cargo.toml:16](), [Cargo.toml:49-53]().

**Sources:** [Cargo.toml:9-16](), [Cargo.toml:45-53]()

## Core Data Structures and Message Flow

The harmony format centers around structured conversations with specific role-based message types and multi-channel assistant responses.

### Message Type Hierarchy

The core data structures are defined in `src/chat.rs` and mirrored in the Python wrapper `python/openai_harmony/__init__.py` [README.md:144-159]().

```mermaid
graph TB
    subgraph "Core Types [src/chat.rs]"
        Role["'Role' enum<br/>System, Developer, User, Assistant, Tool"]
        Message["'Message' struct<br/>role, content, metadata"]
        Conversation["'Conversation' struct<br/>Vec&lt;Message&gt;"]
    end
    
    subgraph "Content Types"
        SystemContent["'SystemContent'<br/>system instructions"]
        DeveloperContent["'DeveloperContent'<br/>tools, instructions"]
        AssistantContent["'AssistantContent'<br/>multi-channel output"]
    end
    
    subgraph "Assistant Channels [README.md]"
        final_channel["'final'<br/>user-facing output"]
        analysis_channel["'analysis'<br/>chain-of-thought"]
        commentary_channel["'commentary'<br/>tool calls, preambles"]
    end
    
    Role --> Message
    Message --> Conversation
    
    Message --> SystemContent
    Message --> DeveloperContent
    Message --> AssistantContent
    
    AssistantContent --> final_channel
    AssistantContent --> analysis_channel
    AssistantContent --> commentary_channel
```

**Sources:** [README.md:72-93](), [README.md:116-126](), [README.md:148-155]()

### Encoding and Parsing Pipeline

The `HarmonyEncoding` handles the conversion between structured objects and token sequences [README.md:48-53]().

```mermaid
flowchart LR
    subgraph "Input Processing"
        input_convo["'Conversation'<br/>Vec&lt;Message&gt;"]
        target_role["target 'Role'<br/>Assistant"]
    end
    
    subgraph "Encoding Pipeline [src/encoding.rs]"
        harmony_enc["'load_harmony_encoding'<br/>HarmonyEncoding"]
        render_method["'render_conversation_for_completion'<br/>tokens: Vec&lt;u32&gt;"]
    end
    
    subgraph "Output Processing"
        parse_method["'parse_messages_from_completion_tokens'<br/>role: Role"]
        parsed_messages["parsed 'Messages'<br/>structured output"]
    end
    
    input_convo --> harmony_enc
    target_role --> harmony_enc
    harmony_enc --> render_method
    render_method --> parse_method
    parse_method --> parsed_messages
```

**Sources:** [README.md:72-99](), [README.md:116-128](), [README.md:149]()

## Dependency Ecosystem and Integration Points

The library integrates with a specific set of dependencies to provide comprehensive functionality while maintaining cross-platform compatibility.

| Dependency | Purpose | Configuration |
|------------|---------|---------------|
| `pyo3` | Python FFI bindings | Optional feature `python-binding` [Cargo.toml:15, 45]() |
| `wasm-bindgen` | WebAssembly FFI bindings | Optional feature `wasm-binding` [Cargo.toml:16, 49]() |
| `reqwest` | HTTP client for tool/image fetching | Uses `rustls-tls` for cross-platform CI [Cargo.toml:32-42]() |
| `serde` | Serialization/Deserialization | Derived for most chat structures [Cargo.toml:22]() |
| `tiktoken` | Tokenization engine | Integrated via `encoding.rs` [README.md:139, 149]() |

**Sources:** [Cargo.toml:13-53](), [README.md:132-141]()

## Build System Integration

The project uses `maturin` for Python packaging and `cargo` for the native Rust core.

```mermaid
graph TB
    subgraph "Development Tools"
        maturin["'maturin'<br/>PyO3 build tool"]
        cargo["'cargo'<br/>Rust build system"]
    end
    
    subgraph "Build Commands [README.md]"
        develop_cmd["'maturin develop --release'<br/>local development"]
        test_cmd["'cargo test' / 'pytest'<br/>test suites"]
    end
    
    subgraph "Output Artifacts"
        so_file["'openai_harmony.*.so'<br/>Python extension"]
        rlib_file["'libopenai_harmony.rlib'<br/>Rust library"]
    end
    
    maturin --> develop_cmd
    cargo --> test_cmd
    
    develop_cmd --> so_file
    cargo --> rlib_file
```

**Sources:** [README.md:163-207](), [AGENTS.md:7-9](), [run_checks.sh:5-7]()

For more details on the architecture, see [Core Library Architecture](#1.1). For more on language-specific implementations, see [Language Bindings](#1.2).

---

