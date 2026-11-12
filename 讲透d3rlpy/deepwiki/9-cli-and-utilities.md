<!-- source: DeepWiki mcp.deepwiki.com · repo takuseno/d3rlpy · page 9 CLI and Utilities · fetched 2026-10-30 -->

# CLI and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [d3rlpy/__init__.py](d3rlpy/__init__.py)
- [d3rlpy/cli.py](d3rlpy/cli.py)
- [d3rlpy/dataset/components.py](d3rlpy/dataset/components.py)
- [d3rlpy/dataset/mini_batch.py](d3rlpy/dataset/mini_batch.py)
- [d3rlpy/dataset/transition_pickers.py](d3rlpy/dataset/transition_pickers.py)
- [d3rlpy/datasets.py](d3rlpy/datasets.py)
- [d3rlpy/envs/wrappers.py](d3rlpy/envs/wrappers.py)
- [d3rlpy/ope/torch/fqe_impl.py](d3rlpy/ope/torch/fqe_impl.py)
- [d3rlpy/torch_utility.py](d3rlpy/torch_utility.py)
- [docs/cli.rst](docs/cli.rst)
- [examples/custom_algo.py](examples/custom_algo.py)
- [examples/deepmind_control.py](examples/deepmind_control.py)
- [mypy.ini](mypy.ini)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)
- [tests/algos/qlearning/algo_test.py](tests/algos/qlearning/algo_test.py)
- [tests/dataset/test_components.py](tests/dataset/test_components.py)
- [tests/dataset/test_mini_batch.py](tests/dataset/test_mini_batch.py)
- [tests/dataset/test_transition_pickers.py](tests/dataset/test_transition_pickers.py)
- [tests/test_datasets.py](tests/test_datasets.py)
- [tests/test_torch_utility.py](tests/test_torch_utility.py)
- [tests/testing_utils.py](tests/testing_utils.py)

</details>



This page covers the command-line interface (CLI) tools and utility functions provided by d3rlpy. The CLI enables users to interact with trained models, visualize training metrics, manage datasets, and install optional dependencies without writing Python code. The utilities provide supporting functions for data processing, model export, and package management.

For information about the core algorithm framework, see [Algorithm System](#5). For data processing pipelines, see [Data Management](#6).

## CLI Architecture

The d3rlpy CLI is built using the Click library and provides a unified entry point for various utility functions. The CLI commands are organized around common workflows like plotting metrics, evaluating models, and managing dependencies.

```mermaid
graph TD
    CLI["d3rlpy CLI Entry Point"] --> PLOT["plot command"]
    CLI --> PLOT_ALL["plot-all command"]
    CLI --> STATS["stats command"]
    CLI --> EXPORT["export command"]
    CLI --> RECORD["record command"]
    CLI --> PLAY["play command"]
    CLI --> INSTALL["install command"]
    
    PLOT --> MATPLOTLIB["matplotlib integration"]
    PLOT_ALL --> MATPLOTLIB
    
    EXPORT --> ONNX["ONNX export"]
    EXPORT --> TORCHSCRIPT["TorchScript export"]
    
    RECORD --> VIDEO["Video recording"]
    PLAY --> RENDERING["Real-time rendering"]
    
    INSTALL --> PACKAGES["Package management"]
    
    STATS --> METRICS["Metrics analysis"]
```

**CLI Command Flow**
Sources: [d3rlpy/cli.py:61-402](), [setup.py:51]()

## CLI Entry Point and Command Structure

The CLI is registered as a console script in the package setup and uses Click's group functionality to organize commands.

```mermaid
graph LR
    SETUP["setup.py entry_points"] --> CLI_MODULE["d3rlpy.cli:cli"]
    CLI_MODULE --> CLICK_GROUP["@click.group()"]
    CLICK_GROUP --> COMMANDS["Individual Commands"]
    
    COMMANDS --> PLOT_CMD["plot()"]
    COMMANDS --> EXPORT_CMD["export()"]
    COMMANDS --> RECORD_CMD["record()"]
    COMMANDS --> PLAY_CMD["play()"]
    COMMANDS --> INSTALL_CMD["install()"]
    COMMANDS --> STATS_CMD["stats()"]
    COMMANDS --> PLOT_ALL_CMD["plot_all()"]
```

**CLI Module Structure**
Sources: [setup.py:51](), [d3rlpy/cli.py:61-64]()

The CLI entry point is defined in [setup.py:51]() as `"d3rlpy=d3rlpy.cli:cli"`, which maps the `d3rlpy` command to the `cli` function in [d3rlpy/cli.py:61-64]().

## Plotting and Visualization Commands

The CLI provides comprehensive plotting capabilities for analyzing training metrics and experiment results.

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `plot` | Plot individual metric files | `--window`, `--show-steps`, `--save` |
| `plot-all` | Plot all metrics in a directory | `--title`, `--save` |
| `stats` | Show metric statistics | None |

### Plot Command Implementation

```mermaid
graph TD
    PLOT_CMD["plot command"] --> LOAD_DATA["np.loadtxt()"]
    LOAD_DATA --> MOVING_AVG["_compute_moving_average()"]
    MOVING_AVG --> PLT_SETUP["get_plt()"]
    PLT_SETUP --> SEABORN_CHECK["seaborn style check"]
    PLT_SETUP --> MATPLOTLIB["matplotlib.pyplot"]
    
    MATPLOTLIB --> PLOT_LINES["plt.plot()"]
    PLOT_LINES --> OPTIONS["Apply options"]
    OPTIONS --> XLIM["plt.xlim()"]
    OPTIONS --> YLIM["plt.ylim()"]
    OPTIONS --> TITLE["plt.title()"]
    OPTIONS --> SAVE_OR_SHOW["plt.savefig() or plt.show()"]
```

**Plot Command Flow**
Sources: [d3rlpy/cli.py:72-161](), [d3rlpy/cli.py:38-58]()

The plotting functions use [d3rlpy/cli.py:51-58]() for moving average computation and [d3rlpy/cli.py:38-48]() for matplotlib setup with optional seaborn styling.

## Model Export and Evaluation Commands

These commands enable model deployment and evaluation workflows.

### Export Command

The `export` command converts trained d3rlpy models to inference-ready formats:

```mermaid
graph LR
    EXPORT["export command"] --> LOAD_MODEL["load_learnable()"]
    LOAD_MODEL --> TYPE_CHECK["isinstance(QLearningAlgoBase)"]
    TYPE_CHECK --> SAVE_POLICY["algo.save_policy()"]
    SAVE_POLICY --> FORMATS["ONNX or TorchScript"]
```

**Model Export Flow**
Sources: [d3rlpy/cli.py:213-231]()

### Record and Play Commands

Both commands support model evaluation with different output modes:

```mermaid
graph TD
    EVAL_CMD["record/play commands"] --> ENV_SETUP["Environment Setup"]
    ENV_SETUP --> ENV_ID["--env-id option"]
    ENV_SETUP --> ENV_HEADER["--env-header option"]
    
    ENV_SETUP --> LOAD_MODEL["load_learnable()"]
    LOAD_MODEL --> ALGO_TYPE["Algorithm Type Check"]
    
    ALGO_TYPE --> QLEARNING["QLearningAlgoBase"]
    ALGO_TYPE --> TRANSFORMER["TransformerAlgoBase"]
    
    QLEARNING --> Q_EVAL["evaluate_qlearning_with_environment()"]
    TRANSFORMER --> T_EVAL["evaluate_transformer_with_environment()"]
    
    Q_EVAL --> OUTPUT["Video/Rendering Output"]
    T_EVAL --> OUTPUT
```

**Evaluation Commands Flow**
Sources: [d3rlpy/cli.py:242-351](), [d3rlpy/cli.py:233-240]()

The environment creation function [d3rlpy/cli.py:233-240]() enables flexible environment setup through code execution.

## Package Management Utilities

The `install` command provides streamlined installation of optional dependencies.

```mermaid
graph TD
    INSTALL_CMD["install command"] --> INSTALL_OPTIONS["INSTALL_OPTIONS dict"]
    INSTALL_OPTIONS --> ATARI["atari"]
    INSTALL_OPTIONS --> D4RL_ATARI["d4rl_atari"]
    INSTALL_OPTIONS --> D4RL["d4rl"]
    INSTALL_OPTIONS --> MINARI["minari"]
    INSTALL_OPTIONS --> DM_CONTROL["dm_control"]
    
    ATARI --> PIP_INSTALL["_install_module()"]
    D4RL_ATARI --> PIP_INSTALL
    D4RL --> PIP_INSTALL
    D4RL --> PIP_UNINSTALL["_uninstall_module()"]
    MINARI --> PIP_INSTALL
    DM_CONTROL --> PIP_INSTALL
    
    PIP_INSTALL --> SUBPROCESS["subprocess.run()"]
    PIP_UNINSTALL --> SUBPROCESS
```

**Package Installation Flow**
Sources: [d3rlpy/cli.py:364-402](), [d3rlpy/cli.py:353-362]()

The package management system uses [d3rlpy/cli.py:364-370]() to define available packages and their descriptions.

## Dataset Utilities

The dataset utilities provide functions for loading and managing various reinforcement learning datasets.

```mermaid
graph TD
    DATASET_UTILS["d3rlpy.datasets"] --> GET_DATASET["get_dataset()"]
    DATASET_UTILS --> GET_CARTPOLE["get_cartpole()"]
    DATASET_UTILS --> GET_PENDULUM["get_pendulum()"]
    DATASET_UTILS --> GET_ATARI["get_atari()"]
    DATASET_UTILS --> GET_D4RL["get_d4rl()"]
    DATASET_UTILS --> GET_MINARI["get_minari()"]
    
    GET_DATASET --> AUTO_DETECT["Pattern matching"]
    AUTO_DETECT --> CARTPOLE_PATTERNS["cartpole-*"]
    AUTO_DETECT --> PENDULUM_PATTERNS["pendulum-*"]
    AUTO_DETECT --> D4RL_PATTERNS["hopper/halfcheetah/walker/ant"]
    
    GET_ATARI --> D4RL_ATARI["d4rl_atari import"]
    GET_D4RL --> D4RL_LIB["d4rl import"]
    GET_MINARI --> MINARI_LIB["minari import"]
```

**Dataset Loading Architecture**
Sources: [d3rlpy/datasets.py:655-740](), [d3rlpy/datasets.py:35-48]()

The main dataset loading function [d3rlpy/datasets.py:655-740]() provides automatic dataset detection, while specialized loaders handle specific dataset types.

## Torch Utilities

The torch utilities provide essential functions for PyTorch operations and model management.

| Utility Category | Key Functions | Purpose |
|------------------|---------------|---------|
| Model Synchronization | `soft_sync`, `hard_sync` | Target network updates |
| Data Conversion | `convert_to_torch_recursively` | NumPy to PyTorch conversion |
| Batch Processing | `TorchMiniBatch`, `TorchTrajectoryMiniBatch` | Batched data handling |
| Model Management | `Modules`, `Checkpointer` | Model state management |

### Torch Data Processing Pipeline

```mermaid
graph LR
    NUMPY_DATA["NumPy Arrays"] --> CONVERT["convert_to_torch_recursively()"]
    CONVERT --> TORCH_TENSORS["PyTorch Tensors"]
    
    TRANSITIONS["Transitions"] --> TORCH_BATCH["TorchMiniBatch.from_batch()"]
    TRAJECTORIES["Trajectories"] --> TORCH_TRAJ["TorchTrajectoryMiniBatch.from_batch()"]
    
    TORCH_BATCH --> SCALERS["Apply Scalers"]
    TORCH_TRAJ --> SCALERS
    
    SCALERS --> OBS_SCALER["ObservationScaler"]
    SCALERS --> ACT_SCALER["ActionScaler"]
    SCALERS --> REW_SCALER["RewardScaler"]
```

**Torch Data Processing**
Sources: [d3rlpy/torch_utility.py:216-276](), [d3rlpy/torch_utility.py:302-340]()

### Model State Management

```mermaid
graph TD
    MODULES["Modules dataclass"] --> CHECKPOINTER["create_checkpointer()"]
    CHECKPOINTER --> SAVE_STATE["save()"]
    CHECKPOINTER --> LOAD_STATE["load()"]
    
    MODULES --> FREEZE["freeze()"]
    MODULES --> UNFREEZE["unfreeze()"]
    MODULES --> SET_EVAL["set_eval()"]
    MODULES --> SET_TRAIN["set_train()"]
    
    SAVE_STATE --> TORCH_SAVE["torch.save()"]
    LOAD_STATE --> TORCH_LOAD["torch.load()"]
```

**Model Management Utilities**
Sources: [d3rlpy/torch_utility.py:442-484](), [d3rlpy/torch_utility.py:409-440]()

The `Modules` class [d3rlpy/torch_utility.py:442-484]() provides a unified interface for managing PyTorch modules and optimizers, while `Checkpointer` [d3rlpy/torch_utility.py:409-440]() handles serialization.

## Integration with Core Systems

The CLI and utilities integrate closely with d3rlpy's core systems:

```mermaid
graph TD
    CLI_UTILS["CLI & Utilities"] --> ALGORITHMS["Algorithm System"]
    CLI_UTILS --> DATA_MGMT["Data Management"]
    CLI_UTILS --> MODELS["Model Components"]
    
    ALGORITHMS --> LOAD_LEARNABLE["load_learnable()"]
    ALGORITHMS --> ALGO_EVAL["Algorithm Evaluation"]
    
    DATA_MGMT --> DATASET_LOADERS["Dataset Loaders"]
    DATA_MGMT --> REPLAY_BUFFERS["Replay Buffers"]
    
    MODELS --> MODEL_EXPORT["Model Export"]
    MODELS --> POLICY_SAVE["Policy Saving"]
```

**System Integration**
Sources: [d3rlpy/base.py:load_learnable](), [d3rlpy/datasets.py](), [d3rlpy/torch_utility.py]()

The utilities serve as the bridge between the command-line interface and d3rlpy's internal systems, enabling users to access core functionality through simple commands while maintaining the flexibility of the underlying Python API.

---

