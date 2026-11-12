<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/bi-att-flow · page 3 Data Pipeline · fetched 2026-10-26 -->

# Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [basic/read_data.py](basic/read_data.py)
- [squad/prepro.py](squad/prepro.py)

</details>



The data pipeline system manages the complete flow of data from raw SQuAD JSON files through preprocessing, storage, and loading into the BiDAF model. This system handles tokenization, embedding integration, data filtering, batching, and multi-GPU data distribution. For model-specific data transformations, see [Model Architecture](#2.1). For training-specific data handling, see [Training Pipeline](#4.1).

## Data Flow Overview

The data pipeline transforms raw question-answer datasets through several stages before feeding them to the BiDAF model:

**Data Flow Architecture**
```mermaid
graph TD
    subgraph "Raw Data Sources"
        A["SQuAD JSON Files<br/>train-v1.1.json<br/>dev-v1.1.json"] --> B["squad/prepro.py<br/>prepro()"]
        C["GloVe Embeddings<br/>glove.*.txt"] --> B
        D["NLTK/CoreNLP<br/>Tokenizers"] --> B
    end
    
    subgraph "Preprocessing Stage"
        B --> E["Tokenization<br/>word_tokenize()<br/>sent_tokenize()"]
        E --> F["Word/Char Counters<br/>word_counter<br/>char_counter"]
        F --> G["Embedding Extraction<br/>get_word2vec()"]
        G --> H["Data Structure Creation<br/>save()"]
    end
    
    subgraph "Processed Data Storage"
        H --> I["data_*.json<br/>Structured Examples"]
        H --> J["shared_*.json<br/>Vocabularies & Embeddings"]
        H --> K["metadata_*.json<br/>Configuration Stats"]
    end
    
    subgraph "Data Loading & Management"
        I --> L["basic/read_data.py<br/>read_data()"]
        J --> L
        K --> M["load_metadata()"]
        L --> N["DataSet Objects<br/>Batching & Filtering"]
        M --> N
    end
    
    subgraph "Model Integration"
        N --> O["get_batches()<br/>Mini-batch Generation"]
        O --> P["Multi-GPU Distribution<br/>get_multi_batches()"]
        P --> Q["BiDAF Model Input<br/>Tensors & Embeddings"]
    end
```

Sources: [basic/read_data.py:158-224](), [squad/prepro.py:55-82](), [squad/prepro.py:107-227]()

## Core Components

The data pipeline consists of two main subsystems with distinct responsibilities:

**Component Architecture**
```mermaid
graph TB
    subgraph "Preprocessing Components"
        A["prepro()<br/>Main Orchestrator"] --> B["prepro_each()<br/>Process Data Split"]
        B --> C["word_tokenize()<br/>NLTK/Stanford"]
        B --> D["get_word_span()<br/>Answer Alignment"]
        B --> E["get_word2vec()<br/>Embedding Loading"]
        B --> F["save()<br/>JSON Serialization"]
    end
    
    subgraph "Data Management Components"
        G["read_data()<br/>Main Data Loader"] --> H["DataSet Class<br/>Container & Batching"]
        I["load_metadata()<br/>Config Loading"] --> H
        J["get_squad_data_filter()<br/>Example Filtering"] --> H
        H --> K["get_batches()<br/>Mini-batch Iterator"]
        H --> L["get_multi_batches()<br/>Multi-GPU Batching"]
    end
    
    subgraph "Abstract Base Classes"
        M["Data Class<br/>get_size()<br/>get_by_idxs()<br/>get_one()"] --> H
        N["DataSet Methods<br/>divide()<br/>__add__()<br/>get_empty()"] --> H
    end
    
    subgraph "Configuration Integration"
        O["update_config()<br/>Size Calculations"] --> P["Config Object<br/>max_*_size values"]
        H --> O
    end
```

Sources: [basic/read_data.py:14-39](), [basic/read_data.py:41-147](), [squad/prepro.py:107-227](), [basic/read_data.py:280-317]()

## Data Structures and Formats

The pipeline uses specific JSON structures to store processed data efficiently:

| File Type | Content | Key Fields |
|-----------|---------|------------|
| `data_*.json` | Example-specific data | `q` (questions), `cq` (char questions), `y` (answers), `*x` (context refs), `ids` |
| `shared_*.json` | Shared vocabularies & embeddings | `x` (contexts), `cx` (char contexts), `word2vec`, `word2idx`, `char2idx` |
| `metadata_*.json` | Dataset statistics | `max_*_size` values, vocabulary sizes |

**Data Structure Organization**
```mermaid
graph LR
    subgraph "Example Data Structure"
        A["data_train.json"] --> B["q: List[List[str]]<br/>Questions as token lists"]
        A --> C["cq: List[List[List[str]]]<br/>Character-level questions"]
        A --> D["y: List[List[List[int]]]<br/>Answer span positions"]
        A --> E["*x: List[List[int]]<br/>Context references"]
        A --> F["ids: List[str]<br/>SQuAD question IDs"]
    end
    
    subgraph "Shared Data Structure"
        G["shared_train.json"] --> H["x: List[List[List[str]]]<br/>Tokenized contexts"]
        G --> I["cx: List[List[List[List[str]]]]<br/>Character contexts"]
        G --> J["word2vec: Dict[str, List[float]]<br/>GloVe embeddings"]
        G --> K["word2idx: Dict[str, int]<br/>Word vocabulary"]
        G --> L["char2idx: Dict[str, int]<br/>Character vocabulary"]
    end
```

Sources: [squad/prepro.py:220-227](), [basic/read_data.py:161-164](), [basic/read_data.py:182-221]()

## Batching and Multi-GPU Support

The `DataSet` class provides sophisticated batching capabilities for efficient training:

**Batching Strategy Flow**
```mermaid
graph TD
    A["DataSet.get_batches()"] --> B{"shuffle=True?"}
    B -->|Yes| C["random.sample()<br/>Shuffle valid_idxs"]
    B -->|No| D["Use valid_idxs order"]
    C --> E{"cluster=True?"}
    E -->|Yes| F["_sort_key()<br/>Sort by max sentence length"]
    E -->|No| G["Random grouping"]
    F --> H["grouper()<br/>Create batch groups"]
    G --> H
    D --> H
    H --> I["get_by_idxs()<br/>Extract batch data"]
    I --> J["Resolve shared references<br/>*x -> shared['x']"]
    J --> K["Return batch DataSet"]
    
    subgraph "Multi-GPU Extension"
        L["get_multi_batches()"] --> M["Larger batch_size_per_step"]
        M --> N["divide()<br/>Split into GPU batches"]
        N --> O["Tuple of batch DataSets"]
    end
```

Sources: [basic/read_data.py:72-112](), [basic/read_data.py:114-119](), [basic/read_data.py:141-146]()

## Data Filtering and Validation

The system includes comprehensive filtering to ensure data quality and compatibility with model constraints:

| Filter Type | Purpose | Configuration |
|-------------|---------|---------------|
| `max` | Strict size limits | `num_sents_th`, `sent_size_th` |
| `valid` | Overall paragraph validation | Check all sentences |
| `semi` | Answer sentence validation | Only validate answer spans |
| `squash` | Paragraph-level processing | Flatten sentence structure |
| `single` | Single sentence answers | Answer spans within one sentence |

**Filtering Process**
```mermaid
graph TD
    A["get_squad_data_filter()"] --> B["data_filter() function"]
    B --> C["Extract data_point fields<br/>rx, rcx, q, cq, y"]
    C --> D["Question size check<br/>len(q) > ques_size_th"]
    D --> E{"config.data_filter"}
    E -->|max| F["Strict validation<br/>Single sentence spans"]
    E -->|valid| G["Full paragraph validation<br/>All sentences checked"]
    E -->|semi| H["Answer sentence validation<br/>Relaxed context limits"]
    F --> I["Return True/False"]
    G --> I
    H --> I
```

Sources: [basic/read_data.py:227-277](), [basic/read_data.py:167-176]()

## Integration Points

The data pipeline integrates with several other system components:

- **Configuration System**: Updates `config` object with data-derived parameters via `update_config()` [basic/read_data.py:280-317]()
- **Model Architecture**: Provides vocabulary sizes and embedding dimensions [basic/read_data.py:308-310]()
- **Training Loop**: Supplies batched data through `get_batches()` and `get_multi_batches()` methods
- **Evaluation Framework**: Supports filtered datasets and custom data splits for testing

The pipeline ensures efficient memory usage through lazy loading, reference-based shared data storage, and configurable batch sizes to accommodate different GPU memory constraints.

Sources: [basic/read_data.py:104-109](), [basic/read_data.py:280-317](), [squad/prepro.py:14-17]()

---

