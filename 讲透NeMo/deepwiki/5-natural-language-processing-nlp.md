<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo · page 5 Natural Language Processing (NLP) · fetched 2026-10-21 -->

# Natural Language Processing (NLP)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py](nemo/collections/common/tokenizers/sentencepiece_tokenizer.py)
- [nemo/utils/timers.py](nemo/utils/timers.py)

</details>



## Purpose and Scope

This section covers NeMo's traditional Natural Language Processing capabilities, including machine translation, token classification, and text classification models. These models typically follow encoder-decoder or encoder-only architectures and are distinct from the large-scale autoregressive language models.

For large language model (LLM) capabilities such as GPT, Mamba, and other decoder-only models, see [Large Language Models (LLMs)](#3). For multimodal models that combine text with other modalities, see the Multimodal section in [Framework Overview](#1).

---

## NLP Collection Overview

The NLP collection in NeMo provides models and utilities for traditional NLP tasks such as machine translation (MT), named entity recognition (NER), and text classification. These models leverage the core NeMo infrastructure including `ModelPT` for lifecycle management, distributed training strategies, and checkpointing.

**Key Components:**
- **Encoder-Decoder Models**: T5, NMT architectures for sequence-to-sequence tasks
- **Classification Models**: Token-level and sequence-level classification
- **Tokenization**: SentencePiece-based tokenizers with multi-language support
- **Training Infrastructure**: Integration with Megatron-Core for distributed training

```mermaid
graph TB
    subgraph "NLP Collection"
        MT["MT Models<br/>(Encoder-Decoder)"]
        TokenClass["Token Classification<br/>(NER, POS)"]
        TextClass["Text Classification<br/>(Sentiment, Intent)"]
        T5["Megatron T5<br/>(Encoder-Decoder)"]
    end
    
    subgraph "Tokenization Layer"
        SPT["SentencePieceTokenizer"]
        TokenizerSpec["TokenizerSpec Interface"]
        ChatTemplate["ChatTemplateMixin"]
    end
    
    subgraph "Core Infrastructure"
        ModelPT["ModelPT Base Class"]
        Lightning["NeMo Lightning"]
        MegatronStrat["MegatronStrategy"]
    end
    
    subgraph "Data Processing"
        TextDatasets["Text Datasets"]
        Preprocessing["Text Preprocessing"]
        Batching["Dynamic Batching"]
    end
    
    MT --> ModelPT
    TokenClass --> ModelPT
    TextClass --> ModelPT
    T5 --> ModelPT
    
    MT --> SPT
    T5 --> SPT
    TokenClass --> SPT
    
    SPT --> TokenizerSpec
    SPT --> ChatTemplate
    
    ModelPT --> Lightning
    Lightning --> MegatronStrat
    
    TextDatasets --> Preprocessing
    Preprocessing --> Batching
    Batching --> MT
    Batching --> T5
```

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:1-616]()

---

## Tokenization Infrastructure

### SentencePieceTokenizer

The `SentencePieceTokenizer` class provides the primary tokenization mechanism for NLP models in NeMo. It wraps the Google SentencePiece library and extends it with NeMo-specific functionality including special token handling, chat templates, and whitespace normalization.

#### Class Architecture

```mermaid
graph TB
    SPT["SentencePieceTokenizer"]
    TokenizerSpec["TokenizerSpec<br/>(Abstract Interface)"]
    ChatTemplateMixin["ChatTemplateMixin<br/>(Chat Formatting)"]
    SentencePieceProcessor["sentencepiece.SentencePieceProcessor<br/>(Google Library)"]
    
    SPT -->|"inherits"| TokenizerSpec
    SPT -->|"inherits"| ChatTemplateMixin
    SPT -->|"contains"| SentencePieceProcessor
    
    subgraph "Key Methods"
        text_to_tokens["text_to_tokens()<br/>text_to_ids()"]
        ids_to_text["ids_to_text()<br/>tokens_to_text()"]
        special_tokens["add_special_tokens()<br/>special_token_to_id"]
    end
    
    SPT --> text_to_tokens
    SPT --> ids_to_text
    SPT --> special_tokens
```

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:31-46]()

#### Initialization and Configuration

The tokenizer supports two operational modes controlled by the `legacy` parameter:

| Mode | Special Tokens | Use Case |
|------|---------------|----------|
| **Legacy** (`legacy=True`) | Added at runtime via `add_special_tokens()` | Backward compatibility with existing models |
| **Modern** (`legacy=False`) | Defined during SentencePiece training | New models, cleaner architecture |

**Constructor Parameters:**

```mermaid
graph LR
    Init["SentencePieceTokenizer.__init__()"]
    
    subgraph "Required Parameters"
        model_path["model_path<br/>(tokenizer.model file)"]
    end
    
    subgraph "Optional Parameters"
        special_tokens["special_tokens<br/>(dict or list)"]
        legacy["legacy<br/>(bool, default False)"]
        ignore_whitespace["ignore_extra_whitespaces<br/>(bool, default True)"]
        chat_template["chat_template<br/>(dict, optional)"]
        trim_separator["trim_spm_separator_after_special_token<br/>(bool, default True)"]
    end
    
    Init --> model_path
    Init --> special_tokens
    Init --> legacy
    Init --> ignore_whitespace
    Init --> chat_template
    Init --> trim_separator
```

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:47-84]()

#### Text-to-IDs Conversion Flow

The tokenization pipeline handles several edge cases including special tokens, extra whitespaces, and chat formatting:

```mermaid
graph TB
    Input["Input Text or<br/>Chat Messages"]
    
    CheckType{"Input Type?"}
    
    StringPath["String Input"]
    ListPath["List Input<br/>(Chat Messages)"]
    
    ChatTemplate["apply_chat_template()<br/>(from ChatTemplateMixin)"]
    
    TextToIDs["_text_to_ids()"]
    
    CheckLegacy{"legacy mode?"}
    
    LegacyPath["Legacy Processing:<br/>1. Find special tokens<br/>2. Split text at special tokens<br/>3. Encode segments separately<br/>4. Trim SPM separator if needed"]
    
    ModernPath["Modern Processing:<br/>1. Handle extra whitespaces<br/>2. Direct encode via SentencePiece<br/>3. Optional sampling (sample_alpha)"]
    
    CheckWhitespace{"ignore_extra_whitespaces<br/>and removed_extra_spaces?"}
    
    ExtraSpaceHandling["_text_to_ids_extra_space()<br/>Preserve extra space tokens"]
    
    DirectEncode["tokenizer.encode_as_ids()"]
    
    Output["List of Token IDs"]
    
    Input --> CheckType
    CheckType -->|"str"| StringPath
    CheckType -->|"list"| ListPath
    
    ListPath --> ChatTemplate
    ChatTemplate --> Output
    
    StringPath --> TextToIDs
    TextToIDs --> CheckLegacy
    
    CheckLegacy -->|"True"| LegacyPath
    CheckLegacy -->|"False"| ModernPath
    
    LegacyPath --> Output
    
    ModernPath --> CheckWhitespace
    CheckWhitespace -->|"Yes"| ExtraSpaceHandling
    CheckWhitespace -->|"No"| DirectEncode
    
    ExtraSpaceHandling --> Output
    DirectEncode --> Output
```

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:145-250]()

#### Special Token Handling (Legacy Mode)

In legacy mode, special tokens are handled separately from the main vocabulary. The tokenizer maintains two mappings:

```mermaid
graph LR
    subgraph "Special Token Mappings"
        special_token_to_id["special_token_to_id<br/>(dict: str → int)"]
        id_to_special_token["id_to_special_token<br/>(dict: int → str)"]
    end
    
    subgraph "Vocabulary Management"
        original_vocab_size["original_vocab_size<br/>(from SentencePiece model)"]
        vocab_size["vocab_size<br/>(original + special tokens)"]
    end
    
    add_special_tokens["add_special_tokens()"]
    
    add_special_tokens --> special_token_to_id
    add_special_tokens --> id_to_special_token
    add_special_tokens --> vocab_size
    
    original_vocab_size -.->|"immutable"| vocab_size
```

**Example Special Token Properties:**

| Property | Legacy Mode | Modern Mode |
|----------|-------------|-------------|
| `pad_id` | `tokens_to_ids([self.pad_token])[0]` | `tokenizer.pad_id()` |
| `bos_id` | `tokens_to_ids([self.bos_token])[0]` | `tokenizer.bos_id()` |
| `eos_id` | `tokens_to_ids([self.eos_token])[0]` | `tokenizer.eos_id()` |
| `unk_id` | `tokenizer.unk_id()` | `tokenizer.unk_id()` |
| `sep_id`, `cls_id`, `mask_id` | Supported | Raises `NameError` |

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:344-452]()

#### Whitespace Normalization

The tokenizer implements sophisticated whitespace handling to accommodate different training scenarios:

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `removed_extra_spaces` | Detects if model ignores extra spaces | Set by comparing `encode_as_pieces('x  y')` vs `encode_as_pieces('x y')` |
| `ignore_extra_whitespaces` | User-configurable flag | Controls whether to preserve or ignore extra spaces |
| `extra_space_token` | Special marker ('☯') | Used to preserve space positions when needed |
| `space_sensitive` | Detects if model is space-aware | Set by comparing `text_to_tokens('x y')` vs `text_to_tokens('x') + text_to_tokens('y')` |

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:82-84](), [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:229-250]()

#### Chat Template Integration

The tokenizer inherits from `ChatTemplateMixin`, enabling it to format conversational inputs according to model-specific templates (e.g., Llama-style `[INST]` tags, ChatML format):

```mermaid
graph TB
    ChatMessages["Chat Messages<br/>(List of dicts)"]
    
    apply_chat_template["apply_chat_template()"]
    
    Format["Format according to<br/>chat_template config"]
    
    Tokenize["Tokenize formatted string"]
    
    HandleSpecial["Handle special tokens<br/>trim_spm_separator_after_special_token"]
    
    TokenIDs["Final Token IDs"]
    
    ChatMessages --> apply_chat_template
    apply_chat_template --> Format
    Format --> Tokenize
    Tokenize --> HandleSpecial
    HandleSpecial --> TokenIDs
```

**Special Token Trimming:** When `trim_spm_separator_after_special_token=True`, the tokenizer removes the SentencePiece separator (`▁`) that appears immediately after special tokens, preventing patterns like `<INST> ▁who` from becoming `[inst_id, sep_id, who_id]` instead of the desired `[inst_id, who_id]`.

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:24](), [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:119-128](), [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:197-207]()

---

### Creating SentencePiece Models

The `create_spt_model()` function provides a wrapper around SentencePiece training with NeMo-specific defaults and options:

```mermaid
graph TB
    DataFile["data_file<br/>(Raw text corpus)"]
    
    Config["Configuration Parameters"]
    
    subgraph "Core Parameters"
        vocab_size["vocab_size<br/>(Vocabulary size)"]
        sample_size["sample_size<br/>(Training sample size)"]
        tokenizer_type["tokenizer_type<br/>(unigram/bpe/char/word)"]
    end
    
    subgraph "Advanced Parameters"
        character_coverage["character_coverage<br/>(0.0-1.0, default 1.0)"]
        byte_fallback["byte_fallback<br/>(Handle OOV chars)"]
        split_digits["split_digits<br/>(Tokenize digits separately)"]
        split_by_whitespace["split_by_whitespace<br/>(Respect whitespace)"]
        remove_extra_whitespaces["remove_extra_whitespaces<br/>(Normalize spaces)"]
    end
    
    subgraph "Special Tokens"
        bos_eos_pad["bos/eos/pad<br/>(Enable/disable)"]
        control_symbols["control_symbols<br/>(Non-encoded tokens)"]
        user_defined_symbols["user_defined_symbols<br/>(Encoded tokens)"]
    end
    
    SPTrain["sentencepiece.SentencePieceTrainer.Train()"]
    
    Output["tokenizer.model<br/>vocab.txt"]
    
    DataFile --> Config
    
    Config --> vocab_size
    Config --> sample_size
    Config --> tokenizer_type
    Config --> character_coverage
    Config --> byte_fallback
    Config --> split_digits
    Config --> split_by_whitespace
    Config --> remove_extra_whitespaces
    Config --> bos_eos_pad
    Config --> control_symbols
    Config --> user_defined_symbols
    
    vocab_size --> SPTrain
    sample_size --> SPTrain
    tokenizer_type --> SPTrain
    character_coverage --> SPTrain
    byte_fallback --> SPTrain
    split_digits --> SPTrain
    split_by_whitespace --> SPTrain
    remove_extra_whitespaces --> SPTrain
    bos_eos_pad --> SPTrain
    control_symbols --> SPTrain
    user_defined_symbols --> SPTrain
    
    SPTrain --> Output
```

#### Parameter Details

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `data_file` | str | Path to training corpus | Required |
| `vocab_size` | int | Target vocabulary size | Required |
| `sample_size` | int | Max sentences to load (-1 for all) | Required |
| `tokenizer_type` | str | Algorithm: `unigram`, `bpe`, `char`, `word` | `'unigram'` |
| `character_coverage` | float | Charset coverage (0.0-1.0) | 1.0 |
| `do_lower_case` | bool | Lowercase normalization | Required |
| `bos` / `eos` / `pad` | bool | Include special tokens | `False` |
| `control_symbols` | List[str] | Non-encoded control tokens | `None` |
| `user_defined_symbols` | List[str] | Encoded user symbols | `None` |
| `byte_fallback` | bool | Fallback to bytes for `<unk>` | `False` |
| `split_digits` | bool | Separate digit tokens | `False` |
| `split_by_whitespace` | bool | Respect whitespace boundaries | `True` |
| `remove_extra_whitespaces` | bool | Normalize multiple spaces | `False` |

**Output Files:**
- `{output_dir}/tokenizer.model`: SentencePiece binary model
- `{output_dir}/vocab.txt`: BERT-style vocabulary file with `##` prefix for subwords

**Sources:** [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:464-616]()

---

## NLP Model Integration

### ModelPT Integration

NLP models in NeMo inherit from `ModelPT`, which provides:

- **Checkpoint Management**: Save/restore with distributed checkpoint support
- **Configuration System**: Hydra-based configuration with OmegaConf
- **Training Lifecycle**: Integration with PyTorch Lightning
- **Export Capabilities**: ONNX, TorchScript, HuggingFace format conversion

**Typical NLP Model Structure:**

```mermaid
graph TB
    ModelPT["ModelPT Base Class<br/>(Lifecycle Management)"]
    
    NLPModel["NLP Model<br/>(MT, Classification, etc.)"]
    
    subgraph "Model Components"
        Tokenizer["SentencePieceTokenizer"]
        Encoder["Encoder<br/>(Transformer/BERT)"]
        Decoder["Decoder<br/>(Transformer/Seq2Seq)"]
        Head["Task Head<br/>(Classification/Generation)"]
    end
    
    subgraph "Training Components"
        Loss["Loss Function<br/>(CrossEntropy, etc.)"]
        Optimizer["Optimizer<br/>(AdamW, Fused)"]
        Scheduler["LR Scheduler"]
    end
    
    ModelPT -->|"inherits"| NLPModel
    
    NLPModel --> Tokenizer
    NLPModel --> Encoder
    NLPModel --> Decoder
    NLPModel --> Head
    
    NLPModel --> Loss
    NLPModel --> Optimizer
    NLPModel --> Scheduler
    
    subgraph "Data Flow"
        Input["Input Text"] --> Tokenizer
        Tokenizer --> Encoder
        Encoder --> Decoder
        Decoder --> Head
        Head --> Output["Predictions"]
    end
```

**Sources:** Based on architecture diagrams and [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py:1-28]()

---

## Training and Inference

### Training Configuration

NLP models leverage NeMo's experiment manager and training infrastructure:

```mermaid
graph LR
    subgraph "Configuration"
        ModelConfig["model:<br/>- encoder<br/>- decoder<br/>- tokenizer"]
        TrainerConfig["trainer:<br/>- devices<br/>- strategy<br/>- precision"]
        DataConfig["data:<br/>- train_ds<br/>- validation_ds"]
        OptimConfig["optim:<br/>- lr<br/>- weight_decay<br/>- scheduler"]
    end
    
    subgraph "Execution"
        ExpManager["exp_manager:<br/>- checkpointing<br/>- logging<br/>- resume"]
        Trainer["PyTorch Lightning Trainer"]
        Strategy["MegatronStrategy<br/>(for large models)"]
    end
    
    ModelConfig --> Trainer
    TrainerConfig --> Trainer
    DataConfig --> Trainer
    OptimConfig --> Trainer
    
    Trainer --> ExpManager
    Trainer --> Strategy
```

### Tokenization in Training Pipeline

```mermaid
graph TB
    RawData["Raw Text Data"]
    
    Preprocess["Text Preprocessing:<br/>- Normalization<br/>- Cleaning"]
    
    Tokenize["SentencePieceTokenizer:<br/>text_to_ids()"]
    
    Batch["Batch Assembly:<br/>- Padding<br/>- Attention masks<br/>- Position IDs"]
    
    Model["NLP Model:<br/>forward()"]
    
    Loss["Loss Computation"]
    
    Backward["Backward Pass"]
    
    RawData --> Preprocess
    Preprocess --> Tokenize
    Tokenize --> Batch
    Batch --> Model
    Model --> Loss
    Loss --> Backward
```

**Sources:** Based on general NeMo architecture patterns

---

## Common Use Cases

### Machine Translation

Machine translation models in NeMo follow encoder-decoder architectures with SentencePiece tokenization for both source and target languages.

**Key Features:**
- Multi-lingual tokenizers with combined vocabularies
- Beam search decoding
- Length penalty and coverage penalty
- Optional parallel corpus filtering

### Token Classification

Token classification tasks (NER, POS tagging) use encoder-only models with per-token prediction heads.

**Key Features:**
- BIO/BIOES tagging schemes
- Conditional Random Field (CRF) layers
- Subword-to-word alignment
- Entity-level F1 metrics

### Text Classification

Sequence-level classification (sentiment analysis, intent detection) uses pooled encoder representations.

**Key Features:**
- CLS token pooling or mean pooling
- Multi-label classification support
- Hierarchical classification
- Few-shot learning capabilities

**Sources:** Based on NLP collection architecture patterns and [nemo/collections/common/tokenizers/sentencepiece_tokenizer.py]() for tokenization integration

---

## Summary

The NLP collection in NeMo provides a comprehensive framework for traditional NLP tasks:

- **Tokenization**: `SentencePieceTokenizer` with legacy and modern modes, special token handling, and chat template support
- **Model Architecture**: Integration with `ModelPT` for lifecycle management and distributed training
- **Training Infrastructure**: Leverages NeMo Lightning, Megatron strategies, and experiment management
- **Task Coverage**: Machine translation, token classification, text classification, and more

For autoregressive language modeling and large-scale pretraining, refer to [Large Language Models (LLMs)](#3). For speech-related NLP tasks, see [Automatic Speech Recognition (ASR)](#4).

---

