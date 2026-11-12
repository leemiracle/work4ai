<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alignet · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [requirements.txt](requirements.txt)

</details>



This page provides an overview of the initial setup process for the AligNet project. It covers the prerequisites, setup workflow, directory structure, and verification steps needed to begin working with the AligNet training code and datasets. For detailed installation instructions, see [Installation](#2.1). For information about accessing the AligNet dataset, see [Accessing the AligNet Dataset](#2.2).

## Prerequisites

Before beginning the setup process, ensure you have:

| Requirement | Purpose | Notes |
|------------|---------|-------|
| Python 3.x | Runtime environment | Compatible with JAX ecosystem |
| pip | Package manager | For installing dependencies |
| ~150GB disk space | ImageNet2012 storage | For manual ILSVRC2012 tar files and generated array_records |
| ~5GB disk space | AligNet dataset | For triplet .npz files |
| ImageNet access | Dataset license | Registration required at https://image-net.org/download-images |
| Google Cloud access | Model downloads | For accessing `gs://alignet/` bucket |

Sources: [README.md:108-127]()

## Setup Workflow Overview

The following diagram illustrates the complete setup process, from repository cloning to running your first training job:

```mermaid
graph TB
    START["Start Setup"]
    
    subgraph "Step 1: Repository Setup"
        CLONE["git clone<br/>github.com/google-deepmind/alignet"]
        INSTALL["pip install -r<br/>alignet/requirements.txt"]
    end
    
    subgraph "Step 2: ImageNet2012 Setup"
        REGISTER["Register at<br/>image-net.org"]
        DOWNLOAD_MANUAL["Download to:<br/>~/tensorflow_datasets/<br/>downloads/manual/<br/>- ILSVRC2012_img_train.tar<br/>- ILSVRC2012_img_val.tar"]
        GENERATE_TFDS["import tensorflow_datasets as tfds<br/>ds = tfds.data_source<br/>('imagenet2012', split='train')"]
        ARRAY_RECORDS["Generated:<br/>~/tensorflow_datasets/<br/>imagenet2012/<br/>*array_record*"]
    end
    
    subgraph "Step 3: AligNet Dataset"
        DOWNLOAD_GCS["Download from GCS:<br/>gs://alignet/<br/>- alignet_train.npz<br/>- alignet_valid.npz"]
        STORE_LOCAL["Store in:<br/>/path/to/alignet/dataset/"]
    end
    
    subgraph "Step 4: Verification"
        RUN_TRAIN["python -m kauldron.main<br/>--cfg=alignet/configs/siglip.py<br/>--cfg.workdir=/tmp/kauldron/workdir<br/>--cfg.aux.data_dir=/path/to/alignet/dataset"]
        CHECK_OUTPUT["Verify:<br/>- Training starts<br/>- Metrics logged<br/>- Checkpoints saved"]
    end
    
    START --> CLONE
    CLONE --> INSTALL
    INSTALL --> REGISTER
    REGISTER --> DOWNLOAD_MANUAL
    DOWNLOAD_MANUAL --> GENERATE_TFDS
    GENERATE_TFDS --> ARRAY_RECORDS
    ARRAY_RECORDS --> DOWNLOAD_GCS
    DOWNLOAD_GCS --> STORE_LOCAL
    STORE_LOCAL --> RUN_TRAIN
    RUN_TRAIN --> CHECK_OUTPUT
    
    style ARRAY_RECORDS fill:#f9f9f9,stroke:#333,stroke-width:2px
    style STORE_LOCAL fill:#f9f9f9,stroke:#333,stroke-width:2px
    style CHECK_OUTPUT fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [README.md:32-152]()

## Workspace Directory Structure

After completing the setup process, your workspace will have the following structure:

```mermaid
graph TB
    ROOT["Workspace Root"]
    
    subgraph "AligNet Repository"
        REPO["alignet/"]
        CONFIGS["alignet/configs/"]
        CONFIG_SIGLIP["alignet/configs/siglip.py"]
        DATA_PY["alignet/data.py"]
        LOSSES["alignet/losses.py"]
        MODELS["alignet/bv_vit.py<br/>alignet/bv_wrapper.py<br/>alignet/bv_utils.py"]
        PREPROC["alignet/preprocessing.py"]
        METRICS["alignet/metrics.py"]
        REQS["alignet/requirements.txt"]
    end
    
    subgraph "TensorFlow Datasets"
        TFDS_ROOT["~/tensorflow_datasets/"]
        MANUAL["~/tensorflow_datasets/downloads/manual/"]
        TAR_TRAIN["ILSVRC2012_img_train.tar"]
        TAR_VAL["ILSVRC2012_img_val.tar"]
        I1K_DATA["~/tensorflow_datasets/imagenet2012/"]
        ARRAY_REC["array_record files<br/>(~150GB total)"]
    end
    
    subgraph "AligNet Dataset"
        ALIGNET_DIR["/path/to/alignet/dataset/"]
        NPZ_TRAIN["alignet_train.npz<br/>(10M triplets)"]
        NPZ_VALID["alignet_valid.npz<br/>(10k triplets)"]
    end
    
    subgraph "Training Output"
        WORKDIR["/tmp/kauldron/workdir/"]
        CKPTS["checkpoints/"]
        LOGS["logs/"]
        SUMMARIES["summaries/"]
    end
    
    ROOT --> REPO
    REPO --> CONFIGS
    CONFIGS --> CONFIG_SIGLIP
    REPO --> DATA_PY
    REPO --> LOSSES
    REPO --> MODELS
    REPO --> PREPROC
    REPO --> METRICS
    REPO --> REQS
    
    TFDS_ROOT --> MANUAL
    MANUAL --> TAR_TRAIN
    MANUAL --> TAR_VAL
    TFDS_ROOT --> I1K_DATA
    I1K_DATA --> ARRAY_REC
    
    ALIGNET_DIR --> NPZ_TRAIN
    ALIGNET_DIR --> NPZ_VALID
    
    WORKDIR --> CKPTS
    WORKDIR --> LOGS
    WORKDIR --> SUMMARIES
```

Sources: [README.md:32-152]()

## Key Dependencies

The AligNet project requires two primary dependencies, specified in [requirements.txt:1-2]():

| Package | Purpose | Key Components Used |
|---------|---------|---------------------|
| `kauldron` | Training framework | `kd.train.Trainer`, `kd.data`, configuration system |
| `opencv-python` | Image preprocessing | Used in `ResizeImage` for interpolation |

Additional implicit dependencies include:
- `tensorflow` - For `tfds.data_source` and SavedModel inference
- `tensorflow-datasets` - For ImageNet2012 access
- `jax` / `flax` - For neural network implementation (via Big Vision)
- `numpy` - For loading `.npz` files

Sources: [requirements.txt:1-2]()

## Data Dependencies and Flow

The following diagram shows how the different data components interact during setup and training:

```mermaid
graph LR
    subgraph "Manual Downloads"
        IMAGENET_WEB["image-net.org<br/>Manual registration required"]
        TAR_FILES["ILSVRC2012_img_train.tar<br/>ILSVRC2012_img_val.tar<br/>(~150GB)"]
        GCS_BUCKET["gs://alignet/<br/>Google Cloud Storage"]
    end
    
    subgraph "Local Storage"
        MANUAL_DIR["~/tensorflow_datasets/<br/>downloads/manual/"]
        TFDS_DIR["~/tensorflow_datasets/<br/>imagenet2012/<br/>array_record format"]
        ALIGNET_LOCAL["/path/to/alignet/dataset/<br/>alignet_train.npz<br/>alignet_valid.npz"]
    end
    
    subgraph "Data Loading"
        DATA_SOURCE["tfds.data_source<br/>('imagenet2012')"]
        ALIGNET_TRIPLETS["AligNetTriplets<br/>data.py:AligNetTriplets"]
        PREPROCESSING["ResizeImage + Stack<br/>preprocessing.py"]
    end
    
    subgraph "Training System"
        KAULDRON["kauldron.main<br/>Training orchestration"]
        CONFIG["configs/siglip.py<br/>cfg.train_ds.from_args<br/>cfg.aux.data_dir"]
    end
    
    IMAGENET_WEB --> TAR_FILES
    TAR_FILES --> MANUAL_DIR
    MANUAL_DIR --> DATA_SOURCE
    DATA_SOURCE --> TFDS_DIR
    
    GCS_BUCKET --> ALIGNET_LOCAL
    
    TFDS_DIR --> DATA_SOURCE
    ALIGNET_LOCAL --> ALIGNET_TRIPLETS
    DATA_SOURCE --> ALIGNET_TRIPLETS
    ALIGNET_TRIPLETS --> PREPROCESSING
    PREPROCESSING --> KAULDRON
    CONFIG --> KAULDRON
    CONFIG --> ALIGNET_TRIPLETS
```

**Key Points:**

- **ImageNet2012 Format Requirement**: The dataset must be in `array_record` format (not TFRecords) to support random access. This is achieved by using `tfds.data_source()` instead of `tfds.load()` as noted in [README.md:129-131]().

- **AligNet Triplet Files**: The `.npz` files contain metadata (indices, similarities, filenames) but not the actual images. Images are fetched from the ImageNet2012 dataset using the indices stored in the `.npz` files.

- **Configuration Path**: The `cfg.aux.data_dir` parameter in the training command specifies where to find the AligNet `.npz` files.

Sources: [README.md:45-132]()

## Verification Steps

After completing the setup, verify your installation with these steps:

### 1. Verify Package Installation

```python
import kauldron
import cv2
import tensorflow_datasets as tfds
print("Dependencies installed successfully")
```

### 2. Verify ImageNet2012 Access

```python
import tensorflow_datasets as tfds

# This should not raise an error if setup is correct
ds = tfds.data_source("imagenet2012", split="train")
print(f"ImageNet2012 dataset accessible with {len(ds)} samples")
```

If this fails, ensure:
- The manual tar files are in `~/tensorflow_datasets/downloads/manual/`
- The `array_record` files have been generated in `~/tensorflow_datasets/imagenet2012/`

### 3. Verify AligNet Dataset Access

```python
import numpy as np

# Load the training set
data = np.load("/path/to/alignet/dataset/alignet_train.npz")
print(f"Training triplets: {data['indices'].shape[0]}")
print(f"Arrays available: {list(data.keys())}")

# Expected output:
# Training triplets: 10000000
# Arrays available: ['indices', 'similarities', 'filenames']
```

### 4. Test Data Pipeline

```python
from alignet import data
import tensorflow_datasets as tfds

# Initialize the data source
ds = data.AligNetTriplets.from_args(
    root_dir="/path/to/alignet/dataset",
    transform="alignet",
    split="train",
    sampling="between_class"
)

# Fetch one batch
batch = next(iter(ds.get_iter(batch_size=2)))
print(f"Batch keys: {batch.keys()}")
print(f"Image triplet shape: {batch['image_triplet'].shape}")

# Expected output:
# Batch keys: dict_keys(['image_triplet', 'image_similarities', 'label_triplet', ...])
# Image triplet shape: (2, 3, 224, 224, 3)
```

Sources: [README.md:122-127](), [data.py]() (referenced via system architecture)

## Quick Start Training

Once verification is complete, you can launch a training run:

```bash
python -m kauldron.main \
  --cfg=alignet/configs/siglip.py \
  --cfg.workdir=/tmp/kauldron/workdir \
  --cfg.aux.data_dir=/path/to/alignet/dataset
```

**Configuration Parameters:**

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `--cfg` | Path to training configuration | `alignet/configs/siglip.py` |
| `--cfg.workdir` | Directory for checkpoints and logs | `/tmp/kauldron/workdir` |
| `--cfg.aux.data_dir` | Path to AligNet `.npz` files | `/path/to/alignet/dataset` |

The training process will:
1. Load the SigLIP-B/16 base model from checkpoint
2. Initialize the AligNet dataset with 10M training triplets
3. Train for 100,000 steps with the JSDTripletLoss
4. Save checkpoints every 10,000 steps
5. Run evaluation every 5,000 steps on three sampling strategies

For detailed information about the training configuration and process, see [Training System](#6).

Sources: [README.md:138-152]()

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `tfds.data_source` not found | TensorFlow Datasets version too old | Upgrade: `pip install --upgrade tensorflow-datasets` |
| "Manual download required" error | ImageNet tar files not in manual directory | Place `ILSVRC2012_img_*.tar` files in `~/tensorflow_datasets/downloads/manual/` |
| "Dataset not found in array_record format" | Dataset generated in TFRecords format | Delete dataset and regenerate using `tfds.data_source()` instead of `tfds.load()` |
| Out of memory during training | Batch size too large for GPU | Reduce batch size in config or use gradient accumulation |
| `.npz` file not found | Incorrect `data_dir` path | Verify `--cfg.aux.data_dir` points to directory containing `alignet_train.npz` |

Sources: [README.md:108-132]()

## Next Steps

After completing the setup and verification:

1. **Understanding the Data**: Learn about triplet structure and sampling strategies in [AligNet Dataset](#3)
2. **Model Architecture**: Explore the Vision Transformer implementation in [Model Architecture](#4)
3. **Training Deep Dive**: Understand loss functions and training configuration in [Training System](#6)
4. **Using Pre-trained Models**: Access the released AligNet models in [Released Models and Inference](#7)
5. **Customization**: Modify configurations for different experiments (see [Training Configuration](#6.1))

Sources: [README.md:1-280]() (overall structure and navigation)

---

