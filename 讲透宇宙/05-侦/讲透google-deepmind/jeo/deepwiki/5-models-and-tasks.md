<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/jeo · page 5 Models and Tasks · fetched 2026-10-26 -->

# Models and Tasks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jeo/tasks/segmentation.py](jeo/tasks/segmentation.py)
- [jeo/tasks/task_builder.py](jeo/tasks/task_builder.py)

</details>



This document provides an overview of the model architectures and task definitions supported by the Jeo framework. It covers the abstract task system, available task types, and how models integrate with tasks during training and evaluation.

For detailed implementation information about specific model architectures, see [Model Implementations](#5.1). For information about configuring and defining custom tasks, see [Task Definitions](#5.2).

## Task System Architecture

The Jeo framework uses an abstract task system that separates the concerns of model computation, loss calculation, and data processing. Tasks define how to compute losses and auxiliary metrics from model outputs and batch data.

### Task Framework Hierarchy

```mermaid
classDiagram
    class TaskBase {
        <<abstract>>
        +loss_fn: Callable
        +modalities: Sequence[str]
        +input_as_dict: bool
        +model_inputs(batches) tuple
        +get_predict_fn(model, rngs, train) PredictFn
        +get_loss_and_aux(model_outputs, batches, train)* tuple
    }

    class ClassificationTask {
        +labels_key: str
        +get_loss_and_aux(model_outputs, batches, train) tuple
    }

    class SegmentationTask {
        +exclude_background_class: bool
        +labels_key: str
        +weights_key: str
        +mask_key: str
        +get_loss_and_aux(model_outputs, batches, train) tuple
    }

    class RegressionSegmentationTask {
        +labels_key: str
        +mask_key: str
        +get_loss_and_aux(model_outputs, batches, train) tuple
    }

    class PanopticSegmentationTask {
        +exclude_background_class: bool
        +min_fraction: float
        +get_loss_and_aux(model_outputs, batches, train) tuple
    }

    TaskBase <|-- ClassificationTask
    TaskBase <|-- SegmentationTask
    TaskBase <|-- RegressionSegmentationTask
    TaskBase <|-- PanopticSegmentationTask
```

*Sources: [jeo/tasks/task_builder.py:35-111](), [jeo/tasks/segmentation.py:22-157]()*

### Task Registration and Factory System

The framework uses a registration system to map task names to their implementations, allowing for easy configuration and extensibility.

```mermaid
graph TD
    subgraph "Task Registry"
        COMMON_TASKS["COMMON_TASKS dict<br/>task_builder.py:113-129"]
        TaskFactory["from_config()<br/>task_builder.py:132-145"]
    end

    subgraph "Task Configuration"
        Config["config.task_type<br/>config.loss<br/>config.task_kw"]
        LossKw["config.loss_kw"]
    end

    subgraph "Task Implementations"
        ClassTask["classification.ClassificationTask"]
        SegTask["segmentation.SegmentationTask"]
        RegTask["regression.RegressionTask"]
        MAETask["mae.MaeTask"]
        ContrastiveTask["contrastive.SimClrTask"]
    end

    Config --> TaskFactory
    LossKw --> TaskFactory
    TaskFactory --> COMMON_TASKS
    COMMON_TASKS --> ClassTask
    COMMON_TASKS --> SegTask
    COMMON_TASKS --> RegTask
    COMMON_TASKS --> MAETask
    COMMON_TASKS --> ContrastiveTask
```

*Sources: [jeo/tasks/task_builder.py:113-146]()*

## Available Task Types

The framework provides a comprehensive set of task types for different machine learning scenarios:

| Task Type | Implementation | Purpose |
|-----------|----------------|---------|
| `classification` | `classification.ClassificationTask` | Standard multi-class classification |
| `classification_multihead` | `classification.MultiHeadClassificationTask` | Multi-output classification |
| `classification_multilabel` | `classification.ClassificationTask` | Multi-label classification |
| `segmentation` | `segmentation.SegmentationTask` | Semantic segmentation |
| `regression_segmentation` | `segmentation.RegressionSegmentationTask` | Regression over spatial data |
| `panoptic_segmentation` | `segmentation.PanopticSegmentationTask` | Combined semantic + instance segmentation |
| `regression` | `regression.RegressionTask` | Standard regression |
| `masked_autoencoder` | `mae.MaeTask` | Self-supervised masked reconstruction |
| `simclr` | `contrastive.SimClrTask` | Contrastive learning |
| `ssl_classification` | `ssl_tasks.SslClassificationTask` | Semi-supervised classification |

*Sources: [jeo/tasks/task_builder.py:113-129]()*

### Segmentation Task Details

The segmentation tasks demonstrate the flexibility of the task system:

```mermaid
graph LR
    subgraph "SegmentationTask"
        SegInput["Model Input<br/>Batch Images"]
        SegLogits["Model Output<br/>logits (B,H,W,N_CLASSES)"]
        SegLabels["Ground Truth<br/>segmentation_mask (B,H,W,1)"]
        SegWeights["Weights Calculation<br/>exclude_background_class<br/>valid_mask"]
        SegLoss["Loss Computation<br/>generalized_softmax_xent"]
    end

    subgraph "RegressionSegmentationTask"
        RegInput["Model Input<br/>Batch Images"]
        RegLogits["Model Output<br/>predictions (B,H,W,1)"]
        RegLabels["Ground Truth<br/>labels (B,H,W,1)"]
        RegMask["Valid Mask<br/>valid_label_mask"]
        RegLoss["Loss Computation<br/>l2_loss"]
    end

    SegInput --> SegLogits
    SegLogits --> SegLoss
    SegLabels --> SegWeights
    SegWeights --> SegLoss

    RegInput --> RegLogits
    RegLogits --> RegLoss
    RegLabels --> RegLoss
    RegMask --> RegLoss
```

*Sources: [jeo/tasks/segmentation.py:22-106]()*

## Model-Task Integration

Tasks define how models interact with data and losses during training. The integration follows a standardized pattern:

### Model Input Processing

```mermaid
sequenceDiagram
    participant Task as "TaskBase"
    participant Model as "Model (BIT/ViT/MTSViT)"
    participant Loss as "Loss Function"
    participant Eval as "Evaluator"

    Task->>Task: "model_inputs(*batches)"
    Note over Task: "Extract modalities<br/>from batch data"
    
    Task->>Model: "model.apply(params, *inputs)"
    Model->>Task: "model_outputs<br/>(logits, aux)"
    
    Task->>Task: "get_loss_and_aux(outputs, batches)"
    Task->>Loss: "loss_fn(logits, labels, weights)"
    Loss->>Task: "loss_value, aux_dict"
    
    Task->>Eval: "predict_fn(params, **batch)"
    Note over Eval: "Used for evaluation<br/>during training"
```

*Sources: [jeo/tasks/task_builder.py:53-111]()*

### Loss and Auxiliary Information Flow

Tasks are responsible for computing both the primary loss and auxiliary information that can be used for monitoring and evaluation:

```mermaid
graph TD
    subgraph "Task Processing Pipeline"
        ModelOutput["Model Outputs<br/>(logits, model_aux)"]
        BatchData["Batch Data<br/>(images, labels, masks)"]
        
        subgraph "Loss Computation"
            LossCalc["Loss Calculation<br/>self.loss_fn()"]
            WeightCalc["Weight Calculation<br/>_get_weights()"]
            MaskApply["Mask Application<br/>valid pixels only"]
        end
        
        subgraph "Output"
            PrimaryLoss["Primary Loss<br/>scalar or array"]
            AuxDict["Auxiliary Dict<br/>metrics, model_aux"]
        end
    end

    ModelOutput --> LossCalc
    BatchData --> WeightCalc
    BatchData --> MaskApply
    WeightCalc --> LossCalc
    MaskApply --> LossCalc
    
    LossCalc --> PrimaryLoss
    LossCalc --> AuxDict
    ModelOutput --> AuxDict
```

*Sources: [jeo/tasks/segmentation.py:42-70]()*

## Task Configuration

Tasks are configured through the main configuration system and can accept various parameters:

### Base Task Parameters

All tasks inherit common configuration options from `TaskBase`:

- `loss_name`: Name of the loss function to use
- `loss_kw`: Additional keyword arguments for the loss function  
- `modalities`: Input modalities to extract from batch data (default: `("image",)`)
- `input_as_dict`: Whether to pass inputs as dictionary to model

### Task-Specific Parameters

Different task types accept specialized parameters:

**SegmentationTask**:
- `exclude_background_class`: Whether to exclude background pixels from loss
- `labels_key`: Key for segmentation labels in batch (default: `"segmentation_mask"`)
- `weights_key`: Optional key for pixel-wise weights
- `mask_key`: Key for valid pixel mask
- `model_aux_metrics`: Model auxiliary metrics to include in output

**RegressionSegmentationTask**:
- `labels_key`: Key for regression target values
- `mask_key`: Key for valid pixel mask

*Sources: [jeo/tasks/task_builder.py:38-51](), [jeo/tasks/segmentation.py:25-40](), [jeo/tasks/segmentation.py:76-81]()*

The task system provides a flexible foundation for defining how models, losses, and evaluation metrics interact during training, making it easy to extend Jeo to new problem domains and model architectures.

---

