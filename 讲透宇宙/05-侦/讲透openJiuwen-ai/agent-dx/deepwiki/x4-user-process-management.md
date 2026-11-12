<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-dx · extra page User Process Management · fetched 2026-11-02 -->

# User Process Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [executor/src/yr/agentexecutor/process_manager.py](executor/src/yr/agentexecutor/process_manager.py)
- [tests/executor/test_process_manager.py](tests/executor/test_process_manager.py)

</details>



## Purpose and Scope

The User Process Management subsystem (implemented in `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:1-167]()) is responsible for bootstrapping, monitoring, logging, and cleanly shutting down user-defined agent processes inside an Agent instance. It parses execution parameters from environment variables, spawns independent process groups, aggregates standard output and error streams into a unified traversal-safe `.std` log file, and enforces graceful termination sequences using `SIGTERM` followed by `SIGKILL`.

Sources: `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:1-167]()

---

## Environment Variables and Bootstrap Configuration

The `ProcessManager` relies on several environment variables configured in the execution container runtime to determine which commands to run, where to store logs, and how to tag diagnostic output.

| Environment Variable | Constant Name | Default Value | Description |
|---|---|---|---|
| `YR_RUNTIME_BOOTSTRAP_CMD` | `BOOTSTRAP_COMMAND_ENV` | `""` | JSON-encoded array of command argument lists to execute. |
| `GLOG_log_dir` | `PROCESS_LOG_DIR_ENV` | `/home/snuser/log/` | Directory path where unified `.std` runtime log files are written. |
| `YR_RUNTIME_ID` | `RUNTIME_ID_ENV` | `""` | Unique identifier for the runtime instance, used to name log files. |
| `YR_TRACE_ID` | `TRACE_ID_ENV` | `""` | Optional trace identifier included in audit and startup logs. |
| `INSTANCE_ID` | `INSTANCE_ID_ENV` | `""` | Optional instance identifier included in startup logs. |

Sources: `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:34-40]()

---

## Bootstrap Command Parsing

The `parse_bootstrap_commands(value: str)` function processes raw environment strings containing JSON arrays of argument vectors (`argv`). 

### Parsing Logic and Validation Rules
1. **JSON Decoding**: The input string is passed to `json.loads(value)` [executor/src/yr/agentexecutor/process_manager.py:56](). Non-JSON values or non-list payloads generate a warning and return an empty list [executor/src/yr/agentexecutor/process_manager.py:57-62]().
2. **Command Limit Enforcement**: If the parsed list contains more than `MAX_BOOTSTRAP_COMMANDS` (64) entries, it is truncated, and a warning is emitted [executor/src/yr/agentexecutor/process_manager.py:40,63-70]().
3. **Type Checking**: Each entry in the command array must be a non-empty list consisting exclusively of string arguments [executor/src/yr/agentexecutor/process_manager.py:72-76](). Invalid entries are skipped individually without invalidating the entire batch.

```mermaid
title "Bootstrap Command Parsing Flow"
graph TD
    A["parse_bootstrap_commands(value)"] --> B{"Is value empty?"}
    B -- Yes --> C["Return empty list []"]
    B -- No --> D["json.loads(value)"]
    D -- "ValueError / TypeError" --> E["Log warning, return []"]
    D -- "Valid JSON" --> F{"Is instance list?"}
    F -- No --> G["Log warning, return []"]
    F -- Yes --> H{"len > MAX_BOOTSTRAP_COMMANDS"}
    H -- Yes --> I["Truncate to 64 commands"]
    H -- No --> J["Iterate commands"]
    I --> J
    J --> K{"Valid argv list of strings?"}
    K -- No --> L["Skip invalid command index"]
    K -- Yes --> M["Append to validated list"]
    M --> N["Return validated list"]
    L --> N
```

Sources: `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:51-77](), `tests/executor/test_process_manager.py` [tests/executor/test_process_manager.py:12-40]()

---

## Process Spawning and Unified Logging

The `ProcessManager` class manages the lifecycle of spawned commands. The method `start_from_env(environ)` reads active environment configurations and delegates to `start(commands, log_dir, runtime_id)` [executor/src/yr/agentexecutor/process_manager.py:90-97]().

### Log File Path Sanitization
Log files are consolidated per runtime instance into a single `.std` file. The helper function `_runtime_log_file(log_dir, runtime_id)` sanitizes the `runtime_id` to prevent directory traversal attacks:
- Characters outside of `[A-Za-z0-9._-]` are substituted with underscores (`_`) [executor/src/yr/agentexecutor/process_manager.py:45]().
- Blank or traversal-only names (`.`, `..`) fallback to `unknown-runtime` [executor/src/yr/agentexecutor/process_manager.py:46-47]().
- The resulting filename format is `<sanitized_runtime_id>.std` [executor/src/yr/agentexecutor/process_manager.py:48]().

### Process Group Creation and Stream Merging
When `ProcessManager.start(...)` executes:
1. It acquires an internal `threading.Lock()` to protect process state [executor/src/yr/agentexecutor/process_manager.py:101]().
2. It opens the unified log file with binary append mode (`ab`) and unbuffered output (`buffering=0`) [executor/src/yr/agentexecutor/process_manager.py:108]().
3. For each command, it spawns a subprocess via `subprocess.Popen` with:
   - `stdin=subprocess.DEVNULL` [executor/src/yr/agentexecutor/process_manager.py:117]()
   - `stdout=log_file` (merging stdout and stderr to the same file descriptor) [executor/src/yr/agentexecutor/process_manager.py:118]()
   - `stderr=subprocess.STDOUT` [executor/src/yr/agentexecutor/process_manager.py:119]()
   - `start_new_session=True` to create a distinct POSIX process group for clean signal propagation [executor/src/yr/agentexecutor/process_manager.py:120]().

```mermaid
title "Process Initialization and Logging Architecture"
graph TD
    A["ProcessManager.start_from_env()"] --> B["ProcessManager.start()"]
    B --> C["_runtime_log_file(log_dir, runtime_id)"]
    C --> D["Sanitize runtime_id and resolve Path"]
    D --> E["Open .std log file (ab, unbuffered)"]
    B --> F["Loop over validated commands"]
    F --> G["subprocess.Popen(start_new_session=True)"]
    G --> H["Redirect stdout & stderr to .std"]
    G --> I["Record subprocess.Popen handle"]
    I --> J["Log startup (pid, bootstrap_index, trace_id, instance_id)"]
```

Sources: `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:43-137](), `tests/executor/test_process_manager.py` [tests/executor/test_process_manager.py:53-155]()

---

## Shutdown Procedure and Graceful Termination

To tear down user processes, `ProcessManager.stop(grace_period_seconds)` invokes `_stop_locked(grace_period_seconds)` under thread synchronization [executor/src/yr/agentexecutor/process_manager.py:145-149]().

### Shutdown Sequence
1. **SIGTERM Broadcast**: All active processes (those where `process.poll() is None`) receive a `signal.SIGTERM` signal targeted at their independent process group (`_signal_process_group`) [executor/src/yr/agentexecutor/process_manager.py:150-152]().
2. **Grace Period Wait**: The manager waits up to `grace_period_seconds` for processes to exit using `process.wait(timeout=remaining)` [executor/src/yr/agentexecutor/process_manager.py:154-162]().
3. **SIGKILL Escalation**: Any processes remaining active after the deadline expire are forcibly terminated by sending `signal.SIGKILL` to their process group [executor/src/yr/agentexecutor/process_manager.py:164-166]().

Sources: `executor/src/yr/agentexecutor/process_manager.py` [executor/src/yr/agentexecutor/process_manager.py:145-167]()

---

