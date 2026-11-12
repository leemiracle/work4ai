<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/samples-for-ai · page 4 Specialized Projects · fetched 2026-10-26 -->

# Specialized Projects

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [projects/BearClassificationUWPDemo/BearClassificationUWP.App/ViewModel/ResultViewModel.cs](projects/BearClassificationUWPDemo/BearClassificationUWP.App/ViewModel/ResultViewModel.cs)
- [projects/BearClassificationUWPDemo/BearClassificationUWPDemo.sln](projects/BearClassificationUWPDemo/BearClassificationUWPDemo.sln)
- [projects/MnistDemo/MNIST/AzureBatchAI_TF_MNIST.json](projects/MnistDemo/MNIST/AzureBatchAI_TF_MNIST.json)
- [projects/MnistDemo/MNIST/DeepLearningVM.json](projects/MnistDemo/MNIST/DeepLearningVM.json)
- [projects/MnistDemo/MNIST/MNIST.pyproj](projects/MnistDemo/MNIST/MNIST.pyproj)
- [projects/MnistDemo/MNIST/mnist.py](projects/MnistDemo/MNIST/mnist.py)
- [projects/MnistDemo/MnistDemo.sln](projects/MnistDemo/MnistDemo.sln)
- [projects/StyleTransfer/StyleTransferTraining/StyleTransferTraining.pyproj](projects/StyleTransfer/StyleTransferTraining/StyleTransferTraining.pyproj)
- [projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000001.jpg](projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000001.jpg)
- [projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000014.jpg](projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000014.jpg)
- [projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000016.jpg](projects/StyleTransfer/StyleTransferTraining/data/test/COCO_test2014_000000000016.jpg)
- [projects/StyleTransfer/StyleTransferTraining/data/train/readme.md](projects/StyleTransfer/StyleTransferTraining/data/train/readme.md)
- [projects/StyleTransfer/StyleTransferTraining/src/Parameter Sweep.json](projects/StyleTransfer/StyleTransferTraining/src/Parameter Sweep.json)
- [projects/StyleTransfer/StyleTransferTraining/src/dlvm.json](projects/StyleTransfer/StyleTransferTraining/src/dlvm.json)
- [projects/StyleTransfer/StyleTransferTraining/src/export.py](projects/StyleTransfer/StyleTransferTraining/src/export.py)
- [projects/StyleTransfer/StyleTransferTraining/src/inference.py](projects/StyleTransfer/StyleTransferTraining/src/inference.py)
- [projects/StyleTransfer/StyleTransferTraining/src/stylenet.py](projects/StyleTransfer/StyleTransferTraining/src/stylenet.py)
- [projects/StyleTransfer/StyleTransferTraining/src/train.py](projects/StyleTransfer/StyleTransferTraining/src/train.py)
- [projects/StyleTransfer/StyleTransferTraining/src/utils.py](projects/StyleTransfer/StyleTransferTraining/src/utils.py)
- [projects/StyleTransfer/StyleTransferTraining/src/vgg.py](projects/StyleTransfer/StyleTransferTraining/src/vgg.py)

</details>



This section covers production-ready applications and research projects that demonstrate real-world AI implementations beyond basic framework examples. These projects showcase complete end-to-end machine learning workflows, from training to deployment, and include mobile/desktop applications that integrate trained models for practical use cases.

For basic framework examples and tutorials, see [Framework Examples](#3). For advanced research topics and distributed training, see [Advanced Topics](#5).

## Architecture Overview

The specialized projects demonstrate different deployment patterns and application architectures for machine learning models:

```mermaid
graph TB
    subgraph "Training Pipeline"
        TRAIN["train.py<br/>Model Training"]
        EXPORT["export.py<br/>Model Export"]
        CHECKPOINT["Checkpoint Files<br/>.ckpt format"]
        SAVEDMODEL["SavedModel<br/>TensorFlow Serving"]
    end
    
    subgraph "Neural Style Transfer"
        STYLENET["stylenet.py<br/>Style Transfer Network"]
        VGG["vgg.py<br/>VGG-19 Feature Extractor"]
        INFERENCE["inference.py<br/>Image Processing"]
    end
    
    subgraph "Production Applications"
        UWP_BEAR["BearClassificationUWP<br/>ONNX + Windows ML"]
        UWP_MNIST["MNIST.App<br/>Digit Recognition"]
        MODELLIB["MNISTModelLibrary<br/>Shared ML Logic"]
    end
    
    subgraph "Model Formats"
        ONNX["ONNX Models<br/>Cross-platform"]
        TFMODEL["TensorFlow Models<br/>Native format"]
    end
    
    TRAIN --> CHECKPOINT
    TRAIN --> SAVEDMODEL
    EXPORT --> SAVEDMODEL
    STYLENET --> INFERENCE
    VGG --> STYLENET
    
    CHECKPOINT --> INFERENCE
    SAVEDMODEL --> UWP_BEAR
    TFMODEL --> UWP_MNIST
    ONNX --> UWP_BEAR
    MODELLIB --> UWP_MNIST
```

Sources: [projects/StyleTransfer/StyleTransferTraining/src/train.py:1-234](), [projects/StyleTransfer/StyleTransferTraining/src/inference.py:1-65](), [projects/BearClassificationUWPDemo/BearClassificationUWP.App/ViewModel/ResultViewModel.cs:1-244](), [projects/MnistDemo/MnistDemo.sln:1-41]()

## Neural Style Transfer Implementation

The neural style transfer project demonstrates real-time artistic style transfer using deep learning, implementing the approach from Gatys et al. with optimizations for faster inference.

### Training Architecture

```mermaid
graph TD
    subgraph "Data Input"
        COCO["COCO Dataset<br/>Training Images"]
        STYLE["Style Images<br/>Artistic References"]
        VGG_MODEL["VGG-19 MatConvNet<br/>Pre-trained Weights"]
    end
    
    subgraph "Network Components"
        CONTENT_NET["Content Network<br/>vgg.net()"]
        STYLE_TARGET["Style Target<br/>get_style_vgg()"]
        TRANSFORM_NET["Transform Network<br/>stylenet.net()"]
    end
    
    subgraph "Loss Functions"
        CONTENT_LOSS["Content Loss<br/>total_content_loss()"]
        STYLE_LOSS["Style Loss<br/>total_style_loss()"]
        TV_LOSS["Total Variation Loss<br/>total_variation_regularization()"]
    end
    
    subgraph "Training Process"
        OPTIMIZER["Adam Optimizer<br/>learning_rate=1e-3"]
        CHECKPOINT_SAVE["Checkpoint Saving<br/>every 2000 steps"]
        TENSORBOARD["TensorBoard Logging<br/>loss tracking"]
    end
    
    COCO --> TRANSFORM_NET
    STYLE --> STYLE_TARGET
    VGG_MODEL --> CONTENT_NET
    VGG_MODEL --> STYLE_TARGET
    
    TRANSFORM_NET --> CONTENT_NET
    CONTENT_NET --> CONTENT_LOSS
    TRANSFORM_NET --> STYLE_LOSS
    TRANSFORM_NET --> TV_LOSS
    
    CONTENT_LOSS --> OPTIMIZER
    STYLE_LOSS --> OPTIMIZER
    TV_LOSS --> OPTIMIZER
    
    OPTIMIZER --> CHECKPOINT_SAVE
    OPTIMIZER --> TENSORBOARD
```

Sources: [projects/StyleTransfer/StyleTransferTraining/src/train.py:142-234](), [projects/StyleTransfer/StyleTransferTraining/src/vgg.py:67-111](), [projects/StyleTransfer/StyleTransferTraining/src/stylenet.py:49-77]()

### Core Implementation Details

The style transfer implementation consists of several key components:

| Component | File | Function | Purpose |
|-----------|------|----------|---------|
| Style Network | `stylenet.py` | `net()` | Transform input images with artistic style |
| VGG Feature Extractor | `vgg.py` | `net()`, `get_style_vgg()` | Extract content and style features |
| Training Loop | `train.py` | `main()` | Orchestrate training process |
| Inference Engine | `inference.py` | Image processing | Apply trained models to new images |
| Model Export | `export.py` | `export()` | Convert checkpoints to SavedModel |

The training process uses three loss components:
- **Content Loss** (`lambda_feat=7.5`): Preserves content structure using VGG `relu4_2` features
- **Style Loss** (`lambda_style=15`): Matches style characteristics using Gram matrices from multiple VGG layers
- **Total Variation Loss** (`lambda_tv=10e-4`): Reduces noise and ensures spatial smoothness

Sources: [projects/StyleTransfer/StyleTransferTraining/src/train.py:23-26](), [projects/StyleTransfer/StyleTransferTraining/src/train.py:158-168](), [projects/StyleTransfer/StyleTransferTraining/src/vgg.py:88-111]()

### Deployment and Inference

The trained models support multiple deployment scenarios:

```mermaid
graph LR
    subgraph "Model Formats"
        CKPT["Checkpoint Format<br/>.ckpt files"]
        SAVED["SavedModel Format<br/>TensorFlow Serving"]
    end
    
    subgraph "Inference Modes"
        CLI["Command Line<br/>inference.py"]
        BATCH["Batch Processing<br/>Multiple images"]
        REALTIME["Real-time Processing<br/>Video streams"]
    end
    
    subgraph "Input Sources"
        LOCAL["Local Images<br/>File system"]
        URL["Remote Images<br/>HTTP URLs"]
        CAMERA["Camera Feed<br/>Live capture"]
    end
    
    CKPT --> CLI
    SAVED --> CLI
    CLI --> BATCH
    CLI --> REALTIME
    
    LOCAL --> CLI
    URL --> CLI
    CAMERA --> REALTIME
```

Sources: [projects/StyleTransfer/StyleTransferTraining/src/inference.py:23-65](), [projects/StyleTransfer/StyleTransferTraining/src/export.py:12-48]()

## UWP Bear Classification Demo

The bear classification demo showcases Windows ML integration with a UWP application, demonstrating how to deploy ONNX models in production Windows applications.

### Application Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        MAINPAGE["MainPage<br/>XAML UI"]
        RESULTVIEW["ResultViewModel<br/>MVVM Pattern"]
        COMMANDS["RelayCommand<br/>UI Actions"]
    end
    
    subgraph "Business Logic"
        LOADMODEL["LoadModel()<br/>ONNX Loading"]
        EVALUATE["EvaluateAsync()<br/>ML Inference"]
        PREPROCESSING["Image Processing<br/>VideoFrame Creation"]
    end
    
    subgraph "Data Sources"
        NETPIC["EvaluateNetPicAsync()<br/>URL Images"]
        LOCALPIC["EvaluateLocalPicAsync()<br/>File Picker"]
        FILEPICKER["FileOpenPicker<br/>Image Selection"]
    end
    
    subgraph "ML Integration"
        ONNXMODEL["BearClassification.onnx<br/>Trained Model"]
        WINML["Windows ML APIs<br/>Model Execution"]
        RESULTS["Classification Results<br/>Probability Dictionary"]
    end
    
    MAINPAGE --> RESULTVIEW
    RESULTVIEW --> COMMANDS
    COMMANDS --> NETPIC
    COMMANDS --> LOCALPIC
    
    NETPIC --> PREPROCESSING
    LOCALPIC --> FILEPICKER
    FILEPICKER --> PREPROCESSING
    
    PREPROCESSING --> EVALUATE
    LOADMODEL --> ONNXMODEL
    ONNXMODEL --> WINML
    EVALUATE --> WINML
    WINML --> RESULTS
    RESULTS --> RESULTVIEW
```

Sources: [projects/BearClassificationUWPDemo/BearClassificationUWP.App/ViewModel/ResultViewModel.cs:19-244]()

### Model Integration Implementation

The `ResultViewModel` class demonstrates best practices for integrating machine learning models in UWP applications:

| Method | Purpose | Key Implementation |
|--------|---------|-------------------|
| `LoadModel()` | Initialize ONNX model | `BearClassificationModel.CreateBearClassificationModel()` |
| `EvaluateNetPicAsync()` | Process web images | HTTP download → `VideoFrame` → inference |
| `EvaluateLocalPicAsync()` | Process local files | File picker → stream → `VideoFrame` → inference |
| `EvaluateAsync()` | Run inference | Model evaluation → probability ranking → UI update |
| `DescribResult()` | Format output | Confidence levels → localized text |

The implementation handles multiple confidence levels:
- **High confidence** (`>= 0.8`): "must be" classification
- **Medium confidence** (`0.5-0.8`): "may be" classification  
- **Low confidence** (`< 0.5`): "might be" classification

Sources: [projects/BearClassificationUWPDemo/BearClassificationUWP.App/ViewModel/ResultViewModel.cs:115-243]()

## MNIST Demo Suite

The MNIST demo provides a complete example of training, model creation, and deployment across multiple platforms, demonstrating the full machine learning lifecycle.

### Multi-Component Architecture

```mermaid
graph TB
    subgraph "Training Component"
        MNIST_PY["mnist.py<br/>TensorFlow Training"]
        LENET["LeNet-5 Architecture<br/>CNN Implementation"]
        DATASET["MNIST Dataset<br/>Automatic Download"]
    end
    
    subgraph "Model Pipeline"
        EXTRACTION["extract_data()<br/>Image Processing"]
        TRAINING["Training Loop<br/>Batch Processing"]
        EVALUATION["Evaluation<br/>Test Accuracy"]
        EXPORT_MODEL["Model Export<br/>SavedModel Format"]
    end
    
    subgraph "UWP Application"
        MNIST_APP["MNIST.App<br/>C# UWP"]
        MODEL_LIB["MNISTModelLibrary<br/>Shared Logic"]
        UI_CONTROLS["Drawing Canvas<br/>User Input"]
    end
    
    subgraph "Configuration"
        PYPROJ["MNIST.pyproj<br/>Visual Studio Project"]
        DLVM_CONFIG["DeepLearningVM.json<br/>Cloud Training"]
        BATCHAI_CONFIG["AzureBatchAI_TF_MNIST.json<br/>Distributed Training"]
    end
    
    MNIST_PY --> LENET
    DATASET --> EXTRACTION
    EXTRACTION --> TRAINING
    TRAINING --> EVALUATION
    EVALUATION --> EXPORT_MODEL
    
    EXPORT_MODEL --> MODEL_LIB
    MODEL_LIB --> MNIST_APP
    UI_CONTROLS --> MNIST_APP
    
    PYPROJ --> MNIST_PY
    DLVM_CONFIG --> MNIST_PY
    BATCHAI_CONFIG --> MNIST_PY
```

Sources: [projects/MnistDemo/MNIST/mnist.py:1-379](), [projects/MnistDemo/MnistDemo.sln:1-41](), [projects/MnistDemo/MNIST/MNIST.pyproj:1-38]()

### Training Implementation

The MNIST training script implements a complete LeNet-5-like convolutional neural network:

| Layer Type | Implementation | Configuration |
|------------|----------------|---------------|
| Input | 28×28×1 images | Normalized to [-0.5, 0.5] |
| Conv1 | `conv2d()` | 5×5 kernels, 32 features |
| Pool1 | `max_pool_2x2()` | 2×2 pooling |
| Conv2 | `conv2d()` | 5×5 kernels, 64 features |
| Pool2 | `max_pool_2x2()` | 2×2 pooling |
| FC1 | Fully connected | 512 units + dropout |
| Output | Softmax | 10 classes (digits 0-9) |

The training process includes:
- Automatic dataset download from `http://yann.lecun.com/exdb/mnist/`
- Validation set management (5000 images)
- Batch processing with configurable batch sizes
- Regular evaluation and checkpoint saving
- Support for both CPU and GPU training

Sources: [projects/MnistDemo/MNIST/mnist.py:42-54](), [projects/MnistDemo/MNIST/mnist.py:64-99](), [projects/MnistDemo/MNIST/mnist.py:204-280]()

### Cloud Training Configuration

The project includes multiple configuration files for different training environments:

```mermaid
graph LR
    subgraph "Local Development"
        PYPROJ_CONFIG["MNIST.pyproj<br/>--input_dir input/<br/>--output_dir output/"]
    end
    
    subgraph "Cloud Training"
        DLVM["DeepLearningVM.json<br/>Anaconda Python 3.5<br/>Single VM"]
        BATCHAI["AzureBatchAI_TF_MNIST.json<br/>TensorFlow 1.1.0-gpu<br/>Distributed"]
    end
    
    subgraph "Training Parameters"
        EPOCHS["NUM_EPOCHS = 10"]
        BATCH["BATCH_SIZE = 64"]
        EVAL["EVAL_FREQUENCY = 100"]
    end
    
    PYPROJ_CONFIG --> EPOCHS
    DLVM --> EPOCHS
    BATCHAI --> EPOCHS
    
    EPOCHS --> BATCH
    BATCH --> EVAL
```

Sources: [projects/MnistDemo/MNIST/MNIST.pyproj:14](), [projects/MnistDemo/MNIST/DeepLearningVM.json:1-10](), [projects/MnistDemo/MNIST/AzureBatchAI_TF_MNIST.json:1]()

## Distributed Training Integration

The specialized projects demonstrate integration with Microsoft's distributed training platforms through configuration files and parameter sweeps.

### Parameter Sweep Configuration

The style transfer project includes sophisticated parameter sweep capabilities for training multiple models simultaneously:

```mermaid
graph TD
    subgraph "Parameter Sweep Jobs"
        MOSAIC["mosaic.jpg<br/>GPU 0"]
        CANDY["candy.jpg<br/>GPU 1"] 
        STARRY["starry_night.jpg<br/>GPU 2"]
        SCREAM["the_scream.jpg<br/>GPU 3"]
        WAVE["wave.jpg<br/>CPU"]
    end
    
    subgraph "Common Parameters"
        INPUT["--input_dir ~/styletransfer"]
        LAMBDA["--lambda_style 15"]
        PYTHON["python train.py"]
    end
    
    subgraph "GPU Assignment"
        GPU0["CUDA_VISIBLE_DEVICES=0"]
        GPU1["CUDA_VISIBLE_DEVICES=1"]
        GPU2["CUDA_VISIBLE_DEVICES=2"]
        GPU3["CUDA_VISIBLE_DEVICES=3"]
    end
    
    PYTHON --> INPUT
    INPUT --> LAMBDA
    
    LAMBDA --> MOSAIC
    LAMBDA --> CANDY
    LAMBDA --> STARRY
    LAMBDA --> SCREAM
    LAMBDA --> WAVE
    
    MOSAIC --> GPU0
    CANDY --> GPU1
    STARRY --> GPU2
    SCREAM --> GPU3
```

Sources: [projects/StyleTransfer/StyleTransferTraining/src/Parameter Sweep.json:1-33](), [projects/StyleTransfer/StyleTransferTraining/src/dlvm.json:1-11]()

This architecture enables efficient multi-style training across multiple GPUs, with each job producing a specialized model for a specific artistic style. The configuration supports both concurrent execution (`EnableConcurrency: true`) and isolated single-model training for debugging purposes.

---

