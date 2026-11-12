# Page: TinyML Project Overview

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

# Page: TinyTL: On-Device Learning

# TinyTL: On-Device Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tinytl/README.md](tinytl/README.md)

</details>



## Purpose and Scope

This document covers the TinyTL sub-project within the TinyML ecosystem, which focuses on enabling efficient transfer learning directly on edge devices. TinyTL addresses the memory bottleneck in on-device learning by reducing activation memory consumption rather than model parameters, making fine-tuning feasible on resource-constrained devices.

For information about the broader TinyML project context and related sub-projects, see [TinyML Project Overview](#1). For dataset preparation procedures, see [Dataset Setup and Preparation](#2.1).

## Core Methodology

TinyTL's fundamental insight is that **activation memory, not model parameters, is the primary bottleneck for on-device learning**. Traditional approaches focus on reducing the number of trainable parameters, but TinyTL demonstrates that activation tensors consume significantly more memory during the forward and backward passes.

### Memory Analysis: Activations vs Parameters

```mermaid
graph TB
    subgraph "Traditional Approach"
        TA1["Reduce Parameters"] --> TA2["Still High Memory Usage"]
        TA2 --> TA3["Limited Device Support"]
    end
    
    subgraph "TinyTL Approach"
        TL1["Reduce Activations"] --> TL2["Lower Memory Usage"]
        TL2 --> TL3["Efficient On-Device Learning"]
    end
    
    subgraph "Memory Breakdown"
        MB1["Parameters: ~4MB"]
        MB2["Activations: ~40MB+"]
        MB3["Gradients: ~40MB+"]
    end
    
    MB2 --> TL1
    MB3 --> TL1
    MB1 --> TA1
    
    TL3 --> RESULT["Successful Edge Deployment"]
    TA3 --> FAILED["Memory Constraints"]
```

**TinyTL Memory Optimization Strategy**

Sources: [tinytl/README.md:19-22]()

### Transfer Learning Architecture

TinyTL implements a specialized transfer learning pipeline that combines activation reduction with batch size 1 training for maximum memory efficiency:

```mermaid
graph LR
    subgraph "Input Processing"
        DS["Dataset Setup<br/>make_all_datasets.sh"] --> PREP["Data Preparation<br/>Class-based Structure"]
    end
    
    subgraph "TinyTL Training Pipeline"
        PREP --> TL1["tinytl_fgvc_train.py<br/>Main Training Script"]
        TL1 --> TL2["Activation Reduction<br/>Techniques"]
        TL2 --> TL3["Batch Size 1<br/>Training"]
        TL3 --> TL4["Fine-Grained Visual<br/>Classification"]
    end
    
    subgraph "Output"
        TL4 --> MODEL["Optimized Model<br/>Low Memory Footprint"]
    end
```

**TinyTL System Architecture**

Sources: [tinytl/README.md:39-48]()

## System Components

### Core Training Infrastructure

The TinyTL system consists of several key components that work together to enable efficient on-device learning:

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Dataset Setup | `dataset_setup_scripts/make_all_datasets.sh` | Prepares all required datasets |
| Training Script | `tinytl_fgvc_train.py` | Main training entry point |
| Experiment Scripts | `exp_scripts/` | Pre-configured experiment workflows |

### Implementation Architecture

```mermaid
graph TD
    subgraph "Dataset Layer"
        DS1["make_all_datasets.sh<br/>Dataset Preparation"] --> DS2["Stanford Cars Setup<br/>make_stanford_cars.py"]
        DS2 --> DS3["FGVC Dataset Structure<br/>Class-based Organization"]
    end
    
    subgraph "Training Layer"
        TL1["tinytl_fgvc_train.py<br/>Main Training Logic"] --> TL2["Activation Memory<br/>Optimization"]
        TL2 --> TL3["Batch Size 1<br/>Training Support"]
        TL3 --> TL4["Transfer Learning<br/>Experiments"]
    end
    
    subgraph "Experiment Layer"
        EL1["exp_scripts/<br/>Experiment Configs"] --> EL2["Fine-Grained Visual<br/>Classification Tasks"]
        EL2 --> EL3["Performance Evaluation<br/>Results"]
    end
    
    DS3 --> TL1
    TL4 --> EL1
    EL3 --> DEPLOY["Edge Device<br/>Deployment"]
```

**TinyTL Implementation Components**

Sources: [tinytl/README.md:39-48]()

## Usage Workflow

### System Requirements

TinyTL requires a minimal but specific environment setup:

- **Python**: 3.6 or higher
- **PyTorch**: 1.4.0 or higher
- **Memory**: Optimized for low-memory devices

Sources: [tinytl/README.md:42-44]()

### Execution Pipeline

The typical workflow for using TinyTL follows this sequence:

```mermaid
flowchart TD
    START["Start TinyTL Setup"] --> SETUP["bash make_all_datasets.sh<br/>in dataset_setup_scripts/"]
    SETUP --> VERIFY["Verify Dataset Structure<br/>Class-based Organization"]
    VERIFY --> CONFIG["Configure Experiments<br/>exp_scripts/ folder"]
    CONFIG --> TRAIN["python tinytl_fgvc_train.py<br/>Execute Training"]
    TRAIN --> EVAL["Evaluate Results<br/>Transfer Learning Performance"]
    EVAL --> DEPLOY["Deploy to Edge Device"]
    
    subgraph "Error Handling"
        ERROR1["Dataset Setup Issues"] --> SETUP
        ERROR2["Training Memory Issues"] --> TRAIN
        ERROR3["Performance Issues"] --> CONFIG
    end
```

**TinyTL Execution Workflow**

Sources: [tinytl/README.md:39-48]()

## Key Features and Optimizations

### Activation Memory Reduction

TinyTL's core innovation lies in targeting activation memory rather than model parameters. This approach yields significant memory savings during both forward and backward passes:

- **Forward Pass**: Reduced intermediate activation storage
- **Backward Pass**: Optimized gradient computation memory
- **Batch Processing**: Support for batch size 1 training

### Fine-Grained Visual Classification (FGVC)

The system specializes in fine-grained visual classification tasks, which are particularly challenging for edge devices due to subtle inter-class differences requiring detailed feature representations.

### Batch Size 1 Training Support

TinyTL provides specialized support for batch size 1 training, which is crucial for memory-constrained devices but presents unique challenges for gradient stability and batch normalization.

Sources: [tinytl/README.md:34-37]()

## Research Context and Performance

TinyTL was published at NeurIPS 2020 and represents a significant advancement in on-device learning capabilities. The system demonstrates substantial improvements in memory efficiency while maintaining competitive accuracy on transfer learning benchmarks.

The approach builds upon foundational work in neural architecture search and model compression, extending these techniques specifically for the on-device learning scenario.

Sources: [tinytl/README.md:3-11](), [tinytl/README.md:55-67]()

## Current Status and Future Work

### Implementation Status

The current TinyTL implementation provides:
- Complete dataset setup automation
- Transfer learning experiment framework
- Memory-optimized training pipeline
- FGVC task support

### Planned Enhancements

According to the project roadmap, future work includes:
- Enhanced system support for TinyTL deployment
- Additional optimization techniques
- Extended device compatibility

Sources: [tinytl/README.md:50-52]()

---

# Page: Dataset Setup and Preparation

# Dataset Setup and Preparation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tinytl/dataset_setup_scripts/make_stanford_cars.py](tinytl/dataset_setup_scripts/make_stanford_cars.py)

</details>



## Purpose and Scope

This document covers the dataset setup and preparation process for TinyTL experiments, focusing on the automated scripts and procedures for downloading, organizing, and structuring datasets into the required format. The primary example demonstrates the Stanford Cars dataset preparation workflow, which serves as a template for other fine-grained visual classification (FGVC) datasets used in TinyTL.

For information about the actual TinyTL training experiments and model optimization, see [TinyTL: On-Device Learning](#2). For general project setup and installation requirements, see [Getting Started Guide](#5).

## Dataset Requirements Overview

TinyTL experiments require datasets to be organized in a specific class-based directory structure to support efficient on-device learning and memory optimization. The preparation process involves:

- Downloading raw dataset files from official sources
- Extracting annotation metadata from MATLAB files
- Reorganizing images into class-specific directories
- Creating separate train/validation directory structures
- Cleaning up temporary files and archives

## Stanford Cars Dataset Setup Process

The Stanford Cars dataset preparation is handled by the `make_stanford_cars.py` script, which automates the entire download-to-organization pipeline.

### Dataset Download and Extraction Workflow

```mermaid
flowchart TD
    START["make_stanford_cars.py execution"]
    
    subgraph "get_data() function"
        DL1["download_file('cars_train.tgz')"]
        DL2["download_file('cars_test.tgz')"]
        DL3["download_file('car_devkit.tgz')"] 
        DL4["download_file('cars_test_annos_withlabels.mat')"]
        EX1["tarfile.open().extractall()"]
    end
    
    subgraph "train_data() function"
        TD1["io.loadmat('devkit/cars_train_annos.mat')"]
        TD2["Create train/ directory structure"]
        TD3["Move images to class folders"]
    end
    
    subgraph "test_data() function"
        VD1["io.loadmat('cars_test_annos_withlabels.mat')"]
        VD2["Create val/ directory structure"]
        VD3["Move images to class folders"]
    end
    
    subgraph "clear() function"
        CL1["Remove temporary files"]
        CL2["Remove archive files"]
    end
    
    START --> DL1
    DL1 --> DL2
    DL2 --> DL3
    DL3 --> DL4
    DL4 --> EX1
    EX1 --> TD1
    TD1 --> TD2
    TD2 --> TD3
    TD3 --> VD1
    VD1 --> VD2
    VD2 --> VD3
    VD3 --> CL1
    CL1 --> CL2
    CL2 --> COMPLETE["Final dataset structure ready"]
```

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:82-90]()

### File Processing and Organization Logic

The script processes annotation files to extract class labels and organize images accordingly:

```mermaid
flowchart LR
    subgraph "Input Files"
        IF1["cars_train.tgz"]
        IF2["cars_test.tgz"]
        IF3["car_devkit.tgz"]
        IF4["cars_test_annos_withlabels.mat"]
    end
    
    subgraph "Processing Functions"
        PF1["get_data()"]
        PF2["train_data()"]
        PF3["test_data()"]
        PF4["clear()"]
    end
    
    subgraph "MATLAB Processing"
        MP1["io.loadmat()"]
        MP2["annotations[0]"]
        MP3["t[4][0][0] = class_id"]
        MP4["t[5][0] = filename"]
    end
    
    subgraph "Output Structure"
        OS1["~/dataset/stanford_car/train/"]
        OS2["~/dataset/stanford_car/val/"]
        OS3["Class directories (1-196)"]
        OS4["Image files organized by class"]
    end
    
    IF1 --> PF1
    IF2 --> PF1
    IF3 --> PF1
    IF4 --> PF1
    
    PF1 --> PF2
    PF1 --> PF3
    
    PF2 --> MP1
    PF3 --> MP1
    MP1 --> MP2
    MP2 --> MP3
    MP2 --> MP4
    
    MP3 --> OS1
    MP3 --> OS2
    MP4 --> OS3
    OS3 --> OS4
    
    PF4 --> CLEANUP["Temporary files removed"]
```

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:35-67]()

## Dataset Directory Structure

The final organized dataset follows this structure:

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `~/dataset/stanford_car/train/` | Training data | Class directories (1-196) with training images |
| `~/dataset/stanford_car/val/` | Validation data | Class directories (1-196) with test images |
| `~/dataset/stanford_car/train/{class_id}/` | Individual class training | Images belonging to specific car model class |
| `~/dataset/stanford_car/val/{class_id}/` | Individual class validation | Test images for specific car model class |

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:36-66]()

## Configuration and Paths

The script uses the following key configuration:

- **Dataset Root Path**: `~/dataset/stanford_car` (expandable home directory path)
- **Download Function**: `download_file()` with wget command execution
- **Annotation Processing**: MATLAB file parsing using `scipy.io.loadmat()`
- **File Organization**: `shutil.move()` for relocating images to class directories

The `dataset_path` variable is set at [tinytl/dataset_setup_scripts/make_stanford_cars.py:7-8]() and expanded using `os.path.expanduser()`.

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:7-11]()

## Download Sources and File Handling

The script downloads four essential files from Stanford AI servers:

| File | Source URL | Purpose |
|------|-----------|---------|
| `cars_train.tgz` | `http://ai.stanford.edu/~jkrause/car196/cars_train.tgz` | Training images archive |
| `cars_test.tgz` | `http://ai.stanford.edu/~jkrause/car196/cars_test.tgz` | Test images archive |
| `car_devkit.tgz` | `https://ai.stanford.edu/~jkrause/cars/car_devkit.tgz` | Development kit with annotations |
| `cars_test_annos_withlabels.mat` | `http://ai.stanford.edu/~jkrause/car196/cars_test_annos_withlabels.mat` | Test annotations with labels |

The `download_file()` function at [tinytl/dataset_setup_scripts/make_stanford_cars.py:14-23]() handles URL downloads using wget and checks for existing files to avoid redundant downloads.

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:25-33]()

## Cleanup and Temporary File Management

After processing, the `clear()` function removes temporary files and archives to maintain a clean dataset directory:

- Archive files: `cars_train.tgz`, `cars_test.tgz`, `car_devkit.tgz`
- Temporary directories: `cars_test/`, `cars_train/`, `devkit/`
- Intermediate files: `cars_test.txt`, `cars_train.txt`, `cars_test_annos_withlabels.mat`

The cleanup process is defined at [tinytl/dataset_setup_scripts/make_stanford_cars.py:69-80]() and ensures only the final organized dataset structure remains.

**Sources:** [tinytl/dataset_setup_scripts/make_stanford_cars.py:69-86]()

---

# Page: NetAug: Network Augmentation for Tiny Networks

# NetAug: Network Augmentation for Tiny Networks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [netaug/README.md](netaug/README.md)

</details>



## Purpose and Scope

NetAug is a training technique designed specifically for tiny neural networks that addresses the fundamental challenge that training tiny networks is different from training large networks. The system provides network augmentation during the training process to give tiny networks more supervision, ultimately improving their performance on resource-constrained edge devices.

This page covers the NetAug methodology, training procedures, evaluation framework, and pretrained models. For on-device learning techniques that complement NetAug, see [TinyTL: On-Device Learning](#2). For broader project context and setup instructions, see [Getting Started Guide](#5).

**Sources:** [netaug/README.md:1-87]()

## Core Methodology

NetAug addresses the key insight that tiny neural networks require different training strategies than large networks. The approach augments tiny networks during training to provide additional supervision signals that help overcome the limitations of reduced model capacity.

### Training Challenges for Tiny Networks

```mermaid
graph TB
    subgraph "Large Networks"
        LN1["High Model Capacity"]
        LN2["Abundant Parameters"]
        LN3["Standard Training Works"]
    end
    
    subgraph "Tiny Networks"
        TN1["Limited Model Capacity"]
        TN2["Few Parameters"]
        TN3["Training Difficulties"]
    end
    
    subgraph "NetAug Solution"
        NA1["Network Augmentation"]
        NA2["More Supervision"]
        NA3["Channel Sorting"]
        NA4["Width Multiplier Management"]
    end
    
    TN3 --> NA1
    NA1 --> NA2
    NA2 --> NA3
    NA2 --> NA4
    
    NA3 --> RESULT["Improved Tiny Network Performance"]
    NA4 --> RESULT
```

### NetAug Training Pipeline

```mermaid
flowchart TD
    subgraph "Training Process"
        TP1["torchpack dist-run"]
        TP2["bash/imagenet scripts"]
        TP3["Network Augmentation"]
        TP4["Channel L1 Sorting"]
        TP5["Width Multiplier Control"]
    end
    
    subgraph "Post-Training"
        PT1["BN Statistics Re-estimation"]
        PT2["eval.py Evaluation"]
        PT3["Model Profiling"]
    end
    
    subgraph "Outputs"
        OUT1["Trained Models"]
        OUT2["Performance Metrics"]
        OUT3["Pretrained Weights"]
    end
    
    TP1 --> TP2
    TP2 --> TP3
    TP3 --> TP4
    TP4 --> TP5
    TP5 --> PT1
    PT1 --> PT2
    PT2 --> PT3
    PT3 --> OUT1
    OUT1 --> OUT2
    OUT1 --> OUT3
```

**Sources:** [netaug/README.md:19-27](), [netaug/README.md:66-74]()

## Technical Implementation Details

### Key Implementation Considerations

NetAug includes several critical technical modifications for training tiny networks effectively:

| Component | Implementation Detail | Rationale |
|-----------|----------------------|-----------|
| Initialization | `nn.init.kaiming_uniform` | `fout` initialization fails for high expand ratios |
| Channel Sorting | L1 value sorting per epoch | Forces target model to use most important channels |
| Width Multiplier | Ratio = 1.0 in second half | Improves results in later training phases |
| BN Statistics | Re-estimation with training subset | Running mean/var become inaccurate during augmentation |

### Training Script Organization

```mermaid
graph TB
    subgraph "Training Scripts"
        TS1["bash/imagenet/"]
        TS2["ImageNet Training Scripts"]
        TS3["Model-Specific Configurations"]
    end
    
    subgraph "Transfer Learning"
        TL1["bash/transfer/"]
        TL2["Transfer Learning Scripts"]
        TL3["Pretrained Model Loading"]
    end
    
    subgraph "Evaluation"
        EV1["eval.py"]
        EV2["torchpack dist-run"]
        EV3["Model Profiling"]
    end
    
    TS1 --> TS2
    TS2 --> TS3
    TL1 --> TL2
    TL2 --> TL3
    EV1 --> EV2
    EV2 --> EV3
    
    TS3 --> EV1
    TL3 --> EV1
```

**Sources:** [netaug/README.md:66-74](), [netaug/README.md:75-76]()

## Environment and Dependencies

### System Requirements

The NetAug system requires specific environment configurations:

- **Python**: 3.8.5
- **PyTorch**: 1.8.2
- **torchpack**: Distributed training framework
- **torchprofile**: Model profiling utilities

### Dependency Integration

```mermaid
graph TB
    subgraph "Core Dependencies"
        CD1["Python 3.8.5"]
        CD2["PyTorch 1.8.2"]
    end
    
    subgraph "Training Framework"
        TF1["torchpack"]
        TF2["Distributed Training"]
        TF3["Multi-GPU Support"]
    end
    
    subgraph "Profiling Tools"
        PT1["torchprofile"]
        PT2["Model Analysis"]
        PT3["Performance Metrics"]
    end
    
    CD1 --> CD2
    CD2 --> TF1
    TF1 --> TF2
    TF2 --> TF3
    CD2 --> PT1
    PT1 --> PT2
    PT2 --> PT3
```

**Sources:** [netaug/README.md:40-44]()

## Pretrained Models

### Available Model Configurations

NetAug provides pretrained models for various tiny network architectures:

| Model Architecture | Parameters | MACs | ImageNet Top1 | Pretrained Weights |
|-------------------|------------|------|---------------|-------------------|
| MobileNetV2-Tiny + NetAug | 0.75M | 23.5M | 53.3% | Google Drive |
| MCUNet + NetAug | 0.74M | 81.8M | 62.7% | Google Drive |
| ProxylessNAS-Mobile + NetAug | 1.8M | 35.7M | 60.8% | Google Drive |

### Model Evaluation Framework

```mermaid
graph LR
    subgraph "Evaluation Process"
        EP1["eval.py"]
        EP2["torchpack dist-run"]
        EP3["Model Loading"]
        EP4["Dataset Processing"]
        EP5["Performance Metrics"]
    end
    
    subgraph "Configuration"
        CF1["--dataset imagenet"]
        CF2["--data_path /dataset/imagenet/"]
        CF3["--image_size 160"]
        CF4["--model proxylessnas-0.35"]
        CF5["--init_from <pretrained_weight>"]
    end
    
    EP1 --> EP2
    EP2 --> EP3
    EP3 --> EP4
    EP4 --> EP5
    
    CF1 --> EP4
    CF2 --> EP4
    CF3 --> EP4
    CF4 --> EP3
    CF5 --> EP3
```

**Sources:** [netaug/README.md:46-64]()

## Training Procedures

### ImageNet Training

Training scripts for NetAug models are organized under `bash/imagenet/` and utilize the `torchpack` distributed training framework. The training process incorporates the key NetAug techniques:

1. **Channel Sorting**: Channels are sorted by L1 value at the beginning of each epoch
2. **Width Multiplier Management**: Augmentation ratio is set to 1.0 in the second half of training
3. **Initialization Strategy**: Uses `nn.init.kaiming_uniform` instead of `fout` initialization
4. **BN Statistics Correction**: Post-training re-estimation using training subset

### Training Workflow

```mermaid
sequenceDiagram
    participant U as "User"
    participant TS as "Training Script"
    participant NA as "NetAug Process"
    participant BN as "BN Re-estimation"
    participant E as "Evaluation"
    
    U->>TS: Execute bash/imagenet script
    TS->>NA: Initialize with kaiming_uniform
    
    loop Each Epoch
        NA->>NA: Sort channels by L1 value
        NA->>NA: Apply width multiplier
        Note over NA: Second half: ratio = 1.0
    end
    
    NA->>BN: Re-estimate running mean/var
    BN->>E: Updated model statistics
    E->>U: Trained model ready
```

**Sources:** [netaug/README.md:66-74]()

## Transfer Learning Capabilities

### Transfer Learning Pipeline

NetAug-trained models can be fine-tuned for downstream tasks using transfer learning. The system provides scripts under `bash/transfer/` for this purpose.

```mermaid
graph TB
    subgraph "Pretrained Models"
        PM1["NetAug ImageNet Models"]
        PM2["MobileNetV2-Tiny + NetAug"]
        PM3["MCUNet + NetAug"]
        PM4["ProxylessNAS + NetAug"]
    end
    
    subgraph "Transfer Learning"
        TL1["bash/transfer/ scripts"]
        TL2["Fine-tuning Process"]
        TL3["Target Dataset Adaptation"]
    end
    
    subgraph "Deployment"
        DP1["Edge Device Models"]
        DP2["Task-Specific Performance"]
        DP3["Memory-Efficient Inference"]
    end
    
    PM1 --> PM2
    PM1 --> PM3
    PM1 --> PM4
    
    PM2 --> TL1
    PM3 --> TL1
    PM4 --> TL1
    
    TL1 --> TL2
    TL2 --> TL3
    TL3 --> DP1
    DP1 --> DP2
    DP1 --> DP3
```

**Sources:** [netaug/README.md:75-76]()

## Integration with TinyML Ecosystem

### Related Projects

NetAug is part of the broader TinyML ecosystem and works in conjunction with:

- **TinyTL**: Focuses on reducing activations for on-device learning
- **MCUNet**: Provides system-algorithm co-design for IoT deployment
- **Once for All**: Train-once-deploy-everywhere approach
- **ProxylessNAS**: Direct neural architecture search framework

### Research Foundation

```mermaid
graph TB
    subgraph "Foundational Work"
        FW1["ProxylessNAS (ICLR'19)"]
        FW2["Once for All (ICLR'20)"]
        FW3["MCUNet (NeurIPS'20)"]
    end
    
    subgraph "NetAug Contribution"
        NC1["Network Augmentation (ICLR'22)"]
        NC2["Tiny Network Training"]
        NC3["Edge Device Optimization"]
    end
    
    subgraph "TinyML Integration"
        TI1["TinyTL On-Device Learning"]
        TI2["MCUNet System Design"]
        TI3["Unified Edge AI Framework"]
    end
    
    FW1 --> NC1
    FW2 --> NC1
    FW3 --> NC1
    
    NC1 --> NC2
    NC2 --> NC3
    NC3 --> TI1
    NC3 --> TI2
    NC3 --> TI3
```

**Sources:** [netaug/README.md:78-86]()

---

# Page: Research Foundation and Related Work

# Research Foundation and Related Work

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page provides comprehensive context on the research ecosystem surrounding TinyML, documenting the foundational papers, related projects, and evolution of techniques from 2018-2020 that led to current implementations. It establishes the theoretical and practical foundations that enable efficient deep learning on edge devices.

For practical usage of the TinyML systems, see [Getting Started Guide](#5). For detailed documentation of individual sub-projects, see [TinyTL: On-Device Learning](#2) and [NetAug: Network Augmentation for Tiny Networks](#3).

## Research Timeline and Evolution

The TinyML project represents the culmination of several years of research in efficient deep learning, building systematically on foundational work in neural architecture search, model compression, and hardware-aware optimization.

```mermaid
timeline
    title "TinyML Research Evolution (2018-2020)"
    
    section 2018
        "ECCV'18 AMC" : "AutoML for Model Compression"
                       : "Automated compression techniques"
                       : "Mobile device optimization"
    
    section 2019
        "ICLR'19 ProxylessNAS" : "Direct Neural Architecture Search"
                                : "Target hardware optimization"
                                : "Differentiable NAS approach"
        
        "CVPR'19 HAQ" : "Hardware-Aware Quantization"
                       : "Automated quantization"
                       : "Hardware-specific optimization"
    
    section 2020
        "ICLR'20 Once for All" : "Train One Network"
                               : "Specialize for deployment"
                               : "Elastic neural networks"
        
        "NeurIPS'20 TinyML" : "MCUNet: System co-design"
                           : "TinyTL: On-device learning"
                           : "NetAug: Network augmentation"
```

**Sources:** [README.md:46-58]()

## Foundational Techniques and Their Influence

The current TinyML implementations directly leverage and extend several key research contributions, each addressing specific challenges in efficient deep learning deployment.

### Neural Architecture Search Foundation

```mermaid
graph TB
    subgraph "ProxylessNAS_Foundation"
        PNS1["ProxylessNAS"]
        PNS2["Direct search on target hardware"]
        PNS3["Differentiable architecture search"]
        PNS4["Hardware-specific optimization"]
    end
    
    subgraph "Once_for_All_Extension"
        OFA1["Once for All"]
        OFA2["Elastic neural networks"]
        OFA3["Progressive shrinking"]
        OFA4["Specialized deployment"]
    end
    
    subgraph "TinyML_Implementation"
        TML1["netaug/ codebase"]
        TML2["tinytl/ codebase"]
        TML3["MCUNet (external)"]
        TML4["Edge device deployment"]
    end
    
    PNS1 --> PNS2
    PNS2 --> PNS3
    PNS3 --> PNS4
    
    OFA1 --> OFA2
    OFA2 --> OFA3
    OFA3 --> OFA4
    
    PNS4 --> OFA1
    OFA4 --> TML1
    OFA4 --> TML2
    OFA4 --> TML3
    
    TML1 --> TML4
    TML2 --> TML4
    TML3 --> TML4
```

**Sources:** [README.md:50-52]()

### Model Compression and Quantization Pipeline

The progression from AMC to HAQ to current TinyML implementations demonstrates systematic advancement in automated model optimization techniques.

```mermaid
graph LR
    subgraph "AMC_ECCV18"
        AMC1["AMC framework"]
        AMC2["Reinforcement learning"]
        AMC3["Compression automation"]
        AMC4["Mobile device targets"]
    end
    
    subgraph "HAQ_CVPR19"
        HAQ1["HAQ framework"]
        HAQ2["Hardware-aware quantization"]
        HAQ3["Automated bit-width selection"]
        HAQ4["Precision optimization"]
    end
    
    subgraph "TinyML_Integration"
        TML1["NetAug training pipeline"]
        TML2["TinyTL memory optimization"]
        TML3["MCUNet system design"]
        TML4["Edge deployment"]
    end
    
    AMC1 --> AMC2
    AMC2 --> AMC3
    AMC3 --> AMC4
    
    HAQ1 --> HAQ2
    HAQ2 --> HAQ3
    HAQ3 --> HAQ4
    
    AMC4 --> HAQ1
    HAQ4 --> TML1
    HAQ4 --> TML2
    HAQ4 --> TML3
    
    TML1 --> TML4
    TML2 --> TML4
    TML3 --> TML4
```

**Sources:** [README.md:56-58]()

## Current Implementation Landscape

The TinyML umbrella project represents a systematic approach to addressing three critical challenges in edge AI deployment, each tackled by a specialized sub-project building on the foundational research.

### Problem-Solution Mapping

| Challenge | Foundational Research | TinyML Solution | Implementation |
|-----------|----------------------|-----------------|----------------|
| Tiny network training difficulties | ProxylessNAS, Once for All | NetAug | `netaug/` codebase |
| Memory constraints for on-device learning | AMC, HAQ | TinyTL | `tinytl/` codebase |
| System-level inference optimization | ProxylessNAS, Once for All | MCUNet | External repository |

### Technical Integration Architecture

```mermaid
graph TB
    subgraph "Research_Papers"
        RP1["AMC (ECCV'18)"]
        RP2["ProxylessNAS (ICLR'19)"]
        RP3["HAQ (CVPR'19)"]
        RP4["Once for All (ICLR'20)"]
    end
    
    subgraph "TinyML_Codebase"
        TC1["netaug/"]
        TC2["tinytl/"]
        TC3["MCUNet (external)"]
    end
    
    subgraph "Core_Components"
        CC1["Network augmentation training"]
        CC2["Memory-efficient transfer learning"]
        CC3["System-algorithm co-design"]
    end
    
    subgraph "Deployment_Targets"
        DT1["Edge devices"]
        DT2["IoT systems"]
        DT3["Mobile platforms"]
    end
    
    RP1 --> CC1
    RP2 --> CC1
    RP2 --> CC3
    RP3 --> CC2
    RP4 --> CC1
    RP4 --> CC2
    RP4 --> CC3
    
    CC1 --> TC1
    CC2 --> TC2
    CC3 --> TC3
    
    TC1 --> DT1
    TC2 --> DT2
    TC3 --> DT3
```

**Sources:** [README.md:15-21](), [README.md:46-58]()

## Technical Contributions and Innovations

### Memory Optimization Techniques

The TinyML project introduces several novel approaches to memory optimization that build directly on foundational research:

- **Activation Memory Reduction (TinyTL)**: Unlike traditional approaches that focus on parameter reduction, TinyTL reduces activation memory during training, enabling on-device learning with minimal memory footprint.

- **Network Augmentation (NetAug)**: Extends the Once for All training methodology to specifically address challenges in tiny neural network training through systematic network augmentation techniques.

- **System-Algorithm Co-design (MCUNet)**: Integrates insights from ProxylessNAS and hardware-aware optimization to achieve optimal deployment on microcontroller units.

### Publication Impact and Recognition

The TinyML project has achieved significant recognition in the research community:

```mermaid
graph TB
    subgraph "NeurIPS_2020"
        N1["MCUNet (Spotlight)"]
        N2["TinyTL (Main Conference)"]
        N3["NetAug (Implied)"]
    end
    
    subgraph "Industrial_Impact"
        I1["100K+ deployed devices"]
        I2["Industrial partnerships"]
        I3["Real-world applications"]
    end
    
    subgraph "Media_Coverage"
        M1["MIT News"]
        M2["WIRED"]
        M3["Morning Brew"]
        M4["Technical publications"]
    end
    
    N1 --> I1
    N2 --> I2
    N3 --> I3
    
    I1 --> M1
    I2 --> M2
    I3 --> M3
    I1 --> M4
```

**Sources:** [README.md:5-13](), [README.md:46-48]()

## Research Ecosystem Context

The TinyML project operates within a broader ecosystem of efficient deep learning research, representing a systematic approach to translating theoretical advances into practical edge AI solutions.

### Relationship to Broader Research Community

The foundational papers cited in the TinyML project have established key principles that extend beyond the specific implementations:

- **Automated Model Optimization**: AMC and HAQ demonstrated the feasibility of automated compression and quantization techniques
- **Hardware-Aware Design**: ProxylessNAS established the paradigm of direct optimization for target hardware
- **Elastic Neural Networks**: Once for All introduced the concept of training one network for multiple deployment scenarios

### Future Research Directions

Based on the foundational work and current implementations, several research directions emerge:

1. **Extended On-Device Learning**: Building on TinyTL's memory optimization techniques for more complex learning scenarios
2. **Advanced Network Augmentation**: Extending NetAug methodologies to additional neural network architectures
3. **Integrated System Design**: Further development of MCUNet-style co-design approaches for emerging edge hardware

**Sources:** [README.md:23-32](), [README.md:54-58]()

---

# Page: Getting Started Guide

# Getting Started Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [netaug/README.md](netaug/README.md)
- [tinytl/README.md](tinytl/README.md)

</details>



## Purpose and Scope

This guide provides step-by-step instructions for new users to set up and run experiments with the TinyML codebase. It covers system requirements, installation procedures, and basic usage workflows for both TinyTL and NetAug sub-projects.

For detailed information about TinyTL methodology and implementation, see [TinyTL: On-Device Learning](#2). For comprehensive NetAug documentation, see [NetAug: Network Augmentation for Tiny Networks](#3). For project background and research context, see [TinyML Project Overview](#1).

## System Requirements

The TinyML codebase has different requirements for its two main sub-projects:

### NetAug Requirements
| Component | Version |
|-----------|---------|
| Python | 3.8.5 |
| PyTorch | 1.8.2 |
| torchpack | Latest |
| torchprofile | Latest |

### TinyTL Requirements
| Component | Version |
|-----------|---------|
| Python | 3.6+ |
| PyTorch | 1.4.0+ |

**Sources:** [netaug/README.md:40-44](), [tinytl/README.md:42-44]()

## Installation and Setup

### Environment Setup Workflow

```mermaid
flowchart TD
    START["Start Installation"]
    PYTHON["Install Python 3.6+/3.8.5"]
    PYTORCH["Install PyTorch 1.4.0+/1.8.2"]
    DEPS["Install Dependencies"]
    
    subgraph "NetAug Dependencies"
        TORCHPACK["pip install torchpack"]
        TORCHPROFILE["pip install torchprofile"]
    end
    
    subgraph "Dataset Setup"
        IMAGENET["Download ImageNet dataset"]
        TINYTL_DATA["bash make_all_datasets.sh"]
    end
    
    VERIFY["Verify Installation"]
    READY["Ready for Experiments"]
    
    START --> PYTHON
    PYTHON --> PYTORCH
    PYTORCH --> DEPS
    DEPS --> TORCHPACK
    DEPS --> TORCHPROFILE
    TORCHPACK --> IMAGENET
    TORCHPROFILE --> TINYTL_DATA
    IMAGENET --> VERIFY
    TINYTL_DATA --> VERIFY
    VERIFY --> READY
```

**Sources:** [netaug/README.md:40-44](), [tinytl/README.md:42-44]()

### Dataset Preparation

For TinyTL experiments, run the dataset setup script:

```bash
cd tinytl/dataset_setup_scripts
bash make_all_datasets.sh
```

This script sets up all required datasets including Stanford Cars and other fine-grained visual classification datasets.

**Sources:** [tinytl/README.md:40]()

## Quick Start Workflows

### NetAug Workflow: Code Entity Mapping

```mermaid
flowchart TD
    subgraph "Entry Points"
        EVAL["eval.py"]
        TRAIN_SCRIPTS["bash/imagenet/*.sh"]
        TRANSFER_SCRIPTS["bash/transfer/*.sh"]
    end
    
    subgraph "Model Resources"
        PRETRAINED["Google Drive Models"]
        MOBILENET["MobileNetV2-Tiny + NetAug<br/>0.75M params"]
        MCUNET["MCUNet + NetAug<br/>0.74M params"]
        PROXYLESS["ProxylessNAS + NetAug<br/>1.8M params"]
    end
    
    subgraph "Execution Commands"
        TORCHPACK["torchpack dist-run -np 1"]
        EVAL_CMD["--dataset imagenet<br/>--data_path /dataset/imagenet/<br/>--image_size 160<br/>--model proxylessnas-0.35<br/>--init_from <path>"]
    end
    
    PRETRAINED --> MOBILENET
    PRETRAINED --> MCUNET
    PRETRAINED --> PROXYLESS
    
    MOBILENET --> EVAL
    MCUNET --> EVAL
    PROXYLESS --> EVAL
    
    EVAL --> TORCHPACK
    TORCHPACK --> EVAL_CMD
    
    TRAIN_SCRIPTS --> TORCHPACK
    TRANSFER_SCRIPTS --> TORCHPACK
```

**Sources:** [netaug/README.md:46-64](), [netaug/README.md:66-77]()

### TinyTL Workflow: Code Entity Mapping

```mermaid
flowchart TD
    subgraph "Setup Scripts"
        MAKE_ALL["make_all_datasets.sh"]
        DATASET_SETUP["dataset_setup_scripts/"]
    end
    
    subgraph "Training Entry Points"
        TINYTL_TRAIN["tinytl_fgvc_train.py"]
        EXP_SCRIPTS["exp_scripts/"]
    end
    
    subgraph "Dataset Components"
        STANFORD_CARS["Stanford Cars Dataset"]
        FGVC_DATASETS["Fine-Grained Visual Classification"]
    end
    
    subgraph "Training Configuration"
        BATCH_SIZE_1["Batch Size 1 Training"]
        ACTIVATION_OPT["Activation Memory Optimization"]
        TRANSFER_LEARNING["Transfer Learning Setup"]
    end
    
    MAKE_ALL --> STANFORD_CARS
    MAKE_ALL --> FGVC_DATASETS
    DATASET_SETUP --> MAKE_ALL
    
    STANFORD_CARS --> TINYTL_TRAIN
    FGVC_DATASETS --> TINYTL_TRAIN
    
    TINYTL_TRAIN --> BATCH_SIZE_1
    TINYTL_TRAIN --> ACTIVATION_OPT
    TINYTL_TRAIN --> TRANSFER_LEARNING
    
    EXP_SCRIPTS --> TINYTL_TRAIN
```

**Sources:** [tinytl/README.md:40](), [tinytl/README.md:46-48]()

## Basic Usage Patterns

### Running NetAug Model Evaluation

To evaluate a pretrained NetAug model:

```bash
torchpack dist-run -np 1 python eval.py \
    --dataset imagenet --data_path /dataset/imagenet/ \
    --image_size 160 \
    --model proxylessnas-0.35 \
    --init_from <path_of_pretrained_weight>
```

Available pretrained models:

| Model | Parameters | MACs | ImageNet Top1 | Download |
|-------|------------|------|---------------|----------|
| MobileNetV2-Tiny + NetAug | 0.75M | 23.5M | 53.3% | Google Drive |
| MCUNet + NetAug | 0.74M | 81.8M | 62.7% | Google Drive |
| ProxylessNAS + NetAug | 1.8M | 35.7M | 60.8% | Google Drive |

**Sources:** [netaug/README.md:55-64](), [netaug/README.md:46-53]()

### Running TinyTL Transfer Learning

After dataset setup, run TinyTL experiments:

```bash
cd tinytl
python tinytl_fgvc_train.py
```

Training scripts with specific configurations are available in the `exp_scripts/` directory.

**Sources:** [tinytl/README.md:46-48]()

### NetAug Training Considerations

When training with NetAug, several important implementation details must be considered:

1. **Initialization Strategy**: Use `nn.init.kaiming_uniform` instead of `fout` initialization due to large expand ratios
2. **Channel Sorting**: Channels are sorted by L1 value at each epoch start
3. **Width Multiplier**: Augmentation stops in the second half of training epochs
4. **Batch Normalization**: Running statistics are re-estimated after training using training subset

**Sources:** [netaug/README.md:69-73]()

## Common Commands Reference

### NetAug Commands
```bash
# Evaluate pretrained model
torchpack dist-run -np 1 python eval.py --dataset imagenet --data_path /path/to/data

# Train with NetAug (see bash/imagenet/ for specific scripts)
bash bash/imagenet/train_script.sh

# Transfer learning (see bash/transfer/ for specific scripts)
bash bash/transfer/transfer_script.sh
```

### TinyTL Commands
```bash
# Setup datasets
bash make_all_datasets.sh

# Run transfer learning experiments
python tinytl_fgvc_train.py

# Use experiment scripts
bash exp_scripts/experiment_script.sh
```

**Sources:** [netaug/README.md:55-77](), [tinytl/README.md:40](), [tinytl/README.md:46-48]()

## Next Steps

After completing this setup guide:

1. **For NetAug users**: Explore training scripts in `bash/imagenet/` and `bash/transfer/` directories
2. **For TinyTL users**: Review experiment scripts in `exp_scripts/` and customize for your datasets
3. **For both**: Download pretrained models from Google Drive links for immediate evaluation

For detailed methodology and implementation details, refer to the respective project documentation: [TinyTL: On-Device Learning](#2) and [NetAug: Network Augmentation for Tiny Networks](#3).

**Sources:** [netaug/README.md:66-77](), [tinytl/README.md:46-48]()