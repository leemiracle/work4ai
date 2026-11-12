<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/nanobot · extra page Shell Execution & Exec Sessions · fetched 2026-11-09 -->

# Shell Execution & Exec Sessions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nanobot/agent/tools/_windows_job.py](nanobot/agent/tools/_windows_job.py)
- [nanobot/agent/tools/exec_session.py](nanobot/agent/tools/exec_session.py)
- [nanobot/agent/tools/shell.py](nanobot/agent/tools/shell.py)
- [tests/tools/test_exec_allow_patterns.py](tests/tools/test_exec_allow_patterns.py)
- [tests/tools/test_exec_env.py](tests/tools/test_exec_env.py)
- [tests/tools/test_exec_platform.py](tests/tools/test_exec_platform.py)
- [tests/tools/test_exec_security.py](tests/tools/test_exec_security.py)
- [tests/tools/test_exec_session_tools.py](tests/tools/test_exec_session_tools.py)
- [tests/tools/test_shell_reap.py](tests/tools/test_shell_reap.py)
- [tests/tools/test_tool_loader.py](tests/tools/test_tool_loader.py)

</details>



This page provides a detailed technical overview of how nanobot executes shell commands, manages long-running sessions, and enforces security policies. It covers the `ExecTool` for one-shot commands, `ExecSessionManager` for interactive sessions, process-tree management, Windows Job Objects, and the allow/deny pattern guards.

## ExecTool: One-Shot Shell Execution

The `ExecTool` [nanobot/agent/tools/shell.py:162-163]() is nanobot's primary mechanism for executing shell commands. It is designed for single, non-interactive commands where the agent expects a final result upon completion.

### Configuration

The behavior of `ExecTool` is governed by `ExecToolConfig` [nanobot/agent/tools/shell.py:94-105](). Key configuration parameters include:
- `enable`: Boolean to enable or disable the tool.
- `timeout`: Hard timeout in seconds for command execution. A value of `0` means no limit.
- `path_prepend`, `path_append`: Strings to prepend or append to the `PATH` environment variable for executed commands. This allows agents to use custom binaries or prioritize certain executables.
- `sandbox`: Specifies a sandboxing mechanism (e.g., `bwrap`).
- `sandbox_ro_binds`, `sandbox_rw_binds`: Lists of paths to bind into the sandbox as read-only or read-write.
- `allowed_env_keys`: A whitelist of environment variables from the parent process that are allowed to be passed to the child process. By default, nanobot aggressively filters environment variables to prevent leakage of sensitive information [tests/tools/test_exec_env.py:15-20]().
- `allow_patterns`, `deny_patterns`: Regular expression lists used to guard against potentially malicious commands.

### Command Preparation and Environment

Before execution, `ExecTool` performs several steps:
1.  **Environment Building**: It constructs a sanitized environment for the subprocess. On Unix, this includes `HOME`, `LANG`, `TERM`, and `PYTHONUNBUFFERED`. On Windows, it includes `SYSTEMROOT`, `COMSPEC`, `USERPROFILE`, and other essential Windows environment variables [tests/tools/test_exec_platform.py:40-47](). Crucially, sensitive environment variables (like API keys) are filtered out [tests/tools/test_exec_platform.py:57-66]().
2.  **PATH Management**: The `path_prepend` and `path_append` configurations are applied to the `PATH` environment variable. `path_prepend` takes precedence [tests/tools/test_exec_env.py:50-67](). Shell metacharacters in `path_append` are treated as literal path characters to prevent injection attacks [tests/tools/test_exec_env.py:125-162]().
3.  **Working Directory**: The `working_dir` parameter specifies the current working directory for the command.
4.  **Shell Selection**: On Unix, `bash` is the default shell, with options for `sh` or `zsh`. On Windows, `PowerShell` is preferred for single-line commands, falling back to `cmd.exe` if `PowerShell` is unavailable or for multi-line commands [tests/tools/test_exec_platform.py:177-188]().

### Security Guards: Allow/Deny Patterns and Workspace Restrictions

`ExecTool` implements robust security measures to prevent arbitrary code execution and unauthorized access:
-   **Allow/Deny Patterns**: Commands are checked against `allow_patterns` and `deny_patterns` [nanobot/agent/tools/shell.py:104-105](). If `allow_patterns` are defined, a command must match at least one pattern to be executed; otherwise, it's blocked [tests/tools/test_exec_allow_patterns.py:50-59](). `deny_patterns` block commands that match any of its regexes, even if they are otherwise allowed [tests/tools/test_exec_allow_patterns.py:8-14](). Allow patterns take precedence over deny patterns [tests/tools/test_exec_allow_patterns.py:15-21]().
-   **Workspace Restrictions**: The `restrict_to_workspace` setting ensures that commands cannot access files or directories outside the agent's designated workspace [nanobot/agent/tools/shell.py:200](). This prevents path traversal attacks.
-   **Internal URL Blocking**: The tool actively guards against attempts to access internal/private network resources (e.g., cloud metadata services, localhost) via `curl`, `wget`, or similar tools, unless explicitly allowed by the workspace scope [tests/tools/test_exec_security.py:32-40]().
-   **Sensitive File Protection**: It prevents writing to nanobot's internal state files (e.g., `history.jsonl`, `SOUL.md`) [tests/tools/test_exec_security.py:176-186]().

### Process Tree Management and Cleanup

For one-shot commands, `ExecTool` ensures proper process termination and cleanup:
-   **Timeout Handling**: If a command exceeds its `timeout`, the entire process tree is terminated [tests/tools/test_shell_reap.py:119-136]().
-   **Cancellation Handling**: If the agent loop is cancelled, the running command's process tree is also terminated [tests/tools/test_shell_reap.py:139-155]().
-   **Zombie Process Prevention**: After a process completes (either normally or due to termination/timeout), `_reap_pid` [nanobot/agent/tools/shell.py:60-82]() is called to perform a best-effort `waitpid` to prevent zombie processes [tests/tools/test_shell_reap.py:99-116]().

#### Windows Job Objects

On Windows, nanobot uses Job Objects to manage process trees. When `process_tree=True` is set for a subprocess, a `WindowsJob` [nanobot/agent/tools/_windows_job.py:150-152]() is created. This Job Object is configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` [nanobot/agent/tools/_windows_job.py:13-14](), ensuring that all processes associated with the job are terminated when the job handle is closed. This is crucial for reliably cleaning up child processes, even if the direct parent process exits [nanobot/agent/tools/_windows_job.py:108-119]().

The process is initially created in a suspended state (`_CREATE_SUSPENDED`) [nanobot/agent/tools/_windows_job.py:8](), assigned to the Job Object, and then resumed. This atomic operation guarantees that the process is under the Job Object's control before it can spawn its own children [nanobot/agent/tools/_windows_job.py:170-186]().

```mermaid
graph TD
    A[ExecTool.execute()] --> B{Is Windows?};
    B -- Yes --> C[Create WindowsJob];
    C --> D[Call asyncio.create_subprocess_exec with CREATE_SUSPENDED];
    D --> E[Assign process to Job Object];
    E --> F[Resume primary thread];
    B -- No --> G[Call asyncio.create_subprocess_exec with start_new_session];
    F --> H[Monitor process output];
    G --> H;
    H --> I{Process completes or times out/cancelled?};
    I -- Yes --> J[Terminate Job Object (Windows) or Process Group (Unix)];
    J --> K[_reap_pid()];
    K --> L[Return ToolResult];
```
**Diagram: ExecTool Process Management Flow**
Sources:
- [nanobot/agent/tools/shell.py:162-163]()
- [nanobot/agent/tools/shell.py:34-35]()
- [nanobot/agent/tools/shell.py:60-82]()
- [nanobot/agent/tools/_windows_job.py:150-152]()
- [nanobot/agent/tools/_windows_job.py:13-14]()
- [nanobot/agent/tools/_windows_job.py:108-119]()
- [nanobot/agent/tools/_windows_job.py:8]()
- [nanobot/agent/tools/_windows_job.py:170-186]()
- [tests/tools/test_shell_reap.py:119-136]()
- [tests/tools/test_shell_reap.py:139-155]()
- [tests/tools/test_shell_reap.py:99-116]()

## ExecSessionManager: Interactive Shell Sessions

For long-running or interactive shell commands, nanobot provides `ExecSessionManager` [nanobot/agent/tools/exec_session.py:19]() and associated tools: `ExecSessionTool` [nanobot/agent/tools/exec_session.py:20]() and `ListExecSessionsTool` [nanobot/agent/tools/exec_session.py:21](). These enable the agent to start a process, interact with its stdin/stdout/stderr over multiple turns, and manage its lifecycle.

### `yield_time_ms` and Session Polling

The key feature enabling interactive sessions is the `yield_time_ms` parameter in `ExecTool` [nanobot/agent/tools/shell.py:142-146]().
-   When `yield_time_ms` is provided (e.g., `yield_time_ms=1000`), `ExecTool` will start a process and return control to the agent after the specified milliseconds, even if the process is still running. The output collected so far is returned, along with a `session_id`.
-   If `yield_time_ms` is omitted, `ExecTool` behaves like a one-shot command, waiting for the process to complete [tests/tools/test_exec_keeps_one_shot_behavior_without_yield_time_ms]().

The `ExecSessionManager` [nanobot/agent/tools/exec_session.py:660-752]() is responsible for:
-   **Creating and Tracking Sessions**: It maintains a dictionary of active `_ExecSession` [nanobot/agent/tools/exec_session.py:117-134]() objects, keyed by `session_id`.
-   **Polling Output**: The `_ExecSession.poll()` method [nanobot/agent/tools/exec_session.py:184-204]() is called periodically to check for new output from the subprocess's stdout and stderr streams.
-   **Timeout Management**: Each session has a `deadline` [nanobot/agent/tools/exec_session.py:137]() after which it will be terminated if still running.
-   **Output Buffering**: `_BoundedOutputBuffer` [nanobot/agent/tools/exec_session.py:57-115]() is used to store process output, ensuring that only a configurable `max_output_chars` [nanobot/agent/tools/exec_session.py:28-29]() are retained (keeping head and tail, dropping middle if necessary) [tests/tools/test_bounded_output_buffer_keeps_head_tail_and_exact_drop_count](). This prevents excessive memory usage for verbose commands.
-   **Session Cleanup**: Sessions are automatically terminated if they exceed their timeout or if the owning agent session is closed.

### Interacting with Sessions

The `ExecSessionTool` [nanobot/agent/tools/exec_session.py:600-658]() allows the agent to interact with an active session:
-   `session_id`: Identifies the target session.
-   `input`: Sends text to the session's stdin.
-   `close_stdin`: Closes the session's stdin.
-   `terminate`: Terminates the session's process tree.
-   `yield_time_ms`: Specifies how long to wait for new output before returning.
-   `max_output_chars`: Limits the amount of output returned in a single poll.

The `ListExecSessionsTool` [nanobot/agent/tools/exec_session.py:570-598]() provides a way to inspect currently active sessions, showing their `session_id`, command, working directory, elapsed time, and return code.

```mermaid
graph TD
    A[Agent calls exec tool with yield_time_ms] --> B{ExecTool.execute()};
    B --> C[ExecSessionManager.start_session()];
    C --> D[Create _ExecSession object];
    D --> E[Spawn subprocess (suspended on Windows)];
    E --> F[Assign to Job Object (Windows) / Process Group (Unix)];
    F --> G[Resume process (Windows)];
    G --> H[Start async tasks to read stdout/stderr];
    H --> I[Return session_id and initial output];

    J[Agent calls exec_session tool with session_id] --> K{ExecSessionManager.poll_session()};
    K --> L[Send input to stdin (if any)];
    L --> M[Wait for yield_time_ms or process exit];
    M --> N[Collect output from _BoundedOutputBuffer];
    N --> O[Return new output, done status, exit code];

    P[Agent calls exec_session tool with terminate=true] --> Q{ExecSessionManager.terminate_session()};
    Q --> R[Kill process tree];
    R --> S[Remove session from manager];

    subgraph _ExecSession
        D -- owns --> H;
        H -- writes to --> T[_BoundedOutputBuffer];
        T -- read by --> N;
    end
```
**Diagram: Exec Session Lifecycle**
Sources:
- [nanobot/agent/tools/shell.py:142-146]()
- [nanobot/agent/tools/exec_session.py:19]()
- [nanobot/agent/tools/exec_session.py:20]()
- [nanobot/agent/tools/exec_session.py:21]()
- [nanobot/agent/tools/exec_session.py:660-752]()
- [nanobot/agent/tools/exec_session.py:117-134]()
- [nanobot/agent/tools/exec_session.py:184-204]()
- [nanobot/agent/tools/exec_session.py:137]()
- [nanobot/agent/tools/exec_session.py:57-115]()
- [nanobot/agent/tools/exec_session.py:28-29]()
- [nanobot/agent/tools/exec_session.py:600-658]()
- [nanobot/agent/tools/exec_session.py:570-598]()
- [tests/tools/test_exec_keeps_one_shot_behavior_without_yield_time_ms]()
- [tests/tools/test_bounded_output_buffer_keeps_head_tail_and_exact_drop_count]()

## Bridging Natural Language to Code Entities

The following diagram illustrates how natural language requests for shell execution are translated into calls to the `ExecTool` and `ExecSessionTool` within the nanobot codebase.

```mermaid
graph TD
    NL[Natural Language Request: "Run a command" or "Interact with a shell"] --> AgentLoop;
    AgentLoop --> ToolRegistry;
    ToolRegistry -- "exec" --> ExecTool;
    ToolRegistry -- "exec_session" --> ExecSessionTool;
    ToolRegistry -- "list_exec_sessions" --> ListExecSessionsTool;

    ExecTool -- "command, working_dir, timeout, yield_time_ms" --> ExecTool.execute();
    ExecTool.execute() -- "Starts new process" --> _ExecSession;
    _ExecSession -- "Manages process lifecycle" --> ExecSessionManager;
    ExecSessionManager -- "Stores active sessions" --> ExecSessionManager._sessions;

    ExecSessionTool -- "session_id, input, yield_time_ms, terminate" --> ExecSessionTool.execute();
    ExecSessionTool.execute() -- "Interacts with existing session" --> ExecSessionManager;

    ListExecSessionsTool -- "No parameters" --> ListExecSessionsTool.execute();
    ListExecSessionsTool.execute() -- "Retrieves session info" --> ExecSessionManager;

    ExecTool.execute() -- "Returns ToolResult" --> AgentLoop;
    ExecSessionTool.execute() -- "Returns ToolResult" --> AgentLoop;
    ListExecSessionsTool.execute() -- "Returns ToolResult" --> AgentLoop;

    subgraph nanobot/agent/tools/shell.py
        ExecTool;
        ExecTool.execute();
        ExecToolConfig;
        _PreparedCommand;
        _ProcessTreeOwner;
        _reap_pid;
    end

    subgraph nanobot/agent/tools/exec_session.py
        ExecSessionManager;
        ExecSessionManager._sessions;
        ExecSessionTool;
        ListExecSessionsTool;
        _ExecSession;
        _BoundedOutputBuffer;
        _SessionPoll;
        ExecSessionInfo;
    end

    subgraph nanobot/agent/tools/_windows_job.py
        WindowsJob;
    end
```
**Diagram: Natural Language to Shell Execution Code Flow**
Sources:
- [nanobot/agent/tools/shell.py:162-163]()
- [nanobot/agent/tools/shell.py:94-105]()
- [nanobot/agent/tools/shell.py:108-116]()
- [nanobot/agent/tools/shell.py:49-57]()
- [nanobot/agent/tools/shell.py:60-82]()
- [nanobot/agent/tools/exec_session.py:19]()
- [nanobot/agent/tools/exec_session.py:20]()
- [nanobot/agent/tools/exec_session.py:21]()
- [nanobot/agent/tools/exec_session.py:117-134]()
- [nanobot/agent/tools/exec_session.py:57-115]()
- [nanobot/agent/tools/exec_session.py:33-42]()
- [nanobot/agent/tools/exec_session.py:46-55]()
- [nanobot/agent/tools/_windows_job.py:150-152]()
- [nanobot/agent/loop.py]() (conceptual)
- [nanobot/agent/tools/registry.py]() (conceptual)

## Key Classes and Functions

| Class/Function | File | Description |
|---|---|---|
| `ExecTool` | [nanobot/agent/tools/shell.py:162-163]() | Main tool for executing shell commands. Handles one-shot execution and initiates sessions. |
| `ExecToolConfig` | [nanobot/agent/tools/shell.py:94-105]() | Pydantic model for configuring `ExecTool` behavior, including timeouts, paths, and security patterns. |
| `ExecSessionManager` | [nanobot/agent/tools/exec_session.py:660-752]() | Manages the lifecycle of all active shell sessions. |
| `_ExecSession` | [nanobot/agent/tools/exec_session.py:117-134]() | Represents a single long-running shell process, managing its I/O, state, and tasks. |
| `ExecSessionTool` | [nanobot/agent/tools/exec_session.py:600-658]() | Tool for interacting with an existing shell session (sending input, polling output, terminating). |
| `ListExecSessionsTool` | [nanobot/agent/tools/exec_session.py:570-598]() | Tool to list all active shell sessions. |
| `_BoundedOutputBuffer` | [nanobot/agent/tools/exec_session.py:57-115]() | Efficiently stores and retrieves process output, truncating in the middle to respect `max_output_chars`. |
| `_reap_pid` | [nanobot/agent/tools/shell.py:60-82]() | Best-effort function to `waitpid` on child processes to prevent zombies. |
| `WindowsJob` | [nanobot/agent/tools/_windows_job.py:150-152]() | Windows-specific class to create and manage Job Objects for process tree cleanup. |
| `_guard_command` | [nanobot/agent/tools/shell.py:300-301]() | Internal method in `ExecTool` that applies allow/deny patterns and workspace/network access checks. |
| `_spawn` | [nanobot/agent/tools/shell.py:400-401]() | Internal method to create the subprocess, handling platform-specific details like `start_new_session` or `WindowsJob` creation. |

Sources:
- [nanobot/agent/tools/shell.py:162-163]()
- [nanobot/agent/tools/shell.py:94-105]()
- [nanobot/agent/tools/exec_session.py:660-752]()
- [nanobot/agent/tools/exec_session.py:117-134]()
- [nanobot/agent/tools/exec_session.py:600-658]()
- [nanobot/agent/tools/exec_session.py:570-598]()
- [nanobot/agent/tools/exec_session.py:57-115]()
- [nanobot/agent/tools/shell.py:60-82]()
- [nanobot/agent/tools/_windows_job.py:150-152]()
- [nanobot/agent/tools/shell.py:300-301]()
- [nanobot/agent/tools/shell.py:400-401]()

---

