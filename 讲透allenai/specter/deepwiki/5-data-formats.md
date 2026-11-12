<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/specter · page 5 Data Formats · fetched 2026-10-26 -->

# Data Formats

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/sample-metadata.json](data/sample-metadata.json)
- [data/sample.ids](data/sample.ids)
- [data/training/metadata.json](data/training/metadata.json)

</details>



This document describes the data formats used throughout the SPECTER system, including input paper metadata, training data structures, and output embedding formats. It covers the JSON schemas, file structures, and data flow patterns used for training citation-informed document embeddings.

For information about the data processing pipeline that transforms these formats, see [Data Processing](#6.2). For details about model training procedures, see [Training Models](#4.2).

## Input Data Formats

### Paper Metadata Format

SPECTER uses a standardized JSON format for paper metadata that serves as the primary input for both training and inference. Each paper is represented as a JSON object with required fields for identification and content.

```mermaid
graph TB
    subgraph "Paper Metadata Schema"
        PaperID["paper_id<br/>SHA1 hash identifier"]
        Title["title<br/>Paper title string"]
        Abstract["abstract<br/>Full abstract text"]
        Optional["Optional Fields<br/>venue, authors, year"]
    end
    
    subgraph "File Formats"
        MetadataJSON["metadata.json<br/>Complete dataset"]
        SampleJSON["sample-metadata.json<br/>Sample subset"]
        IDsFile["sample.ids<br/>Paper ID list"]
    end
    
    PaperID --> MetadataJSON
    Title --> MetadataJSON
    Abstract --> MetadataJSON
    Optional --> MetadataJSON
    
    MetadataJSON --> SampleJSON
    PaperID --> IDsFile
    
    style PaperID fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MetadataJSON fill:#e1f5fe,stroke:#333,stroke-width:2px
```

**Paper Metadata Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paper_id` | string | Yes | SHA1 hash identifier (40 characters) |
| `title` | string | Yes | Complete paper title |
| `abstract` | string | Yes | Full abstract text |
| `venue` | string | No | Publication venue |
| `authors` | array | No | List of author names |
| `year` | integer | No | Publication year |

**Example Structure:**
```json
{
  "000feefa7f77907933e5b29fe7e2cd5ff6410418": {
    "paper_id": "000feefa7f77907933e5b29fe7e2cd5ff6410418",
    "title": "Computational Rationalization: The Inverse Equilibrium Problem",
    "abstract": "Modeling the purposeful behavior of imperfect agents from a small number of observations is a challenging task..."
  }
}
```

Sources: [data/training/metadata.json:1-86](), [data/sample-metadata.json:1-277]()

### Paper ID Lists

Paper identifiers are stored in simple text files with one SHA1 hash per line. These files are used to define dataset splits and specify subsets of papers for processing.

```mermaid
graph LR
    subgraph "ID File Format"
        IDFile["sample.ids"]
        IDList["Paper ID List<br/>One per line<br/>SHA1 format"]
    end
    
    subgraph "Usage Patterns"
        TrainSplit["train.ids<br/>Training papers"]
        ValSplit["validation.ids<br/>Validation papers"]
        TestSplit["test.ids<br/>Test papers"]
    end
    
    IDFile --> IDList
    IDList --> TrainSplit
    IDList --> ValSplit
    IDList --> TestSplit
```

**Format Specification:**
- One paper ID per line
- SHA1 hash format (40 hexadecimal characters)
- UTF-8 encoding
- Unix line endings preferred

Sources: [data/sample.ids:1-56]()

## Training Data Formats

### Citation Network Data

The citation network forms the foundation for creating training triplets. Citations are represented as directed relationships between papers, typically stored in formats that support efficient graph operations.

```mermaid
graph TB
    subgraph "Citation Data Flow"
        RawCitations["Raw Citations<br/>paper_id -> cited_paper_id"]
        CitationGraph["Citation Graph<br/>Directed relationships"]
        TripletSampling["Triplet Sampling<br/>anchor, positive, negative"]
    end
    
    subgraph "Triplet Structure"
        Anchor["Anchor Paper<br/>Query paper"]
        Positive["Positive Paper<br/>Cited by anchor"]
        Negative["Negative Paper<br/>Not cited by anchor"]
    end
    
    RawCitations --> CitationGraph
    CitationGraph --> TripletSampling
    TripletSampling --> Anchor
    TripletSampling --> Positive
    TripletSampling --> Negative
    
    style TripletSampling fill:#fff3e0,stroke:#333,stroke-width:2px
    style Anchor fill:#e8f5e8,stroke:#333,stroke-width:2px
    style Positive fill:#e8f5e8,stroke:#333,stroke-width:2px
    style Negative fill:#ffe8e8,stroke:#333,stroke-width:2px
```

### Training Instance Format

Training instances are created from paper triplets and formatted for consumption by the model training pipeline. Each instance contains the text inputs and relationship labels.

```mermaid
graph LR
    subgraph "Training Instance Schema"
        QueryText["query_text<br/>Title + Abstract"]
        CandidateText["candidate_text<br/>Title + Abstract"]
        Label["label<br/>1 (positive) or 0 (negative)"]
    end
    
    subgraph "Data Reader Processing"
        Tokenization["BERT Tokenization<br/>WordPiece encoding"]
        Padding["Sequence Padding<br/>Fixed length tensors"]
        Batching["Batch Formation<br/>GPU-friendly format"]
    end
    
    QueryText --> Tokenization
    CandidateText --> Tokenization
    Label --> Tokenization
    
    Tokenization --> Padding
    Padding --> Batching
```

**Training Instance Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `query_text` | string | Concatenated title and abstract of anchor paper |
| `candidate_text` | string | Concatenated title and abstract of candidate paper |
| `label` | integer | 1 for positive pairs, 0 for negative pairs |

Sources: Referenced from system architecture diagrams

## Output Data Formats

### Document Embeddings

SPECTER produces fixed-dimensional vector representations of papers. The embedding format depends on the interface used for generation.

```mermaid
graph TB
    subgraph "Embedding Output Formats"
        HFEmbeddings["HuggingFace Format<br/>torch.Tensor or numpy.ndarray"]
        RepoEmbeddings["Repository Format<br/>JSON or pickle serialization"]
        APIEmbeddings["API Format<br/>REST JSON response"]
    end
    
    subgraph "Embedding Properties"
        Dimensions["768 dimensions<br/>BERT-base size"]
        Normalization["L2 normalized<br/>Unit vectors"]
        DataType["float32 precision<br/>IEEE 754 format"]
    end
    
    HFEmbeddings --> Dimensions
    RepoEmbeddings --> Dimensions
    APIEmbeddings --> Dimensions
    
    Dimensions --> Normalization
    Normalization --> DataType
    
    style Dimensions fill:#e3f2fd,stroke:#333,stroke-width:2px
```

**Embedding Specifications:**

| Property | Value | Description |
|----------|-------|-------------|
| Dimensions | 768 | BERT-base hidden size |
| Data Type | float32 | 32-bit floating point |
| Normalization | L2 normalized | Unit vector magnitude |
| Range | [-1, 1] | Normalized value range |

### Serialization Formats

Embeddings can be serialized in multiple formats depending on the use case and storage requirements.

```mermaid
graph LR
    subgraph "Serialization Options"
        JSON["JSON Format<br/>Human readable"]
        Pickle["Pickle Format<br/>Python native"]
        NPZ["NumPy Format<br/>Compressed arrays"]
        HDF5["HDF5 Format<br/>Large datasets"]
    end
    
    subgraph "Use Cases"
        WebAPI["Web APIs<br/>JSON preferred"]
        Research["Research Code<br/>Pickle/NumPy"]
        Production["Production Systems<br/>HDF5 efficient"]
    end
    
    JSON --> WebAPI
    Pickle --> Research
    NPZ --> Research
    HDF5 --> Production
```

Sources: Inferred from system architecture and common ML practices

## Configuration Data Formats

### Training Configuration

Training configurations are specified using JSON or JSONNET formats, defining model hyperparameters, data paths, and training procedures.

```mermaid
graph TB
    subgraph "Configuration Schema"
        ModelConfig["model<br/>Architecture parameters"]
        DataConfig["dataset_reader<br/>Data loading settings"]
        TrainConfig["trainer<br/>Training hyperparameters"]
        ValidationConfig["validation<br/>Evaluation settings"]
    end
    
    subgraph "Format Options"
        JSONNet["JSONNET Format<br/>simple.jsonnet"]
        JSON["JSON Format<br/>config.json"]
    end
    
    ModelConfig --> JSONNet
    DataConfig --> JSONNet
    TrainConfig --> JSONNet
    ValidationConfig --> JSONNet
    
    JSONNet --> JSON
    
    style JSONNet fill:#f3e5f5,stroke:#333,stroke-width:2px
```

**Configuration Categories:**

| Section | Purpose | Key Parameters |
|---------|---------|----------------|
| `model` | Model architecture | hidden_size, num_layers, dropout |
| `dataset_reader` | Data loading | max_sequence_length, batch_size |
| `trainer` | Training process | learning_rate, epochs, optimizer |
| `validation` | Evaluation | validation_metric, patience |

Sources: Referenced from training infrastructure descriptions

## Data Flow Architecture

The following diagram illustrates how different data formats flow through the SPECTER system from raw inputs to final embeddings.

```mermaid
graph TB
    subgraph "Raw Data"
        PaperMeta["metadata.json<br/>Paper information"]
        Citations["Citation Network<br/>Graph relationships"]
        PaperIDs["*.ids files<br/>Dataset splits"]
    end
    
    subgraph "Processing Pipeline"
        TripletGen["create_training_files.py<br/>Triplet generation"]
        DataReader["specter.data readers<br/>Instance creation"]
        Tokenizer["BERT Tokenizer<br/>Text preprocessing"]
    end
    
    subgraph "Training Data"
        TrainingInst["Training Instances<br/>JSON lines format"]
        TokenizedData["Tokenized Batches<br/>PyTorch tensors"]
    end
    
    subgraph "Model Output"
        Embeddings["Document Embeddings<br/>768-dim vectors"]
        SerializedEmb["Serialized Output<br/>Multiple formats"]
    end
    
    PaperMeta --> TripletGen
    Citations --> TripletGen
    PaperIDs --> TripletGen
    
    TripletGen --> DataReader
    DataReader --> TrainingInst
    
    TrainingInst --> Tokenizer
    Tokenizer --> TokenizedData
    
    TokenizedData --> Embeddings
    Embeddings --> SerializedEmb
    
    style TripletGen fill:#fff3e0,stroke:#333,stroke-width:2px
    style DataReader fill:#e8f5e8,stroke:#333,stroke-width:2px
    style Embeddings fill:#e3f2fd,stroke:#333,stroke-width:2px
```

Sources: [data/training/metadata.json:1-86](), [data/sample-metadata.json:1-277](), [data/sample.ids:1-56](), system architecture diagrams

---

