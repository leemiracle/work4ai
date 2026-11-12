<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/controlnet_aux · page 4 Detector Categories · fetched 2026-10-26 -->

# Detector Categories

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [setup.py](setup.py)
- [src/controlnet_aux/__init__.py](src/controlnet_aux/__init__.py)
- [src/controlnet_aux/processor.py](src/controlnet_aux/processor.py)
- [src/controlnet_aux/tests/test_processor_pytest.py](src/controlnet_aux/tests/test_processor_pytest.py)

</details>



This document provides a comprehensive overview of the different types of feature detectors available in controlnet_aux, organized by their primary functionality and intended use cases. The categorization system helps users understand which detector to use for specific image preprocessing tasks in ControlNet workflows.

For information about the unified interface to access these detectors, see [Processor Interface](#3.1). For details about the internal neural network architectures powering these detectors, see [Neural Network Architectures](#5.2).

## Detector Classification System

The controlnet_aux library organizes 20 different detector classes into five main functional categories. Each category serves a specific type of image analysis task required for ControlNet conditioning.

### Category-to-Code Mapping

```mermaid
graph TB
    subgraph "Functional Categories"
        EDGE["Edge Detection<br/>Boundary identification"]
        DEPTH["Depth Estimation<br/>3D structure analysis"] 
        POSE["Pose Detection<br/>Human keypoint extraction"]
        LINEART["Line Art Generation<br/>Sketch-style processing"]
        SEGMENT["Segmentation<br/>Region identification"]
    end
    
    subgraph "Edge Detection Classes"
        HED["HEDdetector"]
        CANNY["CannyDetector"] 
        PIDI["PidiNetDetector"]
        TEED["TEEDdetector"]
        ANYLINE["AnylineDetector"]
    end
    
    subgraph "Depth Estimation Classes"
        MIDAS["MidasDetector"]
        ZOE["ZoeDetector"]
        LERES["LeresDetector"] 
        NORMALBAE["NormalBaeDetector"]
    end
    
    subgraph "Pose Detection Classes"
        OPENPOSE["OpenposeDetector"]
        DWPOSE["DWposeDetector"]
    end
    
    subgraph "Line Art Classes"
        LINEART_DET["LineartDetector"]
        LINEART_ANIME["LineartAnimeDetector"]
        LINEART_STD["LineartStandardDetector"]
        MLSD["MLSDdetector"]
    end
    
    subgraph "Segmentation Classes"
        SAM["SamDetector"]
        MEDIAPIPE["MediapipeFaceDetector"]
        SHUFFLE["ContentShuffleDetector"]
    end
    
    EDGE --> HED
    EDGE --> CANNY
    EDGE --> PIDI
    EDGE --> TEED
    EDGE --> ANYLINE
    
    DEPTH --> MIDAS
    DEPTH --> ZOE
    DEPTH --> LERES
    DEPTH --> NORMALBAE
    
    POSE --> OPENPOSE
    POSE --> DWPOSE
    
    LINEART --> LINEART_DET
    LINEART --> LINEART_ANIME
    LINEART --> LINEART_STD
    LINEART --> MLSD
    
    SEGMENT --> SAM
    SEGMENT --> MEDIAPIPE
    SEGMENT --> SHUFFLE
```

**Sources:** [src/controlnet_aux/__init__.py:3-21](), [src/controlnet_aux/processor.py:20-49]()

## Edge Detection

Edge detection detectors identify boundaries and contours in images, producing binary or grayscale edge maps suitable for line-based ControlNet conditioning.

### Edge Detection Architecture

```mermaid
graph LR
    subgraph "Classical Methods"
        CANNY_CLASS["CannyDetector<br/>canny.py"]
    end
    
    subgraph "Neural Network Methods"
        HED_CLASS["HEDdetector<br/>hed.py"]
        PIDI_CLASS["PidiNetDetector<br/>pidi.py"] 
        TEED_CLASS["TEEDdetector<br/>teed.py"]
        ANYLINE_CLASS["AnylineDetector<br/>anyline.py"]
    end
    
    subgraph "Processor Interface Mappings"
        SCRIBBLE_HED["scribble_hed"]
        SOFTEDGE_HED["softedge_hed"]
        SCRIBBLE_PIDI["scribble_pidinet"]
        SOFTEDGE_PIDI["softedge_pidinet"]
        SAFE_VARIANTS["*safe variants"]
    end
    
    CANNY_CLASS --> CANNY_PROC["canny"]
    
    HED_CLASS --> SCRIBBLE_HED
    HED_CLASS --> SOFTEDGE_HED
    HED_CLASS --> SAFE_VARIANTS
    
    PIDI_CLASS --> SCRIBBLE_PIDI
    PIDI_CLASS --> SOFTEDGE_PIDI
    PIDI_CLASS --> SAFE_VARIANTS
    
    TEED_CLASS --> TEED_PROC["teed"]
    ANYLINE_CLASS --> ANYLINE_PROC["anyline"]
```

| Detector Class | Model Type | Key Features | Processor IDs |
|---|---|---|---|
| `CannyDetector` | Classical CV | Threshold-based, fast | `canny` |
| `HEDdetector` | CNN | Multi-scale, scribble mode | `scribble_hed`, `softedge_hed`, `*hedsafe` |
| `PidiNetDetector` | CNN | Safety filtering, scribble mode | `scribble_pidinet`, `softedge_pidinet`, `*pidsafe` |
| `TEEDdetector` | Lightweight CNN | Efficient edge detection | Not in processor |
| `AnylineDetector` | CNN | Combined edge+line detection | Not in processor |

**Sources:** [src/controlnet_aux/processor.py:22-26,34-37,48](), [README.md:105,126]()

## Depth Estimation

Depth estimation detectors perform monocular depth estimation, generating depth maps and normal maps for 3D-aware ControlNet conditioning.

### Depth Estimation Pipeline

```mermaid
graph TB
    subgraph "Input Processing"
        IMG["Input Image<br/>RGB PIL.Image"]
    end
    
    subgraph "Depth Models"
        MIDAS_MODEL["MidasDetector<br/>Dense Prediction Transformer"]
        ZOE_MODEL["ZoeDetector<br/>Metric depth estimation"] 
        LERES_MODEL["LeresDetector<br/>Multi-scale depth"]
    end
    
    subgraph "Normal Map Generation"
        NORMALBAE_MODEL["NormalBaeDetector<br/>Surface normal estimation"]
        MIDAS_NORMAL["MidasDetector<br/>normal_map=True"]
    end
    
    subgraph "Output Types"
        DEPTH_MAP["Depth Map<br/>Grayscale image"]
        NORMAL_MAP["Normal Map<br/>RGB surface normals"]
    end
    
    IMG --> MIDAS_MODEL
    IMG --> ZOE_MODEL
    IMG --> LERES_MODEL
    IMG --> NORMALBAE_MODEL
    
    MIDAS_MODEL --> DEPTH_MAP
    MIDAS_MODEL --> MIDAS_NORMAL
    ZOE_MODEL --> DEPTH_MAP
    LERES_MODEL --> DEPTH_MAP
    NORMALBAE_MODEL --> NORMAL_MAP
    MIDAS_NORMAL --> NORMAL_MAP
```

| Detector Class | Architecture | Processor IDs | Special Features |
|---|---|---|---|
| `MidasDetector` | DPT (Dense Prediction Transformer) | `depth_midas`, `normal_midas` | Optional normal map generation |
| `ZoeDetector` | ZoeDepth | `depth_zoe` | Metric depth, gamma correction |
| `LeresDetector` | LeRes | `depth_leres`, `depth_leres++` | Boost mode available |
| `NormalBaeDetector` | NormalBAE | `normal_bae` | Dedicated normal map generation |

**Sources:** [src/controlnet_aux/processor.py:26,38,42-44](), [README.md:79,86,89,121]()

## Pose Detection

Pose detection detectors extract human keypoints for body, hand, and face landmarks, enabling pose-conditioned image generation.

### Pose Detection Variants

```mermaid
graph TB
    subgraph "Pose Detector Classes"
        OPENPOSE_CLASS["OpenposeDetector<br/>open_pose.py"]
        DWPOSE_CLASS["DWposeDetector<br/>dwpose.py"]
    end
    
    subgraph "OpenPose Configurations"
        OPENPOSE_BASIC["openpose<br/>Body only"]
        OPENPOSE_HAND["openpose_hand<br/>Hands only"]
        OPENPOSE_FACE["openpose_face<br/>Body + Face"]
        OPENPOSE_FACEONLY["openpose_faceonly<br/>Face only"]
        OPENPOSE_FULL["openpose_full<br/>Body + Hands + Face"]
    end
    
    subgraph "DWPose Configuration"
        DWPOSE_FULL["dwpose<br/>Wholebody detection"]
    end
    
    subgraph "Keypoint Output"
        BODY_KEYPOINTS["Body Keypoints<br/>17 points"]
        HAND_KEYPOINTS["Hand Keypoints<br/>21 points each"]
        FACE_KEYPOINTS["Face Keypoints<br/>68 points"]
    end
    
    OPENPOSE_CLASS --> OPENPOSE_BASIC
    OPENPOSE_CLASS --> OPENPOSE_HAND
    OPENPOSE_CLASS --> OPENPOSE_FACE
    OPENPOSE_CLASS --> OPENPOSE_FACEONLY
    OPENPOSE_CLASS --> OPENPOSE_FULL
    
    DWPOSE_CLASS --> DWPOSE_FULL
    
    OPENPOSE_BASIC --> BODY_KEYPOINTS
    OPENPOSE_HAND --> HAND_KEYPOINTS
    OPENPOSE_FACE --> BODY_KEYPOINTS
    OPENPOSE_FACE --> FACE_KEYPOINTS
    OPENPOSE_FACEONLY --> FACE_KEYPOINTS
    OPENPOSE_FULL --> BODY_KEYPOINTS
    OPENPOSE_FULL --> HAND_KEYPOINTS
    OPENPOSE_FULL --> FACE_KEYPOINTS
    
    DWPOSE_FULL --> BODY_KEYPOINTS
    DWPOSE_FULL --> HAND_KEYPOINTS
    DWPOSE_FULL --> FACE_KEYPOINTS
```

**Sources:** [src/controlnet_aux/processor.py:28-33,59-63](), [README.md:81,115,129]()

## Line Art Generation

Line art detectors generate sketch-like representations and line segment detection for artistic and structural line-based conditioning.

### Line Art Processing Types

```mermaid
graph LR
    subgraph "Line Art Detector Classes"
        LINEART_CLASS["LineartDetector<br/>lineart.py"]
        LINEART_ANIME_CLASS["LineartAnimeDetector<br/>lineart_anime.py"]
        LINEART_STD_CLASS["LineartStandardDetector<br/>lineart_standard.py"]
        MLSD_CLASS["MLSDdetector<br/>mlsd.py"]
    end
    
    subgraph "Processing Modes"
        REALISTIC["lineart_realistic<br/>Fine detail preservation"]
        COARSE["lineart_coarse<br/>Simplified lines"]
        ANIME["lineart_anime<br/>Anime-style processing"]
        STANDARD["Standard processing<br/>Direct instantiation"]
        SEGMENTS["mlsd<br/>Line segment detection"]
    end
    
    subgraph "Output Characteristics"
        DETAILED_LINES["Detailed Line Art<br/>Complex scenes"]
        SIMPLE_LINES["Simplified Line Art<br/>Clean sketches"]
        ANIME_STYLE["Anime Line Art<br/>Stylized processing"]
        MOBILE_SEGMENTS["Mobile Line Segments<br/>Structural lines"]
    end
    
    LINEART_CLASS --> REALISTIC
    LINEART_CLASS --> COARSE
    LINEART_ANIME_CLASS --> ANIME
    LINEART_STD_CLASS --> STANDARD
    MLSD_CLASS --> SEGMENTS
    
    REALISTIC --> DETAILED_LINES
    COARSE --> SIMPLE_LINES
    ANIME --> ANIME_STYLE
    STANDARD --> DETAILED_LINES
    SEGMENTS --> MOBILE_SEGMENTS
```

| Detector Class | Architecture | Processor IDs | Specialization |
|---|---|---|---|
| `LineartDetector` | U-Net | `lineart_realistic`, `lineart_coarse` | General line art with quality control |
| `LineartAnimeDetector` | U-Net | `lineart_anime` | Anime/manga style optimization |
| `LineartStandardDetector` | U-Net | Not in processor | Direct instantiation only |
| `MLSDdetector` | Mobile architecture | `mlsd` | Mobile line segment detection |

**Sources:** [src/controlnet_aux/processor.py:27,39-41,70-72](), [src/controlnet_aux/__init__.py:8-10,13](), [README.md:80,84-85,114,130]()

## Segmentation

Segmentation detectors identify and isolate regions, objects, or specific features for mask-based ControlNet conditioning.

### Segmentation Detector Types

```mermaid
graph TB
    subgraph "Segmentation Classes"
        SAM_CLASS["SamDetector<br/>segment_anything.py"]
        MEDIAPIPE_CLASS["MediapipeFaceDetector<br/>mediapipe_face.py"]
        SHUFFLE_CLASS["ContentShuffleDetector<br/>shuffle.py"]
    end
    
    subgraph "SAM Model Variants"
        SAM_VIT_H["ViT-H<br/>Highest accuracy"]
        SAM_VIT_L["ViT-L<br/>Balanced performance"]  
        SAM_VIT_B["ViT-B<br/>Faster inference"]
        MOBILE_SAM["MobileSAM<br/>Mobile deployment"]
    end
    
    subgraph "Specialized Segmentation"
        FACE_LANDMARKS["Face Landmarks<br/>468 facial points"]
        CONTENT_SHUFFLE["Content Shuffle<br/>Region randomization"]
    end
    
    subgraph "Output Types"
        UNIVERSAL_MASKS["Universal Object Masks"]
        FACE_MESH["Face Mesh Annotations"]
        SHUFFLED_REGIONS["Shuffled Content Map"]
    end
    
    SAM_CLASS --> SAM_VIT_H
    SAM_CLASS --> SAM_VIT_L
    SAM_CLASS --> SAM_VIT_B
    SAM_CLASS --> MOBILE_SAM
    
    MEDIAPIPE_CLASS --> FACE_LANDMARKS
    SHUFFLE_CLASS --> CONTENT_SHUFFLE
    
    SAM_VIT_H --> UNIVERSAL_MASKS
    SAM_VIT_L --> UNIVERSAL_MASKS
    SAM_VIT_B --> UNIVERSAL_MASKS
    MOBILE_SAM --> UNIVERSAL_MASKS
    
    FACE_LANDMARKS --> FACE_MESH
    CONTENT_SHUFFLE --> SHUFFLED_REGIONS
```

| Detector Class | Technology | Processor IDs | Use Case |
|---|---|---|---|
| `SamDetector` | Segment Anything Model | Not in processor | Universal object segmentation |
| `MediapipeFaceDetector` | MediaPipe | `mediapipe_face` | Face landmark detection |
| `ContentShuffleDetector` | Algorithmic | `shuffle` | Content region shuffling |

**Sources:** [src/controlnet_aux/processor.py:46-47](), [README.md:87-88,106-107,127-128]()

## Processor Integration

All detector categories integrate with the unified `Processor` interface through the `MODELS` registry system, enabling consistent access patterns across different detector types.

### Processor Registry Mapping

```mermaid
graph TB
    subgraph "Processor Registry"
        MODELS_DICT["MODELS dictionary<br/>processor.py:20-49"]
        PARAMS_DICT["MODEL_PARAMS dictionary<br/>processor.py:52-79"]
    end
    
    subgraph "Loading Strategies"
        CHECKPOINT["checkpoint: True<br/>from_pretrained()"]
        INSTANTIATE["checkpoint: False<br/>direct __init__()"]
    end
    
    subgraph "Checkpoint Models"
        NEURAL_MODELS["Neural Network Detectors<br/>HED, MiDaS, OpenPose, etc."]
    end
    
    subgraph "Instantiate Models"  
        ALGORITHMIC_MODELS["Algorithmic Detectors<br/>Canny, Shuffle, MediaPipe"]
    end
    
    MODELS_DICT --> CHECKPOINT
    MODELS_DICT --> INSTANTIATE
    
    CHECKPOINT --> NEURAL_MODELS
    INSTANTIATE --> ALGORITHMIC_MODELS
    
    PARAMS_DICT --> NEURAL_MODELS
    PARAMS_DICT --> ALGORITHMIC_MODELS
```

The `MODELS` dictionary in [src/controlnet_aux/processor.py:20-49]() maps 25 processor IDs to their corresponding detector classes and loading strategies. Models requiring pretrained weights use `checkpoint: True`, while algorithmic detectors use `checkpoint: False` for direct instantiation.

**Sources:** [src/controlnet_aux/processor.py:20-49,52-79,117-124](), [src/controlnet_aux/__init__.py:1-21]()

---

