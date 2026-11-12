<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/eureka-ml-insights · page 4 Data Processing · fetched 2026-10-26 -->

# Data Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eureka_ml_insights/data_utils/__init__.py](eureka_ml_insights/data_utils/__init__.py)
- [eureka_ml_insights/data_utils/data.py](eureka_ml_insights/data_utils/data.py)
- [eureka_ml_insights/data_utils/transform.py](eureka_ml_insights/data_utils/transform.py)
- [tests/data_utils_tests/data_tests.py](tests/data_utils_tests/data_tests.py)

</details>



The Data Processing system in Eureka ML Insights is responsible for loading, transforming, and preparing data for model evaluation. It includes components for reading data from various sources, applying transformations to prepare the data for inference, and delivering data to models during evaluation.

For information about model-specific components, see [Model System](#3). For details about how to configure data processing pipelines, see [Configuration System](#2.2).

## Overview

The Data Processing system consists of three main component types:

1. **Data Readers** - Load data from various sources (local files, Azure storage, HuggingFace)
2. **Data Transformations** - Modify and prepare data for model evaluation
3. **Data Loaders** - Feed data to models during inference

```mermaid
graph TD
    subgraph "Data Processing System"
        subgraph "Data Readers"
            DR["DataReader"] --> LR["LocalReaders"]
            DR --> CR["CloudReaders"]
            
            LR --> JR["JsonReader"]
            CR --> AR["AzureDataReader"]
            CR --> HFR["HFDataReader"]
        end
        
        subgraph "Data Transformations"
            DT["DFTransformBase"] --> ST["SequenceTransform"]
            DT --> SCT["SingleColumnTransforms"]
            DT --> MCT["MultiColumnTransform"]
            
            SCT --> CR["ColumnRename"]
            SCT --> RPT["RunPythonTransform"]
            
            MCT --> RT["RegexTransform"]
            MCT --> IT["ImputeNA"]
            MCT --> TT["TokenCounterTransform"]
        end
        
        subgraph "Data Loaders"
            DL["DataLoader"] --> MMDL["MMDataLoader"]
            MMDL --> AMMDL["AzureMMDataLoader"]
        end
    end
    
    DR --> |"produces"| DF[("Pandas DataFrame")]
    DF --> |"processed by"| DT
    DT --> |"outputs"| DF2[("Transformed DataFrame")]
    DF2 --> |"loaded by"| DL
    DL --> |"feeds"| MODEL[("Model Inference")]
```

Sources: [eureka_ml_insights/data_utils/data.py:32-504](), [eureka_ml_insights/data_utils/transform.py:29-506]()

## Data Readers

Data Readers are classes responsible for loading data from various sources into pandas DataFrames.

### Class Hierarchy

```mermaid
classDiagram
    class DataReaderBase {
        <<abstract>>
        +read()*
    }
    
    class DataReader {
        +path: str
        +format: str
        +transform: DFTransformBase
        +load_dataset() DataFrame
        -_load_dataset() DataFrame
    }
    
    class JsonReader {
        +path: str
        +format: str
        +read() dict
    }
    
    class AzureBlobReader {
        +read_azure_blob(blob_url) str
    }
    
    class HFDataReader {
        +path: str
        +split: List[str]|str
        +tasks: List[str]|str
        +transform: DFTransformBase
        +load_dataset() DataFrame
        -_load_dataset() DataFrame
        -_hf_to_dataframe() DataFrame
        -_save_images() DataFrame
    }
    
    class AzureDataReader {
        +account_url: str
        +blob_container: str
        +blob_name: str
        +format: str
        +transform: DFTransformBase
        -_load_dataset() DataFrame
    }
    
    class AzureJsonReader {
        +account_url: str
        +blob_container: str
        +blob_name: str
        +read() dict
    }
    
    class HFJsonReader {
        +repo_id: str
        +repo_type: str
        +filename: str
        +read() dict
    }
    
    DataReaderBase <|-- JsonReader
    DataReaderBase <|-- DataReader
    
    JsonReader <|-- HFJsonReader
    JsonReader <|-- AzureJsonReader
    
    AzureBlobReader <|-- AzureJsonReader
    AzureBlobReader <|-- AzureDataReader
    
    DataReader <|-- AzureDataReader
    DataReader <|-- HFDataReader
```

Sources: [eureka_ml_insights/data_utils/data.py:32-650]()

### Key Data Reader Classes

| Class | Description | Source |
|-------|-------------|--------|
| `DataReaderBase` | Abstract base class for all data readers | [data.py:32-35]() |
| `DataReader` | Base implementation for reading datasets and applying transformations | [data.py:418-468]() |
| `JsonReader` | Reads JSON or JSONL files from local paths | [data.py:302-321]() |
| `AzureDataReader` | Reads data from Azure Blob Storage | [data.py:471-504]() |
| `HFDataReader` | Reads data from HuggingFace datasets | [data.py:507-650]() |
| `AzureJsonReader` | Reads JSON data from Azure Blob Storage | [data.py:340-371]() |
| `HFJsonReader` | Reads JSON data from HuggingFace repositories | [data.py:374-390]() |

Sources: [eureka_ml_insights/data_utils/data.py:32-650]()

#### Common Usage Pattern

```mermaid
sequenceDiagram
    participant User
    participant DataReader
    participant Transform
    
    User->>DataReader: Create reader with path & transform
    User->>DataReader: load_dataset()
    DataReader->>DataReader: _load_dataset()
    DataReader->>Transform: transform.transform(df)
    Transform-->>DataReader: transformed df
    DataReader-->>User: Processed DataFrame
```

Sources: [eureka_ml_insights/data_utils/data.py:445-453]()

## Data Transformations

Data Transformations allow manipulation of DataFrames to prepare data for model evaluation. The framework is built around the `DFTransformBase` abstract class and provides numerous implementations for specific transformation needs.

### Transform Class Hierarchy

```mermaid
classDiagram
    class DFTransformBase {
        <<abstract>>
        +transform(df: DataFrame) DataFrame*
    }
    
    class SequenceTransform {
        +transforms: List[DFTransformBase]
        +transform(df: DataFrame) DataFrame
    }
    
    class MultiColumnTransform {
        +columns: List[str]|str
        +validate(df: DataFrame)
        +transform(df: DataFrame) DataFrame
        #_transform(value) value
    }
    
    class ColumnRename {
        +name_mapping: Dict[str, str]
        +transform(df: DataFrame) DataFrame
    }
    
    class RunPythonTransform {
        +python_code: str
        +global_imports: list
        +validate()
        +transform(df: DataFrame) DataFrame
    }
    
    class ImputeNA {
        +columns: List[str]|str
        +value: str
        +_transform(value) value
    }
    
    class TokenCounterTransform {
        +columns: List[str]|str
        +transform(df: DataFrame, encoding) DataFrame
    }
    
    class RegexTransform {
        +columns: List[str]|str
        +prompt_pattern: str
        +ignore_case: bool
        +occurrence: str
        +_transform(sentence) value
    }
    
    class MajorityVoteTransform {
        +model_output_col: str
        +id_col: str
        +majority_vote_col: str
        +transform(df: DataFrame, random_state) DataFrame
    }
    
    DFTransformBase <|-- SequenceTransform
    DFTransformBase <|-- ColumnRename
    DFTransformBase <|-- RunPythonTransform
    DFTransformBase <|-- MultiColumnTransform
    DFTransformBase <|-- MajorityVoteTransform
    
    MultiColumnTransform <|-- ImputeNA
    MultiColumnTransform <|-- TokenCounterTransform
    MultiColumnTransform <|-- RegexTransform
```

Sources: [eureka_ml_insights/data_utils/transform.py:29-506]()

### Key Transformation Classes

| Category | Class | Description | Source |
|----------|-------|-------------|--------|
| **Base** | `DFTransformBase` | Abstract base class for all transformations | [transform.py:29-32]() |
| **Composition** | `SequenceTransform` | Applies multiple transformations in sequence | [transform.py:35-42]() |
| **Column Operations** | `ColumnRename` | Renames columns according to a mapping | [transform.py:45-50]() |
| | `CopyColumn` | Copies data from one column to another | [transform.py:158-168]() |
| | `AddColumn` | Adds an empty column | [transform.py:138-144]() |
| | `AddColumnAndData` | Adds a column with specified data | [transform.py:147-155]() |
| **Data Manipulation** | `ImputeNA` | Fills missing values | [transform.py:264-275]() |
| | `ReplaceStringsTransform` | Replaces strings in selected columns | [transform.py:278-294]() |
| | `MapStringsTransform` | Maps values according to a dictionary | [transform.py:297-311]() |
| | `RegexTransform` | Extracts patterns using regex | [transform.py:334-361]() |
| **Advanced** | `RunPythonTransform` | Runs arbitrary Python code | [transform.py:53-100]() |
| | `MajorityVoteTransform` | Applies majority voting across repeats | [transform.py:404-429]() |
| **MCQ Specific** | `ShuffleColumnsTransform` | Shuffles values across columns for MCQ benchmarks | [transform.py:204-228]() |
| | `ColumnMatchMapTransform` | Identifies columns with matching values | [transform.py:231-261]() |

Sources: [eureka_ml_insights/data_utils/transform.py:29-506]()

### Transformation Workflow

```mermaid
flowchart TD
    DF1[("Raw DataFrame")] --> TR1["Transform 1\n(ImputeNA)"]
    TR1 --> DF2[("Intermediate Result")]
    DF2 --> TR2["Transform 2\n(ColumnRename)"]
    TR2 --> DF3[("Intermediate Result")]
    DF3 --> TR3["Transform 3\n(RegexTransform)"]
    TR3 --> DF4[("Final DataFrame")]
    
    SEQ["SequenceTransform"]
    SEQ --- TR1
    SEQ --- TR2
    SEQ --- TR3
    
    style SEQ stroke-dasharray: 5 5
```

Sources: [eureka_ml_insights/data_utils/transform.py:35-42]()

### Example: Token Counting

The `TokenCounterTransform` class illustrates a practical transformation that counts tokens in string columns, which is useful for working with LLMs:

```mermaid
flowchart LR
    DF1[("DataFrame\nColumns: ['prompt', 'response']")] --> TC["TokenCounterTransform(['prompt', 'response'])"]
    TC --> DF2[("Transformed DataFrame\nColumns: ['prompt', 'response', 'prompt_token_count', 'response_token_count']")]
```

Sources: [eureka_ml_insights/data_utils/transform.py:377-401]()

## Data Loaders

Data Loaders are responsible for feeding data to models during inference. They handle the iteration through dataset records and prepare the input for models in the expected format.

### Loader Class Hierarchy

```mermaid
classDiagram
    class DataLoader {
        +path: str
        +total_lines: int
        +prepare_model_input(row) tuple
        +get_sample_model_input() tuple
    }
    
    class MMDataLoader {
        +mm_data_path_prefix: str
        +load_images: bool
        +image_column_names: List[str]
        +image_column_search_regex: str
        +misc_columns: List[str]
        +prepare_model_input(row) tuple
        -_search_for_image_columns(data_row) list
        -_gather_image_file_names(data, image_column_names) list
        -_load_images(images) list
        +load_image(image_file_name) Image
    }
    
    class AzureMMDataLoader {
        +account_url: str
        +blob_container: str
        +load_image(image_file_name) Image
    }
    
    DataLoader <|-- MMDataLoader
    MMDataLoader <|-- AzureMMDataLoader
```

Sources: [eureka_ml_insights/data_utils/data.py:38-281]()

### Key Data Loader Classes

| Class | Description | Source |
|-------|-------------|--------|
| `DataLoader` | Base loader for JSONL data | [data.py:38-73]() |
| `MMDataLoader` | Loader for multimodal data with images | [data.py:75-219]() |
| `AzureMMDataLoader` | Loader for multimodal data from Azure | [data.py:237-281]() |

Sources: [eureka_ml_insights/data_utils/data.py:38-281]()

### Multimodal Data Loading Process

```mermaid
sequenceDiagram
    participant User
    participant MMDataLoader
    participant Storage
    participant Model
    
    User->>MMDataLoader: __iter__() 
    loop For each record
        MMDataLoader->>MMDataLoader: prepare_model_input(row)
        alt Has image columns
            MMDataLoader->>MMDataLoader: _search_for_image_columns()
            MMDataLoader->>MMDataLoader: _gather_image_file_names()
            MMDataLoader->>MMDataLoader: _load_images()
            loop For each image
                MMDataLoader->>Storage: load_image()
                Storage-->>MMDataLoader: PIL.Image
            end
        end
        MMDataLoader-->>User: (row, model_args, model_kwargs)
        User->>Model: model(*model_args, **model_kwargs)
    end
```

Sources: [eureka_ml_insights/data_utils/data.py:75-219]()

## Task-Specific Utilities

The Data Processing system includes specialized utilities for processing benchmark-specific data:

| Task Type | Utilities | Purpose |
|-----------|-----------|---------|
| Spatial Reasoning | `ExtractAnswerGrid`, `ExtractAnswerSpatialMapAndMaze` | Extract answers from spatial reasoning tasks |
| Math Problems | `AIMEExtractAnswer` | Extract answers from AIME math problems |
| Multiple Choice | `ShuffleColumnsTransform`, `ColumnMatchMapTransform` | Handle randomization and answer matching in MCQ benchmarks |

Sources: [eureka_ml_insights/data_utils/__init__.py:1-83]()

## Integration with Pipeline System

```mermaid
flowchart LR
    subgraph "Pipeline"
        PC["PipelineConfig"]
        DP["DataProcessingComponent"]
        PP["PromptProcessingComponent"]
        INF["InferenceComponent"]
        ER["EvalReportingComponent"]
        
        PC --> DP
        DP --> PP
        PP --> INF
        INF --> ER
    end
    
    subgraph "Data Processing System"
        DR["DataReader"]
        DT["DFTransformBase"]
        DL["DataLoader"]
        
        DR --> |outputs| DF[("DataFrame")]
        DF --> |processed by| DT
        DT --> |produces| TDF[("Transformed DataFrame")]
        TDF --> |loaded by| DL
    end
    
    DP --- DR
    DP --- DT
    INF --- DL
```

Sources: [eureka_ml_insights/data_utils/data.py:32-650](), [eureka_ml_insights/data_utils/transform.py:29-506]()

## End-to-End Data Processing Flow

```mermaid
flowchart TD
    DS1[("Data Source\n(Local, Azure, HF)")] --> DR["DataReader"]
    DR --> |"load_dataset()"| DF[("Raw DataFrame")]
    DF --> |"transform.transform()"| TDF[("Transformed DataFrame")]
    
    TDF --> |"iter()"| DL["DataLoader"]
    DL --> |"prepare_model_input()"| MI[("Model Input\n(row, model_args, model_kwargs)")]
    MI --> MD["Model"]
    MD --> |"generate()"| MO["Model Output"]
    
    MO --> |"store"| RDF[("Results DataFrame")]
    RDF --> |"MajorityVoteTransform"| ADF[("Aggregated Results")]
    ADF --> |"save"| FDF[("Final Results")]
```

Sources: [eureka_ml_insights/data_utils/data.py:32-650](), [eureka_ml_insights/data_utils/transform.py:29-506]()

## Conclusion

The Data Processing system in Eureka ML Insights provides a comprehensive framework for working with evaluation data throughout the model evaluation lifecycle. Its modular design allows for flexibility in data sources, transformations, and loading strategies, making it adaptable to various evaluation scenarios.

For information about specific task implementations, see the [Benchmarks](#5) section.

---

