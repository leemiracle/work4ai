<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/kinetics-i3d · page 4 Evaluation Framework · fetched 2026-10-26 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evaluate_sample.py](evaluate_sample.py)
- [multi_evaluate.sh](multi_evaluate.sh)

</details>



The evaluation framework provides tools for testing pre-trained I3D models on video samples and analyzing their classification performance. This system supports evaluation of different model configurations including RGB-only, optical flow-only, and joint two-stream models, with both ImageNet pre-trained and from-scratch training variants.

For information about the actual model architectures being evaluated, see [Model Architecture](#2). For details about the pre-trained model checkpoints, see [Pre-trained Models](#3). For analysis of evaluation results, see [Results and Analysis](#5).

## System Overview

The evaluation framework consists of two primary components: a core evaluation script for single runs and a batch evaluation script for systematic testing across multiple configurations.

**Evaluation System Architecture**

```mermaid
graph TD
    MultiEval["multi_evaluate.sh"] --> EvalSample["evaluate_sample.py"]
    
    EvalSample --> ConfigParsing["Configuration Parsing"]
    ConfigParsing --> ModelType{"eval_type parameter"}
    ConfigParsing --> PretrainFlag{"imagenet_pretrained flag"}
    
    ModelType --> RGB["RGB Stream Only"]
    ModelType --> Flow["Flow Stream Only"] 
    ModelType --> RGB600["RGB600 Classes"]
    ModelType --> Joint["Joint Two-Stream"]
    
    PretrainFlag --> ImageNetModels["ImageNet Pre-trained Models"]
    PretrainFlag --> ScratchModels["From-Scratch Models"]
    
    RGB --> RGBPipeline["RGB Processing Pipeline"]
    Flow --> FlowPipeline["Flow Processing Pipeline"]
    RGB600 --> RGB600Pipeline["RGB600 Processing Pipeline"]
    Joint --> JointPipeline["Joint Processing Pipeline"]
    
    RGBPipeline --> OutputGen["Output Generation"]
    FlowPipeline --> OutputGen
    RGB600Pipeline --> OutputGen  
    JointPipeline --> OutputGen
    
    OutputGen --> ResultFiles["Result Files"]
```

Sources: [evaluate_sample.py:47-48](), [evaluate_sample.py:61-62](), [multi_evaluate.sh:17-23]()

## Core Evaluation Script

The `evaluate_sample.py` script serves as the primary evaluation engine, handling model loading, inference, and result generation for individual evaluation runs.

### Configuration Parameters

The script accepts two main configuration flags that determine the evaluation behavior:

| Parameter | Values | Description |
|-----------|--------|-------------|
| `eval_type` | `rgb`, `rgb600`, `flow`, `joint` | Specifies which model stream(s) to evaluate |
| `imagenet_pretrained` | `true`, `false` | Whether to use ImageNet pre-trained models |

Sources: [evaluate_sample.py:47-48]()

### Model Loading and Checkpoint Management

The evaluation script maintains a mapping of model types to their corresponding checkpoint paths:

**Checkpoint Path Configuration**

```mermaid
graph TD
    CheckpointPaths["_CHECKPOINT_PATHS Dictionary"] --> RGB["'rgb': rgb_scratch/model.ckpt"]
    CheckpointPaths --> RGB600["'rgb600': rgb_scratch_kin600/model.ckpt"]
    CheckpointPaths --> Flow["'flow': flow_scratch/model.ckpt"]
    CheckpointPaths --> RGBImageNet["'rgb_imagenet': rgb_imagenet/model.ckpt"]
    CheckpointPaths --> FlowImageNet["'flow_imagenet': flow_imagenet/model.ckpt"]
    
    EvalType["eval_type parameter"] --> ModelSelection{"Model Selection Logic"}
    ImageNetFlag["imagenet_pretrained flag"] --> ModelSelection
    
    ModelSelection --> RGB
    ModelSelection --> RGB600
    ModelSelection --> Flow
    ModelSelection --> RGBImageNet
    ModelSelection --> FlowImageNet
    
    ModelSelection --> TensorFlowSaver["tf.train.Saver"]
    TensorFlowSaver --> SessionRestore["sess.restore()"]
```

Sources: [evaluate_sample.py:34-40](), [evaluate_sample.py:121-124](), [evaluate_sample.py:131-134]()

### Input Data Processing

The script processes sample video data stored as NumPy arrays, with different input shapes for RGB and optical flow streams:

- **RGB Input**: Shape `(1, 79, 224, 224, 3)` for appearance information
- **Flow Input**: Shape `(1, 79, 224, 224, 2)` for motion information

Sources: [evaluate_sample.py:28-32](), [evaluate_sample.py:71-73](), [evaluate_sample.py:96-98]()

### Model Architecture Instantiation

The script creates separate I3D model instances for each stream using the `InceptionI3d` class:

```mermaid
graph LR
    RGBScope["tf.variable_scope('RGB')"] --> RGBModel["i3d.InceptionI3d(NUM_CLASSES)"]
    FlowScope["tf.variable_scope('Flow')"] --> FlowModel["i3d.InceptionI3d(NUM_CLASSES)"]
    
    RGBModel --> RGBLogits["rgb_logits"]
    FlowModel --> FlowLogits["flow_logits"]
    
    EvalType["eval_type"] --> LogitSelection{"Logit Selection"}
    RGBLogits --> LogitSelection
    FlowLogits --> LogitSelection
    
    LogitSelection --> RGBOnly["RGB Only: rgb_logits"]
    LogitSelection --> FlowOnly["Flow Only: flow_logits"] 
    LogitSelection --> JointStream["Joint: rgb_logits + flow_logits"]
    
    LogitSelection --> Softmax["tf.nn.softmax()"]
    Softmax --> Predictions["model_predictions"]
```

Sources: [evaluate_sample.py:76-80](), [evaluate_sample.py:99-103](), [evaluate_sample.py:110-116]()

## Batch Evaluation System

The `multi_evaluate.sh` script orchestrates systematic evaluation across all supported model configurations, generating a comprehensive set of results for comparison.

### Evaluation Configuration Matrix

The batch script executes seven distinct evaluation configurations:

**Batch Evaluation Workflow**

```mermaid
graph TD
    BatchScript["multi_evaluate.sh"] --> ImageNetConfigs["ImageNet Pre-trained Configurations"]
    BatchScript --> ScratchConfigs["From-Scratch Configurations"]
    
    ImageNetConfigs --> ImageNetJoint["--imagenet_pretrained=true --eval_type=joint"]
    ImageNetConfigs --> ImageNetFlow["--imagenet_pretrained=true --eval_type=flow"]
    ImageNetConfigs --> ImageNetRGB["--imagenet_pretrained=true --eval_type=rgb"]
    
    ScratchConfigs --> ScratchRGB600["--imagenet_pretrained=false --eval_type=rgb600"]
    ScratchConfigs --> ScratchJoint["--imagenet_pretrained=false --eval_type=joint"]
    ScratchConfigs --> ScratchFlow["--imagenet_pretrained=false --eval_type=flow"]
    ScratchConfigs --> ScratchRGB["--imagenet_pretrained=false --eval_type=rgb"]
    
    ImageNetJoint --> OutputJoint["out/imagenet_joint.txt"]
    ImageNetFlow --> OutputFlow["out/imagenet_flow.txt"]
    ImageNetRGB --> OutputRGB["out/imagenet_rgb.txt"]
    ScratchRGB600 --> OutputRGB600["out/no_imagenet_rgb600.txt"]
    ScratchJoint --> OutputScratchJoint["out/no_imagenet_joint.txt"]
    ScratchFlow --> OutputScratchFlow["out/no_imagenet_flow.txt"]
    ScratchRGB --> OutputScratchRGB["out/no_imagenet_rgb.txt"]
```

Sources: [multi_evaluate.sh:17-23]()

### Output File Generation

Each evaluation configuration generates a dedicated output file in the `out/` directory with a standardized naming convention:

- **ImageNet Pre-trained**: `imagenet_{stream_type}.txt`
- **From-Scratch**: `no_imagenet_{stream_type}.txt`
- **Special Case**: `no_imagenet_rgb600.txt` for the 600-class RGB model

Sources: [multi_evaluate.sh:17-23]()

## Output Format and Analysis

The evaluation framework generates standardized output containing logit norms, probability rankings, and class predictions.

### Standard Output Structure

Each evaluation produces the following output format:

1. **Logit Norm**: L2 norm of the raw logit values
2. **Top-K Predictions**: Ranked list of top 20 most probable classes
3. **Class Information**: For each prediction, shows probability, logit value, and class label

**Output Generation Process**

```mermaid
graph LR
    ModelLogits["model_logits"] --> LogitNorm["np.linalg.norm()"]
    ModelLogits --> Softmax["tf.nn.softmax()"]
    Softmax --> Predictions["out_predictions"]
    
    Predictions --> Sorting["np.argsort()[::-1]"]
    Sorting --> TopK["sorted_indices[:20]"]
    
    TopK --> OutputLoop["For each index:"]
    OutputLoop --> ProbOutput["out_predictions[index]"]
    OutputLoop --> LogitOutput["out_logits[index]"]
    OutputLoop --> ClassOutput["kinetics_classes[index]"]
    
    LogitNorm --> PrintNorm["print('Norm of logits: %f')"]
    ProbOutput --> PrintResults["print(probability, logit, class_name)"]
    LogitOutput --> PrintResults
    ClassOutput --> PrintResults
```

Sources: [evaluate_sample.py:140-151]()

### Class Label Integration

The system supports both 400-class and 600-class Kinetics datasets through separate label map files:

- **400 Classes**: `data/label_map.txt`
- **600 Classes**: `data/label_map_600.txt`

The appropriate label map is selected based on the `eval_type` parameter, with `rgb600` using the 600-class mapping.

Sources: [evaluate_sample.py:42-43](), [evaluate_sample.py:57-67]()

## Usage Examples

### Single Evaluation

To run a single evaluation configuration:

```bash
python evaluate_sample.py --eval_type joint --imagenet_pretrained true
```

### Comprehensive Evaluation

To run all evaluation configurations:

```bash
./multi_evaluate.sh
```

This generates seven output files covering all combinations of model types and training strategies, enabling comprehensive performance comparison across the I3D model variants.

Sources: [multi_evaluate.sh:1-24](), [evaluate_sample.py:47-48]()

---

