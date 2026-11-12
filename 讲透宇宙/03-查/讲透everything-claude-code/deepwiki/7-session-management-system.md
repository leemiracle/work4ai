<!-- source: DeepWiki mcp.deepwiki.com · repo affaan-m/everything-claude-code · page 7 Session Management System · fetched 2026-10-26 -->

# Session Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [commands/resume-session.md](commands/resume-session.md)
- [commands/save-session.md](commands/save-session.md)
- [scripts/hooks/config-protection.js](scripts/hooks/config-protection.js)
- [scripts/hooks/governance-capture.js](scripts/hooks/governance-capture.js)
- [scripts/hooks/session-end.js](scripts/hooks/session-end.js)
- [scripts/hooks/session-start.js](scripts/hooks/session-start.js)
- [scripts/hooks/suggest-compact.js](scripts/hooks/suggest-compact.js)
- [scripts/lib/agent-compress.js](scripts/lib/agent-compress.js)
- [scripts/lib/inspection.js](scripts/lib/inspection.js)
- [scripts/lib/package-manager.js](scripts/lib/package-manager.js)
- [scripts/lib/session-aliases.js](scripts/lib/session-aliases.js)
- [scripts/lib/session-manager.js](scripts/lib/session-manager.js)
- [scripts/lib/utils.js](scripts/lib/utils.js)
- [tests/ci/validators.test.js](tests/ci/validators.test.js)
- [tests/hooks/governance-capture.test.js](tests/hooks/governance-capture.test.js)
- [tests/hooks/hooks.test.js](tests/hooks/hooks.test.js)
- [tests/integration/hooks.test.js](tests/integration/hooks.test.js)
- [tests/lib/agent-compress.test.js](tests/lib/agent-compress.test.js)
- [tests/lib/inspection.test.js](tests/lib/inspection.test.js)
- [tests/lib/package-manager.test.js](tests/lib/package-manager.test.js)
- [tests/lib/session-aliases.test.js](tests/lib/session-aliases.test.js)
- [tests/lib/session-manager.test.js](tests/lib/session-manager.test.js)
- [tests/lib/utils.test.js](tests/lib/utils.test.js)

</details>



## Purpose and Scope

The session management system provides persistent memory across independent Claude Code invocations through markdown-formatted session files. It handles session CRUD operations, human-readable aliases, metadata extraction, and strategic compaction recommendations. This architecture enables autonomous loops where each `claude -p` invocation can access historical context without relying on the underlying Claude instance's memory.

For information about session hooks integration, see [Session & Context Hooks](#6.4). For session-aliases.json format details, see [Session Aliases System](#7.3).

---

## Session Storage Architecture

### Session File Format and Naming Convention

Session files are stored as markdown in a canonical `session-data` directory with fallback support for legacy paths [scripts/lib/utils.js:16-17](). The system uses a standardized naming convention [scripts/lib/session-manager.js:5-9]():

```
YYYY-MM-DD-session.tmp              (legacy format, no ID)
YYYY-MM-DD-<short-id>-session.tmp   (modern format, short-id is sanitized)
```

**Naming Convention Components:**

| Component | Format | Validation | Example |
|-----------|--------|------------|---------|
| Year | `YYYY` | 4-digit year | `2026` |
| Month | `MM` | 01-12, calendar-accurate | `02` |
| Day | `DD` | 01-31, calendar-accurate with month validation | `01` |
| Short ID | `[a-zA-Z0-9_][a-zA-Z0-9_-]*` | Alphanumeric, underscores, hyphens | `a1b2c3d4` |
| Extension | `.tmp` | Fixed | `.tmp` |

The `parseSessionFilename()` function validates calendar accuracy by rejecting impossible dates like Feb 31 or Apr 31 using JavaScript's `Date` constructor rollover detection [scripts/lib/session-manager.js:34-61]().

### Session Filename Parsing Flow

Title: Session Filename Parsing and Validation Flow
```mermaid
graph LR
    subgraph "Filename Components"
        [DateNode] ["Date<br/>YYYY-MM-DD"]
        [IdNode] ["Short ID<br/>(optional)<br/>alphanumeric"]
        [SuffixNode] ["session.tmp"]
    end
    
    subgraph "Validation Logic [session-manager.js]"
        [DateCheck] ["parseSessionFilename()<br/>- Month: 1-12<br/>- Day: 1-31<br/>- Date rollover check"]
        [IdCheck] ["Regex Match:<br/>- [a-zA-Z0-9_][a-zA-Z0-9_-]*"]
    end
    
    subgraph "Parsed Metadata Entity"
        [ParsedDate] ["date: '2026-02-01'"]
        [ParsedId] ["shortId: 'a1b2c3d4'<br/>or 'no-id'"]
        [ParsedTime] ["datetime: Date object"]
    end
    
    [DateNode] --> [DateCheck]
    [IdNode] --> [IdCheck]
    [DateCheck] --> [ParsedDate]
    [IdCheck] --> [ParsedId]
    [ParsedDate] --> [ParsedTime]
```
**Sources:** [scripts/lib/session-manager.js:27-61](), [tests/lib/session-manager.test.js:51-88]()

---

## Session Manager API

The `session-manager.js` module provides the core API for session CRUD operations, metadata parsing, and candidate resolution.

### Core API Functions

Title: Session Manager API Entity Map
```mermaid
graph TB
    subgraph "Parsing & Metadata [session-manager.js]"
        [ParseFilename] ["parseSessionFilename(filename)<br/>→ {shortId, date, datetime, filename}"]
        [ParseMeta] ["parseSessionMetadata(content)<br/>→ {title, project, branch, worktree, ...}"]
        [GetStats] ["getSessionStats(content)<br/>→ {totalItems, completedItems, lineCount}"]
    end
    
    subgraph "Resolution & Search"
        [GetCandidates] ["getSessionCandidates(options)<br/>→ sessionRecord[]"]
        [GetMatches] ["getMatchingSessionCandidates(id)<br/>→ sessionRecord[]"]
    end
    
    subgraph "I/O Operations"
        [GetContent] ["getSessionContent(path)<br/>→ string | null"]
        [WriteContent] ["writeSessionContent(path, content)<br/>→ boolean"]
    end
    
    subgraph "Storage Utilities [utils.js]"
        [GetSessionsDir] ["getSessionsDir()<br/>→ ~/.claude/session-data/"]
        [GetSearchDirs] ["getSessionSearchDirs()<br/>→ [canonical, legacy]"]
    end
    
    [GetCandidates] --> [GetSearchDirs]
    [GetMatches] --> [GetSearchDirs]
    [GetContent] --> [GetSessionsDir]
```
**Sources:** [scripts/lib/session-manager.js:1-240](), [scripts/lib/utils.js:41-57]()

### Session Metadata Extraction

The `parseSessionMetadata()` function extracts structured data from markdown session files using regex patterns [scripts/lib/session-manager.js:225-270]():

| Field | Extraction Logic | Source File |
|-------|------------------|-------------|
| `title` | First H1 heading (`^#\s+(.+)$`) | [scripts/lib/session-manager.js:227]() |
| `project` | `**Project:**` header field | [scripts/lib/session-manager.js:231]() |
| `worktree` | `**Worktree:**` header field | [scripts/lib/session-manager.js:233]() |
| `completed` | List items under `### Completed` | [scripts/lib/session-manager.js:235]() |
| `context` | Fenced code block under `### Context to Load` | [scripts/lib/session-manager.js:238]() |

**Sources:** [scripts/lib/session-manager.js:225-270](), [tests/lib/session-manager.test.js:92-130]()

---

## Session Aliases System

The aliases system provides human-readable names for sessions, stored in `~/.claude/session-aliases.json` [scripts/lib/session-aliases.js:17-19]().

### Alias Resolution and Validation

Title: Session Alias Resolution and Validation
```mermaid
graph TB
    subgraph "Validation [session-aliases.js]"
        [Input] ["Input: alias string"]
        [ValidateChars] ["Check: /^[a-zA-Z0-9_-]+$/"]
        [ValidateReserved] ["Check: reserved names<br/>(list, help, delete, create, set)"]
    end
    
    subgraph "Storage [session-aliases.json]"
        [LoadFile] ["loadAliases()"]
        [AliasesObj] ["aliases: { 'my-task': { sessionPath, title } }"]
    end
    
    subgraph "Resolution Result"
        [Found] ["Return AliasData:<br/>{ alias, sessionPath, title }"]
        [NotFound] ["Return: null"]
    end
    
    [Input] --> [ValidateChars]
    [ValidateChars] --> [ValidateReserved]
    [ValidateReserved] --> [LoadFile]
    [LoadFile] --> [AliasesObj]
    [AliasesObj] -->|exists| [Found]
    [AliasesObj] -->|not exists| [NotFound]
```
**Sources:** [scripts/lib/session-aliases.js:158-179](), [tests/lib/session-aliases.test.js:104-134]()

---

## Session Lifecycle and Persistence

Session hooks bridge context across independent Claude invocations by loading previous session content and saving session summaries.

### Persistence Logic

1.  **Session Start:** `session-start.js` searches for recent sessions (last 7 days) [scripts/hooks/session-start.js:57](). It prioritizes sessions matching the current working directory (`Worktree`) or project name via `selectMatchingSession` [scripts/hooks/session-start.js:185-208]().
2.  **Session End:** `session-end.js` extracts a summary from the session transcript (`transcript.jsonl`), including user messages, tools used, and files modified [scripts/hooks/session-end.js:39-110]().
3.  **Persistence:** Summaries are updated in the session file using markers (`<!-- ECC:SUMMARY:START -->`) to ensure continuity [scripts/hooks/session-end.js:28-29]().
4.  **Pruning:** The system automatically prunes expired sessions based on the `ECC_SESSION_RETENTION_DAYS` environment variable (defaulting to 30 days) [scripts/hooks/session-start.js:85-90](), [scripts/hooks/session-start.js:119-157]().

**Sources:** [scripts/hooks/session-start.js:1-208](), [scripts/hooks/session-end.js:1-230]()

---

## Child Pages
- [Session Files & Format](#7.1) — Document session file naming convention (YYYY-MM-DD-shortid-session.tmp), markdown structure, metadata sections, and legacy format support.
- [Session Manager API](#7.2) — Document session-manager.js API including parseSessionFilename, getSessionById, getAllSessions, writeSessionContent, and pagination.
- [Session Aliases System](#7.3) — Document session-aliases.js API including setAlias, resolveAlias, listAliases, deleteAlias, renameAlias, and cleanup operations.
- [Session Lifecycle & Persistence](#7.4) — Explain session-start.js and session-end.js hook behavior, summary extraction from transcript.jsonl, and cross-session memory bridge.
- [Strategic Compaction](#7.5) — Document suggest-compact.js behavior, tool call tracking, threshold system, and manual compaction recommendations.
- [Session Adapters](#7.6) — Document the session adapter registry (claude-history, dmux-tmux adapters), the canonical session snapshot format, structured target resolution, and the session-inspect CLI for emitting unified session views across harness types.

---

