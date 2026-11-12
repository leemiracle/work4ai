<!-- source: DeepWiki mcp.deepwiki.com · repo PerforatedAI/PerforatedAI · page 3 Core Library Reference · fetched 2026-10-21 -->

# Core Library Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [perforatedai/__init__.py](perforatedai/__init__.py)
- [setup.py](setup.py)

</details>



This document provides technical documentation for the core PerforatedAI library components and their interactions. It covers the main modules, classes, and functions that implement the dendrite integration functionality.

For practical usage patterns and integration steps, see [Getting Started](#4.1). For detailed configuration options, see individual component sections [Architecture Overview](#3.1) through [Model Processors](#3.6).

## Core Library Structure

The PerforatedAI library consists of five main modules that work together to enable dendrite functionality in PyTorch neural networks. Each module has a specific responsibility in the dendrite integration pipeline.

### Core Module Architecture

```mermaid
graph TB
    subgraph "perforatedai Package"
        PBG["pb_globals<br/>(Configuration Management)"]
        PBU["pb_utils<br/>(Network Conversion)"] 
        PBM["pb_models<br/>(Custom Processors)"]
        PBL["pb_layer<br/>(Layer Wrappers)"]
        PBT["pb_neuron_layer_tracker<br/>(Training Orchestrator)"]
    end
    
    subgraph "Key Classes and Functions"
        INIT["initializePB()"]
        TRACKER["pbTracker"]
        CONVERT["convertNetwork()"]
        PB_NEURON["pb_neuron_layer"]
        PB_DENDRITE["pb_dendrite_layer"]
        TRACKED["tracked_neuron_layer"]
        GLOBALS_CONFIG["Global Configuration"]
        PROCESSORS["Custom Processors"]
    end
    
    PBU --> INIT
    PBU --> CONVERT
    PBT --> TRACKER
    PBL --> PB_NEURON
    PBL --> PB_DENDRITE
    PBL --> TRACKED
    PBG --> GLOBALS_CONFIG
    PBM --> PROCESSORS
    
    INIT --> CONVERT
    TRACKER --> PB_NEURON
    CONVERT --> PB_NEURON
    CONVERT --> TRACKED
    PB_NEURON --> PB_DENDRITE
```

**Sources:** Architecture diagrams, perforatedai/__init__.py

### Component Responsibilities

| Module | Primary Function | Key Components |
|--------|-----------------|----------------|
| `pb_utils` | Network conversion and initialization | `initializePB()`, `convertNetwork()` |
| `pb_neuron_layer_tracker` | Training lifecycle management | `pbTracker` |
| `pb_layer` | PyTorch module wrapping | `pb_neuron_layer`, `pb_dendrite_layer` |
| `pb_globals` | Configuration and settings | Global configuration variables |
| `pb_models` | Custom processing logic | Module-specific processors |

## System Integration Flow

The following diagram shows how user code integrates with the PerforatedAI library and the sequence of operations during model enhancement.

### Integration Sequence

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant PBU as "pb_utils"
    participant PBT as "pb_neuron_layer_tracker"  
    participant PBL as "pb_layer"
    participant Model as "Enhanced Model"
    
    User->>PBU: "initializePB(model, args)"
    PBU->>PBU: "convertNetwork(model)"
    PBU->>PBL: "Create pb_neuron_layer wrappers"
    PBL->>Model: "Wrap original modules"
    PBU->>PBT: "Initialize pbTracker"
    PBU->>User: "Return enhanced model, tracker"
    
    loop "Training Loop"
        User->>Model: "Forward/backward pass"
        User->>PBT: "addValidationScore(score)"
        PBT->>PBT: "Evaluate performance"
        
        alt "Restructuring Needed"
            PBT->>PBL: "Add dendrites to layers"
            PBL->>Model: "Update layer architecture"
            PBT->>User: "Return restructured=True"
        else "Continue Training"
            PBT->>User: "Return restructured=False"
        end
    end
    
    User->>PBT: "saveGraphs(), finalize()"
```

**Sources:** Architecture diagrams, system flow documentation

## Module Dependencies

The core library modules have specific dependency relationships that determine initialization order and functionality availability.

### Dependency Graph

```mermaid
graph TD
    subgraph "User Interface Layer"
        USER_CODE["User Training Code"]
        PYTORCH_MODEL["PyTorch Model"]
    end
    
    subgraph "Core Library Dependencies"
        PBG_CONFIG["pb_globals Configuration"]
        PBU_INIT["pb_utils.initializePB()"]
        PBU_CONVERT["pb_utils.convertNetwork()"] 
        PBM_PROCESSORS["pb_models Processors"]
        PBL_NEURON["pb_layer.pb_neuron_layer"]
        PBL_DENDRITE["pb_layer.pb_dendrite_layer"]
        PBL_TRACKED["pb_layer.tracked_neuron_layer"]
        PBT_TRACKER["pb_neuron_layer_tracker.pbTracker"]
    end
    
    subgraph "Runtime Components"
        ENHANCED_MODEL["Enhanced Model"]
        TRAINING_ORCHESTRATOR["Training Orchestrator"]
    end
    
    USER_CODE --> PBU_INIT
    PYTORCH_MODEL --> PBU_INIT
    
    PBG_CONFIG --> PBU_CONVERT
    PBG_CONFIG --> PBT_TRACKER
    PBU_INIT --> PBU_CONVERT
    PBU_CONVERT --> PBL_NEURON
    PBU_CONVERT --> PBL_TRACKED
    PBM_PROCESSORS --> PBL_NEURON
    PBL_NEURON --> PBL_DENDRITE
    
    PBU_INIT --> PBT_TRACKER
    PBL_NEURON --> ENHANCED_MODEL
    PBL_DENDRITE --> ENHANCED_MODEL
    PBL_TRACKED --> ENHANCED_MODEL
    PBT_TRACKER --> TRAINING_ORCHESTRATOR
    
    ENHANCED_MODEL --> USER_CODE
    TRAINING_ORCHESTRATOR --> USER_CODE
```

**Sources:** Architecture diagrams, module interaction patterns

## Training Mode Management

The library implements a sophisticated training mode switching system that alternates between optimizing neuron parameters and dendrite parameters based on validation performance.

### Mode Switching Logic

```mermaid
stateDiagram-v2
    [*] --> NeuronTraining: "Initial State"
    
    NeuronTraining --> ValidationCheck: "addValidationScore()"
    ValidationCheck --> NeuronTraining: "Performance Improving"
    ValidationCheck --> DendriteAddition: "Performance Plateaued"
    ValidationCheck --> TrainingComplete: "Convergence Criteria Met"
    
    DendriteAddition --> DendriteTraining: "Add Dendrites"
    DendriteTraining --> ValidationCheck: "Continue Training"
    
    TrainingComplete --> [*]
    
    note right of NeuronTraining
        doingHistory = False
        doingFixed = False
        Optimize main parameters
    end note
    
    note right of DendriteTraining
        doingHistory = True
        doingFixed = True  
        Optimize dendrite parameters
    end note
```

**Sources:** Architecture diagrams, training orchestration flow

## Key Integration Points

The library provides several key integration points where user code interacts with the PerforatedAI system:

### Primary Entry Points

| Function/Class | Module | Purpose |
|----------------|---------|---------|
| `initializePB()` | `pb_utils` | Main initialization function for model conversion |
| `pbTracker` | `pb_neuron_layer_tracker` | Central training orchestrator instance |
| `convertNetwork()` | `pb_utils` | Core network conversion function |
| `setupOptimizer()` | `pb_neuron_layer_tracker` | Optimizer configuration for dendrite training |
| `addValidationScore()` | `pb_neuron_layer_tracker` | Performance tracking and mode switching |

### Configuration Control Points

The system exposes several configuration mechanisms:

- **Global Settings**: Through `pb_globals` module configuration
- **Processing Rules**: Via `pb_models` custom processors  
- **Layer Wrapping**: Through `pb_layer` wrapper classes
- **Training Parameters**: Via `pbTracker` orchestrator settings

**Sources:** setup.py, architecture diagrams, integration flow documentation

## Package Structure

The PerforatedAI library is distributed as a single Python package with the following dependencies and structure:

### Dependencies

From [setup.py:18-26]():
- `torch` - PyTorch framework integration
- `torchvision` - Vision model support
- `matplotlib` - Visualization and graphing
- `pandas` - Data analysis and CSV output
- `rsa` - Cryptographic functions
- `pyyaml` - Configuration file support
- `safetensors` - Secure tensor serialization

### Package Information

- **Package Name**: `perforatedai` 
- **Version**: 1.0.9 (from [setup.py:7]())
- **Python Requirements**: >=3.6 (from [setup.py:17]())
- **License**: Apache 2.0

**Sources:** setup.py, perforatedai/__init__.py

---

