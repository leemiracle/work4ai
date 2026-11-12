<!-- source: DeepWiki mcp.deepwiki.com · repo yoshitomo-matsubara/torchdistill · page 2 Core Architecture · fetched 2026-10-21 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [configs/README.md](configs/README.md)
- [demo/extract_intermediate_representations.ipynb](demo/extract_intermediate_representations.ipynb)
- [torchdistill/core/distillation.py](torchdistill/core/distillation.py)
- [torchdistill/core/forward_hook.py](torchdistill/core/forward_hook.py)
- [torchdistill/core/training.py](torchdistill/core/training.py)
- [torchdistill/core/util.py](torchdistill/core/util.py)
- [torchdistill/models/wrapper.py](torchdistill/models/wrapper.py)

</details>



This document explains the core architectural components and design patterns that form the foundation of torchdistill. It covers the configuration-driven system, training framework, component registry, and forward hook management that enable modular, declarative knowledge distillation experiments.

For specific component implementations (models, datasets, losses, optimizers), see [Components](#3). For practical usage examples, see [Examples and Usage](#4).

## Architectural Overview

torchdistill follows a configuration-driven architecture where YAML files declaratively define entire experiments. The framework consists of four main architectural pillars that work together to enable flexible knowledge distillation workflows.

### Core Architecture Diagram

```mermaid
graph TD
    subgraph "Configuration Layer"
        YAML["YAML Configuration Files"]
        IMPORT_CALL["!import_call Constructor"]
        YAML_UTIL["yaml_util.load_yaml_file()"]
    end
    
    subgraph "Execution Engine"
        DISTILL_BOX["DistillationBox"]
        TRAIN_BOX["TrainingBox"]
        MULTI_DISTILL["MultiStagesDistillationBox"]
        MULTI_TRAIN["MultiStagesTrainingBox"]
    end
    
    subgraph "Component Registry"
        MODEL_REG["MODEL_DICT Registry"]
        DATASET_REG["DATASET_DICT Registry"]
        LOSS_REG["LOSS_DICT Registry"]
        OPTIM_REG["OPTIM_DICT Registry"]
    end
    
    subgraph "Forward Hook System"
        HOOK_MGR["ForwardHookManager"]
        IO_DICT["I/O Dictionary Storage"]
        HOOK_REG["register_forward_hook_with_dict()"]
    end
    
    subgraph "Model Adaptation"
        AUX_WRAPPER["AuxiliaryModelWrapper"]
        TEACHER_WRAPPER["Teacher4FactorTransfer"]
        STUDENT_WRAPPER["Student4FactorTransfer"]
        CONNECTOR["Connector4DAB"]
    end
    
    YAML --> YAML_UTIL
    YAML_UTIL --> IMPORT_CALL
    IMPORT_CALL --> DISTILL_BOX
    IMPORT_CALL --> TRAIN_BOX
    
    DISTILL_BOX --> MODEL_REG
    DISTILL_BOX --> DATASET_REG
    DISTILL_BOX --> LOSS_REG
    DISTILL_BOX --> OPTIM_REG
    
    TRAIN_BOX --> MODEL_REG
    TRAIN_BOX --> DATASET_REG
    TRAIN_BOX --> LOSS_REG
    TRAIN_BOX --> OPTIM_REG
    
    DISTILL_BOX --> HOOK_MGR
    TRAIN_BOX --> HOOK_MGR
    HOOK_MGR --> HOOK_REG
    HOOK_REG --> IO_DICT
    
    DISTILL_BOX --> AUX_WRAPPER
    TRAIN_BOX --> AUX_WRAPPER
    AUX_WRAPPER --> TEACHER_WRAPPER
    AUX_WRAPPER --> STUDENT_WRAPPER
    AUX_WRAPPER --> CONNECTOR
    
    MULTI_DISTILL -.-> DISTILL_BOX
    MULTI_TRAIN -.-> TRAIN_BOX
```

Sources: [torchdistill/core/distillation.py:28-567](), [torchdistill/core/training.py:24-416](), [torchdistill/core/forward_hook.py:104-206](), [torchdistill/models/wrapper.py:16-30]()

## Configuration-Driven System

The configuration system enables declarative experiment definition through YAML files. All components are instantiated and configured without requiring Python code changes.

### Configuration Flow

```mermaid
graph LR
    subgraph "YAML Configuration"
        YAML_FILE["experiment.yaml"]
        DEPENDENCIES["dependencies: []"]
        DATASETS["datasets: {}"]
        MODELS["models: {}"]
        TRAIN["train: {}"]
    end
    
    subgraph "Dynamic Loading"
        YAML_LOAD["yaml_util.load_yaml_file()"]
        IMPORT_CONSTRUCTOR["!import_call constructor"]
        DYNAMIC_IMPORT["Dynamic module imports"]
    end
    
    subgraph "Runtime Objects"
        DATASET_OBJS["Dataset instances"]
        MODEL_OBJS["Model instances"]
        CRITERION_OBJS["Loss function instances"]
        OPTIM_OBJS["Optimizer instances"]
    end
    
    YAML_FILE --> YAML_LOAD
    DEPENDENCIES --> DYNAMIC_IMPORT
    DATASETS --> IMPORT_CONSTRUCTOR
    MODELS --> IMPORT_CONSTRUCTOR
    TRAIN --> IMPORT_CONSTRUCTOR
    
    YAML_LOAD --> IMPORT_CONSTRUCTOR
    IMPORT_CONSTRUCTOR --> DATASET_OBJS
    IMPORT_CONSTRUCTOR --> MODEL_OBJS
    IMPORT_CONSTRUCTOR --> CRITERION_OBJS
    IMPORT_CONSTRUCTOR --> OPTIM_OBJS
```

The `!import_call` constructor allows instantiation of any Python class with specified arguments directly from YAML configuration. This eliminates the need to modify framework code when adding new components.

Sources: [README.md:66-140](), [torchdistill/common/yaml_util.py]()

## Training Framework

The training framework provides two main execution engines: `TrainingBox` for standard training and `DistillationBox` for knowledge distillation.

### Training Box Architecture

```mermaid
graph TD
    subgraph "TrainingBox Lifecycle"
        INIT["__init__()"]
        SETUP["setup()"]
        SETUP_DATA["setup_data_loaders()"]
        SETUP_MODEL["setup_model()"]
        SETUP_LOSS["setup_loss()"]
        SETUP_OPTIM["optimizer setup"]
        FORWARD["forward_process()"]
        PRE_EPOCH["pre_epoch_process()"]
        POST_EPOCH["post_epoch_process()"]
    end
    
    subgraph "Data Components"
        TRAIN_LOADER["train_data_loader"]
        VAL_LOADER["val_data_loader"]
        DATASET_DICT["dataset_dict"]
    end
    
    subgraph "Model Components"
        MODEL["self.model"]
        ORG_MODEL["self.org_model"]
        MODEL_IO["model_io_dict"]
        HOOKS["forward hooks"]
    end
    
    subgraph "Training Components"
        CRITERION["self.criterion"]
        OPTIMIZER["self.optimizer"]
        SCHEDULER["self.lr_scheduler"]
    end
    
    INIT --> SETUP
    SETUP --> SETUP_DATA
    SETUP --> SETUP_MODEL
    SETUP --> SETUP_LOSS
    SETUP --> SETUP_OPTIM
    
    SETUP_DATA --> TRAIN_LOADER
    SETUP_DATA --> VAL_LOADER
    SETUP_DATA --> DATASET_DICT
    
    SETUP_MODEL --> MODEL
    SETUP_MODEL --> ORG_MODEL
    SETUP_MODEL --> MODEL_IO
    SETUP_MODEL --> HOOKS
    
    SETUP_LOSS --> CRITERION
    SETUP_OPTIM --> OPTIMIZER
    SETUP_OPTIM --> SCHEDULER
    
    FORWARD --> MODEL
    FORWARD --> CRITERION
    PRE_EPOCH --> MODEL
    POST_EPOCH --> MODEL
```

Sources: [torchdistill/core/training.py:24-416]()

### Distillation Box Architecture

```mermaid
graph TD
    subgraph "DistillationBox Components"
        TEACHER["teacher_model"]
        STUDENT["student_model"]
        TEACHER_IO["teacher_io_dict"]
        STUDENT_IO["student_io_dict"]
        TEACHER_PROC["teacher_forward_proc"]
        STUDENT_PROC["student_forward_proc"]
    end
    
    subgraph "Forward Process Flow"
        GET_TEACHER["get_teacher_output()"]
        TEACHER_FWD["Teacher forward pass"]
        STUDENT_FWD["Student forward pass"]
        EXTRACT_IO["extract_io_dict()"]
        CRITERION_CALC["criterion calculation"]
    end
    
    subgraph "I/O Management"
        TEACHER_HOOKS["teacher forward hooks"]
        STUDENT_HOOKS["student forward hooks"]
        IO_EXTRACTION["I/O dict extraction"]
        CACHE_SUPPORT["Teacher output caching"]
    end
    
    TEACHER --> GET_TEACHER
    STUDENT --> STUDENT_FWD
    GET_TEACHER --> TEACHER_FWD
    TEACHER_FWD --> EXTRACT_IO
    STUDENT_FWD --> EXTRACT_IO
    EXTRACT_IO --> CRITERION_CALC
    
    TEACHER_HOOKS --> TEACHER_IO
    STUDENT_HOOKS --> STUDENT_IO
    TEACHER_IO --> IO_EXTRACTION
    STUDENT_IO --> IO_EXTRACTION
    
    GET_TEACHER --> CACHE_SUPPORT
```

The `DistillationBox` manages both teacher and student models, handles forward hook registration for intermediate feature extraction, and supports teacher output caching for efficiency.

Sources: [torchdistill/core/distillation.py:28-567]()

## Component Registry System

The registry system provides a plugin architecture for models, datasets, losses, and optimizers. Components are registered via decorators and retrieved by string keys.

### Registry Pattern Implementation

```mermaid
graph LR
    subgraph "Registration Phase"
        DECORATOR["@register_model"]
        IMPL_CLASS["ModelImplementation"]
        REGISTER_FUNC["_register_to_dict()"]
        STORAGE["MODEL_DICT storage"]
    end
    
    subgraph "Retrieval Phase"
        CONFIG_KEY["config['key']"]
        GET_FUNC["get_model()"]
        LOOKUP["Dict lookup"]
        INSTANTIATE["Class instantiation"]
    end
    
    subgraph "Registry Categories"
        MODEL_DICT["MODEL_DICT"]
        DATASET_DICT["DATASET_DICT"]
        LOSS_DICT["LOSS_DICT"]
        OPTIM_DICT["OPTIM_DICT"]
    end
    
    DECORATOR --> IMPL_CLASS
    IMPL_CLASS --> REGISTER_FUNC
    REGISTER_FUNC --> STORAGE
    
    CONFIG_KEY --> GET_FUNC
    GET_FUNC --> LOOKUP
    LOOKUP --> INSTANTIATE
    
    STORAGE --> MODEL_DICT
    STORAGE --> DATASET_DICT
    STORAGE --> LOSS_DICT
    STORAGE --> OPTIM_DICT
```

Each component category uses the same registration pattern:

| Component Type | Registry Dict | Registration Decorator | Getter Function |
|----------------|--------------|----------------------|-----------------|
| Models | `MODEL_DICT` | `@register_model` | `get_model()` |
| Datasets | `DATASET_DICT` | `@register_dataset` | `get_dataset()` |
| Losses | `LOSS_DICT` | `@register_loss` | `get_loss()` |
| Optimizers | `OPTIM_DICT` | `@register_optimizer` | `get_optimizer()` |

Sources: [torchdistill/models/registry.py](), [torchdistill/datasets/registry.py](), [torchdistill/losses/registry.py](), [torchdistill/optim/registry.py]()

## Forward Hook Management

The `ForwardHookManager` provides a clean API for extracting intermediate representations from PyTorch models without modifying their forward methods.

### Forward Hook System Architecture

```mermaid
graph TD
    subgraph "ForwardHookManager"
        MANAGER["ForwardHookManager"]
        ADD_HOOK["add_hook()"]
        POP_DICT["pop_io_dict()"]
        TARGET_DEVICE["target_device"]
    end
    
    subgraph "Hook Registration"
        GET_MODULE["get_module()"]
        REGISTER_HOOK["register_forward_hook_with_dict()"]
        HOOK_FUNC["forward_hook function"]
        HANDLE["RemovableHandle"]
    end
    
    subgraph "Data Storage"
        IO_DICT["io_dict storage"]
        MODULE_PATH["module_path keys"]
        INPUT_OUTPUT["input/output tensors"]
        DEVICE_GATHER["device gathering"]
    end
    
    subgraph "Hook Function Types"
        INPUT_HOOK["forward_hook4input"]
        OUTPUT_HOOK["forward_hook4output"]
        IO_HOOK["forward_hook4io"]
    end
    
    MANAGER --> ADD_HOOK
    ADD_HOOK --> GET_MODULE
    GET_MODULE --> REGISTER_HOOK
    REGISTER_HOOK --> HOOK_FUNC
    HOOK_FUNC --> HANDLE
    
    HOOK_FUNC --> IO_DICT
    IO_DICT --> MODULE_PATH
    MODULE_PATH --> INPUT_OUTPUT
    
    POP_DICT --> DEVICE_GATHER
    DEVICE_GATHER --> INPUT_OUTPUT
    
    REGISTER_HOOK --> INPUT_HOOK
    REGISTER_HOOK --> OUTPUT_HOOK
    REGISTER_HOOK --> IO_HOOK
```

The hook system supports three modes:
- Input-only hooks (`requires_input=True, requires_output=False`)
- Output-only hooks (`requires_input=False, requires_output=True`)  
- Input-output hooks (`requires_input=True, requires_output=True`)

Sources: [torchdistill/core/forward_hook.py:39-206]()

## Model Wrapper System

The auxiliary model wrapper system allows modification of model behavior for specific knowledge distillation methods without changing the original model implementations.

### Auxiliary Wrapper Hierarchy

```mermaid
graph TD
    subgraph "Base Wrapper"
        AUX_BASE["AuxiliaryModelWrapper"]
        FORWARD_METHOD["forward()"]
        SECONDARY_FWD["secondary_forward()"]
        POST_EPOCH["post_epoch_process()"]
    end
    
    subgraph "Teacher Wrappers"
        TEACHER_FT["Teacher4FactorTransfer"]
        PARAPHRASER["Paraphraser4FactorTransfer"]
        PARAPHRASER_CKPT["paraphraser checkpoint"]
    end
    
    subgraph "Student Wrappers"
        STUDENT_FT["Student4FactorTransfer"]
        TRANSLATOR["Translator4FactorTransfer"]
        CONNECTOR_DAB["Connector4DAB"]
        VID_DISTRIBUTOR["VariationalDistributor4VID"]
    end
    
    subgraph "Specialized Wrappers"
        LINEAR_CCKD["Linear4CCKD"]
        LINEAR_CRD["Linear4CRD"]
        SS_WRAPPER["SSWrapper4SSKD"]
        HEAD_RCNN["HeadRCNN"]
    end
    
    AUX_BASE --> TEACHER_FT
    AUX_BASE --> STUDENT_FT
    AUX_BASE --> CONNECTOR_DAB
    AUX_BASE --> VID_DISTRIBUTOR
    AUX_BASE --> LINEAR_CCKD
    AUX_BASE --> LINEAR_CRD
    AUX_BASE --> SS_WRAPPER
    AUX_BASE --> HEAD_RCNN
    
    TEACHER_FT --> PARAPHRASER
    PARAPHRASER --> PARAPHRASER_CKPT
    STUDENT_FT --> TRANSLATOR
    
    FORWARD_METHOD --> TEACHER_FT
    SECONDARY_FWD --> TEACHER_FT
    POST_EPOCH --> TEACHER_FT
```

Each wrapper implements:
- `forward()`: Primary model forward pass
- `secondary_forward()`: Additional computations using I/O dict
- `post_epoch_process()`: End-of-epoch operations (e.g., checkpoint saving)

Sources: [torchdistill/models/wrapper.py:16-567]()

## Integration Patterns

The architectural components integrate through well-defined interfaces and data flow patterns.

### Component Integration Flow

```mermaid
graph TD
    subgraph "Configuration Phase"
        YAML_CONFIG["YAML Configuration"]
        COMPONENT_CONFIGS["Component Configurations"]
        REGISTRY_LOOKUP["Registry Lookups"]
    end
    
    subgraph "Setup Phase"
        BOX_INIT["Box Initialization"]
        MODEL_SETUP["Model Setup"]
        HOOK_SETUP["Hook Registration"]
        WRAPPER_SETUP["Wrapper Application"]
    end
    
    subgraph "Execution Phase"
        EPOCH_LOOP["Training Epoch Loop"]
        FORWARD_PASS["Forward Pass"]
        IO_EXTRACTION["I/O Extraction"]
        LOSS_CALC["Loss Calculation"]
        BACKWARD_PASS["Backward Pass"]
    end
    
    subgraph "State Management"
        IO_DICTS["I/O Dictionaries"]
        MODEL_STATE["Model States"]
        CHECKPOINT["Checkpointing"]
    end
    
    YAML_CONFIG --> COMPONENT_CONFIGS
    COMPONENT_CONFIGS --> REGISTRY_LOOKUP
    REGISTRY_LOOKUP --> BOX_INIT
    
    BOX_INIT --> MODEL_SETUP
    MODEL_SETUP --> HOOK_SETUP
    HOOK_SETUP --> WRAPPER_SETUP
    
    WRAPPER_SETUP --> EPOCH_LOOP
    EPOCH_LOOP --> FORWARD_PASS
    FORWARD_PASS --> IO_EXTRACTION
    IO_EXTRACTION --> LOSS_CALC
    LOSS_CALC --> BACKWARD_PASS
    
    IO_EXTRACTION --> IO_DICTS
    MODEL_SETUP --> MODEL_STATE
    EPOCH_LOOP --> CHECKPOINT
```

This integration enables:
- **Declarative Configuration**: Complete experiment definition in YAML
- **Modular Components**: Pluggable models, datasets, losses, optimizers
- **Feature Extraction**: Non-intrusive intermediate representation access
- **Model Adaptation**: Behavior modification through wrappers
- **Multi-stage Training**: Progressive training configurations

Sources: [torchdistill/core/distillation.py:176-282](), [torchdistill/core/training.py:141-220](), [torchdistill/core/util.py:36-67]()

---

