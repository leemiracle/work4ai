<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/finetrainers · page 9 Extending Finetrainers · fetched 2026-10-26 -->

# Extending Finetrainers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/environment.md](docs/environment.md)
- [docs/models/README.md](docs/models/README.md)
- [docs/models/attention.md](docs/models/attention.md)
- [finetrainers/config.py](finetrainers/config.py)
- [finetrainers/constants.py](finetrainers/constants.py)
- [finetrainers/models/__init__.py](finetrainers/models/__init__.py)
- [finetrainers/models/attention_dispatch.py](finetrainers/models/attention_dispatch.py)
- [finetrainers/models/cogvideox/base_specification.py](finetrainers/models/cogvideox/base_specification.py)
- [finetrainers/models/flux/base_specification.py](finetrainers/models/flux/base_specification.py)
- [finetrainers/models/hunyuan_video/base_specification.py](finetrainers/models/hunyuan_video/base_specification.py)
- [finetrainers/models/ltx_video/base_specification.py](finetrainers/models/ltx_video/base_specification.py)
- [finetrainers/models/wan/base_specification.py](finetrainers/models/wan/base_specification.py)
- [finetrainers/models/wan/control_specification.py](finetrainers/models/wan/control_specification.py)
- [finetrainers/patches/__init__.py](finetrainers/patches/__init__.py)
- [finetrainers/trainer/base.py](finetrainers/trainer/base.py)
- [tests/models/flux/base_specification.py](tests/models/flux/base_specification.py)

</details>



This page provides a technical overview of finetrainers' extension architecture, enabling developers to add new models, custom processors, parallel backends, and attention providers. The library is designed with extensibility as a core principle, using abstract base classes and registry patterns to support diverse diffusion architectures without modifying core training logic.

For step-by-step guides on specific extension tasks:
- Adding a new model: See [Adding a New Model](#9.1)
- Creating custom processors or backends: See [Custom Processors and Backends](#9.2)
- Development tools and contribution workflow: See [Development Workflow](#9.3)

---

## Extension Points Overview

Finetrainers provides four primary extension points, each serving a distinct purpose in the training pipeline:

**Extension Points Architecture**

```mermaid
graph TB
    subgraph "Core Extension Points"
        ModelExt["ModelSpecification<br/>finetrainers/models/modeling_utils.py"]
        ProcessorExt["ProcessorMixin<br/>finetrainers/processors/__init__.py"]
        BackendExt["BaseParallelBackend<br/>finetrainers/parallel/base.py"]
        AttentionExt["@_AttentionProviderRegistry.register<br/>finetrainers/models/attention_dispatch.py"]
    end
    
    subgraph "Registration Mechanisms"
        ModelReg["SUPPORTED_MODEL_CONFIGS<br/>Dict[ModelType, Dict[TrainingType, Type]]"]
        AttentionReg["_AttentionProviderRegistry._providers<br/>Dict[AttentionProvider, Callable]"]
    end
    
    subgraph "Implementation Examples"
        WanSpec["WanModelSpecification"]
        HunyuanSpec["HunyuanVideoModelSpecification"]
        LTXSpec["LTXVideoModelSpecification"]
        
        T5Proc["T5Processor"]
        LatentProc["WanLatentEncodeProcessor"]
        
        PTDBackend["PytorchDTensorParallelBackend"]
        AccelBackend["AccelerateParallelBackend"]
        
        FlashAttn["flash_attn_flash_attention"]
        NativeAttn["_native_attention"]
    end
    
    ModelExt -.extends.-> WanSpec
    ModelExt -.extends.-> HunyuanSpec
    ModelExt -.extends.-> LTXSpec
    
    ProcessorExt -.extends.-> T5Proc
    ProcessorExt -.extends.-> LatentProc
    
    BackendExt -.extends.-> PTDBackend
    BackendExt -.extends.-> AccelBackend
    
    AttentionExt -.registers.-> FlashAttn
    AttentionExt -.registers.-> NativeAttn
    
    ModelReg --> WanSpec
    ModelReg --> HunyuanSpec
    ModelReg --> LTXSpec
    
    AttentionReg --> FlashAttn
    AttentionReg --> NativeAttn
    
    style ModelExt fill:#ffcccc
    style ProcessorExt fill:#ccffcc
    style BackendExt fill:#ccccff
    style AttentionExt fill:#ffffcc
```

**Sources:** [finetrainers/models/modeling_utils.py](), [finetrainers/processors/__init__.py](), [finetrainers/parallel/base.py](), [finetrainers/models/attention_dispatch.py](), [finetrainers/config.py:32-63]()

| Extension Point | Base Class | Purpose | Registration Method |
|-----------------|------------|---------|---------------------|
| **Model** | `ModelSpecification` | Define model architectures, component loading, forward pass, validation | Add to `SUPPORTED_MODEL_CONFIGS` dictionary |
| **Processor** | `ProcessorMixin` | Transform data during preprocessing (text encoding, latent encoding) | Pass list to `ModelSpecification` constructor |
| **Parallel Backend** | `BaseParallelBackend` | Implement distributed training strategies (FSDP, TP, CP) | Specify via `--parallel_backend` CLI argument |
| **Attention** | Decorator + function | Provide optimized attention implementations | `@_AttentionProviderRegistry.register` decorator |

---

## Model Extension Architecture

The `ModelSpecification` interface is the most important extension point, defining how models load components, preprocess data, execute forward passes, and generate validation artifacts.

**ModelSpecification Lifecycle**

```mermaid
graph TB
    Init["ModelSpecification.__init__<br/>Store paths, dtypes, processors"]
    
    subgraph "Component Loading (Initialization Phase)"
        LoadCond["load_condition_models()<br/>Returns: tokenizers, text encoders"]
        LoadLatent["load_latent_models()<br/>Returns: VAE"]
        LoadDiff["load_diffusion_models()<br/>Returns: transformer, scheduler"]
        LoadPipe["load_pipeline()<br/>Assembles DiffusionPipeline"]
    end
    
    subgraph "Data Preparation (Training Loop)"
        PrepCond["prepare_conditions(tokenizer, text_encoder, caption)<br/>Calls: condition_model_processors"]
        PrepLatent["prepare_latents(vae, image/video)<br/>Calls: latent_model_processors"]
    end
    
    subgraph "Training Step"
        Forward["forward(transformer, conditions, latents, sigmas)<br/>Returns: pred, target, sigmas"]
    end
    
    subgraph "Validation"
        Valid["validation(pipeline, prompt, ...)<br/>Returns: List[ArtifactType]"]
    end
    
    subgraph "Checkpointing"
        SaveLora["_save_lora_weights(directory, state_dict, ...)"]
        SaveModel["_save_model(directory, transformer, state_dict, ...)"]
    end
    
    Init --> LoadCond
    Init --> LoadLatent
    Init --> LoadDiff
    LoadCond --> LoadPipe
    LoadLatent --> LoadPipe
    LoadDiff --> LoadPipe
    
    LoadCond -.used by.-> PrepCond
    LoadLatent -.used by.-> PrepLatent
    
    PrepCond --> Forward
    PrepLatent --> Forward
    LoadDiff -.transformer.-> Forward
    
    LoadPipe -.used by.-> Valid
    
    Forward -.after training.-> SaveLora
    Forward -.after training.-> SaveModel
    
    style Init fill:#e1f5ff
    style Forward fill:#ffe1e1
    style Valid fill:#e1ffe1
```

**Sources:** [finetrainers/models/modeling_utils.py](), [finetrainers/models/wan/base_specification.py:210-578](), [finetrainers/models/hunyuan_video/base_specification.py:75-392](), [finetrainers/models/ltx_video/base_specification.py:93-414]()

### Core Methods Required

Each `ModelSpecification` implementation must provide the following methods:

**Component Loading Methods:**
- `load_condition_models()` → `Dict[str, torch.nn.Module]`: Load tokenizers and text encoders
- `load_latent_models()` → `Dict[str, torch.nn.Module]`: Load VAE and related models
- `load_diffusion_models()` → `Dict[str, torch.nn.Module]`: Load transformer/UNet and scheduler
- `load_pipeline()` → `DiffusionPipeline`: Assemble components into inference pipeline

**Data Processing Methods:**
- `prepare_conditions()` → `Dict[str, Any]`: Process captions through text encoders via `condition_model_processors`
- `prepare_latents()` → `Dict[str, torch.Tensor]`: Encode images/videos via `latent_model_processors`

**Training Methods:**
- `forward()` → `Tuple[torch.Tensor, ...]`: Execute diffusion forward pass, return predictions and targets
- `validation()` → `List[ArtifactType]`: Generate validation artifacts using pipeline

**Serialization Methods:**
- `_save_lora_weights()`: Save LoRA adapter weights and scheduler
- `_save_model()`: Save full model weights and scheduler

**Sources:** [finetrainers/models/modeling_utils.py](), [finetrainers/models/wan/base_specification.py:265-330]()

---

## Processor Extension System

Processors transform data during preprocessing, executing operations like text tokenization, latent encoding, and custom conditioning. They are invoked by `ModelSpecification.prepare_conditions()` and `ModelSpecification.prepare_latents()` methods.

**Processor Data Flow**

```mermaid
graph LR
    subgraph "Condition Processors"
        Caption["caption: str"]
        
        T5Proc["T5Processor<br/>output_names=['encoder_hidden_states', 'encoder_attention_mask']"]
        LlamaProc["LlamaProcessor<br/>output_names=['encoder_hidden_states', 'encoder_attention_mask']"]
        CLIPProc["CLIPPooledProcessor<br/>output_names=['pooled_projections']"]
        
        CondOut["Dict[str, torch.Tensor]<br/>encoder_hidden_states, attention_mask, pooled_projections"]
    end
    
    subgraph "Latent Processors"
        ImageVideo["image/video: torch.Tensor"]
        
        WanLatent["WanLatentEncodeProcessor<br/>output_names=['latents', 'latents_mean', 'latents_std']"]
        HunyuanLatent["HunyuanLatentEncodeProcessor<br/>output_names=['latents']"]
        LTXLatent["LTXLatentEncodeProcessor<br/>output_names=['latents', 'num_frames', 'height', 'width', 'latents_mean', 'latents_std']"]
        
        LatentOut["Dict[str, torch.Tensor]<br/>latents, metadata"]
    end
    
    Caption --> T5Proc
    Caption --> LlamaProc
    Caption --> CLIPProc
    
    T5Proc --> CondOut
    LlamaProc --> CondOut
    CLIPProc --> CondOut
    
    ImageVideo --> WanLatent
    ImageVideo --> HunyuanLatent
    ImageVideo --> LTXLatent
    
    WanLatent --> LatentOut
    HunyuanLatent --> LatentOut
    LTXLatent --> LatentOut
```

**Sources:** [finetrainers/processors/__init__.py](), [finetrainers/models/wan/base_specification.py:30-82](), [finetrainers/models/hunyuan_video/base_specification.py:28-73](), [finetrainers/models/ltx_video/base_specification.py:32-91]()

### ProcessorMixin Interface

All processors inherit from `ProcessorMixin` and implement a `forward()` method:

```python
class ProcessorMixin:
    def forward(self, **kwargs) -> Dict[str, Any]:
        """Transform input data and return outputs keyed by self.output_names"""
        raise NotImplementedError
```

**Key Characteristics:**
- `output_names`: List of keys for returned dictionary. Use `"__drop__"` to discard outputs.
- `forward()` signature: Accepts model components and data as keyword arguments
- Return type: `Dict[str, Any]` mapping output_names to processed tensors

**Example Implementation:** [finetrainers/models/wan/base_specification.py:30-82]() shows `WanLatentEncodeProcessor` with three outputs (`latents`, `latents_mean`, `latents_std`)

**Sources:** [finetrainers/processors/__init__.py](), [finetrainers/models/wan/base_specification.py:30-82]()

---

## Model and Training Type Registration

Models are registered in the `SUPPORTED_MODEL_CONFIGS` dictionary, which maps `(ModelType, TrainingType)` tuples to `ModelSpecification` classes.

**Registration System**

```mermaid
graph TB
    subgraph "Enum Definitions"
        ModelType["ModelType(Enum)<br/>COGVIDEOX, COGVIEW4, FLUX,<br/>HUNYUAN_VIDEO, LTX_VIDEO, WAN"]
        TrainingType["TrainingType(Enum)<br/>LORA, FULL_FINETUNE,<br/>CONTROL_LORA, CONTROL_FULL_FINETUNE"]
    end
    
    subgraph "Registry Structure"
        Registry["SUPPORTED_MODEL_CONFIGS<br/>Dict[ModelType, Dict[TrainingType, Type[ModelSpecification]]]"]
    end
    
    subgraph "Example Registrations"
        WanSFT["ModelType.WAN + TrainingType.LORA<br/>→ WanModelSpecification"]
        WanControl["ModelType.WAN + TrainingType.CONTROL_LORA<br/>→ WanControlModelSpecification"]
        HunyuanSFT["ModelType.HUNYUAN_VIDEO + TrainingType.FULL_FINETUNE<br/>→ HunyuanVideoModelSpecification"]
        CogViewControl["ModelType.COGVIEW4 + TrainingType.CONTROL_FULL_FINETUNE<br/>→ CogView4ControlModelSpecification"]
    end
    
    subgraph "Lookup Function"
        GetSpec["_get_model_specifiction_cls(model_name, training_type)<br/>Returns: Type[ModelSpecification]"]
    end
    
    ModelType --> Registry
    TrainingType --> Registry
    
    Registry --> WanSFT
    Registry --> WanControl
    Registry --> HunyuanSFT
    Registry --> CogViewControl
    
    Registry --> GetSpec
    
    GetSpec -.raises ValueError.-> InvalidModel["Model/training type not supported"]
```

**Sources:** [finetrainers/config.py:1-76]()

### Adding a New Model to the Registry

To register a new model:

1. **Define the ModelType** (if new): Add enum value to `ModelType` in [finetrainers/config.py:13-20]()
2. **Implement ModelSpecification**: Create a subclass in `finetrainers/models/<model_name>/base_specification.py`
3. **Register in SUPPORTED_MODEL_CONFIGS**: Add mapping in [finetrainers/config.py:32-63]()

Example registration pattern:
```python
SUPPORTED_MODEL_CONFIGS = {
    ModelType.YOUR_MODEL: {
        TrainingType.LORA: YourModelSpecification,
        TrainingType.FULL_FINETUNE: YourModelSpecification,
        # Optional: control variants
        TrainingType.CONTROL_LORA: YourControlModelSpecification,
        TrainingType.CONTROL_FULL_FINETUNE: YourControlModelSpecification,
    },
}
```

**Sources:** [finetrainers/config.py:32-63](), [finetrainers/config.py:66-76]()

---

## Attention Provider System

The attention provider system enables pluggable attention implementations optimized for different hardware and memory profiles. Providers are registered via decorator and dispatched through `attention_dispatch()`.

**Attention Provider Architecture**

```mermaid
graph TB
    subgraph "Provider Registration"
        Register["@_AttentionProviderRegistry.register<br/>(provider, constraints, supports_cp)"]
        
        FlashReg["@register(AttentionProvider.FLASH)<br/>flash_attn_flash_attention"]
        SageReg["@register(AttentionProvider.SAGE)<br/>sageattn"]
        NativeReg["@register(AttentionProvider.NATIVE)<br/>_native_attention"]
        XFormersReg["@register(AttentionProvider.XFORMERS)<br/>xops.memory_efficient_attention"]
    end
    
    subgraph "Registry State"
        Providers["_providers: Dict[AttentionProvider, Callable]"]
        Constraints["_constraints: Dict[AttentionProvider, List[Callable]]"]
        SupportsCP["_supports_cp: Dict[AttentionProvider, bool]"]
        ActiveProvider["_active_provider: AttentionProvider"]
    end
    
    subgraph "Dispatch Mechanism"
        Dispatcher["attention_dispatch(query, key, value, ...)<br/>Routes to active provider"]
        ContextMgr["attention_provider(provider) context manager<br/>Temporarily switches provider"]
    end
    
    subgraph "Validation"
        CheckDevice["_check_device_cuda"]
        CheckDtype["_check_qkv_dtype_bf16_or_fp16"]
        CheckMask["_check_attn_mask_is_none"]
        CheckShape["_check_shape"]
    end
    
    Register --> FlashReg
    Register --> SageReg
    Register --> NativeReg
    Register --> XFormersReg
    
    FlashReg --> Providers
    SageReg --> Providers
    NativeReg --> Providers
    XFormersReg --> Providers
    
    FlashReg --> Constraints
    SageReg --> Constraints
    
    Constraints -.contains.-> CheckDevice
    Constraints -.contains.-> CheckDtype
    Constraints -.contains.-> CheckMask
    Constraints -.contains.-> CheckShape
    
    Providers --> Dispatcher
    ActiveProvider --> Dispatcher
    
    ContextMgr -.modifies.-> ActiveProvider
    
    Dispatcher -.validates via.-> Constraints
```

**Sources:** [finetrainers/models/attention_dispatch.py:295-448]()

### Registering Custom Attention Providers

To add a custom attention provider:

1. **Define the provider function** with signature compatible with `torch.nn.functional.scaled_dot_product_attention`
2. **Add enum value** to `AttentionProvider` in [finetrainers/models/attention_dispatch.py:265-293]()
3. **Register with decorator**:

```python
@_AttentionProviderRegistry.register(
    AttentionProvider.YOUR_PROVIDER,
    constraints=[_check_device_cuda, _check_qkv_dtype_bf16_or_fp16],
    supports_cp=False
)
def your_attention_function(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attn_mask: Optional[torch.Tensor] = None,
    dropout_p: float = 0.0,
    is_causal: bool = False,
    scale: Optional[float] = None,
) -> torch.Tensor:
    # Your implementation
    pass
```

**Supported Arguments:** The registry tracks which arguments each provider supports via `_supported_arg_names`. Unsupported arguments are automatically filtered out during dispatch.

**Constraints:** Optional validation functions that check tensor properties (device, dtype, shape) before invoking the provider. See [finetrainers/models/attention_dispatch.py:460-521]() for built-in constraint functions.

**Context Parallel Support:** Set `supports_cp=True` if the provider works with sequence dimension sharding. See [docs/models/attention.md]() for CP implementation details.

**Sources:** [finetrainers/models/attention_dispatch.py:295-323](), [finetrainers/models/attention_dispatch.py:765-791](), [finetrainers/models/attention_dispatch.py:405-448]()

---

## Patching System

The patching system modifies upstream library behavior to support advanced features like layerwise upcasting, tensor parallelism, and model-specific optimizations. Patches are applied conditionally based on `args` and `parallel_backend` configuration.

**Patch Application Flow**

```mermaid
graph TB
    Start["perform_patches_for_training(args, parallel_backend)"]
    
    subgraph "Core Patches (Always Applied)"
        SDPAPatch["patch_scaled_dot_product_attention()<br/>torch.nn.functional.scaled_dot_product_attention = attention_dispatch"]
        RMSNormPatch["patch.patch_diffusers_rms_norm_forward()<br/>Optimize RMSNorm for bfloat16"]
    end
    
    subgraph "Model-Specific Patches"
        LTXCheck{"args.model_name == ModelType.LTX_VIDEO"}
        LTXTransformer["patch.patch_transformer_forward()<br/>LTX-specific modifications"]
        LTXTPCheck{"parallel_backend.tensor_parallel_enabled"}
        LTXTP["patch.patch_apply_rotary_emb_for_tp_compatibility()<br/>Fix RoPE for TP"]
        
        WanCheck{"args.model_name == ModelType.WAN AND<br/>'transformer' in layerwise_upcasting_modules"}
        WanPatch["patch.patch_time_text_image_embedding_forward()<br/>Support mixed precision"]
    end
    
    subgraph "Training-Type Patches"
        LoRACheck{"args.training_type == TrainingType.LORA AND<br/>layerwise_upcasting_modules"}
        LoRAPatch["patch.patch_peft_move_adapter_to_device_of_base_layer()<br/>Handle adapter dtype/device"]
    end
    
    Start --> SDPAPatch
    Start --> RMSNormPatch
    
    Start --> LTXCheck
    LTXCheck -->|Yes| LTXTransformer
    LTXTransformer --> LTXTPCheck
    LTXTPCheck -->|Yes| LTXTP
    
    Start --> WanCheck
    WanCheck -->|Yes| WanPatch
    
    Start --> LoRACheck
    LoRACheck -->|Yes| LoRAPatch
```

**Sources:** [finetrainers/patches/__init__.py:13-59]()

### Patch Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Core Patches** | Replace attention dispatch, optimize normalization | `patch_scaled_dot_product_attention()` |
| **Model-Specific** | Fix bugs or enable features for specific architectures | `patch_transformer_forward()` for LTX |
| **Parallelism** | Enable TP/CP compatibility | `patch_apply_rotary_emb_for_tp_compatibility()` |
| **Training Mode** | Support LoRA with mixed precision | `patch_peft_move_adapter_to_device_of_base_layer()` |

**Adding New Patches:**
1. Implement patch function in `finetrainers/patches/models/<model_name>/` or `finetrainers/patches/dependencies/<library>/`
2. Add conditional logic to `perform_patches_for_training()` in [finetrainers/patches/__init__.py:13-44]()
3. Document the patch purpose and conditions in code comments

**Sources:** [finetrainers/patches/__init__.py:13-59]()

---

## Control Model Extensions

`ControlModelSpecification` extends `ModelSpecification` to support conditional generation with additional control channels (e.g., depth maps, pose). It adds control-specific preprocessing and injection logic.

**Control Model Architecture**

```mermaid
graph TB
    subgraph "ControlModelSpecification Extensions"
        ControlInjection["control_injection_layer_name: str<br/>Layer where control is concatenated"]
        ControlProcessors["control_model_processors: List[ProcessorMixin]<br/>Process control inputs"]
        
        LoadDiffControl["load_diffusion_models(new_in_features)<br/>Expand input channels with zeroed weights"]
        PrepLatentsControl["prepare_latents(..., control_image, control_video)<br/>Process both target and control"]
        ForwardControl["forward(...)<br/>Concatenate control latents before diffusion"]
    end
    
    subgraph "Control Injection Mechanism"
        ExpandConv["_expand_conv3d_with_zeroed_weights(layer, new_in_channels)<br/>Preserve pretrained weights"]
        ApplyConditioning["apply_frame_conditioning_on_latents(...)<br/>Frame masking strategies"]
        ControlConcat["control_channel_concat context manager<br/>Runtime concatenation"]
    end
    
    subgraph "Example: Wan Control"
        WanControl["WanControlModelSpecification"]
        WanControlProc["WanLatentEncodeProcessor<br/>output_names=['control_latents', '__drop__', '__drop__']"]
        PatchEmbed["transformer.patch_embedding expanded<br/>in_channels: 16 → 32 (latents + control)"]
    end
    
    ControlInjection --> LoadDiffControl
    LoadDiffControl --> ExpandConv
    
    ControlProcessors --> PrepLatentsControl
    PrepLatentsControl --> ApplyConditioning
    
    ForwardControl --> ControlConcat
    
    WanControl -.implements.-> ControlInjection
    WanControl -.implements.-> ControlProcessors
    WanControl -.uses.-> WanControlProc
    WanControl -.modifies.-> PatchEmbed
```

**Sources:** [finetrainers/models/modeling_utils.py](), [finetrainers/models/wan/control_specification.py:36-438]()

### Key Differences from Base ModelSpecification

**Additional Properties:**
- `control_injection_layer_name`: Name of layer where control is concatenated (e.g., `"patch_embedding"`)
- `control_model_processors`: Processors for control inputs (separate from target latent processors)

**Modified Methods:**
- `load_diffusion_models(new_in_features: int)`: Accepts `new_in_features` to expand input channels
- `prepare_latents()`: Processes both target and control images/videos
- `forward()`: Applies frame conditioning and concatenates control latents

**Frame Conditioning Types:** Defined in `FrameConditioningType` enum:
- `"full"`: Use all control frames
- `"first"`: Use only first frame
- `"last"`: Use only last frame
- `"first_and_last"`: Use first and last frames

**Sources:** [finetrainers/models/wan/control_specification.py:36-438](), [finetrainers/models/utils.py]()

---

## Integration with Training Pipeline

Extensions integrate seamlessly with the training pipeline through standardized interfaces. The following diagram shows how custom components are discovered and invoked.

**Extension Invocation in Training**

```mermaid
graph TB
    subgraph "CLI Entry Point"
        CLI["train.py<br/>--model_name, --training_type"]
    end
    
    subgraph "Model Resolution"
        GetSpec["_get_model_specifiction_cls(model_name, training_type)<br/>Looks up SUPPORTED_MODEL_CONFIGS"]
        InstantiateSpec["ModelSpecification(**args)"]
    end
    
    subgraph "Trainer Initialization"
        InitTrainer["SFTTrainer / ControlTrainer"]
        PrepModels["_prepare_models()<br/>Calls load_condition_models, load_latent_models, load_diffusion_models"]
        PrepTrainable["_prepare_trainable_parameters()<br/>Setup LoRA or full finetuning"]
        PrepTraining["_prepare_for_training()<br/>Apply parallel backend, patches"]
    end
    
    subgraph "Training Loop"
        PrepDataset["_prepare_dataset()<br/>Load data via initialize_dataset"]
        Preprocess["Preprocessor<br/>Invokes prepare_conditions, prepare_latents"]
        Forward["forward(transformer, conditions, latents, sigmas)<br/>Model-specific diffusion step"]
        Loss["Compute loss"]
        Backward["Backward pass"]
    end
    
    subgraph "Validation"
        ValidCheck{"Validation step?"}
        GenArtifacts["validation(pipeline, prompt, ...)<br/>Generate images/videos"]
    end
    
    CLI --> GetSpec
    GetSpec --> InstantiateSpec
    InstantiateSpec --> InitTrainer
    
    InitTrainer --> PrepModels
    PrepModels --> PrepTrainable
    PrepTrainable --> PrepTraining
    
    PrepTraining --> PrepDataset
    PrepDataset --> Preprocess
    Preprocess --> Forward
    Forward --> Loss
    Loss --> Backward
    
    Backward --> ValidCheck
    ValidCheck -->|Yes| GenArtifacts
    ValidCheck -->|No| Preprocess
```

**Sources:** [finetrainers/config.py:66-76](), [finetrainers/trainer/base.py]()

### Attention Provider Context Management

The `Trainer` class manages attention provider switching per module using the `attention_provider_ctx()` context manager. This enables different attention implementations for different components (e.g., Flash Attention for transformer, Native SDPA for VAE).

**Configuration:**
- `--attn_provider_training`: List of `module_name:provider_name` pairs for training
- `--attn_provider_inference`: List of `module_name:provider_name` pairs for validation

**Example:** `--attn_provider_training transformer:flash vae:native` uses Flash Attention for the transformer and native PyTorch SDPA for the VAE.

**Sources:** [finetrainers/trainer/base.py:37-91](), [finetrainers/trainer/base.py:148-160]()

---

## Testing Custom Extensions

When adding custom components, implement unit tests to verify:

1. **Model Components Load Correctly:** Test `load_condition_models()`, `load_latent_models()`, `load_diffusion_models()`
2. **Processors Transform Data:** Verify `forward()` returns expected keys and shapes
3. **Forward Pass Executes:** Ensure `forward()` produces valid predictions and targets
4. **Validation Generates Artifacts:** Check `validation()` returns appropriate `ArtifactType` instances
5. **Serialization Works:** Test `_save_lora_weights()` and `_save_model()` produce loadable checkpoints

**Test Structure Example:** See [tests/models/flux/base_specification.py:1-7]() for a minimal test ModelSpecification using a tiny model.

**Sources:** [tests/models/flux/base_specification.py:1-7](), [docs/models/README.md]()

---

For detailed implementation guides:
- **Adding a new model:** See [Adding a New Model](#9.1)
- **Creating custom processors or backends:** See [Custom Processors and Backends](#9.2)
- **Development tools and contribution workflow:** See [Development Workflow](#9.3)

---

