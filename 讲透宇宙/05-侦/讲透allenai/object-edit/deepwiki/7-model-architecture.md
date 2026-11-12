<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/object-edit · page 7 Model Architecture · fetched 2026-10-26 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ldm/extras.py](ldm/extras.py)
- [run_generation.py](run_generation.py)

</details>



## Purpose and Scope

This page provides a detailed technical overview of the **Latent Diffusion Model (LDM)** architecture used in OBJect 3DIT for language-guided 3D-aware image editing. The document covers the core model components, conditioning mechanisms, and sampling procedures. 

For information about training the model, see [Training System](#4). For details on the inference pipeline that uses this architecture, see [Generation Pipeline](#5.1). For specifics on how conditioning is computed for different tasks, see [Task-Specific Generation](#5.2).

---

## Core Architecture Overview

The OBJect 3DIT model is built on a **Latent Diffusion Model** architecture that operates in a compressed latent space rather than directly in pixel space. This architecture consists of three primary components that work together during both training and inference.

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT_IMG["Input Image<br/>(256×256×3)"]
        INPUT_TEXT["Text Prompt<br/>'rotate the car'"]
        INPUT_TASK["Task Parameters<br/>T tensor [4]"]
    end
    
    subgraph "First Stage VAE"
        ENCODER["encode_first_stage()<br/>Encoder Network"]
        LATENT["Latent Space<br/>(4×32×32)"]
        DECODER["decode_first_stage()<br/>Decoder Network"]
    end
    
    subgraph "Conditioning System"
        COND_STAGE["get_learned_conditioning()<br/>CLIP Text Encoder"]
        CC_PROJ["cc_projection<br/>Linear Projection"]
        CONCAT["Concatenate<br/>text + task params"]
    end
    
    subgraph "Diffusion Model"
        UNET["model.diffusion_model<br/>U-Net Architecture"]
        INPUT_BLOCKS["input_blocks.0.0<br/>Conv2d(8, 320, 3×3)"]
        CROSSATTN["Cross-Attention Layers<br/>c_crossattn"]
        CONCAT_COND["Concatenation Conditioning<br/>c_concat"]
    end
    
    subgraph "Sampling"
        SAMPLER["DDIMSampler<br/>Denoising Process"]
        NOISE["Gaussian Noise<br/>x_T"]
        OUTPUT["Generated Image<br/>(256×256×3)"]
    end
    
    INPUT_IMG --> ENCODER
    ENCODER --> LATENT
    LATENT --> CONCAT_COND
    
    INPUT_TEXT --> COND_STAGE
    INPUT_TASK --> CONCAT
    COND_STAGE --> CONCAT
    CONCAT --> CC_PROJ
    CC_PROJ --> CROSSATTN
    
    CONCAT_COND --> INPUT_BLOCKS
    INPUT_BLOCKS --> UNET
    CROSSATTN --> UNET
    
    NOISE --> SAMPLER
    UNET --> SAMPLER
    SAMPLER --> LATENT
    
    LATENT --> DECODER
    DECODER --> OUTPUT
```

**Sources:** [run_generation.py:68-112](), [run_generation.py:119-123]()

---

## Model Components

### First Stage VAE

The first stage is a **Variational Autoencoder (VAE)** that compresses input images into a lower-dimensional latent space. This component is responsible for the perceptual compression that enables efficient diffusion in a compact representation.

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `encode_first_stage()` | Image tensor (B×3×256×256) | Latent tensor (B×4×32×32) | Compress to latent space |
| `decode_first_stage()` | Latent tensor (B×4×32×32) | Image tensor (B×3×256×256) | Reconstruct from latent |

The VAE operates at a compression factor of 8 (256/32 = 8), reducing computational requirements while preserving perceptual quality. The `.mode()` method is called on encoded latents to use the mode of the distribution rather than sampling [run_generation.py:90]().

```mermaid
graph LR
    IMG["RGB Image<br/>256×256×3"] --> ENC["VAE Encoder"]
    ENC --> DIST["Distribution<br/>μ, σ"]
    DIST --> MODE[".mode()"]
    MODE --> LAT["Latent<br/>32×32×4"]
    LAT --> DEC["VAE Decoder"]
    DEC --> RECON["Reconstructed<br/>256×256×3"]
```

**Sources:** [run_generation.py:90-91](), [run_generation.py:94-95](), [run_generation.py:108]()

### Diffusion Model

The core diffusion model is implemented as a U-Net architecture accessed via `model.diffusion_model`. This network learns to predict noise at each timestep of the diffusion process.

#### Input Block Architecture

The first input block is particularly important as it handles channel concatenation:

```
model.diffusion_model.input_blocks.0.0.weight
Shape: (320, 8, 3, 3)
```

This Conv2d layer accepts **8 input channels**:
- **4 channels**: Noisy latent representation
- **4 channels**: Encoded input image (conditioning via concatenation)

The 8-channel input design enables the model to be conditioned on both the noisy latent and the original input image simultaneously [run_generation.py:26-44]().

**Sources:** [run_generation.py:26-29](), [run_generation.py:30-44]()

### Conditioning System

The conditioning system combines multiple sources of information to guide the diffusion process. It uses both **cross-attention conditioning** (`c_crossattn`) and **concatenation conditioning** (`c_concat`).

```mermaid
graph TB
    subgraph "Conditioning Inputs"
        IMG["Input Image"]
        TEXT["Text Prompt"]
        TASK["Task Tensor T<br/>[4] values"]
    end
    
    subgraph "Learned Conditioning"
        GET_COND["get_learned_conditioning()<br/>{'image': img, 'text': text}"]
        NULL_COND["null prompt ''<br/>for unconditional"]
    end
    
    subgraph "Projection and Concatenation"
        TILE["tile(n_samples, 1, 1)"]
        CAT["torch.cat([c, T], dim=-1)"]
        PROJ["cc_projection<br/>Linear Layer"]
    end
    
    subgraph "Final Conditioning Dict"
        C_CROSS["c_crossattn<br/>Cross-Attention"]
        C_CONCAT["c_concat<br/>Encoded Image Latent"]
    end
    
    IMG --> GET_COND
    TEXT --> GET_COND
    GET_COND --> TILE
    
    TASK --> CAT
    TILE --> CAT
    CAT --> PROJ
    
    PROJ --> C_CROSS
    IMG --> C_CONCAT
    
    NULL_COND --> C_CROSS
```

**Sources:** [run_generation.py:81-95]()

---

## Conditioning Mechanisms

### Text and Image Conditioning

The model uses `get_learned_conditioning()` to encode both text prompts and input images into a unified conditioning representation [run_generation.py:81]().

**Input format:**
```python
conditioning_input = {
    "image": input_im,  # Preprocessed image tensor
    "text": prompt       # Text description string
}
c = model.get_learned_conditioning(conditioning_input)
```

The method returns a tensor of shape `(1, N, C)` where:
- `N`: Sequence length (typically 77 for CLIP)
- `C`: Conditioning dimension

**Sources:** [run_generation.py:81]()

### Task Parameter Encoding

Task-specific parameters are encoded as a 4-element tensor `T` that is concatenated with the learned conditioning before projection:

| Task | T Encoding | Dimensions Used |
|------|-----------|-----------------|
| **rotate** | `[π/2, sin(θ), cos(θ), 0]` | [0]: elevation, [1-2]: azimuth encoding, [3]: unused |
| **remove** | `[0, 0, 0, 0]` | All zeros (no spatial info) |
| **insert** | `[0, x, y, 0]` | [1-2]: normalized x,y coordinates |
| **translate** | `[0, x, y, 0]` | [1-2]: normalized x,y coordinates |

The task tensor is repeated to match the conditioning sequence length and then concatenated [run_generation.py:84-86]():

```python
T = T[None, None, :].repeat(n_samples, 1, 1).to(c.device)
T = T.repeat(1, c.shape[1], 1)  # Repeat along sequence dimension
c = torch.cat([c, T], dim=-1)    # Concatenate along feature dimension
```

**Sources:** [run_generation.py:84-87](), [run_generation.py:129-141]()

### Conditioning Projection

After concatenation, the combined conditioning vector passes through `cc_projection`, a learned linear layer that projects it to the dimension expected by the cross-attention layers [run_generation.py:87]().

```
Input: [conditioning_features + 4]
Output: [cross_attention_dimension]
```

**Sources:** [run_generation.py:87]()

### Dual Conditioning Pathways

The diffusion model receives conditioning through two pathways:

1. **Cross-Attention (`c_crossattn`)**: Projected text+task conditioning that interacts with features via attention mechanisms
2. **Concatenation (`c_concat`)**: Encoded image latent that is concatenated with the noisy latent at the input layer

```mermaid
graph TB
    subgraph "Conditional Pathway"
        COND_IN["Conditioning c"]
        COND_OUT["c_crossattn: [c]"]
    end
    
    subgraph "Unconditional Pathway"
        UNCOND_IN["Null Prompt uc"]
        UNCOND_OUT["c_crossattn: [uc]"]
    end
    
    subgraph "Image Concatenation"
        IMG_ENC["encode_first_stage(input_im).mode()"]
        IMG_REPEAT["repeat(n_samples, 1, 1, 1)"]
        CONCAT_COND["c_concat: [encoded_img]"]
        CONCAT_UNCOND["c_concat: [encoded_img]"]
    end
    
    COND_IN --> COND_OUT
    UNCOND_IN --> UNCOND_OUT
    
    IMG_ENC --> IMG_REPEAT
    IMG_REPEAT --> CONCAT_COND
    IMG_REPEAT --> CONCAT_UNCOND
    
    COND_OUT --> SAMPLE["sampler.sample()"]
    CONCAT_COND --> SAMPLE
    UNCOND_OUT --> SAMPLE
    CONCAT_UNCOND --> SAMPLE
```

Note that the same encoded image latent is used for both conditional and unconditional pathways during classifier-free guidance [run_generation.py:90-95]().

**Sources:** [run_generation.py:88-95]()

---

## Model Instantiation and Loading

### Config-Based Instantiation

Models are instantiated from configuration files using the `instantiate_from_config()` utility function. The configuration specifies all model parameters including architecture details, conditioning mechanisms, and training hyperparameters.

```python
from ldm.util import instantiate_from_config
from omegaconf import OmegaConf

config = OmegaConf.load(f"configs/sd-objaverse-{task}.yaml")
model = instantiate_from_config(config.model)
```

**Sources:** [run_generation.py:117-119](), [ldm/extras.py:67]()

### Checkpoint Loading

Checkpoint loading handles nested state dictionaries and performs necessary weight adaptations:

```mermaid
graph TB
    LOAD["torch.load(checkpoint)"] --> CHECK{"'state_dict'<br/>key exists?"}
    CHECK -->|Yes| NESTED["Use old_state['state_dict']"]
    CHECK -->|No| DIRECT["Use old_state directly"]
    
    NESTED --> CHANNEL
    DIRECT --> CHANNEL
    
    CHANNEL{"Input channel<br/>mismatch?"}
    CHANNEL -->|4ch → 8ch| ADAPT["Zero-initialize new channels<br/>Copy first 4 channels"]
    CHANNEL -->|Match| SKIP["No adaptation needed"]
    
    ADAPT --> LOAD_STATE
    SKIP --> LOAD_STATE
    
    LOAD_STATE["model.load_state_dict()<br/>strict=False"]
    LOAD_STATE --> REPORT["Report missing/unexpected keys"]
```

**Sources:** [run_generation.py:16-53]()

### Channel Adaptation for Input Mismatch

When loading a 4-channel pretrained model (e.g., from Stable Diffusion) into an 8-channel model, the loader automatically adapts the input layer weights [run_generation.py:30-44]():

```python
if in_shape != in_filters_load.shape:
    input_weight = new_state[input_key]
    input_weight.zero_()
    input_weight[:, :4, :, :].copy_(old_state[input_key])
    old_state[input_key] = torch.nn.parameter.Parameter(input_weight)
```

This initialization:
1. Zero-initializes the 8-channel weight tensor
2. Copies the 4-channel pretrained weights to the first 4 channels
3. Leaves the additional 4 channels at zero (to be learned during finetuning)

**Sources:** [run_generation.py:25-44]()

### Loading from Training Directory

The `ldm/extras.py` module provides utilities for loading models from training directories:

```python
from ldm.extras import load_training_dir, load_model_from_config

# Load from training directory (finds latest checkpoint)
model = load_training_dir(train_dir, device, epoch="last")

# Load from explicit config and checkpoint
model = load_model_from_config(config, ckpt_path, device)
```

The `load_model_from_config()` function automatically sets the model to evaluation mode and configures the conditioning stage device [ldm/extras.py:74-76]().

**Sources:** [ldm/extras.py:37-53](), [ldm/extras.py:55-76]()

---

## Sampling Process

### DDIM Sampling

The model uses **Denoising Diffusion Implicit Models (DDIM)** for sampling via the `DDIMSampler` class [run_generation.py:144]().

```mermaid
graph TB
    INIT["DDIMSampler(model)"] --> CONFIG["Configure sampling parameters"]
    CONFIG --> NOISE["x_T ~ N(0,I)<br/>Random noise in latent space"]
    
    NOISE --> ITER["Iterative Denoising<br/>S steps (e.g., 50)"]
    
    ITER --> STEP1["Step t"]
    STEP1 --> PRED["model predicts noise ε_θ(x_t, t, c)"]
    PRED --> UPDATE["Update: x_{t-1} = f(x_t, ε_θ, t)"]
    UPDATE --> STEP2{"More steps?"}
    STEP2 -->|Yes| STEP1
    STEP2 -->|No| X0["x_0 (clean latent)"]
    
    X0 --> DECODE["decode_first_stage(x_0)"]
    DECODE --> OUTPUT["Generated Image"]
```

**Sampling parameters:**
- **S (ddim_steps)**: Number of denoising steps (default: 50)
- **shape**: Latent space shape `[4, 32, 32]` for 256×256 output
- **eta**: Stochasticity parameter (0 = deterministic DDIM)

**Sources:** [run_generation.py:98-106](), [run_generation.py:144]()

### Classifier-Free Guidance

The sampling process uses **classifier-free guidance** to improve generation quality and prompt following. This technique combines conditional and unconditional predictions:

```
ε̃_θ = ε_θ(x_t, c) + scale * (ε_θ(x_t, c) - ε_θ(x_t, ∅))
```

Where:
- `ε_θ(x_t, c)`: Conditional noise prediction
- `ε_θ(x_t, ∅)`: Unconditional noise prediction (null prompt)
- `scale`: Guidance scale (unconditional_guidance_scale parameter)

**Implementation details:**

Both conditional (`cond`) and unconditional (`uncond`) dictionaries are passed to the sampler [run_generation.py:88-95]():

```python
cond = {
    'c_crossattn': [c],           # Projected text+task conditioning
    'c_concat': [encoded_image]    # Input image latent
}

uncond = {
    'c_crossattn': [uc],          # Null prompt conditioning
    'c_concat': [encoded_image]    # Same input image latent
}
```

The guidance scale is controlled via the `unconditional_guidance_scale` parameter [run_generation.py:103]().

**Sources:** [run_generation.py:82-95](), [run_generation.py:98-106]()

---

## Model Interface Summary

### Key Methods

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `get_learned_conditioning()` | Encode text and image | `{"image": tensor, "text": str}` | Conditioning tensor |
| `encode_first_stage()` | Encode to latent space | Image tensor (B×3×H×W) | Latent distribution |
| `decode_first_stage()` | Decode from latent | Latent tensor (B×4×H/8×W/8) | Image tensor |
| `cc_projection()` | Project conditioning | Concatenated conditioning | Cross-attention features |

**Sources:** [run_generation.py:81](), [run_generation.py:87](), [run_generation.py:90-91](), [run_generation.py:94-95](), [run_generation.py:108]()

### Model State Dictionary Keys

Important checkpoint keys for debugging and adaptation:

```
model.diffusion_model.input_blocks.0.0.weight     # First conv layer (8 → 320 channels)
model_ema.diffusion_modelinput_blocks00weight     # EMA version (alternate naming)
```

**Sources:** [run_generation.py:26](), [run_generation.py:32-33]()

### Typical Image Processing Pipeline

```mermaid
graph LR
    PIL["PIL Image"] --> RESIZE["Resize(256, 256)"]
    RESIZE --> TOTENSOR["ToTensor()"]
    TOTENSOR --> NORM["Normalize [-1, 1]"]
    NORM --> BATCH["unsqueeze(0)"]
    BATCH --> DEVICE["to(device)"]
    DEVICE --> MODEL["Model Processing"]
    MODEL --> CLAMP["clamp(-1, 1)"]
    CLAMP --> DENORM["Denormalize [0, 1]"]
    DENORM --> UINT8["* 255 → uint8"]
    UINT8 --> SAVE["PIL.Image.fromarray()"]
```

**Sources:** [run_generation.py:55-66](), [run_generation.py:109-110](), [run_generation.py:158-163]()

---

## Dimensions and Shapes Reference

| Component | Shape | Notes |
|-----------|-------|-------|
| Input Image | (B, 3, 256, 256) | RGB image, normalized to [-1, 1] |
| Encoded Latent | (B, 4, 32, 32) | 8× compression factor |
| Task Tensor T | (B, N, 4) | Repeated along sequence dimension N |
| Conditioning | (B, N, C) | N ≈ 77 (CLIP tokens), C varies |
| Projected Conditioning | (B, N, D) | D = cross-attention dimension |
| Diffusion Input | (B, 8, 32, 32) | 4 noisy + 4 conditioning channels |
| Output Image | (B, 3, 256, 256) | RGB image, range [0, 1] after processing |

**Sources:** [run_generation.py:55-66](), [run_generation.py:81-87](), [run_generation.py:90-97]()

---

