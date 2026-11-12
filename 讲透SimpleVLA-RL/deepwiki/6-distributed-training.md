<!-- source: DeepWiki mcp.deepwiki.com · repo PRIME-RL/SimpleVLA-RL · page 6 Distributed Training · fetched 2026-10-30 -->

# Distributed Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [align.json](align.json)
- [verl/trainer/ppo/ray_trainer.py](verl/trainer/ppo/ray_trainer.py)

</details>



## Purpose and Scope

This page documents the distributed training infrastructure in SimpleVLA-RL, which leverages Ray for orchestrating multi-GPU and multi-node training. The system uses Ray's resource pooling to manage different worker types (ActorRollout, Critic, RefPolicy, RewardModel) and employs PyTorch's Fully Sharded Data Parallel (FSDP) to enable training of large Vision-Language-Action models that exceed single-GPU memory capacity.

For information about the overall training loop orchestration, see [PPO Training Loop](#3.1). For details on the actual policy update mechanics, see [Policy Updates and Actor](#3.2). For environment interaction specifics, see [Rollout Workers](#4.3).

---

## Ray Cluster Architecture

SimpleVLA-RL builds on veRL's Ray-based distributed infrastructure to coordinate training across multiple GPUs and nodes. The system organizes computational resources into pools that are dynamically allocated to different worker roles based on the training configuration.

```mermaid
graph TB
    subgraph RayCluster["Ray Cluster"]
        Head["Ray Head Node<br/>(main_ppo.py)"]
        
        subgraph ResourcePools["Resource Pools"]
            ARPool["ActorRollout Pool<br/>RayResourcePool"]
            CPool["Critic Pool<br/>RayResourcePool"]
            RefPool["RefPolicy Pool<br/>RayResourcePool"]
            RMPool["RewardModel Pool<br/>RayResourcePool"]
        end
    end
    
    subgraph WorkerGroups["Ray Worker Groups"]
        ARWG["actor_rollout_wg<br/>RayWorkerGroup"]
        CWG["critic_wg<br/>RayWorkerGroup"]
        RefWG["ref_policy_wg<br/>RayWorkerGroup"]
        RMWG["rm_wg<br/>RayWorkerGroup"]
    end
    
    subgraph Management["Management Layer"]
        RPM["ResourcePoolManager<br/>resource_pool_spec<br/>mapping<br/>resource_pool_dict"]
        RoleMap["Role Enum<br/>Actor, Rollout, ActorRollout<br/>Critic, RefPolicy, RewardModel"]
    end
    
    Head --> RPM
    RPM --> ARPool
    RPM --> CPool
    RPM --> RefPool
    RPM --> RMPool
    
    ARPool --> ARWG
    CPool --> CWG
    RefPool --> RefWG
    RMPool --> RMWG
    
    RoleMap -.defines roles for.-> RPM
```

**Sources:** [verl/trainer/ppo/ray_trainer.py:42-53](), [verl/trainer/ppo/ray_trainer.py:55-79](), [README.md:46-48]()

The Ray cluster is initialized in `main_ppo.py`, which serves as the entry point for distributed training. The `RayTrainer` class in [verl/trainer/ppo/ray_trainer.py:247-830]() manages the lifecycle of all worker groups and coordinates their interactions during training.

---

## Resource Pool Management

The `ResourcePoolManager` dataclass [verl/trainer/ppo/ray_trainer.py:55-79]() is responsible for creating and mapping Ray resource pools to worker roles. Each resource pool represents a collection of GPU resources that can be allocated to worker groups.

### ResourcePoolManager Structure

| Field | Type | Purpose |
|-------|------|---------|
| `resource_pool_spec` | `dict[str, list[int]]` | Specification of which processes run on which nodes |
| `mapping` | `dict[Role, str]` | Maps worker roles to resource pool names |
| `resource_pool_dict` | `dict[str, RayResourcePool]` | Instantiated resource pools |

### Resource Pool Creation

The `create_resource_pool()` method [verl/trainer/ppo/ray_trainer.py:65-74]() instantiates `RayResourcePool` objects based on the specification:

```python
resource_pool = RayResourcePool(
    process_on_nodes=process_on_nodes,
    use_gpu=True,
    max_colocate_count=1,  # Recommended for FSDP backend
    name_prefix=resource_pool_name
)
```

The `max_colocate_count=1` setting merges all worker groups into a single process per resource pool, which is the recommended configuration for FSDP to maximize memory efficiency and minimize communication overhead.

### Role-to-Pool Mapping

The `get_resource_pool()` method [verl/trainer/ppo/ray_trainer.py:76-78]() retrieves the appropriate resource pool for a given role, enabling flexible resource allocation strategies where different roles can share or have dedicated GPU resources.

**Sources:** [verl/trainer/ppo/ray_trainer.py:55-79](), [verl/trainer/ppo/ray_trainer.py:393-467]()

---

## Worker Roles and Responsibilities

The system defines worker roles through the `Role` enum [verl/trainer/ppo/ray_trainer.py:42-53](), which determines the computational responsibilities of each worker group.

```mermaid
graph LR
    subgraph Roles["Role Enum"]
        Actor["Actor<br/>Role.Actor"]
        Rollout["Rollout<br/>Role.Rollout"]
        ActorRollout["ActorRollout<br/>Role.ActorRollout"]
        Critic["Critic<br/>Role.Critic"]
        RefPolicy["RefPolicy<br/>Role.RefPolicy"]
        RewardModel["RewardModel<br/>Role.RewardModel"]
    end
    
    subgraph Responsibilities["Worker Responsibilities"]
        ARResp["ActorRollout Worker<br/>- VLA model inference<br/>- Environment interaction<br/>- Policy gradient updates<br/>- Trajectory collection"]
        CResp["Critic Worker<br/>- Value function estimation<br/>- GAE computation"]
        RefResp["RefPolicy Worker<br/>- Reference log_prob computation<br/>- KL divergence baseline"]
        RMResp["RewardModel Worker<br/>- Reward scoring<br/>(optional)"]
    end
    
    subgraph WorkerImplementations["Worker Implementations"]
        ARImpl["dp_rob.py<br/>rob_rollout.py"]
        CImpl["critic worker<br/>(veRL)"]
        RefImpl["reference policy<br/>(veRL)"]
        RMImpl["reward model<br/>(veRL)"]
    end
    
    ActorRollout --> ARResp
    Critic --> CResp
    RefPolicy --> RefResp
    RewardModel --> RMResp
    
    ARResp --> ARImpl
    CResp --> CImpl
    RefResp --> RefImpl
    RMResp --> RMImpl
```

**Sources:** [verl/trainer/ppo/ray_trainer.py:42-53](), [verl/trainer/ppo/ray_trainer.py:264-274]()

### Hybrid Engine Mode

SimpleVLA-RL operates in "hybrid engine" mode [verl/trainer/ppo/ray_trainer.py:264-269](), which combines the Actor and Rollout roles into a single `ActorRollout` worker group. This design decision reduces communication overhead and memory transfer between policy updates and trajectory collection.

The hybrid engine assertion [verl/trainer/ppo/ray_trainer.py:265]() ensures that `Role.ActorRollout` is present in the worker mapping, as this is currently the only supported configuration.

### Conditional Worker Creation

Not all worker roles are required for every training configuration:

- **Critic Worker**: Only created when using GAE advantage estimation [verl/trainer/ppo/ray_trainer.py:410-422]()
- **Reference Policy Worker**: Only created when KL divergence control is enabled [verl/trainer/ppo/ray_trainer.py:425-430]()
- **Reward Model Worker**: Optional, for learned reward functions [verl/trainer/ppo/ray_trainer.py:433-437]()

**Sources:** [verl/trainer/ppo/ray_trainer.py:264-274](), [verl/trainer/ppo/ray_trainer.py:410-437]()

---

## Worker Group Instantiation

The `init_workers()` method [verl/trainer/ppo/ray_trainer.py:393-467]() orchestrates the creation and initialization of all worker groups required for training.

```mermaid
sequenceDiagram
    participant Trainer as RayTrainer
    participant RPM as ResourcePoolManager
    participant Pool as RayResourcePool
    participant WG as RayWorkerGroup
    participant Worker as Actual Workers
    
    Trainer->>RPM: create_resource_pool()
    RPM->>Pool: Initialize RayResourcePool(s)
    
    Trainer->>Trainer: Build resource_pool_to_cls mapping
    Note over Trainer: Map roles to worker classes<br/>with init args
    
    loop For each resource pool
        Trainer->>Trainer: create_colocated_worker_cls(class_dict)
        Trainer->>WG: Initialize RayWorkerGroup
        WG->>WG: spawn(prefix_set)
        WG-->>Trainer: Return spawned worker groups
    end
    
    alt Use Critic
        Trainer->>WG: critic_wg.init_model()
    end
    
    alt Use Reference Policy
        Trainer->>WG: ref_policy_wg.init_model()
    end
    
    alt Use Reward Model
        Trainer->>WG: rm_wg.init_model()
    end
    
    Trainer->>WG: actor_rollout_wg.init_model()
    Note over Trainer: Actor/Rollout initialized last<br/>for better vLLM memory estimation
```

**Sources:** [verl/trainer/ppo/ray_trainer.py:393-467]()

### Worker Class Specification

Workers are instantiated using `RayClassWithInitArgs` [verl/trainer/ppo/ray_trainer.py:402-405](), which wraps the worker class with its configuration:

```python
actor_rollout_cls = RayClassWithInitArgs(
    cls=self.role_worker_mapping[Role.ActorRollout],
    config=self.config.actor_rollout_ref,
    role='actor_rollout'
)
```

The `role_worker_mapping` dictionary maps each `Role` to its corresponding worker implementation class (e.g., `FSDPWorker` from `verl/workers/fsdp_workers.py`).

### Colocated Worker Pattern

The `create_colocated_worker_cls()` function [verl/trainer/ppo/ray_trainer.py:446]() enables multiple worker types to share the same Ray actors, reducing memory overhead and inter-process communication. All workers in the same resource pool are colocated, with `max_colocate_count=1` ensuring they run in the same process space.

### Worker Initialization Order

The actor/rollout worker is initialized last [verl/trainer/ppo/ray_trainer.py:466-467]() to allow vLLM (if used) to make a more accurate estimate of available KV cache memory after other models have been loaded.

**Sources:** [verl/trainer/ppo/ray_trainer.py:393-467](), [verl/trainer/ppo/ray_trainer.py:440-451]()

---

## FSDP Integration and Memory Optimization

SimpleVLA-RL uses PyTorch's Fully Sharded Data Parallel (FSDP) to enable training of large VLA models by sharding model parameters, gradients, and optimizer states across multiple GPUs.

### FSDP Worker Architecture

```mermaid
graph TB
    subgraph FSDPWorkerGroup["FSDP Worker Group"]
        direction TB
        WG["RayWorkerGroup<br/>world_size = N GPUs"]
        
        subgraph Workers["Individual Workers"]
            W1["Worker 0<br/>GPU 0<br/>Model shard 0"]
            W2["Worker 1<br/>GPU 1<br/>Model shard 1"]
            W3["Worker ...<br/>GPU ...<br/>Model shard ..."]
            WN["Worker N-1<br/>GPU N-1<br/>Model shard N-1"]
        end
        
        WG --> W1
        WG --> W2
        WG --> W3
        WG --> WN
    end
    
    subgraph ModelOperations["FSDP Operations"]
        Forward["Forward Pass<br/>- All-gather parameters<br/>- Compute activations<br/>- Discard parameters"]
        Backward["Backward Pass<br/>- All-gather parameters<br/>- Compute gradients<br/>- Reduce-scatter gradients"]
        Update["Optimizer Update<br/>- Update local shard<br/>- Discard full gradients"]
    end
    
    subgraph MemoryStrategy["Memory Optimization"]
        Offload["CPU Offloading<br/>- Parameters<br/>- Gradients<br/>- Optimizer states"]
        Mixed["Mixed Precision<br/>- bf16 computation<br/>- fp32 optimizer states"]
    end
    
    Workers --> Forward
    Forward --> Backward
    Backward --> Update
    
    Offload -.reduces GPU memory.-> Workers
    Mixed -.reduces memory + speeds up.-> Workers
```

**Sources:** [README.md:48](), [verl/workers/fsdp_workers.py]()

### Data Parallelism with FSDP

The `actor_rollout_wg.world_size` [verl/trainer/ppo/ray_trainer.py:484]() represents the total number of GPUs participating in training. For tensor model parallelism (if enabled), the data parallel size is calculated as:

```python
dp_size = self.actor_rollout_wg.world_size // self.config.actor_rollout_ref.rollout.tensor_model_parallel_size
```

This allows the system to support both data parallelism (multiple replicas processing different data) and tensor parallelism (single model split across GPUs).

### Sharding Strategy

FSDP supports multiple sharding strategies:

| Strategy | Parameters | Gradients | Optimizer States | Memory Efficiency |
|----------|-----------|-----------|------------------|-------------------|
| `FULL_SHARD` | Sharded | Sharded | Sharded | Highest |
| `SHARD_GRAD_OP` | Replicated | Sharded | Sharded | Medium |
| `NO_SHARD` | Replicated | Replicated | Replicated | Lowest (DDP) |

SimpleVLA-RL uses `FULL_SHARD` by default to maximize memory efficiency for large VLA models.

### CPU Offloading

To further reduce GPU memory usage, FSDP can offload components to CPU:

- **Parameter Offloading**: Parameters are stored on CPU and moved to GPU only during forward/backward passes
- **Gradient Offloading**: Gradients are immediately moved to CPU after computation
- **Optimizer State Offloading**: Optimizer momentum and variance buffers reside on CPU

The offloading configuration is specified in the model configuration under `actor_rollout_ref.model.fsdp_config`.

**Sources:** [README.md:48](), [verl/trainer/ppo/ray_trainer.py:484](), [verl/workers/fsdp_workers.py]()

---

## Environment Variables for Distributed Training

The `align.json` configuration file [align.json:1-14]() sets critical environment variables for distributed training:

| Variable | Value | Purpose |
|----------|-------|---------|
| `NCCL_DEBUG` | `WARN` | Controls NCCL (NVIDIA Collective Communications Library) logging verbosity for multi-GPU communication |
| `RAY_memory_monitor_refresh_ms` | `0` | Disables Ray's memory monitoring refresh to reduce overhead |
| `VLLM_ATTENTION_BACKEND` | `XFORMERS` | Selects XFormers as the attention implementation for vLLM (if used) |
| `PYTORCH_CUDA_ALLOC_CONF` | `expandable_segments:True` | Enables PyTorch's expandable CUDA memory segments to reduce fragmentation |
| `TOKENIZERS_PARALLELISM` | `true` | Enables parallel tokenization |
| `WANDB_API_KEY` | User-provided | Authentication for Weights & Biases experiment tracking |

These environment variables are loaded by `main_ppo.py` before initializing the Ray cluster.

**Sources:** [align.json:1-14](), [README.md:116]()

---

## Configuration Example

Here is a typical configuration for distributed training on 2 nodes with 8 GPUs each:

```yaml
# Resource allocation
actor_rollout_ref:
  rollout:
    tensor_model_parallel_size: 1  # No tensor parallelism
    name: fsdp
  
  model:
    fsdp_config:
      sharding_strategy: "FULL_SHARD"
      cpu_offload: false  # Keep on GPU for speed
      mixed_precision: true  # Use bf16
  
  actor:
    optim:
      lr: 1e-5
      total_training_steps: 1000  # Computed dynamically

# Training configuration  
trainer:
  total_epochs: 3
  save_freq: 100
  test_freq: 50
  
data:
  train_batch_size: 32
  n_samples: 8  # Responses per prompt
```

The shell script would specify:

```bash
NUM_NODES=2
NUM_GPUS=8
```

This results in 16 total GPUs being utilized, with the model sharded via FSDP across all GPUs in each worker group.

**Sources:** [README.md:119-135](), [verl/trainer/ppo/ray_trainer.py:329-334]()

---

## Worker Communication Patterns

```mermaid
graph TB
    subgraph TrainingIteration["Single Training Iteration"]
        Generate["actor_rollout_wg.generate_sequences()<br/>- Parallel trajectory collection<br/>- Each GPU processes batch/dp_size prompts"]
        
        RefLogProb["ref_policy_wg.compute_ref_log_prob()<br/>- Compute reference policy logits<br/>- Used for KL penalty"]
        
        Advantage["Driver Process<br/>compute_advantage()<br/>- CPU-based advantage computation<br/>- Supports GAE, RLOO, GRPO"]
        
        ActorUpdate["actor_rollout_wg.update_actor()<br/>- FSDP-synchronized gradient computation<br/>- All-reduce across GPUs<br/>- Optimizer step on local shards"]
        
        CriticUpdate["critic_wg.update_critic()<br/>- Value function training<br/>- Only if using GAE"]
    end
    
    Generate --> RefLogProb
    RefLogProb --> Advantage
    Advantage --> ActorUpdate
    Advantage --> CriticUpdate
```

**Sources:** [verl/trainer/ppo/ray_trainer.py:549](), [verl/trainer/ppo/ray_trainer.py:614-616](), [verl/trainer/ppo/ray_trainer.py:649-654](), [verl/trainer/ppo/ray_trainer.py:662-671]()

The training loop follows a gather-compute-update pattern:

1. **Generation Phase** [verl/trainer/ppo/ray_trainer.py:549](): Worker group generates trajectories in parallel, with data automatically distributed across GPUs
2. **Reference Policy Phase** [verl/trainer/ppo/ray_trainer.py:614-616](): If KL control is enabled, compute reference log probabilities
3. **Advantage Computation** [verl/trainer/ppo/ray_trainer.py:649-654](): Centralized computation on the driver process
4. **Policy Update** [verl/trainer/ppo/ray_trainer.py:662-671](): FSDP-synchronized gradient computation and optimizer step

All worker group methods automatically handle data distribution and collection across the distributed workers.

**Sources:** [verl/trainer/ppo/ray_trainer.py:469-716]()

---

