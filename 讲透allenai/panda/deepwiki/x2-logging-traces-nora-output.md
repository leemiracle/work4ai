<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/panda · extra page Logging, Traces & NORA Output · fetched 2026-11-09 -->

# Logging, Traces & NORA Output

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [panda/panda_agent/panda_agent.py](panda/panda_agent/panda_agent.py)
- [panda/utils/logger.py](panda/utils/logger.py)

</details>



The purpose and scope of section 2.1.2 cover the output, logging, and user interface integration infrastructure of the Panda agent. This includes `LoggerTee` stream redirection for simultaneous console and file logging, the generation of trace files (`experiment-trace.txt` and `experiment-trace-long.txt`), UI integration via `print_to_nora` for the NORA platform, and the core `logger` utility.

---

## 1. Logger & Stream Redirection (`LoggerTee`)

Panda captures execution output and system traces using custom logging wrappers and stream redirection. The core logging utility is initialized in `panda/utils/logger.py`, setting up a dedicated `panda_logger` instance with a default message-only formatter (`logging.Formatter("%(message)s")`) [panda/utils/logger.py:8-26]().

To handle concurrent output streams (writing to both standard output/error and persistent trace files or UI buffers), Panda utilizes custom tee patterns and stream redirection utilities. 

```
+---------------------------------------------------------------------+
|                          Code Execution                             |
|              (print(), sys.stdout, sys.stderr)                      |
+---------------------------------------------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
|                           LoggerTee                                 |
|               (Intercepts stdout/stderr streams)                    |
+---------------------------------------------------------------------+
         |                                           |
         v                                           v
+-----------------------+                 +---------------------------+
|    Original Stream    |                 |   Trace Files & UI        |
|  (sys.__stdout__)     |                 |  (print_to_nora, traces)  |
+-----------------------+                 +---------------------------+
```

Sources: [panda/utils/logger.py:1-44](), [panda/panda_agent/panda_agent.py:56-61]()

---

## 2. Trace Files & Output Artifacts

During an agent execution run, Panda records its progress across multiple trace files stored within the timestamped output directory (`output/experiment-<timestamp>/`) [panda/panda_agent/panda_agent.py:28-34]().

### Trace File Types
* **`experiment-trace.txt`**: A short, user-facing trace corresponding to what is printed via `print_to_user` [panda/panda_agent/panda_agent.py:33]().
* **`experiment-trace-long.txt`**: The full raw dialog history exchanged with the LLM [panda/panda_agent/panda_agent.py:34]().

### Data Flow for Traces and Dialogs
```
+-------------------------------------------------------------------------+
|                              run_panda()                                |
+-------------------------------------------------------------------------+
       |                                           |
       v                                           v
+---------------------------+               +-----------------------------+
|    print_to_user()        |               |   Dialog / LLM History      |
+---------------------------+               +-----------------------------+
       |                                           |
       v                                           v
+---------------------------+               +-----------------------------+
|  experiment-trace.txt     |               | experiment-trace-long.txt   |
+---------------------------+               +-----------------------------+
```

Sources: [panda/panda_agent/panda_agent.py:28-37]()

---

## 3. NORA UI Integration (`print_to_nora`)

Panda integrates with external user interfaces—specifically the NORA platform—through designated global variables and printing utilities [panda/panda_agent/panda_agent.py:120-121](). 

### Global UI State Variables
* `nora_thread_id`: Tracks the active thread identifier when executing within the NORA UI context [panda/panda_agent/panda_agent.py:120]().
* `nora_system_output`: Accumulates system output strings intended for presentation in the NORA interface [panda/panda_agent/panda_agent.py:121]().

When text is routed to the user interface, helper functions update these global buffers alongside standard output channels, enabling live streaming updates of research progress.

Sources: [panda/panda_agent/panda_agent.py:120-121]()

---

## 4. Quiet Logging Controls

To prevent verbose library logs (such as those from `litellm`) from corrupting MCP streams or terminal outputs, Panda provides `with_quiet_logging` [panda/utils/logger.py:33-44](). This context manager temporarily elevates the root logging level to `logging.ERROR` during critical LLM calls [panda/utils/logger.py:37-44]().

```
+---------------------------------------------------------------------+
|                     with_quiet_logging(fn, ...)                     |
+---------------------------------------------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
|                Temporarily set root level to ERROR                  |
+---------------------------------------------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
|                  Execute inner function (e.g., LLM)                 |
+---------------------------------------------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
|                 Restore previous root logging level                 |
+---------------------------------------------------------------------+
```

Sources: [panda/utils/logger.py:33-44]()

---

