<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CoCosNet · page 4 Data Formats and Organization · fetched 2026-10-26 -->

# Data Formats and Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [imgs/DeepFashion/img/WOMEN/Blouses_Shirts/id_00007636/01_1_front.jpg](imgs/DeepFashion/img/WOMEN/Blouses_Shirts/id_00007636/01_1_front.jpg)
- [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_candidate.txt](imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_candidate.txt)
- [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_subset.txt](imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_subset.txt)
- [imgs/DeepFashion/pose/WOMEN/Cardigans/id_00006266/02_2_side_candidate.txt](imgs/DeepFashion/pose/WOMEN/Cardigans/id_00006266/02_2_side_candidate.txt)
- [imgs/DeepFashion/pose/WOMEN/Cardigans/id_00006266/02_2_side_subset.txt](imgs/DeepFashion/pose/WOMEN/Cardigans/id_00006266/02_2_side_subset.txt)

</details>



This document describes the file structures, naming conventions, and data formats used across different datasets in the CoCosNet framework. It covers the organization of image files, reference files, pose data formats, and dataset-specific directory hierarchies that support the cross-domain correspondence learning system.

For information about how these data formats are processed by the dataset implementations, see [Dataset Implementations](#3.2). For details on the dataset loading architecture that consumes these formats, see [Dataset Architecture](#3.1).

## File System Organization

The CoCosNet codebase organizes data assets using a hierarchical structure that separates different types of content while maintaining consistent naming patterns across datasets.

```mermaid
graph TD
    ROOT["CoCosNet Root Directory"]
    
    subgraph "Core Directories"
        DATA_DIR["data/"]
        IMGS_DIR["imgs/"]
        MODELS_DIR["models/"]
    end
    
    subgraph "Dataset Implementations"
        REF_FILES["Reference Files"]
        ADE_DS["ade20k_dataset.py"]
        CELEB_DS["celebahq_dataset.py"]
        FASHION_DS["deepfashion_dataset.py"]
        FLICKR_DS["flickr_dataset.py"]
    end
    
    subgraph "Image Asset Hierarchies"
        DF_IMG["DeepFashion/img/"]
        DF_POSE["DeepFashion/pose/"]
        CELEB_IMG["CelebA-HQ-img/"]
        CELEB_MASK["CelebAMask-HQ-mask-anno/"]
        ADE_TRAIN["ADE20k/training/"]
        ADE_VAL["ADE20k/validation/"]
    end
    
    subgraph "Reference and Configuration"
        REF_TRAIN["*_ref.txt"]
        REF_TEST["*_ref_test.txt"]
        TRAIN_SPLIT["train.txt"]
        VAL_SPLIT["val.txt"]
    end
    
    ROOT --> DATA_DIR
    ROOT --> IMGS_DIR
    ROOT --> MODELS_DIR
    
    DATA_DIR --> REF_FILES
    DATA_DIR --> ADE_DS
    DATA_DIR --> CELEB_DS
    DATA_DIR --> FASHION_DS
    DATA_DIR --> FLICKR_DS
    
    IMGS_DIR --> DF_IMG
    IMGS_DIR --> DF_POSE
    IMGS_DIR --> CELEB_IMG
    IMGS_DIR --> CELEB_MASK
    IMGS_DIR --> ADE_TRAIN
    IMGS_DIR --> ADE_VAL
    
    REF_FILES --> REF_TRAIN
    REF_FILES --> REF_TEST
    REF_FILES --> TRAIN_SPLIT
    REF_FILES --> VAL_SPLIT
```

**Sources:** [imgs/DeepFashion/img/WOMEN/Blouses_Shirts/id_00007636/01_1_front.jpg](), [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_candidate.txt]()

## Dataset-Specific Directory Structures

Each dataset follows a specific organizational pattern that reflects its domain and data characteristics.

### DeepFashion Dataset Structure

The DeepFashion dataset uses a hierarchical structure that separates images and pose data while maintaining parallel directory trees.

```mermaid
graph LR
    subgraph "DeepFashion Image Hierarchy"
        DF_ROOT["DeepFashion/"]
        IMG_DIR["img/"]
        GENDER["WOMEN/"]
        CATEGORY["Blouses_Shirts/"]
        ITEM_ID["id_00007636/"]
        IMG_FILE["01_1_front.jpg"]
        
        DF_ROOT --> IMG_DIR
        IMG_DIR --> GENDER
        GENDER --> CATEGORY
        CATEGORY --> ITEM_ID
        ITEM_ID --> IMG_FILE
    end
    
    subgraph "DeepFashion Pose Hierarchy"
        DF_ROOT2["DeepFashion/"]
        POSE_DIR["pose/"]
        GENDER2["WOMEN/"]
        CATEGORY2["Blouses_Shirts/"]
        ITEM_ID2["id_00007636/"]
        CANDIDATE["01_1_front_candidate.txt"]
        SUBSET["01_1_front_subset.txt"]
        
        DF_ROOT2 --> POSE_DIR
        POSE_DIR --> GENDER2
        GENDER2 --> CATEGORY2
        CATEGORY2 --> ITEM_ID2
        ITEM_ID2 --> CANDIDATE
        ITEM_ID2 --> SUBSET
    end
```

**Sources:** [imgs/DeepFashion/img/WOMEN/Blouses_Shirts/id_00007636/01_1_front.jpg](), [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_candidate.txt](), [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_subset.txt]()

| Directory Level | Purpose | Example Values |
|-----------------|---------|----------------|
| `DeepFashion/` | Dataset root | Fixed |
| `img/` or `pose/` | Content type | `img`, `pose` |
| Gender | Target demographic | `WOMEN`, `MEN` |
| Category | Clothing type | `Blouses_Shirts`, `Cardigans` |
| Item ID | Unique item identifier | `id_00007636`, `id_00006266` |
| Filename | Specific view/angle | `01_1_front.jpg`, `02_2_side_candidate.txt` |

### CelebAHQ Dataset Structure

The CelebAHQ dataset maintains separate directories for images and mask annotations with synchronized naming.

| Component | Directory Path | File Pattern |
|-----------|----------------|--------------|
| Face Images | `CelebA-HQ-img/` | `{id}.jpg` |
| Mask Annotations | `CelebAMask-HQ-mask-anno/` | `{id}.png` |
| Glasses Masks | `CelebAMask-HQ-mask-anno/` | `{id}_eye_g.png` |

### ADE20K Dataset Structure

The ADE20K dataset uses a simpler structure with training and validation splits.

| Component | Directory Path | File Pattern |
|-----------|----------------|--------------|
| Training Images | `ADE20k/training/` | `*.jpg` |
| Validation Images | `ADE20k/validation/` | `*.jpg` |
| Training Masks | `ADE20k/training/` | `*_seg.png` |
| Validation Masks | `ADE20k/validation/` | `*_seg.png` |

## Pose Data Format

The DeepFashion dataset includes human pose keypoint data stored in two complementary file types: candidate files and subset files.

### Candidate Files Format

Candidate files (`*_candidate.txt`) contain detected keypoint coordinates with confidence scores.

```mermaid
graph TD
    subgraph "candidate.txt Structure"
        CANDIDATE_FILE["candidate.txt"]
        
        subgraph "Line Format"
            X_COORD["X Coordinate"]
            Y_COORD["Y Coordinate"] 
            CONFIDENCE["Confidence Score"]
            KEYPOINT_ID["Keypoint ID"]
        end
        
        subgraph "Example Values"
            LINE1["129.0 40.0 0.978 0.0"]
            LINE2["131.0 85.0 0.912 1.0"]
            LINE3["98.0 84.0 0.867 2.0"]
        end
        
        CANDIDATE_FILE --> X_COORD
        CANDIDATE_FILE --> Y_COORD
        CANDIDATE_FILE --> CONFIDENCE
        CANDIDATE_FILE --> KEYPOINT_ID
        
        X_COORD --> LINE1
        Y_COORD --> LINE1
        CONFIDENCE --> LINE1
        KEYPOINT_ID --> LINE1
    end
```

**Sources:** [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_candidate.txt:1-14]()

Each line in a candidate file follows the format:
```
<x_coordinate> <y_coordinate> <confidence_score> <keypoint_index>
```

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| X Coordinate | `float` | Pixel x-position | `129.0` |
| Y Coordinate | `float` | Pixel y-position | `40.0` |
| Confidence Score | `float` | Detection confidence (0-1) | `0.978` |
| Keypoint Index | `float` | Keypoint identifier | `0.0` (head), `1.0` (neck), etc. |

### Subset Files Format

Subset files (`*_subset.txt`) define which keypoints from the candidate file are valid and should be used for pose rendering.

```mermaid
graph TD
    subgraph "subset.txt Structure"
        SUBSET_FILE["subset.txt"]
        
        subgraph "Content Format"
            VALID_IDS["Valid Keypoint IDs"]
            MISSING_IDS["Missing Keypoints (-1)"]
            TOTAL_COUNT["Total Keypoint Count"]
        end
        
        subgraph "Example Line"
            EXAMPLE["0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 -1.0 -1.0 9.0 -1.0 -1.0 10.0 11.0 12.0 13.0 24.57 14.0"]
        end
        
        SUBSET_FILE --> VALID_IDS
        SUBSET_FILE --> MISSING_IDS
        SUBSET_FILE --> TOTAL_COUNT
        
        VALID_IDS --> EXAMPLE
        MISSING_IDS --> EXAMPLE
        TOTAL_COUNT --> EXAMPLE
    end
```

**Sources:** [imgs/DeepFashion/pose/WOMEN/Blouses_Shirts/id_00007636/01_1_front_subset.txt:1-1](), [imgs/DeepFashion/pose/WOMEN/Cardigans/id_00006266/02_2_side_subset.txt:1-1]()

The subset file contains a single line with space-separated values:
- **Valid keypoint IDs**: References to keypoints in the candidate file
- **Missing keypoints**: Marked with `-1.0` when not detected
- **Calculated values**: Derived metrics for pose analysis

| Position | Keypoint | Example Value | Meaning |
|----------|----------|---------------|---------|
| 0 | Head | `0.0` | References candidate line 0 |
| 1 | Neck | `1.0` | References candidate line 1 |
| 9-10 | Ankles | `-1.0` | Not detected/visible |
| 18 | Score | `24.57` | Calculated pose quality |

## Reference File Formats

Reference files establish relationships between input labels and target images for training and testing phases.

### Training Reference Files

Files ending with `_ref.txt` define label-image pairs for training data.

### Test Reference Files  

Files ending with `_ref_test.txt` define label-image pairs for evaluation data.

### Data Split Files

| File | Purpose | Content |
|------|---------|---------|
| `train.txt` | Training set definition | List of training image identifiers |
| `val.txt` | Validation set definition | List of validation image identifiers |

**Sources:** Based on the dataset management system architecture and file organization patterns observed in the provided examples.

---

