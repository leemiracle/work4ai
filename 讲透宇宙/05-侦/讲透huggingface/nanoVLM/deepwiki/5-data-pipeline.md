<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/nanoVLM · page 5 Data Pipeline · fetched 2026-10-26 -->

# Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/collators.py](data/collators.py)
- [data/custom_transforms.py](data/custom_transforms.py)
- [data/datasets.py](data/datasets.py)
- [data/processors.py](data/processors.py)

</details>



The data pipeline system handles data loading, preprocessing, and batch preparation for training and inference in nanoVLM. This system transforms raw multimodal datasets into properly formatted batches that can be consumed by the vision-language model during training and evaluation.

For information about the specific dataset implementations, see [Datasets](#5.1). For details about data processing utilities and collators, see [Data Processing](#5.2).

## Overview

The data pipeline consists of three main components that work together to prepare multimodal data for model consumption:

```mermaid
graph TD
    subgraph "Raw Data Sources"
        CAULDRON["The Cauldron Dataset<br/>42 VQA sub-datasets"]
        MMSTAR["MMStar Dataset<br/>Evaluation benchmark"]
    end
    
    subgraph "Data Processing Layer"
        GET_TOK["get_tokenizer()<br/>processors.py"]
        GET_IMG["get_image_processor()<br/>processors.py"]
        TOKENIZER["AutoTokenizer<br/>Text tokenization"]
        IMG_PROC["Image Transforms<br/>Resize + ToTensor"]
    end
    
    subgraph "Dataset Classes"
        VQA_DS["VQADataset<br/>datasets.py:8-53"]
        MMSTAR_DS["MMStarDataset<br/>datasets.py:56-89"]
    end
    
    subgraph "Batch Preparation"
        BASE_COL["BaseCollator<br/>collators.py:4-61"]
        VQA_COL["VQACollator<br/>collators.py:62-88"]
        MMSTAR_COL["MMStarCollator<br/>collators.py:90-112"]
    end
    
    subgraph "Training Input"
        BATCHED_DATA["Batched Tensors<br/>input_ids, attention_mask, labels, images"]
    end
    
    CAULDRON --> VQA_DS
    MMSTAR --> MMSTAR_DS
    
    GET_TOK --> TOKENIZER
    GET_IMG --> IMG_PROC
    
    TOKENIZER --> VQA_DS
    TOKENIZER --> MMSTAR_DS
    IMG_PROC --> VQA_DS
    IMG_PROC --> MMSTAR_DS
    
    VQA_DS --> VQA_COL
    MMSTAR_DS --> MMSTAR_COL
    BASE_COL --> VQA_COL
    BASE_COL --> MMSTAR_COL
    
    VQA_COL --> BATCHED_DATA
    MMSTAR_COL --> BATCHED_DATA
```

**Sources:** [data/processors.py:1-23](), [data/datasets.py:1-90](), [data/collators.py:1-112]()

## Data Processing Components

The data processing layer provides utilities for initializing tokenizers and image processors that are shared across dataset implementations:

| Component | Function | Purpose |
|-----------|----------|---------|
| `get_tokenizer()` | Tokenizer initialization | Handles caching and special token configuration |
| `get_image_processor()` | Image preprocessing | Creates transform pipeline for image normalization |
| `TOKENIZERS_CACHE` | Tokenizer caching | Prevents redundant tokenizer loading |

The `get_tokenizer()` function supports extra special tokens and chat templates, which are essential for multimodal conversation formatting. The image processor applies standard transformations including resizing to a fixed size and tensor conversion.

**Sources:** [data/processors.py:4-16](), [data/processors.py:18-22]()

## Dataset Processing Flow

The dataset classes handle the conversion from raw data samples to processed multimodal inputs:

```mermaid
flowchart TD
    subgraph "VQADataset Processing"
        VQA_RAW["Raw VQA Sample<br/>images: List[PIL.Image]<br/>texts: List[dict]"]
        VQA_IMG["Image Processing<br/>RGB conversion<br/>image_processor()"]
        VQA_TEXT["Text Processing<br/>User/Assistant messages<br/>Image token injection"]
        VQA_OUT["VQA Output<br/>images: List[Tensor]<br/>text_data: List[dict]"]
    end
    
    subgraph "MMStarDataset Processing"
        MM_RAW["Raw MMStar Sample<br/>image: PIL.Image<br/>question: str<br/>answer: str"]
        MM_IMG["Image Processing<br/>RGB conversion<br/>image_processor()"]
        MM_TEXT["Text Processing<br/>Question formatting<br/>Answer extraction"]
        MM_OUT["MMStar Output<br/>image: Tensor<br/>text_data: List[dict]"]
    end
    
    VQA_RAW --> VQA_IMG
    VQA_RAW --> VQA_TEXT
    VQA_IMG --> VQA_OUT
    VQA_TEXT --> VQA_OUT
    
    MM_RAW --> MM_IMG
    MM_RAW --> MM_TEXT
    MM_IMG --> MM_OUT
    MM_TEXT --> MM_OUT
```

**Sources:** [data/datasets.py:18-53](), [data/datasets.py:66-89]()

### Image Token Injection

Both dataset classes inject special image tokens into the text content to indicate where visual features should be integrated. The number of image tokens is determined by `mp_image_token_length`, which corresponds to the modality projector's output sequence length:

- **VQADataset**: Multiplies image tokens by the number of images in the sample [data/datasets.py:48]()
- **MMStarDataset**: Uses a fixed number of image tokens for single-image samples [data/datasets.py:84]()

## Batch Preparation Architecture

The collator system transforms individual dataset samples into properly formatted training batches:

```mermaid
graph TD
    subgraph "BaseCollator Core Logic"
        PREFIX["prefix_len Calculation<br/>Chat template analysis<br/>collators.py:7-11"]
        CHAT_TEMPLATE["apply_chat_template()<br/>Message formatting<br/>collators.py:19-24"]
        MASK_LOGIC["Loss Mask Creation<br/>Assistant token masking<br/>collators.py:25-41"]
        PADDING["Sequence Padding<br/>Max length alignment<br/>collators.py:51-60"]
    end
    
    subgraph "VQACollator Specialization"
        VQA_BATCH["VQA Batch Input<br/>images: List[List[Tensor]]<br/>text_data: List[List[dict]]"]
        VQA_IMG_STACK["Image Stacking<br/>Flatten and stack<br/>collators.py:72-73"]
        VQA_LABELS["Label Creation<br/>Causal LM shifting<br/>collators.py:79-81"]
        VQA_OUTPUT["VQA Batch Output<br/>image, input_ids, attention_mask, labels"]
    end
    
    subgraph "MMStarCollator Specialization"
        MM_BATCH["MMStar Batch Input<br/>image: List[Tensor]<br/>text_data: List[List[dict]]"]
        MM_IMG_STACK["Image Stacking<br/>Direct stacking<br/>collators.py:99"]
        MM_MASK["Input Masking<br/>Evaluation format<br/>collators.py:103-105"]
        MM_OUTPUT["MMStar Batch Output<br/>images, input_ids, attention_mask, labels"]
    end
    
    PREFIX --> CHAT_TEMPLATE
    CHAT_TEMPLATE --> MASK_LOGIC
    MASK_LOGIC --> PADDING
    
    VQA_BATCH --> VQA_IMG_STACK
    VQA_BATCH --> PADDING
    PADDING --> VQA_LABELS
    VQA_IMG_STACK --> VQA_OUTPUT
    VQA_LABELS --> VQA_OUTPUT
    
    MM_BATCH --> MM_IMG_STACK
    MM_BATCH --> PADDING
    PADDING --> MM_MASK
    MM_IMG_STACK --> MM_OUTPUT
    MM_MASK --> MM_OUTPUT
```

**Sources:** [data/collators.py:4-61](), [data/collators.py:62-88](), [data/collators.py:90-112]()

### Loss Masking Strategy

The `BaseCollator` implements sophisticated loss masking to ensure only assistant tokens contribute to training loss:

1. **Prefix Length Calculation**: Determines the number of tokens before assistant content in chat templates [data/collators.py:7-11]()
2. **Assistant Token Identification**: Locates assistant responses in the conversation flow [data/collators.py:35-38]()
3. **Mask Application**: Sets mask values to 1 for assistant tokens, 0 for all other tokens [data/collators.py:25-41]()

### Batch Output Formats

The collators produce different output formats optimized for their specific use cases:

| Collator | Output Keys | Purpose |
|----------|-------------|---------|
| `VQACollator` | `image`, `input_ids`, `attention_mask`, `labels` | Training with causal language modeling loss |
| `MMStarCollator` | `images`, `input_ids`, `attention_mask`, `labels` | Evaluation with masked inputs |

**Sources:** [data/collators.py:83-88](), [data/collators.py:107-112]()

## Integration Points

The data pipeline integrates with other system components through well-defined interfaces:

- **Training Loop**: Consumes batched tensors from collators for model forward passes
- **Model Architecture**: Receives properly formatted image tensors and tokenized text sequences
- **Configuration System**: Uses parameters like `mp_image_token_length` to coordinate with model components
- **Evaluation Framework**: Provides formatted batches for benchmark testing

**Sources:** [data/datasets.py:9-13](), [data/datasets.py:57-61](), [data/collators.py:63-65](), [data/collators.py:91-92]()

---

