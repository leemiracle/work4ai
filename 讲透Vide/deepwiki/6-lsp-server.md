<!-- source: DeepWiki mcp.deepwiki.com · repo pascal-lab/vide · page 6 LSP Server · fetched 2026-10-12 -->

# LSP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/config.rs](src/config.rs)
- [src/global_state.rs](src/global_state.rs)
- [src/global_state/handlers/notification.rs](src/global_state/handlers/notification.rs)
- [src/global_state/main_loop.rs](src/global_state/main_loop.rs)
- [src/global_state/mem_docs.rs](src/global_state/mem_docs.rs)
- [src/global_state/process_changes.rs](src/global_state/process_changes.rs)
- [src/global_state/reload.rs](src/global_state/reload.rs)
- [src/global_state/snapshot.rs](src/global_state/snapshot.rs)
- [src/main.rs](src/main.rs)

</details>



The LSP Server is the entry point for the Vide language server. It manages the lifecycle of the server process, coordinates between the Virtual File System (VFS) and the incremental analysis engine, and translates between internal compiler representations and the Language Server Protocol (LSP) wire format.

The server is built on a multi-threaded architecture using a central `GlobalState` to manage synchronization and snapshot isolation, ensuring that long-running analysis tasks do not block the main responsive loop.

## Architecture Overview

The server operates as a state machine driven by an event loop. It handles three primary types of events:
1.  **LSP Messages**: Requests, notifications, and responses from the client [src/global_state/event_loop.rs:1-50]().
2.  **Task Results**: Completed background work from the `TaskPool` [src/global_state.rs:86-88]().
3.  **VFS Events**: File system changes or file loading progress [src/global_state.rs:114-122]().

### System Flow: Request to Response
The following diagram illustrates how an LSP request flows through the server components.

**LSP Request Lifecycle**
```mermaid
graph TD
    subgraph "LSP Client (VS Code)"
        [Client]
    end

    subgraph "LSP Server (src/)"
        [main_loop] -- "Event::Lsp" --> [ReqDispatcher]
        [ReqDispatcher] -- "Dispatch" --> [Handlers]
        [Handlers] -- "from_proto" --> [InternalTypes]
        [InternalTypes] -- "Query" --> [GlobalStateSnapshot]
        [GlobalStateSnapshot] -- "ide::Analysis" --> [SalsaDB]
        [SalsaDB] -- "Result" --> [Handlers]
        [Handlers] -- "to_proto" --> [LSPTypes]
        [LSPTypes] -- "Response" --> [main_loop]
    end

    [Client] -- "JSON-RPC Request" --> [main_loop]
    [main_loop] -- "JSON-RPC Response" --> [Client]

    style [GlobalStateSnapshot] stroke-dasharray: 5 5
```
Sources: [src/global_state/main_loop.rs:47-53](), [src/global_state/event_loop.rs:1-100](), [src/global_state/snapshot.rs:65-79]()

## Key Components

### GlobalState and Main Loop
The `GlobalState` struct [src/global_state.rs:67-77]() is the central repository of server state. It owns the `AnalysisHost` (interface to Salsa), the `Vfs`, and the `TaskPool`. The `main_loop` [src/global_state/main_loop.rs:5]() continuously polls for events and dispatches them.

Crucially, the server uses **snapshot isolation**: when a request starts, it takes a `GlobalStateSnapshot` [src/global_state.rs:160-191](), which provides a consistent, immutable view of the database. This allows the main loop to process new changes (like `didChange` notifications) while background threads compute responses for older snapshots.

For details, see [GlobalState and Main Loop](#6.1).

### LSP Request and Notification Handlers
LSP messages are routed via dispatchers [src/global_state.rs:2-3]().
- **Requests**: Handlers perform read-only queries against a snapshot.
- **Notifications**: Handlers like `handle_did_open_text_document` [src/global_state/handlers/notification.rs:7-10]() update the `GlobalState` (e.g., updating `MemDocs` [src/global_state/mem_docs.rs:43-46]() and the `Vfs`).

For details, see [LSP Request and Notification Handlers](#6.2).

### Protocol Translation
The `lsp_ext` module handles the mapping between Vide's internal logic (using `FileId`, `TextRange`, and `AbsPathBuf`) and the LSP's URI and Position-based protocol. This layer also handles `PositionEncoding` [src/config.rs:195-197]() to ensure compatibility with different editors.

For details, see [Protocol Translation (to_proto / from_proto)](#6.3).

### Diagnostic Publishing
Vide supports both "push" and "pull" diagnostics. The `GlobalState` tracks `published_diagnostics` [src/global_state.rs:104]() to avoid redundant updates and manages `DiagnosticFileRevision` [src/global_state.rs:111]() to ensure diagnostics stay in sync with the `MemDocs` [src/global_state/mem_docs.rs:18-21]().

For details, see [Diagnostic Publishing and Snapshot](#6.4).

### Qihe Analysis Integration
The server includes a specialized sub-system for "Qihe Analysis" [src/global_state.rs:73](), which provides deep semantic checks. This integration includes custom LSP extensions for progress reporting and log streaming [src/global_state.rs:54-57]().

For details, see [Qihe Analysis Integration](#6.5).

## Data Mapping: LSP to Internal

The server bridges the gap between the editor's view of a project and the compiler's view.

| LSP Concept | Internal Entity | Mapping Logic |
| :--- | :--- | :--- |
| `lsp_types::Url` | `vfs::VfsPath` | `from_proto::vfs_path` [src/global_state/snapshot.rs:105]() |
| `lsp_types::Position` | `ByteOffset` | `LineIndex::offset()` [src/global_state/snapshot.rs:134]() |
| `lsp_types::Diagnostic` | `ide::diagnostics::Diagnostic` | `to_proto::diagnostic` [src/global_state/snapshot.rs:184]() |
| `lsp_types::TextDocumentVersion` | `MemDocs::version` | `MemDocs::version_for_path` [src/global_state/mem_docs.rs:172-174]() |

**Code Entity Mapping Diagram**
```mermaid
graph LR
    subgraph "LSP Protocol Space"
        [Url]
        [LspPos] -- "Line/Col" --> [LspRange]
    end

    subgraph "Internal Code Space (src/)"
        [VfsPath]
        [FileId]
        [LineInfo]
        [MemDocs]
    end

    [Url] <== "from_proto::vfs_path" ==> [VfsPath]
    [VfsPath] <== "GlobalStateSnapshot::file_id" ==> [FileId]
    [LspPos] <== "LineInfo::index" ==> [LineInfo]
    [FileId] -- "lookup" --> [MemDocs]
```
Sources: [src/global_state/snapshot.rs:104-110](), [src/global_state/snapshot.rs:129-138](), [src/global_state/mem_docs.rs:176-178]()

## Server Entry Point

The server is started via `run_server` in `src/lib.rs`, which is called by the `main` function [src/main.rs:114-125](). It initializes logging [src/main.rs:47-112](), parses command-line `Opt` arguments, and establishes the `lsp_server::Connection`.

```rust
// src/main.rs
fn main() -> anyhow::Result<()> {
    let opt = Opt::parse();
    let _profile_guard = setup_logging(&opt)?;
    run_server(opt)?;
    Ok(())
}
```
Sources: [src/main.rs:114-125]()

### Sources:
- [src/main.rs:1-126]()
- [src/global_state.rs:1-191]()
- [src/global_state/main_loop.rs:1-54]()
- [src/global_state/snapshot.rs:65-188]()
- [src/global_state/mem_docs.rs:1-46]()
- [src/config.rs:1-212]()
- [src/global_state/handlers/notification.rs:1-15]()

---

