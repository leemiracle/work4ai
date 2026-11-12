<!-- source: DeepWiki mcp.deepwiki.com · repo PRIME-RL/TTRL · extra page AMC Tasks · fetched 2026-10-30 -->

# AMC Tasks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [verl/examples/ttrl/LLaMA3.1-Instruct/amc.sh](verl/examples/ttrl/LLaMA3.1-Instruct/amc.sh)
- [verl/examples/ttrl/Qwen2.5-Math/amc.sh](verl/examples/ttrl/Qwen2.5-Math/amc.sh)
- [verl/examples/ttrl/Qwen2.5/amc.sh](verl/examples/ttrl/Qwen2.5/amc.sh)

</details>



This page covers configuration and data setup for training TTRL on AMC (American Mathematics Competitions) tasks. AMC represents a specific mathematical reasoning benchmark focused on competition-style problems.

For general task configuration concepts, see [Task Configurations](#3.3). For other mathematical reasoning tasks, see [AIME Tasks](#3.3.1) and [MATH Tasks](#3.3.3). For model-specific configuration details, see [Model Configurations](#3.2).

---

## Overview

AMC (American Mathematics Competitions) is a series of standardized mathematical examinations that test problem-solving abilities in algebra, geometry, number theory, and combinatorics. In the TTRL framework, AMC tasks are configured with the task identifier `"AMC-TTT"` and are available for all three supported model families: Qwen2.5, Qwen2.5-Math, and LLaMA3.1-Instruct.

**Scope of this document:**
- AMC dataset structure and file paths
- Task-specific configuration parameters
- Model-specific script variations for AMC
- Execution procedures for AMC training

---

## Task Identifier and Data Structure

The AMC task uses a consistent identifier and data structure across all model configurations:

| Configuration | Value | Description |
|---------------|-------|-------------|
| Task Identifier | `AMC-TTT` | Task name used in file paths and experiment naming |
| Training Data | `$DATA_LOCAL_DIR/AMC-TTT/train.parquet` | Parquet file containing training problems |
| Validation Data | `$DATA_LOCAL_DIR/AMC-TTT/test.parquet` | Parquet file containing test problems |
| Data Format | Parquet | Preprocessed from JSON using `verl/data/preprocess.py` |

### Data File Paths

```mermaid
graph LR
    DataRoot["DATA_LOCAL_DIR<br/>'path/to/TTRL/verl/data'"]
    TaskDir["AMC-TTT/"]
    TrainFile["train.parquet"]
    TestFile["test.parquet"]
    
    DataRoot --> TaskDir
    TaskDir --> TrainFile
    TaskDir --> TestFile
    
    TrainFile --> Config["data.train_files"]
    TestFile --> Config2["data.val_files"]
```

**Sources:** [verl/examples/ttrl/Qwen2.5-Math/amc.sh:31](), [verl/examples/ttrl/Qwen2.5-Math/amc.sh:44-45]()

The `DATA_LOCAL_DIR` environment variable must be set to point to the directory containing preprocessed AMC data before running training scripts.

---

## Core Configuration Parameters

### Response Length Configuration

All AMC scripts use a parametric response length configuration based on the `K` parameter:

```bash
K=3
MAX_PROMPT_LENGTH=1024
MAX_RESPONSE_LENGTH=$((1024 * $K))  # 3072 tokens
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:15-17]()

The `K` parameter controls the maximum response length in multiples of 1024 tokens. For AMC tasks, `K=3` provides 3072 tokens for the model to generate step-by-step reasoning and final answers.

### TTRL Voting Parameters

AMC tasks use the standard TTRL voting configuration:

| Parameter | Value | Configuration Key |
|-----------|-------|-------------------|
| Votes per Prompt | 64 | `ttrl.n_votes_per_prompt` |
| Samples per Prompt | 32 | `ttrl.n_samples_per_prompt` |
| Validation Samples | 16 | `actor_rollout_ref.rollout.val_kwargs.n` |

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:26-27](), [verl/examples/ttrl/Qwen2.5/amc.sh:74]()

The system generates 32 samples during training and 16 during validation, using 64 votes to determine majority consensus for reward calculation.

### Training Hyperparameters

```mermaid
graph TB
    subgraph Training["Training Configuration"]
        Episodes["EPISODE=30<br/>trainer.total_epochs"]
        BatchSize["DATA_TRAIN_BATCH_SIZE=8<br/>data.train_batch_size"]
        MiniBatch["MINI_BATCH_SIZE=1<br/>actor.ppo_mini_batch_size"]
        MicroBatch["MICRO_BATCH_SIZE=2<br/>ppo_micro_batch_size_per_gpu"]
    end
    
    subgraph Optimization["Optimizer Settings"]
        ActorLR["Actor LR: 5e-7<br/>actor.optim.lr"]
        CriticLR["Critic LR: 9e-6<br/>critic.optim.lr"]
        Warmup["Warmup: 3% cosine<br/>lr_warmup_steps_ratio"]
        KLCoef["KL Coef: 0.00<br/>kl_ctrl.kl_coef"]
    end
    
    subgraph Advantage["Advantage Estimation"]
        GRPO["ADVANTAGE='grpo'<br/>algorithm.adv_estimator"]
    end
    
    Training --> Optimization
    Training --> Advantage
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:24-29](), [verl/examples/ttrl/Qwen2.5/amc.sh:58-59](), [verl/examples/ttrl/Qwen2.5/amc.sh:80](), [verl/examples/ttrl/Qwen2.5/amc.sh:87]()

---

## Model-Specific Variations

### Temperature Configuration Differences

```mermaid
graph TB
    subgraph Qwen25Math["Qwen2.5-Math-1.5B"]
        Math_Train["Training Temperature<br/>rollout.temperature=1.0"]
        Math_Val["Validation Temperature<br/>val_kwargs.temperature=0.6"]
        Math_Prompt["Suffix Prompt<br/>Not configured"]
    end
    
    subgraph Qwen25["Qwen2.5-7B"]
        Q25_Train["Training Temperature<br/>rollout.temperature=0.6"]
        Q25_Val["Validation Temperature<br/>val_kwargs.temperature=0.6"]
        Q25_Prompt["Suffix Prompt<br/>step by step + boxed"]
    end
    
    subgraph LLaMA31["LLaMA3.1-8B-Instruct"]
        LL_Train["Training Temperature<br/>rollout.temperature=0.6"]
        LL_Val["Validation Temperature<br/>val_kwargs.temperature=0.6"]
        LL_Prompt["Suffix Prompt<br/>step by step + boxed"]
    end
```

**Sources:** [verl/examples/ttrl/Qwen2.5-Math/amc.sh:66](), [verl/examples/ttrl/Qwen2.5/amc.sh:67](), [verl/examples/ttrl/LLaMA3.1-Instruct/amc.sh:67]()

#### Qwen2.5-Math-1.5B Configuration

```bash
actor_rollout_ref.rollout.temperature=1.0
actor_rollout_ref.rollout.val_kwargs.temperature=0.6
# No suffix prompt configured
```

**Sources:** [verl/examples/ttrl/Qwen2.5-Math/amc.sh:66](), [verl/examples/ttrl/Qwen2.5-Math/amc.sh:76]()

Qwen2.5-Math uses higher training temperature (1.0) for more diverse exploration but does not include a suffix prompt, relying on its specialized mathematical training.

#### Qwen2.5-7B Configuration

```bash
actor_rollout_ref.rollout.temperature=0.6
+data.suffix_prompt='"\nPlease reason step by step, and put your final answer within \boxed{}."'
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:51](), [verl/examples/ttrl/Qwen2.5/amc.sh:67]()

Qwen2.5 uses a consistent temperature (0.6) and includes an explicit prompt suffix to guide the model's reasoning format.

#### LLaMA3.1-8B-Instruct Configuration

```bash
actor_rollout_ref.rollout.temperature=0.6
+data.suffix_prompt='"\nPlease reason step by step, and put your final answer within \boxed{}."'
```

**Sources:** [verl/examples/ttrl/LLaMA3.1-Instruct/amc.sh:50](), [verl/examples/ttrl/LLaMA3.1-Instruct/amc.sh:67]()

LLaMA3.1 uses identical configuration to Qwen2.5 for AMC tasks.

---

## Script Execution Flow

```mermaid
flowchart TB
    Start["Script Invocation<br/>./amc.sh"]
    
    subgraph EnvSetup["Environment Setup"]
        VLLM["export VLLM_USE_V1=1<br/>unset VLLM_ATTENTION_BACKEND"]
    end
    
    subgraph VarConfig["Variable Configuration"]
        Task["TASK='AMC-TTT'"]
        Backbone["BACKBONE=model_name"]
        Paths["DATA_LOCAL_DIR, BACKBONE_PATH"]
        Params["K, EPISODE, BATCH_SIZE"]
    end
    
    subgraph Execution["Training Execution"]
        MainPPO["python -m verl.trainer.main_ppo"]
        ConfigFile["--config-name='ppo_trainer_ttrl.yaml'"]
        Overrides["Command-line parameter overrides"]
    end
    
    subgraph Outputs["Output Management"]
        OutputDir["OUTPUT_DIR<br/>checkpoints/TTRL-verl/AMC-TTT-{model}/"]
        WandB["WANDB_PROJECT='TTRL-verl'"]
        LogName["LOG_NAME={date}-TTRL-Len@{K}k-{model}"]
    end
    
    Start --> EnvSetup
    EnvSetup --> VarConfig
    VarConfig --> Execution
    Execution --> Outputs
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:1-106]()

### Execution Steps

1. **Environment Configuration** [verl/examples/ttrl/Qwen2.5/amc.sh:2-4]()
   - Enable VLLM v1 engine
   - Clear attention backend to use default

2. **Path Setup** [verl/examples/ttrl/Qwen2.5/amc.sh:31-32]()
   ```bash
   DATA_LOCAL_DIR="path/to/TTRL/verl/data"
   BACKBONE_PATH="path/to/${BACKBONE}"
   ```
   Update these paths to point to your local data directory and model checkpoint.

3. **Launch Training** [verl/examples/ttrl/Qwen2.5/amc.sh:42-104]()
   ```bash
   python -m verl.trainer.main_ppo \
   --config-name='ppo_trainer_ttrl.yaml' \
   data.train_files=["$DATA_LOCAL_DIR/$TASK/train.parquet"] \
   # ... additional overrides
   ```

---

## Complete Configuration Mapping

```mermaid
graph TB
    subgraph DataConfig["Data Configuration"]
        DataTrain["data.train_files<br/>AMC-TTT/train.parquet"]
        DataVal["data.val_files<br/>AMC-TTT/test.parquet"]
        MaxPrompt["data.max_prompt_length<br/>1024"]
        MaxResp["data.max_response_length<br/>3072"]
        FilterLong["data.filter_overlong_prompts<br/>True"]
        Truncation["data.truncation<br/>'error'"]
        SuffixPrompt["data.suffix_prompt<br/>step-by-step instruction"]
    end
    
    subgraph ActorConfig["Actor Configuration"]
        ActorPath["model.path<br/>BACKBONE_PATH"]
        ActorGradCheck["enable_gradient_checkpointing<br/>True"]
        ActorPadding["use_remove_padding<br/>True"]
        ActorMiniBatch["ppo_mini_batch_size<br/>1"]
        ActorMicroBatch["ppo_micro_batch_size_per_gpu<br/>2"]
        ActorLRVal["optim.lr<br/>5e-7"]
        ActorFSDP["fsdp_config.param_offload<br/>False"]
    end
    
    subgraph CriticConfig["Critic Configuration"]
        CriticPath["model.path<br/>BACKBONE_PATH"]
        CriticLRVal["optim.lr<br/>9e-6"]
        CriticGradCheck["enable_gradient_checkpointing<br/>True"]
        CriticFSDP["fsdp_config.param_offload<br/>False"]
    end
    
    subgraph RolloutConfig["Rollout Configuration (VLLM)"]
        RolloutName["name<br/>'vllm'"]
        RolloutTemp["temperature<br/>0.6 or 1.0"]
        RolloutN["n<br/>32"]
        RolloutGPU["gpu_memory_utilization<br/>0.8"]
        RolloutMaxLen["max_model_len<br/>4096"]
    end
    
    subgraph TTRLConfig["TTRL-Specific Configuration"]
        TTRLEnable["ttrl.enable<br/>True"]
        TTRLVotes["ttrl.n_votes_per_prompt<br/>64"]
        TTRLSamples["ttrl.n_samples_per_prompt<br/>32"]
        RewardFunc["custom_reward_function.path<br/>ttrl_math/__init__.py"]
        RewardName["custom_reward_function.name<br/>reward_func"]
    end
    
    subgraph AlgorithmConfig["Algorithm Configuration"]
        AdvEst["adv_estimator<br/>'grpo'"]
        KLCoefVal["kl_ctrl.kl_coef<br/>0.00"]
    end
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:44-93]()

### Critical Configuration Parameters

| Category | Parameter | Value | Line Reference |
|----------|-----------|-------|----------------|
| Task | `TASK` | `"AMC-TTT"` | [verl/examples/ttrl/Qwen2.5/amc.sh:11]() |
| Episodes | `EPISODE` | `30` | [verl/examples/ttrl/Qwen2.5/amc.sh:24]() |
| Response Length | `MAX_RESPONSE_LENGTH` | `3072` (K=3) | [verl/examples/ttrl/Qwen2.5/amc.sh:17]() |
| Actor LR | `actor.optim.lr` | `5e-7` | [verl/examples/ttrl/Qwen2.5/amc.sh:58]() |
| Critic LR | `critic.optim.lr` | `9e-6` | [verl/examples/ttrl/Qwen2.5/amc.sh:80]() |
| TTRL Votes | `ttrl.n_votes_per_prompt` | `64` | [verl/examples/ttrl/Qwen2.5/amc.sh:92]() |
| Reward Function | `custom_reward_function.path` | `./verl/utils/reward_score/ttrl_math/__init__.py` | [verl/examples/ttrl/Qwen2.5/amc.sh:89]() |

---

## Checkpoint and Logging Configuration

### Output Directory Structure

```mermaid
graph TB
    Root["checkpoints/"]
    Project["TTRL-verl/"]
    Model["AMC-TTT-{BACKBONE}/"]
    Date["{DATE}/"]
    Experiment["TTRL-Len@3k-{ADVANTAGE}-{TIME_TAG}/"]
    
    Root --> Project
    Project --> Model
    Model --> Date
    Date --> Experiment
    
    Experiment --> ActorCkpt["Actor checkpoints"]
    Experiment --> CriticCkpt["Critic checkpoints"]
    Experiment --> Logs["Training logs"]
```

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:39](), [verl/examples/ttrl/Qwen2.5/amc.sh:103]()

### Logging Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `trainer.logger` | `['console','wandb']` | Log to console and WandB |
| `trainer.project_name` | `'TTRL-verl'` | WandB project name |
| `trainer.experiment_name` | `{DATE}-TTRL-Len@{K}k-{MODEL}-{ADVANTAGE}` | Unique experiment identifier |
| `trainer.save_freq` | `2000000` | Checkpoint save frequency (effectively disabled) |
| `trainer.test_freq` | `2` | Run validation every 2 epochs |
| `trainer.max_actor_ckpt_to_keep` | `0` | Disable automatic checkpoint cleanup |
| `trainer.max_critic_ckpt_to_keep` | `0` | Disable automatic checkpoint cleanup |

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:94-102]()

---

## Key Differences from Other Tasks

### Comparison with AIME and MATH

| Aspect | AMC | AIME | MATH |
|--------|-----|------|------|
| Task Identifier | `AMC-TTT` | `AIME-TTT` | `MATH-TTT` |
| Problem Difficulty | Intermediate | Advanced | General |
| Response Length (K) | 3 | 3 | 3 |
| Configuration Complexity | Standard | Standard | Standard |
| Suffix Prompt | Model-dependent | Model-dependent | Model-dependent |

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:11]()

All three tasks (AMC, AIME, MATH) share identical TTRL configuration parameters, differing only in the dataset files loaded. This consistency allows for easy comparison of model performance across different mathematical reasoning benchmarks.

---

## Prerequisites and Dependencies

Before running AMC training scripts, ensure:

1. **Data Preparation**: AMC dataset must be preprocessed into Parquet format
   - Training file: `AMC-TTT/train.parquet`
   - Test file: `AMC-TTT/test.parquet`
   - See [Data Processing Pipeline](#4.1) for preprocessing steps

2. **Model Checkpoints**: Pre-trained model must be downloaded
   - Qwen2.5-7B, Qwen2.5-Math-1.5B, or LLaMA3.1-8B-Instruct
   - Update `BACKBONE_PATH` in the script

3. **Environment Variables**:
   - `VLLM_USE_V1=1` (set in script)
   - `VLLM_ATTENTION_BACKEND` (unset in script)

4. **GPU Resources**: 
   - Configuration assumes 8 GPUs per node (`trainer.n_gpus_per_node=8`)
   - Single node setup (`trainer.nnodes=1`)

**Sources:** [verl/examples/ttrl/Qwen2.5/amc.sh:1-4](), [verl/examples/ttrl/Qwen2.5/amc.sh:31-32](), [verl/examples/ttrl/Qwen2.5/amc.sh:97-98]()

---

