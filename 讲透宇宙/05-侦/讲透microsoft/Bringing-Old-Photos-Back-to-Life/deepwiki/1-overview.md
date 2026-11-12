<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Bringing-Old-Photos-Back-to-Life · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cog.yaml](cog.yaml)
- [download-weights](download-weights)
- [imgs/HOF_2_007_007_my_concat.gif](imgs/HOF_2_007_007_my_concat.gif)
- [imgs/gui.PNG](imgs/gui.PNG)
- [predict.py](predict.py)
- [run.py](run.py)

</details>



The "Bringing Old Photos Back to Life" system is a specialized image restoration framework designed to restore aged and damaged photographs using deep learning techniques. This repository implements the methodology described in the CVPR 2020 paper "Bringing Old Photos Back to Life" and the TPAMI 2022 paper "Old Photo Restoration via Deep Latent Space Translation". For information about setting up and installing the system, see [Installation and Setup](#1.1).

## System Purpose and Capabilities

This system addresses multiple degradation issues found in old photographs:

- Overall quality degradation (fading, discoloration)
- Structural defects (scratches, stains, tears)
- Face-specific deterioration (blurriness, lack of detail)

The restoration process happens through a four-stage pipeline that handles each aspect separately and then combines the results seamlessly.

## Architecture Overview

The restoration process follows a sequential pipeline architecture with specialized modules for each restoration aspect.

```mermaid
flowchart TD
    subgraph "User Interface"
        UI["User Input (CLI/GUI)"]
        RunPy["run.py: Main Entry Point"]
    end
    
    subgraph "Restoration Pipeline"
        GR["Global Restoration"]
        FD["Face Detection"]
        FE["Face Enhancement"]
        FB["Warping & Blending"]
    end
    
    UI --> RunPy
    RunPy --> GR
    GR --> FD
    FD --> FE
    FE --> FB
    FB --> FinalOutput["Final Restored Image"]
    
    subgraph "Global Restoration Components"
        SD["Scratch Detection (detection.py)"]
        QR["Quality Restoration (test.py)"]
    end
    
    GR --> SD
    GR --> QR
    
    subgraph "Face Module Components"
        FLD["Face Landmark Detection"]
        FSR["Face Super-Resolution"]
    end
    
    FD --> FLD
    FE --> FSR
```

Sources: [run.py:45-105](), [README.md:83-106](), [README.md:166-168]()

## Data Flow

The system processes images through a sequence of transformations, with different paths depending on the image's condition.

```mermaid
flowchart TD
    Input["Input Old Photo"] --> ScratchCheck{"Has Scratches?"}
    
    ScratchCheck -->|"Yes"| ScratchDetection["Scratch Detection"]
    ScratchDetection --> ScratchMask["Generate Scratch Mask"]
    ScratchMask --> GlobalRestoreWithScratch["Quality & Scratch Restoration"]
    
    ScratchCheck -->|"No"| GlobalRestoreQuality["Quality Restoration"]
    
    GlobalRestoreWithScratch --> RestoredImage["Globally Restored Image"]
    GlobalRestoreQuality --> RestoredImage
    
    RestoredImage --> FaceDetection["Face Detection (dlib)"]
    FaceDetection --> FaceCheck{"Faces Found?"}
    
    FaceCheck -->|"No"| FinalOutput["Final Output Image"]
    
    FaceCheck -->|"Yes"| ExtractFaces["Extract & Align Faces"]
    ExtractFaces --> EnhanceFaces["Face Enhancement (SPADE)"]
    EnhanceFaces --> WarpBack["Warp Enhanced Faces"]
    WarpBack --> BlendFaces["Blend Faces"]
    BlendFaces --> FinalOutput
```

Sources: [run.py:45-202](), [predict.py:59-202]()

## Code Organization

The codebase is organized into several key directories, each handling a specific aspect of the restoration process:

| Directory | Purpose | Key Components |
|-----------|---------|----------------|
| `Global/` | Overall image restoration | Scratch detection, quality improvement |
| `Face_Detection/` | Face detection and alignment | dlib-based face detection, alignment utilities |
| `Face_Enhancement/` | Face-specific restoration | SPADE-based face enhancement models |
| Root | Main entry points | `run.py`, `predict.py` |

Sources: [README.md:38-75](), [run.py:47-173]()

## Key Components

### Main Entry Points

The system provides several ways to use the restoration functionality:

1. **Command-line interface** (`run.py`): Primary way to process images through the full pipeline
2. **Prediction API** (`predict.py`): Provides programmatic access to the restoration pipeline
3. **GUI Interface**: Visual interface for easier usage

### Global Restoration Module

This module handles the overall image quality improvement and scratch removal:

```mermaid
flowchart LR
    subgraph "Global Restoration"
        detection["detection.py: Scratch Detection"]
        test["test.py: Quality/Scratch Restoration"]
    end
    
    subgraph "Detection Models"
        UNet["U-Net: Scratch Detection"]
    end
    
    subgraph "Restoration Models"
        VAE_A["VAE Domain A"]
        VAE_B["VAE Domain B"]
        Mapping["Mapping Network"]
        NL["Non-Local Operations"]
    end
    
    InputImage["Input Image"] --> detection
    detection --> ScratchMask["Scratch Mask"]
    ScratchMask --> test
    InputImage --> test
    test --> RestoredImage["Restored Image"]
    
    detection --> UNet
    test --> VAE_A
    test --> VAE_B
    test --> Mapping
    test --> NL
```

Sources: [run.py:46-96](), [README.md:127-153]()

### Face Enhancement Module

This module handles face-specific restoration, using specialized models to enhance facial details:

```mermaid
flowchart LR
    subgraph "Face Pipeline"
        detection["detect_all_dlib.py: 
        Face Detection"]
        enhancement["test_face.py: 
        Face Enhancement"]
        warping["align_warp_back_multiple_dlib.py: 
        Face Blending"]
    end
    
    subgraph "Models"
        SPADE["SPADE Generator"]
        dlib["dlib Face Detector"]
    end
    
    GloballyRestored["Globally Restored Image"] --> detection
    detection --> FaceRegions["Detected Faces"]
    FaceRegions --> enhancement
    enhancement --> EnhancedFaces["Enhanced Faces"]
    EnhancedFaces --> warping
    GloballyRestored --> warping
    warping --> FinalImage["Final Restored Image"]
    
    detection --> dlib
    enhancement --> SPADE
```

Sources: [run.py:109-199](), [README.md:157-165]()

## High-Level Execution Flow

When running the restoration pipeline through `run.py`, the system executes the following steps:

1. **Input Processing**: Parse command-line arguments and prepare input/output directories
2. **Global Restoration**:
   - If image has scratches (with_scratch=True): Run scratch detection followed by combined quality and scratch restoration
   - Otherwise: Run quality restoration only
3. **Face Detection**: Detect and extract faces from the globally restored image
4. **Face Enhancement**: Apply specialized face enhancement to each detected face
5. **Face Blending**: Warp and blend the enhanced faces back into the globally restored image

The system also supports high-resolution processing through an HR mode (activated with the `--HR` flag).

Sources: [run.py:17-202](), [README.md:108-116]()

## Model Architecture

The system employs several deep learning models, primarily based on GANs and VAEs:

1. **Scratch Detection**: U-Net based architecture for identifying scratches
2. **Global Restoration**: Domain translation framework using VAEs and mapping networks 
3. **Face Enhancement**: SPADE-based generator for improving facial details

```mermaid
flowchart TD
    subgraph "Domain Translation Framework"
        VaeA["VAE Domain A"]
        VaeB["VAE Domain B"]
        Mapping["Mapping Network"]
        NL["Non-Local Operations"]
    end
    
    subgraph "Face Enhancement Framework"
        SPADE["SPADE Generator"]
        FaceGAN["Pix2PixHD Generator"]
    end
    
    InputLabelMap["Input Label Map"] --> VaeA
    VaeA --> LatentA["Latent Space A"]
    LatentA --> Mapping
    Mapping --> LatentB["Latent Space B"]
    LatentB --> VaeB
    VaeB --> OutputImage["Output Image"]
    
    MaskInfo["Mask Info"] --> NL
    NL --> Mapping
    
    InputFace["Degraded Face"] --> SPADE
    FaceParsing["Face Parsing Map"] --> SPADE
    SPADE --> EnhancedFace["Enhanced Face"]
```

Sources: [README.md:127-153](), [README.md:157-165]()

## Using the System

Basic usage involves running the system through the command-line interface:

For images without scratches:
```
python run.py --input_folder [test_image_folder_path] --output_folder [output_path] --GPU 0
```

For scratched images:
```
python run.py --input_folder [test_image_folder_path] --output_folder [output_path] --GPU 0 --with_scratch
```

For high-resolution images:
```
python run.py --input_folder [test_image_folder_path] --output_folder [output_path] --GPU 0 --with_scratch --HR
```

For more details on usage options and advanced configuration, see [Usage Guide](#6).

Sources: [README.md:83-116](), [run.py:17-34]()

---

