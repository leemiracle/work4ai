<!-- source: DeepWiki mcp.deepwiki.com · repo PerforatedAI/PerforatedAI · page 5 Examples and Tutorials · fetched 2026-10-21 -->

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mnist_perforatedai.py](mnist_perforatedai.py)

</details>



This page provides an overview of practical examples demonstrating PerforatedAI integration patterns with different neural network architectures. The examples show how to modify existing PyTorch training workflows to incorporate automatic dendrite addition and management.

For detailed implementation documentation of the core library components, see [Core Library Reference](#3). For step-by-step integration guidance, see [User Guide](#4).

## Purpose and Scope

The examples and tutorials demonstrate three key integration patterns:

- **Basic Integration**: Minimal changes to existing PyTorch code using `PBU.initializePB()` and `PBG.pbTracker`
- **Architecture-Specific**: Adaptations for BERT, CNN, UNet, and ResNet models with custom processing requirements  
- **Advanced Customization**: Custom processor implementations for complex module types

Each example shows the complete workflow from model conversion through training orchestration and results analysis.

## Available Examples Overview

The repository includes several categories of examples that demonstrate different aspects of PerforatedAI integration:

```mermaid
graph TD
    subgraph "Example Categories"
        MNIST["mnist_perforatedai.py<br/>Basic Integration Demo"]
        ARCH["Architecture Examples<br/>BERT, CNN, UNet, ResNet"]
        PROC["Processor Examples<br/>Custom Module Handlers"]
    end
    
    subgraph "Core Integration Points"
        INIT["PBU.initializePB()<br/>Model Conversion"]
        TRACK["PBG.pbTracker<br/>Training Orchestration"]
        CUSTOM["Custom Processors<br/>Complex Module Support"]
    end
    
    subgraph "Training Patterns"
        BASIC["Basic Training Loop<br/>Minimal Modifications"]
        ADVANCED["Advanced Training<br/>Custom Scoring"]
        MIXED["Mixed Training<br/>Multiple Objectives"]
    end
    
    MNIST --> INIT
    MNIST --> TRACK
    MNIST --> BASIC
    
    ARCH --> INIT
    ARCH --> CUSTOM
    ARCH --> ADVANCED
    
    PROC --> CUSTOM
    PROC --> MIXED
    
    style MNIST fill:#f9f9f9
    style TRACK fill:#f0f0f0
```

Sources: [mnist_perforatedai.py:1-208]()

## Key Integration Patterns

The examples demonstrate several common integration patterns that map PyTorch training workflows to PerforatedAI components:

### Model Initialization Pattern

```mermaid
flowchart LR
    subgraph "User Model Definition"
        PYTORCH_MODEL["class Net(nn.Module)<br/>Standard PyTorch Model"]
        MODEL_INSTANCE["model = Net().to(device)<br/>Model Instantiation"]
    end
    
    subgraph "PerforatedAI Conversion"
        PB_INIT["PBU.initializePB(model)<br/>Convert to PB Model"]
        TRACKER_SETUP["PBG.pbTracker.setupOptimizer()<br/>Configure Training"]
    end
    
    subgraph "Enhanced Model"
        PB_MODEL["Enhanced Model<br/>with pb_neuron_layer"]
        OPTIMIZER["Managed Optimizer<br/>Auto-Reset Capable"]
    end
    
    PYTORCH_MODEL --> MODEL_INSTANCE
    MODEL_INSTANCE --> PB_INIT
    PB_INIT --> PB_MODEL
    PB_MODEL --> TRACKER_SETUP
    TRACKER_SETUP --> OPTIMIZER
```

Sources: [mnist_perforatedai.py:14-24](), [mnist_perforatedai.py:185-194]()

### Training Loop Integration Pattern

The examples show how minimal modifications to existing training loops enable automatic dendrite management:

| Training Phase | Standard PyTorch | PerforatedAI Integration |
|---------------|------------------|-------------------------|
| Model Forward | `output = model(data)` | `output = model(data)` (unchanged) |
| Loss Computation | `loss = criterion(output, target)` | `loss = criterion(output, target)` (unchanged) |
| Backward Pass | `loss.backward()` | `loss.backward()` (unchanged) |
| Optimizer Step | `optimizer.step()` | `optimizer.step()` (unchanged) |
| Validation | Manual accuracy tracking | `PBG.pbTracker.addValidationScore()` |
| Model Updates | Manual architecture changes | Automatic dendrite addition |
| Optimizer Reset | Manual when needed | Automatic when restructured |

Sources: [mnist_perforatedai.py:41-93]()

## Training Orchestration Flow

The following diagram shows how the training orchestration system manages the lifecycle of dendrite addition and training mode switching:

```mermaid
sequenceDiagram
    participant USER as "User Training Loop"
    participant TRACKER as "PBG.pbTracker"
    participant MODEL as "Enhanced Model"
    participant OPT as "Optimizer Management"
    
    USER->>TRACKER: "addValidationScore(score, model)"
    TRACKER->>TRACKER: "Evaluate improvement history"
    
    alt "Performance Plateau Detected"
        TRACKER->>MODEL: "Add dendrites to layers"
        TRACKER->>TRACKER: "Mark as restructured=True"
        TRACKER->>OPT: "Prepare optimizer reset"
        TRACKER->>USER: "Return (model, True, False)"
        USER->>TRACKER: "setupOptimizer(model, args)"
        TRACKER->>USER: "Return new optimizer"
    else "Continue Training"
        TRACKER->>USER: "Return (model, False, False)"
    end
    
    opt "Training Complete"
        TRACKER->>USER: "Return (model, False, True)"
        USER->>USER: "Exit training loop"
    end
```

Sources: [mnist_perforatedai.py:84-93]()

## Code Entity Mapping

The examples demonstrate how high-level concepts map to specific code entities:

```mermaid
graph TB
    subgraph "User Interface Layer"
        IMPORT_PBG["from perforatedai import pb_globals as PBG"]
        IMPORT_PBU["from perforatedai import pb_utils as PBU"] 
        IMPORT_PBM["from perforatedai import pb_models as PBM"]
    end
    
    subgraph "Core Functions Called"
        INIT_FUNC["PBU.initializePB(model)"]
        TRACK_VALIDATE["PBG.pbTracker.addValidationScore()"]
        TRACK_EXTRA["PBG.pbTracker.addExtraScore()"]
        TRACK_OPT["PBG.pbTracker.setupOptimizer()"]
    end
    
    subgraph "Configuration Points"
        TESTING_CAP["PBG.testingDendriteCapacity = False"]
        SET_OPT["PBG.pbTracker.setOptimizer()"]
        SET_SCHED["PBG.pbTracker.setScheduler()"]
    end
    
    subgraph "Training Loop Integration"
        TRAIN_FUNC["train(args, model, device, ...)"]
        TEST_FUNC["test(model, device, ...)"]
        RESTRUCTURE_CHECK["if(restructured): reset optimizer"]
    end
    
    IMPORT_PBG --> TRACK_VALIDATE
    IMPORT_PBG --> TRACK_EXTRA
    IMPORT_PBG --> TESTING_CAP
    
    IMPORT_PBU --> INIT_FUNC
    
    INIT_FUNC --> TRAIN_FUNC
    TRACK_VALIDATE --> RESTRUCTURE_CHECK
    TRACK_OPT --> RESTRUCTURE_CHECK
```

Sources: [mnist_perforatedai.py:10-12](), [mnist_perforatedai.py:62](), [mnist_perforatedai.py:85-92](), [mnist_perforatedai.py:183](), [mnist_perforatedai.py:187](), [mnist_perforatedai.py:190-194]()

## Example Categories

### Basic Integration Examples
- **MNIST Classification**: Complete working example with CNN architecture showing minimal integration steps
- **Training Loop Patterns**: Standard PyTorch training loops with PerforatedAI integration points
- **Optimizer Management**: Automatic optimizer reset handling when model structure changes

### Architecture-Specific Examples  
- **BERT Integration**: Natural language processing models with attention mechanisms
- **CNN Applications**: Computer vision models with convolutional layers
- **UNet Segmentation**: Medical imaging and segmentation architectures
- **ResNet Variants**: Residual networks with skip connections

### Advanced Customization Examples
- **Custom Processors**: Handling specialized module types like LSTM cells
- **Mixed Training Strategies**: Combining gradient descent with correlation learning
- **PEFT Integration**: Parameter-efficient fine-tuning with LoRA adapters

## Detailed Tutorials

For comprehensive walkthroughs of specific examples:

- **Step-by-step MNIST integration**: See [MNIST Tutorial](#5.1)
- **Architecture-specific adaptations**: See [Architecture Examples](#5.2) 
- **Custom processor development**: See [Processor Examples](#5.3)

For installation and setup requirements, see [Installation and Setup](#6).

Sources: [mnist_perforatedai.py:1-208]()

---

