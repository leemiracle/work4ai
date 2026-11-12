<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/object-edit · page 5 Inference and Generation · fetched 2026-10-26 -->

# Inference and Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [run_generation.py](run_generation.py)

</details>



## Purpose and Scope

This document provides an overview of the inference and generation system used to perform language-guided 3D-aware image editing with trained OBJect 3DIT models. The system takes an input image, a text prompt describing the object to edit, and task-specific parameters (e.g., rotation angle, translation coordinates), then generates edited output images using pretrained diffusion models.

For detailed information about:
- The step-by-step generation pipeline and internal processing, see [Generation Pipeline](#5.1)
- How individual tasks (rotate, remove, insert, translate) create their conditioning tensors, see [Task-Specific Generation](#5.2)
- Complete parameter documentation and configuration options, see [Generation Parameters and Configuration](#5.3)
- Model architecture details, see [Model Architecture](#7)
- Training procedures that produce the checkpoints used here, see [Training System](#4)

This page focuses on the high-level architecture and workflow of the inference system as implemented in `run_generation.py`.

## System Overview

The inference system consists of a single main entry point script that orchestrates the entire generation process. The system is designed to work with checkpoints from different tasks and automatically adapts to model configurations.

### Core Components

| Component | Code Location | Purpose |
|-----------|--------------|---------|
| Main Orchestrator | `run_generation.py:run()` | Coordinates the entire inference workflow |
| Checkpoint Loader | `run_generation.py:load_checkpoint()` | Loads pretrained weights with automatic input channel adaptation |
| Image Preprocessor | `run_generation.py:preprocess_image()` | Normalizes and resizes input images to 256×256 |
| Sampling Function | `run_generation.py:sample_model()` | Implements DDIM sampling with classifier-free guidance |
| Sampler Class | `ldm.models.diffusion.ddim.DDIMSampler` | Performs iterative denoising in latent space |

**Sources:** [run_generation.py:1-238]()

## Inference Architecture

The following diagram maps the natural language concepts in the inference system to their concrete code implementations:

```mermaid
graph TB
    subgraph "Entry Point"
        CLI["Command-Line Interface<br/>argparse.ArgumentParser<br/>(run_generation.py:176-234)"]
    end
    
    subgraph "Configuration Loading"
        YAML["Task Config YAML<br/>sd-objaverse-{task}.yaml<br/>(run_generation.py:117)"]
        OMEGA["OmegaConf.load()<br/>(run_generation.py:117)"]
        INST["instantiate_from_config()<br/>(run_generation.py:119)"]
    end
    
    subgraph "Model Initialization"
        CKPT["load_checkpoint()<br/>(run_generation.py:16-53)"]
        STATE["state_dict loading<br/>(run_generation.py:19-23)"]
        ADAPT["4ch→8ch adaptation<br/>(run_generation.py:26-44)"]
        MODEL["LDM model instance<br/>model.state_dict()<br/>(run_generation.py:27)"]
    end
    
    subgraph "Input Processing"
        IMG["PIL.Image.open()<br/>(run_generation.py:126)"]
        PREP["preprocess_image()<br/>(run_generation.py:55-66)"]
        RESIZE["torchvision.transforms.Resize<br/>to 256x256<br/>(run_generation.py:59)"]
        NORM["normalize to [-1, 1]<br/>(run_generation.py:64)"]
    end
    
    subgraph "Task Conditioning"
        TASK["Task-specific logic<br/>(run_generation.py:129-141)"]
        T_ROT["T = [π/2, sin(θ), cos(θ), 0]<br/>(run_generation.py:132)"]
        T_REM["T = [0, 0, 0, 0]<br/>(run_generation.py:135)"]
        T_INS["T = [0, x, y, 0]<br/>(run_generation.py:138)"]
        T_TRANS["T = [0, x, y, 0]<br/>(run_generation.py:141)"]
        PROMPT["f-string prompt construction<br/>(run_generation.py:130-141)"]
    end
    
    subgraph "Sampling Pipeline"
        SAMPLER["DDIMSampler(model)<br/>(run_generation.py:144)"]
        SAMPLE_FN["sample_model()<br/>(run_generation.py:68-112)"]
        COND["get_learned_conditioning()<br/>(run_generation.py:81)"]
        CC_PROJ["cc_projection()<br/>(run_generation.py:87)"]
        DDIM_SAMPLE["sampler.sample()<br/>(run_generation.py:98-106)"]
        DECODE["decode_first_stage()<br/>(run_generation.py:108)"]
    end
    
    subgraph "Output Generation"
        CLAMP["torch.clamp(-1, 1)<br/>(run_generation.py:109)"]
        DENORM["scale to [0, 1]<br/>(run_generation.py:110)"]
        REARR["einops.rearrange()<br/>(run_generation.py:158)"]
        SAVE["Image.save()<br/>(run_generation.py:169)"]
    end
    
    CLI --> YAML
    YAML --> OMEGA
    OMEGA --> INST
    INST --> MODEL
    
    CLI --> CKPT
    CKPT --> STATE
    STATE --> ADAPT
    ADAPT --> MODEL
    
    CLI --> IMG
    IMG --> PREP
    PREP --> RESIZE
    RESIZE --> NORM
    
    CLI --> TASK
    TASK --> T_ROT
    TASK --> T_REM
    TASK --> T_INS
    TASK --> T_TRANS
    TASK --> PROMPT
    
    MODEL --> SAMPLER
    NORM --> SAMPLE_FN
    PROMPT --> SAMPLE_FN
    T_ROT & T_REM & T_INS & T_TRANS --> SAMPLE_FN
    SAMPLER --> SAMPLE_FN
    
    SAMPLE_FN --> COND
    COND --> CC_PROJ
    CC_PROJ --> DDIM_SAMPLE
    DDIM_SAMPLE --> DECODE
    
    DECODE --> CLAMP
    CLAMP --> DENORM
    DENORM --> REARR
    REARR --> SAVE
```

**Sources:** [run_generation.py:1-238](), [README.md:54-62]()

## Generation Workflow

The generation process follows a linear pipeline from input to output. The following sequence diagram shows the exact function calls and data transformations:

```mermaid
sequenceDiagram
    participant User
    participant run as "run(args)<br/>(run_generation.py:114)"
    participant load as "load_checkpoint()<br/>(run_generation.py:16)"
    participant prep as "preprocess_image()<br/>(run_generation.py:55)"
    participant sample as "sample_model()<br/>(run_generation.py:68)"
    participant sampler as "DDIMSampler<br/>(ldm.models.diffusion.ddim)"
    participant model as "LDM model"
    
    User->>run: "Execute with CLI args"
    
    Note over run: "Load config from<br/>sd-objaverse-{task}.yaml"
    run->>run: "OmegaConf.load(config)"
    run->>run: "instantiate_from_config()"
    
    run->>load: "load_checkpoint(model, ckpt_path)"
    Note over load: "Handle 4ch→8ch conversion<br/>(lines 26-44)"
    load->>model: "model.load_state_dict()"
    model-->>run: "Model ready"
    
    run->>prep: "preprocess_image(image)"
    Note over prep: "Resize to 256×256<br/>Normalize to [-1, 1]"
    prep-->>run: "input_im tensor"
    
    Note over run: "Create task-specific T tensor<br/>and prompt (lines 129-141)"
    
    run->>sampler: "DDIMSampler(model)"
    sampler-->>run: "sampler instance"
    
    run->>sample: "sample_model(model, input_im,<br/>prompt, T, sampler, ...)"
    
    sample->>model: "get_learned_conditioning()<br/>(line 81)"
    Note over model: "Encode image + text"
    model-->>sample: "conditioning c"
    
    sample->>model: "cc_projection(c + T)<br/>(line 87)"
    model-->>sample: "projected conditioning"
    
    sample->>model: "encode_first_stage(input_im)<br/>(line 90)"
    model-->>sample: "latent encoding"
    
    sample->>sampler: "sampler.sample(S=ddim_steps,<br/>conditioning, shape, ...)"
    Note over sampler: "Iterative denoising<br/>with CFG scale"
    sampler-->>sample: "samples_ddim (latents)"
    
    sample->>model: "decode_first_stage(samples)<br/>(line 108)"
    model-->>sample: "x_samples_ddim (images)"
    
    Note over sample: "Clamp, denormalize<br/>(lines 109-110)"
    sample-->>run: "Generated image tensors"
    
    Note over run: "Convert to PIL images<br/>Save to disk (lines 157-169)"
    run-->>User: "Generated images saved"
```

**Sources:** [run_generation.py:114-170](), [run_generation.py:68-112](), [run_generation.py:16-53]()

## Checkpoint Loading and Model Initialization

The checkpoint loading system includes automatic adaptation for models with different input channel configurations. This is critical when loading Zero123 or Stable Diffusion checkpoints (4 input channels) into the 8-channel OBJect 3DIT architecture.

### Channel Adaptation Mechanism

The `load_checkpoint()` function [run_generation.py:16-53]() performs the following operations:

1. **Load checkpoint** from disk with `torch.load()` [run_generation.py:19]()
2. **Extract state dict** if nested under `"state_dict"` key [run_generation.py:21-23]()
3. **Check input channel mismatch** by comparing shapes [run_generation.py:26-29]()
4. **Zero-initialize new channels** and copy existing weights [run_generation.py:42-44]()
5. **Load with strict=False** to handle missing/unexpected keys [run_generation.py:46]()

The adaptation specifically handles the input block weights at `model.diffusion_model.input_blocks.0.0.weight`, ensuring the first 4 channels retain pretrained weights while additional channels are zero-initialized.

**Sources:** [run_generation.py:16-53]()

## Image Preprocessing

Input images undergo standardized preprocessing before conditioning:

| Operation | Implementation | Result |
|-----------|---------------|--------|
| Color conversion | `img.convert("RGB")` [run_generation.py:57]() | Ensures 3-channel RGB |
| Resizing | `torchvision.transforms.Resize((256,256))` [run_generation.py:59]() | Standard 256×256 resolution |
| Tensorization | `torchvision.transforms.ToTensor()` [run_generation.py:60]() | Converts to [0,1] tensor |
| Normalization | `img*2. - 1.` [run_generation.py:64]() | Maps to [-1, 1] range |
| Batching | `img.unsqueeze(0)` [run_generation.py:65]() | Adds batch dimension |

**Sources:** [run_generation.py:55-66]()

## Task-Specific Conditioning

Each editing task uses a 4-dimensional transformation tensor `T` that encodes task-specific parameters:

```mermaid
graph LR
    subgraph "Task Logic (run_generation.py:129-141)"
        TASK_ARG["args.task"]
    end
    
    subgraph "Rotation"
        ROT_CHECK["if args.task == 'rotate'"]
        ROT_PROMPT["prompt = f'rotate the {object_prompt}'"]
        ROT_T["T = [π/2, sin(azimuth), cos(azimuth), 0]"]
        ROT_ANGLE["azimuth = radians(args.rotation_angle)"]
    end
    
    subgraph "Removal"
        REM_CHECK["if args.task == 'remove'"]
        REM_PROMPT["prompt = f'remove the {object_prompt}'"]
        REM_T["T = [0, 0, 0, 0]"]
    end
    
    subgraph "Insertion"
        INS_CHECK["if args.task == 'insert'"]
        INS_PROMPT["prompt = f'insert the {object_prompt}'"]
        INS_T["T = [0, x, y, 0]"]
        INS_POS["x, y = map(float, args.position.split(','))"]
    end
    
    subgraph "Translation"
        TRANS_CHECK["if args.task == 'translate'"]
        TRANS_PROMPT["prompt = f'move the {object_prompt}'"]
        TRANS_T["T = [0, x, y, 0]"]
        TRANS_POS["x, y from args.position"]
    end
    
    TASK_ARG --> ROT_CHECK
    TASK_ARG --> REM_CHECK
    TASK_ARG --> INS_CHECK
    TASK_ARG --> TRANS_CHECK
    
    ROT_CHECK --> ROT_ANGLE
    ROT_ANGLE --> ROT_T
    ROT_CHECK --> ROT_PROMPT
    
    REM_CHECK --> REM_T
    REM_CHECK --> REM_PROMPT
    
    INS_CHECK --> INS_POS
    INS_POS --> INS_T
    INS_CHECK --> INS_PROMPT
    
    TRANS_CHECK --> TRANS_POS
    TRANS_POS --> TRANS_T
    TRANS_CHECK --> TRANS_PROMPT
```

The tensor `T` is concatenated with the learned conditioning before being projected by `model.cc_projection()` [run_generation.py:87](). This allows the model to condition generation on both the semantic content (from text and image embeddings) and the geometric transformation parameters.

**Sources:** [run_generation.py:128-141](), [run_generation.py:84-87]()

## Sampling Pipeline

The core generation happens in `sample_model()` [run_generation.py:68-112](), which implements classifier-free guidance with DDIM sampling:

### Conditioning Construction

```mermaid
graph TB
    INPUT["input_im<br/>input image tensor"]
    PROMPT["prompt<br/>task + object description"]
    T["T tensor<br/>task parameters"]
    
    COND["model.get_learned_conditioning()<br/>(line 81)"]
    NULL["null_prompt = get_learned_conditioning([''])<br/>(line 82)"]
    
    TILE["c.tile(n_samples, 1, 1)<br/>(line 81)"]
    UC["uc = null_prompt.repeat(...).tile(...)<br/>(line 83)"]
    
    T_EXPAND["T.repeat(n_samples, 1, 1).repeat(1, c.shape[1], 1)<br/>(line 84-85)"]
    
    CONCAT["torch.cat([c, T], dim=-1)<br/>(line 86)"]
    PROJ["model.cc_projection(c)<br/>(line 87)"]
    
    ENCODE["model.encode_first_stage(input_im).mode()<br/>(line 90)"]
    
    COND_DICT["cond = {<br/>'c_crossattn': [c],<br/>'c_concat': [latent]<br/>}<br/>(line 88-91)"]
    UNCOND_DICT["uncond = {<br/>'c_crossattn': [uc],<br/>'c_concat': [latent]<br/>}<br/>(line 92-95)"]
    
    INPUT --> COND
    PROMPT --> COND
    COND --> TILE
    NULL --> UC
    
    T --> T_EXPAND
    TILE --> CONCAT
    T_EXPAND --> CONCAT
    CONCAT --> PROJ
    
    INPUT --> ENCODE
    
    PROJ --> COND_DICT
    UC --> UNCOND_DICT
    ENCODE --> COND_DICT
    ENCODE --> UNCOND_DICT
```

### Iterative Denoising

The DDIM sampler performs `ddim_steps` iterations [run_generation.py:98]() of denoising in latent space:

1. **Initialize shape**: `[4, h//8, w//8]` for 256×256 output [run_generation.py:96-97]()
2. **Sample with guidance**: `sampler.sample()` with `unconditional_guidance_scale` [run_generation.py:98-106]()
3. **Decode latents**: `model.decode_first_stage()` converts to RGB [run_generation.py:108]()
4. **Clamp and normalize**: Ensures valid pixel range [run_generation.py:109-110]()

The `unconditional_guidance_scale` parameter (exposed as `--cfg_scale` in CLI) controls the strength of conditioning, with higher values producing outputs more faithful to the text prompt and task parameters.

**Sources:** [run_generation.py:68-112](), [run_generation.py:146-155]()

## Output Format

Generated images are saved as PNG files in the specified output directory [run_generation.py:165-169]():

```
save_dir/
├── input_im.png      # Preprocessed input image
├── 0.png             # Sample 1
├── 1.png             # Sample 2
├── ...
└── N.png             # Sample N (N = num_samples)
```

Each sample is generated independently from the same conditioning, providing multiple variations of the requested edit. The number of samples is controlled by `--num_samples` parameter [run_generation.py:220-223]().

**Sources:** [run_generation.py:156-169]()

## Command-Line Interface

The system is invoked through shell scripts that call `run_generation.py`:

| Script | Task | Example Command |
|--------|------|-----------------|
| `generate_scripts/rotate.sh` | Object rotation | Rotates specified object by angle |
| `generate_scripts/remove.sh` | Object removal | Removes specified object |
| `generate_scripts/insert.sh` | Object insertion | Inserts object at position |
| `generate_scripts/translate.sh` | Object translation | Moves object to position |

All scripts follow the pattern of executing `python run_generation.py` with task-specific arguments. The `--object_prompt` parameter should contain only the object description (e.g., "red car"), not the full editing instruction—the system automatically prepends task-specific verbs like "rotate the", "remove the", etc. [run_generation.py:129-141]().

**Sources:** [README.md:54-62](), [run_generation.py:176-235]()

## Usage Example

Basic workflow for running inference:

1. **Prepare checkpoint**: Download from HuggingFace or use trained checkpoint
2. **Prepare input**: Ensure image is accessible on disk
3. **Execute generation script**:
   ```bash
   . generate_scripts/rotate.sh
   ```
4. **Modify parameters** in the script as needed (checkpoint path, image path, object prompt, rotation angle)
5. **Retrieve outputs** from the specified `save_dir`

For complete parameter documentation and advanced configuration options, see [Generation Parameters and Configuration](#5.3).

**Sources:** [README.md:54-62]()

---

