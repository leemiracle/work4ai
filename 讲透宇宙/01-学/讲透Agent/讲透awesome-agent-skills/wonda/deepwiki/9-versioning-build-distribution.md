<!-- source: DeepWiki mcp.deepwiki.com · repo degausai/wonda · page 9 Versioning, Build & Distribution · fetched 2026-10-26 -->

# Versioning, Build & Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mcp/.gitignore](mcp/.gitignore)
- [mcp/package.json](mcp/package.json)
- [mcp/src/tools/annotations.ts](mcp/src/tools/annotations.ts)
- [mcp/src/tools/twin-action-manifest.ts](mcp/src/tools/twin-action-manifest.ts)
- [mcp/src/version-policy.ts](mcp/src/version-policy.ts)
- [mcp/src/version.ts](mcp/src/version.ts)

</details>



This page covers the version management system, build pipeline, and distribution channels for the Wonda MCP server and its relationship with the Wonda CLI binary. Wonda maintains a strict synchronization policy between the MCP server (Node.js) and the CLI (Go) to ensure compatibility across local and remote execution modes.

## Version Management

Wonda uses a dual-versioning system: the `@degausai/wonda-mcp` package version (defined in `package.json`) and the `wonda` CLI binary version. The MCP server is responsible for detecting the local environment, identifying the installation channel, and enforcing update policies to prevent version mismatch errors.

### Version Synchronization Logic
The system uses `captureBinaryVersion` to probe the local environment by executing `wonda --version` [mcp/src/version.ts:73-90](). This version is cached in-process but can be forcefully refreshed via `refreshBinaryVersion` if a user updates their CLI mid-session [mcp/src/version.ts:63-66]().

### Version Flow and Detection
The following diagram illustrates how the MCP server identifies the environment and communicates versioning data to the Wonda Cloud API.

**Version & User-Agent Resolution**
```mermaid
graph TD
    subgraph "Local Environment"
        [PKG_VERSION] -- "Reads" --> A["package.json"]
        [captureBinaryVersion] -- "Executes" --> B["wonda --version"]
        [detectInstallChannel] -- "Inspects" --> C["WONDA_BIN path"]
    end

    subgraph "version.ts"
        B --> D["cachedBinaryVersion"]
        A --> E["PKG_VERSION"]
        D & E --> F["buildUserAgent()"]
    end

    F -- "Headers" --> G["Wonda Cloud API"]
    
    Sources: ["mcp/src/version.ts:37-49", "mcp/src/version.ts:73-90", "mcp/src/version.ts:108-131"]
```

For details on version gating and the `UpdatePolicy` shape, see **[Version Detection & Update Policy](#9.1)**.

## Build Pipeline & Package Structure

The `mcp/` directory is a TypeScript ESM project that produces a distribution ready for both NPM and specialized MCP bundles (MCPB). The build process includes strict validation steps to ensure the `TWIN_ACTION_MANIFEST` remains compatible with the backend API.

### Distribution Channels
Wonda supports multiple installation channels, which are detected by inspecting the file path of the `wonda` binary [mcp/src/version.ts:108-131](). Supported channels include:
*   `brew`: Homebrew Cellar [mcp/src/version.ts:119-121]().
*   `npm`: Global or local node_modules [mcp/src/version.ts:122-122]().
*   `mcpb`: Wonda extension bundle for Claude Desktop [mcp/src/version.ts:118-118]().
*   `windows`: Windows-specific installer [mcp/src/version.ts:129-129]().
*   `curl`: Default shell-script installation [mcp/src/version.ts:130-130]().

### Package Entrypoints
The package exports three primary entrypoints to allow different integration levels:
| Export | Target File | Purpose |
| :--- | :--- | :--- |
| `.` (Main) | `dist/index.js` | Primary CLI entrypoint for `wonda-mcp` binary [mcp/package.json:9-13](). |
| `./api` | `dist/api.js` | The `AsyncLocalStorage` based API client [mcp/package.json:14-17](). |
| `./server` | `dist/server.js` | The MCP server factory and transport logic [mcp/package.json:18-21](). |

### Build & Validation Lifecycle
The build pipeline is managed via `npm scripts` and includes automated compatibility checks.

**Build and Validation Pipeline**
```mermaid
graph LR
    [tsc] --> A["dist/"]
    A --> B["check:annotations"]
    A --> C["check-api-compat"]
    A --> D["check-twin-actions"]
    
    B -- "Validates" --> E["ToolAnnotations"]
    C -- "Validates" --> F["API Endpoints"]
    D -- "Validates" --> G["TWIN_ACTION_MANIFEST"]
    
    subgraph "Scripts"
        B["scripts/check-tool-annotations.mjs"]
        C["scripts/check-api-compat.mjs"]
        D["scripts/check-twin-actions.mjs"]
    end

    Sources: ["mcp/package.json:26-34", "mcp/src/tools/annotations.ts:5-14", "mcp/src/tools/twin-action-manifest.ts:13-20"]
```

For details on the ESM build configuration and validation scripts, see **[Build Pipeline & Package Structure](#9.2)**.

## Update Policy Mechanism

To maintain stability, the MCP server periodically fetches an `UpdatePolicy` from the Wonda API via `GET /cli/version` [mcp/src/version-policy.ts:34-37](). This policy is cached for 30 minutes [mcp/src/version-policy.ts:4-8]().

The policy dictates:
1.  **`minSupported`**: The minimum CLI version required to operate [mcp/src/version.ts:23-23]().
2.  **`latest`**: The current stable version for update notifications [mcp/src/version.ts:22-22]().
3.  **`updateCommands`**: A mapping of `InstallChannel` to specific shell commands (e.g., `brew upgrade wonda`) [mcp/src/version.ts:25-25]().

Sources:
*   `mcp/package.json`: [1-62]()
*   `mcp/src/version.ts`: [10-156]()
*   `mcp/src/version-policy.ts`: [4-57]()
*   `mcp/src/tools/twin-action-manifest.ts`: [1-20]()
*   `mcp/src/tools/annotations.ts`: [1-21]()

---

