<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/EdgeML · page 2 Core Algorithms · fetched 2026-10-26 -->

# Core Algorithms

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



This document provides an overview of the machine learning algorithms implemented in EdgeML, their characteristics, and implementation architecture. These algorithms are specifically designed for resource-constrained edge devices with emphasis on model size, inference speed, and energy efficiency.

For detailed algorithm-specific documentation, see: [DROCC](#2.1), [FastCells](#2.2), [Bonsai and ProtoNN](#2.3), and [Other Algorithms](#2.4). For training examples and usage, see [Training and Examples](#4). For deployment considerations, see [Deployment and Optimization](#5).

## Algorithm Categories

EdgeML implements algorithms across three main categories, each targeting different machine learning paradigms while maintaining resource efficiency:

```mermaid
graph TB
    subgraph "EdgeML Core Algorithms"
        subgraph "Sequence Modeling"
            FastRNN["FastRNNCell"]
            FastGRNN["FastGRNNCell"] 
            FastGRNNCUDA["FastGRNNCUDACell"]
            EMIRNN["EMI-RNN"]
            SRNN["SRNN2"]
            RNNPool["RNNPool"]
        end
        
        subgraph "Classification"
            Bonsai["Bonsai"]
            ProtoNN["ProtoNN"]
        end
        
        subgraph "Anomaly Detection"
            DROCC["DROCCTrainer"]
            DROCCLF["DROCCLFTrainer"]
        end
        
        subgraph "Supporting Components"
            BaseRNN["BaseRNN"]
            LowRankRNNs["LSTMLRCell, GRULRCell, UGRNNLRCell"]
        end
    end
    
    FastRNN --> BaseRNN
    FastGRNN --> BaseRNN
    LowRankRNNs --> BaseRNN
```

**Sources:** [README.md:14-21](), [pytorch/edgeml_pytorch/graph/rnn.py:966-1043]()

## Key Algorithm Characteristics

All EdgeML algorithms share common design principles optimized for edge deployment:

| Characteristic | Implementation | Benefit |
|---|---|---|
| **Low-Rank Parameterization** | `wRank`, `uRank` parameters in RNN cells | Reduces parameter count |
| **Sparsity Control** | `wSparsity`, `uSparsity` with `hardThreshold()` | Further compression |
| **Quantization Support** | Fixed-point arithmetic via SeeDot | Memory and compute efficiency |
| **Custom Non-linearities** | `quantTanh`, `quantSigm` in `gen_nonlinearity()` | Hardware-friendly activations |

**Sources:** [pytorch/edgeml_pytorch/graph/rnn.py:76-143](), [pytorch/edgeml_pytorch/utils.py:73-84]()

## Implementation Architecture

The EdgeML codebase implements algorithms across multiple frameworks with consistent interfaces:

```mermaid
graph LR
    subgraph "Algorithm Classes"
        FastGRNNCell["FastGRNNCell<br/>pytorch/edgeml_pytorch/graph/rnn.py:199"]
        FastRNNCell["FastRNNCell<br/>pytorch/edgeml_pytorch/graph/rnn.py:416"]
        DROCCTrainer["DROCCTrainer<br/>pytorch/edgeml_pytorch/trainer/drocc_trainer.py:11"]
        BaseRNN["BaseRNN<br/>pytorch/edgeml_pytorch/graph/rnn.py:966"]
    end
    
    subgraph "Training Infrastructure"
        FastTrainer["FastTrainer<br/>edgeml_pytorch.trainer.fastTrainer"]
        Optimizers["Adam, SGD with<br/>learning rate scheduling"]
    end
    
    subgraph "Acceleration"
        CUDA["FastGRNNCUDACell<br/>pytorch/edgeml_pytorch/cuda/"]
        CPP["C++ implementations<br/>cpp/"]
        CRef["C Reference<br/>c_reference/"]
    end
    
    FastGRNNCell --> FastTrainer
    FastRNNCell --> FastTrainer
    DROCCTrainer --> Optimizers
    FastGRNNCell --> CUDA
    BaseRNN --> CPP
    FastGRNNCell --> CRef
```

**Sources:** [pytorch/edgeml_pytorch/graph/rnn.py:199-318](), [examples/pytorch/FastCells/fastcell_example.py:84-86](), [pytorch/edgeml_pytorch/cuda/setup.py:7-18]()

## Framework Support Matrix

Different algorithms have varying levels of support across EdgeML's implementation frameworks:

| Algorithm | PyTorch | TensorFlow | C++ | C Reference | CUDA |
|---|---|---|---|---|---|
| **FastGRNN** | ✓ `FastGRNNCell` | ✓ | ✗ | ✓ `quantized_fastgrnn.c` | ✓ `FastGRNNCUDACell` |
| **FastRNN** | ✓ `FastRNNCell` | ✓ | ✗ | ✗ | ✗ |
| **DROCC** | ✓ `DROCCTrainer` | ✗ | ✗ | ✗ | ✗ |
| **Bonsai** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **ProtoNN** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **RNNPool** | ✓ | ✗ | ✗ | ✓ `quantized_rnnpool.c` | ✗ |

**Sources:** [README.md:36-44](), [pytorch/README.md:18-39](), [tf/README.md:5-11]()

## Algorithm Selection Guide

Choose algorithms based on your specific use case and constraints:

```mermaid
flowchart TD
    Start["Machine Learning Task"] --> TaskType{"Task Type?"}
    
    TaskType -->|"Time Series/Sequential"| SeqModeling["Sequence Modeling"]
    TaskType -->|"Classification"| Classification["Classification"]
    TaskType -->|"Anomaly Detection"| AnomalyDet["Anomaly Detection"]
    
    SeqModeling --> Memory{"Memory Constraints?"}
    Memory -->|"Severe"| FastRNN["FastRNNCell<br/>Simplest architecture"]
    Memory -->|"Moderate"| FastGRNN["FastGRNNCell<br/>Gated architecture"]
    Memory -->|"GPU Available"| FastGRNNCUDA["FastGRNNCUDACell<br/>CUDA acceleration"]
    
    Classification --> DataSize{"Dataset Size?"}
    DataSize -->|"Small/Medium"| Bonsai["Bonsai<br/>Tree-based classifier"]
    DataSize -->|"Large"| ProtoNN["ProtoNN<br/>Prototype-based kNN"]
    
    AnomalyDet --> NegativeData{"Negative Examples?"}
    NegativeData -->|"None"| DROCC["DROCCTrainer<br/>One-class classification"]
    NegativeData -->|"Limited"| DROCCLF["DROCCLFTrainer<br/>Limited negatives variant"]
```

**Sources:** [README.md:14-21](), [pytorch/edgeml_pytorch/trainer/drocc_trainer.py:11-34](), [pytorch/edgeml_pytorch/trainer/drocclf_trainer.py:185-210]()

## Low-Rank Parameterization

A key innovation across EdgeML algorithms is low-rank matrix decomposition to reduce model parameters:

```mermaid
graph LR
    subgraph "Standard RNN"
        X1["Input x_t"] --> W1["W matrix<br/>input_size × hidden_size"]
        H1["Hidden h_{t-1}"] --> U1["U matrix<br/>hidden_size × hidden_size"]
        W1 --> Add1["+"]
        U1 --> Add1
    end
    
    subgraph "Low-Rank RNN"
        X2["Input x_t"] --> W1_2["W1 matrix<br/>input_size × wRank"]
        W1_2 --> W2_2["W2 matrix<br/>wRank × hidden_size"]
        H2["Hidden h_{t-1}"] --> U1_2["U1 matrix<br/>hidden_size × uRank"]
        U1_2 --> U2_2["U2 matrix<br/>uRank × hidden_size"]
        W2_2 --> Add2["+"]
        U2_2 --> Add2
    end
```

**Sources:** [pytorch/edgeml_pytorch/graph/rnn.py:253-263](), [pytorch/edgeml_pytorch/graph/rnn.py:280-291]()

---

