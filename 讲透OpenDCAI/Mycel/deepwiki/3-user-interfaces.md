<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/Mycel · page 3 User Interfaces · fetched 2026-11-02 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent.py](agent.py)
- [frontend/app/src/api/message-mapper.ts](frontend/app/src/api/message-mapper.ts)
- [frontend/app/src/api/types.ts](frontend/app/src/api/types.ts)
- [frontend/app/src/components/CenteredInputBox.tsx](frontend/app/src/components/CenteredInputBox.tsx)
- [frontend/app/src/components/DragHandle.tsx](frontend/app/src/components/DragHandle.tsx)
- [frontend/app/src/components/ModelSelector.tsx](frontend/app/src/components/ModelSelector.tsx)
- [frontend/app/src/components/NewChatDialog.tsx](frontend/app/src/components/NewChatDialog.tsx)
- [frontend/app/src/components/Sidebar.tsx](frontend/app/src/components/Sidebar.tsx)
- [frontend/app/src/components/chat-area/AssistantBlock.tsx](frontend/app/src/components/chat-area/AssistantBlock.tsx)
- [frontend/app/src/components/chat-area/NoticeBubble.tsx](frontend/app/src/components/chat-area/NoticeBubble.tsx)
- [frontend/app/src/hooks/stream-event-handlers.ts](frontend/app/src/hooks/stream-event-handlers.ts)
- [frontend/app/src/hooks/use-stream-handler.ts](frontend/app/src/hooks/use-stream-handler.ts)
- [frontend/app/src/hooks/use-thread-manager.ts](frontend/app/src/hooks/use-thread-manager.ts)
- [frontend/app/src/hooks/use-workspace-settings.ts](frontend/app/src/hooks/use-workspace-settings.ts)
- [frontend/app/src/main.tsx](frontend/app/src/main.tsx)
- [frontend/app/src/pages/AppLayout.tsx](frontend/app/src/pages/AppLayout.tsx)
- [frontend/app/src/pages/ChatPage.tsx](frontend/app/src/pages/ChatPage.tsx)
- [frontend/app/src/pages/NewChatPage.tsx](frontend/app/src/pages/NewChatPage.tsx)
- [frontend/app/src/pages/RootLayout.tsx](frontend/app/src/pages/RootLayout.tsx)
- [frontend/app/src/router.tsx](frontend/app/src/router.tsx)
- [pyproject.toml](pyproject.toml)
- [tui/app.py](tui/app.py)
- [tui/leon_cli.py](tui/leon_cli.py)
- [tui/runner.py](tui/runner.py)
- [tui/widgets/status.py](tui/widgets/status.py)
- [uv.lock](uv.lock)

</details>



Mycel provides three distinct user interfaces for interacting with AI agents, each optimized for different use cases and environments. This page documents the architecture, entry points, and key components of each interface.

For detailed information about the backend APIs that power these interfaces, see [Backend Architecture](#8). For information about real-time streaming architecture, see [Real-time Streaming and Event Handling](#7.3).

---

## Overview of Interface Options

Mycel supports three user interfaces that share the same agent runtime and backend services:

| Interface | Entry Point | Primary Use Case | Key Technologies |
|-----------|-------------|------------------|------------------|
| **Web UI** | `http://localhost:8000` | Rich visual interaction, multi-tab workflows | React, TypeScript, Server-Sent Events |
| **Terminal UI (TUI)** | `leonai` command | Local terminal sessions, keyboard-driven workflows | Textual, Python |
| **CLI** | `leonai run`, `leonai thread`, etc. | Scripting, automation, non-interactive execution | argparse, Python asyncio |

All three interfaces communicate with the same FastAPI backend and share thread state through SQLite persistence.

**Sources**: [pyproject.toml:1-137](), [tui/leon_cli.py:1-797](), [frontend/app/src/main.tsx:1-55]()

---

## Web Interface Architecture

The web interface is a React single-page application (SPA) that provides the richest visual experience for interacting with Leon agents.

### Application Entry and Routing

```mermaid
graph TB
    main["main.tsx<br/>ReactDOM.createRoot"]
    router["router.tsx<br/>createBrowserRouter"]
    rootLayout["RootLayout<br/>Global navigation sidebar"]
    appLayout["AppLayout<br/>Chat-specific layout"]
    
    newChat["NewChatPage<br/>/chat/:memberId"]
    chatPage["ChatPage<br/>/chat/:memberId/:threadId"]
    
    members["MembersPage<br/>/members"]
    tasks["TasksPage<br/>/tasks"]
    settings["SettingsPage<br/>/settings"]
    resources["ResourcesPage<br/>/resources"]
    
    main --> router
    router --> rootLayout
    rootLayout --> appLayout
    rootLayout --> members
    rootLayout --> tasks
    rootLayout --> settings
    rootLayout --> resources
    
    appLayout --> newChat
    appLayout --> chatPage
```

**Application Bootstrap Flow**:

1. [frontend/app/src/main.tsx:49-54]() - React strict mode mount
2. [frontend/app/src/router.tsx:13-66]() - Browser router configuration with nested routes
3. [frontend/app/src/pages/RootLayout.tsx:24-178]() - Global navigation shell
4. [frontend/app/src/pages/AppLayout.tsx:15-101]() - Chat layout with sidebar and thread management

**Sources**: [frontend/app/src/main.tsx:1-55](), [frontend/app/src/router.tsx:1-67](), [frontend/app/src/pages/RootLayout.tsx:1-200](), [frontend/app/src/pages/AppLayout.tsx:1-140]()

---

### Chat Interface Components

The chat interface (`ChatPage`) is the core interaction point, orchestrating multiple sub-components and real-time streaming.

```mermaid
graph TB
    chatPage["ChatPage<br/>Main orchestrator"]
    
    subgraph "State Management Hooks"
        threadData["useThreadData<br/>Load history snapshot"]
        streamHandler["useStreamHandler<br/>SSE connection + events"]
        sandboxMgr["useSandboxManager<br/>Pause/resume sessions"]
        bgTasks["useBackgroundTasks<br/>Task notifications"]
    end
    
    subgraph "UI Components"
        header["Header<br/>Sandbox status + model selector"]
        chatArea["ChatArea<br/>Message history display"]
        inputBox["InputBox<br/>User message input"]
        computerPanel["ComputerPanel<br/>Tool execution viewer"]
        taskProgress["TaskProgress<br/>Status indicator"]
    end
    
    subgraph "Message Rendering"
        assistantBlock["AssistantBlock<br/>AI response + tools"]
        toolDetail["ToolDetailBox<br/>Tool call/result display"]
        markdown["MarkdownContent<br/>Text rendering"]
    end
    
    chatPage --> threadData
    chatPage --> streamHandler
    chatPage --> sandboxMgr
    chatPage --> bgTasks
    
    chatPage --> header
    chatPage --> chatArea
    chatPage --> inputBox
    chatPage --> computerPanel
    chatPage --> taskProgress
    
    chatArea --> assistantBlock
    assistantBlock --> toolDetail
    assistantBlock --> markdown
```

**Key Component Responsibilities**:

- **ChatPage** [frontend/app/src/pages/ChatPage.tsx:28-220]() - Root component, mounts with `key={threadId}` to reset state on thread change
- **ChatArea** - Renders message history, handles scrolling, displays `AssistantBlock` and `UserMessage` entries
- **AssistantBlock** [frontend/app/src/components/chat-area/AssistantBlock.tsx:92-170]() - Renders assistant turns with text segments, tool calls, and streaming indicators
- **InputBox** - Text input with sandbox/model selectors, handles Enter to send, Shift+Enter for newline
- **ComputerPanel** - Side panel showing tool execution details, agent hierarchy, and step-by-step flow

**Sources**: [frontend/app/src/pages/ChatPage.tsx:1-221](), [frontend/app/src/components/chat-area/AssistantBlock.tsx:1-171]()

---

### Real-Time Event Flow

The web interface uses Server-Sent Events (SSE) for real-time streaming of agent responses.

```mermaid
sequenceDiagram
    participant User
    participant InputBox
    participant StreamHandler["useStreamHandler"]
    participant API["POST /api/threads/{id}/messages"]
    participant SSE["GET /api/threads/{id}/events"]
    participant ChatArea
    participant ComputerPanel
    
    User->>InputBox: Type message + Enter
    InputBox->>StreamHandler: handleSendMessage(message)
    
    Note over StreamHandler: Create temporary turn<br/>with empty segments
    StreamHandler->>ChatArea: Update entries (optimistic)
    
    StreamHandler->>API: POST message
    API-->>StreamHandler: 200 OK {run_id}
    
    Note over StreamHandler: Persistent SSE connection<br/>already open
    
    SSE-->>StreamHandler: event: run_start
    SSE-->>StreamHandler: event: text {content}
    StreamHandler->>ChatArea: Append text chunk
    
    SSE-->>StreamHandler: event: tool_call
    StreamHandler->>ChatArea: Add tool segment
    StreamHandler->>ComputerPanel: Update tool view
    
    SSE-->>StreamHandler: event: tool_result
    StreamHandler->>ChatArea: Mark tool done
    StreamHandler->>ComputerPanel: Show result
    
    SSE-->>StreamHandler: event: run_done
    StreamHandler->>ChatArea: Finalize turn
```

**Event Processing Pipeline**:

1. [frontend/app/src/hooks/use-stream-handler.ts:72-268]() - `useStreamHandler` hook manages connection and turn state
2. [frontend/app/src/hooks/use-thread-stream.ts]() - `useThreadStream` maintains persistent SSE connection
3. [frontend/app/src/hooks/stream-event-handlers.ts:233-267]() - `processStreamEvent()` routes events to handlers
4. [frontend/app/src/api/message-mapper.ts:169-180]() - `mapBackendEntries()` converts history snapshots to UI format

**Critical Implementation Details**:

- **Persistent Connection**: SSE connection stays open across multiple runs (no reconnect on each message)
- **Turn Grouping**: Events with same `run_id` are grouped into a single `AssistantTurn`
- **Optimistic UI**: User message and empty assistant turn created immediately, then populated by events
- **State Synchronization**: `flushSync()` used to ensure turn ID is set before processing batched events

**Sources**: [frontend/app/src/hooks/use-stream-handler.ts:1-269](), [frontend/app/src/hooks/stream-event-handlers.ts:1-268]()

---

### New Chat Creation Flow

```mermaid
graph LR
    newChatPage["NewChatPage<br/>/chat/:memberId"]
    centeredInput["CenteredInputBox<br/>Sandbox + model selection"]
    handleSend["handleSend(message)"]
    createThread["POST /api/threads"]
    postRun["POST /api/threads/{id}/messages"]
    navigate["navigate() to ChatPage"]
    
    newChatPage --> centeredInput
    centeredInput --> handleSend
    handleSend --> createThread
    handleSend --> postRun
    handleSend --> navigate
    
    note["Note: postRun() is fire-and-forget<br/>ChatPage mounts immediately<br/>SSE picks up run_start when ready"]
```

**Flow Explanation**:

1. User types message in `CenteredInputBox` [frontend/app/src/components/CenteredInputBox.tsx:80-93]()
2. `handleSend()` in `NewChatPage` [frontend/app/src/pages/NewChatPage.tsx:28-46]():
   - Creates thread via `handleCreateThread()`
   - Fires `postRun()` without awaiting (fire-and-forget)
   - Navigates immediately to `ChatPage` with state `{runStarted: true}`
3. `ChatPage` mounts with optimistic user message + empty assistant turn
4. SSE connection starts at `seq=0` to catch buffered events
5. Agent creation completes (3-5s), `run_start` event arrives

**Sources**: [frontend/app/src/pages/NewChatPage.tsx:1-106](), [frontend/app/src/components/CenteredInputBox.tsx:1-280]()

---

## Terminal UI (TUI)

The Terminal UI provides a full-screen interactive experience using the Textual framework.

### TUI Application Structure

```mermaid
graph TB
    main["leon_cli.py main()<br/>CLI entry point"]
    launchTui["_launch_tui()<br/>Initialize agent + session"]
    runTui["run_tui()<br/>Start Textual app"]
    
    leonApp["LeonApp<br/>Textual.App subclass"]
    
    subgraph "Widgets"
        welcomeBanner["WelcomeBanner<br/>ASCII art header"]
        chatContainer["VerticalScroll<br/>Message container"]
        chatInput["ChatInput<br/>Message input"]
        statusBar["StatusBar<br/>Thread ID + shortcuts"]
    end
    
    subgraph "Message Widgets"
        userMsg["UserMessage"]
        assistantMsg["AssistantMessage"]
        toolCallMsg["ToolCallMessage"]
        toolResultMsg["ToolResultMessage"]
        thinking["ThinkingSpinner"]
    end
    
    main --> launchTui
    launchTui --> runTui
    runTui --> leonApp
    
    leonApp --> welcomeBanner
    leonApp --> chatContainer
    leonApp --> chatInput
    leonApp --> statusBar
    
    chatContainer --> userMsg
    chatContainer --> assistantMsg
    chatContainer --> toolCallMsg
    chatContainer --> toolResultMsg
    chatContainer --> thinking
```

**TUI Entry Point Flow**:

1. [tui/leon_cli.py:572-612]() - `main()` parses arguments and routes to subcommands
2. [tui/leon_cli.py:707-761]() - `_launch_tui()` creates agent and session manager
3. [tui/app.py:116-165]() - `LeonApp.__init__()` sets up state and registers callbacks
4. [tui/app.py:157-176]() - `LeonApp.on_mount()` loads history and registers wake handler

**Sources**: [tui/leon_cli.py:572-797](), [tui/app.py:1-800]()

---

### TUI Message Handling

```mermaid
sequenceDiagram
    participant User
    participant ChatInput
    participant LeonApp
    participant Agent["agent.astream()"]
    participant Container["#messages Container"]
    participant StatusBar
    
    User->>ChatInput: Type message + Enter
    ChatInput->>LeonApp: on_chat_input_submitted
    
    LeonApp->>LeonApp: Check if agent active
    
    alt Agent IDLE/READY
        LeonApp->>Container: mount(UserMessage)
        LeonApp->>Container: mount(ThinkingSpinner)
        LeonApp->>LeonApp: _start_agent_run()
        LeonApp->>Agent: astream(message)
        
        loop Streaming
            Agent-->>LeonApp: AIMessage chunk
            LeonApp->>Container: Update AssistantMessage
            Agent-->>LeonApp: tool_calls
            LeonApp->>Container: mount(ToolCallMessage)
            Agent-->>LeonApp: ToolMessage
            LeonApp->>Container: mount(ToolResultMessage)
        end
        
        Agent-->>LeonApp: Stream complete
        LeonApp->>StatusBar: update_stats()
        LeonApp->>LeonApp: Transition to IDLE
        LeonApp->>LeonApp: _state_driven_followup()
    else Agent ACTIVE
        LeonApp->>LeonApp: Queue message (steer)
        LeonApp->>User: notify("Message injected")
    end
```

**Message Processing Details**:

- [tui/app.py:198-212]() - `on_chat_input_submitted()` routes based on agent state
- [tui/app.py:298-332]() - `_handle_submission()` mounts user message with `await` for immediate render
- [tui/app.py:333-528]() - `_process_message()` streams agent response and mounts widgets
- [tui/app.py:530-534]() - `_state_driven_followup()` processes queued messages when agent becomes IDLE

**TUI-Specific Features**:

- **Refocus Input**: [tui/app.py:178-187]() - Click anywhere refocuses input after processing events
- **Double ESC**: [tui/app.py:189-196]() - Opens time-travel checkpoint browser
- **Keyboard Shortcuts**: Ctrl+Y (copy), Ctrl+E (export), Ctrl+L (clear), Ctrl+↑/↓ (history)
- **Command Mode**: [tui/app.py:214-246]() - `/help`, `/clear`, `/history`, `/resume`, `/rollback N`, `/compact`

**Sources**: [tui/app.py:157-800](), [tui/widgets/status.py:1-70]()

---

## Command Line Interface (CLI)

The CLI provides non-interactive and scripting capabilities through `leonai` commands.

### CLI Command Structure

```mermaid
graph TB
    main["main()<br/>Argument parser"]
    
    subgraph "Commands"
        launchTui["Launch TUI<br/>(default, no command)"]
        config["config [show]<br/>Interactive setup"]
        thread["thread ls|history|rewind|rm"]
        sandbox["sandbox ls|new|pause|resume|rm"]
        run["run [message]<br/>Non-interactive execution"]
    end
    
    subgraph "Thread Management"
        threadList["cmd_thread_list()<br/>List all threads"]
        threadHistory["cmd_thread_history()<br/>Show checkpoints"]
        threadRewind["cmd_thread_rewind()<br/>Time travel"]
        threadRm["cmd_thread_rm()<br/>Delete thread"]
    end
    
    subgraph "Sandbox Management"
        sandboxList["_cmd_sandbox_list()<br/>List sessions"]
        sandboxNew["_cmd_sandbox_new()<br/>Create session"]
        sandboxPause["_cmd_sandbox_pause()"]
        sandboxResume["_cmd_sandbox_resume()"]
        sandboxMetrics["_cmd_sandbox_metrics()"]
    end
    
    subgraph "Run Modes"
        runSingle["Single message"]
        runStdin["stdin (blank line separator)"]
        runInteractive["Interactive readline"]
    end
    
    main --> launchTui
    main --> config
    main --> thread
    main --> sandbox
    main --> run
    
    thread --> threadList
    thread --> threadHistory
    thread --> threadRewind
    thread --> threadRm
    
    sandbox --> sandboxList
    sandbox --> sandboxNew
    sandbox --> sandboxPause
    sandbox --> sandboxResume
    sandbox --> sandboxMetrics
    
    run --> runSingle
    run --> runStdin
    run --> runInteractive
```

**Command Categories**:

| Command | Subcommands | Purpose |
|---------|-------------|---------|
| `leonai` | *(none)* | Launch TUI with optional `--thread`, `--model`, `--sandbox`, `--agent` flags |
| `leonai config` | `show` | Interactive API key setup, display current configuration |
| `leonai thread` | `ls`, `history <id>`, `rewind <id> <checkpoint>`, `rm <id>` | Thread lifecycle and time-travel management |
| `leonai sandbox` | *(none)*, `ls`, `new [provider]`, `pause <id>`, `resume <id>`, `rm <id>`, `metrics <id>` | Sandbox session management (TUI or CLI) |
| `leonai run` | `"message"`, `--stdin`, `-i`, `-d` | Non-interactive execution modes |

**Sources**: [tui/leon_cli.py:572-797]()

---

### CLI Run Modes

The `leonai run` command supports multiple execution patterns for automation and scripting.

```mermaid
graph LR
    cmdRun["cmd_run()<br/>tui/runner.py"]
    
    subgraph "Input Modes"
        single["Single message<br/>leonai run 'message'"]
        stdin["Multi-turn stdin<br/>leonai run --stdin"]
        interactive["Interactive readline<br/>leonai run -i"]
    end
    
    subgraph "Execution"
        runner["NonInteractiveRunner"]
        runTurn["run_turn(message)<br/>Execute one turn"]
        processChunk["_process_chunk()<br/>Extract text + tools"]
    end
    
    subgraph "Output"
        stdout["Print to stdout"]
        json["JSON output<br/>--json flag"]
        debug["Debug output<br/>-d flag"]
    end
    
    cmdRun --> single
    cmdRun --> stdin
    cmdRun --> interactive
    
    single --> runner
    stdin --> runner
    interactive --> runner
    
    runner --> runTurn
    runTurn --> processChunk
    
    processChunk --> stdout
    processChunk --> json
    processChunk --> debug
```

**Run Mode Details**:

1. **Single Message** [tui/runner.py:246-279]() - Execute one turn, print response, exit
   ```bash
   leonai run "Explain the agent architecture"
   ```

2. **Multi-Turn via stdin** [tui/runner.py:281-311]() - Read messages separated by blank lines
   ```bash
   echo -e "First question\n\nSecond question" | leonai run --stdin
   ```

3. **Interactive Mode** [tui/runner.py:313-349]() - Simple readline loop (no TUI)
   ```bash
   leonai run -i
   ```

4. **Debug Output** [tui/runner.py:39-42]() - Show tool calls, token stats, runtime state
   ```bash
   leonai run -d "Complex task"
   ```

**NonInteractiveRunner Implementation**:

- [tui/runner.py:21-40]() - Constructor initializes agent and debug flags
- [tui/runner.py:44-109]() - `run_turn()` executes one conversation turn with timing
- [tui/runner.py:174-233]() - `_process_chunk()` extracts AIMessage content and tool calls
- [tui/runner.py:111-172]() - Debug output shows tokens, cost, context usage, memory stats

**Sources**: [tui/runner.py:1-349](), [tui/leon_cli.py:700-705]()

---

### CLI Thread Management

Thread management commands provide programmatic access to conversation history and checkpointing.

```mermaid
graph TB
    subgraph "Thread List"
        threadList["cmd_thread_list()<br/>Display all threads"]
        sessionMgr["SessionManager.get_threads()"]
        dbThreads["get_threads_from_db()"]
        timeTravelMgr["TimeTravelManager<br/>Checkpoint counts"]
    end
    
    subgraph "Thread History"
        threadHist["cmd_thread_history()<br/>Show checkpoints"]
        getCheckpoints["get_checkpoints(thread_id)"]
        displayTable["Rich.Table<br/>ID | Time | Message | File ops"]
    end
    
    subgraph "Thread Rewind"
        threadRewind["cmd_thread_rewind()<br/>Time travel"]
        findCheckpoint["Find checkpoint by prefix"]
        getOps["get_operations_to_revert()"]
        confirmPrompt["Confirmation prompt"]
        rewindTo["rewind_to(checkpoint_id)"]
        revertOps["Revert file operations"]
    end
    
    threadList --> sessionMgr
    threadList --> dbThreads
    threadList --> timeTravelMgr
    
    threadHist --> getCheckpoints
    getCheckpoints --> displayTable
    
    threadRewind --> findCheckpoint
    threadRewind --> getOps
    threadRewind --> confirmPrompt
    threadRewind --> rewindTo
    rewindTo --> revertOps
```

**Thread Command Examples**:

```bash
# List all threads with message counts and last active time
leonai thread ls

# Show checkpoint history for a specific thread
leonai thread history tui-abc12345

# Rewind to a previous checkpoint (time travel)
leonai thread rewind tui-abc12345 checkpoint-xyz -y

# Delete a thread
leonai thread rm tui-abc12345 -y
```

**Implementation Details**:

- [tui/leon_cli.py:47-96]() - `cmd_thread_list()` displays threads with Rich table
- [tui/leon_cli.py:99-143]() - `cmd_thread_history()` shows checkpoints with file operation counts
- [tui/leon_cli.py:146-202]() - `cmd_thread_rewind()` performs time travel with confirmation
- [tui/leon_cli.py:204-224]() - `cmd_thread_rm()` deletes thread from session manager

**Sources**: [tui/leon_cli.py:47-224]()

---

### CLI Sandbox Management

The `leonai sandbox` command provides both CLI and TUI interfaces for managing sandbox sessions.

```mermaid
graph TB
    cmdSandbox["cmd_sandbox(args)"]
    
    noSubcmd{{"subcommand<br/>is None?"}}
    launchTui["_launch_sandbox_tui()<br/>Open SandboxManagerApp"]
    
    subgraph "CLI Handlers"
        listSessions["_cmd_sandbox_list()<br/>Table of sessions"]
        newSession["_cmd_sandbox_new()<br/>Create session"]
        pauseSession["_cmd_sandbox_pause()"]
        resumeSession["_cmd_sandbox_resume()"]
        deleteSession["_cmd_sandbox_rm()"]
        showMetrics["_cmd_sandbox_metrics()"]
        destroyAll["_cmd_sandbox_destroy_all()"]
    end
    
    subgraph "Provider Layer"
        initProviders["_init_sandbox_providers()<br/>Load from ~/.leon/sandboxes/*.json"]
        createProvider["_create_provider(config)<br/>AgentBay/Docker/E2B/Daytona"]
        sandboxMgr["SandboxManager(provider)"]
    end
    
    cmdSandbox --> noSubcmd
    noSubcmd -->|Yes| launchTui
    noSubcmd -->|No| listSessions
    noSubcmd -->|No| newSession
    noSubcmd -->|No| pauseSession
    noSubcmd -->|No| resumeSession
    noSubcmd -->|No| deleteSession
    noSubcmd -->|No| showMetrics
    noSubcmd -->|No| destroyAll
    
    listSessions --> initProviders
    newSession --> initProviders
    pauseSession --> initProviders
    
    initProviders --> createProvider
    createProvider --> sandboxMgr
```

**Sandbox Command Examples**:

```bash
# Launch interactive TUI for managing sessions
leonai sandbox

# List all active sandbox sessions
leonai sandbox ls

# Create new session with default provider
leonai sandbox new

# Create session with specific provider
leonai sandbox new agentbay

# Pause a running session
leonai sandbox pause abc123

# Resume a paused session
leonai sandbox resume abc123

# Show resource metrics for a session
leonai sandbox metrics abc123

# Destroy all sessions (confirmation required)
leonai sandbox destroy-all-sessions
```

**Implementation Details**:

- [tui/leon_cli.py:334-372]() - `cmd_sandbox()` dispatches to subcommand handlers
- [tui/leon_cli.py:374-387]() - `_launch_sandbox_tui()` starts Textual sandbox manager
- [tui/leon_cli.py:226-251]() - `_init_sandbox_providers()` loads configs and creates providers
- [tui/leon_cli.py:253-302]() - `_create_provider()` instantiates provider from config
- [tui/leon_cli.py:389-409]() - `_cmd_sandbox_list()` displays session table
- [tui/leon_cli.py:506-539]() - `_cmd_sandbox_metrics()` shows CPU/memory/disk/network stats

**Sources**: [tui/leon_cli.py:226-570]()

---

## Interface Comparison

| Feature | Web UI | TUI | CLI |
|---------|--------|-----|-----|
| **Launch Command** | `uvicorn` or production server | `leonai` | `leonai run [options]` |
| **Primary Use Case** | Visual exploration, multi-tab workflows | Local terminal, keyboard-driven | Scripting, automation, CI/CD |
| **Message Display** | Rich HTML/CSS rendering | Textual widgets | Plain text or JSON |
| **Real-Time Updates** | SSE streaming | Async widget updates | Buffered output |
| **Tool Visualization** | ComputerPanel with collapsible steps | ToolCallMessage/ToolResultMessage widgets | Text output with optional debug |
| **Thread Management** | Sidebar with search | `/history` command + time travel | `leonai thread ls/history/rewind/rm` |
| **Sandbox Management** | Header status + modal dialogs | `/resume` command | `leonai sandbox [subcommand]` |
| **Multi-Threading** | Yes (browser tabs) | No (single thread per session) | Yes (separate process per thread) |
| **Offline Support** | No | Yes (local mode) | Yes (local mode) |
| **Mobile Support** | Yes (responsive design) | No | No |

**Sources**: [frontend/app/src/pages/ChatPage.tsx:1-221](), [tui/app.py:1-800](), [tui/runner.py:1-349]()

---

## Shared Backend Communication

All three interfaces communicate with the same FastAPI backend through REST and SSE endpoints.

```mermaid
graph TB
    subgraph "User Interfaces"
        webUI["Web UI<br/>React SPA"]
        tui["TUI<br/>Textual App"]
        cli["CLI<br/>Non-interactive"]
    end
    
    subgraph "Backend API Endpoints"
        threads["/api/threads"]
        messages["/api/threads/{id}/messages"]
        events["/api/threads/{id}/events"]
        settings["/api/settings"]
        panel["/api/panel"]
        resources["/api/resources"]
    end
    
    subgraph "Backend Services"
        streamingSvc["streaming_service.py<br/>SSE & Agent Execution"]
        agentPool["agent_pool.py<br/>Per-thread Agents"]
        taskSvc["task_service.py<br/>Task CRUD"]
        sandboxSvc["sandbox_service.py<br/>Session Management"]
    end
    
    subgraph "Persistence"
        sqlite[("SQLite<br/>threads.db")]
        filesystem[("File System<br/>~/.leon/")]
    end
    
    webUI -->|HTTP + SSE| threads
    webUI -->|HTTP + SSE| messages
    webUI -->|SSE| events
    
    tui -->|No HTTP<br/>Direct agent.astream()| agentPool
    cli -->|No HTTP<br/>Direct agent.astream()| agentPool
    
    webUI -->|HTTP| settings
    webUI -->|HTTP| panel
    webUI -->|HTTP| resources
    
    threads --> streamingSvc
    messages --> streamingSvc
    events --> streamingSvc
    
    streamingSvc --> agentPool
    streamingSvc --> sqlite
    
    settings --> filesystem
    panel --> taskSvc
    resources --> sandboxSvc
    
    taskSvc --> sqlite
    sandboxSvc --> sqlite
```

**Key Differences**:

- **Web UI**: Uses HTTP/SSE for all communication, requires backend server running
- **TUI/CLI**: Bypass backend, call `agent.astream()` directly, write to SQLite directly

**Sources**: [frontend/app/src/api/index.ts](), [tui/app.py:333-528](), [tui/runner.py:44-109]()

---

