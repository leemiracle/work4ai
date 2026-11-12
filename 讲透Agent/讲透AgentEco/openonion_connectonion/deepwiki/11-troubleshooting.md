<!-- source: DeepWiki mcp.deepwiki.com · repo openonion/connectonion · page 11 Troubleshooting · fetched 2026-10-27 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [connectonion/console.py](connectonion/console.py)
- [docs/debug/xray.md](docs/debug/xray.md)
- [tests/unit/test_address.py](tests/unit/test_address.py)
- [tests/unit/test_console.py](tests/unit/test_console.py)

</details>



This document provides high-level guidance for diagnosing and resolving issues in ConnectOnion. It serves as a central hub for debugging strategies, linking to detailed child pages for specific error categories.

## Diagnostic Workflow

When an agent fails or behaves unexpectedly, follow this systematic diagnostic path to isolate the root cause:

```mermaid
graph TD
    ["Issue Encountered"] --> ["Check Console Output"]
    ["Check Console Output"] --> ["Review .co/logs/"]
    
    subgraph "Code Entity Space"
        ["Review .co/logs/"] -- "Managed by" --> [connectonion_console.py]
        [connectonion_console.py] -- "Writes to" --> [agent_log_file]
    end

    ["Review .co/logs/"] --> ErrorType{"Error Type?"}
    
    ErrorType -- "API/Keys" --> ["Authentication Problems"]
    ErrorType -- "Crashes/Exceptions" --> ["Common Errors"]
    ErrorType -- "Slowness/Timeouts" --> ["Performance Issues"]
    
    ["Authentication Problems"] --> ChildAuth[Authentication Problems](#11.3)"]
    ["Common Errors"] --> ChildErrors[Common Errors](#11.1)"]
    ["Performance Issues"] --> ChildPerf[Performance Issues](#11.2)"]
```

**Sources:** [connectonion/console.py:75-96](), [connectonion/console.py:181-193]()

---

## Debugging Tools & Strategies

ConnectOnion provides several built-in mechanisms to inspect agent behavior in real-time.

### 1. Console & Logging
The `Console` class in `connectonion/console.py` handles all terminal output and session logging. By default, logs are written to `.co/logs/` in plain text with timestamps, while the terminal uses Rich formatting to distinguish between LLM "thinking" and tool "actions".

*   **LLM Thinking:** Marked with `○` (request) and `●` (response) symbols [connectonion/console.py:29-30]().
*   **Tool Execution:** Marked with `▸` (start) and `✓` or `✗` (result) symbols [connectonion/console.py:33-36]().

### 2. Interactive Debugging with `@xray`
The `@xray` decorator allows you to pause execution and inspect the agent's internal state (messages, task, iteration count) from within a tool. This is the primary method for understanding *why* an agent made a specific decision.

```python
@xray
def my_tool(arg: str):
    # Access agent context during execution
    print(xray.task)
    print(xray.iteration)
    xray.trace() # Print visual execution trace
```

**Sources:** [docs/debug/xray.md:10-34](), [docs/debug/xray.md:59-70]()

---

## Common Issue Categories

### Common Errors
This category covers Python exceptions, missing dependencies (like `playwright`), and configuration mismatches. If your agent crashes with a traceback, start here.
For details, see [Common Errors](#11.1).

### Performance Issues
Agents may become slow due to large context windows, high tool counts, or network latency. This section covers model selection trade-offs and iteration limits.
For details, see [Performance Issues](#11.2).

### Authentication Problems
Covers issues with OpenOnion managed keys, local `.env` files, and OAuth flows for integrations like Gmail.
For details, see [Authentication Problems](#11.3).

---

## Code-to-System Mapping

The following diagram maps common troubleshooting scenarios to the specific code entities responsible for handling them.

```mermaid
graph LR
    subgraph "System Issues"
        A["API Key Missing"]
        B["Tool Exception"]
        C["Slow Execution"]
    end

    subgraph "Code Entities"
        [auth_commands.py]
        [console.py]
        [address.py]
        [xray.md]
    end

    A -- "Managed by" --> [auth_commands.py]
    B -- "Logged by" --> [console.py]
    B -- "Inspected via" --> [xray.md]
    C -- "Traced by" --> [console.py]
    A -- "Identity from" --> [address.py]
```

**Sources:** [connectonion/console.py:68-81](), [connectonion/address.py:14-30](), [docs/debug/xray.md:1-20]()

---

