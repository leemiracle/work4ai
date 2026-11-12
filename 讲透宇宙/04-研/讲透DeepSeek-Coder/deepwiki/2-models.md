<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-Coder · page 2 Models · fetched 2026-10-30 -->

# Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page provides an overview of the DeepSeek Coder model family, including different model sizes, variants, and their general characteristics. For detailed information about the model architecture, refer to [Architecture](#2.1). For comprehensive benchmark results and performance metrics, see [Performance and Benchmarks](#2.2).

## Model Family Overview

DeepSeek Coder consists of a series of transformer-based language models specifically trained for code understanding and generation. All models were trained from scratch on a massive corpus of 2 trillion tokens, with a composition of 87% code and 13% natural language (both English and Chinese).

The model family includes:

1. **Base Models** - Foundation models trained on code and related texts
2. **Instruction-tuned Models** - Enhanced versions fine-tuned on instruction data for interactive coding assistance

```mermaid
graph TD
    subgraph "DeepSeek Coder Family"
        direction LR
        Base["Base Models"] --> Instruct["Instruction-tuned Models"]
    end

    subgraph "Base Model Sizes"
        Base --> Base1B["DeepSeek-Coder-Base-1B"]
        Base --> Base5.7B["DeepSeek-Coder-Base-5.7B"]
        Base --> Base6.7B["DeepSeek-Coder-Base-6.7B"]
        Base --> Base33B["DeepSeek-Coder-Base-33B"]
    end
    
    subgraph "Instruct Model Sizes"
        Instruct --> Instruct6.7B["DeepSeek-Coder-Instruct-6.7B"]
        Instruct --> Instruct33B["DeepSeek-Coder-Instruct-33B"]
    end
```

Sources: [README.md:11-26](). [README.md:57-62]()

## Model Size Comparison

The DeepSeek Coder family comes in various parameter sizes to suit different deployment requirements, from more efficient smaller models to higher-capability larger models.

| Model | Parameters | Context Window | Variants Available |
|-------|------------|----------------|-------------------|
| DeepSeek-Coder-1B | 1 billion | 16K tokens | Base |
| DeepSeek-Coder-5.7B | 5.7 billion | 16K tokens | Base |
| DeepSeek-Coder-6.7B | 6.7 billion | 16K tokens | Base, Instruct |
| DeepSeek-Coder-33B | 33 billion | 16K tokens | Base, Instruct |

Sources: [README.md:21-22](). [README.md:25]()

## Training Process

The DeepSeek Coder models underwent a comprehensive multi-stage training process to develop both their general code understanding and specialized capabilities.

```mermaid
flowchart TD
    subgraph "Training Pipeline"
        direction TB
        InitialPT["Initial Pre-training<br>1.8T tokens, 4K window<br>87% code, 10% code-related language,<br>3% non-code Chinese language"] --> 
        ExtendedPT["Extended Pre-training<br>200B additional tokens<br>16K window size"] -->
        BaseModels["DeepSeek-Coder-Base Models"]
        
        BaseModels --> InstructFT["Instruction Fine-tuning<br>2B tokens of instruction data"]
        InstructFT --> InstructModels["DeepSeek-Coder-Instruct Models"]
    end
```

Sources: [README.md:58-62]()

## Supported Programming Languages

The models support a wide range of programming languages, making them versatile for various development environments and coding tasks.

```mermaid
graph TD
    subgraph "Language Support Categories"
        direction TB
        DeepSeek["DeepSeek Coder<br>Models"] --> PopularLangs["Popular Languages"]
        DeepSeek --> SysLangs["Systems Programming"]
        DeepSeek --> WebLangs["Web Development"]
        DeepSeek --> DataLangs["Data Science"]
        DeepSeek --> OtherLangs["Other Languages"]
    end
    
    PopularLangs --> Python["Python"]
    PopularLangs --> JavaScript["JavaScript"]
    PopularLangs --> Java["Java"]
    PopularLangs --> CPP["C++"]
    PopularLangs --> CSharp["C#"]
    
    SysLangs --> C["C"]
    SysLangs --> Rust["Rust"]
    SysLangs --> Go["Go"]
    
    WebLangs --> TypeScript["TypeScript"]
    WebLangs --> HTML["HTML"]
    WebLangs --> CSS["CSS"]
    WebLangs --> PHP["PHP"]
    
    DataLangs --> SQL["SQL"]
    DataLangs --> R["R"]
    DataLangs --> Julia["Julia"]
```

The models support over 80 programming languages in total, including: Ada, Agda, Alloy, ANTLR, AppleScript, Assembly, and many others. See the README for the complete list.

Sources: [README.md:27-28]()

## Model Capabilities

DeepSeek Coder models offer a range of capabilities that make them suitable for various coding tasks:

```mermaid
flowchart TD
    subgraph "Core Capabilities"
        CodeCompletion["Code Completion<br>Generate code from natural language prompts"]
        CodeInsertion["Code Insertion<br>Fill-in-the-middle (FIM) capability"]
        RepoLevel["Repository-Level Code Understanding<br>16K context window"]
        Chat["Interactive Chat<br>(Instruct models only)"]
    end
    
    subgraph "Implementation Details"
        CodeCompletion --> CompletionImpl["Autoregressive code generation<br>Base & Instruct models"]
        CodeInsertion --> FIMImpl["Special FIM token handling<br>Base & Instruct models"]
        RepoLevel --> RepoImpl["Long-context understanding<br>Base & Instruct models"]
        Chat --> ChatImpl["Instruction following & dialogue<br>Instruct models only"]
    end
```

Sources: [README.md:74-104](). [README.md:102-141](). [README.md:178-254]()

### Feature Support by Model Variant

| Feature | Base Models | Instruct Models |
|---------|------------|-----------------|
| Code Completion | ✅ | ✅ |
| Fill-in-the-Middle (FIM) | ✅ | ✅ |
| Repository-Level Understanding | ✅ | ✅ |
| Interactive Chat | ❌ | ✅ |

Sources: [README.md:74-266]()

## Performance Overview

DeepSeek Coder models have demonstrated strong performance across various benchmarks. The largest model, DeepSeek-Coder-Base-33B, outperforms other open-source models of similar size, while even the smaller 6.7B model achieves performance comparable to much larger models from other families.

| Model | HumanEval (Python) | MBPP | DS-1000 |
|-------|-------------------|------|---------|
| DeepSeek-Coder-Base-33B | Leading performance | Leading performance | Leading performance |
| DeepSeek-Coder-Base-6.7B | Comparable to CodeLlama-34B | Comparable to CodeLlama-34B | Comparable to CodeLlama-34B |
| DeepSeek-Coder-Instruct-33B | Outperforms GPT3.5-turbo | Comparable to GPT3.5-turbo | - |

For detailed benchmark results, please refer to [Performance and Benchmarks](#2.2).

Sources: [README.md:30-43]()

## Model Deployment Options

The DeepSeek Coder models support various deployment options to accommodate different hardware and performance requirements.

```mermaid
flowchart TD
    subgraph "Deployment Methods"
        HF["Hugging Face<br>Transformers"] --> VLLM["High-throughput vLLM<br>Inference"]
        HF --> Quantized["Quantized Models<br>GGUF/GPTQ"]
    end
    
    subgraph "Hardware Adaptations"
        VLLM --> TP["Tensor Parallelism<br>Multi-GPU deployment"]
        Quantized --> CPU["CPU Inference<br>Limited resources"]
        Quantized --> ConsumerGPU["Consumer GPU<br>Limited VRAM"]
    end
```

Sources: [README.md:333-382](). [README.md:386-417]()

## Model License and Availability

All DeepSeek Coder models are available for download from Hugging Face and support commercial use. The models are subject to the Model License, while the code in the repository is licensed under the MIT License.

Sources: [README.md:423-426]()

## Conclusion

DeepSeek Coder models represent a family of code language models designed specifically for software development tasks. Available in different sizes and variants, they offer state-of-the-art performance for code completion, code insertion, repository-level understanding, and interactive assistance. The models support a wide range of programming languages and can be deployed through various methods depending on hardware availability and performance requirements.

For more detailed information about these models, refer to:
- [Architecture](#2.1) - Detailed technical architecture information
- [Performance and Benchmarks](#2.2) - Comprehensive benchmark results
- [Usage and Inference Methods](#3) - How to use the models for different tasks

---

