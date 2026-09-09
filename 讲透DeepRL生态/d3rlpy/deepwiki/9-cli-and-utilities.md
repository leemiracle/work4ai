> 来源: [https://deepwiki.com/takuseno/d3rlpy/9-cli-and-utilities](https://deepwiki.com/takuseno/d3rlpy/9-cli-and-utilities)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# CLI and Utilities

  Relevant source files 
 - [d3rlpy/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py)
 - [d3rlpy/cli.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py)
 - [d3rlpy/dataset/components.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/components.py)
 - [d3rlpy/dataset/mini_batch.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/mini_batch.py)
 - [d3rlpy/dataset/transition_pickers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/dataset/transition_pickers.py)
 - [d3rlpy/datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py)
 - [d3rlpy/envs/wrappers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/envs/wrappers.py)
 - [d3rlpy/ope/torch/fqe_impl.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/ope/torch/fqe_impl.py)
 - [d3rlpy/torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py)
 - [docs/cli.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/cli.rst)
 - [examples/custom_algo.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/custom_algo.py)
 - [examples/deepmind_control.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/deepmind_control.py)
 - [mypy.ini](https://github.com/takuseno/d3rlpy/blob/4f0956ba/mypy.ini)
 - [requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/requirements.txt)
 - [setup.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py)
 - [tests/algos/qlearning/algo_test.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/algos/qlearning/algo_test.py)
 - [tests/dataset/test_components.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_components.py)
 - [tests/dataset/test_mini_batch.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_mini_batch.py)
 - [tests/dataset/test_transition_pickers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/dataset/test_transition_pickers.py)
 - [tests/test_datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/test_datasets.py)
 - [tests/test_torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/test_torch_utility.py)
 - [tests/testing_utils.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/testing_utils.py)
 
  This page covers the command-line interface (CLI) tools and utility functions provided by d3rlpy. The CLI enables users to interact with trained models, visualize training metrics, manage datasets, and install optional dependencies without writing Python code. The utilities provide supporting functions for data processing, model export, and package management.

 For information about the core algorithm framework, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For data processing pipelines, see [Data Management](https://deepwiki.com/takuseno/d3rlpy/6-data-management).

 
## CLI Architecture

 The d3rlpy CLI is built using the Click library and provides a unified entry point for various utility functions. The CLI commands are organized around common workflows like plotting metrics, evaluating models, and managing dependencies.

 
```

```

 **CLI Command Flow** Sources: [d3rlpy/cli.py61-402](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L61-L402) [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51)

 
## CLI Entry Point and Command Structure

 The CLI is registered as a console script in the package setup and uses Click's group functionality to organize commands.

 
```

```

 **CLI Module Structure** Sources: [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51) [d3rlpy/cli.py61-64](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L61-L64)

 The CLI entry point is defined in [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51) as `"d3rlpy=d3rlpy.cli:cli"`, which maps the `d3rlpy` command to the `cli` function in [d3rlpy/cli.py61-64](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L61-L64)

 
## Plotting and Visualization Commands

 The CLI provides comprehensive plotting capabilities for analyzing training metrics and experiment results.

 
| Command | Purpose | Key Options |
|---|---|---|
| plot | Plot individual metric files | --window, --show-steps, --save |
| plot-all | Plot all metrics in a directory | --title, --save |
| stats | Show metric statistics | None |

 
### Plot Command Implementation

 
```

```

 **Plot Command Flow** Sources: [d3rlpy/cli.py72-161](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L72-L161) [d3rlpy/cli.py38-58](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L38-L58)

 The plotting functions use [d3rlpy/cli.py51-58](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L51-L58) for moving average computation and [d3rlpy/cli.py38-48](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L38-L48) for matplotlib setup with optional seaborn styling.

 
## Model Export and Evaluation Commands

 These commands enable model deployment and evaluation workflows.

 
### Export Command

 The `export` command converts trained d3rlpy models to inference-ready formats:

 
```

```

 **Model Export Flow** Sources: [d3rlpy/cli.py213-231](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L213-L231)

 
### Record and Play Commands

 Both commands support model evaluation with different output modes:

 
```

```

 **Evaluation Commands Flow** Sources: [d3rlpy/cli.py242-351](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L242-L351) [d3rlpy/cli.py233-240](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L233-L240)

 The environment creation function [d3rlpy/cli.py233-240](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L233-L240) enables flexible environment setup through code execution.

 
## Package Management Utilities

 The `install` command provides streamlined installation of optional dependencies.

 
```

```

 **Package Installation Flow** Sources: [d3rlpy/cli.py364-402](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L364-L402) [d3rlpy/cli.py353-362](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L353-L362)

 The package management system uses [d3rlpy/cli.py364-370](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L364-L370) to define available packages and their descriptions.

 
## Dataset Utilities

 The dataset utilities provide functions for loading and managing various reinforcement learning datasets.

 
```

```

 **Dataset Loading Architecture** Sources: [d3rlpy/datasets.py655-740](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L655-L740) [d3rlpy/datasets.py35-48](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L35-L48)

 The main dataset loading function [d3rlpy/datasets.py655-740](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L655-L740) provides automatic dataset detection, while specialized loaders handle specific dataset types.

 
## Torch Utilities

 The torch utilities provide essential functions for PyTorch operations and model management.

 
| Utility Category | Key Functions | Purpose |
|---|---|---|
| Model Synchronization | soft_sync, hard_sync | Target network updates |
| Data Conversion | convert_to_torch_recursively | NumPy to PyTorch conversion |
| Batch Processing | TorchMiniBatch, TorchTrajectoryMiniBatch | Batched data handling |
| Model Management | Modules, Checkpointer | Model state management |

 
### Torch Data Processing Pipeline

 
```

```

 **Torch Data Processing** Sources: [d3rlpy/torch_utility.py216-276](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L216-L276) [d3rlpy/torch_utility.py302-340](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L302-L340)

 
### Model State Management

 
```

```

 **Model Management Utilities** Sources: [d3rlpy/torch_utility.py442-484](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L442-L484) [d3rlpy/torch_utility.py409-440](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L409-L440)

 The `Modules` class [d3rlpy/torch_utility.py442-484](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L442-L484) provides a unified interface for managing PyTorch modules and optimizers, while `Checkpointer` [d3rlpy/torch_utility.py409-440](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py#L409-L440) handles serialization.

 
## Integration with Core Systems

 The CLI and utilities integrate closely with d3rlpy's core systems:

 
```

```

 **System Integration** Sources: [d3rlpy/base.pyNaN-NaN](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#LNaN-LNaN) [d3rlpy/datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py) [d3rlpy/torch_utility.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/torch_utility.py)

 The utilities serve as the bridge between the command-line interface and d3rlpy's internal systems, enabling users to access core functionality through simple commands while maintaining the flexibility of the underlying Python API.
