<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DeepLearningExamples · page 2 PyTorch Models · fetched 2026-10-26 -->

# PyTorch Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PyTorch/Classification/ConvNets/Dockerfile](PyTorch/Classification/ConvNets/Dockerfile)
- [PyTorch/Classification/ConvNets/README.md](PyTorch/Classification/ConvNets/README.md)
- [PyTorch/Classification/ConvNets/checkpoint2model.py](PyTorch/Classification/ConvNets/checkpoint2model.py)
- [PyTorch/Classification/ConvNets/classify.py](PyTorch/Classification/ConvNets/classify.py)
- [PyTorch/Classification/ConvNets/configs.yml](PyTorch/Classification/ConvNets/configs.yml)
- [PyTorch/Classification/ConvNets/efficientnet/README.md](PyTorch/Classification/ConvNets/efficientnet/README.md)
- [PyTorch/Classification/ConvNets/image_classification/dataloaders.py](PyTorch/Classification/ConvNets/image_classification/dataloaders.py)
- [PyTorch/Classification/ConvNets/image_classification/gpu_affinity.py](PyTorch/Classification/ConvNets/image_classification/gpu_affinity.py)
- [PyTorch/Classification/ConvNets/image_classification/logger.py](PyTorch/Classification/ConvNets/image_classification/logger.py)
- [PyTorch/Classification/ConvNets/image_classification/models/__init__.py](PyTorch/Classification/ConvNets/image_classification/models/__init__.py)
- [PyTorch/Classification/ConvNets/image_classification/models/common.py](PyTorch/Classification/ConvNets/image_classification/models/common.py)
- [PyTorch/Classification/ConvNets/image_classification/models/efficientnet.py](PyTorch/Classification/ConvNets/image_classification/models/efficientnet.py)
- [PyTorch/Classification/ConvNets/image_classification/models/entrypoints.py](PyTorch/Classification/ConvNets/image_classification/models/entrypoints.py)
- [PyTorch/Classification/ConvNets/image_classification/models/model.py](PyTorch/Classification/ConvNets/image_classification/models/model.py)
- [PyTorch/Classification/ConvNets/image_classification/models/resnet.py](PyTorch/Classification/ConvNets/image_classification/models/resnet.py)
- [PyTorch/Classification/ConvNets/image_classification/optimizers.py](PyTorch/Classification/ConvNets/image_classification/optimizers.py)
- [PyTorch/Classification/ConvNets/image_classification/training.py](PyTorch/Classification/ConvNets/image_classification/training.py)
- [PyTorch/Classification/ConvNets/image_classification/utils.py](PyTorch/Classification/ConvNets/image_classification/utils.py)
- [PyTorch/Classification/ConvNets/main.py](PyTorch/Classification/ConvNets/main.py)
- [PyTorch/Classification/ConvNets/model2onnx.py](PyTorch/Classification/ConvNets/model2onnx.py)
- [PyTorch/Classification/ConvNets/quant_main.py](PyTorch/Classification/ConvNets/quant_main.py)
- [PyTorch/Classification/ConvNets/requirements.txt](PyTorch/Classification/ConvNets/requirements.txt)
- [PyTorch/Classification/ConvNets/resnet50v1.5/README.md](PyTorch/Classification/ConvNets/resnet50v1.5/README.md)
- [PyTorch/Classification/ConvNets/resnext101-32x4d/README.md](PyTorch/Classification/ConvNets/resnext101-32x4d/README.md)
- [PyTorch/Classification/ConvNets/se-resnext101-32x4d/README.md](PyTorch/Classification/ConvNets/se-resnext101-32x4d/README.md)
- [PyTorch/Classification/ConvNets/triton/deployer.py](PyTorch/Classification/ConvNets/triton/deployer.py)
- [hubconf.py](hubconf.py)

</details>



This page provides a technical overview of the PyTorch model implementations in the NVIDIA Deep Learning Examples repository. It covers the common infrastructure, model families, and shared optimizations across these implementations. For information about TensorFlow models, see [TensorFlow Models](#3), and for deployment details, see [Deployment](#5).

## Model Organization

The repository organizes PyTorch models primarily by application domain, with each model family having dedicated directories and shared components.

```mermaid
flowchart TD
    PyTorch["PyTorch Models"]
    PyTorch --> Classification["Classification Models"]
    PyTorch --> NLP["Natural Language Processing"]
    PyTorch --> SpeechSynthesis["Speech Synthesis"]
    PyTorch --> Detection["Object Detection"]
    PyTorch --> Forecasting["Forecasting"]
    
    Classification --> ConvNets["ConvNets"]
    Classification --> GPUNet["GPUNet"]
    
    ConvNets --> ResNet["ResNet50v1.5"]
    ConvNets --> ResNeXt["ResNeXt101-32x4d"]
    ConvNets --> SEResNeXt["SE-ResNeXt101-32x4d"]
    ConvNets --> EfficientNet["EfficientNet"]
    
    NLP --> BERT["BERT"]
    
    SpeechSynthesis --> Tacotron2["Tacotron2"]
    SpeechSynthesis --> FastPitch["FastPitch"]
    SpeechSynthesis --> HiFiGAN["HiFi-GAN"]
    
    Detection --> SSD["SSD"]
    
    Forecasting --> TFT["Temporal Fusion Transformer (TFT)"]
```

Sources: [hubconf.py:1-35](), [PyTorch/Classification/ConvNets/README.md:1-123]()

## Common Infrastructure

### Model Framework

The repository implements a consistent framework for defining models, with a focus on reusability and configurability. The core components include:

```mermaid
classDiagram
    class ModelArch {
        +String name
        +Int default_image_size
    }
    
    class ModelParams {
        +Int num_classes
        +parser()
    }
    
    class Model {
        +constructor: Callable
        +arch: ModelArch
        +params: ModelParams
        +optimizer_params: OptimizerParams
        +checkpoint_url: String
    }
    
    class EntryPoint {
        +String name
        +Model model
        +__call__()
        +parser()
    }
    
    Model --> ModelArch
    Model --> ModelParams
    EntryPoint --> Model
```

Sources: [PyTorch/Classification/ConvNets/image_classification/models/model.py:14-184]()

The architecture adopts a dataclass-based approach for model configuration:

1. `ModelArch` - Defines the architecture characteristics of a model
2. `ModelParams` - Contains model parameters like number of classes
3. `Model` - Combines architecture, parameters and construction logic
4. `EntryPoint` - Provides a standardized interface for model access

This design allows for:
- Consistent model instantiation across all model types
- Easy parameter configuration through common CLI interfaces
- Standardized checkpoint handling for pretrained weights

### Training Framework

The training infrastructure is designed for performance and flexibility:

```mermaid
classDiagram
    class Executor {
        +model: nn.Module
        +loss: nn.Module
        +amp: bool
        +scaler: GradScaler
        +forward_backward()
        +forward()
        +train()
        +eval()
        +distributed()
    }
    
    class Trainer {
        +executor: Executor
        +optimizer: Optimizer
        +grad_acc_steps: int
        +use_ema: bool
        +train_step()
        +train()
        +eval()
        +validation_steps()
        +state_dict()
    }
    
    Trainer --> Executor
```

Sources: [PyTorch/Classification/ConvNets/image_classification/training.py:46-202]()

Key components of the training infrastructure:

- `Executor`: Handles model forward/backward passes, loss computation, mixed precision operations, and distributed setup
- `Trainer`: Manages training state, optimization steps, EMA updates, and checkpointing
- Training utilities: Support for gradient accumulation, loss scaling, validation metrics

The training loop function connects these components to provide a complete training pipeline:

```mermaid
flowchart TD
    train_loop["train_loop()"]
    train_loop --> setup_training["Setup training metrics and checkpointer"]
    setup_training --> epoch_loop["For each epoch"]
    
    epoch_loop --> |"if not skip_training"| train_epoch["Train epoch"]
    epoch_loop --> |"if not skip_validation"| validate["Validate model"]
    validate --> |"if improved"| save_best["Save best checkpoint"]
    
    epoch_loop --> |"if early_stopping"| check_early_stop["Check early stopping"]
    epoch_loop --> |"if save_checkpoints"| save_checkpoint["Save epoch checkpoint"]
```

Sources: [PyTorch/Classification/ConvNets/image_classification/training.py:313-435]()

## Data Loading Framework

The repository implements multiple data backends for efficient input processing:

```mermaid
flowchart LR
    DataBackends["Data Backends"] --> PyTorch["PyTorch Native"]
    DataBackends --> DALI_CPU["DALI CPU"]
    DataBackends --> DALI_GPU["DALI GPU"]
    DataBackends --> Synthetic["Synthetic Data"]
    
    PyTorch --> PytorchLoaders["get_pytorch_train/val_loader()"]
    DALI_CPU --> DALILoaders_CPU["get_dali_train/val_loader(dali_cpu=True)"]
    DALI_GPU --> DALILoaders_GPU["get_dali_train/val_loader(dali_cpu=False)"]
    Synthetic --> SyntheticLoader["get_synthetic_loader()"]
    
    PytorchLoaders --> PrefetchedWrapper["PrefetchedWrapper"]
    DALILoaders_CPU --> DALIWrapper["DALIWrapper"]
    DALILoaders_GPU --> DALIWrapper
    SyntheticLoader --> SynteticDataLoader["SynteticDataLoader"]
```

Sources: [PyTorch/Classification/ConvNets/image_classification/dataloaders.py:30-577]()

Key features of the data loading framework:

- Support for multiple data backends (PyTorch, DALI-CPU, DALI-GPU, Synthetic)
- Prefetching and pipelining for maximizing GPU utilization
- Common data augmentation options (random resized crop, horizontal flip, etc.)
- Mixed precision data preprocessing

## Classification Models

### Model Architectures

The repository includes several state-of-the-art ConvNet architectures:

| Model | Description | Top-1 Accuracy | 
|-------|-------------|----------------|
| ResNet50 | ResNet50 v1.5 with bottleneck blocks | 78.6% |
| ResNeXt101-32x4d | ResNeXt with cardinality=32, bottleneck width=4 | 80.4% |
| SE-ResNeXt101-32x4d | ResNeXt with Squeeze-and-Excitation blocks | 81.0% |
| EfficientNet-B0 | EfficientNet baseline model | 77.6% |
| EfficientNet-B4 | EfficientNet wider/deeper variant | 83.0% |
| EfficientNet-WideSE-B0 | EfficientNet with wider SE layers | 77.9% |
| EfficientNet-WideSE-B4 | EfficientNet-B4 with wider SE layers | 83.3% |

Sources: [PyTorch/Classification/ConvNets/README.md:40-50](), [hubconf.py:7-13]()

### ResNet Architecture

The ResNet/ResNeXt family implements residual blocks with skip connections:

```mermaid
flowchart TD
    subgraph "ResNet Architecture"
        ResNetModel["ResNet Class"] --> Stem["Stem Layer\n(Conv7x7, BN, ReLU, MaxPool)"]
        Stem --> Layers["Layer Blocks 1-4"]
        Layers --> AvgPool["Global Average Pooling"]
        AvgPool --> FC["Fully Connected"]
        
        subgraph "Block Types"
            BasicBlock["BasicBlock\n(Conv3x3 → BN → ReLU → Conv3x3 → BN)"]
            Bottleneck["Bottleneck\n(Conv1x1 → BN → ReLU → Conv3x3 → BN → ReLU → Conv1x1 → BN)"]
            SEBottleneck["SEBottleneck\n(Bottleneck + Squeeze-and-Excitation)"]
        end
    end
```

Sources: [PyTorch/Classification/ConvNets/image_classification/models/resnet.py:56-407]()

### EfficientNet Architecture

EfficientNet models use compound scaling and mobile inverted bottleneck blocks:

```mermaid
flowchart TD
    subgraph "EfficientNet Architecture"
        EfficientNet["EfficientNet Class"] --> EfficientNetStem["Stem\n(Conv3x3, BN, SiLU)"]
        EfficientNetStem --> MBBlocks["Mobile Inverted Bottleneck Blocks"]
        MBBlocks --> Head["Head\n(Conv1x1, BN, SiLU, AvgPool, FC)"]
        
        subgraph "MBConv Block"
            DepthwiseConv["Depthwise Conv"]
            PointwiseConv["Pointwise Conv (Expansion)"]
            SEModule["Squeeze-and-Excitation"]
            ProjectConv["Projection Conv"]
            SkipConnection["Skip Connection"]
        end
    end
```

Sources: [PyTorch/Classification/ConvNets/image_classification/models/efficientnet.py:1-100]()

## Speech Synthesis Models

The repository includes state-of-the-art speech synthesis models:

1. **Tacotron2**: Neural text-to-speech model that generates mel-spectrograms from text
2. **WaveGlow**: Flow-based neural vocoder for high-quality audio generation
3. **FastPitch**: Fast, parallel text-to-speech model with explicit pitch control
4. **HiFi-GAN**: GAN-based neural vocoder for efficient, high-fidelity audio synthesis

Sources: [hubconf.py:23-31]()

## Model Optimization Features

### Mixed Precision Training

All models support mixed precision training using Automatic Mixed Precision (AMP):

```mermaid
flowchart TD
    MixedPrecision["Mixed Precision Training"]
    MixedPrecision --> AMPInitialize["Initialize model with AMP\nmodel, optimizer = amp.initialize()"]
    AMPInitialize --> ForwardPass["Forward Pass in FP16\nautocast(enabled=self.amp)"]
    ForwardPass --> ScaleLoss["Scale Loss\nscaler.scale_loss(loss)"]
    ScaleLoss --> Backward["Backward Pass"]
    Backward --> ScalerStep["Scaler Step\nscaler.step(optimizer)\nscaler.update()"]
```

Sources: [PyTorch/Classification/ConvNets/image_classification/training.py:90-105]()

Mixed precision training features:
- Uses `torch.cuda.amp` package for automatic mixed precision
- Implements dynamic loss scaling to prevent underflow
- Optimized NHWC memory format for Tensor Core acceleration
- TF32 precision support for NVIDIA Ampere GPUs

### Distributed Training

The repository provides robust distributed training support:

```mermaid
flowchart TD
    DistTraining["Distributed Training"]
    DistTraining --> DDP["DistributedDataParallel"]
    DistTraining --> DistSampler["DistributedSampler"]
    DistTraining --> AllReduce["All-Reduce for Metrics"]
    
    DDP --> GradSync["Synchronized Gradient Updates"]
    DistSampler --> DataPartition["Data Partitioning"]
    AllReduce --> GlobalMetrics["Global Metrics Computation"]
```

Sources: [PyTorch/Classification/ConvNets/main.py:360-374](), [PyTorch/Classification/ConvNets/image_classification/training.py:230-233]()

Key distributed training features:
- PyTorch DistributedDataParallel for gradient synchronization
- Multi-GPU and multi-node scaling
- Synchronized batch normalization
- Distributed data sampling

### Optimization Techniques

The repository implements numerous optimization techniques for improved performance and accuracy:

| Technique | Description | Implementation |
|-----------|-------------|----------------|
| Automatic Mixed Precision | FP16/FP32 mixed precision | `torch.cuda.amp` |
| DALI Data Loading | GPU-accelerated data loading | `nvidia.dali` integration |
| EMA | Exponential moving average of weights | `EMA` class |
| Label Smoothing | Softens one-hot labels | `LabelSmoothing` class |
| MixUp | Training on convex combinations of samples | `MixUpWrapper` class |
| Learning Rate Scheduling | Cosine, linear, step schedules | `lr_*_policy` functions |
| Weight Decay | Configurable regularization | Optimizer options |

Sources: [PyTorch/Classification/ConvNets/main.py:92-207](), [PyTorch/Classification/ConvNets/image_classification/training.py:137-152]()

## Model Deployment Options

The repository supports multiple deployment paths:

```mermaid
flowchart TD
    Model["PyTorch Model"] --> Checkpoint["Save Checkpoint\n.pth.tar"]
    Checkpoint --> Export["Export Options"]
    
    Export --> TorchScript["TorchScript\n--jit script"]
    Export --> ONNX["ONNX Export\nmodel2onnx.py"]
    Export --> TensorRT["TensorRT Conversion"]
    
    TorchScript --> ProductionServing["Production Serving"]
    ONNX --> Triton["Triton Inference Server"]
    TensorRT --> HighPerformance["High-Performance Inference"]
    
    Model --> Quantization["Quantization\nquant_main.py"]
    Quantization --> INT8Model["INT8 Model"]
    INT8Model --> QuantONNX["INT8 ONNX Export"]
```

Sources: [PyTorch/Classification/ConvNets/triton/deployer.py:1-106](), [PyTorch/Classification/ConvNets/model2onnx.py:1-45](), [PyTorch/Classification/ConvNets/quant_main.py:1-40]()

Deployment features:
- TorchScript export for production deployment
- ONNX export for cross-platform inference
- Quantization-aware training for INT8 precision
- Triton Inference Server integration
- TensorRT optimization

## Training Process

The standard training flow follows this pattern:

```mermaid
flowchart TD
    Config["Configuration:\n--arch, --batch-size, --lr, etc."] --> Setup["Setup:\nDistributed, AMP, Model, Optimizer"]
    Setup --> DataLoaders["Initialize Data Loaders"]
    DataLoaders --> TrainLoop["Main Training Loop"]
    
    TrainLoop --> Epoch["For each epoch"]
    Epoch --> TrainStep["Train Step:\nForward, Backward, Optimize"]
    Epoch --> Validate["Validate"]
    Validate --> Checkpoint["Save Checkpoint"]
    
    TrainStep --> NextEpoch["Next Epoch or Early Stop"]
    Validate --> NextEpoch
    Checkpoint --> NextEpoch
    
    NextEpoch --> |"Done"| FinalModel["Final Model"]
```

Sources: [PyTorch/Classification/ConvNets/main.py:611-649](), [PyTorch/Classification/ConvNets/image_classification/training.py:313-435]()

## Conclusion

The PyTorch model implementations in this repository provide optimized, production-ready training and inference code for various deep learning tasks. They feature:

1. Common infrastructure for model definition, training, and evaluation
2. State-of-the-art architectures across different domains
3. Optimizations for mixed precision, distributed training, and data loading
4. Multiple deployment paths including TorchScript, ONNX, and TensorRT

Each model family has its own dedicated directory with detailed documentation, training scripts, and performance benchmarks.

---

