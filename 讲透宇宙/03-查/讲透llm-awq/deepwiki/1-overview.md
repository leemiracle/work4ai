<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/llm-awq · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [scripts/qwen_example.sh](scripts/qwen_example.sh)
- [tinychat/README.md](tinychat/README.md)
- [tinychat/utils/constants.py](tinychat/utils/constants.py)

</details>



This page provides an introduction to the AWQ (Activation-aware Weight Quantization) repository, explaining the key components and workflows of the system. AWQ enables efficient and accurate low-bit weight quantization (INT3/4) for Large Language Models (LLMs), supporting both instruction-tuned models and multi-modal language models (VLMs).

The AWQ repository consists of two main systems:
1. The AWQ quantization framework for compressing LLMs while maintaining quality
2. TinyChat, an efficient inference runtime for deploying the quantized models

For detailed information about the quantization algorithm, see [AWQ Quantization System](#2), and for more on the inference system, refer to [TinyChat System](#3).

## System Architecture

Here's a high-level overview of the AWQ system architecture:

```mermaid
graph TD
    A["Original LLM/VLM"] --> B["awq.entry Module"]
    B --> C["Quantized Model (WQLinear layers)"]
    C --> D["TinyChat Runtime"]
    C --> E["Direct Application Integration"]

    subgraph "AWQ Core Components"
        B1["AWQ Search\n(auto_scale, auto_clip)"]
        B2["Weight Quantization\n(WQLinear, CUDA kernels)"]
        B3["Model Evaluation"]
        B1 --- B2 --- B3
    end

    subgraph "TinyChat Features"
        D1["Optimized Inference\n(context streaming)"]
        D2["Text Generation"]
        D3["Visual Input Processing"]
        D1 --- D2 --- D3
    end

    B -.-> B1
    C -.-> D1
```

Sources: [README.md:10-16]()

## Quantization Workflow

The AWQ quantization process involves three main operations, controlled through command-line arguments to the `awq.entry` module:

```mermaid
flowchart LR
    A["Original Model"] --> B["awq.entry Main Function"]
    B --> C{"Mode Selection"}
    
    C -->|"--run_awq"| D["Run AWQ Search"]
    D --> E["auto_scale_block()"]
    D --> F["auto_clip_block()"]
    E --> G["Compute Channel-wise Scales"]
    F --> H["Compute Weight Clipping"]
    G --> I["Save AWQ Results (--dump_awq)"]
    H --> I
    
    C -->|"--load_awq"| J["Load AWQ Results"]
    J --> K{"--q_backend"}
    K -->|"fake"| L["Pseudo Quantize Model"]
    K -->|"real"| M["Real Quantize Model"]
    L --> N["Evaluate Model (--tasks)"]
    M --> O["Create WQLinear Layers"]
    O --> P["Save Quantized Model (--dump_quant)"]
    
    C -->|"--load_quant"| Q["Load Quantized Model"]
    Q --> R["Run Evaluation"]
```

Sources: [scripts/qwen_example.sh:3-25](), [README.md:177-208]()

The workflow consists of three main phases:
1. **Search Mode**: Find optimal quantization parameters (scales and clips)
2. **Quantize Mode**: Apply quantization to the model using these parameters
3. **Evaluate Mode**: Assess the performance of the quantized model

## TinyChat Runtime

TinyChat provides an efficient inference environment for the quantized models:

```mermaid
graph TD
    A["TinyChat System"] --> B["Model Loading"]
    A --> C["Inference Engine"]
    A --> D["User Interfaces"]
    
    B --> B1["load_awq_model()"]
    B --> B2["load_awq_llama_fast()"]
    B --> B3["Memory-Efficient Loading"]
    
    C --> C1["StreamGenerator"]
    C --> C2["LlavaStreamGenerator"]
    C --> C3["Optimized Attention"]
    C --> C4["Context Streaming"]
    
    D --> D1["Command-Line Demo"]
    D --> D2["Gradio Web Server"]
    D --> D3["Controller-Worker Architecture"]
    
    subgraph "Memory Optimizations"
        B3
        C4
        M1["mem_efficient_load"]
    end
    
    B3 --- M1
```

Sources: [README.md:51-52](), [tinychat/utils/constants.py:4-9]()

TinyChat is designed for efficient inference with both text-only and multimodal models. It includes:
- Memory-efficient model loading (especially important for edge devices)
- Optimized attention mechanisms
- Streaming text generation
- Support for various user interfaces (CLI and web-based)

## Inference Flow

During inference, TinyChat processes inputs and generates outputs as follows:

```mermaid
sequenceDiagram
    participant User
    participant Interface as "TinyChat Interface"
    participant Generator as "StreamGenerator"
    participant Model as "Quantized Model"
    participant CUDA as "Optimized CUDA Kernels"
    
    User->>Interface: Input (text/image/video)
    Interface->>Generator: generate() request
    Generator->>Model: Forward pass
    Model->>CUDA: Matrix operations (GEMM/GEMV)
    CUDA->>Model: Results
    Model->>Generator: Logits
    Generator->>Generator: Sample next token
    Generator->>Interface: Yield token
    Interface->>User: Display token
    
    loop Until completion
        Generator->>Model: Forward with updated context
        Model->>CUDA: Matrix operations
        CUDA->>Model: Results
        Model->>Generator: Logits
        Generator->>Generator: Sample next token
        Generator->>Interface: Yield token
        Interface->>User: Display token
    end
```

Sources: [README.md:17-18]()

## Multimodal Support

AWQ and TinyChat support multimodal models that can process text, images, and videos:

```mermaid
flowchart LR
    A["User Input"] --> B{"Input Type"}
    B -->|"Text Only"| C["Text Processing"]
    B -->|"Image"| D["Image Processing"]
    B -->|"Video"| E["Video Processing"]
    
    C --> F["Tokenizer"]
    D --> G["Vision Encoder"]
    E --> H["Frame Extraction"]
    H --> G
    
    F --> I["LLM Component"]
    G --> J["Multimodal Projector"]
    J --> I
    
    I --> K["Text Generation"]
    K --> L["Output"]
    
    subgraph "Vision Processing"
        G1["VILA/LLaVA Vision Tower"]
        G2["Quantized Vision Components"]
        G1 --- G2
    end
    
    G --- G1
```

Sources: [README.md:29-43](), [README.md:135-143]()

The multimodal architecture enables processing of:
- Text inputs through tokenizers
- Image inputs through vision encoders (like those in VILA and LLaVA)
- Video inputs by extracting frames and processing them through the vision encoder

## Configuration Parameters

Key configuration parameters for TinyChat (from `tinychat.utils.constants.py`):

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `max_seq_len` | Maximum sequence length | 8192 |
| `max_batch_size` | Maximum batch size | 1 |
| `llama_multiple_of` | Sequence length multiple | 256 |
| `mem_efficient_load` | Layer-wise model loading | False |

Sources: [tinychat/utils/constants.py:4-9]()

The `mem_efficient_load` parameter is particularly useful for edge devices with limited memory.

## Model Support

AWQ supports a wide range of LLMs and VLMs:

| Model Family | Sizes | INT4 | INT3 |
|--------------|-------|------|------|
| DeepSeek-R1-Distill | 8B | ✅ |  |
| Qwen-2.5 | 7B/72B | ✅ |  |
| VILA-1.5 | 3B/8B/13B/40B | ✅ | ✅ |
| Llama3 | 8B/70B | ✅ | ✅ |
| Llama2 | 7B/13B/70B | ✅ | ✅ |
| LLaMA | 7B/13B/30B/65B | ✅ | ✅ |
| OPT | 125m-30B | ✅ | ✅ |
| CodeLlama | 7B/13B/34B | ✅ | ✅ |
| StarCoder | 15.5B | ✅ | ✅ |
| Vicuna | 7B/13B | ✅ |  |
| LLaVA | 13B | ✅ |  |

Sources: [README.md:144-161]()

## Performance Benefits

AWQ quantization provides significant benefits:

- Memory reduction: 3-4x smaller model size
- Inference speedup: 2-3x faster generation
- Maintained accuracy: Minimal quality degradation compared to FP16
- Edge compatibility: Enables running large models on resource-constrained devices

Sources: [README.md:16-17](), [README.md:20-26]()

## Installation and Usage

The AWQ repository can be installed by following these steps:

1. Clone the repository
2. Install the Python package
3. Compile the CUDA kernels
4. (Optional) Install VILA for multimodal support

For practical usage, the most common workflow is:

1. Run AWQ search to find optimal quantization parameters
2. Apply quantization to create a 4-bit model
3. Deploy the quantized model using TinyChat

Sources: [README.md:99-143](), [README.md:176-208]()

---

