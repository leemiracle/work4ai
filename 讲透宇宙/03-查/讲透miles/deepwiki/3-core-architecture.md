<!-- source: DeepWiki mcp.deepwiki.com · repo radixark/miles · page 3 Core Architecture · fetched 2026-10-21 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [miles/ray/placement_group.py](miles/ray/placement_group.py)
- [miles/ray/specs/entrypoint.py](miles/ray/specs/entrypoint.py)
- [miles/ray/specs/train.py](miles/ray/specs/train.py)
- [miles/utils/audit_utils/process_identity.py](miles/utils/audit_utils/process_identity.py)
- [miles/utils/hot_restart.py](miles/utils/hot_restart.py)
- [tests/fast/ray/rollout/test_rollout_executor_init.py](tests/fast/ray/rollout/test_rollout_executor_init.py)
- [tests/fast/ray/specs/test_entrypoint.py](tests/fast/ray/specs/test_entrypoint.py)
- [tests/fast/ray/specs/test_train.py](tests/fast/ray/specs/test_train.py)
- [tests/fast/ray/test_cell_meta.py](tests/fast/ray/test_cell_meta.py)
- [tests/fast/ray/test_placement_group.py](tests/fast/ray/test_placement_group.py)
- [tests/fast/ray/test_placement_group_shared_ppo.py](tests/fast/ray/test_placement_group_shared_ppo.py)
- [tests/fast/utils/test_hot_restart.py](tests/fast/utils/test_hot_restart.py)
- [tests/fast/utils/test_process_identity.py](tests/fast/utils/test_process_identity.py)

</details>



This document explains Miles' high-level system architecture and design principles, focusing on the separation of training and inference engines, Ray-based orchestration, and distributed communication infrastructure. As a parent page, this overview provides a high-level conceptual summary of the system and links to detailed child pages for each architectural subsystem.

For detailed technical documentation, see the child pages:
- [System Design and Components](#3.1) — Detailed separation of training and inference and component interaction
- [Training Orchestration](#3.2) — Entry points (`train.py`, `train_async.py`), sync/async modes, and `TrainerController`
- [Rollout Generation System](#3.3) — `InferenceController`, `RolloutServer`, `ServerCell`, and data flow
- [Ray Resource Management](#3.4) — Placement groups, resource allocation strategies, and distributed execution
- [Worker Management and RPC Infrastructure](#3.5) — `RayWorkerManager`, worker specs, pools/cells, and RPC client/server layers

---

## High-Level System Overview

Miles is designed as an enterprise-grade reinforcement learning post-training framework that couples distributed model training backends (such as Megatron-LM and FSDP2) with high-throughput inference engines (`SGLang`) via Ray [miles/ray/placement_group.py:146-163](). The architecture decouples policy-updating training actors from rollout generation workers to optimize hardware utilization and avoid memory contention.

Title: Miles Core System Architecture
```mermaid
graph TB
    subgraph "Driver"
        DriverEntryPoint["train.py / train_async.py"]
    end

    subgraph "Control Plane & Orchestration"
        WorkerManager["RayWorkerManager<br/>miles/ray/wiring.py"]
        InferenceCtrl["InferenceController<br/>miles/ray/rollout/inference_controller.py"]
        TrainerCtrl["TrainerController<br/>miles/ray/train/group.py"]
        RolloutExec["RolloutExecutor<br/>miles/ray/rollout/rollout_executor.py"]
    end

    subgraph "Data & Compute Workers"
        TrainActor["MegatronTrainRayActor / FSDPTrainRayActor<br/>miles/ray/specs/train.py"]
        EngineCell["ServerCell / SGLang Engine<br/>miles/ray/specs/inference.py"]
    end

    DriverEntryPoint --> WorkerManager
    WorkerManager --> InferenceCtrl
    WorkerManager --> TrainerCtrl
    InferenceCtrl --> EngineCell
    TrainerCtrl --> TrainActor
    RolloutExec --> InferenceCtrl

    Sources: [miles/ray/placement_group.py:146-163](), [miles/ray/specs/train.py:40-46]()
```

Sources: [miles/ray/placement_group.py:146-163](), [miles/ray/specs/train.py:40-46]()

---

## 3.1. System Design and Components

The Miles architecture isolates training computation from inference generation. Training actors run state-intensive gradient updates utilizing Megatron-LM or FSDP backends, while inference requests are channeled through SGLang-based worker cells [miles/ray/specs/train.py:40-46](). 

For full details on component separation, cluster topology, and interactions, see [System Design and Components](#3.1).

Sources: [miles/ray/specs/train.py:40-46]()

---

## 3.2. Training Orchestration

Training execution is driven by entry points that manage the lifecycle of rollouts, training steps, evaluation dispatches, and periodic checkpoint saving. The system abstracts distributed groups via `TrainerController` and `TrainerCell` handles [miles/ray/specs/train.py:40-114]().

For details on the main training loop, synchronous vs. asynchronous modes, and state transitions, see [Training Orchestration](#3.2).

Sources: [miles/ray/specs/train.py:40-114]()

---

## 3.3. Rollout Generation System

Rollout generation is managed through the `InferenceController`, `RolloutServer`, and `ServerCell` abstraction stack, coordinated alongside the `RolloutExecutor` [miles/ray/placement_group.py:12-19](). Prompts are transformed into training-ready trajectory batches complete with log probabilities, advantages, and rewards.

For details on generation pipelines, sample processing, and data flow from prompts to training datasets, see [Rollout Generation System](#3.3).

Sources: [miles/ray/placement_group.py:12-19]()

---

## 3.4. Ray Resource Management

Ray placement groups govern strict physical hardware layout, bundle creation, and device allocation via `_create_placement_group()` and `_get_placement_group_layout()` [miles/ray/placement_group.py:81-139](). Miles queries physical node topology using helper actors (`InfoActor`) to enforce deterministic bundle sorting and scheduling strategies (`PACK`) across nodes and GPUs [miles/ray/placement_group.py:48-118]().

Title: Placement Group Resource Allocation Flow
```mermaid
graph LR
    Args["args: Namespace"] --> GetLayout["_get_placement_group_layout<br/>miles/ray/placement_group.py:122"]
    GetLayout --> CreatePG["_create_placement_group<br/>miles/ray/placement_group.py:81"]
    CreatePG --> InfoActor["InfoActor.options(...)<br/>miles/ray/placement_group.py:95"]
    InfoActor --> SortBundles["sort_key & Reordering<br/>miles/ray/placement_group.py:54-72"]
    SortBundles --> PGInfo["PlacementGroupInfo<br/>miles/ray/placement_group.py:75-79"]

    Sources: [miles/ray/placement_group.py:48-139]()
```

For details on placement groups, resource allocation strategies, and distributed execution topologies, see [Ray Resource Management](#3.4).

Sources: [miles/ray/placement_group.py:48-139]()

---

## 3.5. Worker Management and Infrastructure

Worker lifecycle management, port/address allocation, and RPC communication layers are structured around worker specifications (`ServeWorkerSpec`) and entrypoint calculations (`compute_specs`) [miles/ray/specs/entrypoint.py:8-23](). This layer handles cross-actor RPC channels, context locking utilities, and process grouping [miles/utils/audit_utils/process_identity.py:9-52]().

For details on worker specs, pools, cell structures, port allocation, and RPC clients/servers, see [Worker Management and RPC Infrastructure](#3.5).

Sources: [miles/ray/specs/entrypoint.py:8-23](), [miles/utils/audit_utils/process_identity.py:9-52]()

---

