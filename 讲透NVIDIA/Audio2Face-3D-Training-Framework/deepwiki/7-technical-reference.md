<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Training-Framework · page 7 Technical Reference · fetched 2026-10-26 -->

# Technical Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [audio2face/deps/charsiu/README.md](audio2face/deps/charsiu/README.md)
- [audio2face/deps/charsiu/src/Charsiu.py](audio2face/deps/charsiu/src/Charsiu.py)
- [audio2face/deps/charsiu/src/processors.py](audio2face/deps/charsiu/src/processors.py)
- [audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py](audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py)
- [audio2face/deps/motion_diffusion_model/diffusion/resample.py](audio2face/deps/motion_diffusion_model/diffusion/resample.py)
- [audio2face/deps/motion_diffusion_model/diffusion/script_utils.py](audio2face/deps/motion_diffusion_model/diffusion/script_utils.py)
- [audio2face/losses.py](audio2face/losses.py)

</details>



## Purpose and Scope

This technical reference provides detailed documentation of the core components and subsystems that implement the Audio2Face-3D Training Framework's functionality. It covers the implementation details, class hierarchies, and technical specifications of the framework's key modules.

For general system overview and architecture, see [Overview](#1). For configuration details, see [Configuration System](#3). For training workflow information, see [Training Framework](#5).

## Core Technical Architecture

The framework consists of several interconnected technical subsystems that handle different aspects of the audio-to-facial animation pipeline:

```mermaid
graph TB
    subgraph "Core Technical Components"
        subgraph "Audio Processing Engine"
            AP[charsiu_aligner]
            AP --> CFA[charsiu_forced_aligner]
            AP --> CPA[charsiu_predictive_aligner]
            AP --> CPP[CharsiuPreprocessor_en/zh]
        end
        
        subgraph "Diffusion Engine"
            GD[GaussianDiffusion]
            GD --> SMS[DDPM/DDIM Sampling]
            GD --> LT[LossType enum]
            GD --> MVT[ModelVarType enum]
            GD --> MMT[ModelMeanType enum]
        end
        
        subgraph "Loss Computation"
            LC[Loss Functions]
            LC --> MSE[mse_loss]
            LC --> ML[motion_loss]  
            LC --> LDL[lip_dist_loss]
            LC --> PL[phoneme_loss]
            LC --> ESR[expression_smooth_reg]
        end
        
        subgraph "Utility Systems"
            SU[Script Utilities]
            SU --> CGD[create_gaussian_diffusion]
            SU --> SD[SpacedDiffusion]
            SU --> SS[ScheduleSampler]
        end
    end
    
    AP --> GD
    LC --> GD
    SU --> GD
    
    style AP fill:#f9f9f9
    style GD fill:#f0f8ff  
    style LC fill:#f5f5f5
    style SU fill:#fff5ee
```

**Sources:** [audio2face/deps/charsiu/src/Charsiu.py:1-576](), [audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py:1-1200](), [audio2face/losses.py:1-232](), [audio2face/deps/motion_diffusion_model/diffusion/script_utils.py:1-60]()

## Diffusion Model Implementation

The core diffusion functionality is implemented through the `GaussianDiffusion` class, which provides a complete diffusion process implementation based on Denoising Diffusion Probabilistic Models (DDPM).

### GaussianDiffusion Class Structure

```mermaid
classDiagram
    class GaussianDiffusion {
        +betas: np.array
        +num_timesteps: int
        +model_mean_type: ModelMeanType
        +model_var_type: ModelVarType  
        +loss_type: LossType
        +q_sample(x_start, t, noise)
        +p_mean_variance(model, x, t)
        +p_sample(model, x, t)
        +p_sample_loop(model, shape)
        +ddim_sample(model, x, t)
        +training_losses(model, x_start, t)
    }
    
    class ModelMeanType {
        <<enumeration>>
        PREVIOUS_X
        START_X
        EPSILON
    }
    
    class ModelVarType {
        <<enumeration>>  
        LEARNED
        FIXED_SMALL
        FIXED_LARGE
        LEARNED_RANGE
    }
    
    class LossType {
        <<enumeration>>
        MSE
        RESCALED_MSE
        KL
        RESCALED_KL
    }
    
    GaussianDiffusion --> ModelMeanType
    GaussianDiffusion --> ModelVarType
    GaussianDiffusion --> LossType
```

The `GaussianDiffusion` class supports multiple sampling strategies:

| Sampling Method | Function | Description |
|-----------------|----------|-------------|
| DDPM | `p_sample_loop()` | Standard denoising diffusion sampling |
| DDIM | `ddim_sample_loop()` | Deterministic sampling with configurable eta |
| Progressive | `p_sample_loop_progressive()` | Yields intermediate samples at each timestep |

**Key Technical Features:**

- **Beta Scheduling**: Supports linear and cosine noise schedules via `get_named_beta_schedule()`
- **Model Prediction Types**: Can predict noise (epsilon), start image (x_0), or previous step (x_{t-1})
- **Variance Handling**: Fixed or learned variance with multiple parameterizations
- **Streaming Support**: Special handling for streaming inference modes

**Sources:** [audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py:125-1200]()

### Diffusion Configuration Factory

The `create_gaussian_diffusion()` function provides a factory pattern for creating configured diffusion instances:

```mermaid
graph LR
    subgraph "Diffusion Configuration"
        CONFIG[Configuration Parameters] 
        CONFIG --> steps["steps=1000"]
        CONFIG --> schedule["noise_schedule='linear'"]  
        CONFIG --> predict["predict_xstart=False"]
        CONFIG --> respacing["timestep_respacing=''"]
        
        steps --> CGD[create_gaussian_diffusion]
        schedule --> CGD
        predict --> CGD  
        respacing --> CGD
        
        CGD --> SD[SpacedDiffusion]
        CGD --> BETA[Beta Schedule]
        CGD --> LOSS[Loss Configuration]
        CGD --> VAR[Variance Configuration]
    end
```

**Sources:** [audio2face/deps/motion_diffusion_model/diffusion/script_utils.py:27-60]()

## Phoneme Alignment System

The Charsiu phoneme alignment system provides forced alignment and text-independent alignment capabilities for multiple languages.

### Aligner Class Hierarchy

```mermaid
classDiagram
    class charsiu_aligner {
        <<abstract>>
        +lang: str
        +processor: CharsiuPreprocessor
        +device: str
        +resolution: float
        +align(audio, text)*
        +serve(audio, save_to)*
        +_to_textgrid(phones, save_to)
        +_to_tsv(phones, save_to)
    }
    
    class charsiu_forced_aligner {
        +aligner: Wav2Vec2ForFrameClassification
        +sil_threshold: int
        +align(audio, text)
        +_merge_silence(aligned_phones, sil_mask)
        +_get_sil_mask(cost)
    }
    
    class charsiu_predictive_aligner {
        +aligner: Wav2Vec2ForFrameClassification
        +temperature: float
        +align(audio)
        +align_probs(audio, sr)
    }
    
    class charsiu_attention_aligner {
        +aligner: Wav2Vec2ForAttentionAlignment
        +align(audio, text)
    }
    
    class CharsiuPreprocessor_en {
        +processor: Wav2Vec2Processor
        +g2p: G2p
        +get_phones_and_words(sen)
        +get_phone_ids(phones)
    }
    
    class CharsiuPreprocessor_zh {
        +processor: Wav2Vec2Processor  
        +g2p: G2pM
        +transform_dict: dict
        +_separate_syllable(syllable)
    }
    
    charsiu_aligner <|-- charsiu_forced_aligner
    charsiu_aligner <|-- charsiu_predictive_aligner
    charsiu_aligner <|-- charsiu_attention_aligner
    charsiu_aligner --> CharsiuPreprocessor_en
    charsiu_aligner --> CharsiuPreprocessor_zh
```

### Alignment Workflow

The alignment process follows a consistent pattern across different aligner types:

```mermaid
sequenceDiagram
    participant Client
    participant Aligner as "charsiu_*_aligner"
    participant Processor as "CharsiuPreprocessor"
    participant Model as "Wav2Vec2Model"
    
    Client->>Aligner: align(audio, text)
    Aligner->>Processor: audio_preprocess(audio)
    Processor-->>Aligner: processed_audio
    
    alt Forced Alignment
        Aligner->>Processor: get_phones_and_words(text)
        Processor-->>Aligner: phones, words
        Aligner->>Processor: get_phone_ids(phones)
        Processor-->>Aligner: phone_ids
    end
    
    Aligner->>Model: forward(processed_audio)
    Model-->>Aligner: logits/alignments
    Aligner->>Aligner: post_process_alignment()
    Aligner-->>Client: aligned_phones, aligned_words
```

**Key Technical Components:**

- **Language Support**: English (`CharsiuPreprocessor_en`) and Mandarin (`CharsiuPreprocessor_zh`)
- **Model Types**: Frame classification, attention-based, and CTC models
- **Output Formats**: TextGrid and TSV file formats
- **Preprocessing**: Audio resampling to 16kHz, phoneme tokenization

**Sources:** [audio2face/deps/charsiu/src/Charsiu.py:41-576](), [audio2face/deps/charsiu/src/processors.py:1-531]()

## Loss Function System

The framework implements a comprehensive set of loss functions for training facial animation models:

### Core Loss Functions

| Function | Purpose | Input Shape | Key Features |
|----------|---------|-------------|--------------|
| `mse_loss()` | Basic reconstruction | `(batch, seq, features)` | Standard L2 loss |
| `motion_loss()` | Temporal consistency | `(batch, seq, features)` | First-order differences |
| `lip_dist_loss()` | Lip closure constraint | `(batch, seq, verts, 3)` | Exponential weighting |
| `phoneme_loss()` | Phoneme classification | `(batch, seq, classes)` | Cross-entropy with weights |
| `expression_smooth_reg()` | Upper face smoothing | `(batch, seq, verts, 3)` | Soft masking |

### Specialized Loss Components

```mermaid
graph TB
    subgraph "Geometric Losses"
        LD[lip_dist_loss]
        LS[lip_size_loss]  
        LD --> EW["Exponential Weighting"]
        LS --> UL["Upper/Lower Lip Constraints"]
    end
    
    subgraph "Temporal Losses" 
        ML[motion_loss]
        MR[motion_reg_loss]
        VS[vol_stab_reg_loss]
        ML --> FD["First Derivatives"]
        MR --> NL["Normalized Loss"]
        VS --> VW["Volume Weighting"]
    end
    
    subgraph "Phoneme Losses"
        PL[phoneme_loss]
        PM[phoneme_motion_loss]
        PL --> CE["Cross Entropy"]
        PM --> TM["Temporal Motion"]
    end
    
    subgraph "Regularization"
        ES[expression_smooth_reg]
        LN[LossNormalizer]
        ES --> SM["Soft Masking"] 
        LN --> AN["Adaptive Normalization"]
    end
```

### Loss Computation Pipeline

The `LossNormalizer` class provides adaptive loss scaling:

```python
class LossNormalizer:
    def __init__(self, mode: str, decay: float)
    def normalize(self, loss: torch.Tensor) -> torch.Tensor
    def reset(self) -> None
```

**Normalization Modes:**
- `"mean"`: Running average normalization
- `"stddev"`: Standard deviation normalization

**Sources:** [audio2face/losses.py:1-232]()

## Sampling and Scheduling System

The framework provides sophisticated timestep sampling strategies for diffusion training:

### Schedule Samplers

```mermaid
classDiagram
    class ScheduleSampler {
        <<abstract>>
        +weights()* 
        +sample(batch_size, device)
    }
    
    class UniformSampler {
        +diffusion: GaussianDiffusion
        +_weights: np.array
        +weights()
    }
    
    class LossSecondMomentResampler {
        +history_per_term: int
        +uniform_prob: float
        +_loss_history: np.array
        +_loss_counts: np.array
        +update_with_all_losses(ts, losses)
        +_warmed_up()
    }
    
    ScheduleSampler <|-- UniformSampler
    ScheduleSampler <|-- LossSecondMomentResampler
```

The `create_named_schedule_sampler()` factory function supports:
- `"uniform"`: Equal probability for all timesteps
- `"loss-second-moment"`: Importance sampling based on loss variance

**Resampling Strategy:**
1. Track loss history per timestep
2. Compute second moment of losses  
3. Sample timesteps proportional to loss variance
4. Apply importance weights to maintain unbiased estimates

**Sources:** [audio2face/deps/motion_diffusion_model/diffusion/resample.py:1-170]()

## Key Implementation Details

### Memory and Performance Optimizations

- **Gradient Accumulation**: Supported for large batch training
- **Mixed Precision**: Compatible with automatic mixed precision
- **Streaming Inference**: Special modes for real-time applications
- **Vectorized Operations**: Loss functions use tensor operations for efficiency

### Model Compatibility

The technical components support multiple model architectures:
- **Regression Models**: `conv_w2v_autocorr` network type
- **Diffusion Models**: `diffusion_rnn` network type  
- **Multi-Actor**: Configurable per-actor parameters
- **Target Channels**: Flexible output dimensionality

**Sources:** [audio2face/deps/motion_diffusion_model/diffusion/gaussian_diffusion.py:308-314](), [audio2face/deps/charsiu/src/Charsiu.py:542-544]()

---

