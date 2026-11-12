<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page LineArt Detectors · fetched 2026-10-26 -->

# LineArt Detectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/leres/__init__.py](src/controlnet_aux/leres/__init__.py)
- [src/controlnet_aux/lineart/__init__.py](src/controlnet_aux/lineart/__init__.py)
- [src/controlnet_aux/lineart_anime/__init__.py](src/controlnet_aux/lineart_anime/__init__.py)

</details>



This page documents the line art generation detectors in controlnet_aux, which convert photographs and complex images into clean line art representations. These detectors use neural networks to extract line-based features suitable for ControlNet conditioning.

For line segment detection (MLSD), see [Line Segment Detection](#4.4.2). For edge detection systems, see [Edge Detection](#4.1).

## Architecture Overview

The line art detection system provides two specialized detectors with different neural network architectures and use cases:

```mermaid
graph TB
    subgraph "LineArt Detection System"
        LA[LineartDetector] 
        LAA[LineartAnimeDetector]
    end
    
    subgraph "LineartDetector Architecture"
        GEN[Generator]
        COARSE[CoarseGenerator] 
        RES[ResidualBlock]
        GEN --> RES
        COARSE --> RES
    end
    
    subgraph "LineartAnimeDetector Architecture"
        UNET[UnetGenerator]
        SKIP[UnetSkipConnectionBlock]
        UNET --> SKIP
    end
    
    subgraph "Model Files"
        SK1["sk_model.pth"]
        SK2["sk_model2.pth"] 
        NETG["netG.pth"]
    end
    
    subgraph "Common Processing"
        HWC3_UTIL[HWC3]
        RESIZE_UTIL[resize_image]
        DEVICE_MGT[Device Management]
    end
    
    LA --> GEN
    LA --> COARSE
    LAA --> UNET
    
    LA --> SK1
    LA --> SK2
    LAA --> NETG
    
    LA --> HWC3_UTIL
    LA --> RESIZE_UTIL
    LAA --> HWC3_UTIL
    LAA --> RESIZE_UTIL
    
    LA --> DEVICE_MGT
    LAA --> DEVICE_MGT
```

Sources: [src/controlnet_aux/lineart/__init__.py:94-119](), [src/controlnet_aux/lineart_anime/__init__.py:116-139]()

## LineartDetector (General Line Art)

The `LineartDetector` implements a dual-model system for general-purpose line art generation using a Generator network with residual blocks.

### Dual Model Architecture

```mermaid
graph TB
    subgraph "LineartDetector Class"
        DETECTOR[LineartDetector]
        MODEL[self.model]
        COARSE_MODEL[self.model_coarse]
    end
    
    subgraph "Generator Architecture"
        subgraph "Initial Block"
            REFLECT1[ReflectionPad2d_3]
            CONV1[Conv2d_7x7]
            NORM1[InstanceNorm2d]
            RELU1[ReLU]
        end
        
        subgraph "Downsampling"
            DOWN1[Conv2d_3x3_stride2]
            DOWN2[Conv2d_3x3_stride2]
        end
        
        subgraph "Residual Blocks"
            RES1[ResidualBlock]
            RES2[ResidualBlock]
            RES3[ResidualBlock]
        end
        
        subgraph "Upsampling"
            UP1[ConvTranspose2d]
            UP2[ConvTranspose2d]
        end
        
        subgraph "Output"
            REFLECT2[ReflectionPad2d_3]
            CONV_OUT[Conv2d_7x7]
            SIGMOID[Sigmoid]
        end
    end
    
    DETECTOR --> MODEL
    DETECTOR --> COARSE_MODEL
    
    MODEL --> REFLECT1
    COARSE_MODEL --> REFLECT1
    
    REFLECT1 --> CONV1 --> NORM1 --> RELU1
    RELU1 --> DOWN1 --> DOWN2
    DOWN2 --> RES1 --> RES2 --> RES3
    RES3 --> UP1 --> UP2
    UP2 --> REFLECT2 --> CONV_OUT --> SIGMOID
```

Sources: [src/controlnet_aux/lineart/__init__.py:36-92](), [src/controlnet_aux/lineart/__init__.py:17-33]()

### Model Loading and Usage

The detector loads two separate models for different levels of detail:

| Model | Filename | Purpose | Parameters |
|-------|----------|---------|------------|
| Fine Model | `sk_model.pth` | Detailed line art | 3 residual blocks |
| Coarse Model | `sk_model2.pth` | Simplified line art | 3 residual blocks |

```python
# Model selection logic
model = self.model_coarse if coarse else self.model
```

Sources: [src/controlnet_aux/lineart/__init__.py:100-119](), [src/controlnet_aux/lineart/__init__.py:142]()

## LineartAnimeDetector (Anime-Specific)

The `LineartAnimeDetector` uses a U-Net architecture optimized for anime and cartoon-style images, producing clean line art with characteristic anime aesthetics.

### U-Net Architecture

```mermaid
graph TB
    subgraph "UnetGenerator Structure"
        INPUT[Input_3_channels]
        
        subgraph "Encoder Path"
            DOWN1[Conv2d_stride2]
            DOWN2[Conv2d_stride2] 
            DOWN3[Conv2d_stride2]
            DOWN4[Conv2d_stride2]
        end
        
        subgraph "Bottleneck"
            INNER[UnetSkipConnectionBlock_innermost]
        end
        
        subgraph "Decoder Path"
            UP1[ConvTranspose2d_stride2]
            UP2[ConvTranspose2d_stride2]
            UP3[ConvTranspose2d_stride2] 
            UP4[ConvTranspose2d_stride2]
        end
        
        subgraph "Skip Connections"
            SKIP1[Skip_Connection_1]
            SKIP2[Skip_Connection_2]
            SKIP3[Skip_Connection_3]
        end
        
        OUTPUT[Output_1_channel]
    end
    
    subgraph "UnetSkipConnectionBlock Details"
        DOWNCONV[Conv2d_4x4_stride2]
        DOWNRELU[LeakyReLU_0.2]
        DOWNNORM[InstanceNorm2d]
        UPRELU[ReLU]
        UPCONV[ConvTranspose2d_4x4_stride2]
        UPNORM[InstanceNorm2d]
        TANH[Tanh]
    end
    
    INPUT --> DOWN1
    DOWN1 --> DOWN2
    DOWN2 --> DOWN3  
    DOWN3 --> DOWN4
    DOWN4 --> INNER
    
    INNER --> UP1
    UP1 --> UP2
    UP2 --> UP3
    UP3 --> UP4
    UP4 --> OUTPUT
    
    DOWN1 -.-> SKIP1 -.-> UP3
    DOWN2 -.-> SKIP2 -.-> UP2  
    DOWN3 -.-> SKIP3 -.-> UP1
    
    DOWNCONV --> DOWNRELU --> DOWNNORM
    UPRELU --> UPCONV --> UPNORM
```

Sources: [src/controlnet_aux/lineart_anime/__init__.py:16-44](), [src/controlnet_aux/lineart_anime/__init__.py:47-113]()

### Skip Connection Mechanism

The U-Net implements skip connections through concatenation:

```python
# Skip connection logic in UnetSkipConnectionBlock
def forward(self, x):
    if self.outermost:
        return self.model(x)
    else:   # add skip connections
        return torch.cat([x, self.model(x)], 1)
```

Sources: [src/controlnet_aux/lineart_anime/__init__.py:109-113]()

## Processing Pipeline

Both detectors follow a similar processing pipeline with detector-specific preprocessing and postprocessing steps:

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT_IMG[input_image]
        NUMPY_CONV[numpy_conversion]
        HWC3_PROC[HWC3_processing]
        RESIZE_DETECT[resize_image_detect_resolution]
    end
    
    subgraph "Detector-Specific Preprocessing"
        subgraph "LineartDetector"
            NORM_01[normalize_0_to_1]
            TENSOR_L[to_tensor_lineart]
        end
        
        subgraph "LineartAnimeDetector"
            PAD_256[pad_to_256_multiple]
            NORM_NEG1_1[normalize_-1_to_1]
            TENSOR_A[to_tensor_anime]
        end
    end
    
    subgraph "Neural Network Processing"
        MODEL_FORWARD[model_forward_pass]
        OUTPUT_TENSOR[output_tensor]
    end
    
    subgraph "Postprocessing"
        DENORM[denormalize]
        RESIZE_FINAL[resize_to_image_resolution]
        INVERT[invert_255_minus_output]
        FORMAT_OUT[format_output_pil_or_np]
    end
    
    INPUT_IMG --> NUMPY_CONV --> HWC3_PROC --> RESIZE_DETECT
    
    RESIZE_DETECT --> NORM_01
    RESIZE_DETECT --> PAD_256
    
    NORM_01 --> TENSOR_L
    PAD_256 --> NORM_NEG1_1 --> TENSOR_A
    
    TENSOR_L --> MODEL_FORWARD
    TENSOR_A --> MODEL_FORWARD
    
    MODEL_FORWARD --> OUTPUT_TENSOR --> DENORM --> RESIZE_FINAL --> INVERT --> FORMAT_OUT
```

Sources: [src/controlnet_aux/lineart/__init__.py:126-167](), [src/controlnet_aux/lineart_anime/__init__.py:145-189]()

### Key Processing Differences

| Aspect | LineartDetector | LineartAnimeDetector |
|--------|-----------------|---------------------|
| Input Normalization | `[0, 1]` | `[-1, 1]` |
| Padding Strategy | None | 256-pixel multiples |
| Model Selection | Coarse/Fine toggle | Single model |
| Output Processing | Direct denormalization | Clipping + denormalization |

Sources: [src/controlnet_aux/lineart/__init__.py:147-148](), [src/controlnet_aux/lineart_anime/__init__.py:167-170]()

## Model Loading and Configuration

Both detectors implement the standard `from_pretrained` pattern for loading models from Hugging Face Hub:

```mermaid
graph TB
    subgraph "Model Loading Flow"
        FROM_PRETRAINED[from_pretrained_classmethod]
        PATH_CHECK[check_local_vs_hub]
        
        subgraph "LineartDetector Loading"
            LOAD_MAIN[load_sk_model.pth]
            LOAD_COARSE[load_sk_model2.pth]
            CREATE_GEN1[create_Generator_3_1_3]
            CREATE_GEN2[create_Generator_3_1_3]
        end
        
        subgraph "LineartAnimeDetector Loading"
            LOAD_NETG[load_netG.pth]
            CREATE_UNET[create_UnetGenerator]
            CLEAN_KEYS[clean_module_keys]
        end
        
        EVAL_MODE[set_eval_mode]
        RETURN_INSTANCE[return_detector_instance]
    end
    
    FROM_PRETRAINED --> PATH_CHECK
    
    PATH_CHECK --> LOAD_MAIN
    PATH_CHECK --> LOAD_NETG
    
    LOAD_MAIN --> CREATE_GEN1
    LOAD_COARSE --> CREATE_GEN2
    LOAD_NETG --> CREATE_UNET --> CLEAN_KEYS
    
    CREATE_GEN1 --> EVAL_MODE
    CREATE_GEN2 --> EVAL_MODE
    CLEAN_KEYS --> EVAL_MODE
    
    EVAL_MODE --> RETURN_INSTANCE
```

Sources: [src/controlnet_aux/lineart/__init__.py:99-119](), [src/controlnet_aux/lineart_anime/__init__.py:120-139]()

### Device Management

Both detectors support device migration through the `.to(device)` method:

```python
def to(self, device):
    self.model.to(device)
    self.model_coarse.to(device)  # LineartDetector only
    return self
```

Sources: [src/controlnet_aux/lineart/__init__.py:121-124](), [src/controlnet_aux/lineart_anime/__init__.py:141-143]()

---

