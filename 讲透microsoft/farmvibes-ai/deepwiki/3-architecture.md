<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/farmvibes-ai · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/requirements.txt](docs/requirements.txt)
- [src/vibe_core/pyproject.toml](src/vibe_core/pyproject.toml)
- [src/vibe_core/vibe_core/client.py](src/vibe_core/vibe_core/client.py)
- [src/vibe_core/vibe_core/data/core_types.py](src/vibe_core/vibe_core/data/core_types.py)
- [src/vibe_core/vibe_core/datamodel.py](src/vibe_core/vibe_core/datamodel.py)

</details>



## Purpose and Scope

This document describes the overall architecture of FarmVibes.AI, including the major system components, their interactions, and key architectural patterns. It provides a high-level view of how the platform is structured and how data flows through the system.

For detailed information about specific subsystems, refer to:
- Package structure and dependencies: [vibe_core Package](#3.1)
- Kubernetes and Dapr infrastructure: [Infrastructure and Deployment](#3.2)
- Data type system and BaseVibe hierarchy: [Data Models](#3.3)
- Client SDK and API interaction: [Client API](#3.4)
- Workflow system details: [Workflows](#4)

---

## System Overview

FarmVibes.AI follows a **microservices architecture** deployed on Kubernetes, with a Python client SDK communicating with a REST API service. The system uses **Dapr** (Distributed Application Runtime) for service-to-service communication, state management, and pub/sub messaging.

### Layered Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        FarmvibesAiClient["FarmvibesAiClient<br/>(client.py)"]
        ClusterType["ClusterType enum<br/>(local/remote)"]
        VibeWorkflowRun["VibeWorkflowRun<br/>(client.py:729)"]
    end
    
    subgraph "API Layer"
        RestAPI["REST API Endpoints<br/>/v0/workflows, /v0/runs"]
        WorkflowRegistry["Workflow Registry<br/>(DAG definitions)"]
    end
    
    subgraph "Data Model Layer"
        BaseVibe["BaseVibe<br/>(core_types.py:303)"]
        DataVibe["DataVibe<br/>(core_types.py:456)"]
        AssetVibe["AssetVibe<br/>(core_types.py:225)"]
        RunConfig["RunConfig<br/>(datamodel.py:186)"]
        RunStatus["RunStatus enum<br/>(datamodel.py:128)"]
    end
    
    subgraph "Execution Engine"
        DaprRuntime["Dapr Runtime<br/>(sidecars)"]
        WorkerPool["Worker Pool<br/>(operator containers)"]
        Scheduler["Task Scheduler"]
    end
    
    subgraph "State & Messaging"
        Redis["Redis<br/>(state store)"]
        RabbitMQ["RabbitMQ<br/>(pub/sub broker)"]
        RunDB["Run Database<br/>(RunConfig storage)"]
    end
    
    subgraph "Infrastructure"
        K8sCluster["Kubernetes Cluster<br/>(k3d or AKS)"]
        Terraform["Terraform Modules<br/>(terraform/*.tf)"]
    end
    
    FarmvibesAiClient --> RestAPI
    ClusterType --> FarmvibesAiClient
    VibeWorkflowRun --> FarmvibesAiClient
    
    RestAPI --> WorkflowRegistry
    RestAPI --> RunConfig
    
    BaseVibe --> DataVibe
    DataVibe --> AssetVibe
    RunConfig --> RunStatus
    
    RestAPI --> Scheduler
    Scheduler --> DaprRuntime
    DaprRuntime --> WorkerPool
    
    DaprRuntime --> Redis
    DaprRuntime --> RabbitMQ
    Scheduler --> RunDB
    
    K8sCluster --> DaprRuntime
    K8sCluster --> Redis
    K8sCluster --> RabbitMQ
    Terraform --> K8sCluster
```

**Sources:** [src/vibe_core/vibe_core/client.py:1-1105](), [src/vibe_core/vibe_core/datamodel.py:1-353](), [src/vibe_core/vibe_core/data/core_types.py:1-870]()

---

## Core Components

### 1. vibe_core Package

The `vibe_core` package is the primary Python distribution that users install via pip. It contains the client SDK, data models, and utility functions.

**Key modules:**
- `vibe_core.client`: Contains `FarmvibesAiClient` class for API interaction
- `vibe_core.datamodel`: Defines `RunConfig`, `RunStatus`, `RunDetails`, and related types
- `vibe_core.data.core_types`: Defines `BaseVibe`, `DataVibe`, `AssetVibe` base classes
- `vibe_core.monitor`: Provides `VibeWorkflowRunMonitor` for tracking execution
- `vibe_core.cli`: Command-line interface via `farmvibes-ai` command

**Package configuration:**

| Property | Value |
|----------|-------|
| Package name | `vibe-core` |
| Python version | `>=3.8` |
| Build system | `setuptools>=42`, `wheel` |
| CLI entry point | `farmvibes-ai` command |

**Dependencies include:**
- `pydantic~=1.10.0` (data validation)
- `pystac~=1.6.0` (STAC format support)
- `requests~=2.32.0` (HTTP client)
- `shapely>=1.7.1` (geometry operations)
- `rich~=13.7.1` (terminal UI)

**Sources:** [src/vibe_core/pyproject.toml:1-64]()

### 2. Client SDK (FarmvibesAiClient)

The `FarmvibesAiClient` class provides the primary interface for users to interact with the platform.

```mermaid
graph LR
    subgraph "FarmvibesAiClient Methods"
        ListWorkflows["list_workflows()<br/>(line 267)"]
        DescribeWorkflow["describe_workflow()<br/>(line 279)"]
        Run["run()<br/>(line 567)"]
        Monitor["monitor()<br/>(line 675)"]
        DescribeRun["describe_run()<br/>(line 391)"]
        CancelRun["cancel_run()<br/>(line 340)"]
    end
    
    subgraph "HTTP Layer"
        Request["_request()<br/>(line 165)"]
        Session["requests.Session<br/>(line 162)"]
    end
    
    subgraph "Service URL"
        LocalURL["get_local_service_url()<br/>(line 1038)"]
        RemoteURL["get_remote_service_url()<br/>(line 1055)"]
        ConfigFile["~/.config/farmvibes-ai/<br/>service_url"]
    end
    
    ListWorkflows --> Request
    DescribeWorkflow --> Request
    Run --> Request
    DescribeRun --> Request
    CancelRun --> Request
    
    Request --> Session
    
    LocalURL --> ConfigFile
    RemoteURL --> ConfigFile
    
    Session --> RestEndpoints["REST API<br/>/v0/workflows<br/>/v0/runs"]
```

**Key responsibilities:**
- Workflow discovery and submission ([src/vibe_core/vibe_core/client.py:267-277](), [src/vibe_core/vibe_core/client.py:567-612]())
- Run lifecycle management ([src/vibe_core/vibe_core/client.py:340-389]())
- Real-time monitoring ([src/vibe_core/vibe_core/client.py:675-726]())
- Service URL resolution ([src/vibe_core/vibe_core/client.py:1038-1104]())

**Sources:** [src/vibe_core/vibe_core/client.py:145-1105]()

### 3. Data Model Layer

The data model is built on a hierarchical type system rooted in `BaseVibe`.

```mermaid
graph TD
    BaseVibe["BaseVibe<br/>(core_types.py:303)"]
    DataVibe["DataVibe<br/>(core_types.py:456)"]
    AssetVibe["AssetVibe<br/>(core_types.py:225)"]
    
    BaseVibe --> DataVibe
    BaseVibe --> FoodVibe["FoodVibe<br/>(core_types.py:641)"]
    
    DataVibe --> TimeSeries["TimeSeries<br/>(core_types.py:526)"]
    DataVibe --> DataSequence["DataSequence<br/>(core_types.py:557)"]
    DataVibe --> ExternalReference["ExternalReference<br/>(core_types.py:626)"]
    DataVibe --> CarbonOffsetInfo["CarbonOffsetInfo<br/>(core_types.py:729)"]
    DataVibe --> GHGFlux["GHGFlux<br/>(core_types.py:737)"]
    
    DataVibe -.contains.-> AssetVibe
    
    DataSequence -.maps.-> AssetOrder["asset_order: Dict[str, int]<br/>(core_types.py:564)"]
    DataSequence -.maps.-> AssetTimeRange["asset_time_range<br/>(core_types.py:566)"]
    
    AssetVibe --> LocalPath["local_path property<br/>(core_types.py:264)"]
    AssetVibe --> URL["url property<br/>(core_types.py:288)"]
```

**Key type properties:**

| Type | Key Fields | Purpose |
|------|------------|---------|
| `BaseVibe` | `id`, `hash_id` | Base for all data types |
| `DataVibe` | `time_range`, `geometry`, `bbox`, `assets` | Spatiotemporal data with assets |
| `AssetVibe` | `path_or_url`, `type`, `id` | Reference to file or remote resource |
| `DataSequence` | `asset_order`, `asset_time_range` | Ordered collection of assets |

**Type registration:** All `BaseVibe` subclasses are automatically registered in `data_registry` during class definition ([src/vibe_core/vibe_core/data/core_types.py:407-410]()).

**Sources:** [src/vibe_core/vibe_core/data/core_types.py:303-870]()

### 4. Run Configuration and Status

Workflow execution state is managed through a set of dataclasses:

```mermaid
graph TB
    subgraph "Configuration Classes"
        RunBase["RunBase<br/>(datamodel.py:93)"]
        RunConfigInput["RunConfigInput<br/>(datamodel.py:112)"]
        RunConfig["RunConfig<br/>(datamodel.py:186)"]
        RunConfigUser["RunConfigUser<br/>(datamodel.py:218)"]
    end
    
    subgraph "Status Tracking"
        RunStatus["RunStatus enum<br/>(datamodel.py:128)"]
        RunDetails["RunDetails<br/>(datamodel.py:168)"]
        StatusValues["pending → queued → running<br/>→ done | failed | cancelled"]
    end
    
    subgraph "Workflow Run"
        VibeWorkflowRun["VibeWorkflowRun<br/>(client.py:729)"]
        StatusProp["status property<br/>(client.py:840)"]
        OutputProp["output property<br/>(client.py:868)"]
        TaskDetails["task_details property<br/>(client.py:849)"]
    end
    
    RunBase --> RunConfigInput
    RunConfigInput --> RunConfig
    RunConfig --> RunConfigUser
    
    RunConfig --> RunDetails
    RunDetails --> RunStatus
    RunStatus --> StatusValues
    
    VibeWorkflowRun --> StatusProp
    VibeWorkflowRun --> OutputProp
    VibeWorkflowRun --> TaskDetails
    
    TaskDetails --> RunDetails
```

**RunStatus state machine:**
- `pending`: Run created but not yet scheduled
- `queued`: Run scheduled, waiting for execution
- `running`: Run is actively executing
- `done`: Run completed successfully
- `failed`: Run encountered an error
- `cancelled`: Run was cancelled by user
- `deleting/deleted`: Run is being/has been deleted

**Sources:** [src/vibe_core/vibe_core/datamodel.py:93-260](), [src/vibe_core/vibe_core/client.py:729-1036]()

---

## Communication Patterns

### Client-Server Interaction

```mermaid
sequenceDiagram
    participant User
    participant FarmvibesAiClient
    participant RequestsSession
    participant RestAPI
    participant WorkflowEngine
    
    User->>FarmvibesAiClient: run(workflow, geometry, time_range)
    FarmvibesAiClient->>FarmvibesAiClient: _form_payload()
    FarmvibesAiClient->>FarmvibesAiClient: verify_disk_space()
    FarmvibesAiClient->>RequestsSession: POST /v0/runs
    RequestsSession->>RestAPI: HTTP POST with RunConfigInput
    RestAPI->>WorkflowEngine: Create workflow run
    WorkflowEngine-->>RestAPI: Return run_id
    RestAPI-->>RequestsSession: {"id": "..."}
    RequestsSession-->>FarmvibesAiClient: Response
    FarmvibesAiClient->>FarmvibesAiClient: get_run_by_id(run_id)
    FarmvibesAiClient-->>User: VibeWorkflowRun object
    
    User->>VibeWorkflowRun: monitor()
    loop Every refresh_time_s
        VibeWorkflowRun->>FarmvibesAiClient: list_runs(id)
        FarmvibesAiClient->>RequestsSession: GET /v0/runs?ids=...
        RequestsSession->>RestAPI: HTTP GET
        RestAPI-->>RequestsSession: Run status
        RequestsSession-->>FarmvibesAiClient: Run details
        FarmvibesAiClient->>VibeWorkflowRunMonitor: update_run_status()
    end
```

**REST API endpoints:**
- `GET /v0/workflows`: List available workflows
- `GET /v0/workflows/{name}`: Get workflow description
- `POST /v0/runs`: Submit new workflow run
- `GET /v0/runs`: List runs (with optional filters)
- `GET /v0/runs/{id}`: Get run details
- `POST /v0/runs/{id}/cancel`: Cancel a run
- `DELETE /v0/runs/{id}`: Delete a run
- `POST /v0/runs/{id}/resubmit`: Resubmit a run
- `GET /v0/system-metrics`: Get system metrics

**Sources:** [src/vibe_core/vibe_core/client.py:165-189](), [src/vibe_core/vibe_core/client.py:267-627]()

### Dapr-based Service Communication

Within the Kubernetes cluster, services communicate through Dapr sidecars:

```mermaid
graph LR
    subgraph "Service A Pod"
        ServiceA["Workflow Service"]
        DaprA["Dapr Sidecar"]
    end
    
    subgraph "Service B Pod"
        ServiceB["Operator Service"]
        DaprB["Dapr Sidecar"]
    end
    
    subgraph "Dapr Components"
        PubSub["RabbitMQ<br/>(control-pubsub)"]
        StateStore["Redis<br/>(statestore)"]
        Resiliency["worker-resiliency<br/>(retry policy)"]
    end
    
    ServiceA --> DaprA
    DaprA -->|"Publish"| PubSub
    PubSub -->|"Subscribe"| DaprB
    DaprB --> ServiceB
    
    ServiceA -.->|"State API"| DaprA
    DaprA -.-> StateStore
    
    DaprA -.-> Resiliency
    DaprB -.-> Resiliency
```

**Dapr features used:**
- **Pub/Sub**: Task distribution via RabbitMQ (`control-pubsub` component)
- **State Store**: Run state persistence via Redis (`statestore` component)
- **Resiliency**: Automatic retries and timeouts (`worker-resiliency` policy)

**Sources:** Inferred from system diagrams and typical Dapr patterns

---

## Data Flow

### Input Data Processing

```mermaid
graph LR
    subgraph "User Input"
        Geometry["BaseGeometry<br/>(shapely)"]
        TimeRange["Tuple[datetime, datetime]"]
        CustomData["InputData[BaseVibe]"]
    end
    
    subgraph "Serialization"
        SerializeInput["serialize_input()<br/>(data/utils.py)"]
        SpatioTemporalJson["SpatioTemporalJson<br/>(datamodel.py:79)"]
        FormPayload["_form_payload()<br/>(client.py:191)"]
    end
    
    subgraph "Transmission"
        DumpToJson["dump_to_json()<br/>(data/json_converter.py)"]
        HttpPost["HTTP POST"]
    end
    
    subgraph "Server Processing"
        ParseInput["Parse RunConfigInput"]
        CreateRun["Create RunConfig"]
        ScheduleTasks["Schedule workflow tasks"]
    end
    
    Geometry --> FormPayload
    TimeRange --> FormPayload
    CustomData --> SerializeInput
    SerializeInput --> FormPayload
    
    FormPayload --> SpatioTemporalJson
    SpatioTemporalJson --> DumpToJson
    DumpToJson --> HttpPost
    
    HttpPost --> ParseInput
    ParseInput --> CreateRun
    CreateRun --> ScheduleTasks
```

**Key transformations:**
1. **Geometry conversion**: Shapely `BaseGeometry` → GeoJSON ([src/vibe_core/vibe_core/client.py:233-238]())
2. **Serialization**: Python objects → JSON via `dump_to_json()` ([src/vibe_core/vibe_core/client.py:608-609]())
3. **Type handling**: `BaseVibe` objects serialized via STAC format

**Sources:** [src/vibe_core/vibe_core/client.py:191-239]()

### Output Data Processing

```mermaid
graph LR
    subgraph "Server Storage"
        CompressOutput["Compress with zlib<br/>encode() (datamodel.py:329)"]
        Base64["Base64 encode"]
        StoreRun["Store in RunConfig.output"]
    end
    
    subgraph "Client Retrieval"
        GetRun["describe_run(run_id)"]
        Decode["decode() (datamodel.py:343)"]
        ParseJson["json.loads()"]
    end
    
    subgraph "Conversion"
        DeserializeStac["deserialize_stac()"]
        StacConverter["StacConverter.from_stac_item()"]
        BaseVibeDict["BaseVibeDict<br/>(Dict[str, BaseVibe])"]
    end
    
    CompressOutput --> Base64
    Base64 --> StoreRun
    
    StoreRun --> GetRun
    GetRun --> Decode
    Decode --> ParseJson
    
    ParseJson --> DeserializeStac
    DeserializeStac --> StacConverter
    StacConverter --> BaseVibeDict
```

**Output encoding/decoding:**
- **Encoding**: `zlib.compress()` → `base64.encode()` ([src/vibe_core/vibe_core/datamodel.py:329-340]())
- **Decoding**: `base64.decode()` → `zlib.decompress()` ([src/vibe_core/vibe_core/datamodel.py:343-352]())
- **STAC conversion**: JSON → `BaseVibe` objects via `StacConverter` ([src/vibe_core/vibe_core/client.py:779-780]())

**Sources:** [src/vibe_core/vibe_core/datamodel.py:329-352](), [src/vibe_core/vibe_core/client.py:762-780]()

---

## Execution Model

### Workflow Run Lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending: User submits run
    pending --> queued: Run accepted by scheduler
    queued --> running: Worker picks up task
    running --> done: All tasks complete successfully
    running --> failed: Task encounters error
    running --> cancelled: User cancels run
    
    done --> deleted: User deletes run
    failed --> deleted: User deletes run
    cancelled --> deleted: User deletes run
    
    pending --> cancelled: User cancels before start
    queued --> cancelled: User cancels before execution
    
    cancelled --> deleting: Delete initiated
    deleting --> deleted: Resources cleaned up
    
    deleted --> [*]
    
    note right of running
        task_details track
        individual operator status
    end note
    
    note right of deleted
        All cached data removed
        unless shared with other runs
    end note
```

**State transitions:**
- `pending` → `queued`: Scheduler accepts run
- `queued` → `running`: First task begins execution
- `running` → `done`/`failed`: All tasks complete/error occurs
- Any state → `cancelled`: User calls `cancel_run()` ([src/vibe_core/vibe_core/client.py:340-362]())
- Terminal states → `deleted`: User calls `delete_run()` ([src/vibe_core/vibe_core/client.py:364-389]())

**Blocking methods:**
- `block_until_complete()`: Wait for `done` or `failed` ([src/vibe_core/vibe_core/client.py:953-973]())
- `block_until_cancelled()`: Wait for `cancelled` ([src/vibe_core/vibe_core/client.py:933-951]())
- `block_until_deleted()`: Wait for `deleted` ([src/vibe_core/vibe_core/client.py:975-993]())

**Sources:** [src/vibe_core/vibe_core/datamodel.py:128-164](), [src/vibe_core/vibe_core/client.py:807-993]()

### Task Execution Flow

```mermaid
graph TB
    subgraph "Run Submission"
        FormPayload["_form_payload()<br/>(client.py:191)"]
        PostRun["POST /v0/runs"]
        CreateRunConfig["Create RunConfig<br/>(datamodel.py:186)"]
    end
    
    subgraph "Scheduling"
        ParseWorkflow["Parse workflow DAG"]
        TopologicalSort["Topological sort tasks"]
        QueueTasks["Queue tasks in order"]
    end
    
    subgraph "Task Distribution"
        PublishMessage["Publish to RabbitMQ<br/>(control-pubsub)"]
        DaprSidecar["Dapr sidecar delivers"]
        WorkerSubscribe["Worker subscribes"]
    end
    
    subgraph "Execution"
        PullTask["Worker pulls task"]
        LoadOperator["Load operator code"]
        ExecuteOp["Execute operator.run()"]
        SaveOutput["Save to state store"]
    end
    
    subgraph "Completion"
        UpdateTaskDetails["Update task_details<br/>(datamodel.py:193)"]
        CheckComplete["All tasks done?"]
        SetRunStatus["Set RunStatus to done"]
    end
    
    FormPayload --> PostRun
    PostRun --> CreateRunConfig
    CreateRunConfig --> ParseWorkflow
    
    ParseWorkflow --> TopologicalSort
    TopologicalSort --> QueueTasks
    QueueTasks --> PublishMessage
    
    PublishMessage --> DaprSidecar
    DaprSidecar --> WorkerSubscribe
    WorkerSubscribe --> PullTask
    
    PullTask --> LoadOperator
    LoadOperator --> ExecuteOp
    ExecuteOp --> SaveOutput
    
    SaveOutput --> UpdateTaskDetails
    UpdateTaskDetails --> CheckComplete
    CheckComplete -->|Yes| SetRunStatus
    CheckComplete -->|No| QueueTasks
```

**Key execution concepts:**
- **DAG-based workflows**: Tasks organized as directed acyclic graphs
- **Topological execution**: Dependencies determine task order
- **Distributed workers**: Multiple operator pods execute tasks concurrently
- **State persistence**: Task outputs stored in Redis for downstream tasks
- **Task details tracking**: Each task has individual `RunDetails` ([src/vibe_core/vibe_core/datamodel.py:168-183]())

**Sources:** [src/vibe_core/vibe_core/client.py:191-612](), [src/vibe_core/vibe_core/datamodel.py:168-196]()

---

## Configuration and Service Discovery

### Service URL Resolution

```mermaid
graph TD
    GetDefault["get_default_vibe_client()<br/>(client.py:1081)"]
    CheckType{ClusterType<br/>specified?}
    TryRemote["Try get_remote_service_url()<br/>(client.py:1055)"]
    RemoteFile["Read from<br/>~/.config/farmvibes-ai/<br/>remote_service_url"]
    TryLocal["Try get_local_service_url()<br/>(client.py:1038)"]
    LocalFile["Read from<br/>~/.config/farmvibes-ai/<br/>service_url"]
    Fallback["Use FALLBACK_SERVICE_URL<br/>http://127.0.0.1:31108/<br/>(client.py:51)"]
    CreateClient["Create FarmvibesAiClient<br/>(client.py:159)"]
    
    GetDefault --> CheckType
    CheckType -->|No| TryRemote
    CheckType -->|Yes| ClusterClient["ClusterType.client()<br/>(client.py:93)"]
    
    TryRemote --> RemoteFile
    RemoteFile -->|Success| CreateClient
    RemoteFile -->|Fail| TryLocal
    
    TryLocal --> LocalFile
    LocalFile -->|Success| CreateClient
    LocalFile -->|Fail| Fallback
    Fallback --> CreateClient
    
    ClusterClient -->|remote| TryRemote
    ClusterClient -->|local| TryLocal
```

**Configuration paths:**
- Remote cluster: `~/.config/farmvibes-ai/remote_service_url` ([src/vibe_core/vibe_core/client.py:69-75]())
- Local cluster: `~/.config/farmvibes-ai/service_url` ([src/vibe_core/vibe_core/client.py:63-67]())
- Fallback URL: `http://127.0.0.1:31108/` ([src/vibe_core/vibe_core/client.py:51-55]())

**ClusterType enum:**
- `ClusterType.local`: Connect to local k3d cluster
- `ClusterType.remote`: Connect to remote AKS cluster

**Sources:** [src/vibe_core/vibe_core/client.py:51-104](), [src/vibe_core/vibe_core/client.py:1038-1104]()

---

## Summary

The FarmVibes.AI architecture is characterized by:

1. **Client-Server Model**: Python SDK (`FarmvibesAiClient`) communicates with REST API
2. **Microservices on Kubernetes**: Containerized operators with Dapr sidecars
3. **Type-Safe Data Model**: `BaseVibe` hierarchy with automatic registry
4. **Stateful Execution**: `RunConfig` and `RunStatus` track workflow lifecycle
5. **Distributed Messaging**: RabbitMQ pub/sub for task distribution
6. **Persistent State**: Redis for operator state and caching
7. **Modular Package**: `vibe_core` provides reusable client and data model components

This architecture enables scalable, distributed execution of geospatial ML workflows while providing a simple Python interface for users.

---

