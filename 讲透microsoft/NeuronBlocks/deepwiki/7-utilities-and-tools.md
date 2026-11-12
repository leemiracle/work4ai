<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/NeuronBlocks · page 7 Utilities and Tools · fetched 2026-10-26 -->

# Utilities and Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataset/get_glove.sh](dataset/get_glove.sh)
- [dataset/get_glove_6B.sh](dataset/get_glove_6B.sh)
- [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json](model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json)
- [register_block.py](register_block.py)
- [tools/calculate_auc.py](tools/calculate_auc.py)
- [utils/corpus_utils.py](utils/corpus_utils.py)

</details>



This section covers the supporting utilities, tools, and helper functions that facilitate development, testing, and data processing within the NeuronBlocks toolkit. These utilities provide essential functionality for corpus processing, embedding management, model registration, evaluation metrics calculation, and automated testing workflows.

For information about the core training and evaluation pipeline, see [Training and Evaluation](#4). For details about data preprocessing within the main pipeline, see [Data Processing](#4.3).

## Overview

The NeuronBlocks toolkit includes several categories of utilities that support the main machine learning pipeline:

```mermaid
graph TB
    subgraph "Data Utilities"
        CORPUS["corpus_utils.py<br/>Core Data Processing"]
        EMBED_DL["get_glove.sh<br/>Embedding Downloads"]
        BATCH["get_batches()<br/>Batch Creation"]
        LOAD_EMB["load_embedding()<br/>Embedding Loading"]
    end
    
    subgraph "Development Tools"
        REGISTER["register_block.py<br/>Block Registration"]
        CALC_AUC["calculate_auc.py<br/>Metric Calculation"]
        AUTO_TEST["Automated Testing<br/>Quality Assurance"]
    end
    
    subgraph "Model Utilities"
        MODEL_VIZ["Model Visualization<br/>Architecture Validation"]
        CONFIG_VAL["Configuration Validation<br/>JSON Schema Checking"]
    end
    
    subgraph "Core Pipeline Integration"
        TRAIN["train.py"]
        TEST["test.py"]
        PREDICT["predict.py"]
    end
    
    %% Data flow connections
    EMBED_DL --> LOAD_EMB
    LOAD_EMB --> CORPUS
    CORPUS --> BATCH
    BATCH --> TRAIN
    BATCH --> TEST
    BATCH --> PREDICT
    
    %% Development workflow
    REGISTER --> TRAIN
    CALC_AUC --> TEST
    AUTO_TEST --> REGISTER
    
    %% Model utilities
    MODEL_VIZ --> CONFIG_VAL
    CONFIG_VAL --> TRAIN
    
    style CORPUS fill:#e3f2fd
    style BATCH fill:#e8f5e8
    style REGISTER fill:#fff3e0
```

Sources: [utils/corpus_utils.py:1-443](), [tools/calculate_auc.py:1-48](), [register_block.py:1-64](), [dataset/get_glove.sh:1-21]()

## Data Processing Utilities

The `corpus_utils.py` module serves as the primary data processing utility, providing functions for embedding loading, text preprocessing, batch creation, and tensor operations.

### Embedding Management

The `load_embedding()` function supports multiple embedding formats and provides flexible loading capabilities:

```mermaid
flowchart TD
    START["load_embedding()"] --> FORMAT{Format Type}
    
    FORMAT -->|"glove"| GLOVE["GloVe Text Format<br/>Line-by-line parsing"]
    FORMAT -->|"word2vec"| W2V["Word2Vec Format<br/>KeyedVectors.load_word2vec_format()"]
    FORMAT -->|"fasttext"| FT["FastText Format<br/>FastText.load_fasttext_format()"]
    
    subgraph "File Type Processing"
        GLOVE --> GLOVE_PARSE["Parse space-separated<br/>word + vector values"]
        W2V --> W2V_BIN{Binary vs Text}
        FT --> FT_BIN{Binary vs Text}
        
        W2V_BIN -->|binary=True| W2V_LOAD["Load binary format"]
        W2V_BIN -->|binary=False| W2V_TEXT["Load text format"]
        FT_BIN -->|binary| FT_LOAD["Load FastText binary"]
        FT_BIN -->|text| FT_TEXT["Load FastText text"]
    end
    
    subgraph "Output Processing"
        GLOVE_PARSE --> FILTER{word_set filtering}
        W2V_LOAD --> FILTER
        W2V_TEXT --> FILTER
        FT_LOAD --> FILTER
        FT_TEXT --> FILTER
        
        FILTER -->|word_set provided| SUBSET["Filtered embedding_dict"]
        FILTER -->|word_set=None| FULL["Complete embedding_dict"]
    end
    
    SUBSET --> RETURN["Return embedding_dict"]
    FULL --> RETURN
```

Sources: [utils/corpus_utils.py:28-72]()

Key parameters for `load_embedding()`:
- `embedding_path`: Path to embedding file
- `embedding_dim`: Expected vector dimensionality  
- `format`: One of 'glove', 'word2vec', 'fasttext'
- `file_type`: 'text' or 'binary'
- `word_set`: Optional set for vocabulary filtering

### Batch Processing Pipeline

The `get_batches()` function transforms preprocessed data into training-ready batches with proper padding and tensor conversion:

```mermaid
graph TD
    subgraph "Input Data Structure"
        DATA["data<br/>{string1: {word1: [...], postag1: [...]},<br/>string2: {word1: [...], postag1: [...]}}"]
        LENGTH["length<br/>{string1: [...], string2: [...]}"]
        TARGET["target<br/>[...]"]
    end
    
    subgraph "Batch Processing Steps"
        PERM["Permutation<br/>corpus_permutation() if permutate=True"]
        PAD_SETUP["Padding Setup<br/>Set pad_ids for input_types and target"]
        BATCH_SPLIT["Batch Splitting<br/>Split corpus into batch_size chunks"]
        TENSOR_PAD["Tensor Padding<br/>cut_and_padding() for sequence alignment"]
    end
    
    subgraph "Output Tensors"
        DATA_BATCH["data_batches<br/>List of padded batch dicts"]
        LENGTH_BATCH["length_batches<br/>Sequence length info per batch"]
        TARGET_BATCH["target_batches<br/>Padded target tensors"]
    end
    
    DATA --> PERM
    LENGTH --> PERM
    TARGET --> PERM
    PERM --> PAD_SETUP
    PAD_SETUP --> BATCH_SPLIT
    BATCH_SPLIT --> TENSOR_PAD
    TENSOR_PAD --> DATA_BATCH
    TENSOR_PAD --> LENGTH_BATCH
    TENSOR_PAD --> TARGET_BATCH
    
    style DATA_BATCH fill:#e8f5e8
    style TENSOR_PAD fill:#e3f2fd
```

Sources: [utils/corpus_utils.py:177-399]()

The `get_batches()` function handles multiple data scenarios:
- **Character-level data**: Applies 2D padding for [batch_size, seq_len, word_len] tensors
- **Sequence tagging**: Pads target sequences to match input sequence lengths
- **Classification**: Handles scalar targets without sequence padding
- **Multi-GPU support**: Converts to `torch.LongTensor` for `nn.DataParallel` compatibility

### Array and Sequence Utilities

Several helper functions support data manipulation:

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `split_array()` | Chunk arrays into fixed-size pieces | `arr`, `n`, `small_chunk_threshold` |
| `split_array_averagely()` | Split arrays into equal-sized chunks | `arr`, `m` |
| `cut_and_padding()` | Truncate or pad sequences to fixed length | `seq`, `max_len`, `pad` |
| `get_seq_mask()` | Generate padding masks for sequences | `seq_len`, `max_seq_len` |
| `to_categorical()` | Convert class indices to one-hot vectors | `y`, `nb_classes` |

Sources: [utils/corpus_utils.py:75-135](), [utils/corpus_utils.py:402-418]()

## Development and Registration Tools

### Block Registration System

The `register_block.py` utility automates the process of registering custom neural network blocks within the Block Zoo architecture:

```mermaid
flowchart LR
    subgraph "Block Registration Workflow"
        INPUT["Custom Block<br/>MyBlock.py"]
        FIND["get_block_path()<br/>Locate block file in block_zoo/"]
        VALIDATE["Path Validation<br/>Check if block exists"]
        WRITE["write_file()<br/>Add import statements"]
        INIT["Update __init__.py<br/>Auto-import MyBlock, MyBlockConf"]
    end
    
    subgraph "Block Zoo Structure"
        ROOT["block_zoo/__init__.py"]
        SUB["block_zoo/subdir/__init__.py"]
        BLOCK["block_zoo/subdir/MyBlock.py"]
    end
    
    INPUT --> FIND
    FIND --> VALIDATE
    VALIDATE -->|"Found"| WRITE
    VALIDATE -->|"Not Found"| ERROR["Exception:<br/>Block file does not exist"]
    WRITE --> INIT
    INIT --> ROOT
    INIT --> SUB
    
    BLOCK --> FIND
    
    style WRITE fill:#e8f5e8
    style ERROR fill:#ffebee
```

Sources: [register_block.py:8-55]()

Usage example:
```bash
python register_block.py --block_name MyCustomBlock
```

The registration process:
1. **Search**: `get_block_path()` recursively searches `block_zoo/` subdirectories
2. **Validation**: Ensures the `.py` file exists before registration
3. **Import Generation**: Creates import statements for both the block class and configuration class
4. **Hierarchy Update**: Updates all relevant `__init__.py` files in the directory hierarchy

### Evaluation Metrics Tools

The `calculate_auc.py` utility provides standalone AUC calculation for model evaluation:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--input_file` | TSV file with predictions and labels | `predictions.tsv` |
| `--predict_index` | Column index for model predictions | `0` |
| `--label_index` | Column index for ground truth labels | `1` |
| `--header` | Whether file contains header row | `--header` |

Sources: [tools/calculate_auc.py:7-48]()

Example usage:
```bash
python tools/calculate_auc.py --input_file results.tsv --predict_index 0 --label_index 1 --header
```

## Embedding Download Utilities

The toolkit includes shell scripts for automated embedding downloads:

### GloVe Embedding Scripts

Two scripts are provided for different GloVe embedding sets:

| Script | Embeddings Downloaded | Size |
|--------|----------------------|------|
| `get_glove.sh` | GloVe 840B.300d + 6B | Large-scale embeddings |
| `get_glove_6B.sh` | GloVe 6B only | Smaller embedding set |

Sources: [dataset/get_glove.sh:1-21](), [dataset/get_glove_6B.sh:1-16]()

Both scripts:
1. Create a `GloVe/` directory structure
2. Download embeddings via `curl` from Stanford NLP servers
3. Extract using `unzip`
4. Clean up temporary ZIP files

The downloaded embeddings integrate with the embedding loading system via:
```json
{
  "data_paths": {
    "pre_trained_emb": "dataset/GloVe/glove.6B.100d.txt"
  }
}
```

Sources: [model_zoo/nlp_tasks/slot_tagging/conf_slot_tagging.json:13]()

## Integration with Core Pipeline

These utilities integrate seamlessly with the main NeuronBlocks pipeline:

```mermaid
graph LR
    subgraph "Preprocessing Phase"
        DOWNLOAD["Embedding Download<br/>get_glove.sh"]
        LOAD["Embedding Loading<br/>load_embedding()"]
        PROCESS["Data Processing<br/>corpus_utils functions"]
    end
    
    subgraph "Training Phase"
        BATCH["Batch Creation<br/>get_batches()"]
        TRAIN["Training Loop<br/>train.py"]
        VALID["Validation<br/>Metrics calculation"]
    end
    
    subgraph "Development Phase"
        REGISTER["Block Registration<br/>register_block.py"]
        TEST["Automated Testing<br/>Quality checks"]
        EVAL["Evaluation<br/>calculate_auc.py"]
    end
    
    DOWNLOAD --> LOAD
    LOAD --> PROCESS
    PROCESS --> BATCH
    BATCH --> TRAIN
    TRAIN --> VALID
    
    REGISTER --> TEST
    TEST --> TRAIN
    VALID --> EVAL
    
    style BATCH fill:#e3f2fd
    style REGISTER fill:#fff3e0
    style EVAL fill:#e8f5e8
```

Sources: [utils/corpus_utils.py:177-399](), [register_block.py:38-55](), [tools/calculate_auc.py:30-34]()

The utilities provide essential infrastructure that enables:
- **Flexible data loading** supporting multiple embedding formats
- **Efficient batch processing** with automatic padding and tensor conversion  
- **Streamlined development** through automated block registration
- **Comprehensive evaluation** with standalone metric calculation tools
- **Reproducible experiments** through standardized data processing pipelines

---

