<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/diffusion-audio-restoration · page 5 Architecture and Core Concepts · fetched 2026-10-26 -->

# Architecture and Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [A2SB_lightning_module.py](A2SB_lightning_module.py)
- [A2SB_lightning_module_api.py](A2SB_lightning_module_api.py)
- [README.md](README.md)

</details>



## Purpose and Scope

This page provides a comprehensive overview of A2SB's architecture and the core concepts that enable vocoder-free, end-to-end audio restoration at 44.1kHz. It explains how the major components interact and bridges high-level system design to concrete code implementations.

For detailed explanations of specific subsystems, see:
- [A2SB Model Overview](#5.1) - High-level model design and unique characteristics
- [Schrödinger Bridge Diffusion](#5.2) - Diffusion formulation and sampling algorithms
- [Audio Representation](#5.3) - STFT, magnitude-instantaneous phase, and SO(2) matrices
- [Time-Partitioned Ensemble](#5.4) - The 2-split training and inference strategy

## System Architecture Overview

A2SB consists of three primary subsystems that work together to perform audio restoration:

1. **Training System** - Learns vector field models on degraded-to-clean audio pairs
2. **Diffusion Engine** - Implements Schrödinger Bridge formulation for stochastic interpolation
3. **Audio Processing Pipeline** - Converts between waveform and STFT representations

### High-Level Component Interaction

```mermaid
graph TB
    subgraph "Audio Domain"
        InputWav["Input Waveform<br/>44.1kHz degraded audio"]
        OutputWav["Output Waveform<br/>44.1kHz restored audio"]
    end
    
    subgraph "STFT Domain (Processing Space)"
        FwdTransforms["Forward Transforms<br/>ComplexSpectrogram<br/>MagInstPhase<br/>PowerScale"]
        STFTTensor["STFT Tensor<br/>3-channel: [mag, cos(phase), sin(phase)]<br/>Shape: B x 3 x H x W"]
        InvTransforms["Inverse Transforms<br/>PowerScale<br/>SO2PhaseCorrection<br/>InverseSpectrogram"]
    end
    
    subgraph "Model Processing"
        VFModel["Vector Field Model<br/>AttnUNetF network<br/>Predicts noise direction"]
        TimeEmb["Time Embedding<br/>SinusoidalTemporalEmbedding<br/>t → 128-dim vector"]
        DiffusionEngine["Diffusion Engine<br/>q_sample: forward process<br/>p_posterior: reverse step"]
    end
    
    subgraph "Training (STFTBridgeModel)"
        TrainLoop["Training Loop<br/>- Sample timestep t<br/>- Compute q_sample(t, x0_clean, x0_corrupted)<br/>- Train VF to predict noise direction"]
    end
    
    subgraph "Inference (TimePartitionedPretrainedSTFTBridgeModel)"
        InferLoop["Inference Loop<br/>- Load multiple VF models<br/>- Select model based on t_cutoffs<br/>- ddpm_sample with multidiffusion"]
    end
    
    InputWav --> FwdTransforms
    FwdTransforms --> STFTTensor
    STFTTensor --> TrainLoop
    STFTTensor --> InferLoop
    
    TrainLoop --> VFModel
    TrainLoop --> TimeEmb
    TrainLoop --> DiffusionEngine
    
    InferLoop --> VFModel
    InferLoop --> TimeEmb
    InferLoop --> DiffusionEngine
    
    VFModel --> STFTTensor
    STFTTensor --> InvTransforms
    InvTransforms --> OutputWav
    
    classDef audioClass fill:#f9f9f9,stroke:#333
    classDef stftClass fill:#f9f9f9,stroke:#333
    classDef modelClass fill:#f9f9f9,stroke:#333
    
    class InputWav,OutputWav audioClass
    class FwdTransforms,STFTTensor,InvTransforms stftClass
    class VFModel,TimeEmb,DiffusionEngine,TrainLoop,InferLoop modelClass
```

**Sources:**
- [A2SB_lightning_module.py:208-476]() - `STFTBridgeModel` training implementation
- [A2SB_lightning_module_api.py:35-210]() - `TimePartitionedPretrainedSTFTBridgeModel` inference implementation
- [README.md:17-25]() - System capabilities overview

## Core Concepts

### Vector Field Model

The vector field model is the core neural network that learns to predict the direction from a noisy/degraded audio sample toward the clean target. It is implemented as an attention-based U-Net architecture.

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Network Architecture | `AttnUNetF` in [networks.py]() | U-Net with attention mechanisms for processing 3-channel STFT |
| Input | STFT tensor (B x 3 x H x W) + time embedding (128-dim) | Current noisy state + diffusion timestep |
| Output | STFT tensor (B x 3 x H x W) | Predicted noise direction (vector field) |
| Training Target | `(x_t - x_0_clean) / std_fwd_t` | Normalized direction from clean to noisy |

The vector field formulation differs from standard diffusion models that predict noise directly. During training, the model learns:

```
vf_output = VectorFieldModel(x_t, time_embedding(t))
target = (x_t - x_0_clean) / std_fwd_t
loss = MSE(vf_output, target) * loss_mask
```

**Sources:**
- [A2SB_lightning_module.py:374-402]() - Training step implementation
- [networks.py]() - Neural network architectures

### Schrödinger Bridge Diffusion

A2SB uses a Schrödinger Bridge formulation rather than standard DDPM. This enables:

1. **Deterministic endpoints**: The forward process interpolates between degraded audio (x₁) and clean audio (x₀)
2. **Flexible scheduling**: Can be formulated as either SDE or ODE (controlled by `use_ot_ode` parameter)
3. **Masked sampling**: Supports inpainting by keeping known regions fixed during sampling

The `Diffusion` class implements:

| Method | Purpose | Key Parameters |
|--------|---------|---------------|
| `q_sample(t, x_0, x_1)` | Forward diffusion: interpolate from x₀ to x₁ at time t | `beta_max=0.3` controls noise schedule |
| `p_posterior(t_prev, t, x_t, pred_x0)` | Reverse diffusion: one step backward | `ot_ode` flag switches SDE/ODE |
| `get_pred_x0(t, x_t, vf_output)` | Recover clean prediction from vector field | Inverts the forward process |

```mermaid
graph LR
    X1["x₁<br/>(degraded audio)<br/>t=1.0"]
    Xt["x_t<br/>(intermediate state)<br/>t=0.5"]
    X0["x₀<br/>(clean audio)<br/>t=0.0"]
    
    X1 -->|"q_sample<br/>(forward process)"| Xt
    Xt -->|"q_sample<br/>(forward process)"| X0
    
    X0 -.->|"p_posterior<br/>(reverse process)<br/>guided by VF model"| Xt
    Xt -.->|"p_posterior<br/>(reverse process)<br/>guided by VF model"| X1
    
    VF["Vector Field Model<br/>predicts direction<br/>from x_t toward x₀"]
    VF -.-> Xt
```

**Sources:**
- [diffusion.py]() - `Diffusion` class implementation
- [A2SB_lightning_module.py:381-388]() - Forward process in training
- [A2SB_lightning_module.py:244-278]() - Reverse process in sampling

### STFT-Based Audio Representation

A2SB processes audio in the STFT domain using a factorized representation that separates magnitude and phase:

**Representation Pipeline:**

```mermaid
graph LR
    Waveform["Waveform<br/>1D time-domain signal"]
    Complex["Complex STFT<br/>complex-valued<br/>frequency-time"]
    MagPhase["Magnitude + Inst. Phase<br/>3 channels:<br/>[mag, cos(φ), sin(φ)]"]
    Processed["Processed<br/>DC term dropped<br/>power=0.25 scaling"]
    Model["Model Input<br/>B x 3 x H x W"]
    
    Waveform -->|"torch.stft"| Complex
    Complex -->|"MagInstPhase transform"| MagPhase
    MagPhase -->|"Drop DC + PowerScale"| Processed
    Processed --> Model
    
    Model -->|"PowerScale^-1"| Processed2["Processed<br/>power=4 scaling"]
    Processed2 -->|"Add DC + SO2 fix"| MagPhase2["Magnitude + Phase"]
    MagPhase2 -->|"Reconstruct complex"| Complex2["Complex STFT"]
    Complex2 -->|"torch.istft"| Waveform2["Waveform"]
```

The key innovation is representing phase as points on the SO(2) manifold (unit circle) using `[cos(φ), sin(φ)]` rather than raw phase angles. This avoids phase wrapping discontinuities.

**Transform Chain:**

| Transform | Direction | Implementation | Purpose |
|-----------|-----------|----------------|---------|
| `ComplexSpectrogram` | Forward | STFT with hann window | Convert waveform to frequency domain |
| `MagInstPhase` | Forward | Separate magnitude and phase | Extract amplitude and instantaneous phase |
| `PowerScale` | Bidirectional | Magnitude^power | Compress dynamic range (power=0.25 forward) |
| `SO2PhaseCorrection` | Inverse | SVD-based correction | Ensure phase vectors lie on unit circle |
| `InverseSpectrogram` | Inverse | iSTFT | Convert back to waveform |

**Sources:**
- [audio_transforms/transforms.py]() - Transform implementations
- [audio_utils.py]() - STFT and SO(2) utilities
- [README.md:21]() - Factorized audio representation mention

### Time-Partitioned Training Strategy

A2SB's most distinctive architectural feature is training separate models for different diffusion timestep ranges, then combining them during inference.

**Two-Split Configuration:**

| Split | Timestep Range | Parameter | Checkpoint |
|-------|---------------|-----------|------------|
| Split 1 | t ∈ [0.0, 0.5] | `train_t_min=0.0, train_t_max=0.5` | Model specialized for denoising |
| Split 2 | t ∈ [0.5, 1.0] | `train_t_min=0.5, train_t_max=1.0` | Model specialized for structure recovery |

```mermaid
graph TB
    subgraph "Training Phase"
        Pretrain["Pretraining<br/>Single model<br/>t ∈ [0.0, 1.0]"]
        Split1Train["T-Finetune Split 1<br/>train_t_min=0.0<br/>train_t_max=0.5"]
        Split2Train["T-Finetune Split 2<br/>train_t_min=0.5<br/>train_t_max=1.0"]
        
        Pretrain --> Split1Train
        Pretrain --> Split2Train
    end
    
    subgraph "Training Loop (STFTBridgeModel)"
        SampleT["sample_t_bounded()<br/>Sample t in [train_t_min, train_t_max]"]
        Forward["q_sample(t, x0_clean, x0_corrupted)<br/>Create noisy sample"]
        Predict["vf_model(x_t, time_emb)<br/>Predict vector field"]
        ComputeLoss["MSE loss between prediction and target"]
        
        SampleT --> Forward
        Forward --> Predict
        Predict --> ComputeLoss
    end
    
    subgraph "Inference (TimePartitionedPretrainedSTFTBridgeModel)"
        LoadModels["load_t_bounded_checkpoints()<br/>Load both split checkpoints"]
        SelectModel["get_vf_model(t)<br/>Select model based on t_cutoffs=[0.5]"]
        Sample["ddpm_sample()<br/>Iterative refinement t=1.0→0.0"]
        
        LoadModels --> SelectModel
        SelectModel --> Sample
    end
    
    Split1Train -->|"Checkpoint 1"| LoadModels
    Split2Train -->|"Checkpoint 2"| LoadModels
```

During inference, the `get_vf_model(t)` method selects which model to use based on the current timestep:

```python
# Simplified from A2SB_lightning_module_api.py:84-89
def get_vf_model(self, t: float):
    model_idx = 0
    for idx, thresh in enumerate(self.t_cutoffs):  # [0.5]
        if t >= thresh:
            model_idx = idx + 1
    return self.t_bounded_pretrained_models[model_idx]
```

**Sources:**
- [A2SB_lightning_module.py:370-376]() - `sample_t_bounded()` method
- [A2SB_lightning_module_api.py:64-81]() - `load_t_bounded_checkpoints()` method
- [A2SB_lightning_module_api.py:83-89]() - `get_vf_model()` model selection
- [configs/t_finetune_2split_0.0_0.5.yaml]() - Split 1 configuration

## Training vs Inference Architecture

A2SB maintains two separate Lightning Module implementations optimized for their respective purposes:

### Code Entity Mapping

```mermaid
graph TB
    subgraph "Training Implementation"
        STFTBridge["STFTBridgeModel<br/>(A2SB_lightning_module.py:208)"]
        SingleVF["self.vf_model<br/>Single AttnUNetF instance"]
        TrainStep["training_step()<br/>Line 374"]
        ValStep["validation_step()<br/>Line 434"]
        SimpleSample["ddpm_sample()<br/>Line 244<br/>No multidiffusion"]
        
        STFTBridge --> SingleVF
        STFTBridge --> TrainStep
        STFTBridge --> ValStep
        ValStep --> SimpleSample
    end
    
    subgraph "Inference Implementation"
        TimePart["TimePartitionedPretrainedSTFTBridgeModel<br/>(A2SB_lightning_module_api.py:35)"]
        MultiVF["self.t_bounded_pretrained_models<br/>ModuleList of AttnUNetF"]
        ModelSelector["get_vf_model(t)<br/>Line 84<br/>Selects based on t_cutoffs"]
        PredictStep["predict_step()<br/>Line 186"]
        MultiSample["ddpm_sample()<br/>Line 106<br/>With multidiffusion support"]
        FastInpaint["fast_inpaint_ddpm_sample()<br/>Line 152<br/>Optimized for inpainting"]
        
        TimePart --> MultiVF
        TimePart --> ModelSelector
        TimePart --> PredictStep
        PredictStep --> MultiSample
        PredictStep --> FastInpaint
        MultiSample --> ModelSelector
        FastInpaint --> ModelSelector
    end
    
    subgraph "Shared Components"
        Diffusion["Diffusion class<br/>(diffusion.py)"]
        TimeEmbedding["SinusoidalTemporalEmbedding<br/>(networks.py)"]
        Transforms["audio_transforms<br/>(transforms.py)"]
    end
    
    STFTBridge --> Diffusion
    STFTBridge --> TimeEmbedding
    STFTBridge --> Transforms
    
    TimePart --> Diffusion
    TimePart --> TimeEmbedding
    TimePart --> Transforms
```

### Key Architectural Differences

| Aspect | Training (`STFTBridgeModel`) | Inference (`TimePartitionedPretrainedSTFTBridgeModel`) |
|--------|------------------------------|-------------------------------------------------------|
| Vector Field Models | Single `vf_model` | Multiple models in `t_bounded_pretrained_models` |
| Model Selection | N/A | `get_vf_model(t)` based on `t_cutoffs` |
| Sampling | Simple `ddpm_sample()` | Enhanced with multidiffusion, fast inpainting |
| Purpose | Optimize model parameters | Generate restored audio |
| Batch Processing | Supports any batch size | Typically batch_size=1 for long audio |
| Configuration | `train_t_min`, `train_t_max` | `pretrained_checkpoints`, `t_cutoffs` |

**Sources:**
- [A2SB_lightning_module.py:208-476]() - Training module implementation
- [A2SB_lightning_module_api.py:35-210]() - Inference module implementation

## Audio Processing Data Flow

The following diagram traces how audio data flows through the system during inference:

```mermaid
graph TB
    Input["Raw Input Audio<br/>degraded.wav<br/>44.1kHz waveform"]
    
    subgraph "Forward Transform Pipeline"
        STFT1["torch.stft<br/>(ComplexSpectrogram)"]
        Complex1["Complex STFT<br/>real + imaginary"]
        MagPhase1["MagInstPhase<br/>magnitude + cos/sin phase"]
        Drop1["Drop DC term<br/>Remove 0 Hz bin"]
        Power1["PowerScale(power=0.25)<br/>Compress dynamic range"]
        Tensor1["Model Input Tensor<br/>B x 3 x H x W"]
    end
    
    subgraph "Iterative Refinement"
        Init["Initialize x_t = x_1<br/>(degraded STFT)"]
        Loop["For each timestep t"]
        GetModel["vf_model = get_vf_model(t)<br/>Select appropriate model"]
        Embed["t_emb = t_to_emb(t)<br/>Embed timestep"]
        Forward["vf_output = vf_model(x_t, t_emb)<br/>Predict vector field"]
        Pred["pred_x0 = get_pred_x0(t, x_t, vf_output)<br/>Estimate clean audio"]
        Step["x_t = p_posterior(t_prev, t, x_t, pred_x0)<br/>Diffusion reverse step"]
        
        Init --> Loop
        Loop --> GetModel
        GetModel --> Embed
        Embed --> Forward
        Forward --> Pred
        Pred --> Step
        Step -.->|"Next timestep"| Loop
    end
    
    subgraph "Inverse Transform Pipeline"
        Tensor2["Final pred_x0<br/>B x 3 x H x W"]
        Power2["PowerScale(power=4)<br/>Expand dynamic range"]
        Add2["Add DC term<br/>Zero-filled"]
        Fix2["SO2 Phase Correction<br/>SVD-based fix"]
        MagPhase2["Complex reconstruction<br/>mag * exp(i*phase)"]
        ISTFT2["torch.istft<br/>(InverseSpectrogram)"]
    end
    
    Output["Restored Audio<br/>restored.wav<br/>44.1kHz waveform"]
    
    Input --> STFT1
    STFT1 --> Complex1
    Complex1 --> MagPhase1
    MagPhase1 --> Drop1
    Drop1 --> Power1
    Power1 --> Tensor1
    
    Tensor1 --> Init
    Step --> Tensor2
    
    Tensor2 --> Power2
    Power2 --> Add2
    Add2 --> Fix2
    Fix2 --> MagPhase2
    MagPhase2 --> ISTFT2
    ISTFT2 --> Output
    
    Mask["loss_mask<br/>(optional)"]
    Mask -.->|"Constrain known regions"| Pred
```

**Key Processing Functions:**

| Stage | Function/Class | File Location | Purpose |
|-------|---------------|---------------|---------|
| STFT Forward | `ComplexSpectrogram` | [audio_transforms/transforms.py]() | Convert waveform to complex spectrogram |
| Phase Representation | `MagInstPhase` | [audio_transforms/transforms.py]() | Split into magnitude and SO(2) phase |
| Model Input Prep | `apply_audio_transforms()` | [audio_transforms/transforms.py]() | Apply forward transform chain |
| Sampling Loop | `ddpm_sample()` | [A2SB_lightning_module_api.py:106-149]() | Iterative refinement |
| Model Selection | `get_vf_model()` | [A2SB_lightning_module_api.py:84-89]() | Choose model based on timestep |
| Vocoding | `vocode_stft()` | [A2SB_lightning_module_api.py:92-103]() | Apply inverse transforms |
| STFT Inverse | `InverseSpectrogram` | [audio_transforms/transforms.py]() | Convert back to waveform |

**Sources:**
- [A2SB_lightning_module_api.py:106-149]() - `ddpm_sample()` implementation
- [A2SB_lightning_module_api.py:186-210]() - `predict_step()` orchestration
- [audio_transforms/transforms.py]() - Transform pipeline
- [audio_utils.py]() - Utility functions for STFT and phase

## Entry Points and Configuration

### Main Entry Points

```mermaid
graph LR
    subgraph "Training Entry Point"
        MainPy["main.py<br/>PyTorch Lightning CLI"]
        TrainConfig["configs/pretrain.yaml<br/>or t_finetune_*.yaml"]
        MainPy --> TrainConfig
        TrainConfig --> STFTBridgeModule["Instantiate STFTBridgeModel"]
    end
    
    subgraph "Inference Entry Points"
        API["inference/A2SB_upsample_api.py<br/>Single file processing"]
        Dataset["inference/A2SB_upsample_dataset.py<br/>Batch upsampling"]
        Inpaint["inference/A2SB_inpaint_dataset.py<br/>Batch inpainting"]
        InfConfig["configs/ensemble_2split_sampling.yaml"]
        
        API --> InfConfig
        Dataset --> InfConfig
        Inpaint --> InfConfig
        InfConfig --> TimePartModule["Instantiate TimePartitionedPretrainedSTFTBridgeModel"]
    end
```

### Configuration Parameters

Key configuration parameters that control architecture:

| Parameter | Location | Purpose | Typical Value |
|-----------|----------|---------|---------------|
| `beta_max` | Model config | Controls noise schedule strength | 0.3 |
| `use_ot_ode` | Model config | SDE vs ODE formulation | false (SDE) |
| `n_timestep_channels` | Model config | Dimensionality of time embedding | 128 |
| `train_t_min`, `train_t_max` | Training config | Timestep range for T-finetuning | [0.0, 0.5] or [0.5, 1.0] |
| `pretrained_checkpoints` | Inference config | List of model checkpoint paths | [split1.ckpt, split2.ckpt] |
| `t_cutoffs` | Inference config | Boundaries between model splits | [0.5] |
| `predict_n_steps` | Inference config | Number of diffusion steps | 50 |
| `predict_win_length` | Inference config | Window size for multidiffusion | 256 |
| `predict_hop_length` | Inference config | Hop size for multidiffusion | 128 |

**Sources:**
- [main.py]() - Training entry point
- [inference/A2SB_upsample_api.py]() - API entry point
- [configs/]() - Configuration files
- [A2SB_lightning_module.py:209-219]() - `STFTBridgeModel.__init__` parameters
- [A2SB_lightning_module_api.py:36-49]() - `TimePartitionedPretrainedSTFTBridgeModel.__init__` parameters

## Summary

A2SB's architecture achieves state-of-the-art audio restoration through:

1. **Vector field formulation** - Learning the direction from degraded to clean rather than predicting noise directly
2. **Schrödinger Bridge** - Flexible SDE/ODE formulation with deterministic endpoints
3. **Factorized STFT representation** - Magnitude + SO(2) phase for stable training
4. **Time-partitioned ensemble** - Specialized models for different diffusion timestep ranges
5. **Separation of concerns** - Distinct training and inference implementations optimized for their purposes

The architecture supports both bandwidth extension (predicting high frequencies) and inpainting (filling gaps) within a unified framework, processing audio in the STFT domain without requiring a separate vocoder.

---

