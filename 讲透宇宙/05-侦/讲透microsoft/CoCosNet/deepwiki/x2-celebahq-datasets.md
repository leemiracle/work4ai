<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CoCosNet · extra page CelebAHQ Datasets · fetched 2026-10-26 -->

# CelebAHQ Datasets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/celebahq_dataset.py](data/celebahq_dataset.py)
- [data/celebahq_ref_test.txt](data/celebahq_ref_test.txt)
- [data/celebahqedge_dataset.py](data/celebahqedge_dataset.py)

</details>



This document covers the CelebAHQ dataset implementations in the CoCosNet framework, which provide face generation capabilities through both mask-to-face and edge-to-face translation. The CelebAHQ datasets support facial part segmentation with detailed semantic labels for high-quality face synthesis.

For information about the overall dataset architecture and factory pattern, see [Dataset Architecture](#3.1). For other dataset implementations, see [Dataset Implementations](#3.2).

## Dataset Implementations Overview

The CelebAHQ datasets consist of two main implementations that extend the base `Pix2pixDataset` class:

```mermaid
graph TB
    subgraph "CelebAHQ Dataset Hierarchy"
        Pix2pixDataset["Pix2pixDataset<br/>Base Implementation"]
        CelebAHQDataset["CelebAHQDataset<br/>Mask-to-Face Translation"]
        CelebAHQEdgeDataset["CelebAHQEdgeDataset<br/>Edge-to-Face Translation"]
    end
    
    subgraph "Data Processing Pipeline"
        ImageInput["Face Images<br/>CelebA-HQ-img/*.jpg"]
        MaskInput["Facial Masks<br/>CelebAMask-HQ-mask-anno"]
        GlassesMask["Glasses Masks<br/>*_eye_g.png"]
        EdgeProcessing["Edge Detection<br/>Canny + Facial Parts"]
        DistanceTransform["Distance Transform<br/>cv2.distanceTransform"]
    end
    
    subgraph "Output Configurations"
        MaskOutput["19 Label Channels<br/>Including Glasses"]
        EdgeOutput["15 Label Channels<br/>Edge + Distance Maps"]
    end
    
    Pix2pixDataset --> CelebAHQDataset
    Pix2pixDataset --> CelebAHQEdgeDataset
    
    ImageInput --> CelebAHQDataset
    MaskInput --> CelebAHQDataset
    GlassesMask --> CelebAHQDataset
    
    ImageInput --> CelebAHQEdgeDataset
    MaskInput --> EdgeProcessing
    EdgeProcessing --> DistanceTransform
    DistanceTransform --> CelebAHQEdgeDataset
    
    CelebAHQDataset --> MaskOutput
    CelebAHQEdgeDataset --> EdgeOutput
```

Sources: [data/celebahq_dataset.py:1-90](), [data/celebahqedge_dataset.py:1-142]()

## CelebAHQDataset Implementation

The `CelebAHQDataset` class implements mask-to-face translation with detailed facial part segmentation. It processes 19 semantic label channels including facial features and accessories.

### Facial Part Labels

The dataset handles the following facial parts as documented in the code:

| Category | Parts |
|----------|-------|
| Facial Features | `hair`, `skin`, `l_brow`, `r_brow`, `l_eye`, `r_eye`, `nose`, `u_lip`, `mouth`, `l_lip` |
| Accessories | `l_ear`, `r_ear`, `neck`, `cloth`, `hat`, `eye_g` (glasses), `ear_r`, `neck_l` |

### Configuration Parameters

The dataset configures specific parameters for CelebAHQ processing:

| Parameter | Training Value | Test Value | Purpose |
|-----------|---------------|------------|---------|
| `load_size` | 286 | 256 | Image loading dimension |
| `crop_size` | 256 | 256 | Final crop dimension |
| `label_nc` | 19 | 19 | Number of label channels |
| `preprocess_mode` | `resize_and_crop` | `resize_and_crop` | Preprocessing strategy |

Sources: [data/celebahq_dataset.py:15-29]()

### Label Processing Pipeline

```mermaid
graph LR
    subgraph "Label Tensor Construction"
        BaseLabel["Base Facial Parts<br/>all_parts_except_glasses/*.png"]
        GlassesLabel["Glasses Mask<br/>*_eye_g.png"]
        Transform["Image Transform<br/>get_transform()"]
        Combine["torch.cat()<br/>Concatenate Channels"]
    end
    
    subgraph "Path Resolution"
        ImagePath["Image Path<br/>CelebA-HQ-img/*.jpg"]
        LabelPath["Label Path<br/>all_parts_except_glasses/*.png"]
        GlassesPath["Glasses Path<br/>*/idx_eye_g.png"]
    end
    
    ImagePath --> LabelPath
    BaseLabel --> Transform
    GlassesLabel --> Transform
    Transform --> Combine
    LabelPath --> BaseLabel
    LabelPath --> GlassesPath
    GlassesPath --> GlassesLabel
```

The `get_label_tensor` method combines base facial parts with glasses masks:

Sources: [data/celebahq_dataset.py:67-84]()

## CelebAHQEdgeDataset Implementation

The `CelebAHQEdgeDataset` class implements edge-to-face translation using edge detection and distance transforms. It processes 15 label channels focused on edge maps and distance-based features.

### Edge Processing Components

```mermaid
graph TB
    subgraph "Edge Detection Pipeline"
        FacialParts["Inner Facial Parts<br/>skin, brow, eye, ear, nose, lip, hair"]
        EdgeDetection["get_edges()<br/>Boundary Detection"]
        DistanceTransform["cv2.distanceTransform<br/>Distance Maps"]
        CannyEdge["Canny Edge Detection<br/>Background Edges"]
    end
    
    subgraph "Label Channel Assembly"
        AllEdges["Combined Edges<br/>tensor_edges_all"]
        DistanceMaps["Distance Maps<br/>tensors_dist (13 channels)"]
        FacialEdges["Facial Edges Only<br/>tensor_edges"]
        FinalTensor["Final Label Tensor<br/>15 channels total"]
    end
    
    FacialParts --> EdgeDetection
    EdgeDetection --> DistanceTransform
    EdgeDetection --> CannyEdge
    
    EdgeDetection --> AllEdges
    DistanceTransform --> DistanceMaps
    EdgeDetection --> FacialEdges
    
    AllEdges --> FinalTensor
    DistanceMaps --> FinalTensor
    FacialEdges --> FinalTensor
```

Sources: [data/celebahqedge_dataset.py:69-116]()

### Inner Facial Parts Processing

The edge dataset focuses on 13 specific inner facial parts:

```python
inner_parts = ['skin', 'l_brow', 'r_brow', 'l_eye', 'r_eye', 'l_ear', 'r_ear', 
               'nose', 'u_lip', 'mouth', 'l_lip', 'eye_g', 'hair']
```

Each part undergoes edge detection and distance transform processing to create feature-rich edge representations.

Sources: [data/celebahqedge_dataset.py:77-103]()

## Data Organization and File Structure

### Directory Structure

```mermaid
graph TD
    subgraph "CelebAHQ Data Organization"
        DataRoot["dataroot/"]
        TrainTxt["train.txt<br/>Training file list"]
        ValTxt["val.txt<br/>Validation file list"]
        
        ImageDir["CelebA-HQ-img/<br/>Face images"]
        MaskDir["CelebAMask-HQ-mask-anno/<br/>Segmentation masks"]
        
        AllParts["all_parts_except_glasses/<br/>Base facial parts"]
        Subfolders["Subfolders 0/, 1/, 2/, ...<br/>Organized by image ID"]
        
        PartMasks["Individual part masks<br/>*_skin.png, *_hair.png, etc."]
        GlassesMasks["Glasses masks<br/>*_eye_g.png"]
    end
    
    DataRoot --> TrainTxt
    DataRoot --> ValTxt
    DataRoot --> ImageDir
    DataRoot --> MaskDir
    
    MaskDir --> AllParts
    MaskDir --> Subfolders
    
    Subfolders --> PartMasks
    Subfolders --> GlassesMasks
```

### Path Resolution Methods

Both dataset classes implement path conversion methods:

| Method | Purpose | Source Dataset |
|--------|---------|----------------|
| `imgpath_to_labelpath` | Convert image path to label path | Both |
| `labelpath_to_imgpath` | Convert label path to image path | Edge dataset only |

The path resolution handles the subfolder organization where images are grouped by ID ranges (every 2000 images).

Sources: [data/celebahq_dataset.py:86-89](), [data/celebahqedge_dataset.py:118-128]()

## Reference System

### Reference File Structure

The datasets use reference files to define training and test pairs:

```mermaid
graph LR
    subgraph "Reference File System"
        RefTrain["celebahq_ref.txt<br/>Training References"]
        RefTest["celebahq_ref_test.txt<br/>Test References"]
        
        TrainPairs["Training: [source, target1, target2]<br/>Multiple references"]
        TestPairs["Test: [source, target]<br/>Single reference"]
    end
    
    RefTrain --> TrainPairs
    RefTest --> TestPairs
```

### Reference Data Format

The reference system provides correspondence between source and target images:

- **Training**: Each source image maps to first and last reference targets
- **Testing**: Each source image maps to one or more reference targets

Example from test reference file:
```
29922.jpg,26768.jpg
29883.jpg,5487.jpg
26969.jpg,6897.jpg
```

Sources: [data/celebahq_dataset.py:49-66](), [data/celebahqedge_dataset.py:51-67](), [data/celebahq_ref_test.txt:1-8]()

---

