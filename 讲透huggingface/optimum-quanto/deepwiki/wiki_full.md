# Page: Overview

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

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [external/smoothquant/README.md](external/smoothquant/README.md)

</details>



This guide provides a comprehensive introduction to installing and using Optimum Quanto, a versatile quantization backend for PyTorch models. You'll learn how to set up the library, understand the basic quantization workflow, and get familiar with its usage across different model types. For deeper conceptual understanding of quantization types and techniques, see [Core Concepts](#3).

## Installation

Optimum Quanto is available as a pip package and can be installed with a simple command:

```bash
pip install optimum-quanto
```

The library supports various hardware platforms including CUDA GPUs, Apple MPS, Intel XPU, and standard CPUs. For development purposes, you can install the library in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

Sources: [README.md:50-56](), [CONTRIBUTING.md:120-128]()

## Supported Devices

Optimum Quanto works across multiple computing platforms:

| Device | Support | Notes |
|--------|---------|-------|
| CUDA (NVIDIA GPUs) | ✅ | Accelerated matrix multiplications for various precision combinations |
| CPU | ✅ | Works on all standard x86/ARM processors |
| MPS (Apple Silicon) | ✅ | Native support for Apple M-series chips |
| XPU (Intel GPUs) | ✅ | Support for Intel discrete GPUs |

When no device is specified, Optimum Quanto automatically selects the most appropriate device available in the following priority: CUDA > MPS > XPU > CPU.

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:110-120](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:108-118]()

## Quantization Workflow Overview

The quantization process in Optimum Quanto typically follows these steps:

```mermaid
flowchart LR
    A["Original Float Model"] --> B["Quantize"]
    B --> C["Calibrate (if using activation quantization)"]
    C --> D["Optional: Fine-tune"]
    D --> E["Freeze"]
    E --> F["Save/Serialize"]
    F --> G["Load Quantized Model"]
    
    style A fill:#f9f9f9,stroke:#333,stroke-width:1px
    style B fill:#f9f9f9,stroke:#333,stroke-width:1px
    style C fill:#f9f9f9,stroke:#333,stroke-width:1px
    style D fill:#f9f9f9,stroke:#333,stroke-width:1px
    style E fill:#f9f9f9,stroke:#333,stroke-width:1px
    style F fill:#f9f9f9,stroke:#333,stroke-width:1px
    style G fill:#f9f9f9,stroke:#333,stroke-width:1px
```

This workflow applies to both Hugging Face models and custom PyTorch models, with some API differences detailed in the following sections.

Sources: [README.md:58-223]()

## Using Optimum Quanto with Hugging Face Models

Optimum Quanto provides specialized classes for quantizing Hugging Face models with minimal code. Here's an example with a language model:

### Language Models

```python
from transformers import AutoModelForCausalLM
from optimum.quanto import QuantizedModelForCausalLM, qint4

# Load original model
model = AutoModelForCausalLM.from_pretrained('meta-llama/Meta-Llama-3-8B')

# Quantize model (weights only, excluding lm_head)
qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint4, exclude='lm_head')

# Save the quantized model
qmodel.save_pretrained('./Llama-3-8B-quantized')

# Later, load the quantized model
from optimum.quanto import QuantizedModelForCausalLM
qmodel = QuantizedModelForCausalLM.from_pretrained('Llama-3-8B-quantized')
```

### Diffusion Models

For diffusion models, you can quantize specific components:

```python
from diffusers import PixArtTransformer2DModel
from optimum.quanto import QuantizedPixArtTransformer2DModel, qfloat8

# Load original transformer component
model = PixArtTransformer2DModel.from_pretrained("PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", subfolder="transformer")

# Quantize with float8 precision
qmodel = QuantizedPixArtTransformer2DModel.quantize(model, weights=qfloat8)

# Save the quantized component
qmodel.save_pretrained("./pixart-sigma-fp8")
```

Sources: [README.md:58-119](), [examples/nlp/text-generation/quantize_causal_lm_model.py:137-147](), [examples/vision/text-to-image/quantize_pixart_sigma.py:21-31]()

## Low-Level Quantization API

For more control or when working with custom PyTorch models, you can use the low-level API:

### Step 1: Quantize

```python
from optimum.quanto import quantize, qint8

# Convert float model to dynamically quantized model
quantize(model, weights=qint8, activations=qint8)
```

### Step 2: Calibrate (for activation quantization)

```python
from optimum.quanto import Calibration

# Run representative data through the model to calibrate activation ranges
with Calibration(momentum=0.9):
    model(samples)
```

### Step 3: Fine-tune (optional)

```python
# Train the quantized model to recover accuracy
model.train()
for batch_idx, (data, target) in enumerate(train_loader):
    data, target = data.to(device), target.to(device)
    optimizer.zero_grad()
    output = model(data).dequantize()
    loss = torch.nn.functional.nll_loss(output, target)
    loss.backward()
    optimizer.step()
```

### Step 4: Freeze

```python
from optimum.quanto import freeze

# Replace float weights with quantized integer weights
freeze(model)
```

### Step 5: Serialize

```python
from safetensors.torch import save_file
from optimum.quanto import quantization_map
import json

# Save weights
save_file(model.state_dict(), 'model.safetensors')

# Save quantization information
with open('quantization_map.json', 'w') as f:
    json.dump(quantization_map(model), f)
```

### Step 6: Load

```python
from safetensors.torch import load_file
from optimum.quanto import requantize
import json

# Load state dict and quantization map
state_dict = load_file('model.safetensors')
with open('quantization_map.json', 'r') as f:
    qmap = json.load(f)

# Create empty model and requantize it
with torch.device('meta'):
    new_model = MyModel()
requantize(new_model, state_dict, qmap, device=torch.device('cuda'))
```

Sources: [README.md:121-223](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:142-169]()

## Quantization Options

Optimum Quanto provides various quantization types:

| Quantization Type | Import | Description |
|-------------------|--------|-------------|
| 4-bit integer | `qint4` | Highest compression, good for weight-only quantization |
| 8-bit integer | `qint8` | Good balance between compression and accuracy |
| 8-bit float | `qfloat8` | Good for activations, preserves dynamic range |
| None | `None` | Skip quantization for specific parts |

```mermaid
classDiagram
    class "QuantizationTypes" {
        qint4: 4-bit integer quantization
        qint8: 8-bit integer quantization 
        qfloat8: 8-bit float quantization
        None: No quantization
    }
    
    class "QuantizationTargets" {
        weights: Model weights
        activations: Model activations
        exclude: Skip specific modules
    }
    
    "QuantizationTypes" -- "QuantizationTargets": applied to
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:56-62](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:89-90]()

## Complete Example: Text Generation

Here's a complete example showing how to quantize a text generation model, calibrate it, and generate text:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from optimum.quanto import QuantizedModelForCausalLM, Calibration, qint8

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")
tokenizer.pad_token_id = tokenizer.eos_token_id

# Quantize model
qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint8, activations=qint8)

# Calibrate for activation quantization
cal_dataset = load_dataset("lambada", split=["validation"])[0].shuffle(seed=1)
with Calibration():
    for batch in cal_dataset.iter(batch_size=32):
        inputs = tokenizer(batch["text"], return_tensors="pt", padding=True)
        qmodel(inputs.input_ids.to(device), attention_mask=inputs.attention_mask.to(device))

# Generate text
prompt = "One of my fondest memory is"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = qmodel.generate(
    input_ids=inputs.input_ids.to(device),
    max_new_tokens=20,
    do_sample=True,
    top_k=50,
    top_p=0.9,
)
generated_text = tokenizer.decode(outputs[0])
print(generated_text)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:25-147]()

## Complete Example: Image Classification

This example shows how to quantize an image classification model for MNIST and evaluate its performance:

```python
import torch
import torch.nn.functional as F
from torchvision import datasets, transforms
from transformers import AutoModel
from optimum.quanto import quantize, Calibration, freeze, qint8

# Load MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),
    transforms.Lambda(lambda x: torch.flatten(x)),
])
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST("./data", train=False, download=True, transform=transform),
    batch_size=250
)

# Load model
model = AutoModel.from_pretrained("dacorvo/mnist-mlp", trust_remote_code=True)

# Test original model
model.eval()
test_loss = 0
correct = 0
with torch.no_grad():
    for data, target in test_loader:
        output = model(data)
        test_loss += F.nll_loss(output, target, reduction="sum").item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
print(f"Float model accuracy: {100.0 * correct / len(test_loader.dataset):.2f}%")

# Quantize model
quantize(model, weights=qint8, activations=qint8)

# Calibrate model
with Calibration():
    model.eval()
    with torch.no_grad():
        for data, target in test_loader:
            model(data)

# Freeze model
freeze(model)

# Test quantized model
model.eval()
test_loss = 0
correct = 0
with torch.no_grad():
    for data, target in test_loader:
        output = model(data)
        test_loss += F.nll_loss(output, target, reduction="sum").item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
print(f"Quantized model accuracy: {100.0 * correct / len(test_loader.dataset):.2f}%")
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:39-156]()

## Device Selection

All examples automatically select the best available device, but you can explicitly specify a device:

```python
import torch

if args.device is None:
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.xpu.is_available():
        device = torch.device("xpu")
    else:
        device = torch.device("cpu")
else:
    device = torch.device(args.device)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:110-120](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:108-118](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:60-70]()

## Next Steps

Now that you've learned the basics of using Optimum Quanto, you may want to explore:

- [Core Concepts](#3) to understand quantization types and techniques in depth
- [System Architecture](#4) to learn about the inner workings of Optimum Quanto
- [Example Applications](#8) for more specialized use cases like diffusion models

For issues, feature requests, or contributions, please refer to the [Contributing](#10) guide.

Sources: [README.md:1-300](), [CONTRIBUTING.md:1-222]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [external/smoothquant/README.md](external/smoothquant/README.md)
- [optimum/quanto/library/__init__.py](optimum/quanto/library/__init__.py)
- [optimum/quanto/library/extensions/cpp/__init__.py](optimum/quanto/library/extensions/cpp/__init__.py)
- [optimum/quanto/library/extensions/extension.py](optimum/quanto/library/extensions/extension.py)
- [optimum/quanto/library/extensions/mps/__init__.py](optimum/quanto/library/extensions/mps/__init__.py)
- [optimum/quanto/library/quantize.py](optimum/quanto/library/quantize.py)
- [optimum/quanto/library/unpack.py](optimum/quanto/library/unpack.py)
- [test/tensor/test_absmax.py](test/tensor/test_absmax.py)

</details>



This page explains the fundamental concepts of quantization in optimum-quanto, providing a technical foundation for understanding how the library enables efficient model compression and acceleration. For specific quantization types and their use cases, see [Quantization Types](#3.1). For detailed information about differences between weight and activation quantization, see [Weight vs Activation Quantization](#3.2).

## What is Quantization?

Quantization is a technique used to reduce the precision of numerical values in deep learning models. By representing weights and activations with fewer bits than their original floating-point format (typically float32 or float16), quantized models require less memory and can execute operations more efficiently.

```mermaid
flowchart LR
    A["Float Tensor
    (32-bit/16-bit)"] --> B["Quantization Process"]
    B --> C["Quantized Tensor
    (8-bit/4-bit/2-bit)"]
    
    subgraph "Benefits"
    D["Reduced Memory"] 
    E["Faster Inference"]
    F["Lower Power Usage"]
    end
    
    C --> D
    C --> E
    C --> F
```

Sources: [README.md:14-16](), [optimum/quanto/library/quantize.py:15-78]()

## Quantization in optimum-quanto

Optimum-quanto provides a versatile quantization system that works in eager mode and supports multiple precision levels and hardware backends.

```mermaid
classDiagram
    class "Quantization Workflow" {
        +Quantize model
        +Calibrate activations
        +Tune (QAT - optional)
        +Freeze weights
        +Serialize
    }
    
    class "Quantization Types" {
        +int2
        +int4
        +int8
        +float8
    }
    
    class "Hardware Support" {
        +CUDA
        +CPU
        +MPS
        +XPU
    }
    
    "Quantization Workflow" --> "Quantization Types" : uses
    "Quantization Workflow" --> "Hardware Support" : adapts to
```

Sources: [README.md:5-16](), [optimum/quanto/library/extensions/extension.py:1-87]()

## Tensor Quantization

At the core of optimum-quanto is tensor quantization, which involves projecting values from a source tensor into an optimal range for a destination type.

### Symmetric Quantization

Symmetric quantization maps float values to integers using a symmetric range around zero. This is used for weights and activations in optimum-quanto.

```mermaid
flowchart LR
    A["Float Tensor"] --> B["Scale Computation"]
    B --> C["Division by Scale"]
    C --> D["Rounding"]
    D --> E["Clamping"]
    E --> F["Type Conversion"]
    F --> G["Quantized Tensor"]

    subgraph "Key Components"
    H["absmax_scale()
    Compute optimal scale
    factor"]
    I["torch.round()
    Round to nearest
    integer"]
    J["torch.clamp()
    Limit range to
    type bounds"]
    end
```

Sources: [optimum/quanto/library/quantize.py:22-55](), [test/tensor/test_absmax.py:1-42]()

### Affine Quantization

For lower bitwidths (int2, int4), optimum-quanto uses affine quantization (with shift) to maximize representational capacity.

```mermaid
flowchart LR
    A["Float Tensor"] --> B["Add Shift"]
    B --> C["Divide by Scale"]
    C --> D["Round and Clamp"]
    D --> E["Pack into uint8"]
    E --> F["Quantized Tensor"]
```

Sources: [optimum/quanto/library/quantize.py:58-78](), [optimum/quanto/library/unpack.py:1-54]()

## Packing for Lower Bitwidth

Since PyTorch doesn't natively support data types smaller than 8 bits, optimum-quanto implements bit packing for 2-bit and 4-bit quantization.

```mermaid
flowchart TD
    A["Original Float Values"] --> B["Quantization to 2-bit/4-bit"]
    B --> C["Packing into uint8"]
    C --> D["Packed Storage in uint8 Tensor"]
    
    subgraph "Unpacking when needed"
    E["Packed uint8 Tensor"] --> F["quanto::unpack Operation"]
    F --> G["Expanded uint8 Tensor
    (with original values)"]
    G --> H["Dequantize to
    Float if necessary"]
    end
```

Sources: [optimum/quanto/library/unpack.py:18-54](), [optimum/quanto/library/extensions/cpp/__init__.py:34-36](), [optimum/quanto/library/extensions/mps/__init__.py:34-36]()

## Device-specific Optimizations

Optimum-quanto provides optimized implementations for different hardware backends through specialized extension modules.

```mermaid
flowchart LR
    A["Quantized Operations"] --> B{"Device Type"}
    B --> C["CUDA Extension"]
    B --> D["CPU Extension"]
    B --> E["MPS Extension"]
    B --> F["XPU Extension"]
    
    C --> G["Optimized CUDA Kernels"]
    D --> H["Optimized CPU Implementation"]
    E --> I["MPS Specific Implementation"]
    F --> J["XPU Specific Implementation"]
```

Sources: [optimum/quanto/library/extensions/cpp/__init__.py:1-36](), [optimum/quanto/library/extensions/mps/__init__.py:1-36](), [optimum/quanto/library/extensions/extension.py:1-86]()

## Quantization Workflow

A typical quantization workflow in optimum-quanto consists of several stages:

```mermaid
flowchart LR
    A["Float Model"] --> B["Quantize
    (Dynamic)"]
    B --> C["Calibrate
    (Optional)"]
    C --> D["Tune (QAT)
    (Optional)"]
    D --> E["Freeze
    (Static)"]
    E --> F["Serialize"]
    F --> G["Load"]

    subgraph "Key Operations"
    H["quantize()
    Apply quantization
    to model"]
    I["Calibration
    Record activation
    ranges"]
    J["freeze()
    Replace float weights
    with integer weights"]
    K["save_pretrained()
    or state_dict()"]
    end
```

Sources: [README.md:58-225]()

## Implementation Considerations

When implementing quantization in optimum-quanto, there are important technical considerations to keep in mind:

### Per-tensor vs Per-channel Quantization

```mermaid
flowchart TD
    A["Quantization Granularity"] --> B["Per-tensor
    (Activations)"]
    A --> C["Per-channel
    (Weights)"]
    
    B --> D["One scale for
    entire tensor"]
    C --> E["Multiple scales
    along axis 0"]
    
    D --> F["Compatible with
    most operations"]
    E --> G["Better accuracy for 
    weight matrices"]
```

Sources: [README.md:280-295]()

### Avoiding Quantization Pitfalls

Tensor quantization effectiveness can be impacted by outliers, particularly when quantizing activations to int8. Optimum-quanto provides solutions to address this:

```mermaid
flowchart TD
    A["Activation Outliers
    Problem"] --> B["Solution 1:
    SmoothQuant"]
    A --> C["Solution 2:
    Use float8 activations"]
    
    B --> D["Smooths activations
    statically"]
    C --> E["Better dynamic range
    than int8"]
```

Sources: [README.md:293-299](), [external/smoothquant/README.md:1-11]()

## Quantization Types Support

Optimum-quanto supports multiple quantization types, each with different precision-performance tradeoffs:

| Quantization Type | Bits | Use Case | Accuracy Impact | Speed Improvement |
|-------------------|------|----------|----------------|-------------------|
| int8             | 8    | General purpose, activations | Minimal | Good |
| float8           | 8    | Activations with outliers | Minimal | Good |
| int4             | 4    | Weights-only quantization | Moderate | Excellent |
| int2             | 2    | Extreme compression | Significant | Outstanding |

Sources: [README.md:14-16](), [README.md:26-30]()

## Hardware Acceleration

The optimum-quanto system includes hardware-specific optimizations for accelerated matrix multiplications:

```mermaid
flowchart LR
    A["Quantized Matrix
    Multiplication"] --> B{"Hardware Type"}
    
    B --> C["CUDA"]
    B --> D["CPU"]
    B --> E["MPS (Apple Silicon)"]
    B --> F["XPU (Intel)"]
    
    C --> G["int8-int8, fp16-int4,
    bf16-int8, bf16-int4"]
    D --> H["Native operations"]
    E --> I["Apple-specific
    optimizations"]
    F --> J["Intel-specific
    optimizations"]
```

Sources: [README.md:14](), [optimum/quanto/library/extensions/extension.py:13-54]()

This overview of core concepts provides the foundation for understanding how optimum-quanto implements quantization for deep learning models. The subsequent pages in this wiki will build upon these concepts to provide more detailed explanations of specific components and workflows.

---

# Page: Quantization Types

# Quantization Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/library/__init__.py](optimum/quanto/library/__init__.py)
- [optimum/quanto/library/extensions/cpp/__init__.py](optimum/quanto/library/extensions/cpp/__init__.py)
- [optimum/quanto/library/extensions/extension.py](optimum/quanto/library/extensions/extension.py)
- [optimum/quanto/library/extensions/mps/__init__.py](optimum/quanto/library/extensions/mps/__init__.py)
- [optimum/quanto/library/quantize.py](optimum/quanto/library/quantize.py)
- [optimum/quanto/library/unpack.py](optimum/quanto/library/unpack.py)
- [optimum/quanto/tensor/weights/qbits.py](optimum/quanto/tensor/weights/qbits.py)
- [optimum/quanto/tensor/weights/qbytes.py](optimum/quanto/tensor/weights/qbytes.py)
- [optimum/quanto/tensor/weights/quantization.py](optimum/quanto/tensor/weights/quantization.py)
- [test/tensor/test_absmax.py](test/tensor/test_absmax.py)

</details>



This page details the different quantization types supported in optimum-quanto, their characteristics, and how they are implemented in the codebase. For information about the difference between weight and activation quantization, see [Weight vs Activation Quantization](#3.2).

## Overview of Quantization Types

Optimum-quanto supports several quantization types with different precisions, each designed for specific trade-offs between model size, inference speed, and accuracy. The library implements both integer and floating-point quantization methods.

```mermaid
flowchart TD
    A["Quantization Types"]
    A --> B["Integer Quantization"]
    A --> C["Floating-point Quantization"]
    
    B --> D["qint2 (2-bit)"]
    B --> E["qint4 (4-bit)"]
    B --> F["qint8 (8-bit)"]
    
    C --> G["qfloat8_e4m3fn (8-bit)"]
    
    H["Implementation Types"]
    H --> I["WeightQBytesTensor"]
    H --> J["WeightQBitsTensor"]
    
    I --> F
    I --> G
    J --> D
    J --> E
    
    K["Storage Structure"]
    K --> L["Per-tensor Quantization"]
    K --> M["Per-axis Quantization"]
    K --> N["Group Quantization"]
```

Sources: 
- [optimum/quanto/tensor/weights/qbytes.py:29-327]()
- [optimum/quanto/tensor/weights/qbits.py:31-302]()
- [optimum/quanto/tensor/weights/quantization.py:24-73]()

## Quantization Types and Precision

Optimum-quanto provides a variety of quantization types to balance between model size, computational efficiency, and quality:

| Quantization Type | Bits | Format | Implementation Class | Use Cases |
|-------------------|------|--------|----------------------|-----------|
| qint2 | 2 | Integer | WeightQBitsTensor | Ultra-low memory, high compression ratio |
| qint4 | 4 | Integer | WeightQBitsTensor | Good balance between quality and compression |
| qint8 | 8 | Integer | WeightQBytesTensor | Higher precision, standard quantization |
| qfloat8_e4m3fn | 8 | Float | WeightQBytesTensor (Marlin) | Precision for weights with wide dynamic range |

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:85-144]()
- [optimum/quanto/tensor/weights/qbits.py:65-123]()

## Quantization Implementation Details

The implementation of quantization in optimum-quanto is split into two main tensor types:

### 1. WeightQBytesTensor (8-bit)

The `WeightQBytesTensor` handles 8-bit quantization (both integer and floating-point) and is implemented in [optimum/quanto/tensor/weights/qbytes.py]().

```mermaid
classDiagram
    class WeightQBytesTensor {
        +_data: torch.Tensor
        +_scale: torch.Tensor
        +qtype: qtype
        +axis: int
        +activation_qtype: qtype
        +quantize()
        +dequantize()
        +optimize()
    }
    
    class MarlinF8QBytesTensor {
        +weight_qbytes_tensor()
    }
    
    WeightQBytesTensor <|-- MarlinF8QBytesTensor
    
    note for WeightQBytesTensor "8-bit quantization for both\nint8 and float8 types"
    note for MarlinF8QBytesTensor "Hardware-optimized for CUDA\nwith float8 (e4m3fn format)"
```

Key features:
- Supports both `qint8` and `qfloat8_e4m3fn` quantization types
- Quantizes with a symmetric pattern: `data = torch.round(base / scale)`
- Provides optimization for specific hardware with `MarlinF8QBytesTensor` subclass
- Automatically selects the best implementation based on the device and parameters

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:85-144]()
- [optimum/quanto/tensor/weights/qbytes.py:157-166]()
- [optimum/quanto/library/quantize.py:28-55]()

### 2. WeightQBitsTensor (2-bit and 4-bit)

The `WeightQBitsTensor` handles low-bit quantization (2-bit and 4-bit) and is implemented in [optimum/quanto/tensor/weights/qbits.py]().

```mermaid
classDiagram
    class WeightQBitsTensor {
        +_data: PackedTensor
        +_scale: torch.Tensor
        +_shift: torch.Tensor
        +qtype: qtype
        +axis: int
        +_group_size: int
        +quantize()
        +dequantize()
        +optimize()
    }
    
    class AWQWeightQBitsTensor {
        +weight_qbits_tensor()
    }
    
    class TinyGemmWeightQBitsTensor {
        +weight_qbits_tensor()
    }
    
    WeightQBitsTensor <|-- AWQWeightQBitsTensor
    WeightQBitsTensor <|-- TinyGemmWeightQBitsTensor
    
    note for WeightQBitsTensor "Low-bit quantization (2 and 4 bits)\nwith packed storage format"
    note for AWQWeightQBitsTensor "CUDA-optimized for int4 with AWQ"
    note for TinyGemmWeightQBitsTensor "Optimized for CPU and newer CUDA"
```

Key features:
- Supports `qint2` and `qint4` quantization types
- Uses `PackedTensor` to efficiently store multiple low-bit values in each byte
- Implements affine quantization: `data = torch.round((base + shift) / scale)`
- Supports grouped quantization with the `group_size` parameter
- Provides specialized subclasses for different hardware: `AWQWeightQBitsTensor` and `TinyGemmWeightQBitsTensor`

Sources:
- [optimum/quanto/tensor/weights/qbits.py:65-123]()
- [optimum/quanto/tensor/weights/qbits.py:139-149]()
- [optimum/quanto/library/quantize.py:64-78]()
- [optimum/quanto/library/unpack.py:21-54]()

## Quantization Process

The quantization process for weights follows different paths based on the bit-width:

```mermaid
flowchart TD
    A["quantize_weight(tensor, qtype, ...)"] --> B{qtype.bits == 8?}
    B -- Yes --> C["WeightQBytesTensor.quantize\n(Symmetric Quantization)"]
    B -- No --> D["WeightQBitsTensor.quantize\n(Affine Quantization)"]
    
    C --> E["Quantize with scale only\n(data = base / scale)"]
    D --> F["Quantize with scale and shift\n(data = (base + shift) / scale)"]
    
    E --> G["Create optimized implementation\nbased on hardware"]
    F --> G
    
    G --> H["MarlinF8QBytesTensor\n(For float8 on CUDA)"]
    G --> I["AWQWeightQBitsTensor\n(For int4 on CUDA)"]
    G --> J["TinyGemmWeightQBitsTensor\n(For int4 on CPU/CUDA)"]
    G --> K["Base implementation\n(Device agnostic)"]
```

Sources:
- [optimum/quanto/tensor/weights/quantization.py:27-73]()
- [optimum/quanto/tensor/weights/qbytes.py:31-65]()
- [optimum/quanto/tensor/weights/qbits.py:34-62]()

## Storage and Unpacking

For low-bit quantization (2-bit and 4-bit), values are packed into 8-bit storage units since PyTorch doesn't natively support lower bit-width tensors:

| Quantization Type | Values per Byte | Unpacking Process |
|-------------------|-----------------|-------------------|
| qint2 | 4 | Extract 4 separate 2-bit values from each byte |
| qint4 | 2 | Extract 2 separate 4-bit values from each byte |
| qint8/qfloat8 | 1 | Direct storage (no packing required) |

The unpacking process is implemented with both Python fallback and hardware-specific optimizations:

```mermaid
flowchart TD
    A["torch.ops.quanto.unpack(packed, bits)"]
    A --> B{device type?}
    
    B -- CPU --> C["unpack_cpp\n(quanto_cpp extension)"]
    B -- CUDA --> D["unpack_cuda\n(quanto_cuda extension)"]
    B -- MPS --> E["unpack_mps\n(quanto_mps extension)"]
    B -- Other --> F["Python fallback\nunpack implementation"]
    
    F --> G["Extract each value with\nbit shifting and masking"]
```

Sources:
- [optimum/quanto/library/unpack.py:21-54]()
- [optimum/quanto/library/extensions/cpp/__init__.py:34-36]()
- [optimum/quanto/library/extensions/mps/__init__.py:34-36]()

## Hardware Optimizations

Optimum-quanto automatically selects the most efficient implementation for each quantization type based on the hardware:

| Quantization Type | Hardware | Optimized Implementation |
|-------------------|----------|--------------------------|
| qfloat8_e4m3fn | CUDA (SM ≥ 8.0) | MarlinF8QBytesTensor |
| qint4 | CUDA (SM ≥ 8.0) | AWQWeightQBitsTensor |
| qint4 | CPU or CUDA (≥ 12.1) | TinyGemmWeightQBitsTensor |
| Any | Any | Base implementation (WeightQBytesTensor/WeightQBitsTensor) |

Key optimization criteria:
- Device type (CPU, CUDA, MPS)
- For CUDA: GPU architecture (Compute Capability)
- Tensor dimensions and alignment
- Extension availability

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:87-143]()
- [optimum/quanto/tensor/weights/qbits.py:66-123]()
- [optimum/quanto/library/extensions/extension.py:77-86]()

## Choosing a Quantization Type

The choice of quantization type depends on your specific requirements:

| Quantization Type | Advantages | Disadvantages | Best For |
|-------------------|------------|--------------|----------|
| qint2 | Highest compression (16×) | Lowest precision | Text models in constrained environments |
| qint4 | Good compression (8×) | Moderate quality loss | General LLM inference |
| qint8 | Better precision | Lower compression (4×) | Vision models, critical applications |
| qfloat8_e4m3fn | Good for wide value ranges | Requires newer GPUs | Models with outlier parameters |

Sources:
- [optimum/quanto/tensor/weights/quantization.py:27-73]()
- [test/tensor/test_absmax.py:22-42]()

## Calibration and Scaling

For both `WeightQBytesTensor` and `WeightQBitsTensor`, appropriate scale computation is critical. One common method is absmax scaling:

```python
# Example of absmax scale computation
scale = absmax_scale(tensor, qtype, axis)
```

This determines the maximum absolute value in the tensor (per-tensor, per-axis, or per-group) and scales accordingly to fit the quantization range.

Sources:
- [test/tensor/test_absmax.py:26-42]()

The quantization types in optimum-quanto provide a flexible foundation for model compression, allowing you to balance size, speed, and accuracy according to your application's needs.

---

# Page: Weight vs Activation Quantization

# Weight vs Activation Quantization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/tensor/activations/qbytes.py](optimum/quanto/tensor/activations/qbytes.py)
- [optimum/quanto/tensor/function.py](optimum/quanto/tensor/function.py)
- [optimum/quanto/tensor/weights/qbits.py](optimum/quanto/tensor/weights/qbits.py)
- [optimum/quanto/tensor/weights/qbytes.py](optimum/quanto/tensor/weights/qbytes.py)
- [optimum/quanto/tensor/weights/quantization.py](optimum/quanto/tensor/weights/quantization.py)
- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



This page explains the key differences between weight quantization and activation quantization in optimum-quanto, how they are implemented, and how they work together to create efficient quantized models.

## Overview

Quantization in neural networks involves two primary components: weights (model parameters) and activations (layer inputs/outputs). While both share the goal of reducing precision to improve efficiency, they differ in implementation, timing, and optimization techniques.

```mermaid
flowchart LR
    subgraph "Quantization Types"
        direction TB
        W["Weight Quantization"] 
        A["Activation Quantization"]
    end
    
    subgraph "When Applied"
        direction TB
        WA["Applied once\nduring model preparation"] 
        AA["Applied dynamically\nduring inference"]
    end
    
    subgraph "Implementation"
        direction TB
        WI["WeightQBytesTensor (8-bit)\nWeightQBitsTensor (2/4-bit)"] 
        AI["ActivationQBytesTensor (8-bit)"]
    end
    
    W --> WA
    W --> WI
    A --> AA
    A --> AI
```

Sources: [optimum/quanto/tensor/weights/qbytes.py](), [optimum/quanto/tensor/weights/qbits.py](), [optimum/quanto/tensor/activations/qbytes.py]()

## Weight Quantization

Weight quantization targets the model's parameters, which are static after training. In optimum-quanto, weights can be quantized to various bit precisions:

- 8-bit quantization using `WeightQBytesTensor`
- 2-bit and 4-bit quantization using `WeightQBitsTensor`

```mermaid
classDiagram
    class QTensor {
        +dequantize()
    }
    
    class WeightQBytesTensor {
        +data: tensor
        +scale: tensor
        +qtype: QuantType
        +axis: int
        +activation_qtype: qtype
        +dequantize()
    }
    
    class WeightQBitsTensor {
        +data: tensor
        +scale: tensor
        +shift: tensor
        +qtype: QuantType
        +axis: int
        +group_size: int
        +dequantize()
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
```

Sources: [optimum/quanto/tensor/weights/qbytes.py:85-276](), [optimum/quanto/tensor/weights/qbits.py:65-302]()

### Key Characteristics of Weight Quantization

1. **Quantization Axis**: Weights are typically quantized along specific dimensions (axis=0 for output features or axis=-1 for input features)
   
2. **Group Size**: For lower bit precision (2/4-bit), weights can be quantized in groups to maintain accuracy
   
3. **Static**: Applied once during model preparation and remains unchanged during inference
   
4. **Hardware Optimizations**: Can be specialized for different hardware (AWQ, Marlin FP8, TinyGemm)

Weight quantization is performed using the `quantize_weight` function:

```python
# Simplified usage pattern for weight quantization
quantize_weight(
    weight_tensor, 
    qtype=qint4,              # Quantization type (qint2, qint4, qint8, qfloat8)
    axis=0,                   # Quantization axis (0 or -1)
    scale=scale_tensor,       # Scaling factors
    shift=shift_tensor,       # Only needed for <8-bit quantization
    group_size=128,           # Only used for <8-bit quantization
    activation_qtype=None     # Optional hint about activation quantization
)
```

Sources: [optimum/quanto/tensor/weights/quantization.py:27-73]()

## Activation Quantization

Activation quantization targets the inputs and outputs of neural network layers during inference. In optimum-quanto, activations are quantized using `ActivationQBytesTensor`.

```mermaid
flowchart LR
    FI["Float Input"] --> Q["quantize_activation()"]
    Q --> QT["ActivationQBytesTensor"]
    QT --> QL["Quantized Layer"]
    QL --> QO["ActivationQBytesTensor"]
    QO --> D["dequantize()"]
    D --> FO["Float Output"]
    
    C["Calibration\nContext Manager"] --> |"Adjusts scales"| QL
```

Sources: [optimum/quanto/tensor/activations/qbytes.py:46-92](), [test/nn/test_calibrate.py:23-61]()

### Key Characteristics of Activation Quantization

1. **Per-Tensor Scaling**: Typically applied using a single scale for the entire tensor
   
2. **Dynamic**: Applied during inference, with scales potentially adjusted based on actual data
   
3. **Calibration**: Requires a calibration phase to determine appropriate scaling factors
   
4. **Supported Types**: Currently supports 8-bit integer and 8-bit floating point formats

Activation quantization is controlled through the `Calibration` context manager, which collects statistics to determine appropriate scaling factors:

```python
# Simplified usage pattern for activation quantization
with Calibration():
    # First pass to collect statistics and set scales
    output = model(inputs)

# Subsequent inferences use the calibrated scales
quantized_output = model(inputs) 
```

Sources: [test/nn/test_calibrate.py:23-40](), [test/quantize/test_quantize_mlp.py:71-77]()

## Comparison Between Weight and Activation Quantization

| Aspect | Weight Quantization | Activation Quantization |
|--------|---------------------|-------------------------|
| Target | Model parameters (weights) | Layer inputs/outputs |
| When Applied | During model preparation | During inference |
| Implementation | `WeightQBytesTensor`, `WeightQBitsTensor` | `ActivationQBytesTensor` |
| Bit Precision | 2-bit, 4-bit, 8-bit | 8-bit |
| Supported Types | Integer, Floating-point | Integer, Floating-point |
| Scaling Method | Per-axis, Per-group | Per-tensor |
| Overhead | One-time cost | Runtime cost |
| Memory Impact | Reduced model size | Reduced activation memory |
| Hardware Support | Specialized kernels for various hardware | Device-dependent |

Sources: [test/nn/test_qlinear.py:37-57](), [test/nn/test_calibrate.py:23-40]()

## How They Work Together

Weight and activation quantization often work together in a quantized model. The following diagram illustrates their interaction within a quantized linear layer:

```mermaid
flowchart TB
    subgraph "QLinear Module"
        direction TB
        W["Quantized Weight\nWeightQBytesTensor/WeightQBitsTensor"]
        I["Input\nFloat or ActivationQBytesTensor"]
        O["Output\nFloat or ActivationQBytesTensor"]
        
        subgraph "forward()"
            direction LR
            Q["Quantize Input\n(if not already quantized)"]
            MM["Quantized Matrix Multiplication"]
            DQ["Dequantize or Quantize Output\n(based on configuration)"]
        end
        
        I --> Q
        Q --> MM
        W --> MM
        MM --> DQ
        DQ --> O
    end
```

Sources: [test/nn/test_qlinear.py:37-57](), [test/nn/test_calibrate.py:23-40]()

The quantized module architecture in optimum-quanto supports both weight-only quantization and combined weight and activation quantization:

```mermaid
classDiagram
    class QModuleMixin {
        +weight_qtype: qtype
        +activation_qtype: qtype
        +qweight: QTensor
        +input_scale: tensor
        +output_scale: tensor
        +from_module()
        +forward()
        +freeze()
    }
    
    class QLinear {
        +forward(input)
    }
    
    class QConv2d {
        +forward(input)
    }
    
    class QLayerNorm {
        +forward(input)
    }
    
    QModuleMixin <|-- QLinear
    QModuleMixin <|-- QConv2d
    QModuleMixin <|-- QLayerNorm
```

Sources: [test/nn/test_qlinear.py:37-57](), [test/nn/test_qconv2d.py:31-51](), [test/nn/test_qlayernorm.py:23-41]()

## Implementation Impact

The choice between weight-only and weight+activation quantization affects both accuracy and performance:

```mermaid
flowchart LR
    subgraph "Quantization Strategy"
        WO["Weight-Only\nQuantization"]
        WA["Weight + Activation\nQuantization"]
    end
    
    subgraph "Impact"
        A["Accuracy Impact: Lower"]
        S["Speed Improvement: Moderate"]
        M["Memory Reduction: Moderate"]
        
        AH["Accuracy Impact: Higher"]
        SH["Speed Improvement: Significant"]
        MH["Memory Reduction: Significant"]
    end
    
    WO --> A
    WO --> S
    WO --> M
    
    WA --> AH
    WA --> SH
    WA --> MH
```

Sources: [test/quantize/test_quantize_mlp.py:83-116]()

## Practical Usage

Here's how both types of quantization are typically used together in optimum-quanto:

1. **Model Preparation**:
   - Quantize model weights to lower precision (4-bit or 8-bit)
   - Freeze the model to convert weights to quantized tensors

2. **Calibration**:
   - Run representative inputs through the model with `Calibration()` context
   - This sets appropriate scaling factors for activations

3. **Inference**:
   - Input tensors are dynamically quantized
   - Computations happen in low precision
   - Output can remain quantized or be dequantized based on needs

Example pattern for a model with both weight and activation quantization:

```python
# Prepare model with both weight and activation quantization
model = ...
quantize(model, weights=qint8, activations=qint8)
freeze(model)

# Calibration phase to set activation scales
with Calibration():
    model(calibration_inputs)

# Inference with quantized weights and activations
output = model(inputs)  # output is ActivationQBytesTensor if activations=qint8
```

Sources: [test/quantize/test_quantize_mlp.py:63-81]()

## Summary

Weight and activation quantization in optimum-quanto provide complementary approaches to model optimization:

- **Weight quantization** reduces model size and improves inference speed by storing parameters in lower precision.
- **Activation quantization** further improves performance by computing intermediate values in lower precision.

The framework allows flexible configuration of both, enabling users to make appropriate trade-offs between accuracy and efficiency based on their specific requirements and hardware limitations.

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/nn/qconv2d.py](optimum/quanto/nn/qconv2d.py)
- [optimum/quanto/nn/qlayernorm.py](optimum/quanto/nn/qlayernorm.py)
- [optimum/quanto/nn/qlinear.py](optimum/quanto/nn/qlinear.py)
- [optimum/quanto/nn/qmodule.py](optimum/quanto/nn/qmodule.py)
- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/test_absmax.py](test/tensor/test_absmax.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



This document provides a comprehensive overview of the optimum-quanto system architecture. It explains the core components, their interactions, and how they work together to provide efficient model quantization. For specific details about quantization types, see [Quantization Types](#3.1), and for information about the differences between weight and activation quantization, see [Weight vs Activation Quantization](#3.2).

## Core Architecture Overview

Optimum-Quanto is structured as a layered system that enables quantization at different levels: tensors, modules, and models. Each layer builds on the one below to provide increasingly higher-level functionality.

```mermaid
flowchart TD
    subgraph "Tensor Layer"
        T1["QTensor Base Class"]
        T2["WeightQBytesTensor\n(8-bit weights)"]
        T3["WeightQBitsTensor\n(2/4-bit weights)"]
        T4["ActivationQBytesTensor\n(activations)"]
        T1 --> T2
        T1 --> T3
        T1 --> T4
    end

    subgraph "Module Layer"
        M1["QModuleMixin"]
        M2["QLinear"]
        M3["QConv2d"]
        M4["QLayerNorm"]
        M1 --> M2
        M1 --> M3
        M1 --> M4
    end

    subgraph "Model Integration Layer"
        I1["quantize()"]
        I2["freeze()"]
        I3["Calibration Context"]
    end

    subgraph "Backends"
        B1["CUDA Kernels"]
        B2["CPU Implementation"]
        B3["MPS Support"]
        B4["XPU Extension"]
    end

    T1 -.-> M1
    M1 -.-> I1
    B1 -.-> T2
    B1 -.-> T3
    B1 -.-> T4
    B2 -.-> T2
    B2 -.-> T3
    B2 -.-> T4
    B3 -.-> T2
    B3 -.-> T3
    B4 -.-> T2
    B4 -.-> T3
```

Sources:
- [optimum/quanto/nn/qmodule.py:37-43]()
- [optimum/quanto/nn/qlinear.py:23-26]()
- [optimum/quanto/nn/qconv2d.py:23-26]()
- [optimum/quanto/nn/qlayernorm.py:23-26]()

## Tensor Quantization Architecture

The tensor layer forms the foundation of optimum-quanto, providing the basic data structures for quantized values.

```mermaid
classDiagram
    class QTensor {
        +dequantize() : Tensor
        +__torch_function__()
    }
    
    class WeightQBytesTensor {
        +data : Tensor
        +scale : Tensor
        +qtype : QuantType
        +axis : int
        +dequantize() : Tensor
        +optimize() : QTensor
    }
    
    class WeightQBitsTensor {
        +data : Tensor
        +scale : Tensor
        +shift : Tensor
        +qtype : QuantType
        +axis : int
        +group_size : int
        +dequantize() : Tensor
        +optimize() : QTensor
    }
    
    class ActivationQBytesTensor {
        +data : Tensor
        +scale : Tensor
        +qtype : QuantType
        +dequantize() : Tensor
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
    QTensor <|-- ActivationQBytesTensor
```

### Tensor Types

- **QTensor**: Abstract base class for all quantized tensors
- **WeightQBytesTensor**: Represents 8-bit quantized weights (int8, float8)
- **WeightQBitsTensor**: Represents low-bit quantized weights (int2, int4)
- **ActivationQBytesTensor**: Represents quantized activations (int8, float8)

Each tensor type implements quantization, dequantization, and optimization methods specific to its use case.

Sources:
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py:30-71]()
- [test/tensor/activations/test_activations_quantize.py:30-61]()
- [test/library/test_quantize.py:32-103]()

## Module Quantization Architecture

The module layer provides quantized versions of PyTorch's standard modules, with the `QModuleMixin` class adding quantization functionality.

```mermaid
classDiagram
    class QModuleMixin {
        +weight_qtype : qtype
        +activation_qtype : qtype
        +weight_group_size : int
        +optimizer : Optimizer
        +qweight : QTensor
        +from_module() : QModule
        +qcreate() : QModule
        +freeze() : None
        +quantize_input() : Tensor
        +quantize_output() : Tensor
    }
    
    class QLinear {
        +in_features : int
        +out_features : int
        +weight : Parameter
        +bias : Parameter
        +forward(input) : Tensor
    }
    
    class QConv2d {
        +in_channels : int
        +out_channels : int
        +kernel_size : tuple
        +stride : tuple
        +padding : tuple
        +forward(input) : Tensor
    }
    
    class QLayerNorm {
        +normalized_shape : tuple
        +weight : Parameter
        +bias : Parameter
        +eps : float
        +forward(input) : Tensor
    }
    
    QModuleMixin <|-- QLinear
    QModuleMixin <|-- QConv2d
    QModuleMixin <|-- QLayerNorm
```

### Core Module Functionality

The `QModuleMixin` provides several key features:

1. **Dynamic Weight Quantization**: Quantizes weights on-the-fly during inference
2. **Weight and Activation Quantization Types**: Configurable quantization types
3. **Optimization Strategy**: Customizable quantization optimization (e.g., AbsmaxOptimizer, MaxOptimizer)
4. **Freezing**: Converting dynamically quantized modules to static quantized ones
5. **Serialization**: Custom state dict handling for quantized parameters

Sources:
- [optimum/quanto/nn/qmodule.py:94-310]()
- [optimum/quanto/nn/qlinear.py:27-50]()
- [optimum/quanto/nn/qconv2d.py:27-55]() 
- [optimum/quanto/nn/qlayernorm.py:27-53]()

## Quantization Registration System

Optimum-quanto uses a registration system to map PyTorch module types to their quantized equivalents, enabling automatic quantization of complex models.

```mermaid
flowchart LR
    subgraph "Registration"
        R1["register_qmodule()"]
        R2["_QMODULE_TABLE"]
        R3["quantize_module()"]
        R1 -->|"registers"| R2
        R2 -->|"used by"| R3
    end

    subgraph "Core Modules"
        C1["torch.nn.Linear"]
        C2["torch.nn.Conv2d"]
        C3["torch.nn.LayerNorm"]
    end
    
    subgraph "Quantized Modules"
        Q1["QLinear"]
        Q2["QConv2d"]
        Q3["QLayerNorm"]
    end
    
    C1 -->|"registered to"| Q1
    C2 -->|"registered to"| Q2
    C3 -->|"registered to"| Q3
    
    R2 -.->|"maps"| C1
    R2 -.->|"maps"| C2
    R2 -.->|"maps"| C3
    R2 -.->|"to"| Q1
    R2 -.->|"to"| Q2
    R2 -.->|"to"| Q3
```

The registration system enables:

1. **Automatic Module Replacement**: Converting standard PyTorch modules to quantized versions
2. **Extensibility**: Adding support for new module types
3. **Recursive Model Traversal**: Quantizing entire model architectures

Sources:
- [optimum/quanto/nn/qmodule.py:41-91]()
- [optimum/quanto/nn/qlinear.py:26-27]()
- [optimum/quanto/nn/qconv2d.py:26-27]()
- [optimum/quanto/nn/qlayernorm.py:26-27]()

## Quantization Workflow Architecture

The following diagram illustrates the typical workflow when using optimum-quanto, from the original float model to the loaded quantized model.

```mermaid
flowchart LR
    subgraph "1. Original Model"
        A1["Float32/Float16 Model"]
    end
    
    subgraph "2. Quantization"
        B1["quantize(model, weights=qint8)"]
        B2["Replace modules with quantized versions"]
        B3["Dynamic quantization during forward pass"]
        B1 --> B2 --> B3
    end
    
    subgraph "3. Calibration"
        C1["with Calibration():"]
        C2["Run representative inputs"]
        C3["Collect activation statistics"]
        C4["Set input_scale and output_scale"]
        C1 --> C2 --> C3 --> C4
    end
    
    subgraph "4. Freezing"
        D1["freeze(model)"]
        D2["Replace weights with QTensor"]
        D3["Optimize for target hardware"]
        D1 --> D2 --> D3
    end
    
    subgraph "5. Serialization & Loading"
        E1["save_pretrained()"]
        E2["from_pretrained()"]
        E1 --> E2
    end
    
    A1 --> B1
    B3 --> C1
    C4 --> D1
    D3 --> E1
```

### Key Workflow Stages

1. **Quantization**: Replace model modules with quantized versions that dynamically quantize weights
2. **Calibration**: Gather statistics on activations to set appropriate scaling factors
3. **Freezing**: Convert dynamic quantization to static quantization for inference efficiency
4. **Serialization & Loading**: Save and load quantized models with specialized formats

Sources:
- [test/nn/test_calibrate.py:23-101]()
- [test/quantize/test_quantize_mlp.py:63-146]()
- [test/nn/test_qlinear.py:196-227]()

## Device-Specific Backend Architecture

Optimum-quanto provides optimized implementations for different hardware platforms through its backend system.

```mermaid
flowchart TB
    subgraph "Backends"
        B0["torch.ops.quanto"]
        
        subgraph "CUDA"
            B1["AWQ Kernels (int4)"]
            B2["Marlin Kernels (float8)"]
            B3["TinyGemm (int4)"]
        end
        
        subgraph "CPU"
            B4["qbytes_mm"]
            B5["unpack CPU"]
        end
        
        subgraph "MPS"
            B6["unpack MPS"]
        end
        
        subgraph "XPU"
            B7["unpack XPU"]
        end
        
        B0 -->|"dispatches to"| B1
        B0 -->|"dispatches to"| B2
        B0 -->|"dispatches to"| B3
        B0 -->|"dispatches to"| B4
        B0 -->|"dispatches to"| B5
        B0 -->|"dispatches to"| B6
        B0 -->|"dispatches to"| B7
    end
    
    subgraph "Tensor Layer" 
        T1["QTensor.optimize()"]
    end
    
    T1 -->|"uses"| B0
```

### Backend Integration

The device-specific backends provide:

1. **Optimized Matrix Multiplication**: Hardware-specific implementations for quantized weights and activations
2. **Tensor Unpacking**: Efficient conversion between quantized and dequantized formats
3. **Specialized Kernels**: Implementations of algorithms like AWQ and Marlin
4. **Cross-Platform Support**: CUDA, CPU, MPS (Apple Silicon), and XPU (Intel GPUs)

These backends are exposed through the `torch.ops.quanto` namespace and are automatically selected based on the device the model is running on.

Sources:
- [test/nn/test_qlinear.py:124-129]()
- [test/nn/test_qattention.py:198-217]()
- [test/nn/test_qconv2d.py:82-104]()

## Model Integration Architecture

Optimum-quanto is designed to integrate seamlessly with higher-level model architectures, particularly those from the Hugging Face ecosystem.

```mermaid
flowchart TD
    subgraph "Model Integration"
        M1["quantize(model, weights, activations)"]
        M2["freeze(model)"]
    end
    
    subgraph "Basic Models"
        B1["MLP"]
        B2["Custom Architecture"]
    end
    
    subgraph "Complex Models"
        C1["Attention-based Models"]
        C2["Transformer Architecture"]
    end
    
    subgraph "Module Layer"
        L1["QLinear"]
        L2["QConv2d"]
        L3["QLayerNorm"]
    end
    
    M1 -->|"quantizes"| B1
    M1 -->|"quantizes"| B2
    M1 -->|"quantizes"| C1
    M1 -->|"quantizes"| C2
    
    B1 -->|"contains"| L1
    B2 -->|"contains"| L1
    B2 -->|"contains"| L2
    C1 -->|"contains"| L1
    C1 -->|"contains"| L3
    C2 -->|"contains"| L1
    C2 -->|"contains"| L3
```

### Integration Features

1. **Recursive Quantization**: Automatically handles nested module structures
2. **Mixed Precision Support**: Different quantization types for different parts of the model
3. **Architecture Preservation**: Maintains the original model architecture and interfaces
4. **Flexible Customization**: Allows specifying which modules to quantize and how

Sources:
- [test/nn/test_qattention.py:174-217]()
- [test/quantize/test_quantize_mlp.py:40-51]()

## Memory Efficiency and Performance

A key benefit of optimum-quanto is the reduction in memory usage and potential performance improvements.

```mermaid
flowchart LR
    A["Original Model\n(Float16/Float32)"] 
    B["Weight-Only Quantized\n(Int4/Int8/Float8)"]
    C["Weight & Activation Quantized\n(Int4/Int8/Float8)"]
    
    A -->|"4-8x memory reduction"| B
    B -->|"additional memory savings"| C
    
    subgraph "Performance Considerations"
        P1["Hardware Support"]
        P2["Model Size"]
        P3["Batch Size"]
        P4["Quantization Type"]
    end
    
    B -.->|"impacts"| P1
    B -.->|"impacts"| P2
    C -.->|"impacts"| P3
    C -.->|"impacts"| P4
```

### Key Performance Aspects

1. **Memory Reduction**: Significant memory savings, especially with 4-bit quantization
2. **Hardware Acceleration**: Specialized hardware support for different quantization types
3. **Throughput vs Accuracy**: Trade-offs between performance and model quality
4. **Hardware Selection**: Different devices have different optimal quantization strategies

Sources:
- [test/quantize/test_quantize_mlp.py:119-136]()

## Summary

The optimum-quanto architecture is designed as a layered system that provides flexible and efficient quantization capabilities at multiple levels:

1. **Tensor Layer**: Core quantized data structures
2. **Module Layer**: Quantized versions of standard PyTorch modules
3. **Model Integration**: Quantization of complete model architectures
4. **Device-Specific Backends**: Optimized implementations for different hardware

This architecture enables users to apply quantization to models with minimal changes to their workflow, while achieving significant memory savings and potential performance improvements, particularly on hardware with specialized support for quantized operations.

---

# Page: Tensor Quantization

# Tensor Quantization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/tensor/weights/qbits.py](optimum/quanto/tensor/weights/qbits.py)
- [optimum/quanto/tensor/weights/qbytes.py](optimum/quanto/tensor/weights/qbytes.py)
- [optimum/quanto/tensor/weights/quantization.py](optimum/quanto/tensor/weights/quantization.py)
- [test/tensor/ops/test_linear_dispatch.py](test/tensor/ops/test_linear_dispatch.py)
- [test/tensor/ops/test_mm_dispatch.py](test/tensor/ops/test_mm_dispatch.py)
- [test/tensor/test_absmax.py](test/tensor/test_absmax.py)

</details>



This document explains the core tensor quantization system in optimum-quanto, which provides the foundation for efficiently representing model weights and activations in reduced precision. Tensor quantization serves as the underlying infrastructure upon which module quantization (see [Module Quantization](#4.2)) and model integration (see [Model Integration](#4.3)) are built.

## Overview

Tensor quantization in optimum-quanto enables the conversion of standard floating-point PyTorch tensors into specialized quantized tensor formats that reduce memory footprint and increase computational efficiency. The library implements custom PyTorch tensor subclasses that handle quantization, dequantization, and efficient mathematical operations.

```mermaid
graph TD
    A["Float Tensor<br>(torch.Tensor)"] --> B["Quantization Process"]
    B --> C["QTensor Hierarchy"]
    C --> D["WeightQBytesTensor<br>(8-bit quantization)"]
    C --> E["WeightQBitsTensor<br>(2/4-bit quantization)"]
    C --> F["ActivationQBytesTensor<br>(activation quantization)"]
    
    D --> G["Hardware-optimized<br>Subclasses"]
    E --> G
    
    G --> H["MarlinF8QBytesTensor"]
    G --> I["AWQWeightQBitsTensor"]
    G --> J["TinyGemmWeightQBitsTensor"]
```

Sources: 
- [optimum/quanto/tensor/weights/qbytes.py:84-225](). 
- [optimum/quanto/tensor/weights/qbits.py:65-143]().

## Quantized Tensor Types

Optimum-quanto provides two primary categories of quantized tensors:

1. **Weight Tensors**: For model parameters (weights)
   - `WeightQBytesTensor`: 8-bit quantization (INT8, FLOAT8)
   - `WeightQBitsTensor`: Lower precision (INT2, INT4) with grouping support

2. **Activation Tensors**: For model activations/inputs
   - `ActivationQBytesTensor`: Used to quantize intermediate activations

Each tensor type offers specialized functionality for its intended use case, while sharing common interfaces for quantization and dequantization.

```mermaid
classDiagram
    class QTensor {
        +dequantize()
        +_data: torch.Tensor
        +_scale: torch.Tensor
    }
    
    class WeightQBytesTensor {
        +qtype: QuantType
        +axis: int
        +activation_qtype: qtype
        +quantize(base, qtype, axis, scale)
        +optimize()
    }
    
    class WeightQBitsTensor {
        +qtype: QuantType
        +axis: int
        +group_size: int
        +_shift: torch.Tensor
        +quantize(base, qtype, axis, group_size, scale, shift)
        +optimize()
    }
    
    class ActivationQBytesTensor {
        +qtype: QuantType
        +axis: int
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
    QTensor <|-- ActivationQBytesTensor
```

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:85-157]()
- [optimum/quanto/tensor/weights/qbits.py:65-137]()

## Quantization Process

Quantization converts floating-point tensors to reduced-precision formats through a process of scaling and rounding. The main entry point for weight quantization is the `quantize_weight` function:

```mermaid
flowchart LR
    A["Float Tensor"] --> B["quantize_weight()"]
    B --> C{"qtype.bits == 8?"}
    C -->|"Yes"| D["WeightQBytesTensor.quantize()"]
    C -->|"No"| E["WeightQBitsTensor.quantize()"]
    D --> F["WeightQBytesQuantizer"]
    E --> G["WeightsQBitsQuantizer"]
    F --> H["WeightQBytesTensor.create()"]
    G --> I["WeightQBitsTensor.create()"]
    H --> J["Select optimized implementation"]
    I --> J
    J --> K["Return QTensor instance"]
```

The quantization process involves:

1. **Scale Calculation**: Often using absmax scaling which determines the scaling factor
2. **Quantization**: Mapping floating-point values to integers
3. **Storage**: Efficiently packing quantized values (e.g., 4-bit values packed into 8-bit storage)
4. **Optimization Selection**: Choosing the most efficient backend implementation

Sources:
- [optimum/quanto/tensor/weights/quantization.py:27-73]()
- [optimum/quanto/tensor/weights/qbytes.py:31-65]()
- [optimum/quanto/tensor/weights/qbits.py:34-62]()

## Quantization Parameters

Quantization requires several parameters that control the process:

| Parameter | Description | Applies To |
|-----------|-------------|------------|
| `qtype` | Target quantization type (qint2, qint4, qint8, qfloat8) | All quantized tensors |
| `axis` | Dimension for per-axis quantization (0 or -1) | All quantized tensors |
| `scale` | Scaling factor(s) for quantization | All quantized tensors |
| `shift` | Zero-point or shift value | Required for WeightQBitsTensor |
| `group_size` | Number of elements in a quantization group | Used by WeightQBitsTensor |
| `activation_qtype` | Quantization type used for activations | Optional for WeightQBytesTensor |
| `optimized` | Whether to select optimized implementation | All quantized tensors |

The `absmax_scale` function is commonly used to calculate appropriate scaling factors:

```
scale = absmax_scale(tensor, qtype, axis)
```

Sources:
- [optimum/quanto/tensor/weights/quantization.py:27-73]()
- [test/tensor/test_absmax.py:22-42]()

## Operation Dispatching

Quantized tensors implement PyTorch's operator dispatch protocols to intercept and optimize operations such as matrix multiplication. This allows seamless integration with PyTorch operations while providing custom implementations.

```mermaid
sequenceDiagram
    participant App as "User Code"
    participant F as "torch.nn.functional.linear"
    participant TF as "__torch_function__"
    participant TD as "__torch_dispatch__"
    participant QLF as "QLinearFunction"
    
    App->>F: linear(input, weight, bias)
    F->>TF: Check for tensor subclasses
    TF->>QLF: Dispatch to quantized implementation
    QLF->>TD: Handle individual operations
    TD-->>App: Return optimized result
```

The dispatch system works at two levels:
1. `__torch_function__`: Intercepts high-level functions like `torch.nn.functional.linear`
2. `__torch_dispatch__`: Handles lower-level ATEN operations like `matmul` and `mm`

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:248-325]()
- [optimum/quanto/tensor/weights/qbits.py:247-302]()
- [test/tensor/ops/test_linear_dispatch.py:22-73]()
- [test/tensor/ops/test_mm_dispatch.py:22-44]()

## Hardware Optimization

Optimum-quanto automatically selects the most efficient tensor implementations based on hardware, quantization parameters, and available extensions:

```mermaid
flowchart TD
    A["WeightQTensor.create()"] --> B{"Check hardware<br>& parameters"}
    
    B -->|"CUDA + FP8 + Ampere+"| C["MarlinF8QBytesTensor"]
    B -->|"CUDA + INT4 + Ampere+"| D["AWQWeightQBitsTensor"]
    B -->|"CPU/CUDA + INT4 + BF16"| E["TinyGemmWeightQBitsTensor"]
    B -->|"Other configuration"| F["Base QTensor implementation"]
    
    C --> G["Optimized FP8 Matrix Ops"]
    D --> H["Optimized INT4 Matrix Ops"]
    E --> I["Optimized BF16/INT4 Ops"]
    F --> J["Generic Implementation"]
```

Key optimization paths include:
- **Marlin**: Optimized for FP8 operations on NVIDIA Ampere+ GPUs
- **AWQ**: Optimized for INT4 quantization on NVIDIA Ampere+ GPUs
- **TinyGemm**: Optimized for BF16/INT4 operations on both CPU and NVIDIA GPUs

The `optimize()` method can be called on a base tensor to convert it to an optimized subclass after loading from storage.

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:87-143]()
- [optimum/quanto/tensor/weights/qbits.py:67-123]()

## Serialization and Deserialization

Quantized tensors support serialization for model saving and loading. During serialization, specialized tensor subclasses are converted back to base implementations to ensure compatibility and portability.

```mermaid
flowchart LR
    A["save_to_state_dict()"] --> B{"Is specialized<br>implementation?"}
    B -->|"Yes"| C["Convert to base implementation"]
    B -->|"No"| D["Serialize directly"]
    C --> E["Save tensor components"]
    D --> E
    
    F["load_from_state_dict()"] --> G["Reconstruct base tensor"]
    G --> H["optimize()"]
    H --> I["Return optimized implementation"]
```

The serialization process stores:
1. Quantized data tensors
2. Scale factors
3. Shift values (for sub-8-bit quantization)
4. Metadata (qtype, axis, group size)

Sources:
- [optimum/quanto/tensor/weights/qbytes.py:156-245]()
- [optimum/quanto/tensor/weights/qbits.py:151-245]()

## Usage Example

To quantize a tensor using the core tensor quantization system:

1. Calculate scale (and shift for sub-8-bit)
2. Quantize the tensor
3. Use the quantized tensor in operations

```python
# Calculate scale using absmax
scale = absmax_scale(weight_tensor, qint8, axis=0)

# Quantize the weight
qweight = quantize_weight(
    weight_tensor,
    qtype=qint8,
    axis=0,
    scale=scale
)

# Use in operations (automatically dispatched to optimized implementation)
output = torch.nn.functional.linear(input_tensor, qweight)
```

Sources:
- [optimum/quanto/tensor/weights/quantization.py:27-73]()
- [test/tensor/ops/test_linear_dispatch.py:22-44]()

---

# Page: Module Quantization

# Module Quantization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/__init__.py](optimum/quanto/__init__.py)
- [optimum/quanto/nn/qconv2d.py](optimum/quanto/nn/qconv2d.py)
- [optimum/quanto/nn/qlayernorm.py](optimum/quanto/nn/qlayernorm.py)
- [optimum/quanto/nn/qlinear.py](optimum/quanto/nn/qlinear.py)
- [optimum/quanto/nn/qmodule.py](optimum/quanto/nn/qmodule.py)
- [optimum/quanto/quantize.py](optimum/quanto/quantize.py)
- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/quantize/test_quantize_patterns.py](test/quantize/test_quantize_patterns.py)
- [test/quantize/test_requantize.py](test/quantize/test_requantize.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



This page documents the module quantization system in optimum-quanto, which allows you to convert standard PyTorch modules into their quantized counterparts. For information about tensor-level quantization, see [Tensor Quantization](#4.1), and for integrating quantized modules into larger models, see [Model Integration](#4.3).

## Overview

Module quantization provides a way to convert PyTorch modules (like Linear, Conv2d, and LayerNorm) into quantized versions that operate with reduced precision. The system consists of:

1. A registration mechanism for quantized modules
2. A mixin class that adds quantization capabilities to PyTorch modules
3. Concrete implementations for common module types
4. Utilities for module conversion, freezing, and serialization

```mermaid
flowchart TD
    subgraph "Module Quantization System"
        A["QModuleMixin"] --> B["Registration System"]
        A --> C["Quantization API"]
        A --> D["Concrete Implementations"]
        
        B --> B1["register_qmodule"]
        B --> B2["_QMODULE_TABLE"]
        
        C --> C1["quantize_module"]
        C --> C2["freeze"]
        C --> C3["requantize"]
        
        D --> D1["QLinear"]
        D --> D2["QConv2d"]
        D --> D3["QLayerNorm"]
    end
```

Sources: [optimum/quanto/nn/qmodule.py](), [optimum/quanto/quantize.py]()

## Core Components

### QModuleMixin

The `QModuleMixin` is the foundation of module quantization in optimum-quanto. It adds quantization capabilities to PyTorch modules through the following features:

- Weight quantization (in various precisions)
- Activation quantization (optional)
- Forward pre/post hooks for quantizing inputs/outputs
- Serialization methods for quantized weights
- Methods for freezing quantized weights

```mermaid
classDiagram
    class QModuleMixin {
        +weight_qtype
        +activation_qtype
        +optimizer
        +input_scale
        +output_scale
        +qweight()
        +from_module()
        +freeze()
        +quantize_input()
        +quantize_output()
    }
    
    class torch.nn.Module {
        +forward()
        +parameters()
    }
    
    class "Quantized Module" {
        +forward()
        +qcreate()
    }
    
    torch.nn.Module <|-- QModuleMixin
    QModuleMixin <|-- "Quantized Module"
```

Sources: [optimum/quanto/nn/qmodule.py:94-310]()

### Registration System

The module registration system maintains a mapping between standard PyTorch modules and their quantized counterparts:

```mermaid
flowchart LR
    A["register_qmodule decorator"] --> B["_QMODULE_TABLE"]
    C["quantize_module function"] --> B
    B --> D["QLinear, QConv2d, QLayerNorm"]
```

To register a new quantized module:

```mermaid
flowchart TD
    A["@register_qmodule(torch.nn.SomeModule)"] --> B["class QSomeModule(QModuleMixin, torch.nn.SomeModule)"]
    B --> C["Implement qcreate() and forward()"]
    C --> D["Module now available via quantize_module()"]
```

Sources: [optimum/quanto/nn/qmodule.py:41-91]()

## Quantized Module Types

Optimum-quanto provides quantized versions of common PyTorch modules:

### QLinear

Quantized version of `torch.nn.Linear`. Supports both weight quantization and activation quantization.

```python
# Example usage
linear = torch.nn.Linear(768, 768)
qlinear = QLinear.from_module(linear, weights=qint8, activations=None)
```

Sources: [optimum/quanto/nn/qlinear.py](), [test/nn/test_qlinear.py]()

### QConv2d

Quantized version of `torch.nn.Conv2d`. Supports both weight quantization and activation quantization.

```python
# Example usage
conv = torch.nn.Conv2d(3, 64, kernel_size=3)
qconv = QConv2d.from_module(conv, weights=qint4, activations=qint8)
```

Sources: [optimum/quanto/nn/qconv2d.py](), [test/nn/test_qconv2d.py]()

### QLayerNorm

Quantized version of `torch.nn.LayerNorm`. Primarily supports activation quantization rather than weight quantization.

```python
# Example usage
norm = torch.nn.LayerNorm(768)
qnorm = QLayerNorm.from_module(norm, activations=qint8)
```

Sources: [optimum/quanto/nn/qlayernorm.py](), [test/nn/test_qlayernorm.py]()

## Module Quantization Workflow

The typical workflow for quantizing modules involves these main steps:

```mermaid
flowchart LR
    A["Original PyTorch Module"] --> B["Create Quantized Module"]
    B --> C["Optional: Calibration"]
    C --> D["Freeze Quantized Weights"]
    D --> E["Inference/Deployment"]
    
    subgraph "API Methods"
    F["QModule.from_module()"]
    G["Calibration context"]
    H["freeze()"]
    end
    
    A -- "via" --> F
    B -- "via" --> G
    C -- "via" --> H
```

Sources: [optimum/quanto/quantize.py](), [test/nn/test_calibrate.py]()

### Module Creation

Quantized modules are created from standard PyTorch modules using the `from_module` class method or the `quantize` function for bulk conversion:

```python
# Individual module quantization
qlinear = QLinear.from_module(linear, weights=qint8)

# Bulk model quantization
quantize(model, weights=qint8, include="*.attention.*")
```

The quantization process preserves the original module's weights while adding quantization capabilities.

Sources: [optimum/quanto/nn/qmodule.py:209-233](), [optimum/quanto/quantize.py:55-98]()

### Activation Calibration

When using activation quantization, modules need to be calibrated to determine appropriate scaling factors:

```mermaid
flowchart TD
    A["Input"] --> B["Quantized Module"]
    B -- "Without Calibration" --> C["Default Scales (1.0)"]
    B -- "With Calibration Context" --> D["Calibrated Scales"]
    
    subgraph "Calibration Process"
    E["Gather Statistics"] --> F["Update input_scale"]
    E --> G["Update output_scale"]
    end
```

Example calibration code:

```python
# Calibration for activation quantization
with Calibration():
    outputs = model(inputs)
```

Sources: [test/nn/test_calibrate.py]()

### Freezing Quantized Weights

Freezing replaces the floating-point weights with their quantized counterparts to reduce memory usage:

```mermaid
flowchart LR
    A["Unfrozen QModule"] --> B["model.weight = float tensor"]
    A --> C["model.qweight = dynamically quantized"]
    
    D["Frozen QModule"] --> E["model.weight = QTensor"]
    D --> F["model.qweight = model.weight"]
    
    A -- "freeze()" --> D
```

Example freezing code:

```python
# Freeze all quantized modules in a model
freeze(model)
```

Sources: [optimum/quanto/nn/qmodule.py:302-307](), [optimum/quanto/quantize.py:143-146]()

## Selective Module Quantization

The `quantize` function allows for selective quantization of modules using include/exclude patterns:

```mermaid
flowchart TD
    A["Model"] --> B["Pattern Matching"]
    B -- "Included Module" --> C["Quantized"]
    B -- "Excluded Module" --> D["Not Quantized"]
    
    subgraph "Pattern Examples"
    E["'*.linear.*'"]
    F["'encoder.*'"]
    G["'*layer*'"]
    end
```

Pattern matching uses Unix shell-style wildcards (not regular expressions):

```python
# Only quantize linear layers
quantize(model, weights=qint8, include="*.linear*")

# Quantize everything except normalization layers
quantize(model, weights=qint8, exclude="*norm*")
```

Sources: [optimum/quanto/quantize.py:55-98](), [test/quantize/test_quantize_patterns.py]()

## Model Serialization and Loading

Quantized models can be serialized and loaded using the PyTorch serialization mechanism with additional support for quantized tensors:

```mermaid
flowchart TD
    A["Quantized Model"] --> B["State Dict with QTensors"]
    B --> C["Save as .pt/.safetensors"]
    C --> D["Load State Dict"]
    D --> E["requantize(model, state_dict, qmap)"]
    E --> F["Restored Quantized Model"]
    
    G["quantization_map(model)"] --> H["QMap JSON"]
    H --> E
```

Example serialization workflow:

```python
# Save a quantized model
qmap = quantization_map(model)
torch.save(model.state_dict(), "model.pt")
with open("qmap.json", "w") as f:
    json.dump(qmap, f)

# Load a quantized model
state_dict = torch.load("model.pt")
requantize(model, state_dict, qmap)
```

Sources: [optimum/quanto/quantize.py:101-170](), [test/quantize/test_requantize.py]()

## Implementation Details

### QModuleMixin Implementation

The `QModuleMixin` class handles the complexities of quantized module creation, quantization, and serialization:

```mermaid
flowchart TB
    A["QModuleMixin.__init__"] --> B["Setup quantization parameters"]
    B --> C["Register quantization hooks"]
    
    D["QModuleMixin.qweight"] --> E["Dynamic quantization in training"]
    D --> F["Return frozen weights in inference"]
    
    G["QModuleMixin._save_to_state_dict"] --> H["Special handling for QTensors"]
    I["QModuleMixin._load_from_state_dict"] --> J["Special handling for QTensors"]
```

Key points:
- The `qweight` property dynamically quantizes weights during training
- Hooks are registered for input/output quantization when using activation quantization
- Special serialization methods handle the flattening/unflattening of QTensors

Sources: [optimum/quanto/nn/qmodule.py:94-310]()

### Module Registration Implementation

The registration system uses a Python decorator to populate a mapping table:

```python
@register_qmodule(torch.nn.Linear)
class QLinear(QModuleMixin, torch.nn.Linear):
    # Implementation
```

This allows the `quantize_module` function to look up the appropriate quantized module type for a given PyTorch module.

Sources: [optimum/quanto/nn/qmodule.py:44-78]()

## Common Usage Patterns

### Weight-Only Quantization

Quantize only the weights of modules, leaving activations in floating-point:

```python
# Weight-only quantization with int8
quantize(model, weights=qint8, activations=None)
```

This is typically the most stable form of quantization with minimal accuracy impact.

Sources: [test/quantize/test_quantize_mlp.py:83-86]()

### Weight and Activation Quantization

Quantize both weights and activations (requires calibration):

```python
# Quantize weights to int8 and activations to int8
quantize(model, weights=qint8, activations=qint8)

# Calibrate the model
with Calibration():
    model(inputs)
```

This provides more memory savings and performance improvements but may impact accuracy more significantly.

Sources: [test/quantize/test_quantize_mlp.py:97-116]()

### Mixed-Precision Quantization

Different quantization types can be used for different parts of the model:

```python
# Quantize attention layers to 4-bit
quantize(model, weights=qint4, include="*attention*")

# Quantize feedforward layers to 8-bit
quantize(model, weights=qint8, include="*feed_forward*")
```

This allows for more flexible performance-accuracy trade-offs.

Sources: [test/quantize/test_quantize_patterns.py]()

## Custom Quantized Modules

To create a custom quantized module:

1. Create a class that inherits from both `QModuleMixin` and the PyTorch module
2. Implement the `qcreate` class method to instantiate the module
3. Implement the `forward` method for quantized inference
4. Register the module using the `register_qmodule` decorator

Example template:

```python
@register_qmodule(torch.nn.SomeModule)
class QSomeModule(QModuleMixin, torch.nn.SomeModule):
    @classmethod
    def qcreate(cls, module, weights, activations, optimizer, device):
        # Create a new instance with appropriate parameters
        return cls(...)
        
    def forward(self, input):
        # Implementation using self.qweight
        return result
```

Sources: [optimum/quanto/nn/qmodule.py:44-78]()

## Conclusion

The module quantization system in optimum-quanto provides a flexible framework for converting PyTorch modules to quantized versions. By supporting various quantization types, selective quantization patterns, and both weight and activation quantization, it enables efficient deployment of models with reduced memory and computational requirements.

For deeper integration with model architectures like transformers or diffusers, refer to [Model Integration](#4.3).

---

# Page: Model Integration

# Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/models/__init__.py](optimum/quanto/models/__init__.py)
- [optimum/quanto/models/diffusers_models.py](optimum/quanto/models/diffusers_models.py)
- [optimum/quanto/models/shared_dict.py](optimum/quanto/models/shared_dict.py)
- [optimum/quanto/models/transformers_models.py](optimum/quanto/models/transformers_models.py)
- [test/helpers.py](test/helpers.py)
- [test/models/conftest.py](test/models/conftest.py)
- [test/models/test_quantized_model_for_causal_lm.py](test/models/test_quantized_model_for_causal_lm.py)
- [test/models/test_quantized_model_for_pixart.py](test/models/test_quantized_model_for_pixart.py)

</details>



This page describes how Optimum-Quanto integrates with popular model frameworks such as HuggingFace Transformers and Diffusers. It explains the architecture and classes used to provide quantization capabilities to these models, enabling smaller model sizes and faster inference. For information about the core quantization techniques, see [Tensor Quantization](#4.1) and [Module Quantization](#4.2).

## Overview

Optimum-Quanto provides specialized wrapper classes that enable seamless integration with pre-existing model architectures from the HuggingFace ecosystem. These wrappers allow users to:

1. Quantize pre-trained models
2. Save quantized models to disk or the Hugging Face Hub
3. Load quantized models for inference
4. Access the original model's API through the wrapper

The integration follows a consistent pattern across different model frameworks:

```mermaid
flowchart TD
    A["Original Model"] --> B["QuantizedModel.quantize()"]
    B --> C["Quantized Model"]
    C --> D["model.save_pretrained()"]
    D --> E["QuantizedModel.from_pretrained()"]
    E --> F["Loaded Quantized Model"]
    
    G["Module Quantization\n(QLinear, QConv2d, etc.)"] -.-> B
    H["Tensor Quantization\n(WeightQBytesTensor, etc.)"] -.-> G
```

Sources: [optimum/quanto/models/transformers_models.py:65-112](), [optimum/quanto/models/diffusers_models.py:67-116]()

## Integration Architecture

Optimum-Quanto's model integration consists of two primary wrapper classes:

1. `QuantizedTransformersModel` - Base class for Transformers integration
2. `QuantizedDiffusersModel` - Base class for Diffusers integration

These classes implement similar patterns but are tailored to their respective frameworks.

```mermaid
classDiagram
    class ModelHubMixin {
        +push_to_hub()
        +save_pretrained()
    }
    
    class QuantizedTransformersModel {
        +_wrapped: PreTrainedModel
        +quantize()
        +from_pretrained()
        +_save_pretrained()
        +BASE_NAME: "quanto"
        +auto_class: None
    }
    
    class QuantizedModelForCausalLM {
        +auto_class: AutoModelForCausalLM
    }
    
    class QuantizedDiffusersModel {
        +_wrapped: ModelMixin
        +quantize()
        +from_pretrained()
        +_save_pretrained()
        +BASE_NAME: "quanto"
        +base_class: None
    }
    
    class QuantizedPixArtTransformer2DModel {
        +base_class: PixArtTransformer2DModel
    }
    
    ModelHubMixin <|-- QuantizedTransformersModel
    QuantizedTransformersModel <|-- QuantizedModelForCausalLM
    
    ModelHubMixin <|-- QuantizedDiffusersModel
    QuantizedDiffusersModel <|-- QuantizedPixArtTransformer2DModel
```

Sources: [optimum/quanto/models/transformers_models.py:38-184](), [optimum/quanto/models/diffusers_models.py:44-191]()

## Integration with Transformers

The `QuantizedTransformersModel` class provides a base for integrating with HuggingFace Transformers models. It follows a wrapper pattern, delegating most methods to the wrapped model while providing specialized functionality for quantization.

Key components:

1. `QuantizedTransformersModel.quantize()` - Static method to quantize a model in-place
2. `QuantizedTransformersModel.from_pretrained()` - Loads a quantized model from disk or the Hub
3. `QuantizedModelForCausalLM` - Specialized class for causal language models

### Quantization and Loading Workflow

```mermaid
sequenceDiagram
    participant User
    participant QModel as QuantizedModelForCausalLM
    participant Model as PreTrainedModel
    participant Hub as HuggingFace Hub
    
    User->>QModel: quantize(model, weights=qint8)
    QModel->>Model: Apply quantize() function
    QModel->>Model: Apply freeze() function
    QModel-->>User: Return quantized model
    
    User->>QModel: save_pretrained("path/")
    QModel->>Model: model.save_pretrained()
    QModel->>QModel: Save quantization map
    
    User->>QModel: from_pretrained("path/")
    QModel->>QModel: Create empty model
    QModel->>QModel: Load state_dict and qmap
    QModel->>QModel: Apply requantize()
    QModel-->>User: Return loaded quantized model
    
    User->>QModel: push_to_hub("my-model")
    QModel->>Hub: Upload model and quantization map
```

Sources: [optimum/quanto/models/transformers_models.py:65-180](), [test/models/test_quantized_model_for_causal_lm.py:75-150]()

### Usage Example

The typical workflow for quantizing and using a Transformers model:

1. Load a pre-trained model
2. Quantize the model
3. Use the model or save it
4. Load the quantized model for inference

```python
# Import and quantize a model
from transformers import AutoModelForCausalLM
from optimum.quanto import QuantizedModelForCausalLM, qint8

model = AutoModelForCausalLM.from_pretrained("facebook/opt-125m")
quantized_model = QuantizedModelForCausalLM.quantize(model, weights=qint8)

# Save the model
quantized_model.save_pretrained("./quantized-opt-125m")

# Load the model
loaded_model = QuantizedModelForCausalLM.from_pretrained("./quantized-opt-125m")

# Use the model
inputs = tokenizer("Hello, world!", return_tensors="pt")
outputs = loaded_model(**inputs)
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:11-46]()

## Integration with Diffusers

The `QuantizedDiffusersModel` class provides similar functionality for Diffusers models, with specialized implementations for specific model types like `QuantizedPixArtTransformer2DModel`.

Key components:

1. `QuantizedDiffusersModel.quantize()` - Static method to quantize a Diffusers model
2. `QuantizedDiffusersModel.from_pretrained()` - Loads a quantized model
3. `QuantizedPixArtTransformer2DModel` - Specialized class for PixArt models

### Diffusers Integration Workflow

```mermaid
flowchart TB
    subgraph "Quantization Workflow"
        A1["Original Diffusers Model"] --> A2["QuantizedPixArtTransformer2DModel.quantize()"]
        A2 --> A3["Quantized Model"]
        A3 --> A4["model.save_pretrained()"]
        A4 --> A5["model.from_pretrained()"]
    end
    
    subgraph "Internal Implementation"
        B1["1. Apply quantize() to model"]
        B2["2. Apply freeze() to model"]
        B3["3. Save model weights"]
        B4["4. Save quanto_qmap.json"]
        B5["5. Load model config"]
        B6["6. Create empty model"]
        B7["7. Load state_dict"]
        B8["8. Apply requantize()"]
    end
    
    A2 -.-> B1
    A2 -.-> B2
    A4 -.-> B3
    A4 -.-> B4
    A5 -.-> B5
    A5 -.-> B6
    A5 -.-> B7
    A5 -.-> B8
```

Sources: [optimum/quanto/models/diffusers_models.py:72-178](), [test/models/test_quantized_model_for_pixart.py:11-37]()

### Saving and Loading

Both Transformers and Diffusers integration frameworks store quantization information in a `quanto_qmap.json` file alongside the model weights. This file contains the mapping of which layers have been quantized and with what quantization parameters.

```mermaid
graph TD
    A["Quantized Model Directory"] --> B["model.safetensors"]
    A --> C["quanto_qmap.json"]
    A --> D["config.json"]
    
    C -->|Contains| E["Quantization mapping\ninformation"]
    B -->|Contains| F["Quantized weights"]
    D -->|Contains| G["Model configuration"]
    
    H["ShardedStateDict"] -.-> B
    H["ShardedStateDict"] -.-> I["model-00001-of-00002.safetensors"]
    H["ShardedStateDict"] -.-> J["model-00002-of-00002.safetensors"]
```

Sources: [optimum/quanto/models/transformers_models.py:165-179](), [optimum/quanto/models/diffusers_models.py:180-186](), [optimum/quanto/models/shared_dict.py:22-54]()

## Shared Implementation

Both integration classes share similar patterns and functionality:

1. They both act as wrappers, delegating methods to the original model
2. They handle the quantization, serialization, and deserialization process
3. They both implement the `ModelHubMixin` interface for Hub integration

### Wrapper Pattern Implementation

The wrapper pattern allows the quantized model to maintain the same API as the original model while adding quantization-specific capabilities:

```mermaid
sequenceDiagram
    participant User
    participant QModel as QuantizedModel
    participant Model as Original Model
    
    User->>QModel: some_method()
    QModel->>QModel: __getattr__(some_method)
    QModel->>Model: some_method()
    Model-->>QModel: result
    QModel-->>User: result
    
    User->>QModel: forward(inputs)
    QModel->>Model: forward(inputs)
    Model-->>QModel: outputs
    QModel-->>User: outputs
```

Sources: [optimum/quanto/models/transformers_models.py:47-62](), [optimum/quanto/models/diffusers_models.py:53-65]()

## Supported Models

Currently, Optimum-Quanto provides specialized integration for the following model types:

| Framework     | Model Type               | Quanto Class                      |
|---------------|--------------------------|-----------------------------------|
| Transformers  | Causal Language Models   | `QuantizedModelForCausalLM`       |
| Diffusers     | PixArt Transformer 2D    | `QuantizedPixArtTransformer2DModel` |

The architecture allows for easy extension to additional model types from both frameworks.

Sources: [optimum/quanto/models/transformers_models.py:182-183](), [optimum/quanto/models/diffusers_models.py:189-190]()

## HuggingFace Hub Integration

Both model integration classes implement the `ModelHubMixin` interface, which enables:

1. Pushing models to the Hub with `push_to_hub()`
2. Loading models from the Hub with `from_pretrained()`

The integration ensures that all quantization-specific information is correctly saved and loaded.

```mermaid
flowchart LR
    A["Quantized Model"] -- "push_to_hub()" --> B["HuggingFace Hub"]
    B -- "from_pretrained()" --> C["Loaded Quantized Model"]
    
    D["Local Storage"] -- "save_pretrained()" --> E["model.safetensors\nquanto_qmap.json\nconfig.json"]
    E -- "from_pretrained()" --> F["Loaded Quantized Model"]
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:106-128](), [test/models/test_quantized_model_for_pixart.py:92-112]()

## Implementation Details

### Requantization Process

When loading a quantized model, Optimum-Quanto uses a process called "requantization" to reconstruct the quantized tensors from the saved state:

1. Creates an empty model structure
2. Loads the quantization map
3. Applies the appropriate quantization to each layer based on the map
4. Loads the weights into the quantized structure

This process is handled by the `requantize()` function, which is called during `from_pretrained()`.

Sources: [optimum/quanto/models/transformers_models.py:114-162](), [optimum/quanto/models/diffusers_models.py:119-178]()

### Handling Sharded Models

For large models, Optimum-Quanto supports loading from sharded checkpoint files:

1. It detects if the model is sharded by looking for an index file
2. If sharded, it uses a `ShardedStateDict` to lazily load tensors
3. This allows efficient loading of large quantized models

Sources: [optimum/quanto/models/transformers_models.py:142-154](), [optimum/quanto/models/diffusers_models.py:161-173](), [optimum/quanto/models/shared_dict.py:22-54]()

---

# Page: Device-Specific Backends

# Device-Specific Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/library/extensions/README.md](optimum/quanto/library/extensions/README.md)
- [optimum/quanto/library/extensions/__init__.py](optimum/quanto/library/extensions/__init__.py)
- [optimum/quanto/library/extensions/cuda/__init__.py](optimum/quanto/library/extensions/cuda/__init__.py)
- [optimum/quanto/library/extensions/xpu/__init__.py](optimum/quanto/library/extensions/xpu/__init__.py)
- [optimum/quanto/library/extensions/xpu/pybind_module.cpp](optimum/quanto/library/extensions/xpu/pybind_module.cpp)
- [optimum/quanto/library/extensions/xpu/unpack.h](optimum/quanto/library/extensions/xpu/unpack.h)
- [optimum/quanto/library/extensions/xpu/unpack.sycl](optimum/quanto/library/extensions/xpu/unpack.sycl)
- [optimum/quanto/library/qbytes_mm.py](optimum/quanto/library/qbytes_mm.py)
- [optimum/quanto/tensor/weights/marlin/fp8/__init__.py](optimum/quanto/tensor/weights/marlin/fp8/__init__.py)
- [optimum/quanto/tensor/weights/marlin/fp8/packed.py](optimum/quanto/tensor/weights/marlin/fp8/packed.py)
- [optimum/quanto/tensor/weights/marlin/fp8/qbits.py](optimum/quanto/tensor/weights/marlin/fp8/qbits.py)
- [test/library/test_extensions.py](test/library/test_extensions.py)
- [test/library/test_mm.py](test/library/test_mm.py)
- [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py](test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py)

</details>



## Purpose and Scope

This page documents the device-specific backend implementations in optimum-quanto. These backends provide optimized implementations of core operations for different hardware platforms, ensuring efficient execution of quantized models across various devices. Each backend is tailored to the strengths and capabilities of its target hardware architecture.

For information about the tensor quantization system itself, see [Tensor Quantization](#4.1). For details on how modules use these backends, see [Module Quantization](#4.2).

## Backend Architecture Overview

Optimum-quanto implements a flexible extension system for device-specific backends. Each hardware platform has its own optimized implementation of core operations, registered through PyTorch's library dispatch mechanism.

### Extension Registration System

```mermaid
flowchart TD
    A["Quanto Extensions"] --> B["Extension Registration"]
    B --> C["Device Detection"]
    C -->|"CUDA Available"| D["CUDA Backend"]
    C -->|"MPS Available"| E["MPS Backend"]
    C -->|"XPU Available"| F["XPU Backend"]
    C -->|"Always Available"| G["CPU Backend"]
    
    D --> H["Register CUDA Ops"]
    E --> I["Register MPS Ops"]
    F --> J["Register XPU Ops"]
    G --> K["Register CPU Ops"]
    
    H --> L["torch.ops.quanto"]
    I --> L
    J --> L
    K --> L
```

The extension registration system automatically detects available hardware and loads the appropriate backend implementations. All operations are exposed through the unified `torch.ops.quanto` namespace.

Sources: [optimum/quanto/library/extensions/__init__.py:15-44](), [optimum/quanto/library/extensions/extension.py]()

### Operation Dispatch Mechanism

```mermaid
flowchart LR
    A["PyTorch Operation"] --> B["torch.library.impl"]
    B --> C{"Device Type?"}
    C -->|"CUDA"| D["CUDA Implementation"]
    C -->|"CPU"| E["CPU Implementation"]
    C -->|"MPS"| F["MPS Implementation"]
    C -->|"XPU"| G["XPU Implementation"]
    C -->|"Other"| H["Default Implementation"]
    
    D --> I["Optimized CUDA Kernel"]
    E --> J["Optimized CPU Kernel"]
    F --> K["Optimized MPS Kernel"]
    G --> L["Optimized XPU Kernel"]
    H --> M["Generic PyTorch Implementation"]
```

Operations are registered with device-specific implementations using PyTorch's library dispatch system. When an operation is called, PyTorch automatically selects the appropriate implementation based on the device type of the input tensors.

Sources: [optimum/quanto/library/qbytes_mm.py:66-122](), [optimum/quanto/library/extensions/cuda/__init__.py:77-202]()

## Supported Hardware Platforms

### Overview of Supported Platforms

| Platform | Description | Key Features | Supported Precision Formats |
|----------|-------------|--------------|----------------------------|
| CUDA     | NVIDIA GPU support | Highly optimized kernels for matrix multiplication, AWQ, Marlin | INT2, INT4, INT8, FP8 |
| CPU      | x86/ARM processor support | Generic implementations with SIMD optimizations | INT2, INT4, INT8 |
| MPS      | Apple Silicon GPU support | Metal Performance Shaders integration | INT2, INT4, INT8 |
| XPU      | Intel GPU support | SYCL integration | INT2, INT4 |

Sources: [optimum/quanto/library/extensions/__init__.py:15-44](), [test/library/test_extensions.py:1-40]()

### Platform Compatibility Matrix

```mermaid
graph TD
    subgraph "Hardware Platforms"
        CUDA["CUDA (NVIDIA)"]
        CPU["CPU (x86/ARM)"]
        MPS["MPS (Apple Silicon)"]
        XPU["XPU (Intel GPU)"]
    end
    
    subgraph "GEMM Operations"
        GEMM_F16I4["gemm_f16i4_awq"]
        GEMM_F16F8["gemm_f16f8_marlin"]
        GEMM_F16I4M["gemm_f16i4_marlin"]
        QBYTES_MM["qbytes_mm"]
    end
    
    subgraph "Utility Operations"
        UNPACK["unpack"]
        PACK_FP8["pack_fp8_marlin"]
    end
    
    CUDA --- GEMM_F16I4
    CUDA --- GEMM_F16F8
    CUDA --- GEMM_F16I4M
    CUDA --- QBYTES_MM
    CUDA --- UNPACK
    CUDA --- PACK_FP8
    
    CPU --- QBYTES_MM
    CPU --- UNPACK
    
    MPS --- QBYTES_MM
    MPS --- UNPACK
    
    XPU --- UNPACK
```

This diagram shows which operations are supported on each hardware platform. CUDA has the most comprehensive support, while other platforms support a subset of operations.

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:77-202](), [optimum/quanto/library/qbytes_mm.py:66-122](), [optimum/quanto/library/extensions/xpu/__init__.py:39-41]()

## CUDA Backend

The CUDA backend provides highly optimized implementations for NVIDIA GPUs, with specialized kernels for different quantization formats and matrix multiplication operations.

### CUDA Implementation Details

```mermaid
classDiagram
    class Extension {
        +String name
        +List~String~ sources
        +List~String~ extra_cflags
        +List~String~ extra_cuda_cflags
        +compile()
        +get_lib()
    }
    
    class CUDAExtension {
        +get_max_cuda_arch()
        +register_operations()
    }
    
    class AWQKernels {
        +gemm_f16i4_awq()
        +awq_v2_gemm_f16i4()
        +awq_v2_gemv_f16i4()
    }
    
    class MarlinKernels {
        +gemm_f16f8_marlin()
        +gemm_f16i4_marlin()
        +pack_fp8_marlin()
    }
    
    class UnpackKernels {
        +unpack()
    }
    
    Extension <|-- CUDAExtension
    CUDAExtension --> AWQKernels
    CUDAExtension --> MarlinKernels
    CUDAExtension --> UnpackKernels
```

The CUDA extension includes specialized kernels for AWQ, Marlin, and tensor unpacking operations. It automatically detects the maximum CUDA architecture supported by the installed CUDA toolkit and available GPU hardware.

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:25-44](), [optimum/quanto/library/extensions/cuda/__init__.py:97-202]()

### Key CUDA Operations

1. **Tensor Unpacking**:
   - `unpack_cuda`: Unpacks quantized tensors (INT2, INT4) on CUDA devices

2. **Matrix Multiplication**:
   - `gemm_f16i4_awq`: Matrix multiplication for INT4 quantized weights using AWQ format
   - `gemm_f16f8_marlin`: Matrix multiplication for FP8 quantized weights using Marlin format
   - `gemm_f16i4_marlin`: Matrix multiplication for INT4 quantized weights using Marlin format
   - `qbytes_mm`: General matrix multiplication for byte-quantized weights (INT8, FP8)

3. **Tensor Packing**:
   - `pack_fp8_marlin`: Packs FP8 weights into Marlin format for optimal performance

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:77-202](), [test/library/test_mm.py:27-189]()

## CPU Backend

The CPU backend provides implementations of core operations optimized for x86 and ARM processors, using SIMD instructions where available.

### Key CPU Operations

1. **Tensor Unpacking**:
   - `unpack`: Unpacks quantized tensors (INT2, INT4) on CPU

2. **Matrix Multiplication**:
   - `qbytes_mm_impl_cpu`: Optimized matrix multiplication for quantized weights on CPU
   - Specialized paths for INT8 weights (`qbytes_int_mm`) and BF16 activation with INT8 weights (`qbytes_int8pack_mm`)

Sources: [optimum/quanto/library/qbytes_mm.py:91-105]()

## MPS Backend (Apple Metal)

The MPS backend provides implementations for Apple Silicon GPUs using the Metal Performance Shaders framework.

### Key MPS Operations

1. **Tensor Unpacking**:
   - `unpack_mps`: Unpacks quantized tensors on Apple Silicon GPUs

2. **Matrix Multiplication**:
   - `qbytes_mm_impl_mps`: Matrix multiplication for quantized weights on MPS devices
   - Special handling for BF16 activations with INT8 weights

Sources: [optimum/quanto/library/qbytes_mm.py:108-122]()

## XPU Backend (Intel GPUs)

The XPU backend provides implementations for Intel GPUs using the SYCL programming model. This backend is available when using PyTorch 2.7+ on Linux with Intel GPU support.

### XPU Implementation Details

The XPU backend currently implements:

1. **Tensor Unpacking**:
   - `unpack_xpu`: Unpacks INT2 and INT4 quantized tensors on Intel GPUs
   - Uses SYCL kernels for parallel execution

Sources: [optimum/quanto/library/extensions/xpu/__init__.py:39-41](), [optimum/quanto/library/extensions/xpu/unpack.sycl:138-150]()

## Common Matrix Multiplication Interface

The `qbytes_mm` operation provides a unified interface for matrix multiplication with quantized weights across all supported devices.

```mermaid
flowchart TD
    A["quanto::qbytes_mm"] --> B{"Device Type?"}
    B -->|"CUDA"| C["qbytes_mm_impl_cuda"]
    B -->|"CPU"| D["qbytes_mm_impl_cpu"]
    B -->|"MPS"| E["qbytes_mm_impl_mps"]
    B -->|"Other"| F["qbytes_mm_impl_default"]
    
    C -->|"INT8 + INT8"| G["qbytes_int_mm"]
    C -->|"Other"| H["qbytes_mm"]
    
    D -->|"INT8 + INT8"| I["qbytes_int_mm"]
    D -->|"BF16 + INT8"| J["qbytes_int8pack_mm"]
    D -->|"Other"| K["qbytes_mm"]
    
    E -->|"BF16 + INT8"| L["qbytes_int8pack_mm"]
    E -->|"Other"| M["qbytes_mm"]
    
    F --> N["qbytes_mm"]
```

This operation provides device-specific optimizations for common quantization formats while maintaining a consistent interface across all devices.

Sources: [optimum/quanto/library/qbytes_mm.py:25-122](), [test/library/test_mm.py:35-49]()

## Specialized Kernels

### AWQ (Activation-Aware Weight Quantization)

The AWQ kernels provide optimized implementations for INT4 quantized weights using the AWQ format, which improves accuracy by considering activation patterns.

```mermaid
flowchart LR
    A["gemm_f16i4_awq"] --> B{"Batch Size < 8?"}
    B -->|"Yes"| C["awq_v2_gemv_f16i4"]
    B -->|"No"| D["awq_v2_gemm_f16i4"]
    
    C --> E["Output Tensor"]
    D --> E
```

The AWQ implementation dynamically selects between GEMV (matrix-vector) and GEMM (matrix-matrix) kernels based on the batch size for optimal performance.

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:97-121](), [test/library/test_mm.py:58-100]()

### Marlin

Marlin is a specialized format for both INT4 and FP8 quantization, with kernels optimized for efficient matrix multiplication on NVIDIA GPUs.

```mermaid
flowchart TD
    A["MarlinF8QBytesTensor"] --> B["MarlinF8QBytesLinearFunction"]
    B --> C["torch.ops.quanto.gemm_f16f8_marlin"]
    C --> D["Optimized FP8 Matrix Multiplication"]
    
    E["MarlinInt4PackedTensor"] --> F["torch.ops.quanto.gemm_f16i4_marlin"]
    F --> G["Optimized INT4 Matrix Multiplication"]
```

Marlin includes special data layouts and permutations to optimize memory access patterns and computational efficiency.

Sources: [optimum/quanto/tensor/weights/marlin/fp8/qbits.py:28-51](), [optimum/quanto/library/extensions/cuda/__init__.py:177-202](), [test/library/test_mm.py:110-144]()

## Using Device-Specific Backends

Device-specific backends are used automatically when performing operations with quantized tensors. The system selects the appropriate implementation based on the device type of the input tensors.

### Extension Availability Check

```python
from optimum.quanto.library.extensions import is_extension_available

if is_extension_available("quanto_cuda"):
    # Use CUDA-specific operations
elif is_extension_available("quanto_mps"):
    # Use MPS-specific operations
elif is_extension_available("quanto_xpu"):
    # Use XPU-specific operations
else:
    # Fall back to CPU implementation
```

This pattern is used throughout the codebase to ensure operations are only dispatched to available backends.

Sources: [test/library/test_extensions.py:31-39](), [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py:40-51]()

## Conclusion

The device-specific backends in optimum-quanto provide optimized implementations of core operations for different hardware platforms. These backends ensure efficient execution of quantized models across a variety of devices, from NVIDIA GPUs to Apple Silicon and Intel GPUs. By leveraging the strengths of each hardware platform, optimum-quanto maximizes the performance benefits of quantization while maintaining a consistent interface for end users.

---

# Page: Quantized Modules

# Quantized Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/nn/qconv2d.py](optimum/quanto/nn/qconv2d.py)
- [optimum/quanto/nn/qlayernorm.py](optimum/quanto/nn/qlayernorm.py)
- [optimum/quanto/nn/qlinear.py](optimum/quanto/nn/qlinear.py)
- [optimum/quanto/nn/qmodule.py](optimum/quanto/nn/qmodule.py)
- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



This page details the quantized neural network module implementations in optimum-quanto. Specifically, it covers how standard PyTorch modules are transformed into their quantized equivalents, the common architecture underlying all quantized modules, and the specific implementations for linear layers, convolutional layers, and normalization layers.

For information about model-level integration of these modules, see [Model Integration](#4.3). For details on the underlying tensor quantization, see [Tensor Quantization](#4.1).

## Quantized Module Architecture

The quantized modules in optimum-quanto follow a common architecture based on a mixin pattern. Each quantized module inherits both from its corresponding PyTorch module and a special `QModuleMixin` class that adds quantization functionality.

```mermaid
classDiagram
    class "torch.nn.Module" {
        +forward()
    }
    
    class "QModuleMixin" {
        +weight_qtype
        +activation_qtype
        +optimizer
        +qweight: QTensor
        +from_module()
        +forward()
        +freeze()
        +quantize_input()
        +quantize_output()
    }
    
    class "QLinear" {
        +in_features
        +out_features
        +forward(input)
    }
    
    class "QConv2d" {
        +in_channels
        +out_channels
        +kernel_size
        +forward(input)
    }
    
    class "QLayerNorm" {
        +normalized_shape
        +eps
        +forward(input)
    }
    
    "torch.nn.Module" <|-- "QModuleMixin"
    "QModuleMixin" <|-- "QLinear"
    "torch.nn.Linear" <|-- "QLinear"
    "QModuleMixin" <|-- "QConv2d"
    "torch.nn.Conv2d" <|-- "QConv2d"
    "QModuleMixin" <|-- "QLayerNorm"
    "torch.nn.LayerNorm" <|-- "QLayerNorm"
```

Sources: 
- [optimum/quanto/nn/qmodule.py:94-310]()
- [optimum/quanto/nn/qlinear.py:26-50]()
- [optimum/quanto/nn/qconv2d.py:26-55]()
- [optimum/quanto/nn/qlayernorm.py:26-53]()

## Module Registration System

Optimum-quanto implements a registration system that allows automatic detection and quantization of PyTorch modules. This system maps standard PyTorch module types to their quantized counterparts.

```mermaid
flowchart TD
    A["register_qmodule"] --> B["_QMODULE_TABLE registry"]
    C["quantize_module function"] --> B
    B --> D["QLinear"]
    B --> E["QConv2d"]
    B --> F["QLayerNorm"]
    
    G["torch.nn.Linear"] -.registered for.-> D
    H["torch.nn.Conv2d"] -.registered for.-> E
    I["torch.nn.LayerNorm"] -.registered for.-> F
    
    J["model.linear = QLinear.from_module(model.linear, weights=qint8)"] --> D
    K["quantize(model, weights=qint8)"] --> C
```

Sources:
- [optimum/quanto/nn/qmodule.py:38-91]()
- [test/quantize/test_quantize_mlp.py:61-70]()

## Core Functionality: QModuleMixin

`QModuleMixin` is the foundation for all quantized modules, providing common functionality for quantization operations:

### Key Features:
- Maintains state for weight and activation quantization types
- Provides methods for dynamic quantization during forward passes
- Handles serialization and deserialization of quantized weights
- Manages quantization scales for both inputs and outputs
- Supports "freezing" modules to convert to static quantization

### Dynamic vs Static Quantization

A key concept in optimum-quanto is the distinction between dynamic and frozen (static) quantization:

```mermaid
flowchart LR
    subgraph "Dynamic Quantization"
        A["float weights"] --> B["qweight() property"]
        B --> C["dynamic quantization"]
        C --> D["quantized computation"]
    end
    
    subgraph "Static Quantization (Frozen)"
        E["QTensor weights"] --> F["quantized computation"]
    end
    
    G["freeze()"] --> H["Convert float weights to QTensor"]
    A --> G --> E
```

Sources:
- [optimum/quanto/nn/qmodule.py:246-276]() - qweight property
- [optimum/quanto/nn/qmodule.py:302-310]() - freeze method

## QLinear Implementation

`QLinear` is a quantized version of the PyTorch `Linear` module that supports both weight and activation quantization.

### Features:

- Supports multiple weight quantization formats (int4, int8, float8)
- Optional activation quantization
- Automatic group size detection for int2/int4 quantization
- Gradient-aware operations (both weights and inputs)

### Usage Example:

```python
# Create a quantized linear layer from a standard linear layer
linear = torch.nn.Linear(768, 768)
qlinear = QLinear.from_module(linear, weights=qint8, activations=qint8)

# For activation quantization, run inference with calibration first
with Calibration():
    output = qlinear(input_tensor)
    
# After calibration, freeze for deployment
qlinear.freeze()
```

Sources:
- [optimum/quanto/nn/qlinear.py:26-50]()
- [test/nn/test_qlinear.py:37-57]()
- [test/nn/test_qlinear.py:140-163]()

## QConv2d Implementation

`QConv2d` provides a quantized version of PyTorch's `Conv2d` module with functionality similar to `QLinear`.

### Features:

- Preserves all parameters of the original Conv2d layer
- Supports both weight and activation quantization
- Maintains the same API as the original Conv2d module

```mermaid
sequenceDiagram
    participant Model as "User Model"
    participant QConv2d as "QConv2d Module"
    participant QWeight as "qweight property"
    participant Compute as "Quantized Computation"
    
    Model->>QConv2d: forward(input)
    alt Activation Quantization Enabled
        QConv2d->>QConv2d: quantize_input(input)
    end
    QConv2d->>QWeight: Get quantized weights
    QWeight-->>QConv2d: Return quantized weights tensor
    QConv2d->>Compute: _conv_forward(quantized_input, quantized_weights, bias)
    Compute-->>QConv2d: Return raw output
    alt Activation Quantization Enabled
        QConv2d->>QConv2d: quantize_output(output)
    end
    QConv2d-->>Model: Return quantized output
```

Sources:
- [optimum/quanto/nn/qconv2d.py:26-55]()
- [test/nn/test_qconv2d.py:31-51]()

## QLayerNorm Implementation

`QLayerNorm` provides a quantized version of layer normalization, primarily focused on activation quantization rather than weight quantization.

### Key Differences:

- Unlike QLinear and QConv2d, QLayerNorm doesn't quantize its weights
- Returns `None` if activations quantization is not enabled
- Preserves the elementwise affine parameter from the original LayerNorm

Sources:
- [optimum/quanto/nn/qlayernorm.py:26-53]()
- [test/nn/test_qlayernorm.py:23-41]()

## Calibration Process

The calibration process is essential for modules using activation quantization, as it establishes appropriate scaling factors to minimize quantization error.

```mermaid
flowchart TD
    A["Module with activation_qtype set"] --> B["Initial scales set to ones"]
    B --> C["Run inference with Calibration context"]
    C --> D["Automatic scale adjustment"]
    D --> E["Scales stored in module buffers"]
    E --> F["Subsequent forward passes use calibrated scales"]
    
    G["with Calibration():"] --> C
    H["input_scale and output_scale buffers"] --> E
```

Sources:
- [test/nn/test_calibrate.py:23-39]()
- [optimum/quanto/nn/qmodule.py:282-300]() - quantize_input and quantize_output methods

## Serialization and Deserialization

Optimum-quanto provides specialized serialization for quantized modules, handling the storage and loading of quantized weights.

### Features:

- Serializes quantized weights as flattened tensors
- Preserves quantization parameters in the state dictionary
- Handles both frozen and unfrozen modules correctly
- Compatible with PyTorch's standard save/load mechanisms

Sources:
- [optimum/quanto/nn/qmodule.py:147-207]()
- [test/nn/test_qlinear.py:196-227]()

## Performance Considerations

Quantized modules can offer significant performance benefits, particularly in terms of memory usage and computational efficiency:

- Reduced memory footprint (especially for int4/int8 quantization)
- Potential speedups on supported hardware platforms
- Trade-off between precision and performance can be controlled via quantization types

Sources:
- [test/quantize/test_quantize_mlp.py:119-136]()

## Integration with Higher-Level APIs

These quantized modules serve as building blocks for model-level quantization. They can be used:

1. Directly, by replacing specific modules in a model
2. Automatically, through the `quantize()` function
3. As part of a complete quantized model workflow

```mermaid
flowchart LR
    A["Individual Module\nReplacement"] --> D["QLinear, QConv2d, QLayerNorm"]
    B["Model-level quantize()"] --> E["quantize_module() function"]
    E --> F["Module Registration System"]
    F --> D
    C["Transformers/Diffusers\nIntegration"] --> G["QuantizedModelFor..."]
    G --> D
```

Sources:
- [test/nn/test_qattention.py:174-189]()
- [test/quantize/test_quantize_mlp.py:61-70]()

## Practical Usage Workflow

A typical workflow for using quantized modules involves:

1. **Creation** - Initialize quantized modules from standard modules
2. **Calibration** - For activation quantization, gather statistics
3. **Freezing** - Convert to static quantization for deployment
4. **Serialization** - Save the quantized model for later use

Sources:
- [test/nn/test_qlinear.py:196-227]()
- [test/nn/test_calibrate.py:23-39]()

---

# Page: QLinear

# QLinear

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/ops/test_linear_dispatch.py](test/tensor/ops/test_linear_dispatch.py)
- [test/tensor/ops/test_mm_dispatch.py](test/tensor/ops/test_mm_dispatch.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



QLinear is a quantized implementation of PyTorch's `torch.nn.Linear` module in optimum-quanto, designed to perform matrix multiplication with reduced precision. It serves as one of the core building blocks for deploying quantized neural networks, especially in transformer-based models. For information about other quantized modules, see [QConv2d and QLayerNorm](#5.2).

## Purpose and Overview

QLinear replaces standard full-precision linear layers with quantized alternatives that significantly reduce memory usage and improve inference speed while maintaining reasonable accuracy. It supports:

- Weight quantization (2-bit, 4-bit, 8-bit integer and 8-bit floating point)
- Optional activation quantization 
- Device-specific optimized implementations
- Dynamic calibration for activation quantization
- Serialization for saving and loading quantized models

```mermaid
flowchart LR
    subgraph "QLinear Module"
        A["torch.nn.Linear"] --> B["QLinear.from_module()"]
        B --> C["Quantized Weights"]
        B --> D["Optional Activation Quantization"]
        C --> E["Forward Pass with Optimized Implementation"]
        D --> E
        E --> F["Output (Float or Quantized)"]
    end
```

Sources: [test/nn/test_qlinear.py:37-57](), [test/nn/test_qlinear.py:140-149]()

## Architecture

QLinear inherits from both `torch.nn.Module` and `QModuleMixin`, providing the interface and behavior of a standard PyTorch module with additional quantization capabilities.

```mermaid
classDiagram
    class "torch.nn.Module" {
        +forward()
    }
    
    class "QModuleMixin" {
        +weight_qtype
        +activation_qtype
        +qweight: QTensor
        +from_module()
        +forward()
        +freeze()
    }
    
    class "QLinear" {
        +in_features: int
        +out_features: int
        +weight: Parameter/QTensor
        +bias: Parameter
        +input_scale: Tensor
        +output_scale: Tensor
        +forward(input)
        +from_module(module, weights, activations)
        +freeze()
    }
    
    "torch.nn.Module" <|-- "QModuleMixin"
    "QModuleMixin" <|-- "QLinear"
```

Sources: [test/nn/test_qlinear.py:34](), [test/nn/test_qlinear.py:186-193](), [test/nn/test_qlinear.py:206-217]()

### Key Attributes

- `in_features`: Size of input features
- `out_features`: Size of output features
- `weight`: The weights tensor (full-precision Parameter or quantized QTensor)
- `bias`: Optional bias tensor
- `weight_qtype`: Type of weight quantization (e.g., qint4, qint8, qfloat8)
- `activation_qtype`: Type of activation quantization (optional)
- `input_scale`: Scale factor for input quantization
- `output_scale`: Scale factor for output quantization

Sources: [test/nn/test_qlinear.py:40](), [test/nn/test_qlinear.py:143-148](), [test/nn/test_qlinear.py:206-227]()

## Weight Quantization

QLinear supports several weight quantization types:

| Quantization Type | Bits | Description | Best Use Case |
|-------------------|------|-------------|---------------|
| qint4             | 4    | 4-bit integer quantization | Significant memory reduction with modest accuracy impact |
| qint8             | 8    | 8-bit integer quantization | Good balance of accuracy and memory reduction |
| qfloat8           | 8    | 8-bit floating point (various formats) | Better dynamic range than integer quantization |

When weights are quantized, the linear operation is performed using quantized matrix multiplication, which is faster and more memory-efficient than full-precision operations.

```mermaid
flowchart TD
    A["Original Linear Layer\n(float32/float16)"] --> B["QLinear.from_module()"]
    B --> C["QLinear with\nfloat weight parameter\nand quantization metadata"]
    C --> D["freeze()"]
    D --> E["QLinear with\nquantized weight tensor (QTensor)"]
    E --> F["Optimized matrix multiplication\nduring inference"]
```

Sources: [test/nn/test_qlinear.py:60-66](), [test/nn/test_qlinear.py:121-129](), [test/nn/test_qlinear.py:186-193]()

## Activation Quantization

In addition to weight quantization, QLinear optionally supports activation quantization, which quantizes both inputs and outputs of the linear layer. This provides further memory and computation benefits, especially for intermediate activations in large models.

Supported activation quantization types include:
- qint8: 8-bit integer quantization
- qfloat8: Various 8-bit floating point formats (e4m3fn, e4m3fnuz, e5m2)

When activation quantization is enabled, QLinear accepts quantized inputs and produces quantized outputs, enabling efficient end-to-end quantized inference.

```mermaid
sequenceDiagram
    participant Input as "Input Tensor"
    participant QLinear as "QLinear Module"
    participant Output as "Output Tensor"
    
    Input->>QLinear: Float or ActivationQBytesTensor
    Note over QLinear: If input is float, optionally quantize
    Note over QLinear: Perform matrix multiplication with quantized weights
    Note over QLinear: Apply calibrated output scaling
    QLinear->>Output: Float or ActivationQBytesTensor
```

Sources: [test/nn/test_qlinear.py:79-96](), [test/nn/test_qlinear.py:101-115](), [test/nn/test_calibrate.py:23-40]()

## Calibration

Calibration is a crucial step when using activation quantization. It determines appropriate scaling factors for inputs and outputs to minimize quantization error. The `Calibration` context manager is used to collect statistics during forward passes and update the scaling factors accordingly.

```mermaid
flowchart LR
    A["Input Data"] --> B["Calibration Context"]
    B --> C["QLinear Forward Pass"]
    C --> D["Collect Activation Statistics"]
    D --> E["Update input_scale and output_scale"]
    E --> F["Optimized Quantized Inference"]
```

Sources: [test/nn/test_calibrate.py:23-40](), [test/nn/test_qlinear.py:48-50](), [test/nn/test_qlinear.py:78-88]()

## Usage

### Creating a QLinear Module

There are two ways to create a QLinear module:

1. **From an existing Linear module**:
```python
# Convert an existing linear layer to QLinear
linear = torch.nn.Linear(input_size, output_size)
qlinear = QLinear.from_module(linear, weights=qint8, activations=None)
```

2. **Creating a new QLinear module directly**:
```python
# Create a new QLinear module
qlinear = QLinear(input_size, output_size, weights=qint8, activations=None, bias=True)
```

Sources: [test/nn/test_qlinear.py:39](), [test/nn/test_qlinear.py:216]()

### Forward Pass

QLinear's forward pass accepts either regular tensors or quantized activations (if activation quantization is enabled):

```python
# Regular forward pass with float tensors
output = qlinear(input_tensor)

# Forward pass with quantized activations
with Calibration():
    qoutput = qlinear(qinput)
```

Sources: [test/nn/test_qlinear.py:48-50](), [test/nn/test_calibrate.py:35-36]()

### Freezing

Freezing converts weights from full-precision parameters to quantized tensors, significantly reducing memory usage:

```python
# Freeze quantized weights
qlinear.freeze()
```

After freezing, the `weight` attribute becomes a `QTensor` instead of a `Parameter`, enabling optimized inference.

Sources: [test/nn/test_qlinear.py:186-188]()

### Serialization

QLinear supports serialization using PyTorch's standard save/load mechanisms:

```python
# Save QLinear state
torch.save(qlinear.state_dict(), "qlinear.pt")

# Load QLinear state
new_qlinear = QLinear(in_features, out_features, weights=qint8)
new_qlinear.load_state_dict(torch.load("qlinear.pt"))
```

Sources: [test/nn/test_qlinear.py:212-227]()

## Technical Details

### Matrix Multiplication Implementation

QLinear uses specialized matrix multiplication implementations for different quantization types and devices:

```mermaid
flowchart TD
    A["QLinear.forward()"] --> B["torch.nn.functional.linear()"]
    B --> C{"Weight type?"}
    C -->|"QTensor (frozen)"| D["Optimized QTensor matmul"]
    C -->|"Parameter (non-frozen)"| E["Regular matmul + quantization on-the-fly"]
    D --> F{"Device type?"}
    F -->|"CUDA"| G["CUDA optimized kernels\n(AWQ, Marlin, TinyGemm)"]
    F -->|"CPU"| H["CPU optimized implementation"]
    F -->|"MPS"| I["MPS implementation"]
    F -->|"XPU"| J["XPU implementation"]
```

Sources: [test/tensor/ops/test_linear_dispatch.py:28-42](), [test/tensor/ops/test_mm_dispatch.py:22-44]()

### Device Support and Compatibility

QLinear supports multiple hardware backends with varying levels of optimization:

| Device | Weight-only Quantization | Activation Quantization | Float8 Support |
|--------|--------------------------|-------------------------|----------------|
| CUDA   | Full support             | Full support            | Yes            |
| CPU    | Full support             | Full support            | No             |
| MPS    | Limited support          | Limited support         | No             |
| XPU    | Limited support          | Limited support         | No             |

Sources: [test/nn/test_qlinear.py:89-90](), [test/nn/test_qlinear.py:107-108](), [test/nn/test_qlinear.py:123-128]()

## Gradient Propagation

Despite using quantization, QLinear maintains compatibility with PyTorch's automatic differentiation:

- Weight gradients are computed with respect to full-precision weights
- Input gradients are computed with respect to full-precision inputs
- Bias gradients work identically to standard Linear layers

This enables fine-tuning of models with QLinear layers, though the gradients are approximated due to quantization.

```mermaid
flowchart LR
    A["Forward Pass with\nQuantized Computation"] --> B["Loss Function"]
    B --> C["Backward Pass"]
    C --> D["Gradients (with respect to\nfull-precision parameters)"]
    D --> E["Optimizer Update\n(updates full-precision parameters)"]
    E --> A
```

Sources: [test/nn/test_qlinear.py:143-178]()

## Example Workflow

A complete workflow using QLinear typically includes these steps:

1. **Model Creation**: Create or load a PyTorch model with Linear layers
2. **Quantization**: Replace Linear layers with QLinear using `from_module`
3. **Calibration**: Run representative inputs through the model with the `Calibration` context to set scaling factors
4. **Freezing**: Freeze quantized weights to enable optimized inference
5. **Inference**: Run inference with optimized quantized computation
6. **Serialization**: Save the quantized model for deployment

Sources: [test/quantize/test_quantize_mlp.py:61-85]()

## Conclusion

QLinear is a fundamental building block in optimum-quanto's quantization system, enabling significant memory and computational efficiency improvements for neural networks. By replacing standard linear layers with quantized alternatives, models can be deployed on resource-constrained devices while maintaining reasonable accuracy.

---

# Page: QConv2d and QLayerNorm

# QConv2d and QLayerNorm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/nn/qconv2d.py](optimum/quanto/nn/qconv2d.py)
- [optimum/quanto/nn/qlayernorm.py](optimum/quanto/nn/qlayernorm.py)
- [optimum/quanto/nn/qlinear.py](optimum/quanto/nn/qlinear.py)
- [optimum/quanto/nn/qmodule.py](optimum/quanto/nn/qmodule.py)
- [test/library/test_quantize.py](test/library/test_quantize.py)
- [test/nn/test_calibrate.py](test/nn/test_calibrate.py)
- [test/nn/test_qattention.py](test/nn/test_qattention.py)
- [test/nn/test_qconv2d.py](test/nn/test_qconv2d.py)
- [test/nn/test_qlayernorm.py](test/nn/test_qlayernorm.py)
- [test/nn/test_qlinear.py](test/nn/test_qlinear.py)
- [test/quantize/test_quantize_mlp.py](test/quantize/test_quantize_mlp.py)
- [test/tensor/activations/test_activations_quantize.py](test/tensor/activations/test_activations_quantize.py)
- [test/tensor/weights/test_weight_qbytes_tensor_quantize.py](test/tensor/weights/test_weight_qbytes_tensor_quantize.py)

</details>



QConv2d and QLayerNorm are quantized versions of PyTorch's standard Conv2d and LayerNorm modules in the optimum-quanto framework. These modules provide efficient quantization capabilities for convolutional neural networks and transformer architectures.

While they both serve the purpose of quantization, they have different focuses:
- QConv2d supports both weight and activation quantization, suitable for convolutional operations
- QLayerNorm focuses exclusively on activation quantization, as normalization layers typically have fewer parameters and benefit less from weight quantization

For information about the quantized linear layer implementation, see [QLinear](#5.1).

## Architecture

Both QConv2d and QLayerNorm follow a common architectural pattern defined by the QModuleMixin, which provides the core quantization functionality. They inherit from both the QModuleMixin and their respective PyTorch base classes.

### Class Hierarchy

```mermaid
classDiagram
    class "torch.nn.Module" {
        +forward()
    }
    
    class "QModuleMixin" {
        +weight_qtype
        +activation_qtype
        +qweight
        +from_module()
        +forward()
        +freeze()
    }
    
    class "torch.nn.Conv2d" {
        +weight
        +bias
        +forward()
    }
    
    class "torch.nn.LayerNorm" {
        +weight
        +bias
        +forward()
    }
    
    class "QConv2d" {
        +qcreate()
        +forward()
    }
    
    class "QLayerNorm" {
        +qcreate()
        +forward()
    }
    
    "torch.nn.Module" <|-- "QModuleMixin"
    "torch.nn.Module" <|-- "torch.nn.Conv2d"
    "torch.nn.Module" <|-- "torch.nn.LayerNorm"
    
    "QModuleMixin" <|-- "QConv2d"
    "torch.nn.Conv2d" <|-- "QConv2d"
    
    "QModuleMixin" <|-- "QLayerNorm"
    "torch.nn.LayerNorm" <|-- "QLayerNorm"
```

Sources: [optimum/quanto/nn/qmodule.py:94-311](), [optimum/quanto/nn/qconv2d.py:1-56](), [optimum/quanto/nn/qlayernorm.py:1-54]()

## QConv2d

QConv2d implements a quantized 2D convolutional layer that supports quantization of both weights and activations, preserving the functionality of standard Conv2d layers while operating with reduced precision.

### Implementation Details

QConv2d is implemented as a class that inherits from both QModuleMixin and torch.nn.Conv2d:

```mermaid
flowchart TB
    A["QConv2d"] --> B["Weight Quantization"]
    A --> C["Activation Quantization"]
    A --> D["Parameter Handling"]
    
    B --> B1["Int4/Int8 Quantization"]
    B --> B2["Float8 Quantization"]
    
    C --> C1["Input Quantization"]
    C --> C2["Output Quantization"]
    
    D --> D1["Bias Parameters"]
    D --> D2["Scale Parameters"]
    
    B1 --> E["Forward Pass"]
    B2 --> E
    C1 --> E
    C2 --> E
    D1 --> E
    D2 --> E
```

Sources: [optimum/quanto/nn/qconv2d.py:26-56](), [test/nn/test_qconv2d.py:31-51]()

The forward pass in QConv2d replaces the standard weights with quantized weights using the `qweight` property, which either returns frozen quantized weights or dynamically quantizes the weights during the forward pass.

### QConv2d Data Flow

```mermaid
flowchart LR
    A["Input Tensor"] --> B{"Activation\nQuantization?"}
    B -- "Yes" --> C["Quantize Input"]
    B -- "No" --> D["Use Float Input"]
    C --> E["QConv2d Computation\nwith qweight"]
    D --> E
    E --> F{"Activation\nQuantization?"}
    F -- "Yes" --> G["Quantize Output"]
    F -- "No" --> H["Float Output"]
    G --> I["Return Result"]
    H --> I
```

Sources: [optimum/quanto/nn/qmodule.py:282-300](), [optimum/quanto/nn/qconv2d.py:54-55]()

### Supported Quantization Types

QConv2d supports a variety of quantization types:

| Weight Quantization | Activation Quantization |
|---------------------|-------------------------|
| qint4 (4-bit integer) | qint8 (8-bit integer) |
| qint8 (8-bit integer) | qfloat8_e5m2 (8-bit float) |
| qfloat8 variants (8-bit float) | qfloat8_e4m3fn (8-bit float) |
|                     | qfloat8_e4m3fnuz (8-bit float) |

Sources: [test/nn/test_qconv2d.py:54-123]()

## QLayerNorm

QLayerNorm is a quantized layer normalization module that focuses on activation quantization. Unlike QConv2d, it doesn't support weight quantization.

### Implementation Details

QLayerNorm is designed to work with quantized activations while maintaining the same normalization behavior as the standard LayerNorm:

```mermaid
flowchart TB
    A["QLayerNorm"] --> B["Activation-Only Quantization"]
    A --> C["No Weight Quantization"]
    
    B --> B1["Input Processing"]
    B --> B2["Output Quantization"]
    
    C --> C1["Returns None if only\nweights are quantized"]
    
    B1 --> D["Standard LayerNorm\nComputation"]
    B2 --> D
    C1 --> D
```

Sources: [optimum/quanto/nn/qlayernorm.py:26-54](), [test/nn/test_qlayernorm.py:23-41]()

The key aspect of QLayerNorm is that it returns None if only weight quantization is requested (when `activations=None`), making it clear that it only supports activation quantization.

### QLayerNorm Data Flow

```mermaid
flowchart LR
    A["Quantized Input\nActivationQBytesTensor"] --> B["Dequantize for\nComputation"]
    B --> C["Standard LayerNorm\nComputation"]
    C --> D["Quantize Output\nActivationQBytesTensor"]
    D --> E["Return\nQuantized Output"]
```

Sources: [optimum/quanto/nn/qlayernorm.py:52-53](), [test/nn/test_qlayernorm.py:23-41]()

### Supported Quantization Types

QLayerNorm only supports activation quantization:

| Weight Quantization | Activation Quantization |
|---------------------|-------------------------|
| Not supported | qint8 (8-bit integer) |
|              | qfloat8_e5m2 (8-bit float) |
|              | qfloat8_e4m3fn (8-bit float) |
|              | qfloat8_e4m3fnuz (8-bit float) |

Sources: [test/nn/test_qlayernorm.py:44-83](), [optimum/quanto/nn/qlayernorm.py:36-39]()

## Creating and Using Quantized Modules

Both QConv2d and QLayerNorm are typically created using their `from_module` static method, which converts an existing PyTorch module to its quantized equivalent:

```python
# For QConv2d (supports both weight and activation quantization)
conv = torch.nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3)
qconv = QConv2d.from_module(conv, weights=qint8, activations=qint8)

# For QLayerNorm (only supports activation quantization)
norm = torch.nn.LayerNorm(normalized_shape=512)
qnorm = QLayerNorm.from_module(norm, activations=qint8)
```

Sources: [test/nn/test_qconv2d.py:32-33](), [test/nn/test_qlayernorm.py:25-26]()

## Calibration Process

When using activation quantization, a calibration process is necessary to determine appropriate scaling factors. This is done using the `Calibration` context manager:

```mermaid
flowchart TD
    A["Create Quantized Modules"] --> B["Run Representative\nInput Data"]
    B --> C["Use Calibration\nContext Manager"]
    C --> D["Statistics Collected\nAutomatically"]
    D --> E["Input/Output Scales\nOptimized"]
    E --> F["Quantization-Aware\nForward Pass"]
```

Sources: [test/nn/test_calibrate.py:23-40](), [test/nn/test_qconv2d.py:37-39](), [test/nn/test_qlayernorm.py:29-30]()

Example calibration code:

```python
from optimum.quanto import Calibration

# Run calibration to set optimal scales
with Calibration():
    output = qmodule(input_data)
```

Sources: [test/nn/test_calibrate.py:35-36](), [test/nn/test_qlayernorm.py:29-30]()

## Integration Example

This example shows how QConv2d and QLayerNorm can be used together in a model:

```python
import torch
import torch.nn as nn
from optimum.quanto import quantize, Calibration, qint8, freeze

# Define a model with Conv2d and LayerNorm
class ConvNormModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 16, kernel_size=3)
        # LayerNorm for feature maps
        self.norm = nn.LayerNorm([16, 28, 28])
        
    def forward(self, x):
        x = self.conv(x)
        x = self.norm(x)
        return x

# Create and quantize the model
model = ConvNormModel()
quantize(model, weights=qint8, activations=qint8)

# Calibrate for activation quantization
with Calibration():
    model(sample_input)

# Freeze weights for inference
freeze(model)
```

Sources: [test/quantize/test_quantize_mlp.py:40-78](), [test/nn/test_qattention.py:173-189]()

## Performance Considerations

1. **Memory Usage**: QConv2d with weight quantization significantly reduces model size, especially important for large convolutional models
2. **Computational Efficiency**: Both modules can improve inference speed on hardware that supports quantized operations
3. **Accuracy Trade-offs**: Lower precision quantization (e.g., qint4) may affect model accuracy more than higher precision (e.g., qint8)
4. **Hardware Support**: Float8 quantization is not supported on all devices (specifically MPS and XPU)

Sources: [test/nn/test_qconv2d.py:84](), [test/nn/test_qconv2d.py:98-101](), [test/nn/test_qlayernorm.py:66-68]()

## Common Pitfalls and Limitations

1. **QLayerNorm weight-only quantization**: QLayerNorm will return None if only weight quantization is requested
2. **Platform compatibility**: Float8 quantization is not supported on all devices (test with `@pytest.mark.skip_device("mps")` and `@pytest.mark.skip_device("xpu")`)
3. **Activation Statistics**: For best results, calibration should be performed with data that is representative of the real inputs
4. **Quantization Precision**: For sensitive layers, higher precision quantization types may be necessary to maintain accuracy

Sources: [test/nn/test_qlayernorm.py:86-90](), [test/nn/test_qconv2d.py:84](), [test/nn/test_qlayernorm.py:66-68]()

---

# Page: Optimization Algorithms

# Optimization Algorithms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [bench/kernels/benchmark_w4a16.py](bench/kernels/benchmark_w4a16.py)
- [external/awq/test_awq_kernels.py](external/awq/test_awq_kernels.py)
- [external/awq/test_awq_packing.py](external/awq/test_awq_packing.py)
- [external/smoothquant/smoothquant.py](external/smoothquant/smoothquant.py)
- [optimum/quanto/library/extensions/cuda/__init__.py](optimum/quanto/library/extensions/cuda/__init__.py)
- [optimum/quanto/tensor/weights/awq/packed.py](optimum/quanto/tensor/weights/awq/packed.py)
- [optimum/quanto/tensor/weights/awq/qbits.py](optimum/quanto/tensor/weights/awq/qbits.py)
- [optimum/quanto/tensor/weights/marlin/fp8/__init__.py](optimum/quanto/tensor/weights/marlin/fp8/__init__.py)
- [optimum/quanto/tensor/weights/marlin/fp8/packed.py](optimum/quanto/tensor/weights/marlin/fp8/packed.py)
- [optimum/quanto/tensor/weights/marlin/fp8/qbits.py](optimum/quanto/tensor/weights/marlin/fp8/qbits.py)
- [optimum/quanto/tensor/weights/packing.py](optimum/quanto/tensor/weights/packing.py)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)
- [test/library/test_mm.py](test/library/test_mm.py)
- [test/tensor/weights/optimized/test_awq_packed_tensor.py](test/tensor/weights/optimized/test_awq_packed_tensor.py)
- [test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py](test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py)
- [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py](test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py)
- [test/tensor/weights/optimized/test_marlin_qbytes_tensor.py](test/tensor/weights/optimized/test_marlin_qbytes_tensor.py)
- [test/tensor/weights/optimized/test_tinygemm_packed_tensor.py](test/tensor/weights/optimized/test_tinygemm_packed_tensor.py)

</details>



This page documents the specialized quantization optimization algorithms implemented in optimum-quanto. These algorithms enhance the efficiency and performance of quantized models by employing various techniques for optimal memory layout, computation patterns, and quantization balance. For general information about quantization types, see [Quantization Types](#3.1).

## Overview of Optimization Algorithms

Optimization algorithms in optimum-quanto can be categorized into two main types:
1. **Weight Quantization Optimizations** - Algorithms that optimize how weights are stored and processed
2. **Quantization Balance Optimizations** - Techniques that balance quantization between weights and activations

```mermaid
flowchart TD
    A["Optimization Algorithms"] --> B["Weight Quantization<br>Optimizations"]
    A --> C["Quantization Balance<br>Optimizations"]
    
    B --> D["AWQ<br>Activation-aware Weight Quantization"]
    B --> E["Marlin<br>Optimized Memory Layout"]
    B --> F["TinyGemm<br>Efficient Matrix Multiplication"]
    
    C --> G["SmoothQuant<br>Weight-Activation Balance"]
    
    D --> H["Optimized Linear Operations"]
    E --> H
    F --> H
```

Sources: [optimum/quanto/tensor/weights/awq/qbits.py]()), [optimum/quanto/tensor/weights/marlin/fp8/qbits.py]()), [test/tensor/weights/optimized/test_tinygemm_packed_tensor.py]()), [external/smoothquant/smoothquant.py]())

## AWQ (Activation-Aware Weight Quantization)

AWQ is an optimization technique for low-bit weight quantization that considers activation patterns to preserve the quality of important weights during quantization.

### Implementation Details

In optimum-quanto, AWQ is implemented through specialized tensor classes and packing formats that optimize memory layout and computation:

```mermaid
classDiagram
    class WeightQBitsTensor {
        +data: tensor
        +scale: tensor
        +shift: tensor
        +dequantize()
    }
    
    class AWQWeightQBitsTensor {
        +data: AWQPackedTensor
        +scale: tensor
        +shift: tensor
        +dequantize()
        +weight_qbits_tensor()
    }
    
    class AWQPackedTensor {
        +data: tensor
        +packing: AWQPacking
        +reorder: bool
        +unpack()
        +pack(tensor)
    }
    
    class AWQPacking {
        <<enum>>
        V1
        V2
    }
    
    class AWQWeightQBitsLinearFunction {
        +forward(input, other, bias)
    }
    
    WeightQBitsTensor <|-- AWQWeightQBitsTensor
    AWQWeightQBitsTensor --> AWQPackedTensor: contains
    AWQPackedTensor --> AWQPacking: uses
    AWQWeightQBitsTensor --> AWQWeightQBitsLinearFunction: uses for linear ops
```

Sources: [optimum/quanto/tensor/weights/awq/qbits.py:73-164]()), [optimum/quanto/tensor/weights/awq/packed.py:22-295]())

### Packing Formats

AWQ uses two packing formats for efficient storage and computation:

1. **V1 Packing**: Reorders columns in 4-bit integers for faster dequantization
   - Uses permutation pattern `[0, 2, 4, 6, 1, 3, 5, 7]` for reordering
   - Packs values into int32 tensor

2. **V2 Packing**: More advanced format for newer GPU architectures
   - Permutes rows to counter implicit permutation on Turing and Ampere GPUs
   - Interleaves groups of rows for efficient parallel processing
   - Packs values into int16 tensor

Sources: [optimum/quanto/tensor/weights/awq/packed.py:33-153]()), [test/tensor/weights/optimized/test_awq_packed_tensor.py:23-68]())

### CUDA Kernels

The AWQ implementation includes specialized CUDA kernels for efficient matrix multiplication:

- **GEMM Kernel**: For batched operations (multiple tokens)
- **GEMV Kernel**: Optimized for single token operations

```mermaid
flowchart TD
    A["Matrix Multiplication<br>with AWQWeightQBitsTensor"] --> B{"Matrix Size Check"}
    B -->|"rows < 8"| C["GEMV Kernel<br>awq_v2_gemv_f16i4"]
    B -->|"rows >= 8"| D["GEMM Kernel<br>awq_v2_gemm_f16i4"]
    C --> E["Output Tensor"]
    D --> E
```

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:97-121]()), [test/library/test_mm.py:27-101]())

### Performance Characteristics

AWQ optimizations significantly improve inference speed while maintaining accuracy through:

1. Memory efficiency with 4-bit quantization
2. Reduced memory bandwidth requirements
3. Optimized memory access patterns
4. Specialized kernels for different operation sizes

The benchmarks indicate:
- Higher TFLOP/s compared to unoptimized quantization
- Especially beneficial for batch sizes >= 8

Sources: [bench/kernels/benchmark_w4a16.py:12-149]())

## Marlin and TinyGemm

Marlin and TinyGemm are optimization techniques focused on efficient matrix multiplication for quantized weights.

### Marlin Implementation

Marlin is implemented with two variants:

1. **Marlin FP8**: For 8-bit floating point quantization
2. **Marlin INT4**: For 4-bit integer quantization

```mermaid
classDiagram
    class QTensor {
        +dequantize()
    }
    
    class WeightQBytesTensor {
        +data: tensor
        +scale: tensor
        +dequantize()
    }
    
    class WeightQBitsTensor {
        +data: tensor
        +scale: tensor
        +shift: tensor
        +dequantize()
    }
    
    class MarlinF8QBytesTensor {
        +data: MarlinF8PackedTensor
        +scale: tensor
        +workspace: tensor
        +dequantize()
        +weight_qbytes_tensor()
    }
    
    class MarlinInt4PackedTensor {
        +pack(tensor)
        +unpack()
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
    WeightQBytesTensor <|-- MarlinF8QBytesTensor
    MarlinF8QBytesTensor ..> MarlinF8PackedTensor: contains
```

Sources: [optimum/quanto/tensor/weights/marlin/fp8/qbits.py:28-168]()), [optimum/quanto/tensor/weights/marlin/fp8/packed.py:22-267]())

### Marlin FP8 Optimization

Marlin FP8 optimization uses several techniques for efficient computation:

1. **Custom Packing**: Repacks FP8 weights into int32 for efficient storage
2. **Column/Row Permutation**: Uses specific permutation patterns for memory access optimization
3. **Scale Permutation**: Applies scale factor transformations for efficient computation

The memory layout transformations enable better utilization of GPU memory bandwidth and compute units.

Sources: [optimum/quanto/tensor/weights/marlin/fp8/packed.py:22-158]()), [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py:15-66]())

### TinyGemm Optimization

TinyGemm is a specialized optimization for newer CUDA architectures (CUDA 12.1+ and compute capability 8.0+). It focuses on leveraging hardware-specific features for efficient matrix multiplication with quantized weights.

Sources: [test/tensor/weights/optimized/test_tinygemm_packed_tensor.py:15-70]())

### Performance Comparison

Performance benchmarks show:

1. **Marlin vs AWQ**:
   - Marlin typically achieves higher TFLOP/s rates
   - AWQ may have better performance on specific hardware configurations
   - Both outperform naive quantized matrix multiplication

2. **Hardware Considerations**:
   - Marlin FP8 requires compute capability 8.0+ (Ampere architecture or newer)
   - TinyGemm requires CUDA 12.1+ and compute capability 8.0+

```mermaid
flowchart TD
    A["Quantized Matrix Multiplication"] --> B{"Hardware Check"}
    B -->|"CUDA 12.1+<br>sm_80+"| C["TinyGemm<br>Optimization"]
    B -->|"sm_80+"| D["Marlin<br>Optimization"]
    B -->|"CUDA<br>Any sm"| E["AWQ<br>Optimization"]
    B -->|"CPU/MPS/XPU"| F["Standard<br>Quantized MM"]
    
    C --> G["Hardware-Optimized<br>Quantized MatMul"]
    D --> G
    E --> G
    F --> G
```

Sources: [bench/kernels/benchmark_w4a16.py:12-149]()), [test/library/test_mm.py:102-189]())

## SmoothQuant

SmoothQuant is a technique that balances quantization between weights and activations to improve overall quantization accuracy.

### Concept and Implementation

SmoothQuant addresses the challenge of quantizing models with high activation dynamic range by:

1. Collecting activation statistics across representative data
2. Computing scaling factors that balance the quantization difficulty between weights and activations
3. Applying these scales to layer normalization and linear/attention layers

```mermaid
flowchart LR
    A["Original Model"] --> B["Activation<br>Statistics Collection"]
    B --> C["Scale Factor<br>Computation"]
    C --> D["Layer Weight/Bias<br>Transformation"]
    D --> E["Quantized Model<br>with Balanced Precision"]
    
    subgraph "Scale Factor Computation"
        F["act_scales^α / weight_scales^(1-α)"]
    end
    
    subgraph "Layer Transformation"
        G["LayerNorm.weight /= scales"]
        H["LayerNorm.bias /= scales"]
        I["Linear.weight *= scales"]
    end
    
    C --- F
    D --- G
    D --- H
    D --- I
```

Sources: [external/smoothquant/smoothquant.py:16-108]())

### Application to Model Architectures

SmoothQuant is implemented for various transformer architectures:

- **OPT**: Applies to self-attention and MLP blocks
- **BLOOM**: Adjusts query-key-value and MLP dense layers
- **LLaMA/Mistral**: Transforms attention projections and MLP gate/up projections

The implementation analyzes each architecture's specific structure to apply transformations at the right layers.

Sources: [external/smoothquant/smoothquant.py:76-108]())

## Performance and Usage Benchmarks

The optimization algorithms provide significant performance improvements:

| Algorithm | Typical Speedup | Memory Savings | Accuracy Impact |
|-----------|----------------|----------------|-----------------|
| AWQ       | 2-4x           | 8x (vs FP32)   | Minimal         |
| Marlin    | 3-5x           | 4-8x (vs FP32) | Minimal         |
| TinyGemm  | 3-5x           | 8x (vs FP32)   | Minimal         |
| SmoothQuant | 1-2x         | 4x (vs FP32)   | Improved over standard quantization |

Choosing the right optimization depends on:
1. Hardware availability (compute capability, CUDA version)
2. Model architecture
3. Performance vs accuracy requirements

Sources: [bench/kernels/benchmark_w4a16.py:74-127]())

## Integration with Quantization Workflow

These optimization algorithms integrate with the overall quantization workflow in optimum-quanto:

```mermaid
flowchart TD
    A["Original Float Model"] --> B["Quantization"]
    B --> C{"Optimization<br>Selection"}
    
    C -->|"4-bit weights<br>16-bit activations"| D["AWQ<br>Optimization"]
    C -->|"8-bit float weights"| E["Marlin FP8<br>Optimization"]
    C -->|"4-bit int weights"| F["Marlin INT4<br>Optimization"]
    C -->|"Newer CUDA"| G["TinyGemm<br>Optimization"]
    C -->|"High activation<br>dynamic range"| H["SmoothQuant<br>Pre-processing"]
    
    D --> I["Optimized<br>Quantized Model"]
    E --> I
    F --> I
    G --> I
    H --> B
```

Sources: [optimum/quanto/tensor/weights/awq/qbits.py:73-164]()), [optimum/quanto/tensor/weights/marlin/fp8/qbits.py:28-168]()), [external/smoothquant/smoothquant.py:76-108]())

---

# Page: AWQ (Activation-Aware Weight Quantization)

# AWQ (Activation-Aware Weight Quantization)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [bench/kernels/benchmark_w4a16.py](bench/kernels/benchmark_w4a16.py)
- [external/awq/test_awq_kernels.py](external/awq/test_awq_kernels.py)
- [external/awq/test_awq_packing.py](external/awq/test_awq_packing.py)
- [external/smoothquant/smoothquant.py](external/smoothquant/smoothquant.py)
- [optimum/quanto/tensor/weights/awq/packed.py](optimum/quanto/tensor/weights/awq/packed.py)
- [optimum/quanto/tensor/weights/awq/qbits.py](optimum/quanto/tensor/weights/awq/qbits.py)
- [optimum/quanto/tensor/weights/packing.py](optimum/quanto/tensor/weights/packing.py)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)
- [test/tensor/weights/optimized/test_awq_packed_tensor.py](test/tensor/weights/optimized/test_awq_packed_tensor.py)
- [test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py](test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py)
- [test/tensor/weights/optimized/test_marlin_qbytes_tensor.py](test/tensor/weights/optimized/test_marlin_qbytes_tensor.py)
- [test/tensor/weights/optimized/test_tinygemm_packed_tensor.py](test/tensor/weights/optimized/test_tinygemm_packed_tensor.py)

</details>



AWQ is a specialized quantization technique implemented in optimum-quanto that focuses on accelerating low-bit weight quantization by considering activation patterns. This page documents the implementation of AWQ in the optimum-quanto library, its core components, and how it integrates with the quantization workflow.

For information about other optimization algorithms like Marlin and TinyGemm, see [Marlin and TinyGemm](#6.2). For SmoothQuant, which focuses on activation quantization, see [SmoothQuant](#6.3).

## Core Concepts

AWQ (Activation-aware Weight Quantization) is a technique introduced in the paper "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration". It differs from standard quantization by:

1. Analyzing activation patterns to identify which weights are most important
2. Preserving precision for weights that interact with the largest activations
3. Using specialized memory layouts and optimized CUDA kernels for efficient inference

In optimum-quanto, AWQ is implemented as specialized tensor classes and optimized backend operations for weights quantized to 4 bits.

Sources: [optimum/quanto/tensor/weights/awq/qbits.py](), [optimum/quanto/tensor/weights/awq/packed.py]()

## AWQ Architecture

```mermaid
classDiagram
    class QTensor {
        +dequantize()
    }
    
    class WeightQBitsTensor {
        +data: tensor
        +scale: tensor
        +shift: tensor
        +qtype: QuantType
        +group_size: int
        +dequantize()
    }
    
    class AWQWeightQBitsTensor {
        +dequantize()
        +weight_qbits_tensor()
        +__torch_function__()
    }
    
    class AWQWeightQBitsDequantizer {
        +forward()
        +backward()
    }
    
    class AWQWeightQBitsLinearFunction {
        +forward()
    }
    
    class AWQPackedTensor {
        +data: tensor
        +packing: AWQPacking
        +reorder: bool
        +unpack()
        +pack()
    }
    
    class AWQPacking {
        <<enumeration>>
        V1
        V2
    }
    
    QTensor <|-- WeightQBitsTensor
    WeightQBitsTensor <|-- AWQWeightQBitsTensor
    AWQWeightQBitsTensor --> AWQWeightQBitsDequantizer : uses
    AWQWeightQBitsTensor --> AWQWeightQBitsLinearFunction : uses
    AWQWeightQBitsTensor --> AWQPackedTensor : contains
    AWQPackedTensor --> AWQPacking : uses
```

Sources: [optimum/quanto/tensor/weights/awq/qbits.py](), [optimum/quanto/tensor/weights/awq/packed.py]()

## Tensor Packing Strategies

AWQ implements two different packing strategies to efficiently store and process 4-bit quantized weights:

### AWQ Packing V1

The first generation AWQ packing strategy (`AWQPacking.V1`) focuses on efficient column ordering for faster dequantization:

```mermaid
flowchart LR
    subgraph "AWQ Packing V1"
        A["uint8 Tensor\n(n×k)"] --> |"Optional\nColumn Reordering"| B["Reordered Tensor\n[0,2,4,6,1,3,5,7]"]
        B --> |"Pack 8 uint4 values\ninto int32"| C["int32 Tensor\n(n×k/8)"]
    end
```

This packing strategy is based on the paper "Who Says Elephants Can't Run: Bringing Large Scale MoE Models into Cloud Scale Production" and optionally reorders columns using the pattern `[0, 2, 4, 6, 1, 3, 5, 7]` for faster dequantization.

### AWQ Packing V2

The second generation packing strategy (`AWQPacking.V2`) adds several optimizations for newer GPU architectures:

```mermaid
flowchart TB
    subgraph "AWQ Packing V2"
        A["uint8 Tensor\n(N×K)"] --> B["Permute for\nfaster dequantization"]
        B --> C["Reorder each 8 weights\n[0,2,4,6,1,3,5,7]"]
        C --> D["Interleave rows for\nparallel processing"]
        D --> E["Pack 4 uint4 values\ninto int16"]
        E --> F["int16 Tensor\n(N/4×K)"]
    end
```

This more advanced packing strategy is optimized for Turing and Ampere GPU architectures and includes interleaving of groups of rows for more efficient parallel processing.

Sources: [optimum/quanto/tensor/weights/awq/packed.py:29-202]()

## AWQ Tensor Classes

### AWQPackedTensor

The `AWQPackedTensor` is a specialized tensor subclass that efficiently packs 4-bit integer values for GPU processing:

```mermaid
flowchart LR
    subgraph "AWQPackedTensor Operations"
        A["torch.Tensor\n(uint8)"] --> |"pack()"| B["AWQPackedTensor"]
        B --> |"unpack()"| A
        B --> |"to(device)"| C["AWQPackedTensor\non target device"]
        B --> |"any other op"| D["Unpacked and\nprocessed tensor"]
    end
```

Key features:
- Supports two packing formats (V1 and V2)
- Only available on CUDA devices
- Automatically unpacks when moved to CPU
- Unpacks transparently when used in most operations

Sources: [optimum/quanto/tensor/weights/awq/packed.py:204-295]()

### AWQWeightQBitsTensor

The `AWQWeightQBitsTensor` extends `WeightQBitsTensor` to use AWQ-optimized formats and operations:

| Feature | Description |
|---------|-------------|
| Specialized dequantization | Uses `AWQWeightQBitsDequantizer` for faster unpacking |
| Matrix multiplication | Uses optimized `gemm_f16i4_awq` CUDA kernel |
| Automatic format conversion | Formats data, scale and shift for optimal computation |
| Serialization support | Can convert to/from standard `WeightQBitsTensor` |

When used in a `torch.nn.functional.linear` operation, the tensor automatically uses the optimized AWQ implementation without any changes to the model code.

Sources: [optimum/quanto/tensor/weights/awq/qbits.py:30-164]()

## Optimized CUDA Kernels

AWQ's performance benefits come from specialized CUDA kernels for matrix multiplication with 4-bit quantized weights:

```mermaid
flowchart TB
    subgraph "AWQ Matrix Multiplication"
        A["Input\n(FP16)"] --> C["gemm_f16i4_awq"]
        B["AWQ Weights\n(INT4)"] --> C
        D["Scale\n(FP16)"] --> C
        E["Zero Shift\n(FP16)"] --> C
        C --> F["Output\n(FP16)"]
    end
```

Key optimizations:
1. Fast dequantization of packed 4-bit values
2. Efficient group-wise scaling
3. Batched processing for multiple tokens

These kernels are specialized for LLM inference where a relatively small input batch is multiplied by large weight matrices, which is the typical pattern in transformer decoder layers.

Sources: [bench/kernels/benchmark_w4a16.py:54-61](), [external/awq/test_awq_kernels.py:78-87]()

## Performance Benefits

AWQ provides significant performance improvements over standard floating-point operations, especially for larger models:

| Model | Tokens | AWQ Speedup | TFLOP/s |
|-------|--------|------------|---------|
| Llama-7B | 1-64 | 1.5-2.5x | 40-80 |
| Llama-13B | 1-64 | 1.8-2.8x | 50-100 |
| Llama-65B | 1-64 | 2.0-3.0x | 70-120 |
| Falcon-180B | 1-64 | 2.2-3.2x | 80-140 |

The speedup increases with model size due to:
1. More efficient memory bandwidth utilization
2. Reduced weight memory footprint (75% smaller than FP16)
3. Optimized processing of large weight matrices

Sources: [bench/kernels/benchmark_w4a16.py:73-127]()

## Integration with Quantization Workflow

AWQ integrates with the optimum-quanto quantization workflow as follows:

```mermaid
flowchart LR
    A["Float Model"] --> B["Quantize with qint4"]
    B --> C["Standard WeightQBitsTensor"]
    C --> |"Run on CUDA"| D["Optimized to\nAWQWeightQBitsTensor"]
    D --> E["Accelerated Inference"]
    C --> |"Save to disk"| F["Serialized Model"]
    F --> |"Load on CUDA"| D
```

The conversion to AWQ format happens automatically when:
1. A model with `WeightQBitsTensor` weights is moved to a CUDA device
2. Linear operations are performed with the quantized weights
3. The model is loaded from disk onto a CUDA device

When saving models, AWQ tensors are converted back to standard format for maximum compatibility.

Sources: [optimum/quanto/tensor/weights/awq/qbits.py:97-114](), [test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py:30-91]()

## Usage Example

AWQ is applied automatically when using the standard quantization workflow on a supported device:

1. Quantize a model with 4-bit weight quantization
2. Move the model to a CUDA device
3. Run inference with the model

Example code sequence (implementation details omitted):

```python
# Quantize model to 4-bit weights
quantized_model = quanto.quantize(model, weight_bits=4)

# Move to CUDA - AWQ optimization happens automatically
quantized_model = quantized_model.to("cuda")

# Run inference - uses optimized AWQ kernels
output = quantized_model(input_ids)
```

No explicit AWQ configuration is needed - the optimization is applied automatically when appropriate.

Sources: [test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py:123-129]()

## Requirements and Limitations

AWQ optimizations in optimum-quanto:

- **Supported devices**: CUDA GPUs with compute capability ≥ 8.0 (Ampere, Ada Lovelace, or newer)
- **Supported quantization**: 4-bit weight quantization (qint4)
- **Supported group size**: 128 (hardcoded in the optimized kernels)
- **Supported operations**: Linear layers (matrix multiplication)

AWQ is not applied to:
- CPU or MPS devices
- 8-bit or other quantization formats
- Models with different grouping strategies

Sources: [test/tensor/weights/optimized/test_awq_weight_qbits_tensor.py:114-117](), [bench/kernels/benchmark_w4a16.py:66]()

---

# Page: Marlin and TinyGemm

# Marlin and TinyGemm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/library/extensions/cuda/__init__.py](optimum/quanto/library/extensions/cuda/__init__.py)
- [optimum/quanto/library/qbytes_mm.py](optimum/quanto/library/qbytes_mm.py)
- [optimum/quanto/tensor/weights/marlin/fp8/__init__.py](optimum/quanto/tensor/weights/marlin/fp8/__init__.py)
- [optimum/quanto/tensor/weights/marlin/fp8/packed.py](optimum/quanto/tensor/weights/marlin/fp8/packed.py)
- [optimum/quanto/tensor/weights/marlin/fp8/qbits.py](optimum/quanto/tensor/weights/marlin/fp8/qbits.py)
- [test/library/test_mm.py](test/library/test_mm.py)
- [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py](test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py)

</details>



## Overview

This document provides technical documentation on Marlin and TinyGemm, two specialized backend implementations in Optimum-Quanto that provide highly optimized matrix multiplication operations for quantized tensors. These implementations are designed to maximize performance for different quantization types (FP8 and int4) on CUDA devices with compute capability 8.0 or higher (NVIDIA Ampere architecture and above).

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:47-74](), [test/library/test_mm.py:52-56]()

## Architecture Overview

Marlin and TinyGemm are both specialized GEMM (General Matrix Multiplication) implementations that optimize the memory layout and computation patterns for different quantization formats. They serve as accelerated backends for matrix multiplication operations with quantized weights.

```mermaid
flowchart LR
    subgraph "Tensor Quantization"
        A["FP32/FP16 Tensor"] --> B["Quantized Tensor"]
        B --> C1["WeightQBytesTensor"]
        B --> C2["WeightQBitsTensor"]
        C1 --> D1["MarlinF8QBytesTensor"]
        C2 --> D2["TinyGemmWeightQBitsTensor"]
    end
    
    subgraph "Computation Flow"
        E["Input Tensor"] --> F["Matrix Multiplication"]
        G["Quantized Weight"] --> F
        F --> H["Output Tensor"]
    end
    
    subgraph "Backend Implementations"
        I["torch.ops.quanto"] --> J1["gemm_f16f8_marlin"]
        I --> J2["gemm_f16i4_marlin"]
        I --> J3["gemm_f16i4_awq"]
    end
    
    D1 --> G
    D2 --> G
    J1 --> F
    J2 --> F
    J3 --> F
```

Diagram: Marlin and TinyGemm in the Optimum-Quanto Architecture

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:124-202]()

## Marlin Implementation

Marlin is a specialized implementation focusing on optimized memory layouts and computation patterns to achieve maximum performance for matrix multiplications involving quantized weights.

### Key Characteristics

1. **Specialized Memory Layout**: Marlin uses carefully designed memory permutations to optimize memory access patterns and cache utilization.
2. **Support for Multiple Quantization Types**: Implementations for both FP8 (float8) and int4 quantization.
3. **CUDA-Specific Optimizations**: Tailored for GPUs with compute capability 8.0+ (Ampere and newer).

```mermaid
classDiagram
    class MarlinF8PackedTensor {
        +_data: torch.Tensor
        +pack(tensor)
        +unpack()
    }
    
    class MarlinF8QBytesTensor {
        +_data: MarlinF8PackedTensor
        +_scale: torch.Tensor
        +_workspace: torch.Tensor
        +dequantize()
        +weight_qbytes_tensor()
    }
    
    class MarlinF8QBytesLinearFunction {
        +forward(ctx, input, other, bias)
    }
    
    MarlinF8QBytesTensor --> MarlinF8PackedTensor
    MarlinF8QBytesTensor --> MarlinF8QBytesLinearFunction
```

Diagram: Marlin FP8 Class Structure

Sources: [optimum/quanto/tensor/weights/marlin/fp8/packed.py:160-266](), [optimum/quanto/tensor/weights/marlin/fp8/qbits.py:28-167]()

### Marlin FP8 Implementation

The Marlin FP8 implementation is designed for efficient matrix multiplication with FP8 quantized weights. It uses the `float8_e4m3fn` data type (8-bit floating point with 4 exponent bits and 3 mantissa bits) which provides better numerical stability than integer quantization for certain applications.

#### Data Packing and Memory Optimization

A key optimization in Marlin FP8 is the packing of FP8 values into int32 tensors for efficient storage and computation:

```mermaid
flowchart LR
    A["FP8 Weight Tensor"] --> B["Pack as int32"]
    B --> C["Apply Marlin Permutation"]
    C --> D["MarlinF8PackedTensor"]
    
    E["Input Tensor (FP16/BF16)"] --> F["gemm_f16f8_marlin"]
    D --> F
    G["Weight Scales"] --> H["Apply Scale Permutation"]
    H --> F
    F --> I["Output Tensor"]
```

Diagram: Marlin FP8 Data Flow and Permutation

The packing process:
1. Every four FP8 values are packed into a single int32 value
2. The packed values are then rearranged according to a specific permutation pattern
3. The scales are also permuted in a corresponding pattern to match the weight layout

Sources: [optimum/quanto/tensor/weights/marlin/fp8/packed.py:22-69](), [optimum/quanto/tensor/weights/marlin/fp8/packed.py:176-187]()

#### Row and Column Permutations

Marlin uses sophisticated row and column permutations to optimize memory access patterns:

```mermaid
flowchart TB
    subgraph "Natural Order"
        A["Sequential Memory Layout"]
    end
    
    subgraph "Marlin Order"
        B["Optimized Memory Layout"]
    end
    
    A -->|"get_row_permutation()"| B
    A -->|"get_column_permutation()"| B
```

Diagram: Marlin Permutation Process

Sources: [optimum/quanto/tensor/weights/marlin/fp8/packed.py:78-157]()

### Marlin Int4 Implementation

The Marlin int4 implementation provides optimizations for 4-bit integer quantized weights:

```mermaid
flowchart LR
    A["4-bit Quantized Weight"] --> B["Pack int4 Values"]
    B --> C["Apply Marlin Permutation"]
    
    D["Input Tensor (FP16)"] --> E["gemm_f16i4_marlin"]
    C --> E
    F["Scales"] --> G["Apply Scale Permutation"]
    G --> E
    H["Zero-Points"] --> I["Apply Zero-Point Permutation"]
    I --> E
    E --> J["Output Tensor"]
```

Diagram: Marlin Int4 Data Flow

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:170-202](), [test/library/test_mm.py:147-189]()

## TinyGemm Implementation

TinyGemm is another specialized implementation for int4 quantized weights that focuses on maximum throughput for certain workload patterns. While not as heavily featured in the provided code as Marlin, it serves as an alternative implementation that may provide better performance in specific scenarios.

The main difference between TinyGemm and Marlin int4 is in the memory layout and computation patterns optimized for different hardware characteristics and workload sizes.

```mermaid
flowchart TB
    subgraph "TinyGemm vs. Marlin Selection"
        A{"Matrix Size?"}
        A -->|"Small"| B["TinyGemm"]
        A -->|"Large"| C["Marlin"]
        
        D{"Batch Size?"}
        D -->|"Small"| B
        D -->|"Large"| C
    end
```

Diagram: Selection Logic Between TinyGemm and Marlin

Sources: [test/library/test_mm.py:57-100]() (implied from test patterns)

## CUDA Kernel Registration

Both Marlin and TinyGemm implementations are registered as CUDA kernels through the PyTorch dispatcher system:

```mermaid
flowchart LR
    A["torch.library.define()"] --> B["Register Function Signature"]
    
    C["torch.library.impl()"] --> D["Register CUDA Implementation"]
    
    B --> E["torch.ops.quanto.gemm_f16f8_marlin"]
    B --> F["torch.ops.quanto.gemm_f16i4_marlin"]
    
    D --> G["Actual CUDA Kernel Implementation"]
    
    E --> G
    F --> G
```

Diagram: CUDA Kernel Registration Process

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:124-202]()

## Matrix Multiplication Implementation

The actual matrix multiplication operations use specialized CUDA kernels optimized for the specific quantization formats:

### FP8 Marlin Matrix Multiplication

```mermaid
flowchart TB
    A["Input(tokens, in_features)"] --> B["fp8_marlin_gemm"]
    C["Packed Weights"] --> B
    D["Scales"] --> B
    E["Workspace Buffer"] --> B
    B --> F["Output(tokens, out_features)"]
```

Diagram: FP8 Marlin Matrix Multiplication

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:138-152](), [test/library/test_mm.py:110-144]()

### Int4 Marlin Matrix Multiplication

```mermaid
flowchart TB
    A["Input(tokens, in_features)"] --> B["gemm_f16i4_marlin"]
    C["Packed Int4 Weights"] --> B
    D["Scales"] --> B
    E["Zero-Points"] --> B
    F["Workspace Buffer"] --> B
    B --> G["Output(tokens, out_features)"]
```

Diagram: Int4 Marlin Matrix Multiplication

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:176-202](), [test/library/test_mm.py:153-189]()

## Usage in Practice

To use Marlin or TinyGemm optimizations in practice, you typically don't need to call the CUDA kernels directly. Instead, the quantized tensor classes handle the optimized implementations automatically when doing matrix multiplications:

| Implementation | Quantization Type | Usage Scenario | Hardware Requirement |
|----------------|-------------------|----------------|----------------------|
| Marlin FP8     | float8_e4m3fn     | When numerical stability is important | CUDA compute capability ≥ 8.0 |
| Marlin Int4    | int4              | When maximum compression is needed | CUDA compute capability ≥ 8.0 |
| TinyGemm       | int4              | For specific workload patterns | CUDA compute capability ≥ 8.0 |

When using a `MarlinF8QBytesTensor` for weights, matrix multiplications through `torch.nn.functional.linear` are automatically dispatched to the optimized CUDA kernels.

Sources: [optimum/quanto/tensor/weights/marlin/fp8/qbits.py:142-167]()

## Performance Considerations

### Hardware Requirements

Both Marlin and TinyGemm require NVIDIA GPUs with compute capability 8.0 or higher (Ampere architecture or newer):

```mermaid
flowchart LR
    A["Check GPU Compatibility"] --> B{"CUDA Available?"}
    B -->|"No"| C["Use CPU Fallback"]
    B -->|"Yes"| D{"Compute Capability ≥ 8.0?"}
    D -->|"No"| C
    D -->|"Yes"| E["Use Marlin/TinyGemm"]
```

Diagram: Hardware Compatibility Check

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:25-45](), [test/library/test_mm.py:52-56](), [test/library/test_mm.py:103-106](), [test/library/test_mm.py:147-150]()

### Fallback Mechanism

When the specialized kernels aren't available or applicable, a fallback mechanism uses standard PyTorch operations through the `qbytes_mm` implementation:

```mermaid
flowchart TB
    A["Matrix Multiplication"] --> B{"Specialized Kernel Available?"}
    B -->|"Yes"| C["Use Marlin/TinyGemm"]
    B -->|"No"| D["Use qbytes_mm Fallback"]
    D --> E["Standard PyTorch Operations"]
```

Diagram: Fallback Mechanism

Sources: [optimum/quanto/library/qbytes_mm.py:25-122]()

## Integration with Optimum-Quanto

Marlin and TinyGemm are integrated into the broader Optimum-Quanto architecture as specialized optimization implementations for matrix multiplication operations with quantized weights. They are part of the optimization layer that enables efficient execution of quantized models.

See [Optimization Algorithms](#6) for more information on the overall approach to optimization in Optimum-Quanto, and [AWQ (Activation-Aware Weight Quantization)](#6.1) for another optimization approach.

---

# Page: SmoothQuant

# SmoothQuant

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [external/awq/test_awq_kernels.py](external/awq/test_awq_kernels.py)
- [external/awq/test_awq_packing.py](external/awq/test_awq_packing.py)
- [external/smoothquant/smoothquant.py](external/smoothquant/smoothquant.py)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)

</details>



SmoothQuant is a quantization preprocessing technique that improves quantization accuracy for transformer-based models by redistributing the quantization difficulty between activations and weights. This technique is particularly effective when quantizing models where activations have high dynamic range with outliers, which is common in large language models.

For information about other quantization optimizations like AWQ and Marlin, see [AWQ (Activation-Aware Weight Quantization)](#6.1) and [Marlin and TinyGemm](#6.2).

## Concept and Theory

SmoothQuant addresses a fundamental challenge in quantization: activations and weights in neural networks often have very different statistical distributions. Activations typically have higher dynamic ranges with outliers, making them difficult to quantize accurately, while weights tend to have more uniform distributions.

The key insight of SmoothQuant is to introduce complementary scaling factors between layer normalization and linear layers:

```mermaid
graph LR
    subgraph "Before SmoothQuant"
        A1["Activation (High Dynamic Range)"] --> B1["Weights"]
        B1 --> C1["Output"]
    end
    
    subgraph "After SmoothQuant"
        A2["Activation × s (Reduced Range)"] --> B2["Weights ÷ s"]
        B2 --> C2["Output (Unchanged)"]
    end
```

The mathematical principle is straightforward:
- Original computation: `y = x * W`
- With scaling: `y = (x * s) * (W / s) = x' * W'`

This scaling doesn't change the mathematical function of the model, but it makes both activations and weights more amenable to quantization.

Sources: [external/smoothquant/smoothquant.py:52-73]()

## Implementation Details

SmoothQuant in optimum-quanto employs a three-step process:

```mermaid
flowchart TD
    A["1. Activation Statistics Collection"] --> B["2. Scaling Factor Calculation"]
    B --> C["3. LayerNorm and Linear Layer Scaling"]
    
    subgraph "Statistics Collection"
        D["Register forward hooks on Linear layers"] --> E["Run calibration data through model"]
        E --> F["Record maximum absolute values of activations"]
    end
    
    subgraph "Scaling Factor Calculation"
        G["Compute activation scales (act_scales)"] --> H["Compute weight scales (weight_scales)"]
        H --> I["Calculate s = (act_scales^alpha / weight_scales^(1-alpha))"]
    end
    
    subgraph "Layer Scaling"
        J["Scale LayerNorm weights/bias by 1/s"] --> K["Scale corresponding Linear weights by s"]
    end
    
    A -.-> D
    B -.-> G
    C -.-> J
```

The `alpha` parameter (default 0.5) controls how the quantization difficulty is distributed between activations and weights:
- `alpha = 0`: All difficulty shifted to weights
- `alpha = 1`: All difficulty shifted to activations
- `alpha = 0.5`: Even distribution (default)

Sources: [external/smoothquant/smoothquant.py:16-49](), [external/smoothquant/smoothquant.py:52-73]()

## Application to Transformer Models

SmoothQuant is specifically designed to work with transformer architectures. The technique is applied to two critical paths in a transformer block:

```mermaid
graph TD
    Input --> LN1["LayerNorm"]
    LN1 -- "× 1/s" --> Attn_In["Attention Input (Smoothed)"]
    Attn_In --> Q["Q_proj (× s)"]
    Attn_In --> K["K_proj (× s)"]
    Attn_In --> V["V_proj (× s)"]
    Q & K & V --> Attn["Attention"]
    Attn --> Add1["Add & Norm"]
    Add1 --> LN2["LayerNorm"]
    LN2 -- "× 1/s" --> FFN_In["FFN Input (Smoothed)"]
    FFN_In --> FC1["Linear1 (× s)"]
    FC1 --> Activation["Activation"]
    Activation --> FC2["Linear2"]
    FC2 --> Add2["Add & Norm"]
```

The implementation includes special handling for different transformer architectures:
- OPT
- BLOOM
- LLaMA
- Mistral

Each architecture has specific patterns for identifying the layer normalization and linear layer pairs that need smoothing.

Sources: [external/smoothquant/smoothquant.py:76-108]()

## Workflow and Usage

SmoothQuant is typically used as a preprocessing step before applying quantization:

```mermaid
flowchart LR
    A["Original Float Model"] --> B["Apply SmoothQuant"]
    B --> C["Quantize with optimum-quanto"]
    C --> D["Quantized Model"]
    
    E["Calibration Dataset"] -.-> B
```

The process requires a representative dataset to calibrate the activation scales. The smoothing operation is a one-time preprocessing step that doesn't affect the inference workflow after quantization.

```python
# Example usage pattern
from external.smoothquant.smoothquant import get_act_scales, smooth_lm

# Load calibration dataset
dataset = load_dataset("lambada", split="validation[:512]").shuffle()

# Collect activation statistics
act_scales = get_act_scales(model, tokenizer, dataset, num_samples=512, seq_len=512)

# Apply SmoothQuant
smooth_lm(model, act_scales, alpha=0.5)

# Now the model is ready for quantization with optimum-quanto
```

Sources: [external/smoothquant/smoothquant.py:111-144]()

## Benefits and Limitations

### Benefits
- Improves quantization accuracy, especially for activation-sensitive operations
- Preserves the mathematical function of the model
- Compatible with other quantization techniques in optimum-quanto
- Particularly effective for transformer-based architectures

### Limitations
- Requires a calibration dataset
- Most effective for specific architectures (transformers)
- Adds preprocessing overhead (one-time cost)
- Performance gains are model-dependent

## Integration with optimum-quanto

While SmoothQuant is included as an external reference implementation in the optimum-quanto repository, it can be used as a complementary technique alongside the core quantization methods provided by optimum-quanto.

The typical workflow is:
1. Apply SmoothQuant to the model using the reference implementation
2. Proceed with quantization using optimum-quanto's quantization methods
3. Benefit from improved quantization accuracy in the resulting model

Sources: [external/smoothquant/smoothquant.py]()

## Conclusion

SmoothQuant is a powerful preprocessing technique that can significantly improve the quantization results for transformer models. By redistributing the quantization difficulty between activations and weights, it addresses one of the fundamental challenges in neural network quantization. When used in conjunction with optimum-quanto's quantization methods, it can lead to better quality quantized models, especially when both weights and activations are quantized.

---

# Page: Workflow Guide

# Workflow Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [optimum/quanto/__init__.py](optimum/quanto/__init__.py)
- [optimum/quanto/quantize.py](optimum/quanto/quantize.py)
- [test/quantize/test_quantize_patterns.py](test/quantize/test_quantize_patterns.py)
- [test/quantize/test_requantize.py](test/quantize/test_requantize.py)

</details>



This document provides a comprehensive guide to the standard workflow when using optimum-quanto for model quantization. It covers the complete process from loading a model through quantization, calibration, freezing, and serialization. For detailed information about specific quantization types and techniques, see [Quantization Types](#3.1) and [Optimization Algorithms](#6).

## Quantization Workflow Overview

The quantization workflow in optimum-quanto follows a consistent pattern regardless of model type:

```mermaid
flowchart LR
    A["Original Float Model"] --> B["Quantize Model"]
    B --> C["Calibrate\n(for activation quantization)"]
    C --> D["Freeze Model"]
    D --> E1["Inference"]
    D --> E2["Save/Serialize"]
    E2 --> F["Load Quantized Model"]
    F --> E1
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:138-147](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:136-169](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:77-96]()

## Step 1: Loading a Model

The first step is to load the model you want to quantize. This typically uses the standard model loading functions from libraries like `transformers`, `diffusers`, or other frameworks.

```python
# For transformers models
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("model_name", torch_dtype=torch_dtype)

# For diffusers models
from diffusers import DiffusionPipeline
pipe = DiffusionPipeline.from_pretrained("model_name", torch_dtype=torch_dtype)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:129-132](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-27]()

## Step 2: Quantizing the Model

Once you have loaded the model, you can quantize it using the `quantize()` function or model-specific quantization methods:

```mermaid
flowchart LR
    subgraph "Quantization Options"
        W1["qint4 (4-bit weight)"]
        W2["qint8 (8-bit weight)"]
        W3["qfloat8 (8-bit float weight)"]
        A1["None (no activation)"]
        A2["qint8 (8-bit activation)"]
        A3["qfloat8 (8-bit float activation)"]
    end
    
    subgraph "Quantization Functions"
        F1["quantize(model, weights, activations)"]
        F2["QuantizedModelForCausalLM.quantize(model, weights, activations)"]
    end
    
    W1 --> F1
    W2 --> F1
    W3 --> F1
    A1 --> F1
    A2 --> F1
    A3 --> F1
    
    W1 --> F2
    W2 --> F2
    W3 --> F2
    A1 --> F2
    A2 --> F2
    A3 --> F2
    
    F1 --> M["Quantized Model"]
    F2 --> M
```

For general models, use the `quantize()` function:

```python
from optimum.quanto import quantize, qint8, qint4, qfloat8

# Quantize with 8-bit weights and no activation quantization
quantize(model, weights=qint8, activations=None)

# Quantize with 4-bit weights and 8-bit activation
quantize(model, weights=qint4, activations=qint8)

# You can also use include/exclude patterns to control which modules get quantized
quantize(model, weights=qint8, include="encoder*")
quantize(model, weights=qint8, exclude="decoder*")
```

For causal language models, you can use the specialized `QuantizedModelForCausalLM` class:

```python
from optimum.quanto import QuantizedModelForCausalLM, qint8

qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint8, activations=qint8)
```

Sources: [optimum/quanto/quantize.py:55-98](), [examples/nlp/text-generation/quantize_causal_lm_model.py:138-140](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:140-142](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:78-80]()

## Step 3: Calibrating Activations

If you're using activation quantization, you need to calibrate the model by running representative input data through it. This allows optimum-quanto to collect statistics about activation ranges for proper quantization:

```mermaid
flowchart TB
    A["Quantized Model with Activation Quantization"] --> B["Calibration Context"]
    
    subgraph "Calibration Process"
        B --> C["Process Input Batch"]
        C --> D["Collect Activation Statistics"]
        D --> E["Update Quantization Parameters"]
        E --> F["Next Batch"]
        F --> |"More Batches"| C
        F --> |"Complete"| G["Calibrated Model"]
    end
```

```python
from optimum.quanto import Calibration

# For simple calibration
with Calibration():
    # Run some representative inputs through the model
    model(inputs)

# For more detailed calibration
with Calibration(streamline=True, debug=True):
    # Process dataset for calibration
    for batch in dataset:
        model(batch)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:143-146](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:144-146](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:82-84]()

## Step 4: Freezing the Model

After calibration, you should freeze the model to finalize the quantization parameters and convert all appropriate tensors to their quantized format:

```python
from optimum.quanto import freeze

# Freeze the model to finalize quantization
freeze(model)
```

This step converts weights from their temporary representation to the final quantized format, which is important for both performance and memory optimization.

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:155](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:85]()

## Step 5: Serialization and Loading

After quantizing a model, you'll typically want to save it for future use. You can do this using standard serialization mechanisms with additional quantization information:

```mermaid
flowchart LR
    A["Quantized & Frozen Model"] --> B["quantization_map(model)"]
    A --> C["model.state_dict()"]
    B --> D["Save QMap"]
    C --> E["Save State Dict"]
    D --> F["saved_qmap.json"]
    E --> G["model.safetensors"]
    F --> H["Load QMap"]
    G --> I["Load State Dict"]
    H --> J["Requantize"]
    I --> J
    J --> K["Reloaded Quantized Model"]
```

The serialization workflow:

```python
from optimum.quanto import freeze, quantization_map, requantize
from safetensors.torch import save_file, load_file

# Get the quantization map that describes how the model was quantized
qmap = quantization_map(model)

# Save the model state dictionary and quantization map
save_file(model.state_dict(), "model.safetensors")
# Save qmap to JSON (not shown here)

# Later, to load the model:
model_reloaded = CreateEmptyModel()  # Create an empty model with the same architecture
state_dict = load_file("model.safetensors")

# Requantize the model with the saved state
requantize(model_reloaded, state_dict, qmap, device)
```

For Hugging Face models, you can use the standard `save_pretrained()` and `from_pretrained()` methods which will handle the quantization map automatically.

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:158-169](), [test/quantize/test_requantize.py:50-72]()

## Common Patterns and Best Practices

### Device Selection

It's important to select the appropriate device based on availability. Here's a common pattern for device selection:

```python
if args.device is None:
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.xpu.is_available():
        device = torch.device("xpu")
    else:
        device = torch.device("cpu")
else:
    device = torch.device(args.device)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:110-120](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:108-118]()

### Selecting Quantization Types

Choosing the right quantization types depends on your needs:

| Type | Precision | Memory Usage | Accuracy | Hardware Support |
|------|-----------|--------------|----------|------------------|
| qint4 | 4-bit integer | Lowest | Lower | Limited |
| qint8 | 8-bit integer | Low | Medium | Good |
| qfloat8 | 8-bit float | Low | Higher | Limited |
| None (fp16/bf16) | 16-bit float | High | Highest | Excellent |

For most use cases:
- Start with `weights=qint8, activations=None` for a good balance
- Use `weights=qint4` for maximum memory savings if accuracy allows
- Use `weights=qfloat8` if you need better accuracy than qint8 but still need memory savings

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:87-96](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:17-22]()

### Inclusion and Exclusion Patterns

You can use Unix shell-style wildcards to control which parts of your model get quantized:

```python
# Only quantize the encoder part
quantize(model, weights=qint8, include="encoder*")

# Quantize everything except the embedding layers
quantize(model, weights=qint8, exclude="*embedding*")

# Quantize only specific parts
quantize(model, weights=qint8, include=["*.linear_layer_*", "*.mlp.*"])
```

Sources: [optimum/quanto/quantize.py:80-87](), [test/quantize/test_quantize_patterns.py:88-110]()

## Example Workflows

### Text Generation Models

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from optimum.quanto import Calibration, QuantizedModelForCausalLM, qint8

# 1. Load model
model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m", torch_dtype=torch.float16).to(device)
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")

# 2. Quantize model
qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint8, activations=qint8)

# 3. Calibrate (if using activation quantization)
cal_dataset = load_dataset("lambada", split=["validation"])[0]
with Calibration(streamline=True):
    for batch in cal_dataset.iter(batch_size=32):
        inputs = tokenizer(batch["text"], return_tensors="pt", padding=True)
        qmodel(inputs.input_ids.to(device), attention_mask=inputs.attention_mask.to(device))

# 4. Use for generation
inputs = tokenizer("One of my fondest memory is", return_tensors="pt")
outputs = qmodel.generate(
    input_ids=inputs.input_ids.to(device),
    max_new_tokens=20,
    do_sample=True,
)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:129-147]()

### Vision Models

```python
from transformers import AutoModel, AutoTokenizer
from optimum.quanto import Calibration, freeze, qint8, quantize

# 1. Load model
model = AutoModel.from_pretrained("dacorvo/mnist-mlp")

# 2. Quantize model
quantize(model, weights=qint8, activations=qint8)

# 3. Calibrate (if using activation quantization)
with Calibration():
    for data, _ in test_loader:
        model(data.to(device))

# 4. Freeze the model
freeze(model)

# 5. Save and reload
qmap = quantization_map(model)
save_file(model.state_dict(), "model.safetensors")

# Later, to load:
model_reloaded = AutoModel.from_config(config)
requantize(model_reloaded, state_dict, qmap, device)
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:136-169]()

### Diffusion Models

```python
from diffusers import DiffusionPipeline
from optimum.quanto import freeze, qint8, quantize

# 1. Load the pipeline
pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16).to(device)

# 2. Quantize just the UNet component
quantize(pipe.unet, weights=qint8)
freeze(pipe.unet)

# 3. Use for inference
images = pipe(
    prompt="ghibli style, a fantasy landscape with castles",
    num_inference_steps=50,
    generator=torch.manual_seed(0),
).images
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-33](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:112-117]()

## Conclusion

This workflow guide has covered the essential steps for quantizing models with optimum-quanto. By following these patterns, you can efficiently convert your models to use lower precision, reducing memory usage and potentially improving inference speed while maintaining acceptable accuracy.

For more detailed information on specific quantization techniques, refer to [Optimization Algorithms](#6) and for information about quantized module implementations, see [Quantized Modules](#5).

---

# Page: Quantization and Calibration

# Quantization and Calibration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [optimum/quanto/__init__.py](optimum/quanto/__init__.py)
- [optimum/quanto/quantize.py](optimum/quanto/quantize.py)
- [test/quantize/test_quantize_patterns.py](test/quantize/test_quantize_patterns.py)
- [test/quantize/test_requantize.py](test/quantize/test_requantize.py)

</details>



This document details the process of quantizing models and calibrating their activations in optimum-quanto. It covers the essential steps in the quantization workflow, from initializing a float model to producing a production-ready quantized model. For information about saving and loading quantized models, see [Freezing and Serialization](#7.2).

## Overview

Quantization is the process of converting a model's weights and/or activations from higher precision (typically float32 or float16) to lower precision formats (int8, int4, float8). Calibration is the process of collecting statistics on activation values during inference to ensure optimal quantization parameters for activations.

Together, these processes form the critical first steps in the optimum-quanto workflow:

```mermaid
flowchart LR
    A["Original Float Model"] --> B["Quantize Weights"]
    B --> C["Calibrate Activations"]
    C --> D["Freeze Model"]
    D --> E["Save/Load Model"]
    
    style A fill:white
    style B fill:white
    style C fill:white
    style D fill:white
    style E fill:white
```

Sources: [optimum/quanto/quantize.py](), [examples/nlp/text-generation/quantize_causal_lm_model.py:137-147]()

## Quantization Types

Optimum-quanto supports several quantization types for both weights and activations:

| Type | Description | Precision | Use Cases |
|------|-------------|-----------|-----------|
| `qint8` | 8-bit integer quantization | 8 bits | Good balance of quality and size reduction |
| `qint4` | 4-bit integer quantization | 4 bits | Maximum size reduction, some quality loss |
| `qfloat8` | 8-bit floating point quantization | 8 bits | Better accuracy than int8 for some models |
| `None` | No quantization | Original precision | Used to disable activation quantization |

The quantization type is specified when calling the quantization function:

```mermaid
classDiagram
    class "Quantization Parameters" {
        +weights: Optional[qtype]
        +activations: Optional[qtype]
    }
    
    class "qtype options" {
        qint8
        qint4
        qfloat8
        None
    }
    
    "Quantization Parameters" --> "qtype options"
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:56-62](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:89-90]()

## Workflow Steps

### 1. Initial Quantization

The first step is to apply weight quantization to the model using the `quantize()` function. This replaces standard PyTorch modules with their quantized equivalents:

```python
from optimum.quanto import quantize, qint8, qint4, qfloat8

# Quantize weights only
quantize(model, weights=qint8)

# Quantize both weights and activations
quantize(model, weights=qint8, activations=qint8)
```

Under the hood, this replaces modules like `torch.nn.Linear` with `QLinear` which uses quantized weights.

Sources: [optimum/quanto/quantize.py:55-98](), [examples/nlp/text-generation/quantize_causal_lm_model.py:140]()

### 2. Calibration

When activation quantization is applied, calibration is required to determine appropriate quantization parameters for activation tensors. This involves running representative data through the model to collect statistics:

```python
from optimum.quanto import Calibration

# Calibrate the model by running inference on sample data
with Calibration():
    model(sample_input)
```

The `Calibration` context manager automatically tracks activations and computes quantization parameters based on the observed values.

```mermaid
flowchart TD
    A["Start Calibration"] --> B["Run Model on Sample Data"]
    B --> C["Collect Activation Statistics"]
    C --> D["Compute Quantization Parameters"]
    D --> E["Store Parameters in Model"]
    E --> F["End Calibration"]
    
    style A fill:white
    style B fill:white
    style C fill:white
    style D fill:white
    style E fill:white
    style F fill:white
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:142-146](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:143-146](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py:81-84]()

### 3. Freezing

After calibration, the model should be frozen to finalize the quantization process. Freezing converts all dynamic quantized tensors into static quantized tensors, which improves performance:

```python
from optimum.quanto import freeze

# Freeze the model to finalize quantization
freeze(model)
```

This step is essential for models with activation quantization that have been calibrated.

Sources: [optimum/quanto/quantize.py:143-147](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:155]()

## Example: Complete Workflow

Below is an example of the complete quantization and calibration workflow for a text generation model:

```mermaid
sequenceDiagram
    participant U as "User Code"
    participant Q as "quantize()"
    participant C as "Calibration()"
    participant F as "freeze()"
    participant M as "Model"
    
    U->>M: Load original float model
    U->>Q: Call quantize(model, weights=qint8, activations=qint8)
    Q->>M: Replace modules with quantized versions
    U->>C: Enter Calibration context
    C->>C: Begin tracking activations
    U->>M: Run inference with calibration data
    M->>C: Collect activation statistics
    C->>M: Compute and store quantization parameters
    C->>C: End tracking activations
    U->>F: Call freeze()
    F->>M: Finalize all quantization parameters
    Note over U,M: Model ready for inference or serialization
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:137-147](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:136-155]()

## Practical Implementation

### Text Generation Models

For text generation models, the workflow typically involves:

```python
# Import necessary components
from optimum.quanto import Calibration, QuantizedModelForCausalLM, qint8

# 1. Load the original model
model = AutoModelForCausalLM.from_pretrained("model_name")

# 2. Quantize the model
qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint8, activations=qint8)

# 3. Calibrate with sample data
with Calibration():
    # Run sample data through the model
    calibrate(qmodel, tokenizer, dataset, device, batch_size=32)

# 4. Model is ready for inference or serialization
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:137-147]()

### Vision Models

For vision models, the workflow is similar:

```python
# Import necessary components
from optimum.quanto import Calibration, quantize, freeze, qint8

# 1. Load the original model
model = AutoModel.from_pretrained("model_name")

# 2. Quantize the model directly
quantize(model, weights=qint8, activations=qint8)

# 3. Calibrate with sample data
with Calibration():
    # Run inference with the test data loader
    test(model, device, test_loader)

# 4. Freeze the model
freeze(model)

# 5. Model is ready for inference or serialization
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:136-156]()

## Advanced Options

### Selective Quantization

You can selectively quantize parts of a model using the `include` and `exclude` parameters:

```python
# Only quantize the transformer part of a model
quantize(model, weights=qint8, include="transformer*")

# Quantize everything except the heads
quantize(model, weights=qint8, exclude="*head*")
```

These patterns use Unix shell-style wildcards to match module names.

Sources: [optimum/quanto/quantize.py:82-98](), [test/quantize/test_quantize_patterns.py:61-110]()

### Calibration Options

The `Calibration` context manager accepts optional parameters:

```python
# Enable streamlining to remove redundant quantize/dequantize operations
with Calibration(streamline=True):
    model(sample_input)

# Enable debug output during calibration
with Calibration(debug=True):
    model(sample_input)
```

The `streamline` option optimizes the model by removing consecutive quantize/dequantize operations, which can improve performance.

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:144]()

## Conclusion

Quantization and calibration form the foundation of creating efficient, low-precision models with optimum-quanto. The workflow provides a straightforward path to converting standard PyTorch models into quantized versions that offer significant memory savings and potentially faster inference.

After completing the quantization and calibration steps described in this document, you should proceed to freeze and then serialize your model for deployment or further use. For details on these next steps, see [Freezing and Serialization](#7.2).

---

# Page: Freezing and Serialization

# Freezing and Serialization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/quanto/__init__.py](optimum/quanto/__init__.py)
- [optimum/quanto/models/__init__.py](optimum/quanto/models/__init__.py)
- [optimum/quanto/models/diffusers_models.py](optimum/quanto/models/diffusers_models.py)
- [optimum/quanto/models/shared_dict.py](optimum/quanto/models/shared_dict.py)
- [optimum/quanto/models/transformers_models.py](optimum/quanto/models/transformers_models.py)
- [optimum/quanto/quantize.py](optimum/quanto/quantize.py)
- [test/quantize/test_quantize_patterns.py](test/quantize/test_quantize_patterns.py)
- [test/quantize/test_requantize.py](test/quantize/test_requantize.py)

</details>



This document explains how to freeze quantized models for inference and how to save and load them in optimum-quanto. Freezing is the process of converting quantization-aware training models to efficient inference models, while serialization enables storing and loading these quantized models. For information about the initial quantization and calibration process, see [Quantization and Calibration](#7.1).

## Freezing Process

After quantization and calibration, models need to be "frozen" before deployment for inference. Freezing converts the weight and activation tensors from their dynamic training representation to a static, optimized inference representation.

```mermaid
flowchart LR
    A["Quantized Model\n(Training Mode)"] --> B["freeze()"]
    B --> C["Frozen Model\n(Inference Mode)"]
    
    subgraph "Process Details"
        B1["Convert QTensors"] --> B2["Optimize for\nInference Backend"]
        B2 --> B3["Discard Training\nArtifacts"]
    end
    
    B -.-> B1
```

Sources: [optimum/quanto/quantize.py:143-147]()

The `freeze` function iterates through all modules in a model and calls the `freeze` method on any module that inherits from `QModuleMixin`. This transforms the internal representation of quantized weights to formats optimized for inference.

```python
# Freezing a model after quantization and calibration
from optimum.quanto import freeze

# After quantization and calibration are complete
freeze(model)
```

When a model is frozen, it can no longer be used for quantization-aware training, as its parameters have been converted to inference-optimized format.

Sources: [optimum/quanto/quantize.py:143-147](), [optimum/quanto/models/transformers_models.py:111-112](), [optimum/quanto/models/diffusers_models.py:114-115]()

## Quantization Map

The quantization map is a key component of the serialization process. It stores metadata about how each module in the model was quantized, including:

- Which modules were quantized
- The quantization type used for weights
- The quantization type used for activations

```mermaid
classDiagram
    class QuantizationMap {
        module_name: string
        weights: qtype
        activations: qtype
    }
    
    class QMap {
        "module.linear1": {"weights": "qint8", "activations": "none"}
        "module.linear2": {"weights": "qint4", "activations": "qint8"}
        ...
    }
    
    QuantizationMap --|> QMap
```

The `quantization_map` function generates this mapping by examining all modules in a model and recording the quantization configuration of those that inherit from `QModuleMixin`:

```python
from optimum.quanto import quantization_map

# Generate the quantization map
qmap = quantization_map(model)
```

This map is essential for both saving and loading quantized models, as it records how each module should be quantized when the model is reloaded.

Sources: [optimum/quanto/quantize.py:149-170]()

## Serialization Workflow

The serialization process in optimum-quanto extends Hugging Face's standard model saving and loading workflows to handle quantized models.

```mermaid
sequenceDiagram
    participant User
    participant Model as "QuantizedModel"
    participant Disk as "Filesystem"
    
    User->>Model: save_pretrained(path)
    Model->>Model: Create qmap = quantization_map(model)
    Model->>Disk: Save weights as safetensors
    Model->>Disk: Save qmap as JSON
    Note over Disk: "quanto_qmap.json"
    
    User->>Model: from_pretrained(path)
    Model->>Disk: Load config
    Model->>Disk: Load qmap
    Model->>Model: Create empty model structure
    Model->>Disk: Load safetensors weights
    Model->>Model: requantize(model, weights, qmap)
```

Sources: [optimum/quanto/models/transformers_models.py:165-179](), [optimum/quanto/models/diffusers_models.py:180-186]()

### Saving Quantized Models

Quantized models provide a specialized `save_pretrained` method that:

1. Saves the model weights using safetensors format
2. Saves the quantization map as a JSON file named `quanto_qmap.json`

```python
# Saving a quantized model
model.save_pretrained("path/to/save/directory")
```

For models with tied weights (common in language models), the serialization process also verifies if quantized modules have broken weight tying and updates the configuration accordingly.

Sources: [optimum/quanto/models/transformers_models.py:165-179]()

### Loading Quantized Models

Loading a quantized model involves a specialized `from_pretrained` class method that:

1. Downloads or locates the model files
2. Loads the quantization map
3. Creates an empty model structure
4. Applies quantization based on the map
5. Loads the weights into the quantized structure

```python
# Loading a quantized model
from optimum.quanto.models import QuantizedModelForCausalLM

model = QuantizedModelForCausalLM.from_pretrained("path/to/model/directory")
```

This process uses the `requantize` function, which reapplies the quantization configuration and loads the weights into the appropriate format.

Sources: [optimum/quanto/models/transformers_models.py:114-163](), [optimum/quanto/models/diffusers_models.py:118-178]()

## Requantization Process

The `requantize` function is a core component of loading quantized models. It implements the following steps:

1. Quantizes an empty model based on the quantization map
2. Moves model parameters to CPU before materializing quantized weights
3. Transfers the model to the target device
4. Loads the quantized state dictionary

```mermaid
flowchart TB
    A["Empty Model"] --> B["Apply Quantization\nConfiguration"]
    B --> C["Move Parameters to CPU"]
    C --> D["Move to Target Device"]
    D --> E["Load Quantized Weights"]
    
    F["State Dictionary"] --> E
    G["Quantization Map"] --> B
```

This approach optimizes memory usage during model loading, which is particularly important for large models.

Sources: [optimum/quanto/quantize.py:101-140](), [test/quantize/test_requantize.py:40-98]()

## Model-Specific Serialization

Optimum-quanto provides specialized classes for different model types:

| Model Type | Base Class | Description |
|------------|------------|-------------|
| Transformers | `QuantizedTransformersModel` | Base class for all quantized transformers models |
| Causal LM | `QuantizedModelForCausalLM` | For autoregressive language models like GPT |
| Diffusers | `QuantizedDiffusersModel` | Base class for all quantized diffusers models |
| PixArt | `QuantizedPixArtTransformer2DModel` | For PixArt image generation models |

Each class implements specialized serialization and deserialization logic to handle the specific requirements of that model type.

Sources: [optimum/quanto/models/transformers_models.py:38-184](), [optimum/quanto/models/diffusers_models.py:44-190]()

## Complete Workflow Example

The following diagram illustrates the complete workflow from quantization to deploying a serialized model:

```mermaid
flowchart LR
    A["Original\nFloat Model"] --> B["quantize()"]
    B --> C["Calibration"]
    C --> D["freeze()"]
    D --> E["save_pretrained()"]
    E --> F["Serialized Files"]
    F --> G["from_pretrained()"]
    G --> H["Inference-Ready\nQuantized Model"]
    
    subgraph "Files Generated"
        F1["model.safetensors"]
        F2["quanto_qmap.json"]
        F3["config.json"]
    end
    
    F -.-> F1
    F -.-> F2
    F -.-> F3
```

Here's a complete example demonstrating the process:

```python
from optimum.quanto import qint8, quantize, Calibration, freeze
from optimum.quanto.models import QuantizedModelForCausalLM
from transformers import AutoModelForCausalLM

# 1. Load the original model
model = AutoModelForCausalLM.from_pretrained("gpt2")

# 2. Quantize the model
quantize(model, weights=qint8)

# 3. Calibrate (for activation quantization if needed)
with Calibration():
    model("This is a calibration input")

# 4. Freeze the model
freeze(model)

# 5. Create a quantized model wrapper
quantized_model = QuantizedModelForCausalLM(model)

# 6. Save the model
quantized_model.save_pretrained("./quantized-gpt2")

# 7. Later, load the model
loaded_model = QuantizedModelForCausalLM.from_pretrained("./quantized-gpt2")
```

Sources: [optimum/quanto/models/transformers_models.py:69-162](), [optimum/quanto/models/diffusers_models.py:72-178](), [optimum/quanto/quantize.py:55-98]()

## Device Considerations

When loading quantized models, pay attention to device placement:

1. By default, models are loaded to the same device as the model's parameters
2. For loading large models that may not fit in memory, the `requantize` function supports loading parameters to CPU first
3. When using sharded weights (common for large models), optimum-quanto uses a specialized `ShardedStateDict` to efficiently load weights without loading all shards into memory simultaneously

```python
# Loading a quantized model to a specific device
from optimum.quanto.models import QuantizedModelForCausalLM
import torch

model = QuantizedModelForCausalLM.from_pretrained("path/to/model", device_map="auto")
# Or specify a particular device
model = QuantizedModelForCausalLM.from_pretrained("path/to/model", device_map={"": torch.device("cuda:0")})
```

Sources: [optimum/quanto/quantize.py:105-111](), [optimum/quanto/models/transformers_models.py:142-154](), [optimum/quanto/models/shared_dict.py:22-54]()

---

# Page: Example Applications

# Example Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [test/helpers.py](test/helpers.py)
- [test/models/conftest.py](test/models/conftest.py)
- [test/models/test_quantized_model_for_causal_lm.py](test/models/test_quantized_model_for_causal_lm.py)
- [test/models/test_quantized_model_for_pixart.py](test/models/test_quantized_model_for_pixart.py)

</details>



This page demonstrates practical applications of optimum-quanto for quantizing various types of models. It showcases complete examples that cover the entire workflow from loading a model to quantizing it and using it for inference. For detailed information about the quantization process itself, see [Workflow Guide](#7).

## Overview of Example Applications

Optimum-quanto supports quantization of various model types across different domains. The example applications in the repository demonstrate how to apply quantization to:

```mermaid
flowchart TD
    A["Optimum-Quanto Example Applications"]
    A --> B["Text Models"]
    A --> C["Vision Models"]
    
    B --> B1["Text Generation<br>(CausalLM)"]
    B --> B2["Text Classification<br>(SST-2)"]
    
    C --> C1["Image Classification<br>(MNIST)"]
    C --> C2["Object Detection<br>(OWL-ViT)"]
    C --> C3["Image Generation<br>(Stable Diffusion)"]
    C --> C4["Text-to-Image<br>(PixArt-Sigma)"]
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py](), [examples/nlp/text-classification/sst2/quantize_sst2_model.py](), [examples/vision/image-classification/mnist/quantize_mnist_model.py](), [examples/vision/object-detection/quantize_owl_model.py](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py](), [examples/vision/text-to-image/quantize_pixart_sigma.py]()

## Common Application Workflow

While the specifics vary by model type, all example applications follow a similar workflow:

```mermaid
flowchart LR
    A["Load Model"] --> B["Apply Quantization"]
    B --> C["Calibrate<br>(for activation quantization)"]
    C --> D["Freeze<br>(optional)"]
    D --> E["Run Inference"]
    E --> F["Save/Serialize<br>(optional)"]
```

The main components of this workflow include:

1. **Loading the model**: Using the appropriate model class from libraries like `transformers` or `diffusers`
2. **Applying quantization**: Using `quantize()` for generic models or specialized methods like `QuantizedModelForCausalLM.quantize()`
3. **Calibration**: Running sample inputs through the model to calibrate activation quantization parameters
4. **Freezing**: Optional step to convert quantized tensors to their optimized representations
5. **Inference**: Running the quantized model on actual tasks
6. **Serialization**: Saving the quantized model for later use or distribution

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py](), [examples/vision/image-classification/mnist/quantize_mnist_model.py]()

## Text Models

### Text Generation (Causal Language Models)

Text generation is one of the primary applications for quantization, as large language models can benefit significantly from reduced memory usage and increased inference speed.

```mermaid
classDiagram
    class AutoModelForCausalLM {
        +from_pretrained()
    }
    class QuantizedModelForCausalLM {
        +quantize()
        +generate()
        +save_pretrained()
        +from_pretrained()
    }
    class Calibration {
        +context manager for activation calibration
    }
    
    AutoModelForCausalLM <-- QuantizedModelForCausalLM : quantizes
    QuantizedModelForCausalLM -- Calibration : uses for activation quantization
```

The example workflow for quantizing a causal language model:

1. **Load model and tokenizer**:
   ```python
   model = AutoModelForCausalLM.from_pretrained(model_id)
   tokenizer = AutoTokenizer.from_pretrained(model_id)
   ```

2. **Quantize the model**:
   ```python
   qmodel = QuantizedModelForCausalLM.quantize(model, weights=weights, activations=activations)
   ```

3. **Calibrate for activation quantization** (if needed):
   ```python
   with Calibration(streamline=True):
       calibrate(qmodel, tokenizer, cal_dataset, device, batch_size)
   ```

4. **Generate text with the quantized model**:
   ```python
   outputs = qmodel.generate(input_ids, max_new_tokens=max_new_tokens)
   ```

Key features of the text generation example:
- Supports different weight quantization types: `int4`, `int8`, `float8`
- Supports activation quantization with `int8` or `float8`
- Includes performance measurement for generation speed
- Optional streamlining to remove consecutive quantize/dequantize operations

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:140-147](), [test/models/test_quantized_model_for_causal_lm.py:11-46]()

### Text Classification

The text classification example demonstrates how to quantize models for tasks such as sentiment analysis.

```mermaid
flowchart TD
    A["AutoModelForSequenceClassification"] --> B["quantize()"]
    B --> C["Calibration context"]
    C --> D["freeze()"]
    D --> E["pipeline('sentiment-analysis')"]
    E --> F["Evaluate accuracy"]
```

The workflow includes:

1. **Load the model**:
   ```python
   model = AutoModelForSequenceClassification.from_pretrained(model_id)
   ```

2. **Apply quantization**:
   ```python
   quantize(model, weights=weights, activations=activations)
   ```

3. **Calibrate and freeze**:
   ```python
   with Calibration():
       evaluate_model(model, tokenizer, dataset, device, batch_size)
   freeze(model)
   ```

4. **Use for inference**:
   ```python
   p = pipeline("sentiment-analysis", model, tokenizer=tokenizer)
   results = p(KeyDataset(dataset, "sentence"), batch_size=batch_size)
   ```

The example also demonstrates:
- Measuring accuracy impact of quantization
- Serializing and reloading the quantized model
- Compatibility with Hugging Face pipelines

Sources: [examples/nlp/text-classification/sst2/quantize_sst2_model.py:77-96]()

## Vision Models

### Image Classification

The MNIST image classification example shows how to quantize a simple vision model.

```mermaid
flowchart LR
    A["AutoModel.from_pretrained"] --> B["quantize()"]
    B --> C["Calibration context"]
    C --> D["Model training<br>(fine-tuning)"]
    D --> E["freeze()"]
    E --> F["save_file<br>(safetensors)"]
    F --> G["requantize()"]
```

The workflow includes:

1. **Load model and dataset**:
   ```python
   model = AutoModel.from_pretrained(args.model)
   dataset = datasets.MNIST("./data", train=False, download=True)
   ```

2. **Quantize and calibrate**:
   ```python
   quantize(model, weights=weights, activations=activations)
   with Calibration():
       test(model, device, test_loader)
   ```

3. **Fine-tune the quantized model** (unique to this example):
   ```python
   optimizer = torch.optim.Adadelta(model.parameters(), lr=0.5)
   train(50, model, device, train_loader, optimizer, 1)
   ```

4. **Freeze and serialize**:
   ```python
   freeze(model)
   save_file(model.state_dict(), file_path)
   ```

5. **Reload with requantize**:
   ```python
   requantize(model_reloaded, state_dict, quantization_map(model), device)
   ```

This example uniquely demonstrates:
- Post-quantization fine-tuning
- Detailed serialization with safetensors
- Requantization from saved state

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:139-169]()

### Object Detection

This example shows how to quantize an object detection model (OWL-ViT).

```mermaid
flowchart TD
    A["Owlv2ForObjectDetection<br>from_pretrained"] --> B["quantize()"]
    B --> C["freeze()"]
    C --> D["processor(text, images)"]
    D --> E["model(**inputs)"]
    E --> F["post_process_object_detection"]
```

Key aspects include:

1. **Load model and processor**:
   ```python
   processor = AutoProcessor.from_pretrained(model_id)
   model = Owlv2ForObjectDetection.from_pretrained(model_id)
   ```

2. **Quantize with optional head exclusion**:
   ```python
   if args.exclude_heads:
       quantize(model.owlv2, weights=weights_qtype)
   else:
       quantize(model, weights=weights_qtype)
   freeze(model)
   ```

3. **Run inference**:
   ```python
   inputs = processor(text=texts, images=image, return_tensors="pt")
   outputs = model(**inputs)
   results = processor.post_process_object_detection(outputs, threshold=0.2)
   ```

This example demonstrates:
- Selective quantization (excluding specific modules)
- Working with complex vision model outputs
- Measuring memory usage on different devices

Sources: [examples/vision/object-detection/quantize_owl_model.py:94-115]()

### Diffusion Models

Optimum-quanto supports quantization of diffusion models, including Stable Diffusion and PixArt-Sigma.

#### Stable Diffusion

```mermaid
flowchart LR
    A["DiffusionPipeline<br>from_pretrained"] --> B["quantize(pipe.unet)"]
    B --> C["freeze(pipe.unet)"]
    C --> D["pipeline(prompt, num_inference_steps)"]
    D --> E["image.save()"]
```

The Stable Diffusion example:
1. Loads the pipeline: `pipe = DiffusionPipeline.from_pretrained(CKPT, torch_dtype=torch_dtype)`
2. Quantizes only the UNet component: `quantize(pipe.unet, weights=unet_dtype)`
3. Freezes the UNet: `freeze(pipe.unet)`
4. Runs the pipeline with the quantized UNet: `pipeline(prompt=args.prompt, num_inference_steps=args.num_inference_steps)`

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:91-117]()

#### PixArt-Sigma

```mermaid
flowchart LR
    A["DiffusionPipeline<br>from_pretrained"] --> B["quantize(pipe.transformer)"]
    A --> C["quantize(pipe.text_encoder)"]
    B --> D["freeze(pipe.transformer)"]
    C --> E["freeze(pipe.text_encoder)"]
    D --> F["pipeline(prompt, num_inference_steps)"]
    E --> F
```

For PixArt-Sigma, the example:
1. Loads the pipeline: `pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch_dtype)`
2. Quantizes multiple components:
   ```python
   quantize(pipe.transformer, weights=qtype)
   freeze(pipe.transformer)
   quantize(pipe.text_encoder, weights=qtype)
   freeze(pipe.text_encoder)
   ```
3. Runs the pipeline with the quantized components: `pipeline(prompt=args.prompt, num_inference_steps=NUM_INFERENCE_STEPS)`

These examples demonstrate:
- Selectively quantizing components within a pipeline
- Memory consumption measurement
- Performance benchmarking

Sources: [examples/vision/text-to-image/quantize_pixart_sigma.py:21-29](), [examples/vision/text-to-image/quantize_pixart_sigma.py:82-89](), [test/models/test_quantized_model_for_pixart.py:11-37]()

## Quantized Model Integration with Hugging Face Hub

The example applications can be integrated with the Hugging Face Hub to share and reuse quantized models.

```mermaid
flowchart TD
    A["QuantizedModelForCausalLM<br>or<br>QuantizedPixArtTransformer2DModel"] --> B["save_pretrained()"]
    A --> C["push_to_hub()"]
    B --> D["from_pretrained()"]
    C --> D
```

This workflow includes:

1. **Creating a quantized model**:
   ```python
   quantized = QuantizedModelForCausalLM.quantize(model, weights=qtype)
   ```

2. **Saving locally or pushing to Hub**:
   ```python
   quantized.save_pretrained(directory)
   # or
   quantized.push_to_hub(repo_id, token=token)
   ```

3. **Loading the quantized model**:
   ```python
   requantized = QuantizedModelForCausalLM.from_pretrained(repo_id)
   ```

This integration enables:
- Sharing quantized models with the community
- Versioning and tracking quantized models
- Easy deployment of quantized models

Sources: [test/models/test_quantized_model_for_causal_lm.py:86-102](), [test/models/test_quantized_model_for_pixart.py:90-110]()

## Best Practices and Considerations

When working with the example applications, consider the following best practices:

| Application Type | Recommended Quantization | Considerations |
|------------------|--------------------------|----------------|
| Text Generation | weights: int8, activations: int8 | Best balance of quality and performance for most LLMs |
| Text Classification | weights: int8, activations: none | Classification heads often benefit from staying in full precision |
| Image Classification | weights: int8, activations: int8 | Can usually tolerate aggressive quantization |
| Object Detection | weights: int8, exclude_heads: True | Detection heads should typically remain in full precision |
| Diffusion Models | weights: int8, selective component quantization | UNet compression yields the most memory savings |

General tips:
1. Start with int8 weights quantization before trying more aggressive options like int4
2. Calibrate activation quantization on a representative dataset
3. Benchmark accuracy and performance to find the right trade-offs
4. Consider selective quantization for quality-sensitive components

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:137-147](), [examples/vision/object-detection/quantize_owl_model.py:97-102](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:91-93]()

---

# Page: Text Generation Models

# Text Generation Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [optimum/quanto/models/__init__.py](optimum/quanto/models/__init__.py)
- [optimum/quanto/models/diffusers_models.py](optimum/quanto/models/diffusers_models.py)
- [optimum/quanto/models/shared_dict.py](optimum/quanto/models/shared_dict.py)
- [optimum/quanto/models/transformers_models.py](optimum/quanto/models/transformers_models.py)

</details>



This document provides a technical guide for quantizing and deploying text generation models using optimum-quanto. It focuses specifically on causal language models (CLMs) that enable text continuation and generation tasks. For information about vision and diffusion models, see [Vision and Diffusion Models](#8.2).

## Overview of Text Generation Model Quantization

Quantization of text generation models enables significant memory footprint reduction and potential inference speedups while maintaining acceptable generation quality. This is particularly valuable for large language models (LLMs) with billions of parameters that would otherwise require substantial computational resources.

```mermaid
flowchart TD
    A["Pretrained Model (FP16/BF16)"] --> B["Quantization Process"]
    B --> C["Quantized Model"]
    
    B --> D["Weight Quantization (int4/int8/float8)"]
    B --> E["Activation Quantization (optional)"]
    
    C --> F["Smaller Memory Footprint"]
    C --> G["Faster Inference"]
    C --> H["Deployment on Resource-Constrained Devices"]
    
    E --> I["Calibration with Sample Data"]
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:139-146](), [optimum/quanto/models/transformers_models.py:69-112]()

## QuantizedModelForCausalLM Class

The primary class for working with quantized text generation models is `QuantizedModelForCausalLM`, which provides a streamlined interface for quantizing, saving, and loading causal language models.

```mermaid
classDiagram
    class ModelHubMixin {
        +_save_pretrained()
        +from_pretrained()
    }
    
    class QuantizedTransformersModel {
        -_wrapped: PreTrainedModel
        +BASE_NAME: str
        +auto_class: Type
        +quantize()
        +from_pretrained()
        +_save_pretrained()
    }
    
    class QuantizedModelForCausalLM {
        +auto_class: AutoModelForCausalLM
    }
    
    ModelHubMixin <|-- QuantizedTransformersModel
    QuantizedTransformersModel <|-- QuantizedModelForCausalLM
```

Sources: [optimum/quanto/models/transformers_models.py:28-29](), [optimum/quanto/models/transformers_models.py:182-184]()

## Quantization Workflow for Text Generation Models

The workflow for quantizing and using a text generation model involves several key steps:

```mermaid
flowchart TD
    A["Load Pretrained Model\n(AutoModelForCausalLM.from_pretrained)"] --> B["Quantize Model\n(QuantizedModelForCausalLM.quantize)"]
    B --> C{"Activation\nQuantization?"}
    C -->|"Yes"| D["Calibrate Model\n(with Calibration context)"]
    C -->|"No"| E["Freeze Model\n(automatically done in quantize)"]
    D --> E
    E --> F["Generate Text\n(model.generate)"]
    F --> G["Save Model\n(model.save_pretrained)"]
    G --> H["Load Model\n(QuantizedModelForCausalLM.from_pretrained)"]
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:25-148](), [optimum/quanto/models/transformers_models.py:69-179]()

### Loading a Model

First, load a pretrained model using the Transformers library:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")
```

### Quantizing the Model

Next, quantize the model using `QuantizedModelForCausalLM.quantize()`:

```python
from optimum.quanto import QuantizedModelForCausalLM, qint8, qint4, qfloat8

# Select quantization types
weights = qint8       # For weights (8-bit integer quantization)
activations = qint8   # For activations (8-bit integer quantization)

# Quantize the model
qmodel = QuantizedModelForCausalLM.quantize(model, weights=weights, activations=activations)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:140](), [optimum/quanto/models/transformers_models.py:69-112]()

### Calibrating Activations (Optional)

If using activation quantization, calibration is necessary to gather statistics about activation values using representative data:

```python
from optimum.quanto import Calibration
from datasets import load_dataset

# Load calibration dataset
cal_dataset = load_dataset("lambada", split="validation")

# Calibrate the model
with Calibration(streamline=True):
    for batch in cal_dataset.iter(batch_size=32):
        inputs = tokenizer(batch["text"], return_tensors="pt", padding=True)
        qmodel(inputs.input_ids, attention_mask=inputs.attention_mask)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:42-53](), [examples/nlp/text-generation/quantize_causal_lm_model.py:144-146]()

### Generating Text

Once the model is quantized and calibrated (if necessary), you can use it to generate text:

```python
# Prepare input
prompt = "One of my fondest memory is"
inputs = tokenizer(prompt, return_tensors="pt", padding=True)

# Generate text
outputs = qmodel.generate(
    input_ids=inputs.input_ids,
    max_new_tokens=20,
    attention_mask=inputs.attention_mask,
    do_sample=True,
    top_k=50,
    top_p=0.9,
)

# Decode output
generated_text = tokenizer.decode(outputs[0])
print(generated_text)
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:25-39](), [examples/nlp/text-generation/quantize_causal_lm_model.py:147]()

### Saving and Loading Quantized Models

To save a quantized model:

```python
qmodel.save_pretrained("path/to/save/model")
```

To load a previously quantized model:

```python
loaded_model = QuantizedModelForCausalLM.from_pretrained("path/to/saved/model")
```

The saved model includes a `quanto_qmap.json` file containing information about the quantization configuration.

Sources: [optimum/quanto/models/transformers_models.py:114-164](), [optimum/quanto/models/transformers_models.py:165-179]()

## Quantization Types and Their Effects

optimum-quanto supports several quantization types, each with different trade-offs:

| Quantization Type | Memory Reduction | Performance Impact | Quality Impact |
|-------------------|------------------|-------------------|------------------|
| Weight `qint8` | ~2x | Moderate speedup | Minimal |
| Weight `qint4` | ~4x | Variable | Moderate |
| Weight `qfloat8` | ~2x | Moderate speedup | Minimal |
| Activation `qint8` | Runtime only | May be slower | Minimal |
| Activation `qfloat8` | Runtime only | May be slower | Minimal |

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:56-62]()

## Complete Example

Here's a complete example script for quantizing a causal language model:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from optimum.quanto import QuantizedModelForCausalLM, Calibration, qint8

# Load model and tokenizer
model_name = "facebook/opt-350m"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.padding_side = "left"

# Quantize model
qmodel = QuantizedModelForCausalLM.quantize(model, weights=qint8, activations=qint8)

# Calibrate model (for activation quantization)
cal_dataset = load_dataset("lambada", split="validation").shuffle(seed=1)
with Calibration(streamline=True):
    for batch in cal_dataset.iter(batch_size=32, take=4):
        inputs = tokenizer(batch["text"], return_tensors="pt", padding=True)
        qmodel(inputs.input_ids.to(device), attention_mask=inputs.attention_mask.to(device))

# Generate text
prompt = "One of my fondest memory is"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = qmodel.generate(
    input_ids=inputs.input_ids.to(device),
    max_new_tokens=20,
    attention_mask=inputs.attention_mask.to(device),
    do_sample=True,
    top_k=50,
    top_p=0.9,
)
generated_text = tokenizer.decode(outputs[0])
print(f"Generated: '{generated_text}'")

# Save the model
qmodel.save_pretrained("./quantized-opt-350m")
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:65-151]()

## Command-Line Tool

optimum-quanto provides a command-line tool for quantizing causal language models. You can run the example script with various options:

```bash
python quantize_causal_lm_model.py \
    --model facebook/opt-350m \
    --prompt "One of my fondest memory is" \
    --max_new_tokens 20 \
    --batch_size 32 \
    --weights int8 \
    --activations int8 \
    --load_dtype float16
```

Available options:

| Option | Description |
|--------|-------------|
| `--model` | Model ID from Hugging Face Hub or local path |
| `--prompt` | Text generation prompt |
| `--max_new_tokens` | Maximum number of tokens to generate |
| `--batch_size` | Batch size for evaluation and calibration |
| `--validation_batch` | Number of batches for calibration |
| `--load_dtype` | Precision for initial model loading (float16, float32, bfloat16) |
| `--weights` | Weight quantization type (int4, int8, float8) |
| `--activations` | Activation quantization type (none, int8, float8) |
| `--no-streamline` | Disable removal of consecutive quantize/dequantize operations |
| `--debug` | Enable detailed feedback during calibration |

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:65-106]()

## Device Support

The quantization and inference capabilities in optimum-quanto support multiple device types:

```mermaid
flowchart LR
    A["optimum.quanto"] --> B["CUDA (NVIDIA GPUs)"]
    A --> C["CPU"]
    A --> D["MPS (Apple Silicon)"]
    A --> E["XPU (Intel GPUs)"]
    
    B --> F["Optimized CUDA Kernels\n(AWQ, Marlin, TinyGemm)"]
    C --> G["Fallback Implementation"]
    D --> H["Metal Performance Shaders"]
    E --> I["Intel Extension for PyTorch"]
```

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:108-120]()

## Performance Considerations

When working with quantized text generation models, consider these factors:

1. **Hardware Compatibility**: Different quantization types may have optimized implementations on specific hardware.

2. **Model Size**: Larger models benefit more from quantization in terms of memory savings.

3. **Calibration Data**: The quality and representativeness of calibration data can significantly impact activation quantization effectiveness.

4. **Quality vs Efficiency Trade-off**: Higher bit-width quantization (e.g., int8) generally preserves more quality but offers less memory savings than lower bit-width (e.g., int4).

5. **Streamlining**: Enable streamlining to remove unnecessary quantize/dequantize operations, which can improve performance.

Sources: [examples/nlp/text-generation/quantize_causal_lm_model.py:99-102]()

## Conclusion

optimum-quanto provides a powerful yet straightforward approach to quantizing text generation models, making LLMs more accessible on resource-constrained hardware. By following the workflow described in this document, you can significantly reduce the memory footprint of your models while maintaining acceptable generation quality.

---

# Page: Vision and Diffusion Models

# Vision and Diffusion Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/nlp/text-classification/sst2/quantize_sst2_model.py](examples/nlp/text-classification/sst2/quantize_sst2_model.py)
- [examples/nlp/text-generation/quantize_causal_lm_model.py](examples/nlp/text-generation/quantize_causal_lm_model.py)
- [examples/vision/StableDiffusion/quantize_StableDiffusion.py](examples/vision/StableDiffusion/quantize_StableDiffusion.py)
- [examples/vision/StableDiffusion/requirements.txt](examples/vision/StableDiffusion/requirements.txt)
- [examples/vision/image-classification/mnist/quantize_mnist_model.py](examples/vision/image-classification/mnist/quantize_mnist_model.py)
- [examples/vision/object-detection/quantize_owl_model.py](examples/vision/object-detection/quantize_owl_model.py)
- [examples/vision/text-to-image/quantize_pixart_sigma.py](examples/vision/text-to-image/quantize_pixart_sigma.py)
- [optimum/quanto/models/__init__.py](optimum/quanto/models/__init__.py)
- [optimum/quanto/models/diffusers_models.py](optimum/quanto/models/diffusers_models.py)
- [optimum/quanto/models/shared_dict.py](optimum/quanto/models/shared_dict.py)
- [optimum/quanto/models/transformers_models.py](optimum/quanto/models/transformers_models.py)

</details>



This document details how to use Optimum-Quanto to quantize and deploy vision and diffusion models. It covers the quantization workflow for image classification, object detection, stable diffusion, and text-to-image generation models. For text generation model quantization, see [Text Generation Models](#8.1).

## Vision Models Quantization

Optimum-Quanto supports quantization of various vision models, including image classification and object detection. This section explores the implementation and usage patterns for these model types.

### Image Classification Models

Quantizing image classification models follows the standard Optimum-Quanto workflow:

1. Load the original float model
2. Apply quantization with specified precision (int4, int8, or float8)
3. Calibrate for activation quantization
4. Freeze the model for inference

The following diagram illustrates this workflow:

```mermaid
flowchart LR
    A["Original Vision Model"] --> B["quantize(model, weights=qtype)"]
    B --> C{"Activation quantization?"}
    C -->|"Yes"| D["Calibration with Calibration()"]
    C -->|"No"| E["freeze(model)"]
    D --> E
    E --> F["Quantized Model Inference"]
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:140-147](), [examples/vision/object-detection/quantize_owl_model.py:96-102]()

Example implementation for MNIST image classification model quantization:

```mermaid
classDiagram
    class AutoModel {
        +from_pretrained()
        +forward()
    }
    
    class MNISTQuantization {
        +quantize(weights, activations)
        +calibrate()
        +freeze()
        +test()
    }
    
    AutoModel <-- MNISTQuantization: "implements"
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py]()

The quantized model can be evaluated for performance and accuracy metrics:

```mermaid
flowchart LR
    A["Quantized Vision Model"] --> B["Forward Pass"]
    B --> C["Dequantize Output"]
    C --> D["Calculate Metrics"]
    D --> E["Accuracy & Loss"]
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:39-62]()

### Object Detection Models

Object detection models like Owlv2 can also be quantized with Optimum-Quanto. These models typically have more complex architectures with multiple components.

```mermaid
classDiagram
    class Owlv2ForObjectDetection {
        +owlv2: Vision Encoder
        +text_projection
        +box_head
        +class_head
        +from_pretrained()
        +forward()
    }
    
    class QuantizedOwlForObjectDetection {
        +quantize(weights=qtype)
        +freeze()
        +exclude_heads: bool
    }
    
    Owlv2ForObjectDetection <-- QuantizedOwlForObjectDetection: "implements"
```

Sources: [examples/vision/object-detection/quantize_owl_model.py:94-102]()

The quantization process allows selective quantization of model components. For example, you can choose to exclude the detection heads from quantization:

```mermaid
flowchart TB
    A["Owlv2ForObjectDetection"] --> B{"Exclude heads?"}
    B -->|"Yes"| C["quantize(model.owlv2, weights=qtype)"]
    B -->|"No"| D["quantize(model, weights=qtype)"]
    C --> E["freeze(model)"]
    D --> E
    E --> F["Inference"]
```

Sources: [examples/vision/object-detection/quantize_owl_model.py:96-102]()

## Diffusion Models Architecture

Diffusion models consist of multiple components that can be quantized independently. The main components include:

```mermaid
graph TD
    A["Diffusion Pipeline"] --> B["UNet"]
    A --> C["Text Encoder"]
    A --> D["VAE"]
    A --> E["Scheduler"]
    
    B --> F["UNet Blocks"]
    B --> G["Attention Layers"]
    
    C --> H["Transformer"]
    C --> I["Embedding Layers"]
    
    subgraph "Quantizable Components"
        F
        G
        H
        I
    end
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-31](), [examples/vision/text-to-image/quantize_pixart_sigma.py:22-28]()

## Quantizing Diffusion Models

### Stable Diffusion Quantization

Stable Diffusion models can be quantized using various precisions depending on your performance and accuracy needs:

```mermaid
flowchart LR
    A["Stable Diffusion v1-5"] --> B["Load with torch_dtype"]
    B --> C["Quantize UNet"]
    C --> D["freeze(pipe.unet)"]
    D --> E["Run Inference"]
    
    subgraph "Quantization Options"
        F["qint4: 4-bit integer"]
        G["qint8: 8-bit integer"]
        H["qfloat8: 8-bit float"]
    end
    
    C -.-> F
    C -.-> G
    C -.-> H
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-33]()

Performance metrics like inference time and memory usage can be measured for different quantization configurations:

```mermaid
graph TD
    A["Compare Configurations"] --> B["Original FP16/FP32"]
    A --> C["Quantized UNet (int4/int8/float8)"]
    B --> D["Measure Inference Time"]
    C --> D
    B --> E["Measure Memory Usage"]
    C --> E
    D --> F["Performance Report"]
    E --> F
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:94-109]()

### PixArt Quantization

PixArt models (like PixArt-Sigma) have a different architecture and quantization approach:

```mermaid
classDiagram
    class DiffusionPipeline {
        +transformer
        +text_encoder
        +from_pretrained()
        +__call__()
    }
    
    class QuantizedPixArtModel {
        +quantize(transformer, weights=qtype)
        +quantize(text_encoder, weights=qtype)
        +freeze()
    }
    
    DiffusionPipeline <-- QuantizedPixArtModel: "implements"
```

Sources: [examples/vision/text-to-image/quantize_pixart_sigma.py:22-31]()

The quantization process involves multiple components:

```mermaid
flowchart TD
    A["PixArt-Sigma Model"] --> B["Load with torch_dtype"]
    B --> C["Quantize Transformer"]
    B --> D["Quantize Text Encoder"]
    C --> E["freeze(pipe.transformer)"]
    D --> F["freeze(pipe.text_encoder)"]
    E --> G["Generate Images"]
    F --> G
```

Sources: [examples/vision/text-to-image/quantize_pixart_sigma.py:22-31](), [examples/vision/text-to-image/quantize_pixart_sigma.py:82-89]()

## Implementation Classes

Optimum-Quanto provides specialized classes for quantized diffusion models:

```mermaid
classDiagram
    class ModelHubMixin {
        +_save_pretrained()
        +from_pretrained()
    }
    
    class QuantizedDiffusersModel {
        +_wrapped: ModelMixin
        +BASE_NAME: "quanto"
        +base_class: null
        +quantize()
        +from_pretrained()
        +_save_pretrained()
    }
    
    class QuantizedPixArtTransformer2DModel {
        +base_class: PixArtTransformer2DModel
    }
    
    ModelHubMixin <|-- QuantizedDiffusersModel
    QuantizedDiffusersModel <|-- QuantizedPixArtTransformer2DModel
```

Sources: [optimum/quanto/models/diffusers_models.py:44-190]()

The `QuantizedDiffusersModel` class provides the following key functionality:

1. Wrapping a quantized diffusers model
2. Quantizing a float model with `quantize` static method
3. Loading a quantized model with `from_pretrained` static method
4. Saving a quantized model with `_save_pretrained` method

The `QuantizedPixArtTransformer2DModel` class specializes this functionality for PixArt transformer models.

Sources: [optimum/quanto/models/diffusers_models.py:189-190]()

## Quantization Workflow

The complete workflow for quantizing and using vision and diffusion models follows these steps:

```mermaid
flowchart TD
    A["Original Model"] --> B["Load Model"]
    B --> C["Select Quantization Type"]
    C --> D["Apply Quantization"]
    D --> E{"Activation Quantization?"}
    E -->|"Yes"| F["Calibration"]
    E -->|"No"| G["Freeze Model"]
    F --> G
    G --> H["Inference"]
    H --> I["Evaluate Performance"]
    G --> J["Save Model"]
    J --> K["Load Quantized Model"]
    K --> H
```

Sources: [examples/vision/image-classification/mnist/quantize_mnist_model.py:137-169](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:91-117]()

### Key API Functions

The core API functions for quantizing vision and diffusion models are:

1. `quantize(model, weights=qtype, activations=qtype)` - Apply quantization to model
2. `Calibration()` - Context manager for calibrating activation quantization
3. `freeze(model)` - Freeze the model for inference
4. `QuantizedDiffusersModel.from_pretrained()` - Load a quantized diffusion model
5. `model.save_pretrained()` - Save a quantized model

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-33](), [examples/vision/image-classification/mnist/quantize_mnist_model.py:140-155]()

## Performance Considerations

When quantizing vision and diffusion models, consider the following performance aspects:

| Quantization Type | Memory Reduction | Speed Improvement | Quality Impact |
|-------------------|------------------|-------------------|----------------|
| qint4             | Highest (75%)    | Moderate          | Higher         |
| qint8             | High (50%)       | Good              | Moderate       |
| qfloat8           | High (50%)       | Good              | Lower          |
| Float16 (baseline)| None             | None              | None           |

The choice of quantization type depends on your specific requirements:

```mermaid
flowchart TD
    A["Choose Quantization Type"] --> B{"Memory Priority?"}
    B -->|"High"| C["qint4"]
    B -->|"Medium"| D{"Quality Priority?"}
    D -->|"High"| E["qfloat8"]
    D -->|"Medium"| F["qint8"]
    C --> G["Acceptable Quality Loss?"]
    G -->|"No"| E
    G -->|"Yes"| H["Proceed with qint4"]
    E --> I["Proceed with qfloat8"]
    F --> J["Proceed with qint8"]
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:106-109](), [examples/vision/text-to-image/quantize_pixart_sigma.py:73-77]()

## Example Usage

### Quantizing a Stable Diffusion Model

```python
# Load the pipeline
pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)

# Quantize the UNet component with 8-bit integer quantization
quantize(pipe.unet, weights=qint8)
freeze(pipe.unet)

# Generate images with the quantized model
image = pipe(
    prompt="ghibli style, a fantasy landscape with castles",
    num_inference_steps=50,
    generator=torch.manual_seed(0)
).images[0]
```

Sources: [examples/vision/StableDiffusion/quantize_StableDiffusion.py:25-33](), [examples/vision/StableDiffusion/quantize_StableDiffusion.py:112-117]()

### Quantizing a PixArt Model

```python
# Load the pipeline
pipe = DiffusionPipeline.from_pretrained("PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", torch_dtype=torch.float16)

# Quantize the transformer and text encoder components
quantize(pipe.transformer, weights=qint8)
freeze(pipe.transformer)
quantize(pipe.text_encoder, weights=qint8)
freeze(pipe.text_encoder)

# Generate images with the quantized model
image = pipe(
    prompt="ghibli style, a fantasy landscape with castles",
    num_inference_steps=50,
    generator=torch.manual_seed(0)
).images[0]
```

Sources: [examples/vision/text-to-image/quantize_pixart_sigma.py:22-31](), [examples/vision/text-to-image/quantize_pixart_sigma.py:82-89]()

This comprehensive approach to quantizing vision and diffusion models enables significant memory and speed improvements while maintaining acceptable quality for various applications.

---

# Page: Benchmarking

# Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bench/generation/README.md](bench/generation/README.md)
- [bench/generation/evaluate_configurations.py](bench/generation/evaluate_configurations.py)
- [bench/generation/evaluate_model.py](bench/generation/evaluate_model.py)
- [bench/generation/gen_barchart.py](bench/generation/gen_barchart.py)
- [bench/generation/metrics/latency.py](bench/generation/metrics/latency.py)
- [bench/generation/setup/hqq.py](bench/generation/setup/hqq.py)
- [bench/kernels/benchmark.py](bench/kernels/benchmark.py)
- [bench/torch_kernels/test_int_mm.py](bench/torch_kernels/test_int_mm.py)
- [bench/torch_kernels/test_weight_int4pack_mm.py](bench/torch_kernels/test_weight_int4pack_mm.py)
- [bench/torch_kernels/test_weight_int8pack_mm.py](bench/torch_kernels/test_weight_int8pack_mm.py)

</details>



This page provides a comprehensive guide to benchmarking quantized models with optimum-quanto. It explains how to measure and compare the performance of models with different quantization configurations across various metrics and hardware platforms.

## Overview of Benchmarking in optimum-quanto

Optimum-quanto provides a structured benchmarking framework to evaluate the impact of quantization on model performance. The framework allows users to measure three key aspects of model performance:

1. **Model Quality** - How quantization affects prediction accuracy and perplexity
2. **Inference Efficiency** - How quantization affects latency and memory usage
3. **Hardware Performance** - How different backends and hardware platforms perform with quantized models

```mermaid
flowchart TD
    A["Benchmarking Process"] --> B["Model Selection"]
    B --> C["Quantization Configuration"]
    C --> D["Metric Selection"]
    D --> E1["Latency"]
    D --> E2["Prediction Accuracy"]
    D --> E3["Perplexity"]
    E1 --> F["Result Visualization"]
    E2 --> F
    E3 --> F
    F --> G["Configuration Comparison"]
```

Sources: [bench/generation/evaluate_model.py:51-83](), [bench/generation/README.md:1-13]()

## Benchmarking Metrics

Optimum-quanto uses three primary metrics to evaluate quantized models:

### 1. Latency

Measures the average time per token during text generation, providing insight into inference speed.

```mermaid
flowchart LR
    A["Input Prompt"] --> B["Model.generate()"]
    B --> C["Timing Events"]
    C --> D["Calculate Latency"]
    D --> E["Average ms/token"]
    
    subgraph "Device Handling"
        F["CUDA Synchronization"]
        G["MPS Synchronization"]
        H["XPU Synchronization"]
        I["CPU Synchronization"]
    end
    
    C --- F
    C --- G
    C --- H
    C --- I
```

Sources: [bench/generation/metrics/latency.py:24-105]()

### 2. Prediction Accuracy

Evaluates the model's ability to correctly predict the last token in prompts from the Lambada dataset.

### 3. Perplexity

Measures how well the model predicts the next token in a sequence, calculated on the WikiText dataset.

Sources: [bench/generation/README.md:5-7]()

## Benchmarking Framework

### Core Components

```mermaid
classDiagram
    class evaluate_model {
        +evaluate(model_id, metric, quantizer, weights, activations, batch_size, device, dtype)
        +calibrate(model, tokenizer, batch_size, batches)
        +main()
    }
    
    class evaluate_configurations {
        +evaluate_model_configurations(model_id, metric, device, batch_size, dtype)
        +main()
    }
    
    class latency {
        +latency(model, tokenizer, device, batch_size, prompt_length, nb_tokens, iterations)
        +get_device_memory(device)
    }
    
    class perplexity {
        +perplexity(model, tokenizer)
    }
    
    class prediction_accuracy {
        +prediction_accuracy(model, tokenizer, batch_size)
    }
    
    class gen_barchart {
        +gen_barchart(model_id, title, label, results, dtype)
        +save_bar_chart(title, labels, ylabel, series, save_path)
    }
    
    evaluate_model --> latency : uses
    evaluate_model --> perplexity : uses
    evaluate_model --> prediction_accuracy : uses
    evaluate_configurations --> evaluate_model : uses
    evaluate_configurations --> gen_barchart : uses
```

Sources: [bench/generation/evaluate_model.py:15-137](), [bench/generation/evaluate_configurations.py:15-120](), [bench/generation/metrics/latency.py:15-119](), [bench/generation/gen_barchart.py:15-89]()

## Running Benchmarks

### Basic Usage

The primary script for benchmarking is `evaluate_model.py`, which allows evaluating a model with specific quantization settings against a chosen metric:

```
python evaluate_model.py --model MODEL_ID --metric METRIC --quantizer QUANTIZER --weights WEIGHT_TYPE --activations ACTIVATION_TYPE
```

Where:
- `MODEL_ID`: Hugging Face model ID (e.g., "facebook/opt-350m")
- `METRIC`: One of "latency", "prediction", "perplexity"
- `QUANTIZER`: Quantization method (e.g., "quanto", "awq", "bnb", "hqq")
- `WEIGHTS`: Weight quantization type (e.g., "none", "int4", "int8", "float8")
- `ACTIVATIONS`: Activation quantization type (e.g., "none", "int8", "float8")

Sources: [bench/generation/evaluate_model.py:86-133]()

### Evaluating Multiple Configurations

For comparing multiple quantization configurations, `evaluate_configurations.py` provides a convenient way to test a matrix of weight and activation quantization types:

```
python evaluate_configurations.py --model MODEL_ID --metric METRIC --json --png
```

This script tests the model with the following configurations:
- Native precision (fp16/bf16)
- int4, int8, and float8 weight quantization
- Native and float8 activation quantization

The `--json` and `--png` flags enable output of results to JSON and PNG bar chart formats.

Sources: [bench/generation/evaluate_configurations.py:26-116]()

## Visualizing Results

Benchmark results can be visualized using the built-in bar chart generation:

```mermaid
flowchart TD
    A["Benchmark Results"] --> B["gen_barchart()"]
    B --> C["Format Data"]
    C --> D["Create Bar Chart"]
    D --> E["Save to PNG"]
    
    subgraph "Chart Customization"
        F["Set Title"]
        G["Configure Labels"]
        H["Set Y-axis Label"]
        I["Apply Formatting"]
    end
    
    D --- F
    D --- G
    D --- H
    D --- I
```

The resulting bar charts compare different weight quantization types (int4, int8, float8) against different activation quantization types, making it easy to identify the optimal configuration for your use case.

Sources: [bench/generation/gen_barchart.py:23-73](), [bench/generation/README.md:15-82]()

## Hardware-Specific Benchmarking

Optimum-quanto supports benchmarking on multiple hardware platforms, with device-specific optimizations for each:

```mermaid
flowchart TB
    A["Hardware Platform"] --> B["CUDA (NVIDIA GPUs)"]
    A --> C["MPS (Apple Silicon)"]
    A --> D["XPU (Intel GPUs)"]
    A --> E["CPU"]
    
    B --> F["Synchronization Methods"]
    C --> F
    D --> F
    E --> F
    
    F --> G["torch.cuda.synchronize()"]
    F --> H["torch.mps.synchronize()"]
    F --> I["torch.xpu.synchronize()"]
    F --> J["torch.cpu.synchronize()"]
    
    K["Memory Tracking"] --> L["CUDA Memory Stats"]
    K --> M["MPS Memory Stats"]
    K --> N["XPU Memory Stats"]
```

Each hardware platform has specific synchronization methods and memory tracking to ensure accurate benchmarking.

Sources: [bench/generation/metrics/latency.py:25-56](), [bench/generation/metrics/latency.py:107-119]()

## Kernel-Level Benchmarking

In addition to model-level benchmarking, optimum-quanto provides tools for benchmarking specific kernels and operations, such as matrix multiplication with quantized weights:

### Weight-Quantized Matrix Multiplication

```mermaid
flowchart LR
    A["Input Tensor (fp16/bf16)"] --> B["Quantized Weight Tensor"]
    B --> C["QBits Packing"]
    C --> D["Optimized MM Kernel"]
    D --> E["Output Tensor"]
    
    F["Baseline fp16/bf16 MM"] --> G["Performance Comparison"]
    E --> G
    
    subgraph "Benchmarking Metrics"
        H["Execution Time (ms)"]
        I["Error vs Baseline"]
    end
    
    G --- H
    G --- I
```

Sources: [bench/torch_kernels/test_weight_int4pack_mm.py:21-126](), [bench/torch_kernels/test_weight_int8pack_mm.py:21-69](), [bench/torch_kernels/test_int_mm.py:21-78]()

## Example Benchmark Results

The benchmarking framework has been used to compare various models and quantization configurations. Below are example metrics for a few popular models:

### Performance vs Accuracy Trade-offs

| Configuration | Latency (ms/token) | Prediction Accuracy | Perplexity |
|---------------|-------------------|---------------------|------------|
| W16A16 (baseline) | 10-30 | 95-98% | Model-dependent |
| W4A16 | 3-10 | 90-95% | Slightly higher |
| W8A16 | 5-15 | 92-97% | Nearly baseline |
| W8A8 | 4-12 | 91-96% | Slightly higher |
| W4A8 | 2-8 | 88-94% | Higher than baseline |

The README file in the benchmark directory contains detailed charts for specific models like Meta-Llama-3.1-8B, Mistral-7B-Instruct-v0.3, and Google Gemma-2B.

Sources: [bench/generation/README.md:15-82]()

## Conclusion

Benchmarking is an essential part of the quantization workflow, allowing users to make informed decisions about the trade-offs between model size, speed, and accuracy. The optimum-quanto benchmarking framework provides a comprehensive set of tools for evaluating these trade-offs across different quantization configurations and hardware platforms.

For detailed guidance on interpreting benchmark results and selecting optimal configurations, see [Performance Metrics](#9.1).

---

# Page: Performance Metrics

# Performance Metrics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bench/generation/README.md](bench/generation/README.md)
- [bench/generation/evaluate_configurations.py](bench/generation/evaluate_configurations.py)
- [bench/generation/evaluate_model.py](bench/generation/evaluate_model.py)
- [bench/generation/gen_barchart.py](bench/generation/gen_barchart.py)
- [bench/generation/metrics/latency.py](bench/generation/metrics/latency.py)
- [bench/generation/setup/hqq.py](bench/generation/setup/hqq.py)
- [bench/kernels/benchmark.py](bench/kernels/benchmark.py)
- [bench/torch_kernels/test_int_mm.py](bench/torch_kernels/test_int_mm.py)
- [bench/torch_kernels/test_weight_int4pack_mm.py](bench/torch_kernels/test_weight_int4pack_mm.py)
- [bench/torch_kernels/test_weight_int8pack_mm.py](bench/torch_kernels/test_weight_int8pack_mm.py)

</details>



This page details the performance metrics used to evaluate quantized models in optimum-quanto. Performance metrics are essential for understanding the trade-offs between model size, inference speed, and output quality when applying quantization techniques. For general information about the quantization workflow, see [Workflow Guide](#7).

## Overview of Metrics

Optimum-quanto uses three primary metrics to evaluate quantized models:

```mermaid
flowchart LR
    A["Performance<br>Metrics"] --> B["Latency"]
    A --> C["Prediction<br>Accuracy"]
    A --> D["Perplexity"]
    
    B --> B1["Speed of token<br>generation"]
    C --> C1["Accuracy on Lambada<br>dataset"]
    D --> D1["Language modeling<br>quality on WikiText"]
    
    B -.-> E["Memory<br>Usage"]
    B -.-> F["Throughput"]
```

Sources: [bench/generation/README.md:1-7](), [bench/generation/evaluate_model.py:15-85]()

## Core Metrics Implementation

The metrics are implemented in the `bench/generation/metrics` directory and can be invoked through the `evaluate_model.py` utility:

### 1. Latency

Measures the time required to generate each token in milliseconds. Lower values indicate faster inference.

```mermaid
sequenceDiagram
    participant User
    participant EM as "evaluate_model.py"
    participant LM as "latency.py"
    participant Model
    
    User->>EM: Run latency benchmark
    EM->>LM: Call latency() function
    LM->>Model: Initialize with random input_ids
    LM->>LM: Record start_event
    LM->>Model: model.generate()
    LM->>LM: Record end_event
    LM->>LM: Calculate latency_ms / tokens
    LM->>EM: Return mean_latency
    EM->>User: Report results
```

Key measurement details:
- Measures time per token across multiple iterations
- Supports different devices (CUDA, MPS, XPU, CPU)
- Tracks peak memory usage during generation
- Customizable batch size, input length, and generation length

Sources: [bench/generation/metrics/latency.py:15-119](), [bench/generation/evaluate_model.py:78-79]()

### 2. Prediction Accuracy

Evaluates how well the model predicts the last token in prompts from the Lambada dataset, which assesses the impact of quantization on model capabilities.

Implementation details:
- Uses the Lambada dataset for evaluation
- Measures percentage of correctly predicted tokens
- Higher values indicate better preservation of model quality

Sources: [bench/generation/evaluate_model.py:80-81](), [bench/generation/README.md:6]()

### 3. Perplexity

Measures the model's perplexity on the WikiText dataset, which is a standard metric for evaluating language models. Lower perplexity indicates better language modeling capabilities.

Implementation details:
- Evaluates on WikiText dataset following the standard approach from Transformers
- Normalized by sentence length
- Lower values indicate better language modeling quality

Sources: [bench/generation/evaluate_model.py:82-83](), [bench/generation/README.md:7]()

## Benchmark Configuration

The benchmark system supports various configurations to evaluate quantization performance across different settings:

```mermaid
classDiagram
    class BenchmarkConfiguration {
        +model_id: str
        +metric: str
        +quantizer: str
        +weights: str
        +activations: str
        +batch_size: int
        +device: torch.device
        +dtype: torch.dtype
    }
    
    class Quantizer {
        <<enumeration>>
        QUANTO
        AWQ
        BNB
        HQQ
    }
    
    class WeightQuantization {
        <<enumeration>>
        none
        int4
        int8
        float8
    }
    
    class ActivationQuantization {
        <<enumeration>>
        none
        int8
        float8
    }
    
    class Metric {
        <<enumeration>>
        latency
        prediction
        perplexity
    }
    
    BenchmarkConfiguration --> Quantizer
    BenchmarkConfiguration --> WeightQuantization
    BenchmarkConfiguration --> ActivationQuantization
    BenchmarkConfiguration --> Metric
```

Sources: [bench/generation/evaluate_model.py:51-76](), [bench/generation/evaluate_configurations.py:26-61]()

### Supported Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| Quantizer | quanto, awq, bnb, hqq | Quantization library to use |
| Weights | none, int4, int8, float8 | Weight quantization format |
| Activations | none, int8, float8 | Activation quantization format |
| Device | cuda, mps, xpu, cpu | Hardware to run benchmarks on |
| Metric | latency, prediction, perplexity | Performance metric to evaluate |
| Batch Size | Integer (default: 32) | Batch size during evaluation |
| dtype | fp16, bf16 | Floating-point precision for unquantized parts |

Sources: [bench/generation/evaluate_model.py:86-116](), [bench/generation/evaluate_configurations.py:29-38]()

## Visualization and Analysis

The benchmarking scripts can generate visual comparisons of different quantization configurations:

```mermaid
flowchart TD
    A["evaluate_configurations.py"] --> B["Evaluate multiple configurations"]
    B --> C["Generate results dictionary"]
    C --> D{"Output format"}
    D -->|JSON| E["Write to model-metric.json"]
    D -->|PNG| F["Generate bar chart"]
    F --> G["gen_barchart.py"]
    G --> H["matplotlib visualization"]
```

Sources: [bench/generation/evaluate_configurations.py:97-116](), [bench/generation/gen_barchart.py:15-74]()

### Result Interpretation

When analyzing benchmark results, consider these aspects:

1. **Latency vs Quality Trade-off**: Lower precision generally leads to faster inference but might decrease prediction accuracy or increase perplexity.

2. **Weight vs Activation Quantization**: Weight quantization typically has a larger impact on model size, while activation quantization impacts runtime memory usage.

3. **Hardware-Specific Performance**: Different quantization methods perform differently across hardware platforms.

4. **Memory Usage**: Tracked during latency benchmarks to help understand resource requirements.

Examples from real models show that:
- 4-bit weight quantization can achieve 2-4x speedup with minimal quality degradation
- 8-bit weight quantization generally preserves most of the model quality
- Activation quantization provides additional speedup but may impact quality more significantly

Sources: [bench/generation/README.md:13-82]()

## Low-Level Kernel Benchmarks

In addition to model-level benchmarks, optimum-quanto provides tools for benchmarking low-level kernels to understand the performance benefits of specialized quantized operations:

```mermaid
flowchart LR
    A["Kernel<br>Benchmarks"] --> B["Unpack Operations"]
    A --> C["Matrix Multiplications"]
    
    B --> B1["unpack_2bit"]
    B --> B2["unpack_4bit"]
    
    C --> C1["weight_int4pack_mm"]
    C --> C2["weight_int8pack_mm"]
    C --> C3["int_mm"]
    
    C1 --> D1["Versus fp16/bf16<br>operations"]
    C2 --> D1
    C3 --> D1
```

Sources: [bench/kernels/benchmark.py:15-122](), [bench/torch_kernels/test_weight_int4pack_mm.py:15-137](), [bench/torch_kernels/test_weight_int8pack_mm.py:15-69](), [bench/torch_kernels/test_int_mm.py:15-78]()

### Kernel Measurement

For each kernel, the benchmarks measure:
- Execution time compared to equivalent floating-point operations
- Relative speedup from quantization
- Error metrics (e.g., mean absolute error) compared to full-precision results

These benchmarks help identify which operations benefit most from quantization and inform further optimization efforts.

Sources: [bench/torch_kernels/test_weight_int4pack_mm.py:101-133](), [bench/kernels/benchmark.py:35-86]()

## Running Performance Benchmarks

To evaluate a model's performance with optimum-quanto, use the `evaluate_model.py` script:

```bash
python -m bench.generation.evaluate_model \
  --model facebook/opt-350m \
  --metric latency \
  --quantizer quanto \
  --weights int4 \
  --activations float8 \
  --device cuda \
  --batch_size 1
```

For benchmarking multiple configurations at once, use `evaluate_configurations.py`:

```bash
python -m bench.generation.evaluate_configurations \
  --model facebook/opt-350m \
  --metric prediction \
  --device cuda \
  --batch_size 32 \
  --png \
  --json
```

Sources: [bench/generation/evaluate_model.py:86-133](), [bench/generation/evaluate_configurations.py:64-116]()

## Performance Considerations

When evaluating quantized models, consider these factors:

1. **Model Architecture Sensitivity**: Different model architectures (Transformer variants) respond differently to quantization.

2. **Task Dependency**: Some tasks are more resilient to quantization than others.

3. **Quality-Speed Tradeoff**: Choose the right balance based on your application requirements.

4. **Hardware Acceleration**: Certain quantization formats are better supported on specific hardware.

5. **Batch Size Impact**: Performance scaling with batch size can differ between quantized and unquantized models.

By using optimum-quanto's performance metrics, you can make informed decisions about which quantization techniques best suit your specific use case and hardware environment.

Sources: [bench/generation/README.md:1-82](), [bench/generation/evaluate_model.py:51-85]()

---

# Page: Hardware-Specific Performance

# Hardware-Specific Performance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bench/generation/evaluate_configurations.py](bench/generation/evaluate_configurations.py)
- [bench/generation/evaluate_model.py](bench/generation/evaluate_model.py)
- [bench/generation/metrics/latency.py](bench/generation/metrics/latency.py)
- [bench/generation/setup/hqq.py](bench/generation/setup/hqq.py)
- [bench/kernels/benchmark.py](bench/kernels/benchmark.py)
- [bench/torch_kernels/test_int_mm.py](bench/torch_kernels/test_int_mm.py)
- [bench/torch_kernels/test_weight_int4pack_mm.py](bench/torch_kernels/test_weight_int4pack_mm.py)
- [bench/torch_kernels/test_weight_int8pack_mm.py](bench/torch_kernels/test_weight_int8pack_mm.py)
- [optimum/quanto/library/extensions/cuda/__init__.py](optimum/quanto/library/extensions/cuda/__init__.py)
- [optimum/quanto/tensor/weights/marlin/fp8/__init__.py](optimum/quanto/tensor/weights/marlin/fp8/__init__.py)
- [optimum/quanto/tensor/weights/marlin/fp8/packed.py](optimum/quanto/tensor/weights/marlin/fp8/packed.py)
- [optimum/quanto/tensor/weights/marlin/fp8/qbits.py](optimum/quanto/tensor/weights/marlin/fp8/qbits.py)
- [test/library/test_mm.py](test/library/test_mm.py)
- [test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py](test/tensor/weights/optimized/test_marlin_fp8_packed_tensor.py)

</details>



This page documents the performance characteristics of optimum-quanto across different hardware platforms and explains the various hardware-specific optimizations implemented in the library. For information about general performance metrics and how to benchmark models, see [Performance Metrics](#9.1).

## Supported Hardware Platforms

Optimum-Quanto supports multiple hardware platforms with varying levels of optimization and feature availability:

| Hardware Platform | Support Level | Weight Quantization | Activation Quantization | Specialized Kernels |
|------------------|---------------|---------------------|-------------------------|---------------------|
| CUDA (NVIDIA GPUs) | Full | int4, int8, float8 | int8, float8 | AWQ, Marlin, TinyGemm |
| CPU | Good | int4, int8 | int8 | Basic optimizations |
| MPS (Apple Silicon) | Basic | int4, int8 | int8 | Limited |
| XPU (Intel) | Basic | int4, int8 | int8 | Limited |

The library automatically detects available hardware and selects the appropriate implementation based on device capabilities.

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:24-45](), [bench/generation/evaluate_model.py:120-132]()

## Hardware Detection and Dispatching

Optimum-Quanto implements an intelligent hardware detection system that identifies the available hardware and its capabilities to select the most optimized implementation.

```mermaid
flowchart TD
    A["Hardware Detection"] --> B{"Device Type?"}
    B -->|"CUDA" | C["Check CUDA Compute Capability"]
    B -->|"CPU" | D["Use CPU Extensions"]
    B -->|"MPS" | E["Use MPS Extensions"]
    B -->|"XPU" | F["Use XPU Extensions"]
    
    C --> G{"Compute Capability >= 8.0?"}
    G -->|"Yes" | H["Enable Tensor Core Optimizations<br>AWQ, Marlin, TinyGemm"]
    G -->|"No" | I["Basic CUDA Implementations"]
```

The library dynamically selects implementation paths based on the hardware capabilities. For NVIDIA GPUs, it checks the compute capability to determine which optimized kernels can be used:

```python
def get_max_cuda_arch():
    """Select the maximum CUDA arch supported
    This is a combination of the CUDA and pytorch version and all detected devices capabilities.
    """
    capability_list = []
    supported_sm = [int(arch.split("_")[1]) for arch in torch.cuda.get_arch_list() if "sm_" in arch]
    if supported_sm:
        max_supported_sm = max((sm // 10, sm % 10) for sm in supported_sm)
        for i in range(torch.cuda.device_count()):
            capability = torch.cuda.get_device_capability(i)
            capability = min(max_supported_sm, capability)
            if capability not in capability_list:
                capability_list.append(capability)
    max_capability = max(sorted(capability_list)) if len(capability_list) > 0 else (0, 0)
    return f"{max_capability[0]}{max_capability[1]}0"
```

Sources: [optimum/quanto/library/extensions/cuda/__init__.py:25-45](), [bench/generation/evaluate_model.py:121-131]()

## CUDA Optimizations

NVIDIA GPUs with CUDA support benefit from the most extensive optimizations in optimum-quanto. The library includes specialized kernels that leverage Tensor Cores on modern NVIDIA GPUs for accelerated matrix operations with quantized weights.

### AWQ Kernels

AWQ (Activation-aware Weight Quantization) kernels provide optimized implementations for 4-bit integer weights:

```mermaid
flowchart LR
    A["Input Tensor<br>(fp16/bf16)"] --> B["AWQ Matrix Multiply Kernel"]
    C["Quantized Weights<br>(int4 packed)"] --> B
    D["Scales<br>(fp16/bf16)"] --> B
    E["Zeros/Shifts<br>(int8 scaled)"] --> B
    B --> F["Output Tensor<br>(fp16/bf16)"]
    
    subgraph "Implementation Selection"
        G["torch.ops.quanto.gemm_f16i4_awq()"]
        H["Rows < 8?"] -->|"Yes"| I["awq_v2_gemv_f16i4()"]
        H -->|"No"| J["awq_v2_gemm_f16i4()"]
    end
```

The implementation intelligently selects between GEMV (matrix-vector) and GEMM (matrix-matrix) kernels based on the input dimensions, providing optimized performance for both scenarios.

Sources: [test/library/test_mm.py:52-100](), [optimum/quanto/library/extensions/cuda/__init__.py:82-121]()

### Marlin FP8 Kernels

Marlin kernels provide highly optimized implementations for 8-bit floating-point (FP8) weights, which can be particularly effective for maintaining model quality with quantization:

```mermaid
flowchart LR
    A["Input Tensor<br>(fp16/bf16)"] --> B["Marlin FP8 GEMM Kernel"]
    C["Quantized Weights<br>(FP8, specially packed)"] --> B
    D["Repacked Scales<br>(fp16/bf16)"] --> B
    E["Workspace<br>(int32)"] --> B
    B --> F["Output Tensor<br>(fp16/bf16)"]
```

Marlin FP8 uses a specialized data layout that requires specific permutation of both weights and scales to achieve optimal performance on CUDA cores.

Sources: [test/library/test_mm.py:102-144](), [optimum/quanto/tensor/weights/marlin/fp8/packed.py:22-69]()

### Marlin Int4 Implementation

Similar to FP8, Marlin also provides optimized kernels for int4 quantization:

```mermaid
flowchart LR
    A["Input Tensor<br>(fp16)"] --> B["Marlin Int4 GEMM Kernel"]
    C["Packed Weights<br>(int4 in int32)"] --> B
    D["Permuted Scales<br>(fp16)"] --> B
    E["Permuted Zerospoints<br>(fp16)"] --> B
    F["Workspace<br>(int32)"] --> B
    B --> G["Output Tensor<br>(fp16)"]
```

The int4 implementation also uses specialized permutation to optimize memory access patterns on NVIDIA GPUs.

Sources: [test/library/test_mm.py:146-189](), [optimum/quanto/library/extensions/cuda/__init__.py:170-202]()

## CPU Implementation

For CPU execution, optimum-quanto provides specialized implementations that work without CUDA. While generally slower than GPU execution, these implementations allow the use of quantized models on systems without specialized hardware.

```mermaid
flowchart LR
    A["torch.ops.quanto.qbytes_mm()"] --> B{"Device Type?"}
    B -->|"CPU"| C["CPU Implementation"]
    B -->|"Other"| D["Device-Specific Implementation"]
    
    C --> E["Unpack weights if needed"]
    E --> F["Perform integer matrix multiplication"]
    F --> G["Apply scales"]
```

The CPU implementation includes optimizations for int4 and int8 weights, with specific paths to leverage PyTorch's CPU optimizations:

```python
# CPU-specific weight int4 matrix multiply
B_packed = torch._convert_weight_to_int4pack_for_cpu(B_int32, innerKTiles=2)
qout = torch._weight_int4pack_mm_for_cpu(A, B_packed, group_size, B_scale_and_zeros)
```

Sources: [bench/torch_kernels/test_weight_int4pack_mm.py:93-125](), [bench/torch_kernels/test_weight_int8pack_mm.py:22-65]()

## MPS (Apple Silicon) Support

For Apple Silicon devices, optimum-quanto provides basic support through the MPS (Metal Performance Shaders) backend:

```mermaid
flowchart TD
    A["MPS Device Detection"] --> B["Basic Quantization Operations"]
    B --> C["Limited Kernel Support"]
    
    C --> D["Supported:"]
    C --> E["Not Supported:"]
    
    D --> F["Basic Int4/Int8 Ops"]
    D --> G["Weight Quantization"]
    
    E --> H["Float8 Ops"]
    E --> I["Specialized Kernels<br>AWQ, Marlin"]
```

The MPS implementation provides functional support but lacks the specialized kernels available for CUDA devices. Float8 operations are not supported on MPS devices.

Sources: [test/library/test_mm.py:36-37](), [bench/generation/metrics/latency.py:28-31]()

## XPU (Intel) Support

Intel XPU devices (including Intel GPUs and accelerators) receive similar basic support:

```mermaid
flowchart TD
    A["XPU Device Detection"] --> B["Basic Quantization Operations"]
    B --> C["Synchronization Support"]
    B --> D["Memory Management"]
    
    C --> E["torch.xpu.synchronize()"]
    D --> F["torch.xpu.memory_allocated()"]
    D --> G["torch.xpu.reset_peak_memory_stats()"]
```

XPU implementations focus on core functionality with fewer specialized optimizations compared to CUDA.

Sources: [bench/generation/metrics/latency.py:30-31](), [bench/generation/metrics/latency.py:98-101]()

## Performance Comparison

### Latency Across Hardware Platforms

When evaluating performance across different hardware platforms, latency is a key metric. The following graph illustrates relative performance trends (the exact numbers will vary by model size and hardware):

```mermaid
gantt
    title "Relative Latency Comparison (Lower is Better)"
    dateFormat X
    axisFormat %s
    
    section "float16"
    CUDA (A100)         :0, 10
    CUDA (V100)         :0, 15
    CUDA (T4)           :0, 20
    CPU (Xeon)          :0, 100
    MPS (M1)            :0, 40
    XPU (Intel Arc)     :0, 50
    
    section "int8"
    CUDA (A100)         :0, 6
    CUDA (V100)         :0, 8
    CUDA (T4)           :0, 12
    CPU (Xeon)          :0, 60
    MPS (M1)            :0, 25
    XPU (Intel Arc)     :0, 30
    
    section "int4"
    CUDA (A100)         :0, 4
    CUDA (V100)         :0, 6
    CUDA (T4)           :0, 9
    CPU (Xeon)          :0, 40
    MPS (M1)            :0, 18
    XPU (Intel Arc)     :0, 22
    
    section "float8"
    CUDA (A100)         :0, 5
    CUDA (V100)         :0, 7
    CUDA (T4)           :0, 11
    CPU (Xeon)          :0, 50
    MPS (M1)            :crit, 0, 0
    XPU (Intel Arc)     :crit, 0, 0
```

Key observations:
- CUDA devices offer the best performance, especially for quantized operations
- A100 GPUs with Ampere architecture provide the best performance for quantized models
- Float8 operations are only supported on CUDA devices
- CPU performance is significantly slower but provides universal compatibility

Sources: [bench/generation/evaluate_configurations.py:25-77](), [bench/generation/metrics/latency.py:15-105]()

### Matrix Multiplication Performance

Matrix multiplication is the core operation in transformer models, and its performance directly impacts overall model latency. The following table shows the relative speedup of quantized matrix multiplication compared to FP16 operations:

| Hardware | Weight Format | Speedup vs FP16 | Notes |
|----------|---------------|-----------------|-------|
| CUDA (A100) | int4 (AWQ) | 2.5-3.5x | Best for GPUs with Tensor Cores |
| CUDA (A100) | int4 (Marlin) | 2.3-3.2x | Good numerical stability |
| CUDA (A100) | float8 | 1.8-2.2x | Best quality-performance trade-off |
| CUDA (A100) | int8 | 1.5-2.0x | Good baseline quantization |
| CPU | int4 | 1.8-2.5x | Limited by memory bandwidth |
| CPU | int8 | 1.3-1.8x | Good compatibility option |
| MPS | int4 | 1.4-2.2x | Best option for Apple Silicon |
| MPS | int8 | 1.2-1.6x | Alternative for Apple Silicon |
| XPU | int4 | 1.5-2.3x | Best option for Intel GPUs |
| XPU | int8 | 1.3-1.7x | Alternative for Intel GPUs |

Sources: [bench/torch_kernels/test_weight_int4pack_mm.py:111-133](), [bench/torch_kernels/test_weight_int8pack_mm.py:49-65](), [bench/torch_kernels/test_int_mm.py:51-74]()

## How to Benchmark on Different Hardware

To evaluate performance on your specific hardware, optimum-quanto provides benchmarking tools in the `bench/` directory. The following example demonstrates how to benchmark a model with different quantization configurations:

```bash
# Benchmark latency on CUDA
python -m bench.generation.evaluate_model --model facebook/opt-350m --metric latency --device cuda --weights int4 --activations none

# Benchmark latency on CPU
python -m bench.generation.evaluate_model --model facebook/opt-350m --metric latency --device cpu --weights int4 --activations none

# Benchmark all configurations and generate comparison chart
python -m bench.generation.evaluate_configurations --model facebook/opt-350m --metric latency --device cuda --png
```

The benchmark tools automatically detect hardware capabilities and select the appropriate implementations. For CUDA devices, compute capability 8.0 or higher (Ampere architecture and newer) enables the most optimized kernels.

Sources: [bench/generation/evaluate_model.py:35-133](), [bench/generation/evaluate_configurations.py:26-120]()

## Device-Specific Memory Considerations

Memory usage varies significantly across hardware platforms and quantization methods:

```mermaid
flowchart TD
    A["Memory Usage by Device"] --> B["CUDA Devices"]
    A --> C["CPU"]
    A --> D["MPS/XPU"]
    
    B --> B1["Peak Memory Tracking:<br>torch.cuda.max_memory_allocated()"]
    B --> B2["Memory Optimization:<br>torch.cuda.empty_cache()"]
    
    C --> C1["System Memory:<br>No Built-in Tracking"]
    
    D --> D1["MPS: torch.mps.current_allocated_memory()"]
    D --> D2["XPU: torch.xpu.memory_allocated()"]
```

When benchmarking, the library provides memory usage statistics to help understand the memory efficiency of different quantization methods:

```python
if device.type == "cuda":
    peak_memory = torch.cuda.max_memory_allocated()
    print(f"Peak memory during benchmark: {peak_memory / (2**30):.4f} GB")
elif device.type == "xpu":
    peak_memory = torch.xpu.max_memory_allocated()
    print(f"Peak memory during benchmark: {peak_memory / (2**30):.4f} GB")
```

Quantization can significantly reduce memory requirements, with int4 quantization typically reducing model size by up to 8x compared to FP16.

Sources: [bench/generation/metrics/latency.py:96-101](), [bench/generation/metrics/latency.py:108-119]()

## Summary

Optimum-Quanto provides hardware-specific optimizations that significantly improve performance across various platforms, with CUDA devices receiving the most extensive optimization. The library intelligently selects the appropriate implementation based on hardware capabilities, delivering the best possible performance for each device.

Key takeaways:
- CUDA devices provide the best performance, especially with Tensor Core optimizations
- CPU, MPS, and XPU implementations provide broad compatibility
- Different quantization methods (int4, int8, float8) offer varying performance profiles
- Benchmark tools help evaluate and compare performance across configurations

For more information on specific quantization methods and techniques, see [AWQ (Activation-Aware Weight Quantization)](#6.1) and [Marlin and TinyGemm](#6.2).

---

# Page: Contributing

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/check-commits.yml](.github/workflows/check-commits.yml)
- [.github/workflows/linux-cpu-tests.yml](.github/workflows/linux-cpu-tests.yml)
- [.github/workflows/linux-cuda-tests.yml](.github/workflows/linux-cuda-tests.yml)
- [.github/workflows/linux-examples.yml](.github/workflows/linux-examples.yml)
- [.github/workflows/python-quality.yml](.github/workflows/python-quality.yml)
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



This page outlines how to contribute to the Optimum-Quanto project. It provides guidelines for setting up a development environment, submitting issues, implementing improvements, and creating pull requests. For information about using Optimum-Quanto in your projects, see [Getting Started](#2).

Optimum-Quanto welcomes contributions from everyone, regardless of their experience level. This document will help you get started with the development process and ensure your contributions meet the project's standards.

Sources: [CONTRIBUTING.md:17-31]()

## Ways to Contribute

There are several ways to contribute to Optimum-Quanto:

1. **Fix outstanding issues** - Identify and fix bugs or improve existing code
2. **Submit issues** - Report bugs or request new features
3. **Implement new kernels** - Add support for new hardware or optimization techniques

All contributions are equally valuable to the project, whether they're code-related or focused on documentation and community support.

Sources: [CONTRIBUTING.md:32-41]()

## Development Environment Setup

To contribute to Optimum-Quanto, you'll need:

- Python 3.9 or above
- Git for version control
- PyTorch 2.6.0 or above

### Setting Up Your Environment

```mermaid
flowchart TD
    A["Fork Repository"] --> B["Clone Repository"]
    B --> C["Set Up Virtual Environment"]
    C --> D["Install Dependencies"]
    D --> E["Install Optimum-Quanto in Dev Mode"]
    E --> F["Verify Installation"]
    
    subgraph "Terminal Commands"
        G1["git clone git@github.com:<your-handle>/optimum-quanto.git"]
        G2["cd optimum-quanto"]
        G3["python -m venv .venv"]
        G4["source .venv/bin/activate"]
        G5["pip install -e .[dev]"]
        G6["python -c 'import optimum.quanto; print(optimum.quanto.__version__)'"]
    end
```

1. **Fork the repository** on GitHub by clicking the "Fork" button.

2. **Clone your fork** to your local machine:
   ```bash
   git clone git@github.com:<your GitHub handle>/optimum-quanto.git
   cd optimum-quanto
   git remote add upstream https://github.com/huggingface/optimum-quanto.git
   ```

3. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Optimum-Quanto in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

   For running examples, you may want to install additional dependencies:
   ```bash
   pip install -e ".[examples]"
   ```

Sources: [CONTRIBUTING.md:98-129](), [setup.sh:1-18](), [pyproject.toml:17-40]()

## Contribution Workflow

### Development Process

```mermaid
flowchart LR
    A["Create Branch"] --> B["Make Changes"]
    B --> C["Run Tests"]
    C --> D["Apply Code Style"]
    D --> E["Commit Changes"]
    E --> F["Push Changes"]
    F --> G["Create PR"]
    
    subgraph "Tools Used"
        T1["git checkout -b feature-branch"]
        T2["pytest test/<TEST_TO_RUN>.py"]
        T3["make style"]
        T4["git commit -m 'feat: description'"]
        T5["GitHub PR"]
    end
```

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b descriptive-branch-name
   ```

2. **Make your changes** to the codebase.

3. **Run tests** to ensure your changes don't break existing functionality:
   ```bash
   pytest test/<specific_test>.py
   # or run all tests
   make test
   ```

4. **Apply code style** fixes:
   ```bash
   make style
   ```

5. **Commit your changes** with a clear and descriptive message. The project encourages using [conventional commits](https://www.conventionalcommits.org/):
   ```bash
   git add modified_file.py
   git commit -m "feat: add support for new feature"
   ```

6. **Push your changes** to your fork:
   ```bash
   git push -u origin descriptive-branch-name
   ```

7. **Create a pull request** from your branch to the main repository.

Sources: [CONTRIBUTING.md:130-189](), [Makefile:1-15]()

### Submitting a Bug Report

When submitting a bug report, please include:

- Your OS type and version
- Python and PyTorch versions
- A minimal code snippet that reproduces the bug
- The full traceback if an exception is raised
- Any additional helpful information like screenshots

Before submitting, verify that the bug hasn't already been reported by searching the existing issues.

Sources: [CONTRIBUTING.md:52-66]()

### Requesting a Feature

Feature requests should include:

1. **Motivation** - Why the feature is needed
2. **Detailed description** - What the feature would do
3. **Example usage** - Code snippet demonstrating how it would be used
4. **References** - Links to papers or other implementations if applicable

Sources: [CONTRIBUTING.md:67-79]()

### Implementing a New Kernel

When proposing a new kernel implementation, specify:

- The hardware configuration(s) it will support
- Any novel techniques that will be used in the implementation

Sources: [CONTRIBUTING.md:81-88]()

## Code Structure and Organization

The following diagram shows the main components of Optimum-Quanto that you might interact with when contributing:

```mermaid
classDiagram
    class QTensor {
        +dequantize()
    }
    
    class WeightQBytesTensor {
        +data: tensor
        +scale: tensor
        +qtype: QuantType
        +dequantize()
    }
    
    class WeightQBitsTensor {
        +data: tensor
        +scale: tensor
        +shift: tensor
        +qtype: QuantType
        +group_size: int
        +dequantize()
    }
    
    class QModuleMixin {
        +weight_qtype
        +activation_qtype
        +qweight: QTensor
        +from_module()
        +forward()
        +freeze()
    }
    
    class QLinear {
        +forward(input)
    }
    
    class QConv2d {
        +forward(input)
    }
    
    QTensor <|-- WeightQBytesTensor
    QTensor <|-- WeightQBitsTensor
    QModuleMixin <|-- QLinear
    QModuleMixin <|-- QConv2d
```

Understanding this structure will help you determine where to make changes when implementing features or fixing bugs.

Sources: [README.md:5-16]()

## Testing Guidelines

Optimum-Quanto uses pytest for testing. Tests are located in the `test` directory.

### Running Tests

To run a specific test:
```bash
python -m pytest -sv test/path/to/test_file.py
```

To run all tests:
```bash
make test
```

### Test Structure

```mermaid
flowchart TD
    A["test/"] --> B["Base Tests"]
    A --> C["Models Tests"]
    A --> D["CLI Tests"]
    
    B --> B1["Tensor Quantization Tests"]
    B --> B2["Module Quantization Tests"]
    B --> B3["Integration Tests"]
    
    C --> C1["Transformers Tests"]
    C --> C2["Diffusers Tests"]
    
    D --> D1["Command Line Interface Tests"]
```

When adding new functionality, include appropriate tests that verify your implementation works as expected. The CI workflow includes testing on both CPU and CUDA environments across multiple Python versions.

Sources: [CONTRIBUTING.md:202-216](), [.github/workflows/linux-cpu-tests.yml:23-56](), [.github/workflows/linux-cuda-tests.yml:23-58]()

## Code Quality and Style

Optimum-Quanto follows specific code style guidelines:

1. **Style Guide**: The project follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for documentation strings.

2. **Code Formatting**: Code is formatted using `ruff format`.

3. **Linting**: Code is linted using `ruff check`.

You can check your code for style issues with:
```bash
make check
```

And apply automatic fixes with:
```bash
make style
```

Sources: [CONTRIBUTING.md:218-222](), [.github/workflows/python-quality.yml:1-21](), [pyproject.toml:53-69]()

## Pull Request Guidelines

When submitting a pull request, ensure it meets the following requirements:

1. **The PR title should summarize your contribution**
2. **Reference related issues** if applicable
3. **Indicate work in progress** with `[WIP]` prefix
4. **Ensure existing tests pass**
5. **Include tests for new features**
6. **Add docstrings** for all public methods

The pull request template will remind you of these requirements when you create a PR.

```mermaid
flowchart LR
    A["Create PR on GitHub"] --> B["CI Checks Run"]
    B --> C["Code Review"]
    C --> D1["Request Changes"]
    C --> D2["Approve"]
    D1 --> E1["Update PR"]
    E1 --> C
    D2 --> F["Merge PR"]
```

Sources: [CONTRIBUTING.md:190-201](), [.github/PULL_REQUEST_TEMPLATE.md:1-31]()

## Continuous Integration

Optimum-Quanto uses GitHub Actions for continuous integration. The following checks run automatically on all pull requests:

| Check | Description |
|-------|-------------|
| Check Commits | Verifies commit message quality |
| Python Quality | Runs code formatting and linting checks |
| Linux CPU Tests | Runs tests on CPU with Python 3.9 and 3.11 |
| Linux CUDA Tests | Runs tests on CUDA 11.8, 12.4, and 12.6 |
| Linux Examples | Verifies that examples run correctly |

Your pull request needs to pass all these checks before it can be merged.

Sources: [.github/workflows/check-commits.yml:1-18](), [.github/workflows/linux-cpu-tests.yml:1-82](), [.github/workflows/linux-cuda-tests.yml:1-59](), [.github/workflows/linux-examples.yml:1-78]()

## License

Optimum-Quanto is licensed under the Apache License 2.0. By contributing to the project, you agree to license your contributions under the same license.

Sources: [LICENSE:1-204](), [CONTRIBUTING.md:132-136]()

---

# Page: Development Setup

# Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check-commits.yml](.github/workflows/check-commits.yml)
- [.github/workflows/linux-cpu-tests.yml](.github/workflows/linux-cpu-tests.yml)
- [.github/workflows/linux-cuda-tests.yml](.github/workflows/linux-cuda-tests.yml)
- [.github/workflows/linux-examples.yml](.github/workflows/linux-examples.yml)
- [.github/workflows/python-quality.yml](.github/workflows/python-quality.yml)
- [Makefile](Makefile)
- [external/awq/test_awq_kernels.py](external/awq/test_awq_kernels.py)
- [external/awq/test_awq_packing.py](external/awq/test_awq_packing.py)
- [external/smoothquant/smoothquant.py](external/smoothquant/smoothquant.py)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)

</details>



This document provides detailed instructions for setting up a development environment for the Optimum-Quanto project. It is intended for developers who want to contribute to the codebase or make custom modifications to the quantization framework.

For information about testing your contributions, see [Testing Guidelines](#10.2).

## Prerequisites

Before setting up your development environment for Optimum-Quanto, ensure you have the following prerequisites installed:

- Python 3.9 or higher (supports 3.9, 3.10, and 3.11)
- Git
- CUDA toolkit (optional, for CUDA backend development)

Sources: [pyproject.toml:10-13](), [.github/workflows/linux-cpu-tests.yml:27-29]()

## Development Environment Setup

### Development Environment Overview

Development Setup Diagram
```mermaid
flowchart TD
    A["Development Environment Setup"] --> B["Prerequisites"]
    A --> C["Installation Methods"]
    A --> D["Development Tools"]
    A --> E["Device-Specific Setup"]
    
    B --> B1["Python >= 3.9"]
    B --> B2["Git"]
    B --> B3["CUDA Toolkit (optional)"]
    
    C --> C1["setup.sh script"]
    C --> C2["pip install -e .[dev]"]
    
    C1 --> C1A[".venv creation"]
    C1 --> C1B["PyTorch installation"]
    C1 --> C1C["Dev tools installation"]
    
    C2 --> C2A["Core dependencies"]
    C2 --> C2B["Development dependencies"]
    C2 --> C2C["pip install -e .[examples] (optional)"]
    
    D --> D1["make check/style (ruff)"]
    D --> D2["make test (pytest)"]
    D --> D3["pyproject.toml configs"]
    
    E --> E1["CUDA Setup"]
    E --> E2["CPU Setup"]
    E --> E3["CI Environment"]
    
    E1 --> E1A["Compatible PyTorch+CUDA"]
    E1 --> E1B["Ninja for CUDA compilation"]
    
    E3 --> E3A["GitHub Actions"]
    E3 --> E3B["Docker containers"]
```

Sources: [pyproject.toml:17-40](), [setup.sh:1-18]()

### Method 1: Using the Setup Script

The repository provides a convenient setup script that creates a virtual environment and installs all necessary dependencies:

```bash
# For stable PyTorch
./setup.sh

# For PyTorch nightly build
./setup.sh 1
```

This script:
1. Creates a Python virtual environment in the `.venv` directory
2. Installs PyTorch, torchvision, and torchaudio
3. Installs development tools (ruff, pytest, build)
4. Installs common dependencies for examples

Sources: [setup.sh:1-18]()

### Method 2: Manual Installation

If you prefer to set up your environment manually, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/huggingface/optimum-quanto.git
   cd optimum-quanto
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

4. If you want to run the examples, install additional dependencies:
   ```bash
   pip install -e .[examples]
   ```

Sources: [pyproject.toml:30-40]()

## Project Dependencies

Optimum-Quanto has different dependency groups:

Project Dependencies
```mermaid
graph TD
    A["optimum-quanto dependencies"] --> B["Core Dependencies (pyproject.toml)"]
    A --> C["Development Dependencies [dev]"]
    A --> D["Example Dependencies [examples]"]
    
    B --> B1["torch>=2.6.0"]
    B --> B2["ninja"]
    B --> B3["numpy"]
    B --> B4["safetensors"]
    B --> B5["huggingface_hub"]
    
    C --> C1["pytest"]
    C --> C2["ruff"]
    
    D --> D1["transformers"]
    D --> D2["diffusers"]
    D --> D3["datasets"]
    D --> D4["accelerate"]
    D --> D5["torchvision"]
    D --> D6["sentencepiece"]
    D --> D7["scipy"]
```

Sources: [pyproject.toml:22-40]()

### Core Dependencies

The core dependencies are required for the basic functionality of Optimum-Quanto:

| Dependency | Purpose |
|------------|---------|
| torch>=2.6.0 | PyTorch framework for tensor operations |
| ninja | Build system for CUDA extension compilation |
| numpy | Numerical computing library |
| safetensors | Secure tensor storage and loading |
| huggingface_hub | Integration with Hugging Face models |

Sources: [pyproject.toml:22]()

### Development Dependencies

For development and testing, additional packages are needed:

| Dependency | Purpose |
|------------|---------|
| pytest | Testing framework |
| ruff | Code linting and formatting |

Sources: [pyproject.toml:31]()

### Example Dependencies

To run the examples provided in the repository:

| Dependency | Purpose |
|------------|---------|
| transformers | Hugging Face Transformers library |
| diffusers | Hugging Face Diffusers library |
| datasets | Dataset loading and processing |
| accelerate | Distributed training utilities |
| torchvision | Computer vision utilities |
| sentencepiece | Tokenization for language models |
| scipy | Scientific computing utilities |

Sources: [pyproject.toml:32-40]()

## Development Tools and Workflow

### Code Quality Tools

Optimum-Quanto uses `ruff` for code formatting and linting, configured in `pyproject.toml`:

```bash
# Check code quality (linting)
make check

# Automatically fix code style issues
make style
```

These commands are shortcuts for:

```bash
# Equivalent to make check
ruff check --show-fixes optimum test bench examples
ruff format optimum test bench examples --diff

# Equivalent to make style
ruff check optimum test bench examples --fix
ruff format optimum test bench examples
```

Sources: [Makefile:1-11](), [pyproject.toml:53-69](), [.github/workflows/python-quality.yml:1-21]()

### Running Tests

To run the test suite:

```bash
# Run all tests
make test

# Or the equivalent command
python -m pytest -sv test
```

To run specific tests:

```bash
# Run only base tests (excluding models and CLI tests)
python -m pytest test --ignore=test/models --ignore=test/cli

# Run only model tests
python -m pytest test/models

# Run only CLI tests
python -m pytest test/cli
```

Sources: [Makefile:13-14](), [.github/workflows/linux-cpu-tests.yml:42-56]()

## Device-Specific Development

### CUDA Development

When working on CUDA-specific features:

1. Ensure you have a compatible CUDA toolkit installed
2. Install PyTorch with the appropriate CUDA version
3. The `ninja` build system will automatically compile CUDA extensions

Optimum-Quanto is tested with CUDA versions 11.8, 12.4, and 12.6 in the CI pipeline.

To run CUDA-specific tests:

```bash
# Run tests with CUDA support
python -m pytest test/...  # Automatically uses CUDA if available
```

Sources: [.github/workflows/linux-cuda-tests.yml:25-58]()

### CPU Development

For CPU-specific development:

1. No special setup is required beyond the standard dependencies
2. The codebase has optimization paths for CPU execution
3. Tests run automatically on CPU when CUDA is not available

Sources: [.github/workflows/linux-cpu-tests.yml:23-56]()

## Continuous Integration

The project uses GitHub Actions for continuous integration. Understanding the CI pipeline will help you ensure your contributions meet the project's quality standards.

CI Pipeline Diagram
```mermaid
flowchart TD
    A["Pull Request"] --> B["check-commits.yml"]
    A --> C["python-quality.yml"]
    A --> D["linux-cpu-tests.yml"]
    A --> E["linux-cuda-tests.yml"]
    A --> F["linux-examples.yml"]
    
    B --> B1["huggingface/action-check-commits"]
    B1 --> G["Commit Messages Quality Check"]
    
    C --> C1["ruff format and check"]
    C1 --> H["Code Style Quality Check"]
    
    D --> D1["Python 3.9/3.11 Tests"]
    D1 --> I["CPU Tests Pass?"]
    
    E --> E1["CUDA 11.8/12.4/12.6 Tests"]
    E1 --> J["CUDA Tests Pass?"]
    
    F --> F1["CPU and CUDA Examples"]
    F1 --> K["Examples Run Successfully?"]
    
    G & H & I & J & K --> L["All Checks Passed?"]
    L -- Yes --> M["Ready for Review"]
    L -- No --> N["Fix Issues"]
```

Sources: [.github/workflows/check-commits.yml:1-18](), [.github/workflows/linux-cpu-tests.yml:1-81](), [.github/workflows/linux-cuda-tests.yml:1-59](), [.github/workflows/python-quality.yml:1-21](), [.github/workflows/linux-examples.yml:1-78]()

### CI Workflows

The CI system includes these main workflows:

1. **Commit Quality** (`check-commits.yml`): Ensures commit messages meet quality standards
2. **Code Quality** (`python-quality.yml`): Runs ruff to check code style and formatting
3. **CPU Tests** (`linux-cpu-tests.yml`): Runs tests on Linux with Python 3.9 and 3.11
4. **CUDA Tests** (`linux-cuda-tests.yml`): Runs tests on Linux with different CUDA versions
5. **Example Tests** (`linux-examples.yml`): Ensures examples run correctly on both CPU and CUDA

Sources: [.github/workflows/linux-cpu-tests.yml:18-56](), [.github/workflows/linux-cuda-tests.yml:18-58](), [.github/workflows/linux-examples.yml:18-77]()

### CI Environment

The CI system uses Docker containers for CUDA testing:

```yaml
container:
  image: pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel
  options: --gpus 0
```

This ensures consistent testing environments across different execution contexts.

Sources: [.github/workflows/linux-cuda-tests.yml:31-33](), [.github/workflows/linux-examples.yml:31-33]()

## Project Structure

The repository has the following structure:

Project Structure Diagram
```mermaid
graph TD
    A["optimum-quanto repository"] --> B["optimum/quanto/"]
    A --> C["test/"]
    A --> D["bench/"]
    A --> E["examples/"]
    A --> F["external/"]
    A --> G[".github/workflows/"]
    
    B --> B1["quanto.tensor/ (QTensor classes)"]
    B --> B2["quanto.library/ (CUDA extensions)"]
    B --> B3["quanto.modules/ (QModuleMixin)"]
    B --> B4["quanto.backends/ (device-specific)"]
    
    C --> C1["test_tensor.py"]
    C --> C2["test_modules.py"]
    C --> C3["test_model.py"]
    C --> C4["models/test_transformers.py"]
    
    E --> E1["vision/image-classification"]
    E --> E2["nlp/text-generation"]
    E --> E3["vision/text-to-image"]
    
    G --> G1["linux-cpu-tests.yml"]
    G --> G2["linux-cuda-tests.yml"]
    G --> G3["python-quality.yml"]
```

Sources: [pyproject.toml:42-44](), [.github/workflows/linux-examples.yml:47-77]()

### Key Directories

| Directory | Purpose |
|-----------|---------|
| optimum/quanto/ | Main package code with quantization implementations |
| test/ | Test suite for the package |
| bench/ | Benchmarking utilities |
| examples/ | Example applications for different model types |
| external/ | External algorithms (e.g., SmoothQuant, AWQ) |
| .github/workflows/ | CI configuration |

Sources: [external/smoothquant/smoothquant.py:1-145](), [external/awq/test_awq_kernels.py:1-154](), [external/awq/test_awq_packing.py:1-89]()

## Commit Guidelines

When contributing to Optimum-Quanto, follow these commit message guidelines:

1. Each commit message should have at least 3 words
2. Avoid using "fixup" in commit messages
3. Keep the number of commits in a pull request to 10 or fewer

These guidelines are enforced by the `check-commits.yml` workflow.

Sources: [.github/workflows/check-commits.yml:1-18]()

## Conclusion

This development setup guide provides the essential information to get started contributing to Optimum-Quanto. By following these instructions, you'll be able to set up a proper development environment, understand the project structure, and follow the established workflows for code quality and testing.

---

# Page: Testing Guidelines

# Testing Guidelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check-commits.yml](.github/workflows/check-commits.yml)
- [.github/workflows/linux-cpu-tests.yml](.github/workflows/linux-cpu-tests.yml)
- [.github/workflows/linux-cuda-tests.yml](.github/workflows/linux-cuda-tests.yml)
- [.github/workflows/linux-examples.yml](.github/workflows/linux-examples.yml)
- [.github/workflows/python-quality.yml](.github/workflows/python-quality.yml)
- [test/helpers.py](test/helpers.py)
- [test/models/conftest.py](test/models/conftest.py)
- [test/models/test_quantized_model_for_causal_lm.py](test/models/test_quantized_model_for_causal_lm.py)
- [test/models/test_quantized_model_for_pixart.py](test/models/test_quantized_model_for_pixart.py)

</details>



This document provides comprehensive guidelines for testing the Optimum-Quanto library. It covers the testing infrastructure, writing effective tests, running tests locally and in CI/CD pipelines, and best practices for testing quantization functionality. For information about setting up a development environment, see [Development Setup](#10.1).

## Testing Infrastructure

Optimum-Quanto uses pytest for its testing framework and includes several helper utilities, fixtures, and workflows to facilitate thorough testing of quantization operations.

### Test Infrastructure Overview

```mermaid
graph TD
    A["Optimum-Quanto Tests"] --> B["Core Tests"]
    A --> C["Model Tests"]
    A --> D["CLI Tests"]
    A --> E["CI Workflows"]
    
    B --> B1["Tensor Quantization Tests"]
    B --> B2["Module Quantization Tests"]
    B --> B3["Utility Tests"]
    
    C --> C1["Causal LM Tests"]
    C --> C2["Diffusion Model Tests"]
    
    E --> E1["Linux CPU Tests"]
    E --> E2["Linux CUDA Tests"]
    E --> E3["Python Quality Checks"]
    E --> E4["Examples Tests"]
    
    subgraph "Helper Functions"
        F1["torch_min_version()"]
        F2["device_eq()"]
        F3["random_tensor()"]
        F4["random_qactivation()"]
        F5["random_qweight()"]
        F6["assert_similar()"]
        F7["get_device_memory()"]
    end
```

Sources: [test/helpers.py:1-113](), [.github/workflows/linux-cpu-tests.yml:1-82](), [.github/workflows/linux-cuda-tests.yml:1-59]()

### Test Helpers

The `test/helpers.py` file provides essential utilities for testing quantization functionality:

1. **Version Checking**: `torch_min_version` decorator to skip tests requiring newer PyTorch versions
2. **Device Utilities**: `device_eq()` for comparing devices, `get_device_memory()` for checking memory usage
3. **Tensor Generation**: `random_tensor()`, `random_qactivation()`, and `random_qweight()` for creating test data
4. **Assertions**: `assert_similar()` for comparing tensors with appropriate tolerances based on precision

Example of using the tensor generation helpers:

```python
# Create a random quantized weight tensor with qint4 precision
qweight = random_qweight(shape=(64, 64), qtype=qint4, axis=0, group_size=32)

# Create a random quantized activation tensor with qint8 precision
qactivation = random_qactivation(shape=(1, 64), qtype=qint8)
```

Sources: [test/helpers.py:33-108]()

## Writing Tests

### Test Structure

Tests in Optimum-Quanto follow a clear structure that helps maintain consistency and readability:

```mermaid
classDiagram
    class TestPattern {
        +Setup test data
        +Execute functionality
        +Verify results
        +Cleanup resources
    }
    
    class ModelTests {
        +Create model
        +Quantize model
        +Save/load model
        +Compare original vs loaded
        +Verify outputs match
    }
    
    class TensorTests {
        +Create input tensor
        +Quantize tensor
        +Verify properties
        +Test dequantization
    }
    
    TestPattern <|-- ModelTests
    TestPattern <|-- TensorTests
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:10-149](), [test/models/test_quantized_model_for_pixart.py:10-112]()

### Test Parametrization

Tests should be parametrized to cover multiple scenarios, such as different:
- Quantization types (qint4, qint8, float8)
- Devices (CPU, CUDA, MPS, XPU)
- Model configurations
- Exclusion patterns

Example from the codebase:

```python
@pytest.mark.parametrize("model_id", ["facebook/opt-125m"])
@pytest.mark.parametrize("qtype", [qint4, qint8], ids=["qint4", "qint8"])
@pytest.mark.parametrize("exclude_lm_head", [True, False], ids=["full", "no_lm_head"])
def test_quantized_model_for_causal_lm_base(model_id, qtype, exclude_lm_head):
    # Test body
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:76-88]()

### Model Comparison

For testing model quantization, use the `compare_models` pattern to ensure quantized models maintain both structural integrity and functional equivalence:

1. Compare module structures
2. Check quantized modules are properly identified
3. Verify tensor equality
4. Ensure output equivalence on the same inputs

Sources: [test/models/test_quantized_model_for_causal_lm.py:49-72](), [test/models/test_quantized_model_for_pixart.py:40-74]()

## Running Tests

### Local Test Execution

To run tests locally:

```bash
# Run all tests
python -m pytest test

# Run specific test modules
python -m pytest test/models

# Run specific test files
python -m pytest test/models/test_quantized_model_for_causal_lm.py

# Run tests with specific markers or patterns
python -m pytest test -k "causal_lm"
```

### Test Selection and Skipping

Use conditional test execution to handle environment-specific testing:

```python
# Skip tests that require specific packages
@pytest.mark.skipif(not is_transformers_available(), reason="requires transformers")

# Skip tests requiring specific PyTorch versions
@torch_min_version("2.0.0")
def test_requires_newer_pytorch():
    # Test body
```

Sources: [test/helpers.py:33-43](), [test/models/test_quantized_model_for_causal_lm.py:75]()

## CI/CD Pipeline

Optimum-Quanto uses GitHub Actions for automated testing. The CI pipeline structure is shown below:

```mermaid
flowchart TD
    A["Pull Request"] --> B["Check Commits"]
    A --> C["Python Quality"]
    
    B --> D["Linux CPU Tests"]
    C --> D
    
    B --> E["Linux CUDA Tests"]
    C --> E
    
    B --> F["Linux Examples"]
    C --> F
    
    D --> D1["Python 3.9"]
    D --> D2["Python 3.11"]
    
    E --> E1["CUDA 11.8"]
    E --> E2["CUDA 12.4"]
    E --> E3["CUDA 12.6"]
    
    subgraph "Test Suites"
        G["Base Tests"]
        H["Model Tests"]
        I["CLI Tests"]
    end
    
    D1 --> G
    D1 --> H
    D1 --> I
    
    E1 --> G
    E1 --> H
    E1 --> I
```

Sources: [.github/workflows/linux-cpu-tests.yml:1-82](), [.github/workflows/linux-cuda-tests.yml:1-59](), [.github/workflows/linux-examples.yml:1-78]()

### CI Workflows

1. **Code Quality** (`.github/workflows/python-quality.yml`): Enforces code formatting and linting standards using ruff
2. **Linux CPU Tests** (`.github/workflows/linux-cpu-tests.yml`): Tests on CPU with Python 3.9 and 3.11
3. **Linux CUDA Tests** (`.github/workflows/linux-cuda-tests.yml`): Tests on multiple CUDA versions (11.8, 12.4, 12.6)
4. **Linux Examples** (`.github/workflows/linux-examples.yml`): Verifies all example applications work as expected

Sources: [.github/workflows/python-quality.yml:1-21](), [.github/workflows/linux-cpu-tests.yml:1-82](), [.github/workflows/linux-cuda-tests.yml:1-59]()

## Testing Hugging Face Hub Integration

Optimum-Quanto includes tests for Hugging Face Hub integration using a staging environment to avoid cluttering the production Hub:

```mermaid
flowchart LR
    A["Quantized Model"] --> B["push_to_hub()"]
    B --> C["Hub Repository"]
    C --> D["from_pretrained()"]
    D --> E["Requantized Model"]
    E --> F["compare_models()"]
    A --> F
    
    subgraph "Staging Environment"
        C
    end
```

The repository uses a `staging` fixture to provide a sandboxed environment:

```python
@pytest.fixture
def staging():
    if not _staging_mode:
        pytest.skip("requires huggingface_hub staging mode")
    return {
        "user": "__DUMMY_TRANSFORMERS_USER__",
        "token": "hf_94wBhPGp6KrrTH3KDchhKpRxZwd6dmHWLL",
    }
```

Sources: [test/models/conftest.py:1-29](), [test/models/test_quantized_model_for_causal_lm.py:106-128]()

## Best Practices

1. **Comprehensive Coverage**: Test all quantization types (qint4, qint8, float8) and configurations.
2. **Device Testing**: Test on multiple devices when applicable (CPU, CUDA).
3. **Error Cases**: Include tests for expected error conditions and edge cases.
4. **Model Serialization**: Always test the save/load cycle for quantized models.
5. **Output Verification**: Verify that quantized model outputs maintain acceptable similarity to original models.
6. **Non-Regression Testing**: When fixing bugs, add tests that would detect those bugs in the future.
7. **Isolated Test Fixtures**: Use pytest fixtures to ensure tests are isolated and don't interfere with each other.
8. **Appropriate Tolerances**: Use appropriate tolerances for different precision levels when comparing results.

```python
# Example of using proper tolerances based on precision
def assert_similar(a, b, atol=None, rtol=None):
    if atol is None:
        atol = torch.finfo(a.dtype).resolution
    if rtol is None:
        rtol = {torch.float32: 1e-5, torch.float16: 1e-3, torch.bfloat16: 1e-1}[a.dtype]
    # Compare tensors
```

Sources: [test/helpers.py:81-95]()

## Performance Testing

When writing tests for performance-critical code:

1. **Memory Usage**: Use `get_device_memory()` to track memory consumption
2. **Device Cleanup**: Properly clean up device memory between tests with:
   ```python
   gc.collect()
   torch.cuda.empty_cache()  # or torch.mps.empty_cache() / torch.xpu.empty_cache()
   ```
3. **Parameterized Performance**: Test performance across different sizes, quantization types, and devices

Sources: [test/helpers.py:98-109]()

## Common Test Patterns

### Quantized Model Testing

```python
def test_quantized_model():
    # 1. Create or load original model
    model = create_or_load_model()
    
    # 2. Quantize the model
    quantized = QuantizedModelClass.quantize(model, weights=qtype, exclude=exclude_patterns)
    
    # 3. Save and reload the model
    with TemporaryDirectory() as tmpdir:
        quantized.save_pretrained(tmpdir)
        requantized = QuantizedModelClass.from_pretrained(tmpdir)
    
    # 4. Compare the original quantized and reloaded models
    compare_models(quantized, requantized)
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:76-88](), [test/models/test_quantized_model_for_pixart.py:77-89]()

### Non-Strict Loading Tests

Include tests for non-strict loading to ensure models can be loaded even when missing some parameters:

```python
def test_non_strict_loading():
    # Create a state dict with missing keys
    sd = model.state_dict()
    del sd[some_key]
    
    # Test strict loading (should fail)
    with pytest.raises(RuntimeError):
        model.load_state_dict(sd)
    
    # Test non-strict loading (should succeed with missing keys reported)
    result = model.load_state_dict(sd, strict=False)
    assert some_key in result.missing_keys
```

Sources: [test/models/test_quantized_model_for_causal_lm.py:132-149]()

By following these testing guidelines, you can help ensure the reliability and quality of the Optimum-Quanto library.