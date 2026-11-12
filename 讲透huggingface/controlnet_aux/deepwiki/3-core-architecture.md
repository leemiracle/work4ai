<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [setup.py](setup.py)
- [src/controlnet_aux/__init__.py](src/controlnet_aux/__init__.py)
- [src/controlnet_aux/processor.py](src/controlnet_aux/processor.py)
- [src/controlnet_aux/tests/test_processor_pytest.py](src/controlnet_aux/tests/test_processor_pytest.py)

</details>



This document explains the fundamental design patterns and architectural components that form the foundation of the controlnet_aux library. It covers the dual API design, model registry system, and loading strategies that enable unified access to diverse computer vision preprocessing models.

For specific details about the unified interface, see [Processor Interface](#3.1). For package organization details, see [Package Structure](#3.2). For implementation details of individual detector categories, see [Detector Categories](#4).

## System Overview

The controlnet_aux library implements a **two-tier architecture** that provides both simplified and advanced access patterns to a collection of computer vision preprocessing models. The system is built around a central registry that maps string identifiers to detector classes and manages their instantiation patterns.

**Core Architecture Components**

```mermaid
graph TB
    subgraph "Public API Layer"
        PROC["Processor Class"]
        DIRECT["Direct Detector Imports"]
    end
    
    subgraph "Registry System"
        MODELS["MODELS Dictionary<br/>19 detector mappings"]
        MODEL_PARAMS["MODEL_PARAMS Dictionary<br/>Default parameters"]
    end
    
    subgraph "Detector Classes"
        CHECKPOINT["Checkpoint-based Detectors<br/>HEDdetector, MidasDetector, etc."]
        INSTANT["Instantiate Detectors<br/>CannyDetector, ContentShuffleDetector"]
    end
    
    subgraph "Infrastructure"
        HF_HUB["Hugging Face Hub<br/>Model Storage"]
        TORCH["PyTorch Framework"]
    end
    
    PROC --> MODELS
    PROC --> MODEL_PARAMS
    DIRECT --> CHECKPOINT
    DIRECT --> INSTANT
    MODELS --> CHECKPOINT
    MODELS --> INSTANT
    CHECKPOINT --> HF_HUB
    CHECKPOINT --> TORCH
    INSTANT --> TORCH
```

Sources: [src/controlnet_aux/processor.py:1-149](), [src/controlnet_aux/__init__.py:1-21](), [setup.py:70-213]()

## Dual API Design Pattern

The architecture provides two distinct usage patterns that cater to different user needs and complexity requirements.

**API Access Patterns**

```mermaid
graph LR
    subgraph "Usage Patterns"
        SIMPLE["Simple Interface<br/>String-based selection"]
        ADVANCED["Advanced Interface<br/>Direct instantiation"]
    end
    
    subgraph "Implementation"
        PROC_CLASS["Processor.__init__<br/>processor_id parameter"]
        LOAD_METHOD["Processor.load_processor<br/>Registry lookup"]
        DIRECT_IMPORT["from controlnet_aux import<br/>HEDdetector, MidasDetector..."]
        FROM_PRETRAINED["HEDdetector.from_pretrained<br/>lllyasviel/Annotators"]
    end
    
    subgraph "Registry Lookup"
        MODELS_DICT["MODELS[processor_id]<br/>{'class': HEDdetector, 'checkpoint': True}"]
        PARAMS_DICT["MODEL_PARAMS[processor_id]<br/>{'scribble': True, 'safe': False}"]
    end
    
    SIMPLE --> PROC_CLASS
    PROC_CLASS --> LOAD_METHOD
    LOAD_METHOD --> MODELS_DICT
    LOAD_METHOD --> PARAMS_DICT
    
    ADVANCED --> DIRECT_IMPORT
    DIRECT_IMPORT --> FROM_PRETRAINED
```

Sources: [src/controlnet_aux/processor.py:84-124](), [src/controlnet_aux/__init__.py:3-20](), [README.md:35-61]()

## Model Loading Strategies

The system implements two distinct loading patterns based on the computational requirements and model architecture of each detector.

| Loading Pattern | Detector Examples | Registry Flag | Instantiation Method |
|----------------|-------------------|---------------|---------------------|
| **Checkpoint-based** | `HEDdetector`, `MidasDetector`, `OpenposeDetector` | `'checkpoint': True` | `DetectorClass.from_pretrained()` |
| **Direct Instantiation** | `CannyDetector`, `ContentShuffleDetector`, `MediapipeFaceDetector` | `'checkpoint': False` | `DetectorClass()` |

**Model Loading Decision Flow**

```mermaid
graph TD
    START["Processor.load_processor()"]
    CHECK_FLAG["MODELS[processor_id]['checkpoint']"]
    CHECKPOINT_PATH["processor.from_pretrained<br/>('lllyasviel/Annotators')"]
    DIRECT_PATH["processor()"]
    
    START --> CHECK_FLAG
    CHECK_FLAG -->|"True"| CHECKPOINT_PATH
    CHECK_FLAG -->|"False"| DIRECT_PATH
```

Sources: [src/controlnet_aux/processor.py:108-124](), [src/controlnet_aux/processor.py:20-49]()

## Registry System Architecture

The registry system centralizes detector metadata and configuration through two primary dictionaries that map string identifiers to classes and parameters.

**Registry Structure**

```mermaid
graph TB
    subgraph "Registry Components"
        MODELS_REG["MODELS Dictionary<br/>20 entries mapping processor_id to metadata"]
        PARAMS_REG["MODEL_PARAMS Dictionary<br/>Parameter defaults for each processor_id"]
    end
    
    subgraph "Registry Entries"
        HED_ENTRY["'scribble_hed': {<br/>'class': HEDdetector,<br/>'checkpoint': True}"]
        CANNY_ENTRY["'canny': {<br/>'class': CannyDetector,<br/>'checkpoint': False}"]
        HED_PARAMS["'scribble_hed': {<br/>'scribble': True}"]
        CANNY_PARAMS["'canny': {}"]
    end
    
    subgraph "Detector Classes"
        HED_CLASS["HEDdetector"]
        CANNY_CLASS["CannyDetector"]
    end
    
    MODELS_REG --> HED_ENTRY
    MODELS_REG --> CANNY_ENTRY
    PARAMS_REG --> HED_PARAMS
    PARAMS_REG --> CANNY_PARAMS
    HED_ENTRY --> HED_CLASS
    CANNY_ENTRY --> CANNY_CLASS
```

The `MODELS` dictionary contains 20 processor configurations that map string identifiers to detector classes and loading metadata. Key entries include multiple variants for edge detection (`scribble_hed`, `softedge_hed`), pose estimation (`openpose`, `openpose_full`, `dwpose`), and depth estimation (`depth_midas`, `depth_zoe`).

Sources: [src/controlnet_aux/processor.py:20-49](), [src/controlnet_aux/processor.py:52-79]()

## Package Structure Design

The package follows a flat module structure where each detector is implemented in its own module and exposed through centralized imports.

**Package Organization**

```mermaid
graph TB
    subgraph "Package Root"
        INIT["__init__.py<br/>Version and exports"]
        PROCESSOR["processor.py<br/>Unified interface"]
    end
    
    subgraph "Detector Modules"
        HED_MOD["hed.py<br/>HEDdetector"]
        MIDAS_MOD["midas.py<br/>MidasDetector"]
        CANNY_MOD["canny.py<br/>CannyDetector"]
        POSE_MOD["open_pose.py<br/>OpenposeDetector"]
        DWPOSE_MOD["dwpose.py<br/>DWposeDetector"]
        OTHER_MODS["... 15 other detector modules"]
    end
    
    subgraph "Infrastructure"
        SETUP["setup.py<br/>Package configuration"]
        DEPS["Dependencies<br/>torch, opencv, huggingface_hub, etc."]
    end
    
    INIT --> HED_MOD
    INIT --> MIDAS_MOD
    INIT --> CANNY_MOD
    INIT --> POSE_MOD
    INIT --> DWPOSE_MOD
    INIT --> OTHER_MODS
    
    PROCESSOR --> HED_MOD
    PROCESSOR --> MIDAS_MOD
    PROCESSOR --> CANNY_MOD
    
    SETUP --> DEPS
```

The `__init__.py` file serves as the central export point, importing all 20 detector classes and making them available for direct import. This design enables both the unified `Processor` interface and direct detector access patterns.

Sources: [src/controlnet_aux/__init__.py:1-21](), [setup.py:166-179]()

## Error Handling and Validation

The architecture includes validation mechanisms to ensure robust operation across different usage patterns.

The `Processor` class validates processor IDs against the registry and provides clear error messages when invalid identifiers are used. The validation logic checks against the `MODELS.keys()` and raises `ValueError` with the complete list of valid options.

```python
# Validation implementation from processor.py lines 96-97
if processor_id not in MODELS:
    raise ValueError(f"{processor_id} is not a valid processor id. Please make sure to choose one of {', '.join(MODELS.keys())}")
```

Sources: [src/controlnet_aux/processor.py:96-97](), [src/controlnet_aux/processor.py:81-82]()

---

