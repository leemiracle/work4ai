<!-- source: DeepWiki mcp.deepwiki.com · repo RLinf/RLinf · page 8 RL Algorithms Reference · fetched 2026-10-21 -->

# RL Algorithms Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/agent-e2e-tests.yml](.github/workflows/agent-e2e-tests.yml)
- [rlinf/algorithms/advantages.py](rlinf/algorithms/advantages.py)
- [rlinf/algorithms/losses.py](rlinf/algorithms/losses.py)
- [rlinf/algorithms/registry.py](rlinf/algorithms/registry.py)
- [rlinf/algorithms/utils.py](rlinf/algorithms/utils.py)
- [rlinf/hybrid_engines/megatron/token_dispatcher.py](rlinf/hybrid_engines/megatron/token_dispatcher.py)
- [rlinf/hybrid_engines/megatron/utils.py](rlinf/hybrid_engines/megatron/utils.py)
- [rlinf/runners/agentlightning_runner.py](rlinf/runners/agentlightning_runner.py)
- [rlinf/utils/metric_utils.py](rlinf/utils/metric_utils.py)
- [rlinf/workers/actor/async_ppo_fsdp_worker.py](rlinf/workers/actor/async_ppo_fsdp_worker.py)
- [rlinf/workers/actor/ma_megatron_actor_worker.py](rlinf/workers/actor/ma_megatron_actor_worker.py)
- [rlinf/workers/actor/megatron_actor_worker.py](rlinf/workers/actor/megatron_actor_worker.py)
- [rlinf/workers/agent/agentlightning_rollout_worker.py](rlinf/workers/agent/agentlightning_rollout_worker.py)
- [rlinf/workers/critic/megatron_critic_worker.py](rlinf/workers/critic/megatron_critic_worker.py)
- [rlinf/workers/megatron_worker.py](rlinf/workers/megatron_worker.py)
- [tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml](tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml)

</details>



This page provides a technical reference for the Reinforcement Learning (RL) algorithms implemented in RLinf. It details the mathematical formulations, implementation details for advantage estimation, and policy loss functions.

RLinf separates algorithm logic into two orthogonal axes:
- **`adv_type`**: Controls how advantages (and optionally returns) are computed from rollout rewards.
- **`loss_type`**: Controls the policy gradient objective used in the actor's training step.

## Overview

Algorithm selection is wired through a registry pattern in `rlinf/algorithms/registry.py`. The system dispatches to specific implementations based on the `cfg.algorithm` configuration [rlinf/algorithms/registry.py:19-25](). RLinf supports a wide range of models for both reasoning and embodiment.

| Algorithm | `adv_type` | `loss_type` | Implementation Context |
|:---|:---|:---|:---|
| **PPO** | `gae` | `actor_critic` | Standard actor-critic with GAE [rlinf/algorithms/advantages.py:24-86]() |
| **GRPO** | `grpo` | `actor` | Group-relative reasoning [rlinf/algorithms/advantages.py:89-121]() |
| **REINFORCE++** | `reinpp` | `reinforce` | Single-response PG with KL [rlinf/algorithms/utils.py:217-219]() |
| **SAC / RLPD** | `embodied_sac` | `embodied_sac` | Off-policy ensemble Q-learning [rlinf/algorithms/utils.py:67-131]() |
| **DAPO** | `grpo`/`gae` | `decoupled_actor_critic` | Domain-Adaptive with dual clipping [rlinf/algorithms/losses.py:24-164]() |

### Algorithm Dispatch Architecture

The following diagram illustrates how the `MegatronActor` or `FSDPActor` interacts with the algorithm registry to compute updates.

**Diagram: Registry Dispatch and Data Flow**
```mermaid
graph TD
    subgraph "Registry_Space"
        [rlinf/algorithms/registry.py] --> REG["registry.py"]
        REG --> ADV_REG["register_advantage"]
        REG --> LOSS_REG["register_policy_loss"]
    end

    subgraph "Implementation_Space"
        [rlinf/algorithms/advantages.py] --> ADV["advantages.py"]
        [rlinf/algorithms/utils.py] --> UTILS["utils.py"]
        ADV --> GAE["compute_gae_advantages_and_returns"]
        ADV --> GRPO_ADV["compute_grpo_advantages"]
        UTILS --> REIN_PP["preprocess_reasoning_advantages_inputs"]
        [rlinf/algorithms/losses.py] --> PPO_LOSS["compute_ppo_actor_loss"]
    end

    MA["MegatronActor"] -- "policy_loss()" --> REG
    FA["FSDPActor"] -- "policy_loss()" --> REG
    
    ADV_REG --> GAE
    ADV_REG --> GRPO_ADV
    
    LOSS_REG --> PPO_LOSS

    GAE -.-> ADV
    GRPO_ADV -.-> ADV
    REIN_PP -.-> UTILS
```
Sources: [rlinf/algorithms/registry.py:19-25](), [rlinf/algorithms/advantages.py:24-121](), [rlinf/algorithms/utils.py:177-224](), [rlinf/workers/actor/megatron_actor_worker.py:25-26]()

---

## Advantage Estimation Methods (#8.1)

Advantage estimation converts raw rewards into a signal for policy improvement. RLinf supports several methods tailored for both embodied (step-wise) and reasoning (outcome-based) tasks.

### GAE (Generalized Advantage Estimation)
Used primarily for PPO. It implements the standard GAE recursion to balance bias and variance. If values are `None` (critic-free), it defaults to Monte Carlo returns by setting `gae_lambda=1` and `gamma=1` [rlinf/algorithms/advantages.py:61-64]().

### GRPO (Group Relative Policy Optimization)
Commonly used in reasoning tasks. It computes advantages by normalizing rewards within a group (size defined by `group_size`) generated from the same prompt [rlinf/algorithms/advantages.py:89-121](). 
*   **Dynamic GRPO**: Supports multi-turn scenarios via `grpo_dynamic`, allowing advantage computation per question across multiple trajectories by mapping turn indices to global trajectory indices using `idx_to_traj` [rlinf/algorithms/advantages.py:124-163](). It supports both "trajectory" and "turn" level advantage modes [rlinf/algorithms/advantages.py:130-131]().

### REINFORCE++
A method that uses per-token KL penalties and global advantage normalization. It processes inputs via `preprocess_reasoning_advantages_inputs` where `adv_type` is set to `reinpp` [rlinf/algorithms/utils.py:217-219]().

For implementation details and hyperparameter guidance, see [Advantage Estimation Methods](#8.1).

---

## Policy Loss Functions (#8.2)

Loss functions define the objective for updating the policy network weights. RLinf implements clipped surrogate objectives and KL penalties to ensure stable training.

### KL Penalties
To prevent policy collapse, RLinf supports multiple KL penalty types used across different algorithms [rlinf/algorithms/utils.py:26-64]():
*   **`kl` / `k1`**: Unbiased linear difference of logprobs [rlinf/algorithms/utils.py:41-42]().
*   **`abs`**: Absolute difference of logprobs [rlinf/algorithms/utils.py:44-45]().
*   **`mse` / `k2`**: Quadratic penalty [rlinf/algorithms/utils.py:47-48]().
*   **`low_var_kl` / `k3`**: Schulman's estimator, often used for numerical stability in reasoning tasks [rlinf/algorithms/utils.py:52-58]().

### PPO/GRPO Clipped Loss
Standard clipped surrogate objective implemented in `compute_ppo_actor_loss` [rlinf/algorithms/losses.py:167-183](). It uses `clip_ratio_low` and `clip_ratio_high` to bound the policy update [rlinf/algorithms/losses.py:170-171](). RLinf also supports **Decoupled PPO** (`compute_decoupled_ppo_actor_loss`) which can use a proximal policy anchor for more stable updates in distributed settings [rlinf/algorithms/losses.py:24-42]().

For detailed formulations and entropy bonus configurations, see [Policy Loss Functions](#8.2).

---

## Value and Q-Function Training (#8.3)

Critic training is essential for actor-critic methods and off-policy algorithms.

### Value Estimation
For on-policy methods like PPO, the value function is trained to minimize the MSE between predicted values and GAE returns [rlinf/algorithms/advantages.py:77-79](). Explained variance is tracked as a key diagnostic metric [rlinf/utils/metric_utils.py:173-199]().

### SAC and RLPD
Embodied tasks often use off-policy methods. RLinf supports SAC-style Q-function training.
*   **Huber Loss**: Used for robust error calculation to mitigate the impact of outliers [rlinf/algorithms/utils.py:20-23]().
*   **Advantage Preprocessing**: The `preprocess_embodied_advantages_inputs` function handles the transformation of chunk-level rewards and dones for advantage computation in robotic control [rlinf/algorithms/utils.py:67-131]().

### Reward Functions for Reasoning
RLinf provides specialized reward functions for reasoning tasks. Rollout metrics for dynamic multi-turn scenarios (e.g. Agentic RL) are aggregated at the trajectory level in `compute_rollout_metrics_dynamic` [rlinf/workers/actor/ma_megatron_actor_worker.py:44-50](). This includes turn rewards, trajectory rewards, and advantage statistics.

**Diagram: Algorithm Logic and Code Entity Mapping**
```mermaid
graph LR
    subgraph "Config_Logic"
        [rlinf/workers/actor/megatron_actor_worker.py] --> MA_CODE["MegatronActor"]
        MA_CODE -- "reads" --> ALG["cfg.algorithm"]
        ALG --> ADV_T["adv_type: grpo_dynamic"]
        ALG --> LOSS_T["loss_type: actor"]
    end

    subgraph "Code_Entity_Space"
        [rlinf/algorithms/utils.py] --> UTIL["utils.py"]
        UTIL --> KL_FUNC["kl_penalty"]
        UTIL --> PRE_REASON["preprocess_reasoning_advantages_inputs"]
        UTIL --> SCORE_CALC["calculate_scores"]
        [rlinf/algorithms/advantages.py] --> ADV_CODE["advantages.py"]
        ADV_CODE --> GRPO_DYN["compute_grpo_dynamic_advantages"]
    end

    ALG --> ADV_T
    ADV_T -- "dispatches" --> PRE_REASON
    PRE_REASON -- "calls" --> GRPO_DYN
    GRPO_DYN -- "calls" --> SCORE_CALC
    ALG -- "kl_penalty_type" --> KL_FUNC
    KL_FUNC -.-> UTIL
```
Sources: [rlinf/algorithms/utils.py:26-30](), [rlinf/algorithms/utils.py:134-152](), [rlinf/algorithms/utils.py:177-224](), [rlinf/workers/actor/megatron_actor_worker.py:66-83](), [rlinf/algorithms/advantages.py:124-163]()

For details on critic loss computation, target updates, and Q-head aggregation strategies, see [Value and Q-Function Training](#8.3).

---

