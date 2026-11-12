<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CoCosNet · extra page DeepFashion Dataset · fetched 2026-10-26 -->

# DeepFashion Dataset

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/deepfashion_dataset.py](data/deepfashion_dataset.py)
- [data/deepfashion_ref_test.txt](data/deepfashion_ref_test.txt)
- [data/deepfashion_self_pair.txt](data/deepfashion_self_pair.txt)

</details>



This document describes the `DeepFashionDataset` implementation, which provides pose-to-image generation capabilities for fashion images using human keypoint detection. The dataset processes pose keypoint data and transforms it into multi-channel pose representations for training and inference with the CoCosNet framework.

For general dataset architecture information, see [Dataset Architecture](#3.1). For other dataset implementations, see [Dataset Implementations](#3.2).

## Purpose and Scope

The `DeepFashionDataset` class enables pose-conditioned image synthesis by:
- Loading fashion images with corresponding human pose keypoint data
- Converting pose annotations into multi-channel tensor representations
- Applying distance transforms to joint and limb information
- Managing reference image selection for exemplar-based generation
- Supporting both training and test phases with appropriate data splits

## Class Architecture

```mermaid
graph TD
    BaseDataset["BaseDataset"] --> Pix2pixDataset["Pix2pixDataset"]
    Pix2pixDataset --> DeepFashionDataset["DeepFashionDataset"]
    
    DeepFashionDataset --> modify_commandline_options["modify_commandline_options()"]
    DeepFashionDataset --> get_paths["get_paths()"]
    DeepFashionDataset --> get_ref["get_ref()"]
    DeepFashionDataset --> get_label_tensor["get_label_tensor()"]
    
    get_ref --> get_ref_video_like["get_ref_video_like()"]
    get_ref --> get_ref_vgg["get_ref_vgg()"]
    
    get_label_tensor --> pose_rendering["Pose Rendering Pipeline"]
    get_label_tensor --> distance_transforms["Distance Transform Computation"]
```

Sources: [data/deepfashion_dataset.py:15-178]()

## Configuration Parameters

The dataset configures specific parameters optimized for fashion image generation:

| Parameter | Training Value | Test Value | Purpose |
|-----------|---------------|------------|---------|
| `preprocess_mode` | resize_and_crop | resize_and_crop | Image preprocessing method |
| `load_size` | 286 | 256 | Initial image size before cropping |
| `crop_size` | 256 | 256 | Final image size after cropping |
| `label_nc` | 20 | 20 | Number of label channels (pose + distance maps) |
| `no_pairing_check` | True | True | Disable strict image-label pairing validation |

The configuration is handled by the `modify_commandline_options` static method which inherits from `Pix2pixDataset` and applies fashion-specific overrides.

Sources: [data/deepfashion_dataset.py:16-31]()

## Data Loading Pipeline

```mermaid
graph TB
    subgraph "File System Structure"
        train_txt["train.txt / val.txt"]
        image_paths["img/WOMEN/Category/id_XXXXX/*.jpg"]
        pose_paths["pose/WOMEN/Category/id_XXXXX/*_{candidate,subset}.txt"]
    end
    
    subgraph "Path Resolution"
        get_paths["get_paths()"]
        path_conversion["Image → Pose Path Conversion"]
        imgpath_to_labelpath["imgpath_to_labelpath()"]
        labelpath_to_imgpath["labelpath_to_imgpath()"]
    end
    
    subgraph "Reference Management"
        ref_files["deepfashion_ref.txt / deepfashion_ref_test.txt"]
        self_pair["deepfashion_self_pair.txt"]
        get_ref_video_like["get_ref_video_like()"]
        get_ref_vgg["get_ref_vgg()"]
    end
    
    train_txt --> get_paths
    get_paths --> image_paths
    get_paths --> pose_paths
    
    path_conversion --> imgpath_to_labelpath
    path_conversion --> labelpath_to_imgpath
    
    ref_files --> get_ref_vgg
    self_pair --> get_ref_video_like
```

Sources: [data/deepfashion_dataset.py:33-52](), [data/deepfashion_dataset.py:171-177]()

## Pose Processing Architecture

The core functionality converts human pose keypoint data into multi-channel tensor representations:

```mermaid
graph TB
    subgraph "Input Data"
        candidate_txt["candidate.txt<br/>Keypoint coordinates"]
        subset_txt["subset.txt<br/>Limb connectivity"]
    end
    
    subgraph "Pose Rendering"
        limbSeq["limbSeq[19]<br/>Joint connectivity pairs"]
        joint_circles["Joint Circle Rendering<br/>cv2.circle()"]
        limb_polygons["Limb Polygon Rendering<br/>cv2.ellipse2Poly()"]
        canvas_composition["Canvas Composition<br/>cv2.addWeighted()"]
    end
    
    subgraph "Distance Transform Pipeline"
        individual_joints["Individual Joint Masks"]
        distance_maps["cv2.distanceTransform()<br/>DIST_L1, kernel=3"]
        tensor_conversion["Transform to Tensors"]
    end
    
    subgraph "Output Tensor"
        pose_tensor["pose_tensor[3]<br/>RGB pose visualization"]
        dist_tensors["dist_tensors[17]<br/>Distance maps per joint"]
        final_tensor["label_tensor[20]<br/>Concatenated output"]
    end
    
    candidate_txt --> joint_circles
    subset_txt --> limb_polygons
    limbSeq --> limb_polygons
    
    joint_circles --> canvas_composition
    limb_polygons --> canvas_composition
    canvas_composition --> pose_tensor
    
    limb_polygons --> individual_joints
    individual_joints --> distance_maps
    distance_maps --> tensor_conversion
    tensor_conversion --> dist_tensors
    
    pose_tensor --> final_tensor
    dist_tensors --> final_tensor
```

Sources: [data/deepfashion_dataset.py:111-169]()

## Reference Image Selection

The dataset supports two modes for reference image selection during training and inference:

### VGG Mode (Default)
- Uses pre-computed reference pairs from `deepfashion_ref.txt` files
- Training: Combines specified reference with random image selection
- Testing: Uses only pre-specified reference images

### Video-Like Mode
- Leverages `deepfashion_self_pair.txt` for self-paired images
- Incorporates additional random sampling for augmented reference sets
- Provides multiple reference candidates per target image

```mermaid
graph LR
    subgraph "Reference Selection Strategy"
        opt_video_like{"`opt.video_like`"}
        get_ref_vgg["get_ref_vgg()<br/>Fixed reference pairs"]
        get_ref_video_like["get_ref_video_like()<br/>Self-pairs + random"]
        
        opt_video_like -->|False| get_ref_vgg
        opt_video_like -->|True| get_ref_video_like
    end
    
    subgraph "Reference Files"
        ref_txt["deepfashion_ref.txt<br/>deepfashion_ref_test.txt"]
        self_pair_txt["deepfashion_self_pair.txt"]
        
        ref_txt --> get_ref_vgg
        self_pair_txt --> get_ref_video_like
    end
    
    subgraph "Output Format"
        ref_dict["ref_dict<br/>target_path → [ref_paths...]"]
    end
    
    get_ref_vgg --> ref_dict
    get_ref_video_like --> ref_dict
```

Sources: [data/deepfashion_dataset.py:54-102]()

## Pose Keypoint Schema

The dataset processes 18 keypoints using the following limb sequence definition:

| Limb Index | Connection | Body Part |
|------------|-----------|-----------|
| 0-6 | Upper body | Head, shoulders, arms |
| 7-11 | Torso | Spine, hips |
| 12-18 | Lower body | Legs, feet |

The `limbSeq` array defines 19 connections between keypoints, creating a skeletal representation that is rendered as colored polygons and converted to distance transforms for neural network processing.

Sources: [data/deepfashion_dataset.py:115-117]()

## Distance Transform Processing

Each limb segment generates an individual distance map using OpenCV's `cv2.distanceTransform` with L1 distance metric. The distance values are normalized and clipped to create smooth gradients around pose structures, providing the network with spatial relationship information between pose elements and image regions.

The final output tensor contains 20 channels:
- 3 channels: RGB pose visualization
- 17 channels: Distance maps for each limb segment

Sources: [data/deepfashion_dataset.py:158-169]()

---

