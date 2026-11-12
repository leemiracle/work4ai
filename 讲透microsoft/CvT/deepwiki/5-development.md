<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CvT · page 5 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

</details>



This document provides essential information for developers contributing to the CvT (Convolutional vision Transformers) codebase. It covers the development workflow, code organization, and guidelines for contributing to the project.

For detailed code structure documentation, see [Code Structure](#5.1). For specific contributing guidelines and governance, see [Contributing Guidelines](#5.2). For environment setup details, see [Development Environment](#5.3).

## Development Workflow Overview

The CvT repository follows a research-oriented development model where the primary workflow involves configuration-driven experimentation. Understanding this workflow is essential for effective contribution to the project.

```mermaid
flowchart TD
    start[["Developer Start"]]
    
    subgraph "Development Tasks"
        feature["Feature Development"]
        experiment["Experiment Design"]
        debug["Debugging & Testing"]
        contribute["Contribution Submission"]
    end
    
    subgraph "Key Entry Points"
        runsh["run.sh<br/>Main execution entry"]
        trainpy["tools/train.py<br/>Training orchestration"]
        configs["experiments/<br/>YAML configurations"]
    end
    
    subgraph "Core Development Areas"
        libmodels["lib/models/<br/>Architecture development"]
        libcore["lib/core/<br/>Training logic"]
        libdataset["lib/dataset/<br/>Data pipeline"]
        libconfig["lib/config/<br/>Configuration system"]
    end
    
    subgraph "Testing & Validation"
        localtest["Local Testing<br/>Single GPU/CPU"]
        distributed["Distributed Testing<br/>Multi-GPU"]
        validation["Result Validation<br/>Metrics & Checkpoints"]
    end
    
    start --> feature
    start --> experiment
    start --> debug
    
    feature --> libmodels
    feature --> libcore
    feature --> libdataset
    feature --> libconfig
    
    experiment --> configs
    experiment --> runsh
    
    debug --> trainpy
    debug --> localtest
    
    libmodels --> localtest
    libcore --> localtest
    libdataset --> localtest
    libconfig --> localtest
    
    localtest --> distributed
    distributed --> validation
    validation --> contribute
    
    runsh --> trainpy
    trainpy --> libcore
    configs --> libconfig
```

*Sources: run.sh, tools/train.py, lib/ directory structure*

## Code Organization and Key Components

The codebase is organized into distinct modules with clear separation of concerns. Understanding this organization is crucial for making targeted contributions.

```mermaid
graph TB
    subgraph "Entry Points & Scripts"
        runsh["run.sh<br/>Main execution script<br/>Handles CLI arguments"]
        trainpy["tools/train.py<br/>Training controller<br/>Orchestrates training pipeline"]
    end
    
    subgraph "Core Library (lib/)"
        subgraph "lib/config"
            configinit["__init__.py<br/>build_config function"]
            configdefault["default.py<br/>Default configuration schema"]
        end
        
        subgraph "lib/core" 
            corefunc["function.py<br/>train_one_epoch, test functions"]
            coreloss["loss.py<br/>Loss function implementations"]
            coreeval["evaluate.py<br/>Accuracy evaluation"]
        end
        
        subgraph "lib/models"
            modelsinit["__init__.py<br/>build_model factory"]
            modelsreg["registry.py<br/>Model registration system"]
            modelscvt["cls_cvt.py<br/>CvT architecture classes"]
        end
        
        subgraph "lib/dataset"
            datasetinit["__init__.py<br/>build_dataloader factory"]
            datasetbuild["build.py<br/>Dataset construction"]
            datasettrans["transformas/<br/>Data augmentation pipeline"]
        end
        
        subgraph "lib/optim"
            optiminit["__init__.py<br/>build_optimizer factory"]
        end
    end
    
    subgraph "Configuration Files"
        expconfigs["experiments/<br/>Model variant YAML files"]
    end
    
    subgraph "Development Infrastructure"
        gitignore[".gitignore<br/>Build artifact exclusions"]
        conduct["CODE_OF_CONDUCT.md<br/>Microsoft OSS guidelines"]
    end
    
    runsh --> trainpy
    trainpy --> configinit
    trainpy --> corefunc
    trainpy --> modelsinit
    trainpy --> datasetinit
    trainpy --> optiminit
    
    configinit --> configdefault
    configinit --> expconfigs
    
    corefunc --> coreloss
    corefunc --> coreeval
    corefunc --> modelsinit
    corefunc --> datasetinit
    
    modelsinit --> modelsreg
    modelsinit --> modelscvt
    
    datasetinit --> datasetbuild
    datasetbuild --> datasettrans
```

*Sources: lib/ directory structure, tools/train.py, run.sh, experiments/ directory*

### Key Development Areas

| Component | Purpose | Primary Files | Key Functions/Classes |
|-----------|---------|---------------|----------------------|
| **Model Architecture** | CvT model definitions and variants | `lib/models/cls_cvt.py`, `lib/models/registry.py` | `CvT`, `ConvolutionalVisionTransformer` |
| **Training Engine** | Core training and evaluation logic | `lib/core/function.py`, `lib/core/loss.py` | `train_one_epoch`, `test`, `LabelSmoothingCrossEntropy` |
| **Data Pipeline** | Dataset loading and augmentation | `lib/dataset/build.py`, `lib/dataset/transformas/` | `build_dataloader`, transformation classes |
| **Configuration** | Parameter management and validation | `lib/config/default.py`, `lib/config/__init__.py` | `build_config`, configuration schemas |
| **Optimization** | Optimizer and scheduler construction | `lib/optim/__init__.py` | `build_optimizer` factory function |

## Development Guidelines and Practices

### Code Contribution Standards

The project follows Microsoft's open source guidelines as defined in the code of conduct. Key principles include:

- **Respectful Communication**: All interactions follow the Microsoft Open Source Code of Conduct
- **Modular Design**: New features should integrate with the existing factory pattern architecture
- **Configuration-Driven**: New functionality should be configurable through YAML files
- **Testing**: Changes should be validated through the training pipeline

*Sources: [CODE_OF_CONDUCT.md:1-10]()*

### File and Directory Conventions

The project uses a structured approach to file organization:

```mermaid
graph LR
    subgraph "File Type Conventions"
        source["Source Files<br/>.py modules"]
        configs["Configuration Files<br/>.yaml experiments"]
        scripts["Execution Scripts<br/>.sh entry points"]
        docs["Documentation<br/>.md governance"]
    end
    
    subgraph "Ignored Artifacts"
        build["Build Results<br/>Debug/, Release/"]
        temp["Temporary Files<br/>*.tmp, *.log"]
        cache["Cache Files<br/>__pycache__/, *.pyc"]
        output["Output Artifacts<br/>checkpoints, logs"]
    end
    
    source --> build
    configs --> output
    scripts --> temp
    
    subgraph "Version Control"
        gitignore[".gitignore<br/>Exclusion patterns"]
    end
    
    build --> gitignore
    temp --> gitignore
    cache --> gitignore
    output --> gitignore
```

*Sources: [.gitignore:1-351]()*

### Factory Pattern Implementation

The codebase extensively uses factory patterns for component creation. When adding new functionality, follow these patterns:

| Factory Function | Location | Purpose | Extension Pattern |
|------------------|----------|---------|-------------------|
| `build_model` | `lib/models/__init__.py` | Model construction | Register in `lib/models/registry.py` |
| `build_config` | `lib/config/__init__.py` | Configuration loading | Extend `lib/config/default.py` schema |
| `build_dataloader` | `lib/dataset/__init__.py` | Dataset construction | Add to `lib/dataset/build.py` |
| `build_optimizer` | `lib/optim/__init__.py` | Optimizer creation | Implement in optim module |

### Testing and Validation Workflow

Development changes should be validated through the standard training pipeline:

1. **Configuration Testing**: Validate new parameters through YAML configuration files
2. **Local Execution**: Test using `run.sh` with minimal configurations
3. **Training Validation**: Ensure `tools/train.py` executes without errors
4. **Integration Testing**: Verify integration with existing `lib/core/function.py` workflows

## Development Environment Considerations

### Build Artifact Management

The project generates various artifacts during development and training. The `.gitignore` configuration excludes standard development artifacts:

- **Python Artifacts**: `__pycache__/`, `*.pyc` files are excluded
- **Build Results**: Debug and Release directories are ignored  
- **Log Files**: Training logs and temporary files are excluded
- **IDE Files**: Visual Studio and development environment files are ignored

*Sources: [.gitignore:306-307](), [.gitignore:88](), [.gitignore:20-32]()*

### Integration Points

Key integration points for development work include:

- **Entry Point Integration**: New functionality should integrate through `run.sh` and `tools/train.py`
- **Configuration Integration**: Parameters should be configurable through the YAML system
- **Model Registry**: New models must be registered in the model registry system
- **Data Pipeline**: Custom datasets should integrate through the dataloader factory

For detailed environment setup procedures, see [Development Environment](#5.3).

*Sources: run.sh, tools/train.py, lib/models/registry.py, lib/dataset/__init__.py*

---

