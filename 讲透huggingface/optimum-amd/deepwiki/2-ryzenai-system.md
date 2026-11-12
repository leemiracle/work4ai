<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-amd · page 2 RyzenAI System · fetched 2026-10-26 -->

# RyzenAI System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/ryzenai/overview.mdx](docs/source/ryzenai/overview.mdx)
- [optimum/amd/ryzenai/__init__.py](optimum/amd/ryzenai/__init__.py)
- [optimum/amd/ryzenai/modeling.py](optimum/amd/ryzenai/modeling.py)
- [optimum/amd/ryzenai/utils.py](optimum/amd/ryzenai/utils.py)

</details>



The RyzenAI System provides optimized inference for Hugging Face models on AMD Ryzen AI NPU hardware using the VitisAI execution provider within ONNX Runtime. This system handles the complete workflow from ONNX model loading to hardware-accelerated inference for computer vision tasks.

For details on model quantization specific to RyzenAI, see [Quantization](#2.2). For high-level pipeline interfaces, see [Pipelines](#2.3). For runtime configuration options, see [Configuration](#2.4). For detailed model implementation and inference mechanics, see [Models and Inference](#2.1).

## System Architecture

The RyzenAI system bridges Hugging Face models with AMD NPU hardware through a layered architecture:

```mermaid
graph TB
    subgraph "Input Layer"
        HF_Model["🤗 Transformers Model"]
        ONNX_Model["ONNX Model"]
        Timm_Model["TIMM Model"]
    end
    
    subgraph "RyzenAI Core Classes"
        RyzenAIModel["RyzenAIModel"]
        CustomTasks["RyzenAIModelForCustomTasks"]
        ImageClass["RyzenAIModelForImageClassification"]
        ObjectDet["RyzenAIModelForObjectDetection"]
        Segmentation["RyzenAIModelForSemanticSegmentation"]
    end
    
    subgraph "ONNX Runtime Layer"
        Session["ort.InferenceSession"]
        VitisAI["VitisAIExecutionProvider"]
    end
    
    subgraph "Hardware Layer"
        NPU["AMD Ryzen AI NPU"]
        XDNA["XDNA Architecture"]
    end
    
    subgraph "Configuration System"
        VAIP["vaip_config.json"]
        DEFAULT_VAIP["DEFAULT_VAIP_CONFIG"]
    end
    
    HF_Model --> RyzenAIModel
    ONNX_Model --> RyzenAIModel
    Timm_Model --> RyzenAIModel
    
    RyzenAIModel --> CustomTasks
    RyzenAIModel --> ImageClass
    RyzenAIModel --> ObjectDet
    RyzenAIModel --> Segmentation
    
    CustomTasks --> Session
    ImageClass --> Session
    ObjectDet --> Session
    Segmentation --> Session
    
    Session --> VitisAI
    VitisAI --> NPU
    NPU --> XDNA
    
    VAIP --> VitisAI
    DEFAULT_VAIP --> VAIP
```

Sources: [optimum/amd/ryzenai/modeling.py:47-70](), [optimum/amd/ryzenai/modeling.py:568-701](), [optimum/amd/ryzenai/utils.py:13]()

## Core Components

### RyzenAIModel Base Class

The `RyzenAIModel` class serves as the foundation for all RyzenAI model implementations:

| Component | Code Entity | Purpose |
|-----------|-------------|---------|
| Base Model | `RyzenAIModel` | Abstract base class with common functionality |
| ONNX Session | `ort.InferenceSession` | ONNX Runtime inference session |
| Provider | `VitisAIExecutionProvider` | AMD NPU execution provider |
| Configuration | `vaip_config` | Runtime configuration for VitisAI |

The class hierarchy establishes shared attributes and methods for model loading, configuration management, and hardware integration.

Sources: [optimum/amd/ryzenai/modeling.py:47-135]()

### Task-Specific Model Classes

```mermaid
graph TD
    RyzenAIModel["RyzenAIModel<br/>(Base Class)"]
    
    CustomTasks["RyzenAIModelForCustomTasks<br/>(Generic Implementation)"]
    ImageClass["RyzenAIModelForImageClassification<br/>(AutoModelForImageClassification)"]
    ObjectDet["RyzenAIModelForObjectDetection<br/>(Object Detection Tasks)"]
    ImageSeg["RyzenAIModelForImageSegmentation<br/>(Image Segmentation)"]
    SemanticSeg["RyzenAIModelForSemanticSegmentation<br/>(Semantic Segmentation)"]
    ImageToImage["RyzenAIModelForImageToImage<br/>(Image-to-Image Tasks)"]
    
    RyzenAIModel --> CustomTasks
    CustomTasks --> ImageClass
    CustomTasks --> ObjectDet
    ObjectDet --> ImageSeg
    ObjectDet --> SemanticSeg
    ObjectDet --> ImageToImage
```

Each task-specific class implements the `forward()` method optimized for its particular use case while inheriting common functionality from the base classes.

Sources: [optimum/amd/ryzenai/modeling.py:568-701]()

## Model Loading and Initialization

### Loading Workflow

```mermaid
graph TD
    from_pretrained["RyzenAIModel.from_pretrained()"]
    
    subgraph "Model Discovery"
        check_files["TasksManager.get_model_files()"]
        config_load["AutoConfig.from_pretrained()"]
        file_discovery["_generate_regular_names_for_filename()"]
    end
    
    subgraph "Provider Setup"
        validate["validate_provider_availability()"]
        provider_options["provider_options configuration"]
        vaip_setup["vaip_config path resolution"]
    end
    
    subgraph "Model Loading"
        load_model["RyzenAIModel.load_model()"]
        ort_session["ort.InferenceSession()"]
        static_check["_check_uses_static_shape()"]
    end
    
    subgraph "Instance Creation"
        shared_init["shared_attributes_init()"]
        inputs_outputs["inputs_names/output_names mapping"]
    end
    
    from_pretrained --> check_files
    from_pretrained --> config_load
    from_pretrained --> file_discovery
    
    check_files --> validate
    config_load --> provider_options
    file_discovery --> vaip_setup
    
    validate --> load_model
    provider_options --> ort_session
    vaip_setup --> static_check
    
    load_model --> shared_init
    ort_session --> inputs_outputs
    static_check --> shared_init
```

The loading process validates provider availability, resolves configuration paths, performs static shape checking, and initializes the ONNX Runtime session with VitisAI provider.

Sources: [optimum/amd/ryzenai/modeling.py:227-508](), [optimum/amd/ryzenai/modeling.py:144-189]()

### Key Loading Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `provider` | `"VitisAIExecutionProvider"` | ONNX Runtime execution provider |
| `vaip_config` | `DEFAULT_VAIP_CONFIG` | VitisAI runtime configuration |
| `file_name` | Auto-detected | ONNX model filename |
| `provider_options` | `None` | Provider-specific options |

Sources: [optimum/amd/ryzenai/modeling.py:240-297](), [optimum/amd/ryzenai/utils.py:13]()

## Execution Flow

### Inference Pipeline

The inference execution follows a standardized pattern across all task-specific models:

```mermaid
graph LR
    input["Input Tensors"]
    
    subgraph "Preprocessing"
        torch_check["isinstance(input, torch.Tensor)"]
        numpy_convert["tensor.cpu().detach().numpy()"]
        onnx_inputs["onnx_inputs dict preparation"]
    end
    
    subgraph "Inference"
        session_run["model.run(None, onnx_inputs)"]
        ort_execution["ONNX Runtime + VitisAI"]
    end
    
    subgraph "Postprocessing"
        output_mapping["output_names index mapping"]
        torch_convert["torch.from_numpy()"]
        model_output["ModelOutput/ImageClassifierOutput"]
    end
    
    input --> torch_check
    torch_check --> numpy_convert
    numpy_convert --> onnx_inputs
    onnx_inputs --> session_run
    session_run --> ort_execution
    ort_execution --> output_mapping
    output_mapping --> torch_convert
    torch_convert --> model_output
```

Sources: [optimum/amd/ryzenai/modeling.py:569-601](), [optimum/amd/ryzenai/modeling.py:607-619]()

### Static Shape Requirements

The system enforces static input/output shapes for VitisAI compatibility:

- Dynamic axes detection via `_check_uses_static_shape()`
- Shape validation during model loading
- Runtime error for models with dynamic dimensions
- Shape reshaping support via `reshape()` method

Sources: [optimum/amd/ryzenai/modeling.py:511-565]()

## Model Export and Compatibility

### Export Capabilities

The system provides export functionality for select model types:

```mermaid
graph TD
    export["_export() method"]
    
    subgraph "Export Configuration"
        temp_dir["TemporaryDirectory()"]
        main_export["main_export() from optimum"]
        export_params["task='image-classification'<br/>opset=17<br/>batch_size=1<br/>no_dynamic_axes=True"]
    end
    
    subgraph "Post-Export Loading"
        from_pretrained["_from_pretrained()"]
        model_instance["RyzenAIModel instance"]
    end
    
    export --> temp_dir
    temp_dir --> main_export
    main_export --> export_params
    export_params --> from_pretrained
    from_pretrained --> model_instance
```

Export is currently supported for `RyzenAIModelForImageClassification` with specific constraints for NPU compatibility.

Sources: [optimum/amd/ryzenai/modeling.py:622-673]()

---

