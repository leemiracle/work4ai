<!-- source: DeepWiki mcp.deepwiki.com · repo e2b-dev/E2B · page 2 JavaScript SDK · fetched 2026-10-29 -->

# JavaScript SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/js-sdk/src/api/http2.ts](packages/js-sdk/src/api/http2.ts)
- [packages/js-sdk/src/envd/http2.ts](packages/js-sdk/src/envd/http2.ts)
- [packages/js-sdk/src/sandbox/index.ts](packages/js-sdk/src/sandbox/index.ts)
- [packages/js-sdk/src/undici.ts](packages/js-sdk/src/undici.ts)
- [packages/js-sdk/src/utils.ts](packages/js-sdk/src/utils.ts)
- [packages/js-sdk/tests/api/http2.test.ts](packages/js-sdk/tests/api/http2.test.ts)
- [packages/js-sdk/tests/envd/http2.test.ts](packages/js-sdk/tests/envd/http2.test.ts)
- [packages/js-sdk/tests/undici.test.ts](packages/js-sdk/tests/undici.test.ts)
- [packages/js-sdk/tests/utils.test.ts](packages/js-sdk/tests/utils.test.ts)
- [packages/js-sdk/vitest.config.mts](packages/js-sdk/vitest.config.mts)
- [packages/python-sdk/e2b/sandbox/main.py](packages/python-sdk/e2b/sandbox/main.py)

</details>



The JavaScript SDK (`e2b`) provides a TypeScript and JavaScript client library for creating and managing isolated cloud sandboxes, executing shell commands, operating on remote filesystems, and integrating with AI workflows. This parent page provides a high-level overview of the SDK's resource classes, module exports, multi-runtime support, and architecture. For deep technical details, refer to the child sections linked below.

Sources: [packages/js-sdk/src/sandbox/index.ts:38-78]()

## Module Exports and Resource Classes

The core entry point for the SDK is the `Sandbox` class, which extends `SandboxApi` [packages/js-sdk/src/sandbox/index.ts:75-76](). It aggregates specialized resource modules such as `Filesystem`, `Commands`, `Pty`, and `Git` [packages/js-sdk/src/sandbox/index.ts:83-97](). Communication with sandboxes leverages a dual-protocol architecture: REST APIs handle lifecycle management via `EnvdApiClient` [packages/js-sdk/src/sandbox/index.ts:10-121](), while ConnectRPC/HTTP2 transports manage runtime streams and RPCs via `createConnectTransport` [packages/js-sdk/src/sandbox/index.ts:1-169]().

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Primary Sandbox Class"] -->|Exposes| B["Filesystem Operations"]
        A -->|Exposes| C["Command Execution"]
        A -->|Exposes| D["Pseudo-Terminal"]
    end

    subgraph "Code Entity Space"
        E["packages/js-sdk/src/sandbox/index.ts:Sandbox"] -->|Has property files| F["packages/js-sdk/src/sandbox/filesystem.ts:Filesystem"]
        E -->|Has property commands| G["packages/js-sdk/src/sandbox/commands/index.ts:Commands"]
        E -->|Has property pty| H["packages/js-sdk/src/sandbox/commands/pty.ts:Pty"]
    end

    A -.-> E
    B -.-> F
    C -.-> G
    D -.-> H
```
Sources: [packages/js-sdk/src/sandbox/index.ts:75-97]()

## Runtime Support

The SDK is designed to run across multiple JavaScript runtimes including Node.js, Bun, Deno, Cloudflare Workers (`workerd`), Vercel Edge, and browsers. The runtime detection utility identifies the active execution environment and configures appropriate transport layers, HTTP/2 dispatchers (such as `undici` in Node.js environments), and WebCrypto APIs [packages/js-sdk/src/utils.ts:16-61]().

```mermaid
graph TD
    subgraph "Natural Language Space"
        RT["Runtime Detection"] -->|Identifies| R1["Node.js / Bun / Deno"]
        RT -->|Identifies| R2["Cloudflare Workers / Browser"]
    end

    subgraph "Code Entity Space"
        RC["packages/js-sdk/src/utils.ts:getRuntime"] -->|Returns runtime string| RCV["packages/js-sdk/src/utils.ts:runtime"]
        RCV -->|Configures fetcher| UHTTP["packages/js-sdk/src/envd/http2.ts:createEnvdFetchForRuntime"]
    end

    RT -.-> RC
    R1 -.-> UHTTP
    R2 -.-> UHTTP
```
Sources: [packages/js-sdk/src/utils.ts:16-52](), [packages/js-sdk/src/envd/http2.ts:25-37]()

## Child Pages Overview

- **Sandbox Management**: See [Sandbox Management](#2.1) for details on the `Sandbox` class and `SandboxApi` lifecycle methods (create, connect, fork, pause/resume, kill, snapshots, timeouts, network options, and MCP integration).
- **Filesystem Operations**: See [Filesystem Operations](#2.2) for details on the `Filesystem` module covering file reading/writing, streams, blobs, multipart uploads, gzip compression, and watch handles.
- **Command Execution and PTY**: See [Command Execution and PTY](#2.3) for details on running shell commands, `CommandHandle`, streaming stdout/stderr, stdin piping, and `Pty` terminal management.
- **Error Handling and Types**: See [Error Handling and Types](#2.4) for the error hierarchy (`SandboxError`, `TimeoutError`, `AuthenticationError`, `RateLimitError`, `ServiceBusyError`) and exception mapping.
- **Connection Configuration and the E2B Client**: See [Connection Configuration and the E2B Client](#2.5) for `ConnectionConfig`, `ClientFactory`, API parameters precedence, timeouts, proxies, and retry mechanisms.
- **Git Integration**: See [Git Integration](#2.6) for repository operations inside sandboxes using the `Git` module.

Sources: [packages/js-sdk/src/sandbox/index.ts:75-98]()

---

