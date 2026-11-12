<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/XPretrain · page 1 XPretrain Overview · fetched 2026-10-26 -->

# XPretrain Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the XPretrain repository, which serves as a centralized collection of multi-modality learning research from Microsoft Research's MSM (Multimedia Search and Mining) group. The repository encompasses both video-language and image-language pre-training models, datasets, and related research implementations spanning 2021-2023.

For specific implementation details of individual models, see the Video-Language Research Track ([#2](#2)) and Image-Language Research Track ([#3](#3)). For development setup and configuration guidance, see the Development Guide ([#4](#4)).

## Repository Architecture

XPretrain functions as an umbrella repository containing multiple independent research projects that share common themes in multi-modality learning and pre-training methodologies. The repository is organized into distinct research tracks with their own codebases, datasets, and model implementations.

### Multi-modality Learning Tracks

```mermaid
graph TD
    XPretrain["XPretrain Repository<br/>microsoft/XPretrain"]
    
    subgraph "Video & Language Track"
        Dataset["hd-vila-100m/<br/>HD-VILA-100M Dataset"]
        HDVILA["hd-vila/<br/>HD-VILA Model"]
        LFVILA["LF-VILA/<br/>LF-VILA Model"] 
        CLIPVIP["CLIP-ViP/<br/>CLIP-ViP Model"]
    end
    
    subgraph "Image & Language Track"
        PixelBERT["Pixel-BERT<br/>(External Reference)"]
        SOHO["SOHO<br/>(External Reference)"]
        VisualParsing["visualparsing/<br/>VisualParsing Model"]
    end
    
    XPretrain --> Dataset
    XPretrain --> HDVILA
    XPretrain --> LFVILA
    XPretrain --> CLIPVIP
    XPretrain --> PixelBERT
    XPretrain --> SOHO
    XPretrain --> VisualParsing
    
    Dataset --> HDVILA
    Dataset --> LFVILA
    Dataset --> CLIPVIP
```

Sources: [README.md:1-66]()

The repository implements two primary research tracks:

| Track | Components | Purpose |
|-------|------------|---------|
| **Video & Language** | `hd-vila-100m/`, `hd-vila/`, `LF-VILA/`, `CLIP-ViP/` | Video-language understanding and pre-training |
| **Image & Language** | `visualparsing/`, external references | Image-language understanding and pre-training |

## Research Timeline and Publications

### Code Repository Structure with Publication Timeline

```mermaid
timeline
    title "XPretrain Research Evolution"
    section 2021
        SOHO : CVPR 2021 oral
             : Image-language pre-training
        VisualParsing : NeurIPS 2021
                     : visualparsing/ directory
    section 2022  
        HD-VILA-100M : March 2022 dataset release
                    : hd-vila-100m/ directory
        HD-VILA : CVPR 2022 acceptance
               : hd-vila/ directory
               : September 2022 code release
        LF-VILA : NeurIPS 2022 acceptance
               : LF-VILA/ directory
    section 2023
        CLIP-ViP : ICLR 2023 acceptance
                : CLIP-ViP/ directory  
                : March 2023 code release
        LF-VILA Code : March 2023 code release
                    : LF-VILA/ directory updates
```

Sources: [README.md:31-37]()

### Research Progression Model

The repository demonstrates a clear research progression where foundational work enables subsequent innovations:

| Year | Innovation | Code Location | Key Contribution |
|------|------------|---------------|------------------|
| 2021 | VisualParsing | `visualparsing/` | Transformer-based image-language pre-training |
| 2022 | HD-VILA-100M | `hd-vila-100m/` | Large-scale video-language dataset foundation |
| 2022 | HD-VILA | `hd-vila/` | High-resolution video-language pre-training |
| 2022 | LF-VILA | `LF-VILA/` | Long-form video processing capabilities |
| 2023 | CLIP-ViP | `CLIP-ViP/` | Adaptation of image-text models to video |

## Technical Architecture Patterns

### Common Pre-training Framework

```mermaid
graph LR
    subgraph "Data Layer"
        RawData["Raw Data<br/>(Videos/Images + Text)"]
        ProcessedData["Processed Data<br/>(hd-vila-100m/)"]
    end
    
    subgraph "Model Architecture"
        Stage1["Stage 1: Dual Encoder<br/>(Contrastive Learning)"]
        Stage2["Stage 2: Cross-modal Transformer<br/>(Masked Language/Video Modeling)"]
    end
    
    subgraph "Downstream Tasks"
        Retrieval["Video-Text Retrieval"]
        QA["Video Question Answering"]
        Classification["Video Classification"]
    end
    
    RawData --> ProcessedData
    ProcessedData --> Stage1
    Stage1 --> Stage2
    Stage2 --> Retrieval
    Stage2 --> QA  
    Stage2 --> Classification
```

Sources: [README.md:7-30]()

### Repository File Structure

The codebase follows a modular structure where each research component maintains its own directory with complete implementation:

```mermaid
graph TD
    Root["XPretrain/"]
    
    subgraph "Core Components"
        README["README.md<br/>(Repository Overview)"]
        License["LICENSE<br/>(MIT License)"]
    end
    
    subgraph "Video-Language Components"
        HDVILADataset["hd-vila-100m/<br/>(Dataset + Processing)"]
        HDVILAModel["hd-vila/<br/>(HD-VILA Implementation)"]
        LFVILAModel["LF-VILA/<br/>(Long-form Model)"]
        CLIPViPModel["CLIP-ViP/<br/>(Adaptation Model)"]
    end
    
    subgraph "Image-Language Components"  
        VisualParsingModel["visualparsing/<br/>(VisualParsing Implementation)"]
    end
    
    Root --> README
    Root --> License
    Root --> HDVILADataset
    Root --> HDVILAModel
    Root --> LFVILAModel
    Root --> CLIPViPModel
    Root --> VisualParsingModel
```

Sources: [README.md:1-66]()

## Research Contributions and Impact

### Video-Language Track Achievements

The video-language research track represents the primary focus of recent XPretrain developments:

| Model | Key Innovation | Technical Contribution |
|-------|----------------|----------------------|
| **HD-VILA-100M** | Large-scale dataset | 3.3M videos, 371.5K hours, high-resolution |
| **HD-VILA** | High-resolution VLP | Dual-stage training with masked modeling |
| **LF-VILA** | Long-form processing | MTC loss and HTWA for extended video content |
| **CLIP-ViP** | Transfer learning | Post-pretraining adaptation from image to video |

### Image-Language Track Foundation

The image-language components provide foundational research that informs video-language developments:

| Model | Publication Venue | Core Technology |
|-------|------------------|-----------------|
| **SOHO** | CVPR 2021 (oral) | Quantized visual tokens |
| **VisualParsing** | NeurIPS 2021 | Transformer-based architecture |
| **Pixel-BERT** | Research paper | End-to-end image-language pre-training |

Sources: [README.md:15-29]()

## Governance and Community

### Contribution Framework

XPretrain operates under Microsoft's standard open-source governance model with specific requirements for contributors:

- **Contributor License Agreement (CLA)** required for all contributions
- **Microsoft Open Source Code of Conduct** compliance mandatory
- **Security and issue reporting** through GitHub issue system
- **Primary contacts**: Bei Liu (`bei.liu@microsoft.com`) and Jianlong Fu (`jianf@microsoft.com`)

### Licensing and Usage

The repository implements Microsoft's standard licensing framework with considerations for research use, trademark guidelines, and responsible AI practices. For detailed licensing information, see Licensing ([#5.1](#5.1)). For responsible AI considerations specific to video-language models, see Responsible AI ([#5.2](#5.2)).

Sources: [README.md:40-66]()

---

