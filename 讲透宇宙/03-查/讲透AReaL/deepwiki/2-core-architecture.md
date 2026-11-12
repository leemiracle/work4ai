<!-- source: DeepWiki mcp.deepwiki.com · repo areal-project/AReaL · page 2 Core Architecture · fetched 2026-10-21 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/workflows/pre-commit.yml](.github/workflows/pre-commit.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [ROADMAP.md](ROADMAP.md)
- [areal/api/alloc_mode.py](areal/api/alloc_mode.py)
- [areal/api/cli_args.py](areal/api/cli_args.py)
- [areal/engine/fsdp_engine.py](areal/engine/fsdp_engine.py)
- [areal/engine/megatron_engine.py](areal/engine/megatron_engine.py)
- [areal/experimental/engine/archon_engine.py](areal/experimental/engine/archon_engine.py)
- [blog/AReaL_v0_2.md](blog/AReaL_v0_2.md)
- [blog/AReaL_v0_3.md](blog/AReaL_v0_3.md)
- [docs/en/cli_reference.md](docs/en/cli_reference.md)
- [docs/en/version_history.md](docs/en/version_history.md)
- [docs/zh/cli_reference.md](docs/zh/cli_reference.md)
- [docs/zh/version_history.md](docs/zh/version_history.md)
- [examples/countdown/README.md](examples/countdown/README.md)
- [examples/tau2/README.md](examples/tau2/README.md)

</details>



AReaL is designed as a high-performance, fully asynchronous reinforcement learning system optimized for large-scale foundation model alignment. Unlike traditional synchronous RL frameworks where generation and training happen sequentially, AReaL decouples these processes into independent, concurrent services. This architecture eliminates hardware underutilization caused by variable-length sequence generation and enables industry-leading scalability across thousands of GPUs.

Sources: [README.md:15-21](), [blog/AReaL_v0_3.md:79-87]()

## The Four-Component Model

The system architecture is structured into four primary functional components that interact asynchronously to maintain high throughput.

### 1. Rollout Workers
These workers host the policy model using high-performance inference engines like SGLang or vLLM. They handle `generate` requests from the controller and `update_weights` requests from the trainers. A key feature is the **Interruptible Rollout**, where workers can update model weights in-flight, re-computing KV caches to ensure trajectories remain as on-policy as possible.
- **Code Entities**: `InferenceEngine` [areal/api/cli_args.py:452-453](), `SGLangEngine`, `vLLMEngine`.
- **For details, see [Inference Engines & Rollout](#4)**.

### 2. Reward Service
An asynchronous service that evaluates generated responses. For verifiable rewards (e.g., math or coding), it executes unit tests or symbolic solvers to provide ground-truth feedback.
- **Code Entities**: `AsyncRewardWrapper`, `reward_fn`.
- **For details, see [Datasets & Rewards](#7)**.

### 3. Trainer Workers
These workers run the training backend (FSDP2, Megatron-Core, or Archon). They consume completed trajectories from the data service, compute gradients, update model parameters, and trigger weight synchronization across the cluster.
- **Code Entities**: `TrainEngine` [areal/api/cli_args.py:417-418](), `FSDPEngine` [areal/engine/fsdp_engine.py:219-220](), `MegatronEngine` [areal/engine/megatron_engine.py:168-169]().
- **For details, see [Training Engines](#3)**.

### 4. Rollout Controller
The orchestrator that manages the lifecycle of an RL episode. It fetches prompts from the dataset, dispatches them to Rollout Workers, routes responses to the Reward Service, and pushes the final trajectories into the replay buffer for the Trainers.
- **Code Entities**: `DistRolloutCoordinator` [areal/infra/dist_rollout.py:1-20](), `RolloutWorkflow`.
- **For details, see [Rollout Controller & Staleness Management](#4.2)**.

Sources: [blog/AReaL_v0_3.md:89-117](), [AGENTS.md:61-72]()

## Asynchronous Execution & Data Flow

The following diagram illustrates the transition from high-level RL concepts to the specific code entities that implement the asynchronous data flow.

**Diagram: System Component Interaction**
```mermaid
graph TD
    subgraph "Control Plane"
        [RolloutController] -- "dispatch prompts" --> [InferenceEngine]
        [RolloutController] -- "request reward" --> [RewardService]
    end

    subgraph "Data Plane"
        [InferenceEngine] -- "trajectories (RTensor)" --> [DataController]
        [RewardService] -- "scores" --> [DataController]
        [DataController] -- "shuffled batches" --> [TrainEngine]
    end

    subgraph "Synchronization"
        [TrainEngine] -- "WeightUpdateMeta" --> [InferenceEngine]
    end

    [InferenceEngine] --> |"SGLang/vLLM"| [Rollout_Worker_Proc]
    [TrainEngine] --> |"FSDP2/MCore"| [Trainer_Worker_Proc]
    [DataController] --> |"RDataset"| [Shared_Replay_Buffer]
```
Sources: [blog/AReaL_v0_3.md:85-87](), [areal/api/cli_args.py:417-453](), [areal/infra/dist_rollout.py:1-20]()

## Subsystem Interaction Map

The architecture relies on several underlying infrastructure layers to handle the complexities of distributed execution.

| Subsystem | Responsibility | Key Code Entities |
| :--- | :--- | :--- |
| **Configuration** | Centralized experiment and hardware specs. | `TrainEngineConfig`, `PPOActorConfig` |
| **Distributed** | Process lifecycle and RPC management. | `Scheduler`, `RPCGuard`, `LocalScheduler` |
| **Data Service** | High-speed tensor movement (RTensor). | `DataWorker`, `Router`, `Gateway` |
| **Engines** | Compute-heavy training/inference logic. | `FSDPEngine`, `MegatronEngine`, `ArchonEngine` |

**Diagram: Infrastructure to Code Mapping**
```mermaid
graph LR
    subgraph "areal.infra"
        [Scheduler] --> [LocalScheduler]
        [Scheduler] --> [RayScheduler]
        [Scheduler] --> [SlurmScheduler]
    end

    subgraph "areal.api.cli_args"
        [Config] --> [TrainEngineConfig]
        [Config] --> [ParallelStrategy]
    end

    subgraph "areal.engine"
        [TrainEngine] --> [FSDPEngine]
        [TrainEngine] --> [MegatronEngine]
        [InferenceEngine] --> [SGLangEngine]
    end

    [LocalScheduler] -- "spawns" --> [FSDPEngine]
    [TrainEngineConfig] -- "configures" --> [TrainEngine]
```
Sources: [areal/api/cli_args.py:300-1000](), [AGENTS.md:58-72](), [CLAUDE.md:10-24]()

## Deep Dives

For detailed technical specifications of the core subsystems, refer to the following child pages:

*   **[Configuration System (cli_args)](#2.1)**: Explains the allocation DSL (e.g., `fsdp:d4t2`) and how YAML configs map to `TrainEngineConfig` and `PPOActorConfig`.
*   **[Distributed Infrastructure (Scheduler & RPC)](#2.2)**: Details the `Scheduler` abstraction for Local, Ray, and Slurm environments, and the `RPC Guard` for worker communication.
*   **[RTensor & Data Service](#2.3)**: Describes the `RTensor` abstraction and the high-performance `DataController` used for moving trajectories between workers.

Sources: [areal/api/cli_args.py:1-100](), [AGENTS.md:109-124]()

---

