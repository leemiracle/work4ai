<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/kinetics-i3d · page 3 Pre-trained Models · fetched 2026-10-26 -->

# Pre-trained Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data/checkpoints/rgb_scratch_kin600/checkpoint](data/checkpoints/rgb_scratch_kin600/checkpoint)

</details>



This document provides a comprehensive overview of the pre-trained I3D model checkpoints available in the repository, their training configurations, and how they are used within the evaluation system. It covers model variants, checkpoint structure, and the relationship between training strategies and model performance.

For information about the model architecture itself, see [Model Architecture](#2). For details on how to run evaluations with these models, see [Evaluation Framework](#4).

## Model Categories

The repository provides two main categories of pre-trained models based on their training strategy:

### ImageNet + Kinetics Models
These models are initialized using ImageNet pre-trained 2D Inception-v1 weights that are "inflated" to 3D, then fine-tuned on the Kinetics dataset. This approach leverages the rich feature representations learned from ImageNet's large-scale image classification task.

### Kinetics-Only Models  
These models are trained from scratch on the Kinetics dataset using standard TensorFlow/Sonnet initializers, without any ImageNet pre-training. This category includes both Kinetics-400 and Kinetics-600 variants.

## Checkpoint Structure and Organization

### Available Model Checkpoints

The repository contains multiple pre-trained checkpoints organized by training strategy and input modality:

```mermaid
graph TD
    subgraph "Checkpoint Directory Structure"
        DataCheckpoints["data/checkpoints/"] --> ImageNetRGB["rgb_imagenet/"]
        DataCheckpoints --> ImageNetFlow["flow_imagenet/"]
        DataCheckpoints --> ScratchRGB["rgb_scratch/"]
        DataCheckpoints --> ScratchFlow["flow_scratch/"]
        DataCheckpoints --> ScratchRGB600["rgb_scratch_kin600/"]
    end
    
    subgraph "Checkpoint Components"
        ImageNetRGB --> RGBImageNetFiles["model.ckpt.data<br/>model.ckpt.index<br/>model.ckpt.meta<br/>checkpoint"]
        ImageNetFlow --> FlowImageNetFiles["model.ckpt.data<br/>model.ckpt.index<br/>model.ckpt.meta<br/>checkpoint"]
        ScratchRGB --> RGBScratchFiles["model.ckpt.data<br/>model.ckpt.index<br/>model.ckpt.meta<br/>checkpoint"]
        ScratchFlow --> FlowScratchFiles["model.ckpt.data<br/>model.ckpt.index<br/>model.ckpt.meta<br/>checkpoint"]
        ScratchRGB600 --> RGB600Files["model.ckpt.data<br/>model.ckpt.index<br/>model.ckpt.meta<br/>checkpoint"]
    end
    
    subgraph "Model Loading"
        EvaluateScript["evaluate_sample.py"] --> CheckpointPath["--imagenet_pretrained<br/>--eval_type flags"]
        CheckpointPath --> ImageNetRGB
        CheckpointPath --> ImageNetFlow
        CheckpointPath --> ScratchRGB
        CheckpointPath --> ScratchFlow
        CheckpointPath --> ScratchRGB600
    end
```

Sources: [README.md:90-104](), [data/checkpoints/rgb_scratch_kin600/checkpoint:1-3]()

### TensorFlow Checkpoint Format

Each model checkpoint consists of three main files that follow TensorFlow's standard checkpoint format:

| File Extension | Purpose |
|---|---|
| `.ckpt.data` | Contains the actual parameter values (weights and biases) |
| `.ckpt.index` | Index file mapping variable names to their locations in the data file |
| `.ckpt.meta` | Contains the graph structure and metadata |
| `checkpoint` | Points to the latest checkpoint file |

Sources: [data/checkpoints/rgb_scratch_kin600/checkpoint:1-3]()

## Model Configuration Mapping

The evaluation system uses command-line flags to select different pre-trained models:

### Evaluation Type to Model Mapping

```mermaid
graph LR
    subgraph "Evaluation Flags"
        EvalRGB["--eval_type rgb<br/>--imagenet_pretrained"] --> RGBImageNet["rgb_imagenet/<br/>checkpoint"]
        EvalFlow["--eval_type flow<br/>--imagenet_pretrained"] --> FlowImageNet["flow_imagenet/<br/>checkpoint"]
        EvalJoint["--eval_type joint<br/>--imagenet_pretrained"] --> BothImageNet["rgb_imagenet/ +<br/>flow_imagenet/"]
        
        EvalRGBScratch["--eval_type rgb<br/>--no-imagenet_pretrained"] --> RGBScratch["rgb_scratch/<br/>checkpoint"]
        EvalFlowScratch["--eval_type flow<br/>--no-imagenet_pretrained"] --> FlowScratch["flow_scratch/<br/>checkpoint"]
        EvalJointScratch["--eval_type joint<br/>--no-imagenet_pretrained"] --> BothScratch["rgb_scratch/ +<br/>flow_scratch/"]
        
        EvalRGB600["--eval_type rgb600<br/>--no-imagenet_pretrained"] --> RGB600["rgb_scratch_kin600/<br/>checkpoint"]
    end
    
    subgraph "Model Loading Logic"
        BothImageNet --> JointClassification1["Joint RGB+Flow<br/>Classification"]
        BothScratch --> JointClassification2["Joint RGB+Flow<br/>Classification"]
    end
```

Sources: [README.md:92-96]()

## Training Configurations and Performance

### Training Strategy Comparison

The models were trained using different initialization strategies, each with distinct performance characteristics:

| Model Category | Initialization | Dataset | Top-1 Accuracy | Top-5 Accuracy |
|---|---|---|---|---|
| RGB-I3D (ImageNet + Kinetics) | ImageNet 2D → 3D inflation | Kinetics-400 | 71.1% | 89.3% |
| Flow-I3D (ImageNet + Kinetics) | ImageNet 2D → 3D inflation | Kinetics-400 | 63.4% | 84.9% |
| Two-Stream I3D (ImageNet + Kinetics) | Combined streams | Kinetics-400 | 74.2% | 91.3% |
| RGB-I3D (Kinetics-only) | Random initialization | Kinetics-400 | 68.4% | 88.0% |
| Flow-I3D (Kinetics-only) | Random initialization | Kinetics-400 | 61.5% | 83.4% |
| Two-Stream I3D (Kinetics-only) | Combined streams | Kinetics-400 | 71.6% | 90.0% |

Sources: [README.md:131-138]()

### Training Hyperparameters

The models were trained using synchronous SGD with the following configuration:

```mermaid
graph TD
    subgraph "Training Configuration"
        SGD["tf.train.SyncReplicasOptimizer"] --> Replicas["64 replicas + 4 backup"]
        SGD --> BatchSize["Minibatch size: 6"]
        SGD --> Dropout["Dropout: 0.5"]
        SGD --> BatchNorm["BatchNorm enabled"]
        SGD --> Momentum["SGD momentum: 0.9"]
        SGD --> WeightDecay["Weight decay: 1e-7"]
    end
    
    subgraph "Learning Rate Schedules"
        RGBSchedule["RGB Model:<br/>0-97k: 1e-1<br/>97k-108k: 1e-2<br/>108k-115k: 1e-3"]
        FlowSchedule["Flow Model:<br/>0-97k: 1e-1<br/>97k-104.5k: 1e-2<br/>104.5k-115k: 1e-3<br/>115k-140k: 1e-1<br/>140k-150k: 1e-2<br/>150k-155k: 1e-3"]
    end
    
    SGD --> RGBSchedule
    SGD --> FlowSchedule
```

Sources: [README.md:106-129]()

## Model Usage in Evaluation Pipeline

### Default Model Loading Behavior

The `evaluate_sample.py` script determines which checkpoints to load based on command-line flags:

```mermaid
graph TD
    subgraph "Flag Processing"
        ImageNetFlag["--imagenet_pretrained<br/>(default: True)"] --> ImageNetPath["ImageNet + Kinetics<br/>Models"]
        NoImageNetFlag["--no-imagenet_pretrained"] --> ScratchPath["Kinetics-only<br/>Models"]
        
        EvalType["--eval_type<br/>(rgb/flow/joint/rgb600)"] --> StreamSelection["Stream Selection<br/>Logic"]
    end
    
    subgraph "Checkpoint Loading"
        ImageNetPath --> LoadImageNet["Load rgb_imagenet/<br/>and/or flow_imagenet/"]
        ScratchPath --> LoadScratch["Load rgb_scratch/<br/>and/or flow_scratch/"]
        
        RGB600Type["--eval_type rgb600"] --> LoadRGB600["Load rgb_scratch_kin600/"]
    end
    
    subgraph "Model Instantiation"
        LoadImageNet --> CreateModel["i3d.InceptionI3d()<br/>model creation"]
        LoadScratch --> CreateModel
        LoadRGB600 --> CreateModel
        
        CreateModel --> TFSession["TensorFlow Session<br/>with loaded weights"]
    end
```

Sources: [README.md:42-47](), [README.md:90-104]()

### Joint Classification Pipeline

For two-stream evaluation (`--eval_type joint`), the system loads both RGB and Flow models and combines their predictions:

```mermaid
graph LR
    subgraph "Model Loading"
        RGBCheckpoint["RGB Checkpoint<br/>(imagenet or scratch)"] --> RGBModel["RGB I3D Model"]
        FlowCheckpoint["Flow Checkpoint<br/>(imagenet or scratch)"] --> FlowModel["Flow I3D Model"]
    end
    
    subgraph "Inference"
        RGBModel --> RGBLogits["RGB Logits<br/>(400 or 600 classes)"]
        FlowModel --> FlowLogits["Flow Logits<br/>(400 or 600 classes)"]
    end
    
    subgraph "Combination"
        RGBLogits --> AddLogits["Logit Addition<br/>(equal weighting)"]
        FlowLogits --> AddLogits
        AddLogits --> FinalPrediction["Final Classification<br/>Results"]
    end
```

Sources: [README.md:102-104]()

## Special Model: Kinetics-600 RGB

The repository includes a special RGB-only model trained from scratch on the larger Kinetics-600 dataset, which contains 600 action classes compared to the standard 400 classes:

- **Checkpoint Path**: `data/checkpoints/rgb_scratch_kin600/`
- **Evaluation Flag**: `--eval_type rgb600`
- **Dataset**: Kinetics-600 (600 action classes)
- **Training**: From scratch (no ImageNet pre-training)
- **Input Modality**: RGB only

This model represents the latest addition to the available pre-trained models and demonstrates performance on the expanded action vocabulary.

Sources: [README.md:20](), [data/checkpoints/rgb_scratch_kin600/checkpoint:1-3]()

---

