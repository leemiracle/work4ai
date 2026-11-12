<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/molmoact · page 3 Data Management System · fetched 2026-10-26 -->

# Data Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



The Data Management System handles the acquisition, storage, and organization of training data for MolmoAct. It provides download infrastructure for three primary data categories: robot demonstration datasets, multimodal web data, and LIBERO task suites. The system emphasizes resumability, parallel processing, and verification to support multi-stage training pipelines across distributed computing environments.

For information about how datasets are used in training stages, see [Training Pipeline](#2). For LIBERO-specific dataset handling and task definitions, see [LIBERO Dataset Management](#3.3).

## Environment Configuration

The data management system relies on three environment variables to control data storage locations and download behavior:

| Environment Variable | Purpose | Example Value | Configuration Location |
|---------------------|---------|---------------|----------------------|
| `HF_HOME` | Hugging Face cache directory for datasets | `/data/molmoact/huggingface` | User shell environment |
| `MOLMOACT_DATA_DIR` | Root directory for additional assets not in HF cache | `/data/molmoact` | User shell environment |
| `HF_DATASETS_OFFLINE` | Prevents online dataset loading during training (rate limiting protection) | `1` | Training launch environment |

The `HF_HOME` variable controls where Hugging Face Datasets library caches downloaded data. This cache is shared across all download scripts and training runs. The `MOLMOACT_DATA_DIR` provides storage for auxiliary assets that don't fit the Hugging Face Datasets model.

```bash
export MOLMOACT_DATA_DIR=/data/molmoact
export HF_HOME=/data/molmoact/huggingface
```

Setting `HF_DATASETS_OFFLINE=1` during distributed training prevents all nodes from simultaneously attempting to download datasets, which can trigger rate limiting from Hugging Face servers. This requires pre-downloading all data before training begins.

**Sources:** [README.md:113-124]()

## Data Sources and Mixtures

MolmoAct training uses three primary data mixtures, each serving a different stage in the curriculum learning pipeline:

| Data Mixture | Training Stage | Contents | Hugging Face Path |
|-------------|----------------|----------|-------------------|
| MolmoAct Pre-training Mixture | Pre-training | Subset of OXE formatted as Action Reasoning data, auxiliary robot data, web data | `allenai/MolmoAct-Pretraining-Mixture` |
| MolmoAct Mid-training Mixture | Mid-training | MolmoAct Dataset formatted as Action Reasoning data | `allenai/MolmoAct-Midtraining-Mixture` |
| MolmoAct Dataset | Mid-training (source) | In-house collected data in LeRobot format | `allenai/MolmoAct-Dataset` |

### Data Source Architecture

```mermaid
graph TB
    subgraph "External Sources"
        HF_API["Hugging Face API<br/>(datasets library)"]
        DIRECT_URL["Direct URL Downloads<br/>(wget/requests)"]
        MANUAL["Manual Downloads<br/>(user-provided)"]
    end
    
    subgraph "Download Scripts"
        ROBOT_SCRIPT["scripts/download_robot_data.py"]
        WEB_SCRIPT["scripts/download_data.py"]
        LIBERO_SCRIPT["experiments/LIBERO/benchmark_scripts/<br/>download_libero_datasets.py"]
    end
    
    subgraph "Data Categories"
        ROBOT_STAGES["Robot Data by Stage<br/>pretrain/midtrain/libero"]
        WEB_DATASETS["Web Datasets<br/>Pixmo/ChartQA/TextCaps"]
        LIBERO_SUITES["LIBERO Task Suites<br/>spatial/object/goal/100"]
    end
    
    subgraph "Storage Layer"
        HF_CACHE["$HF_HOME cache<br/>(Hugging Face datasets)"]
        DATA_DIR["$MOLMOACT_DATA_DIR<br/>(additional assets)"]
    end
    
    HF_API --> ROBOT_SCRIPT
    HF_API --> WEB_SCRIPT
    HF_API --> LIBERO_SCRIPT
    DIRECT_URL --> WEB_SCRIPT
    MANUAL --> WEB_DATASETS
    
    ROBOT_SCRIPT --> ROBOT_STAGES
    WEB_SCRIPT --> WEB_DATASETS
    LIBERO_SCRIPT --> LIBERO_SUITES
    
    ROBOT_STAGES --> HF_CACHE
    WEB_DATASETS --> HF_CACHE
    WEB_DATASETS --> DATA_DIR
    LIBERO_SUITES --> DATA_DIR
    
    style ROBOT_SCRIPT fill:#e8e8e8
    style WEB_SCRIPT fill:#e8e8e8
    style LIBERO_SCRIPT fill:#e8e8e8
```

**Sources:** [README.md:70-77]()

## Download Infrastructure

### Robot Data Download Script

The `scripts/download_robot_data.py` script provides stage-based filtering for robot demonstration datasets. It supports downloading data for specific training stages or individual dataset classes.

```mermaid
graph LR
    subgraph "Script Entry Points"
        ALL_CMD["python3 scripts/download_robot_data.py all"]
        STAGE_CMD["python3 scripts/download_robot_data.py &lt;stage&gt;"]
        CLASS_CMD["python3 scripts/download_robot_data.py &lt;ClassName&gt;"]
    end
    
    subgraph "Stage Filters"
        PRETRAIN_FILTER["pretrain stage"]
        MIDTRAIN_FILTER["midtrain stage"]
        LIBERO_FILTER["libero stage"]
    end
    
    subgraph "Dataset Classes"
        DATASET_REGISTRY["olmo/data/robot_datasets.py<br/>dataset class definitions"]
        HOME_PRIMARY["MolmoActDatasetHomePrimary"]
        OTHER_CLASSES["...other dataset classes"]
    end
    
    subgraph "Download Parameters"
        N_PROC["--n_proc<br/>(parallel workers)"]
        RESUME["Resumable downloads<br/>(checkpointing)"]
    end
    
    ALL_CMD --> PRETRAIN_FILTER
    ALL_CMD --> MIDTRAIN_FILTER
    ALL_CMD --> LIBERO_FILTER
    STAGE_CMD --> PRETRAIN_FILTER
    STAGE_CMD --> MIDTRAIN_FILTER
    STAGE_CMD --> LIBERO_FILTER
    CLASS_CMD --> DATASET_REGISTRY
    
    PRETRAIN_FILTER --> DATASET_REGISTRY
    MIDTRAIN_FILTER --> DATASET_REGISTRY
    LIBERO_FILTER --> DATASET_REGISTRY
    
    DATASET_REGISTRY --> HOME_PRIMARY
    DATASET_REGISTRY --> OTHER_CLASSES
    
    N_PROC --> ALL_CMD
    N_PROC --> STAGE_CMD
    N_PROC --> CLASS_CMD
    RESUME --> ALL_CMD
    RESUME --> STAGE_CMD
    RESUME --> CLASS_CMD
```

**Usage Examples:**

```bash
# Download all robot datasets with 16 parallel workers
python3 scripts/download_robot_data.py all --n_proc 16

# Download only pre-training stage datasets
python3 scripts/download_robot_data.py pretrain --n_proc 16

# Download specific dataset class
python3 scripts/download_robot_data.py MolmoActDatasetHomePrimary --n_proc 16
```

Valid stage identifiers: `pretrain`, `midtrain`, `libero`

Dataset class names are defined at the end of `olmo/data/robot_datasets.py`. The script uses these classes to determine which datasets belong to each training stage.

**Sources:** [README.md:127-147]()

### Web Data Download Script

The `scripts/download_data.py` script handles multimodal web datasets used during pre-training. Some datasets require URL fetching, which can be time-intensive.

```bash
# Download all web datasets
python3 scripts/download_data.py all --n_proc 16

# Download specific dataset
python3 scripts/download_data.py ChartQa --n_proc 16
```

**Special Cases:**

| Dataset | Special Requirement | Handling |
|---------|-------------------|----------|
| Pixmo datasets | Fetch images from URLs | Automatic but can take up to 24 hours |
| InfoQa | Manual download required | Script raises error if missing |
| Scene-Text | Manual download required | Script raises error if missing |
| Android Control | TFRecord parsing | Requires extra dependencies |

The `--n_proc` parameter controls parallelism. Higher values speed up downloads but increase risk of rate limiting from external sources.

**Sources:** [README.md:150-172]()

### LIBERO Dataset Download Script

The `experiments/LIBERO/benchmark_scripts/download_libero_datasets.py` script manages LIBERO task suite data downloads with Hugging Face integration.

```mermaid
graph TB
    subgraph "CLI Arguments"
        DOWNLOAD_DIR["--download-dir<br/>(default: get_libero_path('datasets'))"]
        DATASETS_ARG["--datasets<br/>(all/libero_goal/libero_spatial/<br/>libero_object/libero_100)"]
        USE_HF["--use-huggingface<br/>(preferred source)"]
    end
    
    subgraph "Script Functions"
        PARSE_ARGS["parse_args()"]
        MAIN["main()"]
        LIBERO_DOWNLOAD["download_utils.libero_dataset_download()"]
        CHECK_DATASET["download_utils.check_libero_dataset()"]
    end
    
    subgraph "Path Resolution"
        GET_PATH["get_libero_path('datasets')"]
        LIBERO_ROOT["LIBERO_ROOT env variable"]
    end
    
    subgraph "Download Sources"
        HF_SOURCE["Hugging Face Hub"]
        ORIGINAL_LINKS["Original Download Links<br/>(may expire)"]
    end
    
    subgraph "LIBERO Suites"
        SPATIAL["libero_spatial"]
        OBJECT["libero_object"]
        GOAL["libero_goal"]
        LIBERO100["libero_100"]
    end
    
    DOWNLOAD_DIR --> PARSE_ARGS
    DATASETS_ARG --> PARSE_ARGS
    USE_HF --> PARSE_ARGS
    PARSE_ARGS --> MAIN
    
    MAIN --> GET_PATH
    GET_PATH --> LIBERO_ROOT
    
    MAIN --> LIBERO_DOWNLOAD
    USE_HF --> HF_SOURCE
    USE_HF -.fallback.-> ORIGINAL_LINKS
    HF_SOURCE --> LIBERO_DOWNLOAD
    ORIGINAL_LINKS --> LIBERO_DOWNLOAD
    
    LIBERO_DOWNLOAD --> SPATIAL
    LIBERO_DOWNLOAD --> OBJECT
    LIBERO_DOWNLOAD --> GOAL
    LIBERO_DOWNLOAD --> LIBERO100
    
    LIBERO_DOWNLOAD --> CHECK_DATASET
    
    style LIBERO_DOWNLOAD fill:#e8e8e8
    style CHECK_DATASET fill:#e8e8e8
```

**Script Structure:**

The script uses `libero.libero.get_libero_path("datasets")` to resolve the download directory, which checks for a `LIBERO_ROOT` environment variable or uses a default location. The `--use-huggingface` flag (recommended) switches from original download links to Hugging Face as the data source.

```bash
python3 experiments/LIBERO/benchmark_scripts/download_libero_datasets.py \
    --datasets all \
    --use-huggingface
```

After downloading, the script automatically calls `download_utils.check_libero_dataset()` to verify dataset integrity.

**Sources:** [experiments/LIBERO/benchmark_scripts/download_libero_datasets.py:1-67]()

## Storage and Verification Infrastructure

### Caching Mechanism

All downloads use the Hugging Face Datasets caching system at `$HF_HOME`. The cache stores:
- Downloaded dataset files (raw data)
- Processed dataset builders
- Arrow format tables for fast loading

Cache benefits:
- Shared across multiple training runs
- Supports partial downloads and resumption
- Automatic deduplication of identical data

### Parallel Processing

The `--n_proc` parameter enables parallel downloading across multiple workers:

| Worker Count | Use Case | Rate Limiting Risk |
|-------------|----------|-------------------|
| 1-4 | Conservative, stable | Low |
| 8-16 | Recommended for most cases | Medium |
| 32+ | Fast but risky | High |

Parallel processing is particularly important for large datasets like Pixmo, which fetches thousands of individual images from URLs.

### Resumability

All download scripts support interruption and resumption. If a download is cancelled or fails:
1. Already-downloaded files remain in cache
2. Next run detects existing files
3. Only missing files are downloaded

This is implemented through the Hugging Face Datasets library's built-in caching layer.

### Verification Strategy

Dataset integrity is verified through:

| Verification Method | Datasets | Implementation |
|-------------------|----------|----------------|
| SHA-1 checksums | LIBERO datasets | `experiments/LIBERO/benchmark_scripts/shasum_files.py` |
| Size validation | HF datasets | Automatic via Datasets library |
| Content checks | LIBERO task suites | `download_utils.check_libero_dataset()` |

The LIBERO verification script checks that all expected task demonstration files exist after download.

**Sources:** [README.md:165-172](), [experiments/LIBERO/benchmark_scripts/download_libero_datasets.py:49-63]()

## Dataset Organization

### Stage-Based Organization

Robot datasets are organized by training stage to enable selective downloading:

```mermaid
graph TB
    subgraph "Dataset Registry"
        ROBOT_PY["olmo/data/robot_datasets.py"]
    end
    
    subgraph "Pre-training Stage"
        PRE_ROBOT["Robot demonstration datasets<br/>(OpenX, BridgeData, RT-1, DROID)"]
        PRE_WEB["Multimodal web data<br/>(Pixmo, ChartQA, TextCaps)"]
    end
    
    subgraph "Mid-training Stage"
        MID_DATA["MolmoAct Dataset<br/>(Action Reasoning format)"]
    end
    
    subgraph "Post-training Stage (LIBERO)"
        LIBERO_SPATIAL["libero_spatial suite"]
        LIBERO_OBJECT["libero_object suite"]
        LIBERO_GOAL["libero_goal suite"]
        LIBERO_100["libero_100 suite"]
    end
    
    ROBOT_PY --> PRE_ROBOT
    ROBOT_PY --> MID_DATA
    
    PRE_ROBOT -.used in.-> PRE_STAGE["Stage 1: Pre-training<br/>(100k steps, 256 GPUs)"]
    PRE_WEB -.used in.-> PRE_STAGE
    
    MID_DATA -.used in.-> MID_STAGE["Stage 2: Mid-training<br/>(50k steps, 128 GPUs)"]
    
    LIBERO_SPATIAL -.used in.-> POST_STAGE["Stage 3: Post-training<br/>(40k-80k steps, 64 GPUs)"]
    LIBERO_OBJECT -.used in.-> POST_STAGE
    LIBERO_GOAL -.used in.-> POST_STAGE
    LIBERO_100 -.used in.-> POST_STAGE
    
    style PRE_STAGE fill:#e8e8e8
    style MID_STAGE fill:#e8e8e8
    style POST_STAGE fill:#e8e8e8
```

### Dataset Categories and Locations

| Category | Storage Location | Access Method |
|----------|-----------------|---------------|
| Robot datasets (HF) | `$HF_HOME/datasets/` | Hugging Face Datasets API |
| Web datasets (HF) | `$HF_HOME/datasets/` | Hugging Face Datasets API |
| Additional web assets | `$MOLMOACT_DATA_DIR/` | Direct file access |
| LIBERO demonstrations | `$LIBERO_ROOT/datasets/` or `get_libero_path("datasets")` | LIBERO API |

### Multi-Stage Training Data Flow

```mermaid
graph LR
    subgraph "Data Sources"
        CAPTIONER["MolmoAct-7B-D-Captioner<br/>(starting checkpoint)"]
        PRE_DATA["Pre-training Data<br/>(robot + web mixtures)"]
        MID_DATA["Mid-training Data<br/>(MolmoAct Dataset)"]
        POST_DATA["Post-training Data<br/>(LIBERO task suites)"]
    end
    
    subgraph "Download Scripts"
        DL_ROBOT["download_robot_data.py<br/>(--stage pretrain/midtrain)"]
        DL_WEB["download_data.py<br/>(--dataset all)"]
        DL_LIBERO["download_libero_datasets.py<br/>(--datasets all)"]
    end
    
    subgraph "Training Stages"
        STAGE1["Stage 1: Pre-training<br/>molmoact-pretrain config"]
        STAGE2["Stage 2: Mid-training<br/>molmoact-midtrain config"]
        STAGE3["Stage 3: Post-training<br/>libero-&lt;suite&gt; config"]
    end
    
    DL_ROBOT -.pretrain.-> PRE_DATA
    DL_WEB --> PRE_DATA
    DL_ROBOT -.midtrain.-> MID_DATA
    DL_ROBOT -.libero.-> POST_DATA
    DL_LIBERO --> POST_DATA
    
    CAPTIONER --> STAGE1
    PRE_DATA --> STAGE1
    STAGE1 --> STAGE2
    MID_DATA --> STAGE2
    STAGE2 --> STAGE3
    POST_DATA --> STAGE3
```

The stage-based organization enables:
1. **Incremental downloads**: Download only data needed for current training stage
2. **Storage optimization**: Avoid downloading all datasets upfront
3. **Development iteration**: Test on smaller dataset subsets before full-scale training

**Sources:** [README.md:127-147](), [README.md:174-296]()

## Rate Limiting and Offline Mode

During distributed training, setting `HF_DATASETS_OFFLINE=1` prevents simultaneous dataset loading across compute nodes:

```bash
export HF_DATASETS_OFFLINE=1
```

This is critical when running on 16-256 GPUs across multiple nodes, as each process would otherwise attempt to verify dataset availability via Hugging Face API, triggering rate limits.

**Pre-download workflow:**
1. Download all required datasets on a single machine or with controlled parallelism
2. Verify cache exists at `$HF_HOME`
3. Set `HF_DATASETS_OFFLINE=1` in training environment
4. Launch distributed training

**Sources:** [README.md:171-172]()

---

