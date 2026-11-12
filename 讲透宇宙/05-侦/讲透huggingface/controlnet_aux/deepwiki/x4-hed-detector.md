<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page HED Detector · fetched 2026-10-26 -->

# HED Detector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/hed/__init__.py](src/controlnet_aux/hed/__init__.py)
- [src/controlnet_aux/mlsd/__init__.py](src/controlnet_aux/mlsd/__init__.py)

</details>



The HED Detector implements Holistically-nested Edge Detection (HED) for multi-scale edge map generation with ControlNet optimizations. This detector is specifically designed for ControlNet applications and image-to-image translation tasks, producing smoother edges than standard implementations while supporting advanced features like scribble mode processing.

This document covers the `HEDdetector` class implementation, neural network architecture, and usage patterns. For other edge detection methods, see [Canny Detector](#4.1.2), [PiDiNet Detector](#4.1.3), and [TEED and Anyline Detectors](#4.1.4). For general edge detection concepts, see [Edge Detection](#4.1).

## Architecture Overview

The HED Detector consists of three main architectural components: the detector interface, the neural network model, and convolutional building blocks.

### Class Hierarchy

```mermaid
graph TD
    HEDdetector["HEDdetector<br/>Main Interface"]
    ControlNetHED_Apache2["ControlNetHED_Apache2<br/>Neural Network Model"]
    DoubleConvBlock["DoubleConvBlock<br/>Convolutional Building Block"]
    
    HEDdetector -->|"contains"| ControlNetHED_Apache2
    ControlNetHED_Apache2 -->|"5 instances"| DoubleConvBlock
    
    subgraph "Model Loading"
        from_pretrained["from_pretrained()<br/>Factory Method"]
        hf_hub_download["hf_hub_download()<br/>Model Download"]
        load_state_dict["load_state_dict()<br/>Weight Loading"]
    end
    
    subgraph "Processing Pipeline"
        __call__["__call__()<br/>Main Processing"]
        resize_image["resize_image()<br/>Input Preprocessing"]
        nms["nms()<br/>Scribble Mode NMS"]
        safe_step["safe_step()<br/>Safe Processing"]
    end
    
    HEDdetector --> from_pretrained
    from_pretrained --> hf_hub_download
    from_pretrained --> load_state_dict
    
    HEDdetector --> __call__
    __call__ --> resize_image
    __call__ --> nms
    __call__ --> safe_step
```

**Sources**: [src/controlnet_aux/hed/__init__.py:59-129]()

### Neural Network Architecture

The `ControlNetHED_Apache2` model implements a VGG-inspired architecture with five hierarchical blocks for multi-scale edge detection:

```mermaid
graph TB
    subgraph "Input Processing"
        input["Input Image<br/>RGB (H×W×3)"]
        norm["Normalization<br/>x - self.norm"]
    end
    
    subgraph "Hierarchical Blocks"
        block1["block1<br/>DoubleConvBlock<br/>3→64, 2 layers"]
        block2["block2<br/>DoubleConvBlock<br/>64→128, 2 layers"]
        block3["block3<br/>DoubleConvBlock<br/>128→256, 3 layers"]
        block4["block4<br/>DoubleConvBlock<br/>256→512, 3 layers"]
        block5["block5<br/>DoubleConvBlock<br/>512→512, 3 layers"]
    end
    
    subgraph "Multi-Scale Outputs"
        proj1["projection1<br/>64→1"]
        proj2["projection2<br/>128→1"]
        proj3["projection3<br/>256→1"]
        proj4["projection4<br/>512→1"]
        proj5["projection5<br/>512→1"]
    end
    
    subgraph "Downsampling"
        ds1["No Downsampling"]
        ds2["2×2 MaxPool"]
        ds3["2×2 MaxPool"]
        ds4["2×2 MaxPool"]
        ds5["2×2 MaxPool"]
    end
    
    input --> norm
    norm --> block1
    block1 --> ds1
    block1 --> proj1
    ds1 --> block2
    block2 --> ds2
    block2 --> proj2
    ds2 --> block3
    block3 --> ds3
    block3 --> proj3
    ds3 --> block4
    block4 --> ds4
    block4 --> proj4
    ds4 --> block5
    block5 --> ds5
    block5 --> proj5
```

**Sources**: [src/controlnet_aux/hed/__init__.py:40-57](), [src/controlnet_aux/hed/__init__.py:21-37]()

## Core Components

### DoubleConvBlock Structure

The `DoubleConvBlock` class implements the fundamental building block used throughout the HED architecture:

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `convs` Sequential | Main convolution layers | Variable layer count (2-3) |
| `projection` Conv2d | 1×1 conv to single channel | `output_channels → 1` |
| Downsampling | Optional 2×2 max pooling | Applied between blocks |
| Activation | ReLU after each conv | Applied in forward pass |

The block processes features through multiple 3×3 convolutions with padding, followed by a 1×1 projection layer for edge map generation.

**Sources**: [src/controlnet_aux/hed/__init__.py:21-37]()

### HEDdetector Interface

The `HEDdetector` class provides the main user interface with the following key methods:

```mermaid
graph LR
    subgraph "Initialization"
        from_pretrained["from_pretrained()<br/>Load pretrained model"]
        __init__["__init__()<br/>Direct initialization"]
    end
    
    subgraph "Device Management"
        to_device["to()<br/>Move to device"]
    end
    
    subgraph "Processing"
        call_method["__call__()<br/>Main processing method"]
    end
    
    subgraph "Parameters"
        detect_res["detect_resolution<br/>Processing resolution"]
        image_res["image_resolution<br/>Output resolution"]
        safe_mode["safe<br/>Safe step processing"]
        scribble_mode["scribble<br/>NMS processing"]
        output_type["output_type<br/>pil or np"]
    end
    
    from_pretrained --> HEDdetector
    __init__ --> HEDdetector
    HEDdetector --> to_device
    HEDdetector --> call_method
    
    call_method --> detect_res
    call_method --> image_res
    call_method --> safe_mode
    call_method --> scribble_mode
    call_method --> output_type
```

**Sources**: [src/controlnet_aux/hed/__init__.py:59-81](), [src/controlnet_aux/hed/__init__.py:82-129]()

## Processing Pipeline

### Standard Edge Detection Flow

The HED detector processes images through the following pipeline:

1. **Input Preprocessing**: Convert to numpy array and apply `HWC3` formatting
2. **Resolution Scaling**: Resize input to `detect_resolution` 
3. **Neural Network Inference**: Generate 5 multi-scale edge projections
4. **Edge Fusion**: Combine projections using sigmoid-weighted averaging
5. **Post-processing**: Apply optional safe step or scribble mode processing
6. **Output Scaling**: Resize to `image_resolution` and format output

```mermaid
graph TD
    subgraph "Input Stage"
        input_img["Input Image<br/>PIL/numpy"]
        hwc3["HWC3()<br/>Format normalization"]
        resize_detect["resize_image()<br/>detect_resolution"]
    end
    
    subgraph "Neural Processing"
        tensor_conv["Tensor Conversion<br/>torch.from_numpy()"]
        rearrange_input["rearrange()<br/>h w c → 1 c h w"]
        netNetwork["netNetwork()<br/>5 edge projections"]
        edge_fusion["Edge Fusion<br/>sigmoid + mean"]
    end
    
    subgraph "Post-processing"
        safe_check{"safe=True?"}
        safe_step_proc["safe_step()<br/>Safety processing"]
        scribble_check{"scribble=True?"}
        nms_proc["nms()<br/>Non-max suppression"]
        gaussian_blur["GaussianBlur()<br/>Smoothing"]
    end
    
    subgraph "Output Stage"
        resize_output["resize_image()<br/>image_resolution"]
        format_output["Format Output<br/>PIL or numpy"]
    end
    
    input_img --> hwc3
    hwc3 --> resize_detect
    resize_detect --> tensor_conv
    tensor_conv --> rearrange_input
    rearrange_input --> netNetwork
    netNetwork --> edge_fusion
    
    edge_fusion --> safe_check
    safe_check -->|"Yes"| safe_step_proc
    safe_check -->|"No"| scribble_check
    safe_step_proc --> scribble_check
    
    scribble_check -->|"Yes"| nms_proc
    scribble_check -->|"No"| resize_output
    nms_proc --> gaussian_blur
    gaussian_blur --> resize_output
    
    resize_output --> format_output
```

**Sources**: [src/controlnet_aux/hed/__init__.py:82-129]()

### Scribble Mode Processing

When `scribble=True`, the detector applies specialized post-processing for sketch-like output:

| Step | Function | Parameters | Purpose |
|------|----------|------------|---------|
| 1. NMS | `nms()` | `threshold=127, sigma=3.0` | Remove duplicate edges |
| 2. Gaussian Blur | `cv2.GaussianBlur()` | `sigma=3.0` | Smooth edge lines |
| 3. Thresholding | Binary threshold | `>4 → 255, <255 → 0` | Create clean binary edges |

**Sources**: [src/controlnet_aux/hed/__init__.py:120-124]()

## Model Loading and Configuration

### Pretrained Model Loading

The HED detector supports flexible model loading through the `from_pretrained` classmethod:

```mermaid
graph TD
    subgraph "Model Loading Path"
        pretrained_path["pretrained_model_or_path<br/>String parameter"]
        path_check{"Is directory?"}
        local_path["Local file path<br/>join(path, filename)"]
        hf_download["hf_hub_download()<br/>Download from Hub"]
    end
    
    subgraph "Model Initialization"
        create_network["ControlNetHED_Apache2()<br/>Create model instance"]
        load_weights["load_state_dict()<br/>Load checkpoint weights"]
        set_eval["float().eval()<br/>Set evaluation mode"]
    end
    
    subgraph "Default Configuration"
        default_filename["filename = 'ControlNetHED.pth'"]
        cache_dir_param["cache_dir parameter"]
        local_files_param["local_files_only parameter"]
    end
    
    pretrained_path --> path_check
    path_check -->|"Yes"| local_path
    path_check -->|"No"| hf_download
    
    local_path --> create_network
    hf_download --> create_network
    create_network --> load_weights
    load_weights --> set_eval
    
    default_filename --> hf_download
    cache_dir_param --> hf_download
    local_files_param --> hf_download
```

**Sources**: [src/controlnet_aux/hed/__init__.py:63-76]()

### Parameter Configuration

The HED detector accepts the following configuration parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `detect_resolution` | int | 512 | Processing resolution for edge detection |
| `image_resolution` | int | 512 | Final output image resolution |
| `safe` | bool | False | Apply safe step processing to reduce noise |
| `scribble` | bool | False | Enable scribble mode with NMS processing |
| `output_type` | str | "pil" | Output format: "pil" or "np" |

**Sources**: [src/controlnet_aux/hed/__init__.py:82]()

## Key Implementation Details

### RGB vs BGR Handling

The HED implementation uses RGB input format, differing from official BGR implementations. This design choice improves compatibility with Gradio's RGB protocol and ControlNet applications.

### Multi-Scale Edge Fusion

The detector combines five different scale edge projections using sigmoid activation and averaging:
- `edge = 1 / (1 + np.exp(-np.mean(edges, axis=2).astype(np.float64)))`

This approach produces smoother, more coherent edge maps compared to single-scale detection.

### Memory and Device Management

The detector automatically detects the device of the neural network parameters and ensures tensor operations occur on the same device, supporting both CPU and GPU inference.

**Sources**: [src/controlnet_aux/hed/__init__.py:91](), [src/controlnet_aux/hed/__init__.py:100-111]()

---

