<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Samples · page 2 Character Models and Stylization · fetched 2026-10-26 -->

# Character Models and Stylization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/claire_stylization_config.yaml](configs/claire_stylization_config.yaml)
- [configs/james_stylization_config.yaml](configs/james_stylization_config.yaml)
- [configs/mark_stylization_config.yaml](configs/mark_stylization_config.yaml)

</details>



This document covers the three pre-configured character models available in the Audio2Face-3D system: Claire, James, and Mark. It explains the configuration structure, stylization parameters, and how each character's Audio2Emotion (A2E) and Audio2Face (A2F) settings are customized for optimal performance.

For detailed configuration parameters of individual characters, see [Claire Configuration](#2.1), [James Configuration](#2.2), and [Mark Configuration](#2.3). For information about configuration management and migration tools, see [Configuration Management](#3).

## Character Model System Overview

The Audio2Face-3D system provides three distinct character models, each with specialized configuration files that define their emotional response patterns and facial animation parameters. Each character uses specific inference models and blendshape configurations optimized for their facial topology.

### Character Model Architecture

```mermaid
graph TB
    subgraph "Character Models"
        Claire["Claire Model<br/>claire_v2.3"]
        James["James Model<br/>james_v2.3"] 
        Mark["Mark Model<br/>mark_v2.3"]
    end
    
    subgraph "Configuration Files"
        ClaireConfig["claire_stylization_config.yaml"]
        JamesConfig["james_stylization_config.yaml"]
        MarkConfig["mark_stylization_config.yaml"]
    end
    
    subgraph "Model Components"
        InferenceModels["A2F Inference Models<br/>claire_v2.3, james_v2.3, mark_v2.3"]
        BlendshapeModels["Blendshape Models<br/>claire_topo1_v2.1<br/>james_topo2_v2.2<br/>mark_topo1_v2.1"]
        TongueModels["Tongue Models<br/>*_tongue_v1.0"]
    end
    
    subgraph "Processing Pipeline"
        A2E["Audio2Emotion Processing<br/>emotion detection & smoothing"]
        A2F["Audio2Face Processing<br/>facial animation generation"]
    end
    
    Claire --> ClaireConfig
    James --> JamesConfig  
    Mark --> MarkConfig
    
    ClaireConfig --> InferenceModels
    JamesConfig --> InferenceModels
    MarkConfig --> InferenceModels
    
    ClaireConfig --> BlendshapeModels
    JamesConfig --> BlendshapeModels
    MarkConfig --> BlendshapeModels
    
    InferenceModels --> A2E
    InferenceModels --> A2F
    BlendshapeModels --> A2F
    TongueModels --> A2F
```

**Sources:** [configs/claire_stylization_config.yaml:42-46](), [configs/james_stylization_config.yaml:42-46](), [configs/mark_stylization_config.yaml:42-46]()

## Configuration File Structure

Each character's stylization configuration follows a consistent YAML structure with four main sections that control different aspects of the character's behavior and appearance.

### Configuration Schema

```mermaid
graph LR
    subgraph "Stylization Config Structure"
        Config["*_stylization_config.yaml"]
        
        subgraph "Main Sections"
            DefaultEmotions["default_beginning_emotions<br/>Initial emotion state"]
            A2E["a2e<br/>Audio2Emotion parameters"]
            A2F["a2f<br/>Audio2Face parameters"]
        end
        
        subgraph "A2E Parameters"
            A2EEnabled["enabled: true/false"]
            TransitionTime["live_transition_time"]
            PostProcessing["post_processing_params"]
        end
        
        subgraph "A2F Parameters" 
            ModelID["inference_model_id"]
            BlendshapeID["blendshape_id"]
            TongueID["tongue_blendshape_id"]
            FaceParams["face_params"]
            BlendshapeParams["blendshape_params"]
        end
        
        subgraph "Blendshape Parameters"
            WeightMult["weight_multipliers"]
            WeightOffset["weight_offsets"] 
            ActivePoses["active_poses"]
            CancelPoses["cancel_poses"]
            SymmetryPoses["symmetry_poses"]
        end
    end
    
    Config --> DefaultEmotions
    Config --> A2E
    Config --> A2F
    
    A2E --> A2EEnabled
    A2E --> TransitionTime
    A2E --> PostProcessing
    
    A2F --> ModelID
    A2F --> BlendshapeID
    A2F --> TongueID
    A2F --> FaceParams
    A2F --> BlendshapeParams
    
    BlendshapeParams --> WeightMult
    BlendshapeParams --> WeightOffset
    BlendshapeParams --> ActivePoses
    BlendshapeParams --> CancelPoses
    BlendshapeParams --> SymmetryPoses
```

**Sources:** [configs/claire_stylization_config.yaml:16-332](), [configs/james_stylization_config.yaml:16-332](), [configs/mark_stylization_config.yaml:16-332]()

## Audio2Emotion Configuration

All three characters share identical Audio2Emotion (A2E) processing parameters, providing consistent emotional response behavior across the character set. The A2E system analyzes input audio to detect emotional content and applies smoothing and post-processing to generate natural emotional transitions.

### Emotion Types and Default Values

| Emotion | Default Value | Range | Description |
|---------|---------------|-------|-------------|
| `amazement` | 0.0 | 0.0-1.0 | Wonder and surprise |
| `anger` | 0.0 | 0.0-1.0 | Hostile or aggressive emotion |
| `cheekiness` | 0.0 | 0.0-1.0 | Playful or mischievous behavior |
| `disgust` | 0.0 | 0.0-1.0 | Revulsion or distaste |
| `fear` | 0.0 | 0.0-1.0 | Anxiety or apprehension |
| `grief` | 0.0 | 0.0-1.0 | Deep sorrow or mourning |
| `joy` | 0.0 | 0.0-1.0 | Happiness and pleasure |
| `outofbreath` | 0.0 | 0.0-1.0 | Physical exertion state |
| `pain` | 0.0 | 0.0-1.0 | Physical or emotional suffering |
| `sadness` | 0.0 | 0.0-1.0 | Low-energy negative emotion |

### A2E Processing Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `enabled` | `true` | Enables Audio2Emotion processing |
| `live_transition_time` | `0.5` | Seconds for emotion transitions |
| `emotion_contrast` | `1.0` | Increases spread between emotion values |
| `emotion_strength` | `0.6` | Strength of generated emotions vs neutral |
| `enable_preferred_emotion` | `true` | Blends preferred emotion with auto-emotion |
| `live_blend_coef` | `0.7` | Exponential smoothing coefficient |
| `max_emotions` | `3` | Maximum simultaneous active emotions |
| `preferred_emotion_strength` | `0.5` | Strength of preferred emotion blending |

**Sources:** [configs/claire_stylization_config.yaml:16-39](), [configs/james_stylization_config.yaml:16-39](), [configs/mark_stylization_config.yaml:16-39]()

## Audio2Face Model Configuration

Each character uses distinct Audio2Face models and blendshape configurations tailored to their specific facial topology and animation requirements.

### Character Model Specifications

| Character | Inference Model | Blendshape Model | Tongue Model | Tongue Enabled |
|-----------|----------------|------------------|--------------|----------------|
| Claire | `claire_v2.3` | `claire_topo1_v2.1` | `claire_tongue_v1.0` | `true` |
| James | `james_v2.3` | `james_topo2_v2.2` | `james_tongue_v1.0` | `true` |
| Mark | `mark_v2.3` | `mark_topo1_v2.1` | `mark_tongue_v1.0` | `true` |

### Face Parameter Differences

The characters have distinct face parameter tuning to accommodate their unique facial characteristics:

| Parameter | Claire | James | Mark | Description |
|-----------|--------|-------|------|-------------|
| `eyelid_offset` | `0.0` | `0.06` | `0.06` | Default eyelid pose adjustment |
| `lip_close_offset` | `0.0` | `-0.02` | `-0.03` | Default lip closure pose |
| `input_strength` | `1.0` | `1.0` | `1.3` | Audio input magnitude control |
| `lower_face_smoothing` | `0.006` | `0.006` | `0.0023` | Temporal smoothing for lower face |
| `lower_face_strength` | `1.25` | `1.2` | `1.4` | Range of motion for lower face |
| `skin_strength` | `1.0` | `1.0` | `1.1` | Skin motion range control |

**Sources:** [configs/claire_stylization_config.yaml:48-58](), [configs/james_stylization_config.yaml:48-58](), [configs/mark_stylization_config.yaml:48-58]()

## Blendshape Parameter System

The blendshape system controls facial animation through 52 individual facial poses, each with configurable weight multipliers, offsets, and activation states. All characters use identical blendshape parameter structures but may have different model topologies.

### Blendshape Categories

```mermaid
graph TB
    subgraph "Blendshape Categories"
        EyeControls["Eye Controls<br/>14 blendshapes"]
        JawControls["Jaw Controls<br/>4 blendshapes"] 
        MouthControls["Mouth Controls<br/>24 blendshapes"]
        BrowControls["Brow Controls<br/>5 blendshapes"]
        CheekControls["Cheek Controls<br/>3 blendshapes"]
        NoseControls["Nose Controls<br/>2 blendshapes"]
        TongueControls["Tongue Controls<br/>1 blendshape"]
    end
    
    subgraph "Eye Blendshapes"
        EyeBlink["EyeBlinkLeft/Right"]
        EyeLook["EyeLookDown/In/Out/Up Left/Right"]
        EyeSquint["EyeSquintLeft/Right"] 
        EyeWide["EyeWideLeft/Right"]
    end
    
    subgraph "Mouth Blendshapes"
        MouthBasic["MouthClose/Funnel/Pucker"]
        MouthMovement["MouthLeft/Right"] 
        MouthExpression["MouthSmile/Frown/Dimple Left/Right"]
        MouthShape["MouthStretch/Roll/Shrug/Press"]
        MouthVertical["MouthLowerDown/UpperUp Left/Right"]
    end
    
    subgraph "Parameter Types"
        WeightMult["weight_multipliers<br/>Scale factor for blendshape"]
        WeightOffset["weight_offsets<br/>Baseline offset value"]
        ActivePoses["active_poses<br/>Enable/disable blendshape"]
        CancelPoses["cancel_poses<br/>Mutual exclusion groups"]
        SymmetryPoses["symmetry_poses<br/>Left/right symmetry pairs"]
    end
    
    EyeControls --> EyeBlink
    EyeControls --> EyeLook
    EyeControls --> EyeSquint
    EyeControls --> EyeWide
    
    MouthControls --> MouthBasic
    MouthControls --> MouthMovement
    MouthControls --> MouthExpression
    MouthControls --> MouthShape
    MouthControls --> MouthVertical
```

**Sources:** [configs/claire_stylization_config.yaml:63-331](), [configs/james_stylization_config.yaml:63-331](), [configs/mark_stylization_config.yaml:63-331]()

### Blendshape Control Parameters

Each blendshape is controlled by five parameter types:

- **`weight_multipliers`**: Scaling factor applied to blendshape weights (default: `1.0`)
- **`weight_offsets`**: Baseline offset added to blendshape weights (default: `0.0`)  
- **`active_poses`**: Enable (`1`) or disable (`0`) individual blendshapes
- **`cancel_poses`**: Grouping for mutually exclusive blendshapes (value: `-1`)
- **`symmetry_poses`**: Pairing for left/right symmetric blendshapes (shared group numbers)

### Notable Blendshape Configurations

| Blendshape Group | Active State | Symmetry Groups | Notes |
|------------------|--------------|-----------------|-------|
| Eye Look Controls | Disabled (`0`) | Individual (`-1`) | Gaze tracking disabled by default |
| Tongue Out | Disabled (`0`) | Individual (`-1`) | Requires explicit activation |
| Mouth Smile/Frown | Enabled (`1`) | Paired (`2`/`3`) | Symmetric expression pairs |
| Brow Controls | Enabled (`1`) | Outer paired (`9`), Inner individual | Asymmetric brow capability |

**Sources:** [configs/claire_stylization_config.yaml:171-331](), [configs/james_stylization_config.yaml:171-331](), [configs/mark_stylization_config.yaml:171-331]()

---

