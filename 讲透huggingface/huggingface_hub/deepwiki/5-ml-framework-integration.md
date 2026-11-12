<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface_hub · page 5 ML Framework Integration · fetched 2026-10-26 -->

# ML Framework Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/de/guides/integrations.md](docs/source/de/guides/integrations.md)
- [docs/source/en/guides/integrations.md](docs/source/en/guides/integrations.md)
- [docs/source/en/guides/overview.md](docs/source/en/guides/overview.md)
- [docs/source/en/index.md](docs/source/en/index.md)
- [docs/source/en/quick-start.md](docs/source/en/quick-start.md)
- [src/huggingface_hub/_snapshot_download.py](src/huggingface_hub/_snapshot_download.py)
- [src/huggingface_hub/fastai_utils.py](src/huggingface_hub/fastai_utils.py)
- [src/huggingface_hub/hub_mixin.py](src/huggingface_hub/hub_mixin.py)
- [src/huggingface_hub/utils/_auth.py](src/huggingface_hub/utils/_auth.py)
- [tests/test_cache_layout.py](tests/test_cache_layout.py)
- [tests/test_hub_mixin.py](tests/test_hub_mixin.py)
- [tests/test_hub_mixin_pytorch.py](tests/test_hub_mixin_pytorch.py)
- [tests/test_snapshot_download.py](tests/test_snapshot_download.py)

</details>



This document covers the ML framework integration system in `huggingface_hub`, which provides a unified interface for saving, loading, and sharing models from various machine learning frameworks with the Hugging Face Hub. The system enables seamless integration through mixins and utilities that can be added to existing model classes.

For information about the core HTTP-based API client, see [Core API Client (HfApi)](#2). For details about repository cards and metadata, see [Repository Cards](#5).

## Overview

The ML framework integration system provides a standardized way for different ML frameworks to interact with the Hugging Face Hub. It supports PyTorch, TensorFlow/Keras, and FastAI, with extensible patterns for additional frameworks.

```mermaid
graph TB
    subgraph "User Models"
        PyTorchModel["PyTorch Model Class"]
        KerasModel["Keras Model Class"] 
        FastAIModel["FastAI Learner"]
    end
    
    subgraph "Hub Mixins"
        ModelHubMixin["ModelHubMixin<br/>(Base Class)"]
        PyTorchModelHubMixin["PyTorchModelHubMixin"]
        KerasModelHubMixin["KerasModelHubMixin"]
    end
    
    subgraph "Framework Utils"
        FastAIUtils["fastai_utils<br/>push_to_hub_fastai<br/>from_pretrained_fastai"]
    end
    
    subgraph "Core Hub API"
        HfApi["HfApi"]
        FileDownload["hf_hub_download"]
        SnapshotDownload["snapshot_download"]
    end
    
    PyTorchModel --> PyTorchModelHubMixin
    KerasModel --> KerasModelHubMixin
    FastAIModel --> FastAIUtils
    
    PyTorchModelHubMixin --> ModelHubMixin
    KerasModelHubMixin --> ModelHubMixin
    
    ModelHubMixin --> HfApi
    ModelHubMixin --> FileDownload
    KerasModelHubMixin --> SnapshotDownload
    FastAIUtils --> HfApi
    FastAIUtils --> SnapshotDownload
```

**Sources:** [src/huggingface_hub/hub_mixin.py:76-184](), [src/huggingface_hub/keras_mixin.py:420-454](), [src/huggingface_hub/fastai_utils.py:1-23]()

## Hub Mixin Architecture

### Core Mixin Pattern

The `ModelHubMixin` class provides the foundational interface that all framework integrations inherit from. It implements a generic pattern for saving, loading, and sharing models.

```mermaid
classDiagram
    class ModelHubMixin {
        +save_pretrained(save_directory)
        +from_pretrained(pretrained_model_name_or_path)
        +push_to_hub(repo_id)
        +_save_pretrained(save_directory)*
        +_from_pretrained(...)*
        +generate_model_card()
        -_hub_mixin_config
        -_hub_mixin_info
    }
    
    class PyTorchModelHubMixin {
        +_save_pretrained(save_directory)
        +_from_pretrained(...)
        +_load_as_safetensor(model, model_file)
        +_load_as_pickle(model, model_file)
    }
    
    class KerasModelHubMixin {
        +_save_pretrained(save_directory)
        +_from_pretrained(...)
    }
    
    ModelHubMixin <|-- PyTorchModelHubMixin
    ModelHubMixin <|-- KerasModelHubMixin
    
    note for ModelHubMixin "Abstract methods marked with *"
```

**Sources:** [src/huggingface_hub/hub_mixin.py:76-184](), [src/huggingface_hub/hub_mixin.py:715-759](), [src/huggingface_hub/keras_mixin.py:420-454]()

### Configuration and Metadata System

The mixin system includes sophisticated configuration handling with support for custom types and automatic model card generation.

```mermaid
graph LR
    subgraph "Configuration Flow"
        InitParams["__init__ parameters"] --> ConfigExtraction["_hub_mixin_init_parameters"]
        ConfigExtraction --> JSONSerialization["JSON serialization"]
        JSONSerialization --> ConfigFile["config.json"]
    end
    
    subgraph "Custom Type Handling"
        CustomTypes["Custom Types"] --> Encoders["_hub_mixin_coders"]
        Encoders --> EncodedValues["Encoded Values"]
        EncodedValues --> JSONSerialization
    end
    
    subgraph "Model Card Generation"
        MixinInfo["_hub_mixin_info"] --> ModelCardData["ModelCardData"]
        ModelCardData --> ModelCard["README.md"]
    end
```

**Sources:** [src/huggingface_hub/hub_mixin.py:186-196](), [src/huggingface_hub/hub_mixin.py:276-287](), [src/huggingface_hub/hub_mixin.py:703-712]()

## Framework-Specific Implementations

### PyTorch Integration

The `PyTorchModelHubMixin` provides PyTorch-specific functionality with support for both SafeTensors and pickle formats.

Key features:
- **SafeTensors Support**: Primary serialization format for model weights
- **Fallback to Pickle**: Legacy support for `pytorch_model.bin` files  
- **Device Mapping**: Support for loading models on specific devices
- **Strict Loading**: Optional strict mode for state dict loading

```mermaid
graph TB
    subgraph "PyTorch Save Flow"
        PyTorchModel["PyTorch Model"] --> SavePretrained["save_pretrained()"]
        SavePretrained --> SaveWeights["_save_pretrained()"]
        SaveWeights --> SafeTensors["model.safetensors"]
        SavePretrained --> SaveConfig["config.json"]
        SavePretrained --> ModelCard["README.md"]
    end
    
    subgraph "PyTorch Load Flow"
        FromPretrained["from_pretrained()"] --> DownloadSafeTensors["Download model.safetensors"]
        DownloadSafeTensors --> LoadSafeTensors["_load_as_safetensor()"]
        DownloadSafeTensors -.->|"EntryNotFoundError"| DownloadPickle["Download pytorch_model.bin"]
        DownloadPickle --> LoadPickle["_load_as_pickle()"]
        LoadSafeTensors --> ModelInstance["Model Instance"]
        LoadPickle --> ModelInstance
    end
```

**Sources:** [src/huggingface_hub/hub_mixin.py:767-771](), [src/huggingface_hub/hub_mixin.py:794-820](), [src/huggingface_hub/hub_mixin.py:822-842]()

### Keras/TensorFlow Integration

The Keras integration provides specialized handling for TensorFlow SavedModel format and training history.

Key features:
- **SavedModel Format**: Uses TensorFlow's SavedModel for serialization
- **Training History**: Preserves `model.history` in `history.json`
- **Model Plotting**: Automatic model architecture visualization
- **Optimizer State**: Optional inclusion of optimizer state

```mermaid
graph TB
    subgraph "Keras Save Components"
        KerasModel["Keras Model"] --> SavedModelPB["saved_model.pb"]
        KerasModel --> KerasMetadata["keras_metadata.pb"]
        KerasModel --> Variables["variables/"]
        KerasModel --> Assets["assets/"]
        
        OptionalComponents["Optional Components"]
        OptionalComponents --> HistoryJSON["history.json"]
        OptionalComponents --> ModelPNG["model.png"]
        OptionalComponents --> ConfigJSON["config.json"]
    end
    
    subgraph "Keras Validation"
        ModelBuilt["model.built"] -.->|"False"| ValueError["ValueError:<br/>Model should be built"]
        ModelBuilt -.->|"True"| Proceed["Proceed with save"]
    end
```

**Sources:** [src/huggingface_hub/keras_mixin.py:156-238](), [src/huggingface_hub/keras_mixin.py:456-458](), [src/huggingface_hub/keras_mixin.py:459-500]()

### FastAI Integration

FastAI uses a functional approach rather than mixins, providing dedicated utility functions.

Key features:
- **Pickle Serialization**: Uses FastAI's native pickle format
- **Version Compatibility**: Checks FastAI and FastCore versions
- **PyProject Integration**: Generates `pyproject.toml` with dependencies

```mermaid
graph LR
    subgraph "FastAI Functions"
        PushToHub["push_to_hub_fastai()"]
        FromPretrained["from_pretrained_fastai()"]
        SavePretrained["_save_pretrained_fastai()"]
    end
    
    subgraph "FastAI Files"
        ModelPKL["model.pkl"]
        PyProjectTOML["pyproject.toml"]
        ReadmeMD["README.md"]
        ConfigJSON["config.json"]
    end
    
    subgraph "Version Checks"
        FastAIVersion["fastai >= 2.4"]
        FastCoreVersion["fastcore >= 1.3.27"]
    end
    
    PushToHub --> SavePretrained
    SavePretrained --> ModelPKL
    SavePretrained --> PyProjectTOML
    SavePretrained --> ReadmeMD
    
    FromPretrained --> FastAIVersion
    FromPretrained --> FastCoreVersion
```

**Sources:** [src/huggingface_hub/fastai_utils.py:25-72](), [src/huggingface_hub/fastai_utils.py:211-283](), [src/huggingface_hub/fastai_utils.py:285-339]()

## Configuration System

### Configuration Serialization

The mixin system provides sophisticated configuration handling that automatically serializes model initialization parameters to JSON.

```mermaid
graph TB
    subgraph "Config Extraction Process"
        ModelInit["Model.__init__()"] --> InspectSignature["inspect.signature()"]
        InspectSignature --> ExtractParams["_hub_mixin_init_parameters"]
        ExtractParams --> FilterJsonable["Filter JSON-serializable"]
        FilterJsonable --> DefaultValues["_hub_mixin_jsonable_default_values"]
    end
    
    subgraph "Custom Type Handling"
        CustomType["Custom Type"] --> Encoder["Custom Encoder"]
        Encoder --> JSONValue["JSON Value"]
        JSONValue --> Decoder["Custom Decoder"]
        Decoder --> RestoredType["Restored Type"]
    end
    
    subgraph "Configuration Storage"
        ConfigDict["Config Dict"] --> ConfigJSON["config.json"]
        ConfigDict --> HubMixinConfig["_hub_mixin_config"]
    end
```

**Sources:** [src/huggingface_hub/hub_mixin.py:280-287](), [src/huggingface_hub/hub_mixin.py:343-379](), [src/huggingface_hub/hub_mixin.py:197-221]()

### Custom Type Encoding

The system supports custom encoders and decoders for non-JSON-serializable types through the `coders` parameter.

Example custom type configuration:
- **Dataclasses**: Automatically converted using `asdict()`
- **Custom Objects**: User-defined encoder/decoder pairs
- **Optional Types**: Special handling for `Optional[T]` annotations

**Sources:** [src/huggingface_hub/hub_mixin.py:352-379](), [src/huggingface_hub/hub_mixin.py:364-379]()

## Model Card Generation

### Automatic Model Cards

Each framework integration automatically generates model cards with relevant metadata and framework-specific information.

```mermaid
graph TB
    subgraph "Model Card Components"
        CardData["ModelCardData"]
        CardTemplate["model_card_template"]
        CardKwargs["model_card_kwargs"]
    end
    
    subgraph "Metadata Sources"
        LibraryName["library_name"]
        Tags["tags[]"]
        License["license"]
        PipelineTag["pipeline_tag"]
        Language["language[]"]
    end
    
    subgraph "Generated Files"
        ReadmeMD["README.md"]
        ModelPNG["model.png<br/>(Keras only)"]
    end
    
    CardData --> ReadmeMD
    CardTemplate --> ReadmeMD
    CardKwargs --> ReadmeMD
    
    LibraryName --> CardData
    Tags --> CardData
    License --> CardData
    PipelineTag --> CardData
    Language --> CardData
```

**Sources:** [src/huggingface_hub/hub_mixin.py:67-74](), [src/huggingface_hub/hub_mixin.py:703-712](), [src/huggingface_hub/keras_mixin.py:112-153]()

## Usage Patterns

### Framework Integration Examples

Each framework follows a consistent pattern for integration:

#### PyTorch Example Structure
```python
class MyPyTorchModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self, config=None):
        # Model initialization
        
    def forward(self, x):
        # Model forward pass
```

#### Keras Example Structure  
```python
class MyKerasModel(tf.keras.Model, KerasModelHubMixin):
    def __init__(self, config=None):
        # Model initialization
        
    def call(self, inputs):
        # Model call method
```

#### FastAI Example Structure
```python
# FastAI uses functional API
learner = Learner(...)
push_to_hub_fastai(learner, repo_id="my-model")
loaded_learner = from_pretrained_fastai("username/my-model")
```

**Sources:** [tests/test_hub_mixin_pytorch.py:53-60](), [tests/test_keras_integration.py:43-51](), [tests/test_fastai_integration.py:84-92]()

### Common Operations

All frameworks support these core operations:

- **`save_pretrained()`**: Save model locally
- **`from_pretrained()`**: Load model from Hub or local path  
- **`push_to_hub()`**: Upload model to Hub

The operations maintain consistent signatures across frameworks while allowing framework-specific parameters.

**Sources:** [src/huggingface_hub/hub_mixin.py:381-447](), [src/huggingface_hub/hub_mixin.py:460-583](), [src/huggingface_hub/hub_mixin.py:632-701]()

---

