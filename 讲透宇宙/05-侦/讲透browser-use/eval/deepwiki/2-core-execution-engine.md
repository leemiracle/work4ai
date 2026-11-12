<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/eval · page 2 Core Execution Engine · fetched 2026-10-30 -->

# Core Execution Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [run_browser_use.py](run_browser_use.py)

</details>



The Core Execution Engine is the primary orchestration system that manages the end-to-end execution of browser automation tasks. It coordinates task loading, concurrent browser instance management, LLM provider integration, agent execution, and result evaluation to process hundreds of web navigation tasks efficiently.

This document covers the main task execution pipeline and coordination logic. For browser agent integration details, see [Browser Agent Integration](#2.1). For concurrent task management specifics, see [Concurrent Task Management](#2.2). For evaluation system details, see [Evaluation System](#3).

## System Overview

The execution engine operates as an asynchronous task orchestrator that processes WebVoyager evaluation tasks through a multi-stage pipeline:

```mermaid
graph TB
    subgraph "Initialization"
        A[main] --> B[cleanup_webdriver_cache]
        A --> C["Load WebVoyager_data.jsonl"]
        A --> D["Filter impossible tasks"]
        A --> E["Initialize RunStats & ExperimentResults"]
    end
    
    subgraph "Task Processing Loop"
        F[process_with_semaphore] --> G["Create Browser instance"]
        G --> H[process_single_task]
        H --> I["Initialize Agent with task + LLM"]
        I --> J["agent.run(max_steps=30)"]
        J --> K[auto_eval_by_gpt4o]
        K --> L[save_results]
    end
    
    subgraph "LLM Management"
        M[get_llm_model_generator] --> N["Azure OpenAI instances"]
        M --> O["Anthropic Claude"]
        M --> P["Google Gemini models"]
    end
    
    subgraph "Results & Statistics"
        Q[RunStats] --> R["Track success/failed/unknown"]
        S[ExperimentResults] --> T["Aggregate task results"]
        L --> Q
        L --> S
    end
    
    E --> F
    M --> I
    
    style A fill:#e1f5fe,stroke:#1976d2,stroke-width:2px
    style H fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style M fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Sources**: [run_browser_use.py:313-434]()

## Core Data Models

The execution engine uses several key data structures to manage task processing:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `TaskData` | WebVoyager task definition | `id`, `web`, `ques` |
| `TaskResult` | Individual task execution results | `task_id`, `success`, `duration_seconds`, `num_steps` |
| `ExperimentResults` | Aggregate experiment statistics | `total_tasks`, `total_success`, `all_tasks` |
| `RunStats` | Real-time execution tracking | `successful_tasks`, `failed_tasks`, `current_task` |
| `LLMModel` | LLM provider configuration | `model`, `token_limit` |

**Sources**: [run_browser_use.py:27-88]()

## Task Execution Pipeline

### Task Loading and Filtering

The engine begins by loading task definitions from the WebVoyager dataset and applying filtering rules:

```mermaid
sequenceDiagram
    participant Main as main()
    participant Data as WebVoyager_data.jsonl
    participant Filter as WebVoyagerImpossibleTasks.json
    participant Tasks as Filtered Task List
    
    Main->>Data: "Load tasks with json.loads(line)"
    Data->>Main: "List[TaskData] (812 tasks)"
    Main->>Filter: "Load impossible task IDs"
    Filter->>Main: "Set[str] (54 task IDs)"
    Main->>Tasks: "Filter tasks not in impossible_tasks"
    Main->>Tasks: "random.shuffle with seed=42"
    Tasks->>Main: "Randomized filtered task list"
```

**Sources**: [run_browser_use.py:319-332]()

### LLM Provider Factory

The `get_llm_model_generator` function implements a factory pattern that yields fresh LLM instances for each task, supporting multiple providers with different configurations:

```mermaid
graph TB
    subgraph "LLM Provider Factory"
        A[get_llm_model_generator] --> B{"model_provider"}
        
        B -->|"azure"| C["West EU: 900 tokens"]
        B -->|"azure"| D["East US: 450 tokens"] 
        B -->|"azure"| E["East US 2: 450 tokens"]
        B -->|"azure"| F["West US: 450 tokens"]
        
        B -->|"anthropic"| G["claude-3-5-sonnet-20240620"]
        
        B -->|"google/gemini-1.5-flash"| H["gemini-1.5-flash"]
        B -->|"google/gemini-1.5-pro"| I["gemini-1.5-pro"]
        B -->|"google/gemini-1.5-flash-8b"| J["gemini-1.5-flash-8b"]
    end
    
    subgraph "Model Instance Creation"
        K[AzureChatOpenAI] --> L["api_version: 2024-10-21"]
        M[ChatAnthropic] --> N["timeout: 25, temperature: 0.0"]
        O[ChatGoogleGenerativeAI] --> P["Fresh instances per call"]
    end
    
    C --> K
    D --> K
    E --> K
    F --> K
    G --> M
    H --> O
    I --> O
    J --> O
```

**Sources**: [run_browser_use.py:161-237]()

### Single Task Processing

The `process_single_task` function encapsulates the core logic for executing individual browser automation tasks:

```mermaid
sequenceDiagram
    participant PWT as process_with_semaphore
    participant PST as process_single_task
    participant Agent as browser_use.Agent
    participant Browser as Browser instance
    participant Eval as auto_eval_by_gpt4o
    participant Storage as File System
    
    PWT->>PST: "task, client, stats, results_dir"
    PST->>PST: "Create task_dir, check existing results"
    
    alt "Fresh execution needed"
        PST->>Agent: "Initialize with task_str, llm, browser"
        PST->>Agent: "agent.run(max_steps=30)"
        Agent->>Browser: "Execute web actions"
        Browser->>Agent: "Screenshots + interaction history"
        Agent->>PST: "ActionHistory object"
        
        PST->>Eval: "auto_eval_by_gpt4o(task, client, history)"
        Eval->>PST: "eval_result, gpt_4v_res"
        
        PST->>PST: "create_task_result()"
        PST->>Storage: "Save task_result.json + history.json"
    else "Results exist"
        PST->>Storage: "Load existing task_result.json"
    end
    
    PST->>PWT: "Update stats, print progress"
```

**Sources**: [run_browser_use.py:240-311]()

## Concurrent Execution Management

The engine uses an asyncio `Semaphore` to control the number of concurrent browser instances, preventing resource exhaustion while maximizing throughput:

```mermaid
graph TB
    subgraph "Concurrency Control"
        A[main] --> B["Semaphore(max_concurrent_tasks)"]
        B --> C[asyncio.gather]
        
        subgraph "Per-Task Execution"
            D[process_with_semaphore] --> E["async with semaphore"]
            E --> F["Create Browser instance"]
            F --> G[process_single_task]
            G --> H["browser.close()"]
        end
        
        C --> D
    end
    
    subgraph "Browser Configuration"
        I[BrowserConfig] --> J["headless=True"]
        I --> K["disable_security=True"]
        I --> L["window_size: 1280x1100"]
        I --> M["wait_for_network_idle: 5s"]
        I --> N["max_page_load_time: 20s"]
    end
    
    F --> I
```

The default configuration allows 3 concurrent tasks, which balances resource usage with execution speed on typical hardware configurations.

**Sources**: [run_browser_use.py:342-389]()

## Statistics and Result Tracking

### Real-time Statistics

The `RunStats` class provides real-time tracking of task execution progress:

```mermaid
classDiagram
    class RunStats {
        +total_tasks: int
        +current_task: int
        +successful_tasks: Set[str]
        +failed_tasks: Set[str] 
        +unknown_tasks: Set[str]
        +update(task_id, success) void
        +get_success_rate() str
        +print_periodic_summary() void
    }
    
    class TaskResult {
        +task_id: str
        +web_name: str
        +start_time: datetime
        +end_time: datetime
        +duration_seconds: float
        +num_steps: int
        +success: EvalResult
        +task_prompt: str
        +final_answer: str
        +gpt_4v_res: str
    }
    
    class ExperimentResults {
        +total_tasks: int
        +total_success: int
        +total_failed: int
        +total_unknown: int
        +all_tasks: List[TaskResult]
    }
    
    RunStats --> TaskResult : tracks
    ExperimentResults --> TaskResult : aggregates
```

**Sources**: [run_browser_use.py:36-88]()

### Result Persistence

Results are saved in a structured format under `results/examples-browser-use/`:

- `{task_id}/task_result.json` - Individual task results
- `{task_id}/history.json` - Complete interaction history  
- `experiment_results.json` - Aggregated experiment statistics

**Sources**: [run_browser_use.py:127-152]()

## Command Line Interface

The execution engine supports configurable execution parameters:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `--max-concurrent` | 3 | Number of simultaneous browser instances |
| `--model-provider` | azure | LLM provider selection |

Supported model providers: `azure`, `anthropic`, `google/gemini-1.5-flash`, `google/gemini-1.5-flash-8b`, `google/gemini-1.5-pro`

**Sources**: [run_browser_use.py:406-434]()

## Error Handling and Cleanup

The engine includes comprehensive error handling and resource cleanup:

- **WebDriver Cache Cleanup**: Removes stale selenium cache directories before execution
- **Browser Instance Cleanup**: Ensures browser instances are properly closed even on exceptions
- **Task-level Error Isolation**: Individual task failures don't crash the entire pipeline
- **Graceful Shutdown**: Handles keyboard interrupts and fatal errors appropriately

**Sources**: [run_browser_use.py:90-101](), [run_browser_use.py:377-382](), [run_browser_use.py:435-439]()

---

