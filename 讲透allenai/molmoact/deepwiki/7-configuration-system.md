<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/molmoact · page 7 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiments/LIBERO/libero/configs/config.yaml](experiments/LIBERO/libero/configs/config.yaml)

</details>



## Purpose and Scope

This document describes the hierarchical configuration system used in the LIBERO benchmark framework within MolmoAct. The system is built on [Hydra](https://hydra.cc/), a framework for elegantly configuring complex applications through composable configuration files. This configuration system manages all aspects of LIBERO training and evaluation, including data modalities, policy architectures, lifelong learning algorithms, and training hyperparameters.

For information about the LIBERO benchmark framework architecture, see [LIBERO Benchmark Framework](#6). For details on training and evaluation execution, see [LIBERO Training and Evaluation Scripts](#6.4). For specific policy architecture implementations, see [Policy Architecture Configurations](#7.3).

**Sources:** [experiments/LIBERO/libero/configs/config.yaml]()

---

## Configuration Architecture Overview

The LIBERO configuration system uses a hierarchical structure with six primary configuration layers that compose together to define complete experimental setups. The root configuration file (`config.yaml`) serves as the entry point, importing specialized configuration groups through Hydra's defaults mechanism.

### Configuration File Hierarchy

```mermaid
graph TB
    subgraph "Root Configuration"
        CONFIG["config.yaml<br/>Global defaults + parameters"]
    end
    
    subgraph "Configuration Groups"
        DATA["data/<br/>default.yaml"]
        POLICY["policy/<br/>bc_rnn_policy.yaml<br/>bc_transformer_policy.yaml<br/>bc_vilt_policy.yaml"]
        TRAIN["train/<br/>default.yaml"]
        EVAL["eval/<br/>default.yaml"]
        LIFELONG["lifelong/<br/>base.yaml<br/>sequential.yaml<br/>er.yaml<br/>ewc.yaml<br/>packnet.yaml<br/>multitask.yaml<br/>agem.yaml"]
        TEST["test/<br/>null (optional)"]
    end
    
    subgraph "Parameters by Category"
        GLOBAL_PARAMS["seed<br/>use_wandb<br/>wandb_project<br/>device<br/>task_embedding_format<br/>benchmark_name"]
        DATA_PARAMS["modalities<br/>obs_keys<br/>seq_length<br/>action_scale"]
        POLICY_PARAMS["policy_class<br/>architecture params<br/>encoder settings"]
        TRAIN_PARAMS["epochs<br/>batch_size<br/>learning_rate<br/>optimizer"]
        EVAL_PARAMS["n_eval<br/>eval_every_n_steps<br/>num_procs"]
        LIFELONG_PARAMS["algorithm<br/>buffer_size<br/>task_order"]
    end
    
    CONFIG --> DATA
    CONFIG --> POLICY
    CONFIG --> TRAIN
    CONFIG --> EVAL
    CONFIG --> LIFELONG
    CONFIG --> TEST
    
    CONFIG -.contains.-> GLOBAL_PARAMS
    DATA -.contains.-> DATA_PARAMS
    POLICY -.contains.-> POLICY_PARAMS
    TRAIN -.contains.-> TRAIN_PARAMS
    EVAL -.contains.-> EVAL_PARAMS
    LIFELONG -.contains.-> LIFELONG_PARAMS
```

**Sources:** [experiments/LIBERO/libero/configs/config.yaml:1-25](), [experiments/LIBERO/README.md]()

---

## Hydra Defaults Composition System

The configuration system uses Hydra's defaults list to compose configurations from multiple sources. The root configuration file defines the composition order and default selections for each configuration group.

```mermaid
graph LR
    subgraph "Defaults List Processing"
        SELF["_self_<br/>(process own params last)"]
        DATA_DEFAULT["data: default"]
        POLICY_DEFAULT["policy: bc_transformer_policy"]
        TRAIN_DEFAULT["train: default"]
        EVAL_DEFAULT["eval: default"]
        LIFELONG_DEFAULT["lifelong: base"]
        TEST_DEFAULT["test: null"]
    end
    
    subgraph "Resolution Order"
        ORDER["1. Load group configs<br/>2. Apply _self_ (root params)<br/>3. Apply CLI overrides"]
    end
    
    subgraph "Override Examples"
        CLI_POLICY["CLI: policy=bc_rnn_policy"]
        CLI_LIFELONG["CLI: lifelong=er"]
        CLI_BENCH["CLI: benchmark_name=LIBERO_OBJECT"]
        CLI_SEED["CLI: seed=42"]
    end
    
    DATA_DEFAULT --> ORDER
    POLICY_DEFAULT --> ORDER
    TRAIN_DEFAULT --> ORDER
    EVAL_DEFAULT --> ORDER
    LIFELONG_DEFAULT --> ORDER
    TEST_DEFAULT --> ORDER
    SELF --> ORDER
    
    ORDER --> CLI_POLICY
    ORDER --> CLI_LIFELONG
    ORDER --> CLI_BENCH
    ORDER --> CLI_SEED
```

The `_self_` entry in the defaults list ([config.yaml:4]()) ensures that parameters defined directly in `config.yaml` are processed after group defaults, allowing them to override group-level settings. This is critical for maintaining global parameters like `seed`, `device`, and `benchmark_name` regardless of which policy or lifelong learning algorithm is selected.

**Sources:** [experiments/LIBERO/libero/configs/config.yaml:3-10]()

---

## Configuration Layer Summary

The following table summarizes the six configuration layers, their purposes, and key parameters:

| Layer | File Location | Purpose | Key Parameters |
|-------|--------------|---------|----------------|
| **Global** | `config.yaml` | Root configuration with experiment-level settings | `seed`, `use_wandb`, `device`, `task_embedding_format`, `benchmark_name` |
| **Data** | `data/default.yaml` | Data modalities and observation specifications | `modalities`, `obs_keys`, `seq_length`, `frame_stack`, `action_scale` |
| **Policy** | `policy/*.yaml` | Neural network architecture definitions | `policy_class`, encoder configs, head configs, architecture-specific params |
| **Training** | `train/default.yaml` | Training loop hyperparameters | `epochs`, `batch_size`, `lr`, `optimizer`, `scheduler`, `grad_norm` |
| **Evaluation** | `eval/default.yaml` | Evaluation execution parameters | `n_eval`, `eval_every_n_steps`, `num_procs`, `max_steps` |
| **Lifelong** | `lifelong/*.yaml` | Lifelong learning algorithm settings | `algo_name`, `n_tasks`, `task_order_index`, buffer/regularization params |

**Sources:** [experiments/LIBERO/libero/configs/config.yaml](), [experiments/LIBERO/README.md]()

---

## Global Configuration Parameters

The root configuration file defines experiment-wide parameters that apply regardless of the specific data, policy, or algorithm configuration. These parameters are located in [experiments/LIBERO/libero/configs/config.yaml:12-25]().

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `seed` | int | 10000 | Random seed for reproducibility across PyTorch, NumPy, and Python |
| `use_wandb` | bool | false | Enable Weights & Biases experiment tracking |
| `wandb_project` | str | "lifelong learning" | W&B project name for experiment organization |
| `device` | str | "cuda" | Compute device: "cuda" or "cpu" |
| `benchmark_name` | str | "LIBERO_SPATIAL" | Task suite selection: LIBERO_SPATIAL, LIBERO_OBJECT, LIBERO_GOAL, LIBERO_10, LIBERO_90 |

### Path Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder` | str/null | null | Custom experiment output directory (uses default if null) |
| `bddl_folder` | str/null | null | Custom BDDL task definition directory (uses default if null) |
| `init_states_folder` | str/null | null | Custom initial states directory (uses default if null) |

### Task Embedding Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_embedding_format` | str | "bert" | Task embedding method: "bert" for learned embeddings or "one_hot" for discrete encoding |
| `task_embedding_one_hot_offset` | int | 1 | Offset for one-hot task embeddings (starts at task ID 1 instead of 0) |

### Model Loading

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `load_previous_model` | bool | false | Load checkpoint from previous task for continual learning scenarios |
| `pretrain` | bool | false | Use pretrained model initialization |
| `pretrain_model_path` | str | "" | Path to pretrained checkpoint file |

**Sources:** [experiments/LIBERO/libero/configs/config.yaml:12-25]()

---

## Configuration File to Code Entity Mapping

This diagram shows how configuration files map to Python classes and functions that consume them:

```mermaid
graph TB
    subgraph "Configuration Files"
        CONFIG_YAML["config.yaml"]
        DATA_YAML["data/default.yaml"]
        POLICY_YAML["policy/bc_transformer_policy.yaml"]
        TRAIN_YAML["train/default.yaml"]
        EVAL_YAML["eval/default.yaml"]
        LIFELONG_YAML["lifelong/base.yaml"]
    end
    
    subgraph "Python Entrypoints"
        MAIN_PY["libero/lifelong/main.py<br/>train_sequential()"]
        EVAL_PY["libero/lifelong/evaluate.py<br/>main()"]
    end
    
    subgraph "Configuration Consumers"
        HYDRA_MAIN["@hydra.main<br/>config_path='configs'<br/>config_name='config'"]
        CFG_OBJECT["cfg: DictConfig<br/>OmegaConf object"]
    end
    
    subgraph "Usage Sites"
        SEED["torch.manual_seed(cfg.seed)<br/>np.random.seed(cfg.seed)"]
        BENCHMARK["get_benchmark_dict(cfg.benchmark_name)"]
        DEVICE["device = cfg.device"]
        POLICY_INIT["policy = policy_cls(cfg)"]
        TRAINER["Trainer(cfg)"]
        DATASET["get_dataset(cfg.data)"]
        ALGO["get_algo(cfg.lifelong)"]
    end
    
    CONFIG_YAML --> HYDRA_MAIN
    DATA_YAML --> HYDRA_MAIN
    POLICY_YAML --> HYDRA_MAIN
    TRAIN_YAML --> HYDRA_MAIN
    EVAL_YAML --> HYDRA_MAIN
    LIFELONG_YAML --> HYDRA_MAIN
    
    HYDRA_MAIN --> CFG_OBJECT
    CFG_OBJECT --> MAIN_PY
    CFG_OBJECT --> EVAL_PY
    
    MAIN_PY --> SEED
    MAIN_PY --> BENCHMARK
    MAIN_PY --> DEVICE
    MAIN_PY --> POLICY_INIT
    MAIN_PY --> TRAINER
    MAIN_PY --> DATASET
    MAIN_PY --> ALGO
    
    EVAL_PY --> BENCHMARK
    EVAL_PY --> DEVICE
    EVAL_PY --> POLICY_INIT
```

The configuration files are loaded by Hydra decorators in the main entry points. For training, [libero/lifelong/main.py]() uses the `@hydra.main` decorator to load the configuration. For evaluation, [libero/lifelong/evaluate.py]() similarly loads the composed configuration. The resulting `cfg` object (an OmegaConf `DictConfig`) is then passed to various components for initialization.

**Sources:** [experiments/LIBERO/libero/configs/config.yaml](), [experiments/LIBERO/README.md]()

---

## Configuration Override Patterns

Hydra supports command-line overrides of any configuration parameter. This enables flexible experimentation without modifying configuration files.

### Common Override Examples

```bash
# Change policy architecture
python main.py policy=bc_rnn_policy

# Select different lifelong learning algorithm
python main.py lifelong=er lifelong.buffer_size=5000

# Change benchmark and seed
python main.py benchmark_name=LIBERO_OBJECT seed=42

# Override nested parameters
python main.py train.batch_size=64 train.lr=0.001

# Enable W&B tracking
python main.py use_wandb=true wandb_project="my_experiment"

# Combine multiple overrides
python main.py policy=bc_vilt_policy lifelong=ewc benchmark_name=LIBERO_GOAL seed=123
```

### Override Precedence

The configuration resolution order follows this precedence (highest to lowest):

1. **Command-line overrides** (highest priority)
2. **Root config parameters** (from `config.yaml` after `_self_`)
3. **Group config defaults** (from `data/`, `policy/`, etc.)
4. **Schema defaults** (lowest priority)

This precedence allows CLI overrides to take precedence over all configuration file settings, enabling rapid experimentation.

**Sources:** [experiments/LIBERO/libero/configs/config.yaml:3-10]()

---

## Configuration Validation

While the provided files do not show explicit schema validation, the configuration system relies on:

1. **Hydra's structured configs**: Type checking through OmegaConf
2. **Required parameters**: Missing required parameters cause immediate failures at startup
3. **Default values**: All configuration files provide sensible defaults
4. **Benchmark validation**: The `benchmark_name` parameter is validated against available task suites through `get_benchmark_dict()`

The configuration loading occurs before any training or evaluation begins, ensuring early detection of configuration errors.

**Sources:** [experiments/LIBERO/libero/configs/config.yaml]()

---

## Related Configuration Systems

While this page focuses on the LIBERO configuration system within MolmoAct, note that:

- **MolmoAct training pipeline** (see [Training Pipeline](#2)) uses its own training scripts with different configuration mechanisms
- **SimplerEnv evaluation** (see [SimplerEnv Evaluation](#5.1)) uses command-line arguments rather than Hydra configs
- **LIBERO-specific configurations** only apply to experiments within the `experiments/LIBERO/` directory

The LIBERO configuration system is self-contained and does not interact with the main MolmoAct training configuration, as LIBERO serves primarily as a benchmark and evaluation framework.

**Sources:** [experiments/LIBERO/libero/configs/config.yaml](), [experiments/LIBERO/README.md]()

---

