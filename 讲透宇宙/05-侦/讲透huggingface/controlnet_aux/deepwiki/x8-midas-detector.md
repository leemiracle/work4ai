<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page MiDaS Detector · fetched 2026-10-26 -->

# MiDaS Detector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/midas/__init__.py](src/controlnet_aux/midas/__init__.py)
- [src/controlnet_aux/midas/api.py](src/controlnet_aux/midas/api.py)
- [src/controlnet_aux/midas/midas/__init__.py](src/controlnet_aux/midas/midas/__init__.py)
- [src/controlnet_aux/midas/midas/base_model.py](src/controlnet_aux/midas/midas/base_model.py)
- [src/controlnet_aux/midas/midas/blocks.py](src/controlnet_aux/midas/midas/blocks.py)
- [src/controlnet_aux/midas/midas/dpt_depth.py](src/controlnet_aux/midas/midas/dpt_depth.py)
- [src/controlnet_aux/midas/midas/midas_net.py](src/controlnet_aux/midas/midas/midas_net.py)
- [src/controlnet_aux/midas/midas/midas_net_custom.py](src/controlnet_aux/midas/midas/midas_net_custom.py)
- [src/controlnet_aux/midas/midas/transforms.py](src/controlnet_aux/midas/midas/transforms.py)

</details>



The MiDaS Detector provides monocular depth estimation capabilities using the MiDaS (Monocular Depth Estimation) model family. It supports multiple neural network architectures including Dense Prediction Transformers (DPT) and traditional convolutional networks, with optional normal map generation from estimated depth maps.

For pose-based depth estimation, see [DWpose Detector](#4.3.1). For alternative depth estimation methods, see [ZoeDepth Detector](#4.2.2) and [LeRes and Normal Map Detectors](#4.2.3).

## Architecture Overview

The MiDaS detector implements a multi-layered architecture with pluggable model backends and preprocessing pipelines.

**MiDaS Detector Class Structure**
```mermaid
graph TB
    subgraph "Public Interface"
        MidasDetector["`MidasDetector`<br/>Main detector class"]
        from_pretrained["`from_pretrained()`<br/>Class method loader"]
        __call__["`__call__()`<br/>Inference method"]
    end
    
    subgraph "Model Inference Layer"
        MiDaSInference["`MiDaSInference`<br/>nn.Module wrapper"]
        load_model["`load_model()`<br/>Model factory"]
        load_midas_transform["`load_midas_transform()`<br/>Transform factory"]
    end
    
    subgraph "Model Backends"
        DPTDepthModel["`DPTDepthModel`<br/>Dense Prediction Transformer"]
        MidasNet["`MidasNet`<br/>Original MiDaS architecture"]
        MidasNet_small["`MidasNet_small`<br/>Lightweight variant"]
    end
    
    subgraph "Neural Architecture Components"
        _make_encoder["`_make_encoder()`<br/>Backbone factory"]
        FeatureFusionBlock["`FeatureFusionBlock`<br/>Feature integration"]
        Interpolate["`Interpolate`<br/>Upsampling module"]
    end
    
    subgraph "Preprocessing Pipeline"
        Resize["`Resize`<br/>Image resizing"]
        NormalizeImage["`NormalizeImage`<br/>Normalization"]
        PrepareForNet["`PrepareForNet`<br/>Tensor preparation"]
    end
    
    MidasDetector --> from_pretrained
    from_pretrained --> MiDaSInference
    MidasDetector --> __call__
    __call__ --> MiDaSInference
    
    MiDaSInference --> load_model
    load_model --> DPTDepthModel
    load_model --> MidasNet
    load_model --> MidasNet_small
    
    load_model --> load_midas_transform
    load_midas_transform --> Resize
    load_midas_transform --> NormalizeImage
    load_midas_transform --> PrepareForNet
    
    DPTDepthModel --> _make_encoder
    MidasNet --> _make_encoder
    MidasNet_small --> _make_encoder
    
    _make_encoder --> FeatureFusionBlock
    DPTDepthModel --> Interpolate
    MidasNet --> Interpolate
```

Sources: [src/controlnet_aux/midas/__init__.py:14-96](), [src/controlnet_aux/midas/api.py:145-169](), [src/controlnet_aux/midas/midas/dpt_depth.py:88-109]()

## Model Variants and Backends

The MiDaS detector supports four distinct model architectures with different computational requirements and accuracy characteristics.

| Model Type | Architecture | Input Size | Backbone | Features |
|------------|--------------|------------|----------|----------|
| `dpt_large` | Dense Prediction Transformer | 384×384 | ViT-L/16 | 256 |
| `dpt_hybrid` | Dense Prediction Transformer | 384×384 | ViT-B + ResNet50 | 256 |
| `midas_v21` | Traditional MiDaS | 384×384 | ResNeXt-101 | 256 |
| `midas_v21_small` | Lightweight MiDaS | 256×256 | EfficientNet-Lite3 | 64 |

**Model Loading and Configuration Flow**
```mermaid
graph LR
    subgraph "Model Selection"
        model_type["`model_type`<br/>String parameter"]
        ISL_PATHS["`ISL_PATHS`<br/>Checkpoint paths"]
        remote_model_path["`remote_model_path`<br/>HF Hub URL"]
    end
    
    subgraph "Architecture Factory"
        load_model_func["`load_model()`<br/>Factory function"]
        DPTDepthModel_init["`DPTDepthModel()`<br/>path, backbone, non_negative"]
        MidasNet_init["`MidasNet()`<br/>path, features, non_negative"]
        MidasNet_small_init["`MidasNet_small()`<br/>path, features, backbone, blocks"]
    end
    
    subgraph "Backbone Selection"
        vitl16_384["`vitl16_384`<br/>Vision Transformer Large"]
        vitb_rn50_384["`vitb_rn50_384`<br/>ViT-B + ResNet50 hybrid"]
        resnext101_wsl["`resnext101_wsl`<br/>ResNeXt backbone"]
        efficientnet_lite3["`efficientnet_lite3`<br/>Lightweight backbone"]
    end
    
    model_type --> load_model_func
    load_model_func --> DPTDepthModel_init
    load_model_func --> MidasNet_init  
    load_model_func --> MidasNet_small_init
    
    DPTDepthModel_init --> vitl16_384
    DPTDepthModel_init --> vitb_rn50_384
    MidasNet_init --> resnext101_wsl
    MidasNet_small_init --> efficientnet_lite3
    
    ISL_PATHS --> load_model_func
    remote_model_path --> load_model_func
```

Sources: [src/controlnet_aux/midas/api.py:16-24](), [src/controlnet_aux/midas/api.py:77-143](), [src/controlnet_aux/midas/midas/dpt_depth.py:88-105](), [src/controlnet_aux/midas/midas/midas_net_custom.py:12-70]()

## Usage Patterns and Inference Pipeline

The MiDaS detector supports both depth-only estimation and combined depth + normal map generation through configurable parameters.

**Inference Call Flow**
```mermaid
graph TD
    subgraph "Input Processing"
        input_image["`input_image`<br/>PIL/numpy array"]
        HWC3["`HWC3()`<br/>Channel normalization"]
        resize_image["`resize_image()`<br/>Resolution scaling"]
    end
    
    subgraph "Model Inference"
        torch_preprocessing["`torch.from_numpy()`<br/>Tensor conversion"]
        rearrange["`rearrange()`<br/>BHWC → BCHW"]
        model_forward["`self.model()`<br/>Neural network inference"]
        depth_normalization["`depth_pt normalization`<br/>Min-max scaling"]
    end
    
    subgraph "Post-processing Options"
        depth_only["`depth_image`<br/>Grayscale depth map"]
        normal_computation["`normal computation`<br/>Sobel gradients + normalization"]
        cv2_Sobel["`cv2.Sobel()`<br/>x,y gradients"]
        normal_image["`normal_image`<br/>RGB normal map"]
    end
    
    subgraph "Output Formatting"
        resize_to_target["`cv2.resize()`<br/>Match input resolution"]
        output_type_check["`output_type`<br/>PIL vs numpy"]
        Image_fromarray["`Image.fromarray()`<br/>PIL conversion"]
    end
    
    input_image --> HWC3
    HWC3 --> resize_image
    resize_image --> torch_preprocessing
    torch_preprocessing --> rearrange
    rearrange --> model_forward
    model_forward --> depth_normalization
    
    depth_normalization --> depth_only
    depth_normalization --> normal_computation
    normal_computation --> cv2_Sobel
    cv2_Sobel --> normal_image
    
    depth_only --> resize_to_target
    normal_image --> resize_to_target
    resize_to_target --> output_type_check
    output_type_check --> Image_fromarray
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `detect_resolution` | int | 512 | Input processing resolution |
| `image_resolution` | int | 512 | Output image resolution |
| `depth_and_normal` | bool | False | Enable normal map generation |
| `a` | float | `np.pi * 2.0` | Normal map z-component scaling |
| `bg_th` | float | 0.1 | Background threshold for normal computation |

Sources: [src/controlnet_aux/midas/__init__.py:39-95](), [src/controlnet_aux/midas/__init__.py:65-74]()

## Neural Network Architecture Components

The MiDaS models utilize sophisticated encoder-decoder architectures with feature fusion mechanisms.

**Dense Prediction Transformer Architecture**
```mermaid
graph TB
    subgraph "Input Processing"
        input_tensor["`x`<br/>Input tensor BCHW"]
    end
    
    subgraph "Vision Transformer Encoder"
        forward_vit["`forward_vit()`<br/>Multi-scale feature extraction"]
        layer_1["`layer_1`<br/>Low-level features"]
        layer_2["`layer_2`<br/>Mid-level features"] 
        layer_3["`layer_3`<br/>High-level features"]
        layer_4["`layer_4`<br/>Semantic features"]
    end
    
    subgraph "Feature Projection"
        layer1_rn["`scratch.layer1_rn`<br/>Conv2d projection"]
        layer2_rn["`scratch.layer2_rn`<br/>Conv2d projection"]
        layer3_rn["`scratch.layer3_rn`<br/>Conv2d projection"]
        layer4_rn["`scratch.layer4_rn`<br/>Conv2d projection"]
    end
    
    subgraph "Decoder with Feature Fusion"
        refinenet4["`scratch.refinenet4`<br/>FeatureFusionBlock"]
        refinenet3["`scratch.refinenet3`<br/>FeatureFusionBlock + skip"]
        refinenet2["`scratch.refinenet2`<br/>FeatureFusionBlock + skip"]
        refinenet1["`scratch.refinenet1`<br/>FeatureFusionBlock + skip"]
    end
    
    subgraph "Output Head"
        output_conv["`scratch.output_conv`<br/>Conv2d + Interpolate + ReLU"]
        depth_output["`depth`<br/>Single channel depth map"]
    end
    
    input_tensor --> forward_vit
    forward_vit --> layer_1
    forward_vit --> layer_2
    forward_vit --> layer_3
    forward_vit --> layer_4
    
    layer_1 --> layer1_rn
    layer_2 --> layer2_rn
    layer_3 --> layer3_rn
    layer_4 --> layer4_rn
    
    layer4_rn --> refinenet4
    refinenet4 --> refinenet3
    layer3_rn --> refinenet3
    refinenet3 --> refinenet2
    layer2_rn --> refinenet2
    refinenet2 --> refinenet1
    layer1_rn --> refinenet1
    
    refinenet1 --> output_conv
    output_conv --> depth_output
```

### Feature Fusion Block Architecture

The `FeatureFusionBlock` implements hierarchical feature integration with residual connections:

- **Residual Convolution Units**: Apply `ResidualConvUnit` for feature refinement [src/controlnet_aux/midas/midas/blocks.py:194-227]()
- **Bilinear Upsampling**: 2× scale factor with `align_corners=True` [src/controlnet_aux/midas/midas/blocks.py:222-224]()
- **Skip Connections**: Additive fusion of multi-scale features [src/controlnet_aux/midas/midas/blocks.py:215-220]()

Sources: [src/controlnet_aux/midas/midas/dpt_depth.py:67-85](), [src/controlnet_aux/midas/midas/blocks.py:194-227](), [src/controlnet_aux/midas/midas/blocks.py:155-192]()

## Implementation Details

### Model Loading Strategy

The detector uses a two-stage loading process with fallback mechanisms:

1. **Local Path Check**: Verify checkpoint exists locally [src/controlnet_aux/midas/api.py:92-94]()
2. **Automatic Download**: Use `basicsr.utils.download_util.load_file_from_url` if missing [src/controlnet_aux/midas/api.py:93-94]()
3. **Hugging Face Integration**: Support for `hf_hub_download` in detector class [src/controlnet_aux/midas/__init__.py:25-28]()

### Normal Map Computation

When `depth_and_normal=True`, the detector computes surface normals using Sobel edge detection:

```python
x = cv2.Sobel(depth_np, cv2.CV_32F, 1, 0, ksize=3)  # x-gradient
y = cv2.Sobel(depth_np, cv2.CV_32F, 0, 1, ksize=3)  # y-gradient  
z = np.ones_like(x) * a                              # z-component
normal = np.stack([x, y, z], axis=2)                 # RGB normal map
```

Background regions below `bg_th` threshold are masked to zero gradients [src/controlnet_aux/midas/__init__.py:70-71]().

### Memory Management

The detector implements several memory optimization strategies:

- **Gradient-free Inference**: All model forward passes use `torch.no_grad()` context [src/controlnet_aux/midas/__init__.py:52](), [src/controlnet_aux/midas/api.py:166]()
- **Disabled Training**: Models use `disabled_train` to prevent accidental mode changes [src/controlnet_aux/midas/api.py:26-29](), [src/controlnet_aux/midas/api.py:163]()
- **Device Management**: Automatic device detection and tensor placement [src/controlnet_aux/midas/__init__.py:40](), [src/controlnet_aux/midas/__init__.py:54]()

Sources: [src/controlnet_aux/midas/__init__.py:65-74](), [src/controlnet_aux/midas/api.py:92-94](), [src/controlnet_aux/midas/api.py:26-29]()

---

