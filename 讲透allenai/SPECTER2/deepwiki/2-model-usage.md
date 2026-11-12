<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SPECTER2 · page 2 Model Usage · fetched 2026-10-26 -->

# Model Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides comprehensive guidance on using SPECTER2 models to generate scientific document embeddings. It covers the model architecture, loading methods, task-specific adapters, and practical implementation examples.

SPECTER2 is designed for generating embeddings from scientific papers represented as title-abstract pairs, with specialized adapters for different downstream tasks. For information about installing the system dependencies, see [Installation](#4). For details about the production API service, see [Production API](#3).

## Model Architecture Overview

SPECTER2 follows a modular architecture with a base transformer model and task-specific adapters trained for different embedding purposes.

### Base Model and Adapter System

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT["Paper: {title, abstract}"]
        CONCAT["title + [SEP] + abstract"]
        TOKENIZE["AutoTokenizer.from_pretrained()"]
    end
    
    subgraph "Model Architecture"
        BASE["specter2_base<br/>Base Transformer Model"]
        
        subgraph "Task Adapters"
            PROX["specter2_proximity<br/>Retrieval & Search"]
            CLASS["specter2_classification<br/>Classification Tasks"]
            REGR["specter2_regression<br/>Regression Tasks"] 
            QUERY["specter2_adhoc_query<br/>Short Text Queries"]
        end
    end
    
    subgraph "Output Processing"
        HIDDEN["last_hidden_state"]
        EMBED["embeddings = output[:, 0, :]<br/>768-dimensional vectors"]
    end
    
    INPUT --> CONCAT
    CONCAT --> TOKENIZE
    TOKENIZE --> BASE
    
    BASE --> PROX
    BASE --> CLASS
    BASE --> REGR
    BASE --> QUERY
    
    PROX --> HIDDEN
    CLASS --> HIDDEN
    REGR --> HIDDEN
    QUERY --> HIDDEN
    
    HIDDEN --> EMBED
```

The system uses `AutoAdapterModel.from_pretrained()` to load the base model and `model.load_adapter()` to activate task-specific functionality.

**Sources:** [README.md:19-21](), [README.md:52-77]()

### Task-Specific Adapter Selection

| Task Type | Adapter Model | Use Case | Input Format |
|-----------|---------------|----------|--------------|
| Retrieval/Search | `allenai/specter2_proximity` | Link prediction, nearest neighbor search, candidate paper encoding | Title + Abstract |
| Classification | `allenai/specter2_classification` | Features for linear classifiers | Title + Abstract |
| Regression | `allenai/specter2_regression` | Features for linear regressors | Title + Abstract |
| Adhoc Query | `allenai/specter2_adhoc_query` | Short text query encoding for search | Raw text queries |

**Sources:** [README.md:43-50]()

## Loading Methods

SPECTER2 models can be loaded through two primary methods: HuggingFace Hub and AWS S3 direct download.

### HuggingFace Hub Loading

```mermaid
sequenceDiagram
    participant USER as "User Code"
    participant HF as "HuggingFace Hub"
    participant TOKENIZER as "AutoTokenizer"
    participant MODEL as "AutoAdapterModel"
    participant ADAPTER as "Task Adapter"
    
    USER->>TOKENIZER: "from_pretrained('allenai/specter2_base')"
    HF->>TOKENIZER: "Load tokenizer"
    
    USER->>MODEL: "from_pretrained('allenai/specter2_base')"
    HF->>MODEL: "Load base model"
    
    USER->>MODEL: "load_adapter('allenai/specter2', load_as='proximity')"
    HF->>ADAPTER: "Load adapter weights"
    MODEL->>ADAPTER: "Activate adapter"
    
    USER->>MODEL: "model(**inputs)"
    MODEL->>USER: "embeddings output"
```

The HuggingFace approach uses the `transformers` library with `AutoTokenizer` and the `adapters` library with `AutoAdapterModel` for dynamic adapter loading.

**Sources:** [README.md:52-77]()

### AWS S3 Direct Loading

```mermaid
graph LR
    subgraph "S3 Download Process"
        S3["AWS S3<br/>s3://ai2-s2-research-public/specter2_0/"]
        TAR["specter2_0.tar.gz"]
        EXTRACT["tar -xvf"]
    end
    
    subgraph "Local File Structure"
        BASE_DIR["specter2/models/base/"]
        ADAPTER_DIR["specter2/models/adapters/"]
        
        subgraph "Adapter Types"
            PROX_ADAPTER["proximity/"]
            CLASS_ADAPTER["classification/"]
            REGR_ADAPTER["regression/"]
            QUERY_ADAPTER["adhoc_query/"]
        end
    end
    
    subgraph "Model Loading"
        LOCAL_TOKENIZER["AutoTokenizer.from_pretrained('specter2/models/base')"]
        LOCAL_MODEL["AutoAdapterModel.from_pretrained('specter2/models/base')"]
        LOAD_ADAPTER["model.load_adapter('specter2/models/adapters/proximity')"]
    end
    
    S3 --> TAR
    TAR --> EXTRACT
    EXTRACT --> BASE_DIR
    EXTRACT --> ADAPTER_DIR
    
    ADAPTER_DIR --> PROX_ADAPTER
    ADAPTER_DIR --> CLASS_ADAPTER
    ADAPTER_DIR --> REGR_ADAPTER
    ADAPTER_DIR --> QUERY_ADAPTER
    
    BASE_DIR --> LOCAL_TOKENIZER
    BASE_DIR --> LOCAL_MODEL
    PROX_ADAPTER --> LOAD_ADAPTER
```

**Sources:** [README.md:79-113]()

## Input Processing and Tokenization

### Document Format Requirements

SPECTER2 expects scientific papers as dictionaries with `title` and `abstract` fields. The preprocessing concatenates these fields with the tokenizer's separator token.

```mermaid
flowchart TD
    subgraph "Input Document Structure"
        DOC["{'title': str, 'abstract': str}"]
    end
    
    subgraph "Text Concatenation Process"
        TITLE["paper['title']"]
        SEP["tokenizer.sep_token"]
        ABSTRACT["paper.get('abstract') or ''"]
        CONCAT["title + sep_token + abstract"]
    end
    
    subgraph "Tokenization Parameters"
        PARAMS["padding=True<br/>truncation=True<br/>max_length=512<br/>return_tensors='pt'<br/>return_token_type_ids=False"]
    end
    
    subgraph "Model Input"
        INPUTS["tokenizer(text_batch, **params)"]
        OUTPUT["model(**inputs)"]
        EMBEDDING["output.last_hidden_state[:, 0, :]"]
    end
    
    DOC --> TITLE
    DOC --> ABSTRACT
    TITLE --> CONCAT
    SEP --> CONCAT
    ABSTRACT --> CONCAT
    
    CONCAT --> PARAMS
    PARAMS --> INPUTS
    INPUTS --> OUTPUT
    OUTPUT --> EMBEDDING
```

The system uses the first token (`[:, 0, :]`) of the last hidden state as the document embedding, producing 768-dimensional vectors.

**Sources:** [README.md:66-76](), [README.md:102-112]()

## Batch Processing for Multiple Tasks

For applications requiring multiple task-specific embeddings, SPECTER2 provides a batch processing interface through the SciRepEval Model class.

### Multi-Task Processing Architecture

```mermaid
graph TB
    subgraph "SciRepEval Model Class"
        MODEL_INSTANCE["Model(variant='adapters')"]
        BASE_CHECKPOINT["base_checkpoint='allenai/specter2'"]
        ADAPTERS_DICT["adapters_load_from=adapters_dict"]
        ALL_TASKS["all_tasks=['[CLF]', '[QRY]', '[RGN]', '[PRX]']"]
    end
    
    subgraph "Adapter Configuration"
        CLF["'[CLF]': 'allenai/specter2_classification'"]
        QRY["'[QRY]': 'allenai/specter2_adhoc_query'"]
        RGN["'[RGN]': 'allenai/specter2_regression'"] 
        PRX["'[PRX]': 'allenai/specter2_proximity'"]
    end
    
    subgraph "Processing Pipeline"
        BATCH_INPUT["Input batch of papers"]
        MULTI_EMBED["Multiple task-specific embeddings"]
        GPU_REQUIRED["Requires GPU for efficiency"]
    end
    
    CLF --> ADAPTERS_DICT
    QRY --> ADAPTERS_DICT
    RGN --> ADAPTERS_DICT
    PRX --> ADAPTERS_DICT
    
    BASE_CHECKPOINT --> MODEL_INSTANCE
    ADAPTERS_DICT --> MODEL_INSTANCE
    ALL_TASKS --> MODEL_INSTANCE
    
    MODEL_INSTANCE --> BATCH_INPUT
    BATCH_INPUT --> MULTI_EMBED
    GPU_REQUIRED --> MULTI_EMBED
```

The batch processing approach enables simultaneous generation of embeddings optimized for different downstream tasks from the same input documents.

**Sources:** [README.md:115-123]()

## Implementation Examples

### Basic Single-Task Usage

The most common usage pattern loads a single adapter for a specific task:

```python
# From HuggingFace
tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
model.load_adapter("allenai/specter2", source="hf", load_as="proximity", set_active=True)
```

### Local File Loading

For environments with limited internet access or custom model versions:

```python
# From local S3 download
tokenizer = AutoTokenizer.from_pretrained('specter2/models/base')
model = AutoAdapterModel.from_pretrained('specter2/models/base')
model.load_adapter("specter2/models/adapters/proximity", load_as="proximity", set_active=True)
```

### Multi-Task Configuration

For applications requiring multiple embedding types:

```python
adapters_dict = {
    "[CLF]": "allenai/specter2_classification",
    "[QRY]": "allenai/specter2_adhoc_query", 
    "[RGN]": "allenai/specter2_regression",
    "[PRX]": "allenai/specter2_proximity"
}
model = Model(
    variant="adapters",
    base_checkpoint="allenai/specter2",
    adapters_load_from=adapters_dict,
    all_tasks=["[CLF]", "[QRY]", "[RGN]", "[PRX]"]
)
```

**Sources:** [README.md:52-77](), [README.md:88-113](), [README.md:118-122]()

## Output Format and Dimensionality

SPECTER2 generates 768-dimensional dense vector embeddings suitable for various downstream scientific tasks. The embeddings are extracted from `output.last_hidden_state[:, 0, :]` representing the `[CLS]` token encoding.

These embeddings can be directly used for:
- Similarity computation between papers
- Input features for classification/regression models  
- Retrieval and search applications
- Citation recommendation systems

**Sources:** [README.md:75-76](), [README.md:111-112]()

---

