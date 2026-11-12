<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vidur · page 6 Scheduling and Resource Management · fetched 2026-10-26 -->

# Scheduling and Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vidur/config/config.py](vidur/config/config.py)
- [vidur/config/device_sku_config.py](vidur/config/device_sku_config.py)
- [vidur/config/model_config.py](vidur/config/model_config.py)
- [vidur/config/node_sku_config.py](vidur/config/node_sku_config.py)
- [vidur/request_generator/synthetic_request_generator.py](vidur/request_generator/synthetic_request_generator.py)
- [vidur/simulator.py](vidur/simulator.py)

</details>



This page covers Vidur's multi-level scheduling system and resource management capabilities. The system employs a hierarchical approach with global schedulers for distributing requests across replicas and replica schedulers for managing local execution within each replica. Resource management encompasses memory allocation, KV cache management, batching strategies, and preemption policies.

For workload generation and request characteristics, see [Request Generation](#5). For performance modeling and execution time prediction, see [Performance Modeling](#7).

## Multi-Level Scheduling Architecture

Vidur implements a two-tier scheduling architecture that separates global load balancing from local resource management. The global scheduler distributes incoming requests across available replicas, while each replica scheduler manages its local request queue and resource allocation.

### Scheduling System Overview

```mermaid
graph TB
    subgraph "Simulator Core"
        Sim["Simulator"] --> EventQ["_event_queue: List[BaseEvent]"]
        Sim --> GlobalSched["_scheduler: BaseGlobalScheduler"]
        Sim --> Cluster["_cluster: Cluster"]
    end
    
    subgraph "Global Scheduling Layer"
        GlobalSched --> RR["RoundRobinGlobalScheduler"]
        GlobalSched --> LOR["LORGlobalScheduler"]
        GlobalSched --> LOP["LOPGlobalScheduler"]
        GlobalSched --> Random["RandomGlobalScheduler"]
    end
    
    subgraph "Replica Management"
        Cluster --> Replicas["replicas: List[Replica]"]
        Replicas --> ReplicaSched["replica_scheduler"]
        ReplicaSched --> VLLM["VllmScheduler"]
        ReplicaSched --> Sarathi["SarathiScheduler"]
        ReplicaSched --> ORCA["OrcaScheduler"]
    end
    
    subgraph "Resource Management"
        ReplicaSched --> BatchMgr["batch_manager"]
        ReplicaSched --> Cache["cache_manager"]
        ReplicaSched --> ReqQueue["request_queue"]
        Cache --> KVCache["kv_cache_manager"]
        Cache --> MemAlloc["memory_allocator"]
    end
```

Sources: [vidur/simulator.py:22-54](), [vidur/config/config.py:605-704](), [vidur/config/config.py:342-416]()

## Global Scheduling Strategies

Global schedulers handle request distribution across replicas in the cluster. Each strategy optimizes for different objectives such as load balancing, minimizing outstanding requests, or maintaining session affinity.

### Global Scheduler Types and Configurations

| Scheduler Type | Configuration Class | Strategy |
|----------------|-------------------|----------|
| `ROUND_ROBIN` | `RoundRobinGlobalSchedulerConfig` | Cyclic request distribution |
| `LOR` | `LORGlobalSchedulerConfig` | Least Outstanding Requests |
| `LOP` | `LOPGlobalSchedulerConfig` | Least Outstanding Pairs |
| `RANDOM` | `RandomGlobalSchedulerConfig` | Random replica selection |
| `STICKY_ROUND_ROBIN` | `StickyRoundRobinGlobalSchedulerConfig` | Session-aware round robin |
| `STICKY_LOR` | `StickyLorGlobalSchedulerConfig` | Session-aware LOR |

Sources: [vidur/config/config.py:619-704]()

### Request Distribution Flow

```mermaid
graph LR
    subgraph "Request Arrival"
        ReqArr["RequestArrivalEvent"] --> GlobalSch["BaseGlobalScheduler"]
    end
    
    subgraph "Scheduling Decision"
        GlobalSch --> SelectReplica["select_replica()"]
        SelectReplica --> LoadMetrics["Outstanding requests/pairs"]
        LoadMetrics --> Decision["Replica selection"]
    end
    
    subgraph "Request Dispatch"
        Decision --> TargetRep["target_replica"]
        TargetRep --> RepQueue["replica.request_queue"]
        RepQueue --> RepSched["replica.scheduler"]
    end
    
    subgraph "Scheduling Variants"
        LORImpl["LOR: min outstanding requests"]
        LOPImpl["LOP: min outstanding prefill/decode pairs"] 
        RRImpl["RoundRobin: cyclic assignment"]
    end
```

Sources: [vidur/events/__init__.py](), [vidur/scheduler/global_scheduler/]()

## Replica Scheduling Algorithms

Replica schedulers manage local request execution, batching, and resource allocation within individual replicas. Each algorithm implements different strategies for optimizing throughput and latency.

### Replica Scheduler Implementations

```mermaid
graph TB
    subgraph "BaseReplicaScheduler Interface"
        BaseRS["BaseReplicaScheduler"] --> Schedule["schedule()"]
        BaseRS --> AddReq["add_request()"]
        BaseRS --> GetBatch["get_next_batch()"]
    end
    
    subgraph "vLLM Schedulers"
        VllmV0["VllmScheduler"] --> BatchSize["max_tokens_in_batch: 4096"]
        VllmV1["VllmV1Scheduler"] --> ChunkSize["chunk_size: 512"]
        VllmV1Disk["VllmV1DiskScheduler"] --> DiskCache["disk_caching"]
    end
    
    subgraph "Specialized Schedulers"
        Sarathi["SarathiScheduler"] --> ChunkedPrefill["chunked_prefill"]
        ORCA["OrcaScheduler"] --> IterativeBatch["iterative_batching"]
        FT["FasterTransformerScheduler"] --> StaticBatch["static_batching"]
    end
    
    BaseRS --> VllmV0
    BaseRS --> VllmV1
    BaseRS --> Sarathi
    BaseRS --> ORCA
```

Sources: [vidur/config/config.py:355-416]()

### Scheduling Configuration Parameters

| Parameter | Description | Impact |
|-----------|-------------|--------|
| `batch_size_cap` | Maximum requests per batch | Memory vs. throughput tradeoff |
| `max_tokens_in_batch` | Token limit for vLLM batches | Controls batch density |
| `chunk_size` | Prefill chunking granularity | Preemption granularity |

Sources: [vidur/config/config.py:343-411]()

## Resource Management

The resource management system handles memory allocation, KV cache management, and batch scheduling to optimize hardware utilization while maintaining performance guarantees.

### Cache and Memory Management

```mermaid
graph TB
    subgraph "CacheConfig"
        CacheConf["CacheConfig"] --> BlockSize["block_size: 16"]
        CacheConf --> NumBlocks["num_blocks: Optional[int]"]
        CacheConf --> Watermark["watermark_blocks_fraction: 0.01"]
        CacheConf --> MemMargin["memory_margin_fraction: 0.1"]
    end
    
    subgraph "Caching Features"
        PrefixCache["enable_prefix_caching: bool"]
        DiskCache["enable_disk_caching: bool"]
        HashAlgo["prefix_caching_hash_algo"]
        PreAlloc["num_preallocate_tokens: 64"]
    end
    
    subgraph "Memory Allocation"
        BlockMgr["BlockManager"] --> KVBlocks["kv_cache_blocks"]
        BlockMgr --> FreeBlocks["free_blocks"]
        BlockMgr --> WatermarkCheck["watermark_check()"]
    end
    
    CacheConf --> PrefixCache
    CacheConf --> DiskCache
    BlockMgr --> CacheConf
```

Sources: [vidur/config/config.py:304-339]()

### Preemption and Batching Strategies

Vidur supports sophisticated preemption mechanisms that allow interrupted requests to resume execution while maintaining state consistency through the KV cache system.

```mermaid
graph LR
    subgraph "Batch Formation"
        ReqQueue["RequestQueue"] --> BatchBuilder["batch_builder"]
        BatchBuilder --> PrefillBatch["prefill_batch"]
        BatchBuilder --> DecodeBatch["decode_batch"]
    end
    
    subgraph "Preemption Logic"
        MemPressure["memory_pressure"] --> PreemptDecision["preempt_decision"]
        PreemptDecision --> SaveState["save_kv_state"]
        SaveState --> FreeBlocks["free_memory_blocks"]
    end
    
    subgraph "Resume Logic"
        MemAvailable["memory_available"] --> LoadState["load_kv_state"]
        LoadState --> RestoreBatch["restore_to_batch"]
        RestoreBatch --> ContinueExec["continue_execution"]
    end
```

Sources: [vidur/config/config.py:304-339]()

## Request Queueing and Prioritization

The system supports multiple queueing disciplines to handle different service level objectives and fairness requirements.

### Queue Types and Implementations

```mermaid
graph TB
    subgraph "BaseRequestQueueConfig"
        BaseQueue["BaseRequestQueueConfig"] --> FCFS["FCFSRequestQueueConfig"]
        BaseQueue --> EDF["EDFRequestQueueConfig"]
    end
    
    subgraph "Queue Behavior"
        FCFS --> FIFOOrder["First Come First Served"]
        EDF --> DeadlineOrder["Earliest Deadline First"]
    end
    
    subgraph "SLO Integration"
        SLOConf["SloConfig"] --> TTFTTarget["prefill_e2e_time_normalized"]
        SLOConf --> TTFTMin["prefill_e2e_time_min"]
        EDF --> SLOConf
    end
```

Sources: [vidur/config/config.py:583-602](), [vidur/config/config.py:292-301]()

## Parallelism and Distributed Execution

Vidur models tensor parallelism and pipeline parallelism to simulate distributed inference workloads across multiple GPUs and nodes.

### Parallelism Configuration

```mermaid
graph TB
    subgraph "ReplicaConfig Parallelism"
        RepConf["ReplicaConfig"] --> TPSize["tensor_parallel_size: 1"]
        RepConf --> PPStages["num_pipeline_stages: 1"] 
        RepConf --> WorldSize["world_size = TP × PP"]
    end
    
    subgraph "Model Sharding"
        ModelConf["model_config"] --> QHeads["num_q_heads"]
        ModelConf --> Layers["num_layers"]
        ModelConf --> EmbedDim["embedding_dim"]
    end
    
    subgraph "Computed Properties"
        QPW["q_heads_per_tensor_parallel_worker"]
        KVPW["kv_heads_per_tensor_parallel_worker"]
        LPP["num_layers_per_pipeline_stage"]
    end
    
    RepConf --> ModelConf
    ModelConf --> QPW
    ModelConf --> KVPW
    ModelConf --> LPP
```

Sources: [vidur/config/config.py:513-580]()

## Configuration System Integration

The scheduling and resource management components are configured through a hierarchical configuration system that allows fine-grained control over system behavior.

### Configuration Hierarchy

```mermaid
graph TB
    subgraph "SimulationConfig"
        SimConf["SimulationConfig"] --> ClusterConf["cluster_config: ClusterConfig"]
    end
    
    subgraph "ClusterConfig Components"
        ClusterConf --> NumReplicas["num_replicas: int"]
        ClusterConf --> RepConf["replica_config: ReplicaConfig"]
        ClusterConf --> CacheConf["cache_config: CacheConfig"]
        ClusterConf --> GlobalSchedConf["global_scheduler_config"]
        ClusterConf --> RepSchedConf["replica_scheduler_config"]
        ClusterConf --> QueueConf["request_queue_config"]
    end
    
    subgraph "Scheduler Polymorphism"
        GlobalSchedConf --> BaseGlobalSched["BaseGlobalSchedulerConfig"]
        RepSchedConf --> BaseRepSched["BaseReplicaSchedulerConfig"]
        QueueConf --> BaseQueue["BaseRequestQueueConfig"]
    end
```

Sources: [vidur/config/config.py:854-876](), [vidur/config/config.py:879-934]()

---

