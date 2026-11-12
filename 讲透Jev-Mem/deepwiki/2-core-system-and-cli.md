<!-- source: DeepWiki mcp.deepwiki.com · repo libingzheren/Jev-Mem · page 2 Core System and CLI · fetched 2026-10-13 -->

# Core System and CLI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jev_mem/__init__.py](jev_mem/__init__.py)
- [jev_mem/__main__.py](jev_mem/__main__.py)
- [jev_mem/system.py](jev_mem/system.py)

</details>



This page provides a high-level overview of the core `jev_mem` package, which orchestrates the Jev-Mem system's memory building and querying capabilities. It introduces the main entry points for interacting with the system, including the `JevMemSystem` orchestrator and the Command-Line Interface (CLI). For detailed information on each component, refer to the linked child pages.

## JevMemSystem Orchestrator

The `JevMemSystem` class [jev_mem/system.py:10-73]() serves as the primary orchestrator for Jev-Mem. It integrates various components such as the `MemoryBuilder` [jev_mem/system.py:16-17](), `QueryEngine` [jev_mem/system.py:22-23](), and `JevMemConfig` [jev_mem/system.py:15]() to manage the entire memory lifecycle, from building memory from raw observations to querying it.

The `JevMemSystem` handles the initialization of core memory components like the `TRGMemory` [jev_mem/system.py:18](), `GraphDB` [jev_mem/system.py:19](), and `VectorDB` [jev_mem/system.py:20](). It exposes methods for `build_memory_from_conversation` [jev_mem/system.py:25-53]() to ingest data, `query` [jev_mem/system.py:55-61]() to retrieve information, and `save_memory`/`load_memory` [jev_mem/system.py:63-72]() for persistence.

For details on the `JevMemSystem`'s internal workings, its configuration, and how it wires together the various clients and engines, see [JevMemSystem Orchestrator](#2.1).

### JevMemSystem Component Diagram

```mermaid
graph TD
    subgraph "JevMemSystem"
        JevMemSystem["jev_mem.system.JevMemSystem"]
        MemoryBuilder["memory.memory_builder.MemoryBuilder"]
        QueryEngine["memory.query_engine.QueryEngine"]
        JevMemConfig["memory.jev_mem_config.JevMemConfig"]
        TRGMemory["memory.trg_memory.TRGMemory"]
        GraphDB["memory.graph_db.GraphDB"]
        VectorDB["memory.vector_db.VectorDB"]
        LLMController["controller.llm_controller.LLMController"]
        AnswerFormatter["memory.answer_formatter.AnswerFormatter"]
        JevClient["controller.jev_client.JevClient"]

        JevMemSystem --> MemoryBuilder
        JevMemSystem --> QueryEngine
        JevMemSystem --> JevMemConfig
        MemoryBuilder --> TRGMemory
        MemoryBuilder --> LLMController
        MemoryBuilder --> AnswerFormatter
        MemoryBuilder --> JevClient
        TRGMemory --> GraphDB
        TRGMemory --> VectorDB
        QueryEngine --> TRGMemory
        QueryEngine --> JevClient
    end
```
Sources:
- [jev_mem/system.py:10-73]()
- [jev_mem/system.py:16-17]()
- [jev_mem/system.py:22-23]()
- [jev_mem/system.py:15]()
- [jev_mem/system.py:18]()
- [jev_mem/system.py:19]()
- [jev_mem/system.py:20]()
- [jev_mem/system.py:25-53]()
- [jev_mem/system.py:55-61]()
- [jev_mem/system.py:63-72]()

## Command-Line Interface

The `jev_mem` package provides a command-line interface (CLI) for direct interaction with the Jev-Mem system. This allows users to build memory from various data sources and query the memory without writing Python code. The CLI is implemented in `jev_mem/cli.py` and is the entry point when running `python -m jev_mem` [jev_mem/__main__.py:1-5]().

The CLI supports different modes of operation, such as building memory from conversation data and querying the built memory. It also incorporates ablation flags, which are useful for experimentation and understanding the impact of different system components.

For a comprehensive guide on using the CLI, including available commands, arguments, and ablation flags, see [Command-Line Interface](#2.2).

### CLI Entry Point Diagram

```mermaid
graph TD
    User["User"] --> "python -m jev_mem"
    "python -m jev_mem" --> MainModule["jev_mem/__main__.py"]
    MainModule --> CLI_Main["jev_mem/cli.py::main()"]
    CLI_Main --> JevMemSystem["jev_mem.system.JevMemSystem"]
    JevMemSystem -- "build_memory_from_conversation()" --> MemoryBuilder["memory.memory_builder.MemoryBuilder"]
    JevMemSystem -- "query()" --> QueryEngine["memory.query_engine.QueryEngine"]
```
Sources:
- [jev_mem/__main__.py:1-5]()
- [jev_mem/cli.py]()
- [jev_mem/system.py]()

## Module Entrypoints

The `jev_mem` package exposes key components directly through its `__init__.py` [jev_mem/__init__.py:1-20]() file, allowing for lazy loading of modules to avoid unnecessary initialization of model providers. The `__all__` variable [jev_mem/__init__.py:5]() lists the publicly available classes: `JevMemSystem`, `JevMemConfig`, `MemoryBuilder`, and `QueryEngine`. These can be imported directly from the `jev_mem` package, for example, `from jev_mem import JevMemSystem`.

This lazy loading mechanism [jev_mem/__init__.py:15-20]() ensures that resource-intensive components are only loaded when explicitly accessed, optimizing startup time and resource usage.

Sources:
- [jev_mem/__init__.py:1-20]()
- [jev_mem/__init__.py:5]()
- [jev_mem/__init__.py:15-20]()

---

