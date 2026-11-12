<!-- source: DeepWiki mcp.deepwiki.com · repo elizaOS/eliza · page 9 Multi-Language Support · fetched 2026-10-29 -->

# Multi-Language Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [.github/workflows/sandbox-live-smoke.yml](.github/workflows/sandbox-live-smoke.yml)
- [knip.json](knip.json)
- [packages/agent/docs/e2b-capability-routing.md](packages/agent/docs/e2b-capability-routing.md)
- [packages/agent/scripts/live-sandbox-smoke.ts](packages/agent/scripts/live-sandbox-smoke.ts)
- [packages/agent/scripts/mobile-stubs/e2b-capability-router.cjs](packages/agent/scripts/mobile-stubs/e2b-capability-router.cjs)
- [packages/agent/src/runtime/eliza.ts](packages/agent/src/runtime/eliza.ts)
- [packages/agent/src/services/e2b-capability-router.test.ts](packages/agent/src/services/e2b-capability-router.test.ts)
- [packages/agent/src/services/e2b-capability-router.ts](packages/agent/src/services/e2b-capability-router.ts)
- [packages/app-core/platforms/electrobun/tsconfig.json](packages/app-core/platforms/electrobun/tsconfig.json)
- [packages/app-core/platforms/electrobun/vitest.electrobun.config.ts](packages/app-core/platforms/electrobun/vitest.electrobun.config.ts)
- [packages/core/src/connectors/oauth-role.test.ts](packages/core/src/connectors/oauth-role.test.ts)
- [packages/core/src/connectors/oauth-role.ts](packages/core/src/connectors/oauth-role.ts)
- [packages/core/src/index.browser.ts](packages/core/src/index.browser.ts)
- [packages/core/src/index.edge.ts](packages/core/src/index.edge.ts)
- [packages/core/src/index.node.ts](packages/core/src/index.node.ts)
- [packages/core/src/services/runtime-capability-service.ts](packages/core/src/services/runtime-capability-service.ts)
- [packages/plugin-remote-manifest/examples/carrot-clock/plugin.json](packages/plugin-remote-manifest/examples/carrot-clock/plugin.json)
- [packages/plugin-remote-manifest/examples/hello-carrot/plugin.json](packages/plugin-remote-manifest/examples/hello-carrot/plugin.json)
- [packages/ui/src/components/settings/CloudInstancePanel.tsx](packages/ui/src/components/settings/CloudInstancePanel.tsx)
- [packages/ui/src/onboarding/onboarding-config.ts](packages/ui/src/onboarding/onboarding-config.ts)
- [plugins/plugin-calendly/src/connector-account-provider.ts](plugins/plugin-calendly/src/connector-account-provider.ts)
- [plugins/plugin-elizacloud/src/index.browser.ts](plugins/plugin-elizacloud/src/index.browser.ts)
- [plugins/plugin-linear/src/connector-account-provider.ts](plugins/plugin-linear/src/connector-account-provider.ts)
- [plugins/plugin-shopify/src/connector-account-provider.ts](plugins/plugin-shopify/src/connector-account-provider.ts)

</details>



ElizaOS is designed as a polyglot AI agent framework supporting TypeScript, Python, and Rust implementations. This multi-language architecture enables developers to build agents and plugins in their preferred language while maintaining type safety and interoperability across the entire ecosystem through a shared schema-first approach.

---

## Architecture Overview

ElizaOS achieves multi-language support through a layered architecture with Protocol Buffers at its foundation, providing a single source of truth for all type definitions and enabling seamless interoperability.

### Polyglot Ecosystem Flow
```mermaid
graph TB
    subgraph "Source_of_Truth"
        [SchemaPkg] -- ".proto files" --> [ProtoSchemas]
        [PromptPkg] -- ".txt/.handlebars" --> [PromptSources]
    end
    
    subgraph "Code_Generation"
        [BufGenerate]
        [PromptGen]
    end
    
    subgraph "Language_Runtimes"
        subgraph "TypeScript_@elizaos/core"
            [TSTypes]
            [TSPrompts]
            [AgentRuntimeTS]
        end
        
        subgraph "Rust_@elizaos/rust"
            [RsTypes]
            [RsPrompts]
            [AgentRuntimeRs]
        end
        
        subgraph "Python_@elizaos/python"
            [PyTypes]
            [PyPrompts]
            [AgentRuntimePy]
        end
    end
    
    subgraph "Interoperability"
        [InteropPkg]
        [ProtobufSerde]
    end
    
    [ProtoSchemas] --> [BufGenerate]
    [PromptSources] --> [PromptGen]
    
    [BufGenerate] --> [TSTypes]
    [BufGenerate] --> [RsTypes]
    [BufGenerate] --> [PyTypes]
    
    [PromptGen] --> [TSPrompts]
    [PromptGen] --> [RsPrompts]
    [PromptGen] --> [PyPrompts]
    
    [AgentRuntimeTS] --> [InteropPkg]
    [AgentRuntimeRs] --> [InteropPkg]
    [AgentRuntimePy] --> [InteropPkg]
    [InteropPkg] --> [ProtobufSerde]
```

**Sources:** [packages/core/src/index.node.ts:133-135](), [packages/core/src/index.browser.ts:45-45](), [packages/core/src/prompts.ts:1-20]()

---

## Protocol Buffers Schema System

Protocol Buffers provide a single source of truth that defines all core data structures used in ElizaOS, ensuring consistency and multi-language type generation.

### Schema to Runtime Mapping

```mermaid
graph LR
    subgraph "Schema_Definitions"
        ["agent.proto"]
        ["memory.proto"]
        ["messaging.proto"]
    end

    subgraph "TypeScript_Entities"
        ["AgentRuntime"]
        ["Memory"]
        ["Message"]
    end

    subgraph "Python_Entities"
        ["runtime.py"]
        ["plugin.py"]
    end

    subgraph "Rust_Entities"
        ["runtime.rs"]
        ["sync_runtime.rs"]
    end

    ["agent.proto"] -- "buf generate" --> ["AgentRuntime"]
    ["agent.proto"] -- "buf generate" --> ["runtime.py"]
    ["agent.proto"] -- "buf generate" --> ["runtime.rs"]
    ["memory.proto"] -- "buf generate" --> ["Memory"]
    ["messaging.proto"] -- "buf generate" --> ["Message"]
```

### Code Generation Pipeline Summary

The system uses `buf` to maintain parity across languages. 
- **TypeScript**: Generates types and helpers into `packages/core/src/generated/` [packages/core/src/index.node.ts:133-135]().
- **Python**: Generates types into `packages/python/elizaos/generated/`.
- **Rust**: Generates types into `packages/rust/src/generated/`.
- **Prompts**: The `@elizaos/prompts` package extends this by generating multi-language prompt templates from source files, which are then consumed by the language-specific runtimes [packages/core/src/prompts.ts:18-20]().

**Sources:** [packages/core/src/index.node.ts:133-135](), [packages/core/src/prompts.ts:1-20]()

---

## TypeScript Runtime

TypeScript is the primary runtime for ElizaOS, providing the full implementation of the framework including the core `AgentRuntime`.

- **Package**: Managed under `@elizaos/core` (packages/core).
- **Environment Support**: Includes specific entry points for Node.js (`index.node.ts`), Browser (`index.browser.ts`), and Edge (`index.edge.ts`) environments [packages/core/src/index.node.ts:1-7](), [packages/core/src/index.browser.ts:1-7](), [packages/core/src/index.edge.ts:1-9]().
- **Capabilities**: Implements modular features such as `basicCapabilities` and the `RuntimeCapabilityService` which manages unified capability routing for `fs`, `pty`, `git`, and `model` [packages/core/src/services/runtime-capability-service.ts:108-118]().
- **Search & Context**: Provides `BM25` search and `StreamingContext` for optimized RAG and inference [packages/core/src/index.browser.ts:61-73]().

For details, see [TypeScript Runtime](#9.1).

**Sources:** [packages/core/src/index.node.ts:1-7](), [packages/core/src/index.browser.ts:1-7](), [packages/core/src/services/runtime-capability-service.ts:108-118]()

---

## Rust Runtime and WASM

The `@elizaos/rust` package implements the ElizaOS runtime and types in Rust with support for native binaries and WebAssembly targets.

- **Native Builds**: High-performance execution for server-side and desktop agents.
- **WASM**: Compiled targets allow Rust logic to run in JavaScript environments (Web and Node.js), enabling shared logic between the core TS runtime and high-performance Rust modules.
- **Sync/Async**: Supports both `runtime.rs` and `sync_runtime.rs` patterns for different threading requirements.
- **Native Plugins**: NAPI-RS is used to build high-performance native modules that are loaded by the TypeScript runtime.

For details, see [Rust Runtime and WASM](#9.2).

---

## Python Integration

The Python implementation provides a complete runtime and service layer, allowing for deep integration with the Python AI ecosystem (PyTorch, HuggingFace, etc.).

- **Core Package**: `elizaos` (packages/python/elizaos).
- **Inference & Benchmarking**: Python is used extensively for training and benchmarking. The robotics stack also utilizes Python for perception pipelines and reinforcement learning [packages/agent/src/runtime/eliza.ts:191-191]().
- **Training Pipeline**: Scripts for model release, evaluation gates, and fine-tuning backends are implemented in Python.

For details, see [Python Integration](#9.3).

**Sources:** [packages/agent/src/runtime/eliza.ts:191-191]()

---

## Cross-Language Interoperability

The `@elizaos/interop` package enables seamless cross-runtime plugin development using Protocol Buffer serialization as the bridge.

- **Interop Matrix**: Supports TS↔Rust via WASM/FFI and TS↔Python via IPC.
- **Capability Routing**: The `E2BRemoteCapabilityRouterService` allows the TypeScript runtime to dispatch commands to remote coding containers or sandboxes [packages/agent/src/services/e2b-capability-router.ts:56-81]().
- **Plugin Portability**: Allows a plugin written in one language to be registered and used by an `AgentRuntime` in another through standardized interfaces like `IAgentRuntime` [packages/core/src/types/runtime.ts:1-50]().

For details, see [Cross-Language Interoperability](#9.4).

**Sources:** [packages/agent/src/services/e2b-capability-router.ts:56-81]()

---

## ComputerUse and Native Bindings

Native system integration is handled through specialized plugins that bridge the agent to the operating system, often utilizing NAPI-RS or Capacitor for platform-specific access.

- **Native Plugins**: Modules like `plugin-computeruse` provide the agent with capabilities to interact with the host OS (screenshots, input control).
- **Platform Bridges**: The `mobile-device-bridge-hooks.ts` and `plugin-capacitor-bridge` facilitate interaction between the core runtime and native mobile/desktop APIs [packages/core/src/index.node.ts:143-143]().
- **Connector Accounts**: Supports OAuth and role management for external services like Linear, integrated via the `ConnectorAccountManager` [plugins/plugin-linear/src/connector-account-provider.ts:175-181]().

For details, see [ComputerUse and Native Bindings](#9.5).

**Sources:** [packages/core/src/index.node.ts:143-143](), [plugins/plugin-linear/src/connector-account-provider.ts:175-181]()

---

## Links to Child Pages

- [TypeScript Runtime](#9.1) — Document `@elizaos/core`, environment-specific exports, and TS-specific optimizations.
- [Rust Runtime and WASM](#9.2) — Explain `@elizaos/rust`, native builds, and WASM compilation.
- [Python Integration](#9.3) — Document `@elizaos/python` runtime, types, and Python-specific workflows.
- [Cross-Language Interoperability](#9.4) — Explain `@elizaos/interop`, Protobuf serialization, and the interop matrix.
- [ComputerUse and Native Bindings](#9.5) — Document `@elizaos/plugin-computeruse` and NAPI-RS native system integration.

---

