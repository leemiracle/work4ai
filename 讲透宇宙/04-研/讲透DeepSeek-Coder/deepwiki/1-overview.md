<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-Coder · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a technical introduction to DeepSeek Coder, a system of code language models designed for advanced code generation, comprehension, and manipulation tasks. DeepSeek Coder includes models ranging from 1B to 33B parameters, supports multiple inference methods, and offers state-of-the-art performance on code generation benchmarks.

For detailed information about specific model architectures, see [Architecture](#2.1). For usage instructions and inference methods, see [Usage and Inference Methods](#3).

## System Description

DeepSeek Coder consists of a family of transformer-based language models specialized for code, trained from scratch on 2 trillion tokens. The training data comprises 87% code and 13% natural language content in both English and Chinese. The models support over 80 programming languages and are designed for tasks ranging from basic code completion to complex cross-file code generation.

The system offers both base models and instruction-tuned variants:
- **Base Models**: Optimized for code completion, infilling, and project-level understanding
- **Instruct Models**: Fine-tuned specifically for interactive code generation through chat interfaces

The models are available in multiple parameter sizes to accommodate different resource constraints and performance requirements:

| Model Size | Variants             | Context Window | Primary Use Cases                         |
|------------|----------------------|----------------|------------------------------------------|
| 1B         | Base                 | 16K tokens     | Lightweight code completion               |
| 5.7B       | Base                 | 16K tokens     | Medium-scale code generation              |
| 6.7B       | Base, Instruct       | 16K tokens     | Versatile code generation and instruction |
| 33B        | Base, Instruct       | 16K tokens     | High-performance code generation          |

Sources: [README.md:11-27]()

## Architecture Overview

DeepSeek Coder follows a modular system architecture that enables flexibility in deployment and usage:

```mermaid
flowchart TB
    subgraph "DeepSeekCoderSystem"
        direction TB
        
        subgraph "CoreModels"
            BaseModels["Base Models<br>(1B/5.7B/6.7B/33B)"]
            InstructModels["Instruct Models<br>(6.7B/33B)"]
            
            BaseModels -->|"Instruction<br>Fine-tuning"| InstructModels
        end
        
        subgraph "InferenceMethods"
            CodeCompletion["Code Completion<br>AutoModelForCausalLM.generate()"]
            CodeInsertion["Code Insertion<br>FIM tokens"]
            ChatInference["Chat Inference<br>apply_chat_template()"]
            RepoCompletion["Repository Completion<br>Multi-file context"]
            
            BaseModels --> CodeCompletion
            BaseModels --> CodeInsertion
            BaseModels --> RepoCompletion
            InstructModels --> ChatInference
        end
        
        subgraph "EvaluationSystem"
            HumanEval["HumanEval<br>Python & Multilingual"]
            MBPP["MBPP<br>Python Problems"]
            DS1000["DS-1000<br>Data Science"]
            LeetCode["LeetCode<br>Contest Problems"]
        end
        
        subgraph "FinetuningSystem"
            DeepSpeedZero3["DeepSpeed Zero3<br>finetune_deepseekcoder.py"]
            TrainingData["Training Data<br>instruction/output JSON"]
        end
    end
```

Sources: [README.md:11-27](), [README.md:66-166](), [README.md:273-316]()

## Model Training Workflow

DeepSeek Coder models are trained through a multi-stage process to achieve optimal performance for code-related tasks:

```mermaid
flowchart LR
    subgraph "DataCreation"
        direction TB
        GithubData["GitHub Code<br>Repositories"] -->|"Filtering & Cleaning"| FilteredData["Filtered Code Data"]
        FilteredData -->|"Dependency Parsing"| DependencySorted["Dependency-Sorted Files"]
        DependencySorted -->|"Concatenation &<br>Deduplication"| ProcessedData["Processed Training Data"]
    end
    
    subgraph "TrainingPipeline"
        direction TB
        PretrainingStep1["Initial Pretraining<br>1.8T tokens, 4K window"] -->|"87% code<br>13% text"| BaseModels["Base Models<br>4K context"]
        BaseModels -->|"Extended Pretraining<br>200B tokens, 16K window"| ExtendedModels["Extended Base Models<br>16K context"]
        ExtendedModels -->|"Instruction Finetuning<br>2B tokens"| InstructModels["Instruct Models"]
    end
    
    ProcessedData -->|"Training Data"| PretrainingStep1
```

Sources: [README.md:46-63]()

## Inference Methods

DeepSeek Coder supports several inference methods to accommodate different use cases:

### 1. Code Completion

The base models excel at completing code from comments or partial implementations, generating coherent and contextually appropriate code continuations.

```mermaid
sequenceDiagram
    participant User
    participant Tokenizer as "AutoTokenizer"
    participant Model as "AutoModelForCausalLM"
    
    User->>+Tokenizer: Input prompt/code
    Tokenizer->>+Model: Tokenized input
    Model->>-Tokenizer: Generated token IDs
    Tokenizer->>-User: Completed code
```

Sources: [README.md:74-100]()

### 2. Code Insertion (Fill-in-the-Middle)

The models support filling gaps in existing code using special FIM tokens to mark the beginning, hole, and end of the context.

```mermaid
flowchart TD
    Input["Input with FIM tokens<br>⟨｜fim▁begin｜⟩...⟨｜fim▁hole｜⟩...⟨｜fim▁end｜⟩"] -->|"Tokenization"| TokenizedInput["Tokenized Input"]
    TokenizedInput -->|"model.generate()"| Generated["Generated Completion"]
    Generated -->|"Extraction"| FilledCode["Code with Gap Filled"]
```

Sources: [README.md:102-127]()

### 3. Chat Model Inference

The instruction-tuned models are designed for interactive code generation through a chat interface, using a specific template format.

```mermaid
flowchart LR
    UserMessage["User Message<br>{role: 'user', content: '...'}"] -->|"apply_chat_template()"| FormattedPrompt["Formatted Prompt"]
    FormattedPrompt -->|"model.generate()"| Response["Model Response"]
    Response -->|"Decode & Extract"| FinalOutput["Final Output"]
```

Sources: [README.md:129-175]()

### 4. Repository-Level Completion

DeepSeek Coder can understand and complete code across multiple files in a repository, leveraging its 16K context window to maintain coherence between related files.

```mermaid
flowchart TD
    RepoFiles["Multiple Files<br>With Dependencies"] -->|"Concatenation"| ConcatenatedInput["Concatenated Context"]
    ConcatenatedInput -->|"model.generate()"| CompletedCode["Completed Repository Code"]
```

Sources: [README.md:177-272]()

## Evaluation Framework

DeepSeek Coder includes a comprehensive evaluation system to measure performance across standard coding benchmarks:

| Benchmark | Description | Focus Area | Metrics |
|-----------|-------------|------------|---------|
| HumanEval | 164 hand-written programming problems | Algorithm implementation | pass@k |
| MultiPL-E | HumanEval translated to multiple languages | Cross-language capabilities | pass@k |
| MBPP | 974 Python programming problems | Basic Python scripting | pass@k |
| DS-1000 | Data science-specific problems | Data manipulation libraries | pass@k |
| LeetCode | Competitive programming problems | Algorithm efficiency | pass@k |

Sources: [README.md:30-43](), [README.md:319-332]()

## Fine-tuning Capabilities

DeepSeek Coder provides a fine-tuning system built on DeepSpeed for efficient adaptation to specific domains or tasks:

```mermaid
flowchart TD
    subgraph "FinetuningSystem"
        direction TB
        TrainingData["Training Data<br>instruction/output JSON"] -->|"Data Preparation"| PreparedData["Preprocessed Data"]
        PreparedData -->|"finetune_deepseekcoder.py"| Finetuning["DeepSpeed Zero3 Training"]
        
        subgraph "DeepSpeedConfig"
            Zero3["ZeRO Stage 3"]
            CPUOffload["CPU Offloading"]
            MixedPrecision["BF16 Mixed Precision"]
            GradCheckpointing["Gradient Checkpointing"]
        end
        
        DeepSpeedConfig --> Finetuning
        Finetuning --> FinetunedModel["Fine-tuned Model"]
    end
```

Sources: [README.md:273-316]()

## Inference Deployment Options

DeepSeek Coder models can be deployed for inference using various methods depending on performance and resource requirements:

### Standard Inference with Hugging Face

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-6.7b-base", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-6.7b-base", trust_remote_code=True, torch_dtype=torch.bfloat16).cuda()
```

### High-throughput Inference with vLLM

For scenarios requiring higher throughput, vLLM provides optimized inference capabilities:

```mermaid
flowchart TD
    ModelSelection["Model Selection<br>deepseek-ai/deepseek-coder-*"] --> vLLM["vLLM Initialization"]
    vLLM -->|"Tensor Parallelism"| ParallelInference["Parallel Inference Engine"]
    Prompts["Batch of Prompts"] --> ParallelInference
    ParallelInference --> Results["Generated Results"]
```

Sources: [README.md:333-382]()

## Supported Programming Languages

DeepSeek Coder supports a wide range of programming languages (over 80), including but not limited to:

- Python, JavaScript, TypeScript, Java, C, C++, C#, Go
- Ruby, Rust, PHP, Scala, Swift, Kotlin
- HTML, CSS, SQL, Shell scripting
- Domain-specific languages like GLSL, Verilog, and more

For the complete list of supported languages, refer to the [Model details](#2).

Sources: [README.md:27-28]()

---

