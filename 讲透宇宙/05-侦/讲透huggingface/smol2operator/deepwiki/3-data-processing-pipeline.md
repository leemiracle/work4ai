<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smol2operator · page 3 Data Processing Pipeline · fetched 2026-10-26 -->

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [preprocessing/aguvis_models.py](preprocessing/aguvis_models.py)
- [preprocessing/aguvis_processor.py](preprocessing/aguvis_processor.py)

</details>



The data processing pipeline transforms raw AGUVIS datasets into standardized, training-ready formats for GUI agent development. This system handles the complete end-to-end workflow from downloading heterogeneous datasets to producing unified, validated training data with consistent action spaces.

This document covers the core data transformation pipeline. For training system integration, see [Training System](#4). For action space unification details, see [Action Space Unification](#3.3).

## Pipeline Architecture Overview

The data processing pipeline operates through several coordinated components that handle dataset downloading, validation, transformation, and upload:

```mermaid
graph TD
    subgraph "Raw Data Sources"
        A[xlangai/aguvis-stage1]
        B[xlangai/aguvis-stage2]
    end
    
    subgraph "AguvisDatasetProcessor"
        C[DatasetDownloader]
        D[SampleProcessor] 
        E[DataProcessor]
        F[SingleConfigProcessor]
    end
    
    subgraph "Data Models Layer"
        G[ConversationDataList]
        H[ConversationData]
        I[ChatMessage]
        J[DataRow]
    end
    
    subgraph "Configuration System"
        K[DatasetConfig]
        L[ProcessingConfig]
        M[CONFIG_DICT_STAGE_1]
        N[CONFIG_DICT_STAGE_2]
    end
    
    subgraph "Processing Operations"
        O[extract_zip_files]
        P[extract_tar_parts_grouped]
        Q[action_conversion]
        R[convert_to_new_action_space]
    end
    
    subgraph "Output Datasets"
        S[smolagents/aguvis-stage-1]
        T[smolagents/aguvis-stage-2]
    end
    
    A --> C
    B --> C
    C --> O
    C --> P
    
    K --> F
    L --> F
    M --> L
    N --> L
    
    F --> D
    F --> E
    
    D --> G
    G --> H
    H --> I
    
    E --> Q
    E --> R
    Q --> J
    R --> J
    
    J --> S
    J --> T
```

**Sources:** [preprocessing/aguvis_processor.py:1-526](), [preprocessing/aguvis_models.py:1-362]()

## Core Processing Workflow

The pipeline executes through a structured sequence of operations managed by the `AguvisDatasetProcessor` class:

```mermaid
flowchart TD
    subgraph "Initialization Phase"
        A[load_dotenv]
        B[huggingface_authenticate]
        C[DatasetDownloader.download_dataset]
    end
    
    subgraph "Extraction Phase"  
        D[extract_zip_files]
        E[extract_tar_parts_grouped]
        F[discover_dataset_config]
    end
    
    subgraph "Processing Phase"
        G[SingleConfigProcessor.process_single_config]
        H[DataProcessor.process_subset]
        I[SampleProcessor.convert_to_chat_format]
        J[SampleProcessor.convert_to_new_action_space]
    end
    
    subgraph "Output Phase"
        K[Dataset.from_list]
        L[concatenate_datasets] 
        M[dataset.push_to_hub]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    
    style G fill:#e8f4f8
    style H fill:#e8f4f8
    style I fill:#e8f4f8
    style J fill:#e8f4f8
```

**Sources:** [preprocessing/aguvis_processor.py:430-492](), [preprocessing/aguvis_processor.py:350-411]()

## Data Models and Validation Layer

The pipeline uses Pydantic models to enforce data consistency and validation throughout the transformation process:

| Model Class | Purpose | Key Validation |
|-------------|---------|----------------|
| `ChatMessage` | Individual conversation turns | Role validation (user/assistant/system) |
| `ConversationData` | Image + conversation pairs | Image path normalization, multi-image handling |
| `ConversationDataList` | Collections with deduplication | Text and image duplicate removal |
| `DataRow` | Final training format | Chat message organization, image attachment |

```mermaid
graph LR
    subgraph "Input Validation"
        A[Raw_JSON_Data]
        B[ConversationDataList.from_json_with_deduplication]
        C[ConversationData.validate_image]
    end
    
    subgraph "Data Transformation"
        D[ConversationEntry.to_chat_message]
        E[ChatMessage.from_conversation_list] 
        F[SampleProcessor.convert_to_chat_format]
    end
    
    subgraph "Output Generation"
        G[DataRow.from_chat_messages]
        H[DataRow.model_dump]
        I[Dataset.from_list]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
```

The `ConversationDataList` model implements sophisticated deduplication logic that can be controlled via the `deduplicate` parameter in `DatasetConfig`:

**Sources:** [preprocessing/aguvis_models.py:81-138](), [preprocessing/aguvis_models.py:141-191]()

## Dataset Configuration Discovery

The pipeline automatically discovers dataset configurations using predefined configuration dictionaries that map JSON files to their corresponding image directories:

```mermaid
graph TD
    subgraph "Stage 1 Configuration"
        A[CONFIG_DICT_STAGE_1]
        B["guienv.json → guienvs/images/"]
        C["omniact.json → omniact/images/"]
        D["seeclick.json → seeclick/seeclick_web_imgs/"]
        E["ui_refexp.json → ui_refexp/images/"]
    end
    
    subgraph "Stage 2 Configuration"
        F[CONFIG_DICT_STAGE_2] 
        G["mind2web-l1.json → mind2web/"]
        H["guiact-web-multi-l1.json → guiact-web-multi-v2/images"]
        I["coat.json → coat/images/"]
        J["aitw-l1.json → aitw-v1/images/"]
    end
    
    subgraph "Processing Logic"
        K[DatasetDownloader.discover_dataset_config]
        L[ProcessingConfig.from_config_dict]
        M[check_subset_exists]
    end
    
    A --> K
    F --> K
    K --> L
    L --> M
    
    style A fill:#f0f8ff
    style F fill:#f0f8ff
```

The `discover_dataset_config` method scans the downloaded dataset directory and creates `ProcessingConfig` objects for each discovered configuration, enabling parallel processing of multiple dataset subsets.

**Sources:** [preprocessing/aguvis_processor.py:132-159](), [preprocessing/aguvis_models.py:240-361]()

## Parallel Processing Architecture

The pipeline supports configurable parallel processing to handle multiple dataset configurations simultaneously:

```mermaid
graph TB
    subgraph "Process Coordination"
        A[AguvisDatasetProcessor.make_dataset_from_original_data]
        B[Pool.starmap]
        C[SingleConfigProcessor.process_single_config]
    end
    
    subgraph "Per-Process Operations"
        D[huggingface_authenticate]
        E[check_subset_exists]
        F[DataProcessor.process_subset]
        G[row_generator]
        H[Dataset.push_to_hub]
    end
    
    subgraph "Memory Management"
        I[gc.collect]
        J[concatenate_datasets]
        K[Dataset.from_list_batched]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    F --> G
    G --> J
    J --> K
    K --> I
    I --> H
    
    style C fill:#fff2cc
    style G fill:#fff2cc
```

Each process handles authentication independently and implements memory management through garbage collection and dataset batching to prevent memory overflow during large dataset processing.

**Sources:** [preprocessing/aguvis_processor.py:454-492](), [preprocessing/aguvis_processor.py:334-411]()

## Sample Processing and Action Conversion

The `SampleProcessor` class handles the core transformation logic, converting raw conversation data into standardized chat formats and applying action space unification:

```mermaid
graph LR
    subgraph "Input Processing"
        A[load_image_from_folder]
        B[convert_to_chat_format]
        C[convert_to_code_agent_format]
    end
    
    subgraph "Action Space Processing"
        D[convert_to_new_action_space]
        E[parse_function_call]
        F[action_conversion]
    end
    
    subgraph "Output Generation"
        G[DataRow.from_chat_messages]
        H[model_dump]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    
    style D fill:#e8f5e8
    style E fill:#e8f5e8  
    style F fill:#e8f5e8
```

The processing pipeline applies different formatting based on the `reasoning` parameter in `DatasetConfig`:
- **Stage 1 (reasoning=False)**: Direct action format without thinking blocks
- **Stage 2 (reasoning=True)**: Wrapped in `<think>` and `<code>` blocks for agentic reasoning

**Sources:** [preprocessing/aguvis_processor.py:163-278](), [preprocessing/aguvis_processor.py:310-332]()

---

