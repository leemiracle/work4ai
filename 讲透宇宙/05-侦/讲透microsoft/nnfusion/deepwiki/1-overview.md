<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/nnfusion · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/README.md](docs/README.md)

</details>



## Purpose and Scope

NNFusion is a flexible and efficient Deep Neural Network (DNN) compiler that generates high-performance executables from DNN model descriptions. This page provides a comprehensive overview of the NNFusion system architecture, its key components, and the workflow from model input to optimized code generation. For detailed information about specific subsystems, please refer to their respective wiki pages.

For model importing specifics, see [Frontend Systems](#2). For information about the internal representation, see [Core IR and Graph Representation](#3).

## What is NNFusion?

NNFusion is an optimizing compiler for deep learning models that takes models defined in frameworks like TensorFlow, ONNX, or PyTorch and generates highly efficient executable code tailored for specific hardware targets. It employs various compiler optimization techniques to improve performance beyond what's typically achievable with standard deep learning frameworks.

```mermaid
graph TB
    subgraph "NNFusion Compiler Pipeline"
        A["Input Models<br>(TensorFlow/ONNX/PyTorch)"] --> B["Frontend Import"]
        B --> C["IR Graph Representation"]
        C --> D["Graph Optimization"]
        D --> E["Code Generation"]
        E --> F["Backend-specific Runtime<br>(CUDA/CPU/HLSL/ROCm)"]
    end
```

Sources: [README.md:1-23]()

## Key Objectives

NNFusion aims to achieve three primary goals:

1. **Full-stack Model Optimization**: Applying optimizations at different levels of abstraction, from graph-level to hardware-specific kernel tuning.
2. **Framework-free Code Generation**: Removing dependencies on deep learning frameworks for inference, reducing runtime overhead.
3. **Flexible Target Support**: Enabling deployment on various accelerator devices beyond just standard GPUs.

## System Architecture

NNFusion employs a modular architecture following the traditional compiler design pattern with frontend, intermediate representation, optimization, and backend components. The following diagram illustrates the high-level architecture:

```mermaid
graph TD
    A["Input Models<br>TensorFlow/ONNX/PyTorch"] --> B["Frontend Import Layer"]
    B --> C["IR Graph Representation"]
    C --> D["Graph Optimization Passes"]
    D --> C
    C --> E["Code Generation"]
    E --> F["Backend-specific Runtime<br>CUDA/CPU/HLSL/ROCm"]
    
    subgraph "Frontend Systems"
        B1["ONNX Importer"]
        B2["TensorFlow Importer"]
        B3["PyTorch Converter"]
    end
    
    subgraph "Core IR & Graph"
        C1["GNode Graph"]
        C2["Generic Operators"]
        C3["Tensor Descriptors"]
    end
    
    subgraph "Optimization Passes"
        D1["Kernel Tuning"]
        D2["Kernel Fusion"]
        D3["Block Fusion"]
        D4["AutoDiff"]
    end
    
    subgraph "Code Generation"
        E1["CUDA Codegen"]
        E2["CPU Codegen"]
        E3["HLSL Codegen"]
        E4["ROCm Codegen"]
    end

    B --- B1
    B --- B2
    B --- B3
    C --- C1
    C --- C2
    C --- C3
    D --- D1
    D --- D2
    D --- D3
    D --- D4
    E --- E1
    E --- E2
    E --- E3
    E --- E4
```

Sources: [README.md:14-21]()

## Key Components

### Frontend Import Systems

The frontend subsystem is responsible for importing models from various deep learning frameworks and converting them to NNFusion's internal representation.

```mermaid
graph LR
    subgraph "Input Models"
        A1["TensorFlow Model"]
        A2["ONNX Model"]
        A3["PyTorch Model"]
    end
    
    subgraph "Frontend Layer"
        B1["ONNX Importer"]
        B2["TensorFlow Importer"]
        B3["PyTorch to ONNX Converter"]
        B4["OperatorsBridge"]
    end
    
    subgraph "IR Layer"
        C1["NNFusion Graph"]
        C2["GNodes"]
        C3["GenericOp"]
    end
    
    A1 --> B2
    A2 --> B1
    A3 --> B3
    B3 --> B1
    B1 --> B4
    B2 --> B4
    B4 --> C1
    C1 --> C2
    C2 --> C3
```

For detailed information about each frontend, refer to the [Frontend Systems](#2) page.

Sources: [README.md:19]()

### Core IR and Graph Representation

NNFusion uses a graph-based intermediate representation (IR) to capture the computational nature of deep learning models. The core components include:

- **GNode Graph**: Represents the dataflow graph of operations
- **Generic Operators**: Framework-agnostic representation of neural network operations
- **Tensor Descriptors**: Metadata about tensors including shape, data type, and memory layout

For more detailed information about the internal representation, see [Core IR and Graph Representation](#3).

Sources: [README.md:15]()

### Optimization Passes

NNFusion applies a series of optimization passes to the IR to improve performance:

```mermaid
graph TD
    A["NNFusion Graph<br>with operations"] --> B{"Optimization Passes"}
    
    B --> B1["Kernel Tuning Pass"]
    B1 --> B1a["Antares<br>Auto-tuning"]
    B --> B2["Kernel Fusion Pass"]
    B --> B3["Block Fusion Pass"]
    B --> B4["IR-Based Fusion Pass"]
    B --> B5["AutoDiff Pass"]
    B --> B6["Common Subexpression<br>Elimination"]
    B --> B7["Constant Folding"]
    
    B1 --> C["Optimized Graph"]
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C
    B7 --> C
```

The optimization passes fall into these categories:

| Optimization Type | Description | Examples |
|-------------------|-------------|----------|
| Graph Optimizations | Reduces computational graph complexity | Common Subexpression Elimination, Constant Folding |
| Kernel Optimizations | Improves individual kernel performance | Kernel Tuning with Antares |
| Fusion Optimizations | Combines operations to reduce overhead | Kernel Fusion, Block Fusion |
| Memory Optimizations | Optimizes memory usage patterns | Static Memory Layout Planning |
| Training Support | Enables gradient computation | Automatic Differentiation |

For detailed information on optimization techniques, see [Optimization Passes](#4).

Sources: [README.md:15-17]()

### Code Generation

The code generation subsystem produces optimized code for different hardware targets:

```mermaid
classDiagram
    class KernelEmitter {
        +emit_function_call()
        +get_kernel_cache_entry()
        +get_or_emit_source()
        +emit_dependency()
    }
    
    class CudaEmitter {
        +emit_function_call()
        +set_launch_config()
    }
    
    class CpuKernelEmitter {
        +emit_function_signature()
    }
    
    class DirectXEmitter {
        +emit_hlsl_kernel()
    }
    
    class ROCmEmitter {
        +emit_rocm_kernel()
    }
    
    KernelEmitter <|-- CudaEmitter
    KernelEmitter <|-- CpuKernelEmitter
    KernelEmitter <|-- DirectXEmitter
    KernelEmitter <|-- ROCmEmitter
```

NNFusion supports generating code for:
- NVIDIA GPUs (CUDA)
- AMD GPUs (ROCm)
- CPUs
- DirectX Compute (HLSL)

The generated code is human-readable, allowing for manual inspection and additional customization when needed.

For more details, see [Code Generation](#5).

Sources: [README.md:18](), [README.md:21]()

### Runtime and Execution

After code generation, the model can be executed via different interfaces:

```mermaid
graph LR
    subgraph "Runtime Components"
        D1["nnfusion_rt<br>Generated Code"]
        D2["Device-specific Kernels"]
        D3["Memory Management"]
    end
    
    subgraph "Execution Interfaces"
        E1["Native Executable"]
        E2["Python Interface"]
        E3["Training Support"]
    end
    
    D1 --> D3
    D1 --> E1
    D1 --> E2
    E2 --> E3
```

For more information about runtime systems, see [Runtime and Execution](#6).

Sources: [README.md:18](), [README.md:22](), [README.md:97]()

## Key Capabilities

### Supported Model Formats
- TensorFlow frozen models
- ONNX models
- PyTorch models (via conversion to ONNX)

### Supported Target Platforms
- NVIDIA GPUs (CUDA)
- AMD GPUs (ROCm)
- CPUs
- DirectX Compute (HLSL)

### Distinctive Features

| Feature | Description |
|---------|-------------|
| Source-to-Source Compilation | Generates human-readable, framework-independent source code |
| Kernel Auto-tuning | Integrates with Antares for hardware-specific kernel optimization |
| Fusion Techniques | Multiple fusion strategies to reduce kernel launch overhead |
| Training Support | Automatic differentiation for gradient computation |
| Custom Operator Support | Framework for extending with custom operators |

Sources: [README.md:14-22]()

## Typical Usage Workflow

1. **Model Preparation**: Freeze or export model from original framework (TensorFlow, ONNX, PyTorch)
2. **Compilation**: Use NNFusion to compile the model
3. **Optimization**: Apply automatic or manual optimizations
4. **Code Generation**: Generate code for target hardware
5. **Build and Execute**: Compile and run the generated code

```mermaid
graph LR
    A["Model Preparation"] --> B["NNFusion Compilation"]
    B --> C["Code Generation"]
    C --> D["Build Generated Code"]
    D --> E["Execute Model"]
    
    subgraph "Optimization Loop"
        B --> F["Kernel Tuning"]
        F --> B
    end
```

For more detailed instructions on using NNFusion, refer to the specific guides for different model formats and optimization techniques.

Sources: [README.md:24-97]()

---

