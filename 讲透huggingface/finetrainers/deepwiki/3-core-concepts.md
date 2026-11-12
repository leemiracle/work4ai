<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/finetrainers · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [docs/models/README.md](docs/models/README.md)
- [finetrainers/config.py](finetrainers/config.py)
- [finetrainers/functional/__init__.py](finetrainers/functional/__init__.py)
- [finetrainers/functional/text.py](finetrainers/functional/text.py)
- [finetrainers/models/cogvideox/base_specification.py](finetrainers/models/cogvideox/base_specification.py)
- [finetrainers/models/flux/base_specification.py](finetrainers/models/flux/base_specification.py)
- [finetrainers/models/hunyuan_video/base_specification.py](finetrainers/models/hunyuan_video/base_specification.py)
- [finetrainers/models/ltx_video/base_specification.py](finetrainers/models/ltx_video/base_specification.py)
- [finetrainers/models/wan/base_specification.py](finetrainers/models/wan/base_specification.py)
- [finetrainers/models/wan/control_specification.py](finetrainers/models/wan/control_specification.py)
- [tests/models/flux/base_specification.py](tests/models/flux/base_specification.py)

</details>



This document explains the fundamental architectural concepts that underpin finetrainers: the `ModelType` and `TrainingType` enums, the `ModelSpecification` interface, and how these components interact to enable training of diverse diffusion models with different training strategies.

For specific details on training approaches (LoRA vs full finetuning, SFT vs Control), see [Training Types](#3.1). For deep implementation details of the `ModelSpecification` abstraction, see [Model Specifications](#3.2). For configuration and command-line argument handling, see [Configuration System](#3.3).

## Core Architectural Concepts

Finetrainers is built around three key abstractions that enable extensible, multi-model training:

1. **ModelType**: An enumeration identifying which diffusion model architecture to train
2. **TrainingType**: An enumeration specifying the training strategy (LoRA, full finetune, control conditioning)
3. **ModelSpecification**: An abstract interface that defines how to load, prepare, and train each model

### ModelType and TrainingType Enums

The `ModelType` enum defines all supported model architectures:

```python
class ModelType(str, Enum):
    COGVIDEOX = "cogvideox"
    COGVIEW4 = "cogview4"
    FLUX = "flux"
    HUNYUAN_VIDEO = "hunyuan_video"
    LTX_VIDEO = "ltx_video"
    WAN = "wan"
```

The `TrainingType` enum defines all supported training strategies:

```python
class TrainingType(str, Enum):
    # Supervised Fine-Tuning (SFT)
    LORA = "lora"                           # Low-rank adaptation
    FULL_FINETUNE = "full-finetune"         # Full parameter training
    
    # Control Training
    CONTROL_LORA = "control-lora"           # LoRA with control conditioning
    CONTROL_FULL_FINETUNE = "control-full-finetune"  # Full finetune with control
```

These enums serve as keys in the `SUPPORTED_MODEL_CONFIGS` registry, which maps `(ModelType, TrainingType)` pairs to their corresponding `ModelSpecification` implementation classes.

**Sources:** [finetrainers/config.py:13-30]()

### The Registry Pattern

The `SUPPORTED_MODEL_CONFIGS` dictionary is the central registry that connects models and training types to their implementations:

```python
SUPPORTED_MODEL_CONFIGS = {
    ModelType.COGVIDEOX: {
        TrainingType.LORA: CogVideoXModelSpecification,
        TrainingType.FULL_FINETUNE: CogVideoXModelSpecification,
    },
    ModelType.WAN: {
        TrainingType.LORA: WanModelSpecification,
        TrainingType.FULL_FINETUNE: WanModelSpecification,
        TrainingType.CONTROL_LORA: WanControlModelSpecification,
        TrainingType.CONTROL_FULL_FINETUNE: WanControlModelSpecification,
    },
    # ... other models
}
```

This registry enables dynamic dispatch: given `--model_name wan --training_type control-lora`, the system automatically instantiates `WanControlModelSpecification` without hard-coded conditionals in the trainer logic.

**Sources:** [finetrainers/config.py:32-63]()

## The ModelSpecification Interface

The `ModelSpecification` abstract base class defines a standardized interface that all model implementations must follow. This abstraction is what enables finetrainers to support diverse models with a single training codebase.

### Key Responsibilities

Each `ModelSpecification` implementation must define:

| Method | Purpose |
|--------|---------|
| `load_condition_models()` | Load tokenizers and text encoders for caption conditioning |
| `load_latent_models()` | Load VAE for image/video encoding |
| `load_diffusion_models()` | Load the transformer/UNet and scheduler |
| `load_pipeline()` | Assemble components into a Diffusers pipeline |
| `prepare_conditions()` | Process text captions into embeddings |
| `prepare_latents()` | Encode images/videos into latent space |
| `forward()` | Execute the training forward pass (noise prediction) |
| `validation()` | Generate artifacts during validation |

### Processor Architecture

Model specifications use **processors** (`ProcessorMixin` implementations) to modularize data transformations:

- **Condition Model Processors**: Transform text captions into embeddings (e.g., `T5Processor`, `CLIPPooledProcessor`)
- **Latent Model Processors**: Encode images/videos into latents (e.g., `WanLatentEncodeProcessor`, `LTXLatentEncodeProcessor`)
- **Control Model Processors**: Process control conditioning signals (only for control training)

This processor pattern enables composition and reuse. For example, both HunyuanVideo and LTX-Video use `T5Processor` for text encoding, but with different output names and parameters.

**Sources:** [finetrainers/models/wan/base_specification.py:210-260](), [finetrainers/models/ltx_video/base_specification.py:93-131](), [finetrainers/models/hunyuan_video/base_specification.py:75-122]()

## Model Specification Hierarchy

```mermaid
classDiagram
    class ModelSpecification {
        <<abstract>>
        +load_condition_models() Dict
        +load_latent_models() Dict
        +load_diffusion_models() Dict
        +load_pipeline() Pipeline
        +prepare_conditions() Dict
        +prepare_latents() Dict
        +forward() Tuple
        +validation() List
        +condition_model_processors List
        +latent_model_processors List
    }
    
    class ControlModelSpecification {
        <<abstract>>
        +control_model_processors List
        +load_diffusion_models(new_in_features) Dict
        +control_injection_layer_name str
    }
    
    class WanModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    class WanControlModelSpecification {
        +forward() returns pred, target, sigmas
        +control_injection_layer_name "patch_embedding"
    }
    
    class CogVideoXModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    class LTXVideoModelSpecification {
        +forward() returns pred, target, sigmas
        +apply_tensor_parallel()
    }
    
    class HunyuanVideoModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    class FluxModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    class CogView4ModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    class CogView4ControlModelSpecification {
        +forward() returns pred, target, sigmas
    }
    
    ModelSpecification <|-- WanModelSpecification
    ModelSpecification <|-- CogVideoXModelSpecification
    ModelSpecification <|-- LTXVideoModelSpecification
    ModelSpecification <|-- HunyuanVideoModelSpecification
    ModelSpecification <|-- FluxModelSpecification
    ModelSpecification <|-- CogView4ModelSpecification
    ModelSpecification <|-- ControlModelSpecification
    ControlModelSpecification <|-- WanControlModelSpecification
    ControlModelSpecification <|-- CogView4ControlModelSpecification
```

**Sources:** [finetrainers/config.py:1-11](), [finetrainers/models/wan/base_specification.py:210-261](), [finetrainers/models/wan/control_specification.py:36-77]()

## Registry Lookup and Instantiation

```mermaid
graph TB
    CLI["python train.py<br/>--model_name wan<br/>--training_type control-lora"] --> Parse["Parse Arguments<br/>BaseArgs"]
    
    Parse --> Lookup["_get_model_specifiction_cls()<br/>model_name, training_type"]
    
    Lookup --> Registry["SUPPORTED_MODEL_CONFIGS<br/>{ModelType.WAN: {...}}"]
    
    Registry --> Check1{ModelType<br/>exists?}
    Check1 -->|No| Error1["ValueError:<br/>Model not supported"]
    Check1 -->|Yes| Check2{TrainingType<br/>exists?}
    
    Check2 -->|No| Error2["ValueError:<br/>Training type not supported"]
    Check2 -->|Yes| GetClass["Return:<br/>WanControlModelSpecification"]
    
    GetClass --> Instantiate["model_spec = SpecClass(<br/>pretrained_model_name_or_path,<br/>tokenizer_id, text_encoder_id,<br/>transformer_id, vae_id,<br/>*_dtype, revision, cache_dir<br/>)"]
    
    Instantiate --> LoadModels["model_spec.load_condition_models()<br/>model_spec.load_latent_models()<br/>model_spec.load_diffusion_models()"]
    
    LoadModels --> Trainer["SFTTrainer or ControlTrainer<br/>with model_spec"]
    
    style Registry fill:#f9f9f9
    style GetClass fill:#e8f5e9
    style Instantiate fill:#fff3e0
```

**Sources:** [finetrainers/config.py:66-75](), [finetrainers/models/wan/control_specification.py:36-76]()

## Component Lifecycle and Data Flow

The following diagram shows how `ModelType`, `TrainingType`, and `ModelSpecification` interact during the training lifecycle:

```mermaid
sequenceDiagram
    participant CLI as train.py CLI
    participant Config as BaseArgs
    participant Registry as SUPPORTED_MODEL_CONFIGS
    participant Spec as ModelSpecification
    participant Trainer as SFTTrainer/ControlTrainer
    
    CLI->>Config: Parse --model_name, --training_type
    Config->>Registry: _get_model_specifiction_cls(model_name, training_type)
    Registry-->>Config: Return SpecificationClass
    Config->>Spec: Instantiate with pretrained_model_name_or_path, etc.
    
    Note over Spec: Initialization sets up processors
    
    Trainer->>Spec: load_condition_models()
    Spec-->>Trainer: {tokenizer, text_encoder, ...}
    
    Trainer->>Spec: load_latent_models()
    Spec-->>Trainer: {vae}
    
    Trainer->>Spec: load_diffusion_models()
    Spec-->>Trainer: {transformer, scheduler}
    
    Note over Trainer: Training Loop Starts
    
    loop Each Batch
        Trainer->>Spec: prepare_conditions(tokenizer, text_encoder, caption)
        Spec-->>Trainer: {encoder_hidden_states, ...}
        
        Trainer->>Spec: prepare_latents(vae, image/video)
        Spec-->>Trainer: {latents, ...}
        
        Trainer->>Spec: forward(transformer, conditions, latents, sigmas)
        Spec-->>Trainer: pred, target, sigmas
        
        Note over Trainer: Compute loss, backward, optimizer step
    end
    
    alt Validation Step
        Trainer->>Spec: load_pipeline(tokenizer, text_encoder, transformer, vae)
        Spec-->>Trainer: Pipeline instance
        
        Trainer->>Spec: validation(pipeline, prompt, height, width, ...)
        Spec-->>Trainer: [VideoArtifact]
    end
```

**Sources:** [finetrainers/models/wan/base_specification.py:383-432](), [finetrainers/models/ltx_video/base_specification.py:227-345]()

## Model-Specific Component Loading

Each `ModelSpecification` implementation loads model-specific components with configurable dtype and optional overrides:

```mermaid
graph LR
    subgraph "WanModelSpecification.load_condition_models()"
        Wan1["AutoTokenizer.from_pretrained(<br/>pretrained_model_name_or_path,<br/>subfolder='tokenizer')"]
        Wan2["UMT5EncoderModel.from_pretrained(<br/>pretrained_model_name_or_path,<br/>subfolder='text_encoder',<br/>torch_dtype=text_encoder_dtype)"]
    end
    
    subgraph "HunyuanVideoModelSpecification.load_condition_models()"
        Hunyuan1["AutoTokenizer (LLaMA)"]
        Hunyuan2["CLIPTokenizer"]
        Hunyuan3["LlamaModel (text_encoder)"]
        Hunyuan4["CLIPTextModel (text_encoder_2)"]
    end
    
    subgraph "LTXVideoModelSpecification.load_condition_models()"
        LTX1["T5Tokenizer"]
        LTX2["T5EncoderModel"]
    end
    
    subgraph "Common Pattern"
        Pattern1["if tokenizer_id is not None:<br/>    load from tokenizer_id<br/>else:<br/>    load from pretrained_model_name_or_path<br/>    subfolder='tokenizer'"]
        Pattern2["Same pattern for<br/>text_encoder_id,<br/>transformer_id,<br/>vae_id"]
    end
    
    Wan1 --> Pattern1
    Wan2 --> Pattern2
    Hunyuan1 --> Pattern1
    LTX1 --> Pattern1
```

This pattern enables:
1. **Default loading**: Components loaded from the pretrained model path
2. **Component override**: Users can specify `--tokenizer_id`, `--text_encoder_id`, etc. to use custom components
3. **Mixed-precision**: Each component can have its own dtype (`text_encoder_dtype`, `transformer_dtype`, `vae_dtype`)

**Sources:** [finetrainers/models/wan/base_specification.py:265-287](), [finetrainers/models/hunyuan_video/base_specification.py:127-173](), [finetrainers/models/ltx_video/base_specification.py:137-159]()

## Processor Pattern

Processors encapsulate data transformations and enable composition. Each processor implements a `forward()` method that takes models and data as input and returns named outputs.

### Example: Text Processing Chain

```mermaid
graph TB
    Caption["caption: str<br/>'A cat playing piano'"] --> T5Proc["T5Processor<br/>output_names: ['encoder_hidden_states',<br/>'encoder_attention_mask']"]
    
    T5Proc --> Tokenize["tokenizer(caption,<br/>max_length=max_sequence_length,<br/>truncation=True,<br/>padding='max_length',<br/>return_tensors='pt')"]
    
    Tokenize --> Encode["text_encoder(<br/>input_ids,<br/>attention_mask)"]
    
    Encode --> Output["{<br/>  'encoder_hidden_states': Tensor[B, L, D],<br/>  'encoder_attention_mask': Tensor[B, L]<br/>}"]
    
    style Caption fill:#fff3e0
    style Output fill:#e8f5e9
```

### Example: Latent Encoding Chain

```mermaid
graph TB
    Video["video: Tensor[B, F, C, H, W]"] --> Processor["WanLatentEncodeProcessor<br/>output_names: ['latents',<br/>'latents_mean', 'latents_std']"]
    
    Processor --> Permute["video.permute(0, 2, 1, 3, 4)<br/>[B, F, C, H, W] → [B, C, F, H, W]"]
    
    Permute --> Choice{compute_posterior?}
    
    Choice -->|True| Encode1["vae.encode(video)<br/>.latent_dist.sample(generator)"]
    Choice -->|False| Encode2["vae._encode(video)<br/>returns moments"]
    
    Encode1 --> Output
    Encode2 --> Output
    
    Output["{<br/>  'latents': Tensor[B, C, F, H, W],<br/>  'latents_mean': Tensor[C],<br/>  'latents_std': Tensor[C]<br/>}"]
    
    style Video fill:#fff3e0
    style Output fill:#e8f5e9
```

The processor pattern provides several benefits:
- **Modularity**: Each transformation is self-contained
- **Reusability**: Processors can be shared across models (e.g., `T5Processor` used by multiple models)
- **Composability**: Multiple processors can be chained together
- **Testability**: Each processor can be tested independently

**Sources:** [finetrainers/models/wan/base_specification.py:30-81](), [finetrainers/processors/t5_processor.py]() (referenced but not provided)

## Training Type Dispatch

The choice between `SFTTrainer` and `ControlTrainer` is determined by the `TrainingType`:

| TrainingType | Trainer Class | Key Difference |
|--------------|---------------|----------------|
| `LORA` | `SFTTrainer` | Standard supervised fine-tuning with LoRA adapters |
| `FULL_FINETUNE` | `SFTTrainer` | Standard supervised fine-tuning with all parameters |
| `CONTROL_LORA` | `ControlTrainer` | Control conditioning with LoRA adapters + channel concat |
| `CONTROL_FULL_FINETUNE` | `ControlTrainer` | Control conditioning with all parameters + channel concat |

Control training requires a `ControlModelSpecification` which extends `ModelSpecification` with:
- `control_model_processors`: Processors for control signal encoding
- Modified `load_diffusion_models(new_in_features)`: Expands input channels for control concatenation
- `control_injection_layer_name`: Identifies where to inject control signals (e.g., `"patch_embedding"`)

**Sources:** [finetrainers/config.py:22-30](), [finetrainers/models/wan/control_specification.py:36-84]()

## Forward Pass Structure

All model specifications implement a `forward()` method that follows this general structure:

1. **Extract latents** from `latent_model_conditions` (either pre-sampled or sample from posterior)
2. **Normalize/scale latents** according to model-specific requirements
3. **Generate noise** using the provided generator
4. **Create noisy latents** using flow matching or DDPM noise scheduling
5. **Call transformer** with noisy latents, conditions, and timesteps
6. **Compute target** (either noise or velocity depending on the model)
7. **Return** prediction, target, and sigmas for loss computation

### Example: Wan Forward Pass

The Wan model uses flow matching with latent normalization:

```python
def forward(self, transformer, condition_model_conditions, 
            latent_model_conditions, sigmas, generator, ...):
    # 1. Sample latents from posterior
    mu, logvar = torch.chunk(latents, 2, dim=1)
    mu = self._normalize_latents(mu, latents_mean, latents_std)
    latents = DiagonalGaussianDistribution(...).sample(generator)
    
    # 2. Flow matching
    noise = torch.zeros_like(latents).normal_(generator=generator)
    noisy_latents = FF.flow_match_xt(latents, noise, sigmas)
    
    # 3. Forward through transformer
    pred = transformer(
        hidden_states=noisy_latents,
        encoder_hidden_states=condition_model_conditions["encoder_hidden_states"],
        timestep=timesteps,
        return_dict=False,
    )[0]
    
    # 4. Compute target
    target = FF.flow_match_target(noise, latents)
    
    return pred, target, sigmas
```

**Sources:** [finetrainers/models/wan/base_specification.py:433-493](), [finetrainers/models/ltx_video/base_specification.py:271-345](), [finetrainers/models/cogvideox/base_specification.py:258-333]()

## Configuration Integration

The configuration system connects user-provided command-line arguments to `ModelSpecification` instantiation:

```mermaid
graph TB
    Args["--model_name wan<br/>--training_type lora<br/>--pretrained_model_name_or_path Wan-AI/Wan2.1-T2V-1.3B-Diffusers<br/>--tokenizer_id (optional)<br/>--text_encoder_id (optional)<br/>--transformer_id (optional)<br/>--vae_id (optional)<br/>--text_encoder_dtype bfloat16<br/>--transformer_dtype bfloat16<br/>--vae_dtype bfloat16"] --> BaseArgs["BaseArgs.from_cli_args()"]
    
    BaseArgs --> Validate["Validate model_name in ModelType<br/>Validate training_type in TrainingType"]
    
    Validate --> GetCls["spec_cls = _get_model_specifiction_cls(<br/>model_name, training_type)"]
    
    GetCls --> Instantiate["model_spec = spec_cls(<br/>pretrained_model_name_or_path=args.pretrained_model_name_or_path,<br/>tokenizer_id=args.tokenizer_id,<br/>text_encoder_id=args.text_encoder_id,<br/>transformer_id=args.transformer_id,<br/>vae_id=args.vae_id,<br/>text_encoder_dtype=args.text_encoder_dtype,<br/>transformer_dtype=args.transformer_dtype,<br/>vae_dtype=args.vae_dtype,<br/>revision=args.revision,<br/>cache_dir=args.cache_dir<br/>)"]
    
    Instantiate --> Return["Return model_spec to trainer"]
    
    style Args fill:#fff3e0
    style Return fill:#e8f5e9
```

The modular configuration system is detailed in [Configuration System](#3.3).

**Sources:** [finetrainers/config.py:66-75]()

## Extensibility

Adding a new model requires:

1. **Implement `ModelSpecification`**: Create a subclass defining all required methods
2. **Implement processors**: Create `ProcessorMixin` subclasses for model-specific data transformations
3. **Register in `SUPPORTED_MODEL_CONFIGS`**: Add entries mapping `(ModelType, TrainingType)` to your specification
4. **Add to `ModelType` enum**: Define a new enum value for your model

For control training, additionally implement `ControlModelSpecification` with control-specific methods.

See [Adding a New Model](#9.1) for a step-by-step guide.

**Sources:** [finetrainers/config.py:32-75](), [finetrainers/models/wan/base_specification.py:210-261](), [finetrainers/models/wan/control_specification.py:36-84]()

---

