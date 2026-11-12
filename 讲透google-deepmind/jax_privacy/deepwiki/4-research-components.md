<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/jax_privacy · page 4 Research Components · fetched 2026-10-26 -->

# Research Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [experiments/image_classification/README.md](experiments/image_classification/README.md)

</details>



The Research Components subsystem provides experimental code, reproducible research implementations, and configuration frameworks for conducting differentially private machine learning experiments. This system enables researchers to reproduce published results, run custom experiments, and benchmark different approaches to DP machine learning.

For information about the core production APIs, see [Core Library](#3). For development and testing workflows, see [Development](#5).

## Overview

The research components are organized around reproducible image classification experiments that support the paper "Unlocking High-Accuracy Differentially Private Image Classification through Scale". The system provides a flexible configuration-driven framework for running experiments across different datasets, model architectures, and privacy parameters.

### Research Framework Architecture

```mermaid
graph TB
    subgraph "Experiment Entry Points"
        RUN_EXP["run_experiment_loop.py"]
        CONFIG_FILES["configs/*.py"]
    end
    
    subgraph "Configuration System"
        BASE_CONFIG["config_base.py"]
        MNIST_CONFIG["configs/mnist.py"]
        CIFAR10_CONFIG["configs/cifar10_wrn_16_4_eps1.py"]
        CIFAR100_CONFIG["configs/cifar100_wrn_28_10_eps1_finetune.py"]
        IMAGENET_CONFIG["configs/imagenet_nf_resnet_50_eps8.py"]
    end
    
    subgraph "Core Library Integration"
        DP_SGD["jax_privacy.dp_sgd"]
        TRAINING["jax_privacy.training"]
        ACCOUNTING["jax_privacy.accounting"]
    end
    
    subgraph "Experiment Infrastructure"
        DATA_LOADING["Data Loading Pipeline"]
        MODEL_DEF["Model Definitions"]
        TRAINING_LOOP["Training Loop"]
        EVAL_METRICS["Evaluation Metrics"]
    end
    
    RUN_EXP --> CONFIG_FILES
    CONFIG_FILES --> BASE_CONFIG
    BASE_CONFIG --> MNIST_CONFIG
    BASE_CONFIG --> CIFAR10_CONFIG
    BASE_CONFIG --> CIFAR100_CONFIG
    BASE_CONFIG --> IMAGENET_CONFIG
    
    CONFIG_FILES --> DATA_LOADING
    CONFIG_FILES --> MODEL_DEF
    CONFIG_FILES --> TRAINING_LOOP
    
    TRAINING_LOOP --> DP_SGD
    TRAINING_LOOP --> TRAINING
    TRAINING_LOOP --> ACCOUNTING
    
    TRAINING_LOOP --> EVAL_METRICS
```

**Sources:** [experiments/image_classification/README.md:1-102]()

### Experimental Workflow

The research framework follows a standardized workflow that integrates configuration management with the core DP-SGD implementation:

```mermaid
graph LR
    subgraph "Configuration Phase"
        CONFIG_SELECT["Config File Selection"]
        PARAM_SETUP["Parameter Setup"]
        AUTO_TUNE["Auto-tuning Options"]
    end
    
    subgraph "Training Phase"
        DATA_PREP["Data Preparation"]
        MODEL_INIT["Model Initialization"]
        DP_TRAINING["DP Training Loop"]
        PRIVACY_TRACK["Privacy Tracking"]
    end
    
    subgraph "Evaluation Phase"
        ACCURACY_EVAL["Accuracy Evaluation"]
        PRIVACY_AUDIT["Privacy Audit"]
        RESULT_LOG["Result Logging"]
    end
    
    CONFIG_SELECT --> PARAM_SETUP
    PARAM_SETUP --> AUTO_TUNE
    AUTO_TUNE --> DATA_PREP
    
    DATA_PREP --> MODEL_INIT
    MODEL_INIT --> DP_TRAINING
    DP_TRAINING --> PRIVACY_TRACK
    
    DP_TRAINING --> ACCURACY_EVAL
    PRIVACY_TRACK --> PRIVACY_AUDIT
    ACCURACY_EVAL --> RESULT_LOG
    PRIVACY_AUDIT --> RESULT_LOG
```

**Sources:** [experiments/image_classification/README.md:25-29](), [experiments/image_classification/README.md:33-46]()

## Configuration System

The experimental framework uses a hierarchical configuration system built on `ml_collections` that allows precise control over all experimental parameters:

### Key Configuration Parameters

| Parameter Category | Configuration Path | Purpose |
|-------------------|-------------------|---------|
| Data Augmentation | `config.experiment_kwargs.config.data.augmult` | Controls augmentation multiplier |
| Batch Size | `config.experiment_kwargs.config.training.batch_size.init_value` | Training batch size |
| Learning Rate | `config.experiment_kwargs.config.optimizer.lr.kwargs.value` | Optimizer learning rate |
| Model Architecture | `config.experiment_kwargs.config.model` | Model definition |
| Noise Multiplier | `config.experiment_kwargs.config.training.dp.noise_multiplier` | DP-SGD noise level |
| Training Duration | `config.experiment_kwargs.config.num_updates` | Number of training updates |
| Privacy Budget (δ) | `config.experiment_kwargs.config.dp.delta` | Privacy parameter delta |
| Privacy Budget (ε) | `config.experiment_kwargs.config.dp.auto_tune_target_epsilon` | Target epsilon value |

**Sources:** [experiments/image_classification/README.md:33-46]()

### Configuration Hierarchy

```mermaid
graph TB
    subgraph "Base Configuration"
        CONFIG_BASE["config_base.py<br/>Base parameters and<br/>pre-trained models"]
    end
    
    subgraph "Dataset-Specific Configs"
        MNIST["mnist.py<br/>MNIST experiments"]
        CIFAR10["cifar10_wrn_16_4_eps1.py<br/>CIFAR-10 from scratch"]
        CIFAR100["cifar100_wrn_28_10_eps1_finetune.py<br/>CIFAR-100 fine-tuning"]
        IMAGENET["imagenet_nf_resnet_50_eps8.py<br/>ImageNet experiments"]
    end
    
    subgraph "Configuration Components"
        DATA_CONFIG["Data Pipeline Config"]
        MODEL_CONFIG["Model Architecture Config"]
        TRAINING_CONFIG["Training Loop Config"]
        DP_CONFIG["Privacy Config"]
        OPTIMIZER_CONFIG["Optimizer Config"]
    end
    
    CONFIG_BASE --> MNIST
    CONFIG_BASE --> CIFAR10
    CONFIG_BASE --> CIFAR100
    CONFIG_BASE --> IMAGENET
    
    MNIST --> DATA_CONFIG
    MNIST --> MODEL_CONFIG
    MNIST --> TRAINING_CONFIG
    MNIST --> DP_CONFIG
    MNIST --> OPTIMIZER_CONFIG
```

**Sources:** [experiments/image_classification/README.md:76-77]()

## Available Experiments

The research framework supports several categories of experiments that demonstrate different aspects of differentially private image classification:

### Training from Scratch

These experiments train models from random initialization using DP-SGD:

- **MNIST**: Basic demonstration using the MNIST dataset
- **CIFAR-10**: Wide ResNet 16-4 architecture with ε=1.0 privacy budget
- **ImageNet**: NFNet ResNet-50 architecture with ε=8.0 privacy budget

### Fine-tuning Experiments

These experiments start from pre-trained checkpoints and fine-tune with differential privacy:

- **CIFAR-100**: Wide ResNet 28-10 fine-tuning with ε=1.0 privacy budget

### Experiment Execution Commands

| Experiment Type | Command | Configuration File |
|-----------------|---------|-------------------|
| MNIST | `python run_experiment_loop.py --config=configs/mnist.py` | `configs/mnist.py` |
| CIFAR-10 Scratch | `python run_experiment_loop.py --config=configs/cifar10_wrn_16_4_eps1.py` | `configs/cifar10_wrn_16_4_eps1.py` |
| ImageNet Scratch | `python run_experiment_loop.py --config=configs/imagenet_nf_resnet_50_eps8.py` | `configs/imagenet_nf_resnet_50_eps8.py` |
| CIFAR-100 Fine-tune | `python run_experiment_loop.py --config=configs/cifar100_wrn_28_10_eps1_finetune.py` | `configs/cifar100_wrn_28_10_eps1_finetune.py` |

**Sources:** [experiments/image_classification/README.md:52-77]()

## Integration with Core Library

The research components integrate directly with the core JAX-Privacy library modules to provide production-ready DP-SGD implementations:

```mermaid
graph TB
    subgraph "Research Layer"
        RUN_LOOP["run_experiment_loop.py<br/>Experiment orchestration"]
        CONFIG_SYS["Configuration System<br/>ml_collections based"]
    end
    
    subgraph "Core Library Integration"
        DP_SGD_CORE["jax_privacy.dp_sgd<br/>DP-SGD implementation"]
        TRAINING_UTILS["jax_privacy.training<br/>Training utilities"]
        PRIVACY_ACC["jax_privacy.accounting<br/>Privacy accounting"]
        NOISE_ADD["jax_privacy.noise_addition<br/>Noise generation"]
    end
    
    subgraph "External Dependencies"
        OPTAX_LIB["optax<br/>Optimization"]
        JAX_LIB["jax<br/>Computation backend"]
        DP_ACC_LIB["dp_accounting<br/>Privacy budget tracking"]
    end
    
    RUN_LOOP --> DP_SGD_CORE
    CONFIG_SYS --> TRAINING_UTILS
    CONFIG_SYS --> PRIVACY_ACC
    
    DP_SGD_CORE --> NOISE_ADD
    TRAINING_UTILS --> DP_SGD_CORE
    PRIVACY_ACC --> DP_ACC_LIB
    
    DP_SGD_CORE --> OPTAX_LIB
    DP_SGD_CORE --> JAX_LIB
    TRAINING_UTILS --> OPTAX_LIB
```

**Sources:** [experiments/image_classification/README.md:1-102]()

## Advanced Features

The research framework includes several advanced features for sophisticated experimentation:

### Auto-tuning Capabilities

The `auto_tune` feature allows automatic calibration of privacy parameters:
- Noise multiplier calibration under pre-specified privacy budgets
- Automatic stopping when privacy budget is exhausted
- Dynamic parameter adjustment based on privacy accounting

### Memory Management

The framework includes memory optimization features:
- Configurable `per_device_per_step` batch sizes for memory constraints
- Automatic batch size validation and divisibility checks
- Support for multi-accelerator setups

### Learning Rate Scheduling

Integration with `optax` learning rate schedules is supported, though not used in the paper's best results.

**Sources:** [experiments/image_classification/README.md:93-101]()

## Research Reproducibility

The research components are designed to ensure reproducibility of published results:

### Paper Integration

The experiments directly reproduce results from "Unlocking High-Accuracy Differentially Private Image Classification through Scale" (arXiv:2204.13650), with hyperparameters documented in Appendix C of the paper.

### Citation and References

The system includes proper citation handling through bibtex references and links to the original paper.

### Result Validation

- Training and evaluation accuracies are logged throughout training
- Privacy budget consumption is tracked and reported
- Automatic validation of experimental configurations

**Sources:** [experiments/image_classification/README.md:1-12](), [experiments/image_classification/README.md:81-82]()

---

