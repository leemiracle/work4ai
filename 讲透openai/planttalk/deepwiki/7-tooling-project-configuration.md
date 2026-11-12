<!-- source: DeepWiki mcp.deepwiki.com · repo openai/planttalk · page 7 Tooling & Project Configuration · fetched 2026-10-26 -->

# Tooling & Project Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [eslint.config.mjs](eslint.config.mjs)
- [package.json](package.json)
- [tsconfig.json](tsconfig.json)
- [vite.config.ts](vite.config.ts)

</details>



This section details the build toolchain, development environment, and static analysis configuration of the Plant Talk project. The project utilizes a modern TypeScript stack, leveraging Vite for the frontend build and a custom Express-based backend, orchestrated via a dual-process development script.

## Development Orchestration

Plant Talk operates as a split-architecture system requiring both a frontend development server and a backend API server to run simultaneously. This is managed through the `concurrently` package [package.json:38-38]().

### Dual-Process Execution
The primary entry point for developers is the `npm run dev` script [package.json:13-13](). This script spawns two distinct processes:

1.  **Web Process (`dev:web`)**: Executes `vite dev` [package.json:14-14](). This serves the React SPA on port 3000 [vite.config.ts:21-21]().
2.  **API Process (`dev:api`)**: Executes `tsx watch server/index.ts` [package.json:15-15](). This uses `tsx` to provide hot-reloading for the TypeScript Express server on port 3001.

### Build and Runtime Scripts
| Script | Command | Purpose |
| :--- | :--- | :--- |
| `setup` | `node scripts/setup.mjs` | Initial environment bootstrapping [package.json:12-12](). |
| `build` | `vite build` | Compiles the frontend into the `dist/` directory [package.json:16-16](). |
| `start` | `tsx server/index.ts` | Production-ready start command for the backend [package.json:17-17](). |
| `lint` | `eslint` | Executes static analysis [package.json:18-18](). |

**Sources:** [package.json:11-19](), [vite.config.ts:19-21]()

## Vite Development Proxy

To avoid Cross-Origin Resource Sharing (CORS) issues and simplify client-side networking, Vite is configured with a reverse proxy. Requests starting with `/api` are forwarded from the frontend (port 3000) to the backend (port 3001).

### Socket Management and Stability
A critical aspect of the proxy configuration is the use of a persistent `http.Agent` [vite.config.ts:10-10]().
*   **Keep-Alive**: The `apiProxyAgent` maintains persistent sockets to prevent the socket churn associated with frequent API calls and long-lived NDJSON streams (like `/api/observe`).
*   **ENOBUFS Prevention**: On certain operating systems (notably Windows), rapid opening/closing of sockets can exhaust the ephemeral port buffer. By setting `keepAlive: true` and targeting `127.0.0.1` instead of `localhost` [vite.config.ts:24-27](), the system avoids dual-stack IPv6/IPv4 connection overhead and buffer exhaustion.

### Process Data Flow Diagram
The following diagram illustrates how the tooling manages the lifecycle and communication between the two development processes.

**Title: Development Process Data Flow**
```mermaid
graph TD
    subgraph "Development Host"
        "NPM_DEV[npm run dev]" --> "CONC[concurrently]"
        
        subgraph "Vite Process (Port 3000)"
            "CONC" --> "VITE_SRV[Vite Dev Server]"
            "VITE_SRV" --> "VITE_PROXY[Vite Proxy Config]"
            "VITE_PROXY" -- "agent: apiProxyAgent" --> "HTTP_KEEP_ALIVE[http.Agent Keep-Alive]"
        end

        subgraph "Express Process (Port 3001)"
            "CONC" --> "TSX_WATCH[tsx watch]"
            "TSX_WATCH" --> "EXP_SRV[Express Server]"
        end
        
        "BROWSER[Web Browser]" -- "GET /" --> "VITE_SRV"
        "BROWSER" -- "POST /api/observe" --> "VITE_PROXY"
        "HTTP_KEEP_ALIVE" -- "Forward to 127.0.0.1:3001" --> "EXP_SRV"
    end
```
**Sources:** [package.json:13-15](), [vite.config.ts:10-31]()

## TypeScript Configuration

The project uses a unified `tsconfig.json` to manage both the frontend React code and the backend Express code.

### Compiler Options
*   **Target/Module**: Set to `ES2022` and `ESNext` to leverage modern JavaScript features [tsconfig.json:5-10]().
*   **Path Aliases**: The configuration defines a path alias `@/*` mapping to `./src/*` [tsconfig.json:20-22](). This allows for clean imports (e.g., `import { ... } from "@/stores/..."`) and is mirrored in the `vite.config.ts` resolution settings [vite.config.ts:15-17]().
*   **Strictness**: `strict: true` is enabled to ensure type safety across the board [tsconfig.json:8-8]().
*   **Module Resolution**: Uses `bundler` resolution to align with Vite's expectations [tsconfig.json:11-11]().

### Scope
The compiler includes files from `src/`, `server/`, and the `vite.config.ts` itself [tsconfig.json:2-2](), while excluding `node_modules` and the `dist` build output [tsconfig.json:3-3]().

**Sources:** [tsconfig.json:1-24](), [vite.config.ts:14-18]()

## Linting and Static Analysis

Plant Talk uses ESLint with the "Flat Config" format (`eslint.config.mjs`) and `typescript-eslint`.

### Configuration Structure
*   **Ignores**: The linter is configured to skip build artifacts (`dist/`), dependencies (`node_modules/`), and utility scripts [eslint.config.mjs:7-7]().
*   **Globals**: Environment globals are defined for both `browser` and `node` to accommodate the full-stack nature of the repository [eslint.config.mjs:14-16]().
*   **Rules**: 
    *   Inherits `js.configs.recommended` [eslint.config.mjs:9-9]().
    *   Inherits `tseslint.configs.recommended` for TypeScript-specific best practices [eslint.config.mjs:10-10]().
    *   **Customization**: Specifically allows empty `catch` blocks [eslint.config.mjs:19-19](), which is useful for silent failures in non-critical sensor polling or hardware connection attempts.

### Entity Mapping: Tooling to Code
This diagram bridges the configuration files to their respective roles in the system.

**Title: Configuration Entity Mapping**
```mermaid
classDiagram
    class "Build Toolchain" {
        +package.json scripts
        +vite.config.ts proxy
    }
    class "Static Analysis" {
        +eslint.config.mjs rules
        +tsconfig.json aliases
    }
    class "Runtime Environment" {
        +.env API Keys
        +.gitignore exclusions
    }

    "Build Toolchain" --|> "VITE_SRV[vite dev]" : Configures
    "Build Toolchain" --|> "EXP_SRV[server/index.ts]" : Launches
    "Static Analysis" --|> "SRC_DIR[src/]" : Validates
    "Static Analysis" --|> "SERVER_DIR[server/]" : Validates
    "Runtime Environment" --|> "NODE_ENV[Node >=20.12]" : Constraints
```
**Sources:** [eslint.config.mjs:1-22](), [package.json:8-10](), [.gitignore:1-25]()

---

