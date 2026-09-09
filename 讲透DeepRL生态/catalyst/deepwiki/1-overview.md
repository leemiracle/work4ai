> 来源: [https://deepwiki.com/catalyst-team/catalyst/1-overview](https://deepwiki.com/catalyst-team/catalyst/1-overview)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Overview

  Relevant source files 
 - [.github/workflows/codestyle.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/codestyle.yml)
 - [.github/workflows/deploy_publish.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/deploy_publish.yml)
 - [.github/workflows/deploy_push.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/deploy_push.yml)
 - [.github/workflows/dl_cpu.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/dl_cpu.yml)
 - [.github/workflows/dl_cpu_minimal.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/dl_cpu_minimal.yml)
 - [.github/workflows/integrations.yml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.github/workflows/integrations.yml)
 - [.gitignore](https://github.com/catalyst-team/catalyst/blob/e99f9065/.gitignore)
 - [.pre-commit-config.yaml](https://github.com/catalyst-team/catalyst/blob/e99f9065/.pre-commit-config.yaml)
 - [CHANGELOG.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/CHANGELOG.md?plain=1)
 - [CONTRIBUTING.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1)
 - [README.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1)
 - [bin/workflows/check_config_api.sh](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_config_api.sh)
 - [bin/workflows/check_settings.sh](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_settings.sh)
 - [catalyst/__version__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/__version__.py)
 - [catalyst/contrib/scripts/run.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/scripts/run.py)
 - [catalyst/contrib/scripts/tune.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/scripts/tune.py)
 - [catalyst/core/misc.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/misc.py)
 - [catalyst/settings.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py)
 - [docs/conf.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/conf.py)
 - [docs/index.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/index.rst)
 - [docs/requirements.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/requirements.txt)
 - [examples/README.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/README.md?plain=1)
 - [examples/notebooks/XLA.ipynb](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/notebooks/XLA.ipynb)
 - [examples/notebooks/XLA_ddp.ipynb](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/notebooks/XLA_ddp.ipynb)
 - [examples/notebooks/colab_ci_cd.ipynb](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/notebooks/colab_ci_cd.ipynb)
 - [requirements/requirements-cv.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-cv.txt)
 - [requirements/requirements-dev.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-dev.txt)
 - [requirements/requirements-optuna.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-optuna.txt)
 - [requirements/requirements.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements.txt)
 - [setup.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py)
 - [tests/benchmarks/test_benchmark.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/tests/benchmarks/test_benchmark.py)
 
  Catalyst is a PyTorch framework for accelerated Deep Learning research and development. It provides a comprehensive, flexible architecture that reduces boilerplate code while maintaining full control over the training process. This wiki page introduces the core concepts, architecture, and components of the Catalyst framework.

 Catalyst helps you implement compact but full-featured Deep Learning pipelines with just a few lines of code. You get a training loop with metrics, early-stopping, model checkpointing, and other features without writing repetitive code. The framework is designed to be modular, allowing you to customize any part of the training pipeline while maintaining a clean, organized structure.

 
## Installation

 Basic installation:

 
```

```

 Specialized installations:

 
```

```

 Catalyst is compatible with Python 3.7+ and PyTorch 1.4+. It has been tested on Ubuntu 16.04/18.04/20.04, macOS 10.15, Windows 10, and Windows Subsystem for Linux.

 Sources: [README.md159-183](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L159-L183) [setup.py41-62](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py#L41-L62) [catalyst/__version__.py1-2](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/__version__.py#L1-L2)

 
## Core Architecture

 Catalyst's architecture is centered around a few key abstractions that provide a flexible and extensible framework for deep learning experiments.

 
```

```

 
### Core Components

 The Catalyst framework consists of several key components:

 
 - **Runner System**: Coordinates the entire training process by managing epochs, loaders, and batches. It serves as the central orchestrator that connects all components.
 - **Callback System**: Provides an event-driven mechanism to extend the training loop behavior at specific points, allowing for clean customization.
 - **Engine System**: Abstracts hardware-specific details, allowing models to run on various devices (CPU, GPU, TPU) with different optimizations.
 - **Logger System**: Handles logging of metrics and other training information to different backends (console, TensorBoard, MLflow, etc.).
 - **Metrics System**: Computes and aggregates various performance metrics during training and evaluation.
 - **Utilities**: Common functions and tools used throughout the framework.
 
 Sources: [README.md151-155](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L151-L155) [setup.py63-86](https://github.com/catalyst-team/catalyst/blob/e99f9065/setup.py#L63-L86) [docs/index.rst112-119](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/index.rst#L112-L119) [catalyst/settings.py15-16](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L15-L16)

 
## Training Loop Flow

 The training process in Catalyst follows an event-driven architecture, where the Runner orchestrates the workflow and triggers callbacks at appropriate points in the training loop.

 
```

```

 A typical training workflow in Catalyst:

 
 - The user initializes a Runner with model, criterion, optimizer, and data loaders.
 - The Runner triggers experiment start callbacks.
 - For each epoch, the Runner: 
 - Triggers epoch start callbacks
 - Iterates through each data loader (train/valid)
 - For each batch: 
 - Performs forward pass using the Engine
 - Handles the batch (computes loss, metrics, etc.)
 - If in training mode, performs backward pass and optimizer step
 - Triggers batch end callbacks
 - Triggers loader end callbacks
 - Logs metrics
 - Triggers epoch end callbacks
 - The Runner triggers experiment end callbacks and returns the trained model.
 
 This event-driven architecture allows extensive customization at various stages of the training process through callbacks.

 Sources: [README.md84-104](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L84-L104) [catalyst/core/misc.py40-69](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/misc.py#L40-L69)

 
## Hardware Abstraction with Engine System

 Catalyst provides a unified interface for training models on various hardware configurations through its Engine system. This abstraction allows users to easily switch between different hardware setups without changing their code.

 
```

```

 The Engine system supports:

 
 - **Basic Hardware**:

 
 - CPU Engine for CPU-based training
 - GPU Engine for single GPU training
 - DataParallel Engine for multi-GPU training on a single machine
 - Distributed DataParallel Engine for multi-GPU training across multiple machines
 - XLA Engine for training on TPUs
 - **Optimization Techniques**:

 
 - Automatic Mixed Precision (AMP) for faster training with lower memory usage
 - APEX for NVIDIA's optimized mixed precision training
 - FairScale for memory-efficient large-scale training
 - DeepSpeed for extreme-scale model training optimization
 
 Users can specify their desired engine either programmatically or through the command line, making it easy to adapt to different hardware environments.

 Table of Engine Features:

 
| Engine | Hardware | Mixed Precision | Distributed | Special Features |
|---|---|---|---|---|
| CPU | CPU | No | No | - |
| GPU | Single GPU | No | No | - |
| DP | Multiple GPUs | No | Single Machine | Data Parallelism |
| DDP | Multiple GPUs | No | Multi-Machine | Distributed Data Parallelism |
| XLA | TPU | Yes | Yes | XLA Compilation |
| AMP | GPU | Yes | No | 16-bit Precision |
| APEX | GPU | Yes | Yes | NVIDIA Optimizations |
| FairScale | GPU | Yes | Yes | Zero Redundancy Optimizer |
| DeepSpeed | GPU | Yes | Yes | ZeRO-Offload, Pipeline Parallelism |

 Sources: [catalyst/settings.py241-270](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L241-L270) [examples/notebooks/XLA.ipynb](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/notebooks/XLA.ipynb) [examples/notebooks/XLA_ddp.ipynb](https://github.com/catalyst-team/catalyst/blob/e99f9065/examples/notebooks/XLA_ddp.ipynb)

 
## Data Handling Components

 Catalyst provides several specialized components for efficient data loading and preprocessing, particularly for handling imbalanced datasets, distributed training, and self-supervised learning.

 
```

```

 
### Data Samplers

 Catalyst provides specialized samplers to address common challenges in deep learning:

 
 - **Class Imbalance Samplers**:

 
 - `BalanceClassSampler`: Ensures balanced class representation in each epoch
 - `BatchBalanceClassSampler`: Maintains class balance within each batch
 - `DynamicBalanceClassSampler`: Adaptively balances classes based on training dynamics
 - **Efficiency Samplers**:

 
 - `MiniEpochSampler`: Enables training on a subset of data for faster iterations
 - `DistributedSamplerWrapper`: Adapts any sampler for distributed training
 
 
### Dataset Wrappers

 
 - **Self-Supervised Learning**:

 
 - `SelfSupervisedDatasetWrapper`: Transforms datasets for self-supervised learning tasks
 - **Utility Wrappers**:

 
 - `DatasetFromSampler`: Creates a dataset from a sampler for custom sampling strategies
 - `BatchPrefetchLoaderWrapper`: Prefetches batches to GPU for improved throughput
 
 These components integrate with PyTorch's data loading infrastructure, providing optimizations specific to deep learning workflows while maintaining compatibility with PyTorch's ecosystem.

 Sources: [README.md584-628](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L584-L628) [requirements/requirements-cv.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-cv.txt) [requirements/requirements-ml.txt](https://github.com/catalyst-team/catalyst/blob/e99f9065/requirements/requirements-ml.txt)

 
## Callback System

 Catalyst's callback system provides a flexible way to customize the training process by intercepting at various stages of the training loop. Callbacks are organized in a hierarchy and triggered at specific points during training.

 
```

```

 Catalyst provides a rich set of built-in callbacks:

 
 - **Core Process Callbacks**:

 
 - `OptimizerCallback`: Handles optimizer updates and gradient clipping
 - `SchedulerCallback`: Manages learning rate scheduling
 - `BackwardCallback`: Controls the backward pass and gradient computation
 - `CheckpointCallback`: Saves and loads model checkpoints
 - **Metric Callbacks**:

 
 - `AccuracyCallback`: Computes classification accuracy
 - `PrecisionRecallF1SupportCallback`: Computes precision, recall, and F1 score
 - `AUCCallback`: Computes Area Under the ROC Curve
 - `IOUCallback`, `DiceCallback`: For segmentation metrics
 - `CMCScoreCallback`: For retrieval/ReID tasks
 - **Utility Callbacks**:

 
 - `BatchTransformCallback`: Applies transformations to batches
 - `ProfilerCallback`: Profiles code execution for performance optimization
 - `PeriodicLoaderCallback`: Runs validation at specified intervals
 
 Callbacks are executed in a specific order defined by `CallbackOrder`, ensuring that interdependent operations happen in the correct sequence (e.g., backward pass before optimizer step).

 Sources: [README.md523-563](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L523-L563) [catalyst/core/misc.py19-38](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/core/misc.py#L19-L38)

 
## Metrics System

 Catalyst provides a comprehensive metrics system for evaluating model performance across various machine learning tasks.

 
```

```

 
### Classification Metrics

 
 - **Accuracy**: Computes overall accuracy with support for top-k predictions
 - **Precision, Recall, F1**: Evaluates precision, recall, and F1 score for classification tasks
 - **AUC**: Computes Area Under the ROC Curve for binary classification
 - **Confusion Matrix**: Generates confusion matrix for model analysis
 
 
### Segmentation Metrics

 
 - **IoU (Jaccard Index)**: Measures overlap between predicted and ground truth masks
 - **Dice Coefficient**: Evaluates segmentation quality, particularly in medical imaging
 - **Trevsky Index**: Weighted version of Dice coefficient
 
 
### Retrieval and Recommendation Metrics

 
 - **Mean Average Precision (MAP)**: Evaluates ranking quality
 - **Mean Reciprocal Rank (MRR)**: Measures ranking performance
 - **Normalized Discounted Cumulative Gain (NDCG)**: Evaluates ranking with relevance scores
 - **Hitrate**: Measures if relevant items appear in top-k results
 
 
### Regression Metrics

 
 - **R² Score**: Coefficient of determination for regression quality
 - **MSE/MAE**: Mean squared/absolute error for regression tasks
 
 Metrics can be computed at batch level or aggregated at loader level. For multi-class scenarios, Catalyst supports micro, macro, and weighted averaging strategies.

 
### Logging System

 Metrics are recorded through Catalyst's logger system, which supports various backends:

 
 - **TensorboardLogger**: Visualizes metrics in TensorBoard
 - **ConsoleLogger**: Prints metrics to console
 - **MLflowLogger**: Logs to MLflow tracking server
 - **WandbLogger**: Integrates with Weights & Biases
 - **NeptuneLogger**: Logs to Neptune.ai
 - **CometLogger**: Logs to Comet.ml
 - **CSVLogger**: Saves metrics to CSV files
 
 Settings for metrics computation and logging can be configured globally through the `SETTINGS` object or environment variables:

 
```

```

 Sources: [catalyst/settings.py330-340](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/settings.py#L330-L340) [README.md607-627](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L607-L627)

 
## CLI and Configuration

 Catalyst provides command-line tools for running experiments and hyperparameter optimization:

 
### catalyst-run

 `catalyst-run` allows running experiments defined in YAML configuration files:

 
```

```

 The configuration file specifies the runner, model, criterion, optimizer, scheduler, and callbacks in a declarative way.

 
### catalyst-tune

 `catalyst-tune` integrates with Optuna for hyperparameter optimization:

 
```

```

 This command runs hyperparameter tuning with the specified configuration and number of trials.

 Sources: [catalyst/contrib/scripts/run.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/scripts/run.py) [catalyst/contrib/scripts/tune.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/scripts/tune.py) [bin/workflows/check_config_api.sh](https://github.com/catalyst-team/catalyst/blob/e99f9065/bin/workflows/check_config_api.sh)

 
## Extensibility

 Catalyst is designed to be highly extensible. Users can create custom:

 
 - **Runners**: By extending `Runner` or `SupervisedRunner` to implement custom training logic
 - **Callbacks**: By extending `Callback` to add custom behavior at any point in the training process
 - **Metrics**: By implementing the `IMetric` interface to compute custom performance metrics
 - **Engines**: To support custom hardware acceleration or optimization techniques
 
 The framework provides clear interfaces and base classes for each extensible component, making it easy to customize without breaking the overall architecture.

 Sources: [README.md231-308](https://github.com/catalyst-team/catalyst/blob/e99f9065/README.md?plain=1#L231-L308) [CONTRIBUTING.md](https://github.com/catalyst-team/catalyst/blob/e99f9065/CONTRIBUTING.md?plain=1)
