<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/OpenHarness · page 11 Session Management and Services · fetched 2026-11-09 -->

# Session Management and Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ohmo/session_storage.py](ohmo/session_storage.py)
- [src/openharness/bridge/session_runner.py](src/openharness/bridge/session_runner.py)
- [src/openharness/services/session_storage.py](src/openharness/services/session_storage.py)
- [src/openharness/swarm/subprocess_backend.py](src/openharness/swarm/subprocess_backend.py)
- [src/openharness/tasks/manager.py](src/openharness/tasks/manager.py)
- [src/openharness/tasks/types.py](src/openharness/tasks/types.py)
- [tests/test_bridge/test_core.py](tests/test_bridge/test_core.py)
- [tests/test_ohmo/test_ohmo_session_storage.py](tests/test_ohmo/test_ohmo_session_storage.py)
- [tests/test_services/test_session_storage.py](tests/test_services/test_session_storage.py)
- [tests/test_tasks/test_manager.py](tests/test_tasks/test_manager.py)
- [tests/test_tools/test_task_tools.py](tests/test_tools/test_task_tools.py)

</details>



Session Management in OpenHarness encompasses the lifecycle of user interactions, background execution units, and specialized supporting services that maintain state across restarts. This subsystem ensures that agent progress is persistent, long-running tasks are monitored, and child sessions can be orchestrated through "bridge" mechanisms.

## Session Storage and Persistence

OpenHarness provides robust session persistence by capturing snapshots of the conversation state, including message history, tool results, and metadata. Sessions are scoped to the project directory and keyed using SHA1 hashes of the project path to ensure isolation between different workspaces [src/openharness/services/session_storage.py:54-60]().

The persistence layer uses `save_session_snapshot()` to serialize the current `ConversationMessage` list, `UsageSnapshot`, and critical `tool_metadata` (such as permission modes and skill invocations) to JSON files [src/openharness/services/session_storage.py:63-96](). These snapshots are stored both as a unique session ID file and as a `latest.json` pointer for easy resumption [src/openharness/services/session_storage.py:99-105]().

Key capabilities include:
*   **Snapshots**: Automatically saving and loading session state using `save_session_snapshot()` and `load_session_snapshot()` [src/openharness/services/session_storage.py:123-128]().
*   **Project Isolation**: Directories are named using a digest of the absolute project path [src/openharness/services/session_storage.py:57-58]().
*   **Metadata Sanitization**: A dedicated `_persistable_tool_metadata` filter ensures only safe, relevant keys (e.g., `permission_mode`, `task_focus_state`) are written to disk [src/openharness/services/session_storage.py:18-51]().
*   **Export**: Converting session history into readable formats via `export_session_markdown()` [src/openharness/services/session_storage.py:206-224]().

For details, see [Session Storage](#11.1).

Sources: [src/openharness/services/session_storage.py:1-224](), [ohmo/session_storage.py:41-85]()

## Background Tasks

The `BackgroundTaskManager` in `tasks/manager.py` handles the execution of asynchronous operations that must persist outside the primary LLM query loop [src/openharness/tasks/manager.py:49-59](). This includes shell commands and sub-agent workflows that might take significant time to complete.

*   **Task Types**: Supports `local_bash` for shell commands and `local_agent` / `in_process_teammate` for agentic sub-processes [src/openharness/tasks/types.py:10-11]().
*   **Subprocess Management**: `create_shell_task()` [src/openharness/tasks/manager.py:61-112]() and `create_agent_task()` [src/openharness/tasks/manager.py:114-158]() manage the lifecycle of `asyncio.subprocess.Process` instances.
*   **Input/Output**: Tasks support non-blocking output reading via `read_task_output()` [tests/test_tasks/test_manager.py:29-29]() and interactive stdin writing via `write_to_task()` [src/openharness/tasks/manager.py:147-161]().
*   **Automatic Restart**: If a message is sent to a stopped agent task, the manager can restart the process, though it injects a notice that prior interactive context was lost [src/openharness/tasks/manager.py:20-20](), [tests/test_tasks/test_manager.py:68-91]().

For details, see [Background Tasks](#11.2).

Sources: [src/openharness/tasks/manager.py:49-180](), [src/openharness/tasks/types.py:1-33](), [tests/test_tasks/test_manager.py:15-45]()

## Bridge Sessions and Supporting Services

Bridge sessions allow OpenHarness to spawn and track child processes that act as independent sessions. This is primarily facilitated by the `SubprocessBackend` which bridges the swarm coordination logic with the task management system.

### Bridge Session Architecture
The bridge system uses the `BackgroundTaskManager` to track session records, which wrap underlying process handles.

| Entity | Role |
| :--- | :--- |
| `SubprocessBackend` | Implementation of `TeammateExecutor` that routes agent spawns through the task manager [src/openharness/swarm/subprocess_backend.py:28-35](). |
| `SessionHandle` | Dataclass representing a spawned bridge process with its PID and start time [src/openharness/bridge/session_runner.py:14-20](). |
| `spawn_session` | Helper to create a shell subprocess for bridge-managed child sessions [src/openharness/bridge/session_runner.py:32-46](). |
| `WorkSecret` | Model for encoding session tokens and API URLs for child session authentication [tests/test_bridge/test_core.py:13-17](). |

### Supporting Services
Beyond session management, OpenHarness includes several specialized services:
*   **Conversation Compaction**: Optimizes context window usage by summarizing history, tracked via `compact_checkpoints` in session metadata [src/openharness/services/session_storage.py:27-28]().
*   **Teammate Spawning**: Utilities in `subprocess_backend.py` handle the inheritance of CLI flags (model, prompts) and environment variables for child agents [src/openharness/swarm/subprocess_backend.py:55-73]().
*   **Task Tools**: A suite of tools (`TaskCreateTool`, `TaskOutputTool`, `TaskUpdateTool`) provide the LLM with an interface to interact with the `BackgroundTaskManager` [tests/test_tools/test_task_tools.py:14-16]().

For details, see [Bridge Sessions and Supporting Services](#11.3).

### Bridge Management Flow

The following diagram illustrates how the `SubprocessBackend` coordinates with the `BackgroundTaskManager` to manage child processes.

**Bridge Management Flow**
```mermaid
graph TD
    subgraph "Code Entity Space: swarm/subprocess_backend.py"
        [SB_SubprocessBackend]
        [SB_spawn]
        [SB_send_message]
    end

    subgraph "Code Entity Space: tasks/manager.py"
        [BTM_BackgroundTaskManager]
        [BTM_create_agent_task]
        [BTM_write_to_task]
        [BTM_stop_task]
    end

    subgraph "Code Entity Space: bridge/session_runner.py"
        [SR_spawn_session]
        [SR_SessionHandle]
    end

    [SB_spawn] -- "requests task" --> [BTM_create_agent_task]
    [SB_send_message] -- "writes stdin" --> [BTM_write_to_task]
    [SB_SubprocessBackend] -- "uses" --> [BTM_BackgroundTaskManager]
    [SR_spawn_session] -- "returns" --> [SR_SessionHandle]
    [BTM_BackgroundTaskManager] -- "manages" --> [PROC_asyncio_subprocess_Process]
```
Sources: [src/openharness/swarm/subprocess_backend.py:47-115](), [src/openharness/tasks/manager.py:114-158](), [src/openharness/bridge/session_runner.py:32-46]()

### Session Interaction Components

This diagram maps the natural language concept of "Session Management" to the specific classes and methods responsible for execution within the task and storage subsystems.

**Session Service Mapping**
```mermaid
graph LR
    subgraph "Natural Language Space"
        [NL_Spawn_Agent]
        [NL_Monitor_Output]
        [NL_Save_State]
        [NL_Load_State]
    end

    subgraph "Code Entity Space"
        [CE_BTM_create_agent_task]
        [CE_BTM_read_task_output]
        [CE_SS_save_session_snapshot]
        [CE_SS_load_session_snapshot]
    end

    [NL_Spawn_Agent] --> [CE_BTM_create_agent_task]
    [NL_Monitor_Output] --> [CE_BTM_read_task_output]
    [NL_Save_State] --> [CE_SS_save_session_snapshot]
    [NL_Load_State] --> [CE_SS_load_session_snapshot]
```
Sources: [src/openharness/tasks/manager.py:114-158](), [src/openharness/tasks/manager.py:162-168](), [src/openharness/services/session_storage.py:63-107](), [src/openharness/services/session_storage.py:123-128]()

---

**Child Pages:**
*   [[11.1 Session Storage]]
*   [[11.2 Background Tasks]]
*   [[11.3 Bridge Sessions and Supporting Services]]

---

