<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers-research-projects · page 4 Abstractive Summarization (BertAbs) · fetched 2026-10-26 -->

# Abstractive Summarization (BertAbs)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bertabs/README.md](bertabs/README.md)
- [bertabs/__init__.py](bertabs/__init__.py)
- [bertabs/requirements.txt](bertabs/requirements.txt)

</details>



## Purpose and Scope

The BertAbs system implements abstractive text summarization using pretrained encoder models, based on the research paper "Text Summarization with Pretrained Encoders" by Yang Liu and Mirella Lapata. This system provides both research reproduction capabilities for the CNN/Daily Mail dataset and general-purpose document summarization functionality.

For model architecture details, see [BertAbs Model Architecture](#4.1). For training and evaluation workflows, see [BertAbs Training and Evaluation](#4.2). For data processing utilities, see [BertAbs Data Processing](#4.3).

## System Overview

The BertAbs system combines pretrained BERT encoders with transformer decoders to generate abstractive summaries. The implementation supports both research evaluation on standard datasets and practical summarization of arbitrary documents.

### High-Level Architecture

```mermaid
graph TB
    subgraph "BertAbs System"
        INPUT["Input Documents"]
        ENCODER["Pretrained BERT Encoder"]
        DECODER["Transformer Decoder"]
        OUTPUT["Generated Summaries"]
        
        INPUT --> ENCODER
        ENCODER --> DECODER
        DECODER --> OUTPUT
    end
    
    subgraph "Core Components"
        RUN_SCRIPT["run_summarization.py"]
        MODEL_ARCH["modeling_bertabs.py"]
        UTILS["utils_summarization.py"]
        CONFIG["Configuration System"]
    end
    
    subgraph "Evaluation Framework"
        ROUGE["ROUGE Metrics"]
        SCORES["rouge_scores.txt"]
    end
    
    RUN_SCRIPT --> ENCODER
    RUN_SCRIPT --> DECODER
    MODEL_ARCH --> ENCODER
    MODEL_ARCH --> DECODER
    UTILS --> INPUT
    CONFIG --> RUN_SCRIPT
    
    OUTPUT --> ROUGE
    ROUGE --> SCORES
```

**Sources:** [bertabs/README.md:1-62]()

### Code Entity Mapping

```mermaid
graph LR
    subgraph "Entry Points"
        RUN_SUM["run_summarization.py"]
    end
    
    subgraph "Model Implementation"
        MODELING["modeling_bertabs.py"]
        PRETRAINED["Pretrained Weights"]
    end
    
    subgraph "Data Processing"
        UTILS_SUM["utils_summarization.py"]
        DOCUMENTS_DIR["documents_dir parameter"]
        SUMMARIES_OUTPUT["summaries_output_dir parameter"]
    end
    
    subgraph "Evaluation"
        ROUGE_COMP["compute_rouge parameter"]
        ROUGE_FILE["rouge_scores.txt"]
        BATCH_SIZE["batch_size parameter"]
    end
    
    subgraph "Generation Parameters"
        MIN_LEN["min_length parameter"]
        MAX_LEN["max_length parameter"]
        BEAM_SIZE["beam_size parameter"]
        ALPHA["alpha parameter"]
        BLOCK_TRI["block_trigram parameter"]
    end
    
    RUN_SUM --> MODELING
    RUN_SUM --> UTILS_SUM
    RUN_SUM --> ROUGE_COMP
    UTILS_SUM --> DOCUMENTS_DIR
    UTILS_SUM --> SUMMARIES_OUTPUT
    ROUGE_COMP --> ROUGE_FILE
    
    RUN_SUM --> MIN_LEN
    RUN_SUM --> MAX_LEN
    RUN_SUM --> BEAM_SIZE
    RUN_SUM --> ALPHA
    RUN_SUM --> BLOCK_TRI
```

**Sources:** [bertabs/README.md:29-40](), [bertabs/README.md:49-59]()

## Key Components

### Main Execution Script

The `run_summarization.py` script serves as the primary interface for the BertAbs system, supporting both CNN/Daily Mail dataset evaluation and general document summarization.

| Parameter | Purpose | Default/Example |
|-----------|---------|-----------------|
| `documents_dir` | Input documents directory | `$DATA_PATH` |
| `summaries_output_dir` | Output summaries directory | `$SUMMARIES_PATH` |
| `no_cuda` | Disable GPU usage | `false` |
| `batch_size` | Processing batch size | `4` |
| `min_length` | Minimum summary length | `50` |
| `max_length` | Maximum summary length | `200` |
| `beam_size` | Beam search size | `5` |
| `alpha` | Length penalty parameter | `0.95` |
| `block_trigram` | Prevent trigram repetition | `true` |
| `compute_rouge` | Enable ROUGE evaluation | `true` |

**Sources:** [bertabs/README.md:29-40](), [bertabs/README.md:49-59]()

### Model Architecture

The system uses pretrained weights from models trained on CNN/Daily Mail dataset with both extractive and abstractive tasks. The architecture combines:

- **Encoder**: Pretrained BERT model for document understanding
- **Decoder**: Transformer decoder for summary generation
- **Training Strategy**: Sequential extractive then abstractive training

**Sources:** [bertabs/README.md:7-8]()

### Data Processing Pipeline

```mermaid
graph TD
    subgraph "CNN/Daily Mail Processing"
        CNN_TAR["cnn_stories.tgz"]
        DM_TAR["dailymail_stories.tgz"]
        EXTRACT["tar -xvf extraction"]
        UNIFIED["Unified stories folder"]
    end
    
    subgraph "General Document Processing"
        DOC_DIR["documents_dir"]
        UTILS_PROC["utils_summarization.py processing"]
        BATCH_PROC["Batch processing"]
    end
    
    subgraph "Output Generation"
        SUMMARY_DIR["summaries_output_dir"]
        ROUGE_EVAL["ROUGE evaluation"]
        SCORES_FILE["rouge_scores.txt"]
    end
    
    CNN_TAR --> EXTRACT
    DM_TAR --> EXTRACT
    EXTRACT --> UNIFIED
    UNIFIED --> UTILS_PROC
    
    DOC_DIR --> UTILS_PROC
    UTILS_PROC --> BATCH_PROC
    BATCH_PROC --> SUMMARY_DIR
    BATCH_PROC --> ROUGE_EVAL
    ROUGE_EVAL --> SCORES_FILE
```

**Sources:** [bertabs/README.md:20-27](), [bertabs/README.md:46-61]()

## Dependencies and Requirements

The system requires specific dependencies for proper functionality:

| Component | Version/Package | Purpose |
|-----------|----------------|---------|
| `transformers` | `== 4.38.0` | Core transformer models |
| `nltk` | Latest | Text processing utilities |
| `py-rouge` | Latest | ROUGE metric computation |

**Sources:** [bertabs/requirements.txt:1-6]()

## Performance Characteristics

The system provides the following performance characteristics:

- **Evaluation Time**: 30 hours for full CNN/Daily Mail dataset (300,000 texts)
- **Hardware**: Single Tesla V100 GPU with batch size 10
- **GPU Support**: Single GPU inference (multi-GPU not supported)
- **Scalability**: Configurable batch size for memory optimization

**Sources:** [bertabs/README.md:42-43]()

## Research Foundation

The implementation is based on the original PreSumm codebase and reproduces results from "Text Summarization with Pretrained Encoders" research. The system enables:

- **Research Reproduction**: Exact replication of paper results on CNN/Daily Mail
- **General Summarization**: Application to arbitrary document collections
- **Evaluation Framework**: ROUGE-based performance measurement

**Sources:** [bertabs/README.md:3-6]()

---

