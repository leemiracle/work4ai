<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/promptflow · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/promptflow-azure/CHANGELOG.md](src/promptflow-azure/CHANGELOG.md)
- [src/promptflow-azure/pyproject.toml](src/promptflow-azure/pyproject.toml)
- [src/promptflow-core/CHANGELOG.md](src/promptflow-core/CHANGELOG.md)
- [src/promptflow-core/pyproject.toml](src/promptflow-core/pyproject.toml)
- [src/promptflow-devkit/CHANGELOG.md](src/promptflow-devkit/CHANGELOG.md)
- [src/promptflow-devkit/promptflow/_sdk/_utilities/tracing_utils.py](src/promptflow-devkit/promptflow/_sdk/_utilities/tracing_utils.py)
- [src/promptflow-devkit/pyproject.toml](src/promptflow-devkit/pyproject.toml)
- [src/promptflow-recording/recordings/local/executor_node_cache.shelve.bak](src/promptflow-recording/recordings/local/executor_node_cache.shelve.bak)
- [src/promptflow-recording/recordings/local/executor_node_cache.shelve.dat](src/promptflow-recording/recordings/local/executor_node_cache.shelve.dat)
- [src/promptflow-recording/recordings/local/executor_node_cache.shelve.dir](src/promptflow-recording/recordings/local/executor_node_cache.shelve.dir)
- [src/promptflow-tracing/CHANGELOG.md](src/promptflow-tracing/CHANGELOG.md)
- [src/promptflow-tracing/pyproject.toml](src/promptflow-tracing/pyproject.toml)
- [src/promptflow/CHANGELOG.md](src/promptflow/CHANGELOG.md)
- [src/promptflow/promptflow/_version.py](src/promptflow/promptflow/_version.py)
- [src/promptflow/setup.py](src/promptflow/setup.py)
- [src/promptflow/tests/executor/e2etests/test_langchain.py](src/promptflow/tests/executor/e2etests/test_langchain.py)
- [src/promptflow/tests/executor/e2etests/test_telemetry.py](src/promptflow/tests/executor/e2etests/test_telemetry.py)
- [src/promptflow/tests/executor/e2etests/test_traces.py](src/promptflow/tests/executor/e2etests/test_traces.py)
- [src/promptflow/tests/test_configs/flows/openai_chat_api_flow/chat.py](src/promptflow/tests/test_configs/flows/openai_chat_api_flow/chat.py)
- [src/promptflow/tests/test_configs/flows/openai_chat_api_flow/flow.dag.yaml](src/promptflow/tests/test_configs/flows/openai_chat_api_flow/flow.dag.yaml)
- [src/promptflow/tests/test_configs/flows/openai_chat_api_flow/inputs.jsonl](src/promptflow/tests/test_configs/flows/openai_chat_api_flow/inputs.jsonl)
- [src/promptflow/tests/test_configs/flows/openai_completion_api_flow/completion.py](src/promptflow/tests/test_configs/flows/openai_completion_api_flow/completion.py)
- [src/promptflow/tests/test_configs/flows/openai_completion_api_flow/flow.dag.yaml](src/promptflow/tests/test_configs/flows/openai_completion_api_flow/flow.dag.yaml)
- [src/promptflow/tests/test_configs/flows/openai_completion_api_flow/inputs.jsonl](src/promptflow/tests/test_configs/flows/openai_completion_api_flow/inputs.jsonl)

</details>



This document provides a comprehensive overview of the Microsoft Prompt Flow system architecture, covering the core components, execution model, and integration patterns. It focuses on the technical implementation details including key classes, modules, and their interactions.

For information about specific flow types and their usage, see [Flow Types](#4). For CLI and SDK usage patterns, see [CLI and SDK](#3). For Azure-specific integration details, see [Azure Integration](#7).

## Package Structure

Prompt Flow follows a modular architecture with four core packages that provide distinct but interconnected capabilities.

```mermaid
graph TD
    subgraph "Main Package"
        PF["promptflow<br/>(Meta Package)"]
    end
    
    subgraph "Core Packages"
        PFC["promptflow-core<br/>(Core Execution)"]
        PFD["promptflow-devkit<br/>(Development Tools)"]
        PFT["promptflow-tracing<br/>(Telemetry & Observability)"]
    end
    
    subgraph "Extension Packages"
        PFA["promptflow-azure<br/>(Cloud Integration)"]
        PFTO["promptflow-tools<br/>(Built-in Tools)"]
        PFEV["promptflow-evals<br/>(Evaluation Framework)"]
    end
    
    PF --> PFC
    PF --> PFD
    PF --> PFT
    
    PFD --> PFC
    PFA --> PFD
    PFEV --> PFD
    
    PFC --> PFT
```

**Package Dependencies**

| Package | Purpose | Key Dependencies |
|---------|---------|------------------|
| `promptflow-core` | Flow execution engine, tool system | `promptflow-tracing`, `ruamel.yaml`, `jsonschema` |
| `promptflow-devkit` | CLI, SDK, local services | `promptflow-core`, `httpx`, `sqlalchemy`, `pandas` |
| `promptflow-tracing` | OpenTelemetry integration, trace collection | `opentelemetry-sdk`, `tiktoken` |
| `promptflow-azure` | Azure AI/ML integration | `azure-ai-ml`, `azure-cosmos`, `promptflow-devkit` |

Sources: [src/promptflow/setup.py:23-27](), [src/promptflow-core/pyproject.toml:42-58](), [src/promptflow-devkit/pyproject.toml:42-70](), [src/promptflow-tracing/pyproject.toml:36-40](), [src/promptflow-azure/pyproject.toml:39-47]()

## Flow Execution Architecture

The flow execution system is built around the `FlowExecutor` class which coordinates tool resolution, node scheduling, and trace collection.

```mermaid
graph TD
    subgraph "Execution Entry Points"
        CLI["CLI Commands<br/>(pf flow test)"]
        SDK["SDK Methods<br/>(PFClient.test)"]
        API["Serving API<br/>(Flask/FastAPI)"]
    end
    
    subgraph "Core Execution Engine"
        FE["FlowExecutor<br/>(exec_line, exec_batch)"]
        ANS["AsyncNodesScheduler<br/>(schedule_node_execution)"]
        DAG["DAG Manager<br/>(build_dependency_graph)"]
    end
    
    subgraph "Tool Resolution"
        TR["ToolResolver<br/>(resolve_tool_by_node)"]
        TM["ToolsManager<br/>(load_tool_for_node)"]
        BM["BuiltinsManager<br/>(_load_package_tool)"]
    end
    
    subgraph "Batch Processing"
        BE["BatchEngine<br/>(run)"]
        LEP["LineExecutionProcessPool<br/>(_process_wrapper)"]
        PM["ProcessManager<br/>(create_spawned_fork_process_manager)"]
    end
    
    subgraph "Storage & Tracking"
        RT["RunTracker<br/>(track_node_execution)"]
        RS["RunStorage<br/>(persist_node_run)"]
        NLM["NodeLogManager<br/>(persist_logs)"]
    end
    
    CLI --> FE
    SDK --> FE
    API --> FE
    
    FE --> ANS
    FE --> TR
    FE --> RT
    
    ANS --> DAG
    TR --> TM
    TM --> BM
    
    BE --> LEP
    BE --> FE
    LEP --> PM
    
    RT --> RS
    RT --> NLM
```

**Key Execution Components**

| Component | Responsibility | Location |
|-----------|---------------|----------|
| `FlowExecutor` | Main orchestrator for flow execution | `promptflow.executor.flow_executor` |
| `AsyncNodesScheduler` | Manages parallel node execution | `promptflow.executor._async_nodes_scheduler` |
| `ToolResolver` | Resolves node definitions to executable tools | `promptflow.executor._tool_resolver` |
| `BatchEngine` | Handles batch/bulk execution with multiprocessing | `promptflow.batch._batch_engine` |

Sources: [src/promptflow/tests/executor/e2etests/test_traces.py:19](), [src/promptflow/tests/executor/e2etests/test_telemetry.py:12](), [src/promptflow/tests/executor/e2etests/test_langchain.py:6]()

## Tool System Architecture

The tool system handles discovery, loading, and execution of various tool types including Python functions, LLM calls, and custom tools.

```mermaid
graph TD
    subgraph "Tool Types"
        PT["Python Tools<br/>(@tool decorated)"]
        LT["LLM Tools<br/>(OpenAI/AzureOpenAI)"]
        CT["Custom Tools<br/>(Package/Script)"]
        PROMPT["Prompt Tools<br/>(Jinja2 templates)"]
    end
    
    subgraph "Tool Resolution Pipeline"
        TR["ToolResolver<br/>(resolve_tool_by_node)"]
        TL["ToolLoader<br/>(load_tool_for_*)"]
        BM["BuiltinsManager<br/>(_load_package_tool)"]
        FV["FlowValidator<br/>(validate_node_inputs)"]
    end
    
    subgraph "Tool Loading Strategies"
        RPK["_resolve_package_node<br/>(Built-in tools)"]
        RSN["_resolve_script_node<br/>(File-based tools)"]
        RLN["_resolve_llm_node<br/>(LLM API calls)"]
        RPN["_resolve_prompt_node<br/>(Template rendering)"]
    end
    
    subgraph "Connection Management"
        CM["ConnectionManager<br/>(get_connection)"]
        AOAI["AzureOpenAIConnection"]
        OAI["OpenAIConnection"]
        CUST["CustomConnection"]
    end
    
    TR --> TL
    TL --> BM
    TR --> FV
    
    TR --> RPK
    TR --> RSN
    TR --> RLN
    TR --> RPN
    
    RPK --> PT
    RSN --> CT
    RLN --> LT
    RPN --> PROMPT
    
    LT --> CM
    CM --> AOAI
    CM --> OAI
    CM --> CUST
```

**Tool Resolution Flow**

1. **Node Analysis**: `ToolResolver.resolve_tool_by_node()` examines node type and source
2. **Type-Specific Loading**: Delegates to specialized resolvers based on tool type
3. **Input Validation**: `FlowValidator` ensures required inputs and connections are available
4. **Connection Injection**: Resolves connection references to actual connection objects
5. **Tool Instance Creation**: Returns executable tool with bound inputs and connections

Sources: Test flows showing tool usage patterns in [src/promptflow/tests/test_configs/flows/openai_chat_api_flow/chat.py:35-78](), [src/promptflow/tests/test_configs/flows/openai_completion_api_flow/completion.py:26-66]()

## Tracing and Observability

Prompt Flow integrates with OpenTelemetry to provide comprehensive tracing of flow execution, tool calls, and LLM interactions.

```mermaid
graph TD
    subgraph "Trace Collection"
        OT["OpenTelemetry SDK<br/>(TracerProvider)"]
        AI["OpenAI API Injector<br/>(patch openai calls)"]
        TD["@trace Decorator<br/>(function tracing)"]
    end
    
    subgraph "Trace Processing"
        TE["TraceExporter<br/>(OTLP/Local)"]
        TP["TraceProcessor<br/>(SimpleSpanProcessor)"]
        TU["TracingUtils<br/>(parse_protobuf_span)"]
    end
    
    subgraph "Trace Storage"
        LS["Local Storage<br/>(.promptflow/traces)"]
        PFS["Prompt Flow Service<br/>(local trace UI)"]
        COSMOS["Azure Cosmos DB<br/>(cloud traces)"]
    end
    
    subgraph "Trace Consumers"
        UI["Trace UI<br/>(visualization)"]
        API["Trace API<br/>(programmatic access)"]
        TEL["Telemetry<br/>(usage metrics)"]
    end
    
    OT --> TP
    AI --> OT
    TD --> OT
    
    TP --> TE
    TE --> LS
    TE --> COSMOS
    
    TU --> LS
    
    LS --> PFS
    PFS --> UI
    LS --> API
    LS --> TEL
```

**Tracing Components**

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `openai_injector` | Automatically traces OpenAI API calls | `inject()`, `recover()` |
| `@trace` decorator | Manual function tracing | Applied to user functions |
| `parse_protobuf_span` | Converts OTLP spans to internal format | `parse_protobuf_span()` |
| `TraceTelemetryHelper` | Aggregates usage metrics | `append()`, `log_telemetry()` |

Sources: [src/promptflow/tests/executor/e2etests/test_traces.py:143-151](), [src/promptflow-devkit/promptflow/_sdk/_utilities/tracing_utils.py:342-380]()

## Batch Processing System

The batch processing system enables scalable execution of flows across large datasets using multiprocessing.

```mermaid
graph TD
    subgraph "Batch Orchestration"
        BE["BatchEngine<br/>(run method)"]
        BIP["BatchInputsProcessor<br/>(process_input_dirs)"]
        LEP["LineExecutionProcessPool<br/>(_process_wrapper)"]
    end
    
    subgraph "Process Management"
        PM["ProcessManager<br/>(create_spawned_fork_process_manager)"]
        PF["ProxyFactory<br/>(create_executor_proxy)"]
        TO["TimeoutHandler<br/>(handle_line_timeout)"]
    end
    
    subgraph "Executor Proxies"
        PEP["PythonExecutorProxy<br/>(exec_line)"]
        CEP["CSharpExecutorProxy<br/>(exec_line_async)"]
        CGOP["ChatGroupOrchestratorProxy<br/>(exec_aggregation_async)"]
    end
    
    subgraph "Result Collection"
        BR["BatchResult<br/>(completed_lines, failed_lines)"]
        QRS["QueueRunStorage<br/>(persist_node_run)"]
        LRS["LineRunStorage<br/>(get_run_result)"]
    end
    
    BE --> BIP
    BE --> LEP
    
    LEP --> PM
    PM --> PF
    PM --> TO
    
    PF --> PEP
    PF --> CEP  
    PF --> CGOP
    
    LEP --> BR
    BR --> QRS
    QRS --> LRS
```

**Batch Processing Configuration**

| Setting | Default | Environment Variable | Purpose |
|---------|---------|---------------------|---------|
| Worker Count | 4 | `PF_WORKER_COUNT` | Number of parallel processes |
| Line Timeout | 600s | `PF_LINE_TIMEOUT_SEC` | Per-line execution timeout |
| Batch Timeout | 3600s | `PF_BATCH_TIMEOUT_SEC` | Total batch timeout |

Sources: [src/promptflow/tests/executor/e2etests/test_telemetry.py:117-156](), [src/promptflow/tests/executor/e2etests/test_langchain.py:24-33]()

## Integration Points

The architecture provides multiple integration points for extending and customizing Prompt Flow behavior.

```mermaid
graph TD
    subgraph "Extension Points"
        CONN["Custom Connections<br/>(CustomConnection)"]
        TOOLS["Custom Tools<br/>(@tool decorator)"]
        EXPORT["Custom Exporters<br/>(SpanExporter)"]
        SERVE["Custom Serving<br/>(Flask/FastAPI apps)"]
    end
    
    subgraph "Configuration Management"
        ENV["Environment Variables<br/>(PF_* settings)"]
        CONFIG["Config Files<br/>(.promptflow/pf.yaml)"]
        SECRETS["Secret Management<br/>(keyring integration)"]
    end
    
    subgraph "Runtime Environments"
        LOCAL["Local Development<br/>(pf CLI)"]
        CONTAINER["Container Deployment<br/>(Docker)"]
        AZURE["Azure AI/ML<br/>(pfazure CLI)"]
        CLOUD["Cloud Serving<br/>(Azure Container Apps)"]
    end
    
    CONN --> LOCAL
    TOOLS --> LOCAL
    EXPORT --> LOCAL
    SERVE --> LOCAL
    
    ENV --> CONFIG
    CONFIG --> SECRETS
    
    LOCAL --> CONTAINER
    LOCAL --> AZURE
    CONTAINER --> CLOUD
    AZURE --> CLOUD
```

**Key Integration Patterns**

- **Tool Registration**: Custom tools via `@tool` decorator and package entry points
- **Connection Providers**: Extensible connection system supporting Azure ML, local files, environment variables
- **Trace Exporters**: OpenTelemetry-compatible exporters for various backends
- **Serving Frameworks**: Support for Flask and FastAPI with automatic endpoint generation

Sources: Configuration and integration patterns from [src/promptflow/CHANGELOG.md:88-98](), [src/promptflow-devkit/CHANGELOG.md:52-62]()

---

