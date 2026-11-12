<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · extra page Face and Content Detectors · fetched 2026-10-26 -->

# Face and Content Detectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/controlnet_aux/canny/__init__.py](src/controlnet_aux/canny/__init__.py)
- [src/controlnet_aux/mediapipe_face/__init__.py](src/controlnet_aux/mediapipe_face/__init__.py)
- [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py](src/controlnet_aux/mediapipe_face/mediapipe_face_common.py)
- [src/controlnet_aux/segment_anything/__init__.py](src/controlnet_aux/segment_anything/__init__.py)

</details>



This document covers specialized detectors for facial landmark detection and content manipulation within the controlnet_aux library. The face detector uses MediaPipe to identify and annotate facial features, while content detectors provide image transformation capabilities for preprocessing workflows.

For universal object segmentation capabilities, see [SAM Detector](#4.5.1). For pose estimation including face keypoints, see [Pose Estimation](#4.3).

## MediaPipe Face Detection

The `MediapipeFaceDetector` provides precise facial landmark detection using Google's MediaPipe framework. This detector identifies key facial features including eyes, eyebrows, lips, and face contours, producing detailed annotations suitable for face-aware image processing.

### MediapipeFaceDetector Class

The main detector class implements the standard controlnet_aux interface pattern:

```mermaid
graph TB
    subgraph "MediapipeFaceDetector Interface"
        INIT[MediapipeFaceDetector]
        CALL["__call__()"]
        PARAMS["Parameters:<br/>max_faces: int<br/>min_confidence: float<br/>detect_resolution: int<br/>image_resolution: int"]
    end
    
    subgraph "Core Processing Pipeline"
        PREPROCESS["Image Preprocessing<br/>HWC3, resize_image"]
        GENERATE["generate_annotation()<br/>MediaPipe FaceMesh"]
        POSTPROCESS["Post-processing<br/>Resize, format conversion"]
    end
    
    subgraph "MediaPipe Components"
        FACEMESH["mp_face_mesh.FaceMesh<br/>static_image_mode=True<br/>refine_landmarks=True"]
        LANDMARKS["Face Landmark Detection<br/>468 3D landmarks"]
        FILTER["Face Size Filtering<br/>min_face_size_pixels"]
    end
    
    INIT --> CALL
    CALL --> PARAMS
    CALL --> PREPROCESS
    PREPROCESS --> GENERATE
    GENERATE --> FACEMESH
    FACEMESH --> LANDMARKS
    LANDMARKS --> FILTER
    FILTER --> POSTPROCESS
    
    style INIT fill:#f9f9f9
    style GENERATE fill:#e1f5fe
    style FACEMESH fill:#fff3e0
```

**MediapipeFaceDetector Processing Flow**

Sources: [src/controlnet_aux/mediapipe_face/__init__.py:12-53]()

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_faces` | int | 1 | Maximum number of faces to detect |
| `min_confidence` | float | 0.5 | Minimum detection confidence threshold |
| `detect_resolution` | int | 512 | Resolution for face detection processing |
| `image_resolution` | int | 512 | Output image resolution |

The detector accepts both PIL Images and numpy arrays, with automatic format detection and conversion.

Sources: [src/controlnet_aux/mediapipe_face/__init__.py:13-20]()

### Face Mesh Generation

The core facial landmark detection is implemented in the `generate_annotation` function, which orchestrates MediaPipe's FaceMesh processing:

```mermaid
graph TB
    subgraph "generate_annotation Function"
        INPUT["Input Image<br/>RGB format"]
        FACEMESH_INIT["FaceMesh Initialization<br/>max_num_faces<br/>refine_landmarks<br/>min_detection_confidence"]
        PROCESS["facemesh.process()<br/>Extract multi_face_landmarks"]
    end
    
    subgraph "Face Processing Pipeline"
        DETECT["Face Detection<br/>468 landmarks per face"]
        FILTER_SIZE["Size Filtering<br/>Calculate face_rect<br/>Check min_face_size_pixels"]
        FILTER_CONF["Confidence Filtering<br/>visibility > 0.9<br/>presence > 0.5"]
    end
    
    subgraph "Annotation Drawing"
        EMPTY["Create empty canvas<br/>numpy.zeros_like()"]
        DRAW_LANDMARKS["mp_drawing.draw_landmarks()<br/>Face contours, eyes, lips"]
        DRAW_PUPILS["draw_pupils()<br/>Custom iris drawing"]
        CONVERT["BGR to RGB conversion<br/>reverse_channels()"]
    end
    
    INPUT --> FACEMESH_INIT
    FACEMESH_INIT --> PROCESS
    PROCESS --> DETECT
    DETECT --> FILTER_SIZE
    FILTER_SIZE --> FILTER_CONF
    FILTER_CONF --> EMPTY
    EMPTY --> DRAW_LANDMARKS
    DRAW_LANDMARKS --> DRAW_PUPILS
    DRAW_PUPILS --> CONVERT
    
    style FACEMESH_INIT fill:#e8f5e8
    style DRAW_LANDMARKS fill:#fff3e0
    style DRAW_PUPILS fill:#f3e5f5
```

**Face Mesh Annotation Pipeline**

Sources: [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py:96-164]()

### Facial Feature Specifications

The detector uses predefined drawing specifications for different facial components:

```mermaid
graph LR
    subgraph "Drawing Specifications"
        IRIS_R["right_iris_draw<br/>color: (10, 200, 250)<br/>thickness: 2"]
        EYE_R["right_eye_draw<br/>color: (10, 200, 180)<br/>thickness: 2"]
        EYEBROW_R["right_eyebrow_draw<br/>color: (10, 220, 180)<br/>thickness: 2"]
        IRIS_L["left_iris_draw<br/>color: (250, 200, 10)<br/>thickness: 2"]
        EYE_L["left_eye_draw<br/>color: (180, 200, 10)<br/>thickness: 2"]
        EYEBROW_L["left_eyebrow_draw<br/>color: (180, 220, 10)<br/>thickness: 2"]
        MOUTH["mouth_draw<br/>color: (10, 180, 10)<br/>thickness: 2"]
        HEAD["head_draw<br/>color: (10, 200, 10)<br/>thickness: 2"]
    end
    
    subgraph "Face Connection Mapping"
        FACE_OVAL["FACEMESH_FACE_OVAL → head_draw"]
        LEFT_EYE["FACEMESH_LEFT_EYE → left_eye_draw"]
        RIGHT_EYE["FACEMESH_RIGHT_EYE → right_eye_draw"]
        LEFT_BROW["FACEMESH_LEFT_EYEBROW → left_eyebrow_draw"]
        RIGHT_BROW["FACEMESH_RIGHT_EYEBROW → right_eyebrow_draw"]
        LIPS["FACEMESH_LIPS → mouth_draw"]
    end
    
    IRIS_R --> FACE_OVAL
    EYE_R --> RIGHT_EYE
    EYEBROW_R --> RIGHT_BROW
    IRIS_L --> FACE_OVAL
    EYE_L --> LEFT_EYE
    EYEBROW_L --> LEFT_BROW
    MOUTH --> LIPS
    HEAD --> FACE_OVAL
```

**Facial Feature Drawing Configuration**

Sources: [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py:27-58]()

### Face Size Filtering

The detector implements intelligent face filtering based on pixel size to ensure meaningful detection results:

| Filter Stage | Implementation | Purpose |
|--------------|----------------|---------|
| **Bounding Box Calculation** | `face_rect` computation from landmarks | Determine face dimensions |
| **Pixel Size Check** | `face_width_pixels`, `face_height_pixels` | Convert to absolute pixels |
| **Minimum Size Filter** | `face_size >= min_face_size_pixels` | Reject small faces |
| **Confidence Thresholding** | `visibility > 0.9`, `presence > 0.5` | Quality assurance |

Sources: [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py:121-145]()

## Content Processing Detectors

Content processing detectors provide image transformation and manipulation capabilities for preprocessing workflows. These detectors handle content shuffling, rearrangement, and other data augmentation techniques commonly used in computer vision pipelines.

### Integration with Segmentation Framework

Face and content detectors integrate seamlessly with the controlnet_aux segmentation framework:

```mermaid
graph TB
    subgraph "Segmentation Category (4.5)"
        SAM["SAM Detector<br/>Universal Segmentation"]
        FACE["MediapipeFaceDetector<br/>Face Landmarks"]
        CONTENT["Content Detectors<br/>Image Transformation"]
    end
    
    subgraph "Common Processing Pipeline"
        INPUT["Input Image<br/>PIL/numpy array"]
        PREPROCESS["Image Preprocessing<br/>HWC3, resize_image"]
        DETECT["Detection/Processing<br/>Detector-specific logic"]
        POSTPROCESS["Output Formatting<br/>PIL/numpy conversion"]
    end
    
    subgraph "MediaPipe Dependencies"
        MP_IMPORT["mediapipe import<br/>Optional dependency"]
        MP_FACEMESH["mp_face_mesh.FaceMesh<br/>Core detection"]
        MP_DRAWING["mp_drawing utilities<br/>Annotation rendering"]
    end
    
    SAM --> INPUT
    FACE --> INPUT
    CONTENT --> INPUT
    
    INPUT --> PREPROCESS
    PREPROCESS --> DETECT
    DETECT --> POSTPROCESS
    
    FACE --> MP_IMPORT
    MP_IMPORT --> MP_FACEMESH
    MP_FACEMESH --> MP_DRAWING
    
    style FACE fill:#e1f5fe
    style MP_IMPORT fill:#fff3e0
```

**Segmentation Framework Integration**

Sources: [src/controlnet_aux/mediapipe_face/__init__.py:1-54](), [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py:4-11]()

### Error Handling and Dependencies

The MediaPipe face detector implements robust error handling for optional dependencies:

- **MediaPipe Import**: Graceful degradation when MediaPipe is not installed
- **Input Validation**: Comprehensive checks for image format and parameters
- **Face Detection Fallback**: Zero-filled image return when no faces detected
- **Parameter Deprecation**: Backward compatibility with warning messages

Sources: [src/controlnet_aux/mediapipe_face/mediapipe_face_common.py:4-11](), [src/controlnet_aux/mediapipe_face/__init__.py:22-35]()

---

