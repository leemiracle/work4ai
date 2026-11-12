<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/efficientvit · page 3 Deep Compression Autoencoder · fetched 2026-10-30 -->

# Deep Compression Autoencoder

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [applications/dc_ae/dc_ae_generate_latent.py](applications/dc_ae/dc_ae_generate_latent.py)
- [assets/cityscapes_l1.gif](assets/cityscapes_l1.gif)
- [assets/dc_ae_diffusion_demo.gif](assets/dc_ae_diffusion_demo.gif)
- [efficientvit/ae_model_zoo.py](efficientvit/ae_model_zoo.py)
- [efficientvit/models/efficientvit/dc_ae.py](efficientvit/models/efficientvit/dc_ae.py)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

The Deep Compression Autoencoder (DC-AE) is a specialized neural network architecture within the EfficientViT framework designed to achieve high spatial compression of images while preserving essential visual information. It transforms images into a compact latent representation with spatial reduction factors of 32×, 64×, or 128×. These compressed latent representations serve as the foundation for various diffusion models, enabling efficient image generation and manipulation.

For information about diffusion models that use DC-AE latent representations, see [Diffusion Models](#4).

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:402-434]()
- [efficientvit/ae_model_zoo.py:13-22]()

## Architecture Overview

The DC-AE follows an encoder-decoder architecture specifically tailored for achieving high compression ratios while maintaining reconstruction quality.

DC-AE Architecture
```mermaid
graph TD
    subgraph "DCAE Class"
        Input["Input Image"] --> Encoder["Encoder Class"]
        Encoder --> LatentSpace["Latent Representation"]
        LatentSpace --> Decoder["Decoder Class"]
        Decoder --> Output["Reconstructed Image"]
    end
    
    subgraph "Model Variants"
        F32["dc_ae_f32c32()"]
        F64["dc_ae_f64c128()"]
        F128["dc_ae_f128c512()"]
    end
    
    subgraph "Registration & Loading"
        Registry["REGISTERED_DCAE_MODEL Dictionary"]
        Create["create_dc_ae_model_cfg() Function"]
        HF["DCAE_HF Class for Loading"]
    end
    
    F32 --> Registry
    F64 --> Registry
    F128 --> Registry
    Registry --> Create
    Create --> HF
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:402-434]()
- [efficientvit/ae_model_zoo.py:13-37]()

### Key Features

1. **High Spatial Compression**: DC-AE achieves compression ratios of 32×, 64×, or 128× in spatial dimensions, significantly reducing memory requirements and computational costs for downstream tasks.

2. **Hybrid Block Architecture**: Combines ResBlocks and EfficientViT blocks to balance computational efficiency and representation capability.

3. **Configurable Components**: Flexible configuration system for specifying block types, channel widths, and depths for different compression requirements.

4. **Integration with Diffusion Models**: Designed specifically to work with latent diffusion models for image generation tasks.

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:80-103]()
- [efficientvit/models/efficientvit/dc_ae.py:27-77]()

### Model Variants

DC-AE comes in three main variants with different compression factors and latent space dimensions:

| Variant | Function | Spatial Compression | Latent Channels | Configuration Structure |
|---------|----------|---------------------|-----------------|------------------------|
| dc_ae_f32c32 | `dc_ae_f32c32()` | 32× | 32 | 6 stages, mix of ResBlock and EViT_GLU |
| dc_ae_f64c128 | `dc_ae_f64c128()` | 64× | 128 | 7 stages, mix of ResBlock and EViT_GLU |
| dc_ae_f128c512 | `dc_ae_f128c512()` | 128× | 512 | 8 stages, mix of ResBlock and EViT_GLU |

Sources:
- [efficientvit/ae_model_zoo.py:13-22]()
- [efficientvit/models/efficientvit/dc_ae.py:437-492]()

## Encoder-Decoder Architecture

The DC-AE consists of an encoder that progressively compresses the input image and a decoder that reconstructs the image from the compressed latent representation.

Encoder-Decoder Data Flow
```mermaid
graph TD
    subgraph "Encoder Data Flow"
        EIn["Input Image"] --> EProjectIn["project_in<br>(build_encoder_project_in_block)"]
        EProjectIn --> EStages["stages<br>(OpSequential Modules)"]
        EStages --> EProjectOut["project_out<br>(build_encoder_project_out_block)"]
        EProjectOut --> EOut["Latent Representation"]
    end
    
    subgraph "Decoder Data Flow"
        DIn["Latent Representation"] --> DProjectIn["project_in<br>(build_decoder_project_in_block)"]
        DProjectIn --> DStages["stages<br>(OpSequential Modules)"]
        DStages --> DProjectOut["project_out<br>(build_decoder_project_out_block)"]
        DProjectOut --> DOut["Reconstructed Image"]
    end
    
    EOut --> DIn
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:323-330]()
- [efficientvit/models/efficientvit/dc_ae.py:392-399]()

### Encoder Implementation

The Encoder progressively compresses the input image through a series of configurable stages:

Block Structure and Flow
```mermaid
graph TD
    subgraph "Encoder Block Structure"
        EIn["Input Image"] --> EProjectIn["Project In Block"]
        
        subgraph "Multiple Stages"
            Stage1["Stage 1<br>(depth_list[0] blocks)"]
            Stage2["Stage 2<br>(depth_list[1] blocks)"]
            StageN["...<br>Additional Stages"]
            
            subgraph "Stage Internal Structure"
                Block1["Block 1<br>(ResBlock or EViT_GLU)"]
                Block2["Block 2<br>(ResBlock or EViT_GLU)"]
                BlockN["...<br>Additional Blocks"]
                DS["Downsample Block<br>(if not last stage)"]
                
                Block1 --> Block2
                Block2 --> BlockN
                BlockN --> DS
            end
        end
        
        EProjectIn --> Stage1
        Stage1 --> Stage2
        Stage2 --> StageN
        StageN --> EProjectOut["Project Out Block"]
        EProjectOut --> EOut["Latent Representation"]
    end
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:278-331]()
- [efficientvit/models/efficientvit/dc_ae.py:290-312]()

### Decoder Implementation

The Decoder reconstructs the image from the latent representation through a similar series of stages:

```mermaid
graph TD
    subgraph "Decoder Block Structure"
        DIn["Latent Representation"] --> DProjectIn["Project In Block"]
        
        subgraph "Multiple Stages (Reversed Order)"
            Stage1["Last Stage<br>(depth_list[-1] blocks)"]
            Stage2["Second-to-Last Stage<br>(depth_list[-2] blocks)"]
            StageN["...<br>Earlier Stages"]
            
            subgraph "Stage Internal Structure"
                US["Upsample Block<br>(if not first stage)"]
                Block1["Block 1<br>(ResBlock or EViT_GLU)"]
                Block2["Block 2<br>(ResBlock or EViT_GLU)"]
                BlockN["...<br>Additional Blocks"]
                
                US --> Block1
                Block1 --> Block2
                Block2 --> BlockN
            end
        end
        
        DProjectIn --> Stage1
        Stage1 --> Stage2
        Stage2 --> StageN
        StageN --> DProjectOut["Project Out Block"]
        DProjectOut --> DOut["Reconstructed Image"]
    end
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:333-399]()
- [efficientvit/models/efficientvit/dc_ae.py:354-380]()

### Block Types

DC-AE employs several types of building blocks implemented in the `build_block` function:

1. **ResBlock**: Residual blocks with convolutional layers, normalization, and activation functions
2. **EViT_GLU**: EfficientViT blocks with GLU-based MBConv local modules without multi-scale attention
3. **EViTS5_GLU**: EfficientViT blocks with GLU-based MBConv and scale-5 multi-scale attention

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:80-103]()
- [efficientvit/models/efficientvit/dc_ae.py:106-121]()

## Implementation Details

The DC-AE is implemented in the `efficientvit/models/efficientvit/dc_ae.py` file, with model configurations and utilities in the `efficientvit/ae_model_zoo.py` file.

### Main Classes and Methods

Code Structure
```mermaid
graph TD
    subgraph "DCAE Class Structure"
        DCAE["DCAE Class"]
        Encoder["Encoder Class"]
        Decoder["Decoder Class"]
        
        EncoderConfig["EncoderConfig Dataclass"]
        DecoderConfig["DecoderConfig Dataclass"]
        DCAEConfig["DCAEConfig Dataclass"]
        
        BuildBlock["build_block()"]
        BuildStageMain["build_stage_main()"]
        BuildDownsample["build_downsample_block()"]
        BuildUpsample["build_upsample_block()"]
    end
    
    subgraph "Primary Methods"
        Encode["encode()"]
        Decode["decode()"]
        Forward["forward()"]
        SpatialCompressionRatio["spatial_compression_ratio Property"]
    end
    
    DCAEConfig --> DCAE
    EncoderConfig --> Encoder
    DecoderConfig --> Decoder
    
    DCAE --> Encoder
    DCAE --> Decoder
    
    BuildBlock --> BuildStageMain
    BuildStageMain --> Encoder
    BuildStageMain --> Decoder
    
    BuildDownsample --> Encoder
    BuildUpsample --> Decoder
    
    DCAE --> Encode
    DCAE --> Decode
    DCAE --> Forward
    DCAE --> SpatialCompressionRatio
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:27-77]()
- [efficientvit/models/efficientvit/dc_ae.py:402-434]()

### Configuration System

The DC-AE configuration system is based on dataclasses with nested structures:

1. **DCAEConfig**: Top-level configuration containing:
   - `in_channels`: Input image channels (typically 3 for RGB)
   - `latent_channels`: Number of channels in the latent space
   - `encoder`: Nested EncoderConfig
   - `decoder`: Nested DecoderConfig
   - `pretrained_path`: Path to pretrained weights
   - `scaling_factor`: Optional scaling factor for latent representations

2. **EncoderConfig**: Configuration for the encoder with:
   - `width_list`: List of channel dimensions for each stage
   - `depth_list`: List of block depths for each stage
   - `block_type`: Type of blocks to use (ResBlock, EViT_GLU, etc.)
   - `norm`: Normalization type
   - `act`: Activation function
   - `downsample_block_type`: Type of downsampling block

3. **DecoderConfig**: Similar configuration for the decoder

Example configuration for the dc_ae_f32c32 variant:

```
latent_channels=32
encoder.block_type=[ResBlock,ResBlock,ResBlock,EViT_GLU,EViT_GLU,EViT_GLU]
encoder.width_list=[128,256,512,512,1024,1024] 
encoder.depth_list=[0,4,8,2,2,2]
decoder.block_type=[ResBlock,ResBlock,ResBlock,EViT_GLU,EViT_GLU,EViT_GLU]
decoder.width_list=[128,256,512,512,1024,1024] 
decoder.depth_list=[0,5,10,2,2,2]
decoder.norm=[bn2d,bn2d,bn2d,trms2d,trms2d,trms2d] 
decoder.act=[relu,relu,relu,silu,silu,silu]
```

Sources:
- [efficientvit/models/efficientvit/dc_ae.py:27-77]()
- [efficientvit/models/efficientvit/dc_ae.py:439-446]()

## Usage and Applications

### Generating Latent Representations

DC-AE can be used to generate latent representations of images for use with diffusion models or other generative tasks.

Latent Generation Process
```mermaid
graph TD
    subgraph "GenerateLatentConfig"
        Config["GenerateLatentConfig"]
        ModelName["model_name"]
        ImageRoot["image_root_path"]
        LatentRoot["latent_root_path"]
        Resolution["resolution"]
        ScalingFactor["scaling_factor"]
    end
    
    subgraph "Process Flow"
        LoadModel["Load Model<br>DCAE_HF.from_pretrained()"]
        LoadData["Load Dataset<br>CustomImageFolder"]
        ProcessBatch["Process Batch"]
        Encode["model.encode(images)"]
        Scale["latents * scaling_factor"]
        Save["np.save(latent_path, latent)"]
    end
    
    Config --> ModelName
    ModelName --> LoadModel
    Config --> ImageRoot
    ImageRoot --> LoadData
    Config --> Resolution
    Resolution --> LoadData
    Config --> ScalingFactor
    ScalingFactor --> Scale
    Config --> LatentRoot
    LatentRoot --> Save
    
    LoadModel --> ProcessBatch
    LoadData --> ProcessBatch
    ProcessBatch --> Encode
    Encode --> Scale
    Scale --> Save
```

Sources:
- [applications/dc_ae/dc_ae_generate_latent.py:30-46]()
- [applications/dc_ae/dc_ae_generate_latent.py:57-145]()

Example code for generating latent representations:

```python
# Load model
model = DCAE_HF.from_pretrained("mit-han-lab/dc-ae-f32c32-in-1.0").to(device=device, dtype=dtype)

# Process image
images = load_and_preprocess_images()  # Your preprocessing code

# Generate latent representation
latents = model.encode(images)
latents = latents * scaling_factor  # Apply scaling factor

# Save latent representation
np.save("latent.npy", latents.cpu().numpy())
```

Sources:
- [applications/dc_ae/dc_ae_generate_latent.py:111-134]()

### Integration with Diffusion Models

DC-AE is designed to work seamlessly with diffusion models in the EfficientViT ecosystem:

Integration with Diffusion Pipeline
```mermaid
graph TD
    subgraph "Latent Diffusion Pipeline"
        OriginalImage["Original Image"] --> DC_AE_Encoder["DC-AE Encoder"]
        DC_AE_Encoder --> LatentRepresentation["Latent Representation"]
        LatentRepresentation --> DiffusionModel["Diffusion Model<br>(UViT/DiT)"]
        DiffusionModel --> GeneratedLatent["Generated Latent"]
        GeneratedLatent --> DC_AE_Decoder["DC-AE Decoder"]
        DC_AE_Decoder --> GeneratedImage["Generated Image"]
    end
    
    subgraph "Alternative Autoencoders"
        DCAE_HF["DCAE_HF Class"]
        AutoencoderKL["AutoencoderKL Class<br>(SD-VAE, FLUX-VAE)"]
    end
    
    DCAE_HF -.-> DC_AE_Encoder
    DCAE_HF -.-> DC_AE_Decoder
    AutoencoderKL -.-> DC_AE_Encoder
    AutoencoderKL -.-> DC_AE_Decoder
```

Sources:
- [applications/dc_ae/dc_ae_generate_latent.py:70-77]()
- [efficientvit/ae_model_zoo.py:40-66]()

## Conclusion

The Deep Compression Autoencoder (DC-AE) is a key component in the EfficientViT ecosystem, providing efficient image compression for latent diffusion models. Its configurable architecture with varying compression ratios allows for flexibility in balancing reconstruction quality and computational efficiency. The integration of ResBlocks and EfficientViT blocks ensures effective feature extraction while maintaining a lightweight design.

---

