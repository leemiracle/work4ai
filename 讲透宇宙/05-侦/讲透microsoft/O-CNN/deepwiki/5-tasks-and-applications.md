<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/O-CNN · page 5 Tasks and Applications · fetched 2026-10-26 -->

# Tasks and Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/classification.md](docs/classification.md)
- [docs/completion.md](docs/completion.md)
- [docs/segmentation.md](docs/segmentation.md)
- [docs/unsupervised.md](docs/unsupervised.md)
- [tensorflow/data/cls_modelnet.py](tensorflow/data/cls_modelnet.py)
- [tensorflow/data/seg_shapenet.py](tensorflow/data/seg_shapenet.py)
- [tensorflow/script/configs/cls_hrnet.yaml](tensorflow/script/configs/cls_hrnet.yaml)
- [tensorflow/script/feature.py](tensorflow/script/feature.py)
- [tensorflow/script/run_cls_cmd.py](tensorflow/script/run_cls_cmd.py)
- [tensorflow/script/run_cls_finetune.py](tensorflow/script/run_cls_finetune.py)
- [tensorflow/script/run_linear_cls.py](tensorflow/script/run_linear_cls.py)
- [tensorflow/script/run_linear_cls_cmd.py](tensorflow/script/run_linear_cls_cmd.py)

</details>



This document provides an overview of the main 3D learning tasks and applications supported by the O-CNN framework. It covers the specific implementations, datasets, and code components for each task type, along with their relationships to the underlying octree-based CNN architecture.

For detailed information about the core octree data structures and neural operations that enable these tasks, see [Core Architecture](#3). For framework-specific implementation details, see [Framework Integration](#4). For data preprocessing pipelines, see [Data Processing Pipeline](#6).

## Supported Task Categories

The O-CNN framework supports several categories of 3D learning tasks, each with multiple dataset implementations and framework variations. The tasks are designed to leverage the hierarchical nature of octree representations for efficient 3D processing.

```mermaid
graph TB
    subgraph "Classification Tasks"
        CLS_M40["ModelNet40 Classification<br/>40 object categories"]
        CLS_RETRIEVAL["Shape Retrieval<br/>Feature-based matching"]
    end
    
    subgraph "Segmentation Tasks"
        SEG_SHAPENET["ShapeNet Part Segmentation<br/>16 categories, part-level"]
        SEG_PARTNET["PartNet Segmentation<br/>Fine-grained parts"]
        SEG_SCANNET["ScanNet Scene Segmentation<br/>Indoor scene understanding"]
    end
    
    subgraph "Generation Tasks"
        GEN_COMPLETION["Shape Completion<br/>Incomplete → Complete"]
        GEN_AE["Autoencoder<br/>Compression & Reconstruction"]
        GEN_IMG2SHAPE["Image2Shape<br/>2D → 3D Generation"]
    end
    
    subgraph "Unsupervised Learning"
        UNSUP_PRETRAIN["Multiresolution Instance Discrimination<br/>Self-supervised pretraining"]
        UNSUP_FINETUNE["Transfer Learning<br/>Pretrained → Task-specific"]
    end
    
    CLS_M40 --> UNSUP_FINETUNE
    SEG_SHAPENET --> UNSUP_FINETUNE
    SEG_PARTNET --> UNSUP_FINETUNE
    UNSUP_PRETRAIN --> UNSUP_FINETUNE
```

**Sources:** [README.md:34-44](), [docs/classification.md:1-10](), [docs/segmentation.md:1-10](), [docs/completion.md:1-10](), [docs/unsupervised.md:1-10]()

## Classification Implementation Pipeline

The classification tasks demonstrate the basic O-CNN workflow from mesh input to trained models. The implementation spans multiple frameworks with shared data preprocessing.

```mermaid
graph LR
    subgraph "Data Sources"
        M40_MESH["ModelNet40 Meshes<br/>.off files"]
        M40_POINTS["Point Clouds<br/>.points files"]
    end
    
    subgraph "Preprocessing Tools"
        VIRTUAL_SCANNER["virtual_scanner<br/>Mesh → Points"]
        SIMPLIFY_POINTS["simplify_points<br/>Density reduction"]
        OCTREE_GEN["octree<br/>Points → Octree"]
    end
    
    subgraph "Data Conversion Scripts"
        CLS_MODELNET["cls_modelnet.py<br/>ModelNet40 pipeline"]
        CONVERT_TF["convert_tfrecords.py<br/>TensorFlow format"]
        CONVERT_CAFFE["convert_octree_data<br/>Caffe LMDB format"]
    end
    
    subgraph "Training Frameworks"
        CAFFE_CLS["Caffe<br/>ocnn_m40_5.prototxt"]
        TF_CLS["TensorFlow<br/>run_cls.py + cls_hrnet.yaml"]
        PYTORCH_CLS["PyTorch<br/>classification.py"]
    end
    
    M40_MESH --> VIRTUAL_SCANNER
    VIRTUAL_SCANNER --> M40_POINTS
    M40_POINTS --> SIMPLIFY_POINTS
    SIMPLIFY_POINTS --> OCTREE_GEN
    
    OCTREE_GEN --> CLS_MODELNET
    CLS_MODELNET --> CONVERT_TF
    CLS_MODELNET --> CONVERT_CAFFE
    
    CONVERT_TF --> TF_CLS
    CONVERT_CAFFE --> CAFFE_CLS
    M40_POINTS --> PYTORCH_CLS
```

**Sources:** [tensorflow/data/cls_modelnet.py:36-49](), [docs/classification.md:7-56](), [docs/classification.md:76-139](), [docs/classification.md:156-207]()

### ModelNet40 Classification Implementation

The ModelNet40 classification task is implemented across all three frameworks with consistent preprocessing but different network architectures:

| Framework | Network Architecture | Configuration File | Accuracy |
|-----------|---------------------|-------------------|----------|
| Caffe | O-CNN (LeNet-style) | `ocnn_m40_5_solver.prototxt` | 89.6% |
| TensorFlow | HRNet | `cls_hrnet.yaml` | 92.4% |
| PyTorch | ResNet | `cls_m40.yaml` | Various |

The TensorFlow implementation in [tensorflow/script/configs/cls_hrnet.yaml:1-55]() shows the configuration for the HRNet-based classifier, including data augmentation parameters and training hyperparameters.

**Sources:** [docs/classification.md:47-55](), [docs/classification.md:115-138](), [docs/classification.md:193-206](), [tensorflow/script/configs/cls_hrnet.yaml:1-55]()

## Segmentation Task Implementations

Segmentation tasks require more complex architectures and dataset handling due to the need for dense prediction at the point level.

```mermaid
graph TB
    subgraph "ShapeNet Part Segmentation"
        SN_DOWNLOAD["seg_shapenet.py<br/>download_and_unzip()"]
        SN_CONVERT["txt_to_ply()<br/>Format conversion"]
        SN_POINTS["ply_to_points()<br/>Point extraction"]
        SN_TFRECORDS["points_to_tfrecords()<br/>Database creation"]
        SN_TRAIN["run_seg_shapenet_cmd.py<br/>HRNet training"]
    end
    
    subgraph "PartNet Fine-grained Segmentation"
        PN_DATA["seg_partnet.py<br/>Data preprocessing"]
        PN_TRAIN["run_seg_partnet_cmd.py<br/>Multi-category training"]
        PN_RESULTS["IoU: 58.4<br/>vs PointNet: 35.6"]
    end
    
    subgraph "ScanNet Scene Segmentation"
        SC_SCENES["scannet.py<br/>Indoor scene data"]
        SC_UNET["UNet Architecture<br/>Scene understanding"]
        SC_BENCHMARK["ScanNet Benchmark<br/>76.2 mIoU"]
    end
    
    SN_DOWNLOAD --> SN_CONVERT
    SN_CONVERT --> SN_POINTS
    SN_POINTS --> SN_TFRECORDS
    SN_TFRECORDS --> SN_TRAIN
    
    PN_DATA --> PN_TRAIN
    PN_TRAIN --> PN_RESULTS
```

**Sources:** [tensorflow/data/seg_shapenet.py:27-134](), [docs/segmentation.md:48-79](), [docs/segmentation.md:82-98](), [README.md:50-54]()

### PartNet Segmentation Pipeline

The PartNet segmentation implementation demonstrates fine-grained part segmentation with significant performance improvements over existing methods. The preprocessing pipeline in [tensorflow/data/seg_shapenet.py:87-129]() handles the conversion from the original annotation format to TensorFlow records.

The segmentation results show substantial improvements:
- **O-CNN (HRNet)**: 58.4 IoU
- **PointNet**: 35.6 IoU  
- **PointNet++**: 42.5 IoU
- **SpiderCNN**: 37.0 IoU
- **PointCNN**: 46.5 IoU

**Sources:** [docs/segmentation.md:48-79](), [tensorflow/data/seg_shapenet.py:87-129](), [README.md:66-69]()

## Unsupervised Learning and Transfer

The unsupervised learning framework enables pretraining on large unlabeled datasets and transfer to downstream tasks.

```mermaid
graph TB
    subgraph "Pretraining Phase"
        SHAPENET_DATA["ShapeNetCore.v1<br/>Large-scale 3D shapes"]
        MIDNET_PREPROCESS["midnet_data.py<br/>shapenet_create_tfrecords"]
        MID_HRNET["run_mid.py<br/>mid_hrnet_d6.yaml"]
        PRETRAINED_WEIGHTS["Pretrained Checkpoint<br/>iter_800000.ckpt"]
    end
    
    subgraph "Feature Extraction"
        FEATURE_EXTRACTOR["feature.py<br/>cls_features() / seg_features()"]
        FC1_FEATURES["fc1 features<br/>Classification backbone"]
        FC2_FEATURES["fc2 features<br/>L2-normalized embeddings"]
        SEG_FEATURES["Segmentation features<br/>Dense predictions"]
    end
    
    subgraph "Transfer Learning"
        FINETUNE_CLS["run_cls_cmd.py<br/>--mode finetune"]
        LINEAR_CLS["run_linear_cls_cmd.py<br/>Fixed backbone"]
        FINETUNE_SEG["run_seg_shapenet_cmd.py<br/>--mode finetune"]
    end
    
    SHAPENET_DATA --> MIDNET_PREPROCESS
    MIDNET_PREPROCESS --> MID_HRNET
    MID_HRNET --> PRETRAINED_WEIGHTS
    
    PRETRAINED_WEIGHTS --> FEATURE_EXTRACTOR
    FEATURE_EXTRACTOR --> FC1_FEATURES
    FEATURE_EXTRACTOR --> FC2_FEATURES
    FEATURE_EXTRACTOR --> SEG_FEATURES
    
    PRETRAINED_WEIGHTS --> FINETUNE_CLS
    PRETRAINED_WEIGHTS --> LINEAR_CLS
    PRETRAINED_WEIGHTS --> FINETUNE_SEG
```

**Sources:** [docs/unsupervised.md:3-24](), [tensorflow/script/feature.py:52-86](), [tensorflow/script/run_linear_cls_cmd.py:1-121](), [tensorflow/script/run_cls_cmd.py:1-54]()

### Linear Classification Protocol

The linear classification protocol in [tensorflow/script/run_linear_cls_cmd.py:33-119]() implements the standard evaluation for unsupervised representations. It extracts features using [tensorflow/script/feature.py:52-62]() and trains only a linear classifier on top of frozen backbone features.

The training pipeline supports different data ratios for few-shot learning experiments:

| Data Ratio | Training Samples | Learning Rate Multiplier |
|------------|------------------|-------------------------|
| 1% | 116 | 4x |
| 2% | 214 | 4x |
| 5% | 511 | 2x |
| 10% | 1000 | 2x |
| 20% | 1980 | 1x |
| 50% | 4931 | 1x |
| 100% | 9842 | 1x |

**Sources:** [tensorflow/script/run_linear_cls_cmd.py:23-26](), [tensorflow/script/feature.py:52-62]()

## Shape Completion and Generation

Shape completion tasks focus on reconstructing complete 3D shapes from partial or noisy input using encoder-decoder architectures with skip connections.

```mermaid
graph LR
    subgraph "Input Data"
        PARTIAL_SCANS["Partial Scans<br/>12k test samples"]
        NOISY_INPUT["Noisy Point Clouds<br/>Incomplete geometry"]
    end
    
    subgraph "Completion Pipeline"
        COMPLETION_DATA["completion.py<br/>generate_dataset()"]
        UNET_SKIP["U-Net + Skip Connections<br/>Output-guided refinement"]
        PURE_AE["Pure Autoencoder<br/>No skip connections"]
    end
    
    subgraph "Training Configs"
        TRAIN_CONFIG["completion_train.yaml<br/>Training parameters"]
        TEST_CONFIG["completion_test.yaml<br/>Evaluation setup"]
    end
    
    subgraph "Output Formats"
        OCTREE_OUT["Octree Results<br/>.octree format"]
        POINTS_OUT["Point Clouds<br/>.points/.ply format"]
    end
    
    PARTIAL_SCANS --> COMPLETION_DATA
    NOISY_INPUT --> COMPLETION_DATA
    
    COMPLETION_DATA --> UNET_SKIP
    COMPLETION_DATA --> PURE_AE
    
    TRAIN_CONFIG --> UNET_SKIP
    TEST_CONFIG --> UNET_SKIP
    
    UNET_SKIP --> OCTREE_OUT
    PURE_AE --> OCTREE_OUT
    
    OCTREE_OUT --> POINTS_OUT
```

**Sources:** [docs/completion.md:10-61]()

The completion framework implements output-guided skip connections as described in the CVPR 2020 workshop paper. The architecture can be configured with or without skip connections using the `MODEL.skip_connections` parameter in the training configuration.

**Sources:** [docs/completion.md:20-31]()

## Task Performance Summary

The following table summarizes the performance achievements across different tasks and datasets:

| Task | Dataset | Architecture | Performance Metric | Score |
|------|---------|--------------|-------------------|-------|
| Classification | ModelNet40 | O-CNN (Caffe) | Accuracy | 89.6% |
| Classification | ModelNet40 | HRNet (TensorFlow) | Accuracy | 92.4% |
| Part Segmentation | ShapeNet | HRNet | mIoU | Various |
| Part Segmentation | PartNet | HRNet | mIoU | 58.4% |
| Scene Segmentation | ScanNet | UNet | mIoU | 76.2% |
| Shape Completion | Custom Dataset | UNet + Skip | Visual Quality | SOTA |

The unsupervised pretraining provides consistent improvements across downstream tasks, with the PartNet segmentation showing a +2.4 mIoU improvement (58.4 → 60.8) when using pretrained weights compared to random initialization.

**Sources:** [README.md:50-73](), [docs/classification.md:51](), [docs/classification.md:134-135](), [docs/segmentation.md:52-55](), [docs/unsupervised.md:80-82]()

---

