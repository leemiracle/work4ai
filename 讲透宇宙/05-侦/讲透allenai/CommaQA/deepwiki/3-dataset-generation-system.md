<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/CommaQA · page 3 Dataset Generation System · fetched 2026-10-26 -->

# Dataset Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [commaqa/dataset/build_dataset.py](commaqa/dataset/build_dataset.py)
- [commaqa/dataset/build_submodel_datasets.py](commaqa/dataset/build_submodel_datasets.py)
- [scripts/build_commaqav1.sh](scripts/build_commaqav1.sh)
- [scripts/build_datasets.sh](scripts/build_datasets.sh)
- [scripts/build_decompositions.sh](scripts/build_decompositions.sh)
- [scripts/build_docker_image.sh](scripts/build_docker_image.sh)

</details>



## Purpose and Scope

The Dataset Generation System is responsible for creating the CommaQA datasets from configuration files, generating question-answer pairs, building decompositions for training data, and extracting language models. This system produces three main dataset variants: CommaQA-E (explicit reasoning), CommaQA-I (implicit reasoning), and CommaQA-N (numeric reasoning). 

For information about how these datasets are used during inference, see [Inference Engine](#4.1). For details on the execution of operations within generated datasets, see [Operation Executer](#5.1).

## System Architecture

The dataset generation system follows a multi-stage pipeline that transforms JSONNet configuration files into structured datasets with accompanying decompositions and language models.

### Dataset Generation Pipeline Overview

```mermaid
graph TD
    subgraph "Entry Point"
        BUILD_SCRIPT["build_commaqav1.sh<br/>Main Orchestrator"]
    end
    
    subgraph "Dataset Building Stage"
        BUILD_DATASETS["build_datasets.sh<br/>Dataset Builder Script"]
        BUILD_DATASET_PY["build_dataset.py<br/>DatasetBuilder Class"]
        CONFIG_FILES["JSONNet Configurations<br/>movies1.jsonnet, sports.jsonnet, items*.jsonnet"]
    end
    
    subgraph "Decomposition Generation Stage"
        BUILD_DECOMP["build_decompositions.sh<br/>Decomposition Builder"]
        DECOMP_PY["generate_decomposition_predictions.py<br/>Decomposition Generator"]
    end
    
    subgraph "Language Extraction Stage"
        JQ_PROCESSING["jq + sed Processing<br/>Language Pattern Extraction"]
        MODEL_QUESTIONS["model_questions.tsv<br/>Agent Question Templates"]
        OPERATIONS["operations.txt<br/>Available Operations"]
    end
    
    subgraph "Output Datasets"
        COMMAQA_E["CommaQA-E<br/>Explicit Reasoning"]
        COMMAQA_I["CommaQA-I<br/>Implicit Reasoning"] 
        COMMAQA_N["CommaQA-N<br/>Numeric Reasoning"]
        DECOMP_DATA["Decomposition Data<br/>train_seqs for Training"]
        COMPGEN["Compositional Generalization<br/>Test Sets"]
    end
    
    BUILD_SCRIPT --> BUILD_DATASETS
    BUILD_SCRIPT --> BUILD_DECOMP
    BUILD_SCRIPT --> JQ_PROCESSING
    BUILD_SCRIPT --> COMPGEN
    
    BUILD_DATASETS --> BUILD_DATASET_PY
    CONFIG_FILES --> BUILD_DATASET_PY
    BUILD_DATASET_PY --> COMMAQA_E
    BUILD_DATASET_PY --> COMMAQA_I
    BUILD_DATASET_PY --> COMMAQA_N
    
    BUILD_DECOMP --> DECOMP_PY
    COMMAQA_E --> DECOMP_PY
    COMMAQA_I --> DECOMP_PY
    COMMAQA_N --> DECOMP_PY
    DECOMP_PY --> DECOMP_DATA
    
    JQ_PROCESSING --> MODEL_QUESTIONS
    JQ_PROCESSING --> OPERATIONS
```

Sources: [scripts/build_commaqav1.sh:1-67](), [scripts/build_datasets.sh:1-21](), [scripts/build_decompositions.sh:1-21]()

## Main Components

### Dataset Builder Core Logic

The `DatasetBuilder` class in `build_dataset.py` implements the core dataset generation logic. It processes multiple `DatasetBuildConfig` objects to create structured question-answer datasets.

```mermaid
graph TB
    subgraph "DatasetBuilder Class"
        DATASET_BUILDER["DatasetBuilder.__init__<br/>configs: List[DatasetBuildConfig]"]
        BUILD_METHOD["build_dataset()<br/>Main Generation Method"]
    end
    
    subgraph "Configuration Processing"
        CONFIG_SAMPLING["Config Sampling<br/>config_distribution logic"]
        ENTITY_SAMPLING["Entity Sampling<br/>entities.subsample()"]
        KB_BUILDING["KB Building<br/>pred.populate_kb()"]
    end
    
    subgraph "Question Generation"
        MODEL_LIBRARY["build_models()<br/>Model Library Creation"]
        THEORY_PROCESSING["Theory Processing<br/>theory.create_questions()"]
        QA_SUBSAMPLING["QA Subsampling<br/>Equal distribution per theory"]
    end
    
    subgraph "Output Generation"
        CONTEXT_BUILDING["Context Building<br/>complete_kb_fact_map"]
        FINAL_OUTPUT["Final Output<br/>kb, context, qa_pairs"]
    end
    
    DATASET_BUILDER --> BUILD_METHOD
    BUILD_METHOD --> CONFIG_SAMPLING
    CONFIG_SAMPLING --> ENTITY_SAMPLING
    ENTITY_SAMPLING --> KB_BUILDING
    KB_BUILDING --> MODEL_LIBRARY
    MODEL_LIBRARY --> THEORY_PROCESSING
    THEORY_PROCESSING --> QA_SUBSAMPLING
    QA_SUBSAMPLING --> CONTEXT_BUILDING
    CONTEXT_BUILDING --> FINAL_OUTPUT
```

Sources: [commaqa/dataset/build_dataset.py:37-129]()

### Dataset Generation Workflow

The system generates datasets through a structured process that ensures balanced representation across different reasoning types:

| Stage | Process | Key Components |
|-------|---------|---------------|
| **Configuration** | Load JSONNet configs | `DatasetBuildConfig`, `_jsonnet.evaluate_file()` |
| **Entity Sampling** | Sample entities per group | `entities.subsample()`, `entity_percent` parameter |
| **KB Population** | Build knowledge base | `pred.populate_kb()`, `complete_kb` |
| **Model Library** | Initialize execution models | `build_models()` from `execution.utils` |
| **Question Generation** | Create QA pairs | `theory.create_questions()` |
| **Balancing** | Equalize across theories | `random.sample()`, `min_size` calculation |
| **Output** | Generate train/dev/test | 80%/10%/10% split |

Sources: [commaqa/dataset/build_dataset.py:41-129]()

### Decomposition Generation System

```mermaid
graph LR
    subgraph "Input Processing"
        TRAIN_JSON["train.json<br/>Generated Dataset"]
        DEV_JSON["dev.json<br/>Generated Dataset"] 
        TEST_JSON["test.json<br/>Generated Dataset"]
    end
    
    subgraph "Decomposition Generation"
        DECOMP_SCRIPT["build_decompositions.sh<br/>Orchestrator Script"]
        DECOMP_PY["generate_decomposition_predictions.py<br/>Decomposition Logic"]
    end
    
    subgraph "Output Processing"
        DECOMP_TRAIN["train.json<br/>With Decompositions"]
        DECOMP_DEV["dev.json<br/>With Decompositions"]
        DECOMP_TEST["test.json<br/>With Decompositions"]
    end
    
    TRAIN_JSON --> DECOMP_SCRIPT
    DEV_JSON --> DECOMP_SCRIPT
    TEST_JSON --> DECOMP_SCRIPT
    
    DECOMP_SCRIPT --> DECOMP_PY
    DECOMP_PY --> DECOMP_TRAIN
    DECOMP_PY --> DECOMP_DEV
    DECOMP_PY --> DECOMP_TEST
```

Sources: [scripts/build_decompositions.sh:1-21](), [scripts/build_commaqav1.sh:20-32]()

## Configuration System

The dataset generation system is driven by JSONNet configuration files that define entities, predicates, theories, and predicate language configurations. These configurations are processed by the `DatasetBuildConfig` class.

### Configuration File Structure

```mermaid
graph TD
    subgraph "JSONNet Configuration Files"
        MOVIES1["movies1.jsonnet<br/>Explicit Reasoning Config"]
        MOVIES2["movies2.jsonnet<br/>Explicit Reasoning Config"]
        SPORTS["sports.jsonnet<br/>Numeric Reasoning Config"]
        ITEMS["items0-5.jsonnet<br/>Implicit Reasoning Configs"]
    end
    
    subgraph "Configuration Components"
        ENTITIES["entities<br/>Actor, Movie, etc."]
        PREDICATES["predicates<br/>Relations and Facts"]
        THEORIES["theories<br/>Question Templates"]
        PRED_LANG["predicate_language<br/>Model Configurations"]
    end
    
    subgraph "Processing"
        DATASET_CONFIG["DatasetBuildConfig<br/>Configuration Parser"]
        BUILD_MODELS["build_models()<br/>Model Library Creation"]
    end
    
    MOVIES1 --> DATASET_CONFIG
    MOVIES2 --> DATASET_CONFIG
    SPORTS --> DATASET_CONFIG
    ITEMS --> DATASET_CONFIG
    
    DATASET_CONFIG --> ENTITIES
    DATASET_CONFIG --> PREDICATES
    DATASET_CONFIG --> THEORIES
    DATASET_CONFIG --> PRED_LANG
    
    PRED_LANG --> BUILD_MODELS
```

Sources: [scripts/build_commaqav1.sh:4-17](), [commaqa/dataset/build_dataset.py:149-162]()

## Language Extraction Process

The system extracts language patterns and operation templates from generated datasets using `jq` and `sed` processing to create reusable components for model training.

### Language Processing Pipeline

```mermaid
graph TB
    subgraph "Source Data Processing"
        PRED_LANG_EXTRACT["jq -r '.predicate_language[]|[.model, .questions[]]|@tsv'<br/>Extract Model Questions"]
        SED_PROCESSING["sed 's/$[0-9]/__/g'<br/>Normalize Variable References"]
        SORT_UNIQUE["sort -u<br/>Deduplicate Results"]
    end
    
    subgraph "Training Data Processing"
        DECOMP_EXTRACT["jq -r '.[].qa_pairs[].decomposition[]|[.m, .q]|@tsv'<br/>Extract Decomposition Steps"]
        OP_EXTRACT["jq -r '.[].qa_pairs[].decomposition[].op'<br/>Extract Operations"]
        NORMALIZE["sed 's/[$#][0-9]/__/g'<br/>Normalize Variables"]
    end
    
    subgraph "Output Files"
        MODEL_QUESTIONS_TSV["model_questions.tsv<br/>Model-Question Pairs"]
        OPERATIONS_TXT["operations.txt<br/>Available Operations"]
        RESTRICTED_LANG["restricted_language/<br/>Training-specific Language"]
    end
    
    PRED_LANG_EXTRACT --> SED_PROCESSING
    SED_PROCESSING --> SORT_UNIQUE
    SORT_UNIQUE --> MODEL_QUESTIONS_TSV
    
    DECOMP_EXTRACT --> NORMALIZE
    OP_EXTRACT --> NORMALIZE
    NORMALIZE --> RESTRICTED_LANG
    NORMALIZE --> OPERATIONS_TXT
```

Sources: [scripts/build_commaqav1.sh:34-56]()

## Docker Environment

The dataset generation system includes Docker support for consistent, reproducible builds across different environments.

### Docker Configuration

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Base Image** | `python:3.8` | Python runtime environment |
| **Environment** | `LC_ALL=C.UTF-8`, `LANG=C.UTF-8` | Unicode support |
| **NVIDIA Support** | `NVIDIA_VISIBLE_DEVICES all` | GPU access for model execution |
| **Dependencies** | `requirements.txt` | Python package installation |
| **NLTK Data** | `stopwords`, `punkt` | Natural language processing |
| **Working Directory** | `/stage/` | Container workspace |

Sources: [Dockerfile:1-28](), [scripts/build_docker_image.sh:1-16]()

### Container Build Process

```mermaid
graph LR
    subgraph "Build Process"
        GIT_HASH["git log --format='%h' -n 1<br/>Extract Git Hash"]
        IMAGE_NAME["IMAGE_NAME_USER-HASH<br/>Generate Image Name"]
        DOCKER_BUILD["docker build -f Dockerfile<br/>Build Container"]
    end
    
    subgraph "Container Setup"
        BASE_INSTALL["apt-get install gettext-base<br/>System Dependencies"]
        PIP_INSTALL["pip install -r requirements.txt<br/>Python Dependencies"]
        NLTK_DOWNLOAD["python -m nltk.downloader<br/>stopwords, punkt"]
        COPY_CODE["COPY commaqa/ commaqa/<br/>Application Code"]
    end
    
    GIT_HASH --> IMAGE_NAME
    IMAGE_NAME --> DOCKER_BUILD
    DOCKER_BUILD --> BASE_INSTALL
    BASE_INSTALL --> PIP_INSTALL
    PIP_INSTALL --> NLTK_DOWNLOAD
    NLTK_DOWNLOAD --> COPY_CODE
```

Sources: [scripts/build_docker_image.sh:1-16](), [Dockerfile:1-28]()

## Output Dataset Structure

The dataset generation system produces structured JSON files with specific schemas for different reasoning types.

### Dataset Output Schema

Each generated dataset follows a consistent structure:

```mermaid
graph TD
    subgraph "Dataset Group Structure"
        GROUP["Dataset Group<br/>Single Knowledge Base"]
        KB["kb<br/>Complete Knowledge Base"]
        CONTEXT["context<br/>Textual Representation"]
        FACT_MAP["per_fact_context<br/>Fact-to-Text Mapping"]
        PRED_LANG["pred_lang_config<br/>Model Configuration"]
        QA_PAIRS["qa_pairs<br/>Selected Questions"]
        ALL_QA["all_qa<br/>All Generated Questions"]
    end
    
    subgraph "Question-Answer Structure"
        QUESTION["question<br/>Natural Language Query"]
        ANSWER["answer<br/>Expected Response"]
        DECOMPOSITION["decomposition<br/>Step-by-step Reasoning"]
        FACTS_USED["facts_used<br/>Knowledge Base References"]
    end
    
    GROUP --> KB
    GROUP --> CONTEXT
    GROUP --> FACT_MAP
    GROUP --> PRED_LANG
    GROUP --> QA_PAIRS
    GROUP --> ALL_QA
    
    QA_PAIRS --> QUESTION
    QA_PAIRS --> ANSWER
    QA_PAIRS --> DECOMPOSITION
    QA_PAIRS --> FACTS_USED
```

Sources: [commaqa/dataset/build_dataset.py:75-120]()

### Dataset Variants

| Dataset Type | Configuration | Purpose | Output Location |
|--------------|---------------|---------|-----------------|
| **CommaQA-E** | `explicit/movies1.jsonnet`, `movies2.jsonnet` | Explicit reasoning over movie entities | `output/commaqav1/explicit/commaqa/` |
| **CommaQA-I** | `implicit/items0-5.jsonnet` | Implicit reasoning over item entities | `output/commaqav1/implicit/commaqa/` |
| **CommaQA-N** | `numeric/sports.jsonnet` | Numeric reasoning over sports entities | `output/commaqav1/numeric/commaqa/` |
| **Compositional** | `*_compgen.jsonnet` | Generalization testing | `output/commaqav1/compgen/` |

Sources: [scripts/build_commaqav1.sh:4-67]()

---

