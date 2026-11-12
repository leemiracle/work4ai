<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/diffusion-audio-restoration · page 6 Technical Reference · fetched 2026-10-26 -->

# Technical Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [A2SB_lightning_module.py](A2SB_lightning_module.py)
- [A2SB_lightning_module_api.py](A2SB_lightning_module_api.py)

</details>



## Purpose and Scope

This technical reference provides detailed documentation of the A2SB codebase implementation, covering the core modules, classes, methods, and their interactions. This page serves as an entry point to understanding the code architecture at a detailed level.

The reference is organized into specialized sub-pages covering different aspects of the implementation:
- Lightning module implementations - see [Lightning Modules](#6.1)
- Audio processing and transformation pipeline - see [Audio Processing Pipeline](#6.2)
- Neural network architecture details - see [Model Architecture Details](#6.3)
- Diffusion algorithm implementation - see [Diffusion Process Implementation](#6.4)
- STFT utilities and phase representations - see [STFT and SO(2) Phase Utilities](#6.5)
- Transform class reference - see [Audio Transforms Reference](#6.6)

For high-level architectural concepts and theory, see [Architecture and Core Concepts](#5).

## Module Organization

The A2SB codebase is organized into distinct modules with clear responsibilities. The following diagram maps the primary Python modules to their roles in the system:

```mermaid
graph TB
    subgraph "Entry Points"
        main["main.py<br/>CLI Training Entry"]
        upsample_api["inference/A2SB_upsample_api.py<br/>Single File BWE"]
        upsample_dataset["inference/A2SB_upsample_dataset.py<br/>Batch BWE"]
        inpaint_dataset["inference/A2SB_inpaint_dataset.py<br/>Batch Inpainting"]
    end
    
    subgraph "Lightning Modules"
        train_module["A2SB_lightning_module.py<br/>STFTBridgeModel<br/>LogValidationInpaintingSTFTCallback"]
        api_module["A2SB_lightning_module_api.py<br/>TimePartitionedPretrainedSTFTBridgeModel"]
    end
    
    subgraph "Core Algorithms"
        networks["networks.py<br/>AttnUNetF<br/>SinusoidalTemporalEmbedding"]
        diffusion["diffusion.py<br/>Diffusion class<br/>q_sample, p_posterior"]
    end
    
    subgraph "Audio Processing"
        audio_utils["audio_utils.py<br/>STFT functions<br/>SO2 phase conversion"]
        transforms["audio_transforms/transforms.py<br/>ComplexSpectrogram<br/>MagInstPhase<br/>Griffin-Lim"]
    end
    
    subgraph "Configuration"
        configs["configs/*.yaml<br/>Model params<br/>Training settings"]
    end
    
    main --> train_module
    main --> configs
    
    upsample_api --> api_module
    upsample_dataset --> api_module
    inpaint_dataset --> api_module
    
    train_module --> networks
    train_module --> diffusion
    train_module --> transforms
    train_module --> audio_utils
    
    api_module --> networks
    api_module --> diffusion
    api_module --> transforms
    api_module --> audio_utils
    
    networks --> diffusion
    transforms --> audio_utils
```

**Sources:** [A2SB_lightning_module.py:1-531](), [A2SB_lightning_module_api.py:1-535]()

## Core Lightning Modules

The system implements two primary PyTorch Lightning modules that share common components but serve different purposes:

### Module Comparison

| Aspect | `STFTBridgeModel` | `TimePartitionedPretrainedSTFTBridgeModel` |
|--------|-------------------|---------------------------------------------|
| **File** | A2SB_lightning_module.py | A2SB_lightning_module_api.py |
| **Purpose** | Training and validation | Inference with ensemble models |
| **VF Models** | Single `vf_model` | Multiple models in `t_bounded_pretrained_models` |
| **Timestep Handling** | Random sampling via `sample_t_bounded()` | Model selection via `get_vf_model(t)` |
| **Optimizer** | Configured (RAdam) | None (inference only) |
| **Key Methods** | `training_step()`, `validation_step()` | `predict_step()`, `ddpm_sample()` |
| **Multidiffusion** | Not implemented | Full support with padding/unpadding |
| **Fast Inpainting** | Not implemented | Optional `fast_inpaint_ddpm_sample()` |

**Sources:** [A2SB_lightning_module.py:208-477](), [A2SB_lightning_module_api.py:35-210]()

### Class Hierarchy and Relationships

```mermaid
classDiagram
    class LightningModule {
        <<PyTorch Lightning>>
    }
    
    class STFTBridgeModel {
        +vf_model: Module
        +ddpm: Diffusion
        +t_to_emb: SinusoidalTemporalEmbedding
        +inv_transforms: list
        +train_t_min: float
        +train_t_max: float
        +configure_optimizers()
        +training_step()
        +validation_step()
        +test_step()
        +ddpm_sample()
        +vocode_stft()
        +sample_t_bounded()
    }
    
    class TimePartitionedPretrainedSTFTBridgeModel {
        +vf_model: Module
        +ddpm: Diffusion
        +t_to_emb: SinusoidalTemporalEmbedding
        +t_bounded_pretrained_models: ModuleList
        +t_cutoffs: List[float]
        +fast_inpaint_mode: bool
        +predict_win_length: int
        +predict_hop_length: int
        +load_t_bounded_checkpoints()
        +get_vf_model(t)
        +predict_step()
        +ddpm_sample()
        +fast_inpaint_ddpm_sample()
        +vocode_stft()
    }
    
    class Diffusion {
        +beta_max: float
        +q_sample()
        +p_posterior()
        +get_pred_x0()
        +get_std_t()
        +get_std_fwd()
        +get_std_rev()
    }
    
    class SinusoidalTemporalEmbedding {
        +n_bands: int
        +min_freq: float
        +forward(t)
    }
    
    class AttnUNetF {
        <<Vector Field Model>>
        +forward(x, t_emb)
    }
    
    LightningModule <|-- STFTBridgeModel
    LightningModule <|-- TimePartitionedPretrainedSTFTBridgeModel
    STFTBridgeModel --> Diffusion
    STFTBridgeModel --> SinusoidalTemporalEmbedding
    STFTBridgeModel --> AttnUNetF
    TimePartitionedPretrainedSTFTBridgeModel --> Diffusion
    TimePartitionedPretrainedSTFTBridgeModel --> SinusoidalTemporalEmbedding
    TimePartitionedPretrainedSTFTBridgeModel --> AttnUNetF
```

**Sources:** [A2SB_lightning_module.py:208-477](), [A2SB_lightning_module_api.py:35-210]()

## Key Component Mapping

The following diagram maps high-level system components to specific code entities, bridging natural language descriptions to actual implementation:

```mermaid
graph TB
    subgraph "Training Components"
        training_loop["Training Loop<br/>(Lightning Trainer)"]
        training_step["STFTBridgeModel.training_step()<br/>Line 374-402"]
        sample_t["sample_t_bounded()<br/>Line 370-372"]
        q_sample["Diffusion.q_sample()<br/>diffusion.py"]
        vf_forward["vf_model(x_t, t_emb)<br/>AttnUNetF.forward()"]
        loss_calc["MSE Loss Calculation<br/>Line 388"]
        optimizer["RAdam Optimizer<br/>configure_optimizers()"]
    end
    
    subgraph "Inference Components"
        predict_step["TimePartitionedPretrainedSTFTBridgeModel.predict_step()<br/>Line 186-210"]
        ddpm_sample["ddpm_sample()<br/>Line 106-149"]
        get_vf["get_vf_model(t)<br/>Line 84-89"]
        multidiff_vf["get_multidiffusion_vf()<br/>diffusion.py"]
        p_posterior["Diffusion.p_posterior()<br/>diffusion.py"]
        vocode["vocode_stft()<br/>Line 92-103"]
    end
    
    subgraph "Time Embedding"
        time_input["Timestep t<br/>(float 0-1)"]
        sinusoidal["SinusoidalTemporalEmbedding<br/>networks.py"]
        time_emb["t_emb<br/>(128-dim vector)"]
    end
    
    subgraph "Audio Transform Pipeline"
        input_wav["Waveform Input"]
        forward_xforms["Forward Transforms<br/>audio_transforms"]
        stft_repr["STFT Representation<br/>(3-channel)"]
        inverse_xforms["Inverse Transforms<br/>inv_transforms"]
        output_wav["Waveform Output"]
    end
    
    training_loop --> training_step
    training_step --> sample_t
    training_step --> q_sample
    training_step --> vf_forward
    training_step --> loss_calc
    loss_calc --> optimizer
    
    predict_step --> ddpm_sample
    ddpm_sample --> get_vf
    get_vf --> multidiff_vf
    ddpm_sample --> p_posterior
    predict_step --> vocode
    
    time_input --> sinusoidal
    sinusoidal --> time_emb
    time_emb --> vf_forward
    time_emb --> multidiff_vf
    
    input_wav --> forward_xforms
    forward_xforms --> stft_repr
    stft_repr --> vf_forward
    stft_repr --> vocode
    vocode --> inverse_xforms
    inverse_xforms --> output_wav
```

**Sources:** [A2SB_lightning_module.py:374-402](), [A2SB_lightning_module_api.py:106-210]()

## Configuration Parameters

Key configuration parameters for both Lightning modules are documented below. These correspond to constructor arguments and can be set via YAML configuration files.

### STFTBridgeModel Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vf_model` | `torch.nn.Module` | Required | Vector field neural network (typically `AttnUNetF`) |
| `learning_rate` | `float` | `1e-4` | Learning rate for RAdam optimizer |
| `weight_decay` | `float` | `1e-8` | Weight decay for regularization |
| `inv_transforms` | `list` | `[]` | List of inverse audio transforms for vocoding |
| `sampling_rate` | `int` | `22050` | Audio sampling rate in Hz |
| `n_timestep_channels` | `int` | `128` | Dimensionality of time embedding |
| `beta_max` | `float` | `0.3` | Maximum noise level for diffusion |
| `use_ot_ode` | `bool` | `False` | Use ODE formulation instead of SDE |
| `train_t_min` | `float` | `0` | Minimum timestep for training (T-finetuning) |
| `train_t_max` | `float` | `1` | Maximum timestep for training (T-finetuning) |

**Sources:** [A2SB_lightning_module.py:209-236]()

### TimePartitionedPretrainedSTFTBridgeModel Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vf_model` | `torch.nn.Module` | Required | Template vector field model (architecture only) |
| `pretrained_checkpoints` | `List[str]` | Required | Paths to pretrained checkpoint files |
| `t_cutoffs` | `List[float]` | `[0.5]` | Timestep boundaries for model switching |
| `inv_transforms` | `list` | `[]` | List of inverse audio transforms |
| `sampling_rate` | `int` | `22050` | Audio sampling rate in Hz |
| `n_timestep_channels` | `int` | `128` | Dimensionality of time embedding |
| `beta_max` | `float` | `0.3` | Maximum noise level for diffusion |
| `use_ot_ode` | `bool` | `False` | Use ODE formulation instead of SDE |
| `fast_inpaint_mode` | `bool` | `False` | Enable fast inpainting for sparse masks |
| `predict_n_steps` | `int` | `50` | Number of diffusion sampling steps |
| `predict_hop_length` | `int` | `128` | Hop length for multidiffusion |
| `predict_win_length` | `int` | `256` | Window length for multidiffusion |
| `predict_batch_size` | `int` | `16` | Batch size for multidiffusion processing |

**Sources:** [A2SB_lightning_module_api.py:36-64]()

## Training Data Flow

The following diagram illustrates the complete data flow through the training system, from raw audio to loss computation:

```mermaid
graph LR
    subgraph "Data Loading"
        manifest["Manifest CSV<br/>(file paths)"]
        dataset["PyTorch Dataset<br/>(batch loading)"]
        batch["Batch Dict<br/>x_0_clean, x_0_corrupted, loss_mask"]
    end
    
    subgraph "Forward Pass"
        t_sample["sample_t_bounded()<br/>t ~ U[train_t_min, train_t_max]"]
        t_emb_gen["t_to_emb(t)<br/>SinusoidalTemporalEmbedding"]
        q_sample_step["ddpm.q_sample(t, x_0_clean, x_0_corrupted)<br/>Returns x_t"]
        vf_call["vf_model(x_t, t_emb)<br/>Predicts vector field"]
    end
    
    subgraph "Loss Computation"
        std_fwd["ddpm.get_std_fwd(t)<br/>Forward noise std"]
        target_calc["target = (x_t - x_0_clean) / std_fwd"]
        mse["MSE(vf_output, target)<br/>Masked loss"]
    end
    
    subgraph "Optimization"
        backward["loss.backward()"]
        grad_clip["clip_grad_norm_(max=0.5)"]
        opt_step["optimizer.step()<br/>RAdam"]
    end
    
    manifest --> dataset
    dataset --> batch
    batch --> t_sample
    batch --> q_sample_step
    t_sample --> t_emb_gen
    t_emb_gen --> vf_call
    q_sample_step --> vf_call
    vf_call --> mse
    t_sample --> std_fwd
    std_fwd --> target_calc
    batch --> target_calc
    q_sample_step --> target_calc
    target_calc --> mse
    batch --> mse
    mse --> backward
    backward --> grad_clip
    grad_clip --> opt_step
```

**Sources:** [A2SB_lightning_module.py:374-402]()

## Inference Data Flow

The inference pipeline processes audio through iterative DDPM sampling with optional multidiffusion for long sequences:

```mermaid
graph TB
    subgraph "Input Preparation"
        input_batch["Input Batch<br/>x_0_corrupted, loss_mask"]
        pad_inputs["multidiffusion_pad_inputs()<br/>Add padding for windows"]
        t_schedule["t_steps = linspace(1, 0.05, n_steps)<br/>Discretized timesteps"]
    end
    
    subgraph "Iterative Sampling Loop"
        loop_start["for t_idx in range(n_steps)"]
        get_model["vf_model = get_vf_model(t[t_idx])<br/>Select appropriate model"]
        multidiff["get_multidiffusion_vf()<br/>Window-based processing"]
        pred_x0["ddpm.get_pred_x0(t, x_t, vf_output)<br/>Predict clean signal"]
        mask_apply["pred_x0 = pred_x0 * mask + (1-mask) * x_1<br/>Apply corruption mask"]
        posterior["x_t = ddpm.p_posterior(t_prev, t, x_t, pred_x0)<br/>Reverse step"]
        sde_noise["if SDE: x_t += noise in unmasked regions"]
    end
    
    subgraph "Output Processing"
        unpad["multidiffusion_unpad_outputs()<br/>Remove padding"]
        vocode_call["vocode_stft()<br/>STFT to waveform"]
        write_output["write_wav()<br/>Save restored audio"]
    end
    
    input_batch --> pad_inputs
    pad_inputs --> loop_start
    t_schedule --> loop_start
    loop_start --> get_model
    get_model --> multidiff
    multidiff --> pred_x0
    pred_x0 --> mask_apply
    mask_apply --> posterior
    posterior --> sde_noise
    sde_noise --> loop_start
    loop_start --> unpad
    unpad --> vocode_call
    vocode_call --> write_output
```

**Sources:** [A2SB_lightning_module_api.py:106-210]()

## Checkpoint Loading and Ensemble Setup

The `TimePartitionedPretrainedSTFTBridgeModel` implements a sophisticated checkpoint loading mechanism for ensemble models:

```mermaid
graph TB
    subgraph "Initialization"
        config["Config with:<br/>pretrained_checkpoints<br/>t_cutoffs"]
        validate["Assert len(t_cutoffs) + 1<br/>== len(pretrained_checkpoints)"]
    end
    
    subgraph "Checkpoint Loading"
        loop["for ckpt in pretrained_checkpoints"]
        load_dict["torch.load(ckpt)['state_dict']<br/>Full Lightning state dict"]
        filter["Filter keys:<br/>if 'vf_model' in key"]
        rename["Remove 'vf_model.' prefix"]
        deepcopy["copy.deepcopy(self.vf_model)<br/>Clone architecture"]
        load_state["current_model.load_state_dict()<br/>Load weights"]
        append["loaded_models.append(current_model)"]
    end
    
    subgraph "Model Selection at Inference"
        runtime_t["Runtime timestep t"]
        iterate["for idx, thresh in enumerate(t_cutoffs)"]
        compare["if t >= thresh: model_idx = idx + 1"]
        select["return t_bounded_pretrained_models[model_idx]"]
    end
    
    config --> validate
    validate --> loop
    loop --> load_dict
    load_dict --> filter
    filter --> rename
    rename --> deepcopy
    deepcopy --> load_state
    load_state --> append
    append --> loop
    
    runtime_t --> iterate
    iterate --> compare
    compare --> select
```

**Sources:** [A2SB_lightning_module_api.py:66-89]()

## Method Reference Summary

### STFTBridgeModel Key Methods

| Method | Line Range | Purpose |
|--------|------------|---------|
| `__init__()` | 209-236 | Initialize training module with configuration |
| `configure_optimizers()` | 239-242 | Set up RAdam optimizer |
| `sample_t_bounded()` | 370-372 | Sample timesteps within `[train_t_min, train_t_max]` |
| `training_step()` | 374-402 | Execute one training iteration |
| `validation_step()` | 434-476 | Evaluate model on validation data |
| `test_step()` | 405-419 | Test model and compute audio metrics |
| `ddpm_sample()` | 244-278 | Iterative DDPM sampling for inference |
| `vocode_stft()` | 357-368 | Convert STFT representation to waveform |

**Sources:** [A2SB_lightning_module.py:208-477]()

### TimePartitionedPretrainedSTFTBridgeModel Key Methods

| Method | Line Range | Purpose |
|--------|------------|---------|
| `__init__()` | 36-64 | Initialize inference module with ensemble |
| `load_t_bounded_checkpoints()` | 66-81 | Load multiple checkpoint files into ensemble |
| `get_vf_model()` | 84-89 | Select appropriate model based on timestep |
| `ddpm_sample()` | 106-149 | Multidiffusion-enabled DDPM sampling |
| `fast_inpaint_ddpm_sample()` | 152-183 | Fast inpainting for sparse masks |
| `vocode_stft()` | 92-103 | Convert STFT representation to waveform |
| `predict_step()` | 186-210 | Process batch and save restored audio |

**Sources:** [A2SB_lightning_module_api.py:35-210]()

## Validation and Testing Infrastructure

The training module includes comprehensive validation and testing capabilities:

### Validation Process

During validation (`validation_step`), the model evaluates:

1. **Loss at Multiple Timesteps**: Computes MSE loss at `t ∈ {0.01, 0.25, 0.50, 0.75, 0.99}` to monitor learning across the diffusion trajectory
2. **Full Restoration**: Performs complete DDPM sampling with 25 steps
3. **Audio Metrics**: Computes quality metrics using `ssr_eval.metrics.AudioMetrics`

### Validation Callback

The `LogValidationInpaintingSTFTCallback` class provides TensorBoard logging:

| Logged Item | Method |
|-------------|--------|
| Original audio | `logger.experiment.add_audio()` |
| Original magnitude spectrogram | `logger.experiment.add_image()` |
| Masked magnitude spectrogram | `logger.experiment.add_image()` |
| Inpainted magnitude spectrogram | `logger.experiment.add_image()` |
| Inpainted audio | `logger.experiment.add_audio()` |

**Sources:** [A2SB_lightning_module.py:434-476](), [A2SB_lightning_module.py:479-531]()

## Fast Inpainting Mode

For inpainting tasks with sparse, well-separated corrupted regions, the `fast_inpaint_ddpm_sample()` method provides significant speedup:

**Algorithm:**
1. Identify centers of corrupted segments using `find_middle_of_zero_segments()`
2. For each corrupted segment:
   - Extract window of size `win_length` centered on corruption
   - Run full DDPM sampling on this window only
   - Replace the window in the full sequence
3. Return complete restored sequence

**Assumptions:**
- Each corrupted segment is shorter than `win_length`
- Corrupted segments are sufficiently separated
- Suitable for inpainting but not bandwidth extension

**Sources:** [A2SB_lightning_module_api.py:152-183]()

## Related Documentation

For detailed information about specific components:
- **Lightning module implementation details**: See [Lightning Modules](#6.1)
- **Audio transformation classes**: See [Audio Processing Pipeline](#6.2)
- **Neural network architectures**: See [Model Architecture Details](#6.3)
- **Diffusion algorithm mathematics**: See [Diffusion Process Implementation](#6.4)
- **STFT and phase utilities**: See [STFT and SO(2) Phase Utilities](#6.5)
- **Transform class reference**: See [Audio Transforms Reference](#6.6)

For theoretical background and high-level architecture:
- **A2SB model overview**: See [A2SB Model Overview](#5.1)
- **Schrödinger Bridge theory**: See [Schrödinger Bridge Diffusion](#5.2)
- **Audio representation theory**: See [Audio Representation](#5.3)
- **Time-partitioned ensemble explanation**: See [Time-Partitioned Ensemble](#5.4)

---

