<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlas-super-resolution · page 4 Model Architectures · fetched 2026-10-26 -->

# Model Architectures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ssr/models/ssr_esrgan_model.py](ssr/models/ssr_esrgan_model.py)
- [ssr/models/ssr_l2_model.py](ssr/models/ssr_l2_model.py)

</details>



This document provides an overview of the neural network model architectures available in the Satlas Super-Resolution system. It covers the high-level model organization, inheritance hierarchy, and the relationship between different architectural components.

For detailed information about specific ESRGAN implementations, see [ESRGAN Models](#4.1). For simple CNN baseline architectures, see [CNN Baselines](#4.2). For comprehensive coverage of training objectives, see [Loss Functions](#4.3).

## Model Registry System

The system uses BasicSR's model registry pattern to dynamically discover and instantiate models at runtime. All model classes are decorated with `@MODEL_REGISTRY.register()` and inherit from BasicSR's base model classes.

```mermaid
graph TB
    subgraph "BasicSR Framework"
        A[MODEL_REGISTRY]
        B[SRModel]
        C[SRGANModel]
    end
    
    subgraph "SSR Models"
        D[SSRESRGANModel]
        E[L2Model]
        F[OSMObjESRGANModel]
    end
    
    A --> D
    A --> E
    A --> F
    C --> D
    B --> E
    C --> F
    
    D --> G["net_g: Generator Network"]
    D --> H["net_d: Discriminator Network"]
    E --> I["net_g: Simple CNN"]
    F --> J["net_g: Generator Network"]
    F --> K["net_d: OSM-aware Discriminator"]
```

**Sources**: [ssr/models/ssr_esrgan_model.py:13,18](), [ssr/models/ssr_l2_model.py:10,14]()

## Architecture Overview

The system provides three primary model architectures, each designed for different use cases and complexity requirements:

| Model Class | Base Class | Primary Use Case | Complexity | Networks |
|-------------|------------|------------------|------------|----------|
| `SSRESRGANModel` | `SRGANModel` | Production super-resolution | High | Generator + Discriminator |
| `L2Model` | `SRModel` | Baseline comparison | Low | Generator only |
| `OSMObjESRGANModel` | `SRGANModel` | Geographic feature-aware | High | Generator + OSM-aware Discriminator |

**Sources**: [ssr/models/ssr_esrgan_model.py:19](), [ssr/models/ssr_l2_model.py:15]()

## Model Component Architecture

```mermaid
graph TB
    subgraph "SSRESRGANModel Components"
        A[SSRESRGANModel]
        B["net_g: Generator"]
        C["net_d: Discriminator"] 
        D["net_g_ema: EMA Generator"]
        E["usm_sharpener: USMSharp"]
        F["cri_pix: Pixel Loss"]
        G["cri_perceptual: Perceptual Loss"]
        H["cri_gan: GAN Loss"]
        I["ssim_loss: SSIM Loss"]
        J["clip_sim: CLIP Loss"]
    end
    
    subgraph "L2Model Components"
        K[L2Model]
        L["net_g: Generator"]
        M["MSE Loss (hardcoded)"]
        N["MAE Loss (hardcoded)"]
        O["SSIM Loss (hardcoded)"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    A --> J
    
    K --> L
    K --> M
    K --> N
    K --> O
```

**Sources**: [ssr/models/ssr_esrgan_model.py:31,43,53,67-95](), [ssr/models/ssr_l2_model.py:37-40]()

## Generator Network Integration

The models support different generator architectures through BasicSR's network building system:

```mermaid
graph LR
    subgraph "Configuration"
        A["network_g config"]
    end
    
    subgraph "BasicSR Registry"
        B["build_network()"]
        C["ARCH_REGISTRY"]
    end
    
    subgraph "Generator Architectures"
        D["SSR_RRDBNet"]
        E["SRCNN"]
        F["HighResNet"]
    end
    
    subgraph "Model Integration"
        G["SSRESRGANModel.net_g"]
        H["L2Model.net_g"]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    D --> G
    E --> H
    F --> H
```

**Sources**: [ssr/models/ssr_esrgan_model.py:43](), [ssr/models/ssr_l2_model.py:34]()

## Training and Inference Flow

The models implement standardized interfaces for training and inference:

```mermaid
flowchart TD
    subgraph "Data Flow"
        A["feed_data()"]
        B["lr: Low-res input"]
        C["gt: Ground truth"]
        D["old_hr: Historical high-res"]
    end
    
    subgraph "Training Flow"
        E["optimize_parameters()"]
        F["Generator forward pass"]
        G["Loss computation"]
        H["Discriminator training"]
        I["EMA update"]
    end
    
    subgraph "Inference Flow"
        J["test()"]
        K["Generator inference"]
        L["get_current_visuals()"]
    end
    
    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    
    B --> J
    J --> K
    K --> L
```

**Sources**: [ssr/models/ssr_esrgan_model.py:105-117,119-233,235-244](), [ssr/models/ssr_l2_model.py:25-28,30-54,56-60]()

## Discriminator Input Augmentation

The `SSRESRGANModel` supports feeding additional context to the discriminator beyond just the generated/real images:

```mermaid
graph TB
    subgraph "Discriminator Input Construction"
        A["Base Image"]
        B["old_hr: Historical high-res"]
        C["lr_resized: Upsampled low-res"]
        D["Concatenation Logic"]
        E["Final Discriminator Input"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    
    subgraph "Configuration Options"
        F["old_hr available?"]
        G["feed_disc_lr enabled?"]
        H["Input tensor construction"]
    end
    
    F --> H
    G --> H
    H --> D
```

**Sources**: [ssr/models/ssr_esrgan_model.py:171-178,202-213]()

## Model-Specific Features

### SSRESRGANModel Features
- **Exponential Moving Average (EMA)**: Maintains `net_g_ema` for stable inference [ssr/models/ssr_esrgan_model.py:36-50]()
- **USM Sharpening**: Applies unsharp masking to ground truth images [ssr/models/ssr_esrgan_model.py:31,109]()
- **Multi-loss Training**: Supports pixel, perceptual, GAN, SSIM, and CLIP losses [ssr/models/ssr_esrgan_model.py:67-95]()
- **Flexible Discriminator Input**: Can incorporate historical images and low-res context [ssr/models/ssr_esrgan_model.py:112-117]()

### L2Model Features
- **Hardcoded Loss Combination**: Uses fixed weights (0.3×MSE + 0.4×MAE + 0.3×SSIM) from WorldStrat paper [ssr/models/ssr_l2_model.py:37-40]()
- **Simple Training Loop**: No discriminator, straightforward generator training [ssr/models/ssr_l2_model.py:30-54]()
- **PSNR Loss Logging**: Computes PSNR in dB scale for monitoring [ssr/models/ssr_l2_model.py:43]()

**Sources**: [ssr/models/ssr_esrgan_model.py:1-354](), [ssr/models/ssr_l2_model.py:1-162]()

---

