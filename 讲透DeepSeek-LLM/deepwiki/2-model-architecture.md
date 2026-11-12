<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-LLM · page 2 Model Architecture · fetched 2026-10-30 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document describes the technical architecture of DeepSeek-LLM models, including their internal structure, parameter configurations, and implementation details. For information about training methodology and data composition, see [Training Methodology](#2.1), and for details about the data processing pipeline, see [Data Pipeline](#2.2).

## Overview

DeepSeek-LLM follows the auto-regressive transformer decoder architecture similar to LLaMA. The models are available in two main parameter sizes (7B and 67B), each with base and chat variants. Both sizes support a context length of 4096 tokens, enabling them to process and generate long-form content.

### High-Level Architecture

```mermaid
graph TD
    subgraph "DeepSeek-LLM Architecture"
        Input["Input Tokens"] --> Embed["Token Embeddings"]
        Embed --> Layers["Transformer Decoder Layers"]
        Layers --> LN["Final Layer Normalization"]
        LN --> OutProj["Output Projection"]
        OutProj --> Output["Output Probabilities"]
        
        subgraph "Decoder Layer"
            InNorm["Input Layer Norm"] --> SAttn["Self Attention<br>(MHA or GQA)"]
            SAttn --> AttnOut["Attention Output"]
            AttnOut --> AddResid1["Add Residual"]
            AddResid1 --> FFNorm["FFN Layer Norm"]
            FFNorm --> FFN["Feed Forward Network"]
            FFN --> AddResid2["Add Residual"]
        end
    end
```

Sources: [README.md:196-197]()

## Model Variants and Specifications

DeepSeek-LLM is available in two main parameter sizes, each with specific architectural choices optimized for performance and efficiency.

| Parameter | DeepSeek-LLM 7B | DeepSeek-LLM 67B |
|-----------|----------------|------------------|
| Total Parameters | 7 billion | 67 billion |
| Attention Mechanism | Multi-Head Attention (MHA) | Grouped-Query Attention (GQA) |
| Context Length | 4096 tokens | 4096 tokens |
| Training Batch Size | 2304 | 4608 |
| Learning Rate | 4.2e-4 | 3.2e-4 |
| Tokenizer | Byte-level BPE | Byte-level BPE |

Sources: [README.md:196-197](), [README.md:198-199]()

## Attention Mechanisms

The DeepSeek-LLM models implement different attention mechanisms depending on model size to balance computational efficiency and model capability.

### Multi-Head Attention (7B Model)

The 7B model uses traditional Multi-Head Attention where queries, keys, and values are projected into multiple heads, each operating independently before being concatenated.

```mermaid
graph TD
    subgraph "Multi-Head Attention (7B Model)"
        Input["Input"] --> QProj["Query Projection"]
        Input --> KProj["Key Projection"]
        Input --> VProj["Value Projection"]
        
        QProj --> QSplit["Split into Heads"]
        KProj --> KSplit["Split into Heads"]
        VProj --> VSplit["Split into Heads"]
        
        QSplit --> |"Head 1"| Attn1["Attention Computation 1"]
        KSplit --> |"Head 1"| Attn1
        VSplit --> |"Head 1"| Attn1
        
        QSplit --> |"Head 2"| Attn2["Attention Computation 2"]
        KSplit --> |"Head 2"| Attn2
        VSplit --> |"Head 2"| Attn2
        
        QSplit --> |"..."| AttnN["..."]
        KSplit --> |"..."| AttnN
        VSplit --> |"..."| AttnN
        
        Attn1 --> Concat["Concatenate"]
        Attn2 --> Concat
        AttnN --> Concat
        
        Concat --> OutProj["Output Projection"]
    end
```

### Grouped-Query Attention (67B Model)

The 67B model uses Grouped-Query Attention (GQA), which reduces computational requirements by sharing keys and values across multiple query heads, making large models more efficient.

```mermaid
graph TD
    subgraph "Grouped-Query Attention (67B Model)"
        Input["Input"] --> QProj["Query Projection"]
        Input --> KProj["Key Projection (Reduced)"]
        Input --> VProj["Value Projection (Reduced)"]
        
        QProj --> QSplit["Split into Query Heads"]
        KProj --> KSplit["Split into KV Groups"]
        VProj --> VSplit["Split into KV Groups"]
        
        QSplit --> |"Query 1"| Attn1["Attention 1"]
        QSplit --> |"Query 2"| Attn2["Attention 2"]
        QSplit --> |"Query N"| AttnN["Attention N"]
        
        KSplit --> |"KV Group 1"| KV1["KV Group 1"]
        VSplit --> |"KV Group 1"| KV1
        KV1 --> Attn1
        KV1 --> Attn2
        
        KSplit --> |"KV Group 2"| KV2["KV Group 2"]
        VSplit --> |"KV Group 2"| KV2
        KV2 --> AttnN
        
        Attn1 --> Concat["Concatenate"]
        Attn2 --> Concat
        AttnN --> Concat
        
        Concat --> OutProj["Output Projection"]
    end
```

GQA allows the 67B model to maintain strong performance while reducing memory footprint and computational requirements compared to standard Multi-Head Attention at that scale.

Sources: [README.md:196-197]()

## Tokenization

DeepSeek-LLM uses a custom implementation of the Byte-level BPE (Byte Pair Encoding) algorithm through the Hugging Face Tokenizer library, with specially designed pre-tokenizers for optimal performance.

```mermaid
graph LR
    Text["Raw Text"] --> PreTok["Custom Pre-tokenizers"]
    PreTok --> BPE["Byte-level BPE"]
    BPE --> Tokens["Tokenized Sequence"]
    Tokens --> Embed["Embedding Layer"]
    Embed --> ModelInput["Model Input"]
```

Unlike some other models, DeepSeek-LLM does not use SentencePiece tokenization, which has implications for compatibility with certain quantization methods.

Sources: [README.md:333-334]()

## Training Configuration

DeepSeek-LLM models were trained using the AdamW optimizer on a dataset of 2 trillion tokens. The training employed a multi-step learning rate schedule:

```mermaid
graph LR
    Start["Training Start"] --> Warmup["2000 Warmup Steps"]
    Warmup --> MaxLR["Maximum Learning Rate"]
    MaxLR --> Step1["Step at 1.6T Tokens<br>(31.6% of Max LR)"]
    Step1 --> Step2["Step at 1.8T Tokens<br>(10% of Max LR)"]
    Step2 --> End["Training End<br>(2T Tokens)"]
```

Sources: [README.md:198-199]()

## Memory Requirements for Inference

The memory requirements for inference vary based on model size, batch size, and sequence length:

### 7B Model (1 NVIDIA A100-40GB GPU)

| Batch Size | 256 tokens | 512 tokens | 1024 tokens | 2048 tokens | 4096 tokens |
|------------|------------|------------|-------------|-------------|-------------|
| 1          | 13.29 GB   | 13.63 GB   | 14.47 GB    | 16.37 GB    | 21.25 GB    |
| 2          | 13.63 GB   | 14.39 GB   | 15.98 GB    | 19.82 GB    | 29.59 GB    |
| 4          | 14.47 GB   | 15.82 GB   | 19.04 GB    | 26.65 GB    | OOM         |
| 8          | 15.99 GB   | 18.71 GB   | 25.14 GB    | 35.19 GB    | OOM         |
| 16         | 19.06 GB   | 24.52 GB   | 37.28 GB    | OOM         | OOM         |

### 67B Model (8 NVIDIA A100-40GB GPUs)

| Batch Size | 256 tokens | 512 tokens | 1024 tokens | 2048 tokens | 4096 tokens |
|------------|------------|------------|-------------|-------------|-------------|
| 1          | 16.92 GB   | 17.11 GB   | 17.66 GB    | 20.01 GB    | 33.23 GB    |
| 2          | 17.04 GB   | 17.28 GB   | 18.55 GB    | 25.27 GB    | OOM         |
| 4          | 17.20 GB   | 17.80 GB   | 21.28 GB    | 33.71 GB    | OOM         |
| 8          | 17.59 GB   | 19.25 GB   | 25.69 GB    | OOM         | OOM         |
| 16         | 18.17 GB   | 21.69 GB   | 34.54 GB    | OOM         | OOM         |

Sources: [README.md:365-369]()

## Model Integration Architecture

The following diagram shows how DeepSeek-LLM's architecture integrates with inference systems and user applications:

```mermaid
graph TD
    User["User Application"] --> InterfaceLayer["Interface Layer"]
    
    subgraph "Inference Integration Options"
        HF["HuggingFace Transformers"]
        VLLM["vLLM"]
        Quant["Quantization<br>GGUF/GPTQ"]
    end
    
    InterfaceLayer --> HF
    InterfaceLayer --> VLLM
    InterfaceLayer --> Quant
    
    subgraph "DeepSeek-LLM Architecture"
        HF --> TokenizerBPE["Tokenizer<br>(Byte-level BPE)"]
        VLLM --> TokenizerBPE
        Quant --> TokenizerQuant["Quantized Tokenizer"]
        
        TokenizerBPE --> Embedding["Embedding Layer"]
        TokenizerQuant --> EmbeddingQuant["Quantized Embedding"]
        
        Embedding --> Decoder["Transformer Decoder<br>(MHA for 7B / GQA for 67B)"]
        EmbeddingQuant --> DecoderQuant["Quantized Decoder"]
        
        Decoder --> LM["Language Model Head"]
        DecoderQuant --> LMQuant["Quantized LM Head"]
        
        LM --> OutputProbs["Output Token Probabilities"]
        LMQuant --> OutputProbsQuant["Quantized Output Probabilities"]
    end
    
    OutputProbs --> Response["Generated Response"]
    OutputProbsQuant --> Response
```

Sources: [README.md:196-197](), [README.md:337-358]()

## Base and Chat Model Variants

For each parameter size (7B and 67B), DeepSeek-LLM offers two variants:

1. **Base Models**: Foundation models trained on the full 2 trillion token dataset
2. **Chat Models**: Fine-tuned versions of the base models optimized for conversational interactions

The underlying architecture remains consistent between base and chat variants of the same parameter size, with differences only in the training objectives used during fine-tuning.

Sources: [README.md:77-78]()

---

