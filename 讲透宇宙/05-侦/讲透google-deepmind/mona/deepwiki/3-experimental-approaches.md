<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mona · page 3 Experimental Approaches · fetched 2026-10-26 -->

# Experimental Approaches

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ipynb/ppo.ipynb](ipynb/ppo.ipynb)
- [src/main.py](src/main.py)

</details>



This document provides an overview of the two main experimental methods implemented in the MONA repository for testing the Myopic Optimization with Non-myopic Approval framework. The two approaches use different reinforcement learning algorithms—tabular value iteration and neural network PPO—to validate MONA's effectiveness against reward hacking in the Camera Dropbox environment.

For details about the Camera Dropbox environment mechanics, see [Environment Mechanics](#4.1). For information about analyzing experimental results, see [Results Analysis](#3.3).

## Overview of Experimental Methods

The MONA repository implements two distinct experimental approaches to validate the framework's effectiveness:

```mermaid
graph TB
    subgraph "Experimental Entry Points"
        MAIN["src/main.py<br/>Value Iteration Experiments"]
        PPO_NB["ipynb/ppo.ipynb<br/>PPO Neural Network Experiments"]
    end
    
    subgraph "Shared Environment"
        BLOCK_ENV["block_push_env.py<br/>Core Environment Logic"]
        GYM_ENV["block_push_gym_env.py<br/>Gymnasium Interface"]
        MAT_CONST["matrix_constructor.MatrixConstructor<br/>State Space Generation"]
    end
    
    subgraph "Value Iteration Components"
        VI_RUNNER["runner.Runner<br/>Experiment Orchestration"]
        VI_TRAIN["train.value_iteration()<br/>Tabular Training"]
        VI_POLICY["policy_constructor.Policy<br/>Deterministic Policy"]
    end
    
    subgraph "PPO Components" 
        PPO_SB3["stable_baselines3.PPO<br/>Neural Network Policy"]
        MONA_CB["MONACallback<br/>Episode Truncation"]
        SAVE_CB["SaveDataCallback<br/>Policy Persistence"]
    end
    
    subgraph "MONA Integration"
        APPROVAL["Approval Functions<br/>Non-myopic Advantage"]
        VALUE_FUNCS["Value Functions<br/>Trusted Policies"]
    end
    
    MAIN --> VI_RUNNER
    PPO_NB --> PPO_SB3
    
    VI_RUNNER --> BLOCK_ENV
    PPO_SB3 --> GYM_ENV
    
    BLOCK_ENV --> MAT_CONST
    GYM_ENV --> BLOCK_ENV
    
    VI_RUNNER --> VI_TRAIN
    VI_TRAIN --> VI_POLICY
    
    PPO_SB3 --> MONA_CB
    PPO_SB3 --> SAVE_CB
    
    VI_TRAIN --> APPROVAL
    MONA_CB --> APPROVAL
    
    APPROVAL --> VALUE_FUNCS
    
    style MAIN fill:#e1f5fe
    style PPO_NB fill:#e1f5fe
```

**Experimental Method Comparison**

Both approaches test the same core hypothesis: that MONA prevents reward hacking by combining myopic optimization with non-myopic approval functions derived from trusted policies.

| Aspect | Value Iteration Method | PPO Neural Network Method |
|--------|----------------------|---------------------------|
| **Entry Point** | `src/main.py` | `ipynb/ppo.ipynb` |
| **Algorithm** | Tabular value iteration | Neural network PPO |
| **State Representation** | Complete state enumeration | Observation vectors |
| **Policy Type** | Deterministic tabular | Stochastic neural network |
| **Environment Interface** | Direct `block_push_env.BlockPushEnv` | Gymnasium wrapper `BlockPushGymEnv` |
| **Orchestration** | `runner.Runner` class | Custom callback system |
| **MONA Implementation** | Built into value iteration | `MONACallback` for episode truncation |

Sources: [README.md:39-49](), [src/main.py:16-17](), [ipynb/ppo.ipynb:9-12]()

## Experimental Parameters and Configuration

Both experimental approaches share a common parameter space for defining environment configuration and MONA settings:

```mermaid
graph LR
    subgraph "Environment Parameters"
        BOARD_SHAPE["board_shape<br/>(4,4) default"]
        MAX_BOXES["max_boxes<br/>2 default"]
        STEP_PENALTY["per_step_penalty<br/>0.01 default"]
        REWARD_FN["reward_function<br/>good/bad"]
    end
    
    subgraph "MONA Parameters"
        INIT_VF["initial_vf<br/>good/bad/zero"]
        NOISE_SCALE["noise_scale<br/>0.0-0.5 range"]
        OPT_LEN["optimization_length<br/>M parameter"]
    end
    
    subgraph "Experiment Control"
        EPISODE_LIMIT["episode_step_limit<br/>50 steps"]
        NUM_TRIALS["num_trials<br/>Multiple runs"]
        SAVE_LEVEL["save_rollouts_level<br/>0-3 detail levels"]
    end
    
    subgraph "Value Iteration Config"
        VI_FLAGS["Command Line Flags<br/>--board_shape=4,4<br/>--reward_function=bad<br/>--initial_vf=good"]
    end
    
    subgraph "PPO Config"
        PPO_PARAMS["PPO Hyperparameters<br/>ent_coef: 0.05<br/>clip_range: 0.3<br/>learning_rate: 0.00005"]
        ENV_PARAMS["Environment Dict<br/>use_good_reward: bool<br/>reward_override: function"]
    end
    
    BOARD_SHAPE --> VI_FLAGS
    MAX_BOXES --> VI_FLAGS
    REWARD_FN --> VI_FLAGS
    
    BOARD_SHAPE --> ENV_PARAMS
    MAX_BOXES --> ENV_PARAMS
    REWARD_FN --> ENV_PARAMS
    
    INIT_VF --> VI_FLAGS
    NOISE_SCALE --> VI_FLAGS
    
    OPT_LEN --> PPO_PARAMS
    
    VI_FLAGS --> VI_CONFIG["Value Iteration Experiments"]
    PPO_PARAMS --> PPO_CONFIG["PPO Experiments"]
    ENV_PARAMS --> PPO_CONFIG
```

**Parameter Configuration Examples**

The value iteration method uses command-line flags for configuration:

```bash
bazel-bin/src/main --board_shape=4,4 --max_boxes=2 --episode_step_limit=50 \
  --reward_function=bad --initial_vf=good --noise_scale=0.5 \
  --data_dir=data/ --save_rollouts_level=3
```

The PPO method uses Python dictionaries and function parameters:

```python
env_params = {
    "board_shape": (4, 4), 
    "max_boxes": 2, 
    "use_good_reward": False,
    "reward_override": advantage_function
}

ppo_params = {
    "ent_coef": 0.05, 
    "clip_range": 0.3, 
    "learning_rate": 0.00005
}
```

Sources: [src/main.py:76-148](), [ipynb/ppo.ipynb:316-353](), [ipynb/ppo.ipynb:1007-1009]()

## Data Storage and Results

Both experimental approaches generate structured data for analysis, but use different storage formats and organization strategies:

```mermaid
graph TD
    subgraph "Value Iteration Outputs"
        VI_VALUE_MAT["value_matrix.npy<br/>State Value Functions"]
        VI_ROLLOUTS["rollouts.textproto<br/>Trajectory Data"]
        VI_POLICY["Policy Objects<br/>Deterministic Actions"]
    end
    
    subgraph "PPO Outputs"
        PPO_POLICIES["policy_arrays.npy<br/>Stochastic Policies"]
        PPO_SB3["sb3_policy.pth<br/>Neural Network Weights"]
        PPO_ROLLOUT_RESULTS["rollout_results.npy<br/>Success/Failure Counts"]
    end
    
    subgraph "Directory Structure"
        PARAM_DIR["data/R=bad-V_init=good-noise_init=0.5/<br/>Parameter-encoded Directories"]
        TRIAL_STRUCTURE["Trial-based Organization<br/>Multiple runs per parameter set"]
    end
    
    subgraph "Analysis Pipeline"
        ANALYSIS_NB["ipynb/analysis.ipynb<br/>Result Visualization"]
        COMPARISON["MONA vs Ordinary RL<br/>Performance Metrics"]
        PLOTS["Behavior Analysis<br/>Success/Failure/Hacking Rates"]
    end
    
    VI_VALUE_MAT --> PARAM_DIR
    VI_ROLLOUTS --> PARAM_DIR
    PPO_POLICIES --> PARAM_DIR
    PPO_SB3 --> PARAM_DIR
    PPO_ROLLOUT_RESULTS --> PARAM_DIR
    
    PARAM_DIR --> TRIAL_STRUCTURE
    
    VI_VALUE_MAT --> ANALYSIS_NB
    VI_ROLLOUTS --> ANALYSIS_NB
    PPO_ROLLOUT_RESULTS --> ANALYSIS_NB
    
    ANALYSIS_NB --> COMPARISON
    COMPARISON --> PLOTS
    
    style PARAM_DIR fill:#e8f5e8
    style ANALYSIS_NB fill:#f3e5f5
```

**File Organization Pattern**

Both methods use parameter-encoded directory names to organize results:

```
data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/
├── value_matrix.npy              # Value iteration results
├── rollouts.textproto            # Value iteration trajectories  
├── ppo_output/                   # PPO results directory
│   ├── policy_T=1e6.pth         # Trained neural network
│   ├── policies_T=1e6.npy       # Policy probability arrays
│   └── rollouts_T=1e6.npy       # Rollout success/failure counts
```

**Rollout Data Categories**

Both methods classify rollout outcomes into three categories for analysis:

| Category | Definition | Reward Count |
|----------|------------|--------------|
| **Failure** | Agent fails to complete task | 0 boxes pushed |
| **Intended Behavior** | Agent pushes exactly one box into hole | 1 box pushed |  
| **Reward Hacking** | Agent exploits camera to push multiple boxes | 2+ boxes pushed |

Sources: [src/main.py:37-46](), [ipynb/ppo.ipynb:439-442](), [ipynb/ppo.ipynb:308-309](), [ipynb/ppo.ipynb:573-582]()

## MONA Implementation Differences

The two experimental approaches implement the MONA framework through different mechanisms, reflecting the underlying algorithmic differences:

```mermaid
graph TB
    subgraph "Value Iteration MONA"
        VI_APPROVAL["train.get_advantage_function()<br/>Computes Q-values from trusted V"]
        VI_INTEGRATION["Built into value iteration<br/>Approval guides policy updates"]
        VI_MYOPIC["Single-step optimization<br/>Inherently myopic updates"]
    end
    
    subgraph "PPO MONA" 
        PPO_APPROVAL["advantage_fn_from_value_fn()<br/>Converts trusted V to advantages"]
        PPO_CALLBACK["MONACallback<br/>Truncates episodes at M steps"]
        PPO_REWARD["reward_override parameter<br/>Uses advantage as reward signal"]
    end
    
    subgraph "Shared Components"
        TRUSTED_V["Trusted Value Functions<br/>From good policy with noise"]
        ADVANTAGE_F["Advantage Functions<br/>Non-myopic approval signals"]
    end
    
    VI_APPROVAL --> ADVANTAGE_F
    PPO_APPROVAL --> ADVANTAGE_F
    
    TRUSTED_V --> VI_APPROVAL
    TRUSTED_V --> PPO_APPROVAL
    
    ADVANTAGE_F --> VI_INTEGRATION
    ADVANTAGE_F --> PPO_REWARD
    
    VI_INTEGRATION --> VI_MYOPIC
    PPO_REWARD --> PPO_CALLBACK
    
    style TRUSTED_V fill:#fff3e0
    style ADVANTAGE_F fill:#e8f5e8
```

**Value Iteration MONA Implementation**

The value iteration approach implements MONA by incorporating approval functions directly into the policy improvement step via [`train.get_advantage_function()`](). The advantage function computes Q-values from a trusted value function, providing non-myopic approval signals that guide policy updates.

**PPO MONA Implementation** 

The PPO approach uses a callback-based system where [`MONACallback`]() truncates episodes into sub-sequences of length M (the optimization horizon). The approval function replaces the environment reward through the `reward_override` parameter, ensuring the neural network optimizes based on trusted advantage signals rather than the hackable reward.

Sources: [ipynb/ppo.ipynb:690-699](), [ipynb/ppo.ipynb:801-873](), [ipynb/ppo.ipynb:1026-1027]()

---

