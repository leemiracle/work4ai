<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/pytorch-image-models · page 4 Training and Evaluation · fetched 2026-10-26 -->

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmark.py](benchmark.py)
- [inference.py](inference.py)
- [timm/data/config.py](timm/data/config.py)
- [timm/version.py](timm/version.py)
- [train.py](train.py)
- [validate.py](validate.py)

</details>



This document covers the training and evaluation infrastructure in timm, including training scripts, validation tools, benchmarking utilities, and the comprehensive testing framework. The system provides end-to-end capabilities for training models, evaluating their performance, and ensuring reliability across the extensive model collection.

For information about model creation and the registry system that these tools operate on, see [Model Creation and Registry System](#2). For details about the data pipeline that feeds these training and evaluation processes, see [Data Pipeline](#5).

## Training Infrastructure

The training infrastructure is centered around `train.py`, which provides a comprehensive training framework supporting distributed training, mixed precision, various optimizers and schedulers, and extensive data augmentation options.

### Core Training Pipeline

```mermaid
graph TD
    subgraph "Training Entry Points"
        TRAIN_PY["train.py"]
        DIST_TRAIN["distributed_train.sh"]
    end
    
    subgraph "Model Creation"
        CREATE_MODEL["create_model()"]
        FACTORY["build_model_with_cfg()"]
        PRETRAINED["load pretrained weights"]
    end
    
    subgraph "Data Pipeline"
        CREATE_LOADER["create_loader()"]
        CREATE_NAFLEX["create_naflex_loader()"]
        TRANSFORMS["data transforms"]
        AUGMENTATION["mixup, cutmix, autoaugment"]
    end
    
    subgraph "Optimization"
        CREATE_OPT["create_optimizer_v2()"]
        CREATE_SCHED["create_scheduler_v2()"]
        LOSS_FN["loss functions"]
        AMP["automatic mixed precision"]
    end
    
    subgraph "Training Loop"
        FORWARD["model forward pass"]
        BACKWARD["loss.backward()"]
        OPTIMIZER_STEP["optimizer.step()"]
        SCHEDULER_STEP["scheduler.step()"]
    end
    
    subgraph "Outputs"
        CHECKPOINTS["model checkpoints"]
        WANDB["experiment tracking"]
        LOGS["training logs"]
    end
    
    TRAIN_PY --> CREATE_MODEL
    TRAIN_PY --> CREATE_LOADER
    TRAIN_PY --> CREATE_OPT
    TRAIN_PY --> CREATE_SCHED
    DIST_TRAIN --> TRAIN_PY
    
    CREATE_MODEL --> FACTORY
    FACTORY --> PRETRAINED
    
    CREATE_LOADER --> TRANSFORMS
    CREATE_NAFLEX --> TRANSFORMS
    TRANSFORMS --> AUGMENTATION
    
    CREATE_OPT --> LOSS_FN
    CREATE_SCHED --> AMP
    
    FORWARD --> BACKWARD
    BACKWARD --> OPTIMIZER_STEP
    OPTIMIZER_STEP --> SCHEDULER_STEP
    
    SCHEDULER_STEP --> CHECKPOINTS
    SCHEDULER_STEP --> WANDB
    SCHEDULER_STEP --> LOGS
```

The training system supports extensive configuration through command-line arguments organized into logical groups: dataset parameters, model parameters, device settings, optimizer parameters, learning rate schedules, augmentation settings, batch normalization parameters, model EMA, and miscellaneous options.

**Sources:** [train.py:1-1200]()

### Advanced Training Features

The training infrastructure includes several advanced features:

- **NaFlex Training**: Variable resolution training for NaFlexViT models through `--naflex-loader` with configurable sequence lengths and patch sizes
- **Distributed Training**: Multi-GPU training support with gradient accumulation and synchronized batch normalization
- **Mixed Precision**: Native PyTorch AMP and Apex AMP support with configurable precision types
- **Model Compilation**: Support for TorchScript, torch.compile, and functorch optimization
- **Experiment Tracking**: Weights & Biases integration for monitoring training progress

**Sources:** [train.py:404-417](), [train.py:466-481](), [train.py:529-531]()

## Model Evaluation

The evaluation system provides comprehensive tools for validating trained models and measuring their performance across different metrics and datasets.

### Validation Pipeline

```mermaid
graph LR
    subgraph "Validation Script"
        VALIDATE_PY["validate.py"]
        ARGS["ArgumentParser"]
        VALIDATE_FN["validate()"]
    end
    
    subgraph "Model Setup"
        LOAD_MODEL["create_model()"]
        LOAD_CHECKPOINT["load_checkpoint()"]
        MODEL_CONFIG["resolve_data_config()"]
    end
    
    subgraph "Data Loading"
        CREATE_DATASET["create_dataset()"]
        VALIDATION_LOADER["create_loader()"]
        NAFLEX_LOADER["create_naflex_loader()"]
        REAL_LABELS["RealLabelsImagenet"]
    end
    
    subgraph "Evaluation Loop"
        INFERENCE_MODE["torch.inference_mode()"]
        MODEL_FORWARD["model(input)"]
        ACCURACY_CALC["accuracy()"]
        METRICS["precision, recall, f1"]
    end
    
    subgraph "Results"
        RESULTS_CSV["results CSV/JSON"]
        TOP1_TOP5["top1/top5 accuracy"]
        SKLEARN_METRICS["sklearn metrics"]
    end
    
    VALIDATE_PY --> ARGS
    ARGS --> VALIDATE_FN
    
    VALIDATE_FN --> LOAD_MODEL
    LOAD_MODEL --> LOAD_CHECKPOINT
    LOAD_CHECKPOINT --> MODEL_CONFIG
    
    VALIDATE_FN --> CREATE_DATASET
    CREATE_DATASET --> VALIDATION_LOADER
    CREATE_DATASET --> NAFLEX_LOADER
    CREATE_DATASET --> REAL_LABELS
    
    VALIDATION_LOADER --> INFERENCE_MODE
    INFERENCE_MODE --> MODEL_FORWARD
    MODEL_FORWARD --> ACCURACY_CALC
    ACCURACY_CALC --> METRICS
    
    METRICS --> RESULTS_CSV
    METRICS --> TOP1_TOP5
    METRICS --> SKLEARN_METRICS
```

The validation script supports various evaluation modes including standard validation, real labels evaluation for ImageNet, and comprehensive metrics calculation with scikit-learn integration.

**Sources:** [validate.py:179-467]()

### Evaluation Features

Key evaluation capabilities include:

- **Flexible Data Loading**: Support for various dataset formats with customizable preprocessing
- **Real Labels Support**: Corrected ImageNet labels for more accurate evaluation
- **Advanced Metrics**: Beyond accuracy, supports precision, recall, and F1-score with different averaging methods
- **Test Time Augmentation**: Optional TTA support for improved evaluation accuracy
- **Model Optimizations**: Support for reparameterization, mixed precision, and model compilation during evaluation

**Sources:** [validate.py:164-178](), [validate.py:436-449]()

## Performance Benchmarking

The benchmarking system provides detailed performance analysis for models, measuring inference speed, training throughput, and computational requirements.

### Benchmark Architecture

```mermaid
graph TD
    subgraph "Benchmark Entry"
        BENCHMARK_PY["benchmark.py"]
        BENCHMARK_RUNNER["BenchmarkRunner"]
        INF_RUNNER["InferenceBenchmarkRunner"]
        TRAIN_RUNNER["TrainBenchmarkRunner"]
    end
    
    subgraph "Model Profiling"
        PROFILE_DEEPSPEED["profile_deepspeed()"]
        PROFILE_FVCORE["profile_fvcore()"]
        FLOP_COUNT["FlopCountAnalysis"]
        ACTIVATION_COUNT["ActivationCountAnalysis"]
    end
    
    subgraph "Timing Infrastructure"
        CUDA_TIMESTAMP["cuda_timestamp()"]
        TIME_FN["time_fn"]
        WARMUP["warmup iterations"]
        BENCHMARK_ITER["benchmark iterations"]
    end
    
    subgraph "Inference Benchmark"
        INF_STEP["inference step"]
        SAMPLES_PER_SEC["samples/sec"]
        STEP_TIME["step time (ms)"]
    end
    
    subgraph "Training Benchmark"
        TRAIN_STEP["training step"]
        FWD_TIME["forward time"]
        BWD_TIME["backward time"]
        OPT_TIME["optimizer time"]
    end
    
    subgraph "Results"
        PERFORMANCE_METRICS["performance metrics"]
        FLOP_ANALYSIS["FLOP analysis"]
        MEMORY_USAGE["memory usage"]
        RESULTS_OUTPUT["CSV/JSON output"]
    end
    
    BENCHMARK_PY --> BENCHMARK_RUNNER
    BENCHMARK_RUNNER --> INF_RUNNER
    BENCHMARK_RUNNER --> TRAIN_RUNNER
    
    INF_RUNNER --> PROFILE_DEEPSPEED
    INF_RUNNER --> PROFILE_FVCORE
    PROFILE_FVCORE --> FLOP_COUNT
    PROFILE_FVCORE --> ACTIVATION_COUNT
    
    INF_RUNNER --> CUDA_TIMESTAMP
    TRAIN_RUNNER --> TIME_FN
    TIME_FN --> WARMUP
    WARMUP --> BENCHMARK_ITER
    
    INF_RUNNER --> INF_STEP
    INF_STEP --> SAMPLES_PER_SEC
    INF_STEP --> STEP_TIME
    
    TRAIN_RUNNER --> TRAIN_STEP
    TRAIN_STEP --> FWD_TIME
    TRAIN_STEP --> BWD_TIME
    TRAIN_STEP --> OPT_TIME
    
    SAMPLES_PER_SEC --> PERFORMANCE_METRICS
    FWD_TIME --> FLOP_ANALYSIS
    FLOP_ANALYSIS --> MEMORY_USAGE
    MEMORY_USAGE --> RESULTS_OUTPUT
```

The benchmarking system provides separate runners for inference and training benchmarks, with detailed timing analysis and computational profiling capabilities.

**Sources:** [benchmark.py:214-292](), [benchmark.py:300-372](), [benchmark.py:375-497]()

### Benchmark Capabilities

The benchmark infrastructure supports:

- **Inference Benchmarking**: Measures throughput, latency, and computational requirements for inference workloads
- **Training Benchmarking**: Profiles forward pass, backward pass, and optimizer step timing separately
- **FLOP Analysis**: Integration with DeepSpeed profiler and FVCore for detailed computational analysis
- **Memory Profiling**: Tracks memory usage patterns during model execution
- **Model Compilation**: Benchmarks performance with TorchScript, torch.compile, and other optimization techniques

**Sources:** [benchmark.py:354-367](), [benchmark.py:187-211]()

## Batch Inference

The inference system provides efficient batch processing capabilities for large-scale model deployment and evaluation scenarios.

### Inference Pipeline

The `inference.py` script implements a streamlined pipeline for batch inference with flexible output formatting:

- **Data Processing**: Supports various dataset formats with automatic ImageNet subset detection for labeling
- **Output Formats**: Configurable output in CSV, JSON, or Parquet formats with customizable column naming
- **Label Resolution**: Automatic conversion of class indices to human-readable labels using ImageNet metadata
- **Flexible Precision**: Support for mixed precision inference and model compilation optimizations

**Sources:** [inference.py:156-375]()

## Testing Framework

The testing infrastructure ensures model reliability and compatibility across the extensive collection of model architectures.

### Test Organization

```mermaid
graph TD
    subgraph "Test Categories"
        BASE_TESTS["@pytest.mark.base"]
        CFG_TESTS["@pytest.mark.cfg"]
        TORCHSCRIPT_TESTS["@pytest.mark.torchscript"]
        FEATURES_TESTS["@pytest.mark.features"]
    end
    
    subgraph "Core Test Functions"
        TEST_INFERENCE["test_model_inference()"]
        TEST_FORWARD["test_model_forward()"]
        TEST_BACKWARD["test_model_backward()"]
        TEST_DEFAULT_CFGS["test_model_default_cfgs()"]
        TEST_FEATURES["test_model_forward_features()"]
        TEST_INTERMEDIATES["test_model_forward_intermediates()"]
    end
    
    subgraph "Test Infrastructure"
        MODEL_FILTERS["EXCLUDE_FILTERS, NON_STD_FILTERS"]
        SIZE_LIMITS["TARGET_FWD_SIZE, MAX_BWD_SIZE"]
        INPUT_RESOLUTION["_get_input_size()"]
        TEST_VALIDATION["tensor validation"]
    end
    
    subgraph "Model Validation"
        PRETRAINED_TEST["pretrained weight loading"]
        GRADIENT_CHECK["gradient computation"]
        FEATURE_EXTRACTION["feature extraction"]
        INTERMEDIATE_OUTPUTS["intermediate layer outputs"]
    end
    
    BASE_TESTS --> TEST_INFERENCE
    BASE_TESTS --> TEST_FORWARD
    BASE_TESTS --> TEST_BACKWARD
    CFG_TESTS --> TEST_DEFAULT_CFGS
    FEATURES_TESTS --> TEST_FEATURES
    FEATURES_TESTS --> TEST_INTERMEDIATES
    
    TEST_INFERENCE --> MODEL_FILTERS
    TEST_FORWARD --> SIZE_LIMITS
    TEST_BACKWARD --> INPUT_RESOLUTION
    TEST_DEFAULT_CFGS --> TEST_VALIDATION
    
    TEST_INFERENCE --> PRETRAINED_TEST
    TEST_BACKWARD --> GRADIENT_CHECK
    TEST_FEATURES --> FEATURE_EXTRACTION
    TEST_INTERMEDIATES --> INTERMEDIATE_OUTPUTS
```

The testing framework is organized into multiple categories with specific markers for parallel execution in CI environments.

**Sources:** [tests/test_models.py:1-12](), [tests/test_models.py:125-236]()

### Test Coverage

The testing infrastructure provides comprehensive coverage:

- **Model Inference**: Validates pretrained model outputs against reference tensors stored in Hugging Face Hub
- **Forward/Backward Pass**: Ensures models can perform forward inference and gradient computation
- **Configuration Validation**: Verifies model default configurations match expected specifications  
- **Feature Extraction**: Tests intermediate layer output extraction and feature-only model creation
- **TorchScript Compatibility**: Validates models can be scripted for deployment
- **Memory Management**: Includes adaptive batch size testing with retry mechanisms for resource-constrained environments

**Sources:** [tests/test_models.py:129-167](), [tests/test_models.py:173-236](), [tests/test_models.py:419-440]()

## Integration with Model Creation System

The training and evaluation infrastructure integrates seamlessly with timm's model creation system through standardized interfaces:

| Component | Integration Point | Description |
|-----------|------------------|-------------|
| `create_model()` | All scripts | Unified model instantiation with pretrained weight loading |
| `resolve_data_config()` | Data preprocessing | Automatic resolution of input size, normalization, and preprocessing parameters |
| Model registry | Model selection | Access to all registered models through string identifiers |
| Pretrained configurations | Default settings | Automatic application of model-specific training and evaluation settings |
| Feature extraction | Advanced evaluation | Support for intermediate layer outputs and feature-only model creation |

The system supports over 1000 model variants with consistent interfaces for training, evaluation, and deployment, making it easy to experiment with different architectures using the same infrastructure.

**Sources:** [train.py:502-517](), [validate.py:232-243](), [benchmark.py:244-254](), [tests/test_models.py:175-176]()

---

