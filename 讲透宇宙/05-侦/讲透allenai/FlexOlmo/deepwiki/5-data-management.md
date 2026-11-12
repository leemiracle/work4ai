<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/FlexOlmo · page 5 Data Management · fetched 2026-10-26 -->

# Data Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/data/part-01-00000-tiny.npy](src/data/part-01-00000-tiny.npy)
- [src/data/part-02-00000-tiny.npy](src/data/part-02-00000-tiny.npy)
- [src/flexolmo/data/mixes/__init__.py](src/flexolmo/data/mixes/__init__.py)
- [src/flexolmo/data/mixes/proxy_combined_public_math_code_news.txt](src/flexolmo/data/mixes/proxy_combined_public_math_code_news.txt)

</details>



The data management system in FlexOlmo handles the organization, preprocessing, and configuration of training data across multiple domains and sources. This system supports the flexible combination of public datasets, domain-specific expert data, and proxy datasets used for router training. The data management components enable collaborative model development by allowing different data sources to be combined without direct data sharing.

For information about domain embeddings used in router training, see [Domain Embeddings](#5.2). For data extraction analysis tools, see [Data Extraction Analysis](#5.3).

## Data Mix Architecture

FlexOlmo's data management is built around the concept of data mixes, which are named collections of data sources that can be dynamically combined during training. The system provides a flexible framework for organizing and accessing different types of training data.

### Data Mix System Overview

```mermaid
graph TB
    subgraph "Data Mix Types"
        A["`CustomDataMix`"]
        B["`public_mix`"]
        C["`Domain Data`<br/>creative_writing<br/>mj_finemath4plus<br/>starcoder<br/>news<br/>pes2o<br/>flan<br/>reddit_v0"]
        D["`Proxy Mixes`<br/>proxy_code<br/>proxy_math<br/>proxy_creative<br/>proxy_news<br/>proxy_pes2o<br/>proxy_reddit"]
        E["`Test Mixes`<br/>test_mix<br/>anneal_test_mix"]
    end
    
    subgraph "Data Mix Files"
        F["`*.txt files`<br/>Label,Path pairs"]
        G["`_get_data_mix_path()`"]
        H["`importlib_resources`"]
    end
    
    subgraph "Configuration System"
        I["`NumpyDatasetConfig`"]
        J["`SourceMixtureDatasetConfig`"]
        K["`SourceMixtureConfig`"]
        L["`get_mixture_dataset_config()`"]
    end
    
    subgraph "Data Loading"
        M["`build() method`"]
        N["`Tokenized Data Files`<br/>*.npy"]
        O["`Base Directory`<br/>s3://ai2-llm or local"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    
    A --> M
    M --> G
    G --> F
    G --> H
    
    I --> L
    L --> J
    J --> K
    
    M --> N
    N --> O
    
    F --> N
```

Sources: [src/flexolmo/data/mixes/__init__.py:1-155]()

## CustomDataMix Class

The `CustomDataMix` class serves as the central registry for all available data mixes in FlexOlmo. It inherits from `DataMixBase` and provides enumeration-style access to different data sources.

### Available Data Mix Types

| Category | Mix Names | Purpose |
|----------|-----------|---------|
| **Public Data** | `public_mix` | General public training data (~1T tokens) |
| **Domain Data** | `creative_writing`, `mj_finemath4plus`, `starcoder`, `news`, `pes2o`, `flan`, `reddit_v0` | Domain-specific expert training data |
| **Proxy Data** | `proxy_code`, `proxy_math`, `proxy_creative`, `proxy_news`, `proxy_pes2o`, `proxy_reddit` | Smaller datasets for router training |
| **Combined Proxy** | `proxy_combined_public_math_code_news` | Multi-domain proxy mix |
| **OLMo2 Setup** | `dolmino_minus_math`, `dolmino_minus_math_flan` | Specialized configurations |
| **Test Data** | `test_mix`, `anneal_test_mix` | Development and testing |

### Data Mix File Structure

Data mix files are stored as text files with a simple format:
```
label,path/to/data/file.npy
label,path/to/data/file.npy
```

The `build()` method processes these files to construct file paths and labels:

```mermaid
graph LR
    subgraph "build() Method Flow"
        A["`Input Parameters`<br/>base_dir<br/>tokenizer"]
        B["`_get_data_mix_path()`"]
        C["`Parse .txt file`<br/>Skip comments (#)<br/>Split label,path"]
        D["`Process Paths`<br/>Replace {TOKENIZER}<br/>Prepend base_dir"]
        E["`Return`<br/>List[paths]<br/>List[labels]"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
```

Sources: [src/flexolmo/data/mixes/__init__.py:50-77](), [src/flexolmo/data/mixes/proxy_combined_public_math_code_news.txt:1-82]()

## Data Source Configuration

The system supports flexible configuration of data sources through the `SourceMixtureDatasetConfig` framework, which allows combining multiple data mixes with different target ratios.

### Mixture Dataset Configuration

The `get_mixture_dataset_config()` function converts a comma-separated list of data mixes into a structured configuration:

```mermaid
graph TD
    subgraph "Configuration Process"
        A["`NumpyDatasetConfig`<br/>mix: 'public_mix,math,code'<br/>mix_base_dir: '/path/to/data'"]
        B["`Split mix names`<br/>Parse comma-separated list"]
        C["`Process each mix`<br/>Read .txt files<br/>Build paths list"]
        D["`Create SourceMixtureConfig`<br/>source_name<br/>paths<br/>target_ratio"]
        E["`SourceMixtureDatasetConfig`<br/>source_configs<br/>max_tokens<br/>sequence_length"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    F["`Configuration Parameters`"]
    F --> G["`max_repetition_ratio: 3`<br/>For smaller datasets"]
    F --> H["`target_ratio: 1.0/len(names)`<br/>Equal weighting"]
    F --> I["`max_tokens: 5B`<br/>Data preparation limit"]
    F --> J["`seed: 2025`<br/>Reproducibility"]
    F --> K["`processes: 8`<br/>Parallel processing"]
    
    G --> E
    H --> E
    I --> E
    J --> E
    K --> E
```

### Key Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_repetition_ratio` | 3 | Allows smaller datasets like `mj_finemath4plus` to be repeated |
| `target_ratio` | `1.0/len(names)` | Equal weighting across all mixes by default |
| `max_tokens` | 5,000,000,000 | Upper limit for data preparation (5B tokens) |
| `seed` | 2025 | Ensures reproducible data sampling |
| `processes` | 8 | Number of parallel processes for data loading |

Sources: [src/flexolmo/data/mixes/__init__.py:80-139]()

## Data File Organization

### File Path Structure

Data files are organized in a hierarchical structure under a base directory:

```
base_dir/
├── preprocessed/olmo_modular_data/
│   ├── public/
│   │   └── 600m/
│   │       └── part-XX-00000.npy
│   ├── proxy_domain_data/
│   │   ├── math_600m_tokens/
│   │   ├── code_600m_tokens/
│   │   └── news/
│   └── domain_specific/
│       ├── creative_writing/
│       ├── starcoder/
│       └── pes2o/
```

### Tokenizer Integration

The system supports dynamic tokenizer replacement in file paths using the `{TOKENIZER}` placeholder, allowing the same data mix definitions to work with different tokenizers.

```mermaid
graph LR
    subgraph "Path Resolution"
        A["`Raw Path`<br/>data/{TOKENIZER}/file.npy"]
        B["`Tokenizer ID`<br/>e.g., 'gpt2'"]
        C["`Base Directory`<br/>s3://ai2-llm/"]
        D["`Final Path`<br/>s3://ai2-llm/data/gpt2/file.npy"]
    end
    
    A --> D
    B --> D
    C --> D
```

Sources: [src/flexolmo/data/mixes/__init__.py:74-75]()

## Data Loading Integration

The data management system integrates with the broader FlexOlmo training pipeline through the configuration system:

### Integration Flow

```mermaid
graph TD
    subgraph "Training Pipeline Integration"
        A["`ExperimentConfig`"]
        B["`NumpyDatasetConfig`<br/>mix specification"]
        C["`get_mixture_dataset_config()`"]
        D["`SourceMixtureDatasetConfig`"]
        E["`Data Loading`<br/>During training"]
    end
    
    subgraph "Configuration Update"
        F["`dataset_config.mix`<br/>Comma-separated mix names"]
        G["`dataset_config.mix_base_dir`<br/>Data storage location"]
        H["`dataset_config.source_mixture_config`<br/>Structured configuration"]
        I["`dataset_config.mix = None`<br/>Clear original mix field"]
    end
    
    A --> B
    B --> F
    B --> G
    F --> C
    G --> C
    C --> D
    D --> H
    H --> I
    D --> E
```

### Usage Example

The typical usage pattern involves:

1. Setting `dataset_config.mix` to a comma-separated list of mix names
2. Setting `dataset_config.mix_base_dir` to the data storage location
3. Calling `get_mixture_dataset_config()` to create the structured configuration
4. Clearing the original mix field and using the structured configuration

Sources: [src/flexolmo/data/mixes/__init__.py:84-90]()

## Resource Management

The system uses `importlib_resources` for accessing data mix definition files, ensuring proper resource management across different deployment environments:

```mermaid
graph TB
    subgraph "Resource Access"
        A["`_get_data_mix_path()`<br/>Context manager"]
        B["`importlib_resources`<br/>Cross-platform access"]
        C["`flexolmo/data/mixes/`<br/>Package resources"]
        D["`{mix_name}.txt`<br/>Mix definition files"]
        E["`Automatic cleanup`<br/>Context manager pattern"]
    end
    
    A --> B
    B --> C
    C --> D
    A --> E
```

This approach ensures that data mix definitions are properly packaged with the FlexOlmo installation and accessible regardless of the deployment environment.

Sources: [src/flexolmo/data/mixes/__init__.py:142-154]()

---

