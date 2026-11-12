<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/EdgeML · page 3 Implementation Frameworks · fetched 2026-10-26 -->

# Implementation Frameworks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/pytorch/DROCC/README.md](examples/pytorch/DROCC/README.md)
- [examples/pytorch/DROCC/data_process_scripts/process_cifar.py](examples/pytorch/DROCC/data_process_scripts/process_cifar.py)
- [examples/pytorch/DROCC/data_process_scripts/process_mnist.py](examples/pytorch/DROCC/data_process_scripts/process_mnist.py)
- [examples/pytorch/DROCC/main_cifar.py](examples/pytorch/DROCC/main_cifar.py)
- [examples/pytorch/DROCC/main_drocclf_mnist.py](examples/pytorch/DROCC/main_drocclf_mnist.py)
- [examples/pytorch/DROCC/main_tabular.py](examples/pytorch/DROCC/main_tabular.py)
- [examples/pytorch/DROCC/main_timeseries.py](examples/pytorch/DROCC/main_timeseries.py)
- [examples/pytorch/FastCells/fastcell_example.py](examples/pytorch/FastCells/fastcell_example.py)
- [examples/pytorch/FastCells/helpermethods.py](examples/pytorch/FastCells/helpermethods.py)
- [pytorch/README.md](pytorch/README.md)
- [pytorch/edgeml_pytorch/cuda/fastgrnn_cuda.cpp](pytorch/edgeml_pytorch/cuda/fastgrnn_cuda.cpp)
- [pytorch/edgeml_pytorch/cuda/fastgrnn_cuda_kernel.cu](pytorch/edgeml_pytorch/cuda/fastgrnn_cuda_kernel.cu)
- [pytorch/edgeml_pytorch/cuda/setup.py](pytorch/edgeml_pytorch/cuda/setup.py)
- [pytorch/edgeml_pytorch/graph/rnn.py](pytorch/edgeml_pytorch/graph/rnn.py)
- [pytorch/edgeml_pytorch/trainer/drocc_trainer.py](pytorch/edgeml_pytorch/trainer/drocc_trainer.py)
- [pytorch/edgeml_pytorch/trainer/drocclf_trainer.py](pytorch/edgeml_pytorch/trainer/drocclf_trainer.py)
- [pytorch/edgeml_pytorch/utils.py](pytorch/edgeml_pytorch/utils.py)
- [pytorch/setup.py](pytorch/setup.py)
- [tf/README.md](tf/README.md)

</details>



This document provides an overview of the different implementation frameworks available in EdgeML and their capabilities. EdgeML offers multiple implementation options to support different development environments, deployment targets, and performance requirements.

For detailed information about specific algorithms, see [Core Algorithms](#2). For deployment and optimization techniques, see [Deployment and Optimization](#5).

## Framework Overview

EdgeML provides four distinct implementation frameworks, each optimized for different use cases:

```mermaid
graph TB
    subgraph "EdgeML Implementation Frameworks"
        PT["PyTorch Implementation<br/>pytorch/edgeml_pytorch"]
        TF["TensorFlow Implementation<br/>tf/edgeml_tf"]
        CPP["C++ Implementation<br/>cpp/"]
        CREF["C Reference Implementation<br/>c_reference/"]
    end
    
    subgraph "Capabilities"
        PT --> PT_CAP["• Research & Development<br/>• CUDA Acceleration<br/>• DROCC, FastCells, SRNN<br/>• ONNX Export"]
        TF --> TF_CAP["• Production Deployment<br/>• TensorFlow Lite<br/>• Bonsai, ProtoNN, FastCells<br/>• Mobile Optimization"]
        CPP --> CPP_CAP["• High Performance Training<br/>• Bonsai & ProtoNN<br/>• Cross-platform"]
        CREF --> CREF_CAP["• Edge Inference<br/>• Quantized Operations<br/>• Ultra-low Memory<br/>• Fixed-point Arithmetic"]
    end
    
    subgraph "Target Environments"
        PT_CAP --> ENV1["GPU Clusters<br/>Research Labs"]
        TF_CAP --> ENV2["Mobile Devices<br/>Production Systems"]
        CPP_CAP --> ENV3["Server Deployment<br/>Enterprise Systems"]
        CREF_CAP --> ENV4["Microcontrollers<br/>IoT Devices"]
    end
```

**Sources:** [README.md:36-45](), [pytorch/README.md:1-42](), [tf/README.md:1-17]()

## Algorithm Support Matrix

The following table shows which algorithms are supported by each framework:

| Algorithm | PyTorch | TensorFlow | C++ | C Reference |
|-----------|---------|------------|-----|-------------|
| **DROCC** | ✓ | ✗ | ✗ | ✗ |
| **FastRNN/FastGRNN** | ✓ | ✓ | ✗ | ✓ |
| **Bonsai** | ✓ | ✓ | ✓ | ✗ |
| **ProtoNN** | ✓ | ✓ | ✓ | ✗ |
| **EMI-RNN** | ✗ | ✓ | ✗ | ✗ |
| **SRNN** | ✓ | ✗ | ✗ | ✗ |
| **RNNPool** | ✓ | ✗ | ✗ | ✓ |
| **CUDA Acceleration** | ✓ | ✗ | ✗ | ✗ |
| **Quantization** | ✗ | ✓ | ✗ | ✓ |
| **Mobile Export** | ONNX | TFLite | ✗ | ✓ |

**Sources:** [pytorch/README.md:8-39](), [tf/README.md:5-11]()

## Core Components Architecture

```mermaid
graph TB
    subgraph "PyTorch Framework"
        PT_GRAPH["edgeml_pytorch.graph<br/>• rnn.py<br/>• bonsai.py<br/>• protoNN.py"]
        PT_TRAINER["edgeml_pytorch.trainer<br/>• drocc_trainer.py<br/>• fastTrainer.py<br/>• bonsaiTrainer.py"]
        PT_CUDA["edgeml_pytorch.cuda<br/>• fastgrnn_cuda.cpp<br/>• fastgrnn_cuda_kernel.cu"]
        PT_UTILS["edgeml_pytorch.utils<br/>• findCUDA()<br/>• hardThreshold()"]
    end
    
    subgraph "TensorFlow Framework"
        TF_GRAPH["edgeml_tf.graph<br/>• rnn.py<br/>• bonsai.py<br/>• protoNN.py"]
        TF_TRAINER["edgeml_tf.trainer<br/>• bonsaiTrainer.py<br/>• protoNNTrainer.py"]
        TF_EXPORT["TensorFlow Lite<br/>• bonsai_model_to_tflite.py<br/>• Mobile Deployment"]
    end
    
    subgraph "C++ Framework"
        CPP_BONSAI["Bonsai Implementation<br/>• Training & Inference<br/>• Cross-platform"]
        CPP_PROTONN["ProtoNN Implementation<br/>• Training & Inference<br/>• High Performance"]
    end
    
    subgraph "C Reference Framework"
        CREF_QUANT["Quantized Operations<br/>• quantized_fastgrnn.c<br/>• quantized_rnnpool.c<br/>• quantized_utils.c"]
        CREF_APP["Applications<br/>• Face Detection<br/>• Gesture Recognition"]
    end
    
    PT_GRAPH --> PT_TRAINER
    PT_CUDA --> PT_GRAPH
    PT_UTILS --> PT_GRAPH
    
    TF_GRAPH --> TF_TRAINER
    TF_GRAPH --> TF_EXPORT
```

**Sources:** [pytorch/edgeml_pytorch/graph/rnn.py:1-50](), [pytorch/edgeml_pytorch/trainer/drocc_trainer.py:1-30](), [pytorch/edgeml_pytorch/cuda/fastgrnn_cuda.cpp:1-20]()

## PyTorch Implementation Details

The PyTorch implementation serves as the primary research and development framework, offering the most comprehensive algorithm support and advanced features.

### Core RNN Architecture

```mermaid
graph TB
    subgraph "RNN Cell Hierarchy"
        RNNBASE["RNNCell<br/>(Base Class)"]
        FASTGRNN["FastGRNNCell"]
        FASTGRNN_CUDA["FastGRNNCUDACell"]
        FASTRNN["FastRNNCell"]
        LSTM_LR["LSTMLRCell"]
        GRU_LR["GRULRCell"]
        UGRNN_LR["UGRNNLRCell"]
    end
    
    subgraph "Key Methods"
        FORWARD["forward(input, state)"]
        GETVARS["getVars()"]
        SPARSIFY["sparsify()"]
        MODELSIZE["get_model_size()"]
    end
    
    subgraph "RNN Unroller"
        BASERNN["BaseRNN"]
        BIDIR["Bidirectional Support"]
        BATCH_FIRST["Batch First Option"]
    end
    
    RNNBASE --> FASTGRNN
    RNNBASE --> FASTGRNN_CUDA  
    RNNBASE --> FASTRNN
    RNNBASE --> LSTM_LR
    RNNBASE --> GRU_LR
    RNNBASE --> UGRNN_LR
    
    FASTGRNN --> FORWARD
    FASTGRNN --> GETVARS
    FASTGRNN --> SPARSIFY
    FASTGRNN --> MODELSIZE
    
    BASERNN --> BIDIR
    BASERNN --> BATCH_FIRST
```

**Sources:** [pytorch/edgeml_pytorch/graph/rnn.py:76-198](), [pytorch/edgeml_pytorch/graph/rnn.py:199-318](), [pytorch/edgeml_pytorch/graph/rnn.py:966-1020]()

### CUDA Acceleration Components

The PyTorch implementation includes optimized CUDA kernels for FastGRNN operations:

```mermaid
graph LR
    subgraph "CUDA Implementation"
        KERNEL["fastgrnn_cuda_kernel.cu<br/>• Forward/Backward Kernels<br/>• Sigmoid/ReLU/Tanh Support"]
        WRAPPER["fastgrnn_cuda.cpp<br/>• Python Bindings<br/>• Input Validation"]
        SETUP["setup.py<br/>• Build Configuration<br/>• CUDA Detection"]
    end
    
    subgraph "PyTorch Integration"
        CELL["FastGRNNCUDACell"]
        FUNCTION["FastGRNNFunction"]
        AUTOGRAD["Autograd Support"]
    end
    
    subgraph "Operations"
        FWD["fastgrnn_cuda_forward"]
        BWD["fastgrnn_cuda_backward"]
        UNROLL_FWD["fastgrnn_unroll_cuda_forward"]
        UNROLL_BWD["fastgrnn_unroll_cuda_backward"]
    end
    
    KERNEL --> WRAPPER
    WRAPPER --> SETUP
    SETUP --> CELL
    CELL --> FUNCTION
    FUNCTION --> AUTOGRAD
    
    WRAPPER --> FWD
    WRAPPER --> BWD
    WRAPPER --> UNROLL_FWD
    WRAPPER --> UNROLL_BWD
```

**Sources:** [pytorch/edgeml_pytorch/cuda/fastgrnn_cuda_kernel.cu:1-50](), [pytorch/edgeml_pytorch/cuda/fastgrnn_cuda.cpp:1-50](), [pytorch/edgeml_pytorch/cuda/setup.py:1-19]()

### DROCC Training Framework

The PyTorch implementation provides the only available implementation of the DROCC algorithm:

```mermaid
graph TB
    subgraph "DROCC Training Pipeline"
        TRAINER["DROCCTrainer"]
        MODEL["Neural Network Model"]
        OPTIMIZER["torch.optim Optimizer"]
    end
    
    subgraph "Loss Components"
        CE_LOSS["Binary Cross Entropy Loss"]
        ADV_LOSS["Adversarial Loss"]
        COMBINED["Combined Loss = CE + λ * ADV"]
    end
    
    subgraph "Adversarial Generation"
        SAMPLE["Random Sampling around Data"]
        ASCENT["Gradient Ascent Steps"]
        PROJECT["Projection to N_i(r)"]
    end
    
    TRAINER --> MODEL
    TRAINER --> OPTIMIZER
    TRAINER --> CE_LOSS
    TRAINER --> ADV_LOSS
    
    ADV_LOSS --> SAMPLE
    SAMPLE --> ASCENT
    ASCENT --> PROJECT
    
    CE_LOSS --> COMBINED
    ADV_LOSS --> COMBINED
```

**Sources:** [pytorch/edgeml_pytorch/trainer/drocc_trainer.py:10-35](), [pytorch/edgeml_pytorch/trainer/drocc_trainer.py:158-214]()

## TensorFlow Implementation Details

The TensorFlow implementation focuses on production deployment and mobile optimization, with built-in support for TensorFlow Lite conversion.

### Framework Structure

```mermaid
graph TB
    subgraph "TensorFlow Implementation"
        TF_GRAPH["edgeml_tf.graph<br/>• Algorithm Implementations"]
        TF_TRAINER["edgeml_tf.trainer<br/>• Training Routines"]
        TF_EXAMPLES["examples/tf<br/>• Usage Examples"]
    end
    
    subgraph "Supported Algorithms"
        BONSAI_TF["Bonsai<br/>Tree-based Classifier"]
        PROTONN_TF["ProtoNN<br/>Prototype k-NN"]
        FASTCELLS_TF["FastRNN & FastGRNN<br/>Fast RNN Cells"]
        EMI_RNN["EMI-RNN<br/>Time Series RNN"]
    end
    
    subgraph "Deployment Features"
        TFLITE["TensorFlow Lite Export"]
        QUANTIZATION["Post-training Quantization"]
        MOBILE["Mobile Optimization"]
    end
    
    TF_GRAPH --> BONSAI_TF
    TF_GRAPH --> PROTONN_TF
    TF_GRAPH --> FASTCELLS_TF
    TF_GRAPH --> EMI_RNN
    
    TF_TRAINER --> TFLITE
    TFLITE --> QUANTIZATION
    QUANTIZATION --> MOBILE
```

**Sources:** [tf/README.md:5-14](), [tf/README.md:17-48]()

## C++ Implementation Details

The C++ implementation provides high-performance training and inference for Bonsai and ProtoNN algorithms, designed for server deployment and enterprise systems.

```mermaid
graph LR
    subgraph "C++ Framework"
        CPP_DIR["cpp/ Directory"]
        BONSAI_CPP["Bonsai Implementation"]
        PROTONN_CPP["ProtoNN Implementation"]
    end
    
    subgraph "Capabilities"
        TRAINING["High-Performance Training"]
        INFERENCE["Optimized Inference"]
        CROSS_PLATFORM["Cross-Platform Support"]
    end
    
    subgraph "Use Cases"
        SERVER["Server Deployment"]
        ENTERPRISE["Enterprise Systems"]
        STANDALONE["Standalone Applications"]
    end
    
    CPP_DIR --> BONSAI_CPP
    CPP_DIR --> PROTONN_CPP
    
    BONSAI_CPP --> TRAINING
    PROTONN_CPP --> TRAINING
    TRAINING --> INFERENCE
    INFERENCE --> CROSS_PLATFORM
    
    CROSS_PLATFORM --> SERVER
    CROSS_PLATFORM --> ENTERPRISE
    CROSS_PLATFORM --> STANDALONE
```

**Sources:** [README.md:41]()

## C Reference Implementation Details

The C reference implementation provides quantized inference optimized for edge devices and microcontrollers with severe memory constraints.

### Quantization Architecture

```mermaid
graph TB
    subgraph "C Reference Components"
        FASTGRNN_C["quantized_fastgrnn.c"]
        RNNPOOL_C["quantized_rnnpool.c"]
        MBCONV_C["quantized_mbconv.c"]
        UTILS_C["quantized_utils.c"]
    end
    
    subgraph "Data Types"
        Q7["Q7_T (int8_t)<br/>-128 to 127"]
        Q15["Q15_T (int16_t)<br/>-32768 to 32767"]
        SCALE["SCALE_T (int32_t)<br/>Scaling Operations"]
    end
    
    subgraph "Applications"
        FACE_DETECT["Face Detection"]
        GESTURE["Gesture Recognition"]
        IOT["IoT Applications"]
    end
    
    subgraph "Optimization Features"
        FIXED_POINT["Fixed-Point Arithmetic"]
        LOW_MEMORY["Ultra-Low Memory"]
        SIMD["SIMD Optimization"]
    end
    
    FASTGRNN_C --> Q7
    FASTGRNN_C --> Q15
    RNNPOOL_C --> Q15
    MBCONV_C --> Q7
    UTILS_C --> SCALE
    
    Q7 --> FIXED_POINT
    Q15 --> FIXED_POINT
    SCALE --> FIXED_POINT
    
    FIXED_POINT --> LOW_MEMORY
    LOW_MEMORY --> SIMD
    
    SIMD --> FACE_DETECT
    SIMD --> GESTURE
    SIMD --> IOT
```

**Sources:** [README.md:44]()

## Training to Deployment Pipeline

```mermaid
flowchart TD
    subgraph "Development Phase"
        RESEARCH["Research & Prototyping<br/>PyTorch Implementation"]
        CUDA_DEV["CUDA Acceleration<br/>FastGRNNCUDACell"]
    end
    
    subgraph "Production Training"
        TF_TRAIN["TensorFlow Training<br/>Production Models"]
        CPP_TRAIN["C++ Training<br/>High Performance"]
    end
    
    subgraph "Model Export"
        PYTORCH_EXPORT["PyTorch → ONNX"]
        TF_EXPORT["TensorFlow → TFLite"]
        SEEDOT["SeeDot Quantization<br/>Float → Fixed Point"]
    end
    
    subgraph "Deployment Targets"
        MOBILE["Mobile Devices<br/>TensorFlow Lite"]
        CROSS_PLATFORM["Cross-Platform<br/>ONNX Runtime"]
        EDGE["Edge Devices<br/>C Reference"]
        MICROCONTROLLER["Microcontrollers<br/>Quantized C"]
    end
    
    RESEARCH --> CUDA_DEV
    RESEARCH --> TF_TRAIN
    RESEARCH --> CPP_TRAIN
    
    CUDA_DEV --> PYTORCH_EXPORT
    TF_TRAIN --> TF_EXPORT
    CPP_TRAIN --> SEEDOT
    
    PYTORCH_EXPORT --> CROSS_PLATFORM
    TF_EXPORT --> MOBILE
    SEEDOT --> EDGE
    SEEDOT --> MICROCONTROLLER
```

**Sources:** [README.md:29-44](), [pytorch/README.md:41-78](), [tf/README.md:17-48]()

## Framework Selection Guidelines

| Use Case | Recommended Framework | Key Benefits |
|----------|----------------------|--------------|
| **Research & Development** | PyTorch | Complete algorithm support, CUDA acceleration, flexible experimentation |
| **Mobile Applications** | TensorFlow | TensorFlow Lite integration, mobile optimization |
| **High-Performance Training** | C++ | Optimized performance, enterprise deployment |
| **Edge/IoT Deployment** | C Reference | Quantized operations, minimal memory footprint |
| **Cross-Platform Inference** | PyTorch → ONNX | Wide runtime support, standardized format |
| **Microcontroller Deployment** | C Reference | Fixed-point arithmetic, ultra-low power |

**Sources:** [README.md:36-45](), [pytorch/README.md:44-78](), [tf/README.md:17-33]()

---

