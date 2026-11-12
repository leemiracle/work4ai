<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/large-scale-image-deduplication · page 5 Setup & Configuration · fetched 2026-10-26 -->

# Setup & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [requirements.txt](requirements.txt)

</details>



This document provides guidance for setting up the Large-Scale Image Deduplication Toolkit, including system requirements, dependency installation, project structure, and understanding how data flows through the various components. This covers the foundational setup needed before using any of the analysis tools.

For detailed information about specific processing systems, see [Embedding Generation System](#2). For information about using the analysis tools after setup, see [Analysis & Deduplication Tools](#3).

## System Requirements and Dependencies

The toolkit requires a Python environment with deep learning capabilities, particularly PyTorch and GPU support for efficient processing. The system is designed to work with large-scale datasets and requires substantial computational resources.

### Core Dependencies

The toolkit relies on several key dependency categories that enable its functionality:

```mermaid
graph TB
    subgraph "Deep Learning Framework"
        PYTORCH["pytorch-lightning>=1.5.7"]
        LIGHTNING_BOLTS["lightning-bolts>=0.4.0"]
        TORCH["torch"]
        TORCHVISION["torchvision"]
        TORCHMETRICS["torchmetrics"]
    end
    
    subgraph "Computer Vision & Models"
        CLASSY["classy_vision"]
        TRANSFORMERS["transformers"]
        PILLOW["Pillow"]
    end
    
    subgraph "Scientific Computing"
        NUMPY["numpy"]
        PANDAS["pandas"]
        SKLEARN["scikit-learn"]
        UMAP["umap-learn"]
    end
    
    subgraph "Similarity Search & GPU"
        FAISS["faiss-gpu"]
        AUGLY["augly"]
    end
    
    subgraph "Data & Visualization"
        DATASETS["datasets"]
        MATPLOTLIB["matplotlib"]
        TENSORBOARD["tensorboard"]
        TQDM["tqdm"]
    end
    
    PYTORCH --> TORCH
    PYTORCH --> TORCHVISION
    LIGHTNING_BOLTS --> PYTORCH
    CLASSY --> TORCH
    TRANSFORMERS --> TORCH
    SKLEARN --> NUMPY
    UMAP --> SKLEARN
    FAISS --> NUMPY
```

*Sources: [requirements.txt:1-19]()*

### Dependency Mapping to System Components

The dependencies directly support specific toolkit functionalities:

| Component | Primary Dependencies | Purpose |
|-----------|---------------------|---------|
| `compute_embeddings.py` | `torch`, `torchvision`, `pytorch-lightning` | SSCD model inference and GPU acceleration |
| `dedup_dataset.py` | `scikit-learn`, `numpy`, `faiss-gpu` | Similarity computation and duplicate detection |
| `cluster_embeddings.py` | `umap-learn`, `scikit-learn`, `transformers` | Dimensionality reduction and semantic labeling |
| `find_similar_images.py` | `faiss-gpu`, `matplotlib`, `Pillow` | Fast similarity search and visualization |
| Data loading | `datasets`, `pandas`, `Pillow` | HuggingFace dataset integration and image processing |
| Visualization | `matplotlib`, `tensorboard` | Result visualization and progress tracking |

*Sources: [requirements.txt:1-19]()*

## Project Structure and Data Organization

The toolkit follows a structured directory layout that separates different types of data and outputs. Understanding this structure is essential for configuring and using the system effectively.

### Directory Structure

```mermaid
graph TD
    ROOT["/"] --> SCRIPTS["Python Scripts"]
    ROOT --> DATA["/data/"]
    ROOT --> MODELS["/models/"]
    ROOT --> EMBEDDINGS["/embeddings*/"]
    ROOT --> OUTPUT["/output/"]
    ROOT --> DUPLICATES["/duplicates/"]
    ROOT --> ASSETS["Generated Assets"]
    
    SCRIPTS --> COMPUTE["compute_embeddings.py"]
    SCRIPTS --> DEDUP["dedup_dataset.py"]
    SCRIPTS --> CLUSTER["cluster_embeddings.py"]
    SCRIPTS --> FIND["find_similar_images.py"]
    SCRIPTS --> RUN["run_lmms_embeddings.py"]
    SCRIPTS --> COUNT["count_embeddings.py"]
    
    DATA --> RAW_DATASETS["Raw Dataset Files"]
    MODELS --> SSCD_MODEL["sscd_disc_mixup.torchscript.pt"]
    EMBEDDINGS --> NPY_FILES["*.npy embedding arrays"]
    EMBEDDINGS --> ID_FILES["Image ID mappings"]
    OUTPUT --> PROCESSING_RESULTS["Processing outputs"]
    DUPLICATES --> DUPLICATE_REPORTS["JSON reports"]
    ASSETS --> VISUALIZATIONS["*.png visualizations"]
```

*Sources: [.gitignore:1-11]()*

### Data Flow Architecture

The system processes data through several stages, with each stage producing artifacts consumed by subsequent stages:

```mermaid
graph LR
    subgraph "Input Sources"
        HF_DATASETS["HuggingFace Datasets"]
        LOCAL_IMAGES["Local Image Files"]
        LMMS_DATASETS["LMMS-Lab Datasets"]
    end
    
    subgraph "Processing Storage"
        DATA_DIR["/data/"]
        MODELS_DIR["/models/"]
    end
    
    subgraph "Core Processing"
        COMPUTE["compute_embeddings.py"]
        SSCD["sscd_disc_mixup.torchscript.pt"]
    end
    
    subgraph "Embedding Storage"
        EMBEDDINGS_DIR["/embeddings*/"]
        NPY_ARRAYS["*.npy arrays"]
        ID_MAPPINGS["Image ID files"]
    end
    
    subgraph "Analysis Tools"
        DEDUP["dedup_dataset.py"]
        CLUSTER["cluster_embeddings.py"] 
        FIND["find_similar_images.py"]
        COUNT["count_embeddings.py"]
    end
    
    subgraph "Output Artifacts"
        OUTPUT_DIR["/output/"]
        DUPLICATES_DIR["/duplicates/"]
        VISUALIZATIONS["*.png files"]
        REPORTS["JSON reports"]
    end
    
    HF_DATASETS --> DATA_DIR
    LOCAL_IMAGES --> DATA_DIR
    LMMS_DATASETS --> DATA_DIR
    
    DATA_DIR --> COMPUTE
    MODELS_DIR --> COMPUTE
    COMPUTE --> SSCD
    SSCD --> EMBEDDINGS_DIR
    EMBEDDINGS_DIR --> NPY_ARRAYS
    EMBEDDINGS_DIR --> ID_MAPPINGS
    
    NPY_ARRAYS --> DEDUP
    NPY_ARRAYS --> CLUSTER
    NPY_ARRAYS --> FIND
    NPY_ARRAYS --> COUNT
    ID_MAPPINGS --> FIND
    ID_MAPPINGS --> CLUSTER
    
    DEDUP --> DUPLICATES_DIR
    CLUSTER --> VISUALIZATIONS
    FIND --> VISUALIZATIONS
    DEDUP --> REPORTS
    CLUSTER --> OUTPUT_DIR
```

*Sources: [.gitignore:1-15]()*

## Configuration and Setup Workflow

### Initial Setup Steps

The typical setup workflow involves preparing the environment and understanding the data flow:

1. **Environment Preparation**: Install dependencies from `requirements.txt`
2. **Model Acquisition**: Obtain the SSCD model file (`sscd_disc_mixup.torchscript.pt`)
3. **Directory Structure**: Ensure proper directory structure exists
4. **GPU Configuration**: Verify CUDA and GPU acceleration capabilities
5. **Data Preparation**: Organize input datasets appropriately

### Critical Configuration Points

```mermaid
graph TB
    subgraph "Environment Configuration"
        PYTHON_ENV["Python Environment"]
        GPU_SETUP["CUDA/GPU Setup"]
        DEPS["Dependencies Installation"]
    end
    
    subgraph "Model Configuration"
        SSCD_PATH["SSCD Model Path"]
        MODEL_LOCATION["/models/ directory"]
        TORCH_SCRIPT["TorchScript format"]
    end
    
    subgraph "Storage Configuration"
        EMBEDDINGS_PATH["Embedding output paths"]
        DATA_PATHS["Input data locations"]
        OUTPUT_PATHS["Result output directories"]
        TEMP_STORAGE["Temporary processing space"]
    end
    
    subgraph "Processing Configuration"
        BATCH_SIZE["Batch size settings"]
        NUM_WORKERS["Data loader workers"]
        MEMORY_MANAGEMENT["GPU memory handling"]
        PROGRESS_TRACKING["Progress monitoring"]
    end
    
    PYTHON_ENV --> DEPS
    GPU_SETUP --> DEPS
    DEPS --> SSCD_PATH
    SSCD_PATH --> MODEL_LOCATION
    MODEL_LOCATION --> TORCH_SCRIPT
    
    TORCH_SCRIPT --> EMBEDDINGS_PATH
    DATA_PATHS --> EMBEDDINGS_PATH
    EMBEDDINGS_PATH --> OUTPUT_PATHS
    OUTPUT_PATHS --> TEMP_STORAGE
    
    TEMP_STORAGE --> BATCH_SIZE
    BATCH_SIZE --> NUM_WORKERS
    NUM_WORKERS --> MEMORY_MANAGEMENT
    MEMORY_MANAGEMENT --> PROGRESS_TRACKING
```

*Sources: [requirements.txt:1-19](), [.gitignore:1-15]()*

### Key Configuration Considerations

| Configuration Area | Requirements | Impact |
|-------------------|-------------|---------|
| **GPU Memory** | Adequate VRAM for batch processing | Affects batch size and processing speed |
| **Storage Space** | Space for embeddings, models, and outputs | Critical for large dataset processing |
| **Python Environment** | Compatible versions of PyTorch ecosystem | Ensures proper model loading and execution |
| **FAISS Setup** | GPU-enabled FAISS installation | Enables fast similarity search capabilities |
| **Data Organization** | Proper directory structure | Prevents path resolution issues |

The setup ensures that all components can interact effectively, from initial data ingestion through embedding generation to final analysis and visualization output.

*Sources: [requirements.txt:1-19](), [.gitignore:1-15]()*

---

