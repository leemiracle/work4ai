<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-typescript · page 7 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)

</details>



This page provides an overview of the reference documentation for the Claude Agent SDK TypeScript. It outlines the scope of the configuration options, core API endpoints, and version history, linking directly to the exhaustive child pages for detailed technical specs.

For conceptual explanations, see [Core Concepts](#3). For practical usage examples, see [Examples and Tutorials](#6).

## Reference Page Navigation

The reference documentation is organized into three child pages, covering configuration, API interfaces, and release histories.

```mermaid
graph TB
    subgraph "Reference Parent Page"
        Ref["Reference Root"]
    end
    
    subgraph "Child Pages"
        ConfigRef["7.1 Configuration Options Reference"]
        ApiRef["7.2 API Reference"]
        Changelog["7.3 Version History and Changelog"]
    end
    
    Ref --> ConfigRef
    Ref --> ApiRef
    Ref --> Changelog
```

**Sources:** [CHANGELOG.md:1-5]()

---

## 1. Configuration Options Reference

The configuration system provides hierarchical control over SDK behavior, environment isolation, agent definitions, and security policies. Options can be passed programmatically to `query()` or managed via setting sources [CHANGELOG.md:11-12](). Key subsystems include `systemPrompt`, `settingSources`, tool registries, subagents, and environment definitions [CHANGELOG.md:57-61]().

For exhaustive details on all parameters, defaults, and type definitions, see [Configuration Options Reference](#7.1).

```mermaid
graph TB
    subgraph "Configuration Space"
        Opts["Options Interface"]
        SysOpts["systemPrompt & settingSources"]
        ToolOpts["tools & disallowedTools"]
        AgentOpts["agents & skills"]
        EnvOpts["env & sandbox Options"]
    end
    
    Opts --> SysOpts
    Opts --> ToolOpts
    Opts --> AgentOpts
    Opts --> EnvOpts
```

**Sources:** [CHANGELOG.md:11-12](), [CHANGELOG.md:57-61]()

---

## 2. API Reference

The SDK exposes core execution primitives, session management functions, MCP management utilities, and hook definitions. The primary entry point is the `query()` function, which interfaces with the native Claude Code binary over a JSON-RPC control protocol [CHANGELOG.md:123-125](). Auxiliary functions include `startup()`, `resolveSettings()`, and `SessionStore` integration adapters.

For complete method signatures, type definitions, and interface contracts, see [API Reference](#7.2).

```mermaid
graph TB
    subgraph "API Code Entities"
        QueryFn["query()"]
        StartupFn["startup() / WarmQuery"]
        SessionInterface["Session Interface"]
        SessionStoreInterface["SessionStore Interface"]
        MCPUtils["mcpServerStatus()"]
    end
    
    subgraph "Protocol Layer"
        JSONRPC["JSON-RPC Control Protocol"]
        Binary["Native Claude Code Binary"]
    end
    
    QueryFn --> JSONRPC
    StartupFn --> JSONRPC
    JSONRPC --> Binary
    SessionInterface -.-> QueryFn
```

**Sources:** [CHANGELOG.md:123-125](), [CHANGELOG.md:131-135]()

---

## 3. Version History and Changelog

The SDK maintains strict version parity with the Claude Code CLI. Release versions track breaking changes, feature additions (such as `fast_mode_disabled_reason` or usage reporting), bug fixes, and deprecations across the `0.2.x` and `0.3.x` release series [CHANGELOG.md:3-15]().

For a full chronological log of changes, breaking updates, and version migrations, see [Version History and Changelog](#7.3).

```mermaid
graph TB
    subgraph "Version Control Space"
        V02["SDK 0.2.x Series"]
        V03["SDK 0.3.x Series"]
        Parity["Claude Code CLI Parity"]
    end
    
    V02 --> V03
    V03 --> Parity
```

**Sources:** [CHANGELOG.md:3-15]()

---

