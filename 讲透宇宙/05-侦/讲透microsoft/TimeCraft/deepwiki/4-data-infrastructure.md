<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 4 Data Infrastructure · fetched 2026-10-26 -->

# Data Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [TimeDP/ldm/data/tsg_dataset.py](TimeDP/ldm/data/tsg_dataset.py)
- [TimeDP/utils/prepare_datasets.py](TimeDP/utils/prepare_datasets.py)
- [diffusion/ldm/data/tsg_dataset.py](diffusion/ldm/data/tsg_dataset.py)

</details>



This document provides a comprehensive overview of the data handling infrastructure in the TimeCraft framework. The data infrastructure is responsible for loading, processing, normalizing, and serving time series data to the model training and inference systems. It supports multiple data formats, normalization methods, and conditioning modes including text-based and classification-based generation.

For information about specific dataset preparation utilities, see [Dataset Preparation and Loading](#4.1). For details on TSG dataset classes and their PyTorch Lightning integration, see [TSG Dataset Modules](#4.2).

## Core Data Infrastructure Architecture

The data infrastructure is built around a modular design that separates data loading, normalization, and serving responsibilities. The system supports multiple input formats and provides standardized interfaces for different conditioning modes.

```mermaid
graph TD
    subgraph "Data Sources"
        CSV["CSV Files"]
        TSF["TSF Files"]
        NPY["NPY Files"]
        PKL["PKL Files"]
    end
    
    subgraph "Data Loading Layer"
        LDFF["load_data_from_file()"]
        LDTF["load_data_text_from_file()"]
        CTSF["convert_tsf_to_dataframe()"]
    end
    
    subgraph "Dataset Classes"
        TSGD["TSGDataset"]
        TSGTD["TSGtextDataset"]
        TSCCD["TSClassCondDataset"]
    end
    
    subgraph "Data Modules"
        TSGDM["TSGDataModule"]
        TSGTDM["TSGtextDataModule"]
        TSCCDM["TSClassCondTrainDataModule"]
    end
    
    subgraph "Normalization Engine"
        FN["fit_normalizer()"]
        TRANS["transform()"]
        INVTRANS["inverse_transform()"]
    end
    
    subgraph "PyTorch Integration"
        DL["DataLoader"]
        WRS["WeightedRandomSampler"]
    end
    
    CSV --> LDFF
    TSF --> LDFF
    NPY --> LDFF
    PKL --> LDFF
    TSF --> CTSF
    LDFF --> LDTF
    
    LDFF --> TSGD
    LDTF --> TSGTD
    LDFF --> TSCCD
    
    TSGD --> TSGDM
    TSGTD --> TSGTDM
    TSCCD --> TSCCDM
    
    TSGDM --> FN
    TSGTDM --> FN
    TSCCDM --> FN
    
    FN --> TRANS
    TRANS --> INVTRANS
    
    TSGDM --> DL
    TSGTDM --> DL
    TSCCDM --> DL
    
    DL --> WRS
```

Sources: [diffusion/ldm/data/tsg_dataset.py:1-992]()

## Data Loading and Format Support

The system provides unified data loading through the `load_data_from_file` function, which automatically detects file formats and applies appropriate loading strategies. The loading layer abstracts away format-specific details and provides consistent numpy array outputs.

```mermaid
graph LR
    subgraph "File Formats"
        CSV_FORMAT["CSV\n(Pandas DataFrame)"]
        TSF_FORMAT["TSF\n(Time Series Format)"]
        NPY_FORMAT["NPY\n(NumPy Array)"]
        PKL_FORMAT["PKL\n(Pickle)"]
    end
    
    subgraph "Loading Functions"
        LDFF_MAIN["load_data_from_file()"]
        LDTF_MAIN["load_data_text_from_file()"]
        CTSF_MAIN["convert_tsf_to_dataframe()"]
    end
    
    subgraph "Data Processing"
        RESHAPE["Reshape Operations"]
        WINDOW["Window Slicing"]
        VALIDATE["Data Validation"]
    end
    
    subgraph "Output Format"
        NUMPY["NumPy Arrays\n(N, T, C)"]
        TEXT_EMB["Text Embeddings\n(N, 4096)"]
        LABELS["Labels\n(N,)"]
    end
    
    CSV_FORMAT --> LDFF_MAIN
    TSF_FORMAT --> LDFF_MAIN
    NPY_FORMAT --> LDFF_MAIN
    PKL_FORMAT --> LDFF_MAIN
    
    TSF_FORMAT --> CTSF_MAIN
    LDFF_MAIN --> LDTF_MAIN
    
    LDFF_MAIN --> RESHAPE
    LDTF_MAIN --> RESHAPE
    CTSF_MAIN --> RESHAPE
    
    RESHAPE --> WINDOW
    WINDOW --> VALIDATE
    
    VALIDATE --> NUMPY
    VALIDATE --> TEXT_EMB
    VALIDATE --> LABELS
```

Sources: [diffusion/ldm/data/tsg_dataset.py:828-846](), [diffusion/ldm/data/tsg_dataset.py:685-826](), [diffusion/ldm/data/tsg_dataset.py:849-991]()

## Normalization Methods

The data infrastructure supports six different normalization methods, each suited for different data characteristics and use cases. The normalization system provides both forward and inverse transforms, enabling proper denormalization of generated samples.

| Method | Description | Use Case | Transform Function |
|--------|-------------|----------|-------------------|
| `zscore` | Z-score normalization | Gaussian-like distributions | `(x - mean) / std` |
| `robust_iqr` | Robust scaling with IQR | Outlier-resistant | `(x - median) / IQR` |
| `robust_mad` | Robust scaling with MAD | Heavy outliers | `(x - median) / MAD` |
| `minmax` | Min-max scaling | Bounded range [0,1] | `(x - min) / (max - min)` |
| `pit` | Probability integral transform | Non-parametric | `ECDF(x)` |
| `centered_pit` | Centered PIT | Range [-1,1] | `2 * ECDF(x) - 1` |

```mermaid
graph TD
    subgraph "Normalization Pipeline"
        INPUT["Raw Data\n(N, T, C)"]
        FLATTEN["Flatten for Stats"]
        COMPUTE["Compute Statistics"]
        STORE["Store Normalizer"]
        TRANSFORM["Apply Transform"]
        OUTPUT["Normalized Data"]
    end
    
    subgraph "Normalizer Types"
        ZSCORE["Z-Score\n{mean, std}"]
        ROBUST_IQR["Robust IQR\n{median, iqr}"]
        ROBUST_MAD["Robust MAD\n{median, mad}"]
        MINMAX["MinMax\n{min, max}"]
        PIT["PIT\n{ecdf}"]
        CENTERED_PIT["Centered PIT\n{ecdf}"]
    end
    
    subgraph "Inverse Transform"
        DENORM["Denormalize"]
        ORIGINAL["Original Scale"]
    end
    
    INPUT --> FLATTEN
    FLATTEN --> COMPUTE
    COMPUTE --> ZSCORE
    COMPUTE --> ROBUST_IQR
    COMPUTE --> ROBUST_MAD
    COMPUTE --> MINMAX
    COMPUTE --> PIT
    COMPUTE --> CENTERED_PIT
    
    ZSCORE --> STORE
    ROBUST_IQR --> STORE
    ROBUST_MAD --> STORE
    MINMAX --> STORE
    PIT --> STORE
    CENTERED_PIT --> STORE
    
    STORE --> TRANSFORM
    TRANSFORM --> OUTPUT
    
    OUTPUT --> DENORM
    DENORM --> ORIGINAL
```

Sources: [diffusion/ldm/data/tsg_dataset.py:212-282](), [diffusion/ldm/data/tsg_dataset.py:413-474](), [diffusion/ldm/data/tsg_dataset.py:604-663]()

## Dataset Classes and Data Modules

The system provides specialized dataset classes for different conditioning modes, each paired with a PyTorch Lightning data module for seamless integration with the training pipeline.

```mermaid
graph TB
    subgraph "Base Dataset Classes"
        TSGD["TSGDataset\nBasic time series"]
        TSGTD["TSGtextDataset\nText-conditioned"]
        TSCCD["TSClassCondDataset\nClassification-conditioned"]
    end
    
    subgraph "Data Module Classes"
        TSGDM["TSGDataModule\nBasic training"]
        TSGTDM["TSGtextDataModule\nText training"]
        TSCCDM["TSClassCondTrainDataModule\nClassification training"]
    end
    
    subgraph "Core Methods"
        PREPARE["prepare_data()"]
        SPLIT["split_train_val()"]
        TRAIN_DL["train_dataloader()"]
        VAL_DL["val_dataloader()"]
    end
    
    subgraph "Sampling Support"
        WRS["WeightedRandomSampler\nDataset rebalancing"]
        STATS["cal_data_stats()\nDataset statistics"]
        REWEIGHT["get_reweight_sampler()\nSampling weights"]
    end
    
    TSGD --> TSGDM
    TSGTD --> TSGTDM
    TSCCD --> TSCCDM
    
    TSGDM --> PREPARE
    TSGTDM --> PREPARE
    TSCCDM --> PREPARE
    
    PREPARE --> SPLIT
    SPLIT --> TRAIN_DL
    SPLIT --> VAL_DL
    
    TSGD --> STATS
    TSGTD --> STATS
    TSCCD --> STATS
    
    STATS --> REWEIGHT
    REWEIGHT --> WRS
```

Sources: [diffusion/ldm/data/tsg_dataset.py:284-331](), [diffusion/ldm/data/tsg_dataset.py:476-533](), [diffusion/ldm/data/tsg_dataset.py:16-46]()

## Text-Based Data Processing

The system supports text-conditioned generation through specialized text processing pipelines that integrate with large language models for embedding generation. This enables natural language control over time series generation.

```mermaid
graph LR
    subgraph "Text Data Sources"
        CSV_TEXT["CSV with Text Columns\n_text_description\n_dataset_description"]
        TEXT_DATA["Raw Text Data"]
    end
    
    subgraph "Text Processing Pipeline"
        PREPROCESS["preprocess_text_data()"]
        TOKENIZE["Tokenizer\n(Llama-3.1-8B)"]
        EMBED["Model Embedding\n(Hidden States)"]
        AGGREGATE["Mean Pooling"]
    end
    
    subgraph "Text Embedding Output"
        TEXT_EMB_4096["Text Embeddings\n(N, 4096)"]
        DATASET_EMB["Dataset Embeddings\n(N, 4096)"]
    end
    
    subgraph "Integration with TSG"
        TSGTD_INT["TSGtextDataset"]
        TSGTDM_INT["TSGtextDataModule"]
        COMBINED["Combined Output\n{context, data_key, text_embedding}"]
    end
    
    CSV_TEXT --> PREPROCESS
    TEXT_DATA --> PREPROCESS
    
    PREPROCESS --> TOKENIZE
    TOKENIZE --> EMBED
    EMBED --> AGGREGATE
    
    AGGREGATE --> TEXT_EMB_4096
    AGGREGATE --> DATASET_EMB
    
    TEXT_EMB_4096 --> TSGTD_INT
    DATASET_EMB --> TSGTD_INT
    
    TSGTD_INT --> TSGTDM_INT
    TSGTDM_INT --> COMBINED
```

Sources: [diffusion/ldm/data/tsg_dataset.py:685-805](), [diffusion/ldm/data/tsg_dataset.py:673-684](), [diffusion/ldm/data/tsg_dataset.py:535-663]()

## Data Preparation and External Sources

The framework includes comprehensive utilities for downloading and preparing datasets from various public sources, with automatic format conversion and standardization.

```mermaid
graph TD
    subgraph "External Data Sources"
        MONASH["Monash Archive\n(Zenodo)"]
        GLUONTS["GluonTS Datasets"]
        TIMEGAN["TimeGAN Stock Data"]
        GITHUB["GitHub Raw Data"]
    end
    
    subgraph "Download Functions"
        DL_MONASH["download_monash_dataset()"]
        DL_STOCK["download_timegan_stock_dataset()"]
        CREATE_CSV["create_dataset_csv()"]
    end
    
    subgraph "Data Processing"
        GROUPER["MultivariateGrouper"]
        CONVERT["Format Conversion"]
        SLICE["Sequence Slicing"]
        SPLIT["Train/Val/Test Split"]
    end
    
    subgraph "Output Formats"
        CSV_OUT["CSV Files"]
        NPY_OUT["NPY Files"]
        PKL_OUT["PKL Files"]
    end
    
    MONASH --> DL_MONASH
    TIMEGAN --> DL_STOCK
    GLUONTS --> CREATE_CSV
    GITHUB --> DL_STOCK
    
    DL_MONASH --> GROUPER
    DL_STOCK --> CONVERT
    CREATE_CSV --> GROUPER
    
    GROUPER --> SLICE
    CONVERT --> SLICE
    SLICE --> SPLIT
    
    SPLIT --> CSV_OUT
    SPLIT --> NPY_OUT
    SPLIT --> PKL_OUT
```

Sources: [TimeDP/utils/prepare_datasets.py:24-52](), [TimeDP/utils/prepare_datasets.py:53-61](), [TimeDP/utils/prepare_datasets.py:63-153]()

## Data Flow and Training Integration

The complete data flow from raw sources through normalization to model training demonstrates the integrated nature of the data infrastructure with the broader TimeCraft framework.

```mermaid
graph TB
    subgraph "Data Sources"
        RAW_DATA["Raw Data Files\n(Various Formats)"]
        EXTERNAL["External APIs\n(Zenodo, GitHub)"]
    end
    
    subgraph "Data Preparation"
        PREPARE_SCRIPTS["prepare_datasets.py"]
        LOAD_FUNCS["load_data_from_file()"]
        VALIDATION["Data Validation"]
    end
    
    subgraph "Normalization Layer"
        FIT_NORM["fit_normalizer()"]
        APPLY_NORM["transform()"]
        STORE_NORM["Store Normalizers"]
    end
    
    subgraph "Dataset Layer"
        DATASET_CLASSES["Dataset Classes\n(TSG, TSGtext, TSClassCond)"]
        DATA_MODULES["Data Modules\n(PyTorch Lightning)"]
        SAMPLERS["Weighted Samplers"]
    end
    
    subgraph "Training Pipeline"
        TRAIN_LOADER["Training DataLoader"]
        VAL_LOADER["Validation DataLoader"]
        BATCH_DATA["Batched Data"]
    end
    
    subgraph "Model Interface"
        CONTEXT["Context Tensors"]
        CONDITIONING["Conditioning Info"]
        LABELS["Labels/Keys"]
    end
    
    RAW_DATA --> PREPARE_SCRIPTS
    EXTERNAL --> PREPARE_SCRIPTS
    
    PREPARE_SCRIPTS --> LOAD_FUNCS
    LOAD_FUNCS --> VALIDATION
    
    VALIDATION --> FIT_NORM
    FIT_NORM --> APPLY_NORM
    APPLY_NORM --> STORE_NORM
    
    STORE_NORM --> DATASET_CLASSES
    DATASET_CLASSES --> DATA_MODULES
    DATA_MODULES --> SAMPLERS
    
    SAMPLERS --> TRAIN_LOADER
    SAMPLERS --> VAL_LOADER
    TRAIN_LOADER --> BATCH_DATA
    VAL_LOADER --> BATCH_DATA
    
    BATCH_DATA --> CONTEXT
    BATCH_DATA --> CONDITIONING
    BATCH_DATA --> LABELS
```

Sources: [diffusion/ldm/data/tsg_dataset.py:98-141](), [diffusion/ldm/data/tsg_dataset.py:180-211](), [diffusion/ldm/data/tsg_dataset.py:397-408]()

---

