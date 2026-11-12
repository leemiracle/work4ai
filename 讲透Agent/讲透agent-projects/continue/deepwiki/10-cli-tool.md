<!-- source: DeepWiki mcp.deepwiki.com · repo continuedev/continue · page 10 CLI Tool · fetched 2026-10-29 -->

# CLI Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [binary/README.md](binary/README.md)
- [extensions/cli/BUILD.md](extensions/cli/BUILD.md)
- [extensions/cli/build.mjs](extensions/cli/build.mjs)
- [extensions/cli/package-lock.json](extensions/cli/package-lock.json)
- [extensions/cli/package.json](extensions/cli/package.json)
- [extensions/cli/smoke-test.mjs](extensions/cli/smoke-test.mjs)
- [extensions/cli/src/commands/checks.ts](extensions/cli/src/commands/checks.ts)
- [extensions/cli/src/index.ts](extensions/cli/src/index.ts)
- [extensions/cli/src/services/FileIndexService.test.ts](extensions/cli/src/services/FileIndexService.test.ts)
- [extensions/cli/src/services/FileIndexService.ts](extensions/cli/src/services/FileIndexService.ts)
- [extensions/cli/src/ui/AppRoot.tsx](extensions/cli/src/ui/AppRoot.tsx)
- [extensions/cli/src/ui/FileSearchUI.tsx](extensions/cli/src/ui/FileSearchUI.tsx)
- [extensions/cli/src/ui/__tests__/UserInput.missingFile.test.tsx](extensions/cli/src/ui/__tests__/UserInput.missingFile.test.tsx)
- [extensions/cli/src/ui/index.ts](extensions/cli/src/ui/index.ts)
- [extensions/cli/src/util/errorState.ts](extensions/cli/src/util/errorState.ts)
- [extensions/cli/src/util/exit.ts](extensions/cli/src/util/exit.ts)
- [extensions/cli/src/util/metadata.test.ts](extensions/cli/src/util/metadata.test.ts)
- [extensions/cli/src/util/metadata.ts](extensions/cli/src/util/metadata.ts)
- [extensions/cli/stubs/react-devtools-core.js](extensions/cli/stubs/react-devtools-core.js)
- [extensions/cli/validate-aliases.mjs](extensions/cli/validate-aliases.mjs)

</details>



The Continue CLI is a terminal-based AI assistant distributed as the `@continuedev/cli` npm package (aliased as `cn`) [extensions/cli/package.json:8-10](). It provides a robust Terminal User Interface (TUI) for interactive chat, a `serve` mode for sub-agent execution, and a tool system that bridges natural language prompts with local terminal and file operations.

For deep technical details, see the child pages:
- [CLI Architecture and Commands](#10.1) — Entry points, command structure, and service initialization.
- [TUI Chat Interface](#10.2) — Ink-based terminal rendering and user input handling.
- [CLI Tool System and Sub-agents](#10.3) — Built-in tools, sub-agent execution, and Git integration.

## System Overview

The CLI is built as a React-based terminal application using `ink` [extensions/cli/src/ui/index.ts:105-117](). It initializes a suite of services managed by a `ServiceContainer` that mirror the functionality found in Continue's IDE extensions, including configuration loading, LLM provider management, and context providers [extensions/cli/src/ui/index.ts:66-72]().

### Bridge: Natural Language to Code Entities
The following diagram illustrates how user commands in the terminal are routed through the CLI's command system to the underlying code services.

```mermaid
graph TD
    "UserTerminal"["User Terminal"] -- "cn chat 'fix bug'" --> "CLIEntry"["CLI Entry (extensions/cli/src/index.ts)"]
    "CLIEntry" -- "Invoke" --> "ChatAction"["program.action() (extensions/cli/src/index.ts)"]
    "ChatAction" -- "Initialize" --> "initializeServices"["initializeServices() (extensions/cli/src/services/index.ts)"]
    
    subgraph "Code Entity Space"
        "initializeServices" --> "FileIndexService"["FileIndexService (extensions/cli/src/services/FileIndexService.ts)"]
        "initializeServices" --> "BackgroundJobService"["BackgroundJobService"]
        "initializeServices" --> "TelemetryService"["telemetryService"]
    end

    "ChatAction" -- "Render" --> "startTUIChat"["startTUIChat() (extensions/cli/src/ui/index.ts)"]
    "startTUIChat" -- "React Render" --> "AppRoot"["AppRoot Component (extensions/cli/src/ui/AppRoot.tsx)"]
```
**Sources:** [extensions/cli/src/index.ts:171-200](), [extensions/cli/src/ui/index.ts:32-126](), [extensions/cli/src/services/FileIndexService.ts:23-26]()

## Command Structure

The CLI uses the `commander` library to define its interface. While interactive chat is the default, it supports several specialized modes [extensions/cli/src/index.ts:171-180]():

| Command | Purpose | Key File |
| :--- | :--- | :--- |
| `chat` (Default) | Default interactive TUI session with history and slash commands. | [extensions/cli/src/commands/chat.ts]() |
| `serve` | Headless mode for remote sub-agents, exposing an HTTP control API. | [extensions/cli/src/commands/serve.ts]() |
| `review` | Automated code review of git changes using `getGitDiffSnapshot`. | [extensions/cli/src/commands/review.ts]() |
| `checks` | List and manage check statuses for GitHub Pull Requests. | [extensions/cli/src/commands/checks.ts]() |
| `ls` | List previous chat sessions. | [extensions/cli/src/commands/ls.ts]() |

**Sources:** [extensions/cli/src/index.ts:8-24](), [extensions/cli/src/commands/checks.ts:146-150](), [extensions/cli/src/util/exit.ts:35-40]()

## Terminal User Interface (TUI)

The TUI provides a rich interactive experience within the terminal. It uses `ink` to render React components into ANSI escape codes [extensions/cli/src/ui/index.ts:105-117](). Key features include:
- **Two-Stage Exit:** A custom `SIGINT` handler that requires double `Ctrl+C` within 1 second to exit, preventing accidental data loss [extensions/cli/src/index.ts:59-91]().
- **File Indexing:** The `FileIndexService` uses `fdir` and `fzf` to provide fast, fuzzy file searching within the TUI [extensions/cli/src/services/FileIndexService.ts:207-212]().
- **Graceful Shutdown:** The `gracefulExit` function ensures telemetry is flushed and background jobs are killed before the process terminates [extensions/cli/src/util/exit.ts:193-220]().

For details, see [TUI Chat Interface](#10.2).

**Sources:** [extensions/cli/src/index.ts:59-91](), [extensions/cli/src/services/FileIndexService.ts:140-161](), [extensions/cli/src/util/exit.ts:193-220]()

## Tool System and Sub-agents

The CLI features a sophisticated tool-calling system that allows the LLM to interact with the local environment, particularly in `serve` mode for autonomous agents.

### Tool Execution Flow
This diagram shows how a "Natural Language Space" request to analyze code is transformed into "Code Entity Space" operations like diff calculation.

```mermaid
graph LR
    subgraph "Natural Language Space"
        "Req"["'Summarize my changes'"]
    end

    subgraph "CLI Logic"
        "Agent"["Agent Logic"] -- "Update" --> "updateAgentMetadata"["updateAgentMetadata() (extensions/cli/src/util/exit.ts)"]
    end

    subgraph "Code Entity Space"
        "updateAgentMetadata" --> "collectDiffStats"["collectDiffStats()"]
        "collectDiffStats" --> "getGitDiffSnapshot"["getGitDiffSnapshot() (extensions/cli/src/util/git.ts)"]
        "updateAgentMetadata" --> "postAgentMetadata"["postAgentMetadata() (extensions/cli/src/util/metadata.ts)"]
    end

    "postAgentMetadata" -- "API Call" --> "ControlPlane"["Continue Control Plane"]
```
**Sources:** [extensions/cli/src/util/exit.ts:104-137](), [extensions/cli/src/util/metadata.ts:125-150]()

### Key Built-in Tools and Features
- **Metadata Reporting:** Automatically calculates `DiffStats` (additions/deletions) and extracts conversation summaries to report to the control plane [extensions/cli/src/util/metadata.ts:27-59]().
- **Sub-agent Status:** Reports `FAILED` status and unhandled errors to the API when running in serve mode [extensions/cli/src/index.ts:99-117]().
- **Usage Tracking:** Tracks `totalCost`, `promptTokens`, and `completionTokens` per session [extensions/cli/src/util/exit.ts:76-95]().

For details, see [CLI Tool System and Sub-agents](#10.3).

**Sources:** [extensions/cli/src/util/metadata.ts:125-150](), [extensions/cli/src/util/exit.ts:142-183]()

## Build and Distribution

The CLI is bundled using `esbuild` into a single executable file to eliminate runtime dependency issues [extensions/cli/build.mjs:36-45]().

- **Bundling Strategy:** Local packages like `@continuedev/config-yaml` and `@continuedev/openai-adapters` are aliased and bundled directly into `dist/index.js` [extensions/cli/build.mjs:53-79]().
- **Alias Validation:** A `validate-aliases.mjs` script ensures all local `file:` dependencies in `package.json` have corresponding entries in the esbuild config to prevent runtime errors [extensions/cli/validate-aliases.mjs:137-165]().
- **Binary Wrapper:** A wrapper script `dist/cn.js` is generated with a shebang and execution logic [extensions/cli/build.mjs:93-96]().

**Sources:** [extensions/cli/build.mjs:53-79](), [extensions/cli/validate-aliases.mjs:137-165](), [extensions/cli/package.json:8-10]()

---

