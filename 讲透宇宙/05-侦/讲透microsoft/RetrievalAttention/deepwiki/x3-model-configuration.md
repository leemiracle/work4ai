<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · extra page Model Configuration · fetched 2026-10-26 -->

# Model Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark/LongBench/config/model2maxlen.json](benchmark/LongBench/config/model2maxlen.json)
- [benchmark/LongBench/config/model2path.json](benchmark/LongBench/config/model2path.json)

</details>



This document covers the model configuration system used by RetroInfer, which defines model path mappings and maximum sequence length settings for supported language models. The configuration enables the system to locate and properly configure different model variants for inference and evaluation.

For information about dataset-specific configurations, see [Dataset Configuration](#4.2.2). For general setup instructions, see [Environment Setup](#4.1).

## Configuration Files Overview

The model configuration system consists of two primary JSON configuration files that define model metadata and constraints:

```mermaid
graph TB
    subgraph "Model Configuration System"
        MODEL2PATH["model2path.json<br/>Model Path Mappings"]
        MODEL2MAXLEN["model2maxlen.json<br/>Maximum Length Settings"]
    end
    
    subgraph "Supported Models"
        LLAMA31["llama-3.1-8b"]
        LLAMA3["llama-3-8b-1048k"]
        QWEN7["qwen2.5-7b"]
        QWEN72["qwen2.5-72b"]
    end
    
    subgraph "Model Properties"
        PATHS["HuggingFace Model Paths"]
        MAXLENS["Maximum Sequence Lengths"]
    end
    
    MODEL2PATH --> PATHS
    MODEL2MAXLEN --> MAXLENS
    
    LLAMA31 --> MODEL2PATH
    LLAMA3 --> MODEL2PATH
    QWEN7 --> MODEL2PATH
    QWEN72 --> MODEL2PATH
    
    LLAMA31 --> MODEL2MAXLEN
    LLAMA3 --> MODEL2MAXLEN
    QWEN7 --> MODEL2MAXLEN
    QWEN72 --> MODEL2MAXLEN
```

Sources: [benchmark/LongBench/config/model2path.json:1-6](), [benchmark/LongBench/config/model2maxlen.json:1-6]()

## Model Path Configuration

The `model2path.json` file maps internal model identifiers to their corresponding HuggingFace model repository paths. This configuration enables the system to resolve model names to their actual locations for loading.

### Configuration Structure

| Model Identifier | HuggingFace Path |
|------------------|------------------|
| `llama-3-8b-1048k` | `gradientai/Llama-3-8B-Instruct-Gradient-1048k` |
| `llama-3.1-8b` | `meta-llama/Llama-3.1-8B-Instruct` |
| `qwen2.5-7b` | `Qwen/Qwen2.5-7B-Instruct` |
| `qwen2.5-72b` | `Qwen/Qwen2.5-72B-Instruct` |

### Path Resolution Flow

```mermaid
graph LR
    subgraph "Configuration Loading"
        CONFIG_LOADER["Config Loader"]
        MODEL2PATH_JSON["model2path.json"]
        CONFIG_LOADER --> MODEL2PATH_JSON
    end
    
    subgraph "Model Resolution"
        MODEL_ID["Model Identifier<br/>(e.g., llama-3.1-8b)"]
        PATH_LOOKUP["Path Lookup"]
        HF_PATH["HuggingFace Path<br/>(e.g., meta-llama/Llama-3.1-8B-Instruct)"]
        
        MODEL_ID --> PATH_LOOKUP
        PATH_LOOKUP --> HF_PATH
    end
    
    subgraph "Model Loading"
        MODEL_LOADER["Model Loader"]
        LOADED_MODEL["Loaded Model Instance"]
        
        HF_PATH --> MODEL_LOADER
        MODEL_LOADER --> LOADED_MODEL
    end
    
    MODEL2PATH_JSON --> PATH_LOOKUP
```

Sources: [benchmark/LongBench/config/model2path.json:1-6]()

## Maximum Length Configuration

The `model2maxlen.json` file defines the maximum sequence length for each model during inference and evaluation. This configuration ensures that input sequences do not exceed model-specific constraints.

### Length Specifications

All currently supported models are configured with a maximum sequence length of 130,000 tokens:

| Model | Maximum Length |
|-------|----------------|
| `llama-3-8b-1048k` | 130,000 |
| `llama-3.1-8b` | 130,000 |
| `qwen2.5-7b` | 130,000 |
| `qwen2.5-72b` | 130,000 |

### Length Validation Process

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT_TEXT["Input Text"]
        TOKENIZER["Tokenizer"]
        TOKEN_COUNT["Token Count"]
        
        INPUT_TEXT --> TOKENIZER
        TOKENIZER --> TOKEN_COUNT
    end
    
    subgraph "Length Validation"
        MODEL2MAXLEN_JSON["model2maxlen.json"]
        MAX_LENGTH["Maximum Length<br/>(130,000)"]
        LENGTH_CHECK["Length Check"]
        
        MODEL2MAXLEN_JSON --> MAX_LENGTH
        TOKEN_COUNT --> LENGTH_CHECK
        MAX_LENGTH --> LENGTH_CHECK
    end
    
    subgraph "Processing Decision"
        VALID["Valid Input<br/>(≤ 130,000 tokens)"]
        TRUNCATE["Truncate Input<br/>(> 130,000 tokens)"]
        
        LENGTH_CHECK --> VALID
        LENGTH_CHECK --> TRUNCATE
    end
    
    subgraph "Model Inference"
        INFERENCE_ENGINE["Inference Engine"]
        
        VALID --> INFERENCE_ENGINE
        TRUNCATE --> INFERENCE_ENGINE
    end
```

Sources: [benchmark/LongBench/config/model2maxlen.json:1-6]()

## Supported Models

The configuration system currently supports four language models across two model families:

### Llama Models

- **llama-3.1-8b**: Meta's Llama 3.1 8B Instruct model
- **llama-3-8b-1048k**: Gradient AI's extended-context Llama 3 8B model with 1M+ token support

### Qwen Models

- **qwen2.5-7b**: Qwen 2.5 7B Instruct model
- **qwen2.5-72b**: Qwen 2.5 72B Instruct model

### Model Characteristics

```mermaid
graph TB
    subgraph "Model Families"
        LLAMA_FAMILY["Llama Family"]
        QWEN_FAMILY["Qwen Family"]
    end
    
    subgraph "Llama Models"
        LLAMA31["llama-3.1-8b<br/>8B parameters<br/>meta-llama/Llama-3.1-8B-Instruct"]
        LLAMA3_1048K["llama-3-8b-1048k<br/>8B parameters<br/>gradientai/Llama-3-8B-Instruct-Gradient-1048k"]
    end
    
    subgraph "Qwen Models"
        QWEN7["qwen2.5-7b<br/>7B parameters<br/>Qwen/Qwen2.5-7B-Instruct"]
        QWEN72["qwen2.5-72b<br/>72B parameters<br/>Qwen/Qwen2.5-72B-Instruct"]
    end
    
    subgraph "Common Properties"
        MAX_LEN["Max Length: 130,000 tokens"]
        INSTRUCT_TUNED["Instruction-tuned"]
    end
    
    LLAMA_FAMILY --> LLAMA31
    LLAMA_FAMILY --> LLAMA3_1048K
    QWEN_FAMILY --> QWEN7
    QWEN_FAMILY --> QWEN72
    
    LLAMA31 --> MAX_LEN
    LLAMA3_1048K --> MAX_LEN
    QWEN7 --> MAX_LEN
    QWEN72 --> MAX_LEN
    
    LLAMA31 --> INSTRUCT_TUNED
    LLAMA3_1048K --> INSTRUCT_TUNED
    QWEN7 --> INSTRUCT_TUNED
    QWEN72 --> INSTRUCT_TUNED
```

Sources: [benchmark/LongBench/config/model2path.json:1-6](), [benchmark/LongBench/config/model2maxlen.json:1-6]()

## Configuration Integration

The model configuration files are integrated into the broader RetroInfer system through the benchmarking and evaluation framework. The configuration system provides a centralized way to manage model metadata across different evaluation scenarios.

### Configuration Loading Workflow

```mermaid
graph LR
    subgraph "Configuration Files"
        MODEL2PATH_FILE["model2path.json"]
        MODEL2MAXLEN_FILE["model2maxlen.json"]
    end
    
    subgraph "Config Processing"
        CONFIG_LOADER_FUNC["generate_config()"]
        JSON_PARSER["JSON Parser"]
        
        MODEL2PATH_FILE --> JSON_PARSER
        MODEL2MAXLEN_FILE --> JSON_PARSER
        JSON_PARSER --> CONFIG_LOADER_FUNC
    end
    
    subgraph "System Integration"
        BENCHMARK_SYSTEM["Benchmark System"]
        EVAL_SCRIPTS["Evaluation Scripts"]
        INFERENCE_ENGINE["Inference Engine"]
        
        CONFIG_LOADER_FUNC --> BENCHMARK_SYSTEM
        CONFIG_LOADER_FUNC --> EVAL_SCRIPTS
        CONFIG_LOADER_FUNC --> INFERENCE_ENGINE
    end
    
    subgraph "Runtime Usage"
        MODEL_SELECTION["Model Selection"]
        LENGTH_VALIDATION["Length Validation"]
        PATH_RESOLUTION["Path Resolution"]
        
        BENCHMARK_SYSTEM --> MODEL_SELECTION
        EVAL_SCRIPTS --> LENGTH_VALIDATION
        INFERENCE_ENGINE --> PATH_RESOLUTION
    end
```

Sources: [benchmark/LongBench/config/model2path.json:1-6](), [benchmark/LongBench/config/model2maxlen.json:1-6]()

## Usage Context

The model configuration system serves as the foundation for:

- **Benchmark Evaluation**: Defining which models to evaluate and their constraints
- **Inference Setup**: Resolving model paths for loading and initialization
- **Input Validation**: Ensuring input sequences respect model-specific length limits
- **Multi-model Support**: Enabling seamless switching between different model variants

The configuration files are located in the `benchmark/LongBench/config/` directory and are automatically loaded by the evaluation and inference systems when needed.

Sources: [benchmark/LongBench/config/model2path.json:1-6](), [benchmark/LongBench/config/model2maxlen.json:1-6]()

---

