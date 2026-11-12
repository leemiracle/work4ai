<!-- source: DeepWiki mcp.deepwiki.com · repo radixark/miles · page 6 Training Features · fetched 2026-10-21 -->

# Training Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [miles/backends/megatron_utils/arguments.py](miles/backends/megatron_utils/arguments.py)
- [tests/fast/backends/training_utils/loss/loss_test_utils.py](tests/fast/backends/training_utils/loss/loss_test_utils.py)
- [tests/fast/backends/training_utils/loss/test_advantages_pp_stage_guard.py](tests/fast/backends/training_utils/loss/test_advantages_pp_stage_guard.py)
- [tests/fast/backends/training_utils/loss/test_opd.py](tests/fast/backends/training_utils/loss/test_opd.py)
- [tests/fast/backends/training_utils/loss/test_training_logprob_reuse.py](tests/fast/backends/training_utils/loss/test_training_logprob_reuse.py)
- [tests/fast/backends/training_utils/test_chunked_log_probs.py](tests/fast/backends/training_utils/test_chunked_log_probs.py)
- [tests/fast/backends/training_utils/test_sampling_mask.py](tests/fast/backends/training_utils/test_sampling_mask.py)
- [tests/fast/backends/training_utils/test_true_on_policy_loss_metrics.py](tests/fast/backends/training_utils/test_true_on_policy_loss_metrics.py)

</details>



## Purpose and Scope

This document provides a high-level overview of Miles' core training features, orchestrating the reinforcement learning training lifecycle from data ingestion to gradient updates and weight synchronization. As a PARENT page, this section introduces the fundamental building blocks of the training infrastructure and links to specialized child pages for deep technical details.

For distributed training backend mechanics, see [FSDP Backend](#4.1) and [Megatron Backend](#4.2). For train-inference alignment strategies, see [Train-Inference Alignment](#7).

```mermaid
graph TB
    Start[""Training Orchestration train.py""]
    Rollout[""Rollout Generation RolloutManager""]
    Data[""Data Processing Pipeline DataIterator""]
    Train[""Model Training TrainRayActor""]
    Sync[""Weight Synchronization update_weights()""]
    
    Start --> Rollout
    Rollout --> Data
    Data --> Train
    Train --> Sync
    Sync --> Rollout
```
Sources: [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114](), [miles/backends/megatron_utils/arguments.py:16-65]()

---

## 6.1. RL Algorithms

Miles supports multiple advanced reinforcement learning algorithms and advantage estimators, including Proximal Policy Optimization (PPO), Group Relative Policy Optimization (GRPO), and Group-based Scaled Policy Optimization (GSPO) [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114, tests/fast/backends/training_utils/loss/test_training_logprob_reuse.py:56-63](). These estimators operate on response-aligned log-probabilities, reference KL divergences, and masked advantages. Orthogonal enhancements such as On-Policy Distillation (OPD) and advantage normalization are applied directly within the loss computation pipeline [tests/fast/backends/training_utils/loss/test_opd.py:24-48]().

For detailed documentation on loss formulations, advantage estimation math, and hyperparameter configuration, see [RL Algorithms](#6.1).

Sources: [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114](), [tests/fast/backends/training_utils/loss/test_opd.py:24-48](), [tests/fast/backends/training_utils/loss/test_training_logprob_reuse.py:56-63]()

---

## 6.2. Weight Synchronization

To keep inference engines aligned with newly updated model parameters during iterative RL, Miles implements robust weight update protocols. These include zero-copy shared memory updates, peer-to-peer transfers, disk-delta syncing, and integration with HuggingFace weight iterators. Update timing and propagation strategies ensure minimal blocking overhead across distributed Ray actors.

For a comprehensive explanation of weight update topologies and protocols, see [Weight Synchronization](#6.2).

Sources: [miles/backends/megatron_utils/arguments.py:16-65]()

---

## 6.3. Memory Management

Training large language models alongside high-throughput inference engines requires aggressive memory management. Miles incorporates tensor offloading strategies, CPU tensor backers, disk offload layers, and flexible colocation modes to swap model weights between memory spaces during the rollout and training phases.

For details on memory partitioning and offload configurations, see [Memory Management](#6.3).

Sources: [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114]()

---

## 6.4. Data Processing Pipeline

The data processing pipeline ingests raw rollout trajectories, performs dynamic batch sizing and sequence-length balancing, applies filtering and over-sampling rules, and converts samples into context-parallel (CP) ready training micro-batches [tests/fast/backends/training_utils/test_sampling_mask.py:13-24](). This ensures optimized memory layouts for both `thd` and `bshd` tensor formats.

For details on dataset preparation, padding heuristics, and sampling logic, see [Data Processing Pipeline](#6.4).

Sources: [tests/fast/backends/training_utils/test_sampling_mask.py:13-24]()

---

## 6.5. Metrics and Logging

Experiment tracking and metric collection are unified across distributed training and rollout workers. Miles integrates with platforms such as Weights & Biases (W&B), MLflow, TensorBoard, and Prometheus. Per-rank metrics are gathered and reduced on source data-parallel ranks, while continuous checkers evaluate generation quality and training stability.

For information on metric collection APIs and experiment trackers, see [Metrics and Logging](#6.5).

Sources: [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114]()

---

## 6.6. Debug Dashboard and Data Dumping

Miles provides a dedicated debugging ecosystem centered around the `miles/dashboard` web application. This application includes a centralized store, backend server, React hooks, and static JavaScript views that consume structured training and rollout diagnostic dumps to inspect generation artifacts, reward distributions, and step-level metrics.

For architectural details on the dashboard server, store layout, and data dumping utilities, see [Debug Dashboard and Data Dumping](#6.6).

Sources: [tests/fast/backends/training_utils/loss/loss_test_utils.py:69-114]()

---

