<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page PiDiNet Detector · fetched 2026-10-26 -->

# PiDiNet Detector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/leres/leres/net_tools.py](src/controlnet_aux/leres/leres/net_tools.py)
- [src/controlnet_aux/leres/pix2pix/models/__init__.py](src/controlnet_aux/leres/pix2pix/models/__init__.py)
- [src/controlnet_aux/normalbae/__init__.py](src/controlnet_aux/normalbae/__init__.py)
- [src/controlnet_aux/pidi/__init__.py](src/controlnet_aux/pidi/__init__.py)
- [src/controlnet_aux/pidi/model.py](src/controlnet_aux/pidi/model.py)

</details>



The PiDiNet Detector implements Pixel Difference Network (PiDiNet) for edge detection in images. This detector specializes in generating clean edge maps with configurable safety filtering and scribble mode processing. 

For general edge detection overview, see [Edge Detection](#4.1). For classical edge detection, see [Canny Detector](#4.1.2). For multi-scale edge detection, see [HED Detector](#4.1.1).

## System Architecture

The PiDiNet detector consists of two main components: the detector interface and the underlying neural network model.

```mermaid
graph TB
    subgraph "Public Interface"
        DETECTOR["PidiNetDetector"]
        FROM_PRETRAINED["from_pretrained()"]
        CALL["__call__()"]
        TO_DEVICE["to()"]
    end
    
    subgraph "Model Loading"
        HF_DOWNLOAD["hf_hub_download()"]
        PIDINET_FUNC["pidinet()"]
        LOAD_STATE["load_state_dict()"]
    end
    
    subgraph "Neural Network"
        PIDINET_MODEL["PiDiNet"]
        PDC_BLOCKS["PDCBlock layers"]
        CONV_REDUCES["MapReduce modules"]
        CLASSIFIER["classifier"]
    end
    
    subgraph "Specialized Components"
        CSAM["CSAM<br/>Spatial Attention"]
        CDCM["CDCM<br/>Dilation Convolution"]
        PDC_CONV["Conv2d<br/>Pixel Difference Conv"]
    end
    
    subgraph "Utility Functions"
        HWC3["HWC3()"]
        RESIZE["resize_image()"]
        SAFE_STEP["safe_step()"]
        NMS["nms()"]
    end
    
    DETECTOR --> FROM_PRETRAINED
    FROM_PRETRAINED --> HF_DOWNLOAD
    FROM_PRETRAINED --> PIDINET_FUNC
    FROM_PRETRAINED --> LOAD_STATE
    
    PIDINET_FUNC --> PIDINET_MODEL
    DETECTOR --> CALL
    CALL --> HWC3
    CALL --> RESIZE
    CALL --> SAFE_STEP
    CALL --> NMS
    
    PIDINET_MODEL --> PDC_BLOCKS
    PIDINET_MODEL --> CONV_REDUCES
    PIDINET_MODEL --> CLASSIFIER
    
    PDC_BLOCKS --> PDC_CONV
    PIDINET_MODEL --> CSAM
    PIDINET_MODEL --> CDCM
    
    style DETECTOR fill:#f9f9f9,stroke:#333,stroke-width:2px
    style PIDINET_MODEL fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Architecture Overview**: The `PidiNetDetector` serves as a wrapper around the `PiDiNet` neural network model, providing model loading through Hugging Face Hub and post-processing utilities for edge map generation.

Sources: [src/controlnet_aux/pidi/__init__.py:15-84](), [src/controlnet_aux/pidi/model.py:493-644]()

## Class Structure and Interface

The detector follows the standard controlnet_aux pattern with class-based instantiation and callable interface.

| Component | Type | Purpose | Key Methods |
|-----------|------|---------|-------------|
| `PidiNetDetector` | Main Class | Edge detection interface | `from_pretrained()`, `__call__()`, `to()` |
| `PiDiNet` | Neural Network | Core edge detection model | `forward()`, `get_weights()` |
| `Conv2d` | Convolution Layer | Pixel difference convolutions | `forward()` with PDC operations |
| `PDCBlock` | Building Block | Residual blocks with PDC | Depthwise separable convolution |
| `CSAM` | Attention Module | Spatial attention mechanism | Compact attention weighting |
| `CDCM` | Dilation Module | Multi-scale feature extraction | Multiple dilation rates |

```mermaid
graph LR
    subgraph "Detector Interface"
        INIT["__init__(netNetwork)"]
        FROM_PRETRAINED["from_pretrained(pretrained_model_or_path)"]
        CALL_METHOD["__call__(input_image, **kwargs)"]
        TO_METHOD["to(device)"]
    end
    
    subgraph "Model Parameters"
        DETECT_RES["detect_resolution=512"]
        IMAGE_RES["image_resolution=512"]
        SAFE["safe=False"]
        SCRIBBLE["scribble=False"]
        APPLY_FILTER["apply_filter=False"]
        OUTPUT_TYPE["output_type='pil'"]
    end
    
    subgraph "Processing Pipeline"
        INPUT_PROC["Image preprocessing<br/>HWC3, resize_image"]
        TENSOR_CONV["Tensor conversion<br/>torch.from_numpy"]
        NETWORK_FORWARD["Network forward pass<br/>netNetwork(image_pidi)"]
        POST_PROC["Post-processing<br/>safe_step, filter, scribble"]
    end
    
    CALL_METHOD --> INPUT_PROC
    INPUT_PROC --> TENSOR_CONV
    TENSOR_CONV --> NETWORK_FORWARD
    NETWORK_FORWARD --> POST_PROC
    
    DETECT_RES --> INPUT_PROC
    IMAGE_RES --> POST_PROC
    SAFE --> POST_PROC
    SCRIBBLE --> POST_PROC
    APPLY_FILTER --> POST_PROC
    OUTPUT_TYPE --> POST_PROC
```

**Class Design**: The `PidiNetDetector` implements a consistent interface pattern where `from_pretrained()` handles model loading and `__call__()` performs inference with extensive parameter control.

Sources: [src/controlnet_aux/pidi/__init__.py:15-37](), [src/controlnet_aux/pidi/__init__.py:38-84]()

## Neural Network Architecture

The PiDiNet model implements a specialized architecture for edge detection using Pixel Difference Convolutions (PDC).

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT["Input Image<br/>3 channels"]
        INIT_BLOCK["init_block<br/>Conv2d with PDC"]
    end
    
    subgraph "Feature Extraction Blocks"
        BLOCK1["Block 1<br/>3 PDCBlock layers<br/>C channels"]
        BLOCK2["Block 2<br/>4 PDCBlock layers<br/>2C channels"]
        BLOCK3["Block 3<br/>4 PDCBlock layers<br/>4C channels"]
        BLOCK4["Block 4<br/>4 PDCBlock layers<br/>4C channels"]
    end
    
    subgraph "Feature Enhancement"
        DILATIONS["dilations<br/>CDCM modules"]
        ATTENTIONS["attentions<br/>CSAM modules"]
    end
    
    subgraph "Edge Map Generation"
        REDUCES["conv_reduces<br/>MapReduce modules"]
        INTERPOLATE["Bilinear interpolation<br/>to input size"]
        CLASSIFIER["classifier<br/>4→1 channels"]
        SIGMOID["torch.sigmoid()"]
    end
    
    INPUT --> INIT_BLOCK
    INIT_BLOCK --> BLOCK1
    BLOCK1 --> BLOCK2
    BLOCK2 --> BLOCK3
    BLOCK3 --> BLOCK4
    
    BLOCK1 --> DILATIONS
    BLOCK2 --> DILATIONS  
    BLOCK3 --> DILATIONS
    BLOCK4 --> DILATIONS
    
    DILATIONS --> ATTENTIONS
    ATTENTIONS --> REDUCES
    REDUCES --> INTERPOLATE
    INTERPOLATE --> CLASSIFIER
    CLASSIFIER --> SIGMOID
```

**Architecture Details**: The model uses a 4-block hierarchical structure with progressive channel doubling, enhanced by dilation convolution (`CDCM`) and spatial attention (`CSAM`) modules for multi-scale feature extraction.

### Pixel Difference Convolutions

The core innovation of PiDiNet lies in its specialized convolution operations defined in the `nets` configuration:

| PDC Type | Code | Operation | Kernel Size |
|----------|------|-----------|-------------|
| Standard | `cv` | `F.conv2d` | 3x3 |
| Center Difference | `cd` | `conv - center_sum` | 3x3 |
| Angular Difference | `ad` | `conv - rotated_weights` | 3x3 |
| Radial Difference | `rd` | `conv with 5x5 buffer` | 5x5 effective |

```mermaid
graph LR
    subgraph "PDC Operations"
        CREATE_CONV["createConvFunc(op_type)"]
        CV["cv: F.conv2d"]
        CD["cd: conv - center_sum"]
        AD["ad: conv - rotated_conv"]
        RD["rd: conv with 5x5 buffer"]
    end
    
    subgraph "Network Configuration"
        NETS["nets['carv4']"]
        LAYER_MAPPING["layer0: 'cd'<br/>layer1: 'ad'<br/>layer2: 'rd'<br/>layer3: 'cv'<br/>..."]
    end
    
    subgraph "Model Instantiation"
        CONFIG_MODEL["config_model('carv4')"]
        PIDINET_FUNC["pidinet()"]
        PDCS_LIST["pdcs = [func0, func1, ...]"]
    end
    
    CREATE_CONV --> CV
    CREATE_CONV --> CD
    CREATE_CONV --> AD
    CREATE_CONV --> RD
    
    NETS --> LAYER_MAPPING
    LAYER_MAPPING --> CONFIG_MODEL
    CONFIG_MODEL --> PDCS_LIST
    PDCS_LIST --> PIDINET_FUNC
```

**PDC Implementation**: Each layer type implements different pixel difference operations, with the `carv4` configuration providing a balanced mix of all four types across 16 layers.

Sources: [src/controlnet_aux/pidi/model.py:298-344](), [src/controlnet_aux/pidi/model.py:43-296](), [src/controlnet_aux/pidi/model.py:661-664]()

## Processing Pipeline and Parameters

The detector provides comprehensive control over edge detection behavior through multiple processing stages.

```mermaid
graph TB
    subgraph "Input Preprocessing"
        INPUT_IMG["input_image"]
        HWC3_NORM["HWC3(input_image)"]
        RESIZE_DETECT["resize_image(detect_resolution)"]
        BGR_TO_RGB["image[:, :, ::-1]"]
        NORMALIZE["/ 255.0"]
        REARRANGE["rearrange('h w c -> 1 c h w')"]
    end
    
    subgraph "Network Inference"
        FORWARD["netNetwork(image_pidi)"]
        GET_EDGE["edge = output[-1]"]
        CPU_NUMPY["edge.cpu().numpy()"]
    end
    
    subgraph "Post-processing Options"
        APPLY_FILTER_CHECK{{"apply_filter?"}}
        FILTER_OP["edge > 0.5"]
        SAFE_CHECK{{"safe?"}}
        SAFE_STEP_OP["safe_step(edge)"]
        CLIP_SCALE["(edge * 255.0).clip(0, 255)"]
    end
    
    subgraph "Output Formatting"
        RESIZE_OUTPUT["resize to image_resolution"]
        SCRIBBLE_CHECK{{"scribble?"}}
        NMS_OP["nms(detected_map, 127, 3.0)"]
        GAUSSIAN_BLUR["GaussianBlur(0, 0, 3.0)"]
        THRESHOLD["threshold 4/255"]
        OUTPUT_TYPE_CHECK{{"output_type == 'pil'?"}}
        PIL_CONVERT["Image.fromarray()"]
    end
    
    INPUT_IMG --> HWC3_NORM
    HWC3_NORM --> RESIZE_DETECT
    RESIZE_DETECT --> BGR_TO_RGB
    BGR_TO_RGB --> NORMALIZE
    NORMALIZE --> REARRANGE
    REARRANGE --> FORWARD
    FORWARD --> GET_EDGE
    GET_EDGE --> CPU_NUMPY
    
    CPU_NUMPY --> APPLY_FILTER_CHECK
    APPLY_FILTER_CHECK -->|Yes| FILTER_OP
    APPLY_FILTER_CHECK -->|No| SAFE_CHECK
    FILTER_OP --> SAFE_CHECK
    SAFE_CHECK -->|Yes| SAFE_STEP_OP
    SAFE_CHECK -->|No| CLIP_SCALE
    SAFE_STEP_OP --> CLIP_SCALE
    
    CLIP_SCALE --> RESIZE_OUTPUT
    RESIZE_OUTPUT --> SCRIBBLE_CHECK
    SCRIBBLE_CHECK -->|Yes| NMS_OP
    SCRIBBLE_CHECK -->|No| OUTPUT_TYPE_CHECK
    NMS_OP --> GAUSSIAN_BLUR
    GAUSSIAN_BLUR --> THRESHOLD
    THRESHOLD --> OUTPUT_TYPE_CHECK
    OUTPUT_TYPE_CHECK -->|Yes| PIL_CONVERT
```

**Parameter Control**: The processing pipeline offers fine-grained control through `apply_filter` for binary thresholding, `safe` for gradient-aware processing, and `scribble` for artistic line extraction.

### Key Processing Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `detect_resolution` | int | 512 | Input resolution for edge detection |
| `image_resolution` | int | 512 | Output resolution for final image |
| `safe` | bool | False | Apply safe_step gradient processing |
| `apply_filter` | bool | False | Apply 0.5 threshold to edge values |
| `scribble` | bool | False | Generate scribble-style line art |
| `output_type` | str | "pil" | Output format ("pil" or "np") |

**Scribble Mode Processing**: When `scribble=True`, the detector applies Non-Maximum Suppression (`nms`) followed by Gaussian blur and binary thresholding to create clean line art suitable for artistic applications.

Sources: [src/controlnet_aux/pidi/__init__.py:38-84](), [src/controlnet_aux/util.py]() (referenced functions)

## Model Loading and Configuration

The detector supports flexible model loading from Hugging Face Hub with automatic checkpoint handling.

```mermaid
graph TB
    subgraph "Model Loading Process"
        FROM_PRETRAINED["from_pretrained(pretrained_model_or_path)"]
        PATH_CHECK{{"os.path.isdir()?"}}
        LOCAL_PATH["os.path.join(path, filename)"]
        HF_DOWNLOAD["hf_hub_download()"]
    end
    
    subgraph "Model Instantiation"
        PIDINET_CALL["pidinet()"]
        DEFAULT_CONFIG["config: 'carv4'<br/>dil: 24<br/>sa: True"]
        PIDINET_MODEL["PiDiNet(60, pdcs, dil=24, sa=True)"]
    end
    
    subgraph "Checkpoint Loading"
        TORCH_LOAD["torch.load(model_path)"]
        STATE_DICT["checkpoint['state_dict']"]
        MODULE_STRIP["{k.replace('module.', ''): v}"]
        LOAD_STATE_DICT["netNetwork.load_state_dict()"]
        SET_EVAL["netNetwork.eval()"]
    end
    
    FROM_PRETRAINED --> PATH_CHECK
    PATH_CHECK -->|Yes| LOCAL_PATH
    PATH_CHECK -->|No| HF_DOWNLOAD
    LOCAL_PATH --> TORCH_LOAD
    HF_DOWNLOAD --> TORCH_LOAD
    
    FROM_PRETRAINED --> PIDINET_CALL
    PIDINET_CALL --> DEFAULT_CONFIG
    DEFAULT_CONFIG --> PIDINET_MODEL
    
    TORCH_LOAD --> STATE_DICT
    STATE_DICT --> MODULE_STRIP
    MODULE_STRIP --> LOAD_STATE_DICT
    LOAD_STATE_DICT --> SET_EVAL
```

**Default Configuration**: The detector uses the `carv4` architecture with 60 input channels, dilation factor of 24, and spatial attention enabled, representing the optimal configuration from the original PiDiNet paper.

**Checkpoint Compatibility**: The loading process automatically strips `module.` prefixes from state dict keys to handle both DataParallel and standard model checkpoints seamlessly.

Sources: [src/controlnet_aux/pidi/__init__.py:19-32](), [src/controlnet_aux/pidi/model.py:661-664](), [src/controlnet_aux/pidi/model.py:646-659]()

---

