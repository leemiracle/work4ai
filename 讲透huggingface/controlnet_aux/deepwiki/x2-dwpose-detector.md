<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page DWpose Detector · fetched 2026-10-26 -->

# DWpose Detector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/dwpose/__init__.py](src/controlnet_aux/dwpose/__init__.py)
- [src/controlnet_aux/dwpose/dwpose_config/__init__.py](src/controlnet_aux/dwpose/dwpose_config/__init__.py)
- [src/controlnet_aux/dwpose/dwpose_config/dwpose-l_384x288.py](src/controlnet_aux/dwpose/dwpose_config/dwpose-l_384x288.py)
- [src/controlnet_aux/dwpose/util.py](src/controlnet_aux/dwpose/util.py)
- [src/controlnet_aux/dwpose/wholebody.py](src/controlnet_aux/dwpose/wholebody.py)
- [src/controlnet_aux/dwpose/yolox_config/__init__.py](src/controlnet_aux/dwpose/yolox_config/__init__.py)
- [src/controlnet_aux/dwpose/yolox_config/yolox_l_8xb8-300e_coco.py](src/controlnet_aux/dwpose/yolox_config/yolox_l_8xb8-300e_coco.py)
- [tests/test_controlnet_aux.py](tests/test_controlnet_aux.py)

</details>



The DWpose Detector provides wholebody pose estimation capabilities, detecting body, hand, and face keypoints from input images. This detector combines YOLOX person detection with DWpose wholebody pose estimation to produce comprehensive pose maps suitable for ControlNet conditioning.

For general pose estimation concepts, see [Pose Estimation](#4.3). For the alternative OpenPose implementation, see [OpenPose Detector](#4.3.2).

## System Architecture

The DWpose detector implements a two-stage pipeline: person detection followed by pose estimation. The system integrates MMDetection's YOLOX detector with MMPose's DWpose wholebody estimator to provide comprehensive pose detection including body, hands, and facial landmarks.

```mermaid
graph TD
    subgraph "DWposeDetector Interface"
        DWPOSE["DWposeDetector"]
        CALL["__call__()"]
        TO_DEVICE["to()"]
    end
    
    subgraph "Wholebody Pipeline"
        WB["Wholebody"]
        WB_CALL["__call__()"]
        DETECTOR["self.detector"]
        POSE_EST["self.pose_estimator"]
    end
    
    subgraph "MMDetection Components"
        YOLOX["YOLOX Detector"]
        INFERENCE_DET["inference_detector()"]
        BBOX["Bounding Boxes"]
        NMS["nms()"]
    end
    
    subgraph "MMPose Components"
        POSE_MODEL["DWpose Model"]
        INFERENCE_TOP["inference_topdown()"]
        MERGE["merge_data_samples()"]
        KEYPOINTS["Keypoints + Scores"]
    end
    
    subgraph "Post-processing"
        COORD_NORM["Coordinate Normalization"]
        BODY_SPLIT["Body/Hand/Face Split"]
        POSE_DICT["Pose Dictionary"]
        DRAW["draw_pose()"]
    end
    
    DWPOSE --> WB
    CALL --> WB_CALL
    TO_DEVICE --> WB
    
    WB_CALL --> INFERENCE_DET
    INFERENCE_DET --> YOLOX
    YOLOX --> BBOX
    BBOX --> NMS
    
    NMS --> INFERENCE_TOP
    INFERENCE_TOP --> POSE_MODEL
    POSE_MODEL --> MERGE
    MERGE --> KEYPOINTS
    
    KEYPOINTS --> COORD_NORM
    COORD_NORM --> BODY_SPLIT
    BODY_SPLIT --> POSE_DICT
    POSE_DICT --> DRAW
```

**Sources:** [src/controlnet_aux/dwpose/__init__.py:33-91](), [src/controlnet_aux/dwpose/wholebody.py:32-121]()

## Core Components

### DWposeDetector Class

The `DWposeDetector` class serves as the primary interface for wholebody pose estimation. It wraps the `Wholebody` pipeline and provides a consistent API for pose detection.

| Method | Purpose | Parameters |
|--------|---------|------------|
| `__init__()` | Initialize detector with model configs | `det_config`, `det_ckpt`, `pose_config`, `pose_ckpt`, `device` |
| `__call__()` | Process image and return pose visualization | `input_image`, `detect_resolution`, `image_resolution`, `output_type` |
| `to()` | Move models to specified device | `device` |

```mermaid
graph LR
    subgraph "Input Processing"
        INPUT["input_image"]
        RGB2BGR["cv2.cvtColor()"]
        HWC3["HWC3()"]
        RESIZE["resize_image()"]
    end
    
    subgraph "Pose Estimation"
        WHOLEBODY["pose_estimation()"]
        CANDIDATE["candidate"]
        SUBSET["subset"]
    end
    
    subgraph "Coordinate Processing"
        NORMALIZE["Normalize to [0,1]"]
        BODY_EXTRACT["body[:,:18]"]
        FOOT_EXTRACT["foot[18:24]"]
        FACE_EXTRACT["faces[24:92]"]
        HAND_EXTRACT["hands[92:113+113:]"]
    end
    
    subgraph "Output Generation"
        POSE_DICT["pose dict"]
        DRAW_POSE["draw_pose()"]
        OUTPUT_FMT["output_type conversion"]
    end
    
    INPUT --> RGB2BGR
    RGB2BGR --> HWC3
    HWC3 --> RESIZE
    RESIZE --> WHOLEBODY
    
    WHOLEBODY --> CANDIDATE
    WHOLEBODY --> SUBSET
    
    CANDIDATE --> NORMALIZE
    NORMALIZE --> BODY_EXTRACT
    NORMALIZE --> FOOT_EXTRACT
    NORMALIZE --> FACE_EXTRACT
    NORMALIZE --> HAND_EXTRACT
    
    BODY_EXTRACT --> POSE_DICT
    FOOT_EXTRACT --> POSE_DICT
    FACE_EXTRACT --> POSE_DICT
    HAND_EXTRACT --> POSE_DICT
    
    POSE_DICT --> DRAW_POSE
    DRAW_POSE --> OUTPUT_FMT
```

**Sources:** [src/controlnet_aux/dwpose/__init__.py:43-91]()

### Wholebody Pipeline

The `Wholebody` class implements the core pose estimation pipeline using MMDetection and MMPose frameworks. It handles model initialization, person detection, and pose keypoint estimation.

#### Model Configuration

| Component | Default Config | Default Checkpoint |
|-----------|----------------|-------------------|
| Detection | `yolox_l_8xb8-300e_coco.py` | YOLOX-L COCO checkpoint |
| Pose | `dwpose-l_384x288.py` | DW-LL UBody checkpoint |

#### Processing Pipeline

1. **Person Detection**: Uses YOLOX to detect person bounding boxes
2. **NMS Filtering**: Applies Non-Maximum Suppression with IoU threshold 0.7
3. **Pose Estimation**: Runs DWpose on detected persons or full image if no detections
4. **Keypoint Processing**: Extracts and processes wholebody keypoints
5. **Coordinate Mapping**: Converts from MMPose to OpenPose keypoint ordering

**Sources:** [src/controlnet_aux/dwpose/wholebody.py:33-121]()

## Keypoint Structure

The DWpose detector outputs 133 keypoints organized into distinct body regions:

```mermaid
graph TD
    subgraph "Keypoint Organization"
        TOTAL["133 Total Keypoints"]
        
        subgraph "Body Region"
            BODY["Body: 0-17"]
            BODY_DESC["17 body joints + computed neck"]
        end
        
        subgraph "Foot Region"
            FOOT["Foot: 18-23"]
            FOOT_DESC["6 foot keypoints"]
        end
        
        subgraph "Face Region"
            FACE["Face: 24-91"]
            FACE_DESC["68 facial landmarks"]
        end
        
        subgraph "Hand Region"
            HANDS["Hands: 92-132"]
            LEFT_HAND["Left Hand: 92-112"]
            RIGHT_HAND["Right Hand: 113-132"]
        end
        
        TOTAL --> BODY
        TOTAL --> FOOT
        TOTAL --> FACE
        TOTAL --> HANDS
        
        BODY --> BODY_DESC
        FOOT --> FOOT_DESC
        FACE --> FACE_DESC
        HANDS --> LEFT_HAND
        HANDS --> RIGHT_HAND
    end
    
    subgraph "Processing Steps"
        MMPOSE["MMPose Format"]
        NECK_COMP["Neck Computation"]
        REORDER["OpenPose Reordering"]
        SPLIT["Region Splitting"]
        
        MMPOSE --> NECK_COMP
        NECK_COMP --> REORDER
        REORDER --> SPLIT
    end
```

**Sources:** [src/controlnet_aux/dwpose/__init__.py:56-78](), [src/controlnet_aux/dwpose/wholebody.py:100-116]()

## Pose Visualization

The detector includes comprehensive visualization capabilities through drawing utilities that render different pose components with distinct visual styles.

### Drawing Functions

| Function | Purpose | Visual Style |
|----------|---------|--------------|
| `draw_bodypose()` | Render body skeleton | Colored limbs with joint circles |
| `draw_handpose()` | Render hand keypoints | HSV-colored connections |
| `draw_facepose()` | Render facial landmarks | White circles |

```mermaid
graph LR
    subgraph "Pose Data Structure"
        POSE_DICT["pose dict"]
        BODIES["bodies"]
        HANDS["hands"]
        FACES["faces"]
        
        BODIES_SUB["candidate + subset"]
        HANDS_SUB["hand keypoints"]
        FACES_SUB["face landmarks"]
    end
    
    subgraph "Drawing Pipeline"
        CANVAS["np.zeros canvas"]
        DRAW_BODY["draw_bodypose()"]
        DRAW_HAND["draw_handpose()"]
        DRAW_FACE["draw_facepose()"]
    end
    
    subgraph "Visual Elements"
        LIMBS["Colored limb segments"]
        JOINTS["Joint circles"]
        HAND_LINES["Hand connection lines"]
        FACE_DOTS["Facial landmark dots"]
    end
    
    POSE_DICT --> BODIES
    POSE_DICT --> HANDS
    POSE_DICT --> FACES
    
    BODIES --> BODIES_SUB
    HANDS --> HANDS_SUB
    FACES --> FACES_SUB
    
    BODIES_SUB --> DRAW_BODY
    HANDS_SUB --> DRAW_HAND
    FACES_SUB --> DRAW_FACE
    
    DRAW_BODY --> LIMBS
    DRAW_BODY --> JOINTS
    DRAW_HAND --> HAND_LINES
    DRAW_FACE --> FACE_DOTS
```

**Sources:** [src/controlnet_aux/dwpose/__init__.py:19-31](), [src/controlnet_aux/dwpose/util.py:67-156]()

## Usage Patterns

### Basic Usage

```python
# Initialize detector
dwpose = DWposeDetector()

# Process image
pose_map = dwpose(input_image)
```

### Advanced Configuration

The detector supports custom model configurations and checkpoints:

```python
# Custom configuration
dwpose = DWposeDetector(
    det_config="path/to/detection_config.py",
    det_ckpt="path/to/detection_checkpoint.pth",
    pose_config="path/to/pose_config.py", 
    pose_ckpt="path/to/pose_checkpoint.pth",
    device="cuda"
)

# Process with custom resolutions
result = dwpose(
    input_image,
    detect_resolution=640,
    image_resolution=768,
    output_type="np"
)
```

**Sources:** [tests/test_controlnet_aux.py:123-126]()

## Model Dependencies

The DWpose detector requires several MMOpenLab packages:

| Package | Purpose | Version Requirement |
|---------|---------|---------------------|
| `mmcv` | Computer vision foundation | `>=2.0.1` |
| `mmpose` | Pose estimation framework | `>=1.1.0` |
| `mmdet` | Object detection framework | `>=3.1.0` |

The system gracefully handles missing dependencies by issuing warnings and limiting functionality when packages are unavailable.

**Sources:** [src/controlnet_aux/dwpose/wholebody.py:6-30]()

## Configuration Files

### Detection Configuration

The YOLOX detector uses a large model configuration with the following key settings:

- **Architecture**: YOLOX-L with CSPDarknet backbone
- **Input Size**: 640×640 pixels
- **Training**: 300 epochs with mosaic and mixup augmentation
- **NMS Threshold**: 0.65 IoU threshold

### Pose Configuration  

The DWpose model configuration includes:

- **Architecture**: CSPNeXt backbone with RTMCCHead
- **Input Size**: 288×384 pixels
- **Output**: 133 keypoints with SimCC encoding
- **Training**: 270 epochs with cosine annealing schedule

**Sources:** [src/controlnet_aux/dwpose/yolox_config/yolox_l_8xb8-300e_coco.py](), [src/controlnet_aux/dwpose/dwpose_config/dwpose-l_384x288.py]()

---

