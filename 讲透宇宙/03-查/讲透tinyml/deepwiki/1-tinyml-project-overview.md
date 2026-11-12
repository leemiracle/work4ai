<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/tinyml · page 1 TinyML Project Overview · fetched 2026-10-30 -->

# TinyML Project Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the TinyML umbrella project, which aims to enable efficient deep learning on resource-constrained edge devices. The TinyML project addresses the fundamental challenge of deploying AI systems that traditionally require large computational resources, extensive labeled datasets, and significant engineering expertise onto billions of mobile phones and IoT devices.

This overview covers the project's three main sub-projects, their technical approaches, and deployment outcomes. For detailed implementation guides, see [Getting Started Guide](#5). For specific sub-project documentation, see [TinyTL: On-Device Learning](#2) and [NetAug: Network Augmentation for Tiny Networks](#3).

Sources: [README.md:23-32]()

## Project Architecture and Sub-Projects

The TinyML project consists of three core sub-projects, each addressing different aspects of efficient edge AI deployment:

### TinyML Sub-Project Structure

```mermaid
graph TB
    subgraph "TinyML Repository Structure"
        ROOT["tinyml/"]
        TINYTL_DIR["tinytl/"]
        NETAUG_DIR["netaug/"]
        README["README.md"]
    end
    
    subgraph "TinyTL Components"
        TINYTL_TRAIN["tinytl_fgvc_train.py"]
        DATASET_SETUP["make_all_datasets.sh"]
        STANFORD_CARS["make_stanford_cars.py"]
    end
    
    subgraph "NetAug Components"
        NETAUG_TRAIN["bash/imagenet/"]
        NETAUG_EVAL["eval.py"]
        NETAUG_TRANSFER["bash/transfer/"]
    end
    
    subgraph "External Projects"
        MCUNET_REPO["github.com/mit-han-lab/mcunet"]
    end
    
    ROOT --> TINYTL_DIR
    ROOT --> NETAUG_DIR
    ROOT --> README
    
    TINYTL_DIR --> TINYTL_TRAIN
    TINYTL_DIR --> DATASET_SETUP
    TINYTL_DIR --> STANFORD_CARS
    
    NETAUG_DIR --> NETAUG_TRAIN
    NETAUG_DIR --> NETAUG_EVAL
    NETAUG_DIR --> NETAUG_TRANSFER
    
    ROOT -.->|"Refactored to standalone"| MCUNET_REPO
```

Sources: [README.md:15-21](), [README.md:3]()

### Sub-Project Technical Focus

| Project | Directory | Keywords | Primary Focus |
|---------|-----------|----------|---------------|
| TinyTL | `tinytl/` | On-device learning, Memory-efficient transfer learning | Activation memory optimization |
| NetAug | `netaug/` | Training technique for tiny neural networks | Network augmentation during training |
| MCUNet | External repo | Memory-efficient inference, System-algorithm co-design | Inference optimization |

Sources: [README.md:16-20]()

## Technical Problem-Solution Mapping

The TinyML project addresses specific challenges in deploying deep learning on edge devices through targeted technical solutions:

### Challenge-Solution Architecture

```mermaid
graph LR
    subgraph "Edge AI Challenges"
        COMPUTE_CHALLENGE["Large Computational Resources Required"]
        EXPERT_CHALLENGE["Many AI Experts Required"]
        DATA_CHALLENGE["Large Labeled Datasets Required"]
        MEMORY_CHALLENGE["Memory Constraints for Training"]
        TINY_TRAINING["Tiny Network Training Difficulties"]
    end
    
    subgraph "TinyML Technical Solutions"
        NETAUG_SOLUTION["NetAug: Network Augmentation<br/>Location: netaug/"]
        TINYTL_SOLUTION["TinyTL: Activation Memory Reduction<br/>Location: tinytl/"]
        MCUNET_SOLUTION["MCUNet: System-Algorithm Co-design<br/>External Repository"]
    end
    
    subgraph "Implementation Outcomes"
        REDUCED_COMPUTE["Less Computation Required"]
        FEWER_ENGINEERS["Fewer Engineers Required"]
        LESS_DATA["Less Data Required"]
        EFFICIENT_LEARNING["Efficient On-Device Learning"]
        MEMORY_EFFICIENT["Memory-Efficient Inference"]
    end
    
    TINY_TRAINING --> NETAUG_SOLUTION
    MEMORY_CHALLENGE --> TINYTL_SOLUTION
    COMPUTE_CHALLENGE --> MCUNET_SOLUTION
    
    NETAUG_SOLUTION --> REDUCED_COMPUTE
    NETAUG_SOLUTION --> LESS_DATA
    TINYTL_SOLUTION --> EFFICIENT_LEARNING
    MCUNET_SOLUTION --> MEMORY_EFFICIENT
    
    REDUCED_COMPUTE --> DEPLOYMENT["Edge AI Deployment<br/>100K+ IoT Devices"]
    FEWER_ENGINEERS --> DEPLOYMENT
    LESS_DATA --> DEPLOYMENT
    EFFICIENT_LEARNING --> DEPLOYMENT
    MEMORY_EFFICIENT --> DEPLOYMENT
```

Sources: [README.md:24-32](), [README.md:5]()

## Deployment Impact and Industrial Collaboration

The TinyML project has achieved significant real-world deployment success:

### Deployment Statistics

- **Scale**: Over 100,000 IoT devices deployed
- **Industrial Partners**: Active collaboration with industry for real-world applications
- **Applications**: Smart home, smart retail, autonomous driving, and AIoT systems

### Media Coverage and Recognition

The project has received coverage from major technology publications:
- MIT News, WIRED, Morning Brew
- Stacey on IoT, Analytics Insight, Techable

Sources: [README.md:5](), [README.md:7-13](), [README.md:24-32]()

## Research Foundation and Publication History

The TinyML project builds upon a foundation of research spanning 2018-2020:

### Research Timeline and Dependencies

```mermaid
graph TD
    subgraph "Foundational Research 2018-2019"
        AMC["AMC: AutoML for Model Compression<br/>ECCV'18"]
        PROXYLESS["ProxylessNAS: Direct Neural Architecture Search<br/>ICLR'19"]
        HAQ["HAQ: Hardware-Aware Automated Quantization<br/>CVPR'19"]
    end
    
    subgraph "Advanced Research 2020"
        OFA["Once for All: Train One Network<br/>ICLR'20"]
        MCUNET_PAPER["MCUNet: Tiny Deep Learning on IoT Devices<br/>NeurIPS'20"]
        TINYTL_PAPER["TinyTL: Reduce Memory, Not Parameters<br/>NeurIPS'20"]
        NETAUG_PAPER["NetAug: Network Augmentation<br/>NeurIPS'20"]
    end
    
    subgraph "Current Implementation"
        TINYTL_CODE["tinytl/ directory"]
        NETAUG_CODE["netaug/ directory"]
        MCUNET_CODE["External mcunet repository"]
    end
    
    AMC --> OFA
    PROXYLESS --> OFA
    HAQ --> MCUNET_PAPER
    
    OFA --> TINYTL_PAPER
    OFA --> NETAUG_PAPER
    PROXYLESS --> MCUNET_PAPER
    
    TINYTL_PAPER --> TINYTL_CODE
    NETAUG_PAPER --> NETAUG_CODE
    MCUNET_PAPER --> MCUNET_CODE
```

Sources: [README.md:44-58]()

## Technology Stack and Dependencies

The TinyML project relies on several key technologies:

### Core Dependencies

- **PyTorch Framework**: Primary deep learning framework
- **Python 3.6+**: Runtime environment
- **torchpack**: Distributed training support
- **torchprofile**: Model profiling capabilities

### System Requirements

Each sub-project has specific system requirements and installation procedures detailed in their respective documentation. For complete setup instructions, see [Getting Started Guide](#5).

Sources: [README.md:1-59]()

## Project Status and Future Development

### Current Status

- **MCUNet**: Refactored into standalone repository at `github.com/mit-han-lab/mcunet`
- **TinyTL**: Active development in `tinytl/` directory
- **NetAug**: Active development in `netaug/` directory

### Development Focus

The project continues to evolve with focus on:
- Industrial partnership expansion
- Real-world deployment optimization
- Technology transfer to production environments

For detailed implementation information on specific sub-projects, see [TinyTL: On-Device Learning](#2) and [NetAug: Network Augmentation for Tiny Networks](#3).

Sources: [README.md:3](), [README.md:5]()

---

