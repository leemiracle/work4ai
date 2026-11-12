<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V2 · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [deepseek-v2-tech-report.pdf](deepseek-v2-tech-report.pdf)

</details>



This document provides a comprehensive overview of DeepSeek-V2, a state-of-the-art Mixture-of-Experts (MoE) language model that balances strong performance with economical training and efficient inference capabilities. DeepSeek-V2 represents a significant advancement in large language model architecture, introducing innovative techniques that substantially improve efficiency while maintaining or enhancing performance across various benchmarks.

For detailed information about the model architecture specifics, see [Model Architecture](#1.1). For a breakdown of different model variants, see [Model Variants](#1.2).

Sources: [README.md:57-67]()

## Model Introduction

DeepSeek-V2 is a large language model comprising 236 billion total parameters, of which only 21 billion are activated for each token during operation. The model was pretrained on a diverse corpus of 8.1 trillion tokens, followed by supervised fine-tuning (SFT) and reinforcement learning (RL) to enhance its capabilities.

Compared to its predecessor, DeepSeek-V1 (67B dense model), DeepSeek-V2 achieves:
- 42.5% reduction in training costs
- 93.3% reduction in KV cache size
- 5.76x increase in maximum generation throughput
- Better performance on standard benchmarks

The DeepSeek-V2 family also includes a smaller variant called DeepSeek-V2-Lite with 16B total parameters and 2.4B activated parameters per token.

### DeepSeek-V2 System Architecture

```mermaid
flowchart TD
    subgraph "DeepSeek-V2 Architecture"
        Input["Input Tokens"] --> Embedding["Embedding Layer"]
        Embedding --> Blocks["Transformer Blocks"]
        Blocks --> Output["Output Layer"]
        
        subgraph "Transformer Block"
            A1["Input"] --> A2["Norm"]
            A2 --> A3["Multi-head Latent Attention (MLA)"]
            A3 --> A4["Add & Norm"]
            A4 --> A5["DeepSeekMoE FFN"]
            A5 --> A6["Output"]
            
            subgraph "MLA Implementation"
                B1["Low-rank Key-Value Union Compression"]
                B2["Reduced KV Cache Size"]
            end
            
            subgraph "DeepSeekMoE"
                C1["Expert Router"]
                C2["Expert 1"]
                C3["Expert 2"]
                C4["Expert N"]
                C1 -->|"Route tokens"| C2 & C3 & C4
                C2 & C3 & C4 -->|"Combine outputs"| C5["Final Output"]
            end
        end
    end
```

Sources: [README.md:202-209]()

## Key Architectural Innovations

DeepSeek-V2 introduces two major architectural innovations that enable its efficiency and performance improvements:

1. **Multi-head Latent Attention (MLA)**: A novel attention mechanism that utilizes low-rank key-value union compression to dramatically reduce the memory requirements of the KV cache. This innovation eliminates a major bottleneck in inference-time memory usage, enabling efficient inference with long contexts up to 128K tokens.

2. **DeepSeekMoE Architecture**: A high-performance Mixture-of-Experts approach for Feed-Forward Networks (FFNs) that allows the model to have a large total parameter count while only activating a small subset for each token. This architecture enables training stronger models at lower costs.

```mermaid
flowchart LR
    subgraph "DeepSeek-V1 vs DeepSeek-V2 Comparison"
        subgraph "DeepSeek-V1"
            V1A["Standard Multi-head Attention"]
            V1B["Dense FFN"]
            V1C["67B Total Parameters"]
            V1D["Large KV Cache"]
        end
        
        subgraph "DeepSeek-V2"
            V2A["Multi-head Latent Attention"]
            V2B["MoE FFN"]
            V2C["236B Total Parameters (21B Activated)"]
            V2D["93.3% Smaller KV Cache"]
        end
        
        Improvements{{"Efficiency Improvements"}}
        Improvements --> I1["42.5% Lower Training Costs"]
        Improvements --> I2["93.3% KV Cache Reduction"]
        Improvements --> I3["5.76x Higher Generation Throughput"]
    end
```

Sources: [README.md:202-209](), [README.md:57-67]()

## Model Family and Variants

The DeepSeek-V2 system includes several model variants optimized for different use cases:

```mermaid
graph TD
    Root["DeepSeek-V2 Model Family"] --> A["DeepSeek-V2"]
    Root --> B["DeepSeek-V2-Lite"]
    
    A --> A1["DeepSeek-V2 Base"]
    A --> A2["DeepSeek-V2 Chat (SFT)"]
    A --> A3["DeepSeek-V2 Chat (RL)"]
    
    B --> B1["DeepSeek-V2-Lite Base"]
    B --> B2["DeepSeek-V2-Lite Chat (SFT)"]
    
    subgraph "Model Specifications"
        spec1["DeepSeek-V2:
        - 236B total parameters
        - 21B activated parameters
        - 128K context length"]
        
        spec2["DeepSeek-V2-Lite:
        - 16B total parameters
        - 2.4B activated parameters
        - 32K context length"]
    end
    
    A ---- spec1
    B ---- spec2
```

Sources: [README.md:74-85]()

| Model Variant | Total Parameters | Activated Parameters | Context Length |
|---------------|------------------|----------------------|----------------|
| DeepSeek-V2 | 236B | 21B | 128K |
| DeepSeek-V2-Chat (SFT/RL) | 236B | 21B | 128K |
| DeepSeek-V2-Lite | 16B | 2.4B | 32K |
| DeepSeek-V2-Lite-Chat (SFT) | 16B | 2.4B | 32K |

Sources: [README.md:74-85]()

## Performance Characteristics

DeepSeek-V2 demonstrates strong performance across a range of benchmarks, including English and Chinese language understanding, code generation, and mathematical reasoning.

The model's context window capabilities have been evaluated using the "Needle In A Haystack" (NIAH) test, confirming effective performance with contexts up to 128K tokens.

DeepSeek-V2-Chat (RL) performs particularly well on open-ended generation evaluations, showing competitive results on benchmarks like AlpacaEval 2.0, MTBench, and Alignbench.

Sources: [README.md:90-200]()

## Usage and Integration Options

DeepSeek-V2 can be accessed and used through multiple channels:

```mermaid
flowchart TB
    User["User"] --> Access{"Access Methods"}
    
    Access -->|"Web Interface"| Web["chat.deepseek.com"]
    Access -->|"API"| API["platform.deepseek.com"]
    Access -->|"Local Deployment"| Local{"Local Deployment Options"}
    
    Local -->|"Option 1"| HF["Hugging Face Transformers"]
    Local -->|"Option 2 (Recommended)"| SGL["SGLang"]
    Local -->|"Option 3 (Recommended)"| VLLM["vLLM"]
    Local -->|"Option 4"| LC["LangChain via API"]
    
    subgraph "SGLang Optimizations"
        SG1["MLA optimizations"]
        SG2["FP8 (W8A8)"]
        SG3["FP8 KV Cache"]
        SG4["Torch Compile"]
    end
    
    SGL --- SG1 & SG2 & SG3 & SG4
    
    Note["Note: Local deployment of
    DeepSeek-V2 requires 8x80GB GPUs"]
    
    Local --- Note
```

Sources: [README.md:211-370]()

### Local Deployment Requirements

Running DeepSeek-V2 locally requires significant computational resources:
- 8 GPUs with 80GB memory each for BF16 format inference
- For smaller deployments, DeepSeek-V2-Lite provides a more accessible option

Sources: [README.md:223-224]()

### Integration Examples

The repository provides code examples for integrating DeepSeek-V2 with various frameworks:

1. **Hugging Face Transformers**: Examples for both text completion and chat completion
2. **SGLang**: Commands for launching an OpenAI API-compatible server with various optimizations
3. **vLLM**: Code example for model inference
4. **LangChain**: Example of using DeepSeek-V2 via the API with the ChatOpenAI interface

The chat models implement a standard chat template format that supports system messages and multiple user-assistant interactions.

Sources: [README.md:224-370]()

## Licensing Information

DeepSeek-V2 is distributed under a dual-licensing model:
- The code repository is licensed under the MIT License
- The model weights are subject to a separate Model License that permits commercial use

For complete licensing details, see [Licensing Information](#5).

Sources: [README.md:371-373]()

---

