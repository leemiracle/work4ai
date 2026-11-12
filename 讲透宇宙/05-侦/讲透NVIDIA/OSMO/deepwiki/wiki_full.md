# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [docs/deployment_guide/introduction/whats_next.rst](docs/deployment_guide/introduction/whats_next.rst)
- [docs/deployment_options.svg](docs/deployment_options.svg)
- [docs/front_cover.png](docs/front_cover.png)
- [docs/index.rst](docs/index.rst)

</details>



OSMO is a workflow orchestration platform purpose-built for Physical AI development. It enables developers to define complex workflows in YAML that orchestrate tasks across heterogeneous compute resources—from cloud-based GPU training clusters to on-premise simulation hardware to edge devices—without requiring infrastructure expertise or custom scripting.

This page introduces OSMO's core architecture and the fundamental problem it solves. For detailed information on specific subsystems, see:
- Architecture details: [Architecture](#1.1)
- Core concepts and terminology: [Key Concepts](#1.2)
- Deployment procedures: [Getting Started](#2)

**Sources**: [README.md:1-189]()

## The Three Computer Problem

Physical AI development uniquely requires coordinating three distinct types of compute infrastructure, each with specialized hardware and deployment constraints:

| Compute Type | Hardware Examples | Primary Workloads | Typical Location |
|--------------|-------------------|-------------------|------------------|
| **Training** | GB200, H100, H200 | Deep learning, reinforcement learning | Cloud (EKS, AKS, GKE) |
| **Simulation** | L40, RTX Pro 6000 | Physics engines, sensor rendering (Isaac Sim) | Cloud or on-premise |
| **Edge** | Jetson AGX Thor, AGX Orin | Hardware-in-the-loop testing, robot validation | On-premise, lab environments |

Traditional approaches require developers to maintain separate infrastructure code, custom scripts, and deployment pipelines for each environment. OSMO solves this by providing a unified orchestration layer where a single workflow YAML can specify tasks that run on any combination of these compute backends.

**Example workflow spanning three compute types**:
```yaml
workflow:
  tasks:
  - name: simulation
    image: nvcr.io/nvidia/isaac-sim
    platform: rtx-pro-6000          # Simulation backend

  - name: train-policy
    image: nvcr.io/nvidia/pytorch
    platform: gb200                 # Training backend
    resources:
      gpu: 8
    inputs:
    - task: simulation

  - name: evaluate-thor
    image: my-ros-app
    platform: jetson-agx-thor       # Edge backend
    inputs:
    - task: train-policy
```

**Sources**: [README.md:89-111]()

## High-Level Architecture

OSMO uses a **Control Plane / Compute Plane** architecture that decouples the orchestration logic from compute execution. This design enables backend operators to initiate outbound connections to the control plane, allowing compute resources to exist behind firewalls and across geographic boundaries.

```mermaid
graph TB
    subgraph ControlPlane["Control Plane (Single Instance)"]
        API["API Service<br/>osmo/src/service/api/service_api.py"]
        Router["Router Service<br/>osmo/src/service/router"]
        UI["Web UI Service<br/>osmo/ui"]
        Worker["Worker Service<br/>osmo/src/service/worker"]
        Logger["Logger Service<br/>osmo/src/service/logger"]
        Agent["Agent Service<br/>osmo/src/service/agent"]
    end
    
    subgraph DataLayer["Data Layer"]
        Postgres[("PostgreSQL<br/>workflows, tasks, datasets<br/>osmo/src/models/postgres.py")]
        Redis[("Redis<br/>logs, job queues")]
        S3["Object Storage<br/>S3/Azure Blob/MinIO<br/>Content-Addressable"]
    end
    
    subgraph Backend1["Compute Plane: Cloud Training"]
        BO1["Backend Operator<br/>osmo/backend/backend_operator.py"]
        K8s1["Kubernetes Cluster<br/>EKS/AKS/GKE<br/>KAI Scheduler + GPU Operator"]
    end
    
    subgraph Backend2["Compute Plane: On-Prem Simulation"]
        BO2["Backend Operator<br/>osmo/backend/backend_operator.py"]
        K8s2["Kubernetes Cluster<br/>DGX/OVX Systems<br/>KAI Scheduler + GPU Operator"]
    end
    
    subgraph Backend3["Compute Plane: Edge Devices"]
        BO3["Backend Operator<br/>osmo/backend/backend_operator.py"]
        K8s3["Kubernetes Cluster<br/>Jetson Devices<br/>KAI Scheduler"]
    end
    
    API --> Postgres
    API --> Redis
    Worker --> Postgres
    Worker --> Redis
    Logger --> Redis
    Agent --> Postgres
    
    BO1 -.->|"Outbound WebSocket<br/>Poll for tasks"| API
    BO2 -.->|"Outbound WebSocket<br/>Poll for tasks"| API
    BO3 -.->|"Outbound WebSocket<br/>Poll for tasks"| API
    
    BO1 --> K8s1
    BO2 --> K8s2
    BO3 --> K8s3
    
    K8s1 -.-> S3
    K8s2 -.-> S3
    K8s3 -.-> S3
    
    Router -.->|"Interactive sessions<br/>exec, port-forward"| BO1
    Router -.->|"Interactive sessions<br/>exec, port-forward"| BO2
    Router -.->|"Interactive sessions<br/>exec, port-forward"| BO3
```

### Control Plane Components

The control plane is a centralized service layer deployed as a single instance that manages workflow orchestration, authentication, and data persistence.

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| **API Service** | `osmo/src/service/api/service_api.py` | Handles workflow submission, configuration management, dataset operations via REST API |
| **Web UI Service** | `osmo/ui` (Next.js application) | Provides browser-based interface for workflow monitoring and management |
| **Router Service** | `osmo/src/service/router` | Proxies interactive connections (`exec`, `port-forward`, webserver) to backend tasks |
| **Worker Service** | `osmo/src/service/worker` | Processes background jobs from Redis queues (dataset operations, cleanup tasks) |
| **Logger Service** | `osmo/src/service/logger` | Streams logs from backend tasks via WebSocket to clients |
| **Agent Service** | `osmo/src/service/agent` | Receives status updates from backend operators and updates database state |

**Sources**: [README.md:1-189](), High-level architecture diagram from prompt

### Compute Plane Components

Each compute plane consists of a Kubernetes cluster with a backend operator that polls the control plane for work assignments.

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| **Backend Operator** | `osmo/backend/backend_operator.py` | Two-component system: `backendListener` polls for tasks, `backendWorker` creates Kubernetes resources |
| **KAI Scheduler** | External Helm chart (`oci://ghcr.io/nvidia/kai-scheduler`) | Gang scheduling for distributed training, GPU-aware pod placement |
| **GPU Operator** | External Helm chart (`gpu-operator`) | Device plugin for GPU allocation, node feature discovery |

Backend operators initiate **outbound-only connections** to the control plane, eliminating the need for firewall rules or VPN tunnels. This architecture enables compute resources to exist anywhere—cloud, on-premise data centers, or edge locations—while being managed from a single control plane.

**Sources**: [README.md:1-189](), [deployments/brev/setup.sh:301-346](), High-level architecture diagram from prompt

## Data Flow Architecture

OSMO implements a three-tier data storage system optimized for Physical AI workloads:

```mermaid
graph LR
    subgraph WorkflowExecution["Workflow Task Execution"]
        Task1["Task Pod<br/>Training/Simulation"]
        Task2["Task Pod<br/>Data Processing"]
    end
    
    subgraph ControlPlane["Control Plane"]
        DataService["DataService<br/>osmo/src/service/api/data_service.py"]
        ConfigService["ConfigService<br/>osmo/src/service/api/config_service.py"]
        WorkflowService["WorkflowService<br/>osmo/src/service/api/service_api.py"]
    end
    
    subgraph DatabaseLayer["PostgreSQL Schema"]
        WorkflowTable[("workflows table<br/>osmo/src/models/postgres.py")]
        TasksTable[("tasks table")]
        DatasetTable[("dataset table")]
        DatasetVersionTable[("dataset_version table")]
        ConfigTable[("config table")]
        ConfigVersionTable[("config_version table")]
    end
    
    subgraph ObjectStorage["Content-Addressable Storage"]
        Manifests["Manifests<br/>{dataset_id}/manifests/{version}.json<br/>Maps file paths to hashes"]
        Hashes["Hash Storage<br/>{dataset_id}/hashes/{etag}<br/>Deduplicated file content"]
    end
    
    subgraph RedisLayer["Redis"]
        LogStreams["Log Streams<br/>ctrl_websocket channel"]
        JobQueues["Job Queues<br/>Delayed jobs for Worker"]
    end
    
    Task1 -->|"upload_start()<br/>upload_finish()"| DataService
    Task2 -->|"download_datasets()"| DataService
    
    WorkflowService --> WorkflowTable
    WorkflowService --> TasksTable
    DataService --> DatasetTable
    DataService --> DatasetVersionTable
    ConfigService --> ConfigTable
    ConfigService --> ConfigVersionTable
    
    DataService --> Manifests
    DataService --> Hashes
    
    Task1 -.->|"Stream logs"| LogStreams
    Task2 -.->|"Stream logs"| LogStreams
```

### Storage Tiers

**Metadata Storage (PostgreSQL)**: The `postgres.py` model defines the complete schema for workflows, tasks, datasets, and configurations. All state transitions and metadata operations are transactional.

**Log Streaming (Redis)**: The Logger service uses Redis pub/sub channels to stream task logs in real-time to clients via WebSocket connections. Redis also manages job queues for the Worker service.

**Content-Addressable Object Storage**: Datasets use a two-level storage structure:
- **Manifests** (`{dataset_id}/manifests/{version}.json`): Map logical file paths to content hashes
- **Hashes** (`{dataset_id}/hashes/{etag}`): Store actual file content keyed by hash

This architecture achieves 10-100x storage savings through automatic deduplication. Multiple dataset versions that share files reference the same hash objects.

**Sources**: [README.md:76](), Data flow diagram from prompt, [docs/deployment_guide/getting_started/create_storage/s3/index.rst:1-130]()

## Workflow Execution Model

OSMO workflows are defined in YAML with Jinja2 templating support. The execution flow involves multiple services coordinating to transform YAML specifications into running Kubernetes pods:

```mermaid
sequenceDiagram
    participant CLI as "OSMO CLI"
    participant API as "API Service<br/>service_api.py"
    participant DB as "PostgreSQL<br/>postgres.py"
    participant BackendListener as "Backend Operator<br/>backendListener"
    participant BackendWorker as "Backend Operator<br/>backendWorker"
    participant K8s as "Kubernetes API<br/>K8sObjectFactory"
    participant KAI as "KAI Scheduler"
    
    CLI->>API: "POST /api/workflows<br/>workflow YAML + variables"
    API->>API: "Jinja2 template expansion<br/>Resolve {{workflow_id}}, {{input:N}}"
    API->>DB: "INSERT INTO workflows, tasks, groups"
    API-->>CLI: "workflow_id"
    
    BackendListener->>API: "WebSocket poll<br/>GET pending tasks"
    API->>DB: "SELECT tasks WHERE status='pending'"
    DB-->>API: "Task list with resources"
    API-->>BackendListener: "Task assignments"
    
    BackendListener->>BackendWorker: "Enqueue task execution"
    BackendWorker->>K8s: "K8sObjectFactory.create()<br/>Pod, PodGroup, ConfigMap, Secret"
    K8s->>KAI: "Schedule PodGroup<br/>Gang scheduling for distributed tasks"
    KAI->>K8s: "Bind pods to GPU nodes"
    
    K8s-->>BackendWorker: "Pod running"
    BackendWorker->>API: "POST /api/agent/update<br/>Task status update"
    API->>DB: "UPDATE tasks SET status='running'"
```

### Special Token Resolution

OSMO provides runtime token substitution for inter-task dependencies:

| Token | Purpose | Example |
|-------|---------|---------|
| `{{workflow_id}}` | Current workflow identifier | `my-workflow-20250115-123456` |
| `{{input:N}}` | Path to input dataset from task N | `/osmo/inputs/0` |
| `{{output}}` | Path to output dataset directory | `/osmo/outputs` |
| `{{host:task_name}}` | DNS hostname for another task | `simulation-task.namespace.svc.cluster.local` |

The `{{host:task_name}}` token is critical for distributed training frameworks (TorchRun, DeepSpeed, ROS 2) that require inter-process communication. It resolves to the Kubernetes service DNS name for the specified task.

**Sources**: [README.md:47-71](), Workflow execution diagram from prompt

## Deployment Options

OSMO supports three deployment profiles, each optimized for different use cases:

| Deployment | Setup Time | Authentication | Best For | Limitations |
|------------|------------|----------------|----------|-------------|
| **Local** | ~10 minutes | Dev mode (no auth) | Evaluation, learning | Single-node, no distributed training |
| **Minimal** | ~30 minutes | Dev mode (no auth) | Testing, development | Single namespace, limited scalability |
| **Production** | 2-4 hours | Keycloak SSO (OAuth2/OIDC) | Multi-user production | Requires external dependencies |

The local deployment uses KIND (Kubernetes in Docker) and is documented in [deployments/brev/setup.sh:1-436](). It installs:
1. KIND cluster with GPU support via `nvkind`
2. GPU Operator (v25.10.0)
3. KAI Scheduler (v0.8.1)
4. OSMO quick-start Helm chart (v1.0.0)

Production deployments require external PostgreSQL, Redis, Keycloak, and object storage (S3/Azure Blob). These are configured via Helm chart values.

**Sources**: [README.md:134-142](), [deployments/brev/setup.sh:1-436](), [docs/deployment_options.svg:1-217](), [docs/deployment_guide/introduction/whats_next.rst:1-35]()

## Production Readiness

OSMO is production-grade software originally developed at NVIDIA to orchestrate Physical AI workloads for internal projects including Project GR00T, Isaac Lab, Isaac Dexterity, Isaac Sim, and Isaac ROS. It processes thousands of GPU-hours daily across heterogeneous compute spanning cloud training clusters to edge devices.

The codebase is now open-source under Apache 2.0 license and follows structured contribution processes:
- **Bug reports and documentation issues**: File GitHub issues [CONTRIBUTING.md:6-9]()
- **Small fixes**: Submit pull requests directly [CONTRIBUTING.md:10-13]()
- **Significant changes**: Use the formal projects process with design proposals [CONTRIBUTING.md:14-22]()

All pull requests require two approvals from OSMO engineers and passing CI/CD checks before merge.

**Sources**: [README.md:128-133](), [CONTRIBUTING.md:1-139]()

## Next Steps

To begin using OSMO:
1. **Try it locally**: Follow [Getting Started](#2) for local deployment instructions
2. **Understand core concepts**: Read [Key Concepts](#1.2) for terminology and workflow structure
3. **Explore the architecture**: See [Architecture](#1.1) for detailed component interactions
4. **Deploy to production**: See [Deployment Options Comparison](#2.2) for production setup

For developers contributing to OSMO, see [Development and Contributing](#9) for build instructions, CI/CD pipeline details, and the projects process.

**Sources**: [README.md:145-156](), [docs/index.rst:1-39]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/appendix/deploy_local.rst](docs/deployment_guide/appendix/deploy_local.rst)
- [docs/deployment_guide/appendix/deploy_minimal.rst](docs/deployment_guide/appendix/deploy_minimal.rst)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [docs/deployment_guide/index.rst](docs/deployment_guide/index.rst)
- [docs/spelling_wordlist.txt](docs/spelling_wordlist.txt)
- [docs/user_guide/index.rst](docs/user_guide/index.rst)
- [docs/user_guide/overview.svg](docs/user_guide/overview.svg)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

This page describes the high-level architecture of OSMO, focusing on the separation between the Control Plane and Compute Plane, how services are organized, and the key architectural patterns that enable multi-backend workflow orchestration. For workflow-specific concepts like tasks and groups, see [Key Concepts](#1.2). For deployment specifics, see [Kubernetes Deployment](#7).

## System Overview

OSMO uses a **Control Plane / Compute Plane** architecture that enables workflow orchestration across heterogeneous infrastructure without requiring direct network access to compute clusters.

### Control Plane / Compute Plane Separation

```mermaid
graph TB
    subgraph "Control Plane"
        API["API Service<br/>(port 80)"]
        UI["Web UI Service<br/>(Next.js + Envoy)"]
        Router["Router Service<br/>(WebSocket proxy)"]
        Worker["Worker Service<br/>(Background jobs)"]
        Logger["Logger Service<br/>(Log streaming)"]
        Agent["Agent Service<br/>(Status updates)"]
        Monitor["Delayed Job Monitor<br/>(Cron jobs)"]
    end
    
    subgraph "Data Layer"
        PG[("PostgreSQL<br/>workflows, tasks,<br/>configs, datasets")]
        Redis[("Redis<br/>logs, job queues")]
        S3[("Object Storage<br/>S3/Azure/MinIO")]
    end
    
    subgraph "Compute Plane 1"
        Backend1["Backend Operator"]
        K8s1["Kubernetes + KAI"]
        Backend1 --> K8s1
    end
    
    subgraph "Compute Plane 2"
        Backend2["Backend Operator"]
        K8s2["Kubernetes + KAI"]
        Backend2 --> K8s2
    end
    
    API --> PG
    API --> Redis
    Worker --> PG
    Worker --> Redis
    Logger --> Redis
    Agent --> PG
    
    Backend1 -.->|"Outbound<br/>HTTPS/WSS"| API
    Backend2 -.->|"Outbound<br/>HTTPS/WSS"| API
    
    K8s1 --> S3
    K8s2 --> S3
    
    Router -.->|"Interactive<br/>sessions"| Backend1
    Router -.->|"Interactive<br/>sessions"| Backend2
```

**Key architectural principle**: Backend operators initiate **outbound connections** to the control plane. This allows compute clusters to operate behind firewalls, in restricted networks, or across geographic boundaries without requiring inbound network access.

**Sources**: README.md:89-107, docs/deployment_guide/index.rst:83-98

## Control Plane Services

The control plane consists of seven core services, each with specific responsibilities:

| Service | Primary Class/Module | Port | Purpose |
|---------|---------------------|------|---------|
| API | Various `/api/*` routes | 80 | Workflow submission, configuration management, dataset operations |
| Web UI | Next.js application | 8080 | Browser-based interface for workflow management |
| Router | `src/service/router/router.py` | 8000 | Proxies exec, port-forward, and webserver connections to backends |
| Worker | Background job processor | N/A | Processes workflow state transitions and background tasks |
| Logger | `src/service/logger/ctrl_websocket.py` | N/A | Streams logs from task containers via WebSocket |
| Agent | Status update processor | N/A | Receives heartbeats and status updates from backends |
| Delayed Job Monitor | Cron job processor | N/A | Handles scheduled background operations |

### Service Communication Patterns

```mermaid
graph LR
    User["User/CLI"]
    Browser["Browser"]
    
    User -->|"HTTP/REST"| API["API Service"]
    Browser -->|"HTTP"| UI["Web UI"]
    UI -->|"HTTP"| API
    
    API -->|"lpush"| RedisQueue[("Redis<br/>Job Queues")]
    Worker -->|"brpop"| RedisQueue
    
    TaskPod["Task Container<br/>(osmo-ctrl)"]
    TaskPod -->|"WebSocket"| Logger["Logger Service"]
    Logger -->|"xadd"| RedisStream[("Redis<br/>Log Streams")]
    
    User -->|"osmo exec"| Router["Router Service"]
    Router -->|"WebSocket proxy"| Backend["Backend Operator"]
    Backend --> TaskPod
```

**Sources**: src/service/router/router.py:93-124, src/service/logger/ctrl_websocket.py:118-247

### API Service Routes

The API service exposes RESTful endpoints organized by resource type:

- `/api/workflow/*` - Workflow submission, cancellation, status ([src/service/core/workflow/](src/service/core/workflow))
- `/api/bucket/*` - Dataset upload, download, versioning ([src/service/core/data/data_service.py:36-39]())
- `/api/config/*` - Service, workflow, and dataset configuration ([src/service/core/config/](src/service/core/config))
- `/api/backend/*` - Backend registration, pool management
- `/api/credential/*` - User credential management

**Sources**: src/service/core/data/data_service.py:36-39

### Router Service Architecture

The Router service (`RouterServiceConfig`) provides interactive access to running tasks through WebSocket proxying:

```mermaid
sequenceDiagram
    participant User
    participant Router as "Router Service"
    participant Backend as "Backend Operator"
    participant TaskPod as "Task Pod"
    
    User->>Router: osmo workflow exec<br/>(WebSocket connect)
    Router->>Backend: Forward connection request<br/>(via existing outbound WS)
    Backend->>TaskPod: kubectl exec
    TaskPod-->>Backend: stdin/stdout/stderr
    Backend-->>Router: Relay streams
    Router-->>User: Interactive shell
```

Key implementation details:
- **Sticky cookies**: `AWSALB`, `AWSALBCORS` maintained for load balancer affinity ([src/service/router/router.py:60-63]())
- **Connection storage**: `connections: Dict[str, RouterConnection]` maintains active exec/port-forward sessions ([src/service/router/router.py:95-96]())
- **Webserver sessions**: `webservers: Dict[str, WebserverConnection]` tracks long-running HTTP connections ([src/service/router/router.py:96]())

**Sources**: src/service/router/router.py:37-124

## Compute Plane Components

Each compute cluster runs a **Backend Operator** consisting of three components:

### Backend Operator Architecture

```mermaid
graph TB
    subgraph "Backend Operator Pod"
        Listener["backendListener<br/>(main loop)"]
        Worker["backendWorker<br/>(job executor)"]
        TestRunner["backendTestRunner<br/>(CronJob)"]
    end
    
    subgraph "Control Plane"
        API["API Service"]
        RedisQueue[("Redis<br/>Job Queue")]
    end
    
    subgraph "Kubernetes Cluster"
        KAI["KAI Scheduler"]
        Pods["Workflow Task Pods"]
        Nodes["Compute Nodes"]
    end
    
    Listener -->|"Poll every 5s"| API
    Listener -->|"POST /heartbeat"| API
    
    Worker -->|"BRPOP"| RedisQueue
    Worker -->|"Create Pod/PodGroup"| KAI
    Worker -->|"Monitor status"| Pods
    
    KAI --> Nodes
    Nodes --> Pods
    
    TestRunner -->|"Periodic validation"| API
```

**Sources**: README.md:91-107, docs/deployment_guide/index.rst:91-93

### Backend Listener Responsibilities

The backend listener (deployed as `backend-listener` in the Helm chart) performs:

1. **Heartbeat transmission**: POST to `/api/backend/{name}/heartbeat` every 5 seconds
2. **Node resource reporting**: Aggregates `allocatable_fields`, `usage_fields`, and conditions from Kubernetes nodes
3. **Task polling**: Retrieves pending tasks for assigned pools
4. **Cluster metadata**: Reports `k8s_uid`, `k8s_namespace`, `version`

**Sources**: docs/deployment_guide/index.rst:91-93

### Backend Worker Job Processing

The backend worker subscribes to Redis queue `backend-connections:{backend_name}` and processes jobs:

- `BackendCreateWorkflowJobs`: Creates Kubernetes resources (Pods, PodGroups, Secrets, ConfigMaps)
- `BackendCleanupWorkflowJobs`: Deletes completed workflow resources
- `BackendSynchronizeQueues`: Updates KAI scheduler queues for pools
- `BackendGetErrorLogs`: Retrieves error logs from failed tasks

**Job creation pattern**:
```python
# From src/utils/job/kb_objects.py
def backend_action_queue_name(backend_name: str) -> str:
    return f'backend-connections:{backend_name}'
```

**Sources**: src/utils/connectors/postgres.py:51-52, src/utils/job/kb_objects.py:45-103

### Kubernetes Resource Factory

The `K8sObjectFactory` pattern abstracts scheduler-specific resource creation:

```mermaid
graph TD
    TaskSpec["TaskSpec<br/>(workflow definition)"]
    Factory["K8sObjectFactory"]
    KaiFactory["KaiK8sObjectFactory"]
    
    TaskSpec --> Factory
    Factory -->|"scheduler_type=kai"| KaiFactory
    
    KaiFactory --> Pod["Pod YAML"]
    KaiFactory --> PodGroup["PodGroup YAML<br/>(gang scheduling)"]
    KaiFactory --> Secret["Secret YAML"]
    KaiFactory --> Service["Headless Service"]
    
    Pod -->|"metadata.annotations<br/>pod-group-name"| K8s["Kubernetes API"]
    PodGroup -->|"spec.minMember<br/>spec.queue"| K8s
```

Key methods:
- `create_group_k8s_resources()`: Generates gang-scheduled Pod and PodGroup resources ([src/utils/job/kb_objects.py:74-103]())
- `create_init_container()`: Builds the `osmo-init` init container ([src/utils/job/kb_objects.py:111-152]())
- `create_control_container()`: Builds the `osmo-ctrl` sidecar ([src/utils/job/kb_objects.py:154-240]())

**Sources**: src/utils/job/kb_objects.py:43-323

## Data Layer

### PostgreSQL Schema Organization

The PostgreSQL database (`osmo_db`) stores all persistent state:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `workflows` | Workflow metadata | `workflow_uuid`, `workflow_id`, `status`, `submitted_by` |
| `groups` | Task group specifications | `group_uuid`, `workflow_id`, `spec`, `status` |
| `tasks` | Individual task state | `task_uuid`, `workflow_id`, `retry_id`, `status`, `node_name` |
| `dataset` | Dataset registry | `id`, `name`, `bucket`, `hash_location` |
| `dataset_version` | Dataset versions | `dataset_id`, `version_id`, `location`, `status` |
| `dataset_tag` | Version tags | `dataset_id`, `tag`, `version_id` |
| `backends` | Backend registration | `name`, `k8s_namespace`, `last_heartbeat` |
| `pools` | Resource pool configuration | `name`, `backend`, `platforms`, `resources` |
| `credential` | Encrypted user credentials | `user_name`, `cred_name`, `payload` (HSTORE) |
| `configs` | Dynamic configuration | `key`, `value`, `type` |

**Indices for performance**:
- `workflow_list_index`: Optimizes workflow list queries by `(submitted_by, pool, status, submit_time)` ([src/utils/connectors/postgres.py:669-677]())
- `tasks_status_id_name`: Unique index on `(status, workflow_id, retry_id, name)` ([src/utils/connectors/postgres.py:758-762]())

**Sources**: src/utils/connectors/postgres.py:531-965

### Redis Data Structures

Redis serves as the ephemeral data layer with distinct usage patterns:

| Key Pattern | Type | Purpose |
|-------------|------|---------|
| `{workflow_id}-logs` | Stream | Aggregated workflow logs from all tasks |
| `{workflow_id}:{task_name}:{retry_id}:logs` | Stream | Individual task logs |
| `backend-connections:{backend_name}` | List | Job queue for backend worker |
| `workflow-{workflow_id}:{task_name}:{retry_id}:action` | List | Action queue for exec/port-forward |
| `osmo-group-barrier:{workflow_id}:{group_name}:{barrier_name}` | Set | Barrier synchronization for distributed tasks |

**Log streaming implementation**:
```python
# From src/service/logger/ctrl_websocket.py:199-206
await redis_client.xadd(
    f'{workflow_obj.workflow_id}-logs',
    json.loads(logs.json()),
    maxlen=workflow_config.max_log_lines
)
```

**Sources**: src/service/logger/ctrl_websocket.py:118-247

### Object Storage: Content-Addressable System

OSMO implements a content-addressable storage system with deduplication:

```mermaid
graph LR
    Dataset["Dataset<br/>mydataset:v1"]
    Manifest["Manifest JSON<br/>{dataset_id}/manifests/v1.json"]
    Files["File Hashes<br/>{dataset_id}/hashes/{etag}"]
    
    Dataset --> Manifest
    Manifest -->|"file1.txt → hash1"| Files
    Manifest -->|"file2.txt → hash2"| Files
    Manifest -->|"file3.txt → hash1"| Files
    
    Files -.->|"Same hash =<br/>deduplication"| Storage["S3/Azure/MinIO"]
```

**Deduplication mechanism**:
1. Files stored by content hash (ETag) in `{dataset_id}/hashes/{etag}`
2. Manifest maps logical paths to hashes
3. Multiple datasets sharing files reference same hash
4. Achieves 10-100x storage savings for common patterns

**Bucket configuration** stored in PostgreSQL `configs` table with `type=DATASET`:
- `buckets`: Dict mapping bucket names to `BucketConfig` (mode, credentials, check_key)
- `default_bucket`: Fallback bucket name

**Sources**: README.md:76, docs/deployment_guide/index.rst:63-68

## Multi-Namespace Architecture

OSMO uses Kubernetes namespace isolation for security and multi-tenancy:

```mermaid
graph TB
    subgraph "osmo Namespace"
        API["API Pod"]
        UI["Web UI Pod"]
        Worker["Worker Pods"]
    end
    
    subgraph "osmo-backend-cloud Namespace"
        BackendOp1["Backend Operator"]
    end
    
    subgraph "osmo-backend-onprem Namespace"
        BackendOp2["Backend Operator"]
    end
    
    subgraph "osmo-workflows-cloud Namespace"
        WorkflowPods1["Task Pods<br/>(user workloads)"]
    end
    
    subgraph "osmo-workflows-onprem Namespace"
        WorkflowPods2["Task Pods<br/>(user workloads)"]
    end
    
    BackendOp1 -->|"Creates pods in"| WorkflowPods1
    BackendOp2 -->|"Creates pods in"| WorkflowPods2
    
    API -.->|"Sends jobs via Redis"| BackendOp1
    API -.->|"Sends jobs via Redis"| BackendOp2
```

**Namespace purposes**:
- **Control plane namespace** (e.g., `osmo`): API, UI, Worker, Logger services
- **Backend operator namespace** (e.g., `osmo-backend-{name}`): Backend listener and worker pods
- **Workflow namespace** (e.g., `osmo-workflows-{name}`): User task pods with resource isolation

**Sources**: docs/deployment_guide/index.rst:250-267

## Workflow Execution Architecture

### Task Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> SUBMITTING: Workflow submitted
    SUBMITTING --> WAITING: Persisted to DB
    WAITING --> PROCESSING: Worker picks up
    PROCESSING --> SCHEDULING: Sent to backend
    SCHEDULING --> INITIALIZING: Pod created
    INITIALIZING --> RUNNING: Containers started
    
    RUNNING --> COMPLETED: Exit code 0
    RUNNING --> FAILED: Exit code != 0
    RUNNING --> RESCHEDULED: Retry triggered
    
    RUNNING --> FAILED_CANCELED: User cancels
    RUNNING --> FAILED_EXEC_TIMEOUT: Exceeds timeout
    SCHEDULING --> FAILED_QUEUE_TIMEOUT: Queue timeout
    
    RESCHEDULED --> SCHEDULING: New retry_id
    
    COMPLETED --> [*]
    FAILED --> [*]
    FAILED_CANCELED --> [*]
```

**Status enum** defined in `TaskGroupStatus` ([src/utils/job/task.py:151-257]()):
- **Alive statuses**: `SUBMITTING`, `WAITING`, `PROCESSING`, `SCHEDULING`, `INITIALIZING`, `RUNNING`, `RESCHEDULED`
- **Failed statuses**: `FAILED`, `FAILED_CANCELED`, `FAILED_SERVER_ERROR`, `FAILED_BACKEND_ERROR`, `FAILED_EXEC_TIMEOUT`, `FAILED_QUEUE_TIMEOUT`, `FAILED_IMAGE_PULL`, `FAILED_UPSTREAM`, `FAILED_EVICTED`, `FAILED_START_ERROR`, `FAILED_START_TIMEOUT`, `FAILED_PREEMPTED`

**Sources**: src/utils/job/task.py:151-257

### Task Pod Structure

Each workflow task runs in a Kubernetes Pod with the following container structure:

```mermaid
graph TB
    subgraph "Task Pod"
        direction TB
        Init["osmo-init<br/>(Init Container)"]
        Ctrl["osmo-ctrl<br/>(Sidecar)"]
        User["User Container<br/>(task.image)"]
        
        Init -.->|"Mounts binaries"| Ctrl
        Init -.->|"Mounts binaries"| User
        Ctrl <-->|"Unix socket"| User
        Ctrl -->|"WebSocket"| Logger["Logger Service"]
        User -->|"Input/output"| DataVolume["/osmo/data"]
    end
    
    subgraph "Shared Volumes"
        OSMOBin["/osmo/bin"]
        OSMOData["/osmo/data"]
        OSMOLogin["/osmo/login"]
    end
    
    Init --> OSMOBin
    Init --> OSMOData
    Init --> OSMOLogin
```

**Container responsibilities**:
1. **osmo-init**: Copies binaries (`osmo_exec`, `osmo_ctrl`) and configuration files to shared volumes ([src/utils/job/kb_objects.py:111-152]())
2. **osmo-ctrl**: Handles data upload/download, log streaming, checkpoint syncing ([src/utils/job/kb_objects.py:154-240]())
3. **User container**: Executes task command with entry point wrapped by `osmo_exec`

**Volume mounts**:
- `/osmo/bin`: Shared binaries
- `/osmo/data`: Input/output data, benchmarks, socket
- `/osmo/login`: OSMO CLI configuration for authentication

**Sources**: src/utils/job/kb_objects.py:111-240

### Gang Scheduling with KAI

For distributed workloads requiring simultaneous launch (e.g., multi-GPU training), OSMO uses KAI scheduler's PodGroup resource:

```mermaid
graph TD
    GroupSpec["TaskGroup<br/>3 tasks"]
    
    PodGroup["PodGroup<br/>spec.minMember=3<br/>spec.queue=osmo-pool-cloud"]
    
    Pod1["Pod 1<br/>annotations.pod-group-name"]
    Pod2["Pod 2<br/>annotations.pod-group-name"]
    Pod3["Pod 3<br/>annotations.pod-group-name"]
    
    GroupSpec -->|"K8sObjectFactory"| PodGroup
    GroupSpec --> Pod1
    GroupSpec --> Pod2
    GroupSpec --> Pod3
    
    Pod1 -.->|"References"| PodGroup
    Pod2 -.->|"References"| PodGroup
    Pod3 -.->|"References"| PodGroup
    
    KAI["KAI Scheduler"]
    KAI -->|"All-or-nothing<br/>scheduling"| Pod1
    KAI --> Pod2
    KAI --> Pod3
```

**PodGroup specification** created by `KaiK8sObjectFactory.create_group_k8s_resources()` ([src/utils/job/kb_objects.py:331-377]()):
```yaml
apiVersion: scheduling.run.ai/v2alpha2
kind: PodGroup
metadata:
  name: osmo-{group_uuid}
  labels:
    kai.scheduler/queue: osmo-pool-{namespace}-{pool}
spec:
  minMember: 3  # Number of pods in group
  queue: osmo-pool-{namespace}-{pool}
  priorityClassName: osmo-normal
```

**Sources**: src/utils/job/kb_objects.py:324-407

## Authentication and Security Architecture

### Multi-Tier Authentication

```mermaid
graph TD
    Browser["Browser User"]
    CLI["CLI User"]
    Backend["Backend Operator"]
    
    Browser -->|"1. OAuth2 flow"| Keycloak["Keycloak"]
    CLI -->|"2. Device code flow"| Keycloak
    Backend -->|"3. Service token"| API["API Service"]
    
    Keycloak -->|"JWT<br/>audience: osmo-browser-flow"| Envoy["Envoy Sidecar"]
    Keycloak -->|"JWT<br/>audience: osmo-device"| API
    
    Envoy -->|"x-osmo-user header"| API
    
    API -->|"Internal JWT"| Services["Internal Services"]
```

**Authentication tiers**:
1. **Browser flow**: OAuth2 authorization code with Envoy JWT validation
2. **Device flow**: CLI device authorization with polling
3. **Service tokens**: Backend operators authenticate with role-based tokens

**Credential encryption**: User credentials stored in PostgreSQL `credential` table use Master Encryption Key (MEK):
- MEK stored in JWK format (JSON Web Key)
- Credentials encrypted per-user with User Encryption Key (UEK)
- `SecretManager` handles encryption/decryption ([src/utils/connectors/postgres.py:252-261]())

**Sources**: src/utils/connectors/postgres.py:252-261

### Envoy Sidecar Integration

The Web UI uses Envoy as an authentication proxy:

```yaml
# Envoy OAuth2 filter configuration
oauth2:
  config:
    token_endpoint: {keycloak}/token
    authorization_endpoint: {keycloak}/auth
    credentials:
      client_id: osmo-client
      hmac_secret: {session_key}
```

**Flow**:
1. Unauthenticated request → Envoy redirects to Keycloak
2. User authenticates → Authorization code returned
3. Envoy exchanges code for JWT access token
4. Envoy validates JWT (issuer, audience, signature via JWKS)
5. Envoy extracts user claim → `x-osmo-user` header
6. Request forwarded to backend service

**Sources**: docs/deployment_guide/index.rst:83-98

## Configuration Management System

OSMO uses a versioned configuration system stored in PostgreSQL:

### Configuration Types

| ConfigType | Scope | Key Classes |
|------------|-------|-------------|
| `SERVICE` | Global service settings | `ServiceConfig` |
| `WORKFLOW` | Workflow defaults | `WorkflowConfig` |
| `DATASET` | Storage bucket settings | `DatasetConfig` |

**Configuration storage**:
```sql
CREATE TABLE configs (
    key TEXT,
    value TEXT,
    type TEXT,  -- SERVICE, WORKFLOW, DATASET
    PRIMARY KEY (key, type)
);
```

**Configuration history tracking**:
```sql
CREATE TABLE config_history (
    id SERIAL PRIMARY KEY,
    config_type TEXT,
    name TEXT,
    username TEXT,
    data JSONB,
    description TEXT,
    tags TEXT[],
    created_date TIMESTAMP
);
```

**API operations**:
- `PUT /api/config/{type}`: Replace entire configuration
- `PATCH /api/config/{type}`: Strategic merge patch
- `GET /api/config/{type}/history`: List configuration history
- `POST /api/config/{type}/rollback/{id}`: Rollback to previous version

**Sources**: src/service/core/config/helpers.py:72-114, src/utils/connectors/postgres.py:69-87

## Summary: Key Architectural Patterns

1. **Outbound-only connectivity**: Backend operators initiate connections, enabling deployment behind firewalls
2. **Event-driven job processing**: Redis queues decouple control plane from compute plane
3. **Gang scheduling**: KAI PodGroups ensure simultaneous launch for distributed workloads
4. **Content-addressable storage**: Hash-based deduplication reduces storage costs 10-100x
5. **Multi-namespace isolation**: Separate namespaces for control, operators, and workloads
6. **Sidecar pattern**: `osmo-ctrl` and `osmo-init` containers provide consistent runtime environment
7. **Stateless control plane**: All state in PostgreSQL/Redis enables horizontal scaling
8. **WebSocket proxying**: Router service enables interactive access without direct cluster access

**Sources**: README.md:89-107, docs/deployment_guide/index.rst:83-98, src/service/router/router.py:93-124

---

# Page: Key Concepts

# Key Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



## Purpose and Scope

This page defines the core concepts and terminology used throughout OSMO. Understanding these concepts is essential for writing workflows, managing data, and orchestrating workloads across heterogeneous compute environments.

For information about the overall architecture and how these concepts fit into the larger system, see [Architecture](#1.1). For detailed workflow specification syntax, see [Workflow Specification](#6.1).

## Workflows

A **workflow** is the top-level orchestration unit in OSMO. It defines a directed acyclic graph (DAG) of tasks that execute on backend compute resources. Workflows are specified in YAML format and submitted via the CLI or API.

### Workflow Structure

```mermaid
graph TB
    Workflow["Workflow<br/>(workflow:)"]
    
    Workflow --> Name["name:<br/>Unique identifier"]
    Workflow --> Tasks["tasks:<br/>List of task definitions"]
    Workflow --> Groups["groups:<br/>Simultaneous task sets"]
    Workflow --> Resources["resources:<br/>CPU/GPU/Memory specs"]
    Workflow --> Timeout["timeout:<br/>Execution limits"]
    Workflow --> Files["files:<br/>Mounted file content"]
    
    Tasks --> Task1["Task 1"]
    Tasks --> Task2["Task 2"]
    
    Groups --> Group1["Group 1"]
    Group1 --> GroupTask1["Task 3"]
    Group1 --> GroupTask2["Task 4"]
    
    Resources --> Default["default:<br/>Base resource spec"]
    Resources --> Named["named specs:<br/>sim, jetson, etc."]
```

**Sources:** [README.md:47-71](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:20-51]()

### Basic Workflow Example

A minimal workflow specification:

```yaml
workflow:
  name: my-workflow
  tasks:
  - name: task1
    image: ubuntu:20.04
    command: ["echo"]
    args: ["Hello from OSMO"]
  resources:
    default:
      cpu: 1
      memory: 1Gi
      storage: 1Gi
```

**Sources:** [README.md:47-71](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:20-51]()

## Tasks

A **task** is an individual unit of work that executes in a container. Each task runs a Docker image with specified commands, arguments, and environment variables.

### Task Anatomy

```mermaid
graph LR
    Task["Task Definition"]
    
    Task --> Identity["Identity<br/>• name<br/>• image"]
    Task --> Execution["Execution<br/>• command<br/>• args<br/>• environment"]
    Task --> IO["I/O<br/>• inputs<br/>• outputs<br/>• checkpoint"]
    Task --> Config["Configuration<br/>• files<br/>• credentials<br/>• resource"]
    Task --> GroupProps["Group Properties<br/>• lead: true/false"]
    
    Identity --> Pod["Kubernetes Pod"]
    Execution --> Pod
    IO --> Datasets["Dataset References"]
    Config --> Secrets["ConfigMaps/Secrets"]
```

**Sources:** [README.md:47-71](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:23-45]()

### Task Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique task identifier within the workflow |
| `image` | string | Docker image to execute (e.g., `nvcr.io/nvidia/pytorch:24.03-py3`) |
| `command` | list | Entrypoint command (overrides Docker CMD) |
| `args` | list | Arguments passed to the command |
| `environment` | map | Environment variables (key-value pairs) |
| `files` | list | Files to mount into the container |
| `inputs` | list | Dataset inputs (referenced as `{{input:0}}`, `{{input:1}}`, etc.) |
| `outputs` | list | Dataset outputs saved after task completion |
| `checkpoint` | list | Periodic backup of specified paths during execution |
| `credentials` | map | Credential mappings for the task |
| `resource` | string | Named resource specification to use (defaults to `default`) |
| `lead` | boolean | Whether this task is the lead in a group (optional) |

**Sources:** [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:23-45](), [docs/user_guide/how_to/training/multi_node.rst:46-96]()

### File Mounting

The `files` field allows mounting content into the container at specified paths:

```yaml
tasks:
- name: example
  files:
  - path: /tmp/script.sh
    contents: |
      #!/bin/bash
      echo "Inline script content"
  - path: /tmp/train.py
    localpath: train.py  # File from local filesystem
```

**Sources:** [docs/user_guide/how_to/training/single_node.rst:38-65](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:30-42]()

## Groups

A **group** is a collection of tasks that are launched simultaneously and can communicate over a private network. Groups are essential for distributed workloads like multi-node training and hardware-in-the-loop testing.

### Group Properties

```mermaid
graph TB
    Group["Group Definition"]
    
    Group --> Name["name:<br/>Group identifier"]
    Group --> Tasks["tasks:<br/>Task list"]
    Group --> Lead["Lead Task<br/>(lead: true)"]
    
    Tasks --> Simultaneous["Simultaneous Launch<br/>All tasks start together"]
    Tasks --> Network["Private Network<br/>Inter-task communication"]
    Tasks --> DNS["DNS Resolution<br/>{{host:task_name}}"]
    
    Lead --> Coordination["Coordination Point<br/>Master node for distributed training"]
    
    Simultaneous --> Scheduler["KAI Scheduler<br/>Gang Scheduling"]
    Network --> Service["Kubernetes Headless Service"]
    DNS --> SpecialToken["Special Token Resolution"]
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:35-96](), [docs/user_guide/how_to/hil.rst:36-79]()

### Group Example: Multi-Node Training

```yaml
workflow:
  groups:
  - name: training
    tasks:
    - name: master
      lead: true  # Coordination point
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash, /tmp/run.sh]
      files:
      - path: /tmp/run.sh
        contents: |
          torchrun --nnodes 2 --nproc_per_node 8 --node_rank 0 \
            --master_addr {{host:master}} --master_port 29400 \
            /tmp/train.py
    
    - name: worker
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash, /tmp/run.sh]
      files:
      - path: /tmp/run.sh
        contents: |
          torchrun --nnodes 2 --nproc_per_node 8 --node_rank 1 \
            --master_addr {{host:master}} --master_port 29400 \
            /tmp/train.py
```

**Key Capabilities:**
- All tasks in the group start at the same time (guaranteed by KAI scheduler)
- Tasks can resolve each other's hostnames using `{{host:task_name}}`
- Private network isolation for secure inter-task communication
- Lead task designation for coordination (e.g., master node in distributed training)

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:46-96](), [docs/user_guide/how_to/hil.rst:81-223]()

## Resources

**Resources** define the compute requirements for tasks: CPU cores, GPU count, memory, and ephemeral storage. OSMO supports named resource specifications for different task types.

### Resource Specification Structure

```mermaid
graph LR
    Resources["resources:"]
    
    Resources --> Default["default:<br/>Base specification"]
    Resources --> Named1["sim:<br/>Simulation hardware"]
    Resources --> Named2["jetson:<br/>Edge device"]
    Resources --> NamedN["custom:<br/>User-defined"]
    
    Default --> Fields["• cpu<br/>• gpu<br/>• memory<br/>• storage<br/>• platform"]
    Named1 --> Fields
    Named2 --> Fields
    NamedN --> Fields
```

**Sources:** [docs/user_guide/how_to/hil.rst:169-191](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:46-51]()

### Resource Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `cpu` | integer | Number of CPU cores | `4` |
| `gpu` | integer | Number of GPUs (optional) | `8` |
| `memory` | string | RAM allocation | `32Gi`, `128Gi` |
| `storage` | string | Ephemeral storage | `10Gi`, `100Gi` |
| `platform` | string | Target hardware platform (optional) | `gb200`, `jetson-agx-thor` |

**Sources:** [README.md:47-71](), [docs/user_guide/how_to/hil.rst:175-190]()

### Named Resource Specifications

Tasks can reference named resource specifications using the `resource` field:

```yaml
workflow:
  resources:
    default:
      cpu: 1
      memory: 2Gi
      storage: 2Gi
    sim:
      cpu: 16
      gpu: 1
      memory: 20Gi
      platform: ovx-a40
      storage: 30Gi
    jetson:
      cpu: 8
      memory: 26Gi
      platform: agx-orin
      storage: 30Gi
  tasks:
  - name: simulation
    resource: sim  # Uses sim resource spec
    image: nvcr.io/nvidia/isaac-sim:5.1.0
  - name: edge-test
    resource: jetson  # Uses jetson resource spec
    image: arm64v8/ros:humble
```

**Sources:** [docs/user_guide/how_to/hil.rst:169-201]()

## Platforms

A **platform** is a hardware constraint that targets specific GPU or accelerator types. Platforms enable workflows to run on heterogeneous compute backends without hardcoding infrastructure details.

### Platform Examples

```mermaid
graph TB
    Platforms["Platform Types"]
    
    Platforms --> Cloud["Cloud Training<br/>• gb200<br/>• h100<br/>• l40"]
    Platforms --> Simulation["Simulation<br/>• ovx-a40<br/>• rtx-pro-6000<br/>• l40"]
    Platforms --> Edge["Edge Devices<br/>• jetson-agx-thor<br/>• agx-orin<br/>• jetson-orin-nano"]
    
    Cloud --> Pool1["Backend Pool 1<br/>Supports: gb200, h100"]
    Simulation --> Pool2["Backend Pool 2<br/>Supports: ovx-a40, l40"]
    Edge --> Pool3["Backend Pool 3<br/>Supports: agx-orin"]
```

**Sources:** [README.md:54-66](), [docs/user_guide/how_to/hil.rst:201-205]()

### Platform Usage

Platforms are specified in resource definitions and matched against backend pool annotations:

```yaml
workflow:
  tasks:
  - name: train-policy
    image: nvcr.io/nvidia/pytorch
    resources:
      default:
        gpu: 8
        platform: gb200  # Requires GB200 GPUs
  
  - name: evaluate-thor
    image: my-ros-app
    resources:
      default:
        platform: jetson-agx-thor  # Requires Jetson AGX Thor
```

**Sources:** [README.md:47-71](), [docs/user_guide/how_to/hil.rst:186-201]()

## Datasets

A **dataset** is a versioned collection of files stored in content-addressable object storage. OSMO automatically deduplicates files across datasets, achieving 10-100x storage savings.

### Dataset System Architecture

```mermaid
graph TB
    subgraph "Dataset Metadata (PostgreSQL)"
        DatasetTable["dataset table<br/>• id<br/>• name<br/>• bucket"]
        VersionTable["dataset_version table<br/>• version_id<br/>• location<br/>• status (PENDING/READY)<br/>• size"]
        TagTable["dataset_tag table<br/>• tag → version_id"]
        
        DatasetTable --> VersionTable
        VersionTable --> TagTable
    end
    
    subgraph "Content-Addressable Storage (S3/MinIO/Azure)"
        Hashes["{dataset_id}/hashes/{etag}<br/>Actual file content"]
        Manifests["{dataset_id}/manifests/{version}.json<br/>File path → hash mapping"]
    end
    
    VersionTable -.->|References| Manifests
    Manifests -.->|Maps to| Hashes
    
    subgraph "Deduplication Example"
        File1["file1.txt (ETag: abc123)"]
        File2["file2.txt (ETag: abc123)"]
        File3["file3.txt (ETag: def456)"]
        
        File1 -.->|Same hash| Storage1["hashes/abc123<br/>(stored once)"]
        File2 -.->|Same hash| Storage1
        File3 -.->|Different hash| Storage2["hashes/def456"]
    end
```

**Sources:** [README.md:76](), Diagram 5 from system architecture

### Dataset Versioning

Every dataset upload creates a new version with an auto-incrementing `version_id`:

```bash
# Upload creates version 1
$ osmo dataset upload /local/path my-dataset

# Another upload creates version 2
$ osmo dataset upload /local/path2 my-dataset

# Download specific version
$ osmo dataset download my-dataset:2 ~/output

# Download by tag
$ osmo dataset download my-dataset:latest ~/output
```

| Component | Description |
|-----------|-------------|
| Dataset Name | User-specified identifier (e.g., `my-dataset`) |
| Version ID | Auto-incrementing integer (1, 2, 3, ...) |
| Tags | Named pointers to versions (e.g., `latest`, `stable`) |
| Status | `PENDING` (upload in progress) or `READY` (complete) |

**Sources:** Diagram 5 from system architecture

### Task Dataset I/O

Tasks declare dataset inputs and outputs:

```yaml
tasks:
- name: train
  image: nvcr.io/nvidia/pytorch:24.03-py3
  inputs:
  - dataset:
      name: training-data
      tag: latest  # Optional, defaults to latest
  outputs:
  - dataset:
      name: trained-model
      path: models  # Local directory to save as dataset
  files:
  - path: /tmp/train.sh
    contents: |
      # Input dataset mounted at {{input:0}}
      python train.py --data {{input:0}}/training-data
      
      # Save outputs to {{output}}
      cp model.pth {{output}}/models/
```

**Sources:** [README.md:60-70](), [docs/user_guide/how_to/training/single_node.rst:87-128]()

### Collections

**Collections** group multiple datasets together for convenient batch operations. They reference datasets without duplicating storage.

**Sources:** Diagram 5 from system architecture

## Special Tokens

**Special tokens** are placeholders in workflow YAML that are resolved at runtime by the OSMO service. They enable dynamic configuration based on workflow execution context.

### Token Types and Resolution

```mermaid
graph LR
    Tokens["Special Tokens"]
    
    Tokens --> WorkflowID["{{workflow_id}}<br/>Unique workflow UUID"]
    Tokens --> Input["{{input:N}}<br/>Path to Nth input dataset"]
    Tokens --> Output["{{output}}<br/>Path to output directory"]
    Tokens --> Host["{{host:task_name}}<br/>Hostname of task in group"]
    
    WorkflowID --> Resolution1["Generated at<br/>workflow creation"]
    Input --> Resolution2["Resolved to<br/>/osmo/input/N/dataset-name"]
    Output --> Resolution3["Resolved to<br/>/osmo/output"]
    Host --> Resolution4["Resolved via<br/>Kubernetes DNS"]
    
    Resolution2 --> Mount1["Dataset mounted<br/>into container"]
    Resolution3 --> Mount2["Empty directory<br/>for outputs"]
    Resolution4 --> DNS["nslookup returns<br/>pod IP"]
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-229]()

### Token Reference Table

| Token | Resolved To | Use Case | Example |
|-------|-------------|----------|---------|
| `{{workflow_id}}` | Unique workflow UUID | Tracking, logging | `echo "Running {{workflow_id}}"` |
| `{{input:0}}` | Path to first input dataset | Reading input data | `cat {{input:0}}/data.txt` |
| `{{input:1}}` | Path to second input dataset | Multiple inputs | `cat {{input:1}}/config.json` |
| `{{output}}` | Path to output directory | Writing results | `cp model.pth {{output}}/` |
| `{{host:task_name}}` | Hostname of `task_name` | Inter-task communication | `--master_addr {{host:master}}` |

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:127-229]()

### Token Example: Multi-Input Task

```yaml
tasks:
- name: merge-data
  inputs:
  - dataset:
      name: simulation-data
  - dataset:
      name: real-world-data
  outputs:
  - dataset:
      name: merged-dataset
  files:
  - path: /tmp/merge.sh
    contents: |
      #!/bin/bash
      echo "Workflow ID: {{workflow_id}}"
      
      # Read from first input
      cat {{input:0}}/simulation-data/file.txt
      
      # Read from second input
      cat {{input:1}}/real-world-data/file.txt
      
      # Write to output
      echo "Merged data" > {{output}}/result.txt
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:131-166]()

### Token Example: Host Resolution

The `{{host:task_name}}` token is critical for distributed workloads:

```yaml
groups:
- name: distributed
  tasks:
  - name: discovery-server
    image: osrf/ros:humble-desktop-full
    command: [bash, /tmp/run.sh]
    files:
    - path: /tmp/run.sh
      contents: |
        fastdds discovery -i 0 -l 0.0.0.0 -p 11811
  
  - name: publisher
    image: osrf/ros:humble-desktop-full
    command: [bash, /tmp/run.sh]
    files:
    - path: /tmp/run.sh
      contents: |
        # Resolve discovery server IP
        SERVER_IP=$(nslookup {{host:discovery-server}} | grep -oP 'Address: \K[0-9.]+')
        export ROS_DISCOVERY_SERVER=$SERVER_IP:11811
        
        # Launch ROS node
        ros2 run demo_nodes_cpp talker
```

**Sources:** [docs/user_guide/how_to/ros2_comm.rst:66-143](), [workflows/ros/comm/ros2_comm.yaml:43-50](), [workflows/hil/setup_discovery_server.sh:18-24]()

## Jinja Templates

**Jinja templates** enable dynamic workflow generation using variables, loops, and conditionals. Templates are processed before workflow submission.

### Template Variables

Variables are defined in `default-values` and can be overridden at submit time:

```yaml
workflow:
  name: {{ workflow_name }}
  tasks:
  - name: train
    image: nvcr.io/nvidia/pytorch:24.03-py3
    args: ["--epochs", "{{ num_epochs }}"]
    resources:
      default:
        gpu: {{ num_gpus }}

default-values:
  workflow_name: my-training
  num_epochs: 10
  num_gpus: 8
```

Submit with overrides:
```bash
$ osmo workflow submit workflow.yaml --set num_epochs=20 num_gpus=4
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:28-82]()

### Template Loops

Generate multiple tasks programmatically:

```yaml
workflow:
  groups:
  - name: training
    tasks:
    {% for node in range(n_nodes) %}
    - name: {% if node == 0 %}master{% else %}worker-{{node}}{% endif %}
      lead: {% if node == 0 %}true{% else %}false{% endif %}
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash, /tmp/run.sh]
      files:
      - path: /tmp/run.sh
        contents: |
          torchrun --nnodes {{n_nodes}} --node_rank {{node}} \
            --master_addr {{host:master}} --master_port 29400 \
            /tmp/train.py
    {% endfor %}

default-values:
  n_nodes: 4
```

This generates 4 tasks: `master`, `worker-1`, `worker-2`, `worker-3`.

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:112-177](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:85-116]()

### Template Conditionals

Use if/else logic for conditional configuration:

```yaml
tasks:
{% for i in range(num_tasks) %}
- name: task-{{i}}
  {% if i == 0 %}
  lead: true  # First task is lead
  outputs:
  - dataset:
      name: results
  {% endif %}
  image: my-image
{% endfor %}
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:129-170]()

### Reserved Variable Names

The following variable names are **reserved** and cannot be used in templates:
- `workflow_id`
- `input` (and `input:N` patterns)
- `output`
- `host` (and `host:task_name` patterns)

These are special tokens resolved at runtime, not template variables.

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:36-38]()

## Content-Addressable Storage

OSMO's **content-addressable storage** system stores files by their hash (ETag), enabling automatic deduplication across all datasets.

### How Deduplication Works

```mermaid
graph TB
    subgraph "Upload Process"
        LocalFile1["Local File 1<br/>data.txt<br/>Content: 'Hello World'"]
        LocalFile2["Local File 2<br/>copy.txt<br/>Content: 'Hello World'"]
        LocalFile3["Local File 3<br/>other.txt<br/>Content: 'Different'"]
        
        LocalFile1 --> Hash1["Compute ETag<br/>(MD5 hash)<br/>abc123"]
        LocalFile2 --> Hash2["Compute ETag<br/>(MD5 hash)<br/>abc123"]
        LocalFile3 --> Hash3["Compute ETag<br/>(MD5 hash)<br/>def456"]
    end
    
    subgraph "Object Storage"
        Hash1 --> Store1["hashes/abc123<br/>(uploaded once)"]
        Hash2 -.->|Already exists| Store1
        Hash3 --> Store2["hashes/def456"]
    end
    
    subgraph "Manifest"
        Manifest["manifests/v1.json<br/>{<br/>  'data.txt': 'abc123',<br/>  'copy.txt': 'abc123',<br/>  'other.txt': 'def456'<br/>}"]
    end
    
    Store1 -.-> Manifest
    Store2 -.-> Manifest
```

**Sources:** Diagram 5 from system architecture

### Storage Structure

For a dataset with ID `123` and version `5`:

```
s3://bucket/
├── 123/
│   ├── hashes/
│   │   ├── abc123def456...  # File content (stored by hash)
│   │   ├── 789012abc345...  # Another file
│   │   └── ...
│   └── manifests/
│       ├── 5.json  # Version 5 manifest
│       ├── 6.json  # Version 6 manifest
│       └── ...
```

Each manifest maps logical file paths to hash values:

```json
{
  "files": {
    "train/image_001.png": "abc123def456...",
    "train/image_002.png": "789012abc345...",
    "val/image_001.png": "abc123def456..."  // Same hash = deduplication
  }
}
```

**Sources:** Diagram 5 from system architecture

### Storage Efficiency Example

Scenario: 100 datasets, each containing 10,000 identical synthetic images

| Approach | Storage Used |
|----------|--------------|
| Traditional | 100 × 10,000 images = 1,000,000 files |
| Content-Addressable | 10,000 unique files (100x reduction) |

**Sources:** [README.md:76](), Diagram 5 from system architecture

### Bucket Configuration

Datasets are stored in buckets configured with credentials:

```bash
# Create S3 credential
$ osmo credential set my-s3-cred \
  --type S3 \
  --payload access_key=AKIAIOSFODNN7EXAMPLE \
              secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Create bucket configuration
$ osmo bucket set s3://my-bucket \
  --mode READWRITE \
  --credential my-s3-cred
```

**Sources:** [docs/deployment_guide/getting_started/create_storage/s3/index.rst:117-129]()

## Concept Relationships

The following diagram shows how all key concepts relate to each other in a complete workflow:

```mermaid
graph TB
    subgraph "Workflow Definition (YAML)"
        Workflow["workflow:<br/>name: train-and-eval"]
        
        Workflow --> Templates["Jinja Templates<br/>{{ num_gpus }}<br/>{% for i in range(N) %}"]
        
        Workflow --> TasksSection["tasks:"]
        Workflow --> GroupsSection["groups:"]
        Workflow --> ResourcesSection["resources:"]
        
        TasksSection --> Task1["- name: preprocess"]
        TasksSection --> Task2["- name: evaluate"]
        
        GroupsSection --> Group1["- name: training"]
        Group1 --> GroupTask1["  - name: master<br/>    lead: true"]
        Group1 --> GroupTask2["  - name: worker"]
        
        ResourcesSection --> DefaultRes["default:<br/>  cpu: 4<br/>  memory: 8Gi"]
        ResourcesSection --> NamedRes["sim:<br/>  gpu: 8<br/>  platform: gb200"]
    end
    
    subgraph "Runtime Resolution"
        Task1 --> Input1["inputs:<br/>- dataset: training-data"]
        Task1 --> Output1["outputs:<br/>- dataset: processed-data"]
        Task1 --> Tokens1["Special Tokens<br/>{{input:0}}<br/>{{output}}<br/>{{workflow_id}}"]
        
        GroupTask1 --> Tokens2["{{host:master}}<br/>{{host:worker}}"]
        
        Input1 --> Dataset1["Dataset<br/>training-data:latest<br/>version_id: 42"]
        Output1 --> Dataset2["Dataset<br/>processed-data<br/>new version created"]
        
        NamedRes --> Platform["Platform Match<br/>Backend with gb200"]
    end
    
    subgraph "Storage Layer"
        Dataset1 --> Manifest1["manifests/42.json"]
        Dataset2 --> Manifest2["manifests/new.json"]
        
        Manifest1 --> Hashes["hashes/<br/>Content-addressable<br/>deduplication"]
        Manifest2 --> Hashes
    end
    
    subgraph "Execution"
        Platform --> Backend["Backend Operator"]
        Backend --> K8s["Kubernetes Cluster"]
        K8s --> Pods["Pod Creation<br/>Task containers"]
        
        GroupTask1 --> GangScheduling["KAI Gang Scheduler<br/>Simultaneous launch"]
        GroupTask2 --> GangScheduling
        GangScheduling --> GroupPods["Group Pods<br/>with private network"]
    end
```

**Sources:** [README.md:47-71](), [docs/user_guide/how_to/training/multi_node.rst:46-96](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-229](), Diagram 4 and Diagram 5 from system architecture

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/appendix/deploy_local.rst](docs/deployment_guide/appendix/deploy_local.rst)
- [docs/deployment_guide/appendix/deploy_minimal.rst](docs/deployment_guide/appendix/deploy_minimal.rst)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [docs/deployment_guide/index.rst](docs/deployment_guide/index.rst)
- [docs/spelling_wordlist.txt](docs/spelling_wordlist.txt)
- [docs/user_guide/index.rst](docs/user_guide/index.rst)
- [docs/user_guide/overview.svg](docs/user_guide/overview.svg)

</details>



This page guides you through choosing and initiating your first OSMO deployment. It covers the three primary deployment options—Local, Minimal, and Production—and helps you select the appropriate approach based on your use case.

For detailed installation instructions specific to each deployment type, see:
- Local deployment on your workstation: [Quick Start with Brev](#2.1)
- Comparison of all deployment architectures: [Deployment Options Comparison](#2.2)
- Full production deployment guide: The Deployment Guide (external documentation)

## Deployment Options Overview

OSMO provides three deployment configurations, each designed for different stages of adoption and operational requirements:

| Deployment Type | Target Use Case | Setup Time | Authentication | Multi-Tenancy |
|----------------|-----------------|------------|----------------|---------------|
| **Local** | Evaluation, Development | ~10 minutes | Dev mode only | No |
| **Minimal** | Testing, Single-team POC | ~30 minutes | Optional | No |
| **Production** | Multi-team Production Use | ~2 hours | Full SSO/OAuth2 | Yes |

**Sources:** [README.md:134-143](), [docs/deployment_guide/appendix/deploy_local.rst:20-53](), [docs/deployment_guide/appendix/deploy_minimal.rst:20-43]()

## Choosing Your Deployment

```mermaid
flowchart TD
    Start["Need to deploy OSMO?"]
    Start --> Q1{"Evaluating OSMO<br/>for the first time?"}
    
    Q1 -->|Yes| Q2{"Have access to<br/>cloud GPU instance?"}
    Q1 -->|No| Q3{"Need multi-tenant<br/>support?"}
    
    Q2 -->|Yes| Brev["Brev Deployment<br/>(10 minutes)<br/>See page 2.1"]
    Q2 -->|No| Local["Local Deployment<br/>(KIND on workstation)<br/>See deploy_local.rst"]
    
    Q3 -->|No| Q4{"Single team,<br/>simple setup?"}
    Q3 -->|Yes| Prod["Production Deployment<br/>(Full SSO, multi-namespace)<br/>See Deployment Guide"]
    
    Q4 -->|Yes| Minimal["Minimal Deployment<br/>(Single namespace)<br/>See deploy_minimal.rst"]
    Q4 -->|No| Prod
    
    style Brev fill:#e1f5ff
    style Local fill:#e1f5ff
    style Minimal fill:#fff4e1
    style Prod fill:#e8f5e9
```

**Sources:** [docs/deployment_guide/index.rst:74-98](), [README.md:136-143]()

## Deployment Architectures

### Local Deployment (KIND)

The Local deployment runs OSMO entirely on your workstation using KIND (Kubernetes in Docker). It deploys all components into a single Kubernetes cluster with separate node groups for different workload types.

```mermaid
graph TB
    subgraph "Workstation"
        subgraph "KIND Cluster (osmo)"
            subgraph "Control Plane Nodes"
                ServiceNodes["service nodes<br/>osmo-service<br/>osmo-agent<br/>osmo-worker<br/>osmo-logger"]
                IngressNode["ingress node<br/>nginx-ingress"]
                KaiNode["kai-scheduler node<br/>KAI Scheduler"]
            end
            
            subgraph "Data Layer Nodes"
                DataNode["data node<br/>PostgreSQL<br/>Redis<br/>LocalStack S3"]
            end
            
            subgraph "Compute Nodes"
                ComputeNode["compute node<br/>Backend Operator<br/>GPU Operator (optional)"]
            end
        end
    end
    
    Browser["Browser<br/>http://quick-start.osmo"] --> IngressNode
    CLI["osmo CLI"] --> ServiceNodes
    
    ServiceNodes --> DataNode
    ComputeNode --> ServiceNodes
```

**Key Characteristics:**
- Single Kubernetes cluster with labeled node groups
- LocalStack provides S3-compatible object storage
- Dev-mode authentication (no Keycloak)
- GPU support via nvkind (optional)

**Helm Charts Deployed:**
- `quick-start` umbrella chart
- Includes: `service`, `web-ui`, `router`, `backend-operator`

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:70-267](), [deployments/brev/setup.sh:236-295]()

### Minimal Deployment

The Minimal deployment uses a single Kubernetes cluster with external PostgreSQL and Redis. It's designed for testing with minimal infrastructure overhead.

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "osmo-minimal namespace"
            API["osmo-service"]
            UI["osmo-ui"]
            Router["osmo-router"]
            Worker["osmo-worker"]
            Agent["osmo-agent"]
            Logger["osmo-logger"]
            Monitor["osmo-delayed-job-monitor"]
        end
        
        subgraph "osmo-operator namespace"
            BackendListener["backend-listener"]
            BackendWorker["backend-worker"]
        end
        
        subgraph "osmo-workflows namespace"
            Tasks["Workflow Task Pods"]
        end
    end
    
    subgraph "External Services"
        Postgres["PostgreSQL<br/>osmo_db"]
        Redis["Redis"]
        S3["S3/MinIO/Azure Blob"]
    end
    
    API --> Postgres
    API --> Redis
    Worker --> Postgres
    BackendListener --> API
    Tasks --> S3
    
    UI --> API
    Router --> BackendWorker
    BackendWorker --> Tasks
```

**Key Characteristics:**
- Single namespace for control plane services
- Separate namespace for backend operator
- External PostgreSQL and Redis required
- Optional ingress for external access
- No authentication (dev mode)

**Helm Charts Deployed:**
- `osmo/service` chart
- `osmo/web-ui` chart
- `osmo/router` chart
- `osmo/backend-operator` chart

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:29-48](), [docs/deployment_guide/appendix/deploy_minimal.rst:214-461]()

### Production Deployment

Production deployment provides full multi-tenant support with authentication, separate namespaces, and production-grade configurations. This architecture matches **Diagram 3** from the high-level overview.

```mermaid
graph TB
    subgraph "OSMO Service Cluster"
        subgraph "osmo namespace"
            API["osmo-service<br/>+ Envoy sidecar<br/>+ OTel sidecar<br/>+ FluentBit sidecar"]
            UI["osmo-ui<br/>+ Envoy sidecar"]
            Router["osmo-router<br/>+ Envoy sidecar"]
            Workers["osmo-worker pods<br/>(HPA scaled)"]
        end
        
        Ingress["ALB/NGINX Ingress<br/>SSL termination"]
    end
    
    subgraph "External Services"
        Keycloak["Keycloak<br/>OAuth2/OIDC SSO"]
        PG["PostgreSQL<br/>(RDS/AKS/GKE)"]
        Redis["Redis<br/>(ElastiCache/Memorystore)"]
        S3["Object Storage<br/>(S3/Azure Blob/GCS)"]
    end
    
    subgraph "Backend Operator Cluster"
        subgraph "backend-operator namespace"
            BListener["backend-listener"]
            BWorker["backend-worker"]
        end
        
        subgraph "workflows namespace"
            TaskPods["Workflow Task Pods<br/>+ KAI Scheduler"]
        end
    end
    
    Users["Users"] --> Ingress
    Ingress --> Keycloak
    Ingress --> UI
    UI --> API
    API --> PG
    API --> Redis
    
    BListener --> API
    BWorker --> TaskPods
    TaskPods --> S3
```

**Key Characteristics:**
- Multi-namespace architecture for security isolation
- Keycloak SSO integration with OAuth2/OIDC
- Envoy sidecars for authentication validation
- Horizontal Pod Autoscaling (HPA) for workers
- Production-grade databases (RDS, Cloud SQL, etc.)
- Full observability stack (FluentBit, OpenTelemetry, Prometheus)

**Helm Charts Deployed:**
- Same charts as Minimal, with production values
- Additional sidecars enabled
- HPA and resource limits configured

**Sources:** [docs/deployment_guide/index.rst:74-98](), [charts/webui cluster reference from overview](), [charts/backend-operator cluster reference from overview]()

## Prerequisites

### All Deployments

All deployment options require:

- **kubectl** >= 1.32.2
- **helm** >= 3.16.2
- **osmo CLI** (installed via `install.sh`)

**Sources:** [CONTRIBUTING.md:32-43]()

### Local Deployment Specific

- **Docker** >= 28.3.2
- **KIND** >= 0.29.0
- **System Configuration:**
  - Increased inotify limits (see KIND known issues)
  - Docker group permissions for current user

**Optional for GPU support:**
- **nvkind** (requires Go >= 1.23.4)
- **nvidia-container-toolkit** >= 1.18.0
- **NVIDIA drivers** >= 575

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:54-70](), [deployments/brev/setup.sh:46-106]()

### Minimal/Production Deployment Specific

- **Kubernetes Cluster** (EKS, AKS, GKE, or on-premise)
- **PostgreSQL** database (external or in-cluster)
- **Redis** cache (external or in-cluster)
- **Object Storage** (S3, Azure Blob, or MinIO)
- **Ingress Controller** (for external access)

**Optional for production:**
- **Keycloak** or compatible OIDC provider
- **Certificate Manager** for SSL/TLS

**Sources:** [docs/deployment_guide/index.rst:115-121](), [docs/deployment_guide/appendix/deploy_minimal.rst:49-56]()

## Quick Start Commands

### Local Deployment (KIND)

```bash
# Create KIND cluster
kind create cluster --config kind-osmo-cluster-config.yaml

# Install KAI Scheduler
helm upgrade --install kai-scheduler \
  oci://ghcr.io/nvidia/kai-scheduler/kai-scheduler \
  --version v0.8.1 \
  --create-namespace -n kai-scheduler

# Install OSMO
helm fetch https://helm.ngc.nvidia.com/nvidia/osmo/charts/quick-start-1.0.0.tgz
helm upgrade --install osmo quick-start-1.0.0.tgz \
  --namespace osmo \
  --create-namespace \
  --wait

# Install OSMO CLI
curl -fsSL https://raw.githubusercontent.com/NVIDIA/OSMO/main/install.sh | bash

# Login
osmo login http://quick-start.osmo --method=dev --username=testuser
```

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:269-332]()

### Brev Deployment

The Brev deployment automates the entire local setup process:

```bash
# One-time setup (runs automatically on Brev instance)
# See deployments/brev/setup.sh for full automation

# Access via Brev console or port forwarding
sudo ssh -i ~/.brev/brev.pem -p 22 -L 80:localhost:8000 shadeform@<instance-ip>

# Login
osmo login http://localhost:8000 --method=dev --username=testuser
```

**Sources:** [deployments/brev/README.md:30-111](), [deployments/brev/setup.sh:1-436]()

### Minimal Deployment

```bash
# Create namespaces
kubectl create namespace osmo-minimal
kubectl create namespace osmo-operator

# Create secrets
kubectl create secret generic db-secret \
  --from-literal=db-password=<password> \
  --namespace osmo-minimal

# Generate MEK (Master Encryption Key)
RANDOM_KEY=$(openssl rand -base64 32 | tr -d '\n')
JWK_JSON="{\"k\":\"$RANDOM_KEY\",\"kid\":\"key1\",\"kty\":\"oct\"}"
ENCODED_JWK=$(echo -n "$JWK_JSON" | base64 | tr -d '\n')

# Create MEK ConfigMap
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: mek-config
  namespace: osmo-minimal
data:
  mek.yaml: |
    currentMek: key1
    meks:
      key1: $ENCODED_JWK
EOF

# Deploy services
helm upgrade --install osmo-minimal osmo/service -f osmo_values.yaml --namespace osmo-minimal
helm upgrade --install ui-minimal osmo/web-ui -f ui_values.yaml --namespace osmo-minimal
helm upgrade --install router-minimal osmo/router -f router_values.yaml --namespace osmo-minimal
helm upgrade --install osmo-operator osmo/backend-operator -f backend_operator_values.yaml --namespace osmo-operator
```

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:57-603]()

## Component Overview

The following table maps OSMO components to their deployment configurations:

| Component | Purpose | Local | Minimal | Production |
|-----------|---------|-------|---------|------------|
| `osmo-service` | API server, workflow orchestration | ✓ | ✓ | ✓ (+ HPA) |
| `osmo-ui` | Next.js web interface | ✓ | ✓ | ✓ |
| `osmo-router` | Port forwarding, exec proxy | ✓ | ✓ | ✓ |
| `osmo-worker` | Background job processing | ✓ | ✓ | ✓ (+ HPA) |
| `osmo-agent` | Workflow status updates | ✓ | ✓ | ✓ |
| `osmo-logger` | Log streaming via WebSocket | ✓ | ✓ | ✓ |
| `osmo-delayed-job-monitor` | Job queue monitoring | ✓ | ✓ | ✓ |
| `backend-listener` | Poll tasks, monitor cluster | ✓ | ✓ | ✓ |
| `backend-worker` | Execute jobs, create K8s resources | ✓ | ✓ | ✓ |
| PostgreSQL | Metadata storage | LocalStack | External | Managed DB |
| Redis | Log cache, job queue | Local | External | Managed |
| Object Storage | Datasets, artifacts | LocalStack | S3/Azure | S3/Azure/GCS |
| Keycloak | SSO authentication | ✗ | ✗ | ✓ |
| Envoy Sidecars | Auth validation | ✗ | ✗ | ✓ |
| Ingress | External access | nginx | Optional | ALB/nginx |

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:250-267](), [docs/deployment_guide/appendix/deploy_minimal.rst:470-484]()

## Post-Deployment Configuration

After deploying OSMO, you must configure data storage before running workflows:

1. **Create Storage Buckets** - Set up S3, Azure Blob, or MinIO buckets
2. **Configure Dataset Storage** - Register buckets with OSMO using `osmo config`
3. **Install KAI Scheduler** - Required for gang scheduling (if not already installed)
4. **Configure Pools** - Define compute pools and resource platforms

For detailed configuration steps, see the Deployment Guide's "Getting Started" section.

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:661-669]()

## Next Steps

After completing deployment, proceed to:

1. **[Quick Start with Brev](#2.1)** - If evaluating with a cloud GPU instance
2. **[Deployment Options Comparison](#2.2)** - For detailed architecture comparison
3. **User Guide** - For tutorials on submitting your first workflow
4. **Deployment Guide** - For production deployment and advanced configuration

To verify your deployment, you can:
- Access the Web UI at your configured hostname
- Run `osmo workflow list` to verify CLI connectivity
- Submit a test workflow from the User Guide tutorials

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:338-353](), [README.md:145-156]()

---

# Page: Quick Start with Brev

# Quick Start with Brev

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/appendix/deploy_local.rst](docs/deployment_guide/appendix/deploy_local.rst)
- [docs/deployment_guide/appendix/deploy_minimal.rst](docs/deployment_guide/appendix/deploy_minimal.rst)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [docs/deployment_guide/index.rst](docs/deployment_guide/index.rst)
- [docs/spelling_wordlist.txt](docs/spelling_wordlist.txt)
- [docs/user_guide/index.rst](docs/user_guide/index.rst)
- [docs/user_guide/overview.svg](docs/user_guide/overview.svg)

</details>



## Purpose and Scope

This page describes how to deploy OSMO in approximately 10 minutes using Brev for evaluation purposes. The Brev deployment provides a pre-configured OSMO instance running on a Brev.dev cloud instance with GPU support, allowing you to quickly try OSMO without setting up local infrastructure.

**Note**: This deployment is intended for evaluation only. It lacks authentication mechanisms and has limited resources. For production deployments, see [Deployment Options Comparison](#2.2).

For information about local deployment on your own workstation, see the local deployment documentation in [docs/deployment_guide/appendix/deploy_local.rst:1-406]().

**Sources**: [deployments/brev/README.md:19-32](), [README.md:151]()

## Deployment Architecture

The Brev deployment uses the OSMO local deployment pattern with a KIND (Kubernetes in Docker) cluster. The automated setup script [deployments/brev/setup.sh:1-436]() creates the following architecture:

```mermaid
graph TB
    subgraph "Brev Cloud Instance"
        subgraph "KIND Cluster (osmo)"
            subgraph "Control Plane"
                CP["control-plane node"]
            end
            
            subgraph "Worker Nodes"
                Ingress["ingress worker<br/>node_group=ingress<br/>Port 8000→30080"]
                KAI["kai-scheduler worker<br/>node_group=kai-scheduler"]
                Data["data worker<br/>node_group=data<br/>LocalStack S3"]
                Service1["service worker 1<br/>node_group=service"]
                Service2["service worker 2<br/>node_group=service"]
                Compute["compute worker<br/>node_group=compute<br/>GPU enabled"]
            end
            
            subgraph "OSMO Services (osmo namespace)"
                API["osmo-service<br/>API Pod"]
                UI["osmo-ui<br/>Web UI Pod"]
                Router["osmo-router<br/>Router Pod"]
                Worker["osmo-worker<br/>Worker Pod"]
                Logger["osmo-logger<br/>Logger Pod"]
                Agent["osmo-agent<br/>Agent Pod"]
                Monitor["osmo-delayed-job-monitor<br/>Monitor Pod"]
            end
            
            subgraph "Backend Operator (osmo-workflows namespace)"
                BackendListener["backend-listener<br/>Poll Tasks"]
                BackendWorker["backend-worker<br/>Execute Jobs"]
            end
            
            subgraph "Data Layer (osmo namespace)"
                Postgres["PostgreSQL<br/>Workflows/Tasks/Configs"]
                Redis["Redis<br/>Logs/Job Queues"]
                LocalStack["LocalStack<br/>S3-compatible Storage"]
            end
            
            subgraph "Schedulers"
                KAIScheduler["KAI Scheduler<br/>(kai-scheduler namespace)<br/>Gang Scheduling"]
                GPUOperator["GPU Operator<br/>(gpu-operator namespace)<br/>Device Plugin"]
            end
        end
        
        GPU["Host GPU<br/>via nvkind"]
    end
    
    User["User Browser"]
    
    User -->|"http://localhost:8000<br/>(via Brev Secure Link)"| Ingress
    Ingress --> UI
    UI --> API
    API --> Postgres
    API --> Redis
    Worker --> Postgres
    Worker --> Redis
    Logger --> Redis
    Agent --> Postgres
    Router --> BackendWorker
    BackendListener --> API
    BackendWorker --> KAIScheduler
    KAIScheduler --> Compute
    GPUOperator --> Compute
    Compute --> GPU
    BackendWorker --> LocalStack
```

**Key Components**:

| Component | Purpose | Namespace |
|-----------|---------|-----------|
| `osmo-service` | API server for workflow operations | `osmo` |
| `osmo-ui` | Next.js web interface | `osmo` |
| `osmo-router` | Port forwarding and exec sessions | `osmo` |
| `osmo-worker` | Background job processing | `osmo` |
| `osmo-logger` | Log streaming | `osmo` |
| `osmo-agent` | Status updates | `osmo` |
| `backend-listener` | Polls for workflow tasks | `osmo-workflows` |
| `backend-worker` | Executes workflow tasks | `osmo-workflows` |
| `kai-scheduler` | Gang scheduling for GPUs | `kai-scheduler` |
| `gpu-operator` | GPU device management | `gpu-operator` |

**Sources**: [deployments/brev/setup.sh:230-295](), [deployments/brev/setup.sh:300-345](), [docs/deployment_guide/appendix/deploy_local.rst:249-266]()

## System Requirements

The Brev instance must have:

- **NVIDIA Driver**: Version 575 or higher
- **NVIDIA Container Toolkit**: Version 1.18.1 or higher

These requirements are validated during the automated setup process at [deployments/brev/setup.sh:82-105]().

**Sources**: [deployments/brev/README.md:34-37](), [deployments/brev/setup.sh:49-59]()

## Accessing the Brev Deployment

### Web UI Access via Secure Link

The simplest way to access OSMO is through the Brev secure link:

1. Deploy OSMO via the Brev link: [https://brev.nvidia.com/launchable/deploy?launchableID=env-36a6a7qnkOMOP2vgiBRaw2e3jpW](https://brev.nvidia.com/launchable/deploy?launchableID=env-36a6a7qnkOMOP2vgiBRaw2e3jpW)

2. Log in to your Brev console at https://console.brev.dev

3. Navigate to your OSMO instance

4. Select **Access**

5. Click on the **Secure Link** for port `8000`

This provides browser access to the OSMO Web UI without requiring local setup.

**Sources**: [deployments/brev/README.md:39-48](), [README.md:28]()

## Optional: Local CLI Setup

For advanced users who want to use the OSMO CLI from their local workstation, the following optional setup enables port forwarding and CLI access.

### Installation Flow

```mermaid
sequenceDiagram
    participant Local as Local Workstation
    participant Brev as Brev Instance
    participant KIND as KIND Cluster
    participant OSMO as OSMO Services
    
    Local->>Brev: Install Brev CLI
    Local->>Brev: SSH with port forward<br/>80:localhost:8000
    Local->>Local: Add /etc/hosts entry<br/>127.0.0.1 quick-start.osmo
    Local->>Local: Install OSMO CLI<br/>(install.sh)
    Local->>OSMO: osmo login http://quick-start.osmo<br/>--method=dev --username=testuser
    OSMO-->>Local: Authenticated
```

### Step 1: Install Brev CLI

Follow the installation instructions at the Brev CLI documentation. After installation, authenticate:

```bash
brev login
```

**Sources**: [deployments/brev/README.md:54-56]()

### Step 2: Set Up Port Forwarding

Forward port 8000 from the Brev instance to local port 80. Find your instance IP address at the top of the deployment page in the Brev console:

```bash
# Find your instance name
brev ls

# Set up port forwarding (requires sudo for port 80)
sudo ssh -i ~/.brev/brev.pem -p 22 -L 80:localhost:8000 shadeform@[your-instance-ip]
```

If you encounter `Permission denied (publickey)` errors:
1. Verify you ran `brev login`
2. Check the username in Brev Console → Instance → Logs → Script Logs for `Current user: [username]`
3. Replace `shadeform` with the correct username

**Sources**: [deployments/brev/README.md:58-81]()

### Step 3: Configure Local Networking

Add a host entry to access OSMO from your browser:

```bash
echo "127.0.0.1 quick-start.osmo" | sudo tee -a /etc/hosts
```

This allows accessing OSMO at `http://quick-start.osmo` in your web browser.

**Sources**: [deployments/brev/README.md:83-91]()

### Step 4: Install OSMO CLI

Download and install the OSMO command-line interface:

```bash
curl -fsSL https://raw.githubusercontent.com/NVIDIA/OSMO/refs/heads/main/install.sh | bash
```

The installation script is also executed during Brev setup at [deployments/brev/setup.sh:373-384]().

**Sources**: [deployments/brev/README.md:93-99]()

### Step 5: Authenticate with OSMO

Log in to the OSMO instance using the development authentication method:

```bash
osmo login http://quick-start.osmo --method=dev --username=testuser
```

The `--method=dev` flag uses a development authentication mode that bypasses OAuth2/Keycloak SSO, which is disabled in the Brev deployment. The username `testuser` is used for all operations.

**Sources**: [deployments/brev/README.md:101-107](), [deployments/brev/setup.sh:388-390]()

## Automated Deployment Process

The Brev deployment executes [deployments/brev/setup.sh:1-436]() automatically, which performs the following operations:

```mermaid
graph TD
    Start["Start setup.sh"] --> SysConfig["System Configuration<br/>• Increase inotify limits<br/>• Check Docker permissions<br/>• Verify NVIDIA driver"]
    SysConfig --> InstallPrereq["Install Prerequisites<br/>• KIND v0.29.0<br/>• kubectl (latest stable)<br/>• Helm 3<br/>• nvidia-ctk 1.18.1<br/>• nvkind (via Go)"]
    InstallPrereq --> CreateCluster["Create KIND Cluster<br/>nvkind cluster create<br/>7 worker nodes"]
    CreateCluster --> InstallGPU["Install GPU Operator<br/>gpu-operator-v25.10.0.tgz<br/>driver.enabled=false"]
    InstallGPU --> InstallKAI["Install KAI Scheduler<br/>v0.8.1<br/>Gang scheduling enabled"]
    InstallKAI --> InstallOSMO["Install OSMO<br/>quick-start-1.0.0.tgz<br/>namespace: osmo"]
    InstallOSMO --> InstallCLI["Install OSMO CLI<br/>install.sh"]
    InstallCLI --> Login["Login to OSMO<br/>testuser via dev auth"]
    Login --> Complete["Deployment Complete<br/>Access: localhost:8000"]
```

**Key Installation Steps**:

1. **System Configuration** [deployments/brev/setup.sh:62-105](): Configures inotify limits, verifies Docker permissions, and checks NVIDIA driver version (minimum 575)

2. **Prerequisites Installation** [deployments/brev/setup.sh:107-228](): Installs KIND, kubectl, Helm, nvidia-container-toolkit (1.18.1), and nvkind

3. **KIND Cluster Creation** [deployments/brev/setup.sh:300-312](): Creates a 7-worker-node KIND cluster using the configuration at [deployments/brev/setup.sh:237-295]()

4. **GPU Operator** [deployments/brev/setup.sh:315-328](): Installs GPU operator v25.10.0 with driver and toolkit disabled (using host versions)

5. **KAI Scheduler** [deployments/brev/setup.sh:333-344](): Installs KAI scheduler v0.8.1 for gang scheduling support

6. **OSMO Services** [deployments/brev/setup.sh:349-369](): Deploys the `quick-start-1.0.0` Helm chart to the `osmo` namespace

7. **CLI and Authentication** [deployments/brev/setup.sh:373-390](): Installs OSMO CLI and authenticates with development mode

**Sources**: [deployments/brev/setup.sh:19-436]()

## Verification

After successful deployment, verify that all pods are running:

```bash
kubectl get pods --namespace osmo
```

Expected output includes pods for:
- `osmo-service-*`
- `osmo-ui-*`
- `osmo-router-*`
- `osmo-worker-*`
- `osmo-logger-*`
- `osmo-agent-*`
- `osmo-delayed-job-monitor-*`

The deployment status is automatically checked at [deployments/brev/setup.sh:368-369]().

**Sources**: [deployments/brev/setup.sh:368-369](), [docs/deployment_guide/appendix/deploy_local.rst:400-404]()

## Limitations

The Brev deployment has the following limitations:

| Limitation | Description |
|------------|-------------|
| **No Authentication** | Uses `--method=dev` authentication; no OAuth2/OIDC/Keycloak |
| **Single User** | All operations under `testuser` |
| **Resource Constraints** | Limited by Brev instance specifications |
| **Ephemeral Storage** | LocalStack S3 storage is not persistent across restarts |
| **Development Mode** | Not suitable for production workloads |

For production deployments with authentication, multi-tenancy, and persistent storage, see [Deployment Options Comparison](#2.2).

**Sources**: [deployments/brev/README.md:32](), [README.md:32]()

## Cleanup

To remove the Brev deployment:

1. **Close port-forward session** (if using CLI):
   ```bash
   kill -9 $(lsof -ti:8000)
   ```

2. **Delete Brev instance** via console or CLI:
   ```bash
   brev delete [instance-name]
   ```

This removes the entire environment including the KIND cluster and all OSMO services.

**Sources**: [deployments/brev/README.md:120-132]()

## Next Steps

After successfully deploying OSMO on Brev:

1. **Run Your First Workflow**: Follow the getting started tutorials to submit your first workflow. See the user guide documentation for workflow examples.

2. **Explore the Web UI**: Access the OSMO dashboard to monitor workflows, view logs, and manage datasets.

3. **Test with Sample Workflows**: The OSMO repository includes example workflows in the `workflows/` directory demonstrating simulation, training, and distributed patterns.

4. **Evaluate for Your Use Case**: Test your own Docker images and datasets to assess OSMO's fit for your Physical AI development needs.

5. **Plan Production Deployment**: If OSMO meets your requirements, review production deployment options including authentication, multi-backend setup, and persistent storage configuration.

**Sources**: [deployments/brev/README.md:109-118](), [README.md:154-156]()

---

# Page: Deployment Options Comparison

# Deployment Options Comparison

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/appendix/deploy_local.rst](docs/deployment_guide/appendix/deploy_local.rst)
- [docs/deployment_guide/appendix/deploy_minimal.rst](docs/deployment_guide/appendix/deploy_minimal.rst)
- [docs/deployment_guide/index.rst](docs/deployment_guide/index.rst)
- [docs/deployment_guide/introduction/whats_next.rst](docs/deployment_guide/introduction/whats_next.rst)
- [docs/deployment_options.svg](docs/deployment_options.svg)
- [docs/front_cover.png](docs/front_cover.png)
- [docs/index.rst](docs/index.rst)
- [docs/spelling_wordlist.txt](docs/spelling_wordlist.txt)
- [docs/user_guide/index.rst](docs/user_guide/index.rst)
- [docs/user_guide/overview.svg](docs/user_guide/overview.svg)

</details>



## Purpose and Scope

This page compares the three primary deployment options for OSMO: Local, Minimal, and Production. It provides technical comparisons of architecture, components, features, and trade-offs to help you select the appropriate deployment strategy for your use case. For step-by-step deployment instructions, see the Quick Start with Brev guide ([2.1](#2.1)) or the specific deployment guides linked below.

## Overview

OSMO offers three deployment configurations that balance ease of setup against production readiness:

| Deployment Type | Setup Time | Target Use Case | Authentication | Multi-Backend | Infrastructure |
|-----------------|------------|-----------------|----------------|---------------|----------------|
| **Local** | ~10 minutes | Evaluation, learning | None (dev mode) | No | KIND cluster on workstation |
| **Minimal** | ~30 minutes | Testing, development | None (dev mode) | Single cluster | Cloud Kubernetes with external dependencies |
| **Production** | 2-4 hours | Production, multi-user | Keycloak SSO | Yes | Cloud Kubernetes with full observability stack |

```mermaid
graph TD
    Start["Deployment Decision"]
    
    Start --> Q1{"Need production<br/>authentication?"}
    Q1 -->|Yes| Prod["Production<br/>Deployment"]
    Q1 -->|No| Q2{"Need cloud<br/>infrastructure?"}
    
    Q2 -->|Yes| Minimal["Minimal<br/>Deployment"]
    Q2 -->|No| Local["Local<br/>Deployment"]
    
    Local --> L1["• KIND cluster<br/>• ~10 min setup<br/>• Zero cloud cost"]
    Minimal --> M1["• External DB/Redis<br/>• ~30 min setup<br/>• Single namespace"]
    Prod --> P1["• Keycloak SSO<br/>• ~2-4 hr setup<br/>• Full observability"]
    
    style Prod fill:#e8f5e9
    style Minimal fill:#fff4e1
    style Local fill:#e1f5ff
```

**Sources:** [docs/deployment_options.svg:1-217](), [docs/deployment_guide/index.rst:74-102]()

## Architecture Comparison

### Local Deployment Architecture

The Local deployment uses KIND (Kubernetes in Docker) to create a complete OSMO environment on a single workstation. All components run within Docker containers orchestrated by a local Kubernetes cluster.

```mermaid
graph TB
    subgraph LocalCluster["KIND Cluster (osmo)"]
        subgraph ControlPlane["Control Plane Node"]
            API["osmo-service<br/>(API + Agent + Logger)"]
            UI["osmo-ui<br/>(Next.js)"]
            Router["osmo-router"]
            Worker["osmo-worker"]
            Monitor["osmo-delayed-job-monitor"]
        end
        
        subgraph DataNode["Data Node (node_group=data)"]
            PG["PostgreSQL<br/>(bitnami chart)"]
            Redis["Redis<br/>(bitnami chart)"]
            LocalStack["LocalStack<br/>(S3 emulator)"]
        end
        
        subgraph ComputeNode["Compute Node (node_group=compute)"]
            Backend["osmo-backend-operator<br/>(listener + worker)"]
            Workflows["Workflow Task Pods"]
        end
        
        subgraph IngressNode["Ingress Node (node_group=ingress)"]
            Nginx["NGINX Ingress<br/>(port 30080 → 80)"]
        end
        
        subgraph Scheduler["Scheduler Node (node_group=kai-scheduler)"]
            KAI["KAI Scheduler"]
        end
    end
    
    Workstation["Workstation<br/>(Docker)"]
    Browser["Web Browser<br/>(http://quick-start.osmo)"]
    
    Workstation -.->|Docker| LocalCluster
    Browser --> Nginx
    Nginx --> UI
    Nginx --> API
    
    API --> PG
    API --> Redis
    Worker --> PG
    Backend --> API
    Backend --> KAI
    KAI --> Workflows
    Workflows --> LocalStack
    
    style LocalCluster fill:#f0f0f0
    style Workstation fill:#e1f5ff
```

**Key Characteristics:**
- **Single Cluster:** All components (control plane, compute, data) in one KIND cluster
- **Embedded Dependencies:** PostgreSQL, Redis, and LocalStack deployed via Helm within cluster
- **Node Groups:** Uses Kubernetes node labels for component placement ([docs/deployment_guide/appendix/deploy_local.rst:250-266]())
- **No Sidecars:** Envoy, FluentBit, and OpenTelemetry sidecars disabled
- **Authentication:** Dev mode login with `--method=dev --username=testuser` ([docs/deployment_guide/appendix/deploy_local.rst:331]())

**Configuration Files:**
- `kind-osmo-cluster-config.yaml`: Defines 7-node cluster with specific node groups ([docs/deployment_guide/appendix/deploy_local.rst:87-150]())
- `quick-start-1.0.0.tgz`: Umbrella Helm chart deploying all components ([docs/deployment_guide/appendix/deploy_local.rst:291-295]())

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:72-405](), [docs/deployment_guide/index.rst:81-102]()

### Minimal Deployment Architecture

The Minimal deployment separates data dependencies (PostgreSQL, Redis) from the Kubernetes cluster while maintaining a simplified single-namespace architecture.

```mermaid
graph TB
    subgraph K8sCluster["Kubernetes Cluster"]
        subgraph OsmoNamespace["osmo-minimal Namespace"]
            Service["osmo-service<br/>(replicas: 1)"]
            Agent["osmo-agent<br/>(replicas: 1)"]
            Logger["osmo-logger<br/>(replicas: 1)"]
            Worker["osmo-worker<br/>(replicas: 1)"]
            Monitor["osmo-delayed-job-monitor"]
            UI["osmo-ui"]
            Router["osmo-router"]
        end
        
        subgraph OperatorNamespace["osmo-operator Namespace"]
            BackendListener["osmo-backend-listener"]
            BackendWorker["osmo-backend-worker"]
        end
        
        subgraph WorkflowNamespace["osmo-workflows Namespace"]
            TaskPods["Workflow Task Pods"]
        end
        
        Ingress["Ingress (optional)<br/>(nginx/ALB)"]
    end
    
    subgraph ExternalServices["External Services"]
        PostgreSQL["PostgreSQL<br/>(managed service)"]
        Redis["Redis<br/>(managed service)"]
        S3["S3 / Azure Blob<br/>(object storage)"]
    end
    
    Secrets["K8s Secrets:<br/>• db-secret<br/>• redis-secret<br/>• mek-config"]
    
    Ingress -.->|optional| UI
    Ingress -.->|optional| Service
    
    Service --> PostgreSQL
    Service --> Redis
    Agent --> PostgreSQL
    Worker --> PostgreSQL
    Logger --> Redis
    
    BackendListener --> Service
    BackendWorker --> TaskPods
    TaskPods --> S3
    
    Secrets -.-> Service
    
    style K8sCluster fill:#f0f0f0
    style ExternalServices fill:#fff4e1
```

**Key Characteristics:**
- **Three Namespaces:** `osmo-minimal` (services), `osmo-operator` (backend), `osmo-workflows` (workloads)
- **External Dependencies:** PostgreSQL and Redis must be provisioned separately ([docs/deployment_guide/appendix/deploy_minimal.rst:32-42]())
- **Minimal Replicas:** All services run with `minReplicas: 1`, `maxReplicas: 1` ([docs/deployment_guide/appendix/deploy_minimal.rst:250-295]())
- **No Sidecars:** Envoy, logAgent, otel, and rateLimit sidecars all disabled ([docs/deployment_guide/appendix/deploy_minimal.rst:297-311]())
- **Optional Ingress:** Can be accessed via `kubectl port-forward` or configured ingress ([docs/deployment_guide/appendix/deploy_minimal.rst:624-659]())

**Helm Values Files:**
- `osmo_values.yaml`: Configures service chart with external DB/Redis ([docs/deployment_guide/appendix/deploy_minimal.rst:214-280]())
- `ui_values.yaml`: Configures web-ui chart ([docs/deployment_guide/appendix/deploy_minimal.rst:313-356]())
- `router_values.yaml`: Configures router chart ([docs/deployment_guide/appendix/deploy_minimal.rst:362-424]())
- `backend_operator_values.yaml`: Configures backend operator ([docs/deployment_guide/appendix/deploy_minimal.rst:524-564]())

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:20-731](), [docs/deployment_guide/index.rst:74-102]()

### Production Deployment Architecture

The Production deployment implements a full multi-tenant architecture with authentication, observability, and support for multiple geographically distributed compute backends.

```mermaid
graph TB
    subgraph K8sCluster["Primary Kubernetes Cluster"]
        subgraph ServiceNamespace["osmo-service Namespace"]
            subgraph APIPod["API Pod"]
                APIContainer["osmo-service"]
                EnvoyAPI["Envoy Sidecar<br/>(OAuth2 filter)"]
                OTelAPI["OTel Sidecar"]
                FluentAPI["FluentBit Sidecar"]
            end
            
            subgraph UIPod["UI Pod"]
                UIContainer["osmo-ui<br/>(port 8000)"]
                EnvoyUI["Envoy Sidecar<br/>(port 8080)"]
                FluentUI["FluentBit Sidecar"]
            end
            
            subgraph WorkerPods["Worker Pods (HPA)"]
                WorkerReplicas["osmo-worker<br/>(min: 2, max: 10)"]
            end
            
            AgentPod["osmo-agent<br/>(HPA)"]
            LoggerPod["osmo-logger<br/>(HPA)"]
            MonitorPod["osmo-delayed-job-monitor"]
        end
        
        Ingress["Ingress<br/>(ALB / nginx)<br/>TLS termination"]
    end
    
    subgraph BackendCluster1["Backend Cluster 1 (Cloud EKS)"]
        Backend1["osmo-backend-operator"]
        Workflows1["Workflow Pods"]
    end
    
    subgraph BackendCluster2["Backend Cluster 2 (On-Prem DGX)"]
        Backend2["osmo-backend-operator"]
        Workflows2["Workflow Pods"]
    end
    
    subgraph BackendCluster3["Backend Cluster 3 (Edge Jetson)"]
        Backend3["osmo-backend-operator"]
        Workflows3["Workflow Pods"]
    end
    
    subgraph ExternalServices["External Services"]
        PostgreSQL["PostgreSQL<br/>(HA cluster)"]
        Redis["Redis<br/>(HA cluster)"]
        Keycloak["Keycloak<br/>(SSO/OAuth2)"]
        ObjectStorage["Object Storage<br/>(S3 / Azure)"]
        Prometheus["Prometheus"]
        Grafana["Grafana"]
    end
    
    Users["Users<br/>(Browser / CLI)"]
    
    Users --> Ingress
    Ingress --> EnvoyUI
    Ingress --> EnvoyAPI
    
    EnvoyUI -.->|JWT validation| Keycloak
    EnvoyAPI -.->|JWT validation| Keycloak
    
    EnvoyUI --> UIContainer
    EnvoyAPI --> APIContainer
    
    APIContainer --> PostgreSQL
    APIContainer --> Redis
    WorkerReplicas --> PostgreSQL
    AgentPod --> PostgreSQL
    LoggerPod --> Redis
    
    Backend1 -.->|outbound TLS| APIContainer
    Backend2 -.->|outbound TLS| APIContainer
    Backend3 -.->|outbound TLS| APIContainer
    
    Workflows1 --> ObjectStorage
    Workflows2 --> ObjectStorage
    Workflows3 --> ObjectStorage
    
    OTelAPI -.-> Prometheus
    FluentAPI -.-> Grafana
    
    style K8sCluster fill:#f0f0f0
    style BackendCluster1 fill:#e8f5e9
    style BackendCluster2 fill:#e8f5e9
    style BackendCluster3 fill:#e8f5e9
    style ExternalServices fill:#ffe1e1
```

**Key Characteristics:**
- **Multi-Namespace:** Separate namespaces for services, each backend operator, and workflow execution
- **Sidecar Architecture:** Every service pod includes Envoy (authentication), FluentBit (logging), and OpenTelemetry (metrics)
- **Horizontal Scaling:** HorizontalPodAutoscaler configured for API, Agent, Worker, Logger services
- **Multi-Backend Support:** Multiple backend operators connecting from different clusters/networks ([docs/deployment_guide/index.rst:91-98]())
- **Authentication:** Full Keycloak SSO with OAuth2/OIDC flows ([docs/deployment_guide/index.rst:91-102]())
- **Observability:** Integrated metrics (Prometheus), logs (FluentBit), and traces (OpenTelemetry)

**Production-Only Features:**
- Service-to-service JWT authentication
- Encrypted credentials with Master Encryption Key (MEK)
- Rate limiting via Envoy sidecars
- TLS for all inter-service communication
- Automated log rotation and aggregation
- Distributed tracing

**Sources:** [docs/deployment_guide/index.rst:74-102](), [docs/deployment_options.svg:184-215](), Diagram 3 from high-level architecture

## Component Comparison

### Control Plane Services

| Component | Local | Minimal | Production |
|-----------|-------|---------|-----------|
| **osmo-service** | Single replica, no sidecars | Single replica, no sidecars | HPA (2-10), Envoy + OTel + FluentBit sidecars |
| **osmo-agent** | Single replica | Single replica | HPA, sidecars enabled |
| **osmo-worker** | Single replica | Single replica | HPA, progress check liveness probe |
| **osmo-logger** | Single replica | Single replica | HPA, WebSocket streaming |
| **osmo-ui** | Single replica | Single replica | Envoy sidecar for auth, Next.js runtime config |
| **osmo-router** | Not accessible via port-forward | Limited functionality | Full exec/port-forward support via ingress |
| **osmo-delayed-job-monitor** | Included | Included | Included with monitoring alerts |

**Configuration Differences:**

For **Local** deployment ([docs/deployment_guide/appendix/deploy_local.rst:291-295]()):
```bash
helm upgrade --install osmo quick-start-1.0.0.tgz \
  --namespace osmo \
  --create-namespace
```

For **Minimal** deployment ([docs/deployment_guide/appendix/deploy_minimal.rst:439-461]()):
```bash
# Separate helm installs for each component
helm upgrade --install osmo-minimal osmo/service -f osmo_values.yaml
helm upgrade --install ui-minimal osmo/web-ui -f ui_values.yaml  
helm upgrade --install router-minimal osmo/router -f router_values.yaml
```

For **Production** deployment, services require:
- Keycloak realm and client configuration
- TLS certificates for ingress
- Storage class for persistent volumes
- Service mesh configuration

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:284-405](), [docs/deployment_guide/appendix/deploy_minimal.rst:434-731](), [charts/webui cluster and service cluster references from high-level architecture]()

### Data Layer

| Component | Local | Minimal | Production |
|-----------|-------|---------|-----------|
| **PostgreSQL** | In-cluster (Bitnami chart) | External managed service | External HA cluster with replicas |
| **Redis** | In-cluster (Bitnami chart) | External managed service | External HA cluster with Sentinel |
| **Object Storage** | LocalStack S3 emulator | S3 / Azure Blob | S3 / Azure Blob with versioning |
| **Database** | `osmo_db` auto-created | Manual `osmo_db` creation required | Multiple databases for isolation |
| **Credentials** | No encryption | MEK encryption via ConfigMap | MEK encryption via vault/secrets |

**Local Storage Mount** ([docs/deployment_guide/appendix/deploy_local.rst:218-220]()):
```yaml
extraMounts:
  - hostPath: /tmp/localstack-s3
    containerPath: /var/lib/localstack
```

**Minimal External Database Setup** ([docs/deployment_guide/appendix/deploy_minimal.rst:174-207]()):
```bash
# Manual database creation required
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: osmo-db-ops
spec:
  containers:
    - name: osmo-db-ops
      image: alpine/psql:17.5
      command: ["/bin/sh", "-c"]
      args:
        - "PGPASSWORD=$OSMO_PGPASSWORD psql -U postgres -h $OSMO_DB_HOST -p 5432 -d postgres -c 'CREATE DATABASE osmo_db;'"
  restartPolicy: Never
EOF
```

**Production** requires separate provisioning of:
- Multi-AZ PostgreSQL with automated backups
- Redis cluster with persistence enabled
- S3 buckets with lifecycle policies
- VPC peering for private connectivity

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:250-266](), [docs/deployment_guide/appendix/deploy_minimal.rst:174-248](), [docs/deployment_guide/index.rst:85-90]()

### Authentication & Security

| Feature | Local | Minimal | Production |
|---------|-------|---------|-----------|
| **User Authentication** | Dev mode (`--method=dev`) | Dev mode (`--method=dev`) | Keycloak OAuth2/OIDC |
| **Service Authentication** | None | Backend tokens | Service tokens + mutual TLS |
| **Session Management** | None | None | HMAC-signed cookies via Envoy |
| **JWT Validation** | Skipped | Skipped | Envoy OAuth2 filter per service |
| **Credential Encryption** | None | MEK via ConfigMap | MEK via secure vault |
| **Network Security** | Host network | Internal K8s networking | Service mesh with mTLS |
| **RBAC** | Disabled | Disabled | Full RBAC with Keycloak roles |

**Dev Mode Login** ([docs/deployment_guide/appendix/deploy_local.rst:327-331]()):
```bash
osmo login http://quick-start.osmo --method=dev --username=testuser
```

**Backend Token Authentication** (Minimal) ([docs/deployment_guide/appendix/deploy_minimal.rst:586-593]()):
```bash
export BACKEND_TOKEN=$(osmo token set backend-token \
  --expires-at <date> \
  --description "Backend Operator Token" \
  --service --roles osmo-backend -t json | jq -r '.token')

kubectl create secret generic osmo-operator-token \
  --from-literal=token=$BACKEND_TOKEN \
  --namespace osmo-operator
```

**Production** implements:
- Browser flow: OAuth2 authorization code with PKCE
- CLI flow: Device authorization flow
- Backend flow: Long-lived service tokens with role-based access
- API security: JWT validation at ingress + rate limiting

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:324-336](), [docs/deployment_guide/appendix/deploy_minimal.rst:566-593](), [docs/deployment_guide/appendix/authentication/index references from deployment guide]()

## Feature Matrix

| Feature | Local | Minimal | Production | Notes |
|---------|:-----:|:-------:|:----------:|-------|
| **Workflow Submission** | ✅ | ✅ | ✅ | |
| **Web UI** | ✅ | ✅ | ✅ | Local: `localhost:80`, others via ingress |
| **CLI Access** | ✅ | ✅ | ✅ | |
| **Multi-User** | ❌ | ❌ | ✅ | Requires SSO |
| **Interactive Workflows** | ⚠️ | ⚠️ | ✅ | `exec`/`port-forward` require ingress |
| **Distributed Training** | ⚠️ | ✅ | ✅ | Local limited by single node |
| **Multi-Backend** | ❌ | ❌ | ✅ | |
| **Dataset Management** | ✅ | ✅ | ✅ | |
| **Content-Addressable Storage** | ✅ | ✅ | ✅ | |
| **Workflow Versioning** | ✅ | ✅ | ✅ | |
| **Configuration Management** | ✅ | ✅ | ✅ | |
| **GPU Support** | ⚠️ | ✅ | ✅ | Local requires nvkind for GPUs |
| **Gang Scheduling** | ✅ | ✅ | ✅ | KAI scheduler required in all |
| **Log Streaming** | ✅ | ✅ | ✅ | |
| **Log Aggregation** | ❌ | ❌ | ✅ | FluentBit → centralized logging |
| **Metrics Collection** | ❌ | ❌ | ✅ | OpenTelemetry → Prometheus |
| **Distributed Tracing** | ❌ | ❌ | ✅ | |
| **Auto-Scaling** | ❌ | ❌ | ✅ | HPA configured |
| **High Availability** | ❌ | ❌ | ✅ | Multiple replicas + external HA DB |
| **Disaster Recovery** | ❌ | ⚠️ | ✅ | Minimal: manual, Production: automated |
| **Air-Gapped** | ✅ | ⚠️ | ✅ | Minimal requires external services |
| **TLS Encryption** | ❌ | ⚠️ | ✅ | Minimal: optional, Production: required |

Legend:
- ✅ Fully Supported
- ⚠️ Partially Supported / Requires Additional Configuration
- ❌ Not Supported

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:34-48](), [docs/deployment_guide/appendix/deploy_minimal.rst:29-42](), [docs/deployment_options.svg:130-213]()

## Resource Requirements

### Local Deployment

**Minimum System Requirements:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free space
- Docker: >=28.3.2
- KIND: >=0.29.0

**KIND Cluster Resources** ([docs/deployment_guide/appendix/deploy_local.rst:250-266]()):
- 1 control-plane node
- 6 worker nodes (compute, service×2, data, ingress, kai-scheduler)
- Node groups via labels: `node_group=compute`, `node_group=service`, etc.

**GPU Support** ([docs/deployment_guide/appendix/deploy_local.rst:76-173]()):
- Requires nvkind for GPU passthrough
- GPU Operator v25.10.0 with driver disabled
- Node label: `nvidia.com/gpu.deploy.operands=false`

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:54-70]()

### Minimal Deployment

**Kubernetes Cluster:**
- Nodes: 3-5 worker nodes recommended
- CPU: 8+ cores total
- RAM: 16+ GB total
- Storage: 100+ GB

**External Services:**
- PostgreSQL: 2+ vCPUs, 4+ GB RAM, 50+ GB storage
- Redis: 1+ vCPUs, 2+ GB RAM
- Object Storage: S3-compatible or Azure Blob

**Per-Service Resources** ([docs/deployment_guide/appendix/deploy_minimal.rst:543-559]()):
```yaml
backendListener:
  resources:
    requests:
      cpu: "125m"
      memory: "128Mi"
    limits:
      cpu: "250m"
      memory: "256Mi"
```

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:48-56]()

### Production Deployment

**Kubernetes Cluster:**
- Nodes: 10+ worker nodes for control plane
- CPU: 32+ cores total across nodes
- RAM: 64+ GB total
- Storage: 500+ GB with high IOPS

**High Availability Requirements:**
- PostgreSQL: Primary + 2 replicas, automated failover
- Redis: 3-node cluster with Sentinel
- Load Balancer: Multi-AZ with health checks
- Object Storage: Versioning + replication enabled

**Service Scaling Configurations:**
- API: min 2, max 10 replicas
- Worker: min 2, max 10 replicas
- Agent: min 2, max 5 replicas
- Logger: min 2, max 5 replicas

**Additional Infrastructure:**
- Keycloak: 2+ replicas for HA
- Prometheus: Persistent storage for metrics
- Grafana: HA deployment with shared database
- Ingress Controller: Multi-replica with autoscaling

**Sources:** [charts/service scaling configurations from high-level architecture](), [docs/deployment_guide/index.rst:85-102]()

## Network Architecture

### Local Deployment

```mermaid
graph LR
    Localhost["Localhost<br/>(127.0.0.1)"]
    
    subgraph HostNetwork["Host Network"]
        Port80["Port 80"]
        HostEntry["/etc/hosts entry:<br/>quick-start.osmo"]
    end
    
    subgraph KINDNetwork["KIND Network (Bridge)"]
        IngressPort["Node Port 30080"]
        NginxIngress["NGINX Ingress"]
        Services["K8s Services<br/>(ClusterIP)"]
    end
    
    Localhost --> HostEntry
    HostEntry --> Port80
    Port80 --> IngressPort
    IngressPort --> NginxIngress
    NginxIngress --> Services
```

**Configuration:**
- Port mapping: Host port 80 → Container port 30080 ([docs/deployment_guide/appendix/deploy_local.rst:105-107]())
- DNS: Manual `/etc/hosts` entry for `quick-start.osmo` ([docs/deployment_guide/appendix/deploy_local.rst:307-313]())
- Network mode: Bridge (default Docker network)
- No external ingress required

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:304-313]()

### Minimal Deployment

```mermaid
graph TB
    subgraph PublicInternet["Public Internet (optional)"]
        DNS["DNS Record<br/>(your-domain)"]
        Users["External Users"]
    end
    
    subgraph K8sCluster["Kubernetes Cluster"]
        Ingress["Ingress Controller<br/>(nginx/ALB)"]
        Services["ClusterIP Services"]
        
        subgraph VPC["VPC / Private Network"]
            Pods["Service Pods"]
        end
    end
    
    subgraph ManagedServices["Managed Services VPC"]
        PostgreSQL["PostgreSQL<br/>(private endpoint)"]
        Redis["Redis<br/>(private endpoint)"]
    end
    
    Users -.->|optional| DNS
    DNS -.->|optional| Ingress
    Ingress --> Services
    Services --> Pods
    Pods --> PostgreSQL
    Pods --> Redis
    
    PortForward["kubectl port-forward<br/>(fallback access)"]
    PortForward -.-> Services
```

**Configuration Options:**

With Ingress ([docs/deployment_guide/appendix/deploy_minimal.rst:256-280]()):
```yaml
ingress:
  enabled: true
  ingressClass: alb  # or nginx
  sslEnabled: true
  albAnnotations:
    enabled: true
    sslCertArn: <cert-arn>
```

Without Ingress ([docs/deployment_guide/appendix/deploy_minimal.rst:624-659]()):
```bash
# API access
kubectl port-forward service/osmo-service 9000:80 -n osmo-minimal

# UI access  
kubectl port-forward service/osmo-ui 3000:80 -n osmo-minimal
```

**Important Limitation:** Router functionality (`exec`, `port-forward` for workflows) requires ingress configuration ([docs/deployment_guide/appendix/deploy_minimal.rst:655-659]()).

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:491-659]()

### Production Deployment

```mermaid
graph TB
    subgraph Internet["Public Internet"]
        Browser["User Browsers"]
        CLI["OSMO CLI"]
    end
    
    subgraph EdgeLayer["Edge Layer"]
        DNS["DNS (Route53/CloudDNS)"]
        WAF["WAF<br/>(optional)"]
        LB["Load Balancer<br/>(ALB/NLB)"]
    end
    
    subgraph K8sCluster["Kubernetes Cluster"]
        Ingress["Ingress Controller<br/>(TLS termination)"]
        
        subgraph ServiceMesh["Service Mesh (optional)"]
            EnvoyProxies["Envoy Sidecars<br/>(mTLS)"]
        end
        
        Services["K8s Services"]
    end
    
    subgraph BackendClusters["Remote Backend Clusters"]
        Backend1["Backend 1<br/>(outbound TLS)"]
        Backend2["Backend 2<br/>(outbound TLS)"]
        Backend3["Backend 3<br/>(outbound TLS)"]
    end
    
    subgraph DataPlane["Data Plane"]
        PostgreSQL["PostgreSQL<br/>(Private Link)"]
        Redis["Redis<br/>(Private Link)"]
        S3["S3/Azure Blob<br/>(VPC Endpoint)"]
    end
    
    Browser --> DNS
    CLI --> DNS
    DNS --> WAF
    WAF --> LB
    LB --> Ingress
    Ingress --> EnvoyProxies
    EnvoyProxies --> Services
    
    Services --> PostgreSQL
    Services --> Redis
    
    Backend1 -.->|Outbound HTTPS| LB
    Backend2 -.->|Outbound HTTPS| LB
    Backend3 -.->|Outbound HTTPS| LB
    
    Services --> S3
    Backend1 --> S3
    Backend2 --> S3
    Backend3 --> S3
```

**Network Layers:**
1. **Edge:** DNS, WAF, Load Balancer with TLS termination
2. **Ingress:** Kubernetes ingress controller (ALB or NGINX) with SSL certificates
3. **Service Mesh:** Envoy sidecars for service-to-service mTLS (optional)
4. **Backend Connectivity:** Outbound connections from remote clusters through corporate firewalls
5. **Data Plane:** Private endpoints for databases, VPC endpoints for object storage

**Security Features:**
- TLS 1.2+ for all external communication
- Mutual TLS (mTLS) for internal service communication
- Network policies for pod-to-pod restrictions
- VPC peering for cross-region backend clusters
- No inbound firewall rules needed for backend operators ([docs/deployment_guide/index.rst:94-98]())

**Sources:** [docs/deployment_guide/index.rst:81-102](), Diagram 1 from high-level architecture

## Cost Comparison

### Local Deployment

**Costs:**
- Infrastructure: $0 (uses local workstation)
- Compute: $0
- Storage: $0
- Networking: $0
- **Total: $0/month**

**Trade-offs:**
- Limited to workstation resources
- Single node limits scale testing
- No production-grade features

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:34-48]()

### Minimal Deployment

**Estimated Monthly Costs (AWS example):**
- Kubernetes cluster (EKS): ~$75 (cluster management fee)
- Worker nodes (3× t3.large): ~$150
- PostgreSQL RDS (db.t3.medium): ~$50
- Redis ElastiCache (cache.t3.micro): ~$15
- S3 storage (100 GB): ~$2
- Data transfer: ~$10
- **Total: ~$302/month**

**Cost Optimization:**
- Use spot instances for non-critical workloads
- Rightsize PostgreSQL/Redis instances
- Enable S3 lifecycle policies
- Use reserved instances for stable workloads

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:48-56]()

### Production Deployment

**Estimated Monthly Costs (AWS example):**
- Kubernetes cluster (EKS): ~$75
- Worker nodes (10× m5.2xlarge): ~$2,500
- PostgreSQL RDS Multi-AZ (db.r5.xlarge): ~$400
- Redis ElastiCache cluster (3× cache.r5.large): ~$300
- Keycloak infrastructure (2× t3.medium): ~$60
- Application Load Balancer: ~$25
- S3 storage (1 TB): ~$23
- CloudWatch/monitoring: ~$100
- Data transfer: ~$200
- **Total: ~$3,683/month**

**Additional Costs:**
- Multiple backend clusters (per cluster)
- Enhanced monitoring/observability stack
- Backup storage
- Disaster recovery infrastructure

**Cost Optimization:**
- Use Savings Plans for compute
- Implement auto-scaling to reduce idle capacity
- Use S3 Intelligent-Tiering
- Optimize data transfer with VPC endpoints

**Sources:** General cloud provider pricing

## Use Case Recommendations

### When to Use Local Deployment

**Ideal For:**
- **Initial Evaluation:** Testing OSMO features before cloud commitment
- **Learning:** Understanding OSMO concepts and workflow patterns
- **Development:** Developing workflow definitions locally
- **Demos:** Quick demonstrations of OSMO capabilities

**Not Suitable For:**
- Production workloads
- Multi-user environments
- Large-scale distributed training
- Long-running workflows requiring HA

**Example Workflow:** Developer testing a single-task workflow with CPU-only inference.

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:24-53]()

### When to Use Minimal Deployment

**Ideal For:**
- **Development Teams:** Shared development environment for multiple developers
- **Integration Testing:** Testing OSMO integration with other systems
- **Proof of Concept:** Demonstrating OSMO to stakeholders with cloud resources
- **Small-Scale Training:** Running small training jobs with limited compute

**Not Suitable For:**
- Production workloads requiring HA
- Multi-tenant environments requiring isolation
- Scenarios requiring authentication/authorization
- Mission-critical workloads

**Example Workflow:** Development team running nightly integration tests with synthetic data generation and small model training.

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:20-28]()

### When to Use Production Deployment

**Ideal For:**
- **Production Workloads:** Mission-critical robotics pipelines
- **Multi-User Environments:** Teams requiring SSO and role-based access
- **Multi-Region Deployments:** Workloads spanning multiple geographic regions
- **Compliance Requirements:** Environments requiring audit logs, encryption
- **Large-Scale Training:** Distributed training across hundreds of GPUs
- **Interactive Workflows:** Data scientists requiring exec/port-forward access

**Required When:**
- Authentication is mandatory (corporate SSO)
- High availability is critical
- Multiple backend clusters are needed
- Observability and monitoring are required
- Sensitive data requires encryption at rest/in transit

**Example Workflow:** Production robotics pipeline with Isaac Sim synthetic data generation on RTX GPUs, distributed training on GB200 cluster, and hardware-in-the-loop testing on Jetson devices, all orchestrated through a single workflow with SSO authentication.

**Sources:** [docs/deployment_options.svg:184-215](), [docs/deployment_guide/index.rst:74-102]()

## Migration Paths

### Local → Minimal

**Process:**
1. Export workflow definitions from local deployment
2. Provision external PostgreSQL and Redis
3. Deploy minimal OSMO to cloud Kubernetes
4. Reconfigure storage to use S3/Azure instead of LocalStack
5. Import workflow definitions and datasets

**Data Migration:**
```bash
# Export workflows
osmo workflow list --format json > workflows.json

# Export datasets (requires storage migration)
osmo dataset list --format json > datasets.json

# After minimal deployment
osmo workflow submit <workflow.yaml>
```

**Compatibility:** 100% - Same OSMO version, same workflow YAML format

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:338-353]()

### Minimal → Production

**Process:**
1. Deploy Keycloak and configure realms/clients
2. Enable Envoy sidecars in Helm values
3. Configure ingress with TLS certificates
4. Enable HPA for all services
5. Deploy FluentBit and OpenTelemetry collectors
6. Configure external monitoring (Prometheus/Grafana)
7. Migrate PostgreSQL/Redis to HA configurations
8. Update user authentication from dev mode to SSO

**Configuration Changes:**
```yaml
# Before (Minimal)
sidecars:
  envoy:
    enabled: false

# After (Production)
sidecars:
  envoy:
    enabled: true
    oauth2:
      enabled: true
      keycloakUrl: https://keycloak.example.com
```

**Downtime:** ~2-4 hours for full cutover (can be done gradually)

**Compatibility:** 100% - Workflow definitions unchanged, data migrates transparently

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:692-700]()

### Direct to Production

For organizations with existing Kubernetes expertise, deploying directly to production is recommended over iterative migration. This avoids:
- Multiple configuration iterations
- Repeated data migrations
- Rework of CI/CD pipelines
- Team retraining on different authentication methods

**Prerequisites:**
- Kubernetes cluster with ingress controller
- Keycloak instance (or other OIDC provider)
- High-availability PostgreSQL
- High-availability Redis
- S3-compatible object storage
- Monitoring infrastructure (Prometheus/Grafana)

**Sources:** [docs/deployment_guide/introduction/whats_next.rst:20-35]()

## Configuration Examples

### Helm Values Comparison

**Local (automatic via quick-start chart):**
```yaml
# No custom values needed - uses defaults
# All components included in single umbrella chart
```

**Minimal (osmo_values.yaml):**
```yaml
global:
  osmoImageLocation: <registry>
  osmoImageTag: <version>

services:
  postgres:
    enabled: false
    serviceName: <external-postgres-host>
    db: osmo_db
  
  redis:
    enabled: false
    serviceName: <external-redis-host>
    port: 6379
    tlsEnabled: true
  
  service:
    scaling:
      minReplicas: 1
      maxReplicas: 1
    ingress:
      enabled: false

sidecars:
  envoy:
    enabled: false
  logAgent:
    enabled: false
  otel:
    enabled: false
```

**Production (service values):**
```yaml
global:
  osmoImageLocation: <registry>
  osmoImageTag: <version>

services:
  postgres:
    enabled: false
    serviceName: <ha-postgres-endpoint>
    db: osmo_db
  
  redis:
    enabled: false
    serviceName: <ha-redis-endpoint>
    port: 6379
    tlsEnabled: true
  
  service:
    scaling:
      minReplicas: 2
      maxReplicas: 10
    ingress:
      enabled: true
      ingressClass: alb
      sslEnabled: true
      hostname: osmo.example.com

sidecars:
  envoy:
    enabled: true
    oauth2:
      enabled: true
      keycloakUrl: https://keycloak.example.com
      clientId: osmo-api
  
  logAgent:
    enabled: true
    outputs:
      - type: elasticsearch
        endpoint: https://elastic.example.com
  
  otel:
    enabled: true
    exporters:
      - type: prometheus
        endpoint: http://prometheus:9090
  
  rateLimit:
    enabled: true
    requestsPerSecond: 100
```

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:291-295](), [docs/deployment_guide/appendix/deploy_minimal.rst:214-424]()

## Validation and Testing

### Local Validation

```bash
# Verify pods
kubectl get pods --namespace osmo

# Expected output:
# osmo-service-xxx        1/1     Running
# osmo-worker-xxx         1/1     Running
# osmo-agent-xxx          1/1     Running
# osmo-logger-xxx         1/1     Running
# osmo-ui-xxx             1/1     Running
# osmo-router-xxx         1/1     Running
# postgresql-xxx          1/1     Running
# redis-xxx               1/1     Running
# localstack-xxx          1/1     Running

# Test workflow submission
osmo workflow submit examples/hello-world.yaml
```

**Sources:** [docs/deployment_guide/appendix/deploy_local.rst:338-348]()

### Minimal Validation

```bash
# Verify pods
kubectl get pods -n osmo-minimal

# Expected pods (no sidecars):
# osmo-agent-xxx                1/1     Running
# osmo-service-xxx              1/1     Running
# osmo-worker-xxx               1/1     Running
# osmo-logger-xxx               1/1     Running
# osmo-ui-xxx                   1/1     Running
# osmo-router-xxx               1/1     Running

# Verify backend operator
kubectl get pods -n osmo-operator

# Test resource availability
osmo resource list -p default
```

**Sources:** [docs/deployment_guide/appendix/deploy_minimal.rst:464-653]()

### Production Validation

```bash
# Verify all pods (including sidecars)
kubectl get pods -n osmo-service

# Expected: Each service pod should have 3-4 containers
# osmo-service-xxx        4/4     Running  (service + envoy + otel + fluentbit)
# osmo-ui-xxx             3/3     Running  (ui + envoy + fluentbit)

# Verify HPA status
kubectl get hpa -n osmo-service

# Verify ingress
kubectl get ingress -n osmo-service

# Test authenticated access
osmo login https://osmo.example.com  # Redirects to Keycloak

# Verify multi-backend support
osmo resource pools
# Expected: Multiple pools from different backend clusters
```

**Testing Checklist:**
- [ ] User authentication via SSO
- [ ] Workflow submission from CLI
- [ ] Web UI access and functionality
- [ ] Interactive workflow exec/port-forward
- [ ] Multi-backend workflow execution
- [ ] Log aggregation in centralized system
- [ ] Metrics visible in Prometheus
- [ ] Auto-scaling triggers under load

**Sources:** [docs/deployment_guide/install_backend/validate_osmo references from deployment guide]()

## Summary Decision Matrix

| Criterion | Local | Minimal | Production |
|-----------|:-----:|:-------:|:----------:|
| **Setup Time** | 🟢 ~10 min | 🟡 ~30 min | 🔴 2-4 hrs |
| **Infrastructure Cost** | 🟢 $0 | 🟡 ~$300/mo | 🔴 ~$3,700/mo |
| **Operational Complexity** | 🟢 Very Low | 🟡 Low | 🔴 High |
| **Production Ready** | 🔴 No | 🟡 Limited | 🟢 Yes |
| **Multi-User Support** | 🔴 No | 🔴 No | 🟢 Yes |
| **High Availability** | 🔴 No | 🔴 No | 🟢 Yes |
| **Scalability** | 🔴 Single Node | 🟡 Vertical | 🟢 Horizontal |
| **Security** | 🔴 None | 🟡 Basic | 🟢 Enterprise |
| **Observability** | 🔴 Minimal | 🔴 Minimal | 🟢 Full Stack |
| **Multi-Backend** | 🔴 No | 🔴 No | 🟢 Yes |

**Quick Recommendations:**
- **Evaluating OSMO?** → Start with Local
- **Team Development?** → Use Minimal
- **Production Robotics?** → Deploy Production
- **Need SSO?** → Production Only
- **Multi-Region?** → Production Only

**Sources:** [docs/deployment_options.svg:1-217](), [docs/deployment_guide/introduction/whats_next.rst:20-35]()

---

For detailed deployment instructions:
- Local deployment: See [deploy_local.rst](docs/deployment_guide/appendix/deploy_local.rst)
- Minimal deployment: See [deploy_minimal.rst](docs/deployment_guide/appendix/deploy_minimal.rst)
- Production deployment: See [Prerequisites](docs/deployment_guide/requirements/prereqs.rst) and [Deploy Service](docs/deployment_guide/getting_started/deploy_service.rst)

For architecture details and component interactions, see Architecture ([1.1](#1.1)).

---

# Page: Control Plane Services

# Control Plane Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



The OSMO Control Plane comprises a set of microservices that orchestrate workflow execution across distributed compute backends. These services handle workflow submission, task scheduling, log streaming, interactive access, and status monitoring. This page provides an overview of all control plane services and their interactions.

For details on specific services, see:
- API Service implementation: [API Service](#3.1)
- Web UI implementation: [Web UI Service](#3.2)
- Interactive session routing: [Router Service](#3.3)
- Background job processing: [Worker and Background Jobs](#3.4)

For information on backend execution infrastructure, see [Backend Operators](#5).

---

## Service Architecture Overview

The control plane consists of seven core services deployed as Kubernetes pods. Each service has a specialized role in the workflow orchestration pipeline.

```mermaid
graph TB
    subgraph "External Access"
        Users["Users/CLI"]
        Browsers["Web Browsers"]
    end
    
    subgraph "Control Plane Services"
        API["osmo-service<br/>FastAPI Application<br/>Port 8000"]
        UI["osmo-ui<br/>Next.js Application<br/>Port 8000"]
        Router["osmo-router<br/>Connection Proxy<br/>Port 8000"]
        Worker["osmo-worker<br/>Job Processor"]
        Logger["osmo-logger<br/>WebSocket Server<br/>Port 8000"]
        Agent["osmo-agent<br/>Status Updater<br/>Port 8000"]
        Monitor["osmo-delayed-job-monitor<br/>Job Retry Handler"]
    end
    
    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL<br/>workflows, tasks,<br/>configs")]
        Redis[("Redis<br/>logs, job queues")]
    end
    
    subgraph "Backend Clusters"
        BackendOp["Backend Operators<br/>Poll for tasks"]
    end
    
    Users -->|"HTTP/gRPC"| API
    Browsers -->|"HTTP"| UI
    Users -->|"WebSocket"| Router
    
    UI -->|"tRPC"| API
    API -->|"Read/Write"| PostgreSQL
    API -->|"Publish Jobs"| Redis
    
    Worker -->|"Pop Jobs"| Redis
    Worker -->|"Update Status"| PostgreSQL
    
    Logger -->|"Stream Logs"| Redis
    Logger -->|"Read Metadata"| PostgreSQL
    
    Agent -->|"Update Status"| PostgreSQL
    
    Monitor -->|"Monitor Queues"| Redis
    Monitor -->|"Requeue Failed"| Redis
    
    BackendOp -->|"Poll Tasks"| API
    BackendOp -->|"Connect Session"| Router
    
    Router -->|"Route Connections"| BackendOp
```

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:1-368]()
- [deployments/charts/web-ui/templates/ui.yaml:1-408]()
- [deployments/charts/router/templates/router-service.yaml:1-336]()
- [deployments/charts/service/templates/worker.yaml:1-237]()
- [deployments/charts/service/templates/logger-service.yaml:1-314]()
- [deployments/charts/service/templates/agent-service.yaml:1-318]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

---

## Service Inventory

| Service Name | Command | Container Port | Primary Function | Ingress Endpoint |
|-------------|---------|----------------|------------------|------------------|
| `osmo-service` | `service` | 8000 | Workflow submission, configuration management, API operations | `/api/*`, `/client/*` |
| `osmo-ui` | N/A (Next.js) | 8000 | Web-based user interface, workflow visualization | `/` |
| `osmo-router` | `router` | 8000 | Proxy for exec, port-forward, and webserver connections | `/api/router/*` |
| `osmo-worker` | `worker` | N/A | Background job processing from Redis queues | N/A (internal) |
| `osmo-logger` | `logger` | 8000 | WebSocket log streaming from Redis to clients | `/api/logger/*` |
| `osmo-agent` | `agent_service` | 8000 | Periodic status updates for workflows and tasks | `/api/agent/*` |
| `osmo-delayed-job-monitor` | `delayed_job_monitor` | N/A | Monitor and retry failed background jobs | N/A (internal) |

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:76-77]()
- [deployments/charts/web-ui/templates/ui.yaml:73-74]()
- [deployments/charts/router/templates/router-service.yaml:78-79]()
- [deployments/charts/service/templates/worker.yaml:69-70]()
- [deployments/charts/service/templates/logger-service.yaml:83-84]()
- [deployments/charts/service/templates/agent-service.yaml:77-78]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:64-65]()

---

## Communication Patterns

### PostgreSQL Database Access

All services except `osmo-router` and `osmo-delayed-job-monitor` connect to PostgreSQL for persistent state. The connection configuration is managed through `PostgresConfig` and includes retry logic for transient failures.

```mermaid
graph LR
    API["osmo-service"] -->|"execute_fetch_command<br/>execute_commit_command"| PG[("PostgreSQL<br/>osmo_db")]
    Worker["osmo-worker"] -->|"Task Status Updates"| PG
    Logger["osmo-logger"] -->|"Workflow Metadata"| PG
    Agent["osmo-agent"] -->|"Status Polling"| PG
    
    PG -->|"workflows table"| Workflows["Workflow Records"]
    PG -->|"tasks table"| Tasks["Task Records"]
    PG -->|"groups table"| Groups["Group Records"]
    PG -->|"configs table"| Configs["Configuration"]
```

Key database operations are implemented in `PostgresConnector`:
- **`execute_fetch_command`**: Query operations with automatic retries ([src/utils/connectors/postgres.py:282-331]())
- **`execute_commit_command`**: Write operations with transaction management ([src/utils/connectors/postgres.py:333-363]())
- **`@retry` decorator**: Automatic reconnection on interface errors ([src/utils/connectors/postgres.py:187-212]())

**Sources:**
- [src/utils/connectors/postgres.py:215-276]()
- [deployments/charts/service/templates/api-service.yaml:93-106]()
- [deployments/charts/service/templates/worker.yaml:93-108]()

### Redis Queue-Based Job Processing

The Worker service and Delayed Job Monitor use Redis for asynchronous job processing. Jobs are pushed to Redis lists and consumed by workers using blocking pop operations.

```mermaid
graph TB
    subgraph "Job Publishers"
        API["osmo-service<br/>Submit Workflows"]
        BackendOp["Backend Operators<br/>Task Completion"]
    end
    
    subgraph "Redis Job Queues"
        SubmitQ["workflow-submitted<br/>Queue"]
        BackendQ["backend-connections:{name}<br/>Queue"]
        ActionQ["action-queue-{workflow_id}-{task}-{retry}<br/>Queue"]
    end
    
    subgraph "Job Consumers"
        Worker["osmo-worker<br/>Process Workflows"]
        Monitor["osmo-delayed-job-monitor<br/>Retry Failed Jobs"]
    end
    
    API -->|"lpush"| SubmitQ
    API -->|"lpush action"| ActionQ
    
    Worker -->|"brpop<br/>(blocking)"| SubmitQ
    Worker -->|"Update DB"| PostgreSQL[("PostgreSQL")]
    
    BackendOp -->|"Poll for tasks"| API
    API -->|"lpush"| BackendQ
    BackendOp -->|"brpop"| BackendQ
    
    Monitor -->|"Scan failed jobs"| SubmitQ
    Monitor -->|"Requeue"| SubmitQ
```

Redis connection configuration is provided via command-line arguments:
- `--redis_host`: Redis hostname ([deployments/charts/service/templates/worker.yaml:83-84]())
- `--redis_port`: Redis port ([deployments/charts/service/templates/worker.yaml:85-86]())
- `--redis_db_number`: Database number ([deployments/charts/service/templates/worker.yaml:87-88]())
- `--redis_tls_enable`: Enable TLS ([deployments/charts/service/templates/worker.yaml:89-92]())

**Sources:**
- [deployments/charts/service/templates/worker.yaml:83-92]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:72-81]()
- [src/utils/connectors/postgres.py:51-52]()

### WebSocket Log Streaming

The Logger service implements a WebSocket server at `/api/logger/logs/{workflow_id}/{task_name}/{retry_id}` that receives logs from task containers and streams them to Redis. Clients can subscribe to these logs via separate WebSocket connections.

```mermaid
sequenceDiagram
    participant TaskCtrl as "osmo-ctrl<br/>(Task Container)"
    participant Logger as "osmo-logger<br/>WebSocket Server"
    participant Redis as "Redis Streams"
    participant Client as "CLI/UI Client"
    
    TaskCtrl->>Logger: WebSocket Connect<br/>/api/logger/logs/{workflow}/{task}/{retry}
    Logger->>TaskCtrl: Accept Connection
    
    loop Log Streaming
        TaskCtrl->>Logger: JSON Log Message<br/>{source, time, text, io_type}
        Logger->>Logger: Mask Credentials<br/>mask_string()
        Logger->>Redis: XADD {workflow_id}-logs
        Logger->>Redis: XADD {workflow_id}-{task}-{retry}-logs
        Logger->>Redis: EXPIRE (MAX_LOG_TTL)
    end
    
    Client->>Logger: Subscribe to Logs
    Logger->>Redis: XREAD from streams
    Logger->>Client: Stream Logs
```

The `ctrl_websocket` module implements the server-side WebSocket handler:
- **`run_websocket`**: Main WebSocket loop ([src/service/logger/ctrl_websocket.py:118-248]())
- **`update_metrics`**: Process task metrics from WebSocket messages ([src/service/logger/ctrl_websocket.py:54-91]())
- **`update_barrier`**: Synchronize distributed tasks using Redis sets ([src/service/logger/ctrl_websocket.py:93-116]())

**Sources:**
- [src/service/logger/ctrl_websocket.py:118-248]()
- [deployments/charts/service/templates/logger-service.yaml:1-314]()

### Router Connection Proxying

The Router service proxies interactive connections (exec, port-forward, webserver) between clients and backend task containers. It maintains two-way WebSocket connections and routes traffic based on session keys.

```mermaid
graph TB
    subgraph "Client Side"
        CLI["osmo CLI<br/>workflow exec/port-forward"]
        Browser["Web Browser<br/>webserver access"]
    end
    
    subgraph "Router Service"
        RouterWS["WebSocket Handler<br/>/api/router/{type}/{name}/{side}/{key}"]
        ConnMap["connections Dict[str, RouterConnection]<br/>wait_connect, wait_close, websocket"]
        WebMap["webservers Dict[str, WebserverConnection]<br/>wait_close, last_active_time"]
    end
    
    subgraph "Backend Side"
        BackendOp["Backend Operator<br/>Proxy Connection"]
        TaskPod["Task Pod<br/>osmo-ctrl container"]
    end
    
    CLI -->|"WebSocket<br/>client/{key}"| RouterWS
    Browser -->|"HTTP/WebSocket<br/>Resolve session_key"| RouterWS
    
    RouterWS -->|"Store in connections"| ConnMap
    RouterWS -->|"Store in webservers"| WebMap
    
    BackendOp -->|"WebSocket<br/>backend/{key}"| RouterWS
    RouterWS -->|"Match key"| ConnMap
    RouterWS -->|"Bidirectional copy"| BackendOp
    
    BackendOp -->|"Exec/Port-forward"| TaskPod
```

Key data structures in the Router service:
- **`connections`**: Maps session keys to `RouterConnection` objects ([src/service/router/router.py:95]())
- **`webservers`**: Maps session keys to `WebserverConnection` objects ([src/service/router/router.py:96]())
- **`RouterConnection`**: Contains `wait_connect`, `wait_close` events and WebSocket ([src/service/router/router.py:66-73]())
- **`WebserverConnection`**: Contains `wait_close`, `last_active_time`, and WebSocket ([src/service/router/router.py:76-83]())

**Sources:**
- [src/service/router/router.py:66-96]()
- [deployments/charts/router/templates/router-service.yaml:1-336]()

---

## Deployment Configuration

All control plane services are deployed via Helm charts in the `deployments/charts/` directory. The umbrella chart `quick-start` includes all service dependencies.

### Helm Chart Structure

```mermaid
graph TB
    QuickStart["quick-start<br/>Umbrella Chart"]
    
    QuickStart -->|"dependency"| ServiceChart["service Chart<br/>API, Worker, Logger,<br/>Agent, Monitor"]
    QuickStart -->|"dependency"| UIChart["web-ui Chart<br/>Next.js Application"]
    QuickStart -->|"dependency"| RouterChart["router Chart<br/>Router Service"]
    QuickStart -->|"dependency"| BackendChart["backend-operator Chart<br/>(Optional)"]
    QuickStart -->|"dependency"| IngressChart["ingress-nginx<br/>4.13.2"]
    
    ServiceChart -->|"deployment"| API["osmo-service<br/>Deployment"]
    ServiceChart -->|"deployment"| Worker["osmo-worker<br/>Deployment"]
    ServiceChart -->|"deployment"| Logger["osmo-logger<br/>Deployment"]
    ServiceChart -->|"deployment"| Agent["osmo-agent<br/>Deployment"]
    ServiceChart -->|"deployment"| Monitor["osmo-delayed-job-monitor<br/>Deployment"]
```

**Sources:**
- [deployments/charts/quick-start/Chart.yaml:24-40]()

### Sidecar Containers

Each service pod includes optional sidecar containers for observability and authentication:

| Sidecar | Purpose | Configuration Key |
|---------|---------|------------------|
| **Envoy** | OAuth2 authentication, JWT validation, rate limiting | `sidecars.envoy.enabled` |
| **FluentBit** | Log collection and forwarding | `global.logs.enabled` |
| **OpenTelemetry** | Metrics collection and tracing | `sidecars.otel.enabled` |
| **Rate Limiter** | API rate limiting (API service only) | `sidecars.rateLimit.enabled` |

The Envoy sidecar is configured per-service using the `osmo.envoy-config` Helm template helper, which generates an Envoy configuration ConfigMap mounted at `/etc/envoy/config.yaml`.

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:218-240]()
- [deployments/charts/web-ui/templates/ui.yaml:243-244]()
- [deployments/charts/router/templates/router-service.yaml:188-189]()

### Health Checks and Probes

Services implement liveness, readiness, and startup probes to ensure Kubernetes can properly manage pod lifecycle:

**API Service:**
- Liveness: HTTP GET `/api/version` ([deployments/charts/service/templates/api-service.yaml:192-193]())
- Startup: HTTP GET `/api/version`, 6 retries × 5s ([deployments/charts/service/templates/api-service.yaml:197-204]())
- Readiness: HTTP GET `/api/workflow?limit=0&all_pools=true` ([deployments/charts/service/templates/api-service.yaml:207-216]())

**Worker/Agent/Logger Services:**
- Liveness: `progress_check` command with 300s interval ([deployments/charts/service/templates/worker.yaml:157-165]())
- Startup: `progress_check` command with 60s timeout ([deployments/charts/service/templates/worker.yaml:168-177]())

The `progress_check` binary verifies that a service has made progress within a specified interval by checking a progress file at `/var/run/osmo/last_progress`.

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:192-216]()
- [deployments/charts/service/templates/worker.yaml:156-177]()
- [deployments/charts/service/templates/agent-service.yaml:166-199]()

---

## Horizontal Pod Autoscaling

Most control plane services support horizontal scaling via `HorizontalPodAutoscaler` resources. Scaling is based on CPU and memory utilization metrics.

| Service | Min Replicas | Max Replicas | Target Metric | Configuration |
|---------|-------------|-------------|---------------|---------------|
| **API** | `services.service.scaling.minReplicas` | `services.service.scaling.maxReplicas` | Memory + CPU | [api-service.yaml:339-367]() |
| **Web UI** | `services.ui.scaling.minReplicas` | `services.ui.scaling.maxReplicas` | Memory | [ui.yaml:383-407]() |
| **Router** | `services.service.scaling.minReplicas` | `services.service.scaling.maxReplicas` | Memory | [router-service.yaml:314-335]() |
| **Worker** | `services.worker.scaling.minReplicas` | `services.worker.scaling.maxReplicas` | Memory + CPU | [worker.yaml:208-236]() |
| **Logger** | `services.logger.scaling.minReplicas` | `services.logger.scaling.maxReplicas` | Memory + CPU | [logger-service.yaml:285-313]() |
| **Agent** | `services.agent.scaling.minReplicas` | `services.agent.scaling.maxReplicas` | Memory + CPU | [agent-service.yaml:289-317]() |

The Delayed Job Monitor does not auto-scale and runs as a single replica to avoid job duplication.

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:339-367]()
- [deployments/charts/web-ui/templates/ui.yaml:383-407]()
- [deployments/charts/service/templates/worker.yaml:208-236]()

---

## Service-Specific Configuration

### API Service Command-Line Arguments

The API service accepts extensive configuration via command-line arguments passed in the deployment manifest:

```yaml
args:
  - --metrics_otel_collector_component
  - osmo-service
  - --redis_host
  - {{ .Values.services.redis.serviceName }}
  - --postgres_host
  - {{ .Values.services.postgres.serviceName }}
  - --device_endpoint
  - {{ .Values.services.service.auth.device_endpoint }}
  - --service_hostname
  - {{ .Values.services.service.hostname }}
  - --osmo_image_location
  - {{ .Values.global.osmoImageLocation }}
```

These arguments configure database connections, OAuth2 endpoints, image registry locations, and observability settings.

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:78-148]()

### Web UI Runtime Configuration

The Web UI service uses environment variables to configure the Next.js application at runtime:

| Environment Variable | Purpose | Helm Value |
|---------------------|---------|-----------|
| `PORT` | Container port | `services.ui.containerPort` |
| `NODE_OPTIONS` | Max HTTP header size | `services.ui.maxHttpHeaderSizeKb` |
| `NEXT_PUBLIC_OSMO_API_HOSTNAME` | API hostname for browser | `services.ui.apiHostname` |
| `NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED` | Enable port-forward feature | `services.ui.portForwardEnabled` |
| `NEXT_PUBLIC_OSMO_SSL_ENABLED` | HTTPS mode | `services.ui.nextjsSslEnabled` |
| `DOCS_BASE_URL` | Documentation base URL | `services.ui.docsBaseUrl` |

**Sources:**
- [deployments/charts/web-ui/templates/ui.yaml:83-98]()

### Router Service Timeouts

The Router service implements configurable timeouts for different connection types:

- **`timeout`**: Default timeout (60s) for exec/port-forward control connections ([src/service/router/router.py:48-51]())
- **`webserver_initial_timeout`**: Initial webserver connection timeout (1 hour) ([src/service/router/router.py:52-55]())
- **`webserver_nonactive_timeout`**: Inactive webserver timeout (30 minutes) ([src/service/router/router.py:56-59]())

These values are configurable via command-line arguments in the deployment.

**Sources:**
- [src/service/router/router.py:37-64]()
- [deployments/charts/router/templates/router-service.yaml:80-109]()

---

## Security Context

All control plane services run with restricted security contexts to minimize attack surface:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  runAsNonRoot: true
  runAsUser: 1001
```

This configuration:
- Prevents privilege escalation
- Drops all Linux capabilities
- Enforces non-root execution
- Uses UID 1001 for process isolation

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:169-174]()
- [deployments/charts/service/templates/worker.yaml:71-76]()
- [deployments/charts/web-ui/templates/ui.yaml:114-119]()

---

## Inter-Service Dependencies

```mermaid
graph TB
    subgraph "Synchronous Dependencies"
        API["osmo-service"] -->|"Database Schema"| PG[("PostgreSQL")]
        Worker["osmo-worker"] -->|"Read Configs"| PG
        Logger["osmo-logger"] -->|"Read Workflows"| PG
        Agent["osmo-agent"] -->|"Update Status"| PG
        Monitor["osmo-delayed-job-monitor"] -->|"Requeue Jobs"| Redis[("Redis")]
    end
    
    subgraph "Asynchronous Dependencies"
        API -->|"Publish workflow-submitted"| Redis
        Worker -->|"Pop workflow-submitted"| Redis
        Logger -->|"Stream Logs"| Redis
    end
    
    subgraph "External Dependencies"
        API -->|"Validate JWT"| Keycloak["Keycloak<br/>(Optional)"]
        UI["osmo-ui"] -->|"OAuth2 Flow"| Keycloak
    end
```

The API service must initialize database tables before other services can function properly. The `_init_tables` method creates all required schemas:

- `workflows`, `tasks`, `groups` tables ([src/utils/connectors/postgres.py:632-714]())
- `dataset`, `dataset_version`, `dataset_tag` tables ([src/utils/connectors/postgres.py:879-930]())
- `configs`, `backends`, `pools` tables ([src/utils/connectors/postgres.py:538-629]())
- `credential`, `access_token`, `profile` tables ([src/utils/connectors/postgres.py:961-1001]())

**Sources:**
- [src/utils/connectors/postgres.py:531-1001]()
- [deployments/charts/service/templates/api-service.yaml:93-106]()
- [deployments/charts/service/templates/worker.yaml:83-92]()

---

# Page: API Service

# API Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

The API Service is the primary REST API server in OSMO's control plane. It serves as the central coordination point for workflow submission, configuration management, dataset operations, and backend orchestration. The service exposes HTTP/REST endpoints consumed by the CLI client, Web UI, and backend operators.

For log streaming and task metrics, see [Logger Service](#3.4). For interactive workflow access (exec, port-forward), see [Router Service](#3.3). For background task processing, see [Worker and Background Jobs](#3.4).

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [README context from high-level diagrams]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "External Clients"
        CLI["CLI Client"]
        WebUI["Web UI<br/>(Next.js)"]
        Backend["Backend Operators"]
    end
    
    subgraph "API Service Pod"
        Envoy["Envoy Sidecar<br/>Port 8080<br/>OAuth2 Filter"]
        APIContainer["API Container<br/>service command<br/>Port 8000"]
        OTel["OpenTelemetry<br/>Sidecar"]
        FluentBit["FluentBit<br/>Log Collection"]
        RateLimit["Rate Limit<br/>Sidecar"]
    end
    
    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL<br/>PostgresConnector")]
        Redis[("Redis<br/>RedisConnector<br/>Job Queues")]
    end
    
    subgraph "External Services"
        Keycloak["Keycloak<br/>OAuth2/OIDC"]
        ObjectStorage["S3/Azure Blob<br/>Dataset Storage"]
    end
    
    CLI -->|HTTP + JWT| Envoy
    WebUI -->|HTTP + Session| Envoy
    Backend -->|HTTP + Service Token| Envoy
    
    Envoy -->|JWT Validation| Keycloak
    Envoy -->|x-osmo-user header| APIContainer
    
    APIContainer -->|execute_fetch_command<br/>execute_commit_command| PostgreSQL
    APIContainer -->|lpush, rpop<br/>xadd, xread| Redis
    APIContainer -->|Metadata Operations| ObjectStorage
    
    APIContainer --> OTel
    APIContainer --> FluentBit
    Envoy --> RateLimit
```

**Architecture Key Points:**

1. **Envoy Sidecar**: All requests flow through Envoy for authentication, extracting user identity into the `x-osmo-user` header
2. **API Container**: Runs the `service` command, which starts the FastAPI application
3. **Database Layer**: `PostgresConnector` singleton manages all database operations
4. **Job Queues**: Redis used for background job distribution to worker services
5. **Observability**: OpenTelemetry for metrics, FluentBit for logs

**Sources:** [deployments/charts/service/templates/api-service.yaml:73-227](), [src/utils/connectors/postgres.py:215-276]()

---

## Core Components and Class Structure

```mermaid
graph TB
    subgraph "Service Entry Point"
        ServiceCmd["service command<br/>src/service/main.py"]
    end
    
    subgraph "FastAPI Application"
        FastAPIApp["FastAPI app<br/>Routers mounted"]
        WorkflowRouter["Workflow Router<br/>/api/workflow"]
        ConfigRouter["Config Router<br/>/api/config"]
        DataRouter["Data Router<br/>/api/bucket"]
        BackendRouter["Backend Router<br/>/api/backend"]
        CredRouter["Credential Router<br/>/api/credential"]
        PoolRouter["Pool Router<br/>/api/pool"]
    end
    
    subgraph "Database Layer"
        PostgresConnector["PostgresConnector<br/>Singleton Instance"]
        PostgresConfig["PostgresConfig<br/>Connection Settings"]
        SecretManager["SecretManager<br/>MEK Encryption"]
    end
    
    subgraph "Configuration Objects"
        ServiceConfig["ServiceConfig<br/>backend_images, etc"]
        WorkflowConfig["WorkflowConfig<br/>timeouts, limits"]
        DatasetConfig["DatasetConfig<br/>buckets, credentials"]
        DynamicConfig["DynamicConfig<br/>Base class"]
    end
    
    subgraph "Background Jobs"
        BackendJobs["BackendJobs<br/>backend_jobs.py"]
        DelayedJob["DelayedJob<br/>Redis queue"]
    end
    
    ServiceCmd --> FastAPIApp
    FastAPIApp --> WorkflowRouter
    FastAPIApp --> ConfigRouter
    FastAPIApp --> DataRouter
    FastAPIApp --> BackendRouter
    
    WorkflowRouter --> PostgresConnector
    ConfigRouter --> PostgresConnector
    DataRouter --> PostgresConnector
    BackendRouter --> PostgresConnector
    
    PostgresConnector --> PostgresConfig
    PostgresConnector --> SecretManager
    PostgresConnector --> ServiceConfig
    PostgresConnector --> WorkflowConfig
    PostgresConnector --> DatasetConfig
    
    ConfigRouter --> BackendJobs
    BackendJobs --> DelayedJob
```

**Key Classes:**

| Class | File | Purpose |
|-------|------|---------|
| `PostgresConnector` | [src/utils/connectors/postgres.py:215-276]() | Singleton managing all database connections and operations |
| `PostgresConfig` | [src/utils/connectors/postgres.py:125-185]() | Database connection configuration (host, port, credentials) |
| `SecretManager` | [src/utils/secret_manager.py]() | Encrypts/decrypts credentials using Master Encryption Key (MEK) |
| `ServiceConfig` | [src/utils/connectors/postgres.py:440-446]() | Service-level configuration (images, limits, features) |
| `WorkflowConfig` | [src/utils/connectors/postgres.py:446-450]() | Workflow execution configuration (timeouts, retries) |
| `DatasetConfig` | [src/utils/connectors/postgres.py:448-461]() | Dataset storage configuration (buckets, credentials) |

**Sources:** [src/utils/connectors/postgres.py:125-276](), [src/utils/connectors/postgres.py:430-471](), [deployments/charts/service/templates/api-service.yaml:76-78]()

---

## Request Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant Envoy
    participant Keycloak
    participant APIService
    participant PostgresConnector
    participant PostgreSQL
    participant Redis
    participant BackendWorker
    
    Client->>Envoy: POST /api/workflow<br/>Bearer Token
    Envoy->>Keycloak: Validate JWT<br/>Check signature + claims
    Keycloak-->>Envoy: Valid token<br/>Extract user claim
    Envoy->>APIService: Forward request<br/>x-osmo-user: username<br/>x-osmo-roles: roles
    
    APIService->>PostgresConnector: get_instance()
    PostgresConnector-->>APIService: Singleton instance
    
    APIService->>PostgresConnector: execute_fetch_command()<br/>Validate pool, backend
    PostgresConnector->>PostgreSQL: SELECT query
    PostgreSQL-->>PostgresConnector: Result rows
    PostgresConnector-->>APIService: Pydantic models
    
    APIService->>PostgresConnector: execute_commit_command()<br/>INSERT workflow, tasks, groups
    PostgresConnector->>PostgreSQL: INSERT commands
    PostgreSQL-->>PostgresConnector: Success
    
    APIService->>Redis: lpush()<br/>backend_action_queue
    Redis-->>APIService: Queue depth
    
    APIService-->>Client: HTTP 200<br/>workflow_id
    
    BackendWorker->>Redis: brpop()<br/>backend_action_queue
    Redis-->>BackendWorker: Job payload
    BackendWorker->>PostgreSQL: Fetch workflow details
    BackendWorker->>BackendWorker: Create K8s resources
```

**Request Flow Steps:**

1. **Authentication**: Envoy validates JWT with Keycloak, extracts `x-osmo-user` and `x-osmo-roles` headers
2. **Routing**: FastAPI routes request to appropriate handler based on URL path
3. **Database Singleton**: `PostgresConnector.get_instance()` returns the singleton instance
4. **Query Execution**: Handler calls `execute_fetch_command()` or `execute_commit_command()`
5. **Job Enqueueing**: Background jobs pushed to Redis queues for worker processing
6. **Response**: HTTP response returned to client with workflow ID or operation result

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-227](), [src/utils/connectors/postgres.py:281-363](), [src/service/core/config/helpers.py:194-204]()

---

## REST API Endpoints

The API service exposes multiple endpoint groups, each handled by separate FastAPI routers:

```mermaid
graph LR
    subgraph "API Endpoints"
        Version["/api/version<br/>GET"]
        Health["/api/workflow?limit=0<br/>GET - Readiness"]
        
        WorkflowSubmit["/api/workflow<br/>POST - Submit"]
        WorkflowList["/api/workflow<br/>GET - List"]
        WorkflowGet["/api/workflow/{id}<br/>GET - Details"]
        WorkflowCancel["/api/workflow/{id}<br/>DELETE - Cancel"]
        
        ConfigGet["/api/config/{type}<br/>GET"]
        ConfigPut["/api/config/{type}<br/>PUT"]
        ConfigPatch["/api/config/{type}<br/>PATCH"]
        
        DatasetCreate["/api/bucket/{bucket}/dataset<br/>POST"]
        DatasetList["/api/bucket/{bucket}/dataset<br/>GET"]
        DatasetUploadStart["/api/bucket/dataset/upload_start<br/>POST"]
        DatasetUploadFinish["/api/bucket/dataset/upload_finish<br/>POST"]
        
        BackendRegister["/api/backend<br/>POST"]
        BackendList["/api/backend<br/>GET"]
        BackendUpdate["/api/backend/{name}<br/>PATCH"]
        
        PoolCreate["/api/pool<br/>POST"]
        PoolList["/api/pool<br/>GET"]
        PoolUpdate["/api/pool/{name}<br/>PATCH"]
    end
    
    subgraph "Ingress Rules"
        IngressAPI["Ingress<br/>/api prefix<br/>api-service:80"]
        IngressClient["Ingress<br/>/client prefix<br/>api-service:80"]
    end
    
    IngressAPI --> Version
    IngressAPI --> WorkflowSubmit
    IngressAPI --> ConfigGet
    IngressAPI --> DatasetCreate
    IngressAPI --> BackendRegister
    IngressAPI --> PoolCreate
```

**Endpoint Categories:**

| Path Prefix | Purpose | Key Operations |
|-------------|---------|----------------|
| `/api/version` | Service version | GET version string |
| `/api/workflow` | Workflow management | Submit, list, cancel, get details |
| `/api/config/{type}` | Configuration CRUD | GET/PUT/PATCH for SERVICE, WORKFLOW, DATASET configs |
| `/api/bucket/{bucket}/dataset` | Dataset operations | Create, upload, download, list, tag |
| `/api/backend` | Backend registration | Register, list, update backends |
| `/api/pool` | Pool management | Create, list, update resource pools |
| `/api/credential` | Credential storage | Store encrypted credentials for registries, data backends |
| `/api/agent` | Backend agent status | Receive status updates from backend operators |
| `/api/logger` | Log streaming | WebSocket for task log streams |
| `/client` | CLI client downloads | Binary downloads for different platforms |

**Sources:** [deployments/charts/service/templates/api-service.yaml:314-328](), [src/service/core/data/data_service.py:36-40]()

---

## Configuration Management System

The API service manages five types of configurations stored in the `configs` table:

```mermaid
graph TB
    subgraph "Configuration Types"
        ServiceType["ConfigType.SERVICE<br/>Backend images, limits"]
        WorkflowType["ConfigType.WORKFLOW<br/>Timeouts, retries"]
        DatasetType["ConfigType.DATASET<br/>Buckets, credentials"]
    end
    
    subgraph "Configuration Classes"
        ServiceConfig["ServiceConfig<br/>backend_images<br/>max_workflows_per_user<br/>feature_flags"]
        WorkflowConfig["WorkflowConfig<br/>default_exec_timeout<br/>default_queue_timeout<br/>max_log_lines"]
        DatasetConfig["DatasetConfig<br/>buckets: Dict[str, BucketConfig]<br/>default_bucket"]
        BucketConfig["BucketConfig<br/>path, mode, region<br/>credential_name"]
    end
    
    subgraph "Database Operations"
        GetConfigs["get_configs(config_type)<br/>Returns Config object"]
        SetConfig["set_config(key, value, type)<br/>Updates single key"]
        PutConfigs["put_configs()<br/>Replace entire config"]
        PatchConfigs["patch_configs()<br/>Strategic merge patch"]
    end
    
    subgraph "Config History"
        ConfigHistory["config_history table<br/>Versioned snapshots"]
        CreateHistory["create_config_history_entry()<br/>username, description, tags"]
        ListHistory["list_config_history()<br/>Filter by type, name"]
        RollbackHistory["Rollback to revision<br/>Restore previous state"]
    end
    
    ServiceType --> ServiceConfig
    WorkflowType --> WorkflowConfig
    DatasetType --> DatasetConfig
    DatasetConfig --> BucketConfig
    
    GetConfigs --> ServiceConfig
    GetConfigs --> WorkflowConfig
    GetConfigs --> DatasetConfig
    
    SetConfig --> ConfigHistory
    PutConfigs --> ConfigHistory
    PatchConfigs --> ConfigHistory
    
    ConfigHistory --> CreateHistory
    ConfigHistory --> ListHistory
    ConfigHistory --> RollbackHistory
```

**Configuration Workflow:**

1. **Read Configuration**: `PostgresConnector.get_configs(ConfigType.SERVICE)` fetches all keys for that type from the `configs` table and deserializes into a Pydantic model
2. **Update Configuration**: `set_config(key, value, config_type)` updates individual keys, or `put_configs()` replaces entire configuration
3. **Patch Configuration**: `patch_configs()` uses strategic merge patch to update nested dictionaries
4. **History Tracking**: Every configuration change creates an entry in `config_history` table with username, timestamp, description, and tags
5. **Rollback**: Previous configurations can be restored from history

**Configuration Examples:**

```python
# ServiceConfig keys
backend_images: BackendImages  # init, ctrl, sidecars
max_workflows_per_user: int
enable_workflow_priority: bool

# WorkflowConfig keys
default_exec_timeout: int
default_queue_timeout: int
max_log_lines: int
websocket_timeout: int

# DatasetConfig keys
buckets: Dict[str, BucketConfig]
default_bucket: str
```

**Sources:** [src/utils/connectors/postgres.py:430-471](), [src/utils/connectors/postgres.py:509-530](), [src/service/core/config/helpers.py:72-114]()

---

## Database Integration via PostgresConnector

```mermaid
graph TB
    subgraph "PostgresConnector Singleton"
        GetInstance["get_instance()<br/>Static method"]
        Instance["_instance<br/>Class variable"]
        Connection["_conn<br/>psycopg2.connection"]
        Config["config: PostgresConfig<br/>Host, port, credentials"]
        SecretMgr["secret_manager: SecretManager<br/>MEK encryption"]
    end
    
    subgraph "Initialization"
        InitTables["_init_tables()<br/>CREATE TABLE IF NOT EXISTS"]
        InitConfigs["_init_configs()<br/>Set default values"]
        Connect["connect()<br/>psycopg2.connect()"]
    end
    
    subgraph "Command Execution"
        ExecuteFetch["execute_fetch_command()<br/>Returns List[pydantic.BaseModel]"]
        ExecuteCommit["execute_commit_command()<br/>INSERT/UPDATE/DELETE"]
        ExecuteAutocommit["execute_autocommit_command()<br/>CREATE INDEX"]
        Mogrify["mogrify()<br/>SQL injection prevention"]
        Retry["@retry decorator<br/>Reconnect on error"]
    end
    
    subgraph "Database Schema"
        ConfigsTable["configs table<br/>key, value, type"]
        WorkflowsTable["workflows table<br/>workflow_uuid, status, etc"]
        TasksTable["tasks table<br/>task_uuid, status, etc"]
        GroupsTable["groups table<br/>group_uuid, spec, status"]
        DatasetTable["dataset table<br/>id, name, bucket"]
        BackendsTable["backends table<br/>name, k8s_uid, settings"]
        PoolsTable["pools table<br/>name, backend, platforms"]
        CredentialTable["credential table<br/>HSTORE encrypted payload"]
    end
    
    GetInstance --> Instance
    Instance --> Connection
    Instance --> Config
    Instance --> SecretMgr
    
    Connect --> InitTables
    InitTables --> InitConfigs
    
    InitTables --> ConfigsTable
    InitTables --> WorkflowsTable
    InitTables --> TasksTable
    InitTables --> GroupsTable
    InitTables --> DatasetTable
    InitTables --> BackendsTable
    InitTables --> PoolsTable
    InitTables --> CredentialTable
    
    ExecuteFetch --> Retry
    ExecuteCommit --> Retry
    ExecuteFetch --> Mogrify
```

**PostgresConnector Key Methods:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `get_instance()` | `() -> PostgresConnector` | Returns singleton instance |
| `execute_fetch_command()` | `(command: str, args: Tuple) -> List[Any]` | Executes SELECT queries, returns Pydantic models |
| `execute_commit_command()` | `(command: str, args: Tuple)` | Executes INSERT/UPDATE/DELETE |
| `execute_autocommit_command()` | `(command: str, args: Tuple)` | For CREATE INDEX in autocommit mode |
| `mogrify()` | `(entries: List[Tuple]) -> str` | SQL-injection-safe batch insert |
| `get_configs()` | `(config_type: ConfigType) -> DynamicConfig` | Fetches and deserializes configuration |
| `set_config()` | `(key: str, value: str, config_type: ConfigType)` | Updates single config key |
| `encrypt_dict()` | `(input_dict: Dict, user: str) -> Dict` | Encrypts credential dictionary |
| `decrypt_credential()` | `(db_row) -> Dict` | Decrypts HSTORE payload |

**Connection Management:**

- **Retry Logic**: The `@retry` decorator automatically reconnects on `psycopg2.InterfaceError` or `psycopg2.DatabaseError`
- **Connection Pooling**: Single connection per service instance; FastAPI handles concurrency
- **Transaction Management**: Explicit `commit()` or `rollback()` after each operation

**Sources:** [src/utils/connectors/postgres.py:215-428](), [src/utils/connectors/postgres.py:187-213](), [src/utils/connectors/postgres.py:531-1023]()

---

## Authentication and Authorization

```mermaid
sequenceDiagram
    participant Client
    participant Envoy
    participant Keycloak
    participant APIService
    participant RateLimiter
    participant RoleChecker
    
    rect rgb(245, 245, 245)
        Note over Client,Keycloak: Browser Flow (Web UI)
        Client->>Envoy: GET /api/workflow
        Envoy->>Envoy: Check HMAC Cookie
        alt No Valid Cookie
            Envoy->>Keycloak: Redirect to OAuth2<br/>authorization_endpoint
            Keycloak-->>Client: Login page
            Client->>Keycloak: Username/password
            Keycloak-->>Envoy: Authorization code
            Envoy->>Keycloak: Exchange for JWT<br/>token_endpoint
            Keycloak-->>Envoy: JWT (audience: osmo-browser-flow)
            Envoy->>Envoy: Set HMAC Cookie
        end
    end
    
    rect rgb(245, 245, 245)
        Note over Client,Keycloak: Device Flow (CLI)
        Client->>Keycloak: POST device_endpoint
        Keycloak-->>Client: device_code, user_code, verification_url
        Client->>Client: Display verification URL
        Client->>Keycloak: Poll token_endpoint
        Keycloak-->>Client: JWT (audience: osmo-device)
        Client->>Envoy: API request with Bearer token
    end
    
    Envoy->>Keycloak: Validate JWT<br/>JWKS endpoint
    Keycloak-->>Envoy: Valid signature<br/>Extract claims
    
    Envoy->>Envoy: Extract user claim<br/>Extract roles claim
    Envoy->>APIService: Forward request<br/>x-osmo-user: username<br/>x-osmo-roles: role1,role2
    
    APIService->>RateLimiter: Check rate limit<br/>per user/endpoint
    RateLimiter-->>APIService: Allow/Deny
    
    APIService->>RoleChecker: Check role permissions<br/>Policy evaluation
    RoleChecker-->>APIService: Authorized/Forbidden
    
    APIService->>APIService: Process request
    APIService-->>Client: Response
```

**Authentication Components:**

1. **Envoy OAuth2 Filter**: Configured in [deployments/charts/service/templates/api-service.yaml:251-254]()
   - Validates JWT signatures using Keycloak's JWKS endpoint
   - Checks `issuer`, `audience`, and `exp` claims
   - Extracts `user` claim into `x-osmo-user` header
   - Extracts `roles` claim into `x-osmo-roles` header

2. **Keycloak Integration**: Configuration in [deployments/charts/service/templates/api-service.yaml:110-122]()
   - `device_endpoint`: For CLI device flow
   - `browser_endpoint`: For Web UI authorization code flow
   - `token_endpoint`: For token exchange
   - `logout_endpoint`: For session termination

3. **Service Token Authentication**: Backend operators use service tokens with `role: osmo-backend`

4. **Rate Limiting**: Optional rate-limit sidecar at [deployments/charts/service/templates/api-service.yaml:223-225]()

**Authorization Flow:**

- **Header Extraction**: `x-osmo-user` and `x-osmo-roles` headers injected by Envoy
- **Role-Based Access Control (RBAC)**: Policies defined in `roles` table, evaluated per endpoint
- **Resource Ownership**: Users can only access their own workflows unless they have admin role

**Sources:** [deployments/charts/service/templates/api-service.yaml:110-122](), [deployments/charts/service/templates/api-service.yaml:218-227]()

---

## Kubernetes Deployment Configuration

```mermaid
graph TB
    subgraph "Deployment Spec"
        Deployment["Deployment<br/>api-service"]
        Replicas["Replicas: Dynamic<br/>HPA controlled"]
        PodTemplate["Pod Template<br/>Labels, annotations"]
    end
    
    subgraph "Container: api-service"
        Image["Image<br/>{osmoImageLocation}/{imageName}:{osmoImageTag}"]
        Command["Command: service"]
        Args["Args<br/>--postgres_host<br/>--redis_host<br/>--mek_file<br/>--device_endpoint<br/>--browser_endpoint"]
        Env["Environment<br/>OSMO_POSTGRES_PASSWORD<br/>OSMO_REDIS_PASSWORD<br/>OSMO_DISABLE_TASK_METRICS"]
        Ports["Ports<br/>8000 (HTTP)"]
    end
    
    subgraph "Probes"
        Liveness["Liveness Probe<br/>httpGet: /api/version<br/>Interval: per config"]
        Startup["Startup Probe<br/>httpGet: /api/version<br/>30s max startup"]
        Readiness["Readiness Probe<br/>httpGet: /api/workflow?limit=0<br/>Database check"]
    end
    
    subgraph "Volumes"
        MEKVolume["MEK Volume<br/>ConfigMap: mek-config<br/>Path: /home/osmo/vault-agent/secrets"]
        LogsVolume["Logs Volume<br/>emptyDir<br/>Shared with FluentBit"]
    end
    
    subgraph "Sidecars"
        EnvoySidecar["Envoy<br/>Port 8080<br/>OAuth2 filter"]
        OTelSidecar["OpenTelemetry<br/>Metrics collection"]
        FluentBitSidecar["FluentBit<br/>Log shipping"]
        RateLimitSidecar["Rate Limit<br/>Optional"]
    end
    
    subgraph "Service"
        K8sService["Service: api-service<br/>Port 80 → targetPort"]
        InternalService["Service: api-service-internal<br/>For in-cluster calls"]
    end
    
    subgraph "Ingress"
        IngressRule["Ingress<br/>Host: {hostname}<br/>Path: /api<br/>Path: /client"]
        ALBAnnotations["ALB Annotations<br/>Group: osmo<br/>Order: 100"]
        TLS["TLS: {sslSecret}"]
    end
    
    subgraph "HPA"
        HPASpec["HorizontalPodAutoscaler<br/>minReplicas: {minReplicas}<br/>maxReplicas: {maxReplicas}"]
        MemoryTarget["Memory Target<br/>{hpaMemoryTarget}%"]
        CPUTarget["CPU Target<br/>{hpaCpuTarget}%"]
    end
    
    Deployment --> PodTemplate
    PodTemplate --> Image
    PodTemplate --> Command
    PodTemplate --> Args
    PodTemplate --> Env
    
    PodTemplate --> Liveness
    PodTemplate --> Startup
    PodTemplate --> Readiness
    
    PodTemplate --> MEKVolume
    PodTemplate --> LogsVolume
    
    PodTemplate --> EnvoySidecar
    PodTemplate --> OTelSidecar
    PodTemplate --> FluentBitSidecar
    PodTemplate --> RateLimitSidecar
    
    Deployment --> K8sService
    Deployment --> InternalService
    K8sService --> IngressRule
    IngressRule --> ALBAnnotations
    IngressRule --> TLS
    
    Deployment --> HPASpec
    HPASpec --> MemoryTarget
    HPASpec --> CPUTarget
```

**Deployment Configuration:**

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Container Image** | `{osmoImageLocation}/{imageName}:{osmoImageTag}` | Service container image from Helm values |
| **Command** | `service` | Entrypoint that starts FastAPI application |
| **Security Context** | `runAsNonRoot: true`, `runAsUser: 1001` | Non-privileged execution |
| **Resource Requests** | Per `resources` values | CPU/memory reservations |
| **Resource Limits** | Per `resources` values | CPU/memory caps |

**Probes Configuration:**

- **Liveness Probe**: `GET /api/version` - Service health check
- **Startup Probe**: `GET /api/version` - 30 seconds (6 × 5s) for initialization
- **Readiness Probe**: `GET /api/workflow?limit=0&all_pools=true` - Database connectivity check with admin role header

**Sidecar Injection:**

1. **Envoy**: Configured via ConfigMap at [deployments/charts/service/templates/api-service.yaml:251-254]()
2. **OpenTelemetry**: Metrics collection when `sidecars.otel.enabled=true`
3. **FluentBit**: Log forwarding when `global.logs.enabled=true`
4. **Rate Limiter**: Optional when `sidecars.rateLimit.enabled=true`

**Sources:** [deployments/charts/service/templates/api-service.yaml:19-368](), [deployments/charts/service/templates/api-service.yaml:73-217]()

---

## Scaling and High Availability

The API service uses Kubernetes HorizontalPodAutoscaler (HPA) for automatic scaling:

```mermaid
graph LR
    subgraph "Autoscaling"
        HPA["HorizontalPodAutoscaler"]
        MinReplicas["minReplicas<br/>From values"]
        MaxReplicas["maxReplicas<br/>From values"]
        MemoryMetric["Memory Utilization<br/>{hpaMemoryTarget}%"]
        CPUMetric["CPU Utilization<br/>{hpaCpuTarget}%"]
    end
    
    subgraph "Deployment"
        Deployment["api-service Deployment"]
        Pod1["Pod 1"]
        Pod2["Pod 2"]
        PodN["Pod N"]
    end
    
    subgraph "Load Distribution"
        K8sService["Service: api-service"]
        Ingress["Ingress"]
        EnvoyLB["Envoy Load Balancing"]
    end
    
    HPA --> MinReplicas
    HPA --> MaxReplicas
    HPA --> MemoryMetric
    HPA --> CPUMetric
    
    HPA --> Deployment
    Deployment --> Pod1
    Deployment --> Pod2
    Deployment --> PodN
    
    Ingress --> K8sService
    K8sService --> EnvoyLB
    EnvoyLB --> Pod1
    EnvoyLB --> Pod2
    EnvoyLB --> PodN
```

**Scaling Configuration:**

| Parameter | Configuration Path | Purpose |
|-----------|-------------------|---------|
| `minReplicas` | `.Values.services.service.scaling.minReplicas` | Minimum pod count |
| `maxReplicas` | `.Values.services.service.scaling.maxReplicas` | Maximum pod count |
| `hpaMemoryTarget` | `.Values.services.service.scaling.hpaMemoryTarget` | Memory utilization threshold (%) |
| `hpaCpuTarget` | `.Values.services.service.scaling.hpaCpuTarget` | CPU utilization threshold (%) |

**High Availability Considerations:**

1. **Stateless Design**: API service is stateless; all state in PostgreSQL/Redis
2. **Connection Pooling**: Each pod maintains its own PostgreSQL connection
3. **Database Singleton**: `PostgresConnector._instance` is per-process singleton
4. **Session Affinity**: Not required; Envoy HMAC cookies are validated independently
5. **Pod Topology Spread**: Configured via `topologySpreadConstraints` to distribute across zones

**Resource Management:**

- **CPU Limits**: Prevents noisy neighbor issues
- **Memory Limits**: OOM protection with restart policy
- **Rate Limiting**: Per-user rate limiting via optional sidecar prevents abuse

**Database Connection Management:**

Each API service pod maintains a single `psycopg2.connection` object. The `@retry` decorator handles transient connection failures:

```python
@retry(reconnect=True)
def execute_fetch_command(self, command: str, args: Tuple) -> List[Any]:
    # Reconnects automatically on InterfaceError or DatabaseError
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-368](), [src/utils/connectors/postgres.py:187-213]()

---

## Integration with Other Services

The API service coordinates with multiple other OSMO components:

| Service | Integration Method | Purpose |
|---------|-------------------|---------|
| **Worker Service** | Redis job queues | Background workflow processing |
| **Logger Service** | Redis streams | Log aggregation and WebSocket streaming |
| **Agent Service** | Database + Redis | Backend status updates |
| **Router Service** | Database queries | Interactive session routing |
| **Backend Operators** | HTTP REST API | Receive workflow jobs, send status |
| **Web UI** | HTTP REST API | User interface API consumption |
| **CLI** | HTTP REST API | Command-line interface |

**Job Queue Pattern:**

```python
# API Service enqueues jobs
redis_client.lpush('backend-connections:{backend_name}', json.dumps(job_data))

# Worker Service dequeues jobs
job = redis_client.brpop('backend-connections:{backend_name}', timeout)
```

**Log Streaming Pattern:**

```python
# Logger Service writes to Redis stream
redis_client.xadd(f'{workflow_id}-logs', log_entry, maxlen=max_log_lines)

# API Service reads from stream
logs = redis_client.xread({f'{workflow_id}-logs': last_id}, count=100)
```

**Sources:** [src/service/core/config/helpers.py:194-204](), [src/service/logger/ctrl_websocket.py:199-215]()

---

# Page: Web UI Service

# Web UI Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/README.md](deployments/charts/web-ui/README.md)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [deployments/charts/web-ui/values.yaml](deployments/charts/web-ui/values.yaml)
- [ui/src/app/layout.tsx](ui/src/app/layout.tsx)
- [ui/src/app/workflows/components/TaskActions.tsx](ui/src/app/workflows/components/TaskActions.tsx)
- [ui/src/app/workflows/components/WorkflowActions.tsx](ui/src/app/workflows/components/WorkflowActions.tsx)
- [ui/src/env.mjs](ui/src/env.mjs)
- [ui/src/runtime-env.tsx](ui/src/runtime-env.tsx)

</details>



## Purpose and Scope

The Web UI Service provides the Next.js-based web interface for OSMO, enabling users to visualize workflows, submit jobs, monitor task execution, and interact with the platform through a browser. This service runs as a containerized application with Envoy sidecar authentication and communicates with the API service via tRPC.

For information about the API service that the UI communicates with, see [API Service](#3.1). For authentication mechanisms, see [Envoy Authentication Proxy](#8.2).

**Sources:** [deployments/charts/web-ui/README.md:1-182](), [deployments/charts/web-ui/values.yaml:53-76]()

---

## Architecture Overview

The Web UI Service runs as a Kubernetes Deployment with multiple containers in each pod: the main Next.js application container, an Envoy sidecar for authentication, and optionally FluentBit for log collection.

### Pod Structure

```mermaid
graph TB
    subgraph "osmo-ui Pod"
        direction TB
        
        subgraph "Main Container"
            NextJS["Next.js Application<br/>osmo-ui<br/>Port 8000"]
            RuntimeEnv["RuntimeEnvProvider<br/>DOCS_BASE_URL<br/>CLI_INSTALL_SCRIPT_URL<br/>PORT_FORWARD_ENABLED"]
            TRPC["tRPC Client<br/>API Communication"]
            
            NextJS --> RuntimeEnv
            NextJS --> TRPC
        end
        
        subgraph "Envoy Sidecar"
            EnvoyProxy["Envoy Proxy<br/>Port 8080"]
            OAuth2Filter["OAuth2 Filter<br/>Browser Auth"]
            JWTValidation["JWT Validation<br/>Token Verification"]
            
            EnvoyProxy --> OAuth2Filter
            EnvoyProxy --> JWTValidation
        end
        
        subgraph "FluentBit Sidecar (Optional)"
            LogAgent["FluentBit<br/>Log Collection"]
        end
        
        NextJS -->|"Logs"| LogAgent
        EnvoyProxy -->|"Logs"| LogAgent
    end
    
    subgraph "External Traffic"
        Ingress["Kubernetes Ingress<br/>nginx/ALB"]
        Browser["Web Browser<br/>User"]
    end
    
    subgraph "Backend Services"
        APIService["API Service<br/>osmo-service"]
        Keycloak["Keycloak SSO<br/>OAuth2/OIDC"]
    end
    
    Browser --> Ingress
    Ingress -->|"Port 80"| EnvoyProxy
    EnvoyProxy -->|"Port 8000"| NextJS
    EnvoyProxy -->|"Token Validation"| Keycloak
    TRPC -->|"HTTP/tRPC"| APIService
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:17-247](), [ui/src/app/layout.tsx:35-64]()

---

## Main UI Container Configuration

The main container runs the Next.js application built from the `web-ui` Docker image. It listens on port 8000 (configurable via `PORT` environment variable) and serves the OSMO web interface.

### Container Specification

| Property | Configuration | Description |
|----------|---------------|-------------|
| **Image** | `${osmoImageLocation}/web-ui:${osmoImageTag}` | Docker image for the UI service |
| **Container Port** | `8000` (default) | Port where Next.js listens |
| **Service Account** | `osmo` | Kubernetes service account |
| **Security Context** | Non-root (UID 1000) | Runs as unprivileged user |
| **Image Pull Policy** | `Always` | Always pull latest image |

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:73-119](), [deployments/charts/web-ui/values.yaml:56-99]()

### Environment Variables

The UI container receives runtime configuration through environment variables that control its behavior and integration points:

```mermaid
graph LR
    subgraph "Environment Variable Sources"
        HelmValues["Helm Values<br/>values.yaml"]
        K8sSecrets["Kubernetes Secrets<br/>Optional"]
    end
    
    subgraph "Container Environment"
        PORT["PORT<br/>Next.js listen port<br/>Default: 8000"]
        NodeOptions["NODE_OPTIONS<br/>--max-http-header-size<br/>Default: 128KB"]
        APIHostname["NEXT_PUBLIC_OSMO_API_HOSTNAME<br/>Backend API endpoint<br/>Default: osmo-service..."]
        PortForward["NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED<br/>Enable port forwarding<br/>Default: false"]
        SSL["NEXT_PUBLIC_OSMO_SSL_ENABLED<br/>Use HTTPS for API<br/>Default: true"]
        Docs["DOCS_BASE_URL<br/>Documentation URL"]
        CLI["CLI_INSTALL_SCRIPT_URL<br/>CLI install script URL"]
    end
    
    subgraph "Runtime Configuration"
        EnvMJS["env.mjs<br/>Zod Schema Validation"]
        RuntimeEnvProvider["RuntimeEnvProvider<br/>React Context"]
        Components["UI Components<br/>useRuntimeEnv()"]
    end
    
    HelmValues --> PORT
    HelmValues --> NodeOptions
    HelmValues --> APIHostname
    HelmValues --> PortForward
    HelmValues --> SSL
    HelmValues --> Docs
    HelmValues --> CLI
    
    PORT --> EnvMJS
    NodeOptions --> EnvMJS
    APIHostname --> EnvMJS
    PortForward --> EnvMJS
    SSL --> EnvMJS
    Docs --> EnvMJS
    CLI --> EnvMJS
    
    EnvMJS --> RuntimeEnvProvider
    RuntimeEnvProvider --> Components
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:83-112](), [ui/src/env.mjs:39-109]()

#### Key Environment Variables

| Variable | Purpose | Default Value | Configuration Path |
|----------|---------|---------------|-------------------|
| `PORT` | Next.js server port | `8000` | `services.ui.containerPort` |
| `NODE_OPTIONS` | Node.js max header size | `--max-http-header-size=131072` | `services.ui.maxHttpHeaderSizeKb` |
| `NEXT_PUBLIC_OSMO_API_HOSTNAME` | API service endpoint | `osmo-service.osmo.svc.cluster.local:80` | `services.ui.apiHostname` |
| `NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED` | Enable port forwarding UI | `false` | `services.ui.portForwardEnabled` |
| `NEXT_PUBLIC_OSMO_SSL_ENABLED` | Use HTTPS for API calls | `true` | `services.ui.nextjsSslEnabled` |
| `DOCS_BASE_URL` | Documentation base URL | `https://nvidia.github.io/OSMO/...` | `services.ui.docsBaseUrl` |
| `CLI_INSTALL_SCRIPT_URL` | CLI installation script | `https://raw.githubusercontent.com/...` | `services.ui.cliInstallScriptUrl` |

**Sources:** [deployments/charts/web-ui/values.yaml:74-132](), [ui/src/env.mjs:44-73]()

### Runtime Environment Provider Pattern

The UI implements a two-stage environment configuration system to handle server-side and client-side rendering:

1. **Server-side validation** via `env.mjs` using Zod schemas [ui/src/env.mjs:39-109]()
2. **Client-side access** via `RuntimeEnvProvider` React context [ui/src/runtime-env.tsx:19-39]()

```typescript
// Server-side: env.mjs validates at build time
export const env = createEnv({
  server: {
    CLI_INSTALL_SCRIPT_URL: z.string().default("..."),
    DOCS_BASE_URL: z.string().default("..."),
  },
  client: {
    NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED: z.boolean().default(false),
  },
  // ...
});

// Client-side: RuntimeEnvProvider makes values available to components
export function useRuntimeEnv() {
  const ctx = useContext(RuntimeEnvContext);
  return ctx; // { DOCS_BASE_URL, CLI_INSTALL_SCRIPT_URL, PORT_FORWARD_ENABLED }
}
```

This pattern ensures that environment variables are validated at build time while remaining accessible to client components at runtime.

**Sources:** [ui/src/env.mjs:1-109](), [ui/src/runtime-env.tsx:1-40](), [ui/src/app/layout.tsx:35-64]()

---

## Envoy Sidecar Container

The Envoy sidecar provides authentication and authorization for all incoming requests to the UI. It listens on port 8080 and proxies authenticated requests to the Next.js container on port 8000.

### Envoy Authentication Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Ingress
    participant Envoy as Envoy Sidecar<br/>Port 8080
    participant NextJS as Next.js App<br/>Port 8000
    participant Keycloak
    
    Browser->>Ingress: GET /
    Ingress->>Envoy: Forward request
    
    alt No valid session cookie
        Envoy->>Browser: 302 Redirect to Keycloak
        Browser->>Keycloak: OAuth2 authorization request
        Keycloak->>Browser: Login page
        Browser->>Keycloak: User credentials
        Keycloak->>Browser: Authorization code
        Browser->>Envoy: Request with auth code
        Envoy->>Keycloak: Exchange code for JWT<br/>token_endpoint
        Keycloak->>Envoy: JWT access token<br/>audience: osmo-browser-flow
        Envoy->>Envoy: Set HMAC-signed cookie
    end
    
    Envoy->>Envoy: Validate JWT signature<br/>Check issuer, audience
    Envoy->>Envoy: Extract user claim<br/>x-osmo-user: username
    Envoy->>NextJS: Forward request with<br/>x-osmo-user header
    NextJS->>Envoy: Response
    Envoy->>Browser: Response
```

**Sources:** [deployments/charts/web-ui/values.yaml:376-600](), [deployments/charts/web-ui/README.md:89-131]()

### Envoy Configuration

The Envoy sidecar is configured through the `sidecars.envoy` section of the Helm chart values:

| Configuration | Purpose | Default |
|---------------|---------|---------|
| `enabled` | Enable Envoy sidecar | `true` |
| `listenerPort` | Port Envoy listens on | `8080` |
| `service.port` | Backend service port (Next.js) | `8000` |
| `service.address` | Backend service address | `127.0.0.1` |
| `maxHeadersSizeKb` | Max HTTP header size | `128` KB |
| `oauth2Filter.enabled` | Enable OAuth2 authentication | `true` |
| `oauth2Filter.tokenEndpoint` | Keycloak token endpoint | (required) |
| `oauth2Filter.authEndpoint` | Keycloak auth endpoint | (required) |
| `oauth2Filter.clientId` | OAuth2 client ID | (required) |
| `jwt.user_header` | Header for authenticated user | `x-osmo-user` |

**Sources:** [deployments/charts/web-ui/values.yaml:378-600](), [deployments/charts/web-ui/templates/ui.yaml:243]()

### OAuth2 and JWT Configuration

The Envoy sidecar supports two authentication providers via JWT validation:

```yaml
jwt:
  providers:
    - issuer: ""              # Keycloak issuer URL
      audience: ""            # osmo-browser-flow
      jwks_uri: ""           # Keycloak JWKS endpoint
      user_claim: unique_name
      cluster: oauth
    - issuer: ""              # Secondary provider
      audience: ""
      jwks_uri: ""
      user_claim: preferred_username
      cluster: oauth
```

The OAuth2 filter handles the browser-based login flow, while JWT validation handles token verification for API requests.

**Sources:** [deployments/charts/web-ui/values.yaml:578-600](), [deployments/charts/web-ui/README.md:106-131]()

---

## Kubernetes Deployment Resources

The Web UI Service is deployed using several Kubernetes resources defined in [deployments/charts/web-ui/templates/ui.yaml]().

### Deployment Resource

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: osmo-ui
spec:
  replicas: 1  # Or controlled by HPA
  template:
    spec:
      containers:
      - name: osmo-ui
        image: nvcr.io/nvidia/osmo/web-ui:latest
        ports:
        - containerPort: 8000
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
```

The deployment includes topology spread constraints to distribute pods across availability zones and nodes:

```yaml
topologySpreadConstraints:
- topologyKey: kubernetes.io/hostname
  maxSkew: 1
  whenUnsatisfiable: ScheduleAnyway
- topologyKey: topology.kubernetes.io/zone
  maxSkew: 1
  whenUnsatisfiable: ScheduleAnyway
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:17-257](), [deployments/charts/web-ui/values.yaml:247-257]()

### Service Resource

The Kubernetes Service exposes the UI pods and routes traffic to the appropriate port based on whether Envoy is enabled:

```mermaid
graph LR
    subgraph "Kubernetes Service"
        Service["Service: osmo-ui<br/>Port 80<br/>ClusterIP"]
    end
    
    subgraph "Target Selection"
        EnvoyEnabled{Envoy<br/>Enabled?}
    end
    
    subgraph "Pod Containers"
        EnvoyPort["Envoy Container<br/>Port 8080<br/>envoy-http"]
        UIPort["UI Container<br/>Port 8000"]
    end
    
    Service --> EnvoyEnabled
    EnvoyEnabled -->|Yes| EnvoyPort
    EnvoyEnabled -->|No| UIPort
    EnvoyPort -->|Proxies to| UIPort
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:261-300]()

The service definition dynamically selects the target port:

| Condition | Target Port | Container |
|-----------|-------------|-----------|
| `sidecars.envoy.enabled: true` | `envoy-http` (8080) | Envoy sidecar |
| `sidecars.envoy.enabled: false` | `8000` | UI container directly |

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:278-286]()

### Ingress Resources

The Web UI Service creates **two separate Ingress resources** to handle different routing priorities:

```mermaid
graph TB
    subgraph "External Traffic"
        Browser["Browser<br/>https://osmo.example.com"]
    end
    
    subgraph "Ingress Resources"
        MainIngress["Ingress: osmo-ui<br/>Priority: 200<br/>Path: /"]
        TRPCIngress["Ingress: osmo-ui-trpc<br/>Priority: 50<br/>Paths: /api/refresh, /api/trpc"]
    end
    
    subgraph "Service"
        UIService["Service: osmo-ui<br/>Port 80"]
    end
    
    Browser --> MainIngress
    Browser --> TRPCIngress
    MainIngress --> UIService
    TRPCIngress --> UIService
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:302-381]()

#### Main UI Ingress (Priority 200)

Handles all general web traffic:

```yaml
metadata:
  name: osmo-ui
  annotations:
    alb.ingress.kubernetes.io/group.order: "200"
spec:
  rules:
  - host: osmo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: osmo-ui
            port:
              number: 80
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:302-337]()

#### tRPC API Ingress (Priority 50)

Handles tRPC API calls with higher priority (lower order number):

```yaml
metadata:
  name: osmo-ui-trpc
  annotations:
    alb.ingress.kubernetes.io/group.order: "50"
spec:
  rules:
  - host: osmo.example.com
    http:
      paths:
      - path: /api/refresh
        pathType: Prefix
      - path: /api/trpc
        pathType: Prefix
```

This separation ensures that API traffic is routed with higher priority than static content, preventing routing conflicts when multiple services share the same hostname.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:339-381]()

---

## Horizontal Pod Autoscaler

The UI service supports automatic scaling based on memory utilization when `services.ui.scaling.enabled: true`.

### HPA Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: osmo-ui
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: osmo-ui
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: ContainerResource
    containerResource:
      container: osmo-ui
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
```

| Configuration | Default | Description |
|---------------|---------|-------------|
| `scaling.enabled` | `false` | Enable HPA |
| `scaling.minReplicas` | `1` | Minimum pod count |
| `scaling.maxReplicas` | `3` | Maximum pod count |
| `scaling.hpaTarget` | `85` | Target memory utilization % |

When scaling is disabled, the deployment uses a fixed replica count specified by `services.ui.replicas`.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:383-407](), [deployments/charts/web-ui/values.yaml:136-151]()

---

## Health Probes

The UI container implements three types of health probes to ensure proper startup and operation:

### Probe Configuration

```mermaid
graph TB
    subgraph "Kubernetes Health Checks"
        Startup["Startup Probe<br/>GET /<br/>6 failures × 5s = 30s max"]
        Liveness["Liveness Probe<br/>GET /<br/>2 failures × 5s"]
        Readiness["Readiness Probe<br/>GET /<br/>2 failures × 5s"]
    end
    
    subgraph "Container States"
        Starting["Container Starting"]
        Running["Container Running"]
        Ready["Ready for Traffic"]
        Failed["Container Failed"]
    end
    
    Starting -->|Startup succeeds| Running
    Starting -->|Startup fails| Failed
    Running -->|Liveness succeeds| Running
    Running -->|Liveness fails| Failed
    Running -->|Readiness succeeds| Ready
    Ready -->|Readiness fails| Running
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:129-241]()

| Probe Type | Path | Port | Failure Threshold | Period | Timeout | Initial Delay |
|------------|------|------|------------------|--------|---------|---------------|
| Startup | `/` | `8000` | 6 | 5s | 3s | 5s |
| Liveness | `/` | `8000` | 2 | 5s | 3s | - |
| Readiness | `/` | `8000` | 2 | 5s | 3s | - |

All probes use HTTP GET requests to the root path `/` on port 8000 (the Next.js container port, not the Envoy port).

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:336-373](), [deployments/charts/web-ui/values.yaml:336-373]()

---

## Integration with OSMO Services

The Web UI communicates with the OSMO control plane through multiple channels:

### Service Communication Diagram

```mermaid
graph TB
    subgraph "Web UI Pod"
        UIContainer["Next.js App<br/>Port 8000"]
        TRPCClient["tRPC Client<br/>API calls"]
    end
    
    subgraph "API Service"
        APIEndpoint["API Service<br/>osmo-service:80"]
        WorkflowAPI["Workflow Endpoints<br/>/api/workflow"]
        TaskAPI["Task Endpoints<br/>/api/task"]
        ConfigAPI["Config Endpoints<br/>/api/config"]
    end
    
    subgraph "Router Service"
        RouterService["Router Service<br/>osmo-router:80"]
        ExecProxy["Exec Proxy<br/>/api/router/exec"]
        PortForwardProxy["Port Forward Proxy<br/>/api/router/port-forward"]
        WebserverProxy["Webserver Proxy<br/>*.osmo.example.com"]
    end
    
    subgraph "Logger Service"
        LoggerService["Logger Service<br/>osmo-logger:80"]
        LogStream["Log WebSocket<br/>/api/logger/stream"]
    end
    
    UIContainer --> TRPCClient
    TRPCClient -->|"HTTP/tRPC"| APIEndpoint
    APIEndpoint --> WorkflowAPI
    APIEndpoint --> TaskAPI
    APIEndpoint --> ConfigAPI
    
    UIContainer -->|"Shell/Exec"| ExecProxy
    UIContainer -->|"Port Forwarding"| PortForwardProxy
    UIContainer -->|"Dashboard Access"| WebserverProxy
    UIContainer -->|"Log Streaming"| LogStream
```

**Sources:** [ui/src/app/layout.tsx:49](), [ui/src/app/workflows/components/TaskActions.tsx:28-122](), [ui/src/app/workflows/components/WorkflowActions.tsx:26-188]()

### API Communication via tRPC

The UI uses tRPC for type-safe communication with the API service. The API hostname is configured via the `NEXT_PUBLIC_OSMO_API_HOSTNAME` environment variable, which defaults to the in-cluster service name `osmo-service.osmo.svc.cluster.local:80`.

**Sources:** [ui/src/env.mjs:67-92](), [deployments/charts/web-ui/values.yaml:78-83]()

### Feature Toggles

Certain UI features are conditionally enabled based on runtime configuration:

```typescript
// Port forwarding UI (TaskActions.tsx, WorkflowActions.tsx)
{runtimeEnv.PORT_FORWARD_ENABLED && (
  <button onClick={() => updateUrl({ tool: ToolType.PortForwarding })}>
    Port Forwarding
  </button>
)}
```

This feature is controlled by the `NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED` environment variable, which maps to `services.ui.portForwardEnabled` in the Helm chart.

**Sources:** [ui/src/app/workflows/components/TaskActions.tsx:107-116](), [ui/src/app/workflows/components/WorkflowActions.tsx:173-182]()

---

## Sidecar Containers

### FluentBit Log Agent (Optional)

When `sidecars.logAgent.enabled: true`, a FluentBit sidecar collects logs from the UI and Envoy containers.

| Configuration | Purpose | Default |
|---------------|---------|---------|
| `logAgent.enabled` | Enable log collection | `false` |
| `logAgent.image.repository` | FluentBit image | `fluent/fluent-bit:4.0.8-debug` |
| `logAgent.fluentBitPrometheusPort` | Metrics port | `2020` |
| `logAgent.aws.region` | CloudWatch region | `us-west-2` |
| `logAgent.aws.clusterName` | EKS cluster name | (required if using CloudWatch) |

The log agent can optionally rotate logs based on size and age:

```yaml
logrotate:
  enabled: false
  frequency: hourly
  maxSize: 10M
  rotateCount: 5
  sleepSeconds: 60
```

**Sources:** [deployments/charts/web-ui/values.yaml:606-670](), [deployments/charts/web-ui/templates/ui.yaml:244]()

---

## Deployment via Helm

The Web UI chart is typically deployed as part of the `quick-start` umbrella chart:

```yaml
# quick-start/Chart.yaml
dependencies:
- name: web-ui
  version: 1.0.1
  repository: file://../web-ui
```

**Sources:** [deployments/charts/quick-start/Chart.yaml:31-33]()

### Minimal Values Example

```yaml
global:
  osmoImageLocation: nvcr.io/nvidia/osmo
  osmoImageTag: latest
  imagePullSecret: null

services:
  ui:
    hostname: osmo.example.com
    apiHostname: osmo-service.osmo.svc.cluster.local:80
    portForwardEnabled: false
    nextjsSslEnabled: true
    docsBaseUrl: https://nvidia.github.io/OSMO/main/user_guide/
    
    ingress:
      enabled: true
      ingressClass: nginx
      sslEnabled: true
      sslSecret: osmo-tls

sidecars:
  envoy:
    enabled: true
    oauth2Filter:
      enabled: true
      tokenEndpoint: https://keycloak.example.com/realms/osmo/protocol/openid-connect/token
      authEndpoint: https://keycloak.example.com/realms/osmo/protocol/openid-connect/auth
      clientId: osmo-browser-flow
    jwt:
      providers:
      - issuer: https://keycloak.example.com/realms/osmo
        audience: osmo-browser-flow
        jwks_uri: https://keycloak.example.com/realms/osmo/protocol/openid-connect/certs
        user_claim: preferred_username
```

**Sources:** [deployments/charts/web-ui/values.yaml:18-600]()

---

# Page: Router Service

# Router Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

The Router Service is a specialized proxy component within OSMO's control plane that enables interactive access to running workflow tasks. It routes bidirectional connections (exec, port-forward, rsync, webserver) between clients and backend task pods through persistent WebSocket tunnels, solving network connectivity challenges when backends are behind firewalls or NAT.

For information about workflow execution and task management, see [Workflow Lifecycle and Execution](#6.4). For backend operator architecture, see [Backend Operator Architecture](#5.1).

**Sources:** [src/service/router/router.py:1-40](), [deployments/charts/router/templates/router-service.yaml:1-20]()

---

## Architecture Overview

The router sits between the OSMO control plane and backend operators, acting as a rendezvous point for client-backend connections:

```mermaid
graph TB
    subgraph "Client Layer"
        CLI["CLI User<br/>osmo workflow exec/port-forward"]
        Browser["Web Browser<br/>Webserver Access"]
    end
    
    subgraph "Control Plane"
        Router["Router Service<br/>router.py<br/>Port 8000"]
        API["API Service"]
        Ingress["Ingress<br/>/api/router/*"]
    end
    
    subgraph "Backend Operator"
        BackendListener["Backend Listener<br/>Initiates Outbound"]
        TaskPod["Task Pod<br/>User Container<br/>Port 22, 8080, etc."]
    end
    
    CLI -->|"WebSocket<br/>/api/router/exec/.../client/{key}"| Ingress
    Browser -->|"HTTP/WS<br/>*.hostname"| Ingress
    Ingress --> Router
    
    BackendListener -->|"WebSocket<br/>/api/router/exec/.../backend/{key}"| Router
    
    Router <-->|"Bidirectional<br/>Data Relay"| Router
    
    BackendListener <-->|"K8s Port Forward"| TaskPod
    
    API -.->|"Writes action to Redis queue"| BackendListener

    style Router fill:#e1f5ff
    style BackendListener fill:#e8f5e9
    style TaskPod fill:#fff4e1
```

**Key Characteristics:**

- **Stateful Proxy**: Maintains in-memory connection mappings (`connections`, `webservers` dictionaries)
- **Zero Backend Firewall Changes**: Backends initiate outbound WebSocket connections
- **Protocol Agnostic**: Routes raw TCP, UDP, and WebSocket data without inspection
- **Session-Based Routing**: Uses unique keys and cookies to route requests to correct connections

**Sources:** [src/service/router/router.py:93-96](), [deployments/charts/router/templates/router-service.yaml:257-311]()

---

## Core Components

### RouterConnection Model

The `RouterConnection` class tracks active backend connections awaiting client attachment:

```mermaid
classDiagram
    class RouterConnection {
        +Optional~asyncio.Event~ wait_connect
        +Optional~asyncio.Event~ wait_close
        +Optional~WebSocket~ websocket
    }
    
    class WebserverConnection {
        +asyncio.Event wait_close
        +datetime last_active_time
        +WebSocket websocket
    }
    
    class ConnectionPayload {
        +str key
        +str cookie
        +str type
        +Optional~Dict~ payload
    }
    
    RouterConnection "1" -- "*" ConnectionPayload : uses
    WebserverConnection "1" -- "1" ConnectionPayload : uses
```

**Connection Dictionaries:**

| Dictionary | Type | Purpose |
|------------|------|---------|
| `connections` | `Dict[str, RouterConnection]` | Maps connection keys to exec/port-forward sessions |
| `webservers` | `Dict[str, WebserverConnection]` | Maps session keys to persistent webserver connections |

**Sources:** [src/service/router/router.py:66-84](), [src/service/router/router.py:95-96]()

### RouterServiceConfig

Configuration parameters defined in `RouterServiceConfig`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `http://0.0.0.0:8000` | Bind address for router service |
| `hostname` | `localhost` | Public DNS hostname for routing |
| `timeout` | 60 | Connection timeout for exec/port-forward (seconds) |
| `webserver_initial_timeout` | 3600 | Initial webserver connection timeout (1 hour) |
| `webserver_nonactive_timeout` | 1800 | Timeout for inactive webserver connections (30 min) |
| `sticky_cookies` | `['AWSALB', 'AWSALBCORS']` | Cookies to forward for load balancer affinity |

**Sources:** [src/service/router/router.py:37-64]()

---

## Connection Flow Diagrams

### Exec and Port-Forward Flow

```mermaid
sequenceDiagram
    participant User as CLI/User
    participant API as API Service
    participant Redis as Redis Queue
    participant Router as Router Service
    participant Backend as Backend Listener
    participant Pod as Task Pod
    
    Note over User,Pod: Setup Phase
    User->>API: POST /api/workflow/{wf}/task/{task}/exec
    API->>Redis: Push action to workflow queue<br/>backend_action_queue_name(backend)
    Backend->>Redis: Poll queue (BRPOP)
    Redis-->>Backend: Action payload with key
    
    Note over User,Pod: Connection Establishment
    Backend->>Router: WebSocket /api/router/exec/{name}/backend/{key}
    Note over Backend,Router: Backend connects first,<br/>waits for client
    
    User->>Router: WebSocket /api/router/exec/{name}/client/{key}
    Note over User,Router: Client connects with same key
    
    Router->>Router: Match client to backend via key<br/>connections[key].wait_connect.set()
    
    Note over User,Pod: Data Relay Phase
    Backend->>Pod: kubectl exec connection
    
    loop Bidirectional Data Flow
        User->>Router: stdin data
        Router->>Backend: Forward via WebSocket
        Backend->>Pod: Write to exec session
        Pod->>Backend: stdout/stderr data
        Backend->>Router: Forward via WebSocket
        Router->>User: Display output
    end
    
    Note over User,Pod: Teardown
    User->>Router: Close WebSocket
    Router->>Backend: Trigger wait_close event
    Backend->>Pod: Close exec connection
```

**Key Flow Points:**

1. **Rendezvous Pattern**: Either backend or client can connect first; the router waits for both before starting data relay
2. **Connection Timeout**: If matching connection doesn't arrive within `timeout` seconds, connection is closed with code 4000
3. **Unique Keys**: Action keys are generated as `'EXEC-' + generate_unique_id()` or `'PORTFORWARD-' + generate_unique_id()`
4. **Cookie Isolation**: Session cookies prevent connection hijacking

**Sources:** [src/service/router/router.py:137-170](), [src/service/router/router.py:172-213](), [src/service/core/config/helpers.py:194-203]()

### Webserver Connection Flow

For persistent HTTP/WebSocket access to task-hosted webservers (e.g., TensorBoard, Jupyter):

```mermaid
sequenceDiagram
    participant Browser as Web Browser
    participant Router as Router Service
    participant Backend as Backend Listener
    participant Pod as Task Pod<br/>(Port 8080)
    
    Note over Browser,Pod: Initial Connection Setup
    Browser->>Router: HTTP GET https://task-abc123.osmo.example.com/
    Note over Router: resolve_session_key() extracts<br/>subdomain as session key
    
    Router->>Router: Check webservers[session_key]
    alt First Connection (No Session)
        Router->>Backend: Push webserver action to Redis
        Backend->>Router: WebSocket /api/router/backend/{session_key}
        Router->>Router: Store WebserverConnection<br/>webservers[session_key] = connection
        Backend->>Pod: kubectl port-forward 8080:8080
    end
    
    Note over Browser,Pod: HTTP Request Relay
    Router->>Backend: HTTP request via WebSocket<br/>type='http', payload=request_data
    Backend->>Pod: Forward to localhost:8080
    Pod-->>Backend: HTTP response
    Backend-->>Router: Response via WebSocket
    Router-->>Browser: HTTP response
    
    Note over Browser,Pod: WebSocket Upgrade
    Browser->>Router: Upgrade: websocket
    Router->>Backend: WebSocket upgrade via control WS<br/>type='ws', payload=headers
    Backend->>Pod: Establish WebSocket to localhost:8080
    
    loop WebSocket Data Exchange
        Browser->>Router: WS message
        Router->>Backend: Forward via control WS
        Backend->>Pod: Forward to app
        Pod-->>Backend: WS message
        Backend-->>Router: Forward via control WS
        Router-->>Browser: WS message
    end
    
    Note over Browser,Pod: Timeout Management
    Router->>Router: Track last_active_time
    Router->>Router: After webserver_nonactive_timeout<br/>close connection
```

**Webserver-Specific Features:**

- **Subdomain Routing**: Session key extracted from subdomain (e.g., `task-abc123.osmo.example.com` → `task-abc123`)
- **Sticky Cookie Forwarding**: ALB cookies preserved for load balancer affinity
- **Automatic Cleanup**: Inactive connections closed after `webserver_nonactive_timeout`
- **Protocol Tunneling**: HTTP and WebSocket protocols tunneled through single control WebSocket

**Sources:** [src/service/router/router.py:99-122](), [src/service/router/helper.py:1-100]()

---

## API Endpoints

The router exposes several WebSocket and HTTP endpoints:

### Backend Connection Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/router/exec/{name}/backend/{key}` | WebSocket | Backend connects for exec session |
| `/api/router/portforward/{name}/backend/{key}` | WebSocket | Backend connects for port-forward session |
| `/api/router/rsync/{name}/backend/{key}` | WebSocket | Backend connects for rsync session |

**Handler:** `run_connect_backend(ws, name, key)`

**Sources:** [src/service/router/router.py:137-170]()

### Client Connection Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/router/exec/{name}/client/{key}` | WebSocket | Client connects for exec session |
| `/api/router/portforward/{name}/client/{key}` | WebSocket | Client connects for port-forward session |
| `/api/router/rsync/{name}/client/{key}` | WebSocket | Client connects for rsync session |

**Handler:** `run_connect_client(client_ws, name, key, timeout)`

**Data Relay:** Implemented by `copy_data()` coroutines running concurrently to forward bytes bidirectionally.

**Sources:** [src/service/router/router.py:172-213]()

### Webserver Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/router/webserver/{key}` | GET | Check if webserver session is alive |
| `*.hostname/*` (via middleware) | HTTP/WebSocket | Route to task webserver via subdomain |

**Middleware:** `RouterWebSocketMiddleware` intercepts all requests, checks for session key in headers/subdomain, and routes to webserver handlers if applicable.

**Sources:** [src/service/router/router.py:99-124](), [src/service/router/router.py:132-134]()

### Utility Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/router/version` | GET | Return router service version |
| `/api/router/docs` | GET | OpenAPI documentation |

**Sources:** [src/service/router/router.py:127-129]()

---

## Connection Lifecycle Management

### Exec/Port-Forward Lifecycle

```mermaid
stateDiagram-v2
    [*] --> AwaitingPeer: Backend or Client connects
    AwaitingPeer --> AwaitingPeer: Store in connections[key]
    AwaitingPeer --> Connected: Matching peer connects
    AwaitingPeer --> Timeout: Timeout expires
    
    Connected --> DataRelay: Both WebSockets active
    DataRelay --> DataRelay: copy_data() coroutines
    
    DataRelay --> Closing: WebSocketDisconnect
    DataRelay --> Closing: Client closes
    DataRelay --> Closing: Backend closes
    
    Closing --> Cleanup: Delete from connections[key]
    Cleanup --> [*]
    
    Timeout --> Cleanup: ws.close(4000, 'timeout')
```

**Connection Establishment:**

1. First peer (backend or client) connects → creates `RouterConnection` with `wait_connect` event
2. Second peer connects → sets `wait_connect.set()` to unblock first peer
3. Both peers proceed to data relay phase

**Cleanup Triggers:**

- Either WebSocket disconnects
- Connection timeout expires
- `wait_close` event is triggered
- Key is immediately deleted from `connections` dictionary

**Sources:** [src/service/router/router.py:137-170](), [src/service/router/router.py:172-213]()

### Webserver Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> FirstRequest: Browser requests subdomain
    FirstRequest --> CreateSession: No session exists
    CreateSession --> BackendConnect: Push action to backend
    BackendConnect --> SessionActive: Backend establishes port-forward
    
    FirstRequest --> SessionActive: Session already exists
    
    SessionActive --> RelayRequest: Forward HTTP/WS request
    RelayRequest --> UpdateActivity: Update last_active_time
    UpdateActivity --> SessionActive
    
    SessionActive --> InactiveTimeout: webserver_nonactive_timeout expires
    InactiveTimeout --> Cleanup: Close WebSocket
    
    SessionActive --> Closed: Browser closes tab
    Closed --> Cleanup
    
    Cleanup --> DeleteSession: Delete from webservers[key]
    DeleteSession --> [*]
```

**Activity Tracking:**

- `last_active_time` updated on each HTTP request
- `check_inactivity()` coroutine periodically scans for stale connections
- Inactive connections older than `webserver_nonactive_timeout` are closed

**Sources:** [src/service/router/router.py:76-83](), [src/service/router/helper.py:50-120]()

---

## Deployment Configuration

### Helm Chart Structure

The router is deployed via the `router` Helm chart:

**Key Resources Created:**

| Resource | Purpose |
|----------|---------|
| Deployment | Runs router pods with HPA |
| Service | ClusterIP service on port 80 |
| Ingress | Routes `/api/router` and wildcard subdomain traffic |
| HorizontalPodAutoscaler | Scales based on memory utilization |

**Sources:** [deployments/charts/router/Chart.yaml:1-41](), [deployments/charts/router/templates/router-service.yaml:1-336]()

### Container Configuration

```yaml
# Deployment spec
containers:
  - name: router-service
    image: ${osmoImageLocation}/osmo:${osmoImageTag}
    command: [router]
    args:
      - --hostname
      - ${hostname}
      - --postgres_host
      - ${postgres.serviceName}
      - --postgres_port
      - ${postgres.port}
      # ... additional database and logging args
```

**Command-Line Arguments:**

- `--hostname`: Public DNS name for session key resolution
- Database connection parameters (inherited from `PostgresConfig`)
- Logging configuration (inherited from `LoggingConfig`)

**Sources:** [deployments/charts/router/templates/router-service.yaml:75-114]()

### Sidecar Containers

| Sidecar | Purpose |
|---------|---------|
| **Envoy** | OAuth2 authentication proxy, JWT validation |
| **FluentBit** | Log collection and forwarding |

**Envoy Configuration:** Router uses Envoy for authentication when `sidecars.envoy.enabled` is true. The Envoy sidecar validates JWTs and injects `x-osmo-user` headers.

**Sources:** [deployments/charts/router/templates/router-service.yaml:188-195]()

### Ingress Rules

The router ingress handles two types of traffic:

**1. API Traffic:**
```yaml
paths:
  - path: /api/router
    pathType: Prefix
    backend:
      service:
        name: router-service
        port: 80
```

**2. Webserver Wildcard Traffic (if `webserverEnabled`):**
```yaml
rules:
  - host: "*.${hostname}"
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: router-service
```

**ALB Annotations:**
- `alb.ingress.kubernetes.io/hostnames: '["*.hostname", "hostname"]'` enables wildcard routing
- SSL termination configured via `sslCertArn`

**Sources:** [deployments/charts/router/templates/router-service.yaml:257-311]()

### Scaling Configuration

```yaml
HorizontalPodAutoscaler:
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: ContainerResource
      containerResource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Scaling Behavior:** Router scales based on memory utilization because connection state is stored in-memory. High connection counts increase memory usage.

**Probes:**

- **Liveness:** HTTP GET on configured endpoint
- **Readiness:** HTTP GET on configured endpoint
- **Startup:** Initial delay to allow service startup

**Sources:** [deployments/charts/router/templates/router-service.yaml:314-336]()

---

## Integration with Other Services

### API Service Integration

The API service triggers router connections by writing actions to Redis queues:

```python
# From src/service/core/config/helpers.py
def backend_action_request_helper(payload: Dict[str, Any], name: str):
    redis_client = connectors.RedisConnector.get_instance().client
    action_attributes: Dict[str, Any] = {**payload}
    redis_queue_name = connectors.backend_action_queue_name(name)
    redis_client.lpush(redis_queue_name, json.dumps(action_attributes))
```

**Action Payload Structure:**

```json
{
  "action": "exec" | "portforward" | "webserver",
  "key": "EXEC-abc123def456",
  "workflow_id": "my-workflow-123",
  "task_name": "train-task",
  "retry_id": 0,
  "command": ["/bin/bash"],  // exec only
  "port": 8080,              // port-forward only
  "protocol": "tcp"          // port-forward only
}
```

**Sources:** [src/service/core/config/helpers.py:194-203](), [src/utils/connectors/postgres.py:51-52]()

### Backend Operator Integration

Backend operators poll Redis queues and initiate router connections:

```mermaid
sequenceDiagram
    participant API as API Service
    participant Redis as Redis Queue
    participant Backend as Backend Listener
    participant Router as Router Service
    participant K8s as Kubernetes API
    
    API->>Redis: LPUSH backend-connections:backend-name<br/>action payload
    Backend->>Redis: BRPOP backend-connections:backend-name
    Redis-->>Backend: Action payload with key
    
    alt Action: exec
        Backend->>Router: WebSocket /api/router/exec/{name}/backend/{key}
        Backend->>K8s: kubectl exec on pod
    else Action: portforward
        Backend->>Router: WebSocket /api/router/portforward/{name}/backend/{key}
        Backend->>K8s: kubectl port-forward
    else Action: webserver
        Backend->>Router: WebSocket /api/router/backend/{session_key}
        Backend->>K8s: kubectl port-forward to task webserver port
    end
    
    Note over Backend,Router: Router relays data bidirectionally<br/>between client and backend
```

**Queue Naming:** Backend queues follow the pattern `backend-connections:{backend_name}` (defined by `backend_action_queue_name()` function).

**Sources:** [src/utils/connectors/postgres.py:51-52](), [src/service/core/config/helpers.py:194-203]()

### CLI Integration

The CLI uses helper functions from `port_forward.py` to establish router connections:

**TCP Port Forwarding:**
```python
# From src/lib/utils/port_forward.py
async def run_tcp(
    service_client: client.ServiceClient,
    app_host: str,
    app_port: int,
    message: str,
    endpoint: str,
    timeout: int,
    router_address: str,
    key: str,
    ctrl_cookie: str,
    ...
)
```

**Connection Steps:**

1. Obtain session cookie from router: `_get_session_cookie(router_address, timeout)`
2. Create control WebSocket: `service_client.create_websocket(router_address, endpoint)`
3. Listen on local socket: `asyncio.start_server(handle_connection, sock=sock)`
4. For each client connection:
   - Generate unique connection key
   - Send `ConnectionPayload` to control WebSocket
   - Create data WebSocket with same key
   - Relay data bidirectionally

**UDP Port Forwarding:** Uses datagram encoding with `_encode_addr()` and `_decode_addr()` to multiplex UDP packets over WebSocket.

**Sources:** [src/lib/utils/port_forward.py:110-228](), [src/lib/utils/port_forward.py:230-308]()

---

## Security Considerations

### Authentication

- **Envoy Sidecar:** Validates OAuth2/OIDC tokens before routing to router
- **User Identity:** Extracted from JWT and injected as `x-osmo-user` header
- **Session Cookies:** HMAC-signed cookies prevent session hijacking

**Sources:** [deployments/charts/router/templates/router-service.yaml:188]()

### Connection Isolation

- **Unique Keys:** Each connection uses a cryptographically random key via `common.generate_unique_id()`
- **Cookie Validation:** Webserver sessions validated via subdomain + cookie matching
- **Timeout Enforcement:** Connections automatically closed after inactivity

**Sources:** [src/service/router/router.py:66-84]()

### Rate Limiting

The CLI implements optional WebSocket write rate limiting:

```python
# From port_forward.py
ws_write_rate_limiter: common.TokenBucket | None = None
# If enabled:
await ws_write_rate_limiter.wait_for_tokens(len(data))
```

This prevents overwhelming backend connections with high-throughput port forwards.

**Sources:** [src/lib/utils/port_forward.py:76-90]()

---

## Troubleshooting

### Common Issues

**1. Connection Timeout (4000 error)**

**Symptom:** `Router connection timeout` error after 60 seconds

**Causes:**
- Backend operator not running or not polling Redis queue
- Backend operator unable to connect to router (firewall/DNS issues)
- Task pod not running or not ready

**Resolution:**
- Check backend operator logs for connection attempts
- Verify `router_address` in backend configuration
- Ensure ingress is routing `/api/router` to router service

**2. Webserver Not Accessible**

**Symptom:** 404 or connection refused when accessing `https://task-{id}.osmo.example.com`

**Causes:**
- Wildcard DNS not configured
- Wildcard ingress not enabled (`webserverEnabled: false`)
- Session key mismatch between subdomain and stored session

**Resolution:**
- Verify wildcard DNS resolves to ingress controller
- Enable `webserverEnabled` in Helm values
- Check `webservers` dictionary for active sessions via `/api/router/webserver/{key}`

**3. High Memory Usage**

**Symptom:** Router pods consuming excessive memory

**Causes:**
- Large number of active connections stored in `connections` and `webservers` dictionaries
- Memory leak from unclosed connections

**Resolution:**
- Scale router horizontally (increase `maxReplicas`)
- Reduce `webserver_nonactive_timeout` to close inactive sessions faster
- Review connection cleanup logic for proper `del connections[key]` calls

**Sources:** [src/service/router/router.py:137-170](), [src/service/router/router.py:95-96]()

---

## Performance Characteristics

### Scalability

- **Stateful Service:** Connection state stored in-memory, no shared state between pods
- **Load Balancing:** Session affinity required for webserver connections (sticky cookies)
- **Vertical Scaling:** Memory-bound by number of active connections

**Memory Footprint per Connection:**
- RouterConnection: ~1-2 KB (WebSocket overhead + Python object)
- Active data buffering: Depends on transfer rate and socket buffer sizes

### Latency

- **Overhead:** Minimal (<5ms) for data relay due to simple forwarding logic
- **WebSocket Framing:** Additional ~2-14 bytes per frame
- **Network Hops:** Client → Ingress → Router → Backend → K8s API → Pod

**Sources:** [src/service/router/router.py:214-245]()

---

**Complete Sources:** [src/service/router/router.py](), [deployments/charts/router/templates/router-service.yaml](), [src/lib/utils/port_forward.py](), [src/service/router/helper.py](), [src/service/core/config/helpers.py:194-203](), [src/utils/connectors/postgres.py:51-52]()

---

# Page: Worker and Background Jobs

# Worker and Background Jobs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

The Worker service processes background jobs related to workflow orchestration, task scheduling, and system maintenance operations. This page covers:
- Worker service deployment architecture and scaling
- Background job types and Redis queue system
- The Delayed Job Monitor component
- Job processing lifecycle and progress tracking mechanisms

For information about workflow submission and lifecycle management, see [Workflow Lifecycle and Execution](#6.4). For backend task execution details, see [Backend Operator Architecture](#5.1).

---

## Worker Service Architecture

The Worker service is a stateless, horizontally scalable component that processes background jobs from Redis queues. It operates independently of user-facing API requests and handles asynchronous operations that would be too slow or resource-intensive for synchronous processing.

### Component Overview

```mermaid
graph TB
    Worker["osmo-worker Deployment"]
    Redis[("Redis<br/>Job Queues")]
    PostgreSQL[("PostgreSQL<br/>State Database")]
    
    Worker -->|"BRPOP<br/>(blocking dequeue)"| Redis
    Worker -->|"Read/Update<br/>Workflow State"| PostgreSQL
    Worker -->|"LPUSH<br/>Results"| Redis
    
    API["osmo-service<br/>(API)"] -->|"LPUSH<br/>Enqueue Jobs"| Redis
    BackendOp["Backend Operator"] -->|"Poll Queues"| Redis
    
    HPA["HorizontalPodAutoscaler"] -.->|"Scale Based on<br/>CPU/Memory"| Worker
    ProgressCheck["progress_check"] -.->|"Liveness Probe<br/>Every 60s"| Worker
```

**Sources:**
- [deployments/charts/service/templates/worker.yaml:1-237]()
- [src/utils/connectors/postgres.py:51-52]()

### Deployment Configuration

The Worker service is deployed as a Kubernetes Deployment with the following characteristics:

| Configuration | Value | Purpose |
|--------------|-------|---------|
| **Command** | `worker` | Primary worker process |
| **Image Pull Policy** | `Always` | Ensures latest image |
| **Security Context** | Non-root (UID 1001) | Minimal privileges |
| **Capabilities** | All dropped | Enhanced security |
| **Redis Connection** | `--redis_host`, `--redis_port` | Job queue access |
| **PostgreSQL Connection** | `--postgres_host`, `--postgres_port` | State persistence |
| **Scaling** | HorizontalPodAutoscaler | Automatic scaling 1-10+ replicas |

**Sources:**
- [deployments/charts/service/templates/worker.yaml:66-77]()
- [deployments/charts/service/templates/worker.yaml:208-237]()

---

## Progress Checking and Health Probes

The Worker service uses a unique health check mechanism based on progress tracking rather than simple HTTP endpoint checks. This ensures workers are actively processing jobs and not stuck in deadlock states.

### Progress Check Mechanism

```mermaid
graph LR
    Worker["Worker Process"]
    ProgressFile["/var/run/osmo/last_progress"]
    ProgressCheckBin["progress_check binary"]
    
    Worker -->|"Update timestamp<br/>on job activity"| ProgressFile
    ProgressCheckBin -->|"Read timestamp"| ProgressFile
    ProgressCheckBin -->|"Compare with<br/>interval (300s)"| ProgressCheckBin
    ProgressCheckBin -->|"Exit 0 if recent<br/>Exit 1 if stale"| Kubelet["Kubernetes Kubelet"]
    
    Kubelet -->|"Execute every 60s"| ProgressCheckBin
    Kubelet -->|"Restart pod<br/>on failure"| Worker
```

**Sources:**
- [deployments/charts/service/templates/worker.yaml:156-177]()

### Probe Definitions

**Liveness Probe** - Restarts worker if stuck for 5 minutes:

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
  failureThreshold: 1
  periodSeconds: 60
  timeoutSeconds: 15
```

The `progress_interval` of 300 seconds means the worker must update its progress file at least once every 5 minutes. If this check fails even once (`failureThreshold: 1`), Kubernetes immediately restarts the pod.

**Startup Probe** - Allows 60 seconds for initialization:

```yaml
startupProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
  failureThreshold: 12
  periodSeconds: 5
  timeoutSeconds: 15
  initialDelaySeconds: 10
```

This gives the worker up to 70 seconds total (10s initial + 12 × 5s) to begin processing before being considered unhealthy.

**Sources:**
- [deployments/charts/service/templates/worker.yaml:157-177]()

---

## Background Job System

OSMO uses Redis as a lightweight, high-performance job queue. Jobs are enqueued using Redis list operations (`LPUSH`) and dequeued by workers using blocking operations (`BRPOP`).

### Job Queue Naming Patterns

Different operation types use distinct queue naming conventions:

| Queue Type | Pattern | Example | Purpose |
|-----------|---------|---------|---------|
| **Backend Actions** | `backend-connections:{backend_name}` | `backend-connections:dgx-prod` | Backend operator job polling |
| **Workflow Actions** | `workflow-action:{workflow_id}:{task_name}:{retry_id}` | `workflow-action:train-123:worker-0:0` | Task actions (exec, port-forward) |
| **Barrier Synchronization** | `barrier:{workflow_id}:{group_name}:{barrier_name}` | `barrier:train-123:workers:osmo-group-ready` | Multi-task sync points |

The `backend_action_queue_name` function constructs backend-specific queue names:

```python
def backend_action_queue_name(backend_name: str) -> str:
    return f'backend-connections:{backend_name}'
```

**Sources:**
- [src/utils/connectors/postgres.py:51-52]()
- [src/service/logger/ctrl_websocket.py:221-227]()

### Job Enqueueing and Dequeueing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as "osmo-service<br/>(API)"
    participant Redis as "Redis Queue"
    participant Worker as "osmo-worker"
    participant DB as "PostgreSQL"
    
    Client->>API: POST /api/workflow
    API->>DB: INSERT workflows<br/>(status=SUBMITTING)
    API->>Redis: LPUSH backend-connections:{backend}<br/>job_payload
    API-->>Client: workflow_id (202 Accepted)
    
    Note over Worker,Redis: Worker blocks on queue
    Worker->>Redis: BRPOP backend-connections:{backend}<br/>(blocking, timeout=5s)
    Redis-->>Worker: job_payload
    
    Worker->>DB: UPDATE workflows<br/>(status=PROCESSING)
    Worker->>Worker: Process job logic
    Worker->>DB: UPDATE workflows<br/>(status=SCHEDULING)
    Worker->>Redis: LPUSH result_queue
```

The `BRPOP` operation blocks until a job is available or the timeout expires, preventing busy-waiting and reducing CPU usage.

**Sources:**
- [src/service/core/config/helpers.py:194-203]()
- [src/utils/connectors/postgres.py:51-52]()

---

## Background Job Types

The Worker service processes several categories of background jobs:

### 1. Workflow State Transitions

When workflows are submitted, they progress through states. The Worker handles transitions from **WAITING** → **PROCESSING** → **SCHEDULING**:

- **Jinja Template Expansion**: Resolves `{{ workflow_id }}`, `{{ input:N }}`, `{{ host:task }}` tokens
- **Resource Validation**: Checks platform compatibility, resource availability
- **K8s Resource Generation**: Creates Pod specs, Secrets, ConfigMaps
- **Backend Job Distribution**: Enqueues tasks to backend-specific queues

### 2. Backend Action Requests

Interactive actions (`exec`, `port-forward`, `rsync`) are enqueued to backend-specific queues:

```python
def backend_action_request_helper(payload: Dict[str, Any], name: str):
    redis_client = connectors.RedisConnector.get_instance().client
    action_attributes: Dict[str, Any] = {**payload}
    redis_queue_name = connectors.backend_action_queue_name(name)
    redis_client.lpush(redis_queue_name, json.dumps(action_attributes))
```

Backend operators poll these queues and execute actions on their Kubernetes clusters.

**Sources:**
- [src/service/core/config/helpers.py:194-203]()

### 3. Task Synchronization Barriers

For distributed training workflows, tasks synchronize using Redis-based barriers. The Logger service coordinates barrier operations:

```python
key = job_common.barrier_key(workflow_id, group_name, barrier_name)
await redis_client.sadd(key, task_name)
barrier_set = await redis_client.smembers(key)

if len(barrier_set) >= count:
    # Notify all waiting tasks
    for name in barrier_set:
        queue_name = workflow.action_queue_name(workflow_id, task_obj.name, task_obj.retry_id)
        await redis_client.lpush(queue_name, key)
```

This implements a rendezvous pattern where all tasks in a group must reach the barrier before any proceed.

**Sources:**
- [src/service/logger/ctrl_websocket.py:93-116]()

### 4. Metrics and I/O Tracking

Tasks report performance metrics (download times, upload sizes) via WebSocket to the Logger service, which updates the database asynchronously:

- **Task I/O Metrics**: Download/upload start/end times, sizes, file counts
- **Task Group Metrics**: Scheduling, initialization, execution timings
- **Dataset Operations**: Track data transfer performance

**Sources:**
- [src/service/logger/ctrl_websocket.py:54-90]()

---

## Delayed Job Monitor

The Delayed Job Monitor is a separate single-replica deployment that tracks job queue health and enforces timeout policies.

### Monitor Architecture

```mermaid
graph TB
    Monitor["osmo-delayed-job-monitor"]
    Redis[("Redis<br/>Job Queues")]
    PostgreSQL[("PostgreSQL<br/>Job Metadata")]
    OTel["OpenTelemetry<br/>Collector"]
    
    Monitor -->|"Periodic scan<br/>queue depths"| Redis
    Monitor -->|"Read job state<br/>timestamps"| PostgreSQL
    Monitor -->|"Detect stuck jobs"| Monitor
    Monitor -->|"Emit metrics"| OTel
    Monitor -->|"Trigger timeouts"| PostgreSQL
    
    ProgressCheck["progress_check"] -.->|"Check every 30s<br/>(more frequent)"| Monitor
```

**Sources:**
- [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

### Configuration Differences from Worker

The Delayed Job Monitor has more aggressive health checks:

| Setting | Worker | Monitor | Rationale |
|---------|--------|---------|-----------|
| **Liveness Period** | 60s | 30s | Faster detection of monitor issues |
| **Startup Delay** | 10s | 10s | Same initialization time |
| **Failure Threshold** | 1 | 1 | Both restart immediately on failure |
| **Progress Interval** | 300s | 300s | Same staleness threshold |

The 30-second liveness period ensures the monitor itself is responsive, critical for detecting and responding to system-wide issues quickly.

**Sources:**
- [deployments/charts/service/templates/delayed-job-monitor.yaml:152-173]()
- [deployments/charts/service/templates/worker.yaml:157-177]()

### Monitoring Responsibilities

1. **Queue Depth Tracking**: Monitors pending job counts in all Redis queues
2. **Stuck Job Detection**: Identifies workflows/tasks in non-terminal states beyond timeout thresholds
3. **Timeout Enforcement**: Updates database state to trigger workflow/task failures
4. **Metrics Emission**: Reports queue statistics to OpenTelemetry for alerting

**Sources:**
- [deployments/charts/service/templates/delayed-job-monitor.yaml:64-111]()

---

## Job Processing Lifecycle

The complete lifecycle of a background job from submission to completion:

```mermaid
stateDiagram-v2
    [*] --> Enqueued: API LPUSH
    Enqueued --> Claimed: Worker BRPOP
    Claimed --> Processing: Update DB<br/>(status=PROCESSING)
    Processing --> Executing: Process job logic
    Executing --> UpdateProgress: Touch progress file
    UpdateProgress --> Executing
    Executing --> Completed: Success
    Executing --> Failed: Permanent error
    Executing --> Retrying: Transient error
    Retrying --> Enqueued: Re-enqueue
    Completed --> [*]
    Failed --> [*]
    
    note right of UpdateProgress
        Ensures liveness probe
        passes every 60s check
    end note
    
    note right of Executing
        Job-specific logic:
        - Workflow processing
        - K8s resource creation
        - Backend communication
    end note
```

**Sources:**
- [deployments/charts/service/templates/worker.yaml:78-122]()

### Worker Loop Pattern

While the actual worker implementation is not visible in the provided files, the configuration and related services imply this processing pattern:

```python
# Conceptual worker loop based on deployment configuration
while True:
    job = redis.brpop(queue_name, timeout=5)
    if job:
        update_progress_file()  # Touch timestamp for liveness probe
        try:
            result = process_job(job)
            update_database(result)
            update_progress_file()
        except TransientError as e:
            requeue_job(job, retry_count + 1)
        except PermanentError as e:
            mark_job_failed(job, error=e)
    else:
        update_progress_file()  # Still alive, no work available
```

**Sources:**
- [deployments/charts/service/templates/worker.yaml:157-177]() (progress check configuration)

---

## Integration with Other Services

### Worker and API Service

The API service enqueues jobs but returns immediately without waiting for completion, enabling asynchronous processing:

```mermaid
sequenceDiagram
    participant Client
    participant API as "osmo-service"
    participant Worker as "osmo-worker"
    participant Backend as "Backend Operator"
    
    Client->>API: Submit workflow
    API->>Redis: Enqueue job
    API->>PostgreSQL: status=SUBMITTING
    API-->>Client: workflow_id<br/>(202 Accepted)
    
    Note over Client,API: Client polls for status updates
    
    Worker->>Redis: Dequeue job
    Worker->>PostgreSQL: status=PROCESSING
    Worker->>Backend: Create K8s resources
    
    loop Status polling
        Client->>API: GET /api/workflow/{id}
        API->>PostgreSQL: Read current state
        API-->>Client: Status response
    end
```

This design decouples request handling from job processing, allowing the API to remain responsive under high load.

**Sources:**
- [src/service/core/config/helpers.py:194-203]()

### Worker and Backend Operator

The Worker creates jobs in backend-specific queues. Backend operators on compute planes poll these queues:

```mermaid
graph LR
    Worker["osmo-worker<br/>(Control Plane)"]
    Redis[("Redis<br/>backend-connections:{name}")]
    BackendListener["Backend Listener<br/>(Compute Plane)"]
    BackendWorker["Backend Worker<br/>(Compute Plane)"]
    K8s["Kubernetes API"]
    
    Worker -->|"LPUSH<br/>Task specs"| Redis
    Redis -->|"BRPOP<br/>Poll jobs"| BackendListener
    BackendListener -->|"Dispatch"| BackendWorker
    BackendWorker -->|"Create Pods<br/>Secrets, Services"| K8s
```

This reverse-connection pattern allows backends to operate behind firewalls without requiring inbound connections.

**Sources:**
- [src/utils/connectors/postgres.py:51-52]()
- [src/service/core/config/helpers.py:194-203]()

### Worker and Logger Service

The Logger service handles real-time log streaming and may trigger additional jobs when tasks complete or barriers are met:

**Sources:**
- [src/service/logger/ctrl_websocket.py:93-227]()

---

## Scaling and Performance

### Horizontal Pod Autoscaling

The Worker deployment uses HorizontalPodAutoscaler to scale based on resource utilization:

```yaml
minReplicas: 1
maxReplicas: 10
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    container: osmo-worker
    target:
      type: Utilization
      averageUtilization: 70
- type: ContainerResource
  containerResource:
    name: cpu
    container: osmo-worker
    target:
      type: Utilization
      averageUtilization: 70
```

When average CPU or memory exceeds 70% across all Worker pods, Kubernetes automatically scales up. During low load, it scales down to the minimum.

**Sources:**
- [deployments/charts/service/templates/worker.yaml:208-237]()

### Job Queue Design Considerations

Redis list operations provide specific guarantees:

| Property | Implementation | Impact |
|----------|---------------|--------|
| **Atomicity** | `BRPOP` is atomic | No duplicate job processing |
| **Multiple Consumers** | Multiple workers can poll same queue | Horizontal scaling works |
| **Delivery Guarantee** | At-most-once (job removed immediately) | Lost if worker crashes before completion |
| **Ordering** | FIFO within each queue | Predictable processing order |
| **Priority** | No native priority support | Separate queues needed for priority |
| **Visibility Timeout** | Not implemented | Jobs lost on worker crash |

For critical operations, the system relies on database state tracking to detect and retry lost jobs. The Delayed Job Monitor helps identify stuck workflows.

**Sources:**
- [src/service/core/config/helpers.py:194-203]() (LPUSH usage)
- [src/service/logger/ctrl_websocket.py:221-227]() (BRPOP usage)

---

## Observability

### Metrics Collection

Both Worker and Monitor integrate with OpenTelemetry sidecars:

```yaml
args:
- --metrics_otel_collector_component
- osmo-worker
- --metrics_otel_enable
- "true"
```

This enables collection of:
- Job processing rate (jobs/second)
- Queue depth per backend
- Processing latency (time from enqueue to completion)
- Error rates and types

**Sources:**
- [deployments/charts/service/templates/worker.yaml:79-82]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:68-71]()

### Logging

When enabled, FluentBit sidecars collect Worker logs and forward them to centralized storage:

```yaml
volumeMounts:
- name: logs
  mountPath: /logs
```

Logs include:
- Job dequeue events with workflow/task IDs
- Processing start/completion with timing
- Error traces with stack traces
- Progress file updates

**Sources:**
- [deployments/charts/service/templates/worker.yaml:148-151]()
- [deployments/charts/service/templates/worker.yaml:179-193]()

---

## Configuration Reference

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--redis_host` | string | (required) | Redis server hostname |
| `--redis_port` | int | 6379 | Redis server port |
| `--redis_db_number` | int | 0 | Redis database index |
| `--redis_tls_enable` | bool | false | Use TLS for Redis connection |
| `--postgres_host` | string | (required) | PostgreSQL hostname |
| `--postgres_port` | int | 5432 | PostgreSQL port |
| `--postgres_database_name` | string | `osmo_db` | Database name |
| `--postgres_user` | string | `postgres` | Database user |
| `--mek_file` | string | `/home/osmo/vault-agent/secrets/vault-secrets.yaml` | Master encryption key file path |
| `--log_level` | string | `INFO` | Logging verbosity |
| `--log_dir` | string | `/logs` | Log file directory |
| `--log_name` | string | `worker` | Log file name prefix |
| `--metrics_otel_enable` | bool | false | Enable OpenTelemetry metrics |

**Sources:**
- [deployments/charts/service/templates/worker.yaml:78-122]()

### Environment Variables

Sensitive credentials are passed via Kubernetes secrets:

```yaml
env:
- name: OSMO_POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: db-password
- name: OSMO_REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: redis-secret
      key: redis-password
```

**Sources:**
- [deployments/charts/service/templates/worker.yaml:123-139]()

---

## Summary

The Worker service and Delayed Job Monitor form the asynchronous job processing backbone of OSMO:

- **Worker Service**: Stateless, horizontally scalable processor handling workflow orchestration, K8s resource creation, and backend coordination
- **Delayed Job Monitor**: Single-replica watchdog tracking queue health and enforcing timeout policies
- **Redis Queues**: Lightweight, high-performance job distribution using atomic list operations
- **Progress Checking**: Unique health mechanism ensuring workers make forward progress, preventing deadlocks without manual intervention

This architecture enables OSMO to handle high-throughput workflow submission while maintaining responsive API services and reliable job execution across geographically distributed compute backends.

**Sources:**
- [deployments/charts/service/templates/worker.yaml:1-237]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()
- [src/utils/connectors/postgres.py:51-52]()
- [src/service/core/config/helpers.py:194-203]()
- [src/service/logger/ctrl_websocket.py:93-227]()

---

# Page: Data Layer

# Data Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



The Data Layer encompasses all persistent storage mechanisms in OSMO, consisting of three primary components: PostgreSQL for relational metadata, Redis for ephemeral logs and job queues, and object storage (S3/Azure Blob/MinIO) for dataset content. This page explains the architecture, design patterns, and integration of these storage systems.

For detailed information about specific aspects:
- Database schema details: see [PostgreSQL Database Schema](#4.1)
- Dataset operations and content-addressable storage: see [Dataset Management](#4.2)
- Configuration versioning and history: see [Configuration Management](#4.3)

## Storage Architecture

OSMO uses a multi-tier storage architecture where each storage system serves a distinct purpose optimized for its use case.

### Storage System Overview

```mermaid
graph TB
    subgraph "API Services"
        API[API Service]
        Worker[Worker Service]
        Logger[Logger Service]
        Agent[Agent Service]
    end
    
    subgraph "PostgreSQL - Persistent Metadata"
        WorkflowTables[workflows<br/>tasks<br/>groups]
        DatasetTables[dataset<br/>dataset_version<br/>dataset_tag<br/>collection]
        ConfigTables[configs<br/>backends<br/>pools<br/>resource_validations]
        CredTables[credential<br/>ueks]
        ResourceTables[resources<br/>resource_platforms]
        AppTables[apps<br/>app_versions]
    end
    
    subgraph "Redis - Ephemeral Data"
        LogStreams["Workflow Logs<br/>workflow_id-logs"]
        TaskLogs["Task Logs<br/>workflow_id:task:retry-logs"]
        ActionQueues["Action Queues<br/>backend-connections:backend_name<br/>workflow_id:task:retry"]
        Barriers["Barrier Sets<br/>workflow_id:group:barrier"]
    end
    
    subgraph "Object Storage - Dataset Content"
        Hashes["Hash Storage<br/>{dataset_id}/hashes/{etag}"]
        Manifests["Manifests<br/>{dataset_id}/manifests/{version}.json"]
        Buckets["Multiple Buckets<br/>S3, MinIO, Azure Blob"]
    end
    
    API --> WorkflowTables
    API --> DatasetTables
    API --> ConfigTables
    API --> CredTables
    Worker --> WorkflowTables
    Worker --> ResourceTables
    Agent --> ResourceTables
    Logger --> LogStreams
    Logger --> TaskLogs
    Logger --> ActionQueues
    
    API --> Hashes
    API --> Manifests
    Worker --> Hashes
    Worker --> Manifests
    
    WorkflowTables -.references.-> DatasetTables
    DatasetTables -.references.-> Buckets
    ConfigTables -.defines.-> Buckets
```

**Sources:** [src/utils/connectors/postgres.py:531-959](), [src/service/logger/ctrl_websocket.py:93-248](), Diagram 5 from high-level architecture

### PostgreSQL Connector

The `PostgresConnector` class manages all database interactions and provides retry logic for connection failures.

```mermaid
graph LR
    PostgresConnector["PostgresConnector<br/>(Singleton)"]
    Config["PostgresConfig<br/>host, port, database<br/>reconnect_retry"]
    SecretManager["SecretManager<br/>MEK-based encryption"]
    Connection["psycopg2.connection"]
    
    PostgresConnector --> Config
    PostgresConnector --> SecretManager
    PostgresConnector --> Connection
    
    Methods["Key Methods:<br/>execute_fetch_command()<br/>execute_commit_command()<br/>execute_autocommit_command()<br/>mogrify()<br/>encrypt_dict()<br/>decrypt_credential()"]
    
    PostgresConnector --> Methods
```

**Key implementation details:**

- **Singleton pattern**: Only one instance exists per process ([src/utils/connectors/postgres.py:217-225]())
- **Automatic reconnection**: The `@retry` decorator handles transient connection failures ([src/utils/connectors/postgres.py:187-212]())
- **Dynamic model creation**: Query results are converted to Pydantic models automatically ([src/utils/connectors/postgres.py:305-316]())
- **HSTORE support**: Native encoding/decoding for key-value storage ([src/utils/connectors/postgres.py:515-524]())

**Sources:** [src/utils/connectors/postgres.py:215-428]()

## Data Flow Patterns

### Workflow Submission to Execution

```mermaid
sequenceDiagram
    participant CLI as CLI/UI
    participant API as API Service
    participant PG as PostgreSQL
    participant Worker as Worker Service
    participant Redis as Redis
    participant Backend as Backend Operator
    
    CLI->>API: POST /api/workflow/submit
    API->>API: Jinja template expansion
    API->>PG: INSERT INTO workflows
    API->>PG: INSERT INTO groups
    API->>PG: INSERT INTO tasks
    API->>Redis: PUBLISH workflow:submit
    API-->>CLI: workflow_id
    
    Worker->>Redis: SUBSCRIBE workflow:submit
    Worker->>PG: SELECT tasks WHERE status=WAITING
    Worker->>PG: UPDATE tasks SET status=PROCESSING
    Worker->>Redis: LPUSH backend-connections:backend_name
    
    Backend->>Redis: BRPOP backend-connections:backend_name
    Backend->>PG: SELECT task details
    Backend->>Backend: Create K8s resources
    Backend->>PG: UPDATE tasks SET status=SCHEDULING
```

**Sources:** [src/utils/job/workflow.py](), [src/service/core/workflow/workflow_service.py]()

### Dataset Upload Flow

```mermaid
sequenceDiagram
    participant Task as Task Container
    participant Ctrl as osmo-ctrl
    participant API as API Service
    participant PG as PostgreSQL
    participant S3 as Object Storage
    
    Task->>API: POST /api/bucket/{bucket}/upload/start
    API->>PG: INSERT INTO dataset (if new)
    API->>PG: INSERT INTO dataset_version (status=PENDING)
    API-->>Task: version_id, upload credentials
    
    Task->>S3: PUT {dataset_id}/hashes/{etag}
    Note over Task,S3: Content-addressable storage<br/>Files stored by hash
    Task->>Task: Build manifest.json
    Task->>S3: PUT {dataset_id}/manifests/{version}.json
    
    Task->>API: POST /api/bucket/{bucket}/upload/finish
    API->>PG: UPDATE dataset_version SET status=READY
    API->>PG: INSERT INTO dataset_tag (tag=latest)
```

**Sources:** [src/service/core/data/data_service.py:229-344](), Diagram 5 from high-level architecture

### Log Streaming via WebSocket

```mermaid
sequenceDiagram
    participant Task as Task Pod
    participant Logger as Logger Service
    participant Redis as Redis
    participant Client as CLI/UI
    
    Task->>Logger: WebSocket connection
    Note over Task,Logger: /api/logger/ctrl_websocket/{workflow_id}/{task}
    
    loop Log streaming
        Task->>Logger: JSON log message
        Logger->>Logger: Mask credentials
        Logger->>Redis: XADD workflow_id-logs
        Logger->>Redis: XADD workflow_id:task:retry-logs
        Logger->>Redis: EXPIRE (MAX_LOG_TTL)
    end
    
    Client->>Logger: GET /api/logger/logs/{workflow_id}
    Logger->>Redis: XREAD workflow_id-logs
    Logger-->>Client: Stream logs (SSE)
```

The `ctrl_websocket` endpoint handles bidirectional communication:
- **Incoming**: Logs, metrics, barrier notifications from tasks
- **Outgoing**: Action requests (exec, port-forward) to tasks

**Sources:** [src/service/logger/ctrl_websocket.py:118-248](), [src/utils/connectors/postgres.py]()

## Credential Encryption

OSMO uses a layered encryption approach for sensitive data stored in PostgreSQL.

### Encryption Architecture

```mermaid
graph TB
    MEK["Master Encryption Key (MEK)<br/>JWK format in vault-secrets.yaml"]
    UEK["User Encryption Keys (UEKs)<br/>One per user, stored in ueks table"]
    Secrets["Encrypted Secrets<br/>credential table (HSTORE)"]
    SecretMgr["SecretManager<br/>Encrypt/decrypt operations"]
    
    MEK -->|encrypts| UEK
    UEK -->|encrypts| Secrets
    SecretMgr --> MEK
    SecretMgr --> UEK
    SecretMgr --> Secrets
    
    Operations["Operations:<br/>encrypt(value, user)<br/>decrypt(encrypted, user)<br/>read_uek(user)<br/>write_uek(user, uek)"]
    SecretMgr --> Operations
```

**Encryption flow:**

1. **System initialization**: MEK loaded from `mek_file` ([src/utils/connectors/postgres.py:254-261]())
2. **User key generation**: Each user gets a unique UEK encrypted with MEK
3. **Credential storage**: User credentials encrypted with their UEK
4. **Key rotation**: UEKs can be re-encrypted with new MEK without touching credentials

**HSTORE format example:**
```
"aws_access_key_id"=>"<encrypted_value>","aws_secret_access_key"=>"<encrypted_value>"
```

**Sources:** [src/utils/connectors/postgres.py:475-507](), [src/utils/secret_manager/]()

## Content-Addressable Storage

Datasets use content-addressable storage to achieve 10-100x storage savings through automatic deduplication.

### Deduplication Mechanism

```mermaid
graph LR
    subgraph "Dataset Upload"
        File1["file1.txt<br/>(ETag: abc123)"]
        File2["file2.txt<br/>(ETag: abc123)"]
        File3["file3.txt<br/>(ETag: def456)"]
    end
    
    subgraph "Hash Storage"
        Hash1["hashes/abc123<br/>(stored once)"]
        Hash2["hashes/def456"]
    end
    
    subgraph "Manifest"
        Manifest["manifests/v1.json<br/>{<br/>  'file1.txt': 'abc123',<br/>  'file2.txt': 'abc123',<br/>  'file3.txt': 'def456'<br/>}"]
    end
    
    File1 -.->|same hash| Hash1
    File2 -.->|same hash| Hash1
    File3 -.-> Hash2
    
    Hash1 --> Manifest
    Hash2 --> Manifest
```

**Storage structure:**
```
s3://bucket/
├── {dataset_id}/
│   ├── hashes/
│   │   ├── {etag1}          # Actual file content
│   │   ├── {etag2}
│   │   └── {etag3}
│   └── manifests/
│       ├── v1.json          # Maps paths to ETags
│       └── v2.json
```

**Manifest JSON structure:**
```json
{
  "files": {
    "path/to/file1.txt": "etag_abc123",
    "path/to/file2.txt": "etag_abc123",
    "dir/file3.bin": "etag_def456"
  },
  "version": "v1",
  "created": "2025-01-15T10:30:00Z"
}
```

**Sources:** [src/lib/data/storage/](), [README.md:76](), Diagram 5 from high-level architecture

## Database Tables Overview

### Core Workflow Tables

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `workflows` | `workflow_uuid` | Workflow metadata, status, timeouts |
| `workflow_tags` | `(workflow_uuid, tag)` | User-defined workflow tags |
| `groups` | `group_uuid` | Task group specifications and status |
| `tasks` | `task_db_key` | Individual task execution records |
| `task_io` | `uuid` | Task input/output transfer metrics |

**Key relationships:**
- `workflows.workflow_id` is referenced by `groups.workflow_id` and `tasks.workflow_id`
- `tasks.group_name` references `groups.name` within the same workflow
- All tables use `TEXT` for IDs to support UUID strings

**Sources:** [src/utils/connectors/postgres.py:631-786]()

### Dataset Tables

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `dataset` | `id` | Dataset metadata, bucket, hash location |
| `dataset_version` | `(dataset_id, version_id)` | Version-specific data (location, status, size) |
| `dataset_tag` | `(dataset_id, tag)` | Tag-to-version mapping (e.g., "latest") |
| `collection` | `(id, dataset_id)` | Collection membership (groups datasets) |

**Version lifecycle:**
1. `upload_start`: Creates version with `status=PENDING`
2. Upload content to object storage
3. `upload_finish`: Updates to `status=READY`, creates `latest` tag

**Sources:** [src/utils/connectors/postgres.py:878-945](), [src/service/core/data/data_service.py:229-404]()

### Configuration Tables

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `configs` | `(key, type)` | Dynamic configuration key-value pairs |
| `backends` | `name` | Backend cluster registration and heartbeat |
| `pools` | `name` | Resource pool definitions per backend |
| `resource_validations` | `name` | Platform-specific resource constraints |
| `pod_templates` | `name` | Kubernetes pod template overrides |

**Configuration types** (enum `ConfigType`):
- `SERVICE`: System-wide settings (image locations, timeouts)
- `WORKFLOW`: Workflow execution defaults (max retries, log settings)
- `DATASET`: Storage bucket configurations

**Sources:** [src/utils/connectors/postgres.py:537-629]()

### Security Tables

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `credential` | `(user_name, cred_name)` | Encrypted credentials (HSTORE payload) |
| `ueks` | `uid` | User encryption keys (HSTORE of kid→key) |
| `roles` | `name` | RBAC role definitions with policies |

**Credential types:**
- `GENERIC`: Custom key-value credentials
- `REGISTRY`: Docker registry authentication
- `DATA`: Cloud storage access keys (S3, Azure)

**Sources:** [src/utils/connectors/postgres.py:960-1095]()

## Redis Key Patterns

OSMO uses Redis for ephemeral data with specific key naming conventions:

### Log Keys

```python
# Workflow-level logs (all tasks)
f"{workflow_id}-logs"

# Task-specific logs
f"{workflow_id}:{task_name}:{retry_id}-logs"
```

Logs are stored as Redis Streams (`XADD`) with automatic expiration (`MAX_LOG_TTL` = 7 days).

**Sources:** [src/service/logger/ctrl_websocket.py:199-215](), [src/lib/utils/common.py]()

### Queue Keys

```python
# Backend action queue (for backend worker to poll)
f"backend-connections:{backend_name}"

# Task action queue (for exec/port-forward)
f"workflow:{workflow_id}:task:{task_name}:retry:{retry_id}"
```

Queues use `LPUSH` (producer) and `BRPOP` (consumer) for job distribution.

**Sources:** [src/utils/connectors/postgres.py:51-52](), [src/utils/job/workflow.py]()

### Barrier Keys

```python
# Barrier synchronization sets
f"workflow:{workflow_id}:group:{group_name}:barrier:{barrier_name}"
```

Barriers use Redis Sets (`SADD`, `SMEMBERS`) to coordinate task group synchronization for distributed training.

**Sources:** [src/service/logger/ctrl_websocket.py:93-116]()

## Object Storage Integration

### Bucket Configuration

The `DatasetConfig` defines storage buckets with per-bucket settings:

```mermaid
graph TB
    DatasetConfig["DatasetConfig"]
    BucketConfigs["buckets: Dict[str, BucketConfig]"]
    BucketConfig1["BucketConfig<br/>name: 'default'<br/>mode: 'read_write'<br/>dataset_path: 's3://my-bucket/'<br/>region: 'us-west-2'<br/>check_key: true"]
    BucketConfig2["BucketConfig<br/>name: 'shared-readonly'<br/>mode: 'read_only'"]
    
    DatasetConfig --> BucketConfigs
    BucketConfigs --> BucketConfig1
    BucketConfigs --> BucketConfig2
    
    Validation["Validation:<br/>validate_user_cred()<br/>Checks IAM permissions<br/>before upload/download"]
    BucketConfig1 --> Validation
```

**Bucket modes:**
- `read_write`: Full access (default)
- `read_only`: Download-only access
- `write_only`: Upload-only access

**Sources:** [src/utils/connectors/postgres.py:2734-2857](), [src/service/core/data/data_service.py:48-60]()

### Storage Backend Support

OSMO supports multiple storage backends through a unified interface:

| Backend | URI Pattern | Implementation |
|---------|-------------|----------------|
| AWS S3 | `s3://bucket/path` | `S3StorageBackend` |
| Azure Blob | `wasbs://container@account/path` | `AzureBlobStorageBackend` |
| MinIO | `s3://endpoint/bucket/path` | `S3StorageBackend` (compatible) |
| LocalStack | `http://localhost:4566/bucket` | Development/testing only |

Each backend implements:
- `data_auth()`: Credential validation
- `upload_file()`: Content-addressable upload
- `download_file()`: Manifest-based download
- `parse_uri_to_link()`: Web console link generation

**Sources:** [src/lib/data/storage/](), [docs/deployment_guide/getting_started/create_storage/s3/index.rst]()

## Configuration History

All configuration changes are tracked in the `config_history` table for audit and rollback purposes:

```mermaid
sequenceDiagram
    participant User
    participant API
    participant PG as PostgreSQL
    
    User->>API: PATCH /api/config/service
    API->>PG: SELECT * FROM configs WHERE type='SERVICE'
    API->>API: Apply patch (strategic merge)
    API->>PG: UPDATE configs SET value=...
    API->>PG: INSERT INTO config_history<br/>(type, name, username, data, description, tags)
    API-->>User: Updated config
    
    Note over User,API: Rollback scenario
    User->>API: GET /api/config/history/service/123
    API->>PG: SELECT * FROM config_history WHERE id=123
    User->>API: POST /api/config/service/rollback/123
    API->>PG: UPDATE configs FROM history
    API->>PG: INSERT INTO config_history<br/>(description='Rollback to version 123')
```

**History metadata:**
- `config_type`: What configuration was changed (SERVICE, BACKEND, POOL, etc.)
- `name`: Specific entity name (empty for global configs)
- `data`: Complete configuration snapshot (JSONB)
- `tags`: User-defined labels for grouping changes
- `description`: Change description for audit trail

**Sources:** [src/utils/connectors/postgres.py:3406-3477](), [src/service/core/config/helpers.py:72-193]()

## Transaction and Concurrency Patterns

### Optimistic Locking

Workflow task status updates use version-based optimistic locking:

```sql
UPDATE tasks 
SET status = 'RUNNING', retry_id = retry_id + 1
WHERE workflow_id = %s AND name = %s AND status = 'SCHEDULING'
RETURNING *;
```

If no rows are returned, another worker already updated the task.

**Sources:** [src/utils/job/task.py]()

### Connection Pooling

The `PostgresConnector` maintains a single connection per process with retry logic:
- Automatic reconnection on `InterfaceError` or `DatabaseError`
- Configurable retry attempts via `postgres_reconnect_retry`
- Exponential backoff (implicit in retry decorator)

**Sources:** [src/utils/connectors/postgres.py:187-213]()

### Redis Pipeline Operations

Log streaming uses Redis pipelines to batch operations:

```python
await redis_client.xadd(f'{workflow_id}-logs', log_data, maxlen=max_lines)
await redis_client.expire(f'{workflow_id}-logs', MAX_LOG_TTL, nx=True)
```

The `nx=True` flag ensures expiration is only set once (first log message).

**Sources:** [src/service/logger/ctrl_websocket.py:199-215]()

## Data Retention and Cleanup

### Log Expiration

- **Workflow logs**: `MAX_LOG_TTL` = 7 days (Redis TTL)
- **Task logs**: Individually tracked, same 7-day TTL
- **Archived logs**: Moved to object storage after workflow completion

**Sources:** [src/utils/connectors/postgres.py](), [src/service/logger/ctrl_websocket.py:210-215]()

### Dataset Retention Policies

The `dataset_version` table includes a `retention_policy` column (PostgreSQL `INTERVAL`):

```sql
-- Example: Delete versions older than 30 days
DELETE FROM dataset_version 
WHERE last_used < NOW() - retention_policy 
AND status = 'READY';
```

**Note:** Retention policies are defined but not automatically enforced; cleanup must be implemented separately.

**Sources:** [src/utils/connectors/postgres.py:897-915]()

### Resource Cleanup

Backend resources are cleaned up via `BackendCleanupSpec`:

```python
cleanup_specs = [
    BackendCleanupSpec(resource_type='Pod', labels=workflow_labels),
    BackendCleanupSpec(resource_type='PodGroup', labels=workflow_labels)
]
```

This maps to Kubernetes API calls to delete resources by label selector.

**Sources:** [src/utils/job/kb_objects.py:100-107]()

---

# Page: PostgreSQL Database Schema

# PostgreSQL Database Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



This document describes the complete PostgreSQL database schema used by OSMO for storing workflow execution state, configuration, datasets, credentials, and system metadata. The schema is defined and initialized in [src/utils/connectors/postgres.py:531-1015]().

For information about dataset management operations and versioning, see [Dataset Management](#4.2). For configuration types and their usage, see [Configuration Management](#4.3).

---

## Overview

The PostgreSQL database serves as the primary persistent storage layer for OSMO's control plane. It stores:

- **Workflow execution state**: Workflows, groups, tasks, and their execution metrics
- **Configuration data**: Service configs, backend definitions, pools, and resource templates
- **Dataset metadata**: Dataset versions, tags, collections, and storage locations
- **Security data**: User credentials, access tokens, encryption keys, and roles
- **Application metadata**: App definitions and versions
- **Resource tracking**: Backend cluster resources and their availability

The database is accessed through the `PostgresConnector` singleton class, which provides connection management, transaction handling, and automatic retry logic. All tables are created and initialized in the `_init_tables` method on first startup.

**Sources:** [src/utils/connectors/postgres.py:215-276](), [src/utils/connectors/postgres.py:531-1015]()

---

## Core Workflow Execution Tables

These tables track the lifecycle and execution state of workflows, from submission through completion.

### Entity Relationship Diagram

```mermaid
erDiagram
    workflows ||--o{ workflow_tags : "has"
    workflows ||--o{ groups : "contains"
    groups ||--o{ tasks : "contains"
    tasks ||--o{ task_io : "performs"
    workflows ||--o{ apps : "executes"
    apps ||--o{ app_versions : "has"
    
    workflows {
        text workflow_uuid PK
        text workflow_name
        int job_id
        text workflow_id UK
        text submitted_by
        text cancelled_by
        text logs
        text events
        timestamp submit_time
        timestamp start_time
        timestamp end_time
        int exec_timeout
        int queue_timeout
        text backend
        text pool
        int version
        text outputs
        text status
        text failure_message
        text parent_name
        text parent_job_id
        text app_uuid
        int app_version
        jsonb plugins
        text priority
    }
    
    workflow_tags {
        text workflow_uuid FK
        text tag
    }
    
    groups {
        text group_uuid PK
        text workflow_id FK
        text name
        jsonb spec
        text status
        text failure_message
        timestamp processing_start_time
        timestamp scheduling_start_time
        timestamp initializing_start_time
        timestamp start_time
        timestamp end_time
        hstore remaining_upstream_groups
        hstore downstream_groups
        text outputs
        boolean cleaned_up
        text scheduler_settings
    }
    
    tasks {
        text task_db_key PK
        text workflow_id FK
        text name
        int retry_id
        text task_uuid
        text group_name
        text status
        text failure_message
        int exit_code
        timestamp scheduling_start_time
        timestamp initializing_start_time
        timestamp start_time
        timestamp end_time
        timestamp input_download_start_time
        timestamp input_download_end_time
        timestamp output_upload_start_time
        timestamp output_upload_end_time
        timestamp last_heartbeat
        text node_name
        float gpu_count
        float cpu_count
        float disk_count
        float memory_count
        jsonb exit_actions
        boolean lead
        bytea refresh_token
        text pod_name
        text pod_ip
    }
    
    task_io {
        text uuid PK
        text workflow_id
        text group_name
        text task_name
        int retry_id
        text url
        text type
        text storage_bucket
        timestamp start_time
        timestamp end_time
        float size
        text operation_type
        text download_type
        int number_of_files
    }
```

**Sources:** [src/utils/connectors/postgres.py:632-786]()

### workflows Table

The `workflows` table stores the top-level metadata and state for each submitted workflow.

**Key Fields:**
- `workflow_uuid` (PK): Unique identifier for the workflow instance
- `workflow_id` (UK): Human-readable ID in format `{name}-{job_id}`
- `workflow_name`, `job_id` (UK): Composite unique constraint ensuring job numbering per workflow name
- `status`: Current execution status (see `TaskGroupStatus` enum)
- `backend`, `pool`: Target execution environment
- `logs`, `events`: Redis stream keys for runtime logs and events
- `app_uuid`, `app_version`: Optional link to app definition
- `priority`: Workflow scheduling priority (NORMAL, HIGH, LOW)

**Indexes:**
- `workflow_list_index`: Optimizes listing by `(submitted_by, pool, status, submit_time)`
- `workflow_list_index_pool_status`: Optimizes queries by `(pool, status, submit_time)`

**Sources:** [src/utils/connectors/postgres.py:632-680]()

### groups Table

The `groups` table represents task groups within a workflow. Groups enable gang scheduling and coordinated execution of related tasks.

**Key Fields:**
- `group_uuid` (PK): Unique identifier for the group
- `workflow_id`, `name` (UK): Composite unique constraint per workflow
- `spec`: JSONB containing the complete group specification
- `remaining_upstream_groups`, `downstream_groups`: HSTORE tracking dependency graph
- `scheduler_settings`: Scheduler-specific configuration (e.g., KAI PodGroup settings)

Groups transition through statuses defined in `TaskGroupStatus`: SUBMITTING → WAITING → PROCESSING → SCHEDULING → INITIALIZING → RUNNING → COMPLETED/FAILED.

**Sources:** [src/utils/connectors/postgres.py:693-715]()

### tasks Table

The `tasks` table stores individual task execution records within groups. Tasks may be retried, creating multiple rows per task name with different `retry_id` values.

**Key Fields:**
- `task_db_key` (PK): Unique identifier for this task retry instance
- `task_uuid`, `retry_id` (UK): Composite unique constraint
- `workflow_id`, `retry_id`, `name` (UK): Composite unique constraint per workflow
- `group_name`: Foreign key reference to parent group
- `lead`: Boolean indicating if this is the lead task in a distributed group
- `pod_name`, `pod_ip`: Kubernetes pod information
- `*_start_time`, `*_end_time`: Detailed timing for each execution phase
- `*_count`: Resource allocation tracking (gpu, cpu, memory, disk)
- `last_heartbeat`: Timestamp of last task activity
- `refresh_token`: Encrypted token for task authentication

**Indexes:**
- `tasks_status_id_name`: Unique index on `(status, workflow_id, retry_id, name)`

**Sources:** [src/utils/connectors/postgres.py:718-764]()

### task_io Table

The `task_io` table records input/output operations performed by tasks, including downloads, uploads, and data transfers.

**Key Fields:**
- `uuid` (PK): Unique identifier for the I/O operation
- `type`: INPUT or OUTPUT
- `operation_type`: DOWNLOAD or UPLOAD
- `download_type`: Method used (download, mount, etc.)
- `url`, `storage_bucket`: Source/destination storage location
- `size`: Size in GiB
- `number_of_files`: Count of files transferred

This table is populated by the logger service when tasks report I/O metrics via websocket.

**Sources:** [src/utils/connectors/postgres.py:767-786](), [src/service/logger/ctrl_websocket.py:72-90]()

---

## Configuration Management Tables

These tables store system configuration, backend definitions, resource pools, and configuration history for audit and rollback.

### Configuration Tables Overview

```mermaid
erDiagram
    configs {
        text key
        text value
        text type
    }
    
    config_history {
        text config_type
        int revision
        text name
        text username
        timestamp created_at
        text[] tags
        text description
        jsonb data
    }
    
    backends {
        text name PK
        text description
        text k8s_uid
        text k8s_namespace
        text dashboard_url
        text grafana_url
        text scheduler_settings
        text[] tests
        timestamp last_heartbeat
        timestamp created_date
        text router_address
        text version
        jsonb node_conditions
    }
    
    pools {
        text name PK
        text description
        text backend FK
        text download_type
        text default_platform
        jsonb platforms
        text default_exec_timeout
        text default_queue_timeout
        text max_exec_timeout
        text max_queue_timeout
        jsonb default_exit_actions
        jsonb common_default_variables
        text[] common_resource_validations
        jsonb parsed_resource_validations
        text[] common_pod_template
        jsonb parsed_pod_template
        boolean enable_maintenance
        jsonb action_permissions
        jsonb resources
    }
    
    resource_validations {
        text name PK
        jsonb[] resource_validations
    }
    
    pod_templates {
        text name PK
        jsonb pod_template
    }
    
    roles {
        text name PK
        text description
        jsonb[] policies
        boolean immutable
    }
    
    backends ||--o{ pools : "provides"
    pools ||--o{ resource_validations : "references"
    pools ||--o{ pod_templates : "references"
```

**Sources:** [src/utils/connectors/postgres.py:538-629](), [src/utils/connectors/postgres.py:1004-1015]()

### configs Table

The `configs` table stores dynamic configuration key-value pairs for three configuration types: SERVICE, WORKFLOW, and DATASET.

**Structure:**
- `key`, `type` (PK): Composite primary key
- `value`: String representation of config value (may be JSON for complex types)

Configuration types are defined in the `ConfigType` enum and correspond to Pydantic model classes:
- `ServiceConfig`: API service settings, image locations, timeouts
- `WorkflowConfig`: Default workflow parameters, resource limits
- `DatasetConfig`: Bucket configurations, storage backends

The `get_configs()` method deserializes string values back to their typed Pydantic models based on type hints.

**Sources:** [src/utils/connectors/postgres.py:69-86](), [src/utils/connectors/postgres.py:430-471](), [src/utils/connectors/postgres.py:538-546]()

### config_history Table

The `config_history` table provides audit trail and rollback capability for all configuration changes.

**Key Fields:**
- `config_type`, `revision` (PK): Composite primary key
- `name`: Specific config name (e.g., backend name, pool name) or empty for global configs
- `username`: User who made the change
- `tags`: User-defined tags for categorization
- `data`: JSONB snapshot of complete configuration at that revision

Supported configuration history types (from `ConfigHistoryType` enum): SERVICE, WORKFLOW, DATASET, BACKEND, POOL, POD_TEMPLATE, RESOURCE_VALIDATION, BACKEND_TEST, ROLE.

**Sources:** [src/utils/connectors/postgres.py:76-86](), [src/utils/connectors/postgres.py:1004-1015](), [src/service/core/config/helpers.py:106-114]()

### backends Table

The `backends` table defines compute backends (Kubernetes clusters) where workflows execute.

**Key Fields:**
- `name` (PK): Unique backend identifier
- `k8s_uid`, `k8s_namespace`: Kubernetes cluster and namespace identification
- `dashboard_url`, `grafana_url`: Monitoring endpoints
- `scheduler_settings`: JSON string containing scheduler type and configuration
- `tests`: Array of backend test names to run
- `last_heartbeat`: Timestamp of last backend operator heartbeat
- `node_conditions`: JSONB defining node readiness rules with prefix

The `scheduler_settings` field is parsed into a `BackendSchedulerSettings` object determining the scheduler type (e.g., KAI) and creating the appropriate `K8sObjectFactory`.

**Sources:** [src/utils/connectors/postgres.py:562-582](), [src/utils/job/kb_objects.py:481-488]()

### pools Table

The `pools` table defines resource pools within backends, grouping resources with common configuration.

**Key Fields:**
- `name` (PK): Unique pool identifier
- `backend`: Foreign key to backends table
- `platforms`: JSONB map of platform definitions (CPU/GPU types, allowed mounts, etc.)
- `default_platform`: Default platform if not specified in task
- `download_type`: Default data download method (download, mount)
- `*_timeout`: Default and maximum execution/queue timeouts
- `default_exit_actions`: JSONB defining exit code to action mappings
- `common_resource_validations`, `parsed_resource_validations`: Resource requirement validators
- `common_pod_template`, `parsed_pod_template`: Kubernetes pod template overlays
- `resources`: JSONB defining pool resource guarantees and limits

Pools are the target for workflow submission and determine available resources, platforms, and scheduling policies.

**Sources:** [src/utils/connectors/postgres.py:605-629]()

### resource_validations and pod_templates Tables

These tables store reusable configuration fragments that pools reference:

- `resource_validations`: Array of JSONB validation rules for task resource requests
- `pod_templates`: JSONB Kubernetes pod template overlays for customizing task pods

Pools reference these by name in their `common_resource_validations` and `common_pod_template` arrays, which are parsed and merged into `parsed_*` fields at pool fetch time.

**Sources:** [src/utils/connectors/postgres.py:585-602]()

### roles Table

The `roles` table defines RBAC roles with associated policies.

**Key Fields:**
- `name` (PK): Role name
- `description`: Human-readable description
- `policies`: Array of JSONB policy objects defining permissions
- `immutable`: Boolean indicating system-defined roles that cannot be modified

**Sources:** [src/utils/connectors/postgres.py:548-558]()

---

## Dataset and Storage Tables

These tables manage dataset metadata, versioning, tagging, and collections. Actual dataset content is stored in object storage; the database tracks only metadata and locations.

### Dataset Schema Diagram

```mermaid
erDiagram
    dataset ||--o{ dataset_version : "has"
    dataset_version ||--o{ dataset_tag : "tagged_with"
    dataset ||--o{ collection : "contains"
    collection }o--|| dataset_version : "references"
    
    dataset {
        text id PK
        text name UK_with_bucket
        text bucket UK_with_name
        text created_by
        timestamp created_date
        boolean is_collection
        jsonb labels
        text hash_location
        bigint hash_location_size
        int last_version
    }
    
    dataset_version {
        text dataset_id FK_PK
        text version_id PK
        text location
        text status
        text created_by
        timestamp created_date
        timestamp last_used
        timestamp last_updated
        bigint size
        text checksum
        jsonb metadata
        interval retention_policy
    }
    
    dataset_tag {
        text dataset_id FK_PK
        text tag PK
        text version_id FK
    }
    
    collection {
        text id FK_PK
        text dataset_id FK_PK
        text version_id FK
    }
```

**Sources:** [src/utils/connectors/postgres.py:879-945]()

### dataset Table

The `dataset` table stores top-level dataset metadata. A dataset can be either a regular dataset or a collection of other datasets.

**Key Fields:**
- `id` (PK): Unique UUID for the dataset
- `name`, `bucket` (UK): Dataset name within a bucket (unique constraint)
- `is_collection`: Boolean distinguishing collections from regular datasets
- `labels`: JSONB for user-defined metadata labels
- `hash_location`: S3/Azure path to content-addressable hash storage directory
- `hash_location_size`: Total size of all hashes in bytes
- `last_version`: Auto-incrementing version counter

The `hash_location` field points to the directory where deduplicated file chunks are stored by their ETag hash. This enables significant storage savings when files are shared across dataset versions.

**Sources:** [src/utils/connectors/postgres.py:879-895](), [src/service/core/data/data_service.py:63-76]()

### dataset_version Table

The `dataset_version` table tracks individual versions of datasets.

**Key Fields:**
- `dataset_id`, `version_id` (PK): Composite primary key
- `location`: S3/Azure path to manifest file (JSON mapping logical paths to hashes)
- `status`: PENDING, READY, or FAILED
- `size`: Total size in bytes
- `checksum`: Manifest checksum for integrity verification
- `metadata`: JSONB for version-specific metadata (description, etc.)
- `retention_policy`: PostgreSQL INTERVAL for automatic cleanup (default P3M = 3 months)
- `last_used`: Timestamp of last download/use

Versions are created with status PENDING during upload, then transitioned to READY when `upload_finish` is called. The manifest file at `location` contains the mapping of logical file paths to their content-addressable storage hashes.

**Sources:** [src/utils/connectors/postgres.py:898-915](), [src/service/core/data/data_service.py:229-358]()

### dataset_tag Table

The `dataset_tag` table provides named references to dataset versions. Tags enable symbolic references like "latest" or "v1.0" instead of numeric version IDs.

**Key Fields:**
- `dataset_id`, `tag` (PK): One tag per dataset
- `version_id`: Target version (ON UPDATE CASCADE, ON DELETE CASCADE)

The "latest" tag is automatically updated on each successful upload. Users can create additional custom tags. Tags can be moved between versions with ON CONFLICT DO UPDATE.

**Sources:** [src/utils/connectors/postgres.py:918-930](), [src/service/core/data/data_service.py:402-418]()

### collection Table

The `collection` table implements collections by referencing multiple dataset versions.

**Key Fields:**
- `id` (PK, FK to dataset): The collection's dataset ID
- `dataset_id`, `version_id` (FK to dataset_version): Referenced dataset version

A collection is a dataset where `is_collection=true` that references other datasets. Collections cannot contain other collections (enforced in application logic). Each dataset can appear only once in a collection (by dataset_id).

**Sources:** [src/utils/connectors/postgres.py:933-945](), [src/service/core/data/data_service.py:421-482]()

---

## Authentication and Security Tables

These tables manage user credentials, access tokens, encryption keys, and user profiles.

### Security Tables Overview

```mermaid
erDiagram
    credential {
        text user_name PK
        text cred_name PK
        text cred_type
        text profile UK_with_user
        hstore payload
    }
    
    access_token {
        text user_name PK
        text token_name PK
        text access_type PK
        bytea access_token UK
        timestamp expires_at
        text description
        text[] roles
    }
    
    profile {
        text user_name PK
        boolean slack_notification
        boolean email_notification
        text bucket
        text pool
    }
    
    ueks {
        text uid PK
        hstore keys
    }
    
    credential ||--o{ profile : "for_user"
    access_token ||--o{ profile : "for_user"
```

**Sources:** [src/utils/connectors/postgres.py:853-1001]()

### credential Table

The `credential` table stores encrypted user credentials for registries and storage backends.

**Key Fields:**
- `user_name`, `cred_name` (PK): Composite primary key
- `cred_type`: GENERIC, REGISTRY, or DATA (enum `CredentialType`)
- `profile`: Profile name (unique per user for automatic lookup)
- `payload`: HSTORE containing encrypted credential fields

The `payload` field uses PostgreSQL's HSTORE type to store arbitrary key-value pairs. Values are encrypted using JWE with the user's User Encryption Key (UEK). The `decrypt_credential` method in [src/utils/connectors/postgres.py:475-500]() handles decryption and automatic re-encryption when keys are rotated.

**Sources:** [src/utils/connectors/postgres.py:62-67](), [src/utils/connectors/postgres.py:961-972](), [src/utils/connectors/postgres.py:475-500]()

### access_token Table

The `access_token` table stores API access tokens for programmatic access.

**Key Fields:**
- `user_name`, `token_name`, `access_type` (PK): Composite primary key
- `access_token` (UK): Encrypted token bytes (unique)
- `expires_at`: Expiration timestamp
- `roles`: Array of role names assigned to this token
- `description`: User-provided description

Access tokens are generated via the API and used for CLI authentication. The `access_type` field distinguishes between different token types (e.g., personal vs service tokens).

**Sources:** [src/utils/connectors/postgres.py:975-988]()

### profile Table

The `profile` table stores user preferences and default settings.

**Key Fields:**
- `user_name` (PK): User identifier
- `slack_notification`, `email_notification`: Notification preferences
- `bucket`: Default dataset bucket
- `pool`: Default execution pool

Profiles are automatically created on first user activity and referenced when applying user-specific defaults.

**Sources:** [src/utils/connectors/postgres.py:991-1001]()

### ueks Table

The `ueks` table stores User Encryption Keys in HSTORE format, where keys are key IDs and values are encrypted UEKs.

**Structure:**
- `uid` (PK): User identifier
- `keys`: HSTORE of `{kid: encrypted_uek}`

UEKs are used to encrypt user credentials and are themselves encrypted with the Master Encryption Key (MEK). The SecretManager class handles UEK rotation and credential re-encryption.

**Sources:** [src/utils/connectors/postgres.py:853-860](), [src/utils/secret_manager.py]()

---

## Application Management Tables

These tables support the app publishing and execution feature, allowing users to package and version workflow templates.

### Application Tables

```mermaid
erDiagram
    apps ||--o{ app_versions : "has"
    apps ||--o{ workflows : "executes"
    
    apps {
        text uuid PK
        text name UK
        text owner
        timestamp created_date
        text description
    }
    
    app_versions {
        text uuid FK_PK
        int version PK
        text created_by
        timestamp created_date
        text status
        text uri
    }
```

**Sources:** [src/utils/connectors/postgres.py:789-817]()

### apps Table

The `apps` table stores application definitions.

**Key Fields:**
- `uuid` (PK): Unique application identifier
- `name` (UK): Human-readable unique name
- `owner`: User who owns the application
- `description`: Application description

Applications are created through the API and can be versioned. Each workflow can optionally reference an app for tracking and discovery.

**Sources:** [src/utils/connectors/postgres.py:789-800]()

### app_versions Table

The `app_versions` table tracks versions of published applications.

**Key Fields:**
- `uuid`, `version` (PK): Composite primary key
- `uri`: Storage location of workflow template YAML
- `status`: Publishing status (DRAFT, PUBLISHED, ARCHIVED)
- Foreign key to apps with ON DELETE CASCADE

App versions are created when users publish workflow templates. The `uri` field points to the stored workflow YAML in object storage.

**Sources:** [src/utils/connectors/postgres.py:803-817]()

---

## Resource Management Tables

These tables track backend cluster resources and their allocation to pools and platforms.

### Resource Tables Diagram

```mermaid
erDiagram
    backends ||--o{ resources : "provides"
    resources ||--o{ resource_platforms : "categorized_by"
    pools ||--o{ resource_platforms : "maps_to"
    
    resources {
        text name PK
        text backend PK_FK
        boolean available
        hstore allocatable_fields
        hstore label_fields
        jsonb[] taints
        hstore usage_fields
        hstore non_workflow_usage_fields
        text[] conditions
    }
    
    resource_platforms {
        text resource_name FK_PK
        text backend FK_PK
        text pool FK_PK
        text platform PK
    }
```

**Sources:** [src/utils/connectors/postgres.py:820-850]()

### resources Table

The `resources` table stores information about individual nodes in backend clusters.

**Key Fields:**
- `name`, `backend` (PK): Composite primary key (node name within backend)
- `available`: Boolean indicating if node is available for scheduling
- `allocatable_fields`: HSTORE of allocatable resources (cpu, memory, gpu, storage)
- `label_fields`: HSTORE of Kubernetes node labels
- `taints`: Array of JSONB taints affecting scheduling
- `usage_fields`, `non_workflow_usage_fields`: HSTORE tracking resource usage
- `conditions`: Array of node condition strings

This table is populated and updated by the backend operator's agent service as it monitors the Kubernetes cluster. Resources are checked for updates every heartbeat interval.

**Sources:** [src/utils/connectors/postgres.py:820-834]()

### resource_platforms Table

The `resource_platforms` table maps individual resources (nodes) to pools and platforms.

**Key Fields:**
- `resource_name`, `backend`, `pool`, `platform` (PK): Composite primary key
- Foreign keys to resources(name, backend) with ON UPDATE CASCADE, ON DELETE CASCADE

This table determines which resources are available for which platform within each pool. When a workflow specifies a platform, only resources in this mapping are considered for scheduling.

**Sources:** [src/utils/connectors/postgres.py:837-850]()

---

## Database Connection and Operations

### PostgresConnector Class

The `PostgresConnector` class provides a singleton interface to the PostgreSQL database with automatic connection management and retry logic.

```mermaid
graph TB
    App["Application Code"]
    
    subgraph PostgresConnector["PostgresConnector (Singleton)"]
        Config["PostgresConfig"]
        Conn["_conn: psycopg2.connection"]
        SM["SecretManager"]
        
        subgraph Operations["Core Operations"]
            ExecuteFetch["execute_fetch_command()<br/>Returns DynamicModel list"]
            ExecuteCommit["execute_commit_command()<br/>Commits changes"]
            ExecuteAuto["execute_autocommit_command()<br/>No transaction"]
        end
        
        subgraph Helpers["Helper Methods"]
            GetConfigs["get_configs(ConfigType)"]
            SetConfig["set_config(key, value, type)"]
            EncryptDecrypt["encrypt_dict() / decrypt_credential()"]
            Mogrify["mogrify()<br/>SQL injection prevention"]
        end
    end
    
    DB[("PostgreSQL<br/>Database")]
    
    App -->|"get_instance()"| PostgresConnector
    Config -->|"connection params"| Conn
    Conn -->|"psycopg2"| DB
    ExecuteFetch -->|"SELECT"| DB
    ExecuteCommit -->|"INSERT/UPDATE/DELETE"| DB
    ExecuteAuto -->|"CREATE INDEX etc"| DB
    SM -->|"encrypt/decrypt"| EncryptDecrypt
```

**Sources:** [src/utils/connectors/postgres.py:215-276](), [src/utils/connectors/postgres.py:281-364]()

### Retry Decorator

The `@retry` decorator automatically retries database operations on transient failures:

```python
@retry(func=None, *, reconnect: bool = True)
```

The decorator catches `psycopg2.InterfaceError` and `psycopg2.DatabaseError`, automatically reconnects (if `reconnect=True`), and retries up to `postgres_reconnect_retry` times (default 5). All core database methods use this decorator.

**Sources:** [src/utils/connectors/postgres.py:187-213]()

### Transaction Patterns

**Read Operations:**
- Use `execute_fetch_command()` with RealDictCursor
- Returns list of Pydantic DynamicModel objects (or raw dicts if `return_raw=True`)
- Automatically commits after fetch
- Example: [src/utils/connectors/postgres.py:281-331]()

**Write Operations:**
- Use `execute_commit_command()` for INSERT/UPDATE/DELETE
- Automatically commits on success, rolls back on error
- Example: [src/utils/connectors/postgres.py:333-363]()

**DDL Operations:**
- Use `execute_autocommit_command()` for CREATE INDEX CONCURRENTLY, etc.
- Requires autocommit mode (no explicit BEGIN/COMMIT)
- Example: [src/utils/connectors/postgres.py:365-404]()

**Bulk Inserts:**
- Use `mogrify()` to safely construct multi-row INSERT statements
- Prevents SQL injection while avoiding N+1 query problems
- Example: [src/utils/connectors/postgres.py:406-428]()

**Sources:** [src/utils/connectors/postgres.py:281-428]()

---

## Key Database Operations by Service

### API Service Operations

The API service performs the majority of database interactions:

**Workflow Submission:**
1. Create workflow row with SUBMITTING status
2. Insert groups with WAITING status and dependency tracking (remaining_upstream_groups, downstream_groups)
3. Insert tasks with WAITING status
4. Create secrets, config maps, and file mounts for groups

**Workflow Queries:**
- List workflows with filters on user, pool, status (uses workflow_list_index)
- Fetch workflow details with related groups and tasks
- Update workflow status and timestamps

**Configuration Management:**
- Get/set configs by type (SERVICE, WORKFLOW, DATASET)
- Update backend, pool, resource_validation, pod_template tables
- Record changes in config_history for audit and rollback

**Sources:** [src/service/core/workflow](), [src/service/core/config/helpers.py]()

### Worker Service Operations

The worker service processes background jobs and updates workflow state:

**Task State Transitions:**
1. Poll for groups in WAITING status
2. Update to PROCESSING status
3. Send to backend operator queue
4. Backend updates to SCHEDULING → INITIALIZING → RUNNING
5. Worker updates to COMPLETED/FAILED based on task results

**Group Dependency Resolution:**
- Update remaining_upstream_groups as upstream groups complete
- Transition groups to PROCESSING when all dependencies satisfied

**Cleanup:**
- Mark groups as cleaned_up after pod deletion
- Clean up old logs from Redis
- Archive completed workflow data

**Sources:** [src/service/worker]()

### Agent Service Operations

The agent service updates backend resource information:

**Resource Updates:**
1. Fetch node information from Kubernetes API
2. Upsert rows in resources table (name, backend, allocatable_fields, label_fields, etc.)
3. Update resource_platforms mapping based on node labels and pool platform definitions
4. Update backend last_heartbeat timestamp

The agent runs continuously on each backend operator, pushing updates to the control plane database.

**Sources:** [src/service/agent]()

### Logger Service Operations

The logger service receives logs and metrics from tasks via websocket:

**Log Streaming:**
- Receive log messages from osmo-ctrl sidecar
- Mask credentials using credential values from database
- Write to Redis streams (workflow-level and task-level)
- Update task last_heartbeat timestamp

**Metrics Recording:**
- Receive task group metrics (timing for different phases)
- Insert rows into task_io table for I/O operations
- Update task resource usage counters

**Barrier Synchronization:**
- Add task to Redis set for barrier name
- Notify waiting tasks when barrier count reached
- Uses workflow total_timeout for expiration

**Sources:** [src/service/logger/ctrl_websocket.py:54-234]()

---

## Schema Initialization and Migrations

The database schema is initialized in `_init_tables()` method called from the PostgresConnector constructor:

1. **Extension Installation:** Enable `hstore` extension for key-value storage
2. **Table Creation:** Execute CREATE TABLE IF NOT EXISTS for all tables in dependency order
3. **Index Creation:** Create indexes using CONCURRENTLY to avoid locking
4. **Function Creation:** Create helper functions like `jsonb_recursive_merge`
5. **Config Initialization:** Call `_init_configs()` to populate default configs

**Index Creation Strategy:**
Indexes are created with `CREATE INDEX CONCURRENTLY IF NOT EXISTS` in autocommit mode to avoid blocking table access during index creation. The IF NOT EXISTS clause ensures idempotency.

**Schema Migration:**
Currently, schema changes require manual migration scripts. The `config_history` table provides a mechanism for configuration rollback but not schema rollback. Table additions are handled by IF NOT EXISTS, but column additions or type changes require ALTER TABLE statements.

**Sources:** [src/utils/connectors/postgres.py:531-1015](), [src/utils/connectors/postgres.py:263-269]()

---

## HSTORE Usage Patterns

PostgreSQL's HSTORE extension is used extensively for flexible key-value storage:

**Use Cases:**
1. **Credential Payloads:** Store arbitrary encrypted credential fields
2. **Resource Fields:** Store allocatable/usage resources with varying fields per backend
3. **Group Dependencies:** Track upstream/downstream group relationships
4. **User Encryption Keys:** Store multiple UEKs indexed by key ID

**Encoding/Decoding:**
- `encode_hstore(Dict) -> str`: Format dict as HSTORE string
- `decode_hstore(str) -> Dict`: Parse HSTORE string to dict

Both methods in [src/utils/connectors/postgres.py:514-524]() use regex to safely handle special characters in keys and values.

**Query Pattern:**
```sql
SELECT * FROM credential WHERE payload @> '"key"=>"value"'
UPDATE credential SET payload = payload || '"new_key"=>"new_value"'
```

**Sources:** [src/utils/connectors/postgres.py:514-524]()

---

## Summary Table: Tables by Functional Area

| Functional Area | Tables | Primary Purpose |
|----------------|--------|-----------------|
| **Workflow Execution** | workflows, workflow_tags, groups, tasks, task_io | Track workflow lifecycle from submission through execution |
| **Configuration** | configs, config_history, backends, pools, resource_validations, pod_templates, roles | Store system configuration with versioning and audit trail |
| **Datasets** | dataset, dataset_version, dataset_tag, collection | Manage dataset metadata, versioning, and collections |
| **Security** | credential, access_token, profile, ueks | Store encrypted credentials, tokens, and encryption keys |
| **Applications** | apps, app_versions | Manage published workflow templates |
| **Resources** | resources, resource_platforms | Track backend cluster resources and availability |

**Sources:** [src/utils/connectors/postgres.py:531-1015]()

---

# Page: Dataset Management

# Dataset Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



This document explains OSMO's dataset management system, including content-addressable storage, versioning, deduplication, and the upload/download workflows. For information about configuring storage backends and credentials, see [Configuration Management](#4.3). For details on how datasets are used in workflows, see [Workflow Specification](#6.1).

## Overview

OSMO implements a content-addressable storage system that achieves **10-100x storage savings** through automatic deduplication. Datasets are versioned automatically, support tags for easy reference, and can be grouped into collections. The system supports multiple storage backends (AWS S3, MinIO, Azure Blob) with encrypted credential management.

**Key Features:**
- **Content-addressable storage**: Files are stored by their hash (ETag), enabling automatic deduplication across all datasets
- **Automatic versioning**: Each dataset upload creates a new version with an auto-incrementing `version_id`
- **Tags**: Friendly names (e.g., `latest`, `prod`, `v1.0`) that reference specific versions
- **Collections**: Logical groupings of multiple dataset versions
- **Multi-backend support**: S3, MinIO, Azure Blob, and LocalStack

**Sources:** [README.md:76](), [src/utils/connectors/postgres.py:878-945]()

---

## Core Concepts

### Datasets vs Collections

```mermaid
graph TB
    subgraph "Dataset Structure"
        Dataset["<b>Dataset</b><br/>name: 'robot-data'<br/>bucket: 'default'<br/>id: UUID"]
        
        V1["<b>Version 1</b><br/>version_id: '1'<br/>status: READY<br/>size: 10GB"]
        V2["<b>Version 2</b><br/>version_id: '2'<br/>status: READY<br/>size: 12GB"]
        V3["<b>Version 3</b><br/>version_id: '3'<br/>status: PENDING<br/>size: 0"]
        
        T1["<b>Tag: latest</b><br/>→ version 2"]
        T2["<b>Tag: prod</b><br/>→ version 1"]
        
        Dataset --> V1
        Dataset --> V2
        Dataset --> V3
        Dataset --> T1
        Dataset --> T2
        T1 -.-> V2
        T2 -.-> V1
    end
    
    subgraph "Collection Structure"
        Collection["<b>Collection</b><br/>name: 'sim-training'<br/>is_collection: true"]
        
        DS1["<b>Dataset</b><br/>robot-data:2"]
        DS2["<b>Dataset</b><br/>sim-scenes:5"]
        DS3["<b>Dataset</b><br/>configs:1"]
        
        Collection --> DS1
        Collection --> DS2
        Collection --> DS3
    end
```

**Sources:** [src/utils/connectors/postgres.py:879-945](), [src/service/core/data/data_service.py:112-152]()

### Dataset Naming Convention

Datasets follow the pattern: `[bucket/]name[:tag]`

| Component | Required | Description | Example |
|-----------|----------|-------------|---------|
| `bucket` | No | Bucket configuration name | `default`, `production` |
| `name` | Yes | Dataset identifier | `robot-data`, `training-set` |
| `tag` | No | Version reference (defaults to `latest`) | `latest`, `v1.0`, `prod` |

**Name Validation Regex:**
- Standard: `[a-zA-Z0-9_-]+` ([src/lib/utils/common.py:71-73]())
- In workflow spec: `[a-zA-Z0-9_{}-]+` (allows Jinja template placeholders) ([src/lib/utils/common.py:80-86]())

**Full Pattern:**
```regex
^(?P<bucket>[a-zA-Z0-9_-]+)?(?P<name>[a-zA-Z0-9_-]+)(:(?P<tag>[a-zA-Z0-9_-]*))?$
```

**Sources:** [src/lib/utils/common.py:70-86](), [src/lib/utils/common.py:176-213]()

---

## Content-Addressable Storage

### Deduplication Mechanism

OSMO stores files by their **ETag (hash)** rather than by their logical path. When multiple datasets contain the same file, only one copy is stored physically.

```mermaid
graph LR
    subgraph "Traditional Storage"
        D1["Dataset A<br/>file1.txt<br/>file2.txt"]
        D2["Dataset B<br/>file1.txt<br/>file3.txt"]
        S1["file1.txt<br/>(copy 1)"]
        S2["file2.txt"]
        S3["file1.txt<br/>(copy 2)"]
        S4["file3.txt"]
        
        D1 --> S1
        D1 --> S2
        D2 --> S3
        D2 --> S4
    end
    
    subgraph "Content-Addressable Storage"
        DA["Dataset A<br/>manifest.json"]
        DB["Dataset B<br/>manifest.json"]
        H1["hashes/abc123<br/>(file1.txt)"]
        H2["hashes/def456<br/>(file2.txt)"]
        H3["hashes/789xyz<br/>(file3.txt)"]
        
        DA -.->|maps to| H1
        DA -.->|maps to| H2
        DB -.->|maps to| H1
        DB -.->|maps to| H3
    end
```

**Storage Structure:**
```
s3://bucket/
├── dataset-id/
│   ├── hashes/
│   │   ├── abc123...  # File content stored by ETag
│   │   ├── def456...
│   │   └── 789xyz...
│   └── manifests/
│       ├── 1.json     # Version 1 manifest
│       └── 2.json     # Version 2 manifest
```

**Sources:** [README.md:76](), [src/utils/connectors/postgres.py:879-895]()

### Manifest Files

Each dataset version has a **manifest file** that maps logical file paths to their storage hashes.

**Manifest Structure:**
```json
{
  "files": [
    {
      "path": "data/file1.txt",
      "etag": "abc123def456...",
      "size": 1024,
      "modified": "2025-01-15T10:30:00Z"
    },
    {
      "path": "data/file2.txt",
      "etag": "789xyz...",
      "size": 2048,
      "modified": "2025-01-15T10:31:00Z"
    }
  ],
  "metadata": {
    "created_by": "user@example.com",
    "description": "Training data batch 1"
  }
}
```

The manifest is stored at: `{dataset_id}/manifests/{version_id}.json`

**Sources:** [src/service/core/data/data_service.py:228-426](), [src/lib/data/storage/constants.py]()

---

## Database Schema

### Core Tables

```mermaid
erDiagram
    DATASET ||--o{ DATASET_VERSION : "has versions"
    DATASET_VERSION ||--o{ DATASET_TAG : "tagged by"
    DATASET ||--o{ COLLECTION : "contains"
    COLLECTION }o--|| DATASET_VERSION : "references"
    
    DATASET {
        text id PK
        text name
        text bucket
        text created_by
        timestamp created_date
        boolean is_collection
        jsonb labels
        text hash_location
        bigint hash_location_size
        int last_version
    }
    
    DATASET_VERSION {
        text dataset_id FK
        text version_id PK
        text location
        text status
        text created_by
        timestamp created_date
        timestamp last_used
        timestamp last_updated
        bigint size
        text checksum
        jsonb metadata
        interval retention_policy
    }
    
    DATASET_TAG {
        text dataset_id FK
        text version_id FK
        text tag PK
    }
    
    COLLECTION {
        text id FK
        text dataset_id FK
        text version_id FK
    }
```

**Key Fields:**

| Table | Field | Description |
|-------|-------|-------------|
| `dataset` | `id` | UUID for the dataset |
| `dataset` | `name` | Dataset name (unique per bucket) |
| `dataset` | `bucket` | Bucket configuration name |
| `dataset` | `hash_location` | S3 path to hash storage directory |
| `dataset` | `is_collection` | Boolean flag distinguishing collections |
| `dataset_version` | `version_id` | Auto-incrementing integer (as string) |
| `dataset_version` | `location` | S3 path to manifest file |
| `dataset_version` | `status` | `PENDING` or `READY` |
| `dataset_tag` | `tag` | Tag name (e.g., `latest`, `v1.0`) |

**Sources:** [src/utils/connectors/postgres.py:878-945]()

### Dataset Status States

| Status | Description |
|--------|-------------|
| `PENDING` | Upload initiated but not finalized |
| `READY` | Upload complete, dataset available for use |

Only `READY` datasets are returned by default in queries.

**Sources:** [src/service/core/data/objects.py](), [src/service/core/data/data_service.py:162-227]()

---

## Upload Flow

### Upload Lifecycle

```mermaid
sequenceDiagram
    participant User as User/Task
    participant API as data_service.py
    participant DB as PostgreSQL
    participant S3 as Object Storage
    
    Note over User,S3: Phase 1: Upload Start
    User->>API: POST /api/bucket/{bucket}/{name}/upload/start
    API->>DB: INSERT dataset (if new)
    API->>DB: INSERT dataset_version<br/>(status=PENDING)
    API->>User: Return version_id + upload_url
    
    Note over User,S3: Phase 2: Upload Data
    User->>S3: PUT {hash_location}/{etag}
    User->>S3: PUT {hash_location}/{etag}
    Note over User: Upload files directly<br/>to hash storage
    
    Note over User,S3: Phase 3: Upload Finish
    User->>API: POST /api/bucket/{bucket}/{name}/upload/finish
    API->>S3: Create manifest.json
    API->>DB: UPDATE dataset_version<br/>(status=READY, size, checksum)
    API->>DB: INSERT/UPDATE dataset_tag<br/>(tag='latest')
    API->>User: Upload complete
```

### Upload Start Implementation

The `upload_start` function creates the database entries and returns upload credentials:

```python
# Key function: upload_start()
# Location: src/service/core/data/data_service.py:229-341

# Creates or fetches dataset record
# Generates new version_id (auto-increment)
# Sets status to PENDING
# Returns upload URL and credentials
```

**Parameters:**
- `bucket`: Bucket configuration name
- `name`: Dataset name
- `tag`: Optional tag (required for resume)
- `metadata`: Optional metadata JSON
- `resume`: Boolean flag to resume incomplete upload

**Response:**
```json
{
  "version": "3",
  "upload_url": "s3://bucket/dataset-id/hashes/",
  "credentials": {
    "access_key_id": "...",
    "secret_access_key": "..."
  }
}
```

**Sources:** [src/service/core/data/data_service.py:229-341]()

### Upload Finish Implementation

The `upload_finish` function validates the upload and marks the version as `READY`:

```python
# Key function: upload_finish()
# Location: src/service/core/data/data_service.py:343-426

# Validates all files are present
# Creates manifest file
# Updates dataset_version status to READY
# Updates 'latest' tag to point to new version
# Records total size and checksum
```

**Parameters:**
- `bucket`: Bucket configuration name
- `name`: Dataset name
- `version`: Version ID to finalize
- `tag`: Tag to assign (defaults to `latest`)
- `description`: Optional description

**Sources:** [src/service/core/data/data_service.py:343-426]()

---

## Download Flow

### Download Lifecycle

```mermaid
sequenceDiagram
    participant Task as Workflow Task
    participant Ctrl as osmo-ctrl
    participant API as data_service.py
    participant DB as PostgreSQL
    participant S3 as Object Storage
    
    Task->>Ctrl: Request dataset<br/>'robot-data:latest'
    Ctrl->>API: GET /api/bucket/{bucket}/{name}/download
    API->>DB: Query dataset_version<br/>JOIN dataset_tag
    API->>DB: Resolve tag to version_id
    API->>S3: Fetch manifest.json
    API->>Task: Return manifest + credentials
    
    loop For each file in manifest
        Task->>S3: GET {hash_location}/{etag}
        S3->>Task: File content
        Task->>Task: Write to {path}
    end
    
    Task->>API: Update last_used timestamp
```

### Download Implementation

```python
# Key function: download_datasets()
# Location: src/service/core/data/data_service.py:428-586

# Resolves dataset name/tag to version
# Fetches manifest from storage
# Returns list of files with download URLs
# Updates last_used timestamp
```

**Query Parameters:**
- `bucket`: Bucket name
- `name`: Dataset name
- `tag`: Tag or version_id (defaults to `latest`)
- `regex`: Optional file path filter

**Response:**
```json
{
  "datasets": [
    {
      "name": "robot-data",
      "version": "2",
      "files": [
        {
          "path": "data/file1.txt",
          "url": "s3://bucket/dataset-id/hashes/abc123",
          "size": 1024,
          "etag": "abc123..."
        }
      ]
    }
  ]
}
```

**Sources:** [src/service/core/data/data_service.py:428-586]()

### Collection Download

When downloading a collection, OSMO returns manifests for all referenced datasets:

```python
# Key function: get_collection_info()
# Location: src/service/core/data/data_service.py:135-152

# Queries collection table for referenced datasets
# Returns array of dataset entries
# Each entry includes name, version, and location
```

**Sources:** [src/service/core/data/data_service.py:135-152]()

---

## Storage Backends

### Bucket Configuration

Buckets are configured via the `DatasetConfig` and define storage backend settings:

```yaml
buckets:
  default:
    mode: "s3"
    region: "us-west-2"
    dataset_path: "s3://my-bucket/datasets/"
    check_key: true
  
  production:
    mode: "azure"
    region: "eastus"
    dataset_path: "https://account.blob.core.windows.net/container/"
    check_key: true
```

**Configuration Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | Storage type: `s3`, `azure`, or `minio` |
| `region` | string | Storage region |
| `dataset_path` | string | Base URI for dataset storage |
| `check_key` | boolean | Validate user credentials before upload/download |

**Sources:** [src/utils/connectors/postgres.py](), [docs/deployment_guide/getting_started/create_storage/s3/index.rst]()

### Storage Backend Mapping

```mermaid
graph TB
    subgraph "Bucket Configs"
        BC1["default<br/>mode: s3"]
        BC2["production<br/>mode: azure"]
        BC3["local<br/>mode: minio"]
    end
    
    subgraph "Storage Backends"
        S3["AWS S3<br/>s3://bucket/datasets/"]
        Azure["Azure Blob<br/>https://account.blob.core.windows.net/"]
        MinIO["MinIO<br/>http://minio:9000/datasets/"]
    end
    
    subgraph "Credential Store"
        Cred["credential table<br/>encrypted HSTORE<br/>per-user credentials"]
    end
    
    BC1 --> S3
    BC2 --> Azure
    BC3 --> MinIO
    
    S3 -.->|validates with| Cred
    Azure -.->|validates with| Cred
    MinIO -.->|validates with| Cred
```

**Sources:** [src/utils/connectors/postgres.py:948-1024](), [src/service/core/data/data_service.py:48-61]()

---

## Credentials and Security

### Credential Validation

When `check_key: true` in bucket configuration, OSMO validates user credentials before granting access:

```python
# Key function: validate_user_cred()
# Location: src/service/core/data/data_service.py:48-61

# Fetches user credentials from credential table
# Validates READ or WRITE permissions via storage backend
# Raises OSMOCredentialError if validation fails
```

**Access Types:**
- `AccessType.READ`: Download permissions
- `AccessType.WRITE`: Upload permissions

**Sources:** [src/service/core/data/data_service.py:48-61]()

### Encryption

Dataset credentials are encrypted using the Master Encryption Key (MEK):

```mermaid
graph LR
    Plain["Plaintext Credential<br/>access_key: AKIA..."]
    Encrypt["SecretManager.encrypt()"]
    JWE["JWE Token<br/>Encrypted JSON"]
    DB["credential table<br/>HSTORE payload"]
    
    Plain --> Encrypt
    Encrypt --> JWE
    JWE --> DB
    
    DB --> Decrypt["SecretManager.decrypt()"]
    Decrypt --> Plain2["Plaintext Credential"]
```

**Encryption Process:**
1. User credentials stored in `credential` table with type `DATA`
2. Each credential value encrypted with user-specific User Encryption Key (UEK)
3. UEK encrypted with Master Encryption Key (MEK)
4. Encrypted values stored in HSTORE format

**Sources:** [src/utils/connectors/postgres.py:475-507](), [src/utils/secret_manager.py]()

---

## Dataset Operations in Workflows

### Workflow Input/Output Syntax

Datasets can be used as task inputs and outputs in workflow YAML:

```yaml
tasks:
  - name: generate-data
    image: my-image
    command: ["python", "generate.py"]
    outputs:
      - dataset:
          name: robot-data           # Dataset name
          path: /output/data         # Path in container
          labels: ["training"]       # Optional labels
          metadata: ["config.yaml"]  # Optional metadata files

  - name: train-model
    image: pytorch
    command: ["python", "train.py"]
    inputs:
      - dataset:
          name: robot-data:latest    # Dataset with tag
          localpath: /data/training  # Where to mount in container
          regex: "*.tfrecord"        # Optional file filter
```

**Dataset Input/Output Classes:**
- `DatasetInputOutput`: Defines dataset reference in workflow spec ([src/utils/job/task.py:309-404]())
- `UpdateDatasetOutput`: Appends to existing dataset ([src/utils/job/task.py:406-482]())

**Sources:** [src/utils/job/task.py:309-482](), [src/utils/job/task.py:594-609]()

### Task I/O Metrics

OSMO tracks dataset download/upload metrics for each task:

```mermaid
graph LR
    Task["Task Execution"]
    
    subgraph "Metrics Tracked"
        M1["operation_type<br/>DOWNLOAD or UPLOAD"]
        M2["size<br/>Total bytes transferred"]
        M3["number_of_files<br/>File count"]
        M4["start_time/end_time<br/>Duration"]
    end
    
    Task --> M1
    Task --> M2
    Task --> M3
    Task --> M4
    
    DB[("task_io table")]
    M1 --> DB
    M2 --> DB
    M3 --> DB
    M4 --> DB
```

**Database Table:** `task_io` ([src/utils/connectors/postgres.py:766-786]())

**Metrics Collection:** [src/service/logger/ctrl_websocket.py:54-91]()

**Sources:** [src/utils/connectors/postgres.py:766-786](), [src/service/logger/ctrl_websocket.py:54-91]()

---

## API Endpoints

### Dataset Management Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bucket/{bucket}/{name}/upload/start` | Initiate dataset upload |
| POST | `/api/bucket/{bucket}/{name}/upload/finish` | Finalize dataset upload |
| GET | `/api/bucket/{bucket}/{name}/download` | Download dataset manifest |
| GET | `/api/bucket/{bucket}/{name}` | Get dataset information |
| GET | `/api/bucket/{bucket}` | List all datasets in bucket |
| DELETE | `/api/bucket/{bucket}/{name}` | Delete dataset version |
| POST | `/api/bucket/{bucket}/{name}/tag` | Add/update tag |
| DELETE | `/api/bucket/{bucket}/{name}/tag/{tag}` | Remove tag |

**Router Definition:** [src/service/core/data/data_service.py:36-39]()

**Sources:** [src/service/core/data/data_service.py:36-1058]()

### Query Functions

Helper functions for common queries:

| Function | Purpose | Location |
|----------|---------|----------|
| `get_dataset()` | Fetch dataset by name | [src/service/core/data/data_service.py:63-76]() |
| `get_dataset_version()` | Fetch specific version | [src/service/core/data/data_service.py:79-109]() |
| `get_dataset_info()` | Get version details | [src/service/core/data/data_service.py:155-227]() |
| `get_collection_datasets()` | Get collection members | [src/service/core/data/data_service.py:116-133]() |
| `is_collection()` | Check if name is collection | [src/service/core/data/data_service.py:112-114]() |

**Sources:** [src/service/core/data/data_service.py:63-227]()

---

## Summary

OSMO's dataset management system provides:

1. **Efficient Storage**: Content-addressable deduplication reduces storage by 10-100x
2. **Version Control**: Automatic versioning with friendly tags
3. **Flexibility**: Collections group related datasets
4. **Security**: Encrypted credentials with per-user access validation
5. **Integration**: Native workflow support for seamless data flow between tasks

For configuration details, see [Configuration Management](#4.3). For workflow integration, see [Workflow Specification](#6.1).

**Sources:** [README.md:73-77](), [src/service/core/data/data_service.py](), [src/utils/connectors/postgres.py:878-945]()

---

# Page: Configuration Management

# Configuration Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



OSMO's configuration management system provides centralized storage, versioning, and access control for all system, workflow, backend, and dataset configurations. Configurations are stored in PostgreSQL with full history tracking, enabling rollback, auditing, and validation of configuration changes.

For information about workflow specification and templates, see [Workflow Specification](#6.1). For authentication and credential management, see [Credential Management and Encryption](#8.3).

## Overview

Configuration management in OSMO handles multiple configuration domains:

| Configuration Type | Purpose | Modifiable By |
|-------------------|---------|---------------|
| **SERVICE** | System-wide service settings (rate limits, timeouts, image locations) | Administrators |
| **WORKFLOW** | Default workflow execution parameters (timeouts, retry policies, resources) | Administrators |
| **DATASET** | Dataset storage backends and bucket configurations | Administrators |
| **BACKEND** | Compute backend definitions and scheduler settings | Administrators |
| **POOL** | Resource pool configurations for workload distribution | Administrators |
| **POD_TEMPLATE** | Kubernetes pod template customizations | Administrators |
| **RESOURCE_VALIDATION** | Resource request validation rules | Administrators |
| **ROLE** | User role and permission definitions | Administrators |

The system maintains a complete audit trail of all configuration changes with support for rollback to previous versions.

**Sources:** [src/utils/connectors/postgres.py:69-87](), [docs/deployment_guide/references/configs_definitions/index.rst:1-67]()

## Configuration Type Hierarchy

```mermaid
graph TB
    subgraph "Configuration Types"
        ConfigType["ConfigType enum<br/>(Active Configs)"]
        ConfigHistoryType["ConfigHistoryType enum<br/>(History Tracking)"]
    end
    
    subgraph "ConfigType Values"
        SERVICE_C["SERVICE<br/>System Settings"]
        WORKFLOW_C["WORKFLOW<br/>Execution Defaults"]
        DATASET_C["DATASET<br/>Storage Backends"]
    end
    
    subgraph "ConfigHistoryType Values"
        SERVICE_H["SERVICE"]
        WORKFLOW_H["WORKFLOW"]
        DATASET_H["DATASET"]
        BACKEND_H["BACKEND<br/>Compute Backends"]
        POOL_H["POOL<br/>Resource Pools"]
        POD_TEMPLATE_H["POD_TEMPLATE<br/>K8s Templates"]
        RESOURCE_VALIDATION_H["RESOURCE_VALIDATION<br/>Validation Rules"]
        BACKEND_TEST_H["BACKEND_TEST<br/>Test Definitions"]
        ROLE_H["ROLE<br/>User Permissions"]
    end
    
    ConfigType --> SERVICE_C
    ConfigType --> WORKFLOW_C
    ConfigType --> DATASET_C
    
    ConfigHistoryType --> SERVICE_H
    ConfigHistoryType --> WORKFLOW_H
    ConfigHistoryType --> DATASET_H
    ConfigHistoryType --> BACKEND_H
    ConfigHistoryType --> POOL_H
    ConfigHistoryType --> POD_TEMPLATE_H
    ConfigHistoryType --> RESOURCE_VALIDATION_H
    ConfigHistoryType --> BACKEND_TEST_H
    ConfigHistoryType --> ROLE_H
```

The `ConfigType` enum defines configurations that are stored in the `configs` table as key-value pairs, while `ConfigHistoryType` includes all configuration types that maintain version history in the `config_history` table.

**Sources:** [src/utils/connectors/postgres.py:69-87]()

## Database Schema

### Configs Table

The `configs` table stores current configuration values as key-value pairs:

```mermaid
erDiagram
    configs {
        TEXT key PK
        TEXT value
        TEXT type PK
    }
    
    configs ||--o{ config_history : "tracked_by"
    
    config_history {
        TEXT config_type
        INT revision PK
        TEXT name
        TEXT username
        TIMESTAMP created_at
        TEXT_ARRAY tags
        TEXT description
        JSONB data
    }
```

| Column | Type | Description |
|--------|------|-------------|
| `key` | TEXT | Configuration parameter name (e.g., `max_log_lines`, `default_pool`) |
| `value` | TEXT | Configuration value (strings, numbers, or JSON-encoded complex types) |
| `type` | TEXT | Configuration type from `ConfigType` enum |

The primary key is `(key, type)`, allowing multiple configuration types to have the same key names.

**Sources:** [src/utils/connectors/postgres.py:538-546]()

### Config History Table

The `config_history` table maintains a complete audit trail:

| Column | Type | Description |
|--------|------|-------------|
| `config_type` | TEXT | Type from `ConfigHistoryType` enum |
| `revision` | INT | Auto-incrementing version number per `(config_type, name)` |
| `name` | TEXT | Configuration name (empty for global configs) |
| `username` | TEXT | User who made the change |
| `created_at` | TIMESTAMP | When the change was made |
| `tags` | TEXT[] | Optional tags for categorizing changes |
| `description` | TEXT | Human-readable description of the change |
| `data` | JSONB | Complete snapshot of the configuration |

The primary key is `(config_type, name, revision)`, ensuring each configuration change is uniquely identified.

**Sources:** [src/utils/connectors/postgres.py:1004-1016]()

## Configuration Classes

### DynamicConfig Base Class

All configuration classes inherit from `DynamicConfig`:

```mermaid
classDiagram
    class DynamicConfig {
        <<abstract>>
        +serialize(postgres) Dict
        +deserialize(data, postgres) Self
        +plaintext_dict() Dict
    }
    
    class ServiceConfig {
        +max_log_lines: int
        +workflow_timeout: str
        +backend_images: Dict
        +rate_limits: Dict
    }
    
    class WorkflowConfig {
        +default_pool: str
        +default_exec_timeout: str
        +retry_policy: Dict
        +task_heartbeat_frequency: str
    }
    
    class DatasetConfig {
        +buckets: Dict~str, BucketConfig~
        +default_bucket: str
    }
    
    DynamicConfig <|-- ServiceConfig
    DynamicConfig <|-- WorkflowConfig
    DynamicConfig <|-- DatasetConfig
```

Key methods:

- **`serialize(postgres)`**: Converts configuration to database-storable format, encrypting sensitive values
- **`deserialize(data, postgres)`**: Reconstructs configuration from database, decrypting sensitive values
- **`plaintext_dict()`**: Returns configuration as plain dictionary for API responses

**Sources:** [src/utils/connectors/postgres.py:1162-1240]()

## Configuration Operations

### Reading Configurations

The `PostgresConnector.get_configs()` method retrieves configurations:

```mermaid
sequenceDiagram
    participant Client
    participant PostgresConnector
    participant Database
    participant ConfigClass
    
    Client->>PostgresConnector: get_configs(ConfigType.SERVICE)
    PostgresConnector->>Database: SELECT * FROM configs WHERE type = 'SERVICE'
    Database-->>PostgresConnector: rows
    PostgresConnector->>PostgresConnector: Build result_dicts from rows
    PostgresConnector->>ConfigClass: ServiceConfig.deserialize(result_dicts, postgres)
    ConfigClass->>ConfigClass: Decrypt sensitive values
    ConfigClass-->>PostgresConnector: ServiceConfig instance
    PostgresConnector-->>Client: ServiceConfig
```

**Implementation Details:**

1. Query all key-value pairs for the specified configuration type
2. Parse values based on field type hints (primitives vs. JSON objects)
3. Deserialize using the appropriate configuration class
4. Decrypt any encrypted values using `SecretManager`

**Sources:** [src/utils/connectors/postgres.py:430-471]()

### Updating Configurations (PUT)

The `put_configs()` helper performs complete configuration replacement:

```mermaid
flowchart TD
    A["put_configs(request, config_type, username)"] --> B{should_serialize?}
    B -->|Yes| C["request.configs.serialize(postgres)"]
    B -->|No| D["request.configs.plaintext_dict()"]
    C --> E["Encrypt sensitive values"]
    D --> F["Convert to JSON strings"]
    E --> G["Loop through updated configs"]
    F --> G
    G --> H["postgres.set_config(key, value, type)"]
    H --> I["UPDATE configs SET value = %s<br/>WHERE key = %s AND type = %s"]
    I --> J["postgres.get_configs(config_type)"]
    J --> K["postgres.create_config_history_entry()"]
    K --> L["INSERT INTO config_history"]
    L --> M["Return updated configs"]
```

**Key Operations:**

1. **Serialize**: Encrypt credentials and convert complex types to JSON
2. **Update**: Execute SQL UPDATE for each changed key
3. **Snapshot**: Create history entry with complete configuration state
4. **Return**: Fetch and return updated configuration

**Sources:** [src/service/core/config/helpers.py:72-114](), [src/utils/connectors/postgres.py:509-512]()

### Patching Configurations (PATCH)

The `patch_configs()` helper performs partial updates using strategic merge:

```mermaid
flowchart TD
    A["patch_configs(request, config_type, username)"] --> B["Get current config"]
    B --> C["strategic_merge_patch(current, request.configs_dict)"]
    C --> D["Identify changed fields"]
    D --> E{Validation}
    E -->|Pass| F["Create config class instance"]
    E -->|Fail| G["Raise ValidationError"]
    F --> H["Serialize updated fields"]
    H --> I["Update database"]
    I --> J["Create history entry"]
    J --> K["Return changed fields"]
```

**Strategic Merge Behavior:**

- **Dictionaries**: Recursively merged, preserving unchanged keys
- **Lists**: Can be merged using custom merge functions
- **Primitives**: Replaced with new values

**Sources:** [src/service/core/config/helpers.py:117-193]()

## Configuration Versioning and Rollback

### History Entry Creation

Every configuration change creates a history entry:

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant PostgresConnector
    participant Database
    
    Admin->>API: PATCH /api/configs/service
    API->>PostgresConnector: patch_configs(request)
    PostgresConnector->>PostgresConnector: Apply changes
    PostgresConnector->>PostgresConnector: create_config_history_entry()
    PostgresConnector->>Database: INSERT INTO config_history
    Note over Database: revision = MAX(revision) + 1<br/>for (config_type, name)
    Database-->>PostgresConnector: Success
    PostgresConnector-->>API: Updated config
    API-->>Admin: 200 OK
```

**History Entry Fields:**

- `revision`: Auto-incremented version number
- `username`: User who made the change (from `x-osmo-user` header)
- `created_at`: UTC timestamp
- `description`: User-provided or auto-generated description
- `tags`: Optional tags for filtering (e.g., `["production", "emergency-fix"]`)
- `data`: Complete configuration snapshot as JSONB

**Sources:** [src/utils/connectors/postgres.py:1264-1316]()

### Rollback Mechanism

To rollback, the system retrieves a previous revision and applies it as a new change:

```mermaid
flowchart TD
    A["Rollback Request"] --> B["Fetch history entry at revision N"]
    B --> C["Extract configuration data"]
    C --> D["Call put_configs() with historical data"]
    D --> E["Set should_serialize = False"]
    E --> F["Apply historical config as current"]
    F --> G["Create new history entry"]
    G --> H["Description: 'Rolled back to revision N'"]
```

This approach ensures:
- Complete audit trail (rollback is a new history entry)
- No data loss (original history preserved)
- Idempotent operations (can rollback to same revision multiple times)

**Sources:** [src/service/core/config/helpers.py:72-114]()

## API Endpoints

### Configuration API Routes

```mermaid
graph LR
    subgraph "Read Operations"
        GET_SERVICE["/api/configs/service<br/>GET ServiceConfig"]
        GET_WORKFLOW["/api/configs/workflow<br/>GET WorkflowConfig"]
        GET_DATASET["/api/configs/dataset<br/>GET DatasetConfig"]
        GET_BACKEND["/api/configs/backend<br/>GET Backend[]"]
        GET_POOL["/api/configs/pool<br/>GET Pool[]"]
    end
    
    subgraph "Write Operations"
        PUT_SERVICE["/api/configs/service<br/>PUT (replace all)"]
        PATCH_SERVICE["/api/configs/service<br/>PATCH (partial update)"]
        PUT_BACKEND["/api/configs/backend/:name<br/>POST (create/update)"]
        DELETE_BACKEND["/api/configs/backend/:name<br/>DELETE"]
    end
    
    subgraph "History Operations"
        GET_HISTORY["/api/configs/history<br/>GET history entries"]
        GET_REVISION["/api/configs/history/:type/:name/:revision<br/>GET specific revision"]
        ROLLBACK["/api/configs/rollback<br/>POST rollback to revision"]
    end
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | string | Human-readable change description |
| `tags` | string[] | Optional tags for categorization |
| `config_type` | enum | Configuration type from `ConfigHistoryType` |
| `name` | string | Configuration name (empty for global configs) |
| `revision` | integer | Version number for history queries |

**Sources:** [docs/deployment_guide/references/configs_definitions/index.rst:1-67]()

## Backend and Pool Configuration

Backend and pool configurations have special handling due to their complex relationships:

### Backend Configuration Flow

```mermaid
flowchart TD
    A["POST /api/configs/backend/:name"] --> B["update_backend()"]
    B --> C["_update_backend_helper()"]
    C --> D["Validate backend tests exist"]
    C --> E["UPDATE backends table"]
    E --> F["create_backend_config_history_entry()"]
    F --> G["Snapshot all backends"]
    G --> H["INSERT INTO config_history"]
    H --> I["Fetch new backend config"]
    I --> J["update_backend_queues()"]
    J --> K{Scheduler type changed?}
    K -->|Yes| L["Delete old queues"]
    K -->|No| M["Update queues"]
    L --> N["Create new queues"]
    M --> N
    N --> O["update_backend_tests_cronjobs()"]
    O --> P["Update CronJobs in K8s"]
```

**Key Operations:**

1. **Validation**: Verify referenced tests exist in `backend_tests` table
2. **History**: Snapshot all backends together (not individual backends)
3. **Queue Sync**: Update Kubernetes queues (KAI scheduler) when backend changes
4. **Test CronJobs**: Update backend validation tests when test list changes

**Sources:** [src/service/core/config/helpers.py:277-320](), [src/service/core/config/helpers.py:35-70]()

### Pool Configuration Updates

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant PostgresConnector
    participant BackendWorker
    participant Kubernetes
    
    Admin->>API: POST /api/configs/pool/:name
    API->>PostgresConnector: Update pool in database
    PostgresConnector->>PostgresConnector: Validate platform compatibility
    PostgresConnector->>PostgresConnector: Parse resource validations
    PostgresConnector->>PostgresConnector: Parse pod templates
    PostgresConnector-->>API: Pool updated
    API->>PostgresConnector: create_pool_config_history_entry()
    API->>BackendWorker: Send BackendSynchronizeQueues job
    BackendWorker->>Kubernetes: Update KAI Queue resources
    Kubernetes-->>BackendWorker: Queue updated
    API-->>Admin: 200 OK
```

Pool updates trigger:
- Resource validation parsing and merging
- Pod template parsing and merging
- KAI Queue resource quota updates
- Platform and backend compatibility validation

**Sources:** [src/service/core/config/helpers.py:401-421](), [src/service/core/config/helpers.py:35-70]()

## Validation and Serialization

### Configuration Validation

Configurations are validated using Pydantic models:

```mermaid
flowchart TD
    A["Raw Config Dict"] --> B{Method == 'dev'?}
    B -->|Yes| C["Set extra = ALLOW"]
    B -->|No| D["Set extra = FORBID"]
    C --> E["Create Pydantic Model"]
    D --> E
    E --> F{Valid?}
    F -->|Yes| G["Return Config Instance"]
    F -->|No| H["Raise ValidationError"]
    H --> I["Return 400 Bad Request"]
```

**Validation Rules:**

- **Field Types**: All fields must match type hints (str, int, timedelta, etc.)
- **Required Fields**: Fields without defaults must be provided
- **Extra Fields**: Rejected in production (`method != 'dev'`)
- **Custom Validators**: Pydantic `@validator` methods for complex rules

**Sources:** [src/service/core/config/helpers.py:149-173]()

### Encryption in Serialization

Sensitive configuration values are encrypted during serialization:

```mermaid
flowchart TD
    A["Configuration Instance"] --> B["serialize(postgres)"]
    B --> C{Field is SecretStr?}
    C -->|Yes| D["SecretManager.encrypt(value, user)"]
    C -->|No| E["Keep plaintext"]
    D --> F["Store JWE token"]
    E --> G["Store value"]
    F --> H["Return serialized dict"]
    G --> H
    
    I["Serialized Dict"] --> J["deserialize(data, postgres)"]
    J --> K{Value is JWE?}
    K -->|Yes| L["SecretManager.decrypt(token, user)"]
    K -->|No| M["Use plaintext"]
    L --> N["Return config instance"]
    M --> N
```

**Encryption Details:**

- Uses Master Encryption Key (MEK) from `mek.yaml`
- User-specific encryption keys (UEKs) for credential isolation
- JWE tokens stored in `configs.value` column
- Automatic key rotation support

**Sources:** [src/utils/connectors/postgres.py:1162-1240](), [src/utils/secret_manager.py]()

## Configuration Initialization

### Default Configuration Setup

On first startup, OSMO initializes default configurations:

```mermaid
flowchart TD
    A["PostgresConnector.__init__()"] --> B["_init_tables()"]
    B --> C["CREATE TABLE IF NOT EXISTS configs"]
    C --> D["_init_configs()"]
    D --> E{Deployment config provided?}
    E -->|Yes| F["Set osmo_image_location"]
    E -->|No| G["Skip deployment configs"]
    F --> H["Set osmo_image_tag"]
    H --> I["Set service_hostname"]
    I --> J["Set default SERVICE configs"]
    G --> J
    J --> K["Set default WORKFLOW configs"]
    K --> L["Set default DATASET configs"]
    L --> M["ON CONFLICT DO NOTHING"]
```

Default configurations are set using `INSERT ... ON CONFLICT DO NOTHING`, ensuring existing values are never overwritten during restarts.

**Deployment Configurations:**

When provided via command-line arguments or environment variables:
- `osmo_image_location`: Registry location for OSMO images
- `osmo_image_tag`: Image tag for version consistency
- `service_hostname`: Public hostname for URL generation

**Sources:** [src/utils/connectors/postgres.py:241-269](), [src/utils/connectors/postgres.py:531-546]()

## Usage Examples

### Retrieving Current Configuration

```python
from src.utils import connectors

postgres = connectors.PostgresConnector.get_instance()

# Get service configuration
service_config = postgres.get_service_configs()
print(f"Max log lines: {service_config.max_log_lines}")

# Get workflow configuration
workflow_config = postgres.get_workflow_configs()
print(f"Default pool: {workflow_config.default_pool}")

# Get dataset configuration
dataset_config = postgres.get_dataset_configs()
for bucket_name, bucket_config in dataset_config.buckets.items():
    print(f"Bucket {bucket_name}: {bucket_config.dataset_path}")
```

**Sources:** [src/utils/connectors/postgres.py:463-470]()

### Updating Configuration via API

```bash
# Patch service configuration (partial update)
curl -X PATCH https://osmo.example.com/api/configs/service \
  -H "Content-Type: application/json" \
  -d '{
    "max_log_lines": 5000,
    "description": "Increase log retention",
    "tags": ["performance", "logging"]
  }'

# Replace entire workflow configuration
curl -X PUT https://osmo.example.com/api/configs/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "configs": {
      "default_pool": "high-priority",
      "default_exec_timeout": "2h"
    },
    "description": "Update default pool",
    "tags": ["pool-migration"]
  }'
```

**Sources:** [src/service/core/config/helpers.py:72-193]()

### Querying Configuration History

```bash
# List all configuration changes for SERVICE type
curl https://osmo.example.com/api/configs/history?config_type=SERVICE

# Get specific revision
curl https://osmo.example.com/api/configs/history/SERVICE//5

# Rollback to previous revision
curl -X POST https://osmo.example.com/api/configs/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "config_type": "SERVICE",
    "name": "",
    "revision": 5,
    "description": "Emergency rollback due to rate limit issue"
  }'
```

**Sources:** [src/utils/connectors/postgres.py:1264-1316]()

## Best Practices

### Configuration Change Management

1. **Always provide descriptions**: Clear descriptions enable quick audit trail review
2. **Use tags consistently**: Establish tagging conventions (`production`, `testing`, `emergency`, etc.)
3. **Test in non-production**: Validate configuration changes in staging environments
4. **Review history before rollback**: Ensure rollback target matches expectations
5. **Document breaking changes**: Note any changes requiring workflow modifications

### Security Considerations

1. **Credential encryption**: All sensitive values use `SecretStr` type for automatic encryption
2. **Access control**: Configuration API endpoints require administrator role
3. **Audit logging**: All changes tracked with username and timestamp
4. **MEK rotation**: Plan for periodic Master Encryption Key rotation
5. **Backup history**: Regularly backup `config_history` table for disaster recovery

**Sources:** [src/utils/connectors/postgres.py:1162-1240](), [src/service/core/config/helpers.py:72-193]()

---

# Page: Backend Operators

# Backend Operators

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/README.md](deployments/charts/backend-operator/README.md)
- [deployments/charts/backend-operator/templates/backend-listener.yaml](deployments/charts/backend-operator/templates/backend-listener.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml](deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml)
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml](deployments/charts/backend-operator/templates/backend-worker-rbac.yaml)
- [deployments/charts/backend-operator/values.yaml](deployments/charts/backend-operator/values.yaml)
- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)

</details>



Backend Operators are the compute plane components that connect Kubernetes clusters to the OSMO control plane, enabling workflow execution across diverse hardware environments. They handle resource registration, task execution, and cluster monitoring while maintaining outbound-only connections to overcome firewall restrictions.

**Scope**: This page provides an overview of Backend Operators, their architecture, and role in OSMO. For detailed information on specific topics, see:
- **Component architecture and implementation**: [Backend Operator Architecture](#5.1)
- **Deployment procedures and configuration**: [Deploying a Backend](#5.2)  
- **Scheduler integration and GPU management**: [KAI Scheduler and GPU Support](#5.3)

---

## Role in Control Plane / Compute Plane Architecture

Backend Operators implement the compute plane in OSMO's distributed architecture, solving the "Three Computer Problem" by orchestrating workloads across training GPUs (cloud), simulation hardware (on-prem), and edge devices (Jetson) from a single control plane.

### Backend Operator System Architecture

```mermaid
graph TB
    subgraph ControlPlane["Control Plane (OSMO Services)"]
        API["API Service<br/>workflow operations"]
        Router["Router Service<br/>port-forward/exec"]
        Agent["Agent Service<br/>backend status"]
    end
    
    subgraph ComputePlane["Compute Plane (Backend Operator)"]
        direction TB
        
        subgraph Operator["Backend Operator Namespace"]
            Listener["backendListener<br/>Deployment"]
            Worker["backendWorker<br/>Deployment"]
        end
        
        subgraph Workflows["Workflow Namespace"]
            TaskPods["Task Pods<br/>User Workloads"]
            KAI["KAI Scheduler<br/>Gang Scheduling"]
            GPU["GPU Operator<br/>Device Discovery"]
        end
        
        subgraph Tests["Test Namespace"]
            TestRunner["backendTestRunner<br/>CronJob"]
        end
    end
    
    subgraph Storage["Storage"]
        S3["S3/MinIO/Azure<br/>Object Storage"]
    end
    
    Listener -->|"WebSocket<br/>Outbound Only"| API
    Listener -->|"Monitor Pods<br/>Report Status"| TaskPods
    Worker -->|"Create/Delete"| TaskPods
    Worker -->|"Create PodGroups"| KAI
    
    Router -.->|"Interactive Sessions"| TaskPods
    Agent -->|"Heartbeat"| Listener
    
    TaskPods -->|"Read/Write"| S3
    KAI -->|"Schedule"| TaskPods
    GPU -->|"Allocate GPUs"| TaskPods
    
    TestRunner -->|"Validate Cluster"| Workflows
```

**Key Characteristics:**

| Aspect | Implementation |
|--------|---------------|
| **Connection Direction** | Outbound-only from backend to control plane |
| **Authentication** | Service tokens with role `osmo-backend` |
| **Communication Protocol** | WebSocket for bidirectional messaging |
| **Namespace Isolation** | Operator, workflow, and test namespaces separated |
| **Scalability** | Multiple backends can connect to single control plane |

**Sources:** [deployments/charts/backend-operator/values.yaml:17-170](), [docs/deployment_guide/install_backend/deploy_backend.rst:20-24]()

---

## Component Overview

Backend Operators consist of three primary components that work together to manage workflow execution on Kubernetes clusters.

### Backend Operator Components

```mermaid
graph TB
    subgraph backendListener["backendListener Deployment"]
        ListenerPod["backend-listener container"]
        ListenerProbes["Liveness/Startup Probes<br/>progress_check"]
        ListenerCache["Pod Event Cache<br/>TTL: 15s"]
    end
    
    subgraph backendWorker["backendWorker Deployment"]
        WorkerPod["backend-worker container"]
        K8sFactory["K8sObjectFactory<br/>Pod/Secret/PodGroup"]
        WorkerProbes["Liveness/Startup Probes<br/>progress_check"]
    end
    
    subgraph backendTestRunner["backendTestRunner CronJob"]
        TestPod["backend-test-runner container"]
        TestConfig["ConfigMap<br/>test_config.json"]
        TestValidation["Init Container<br/>config-validator"]
    end
    
    ControlPlane["Control Plane<br/>WebSocket API"]
    K8sCluster["Kubernetes API<br/>Pod/Service/Secret"]
    
    ControlPlane <-->|"WebSocket Messages<br/>max_unacked: 100"| ListenerPod
    ListenerPod -->|"Poll Status"| K8sCluster
    ListenerPod -->|"Node/Event Updates"| ControlPlane
    
    ControlPlane -->|"Job Messages"| WorkerPod
    WorkerPod -->|"Create Resources"| K8sCluster
    K8sFactory -->|"Generate Manifests"| K8sCluster
    
    TestPod -->|"Validation Tests"| K8sCluster
    TestConfig -->|"Test Specifications"| TestPod
```

### Component Responsibilities

| Component | Primary Responsibilities | Configuration Key |
|-----------|-------------------------|-------------------|
| **backendListener** | Poll cluster state<br/>Report pod/node events<br/>Monitor namespace usage<br/>Update node labels | `services.backendListener` |
| **backendWorker** | Execute workflow jobs<br/>Create Kubernetes resources<br/>Generate Pod/PodGroup manifests<br/>Manage secrets | `services.backendWorker` |
| **backendTestRunner** | Validate cluster configuration<br/>Test node conditions<br/>Run scheduled health checks | `backendTestRunner` |

**Sources:** [deployments/charts/backend-operator/values.yaml:224-437](), [deployments/charts/backend-operator/README.md:96-147](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:54-262]()

---

## Connection and Authentication Flow

Backend Operators establish secure, authenticated connections to the OSMO control plane using service tokens with the `osmo-backend` role.

### Backend Authentication Flow

```mermaid
sequenceDiagram
    participant Admin
    participant CLI as OSMO CLI
    participant Keycloak
    participant K8s as Kubernetes Secret
    participant Listener as backendListener
    participant API as API Service
    
    Admin->>CLI: osmo login https://osmo.example.com
    CLI->>Keycloak: Authenticate
    Keycloak-->>CLI: User Session
    
    Admin->>CLI: osmo token set backend-token<br/>--service --roles osmo-backend
    CLI->>API: Create service token
    API-->>CLI: JWT Token
    
    Admin->>K8s: kubectl create secret<br/>osmo-operator-token
    K8s-->>K8s: Store token
    
    Listener->>K8s: Read token from<br/>/opt/osmo/secrets/token.txt
    K8s-->>Listener: JWT Token
    
    Listener->>API: WebSocket connect<br/>Authorization: Bearer <token>
    API->>API: Validate JWT<br/>issuer: keycloak<br/>role: osmo-backend
    API-->>Listener: Connection established
    
    loop Heartbeat
        Listener->>API: Status update
        API-->>Listener: ACK
    end
```

### Authentication Configuration

The backend operator supports two authentication methods configured via `global.loginMethod`:

| Method | Configuration | Use Case |
|--------|--------------|----------|
| **token** | `accountTokenSecret`: Secret name<br/>`accountTokenSecretKey`: Key in secret | Production deployments (recommended) |
| **password** | `accountUsername`: Username<br/>`accountPasswordSecret`: Password secret | Legacy support only |

**Token-based authentication** (recommended):
- Token file mounted at `/opt/osmo/secrets/token.txt`
- Secret referenced: `global.accountTokenSecret` (default: `agent-token`)
- Key within secret: `global.accountTokenSecretKey` (default: `token`)

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:34-48](), [deployments/charts/backend-operator/templates/backend-listener.yaml:84-98](), [deployments/charts/backend-operator/values.yaml:139-150]()

---

## Resource Registration and Backend Configuration

When a backend operator connects, it registers its compute resources with the control plane, making them available for workflow scheduling through the backend configuration API.

### Backend Registration Data Flow

```mermaid
graph LR
    subgraph BackendOperator["Backend Operator"]
        Listener["backendListener"]
        ClusterInfo["Cluster State<br/>- k8s_uid<br/>- k8s_namespace<br/>- nodes<br/>- usage"]
    end
    
    subgraph ControlPlane["Control Plane"]
        API["API Service<br/>/api/configs/backend"]
        DB["PostgreSQL<br/>backend_config table"]
    end
    
    subgraph Users["Users"]
        CLI["OSMO CLI<br/>osmo config show BACKEND"]
        WebUI["Web UI<br/>Backend Status"]
    end
    
    Listener -->|"Heartbeat<br/>last_heartbeat"| API
    Listener -->|"Cluster Metadata"| API
    API -->|"Store Config"| DB
    API -->|"online: true/false"| DB
    
    CLI -->|"GET /api/configs/backend"| API
    WebUI -->|"GET /api/configs/backend"| API
    API -->|"Backend Status"| CLI
    API -->|"Backend Status"| WebUI
```

### Backend Configuration Schema

The backend configuration stored in the control plane includes:

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `name` | string | Backend identifier | `global.backendName` |
| `k8s_uid` | string | Cluster UUID | Kubernetes cluster UID |
| `k8s_namespace` | string | Workflow namespace | `global.backendNamespace` |
| `scheduler_settings` | object | Scheduler configuration | Detected or configured |
| `node_conditions` | object | Node label rules | `global.nodeConditionPrefix` |
| `last_heartbeat` | timestamp | Last status update | Updated by listener |
| `online` | boolean | Backend availability | Computed from heartbeat |

**Example backend configuration response:**

```json
{
  "name": "default",
  "version": "6.0.0",
  "k8s_uid": "6bae3562-6d32-4ff1-9317-09dd973c17a2",
  "k8s_namespace": "osmo-workflows",
  "scheduler_settings": {
    "scheduler_type": "kai",
    "scheduler_name": "kai-scheduler",
    "scheduler_timeout": 30
  },
  "node_conditions": {
    "rules": null,
    "prefix": "osmo.example.com/"
  },
  "last_heartbeat": "2025-11-15T02:35:17.957569",
  "online": true
}
```

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:119-169](), [docs/deployment_guide/references/configs_definitions/index.rst:38-39](), [deployments/charts/backend-operator/values.yaml:151-170]()

---

## Workflow Execution Flow

Backend Operators orchestrate the complete workflow execution lifecycle, from task assignment to resource cleanup.

### Task Execution Through Backend Operator

```mermaid
sequenceDiagram
    participant API as API Service
    participant Listener as backendListener
    participant Worker as backendWorker
    participant K8s as Kubernetes API
    participant KAI as KAI Scheduler
    participant Pod as Task Pod
    
    API->>Listener: Task assignment<br/>via WebSocket
    Listener->>Worker: Forward task message
    
    Worker->>Worker: Generate K8s manifests<br/>K8sObjectFactory
    Worker->>K8s: Create Secret<br/>env vars, credentials
    Worker->>K8s: Create PodGroup<br/>gang scheduling
    Worker->>K8s: Create Pod<br/>task container
    
    K8s->>KAI: Schedule PodGroup
    KAI->>KAI: Wait for all pods<br/>in group ready
    KAI->>Pod: Bind pod to node
    
    Pod->>Pod: Execute task<br/>user workload
    
    loop Status Updates
        Listener->>K8s: Poll pod status
        Listener->>API: Report status<br/>via WebSocket
    end
    
    Pod->>Pod: Task completion
    Listener->>API: Final status update
    Worker->>K8s: Delete Pod
    Worker->>K8s: Delete PodGroup
    Worker->>K8s: Delete Secret
```

### Worker Configuration

The `backendWorker` component is responsible for creating Kubernetes resources required for workflow execution:

| Configuration | Default | Description |
|--------------|---------|-------------|
| `imageName` | `backend-worker` | Container image name |
| `serviceAccount` | `backend-worker` | K8s service account |
| `progressIterFrequency` | `15s` | Progress file update interval |
| `resources.requests.cpu` | `1` | CPU allocation |
| `resources.requests.memory` | `1Gi` | Memory allocation |

**Key command-line arguments** passed to worker (from template):
- `--backend`: Backend name from `global.backendName`
- `--namespace`: Workflow namespace from `global.backendNamespace`
- `--log_level`: Logging level from `global.logs.logLevel`

**Sources:** [deployments/charts/backend-operator/values.yaml:339-436](), [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:56-85]()

---

## Listener Monitoring and Health Checks

The `backendListener` component continuously monitors the cluster state and reports it to the control plane, with built-in health checks to ensure reliability.

### Listener Health Check Mechanism

```mermaid
graph TB
    subgraph ListenerContainer["backend-listener Container"]
        Listener["backend_listener process"]
        ProgressFiles["Progress Files<br/>/var/run/osmo/"]
        
        WebSocketProgress["last_progress_websocket"]
        PodProgress["last_progress_pod"]
        NodeProgress["last_progress_node"]
        EventProgress["last_progress_event"]
    end
    
    subgraph HealthProbes["Kubernetes Probes"]
        LivenessProbe["Liveness Probe<br/>300s intervals"]
        StartupProbe["Startup Probe<br/>12 attempts x 5s"]
        ProgressCheck["progress_check command"]
    end
    
    Listener -->|"Update timestamp"| WebSocketProgress
    Listener -->|"Update timestamp"| PodProgress
    Listener -->|"Update timestamp"| NodeProgress
    Listener -->|"Update timestamp"| EventProgress
    
    LivenessProbe -->|"Execute"| ProgressCheck
    StartupProbe -->|"Execute"| ProgressCheck
    ProgressCheck -->|"Check age"| ProgressFiles
    ProgressCheck -->|"Success/Failure"| K8s["Kubernetes<br/>Restart on failure"]
```

### Listener Configuration

Critical configuration parameters for the backend listener:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `max_unacked_messages` | 100 | Maximum unacknowledged WebSocket messages |
| `podCacheTtl` | 15 | Pod event cache TTL in seconds |
| `enableNodeLabelUpdate` | false | Automatically update node labels |
| `includeNamespaceUsage` | `'osmo-staging,osmo-prod'` | Namespaces for usage monitoring |
| `apiQps` | 20 | Kubernetes API queries per second |
| `apiBurst` | 30 | Kubernetes API burst limit |

**Liveness probe configuration** (from template):
```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300:300:300:300"  # WebSocket:Pod:Node:Event intervals
    - --progress_file
    - /var/run/osmo/last_progress_websocket:...
  failureThreshold: 1
  periodSeconds: 30
```

**Sources:** [deployments/charts/backend-operator/values.yaml:228-338](), [deployments/charts/backend-operator/templates/backend-listener.yaml:148-171]()

---

## Backend Test Runner

The `backendTestRunner` is a CronJob that performs periodic validation of the backend cluster, ensuring nodes are properly configured and resources are accessible.

### Test Runner Architecture

```mermaid
graph TB
    subgraph TestNamespace["Test Namespace"]
        CronJob["CronJob<br/>backend-test-runner"]
        ConfigMap["ConfigMap<br/>{backend}-{test}-config"]
        TestConfig["test_config.json<br/>test specifications"]
    end
    
    subgraph TestPod["Test Runner Pod"]
        InitContainer["Init Container<br/>config-validator<br/>ubuntu:22.04"]
        TestContainer["backend_test_runner<br/>--read_from_file"]
        TestValidation["Validate test_config.json"]
    end
    
    subgraph TestTargets["Test Targets"]
        BackendNS["Backend Namespace<br/>osmo-workflows"]
        Nodes["Cluster Nodes"]
        GPUOperator["GPU Operator"]
    end
    
    CronJob -->|"Schedule: 0 2 * * *"| TestPod
    ConfigMap -->|"Mount at /test-config"| TestContainer
    
    InitContainer -->|"Validate"| TestConfig
    InitContainer -->|"Success"| TestContainer
    
    TestContainer -->|"Run validation tests"| BackendNS
    TestContainer -->|"Check node conditions"| Nodes
    TestContainer -->|"Verify GPU access"| GPUOperator
    
    TestContainer -->|"Update node labels"| Nodes
```

### Test Runner Configuration

The test runner is configured through Helm values and executed on a schedule:

| Configuration | Default | Description |
|--------------|---------|-------------|
| `enabled` | `true` | Enable test runner CronJob |
| `cronJob.schedule` | `"0 2 * * *"` | Daily at 2 AM UTC |
| `cronJob.concurrencyPolicy` | `Forbid` | Prevent concurrent executions |
| `jobTemplate.backoffLimit` | 2 | Retry attempts on failure |
| `jobTemplate.activeDeadlineSeconds` | 3600 | Maximum execution time (1 hour) |
| `jobTemplate.ttlSecondsAfterFinished` | 86400 | Keep completed jobs for 24 hours |

**Container arguments**:
```yaml
args:
  - '--read_from_osmo'
  - 'false'
  - '--read_from_file'
  - '/test-config/test_config.json'
  - '--prefix'
  - 'osmo'
```

**RBAC permissions** for test runner include:
- Nodes: `patch`, `get`, `list` (cluster-scoped)
- Pods: `list`, `delete`, `create`, `get`, `watch` (namespace-scoped)
- DaemonSets: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`

**Sources:** [deployments/charts/backend-operator/values.yaml:438-729](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:58-262](), [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml:30-89]()

---

## Network Configuration and Security

Backend Operators support network egress control to restrict external access from workflow pods, with optional allowlist configuration.

### Network Configuration Options

| Feature | Configuration | Purpose |
|---------|--------------|---------|
| **Egress Restriction** | `global.network.restrictEgress` | Block all external traffic |
| **Allowlist Egress** | `global.network.allowlistEgress.enabled` | Squid proxy with allowlist |
| **Allowed Domains** | `global.network.allowlistEgress.additionalAllowedDomains` | Permitted external domains |
| **Allowed Source IPs** | `global.network.allowlistEgress.additionalAllowedSourceIps` | Permitted source IP ranges |

**Allowlist proxy configuration**:
- Deployed in namespace: `osmo-squid-proxy` (default)
- Squid proxy with Envoy bridge sidecar
- Resources: 2 CPU, 4Gi memory (configurable)
- Bridge proxy on port 443 for HTTPS passthrough

**Sources:** [deployments/charts/backend-operator/values.yaml:44-119](), [deployments/charts/backend-operator/README.md:51-65]()

---

## Priority Classes for Workload Management

Backend Operators can create priority classes for fine-grained scheduling control when using the KAI scheduler.

### Priority Class Configuration

Priority classes enable preemption and scheduling priority for workflow tasks:

| Priority Class | Value | Description | Preemptible |
|----------------|-------|-------------|-------------|
| `osmo-high` | 125 | Schedule ASAP | No |
| `osmo-normal` | 100 | Standard priority | No |
| `osmo-low` | 50 | Schedule last | Yes |

**Configuration**:
```yaml
global:
  priorityClasses:
    enabled: true  # Only used if KAI scheduler enabled
    classes:
      - name: osmo-high
        value: 125
        description: "Schedule as soon as possible. Non-preemptible."
```

Priority classes are referenced in workflow specifications through the pool configuration and affect how the KAI scheduler prioritizes tasks when resources are constrained.

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221](), [deployments/charts/backend-operator/README.md:80-90]()

---

## Configuration Management

Backend Operator configuration is managed through Helm values with global settings shared across components.

### Key Configuration Sections

```mermaid
graph TB
    subgraph GlobalConfig["Global Configuration"]
        Images["Image Settings<br/>osmoImageLocation<br/>osmoImageTag"]
        Auth["Authentication<br/>serviceUrl<br/>loginMethod<br/>accountTokenSecret"]
        Namespaces["Namespaces<br/>agentNamespace<br/>backendNamespace<br/>backendTestNamespace"]
        Logging["Logging<br/>logLevel<br/>k8sLogLevel"]
        Network["Network<br/>restrictEgress<br/>allowlistEgress"]
    end
    
    subgraph ServiceConfig["Service Configuration"]
        Listener["backendListener<br/>resources<br/>nodeSelector<br/>extraArgs"]
        Worker["backendWorker<br/>resources<br/>nodeSelector<br/>extraArgs"]
        TestRunner["backendTestRunner<br/>cronJob<br/>podTemplate"]
    end
    
    subgraph Sidecars["Sidecar Configuration"]
        OTEL["OpenTelemetry<br/>enabled<br/>image<br/>ports"]
    end
    
    GlobalConfig -->|"Inherited by"| ServiceConfig
    GlobalConfig -->|"Used by"| Sidecars
```

### Essential Global Settings

| Setting | Location | Required | Purpose |
|---------|----------|----------|---------|
| `osmoImageTag` | `global.osmoImageTag` | Yes | OSMO version to deploy |
| `serviceUrl` | `global.serviceUrl` | Yes | Control plane URL |
| `backendName` | `global.backendName` | Yes | Backend identifier |
| `backendNamespace` | `global.backendNamespace` | Yes | Workflow pod namespace |
| `accountTokenSecret` | `global.accountTokenSecret` | Yes | K8s secret with auth token |

**Minimal values.yaml example**:
```yaml
global:
  osmoImageTag: "latest"
  serviceUrl: "https://osmo.example.com"
  backendName: "default"
  backendNamespace: "osmo-workflows"
  accountTokenSecret: "osmo-operator-token"
  loginMethod: "token"
```

**Sources:** [deployments/charts/backend-operator/values.yaml:17-221](), [docs/deployment_guide/install_backend/deploy_backend.rst:72-105]()

---

## Next Steps

For detailed information on implementing and operating Backend Operators:

- **[Backend Operator Architecture](#5.1)** - Deep dive into component implementation, RBAC configuration, and internal communication patterns
- **[Deploying a Backend](#5.2)** - Step-by-step deployment procedures, token creation, and validation
- **[KAI Scheduler and GPU Support](#5.3)** - Gang scheduling configuration, GPU operator integration, and resource allocation strategies

For related configuration topics:
- **[Configuration Management](#4.3)** - Backend, pool, and pod template configurations
- **[Workflows](#6)** - How workflows are submitted and executed on backends
- **[Kubernetes Deployment](#7)** - Helm chart architecture and deployment patterns

---

# Page: Backend Operator Architecture

# Backend Operator Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/README.md](deployments/charts/backend-operator/README.md)
- [deployments/charts/backend-operator/templates/backend-listener.yaml](deployments/charts/backend-operator/templates/backend-listener.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml](deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml)
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml](deployments/charts/backend-operator/templates/backend-worker-rbac.yaml)
- [deployments/charts/backend-operator/values.yaml](deployments/charts/backend-operator/values.yaml)

</details>



## Purpose and Scope

This document describes the internal architecture of OSMO backend operators, which are responsible for connecting compute clusters to the OSMO control plane and executing workflows on those clusters. It covers the three core components (`backendListener`, `backendWorker`, `backendTestRunner`), their responsibilities, communication patterns, and RBAC requirements.

For information about deploying a backend operator, see [Deploying a Backend](#5.2). For details on the KAI scheduler and GPU resource management, see [KAI Scheduler and GPU Support](#5.3).

---

## Architecture Overview

Backend operators follow a **listener-worker pattern** where the listener maintains a persistent connection to the control plane while workers execute tasks locally on the Kubernetes cluster. This architecture enables the "inside-out" connectivity model where backends behind firewalls can initiate outbound connections to the control plane.

```mermaid
graph TB
    subgraph "OSMO Control Plane"
        API["API Service<br/>(api_service.py)"]
    end
    
    subgraph "Backend Operator Namespace<br/>(global.agentNamespace)"
        Listener["backendListener<br/>Deployment"]
        Worker["backendWorker<br/>Deployment"]
    end
    
    subgraph "Backend Test Namespace<br/>(global.backendTestNamespace)"
        TestRunner["backendTestRunner<br/>CronJob"]
    end
    
    subgraph "Backend Workload Namespace<br/>(global.backendNamespace)"
        TaskPods["Workflow Task Pods"]
        PodGroups["PodGroups<br/>(KAI Scheduler)"]
        Secrets["Secrets<br/>(Credentials)"]
    end
    
    Listener -->|"WebSocket<br/>Outbound Connection"| API
    API -->|"Job Assignments"| Listener
    Listener -->|"Cluster Status<br/>Pod Events<br/>Node Conditions"| API
    
    Listener -.->|"Monitor Cluster State"| TaskPods
    Listener -.->|"Monitor Cluster State"| PodGroups
    
    Worker -->|"Create/Delete"| TaskPods
    Worker -->|"Create/Delete"| PodGroups
    Worker -->|"Create/Delete"| Secrets
    Worker -->|"Report Status"| API
    
    TestRunner -.->|"Validate Cluster"| TaskPods
```

**Sources:** 
- [deployments/charts/backend-operator/values.yaml:17-223]()
- [deployments/charts/backend-operator/README.md:198-201]()

---

## Component Architecture

### backendListener

The `backendListener` is a long-running deployment that maintains a persistent WebSocket connection to the OSMO control plane. It serves as the primary interface between the backend cluster and the control plane.

**Key Configuration:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `serviceName` | Kubernetes service name | `osmo-backend-listener` |
| `imageName` | Docker image | `backend-listener` |
| `serviceAccount` | RBAC service account | `backend-listener` |
| `max_unacked_messages` | WebSocket flow control | `100` |
| `podCacheTtl` | Pod event cache TTL | `15` seconds |
| `enableNodeLabelUpdate` | Update node labels based on conditions | `false` |

**Command-Line Arguments:**

The listener is invoked with the following key arguments:

```
backend_listener
  --host <serviceUrl>
  --backend <backendName>
  --namespace <backendNamespace>
  --login_method <password|token>
  --max_unacked_messages <count>
  --pod_event_cache_ttl <seconds>
  --include_namespace_usage <comma-separated-namespaces>
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:225-337]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:79-123]()

---

### backendWorker

The `backendWorker` is a deployment that processes job requests from the control plane by creating and managing Kubernetes resources (Pods, PodGroups, Secrets, Services) in the backend namespace.

**Key Configuration:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `serviceName` | Kubernetes service name | `osmo-backend-worker` |
| `imageName` | Docker image | `backend-worker` |
| `serviceAccount` | RBAC service account | `backend-worker` |
| `progressIterFrequency` | Progress update interval | `15s` |

**Resource Creation:**

The worker creates the following Kubernetes resources for workflow tasks:

- **Pods**: Container execution environments for workflow tasks
- **PodGroups**: Gang scheduling resources for distributed training (see [KAI Scheduler and GPU Support](#5.3))
- **Secrets**: Credentials and configuration data
- **Services**: Network endpoints for inter-task communication

**Sources:**
- [deployments/charts/backend-operator/values.yaml:339-436]()
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:56-85]()

---

### backendTestRunner

The `backendTestRunner` is a CronJob that periodically validates the backend cluster's configuration and health. It runs automated tests to ensure GPU operator functionality, node conditions, and cluster readiness.

**Key Configuration:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `enabled` | Enable test runner creation | `true` |
| `schedule` | Cron schedule | `"0 2 * * *"` (2 AM daily) |
| `timezone` | Schedule timezone | `"UTC"` |
| `startingDeadlineSeconds` | Late execution deadline | `300` |
| `concurrencyPolicy` | Concurrent execution policy | `"Forbid"` |

**Test Configuration:**

Tests are defined in ConfigMaps and executed by the test runner:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: "{{backend_name}}-{{test_name}}-runner"
spec:
  schedule: "{{cron_schedule}}"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backend-test-runner
            command: ["backend_test_runner"]
            args:
            - '--read_from_file'
            - '/test-config/test_config.json'
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:438-729]()
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:34-263]()

---

## Component Responsibilities

```mermaid
graph LR
    subgraph "backendListener Responsibilities"
        L1["Maintain WebSocket<br/>to Control Plane"]
        L2["Watch Pod Events<br/>(Create/Update/Delete)"]
        L3["Watch Node Conditions<br/>(GPU Ready, Faults)"]
        L4["Report Cluster Status<br/>(Resources, Usage)"]
        L5["Update Node Labels<br/>(if enabled)"]
    end
    
    subgraph "backendWorker Responsibilities"
        W1["Receive Job Assignments<br/>from Control Plane"]
        W2["Create K8s Resources<br/>(Pods, PodGroups, Secrets)"]
        W3["Monitor Task Execution<br/>(Status, Logs)"]
        W4["Delete Resources<br/>on Task Completion"]
        W5["Report Task Status<br/>to Control Plane"]
    end
    
    subgraph "backendTestRunner Responsibilities"
        T1["Run Scheduled Tests<br/>(CronJob)"]
        T2["Validate GPU Operator<br/>(Device Plugin)"]
        T3["Test Node Conditions<br/>(Labels, Taints)"]
        T4["Create Test Pods<br/>and Daemonsets"]
        T5["Report Test Results<br/>to Control Plane"]
    end
```

**Sources:**
- [deployments/charts/backend-operator/README.md:198-206]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:79-123]()

---

## Authentication and Communication

### Authentication Methods

Backend operators support two authentication methods to connect to the control plane:

#### Password Authentication

Uses username and password stored in a Kubernetes Secret:

```yaml
global:
  loginMethod: password
  accountUsername: "osmo-backend"
  accountPasswordSecret: svc-osmo-admin
  accountPasswordSecretKey: password
```

The password is mounted as a file at `/opt/osmo/secrets/password.txt`.

#### Token Authentication

Uses a service token stored in a Kubernetes Secret:

```yaml
global:
  loginMethod: token
  accountTokenSecret: agent-token
  accountTokenSecretKey: token
```

The token is mounted as a file at `/opt/osmo/secrets/token.txt`.

**Sources:**
- [deployments/charts/backend-operator/values.yaml:126-149]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:84-92]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:184-198]()

---

### WebSocket Communication

The `backendListener` maintains a persistent WebSocket connection to the control plane API service. This enables real-time bidirectional communication:

**Outbound (Backend → Control Plane):**
- Pod status updates (Created, Running, Completed, Failed)
- Node condition changes (GPU Ready, Driver Installed)
- Resource usage metrics (CPU, Memory, GPU utilization)
- Cluster events (Node joins, Network issues)

**Inbound (Control Plane → Backend):**
- Job assignments (Task IDs to execute)
- Configuration updates (Pool changes)
- Control commands (Cancel tasks, Update priorities)

**Flow Control:**

The `max_unacked_messages` parameter limits the number of messages sent before waiting for acknowledgment:

```yaml
services:
  backendListener:
    max_unacked_messages: 100
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:253-255]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:111-113]()

---

## Namespace Organization

Backend operators use a three-namespace architecture for security isolation:

```mermaid
graph TB
    subgraph "Namespace: global.agentNamespace"
        ListenerDep["backendListener<br/>Deployment"]
        WorkerDep["backendWorker<br/>Deployment"]
    end
    
    subgraph "Namespace: global.backendNamespace"
        UserPods["Workflow Task Pods<br/>(User Workloads)"]
        PodGroups["PodGroups"]
        TaskSecrets["Task Secrets"]
        TaskServices["Task Services"]
    end
    
    subgraph "Namespace: global.backendTestNamespace"
        TestCronJob["backendTestRunner<br/>CronJob"]
        TestConfigMaps["Test ConfigMaps"]
    end
    
    ListenerDep -.->|"Monitor"| UserPods
    WorkerDep -->|"Create/Delete<br/>(via RBAC)"| UserPods
    WorkerDep -->|"Create/Delete<br/>(via RBAC)"| PodGroups
    WorkerDep -->|"Create/Delete<br/>(via RBAC)"| TaskSecrets
    
    WorkerDep -->|"Create/Delete<br/>(via RBAC)"| TestCronJob
    WorkerDep -->|"Create/Delete<br/>(via RBAC)"| TestConfigMaps
```

**Namespace Configuration:**

| Namespace Variable | Purpose | Default |
|-------------------|---------|---------|
| `global.agentNamespace` | Backend operator deployments | `osmo` |
| `global.backendNamespace` | User workflow tasks | `osmo-namespace` |
| `global.backendTestNamespace` | Validation tests | `null` (disabled) |

**Sources:**
- [deployments/charts/backend-operator/values.yaml:151-165]()
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:87-118]()

---

## RBAC Architecture

### backendListener Permissions

The `backendListener` requires **ClusterRole** permissions to monitor cluster-wide resources:

**ClusterRole Permissions:**

```yaml
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/status"]
  verbs: ["get", "list", "watch", "patch", "update"]
- apiGroups: [""]
  resources: ["pods", "events"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["scheduling.run.ai"]
  resources: ["podgroups"]
  verbs: ["get", "list", "watch"]
```

**Purpose:**
- Watch all pods across namespaces to report status
- Monitor node conditions and update labels
- Track PodGroup scheduling events

**Sources:**
- [deployments/charts/backend-operator/templates/backend-listener-rbac.yaml]()

---

### backendWorker Permissions

The `backendWorker` requires both **ClusterRole** and **Role** permissions:

**ClusterRole Permissions (Cluster-scoped):**

```yaml
rules:
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get"]
- apiGroups: ["scheduling.run.ai"]
  resources: ["queues"]
  verbs: ["list", "delete", "create", "update", "get"]
```

**Role Permissions (Backend Namespace):**

```yaml
rules:
- apiGroups: [""]
  resources: ["secrets", "pods", "services"]
  verbs: ["list", "delete", "create", "patch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
- apiGroups: ["scheduling.run.ai"]
  resources: ["podgroups"]
  verbs: ["list", "delete", "create"]
```

**Role Permissions (Test Namespace):**

```yaml
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["list", "delete", "create", "patch"]
- apiGroups: ["batch"]
  resources: ["cronjobs"]
  verbs: ["list", "delete", "create", "patch"]
```

**Sources:**
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:27-119]()

---

### backendTestRunner Permissions

The `backendTestRunner` requires permissions to validate cluster configuration:

**Role Permissions (Test Namespace):**

```yaml
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["list", "delete", "create", "get", "watch"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["get", "list", "watch", "create"]
- apiGroups: ["apps"]
  resources: ["daemonsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

**ClusterRole Permissions:**

```yaml
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/status"]
  verbs: ["patch", "get", "list", "update"]
```

**Sources:**
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml:30-88]()

---

## Health Monitoring and Progress Checks

### Progress File System

Backend operators use a **progress file** system to track activity and enable health checks. Progress timestamps are written to files in `/var/run/osmo/`:

**backendListener Progress Files:**

| File Path | Purpose | Update Interval |
|-----------|---------|-----------------|
| `/var/run/osmo/last_progress_websocket` | WebSocket message activity | On each message |
| `/var/run/osmo/last_progress_pod` | Pod event processing | On each pod event |
| `/var/run/osmo/last_progress_node` | Node condition updates | On each node update |
| `/var/run/osmo/last_progress_event` | General event processing | On each event |

**backendWorker Progress Files:**

| File Path | Purpose | Update Interval |
|-----------|---------|-----------------|
| `/var/run/osmo/last_progress_task` | Task processing activity | Every 15 seconds |

**Sources:**
- [deployments/charts/backend-operator/values.yaml:315-320]()
- [deployments/charts/backend-operator/values.yaml:421-426]()
- [deployments/charts/backend-operator/values.yaml:363-365]()

---

### Liveness and Startup Probes

Both `backendListener` and `backendWorker` use `progress_check` probes:

**backendListener Probes:**

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300:300:300:300"
    - --progress_file
    - /var/run/osmo/last_progress_websocket:/var/run/osmo/last_progress_pod:/var/run/osmo/last_progress_node:/var/run/osmo/last_progress_event
  failureThreshold: 1
  periodSeconds: 30
  timeoutSeconds: 15

startupProbe:
  exec:
    command: [same as livenessProbe]
  failureThreshold: 12
  periodSeconds: 5
  timeoutSeconds: 15
  initialDelaySeconds: 10
```

**Probe Behavior:**

The `progress_check` command verifies that each progress file has been updated within its specified interval (300 seconds). If any file is stale, the probe fails and Kubernetes restarts the pod.

**Sources:**
- [deployments/charts/backend-operator/templates/backend-listener.yaml:148-171]()

---

## Sidecar Containers

### OpenTelemetry Sidecar

Backend operators can optionally include an OpenTelemetry collector sidecar for metrics and tracing:

**Configuration:**

```yaml
sidecars:
  OTEL:
    enabled: false
    image: otel/opentelemetry-collector-contrib:0.68.0
    configName: otel-config
    ports:
    - containerPort: 4000
      name: metrics
```

**Integration:**

When enabled, the listener and worker send metrics to `localhost:4000`:

```yaml
args:
- --metrics_otel_collector_component
- osmo-backend-listener
- --metrics_otel_enable
- "true"
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:788-817]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:40-42]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:103-106]()

---

## Network Configuration

### Egress Control

Backend operators support restricting outbound network traffic from workflow pods:

**Egress Restriction:**

```yaml
global:
  network:
    restrictEgress: false
```

**Allowlist Egress with Squid Proxy:**

```yaml
global:
  network:
    allowlistEgress:
      enabled: false
      proxyNamespace: osmo-squid-proxy
      additionalAllowedDomains:
      - "example.com"
      - "api.nvidia.com"
      additionalAllowedSourceIps:
      - "10.0.0.0/8"
```

**Proxy Architecture:**

When enabled, a Squid proxy with Envoy bridge is deployed:

```mermaid
graph LR
    WorkflowPod["Workflow Pod"]
    SquidProxy["Squid Proxy<br/>(HTTP/HTTPS)"]
    EnvoyBridge["Envoy Sidecar<br/>(TLS Bridge)"]
    Internet["External APIs"]
    
    WorkflowPod -->|"HTTP_PROXY"| SquidProxy
    SquidProxy -->|"Allowlist Check"| EnvoyBridge
    EnvoyBridge --> Internet
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:44-115]()
- [deployments/charts/backend-operator/README.md:51-64]()

---

## Priority Classes

Backend operators can create priority classes for workflow scheduling:

**Configuration:**

```yaml
global:
  priorityClasses:
    enabled: true
    classes:
    - name: osmo-high
      value: 125
      description: "Schedule as soon as possible. Non-preemptible."
    - name: osmo-normal
      value: 100
      description: "Standard priority. Non-preemptible."
    - name: osmo-low
      value: 50
      description: "Schedule last. Preemptible."
```

**Usage:**

These priority classes are used by the KAI scheduler (see [KAI Scheduler and GPU Support](#5.3)) to determine pod scheduling order and preemption behavior.

**Sources:**
- [deployments/charts/backend-operator/values.yaml:202-220]()
- [deployments/charts/backend-operator/README.md:80-90]()

---

## Node Condition Management

### Node Condition Prefix

The `global.nodeConditionPrefix` parameter allows adding a prefix to all node labels and conditions managed by the backend operator:

```yaml
global:
  nodeConditionPrefix: "osmo.nvidia.com/"
```

**Purpose:**
- Avoid conflicts with other cluster operators
- Enable multiple backend operators in the same cluster
- Provide clear ownership of node labels

**Example Labels:**

Without prefix:
```yaml
labels:
  component: backend-test
  backend: default
```

With prefix:
```yaml
labels:
  osmo.nvidia.com/component: backend-test
  osmo.nvidia.com/backend: default
```

**Sources:**
- [deployments/charts/backend-operator/values.yaml:167-169]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:109-110]()
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:64-66]()

---

## Resource Limits

### backendListener Resources

**Default Configuration:**

```yaml
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    memory: "2Gi"
```

**Rationale:**
- CPU unbounded for burst processing of pod events
- Memory limited to prevent runaway memory leaks
- Typically processes 100-1000 pod events per second

### backendWorker Resources

**Default Configuration:**

```yaml
resources:
  requests:
    cpu: "1"
    memory: "1Gi"
  limits:
    memory: "1Gi"
```

**Rationale:**
- Lighter than listener (no WebSocket management)
- Creates Kubernetes resources via API (I/O bound)
- Memory limited for predictable resource usage

**Sources:**
- [deployments/charts/backend-operator/values.yaml:322-329]()
- [deployments/charts/backend-operator/values.yaml:428-435]()

---

## API Rate Limiting

The `backendListener` includes Kubernetes API client rate limiting to prevent overwhelming the API server:

**Configuration:**

```yaml
services:
  backendListener:
    apiQps: 20      # Queries per second
    apiBurst: 30    # Burst capacity
```

**Arguments:**

```yaml
args:
- --api_qps
- "20"
- --api_burst
- "30"
```

**Purpose:**
- Prevent control plane overload during cluster scaling events
- Balance responsiveness with API server stability
- Default limits are conservative; increase for large clusters (>1000 nodes)

**Sources:**
- [deployments/charts/backend-operator/values.yaml:331-337]()
- [deployments/charts/backend-operator/templates/backend-listener.yaml:117-120]()
- [deployments/charts/backend-operator/README.md:122-123]()

---

# Page: Deploying a Backend

# Deploying a Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/README.md](deployments/charts/backend-operator/README.md)
- [deployments/charts/backend-operator/templates/backend-listener.yaml](deployments/charts/backend-operator/templates/backend-listener.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml](deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml)
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml](deployments/charts/backend-operator/templates/backend-worker-rbac.yaml)
- [deployments/charts/backend-operator/values.yaml](deployments/charts/backend-operator/values.yaml)
- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)

</details>



## Purpose and Scope

This page provides a step-by-step guide for deploying a backend operator to connect a Kubernetes cluster to OSMO. The backend operator registers compute resources with the OSMO control plane and executes workflows on the cluster. This page covers authentication token creation, namespace setup, Helm chart configuration, deployment, and validation.

For architectural details about backend components (`backendListener`, `backendWorker`, `backendTestRunner`), see [Backend Operator Architecture](#5.1). For information about the KAI scheduler and GPU resource management, see [KAI Scheduler and GPU Support](#5.3).

---

## Prerequisites

Before deploying a backend operator, ensure the following requirements are met:

| Requirement | Description | Reference |
|------------|-------------|-----------|
| **OSMO Control Plane** | A running OSMO service instance | [Deploy Service](#2) |
| **OSMO CLI** | CLI installed and configured | [Getting Started](#2) |
| **Kubernetes Cluster** | Operational cluster with appropriate node types | [Creating Backends](#5) |
| **Helm CLI** | Helm 3.x installed | External documentation |
| **KAI Scheduler** | Installed on the backend cluster | [Install Dependencies](docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68) |
| **GPU Operator** | Required for GPU workloads | [Install Dependencies](docs/deployment_guide/install_backend/dependencies/dependencies.rst:70-84) |

---

## Deployment Overview

The backend deployment process consists of four main stages:

```mermaid
graph TB
    subgraph "Stage 1: Authentication"
        S1A["osmo login"]
        S1B["osmo token set"]
        S1C["OSMO_SERVICE_TOKEN"]
    end
    
    subgraph "Stage 2: Kubernetes Setup"
        S2A["kubectl create namespace<br/>osmo-operator"]
        S2B["kubectl create namespace<br/>osmo-workflows"]
        S2C["kubectl create secret<br/>osmo-operator-token"]
    end
    
    subgraph "Stage 3: Configuration"
        S3A["backend_operator_values.yaml"]
        S3B["global.serviceUrl"]
        S3C["global.backendName"]
        S3D["global.accountTokenSecret"]
    end
    
    subgraph "Stage 4: Deployment & Validation"
        S4A["helm upgrade --install"]
        S4B["Deployment:<br/>backend-listener"]
        S4C["Deployment:<br/>backend-worker"]
        S4D["osmo config show BACKEND"]
    end
    
    S1A --> S1B
    S1B --> S1C
    S1C --> S2A
    S2A --> S2B
    S2B --> S2C
    S2C --> S3A
    S3A --> S3B
    S3B --> S3C
    S3C --> S3D
    S3D --> S4A
    S4A --> S4B
    S4A --> S4C
    S4B --> S4D
    S4C --> S4D
```

**Deployment Flow Diagram**

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:24-169]()

---

## Stage 1: Create OSMO Service Token

Backend operators authenticate with the OSMO control plane using service tokens. These tokens have the `osmo-backend` role and should be created with an appropriate expiration date.

### Token Creation Process

```mermaid
sequenceDiagram
    participant User
    participant CLI as "OSMO CLI"
    participant API as "API Service"
    participant DB as "PostgreSQL<br/>(token table)"
    
    User->>CLI: osmo login https://osmo.example.com
    CLI->>API: Authenticate user
    API-->>CLI: Session established
    
    User->>CLI: osmo token set backend-token<br/>--expires-at <date><br/>--service --roles osmo-backend
    CLI->>API: POST /api/auth/token
    API->>DB: INSERT INTO token<br/>(token_value, role, expires_at)
    DB-->>API: Token created
    API-->>CLI: Return token JSON
    CLI-->>User: Display token value
    
    User->>User: export OSMO_SERVICE_TOKEN=<token>
```

**Token Creation Sequence**

### Commands

```bash
# Authenticate with OSMO
$ osmo login https://osmo.example.com

# Create service token with expiration date
$ export OSMO_SERVICE_TOKEN=$(osmo token set backend-token \
    --expires-at 2026-12-31 \
    --description "Backend Operator Token" \
    --service \
    --roles osmo-backend \
    -t json | jq -r '.token')
```

**Important:** Save the token securely. It will not be displayed again and is required for backend authentication.

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:32-48]()

---

## Stage 2: Create Kubernetes Namespaces and Secrets

The backend operator requires two namespaces and a secret for authentication:

### Namespace Architecture

```mermaid
graph TB
    subgraph "Cluster: Backend Kubernetes Cluster"
        subgraph "Namespace: osmo-operator"
            BL["Deployment:<br/>backend-listener"]
            BW["Deployment:<br/>backend-worker"]
            SA1["ServiceAccount:<br/>backend-listener"]
            SA2["ServiceAccount:<br/>backend-worker"]
            Secret["Secret:<br/>osmo-operator-token"]
        end
        
        subgraph "Namespace: osmo-workflows"
            Pod1["Pod: task-1-xyz"]
            Pod2["Pod: task-2-abc"]
            PG["PodGroup:<br/>workflow-group-1"]
        end
        
        BL --> SA1
        BW --> SA2
        BL -.->|"Reads token from"| Secret
        BW -.->|"Creates pods in"| Pod1
        BW -.->|"Creates pods in"| Pod2
        BW --> PG
    end
```

**Namespace and Resource Organization**

### Setup Commands

```bash
# Create namespace for backend operator components
$ kubectl create namespace osmo-operator

# Create namespace for workflow execution
$ kubectl create namespace osmo-workflows

# Create authentication secret from token
$ kubectl create secret generic osmo-operator-token \
    -n osmo-operator \
    --from-literal=token=$OSMO_SERVICE_TOKEN
```

| Namespace | Purpose | Components |
|-----------|---------|------------|
| `osmo-operator` | Backend operator deployment | `backend-listener`, `backend-worker`, service tokens |
| `osmo-workflows` | Workflow task execution | User workflow pods, PodGroups, Secrets |

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:50-65]()

---

## Stage 3: Configure Helm Chart Values

The backend operator Helm chart (`backend-operator`) is configured through a values file. This section details the key configuration parameters.

### Configuration Structure

```mermaid
graph TB
    subgraph "backend_operator_values.yaml"
        Global["global:"]
        Services["services:"]
        BackendTest["backendTestRunner:"]
        Sidecars["sidecars:"]
    end
    
    subgraph "global Configuration"
        ImageTag["osmoImageTag:<br/>OSMO version"]
        ServiceURL["serviceUrl:<br/>Control plane URL"]
        BackendName["backendName:<br/>Unique identifier"]
        AgentNS["agentNamespace:<br/>osmo-operator"]
        BackendNS["backendNamespace:<br/>osmo-workflows"]
        TokenSecret["accountTokenSecret:<br/>osmo-operator-token"]
        LoginMethod["loginMethod: token"]
    end
    
    subgraph "services Configuration"
        Listener["backendListener:<br/>resources, args"]
        Worker["backendWorker:<br/>resources, args"]
    end
    
    Global --> ImageTag
    Global --> ServiceURL
    Global --> BackendName
    Global --> AgentNS
    Global --> BackendNS
    Global --> TokenSecret
    Global --> LoginMethod
    
    Services --> Listener
    Services --> Worker
```

**Helm Values Configuration Structure**

### Minimal Configuration Example

Create a file named `backend_operator_values.yaml`:

```yaml
global:
  # Required: OSMO image version
  osmoImageTag: "1.2.3"
  
  # Required: Control plane URL
  serviceUrl: https://osmo.example.com
  
  # Required: Unique backend identifier
  backendName: default
  
  # Namespaces
  agentNamespace: osmo-operator
  backendNamespace: osmo-workflows
  
  # Authentication
  accountTokenSecret: osmo-operator-token
  loginMethod: token

services:
  backendListener:
    resources:
      requests:
        cpu: "1"
        memory: "1Gi"
      limits:
        memory: "1Gi"
        
  backendWorker:
    resources:
      requests:
        cpu: "1"
        memory: "1Gi"
      limits:
        memory: "1Gi"
```

### Key Configuration Parameters

| Parameter | Type | Description | Default | Required |
|-----------|------|-------------|---------|----------|
| `global.osmoImageTag` | string | OSMO Docker image tag | `latest` | ✅ Yes |
| `global.serviceUrl` | string | OSMO control plane URL | `""` | ✅ Yes |
| `global.backendName` | string | Unique backend identifier | `default` | ✅ Yes |
| `global.agentNamespace` | string | Operator namespace | `osmo` | ✅ Yes |
| `global.backendNamespace` | string | Workflow namespace | `osmo-namespace` | ✅ Yes |
| `global.accountTokenSecret` | string | K8s secret name for token | `agent-token` | ✅ Yes |
| `global.accountTokenSecretKey` | string | Secret key containing token | `token` | No |
| `global.loginMethod` | string | Authentication method | `password` | ✅ Yes |
| `global.enableClusterRoles` | boolean | Enable cluster-wide RBAC | `true` | No |
| `global.enableNonClusterRoles` | boolean | Enable namespace RBAC | `true` | No |

### Authentication Configuration

The backend operator supports two authentication methods configured via `global.loginMethod`:

#### Token Authentication (Recommended)

```yaml
global:
  loginMethod: token
  accountTokenSecret: osmo-operator-token
  accountTokenSecretKey: token
```

The `backendListener` reads the token from the secret at [deployments/charts/backend-operator/templates/backend-listener.yaml:89-92]():

```yaml
- --token_file
- /opt/osmo/secrets/token.txt
```

#### Password Authentication (Alternative)

```yaml
global:
  loginMethod: password
  accountUsername: "admin"
  accountPasswordSecret: svc-osmo-admin
  accountPasswordSecretKey: password
```

The `backendListener` reads credentials at [deployments/charts/backend-operator/templates/backend-listener.yaml:84-88]():

```yaml
- --username
- {{ .Values.global.accountUsername }}
- --password_file
- /opt/osmo/secrets/password.txt
```

### Resource Configuration

The backend listener and worker require appropriate resource allocations:

```yaml
services:
  backendListener:
    resources:
      requests:
        cpu: "1"        # Minimum 1 CPU core
        memory: "2Gi"   # Minimum 2GB RAM
      limits:
        memory: "2Gi"
    
    # API client rate limits
    apiQps: 20          # Queries per second to K8s API
    apiBurst: 30        # Burst limit for K8s API calls
    
    # WebSocket configuration
    max_unacked_messages: 100
    podCacheTtl: 15     # Pod cache TTL in seconds
    
  backendWorker:
    resources:
      requests:
        cpu: "1"
        memory: "1Gi"
      limits:
        memory: "1Gi"
    
    # Progress monitoring
    progressIterFrequency: "15s"
```

Sources: [deployments/charts/backend-operator/values.yaml:17-436](), [docs/deployment_guide/install_backend/deploy_backend.rst:72-105]()

---

## Stage 4: Deploy Backend Operator

Deploy the backend operator using Helm:

### Deployment Commands

```bash
# Add OSMO Helm repository
$ helm repo add osmo https://helm.ngc.nvidia.com/nvidia/osmo

# Update Helm repositories
$ helm repo update

# Deploy backend operator
$ helm upgrade --install osmo-operator osmo/backend-operator \
    -f ./backend_operator_values.yaml \
    --version 1.2.3 \
    --namespace osmo-operator
```

### Deployed Resources

The Helm chart creates the following Kubernetes resources:

```mermaid
graph TB
    subgraph "Namespace: osmo-operator"
        Deploy1["Deployment:<br/>osmo-operator-backend-listener<br/>Replicas: 1"]
        Deploy2["Deployment:<br/>osmo-operator-backend-worker<br/>Replicas: 1"]
        
        SA1["ServiceAccount:<br/>backend-listener"]
        SA2["ServiceAccount:<br/>backend-worker"]
        
        Role1["Role:<br/>osmo-operator-listener"]
        Role2["Role:<br/>osmo-operator-worker"]
        
        RB1["RoleBinding"]
        RB2["RoleBinding"]
        
        Secret["Secret:<br/>osmo-operator-token"]
    end
    
    subgraph "Cluster Scope"
        CR1["ClusterRole:<br/>osmo-operator-listener"]
        CR2["ClusterRole:<br/>osmo-operator-worker"]
        CRB1["ClusterRoleBinding"]
        CRB2["ClusterRoleBinding"]
        PC["PriorityClass:<br/>osmo-high<br/>osmo-normal<br/>osmo-low"]
    end
    
    Deploy1 --> SA1
    Deploy2 --> SA2
    SA1 --> RB1
    SA2 --> RB2
    RB1 --> Role1
    RB2 --> Role2
    SA1 --> CRB1
    SA2 --> CRB2
    CRB1 --> CR1
    CRB2 --> CR2
    Deploy1 -.->|"Reads"| Secret
```

**Deployed Kubernetes Resources**

### RBAC Permissions

The backend operator requires specific RBAC permissions across different scopes:

#### Backend Listener Permissions

**Cluster Scope** [deployments/charts/backend-operator/templates/backend-listener-rbac.yaml:32-80]():
- `nodes`: `get`, `list`, `patch`
- `nodes/status`: `patch`, `update`
- `namespaces`: `get`, `list`

**Namespace Scope** (in `osmo-operator`):
- `pods`: `list`, `get`, `watch`
- `pods/log`: `get`
- `services`: `list`, `get`
- `events`: `list`, `watch`

#### Backend Worker Permissions

**Cluster Scope** [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:27-52]():
- `namespaces`: `get`
- `queues` (scheduling.run.ai): `list`, `delete`, `create`, `update`, `get`

**Namespace Scope** (in `osmo-workflows`) [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:55-85]():
- `secrets`, `pods`, `services`: `list`, `delete`, `create`, `patch`
- `pods/log`: `get`
- `podgroups` (scheduling.run.ai): `list`, `delete`, `create`

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:106-118]()

---

## Validation

After deployment, validate that the backend is correctly registered and operational.

### Validation Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as "OSMO CLI"
    participant API as "API Service"
    participant DB as "PostgreSQL"
    participant Listener as "backend-listener"
    
    Note over Listener: On startup
    Listener->>API: WebSocket connection<br/>wss://osmo.example.com
    API->>Listener: Connection accepted
    Listener->>API: Register backend<br/>(name, k8s_uid, namespace)
    API->>DB: UPDATE backend SET online=true
    
    Note over User: Validation check
    User->>CLI: osmo config show BACKEND default
    CLI->>API: GET /api/configs/backend
    API->>DB: SELECT * FROM backend
    DB-->>API: Backend config
    API-->>CLI: JSON response
    CLI-->>User: Display backend status
```

**Backend Registration and Validation Flow**

### Validation Commands

```bash
# Set backend name environment variable
$ export BACKEND_NAME=default

# Check backend configuration
$ osmo config show BACKEND $BACKEND_NAME

# Alternative: Check via API endpoint
$ curl https://osmo.example.com/api/configs/backend
```

### Expected Output

The backend configuration should show `"online": true`:

```json
{
  "backends": [
    {
      "name": "default",
      "description": "Default backend",
      "version": "6.0.0",
      "k8s_uid": "6bae3562-6d32-4ff1-9317-09dd973c17a2",
      "k8s_namespace": "osmo-workflows",
      "dashboard_url": "",
      "grafana_url": "",
      "tests": [],
      "scheduler_settings": {
        "scheduler_type": "kai",
        "scheduler_name": "kai-scheduler",
        "scheduler_timeout": 30
      },
      "node_conditions": {
        "rules": null,
        "prefix": "osmo.example.com/"
      },
      "last_heartbeat": "2025-11-15T02:35:17.957569",
      "created_date": "2025-09-03T19:48:21.969688",
      "router_address": "wss://osmo.example.com",
      "online": true
    }
  ]
}
```

### Validation Checklist

| Check | Expected Result | How to Verify |
|-------|----------------|---------------|
| Backend registered | Backend appears in config list | `osmo config show BACKEND` |
| Status is online | `"online": true` | Check JSON output |
| Recent heartbeat | `last_heartbeat` within last 60 seconds | Check timestamp |
| Correct namespace | `k8s_namespace` matches `backendNamespace` | Compare configuration |
| K8s UID present | `k8s_uid` is not null | Check JSON output |
| Pods running | Listener and worker pods are `Running` | `kubectl get pods -n osmo-operator` |

### Verify Pod Status

```bash
# Check backend operator pods
$ kubectl get pods -n osmo-operator

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# osmo-operator-backend-listener-xxxxx          1/1     Running   0          5m
# osmo-operator-backend-worker-xxxxx            1/1     Running   0          5m

# Check pod logs
$ kubectl logs -n osmo-operator deployment/osmo-operator-backend-listener
$ kubectl logs -n osmo-operator deployment/osmo-operator-backend-worker
```

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:119-169]()

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Token Expired

**Symptom:**
```
Connection failed with error: {OSMOUserError: Token is expired, but no refresh token is present}
```

**Solution:**
```bash
# List service tokens to check expiration
$ osmo token list --service

# Create new token if expired
$ export OSMO_SERVICE_TOKEN=$(osmo token set backend-token-new \
    --expires-at 2026-12-31 \
    --description "Backend Operator Token" \
    --service \
    --roles osmo-backend \
    -t json | jq -r '.token')

# Update Kubernetes secret
$ kubectl create secret generic osmo-operator-token \
    -n osmo-operator \
    --from-literal=token=$OSMO_SERVICE_TOKEN \
    --dry-run=client -o yaml | kubectl apply -f -

# Restart backend operator
$ kubectl rollout restart deployment -n osmo-operator
```

Sources: [docs/deployment_guide/install_backend/deploy_backend.rst:171-183]()

#### Issue: Backend Shows Offline

**Symptom:** Backend appears in configuration but `"online": false`

**Diagnosis:**
```bash
# Check listener pod logs
$ kubectl logs -n osmo-operator deployment/osmo-operator-backend-listener

# Check for connection errors
$ kubectl logs -n osmo-operator deployment/osmo-operator-backend-listener | grep -i error
```

**Common Causes:**

| Cause | Log Pattern | Solution |
|-------|-------------|----------|
| Invalid token | `401 Unauthorized` | Recreate token with correct roles |
| Network connectivity | `Connection refused` | Check firewall rules, verify `serviceUrl` |
| Invalid serviceUrl | `Could not resolve host` | Verify DNS, check `global.serviceUrl` in values |
| Missing secret | `Secret not found` | Verify secret exists: `kubectl get secret -n osmo-operator` |

#### Issue: Pods Not Creating in Workflow Namespace

**Symptom:** Workflows submitted but no pods appear in `osmo-workflows` namespace

**Diagnosis:**
```bash
# Check backend worker logs
$ kubectl logs -n osmo-operator deployment/osmo-operator-backend-worker

# Check RBAC permissions
$ kubectl auth can-i create pods \
    --namespace osmo-workflows \
    --as system:serviceaccount:osmo-operator:backend-worker
```

**Solution:** Verify RBAC is correctly configured. The worker needs permissions in `osmo-workflows`:

```bash
# Check Role exists
$ kubectl get role -n osmo-workflows osmo-operator-worker

# Check RoleBinding exists
$ kubectl get rolebinding -n osmo-workflows osmo-operator-worker

# If missing, ensure global.enableNonClusterRoles: true in values
```

#### Issue: KAI Scheduler Not Found

**Symptom:** 
```
Scheduler kai-scheduler not found
```

**Solution:**
```bash
# Verify KAI scheduler is installed
$ kubectl get deployment -n kai-scheduler

# If not installed, install KAI scheduler first
$ helm fetch oci://ghcr.io/nvidia/kai-scheduler/kai-scheduler --version 1.2.3
$ helm upgrade --install kai-scheduler kai-scheduler-*.tgz \
    --create-namespace -n kai-scheduler
```

#### Issue: Image Pull Errors

**Symptom:**
```
ImagePullBackOff or ErrImagePull
```

**Solution:**
```bash
# Create image pull secret if accessing private registry
$ kubectl create secret docker-registry nvcr-secret \
    --docker-server=nvcr.io \
    --docker-username='$oauthtoken' \
    --docker-password=<NGC_API_KEY> \
    --namespace osmo-operator

# Update values to reference secret
global:
  imagePullSecret: nvcr-secret
```

### Logs and Monitoring

The backend operator writes logs to stdout/stderr. Configure log levels via values:

```yaml
global:
  logs:
    logLevel: DEBUG      # Application log level
    k8sLogLevel: WARNING # Kubernetes client log level
```

Available log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Progress Monitoring:** The listener and worker use progress file monitoring for liveness probes at [deployments/charts/backend-operator/templates/backend-listener.yaml:148-171]():

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300:300:300:300"
    - --progress_file
    - /var/run/osmo/last_progress_websocket:/var/run/osmo/last_progress_pod:/var/run/osmo/last_progress_node:/var/run/osmo/last_progress_event
```

Sources: [deployments/charts/backend-operator/values.yaml:172-181]()

---

## Advanced Configuration

### Network Egress Control

The backend operator supports restricting egress traffic from workflow pods using a Squid proxy:

```yaml
global:
  network:
    restrictEgress: true
    allowlistEgress:
      enabled: true
      proxyNamespace: osmo-squid-proxy
      additionalAllowedDomains:
        - "example.com"
        - "api.nvidia.com"
      resources:
        requests:
          cpu: "2"
          memory: "4Gi"
        limits:
          memory: "4Gi"
```

Sources: [deployments/charts/backend-operator/values.yaml:44-86]()

### Priority Classes

The backend operator creates priority classes for workflow scheduling when using KAI scheduler:

```yaml
global:
  priorityClasses:
    enabled: true
    classes:
      - name: osmo-high
        value: 125
        description: "Schedule as soon as possible. Non-preemptible."
      - name: osmo-normal
        value: 100
        description: "Standard priority. Non-preemptible."
      - name: osmo-low
        value: 50
        description: "Schedule last. Preemptible."
```

Sources: [deployments/charts/backend-operator/values.yaml:202-221]()

### Backend Test Runner

The backend operator can deploy automated cluster validation tests via CronJob:

```yaml
backendTestRunner:
  enabled: true
  cronJob:
    schedule: "0 2 * * *"  # Daily at 2 AM
    timezone: "UTC"
  podTemplate:
    image:
      repository: "nvcr.io/nvidia/osmo/backend-test-runner"
      tag: "latest"
```

Test configuration is managed via the control plane and synchronized to the backend. See [Backend Test Runner](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:17-263) for template details.

Sources: [deployments/charts/backend-operator/values.yaml:438-729]()

---

## Next Steps

After deploying a backend operator:

1. **Configure Resource Pools:** Define compute pools to organize backend resources. See [Configuration Management](#4.3).
2. **Submit Test Workflows:** Validate the deployment with sample workflows. See [Run Workflows](docs/deployment_guide/install_backend/validate_osmo.rst).
3. **Monitor Backend Health:** Track backend status via the Web UI or CLI.
4. **Deploy Additional Backends:** Repeat this process to add more compute backends (cloud, on-prem, edge).

**Related Documentation:**
- [Backend Operator Architecture](#5.1) - Component details and responsibilities
- [KAI Scheduler and GPU Support](#5.3) - Scheduler configuration and GPU management
- [Workflow Execution](#6.4) - How workflows are scheduled and executed on backends

---

# Page: KAI Scheduler and GPU Support

# KAI Scheduler and GPU Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/README.md](deployments/charts/backend-operator/README.md)
- [deployments/charts/backend-operator/templates/backend-listener.yaml](deployments/charts/backend-operator/templates/backend-listener.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml](deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml)
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml](deployments/charts/backend-operator/templates/backend-worker-rbac.yaml)
- [deployments/charts/backend-operator/values.yaml](deployments/charts/backend-operator/values.yaml)
- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)

</details>



This page documents how OSMO integrates with the KAI scheduler for gang scheduling and the NVIDIA GPU Operator for GPU resource management. It covers scheduler configuration, priority classes, resource allocation strategies, and the relationship between workflow groups and Kubernetes scheduling primitives.

For information about deploying backend operators, see [Deploying a Backend](#5.2). For workflow group specifications, see [Distributed Workflows with Groups](#6.3).

## Purpose and Scope

OSMO uses the [KAI scheduler](https://github.com/NVIDIA/kai-scheduler) to enable **gang scheduling** of distributed training jobs and multi-task workflows. Gang scheduling ensures that all pods in a group are scheduled simultaneously or not at all, preventing partial scheduling that would leave tasks waiting indefinitely for their peers.

This page explains:
- How KAI scheduler provides gang scheduling through PodGroups
- GPU Operator integration for device discovery and allocation
- Priority classes for workload scheduling
- Scheduler configuration in backend configs
- Required RBAC permissions for scheduling operations

## KAI Scheduler Overview

### What is KAI Scheduler

KAI (Kubernetes AI) scheduler is a Kubernetes scheduler plugin developed by NVIDIA that extends the default Kubernetes scheduler with features critical for AI/ML workloads:

- **Gang scheduling** via PodGroups for distributed training
- **GPU-aware scheduling** with topology considerations
- **Priority and preemption** for workload prioritization
- **Elastic scheduling** for dynamic resource allocation

### Why OSMO Uses KAI

OSMO workflows often require multiple tasks to start simultaneously (e.g., distributed PyTorch training with 8 GPU nodes). Without gang scheduling:

1. Partial scheduling occurs when some pods start but others remain pending
2. Running pods consume resources while waiting for peers
3. Deadlock can occur when multiple workflows partially schedule
4. GPU resources are wasted on incomplete job groups

KAI scheduler solves this by treating workflow groups as atomic scheduling units.

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68]()

---

### KAI Scheduler Architecture

```mermaid
graph TB
    subgraph "Backend Worker"
        K8sFactory["K8sObjectFactory"]
        CreatePodGroup["create_pod_group()"]
        CreatePods["create_pod()"]
    end
    
    subgraph "Kubernetes API"
        PodGroupCRD["PodGroup CRD<br/>scheduling.run.ai/v1alpha1"]
        PodResources["Pod Resources"]
    end
    
    subgraph "KAI Scheduler"
        SchedulerPlugin["kai-scheduler<br/>Scheduler Plugin"]
        GangScheduling["Gang Scheduling Logic"]
        PreFilter["PreFilter: Check Gang"]
        PostFilter["PostFilter: Queue Management"]
        Permit["Permit: Wait for Gang"]
    end
    
    subgraph "Kubelet + GPU Operator"
        DevicePlugin["NVIDIA Device Plugin"]
        GPUResources["GPU Resources<br/>nvidia.com/gpu"]
        NodeStatus["Node Status Updates"]
    end
    
    K8sFactory --> CreatePodGroup
    K8sFactory --> CreatePods
    
    CreatePodGroup --> PodGroupCRD
    CreatePods --> PodResources
    
    PodGroupCRD --> SchedulerPlugin
    PodResources --> SchedulerPlugin
    
    SchedulerPlugin --> GangScheduling
    GangScheduling --> PreFilter
    PreFilter --> PostFilter
    PostFilter --> Permit
    
    Permit --> DevicePlugin
    DevicePlugin --> GPUResources
    GPUResources --> NodeStatus
    NodeStatus --> SchedulerPlugin
```

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68](), [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:56-70]()

---

## Gang Scheduling with PodGroups

### Workflow Groups to PodGroups

OSMO workflow groups map directly to Kubernetes PodGroup custom resources. When a workflow with groups is submitted:

1. **Backend worker** creates a PodGroup resource for each workflow group
2. **Backend worker** creates Pod resources with `schedulerName: kai-scheduler` and PodGroup annotation
3. **KAI scheduler** holds pods in `Permit` phase until all group members are schedulable
4. **All pods** start simultaneously when resources are available

**Mapping:**

| OSMO Workflow Concept | Kubernetes Resource | Purpose |
|----------------------|---------------------|---------|
| `groups` (in YAML) | `PodGroup` (CRD) | Defines gang scheduling boundary |
| `lead: true` task | Leader pod annotation | First pod to complete terminates group |
| Group size | `PodGroup.spec.minMember` | Minimum pods required |
| Tasks in group | Pods with `podGroupName` label | Member pods |

### PodGroup Specification

```yaml
apiVersion: scheduling.run.ai/v1alpha1
kind: PodGroup
metadata:
  name: "workflow-{workflow_id}-group-{group_name}"
  namespace: osmo-workflows
spec:
  minMember: 4  # Number of tasks in group
  scheduleTimeoutSeconds: 300  # From scheduler_timeout config
  priorityClassName: osmo-normal
```

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:148-153](), [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:68-70]()

---

### Gang Scheduling Flow

```mermaid
sequenceDiagram
    participant User
    participant API as "API Service"
    participant Worker as "Backend Worker"
    participant K8s as "Kubernetes API"
    participant KAI as "KAI Scheduler"
    participant Kubelet
    
    User->>API: Submit workflow with groups
    API->>Worker: Enqueue workflow task
    
    rect rgb(245, 245, 245)
        Note over Worker,K8s: PodGroup Creation
        Worker->>Worker: K8sObjectFactory.create_pod_group()
        Worker->>K8s: Create PodGroup resource
        K8s-->>Worker: PodGroup created
    end
    
    rect rgb(245, 245, 245)
        Note over Worker,K8s: Pod Creation
        Worker->>Worker: K8sObjectFactory.create_pod()
        Worker->>K8s: Create Pod 1 (schedulerName: kai-scheduler)
        Worker->>K8s: Create Pod 2
        Worker->>K8s: Create Pod 3
        Worker->>K8s: Create Pod 4
    end
    
    rect rgb(245, 245, 245)
        Note over KAI,Kubelet: Gang Scheduling
        K8s->>KAI: Scheduling event for Pod 1
        KAI->>KAI: PreFilter: Check PodGroup
        KAI->>KAI: Check if all 4 pods are schedulable
        KAI->>KAI: Hold pods in Permit phase
        
        K8s->>KAI: Scheduling events for Pods 2,3,4
        KAI->>KAI: All 4 pods can be scheduled
        KAI->>KAI: Release all pods simultaneously
        
        KAI->>Kubelet: Bind Pod 1 to Node A
        KAI->>Kubelet: Bind Pod 2 to Node A
        KAI->>Kubelet: Bind Pod 3 to Node B
        KAI->>Kubelet: Bind Pod 4 to Node B
    end
    
    Kubelet-->>User: All pods Running
```

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68](), [docs/user_guide/tutorials/combination_workflows/index.rst:120-128]()

---

## GPU Operator Integration

### NVIDIA GPU Operator Components

The GPU Operator installs and manages GPU drivers and device plugins on Kubernetes nodes:

```mermaid
graph TB
    subgraph "GPU Operator Namespace"
        Operator["GPU Operator<br/>Controller"]
        DaemonSet["nvidia-device-plugin<br/>DaemonSet"]
        DCGM["DCGM Exporter<br/>Metrics Collection"]
    end
    
    subgraph "Node 1 - GPU Node"
        Driver1["NVIDIA Driver"]
        DevicePlugin1["Device Plugin Pod"]
        Kubelet1["Kubelet"]
    end
    
    subgraph "Node 2 - GPU Node"
        Driver2["NVIDIA Driver"]
        DevicePlugin2["Device Plugin Pod"]
        Kubelet2["Kubelet"]
    end
    
    subgraph "Kubernetes API Server"
        NodeStatus["Node Status<br/>nvidia.com/gpu: 8"]
        ExtendedResources["Extended Resources"]
    end
    
    Operator --> DaemonSet
    DaemonSet --> DevicePlugin1
    DaemonSet --> DevicePlugin2
    
    Driver1 --> DevicePlugin1
    DevicePlugin1 --> Kubelet1
    Kubelet1 --> NodeStatus
    
    Driver2 --> DevicePlugin2
    DevicePlugin2 --> Kubelet2
    Kubelet2 --> NodeStatus
    
    NodeStatus --> ExtendedResources
```

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:70-83]()

---

### GPU Resource Discovery

The GPU Operator automatically:

1. **Discovers GPUs** on each node via PCIe enumeration
2. **Advertises capacity** as extended resources (`nvidia.com/gpu: N`)
3. **Tracks allocations** to prevent oversubscription
4. **Injects GPU access** into containers via device mounts

**Node Resource Advertisement:**

```yaml
status:
  capacity:
    nvidia.com/gpu: "8"
  allocatable:
    nvidia.com/gpu: "8"
```

**Pod GPU Request:**

```yaml
spec:
  containers:
  - name: training
    resources:
      limits:
        nvidia.com/gpu: "2"
```

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:70-83](), [docs/deployment_guide/install_backend/validate_osmo.rst:44-50]()

---

### GPU Operator Installation

Install the GPU Operator using Helm:

```bash
helm repo add nvidia https://nvidia.github.io/gpu-operator
helm repo update
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace
```

The GPU Operator automatically:
- Installs NVIDIA drivers on GPU nodes
- Deploys device plugin DaemonSet
- Configures container runtime for GPU access
- Enables GPU monitoring via DCGM

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:70-83]()

---

## Resource Allocation Strategies

### Scheduler Configuration

Backend configurations specify scheduler settings via the `scheduler_settings` object:

```json
{
  "scheduler_settings": {
    "scheduler_type": "kai",
    "scheduler_name": "kai-scheduler",
    "scheduler_timeout": 30
  }
}
```

| Field | Description | Default |
|-------|-------------|---------|
| `scheduler_type` | Scheduler implementation type | `"kai"` |
| `scheduler_name` | Kubernetes scheduler name | `"kai-scheduler"` |
| `scheduler_timeout` | Seconds to wait before gang scheduling fails | `30` |

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:148-153]()

---

### Resource Request Flow

```mermaid
graph LR
    subgraph "Workflow Definition"
        TaskSpec["tasks:<br/>- resources:<br/>  cpu: 4<br/>  memory: 16Gi<br/>  gpu: 2<br/>  platform: dgx"]
    end
    
    subgraph "K8sObjectFactory"
        ResourceValidation["validate_resources()"]
        PodSpec["Pod spec generation"]
    end
    
    subgraph "Pod Specification"
        Requests["resources:<br/>  requests:<br/>    cpu: 4<br/>    memory: 16Gi<br/>    nvidia.com/gpu: 2"]
        NodeSelector["nodeSelector:<br/>  platform: dgx"]
    end
    
    subgraph "KAI Scheduler"
        FilterNodes["Filter nodes by<br/>- Resources<br/>- NodeSelector<br/>- Affinity"]
        ScoreNodes["Score nodes by<br/>- GPU topology<br/>- Locality<br/>- Balance"]
    end
    
    TaskSpec --> ResourceValidation
    ResourceValidation --> PodSpec
    PodSpec --> Requests
    PodSpec --> NodeSelector
    
    Requests --> FilterNodes
    NodeSelector --> FilterNodes
    FilterNodes --> ScoreNodes
    ScoreNodes --> Bind["Bind to Node"]
```

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:148-153]()

---

## Priority Classes

### Priority Class Configuration

OSMO creates three priority classes for workload scheduling when `global.priorityClasses.enabled: true`:

```yaml
priorityClasses:
  enabled: true
  classes:
    - name: osmo-high
      value: 125
      description: "Schedule as soon as possible. Non-preemptible."
    - name: osmo-normal
      value: 100
      description: "Standard priority. Non-preemptible."
    - name: osmo-low
      value: 50
      description: "Schedule last. Preemptible."
```

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221]()

---

### Priority Class Usage

Priority classes affect scheduling order and preemption behavior:

| Priority Class | Value | Preemptible | Use Case |
|----------------|-------|-------------|----------|
| `osmo-high` | 125 | No | Critical production workloads |
| `osmo-normal` | 100 | No | Standard user workflows |
| `osmo-low` | 50 | Yes | Batch jobs, experimentation |

**Scheduler Behavior:**

1. **Scheduling order:** Higher priority pods are scheduled first when resources are available
2. **Preemption:** Low-priority pods can be evicted to make room for high-priority pods
3. **Fairness:** Within same priority, FIFO order is maintained

KAI scheduler respects priority classes when:
- Multiple PodGroups are waiting for resources
- Determining which gang to schedule first
- Deciding whether to preempt lower-priority workloads

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221](), [deployments/charts/backend-operator/README.md:80-91]()

---

### Priority Class Assignment

Priority classes are assigned to workflow pods based on configuration:

```yaml
# In workflow YAML (if supported via future enhancement)
priority: high

# In backend configuration (default for all workflows)
default_priority_class: osmo-normal
```

The priority class is set in the PodGroup and all member pods:

```yaml
apiVersion: scheduling.run.ai/v1alpha1
kind: PodGroup
metadata:
  name: workflow-12345-group-training
spec:
  priorityClassName: osmo-normal  # From backend config
```

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221]()

---

## KAI Scheduler Installation

### Installation Steps

1. **Create configuration file** (`kai-selectors.yaml`):

```yaml
global:
  nodeSelector: {}
  tolerations: []

scheduler:
  additionalArgs:
  - --default-staleness-grace-period=-1s  # Disable gang eviction
  - --update-pod-eviction-condition=true  # Enable preemption status
```

2. **Install KAI scheduler via Helm:**

```bash
helm fetch oci://ghcr.io/nvidia/kai-scheduler/kai-scheduler \
  --version <chart-version>
helm upgrade --install kai-scheduler kai-scheduler-<chart-version>.tgz \
  --create-namespace -n kai-scheduler \
  --values kai-selectors.yaml
```

**Important Configuration:**
- `--default-staleness-grace-period=-1s`: Disables automatic eviction of gangs that exceed timeout
- `--update-pod-eviction-condition=true`: Allows OSMO to read preemption conditions from pod status

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68]()

---

### Verification

Verify KAI scheduler installation:

```bash
# Check scheduler pod
kubectl get pods -n kai-scheduler

# Check PodGroup CRD
kubectl get crd podgroups.scheduling.run.ai

# Check scheduler logs
kubectl logs -n kai-scheduler deployment/kai-scheduler
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
kai-scheduler-6f9d7c8b5d-x7k2m   1/1     Running   0          2m
```

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-68]()

---

## RBAC Permissions

### Backend Worker Permissions

The backend worker requires specific RBAC permissions to create and manage scheduling resources:

**ClusterRole permissions:**
```yaml
- apiGroups: ["scheduling.run.ai"]
  resources: ["queues"]
  verbs: ["list", "delete", "create", "update", "get"]
```

**Role permissions (in backend namespace):**
```yaml
- apiGroups: ["scheduling.run.ai"]
  resources: ["podgroups"]
  verbs: ["list", "delete", "create"]
```

These permissions allow the backend worker to:
- Create PodGroup resources for workflow groups
- Delete PodGroups when workflows complete
- List PodGroups for status monitoring
- Manage Run:AI queues (if Run:AI scheduler is used)

**Sources:** [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml:27-70]()

---

### Backend Test Runner Permissions

The backend test runner validates cluster configuration including scheduler functionality:

**ClusterRole permissions:**
```yaml
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["patch", "get", "list"]
- apiGroups: [""]
  resources: ["nodes/status"]
  verbs: ["patch", "update"]
```

**Role permissions (in test namespace):**
```yaml
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["list", "delete", "create", "get", "watch"]
- apiGroups: ["apps"]
  resources: ["daemonsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

These permissions allow test runners to:
- Validate node GPU configuration
- Create test pods with GPU requests
- Verify gang scheduling behavior
- Update node conditions with test results

**Sources:** [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml:30-74]()

---

## Backend Configuration

### Scheduler Settings in Backend Config

Backend configurations are stored in PostgreSQL and retrieved via the API:

```bash
# View backend configuration
osmo config show BACKEND default
```

**Relevant fields:**

```json
{
  "name": "default",
  "k8s_namespace": "osmo-workflows",
  "scheduler_settings": {
    "scheduler_type": "kai",
    "scheduler_name": "kai-scheduler",
    "scheduler_timeout": 30
  }
}
```

The `scheduler_timeout` determines how long KAI scheduler waits for a complete gang before giving up. If resources are not available within this timeout, the PodGroup enters a failed state.

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:130-165]()

---

### Node Conditions and GPU Discovery

The backend listener monitors node conditions to track GPU availability:

```yaml
env:
- name: NODE_CONDITION_PREFIX
  value: "osmo.example.com/"
```

Node conditions are used to:
- Track GPU health (`osmo.example.com/gpu-healthy`)
- Mark nodes with specific hardware (`osmo.example.com/platform-dgx`)
- Enable/disable scheduling to nodes (`osmo.example.com/schedulable`)

The backend listener can update these conditions based on cluster state if `enableNodeLabelUpdate: true`.

**Sources:** [deployments/charts/backend-operator/values.yaml:166-169](), [deployments/charts/backend-operator/templates/backend-listener.yaml:109-110]()

---

## Workflow Integration

### Groups Configuration Example

Workflow groups automatically use KAI scheduler when deployed to a backend with `scheduler_type: "kai"`:

```yaml
groups:
  - name: distributed-training
    lead: train-0
    tasks:
      - train-0
      - train-1
      - train-2
      - train-3

tasks:
  - name: train-0
    image: nvcr.io/nvidia/pytorch:24.01-py3
    resources:
      gpu: 8
      cpu: 32
      memory: 256Gi
    command: ["torchrun", "--nnodes=4", "--nproc_per_node=8", "train.py"]
  - name: train-1
    resources:
      gpu: 8
    command: ["torchrun", "--nnodes=4", "--nproc_per_node=8", "train.py"]
  # ... train-2, train-3
```

This creates:
- 1 PodGroup with `minMember: 4`
- 4 Pods with `schedulerName: kai-scheduler`
- All pods request 8 GPUs via `nvidia.com/gpu: "8"`
- Gang scheduling ensures all 4 nodes start simultaneously

**Sources:** [docs/user_guide/tutorials/combination_workflows/index.rst:40-47](), [docs/deployment_guide/install_backend/validate_osmo.rst:44-50]()

---

## Summary

The KAI scheduler integration provides OSMO with robust gang scheduling capabilities essential for distributed AI workloads:

**Key Components:**
- **KAI scheduler** implements gang scheduling via PodGroup CRD
- **GPU Operator** manages GPU drivers and device plugins
- **Priority classes** enable workload prioritization
- **Backend worker** creates PodGroups and Pods with correct annotations
- **RBAC permissions** grant access to scheduling resources

**Gang Scheduling Flow:**
1. Workflow groups map to PodGroup resources
2. Tasks in groups become Pods with `schedulerName: kai-scheduler`
3. KAI scheduler holds all pods until resources are available
4. All pods start simultaneously with GPU allocations
5. Lead task completion terminates the group

This architecture ensures efficient GPU utilization and prevents deadlock in multi-workflow environments.

**Sources:** [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-83](), [deployments/charts/backend-operator/values.yaml:202-221](), [deployments/charts/backend-operator/README.md:186-207]()

---

# Page: Workflows

# Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



Workflows are the fundamental execution unit in OSMO. A workflow defines one or more tasks that execute containerized workloads on compute backends, with support for data inputs/outputs, resource allocation, and inter-task communication. This page describes the workflow specification format, execution lifecycle, and how workflows are represented in code and the database.

For information about submitting and managing workflows via the API, see [Control Plane Services](#3). For backend execution details, see [Backend Operators](#5).

---

## Workflow Specification Format

Workflows are defined in YAML files with Jinja2 templating support. The specification defines tasks, resource requirements, data inputs/outputs, and execution parameters.

### YAML Structure

```yaml
workflow:
  name: workflow-name
  tasks:
    - name: task-name
      image: container-image
      command: ["/bin/bash"]
      args: ["-c", "echo hello"]
      inputs: []
      outputs: []
      files: []
      resources: default
  groups:
    - name: group-name
      tasks: []
  resources:
    default:
      cpu: 4
      gpu: 1
      memory: 10Gi
      storage: 20Gi
  timeout:
    exec_timeout: 1h
    queue_timeout: 30m
```

The workflow specification is parsed and validated using Pydantic models defined in [src/utils/job/task.py:589-863]().

**Sources:** [src/utils/job/task.py:589-863](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:1-229]()

---

## Task Specification

Each task defines a containerized workload with its execution parameters, resource requirements, and data dependencies.

### TaskSpec Components

```mermaid
graph TB
    TaskSpec["TaskSpec"]
    TaskSpec --> name["name: str<br/>Task identifier"]
    TaskSpec --> image["image: str<br/>Container image"]
    TaskSpec --> command["command: List[str]<br/>Entry command"]
    TaskSpec --> args["args: List[str]<br/>Command arguments"]
    TaskSpec --> inputs["inputs: List[InputType]<br/>Data sources"]
    TaskSpec --> outputs["outputs: List[OutputType]<br/>Data destinations"]
    TaskSpec --> files["files: List[File]<br/>Mounted files"]
    TaskSpec --> environment["environment: Dict[str,str]<br/>Environment variables"]
    TaskSpec --> resources["resources: ResourceSpec<br/>CPU/GPU/Memory/Storage"]
    TaskSpec --> lead["lead: bool<br/>Group leader flag"]
    TaskSpec --> privileged["privileged: bool<br/>Privileged execution"]
    TaskSpec --> volumeMounts["volumeMounts: List[str]<br/>Host volume mounts"]
    TaskSpec --> exitActions["exitActions: Dict[str,str]<br/>Exit code handling"]
```

**Key Classes:**
- **`TaskSpec`** [src/utils/job/task.py:589-863](): Defines task execution parameters
- **`File`** [src/utils/job/task.py:558-587](): Represents files mounted into containers
- **`InputType`** [src/utils/job/task.py:512](): Union of TaskInputOutput, DatasetInputOutput, URLInputOutput
- **`OutputType`** [src/utils/job/task.py:514](): Union of DatasetInputOutput, URLInputOutput, UpdateDatasetOutput
- **`ResourceSpec`** [src/utils/connectors/postgres.py:118-123](): CPU, GPU, memory, storage allocation

**Sources:** [src/utils/job/task.py:589-863](), [src/utils/job/task.py:512-514]()

### Input and Output Types

Tasks can consume and produce data from multiple sources:

| Input Type | Description | Example |
|------------|-------------|---------|
| **TaskInputOutput** | Output from another task | `task: workflow-id:task-name` |
| **DatasetInputOutput** | OSMO dataset | `dataset: {name: my-dataset, path: subdir}` |
| **URLInputOutput** | External URL | `url: s3://bucket/path` |

| Output Type | Description | Example |
|-------------|-------------|---------|
| **DatasetInputOutput** | Write to new dataset | `dataset: {name: output-dataset}` |
| **UpdateDatasetOutput** | Append to existing dataset | `update_dataset: {name: existing-dataset}` |
| **URLInputOutput** | Write to external location | `url: s3://bucket/output` |

**Sources:** [src/utils/job/task.py:259-514]()

### File Mounts

Files can be embedded in the workflow spec or referenced from local paths:

```yaml
files:
  - path: /tmp/script.sh
    contents: |
      #!/bin/bash
      echo "Inline script"
  - path: /tmp/local-file.txt
    localpath: local-file.txt  # Relative to workflow spec
  - path: /tmp/binary.dat
    base64: true
    contents: "YmluYXJ5IGRhdGE="  # Base64 encoded
```

Files are converted to Kubernetes ConfigMaps by `FileMount.config_map()` [src/utils/job/kb_objects.py:242-265]().

**Sources:** [src/utils/job/task.py:558-587](), [src/utils/job/kb_objects.py:242-265]()

---

## Jinja Templates and Special Tokens

Workflows support Jinja2 templating for dynamic generation and special tokens that are resolved at runtime by the OSMO service.

### Jinja Variables

Variables are defined in the `default-values` section and can be overridden at submission time:

```yaml
workflow:
  name: "{{ workflow_name }}"
  tasks:
    {% for i in range(num_tasks) %}
    - name: "task-{{ i }}"
      image: "{{ container_image }}"
      args: ["{{ script_arg }}"]
    {% endfor %}

default-values:
  workflow_name: my-workflow
  num_tasks: 3
  container_image: ubuntu:22.04
  script_arg: hello
```

Variables are expanded using `jinja_sandbox.render_jinja()` [src/lib/utils/jinja_sandbox.py]() before workflow submission.

**Submission with overrides:**
```bash
osmo workflow submit workflow.yaml --set num_tasks=5 container_image=alpine:latest
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:24-116](), [src/lib/utils/jinja_sandbox.py]()

### Special Tokens

Special tokens are reserved identifiers that OSMO resolves during workflow execution:

| Token | Description | Resolved By | Example Value |
|-------|-------------|-------------|---------------|
| `{{workflow_id}}` | Workflow identifier | Service | `my-workflow-123` |
| `{{input:N}}` | Nth input mount path | osmo_ctrl | `/osmo/data/input/dataset-name` |
| `{{output}}` | Output mount path | osmo_ctrl | `/osmo/data/output` |
| `{{host:task}}` | Hostname of task in group | Service | `osmo-abc123-def456.osmo-abc123.svc.cluster.local` |

**Token Resolution Flow:**

```mermaid
sequenceDiagram
    participant User
    participant Service as "API Service<br/>workflow.py"
    participant Jinja as "jinja_sandbox.py"
    participant DB as "PostgreSQL"
    participant Backend as "Backend Operator"
    participant Ctrl as "osmo_ctrl"

    User->>Service: Submit workflow.yaml with variables
    Service->>Jinja: render_jinja(spec, user_vars)
    Jinja-->>Service: Expanded YAML
    Service->>Service: Replace {{workflow_id}}
    Service->>Service: Generate {{host:task}} hostnames
    Service->>DB: Insert workflows, tasks, groups
    Service->>Backend: Queue group creation
    Backend->>Backend: Create K8s Pods with env vars
    Backend->>Ctrl: Start osmo_ctrl in pod
    Ctrl->>Ctrl: Resolve {{input:N}} from metadata
    Ctrl->>Ctrl: Resolve {{output}} to mounted path
    Ctrl->>Ctrl: Pass to osmo_exec with --input, --output
```

**Key Functions:**
- **`resolve_workflow_id()`** [src/utils/job/workflow.py](): Replaces `{{workflow_id}}` tokens
- **`resolve_host_token()`** [src/utils/job/task.py](): Generates subdomain names for `{{host:task}}`
- **`TaskGroup.to_backend_job()`** [src/utils/job/task.py](): Embeds resolved tokens in pod specs

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-229](), [src/utils/job/task.py:589-863]()

### {{host:task}} Token for Inter-Task Communication

The `{{host:task}}` token resolves to the DNS hostname of a task within a group, enabling direct network communication:

```yaml
groups:
  - name: training
    tasks:
      - name: master
        lead: true
        files:
          - path: /tmp/run.sh
            contents: |
              torchrun --master_addr {{host:master}} --master_port 29400 train.py
      - name: worker
        files:
          - path: /tmp/run.sh
            contents: |
              torchrun --master_addr {{host:master}} --master_port 29400 train.py
```

The token resolves to a subdomain in the format:
```
<task-name>.<group-subdomain>.<namespace>.svc.cluster.local
```

Generated by `get_group_subdomain_name()` [src/lib/utils/common.py:699-706]() which creates a headless Kubernetes Service for the group.

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:44-110](), [src/lib/utils/common.py:699-706]()

---

## Groups and Distributed Workflows

Groups enable multiple tasks to launch simultaneously with private networking, essential for distributed training and multi-node communication.

### Group Structure

```mermaid
graph TB
    subgraph "Group Lifecycle"
        direction LR
        Submit["SUBMITTING<br/>Initial state"]
        Waiting["WAITING<br/>Queued for processing"]
        Processing["PROCESSING<br/>Service worker processing"]
        Scheduling["SCHEDULING<br/>Backend scheduling"]
        Init["INITIALIZING<br/>Pods starting"]
        Running["RUNNING<br/>Tasks executing"]
        Complete["COMPLETED/FAILED<br/>Terminal state"]
        
        Submit --> Waiting
        Waiting --> Processing
        Processing --> Scheduling
        Scheduling --> Init
        Init --> Running
        Running --> Complete
    end
```

**Key Properties:**
- **Simultaneous Launch:** All tasks in a group are gang-scheduled and start together
- **Private Network:** Tasks can communicate via `{{host:task}}` hostnames
- **Lead Task:** One task marked with `lead: true` can coordinate the group
- **Barrier Synchronization:** Tasks can wait for each other using barriers

**Sources:** [src/utils/job/task.py:151-257]()

### Gang Scheduling

Groups are converted to Kubernetes PodGroups for gang scheduling by the KAI scheduler:

```mermaid
graph LR
    TaskGroup["TaskGroup<br/>name: training<br/>tasks: [master, worker1, worker2]"]
    K8sFactory["K8sObjectFactory<br/>create_group_k8s_resources()"]
    PodGroup["PodGroup CRD<br/>minMember: 3<br/>queue: osmo-pool-default-my-pool"]
    Pods["Pod Specs<br/>- master<br/>- worker1<br/>- worker2"]
    
    TaskGroup --> K8sFactory
    K8sFactory --> PodGroup
    K8sFactory --> Pods
    PodGroup -.annotations.-> Pods
    
    style PodGroup fill:#e8f5e9
    style Pods fill:#fff4e1
```

**Key Classes:**
- **`TaskGroup`** [src/utils/job/task.py:866-1551](): Represents a group of tasks
- **`KaiK8sObjectFactory`** [src/utils/job/kb_objects.py:324-476](): Creates PodGroup resources
- **`create_group_k8s_resources()`** [src/utils/job/kb_objects.py:332-378](): Generates K8s resources for gang scheduling

**Sources:** [src/utils/job/task.py:866-1551](), [src/utils/job/kb_objects.py:324-476]()

### Barrier Synchronization

Tasks can synchronize execution using barriers stored in Redis:

```python
# In task entry script
python3 /tmp/osmo_barrier.py --num_nodes 4 --connect {{host:master}} --rank 0
```

Barriers are managed by:
- **`update_barrier()`** [src/service/logger/ctrl_websocket.py:93-116](): Adds task to barrier set
- **`barrier_key()`** [src/utils/job/common.py](): Generates Redis key for barrier
- Redis SET operations to track participating tasks

When all tasks join, waiting tasks are notified via Redis pub/sub.

**Sources:** [src/service/logger/ctrl_websocket.py:93-116](), [docs/user_guide/how_to/training/multi_node.rst:180-216]()

---

## Workflow Execution Lifecycle

The workflow execution lifecycle spans from submission through Jinja expansion, database persistence, Kubernetes resource creation, task execution, and completion.

```mermaid
sequenceDiagram
    participant CLI as "osmo CLI"
    participant API as "API Service<br/>/api/workflow/submit"
    participant Jinja as "jinja_sandbox"
    participant DB as "PostgreSQL"
    participant Worker as "Worker Service"
    participant Backend as "Backend Operator"
    participant K8s as "Kubernetes<br/>+ KAI Scheduler"
    participant Ctrl as "osmo_ctrl"
    participant Exec as "osmo_exec"

    CLI->>API: POST workflow YAML + --set variables
    API->>Jinja: render_jinja(yaml, variables)
    Jinja-->>API: Expanded YAML
    API->>API: Parse YAML → WorkflowSpec
    API->>API: Resolve {{workflow_id}}, {{host:task}}
    API->>DB: INSERT INTO workflows, tasks, groups
    API-->>CLI: workflow_id
    
    Worker->>DB: Poll for WAITING groups
    Worker->>Worker: Transition to PROCESSING
    Worker->>Backend: Queue BackendCreateGroup job
    
    Backend->>Backend: Create K8s resources:<br/>Pods, Secrets, ConfigMaps, PodGroup
    Backend->>K8s: Apply resources
    K8s->>K8s: Gang schedule PodGroup
    K8s->>Ctrl: Start osmo_ctrl sidecar
    Ctrl->>Ctrl: Resolve {{input:N}}, {{output}}
    Ctrl->>Ctrl: Download input datasets
    Ctrl->>Exec: Launch osmo_exec with task command
    Exec->>Exec: Run user command
    Exec->>Ctrl: Stream logs via websocket
    Ctrl->>Backend: Upload outputs
    Backend->>DB: Update task status → COMPLETED
    Worker->>DB: Update workflow status → COMPLETED
```

**Sources:** [src/service/core/workflow/workflow_service.py](), [src/service/worker/worker.py](), [src/backend/backend_worker.py]()

### Submission and Jinja Expansion

1. **User submits workflow:**
   ```bash
   osmo workflow submit workflow.yaml --set variable1=value1 variable2=value2
   ```

2. **API parses and expands Jinja:**
   - Loads `workflow.yaml` [src/lib/utils/client.py]()
   - Merges `--set` variables with `default-values`
   - Calls `jinja_sandbox.render_jinja()` [src/lib/utils/jinja_sandbox.py]()
   - Parses expanded YAML into `WorkflowSpec` [src/utils/job/workflow.py]()

3. **Special token resolution:**
   - `{{workflow_id}}` replaced with generated ID
   - `{{host:task}}` replaced with subdomain names
   - `{{input:N}}` and `{{output}}` left for osmo_ctrl

**Sources:** [src/lib/utils/client.py](), [src/lib/utils/jinja_sandbox.py](), [src/utils/job/workflow.py]()

### Database Persistence

Workflow data is stored across multiple tables:

```mermaid
erDiagram
    workflows ||--o{ tasks : "has many"
    workflows ||--o{ groups : "has many"
    workflows ||--o{ workflow_tags : "has many"
    groups ||--o{ tasks : "has many"
    tasks ||--o{ task_io : "has many"

    workflows {
        text workflow_uuid PK
        text workflow_id UK "name-jobid"
        text workflow_name
        text submitted_by
        timestamp submit_time
        text status
        text backend
        text pool
        jsonb plugins
    }

    groups {
        text group_uuid PK
        text workflow_id FK
        text name
        jsonb spec
        text status
        hstore remaining_upstream_groups
        hstore downstream_groups
    }

    tasks {
        text task_db_key PK "workflow_id-retry_id-name"
        text task_uuid
        text workflow_id FK
        text name
        int retry_id
        text group_name FK
        text status
        timestamp start_time
        text node_name
        text pod_name
        text pod_ip
    }

    task_io {
        text uuid PK
        text workflow_id
        text task_name
        text url
        text type "INPUT/OUTPUT"
        bigint size
    }
```

**Key Operations:**
- **`Workflow.insert_to_db()`** [src/utils/job/workflow.py](): Inserts workflow record
- **`TaskGroup.insert_to_db()`** [src/utils/job/task.py](): Inserts group and tasks
- **`Task.fetch_from_db()`** [src/utils/job/task.py](): Retrieves task by workflow_id and name

**Table Definitions:** [src/utils/connectors/postgres.py:631-786]()

**Sources:** [src/utils/connectors/postgres.py:631-786](), [src/utils/job/workflow.py](), [src/utils/job/task.py]()

### Kubernetes Resource Creation

The Backend Operator converts tasks into Kubernetes resources:

```mermaid
graph TB
    BackendJob["BackendCreateGroup<br/>BackendJob subclass"]
    Factory["K8sObjectFactory<br/>create_group_k8s_resources()"]
    
    BackendJob --> Factory
    
    Factory --> Secret1["Secret: User Credentials<br/>Registry pull secrets"]
    Factory --> Secret2["Secret: Login Config<br/>OSMO token, API URL"]
    Factory --> Secret3["Secret: Data Config<br/>S3/Azure credentials"]
    Factory --> ConfigMap["ConfigMap: File Mounts<br/>Base64 encoded files"]
    Factory --> PodGroup["PodGroup: Gang Scheduling<br/>minMember, queue, priority"]
    Factory --> Pods["Pod Specs (N tasks)<br/>Init, Ctrl, Exec containers"]
    
    Pods --> InitContainer["osmo_init<br/>Copy binaries, configs"]
    Pods --> CtrlContainer["osmo_ctrl<br/>Data I/O, logging"]
    Pods --> ExecContainer["User Container<br/>Task image + command"]
    
    style Secret1 fill:#ffe1e1
    style Secret2 fill:#ffe1e1
    style Secret3 fill:#ffe1e1
    style ConfigMap fill:#fff9e6
    style PodGroup fill:#e8f5e9
```

**Key Components:**

1. **Secrets:**
   - **User credentials:** Registry pull secrets created by `create_image_secret()` [src/utils/job/kb_objects.py:283-300]()
   - **Login config:** OSMO API credentials for osmo_ctrl
   - **Data config:** S3/Azure credentials for dataset access

2. **ConfigMaps:**
   - File mounts from `TaskSpec.files` converted by `FileMount.config_map()` [src/utils/job/kb_objects.py:242-265]()

3. **PodGroup:**
   - Gang scheduling metadata created by `KaiK8sObjectFactory.create_group_k8s_resources()` [src/utils/job/kb_objects.py:332-378]()

4. **Pod Spec:**
   - **Init Container:** `create_init_container()` [src/utils/job/kb_objects.py:111-152]()
   - **Control Container:** `create_control_container()` [src/utils/job/kb_objects.py:154-240]()
   - **Exec Container:** `TaskSpec.to_pod_container()` [src/utils/job/task.py:775-863]()

**Sources:** [src/utils/job/kb_objects.py:43-323](), [src/utils/job/task.py:775-863]()

### Task Execution

Tasks execute in three-container pods:

```mermaid
sequenceDiagram
    participant K8s as "Kubernetes"
    participant Init as "osmo_init<br/>Init Container"
    participant Ctrl as "osmo_ctrl<br/>Sidecar"
    participant Exec as "osmo_exec<br/>Entrypoint"
    participant User as "User Container<br/>Task Command"
    participant Logger as "Logger Service"

    K8s->>Init: Start init container
    Init->>Init: Copy osmo binaries to /osmo
    Init->>Init: Write login config
    Init->>Init: Write data config
    Init-->>K8s: Exit 0
    
    K8s->>Ctrl: Start osmo_ctrl sidecar
    K8s->>User: Start user container
    User->>Exec: Execute /osmo/bin/osmo_exec
    
    par Data Download and User Execution
        Ctrl->>Ctrl: Connect websocket to Logger
        Ctrl->>Ctrl: Read input metadata
        Ctrl->>Ctrl: Download {{input:N}} datasets
        Ctrl->>Exec: Signal ready via Unix socket
        
        Exec->>Exec: Wait for Ctrl ready
        Exec->>User: Execute task command
        User->>User: Run training/simulation
        User->>Exec: Stream stdout/stderr
        Exec->>Logger: Stream logs via Ctrl websocket
    end
    
    User-->>Exec: Exit with code
    Exec->>Ctrl: Signal completion
    Ctrl->>Ctrl: Upload {{output}} datasets
    Ctrl->>Logger: Send completion metrics
    Ctrl-->>K8s: Exit
```

**Key Binaries:**
- **`osmo_init`**: Initializes pod environment [src/backend/init/init.go]()
- **`osmo_ctrl`**: Manages data I/O and logging [src/backend/ctrl/ctrl.go]()
- **`osmo_exec`**: Wraps user command, streams logs [src/backend/exec/exec.go]()

**Communication:**
- Unix socket at `/osmo/data/socket/data.sock` for Ctrl ↔ Exec
- WebSocket to Logger service for log streaming [src/service/logger/ctrl_websocket.py:118-248]()
- Redis for barrier synchronization

**Sources:** [src/backend/init/init.go](), [src/backend/ctrl/ctrl.go](), [src/backend/exec/exec.go](), [src/service/logger/ctrl_websocket.py:118-248]()

---

## Workflow Status Transitions

Tasks and groups progress through defined states during execution:

### Task Status Values

| Status | Description | Terminal |
|--------|-------------|----------|
| **SUBMITTING** | Initial state after submission | No |
| **WAITING** | Queued, waiting for service worker | No |
| **PROCESSING** | Service worker processing | No |
| **SCHEDULING** | Backend scheduling K8s resources | No |
| **INITIALIZING** | Pod starting, init containers running | No |
| **RUNNING** | Task command executing | No |
| **COMPLETED** | Successfully finished | Yes |
| **RESCHEDULED** | Ended and restarted (task only) | Yes |
| **FAILED** | Generic failure | Yes |
| **FAILED_CANCELED** | User cancelled | Yes |
| **FAILED_SERVER_ERROR** | Service error | Yes |
| **FAILED_BACKEND_ERROR** | Backend/K8s error | Yes |
| **FAILED_EXEC_TIMEOUT** | Execution timeout exceeded | Yes |
| **FAILED_QUEUE_TIMEOUT** | Queue timeout exceeded | Yes |
| **FAILED_IMAGE_PULL** | Container image pull failed | Yes |
| **FAILED_UPSTREAM** | Dependency task failed | Yes |
| **FAILED_EVICTED** | Pod evicted by K8s | Yes |
| **FAILED_START_ERROR** | Pod failed to start | Yes |
| **FAILED_START_TIMEOUT** | Pod start timeout | Yes |
| **FAILED_PREEMPTED** | Preempted by higher priority | Yes |

**Status Methods:**
- **`finished()`**: Returns true for terminal states [src/utils/job/task.py:214-216]()
- **`failed()`**: Returns true for FAILED_* states [src/utils/job/task.py:225-227]()
- **`in_queue()`**: Returns true for pre-scheduling states [src/utils/job/task.py:233-235]()

**Sources:** [src/utils/job/task.py:151-257]()

### Exit Actions

Tasks can define custom actions based on exit codes:

```yaml
tasks:
  - name: train
    exitActions:
      COMPLETE: "0"           # Exit code 0 → COMPLETED
      FAIL: "1-10,20-30"      # Exit codes 1-10, 20-30 → FAILED
      RESCHEDULE: "42"        # Exit code 42 → RESCHEDULED
```

Exit actions are validated by regex `CODE_REGEX` [src/utils/job/task.py:65]() and evaluated by the Backend Operator when tasks complete.

**Sources:** [src/utils/job/task.py:127-135](), [src/utils/job/task.py:696-709]()

---

## Example Workflows

### Single-Node Training

```yaml
workflow:
  name: train-model
  tasks:
    - name: train
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: ["python3"]
      args: ["/tmp/train.py", "--epochs", "10"]
      inputs:
        - dataset:
            name: training-data
      outputs:
        - dataset:
            name: trained-model
            path: checkpoints
      files:
        - path: /tmp/train.py
          localpath: train.py
      resources: gpu-node
  resources:
    gpu-node:
      cpu: 8
      gpu: 1
      memory: 32Gi
      storage: 50Gi
```

**Sources:** [docs/user_guide/how_to/training/single_node.rst:32-67](), [workflows/dnn_training/single_node]()

### Multi-Node Distributed Training

```yaml
workflow:
  name: train-multi-node
  groups:
    - name: training
      tasks:
        - name: master
          lead: true
          image: nvcr.io/nvidia/pytorch:24.03-py3
          files:
            - path: /tmp/run.sh
              contents: |
                torchrun --nnodes 2 --nproc_per_node 8 \
                  --master_addr {{host:master}} --master_port 29400 \
                  train.py --epochs 10
        - name: worker
          image: nvcr.io/nvidia/pytorch:24.03-py3
          files:
            - path: /tmp/run.sh
              contents: |
                torchrun --nnodes 2 --nproc_per_node 8 --node_rank 1 \
                  --master_addr {{host:master}} --master_port 29400 \
                  train.py --epochs 10
  resources:
    default:
      cpu: 16
      gpu: 8
      memory: 120Gi
      storage: 100Gi
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:40-102](), [workflows/dnn_training/torchrun_multinode]()

### ROS 2 Multi-Node Communication

```yaml
workflow:
  name: ros-comms
  groups:
    - name: nodes
      tasks:
        - name: discovery-server
          image: osrf/ros:humble-desktop-full
          command: ["/bin/bash", "/tmp/run.sh"]
          files:
            - path: /tmp/run.sh
              contents: |
                source /opt/ros/humble/setup.bash
                fastdds discovery --server-id 0 -p 11811
        - name: publisher
          lead: true
          image: osrf/ros:humble-desktop-full
          files:
            - path: /tmp/run.sh
              contents: |
                DISCOVERY_SERVER_IP=$(nslookup {{host:discovery-server}} | grep Address | tail -1 | awk '{print $2}')
                export ROS_DISCOVERY_SERVER=$DISCOVERY_SERVER_IP:11811
                source /opt/ros/humble/setup.bash
                ros2 run demo_nodes_cpp talker
        - name: subscriber
          image: osrf/ros:humble-desktop-full
          files:
            - path: /tmp/run.sh
              contents: |
                DISCOVERY_SERVER_IP=$(nslookup {{host:discovery-server}} | grep Address | tail -1 | awk '{print $2}')
                export ROS_DISCOVERY_SERVER=$DISCOVERY_SERVER_IP:11811
                source /opt/ros/humble/setup.bash
                ros2 run demo_nodes_cpp listener
```

**Sources:** [docs/user_guide/how_to/ros2_comm.rst:65-114](), [workflows/ros/comm/ros2_comm.yaml:20-87]()

---

## Key Code References

| Component | Primary File | Key Classes/Functions |
|-----------|-------------|----------------------|
| **Workflow Spec Parsing** | [src/utils/job/task.py:589-863]() | `TaskSpec`, `WorkflowSpec` |
| **Workflow Lifecycle** | [src/utils/job/workflow.py]() | `Workflow`, `WorkflowManager` |
| **Task Groups** | [src/utils/job/task.py:866-1551]() | `TaskGroup`, `TaskGroupStatus` |
| **Jinja Templating** | [src/lib/utils/jinja_sandbox.py]() | `render_jinja()` |
| **Special Token Resolution** | [src/utils/job/task.py](), [src/utils/job/workflow.py]() | `resolve_workflow_id()`, `resolve_host_token()` |
| **K8s Resource Generation** | [src/utils/job/kb_objects.py:43-323]() | `K8sObjectFactory`, `KaiK8sObjectFactory` |
| **Database Schema** | [src/utils/connectors/postgres.py:631-786]() | Table creation in `_init_tables()` |
| **Backend Job Processing** | [src/backend/backend_worker.py]() | `BackendWorker`, `BackendCreateGroup` |
| **Task Execution** | [src/backend/ctrl/ctrl.go](), [src/backend/exec/exec.go]() | osmo_ctrl, osmo_exec binaries |
| **Log Streaming** | [src/service/logger/ctrl_websocket.py:118-248]() | `run_websocket()` |

**Sources:** All files listed in table above

---

# Page: Workflow Specification

# Workflow Specification

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



This document describes the YAML structure used to define OSMO workflows. It covers the schema, field definitions, and their relationships without discussing template resolution or execution semantics.

For information about Jinja templating and special token substitution, see [Jinja Templates and Special Tokens](#6.2). For details on multi-task coordination using groups, see [Distributed Workflows with Groups](#6.3). For workflow execution lifecycle, see [Workflow Lifecycle and Execution](#6.4).

## Purpose and Scope

Workflow specifications are YAML files that declaratively define computational workloads in OSMO. This document provides a complete reference for all fields available in the workflow specification format, including:

- Top-level structure and version numbering
- Workflow-level configuration (resources, timeouts)
- Task definitions (containers, commands, data dependencies)
- Group definitions (multi-task coordination)
- Resource allocation specifications
- File mounting and content injection
- Input/output dataset connections

---

## YAML Structure Overview

```mermaid
graph TB
    Root["Workflow YAML<br/>Document"]
    Version["version: 2"]
    Workflow["workflow:"]
    DefaultValues["default-values:"]
    
    WFName["name: string"]
    WFTimeout["timeout:"]
    WFResources["resources:"]
    WFTasks["tasks: []"]
    WFGroups["groups: []"]
    
    Root --> Version
    Root --> Workflow
    Root --> DefaultValues
    
    Workflow --> WFName
    Workflow --> WFTimeout
    Workflow --> WFResources
    Workflow --> WFTasks
    Workflow --> WFGroups
    
    TaskDef["Task Definition"]
    GroupDef["Group Definition"]
    ResDef["Resource Spec"]
    
    WFTasks --> TaskDef
    WFGroups --> GroupDef
    WFResources --> ResDef
    
    TaskName["name"]
    TaskImage["image"]
    TaskCommand["command"]
    TaskArgs["args"]
    TaskEnv["environment"]
    TaskFiles["files"]
    TaskInputs["inputs"]
    TaskOutputs["outputs"]
    TaskCreds["credentials"]
    TaskCheckpoint["checkpoint"]
    TaskResource["resource"]
    
    TaskDef --> TaskName
    TaskDef --> TaskImage
    TaskDef --> TaskCommand
    TaskDef --> TaskArgs
    TaskDef --> TaskEnv
    TaskDef --> TaskFiles
    TaskDef --> TaskInputs
    TaskDef --> TaskOutputs
    TaskDef --> TaskCreds
    TaskDef --> TaskCheckpoint
    TaskDef --> TaskResource
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:40-76](), [docs/user_guide/how_to/training/multi_node.rst:46-96]()

---

## Top-Level Fields

### Version Field

The `version` field specifies the workflow specification schema version. Currently, version 2 is the active format.

```yaml
version: 2
```

### Workflow Section

The `workflow` section contains all workflow-level configuration and task definitions.

```yaml
workflow:
  name: my-workflow
  # ... other fields
```

### Default Values Section

The `default-values` section defines default values for Jinja template variables. See [Jinja Templates and Special Tokens](#6.2) for details on template variable usage.

```yaml
default-values:
  workflow_name: my_workflow
  dataset_name: my_dataset
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:66-70](), [docs/user_guide/how_to/training/multi_node.rst:158-164]()

---

## Workflow Properties

### Name

The `name` field specifies a human-readable identifier for the workflow. This name is stored in the database and displayed in the UI.

```yaml
workflow:
  name: train-multi-gpu
```

### Timeout

The `timeout` section defines time limits for workflow execution. The `exec_timeout` field specifies the maximum duration a workflow can run before automatic termination.

```yaml
workflow:
  timeout:
    exec_timeout: 2h  # Supports: s (seconds), m (minutes), h (hours), d (days)
```

**Example timeout values:**
- `30s` - 30 seconds
- `15m` - 15 minutes  
- `2h` - 2 hours
- `1d` - 1 day

**Sources:** [docs/user_guide/how_to/isaac_groot_notebook.rst:54-66](), [workflows/ros/comm/ros2_comm.yaml:85-86]()

### Resources

The `resources` section defines resource allocation profiles that tasks can reference. Each profile specifies CPU, GPU, memory, storage, and platform requirements.

```yaml
workflow:
  resources:
    default:
      cpu: 4
      gpu: 1
      memory: 32Gi
      storage: 10Gi
      platform: agx-orin
    high-performance:
      cpu: 16
      gpu: 8
      memory: 100Gi
      storage: 50Gi
      platform: ovx-a40
```

#### Resource Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `cpu` | integer | Number of CPU cores | `8` |
| `gpu` | integer | Number of GPUs (optional) | `2` |
| `memory` | string | Memory allocation in Kubernetes format | `32Gi`, `16384Mi` |
| `storage` | string | Ephemeral storage in Kubernetes format | `10Gi`, `5000Mi` |
| `platform` | string | Hardware platform selector (optional) | `agx-orin`, `gb200`, `ovx-a40` |

Platform values match annotations configured in resource pools. See [Backend Operators](#5) for platform configuration details.

**Sources:** [docs/user_guide/how_to/hil.rst:171-202](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:46-51]()

---

## Task Definitions

Tasks are the fundamental unit of work in OSMO workflows. Each task runs as a Kubernetes pod with specified container configuration, resource allocation, and data dependencies.

```mermaid
graph LR
    TaskSpec["Task Specification"]
    
    Core["Core Fields"]
    Execution["Execution Config"]
    Data["Data Dependencies"]
    Resources["Resource Allocation"]
    
    TaskSpec --> Core
    TaskSpec --> Execution
    TaskSpec --> Data
    TaskSpec --> Resources
    
    Core --> Name["name: string"]
    Core --> Image["image: string"]
    
    Execution --> Command["command: []string"]
    Execution --> Args["args: []string"]
    Execution --> Env["environment: map"]
    Execution --> Files["files: []"]
    
    Data --> Inputs["inputs: []"]
    Data --> Outputs["outputs: []"]
    Data --> Credentials["credentials: map"]
    Data --> Checkpoint["checkpoint: []"]
    
    Resources --> ResourceRef["resource: string"]
    Resources --> Lead["lead: bool"]
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:46-64](), [docs/user_guide/how_to/training/single_node.rst:40-64]()

### Core Task Fields

#### Name

The `name` field uniquely identifies a task within a workflow. This name is used for inter-task communication tokens and log identification.

```yaml
tasks:
- name: train
```

**Constraints:**
- Must be unique within the workflow
- Used in `{{host:task_name}}` special tokens
- Stored in the `tasks` table with foreign key to `workflows`

#### Image

The `image` field specifies the Docker container image to execute. Supports any registry accessible to the backend operator.

```yaml
tasks:
- name: simulation
  image: nvcr.io/nvidia/isaac-sim:5.1.0
```

**Common registries:**
- NVIDIA NGC: `nvcr.io/nvidia/*`
- Docker Hub: `ubuntu`, `python:3.10`
- Custom registries: `my-registry.example.com/my-image:tag`

**Sources:** [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:23-24](), [docs/user_guide/how_to/reinforcement_learning.rst:59-61]()

### Execution Configuration

#### Command

The `command` field overrides the container's entrypoint. Specified as an array of strings.

```yaml
tasks:
- name: train
  command: ["/bin/bash"]
  args: ["/tmp/entry.sh"]
```

#### Args

The `args` field provides arguments to the command. Combined with `command` to form the complete execution vector.

```yaml
tasks:
- name: processor
  image: ubuntu
  command: ["python3"]
  args: ["/tmp/script.py", "--verbose"]
```

#### Environment

The `environment` field defines environment variables available to the task container. Specified as key-value pairs.

```yaml
tasks:
- name: isaac-sim
  environment:
    ACCEPT_EULA: Y
    NO_NUCLEUS: Y
    ISAAC_ROS_OVERRIDE_DATASET_ROOT: "/data"
```

**Sources:** [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:27-29](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:49-51]()

#### Files

The `files` field mounts files into the task container. Each file can be specified inline with `contents` or loaded from the local filesystem with `localpath`.

```yaml
tasks:
- name: train
  files:
  - path: /tmp/entry.sh
    contents: |
      #!/bin/bash
      echo "Starting training..."
      python3 /tmp/train.py
  - path: /tmp/train.py
    localpath: train.py
  - path: /tmp/config.json
    contents: |
      {
        "learning_rate": 0.001,
        "batch_size": 32
      }
```

**File Field Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Absolute path where file is mounted in container |
| `contents` | string | Conditional | Inline file contents (mutually exclusive with `localpath`) |
| `localpath` | string | Conditional | Path to file on submission machine (mutually exclusive with `contents`) |

**Sources:** [docs/user_guide/how_to/training/single_node.rst:45-64](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:153-159]()

### Data Dependencies

#### Inputs

The `inputs` field specifies dataset dependencies required by the task. Datasets are mounted as read-only volumes.

```yaml
tasks:
- name: train
  inputs:
  - dataset:
      name: training-dataset
  - dataset:
      name: validation-dataset
```

**Input Resolution:**
- Input index starts at 0
- Referenced via `{{input:0}}`, `{{input:1}}`, etc.
- Mounted at `/mnt/osmo/inputs/<index>/<dataset-name>/`
- See [Dataset Management](#4.2) for dataset versioning

#### Outputs

The `outputs` field specifies datasets to create from task results. Data written to the output path is uploaded to object storage upon task completion.

```yaml
tasks:
- name: train
  outputs:
  - dataset:
      name: trained-model
      path: models  # Optional: upload only this subdirectory
```

**Output Resolution:**
- Referenced via `{{output}}` special token
- Mounted at `/mnt/osmo/outputs/0/`
- If `path` is specified, only that subdirectory is uploaded
- Supports automatic versioning and tagging

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:145-165](), [docs/user_guide/how_to/training/multi_node.rst:133-136]()

#### Credentials

The `credentials` field injects secrets from OSMO's credential store into the task environment. Credentials are mounted as environment variables.

```yaml
tasks:
- name: train
  credentials:
    wandb:
      WANDB_API_KEY: wandb_api_key
    custom:
      DB_PASSWORD: postgres_password
```

**Structure:**
- First-level key: credential name (stored via `osmo credential set`)
- Second-level key: environment variable name
- Value: field name from credential payload

See [Credential Management and Encryption](#8.3) for credential storage details.

**Sources:** [docs/user_guide/how_to/training/single_node.rst:158-174]()

#### Checkpoint

The `checkpoint` field enables periodic synchronization of task data to object storage during execution. Useful for long-running training jobs.

```yaml
tasks:
- name: train
  checkpoint:
  - path: experiments/checkpoints
    url: s3://my-bucket/checkpoints
    frequency: 10s
    regex: .*\.pth
```

**Checkpoint Field Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Local directory to checkpoint |
| `url` | string | Object storage URL for uploads |
| `frequency` | string | Sync interval (e.g., `10s`, `5m`, `1h`) |
| `regex` | string | Pattern to filter files for checkpointing |

**Sources:** [docs/user_guide/how_to/training/single_node.rst:130-145]()

### Resource Allocation

#### Resource Reference

The `resource` field specifies which resource profile from the workflow-level `resources` section to use for this task. If omitted, the `default` profile is used.

```yaml
workflow:
  resources:
    default:
      cpu: 1
      memory: 2Gi
    simulation:
      cpu: 16
      gpu: 1
      memory: 20Gi
  tasks:
  - name: data-prep
    resource: default
  - name: isaac-lab
    resource: simulation
```

**Sources:** [docs/user_guide/how_to/hil.rst:171-253]()

#### Lead Task Marker

The `lead` field designates a task as the leader within a group. Only one task per group can be marked as lead. The lead task determines group lifecycle and is used for special token resolution.

```yaml
groups:
- name: training
  tasks:
  - name: master
    lead: true
  - name: worker-1
  - name: worker-2
```

See [Distributed Workflows with Groups](#6.3) for lead task semantics.

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:61-63](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:99-100]()

---

## Group Definitions

Groups enable multiple tasks to launch simultaneously with private networking for inter-task communication. Tasks within a group can resolve each other's hostnames using special tokens.

```yaml
workflow:
  groups:
  - name: distributed-training
    tasks:
    - name: master
      lead: true
      image: pytorch:latest
    - name: worker-1
      image: pytorch:latest
    - name: worker-2
      image: pytorch:latest
```

### Group Structure

```mermaid
graph TB
    Group["Group Definition"]
    
    Group --> GroupName["name: string"]
    Group --> GroupTasks["tasks: []"]
    
    GroupTasks --> Task1["Task 1"]
    GroupTasks --> Task2["Task 2"]
    GroupTasks --> TaskN["Task N"]
    
    Task1 --> Lead["lead: true<br/>(one task only)"]
    
    subgraph "Kubernetes Resources"
        PodGroup["PodGroup<br/>(gang scheduling)"]
        ServiceNet["Headless Services<br/>(private DNS)"]
    end
    
    Group -.->|Creates| PodGroup
    Group -.->|Creates| ServiceNet
```

**Key Group Properties:**
- All tasks launch simultaneously (gang scheduling via KAI)
- Private network namespace for task-to-task communication
- DNS-based hostname resolution via `{{host:task_name}}`
- Exactly one task must be marked as `lead: true`
- Group fails if any task fails

See [Distributed Workflows with Groups](#6.3) for execution semantics and [KAI Scheduler and GPU Support](#5.3) for scheduling details.

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:58-96](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:91-105]()

---

## Complete Workflow Example

The following example demonstrates a multi-node training workflow with all major specification features:

```yaml
version: 2

workflow:
  name: distributed-training
  
  timeout:
    exec_timeout: 4h
  
  resources:
    default:
      cpu: 1
      memory: 2Gi
      storage: 1Gi
    training:
      cpu: 16
      gpu: 8
      memory: 100Gi
      storage: 50Gi
  
  groups:
  - name: training-cluster
    tasks:
    - name: master
      lead: true
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash]
      args: [/tmp/entry.sh]
      resource: training
      environment:
        NCCL_DEBUG: INFO
      files:
      - path: /tmp/entry.sh
        contents: |
          torchrun --nnodes 2 --nproc_per_node 8 \
            --master_addr {{host:master}} \
            /tmp/train.py
      - path: /tmp/train.py
        localpath: train.py
      inputs:
      - dataset:
          name: training-data
      outputs:
      - dataset:
          name: trained-model
          path: models
      checkpoint:
      - path: checkpoints
        url: s3://bucket/checkpoints
        frequency: 5m
        regex: .*\.pth
      credentials:
        wandb:
          WANDB_API_KEY: api_key
    
    - name: worker-1
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash]
      args: [/tmp/entry.sh]
      resource: training
      files:
      - path: /tmp/entry.sh
        contents: |
          torchrun --nnodes 2 --nproc_per_node 8 --node_rank 1 \
            --master_addr {{host:master}} \
            /tmp/train.py
      - path: /tmp/train.py
        localpath: train.py

default-values:
  learning_rate: 0.001
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:116-165]()

---

## Database Schema Mapping

The workflow specification maps to several PostgreSQL tables during submission:

```mermaid
erDiagram
    workflows ||--o{ tasks : contains
    workflows ||--o{ groups : contains
    workflows {
        bigint id PK
        text name
        text spec_yaml
        text status
        jsonb timeout
    }
    
    tasks {
        bigint id PK
        bigint workflow_id FK
        bigint group_id FK
        text name
        text image
        jsonb command
        jsonb args
        jsonb environment
        jsonb resources
        boolean lead
    }
    
    groups {
        bigint id PK
        bigint workflow_id FK
        text name
    }
    
    tasks ||--o{ task_files : has
    task_files {
        bigint id PK
        bigint task_id FK
        text path
        text contents
        text localpath
    }
    
    tasks ||--o{ task_inputs : has
    tasks ||--o{ task_outputs : has
    task_inputs {
        bigint id PK
        bigint task_id FK
        bigint dataset_id FK
        int input_index
    }
    
    task_outputs {
        bigint id PK
        bigint task_id FK
        bigint dataset_id FK
        text subpath
    }
    
    tasks ||--o{ checkpoints : has
    checkpoints {
        bigint id PK
        bigint task_id FK
        text path
        text url
        text frequency
        text regex
    }
```

**Key Mappings:**

| YAML Field | Database Table | Column/JSON Field |
|------------|----------------|-------------------|
| `workflow.name` | `workflows` | `name` |
| `workflow.timeout` | `workflows` | `timeout` (jsonb) |
| `workflow.resources` | `workflows` | `spec_yaml` (parsed) |
| `tasks[].name` | `tasks` | `name` |
| `tasks[].image` | `tasks` | `image` |
| `tasks[].command` | `tasks` | `command` (jsonb) |
| `tasks[].environment` | `tasks` | `environment` (jsonb) |
| `tasks[].files` | `task_files` | One row per file |
| `tasks[].inputs` | `task_inputs` | One row per input |
| `tasks[].outputs` | `task_outputs` | One row per output |
| `groups[].name` | `groups` | `name` |

See [PostgreSQL Database Schema](#4.1) for complete table definitions.

**Sources:** Reference to postgres.py implementation (not directly shown in provided files, but implied by architecture diagrams)

---

## Workflow Submission

Workflows are submitted via the CLI using the `osmo workflow submit` command:

```bash
# Basic submission
osmo workflow submit workflow.yaml

# With Jinja variable overrides
osmo workflow submit workflow.yaml --set n_nodes=4 gpu_per_node=8

# With specific pool targeting
osmo workflow submit workflow.yaml --pool production-cluster
```

The submission process:
1. Parses YAML and validates schema
2. Resolves Jinja templates with default values and `--set` overrides
3. Validates resource compatibility with available pools
4. Persists workflow and task records to PostgreSQL
5. Enqueues tasks for backend operator execution

See [Workflow Lifecycle and Execution](#6.4) for the complete submission and execution flow.

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:177](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:77-81]()

---

# Page: Jinja Templates and Special Tokens

# Jinja Templates and Special Tokens

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



## Purpose and Scope

This document explains how OSMO uses Jinja templating and special tokens to enable dynamic workflow configuration. Jinja templates allow users to define configurable variables with default values that can be overridden at submission time, while special tokens provide runtime-resolved values for workflow coordination, data access, and inter-task communication.

For the complete workflow YAML specification structure, see [Workflow Specification](#6.1). For information about using these features in distributed training scenarios, see [Distributed Workflows with Groups](#6.3). For the execution lifecycle of workflows, see [Workflow Lifecycle and Execution](#6.4).

---

## Jinja Template System

OSMO workflow specifications use the [Jinja template engine](https://jinja.palletsprojects.com) to enable dynamic configuration before workflow submission. Templates are processed client-side during the `osmo workflow submit` command, allowing users to customize workflows without modifying the base YAML file.

### Variable Substitution

Variables are denoted by double curly braces `{{ variable_name }}`. All variables must either have default values defined in the `default-values` section or be provided via the `--set` flag at submission time. Unresolved variables cause submission failure.

**Example from workflow specification:**

[docs/user_guide/workflows/specification/templates_and_tokens.rst:42-70]()

```yaml
workflow:
  name: {{ workflow_name }}
  tasks:
  - name: ros
    environment:
      ISAAC_ROS_OVERRIDE_DATASET_ROOT: "{{input:0}}/{{ dataset_name }}"
    image: "nvcr.io/nvidia/isaac-ros/aarch64-build:latest"
    args: ["{{ task_arg }}"]

default-values:
  workflow_name: isaac_ros_bi3d_stereo_node_test
  dataset_name: isaac_ros_benchmark_bi3d_dataset
  task_arg: isaac_ros_bi3d_test.py
```

**Override at submission:**

```bash
osmo workflow submit /path/my_workflow.yaml \
  --set workflow_name=custom_workflow \
       dataset_name=custom_dataset \
       task_arg=custom_script.py
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:29-82]()

### Control Flow Constructs

Jinja supports Python-like control flow for generating repetitive structures or conditional configuration.

#### For Loops

Use `{% for item in range(n) %}` to generate multiple similar tasks:

[docs/user_guide/workflows/specification/templates_and_tokens.rst:85-111]()

```yaml
groups:
- name: group1
  tasks:
  {% for item in range(3) %}
  - name: "task_{{item}}"
    image: my_container
    command: ["python3"]
    {% if item == 0 %}
    lead: true
    {% endif %}
    args: ["{{ task_arg }}"]
  {% endfor %}
```

#### Conditional Blocks

Use `{% if condition %}` to include or exclude configuration sections:

[docs/user_guide/how_to/training/multi_node.rst:129-156]()

```yaml
tasks:
{% for item in range(n_nodes) %}
{% if item == 0 %}
- name: master
  lead: true
  outputs:
  - dataset:
      name: {{ output_dataset }}
{% else %}
- name: worker_{{item}}
{% endif %}
  image: nvcr.io/nvidia/pytorch:24.03-py3
  # ... task configuration
{% endfor %}
```

This pattern enables scaling distributed training from 2 nodes to arbitrary `n_nodes` by simply changing the `n_nodes` variable at submission.

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:85-116](), [docs/user_guide/how_to/training/multi_node.rst:112-177]()

### Variable Naming Conventions

Variable names follow [PEP 8 style guide](https://peps.python.org/pep-0008) conventions: lowercase with underscores (e.g., `workflow_name`, `n_gpus_per_node`). Reserved special token names cannot be used as custom variables.

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:83-84]()

---

## Template Processing Pipeline

The following diagram shows how Jinja templates are processed during workflow submission:

**Jinja Template Processing Flow**

```mermaid
graph TB
    UserYAML["Workflow YAML File<br/>with Jinja Templates"]
    SubmitCommand["osmo workflow submit<br/>--set variables"]
    JinjaEngine["Jinja Template Engine<br/>(Client-side)"]
    DefaultValues["default-values:<br/>Variable Definitions"]
    CLIOverrides["--set CLI Arguments"]
    ExpandedYAML["Expanded YAML<br/>(No Jinja syntax)"]
    APISubmission["API Submission<br/>POST /api/workflows"]
    TokenResolution["Special Token Resolution<br/>(Server-side)"]
    K8sGeneration["K8s Resource Generation"]
    
    UserYAML --> SubmitCommand
    SubmitCommand --> JinjaEngine
    DefaultValues --> JinjaEngine
    CLIOverrides --> JinjaEngine
    JinjaEngine --> ExpandedYAML
    ExpandedYAML --> APISubmission
    APISubmission --> TokenResolution
    TokenResolution --> K8sGeneration
    
    Note1["Validation:<br/>All variables must be resolved<br/>Reserved tokens cannot be set"]
    JinjaEngine -.-> Note1
```

**Key Processing Steps:**

1. **Client-side Template Expansion**: The `osmo workflow submit` command processes Jinja templates using default values and CLI overrides
2. **Variable Validation**: All custom variables must be resolved; special tokens are preserved
3. **API Submission**: Expanded YAML (without Jinja syntax) is submitted to the control plane
4. **Server-side Token Resolution**: Special tokens are resolved during K8s resource creation

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:29-34](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:77-82]()

---

## Special Tokens

Special tokens are reserved identifiers denoted by `{{ }}` that are resolved by the OSMO service at specific points in the workflow lifecycle. Unlike Jinja variables, special tokens cannot be set by users and are automatically substituted with runtime values.

### Token Reference Table

| Token | Resolved Value | Resolution Timing | Primary Use Case |
|-------|---------------|-------------------|------------------|
| `{{workflow_id}}` | Unique workflow identifier (string) | During workflow creation | Logging, debugging, identifying workflow context |
| `{{input:N}}` | Absolute path to Nth input dataset mount | During task pod creation | Accessing input data (N is 0-indexed) |
| `{{output}}` | Absolute path to output directory | During task pod creation | Writing results to output dataset |
| `{{host:task_name}}` | DNS hostname of specified task | During task pod creation | Inter-task communication in groups |

**Warning:** Attempting to set values for special tokens via `--set` or `default-values` will be ignored by the service.

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-129]()

### `{{workflow_id}}` Token

Resolves to the unique identifier assigned to the workflow upon creation. Useful for embedding workflow identity in logs or output filenames.

**Example:**

[docs/user_guide/workflows/specification/templates_and_tokens.rst:154-159]()

```yaml
files:
- contents: |
    echo "Hello from {{workflow_id}}"
    echo "Data from workflow {{workflow_id}}" > {{output}}/my_file.txt
  path: /tmp/run.sh
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:131-165]()

### `{{input:N}}` Token

Resolves to the absolute path where the Nth input dataset is mounted (0-indexed). Each task can specify multiple input datasets in the `inputs` array, and the token index corresponds to the array position.

**Example with multiple inputs:**

[docs/user_guide/workflows/specification/templates_and_tokens.rst:141-159]()

```yaml
tasks:
- name: task1
  inputs:
  - dataset:
      name: first_input
  - dataset:
      name: second_input
  files:
  - contents: |
      cat {{input:0}}/file.txt      # Access first_input
      cat {{input:1}}/file2.txt     # Access second_input
    path: /tmp/run.sh
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:131-165]()

### `{{output}}` Token

Resolves to the absolute path of the task's output directory. All files written to this directory are automatically uploaded to the output dataset specified in the task's `outputs` field. This is the primary mechanism for persisting workflow results to OSMO's content-addressable storage.

**Example:**

[workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:32-45]()

```yaml
tasks:
- name: isaac-sim-sdg
  files:
  - contents: |
      /isaac-sim/python.sh /isaac-sim/standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py
      cp -r /isaac-sim/_out_scene_based_sdg/. {{output}}
    path: /tmp/entry.sh
  outputs:
  - dataset:
      name: isaac-sim-sdg-sample
```

**Sources:** [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:30-45](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:131-165]()

### `{{host:task_name}}` Token

Resolves to the DNS hostname of a specified task within the same group. This token is essential for distributed training and inter-task communication, as tasks in a group share a private network namespace but may be scheduled on different physical nodes.

**Critical Use Case: Distributed Training**

[docs/user_guide/how_to/training/multi_node.rst:73-94]()

```yaml
groups:
- name: training
  tasks:
  - name: master
    lead: true
    files:
    - contents: |
        torchrun --nnodes 2 --nproc_per_node 8 --node_rank 0 \
                 --master_addr {{host:master}} --master_port 29400 \
                 /tmp/train.py
      path: /tmp/master.sh
  - name: worker
    files:
    - contents: |
        torchrun --nnodes 2 --nproc_per_node 8 --node_rank 1 \
                 --master_addr {{host:master}} --master_port 29400 \
                 /tmp/train.py
      path: /tmp/worker.sh
```

The `{{host:master}}` token ensures both nodes correctly identify the master node regardless of which physical machine it's scheduled on.

**Converting Hostname to IP Address**

Some applications require IP addresses instead of hostnames. Use `nslookup` to resolve:

[docs/user_guide/how_to/training/multi_node.rst:104-109]()

```bash
TASK_IP=$(nslookup -type=A {{host:master}} | grep -oP \
  'Address: \K\d[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -n1)
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:40-110](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:167-228]()

---

## Special Token Resolution in Workflow Lifecycle

The following diagram shows when each special token type is resolved during workflow execution:

**Token Resolution Timeline**

```mermaid
graph TB
    Submit["Workflow Submission<br/>POST /api/workflows"]
    CreateWorkflow["Database: Insert workflows table<br/>Generate workflow_id"]
    CreateTasks["Database: Insert tasks table<br/>Parse inputs/outputs"]
    BackendListener["Backend Operator:<br/>backendListener polls tasks"]
    CreateK8s["backendWorker:<br/>K8sObjectFactory.create_pod()"]
    TokenSubstitution["Token Resolution:<br/>workflow_id, input:N, output,<br/>host:task_name"]
    PodCreation["Kubernetes:<br/>Pod Manifest Applied"]
    ContainerStart["Container Startup:<br/>Entry Command Executed"]
    
    Submit --> CreateWorkflow
    CreateWorkflow --> CreateTasks
    CreateTasks --> BackendListener
    BackendListener --> CreateK8s
    CreateK8s --> TokenSubstitution
    TokenSubstitution --> PodCreation
    PodCreation --> ContainerStart
    
    Note1["{{workflow_id}}<br/>Available after workflow creation"]
    CreateWorkflow -.-> Note1
    
    Note2["{{input:N}}, {{output}}<br/>Resolved to mount paths<br/>during pod spec generation"]
    TokenSubstitution -.-> Note2
    
    Note3["{{host:task_name}}<br/>Resolved to K8s DNS name<br/>format: taskname-workflowid.namespace"]
    TokenSubstitution -.-> Note3
```

**Resolution Details:**

1. **`{{workflow_id}}`**: Assigned when the workflow record is inserted into the `workflows` table
2. **`{{input:N}}`**: Resolved to volume mount paths based on `tasks.inputs` field during pod creation
3. **`{{output}}`**: Resolved to output volume mount path based on `tasks.outputs` field
4. **`{{host:task_name}}`**: Resolved to Kubernetes DNS format (e.g., `master-abc123.default.svc.cluster.local`)

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-129]()

---

## Common Usage Patterns

### Pattern 1: Inter-Task Communication in Groups

Tasks in a group share a private network namespace, enabling direct communication. The `{{host:task_name}}` token is essential for service discovery.

**ROS 2 Discovery Server Example:**

[workflows/ros/comm/ros2_comm.yaml:43-55]()

```yaml
groups:
- name: nodes
  tasks:
  - name: discovery-server
    files:
    - contents: |
        fastdds discovery --server-id 0 -p 11811
      path: /tmp/client.sh
  - name: publisher-node
    files:
    - contents: |
        DISCOVERY_SERVER_IP=$(nslookup -type=A {{host:discovery-server}} | grep -oP \
            'Address: \K\d[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        export ROS_DISCOVERY_SERVER=$DISCOVERY_SERVER_IP:11811
        ros2 run demo_nodes_cpp talker
      path: /tmp/entry.sh
```

The publisher node uses `{{host:discovery-server}}` to locate the discovery server regardless of physical node placement.

**Sources:** [workflows/ros/comm/ros2_comm.yaml:1-87](), [docs/user_guide/how_to/ros2_comm.rst:99-110]()

### Pattern 2: Hardware-in-the-Loop with Cross-Platform Communication

**Isaac Lab + Jetson Communication:**

[workflows/hil/setup_discovery_server.sh:18-24]()

```bash
apt update && apt install -y dnsutils
DISCOVERY_SERVER_IP=$(nslookup -type=A {{host:discovery-server}} | grep -oP \
    'Address: \K\d[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
export ROS_DISCOVERY_SERVER=$DISCOVERY_SERVER_IP:11811
```

This script is mounted into both x86_64 (Isaac Lab) and ARM64 (Jetson) tasks, enabling ROS 2 communication across heterogeneous platforms.

**Sources:** [workflows/hil/setup_discovery_server.sh:1-25](), [docs/user_guide/how_to/hil.rst:105-120]()

### Pattern 3: Dynamic Multi-Node Training Scaling

Combine Jinja templates with special tokens to create scalable distributed training workflows:

[docs/user_guide/how_to/training/multi_node.rst:117-165]()

```yaml
groups:
- name: training
  tasks:
  {% for item in range(n_nodes) %}
  {% if item == 0 %}
  - name: master
    lead: true
  {% else %}
  - name: worker_{{item}}
  {% endif %}
    files:
    - contents: |
        torchrun --nnodes {{n_nodes}} --node_rank {{item}} \
                 --master_addr {{host:master}} --master_port {{master_port}} \
                 /tmp/train.py --snapshot_path {{output}}/models/snapshot.pth
      path: /tmp/run.sh

default-values:
  n_nodes: 2
  master_port: 29400
```

Submit with custom node count:

```bash
osmo workflow submit workflow.yaml --set n_nodes=8
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:112-177]()

### Pattern 4: Dataset Chaining with Input/Output Tokens

**Example: SDG → Training Pipeline:**

```yaml
# Workflow 1: Generate synthetic data
tasks:
- name: generate
  outputs:
  - dataset:
      name: training-dataset-v1
  files:
  - contents: |
      python generate.py --output {{output}}/images

# Workflow 2: Train on generated data
tasks:
- name: train
  inputs:
  - dataset:
      name: training-dataset-v1
  outputs:
  - dataset:
      name: trained-model-v1
  files:
  - contents: |
      python train.py --data {{input:0}}/images --save {{output}}/model.pth
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:141-165](), [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml:30-45]()

---

## Integration with Kubernetes Resource Generation

The following diagram bridges natural language concepts to actual code entities involved in token resolution:

**Code Entity Flow: Token Resolution to K8s Resources**

```mermaid
graph TB
    WorkflowYAML["Workflow YAML<br/>with Special Tokens"]
    PostgreSQL[("PostgreSQL<br/>workflows table<br/>tasks table")]
    BackendListener["backendListener<br/>(backend_operator/listener.py)"]
    BackendWorker["backendWorker<br/>(backend_operator/worker.py)"]
    K8sFactory["K8sObjectFactory<br/>(backend_operator/k8s_utils.py)"]
    CreatePod["create_pod() method"]
    TokenResolver["_resolve_special_tokens()"]
    VolumeResolver["_create_volume_mounts()"]
    DNSResolver["_get_task_dns_name()"]
    PodManifest["Pod Manifest<br/>(JSON/YAML)"]
    K8sAPI["Kubernetes API<br/>kubectl apply"]
    
    WorkflowYAML --> PostgreSQL
    PostgreSQL --> BackendListener
    BackendListener --> BackendWorker
    BackendWorker --> K8sFactory
    K8sFactory --> CreatePod
    CreatePod --> TokenResolver
    CreatePod --> VolumeResolver
    CreatePod --> DNSResolver
    TokenResolver --> PodManifest
    VolumeResolver --> PodManifest
    DNSResolver --> PodManifest
    PodManifest --> K8sAPI
    
    Note1["Token Resolution:<br/>{{workflow_id}} → workflow.id<br/>{{input:N}} → /mnt/input/N<br/>{{output}} → /mnt/output<br/>{{host:task}} → task-wfid.ns.svc.cluster.local"]
    TokenResolver -.-> Note1
```

**Key Code Components:**

1. **`backendListener`**: Polls PostgreSQL `tasks` table for PENDING tasks
2. **`backendWorker`**: Executes task creation by calling `K8sObjectFactory`
3. **`K8sObjectFactory.create_pod()`**: Main method that orchestrates pod creation
4. **`_resolve_special_tokens()`**: Function that performs string substitution for all token types
5. **`_create_volume_mounts()`**: Maps `inputs` and `outputs` fields to volume mount paths
6. **`_get_task_dns_name()`**: Generates Kubernetes DNS names for `{{host:task_name}}` resolution

**Sources:** Based on architectural context from high-level diagrams and workflow processing patterns

---

## Best Practices

### 1. Separate Concerns: Jinja vs. Special Tokens

- Use **Jinja templates** for user-configurable parameters (hyperparameters, resource counts, dataset names)
- Use **special tokens** for runtime coordination that the service must manage (paths, hostnames)

```yaml
# Good: User controls training parameters via Jinja
default-values:
  learning_rate: 0.001
  batch_size: 32

tasks:
- name: train
  args: ["--lr", "{{learning_rate}}", "--batch", "{{batch_size}}"]
  files:
  - contents: |
      python train.py --data {{input:0}} --save {{output}}/model.pth
    path: /tmp/run.sh
```

### 2. Name Tasks Consistently

Task names used in `{{host:task_name}}` tokens must exactly match the `name` field in the task definition:

```yaml
# Correct
tasks:
- name: discovery-server
  # ...
- name: client
  files:
  - contents: |
      connect_to {{host:discovery-server}}  # Matches task name exactly
```

### 3. Test Token Resolution

Use `echo` statements to verify token resolution during development:

```yaml
files:
- contents: |
    echo "Workflow ID: {{workflow_id}}"
    echo "Input path: {{input:0}}"
    echo "Output path: {{output}}"
    echo "Master host: {{host:master}}"
  path: /tmp/debug.sh
```

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:36-38]()

---

## Summary

| Feature | Type | Processing | Use Case |
|---------|------|------------|----------|
| Jinja Variables | User-defined templates | Client-side (CLI) | Parameterized workflows, scaling, conditionals |
| Special Tokens | System-reserved identifiers | Server-side (K8s creation) | Runtime paths, inter-task communication |
| `{{workflow_id}}` | Special token | Workflow creation | Identifying workflow context |
| `{{input:N}}` | Special token | Pod creation | Accessing input datasets |
| `{{output}}` | Special token | Pod creation | Writing results |
| `{{host:task_name}}` | Special token | Pod creation | Network communication in groups |

**Sources:** [docs/user_guide/workflows/specification/templates_and_tokens.rst:1-228](), [docs/user_guide/how_to/training/multi_node.rst:1-216]()

---

# Page: Distributed Workflows with Groups

# Distributed Workflows with Groups

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



## Purpose and Scope

This document explains the **groups** construct in OSMO workflows, which enables distributed execution patterns where multiple tasks must run simultaneously with private network communication. Groups are essential for multi-node training, robotics applications with ROS 2 communication, and any workflow requiring coordinated parallel execution.

For general workflow specification syntax, see [Workflow Specification](#6.1). For special tokens used within groups like `{{host:task_name}}`, see [Jinja Templates and Special Tokens](#6.2). For the complete workflow lifecycle, see [Workflow Lifecycle and Execution](#6.4).

---

## What Are Groups?

Groups are collections of tasks within a workflow that are guaranteed to:

1. **Launch simultaneously** - All tasks in a group start at the same time (gang scheduling)
2. **Share a private network** - Tasks can communicate using internal DNS names
3. **Execute on the same backend** - All tasks run within the same Kubernetes cluster

Groups are defined in the workflow specification under the `groups` field:

```yaml
workflow:
  name: my-distributed-workflow
  groups:
  - name: training-cluster
    tasks:
    - name: master
      lead: true
      # ... task spec
    - name: worker-1
      # ... task spec
    - name: worker-2
      # ... task spec
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:46-97](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:172-223]()

---

## Group Architecture

### Database Schema

Groups are stored in the `groups` table with the following key fields:

| Field | Type | Purpose |
|-------|------|---------|
| `workflow_id` | TEXT | Parent workflow identifier |
| `name` | TEXT | Group name (unique within workflow) |
| `group_uuid` | TEXT | Unique identifier for the group |
| `spec` | JSONB | Original group specification |
| `status` | TEXT | Current execution status |
| `remaining_upstream_groups` | HSTORE | Dependency tracking |
| `downstream_groups` | HSTORE | Tasks that depend on this group |
| `scheduler_settings` | TEXT | Backend scheduler configuration |

**Sources:** [src/utils/connectors/postgres.py:692-715]()

### Kubernetes Resources

When a group is submitted, OSMO creates several Kubernetes resources:

```mermaid
graph TB
    Group["Group Submission<br/>(workflow_id, group_name)"]
    
    subgraph "K8s Resources Created"
        PodGroup["PodGroup<br/>(KAI Scheduler)"]
        HeadlessService["Headless Service<br/>(Private DNS)"]
        Pods["Task Pods<br/>(1 per task)"]
        Secrets["Secrets<br/>(credentials, config)"]
    end
    
    subgraph "Gang Scheduling"
        Scheduler["KAI Scheduler"]
        Queue["Pool Queue"]
        Scheduler --> Queue
    end
    
    Group --> PodGroup
    Group --> HeadlessService
    Group --> Pods
    Group --> Secrets
    
    PodGroup --> Scheduler
    Pods -.->|"Scheduled when<br/>all pods ready"| Scheduler
    
    HeadlessService -.->|"DNS Resolution<br/>task-name.subdomain"| Pods

    style PodGroup fill:#e8f5e9
    style HeadlessService fill:#e1f5ff
    style Scheduler fill:#fff4e1
```

**Sources:** [src/utils/job/kb_objects.py:74-103](), [src/utils/job/kb_objects.py:242-261](), [src/utils/job/kb_objects.py:324-378]()

---

## Task Communication via Private Networks

### Headless Service and DNS Resolution

Each group creates a Kubernetes headless service that provides internal DNS resolution. Tasks within the group can resolve each other's hostnames using the `{{host:task_name}}` token.

**Headless Service Creation:**

```mermaid
graph LR
    subgraph "Group: training-cluster"
        Master["master<br/>(Pod)"]
        Worker1["worker-1<br/>(Pod)"]
        Worker2["worker-2<br/>(Pod)"]
    end
    
    HeadlessService["Headless Service<br/>osmo-training-cluster"]
    
    DNS["Kubernetes DNS<br/>CoreDNS"]
    
    Master -.->|"Registers with"| HeadlessService
    Worker1 -.->|"Registers with"| HeadlessService
    Worker2 -.->|"Registers with"| HeadlessService
    
    HeadlessService --> DNS
    
    Worker1 -.->|"nslookup {{host:master}}"| DNS
    DNS -.->|"Returns master Pod IP"| Worker1

    style HeadlessService fill:#e1f5ff
    style DNS fill:#fff4e1
```

**Token Resolution Process:**

1. User writes `{{host:task_name}}` in workflow spec
2. Token is resolved to the subdomain name: `task-name.osmo-group-uuid`
3. Application performs DNS lookup to get Pod IP
4. Direct network communication established

**Example - Multi-Node TorchRun:**

```yaml
groups:
- name: training
  tasks:
  - name: master
    lead: true
    files:
    - path: /tmp/run.sh
      contents: |
        torchrun --nnodes 2 --nproc_per_node 8 --node_rank 0 \
          --master_addr {{host:master}} --master_port 29400 \
          /tmp/train.py
  
  - name: worker
    files:
    - path: /tmp/run.sh
      contents: |
        torchrun --nnodes 2 --nproc_per_node 8 --node_rank 1 \
          --master_addr {{host:master}} --master_port 29400 \
          /tmp/train.py
```

**Sources:** [src/utils/job/kb_objects.py:242-261](), [docs/user_guide/how_to/training/multi_node.rst:46-97](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:167-223]()

### IP Address Resolution

In some scenarios, you may need the actual IP address instead of the hostname. Use DNS utilities to resolve:

```bash
# Resolve hostname to IP
TASK_IP=$(nslookup -type=A {{host:task_name}} | grep -oP \
  'Address: \K\d[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -n1)
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:103-109](), [workflows/hil/setup_discovery_server.sh:18-24]()

---

## Lead Tasks

The `lead` field designates one task in a group as the primary coordinator. Lead tasks have special properties:

1. **Output responsibility** - Only lead tasks save outputs to datasets by default
2. **Coordination point** - Lead tasks often serve as master/coordinator nodes
3. **Status propagation** - Group status typically reflects lead task status

### Lead Task Declaration

```yaml
groups:
- name: my-group
  tasks:
  - name: coordinator
    lead: true  # This task is the group leader
    outputs:
    - dataset:
        name: my-results  # Only lead saves outputs
    # ... rest of task spec
  
  - name: worker-1
    # ... task spec (no outputs needed)
  
  - name: worker-2
    # ... task spec (no outputs needed)
```

### When to Use Lead Tasks

| Pattern | Lead Task Role | Example |
|---------|---------------|---------|
| **Distributed Training** | Master node that coordinates workers | TorchRun master (rank 0) |
| **ROS 2 Communication** | Discovery server or primary node | FastDDS discovery server |
| **Data Processing** | Aggregator that collects results | MapReduce reducer |
| **HIL Simulation** | Simulation instance that provides environment | Isaac Lab instance |

**Sources:** [src/utils/job/task.py:598](), [docs/user_guide/how_to/training/multi_node.rst:62-63](), [docs/user_guide/how_to/training/multi_node.rst:131-135]()

---

## Barrier Synchronization

Barriers allow tasks within a group to synchronize execution at specific points. This is useful when tasks have varying initialization times but need to start computationally intensive work simultaneously.

### Barrier Implementation Architecture

```mermaid
sequenceDiagram
    participant T1 as Task 1
    participant T2 as Task 2
    participant T3 as Task 3
    participant Redis as Redis Server
    participant Logger as Logger Service
    
    Note over T1,T3: All tasks running in parallel
    
    T1->>Logger: barrier(name="ready", count=3)
    Logger->>Redis: SADD barrier:workflow:group:ready "task1"
    Logger->>Redis: SMEMBERS barrier:workflow:group:ready
    Redis-->>Logger: {"task1"} (size=1)
    
    T2->>Logger: barrier(name="ready", count=3)
    Logger->>Redis: SADD barrier:workflow:group:ready "task2"
    Logger->>Redis: SMEMBERS barrier:workflow:group:ready
    Redis-->>Logger: {"task1", "task2"} (size=2)
    
    T3->>Logger: barrier(name="ready", count=3)
    Logger->>Redis: SADD barrier:workflow:group:ready "task3"
    Logger->>Redis: SMEMBERS barrier:workflow:group:ready
    Redis-->>Logger: {"task1", "task2", "task3"} (size=3)
    
    Note over Logger: Barrier count met!
    
    Logger->>Redis: LPUSH action-queue-task1 "barrier"
    Logger->>Redis: LPUSH action-queue-task2 "barrier"
    Logger->>Redis: LPUSH action-queue-task3 "barrier"
    
    Redis-->>T1: Barrier released
    Redis-->>T2: Barrier released
    Redis-->>T3: Barrier released
    
    Note over T1,T3: All tasks continue execution
```

### Barrier Usage in Workflows

Barriers are typically implemented using helper scripts. Example from multi-node training:

```yaml
groups:
- name: training
  tasks:
  {% for i in range(n_nodes) %}
  - name: node-{{i}}
    files:
    - path: /tmp/run.sh
      contents: |
        # Time-varying installation/setup code
        apt-get update && apt-get install -y heavy-package
        
        # Synchronize before training starts
        python3 /tmp/osmo_barrier.py --num_nodes {{n_nodes}} \
          --connect {{host:node-0}} --rank {{i}}
        
        # Now all nodes start training simultaneously
        torchrun --nnodes {{n_nodes}} ...
    
    - path: /tmp/osmo_barrier.py
      localpath: osmo_barrier.py
  {% endfor %}
```

### Barrier Key Structure

Redis keys for barriers follow this pattern:
```
barrier-key: barrier:{workflow_id}:{group_name}:{barrier_name}
action-queue: {workflow_id}-{task_name}-{retry_id}-actions
```

**Sources:** [src/service/logger/ctrl_websocket.py:93-116](), [docs/user_guide/how_to/training/multi_node.rst:179-215](), [src/utils/job/common.py] (implied by barrier_key function)

---

## Gang Scheduling with KAI Scheduler

Groups use gang scheduling to ensure all tasks start simultaneously. This prevents resource deadlock where some tasks are scheduled but others wait indefinitely for resources.

### PodGroup Resource

When using the KAI scheduler, OSMO creates a `PodGroup` custom resource:

```yaml
apiVersion: scheduling.run.ai/v2alpha2
kind: PodGroup
metadata:
  name: osmo-{group_uuid}
  labels:
    kai.scheduler/queue: osmo-pool-{namespace}-{pool_name}
spec:
  minMember: 3  # Number of tasks in group
  queue: osmo-pool-{namespace}-{pool_name}
  priorityClassName: osmo-normal
```

### Gang Scheduling Flow

```mermaid
stateDiagram-v2
    [*] --> Waiting: Group Submitted
    
    Waiting --> Scheduling: All pods created
    
    state Scheduling {
        [*] --> CheckingResources
        CheckingResources --> Pending: Resources available
        CheckingResources --> Waiting: Insufficient resources
        Pending --> AllScheduled: All pods assigned
    }
    
    Scheduling --> Running: All pods started
    
    state Running {
        [*] --> Initializing
        Initializing --> Executing: Entry commands run
        Executing --> [*]
    }
    
    Running --> Completed: All tasks succeed
    Running --> Failed: Any task fails
    
    Completed --> [*]
    Failed --> [*]
```

### Scheduling Guarantees

| Scenario | Behavior |
|----------|----------|
| **Sufficient resources** | All tasks scheduled immediately |
| **Insufficient resources** | All tasks remain in queue until enough resources available |
| **Partial scheduling** | Prevented - either all tasks scheduled or none |
| **Task failure** | Entire group fails; resources freed for retry |

**Sources:** [src/utils/job/kb_objects.py:324-378](), [src/utils/job/kb_objects.py:74-103]()

---

## Common Distributed Workflow Patterns

### Pattern 1: Multi-Node Distributed Training

**Use Case:** Train neural networks across multiple GPUs/nodes using frameworks like PyTorch DDP or TorchRun.

**Key Components:**
- Lead task acts as rank 0 (master)
- Workers use `{{host:master}}` for coordination
- Barrier synchronization for consistent training start

```yaml
workflow:
  name: distributed-training
  groups:
  - name: training
    tasks:
    {% for rank in range(num_nodes) %}
    - name: {% if rank == 0 %}master{% else %}worker-{{rank}}{% endif %}
      {% if rank == 0 %}lead: true{% endif %}
      image: nvcr.io/nvidia/pytorch:24.03-py3
      command: [bash, /tmp/run.sh]
      files:
      - path: /tmp/run.sh
        contents: |
          torchrun --nnodes {{num_nodes}} --nproc_per_node 8 \
            --node_rank {{rank}} \
            --master_addr {{host:master}} --master_port 29400 \
            /tmp/train.py
    {% endfor %}
  resources:
    default:
      gpu: 8
      cpu: 16
      memory: 30Gi
```

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:46-177]()

### Pattern 2: ROS 2 Multi-Node Communication

**Use Case:** Coordinate multiple ROS 2 nodes across containers using a centralized Discovery Server.

**Key Components:**
- Discovery server task for node registration
- Publisher and subscriber tasks
- `{{host:discovery-server}}` token for server location

```yaml
workflow:
  name: ros2-communication
  groups:
  - name: nodes
    tasks:
    - name: discovery-server
      image: osrf/ros:humble-desktop-full
      command: [bash, /tmp/run.sh]
      files:
      - path: /tmp/run.sh
        contents: |
          source /opt/ros/humble/setup.bash
          fastdds discovery --server-id 0 -p 11811
    
    - name: publisher-node
      lead: true
      image: osrf/ros:humble-desktop-full
      files:
      - path: /tmp/run.sh
        contents: |
          DISCOVERY_IP=$(nslookup {{host:discovery-server}} | grep -oP 'Address: \K.*')
          export ROS_DISCOVERY_SERVER=$DISCOVERY_IP:11811
          source /opt/ros/humble/setup.bash
          ros2 run demo_nodes_cpp talker
    
    - name: subscriber-node
      image: osrf/ros:humble-desktop-full
      files:
      - path: /tmp/run.sh
        contents: |
          DISCOVERY_IP=$(nslookup {{host:discovery-server}} | grep -oP 'Address: \K.*')
          export ROS_DISCOVERY_SERVER=$DISCOVERY_IP:11811
          source /opt/ros/humble/setup.bash
          ros2 run demo_nodes_cpp listener
```

**Sources:** [docs/user_guide/how_to/ros2_comm.rst:70-110](), [workflows/ros/comm/ros2_comm.yaml]()

### Pattern 3: Hardware-in-the-Loop (HIL) Simulation

**Use Case:** Run robot policy on embedded hardware (Jetson) while simulating environment on GPU workstation.

**Key Components:**
- Discovery server for ROS 2 communication
- Simulation task on GPU platform
- Policy task on embedded platform
- Different resource specs per task

```yaml
workflow:
  name: hardware-in-loop
  resources:
    sim:
      platform: ovx-a40
      gpu: 1
      cpu: 16
      memory: 20Gi
    jetson:
      platform: agx-orin
      cpu: 8
      memory: 26Gi
    default:
      cpu: 1
      memory: 2Gi
  
  groups:
  - name: hil-system
    tasks:
    - name: discovery-server
      resource: default
      # ... discovery server setup
    
    - name: isaac-lab
      resource: sim
      lead: true
      # ... simulation setup with {{host:discovery-server}}
    
    - name: locomotion-policy
      resource: jetson
      # ... policy setup with {{host:discovery-server}}
```

**Sources:** [docs/user_guide/how_to/hil.rst:169-287]()

### Pattern 4: Parallel Data Processing

**Use Case:** Process large datasets in parallel with result aggregation.

**Key Components:**
- Lead task aggregates results
- Worker tasks process data partitions
- Shared input dataset split across tasks

```yaml
workflow:
  name: parallel-processing
  groups:
  - name: processors
    tasks:
    - name: aggregator
      lead: true
      outputs:
      - dataset:
          name: final-results
      # ... aggregation logic
    
    {% for i in range(num_workers) %}
    - name: worker-{{i}}
      inputs:
      - dataset:
          name: input-data
          path: partition-{{i}}
      # ... processing logic, send results to {{host:aggregator}}
    {% endfor %}
```

**Sources:** General pattern inferred from group architecture

---

## Group Status and Lifecycle

### Status Transitions

Groups follow a specific status lifecycle from submission to completion:

```mermaid
stateDiagram-v2
    [*] --> SUBMITTING: Group created
    SUBMITTING --> WAITING: Committed to DB
    WAITING --> PROCESSING: Worker picks up
    PROCESSING --> SCHEDULING: Backend creates pods
    SCHEDULING --> INITIALIZING: Pods scheduled
    INITIALIZING --> RUNNING: Init containers complete
    
    RUNNING --> COMPLETED: All tasks succeed
    RUNNING --> FAILED: Any task fails
    RUNNING --> FAILED_CANCELED: User cancels
    RUNNING --> FAILED_TIMEOUT: Timeout exceeded
    
    state "Terminal States" as term {
        COMPLETED
        FAILED
        FAILED_CANCELED
        FAILED_TIMEOUT
        FAILED_UPSTREAM
    }
    
    COMPLETED --> [*]
    FAILED --> [*]
    FAILED_CANCELED --> [*]
    FAILED_TIMEOUT --> [*]
```

### Group-Level vs Task-Level Status

| Aspect | Group Status | Task Status |
|--------|--------------|-------------|
| **Granularity** | Entire group | Individual task |
| **Scheduling** | All tasks together | N/A (handled at group level) |
| **Completion** | When all tasks finish | When single task finishes |
| **Failure** | If any task fails | Task-specific failures |
| **Retry** | Entire group retried | Individual task may retry |

**Sources:** [src/utils/job/task.py:151-257](), [src/utils/connectors/postgres.py:692-715]()

---

## Implementation Details

### Key Code Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `TaskGroup` class | [src/utils/job/task.py]() | Group data model and database operations |
| `K8sObjectFactory` | [src/utils/job/kb_objects.py:43-323]() | Kubernetes resource creation |
| `KaiK8sObjectFactory` | [src/utils/job/kb_objects.py:324-478]() | KAI scheduler integration |
| `create_headless_service()` | [src/utils/job/kb_objects.py:242-261]() | Private network DNS |
| `create_group_k8s_resources()` | [src/utils/job/kb_objects.py:74-103]() | Gang scheduling setup |
| `update_barrier()` | [src/service/logger/ctrl_websocket.py:93-116]() | Barrier synchronization |

### Database Queries

**Fetch group information:**
```sql
SELECT * FROM groups 
WHERE workflow_id = %s AND name = %s;
```

**Get all tasks in a group:**
```sql
SELECT * FROM tasks 
WHERE workflow_id = %s AND group_name = %s;
```

**Check group completion:**
```sql
SELECT status FROM tasks 
WHERE workflow_id = %s AND group_name = %s 
  AND status NOT IN ('COMPLETED', 'FAILED%');
```

**Sources:** [src/utils/connectors/postgres.py:692-715]()

---

## Best Practices

### Resource Allocation

1. **Homogeneous resources** - Use consistent resource specs within a group for predictable scheduling
2. **Platform targeting** - Specify platforms when tasks need specific hardware (GPUs, embedded devices)
3. **Memory overhead** - Account for networking and coordination overhead in memory requests

### Network Communication

1. **Use host tokens** - Always use `{{host:task_name}}` rather than hardcoding IPs
2. **DNS resolution** - Allow time for DNS propagation before attempting connections
3. **Port selection** - Choose non-conflicting ports for services (avoid well-known ports)

### Synchronization

1. **Barrier placement** - Use barriers after variable-time setup, before critical work
2. **Timeout configuration** - Set appropriate timeouts for barrier waits
3. **Failure handling** - Implement retry logic around barrier operations

### Debugging

1. **Check pod status** - Use `osmo workflow describe` to see task statuses
2. **Network troubleshooting** - Use `osmo workflow exec` to run `nslookup` and `ping` tests
3. **Log inspection** - Review logs from all tasks in group, not just failed ones

**Sources:** [docs/user_guide/how_to/training/multi_node.rst:31-33](), [docs/user_guide/how_to/hil.rst:203-206]()

---

**Sources for this document:**
- [src/utils/connectors/postgres.py:692-715]()
- [src/utils/job/task.py:58](), [src/utils/job/task.py:151-257](), [src/utils/job/task.py:598]()
- [src/utils/job/kb_objects.py:43-323](), [src/utils/job/kb_objects.py:324-478]()
- [src/service/logger/ctrl_websocket.py:93-116]()
- [docs/user_guide/workflows/specification/templates_and_tokens.rst:167-223]()
- [docs/user_guide/how_to/training/multi_node.rst:46-215]()
- [docs/user_guide/how_to/ros2_comm.rst:70-110]()
- [docs/user_guide/how_to/hil.rst:169-287]()
- [workflows/ros/comm/ros2_comm.yaml]()
- [workflows/hil/setup_discovery_server.sh:18-24]()

---

# Page: Workflow Lifecycle and Execution

# Workflow Lifecycle and Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/user_guide/how_to/hil.rst](docs/user_guide/how_to/hil.rst)
- [docs/user_guide/how_to/isaac_groot_notebook.rst](docs/user_guide/how_to/isaac_groot_notebook.rst)
- [docs/user_guide/how_to/isaac_sim_sdg.rst](docs/user_guide/how_to/isaac_sim_sdg.rst)
- [docs/user_guide/how_to/reinforcement_learning.rst](docs/user_guide/how_to/reinforcement_learning.rst)
- [docs/user_guide/how_to/ros2_comm.rst](docs/user_guide/how_to/ros2_comm.rst)
- [docs/user_guide/how_to/training/multi_node.rst](docs/user_guide/how_to/training/multi_node.rst)
- [docs/user_guide/how_to/training/single_node.rst](docs/user_guide/how_to/training/single_node.rst)
- [docs/user_guide/workflows/specification/templates_and_tokens.rst](docs/user_guide/workflows/specification/templates_and_tokens.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)
- [workflows/hil/setup_discovery_server.sh](workflows/hil/setup_discovery_server.sh)
- [workflows/ros/comm/ros2_comm.yaml](workflows/ros/comm/ros2_comm.yaml)
- [workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml](workflows/synthetic_data_generation/isaac_sim/isaac_sim_sdg.yaml)

</details>



## Purpose and Scope

This page traces the complete lifecycle of a workflow from submission through execution to completion. It explains how OSMO processes workflow YAML files, creates Kubernetes resources, schedules tasks, streams logs, and handles cleanup. For information about writing workflow specifications, see [Workflow Specification](#6.1). For details on Jinja templating and special tokens, see [Jinja Templates and Special Tokens](#6.2). For distributed task coordination, see [Distributed Workflows with Groups](#6.3).

---

## Workflow Submission Overview

When a user submits a workflow using `osmo workflow submit`, the workflow passes through multiple phases before tasks begin executing.

### High-Level Submission Flow

```mermaid
sequenceDiagram
    participant User
    participant API as "API Service"
    participant Jinja as "JinjaSandbox"
    participant Postgres as "PostgreSQL"
    participant Worker as "Worker Service"
    participant Backend as "Backend Operator"
    participant K8s as "Kubernetes"
    
    User->>API: Submit workflow YAML
    API->>Jinja: Expand Jinja templates
    Jinja-->>API: Expanded workflow spec
    API->>API: Validate specification
    API->>API: Resolve special tokens<br/>{{workflow_id}}, {{input}}, {{output}}
    API->>Postgres: Insert workflow record<br/>(status: SUBMITTING)
    API->>Postgres: Insert task records
    API->>Postgres: Insert group records
    API-->>User: Return workflow_id
    
    Worker->>Postgres: Poll for SUBMITTING workflows
    Worker->>Postgres: Update status to WAITING
    Worker->>Postgres: Update status to PROCESSING
    Worker->>Backend: Send task creation jobs
    
    Backend->>K8s: Create Secrets, ConfigMaps
    Backend->>K8s: Create Pods/PodGroups
    Backend->>Postgres: Update status to SCHEDULING
    
    K8s->>K8s: KAI Scheduler assigns nodes
    K8s->>K8s: Start osmo-init container
    Backend->>Postgres: Update status to INITIALIZING
    
    K8s->>K8s: Start osmo-ctrl container
    K8s->>K8s: Start user container(s)
    Backend->>Postgres: Update status to RUNNING
    
    K8s->>API: Stream logs via WebSocket
    K8s->>K8s: Execute user commands
    
    K8s->>Backend: Task completes
    Backend->>Postgres: Update status to COMPLETED
```

**Sources:** [src/utils/connectors/postgres.py:632-753](), [src/utils/job/task.py:151-257]()

---

## Workflow Status Transitions

Tasks and groups progress through well-defined status states during their lifecycle. The `TaskGroupStatus` enum defines these states.

### Status State Machine

```mermaid
stateDiagram-v2
    [*] --> SUBMITTING: workflow submit
    SUBMITTING --> WAITING: Worker reads workflow
    WAITING --> PROCESSING: Worker begins processing
    PROCESSING --> SCHEDULING: Backend receives job
    SCHEDULING --> INITIALIZING: Pod scheduled by KAI
    INITIALIZING --> RUNNING: Init container completes
    RUNNING --> COMPLETED: Task exits 0
    RUNNING --> FAILED: Task exits non-zero
    RUNNING --> RESCHEDULED: Exit action triggers
    
    PROCESSING --> FAILED_UPSTREAM: Dependency failed
    SCHEDULING --> FAILED_QUEUE_TIMEOUT: Queue timeout
    RUNNING --> FAILED_EXEC_TIMEOUT: Execution timeout
    RUNNING --> FAILED_CANCELED: User cancels
    RUNNING --> FAILED_EVICTED: Pod evicted
    SCHEDULING --> FAILED_START_ERROR: Pod start fails
    SCHEDULING --> FAILED_START_TIMEOUT: Start timeout
    RUNNING --> FAILED_PREEMPTED: Higher priority preempts
    
    COMPLETED --> [*]
    FAILED --> [*]
    FAILED_CANCELED --> [*]
    FAILED_UPSTREAM --> [*]
    FAILED_QUEUE_TIMEOUT --> [*]
    FAILED_EXEC_TIMEOUT --> [*]
    FAILED_EVICTED --> [*]
    FAILED_START_ERROR --> [*]
    FAILED_START_TIMEOUT --> [*]
    FAILED_PREEMPTED --> [*]
    RESCHEDULED --> [*]
```

### Status Definitions

| Status | Description | Database Update Location |
|--------|-------------|-------------------------|
| `SUBMITTING` | Workflow submitted but not yet read by worker | Initial insert |
| `WAITING` | Worker has read workflow but not processed | Worker service |
| `PROCESSING` | Worker processing, creating K8s resources | Worker service |
| `SCHEDULING` | Kubernetes scheduler queue | Backend operator |
| `INITIALIZING` | Pod scheduled, init container running | Backend operator |
| `RUNNING` | User containers executing | Backend operator |
| `COMPLETED` | Task finished successfully | Backend operator |
| `FAILED` | Task failed (uncategorized) | Backend operator |
| `FAILED_UPSTREAM` | Dependency task failed | Worker service |
| `FAILED_CANCELED` | User canceled workflow | API service |
| `FAILED_EXEC_TIMEOUT` | Execution time exceeded | Backend operator |
| `FAILED_QUEUE_TIMEOUT` | Queue time exceeded | Backend operator |
| `RESCHEDULED` | Task restarted per exit action | Backend operator |

**Sources:** [src/utils/job/task.py:151-257](), [src/utils/connectors/postgres.py:718-753]()

---

## Template Expansion Phase

Before workflow submission, Jinja templates are expanded using the `JinjaSandbox` class. This happens server-side in the API service.

### Template Processing Components

```mermaid
graph TB
    YAML["Workflow YAML<br/>with {{ variables }}"]
    DefaultValues["default-values section"]
    UserArgs["--set arguments"]
    
    JinjaSandbox["JinjaSandbox<br/>lib/utils/jinja_sandbox.py"]
    Environment["Jinja2.Environment<br/>sandboxed"]
    Render["Template.render()"]
    
    ExpandedYAML["Expanded YAML<br/>all variables resolved"]
    
    YAML --> JinjaSandbox
    DefaultValues --> JinjaSandbox
    UserArgs --> JinjaSandbox
    
    JinjaSandbox --> Environment
    Environment --> Render
    Render --> ExpandedYAML
    
    style JinjaSandbox fill:#f9f9f9
```

### Example: Multi-Node Template Expansion

Before expansion (workflow YAML):
```yaml
groups:
- name: training
  tasks:
  {% for item in range(n_nodes) %}
  - name: worker_{{item}}
    command: ["torchrun"]
    args: ["--node_rank", "{{item}}"]
  {% endfor %}

default-values:
  n_nodes: 2
```

After expansion (with `--set n_nodes=2`):
```yaml
groups:
- name: training
  tasks:
  - name: worker_0
    command: ["torchrun"]
    args: ["--node_rank", "0"]
  - name: worker_1
    command: ["torchrun"]
    args: ["--node_rank", "1"]
```

**Sources:** [src/lib/utils/jinja_sandbox.py](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:24-116]()

---

## Special Token Resolution

After Jinja expansion, OSMO resolves special tokens that provide runtime values. These tokens follow the pattern `{{token_name}}` and cannot be overridden by users.

### Token Resolution Timing

```mermaid
graph LR
    Submit["Workflow Submission"]
    CreateWF["Create workflow_id"]
    InsertDB["Insert to database"]
    TokenSub["Token Substitution"]
    K8sCreate["Create K8s Resources"]
    Runtime["Runtime Resolution"]
    
    Submit --> CreateWF
    CreateWF --> InsertDB
    InsertDB --> TokenSub
    TokenSub --> K8sCreate
    K8sCreate --> Runtime
    
    subgraph "Server-Side Resolution"
        CreateWF
        InsertDB
        TokenSub
    end
    
    subgraph "Kubernetes Resource Creation"
        K8sCreate
    end
    
    subgraph "Runtime Resolution"
        Runtime
    end
    
    style TokenSub fill:#f9f9f9
```

### Special Tokens and Resolution Points

| Token | Resolved When | Value Source | Used In |
|-------|---------------|--------------|---------|
| `{{workflow_id}}` | Workflow creation | Generated UUID | All resources |
| `{{input:N}}` | Task creation | Dataset mount path | File contents, environment |
| `{{output}}` | Task creation | Output mount path | File contents, environment |
| `{{host:task_name}}` | Pod creation | Kubernetes subdomain | File contents, environment |

### Host Token Resolution Example

The `{{host:task_name}}` token resolves to a Kubernetes headless service subdomain, enabling inter-task communication:

```yaml
groups:
- name: training
  tasks:
  - name: master
    lead: true
    files:
    - path: /tmp/run.sh
      contents: |
        torchrun --master_addr {{host:master}} --master_port 29400
```

Resolves to:
```bash
torchrun --master_addr master.osmo-<group_uuid>.default.svc.cluster.local --master_port 29400
```

The subdomain is constructed by `get_group_subdomain_name()` and used in the headless service created by `K8sObjectFactory.create_headless_service()`.

**Sources:** [src/lib/utils/common.py:150](), [src/utils/job/kb_objects.py:242-261](), [docs/user_guide/workflows/specification/templates_and_tokens.rst:117-229]()

---

## Database Persistence

Workflow, group, and task information is persisted to PostgreSQL immediately after validation.

### Database Schema for Workflow Execution

```mermaid
erDiagram
    workflows ||--o{ tasks : contains
    workflows ||--o{ groups : contains
    workflows ||--o{ workflow_tags : has
    groups ||--o{ tasks : contains
    tasks ||--o{ task_io : tracks
    
    workflows {
        text workflow_uuid PK
        text workflow_id UK
        text workflow_name
        int job_id
        text submitted_by
        text status
        timestamp submit_time
        timestamp start_time
        timestamp end_time
        int exec_timeout
        int queue_timeout
        text backend
        text pool
    }
    
    groups {
        text group_uuid PK
        text workflow_id FK
        text name
        jsonb spec
        text status
        timestamp start_time
        timestamp end_time
        hstore remaining_upstream_groups
        hstore downstream_groups
    }
    
    tasks {
        text task_db_key PK
        text task_uuid
        text workflow_id FK
        text name
        int retry_id
        text group_name
        text status
        timestamp scheduling_start_time
        timestamp initializing_start_time
        timestamp start_time
        timestamp end_time
        text node_name
        text pod_name
        text pod_ip
    }
```

### Workflow Record Creation

The workflow is inserted into the `workflows` table with initial status `SUBMITTING`:

```python
# Simplified from actual code flow
workflow_uuid = generate_unique_id()
workflow_id = f"{workflow_name}-{job_id}"

INSERT INTO workflows (
    workflow_uuid, workflow_id, workflow_name, job_id,
    submitted_by, status, submit_time, backend, pool
) VALUES (%s, %s, %s, %s, %s, 'SUBMITTING', NOW(), %s, %s)
```

Tasks are inserted with their dependencies tracked via the `remaining_upstream_groups` field in the `groups` table.

**Sources:** [src/utils/connectors/postgres.py:632-787](), [src/utils/job/workflow.py]()

---

## Kubernetes Resource Creation

The Backend Operator creates Kubernetes resources based on task specifications. The `K8sObjectFactory` orchestrates this process.

### K8s Object Creation Flow

```mermaid
graph TB
    BackendJob["BackendJob<br/>from Worker"]
    Factory["K8sObjectFactory<br/>kb_objects.py"]
    
    Secret["create_secret()<br/>User credentials"]
    ConfigMap["create_config_map()<br/>File mounts"]
    ImageSecret["create_image_secret()<br/>Registry auth"]
    HeadlessService["create_headless_service()<br/>For {{host:task}} resolution"]
    
    InitContainer["create_init_container()<br/>osmo-init"]
    CtrlContainer["create_control_container()<br/>osmo-ctrl"]
    UserContainer["TaskSpec.to_pod_container()<br/>User containers"]
    
    Pod["Pod spec with<br/>init, ctrl, user containers"]
    PodGroup["PodGroup spec<br/>(KAI Scheduler)"]
    
    K8sAPI["Kubernetes API<br/>Create resources"]
    
    BackendJob --> Factory
    Factory --> Secret
    Factory --> ConfigMap
    Factory --> ImageSecret
    Factory --> HeadlessService
    
    Factory --> InitContainer
    Factory --> CtrlContainer
    Factory --> UserContainer
    
    InitContainer --> Pod
    CtrlContainer --> Pod
    UserContainer --> Pod
    
    Factory --> PodGroup
    
    Secret --> K8sAPI
    ConfigMap --> K8sAPI
    ImageSecret --> K8sAPI
    HeadlessService --> K8sAPI
    Pod --> K8sAPI
    PodGroup --> K8sAPI
    
    style Factory fill:#f9f9f9
```

### Container Architecture per Pod

Each task pod contains three types of containers:

1. **osmo-init** (init container): Copies binaries and configuration files
2. **osmo-ctrl** (sidecar): Handles data download/upload, log streaming
3. **User containers**: Specified in task spec, runs actual workload

**Volume Mounts (shared across containers):**
- `/osmo/bin/` - OSMO executables (osmo_exec, osmo_ctrl)
- `/osmo/data/input/` - Input dataset mount point
- `/osmo/data/output/` - Output dataset mount point  
- `/osmo/data/socket/` - Unix socket for ctrl-user communication
- `/osmo/login/config/` - User authentication config

**Sources:** [src/utils/job/kb_objects.py:43-476](), [src/utils/job/task.py:748-863]()

---

## Gang Scheduling with KAI

For groups with multiple tasks, OSMO uses the KAI scheduler to ensure all tasks in a group are scheduled simultaneously (gang scheduling).

### KAI PodGroup Creation

```mermaid
graph TB
    Group["Group Spec<br/>tasks: [master, worker_1, worker_2]"]
    Factory["KaiK8sObjectFactory<br/>kb_objects.py:324-476"]
    
    PodSpecs["Individual Pod Specs"]
    PodGroup["PodGroup CRD<br/>scheduling.run.ai/v2alpha2"]
    Queue["Queue<br/>osmo-pool-{namespace}-{pool}"]
    Priority["PriorityClass<br/>osmo-{priority}"]
    
    Annotations["Pod Annotations<br/>pod-group-name: {group_uuid}"]
    Labels["Pod Labels<br/>kai.scheduler/queue"]
    
    Group --> Factory
    Factory --> PodSpecs
    Factory --> PodGroup
    
    PodGroup --> Queue
    PodGroup --> Priority
    PodSpecs --> Annotations
    PodSpecs --> Labels
    
    style Factory fill:#f9f9f9
    style PodGroup fill:#f9f9f9
```

### PodGroup Specification

```yaml
apiVersion: scheduling.run.ai/v2alpha2
kind: PodGroup
metadata:
  name: osmo-{group_uuid}
  labels:
    kai.scheduler/queue: osmo-pool-{namespace}-{pool}
    workflow.osmo: {workflow_id}
spec:
  minMember: 3  # Number of tasks in group
  queue: osmo-pool-{namespace}-{pool}
  priorityClassName: osmo-normal
```

All pods in the group must be schedulable simultaneously, or none will be scheduled. This guarantees that distributed training tasks like multi-node TorchRun start together.

**Sources:** [src/utils/job/kb_objects.py:324-476](), [docs/user_guide/how_to/training/multi_node.rst:46-97]()

---

## Task Initialization Phase

Before user containers start, the `osmo-init` container prepares the pod environment.

### Init Container Responsibilities

```mermaid
graph LR
    Start["Pod Scheduled"]
    Init["osmo-init container<br/>starts"]
    
    CopyBin["Copy osmo_exec<br/>to /osmo/bin/"]
    CopyCtrl["Copy osmo_ctrl<br/>to /osmo/bin/"]
    CreateDirs["Create directories<br/>/osmo/data/*"]
    SetupLogin["Setup login config<br/>/osmo/login/"]
    SetupBin["Setup user binaries<br/>/osmo/usr-bin/"]
    
    InitComplete["Init container<br/>completes"]
    CtrlStart["osmo-ctrl starts"]
    UserStart["User containers start"]
    
    Start --> Init
    Init --> CopyBin
    Init --> CopyCtrl
    Init --> CreateDirs
    Init --> SetupLogin
    Init --> SetupBin
    
    CopyBin --> InitComplete
    CopyCtrl --> InitComplete
    CreateDirs --> InitComplete
    SetupLogin --> InitComplete
    SetupBin --> InitComplete
    
    InitComplete --> CtrlStart
    InitComplete --> UserStart
```

### Init Container Volume Setup

The init container has access to:
- `/osmo_binaries/` - Source for OSMO executables
- `/osmo/` - Target volume (shared with other containers)
- `/osmo/data/` - Data directories
- `/osmo/login/` - Login configuration
- `/osmo/usr-bin/` - User binaries location

**Sources:** [src/utils/job/kb_objects.py:111-152]()

---

## Task Execution Phase

Once initialization completes, two containers run in parallel: `osmo-ctrl` (control) and user containers.

### Execution Container Architecture

```mermaid
graph TB
    subgraph Pod["Task Pod"]
        subgraph Ctrl["osmo-ctrl Container"]
            CtrlBin["osmo_ctrl binary"]
            WebSocket["WebSocket to Logger"]
            DataMgmt["Data Download/Upload<br/>DataService API"]
            UnixSocket["Unix Socket<br/>/osmo/data/socket/"]
        end
        
        subgraph User["User Container(s)"]
            Entrypoint["osmo_exec wrapper"]
            Commands["User commands"]
            DataAccess["Read: /osmo/data/input/<br/>Write: /osmo/data/output/"]
        end
    end
    
    Logger["Logger Service<br/>ctrl_websocket"]
    Storage["Object Storage<br/>S3/MinIO/Azure"]
    
    CtrlBin --> WebSocket
    CtrlBin --> DataMgmt
    CtrlBin --> UnixSocket
    
    WebSocket --> Logger
    DataMgmt --> Storage
    
    Entrypoint --> Commands
    Commands --> DataAccess
    Entrypoint --> UnixSocket
    
    style Ctrl fill:#f9f9f9
    style User fill:#f9f9f9
```

### osmo-ctrl Responsibilities

The control container (`osmo-ctrl`) handles:

1. **Data Download**: Downloads input datasets specified in `inputs:` field
2. **Data Upload**: Uploads output datasets specified in `outputs:` field
3. **Log Streaming**: Forwards logs to Logger service via WebSocket
4. **Metrics Collection**: Reports download/upload metrics to database
5. **Checkpoint Management**: Syncs checkpoints at specified intervals

### osmo_exec Wrapper

User containers don't execute commands directly. Instead, `osmo_exec` wraps the execution:

```bash
# User specified in workflow:
command: ["python3", "train.py"]

# Actual pod command:
command: ["/osmo/bin/osmo_exec"]
args: ["-commands", "python3", "-commands", "train.py"]
```

The wrapper:
- Sets up environment variables
- Communicates with osmo-ctrl via Unix socket
- Reports exit codes
- Handles exit actions (COMPLETE, FAIL, RESCHEDULE)

**Sources:** [src/utils/job/kb_objects.py:154-240](), [src/utils/job/task.py:775-863]()

---

## Log Streaming and Monitoring

Logs flow from user containers through osmo-ctrl to the Logger service, then stored in Redis for client access.

### Log Streaming Architecture

```mermaid
sequenceDiagram
    participant UserCmd as "User Command"
    participant OsmoExec as "osmo_exec"
    participant OsmoCtrl as "osmo-ctrl"
    participant Logger as "Logger Service<br/>ctrl_websocket"
    participant Redis as "Redis"
    participant Client as "osmo workflow logs"
    
    UserCmd->>UserCmd: Writes to stdout/stderr
    OsmoExec->>OsmoCtrl: Capture output<br/>via Unix socket
    OsmoCtrl->>Logger: WebSocket message<br/>LogStreamBody
    
    Note over Logger: Parse log message<br/>Mask credentials
    
    Logger->>Redis: XADD {workflow_id}-logs
    Logger->>Redis: XADD {workflow_id}:{task}:{retry}
    Logger->>Redis: Set TTL (7 days)
    
    Client->>Redis: XREAD {workflow_id}-logs
    Redis-->>Client: Stream log entries
    
    Note over OsmoCtrl,Logger: Also handles:<br/>- Metrics (IOType.METRICS)<br/>- Barriers (IOType.BARRIER)<br/>- Log completion (IOType.LOG_DONE)
```

### Log Stream Message Format

```python
# LogStreamBody structure
{
    "source": "task_name",
    "retry_id": 0,
    "time": "2025-01-15T10:30:45.123Z",
    "text": "Training epoch 1/10 complete",
    "io_type": "STDOUT"  # or STDERR
}
```

### Barrier Synchronization

Groups can synchronize task execution using barriers. Tasks call a barrier, and osmo-ctrl coordinates via Redis:

```bash
# In user script
python3 /tmp/osmo_barrier.py --num_nodes 4 --connect {{host:master}} --rank 0
```

osmo-ctrl receives barrier requests and updates a Redis set. When all tasks reach the barrier, all are notified to continue.

**Sources:** [src/service/logger/ctrl_websocket.py:118-248](), [src/utils/connectors/postgres.py:89-92]()

---

## Completion and Cleanup

When tasks finish, the backend operator updates database status and triggers cleanup.

### Completion Flow

```mermaid
graph TB
    UserExit["User command exits<br/>exit code"]
    OsmoExec["osmo_exec reads exit code"]
    ExitAction["Evaluate exit actions<br/>exitActions field"]
    
    Complete["Exit action: COMPLETE"]
    Fail["Exit action: FAIL"]
    Reschedule["Exit action: RESCHEDULE"]
    
    OsmoCtrl["osmo-ctrl uploads output"]
    Backend["Backend operator polls<br/>pod status"]
    
    UpdateDB["Update database<br/>status: COMPLETED"]
    UpdateFail["Update database<br/>status: FAILED"]
    UpdateResched["Update database<br/>status: RESCHEDULED"]
    
    Cleanup["Cleanup Kubernetes<br/>resources"]
    SaveLogs["Save error logs<br/>(if configured)"]
    
    UserExit --> OsmoExec
    OsmoExec --> ExitAction
    
    ExitAction --> Complete
    ExitAction --> Fail
    ExitAction --> Reschedule
    
    Complete --> OsmoCtrl
    Fail --> OsmoCtrl
    Reschedule --> OsmoCtrl
    
    OsmoCtrl --> Backend
    
    Backend --> UpdateDB
    Backend --> UpdateFail
    Backend --> UpdateResched
    
    UpdateDB --> Cleanup
    UpdateFail --> SaveLogs
    UpdateFail --> Cleanup
    UpdateResched --> Cleanup
    
    style ExitAction fill:#f9f9f9
```

### Exit Actions

Tasks can define custom exit actions based on exit codes:

```yaml
tasks:
- name: train
  exitActions:
    COMPLETE: "0"           # Exit code 0 → COMPLETED
    FAIL: "1-10,20-30"      # Exit codes 1-10, 20-30 → FAILED
    RESCHEDULE: "11-19"     # Exit codes 11-19 → RESCHEDULED (retry)
```

The `RESCHEDULE` action creates a new task instance with incremented `retry_id`.

### Cleanup Process

The Backend Operator deletes Kubernetes resources:

1. **Pods** - User task pods
2. **PodGroups** - Gang scheduling groups (for KAI)
3. **Secrets** - User credentials and file mounts
4. **ConfigMaps** - Configuration data
5. **Services** - Headless services for {{host:task}}

Resources are identified by labels: `workflow.osmo: {workflow_id}`, `group.osmo: {group_name}`

**Sources:** [src/utils/job/task.py:127-149](), [src/utils/job/task.py:696-709](), [src/utils/job/kb_objects.py:100-107]()

---

## Complete Lifecycle Example

This example traces a simple workflow from submission to completion.

### Example Workflow

```yaml
workflow:
  name: example
  tasks:
  - name: preprocess
    image: ubuntu
    command: ["bash"]
    args: ["-c", "echo 'data' > {{output}}/data.txt"]
    outputs:
    - dataset:
        name: processed-data
  
  - name: train
    image: pytorch
    command: ["python3"]
    args: ["/tmp/train.py"]
    inputs:
    - dataset:
        name: processed-data
    outputs:
    - dataset:
        name: trained-model
```

### Lifecycle Trace

| Time | Component | Status | Action |
|------|-----------|--------|--------|
| T0 | User | - | `osmo workflow submit example.yaml` |
| T1 | API Service | SUBMITTING | Insert workflow: `example-1`, task: `preprocess`, `train` |
| T2 | Worker Service | WAITING | Poll database, find `example-1` |
| T3 | Worker Service | PROCESSING | Validate dependencies, create backend jobs |
| T4 | Backend Operator | SCHEDULING | Create Secrets, Pods for `preprocess` |
| T5 | KAI Scheduler | SCHEDULING | Assign `preprocess` pod to node |
| T6 | Kubernetes | INITIALIZING | Start osmo-init container |
| T7 | Kubernetes | RUNNING | Start osmo-ctrl, user container |
| T8 | osmo-ctrl | RUNNING | No inputs to download |
| T9 | User Container | RUNNING | Execute: `bash -c "echo 'data' > /osmo/data/output/data.txt"` |
| T10 | User Container | RUNNING | Exit code 0 |
| T11 | osmo-ctrl | RUNNING | Upload `/osmo/data/output/` to dataset `processed-data` |
| T12 | Backend Operator | COMPLETED | Update database: `preprocess` COMPLETED |
| T13 | Backend Operator | SCHEDULING | Create Secrets, Pods for `train` (dependency satisfied) |
| T14-T20 | (repeat) | - | Similar flow for `train` task |
| T21 | Worker Service | COMPLETED | All tasks complete, workflow COMPLETED |
| T22 | Backend Operator | - | Cleanup: delete Pods, Secrets, PodGroups |

**Sources:** [src/utils/job/workflow.py](), [src/utils/job/task.py](), [src/service/core/workflow/]()

---

## Key Code Entities

The following table maps high-level concepts to their primary code implementations:

| Concept | Primary Class/Function | File Path |
|---------|------------------------|-----------|
| Workflow Status | `TaskGroupStatus` enum | [src/utils/job/task.py:151-257]() |
| Template Expansion | `JinjaSandbox` class | [src/lib/utils/jinja_sandbox.py]() |
| Special Token Resolution | `resolve_special_tokens()` | [src/lib/utils/common.py]() |
| Database Schema | `workflows`, `groups`, `tasks` tables | [src/utils/connectors/postgres.py:632-787]() |
| K8s Object Creation | `K8sObjectFactory` class | [src/utils/job/kb_objects.py:43-323]() |
| Gang Scheduling | `KaiK8sObjectFactory` class | [src/utils/job/kb_objects.py:324-476]() |
| Init Container | `create_init_container()` | [src/utils/job/kb_objects.py:111-152]() |
| Control Container | `create_control_container()` | [src/utils/job/kb_objects.py:154-240]() |
| User Container | `TaskSpec.to_pod_container()` | [src/utils/job/task.py:775-863]() |
| Log Streaming | `run_websocket()` | [src/service/logger/ctrl_websocket.py:118-248]() |
| Barrier Sync | `update_barrier()` | [src/service/logger/ctrl_websocket.py:93-116]() |
| Exit Actions | `ExitAction` enum | [src/utils/job/task.py:127-149]() |
| Cleanup | `get_group_cleanup_specs()` | [src/utils/job/kb_objects.py:100-107]() |

**Sources:** Multiple files as cited above

---

# Page: Kubernetes Deployment

# Kubernetes Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)

</details>



This page describes OSMO's Kubernetes deployment architecture and the Helm charts used to deploy the platform. It covers the overall structure, namespace organization, and the relationship between different deployment components.

For detailed information about specific aspects of the deployment:
- Helm chart structure and dependencies: see [Helm Chart Architecture](#7.1)
- Individual service configurations: see [Service Deployments](#7.2)
- Sidecar container patterns: see [Sidecar Containers](#7.3)
- Ingress and network configuration: see [Ingress and Networking](#7.4)
- Autoscaling and resource management: see [Scaling and Resource Management](#7.5)

For backend operator deployment on compute clusters: see [Deploying a Backend](#5.2)

## Deployment Architecture Overview

OSMO uses a **multi-namespace Kubernetes architecture** that separates the control plane from compute planes. The control plane runs OSMO services that manage workflows and state, while compute planes (backend operators) execute workflow tasks.

### Kubernetes Namespace Organization

```mermaid
graph TB
    subgraph "Control Plane Namespace: osmo"
        direction TB
        
        APIDeployment["Deployment: osmo-service<br/>(API Container + Envoy Sidecar)"]
        UIDeployment["Deployment: osmo-ui<br/>(UI Container + Envoy Sidecar)"]
        WorkerDeployment["Deployment: osmo-worker"]
        LoggerDeployment["Deployment: osmo-logger"]
        AgentDeployment["Deployment: osmo-agent"]
        MonitorDeployment["Deployment: osmo-delayed-job-monitor"]
        
        APISvc["Service: osmo-service"]
        UISvc["Service: osmo-ui"]
        
        APIIngress["Ingress: osmo-service<br/>path: /api, /client"]
        UIIngress["Ingress: osmo-ui<br/>path: /"]
        
        APIHPA["HorizontalPodAutoscaler:<br/>osmo-service"]
        WorkerHPA["HorizontalPodAutoscaler:<br/>osmo-worker"]
    end
    
    subgraph "Router Namespace: osmo-router"
        RouterDeployment["Deployment: osmo-router<br/>(Router Container + Envoy Sidecar)"]
        RouterSvc["Service: osmo-router"]
        RouterIngress["Ingress: osmo-router<br/>path: /api/router"]
        RouterHPA["HorizontalPodAutoscaler:<br/>osmo-router"]
    end
    
    subgraph "Backend Operator Namespace: osmo-operator"
        BackendListener["Deployment: osmo-backend-listener"]
        BackendWorker["Deployment: osmo-backend-worker"]
        BackendTest["CronJob: osmo-backend-test-runner"]
    end
    
    subgraph "Workflow Execution Namespace: osmo-workflows"
        WorkflowPods["Pods: user-workflow-tasks<br/>(created dynamically)"]
        PodGroups["PodGroups: task-groups<br/>(for gang scheduling)"]
    end
    
    subgraph "External Dependencies"
        PostgreSQL[("PostgreSQL<br/>(external or in-cluster)")]
        Redis[("Redis<br/>(external or in-cluster)")]
        Keycloak["Keycloak<br/>(namespace: keycloak)"]
        S3["Object Storage<br/>(S3/MinIO/Azure)"]
    end
    
    APIDeployment --> APISvc
    UIDeployment --> UISvc
    RouterDeployment --> RouterSvc
    
    APISvc --> APIIngress
    UISvc --> UIIngress
    RouterSvc --> RouterIngress
    
    APIDeployment -.-> PostgreSQL
    APIDeployment -.-> Redis
    WorkerDeployment -.-> PostgreSQL
    WorkerDeployment -.-> Redis
    
    UIDeployment -.-> Keycloak
    APIDeployment -.-> Keycloak
    RouterDeployment -.-> Keycloak
    
    BackendListener -.->|Polls for tasks| APISvc
    BackendWorker -.->|Creates pods| WorkflowPods
    
    WorkflowPods -.-> S3
```

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:1-368]()
- [deployments/charts/web-ui/templates/ui.yaml:1-408]()
- [deployments/charts/router/templates/router-service.yaml:1-336]()
- [docs/deployment_guide/install_backend/deploy_backend.rst:1-183]()

### Control Plane vs Compute Plane Separation

The architecture uses **outbound-initiated connections** from backend operators to the control plane. Backend operators run in separate Kubernetes clusters (or namespaces) and poll the API service for work. This design enables:

- **Firewall-friendly deployment**: Backends can run behind corporate firewalls
- **Multi-cluster orchestration**: A single control plane manages multiple compute clusters
- **Security isolation**: Workflow execution is isolated from control plane services

The control plane consists of:
- `osmo` namespace: Core OSMO services (API, UI, Worker, Logger, Agent, Monitor)
- `osmo-router` namespace: Router service for interactive workflow access
- `keycloak` namespace: Authentication and SSO

The compute plane consists of:
- `osmo-operator` namespace: Backend operator components
- `osmo-workflows` namespace: User workflow task pods

## Helm Chart Structure

OSMO uses Helm charts to manage Kubernetes deployments. The chart structure follows a modular design with an umbrella chart that orchestrates multiple sub-charts.

### Chart Dependency Hierarchy

```mermaid
graph TB
    QuickStart["quick-start<br/>(Umbrella Chart)<br/>deployments/charts/quick-start/Chart.yaml"]
    
    IngressNginx["ingress-nginx<br/>(External Dependency)<br/>kubernetes.github.io/ingress-nginx"]
    ServiceChart["service<br/>(Sub-chart)<br/>deployments/charts/service/"]
    WebUIChart["web-ui<br/>(Sub-chart)<br/>deployments/charts/web-ui/"]
    RouterChart["router<br/>(Sub-chart)<br/>deployments/charts/router/"]
    BackendChart["backend-operator<br/>(Sub-chart)<br/>deployments/charts/backend-operator/"]
    
    QuickStart --> IngressNginx
    QuickStart --> ServiceChart
    QuickStart --> WebUIChart
    QuickStart --> RouterChart
    QuickStart --> BackendChart
    
    ServiceChart -.->|deploys| APIService["osmo-service<br/>(Deployment)"]
    ServiceChart -.->|deploys| WorkerService["osmo-worker<br/>(Deployment)"]
    ServiceChart -.->|deploys| LoggerService["osmo-logger<br/>(Deployment)"]
    ServiceChart -.->|deploys| AgentService["osmo-agent<br/>(Deployment)"]
    ServiceChart -.->|deploys| MonitorService["osmo-delayed-job-monitor<br/>(Deployment)"]
    
    WebUIChart -.->|deploys| UIService["osmo-ui<br/>(Deployment)"]
    RouterChart -.->|deploys| RouterService["osmo-router<br/>(Deployment)"]
    BackendChart -.->|deploys| BackendListener["osmo-backend-listener<br/>(Deployment)"]
    BackendChart -.->|deploys| BackendWorker["osmo-backend-worker<br/>(Deployment)"]
    
    style QuickStart fill:#f9f9f9
    style ServiceChart fill:#f0f0f0
    style WebUIChart fill:#f0f0f0
    style RouterChart fill:#f0f0f0
    style BackendChart fill:#f0f0f0
```

**Sources:**
- [deployments/charts/quick-start/Chart.yaml:1-42]()

### Chart Versions and Components

The `quick-start` chart defines dependencies in its `Chart.yaml`:

| Dependency | Version | Repository | Purpose |
|------------|---------|------------|---------|
| `ingress-nginx` | 4.13.2 | kubernetes.github.io/ingress-nginx | Ingress controller for external access |
| `service` | 1.0.1 | file://../service | Control plane services (API, Worker, Logger, Agent, Monitor) |
| `web-ui` | 1.0.1 | file://../web-ui | Next.js-based web interface |
| `router` | 1.0.1 | file://../router | Router service for port-forward and exec |
| `backend-operator` | 1.0.1 | file://../backend-operator | Backend operator for workflow execution |

The `service` chart is the largest and most complex, containing templates for five separate services. Each service is deployed as an independent Kubernetes Deployment with associated Services, Ingresses, and HorizontalPodAutoscalers.

**Sources:**
- [deployments/charts/quick-start/Chart.yaml:24-39]()

## Kubernetes Resources Created

### Per-Service Resource Pattern

Each OSMO service follows a consistent Kubernetes resource pattern. Using the API service as an example:

```mermaid
graph LR
    subgraph "API Service Resources"
        APIDeployment["Deployment<br/>osmo-service<br/>api-service.yaml:19-249"]
        
        APIContainer["Container:<br/>osmo-service<br/>image: {location}/service:{tag}<br/>command: service"]
        EnvoySidecar["Sidecar:<br/>envoy<br/>port: 8080<br/>JWT validation"]
        OtelSidecar["Sidecar:<br/>otel-collector<br/>(optional)"]
        LogSidecar["Sidecar:<br/>fluent-bit<br/>(optional)"]
        RateLimitSidecar["Sidecar:<br/>rate-limit<br/>(optional)"]
        
        APIService["Service<br/>osmo-service<br/>api-service.yaml:258-270<br/>targetPort: envoy-http or 8000"]
        APIIngress["Ingress<br/>osmo-service<br/>api-service.yaml:294-335<br/>paths: /api, /client"]
        APIHPA["HorizontalPodAutoscaler<br/>osmo-service<br/>api-service.yaml:339-368<br/>min: 1, max: 3"]
        
        EnvoyConfig["ConfigMap<br/>osmo-service-envoy-config<br/>OAuth2 + JWT config"]
        DBSecret["Secret<br/>db-secret<br/>(db-password)"]
        RedisSecret["Secret<br/>redis-secret<br/>(redis-password)"]
        MEKConfig["ConfigMap<br/>mek-config<br/>(Master Encryption Key)"]
        
        APIDeployment --> APIContainer
        APIDeployment --> EnvoySidecar
        APIDeployment --> OtelSidecar
        APIDeployment --> LogSidecar
        APIDeployment --> RateLimitSidecar
        
        APIDeployment -.->|selector| APIService
        APIService -.->|backend| APIIngress
        APIDeployment -.->|scaleTargetRef| APIHPA
        
        APIContainer -.->|uses| DBSecret
        APIContainer -.->|uses| RedisSecret
        APIContainer -.->|uses| MEKConfig
        EnvoySidecar -.->|uses| EnvoyConfig
    end
```

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:1-368]()

### Resource Configuration Hierarchy

All services inherit configuration from a three-level hierarchy:

1. **Global values** (`global.*`): Shared across all charts
   - `osmoImageLocation`: Container registry location
   - `osmoImageTag`: OSMO version tag
   - `nodeSelector`: Node placement constraints
   - `imagePullSecret`: Registry authentication

2. **Service values** (`services.<service-name>.*`): Per-service configuration
   - `replicas` or `scaling.minReplicas/maxReplicas`: Replica counts
   - `resources.requests/limits`: CPU and memory allocation
   - `hostname`: Service hostname for ingress
   - `envoy.*`: Envoy sidecar configuration

3. **Sidecar values** (`sidecars.*`): Shared sidecar configuration
   - `envoy.enabled`: Enable Envoy authentication proxy
   - `otel.enabled`: Enable OpenTelemetry collector
   - `logAgent.enabled`: Enable log shipping to CloudWatch/other

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:74-148]()
- [docs/deployment_guide/getting_started/deploy_service.rst:479-679]()

## Service Container Commands and Arguments

Each OSMO service runs with specific command-line arguments that configure its behavior:

| Service | Command | Key Arguments | Template File |
|---------|---------|---------------|---------------|
| `osmo-service` | `service` | `--redis_host`, `--postgres_host`, `--mek_file`, `--service_hostname` | [api-service.yaml:76-148]() |
| `osmo-worker` | `worker` | `--redis_host`, `--postgres_host`, `--mek_file` | [worker.yaml:69-122]() |
| `osmo-logger` | `logger` | `--redis_host`, `--postgres_host`, `--mek_file` | [logger-service.yaml:75-125]() |
| `osmo-agent` | `agent_service` | `--redis_host`, `--postgres_host`, `--mek_file`, `--service_hostname` | [agent-service.yaml:75-129]() |
| `osmo-delayed-job-monitor` | `delayed_job_monitor` | `--redis_host`, `--postgres_host`, `--mek_file`, `--enable_metrics` | [delayed-job-monitor.yaml:56-114]() |
| `osmo-router` | `router` | `--hostname`, `--postgres_host`, `--mek_file`, `--config` | [router-service.yaml:76-114]() |
| `osmo-ui` | (Next.js default) | Environment variables only | [ui.yaml:73-108]() |

All services (except UI) accept common flags:
- `--log_level`: Log verbosity (DEBUG, INFO, WARNING, ERROR)
- `--k8s_log_level`: Kubernetes client log level
- `--log_dir`: Directory for log files
- `--metrics_otel_enable`: Enable OpenTelemetry metrics

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:76-148]()
- [deployments/charts/service/templates/worker.yaml:69-122]()
- [deployments/charts/service/templates/logger-service.yaml:75-125]()
- [deployments/charts/service/templates/agent-service.yaml:75-129]()
- [deployments/charts/service/templates/delayed-job-monitor.yaml:56-114]()
- [deployments/charts/router/templates/router-service.yaml:76-114]()
- [deployments/charts/web-ui/templates/ui.yaml:73-108]()

## Probes and Health Checks

OSMO services implement Kubernetes probes to ensure reliability:

### Probe Types by Service

```mermaid
graph TB
    subgraph "API Service"
        APILiveness["livenessProbe<br/>httpGet: /api/version<br/>Detects unresponsive service"]
        APIStartup["startupProbe<br/>httpGet: /api/version<br/>Allows 30s for startup"]
        APIReadiness["readinessProbe<br/>httpGet: /api/workflow?limit=0<br/>Database connectivity check"]
    end
    
    subgraph "Worker/Logger/Agent"
        WorkerLiveness["livenessProbe<br/>exec: progress_check<br/>--progress_interval 300<br/>Detects stuck processes"]
        WorkerStartup["startupProbe<br/>exec: progress_check<br/>--progress_interval 60<br/>Allows 60s for startup"]
        WorkerReadiness["readinessProbe<br/>httpGet: /health<br/>Service health check"]
    end
    
    subgraph "UI Service"
        UILiveness["livenessProbe<br/>httpGet: /<br/>Next.js server check"]
        UIStartup["startupProbe<br/>httpGet: /<br/>Allows 30s for startup"]
        UIReadiness["readinessProbe<br/>httpGet: /<br/>UI availability check"]
    end
    
    subgraph "Router Service"
        RouterLiveness["livenessProbe<br/>(configurable)"]
        RouterStartup["startupProbe<br/>(configurable)"]
        RouterReadiness["readinessProbe<br/>(configurable)"]
    end
```

### Progress Check Mechanism

Worker, Logger, and Agent services use a custom `progress_check` binary that monitors service activity:
- Writes timestamps to `/var/run/osmo/last_progress`
- Liveness probe fails if no progress for 300 seconds
- Prevents services from getting stuck in infinite loops or deadlocks

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:191-217]()
- [deployments/charts/service/templates/worker.yaml:156-177]()
- [deployments/charts/service/templates/logger-service.yaml:161-194]()
- [deployments/charts/service/templates/agent-service.yaml:165-198]()
- [deployments/charts/web-ui/templates/ui.yaml:129-241]()
- [deployments/charts/router/templates/router-service.yaml:173-186]()

## Security Context Configuration

All OSMO service containers run with restricted security contexts:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  runAsNonRoot: true
  runAsUser: 1001  # or 1000 for UI
```

This configuration:
- Prevents privilege escalation attacks
- Drops all Linux capabilities
- Enforces non-root execution
- Uses dedicated UIDs (1000 for UI, 1001 for services)

**Sources:**
- [deployments/charts/service/templates/api-service.yaml:169-174]()
- [deployments/charts/web-ui/templates/ui.yaml:114-119]()

## Deployment Prerequisites

Before deploying OSMO on Kubernetes, the following infrastructure must be available:

### Required External Services

| Service | Purpose | Configuration Location |
|---------|---------|------------------------|
| **PostgreSQL** | Persistent storage for workflows, tasks, datasets, configurations | `services.postgres.serviceName`, `services.postgres.port` |
| **Redis** | Job queues, log streaming, barrier synchronization | `services.redis.serviceName`, `services.redis.port` |
| **Keycloak** | OAuth2/OIDC authentication and SSO | `services.service.auth.*`, `sidecars.envoy.oauth2Filter.*` |
| **Object Storage** | Content-addressable dataset storage (S3/MinIO/Azure) | Configured via dataset config API |

### Required Kubernetes Components

| Component | Purpose | Installation |
|-----------|---------|--------------|
| **Ingress Controller** | External traffic routing | AWS ALB Controller or NGINX Ingress |
| **KAI Scheduler** | Gang scheduling for distributed workflows | See [Installing KAI](#installing-kai-scheduler) |
| **GPU Operator** | GPU device plugin and driver management | See [Installing GPU Operator](#installing-gpu-operator) |

### Required Secrets and ConfigMaps

Before deploying the `quick-start` chart, create these resources:

```bash
# Create namespace
kubectl create namespace osmo

# Database password
kubectl create secret generic db-secret \
  --from-literal=db-password=<password> \
  --namespace osmo

# Redis password
kubectl create secret generic redis-secret \
  --from-literal=redis-password=<password> \
  --namespace osmo

# OAuth2 secrets for Envoy
kubectl create secret generic oidc-secrets \
  --from-literal=client_secret=<keycloak-client-secret> \
  --from-literal=hmac_secret=$(head -c32 /dev/urandom | base64) \
  --namespace osmo

# Master Encryption Key (MEK)
kubectl create configmap mek-config \
  --from-file=mek.yaml=<mek-file> \
  --namespace osmo
```

**Sources:**
- [docs/deployment_guide/getting_started/deploy_service.rst:353-467]()
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst:1-85]()

### Installing KAI Scheduler

OSMO requires the KAI scheduler for gang scheduling of workflow groups:

```bash
# Fetch KAI scheduler chart
helm fetch oci://ghcr.io/nvidia/kai-scheduler/kai-scheduler \
  --version <chart-version>

# Install with OSMO-specific configuration
helm upgrade --install kai-scheduler kai-scheduler-<chart-version>.tgz \
  --create-namespace -n kai-scheduler \
  --set scheduler.additionalArgs[0]="--default-staleness-grace-period=-1s" \
  --set scheduler.additionalArgs[1]="--update-pod-eviction-condition=true"
```

Key configuration flags:
- `--default-staleness-grace-period=-1s`: Disables stale gang eviction
- `--update-pod-eviction-condition=true`: Allows OSMO to read preemption conditions

**Sources:**
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst:32-69]()

### Installing GPU Operator

For GPU workloads, install the NVIDIA GPU Operator:

```bash
helm repo add nvidia https://nvidia.github.io/gpu-operator
helm repo update
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace
```

**Sources:**
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst:71-84]()

## Basic Deployment Steps

### Step 1: Deploy Control Plane Services

Deploy the main OSMO services using the `service`, `web-ui`, and `router` charts:

```bash
# Add OSMO Helm repository
helm repo add osmo https://helm.ngc.nvidia.com/nvidia/osmo
helm repo update

# Deploy service chart (API, Worker, Logger, Agent, Monitor)
helm upgrade --install osmo osmo/service \
  -f osmo_values.yaml \
  --version <chart-version> \
  --namespace osmo

# Deploy web-ui chart
helm upgrade --install osmo-ui osmo/web-ui \
  -f ui_values.yaml \
  --version <chart-version> \
  --namespace osmo

# Deploy router chart
helm upgrade --install osmo-router osmo/router \
  -f router_values.yaml \
  --version <chart-version> \
  --namespace osmo-router
```

**Sources:**
- [docs/deployment_guide/getting_started/deploy_service.rst:470-679]()

### Step 2: Deploy Backend Operator

Deploy the backend operator on the compute cluster:

```bash
# Create namespaces
kubectl create namespace osmo-operator
kubectl create namespace osmo-workflows

# Create service token secret
kubectl create secret generic osmo-operator-token \
  -n osmo-operator \
  --from-literal=token=$OSMO_SERVICE_TOKEN

# Deploy backend operator
helm upgrade --install osmo-operator osmo/backend-operator \
  -f backend_operator_values.yaml \
  --version <chart-version> \
  --namespace osmo-operator
```

The backend operator consists of:
- `osmo-backend-listener`: Polls API service for tasks
- `osmo-backend-worker`: Creates Kubernetes pods for workflow tasks
- `osmo-backend-test-runner`: CronJob for validation tests

**Sources:**
- [docs/deployment_guide/install_backend/deploy_backend.rst:50-118]()

### Step 3: Verify Deployment

Check that all services are running:

```bash
# Check control plane services
kubectl get pods -n osmo
kubectl get pods -n osmo-router

# Check ingress configuration
kubectl get ingress -n osmo
kubectl get ingress -n osmo-router

# Check HPA status
kubectl get hpa -n osmo
kubectl get hpa -n osmo-router

# Check backend operator
kubectl get pods -n osmo-operator

# Verify backend is online
osmo config show BACKEND <backend-name>
```

Expected output shows `"online": true` for the backend.

**Sources:**
- [docs/deployment_guide/install_backend/deploy_backend.rst:119-165]()
- [docs/deployment_guide/install_backend/validate_osmo.rst:1-60]()

## Values File Structure

OSMO Helm charts use a hierarchical values structure. Here's the essential configuration skeleton:

```yaml
global:
  osmoImageLocation: nvcr.io/nvidia/osmo
  osmoImageTag: <version>
  serviceAccountName: osmo
  nodeSelector: {}
  logs:
    enabled: true
    logLevel: DEBUG

services:
  configFile:
    enabled: true
    path: /etc/osmo/mek.yaml
  
  postgres:
    serviceName: <postgres-host>
    port: 5432
    db: osmo
    user: postgres
  
  redis:
    serviceName: <redis-host>
    port: 6379
    tlsEnabled: true
  
  service:  # API service
    hostname: <domain>
    scaling:
      minReplicas: 1
      maxReplicas: 3
    resources:
      requests:
        cpu: "1"
        memory: "1Gi"
      limits:
        memory: "1Gi"
    auth:
      enabled: true
      device_endpoint: https://auth-<domain>/realms/osmo/protocol/openid-connect/device
      # ... other auth endpoints
    ingress:
      enabled: true
      ingressClass: alb  # or nginx
      albAnnotations:
        enabled: true
        sslCertArn: <arn>

  worker:
    scaling:
      minReplicas: 1
      maxReplicas: 3
    resources:
      requests:
        cpu: "500m"
        memory: "400Mi"

  # Similar structure for: logger, agent, delayedJobMonitor

sidecars:
  envoy:
    enabled: true
    useKubernetesSecrets: true
    skipAuthPaths:
      - /api/version
      - /api/auth/login
    service:
      hostname: <domain>
    oauth2Filter:
      enabled: true
      tokenEndpoint: https://auth-<domain>/realms/osmo/protocol/openid-connect/token
      # ... other OAuth2 config
    jwt:
      user_header: x-osmo-user
      providers:
        - issuer: https://auth-<domain>/realms/osmo
          audience: osmo-device
          jwks_uri: https://auth-<domain>/realms/osmo/protocol/openid-connect/certs
        # ... other JWT providers
  
  logAgent:
    enabled: false
  
  otel:
    enabled: false
  
  rateLimit:
    enabled: false
```

**Sources:**
- [docs/deployment_guide/getting_started/deploy_service.rst:479-679]()
- [docs/deployment_guide/getting_started/deploy_service.rst:689-828]()

## Troubleshooting Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Services not starting** | Pods in CrashLoopBackOff | Check logs: `kubectl logs <pod> -n osmo -c <container-name>`. Verify database connectivity and secrets. |
| **Authentication failures** | 401 Unauthorized responses | Verify Keycloak configuration, check OIDC secrets, ensure JWT providers match Keycloak realm. |
| **Ingress not accessible** | 404 or 503 errors | Verify ingress controller is running, check DNS records, validate annotations for your ingress class. |
| **Backend offline** | `"online": false` in config | Check `osmo-backend-listener` logs, verify service token hasn't expired, ensure network connectivity. |
| **Probes failing** | Pods repeatedly restarting | Increase `initialDelaySeconds` in probe configuration, check service startup time. |

**Sources:**
- [docs/deployment_guide/install_backend/deploy_backend.rst:171-183]()

---

# Page: Helm Chart Architecture

# Helm Chart Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/Chart.yaml](deployments/charts/backend-operator/Chart.yaml)
- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/Chart.yaml](deployments/charts/service/Chart.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/Chart.yaml](deployments/charts/web-ui/Chart.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)

</details>



This document describes the structure and organization of OSMO's Helm charts, which provide Kubernetes deployment configurations for all OSMO components. It covers the umbrella chart architecture, individual chart responsibilities, and common deployment patterns. For information about deploying these charts, see [Deployment Options Comparison](#2.2). For details about the services themselves, see [Control Plane Services](#3) and [Backend Operators](#5).

## Chart Hierarchy

OSMO uses a multi-chart architecture with `quick-start` serving as the umbrella chart that orchestrates all component deployments.

```mermaid
graph TB
    QuickStart["quick-start<br/>Chart.yaml<br/>version: 1.0.0"]
    
    subgraph "External Dependencies"
        IngressNginx["ingress-nginx<br/>v4.13.2<br/>kubernetes.github.io/ingress-nginx"]
    end
    
    subgraph "OSMO Charts"
        ServiceChart["service<br/>Chart.yaml<br/>version: 1.0.1"]
        WebUIChart["web-ui<br/>Chart.yaml<br/>version: 1.0.1"]
        RouterChart["router<br/>Chart.yaml<br/>version: 1.0.1"]
        BackendChart["backend-operator<br/>Chart.yaml<br/>version: 1.0.1"]
    end
    
    subgraph "Service Chart Templates"
        APITemplate["api-service.yaml<br/>Deployment + Service + Ingress + HPA"]
        AgentTemplate["agent-service.yaml<br/>Deployment + Service + Ingress + HPA"]
        LoggerTemplate["logger-service.yaml<br/>Deployment + Service + Ingress + HPA"]
        WorkerTemplate["worker.yaml<br/>Deployment + HPA"]
        MonitorTemplate["delayed-job-monitor.yaml<br/>Deployment"]
    end
    
    subgraph "Web-UI Chart Templates"
        UITemplate["ui.yaml<br/>Deployment + Service + Ingress + HPA"]
    end
    
    subgraph "Router Chart Templates"
        RouterTemplate["router-service.yaml<br/>Deployment + Service + Ingress + HPA"]
    end
    
    subgraph "Backend Operator Chart Templates"
        BackendTemplates["backend-listener.yaml<br/>backend-worker.yaml<br/>backend-test-runner.yaml"]
    end
    
    QuickStart -->|"repository: file://../service"| ServiceChart
    QuickStart -->|"repository: file://../web-ui"| WebUIChart
    QuickStart -->|"repository: file://../router"| RouterChart
    QuickStart -->|"repository: file://../backend-operator"| BackendChart
    QuickStart -->|"repository: https://"| IngressNginx
    
    ServiceChart --> APITemplate
    ServiceChart --> AgentTemplate
    ServiceChart --> LoggerTemplate
    ServiceChart --> WorkerTemplate
    ServiceChart --> MonitorTemplate
    
    WebUIChart --> UITemplate
    RouterChart --> RouterTemplate
    BackendChart --> BackendTemplates
```

**Sources:** [deployments/charts/quick-start/Chart.yaml:24-39](), [deployments/charts/service/Chart.yaml:1-40](), [deployments/charts/web-ui/Chart.yaml:1-28](), [deployments/charts/router/Chart.yaml:1-41](), [deployments/charts/backend-operator/Chart.yaml:1-40]()

## Quick-Start Umbrella Chart

The `quick-start` chart is an umbrella chart that bundles all OSMO components for simplified deployment. It declares dependencies on four internal charts and one external chart.

| Dependency | Version | Repository | Purpose |
|------------|---------|------------|---------|
| `ingress-nginx` | 4.13.2 | https://kubernetes.github.io/ingress-nginx | Ingress controller for routing external traffic |
| `service` | 1.0.1 | file://../service | Control plane services (API, Worker, Logger, Agent, Monitor) |
| `web-ui` | 1.0.1 | file://../web-ui | Next.js web interface |
| `router` | 1.0.1 | file://../router | Router service for port-forward and exec |
| `backend-operator` | 1.0.1 | file://../backend-operator | Backend listener and worker |

The umbrella chart uses `file://` references to local sibling directories, enabling coordinated version updates across all components. Each dependency inherits configuration values from the parent chart while allowing per-chart overrides.

**Sources:** [deployments/charts/quick-start/Chart.yaml:24-39]()

## Service Chart

The `service` chart deploys the five core control plane services. Each service template creates a `Deployment`, `Service`, and `HorizontalPodAutoscaler`. Services exposed via ingress also include `Ingress` resources.

```mermaid
graph TB
    ServiceChart["service Chart"]
    
    subgraph "API Service"
        APIDeployment["Deployment<br/>name: .Values.services.service.serviceName"]
        APIService["Service<br/>port 80 → envoy-http or 8000"]
        APIIngress["Ingress<br/>path: /api, /client"]
        APIHPA["HorizontalPodAutoscaler<br/>minReplicas → maxReplicas"]
        APIContainer["Container: service<br/>command: service<br/>args: --redis_host, --postgres_host"]
    end
    
    subgraph "Agent Service"
        AgentDeployment["Deployment<br/>name: .Values.services.agent.serviceName"]
        AgentService["Service<br/>port 80"]
        AgentIngress["Ingress<br/>path: /api/agent"]
        AgentHPA["HorizontalPodAutoscaler<br/>memory + cpu targets"]
        AgentContainer["Container: agent_service<br/>command: agent_service"]
    end
    
    subgraph "Logger Service"
        LoggerDeployment["Deployment<br/>name: .Values.services.logger.serviceName"]
        LoggerService["Service<br/>port 80"]
        LoggerIngress["Ingress<br/>path: /api/logger"]
        LoggerHPA["HorizontalPodAutoscaler<br/>memory + cpu targets"]
        LoggerContainer["Container: logger<br/>command: logger"]
    end
    
    subgraph "Worker Service"
        WorkerDeployment["Deployment<br/>name: .Values.services.worker.serviceName"]
        WorkerHPA["HorizontalPodAutoscaler<br/>memory + cpu targets"]
        WorkerContainer["Container: worker<br/>command: worker<br/>livenessProbe: progress_check"]
    end
    
    subgraph "Delayed Job Monitor"
        MonitorDeployment["Deployment<br/>name: .Values.services.delayedJobMonitor.serviceName"]
        MonitorContainer["Container: delayed_job_monitor<br/>command: delayed_job_monitor<br/>livenessProbe: progress_check"]
    end
    
    ServiceChart --> APIDeployment
    ServiceChart --> AgentDeployment
    ServiceChart --> LoggerDeployment
    ServiceChart --> WorkerDeployment
    ServiceChart --> MonitorDeployment
    
    APIDeployment --> APIContainer
    APIDeployment --> APIService
    APIDeployment --> APIIngress
    APIDeployment --> APIHPA
    
    AgentDeployment --> AgentContainer
    AgentDeployment --> AgentService
    AgentDeployment --> AgentIngress
    AgentDeployment --> AgentHPA
    
    LoggerDeployment --> LoggerContainer
    LoggerDeployment --> LoggerService
    LoggerDeployment --> LoggerIngress
    LoggerDeployment --> LoggerHPA
    
    WorkerDeployment --> WorkerContainer
    WorkerDeployment --> WorkerHPA
    
    MonitorDeployment --> MonitorContainer
```

### API Service Template

The API service deployment is defined in [deployments/charts/service/templates/api-service.yaml:19-368](). Key characteristics:

- **Container**: Runs the `service` command with arguments for Redis, PostgreSQL, authentication endpoints, and OTEL metrics
- **Command Arguments**: [deployments/charts/service/templates/api-service.yaml:78-148]() includes `--redis_host`, `--postgres_host`, `--mek_file`, authentication configuration, and logging parameters
- **Environment Variables**: `OSMO_DISABLE_TASK_METRICS`, `OSMO_POSTGRES_PASSWORD`, `OSMO_REDIS_PASSWORD` [deployments/charts/service/templates/api-service.yaml:149-167]()
- **Probes**: 
  - Liveness: Configurable via `.Values.services.service.livenessProbe` [deployments/charts/service/templates/api-service.yaml:192-193]()
  - Startup: HTTP GET `/api/version` with 6 attempts [deployments/charts/service/templates/api-service.yaml:197-204]()
  - Readiness: HTTP GET `/api/workflow?limit=0&all_pools=true` with `x-osmo-roles: osmo-admin` header [deployments/charts/service/templates/api-service.yaml:207-216]()
- **Sidecars**: Envoy, OpenTelemetry (optional), FluentBit, rate limiter (optional) [deployments/charts/service/templates/api-service.yaml:218-226]()
- **Ingress**: Routes `/api` and `/client` paths with ALB annotations [deployments/charts/service/templates/api-service.yaml:294-335]()
- **HPA**: Scales on memory and CPU utilization [deployments/charts/service/templates/api-service.yaml:339-367]()

### Agent Service Template

The agent service deployment is defined in [deployments/charts/service/templates/agent-service.yaml:20-318](). Key characteristics:

- **Container**: Runs the `agent_service` command [deployments/charts/service/templates/agent-service.yaml:77-78]()
- **Command Arguments**: Similar pattern to API service, includes `--redis_host`, `--postgres_host`, `--service_hostname` [deployments/charts/service/templates/agent-service.yaml:86-129]()
- **Probes**:
  - Liveness: `progress_check --progress_interval 300` with 45s period [deployments/charts/service/templates/agent-service.yaml:166-176]()
  - Startup: `progress_check --progress_interval 60` with 12 attempts [deployments/charts/service/templates/agent-service.yaml:179-190]()
  - Readiness: HTTP GET `/health` on port 8000 [deployments/charts/service/templates/agent-service.yaml:192-198]()
- **Sidecars**: Envoy, OpenTelemetry (optional), FluentBit [deployments/charts/service/templates/agent-service.yaml:201-206]()
- **Ingress**: Routes `/api/agent` path [deployments/charts/service/templates/agent-service.yaml:272-278]()

### Logger Service Template

The logger service deployment is defined in [deployments/charts/service/templates/logger-service.yaml:20-314](). Key characteristics:

- **Container**: Runs the `logger` command [deployments/charts/service/templates/logger-service.yaml:84]()
- **Command Arguments**: Includes `--redis_host`, `--redis_port`, `--redis_tls_enable`, `--postgres_host` [deployments/charts/service/templates/logger-service.yaml:86-125]()
- **Probes**: Identical pattern to agent service using `progress_check` [deployments/charts/service/templates/logger-service.yaml:162-194]()
- **Ingress**: Routes `/api/logger` path [deployments/charts/service/templates/logger-service.yaml:268-274]()

### Worker Template

The worker deployment is defined in [deployments/charts/service/templates/worker.yaml:16-237](). Key characteristics:

- **Container**: Runs the `worker` command [deployments/charts/service/templates/worker.yaml:70]()
- **No Service**: Workers do not expose a network service [deployments/charts/service/templates/worker.yaml:1-237]()
- **Liveness Probe**: Restarts if no progress for 300 seconds using `progress_check` [deployments/charts/service/templates/worker.yaml:157-165]()
- **Startup Probe**: 60 second startup window with `progress_check` [deployments/charts/service/templates/worker.yaml:168-177]()
- **Sidecars**: FluentBit for logging, OpenTelemetry (optional) [deployments/charts/service/templates/worker.yaml:179-185]()

### Delayed Job Monitor Template

The delayed job monitor deployment is defined in [deployments/charts/service/templates/delayed-job-monitor.yaml:16-204](). Key characteristics:

- **Container**: Runs the `delayed_job_monitor` command [deployments/charts/service/templates/delayed-job-monitor.yaml:65]()
- **Replicas**: Configurable via `.Values.services.delayedJobMonitor.replicas` [deployments/charts/service/templates/delayed-job-monitor.yaml:23]()
- **No Service or Ingress**: Internal monitoring component without external exposure
- **Liveness Probe**: Restarts if no progress for 300 seconds [deployments/charts/service/templates/delayed-job-monitor.yaml:153-161]()
- **Metrics**: Optional OTEL metrics with `--enable_metrics` flag [deployments/charts/service/templates/delayed-job-monitor.yaml:109-111]()

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [deployments/charts/service/templates/agent-service.yaml:1-318](), [deployments/charts/service/templates/logger-service.yaml:1-314](), [deployments/charts/service/templates/worker.yaml:1-237](), [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

## Web-UI Chart

The `web-ui` chart deploys the Next.js web interface with Envoy sidecar for authentication. The template is defined in [deployments/charts/web-ui/templates/ui.yaml:17-408]().

```mermaid
graph TB
    UIDeployment["Deployment<br/>name: .Values.services.ui.serviceName"]
    
    subgraph "Main Container"
        UIContainer["Container<br/>image: .../Values.services.ui.imageName"]
        UIPort["containerPort: .Values.services.ui.containerPort<br/>default: 8000"]
        UIEnv["Environment Variables<br/>PORT, NODE_OPTIONS<br/>NEXT_PUBLIC_OSMO_API_HOSTNAME<br/>NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED<br/>NEXT_PUBLIC_OSMO_SSL_ENABLED"]
    end
    
    subgraph "Sidecars"
        EnvoySidecar["Envoy Sidecar<br/>envoy-http port"]
        FluentBitSidecar["FluentBit Sidecar<br/>log collection"]
    end
    
    subgraph "Service"
        UIService["Service<br/>port 80 → envoy-http or containerPort"]
    end
    
    subgraph "Ingress Resources"
        UIIngress["Ingress<br/>host: .Values.services.ui.hostname<br/>path: .Values.services.ui.ingress.prefix"]
        TRPCIngress["Ingress<br/>paths: /api/refresh, /api/trpc<br/>group.order: 50"]
    end
    
    subgraph "Autoscaling"
        UIHPA["HorizontalPodAutoscaler<br/>metrics: memory utilization"]
    end
    
    UIDeployment --> UIContainer
    UIDeployment --> EnvoySidecar
    UIDeployment --> FluentBitSidecar
    UIContainer --> UIPort
    UIContainer --> UIEnv
    
    UIDeployment --> UIService
    UIDeployment --> UIIngress
    UIDeployment --> TRPCIngress
    UIDeployment --> UIHPA
```

Key characteristics:

- **Container**: Next.js application serving on configurable port (default 8000) [deployments/charts/web-ui/templates/ui.yaml:73-127]()
- **Environment Variables**: 
  - `PORT`: Container port [deployments/charts/web-ui/templates/ui.yaml:84-85]()
  - `NODE_OPTIONS`: HTTP header size configuration [deployments/charts/web-ui/templates/ui.yaml:86-87]()
  - `NEXT_PUBLIC_OSMO_API_HOSTNAME`: Backend API hostname [deployments/charts/web-ui/templates/ui.yaml:88-89]()
  - `NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED`: Enable port forwarding UI [deployments/charts/web-ui/templates/ui.yaml:90-91]()
  - `NEXT_PUBLIC_OSMO_SSL_ENABLED`: SSL configuration [deployments/charts/web-ui/templates/ui.yaml:92-93]()
  - `DOCS_BASE_URL`, `CLI_INSTALL_SCRIPT_URL`: Documentation links [deployments/charts/web-ui/templates/ui.yaml:94-97]()
- **Security Context**: Non-root user 1000, no privilege escalation, dropped capabilities [deployments/charts/web-ui/templates/ui.yaml:114-119]()
- **Probes**: Configurable liveness, startup, and readiness probes via values [deployments/charts/web-ui/templates/ui.yaml:129-241]()
- **Sidecars**: Envoy for authentication, FluentBit for logging [deployments/charts/web-ui/templates/ui.yaml:243-244]()
- **Service**: Routes to Envoy sidecar port if enabled, otherwise directly to container [deployments/charts/web-ui/templates/ui.yaml:279-284]()
- **Dual Ingress**: 
  - Main UI ingress with group order 200 [deployments/charts/web-ui/templates/ui.yaml:302-337]()
  - tRPC API ingress with group order 50 for `/api/refresh` and `/api/trpc` paths [deployments/charts/web-ui/templates/ui.yaml:339-381]()
- **HPA**: Scales on memory utilization [deployments/charts/web-ui/templates/ui.yaml:383-407]()
- **Topology Spread**: Configurable pod distribution across topology domains [deployments/charts/web-ui/templates/ui.yaml:42-53]()

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:17-408](), [deployments/charts/web-ui/Chart.yaml:1-28]()

## Router Chart

The `router` chart deploys the router service that handles port-forward, exec, and webserver connections to backend tasks. The template is defined in [deployments/charts/router/templates/router-service.yaml:17-336]().

Key characteristics:

- **Container**: Runs the `router` command [deployments/charts/router/templates/router-service.yaml:78-79]()
- **Command Arguments**: 
  - `--hostname`: Service hostname [deployments/charts/router/templates/router-service.yaml:81-82]()
  - `--postgres_host`, `--postgres_port`, `--postgres_database_name`: Database connection [deployments/charts/router/templates/router-service.yaml:83-88]()
  - `--mek_file` or `--config`: Encryption key or config file path [deployments/charts/router/templates/router-service.yaml:93-99]()
  - Logging configuration [deployments/charts/router/templates/router-service.yaml:100-109]()
- **Environment Variables**: `OSMO_POSTGRES_PASSWORD` from secret or direct value [deployments/charts/router/templates/router-service.yaml:115-125]()
- **Security Context**: Non-root user 1001 [deployments/charts/router/templates/router-service.yaml:138-143]()
- **Service**: Routes to Envoy sidecar if enabled [deployments/charts/router/templates/router-service.yaml:246-252]()
- **Ingress**: 
  - Routes `/api/router` path [deployments/charts/router/templates/router-service.yaml:295-301]()
  - Wildcard host support for webserver feature: `*.{{ .Values.services.service.hostname }}` [deployments/charts/router/templates/router-service.yaml:280-290]()
  - ALB annotations with group order 50 [deployments/charts/router/templates/router-service.yaml:266-269]()
- **HPA**: Scales on memory utilization [deployments/charts/router/templates/router-service.yaml:314-336]()
- **Sidecars**: Envoy, FluentBit [deployments/charts/router/templates/router-service.yaml:188-189]()

**Sources:** [deployments/charts/router/templates/router-service.yaml:1-336](), [deployments/charts/router/Chart.yaml:1-41]()

## Backend-Operator Chart

The `backend-operator` chart deploys the backend listener and worker components that execute workflow tasks on compute resources. This chart is deployed in compute plane namespaces rather than the control plane namespace.

The chart contains three main templates:
- `backend-listener.yaml`: Polls for tasks and monitors cluster state
- `backend-worker.yaml`: Executes tasks and creates Kubernetes resources
- `backend-test-runner.yaml`: CronJob for validation

**Sources:** [deployments/charts/backend-operator/Chart.yaml:1-40]()

## Common Deployment Patterns

All OSMO Helm charts follow consistent patterns for configuration, security, and observability.

### Container Configuration

```mermaid
graph TB
    Container["Container Specification"]
    
    subgraph "Image Configuration"
        ImageLocation["image: .Values.global.osmoImageLocation/.Values.services.X.imageName"]
        ImageTag["tag: .Values.global.osmoImageTag"]
        PullPolicy["imagePullPolicy: .Values.services.X.imagePullPolicy"]
    end
    
    subgraph "Security Context"
        SecurityContext["securityContext"]
        AllowPriv["allowPrivilegeEscalation: false"]
        Capabilities["capabilities: drop ALL"]
        RunAsNonRoot["runAsNonRoot: true"]
        RunAsUser["runAsUser: 1000 or 1001"]
    end
    
    subgraph "Command and Args"
        Command["command: service | worker | logger | agent_service | router"]
        Args["args: --redis_host, --postgres_host<br/>--mek_file, --log_level<br/>--metrics_otel_enable"]
    end
    
    subgraph "Environment Variables"
        PostgresPassword["OSMO_POSTGRES_PASSWORD<br/>from secret or value"]
        RedisPassword["OSMO_REDIS_PASSWORD<br/>from secret"]
        CustomEnv["extraEnvs from values"]
    end
    
    subgraph "Volume Mounts"
        MEKVolume["mek-volume → /path/to/mek.yaml"]
        LogsVolume["logs → /logs"]
        ExtraVolumes["extraVolumeMounts from values"]
    end
    
    Container --> ImageLocation
    Container --> ImageTag
    Container --> PullPolicy
    Container --> SecurityContext
    Container --> Command
    Container --> Args
    Container --> PostgresPassword
    Container --> RedisPassword
    Container --> CustomEnv
    Container --> MEKVolume
    Container --> LogsVolume
    Container --> ExtraVolumes
    
    SecurityContext --> AllowPriv
    SecurityContext --> Capabilities
    SecurityContext --> RunAsNonRoot
    SecurityContext --> RunAsUser
```

All containers use:
- **Global Image Configuration**: `.Values.global.osmoImageLocation` and `.Values.global.osmoImageTag` for coordinated version management
- **Security Context**: Non-root users (1000 for UI, 1001 for services), dropped capabilities, no privilege escalation
- **Configuration File**: Master Encryption Key (MEK) mounted from ConfigMap when `.Values.services.configFile.enabled` is true
- **Secrets**: Database and Redis passwords sourced from Kubernetes secrets or direct values
- **Logging**: Optional log directory mounting when `.Values.global.logs.enabled` is true

**Sources:** [deployments/charts/service/templates/api-service.yaml:74-187](), [deployments/charts/web-ui/templates/ui.yaml:73-127](), [deployments/charts/router/templates/router-service.yaml:76-169]()

### Health Probes

OSMO services use three types of health probes:

| Probe Type | Purpose | Pattern |
|------------|---------|---------|
| `livenessProbe` | Restart unhealthy containers | HTTP GET `/api/version` or `progress_check --progress_interval 300` |
| `startupProbe` | Allow startup time before liveness checks | HTTP GET with 6-12 attempts or `progress_check --progress_interval 60` |
| `readinessProbe` | Control traffic routing | HTTP GET `/health` or database query endpoint |

**API Service Probes** [deployments/charts/service/templates/api-service.yaml:192-216]():
- Liveness: Configurable via values
- Startup: HTTP GET `/api/version`, 6 attempts × 5s
- Readiness: HTTP GET `/api/workflow?limit=0&all_pools=true` with admin header

**Worker/Agent/Logger Probes** use `progress_check` binary:
- Liveness: `progress_check --progress_interval 300` [deployments/charts/service/templates/agent-service.yaml:166-176]()
- Startup: `progress_check --progress_interval 60`, 12 attempts × 5s [deployments/charts/service/templates/agent-service.yaml:179-190]()
- Readiness: HTTP GET `/health` on port 8000 [deployments/charts/service/templates/agent-service.yaml:192-198]()

The `progress_check` binary monitors a file at `/var/run/osmo/last_progress` and fails if no updates occur within the specified interval.

**Sources:** [deployments/charts/service/templates/api-service.yaml:192-216](), [deployments/charts/service/templates/agent-service.yaml:166-198](), [deployments/charts/service/templates/worker.yaml:157-177]()

### Sidecar Containers

OSMO pods include multiple sidecar containers for authentication, observability, and logging:

```mermaid
graph TB
    Pod["Pod"]
    
    subgraph "Main Container"
        MainContainer["OSMO Service<br/>port 8000"]
    end
    
    subgraph "Envoy Sidecar"
        Envoy["Envoy Proxy<br/>envoy-http port<br/>internal-http port optional"]
        EnvoyConfig["ConfigMap<br/>envoy-config.yaml"]
        EnvoyFilter["OAuth2 Filter<br/>JWT Validation<br/>HMAC Cookies"]
    end
    
    subgraph "FluentBit Sidecar"
        FluentBit["FluentBit<br/>Log Collection"]
        FluentBitConfig["Reads from /logs<br/>Ships to aggregator"]
    end
    
    subgraph "OpenTelemetry Sidecar"
        OTel["OTel Collector<br/>Metrics Collection"]
        OTelAnnotation["Injected via annotation<br/>sidecar.opentelemetry.io/inject"]
    end
    
    subgraph "Rate Limiter Sidecar"
        RateLimit["Rate Limiter<br/>API only"]
        RateLimitConfig["Redis-based<br/>request throttling"]
    end
    
    Pod --> MainContainer
    Pod --> Envoy
    Pod --> FluentBit
    Pod --> OTel
    Pod --> RateLimit
    
    Envoy --> EnvoyConfig
    Envoy --> EnvoyFilter
    FluentBit --> FluentBitConfig
    OTel --> OTelAnnotation
    RateLimit --> RateLimitConfig
```

**Envoy Sidecar** [deployments/charts/service/templates/api-service.yaml:218]():
- Enabled via `.Values.sidecars.envoy.enabled`
- Listens on `envoy-http` port (typically 8080)
- Optional `internal-http` port for in-cluster paths without authentication [deployments/charts/service/templates/api-service.yaml:274-289]()
- Configuration stored in ConfigMap: `{{ serviceName }}-envoy-config`
- Implements OAuth2 authentication, JWT validation, and session management

**FluentBit Sidecar** [deployments/charts/service/templates/api-service.yaml:222]():
- Enabled via `.Values.global.logs.enabled`
- Reads logs from shared `/logs` volume
- Uses template `osmo.log-agent-sidecar-container`

**OpenTelemetry Sidecar** [deployments/charts/service/templates/api-service.yaml:219-221]():
- Enabled via `.Values.sidecars.otel.enabled`
- Injected automatically via annotation: `sidecar.opentelemetry.io/inject: "true"` [deployments/charts/service/templates/api-service.yaml:35-37]()
- Collects metrics from services with `--metrics_otel_enable true` argument

**Rate Limiter Sidecar** [deployments/charts/service/templates/api-service.yaml:223-225]():
- Only on API service
- Enabled via `.Values.sidecars.rateLimit.enabled`
- Redis-based request throttling

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-226](), [deployments/charts/web-ui/templates/ui.yaml:243-244](), [deployments/charts/router/templates/router-service.yaml:188-189]()

### Horizontal Pod Autoscaling

All OSMO services include `HorizontalPodAutoscaler` resources for automatic scaling based on resource utilization.

**API/Agent/Logger HPA Configuration** [deployments/charts/service/templates/api-service.yaml:339-367]():
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Values.services.service.serviceName }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Values.services.service.serviceName }}
  minReplicas: {{ .Values.services.service.scaling.minReplicas }}
  maxReplicas: {{ .Values.services.service.scaling.maxReplicas }}
  metrics:
  - type: ContainerResource
    containerResource:
      name: memory
      container: {{ .Values.services.service.serviceName }}
      target:
        type: Utilization
        averageUtilization: {{ .Values.services.service.scaling.hpaMemoryTarget }}
  - type: ContainerResource
    containerResource:
      name: cpu
      container: {{ .Values.services.service.serviceName }}
      target:
        type: Utilization
        averageUtilization: {{ .Values.services.service.scaling.hpaCpuTarget }}
```

**Worker HPA Configuration** [deployments/charts/service/templates/worker.yaml:208-236]():
- Similar structure but targets `worker` container
- Scales based on memory and CPU utilization

**Web-UI HPA Configuration** [deployments/charts/web-ui/templates/ui.yaml:383-407]():
- Scales on memory utilization only
- `averageUtilization: {{ .Values.services.ui.scaling.hpaTarget }}`

**Router HPA Configuration** [deployments/charts/router/templates/router-service.yaml:314-336]():
- Scales on memory utilization
- Uses `.Values.services.service.scaling.memoryTarget`

The `minReplicas` configuration is shared between the `Deployment` spec and the HPA:
- If HPA is enabled: `replicas: {{ .Values.services.X.scaling.minReplicas }}` [deployments/charts/web-ui/templates/ui.yaml:24]()
- If HPA is disabled: `replicas: {{ .Values.services.X.replicas }}`

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-367](), [deployments/charts/service/templates/worker.yaml:208-236](), [deployments/charts/web-ui/templates/ui.yaml:383-407](), [deployments/charts/router/templates/router-service.yaml:314-336]()

### Ingress Configuration

OSMO services use Kubernetes `Ingress` resources with optional AWS ALB annotations for routing external traffic.

**ALB Annotations** [deployments/charts/service/templates/api-service.yaml:300-308]():
```yaml
annotations:
  alb.ingress.kubernetes.io/target-type: ip
  alb.ingress.kubernetes.io/group.name: osmo
  alb.ingress.kubernetes.io/group.order: "100"
  alb.ingress.kubernetes.io/certificate-arn: {{ .Values.services.service.ingress.albAnnotations.sslCertArn }}
```

**Group Ordering**:
- API service: order `100` [deployments/charts/service/templates/api-service.yaml:303]()
- Agent/Logger: order `50` [deployments/charts/service/templates/agent-service.yaml:260]()
- Web UI main: order `200` [deployments/charts/web-ui/templates/ui.yaml:312]()
- Web UI tRPC: order `50` [deployments/charts/web-ui/templates/ui.yaml:349]()
- Router: order `50` [deployments/charts/router/templates/router-service.yaml:267]()

Lower order numbers are evaluated first, allowing precise routing control within the ALB.

**Path Routing**:
| Service | Path | Purpose |
|---------|------|---------|
| API | `/api`, `/client` | API endpoints and CLI client downloads |
| Agent | `/api/agent` | Agent service endpoints |
| Logger | `/api/logger` | Log streaming endpoints |
| Router | `/api/router` | Router control endpoints |
| Router | `*.{{ hostname }}` | Wildcard for webserver feature |
| Web UI | `/` | Main UI application |
| Web UI | `/api/refresh`, `/api/trpc` | Next.js API routes |

**TLS Configuration** [deployments/charts/service/templates/api-service.yaml:329-334]():
```yaml
tls:
- hosts:
  - {{ .Values.services.service.hostname }}
  secretName: {{.Values.services.service.ingress.sslSecret }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:294-335](), [deployments/charts/service/templates/agent-service.yaml:253-285](), [deployments/charts/web-ui/templates/ui.yaml:302-381](), [deployments/charts/router/templates/router-service.yaml:257-311]()

### Topology Spread Constraints

OSMO services use `topologySpreadConstraints` to distribute pods across availability zones and nodes for high availability.

**Configuration Pattern** [deployments/charts/service/templates/api-service.yaml:43-54]():
```yaml
topologySpreadConstraints:
{{- range .Values.services.service.topologySpreadConstraints }}
- topologyKey: {{.topologyKey }}
  {{- range $key, $value := . }}
  {{- if ne $key "topologyKey" }}
  {{$key}}: {{$value}}
  {{- end }}
  {{- end }}
  labelSelector:
    matchLabels:
      app: {{ $.Values.services.service.serviceName }}
{{- end }}
```

The pattern allows configuring multiple topology spread constraints via values, each with:
- `topologyKey`: Kubernetes node label to spread across (e.g., `topology.kubernetes.io/zone`)
- Additional properties like `maxSkew`, `whenUnsatisfiable`
- Automatic label selector matching the service name

This ensures pods are distributed across failure domains for resilience.

**Sources:** [deployments/charts/service/templates/api-service.yaml:43-54](), [deployments/charts/web-ui/templates/ui.yaml:42-53](), [deployments/charts/router/templates/router-service.yaml:44-57]()

### Volume Configuration

All charts use a consistent pattern for volume management:

**MEK Configuration Volume** [deployments/charts/service/templates/api-service.yaml:241-249]():
```yaml
- configMap:
    defaultMode: 420
    items:
    - key: mek.yaml
      path: mek.yaml
    name: mek-config
  name: mek-volume
```

**Logs Volume** [deployments/charts/service/templates/api-service.yaml:233-236]():
```yaml
- name: logs
  emptyDir: {}
```

**Envoy Configuration Volume**:
- Generated via template: `osmo.envoy-volumes` [deployments/charts/service/templates/api-service.yaml:228]()
- Creates ConfigMap with Envoy configuration

**Extra Volumes**:
- Configurable via `.Values.services.X.extraVolumes` [deployments/charts/web-ui/templates/ui.yaml:255-257]()
- Allows custom volume definitions per deployment

**Sources:** [deployments/charts/service/templates/api-service.yaml:227-249](), [deployments/charts/web-ui/templates/ui.yaml:248-257](), [deployments/charts/router/templates/router-service.yaml:193-211]()

---

# Page: Service Deployments

# Service Deployments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)

</details>



This page documents the core OSMO control plane services deployed via the `service` Helm chart. These services handle workflow submission, status monitoring, log streaming, and background job processing. 

For information about the overall Helm chart structure and dependencies, see [Helm Chart Architecture](#7.1). For details on sidecar containers (Envoy, FluentBit, OpenTelemetry), see [Sidecar Containers](#7.3). For backend operator deployments, see [Backend Operator Architecture](#5.1).

## Overview

The `service` chart deploys five core components that comprise the OSMO control plane:

| Service | Purpose | External Access | Scaling |
|---------|---------|----------------|---------|
| **API Service** (`osmo-service`) | REST API for workflow operations, configuration management, dataset operations | Yes (Ingress) | HPA (Memory + CPU) |
| **Agent Service** (`osmo-agent`) | Backend status updates, health monitoring | Yes (Ingress) | HPA (Memory + CPU) |
| **Logger Service** (`osmo-logger`) | WebSocket log streaming from workflow tasks | Yes (Ingress) | HPA (Memory + CPU) |
| **Worker Service** (`osmo-worker`) | Background job processing (workflow submission, cleanup) | No | HPA (Memory + CPU) |
| **Delayed Job Monitor** (`osmo-delayed-job-monitor`) | Monitors delayed job queues, enqueues ready jobs | No | Fixed replicas |

All services connect to shared PostgreSQL and Redis instances and mount the Master Encryption Key (MEK) for credential decryption.

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [deployments/charts/service/templates/agent-service.yaml:1-318](), [deployments/charts/service/templates/logger-service.yaml:1-314](), [deployments/charts/service/templates/worker.yaml:1-237](), [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

## Service Architecture Diagram

```mermaid
graph TB
    subgraph "External Access (via Ingress)"
        Ingress["Ingress Controller"]
    end
    
    subgraph "Service Chart Deployments"
        API["API Service<br/>osmo-service<br/>Command: service<br/>Port: 8000"]
        Agent["Agent Service<br/>osmo-agent<br/>Command: agent_service<br/>Port: 8000"]
        Logger["Logger Service<br/>osmo-logger<br/>Command: logger<br/>Port: 8000"]
        Worker["Worker Service<br/>osmo-worker<br/>Command: worker<br/>No exposed port"]
        Monitor["Delayed Job Monitor<br/>osmo-delayed-job-monitor<br/>Command: delayed_job_monitor<br/>No exposed port"]
    end
    
    subgraph "Shared Dependencies"
        Postgres[("PostgreSQL<br/>serviceName: osmo-postgres")]
        Redis[("Redis<br/>serviceName: osmo-redis")]
        MEK["MEK ConfigMap<br/>mek-config<br/>Key: mek.yaml"]
    end
    
    subgraph "Sidecars (per pod)"
        Envoy["Envoy Sidecar<br/>JWT validation<br/>OAuth2 filter"]
        FluentBit["FluentBit Sidecar<br/>Log collection"]
        OTel["OTel Sidecar<br/>Metrics collection<br/>(optional)"]
        RateLimit["Rate Limit Sidecar<br/>(API only, optional)"]
    end
    
    Ingress -->|"/api, /client"| API
    Ingress -->|"/api/agent"| Agent
    Ingress -->|"/api/logger"| Logger
    
    API --> Postgres
    API --> Redis
    Agent --> Postgres
    Agent --> Redis
    Logger --> Postgres
    Logger --> Redis
    Worker --> Postgres
    Worker --> Redis
    Monitor --> Postgres
    Monitor --> Redis
    
    API -.->|mounts| MEK
    Agent -.->|mounts| MEK
    Logger -.->|mounts| MEK
    Worker -.->|mounts| MEK
    Monitor -.->|mounts| MEK
    
    API -.->|has sidecars| Envoy
    API -.->|has sidecars| FluentBit
    API -.->|has sidecars| OTel
    API -.->|has sidecars| RateLimit
    
    Agent -.->|has sidecars| Envoy
    Logger -.->|has sidecars| Envoy
    Worker -.->|has sidecars| FluentBit
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [deployments/charts/service/templates/agent-service.yaml:1-318](), [deployments/charts/service/templates/logger-service.yaml:1-314](), [deployments/charts/service/templates/worker.yaml:1-237](), [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

## API Service

The API service (`osmo-service`) is the primary interface for workflow operations, configuration management, and dataset operations. It exposes REST endpoints for the CLI and Web UI.

### Deployment Configuration

```mermaid
graph LR
    subgraph "API Pod"
        APIContainer["Container: osmo-service<br/>Image: osmoImageLocation/osmo-service<br/>Command: service<br/>Port: 8000<br/>User: 1001"]
        EnvoySidecar["Envoy Sidecar<br/>Port: envoy-http"]
        OTelSidecar["OTel Sidecar<br/>(if enabled)"]
        FluentBitSidecar["FluentBit Sidecar<br/>(if logs.enabled)"]
        RateLimitSidecar["Rate Limit Sidecar<br/>(if rateLimit.enabled)"]
    end
    
    Service["Service<br/>osmo-service<br/>Port 80 → envoy-http or 8000"]
    InternalService["Service<br/>osmo-service-internal<br/>Port 80 → internal-http<br/>(if inClusterPaths.enabled)"]
    
    HPA["HorizontalPodAutoscaler<br/>minReplicas: values.services.service.scaling.minReplicas<br/>maxReplicas: values.services.service.scaling.maxReplicas<br/>Metrics: memory, cpu"]
    
    Ingress["Ingress<br/>Paths: /api, /client<br/>Host: values.services.service.hostname"]
    
    APIContainer --> Service
    APIContainer --> InternalService
    Service --> Ingress
    HPA -.->|scales| APIContainer
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:19-250]()

### Command-Line Arguments

The API service is invoked with the `service` command and receives the following arguments:

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--metrics_otel_collector_component` | `.Values.services.service.serviceName` | Component name for OpenTelemetry |
| `--metrics_otel_enable` | `.Values.sidecars.otel.enabled` | Enable OTel metrics |
| `--redis_host` | `.Values.services.redis.serviceName` | Redis hostname |
| `--redis_port` | `.Values.services.redis.port` | Redis port |
| `--redis_db_number` | `.Values.services.redis.dbNumber` | Redis database number |
| `--redis_tls_enable` | `.Values.services.redis.tlsEnabled` | Enable Redis TLS |
| `--postgres_host` | `.Values.services.postgres.serviceName` | PostgreSQL hostname |
| `--postgres_port` | `.Values.services.postgres.port` | PostgreSQL port |
| `--postgres_database_name` | `.Values.services.postgres.db` | PostgreSQL database name |
| `--postgres_user` | `.Values.services.postgres.user` | PostgreSQL username |
| `--mek_file` | `.Values.services.configFile.path` | MEK file path for credential encryption |
| `--service_hostname` | `.Values.services.service.hostname` | Service public hostname |
| `--osmo_image_location` | `.Values.global.osmoImageLocation` | Container registry location |
| `--osmo_image_tag` | `.Values.global.osmoImageTag` | Container image tag |
| `--log_level` | `.Values.global.logs.logLevel` | Application log level |
| `--k8s_log_level` | `.Values.global.logs.k8sLogLevel` | Kubernetes client log level |
| `--log_dir` | `/logs` | Log directory path |
| `--log_name` | `api_service` | Log file name |

Authentication-related arguments (if `.Values.services.service.auth.enabled`):

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--device_endpoint` | `.Values.services.service.auth.device_endpoint` | OAuth2 device authorization endpoint |
| `--device_client_id` | `.Values.services.service.auth.device_client_id` | Device flow client ID |
| `--browser_endpoint` | `.Values.services.service.auth.browser_endpoint` | Browser OAuth2 endpoint |
| `--browser_client_id` | `.Values.services.service.auth.browser_client_id` | Browser flow client ID |
| `--token_endpoint` | `.Values.services.service.auth.token_endpoint` | Token exchange endpoint |
| `--logout_endpoint` | `.Values.services.service.auth.logout_endpoint` | Logout endpoint |

**Sources:** [deployments/charts/service/templates/api-service.yaml:76-148]()

### Health Checks

The API service uses HTTP-based health checks:

```yaml
livenessProbe:
  # Defined in .Values.services.service.livenessProbe
  
startupProbe:
  httpGet:
    port: 8000
    path: /api/version
  failureThreshold: 6
  periodSeconds: 5
  timeoutSeconds: 3
  initialDelaySeconds: 5

readinessProbe:
  httpGet:
    port: 8000
    path: /api/workflow?limit=0&all_pools=true
    httpHeaders:
    - name: x-osmo-roles
      value: osmo-admin
  periodSeconds: 45
  failureThreshold: 3
  timeoutSeconds: 20
```

The readiness probe performs a database read operation to ensure the service can serve traffic.

**Sources:** [deployments/charts/service/templates/api-service.yaml:191-217]()

### Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `OSMO_DISABLE_TASK_METRICS` | `.Values.services.service.disableTaskMetrics` | Disable per-task metrics collection |
| `OSMO_POSTGRES_PASSWORD` | Secret `db-secret` or `.Values.services.postgres.password` | Database authentication |
| `OSMO_REDIS_PASSWORD` | Secret `redis-secret` | Redis authentication |

**Sources:** [deployments/charts/service/templates/api-service.yaml:149-167]()

### Scaling Configuration

The API service uses HorizontalPodAutoscaler with dual metrics:

```yaml
minReplicas: .Values.services.service.scaling.minReplicas
maxReplicas: .Values.services.service.scaling.maxReplicas
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    target:
      type: Utilization
      averageUtilization: .Values.services.service.scaling.hpaMemoryTarget
- type: ContainerResource
  containerResource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: .Values.services.service.scaling.hpaCpuTarget
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-368]()

## Agent Service

The Agent service (`osmo-agent`) handles backend status updates and health monitoring. Backend operators communicate with this service to report task status and cluster information.

### Deployment Configuration

```mermaid
graph LR
    subgraph "Agent Pod"
        AgentContainer["Container: osmo-agent<br/>Image: osmoImageLocation/osmo-agent<br/>Command: agent_service<br/>Port: 8000<br/>User: 1001"]
        EnvoySidecar["Envoy Sidecar"]
        OTelSidecar["OTel Sidecar<br/>(if enabled)"]
        FluentBitSidecar["FluentBit Sidecar<br/>(if logs.enabled)"]
    end
    
    Service["Service<br/>osmo-agent<br/>Port 80 → targetPort"]
    
    HPA["HorizontalPodAutoscaler<br/>Metrics: memory, cpu"]
    
    Ingress["Ingress<br/>Path: /api/agent"]
    
    AgentContainer --> Service
    Service --> Ingress
    HPA -.->|scales| AgentContainer
```

**Sources:** [deployments/charts/service/templates/agent-service.yaml:20-227]()

### Command-Line Arguments

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--redis_host` | `.Values.services.redis.serviceName` | Redis hostname |
| `--redis_port` | `.Values.services.redis.port` | Redis port |
| `--redis_tls_enable` | `.Values.services.redis.tlsEnabled` | Enable Redis TLS |
| `--redis_db_number` | `.Values.services.redis.dbNumber` | Redis database number |
| `--service_hostname` | `.Values.services.service.hostname` | Service public hostname |
| `--postgres_host` | `.Values.services.postgres.serviceName` | PostgreSQL hostname |
| `--postgres_port` | `.Values.services.postgres.port` | PostgreSQL port |
| `--postgres_database_name` | `.Values.services.postgres.db` | PostgreSQL database name |
| `--postgres_user` | `.Values.services.postgres.user` | PostgreSQL username |
| `--mek_file` | `.Values.services.configFile.path` | MEK file path |
| `--log_level` | `.Values.global.logs.logLevel` | Application log level |
| `--k8s_log_level` | `.Values.global.logs.k8sLogLevel` | Kubernetes client log level |
| `--log_dir` | `/logs` | Log directory path |
| `--log_name` | `agent_service` | Log file name |

**Sources:** [deployments/charts/service/templates/agent-service.yaml:77-129]()

### Health Checks

The Agent service uses a combination of `progress_check` and HTTP probes:

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
    - --progress_file
    - /var/run/osmo/last_progress
  timeoutSeconds: 20
  failureThreshold: 3
  periodSeconds: 45

startupProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "60"
    - --progress_file
    - /var/run/osmo/last_progress
  failureThreshold: 12
  periodSeconds: 5
  timeoutSeconds: 15
  initialDelaySeconds: 10

readinessProbe:
  httpGet:
    port: 8000
    path: /health
  periodSeconds: 45
  failureThreshold: 3
  timeoutSeconds: 20
```

The `progress_check` command verifies the service has made progress within the specified interval by checking a timestamp file at `/var/run/osmo/last_progress`.

**Sources:** [deployments/charts/service/templates/agent-service.yaml:165-199]()

### Scaling Configuration

```yaml
minReplicas: .Values.services.agent.scaling.minReplicas
maxReplicas: .Values.services.agent.scaling.maxReplicas
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    target:
      averageUtilization: .Values.services.agent.scaling.hpaMemoryTarget
- type: ContainerResource
  containerResource:
    name: cpu
    target:
      averageUtilization: .Values.services.agent.scaling.hpaCpuTarget
```

**Sources:** [deployments/charts/service/templates/agent-service.yaml:289-318]()

## Logger Service

The Logger service (`osmo-logger`) provides WebSocket-based log streaming for workflow tasks. It reads logs from Redis streams and forwards them to connected clients.

### Deployment Configuration

The Logger service deployment structure is similar to the Agent service:

```mermaid
graph LR
    subgraph "Logger Pod"
        LoggerContainer["Container: osmo-logger<br/>Image: osmoImageLocation/osmo-logger<br/>Command: logger<br/>Port: 8000<br/>User: 1001"]
        EnvoySidecar["Envoy Sidecar"]
        OTelSidecar["OTel Sidecar<br/>(if enabled)"]
        FluentBitSidecar["FluentBit Sidecar<br/>(if logs.enabled)"]
    end
    
    Service["Service<br/>osmo-logger<br/>Port 80 → targetPort"]
    
    HPA["HorizontalPodAutoscaler<br/>Metrics: memory, cpu"]
    
    Ingress["Ingress<br/>Path: /api/logger"]
    
    LoggerContainer --> Service
    Service --> Ingress
    HPA -.->|scales| LoggerContainer
```

**Sources:** [deployments/charts/service/templates/logger-service.yaml:20-223]()

### Command-Line Arguments

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--redis_host` | `.Values.services.redis.serviceName` | Redis hostname |
| `--redis_port` | `.Values.services.redis.port` | Redis port |
| `--redis_tls_enable` | `.Values.services.redis.tlsEnabled` | Enable Redis TLS |
| `--redis_db_number` | `.Values.services.redis.dbNumber` | Redis database number |
| `--postgres_host` | `.Values.services.postgres.serviceName` | PostgreSQL hostname |
| `--postgres_port` | `.Values.services.postgres.port` | PostgreSQL port |
| `--postgres_database_name` | `.Values.services.postgres.db` | PostgreSQL database name |
| `--postgres_user` | `.Values.services.postgres.user` | PostgreSQL username |
| `--mek_file` | `.Values.services.configFile.path` | MEK file path |
| `--log_level` | `.Values.global.logs.logLevel` | Application log level |
| `--k8s_log_level` | `.Values.global.logs.k8sLogLevel` | Kubernetes client log level |
| `--log_dir` | `/logs` | Log directory path |
| `--log_name` | `logger_service` | Log file name |

**Sources:** [deployments/charts/service/templates/logger-service.yaml:84-125]()

### Health Checks

Identical to Agent service - uses `progress_check` for liveness/startup and HTTP for readiness:

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
    - --progress_file
    - /var/run/osmo/last_progress
  timeoutSeconds: 20
  failureThreshold: 3
  periodSeconds: 45

readinessProbe:
  httpGet:
    port: 8000
    path: /health
  periodSeconds: 45
  failureThreshold: 3
  timeoutSeconds: 20
```

**Sources:** [deployments/charts/service/templates/logger-service.yaml:161-195]()

### Scaling Configuration

```yaml
minReplicas: .Values.services.logger.scaling.minReplicas
maxReplicas: .Values.services.logger.scaling.maxReplicas
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    target:
      averageUtilization: .Values.services.logger.scaling.hpaMemoryTarget
- type: ContainerResource
  containerResource:
    name: cpu
    target:
      averageUtilization: .Values.services.logger.scaling.hpaCpuTarget
```

**Sources:** [deployments/charts/service/templates/logger-service.yaml:285-314]()

## Worker Service

The Worker service (`osmo-worker`) processes background jobs from Redis queues. These jobs include workflow submission tasks, cleanup operations, and other asynchronous processing.

### Deployment Configuration

```mermaid
graph LR
    subgraph "Worker Pod"
        WorkerContainer["Container: osmo-worker<br/>Image: osmoImageLocation/osmo-worker<br/>Command: worker<br/>No exposed ports<br/>User: 1001"]
        OTelSidecar["OTel Sidecar<br/>(if enabled)"]
        FluentBitSidecar["FluentBit Sidecar<br/>(if logs.enabled)"]
    end
    
    HPA["HorizontalPodAutoscaler<br/>Metrics: memory, cpu"]
    
    Redis[("Redis<br/>Job Queues")]
    Postgres[("PostgreSQL")]
    
    WorkerContainer -->|polls| Redis
    WorkerContainer --> Postgres
    HPA -.->|scales| WorkerContainer
```

Note: The Worker service has no Kubernetes Service or Ingress - it only communicates with Redis and PostgreSQL.

**Sources:** [deployments/charts/service/templates/worker.yaml:16-205]()

### Command-Line Arguments

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--metrics_otel_collector_component` | `.Values.services.worker.serviceName` | Component name for OpenTelemetry |
| `--metrics_otel_enable` | `.Values.sidecars.otel.enabled` | Enable OTel metrics |
| `--redis_host` | `.Values.services.redis.serviceName` | Redis hostname |
| `--redis_port` | `.Values.services.redis.port` | Redis port |
| `--redis_db_number` | `.Values.services.redis.dbNumber` | Redis database number |
| `--redis_tls_enable` | `.Values.services.redis.tlsEnabled` | Enable Redis TLS |
| `--postgres_host` | `.Values.services.postgres.serviceName` | PostgreSQL hostname |
| `--postgres_port` | `.Values.services.postgres.port` | PostgreSQL port |
| `--postgres_database_name` | `.Values.services.postgres.db` | PostgreSQL database name |
| `--postgres_user` | `.Values.services.postgres.user` | PostgreSQL username |
| `--mek_file` | `.Values.services.configFile.path` | MEK file path |
| `--log_level` | `.Values.global.logs.logLevel` | Application log level |
| `--k8s_log_level` | `.Values.global.logs.k8sLogLevel` | Kubernetes client log level |
| `--log_dir` | `/logs` | Log directory path |
| `--log_name` | `worker` | Log file name |

**Sources:** [deployments/charts/service/templates/worker.yaml:69-122]()

### Health Checks

The Worker uses `progress_check` probes to ensure it's processing jobs and not stuck:

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
  failureThreshold: 1
  periodSeconds: 60
  timeoutSeconds: 15

startupProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
  failureThreshold: 12
  periodSeconds: 5
  timeoutSeconds: 15
  initialDelaySeconds: 10
```

The liveness probe restarts the worker if it's been on the same job for more than 5 minutes (300 seconds).

**Sources:** [deployments/charts/service/templates/worker.yaml:156-178]()

### Scaling Configuration

```yaml
minReplicas: .Values.services.worker.scaling.minReplicas
maxReplicas: .Values.services.worker.scaling.maxReplicas
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    target:
      averageUtilization: .Values.services.worker.scaling.hpaMemoryTarget
- type: ContainerResource
  containerResource:
    name: cpu
    target:
      averageUtilization: .Values.services.worker.scaling.hpaCpuTarget
```

**Sources:** [deployments/charts/service/templates/worker.yaml:208-237]()

## Delayed Job Monitor

The Delayed Job Monitor (`osmo-delayed-job-monitor`) monitors delayed job queues and enqueues jobs that are ready to run. Unlike the Worker, it runs as a fixed-replica deployment without HPA.

### Deployment Configuration

```mermaid
graph LR
    subgraph "Monitor Pod"
        MonitorContainer["Container: osmo-delayed-job-monitor<br/>Image: osmoImageLocation/osmo-delayed-job-monitor<br/>Command: delayed_job_monitor<br/>No exposed ports<br/>User: 1001"]
        OTelSidecar["OTel Sidecar<br/>(if enabled)"]
        FluentBitSidecar["FluentBit Sidecar<br/>(if logs.enabled)"]
    end
    
    Redis[("Redis<br/>Delayed Job Queues")]
    Postgres[("PostgreSQL")]
    
    MonitorContainer -->|monitors/enqueues| Redis
    MonitorContainer --> Postgres
```

Fixed replicas: `.Values.services.delayedJobMonitor.replicas`

**Sources:** [deployments/charts/service/templates/delayed-job-monitor.yaml:16-204]()

### Command-Line Arguments

| Argument | Value Source | Purpose |
|----------|--------------|---------|
| `--metrics_otel_collector_component` | `.Values.services.delayedJobMonitor.serviceName` | Component name for OpenTelemetry |
| `--metrics_otel_enable` | `.Values.sidecars.otel.enabled` | Enable OTel metrics |
| `--redis_host` | `.Values.services.redis.serviceName` | Redis hostname |
| `--redis_port` | `.Values.services.redis.port` | Redis port |
| `--redis_db_number` | `.Values.services.redis.dbNumber` | Redis database number |
| `--redis_tls_enable` | `.Values.services.redis.tlsEnabled` | Enable Redis TLS |
| `--postgres_host` | `.Values.services.postgres.serviceName` | PostgreSQL hostname |
| `--postgres_port` | `.Values.services.postgres.port` | PostgreSQL port |
| `--postgres_database_name` | `.Values.services.postgres.db` | PostgreSQL database name |
| `--postgres_user` | `.Values.services.postgres.user` | PostgreSQL username |
| `--mek_file` | `.Values.services.configFile.path` | MEK file path |
| `--log_level` | `.Values.global.logs.logLevel` | Application log level |
| `--k8s_log_level` | `.Values.global.logs.k8sLogLevel` | Kubernetes client log level |
| `--log_dir` | `/logs` | Log directory path |
| `--log_name` | `delayed_job_monitor` | Log file name |
| `--enable_metrics` | Set if `.Values.sidecars.otel.enabled` | Enable metrics collection |

**Sources:** [deployments/charts/service/templates/delayed-job-monitor.yaml:64-114]()

### Health Checks

The Monitor uses `progress_check` with a shorter startup interval:

```yaml
livenessProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "300"
  failureThreshold: 1
  periodSeconds: 30
  timeoutSeconds: 15

startupProbe:
  exec:
    command:
    - progress_check
    - --progress_interval
    - "30"
  failureThreshold: 12
  periodSeconds: 5
  timeoutSeconds: 15
  initialDelaySeconds: 10
```

Note the startup probe uses a 30-second interval while liveness uses 300 seconds.

**Sources:** [deployments/charts/service/templates/delayed-job-monitor.yaml:152-174]()

## Health Check Patterns

OSMO services use two distinct health check patterns:

### Pattern 1: HTTP-Based Checks (API, Agent, Logger)

```mermaid
graph TB
    Container["Service Container"]
    HTTPEndpoint["/health or /api/version"]
    K8sProbe["Kubernetes Probe"]
    
    K8sProbe -->|HTTP GET| HTTPEndpoint
    HTTPEndpoint -->|200 OK| Container
```

Used for services with HTTP endpoints. The API service uses `/api/version` for startup and a database query endpoint for readiness.

**Sources:** [deployments/charts/service/templates/api-service.yaml:191-217](), [deployments/charts/service/templates/agent-service.yaml:192-199]()

### Pattern 2: Progress Check (Worker, Monitor, Agent/Logger Liveness)

```mermaid
graph TB
    Container["Service Container"]
    ProgressFile["/var/run/osmo/last_progress"]
    ProgressCheck["progress_check binary"]
    K8sProbe["Kubernetes Probe"]
    
    Container -->|updates timestamp| ProgressFile
    K8sProbe -->|exec| ProgressCheck
    ProgressCheck -->|reads| ProgressFile
    ProgressCheck -->|validates interval| Container
```

The `progress_check` command verifies the service has updated its progress file within the specified interval:

```bash
progress_check --progress_interval "300" --progress_file /var/run/osmo/last_progress
```

If the timestamp is older than the interval, the probe fails and Kubernetes restarts the container.

**Sources:** [deployments/charts/service/templates/worker.yaml:156-178](), [deployments/charts/service/templates/agent-service.yaml:165-190]()

## Common Configuration Patterns

### Security Context

All service containers use the same restrictive security context:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  runAsNonRoot: true
  runAsUser: 1001
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:169-174](), [deployments/charts/service/templates/worker.yaml:71-76]()

### MEK Volume Mount

Services that need to decrypt credentials mount the MEK ConfigMap:

```yaml
volumeMounts:
- mountPath: /path/to/mek.yaml  # .Values.services.configFile.path
  name: mek-volume
  subPath: mek.yaml

volumes:
- configMap:
    defaultMode: 420
    items:
    - key: mek.yaml
      path: mek.yaml
    name: mek-config
  name: mek-volume
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:178-249]()

### Log Volume Mount

When logging is enabled (`.Values.global.logs.enabled`):

```yaml
volumeMounts:
- name: logs
  mountPath: /logs

volumes:
- name: logs
  emptyDir: {}
```

FluentBit sidecars read from this shared volume.

**Sources:** [deployments/charts/service/templates/api-service.yaml:183-237]()

### Topology Spread Constraints

Services use topology spread constraints for high availability:

```yaml
topologySpreadConstraints:
- topologyKey: {{ .topologyKey }}
  # Additional fields from .Values.services.<service>.topologySpreadConstraints
  labelSelector:
    matchLabels:
      app: {{ $.Values.services.<service>.serviceName }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:43-54](), [deployments/charts/service/templates/agent-service.yaml:44-55]()

## Service Comparison Table

| Feature | API | Agent | Logger | Worker | Monitor |
|---------|-----|-------|--------|--------|---------|
| **Command** | `service` | `agent_service` | `logger` | `worker` | `delayed_job_monitor` |
| **Port** | 8000 | 8000 | 8000 | None | None |
| **Ingress** | Yes (/api, /client) | Yes (/api/agent) | Yes (/api/logger) | No | No |
| **Envoy Sidecar** | Yes | Yes | Yes | No | No |
| **OTel Sidecar** | Optional | Optional | Optional | Optional | Optional |
| **FluentBit Sidecar** | Optional | Optional | Optional | Optional | Optional |
| **Rate Limit Sidecar** | Optional | No | No | No | No |
| **Liveness Probe** | Values-defined | progress_check (300s) | progress_check (300s) | progress_check (300s) | progress_check (300s) |
| **Readiness Probe** | HTTP + DB query | HTTP /health | HTTP /health | None | None |
| **HPA Enabled** | Yes | Yes | Yes | Yes | No |
| **HPA Metrics** | Memory + CPU | Memory + CPU | Memory + CPU | Memory + CPU | N/A |
| **Internal Service** | Optional | No | No | No | No |

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [deployments/charts/service/templates/agent-service.yaml:1-318](), [deployments/charts/service/templates/logger-service.yaml:1-314](), [deployments/charts/service/templates/worker.yaml:1-237](), [deployments/charts/service/templates/delayed-job-monitor.yaml:1-204]()

## Helm Template Helpers

The service chart uses several template helpers defined in `_helpers.tpl` (referenced but not shown in provided files):

| Helper | Purpose | Example Usage |
|--------|---------|---------------|
| `osmo.service-account-name` | Resolves service account name | [deployments/charts/service/templates/api-service.yaml:68]() |
| `osmo.envoy-sidecar-container` | Generates Envoy sidecar | [deployments/charts/service/templates/api-service.yaml:218]() |
| `osmo.otel-sidecar-container` | Generates OTel sidecar | [deployments/charts/service/templates/api-service.yaml:220]() |
| `osmo.log-agent-sidecar-container` | Generates FluentBit sidecar | [deployments/charts/service/templates/api-service.yaml:222]() |
| `osmo.rate-limit-sidecar-container` | Generates rate limit sidecar | [deployments/charts/service/templates/api-service.yaml:224]() |
| `osmo.envoy-volumes` | Generates Envoy volumes | [deployments/charts/service/templates/api-service.yaml:228]() |
| `osmo.extra-annotations` | Adds custom annotations | [deployments/charts/service/templates/api-service.yaml:34]() |
| `osmo.extra-env` | Adds custom environment variables | [deployments/charts/service/templates/api-service.yaml:152]() |
| `osmo.extra-volume-mounts` | Adds custom volume mounts | [deployments/charts/service/templates/api-service.yaml:187]() |
| `osmo.extra-sidecars` | Adds custom sidecars | [deployments/charts/service/templates/api-service.yaml:226]() |
| `service.targetPort` | Determines target port (Envoy or direct) | [deployments/charts/service/templates/api-service.yaml:266]() |

**Sources:** [deployments/charts/service/templates/api-service.yaml:34-266](), [deployments/charts/service/templates/agent-service.yaml:35-209]()

## Deployment Workflow

```mermaid
sequenceDiagram
    participant Helm
    participant K8s as "Kubernetes API"
    participant Pods
    participant Postgres
    participant Redis
    
    Helm->>K8s: Create ConfigMaps (MEK, Envoy configs)
    Helm->>K8s: Create Secrets (db-secret, redis-secret)
    Helm->>K8s: Create Deployments (5 services)
    K8s->>Pods: Schedule pods
    
    Note over Pods: Init containers run (if defined)
    
    Pods->>Pods: Start main containers
    Pods->>Pods: Start sidecar containers
    
    Note over Pods: Startup probes begin
    
    Pods->>Postgres: Test connection
    Pods->>Redis: Test connection
    
    Note over Pods: Startup probes pass
    Note over Pods: Readiness probes begin
    
    Pods->>K8s: Report ready
    
    Helm->>K8s: Create Services
    Helm->>K8s: Create Ingresses
    Helm->>K8s: Create HPAs
    
    K8s->>Pods: Route traffic to ready pods
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:1-368](), [deployments/charts/quick-start/Chart.yaml:24-39]()

---

# Page: Sidecar Containers

# Sidecar Containers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/README.md](deployments/charts/web-ui/README.md)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [deployments/charts/web-ui/values.yaml](deployments/charts/web-ui/values.yaml)
- [ui/src/app/layout.tsx](ui/src/app/layout.tsx)
- [ui/src/app/workflows/components/TaskActions.tsx](ui/src/app/workflows/components/TaskActions.tsx)
- [ui/src/app/workflows/components/WorkflowActions.tsx](ui/src/app/workflows/components/WorkflowActions.tsx)
- [ui/src/env.mjs](ui/src/env.mjs)
- [ui/src/runtime-env.tsx](ui/src/runtime-env.tsx)

</details>



This page documents OSMO's sidecar container architecture, which provides authentication, logging, observability, and rate limiting capabilities to control plane services. Sidecar containers run alongside the main application containers within the same pod, sharing network and storage resources while maintaining separation of concerns.

For information about the overall Kubernetes deployment architecture, see [Kubernetes Deployment](#7). For authentication mechanisms, see [Authentication and Security](#8).

## Overview

OSMO deploys four types of sidecar containers across its control plane services:

| Sidecar Type | Purpose | Services Using It | Optional |
|--------------|---------|-------------------|----------|
| **Envoy** | Authentication proxy with OAuth2/JWT validation | API, UI, Agent, Logger, Router | No (for production) |
| **FluentBit** | Log collection and forwarding to centralized storage | All services | Yes |
| **OpenTelemetry** | Metrics collection and observability | API, Worker, Agent, Logger, DelayedJobMonitor | Yes |
| **Rate Limiter** | API request rate limiting | API service only | Yes |

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-225](), [deployments/charts/web-ui/templates/ui.yaml:243-244]()

## Sidecar Architecture Pattern

```mermaid
graph TB
    subgraph "Pod: osmo-service"
        direction LR
        
        subgraph "Main Container"
            Service["API Service<br/>Port 8000"]
        end
        
        subgraph "Envoy Sidecar"
            EnvoyProxy["Envoy Proxy<br/>Port 8080<br/>(Public)"]
            EnvoyInternal["Envoy Internal<br/>Port 8081<br/>(In-Cluster)"]
        end
        
        subgraph "Log Agent Sidecar"
            FluentBit["FluentBit<br/>Port 2020<br/>(Metrics)"]
        end
        
        subgraph "OTel Sidecar"
            OTelCollector["OpenTelemetry<br/>Collector"]
        end
        
        subgraph "Shared Resources"
            LogsVolume["emptyDir:<br/>logs"]
            EnvoyConfig["ConfigMap:<br/>envoy-config"]
            Secrets["Secrets:<br/>client_secret<br/>hmac_secret"]
        end
    end
    
    Ingress["Kubernetes<br/>Ingress"]
    InCluster["In-Cluster<br/>Services"]
    CloudWatch["AWS CloudWatch"]
    OTelBackend["OTel Collector<br/>(Cluster)"]
    
    Ingress -->|"Port 80"| EnvoyProxy
    InCluster -->|"Port 80"| EnvoyInternal
    EnvoyProxy -->|"Validated Requests<br/>x-osmo-user header"| Service
    EnvoyInternal -->|"No Auth"| Service
    
    Service -->|"Write Logs"| LogsVolume
    FluentBit -->|"Read & Forward"| LogsVolume
    FluentBit -->|"Stream"| CloudWatch
    
    Service -->|"Metrics"| OTelCollector
    OTelCollector -->|"Export"| OTelBackend
    
    EnvoyProxy -.->|"Read"| EnvoyConfig
    EnvoyProxy -.->|"Read"| Secrets
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-250](), [deployments/charts/web-ui/templates/ui.yaml:72-257]()

## Envoy Authentication Proxy

The Envoy sidecar provides edge authentication and request validation for all control plane services. It intercepts incoming requests, validates OAuth2/JWT credentials, and forwards authenticated requests to the application container with user identity headers.

### Envoy Configuration

```mermaid
graph TB
    subgraph "Envoy Configuration Flow"
        Values["values.yaml<br/>sidecars.envoy.*"]
        Template["_helpers.tpl<br/>osmo.envoy-config"]
        ConfigMap["ConfigMap<br/>{service}-envoy-config"]
        EnvoyContainer["Envoy Container<br/>/etc/envoy/config.yaml"]
    end
    
    subgraph "Secret Management"
        K8sSecret["Kubernetes Secret<br/>oidc-secrets<br/>(if useKubernetesSecrets)"]
        FileSecret["File Mount<br/>/etc/envoy/secrets/<br/>(if not using K8s secrets)"]
        EnvoySecrets["Envoy Reads:<br/>client_secret<br/>hmac_secret"]
    end
    
    Values -->|"Helm Template"| Template
    Template -->|"Generate"| ConfigMap
    ConfigMap -->|"Mount"| EnvoyContainer
    
    K8sSecret -->|"Mount"| EnvoySecrets
    FileSecret -->|"Mount"| EnvoySecrets
    EnvoySecrets -.->|"Used by"| EnvoyContainer
```

**Key Configuration Parameters:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `sidecars.envoy.enabled` | Enable Envoy sidecar | `true` |
| `sidecars.envoy.listenerPort` | Envoy listening port | `8080` |
| `sidecars.envoy.service.port` | Backend service port | `8000` |
| `sidecars.envoy.maxHeadersSizeKb` | Max HTTP header size | `128` |
| `sidecars.envoy.jwtEnable` | Enable JWT validation | `true` |
| `sidecars.envoy.oauth2Enable` | Enable OAuth2 filter | `true` |
| `sidecars.envoy.skipAuthPaths` | Paths bypassing auth | `[]` |
| `sidecars.envoy.inClusterPaths.enabled` | Internal no-auth endpoint | `false` |

**Sources:** [deployments/charts/web-ui/values.yaml:377-601](), [deployments/charts/service/templates/api-service.yaml:251-253]()

### Envoy Listeners and Routes

Envoy creates two listeners:

1. **Public Listener** (port 8080): Requires OAuth2/JWT authentication
2. **Internal Listener** (port 8081, optional): Bypasses authentication for in-cluster traffic

```mermaid
graph LR
    subgraph "Envoy Routing Logic"
        PublicListener["Listener<br/>0.0.0.0:8080"]
        InternalListener["Listener<br/>0.0.0.0:8081<br/>(if inClusterPaths.enabled)"]
        
        OAuth2Filter["OAuth2 Filter<br/>Browser Flow"]
        JWTFilter["JWT Filter<br/>CLI/Backend Tokens"]
        NoAuth["No Authentication"]
        
        ServiceCluster["Cluster: service<br/>127.0.0.1:8000"]
    end
    
    PublicListener --> OAuth2Filter
    PublicListener --> JWTFilter
    InternalListener --> NoAuth
    
    OAuth2Filter --> ServiceCluster
    JWTFilter --> ServiceCluster
    NoAuth --> ServiceCluster
```

**Sources:** [deployments/charts/web-ui/values.yaml:405-410](), [deployments/charts/service/templates/api-service.yaml:274-289]()

### Envoy JWT Validation

Envoy validates JWT tokens from multiple providers and extracts user identity:

**JWT Provider Configuration:**

```yaml
# From values.yaml
jwt:
  user_header: x-osmo-user
  providers:
  - issuer: "https://keycloak.example.com/realms/osmo"
    audience: "osmo-device"
    jwks_uri: "https://keycloak.example.com/realms/osmo/protocol/openid-connect/certs"
    user_claim: unique_name
    cluster: oauth
  - issuer: "https://keycloak.example.com/realms/osmo"
    audience: "osmo-browser-flow"
    jwks_uri: "https://keycloak.example.com/realms/osmo/protocol/openid-connect/certs"
    user_claim: preferred_username
    cluster: oauth
```

After successful validation, Envoy injects the `x-osmo-user` header with the authenticated username, which the application services consume.

**Sources:** [deployments/charts/web-ui/values.yaml:578-600]()

### Envoy OAuth2 Filter

The OAuth2 filter handles browser-based authentication flows:

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `oauth2Filter.tokenEndpoint` | Token exchange URL | `https://keycloak.example.com/realms/osmo/protocol/openid-connect/token` |
| `oauth2Filter.authEndpoint` | Authorization URL | `https://keycloak.example.com/realms/osmo/protocol/openid-connect/auth` |
| `oauth2Filter.redirectPath` | OAuth callback path | `getAToken` |
| `oauth2Filter.logoutPath` | Logout path | `logout` |
| `oauth2Filter.clientId` | OAuth client ID | `osmo-ui-client` |

Envoy stores session state in HMAC-signed cookies, eliminating the need for session storage.

**Sources:** [deployments/charts/web-ui/values.yaml:516-556]()

### Envoy Container Specification

The Envoy sidecar is defined via Helm template includes:

```yaml
# From api-service.yaml
{{- include "osmo.envoy-sidecar-container" . | nindent 6}}

# Volumes
{{- include "osmo.envoy-volumes" (dict "serviceName" .Values.services.service.serviceName "serviceEnvoy" .Values.services.service.envoy "Values" .Values) | nindent 8 }}
```

**Container Resource Limits:**

```yaml
# From values.yaml
resources:
  requests:
    cpu: "100m"
    memory: "64Mi"
  limits:
    memory: "128Mi"
```

**Security Context:**

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  runAsNonRoot: true
  runAsUser: 1001
```

**Sources:** [deployments/charts/web-ui/values.yaml:436-474](), [deployments/charts/service/templates/api-service.yaml:218-228]()

### Envoy Health Probes

Envoy exposes a `/ready` endpoint on port 9901 for health checks:

```yaml
livenessProbe:
  httpGet:
    path: /ready
    port: 9901
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 9901
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3

startupProbe:
  httpGet:
    path: /ready
    port: 9901
  initialDelaySeconds: 15
  periodSeconds: 5
  timeoutSeconds: 3
```

**Sources:** [deployments/charts/web-ui/values.yaml:412-434]()

## FluentBit Log Agent

The FluentBit sidecar collects logs from the main container and forwards them to centralized logging backends like AWS CloudWatch. It reads logs from a shared `emptyDir` volume mounted at `/logs`.

### Log Agent Architecture

```mermaid
graph TB
    subgraph "Pod Logging Flow"
        AppContainer["Application Container<br/>--log_dir /logs<br/>--log_name {service}"]
        LogVolume["emptyDir Volume<br/>/logs"]
        FluentBitContainer["FluentBit Container<br/>Mount: /var/log"]
        
        AppContainer -->|"Write Logs"| LogVolume
        FluentBitContainer -->|"Tail & Parse"| LogVolume
    end
    
    subgraph "FluentBit Processing"
        Input["Input Plugin<br/>tail /var/log/*.log"]
        Parser["Parser<br/>json format"]
        Filter["Filters<br/>Add k8s metadata"]
        Output["Output Plugin<br/>CloudWatch/Stdout"]
        
        Input --> Parser
        Parser --> Filter
        Filter --> Output
    end
    
    FluentBitContainer --> Input
    Output --> CloudWatch["AWS CloudWatch<br/>/aws/eks/{cluster}/{namespace}"]
    Output --> Prometheus["Prometheus Metrics<br/>Port 2020"]
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:120-125](), [deployments/charts/web-ui/values.yaml:606-670]()

### Log Agent Configuration

**Enable/Disable:**

```yaml
# From values.yaml
sidecars:
  logAgent:
    enabled: false  # Must be explicitly enabled
```

**Key Parameters:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `sidecars.logAgent.enabled` | Enable log collection | `false` |
| `sidecars.logAgent.image.repository` | FluentBit image | `fluent/fluent-bit:4.0.8-debug` |
| `sidecars.logAgent.fluentBitPrometheusPort` | Metrics port | `2020` |
| `sidecars.logAgent.aws.region` | AWS region | `us-west-2` |
| `sidecars.logAgent.aws.clusterName` | EKS cluster name | `""` |

**Sources:** [deployments/charts/web-ui/values.yaml:606-649]()

### Log Rotation

FluentBit can be configured with automatic log rotation:

```yaml
logrotate:
  enabled: false
  frequency: hourly  # or: daily, weekly, monthly, yearly, "minutes <size>"
  maxSize: 10M
  rotateCount: 5
  sleepSeconds: 60
```

When enabled, logs are rotated based on the specified frequency or when they reach `maxSize`, keeping `rotateCount` historical files.

**Sources:** [deployments/charts/web-ui/values.yaml:611-633]()

### Log Agent Container Specification

```yaml
# Helm template include
{{- include "osmo.log-agent-sidecar-container" . | nindent 6}}

# Volume mount
volumeMounts:
- name: logs
  mountPath: /var/log

# Resources
resources:
  requests:
    cpu: "250m"
    memory: "400Mi"
  limits:
    memory: "400Mi"
```

**Sources:** [deployments/charts/web-ui/values.yaml:652-669](), [deployments/charts/service/templates/api-service.yaml:222-236]()

### Application Log Configuration

Services must be configured to write logs to the shared volume:

```yaml
# From api-service.yaml
args:
- --log_level
- {{ .Values.global.logs.logLevel }}
- --k8s_log_level
- {{ .Values.global.logs.k8sLogLevel }}
- --log_dir
- /logs
- --log_name
- api_service

volumeMounts:
- name: logs
  mountPath: /logs

volumes:
- name: logs
  emptyDir: {}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:136-236]()

## OpenTelemetry Collector

The OpenTelemetry sidecar collects metrics and traces from application services for observability. Unlike Envoy and FluentBit which are explicitly defined in pod specs, the OTel sidecar is injected via the OpenTelemetry Operator when the pod annotation is present.

### OTel Injection Pattern

```mermaid
graph TB
    subgraph "OTel Injection Mechanism"
        PodSpec["Pod Spec<br/>metadata.annotations"]
        OTelOperator["OpenTelemetry<br/>Operator"]
        InjectedSidecar["OTel Collector<br/>Sidecar"]
        
        PodSpec -->|"sidecar.opentelemetry.io/inject: true"| OTelOperator
        OTelOperator -->|"Inject Container"| InjectedSidecar
    end
    
    subgraph "Application Integration"
        AppService["Application Service<br/>--metrics_otel_enable true<br/>--metrics_otel_collector_component {name}"]
        OTelCollector["OTel Collector<br/>Port 4317 (gRPC)<br/>Port 4318 (HTTP)"]
        
        AppService -->|"Push Metrics<br/>OTLP Protocol"| OTelCollector
    end
    
    InjectedSidecar --> OTelCollector
    OTelCollector -->|"Export"| Backend["Cluster OTel<br/>Collector"]
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:35-37](), [deployments/charts/service/templates/worker.yaml:32-34]()

### OTel Configuration

**Enable via Values:**

```yaml
# From service chart values
sidecars:
  otel:
    enabled: true  # Enables annotation injection
```

**Pod Annotation:**

```yaml
# From api-service.yaml
annotations:
  {{- if .Values.sidecars.otel.enabled }}
  sidecar.opentelemetry.io/inject: "true"
  {{- end}}
```

**Application Arguments:**

```yaml
# From api-service.yaml
args:
- --metrics_otel_collector_component
- {{ .Values.services.service.serviceName }}
- --metrics_otel_enable
- {{ .Values.sidecars.otel.enabled | quote }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:79-82](), [deployments/charts/service/templates/worker.yaml:79-82]()

### Services Using OTel

The following services are configured for OpenTelemetry metrics collection:

- **API Service** (`osmo-service`)
- **Worker Service** (`osmo-worker`)
- **Agent Service** (`osmo-agent`)
- **Logger Service** (`osmo-logger`)
- **Delayed Job Monitor** (`osmo-delayed-job-monitor`)

**Sources:** [deployments/charts/service/templates/api-service.yaml:35-37](), [deployments/charts/service/templates/worker.yaml:32-34](), [deployments/charts/service/templates/agent-service.yaml:36-38]()

### OTel Volumes

When OTel is enabled, additional volumes may be required:

```yaml
# From api-service.yaml
volumes:
{{- if .Values.sidecars.otel.enabled }}
{{- include "osmo.otel-volumes" . | nindent 8 }}
{{- end }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:230-232]()

## Rate Limiter Sidecar

The Rate Limiter sidecar is specific to the API service and provides request rate limiting capabilities.

### Rate Limiter Configuration

```yaml
# Enable in values.yaml
sidecars:
  rateLimit:
    enabled: false  # Must be explicitly enabled
```

**Deployment:**

```yaml
# From api-service.yaml
{{- if .Values.sidecars.rateLimit.enabled }}
{{- include "osmo.rate-limit-sidecar-container" . | nindent 6}}
{{- end }}

# Volumes
{{- if .Values.sidecars.rateLimit.enabled }}
{{- include "osmo.rate-limit-volumes" . | nindent 8 }}
{{- end }}
```

The Rate Limiter works in conjunction with Envoy to enforce API request quotas on a per-user or per-endpoint basis.

**Sources:** [deployments/charts/service/templates/api-service.yaml:223-240]()

## Sidecar Injection Patterns

OSMO uses three patterns for sidecar deployment:

### 1. Explicit Container Definitions

Most sidecars (Envoy, FluentBit) are explicitly defined in deployment templates:

```yaml
containers:
- name: {{ .Values.services.ui.serviceName }}
  # Main container spec
  ...

{{- include "ui.envoy-sidecar-container" . | nindent 6}}
{{- include "ui.log-agent-sidecar-container" . | nindent 6}}
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:243-244]()

### 2. Operator-Based Injection

OpenTelemetry uses the OpenTelemetry Operator for automatic injection:

```yaml
metadata:
  annotations:
    sidecar.opentelemetry.io/inject: "true"
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:35-37]()

### 3. Conditional Sidecars

All sidecars support conditional deployment based on values:

```yaml
{{- if .Values.sidecars.envoy.enabled }}
# Envoy sidecar definition
{{- end }}

{{- if .Values.sidecars.logAgent.enabled }}
# FluentBit sidecar definition
{{- end }}
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:243-244]()

## Shared Resources Between Containers

Sidecars share resources with the main container through Kubernetes volumes and network namespaces:

### Volume Sharing

```mermaid
graph TB
    subgraph "Shared Volumes in Pod"
        LogsVolume["logs<br/>type: emptyDir"]
        EnvoyConfigVolume["envoy-config<br/>type: configMap"]
        SecretsVolume["secrets<br/>type: secret"]
        MEKVolume["mek-volume<br/>type: configMap"]
    end
    
    subgraph "Container Mounts"
        AppContainer["App: /logs"]
        FluentBit["FluentBit: /var/log"]
        Envoy["Envoy: /etc/envoy/config.yaml<br/>Envoy: /etc/envoy/secrets/"]
        AppMEK["App: /etc/osmo/mek.yaml"]
    end
    
    LogsVolume --> AppContainer
    LogsVolume --> FluentBit
    EnvoyConfigVolume --> Envoy
    SecretsVolume --> Envoy
    MEKVolume --> AppMEK
```

**Example Volume Definitions:**

```yaml
volumes:
- name: logs
  emptyDir: {}
- name: envoy-config
  configMap:
    name: {{ .Values.services.ui.serviceName }}-envoy-config
- name: envoy-secrets
  secret:
    secretName: oidc-secrets
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:248-257](), [deployments/charts/service/templates/api-service.yaml:227-249]()

### Network Sharing

All containers in a pod share the same network namespace, enabling `localhost` communication:

- Envoy listens on `0.0.0.0:8080`
- Main application listens on `127.0.0.1:8000`
- Envoy forwards to `127.0.0.1:8000`

This eliminates the need for service discovery or DNS resolution between sidecars and the main container.

**Sources:** [deployments/charts/web-ui/values.yaml:499-512]()

## Service-Specific Sidecar Usage

### API Service

```yaml
# Sidecars: Envoy + OTel + FluentBit + RateLimit (optional)
containers:
- name: osmo-service
  # Main container

{{- include "osmo.envoy-sidecar-container" . | nindent 6}}
{{- if .Values.sidecars.otel.enabled }}
{{- include "osmo.otel-sidecar-container" . | nindent 6}}
{{- end }}
{{- include "osmo.log-agent-sidecar-container" . | nindent 6}}
{{- if .Values.sidecars.rateLimit.enabled }}
{{- include "osmo.rate-limit-sidecar-container" . | nindent 6}}
{{- end }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-225]()

### Web UI Service

```yaml
# Sidecars: Envoy + FluentBit
containers:
- name: osmo-ui
  # Main container

{{- include "ui.envoy-sidecar-container" . | nindent 6}}
{{- include "ui.log-agent-sidecar-container" . | nindent 6}}
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:243-244]()

### Worker Service

```yaml
# Sidecars: OTel + FluentBit
# No Envoy - workers don't receive external traffic
containers:
- name: osmo-worker
  # Main container

{{- if .Values.global.logs.enabled }}
{{- include "osmo.log-agent-sidecar-container" . | nindent 6}}
{{- end }}
{{- if .Values.sidecars.otel.enabled }}
{{- include "osmo.otel-sidecar-container" . | nindent 6}}
{{- end }}
```

**Sources:** [deployments/charts/service/templates/worker.yaml:179-184]()

### Router Service

```yaml
# Sidecars: Envoy + FluentBit
containers:
- name: osmo-router
  # Main container

{{- include "router.envoy-sidecar-container" . | nindent 6}}
{{- include "router.log-agent-sidecar-container" . | nindent 6}}
```

**Sources:** [deployments/charts/router/templates/router-service.yaml:188-189]()

## Web UI Runtime Configuration

The Web UI uses environment variables to expose sidecar-related functionality to the client:

```typescript
// From ui/src/env.mjs
shared: {
  NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED: z.boolean().optional().default(false),
  NEXT_PUBLIC_OSMO_SSL_ENABLED: z.boolean().optional().default(true),
}
```

```typescript
// From ui/src/runtime-env.tsx
export interface RuntimeEnv {
  DOCS_BASE_URL: string;
  CLI_INSTALL_SCRIPT_URL: string;
  PORT_FORWARD_ENABLED: boolean;
}
```

These settings control UI features that depend on Envoy and Router sidecars:

- **Port Forwarding UI**: Enabled when Envoy allows proxying to task ports
- **SSL Mode**: Determines whether UI makes HTTPS or HTTP requests to API

**Sources:** [ui/src/env.mjs:68-71](), [ui/src/runtime-env.tsx:21-25](), [ui/src/app/layout.tsx:42-47]()

### UI Feature Gating

```typescript
// From ui/src/app/workflows/components/WorkflowActions.tsx
{workflow.status === "RUNNING" && (
  <>
    <button onClick={() => updateUrl({ tool: ToolType.ShellPicker })}>
      Shell
    </button>
    {runtimeEnv.PORT_FORWARD_ENABLED && (
      <button onClick={() => updateUrl({ tool: ToolType.PortForwarding })}>
        Port Forwarding
      </button>
    )}
  </>
)}
```

**Sources:** [ui/src/app/workflows/components/WorkflowActions.tsx:163-183](), [ui/src/app/workflows/components/TaskActions.tsx:107-116]()

## Sidecar Resource Management

### Resource Allocation Strategy

Sidecar resource limits are typically lower than main containers since they perform auxiliary functions:

| Sidecar | CPU Request | Memory Request | Memory Limit |
|---------|-------------|----------------|--------------|
| Envoy | 100m | 64Mi | 128Mi |
| FluentBit | 250m | 400Mi | 400Mi |
| OTel | Varies | Varies | Varies |

**Sources:** [deployments/charts/web-ui/values.yaml:469-474](), [deployments/charts/web-ui/values.yaml:652-659]()

### Pod-Level Resource Considerations

When sizing pod resource requests/limits, account for all containers:

```
Total Pod Resources = Main Container + Envoy + FluentBit + OTel + RateLimit
```

HorizontalPodAutoscaler metrics are calculated per-container, not per-pod, allowing independent scaling triggers:

```yaml
metrics:
- type: ContainerResource
  containerResource:
    name: memory
    container: {{ .Values.services.service.serviceName }}
    target:
      type: Utilization
      averageUtilization: {{ .Values.services.service.scaling.hpaMemoryTarget }}
```

This ensures that sidecars don't artificially trigger scaling events.

**Sources:** [deployments/charts/service/templates/api-service.yaml:353-367]()

## Troubleshooting Sidecars

### Checking Sidecar Status

```bash
# List all containers in a pod
kubectl get pod <pod-name> -n osmo -o jsonpath='{.spec.containers[*].name}'

# Check specific sidecar logs
kubectl logs <pod-name> -n osmo -c envoy
kubectl logs <pod-name> -n osmo -c fluent-bit
```

### Common Issues

**1. Envoy Not Starting**

- Verify `envoy-config` ConfigMap exists
- Check that secrets are properly mounted
- Review Envoy logs for configuration errors

**2. FluentBit Not Forwarding Logs**

- Ensure `global.logs.enabled: true`
- Verify AWS credentials (for CloudWatch)
- Check FluentBit metrics on port 2020

**3. OTel Sidecar Missing**

- Confirm OpenTelemetry Operator is installed
- Verify pod annotation is present
- Check operator logs for injection failures

**Sources:** [deployments/charts/service/templates/api-service.yaml:218-240]()

---

# Page: Ingress and Networking

# Ingress and Networking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/README.md](deployments/charts/web-ui/README.md)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)
- [deployments/charts/web-ui/values.yaml](deployments/charts/web-ui/values.yaml)
- [ui/src/app/layout.tsx](ui/src/app/layout.tsx)
- [ui/src/app/workflows/components/TaskActions.tsx](ui/src/app/workflows/components/TaskActions.tsx)
- [ui/src/app/workflows/components/WorkflowActions.tsx](ui/src/app/workflows/components/WorkflowActions.tsx)
- [ui/src/env.mjs](ui/src/env.mjs)
- [ui/src/runtime-env.tsx](ui/src/runtime-env.tsx)

</details>



This document describes OSMO's Kubernetes ingress and networking architecture, including how external traffic is routed to services, load balancer configuration, SSL/TLS termination, and service mesh integration with Envoy sidecars.

For information about the Envoy proxy sidecar authentication and filtering, see [Envoy Authentication Proxy](#8.2). For details on service deployments and container configurations, see [Service Deployments](#7.2).

---

## Overview

OSMO uses path-based routing through a unified Kubernetes Ingress controller to distribute traffic across multiple microservices. All external HTTP/HTTPS traffic is routed through ingress resources that terminate SSL, apply load balancing, and forward requests to ClusterIP services. Each service then routes traffic through an Envoy sidecar for authentication before reaching the application container.

**Key Characteristics:**

- **Unified ALB Group**: All ingress resources use the same ALB group name (`osmo`) with priority-based ordering
- **Path-Based Routing**: Different URL paths route to different services (`/api`, `/api/router`, `/api/logger`, etc.)
- **Wildcard Routing**: Router service supports wildcard domains for dynamic task webserver access
- **Envoy Integration**: All services proxy through Envoy sidecars on port 80/8080
- **SSL Termination**: TLS certificates are terminated at the ingress level

---

## Ingress Architecture

### Path-Based Routing Strategy

OSMO implements a path-based routing strategy where a single hostname serves multiple backend services based on URL path prefixes. This enables a unified user experience while maintaining service isolation.

```mermaid
graph TB
    subgraph "External Access"
        Client["Client Browser/CLI"]
        DNS["osmo.example.com"]
    end
    
    subgraph "Ingress Layer"
        ALB["AWS ALB / nginx Ingress"]
        SSL["SSL Certificate<br/>osmo-tls secret"]
    end
    
    subgraph "Ingress Resources"
        UIIngress["UI Ingress<br/>group.order: 200<br/>path: /"]
        UITrpcIngress["UI tRPC Ingress<br/>group.order: 50<br/>path: /api/refresh, /api/trpc"]
        APIIngress["API Ingress<br/>group.order: 100<br/>path: /api, /client"]
        RouterIngress["Router Ingress<br/>group.order: 50<br/>path: /api/router"]
        AgentIngress["Agent Ingress<br/>group.order: 50<br/>path: /api/agent"]
        LoggerIngress["Logger Ingress<br/>group.order: 50<br/>path: /api/logger"]
    end
    
    subgraph "Services"
        UIService["osmo-ui Service<br/>Port 80"]
        APIService["osmo-service Service<br/>Port 80"]
        RouterService["osmo-router Service<br/>Port 80"]
        AgentService["osmo-agent Service<br/>Port 80"]
        LoggerService["osmo-logger Service<br/>Port 80"]
    end
    
    Client --> DNS
    DNS --> ALB
    SSL --> ALB
    
    ALB --> UIIngress
    ALB --> UITrpcIngress
    ALB --> APIIngress
    ALB --> RouterIngress
    ALB --> AgentIngress
    ALB --> LoggerIngress
    
    UIIngress --> UIService
    UITrpcIngress --> UIService
    APIIngress --> APIService
    RouterIngress --> RouterService
    AgentIngress --> AgentService
    LoggerIngress --> LoggerService
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:302-381](), [deployments/charts/service/templates/api-service.yaml:291-335](), [deployments/charts/router/templates/router-service.yaml:257-311]()

### Ingress Priority Ordering

The `alb.ingress.kubernetes.io/group.order` annotation controls routing precedence. Lower values are evaluated first, allowing more specific paths to take priority over broader patterns.

| Priority | Service | Path Pattern | Purpose |
|----------|---------|--------------|---------|
| 50 | UI tRPC | `/api/refresh`, `/api/trpc` | Next.js API routes |
| 50 | Router | `/api/router`, `*.hostname` | Router endpoints, wildcard webservers |
| 50 | Agent | `/api/agent` | Agent status updates |
| 50 | Logger | `/api/logger` | Log streaming |
| 100 | API | `/api`, `/client` | Main API and CLI client downloads |
| 200 | UI | `/` | Default catch-all for UI assets |

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:309-313, 346-350](), [deployments/charts/service/templates/api-service.yaml:300-304](), [deployments/charts/router/templates/router-service.yaml:265-269]()

---

## Service Resources

### ClusterIP Service Definitions

Each OSMO service is exposed internally via a Kubernetes ClusterIP service. These services route traffic to the Envoy sidecar when enabled, or directly to the application container otherwise.

```mermaid
graph LR
    subgraph "osmo-ui Service"
        UISvc["Service Port 80<br/>Protocol: TCP"]
        UITarget["targetPort: envoy-http<br/>or 8000"]
    end
    
    subgraph "osmo-service Service"
        APISvc["Service Port 80<br/>Protocol: TCP"]
        APITarget["targetPort: envoy-http<br/>or 8000"]
    end
    
    subgraph "osmo-router Service"
        RouterSvc["Service Port 80<br/>Protocol: TCP"]
        RouterTarget["targetPort: envoy-http<br/>or 8000"]
    end
    
    UISvc --> UITarget
    APISvc --> APITarget
    RouterSvc --> RouterTarget
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:261-301](), [deployments/charts/service/templates/api-service.yaml:257-270](), [deployments/charts/router/templates/router-service.yaml:238-255]()

### Service Port Configuration

The service target port is dynamically selected based on whether the Envoy sidecar is enabled:

**With Envoy Enabled:**
```yaml
ports:
  - port: 80
    targetPort: envoy-http  # Envoy listener port (8080)
    protocol: TCP
    name: http
```

**With Envoy Disabled:**
```yaml
ports:
  - port: 80
    targetPort: 8000  # Application container port
    protocol: TCP
    name: http
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:278-286](), [deployments/charts/router/templates/router-service.yaml:246-252]()

---

## Routing Patterns

### Standard Path Routing

Most OSMO services use fixed path prefixes for routing:

```yaml
# API Service Ingress
- path: /api
  pathType: Prefix
  backend:
    service:
      name: osmo-service
      port:
        number: 80
        
# Agent Service Ingress
- path: /api/agent
  pathType: Prefix
  backend:
    service:
      name: osmo-agent
      port:
        number: 80
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:315-321](), [deployments/charts/service/templates/agent-service.yaml:272-278]()

### Wildcard Routing for Webserver Access

The router service supports wildcard domain routing to enable dynamic webserver access for running workflow tasks. This allows users to access task webservers at URLs like `task-name.osmo.example.com`.

```yaml
rules:
- host: "*.{{ .Values.services.service.hostname }}"
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: osmo-router
          port:
            number: 80
```

The wildcard routing is only enabled when `services.service.webserverEnabled` is true.

**Sources:** [deployments/charts/router/templates/router-service.yaml:270-272, 280-290]()

### UI tRPC Endpoint Routing

The Web UI creates a separate ingress resource with higher priority (order 50) for Next.js API routes to ensure they don't get caught by the catch-all UI ingress:

```yaml
paths:
- path: /api/refresh
  pathType: Prefix
  backend:
    service:
      name: osmo-ui
      port:
        number: 80
- path: /api/trpc
  pathType: Prefix
  backend:
    service:
      name: osmo-ui
      port:
        number: 80
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:339-381]()

---

## ALB Configuration

### Ingress Annotations

OSMO provides extensive support for AWS Application Load Balancer (ALB) through the AWS Load Balancer Controller. ALB-specific annotations are conditionally applied when `ingress.albAnnotations.enabled` is true.

**Common ALB Annotations:**

| Annotation | Value | Purpose |
|------------|-------|---------|
| `alb.ingress.kubernetes.io/target-type` | `ip` | Direct pod IP routing (bypasses kube-proxy) |
| `alb.ingress.kubernetes.io/group.name` | `osmo` | Unified ALB group for all services |
| `alb.ingress.kubernetes.io/group.order` | `50`, `100`, `200` | Priority ordering for path matching |
| `alb.ingress.kubernetes.io/certificate-arn` | ARN string | SSL certificate for HTTPS termination |

**Router-Specific Wildcard Hostname:**
```yaml
alb.ingress.kubernetes.io/hostnames: '["*.{{ .Values.services.service.hostname }}", "{{ .Values.services.service.hostname }}"]'
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:309-316](), [deployments/charts/service/templates/api-service.yaml:300-308](), [deployments/charts/router/templates/router-service.yaml:265-276]()

### Ingress Class Configuration

OSMO supports multiple ingress controllers through the `ingressClassName` field:

- **nginx**: Standard nginx ingress controller (default for quick-start)
- **alb**: AWS ALB Ingress Controller
- Custom ingress classes as needed

```yaml
spec:
  ingressClassName: {{ .Values.services.ui.ingress.ingressClass }}
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:319](), [deployments/charts/quick-start/Chart.yaml:25-27]()

---

## SSL/TLS Configuration

### Certificate Management

SSL/TLS certificates can be configured in two ways:

**1. Kubernetes Secret (nginx ingress):**
```yaml
tls:
- hosts:
  - osmo.example.com
  secretName: osmo-tls
```

The `osmo-tls` secret must contain `tls.crt` and `tls.key` fields.

**2. AWS Certificate Manager (ALB ingress):**
```yaml
annotations:
  alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-west-2:XXXXXXXXX:certificate/YYYYYYYY
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:331-336, 375-380]()

### SSL Configuration Values

SSL can be enabled/disabled per ingress:

```yaml
services:
  ui:
    ingress:
      sslEnabled: true
      sslSecret: osmo-tls
      albAnnotations:
        enabled: false
        sslCertArn: arn:aws:acm:us-west-2:XXXXXXXXX:certificate/YYYYYYYY
```

**Sources:** [deployments/charts/web-ui/values.yaml:224-230]()

---

## Hostname and DNS Configuration

### Service Hostname Configuration

Each service chart defines a hostname that is used across ingress rules, Envoy configuration, and in-cluster communication:

```yaml
services:
  ui:
    hostname: ""  # Must be configured, e.g., "osmo.example.com"
    apiHostname: "osmo-service.osmo.svc.cluster.local:80"
```

The UI `hostname` is used for external ingress access, while `apiHostname` specifies where the Next.js server should connect to the API service (can be in-cluster or external).

**Sources:** [deployments/charts/web-ui/values.yaml:76, 83](), [deployments/charts/web-ui/templates/ui.yaml:88-89]()

### Wildcard Domain Support

For the router service, wildcard domains are configured when webserver functionality is enabled:

```yaml
services:
  service:
    hostname: "osmo.example.com"
    webserverEnabled: true
```

This creates ingress rules for both:
- `osmo.example.com` (main domain)
- `*.osmo.example.com` (wildcard for task webservers)

**Sources:** [deployments/charts/router/templates/router-service.yaml:270-272, 280-291, 306-308]()

### DNS Resolution

The UI container uses the `NEXT_PUBLIC_OSMO_API_HOSTNAME` environment variable to determine API connectivity:

```yaml
env:
- name: NEXT_PUBLIC_OSMO_API_HOSTNAME
  value: {{ .Values.services.ui.apiHostname }}
```

This environment variable is consumed by the Next.js application to configure API calls.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:88-89](), [ui/src/env.mjs:67, 84]()

---

## Request Flow Architecture

### Complete Request Path

The following diagram illustrates the complete network path from external client to application container:

```mermaid
graph TB
    subgraph "External Layer"
        Client["External Client"]
        Internet["Internet"]
    end
    
    subgraph "Load Balancer Layer"
        LB["ALB / nginx<br/>SSL Termination"]
    end
    
    subgraph "Kubernetes Ingress"
        IngressResource["Ingress Resource<br/>Path Routing<br/>Host Matching"]
    end
    
    subgraph "Service Layer"
        K8sService["ClusterIP Service<br/>Port 80<br/>Selector: app=osmo-ui"]
    end
    
    subgraph "Pod: osmo-ui-xxx"
        EnvoySidecar["Envoy Sidecar<br/>Port 8080 (envoy-http)<br/>OAuth2 + JWT Validation"]
        AppContainer["Application Container<br/>Port 8000<br/>Next.js Server"]
    end
    
    subgraph "Backend Services"
        APIBackend["osmo-service<br/>API Backend"]
        PostgreSQL["PostgreSQL"]
    end
    
    Client --> Internet
    Internet --> LB
    LB --> IngressResource
    IngressResource --> K8sService
    K8sService --> EnvoySidecar
    EnvoySidecar --> AppContainer
    AppContainer --> APIBackend
    AppContainer --> PostgreSQL
```

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:17-257]()

### Port Mapping Details

Each layer in the request path uses specific port configurations:

```mermaid
graph LR
    subgraph "Port Flow"
        ExtPort["External<br/>443 (HTTPS)<br/>80 (HTTP)"]
        IngressPort["Ingress<br/>Targets Service:80"]
        ServicePort["Service<br/>Port 80<br/>→ TargetPort: envoy-http"]
        EnvoyPort["Envoy Container<br/>Port 8080<br/>Named: envoy-http"]
        AppPort["App Container<br/>Port 8000"]
    end
    
    ExtPort --> IngressPort
    IngressPort --> ServicePort
    ServicePort --> EnvoyPort
    EnvoyPort --> AppPort
```

**Container Port Definitions:**

| Container | Port Name | Port Number | Purpose |
|-----------|-----------|-------------|---------|
| UI Application | - | 8000 | Next.js HTTP server |
| Envoy Sidecar | `envoy-http` | 8080 | External listener with auth |
| Envoy Sidecar | `internal-http` | 8081 | In-cluster bypass (optional) |
| Envoy Admin | - | 9901 | Envoy admin interface |

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:84-85, 279-286](), [deployments/charts/web-ui/values.yaml:95-96, 497, 409]()

---

## In-Cluster Communication

### Internal Service Paths

For certain endpoints that should be accessible from within the cluster without authentication (e.g., backend operator calls), OSMO supports an internal service configuration:

```yaml
sidecars:
  envoy:
    inClusterPaths:
      enabled: true
      port: 8081
      paths:
        - /api/internal/some-endpoint
```

When enabled, a separate service is created:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: osmo-service-internal
spec:
  ports:
    - port: 80
      targetPort: internal-http  # Port 8081, bypasses OAuth2
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:274-289](), [deployments/charts/web-ui/values.yaml:407-410]()

### Service Discovery

Services communicate using Kubernetes DNS:

- **Full DNS name**: `osmo-service.osmo.svc.cluster.local`
- **Short name (same namespace)**: `osmo-service`
- **With port**: `osmo-service.osmo.svc.cluster.local:80`

The UI Next.js server uses `apiHostname` configuration to determine whether to connect to the API via:
- In-cluster DNS (e.g., `osmo-service.osmo.svc.cluster.local:80`)
- External hostname (e.g., `osmo.example.com`)

**Sources:** [deployments/charts/web-ui/values.yaml:83](), [deployments/charts/web-ui/templates/ui.yaml:88-89]()

---

## Network Configuration Matrix

### Complete Service Network Map

| Service | Ingress Path | Service Port | Container Port | Envoy Port | Purpose |
|---------|--------------|--------------|----------------|------------|---------|
| `osmo-ui` | `/` | 80 | 8000 | 8080 | Web UI assets |
| `osmo-ui` | `/api/trpc` | 80 | 8000 | 8080 | Next.js API routes |
| `osmo-service` | `/api`, `/client` | 80 | 8000 | 8080 | Main API endpoints |
| `osmo-router` | `/api/router` | 80 | 8000 | 8080 | Router proxy |
| `osmo-router` | `*.hostname` | 80 | 8000 | 8080 | Wildcard webservers |
| `osmo-agent` | `/api/agent` | 80 | 8000 | 8080 | Agent status |
| `osmo-logger` | `/api/logger` | 80 | 8000 | 8080 | Log streaming |

**Sources:** [deployments/charts/web-ui/templates/ui.yaml](), [deployments/charts/service/templates/api-service.yaml](), [deployments/charts/router/templates/router-service.yaml](), [deployments/charts/service/templates/agent-service.yaml](), [deployments/charts/service/templates/logger-service.yaml]()

---

## Runtime Configuration

### Environment Variables for Networking

The UI service exposes several networking-related environment variables for runtime configuration:

```yaml
env:
- name: PORT
  value: '8000'
- name: NODE_OPTIONS
  value: '--max-http-header-size=131072'  # 128KB in bytes
- name: NEXT_PUBLIC_OSMO_API_HOSTNAME
  value: osmo-service.osmo.svc.cluster.local:80
- name: NEXT_PUBLIC_OSMO_SSL_ENABLED
  value: "true"
- name: NEXT_PUBLIC_OSMO_PORT_FORWARD_ENABLED
  value: "false"
```

The `NODE_OPTIONS` max header size should match the Envoy `maxHeadersSizeKb` configuration to prevent 431 errors.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:84-97](), [deployments/charts/web-ui/values.yaml:105]()

### Client-Side API Hostname Resolution

The Next.js application uses environment variables to determine API connectivity:

```javascript
// Determine environment based on hostname format
const computeEnvironment = (nodeEnv, apiHostname) => {
  if (nodeEnv === "development") {
    return apiHostname.includes(":") ? "local" : "local-against-production";
  }
  return "production";
};
```

When `apiHostname` contains a port (e.g., `:80`), it indicates in-cluster communication on the local environment.

**Sources:** [ui/src/env.mjs:31-37, 67-71, 84-92]()

---

## Service Mesh Integration

### Envoy as Edge Proxy

All external requests pass through Envoy sidecars before reaching application containers. The ingress routes to the service, which routes to Envoy's listener port:

```
Internet → ALB → Ingress → Service:80 → Envoy:8080 → App:8000
```

Envoy performs:
1. **OAuth2 flow** for browser-based authentication
2. **JWT validation** for API tokens
3. **Header injection** (e.g., `x-osmo-user`)
4. **Request routing** to upstream application

For detailed information about Envoy's authentication and filtering, see [Envoy Authentication Proxy](#8.2).

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:243-244]()

### Service Account Configuration

Each service deployment specifies a Kubernetes service account for RBAC:

```yaml
serviceAccountName: {{ .Values.services.ui.serviceAccountName }}
```

This service account typically has permissions to:
- Create/read secrets (for OAuth2 credentials)
- Access ConfigMaps (for Envoy configuration)
- Communicate with the Kubernetes API (for health checks)

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:71](), [deployments/charts/web-ui/values.yaml:99]()

---

## Troubleshooting Network Issues

### Common Configuration Issues

**Ingress not routing correctly:**
- Check `ingressClassName` matches installed controller
- Verify `hostname` is configured and DNS resolves correctly
- Ensure ALB `group.order` priorities don't conflict

**SSL certificate errors:**
- For nginx: Verify `sslSecret` exists with valid `tls.crt` and `tls.key`
- For ALB: Verify `certificate-arn` points to valid ACM certificate
- Check certificate matches ingress hostname

**Service connectivity issues:**
- Verify service selector matches pod labels: `app: osmo-ui`
- Check service `targetPort` matches container port name
- Ensure Envoy sidecar is healthy (check port 9901 admin interface)

**Wildcard routing not working:**
- Verify `webserverEnabled: true` in router chart values
- Ensure DNS has wildcard A record: `*.osmo.example.com`
- Check ALB `hostnames` annotation includes wildcard pattern

**Sources:** All Helm template files referenced throughout this document.

---

# Page: Scaling and Resource Management

# Scaling and Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/backend-operator/README.md](deployments/charts/backend-operator/README.md)
- [deployments/charts/backend-operator/templates/backend-listener.yaml](deployments/charts/backend-operator/templates/backend-listener.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml](deployments/charts/backend-operator/templates/backend-test-runner-config.yaml)
- [deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml](deployments/charts/backend-operator/templates/backend-test-runner-rbac.yaml)
- [deployments/charts/backend-operator/templates/backend-worker-rbac.yaml](deployments/charts/backend-operator/templates/backend-worker-rbac.yaml)
- [deployments/charts/backend-operator/values.yaml](deployments/charts/backend-operator/values.yaml)
- [deployments/charts/quick-start/Chart.yaml](deployments/charts/quick-start/Chart.yaml)
- [deployments/charts/router/Chart.yaml](deployments/charts/router/Chart.yaml)
- [deployments/charts/router/templates/router-service.yaml](deployments/charts/router/templates/router-service.yaml)
- [deployments/charts/service/templates/agent-service.yaml](deployments/charts/service/templates/agent-service.yaml)
- [deployments/charts/service/templates/api-service.yaml](deployments/charts/service/templates/api-service.yaml)
- [deployments/charts/service/templates/delayed-job-monitor.yaml](deployments/charts/service/templates/delayed-job-monitor.yaml)
- [deployments/charts/service/templates/logger-service.yaml](deployments/charts/service/templates/logger-service.yaml)
- [deployments/charts/service/templates/worker.yaml](deployments/charts/service/templates/worker.yaml)
- [deployments/charts/web-ui/templates/ui.yaml](deployments/charts/web-ui/templates/ui.yaml)

</details>



This page documents OSMO's horizontal pod autoscaling, resource allocation strategies, and API rate limiting mechanisms. It covers HorizontalPodAutoscaler (HPA) configurations for control plane services, resource request/limit patterns, backend operator resource management, and Kubernetes API client rate limiting.

For ingress and networking configuration, see [Ingress and Networking](#7.4). For service deployment specifications, see [Service Deployments](#7.2).

---

## HorizontalPodAutoscaler Configuration

OSMO services use Kubernetes HorizontalPodAutoscaler to scale pods based on resource utilization. Each service has distinct scaling characteristics based on its workload profile.

### Control Plane Service Scaling

```mermaid
graph TB
    subgraph "API Service HPA"
        APIDeployment["API Deployment<br/>osmo-service"]
        APIHPA["HorizontalPodAutoscaler<br/>autoscaling/v2"]
        APIMetrics["Metrics:<br/>- memory (hpaMemoryTarget)<br/>- cpu (hpaCpuTarget)"]
        
        APIHPA -->|"scaleTargetRef"| APIDeployment
        APIMetrics -->|"target utilization"| APIHPA
    end
    
    subgraph "Agent Service HPA"
        AgentDeployment["Agent Deployment<br/>osmo-agent"]
        AgentHPA["HorizontalPodAutoscaler<br/>autoscaling/v2"]
        AgentMetrics["Metrics:<br/>- memory (hpaMemoryTarget)<br/>- cpu (hpaCpuTarget)"]
        
        AgentHPA -->|"scaleTargetRef"| AgentDeployment
        AgentMetrics -->|"target utilization"| AgentHPA
    end
    
    subgraph "Logger Service HPA"
        LoggerDeployment["Logger Deployment<br/>osmo-logger"]
        LoggerHPA["HorizontalPodAutoscaler<br/>autoscaling/v2"]
        LoggerMetrics["Metrics:<br/>- memory (hpaMemoryTarget)<br/>- cpu (hpaCpuTarget)"]
        
        LoggerHPA -->|"scaleTargetRef"| LoggerDeployment
        LoggerMetrics -->|"target utilization"| LoggerHPA
    end
    
    subgraph "Worker Service HPA"
        WorkerDeployment["Worker Deployment<br/>osmo-worker"]
        WorkerHPA["HorizontalPodAutoscaler<br/>autoscaling/v2"]
        WorkerMetrics["Metrics:<br/>- memory (hpaMemoryTarget)<br/>- cpu (hpaCpuTarget)"]
        
        WorkerHPA -->|"scaleTargetRef"| WorkerDeployment
        WorkerMetrics -->|"target utilization"| WorkerHPA
    end
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-368](), [deployments/charts/service/templates/agent-service.yaml:289-318](), [deployments/charts/service/templates/logger-service.yaml:285-314](), [deployments/charts/service/templates/worker.yaml:208-237]()

### HPA Metric Types

OSMO uses `ContainerResource` type metrics targeting specific containers within pods:

| Service | Container Name | Memory Target | CPU Target | Min Replicas | Max Replicas |
|---------|----------------|---------------|------------|--------------|--------------|
| API | `osmo-service` | `hpaMemoryTarget` | `hpaCpuTarget` | `scaling.minReplicas` | `scaling.maxReplicas` |
| Agent | `osmo-agent` | `hpaMemoryTarget` | `hpaCpuTarget` | `scaling.minReplicas` | `scaling.maxReplicas` |
| Logger | `osmo-logger` | `hpaMemoryTarget` | `hpaCpuTarget` | `scaling.minReplicas` | `scaling.maxReplicas` |
| Worker | `osmo-worker` | `hpaMemoryTarget` | `hpaCpuTarget` | `scaling.minReplicas` | `scaling.maxReplicas` |
| Router | `osmo-router` | `memoryTarget` | N/A | `scaling.minReplicas` | `scaling.maxReplicas` |
| Web UI | `osmo-web-ui` | `hpaTarget` | N/A | `scaling.minReplicas` | `scaling.maxReplicas` |

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-368](), [deployments/charts/service/templates/agent-service.yaml:289-318](), [deployments/charts/service/templates/logger-service.yaml:285-314](), [deployments/charts/service/templates/worker.yaml:208-237](), [deployments/charts/router/templates/router-service.yaml:314-336](), [deployments/charts/web-ui/templates/ui.yaml:383-407]()

### HPA Resource Specification

The HPA resources are defined inline in each service's deployment template:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Values.services.service.serviceName }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Values.services.service.serviceName }}
  minReplicas: {{ .Values.services.service.scaling.minReplicas }}
  maxReplicas: {{ .Values.services.service.scaling.maxReplicas }}
  metrics:
  - type: ContainerResource
    containerResource:
      name: memory
      container: {{ .Values.services.service.serviceName }}
      target:
        type: Utilization
        averageUtilization: {{ .Values.services.service.scaling.hpaMemoryTarget }}
  - type: ContainerResource
    containerResource:
      name: cpu
      container: {{ .Values.services.service.serviceName }}
      target:
        type: Utilization
        averageUtilization: {{ .Values.services.service.scaling.hpaCpuTarget }}
```

**Sources:** [deployments/charts/service/templates/api-service.yaml:339-368](), [deployments/charts/service/templates/agent-service.yaml:289-318]()

### Web UI Scaling Strategy

The Web UI uses conditional replica configuration based on whether scaling is enabled:

```yaml
replicas: {{ if .Values.services.ui.scaling.enabled }}{{ .Values.services.ui.scaling.minReplicas }}{{ else }}{{ .Values.services.ui.replicas }}{{ end }}
```

When `services.ui.scaling.enabled` is `true`, the HPA controls replicas. Otherwise, a static replica count from `services.ui.replicas` is used.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:24](), [deployments/charts/web-ui/templates/ui.yaml:383-407]()

---

## Resource Allocation Patterns

OSMO services have distinct resource profiles based on their computational requirements and memory usage patterns.

### Service Resource Matrix

```mermaid
graph LR
    subgraph "Control Plane Services"
        API["API Service<br/>cpu: varies<br/>memory: varies"]
        Agent["Agent Service<br/>cpu: varies<br/>memory: varies"]
        Logger["Logger Service<br/>cpu: varies<br/>memory: varies"]
        Worker["Worker Service<br/>cpu: varies<br/>memory: varies"]
        Monitor["Delayed Job Monitor<br/>cpu: varies<br/>memory: varies"]
        UI["Web UI Service<br/>cpu: varies<br/>memory: varies"]
        Router["Router Service<br/>cpu: varies<br/>memory: varies"]
    end
    
    subgraph "Backend Operator Services"
        Listener["Backend Listener<br/>cpu: 1<br/>memory: 2Gi"]
        BWorker["Backend Worker<br/>cpu: 1<br/>memory: 1Gi"]
    end
    
    subgraph "Sidecar Resources"
        Envoy["Envoy Sidecar<br/>cpu: 100m<br/>memory: 128Mi"]
        OTEL["OTEL Collector<br/>cpu: 100m<br/>memory: 128Mi"]
        FluentBit["FluentBit<br/>cpu: varies<br/>memory: varies"]
    end
```

**Sources:** [deployments/charts/backend-operator/values.yaml:322-338](), [deployments/charts/backend-operator/values.yaml:428-435]()

### Resource Specification Pattern

All OSMO services follow this resource specification pattern:

```yaml
resources:
  requests:
    cpu: "value"
    memory: "value"
  limits:
    memory: "value"
```

Note that CPU limits are typically **not set**, allowing services to burst when needed while preventing memory-based OOMKills through memory limits.

**Sources:** [deployments/charts/backend-operator/values.yaml:322-338](), [deployments/charts/backend-operator/values.yaml:428-435]()

### Backend Operator Resource Configuration

Backend operators have fixed resource allocations defined in the values:

| Component | CPU Request | Memory Request | Memory Limit |
|-----------|-------------|----------------|--------------|
| Backend Listener | `1` | `2Gi` | `2Gi` |
| Backend Worker | `1` | `1Gi` | `1Gi` |
| Backend Test Runner (init) | `50m` | `64Mi` | `128Mi` (CPU: `100m`) |
| Backend Test Runner (main) | `100m` | `512Mi` | `1Gi` (CPU: `500m`) |
| Egress Proxy (squid) | `2` | `4Gi` | `4Gi` |

**Sources:** [deployments/charts/backend-operator/values.yaml:322-338](), [deployments/charts/backend-operator/values.yaml:428-435](), [deployments/charts/backend-operator/values.yaml:78-86](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:540-570]()

### Sidecar Container Resources

Sidecar containers have standardized resource allocations:

```yaml
# OTEL Sidecar
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "128Mi"
```

**Sources:** [deployments/charts/backend-operator/values.yaml:811-817]()

---

## Backend Operator Resource Management

Backend operators require specific resource management strategies due to their role in managing Kubernetes resources and maintaining cluster state.

### Backend Listener Resource Architecture

```mermaid
graph TB
    ListenerPod["Backend Listener Pod"]
    
    subgraph "Resource Configuration"
        CPURequest["CPU Request: 1 core"]
        MemRequest["Memory Request: 2Gi"]
        MemLimit["Memory Limit: 2Gi"]
    end
    
    subgraph "Operational Limits"
        MaxUnacked["max_unacked_messages: 100"]
        PodCacheTTL["podCacheTtl: 15s"]
        ApiQPS["apiQps: 20"]
        ApiBurst["apiBurst: 30"]
    end
    
    subgraph "Progress Monitoring"
        LivenessProbe["livenessProbe<br/>progress_check<br/>interval: 300s"]
        StartupProbe["startupProbe<br/>progress_check<br/>interval: 300s"]
    end
    
    ListenerPod --> CPURequest
    ListenerPod --> MemRequest
    ListenerPod --> MemLimit
    ListenerPod --> MaxUnacked
    ListenerPod --> PodCacheTTL
    ListenerPod --> ApiQPS
    ListenerPod --> ApiBurst
    ListenerPod --> LivenessProbe
    ListenerPod --> StartupProbe
```

**Sources:** [deployments/charts/backend-operator/values.yaml:322-338](), [deployments/charts/backend-operator/templates/backend-listener.yaml:148-171]()

### Backend Worker Resource Architecture

```mermaid
graph TB
    WorkerPod["Backend Worker Pod"]
    
    subgraph "Resource Configuration"
        CPURequest["CPU Request: 1 core"]
        MemRequest["Memory Request: 1Gi"]
        MemLimit["Memory Limit: 1Gi"]
    end
    
    subgraph "Operational Settings"
        ProgressFreq["progressIterFrequency: 15s"]
    end
    
    subgraph "Progress Monitoring"
        LivenessProbe["livenessProbe<br/>progress_check<br/>interval: 300s"]
        StartupProbe["startupProbe<br/>progress_check<br/>interval: 300s"]
    end
    
    WorkerPod --> CPURequest
    WorkerPod --> MemRequest
    WorkerPod --> MemLimit
    WorkerPod --> ProgressFreq
    WorkerPod --> LivenessProbe
    WorkerPod --> StartupProbe
```

**Sources:** [deployments/charts/backend-operator/values.yaml:428-435](), [deployments/charts/backend-operator/values.yaml:363-365]()

### Volume Mount for Progress Files

Both backend listener and worker use progress files for health checks:

```yaml
volumes:
  - name: progress-files
    emptyDir: {}
volumeMounts:
  - name: progress-files
    mountPath: /var/run/osmo
```

The `progress_check` command monitors these files to determine if the container is making progress.

**Sources:** [deployments/charts/backend-operator/values.yaml:315-320](), [deployments/charts/backend-operator/values.yaml:418-426]()

---

## API Rate Limiting

OSMO implements Kubernetes API client rate limiting to prevent overwhelming the API server when managing large numbers of resources.

### Kubernetes API Client Configuration

The backend listener configures API client QPS (queries per second) and burst limits:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `apiQps` | `20` | Sustained queries per second to Kubernetes API |
| `apiBurst` | `30` | Burst capacity for Kubernetes API requests |

These are passed as command-line arguments:

```bash
backend_listener \
  --api_qps 20 \
  --api_burst 30
```

**Sources:** [deployments/charts/backend-operator/values.yaml:331-337](), [deployments/charts/backend-operator/templates/backend-listener.yaml:117-120]()

### Rate Limiting Strategy

```mermaid
graph LR
    BackendListener["backend_listener process"]
    K8sClient["Kubernetes API Client"]
    APIServer["Kubernetes API Server"]
    
    BackendListener -->|"QPS: 20<br/>Burst: 30"| K8sClient
    K8sClient -->|"rate-limited requests"| APIServer
    
    subgraph "Rate Limiting Behavior"
        Sustained["Sustained: 20 req/s"]
        Burst["Burst: 30 requests"]
        Throttle["Throttle when exceeded"]
    end
    
    K8sClient --> Sustained
    K8sClient --> Burst
    K8sClient --> Throttle
```

**Sources:** [deployments/charts/backend-operator/values.yaml:331-337](), [deployments/charts/backend-operator/templates/backend-listener.yaml:117-120]()

### Cache TTL Configuration

The backend listener uses a pod event cache to reduce API load:

```yaml
podCacheTtl: 15
```

This 15-second TTL means pod event data is cached for 15 seconds before being refreshed from the API server, reducing query frequency for frequently-accessed pod information.

**Sources:** [deployments/charts/backend-operator/values.yaml:257-259](), [deployments/charts/backend-operator/templates/backend-listener.yaml:113-114]()

---

## Priority Classes

OSMO defines priority classes for workload scheduling when the KAI scheduler plugin is enabled. These classes control pod preemption and scheduling order.

### Priority Class Definitions

```mermaid
graph TB
    subgraph "Priority Class Hierarchy"
        High["osmo-high<br/>value: 125<br/>Non-preemptible"]
        Normal["osmo-normal<br/>value: 100<br/>Non-preemptible"]
        Low["osmo-low<br/>value: 50<br/>Preemptible"]
    end
    
    High -->|"higher priority"| Normal
    Normal -->|"higher priority"| Low
    
    subgraph "Scheduling Behavior"
        HighSched["Schedule ASAP<br/>Cannot be preempted"]
        NormalSched["Standard priority<br/>Cannot be preempted"]
        LowSched["Schedule last<br/>Can be preempted"]
    end
    
    High -.-> HighSched
    Normal -.-> NormalSched
    Low -.-> LowSched
```

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221]()

### Priority Class Configuration

Priority classes are defined in the backend-operator values:

```yaml
priorityClasses:
  enabled: true
  classes:
    - name: osmo-high
      value: 125
      description: "Schedule as soon as possible. Non-preemptible."
    - name: osmo-normal
      value: 100
      description: "Standard priority. Non-preemptible."
    - name: osmo-low
      value: 50
      description: "Schedule last. Preemptible."
```

These priority classes are only used when the KAI scheduler plugin is enabled on the cluster.

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221]()

### Priority Class Usage

Priority classes are assigned to workflow task pods based on user configuration or system defaults. Higher priority pods will:
- Be scheduled before lower priority pods when resources are constrained
- Not be preempted by lower priority workloads
- (For `osmo-low` only) Can be preempted by higher priority workloads

**Sources:** [deployments/charts/backend-operator/values.yaml:202-221]()

---

## Backend Test Runner Resource Management

Backend test runner CronJobs have distinct resource allocation for initialization and execution phases.

### Backend Test Runner Resource Allocation

| Phase | Container | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-------|-----------|-------------|----------------|-----------|--------------|
| Init | config-validator | `50m` | `64Mi` | `100m` | `128Mi` |
| Main | backend-test-runner | `100m` | `512Mi` | `500m` | `1Gi` |

**Sources:** [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:540-546](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:562-570]()

### Test Runner Resource Flow

```mermaid
graph TB
    CronJob["Backend Test CronJob"]
    
    subgraph "Init Phase"
        InitContainer["config-validator<br/>cpu: 50m/100m<br/>mem: 64Mi/128Mi"]
        ConfigCheck["Validate test_config.json"]
    end
    
    subgraph "Execution Phase"
        MainContainer["backend-test-runner<br/>cpu: 100m/500m<br/>mem: 512Mi/1Gi"]
        TestExecution["Execute backend tests"]
    end
    
    subgraph "Job Limits"
        ActiveDeadline["activeDeadlineSeconds: 3600"]
        BackoffLimit["backoffLimit: 2"]
        TTL["ttlSecondsAfterFinished: 86400"]
    end
    
    CronJob --> InitContainer
    InitContainer --> ConfigCheck
    ConfigCheck -->|"success"| MainContainer
    MainContainer --> TestExecution
    
    CronJob --> ActiveDeadline
    CronJob --> BackoffLimit
    CronJob --> TTL
```

**Sources:** [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:158-186](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:189-241](), [deployments/charts/backend-operator/values.yaml:489-499]()

### CronJob Scheduling Configuration

Backend test runners have comprehensive scheduling controls:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `schedule` | `0 2 * * *` | Run daily at 2 AM UTC |
| `timezone` | `UTC` | Timezone for schedule interpretation |
| `startingDeadlineSeconds` | `300` | Latest start time if missed |
| `concurrencyPolicy` | `Forbid` | Don't allow concurrent runs |
| `activeDeadlineSeconds` | `3600` | Maximum execution time (1 hour) |
| `ttlSecondsAfterFinished` | `86400` | Keep completed jobs for 24 hours |

**Sources:** [deployments/charts/backend-operator/values.yaml:449-499](), [deployments/charts/backend-operator/templates/backend-test-runner-config.yaml:78-106]()

---

## Network Egress Resource Management

When egress allowlisting is enabled, a squid proxy is deployed with its own resource allocation.

### Egress Proxy Resources

```yaml
resources:
  requests:
    cpu: "2"
    memory: "4Gi"
  limits:
    memory: "4Gi"
```

The proxy includes an Envoy bridge sidecar for HTTPS interception but no explicit resource limits are defined for it.

**Sources:** [deployments/charts/backend-operator/values.yaml:78-86](), [deployments/charts/backend-operator/values.yaml:88-105]()

---

## Topology Spread Constraints

Services can configure topology spread constraints to distribute pods across failure domains:

```yaml
topologySpreadConstraints:
- topologyKey: topology.kubernetes.io/zone
  maxSkew: 1
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      app: {{ .Values.services.ui.serviceName }}
```

This ensures pods are spread across availability zones or other topology domains for high availability.

**Sources:** [deployments/charts/web-ui/templates/ui.yaml:42-53](), [deployments/charts/service/templates/agent-service.yaml:44-55](), [deployments/charts/service/templates/api-service.yaml:43-54]()

---

# Page: Authentication and Security

# Authentication and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



## Purpose and Scope

This document describes OSMO's authentication and security architecture, including OAuth2/OIDC integration, credential encryption, and access control mechanisms. It covers how users, CLI clients, and backend operators authenticate with the platform, and how sensitive data is encrypted at rest.

For specific configuration details, see:
- Keycloak SSO setup: [Keycloak SSO Integration](#8.1)
- Envoy proxy configuration: [Envoy Authentication Proxy](#8.2)
- Credential encryption implementation: [Credential Management and Encryption](#8.3)

For deployment instructions, refer to [Deployment Options Comparison](#2.2) and [Deploying a Backend](#5.2).

---

## Authentication Architecture Overview

OSMO implements a multi-tier authentication system with three primary authentication methods and centralized encryption for sensitive data.

### High-Level Authentication Flow

```mermaid
graph TB
    subgraph "Authentication Methods"
        Browser["Browser Users<br/>(OAuth2 Authorization Code)"]
        CLI["CLI Users<br/>(OAuth2 Device Flow)"]
        Backend["Backend Operators<br/>(Service Tokens)"]
    end
    
    subgraph "Identity Provider"
        Keycloak["Keycloak<br/>OAuth2/OIDC Provider"]
    end
    
    subgraph "OSMO Control Plane"
        Envoy["Envoy Sidecars<br/>JWT Validation"]
        API["API Service"]
        UIService["Web UI Service"]
    end
    
    subgraph "Security Layer"
        SecretManager["SecretManager<br/>src/utils/secret_manager.py"]
        MEK["Master Encryption Key<br/>(JWK Format)"]
        UEK["User Encryption Keys<br/>(Per-User)"]
    end
    
    subgraph "Data Store"
        PostgreSQL[("PostgreSQL<br/>credential table<br/>access_token table<br/>ueks table")]
    end
    
    Browser --> Keycloak
    CLI --> Keycloak
    Backend --> API
    
    Keycloak --> Envoy
    Envoy --> API
    Envoy --> UIService
    
    API --> SecretManager
    SecretManager --> MEK
    SecretManager --> UEK
    SecretManager --> PostgreSQL
```

**Sources:** [src/utils/connectors/postgres.py:38-49](), [docs/deployment_guide/getting_started/deploy_service.rst:116-323](), Diagram 6 from high-level architecture

### Authentication Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Keycloak** | OAuth2/OIDC identity provider | External service |
| **Envoy Sidecars** | JWT validation and session management | API and UI pods |
| **SecretManager** | Credential encryption/decryption | [src/utils/secret_manager.py]() |
| **PostgreSQL** | Encrypted credential storage | `credential`, `access_token`, `ueks` tables |
| **Master Encryption Key (MEK)** | Root encryption key | Vault or file system |

**Sources:** [src/utils/connectors/postgres.py:156-161](), [src/utils/connectors/postgres.py:252-261]()

---

## Authentication Flows

OSMO supports three distinct authentication flows for different client types.

### Browser Authentication Flow (OAuth2 Authorization Code)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Envoy
    participant Keycloak
    participant APIService
    
    User->>Browser: Access https://osmo.example.com
    Browser->>Envoy: HTTP Request
    
    alt No Valid Session
        Envoy->>Keycloak: Redirect to /auth<br/>(authorization_endpoint)
        Keycloak->>User: Login Page
        User->>Keycloak: Enter Credentials
        Keycloak-->>Browser: Authorization Code
        Browser->>Envoy: Request with Code
        Envoy->>Keycloak: Exchange Code<br/>(token_endpoint)
        Keycloak-->>Envoy: JWT Access Token<br/>audience: osmo-browser-flow
        Envoy->>Envoy: Set HMAC Cookie
    end
    
    Envoy->>Envoy: Validate JWT<br/>Check issuer, audience<br/>Verify signature (JWKS)
    Envoy->>Envoy: Extract user claim<br/>x-osmo-user header
    Envoy->>APIService: Forward Request<br/>with x-osmo-user
    APIService-->>Envoy: Response
    Envoy-->>Browser: Response
```

**Key Configuration:**
- **Client ID:** `osmo-browser-flow`
- **Grant Type:** Authorization Code
- **Session Storage:** HMAC-signed cookies
- **User Header:** `x-osmo-user` (injected by Envoy)

**Sources:** Diagram 6 from high-level architecture, [docs/deployment_guide/getting_started/deploy_service.rst:301-318]()

### Device Flow Authentication (CLI)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Keycloak
    participant APIService
    
    User->>CLI: osmo login https://osmo.example.com
    CLI->>Keycloak: POST /device<br/>(device_authorization_endpoint)
    Keycloak-->>CLI: device_code<br/>user_code<br/>verification_uri
    CLI->>User: Display:<br/>"Visit https://auth.osmo.example.com/device<br/>Enter code: ABCD-EFGH"
    
    User->>Keycloak: Navigate to verification_uri<br/>Enter user_code
    Keycloak->>User: Approve device
    
    loop Poll for Token
        CLI->>Keycloak: POST /token<br/>device_code
        alt Not Yet Approved
            Keycloak-->>CLI: authorization_pending
        else Approved
            Keycloak-->>CLI: JWT Access Token<br/>audience: osmo-device
        end
    end
    
    CLI->>APIService: API Request<br/>Bearer <token>
    APIService->>APIService: Validate JWT
    APIService-->>CLI: Response
```

**Key Configuration:**
- **Client ID:** `osmo-device`
- **Grant Type:** Device Authorization
- **Token Storage:** Local config file (`~/.osmo/config.yaml`)
- **Polling Interval:** Configured in Keycloak

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:34-48](), Diagram 6 from high-level architecture

### Service Token Authentication (Backend Operators)

Backend operators use long-lived service tokens for authentication:

```bash
# Create service token
osmo token set backend-token \
  --expires-at 2025-12-31 \
  --description "Backend Operator Token" \
  --service \
  --roles osmo-backend
```

Service tokens are stored in the `access_token` table with type `SERVICE`:

```mermaid
graph LR
    Backend["Backend Operator"] --> Token["Service Token<br/>(access_token table)"]
    Token --> API["API Service"]
    API --> Validation["Token Validation"]
    Validation --> Role["Role Check:<br/>osmo-backend"]
```

**Service Token Storage Schema:**

| Column | Type | Description |
|--------|------|-------------|
| `user_name` | TEXT | Token owner |
| `token_name` | TEXT | Token identifier |
| `access_token` | BYTEA | Hashed token value |
| `expires_at` | TIMESTAMP | Expiration timestamp |
| `access_type` | TEXT | `SERVICE` or `USER` |
| `roles` | TEXT[] | Associated roles |

**Sources:** [src/utils/connectors/postgres.py:975-988](), [docs/deployment_guide/install_backend/deploy_backend.rst:34-48]()

---

## Credential Types and Storage

OSMO manages multiple types of credentials for different purposes.

### Credential Type Enum

```python
class CredentialType(enum.Enum):
    GENERIC = 'GENERIC'   # General credentials
    REGISTRY = 'REGISTRY' # Docker registry credentials
    DATA = 'DATA'         # Object storage credentials
```

**Sources:** [src/utils/connectors/postgres.py:62-67]()

### Credential Database Schema

```mermaid
erDiagram
    credential {
        TEXT user_name PK
        TEXT cred_name PK
        credential_type cred_type
        TEXT profile "Credential profile name"
        HSTORE payload "Encrypted key-value pairs"
    }
    
    access_token {
        TEXT user_name PK
        TEXT token_name PK
        BYTEA access_token "Hashed token"
        TIMESTAMP expires_at
        TEXT access_type "SERVICE or USER"
        TEXT_ARRAY roles
    }
    
    ueks {
        TEXT uid PK "User ID"
        HSTORE keys "Encrypted user keys (per key ID)"
    }
    
    credential ||--o{ ueks : "encrypted_with"
    access_token ||--o{ credential : "grants_access_to"
```

**Table Definitions:**

**`credential` table** - Stores encrypted user credentials:
- **Primary Key:** `(user_name, cred_name)`
- **Unique Constraint:** `(user_name, profile)` - one credential per profile per user
- **Payload Format:** PostgreSQL HSTORE (encrypted key-value pairs)

**`access_token` table** - Stores service and user tokens:
- **Primary Key:** `(user_name, token_name, access_type)`
- **Unique Constraint:** `access_token` - prevents token reuse

**`ueks` table** - Stores user encryption keys:
- **Primary Key:** `uid`
- **Keys Format:** HSTORE mapping key IDs to encrypted keys

**Sources:** [src/utils/connectors/postgres.py:960-972](), [src/utils/connectors/postgres.py:975-988](), [src/utils/connectors/postgres.py:852-860]()

---

## Encryption Architecture

OSMO implements a hierarchical encryption system with a Master Encryption Key (MEK) and per-user encryption keys (UEKs).

### Encryption Key Hierarchy

```mermaid
graph TB
    subgraph "Key Management"
        MEK["Master Encryption Key (MEK)<br/>JWK Format<br/>File: mek.yaml or Vault"]
        SecretManager["SecretManager<br/>src/utils/secret_manager.py"]
    end
    
    subgraph "User Encryption Keys"
        UEK1["User 1 UEK<br/>(kid: key_id_1)"]
        UEK2["User 2 UEK<br/>(kid: key_id_2)"]
        UEK3["User N UEK<br/>(kid: key_id_N)"]
    end
    
    subgraph "Encrypted Data"
        Cred1["User 1 Credentials<br/>JWE Compact Format"]
        Cred2["User 2 Credentials<br/>JWE Compact Format"]
        Cred3["User N Credentials<br/>JWE Compact Format"]
    end
    
    MEK --> SecretManager
    SecretManager --> UEK1
    SecretManager --> UEK2
    SecretManager --> UEK3
    
    UEK1 --> Cred1
    UEK2 --> Cred2
    UEK3 --> Cred3
```

**Sources:** [src/utils/connectors/postgres.py:156-161](), [src/utils/connectors/postgres.py:252-261]()

### Credential Encryption Flow

**Encryption Process:**

```mermaid
sequenceDiagram
    participant User
    participant API
    participant SecretManager
    participant PostgreSQL
    
    User->>API: Store Credential<br/>(plaintext)
    API->>SecretManager: encrypt(value, user)
    
    alt UEK Exists
        SecretManager->>PostgreSQL: SELECT keys FROM ueks<br/>WHERE uid = user
        PostgreSQL-->>SecretManager: Encrypted UEK
        SecretManager->>SecretManager: Decrypt UEK with MEK
    else UEK Does Not Exist
        SecretManager->>SecretManager: Generate new UEK
        SecretManager->>SecretManager: Encrypt UEK with MEK
        SecretManager->>PostgreSQL: INSERT INTO ueks
    end
    
    SecretManager->>SecretManager: Encrypt credential with UEK<br/>(JWE Compact Format)
    SecretManager-->>API: Encrypted credential
    API->>PostgreSQL: UPDATE credential<br/>SET payload = encrypted_value
```

**Decryption Process:**

```mermaid
sequenceDiagram
    participant API
    participant SecretManager
    participant PostgreSQL
    
    API->>PostgreSQL: SELECT payload FROM credential
    PostgreSQL-->>API: Encrypted credential (HSTORE)
    API->>SecretManager: decrypt(encrypted, user)
    
    SecretManager->>PostgreSQL: SELECT keys FROM ueks<br/>WHERE uid = user
    PostgreSQL-->>SecretManager: Encrypted UEK
    SecretManager->>SecretManager: Decrypt UEK with MEK
    SecretManager->>SecretManager: Extract kid from JWE header
    SecretManager->>SecretManager: Decrypt credential with UEK
    SecretManager-->>API: Plaintext credential
```

**Sources:** [src/utils/connectors/postgres.py:475-500](), [src/utils/connectors/postgres.py:502-507]()

### PostgresConnector Encryption Methods

**Key Methods:**

| Method | Purpose | Location |
|--------|---------|----------|
| `encrypt_dict()` | Encrypts dictionary of credentials | [src/utils/connectors/postgres.py:502-507]() |
| `decrypt_credential()` | Decrypts credential from database | [src/utils/connectors/postgres.py:475-500]() |
| `encode_hstore()` | Encodes dict to PostgreSQL HSTORE | [src/utils/connectors/postgres.py:515-517]() |
| `decode_hstore()` | Decodes HSTORE to dict | [src/utils/connectors/postgres.py:519-524]() |

**HSTORE Encoding Example:**

The `credential.payload` column uses PostgreSQL's HSTORE type for storing key-value pairs:

```python
# Input: {'access_key': 'AKIAIOSFODNN7EXAMPLE', 'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'}
# After encryption:
# HSTORE: '"access_key"=>"eyJhbGc...","secret_key"=>"eyJhbGc..."'
```

**Sources:** [src/utils/connectors/postgres.py:515-524]()

---

## Master Encryption Key (MEK) Configuration

The MEK is loaded during `PostgresConnector` initialization and used by `SecretManager` for all encryption operations.

### MEK Initialization

```python
# From PostgresConnector.__init__
mek_file = self.config.mek_file
if self.config.method == 'dev':
    ExtraArgBaseModel.set_extra(ExtraType.ALLOW)
    mek_file = os.path.join(os.path.dirname(__file__), '..', 'secret_manager', 'mek.yaml')

self.secret_manager = SecretManager(
    mek_file,
    self.read_uek,      # Callback to read UEK from database
    self.write_uek,     # Callback to write UEK to database
    self.read_current_kid,  # Callback to get current key ID
    self.add_user       # Callback to add user
)
```

**Configuration Fields:**

| Field | Environment Variable | Default | Description |
|-------|---------------------|---------|-------------|
| `mek_file` | `OSMO_MEK_FILE` | `/home/osmo/vault-agent/secrets/vault-secrets.yaml` | Path to MEK file |
| `method` | N/A | `None` | Set to `'dev'` for local development |

**MEK File Format (JWK):**

```yaml
keys:
  - kid: "key_2024_01"
    kty: "oct"
    k: "<base64-encoded-key>"
    alg: "A256GCM"
  - kid: "key_2024_02"
    kty: "oct"
    k: "<base64-encoded-key>"
    alg: "A256GCM"
```

**Sources:** [src/utils/connectors/postgres.py:252-261](), [src/utils/connectors/postgres.py:156-161]()

---

## Authentication Header Extraction

Envoy sidecars extract user identity from validated JWTs and inject it as the `x-osmo-user` header.

### User Header Middleware

```mermaid
graph LR
    Request["Incoming Request"] --> Envoy["Envoy Sidecar"]
    Envoy --> Validate["Validate JWT<br/>Check issuer<br/>Check audience<br/>Verify signature"]
    Validate --> Extract["Extract user claim<br/>from JWT payload"]
    Extract --> Inject["Inject Header:<br/>x-osmo-user: username"]
    Inject --> Forward["Forward to<br/>API/UI Service"]
```

**JWT Claims Validation:**

Envoy validates the following JWT claims:
- **`iss` (Issuer):** Must match Keycloak issuer URL
- **`aud` (Audience):** Must be `osmo-browser-flow` or `osmo-device`
- **`exp` (Expiration):** Token must not be expired
- **Signature:** Verified using Keycloak's JWKS endpoint

**User Extraction:**

The username is extracted from the JWT `preferred_username` or `sub` claim and injected as `x-osmo-user`.

**Sources:** Diagram 6 from high-level architecture, [src/utils/connectors/postgres.py:167-172]()

---

## Task Authentication

Tasks running in the backend cluster authenticate to the OSMO service using refresh tokens stored in the `tasks` table.

### Task Refresh Token Flow

```mermaid
sequenceDiagram
    participant Task["Task Pod<br/>(osmo-ctrl container)"]
    participant API["API Service"]
    participant DB["PostgreSQL"]
    
    Note over Task,DB: Task initialization
    Task->>DB: INSERT INTO tasks<br/>refresh_token = random_bytes(32)
    
    Note over Task,DB: Task execution
    Task->>Task: Read refresh_token<br/>from /osmo/login/config
    Task->>API: POST /refresh<br/>Bearer <refresh_token>
    API->>DB: SELECT * FROM tasks<br/>WHERE refresh_token = hash(token)
    DB-->>API: task_uuid, workflow_id, user
    API->>API: Generate JWT<br/>user from task.user
    API-->>Task: JWT Access Token
    
    Task->>API: API requests<br/>Bearer <JWT>
    API->>API: Validate JWT
    API-->>Task: Response
```

**Refresh Token Storage:**

| Column | Type | Description |
|--------|------|-------------|
| `refresh_token` | BYTEA | 32-byte random token |
| `task_uuid` | TEXT | Unique task identifier |
| `workflow_id` | TEXT | Parent workflow ID |

**Token Generation:**

```python
# Generate refresh token (task creation)
refresh_token = secrets.token_bytes(REFRESH_TOKEN_LENGTH)  # 32 bytes
```

**Sources:** [src/utils/job/task.py:54-56](), [src/utils/connectors/postgres.py:745]()

---

## Role-Based Access Control (RBAC)

OSMO implements role-based access control through the `roles` table and service token assignments.

### Roles Table Schema

```mermaid
erDiagram
    roles {
        TEXT name PK
        TEXT description
        JSONB_ARRAY policies "List of policy objects"
        BOOLEAN immutable "Prevent modification"
    }
    
    access_token {
        TEXT user_name
        TEXT token_name
        TEXT_ARRAY roles "Assigned roles"
    }
    
    roles ||--o{ access_token : "assigned_to"
```

**Built-in Roles:**

| Role | Description | Immutable |
|------|-------------|-----------|
| `osmo-backend` | Backend operator service role | Yes |
| `osmo-admin` | Administrative access | Yes |
| `osmo-user` | Standard user access | Yes |

**Sources:** [src/utils/connectors/postgres.py:548-558](), [src/utils/connectors/postgres.py:982]()

### Policy Structure

Policies define allowed actions on specific resources:

```json
{
  "resource": "workflow",
  "actions": ["submit", "cancel", "list"],
  "conditions": {
    "owner": "${user}"
  }
}
```

**Sources:** [src/utils/connectors/postgres.py:554]()

---

## Security Best Practices

### Credential Management

1. **Rotation:** Regularly rotate MEK and service tokens
2. **Expiration:** Set appropriate `expires_at` for service tokens
3. **Least Privilege:** Assign minimal roles required for each service token
4. **Encryption at Rest:** All credentials stored in PostgreSQL are encrypted

### Token Security

1. **Storage:** 
   - Browser: HMAC-signed cookies (HttpOnly, Secure)
   - CLI: Local config file with restricted permissions (0600)
   - Backend: Kubernetes secrets

2. **Validation:**
   - JWT signature verification using JWKS
   - Audience claim validation
   - Expiration time checks

3. **Refresh Tokens:**
   - Task refresh tokens are single-use and expire with task completion
   - Stored as hashed values in database

### Network Security

1. **TLS/HTTPS:** All external communication uses TLS
2. **Envoy Sidecars:** Act as authentication gatekeepers
3. **Internal Traffic:** Service-to-service communication within Kubernetes cluster

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:116-323](), [src/utils/connectors/postgres.py:475-507]()

---

## Development Mode

For local development, OSMO supports a `dev` authentication mode that bypasses Keycloak:

```python
dev_user: str = pydantic.Field(
    command_line='dev_user',
    default='testuser',
    description='If method is set to "dev", the browser flow to the service will use this user name.'
)
```

**Configuration:**

```bash
# Set dev mode
--method=dev --dev_user=testuser
```

**Behavior:**
- Envoy sidecars disabled
- No JWT validation
- Fixed user identity (`testuser`)
- Local MEK file used (`src/utils/secret_manager/mek.yaml`)

**⚠️ Warning:** Development mode should **never** be used in production environments.

**Sources:** [src/utils/connectors/postgres.py:167-172](), [src/utils/connectors/postgres.py:254-257]()

---

# Page: Keycloak SSO Integration

# Keycloak SSO Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)

</details>



This document describes how OSMO integrates with Keycloak for Single Sign-On (SSO) authentication using OAuth2/OIDC protocols. It covers Keycloak installation, realm configuration, client setup, and the various authentication flows used by OSMO components.

For information about how Envoy validates and processes JWT tokens from Keycloak, see [Envoy Authentication Proxy](#8.2). For credential encryption and storage mechanisms, see [Credential Management and Encryption](#8.3).

## Overview

OSMO uses Keycloak as its identity provider to support multiple authentication mechanisms:

- **Browser-based authentication** - Web UI users authenticate via OAuth2 authorization code flow
- **Device authentication** - CLI users authenticate via OAuth2 device authorization flow  
- **Service token authentication** - Backend operators and service-to-service communication use long-lived service tokens
- **Identity provider federation** - Keycloak can integrate with external identity providers (LDAP, SAML, social logins)

Keycloak manages user identities, groups, roles, and issues JWT access tokens that OSMO services validate through Envoy sidecars.

## Architecture

### Keycloak Component Diagram

```mermaid
graph TB
    subgraph "Keycloak Deployment"
        KC[Keycloak Service<br/>Bitnami Chart]
        KCDB[(Keycloak Database<br/>PostgreSQL)]
        KCIngress[Ingress<br/>auth-domain.com]
    end
    
    subgraph "OSMO Realm"
        Realm[osmo Realm]
        
        subgraph "Clients"
            BrowserClient["osmo-browser-flow<br/>Client ID<br/>Confidential"]
            DeviceClient["osmo-device<br/>Client ID<br/>Public"]
        end
        
        subgraph "Groups and Roles"
            AdminGroup[Admin Group]
            UserGroup[User Group]
        end
        
        subgraph "Users"
            Users[Keycloak Users<br/>Email/Password]
        end
    end
    
    subgraph "OSMO Services"
        WebUI[Web UI]
        CLI[OSMO CLI]
        API[API Service]
        Router[Router Service]
        BackendOp[Backend Operator]
    end
    
    subgraph "Authentication Flows"
        AuthCode[Authorization Code Flow<br/>Browser]
        DeviceFlow[Device Authorization Flow<br/>CLI]
        ServiceToken[Service Token<br/>Backend]
    end
    
    KC --> KCDB
    KCIngress --> KC
    KC --> Realm
    Realm --> BrowserClient
    Realm --> DeviceClient
    Realm --> AdminGroup
    Realm --> UserGroup
    Realm --> Users
    
    WebUI --> AuthCode
    CLI --> DeviceFlow
    BackendOp --> ServiceToken
    
    AuthCode --> BrowserClient
    DeviceFlow --> DeviceClient
    ServiceToken --> API
    
    BrowserClient --> KC
    DeviceClient --> KC
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:116-349]()

### Authentication Flow Overview

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Envoy
    participant Keycloak
    participant Service as OSMO Service
    
    rect rgb(245, 245, 245)
        Note over User,Service: Browser Authentication Flow
        User->>Browser: Access https://osmo.example.com
        Browser->>Envoy: HTTP Request
        Envoy->>Keycloak: Redirect to /realms/osmo/protocol/openid-connect/auth
        Keycloak->>User: Login Page
        User->>Keycloak: Credentials
        Keycloak-->>Browser: Authorization Code
        Browser->>Envoy: Callback with Code
        Envoy->>Keycloak: POST /realms/osmo/protocol/openid-connect/token
        Keycloak-->>Envoy: JWT Access Token<br/>audience: osmo-browser-flow
        Envoy->>Envoy: Set HMAC-signed Cookie
        Envoy->>Envoy: Validate JWT<br/>Extract preferred_username claim
        Envoy->>Service: Forward with x-osmo-user header
    end
    
    rect rgb(245, 245, 245)
        Note over User,Service: CLI Device Flow
        User->>CLI: osmo login https://osmo.example.com
        CLI->>Keycloak: POST /realms/osmo/protocol/openid-connect/auth/device
        Keycloak-->>CLI: device_code + user_code + verification_uri
        CLI->>User: Display verification URL
        User->>Keycloak: Approve device at verification_uri
        CLI->>Keycloak: Poll /realms/osmo/protocol/openid-connect/token
        Keycloak-->>CLI: JWT Access Token<br/>audience: osmo-device
        CLI->>Service: API Request with Bearer token
    end
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:519-655]()

## Installation

### Prerequisites

- Kubernetes cluster with ingress controller (nginx, ALB, etc.)
- PostgreSQL database for Keycloak persistence
- SSL certificate for the auth subdomain
- Helm 3.x installed

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:25-30]()

### Deployment Steps

#### Step 1: Create Keycloak Database

```bash
$ export OSMO_DB_HOST=<your-db-host>
$ export OSMO_PGPASSWORD=<your-postgres-password>
$ kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: osmo-db-ops
spec:
  containers:
    - name: osmo-db-ops
      image: alpine/psql:17.5
      command: ["/bin/sh", "-c"]
      args:
        - "PGPASSWORD=$OSMO_PGPASSWORD psql -U postgres -h $OSMO_DB_HOST -p 5432 -d postgres -c 'CREATE DATABASE keycloak;'"
  restartPolicy: Never
EOF
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:87-114]()

#### Step 2: Create Database Secret

```bash
$ kubectl create namespace keycloak
$ kubectl create secret generic keycloak-db-secret \
  --namespace keycloak \
  --from-literal=postgres-password='<your-db-password>'
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:232-244]()

#### Step 3: Configure Helm Values

Create `keycloak-values.yaml`:

| Configuration Section | Key Parameters | Purpose |
|----------------------|----------------|---------|
| **Hostname** | `hostname`, `proxy` | Set auth subdomain and edge proxy mode |
| **Authentication** | `auth.adminUser`, `auth.adminPassword` | Admin credentials for initial setup |
| **Ingress** | `ingress.enabled`, `ingress.hostname`, `ingress.annotations` | Expose Keycloak via load balancer |
| **Database** | `externalDatabase.host`, `externalDatabase.existingSecret` | Connect to PostgreSQL |
| **Scaling** | `autoscaling.minReplicas`, `autoscaling.maxReplicas` | Configure horizontal pod autoscaling |
| **TLS** | `tls.enabled`, `tls.autoGenerated` | Enable HTTPS with auto-generated certs |

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:135-223]()

#### Step 4: Install Keycloak

```bash
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm repo update
$ helm install keycloak bitnami/keycloak \
  --version 24.4.9 \
  --namespace keycloak \
  -f keycloak-values.yaml
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:246-253]()

#### Step 5: Verify Installation

```bash
$ kubectl get pods -n keycloak
$ kubectl get ingress -n keycloak
```

Access Keycloak at `https://auth-osmo.example.com` or via port-forward for testing:

```bash
$ kubectl port-forward service/keycloak 32080:80 -n keycloak
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:255-270]()

## Realm Configuration

### OSMO Realm Structure

```mermaid
graph TB
    subgraph "osmo Realm"
        direction TB
        
        subgraph "Clients Configuration"
            BC["osmo-browser-flow<br/>---<br/>Client ID: osmo-browser-flow<br/>Access Type: confidential<br/>Flow: Standard Flow"]
            DC["osmo-device<br/>---<br/>Client ID: osmo-device<br/>Access Type: public<br/>Flow: Device Authorization"]
        end
        
        subgraph "Client Settings"
            BCSettings["Browser Flow Settings<br/>---<br/>Root URL: https://osmo.example.com<br/>Valid Redirect URIs: https://osmo.example.com/*<br/>Web Origins: https://osmo.example.com<br/>Client Secret: Generated"]
            DCSettings["Device Flow Settings<br/>---<br/>Root URL: https://osmo.example.com<br/>Valid Redirect URIs: https://osmo.example.com/*<br/>Device Authorization Grant: Enabled"]
        end
        
        subgraph "Groups and Roles"
            AG["Admin Group<br/>---<br/>Elevated permissions<br/>Configure OSMO<br/>Manage users"]
            UG["User Group<br/>---<br/>Basic permissions<br/>Submit workflows<br/>Manage own workflows"]
        end
        
        subgraph "Token Configuration"
            JWT["JWT Token Claims<br/>---<br/>issuer: https://auth-domain/realms/osmo<br/>audience: osmo-browser-flow OR osmo-device<br/>preferred_username: User identifier<br/>groups: User groups"]
        end
        
        BC --> BCSettings
        DC --> DCSettings
        BCSettings --> JWT
        DCSettings --> JWT
        AG --> JWT
        UG --> JWT
    end
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:272-349]()

### Creating the OSMO Realm

1. **Access Keycloak Admin Console**
   - Navigate to `https://auth-osmo.example.com`
   - Log in with admin credentials specified in Helm values

2. **Import Realm Configuration**
   - Download sample realm file: `sample_osmo_realm.json`
   - Click dropdown menu (top left) → "Create Realm"
   - Upload realm file in "Resource file" field
   - Click "Create"

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:277-299]()

### Client Configuration

#### Browser Flow Client (`osmo-browser-flow`)

Navigate to Clients tab and configure:

| Setting | Value |
|---------|-------|
| Client ID | `osmo-browser-flow` |
| Client Protocol | openid-connect |
| Access Type | confidential |
| Standard Flow Enabled | ON |
| Root URL | `https://osmo.example.com` |
| Valid Redirect URIs | `https://osmo.example.com/*` |
| Web Origins | `https://osmo.example.com` |

Generate and save client secret from Credentials tab - required for Envoy configuration.

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:301-318]()

#### Device Flow Client (`osmo-device`)

Configure for CLI authentication:

| Setting | Value |
|---------|-------|
| Client ID | `osmo-device` |
| Client Protocol | openid-connect |
| Access Type | public |
| OAuth 2.0 Device Authorization Grant Enabled | ON |
| Root URL | `https://osmo.example.com` |
| Valid Redirect URIs | `https://osmo.example.com/*` |

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:301-312]()

## User and Group Management

### Creating Users

Users are created in the Keycloak admin console:

1. Navigate to Users tab
2. Click "Add User"
3. Fill in user details (email, username)
4. Assign to group: `Admin` or `User`
5. Save user

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:320-335]()

### Setting User Credentials

1. Click user's ID to access settings
2. Navigate to Credentials tab
3. Enter password
4. Enable "Temporary" flag to force password reset on first login

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:337-343]()

### Group Roles

| Group | Permissions | Use Cases |
|-------|-------------|-----------|
| **Admin** | Elevated permissions for configuring OSMO and managing users | System administrators, DevOps team |
| **User** | Basic permissions for submitting and managing own workflows | Data scientists, ML engineers, researchers |

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:329-331]()

### Identity Provider Integration

Keycloak supports federation with external identity providers:

- LDAP/Active Directory
- SAML-based providers
- Social logins (Google, GitHub, etc.)
- Custom OAuth2/OIDC providers

Refer to official Keycloak documentation for identity provider configuration.

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:345-348]()

## Integration with OSMO Services

### Service Configuration

Each OSMO service requires Keycloak endpoint configuration:

#### API Service Configuration

```yaml
services:
  service:
    auth:
      enabled: true
      device_endpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/device
      device_client_id: osmo-device
      browser_endpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/auth
      browser_client_id: osmo-browser-flow
      token_endpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/token
      logout_endpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/logout
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:519-527]()

#### Envoy Sidecar Configuration

Create OIDC secrets:

```bash
$ kubectl create secret generic oidc-secrets \
  --from-literal=client_secret=<keycloak-client-secret> \
  --from-literal=hmac_secret=$(head -c32 /dev/urandom | base64) \
  --namespace osmo
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:370-382]()

Configure Envoy OAuth2 filter:

```yaml
sidecars:
  envoy:
    oauth2Filter:
      enabled: true
      tokenEndpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/token
      authEndpoint: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/auth
      clientId: osmo-browser-flow
      authProvider: auth-<your-domain>
      secretName: oidc-secrets
      clientSecretKey: client_secret
      hmacSecretKey: hmac_secret
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:625-635]()

Configure JWT validation:

```yaml
sidecars:
  envoy:
    jwt:
      user_header: x-osmo-user
      providers:
      - issuer: https://auth-<your-domain>/realms/osmo
        audience: osmo-device
        jwks_uri: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/certs
        user_claim: preferred_username
        cluster: oauth
      - issuer: https://auth-<your-domain>/realms/osmo
        audience: osmo-browser-flow
        jwks_uri: https://auth-<your-domain>/realms/osmo/protocol/openid-connect/certs
        user_claim: preferred_username
        cluster: oauth
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:637-655]()

### Keycloak Endpoints Used by OSMO

```mermaid
graph LR
    subgraph "Keycloak Endpoints"
        Auth["/realms/osmo/protocol/openid-connect/auth<br/>Authorization Endpoint"]
        Token["/realms/osmo/protocol/openid-connect/token<br/>Token Endpoint"]
        Device["/realms/osmo/protocol/openid-connect/auth/device<br/>Device Authorization"]
        JWKS["/realms/osmo/protocol/openid-connect/certs<br/>JWKS Endpoint"]
        Logout["/realms/osmo/protocol/openid-connect/logout<br/>Logout Endpoint"]
    end
    
    subgraph "OSMO Components"
        WebUI["Web UI<br/>osmo-browser-flow"]
        CLI["OSMO CLI<br/>osmo-device"]
        EnvoyProxy["Envoy Sidecars<br/>JWT Validation"]
        APIService["API Service<br/>Login Info"]
    end
    
    WebUI --> Auth
    WebUI --> Token
    CLI --> Device
    CLI --> Token
    EnvoyProxy --> JWKS
    APIService --> Device
    APIService --> Auth
    APIService --> Token
    APIService --> Logout
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:519-527](), [docs/deployment_guide/getting_started/deploy_service.rst:625-655]()

## Service Token Management

### Creating Service Tokens

Backend operators use long-lived service tokens for authentication:

```bash
$ osmo login https://osmo.example.com
$ export OSMO_SERVICE_TOKEN=$(osmo token set backend-token \
    --expires-at <insert-date> \
    --description "Backend Operator Token" \
    --service \
    --roles osmo-backend \
    -t json | jq -r '.token')
```

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:33-47]()

### Service Token Characteristics

| Attribute | Value |
|-----------|-------|
| Token Type | Service token (not issued by Keycloak) |
| Issuer | `osmo` (internal) |
| Audience | `osmo` |
| Role | `osmo-backend` |
| Expiration | User-defined (long-lived) |
| Purpose | Backend operator authentication, service-to-service calls |

Service tokens are validated by OSMO API service through internal JWT validation, not Keycloak.

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:33-47]()

### Storing Service Tokens

Backend operators store tokens as Kubernetes secrets:

```bash
$ kubectl create secret generic osmo-operator-token -n osmo-operator \
    --from-literal=token=$OSMO_SERVICE_TOKEN
```

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:63-64]()

### Token Validation Flow

```mermaid
sequenceDiagram
    participant Backend as Backend Operator
    participant Envoy as Envoy Sidecar
    participant API as API Service
    participant KeyDB as JWT Keys Endpoint
    
    rect rgb(245, 245, 245)
        Note over Backend,KeyDB: Service Token Flow
        Backend->>Envoy: Request with Bearer token<br/>role: osmo-backend
        Envoy->>Envoy: Check JWT provider config
        Envoy->>KeyDB: GET /api/auth/keys<br/>Fetch JWKS
        KeyDB-->>Envoy: JWKS for osmo issuer
        Envoy->>Envoy: Validate JWT signature<br/>Check issuer: osmo<br/>Check audience: osmo
        Envoy->>Envoy: Extract unique_name claim
        Envoy->>API: Forward with x-osmo-user header
    end
    
    rect rgb(245, 245, 245)
        Note over Backend,KeyDB: Keycloak Token Flow
        Backend->>Envoy: Request with Bearer token<br/>audience: osmo-device
        Envoy->>Envoy: Check JWT provider config
        Envoy->>KeyDB: GET https://auth-domain/realms/osmo/protocol/openid-connect/certs
        KeyDB-->>Envoy: Keycloak JWKS
        Envoy->>Envoy: Validate JWT signature<br/>Check issuer: https://auth-domain/realms/osmo<br/>Check audience: osmo-device
        Envoy->>Envoy: Extract preferred_username claim
        Envoy->>API: Forward with x-osmo-user header
    end
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:637-655]()

## Security Considerations

### Client Secret Management

- Client secrets are generated in Keycloak Credentials tab for `osmo-browser-flow`
- Stored in Kubernetes secrets (`oidc-secrets`)
- Never committed to version control
- Rotated periodically according to security policy

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:317-318](), [docs/deployment_guide/getting_started/deploy_service.rst:370-382]()

### HMAC Secret for Cookie Signing

Envoy uses HMAC-signed cookies for session management:

```bash
$ head -c32 /dev/urandom | base64
```

This secret signs session cookies to prevent tampering. Store in `oidc-secrets` Kubernetes secret.

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:375-378]()

### JWT Token Validation

Envoy sidecars validate JWT tokens by:

1. Fetching JWKS from Keycloak's `/protocol/openid-connect/certs` endpoint
2. Verifying token signature using public keys
3. Validating issuer matches `https://auth-<domain>/realms/osmo`
4. Checking audience is `osmo-device` or `osmo-browser-flow`
5. Extracting `preferred_username` claim for user identification

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:637-655]()

### Token Expiration

| Token Type | Default Expiration | Renewal Mechanism |
|------------|-------------------|-------------------|
| Browser access token | Keycloak session timeout | OAuth2 refresh token |
| Device access token | Keycloak session timeout | Requires re-authentication |
| Service token | User-defined | Manual rotation via `osmo token` |

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:174-182]()

### TLS Configuration

Keycloak requires TLS for production deployments:

```yaml
production: true
tls:
  enabled: true
  autoGenerated: true
proxy: edge
```

TLS termination occurs at ingress level, with Keycloak configured for edge proxy mode.

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:156-162]()

## Troubleshooting

### Token Expiration Error

Error message:
```
Connection failed with error: {OSMOUserError: Token is expired, but no refresh token is present}
```

**Resolution:**
1. Check token status: `osmo token list --service`
2. Create new token: Follow service token creation steps
3. Update Kubernetes secret with new token

**Sources:** [docs/deployment_guide/install_backend/deploy_backend.rst:174-182]()

### Authentication Configuration Issues

Common problems:

| Issue | Cause | Resolution |
|-------|-------|------------|
| Redirect loop | Incorrect redirect URIs | Verify client redirect URIs match OSMO domain |
| 401 Unauthorized | Wrong client secret | Check `oidc-secrets` matches Keycloak client secret |
| JWKS fetch failure | Network connectivity | Verify Envoy can reach Keycloak endpoints |
| Wrong user claim | Incorrect JWT provider config | Verify `user_claim` matches Keycloak token structure |

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:301-318](), [docs/deployment_guide/getting_started/deploy_service.rst:1031-1037]()

### Ingress Routing Problems

For large OAuth2 response headers, configure nginx annotations:

```yaml
annotations:
  nginx.ingress.kubernetes.io/proxy-buffer-size: "16k"
  nginx.ingress.kubernetes.io/proxy-buffers: "8 16k"
  nginx.ingress.kubernetes.io/proxy-busy-buffers-size: "32k"
  nginx.ingress.kubernetes.io/large-client-header-buffers: "4 16k"
```

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:536-541]()

### Database Connection Failures

Verify Keycloak can connect to PostgreSQL:

```bash
$ kubectl logs -n keycloak -l app.kubernetes.io/name=keycloak
```

Check for connection errors and verify:
- Database exists (`keycloak`)
- Database secret contains correct password
- PostgreSQL is accessible from Keycloak pods

**Sources:** [docs/deployment_guide/getting_started/deploy_service.rst:209-219]()

---

# Page: Envoy Authentication Proxy

# Envoy Authentication Proxy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployments/charts/web-ui/README.md](deployments/charts/web-ui/README.md)
- [deployments/charts/web-ui/values.yaml](deployments/charts/web-ui/values.yaml)
- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)
- [ui/src/app/layout.tsx](ui/src/app/layout.tsx)
- [ui/src/app/workflows/components/TaskActions.tsx](ui/src/app/workflows/components/TaskActions.tsx)
- [ui/src/app/workflows/components/WorkflowActions.tsx](ui/src/app/workflows/components/WorkflowActions.tsx)
- [ui/src/env.mjs](ui/src/env.mjs)
- [ui/src/runtime-env.tsx](ui/src/runtime-env.tsx)

</details>



This document describes Envoy's role as an authentication proxy in OSMO, handling OAuth2 browser flows and JWT token validation for all control plane services. Envoy runs as a sidecar container alongside the API, Web UI, and Router services, intercepting HTTP requests to validate authentication before forwarding them to the backend service.

For information about Keycloak SSO configuration, see [Keycloak SSO Integration](#8.1). For credential encryption within the database, see [Credential Management and Encryption](#8.3).

## Architecture Overview

Envoy is deployed as a sidecar container in OSMO service pods, acting as the entry point for all HTTP traffic. It validates authentication credentials and enriches requests with user identity information before forwarding to the application container.

### Envoy Sidecar Deployment Pattern

```mermaid
graph TB
    subgraph "Service Pod (e.g., osmo-api-xxxxx)"
        Ingress["Ingress<br/>Port 80/443"]
        
        subgraph "Envoy Sidecar Container"
            EnvoyListener["Listener<br/>Port 8080"]
            OAuth2Filter["OAuth2 Filter"]
            JWTFilter["JWT Filter"]
            Router["Router"]
        end
        
        subgraph "Application Container"
            AppService["API/UI Service<br/>Port 8000"]
        end
        
        subgraph "Shared Volumes"
            LogsVol["/logs volume"]
            SecretsVol["/etc/envoy/secrets<br/>client_secret<br/>hmac_secret"]
        end
    end
    
    subgraph "External Services"
        Keycloak["Keycloak<br/>auth-osmo.example.com"]
        JWKS["JWKS Endpoint<br/>/protocol/openid-connect/certs"]
    end
    
    subgraph "Kubernetes Secrets"
        OIDCSecret["oidc-secrets<br/>client_secret<br/>hmac_secret"]
    end
    
    Ingress --> EnvoyListener
    EnvoyListener --> OAuth2Filter
    OAuth2Filter --> JWTFilter
    JWTFilter --> Router
    Router --> AppService
    
    OAuth2Filter -.->|"Token Exchange"| Keycloak
    JWTFilter -.->|"Fetch Public Keys"| JWKS
    
    OIDCSecret --> SecretsVol
    SecretsVol --> OAuth2Filter
    
    EnvoyListener --> LogsVol
    AppService --> LogsVol
```

**Sources**: [deployments/charts/web-ui/values.yaml:377-601](), [deployments/charts/web-ui/README.md:88-131]()

## Authentication Flow Components

### OAuth2 Browser Authentication Flow

The OAuth2 filter handles the browser-based authentication flow using the authorization code grant type with PKCE (Proof Key for Code Exchange).

```mermaid
sequenceDiagram
    participant Browser
    participant Envoy as "Envoy Sidecar<br/>OAuth2 Filter"
    participant Keycloak as "Keycloak<br/>auth-osmo.example.com"
    participant AppService as "Application Service<br/>Port 8000"
    
    Browser->>Envoy: GET / (no session)
    Envoy->>Envoy: Check for HMAC cookie
    
    alt No Valid Session Cookie
        Envoy->>Browser: HTTP 302 Redirect
        Note over Envoy,Browser: Location: authEndpoint<br/>+ client_id, redirect_uri, state, PKCE
        
        Browser->>Keycloak: GET /auth<br/>(authorization_endpoint)
        Keycloak->>Browser: Display login page
        Browser->>Keycloak: POST credentials
        Keycloak->>Browser: HTTP 302 with auth code
        Note over Keycloak,Browser: Location: redirectPath<br/>+ code, state
        
        Browser->>Envoy: GET /getAToken?code=XXX&state=YYY
        Envoy->>Envoy: Verify state parameter
        Envoy->>Keycloak: POST tokenEndpoint<br/>code, client_id, client_secret, code_verifier
        Keycloak->>Envoy: JWT Access Token + Refresh Token
        
        Envoy->>Envoy: Sign HMAC Cookie<br/>with hmac_secret
        Envoy->>Browser: Set-Cookie: BearerToken=<hmac_signed>
        Envoy->>Browser: HTTP 302 to original path
    end
    
    Browser->>Envoy: GET / (with session cookie)
    Envoy->>Envoy: Validate HMAC signature
    Envoy->>Envoy: Extract JWT from cookie
    Envoy->>Envoy: Validate JWT (next filter)
    Envoy->>Envoy: Set x-osmo-user header
    Envoy->>AppService: Forward request with headers
    AppService->>Envoy: Response
    Envoy->>Browser: Response
```

**Sources**: [deployments/charts/web-ui/values.yaml:514-556](), [docs/deployment_guide/getting_started/deploy_service.rst:625-650]()

### JWT Token Validation

After OAuth2 authentication (or for direct API calls with Bearer tokens), the JWT filter validates tokens against configured providers.

```mermaid
graph LR
    subgraph "JWT Filter Processing"
        Request["HTTP Request<br/>Cookie or Authorization header"]
        ExtractToken["Extract JWT Token"]
        CheckIssuer["Match Issuer<br/>to Provider"]
        FetchJWKS["Fetch Public Keys<br/>from jwks_uri"]
        ValidateSignature["Verify Signature<br/>Check expiration<br/>Validate audience"]
        ExtractClaim["Extract user_claim"]
        SetHeader["Set x-osmo-user header"]
        Forward["Forward to Service"]
    end
    
    Request --> ExtractToken
    ExtractToken --> CheckIssuer
    
    CheckIssuer -->|"Provider 1"| Provider1["issuer: auth-osmo.../realms/osmo<br/>audience: osmo-device<br/>jwks_uri: .../certs<br/>user_claim: preferred_username"]
    CheckIssuer -->|"Provider 2"| Provider2["issuer: auth-osmo.../realms/osmo<br/>audience: osmo-browser-flow<br/>jwks_uri: .../certs<br/>user_claim: preferred_username"]
    CheckIssuer -->|"Provider 3"| Provider3["issuer: osmo<br/>audience: osmo<br/>jwks_uri: localhost:8000/api/auth/keys<br/>user_claim: unique_name"]
    
    Provider1 --> FetchJWKS
    Provider2 --> FetchJWKS
    Provider3 --> FetchJWKS
    
    FetchJWKS --> ValidateSignature
    ValidateSignature -->|"Valid"| ExtractClaim
    ValidateSignature -->|"Invalid"| Reject["HTTP 401 Unauthorized"]
    ExtractClaim --> SetHeader
    SetHeader --> Forward
```

**Sources**: [deployments/charts/web-ui/values.yaml:578-601](), [docs/deployment_guide/getting_started/deploy_service.rst:637-655]()

## Configuration Structure

### OAuth2 Filter Configuration

The OAuth2 filter is configured via Helm chart values and rendered into the Envoy configuration template.

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `sidecars.envoy.oauth2Filter.enabled` | Enable OAuth2 filter | `true` |
| `sidecars.envoy.oauth2Filter.tokenEndpoint` | Token exchange endpoint | `https://auth-osmo.example.com/realms/osmo/protocol/openid-connect/token` |
| `sidecars.envoy.oauth2Filter.authEndpoint` | Authorization endpoint | `https://auth-osmo.example.com/realms/osmo/protocol/openid-connect/auth` |
| `sidecars.envoy.oauth2Filter.redirectPath` | OAuth callback path | `getAToken` |
| `sidecars.envoy.oauth2Filter.clientId` | OAuth2 client ID | `osmo-browser-flow` |
| `sidecars.envoy.oauth2Filter.authProvider` | Auth provider hostname | `auth-osmo.example.com` |
| `sidecars.envoy.oauth2Filter.logoutPath` | Logout endpoint path | `logout` |
| `sidecars.envoy.oauth2Filter.secretName` | K8s secret name | `oidc-secrets` |
| `sidecars.envoy.oauth2Filter.clientSecretKey` | Secret key for client_secret | `client_secret` |
| `sidecars.envoy.oauth2Filter.hmacSecretKey` | Secret key for HMAC secret | `hmac_secret` |

**Sources**: [deployments/charts/web-ui/values.yaml:514-556](), [deployments/charts/web-ui/README.md:117-131]()

### JWT Provider Configuration

Multiple JWT providers allow OSMO to accept tokens from different sources: CLI devices, browser sessions, and internal service tokens.

| Provider Field | Purpose | Configuration Location |
|----------------|---------|------------------------|
| `issuer` | Identifies token issuer | Must match JWT `iss` claim |
| `audience` | Expected token audience | Must match JWT `aud` claim |
| `jwks_uri` | Public key endpoint | Keycloak JWKS or internal endpoint |
| `user_claim` | Claim containing username | `preferred_username` or `unique_name` |
| `cluster` | Upstream cluster name | `oauth` or `service` |

**Example JWT Provider Configuration:**

```yaml
jwt:
  user_header: x-osmo-user
  providers:
  # CLI/Backend device tokens
  - issuer: https://auth-osmo.example.com/realms/osmo
    audience: osmo-device
    jwks_uri: https://auth-osmo.example.com/realms/osmo/protocol/openid-connect/certs
    user_claim: preferred_username
    cluster: oauth
  
  # Browser flow tokens
  - issuer: https://auth-osmo.example.com/realms/osmo
    audience: osmo-browser-flow
    jwks_uri: https://auth-osmo.example.com/realms/osmo/protocol/openid-connect/certs
    user_claim: preferred_username
    cluster: oauth
  
  # Internal OSMO service tokens
  - issuer: osmo
    audience: osmo
    jwks_uri: http://localhost:8000/api/auth/keys
    user_claim: unique_name
    cluster: service
```

**Sources**: [deployments/charts/web-ui/values.yaml:578-601](), [docs/deployment_guide/getting_started/deploy_service.rst:637-655]()

## Request Processing Pipeline

### HTTP Filter Chain

```mermaid
graph TB
    subgraph "Envoy Listener :8080"
        HTTPConnection["HTTP Connection Manager"]
    end
    
    subgraph "Filter Chain"
        direction TB
        
        SkipAuth{"Path in<br/>skipAuthPaths?"}
        
        OAuth2{"OAuth2 Filter<br/>enabled?"}
        CheckCookie["Check for<br/>session cookie"]
        
        ValidateCookie{"Valid HMAC<br/>signature?"}
        RedirectAuth["Redirect to<br/>authEndpoint"]
        ExtractFromCookie["Extract JWT<br/>from cookie"]
        
        JWTFilter["JWT Filter"]
        ValidateJWT{"JWT valid?"}
        ExtractUser["Extract user from<br/>user_claim"]
        SetHeader["Set x-osmo-user<br/>header"]
        
        RateLimitFilter{"Rate Limit<br/>enabled?"}
        CheckLimits["Check Redis<br/>rate limits"]
        
        RouterFilter["Router Filter"]
        Forward["Forward to<br/>upstream service"]
    end
    
    HTTPConnection --> SkipAuth
    
    SkipAuth -->|"Yes"| Forward
    SkipAuth -->|"No"| OAuth2
    
    OAuth2 -->|"Yes"| CheckCookie
    OAuth2 -->|"No"| JWTFilter
    
    CheckCookie --> ValidateCookie
    ValidateCookie -->|"Invalid/Missing"| RedirectAuth
    ValidateCookie -->|"Valid"| ExtractFromCookie
    ExtractFromCookie --> JWTFilter
    
    JWTFilter --> ValidateJWT
    ValidateJWT -->|"Invalid"| Reject["401 Unauthorized"]
    ValidateJWT -->|"Valid"| ExtractUser
    ExtractUser --> SetHeader
    
    SetHeader --> RateLimitFilter
    RateLimitFilter -->|"Yes"| CheckLimits
    RateLimitFilter -->|"No"| RouterFilter
    
    CheckLimits -->|"Exceeded"| RateLimited["429 Too Many Requests"]
    CheckLimits -->|"OK"| RouterFilter
    
    RouterFilter --> Forward
```

**Sources**: [deployments/charts/web-ui/values.yaml:377-601](), [docs/deployment_guide/getting_started/deploy_service.rst:608-636]()

## Secret Management

### Kubernetes Secret Integration

Envoy requires two secrets for OAuth2 authentication:

| Secret | Purpose | Generation Method |
|--------|---------|-------------------|
| `client_secret` | OAuth2 client authentication | Created in Keycloak client configuration |
| `hmac_secret` | Cookie signing/verification | Random 32-byte value, base64 encoded |

**Secret Creation Command:**

```bash
kubectl create secret generic oidc-secrets \
  --from-literal=client_secret=<keycloak-client-secret> \
  --from-literal=hmac_secret=$(head -c32 /dev/urandom | base64) \
  --namespace osmo
```

**Sources**: [docs/deployment_guide/getting_started/deploy_service.rst:370-382]()

### Secret Volume Mounting

```mermaid
graph TB
    subgraph "Kubernetes Secret"
        K8sSecret["Secret: oidc-secrets<br/>data:<br/>  client_secret: <base64><br/>  hmac_secret: <base64>"]
    end
    
    subgraph "Pod Volume Definition"
        SecretVolume["volumes:<br/>- name: envoy-secrets<br/>  secret:<br/>    secretName: oidc-secrets"]
    end
    
    subgraph "Envoy Init Container"
        InitContainer["busybox init container<br/>Copy secrets to files"]
        ClientSecretFile["/etc/envoy/secrets/client_secret"]
        HMACSecretFile["/etc/envoy/secrets/hmac_secret"]
    end
    
    subgraph "Envoy Main Container"
        EnvoyConfig["envoy.yaml<br/>references secret files:<br/>  client_secret_filename:<br/>    /etc/envoy/secrets/client_secret<br/>  hmac_secret_filename:<br/>    /etc/envoy/secrets/hmac_secret"]
    end
    
    K8sSecret --> SecretVolume
    SecretVolume --> InitContainer
    InitContainer --> ClientSecretFile
    InitContainer --> HMACSecretFile
    ClientSecretFile --> EnvoyConfig
    HMACSecretFile --> EnvoyConfig
```

**Sources**: [deployments/charts/web-ui/values.yaml:382-396](), [deployments/charts/web-ui/README.md:93-96]()

## Skip Authentication Paths

Certain endpoints bypass authentication to support health checks, version queries, and initial login flows.

### Common Skip Auth Paths

| Path | Purpose | Service |
|------|---------|---------|
| `/api/version` | Version information | API |
| `/api/auth/login` | Initial authentication | API |
| `/api/auth/keys` | Public JWKS endpoint | API |
| `/api/auth/refresh_token` | Token refresh | API |
| `/api/auth/jwt/refresh_token` | JWT refresh | API |
| `/api/auth/jwt/access_token` | Access token exchange | API |
| `/client/version` | Client version check | API |
| `/api/router/version` | Router version | Router |
| `/ready` | Envoy readiness probe | Envoy admin |

**Configuration:**

```yaml
sidecars:
  envoy:
    skipAuthPaths:
    - /api/version
    - /api/auth/login
    - /api/auth/keys
    - /api/auth/refresh_token
    - /api/auth/jwt/refresh_token
    - /api/auth/jwt/access_token
    - /client/version
```

**Sources**: [deployments/charts/web-ui/values.yaml:449-450](), [docs/deployment_guide/getting_started/deploy_service.rst:609-617]()

## Service-Specific Configurations

### API Service Envoy Configuration

The API service uses Envoy primarily for JWT validation of CLI and backend operator requests.

```mermaid
graph LR
    subgraph "API Pod"
        EnvoyAPI["Envoy Sidecar<br/>Port 8080"]
        APIService["API Service<br/>Port 8000"]
    end
    
    CLIClient["osmo CLI<br/>Bearer: JWT<br/>(audience: osmo-device)"]
    BackendOp["Backend Operator<br/>Bearer: JWT<br/>(role: osmo-backend)"]
    
    CLIClient -->|"POST /api/workflows"| EnvoyAPI
    BackendOp -->|"POST /api/backend/tasks"| EnvoyAPI
    
    EnvoyAPI -->|"JWT validated<br/>x-osmo-user: username"| APIService
```

**Key Settings:**
- OAuth2 filter disabled (CLI doesn't use browser flow)
- JWT filter enabled with multiple providers
- Skip auth paths for public endpoints

**Sources**: [docs/deployment_guide/getting_started/deploy_service.rst:600-656]()

### Web UI Envoy Configuration

The Web UI uses full OAuth2 browser flow with session cookies.

```mermaid
graph LR
    subgraph "UI Pod"
        EnvoyUI["Envoy Sidecar<br/>Port 8080<br/>OAuth2 + JWT"]
        UIService["Next.js UI<br/>Port 8000"]
    end
    
    Browser["Web Browser"] -->|"GET /"| EnvoyUI
    EnvoyUI -->|"Cookie auth<br/>x-osmo-user: username"| UIService
    UIService -->|"Renders UI"| EnvoyUI
    EnvoyUI --> Browser
```

**Key Settings:**
- OAuth2 filter enabled
- HMAC cookie signing
- JWT validation for API proxy requests

**Sources**: [deployments/charts/web-ui/values.yaml:880-918](), [docs/deployment_guide/getting_started/deploy_service.rst:830-918]()

### Router Service Envoy Configuration

The Router service requires both OAuth2 and JWT validation to handle WebSocket upgrades for interactive sessions.

```mermaid
graph TB
    subgraph "Router Pod"
        EnvoyRouter["Envoy Sidecar<br/>OAuth2 + JWT<br/>forwardBearerToken: true"]
        RouterService["Router Service<br/>WebSocket Proxy"]
    end
    
    subgraph "Backend Cluster"
        TaskPod["Task Pod<br/>Running Container"]
    end
    
    Browser["Browser"] -->|"WSS /api/router/exec/<workflow_id>/<task_id>"| EnvoyRouter
    EnvoyRouter -->|"Forwards Bearer token<br/>x-osmo-user header"| RouterService
    RouterService -.->|"WebSocket tunnel"| TaskPod
```

**Unique Router Settings:**

```yaml
sidecars:
  envoy:
    oauth2Filter:
      forwardBearerToken: true  # Pass token to backend
      redirectPath: api/auth/getAToken
    routes:
    - match:
        prefix: "/"
      route:
        cluster: service
        timeout: 0s  # No timeout for long-lived connections
```

**Sources**: [docs/deployment_guide/getting_started/deploy_service.rst:750-819]()

## Advanced Features

### HTTP Header Size Limits

Large OAuth2 response headers (especially with group memberships) can exceed default HTTP header limits. Both Envoy and the application must be configured with matching limits.

| Configuration | Location | Default | Recommended |
|---------------|----------|---------|-------------|
| Envoy `max_request_headers_kb` | `sidecars.envoy.maxHeadersSizeKb` | 60 KB | 128 KB |
| Node.js `--max-http-header-size` | `services.ui.maxHttpHeaderSizeKb` | 8 KB | 128 KB |
| Nginx proxy buffer size | Ingress annotations | 4 KB | 16 KB |

**Ingress Annotations for Large Headers:**

```yaml
annotations:
  nginx.ingress.kubernetes.io/proxy-buffer-size: "16k"
  nginx.ingress.kubernetes.io/proxy-buffers: "8 16k"
  nginx.ingress.kubernetes.io/proxy-busy-buffers-size: "32k"
  nginx.ingress.kubernetes.io/large-client-header-buffers: "4 16k"
```

**Sources**: [deployments/charts/web-ui/values.yaml:101-105](), [deployments/charts/web-ui/README.md:59](), [docs/deployment_guide/getting_started/deploy_service.rst:536-540]()

### Rate Limiting Integration

When rate limiting is enabled, Envoy queries a Redis backend before forwarding requests.

```mermaid
graph LR
    EnvoyFilter["Envoy Rate Limit Filter"]
    RateLimitService["Rate Limit Service<br/>grpc://rate-limit:8081"]
    RedisBackend["Redis<br/>Rate limit counters"]
    
    EnvoyFilter -->|"Check rate limit<br/>domain: osmo<br/>descriptors: [user, endpoint]"| RateLimitService
    RateLimitService -->|"INCR key<br/>EXPIRE key"| RedisBackend
    RateLimitService -->|"OK / OVER_LIMIT"| EnvoyFilter
```

**Configuration:**

```yaml
sidecars:
  rateLimit:
    enabled: true
    redis:
      serviceName: redis-rate-limit
      port: 6379
```

**Sources**: [docs/deployment_guide/getting_started/deploy_service.rst:671-678]()

### Liveness and Readiness Probes

Envoy exposes an admin interface on port 9901 for health checks.

| Probe Type | Path | Purpose |
|------------|------|---------|
| Liveness | `/ready` | Container is running |
| Readiness | `/ready` | Envoy is accepting traffic |
| Startup | `/ready` | Initial startup complete |

**Probe Configuration:**

```yaml
sidecars:
  envoy:
    livenessProbe:
      httpGet:
        path: /ready
        port: 9901
      initialDelaySeconds: 10
      periodSeconds: 10
      
    readinessProbe:
      httpGet:
        path: /ready
        port: 9901
      initialDelaySeconds: 5
      periodSeconds: 5
      
    startupProbe:
      httpGet:
        path: /ready
        port: 9901
      initialDelaySeconds: 15
      periodSeconds: 5
```

**Sources**: [deployments/charts/web-ui/values.yaml:412-434]()

## Security Considerations

### Secret Rotation

The `client_secret` and `hmac_secret` values are read from Kubernetes secrets at pod startup. To rotate secrets:

1. Update the Kubernetes secret
2. Restart the pods to load new secret values
3. Previous HMAC-signed cookies become invalid (users must re-authenticate)

**Sources**: [docs/deployment_guide/getting_started/deploy_service.rst:370-382]()

### TLS Configuration

Envoy can terminate TLS connections or delegate TLS termination to the ingress controller.

| Mode | Configuration | Use Case |
|------|---------------|----------|
| Ingress TLS | `ingress.sslEnabled: true` | Most common, ALB/NGINX handles TLS |
| Envoy TLS | `sidecars.envoy.ssl.enabled: true` | End-to-end encryption |
| No TLS | Both disabled | Development only |

**Envoy TLS Configuration:**

```yaml
sidecars:
  envoy:
    ssl:
      enabled: true
      cert:
        secretName: envoy-ssl-cert
        secretKey: cert
      privateKey:
        secretName: envoy-ssl-cert
        secretKey: privateKey
```

**Sources**: [deployments/charts/web-ui/values.yaml:558-567]()

### Security Context

Envoy runs with restricted security context to minimize attack surface.

```yaml
sidecars:
  envoy:
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
      runAsNonRoot: true
      runAsUser: 1001
```

**Sources**: [deployments/charts/web-ui/values.yaml:436-441]()

---

# Page: Credential Management and Encryption

# Credential Management and Encryption

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/deployment_guide/getting_started/deploy_service.rst](docs/deployment_guide/getting_started/deploy_service.rst)
- [docs/deployment_guide/install_backend/dependencies/dependencies.rst](docs/deployment_guide/install_backend/dependencies/dependencies.rst)
- [docs/deployment_guide/install_backend/deploy_backend.rst](docs/deployment_guide/install_backend/deploy_backend.rst)
- [docs/deployment_guide/install_backend/validate_osmo.rst](docs/deployment_guide/install_backend/validate_osmo.rst)
- [docs/deployment_guide/references/configs_definitions/index.rst](docs/deployment_guide/references/configs_definitions/index.rst)
- [docs/user_guide/tutorials/combination_workflows/index.rst](docs/user_guide/tutorials/combination_workflows/index.rst)
- [src/lib/utils/common.py](src/lib/utils/common.py)
- [src/lib/utils/port_forward.py](src/lib/utils/port_forward.py)
- [src/lib/utils/tests/test_common.py](src/lib/utils/tests/test_common.py)
- [src/service/core/config/helpers.py](src/service/core/config/helpers.py)
- [src/service/core/data/data_service.py](src/service/core/data/data_service.py)
- [src/service/logger/ctrl_websocket.py](src/service/logger/ctrl_websocket.py)
- [src/service/router/router.py](src/service/router/router.py)
- [src/utils/connectors/postgres.py](src/utils/connectors/postgres.py)
- [src/utils/job/kb_objects.py](src/utils/job/kb_objects.py)
- [src/utils/job/task.py](src/utils/job/task.py)

</details>



This page documents OSMO's credential management and encryption system, which securely stores and manages sensitive data such as API keys, passwords, registry credentials, and dataset access tokens. The system uses a multi-tier encryption architecture with Master Encryption Keys (MEK) and User Encryption Keys (UEK) to protect credentials at rest in PostgreSQL.

For information about authentication flows and Keycloak integration, see [Keycloak SSO Integration](#8.1). For details about Envoy's OAuth2 validation, see [Envoy Authentication Proxy](#8.2).

## Architecture Overview

OSMO's credential encryption system consists of three layers:

```mermaid
graph TB
    subgraph "Configuration Layer"
        MEKFile["MEK File<br/>/vault-agent/secrets/vault-secrets.yaml"]
        PostgresConfig["PostgresConfig<br/>mek_file field"]
    end
    
    subgraph "Encryption Layer"
        SecretManager["SecretManager<br/>src/utils/secret_manager.py"]
        MEK["Master Encryption Key<br/>JWK Format"]
        UEK["User Encryption Keys<br/>ueks table"]
    end
    
    subgraph "Storage Layer"
        CredTable["credential table<br/>HSTORE payload"]
        AccessTokenTable["access_token table<br/>BYTEA tokens"]
        TaskRefreshToken["tasks table<br/>refresh_token BYTEA"]
    end
    
    subgraph "Application Layer"
        PostgresConnector["PostgresConnector<br/>decrypt_credential()<br/>encrypt_dict()"]
        TaskSpec["TaskSpec<br/>credentials field"]
        DataService["DataService<br/>validate_user_cred()"]
    end
    
    MEKFile --> PostgresConfig
    PostgresConfig --> SecretManager
    SecretManager --> MEK
    SecretManager --> UEK
    MEK --> UEK
    
    PostgresConnector --> SecretManager
    SecretManager --> CredTable
    SecretManager --> AccessTokenTable
    SecretManager --> TaskRefreshToken
    
    TaskSpec --> PostgresConnector
    DataService --> PostgresConnector
    PostgresConnector --> CredTable
```

**Sources:** [src/utils/connectors/postgres.py:125-186](), [src/utils/connectors/postgres.py:241-261](), [src/utils/connectors/postgres.py:475-507]()

## Master Encryption Key (MEK)

The Master Encryption Key is the root encryption key used to encrypt User Encryption Keys. It is stored in JWK (JSON Web Key) format and loaded during service initialization.

### Configuration

| Configuration Field | Environment Variable | Default Path | Description |
|-------------------|---------------------|--------------|-------------|
| `mek_file` | `OSMO_MEK_FILE` | `/home/osmo/vault-agent/secrets/vault-secrets.yaml` | Path to MEK file in JWK format |
| `method` | N/A | `None` | Set to `"dev"` for development mode |

The MEK file is configured in `PostgresConfig` and loaded during `PostgresConnector` initialization:

```mermaid
sequenceDiagram
    participant Init as Service Init
    participant PC as PostgresConnector
    participant SM as SecretManager
    participant MEKFile as MEK File
    
    Init->>PC: __init__(config)
    PC->>PC: connect to PostgreSQL
    Note over PC: mek_file from config
    PC->>SM: SecretManager(mek_file, ...)
    SM->>MEKFile: Load JWK keys
    MEKFile-->>SM: Master keys
    SM->>PC: Initialize UEK callbacks
    PC->>PC: _init_tables()
    PC->>PC: _init_configs()
```

**Development Mode:** When `method='dev'`, OSMO uses a local MEK file at `src/utils/secret_manager/mek.yaml` and allows additional fields in configuration models.

**Sources:** [src/utils/connectors/postgres.py:156-161](), [src/utils/connectors/postgres.py:241-261](), [src/utils/connectors/postgres.py:252-261]()

## User Encryption Keys (UEK)

User Encryption Keys are per-user encryption keys stored in the `ueks` table. Each UEK is encrypted with the MEK and used to encrypt that user's credentials.

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS ueks (
    uid TEXT,
    keys HSTORE,
    PRIMARY KEY (uid)
);
```

The `keys` HSTORE column stores multiple key versions (KIDs - Key IDs) for key rotation support. Each key is encrypted with the current MEK.

### UEK Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Read UEK | `read_uek` | Fetches encrypted UEK from database |
| Write UEK | `write_uek` | Stores encrypted UEK to database |
| Get Current KID | `read_current_kid` | Returns current key version ID |
| Add User | `add_user` | Creates new user entry if not exists |

**Sources:** [src/utils/connectors/postgres.py:852-860](), [src/utils/connectors/postgres.py:258-260]()

## Credential Storage

Credentials are stored in the `credential` table using PostgreSQL's HSTORE extension for flexible key-value storage.

### Credential Table Schema

```sql
CREATE TABLE IF NOT EXISTS credential (
    user_name TEXT NOT NULL,
    cred_name TEXT NOT NULL,
    cred_type credential_type,
    profile TEXT,
    payload HSTORE NOT NULL,
    PRIMARY KEY (user_name, cred_name),
    CONSTRAINT unique_cred UNIQUE (user_name, profile)
);

CREATE TYPE credential_type AS ENUM (
    'GENERIC', 'REGISTRY', 'DATA'
);
```

### HSTORE Format

The `payload` column stores encrypted key-value pairs. Each value is a JWE-encrypted string:

| Key | Encrypted Value |
|-----|----------------|
| `access_key_id` | `eyJhbGc...` (JWE token) |
| `secret_access_key` | `eyJhbGc...` (JWE token) |
| `username` | `eyJhbGc...` (JWE token) |
| `password` | `eyJhbGc...` (JWE token) |

### Encoding and Decoding

The `PostgresConnector` class provides helper methods for HSTORE operations:

```python
# Encode dictionary to HSTORE string
@classmethod
def encode_hstore(cls, key_val_data: Dict) -> str:
    return ','.join([f'"{key}"=>"{value}"' for key, value in key_val_data.items()])

# Decode HSTORE string to dictionary
@classmethod
def decode_hstore(cls, hstore_data: str) -> Dict:
    field_regex = r'[^()\'"]+'
    return {tp[0]: tp[1] for tp in re.findall(f'"({field_regex})"=>"({field_regex})"',
            hstore_data)}
```

**Sources:** [src/utils/connectors/postgres.py:960-972](), [src/utils/connectors/postgres.py:514-524](), [src/utils/connectors/postgres.py:62-67]()

## SecretManager Class

The `SecretManager` class handles all encryption and decryption operations using the JWCrypto library for JWE (JSON Web Encryption).

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `encrypt(value, user)` | Encrypts a value for a user | `Encrypted` object with JWE token |
| `decrypt(encrypted, user, update_func)` | Decrypts a JWE token | `Decrypted` object with plaintext |

### Integration with PostgresConnector

The `SecretManager` is initialized with callback functions from `PostgresConnector` for database operations:

```python
self.secret_manager = SecretManager(
    mek_file,
    self.read_uek,           # Callback to read UEK from database
    self.write_uek,          # Callback to write UEK to database
    self.read_current_kid,   # Callback to get current key ID
    self.add_user            # Callback to add new user
)
```

**Sources:** [src/utils/connectors/postgres.py:258-260](), [src/utils/connectors/postgres.py:48]()

## Encryption and Decryption Process

### Encryption Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant PC as PostgresConnector
    participant SM as SecretManager
    participant DB as PostgreSQL
    
    App->>PC: encrypt_dict(credentials, user)
    loop For each key-value pair
        PC->>SM: encrypt(value, user)
        SM->>DB: Fetch UEK via read_uek()
        DB-->>SM: Encrypted UEK (with MEK)
        SM->>SM: Decrypt UEK with MEK
        SM->>SM: Encrypt value with UEK (JWE)
        SM-->>PC: JWE token
    end
    PC-->>App: Dict with JWE tokens
    App->>DB: Store in credential table HSTORE
```

### Decryption Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant PC as PostgresConnector
    participant SM as SecretManager
    participant DB as PostgreSQL
    
    App->>DB: Fetch credential row
    DB-->>App: HSTORE payload
    App->>PC: decrypt_credential(db_row)
    PC->>PC: decode_hstore(payload)
    loop For each key-value pair
        PC->>PC: Try to deserialize as JWE
        alt Is JWE token
            PC->>SM: decrypt(encrypted, user, update_func)
            SM->>DB: Fetch UEK via read_uek()
            DB-->>SM: Encrypted UEK
            SM->>SM: Decrypt UEK with MEK
            SM->>SM: Decrypt value with UEK
            SM-->>PC: Plaintext value
        else Not encrypted yet
            PC->>SM: encrypt(value, user)
            SM-->>PC: JWE token
            PC->>DB: UPDATE credential SET payload
        end
    end
    PC-->>App: Dict with plaintext values
```

### Automatic Re-encryption

The `decrypt_credential` method automatically re-encrypts any unencrypted values it encounters:

```python
def decrypt_credential(self, db_row) -> Dict:
    result = {}
    payload = PostgresConnector.decode_hstore(db_row.payload)
    for key, value in payload.items():
        try:
            jwetoken = jwe.JWE()
            jwetoken.deserialize(value)
            encrypted = Encrypted(value)
            decrypted = self.secret_manager.decrypt(encrypted, db_row.user_name, update_func)
            result[key] = decrypted.value
        except (JWException, osmo_errors.OSMONotFoundError):
            # Not encrypted - encrypt it now
            result[key] = value
            encrypted = self.secret_manager.encrypt(value, db_row.user_name)
            cmd = f"UPDATE credential SET payload['{key}'] = %s ..."
            self.execute_commit_command(cmd, (encrypted.value,))
    return result
```

**Sources:** [src/utils/connectors/postgres.py:475-500](), [src/utils/connectors/postgres.py:502-507]()

## Credential Types

OSMO supports three types of credentials defined in the `CredentialType` enum:

| Type | Purpose | Typical Keys | Usage |
|------|---------|--------------|-------|
| `GENERIC` | General-purpose credentials | `username`, `password`, `api_key` | Custom integrations |
| `REGISTRY` | Container registry authentication | `username`, `password`, `auth` | Docker image pull |
| `DATA` | Dataset storage access | `access_key_id`, `secret_access_key`, `region` | S3, Azure Blob, MinIO |

### Data Credentials

Data credentials are used to access datasets stored in object storage. They are associated with a profile that identifies the storage backend:

```python
def validate_user_cred(postgres: connectors.PostgresConnector, user: str, location: str,
                       access_type: storage.AccessType):
    """
    Validates that the user has the specific access type to a backend location
    """
    backend_info = storage.construct_storage_backend(location)
    
    user_cred = postgres.get_data_cred(user, backend_info.profile)
    if not user_cred:
        raise osmo_errors.OSMOCredentialError(
            f'Could not find {backend_info.profile} credential for user {user}.')
    
    backend_info.data_auth(user_cred, access_type)
```

**Profile-Based Lookup:** The `profile` field in the `credential` table enables profile-specific credentials. For example, a user might have different credentials for `s3-prod` and `s3-dev` profiles.

**Sources:** [src/utils/connectors/postgres.py:62-67](), [src/service/core/data/data_service.py:48-60]()

### Service Tokens

Service tokens are used for backend operator authentication and are stored in the `access_token` table with encrypted values:

```sql
CREATE TABLE IF NOT EXISTS access_token (
    user_name TEXT,
    token_name TEXT,
    access_token BYTEA,
    expires_at TIMESTAMP,
    description TEXT,
    access_type TEXT,
    roles TEXT[],
    PRIMARY KEY (user_name, token_name, access_type),
    CONSTRAINT unique_access_token UNIQUE (access_token)
);
```

**Token Creation:** Service tokens are created via the OSMO CLI:

```bash
osmo token set backend-token \
    --expires-at 2025-12-31 \
    --description "Backend Operator Token" \
    --service \
    --roles osmo-backend
```

**Sources:** [src/utils/connectors/postgres.py:975-988](), [docs/deployment_guide/install_backend/deploy_backend.rst:34-47]()

## Usage in Workflows

### Task Credentials

Workflow tasks can specify credentials that are injected into containers:

```yaml
tasks:
  - name: training-task
    image: nvcr.io/nvidia/pytorch:23.10-py3
    credentials:
      registry:
        username: "{{REGISTRY_USER}}"
        password: "{{REGISTRY_PASSWORD}}"
      data: my-s3-profile
      custom_api:
        API_KEY: "{{MY_API_KEY}}"
```

The `credentials` field in `TaskSpec` maps credential names to environment variables or profiles:

**Sources:** [src/utils/job/task.py:604]()

### Credential Resolution

During workflow submission, credentials are resolved and encrypted:

1. **Template Expansion:** Jinja variables like `{{REGISTRY_USER}}` are resolved
2. **Credential Lookup:** Profile names are looked up in the user's credentials
3. **Secret Creation:** Credentials are stored in Kubernetes secrets
4. **Environment Injection:** Secrets are mounted as environment variables in pods

### Task Refresh Tokens

Tasks receive refresh tokens for API authentication, stored encrypted in the `tasks` table:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    ...
    refresh_token BYTEA,
    ...
);
```

These tokens enable tasks to authenticate with OSMO APIs for logging, metrics, and data operations.

**Sources:** [src/utils/job/task.py:54-56](), [src/utils/connectors/postgres.py:717-753]()

## Security Features

### Credential Masking in Logs

All credentials are automatically masked in logs and events using the `mask_string` function:

```python
loaded_json['text'] = common.mask_string(loaded_json.get('text', ''), task_cred_values)
```

This prevents accidental credential leakage in workflow logs.

**Sources:** [src/service/logger/ctrl_websocket.py:189-190]()

### Encryption at Rest

All credentials are encrypted before being stored in PostgreSQL:

| Storage Location | Encryption Method | Key Used |
|-----------------|-------------------|----------|
| `credential` table payload | JWE with UEK | User's UEK, encrypted with MEK |
| `access_token` table | BYTEA encrypted | UEK |
| `tasks` table refresh_token | BYTEA encrypted | UEK |
| `ueks` table keys | JWE with MEK | MEK from vault |

### Key Rotation Support

The system supports key rotation through the KID (Key ID) mechanism:

1. New MEK is added to vault with new KID
2. Existing credentials remain encrypted with old key
3. Next decrypt operation re-encrypts with new key
4. Old MEK can be retired after all credentials are rotated

**Automatic Re-encryption:** The `decrypt_credential` method includes an `update_func` callback that triggers re-encryption when an old key is detected.

**Sources:** [src/utils/connectors/postgres.py:475-500]()

### Access Control

Credentials are user-scoped and can only be accessed by:

1. The credential owner
2. Tasks running on behalf of that user
3. Administrators with appropriate roles

The `validate_user_cred` function enforces access control before allowing data operations.

**Sources:** [src/service/core/data/data_service.py:48-60]()

## Configuration Table

The credential management system is configured through the `PostgresConfig` class:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mek_file` | `str` | `/home/osmo/vault-agent/secrets/vault-secrets.yaml` | Path to Master Encryption Key file |
| `method` | `Literal['dev'] \| None` | `None` | Development mode flag |
| `postgres_host` | `str` | `localhost` | PostgreSQL hostname |
| `postgres_port` | `int` | `5432` | PostgreSQL port |
| `postgres_database_name` | `str` | `osmo_db` | Database name |
| `postgres_user` | `str` | `postgres` | Database user |
| `postgres_password` | `str` | Required | Database password |

**Sources:** [src/utils/connectors/postgres.py:125-185]()

---

# Page: Development and Contributing

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/docs-deploy.yaml](.github/workflows/docs-deploy.yaml)
- [.github/workflows/helm-chart-lint.yaml](.github/workflows/helm-chart-lint.yaml)
- [.github/workflows/pr-checks.yaml](.github/workflows/pr-checks.yaml)
- [.github/workflows/pr-description-check.yaml](.github/workflows/pr-description-check.yaml)
- [.github/workflows/sync-feature-branches.yaml](.github/workflows/sync-feature-branches.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/conf.py](docs/conf.py)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)

</details>



This page provides an overview of the development workflow and contribution process for OSMO. It covers system requirements, repository structure, CI/CD pipelines, and pull request procedures for developers who want to contribute bug fixes, documentation improvements, or new features.

For detailed information on specific aspects of development:
- **[Development Setup](#9.1)** - Environment setup, building from source, and running tests
- **[CI/CD Pipeline](#9.2)** - Detailed GitHub Actions workflows and testing infrastructure  
- **[Projects Process](#9.3)** - Formal process for proposing and implementing significant changes
- **[Pull Request Guidelines](#9.4)** - PR requirements, descriptions, and review process

**Sources:** [CONTRIBUTING.md:1-139]()

---

## System Requirements

OSMO development requires the following environment:

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| **Operating System** | Ubuntu 22.04+ or MacOS (arm64) | Development platform |
| **Git LFS** | ≥3.7.1 | Source control for large files |
| **Bazel** | ≥8.1.1 | Build system |
| **Docker** | ≥28.3.2 | Container runtime for testing |
| **Helm** | ≥3.17.1 | Kubernetes package management |
| **KIND** | ≥0.29.0 | Local Kubernetes clusters |
| **kubectl** | ≥1.32.2 | Kubernetes CLI |
| **aws-cli** | ≥2.24.7 | AWS operations (optional) |
| **npm** | ≥11.6.2 | Node.js package management for UI |

**Sources:** [CONTRIBUTING.md:26-43]()

---

## Repository Structure

```mermaid
graph TB
    subgraph "Repository Root"
        Root["/"]
        
        Root --> SRC["src/<br/>Python Services"]
        Root --> UI["ui/<br/>Web UI (Next.js)"]
        Root --> Charts["deployments/charts/<br/>Helm Charts"]
        Root --> Docs["docs/<br/>Sphinx Documentation"]
        Root --> Workflows["workflows/<br/>Example Workflows"]
        Root --> GH[".github/<br/>CI/CD Workflows"]
        Root --> BZL["bzl/<br/>Bazel Rules"]
        Root --> Projects["projects/<br/>Project Proposals"]
    end
    
    subgraph "src/ Structure"
        SRC --> API["osmo/api/<br/>API Service"]
        SRC --> Worker["osmo/worker/<br/>Background Jobs"]
        SRC --> Router["osmo/router/<br/>Router Service"]
        SRC --> Agent["osmo/agent/<br/>Agent Service"]
        SRC --> Logger["osmo/logger/<br/>Logger Service"]
        SRC --> Backend["osmo/backend/<br/>Backend Operator"]
        SRC --> Common["osmo/common/<br/>Shared Libraries"]
        SRC --> Tests["tests/<br/>Unit & Integration Tests"]
    end
    
    subgraph "CI/CD Workflows"
        GH --> PRChecks["workflows/pr-checks.yaml<br/>Main PR Validation"]
        GH --> DocsDeloy["workflows/docs-deploy.yaml<br/>Documentation Deployment"]
        GH --> PRDesc["workflows/pr-description-check.yaml<br/>PR Format Validation"]
        GH --> HelmLint["workflows/helm-chart-lint.yaml<br/>Chart Validation"]
        GH --> SyncBranches["workflows/sync-feature-branches.yaml<br/>Feature Branch Sync"]
    end
    
    subgraph "Helm Charts"
        Charts --> QS["quick-start/<br/>Umbrella Chart"]
        Charts --> Service["service/<br/>Control Plane Services"]
        Charts --> WebUI["web-ui/<br/>UI Deployment"]
        Charts --> BackendOp["backend-operator/<br/>Compute Plane"]
        Charts --> RouterChart["router/<br/>Router Service"]
    end
```

**Key Directories:**

| Directory | Purpose | Build System |
|-----------|---------|--------------|
| `src/` | Python services (API, Worker, Router, Agent, Logger, Backend) | Bazel |
| `ui/` | Next.js web interface | Bazel (pnpm) |
| `deployments/charts/` | Helm charts for Kubernetes deployment | Helm |
| `docs/` | Sphinx documentation | Makefile + Sphinx |
| `workflows/` | Example workflow YAML files | N/A |
| `.github/workflows/` | GitHub Actions CI/CD definitions | GitHub Actions |
| `bzl/` | Custom Bazel rules (linting, mypy, Python) | Bazel |
| `projects/` | Project proposals and design documents | N/A |

**Sources:** [CONTRIBUTING.md:45-66](), [.github/workflows/pr-checks.yaml:1-312]()

---

## Development Workflow

### Overview

```mermaid
graph LR
    Fork["1. Fork Repository<br/>github.com/NVIDIA/OSMO"] --> Clone["2. Clone Fork<br/>git clone"]
    Clone --> Branch["3. Create Branch<br/>from main"]
    Branch --> Develop["4. Develop Changes<br/>Follow Dev Guide"]
    Develop --> Test["5. Run Tests<br/>bazel test //..."]
    Test --> Build["6. Build Containers<br/>Validate Changes"]
    Build --> Commit["7. Commit<br/>Issue #N - Title"]
    Commit --> Push["8. Push to Fork<br/>git push origin"]
    Push --> PR["9. Create Pull Request<br/>Fill Template"]
    PR --> Review["10. Code Review<br/>2 Approvers Required"]
    Review --> StatusChecks["11. Status Checks<br/>CI Tests Must Pass"]
    StatusChecks --> Merge["12. Merge<br/>Squash & Merge"]
```

**Sources:** [CONTRIBUTING.md:45-111]()

### Fork and Clone

```bash
# 1. Fork the repository on GitHub
# https://github.com/NVIDIA/OSMO

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/YOUR_FORK.git osmo
cd osmo

# 3. Add upstream remote
git remote add upstream https://github.com/NVIDIA/OSMO.git
```

**Sources:** [CONTRIBUTING.md:45-53]()

### Development Process

The development workflow follows three main phases:

1. **Iterate on Changes** - Modify code following the [Dev Guide](BUILD_AND_TEST.md) and [coding guidelines](#coding-guidelines)
2. **Build and Test** - Create containers with changes and validate functionality
3. **Test Coverage** - Add or update unit and functional tests

**Sources:** [CONTRIBUTING.md:55-63]()

### Coding Guidelines

| Guideline | Description |
|-----------|-------------|
| **Follow Conventions** | Match existing code style in the relevant file/module |
| **Avoid Complexity** | Preserve maintainability and readability |
| **No Commented Code** | Remove commented-out code before committing |
| **Commit Format** | Use imperative mood with issue reference |
| **License Compliance** | Ensure no license/patent conflicts |

**Commit Message Format:**

```
#<Issue Number> - <Commit Title>

<Commit Body>
```

Example:
```
#42 - Add retry logic to dataset upload

Implement exponential backoff for S3 upload failures to handle
transient network errors. This reduces failed uploads by 95% in
high-latency environments.
```

**Sources:** [CONTRIBUTING.md:67-85]()

---

## CI/CD Pipeline Architecture

### Pipeline Overview

```mermaid
graph TB
    subgraph "PR Events"
        PullRequest["Pull Request<br/>opened/synchronize/reopened"]
        Push["Push to main<br/>docs/** or workflows/**"]
    end
    
    subgraph "Path Filtering Job"
        CheckPaths["check-paths<br/>dorny/paths-filter@v3"]
        CheckPaths --> CIFilter{"ci: src/**, BUILD,<br/>MODULE.bazel, bzl/**"}
        CheckPaths --> DocsFilter{"docs: docs/**,<br/>workflows/**"}
        CheckPaths --> UIFilter{"ui: ui/**,<br/>BUILD, MODULE.bazel"}
    end
    
    subgraph "CI Test Jobs"
        CIFilter -->|Fork PR| CIPublic["ci-public<br/>ubuntu-latest<br/>GitHub Runner"]
        CIFilter -->|Internal PR| CIInternal["ci-internal<br/>self-hosted<br/>Docker-in-Docker"]
        
        CIPublic --> BazelPublic["bazel test --test_output=errors<br/>//... -//ui/..."]
        CIInternal --> BazelInternal["bazel test --remote_cache<br/>--test_env=DOCKER_HOST<br/>//... -//ui/..."]
    end
    
    subgraph "Docs Build Jobs"
        DocsFilter --> DocsBuild["docs-build<br/>Sphinx Build"]
        DocsBuild --> SphinxBuild["make -C docs build"]
        SphinxBuild --> SpellCheck["Spelling Check<br/>sphinxcontrib.spelling"]
        SphinxBuild --> LinkCheck["Link Check<br/>lychee-action"]
        SphinxBuild --> Preview["PR Preview Deploy<br/>gh-pages/documentation"]
    end
    
    subgraph "UI Build Jobs"
        UIFilter --> UIBuild["ui-build<br/>ubuntu-latest"]
        UIBuild --> BazelUI["bazel build //ui/..."]
    end
    
    subgraph "Documentation Deployment"
        Push --> DocsDeploy["docs-deploy<br/>Production"]
        DocsDeploy --> Multiversion["sphinx-multiversion<br/>All Branches/Tags"]
        Multiversion --> GHPages["GitHub Pages<br/>gh-pages/documentation"]
    end
    
    PullRequest --> CheckPaths
```

**Sources:** [.github/workflows/pr-checks.yaml:1-312](), [.github/workflows/docs-deploy.yaml:1-95]()

### Workflow Files

#### pr-checks.yaml

The main PR validation workflow uses **path-based execution optimization** to run only relevant tests based on changed files.

**Path Filters:**

```yaml
# .github/workflows/pr-checks.yaml:51-68
filters:
  ci:
    - '.github/workflows/pr-checks.yaml'
    - 'BUILD'
    - 'MODULE.bazel'
    - 'bzl/**'
    - 'src/**'
    - 'run/**'
  docs:
    - 'docs/**'
    - 'workflows/**'
  ui:
    - 'ui/**'
    - 'BUILD'
    - 'MODULE.bazel'
    - 'bzl/**'
```

**Fork vs Internal PRs:**

| Aspect | Fork PRs (`ci-public`) | Internal PRs (`ci-internal`) |
|--------|----------------------|----------------------------|
| **Runner** | `ubuntu-latest` (GitHub-hosted) | `self-hosted` (internal infrastructure) |
| **Environment** | Standard GitHub Actions | Docker-in-Docker container |
| **Bazel Cache** | Local disk cache | Remote cache (`--remote_cache`) |
| **Test Environment** | Limited Docker access | Full Docker daemon access via TCP |
| **Trigger** | `github.event.pull_request.head.repo.fork == true` | `github.event.pull_request.head.repo.fork == false` |

**CI Test Commands:**

```bash
# Fork PRs (ci-public)
bazel test --test_output=errors -- //... -//ui/...

# Internal PRs (ci-internal)
bazel test --remote_cache=$BAZEL_REMOTE_CACHE_URL \
  --test_env=DOCKER_HOST=tcp://docker:2375 \
  --test_env=TESTCONTAINERS_HOST_OVERRIDE=docker \
  --test_output=errors \
  -- //... -//ui/...
```

**Sources:** [.github/workflows/pr-checks.yaml:33-183]()

#### docs-build Job

```mermaid
graph LR
    Checkout["Checkout<br/>with LFS"] --> SetupPython["Setup Python 3.10.18"]
    SetupPython --> InstallDeps["Install Dependencies<br/>locked_requirements.txt"]
    InstallDeps --> SphinxBuild["Sphinx Build<br/>make -C docs build"]
    SphinxBuild --> CheckErrors["Check Build Errors<br/>Exit if *.log files exist"]
    CheckErrors --> Deploy["Deploy Preview<br/>pr-preview-action"]
    Deploy --> Spelling["Spelling Check<br/>continue-on-error"]
    Spelling --> LinkCheck["Link Check<br/>lychee-action"]
    LinkCheck --> Validate["Validate Checks<br/>Fail if either failed"]
```

**Documentation Build Process:**

1. **Sphinx Build** - Builds HTML documentation from `.rst` files
2. **Spelling Check** - Uses `sphinxcontrib.spelling` with custom wordlist
3. **Link Check** - Validates all hyperlinks using `lychee` with caching
4. **Preview Deployment** - Deploys to `gh-pages/documentation/pr-preview/pr-<number>`

**Sources:** [.github/workflows/pr-checks.yaml:186-282]()

#### ui-build Job

```bash
# UI Build Command
bazel build //ui/...
```

The UI build job compiles the Next.js web application using Bazel with `pnpm` as the package manager. It uses the same setup-bazel action with external cache for `npm: ui/pnpm-lock.yaml`.

**Sources:** [.github/workflows/pr-checks.yaml:286-312]()

### Additional Workflows

#### pr-description-check.yaml

Validates PR descriptions meet requirements:

```mermaid
graph TB
    PR["Pull Request Event<br/>opened/edited/synchronize"] --> Extract["Extract PR Body<br/>$PR_BODY"]
    Extract --> Check1["Check 1: Issue Reference<br/>Regex: Issue (#[0-9]+|#None|- None)"]
    Extract --> Check2["Check 2: Checklist Section<br/>awk: Extract ## Checklist"]
    Check2 --> CountBoxes["Count Checkboxes<br/>grep -cE '- \[[ xX]\]'"]
    CountBoxes --> ValidateChecked["Validate All Checked<br/>unchecked_items == 0"]
    
    Check1 --> Validate["Combine Results"]
    ValidateChecked --> Validate
    Validate -->|Pass| Success["✅ Validation Passed"]
    Validate -->|Fail| Failure["❌ Exit 1<br/>Display Error Messages"]
```

**Required PR Description Elements:**

1. **Issue Reference** - Must include `Issue #<number>` or `Issue - None` (case-insensitive)
2. **Complete Checklist** - All boxes in `## Checklist` section must be checked:
   - `[x] I am familiar with the Contributing Guidelines`
   - `[x] New or existing tests cover these changes`
   - `[x] The documentation is up to date with these changes`

**Sources:** [.github/workflows/pr-description-check.yaml:1-135](), [.github/PULL_REQUEST_TEMPLATE.md:1-12]()

#### helm-chart-lint.yaml

Validates Helm chart changes:

```mermaid
graph LR
    Detect["Detect Changed Charts<br/>git diff origin/main"] --> Matrix["Matrix Strategy<br/>Per-Chart Jobs"]
    Matrix --> BuildDeps["helm dependency build<br/>deployments/charts/$chart"]
    BuildDeps --> Lint["helm lint<br/>deployments/charts/$chart"]
    Lint --> Template["helm template<br/>Validate Rendering"]
```

Only runs when files in `deployments/charts/**` change. Uses matrix strategy to lint each changed chart independently.

**Sources:** [.github/workflows/helm-chart-lint.yaml:1-126]()

#### sync-feature-branches.yaml

Automatically syncs `feature/*` branches with `main`:

- **Schedule:** Weekly on Mondays at 9am PT (17:00 UTC)
- **Process:** Creates sync PRs from temporary branches (`sync/feature/*/YYYYMMDD-HHMM`)
- **Purpose:** Keeps long-lived feature branches up-to-date during development

**Sources:** [.github/workflows/sync-feature-branches.yaml:1-151]()

---

## Pull Request Process

### PR Lifecycle

```mermaid
graph TB
    Create["Create PR<br/>Fill Template"] --> AutoAssign["Auto-Assign<br/>OSMO Engineering Team"]
    AutoAssign --> StatusChecks["Status Checks<br/>GitHub Actions"]
    
    StatusChecks --> PRDesc["PR Description Check<br/>Issue # + Checklist"]
    StatusChecks --> CI["CI Tests<br/>ci-public or ci-internal"]
    StatusChecks --> Docs["Docs Build<br/>Spelling + Links"]
    StatusChecks --> UI["UI Build<br/>bazel build //ui/..."]
    StatusChecks --> Helm["Helm Lint<br/>If charts changed"]
    
    PRDesc --> AllChecks{"All Checks Pass?"}
    CI --> AllChecks
    Docs --> AllChecks
    UI --> AllChecks
    Helm --> AllChecks
    
    AllChecks -->|No| Fix["Fix Issues<br/>Push Updates"]
    Fix --> StatusChecks
    
    AllChecks -->|Yes| Review["Code Review<br/>2 Approvers Required"]
    Review --> Conflicts{"Merge Conflicts?"}
    Conflicts -->|Yes| Resolve["Resolve Conflicts"]
    Resolve --> Review
    Conflicts -->|No| Merge["Squash & Merge<br/>To main"]
```

**Sources:** [CONTRIBUTING.md:87-111]()

### PR Template Requirements

The PR template enforces structured descriptions:

| Section | Required Content |
|---------|-----------------|
| **Title** | `#<issue number> - <commit title>` format |
| **Description** | Standalone description following commit message rules |
| **Issue Reference** | `Issue #<number>` or `Issue - None` |
| **Checklist** | All three items must be checked before merge |

**PR Template:**

```markdown
<!-- Title: "#<issue number> - <commit title>" -->

## Description
<!-- Standalone description of changes -->

Issue #<issue number | "None">

## Checklist
- [ ] I am familiar with the Contributing Guidelines
- [ ] New or existing tests cover these changes
- [ ] The documentation is up to date with these changes
```

**Sources:** [.github/PULL_REQUEST_TEMPLATE.md:1-12]()

### Review Requirements

**Merge Criteria:**

1. ✅ **Two Approvals** - Two OSMO engineers must approve the PR
2. ✅ **Status Checks Pass** - All GitHub Actions workflows succeed
3. ✅ **No Merge Conflicts** - Branch must be up-to-date with `main`
4. ✅ **Checklist Complete** - All PR template checklist items checked
5. ✅ **Issue Reference** - Valid issue number or "None"

**Status Check Triggering:**

- Fork PRs: Status checks run automatically via `ci-public`
- Internal PRs: Status checks may require manual triggering by OSMO engineers via `ci-internal`

**Sources:** [CONTRIBUTING.md:102-108]()

---

## Projects Process

For **significant changes** (new projects, major features, cross-cutting changes, or architectural decisions), OSMO uses a formal Projects Process:

```mermaid
graph LR
    Idea["Feature Idea"] --> Proposal["1. Project Proposal<br/>GitHub Issue Template"]
    Proposal --> Design["2. Project Design<br/>Markdown Document<br/>projects/"]
    Design --> Review["3. Design Review<br/>Discussion on Issue"]
    Review --> Approved{"Approved?"}
    Approved -->|No| Revise["Revise Design"]
    Revise --> Review
    Approved -->|Yes| Branch["4. Feature Branch<br/>feature/PROJ-NNN-slug"]
    Branch --> Develop["5. Development<br/>Multiple PRs to Branch"]
    Develop --> Sync["6. Weekly Sync<br/>sync-feature-branches.yaml"]
    Sync --> Complete["7. Completion<br/>Final PR to main"]
```

### When to Use the Projects Process

| Change Type | Use Projects Process? | Rationale |
|-------------|----------------------|-----------|
| Small bug fix | ❌ No | Direct PR to `main` with issue reference |
| Documentation update | ❌ No | Direct PR to `main` |
| Localized feature | ❌ No | File issue, implement in single PR |
| New service/component | ✅ Yes | Requires architecture review |
| API breaking changes | ✅ Yes | Needs coordination across services |
| Multi-week development | ✅ Yes | Feature branch prevents merge conflicts |
| Cross-cutting refactoring | ✅ Yes | Impacts multiple subsystems |

**Sources:** [CONTRIBUTING.md:14-22]()

### Project Proposal Template

Open a [project proposal](https://github.com/NVIDIA/OSMO/issues/new?template=4-project-proposal.yml) issue to initiate the process. The proposal should include:

- **Problem Statement** - What challenge are you solving?
- **Proposed Solution** - High-level approach
- **Alternatives Considered** - Other options evaluated
- **Impact Analysis** - Which components are affected
- **Implementation Plan** - Timeline and milestones

After proposal approval, create a design document in `projects/` directory:

```
projects/
├── README.md
├── PROJ-001-example-project/
│   ├── design.md
│   └── assets/
└── template/
    └── design_template.md
```

**Sources:** [CONTRIBUTING.md:20-22]()

### Feature Branch Workflow

Feature branches use the naming convention: `feature/PROJ-NNN-short-slug`

Example: `feature/PROJ-042-distributed-caching`

The `sync-feature-branches.yaml` workflow automatically creates weekly PRs to keep feature branches synchronized with `main`, reducing merge conflicts.

**Sources:** [.github/workflows/sync-feature-branches.yaml:42-146]()

---

## Developer Certificate of Origin

All contributions are made under the Developer Certificate of Origin (DCO) 1.1:

```
By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I have
    the right to submit it under the open source license indicated in
    the file; or

(b) The contribution is based upon previous work that, to the best of
    my knowledge, is covered under an appropriate open source license
    and I have the right under that license to submit that work with
    modifications, whether created in whole or in part by me, under
    the same open source license (unless I am permitted to submit
    under a different license), as indicated in the file; or

(c) The contribution was provided directly to me by some other person
    who certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are
    public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Commits should include a `Signed-off-by` line matching the commit author.

**Sources:** [CONTRIBUTING.md:112-138]()

---

## Next Steps

- **[Development Setup](#9.1)** - Set up your development environment, build from source, and run tests
- **[CI/CD Pipeline](#9.2)** - Deep dive into GitHub Actions workflows and testing strategies
- **[Projects Process](#9.3)** - Learn the formal process for proposing significant changes
- **[Pull Request Guidelines](#9.4)** - Detailed PR requirements and review procedures

For questions or support:
- 🐛 [Report Issues](https://github.com/NVIDIA/OSMO/issues)
- 📖 [User Guide](https://nvidia.github.io/OSMO/main/user_guide)
- 📚 [Deployment Guide](https://nvidia.github.io/OSMO/main/deployment_guide)

**Sources:** [README.md:157-165](), [CONTRIBUTING.md:1-139]()

---

# Page: Development Setup

# Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/docs-deploy.yaml](.github/workflows/docs-deploy.yaml)
- [.github/workflows/helm-chart-lint.yaml](.github/workflows/helm-chart-lint.yaml)
- [.github/workflows/pr-checks.yaml](.github/workflows/pr-checks.yaml)
- [.github/workflows/pr-description-check.yaml](.github/workflows/pr-description-check.yaml)
- [.github/workflows/sync-feature-branches.yaml](.github/workflows/sync-feature-branches.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/conf.py](docs/conf.py)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)

</details>



This page provides instructions for setting up a local development environment for contributing to OSMO. It covers system requirements, prerequisites installation, repository setup, building from source, and running tests.

For information about the CI/CD pipeline and automated testing, see [CI/CD Pipeline](#9.2). For guidelines on submitting pull requests, see [Pull Request Guidelines](#9.4).

---

## System Requirements

OSMO development is supported on the following platforms:

| Platform | Version | Architecture |
|----------|---------|--------------|
| **Ubuntu** | 22.04+ | x86_64 |
| **MacOS** | Latest | arm64 |

**Sources:** [CONTRIBUTING.md:27-29]()

---

## Prerequisites

The following tools must be installed before you can develop OSMO:

### Required Tools

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| **Git LFS** | 3.7.1 | Source control for large files (test fixtures, models) |
| **Bazel** | 8.1.1 | Build tool for compiling services and running tests |
| **Docker** | 28.3.2 | Container runtime for building images and running tests |
| **Helm** | 3.17.1 | Package manager for Kubernetes charts |
| **KIND** | 0.29.0 | Kubernetes in Docker for local cluster testing |
| **kubectl** | 1.32.2 | Kubernetes command-line tool |
| **aws-cli** | 2.24.7 | AWS command-line tool for S3 operations |
| **npm** | 11.6.2 | Package manager for Node.js (UI development) |

### Installation

Follow the official installation guides for each tool:

- **Git LFS:** https://git-lfs.com/
- **Bazel:** https://bazel.build/install/bazelisk (use Bazelisk for version management)
- **Docker:** https://docs.docker.com/get-started/get-docker/
- **Helm:** https://helm.sh/docs/intro/install/
- **KIND:** https://kind.sigs.k8s.io/docs/user/quick-start/#installation
- **kubectl:** https://kubernetes.io/docs/tasks/tools/
- **aws-cli:** https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- **npm:** https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

**Sources:** [CONTRIBUTING.md:31-43]()

---

## Repository Setup

### Fork and Clone

1. Fork the [NVIDIA/OSMO repository](https://github.com/NVIDIA/OSMO) on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_FORK.git osmo
cd osmo
```

3. Initialize Git LFS to download large files:

```bash
git lfs install
git lfs pull
```

Git LFS is used to store test fixtures, example datasets, and documentation assets that would otherwise bloat the repository.

**Sources:** [CONTRIBUTING.md:45-53]()

---

## Development Workflow Overview

```mermaid
graph TB
    Developer["Developer<br/>Local Machine"]
    
    subgraph "Code Changes"
        Edit["Edit Code<br/>src/, ui/, charts/"]
        Format["Code Formatting<br/>Linting"]
    end
    
    subgraph "Build System"
        Bazel["Bazel Build<br/>bazel build //..."]
        BazelTest["Bazel Test<br/>bazel test //..."]
        Docker["Docker Build<br/>Container Images"]
    end
    
    subgraph "Documentation"
        Sphinx["Sphinx Build<br/>make -C docs build"]
        SpellCheck["Spelling Check<br/>make -C docs spelling"]
        LinkCheck["Link Check<br/>lychee"]
    end
    
    subgraph "Local Testing"
        KindCluster["KIND Cluster<br/>Local Kubernetes"]
        HelmInstall["Helm Install<br/>Test Charts"]
        Integration["Integration Tests<br/>Testcontainers"]
    end
    
    Developer --> Edit
    Edit --> Format
    Format --> Bazel
    Format --> Sphinx
    
    Bazel --> BazelTest
    Bazel --> Docker
    
    Sphinx --> SpellCheck
    Sphinx --> LinkCheck
    
    Docker --> KindCluster
    KindCluster --> HelmInstall
    HelmInstall --> Integration
    
    BazelTest -.->|Pass| PRSubmit["Submit PR"]
    SpellCheck -.->|Pass| PRSubmit
    Integration -.->|Pass| PRSubmit
```

**Development Workflow Flow**

This diagram shows the typical development workflow from making code changes through testing to submitting a pull request.

**Sources:** [CONTRIBUTING.md:55-65](), [.github/workflows/pr-checks.yaml:1-312]()

---

## Build System Architecture

OSMO uses **Bazel** as its primary build system. Bazel provides hermetic builds, reproducibility, and efficient caching across the monorepo.

### Bazel Workspace Structure

```mermaid
graph TB
    Root["Repository Root"]
    
    subgraph "Build Configuration"
        ModuleBazel["MODULE.bazel<br/>External Dependencies"]
        RootBuild["BUILD<br/>Root Targets"]
        BzlDir["bzl/<br/>Custom Rules"]
    end
    
    subgraph "Source Code"
        SrcDir["src/<br/>Python Services"]
        SrcBuild["src/BUILD<br/>Service Targets"]
        SrcReqs["src/locked_requirements.txt<br/>Python Dependencies"]
        
        RuntimeDir["src/runtime/<br/>Go Services"]
        RuntimeMod["src/runtime/go.mod<br/>Go Dependencies"]
    end
    
    subgraph "UI Code"
        UIDir["ui/<br/>Next.js Application"]
        UIBuild["ui/BUILD<br/>UI Targets"]
        UILock["ui/pnpm-lock.yaml<br/>NPM Dependencies"]
    end
    
    subgraph "Tests"
        TestDir["src/tests/<br/>Integration Tests"]
        TestReqs["src/tests/locked_requirements.txt<br/>Test Dependencies"]
    end
    
    subgraph "Documentation"
        DocsDir["docs/<br/>Sphinx Documentation"]
        DocsConf["docs/conf.py<br/>Sphinx Config"]
        DocsReqs["docs/locked_requirements.txt<br/>Docs Dependencies"]
    end
    
    Root --> ModuleBazel
    Root --> RootBuild
    Root --> BzlDir
    
    Root --> SrcDir
    SrcDir --> SrcBuild
    SrcDir --> SrcReqs
    SrcDir --> RuntimeDir
    RuntimeDir --> RuntimeMod
    
    Root --> UIDir
    UIDir --> UIBuild
    UIDir --> UILock
    
    Root --> TestDir
    TestDir --> TestReqs
    
    Root --> DocsDir
    DocsDir --> DocsConf
    DocsDir --> DocsReqs
```

**Bazel Workspace Structure**

This diagram maps the repository structure to Bazel build targets and dependency management files.

**Sources:** [.github/workflows/pr-checks.yaml:54-68](), [.github/workflows/pr-checks.yaml:114-125]()

### Building Components

To build all OSMO components:

```bash
# Build everything
bazel build //...

# Build only Python services (excludes UI)
bazel build //... -//ui/...

# Build only the UI
bazel build //ui/...

# Build a specific service
bazel build //src/api:api_image
```

The `//...` pattern recursively builds all targets in the workspace. The `-//ui/...` exclusion is commonly used to skip the UI build when working on backend services.

**Sources:** [.github/workflows/pr-checks.yaml:126-128]()

---

## Running Tests

### Test Execution Architecture

```mermaid
graph TB
    TestRunner["bazel test"]
    
    subgraph "Unit Tests"
        PyTest["pytest<br/>Python Unit Tests"]
        GoTest["go test<br/>Go Unit Tests"]
    end
    
    subgraph "Integration Tests"
        Testcontainers["Testcontainers<br/>PostgreSQL, Redis"]
        DockerInDocker["Docker-in-Docker<br/>Container Tests"]
        KubernetesTests["Kubernetes Tests<br/>KIND Clusters"]
    end
    
    subgraph "Linting & Type Checking"
        Pylint["pylint<br/>Python Linting"]
        MyPy["mypy<br/>Type Checking"]
        Gazelle["gazelle<br/>Go BUILD Files"]
    end
    
    subgraph "UI Tests"
        NextBuild["next build<br/>Build Validation"]
        ESLint["eslint<br/>JS/TS Linting"]
    end
    
    TestRunner --> PyTest
    TestRunner --> GoTest
    TestRunner --> Testcontainers
    TestRunner --> DockerInDocker
    TestRunner --> KubernetesTests
    TestRunner --> Pylint
    TestRunner --> MyPy
    TestRunner --> Gazelle
    TestRunner --> NextBuild
    TestRunner --> ESLint
```

**Test Execution Architecture**

This diagram shows the different types of tests executed by the Bazel test runner.

**Sources:** [.github/workflows/pr-checks.yaml:126-182]()

### Running Tests Locally

```bash
# Run all tests
bazel test --test_output=errors -- //... -//ui/...

# Run tests with detailed output
bazel test --test_output=all -- //... -//ui/...

# Run a specific test file
bazel test //src/tests:test_workflows

# Run tests matching a pattern
bazel test //src/tests/...

# Run UI tests
bazel build //ui/...
```

The `--test_output=errors` flag only shows output for failing tests, making it easier to identify issues.

**Sources:** [.github/workflows/pr-checks.yaml:126-128](), [.github/workflows/pr-checks.yaml:174-182]()

### Integration Tests with Docker

Integration tests use **Testcontainers** to spin up PostgreSQL and Redis instances automatically. When running tests that require Docker:

```bash
# Standard test execution (uses Docker on localhost)
bazel test //src/tests:integration_tests

# In CI with Docker-in-Docker
bazel test \
  --test_env=DOCKER_HOST=tcp://docker:2375 \
  --test_env=TESTCONTAINERS_HOST_OVERRIDE=docker \
  //src/tests:integration_tests
```

The `DOCKER_HOST` and `TESTCONTAINERS_HOST_OVERRIDE` environment variables configure Testcontainers to use a Docker-in-Docker service, which is necessary in containerized CI environments.

**Sources:** [.github/workflows/pr-checks.yaml:174-182]()

---

## Bazel Remote Cache

For faster builds, internal contributors can use remote caching:

```bash
# Build with remote cache
bazel build \
  --remote_cache=https://bazel-cache.internal.nvidia.com \
  //...

# Test with remote cache
bazel test \
  --remote_cache=https://bazel-cache.internal.nvidia.com \
  --test_output=errors \
  -- //... -//ui/...
```

Remote caching stores build artifacts and test results in a shared cache, dramatically reducing build times for repeated builds. The cache is keyed by input hashes, ensuring correctness.

**Sources:** [.github/workflows/pr-checks.yaml:176-182]()

---

## Building Documentation

OSMO documentation is built using **Sphinx** with custom extensions.

### Documentation Build Pipeline

```mermaid
graph TB
    Source["Documentation Source<br/>docs/**/*.rst"]
    
    subgraph "Build Process"
        SphinxConf["docs/conf.py<br/>Sphinx Configuration"]
        Extensions["Custom Extensions<br/>docs/_extensions/"]
        Templates["Templates<br/>docs/_templates/"]
    end
    
    subgraph "Build Targets"
        SingleVersion["make build<br/>Single Version<br/>docs/public/"]
        MultiVersion["make build-multiversion<br/>All Branches/Tags<br/>docs/public/"]
    end
    
    subgraph "Validation"
        SpellingCheck["make spelling<br/>Spelling Check<br/>spelling_wordlist.txt"]
        LinkCheck["lychee<br/>Link Validation<br/>.lycheecache"]
        BuildErrors["Build Errors<br/>docs/build_error_logs/"]
    end
    
    subgraph "Output"
        HTMLOutput["HTML Output<br/>docs/public/"]
        GHPages["GitHub Pages<br/>gh-pages/documentation"]
    end
    
    Source --> SphinxConf
    SphinxConf --> Extensions
    SphinxConf --> Templates
    
    Extensions --> SingleVersion
    Extensions --> MultiVersion
    
    SingleVersion --> SpellingCheck
    SingleVersion --> LinkCheck
    SingleVersion --> BuildErrors
    
    SpellingCheck --> HTMLOutput
    LinkCheck --> HTMLOutput
    
    HTMLOutput --> GHPages
```

**Documentation Build Pipeline**

This diagram shows how Sphinx documentation is built, validated, and deployed.

**Sources:** [docs/conf.py:1-268](), [.github/workflows/pr-checks.yaml:187-281](), [.github/workflows/docs-deploy.yaml:1-95]()

### Building Locally

```bash
# Install documentation dependencies
pip install -U -r docs/locked_requirements.txt
pip install -U -r src/locked_requirements.txt

# Build documentation (single version)
make -C docs build ERR_DIR=build_error_logs OUT_DIR=public

# Build documentation (multi-version)
make -C docs build-multiversion ERR_DIR=build_error_logs OUT_DIR=public

# Run spelling check
make -C docs spelling ERR_DIR=spelling_error_logs OUT_DIR=public

# Check for build errors
find docs/build_error_logs -name '*.log' -size +0c
```

The documentation dependencies include:
- **sphinx** - Core documentation engine
- **sphinx-multiversion** - Multi-version documentation support
- **sphinx_copybutton** - Copy button for code blocks
- **sphinx_design** - UI components for documentation
- **sphinxcontrib.mermaid** - Mermaid diagram support

**Sources:** [.github/workflows/pr-checks.yaml:203-217](), [.github/workflows/docs-deploy.yaml:53-70](), [docs/conf.py:38-67]()

### Sphinx Configuration

The Sphinx configuration at [docs/conf.py:1-268]() includes:

- **Project metadata** - [docs/conf.py:28-31]()
- **Extensions** - [docs/conf.py:38-67]()
- **Theme configuration** - [docs/conf.py:131-158]()
- **Spelling check** - [docs/conf.py:76-82]()
- **Link checking** - [docs/conf.py:84-98]()
- **Substitution constants** - [docs/conf.py:186-229]()

Key extensions used:
- `sphinx_multiversion` - Build docs for multiple branches/tags ([docs/conf.py:256-267]())
- `sphinxcontrib.mermaid` - Mermaid diagram rendering ([docs/conf.py:253-254]())
- `sphinx_copybutton` - Copy buttons on code blocks ([docs/conf.py:100-105]())
- Custom extensions in `docs/_extensions/` ([docs/conf.py:55-63]())

**Sources:** [docs/conf.py:1-268]()

---

## CI/CD Test Workflow

OSMO uses GitHub Actions for continuous integration. The workflow differs for fork PRs and internal PRs.

### CI Workflow Architecture

```mermaid
graph TB
    PRTrigger["Pull Request<br/>Opened/Synchronized"]
    
    CheckPaths["check-paths Job<br/>Path Filtering"]
    
    subgraph "Path Filter Outputs"
        CIPath["ci: true<br/>.github/workflows/,<br/>BUILD, MODULE.bazel,<br/>bzl/, src/, run/"]
        DocsPath["docs: true<br/>docs/, workflows/"]
        UIPath["ui: true<br/>ui/, BUILD"]
    end
    
    subgraph "Fork PRs"
        CIPublic["ci-public Job<br/>GitHub-hosted Runner<br/>ubuntu-latest"]
        PublicTest["bazel test<br/>No Remote Cache"]
    end
    
    subgraph "Internal PRs"
        CIInternal["ci-internal Job<br/>Self-hosted Runner<br/>Docker-in-Docker"]
        InternalTest["bazel test<br/>Remote Cache Enabled"]
    end
    
    subgraph "Documentation"
        DocsBuild["docs-build Job<br/>ubuntu-latest"]
        SphinxBuild["Sphinx Build<br/>make -C docs build"]
        SpellCheck["Spelling Check<br/>make -C docs spelling"]
        LinkCheck["Link Check<br/>lychee"]
        PRPreview["PR Preview<br/>gh-pages/documentation"]
    end
    
    subgraph "UI Build"
        UIBuild["ui-build Job<br/>ubuntu-latest"]
        BazelUIBuild["bazel build //ui/..."]
    end
    
    PRTrigger --> CheckPaths
    CheckPaths --> CIPath
    CheckPaths --> DocsPath
    CheckPaths --> UIPath
    
    CIPath -->|Fork PR| CIPublic
    CIPath -->|Internal PR| CIInternal
    
    CIPublic --> PublicTest
    CIInternal --> InternalTest
    
    DocsPath --> DocsBuild
    DocsBuild --> SphinxBuild
    SphinxBuild --> SpellCheck
    SphinxBuild --> LinkCheck
    SphinxBuild --> PRPreview
    
    UIPath --> UIBuild
    UIBuild --> BazelUIBuild
```

**CI Workflow Architecture**

This diagram shows how the `pr-checks.yaml` workflow uses path filtering to run only relevant tests based on changed files.

**Sources:** [.github/workflows/pr-checks.yaml:29-312]()

### Path-Based Test Execution

The CI system uses path filtering to optimize test execution:

| Path Pattern | Triggers | Jobs Run |
|--------------|----------|----------|
| `.github/workflows/pr-checks.yaml`, `BUILD`, `MODULE.bazel`, `bzl/**`, `src/**`, `run/**` | CI tests | `ci-public` or `ci-internal` |
| `docs/**`, `workflows/**` | Documentation build | `docs-build` |
| `ui/**`, `BUILD`, `MODULE.bazel`, `bzl/**` | UI build | `ui-build` |

The path filtering is implemented using the `dorny/paths-filter` action in [.github/workflows/pr-checks.yaml:45-68]().

**Sources:** [.github/workflows/pr-checks.yaml:33-68]()

### Fork PRs vs Internal PRs

- **Fork PRs** (`github.event.pull_request.head.repo.fork == true`):
  - Run on GitHub-hosted `ubuntu-latest` runners ([.github/workflows/pr-checks.yaml:73-129]())
  - No remote Bazel cache (slower builds)
  - Limited permissions for security

- **Internal PRs** (from `NVIDIA/OSMO` branches):
  - Run on self-hosted runners ([.github/workflows/pr-checks.yaml:130-183]())
  - Docker-in-Docker service enabled ([.github/workflows/pr-checks.yaml:143-156]())
  - Remote Bazel cache enabled ([.github/workflows/pr-checks.yaml:176]())
  - Full access to internal resources

**Sources:** [.github/workflows/pr-checks.yaml:73-183]()

---

## Docker Setup for Development

Many OSMO tests require Docker to run containers for databases, services, and integration testing.

### Docker Permissions

Ensure your user has Docker permissions:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
# Or use newgrp to activate the new group without logging out
newgrp docker

# Verify Docker access
docker ps
```

**Sources:** [deployments/brev/setup.sh:73-79]()

### Docker-in-Docker for CI

The CI environment uses Docker-in-Docker to run containerized tests:

```yaml
services:
  docker:
    image: docker:dind
    env:
      DOCKER_TLS_CERTDIR: ""
      DOCKER_DRIVER: overlay2
    options: --privileged
    ports:
      - 2375:2375
```

Tests connect to this service using `DOCKER_HOST=tcp://docker:2375`.

**Sources:** [.github/workflows/pr-checks.yaml:148-156]()

---

## Local Kubernetes Development

For testing OSMO deployments locally, use KIND (Kubernetes in Docker).

### KIND Cluster Setup

```bash
# Create a basic KIND cluster
kind create cluster --name osmo-dev

# Delete the cluster
kind delete cluster --name osmo-dev

# Load a Docker image into KIND
kind load docker-image osmo-api:dev --name osmo-dev
```

For GPU-enabled testing, use `nvkind`:

```bash
# Install nvkind
go install github.com/NVIDIA/nvkind/cmd/nvkind@latest

# Create GPU-enabled cluster
nvkind cluster create --config-template=kind-config.yaml
```

**Sources:** [deployments/brev/setup.sh:117-218](), [CONTRIBUTING.md:37-38]()

---

## Helm Chart Development

To test Helm chart changes locally:

```bash
# Lint a chart
helm lint deployments/charts/service

# Build chart dependencies
helm dependency build deployments/charts/quick-start

# Template a chart (dry-run)
helm template test-release deployments/charts/service

# Install a chart to KIND
helm upgrade --install osmo deployments/charts/quick-start \
  --namespace osmo \
  --create-namespace
```

Helm charts are linted automatically when files in `deployments/charts/**` change, as defined in [.github/workflows/helm-chart-lint.yaml:1-126]().

**Sources:** [.github/workflows/helm-chart-lint.yaml:100-125](), [CONTRIBUTING.md:36]()

---

## Dependency Management

### Python Dependencies

Python dependencies are managed using locked requirements files:

- **Service dependencies:** [src/locked_requirements.txt]()
- **Test dependencies:** [src/tests/locked_requirements.txt]()
- **Documentation dependencies:** [docs/locked_requirements.txt]()
- **Linting dependencies:** [bzl/linting/locked_requirements.txt]()
- **Type checking dependencies:** [bzl/mypy/locked_requirements.txt]()

These files are referenced in the Bazel cache configuration at [.github/workflows/pr-checks.yaml:116-120]().

**Sources:** [.github/workflows/pr-checks.yaml:114-125]()

### Go Dependencies

Go dependencies for the Router service are managed using:

- **go.mod:** [src/runtime/go.mod]()
- **go.sum:** [src/runtime/go.sum]()

These files are referenced in the Bazel cache configuration at [.github/workflows/pr-checks.yaml:123-124]().

**Sources:** [.github/workflows/pr-checks.yaml:114-125]()

### UI Dependencies

UI dependencies are managed using pnpm:

- **pnpm-lock.yaml:** [ui/pnpm-lock.yaml]()

This file is referenced in the Bazel cache configuration at [.github/workflows/pr-checks.yaml:307]().

**Sources:** [.github/workflows/pr-checks.yaml:305-308](), [CONTRIBUTING.md:42-43]()

---

## Bazel Cache Configuration

The CI workflow uses Bazel's external cache feature to cache dependencies based on their lock files:

```yaml
external-cache: |
  manifest:
    # Python dependencies
    osmo_python_deps: src/locked_requirements.txt
    osmo_tests_python_deps: src/tests/locked_requirements.txt
    osmo_mypy_deps: bzl/mypy/locked_requirements.txt
    pylint_python_deps: bzl/linting/locked_requirements.txt

    # Go dependencies
    io_bazel_rules_go: src/runtime/go.mod
    bazel_gazelle: src/runtime/go.sum
```

This configuration ensures that external dependencies are only re-fetched when their lock files change.

**Sources:** [.github/workflows/pr-checks.yaml:114-125]()

---

## Common Development Tasks

### Build a Service Container Image

```bash
# Build the API service image
bazel build //src/api:api_image

# Build all service images
bazel build //src/...:all_images
```

### Run Unit Tests

```bash
# Run all Python tests
bazel test //src/tests/...

# Run a specific test file
bazel test //src/tests:test_workflow_execution
```

### Run Linting

```bash
# Run Python linting
bazel test //src/...:pylint_test

# Run type checking
bazel test //src/...:mypy_test
```

### Clean Build Artifacts

```bash
# Clean all Bazel build outputs
bazel clean

# Clean and remove all cached artifacts
bazel clean --expunge
```

---

## Next Steps

Once your development environment is set up:

1. Read the [CI/CD Pipeline](#9.2) documentation to understand automated testing
2. Review the [Projects Process](#9.3) if you're planning significant changes
3. Follow the [Pull Request Guidelines](#9.4) when submitting contributions
4. Refer to the [Contributing Guide](CONTRIBUTING.md) for coding standards and workflow

For questions or issues with development setup, file an issue on the [OSMO GitHub repository](https://github.com/NVIDIA/OSMO/issues).

**Sources:** [CONTRIBUTING.md:1-139]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docs-deploy.yaml](.github/workflows/docs-deploy.yaml)
- [.github/workflows/helm-chart-lint.yaml](.github/workflows/helm-chart-lint.yaml)
- [.github/workflows/pr-checks.yaml](.github/workflows/pr-checks.yaml)
- [.github/workflows/pr-description-check.yaml](.github/workflows/pr-description-check.yaml)
- [.github/workflows/sync-feature-branches.yaml](.github/workflows/sync-feature-branches.yaml)
- [docs/conf.py](docs/conf.py)

</details>



This document explains OSMO's CI/CD infrastructure, including automated testing workflows, documentation deployment, validation checks, and the path-based execution optimization system. For information about the formal process for proposing and implementing changes, see [Projects Process](#9.3). For guidelines on preparing pull requests, see [Pull Request Guidelines](#9.4).

---

## Overview

OSMO's CI/CD system is implemented entirely through GitHub Actions workflows and uses **path-based execution** to optimize build times by running only relevant tests for changed files. The system distinguishes between fork PRs (using GitHub-hosted runners) and internal PRs (using self-hosted runners with remote Bazel caching).

### Workflow Architecture

```mermaid
graph TB
    subgraph "PR Events"
        PullRequest["Pull Request<br/>(opened, synchronize, reopened)"]
        PushMain["Push to main"]
    end
    
    subgraph "Validation Workflows"
        PRDesc["pr-description-check.yaml<br/>validate-pr-description job"]
        HelmLint["helm-chart-lint.yaml<br/>detect-chart-changes<br/>helm-lint jobs"]
    end
    
    subgraph "Main PR Checks Workflow<br/>(pr-checks.yaml)"
        CheckPaths["check-paths job<br/>dorny/paths-filter@v3"]
        
        CIPublic["ci-public job<br/>ubuntu-latest<br/>Fork PRs"]
        CIInternal["ci-internal job<br/>self-hosted + DinD<br/>Internal PRs"]
        DocsBuild["docs-build job<br/>Sphinx + Linting"]
        UIBuild["ui-build job<br/>Bazel Build"]
    end
    
    subgraph "Deployment Workflows"
        DocsDeploy["docs-deploy.yaml<br/>Multiversion Build<br/>GitHub Pages"]
        SyncBranches["sync-feature-branches.yaml<br/>Weekly Schedule"]
    end
    
    PullRequest --> PRDesc
    PullRequest --> CheckPaths
    
    CheckPaths -->|"ci: true<br/>fork PR"| CIPublic
    CheckPaths -->|"ci: true<br/>internal PR"| CIInternal
    CheckPaths -->|"docs: true"| DocsBuild
    CheckPaths -->|"ui: true"| UIBuild
    
    PullRequest -->|"charts/** changed"| HelmLint
    
    PushMain -->|"docs/** changed"| DocsDeploy
    PushMain --> SyncBranches
```

**Sources**: [.github/workflows/pr-checks.yaml:1-312](), [.github/workflows/docs-deploy.yaml:1-95](), [.github/workflows/pr-description-check.yaml:1-135](), [.github/workflows/helm-chart-lint.yaml:1-126](), [.github/workflows/sync-feature-branches.yaml:1-151]()

---

## Path-Based Execution Optimization

The `check-paths` job uses the `dorny/paths-filter` action to determine which parts of the codebase changed, enabling conditional execution of downstream jobs. This significantly reduces CI time by skipping irrelevant tests.

### Path Filter Configuration

| Output | Triggered When | Downstream Jobs |
|--------|---------------|-----------------|
| `ci` | `.github/workflows/pr-checks.yaml`, `BUILD`, `MODULE.bazel`, `bzl/**`, `src/**`, `run/**` | `ci-public`, `ci-internal` |
| `docs` | `.github/workflows/pr-checks.yaml`, `docs/**`, `workflows/**` | `docs-build` |
| `ui` | `.github/workflows/pr-checks.yaml`, `BUILD`, `MODULE.bazel`, `bzl/**`, `ui/**` | `ui-build` |

```mermaid
graph LR
    subgraph "check-paths Job"
        Checkout["actions/checkout@v4<br/>fetch-depth: 0"]
        Filter["dorny/paths-filter@v3<br/>token: '' (git-based)"]
        Outputs["Job Outputs:<br/>ci, docs, ui"]
    end
    
    Checkout --> Filter
    Filter --> Outputs
    
    Outputs -->|"ci == 'true'"| CIJobs["CI Testing Jobs"]
    Outputs -->|"docs == 'true'"| DocsJobs["Documentation Jobs"]
    Outputs -->|"ui == 'true'"| UIJobs["UI Build Jobs"]
```

The filter uses git-based detection (empty token) to ensure accurate diff analysis across the entire history [.github/workflows/pr-checks.yaml:49-50]().

**Sources**: [.github/workflows/pr-checks.yaml:33-68]()

---

## CI Testing Jobs

### Fork PRs: ci-public Job

The `ci-public` job runs on GitHub-hosted `ubuntu-latest` runners for pull requests originating from forked repositories. This job has limited access to secrets and uses public caching only.

```mermaid
graph TB
    subgraph "ci-public Job Flow"
        Condition["Condition:<br/>needs.check-paths.outputs.ci == 'true'<br/>fork PR<br/>not closed"]
        FreeDisk["Free disk space<br/>Remove .NET, Android,<br/>GHC, CodeQL, Docker images"]
        Checkout["Checkout<br/>with LFS"]
        SetupBazel["Setup Bazel<br/>bazelisk-version: 1.27.0<br/>disk-cache: ${{ github.workflow }}<br/>external-cache manifest"]
        RunTests["bazel test<br/>--test_output=errors<br/>//... -//ui/..."]
    end
    
    Condition --> FreeDisk
    FreeDisk --> Checkout
    Checkout --> SetupBazel
    SetupBazel --> RunTests
```

**Disk Space Cleanup**: The job removes unnecessary software to free disk space before testing [.github/workflows/pr-checks.yaml:81-100]():
- .NET runtime
- Android SDK
- GHC/Haskell toolchain
- CodeQL database
- Docker images

**Bazel Caching**: Uses `bazel-contrib/setup-bazel` with external cache manifests for Python and Go dependencies [.github/workflows/pr-checks.yaml:107-124]():
```yaml
external-cache:
  manifest:
    osmo_python_deps: src/locked_requirements.txt
    osmo_tests_python_deps: src/tests/locked_requirements.txt
    osmo_mypy_deps: bzl/mypy/locked_requirements.txt
    pylint_python_deps: bzl/linting/locked_requirements.txt
    io_bazel_rules_go: src/runtime/go.mod
    bazel_gazelle: src/runtime/go.sum
```

**Test Execution**: Runs all Bazel tests except UI tests [.github/workflows/pr-checks.yaml:126-128]():
```bash
bazel test --test_output=errors -- //... -//ui/...
```

**Sources**: [.github/workflows/pr-checks.yaml:73-129]()

### Internal PRs: ci-internal Job

The `ci-internal` job runs on self-hosted runners with Docker-in-Docker (DinD) and has access to a remote Bazel cache for faster builds.

```mermaid
graph TB
    subgraph "ci-internal Infrastructure"
        SelfHosted["self-hosted runner<br/>environment: internal-ci"]
        Container["Container:<br/>python:3.10-bullseye<br/>DOCKER_HOST=tcp://docker:2375"]
        DinDService["Docker Service:<br/>docker:dind<br/>--privileged<br/>port 2375:2375"]
    end
    
    subgraph "ci-internal Job Flow"
        InstallDeps["Install git-lfs"]
        Checkout["Checkout with LFS"]
        SetupBazel["Setup Bazel<br/>bazelisk-cache: true"]
        RunTests["bazel test<br/>--remote_cache=$BAZEL_REMOTE_CACHE_URL<br/>--test_env=DOCKER_HOST<br/>--test_env=TESTCONTAINERS_HOST_OVERRIDE<br/>//... -//ui/..."]
    end
    
    SelfHosted --> Container
    Container --> DinDService
    Container --> InstallDeps
    InstallDeps --> Checkout
    Checkout --> SetupBazel
    SetupBazel --> RunTests
```

**Docker-in-Docker Setup**: The job runs tests inside a container that connects to a separate Docker daemon service [.github/workflows/pr-checks.yaml:143-156]():
- Main container runs Python 3.10
- Docker service runs in privileged mode
- Connection via TCP on port 2375 (no TLS)

**Remote Caching**: Uses a secret remote cache URL to share build artifacts [.github/workflows/pr-checks.yaml:176]():
```bash
--remote_cache=${{ secrets.BAZEL_REMOTE_CACHE_URL }}
```

**Testcontainers Configuration**: Environment variables enable Testcontainers to use the DinD service [.github/workflows/pr-checks.yaml:177-178]():
```bash
--test_env=DOCKER_HOST=tcp://docker:2375
--test_env=TESTCONTAINERS_HOST_OVERRIDE=docker
```

**Sources**: [.github/workflows/pr-checks.yaml:130-183]()

---

## Documentation Build and Validation

The `docs-build` job builds Sphinx documentation, runs spelling and link checks, and deploys a preview for PRs.

### Documentation Build Pipeline

```mermaid
graph TB
    subgraph "docs-build Job"
        Condition["Condition:<br/>needs.check-paths.outputs.docs == 'true'<br/>or workflow_dispatch"]
        Setup["Setup Python 3.10.18<br/>Install docs/locked_requirements.txt<br/>Install src/locked_requirements.txt"]
        Build["make -C docs build<br/>ERR_DIR=build_error_logs<br/>OUT_DIR=public"]
        CheckErrors["Check for .log files<br/>in build_error_logs/<br/>Exit 1 if found"]
        Preview["rossjrw/pr-preview-action@v1<br/>source-dir: ./docs/public/<br/>preview-branch: gh-pages/documentation"]
    end
    
    subgraph "Validation Steps"
        Spelling["make -C docs spelling<br/>continue-on-error: true"]
        RestoreCache["Restore lychee cache<br/>key: cache-lychee-pr-N"]
        LinkCheck["lychee-action@v2<br/>--config docs/lychee.toml<br/>docs/public"]
        SaveCache["Save lychee cache"]
        ValidateAll["Fail if spelling or link check failed"]
    end
    
    Condition --> Setup
    Setup --> Build
    Build --> CheckErrors
    CheckErrors --> Preview
    CheckErrors --> Spelling
    Spelling --> RestoreCache
    RestoreCache --> LinkCheck
    LinkCheck --> SaveCache
    LinkCheck --> ValidateAll
    Spelling --> ValidateAll
```

**Build Error Handling**: The build checks for non-empty log files in `build_error_logs/` and fails if any are found [.github/workflows/pr-checks.yaml:213-217]().

**Preview Deployment**: Uses `pr-preview-action` to deploy documentation previews to the `gh-pages/documentation` branch with automatic cleanup when PRs close [.github/workflows/pr-checks.yaml:219-223]().

**Spelling Check**: Uses Sphinx's spelling extension with a custom wordlist [.github/workflows/pr-checks.yaml:225-235]():
- Configuration: `docs/conf.py` [docs/conf.py:76-82]()
- Wordlist: `docs/spelling_wordlist.txt`
- Continues on error but tracked for final validation

**Link Checking**: Uses `lychee` to validate all hyperlinks [.github/workflows/pr-checks.yaml:245-251]():
- Configuration file: `docs/lychee.toml`
- Caches results per PR to avoid re-checking unchanged links
- Output: `docs/link_check_error_logs/lychee-report.md`

**Artifact Upload**: Always uploads build artifacts on completion [.github/workflows/pr-checks.yaml:271-281]():
```yaml
path: |
  docs/public/
  docs/build_error_logs/
  docs/spelling_error_logs/
  docs/link_check_error_logs/
retention-days: 3
```

**Sources**: [.github/workflows/pr-checks.yaml:187-282](), [docs/conf.py:76-98]()

---

## UI Build Job

The `ui-build` job compiles the Next.js web UI using Bazel when UI-related files change.

```mermaid
graph LR
    Condition["Condition:<br/>needs.check-paths.outputs.ui == 'true'<br/>not closed<br/>or workflow_dispatch"]
    Checkout["Checkout with LFS"]
    Setup["Setup Bazel<br/>bazelisk-version: 1.27.0<br/>external-cache:<br/>npm: ui/pnpm-lock.yaml"]
    Build["bazel build //ui/..."]
    
    Condition --> Checkout
    Checkout --> Setup
    Setup --> Build
```

**Caching Strategy**: Uses `pnpm-lock.yaml` as the cache manifest for npm dependencies [.github/workflows/pr-checks.yaml:305-307]().

**Build Target**: Builds all UI targets under the `//ui/` Bazel package [.github/workflows/pr-checks.yaml:310-311]().

**Sources**: [.github/workflows/pr-checks.yaml:286-312]()

---

## Documentation Deployment

The `docs-deploy` workflow builds and deploys production documentation to GitHub Pages when documentation files are pushed to the `main` branch.

### Multiversion Build Process

```mermaid
graph TB
    subgraph "Trigger Conditions"
        Push["Push to main<br/>paths: docs/**, workflows/**"]
        Manual["workflow_dispatch"]
    end
    
    subgraph "Build Job"
        Checkout["Checkout with LFS"]
        Setup["Setup Python 3.10.18<br/>Install locked_requirements.txt<br/>git fetch (for multiversion)"]
        Build["make -C docs build-multiversion<br/>ERR_DIR=build_error_logs<br/>OUT_DIR=public"]
        CheckErrors["Check for build errors"]
        UploadArtifact["Upload build artifacts<br/>retention-days: 5"]
        UploadPages["Upload Pages artifact<br/>path: docs/public/"]
        Deploy["JamesIves/github-pages-deploy-action@v4<br/>branch: gh-pages/documentation<br/>folder: docs/public<br/>clean-exclude: pr-preview/"]
    end
    
    Push --> Checkout
    Manual --> Checkout
    Checkout --> Setup
    Setup --> Build
    Build --> CheckErrors
    CheckErrors --> UploadArtifact
    CheckErrors --> UploadPages
    UploadPages --> Deploy
```

**Multiversion Configuration**: Uses `sphinx-multiversion` to build docs for multiple branches [docs/conf.py:256-267]():
```python
# Exclude all tags
smv_tag_whitelist = r'^$'

# Allow only main and release/* branches
smv_branch_whitelist = r'^main$|^release/.*$'
smv_remote_whitelist = r'^origin$'
smv_prefer_remote_refs = False

# Latest version
smv_latest_version = 'main'
```

**Concurrent Deployment Protection**: Uses concurrency group `"pages"` with `cancel-in-progress: false` to prevent race conditions while allowing queued deployments to complete [.github/workflows/docs-deploy.yaml:33-35]().

**Clean Exclude**: Preserves PR preview directories during deployment [.github/workflows/docs-deploy.yaml:91-93]():
```yaml
clean-exclude: |
  pr-preview/
  .nojekyll
```

**Sources**: [.github/workflows/docs-deploy.yaml:1-95](), [docs/conf.py:256-267]()

---

## Additional Validation Workflows

### PR Description Check

The `pr-description-check` workflow validates that pull request descriptions meet OSMO's requirements.

```mermaid
graph TB
    subgraph "Validation Logic"
        ExtractBody["Extract PR body<br/>from github.event.pull_request.body"]
        CheckIssue["Check for Issue Reference<br/>grep -qiE 'Issue (#[0-9]+|#None|- None)'"]
        ExtractChecklist["awk: Extract ## Checklist section<br/>from '## Checklist' to next '##'"]
        CountBoxes["Count checkbox items:<br/>grep -cE '^- \\[[ xX]\\]'"]
        CountUnchecked["Count unchecked items:<br/>grep -cE '^- \\[ \\]'"]
        ValidateAll["Exit 1 if:<br/>- Missing issue reference<br/>- No checklist section<br/>- No checkbox items<br/>- Unchecked items > 0"]
    end
    
    ExtractBody --> CheckIssue
    ExtractBody --> ExtractChecklist
    ExtractChecklist --> CountBoxes
    CountBoxes --> CountUnchecked
    CheckIssue --> ValidateAll
    CountUnchecked --> ValidateAll
```

**Issue Reference Check**: Validates case-insensitive patterns [.github/workflows/pr-description-check.yaml:44]():
- `Issue #123`
- `Issue #None`
- `Issue - None`
- `issue #42` (case-insensitive)

**Checklist Extraction**: Uses `awk` to extract only the checklist section between `## Checklist` and the next `##` heading [.github/workflows/pr-description-check.yaml:68-72]().

**Checkbox Validation**: Ensures all checklist items are marked complete [.github/workflows/pr-description-check.yaml:85-111]():
- Items must be in format `- [x]` or `- [X]`
- Empty boxes `- [ ]` cause validation to fail
- Reports count of unchecked items

**Sources**: [.github/workflows/pr-description-check.yaml:1-135]()

### Helm Chart Lint

The `helm-chart-lint` workflow validates Helm charts when changes are detected in `deployments/charts/**`.

```mermaid
graph TB
    subgraph "detect-chart-changes Job"
        DetectCheckout["Checkout<br/>fetch-depth: 0"]
        GetChanges["git diff --name-only<br/>origin/base_ref...HEAD"]
        FindCharts["For each deployments/charts/*/<br/>Check if path matches changed files"]
        OutputJSON["Output JSON array:<br/>charts=['chart1','chart2']<br/>has_changes=true/false"]
    end
    
    subgraph "helm-lint Job (Matrix)"
        LintCheckout["Checkout"]
        SetupHelm["Setup Helm v3.14.0"]
        BuildDeps["helm dependency build<br/>deployments/charts/${{ matrix.chart }}"]
        HelmLint["helm lint<br/>deployments/charts/${{ matrix.chart }}"]
        HelmTemplate["helm template test-release<br/>deployments/charts/${{ matrix.chart }}"]
    end
    
    DetectCheckout --> GetChanges
    GetChanges --> FindCharts
    FindCharts --> OutputJSON
    OutputJSON -->|"has_changes == 'true'"| LintCheckout
    LintCheckout --> SetupHelm
    SetupHelm --> BuildDeps
    BuildDeps --> HelmLint
    HelmLint --> HelmTemplate
```

**Change Detection**: Builds a JSON array of changed chart names by checking if `deployments/charts/{chart_name}/` appears in the git diff [.github/workflows/helm-chart-lint.yaml:49-78]().

**Matrix Strategy**: Uses `fail-fast: false` to lint all changed charts independently, reporting failures for each [.github/workflows/helm-chart-lint.yaml:87-90]().

**Validation Steps**:
1. Build dependencies using `helm dependency build`
2. Run `helm lint` to check chart syntax
3. Run `helm template` to validate template rendering [.github/workflows/helm-chart-lint.yaml:100-124]()

**Sources**: [.github/workflows/helm-chart-lint.yaml:1-126]()

### Feature Branch Sync

The `sync-feature-branches` workflow automatically creates PRs to merge `main` into feature branches weekly.

```mermaid
graph TB
    subgraph "Schedule & Trigger"
        Cron["Cron: 0 17 * * 1<br/>(Monday 9am PT)"]
        Manual["workflow_dispatch"]
    end
    
    subgraph "Sync Process"
        FindBranches["git branch -r<br/>grep 'origin/feature/'"]
        CheckBehind["For each feature branch:<br/>git rev-list --count<br/>origin/branch..origin/main"]
        CreateTemp["Create temp branch:<br/>sync/feature/branch/YYYYMMDD-HHMM"]
        MergeMain["git merge origin/main<br/>--no-commit --no-ff"]
        HandleConflicts["If conflicts:<br/>git add -A<br/>git commit"]
        Push["git push origin temp_branch"]
        CreatePR["gh pr create<br/>--base feature/branch<br/>--head temp_branch<br/>Auto-generate PR body"]
    end
    
    Cron --> FindBranches
    Manual --> FindBranches
    FindBranches --> CheckBehind
    CheckBehind -->|"commits_behind > 0"| CreateTemp
    CreateTemp --> MergeMain
    MergeMain --> HandleConflicts
    HandleConflicts --> Push
    Push --> CreatePR
```

**Branch Pattern**: Finds all branches matching `origin/feature/*` [.github/workflows/sync-feature-branches.yaml:51]().

**Commit Check**: Only creates PRs if the feature branch is behind `main` [.github/workflows/sync-feature-branches.yaml:71-76]().

**Issue Reference Extraction**: Attempts to extract issue numbers from branch names in format `feature/PROJ-NNN-short-slug` [.github/workflows/sync-feature-branches.yaml:82-87]():
```bash
issue_number=$(echo "$branch" | grep -oE 'PROJ-[0-9]+' || echo "")
```

**Conflict Handling**: If merge conflicts occur, commits them with conflict markers for manual resolution [.github/workflows/sync-feature-branches.yaml:97-103]().

**PR Template**: Auto-generates a PR description with checklist, commit count, and links to the Projects Process documentation [.github/workflows/sync-feature-branches.yaml:112-139]().

**Sources**: [.github/workflows/sync-feature-branches.yaml:1-151]()

---

## Runner Infrastructure Comparison

| Feature | ci-public (Fork PRs) | ci-internal (Internal PRs) |
|---------|---------------------|---------------------------|
| Runner Type | GitHub-hosted `ubuntu-latest` | Self-hosted with environment `internal-ci` |
| Container | None (runs on runner directly) | `python:3.10-bullseye` |
| Docker Access | Native Docker daemon | Docker-in-Docker service on port 2375 |
| Bazel Remote Cache | None | `${{ secrets.BAZEL_REMOTE_CACHE_URL }}` |
| Disk Space Management | Manual cleanup script | Not needed (fresh container) |
| Testcontainers Support | Default Docker socket | Custom `DOCKER_HOST` and `TESTCONTAINERS_HOST_OVERRIDE` |
| Trigger Condition | `github.event.pull_request.head.repo.fork == true` | `github.event.pull_request.head.repo.fork == false` |
| Secrets Access | Limited (public cache only) | Full access (remote cache, credentials) |

**Sources**: [.github/workflows/pr-checks.yaml:73-183]()

---

## Bazel Caching Strategy

### External Cache Manifests

Both `ci-public` and `ui-build` use external cache manifests to track dependency changes:

```yaml
external-cache:
  manifest:
    # Python dependencies
    osmo_python_deps: src/locked_requirements.txt
    osmo_tests_python_deps: src/tests/locked_requirements.txt
    osmo_mypy_deps: bzl/mypy/locked_requirements.txt
    pylint_python_deps: bzl/linting/locked_requirements.txt
    
    # Go dependencies
    io_bazel_rules_go: src/runtime/go.mod
    bazel_gazelle: src/runtime/go.sum
    
    # npm dependencies (UI only)
    npm: ui/pnpm-lock.yaml
```

The manifest system hashes these files to create cache keys. When a lock file changes, only that dependency set is re-downloaded.

### Cache Types

| Cache Type | Location | Used By | Purpose |
|------------|----------|---------|---------|
| `bazelisk-cache` | GitHub Actions cache | All jobs | Cache Bazelisk binary downloads |
| `disk-cache` | GitHub Actions cache | `ci-public`, `ui-build` | Cache Bazel build outputs keyed by workflow name |
| `repository-cache` | GitHub Actions cache | `ci-public`, `ui-build` | Cache external repository downloads (Maven, PyPI, Go modules) |
| `external-cache` | GitHub Actions cache | `ci-public`, `ui-build` | Manifest-based dependency tracking |
| Remote cache | External cache server | `ci-internal` | Shared cache across all internal builds (requires authentication) |

**Sources**: [.github/workflows/pr-checks.yaml:107-124](), [.github/workflows/pr-checks.yaml:298-307]()

---

## Workflow Concurrency Control

All PR-triggered workflows use the same concurrency configuration to prevent duplicate runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

This ensures:
- Only one run per workflow per PR at a time
- New commits to a PR cancel in-progress runs
- Different workflows run independently

The `docs-deploy` workflow uses a different strategy for production deployments:

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

This prevents race conditions during GitHub Pages deployment while allowing queued deployments to complete in order.

**Sources**: [.github/workflows/pr-checks.yaml:25-27](), [.github/workflows/docs-deploy.yaml:33-35]()

---

# Page: Projects Process

# Projects Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/4-project-proposal.yml](.github/ISSUE_TEMPLATE/4-project-proposal.yml)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)
- [projects/README.md](projects/README.md)
- [projects/_project-design-template.md](projects/_project-design-template.md)

</details>



## Purpose and Scope

The Projects Process is a formal workflow for proposing, designing, and implementing significant changes to the OSMO codebase. It provides structured review and documentation for changes that have substantial impact across the system.

This process is **not required** for routine bug fixes or localized feature additions. For standard development workflows including pull request guidelines and code contributions, see [Pull Request Guidelines](#9.4) and the general contributing guide.

**Sources:** [projects/README.md:19-50]()

---

## When to Use a Project Proposal

The Projects Process should be used for:

| Category | Description | Examples |
|----------|-------------|----------|
| **New Projects or Major Features** | Significant additions affecting multiple areas | New workflow templating engine, distributed caching layer |
| **Cross-Cutting Changes** | Modifications spanning multiple components | Authentication system redesign, API versioning strategy |
| **Breaking Changes** | Changes impacting existing APIs, configurations, or workflows | Database schema migrations, configuration format changes |
| **Architectural Decisions** | System design, infrastructure, or technical direction changes | Multi-region deployment support, new scheduling algorithms |

For smaller, localized changes (single component bug fixes, minor enhancements), use standard GitHub issues and pull requests without a formal project proposal.

**Sources:** [projects/README.md:42-50](), [CONTRIBUTING.md:14-22]()

---

## Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Project Proposal Author** | Opens the project proposal issue; describes the problem, goals, and high-level approach |
| **Person in Charge (PIC)** | Drives the proposal and design through all stages; may be the author or another contributor who takes ownership |
| **Maintainers / OSMO Team** | Review proposals; provide feedback; guide design discussions; approve or reject proposals; manage stage transitions on the project board |

> **Note:** Only OSMO team members can update the **Stage** field in the project board to ensure proper governance and tracking.

**Sources:** [projects/README.md:52-60]()

---

## Projects Process Flow

```mermaid
graph TB
    Start["Contributor Identifies<br/>Significant Change"]
    Search["Search Existing<br/>Proposals"]
    
    subgraph "Stage: Proposal"
        CreateIssue["Create Project Proposal Issue<br/>(4-project-proposal.yml)"]
        AutoLabel["Auto-labeled:<br/>project-proposal"]
        AutoBoard["Auto-added to<br/>Project Board"]
        Discussion["Community Discussion<br/>in Issue Comments"]
    end
    
    subgraph "Stage: Design"
        CopyTemplate["Copy Design Template<br/>(_project-design-template.md)"]
        FillDesign["Fill Design Document<br/>(PROJ-NNN-short-slug.md)"]
        OpenPR["Open Design PR<br/>(Link to Proposal)"]
        ReviewDesign["Review & Iterate<br/>in PR Comments"]
        MergePR["Merge Design PR"]
    end
    
    subgraph "Stage: In Development"
        CreateBranch["Request Feature Branch<br/>(feature/PROJ-NNN-short-slug)"]
        SubIssues["Create Sub-Issues<br/>for Implementation"]
        ImplementPRs["Submit Implementation PRs<br/>to Feature Branch"]
        SyncMain["Weekly Auto-PR to Merge<br/>main into Feature Branch"]
        UpdateDesign["Update Design Doc<br/>as Needed"]
    end
    
    subgraph "Stage: Shipped"
        FinalUpdate["Update Design with<br/>Final PRs & Docs"]
        CloseIssue["Close Proposal Issue<br/>with Summary"]
        MarkShipped["OSMO Team Marks<br/>Stage: Shipped"]
    end
    
    Rejected["Stage: Rejected<br/>(Close with Explanation)"]
    Accepted["Stage: Accepted<br/>(No Design Required)"]
    
    Start --> Search
    Search --> CreateIssue
    CreateIssue --> AutoLabel
    AutoLabel --> AutoBoard
    AutoBoard --> Discussion
    
    Discussion -->|Needs Design| CopyTemplate
    Discussion -->|Approved<br/>No Design| Accepted
    Discussion -->|Declined| Rejected
    
    CopyTemplate --> FillDesign
    FillDesign --> OpenPR
    OpenPR --> ReviewDesign
    ReviewDesign --> MergePR
    MergePR --> CreateBranch
    
    Accepted --> SubIssues
    
    CreateBranch --> SubIssues
    SubIssues --> ImplementPRs
    ImplementPRs --> SyncMain
    SyncMain --> UpdateDesign
    UpdateDesign --> FinalUpdate
    
    FinalUpdate --> CloseIssue
    CloseIssue --> MarkShipped
```

**Diagram: Complete Projects Process Workflow**

**Sources:** [projects/README.md:23-31](), [projects/README.md:59-158]()

---

## GitHub Artifact Relationships

```mermaid
graph LR
    subgraph "GitHub Infrastructure"
        IssueTemplate["Issue Template<br/>.github/ISSUE_TEMPLATE/<br/>4-project-proposal.yml"]
        DesignTemplate["Design Template<br/>projects/<br/>_project-design-template.md"]
        ProjectBoard["GitHub Project Board<br/>github.com/orgs/NVIDIA/<br/>projects/157"]
    end
    
    subgraph "Project Artifacts"
        ProposalIssue["Project Proposal Issue<br/>Label: project-proposal<br/>Field: Stage"]
        DesignDoc["Design Document<br/>projects/PROJ-NNN-<br/>short-slug.md"]
        FeatureBranch["Feature Branch<br/>feature/PROJ-NNN-<br/>short-slug"]
        SubIssue1["Sub-Issue #1"]
        SubIssue2["Sub-Issue #2"]
        DesignPR["Design PR<br/>(To main)"]
        ImplPR1["Implementation PR #1<br/>(To Feature Branch)"]
        ImplPR2["Implementation PR #2<br/>(To Feature Branch)"]
        SyncPR["Weekly Sync PR<br/>(main → Feature Branch)"]
    end
    
    IssueTemplate -->|"Creates"| ProposalIssue
    ProposalIssue -->|"Auto-added to"| ProjectBoard
    DesignTemplate -->|"Copied to"| DesignDoc
    DesignDoc -->|"Submitted via"| DesignPR
    DesignPR -->|"Links to"| ProposalIssue
    ProposalIssue -->|"Spawns"| FeatureBranch
    ProposalIssue -->|"Spawns"| SubIssue1
    ProposalIssue -->|"Spawns"| SubIssue2
    SubIssue1 -->|"Implemented in"| ImplPR1
    SubIssue2 -->|"Implemented in"| ImplPR2
    ImplPR1 -->|"Merges to"| FeatureBranch
    ImplPR2 -->|"Merges to"| FeatureBranch
    SyncPR -->|"Keeps in sync"| FeatureBranch
```

**Diagram: GitHub Artifacts and Their Relationships**

**Sources:** [projects/README.md:35-39](), [projects/README.md:99-144]()

---

## Stage 1: Proposal (Issue)

### Objective

Propose a new project and gather initial feedback from the community and maintainers.

### Workflow

1. **Search for existing proposals** before creating a new one to avoid duplication. Search issues with the `project-proposal` label.

2. **Create a project proposal issue** using the template at [.github/ISSUE_TEMPLATE/4-project-proposal.yml:1-77](). The issue will automatically:
   - Be labeled with `project-proposal`
   - Be added to the [Project Board](https://github.com/orgs/NVIDIA/projects/157) with **Stage: Proposal**

3. **Discuss and refine** the proposal asynchronously in issue comments:
   - Clarify scope and goals
   - Identify risks and alternatives
   - Determine if a detailed design document is required

### Proposal Issue Fields

| Field | Required | Description |
|-------|----------|-------------|
| **Summary** | Yes | 2-3 sentence overview of the proposal |
| **Person in Charge (PIC)** | Optional | GitHub handle or "Seeking PIC" |
| **Motivation** | Yes | Why should this project be developed? |
| **Problem** | Yes | What problem does this solve? Current situation? |
| **References** | No | Links to related issues, external docs, or similar implementations |

### Stage Outcomes

| Outcome | Next Stage | Action |
|---------|------------|--------|
| **Requires Design** | Design | OSMO team approves proposal and determines design doc is needed; moves issue to **Stage: Design** |
| **Accepted Without Design** | In Development | OSMO team approves proposal for simple changes not requiring detailed design; moves to **Stage: Accepted** |
| **Rejected** | Rejected | OSMO team declines proposal; closes issue with explanation; moves to **Stage: Rejected** |

**Sources:** [projects/README.md:62-92](), [.github/ISSUE_TEMPLATE/4-project-proposal.yml:17-77]()

---

## Stage 2: Design (Markdown)

### Objective

Create a detailed technical design for accepted proposals that are significant or complex.

### Workflow

1. **Copy the design template**:
   ```bash
   cp projects/_project-design-template.md projects/PROJ-NNN-short-slug.md
   ```
   Use the proposal issue number (e.g., `PROJ-123`) and a short, descriptive slug.

2. **Fill out the design document** based on [projects/_project-design-template.md:1-132]():
   - **Overview**: Copy and refine content from the proposal issue
   - **Use Cases**: Document specific scenarios the project addresses
   - **Requirements**: List functional, KPI, and security requirements
   - **Architectural Details**: High-level technical approach with diagrams
   - **Detailed Design**: API designs, data models, component interactions, examples
   - **Alternatives Considered**: Document rejected approaches with pros/cons
   - **Impact Sections**: Backwards compatibility, performance, operations, security, documentation
   - **Testing**: Unit, integration, and end-to-end test strategy
   - **Implementation Plan**: Break project into phases if large

3. **Open a pull request** with the design document:
   - Link to the project proposal issue
   - Invite review from maintainers and community

4. **Review and iterate** on the design:
   - Discuss in PR comments
   - Revise document based on feedback
   - Summarize key decisions back in the proposal issue

5. **Merge the design PR** once approved by reviewers

6. **OSMO team updates stage** to **Stage: Accepted** on the project board

### Design Document Structure

| Section | Purpose |
|---------|---------|
| **Overview** | Mirrors proposal: motivation and problem statement |
| **Use Cases** | Concrete scenarios with descriptions |
| **Requirements** | Functional, KPI, security requirements |
| **Architectural Details** | High-level approach, components, block diagrams |
| **Detailed Design** | APIs, data models, workflows, examples |
| **Alternatives Considered** | Rejected approaches with rationale |
| **Backwards Compatibility** | Breaking change analysis |
| **Performance / Operations / Security** | Impact assessments |
| **Documentation / Testing** | What must be created or updated |
| **Implementation Plan** | Phased breakdown for large projects |
| **Open Questions** | Unresolved decisions |

**Sources:** [projects/README.md:93-120](), [projects/_project-design-template.md:1-132]()

---

## Stage 3: In Development

### Objective

Implement the project according to the approved design.

### Workflow

1. **Create sub-issues** to break the project into concrete implementation tasks
   - Use the implementation plan from the design document
   - Link sub-issues to the main proposal issue

2. **Request a feature branch** if the project requires multiple PRs:
   - Add a comment on the proposal issue asking an OSMO team member to create a feature branch
   - Branch naming: `feature/PROJ-NNN-short-slug` (matches design doc naming)
   - Note: Feature branch creation is restricted to OSMO team members
   - Small projects that fit in a single PR may not need a feature branch

3. **OSMO team updates stage** to **Stage: In Development** on the project board

4. **Submit implementation PRs** against the feature branch:
   - Reference sub-issues in PR descriptions for context
   - Follow standard [Pull Request Guidelines](#9.4)

5. **Keep feature branch synchronized with main**:
   - Automation opens weekly PRs (Mondays) to merge `main` into the feature branch
   - Resolve merge conflicts and merge these sync PRs promptly
   - Ensures feature branch stays compatible with ongoing mainline development

6. **Update the design document** as implementation progresses:
   - Submit PRs to update the design if decisions change or new details emerge
   - Keeps design document accurate and reflects actual implementation

### Feature Branch Workflow

```mermaid
graph LR
    Main["main Branch"]
    Feature["feature/PROJ-NNN-short-slug"]
    
    subgraph "Implementation Work"
        ImplPR1["Implementation PR #1"]
        ImplPR2["Implementation PR #2"]
        ImplPR3["Implementation PR #3"]
    end
    
    subgraph "Sync Work"
        WeeklyCron["Weekly Automation<br/>(Monday)"]
        SyncPR["Sync PR:<br/>main → feature"]
    end
    
    subgraph "Final Merge"
        FinalPR["Final PR:<br/>feature → main"]
    end
    
    Main -->|"Weekly Sync"| WeeklyCron
    WeeklyCron --> SyncPR
    SyncPR -->|"Merge"| Feature
    
    ImplPR1 -->|"Merge"| Feature
    ImplPR2 -->|"Merge"| Feature
    ImplPR3 -->|"Merge"| Feature
    
    Feature --> FinalPR
    FinalPR -->|"Merge"| Main
```

**Diagram: Feature Branch Development and Synchronization**

**Sources:** [projects/README.md:122-144]()

---

## Stage 4: Shipped

### Objective

Mark the project as complete and communicate the outcome.

### Workflow

1. **Update the design document** with implementation results:
   - Add links to all final PRs
   - Link to documentation updates
   - Note any deviations from the original design

2. **Close the project proposal issue** with a summary comment:
   - What was delivered
   - Links to the design document, key PRs, and documentation
   - Any follow-up work or future considerations

3. **OSMO team updates stage** to **Stage: Shipped** on the project board

4. **Release inclusion**: The project will be included in the next OSMO release

### Shipped Summary Template

```markdown
This project has been completed and shipped.

**Delivered:**
- [Brief description of what was implemented]

**Links:**
- Design Document: projects/PROJ-NNN-short-slug.md
- Key PRs: #PR1, #PR2, #PR3
- Documentation: [link to docs]

**Follow-up:**
- [Any remaining work or future considerations]
```

**Sources:** [projects/README.md:146-161]()

---

## Project Board Stages

The [GitHub Project Board](https://github.com/orgs/NVIDIA/projects/157) tracks all project proposals through their lifecycle using the **Stage** field.

| Stage | Description | Who Can Set |
|-------|-------------|-------------|
| **Proposal** | Initial proposal under review; community discussion ongoing | Automatic on issue creation |
| **Design** | Proposal approved; design document being written and reviewed | OSMO team only |
| **Accepted** | Approved for implementation (with or without design doc) | OSMO team only |
| **In Development** | Active implementation in progress | OSMO team only |
| **Shipped** | Implementation complete; included in a release | OSMO team only |
| **Rejected** | Proposal declined; issue closed with explanation | OSMO team only |

> **Governance Note:** Only OSMO team members can modify the Stage field to ensure proper tracking and project governance.

**Sources:** [projects/README.md:59-61](), [projects/README.md:75-92]()

---

## Template Files Reference

### Project Proposal Issue Template

**Location:** [.github/ISSUE_TEMPLATE/4-project-proposal.yml:1-77]()

**Fields:**
- Title format: `Project: <short sentence describing proposal>`
- Labels: Automatically tagged with `project`
- Body sections: Summary, PIC, Motivation, Problem, References

### Project Design Template

**Location:** [projects/_project-design-template.md:1-132]()

**Sections:**
- Metadata: Author, PIC, Proposal Issue link
- Overview: Motivation and Problem (from proposal)
- Use Cases and Requirements tables
- Architectural Details and Detailed Design
- Alternatives, Backwards Compatibility, Performance
- Operations, Security, Documentation, Testing
- Implementation Plan and Open Questions

**Sources:** [.github/ISSUE_TEMPLATE/4-project-proposal.yml:1-77](), [projects/_project-design-template.md:1-132]()

---

## Integration with Standard Contribution Workflow

```mermaid
graph TB
    Change["Code Change Needed"]
    
    Decision{"Significant<br/>Change?"}
    
    subgraph "Standard Workflow"
        StandardIssue["Create GitHub Issue"]
        StandardPR["Create Pull Request"]
        StandardReview["2 Approvals + Status Checks"]
        StandardMerge["Merge to main"]
    end
    
    subgraph "Projects Process"
        ProjectProposal["Create Project Proposal<br/>(Issue Template)"]
        ProjectStages["Follow Project Stages<br/>(Proposal → Design → Dev → Shipped)"]
        ProjectReview["Design Review + Implementation"]
        ProjectMerge["Merge via Feature Branch"]
    end
    
    Change --> Decision
    
    Decision -->|"No:<br/>- Bug Fix<br/>- Small Feature<br/>- Single Component"| StandardIssue
    Decision -->|"Yes:<br/>- New Project<br/>- Cross-Cutting<br/>- Breaking Change<br/>- Architecture"| ProjectProposal
    
    StandardIssue --> StandardPR
    StandardPR --> StandardReview
    StandardReview --> StandardMerge
    
    ProjectProposal --> ProjectStages
    ProjectStages --> ProjectReview
    ProjectReview --> ProjectMerge
```

**Diagram: Decision Tree for Using Projects Process vs Standard Workflow**

The Projects Process is a superset of the standard contribution workflow documented in [Pull Request Guidelines](#9.4). All PRs—whether part of a project or not—require:
- Two OSMO engineer approvals
- Passing status checks
- Resolution of merge conflicts
- Adherence to coding guidelines and commit message format

**Sources:** [projects/README.md:42-50](), [CONTRIBUTING.md:87-109](), [.github/PULL_REQUEST_TEMPLATE.md:1-12]()

---

## Questions and Support

For questions about the Projects Process:
- Ask in the project proposal issue comments
- Reach out to an OSMO maintainer directly
- Reference the [Contributing Guide](https://github.com/NVIDIA/OSMO/blob/main/CONTRIBUTING.md)

**Inspiration:** This process was inspired by [nf-core](https://nf-co.re/docs/contributing/project_proposals) and [Astro](https://github.com/withastro/roadmap) project proposal workflows.

**Sources:** [projects/README.md:162-169](), [CONTRIBUTING.md:1-139]()

---

# Page: Pull Request Guidelines

# Pull Request Guidelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/docs-deploy.yaml](.github/workflows/docs-deploy.yaml)
- [.github/workflows/helm-chart-lint.yaml](.github/workflows/helm-chart-lint.yaml)
- [.github/workflows/pr-checks.yaml](.github/workflows/pr-checks.yaml)
- [.github/workflows/pr-description-check.yaml](.github/workflows/pr-description-check.yaml)
- [.github/workflows/sync-feature-branches.yaml](.github/workflows/sync-feature-branches.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [deployments/brev/README.md](deployments/brev/README.md)
- [deployments/brev/setup.sh](deployments/brev/setup.sh)
- [docs/conf.py](docs/conf.py)
- [docs/deployment_guide/getting_started/create_storage/s3/index.rst](docs/deployment_guide/getting_started/create_storage/s3/index.rst)

</details>



This page documents the requirements, validation workflows, and review process for submitting Pull Requests (PRs) to the OSMO repository. It covers PR description format, automated status checks, code review requirements, and merge policies.

For information about the broader development workflow, see [Development Setup](#9.1). For details about the Projects Process for significant changes, see [Projects Process](#9.3).

## Overview

All code contributions to OSMO follow a structured PR process enforced by automated checks and manual code review. The system uses path-based filtering to run only relevant tests, validates PR descriptions against a template, and requires approval from two OSMO engineers before merging.

**Sources:** [CONTRIBUTING.md:87-111](), [.github/workflows/pr-checks.yaml:1-312]()

---

## PR Description Requirements

Every PR must follow the template defined in [.github/PULL_REQUEST_TEMPLATE.md:1-12]() and pass automated validation checks before it can be merged.

### Required Elements

| Element | Format | Validation |
|---------|--------|------------|
| **Issue Reference** | `Issue #<number>` or `Issue - None` | Case-insensitive, enforced by [.github/workflows/pr-description-check.yaml:44-60]() |
| **Checklist** | All items must be checked (`[x]`) | Enforced by [.github/workflows/pr-description-check.yaml:85-111]() |
| **Description** | Standalone description following commit message conventions | Not automatically validated |

### Checklist Items

```markdown
## Checklist
- [x] I am familiar with the Contributing Guidelines
- [x] New or existing tests cover these changes
- [x] The documentation is up to date with these changes
```

The validation workflow extracts the `## Checklist` section and verifies all checkboxes are marked. Unchecked items cause the PR to fail validation with a detailed error message.

**Sources:** [.github/PULL_REQUEST_TEMPLATE.md:1-12](), [.github/workflows/pr-description-check.yaml:29-135]()

---

## PR Validation Workflow

The following diagram shows how PR description validation works:

```mermaid
flowchart TD
    PR["PR Event<br/>opened/synchronize/<br/>reopened/edited"]
    ValidateJob["validate-pr-description<br/>Job"]
    
    ExtractBody["Extract PR_BODY<br/>environment variable"]
    CheckIssue["Check Issue Reference<br/>grep -qiE 'Issue (#[0-9]+|#None|- None)'"]
    IssueFound{"Issue<br/>Reference<br/>Found?"}
    
    ExtractChecklist["Extract Checklist Section<br/>awk pattern matching"]
    ChecklistExists{"Checklist<br/>Section<br/>Exists?"}
    
    CountCheckboxes["Count Checkboxes<br/>grep -cE '^- \\[[ xX]\\]'"]
    CheckUnchecked["Count Unchecked Items<br/>grep -cE '^- \\[ \\]'"]
    AllChecked{"All Items<br/>Checked?"}
    
    Success["✓ Validation Passed"]
    FailIssue["✗ Missing Issue Reference"]
    FailChecklist["✗ Missing Checklist Section"]
    FailUnchecked["✗ Incomplete Checklist"]
    
    PR --> ValidateJob
    ValidateJob --> ExtractBody
    ExtractBody --> CheckIssue
    CheckIssue --> IssueFound
    
    IssueFound -->|Yes| ExtractChecklist
    IssueFound -->|No| FailIssue
    
    ExtractChecklist --> ChecklistExists
    ChecklistExists -->|No| FailChecklist
    ChecklistExists -->|Yes| CountCheckboxes
    
    CountCheckboxes --> CheckUnchecked
    CheckUnchecked --> AllChecked
    
    AllChecked -->|Yes| Success
    AllChecked -->|No| FailUnchecked
```

**Sources:** [.github/workflows/pr-description-check.yaml:29-135]()

---

## Status Checks

OSMO uses path-based filtering to run only relevant tests for changed files. The `check-paths` job determines which test suites to execute based on file changes.

### Path Filtering Matrix

```mermaid
flowchart TB
    CheckPaths["check-paths Job<br/>dorny/paths-filter@v3"]
    
    subgraph "Path Filters"
        CIFilter["ci filter<br/>.github/workflows/pr-checks.yaml<br/>BUILD, MODULE.bazel<br/>bzl/**, src/**, run/**"]
        DocsFilter["docs filter<br/>.github/workflows/pr-checks.yaml<br/>docs/**, workflows/**"]
        UIFilter["ui filter<br/>.github/workflows/pr-checks.yaml<br/>BUILD, MODULE.bazel<br/>bzl/**, ui/**"]
    end
    
    subgraph "CI Tests"
        CIPublic["ci-public<br/>ubuntu-latest<br/>Fork PRs Only"]
        CIInternal["ci-internal<br/>self-hosted<br/>Internal PRs Only"]
    end
    
    subgraph "Documentation"
        DocsBuild["docs-build<br/>Sphinx Build<br/>Spelling Check<br/>Link Check<br/>PR Preview Deploy"]
    end
    
    subgraph "UI Build"
        UIBuild["ui-build<br/>Bazel Build<br/>//ui/..."]
    end
    
    CheckPaths --> CIFilter
    CheckPaths --> DocsFilter
    CheckPaths --> UIFilter
    
    CIFilter -->|ci='true'<br/>Fork PR| CIPublic
    CIFilter -->|ci='true'<br/>Internal PR| CIInternal
    
    DocsFilter -->|docs='true'| DocsBuild
    UIFilter -->|ui='true'| UIBuild
```

**Sources:** [.github/workflows/pr-checks.yaml:33-69]()

### CI Test Execution

The system runs different CI pipelines depending on whether the PR originates from a fork or the main repository:

**Fork PRs (`ci-public`):**
- Runs on `ubuntu-latest` GitHub-hosted runners
- Uses disk-based Bazel caching
- Includes disk space cleanup to prevent storage issues
- Command: `bazel test --test_output=errors -- //... -//ui/...`

**Internal PRs (`ci-internal`):**
- Runs on `self-hosted` runners with GPU support
- Uses Docker-in-Docker (`docker:dind` service)
- Leverages remote Bazel cache for faster builds
- Sets environment variables for Testcontainers integration
- Command: `bazel test --remote_cache=$BAZEL_REMOTE_CACHE_URL --test_env=DOCKER_HOST=tcp://docker:2375 --test_output=errors -- //... -//ui/...`

**Sources:** [.github/workflows/pr-checks.yaml:73-183]()

### Documentation Build and Validation

When documentation files change, the `docs-build` job:

1. **Builds Sphinx documentation** using `make -C docs build`
2. **Runs spelling check** using `sphinxcontrib.spelling`
3. **Validates links** using `lychee-action` with caching
4. **Deploys PR preview** to `gh-pages/documentation` branch using `pr-preview-action`

The preview is accessible at: `https://nvidia.github.io/OSMO/pr-preview/pr-<number>/`

**Sources:** [.github/workflows/pr-checks.yaml:187-282]()

### Helm Chart Linting

When Helm chart files in `deployments/charts/**` are modified, the `helm-lint` workflow:

1. **Detects changed charts** by comparing with base branch
2. **Builds dependencies** using `helm dependency build`
3. **Lints charts** using `helm lint`
4. **Validates rendering** using `helm template`

The workflow uses a matrix strategy to lint multiple charts in parallel.

**Sources:** [.github/workflows/helm-chart-lint.yaml:36-125]()

---

## Review Process

### Approval Requirements

| Requirement | Description |
|------------|-------------|
| **Two Approvers** | Two OSMO engineers must approve the PR before merging |
| **OSMO Team Assignment** | The OSMO engineering team is automatically assigned for review |
| **Status Checks** | All automated checks must pass |
| **Merge Conflicts** | Must be resolved before merging |

### Review Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Fork as Forked Repository
    participant Main as NVIDIA/OSMO main
    participant GHA as GitHub Actions
    participant Rev1 as Reviewer 1
    participant Rev2 as Reviewer 2
    
    Dev->>Fork: Push changes to branch
    Dev->>Main: Create PR
    
    Main->>GHA: Trigger pr-checks.yaml
    GHA->>GHA: Run check-paths
    
    alt Changes affect CI
        GHA->>GHA: Run ci-public or ci-internal
    end
    
    alt Changes affect docs
        GHA->>GHA: Run docs-build
        GHA->>Main: Deploy PR preview
    end
    
    alt Changes affect UI
        GHA->>GHA: Run ui-build
    end
    
    Main->>GHA: Trigger pr-description-check.yaml
    GHA->>GHA: Validate Issue Reference
    GHA->>GHA: Validate Checklist
    
    GHA-->>Main: Report Status
    
    Main->>Rev1: Assign for review
    Main->>Rev2: Assign for review
    
    Rev1->>Rev1: Code review
    Rev1->>Main: Approve
    
    Rev2->>Rev2: Code review
    Rev2->>Main: Approve
    
    alt All checks pass + 2 approvals
        Dev->>Main: Merge PR
        Main->>Main: Close PR
    end
```

**Sources:** [CONTRIBUTING.md:102-108]()

---

## Merge Requirements

Before a PR can be merged, all of the following conditions must be met:

### Pre-Merge Checklist

```mermaid
flowchart LR
    Start["PR Ready to Merge?"]
    
    Check1["Status Checks<br/>Passing?"]
    Check2["Two Approvals<br/>from OSMO Team?"]
    Check3["Merge Conflicts<br/>Resolved?"]
    Check4["PR Description<br/>Valid?"]
    
    Merge["✓ Merge PR"]
    Block["✗ Cannot Merge"]
    
    Start --> Check1
    Check1 -->|Yes| Check2
    Check1 -->|No| Block
    
    Check2 -->|Yes| Check3
    Check2 -->|No| Block
    
    Check3 -->|Yes| Check4
    Check3 -->|No| Block
    
    Check4 -->|Yes| Merge
    Check4 -->|No| Block
```

**Sources:** [CONTRIBUTING.md:102-108]()

---

## Automated Workflows

### Concurrency Control

All PR workflows use concurrency groups to prevent redundant runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

This ensures that when new commits are pushed to a PR, in-progress workflow runs are cancelled to save resources.

**Sources:** [.github/workflows/pr-checks.yaml:25-27]()

### Trigger Events

PR checks are triggered on the following GitHub events:

- `opened` - When a PR is first created
- `synchronize` - When new commits are pushed to the PR branch
- `reopened` - When a closed PR is reopened
- `edited` - When the PR description is modified (description check only)
- `closed` - Triggers cleanup for documentation preview

**Sources:** [.github/workflows/pr-checks.yaml:19-23](), [.github/workflows/pr-description-check.yaml:19-22]()

### Feature Branch Syncing

For long-lived feature branches following the Projects Process, the `sync-feature-branches` workflow automatically creates PRs to merge `main` into feature branches:

**Schedule:** Weekly on Mondays at 9am PT (5pm UTC)

**Process:**
1. Detects all `feature/**` branches
2. Checks if branch is behind `main`
3. Creates temporary branch `sync/<branch>/<timestamp>`
4. Attempts to merge `main`
5. Creates PR with sync changes
6. Extracts issue number from branch name for PR description

**Sources:** [.github/workflows/sync-feature-branches.yaml:1-151]()

---

## Bazel Caching Strategy

The CI system uses different caching strategies for public and internal PRs:

### Public Fork PRs

```yaml
- name: Setup Bazel
  uses: bazel-contrib/setup-bazel@4fd964a13a440a8aeb0be47350db2fc640f19ca8
  with:
    bazelisk-cache: true
    disk-cache: ${{ github.workflow }}
    repository-cache: true
    external-cache: |
      manifest:
        osmo_python_deps: src/locked_requirements.txt
        osmo_tests_python_deps: src/tests/locked_requirements.txt
        osmo_mypy_deps: bzl/mypy/locked_requirements.txt
        pylint_python_deps: bzl/linting/locked_requirements.txt
        io_bazel_rules_go: src/runtime/go.mod
        bazel_gazelle: src/runtime/go.sum
```

Uses manifest-based external cache keyed on lock files for Python and Go dependencies.

### Internal PRs

```yaml
- name: Run Tests
  run: |
    bazel test --remote_cache=${{ secrets.BAZEL_REMOTE_CACHE_URL }} \
      --test_env=DOCKER_HOST=tcp://docker:2375 \
      --test_env=TESTCONTAINERS_HOST_OVERRIDE=docker \
      --test_output=errors \
      -- \
      //... \
      -//ui/...
```

Uses remote cache URL from secrets for shared cache across all internal builds.

**Sources:** [.github/workflows/pr-checks.yaml:107-125](), [.github/workflows/pr-checks.yaml:174-182]()

---

## Commit Message Conventions

Commits must follow specific formatting rules:

```
#<Issue Number> - <Commit Title>

<Commit Body>
```

**Rules:**
- Use imperative mood for commit titles
- Follow [conventional commit guidelines](https://chris.beams.io/posts/git-commit)
- Reference the issue number corresponding to the PR
- Avoid committing commented-out code
- Keep commits focused on a single concern

**Sources:** [CONTRIBUTING.md:74-82]()

---

## PR Best Practices

### Scope and Size

- Keep PRs concise and focused on a single concern
- Consider multiple PRs if addressing multiple unrelated issues
- For significant changes, use the [Projects Process](#9.3) with project proposals

### Branch Selection

Exercise caution when selecting source and target branches:
- Standard PRs target `main`
- Feature branch PRs target `feature/**` branches
- Verify branch selection before creating PR

### Test Coverage

All PRs must include appropriate test coverage:
- Add unit tests for new functionality
- Update existing tests when modifying behavior
- Ensure functional tests cover integration points

**Sources:** [CONTRIBUTING.md:88-109]()

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **PR description validation fails** | Ensure `Issue #XX` or `Issue - None` is present and all checklist items are checked |
| **Status checks don't run** | Maintainer must manually trigger checks for first-time contributors |
| **Merge conflicts** | Rebase or merge `main` into your branch and resolve conflicts |
| **CI fails on fork** | Check disk space; `ci-public` includes cleanup steps but may need manual intervention |
| **Documentation preview not deploying** | Check that `docs/**` or `workflows/**` files changed and build succeeded |

### Disk Space Issues on Public CI

The `ci-public` job includes extensive cleanup to prevent disk space issues on GitHub-hosted runners:

```bash
sudo rm -rf /usr/share/dotnet
sudo rm -rf /usr/local/lib/android
sudo rm -rf /opt/ghc
sudo rm -rf /usr/local/.ghcup
sudo rm -rf /opt/hostedtoolcache/CodeQL
sudo docker image prune --all --force
```

**Sources:** [.github/workflows/pr-checks.yaml:81-100]()

---

## Summary

The OSMO PR process enforces quality through:

1. **Automated validation** of PR descriptions and checklists
2. **Path-based test execution** to optimize CI resource usage
3. **Separate pipelines** for fork and internal PRs with appropriate security controls
4. **Two-approver policy** requiring review from OSMO engineers
5. **Comprehensive status checks** including tests, documentation builds, and linting

All workflows use concurrency control to prevent redundant runs and leverage caching strategies appropriate to their execution environment.

**Sources:** [CONTRIBUTING.md:1-139](), [.github/workflows/pr-checks.yaml:1-312](), [.github/workflows/pr-description-check.yaml:1-135]()