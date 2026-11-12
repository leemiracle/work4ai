<!-- source: DeepWiki mcp.deepwiki.com · repo intel/neural-compressor · page 7 Advanced Techniques · fetched 2026-10-21 -->

# Advanced Techniques

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/quantization_weight_only.md](docs/source/quantization_weight_only.md)
- [neural_compressor/adaptor/pytorch.py](neural_compressor/adaptor/pytorch.py)
- [neural_compressor/adaptor/pytorch_cpu.yaml](neural_compressor/adaptor/pytorch_cpu.yaml)
- [neural_compressor/adaptor/pytorch_ipex.yaml](neural_compressor/adaptor/pytorch_ipex.yaml)
- [neural_compressor/adaptor/torch_utils/awq.py](neural_compressor/adaptor/torch_utils/awq.py)
- [neural_compressor/adaptor/torch_utils/bf16_convert.py](neural_compressor/adaptor/torch_utils/bf16_convert.py)
- [neural_compressor/adaptor/torch_utils/model_wrapper.py](neural_compressor/adaptor/torch_utils/model_wrapper.py)
- [neural_compressor/adaptor/torch_utils/teq.py](neural_compressor/adaptor/torch_utils/teq.py)
- [neural_compressor/adaptor/torch_utils/util.py](neural_compressor/adaptor/torch_utils/util.py)
- [neural_compressor/adaptor/torch_utils/weight_only.py](neural_compressor/adaptor/torch_utils/weight_only.py)
- [neural_compressor/algorithm/smooth_quant.py](neural_compressor/algorithm/smooth_quant.py)
- [neural_compressor/benchmark.py](neural_compressor/benchmark.py)
- [neural_compressor/config.py](neural_compressor/config.py)
- [neural_compressor/mix_precision.py](neural_compressor/mix_precision.py)
- [neural_compressor/model/model.py](neural_compressor/model/model.py)
- [neural_compressor/model/torch_model.py](neural_compressor/model/torch_model.py)
- [neural_compressor/quantization.py](neural_compressor/quantization.py)
- [neural_compressor/training.py](neural_compressor/training.py)
- [neural_compressor/utils/pytorch.py](neural_compressor/utils/pytorch.py)
- [neural_compressor/utils/utility.py](neural_compressor/utils/utility.py)
- [test/adaptor/pytorch_adaptor/test_adaptor_pytorch_2x.py](test/adaptor/pytorch_adaptor/test_adaptor_pytorch_2x.py)
- [test/adaptor/pytorch_adaptor/test_adaptor_security.py](test/adaptor/pytorch_adaptor/test_adaptor_security.py)
- [test/algorithm/test_smooth_quant.py](test/algorithm/test_smooth_quant.py)
- [test/ipex/test_adaptor_ipex.py](test/ipex/test_adaptor_ipex.py)
- [test/quantization/test_weight_only_quantization.py](test/quantization/test_weight_only_quantization.py)
- [test/utils/test_huggingface.py](test/utils/test_huggingface.py)

</details>



## Purpose and Scope

This page provides an overview of advanced optimization methods available in Intel® Neural Compressor that go beyond standard quantization approaches. These techniques can be used standalone or combined with quantization to achieve better accuracy-performance trade-offs.

For basic quantization methods (PTQ, QAT, weight-only), see [Quantization Techniques](#6). For framework-specific implementation details, see [Framework Adaptors](#5).

## Overview

Advanced techniques in Neural Compressor address specific challenges in model optimization:

- **SmoothQuant**: Mitigates accuracy degradation in activation quantization by balancing the difficulty between weights and activations
- **Pruning**: Reduces model size by removing redundant weights
- **Distillation**: Transfers knowledge from a larger teacher model to maintain accuracy in compressed models

These techniques integrate seamlessly with the 2.x API's accuracy-aware tuning system and can be orchestrated together for multi-objective optimization.

## Technique Categories

### Transformation-Based Techniques

SmoothQuant operates as a pre-quantization transformation that modifies the model's numeric properties without changing its architecture. It can be applied before any quantization method to improve final accuracy.

### Training-Based Techniques

Pruning and distillation require model retraining with specialized callbacks. The `CompressionManager` class orchestrates these techniques during the training loop.

## System Architecture

```mermaid
graph TB
    subgraph "User Configuration"
        Recipe["recipes dict<br/>smooth_quant: bool<br/>smooth_quant_args: dict"]
        QATConfig["QuantizationAwareTrainingConfig"]
        PruneConfig["WeightPruningConfig"]
        DistillConfig["DistillationConfig"]
    end
    
    subgraph "Advanced Techniques Layer"
        SQ["TorchSmoothQuant<br/>activation-weight balancing"]
        CM["CompressionManager<br/>orchestration"]
        Callbacks["Callbacks System<br/>QATCallbacks<br/>PruningCallbacks<br/>DistillationCallbacks"]
    end
    
    subgraph "Integration Points"
        PreQuant["Pre-Quantization<br/>Transform model"]
        DuringQuant["During Quantization<br/>QAT workflow"]
        PostQuant["Post-Quantization<br/>Combined optimization"]
    end
    
    subgraph "Quantization System"
        Adaptor["Framework Adaptor<br/>PyTorch/TF/ONNX"]
        Strategy["Strategy System<br/>Tuning loop"]
        Model["Quantized Model"]
    end
    
    Recipe --> SQ
    QATConfig --> CM
    PruneConfig --> CM
    DistillConfig --> CM
    
    SQ --> PreQuant
    CM --> DuringQuant
    CM --> Callbacks
    
    PreQuant --> Adaptor
    DuringQuant --> Adaptor
    Callbacks --> Strategy
    
    Adaptor --> Model
    Strategy --> Model
    
    PostQuant --> Model
```

**Sources:** [neural_compressor/adaptor/torch_utils/waq/__init__.py](), [neural_compressor/training.py:38-62](), [neural_compressor/config.py:729-744]()

## Technique Integration Patterns

### Pattern 1: SmoothQuant + PTQ

SmoothQuant transforms the model before static quantization calibration:

| Step | Component | Action |
|------|-----------|--------|
| 1 | Configuration | Set `recipes={'smooth_quant': True}` |
| 2 | `TorchSmoothQuant` | Analyze activation distributions |
| 3 | `TorchSmoothQuant.transform()` | Apply channel-wise scaling |
| 4 | Adaptor | Perform standard PTQ calibration |
| 5 | Strategy | Tune with accuracy criterion |

### Pattern 2: QAT + Pruning + Distillation (Orchestration)

Multiple techniques are orchestrated during training:

| Step | Component | Action |
|------|-----------|--------|
| 1 | `prepare_compression()` | Create `CompressionManager` |
| 2 | `CompressionManager.callbacks` | Register all technique callbacks |
| 3 | Training loop | Execute callbacks at lifecycle points |
| 4 | `on_step_begin()` | Apply pruning masks |
| 5 | `on_after_compute_loss()` | Add distillation loss |
| 6 | Convert | Apply QAT quantization |

**Sources:** [neural_compressor/training.py:38-130](), [neural_compressor/compression/callbacks.py]()

## Configuration System

```mermaid
graph LR
    subgraph "SmoothQuant Config"
        R1["recipes dict"]
        SQKey["smooth_quant: True"]
        SQArgs["smooth_quant_args:<br/>alpha: float or 'auto'<br/>folding: bool<br/>op_types: list"]
        
        R1 --> SQKey
        R1 --> SQArgs
    end
    
    subgraph "Orchestration Config"
        Configs["List of Configs"]
        C1["QuantizationAwareTrainingConfig"]
        C2["WeightPruningConfig<br/>pruning_type<br/>target_sparsity<br/>start_step/end_step"]
        C3["DistillationConfig<br/>teacher_model<br/>criterion"]
        
        Configs --> C1
        Configs --> C2
        Configs --> C3
    end
    
    subgraph "Application"
        PTQFit["quantization.fit()<br/>with recipes"]
        PrepComp["prepare_compression()<br/>with config list"]
        
        R1 --> PTQFit
        Configs --> PrepComp
    end
```

**Sources:** [neural_compressor/config.py:715-859](), [neural_compressor/training.py:285-357]()

## Key Classes and Functions

### SmoothQuant Implementation

The `TorchSmoothQuant` class implements the transformation algorithm:

```
TorchSmoothQuant(model, dataloader)
├── __init__: Initialize with model and calibration data
├── transform: Main entry point
│   ├── alpha: Balancing factor (0.0-1.0 or "auto")
│   ├── calib_iter: Number of calibration iterations
│   └── folding: Whether to fold scaling into weights
├── _get_all_hook_module_names: Identify quantizable modules
├── _adjust_parameters: Apply channel-wise scaling
└── absorb_to_layer: Dict of absorption relationships
```

### Compression Manager

The `CompressionManager` orchestrates multiple techniques:

```
CompressionManager
├── __init__(model, confs): Initialize with configs
├── callbacks: Combined callback object
│   ├── on_train_begin()
│   ├── on_epoch_begin(epoch)
│   ├── on_step_begin(batch)
│   ├── on_after_compute_loss(input, output, loss)
│   ├── on_before_optimizer_step()
│   └── on_train_end()
├── model: Wrapped/prepared model
├── _optimizer_parameters: Parameters to optimize
└── prune(): Apply pruning (if configured)
```

**Sources:** [neural_compressor/adaptor/torch_utils/waq/waq.py:1-100](), [neural_compressor/training.py:38-264]()

## Execution Flow Diagrams

### SmoothQuant Transformation Flow

```mermaid
sequenceDiagram
    participant User
    participant Config as PostTrainingQuantConfig
    participant Fit as quantization.fit
    participant Adaptor as PyTorchAdaptor
    participant SQ as TorchSmoothQuant
    participant Model
    
    User->>Config: recipes={'smooth_quant': True}
    User->>Fit: fit(model, config, dataloader)
    Fit->>Adaptor: quantize(model, tune_cfg)
    
    alt SmoothQuant enabled
        Adaptor->>SQ: __init__(model, dataloader)
        Adaptor->>SQ: transform(alpha, folding)
        SQ->>Model: Hook activation collection
        loop Calibration
            SQ->>Model: forward(batch)
            Model-->>SQ: activation statistics
        end
        SQ->>SQ: Calculate scale factors
        SQ->>Model: Apply weight scaling
        alt folding=True
            SQ->>Model: Absorb scales into weights
        else folding=False
            SQ->>Model: Insert SQLinearWrapper
        end
        Model-->>Adaptor: Transformed model
    end
    
    Adaptor->>Model: Standard quantization
    Model-->>User: Quantized model
```

**Sources:** [neural_compressor/adaptor/pytorch.py:1175-1250](), [test/algorithm/test_smooth_quant.py:732-777]()

### Orchestration Training Flow

```mermaid
sequenceDiagram
    participant User
    participant PrepComp as prepare_compression
    participant CM as CompressionManager
    participant Callbacks
    participant Model
    participant Optimizer
    
    User->>PrepComp: prepare_compression(model, [configs])
    PrepComp->>CM: Create manager
    CM->>Callbacks: Combine all callbacks
    CM-->>User: manager with model
    
    User->>Callbacks: on_train_begin()
    Callbacks->>Model: Prepare for QAT/pruning
    
    loop Training Loop
        User->>Callbacks: on_epoch_begin(epoch)
        
        loop Batch Loop
            User->>Callbacks: on_step_begin(batch)
            Callbacks->>Model: Apply pruning masks
            
            User->>Model: forward(input)
            Model-->>User: output
            User->>User: compute_loss(output, target)
            
            User->>Callbacks: on_after_compute_loss(input, output, loss)
            Callbacks->>Callbacks: Add distillation loss
            Callbacks-->>User: modified_loss
            
            User->>User: loss.backward()
            User->>Callbacks: on_before_optimizer_step()
            User->>Optimizer: step()
            
            Callbacks->>Callbacks: Update pruning schedule
        end
        
        User->>Callbacks: on_epoch_end()
    end
    
    User->>Callbacks: on_train_end()
    Callbacks->>Model: Convert to quantized
```

**Sources:** [neural_compressor/training.py:285-357](), [neural_compressor/compression/callbacks.py]()

## Integration with Tuning System

Advanced techniques interact with the 2.x API's accuracy-aware tuning:

| Technique | Tuning Integration | Impact |
|-----------|-------------------|--------|
| **SmoothQuant** | Pre-processes model before tuning space exploration | Reduces tuning search space by improving baseline accuracy |
| **QAT** | Can be tuned with different observer/qconfig settings | Strategy samples different QAT configurations |
| **Pruning** | Sparsity level can be part of tuning space | MultiObjective evaluates accuracy vs model size |
| **Distillation** | Temperature/criterion can be tuned | Usually fixed during tuning, applied in orchestration |

The `Strategy` system can explore different combinations of these techniques when configured with appropriate tuning criteria.

**Sources:** [neural_compressor/strategy/strategy.py](), [neural_compressor/quantization.py:33-159]()

## Usage Examples

### Example 1: SmoothQuant with Auto Alpha Search

```python
from neural_compressor import PostTrainingQuantConfig, quantization

conf = PostTrainingQuantConfig(
    calibration_sampling_size=100,
    recipes={
        'smooth_quant': True,
        'smooth_quant_args': {
            'alpha': 'auto',  # Search for optimal alpha
            'folding': True,   # Absorb scales into weights
        }
    }
)

q_model = quantization.fit(
    model, 
    conf, 
    calib_dataloader=calib_dataloader,
    eval_func=eval_func  # Optional: for accuracy-aware tuning
)
```

### Example 2: Orchestrated Optimization

```python
from neural_compressor import (
    QuantizationAwareTrainingConfig,
    WeightPruningConfig,
    DistillationConfig
)
from neural_compressor.training import prepare_compression

configs = [
    QuantizationAwareTrainingConfig(approach='qat'),
    WeightPruningConfig(target_sparsity=0.5, start_step=0, end_step=1000),
    DistillationConfig(teacher_model=teacher_model)
]

compression_manager = prepare_compression(model, configs)
model = compression_manager.model

for epoch in range(epochs):
    compression_manager.callbacks.on_epoch_begin(epoch)
    for batch, label in dataloader:
        compression_manager.callbacks.on_step_begin(batch)
        output = model(batch)
        loss = criterion(output, label)
        loss = compression_manager.callbacks.on_after_compute_loss(
            batch, output, loss
        )
        loss.backward()
        compression_manager.callbacks.on_before_optimizer_step()
        optimizer.step()
```

**Sources:** [test/algorithm/test_smooth_quant.py:752-811](), [neural_compressor/training.py:359-420]()

## Technical Considerations

### SmoothQuant Limitations

- Only applicable to models with paired layers (e.g., Linear→LayerNorm→Linear)
- Requires calibration data to analyze activation distributions
- `alpha="auto"` increases calibration time but improves accuracy
- Folding may not be possible if scales cannot be absorbed by preceding layers

### Orchestration Constraints

- Not all technique combinations are compatible (e.g., dynamic quantization + pruning)
- Callbacks must be called in correct order: `on_step_begin` → forward → loss → `on_after_compute_loss` → backward → `on_before_optimizer_step` → optimizer step
- Some techniques require specific framework versions (QAT requires PyTorch ≥1.8)
- Memory overhead during training when combining multiple techniques

**Sources:** [neural_compressor/adaptor/torch_utils/waq/waq.py:150-250](), [neural_compressor/training.py:38-130]()

## Next Steps

- For detailed SmoothQuant algorithm, configuration options, and examples, see [SmoothQuant](#7.1)
- For pruning methods, distillation techniques, and orchestration modes, see [Pruning and Distillation](#7.2)
- For integration with specific frameworks, see [Framework Adaptors](#5)

---

