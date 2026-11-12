<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/vision · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [docs/source/datasets.rst](docs/source/datasets.rst)
- [docs/source/io.rst](docs/source/io.rst)
- [docs/source/models.rst](docs/source/models.rst)
- [hubconf.py](hubconf.py)
- [references/classification/README.md](references/classification/README.md)
- [setup.py](setup.py)
- [test/assets/fakedata/draw_rotated_boxes.png](test/assets/fakedata/draw_rotated_boxes.png)
- [test/common_extended_utils.py](test/common_extended_utils.py)
- [test/common_utils.py](test/common_utils.py)
- [test/datasets_utils.py](test/datasets_utils.py)
- [test/expect/ModelTester.test_vit_h_14_expect.pkl](test/expect/ModelTester.test_vit_h_14_expect.pkl)
- [test/test_datasets.py](test/test_datasets.py)
- [test/test_extended_models.py](test/test_extended_models.py)
- [test/test_functional_tensor.py](test/test_functional_tensor.py)
- [test/test_image.py](test/test_image.py)
- [test/test_models.py](test/test_models.py)
- [test/test_transforms.py](test/test_transforms.py)
- [test/test_transforms_tensor.py](test/test_transforms_tensor.py)
- [test/test_transforms_v2.py](test/test_transforms_v2.py)
- [test/test_transforms_v2_utils.py](test/test_transforms_v2_utils.py)
- [test/test_tv_tensors.py](test/test_tv_tensors.py)
- [torchvision/csrc/io/image/cpu/decode_image.cpp](torchvision/csrc/io/image/cpu/decode_image.cpp)
- [torchvision/csrc/io/image/image.cpp](torchvision/csrc/io/image/image.cpp)
- [torchvision/csrc/io/image/image.h](torchvision/csrc/io/image/image.h)
- [torchvision/datasets/__init__.py](torchvision/datasets/__init__.py)
- [torchvision/datasets/_optical_flow.py](torchvision/datasets/_optical_flow.py)
- [torchvision/datasets/_stereo_matching.py](torchvision/datasets/_stereo_matching.py)
- [torchvision/datasets/inaturalist.py](torchvision/datasets/inaturalist.py)
- [torchvision/datasets/places365.py](torchvision/datasets/places365.py)
- [torchvision/io/__init__.py](torchvision/io/__init__.py)
- [torchvision/io/image.py](torchvision/io/image.py)
- [torchvision/models/__init__.py](torchvision/models/__init__.py)
- [torchvision/models/_api.py](torchvision/models/_api.py)
- [torchvision/ops/_box_convert.py](torchvision/ops/_box_convert.py)
- [torchvision/transforms/autoaugment.py](torchvision/transforms/autoaugment.py)
- [torchvision/transforms/functional.py](torchvision/transforms/functional.py)
- [torchvision/transforms/transforms.py](torchvision/transforms/transforms.py)
- [torchvision/transforms/v2/_geometry.py](torchvision/transforms/v2/_geometry.py)
- [torchvision/transforms/v2/functional/_geometry.py](torchvision/transforms/v2/functional/_geometry.py)
- [torchvision/transforms/v2/functional/_meta.py](torchvision/transforms/v2/functional/_meta.py)
- [torchvision/transforms/v2/functional/_utils.py](torchvision/transforms/v2/functional/_utils.py)
- [torchvision/tv_tensors/__init__.py](torchvision/tv_tensors/__init__.py)
- [torchvision/tv_tensors/_bounding_boxes.py](torchvision/tv_tensors/_bounding_boxes.py)

</details>



TorchVision is a computer vision library for PyTorch that provides fundamental building blocks for image and video processing tasks. This document covers the library's architecture, major components, and how they integrate to support computer vision workflows.

**Scope**: This page introduces TorchVision's overall structure and component interactions. For detailed information on specific subsystems, see:
- Image and video transformations: [Transforms](#2)
- Pre-trained neural network architectures: [Models](#3)
- Dataset loaders and utilities: [Datasets](#4)
- Image/video reading and writing: [I/O Operations](#5)
- Computer vision operators: [Operators](#6)

## Purpose and Design

TorchVision provides three primary capabilities:

1. **Data Processing**: Transform and augment images/videos for training and inference
2. **Pre-trained Models**: Access to state-of-the-art architectures with standardized weight management
3. **Dataset Integration**: Loaders for standard computer vision datasets with built-in downloading and preprocessing

The library is designed around PyTorch's tensor operations and integrates seamlessly with `torch.utils.data.DataLoader` for efficient data loading pipelines.

Sources: [torchvision/transforms/transforms.py:1-57](), [torchvision/models/__init__.py:1-14](), [torchvision/datasets/__init__.py:1-148]()

## Core Architecture

```mermaid
graph TB
    subgraph "Public API Modules"
        TRANSFORMS["torchvision.transforms<br/>transforms.py<br/>Class-based transforms"]
        TRANSFORMS_V2["torchvision.transforms.v2<br/>Type-aware transforms<br/>tv_tensors integration"]
        MODELS["torchvision.models<br/>Pre-trained architectures<br/>Weight management"]
        DATASETS["torchvision.datasets<br/>Dataset loaders<br/>VisionDataset base"]
        IO["torchvision.io<br/>image.py, video.py<br/>Encode/decode operations"]
        OPS["torchvision.ops<br/>Detection operators<br/>RoI pooling, NMS"]
        UTILS["torchvision.utils<br/>Visualization helpers<br/>make_grid, draw_*"]
    end
    
    subgraph "Supporting Infrastructure"
        TV_TENSORS["torchvision.tv_tensors<br/>_bounding_boxes.py<br/>Metadata-rich tensors"]
        CPP_EXT["C++/CUDA Extensions<br/>torchvision/csrc/<br/>Performance-critical ops"]
        PROTOTYPE["torchvision.prototype<br/>Experimental features"]
    end
    
    TRANSFORMS_V2 --> TV_TENSORS
    TRANSFORMS_V2 -.replaces.-> TRANSFORMS
    MODELS --> OPS
    MODELS --> TRANSFORMS
    DATASETS --> IO
    DATASETS --> TRANSFORMS_V2
    OPS --> CPP_EXT
    IO --> CPP_EXT
    UTILS --> TRANSFORMS
    PROTOTYPE --> TRANSFORMS_V2
```

**Core Architecture Diagram**: Shows the seven main public modules and their relationships. Solid arrows indicate dependencies; dashed arrows indicate evolutionary relationships.

Sources: [torchvision/transforms/transforms.py:1-60](), [torchvision/transforms/v2/__init__.py](), [torchvision/models/__init__.py:1-14](), [torchvision/datasets/__init__.py:1-148](), [torchvision/io/__init__.py:1-58](), [torchvision/ops/__init__.py]()

## Module Overview

### Transform System

The transform system provides data augmentation and preprocessing capabilities through two APIs:

| Component | Module Path | Purpose |
|-----------|-------------|---------|
| **v1 Transforms** | `torchvision.transforms` | Legacy PIL/Tensor transforms with type dispatch |
| **v2 Transforms** | `torchvision.transforms.v2` | Type-aware transforms with kernel registry |
| **Functional API** | `torchvision.transforms.functional` | Stateless transform functions |
| **TV Tensors** | `torchvision.tv_tensors` | Metadata-preserving tensor subclasses |

**Key Classes**:
- `Compose`: Sequential transform application [torchvision/transforms/transforms.py:60-104]()
- `RandomHorizontalFlip`, `Resize`, `Normalize`: Common v1 transforms [torchvision/transforms/transforms.py:697-757]()
- Transform v2 variants with type awareness [torchvision/transforms/v2/_geometry.py]()

Sources: [torchvision/transforms/transforms.py:1-104](), [torchvision/transforms/functional.py:1-51](), [torchvision/tv_tensors/_tv_tensor.py]()

### Models System

Pre-trained model architectures organized by task:

| Task Category | Module | Example Models |
|---------------|--------|----------------|
| Classification | `torchvision.models` | ResNet, VGG, EfficientNet, ViT |
| Detection | `torchvision.models.detection` | Faster R-CNN, RetinaNet, FCOS |
| Segmentation | `torchvision.models.segmentation` | FCN, DeepLabV3, LRASPP |
| Video | `torchvision.models.video` | R3D, MC3, MViT |
| Optical Flow | `torchvision.models.optical_flow` | RAFT |

**Weight Management**: Each model has a `WeightsEnum` class (e.g., `ResNet50_Weights`) containing versioned weight sets with metadata including accuracy metrics, preprocessing transforms, and training details.

Sources: [torchvision/models/__init__.py:1-14](), [torchvision/models/_api.py:1-100](), [hubconf.py:1-50]()

### Datasets System

Built-in dataset loaders with automatic downloading:

```mermaid
graph LR
    VISION["VisionDataset<br/>vision.py<br/>Base class"]
    FOLDER["DatasetFolder<br/>ImageFolder<br/>folder.py"]
    DOWNLOAD["Download Utilities<br/>download_url<br/>extract_archive"]
    
    VISION --> CLASSIFICATION["Classification<br/>MNIST, CIFAR, ImageNet"]
    VISION --> DETECTION["Detection<br/>COCO, VOC, Cityscapes"]
    VISION --> VIDEO["Video<br/>Kinetics, UCF101"]
    VISION --> FLOW["Optical Flow<br/>FlyingChairs, Sintel"]
    
    FOLDER --> VISION
    DOWNLOAD --> VISION
    
    CLASSIFICATION -.uses.-> DOWNLOAD
    DETECTION -.uses.-> DOWNLOAD
```

**Dataset Base Class**: All datasets inherit from `VisionDataset` which provides standard `__getitem__` and `__len__` interfaces compatible with PyTorch's DataLoader.

Sources: [torchvision/datasets/__init__.py:1-148](), [torchvision/datasets/vision.py](), [torchvision/datasets/folder.py]()

### I/O Operations

Efficient image and video encoding/decoding through C++ extensions:

**Image I/O Functions**:
- `read_image(path)`: Read and decode image files [torchvision/io/image.py:52-300]()
- `decode_jpeg(data, mode)`: JPEG decoding with CPU/CUDA support
- `decode_png(data, mode)`: PNG decoding
- `encode_jpeg(input, quality)`: JPEG encoding
- Format auto-detection via `decode_image(data)`

**Video I/O**: Functions for reading/writing video files (deprecated in favor of TorchCodec).

Sources: [torchvision/io/image.py:1-300](), [torchvision/io/__init__.py:1-58](), [torchvision/io/video.py]()

### Operators

Computer vision operations optimized with C++/CUDA:

**Detection Operators**:
- `nms`, `batched_nms`: Non-maximum suppression
- `roi_align`, `roi_pool`: Region of interest pooling
- `MultiScaleRoIAlign`: Multi-scale feature extraction

**Box Operations**:
- `box_iou`, `box_convert`: Bounding box utilities
- `clip_boxes`, `remove_small_boxes`: Box filtering
- `BoxCoder`: Encode/decode box deltas

**Layer Components**:
- `FrozenBatchNorm2d`: Batch normalization with frozen statistics
- `DeformConv2d`: Deformable convolutions
- `SqueezeExcitation`: Channel attention mechanism

Sources: [torchvision/ops/__init__.py](), [torchvision/ops/boxes.py](), [torchvision/ops/roi_align.py]()

## Data Pipeline Flow

```mermaid
graph TB
    SOURCE["Data Source<br/>Files, URLs, Archives"]
    
    DATASET["Dataset Class<br/>VisionDataset subclass<br/>__getitem__ returns sample"]
    
    IO_READ["I/O Layer<br/>read_file()<br/>decode_image()"]
    
    TRANSFORM_V1["transforms.Compose<br/>PIL/Tensor transforms"]
    TRANSFORM_V2["transforms.v2.Compose<br/>Type-aware transforms<br/>tv_tensors support"]
    
    WRAPPER["wrap_dataset_for_transforms_v2<br/>Convert outputs to tv_tensors"]
    
    LOADER["DataLoader<br/>Batching, shuffling<br/>Multiprocessing"]
    
    MODEL["Model Forward Pass<br/>Classification, Detection, etc."]
    
    SOURCE --> DATASET
    DATASET --> IO_READ
    IO_READ --> TRANSFORM_V1
    IO_READ --> WRAPPER
    WRAPPER --> TRANSFORM_V2
    TRANSFORM_V1 --> LOADER
    TRANSFORM_V2 --> LOADER
    LOADER --> MODEL
```

**Typical Usage Pattern**:

1. **Dataset Instantiation**: Create dataset with `root` directory and optional `download=True`
2. **Transform Application**: Apply preprocessing via `transform` parameter
3. **DataLoader Integration**: Wrap in `DataLoader` for batching and parallel loading
4. **Model Inference/Training**: Pass batched data to model

Sources: [torchvision/datasets/vision.py](), [torchvision/tv_tensors/_dataset_wrapper.py](), [test/test_datasets.py:1-50]()

## Build System and Extensions

TorchVision includes C++/CUDA extensions for performance-critical operations:

```mermaid
graph TB
    SETUP["setup.py<br/>Extension builder<br/>Environment variable config"]
    CMAKE["CMakeLists.txt<br/>Alternative build system"]
    
    CSRC["torchvision/csrc/<br/>C++ source code"]
    CUDA_SRC["torchvision/csrc/ops/cuda/<br/>CUDA kernels"]
    CPU_SRC["torchvision/csrc/ops/cpu/<br/>CPU implementations"]
    
    IMAGE_EXT["image extension<br/>JPEG, PNG, WebP codecs<br/>NVJPEG for GPU"]
    OPS_EXT["_C extension<br/>RoI ops, NMS<br/>Deformable conv"]
    VIDEO_EXT["video_reader extension<br/>FFmpeg integration"]
    
    ENV["Environment Variables<br/>USE_CUDA, USE_PNG<br/>USE_JPEG, USE_NVJPEG"]
    
    LIBS["External Libraries<br/>libjpeg, libpng<br/>FFmpeg, CUDA"]
    
    SETUP --> ENV
    CMAKE --> ENV
    ENV --> CSRC
    LIBS --> IMAGE_EXT
    LIBS --> VIDEO_EXT
    
    CSRC --> CPU_SRC
    CSRC --> CUDA_SRC
    
    CPU_SRC --> OPS_EXT
    CUDA_SRC --> OPS_EXT
    CSRC --> IMAGE_EXT
    CSRC --> VIDEO_EXT
```

**Build Configuration**:

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `USE_CUDA` | Auto-detect | Enable CUDA operations |
| `USE_PNG` | `1` | Enable PNG codec support |
| `USE_JPEG` | `1` | Enable JPEG codec support |
| `USE_NVJPEG` | `1` | Enable NVJPEG GPU decoder |
| `FORCE_CUDA` | `0` | Force CUDA build |

**Extension Modules**:
- `torchvision._C`: Core operators (NMS, RoI operations) [setup.py:158-203]()
- `torchvision.image`: Image codecs with optional GPU support [setup.py:288-374]()
- `torchvision.video_reader`: CPU video decoder (FFmpeg-based) [setup.py:436-476]()

Sources: [setup.py:1-550](), [CMakeLists.txt:1-100](), [torchvision/csrc/]()

## Integration with PyTorch Ecosystem

### DataLoader Integration

TorchVision datasets implement `torch.utils.data.Dataset` interface:

```python
# All datasets provide __len__ and __getitem__
dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)
```

Sources: [torchvision/datasets/vision.py](), [test/test_datasets.py:14-30]()

### TorchScript Compatibility

Most transforms and models support TorchScript compilation:

```python
# Transforms can be scripted
scripted_transform = torch.jit.script(transforms.Normalize(mean=[0.5], std=[0.5]))

# Models support scripting and tracing
model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
scripted_model = torch.jit.script(model)
```

Sources: [test/test_models.py:158-190](), [test/test_transforms.py:44-53]()

### ONNX Export Support

Detection models include custom ONNX symbolic functions for export compatibility:

- Custom operators registered via `_register_onnx_ops` mechanism
- Symbolic functions for `nms`, `roi_align`, `roi_pool` operations
- Model-specific export handling in detection module

Sources: [torchvision/onnx/](), test files referencing ONNX export

## File Organization

```mermaid
graph TB
    ROOT["torchvision/"]
    
    TRANSFORMS_PKG["transforms/<br/>transforms.py (v1)<br/>functional.py<br/>_functional_tensor.py<br/>_functional_pil.py"]
    
    TRANSFORMS_V2_PKG["transforms/v2/<br/>Type-aware API<br/>functional/ kernels<br/>_geometry.py<br/>_augment.py"]
    
    MODELS_PKG["models/<br/>Model definitions<br/>_api.py (discovery)<br/>_utils.py (weights)"]
    
    DATASETS_PKG["datasets/<br/>Dataset classes<br/>vision.py (base)<br/>folder.py (generic)"]
    
    IO_PKG["io/<br/>image.py<br/>video.py<br/>_video_opt.py"]
    
    OPS_PKG["ops/<br/>boxes.py<br/>roi_align.py<br/>roi_pool.py"]
    
    TV_TENSORS_PKG["tv_tensors/<br/>_tv_tensor.py (base)<br/>_bounding_boxes.py<br/>_image.py"]
    
    CSRC["csrc/<br/>C++ source code<br/>ops/cpu/<br/>ops/cuda/<br/>io/image/<br/>io/video/"]
    
    ROOT --> TRANSFORMS_PKG
    ROOT --> TRANSFORMS_V2_PKG
    ROOT --> MODELS_PKG
    ROOT --> DATASETS_PKG
    ROOT --> IO_PKG
    ROOT --> OPS_PKG
    ROOT --> TV_TENSORS_PKG
    ROOT --> CSRC
```

**Key Implementation Files**:

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `transforms/transforms.py` | v1 transform classes | ~1500 |
| `transforms/functional.py` | Transform functional API | ~1200 |
| `transforms/v2/functional/_geometry.py` | v2 geometry kernels | ~2500 |
| `models/_api.py` | Model discovery/registration | ~300 |
| `io/image.py` | Image I/O interface | ~300 |
| `ops/boxes.py` | Bounding box operations | ~500 |
| `csrc/ops/` | C++/CUDA implementations | ~10000+ |

Sources: [torchvision/transforms/transforms.py:1-1500](), [torchvision/transforms/functional.py:1-1200](), [torchvision/models/_api.py:1-300]()

## Testing Infrastructure

TorchVision includes comprehensive testing with specialized utilities:

- **Transform Testing**: Cross-backend validation (PIL vs Tensor), gradient checks, scriptability
- **Model Testing**: Forward pass validation, TorchScript compatibility, FX tracing
- **Dataset Testing**: Fake data injection, integrity checking, v2 wrapper validation
- **Ops Testing**: CPU vs CUDA consistency, deterministic algorithms, gradient checks

**Test Utilities**: `common_utils.py` provides fixtures for device parametrization, RNG state management, and assertion helpers.

Sources: [test/common_utils.py:1-400](), [test/datasets_utils.py:1-200](), [test/test_transforms_v2.py:1-100]()

---

