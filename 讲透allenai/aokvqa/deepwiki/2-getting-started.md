<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/aokvqa · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [environment.yml](environment.yml)

</details>



This document provides step-by-step instructions for setting up the A-OKVQA benchmark environment and preparing the initial data required for running experiments. It covers repository setup, environment configuration, and basic data acquisition to get you ready for feature extraction and model training.

For detailed information about specific data preparation steps like vocabulary building, see [Data Preparation](#2.2). For comprehensive environment configuration details, see [Environment Setup](#2.1).

## Repository Setup and Initial Configuration

The A-OKVQA repository requires specific setup steps to properly initialize submodules and configure the Python environment.

### Repository Cloning and Structure

Clone the repository with all required submodules and configure the Python path:

```bash
git clone --single-branch --recurse-submodules https://github.com/allenai/aokvqa.git
cd aokvqa
export PYTHONPATH=.
```

**Setup Workflow Diagram**

```mermaid
graph TD
    START["User starts setup"]
    CLONE["git clone --recurse-submodules"]
    PYTHONPATH["export PYTHONPATH=."]
    CONDA_CREATE["conda env create --name aokvqa"]
    CONDA_ACTIVATE["conda activate aokvqa"]
    DIRS["mkdir -p directories"]
    DOWNLOAD["Download datasets"]
    VERIFY["Verify installation"]
    
    START --> CLONE
    CLONE --> PYTHONPATH
    PYTHONPATH --> CONDA_CREATE
    CONDA_CREATE --> CONDA_ACTIVATE
    CONDA_ACTIVATE --> DIRS
    DIRS --> DOWNLOAD
    DOWNLOAD --> VERIFY
    
    subgraph "Required Directories"
        AOKVQA_DIR["$AOKVQA_DIR/datasets/aokvqa/"]
        COCO_DIR["$COCO_DIR/datasets/coco/"]
        FEATURES_DIR["$FEATURES_DIR/features/"]
        LOG_DIR["$LOG_DIR/logs/"]
        PREDS_DIR["$PREDS_DIR/predictions/"]
    end
    
    DIRS --> AOKVQA_DIR
    DIRS --> COCO_DIR  
    DIRS --> FEATURES_DIR
    DIRS --> LOG_DIR
    DIRS --> PREDS_DIR
```

Sources: [README.md:28-36]()

## Environment Configuration Overview

The A-OKVQA environment requires specific Python packages and CUDA support for optimal performance. The conda environment includes PyTorch, CLIP, transformers, and other deep learning dependencies.

**Environment Dependencies Structure**

```mermaid
graph TB
    subgraph "Core Dependencies"
        PYTHON["python=3.7"]
        PYTORCH["pytorch=1.11.0"]
        TORCHVISION["torchvision=0.12.0"]
        CUDA["cudatoolkit=11.3"]
    end
    
    subgraph "ML Libraries"
        LIGHTNING["pytorch-lightning=1.6.3"]
        METRICS["torchmetrics=0.8.1"]
        CLIP_LIB["clip @ github.com/openai/CLIP"]
        TRANSFORMERS["transformers==4.10.3"]
    end
    
    subgraph "Utilities"
        GDOWN["gdown=4.4.0"]
        NLTK["nltk==3.7"]
        OPENAI["openai==0.18.1"]
        DATASETS["datasets==2.1.0"]
    end
    
    PYTHON --> PYTORCH
    PYTORCH --> CUDA
    PYTORCH --> LIGHTNING
    LIGHTNING --> METRICS
    CLIP_LIB --> PYTORCH
    TRANSFORMERS --> PYTORCH
```

### Environment Creation

Create and activate the conda environment using the provided configuration:

```bash
conda env create --name aokvqa
conda activate aokvqa
```

The `environment.yml` file specifies all required dependencies including CUDA toolkit version 11.3 and PyTorch 1.11.0 for optimal compatibility.

Sources: [README.md:34-36](), [environment.yml:1-37]()

## Data Acquisition Overview

The A-OKVQA benchmark requires the A-OKVQA dataset and optionally the COCO 2017 images for full functionality.

**Data Download and Organization Workflow**

```mermaid
graph LR
    subgraph "Environment Variables"
        AOKVQA_ENV["export AOKVQA_DIR=./datasets/aokvqa/"]
        COCO_ENV["export COCO_DIR=./datasets/coco/"]
    end
    
    subgraph "A-OKVQA Dataset"
        AOKVQA_URL["prior-datasets.s3.us-east-2.amazonaws.com"]
        AOKVQA_TAR["aokvqa_v1p0.tar.gz"]
        AOKVQA_FILES["train.json, val.json, test.json<br/>large_vocab_train.csv"]
    end
    
    subgraph "COCO 2017 Images"
        COCO_URL["images.cocodataset.org"]
        COCO_SPLITS["train2017.zip<br/>val2017.zip<br/>test2017.zip"]
        COCO_ANNOTATIONS["annotations_trainval2017.zip"]
    end
    
    AOKVQA_ENV --> AOKVQA_URL
    AOKVQA_URL --> AOKVQA_TAR
    AOKVQA_TAR --> AOKVQA_FILES
    
    COCO_ENV --> COCO_URL
    COCO_URL --> COCO_SPLITS
    COCO_URL --> COCO_ANNOTATIONS
```

### A-OKVQA Dataset Download

Download the core A-OKVQA dataset containing questions, answers, and vocabulary:

```bash
export AOKVQA_DIR=./datasets/aokvqa/
mkdir -p ${AOKVQA_DIR}
curl -fsSL https://prior-datasets.s3.us-east-2.amazonaws.com/aokvqa/aokvqa_v1p0.tar.gz | tar xvz -C ${AOKVQA_DIR}
```

### COCO Images Download (Optional)

For experiments requiring image features, download the COCO 2017 dataset:

```bash
export COCO_DIR=./datasets/coco/
mkdir -p ${COCO_DIR}

for split in train val test; do
    wget "http://images.cocodataset.org/zips/${split}2017.zip"
    unzip "${split}2017.zip" -d ${COCO_DIR}; rm "${split}2017.zip"
done
```

Sources: [README.md:40-62]()

## Data Loading Verification

Verify the setup by loading and examining the dataset using the provided utilities.

**Data Loading Flow**

```mermaid
graph TD
    ENV_VARS["Environment Variables<br/>AOKVQA_DIR, COCO_DIR"]
    LOAD_SCRIPT["load_aokvqa.py"]
    LOAD_FUNC["load_aokvqa()"]
    COCO_FUNC["get_coco_path()"]
    DATASET["Dataset Object"]
    SAMPLE["Sample Entry"]
    
    ENV_VARS --> LOAD_SCRIPT
    LOAD_SCRIPT --> LOAD_FUNC
    LOAD_SCRIPT --> COCO_FUNC
    LOAD_FUNC --> DATASET
    DATASET --> SAMPLE
    COCO_FUNC --> SAMPLE
    
    subgraph "Sample Structure"
        QID["question_id"]
        IMG_ID["image_id"]
        QUESTION["question"]
        CHOICES["choices[]"]
        CORRECT["correct_choice_idx"]
        RATIONALES["rationales[]"]
    end
    
    SAMPLE --> QID
    SAMPLE --> IMG_ID
    SAMPLE --> QUESTION
    SAMPLE --> CHOICES
    SAMPLE --> CORRECT
    SAMPLE --> RATIONALES
```

### Basic Data Loading Test

Test the installation by loading a sample from the dataset:

```python
import os
aokvqa_dir = os.getenv('AOKVQA_DIR')

from load_aokvqa import load_aokvqa, get_coco_path
train_dataset = load_aokvqa(aokvqa_dir, 'train')

# Examine first entry
sample = train_dataset[0]
print(f"Question ID: {sample['question_id']}")
print(f"Question: {sample['question']}")
print(f"Choices: {sample['choices']}")
```

This verification step ensures that the dataset is properly downloaded and accessible through the provided loading utilities.

Sources: [README.md:64-98](), [load_aokvqa.py]()

## Directory Structure Preparation

Set up the required directory structure for storing features, logs, predictions, and pretrained models:

```bash
export FEATURES_DIR=./features/
export LOG_DIR=./logs/
export PREDS_DIR=./predictions/
export PT_MODEL_DIR=./pretrained_models/

mkdir -p ${FEATURES_DIR} ${LOG_DIR} ${PREDS_DIR} ${PT_MODEL_DIR}
```

These directories will be used throughout the experimentation pipeline for storing intermediate results and model artifacts.

Sources: [README.md:131-175]()

## Next Steps

After completing the getting started setup, you can proceed with:

1. **Environment Setup Details** - See [Environment Setup](#2.1) for comprehensive dependency management and troubleshooting
2. **Data Preparation** - See [Data Preparation](#2.2) for vocabulary building and preprocessing steps  
3. **Feature Extraction** - See [Feature Extraction Pipeline](#3) to generate multi-modal features using CLIP, ResNet, or BERT
4. **Model Training** - See [Model Training and Inference](#4) to begin running experiments with transfer learning or other approaches

The basic setup provides the foundation for all subsequent A-OKVQA benchmark experiments and evaluations.

Sources: [README.md:125-208]()

---

