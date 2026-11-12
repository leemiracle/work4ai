<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/specter · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a comprehensive overview of the SPECTER system, including its architecture, components, and interfaces. SPECTER (Document-level Representation Learning using Citation-informed Transformers) is a machine learning system that generates embeddings for scientific documents using citation relationships during training.

For detailed instructions on installation and setup, see [Installation & Setup](#2). For immediate usage examples, see [Quick Start](#3). For comprehensive usage documentation, see [User Guide](#4).

## Purpose and Scope

SPECTER generates vector representations (embeddings) of scientific documents by leveraging both textual content (title and abstract) and citation relationships. Unlike standard language models that only consider text, SPECTER incorporates citation networks during training to produce embeddings that capture semantic relationships between papers.

The system serves two primary functions:
- **Inference**: Generate embeddings for new scientific documents
- **Training**: Train custom models using citation-informed learning

## System Architecture

SPECTER provides multiple interfaces for different use cases, all built around a core transformer-based model architecture.

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        HF["HuggingFace Interface<br/>AutoModel/AutoTokenizer"]
        Scripts["Repository Scripts<br/>embed.py, embed_papers_hf.py"]
        API["Public APIs<br/>Semantic Scholar"]
    end
    
    subgraph "Core Components"
        Model["SPECTER Model<br/>allenai/specter"]
        Tokenizer["BERT Tokenizer<br/>allenai/specter"]
        ModelFiles["Model Files<br/>model.tar.gz"]
    end
    
    subgraph "Data Processing"
        MetadataProcessor["Metadata Processing<br/>metadata.json"]
        EmbeddingGenerator["Embedding Generation<br/>result.last_hidden_state"]
        OutputFormatter["Output Formatting<br/>output.jsonl"]
    end
    
    subgraph "Training Infrastructure"
        DataUtils["Data Utilities<br/>create_training_files.py"]
        TrainingScript["Training Scripts<br/>run-exp-simple.sh"]
        ConfigFiles["Configuration<br/>simple.jsonnet"]
    end
    
    HF --> Model
    Scripts --> Model
    API --> Model
    
    Model --> Tokenizer
    Model --> ModelFiles
    
    Scripts --> MetadataProcessor
    MetadataProcessor --> EmbeddingGenerator
    EmbeddingGenerator --> OutputFormatter
    
    DataUtils --> TrainingScript
    TrainingScript --> ConfigFiles
    TrainingScript --> Model
```

Sources: [README.md:1-220]()

### Core Model Components

```mermaid
graph LR
    subgraph "Input Processing"
        TitleAbstract["Title + Abstract<br/>title + sep_token + abstract"]
        TokenizerInput["Tokenizer Input<br/>max_length=512"]
        ModelInput["Model Input<br/>inputs dict"]
    end
    
    subgraph "Model Architecture"
        BERTEmbeddings["BERT Embeddings<br/>SciBERT base"]
        TransformerLayers["Transformer Layers<br/>scalar_mix"]
        PoolingLayer["Pooling Layer<br/>average pooling"]
    end
    
    subgraph "Output Generation"
        HFOutput["HuggingFace Output<br/>last_hidden_state[:, 0, :]"]
        RepoOutput["Repository Output<br/>scalar mix + pooling"]
        EmbeddingVector["Embedding Vector<br/>768 dimensions"]
    end
    
    TitleAbstract --> TokenizerInput
    TokenizerInput --> ModelInput
    ModelInput --> BERTEmbeddings
    BERTEmbeddings --> TransformerLayers
    TransformerLayers --> PoolingLayer
    PoolingLayer --> HFOutput
    PoolingLayer --> RepoOutput
    HFOutput --> EmbeddingVector
    RepoOutput --> EmbeddingVector
```

Sources: [README.md:28-44](), [README.md:66-69]()

## Data Flow

### Inference Pipeline

The system processes scientific documents through a standardized pipeline regardless of the interface used:

| Stage | HuggingFace Interface | Repository Interface | Public API |
|-------|----------------------|---------------------|------------|
| Input Format | Python dict with title/abstract | `metadata.json` + `sample.ids` | HTTP request |
| Tokenization | `AutoTokenizer.from_pretrained('allenai/specter')` | Built-in tokenizer | Pre-processed |
| Model Loading | `AutoModel.from_pretrained('allenai/specter')` | `model.tar.gz` | Server-side |
| Embedding Extraction | `result.last_hidden_state[:, 0, :]` | Scalar mix + pooling | API response |
| Output Format | NumPy array | `output.jsonl` | JSON response |

### Training Data Flow

```mermaid
graph TB
    subgraph "Raw Data"
        Papers["Papers<br/>title, abstract"]
        Citations["Citation Network<br/>data.json"]
        Metadata["Metadata<br/>metadata.json"]
    end
    
    subgraph "Data Processing"
        CreateTrainingFiles["create_training_files.py<br/>--data-dir --metadata --outdir"]
        TripletSampler["Triplet Sampler<br/>positive/negative sampling"]
        PickledFiles["Pickled Files<br/>data-train.p, data-val.p"]
    end
    
    subgraph "Training"
        TrainingScript["run-exp-simple.sh<br/>--train-path --dev-path"]
        ModelTraining["Model Training<br/>simple.jsonnet config"]
        ModelOutput["Model Output<br/>model-output/ directory"]
    end
    
    Papers --> CreateTrainingFiles
    Citations --> CreateTrainingFiles
    Metadata --> CreateTrainingFiles
    
    CreateTrainingFiles --> TripletSampler
    TripletSampler --> PickledFiles
    
    PickledFiles --> TrainingScript
    TrainingScript --> ModelTraining
    ModelTraining --> ModelOutput
```

Sources: [README.md:149-196]()

## Interface Comparison

SPECTER provides three distinct interfaces, each optimized for different use cases:

### HuggingFace Interface
- **Entry Point**: `AutoModel.from_pretrained('allenai/specter')`
- **Script**: `scripts/embed_papers_hf.py`
- **Embedding Method**: CLS token from final layer
- **Use Case**: Python integration, batch processing
- **Performance**: Slightly higher than paper results

### Repository Interface  
- **Entry Point**: `scripts/embed.py`
- **Model Loading**: `model.tar.gz`
- **Embedding Method**: Scalar mix + average pooling
- **Use Case**: Reproducing paper results, custom configurations
- **Dependencies**: AllenNLP, custom environment

### Public API Interface
- **Entry Point**: Semantic Scholar API endpoints
- **Access**: HTTP requests
- **Use Case**: Pre-computed embeddings, production applications
- **Note**: Different model version than repository

Sources: [README.md:14-70](), [README.md:139-143]()

## Key Technical Specifications

| Component | Specification |
|-----------|--------------|
| Model Base | SciBERT (BERT-base) |
| Input Length | 512 tokens maximum |
| Embedding Dimension | 768 |
| Supported Formats | JSON, JSONL |
| Training Framework | AllenNLP, PyTorch Lightning |
| Inference Backend | PyTorch, HuggingFace Transformers |

## Training Approach

SPECTER uses citation-informed learning where:
- **Positive Examples**: Papers with direct citations (`count=5`)
- **Hard Negatives**: Papers with indirect citations (`count=1`) 
- **Easy Negatives**: Unrelated papers
- **Sampling Strategy**: Configurable via `--ratio_hard_negatives`

The training data structure in `data.json` follows this format:
```json
{
  "docid1": {
    "docid11": {"count": 1},
    "docid12": {"count": 5}
  }
}
```

Sources: [README.md:160-172]()

## Evaluation

SPECTER performance is measured using the SciDocs benchmark, which evaluates document-level representations across multiple tasks including classification, citation prediction, and recommendation.

For detailed evaluation procedures, see [Evaluation](#8).

Sources: [README.md:60-64](), [README.md:199-205]()

---

