<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/bi-att-flow · page 4 Training and Evaluation · fetched 2026-10-26 -->

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [basic/evaluator.py](basic/evaluator.py)
- [basic/trainer.py](basic/trainer.py)

</details>



This document covers the training and evaluation systems in the BiDAF codebase, including the core training loops, evaluation metrics, and multi-GPU support. It provides an overview of how models are trained and assessed for performance on question answering tasks.

For detailed information about the training pipeline implementation, see [Training Pipeline](#4.1). For comprehensive coverage of evaluation metrics and assessment frameworks, see [Evaluation Framework](#4.2). For tools to analyze and visualize training results, see [Visualization and Analysis](#4.3).

## Training and Evaluation Pipeline Overview

The BiDAF system implements a comprehensive training and evaluation pipeline that supports both single-GPU and multi-GPU configurations. The system is designed around separate but coordinated training and evaluation phases that work together to optimize and assess model performance.

### Training and Evaluation Architecture

```mermaid
graph TB
    subgraph "Training System"
        A["Trainer"] --> B["MultiGPUTrainer"]
        B --> C["AdadeltaOptimizer"]
        C --> D["gradient computation"]
        D --> E["parameter updates"]
    end
    
    subgraph "Evaluation System"
        F["Evaluator"] --> G["LabeledEvaluator"]
        G --> H["AccuracyEvaluator"]
        G --> I["F1Evaluator"]
        I --> J["MultiGPUF1Evaluator"]
        G --> K["ForwardEvaluator"]
    end
    
    subgraph "Evaluation Results"
        L["Evaluation"] --> M["AccuracyEvaluation"]
        L --> N["F1Evaluation"]  
        L --> O["ForwardEvaluation"]
        M --> P["accuracy, loss metrics"]
        N --> Q["F1, EM scores"]
        O --> R["answer predictions"]
    end
    
    subgraph "Training Loop Integration"
        S["basic/main.py _train"] --> A
        S --> F
        T["basic/main.py _test"] --> I
        U["basic/main.py _forward"] --> K
    end
    
    A --> V["model.get_loss()"]
    F --> W["model.yp, model.yp2"]
    
    style B fill:#f9f9f9
    style J fill:#f9f9f9
    style S fill:#e1f5fe
```

Sources: [basic/trainer.py:1-74](), [basic/evaluator.py:1-423]()

## Training System Components

The training system is built around two main trainer classes that handle optimization and gradient computation for both single and multi-GPU scenarios.

### Core Training Classes

| Class | Purpose | Key Features |
|-------|---------|-------------|
| `Trainer` | Single-GPU training | Basic gradient computation and optimization |
| `MultiGPUTrainer` | Distributed training | Gradient averaging across multiple GPUs |

### Training Class Hierarchy

```mermaid
graph TD
    A["Trainer"] --> B["config: training parameters"]
    A --> C["model: Model instance"]  
    A --> D["opt: AdadeltaOptimizer"]
    A --> E["loss: model.get_loss()"]
    A --> F["train_op: apply_gradients"]
    
    G["MultiGPUTrainer"] --> H["models: list of Model instances"]
    G --> I["losses: per-GPU loss computation"]
    G --> J["grads_list: per-GPU gradients"]
    G --> K["average_gradients()"]
    
    L["Training Step Process"] --> M["get_feed_dict()"]
    M --> N["sess.run([loss, train_op])"]
    N --> O["return loss, summary"]
    
    style A fill:#f9f9f9
    style G fill:#f9f9f9
```

Sources: [basic/trainer.py:7-35](), [basic/trainer.py:36-74]()

The `Trainer` class handles single-GPU training with Adadelta optimization [basic/trainer.py:12](), while `MultiGPUTrainer` coordinates training across multiple GPUs using gradient averaging [basic/trainer.py:57]().

## Evaluation System Components

The evaluation system provides multiple evaluation strategies and metrics for assessing model performance on question answering tasks.

### Evaluation Class Architecture

```mermaid
graph TB
    subgraph "Evaluation Result Classes"
        A["Evaluation"] --> B["LabeledEvaluation"] 
        B --> C["AccuracyEvaluation"]
        C --> D["F1Evaluation"]
        A --> E["ForwardEvaluation"]
    end
    
    subgraph "Evaluator Classes"
        F["Evaluator"] --> G["LabeledEvaluator"]
        G --> H["AccuracyEvaluator"] 
        G --> I["F1Evaluator"]
        I --> J["MultiGPUF1Evaluator"]
        F --> K["ForwardEvaluator"]
    end
    
    subgraph "Key Methods"
        L["get_evaluation()"] --> M["sess.run() execution"]
        M --> N["metric computation"]
        N --> O["result aggregation"]
    end
    
    subgraph "Metrics Computed"
        P["accuracy: correct predictions"]
        Q["F1 score: span overlap"]
        R["exact match: perfect matches"]
        S["loss: cross-entropy"]
    end
    
    H --> P
    I --> Q
    I --> R
    C --> S
    
    style J fill:#f9f9f9
    style I fill:#f9f9f9
```

Sources: [basic/evaluator.py:11-48](), [basic/evaluator.py:99-119](), [basic/evaluator.py:236-333]()

### Evaluation Metrics and Processing

The evaluation system computes several key metrics:

- **Accuracy**: Exact match between predicted and ground truth answer spans [basic/evaluator.py:149-159]()
- **F1 Score**: Token-level overlap between predicted and ground truth spans [basic/evaluator.py:322-331]()
- **Loss**: Cross-entropy loss for training optimization [basic/evaluator.py:146]()

The `F1Evaluator` performs span extraction using `get_best_span()` [basic/evaluator.py:272]() and computes F1 scores using span overlap analysis [basic/evaluator.py:293]().

## Multi-GPU Training and Evaluation

The system provides comprehensive multi-GPU support for both training and evaluation phases.

### Multi-GPU Processing Flow

```mermaid
graph LR
    subgraph "Multi-GPU Training"
        A["MultiGPUTrainer"] --> B["GPU 0: model_0"]
        A --> C["GPU 1: model_1"] 
        A --> D["GPU N: model_N"]
        B --> E["gradients_0"]
        C --> F["gradients_1"]
        D --> G["gradients_N"]
        E --> H["average_gradients()"]
        F --> H
        G --> H
        H --> I["global parameter update"]
    end
    
    subgraph "Multi-GPU Evaluation"
        J["MultiGPUF1Evaluator"] --> K["GPU 0: yp_0, yp2_0"]
        J --> L["GPU 1: yp_1, yp2_1"]
        J --> M["GPU N: yp_N, yp2_N"]
        K --> N["tf.concat() predictions"]
        L --> N
        M --> N
        N --> O["combined F1 computation"]
    end
    
    style A fill:#f9f9f9
    style J fill:#f9f9f9
```

Sources: [basic/trainer.py:49-58](), [basic/evaluator.py:334-355]()

The `MultiGPUTrainer` distributes batches across GPUs and averages gradients [basic/trainer.py:57](), while `MultiGPUF1Evaluator` concatenates predictions from multiple GPUs [basic/evaluator.py:340-342]().

## Training and Evaluation Integration

The training and evaluation systems are integrated through the main orchestration system, which coordinates different execution modes.

### Execution Mode Integration

```mermaid
graph TD
    A["basic/main.py"] --> B["_train mode"]
    A --> C["_test mode"] 
    A --> D["_forward mode"]
    
    B --> E["MultiGPUTrainer.step()"]
    E --> F["gradient computation"]
    F --> G["parameter updates"]
    G --> H["periodic evaluation"]
    
    C --> I["MultiGPUF1Evaluator"]
    I --> J["F1 and accuracy metrics"]
    J --> K["performance assessment"]
    
    D --> L["ForwardEvaluator"]
    L --> M["answer prediction"]
    M --> N["id2answer_dict output"]
    
    H --> O["model checkpointing"]
    K --> P["evaluation summaries"]
    N --> Q["prediction files"]
    
    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#fff3e0
```

Sources: [basic/trainer.py:23-33](), [basic/evaluator.py:242-297](), [basic/evaluator.py:363-392]()

The system supports three primary execution modes:
- **Training mode**: Uses `MultiGPUTrainer` for model optimization
- **Test mode**: Uses `MultiGPUF1Evaluator` for performance assessment  
- **Forward mode**: Uses `ForwardEvaluator` for answer prediction generation

Each mode leverages the appropriate trainer or evaluator class to accomplish its specific objectives while maintaining consistent interfaces for model interaction and result processing.

---

