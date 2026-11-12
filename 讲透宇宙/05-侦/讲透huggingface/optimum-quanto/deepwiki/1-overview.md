<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-quanto · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [Makefile](Makefile)
- [README.md](README.md)
- [external/awq/test_awq_kernels.py](external/awq/test_awq_kernels.py)
- [external/awq/test_awq_packing.py](external/awq/test_awq_packing.py)
- [external/smoothquant/README.md](external/smoothquant/README.md)
- [external/smoothquant/smoothquant.py](external/smoothquant/smoothquant.py)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)

</details>



Optimum Quanto is a PyTorch quantization backend for Hugging Face's optimum library. It provides a comprehensive system for quantizing deep learning models with a focus on ease of use and performance. This page introduces the purpose, architecture, and key features of Optimum Quanto.

For detailed information about getting started with the library, see [Getting Started](#2).

## Purpose and Key Features

Optimum Quanto enables efficient model compression through quantization, reducing memory requirements and potentially improving inference speed while maintaining model accuracy. The library has been designed with versatility and simplicity as core principles.

Key features include:

- **Full eager mode support**: Works with non-traceable models without requiring graph compilation
- **Multi-device compatibility**: Quantized models can run on any device including CUDA, CPU, and MPS (Metal Performance Shaders)
- **Automatic quantization handling**: Automatically inserts quantization/dequantization operations and quantized modules
- **Complete workflow**: Provides a seamless process from float model to dynamic to static quantized model
- **Flexible serialization**: Compatible with PyTorch `weight_only` and Hugging Face `safetensors`
- **Accelerated operations**: Optimized matrix multiplications on CUDA devices (int8-int8, fp16-int4, bf16-int8, bf16-int4)
- **Multiple precision support**: Supports int2, int4, int8, and float8 for weights; int8 and float8 for activations

Sources: [README.md:3-16](), [pyproject.toml:1-25]()

## System Architecture

Optimum Quanto follows a layered architecture design, with each layer handling specific aspects of the quantization process.

```mermaid
graph TD
    subgraph "Core Components"
        A["optimum.quanto"] --> B["Tensor Quantization"]
        A --> C["Module Quantization"]
        A --> D["Model Integration"]
        A --> E["Device-Specific Backends"]
    end
    
    subgraph "Tensor Quantization"
        B --> B1["QTensor Types"]
        B1 --> B11["WeightQBytesTensor<br>8-bit Quantization"]
        B1 --> B12["WeightQBitsTensor<br>2/4-bit Quantization"]
        B1 --> B13["ActivationQBytesTensor"]
        B --> B2["Quantization Algorithms"]
        B2 --> B21["AbsmaxOptimizer"]
        B2 --> B22["MaxOptimizer"]
    end
    
    subgraph "Module Quantization"
        C --> C1["QModuleMixin"]
        C1 --> C11["QLinear"]
        C1 --> C12["QConv2d"]
        C1 --> C13["QLayerNorm"]
    end
    
    subgraph "Model Integration"
        D --> D1["Transformers"]
        D1 --> D11["QuantizedModelForCausalLM"]
        D --> D2["Diffusers"]
        D2 --> D21["QuantizedPixArtTransformer2DModel"]
    end
    
    subgraph "Device Backends"
        E --> E1["CUDA"]
        E1 --> E11["AWQ Kernels"]
        E1 --> E12["Marlin FP8 Kernels"]
        E1 --> E13["TinyGemm"]
        E --> E2["CPU"]
        E --> E3["MPS"]
        E --> E4["XPU"]
    end
```

Sources: [README.md:228-299](), [external/awq/test_awq_kernels.py:38-153]()

## Quantization Workflow

The typical workflow when using Optimum Quanto involves several steps, from quantizing a model to deploying it.

```mermaid
flowchart LR
    A["Original Float Model"] --> B["Quantize Model"]
    B --> C["Calibrate Activations\n(optional)"]
    C --> D["Tune Model\n(optional)"]
    D --> E["Freeze Integer Weights"]
    E --> F["Serialize Model"]
    F --> G["Deploy Model"]
    
    subgraph "Implementation Details"
        H1["quantize() function"] -.- B
        H2["Calibration context"] -.- C
        H3["QAT training"] -.- D
        H4["freeze() function"] -.- E
        H5["save_pretrained()\nor safetensors"] -.- F
        H6["from_pretrained()\nor requantize()"] -.- G
    end
```

Sources: [README.md:58-126](), [README.md:127-223]()

## Tensor Quantization

At the core of Optimum Quanto is tensor quantization. The library provides specialized tensor classes that efficiently represent tensors in lower precision formats.

```mermaid
classDiagram
    class QTensor {
        +dequantize() : Tensor
    }
    
    class WeightQBytesTensor {
        +data: Tensor
        +scale: Tensor
        +qtype: QuantType
        +dequantize() : Tensor
    }
    
    class WeightQBitsTensor {
        +data: Tensor
        +scale: Tensor
        +shift: Tensor
        +qtype: QuantType
        +group_size: int
        +dequantize() : Tensor
    }
    
    class ActivationQBytesTensor {
        +data: Tensor
        +scale: Tensor
        +qtype: QuantType
        +dequantize() : Tensor
    }
    
    class MarlinF8QBytesTensor {
        +optimize() : Tensor
    }
    
    class AWQWeightQBitsTensor {
        +optimize() : Tensor
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
    QTensor <|-- ActivationQBytesTensor
    
    WeightQBytesTensor <|-- MarlinF8QBytesTensor
    WeightQBitsTensor <|-- AWQWeightQBitsTensor
```

Quanto uses a projection technique to minimize quantization errors by:
- Avoiding saturated values (mapped to the destination type min/max)
- Preventing zeroed values (below the smallest representable number)

The quantization approaches include:
- Symmetric per-tensor or per-channel for `int8` and `float8`
- Group-wise affine (with shift or 'zero-point') for lower bitwidth (int2, int4)

Sources: [README.md:228-246](), [external/awq/test_awq_packing.py:22-87]()

## Module Quantization

Optimum Quanto provides quantized versions of key PyTorch modules that are commonly used in deep learning models.

```mermaid
classDiagram
    class torch.nn.Module {
        +forward() : Tensor
    }
    
    class QModuleMixin {
        +weight_qtype: QuantType
        +activation_qtype: QuantType
        +qweight: QTensor
        +from_module() : QModule
        +forward() : Tensor
        +freeze() : None
    }
    
    class QLinear {
        +in_features: int
        +out_features: int
        +bias: bool
        +forward(input) : Tensor
    }
    
    class QConv2d {
        +in_channels: int
        +out_channels: int
        +kernel_size: tuple
        +forward(input) : Tensor
    }
    
    class QLayerNorm {
        +normalized_shape: tuple
        +eps: float
        +forward(input) : Tensor
    }
    
    torch.nn.Module <|-- QModuleMixin
    QModuleMixin <|-- QLinear
    QModuleMixin <|-- QConv2d
    QModuleMixin <|-- QLayerNorm
```

The supported quantized modules include:
- **QLinear**: Quantized version of `torch.nn.Linear` with quantized weights and optional quantized inputs/outputs
- **QConv2d**: Quantized version of `torch.nn.Conv2d` with quantized weights and optional quantized inputs/outputs
- **QLayerNorm**: Quantized version of `torch.nn.LayerNorm` with quantized outputs (weights and biases are not quantized)

Sources: [README.md:247-279]()

## Model Integration

Optimum Quanto seamlessly integrates with Hugging Face's transformers and diffusers libraries, providing helper classes for quantizing popular model architectures.

```mermaid
flowchart TD
    subgraph "Transformers Integration"
        A1["AutoModelForCausalLM"] --> A2["QuantizedModelForCausalLM.quantize()"]
        A2 --> A3["Quantized LLM Model"]
        A3 --> A4["save_pretrained()"]
        A5["from_pretrained()"] --> A3
    end
    
    subgraph "Diffusers Integration"
        B1["PixArtTransformer2DModel"] --> B2["QuantizedPixArtTransformer2DModel.quantize()"]
        B2 --> B3["Quantized Diffusion Model"]
        B3 --> B4["save_pretrained()"]
        B5["from_pretrained()"] --> B3
    end
    
    subgraph "Example Integration"
        C1["Hugging Face Pipeline"] --> C2["Integrate Quantized Components"]
        C2 --> C3["Optimized Pipeline"]
    end
```

The integration provides:
- High-level API for quantizing, saving, and loading Hugging Face models
- Support for common model types including causal language models and diffusion models
- Selective quantization (e.g., excluding specific layers like `lm_head`)
- Seamless inclusion in existing pipelines

Sources: [README.md:58-119]()

## Hardware-Specific Backends

Optimum Quanto provides optimized backends for different hardware platforms to maximize performance of quantized operations.

```mermaid
graph TD
    subgraph "Device-Specific Backends"
        A["torch.ops.quanto"] --> B["CUDA Extensions"]
        A --> C["CPU Extensions"]
        A --> D["MPS Extensions"]
        A --> E["XPU Extensions"]
    end
    
    B --> B1["AWQ Kernels\n(int4)"]
    B --> B2["Marlin Kernels\n(float8, int4)"]
    B --> B3["TinyGemm Kernels"]
    B --> B4["Matrix Multiplication\nAcceleration"]
    
    C --> C1["CPU Optimized\nOperations"]
    D --> D1["Metal Performance\nShaders Support"]
    E --> E1["Intel XPU\nSupport"]
```

The backend system provides:
- Optimized kernels for matrix multiplication with mixed-precision operations
- Specialized implementations for different quantization schemes (AWQ, Marlin, TinyGemm)
- Support for CPU, CUDA, MPS (Apple Metal), and Intel XPU devices
- Common interface through the `torch.ops.quanto` namespace

Sources: [external/awq/test_awq_kernels.py:38-153](), [README.md:14-16]()

## Advanced Quantization Techniques

Optimum Quanto implements several advanced quantization techniques to improve the accuracy and performance of quantized models.

### SmoothQuant

SmoothQuant is a technique that helps mitigate quantization errors in activations by "smoothing" the distribution of activation values. This is particularly useful for int8 quantization where large outlier values can cause most values to be quantized to zero.

The technique works by:
1. Collecting activation statistics during model calibration
2. Scaling the weights and inverse-scaling the activations to make the activation distribution more amenable to quantization
3. This results in better quantization accuracy while maintaining mathematical equivalence

Sources: [external/smoothquant/smoothquant.py:16-145](), [external/smoothquant/README.md:1-12](), [README.md:280-299]()

### AWQ (Activation-Aware Weight Quantization)

AWQ is an approach for low-bit weight quantization that takes into account activation patterns to improve quantization accuracy. The implementation includes specialized CUDA kernels for efficient inference.

Key features include:
- Groupwise quantization with configurable group size
- Per-group scaling and zero-point calculation
- Optimized packing formats for efficient memory access
- Specialized GEMM (General Matrix Multiplication) kernels

Sources: [external/awq/test_awq_kernels.py:38-153](), [external/awq/test_awq_packing.py:22-87]()

## Performance Characteristics

The performance of models quantized with Optimum Quanto varies depending on the quantization strategy and hardware:

- **Accuracy**: Models with int8/float8 weights and float8 activations typically maintain accuracy very close to the full-precision models
- **Latency**: When optimized kernels are available, inference speed is comparable to full-precision models when only weights are quantized
- **Memory Usage**: Memory requirements are approximately reduced by a factor of (float bits / quantized bits)

The optimal quantization strategy depends on the specific model architecture, task requirements, and target hardware.

Sources: [README.md:24-32]()

## Contributing

Optimum Quanto is an open-source project that welcomes contributions. Areas for contribution include:

- Fixing outstanding issues
- Implementing new kernels for different hardware
- Adding support for new model architectures
- Improving documentation and examples

The project follows standard open-source contribution practices with pull requests, code reviews, and continuous integration.

Sources: [CONTRIBUTING.md:17-222](), [Makefile:1-14](), [.github/PULL_REQUEST_TEMPLATE.md:1-30]()

---

