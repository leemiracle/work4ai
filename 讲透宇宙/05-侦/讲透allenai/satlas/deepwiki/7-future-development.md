<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlas · page 7 Future Development · fetched 2026-10-26 -->

# Future Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OngoingProjects.md](OngoingProjects.md)
- [README.md](README.md)
- [satlaspretrain_urls.txt](satlaspretrain_urls.txt)
- [satlaspretrain_urls_small.txt](satlaspretrain_urls_small.txt)

</details>



This document outlines ongoing and planned development initiatives for the Satlas project. It provides an overview of the roadmap, current projects in progress, and future planned features. For information about the current system architecture and components, see [Overview](#1) and [Model System](#3).

## Development Roadmap Overview

Satlas is continually evolving with several parallel development streams focused on enhancing accessibility, expanding data offerings, and improving model capabilities. The following diagram illustrates the high-level roadmap of development initiatives.

```mermaid
gantt
    title "Satlas Development Roadmap (2024-2025)"
    dateFormat  YYYY-MM
    axisFormat  %b %Y
    
    section Data Improvements
    Satlas.allen.ai 2023-2024 Data          :active, data1, 2023-12, 2024-03
    Release on Google Earth Engine           :gee, 2024-03, 2024-09
    
    section Model Enhancements
    SatlasPretrain Ease-of-use              :active, ease, 2023-12, 2024-04
    Updated Training Data & Models           :models, 2024-04, 2024-08
    Improved Super-Resolution                :super, 2024-02, 2024-08
    
    section New Features
    Off-shore Platform Classification        :platform, 2024-04, 2024-09
    Forest Loss Cause Classification         :active, forest, 2024-01, 2024-12
    Land Cover Monitoring                    :landcover, 2024-06, 2025-03
```

Sources: [OngoingProjects.md:6-66]()

## Ongoing Projects

The following projects are currently in active development by the Satlas team:

### SatlasPretrain Ease-of-use (75% Complete)

This initiative focuses on making SatlasPretrain foundation models more accessible for downstream tasks.

**Key accomplishments:**
- Released the `satlaspretrain_models` package for simplified model application
- Made the SatlasPretrain dataset available on Hugging Face
- Created accompanying tutorials for model usage

**Remaining work:**
- Integration with TorchGeo platform (expected March 2024)

```mermaid
flowchart LR
    subgraph "SatlasPretrain Access Improvements"
        A["satlaspretrain_models Package"] --> D["User Application"]
        B["Hugging Face Integration"] --> D
        C["TorchGeo Integration\n(Planned)"] --> D
    end
    
    D --> E["Downstream Tasks"]
    
    subgraph "Downstream Applications"
        E --> F["Fine-tuning"]
        E --> G["Transfer Learning"]
        E --> H["Custom Inference"]
    end
```

Sources: [OngoingProjects.md:14-21](), [README.md:9-11]()

### Data Updates for satlas.allen.ai (75% Complete)

This project involves updating the Satlas website with more recent data products.

**Key accomplishments:**
- Released renewable energy and marine infrastructure data through 2024-01
- Fixed shapefile downloads

**Remaining work:**
- Website integration of new data (expected March 2024)

```mermaid
flowchart TD
    A["Sentinel-2 Imagery\n(2023-2024)"] --> B["Model Inference"]
    B --> C["Data Product Generation"]
    
    subgraph "Data Products"
        C --> D["Renewable Energy\nInfrastructure"]
        C --> E["Marine Infrastructure"]
        C --> F["Tree Cover"]
    end
    
    subgraph "Distribution Channels"
        D --> G["Direct Downloads\n(Completed)"]
        E --> G
        F --> G
        
        D --> H["satlas.allen.ai\n(In Progress)"]
        E --> H
        F --> H
    end
```

Sources: [OngoingProjects.md:23-31](), [README.md:19-21]()

### Forest Loss Cause Classification (25% Complete)

This project focuses on developing a model that can classify the causes of detected forest loss from Sentinel-2 imagery.

**Key features:**
- Classification of forest loss into categories like mining, agriculture, and natural disasters
- Integration with existing tree cover monitoring capabilities
- Targeted release in Q4 2024

```mermaid
flowchart LR
    A["Sentinel-2 Time Series"] --> B["Forest Loss Detection"]
    B --> C["Cause Classification Model"]
    
    subgraph "Loss Classifications"
        C --> D["Agricultural Conversion"]
        C --> E["Resource Extraction\n(Mining, Logging)"]
        C --> F["Natural Disasters\n(Fire, Hurricane)"]
        C --> G["Urban Development"]
        C --> H["Other Causes"]
    end
```

Sources: [OngoingProjects.md:64-66]()

## Planned Future Projects

### Release Updated Training Data and Fine-tuned Models

Currently, the training data and models were last released in July 2023. This initiative aims to establish a more efficient system for automatically sharing updated training data and models.

**Objectives:**
- Create a streamlined release pipeline for training data
- Implement automated model publishing
- Provide more frequent updates to fine-tuned models

Sources: [OngoingProjects.md:33-38](), [README.md:43-55]()

### Off-shore Platform Classification (Q3 2024)

This exploratory project aims to enhance the existing marine infrastructure detection by adding classification capabilities.

**Planned features:**
- Classification of detected offshore platforms into categories:
  - Oil and gas platforms
  - Air force towers
  - Power line structures
  - Other marine infrastructure

```mermaid
flowchart TD
    A["Marine Infrastructure\nDetection"] --> B["Platform Detection"]
    
    B --> C["Platform Classification\nModel"]
    
    subgraph "Classification Types"
        C --> D["Oil and Gas Platforms"]
        C --> E["Air Force Towers"]
        C --> F["Power Line Structures"]
        C --> G["Other Marine Structures"]
    end
    
    subgraph "Existing System Integration"
        H["SatlasNet Model"] --> A
        I["Sentinel-2 Imagery"] --> H
    end
```

Sources: [OngoingProjects.md:40-43]()

### Improved Super-Resolution (Q3 2024)

This project focuses on enhancing the accuracy and quality of the super-resolution capabilities in Satlas.

**Planned improvements:**
- Enhanced model architecture for better detail preservation
- Updated dataset for training
- Refreshed super-resolution layer in the Satlas web interface

Sources: [OngoingProjects.md:46-49](), [README.md:12]()

### Release on Google Earth Engine (Q3 2024)

This initiative aims to make all Satlas geospatial data products available on Google Earth Engine.

**Benefits:**
- Broader accessibility of Satlas data
- Integration with other geospatial datasets
- Enhanced analysis capabilities through Google Earth Engine's computing platform

Sources: [OngoingProjects.md:52-54]()

### Land Cover Monitoring and Change Detection (Q1 2025)

This long-term exploratory project is investigating the feasibility of global monitoring of land cover and the detection of land cover changes using Sentinel-2 imagery.

**Planned capabilities:**
- Continuous monitoring of land cover changes
- Detection of urban expansion
- Identification of forest conversion to agriculture
- Time series analysis for change tracking

```mermaid
flowchart TD
    A["Time Series Sentinel-2 Imagery"] --> B["Land Cover Classification"]
    A --> C["Change Detection Algorithm"]
    
    B --> D["Land Cover Maps"]
    C --> E["Change Detection Maps"]
    
    subgraph "Change Categories"
        E --> F["Forest to Agriculture"]
        E --> G["Natural to Urban"]
        E --> H["Water Body Changes"]
        E --> I["Other Conversions"]
    end
    
    subgraph "System Integration"
        J["Satlas Foundation Models"] --> B
        J --> C
    end
```

Sources: [OngoingProjects.md:57-60]()

## Technical Integration with Existing Systems

The following diagram illustrates how the planned future developments integrate with the existing Satlas architecture:

```mermaid
flowchart TD
    subgraph "Foundation Layer"
        FM["SatlasPretrain\nFoundation Models"]
        DS["SatlasPretrain Dataset"]
        DS --> FM
    end
    
    subgraph "Model Layer"
        SN["SatlasNet Architecture"]
        TP["Training Pipeline"]
        IP["Inference Pipeline"]
        
        FM --> SN
        SN --> TP
        TP --> IP
    end
    
    subgraph "Current Data Products"
        REI["Renewable Energy\nInfrastructure"]
        MI["Marine Infrastructure"]
        TC["Tree Cover"]
        SR["Super-Resolution"]
        
        IP --> REI
        IP --> MI
        IP --> TC
        IP --> SR
    end
    
    subgraph "Future Data Products"
        PC["Platform Classification"]
        ISR["Improved Super-Resolution"]
        LCCD["Land Cover Change\nDetection"]
        FLCC["Forest Loss Cause\nClassification"]
        
        IP --> PC
        IP --> ISR
        IP --> LCCD
        IP --> FLCC
    end
    
    subgraph "Distribution Channels"
        WS["satlas.allen.ai"]
        DD["Direct Downloads"]
        HF["Hugging Face"]
        GEE["Google Earth Engine\n(Planned)"]
        
        REI --> WS
        MI --> WS
        TC --> WS
        SR --> WS
        
        REI --> DD
        MI --> DD
        TC --> DD
        SR --> DD
        
        DS --> HF
        FM --> HF
        
        REI --> GEE
        MI --> GEE
        TC --> GEE
        LCCD --> GEE
    end
```

Sources: [README.md:27-33](), [OngoingProjects.md:14-66]()

## Development Timeline

The table below summarizes the development timeline for current and planned projects:

| Project | Status | Progress | Expected Completion |
|---------|--------|----------|---------------------|
| SatlasPretrain Ease-of-use | Active | 75% | March 2024 |
| satlas.allen.ai 2023 Data | Active | 75% | March 2024 |
| Release Updated Training Data and Models | Not Started | 0% | Q3 2024 |
| Off-shore Platform Classification | Exploratory | Planning | Q3 2024 |
| Improved Super-Resolution | Exploratory | Research | Q3 2024 |
| Release on Google Earth Engine | Not Started | 0% | Q3 2024 |
| Forest Loss Cause Classification | Active | 25% | Q4 2024 |
| Land Cover Monitoring and Change Detection | Exploratory | Research | Q1 2025 |

Sources: [OngoingProjects.md:14-66]()

## Update Frequency

As noted in the OngoingProjects.md file, the Satlas team updates this roadmap approximately monthly. All timelines are estimates and subject to change as projects develop, encounter challenges, or priorities shift.

Sources: [OngoingProjects.md:1-5]()