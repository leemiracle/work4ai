<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page OpenPose Detector · fetched 2026-10-26 -->

# OpenPose Detector

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/open_pose/__init__.py](src/controlnet_aux/open_pose/__init__.py)
- [src/controlnet_aux/open_pose/body.py](src/controlnet_aux/open_pose/body.py)
- [src/controlnet_aux/open_pose/face.py](src/controlnet_aux/open_pose/face.py)
- [src/controlnet_aux/open_pose/hand.py](src/controlnet_aux/open_pose/hand.py)
- [src/controlnet_aux/open_pose/util.py](src/controlnet_aux/open_pose/util.py)

</details>



The OpenPose Detector provides classic OpenPose implementation for human pose estimation, supporting modular detection of body keypoints, hand landmarks, and facial features. This detector uses separate neural network models for each component and combines them into comprehensive pose results.

For whole-body pose detection with unified processing, see [DWpose Detector](#4.3.1).

## System Architecture

The OpenPose detector follows a modular three-component architecture where each detection type (body, hand, face) operates as an independent subsystem with its own neural network model.

```mermaid
graph TD
    subgraph "OpenposeDetector Class"
        DETECTOR["OpenposeDetector<br/>Main Controller"]
        INIT_METHOD["from_pretrained()<br/>Factory Method"]
        DETECT_METHOD["detect_poses()<br/>Orchestration"]
        CALL_METHOD["__call__()<br/>Public API"]
    end
    
    subgraph "Component Models"
        BODY_EST["Body<br/>body_estimation"]
        HAND_EST["Hand<br/>hand_estimation"] 
        FACE_EST["Face<br/>face_estimation"]
    end
    
    subgraph "Neural Networks"
        BODY_MODEL["bodypose_model()<br/>Body CNN"]
        HAND_MODEL["handpose_model()<br/>Hand CNN"]
        FACE_NET["FaceNet<br/>Face CNN"]
    end
    
    subgraph "Detection Pipeline"
        BODY_DETECT["Body Detection<br/>18 keypoints"]
        HAND_DETECT["Hand Detection<br/>21 landmarks each"]
        FACE_DETECT["Face Detection<br/>70 landmarks"]
    end
    
    subgraph "Results Structure"
        POSE_RESULT["PoseResult<br/>Combined Result"]
        BODY_RESULT["BodyResult<br/>Body keypoints"]
        HAND_RESULT["HandResult<br/>Hand landmarks"]
        FACE_RESULT["FaceResult<br/>Face landmarks"]
    end
    
    DETECTOR --> BODY_EST
    DETECTOR --> HAND_EST
    DETECTOR --> FACE_EST
    
    BODY_EST --> BODY_MODEL
    HAND_EST --> HAND_MODEL
    FACE_EST --> FACE_NET
    
    DETECT_METHOD --> BODY_DETECT
    DETECT_METHOD --> HAND_DETECT
    DETECT_METHOD --> FACE_DETECT
    
    BODY_DETECT --> BODY_RESULT
    HAND_DETECT --> HAND_RESULT
    FACE_DETECT --> FACE_RESULT
    
    BODY_RESULT --> POSE_RESULT
    HAND_RESULT --> POSE_RESULT
    FACE_RESULT --> POSE_RESULT
```

Sources: [src/controlnet_aux/open_pose/__init__.py:70-235](), [src/controlnet_aux/open_pose/body.py:31-261](), [src/controlnet_aux/open_pose/hand.py:11-79](), [src/controlnet_aux/open_pose/face.py:306-364]()

## Core Data Structures

The detector uses structured data types to represent pose information at different levels of granularity.

| Data Structure | Purpose | Key Fields |
|----------------|---------|------------|
| `Keypoint` | Individual landmark | `x`, `y`, `score`, `id` |
| `BodyResult` | Body pose data | `keypoints`, `total_score`, `total_parts` |
| `HandResult` | Hand landmarks | `List[Keypoint]` |
| `FaceResult` | Face landmarks | `List[Keypoint]` |
| `PoseResult` | Complete pose | `body`, `left_hand`, `right_hand`, `face` |

```mermaid
graph LR
    subgraph "Data Structure Hierarchy"
        KEYPOINT["Keypoint<br/>{x, y, score, id}"]
        
        subgraph "Component Results"
            BODY_R["BodyResult<br/>{keypoints: List[Keypoint],<br/>total_score, total_parts}"]
            HAND_R["HandResult<br/>List[Keypoint]"]
            FACE_R["FaceResult<br/>List[Keypoint]"]
        end
        
        POSE_R["PoseResult<br/>{body: BodyResult,<br/>left_hand: HandResult,<br/>right_hand: HandResult,<br/>face: FaceResult}"]
    end
    
    KEYPOINT --> BODY_R
    KEYPOINT --> HAND_R
    KEYPOINT --> FACE_R
    
    BODY_R --> POSE_R
    HAND_R --> POSE_R
    FACE_R --> POSE_R
```

Sources: [src/controlnet_aux/open_pose/body.py:13-29](), [src/controlnet_aux/open_pose/__init__.py:30-37]()

## Detection Pipeline

The detection process follows a hierarchical approach where body detection drives hand and face region detection.

```mermaid
flowchart TD
    INPUT["Input Image<br/>numpy.ndarray"]
    
    subgraph "Body Detection Phase"
        BODY_PROC["Body.__call__()<br/>Multi-scale processing"]
        BODY_PEAKS["Peak Detection<br/>Heatmap analysis"]
        BODY_CONN["Connection Assembly<br/>Limb associations"]
        BODY_FMT["format_body_result()<br/>Structure conversion"]
    end
    
    subgraph "Conditional Detection"
        HAND_CHECK{"include_hand?"}
        FACE_CHECK{"include_face?"}
        
        subgraph "Hand Detection"
            HAND_REGION["handDetect()<br/>Region estimation"]
            HAND_PROC["Hand.__call__()<br/>Landmark detection"]
        end
        
        subgraph "Face Detection"
            FACE_REGION["faceDetect()<br/>Region estimation"]
            FACE_PROC["Face.__call__()<br/>Landmark detection"]
        end
    end
    
    RESULT_ASSEMBLY["PoseResult Assembly<br/>Coordinate normalization"]
    OUTPUT["List[PoseResult]"]
    
    INPUT --> BODY_PROC
    BODY_PROC --> BODY_PEAKS
    BODY_PEAKS --> BODY_CONN
    BODY_CONN --> BODY_FMT
    
    BODY_FMT --> HAND_CHECK
    BODY_FMT --> FACE_CHECK
    
    HAND_CHECK -->|Yes| HAND_REGION
    HAND_REGION --> HAND_PROC
    
    FACE_CHECK -->|Yes| FACE_REGION
    FACE_REGION --> FACE_PROC
    
    BODY_FMT --> RESULT_ASSEMBLY
    HAND_PROC --> RESULT_ASSEMBLY
    FACE_PROC --> RESULT_ASSEMBLY
    
    RESULT_ASSEMBLY --> OUTPUT
```

Sources: [src/controlnet_aux/open_pose/__init__.py:160-197](), [src/controlnet_aux/open_pose/body.py:42-227](), [src/controlnet_aux/open_pose/util.py:202-292](), [src/controlnet_aux/open_pose/util.py:296-374]()

## Model Loading and Configuration

The detector supports flexible model loading from Hugging Face Hub with component-specific checkpoints.

### Model Loading Process

```mermaid
graph TD
    subgraph "from_pretrained() Process"
        INPUT_PATH["pretrained_model_or_path<br/>Repository ID or local path"]
        
        subgraph "Path Resolution"
            CHECK_PATH{"os.path.isdir()?"}
            LOCAL_PATH["Local File Paths<br/>Direct concatenation"]
            HF_DOWNLOAD["hf_hub_download()<br/>Remote retrieval"]
        end
        
        subgraph "Default Configurations"
            CONTROLNET_DEFAULT["lllyasviel/ControlNet<br/>Standard checkpoint paths"]
            CUSTOM_PATHS["Custom filenames<br/>User-specified paths"]
        end
        
        subgraph "Model Instantiation"
            BODY_INIT["Body(body_model_path)"]
            HAND_INIT["Hand(hand_model_path)"]
            FACE_INIT["Face(face_model_path)"]
        end
        
        DETECTOR_INIT["OpenposeDetector()<br/>Component assembly"]
    end
    
    INPUT_PATH --> CHECK_PATH
    CHECK_PATH -->|True| LOCAL_PATH
    CHECK_PATH -->|False| HF_DOWNLOAD
    
    INPUT_PATH --> CONTROLNET_DEFAULT
    INPUT_PATH --> CUSTOM_PATHS
    
    LOCAL_PATH --> BODY_INIT
    HF_DOWNLOAD --> BODY_INIT
    LOCAL_PATH --> HAND_INIT
    HF_DOWNLOAD --> HAND_INIT
    LOCAL_PATH --> FACE_INIT
    HF_DOWNLOAD --> FACE_INIT
    
    BODY_INIT --> DETECTOR_INIT
    HAND_INIT --> DETECTOR_INIT
    FACE_INIT --> DETECTOR_INIT
```

### Default Model Configurations

| Component | Default Filename | Repository |
|-----------|------------------|------------|
| Body | `body_pose_model.pth` | `lllyasviel/ControlNet` |
| Hand | `hand_pose_model.pth` | `lllyasviel/ControlNet` |
| Face | `facenet.pth` | `lllyasviel/Annotators` |

Sources: [src/controlnet_aux/open_pose/__init__.py:82-111]()

## Component Details

### Body Detection

The `Body` class handles 18-keypoint body pose detection using a convolutional neural network with Part Affinity Fields (PAF).

**Key Processing Steps:**
- Multi-scale inference at scale factor 0.5
- Heatmap and PAF generation via `bodypose_model`
- Peak detection with Gaussian filtering
- Limb connection assembly using PAF vectors
- Person grouping with subset formation

**Keypoint Layout:**
```
0: Head, 1: Neck, 2: Right Shoulder, 3: Right Elbow, 4: Right Wrist
5: Left Shoulder, 6: Left Elbow, 7: Left Wrist, 8: Right Hip
9: Right Knee, 10: Right Ankle, 11: Left Hip, 12: Left Knee
13: Left Ankle, 14: Right Eye, 15: Left Eye, 16: Right Ear, 17: Left Ear
```

Sources: [src/controlnet_aux/open_pose/body.py:42-227](), [src/controlnet_aux/open_pose/body.py:229-260]()

### Hand Detection

The `Hand` class processes 21-landmark hand detection within body-derived bounding boxes.

**Processing Pipeline:**
- Multi-scale inference (0.5, 1.0, 1.5, 2.0)
- Gaussian blur preprocessing
- 128x128 normalized output resolution
- Peak detection with connected component analysis

**Region Detection:**
Hand regions are estimated from body keypoints using shoulder-elbow-wrist triangulation with configurable ratio parameters.

Sources: [src/controlnet_aux/open_pose/hand.py:22-79](), [src/controlnet_aux/open_pose/util.py:202-292]()

### Face Detection  

The `Face` class implements 70-landmark facial keypoint detection using a 6-stage convolutional model.

**Architecture Features:**
- `FaceNet` with cascading heatmap refinement
- VGG-style backbone with 6 iterative stages
- 384x384 input resolution with bilinear upsampling
- Configurable inference size and threshold parameters

**Detection Process:**
Face regions are derived from head-eye-ear keypoint relationships with adaptive bounding box sizing.

Sources: [src/controlnet_aux/open_pose/face.py:12-275](), [src/controlnet_aux/open_pose/face.py:306-364](), [src/controlnet_aux/open_pose/util.py:296-374]()

## Visualization System

The detector includes comprehensive drawing utilities for pose visualization.

### Drawing Functions

| Function | Purpose | Key Features |
|----------|---------|--------------|
| `draw_bodypose()` | Body skeleton rendering | Colored limbs, joint circles |
| `draw_handpose()` | Hand connection lines | HSV color coding, finger chains |
| `draw_facepose()` | Face landmark points | White circles, minimal styling |
| `draw_poses()` | Complete pose assembly | Configurable component visibility |

### Rendering Pipeline

```mermaid
graph LR
    subgraph "Visualization Pipeline"
        POSES["List[PoseResult]<br/>Normalized coordinates"]
        CANVAS["np.zeros((H, W, 3))<br/>Black canvas"]
        
        subgraph "Component Rendering"
            BODY_DRAW["draw_bodypose()<br/>Limb + joint rendering"]
            HAND_DRAW["draw_handpose()<br/>Connection lines"]
            FACE_DRAW["draw_facepose()<br/>Landmark points"]
        end
        
        COMPOSITE["Canvas composition<br/>Additive drawing"]
        OUTPUT["Final visualization<br/>RGB numpy array"]
    end
    
    POSES --> CANVAS
    CANVAS --> BODY_DRAW
    CANVAS --> HAND_DRAW  
    CANVAS --> FACE_DRAW
    
    BODY_DRAW --> COMPOSITE
    HAND_DRAW --> COMPOSITE
    FACE_DRAW --> COMPOSITE
    
    COMPOSITE --> OUTPUT
```

Sources: [src/controlnet_aux/open_pose/__init__.py:39-67](), [src/controlnet_aux/open_pose/util.py:69-197]()

## Usage Examples

### Basic Usage

```python
# Initialize detector
detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")

# Detect poses with body only
result = detector(image, include_body=True, include_hand=False, include_face=False)

# Full pose detection
result = detector(image, include_hand=True, include_face=True)
```

### Advanced Configuration

```python
# Custom model paths
detector = OpenposeDetector.from_pretrained(
    "custom/repo",
    filename="custom_body.pth",
    hand_filename="custom_hand.pth", 
    face_filename="custom_face.pth"
)

# Device placement
detector = detector.to("cuda")

# Resolution control
result = detector(image, detect_resolution=512, image_resolution=1024)
```

Sources: [src/controlnet_aux/open_pose/__init__.py:199-234]()

## Integration Points

The OpenPose detector integrates with the broader controlnet_aux ecosystem through:

- **Processor Interface**: Registered as `"openpose"` in the `MODELS` registry
- **Common Utilities**: Uses `HWC3()` and `resize_image()` from shared utilities  
- **Hugging Face Hub**: Automatic model downloading and caching
- **Device Management**: Consistent GPU/CPU handling across components

The detector outputs standard PIL Images or numpy arrays compatible with ControlNet preprocessing pipelines.

Sources: [src/controlnet_aux/open_pose/__init__.py:24](), [src/controlnet_aux/open_pose/__init__.py:199-234]()

---

