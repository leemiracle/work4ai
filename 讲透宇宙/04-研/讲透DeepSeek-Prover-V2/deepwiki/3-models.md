<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-Prover-V2 · page 3 Models · fetched 2026-10-30 -->

# Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DeepSeek_Prover_V2.pdf](DeepSeek_Prover_V2.pdf)
- [README.md](README.md)

</details>



This page provides a comprehensive overview of the available models in the DeepSeek-Prover-V2 system, including their architectures, capabilities, and specifications. For information about the training methodology, see [Training Pipeline](#3.1), and for detailed usage instructions, see [Inference Guide](#3.2).

## Model Overview

DeepSeek-Prover-V2 is a family of large language models specifically designed for formal theorem proving in Lean 4. The system is released in two model sizes: 7B and 671B parameters, each built upon different base models with specialized capabilities for mathematical reasoning.

### Model Variants and Specifications

```mermaid
graph TD
    subgraph "DeepSeek_Prover_V2_Models"
        DSP7B["DeepSeek-Prover-V2-7B"] -->|"Built upon"| DSP15["DeepSeek-Prover-V1.5-Base"]
        DSP671B["DeepSeek-Prover-V2-671B"] -->|"Built upon"| DSV3["DeepSeek-V3-Base"]
    end
    
    DSP15 -->|"Features"| Context["32K token context length"]
    DSV3 -->|"Features"| Reasoning["Advanced reasoning capabilities"]
    
    DSP7B -->|"Performance"| P1["MiniF2F benchmarking"]
    DSP671B -->|"Performance"| P2["MiniF2F: 88.9% pass rate"]
    DSP671B -->|"Performance"| P3["PutnamBench: 49/658 problems solved"]
```

Sources: [README.md:94-103]()

The following table provides a detailed comparison of the two model variants:

| Model | Parameters | Base Model | Context Length | Primary Use Cases |
|-------|------------|------------|----------------|-------------------|
| DeepSeek-Prover-V2-7B | 7 billion | DeepSeek-Prover-V1.5-Base | Up to 32K tokens | Formal theorem proving, moderate complexity problems |
| DeepSeek-Prover-V2-671B | 671 billion | DeepSeek-V3-Base | Standard | Advanced reasoning, complex theorem proving, competition-level problems |

Sources: [README.md:94-96]()

## Model Architecture

The DeepSeek-Prover-V2 models are transformer-based language models optimized for mathematical reasoning tasks, with specific architectural enhancements that enable formal theorem proving capabilities.

### Architecture Components

```mermaid
graph TD
    subgraph "Model_Architecture"
        Input["Input (Theorem Statement)"] --> Tokenizer["Tokenization Layer"]
        Tokenizer --> Embedding["Embedding Layer"]
        Embedding --> Transformer["Transformer Layers"]
        Transformer --> Output["Output Layer"]
        Output --> Decoding["Decoding Layer"]
        Decoding --> Proof["Formal Proof"]
    end
    
    subgraph "Implementation_Entities"
        Code1["AutoTokenizer.from_pretrained()"] --> Tokenizer
        Code2["model.generate()"] --> Transformer
        Code3["tokenizer.batch_decode()"] --> Decoding
    end
    
    subgraph "Model_Variants"
        V1["DeepSeek-Prover-V2-7B (7B parameters)"]
        V2["DeepSeek-Prover-V2-671B (671B parameters)"]
    end
    
    V1 --> Transformer
    V2 --> Transformer
```

Sources: [README.md:94-96](), [README.md:114-163]()

## Model Capabilities

DeepSeek-Prover-V2 models combine informal mathematical reasoning with formal proof construction, enabling them to tackle complex mathematical problems through a process of decomposition, reasoning, and formalization.

### Key Capabilities

```mermaid
flowchart LR
    subgraph "Reasoning_Capabilities"
        InformalReasoning["Informal mathematical reasoning"] --> Decomposition["Theorem decomposition"]
        Decomposition --> Subgoals["Subgoal formulation"]
        Subgoals --> Formalization["Formal proof construction"]
        Formalization --> EndToEnd["End-to-end theorem proving"]
    end
    
    subgraph "Application_Domains"
        HighSchool["High-school competition problems"]
        Undergraduate["Undergraduate mathematics"]
        Benchmark1["MiniF2F benchmark"]
        Benchmark2["PutnamBench"]
        ProverBench["ProverBench"]
    end
    
    EndToEnd --> HighSchool
    EndToEnd --> Undergraduate
    EndToEnd --> Benchmark1
    EndToEnd --> Benchmark2
    EndToEnd --> ProverBench
```

Sources: [README.md:40-67](), [README.md:71-91]()

### Performance Benchmarks

The models have been evaluated on multiple mathematical benchmarks:

- **MiniF2F-test**: DeepSeek-Prover-V2-671B achieves 88.9% pass ratio
- **PutnamBench**: Solves 49 out of 658 problems
- **ProverBench**: Comprehensive evaluation on 325 problems including:
  - 15 AIME competition problems
  - 310 undergraduate-level problems across various mathematical domains

Sources: [README.md:67-68](), [README.md:71-91]()

## Model Inference Process

The following sequence diagram illustrates the typical workflow for using DeepSeek-Prover-V2 models for formal theorem proving:

```mermaid
sequenceDiagram
    participant User
    participant Tokenizer as "AutoTokenizer"
    participant Model as "AutoModelForCausalLM"
    participant Lean4 as "Lean 4 Environment"
    
    User->>Tokenizer: Initialize tokenizer from model_id
    User->>User: Prepare theorem statement in Lean 4
    User->>User: Format as chat prompt
    User->>Tokenizer: Apply chat template
    User->>Model: Load model (device_map="auto")
    Tokenizer->>Model: Send tokenized input
    Model->>Model: Generate response (max_new_tokens=8192)
    Model->>Tokenizer: Return generated tokens
    Tokenizer->>User: Decode to formal proof
    User->>Lean4: Verify proof
```

Sources: [README.md:114-163]()

## Model Integration with Code

This diagram shows how the natural language concepts map to specific code implementations when working with DeepSeek-Prover-V2 models:

```mermaid
graph TD
    subgraph "Code_Implementation"
        Init1["AutoTokenizer.from_pretrained(model_id)"] --> Format["tokenizer.apply_chat_template(chat)"]
        Init2["AutoModelForCausalLM.from_pretrained(model_id)"] --> Generate["model.generate(inputs, max_new_tokens=8192)"]
        Generate --> Decode["tokenizer.batch_decode(outputs)"]
    end
    
    subgraph "Workflow_Concepts"
        Step1["Initialize Prover Model"] --> Step2["Format Theorem as Prompt"]
        Step2 --> Step3["Generate Formal Proof"]
        Step3 --> Step4["Verify in Lean 4"]
    end
    
    Init1 --> Step1
    Init2 --> Step1
    Format --> Step2
    Generate --> Step3
    Decode --> Step4
```

Sources: [README.md:114-163]()

## Accessing the Models

Both DeepSeek-Prover-V2 models are available for download from Hugging Face:

| Model | Download Link |
|-------|---------------|
| DeepSeek-Prover-V2-7B | HuggingFace: deepseek-ai/DeepSeek-Prover-V2-7B |
| DeepSeek-Prover-V2-671B | HuggingFace: deepseek-ai/DeepSeek-Prover-V2-671B |

The models can be directly loaded using the Hugging Face Transformers library as shown in the inference process diagram above.

Sources: [README.md:97-103]()

## Usage Guidelines

When using the DeepSeek-Prover-V2 models for theorem proving:

1. **Context Length**: The 7B model supports up to 32K tokens, making it suitable for longer proofs
2. **Prompt Format**: Include a clear theorem statement formatted in Lean 4 syntax
3. **Proof Planning**: Request a detailed proof plan before the formal proof for better results
4. **Token Generation**: Set a high value for `max_new_tokens` (e.g., 8192) to allow for complete proofs
5. **Model Selection**: Use the 671B model for more complex theorems and competition-level problems

Sources: [README.md:114-163]()

## License Information

The use of DeepSeek-Prover-V2 models is subject to the Model License. For complete details on licensing, see [License and Legal Information](#5).

Sources: [README.md:166]()

---

