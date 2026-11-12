<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Multi_Species_Bioacoustic_Classification · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [extract_melspectrograms.py](extract_melspectrograms.py)
- [requirements.txt](requirements.txt)

</details>



This document provides a comprehensive overview of the Multi-Species Bioacoustic Classification system architecture, including core components, data flow patterns, and the relationship between the three deep learning models. For detailed information about individual models, see [Deep Learning Models](#4). For environment setup details, see [Environment Setup and Dependencies](#5).

## Overview

The system implements a multi-stage pipeline that transforms raw audio recordings into species classifications through mel-spectrogram extraction and deep learning models. The architecture consists of three primary subsystems: data processing, model training, and evaluation frameworks.

## Core System Components

### Data Processing Pipeline Architecture

The central component of the system is the mel-spectrogram extraction pipeline implemented in `extract_melspectrograms.py`. This module orchestrates the transformation from raw audio data to visual representations suitable for CNN processing.

```mermaid
flowchart TD
    A["Raw Audio Files\n(48kHz sampling rate)"] --> B["Audio Loading\nlibrosa.load()"]
    B --> C["Metadata Matching\ntrue_positive_metadata.csv\nfalse_positive_metadata.csv"]
    C --> D["Mel-Spectrogram Generation\nlibrosa.feature.melspectrogram()"]
    D --> E["Image Export\nmatplotlib.pyplot.savefig()"]
    E --> F["True Positive Spectrograms\n/tp/*.png"]
    E --> G["False Positive Spectrograms\n/fp/*.png"]
    
    H["Parallel Processing\njoblib.Parallel"] --> B
    I["Directory Structure\noutput_mel_spectrogram_dir"] --> F
    I --> G
```

**Data Processing Pipeline Components**

The pipeline processes two distinct data types through parallel execution paths:

Sources: [extract_melspectrograms.py:50-56](), [extract_melspectrograms.py:147-161]()

### Model Training Architecture

The system implements three distinct model training approaches that operate on the same mel-spectrogram inputs but use different architectures and training strategies.

```mermaid
flowchart LR
    A["Mel-Spectrogram Input\n224x224 images"] --> B["model1_vgg16_architecture_TP_only.py"]
    A --> C["model2_transfer_learning_TP_only.py"]
    A --> D["model3_transfer_learning_pseudo_labeling.py"]
    
    B --> E["VGG16 from Scratch\nTrue Positives Only"]
    C --> F["ResNet50 Transfer Learning\nTrue Positives Only"]
    D --> G["ResNet50 + Pseudo-labeling\nTrue Positives + False Positives"]
    
    E --> H["Model Evaluation\nSpecies-level metrics"]
    F --> H
    G --> H
```

**Model Training Components**

Each model represents increasing sophistication in training methodology:

1. **Model 1**: Baseline CNN implementation using VGG16 architecture
2. **Model 2**: Transfer learning approach with pre-trained ResNet50
3. **Model 3**: Advanced semi-supervised learning with custom loss functions

Sources: [README.md:17-22]()

### Technology Stack Architecture

The system dependencies form a layered architecture supporting audio processing, machine learning, and parallel computation.

```mermaid
graph TB
    subgraph "Application Layer"
        A["extract_melspectrograms.py"]
        B["model1_vgg16_architecture_TP_only.py"]
        C["model2_transfer_learning_TP_only.py"]
        D["model3_transfer_learning_pseudo_labeling.py"]
    end
    
    subgraph "ML Framework Layer"
        E["tensorflow"]
        F["keras"]
        G["scikit-learn"]
    end
    
    subgraph "Audio Processing Layer"
        H["librosa"]
        I["numpy"]
        J["scipy"]
    end
    
    subgraph "Image Processing Layer"
        K["matplotlib"]
        L["opencv-python"]
    end
    
    subgraph "Data Processing Layer"
        M["pandas"]
        N["joblib"]
        O["multiprocess"]
    end
    
    A --> H
    A --> K
    A --> M
    A --> N
    B --> E
    B --> F
    C --> E
    C --> F
    D --> E
    D --> F
    E --> I
    F --> I
    G --> I
    H --> I
    H --> J
    K --> I
```

**Technology Stack Components**

The stack is organized into functional layers with clear dependencies between components.

Sources: [requirements.txt:1-11]()

## Data Flow Architecture

### Audio Processing Data Flow

The core data processing follows a systematic pipeline from raw audio files to labeled spectrograms ready for model training.

```mermaid
sequenceDiagram
    participant AudioFiles as "Raw Audio Files"
    participant MetadataCSV as "Metadata CSV Files"
    participant LibrosaLoad as "librosa.load()"
    participant SpecGen as "graph_spectrogram()"
    participant ParallelProc as "Parallel Processing"
    participant OutputDir as "Output Directories"
    
    AudioFiles->>LibrosaLoad: "Load audio at 48kHz"
    MetadataCSV->>SpecGen: "Species ID, time bounds"
    LibrosaLoad->>SpecGen: "Sound data array"
    SpecGen->>SpecGen: "Extract 2-second segments"
    SpecGen->>SpecGen: "Generate mel-spectrogram"
    ParallelProc->>SpecGen: "Parallel execution per audio file"
    SpecGen->>OutputDir: "Save PNG files with metadata"
```

**Data Flow Implementation Details**

Key processing functions handle the transformation pipeline:

- `graph_spectrogram()`: Core spectrogram generation function [extract_melspectrograms.py:107-137]()
- `generate_spectrogram_tp()`: True positive processing wrapper [extract_melspectrograms.py:140-145]()
- `generate_spectrogram_fp()`: False positive processing wrapper [extract_melspectrograms.py:152-157]()

Sources: [extract_melspectrograms.py:107-161]()

### File Organization Structure

The system maintains a structured directory hierarchy that separates raw data, processed spectrograms, and model outputs.

```mermaid
graph TD
    A["multispecies_bioacoustics/"] --> B["Data/"]
    B --> C["Raw_Audio/"]
    B --> D["Labeled_Data/"]
    B --> E["Extracted_Mel_Spectrogram/"]
    
    D --> F["true_positive_metadata.csv"]
    D --> G["false_positive_metadata.csv"]
    
    E --> H["tp/"]
    E --> I["fp/"]
    
    H --> J["*.png files\n(True Positive Spectrograms)"]
    I --> K["*.png files\n(False Positive Spectrograms)"]
    
    C --> L["Audio files\n(48kHz WAV format)"]
```

**Directory Structure Configuration**

The path configuration defines the complete file organization:

| Directory Variable | Purpose | Path |
|-------------------|---------|------|
| `current_dir` | Root project directory | `./multispecies_bioacoustics/` |
| `data_dir` | Main data directory | `Data/` |
| `labeled_data_dir` | Metadata CSV files | `Data/Labeled_Data/` |
| `audio_dir` | Raw audio recordings | `Data/Raw_Audio/` |
| `output_mel_spectrogram_dir` | Processed spectrograms | `Data/Extracted_Mel_Spectrogram/` |

Sources: [extract_melspectrograms.py:27-46]()

## Processing Configuration

### Spectrogram Generation Parameters

The mel-spectrogram extraction uses standardized parameters to ensure consistency across all model training:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Sampling Rate | 48,000 Hz | Audio loading resolution |
| Spectrogram Duration | 2 seconds | Fixed-length segments |
| Image Resolution | 300x300 pixels | CNN input size |
| DPI | 100 | Image quality setting |
| Audio Segment Extraction | `floor(t_min)` to `ceil(t_max)` | Time boundary calculation |

Sources: [extract_melspectrograms.py:108-124]()

### Parallel Processing Implementation

The system leverages multi-core processing for efficient spectrogram generation across large audio datasets.

```mermaid
flowchart LR
    A["Audio File List"] --> B["multiprocessing.cpu_count()"]
    B --> C["joblib.Parallel"]
    C --> D["generate_spectrogram_tp()"]
    C --> E["generate_spectrogram_fp()"]
    D --> F["True Positive PNG Files"]
    E --> G["False Positive PNG Files"]
    
    H["Exception Handling\ntry/except blocks"] --> D
    H --> E
    I["Memory Management\ngc.collect()"] --> D
    I --> E
```

**Parallel Processing Configuration**

The implementation uses joblib for distributed processing with automatic core detection and memory management.

Sources: [extract_melspectrograms.py:147-161]()

## Model Integration Architecture

The three models operate independently but share common input formats and evaluation frameworks, enabling direct performance comparison.

```mermaid
graph TB
    subgraph "Shared Input Layer"
        A["Mel-Spectrogram Images\n224x224 PNG files"]
        B["Species Labels\n24 bird and frog species"]
    end
    
    subgraph "Model Implementations"
        C["VGG16 Baseline\nmodel1_vgg16_architecture_TP_only.py"]
        D["ResNet50 Transfer Learning\nmodel2_transfer_learning_TP_only.py"]  
        E["ResNet50 + Pseudo-labeling\nmodel3_transfer_learning_pseudo_labeling.py"]
    end
    
    subgraph "Shared Evaluation Layer"
        F["Species-level Metrics"]
        G["Confusion Matrix Analysis"]
        H["Conservation Performance Assessment"]
    end
    
    A --> C
    A --> D
    A --> E
    B --> C
    B --> D
    B --> E
    
    C --> F
    D --> F
    E --> F
    F --> G
    F --> H
```

**Model Integration Points**

The architecture enables systematic comparison through standardized interfaces and shared evaluation metrics.

Sources: [README.md:17-22]()

---

