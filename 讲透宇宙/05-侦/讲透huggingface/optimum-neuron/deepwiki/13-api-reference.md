<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-neuron · page 13 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/neuron/__init__.py](optimum/neuron/__init__.py)
- [optimum/neuron/modeling.py](optimum/neuron/modeling.py)
- [optimum/neuron/modeling_base.py](optimum/neuron/modeling_base.py)
- [optimum/neuron/pipelines/transformers/base.py](optimum/neuron/pipelines/transformers/base.py)
- [optimum/neuron/utils/__init__.py](optimum/neuron/utils/__init__.py)

</details>



This document provides an overview of the optimum-neuron API structure and serves as an index to detailed API reference pages. The optimum-neuron library exposes four main API categories: Training, Inference, Export, and Cache management. Each category is documented in detail in its respective sub-page.

For practical usage examples and tutorials, see [Quick Start Guide](#3). For conceptual explanations of the training system, see [Training on AWS Neuron](#5). For inference system concepts, see [Inference with Neuron Models](#6).

## API Organization

The optimum-neuron API is organized into four primary categories:

| Category | Purpose | Key Classes | Reference Page |
|----------|---------|-------------|----------------|
| **Training** | Fine-tuning and training models on Trainium | `NeuronTrainer`, `NeuronAccelerator`, `NeuronTrainingArguments` | [Training API](#12.1) |
| **Inference** | Running pre-compiled or exported models for prediction | `NeuronModelForCausalLM`, `NeuronModelForFeatureExtraction`, diffusion pipelines | [Inference API](#12.2) |
| **Export** | Converting standard models to Neuron format | `NeuronDefaultConfig`, model-specific export configs | [Export API](#12.3) |
| **Cache** | Managing compilation artifacts | Cache utility functions, Hub repository management | [Cache API](#12.4) |

Sources: [optimum/neuron/__init__.py:34-88]()

## Package Entry Points

```mermaid
graph TB
    subgraph "optimum.neuron Package"
        INIT["__init__.py<br/>Package Entry Point"]
        
        subgraph "Training Components"
            TRAINER["NeuronTrainer<br/>NeuronSFTTrainer"]
            ARGS["NeuronTrainingArguments<br/>NeuronSFTConfig"]
            ACCEL["NeuronAccelerator<br/>NeuronAcceleratorState"]
        end
        
        subgraph "Inference Models"
            DECODER["NeuronModelForCausalLM"]
            SEQ2SEQ["NeuronModelForSeq2SeqLM"]
            ENCODER["NeuronModelForFeatureExtraction<br/>NeuronModelForSequenceClassification<br/>+ 11 more task-specific models"]
            DIFFUSION["NeuronStableDiffusionPipeline<br/>+ 12 more diffusion pipelines"]
            TRACED["NeuronTracedModel"]
        end
        
        subgraph "Utilities"
            PIPE["pipeline()"]
            ARGPARSER["NeuronHfArgumentParser"]
        end
    end
    
    INIT --> TRAINER
    INIT --> ARGS
    INIT --> ACCEL
    INIT --> DECODER
    INIT --> SEQ2SEQ
    INIT --> ENCODER
    INIT --> DIFFUSION
    INIT --> TRACED
    INIT --> PIPE
    INIT --> ARGPARSER
```

**Package Entry Points Diagram**: Shows all classes and functions exported by the `optimum.neuron` package namespace, organized by functional category.

Sources: [optimum/neuron/__init__.py:34-88](), [optimum/neuron/__init__.py:103-162]()

## Model Class Hierarchy

The inference API uses an inheritance-based architecture where all Neuron models derive from common base classes:

```mermaid
graph TB
    BASE["NeuronModel<br/>Abstract base class<br/>modeling_base.py:28"]
    PRETRAINED["PreTrainedModel<br/>Fake class for transformers compatibility<br/>modeling_base.py:21"]
    TRACED["NeuronTracedModel<br/>Compiled model wrapper<br/>modeling_traced.py"]
    
    DECODER["NeuronModelForCausalLM<br/>Abstract decoder base<br/>modeling_decoder.py:105"]
    SEQ2SEQ["NeuronModelForSeq2SeqLM<br/>Seq2seq models<br/>modeling_seq2seq.py"]
    
    subgraph "Task-Specific Models"
        FEAT["NeuronModelForFeatureExtraction"]
        MASKED["NeuronModelForMaskedLM"]
        QA["NeuronModelForQuestionAnswering"]
        SEQCLS["NeuronModelForSequenceClassification"]
        TOKCLS["NeuronModelForTokenClassification"]
        IMGCLS["NeuronModelForImageClassification"]
        AUDIO["NeuronModelForAudioClassification"]
    end
    
    subgraph "Concrete Decoder Implementations"
        HLO["HloGenerationNeuronModel<br/>HLO backend"]
        NXD["NxDModelForCausalLM<br/>NeuronX Distributed backend"]
        VLLM["vLLM backend models"]
    end
    
    BASE --> PRETRAINED
    PRETRAINED --> TRACED
    PRETRAINED --> DECODER
    PRETRAINED --> SEQ2SEQ
    
    TRACED --> FEAT
    TRACED --> MASKED
    TRACED --> QA
    TRACED --> SEQCLS
    TRACED --> TOKCLS
    TRACED --> IMGCLS
    TRACED --> AUDIO
    
    DECODER --> HLO
    DECODER --> NXD
    DECODER --> VLLM
```

**Model Class Inheritance Hierarchy**: All Neuron models inherit from `NeuronModel` base class. Task-specific encoder models inherit from `NeuronTracedModel`, while decoder models inherit from the abstract `NeuronModelForCausalLM` class with multiple backend implementations.

Sources: [optimum/neuron/modeling_base.py:28-44](), [optimum/neuron/modeling_decoder.py:105-368](), [optimum/neuron/modeling.py:92-743]()

## Training System Components

```mermaid
graph LR
    subgraph "User-Facing API"
        TRAINER["NeuronTrainer<br/>trainers.py"]
        SFT["NeuronSFTTrainer<br/>trainers.py"]
        ARGS["NeuronTrainingArguments<br/>trainers.py"]
    end
    
    subgraph "Acceleration Layer"
        ACCEL["NeuronAccelerator<br/>accelerate/accelerator.py:79"]
        STATE["NeuronAcceleratorState<br/>accelerate/state.py:85"]
        PARTIAL["NeuronPartialState<br/>accelerate/state.py:43"]
    end
    
    subgraph "Configuration"
        MIXED["MixedPrecisionConfig<br/>accelerate/utils/dataclasses.py:35"]
        TRN["TrainingNeuronConfig<br/>models/neuron_config.py"]
    end
    
    TRAINER --> ACCEL
    SFT --> ACCEL
    ARGS --> TRAINER
    ACCEL --> STATE
    STATE --> PARTIAL
    ACCEL --> MIXED
    STATE --> TRN
```

**Training API Component Relationships**: The `NeuronTrainer` uses `NeuronAccelerator` which manages state through `NeuronAcceleratorState` and applies configurations via `MixedPrecisionConfig` and `TrainingNeuronConfig`.

Sources: [optimum/neuron/accelerate/accelerator.py:79-597](), [optimum/neuron/accelerate/state.py:43-177](), [optimum/neuron/accelerate/utils/dataclasses.py:35-70]()

## Typical API Usage Patterns

The following diagram illustrates common workflows and which API components are involved at each stage:

```mermaid
flowchart TD
    START["User Code"]
    
    subgraph "Export Workflow"
        E1["from_pretrained(export=True)"]
        E2["NeuronDefaultConfig"]
        E3["neuron-cc compiler"]
        E4["save_pretrained()"]
    end
    
    subgraph "Training Workflow"
        T1["NeuronTrainingArguments"]
        T2["NeuronAccelerator.prepare()"]
        T3["NeuronTrainer.train()"]
        T4["model.save_pretrained()"]
    end
    
    subgraph "Inference Workflow"
        I1["NeuronModelForCausalLM.from_pretrained()"]
        I2["model.generate()"]
        I3["pipeline()"]
    end
    
    subgraph "Cache Workflow"
        C1["cache_utils.get_hf_hub_cache_repos()"]
        C2["cache_utils.set_neuron_cache_path()"]
        C3["CLI: neuron cache sync"]
    end
    
    START --> E1
    START --> T1
    START --> I1
    START --> C1
    
    E1 --> E2
    E2 --> E3
    E3 --> E4
    
    T1 --> T2
    T2 --> T3
    T3 --> T4
    
    I1 --> I2
    I1 --> I3
    
    C1 --> C2
    C2 --> C3
```

**Common API Usage Patterns**: Four typical workflows showing which API functions and classes are invoked for export, training, inference, and cache management tasks.

Sources: [optimum/neuron/modeling_decoder.py:198-248](), [optimum/neuron/accelerate/accelerator.py:79-597]()

## Training API

The training API enables distributed fine-tuning on Trainium devices with support for tensor parallelism, pipeline parallelism, and ZeRO-1 optimization. Key components:

- **`NeuronTrainer`**: Drop-in replacement for Hugging Face `Trainer` with Neuron-specific optimizations
- **`NeuronSFTTrainer`**: Specialized trainer for supervised fine-tuning with integration to TRL library
- **`NeuronAccelerator`**: Extends `accelerate.Accelerator` with Neuron hardware support
- **`NeuronTrainingArguments`**: Configuration dataclass extending `TrainingArguments`
- **`TrainingNeuronConfig`**: Neuron-specific training parameters (tensor/pipeline parallelism sizes)
- **`MixedPrecisionConfig`**: Controls BF16 training modes and optimizer precision settings

For detailed documentation of all training classes and methods, see [Training API](#12.1).

Sources: [optimum/neuron/__init__.py:36-41](), [optimum/neuron/accelerate/accelerator.py:79-597]()

## Inference API

The inference API provides pre-compiled model classes organized by task modality. All inference models support:

- Loading from pre-compiled Neuron models via `from_pretrained()`
- Exporting standard models via `from_pretrained(export=True)`
- Saving compiled artifacts via `save_pretrained()`
- Standard transformers-compatible interfaces

**Model Categories:**

| Category | Base Class | Example Tasks |
|----------|-----------|---------------|
| **Decoder Models** | `NeuronModelForCausalLM` | Text generation, chat, instruction following |
| **Encoder Models** | `NeuronTracedModel` | Feature extraction, classification, NER, Q&A |
| **Seq2Seq Models** | `NeuronModelForSeq2SeqLM` | Translation, summarization |
| **Vision Models** | `NeuronTracedModel` | Image classification, object detection, segmentation |
| **Audio Models** | `NeuronTracedModel` | Audio classification, CTC, speaker verification |
| **Diffusion Models** | `NeuronDiffusionPipelineBase` | Image generation, inpainting, ControlNet |

For detailed documentation of all inference classes and methods, see [Inference API](#12.2).

Sources: [optimum/neuron/modeling.py:92-743](), [optimum/neuron/modeling_decoder.py:105-368](), [optimum/neuron/__init__.py:43-80]()

## Export API

The export API handles conversion of standard PyTorch/Hugging Face models to Neuron-compiled format. Key components:

- **`NeuronDefaultConfig`**: Base configuration class specifying batch size, sequence length, tensor parallelism
- **Model-specific configs**: Specialized configurations for different architectures (e.g., `BertNeuronConfig`)
- **Export functions**: `export_neuronx()`, `export_models()` for batch compilation
- **Compiler argument builders**: Functions to construct `neuron-cc` and `neuronx-cc` flags

The export process:
1. Load standard model from Hub or local path
2. Apply `NeuronConfig` to determine compilation parameters
3. Generate dummy inputs matching target shapes
4. Invoke Neuron compiler to create NEFF (Neuron Executable File Format)
5. Validate outputs match PyTorch reference
6. Save compiled artifacts with configuration

For detailed documentation of export configurations and functions, see [Export API](#12.3).

Sources: [optimum/neuron/utils/__init__.py:21-89]()

## Cache API

The cache API manages compilation artifacts to avoid redundant compilations. The cache system operates at three levels:

1. **Local cache**: `/var/tmp/neuron-compile-cache` (instant lookup)
2. **Hub cache**: Pre-compiled models on Hugging Face Hub (download in seconds)
3. **Compile on miss**: Full compilation when no cache hit (30-60 minutes)

**Key Functions:**

- **`get_hf_hub_cache_repos()`**: Retrieve list of cache repositories (official + custom)
- **`set_neuron_cache_path()`**: Configure custom cache repository
- **`synchronize_hub_cache()`**: Upload local compilations to Hub
- **`lookup_in_cache()`**: Check if compilation exists in cache hierarchy

**Environment Variables:**

- `CUSTOM_CACHE_REPO`: Override default cache repository
- `NEURON_CC_FLAGS`: Pass flags to Neuron compiler (affects cache keys)

For detailed documentation of cache functions and CLI commands, see [Cache API](#12.4) and [Cache CLI Commands](#7.3).

Sources: [optimum/neuron/utils/__init__.py:21-89]()

## Configuration Classes

```mermaid
graph TB
    subgraph "Training Configuration"
        TRN["TrainingNeuronConfig<br/>tensor_parallel_size<br/>pipeline_parallel_size<br/>sequence_parallel_enabled"]
        MIXED["MixedPrecisionConfig<br/>mode: FULL_BF16 | AUTOCAST_BF16<br/>stochastic_rounding<br/>optimizer_use_master_weights"]
        TARGS["NeuronTrainingArguments<br/>Extends TrainingArguments"]
    end
    
    subgraph "Inference Configuration"
        NCONFIG["NeuronConfig<br/>Base configuration class<br/>batch_size, sequence_length<br/>tensor_parallel_size"]
        DEFAULT["NeuronDefaultConfig<br/>Generic model config"]
        SPECIFIC["Model-specific configs<br/>BertNeuronConfig<br/>LlamaConfig, etc."]
    end
    
    TARGS --> TRN
    TARGS --> MIXED
    DEFAULT --> SPECIFIC
    NCONFIG --> DEFAULT
```

**Configuration Class Hierarchy**: Training configurations control distributed training parameters, while inference configurations specify model compilation shapes and parallelism.

Sources: [optimum/neuron/accelerate/utils/dataclasses.py:35-70](), [optimum/neuron/__init__.py:36-41]()

## Method Signatures Overview

The following table summarizes key methods across all API categories:

| Class | Key Methods | Purpose |
|-------|-------------|---------|
| **`NeuronModelForCausalLM`** | `from_pretrained()`, `export()`, `generate()`, `save_pretrained()` | Load, export, run inference, save |
| **`NeuronTracedModel`** | `from_pretrained()`, `forward()`, `save_pretrained()` | Load traced model, run forward pass |
| **`NeuronTrainer`** | `train()`, `evaluate()`, `save_model()` | Execute training loop |
| **`NeuronAccelerator`** | `prepare()`, `prepare_model()`, `prepare_optimizer()`, `backward()` | Setup distributed training |
| **`NeuronConfig`** | `from_pretrained()`, `save_pretrained()` | Load/save configuration |

For complete method signatures with parameters and return types, see the detailed API reference pages for each category.

Sources: [optimum/neuron/modeling_decoder.py:105-368](), [optimum/neuron/accelerate/accelerator.py:79-597]()

## Import Patterns

Common import statements for each API category:

```python
# Training API
from optimum.neuron import NeuronTrainer, NeuronTrainingArguments
from optimum.neuron import NeuronAccelerator
from optimum.neuron.accelerate.utils import MixedPrecisionConfig

# Inference API - Decoder models
from optimum.neuron import NeuronModelForCausalLM

# Inference API - Encoder models
from optimum.neuron import (
    NeuronModelForFeatureExtraction,
    NeuronModelForSequenceClassification,
    NeuronModelForTokenClassification,
)

# Inference API - Vision models
from optimum.neuron import (
    NeuronModelForImageClassification,
    NeuronModelForSemanticSegmentation,
    NeuronModelForObjectDetection,
)

# Inference API - Diffusion models
from optimum.neuron import (
    NeuronStableDiffusionPipeline,
    NeuronStableDiffusionXLPipeline,
)

# Pipeline abstraction
from optimum.neuron import pipeline

# Cache utilities
from optimum.neuron.utils.cache_utils import (
    get_hf_hub_cache_repos,
    set_neuron_cache_path,
)
```

Sources: [optimum/neuron/__init__.py:103-162]()

## Next Steps

- For Training API details: [Training API](#12.1)
- For Inference API details: [Inference API](#12.2)
- For Export API details: [Export API](#12.3)
- For Cache API details: [Cache API](#12.4)
- For CLI reference: [CLI Reference](#9)

---

