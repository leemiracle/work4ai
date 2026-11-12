<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page TEED and Anyline Detectors · fetched 2026-10-26 -->

# TEED and Anyline Detectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/anyline/__init__.py](src/controlnet_aux/anyline/__init__.py)
- [src/controlnet_aux/lineart_standard/__init__.py](src/controlnet_aux/lineart_standard/__init__.py)
- [src/controlnet_aux/teed/Fsmish.py](src/controlnet_aux/teed/Fsmish.py)
- [src/controlnet_aux/teed/LICENSE.txt](src/controlnet_aux/teed/LICENSE.txt)
- [src/controlnet_aux/teed/Xsmish.py](src/controlnet_aux/teed/Xsmish.py)
- [src/controlnet_aux/teed/__init__.py](src/controlnet_aux/teed/__init__.py)
- [src/controlnet_aux/teed/ted.py](src/controlnet_aux/teed/ted.py)

</details>



This document covers the Tiny Efficient Edge Detection (TEED) and Anyline detection systems within controlnet_aux. These detectors provide edge detection and combined edge/line art generation capabilities for ControlNet preprocessing.

The TEED detector focuses on efficient neural edge detection, while the Anyline detector combines neural edge detection with classical line art techniques. For broader edge detection options, see [Edge Detection](#4.1). For line art generation, see [Line Art Generation](#4.4).

## Overview

The TEED and Anyline detectors represent hybrid approaches to edge and line detection, combining deep learning models with classical computer vision techniques. Both detectors utilize the same underlying `TED` neural network architecture but apply different post-processing strategies.

```mermaid
graph TB
    subgraph "Detection Systems"
        TEED["TEEDdetector<br/>Pure Edge Detection"]
        ANYLINE["AnylineDetector<br/>Combined Edge+Line"]
        STANDARD["LineartStandardDetector<br/>Classical Processing"]
    end
    
    subgraph "Core Architecture"
        TED_MODEL["TED Neural Network<br/>ted.py"]
        SMISH["Smish Activation<br/>Fsmish.py, Xsmish.py"]
    end
    
    subgraph "Processing Pipeline"
        INPUT["Input Image"]
        RESIZE["Image Preprocessing<br/>HWC3, resize_image"]
        NEURAL["Neural Processing<br/>torch inference"]
        POSTPROC["Post-processing"]
        OUTPUT["Edge Map Output"]
    end
    
    subgraph "Post-processing Methods"
        SAFE_STEP["safe_step()<br/>Edge smoothing"]
        GAUSSIAN["cv2.GaussianBlur<br/>Classical filtering"] 
        MORPHOLOGY["morphology.remove_small_objects<br/>Noise removal"]
        COMBINE["combine_layers()<br/>Layer blending"]
    end
    
    TEED --> TED_MODEL
    ANYLINE --> TED_MODEL
    TED_MODEL --> SMISH
    
    INPUT --> RESIZE
    RESIZE --> NEURAL
    NEURAL --> POSTPROC
    POSTPROC --> OUTPUT
    
    TEED --> SAFE_STEP
    ANYLINE --> GAUSSIAN
    ANYLINE --> MORPHOLOGY
    ANYLINE --> COMBINE
    STANDARD --> GAUSSIAN
```

Sources: [src/controlnet_aux/teed/__init__.py:1-85](), [src/controlnet_aux/anyline/__init__.py:1-119](), [src/controlnet_aux/teed/ted.py:1-333]()

## TEED Detector Architecture

The `TEEDdetector` class provides a streamlined interface to the Tiny Efficient Edge Detector neural network. The detector loads pretrained models and performs inference with configurable safety post-processing.

### Core Components

| Component | File Location | Purpose |
|-----------|---------------|---------|
| `TEEDdetector` | [src/controlnet_aux/teed/__init__.py:14-84]() | Main detector interface |
| `TED` | [src/controlnet_aux/teed/ted.py:215-312]() | Neural network architecture |
| `Smish` | [src/controlnet_aux/teed/Xsmish.py:16-42]() | Custom activation function |
| `smish` | [src/controlnet_aux/teed/Fsmish.py:12-19]() | JIT-compiled activation |

### Neural Network Architecture

The `TED` model implements a compact edge detection architecture with the following structure:

```mermaid
graph TD
    subgraph "TED Architecture"
        INPUT_LAYER["Input<br/>3 channels"]
        
        subgraph "Encoder Blocks"
            BLOCK1["DoubleConvBlock<br/>3→16, stride=2"]
            BLOCK2["DoubleConvBlock<br/>16→32"]
            DBLOCK3["_DenseBlock<br/>32→48, 1 layer"]
        end
        
        subgraph "Skip Connections"
            SIDE1["SingleConvBlock<br/>16→32, stride=2"]
            PRE_DENSE["SingleConvBlock<br/>32→48"]
        end
        
        subgraph "Decoder Blocks"
            UP1["UpConvBlock<br/>16→1, scale=1"]
            UP2["UpConvBlock<br/>32→1, scale=1"]
            UP3["UpConvBlock<br/>48→1, scale=2"]
        end
        
        subgraph "Fusion"
            FUSION["DoubleFusion<br/>3→1 channels"]
        end
        
        MULTI_OUT["Multi-scale Outputs<br/>[out_1, out_2, out_3, fused]"]
    end
    
    INPUT_LAYER --> BLOCK1
    BLOCK1 --> BLOCK2
    BLOCK1 --> SIDE1
    BLOCK2 --> DBLOCK3
    BLOCK2 --> PRE_DENSE
    
    BLOCK1 --> UP1
    BLOCK2 --> UP2
    DBLOCK3 --> UP3
    
    UP1 --> FUSION
    UP2 --> FUSION
    UP3 --> FUSION
    
    FUSION --> MULTI_OUT
```

Sources: [src/controlnet_aux/teed/ted.py:215-312](), [src/controlnet_aux/teed/ted.py:280-311]()

### Processing Pipeline

The TEED detector follows this processing sequence:

1. **Preprocessing**: [src/controlnet_aux/teed/__init__.py:50-54]()
   - Convert input to numpy array
   - Apply `HWC3` normalization
   - Resize to detection resolution

2. **Neural Inference**: [src/controlnet_aux/teed/__init__.py:57-67]()
   - Convert to torch tensor
   - Forward pass through `TED` model
   - Multi-scale edge prediction

3. **Post-processing**: [src/controlnet_aux/teed/__init__.py:67-71]()
   - Sigmoid activation: `1 / (1 + np.exp(-np.mean(edges, axis=2)))`
   - Optional `safe_step` smoothing
   - Resize to original dimensions

Sources: [src/controlnet_aux/teed/__init__.py:36-84]()

## Anyline Detector Architecture

The `AnylineDetector` extends the TEED approach by combining neural edge detection with classical line art processing. This hybrid approach produces more comprehensive line detection suitable for artistic applications.

### Dual Processing Pipeline

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT["Input Image"]
        PREPROCESS["HWC3 + resize_image<br/>detect_resolution=1280"]
    end
    
    subgraph "Neural Edge Detection"
        TED_INFERENCE["TED Model Inference<br/>Same as TEED"]
        TED_EDGES["Neural Edge Map<br/>mteed_result"]
    end
    
    subgraph "Classical Line Art"
        GAUSSIAN_BLUR["cv2.GaussianBlur<br/>guassian_sigma=2.0"]
        INTENSITY_CALC["Intensity Calculation<br/>np.min(g - x, axis=2)"]
        THRESHOLD["Intensity Thresholding<br/>intensity_threshold=3"]
        LINEART_MAP["Classical Line Map<br/>lineart_result"]
    end
    
    subgraph "Combination Processing"
        INTENSITY_MASK["get_intensity_mask()<br/>Bound filtering"]
        MORPHOLOGY_CLEAN["morphology.remove_small_objects<br/>min_size=36"]
        LAYER_COMBINE["combine_layers()<br/>Blend neural + classical"]
    end
    
    FINAL_OUTPUT["Combined Edge+Line Map"]
    
    INPUT --> PREPROCESS
    PREPROCESS --> TED_INFERENCE
    PREPROCESS --> GAUSSIAN_BLUR
    
    TED_INFERENCE --> TED_EDGES
    GAUSSIAN_BLUR --> INTENSITY_CALC
    INTENSITY_CALC --> THRESHOLD
    THRESHOLD --> LINEART_MAP
    
    LINEART_MAP --> INTENSITY_MASK
    INTENSITY_MASK --> MORPHOLOGY_CLEAN
    MORPHOLOGY_CLEAN --> LAYER_COMBINE
    TED_EDGES --> LAYER_COMBINE
    
    LAYER_COMBINE --> FINAL_OUTPUT
```

Sources: [src/controlnet_aux/anyline/__init__.py:38-106]()

### Key Processing Methods

The Anyline detector implements several specialized processing methods:

**Intensity Mask Generation**: [src/controlnet_aux/anyline/__init__.py:108-112]()
```python
def get_intensity_mask(self, image_array, lower_bound, upper_bound):
    mask = image_array[:, :, 0]
    mask = np.where((mask >= lower_bound) & (mask <= upper_bound), mask, 0)
    mask = np.expand_dims(mask, 2).repeat(3, axis=2)
    return mask
```

**Layer Combination**: [src/controlnet_aux/anyline/__init__.py:114-118]()
```python
def combine_layers(self, base_layer, top_layer):
    mask = top_layer.astype(bool)
    temp = 1 - (1 - top_layer) * (1 - base_layer)
    result = base_layer * (~mask) + temp * mask
    return result
```

Sources: [src/controlnet_aux/anyline/__init__.py:108-118]()

## Activation Function System

Both detectors utilize the custom Smish activation function, which combines properties of sigmoid and tanh functions for improved edge detection performance.

### Smish Implementation

```mermaid
graph LR
    subgraph "Smish Activation"
        INPUT_X["Input x"]
        SIGMOID["torch.sigmoid(input)"]
        LOG1P["torch.log(1 + sigmoid_result)"]
        TANH["torch.tanh(log_result)"]
        MULTIPLY["input * tanh_result"]
        OUTPUT_Y["Output y"]
    end
    
    INPUT_X --> SIGMOID
    SIGMOID --> LOG1P
    LOG1P --> TANH
    INPUT_X --> MULTIPLY
    TANH --> MULTIPLY
    MULTIPLY --> OUTPUT_Y
```

The mathematical formula implemented is: `smish(x) = x * tanh(ln(1 + sigmoid(x)))`

Sources: [src/controlnet_aux/teed/Fsmish.py:12-19](), [src/controlnet_aux/teed/Xsmish.py:16-42]()

## Usage Patterns

### TEED Detector Usage

```python
# Via Processor interface
processor = Processor('teed')
result = processor(image, detect_resolution=512, safe_steps=2)

# Direct instantiation
detector = TEEDdetector.from_pretrained('lllyasviel/Annotators')
result = detector(image, detect_resolution=512, safe_steps=2)
```

### Anyline Detector Usage

```python
# Via Processor interface  
processor = Processor('anyline')
result = processor(image, detect_resolution=1280, guassian_sigma=2.0)

# Direct instantiation
detector = AnylineDetector.from_pretrained('TheMistoAI/MistoLine')
result = detector(image, detect_resolution=1280, guassian_sigma=2.0, intensity_threshold=3)
```

### Configuration Parameters

| Parameter | TEED Default | Anyline Default | Purpose |
|-----------|--------------|-----------------|---------|
| `detect_resolution` | 512 | 1280 | Processing resolution |
| `safe_steps` | 2 | N/A | Edge smoothing iterations |
| `guassian_sigma` | N/A | 2.0 | Gaussian blur strength |
| `intensity_threshold` | N/A | 3 | Line art threshold |

Sources: [src/controlnet_aux/teed/__init__.py:36-42](), [src/controlnet_aux/anyline/__init__.py:38-45]()

## Model Loading and Checkpoints

Both detectors support loading from Hugging Face Hub repositories using the `from_pretrained` class method pattern:

```mermaid
graph TD
    subgraph "Model Loading Process"
        PRETRAINED_CALL["from_pretrained(repo, filename, subfolder)"]
        PATH_CHECK["os.path.isdir() check"]
        LOCAL_PATH["Local file path"]
        HF_DOWNLOAD["hf_hub_download()"]
        
        subgraph "Model Instantiation"
            TED_INIT["TED() initialization"]
            STATE_LOAD["torch.load(model_path)"]
            STATE_DICT["model.load_state_dict()"]
        end
        
        DETECTOR_INIT["TEEDdetector(model) or<br/>AnylineDetector(model)"]
    end
    
    PRETRAINED_CALL --> PATH_CHECK
    PATH_CHECK --> LOCAL_PATH
    PATH_CHECK --> HF_DOWNLOAD
    
    LOCAL_PATH --> TED_INIT
    HF_DOWNLOAD --> TED_INIT
    TED_INIT --> STATE_LOAD
    STATE_LOAD --> STATE_DICT
    STATE_DICT --> DETECTOR_INIT
```

Sources: [src/controlnet_aux/teed/__init__.py:18-30](), [src/controlnet_aux/anyline/__init__.py:20-32]()

---

