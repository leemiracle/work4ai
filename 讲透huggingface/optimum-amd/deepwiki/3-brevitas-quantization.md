<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-amd · page 3 Brevitas Quantization · fetched 2026-10-26 -->

# Brevitas Quantization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/brevitas/usage_guide.mdx](docs/source/brevitas/usage_guide.mdx)
- [examples/quantization/brevitas/quantize_llm.py](examples/quantization/brevitas/quantize_llm.py)
- [optimum/amd/__init__.py](optimum/amd/__init__.py)
- [optimum/amd/brevitas/accelerate_utils.py](optimum/amd/brevitas/accelerate_utils.py)
- [optimum/amd/brevitas/configuration.py](optimum/amd/brevitas/configuration.py)
- [optimum/amd/brevitas/data_utils.py](optimum/amd/brevitas/data_utils.py)
- [optimum/amd/brevitas/quantizer.py](optimum/amd/brevitas/quantizer.py)

</details>



Brevitas Quantization is a neural network quantization system that provides advanced post-training quantization (PTQ) techniques for Large Language Models (LLMs) within the optimum-amd package. The system integrates AMD's Brevitas library with Hugging Face Transformers to enable efficient quantization of models for deployment on AMD hardware.

This page covers the quantization workflow, configuration options, and advanced techniques like GPTQ and SmoothQuant. For RyzenAI-specific quantization of vision models, see [RyzenAI Quantization](#2.2). For general AMD GPU support, see [ROCm GPU Support](#4).

## Core Components

The Brevitas quantization system consists of two primary classes and supporting utilities that handle the complete quantization workflow from model loading to ONNX export.

```mermaid
graph TD
    subgraph "Core Classes"
        BQ["BrevitasQuantizer<br/>(.quantizer.py:27)"]
        BQC["BrevitasQuantizationConfig<br/>(.configuration.py:9)"]
    end
    
    subgraph "Workflow Methods"
        BQ --> from_pretrained["from_pretrained()<br/>(.quantizer.py:40)"]
        BQ --> quantize["quantize()<br/>(.quantizer.py:108)"]
        from_pretrained --> load_model["TasksManager.get_model_from_task<br/>(.quantizer.py:90)"]
    end
    
    subgraph "Supporting Systems"
        data_utils["Data Utilities<br/>(.data_utils.py)"]
        accel_utils["Accelerate Integration<br/>(.accelerate_utils.py)"]
        export_utils["ONNX Export<br/>(.export.py)"]
    end
    
    subgraph "Configuration Parameters"
        BQC --> weights_config["weights_bitwidth<br/>weights_symmetric<br/>weights_quant_granularity"]
        BQC --> activations_config["activations_bitwidth<br/>activations_symmetric<br/>is_static"]
        BQC --> advanced_config["apply_gptq<br/>activations_equalization<br/>apply_weight_equalization"]
    end
    
    BQ --> data_utils
    BQ --> accel_utils
    quantize --> export_utils
    BQC --> BQ
```

Sources: [optimum/amd/brevitas/quantizer.py:27-106](), [optimum/amd/brevitas/configuration.py:9-142]()

### Class Architecture Mapping

The system architecture maps directly to specific code entities within the codebase, providing a clear connection between conceptual components and their implementation.

```mermaid
graph LR
    subgraph "Public API"
        API_BQ["BrevitasQuantizer"]
        API_BQC["BrevitasQuantizationConfig"]
    end
    
    subgraph "Implementation Files"
        quantizer_py["quantizer.py"]
        config_py["configuration.py"]
        data_utils_py["data_utils.py"]
        accel_utils_py["accelerate_utils.py"]
    end
    
    subgraph "Key Functions"
        apply_gptq["apply_gptq()<br/>(.quantizer.py:303)"]
        apply_act_equalization["apply_act_equalization()<br/>(.quantizer.py:276)"]
        apply_calibration["apply_calibration()<br/>(.quantizer.py:326)"]
        get_dataset_for_model["get_dataset_for_model()<br/>(.data_utils.py:217)"]
        offload_model["offload_model()<br/>(.accelerate_utils.py:383)"]
    end
    
    API_BQ --> quantizer_py
    API_BQC --> config_py
    quantizer_py --> apply_gptq
    quantizer_py --> apply_act_equalization
    quantizer_py --> apply_calibration
    data_utils_py --> get_dataset_for_model
    accel_utils_py --> offload_model
```

Sources: [optimum/amd/__init__.py:10-16](), [optimum/amd/brevitas/quantizer.py:303-338](), [optimum/amd/brevitas/data_utils.py:217-294]()

## Quantization Configuration

The `BrevitasQuantizationConfig` class controls all aspects of the quantization process through a comprehensive set of parameters that define precision, granularity, and advanced optimization techniques.

### Core Configuration Parameters

| Parameter Category | Key Options | Default Values | Purpose |
|-------------------|-------------|----------------|---------|
| **Weight Quantization** | `weights_bitwidth` | 8 | Bit precision for weights |
| | `weights_symmetric` | True | Symmetric vs asymmetric quantization |
| | `weights_quant_granularity` | "per_tensor" | Granularity level (per_tensor/per_channel/per_group) |
| **Activation Quantization** | `activations_bitwidth` | 8 | Bit precision for activations |
| | `is_static` | False | Static vs dynamic quantization |
| | `activations_symmetric` | False | Symmetric vs asymmetric quantization |
| **Advanced Techniques** | `apply_gptq` | False | Enable GPTQ algorithm |
| | `activations_equalization` | "cross_layer" | SmoothQuant type |
| | `apply_weight_equalization` | False | Cross-layer weight balancing |

Sources: [optimum/amd/brevitas/configuration.py:67-89](), [optimum/amd/brevitas/configuration.py:14-65]()

### Configuration Validation

The configuration system includes extensive validation logic to ensure parameter compatibility and prevent invalid combinations.

```mermaid
graph TD
    subgraph "Validation Rules"
        post_init["__post_init__()<br/>(.configuration.py:91)"]
        
        post_init --> check_static["Static + per_tensor only<br/>(.configuration.py:101)"]
        post_init --> check_mse_group["MSE incompatible with per_group<br/>(.configuration.py:106)"]
        post_init --> check_power_of_two["Power-of-two requires symmetric<br/>(.configuration.py:111)"]
        post_init --> check_asymmetric_group["Asymmetric per_group validation<br/>(.configuration.py:123)"]
    end
    
    subgraph "Auto-Configuration"
        post_init --> set_defaults["Set default group sizes<br/>(.configuration.py:92-96)"]
        post_init --> set_gptq_order["Set GPTQ act_order<br/>(.configuration.py:98)"]
        post_init --> disable_activations["Weights-only mode cleanup<br/>(.configuration.py:133)"]
    end
```

Sources: [optimum/amd/brevitas/configuration.py:91-142]()

## Quantization Workflow

The quantization process follows a structured workflow that applies various optimization techniques in a specific order to achieve optimal quantized model performance.

### Complete Quantization Pipeline

```mermaid
sequenceDiagram
    participant User
    participant BQ as "BrevitasQuantizer"
    participant Model as "PyTorch Model"
    participant Dataset as "Calibration Data"
    participant BrevitasLib as "Brevitas Library"

    User->>BQ: from_pretrained(model_name)
    BQ->>Model: Load via TasksManager
    
    User->>Dataset: get_dataset_for_model()
    Dataset->>Dataset: Load wikitext2/c4 data
    
    User->>BQ: quantize(config, dataset)
    
    alt FX Graph Required
        BQ->>Model: symbolic_trace()
    end
    
    alt Weight Equalization
        BQ->>BrevitasLib: apply_weight_equalization()
    end
    
    alt SmoothQuant
        BQ->>BrevitasLib: apply_act_equalization()
    end
    
    BQ->>BrevitasLib: quantize_model()
    
    alt GPTQ
        BQ->>BrevitasLib: apply_gptq()
    end
    
    alt Static Quantization
        BQ->>BrevitasLib: apply_calibration()
    end
    
    alt Bias Correction
        BQ->>BrevitasLib: apply_bias_correction()
    end
    
    BQ->>User: Return quantized model
```

Sources: [optimum/amd/brevitas/quantizer.py:108-250](), [examples/quantization/brevitas/quantize_llm.py:63-79]()

### Technique Application Order

The quantization techniques are applied in a carefully orchestrated sequence to maximize effectiveness:

1. **Weight Equalization** - Balances weight scales across layers [quantizer.py:180-183]()
2. **Activation Equalization (SmoothQuant)** - Rescales activations [quantizer.py:185-190]()
3. **Base Quantization** - Applies core quantization parameters [quantizer.py:199-222]()
4. **GPTQ** - Advanced weight optimization [quantizer.py:227-235]()
5. **Static Calibration** - For static activation quantization [quantizer.py:237-240]()
6. **Bias Correction** - Compensates for quantization bias [quantizer.py:242-248]()

Sources: [optimum/amd/brevitas/quantizer.py:180-250]()

## Advanced Quantization Techniques

### GPTQ Implementation

GPTQ (Generative Pre-trained Transformer Quantization) provides advanced weight quantization through iterative optimization based on the Hessian of the loss function.

```mermaid
graph TD
    subgraph "GPTQ Process"
        gptq_mode["gptq_mode()<br/>(.quantizer.py:312)"]
        
        gptq_mode --> iterate["Iterate through layers<br/>(.quantizer.py:319)"]
        iterate --> forward_pass["Forward pass with dataset<br/>(.quantizer.py:321)"]
        forward_pass --> update["gptq.update()<br/>(.quantizer.py:322)"]
        update --> iterate
    end
    
    subgraph "Configuration"
        act_order["act_order parameter<br/>Activation reordering"]
        parallel_layers["group_of_parallel_layers<br/>Parallel optimization"]
    end
    
    gptq_mode --> act_order
    gptq_mode --> parallel_layers
```

Sources: [optimum/amd/brevitas/quantizer.py:303-323]()

### SmoothQuant (Activation Equalization)

SmoothQuant redistributes quantization difficulty from activations to weights through mathematical equivalence transformations.

| Mode | Description | Requirements |
|------|-------------|--------------|
| `layerwise` | Applies rescaling as separate multiplication nodes | Standard PyTorch model |
| `cross_layer` | Fuses rescaling into preceding layers | FX-traced GraphModule |

The implementation uses different approaches based on the chosen mode:

```mermaid
graph LR
    subgraph "Layerwise Mode"
        layerwise["activation_equalization_mode<br/>layerwise=True"]
        layerwise --> mul_node["add_mul_node=True<br/>Separate rescaling"]
    end
    
    subgraph "Cross-layer Mode"
        cross_layer["activation_equalization_mode<br/>layerwise=False"]
        cross_layer --> fused["co_optimize_act_weights=True<br/>Fused rescaling"]
        cross_layer --> fx_required["Requires torch.fx.GraphModule"]
    end
```

Sources: [optimum/amd/brevitas/quantizer.py:276-300]()

## Data Utilities

### Dataset Management

The data utilities provide standardized calibration datasets for quantization with support for multiple dataset sources and preprocessing options.

```mermaid
graph TD
    subgraph "Dataset Sources"
        wikitext2["get_wikitext2()<br/>(.data_utils.py:101)"]
        c4["get_c4()<br/>(.data_utils.py:149)"]
    end
    
    subgraph "Processing Options"
        fuse_seq["fuse_sequences<br/>Concatenate short texts"]
        individual["Individual samples<br/>Preserve boundaries"]
    end
    
    subgraph "Main Interface"
        get_dataset["get_dataset_for_model()<br/>(.data_utils.py:217)"]
        get_dataset --> wikitext2
        get_dataset --> c4
        get_dataset --> fuse_seq
        get_dataset --> individual
    end
    
    subgraph "FX Graph Support"
        fx_support["Add past_key_values<br/>(.data_utils.py:268)"]
        get_dataset --> fx_support
    end
```

Sources: [optimum/amd/brevitas/data_utils.py:101-294]()

### Perplexity Evaluation

The system includes built-in perplexity computation for evaluating quantized model quality:

```python
perplexity = compute_perplexity(
    model=quantized_model,
    data=validation_dataset,
    context_length=args.seqlen // 2,
    tokenizer=tokenizer
)
```

The `compute_perplexity` function implements sliding window evaluation with cross-entropy loss calculation [data_utils.py:43-98]().

Sources: [optimum/amd/brevitas/data_utils.py:43-98](), [examples/quantization/brevitas/quantize_llm.py:66-70]()

## Memory Management Integration

### Accelerate Integration

The system integrates with Hugging Face Accelerate to handle large models that don't fit in single-device memory through sophisticated device mapping and offloading.

```mermaid
graph TD
    subgraph "Device Mapping"
        calc_gpu["calc_gpu_device_map()<br/>(.accelerate_utils.py:369)"]
        calc_cpu["calc_cpu_device_map()<br/>(.accelerate_utils.py:378)"]
        
        calc_gpu --> gpu_margin["GPU memory margins<br/>absolute + relative"]
        calc_cpu --> cpu_margin["CPU memory margins<br/>available memory"]
    end
    
    subgraph "Model Offloading"
        offload["offload_model()<br/>(.accelerate_utils.py:383)"]
        
        offload --> fx_check{"FX GraphModule?"}
        fx_check -->|Yes| infer_fx["infer_fx_auto_device_map<br/>(.accelerate_utils.py:39)"]
        fx_check -->|No| infer_regular["infer_auto_device_map<br/>Accelerate default"]
        
        infer_fx --> dispatch["dispatch_model()"]
        infer_regular --> dispatch
    end
    
    subgraph "FX Graph Handling"
        infer_fx --> offload_call_function["offload_call_function()<br/>(.accelerate_utils.py:258)"]
        offload_call_function --> align_devices["AlignDevicesHook<br/>for call_function nodes"]
    end
```

Sources: [optimum/amd/brevitas/accelerate_utils.py:369-454]()

### Hook Management

The integration provides specialized hook management for quantization workflows:

| Function | Purpose | Location |
|----------|---------|----------|
| `allocate_params()` | Move parameters to compute device | [accelerate_utils.py:423-434]() |
| `offload_params()` | Return parameters to storage | [accelerate_utils.py:436-446]() |
| `remove_hooks()` | Clean up all accelerate hooks | [accelerate_utils.py:314-331]() |

Sources: [optimum/amd/brevitas/accelerate_utils.py:314-454]()

## ONNX Export Integration

### Export Workflow

Brevitas quantized models can be exported to ONNX format using the optimum exporters framework with quantization-aware optimizations.

```mermaid
graph LR
    subgraph "Export Process"
        quantized_model["Quantized PyTorch Model"]
        
        quantized_model --> onnx_export["onnx_export_from_quantized_model<br/>(.export.py)"]
        onnx_export --> optimum_exporters["optimum.exporters<br/>ONNX conversion"]
        optimum_exporters --> quantized_onnx["Quantized ONNX Model"]
    end
    
    subgraph "Optimizations"
        quantized_onnx --> matmul_integer["MatMulInteger ops<br/>Hardware-optimized"]
        quantized_onnx --> qop_style["QOP-style quantization<br/>ONNX Runtime compatible"]
    end
```

The export process maintains quantization information and applies ONNX-specific optimizations for efficient inference on AMD hardware.

Sources: [optimum/amd/brevitas/export.py](), [examples/quantization/brevitas/quantize_llm.py:77-78](), [docs/source/brevitas/usage_guide.mdx:71-81]()

---

