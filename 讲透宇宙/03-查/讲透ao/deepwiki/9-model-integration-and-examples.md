<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/ao · page 9 Model Integration and Examples · fetched 2026-10-21 -->

# Model Integration and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmarks/quantization/calibration_based/create_quantized_model.py](benchmarks/quantization/calibration_based/create_quantized_model.py)
- [benchmarks/quantization/calibration_based/measure_accuracy_and_performance.sh](benchmarks/quantization/calibration_based/measure_accuracy_and_performance.sh)
- [benchmarks/quantization/calibration_based/utils.py](benchmarks/quantization/calibration_based/utils.py)
- [benchmarks/quantization/create_quantized_model.py](benchmarks/quantization/create_quantized_model.py)
- [benchmarks/quantization/eval_accuracy_and_perf_of_flux.py](benchmarks/quantization/eval_accuracy_and_perf_of_flux.py)
- [benchmarks/quantization/eval_accuracy_and_perf_of_flux.sh](benchmarks/quantization/eval_accuracy_and_perf_of_flux.sh)
- [benchmarks/quantization/measure_accuracy_and_performance.sh](benchmarks/quantization/measure_accuracy_and_performance.sh)
- [benchmarks/quantization/parse_log.py](benchmarks/quantization/parse_log.py)
- [benchmarks/quantization/utils.py](benchmarks/quantization/utils.py)
- [examples/sam2_amg_server/README.md](examples/sam2_amg_server/README.md)
- [examples/sam2_amg_server/compare_rle_lists.py](examples/sam2_amg_server/compare_rle_lists.py)
- [examples/sam2_amg_server/dog_rle.json](examples/sam2_amg_server/dog_rle.json)
- [examples/sam2_amg_server/server.py](examples/sam2_amg_server/server.py)
- [torchao/_models/sam2/automatic_mask_generator.py](torchao/_models/sam2/automatic_mask_generator.py)
- [torchao/_models/sam2/modeling/sam/mask_decoder.py](torchao/_models/sam2/modeling/sam/mask_decoder.py)
- [torchao/_models/sam2/sam2_image_predictor.py](torchao/_models/sam2/sam2_image_predictor.py)
- [torchao/_models/sam2/utils/amg.py](torchao/_models/sam2/utils/amg.py)
- [torchao/_models/sam2/utils/transforms.py](torchao/_models/sam2/utils/transforms.py)

</details>



This page demonstrates practical integration of TorchAO quantization with real models and frameworks. It focuses on the `quantize_()` API and configuration system, showing how to apply quantization to PyTorch models for inference and training workflows.

For detailed API reference, see [Quantization API Reference](#2). For tensor subclass internals, see [Tensor Subclass Framework](#3). For QAT and Float8 training, see [Quantization-Aware Training (QAT)](#4) and [Float8 Training System](#5).

## Using quantize_ with Models

The `quantize_()` function is the primary API for applying quantization to PyTorch models. It takes a model, a configuration object, and an optional filter function to control which modules are quantized.

**quantize_() Function Signature**

Title: quantize_ API and Configuration System

```mermaid
graph TB
    subgraph "API Entry Point"
        MODEL["nn.Module"] --> QUANTIZE["quantize_(model, config, filter_fn, device)"]
        CONFIG["AOBaseConfig subclass"] --> QUANTIZE
        FILTER["filter_fn(module, fqn) -> bool"] --> QUANTIZE
        DEVICE["device (optional)"] --> QUANTIZE
    end
    
    subgraph "Configuration Classes"
        QUANTIZE --> INT4["Int4WeightOnlyConfig"]
        QUANTIZE --> INT8WO["Int8WeightOnlyConfig"]
        QUANTIZE --> INT8DQ["Int8DynamicActivationInt8WeightConfig"]
        QUANTIZE --> FP8WO["Float8WeightOnlyConfig"]
        QUANTIZE --> FP8DQ["Float8DynamicActivationFloat8WeightConfig"]
        QUANTIZE --> INTX["Int8DynamicActivationIntxWeightConfig"]
    end
    
    subgraph "Handler Registration System"
        INT4 --> HANDLER["_QUANTIZE_CONFIG_HANDLER[type(config)]"]
        INT8WO --> HANDLER
        INT8DQ --> HANDLER
        HANDLER --> TRANSFORM["module transformation function"]
        TRANSFORM --> QMODULE["Quantized module"]
    end
    
    subgraph "Filter Function"
        FILTER --> ISLINEAR["_is_linear(mod, fqn)"]
        ISLINEAR --> CHECK["isinstance(mod, nn.Linear)"]
    end
```

Sources: [torchao/quantization/quant_api.py:431-504](), [torchao/quantization/quant_api.py:226-244](), [torchao/quantization/transform_module.py:94-96]()

The function signature is defined at [torchao/quantization/quant_api.py:431-445]() and uses a handler registry system at [torchao/quantization/transform_module.py:94]() to dispatch to the appropriate transformation function for each config type.

### Configuration Objects

Each quantization scheme has a corresponding configuration class that inherits from `AOBaseConfig`:

| Configuration Class | Purpose | Key Parameters |
|---------------------|---------|----------------|
| `Int4WeightOnlyConfig` | 4-bit weight quantization | `group_size`, `int4_packing_format`, `int4_choose_qparams_algorithm` |
| `Int8WeightOnlyConfig` | 8-bit weight quantization | `granularity`, `group_size` |
| `Int8DynamicActivationInt8WeightConfig` | Dynamic int8 quantization | `act_mapping_type` |
| `Int8DynamicActivationIntxWeightConfig` | Dynamic int8 act with 1-8 bit weights | `weight_dtype`, `weight_granularity`, `weight_mapping_type` |
| `Float8WeightOnlyConfig` | FP8 weight quantization | `granularity` |
| `Float8DynamicActivationFloat8WeightConfig` | FP8 dynamic quantization | `granularity` |

Sources: [torchao/quantization/quant_api.py:742-774](), [torchao/quantization/quant_api.py:939-963](), [torchao/quantization/quant_api.py:566-631](), [torchao/quantization/quant_api.py:1015-1095]()

### Per-Module Configuration with ModuleFqnToConfig

For fine-grained control, use `ModuleFqnToConfig` to apply different quantization schemes to different modules. This system supports exact FQN matches or regex patterns.

Title: Per-Module Quantization Configuration

```mermaid
graph LR
    subgraph "ModuleFqnToConfig"
        FQN["Module FQN"] --> LOOKUP["fqn_to_config dict"]
        LOOKUP --> DEFAULT["_default config"]
        LOOKUP --> EXACT["Exact match: 'linear1'"]
        LOOKUP --> REGEX["Regex match: 're:.*attn.*'"]
    end
    
    subgraph "Quantization Application"
        DEFAULT --> CONFIG1["Int4WeightOnlyConfig"]
        EXACT --> CONFIG2["Float8WeightOnlyConfig"]
        REGEX --> CONFIG3["Int8WeightOnlyConfig"]
        CONFIG1 --> TRANSFORM["Module transformation"]
        CONFIG2 --> TRANSFORM
        CONFIG3 --> TRANSFORM
    end
    
    subgraph "Precedence Rules"
        TRANSFORM --> RULE1["1. Exact FQN match"]
        RULE1 --> RULE2["2. Regex pattern match"]
        RULE2 --> RULE3["3. _default fallback"]
    end
```

Sources: [torchao/quantization/quant_api.py:1516-1668](), [benchmarks/quantization/eval_accuracy_and_perf_of_flux.py:26-28]()

For details on selective quantization and advanced configuration, see [Using quantize_ with Models](#9.1).

## LLM Inference Examples

TorchAO provides optimized pathways for LLM inference, including 4-bit and 8-bit quantization for models like Llama.

Title: LLM Model Quantization Workflow

```mermaid
graph TB
    subgraph "Model Preparation"
        LOAD["Load pretrained model"] --> MODEL["nn.Module (e.g., Llama)"]
        MODEL --> DTYPE["Convert to bfloat16/float16"]
    end
    
    subgraph "Quantization Step"
        DTYPE --> CONFIG["Select AOBaseConfig"]
        CONFIG --> INT4["Int4WeightOnlyConfig(group_size=32)"]
        CONFIG --> FP8["Float8DynamicActivationFloat8WeightConfig()"]
        CONFIG --> INT8["Int8DynamicActivationInt8WeightConfig()"]
        
        INT4 --> QUANTIZE["quantize_(model, config)"]
        FP8 --> QUANTIZE
        INT8 --> QUANTIZE
    end
    
    subgraph "Compilation & Inference"
        QUANTIZE --> QMODEL["Quantized model with AffineQuantizedTensor weights"]
        QMODEL --> COMPILE["torch.compile(model, mode='max-autotune')"]
        COMPILE --> INFERENCE["model(input_ids)"]
    end
```

Sources: [benchmarks/quantization/create_quantized_model.py:14-30](), [benchmarks/quantization/utils.py:25-54]()

Common LLM patterns include using `Int4WeightOnlyConfig` with HQQ for high compression or `Float8DynamicActivationFloat8WeightConfig` for modern hardware like H100. Benchmarks for models like Flux also demonstrate these patterns using specialized eval scripts [benchmarks/quantization/eval_accuracy_and_perf_of_flux.py:78-100]().

For details, see [LLM Inference Examples](#9.2).

## vLLM Integration

TorchAO is integrated as a quantization backend in vLLM for production model serving. This allows users to load models quantized with TorchAO directly into vLLM's high-performance inference engine.

Title: TorchAO + HuggingFace Integration Flow

```mermaid
graph TB
    subgraph "Configuration"
        CONFIG_CLS["TorchAoConfig"] --> QUANT_TYPE["quant_type parameter"]
        QUANT_TYPE --> INT4["Int4WeightOnlyConfig(...)"]
        QUANT_TYPE --> FP8["Float8DynamicActivationFloat8WeightConfig(granularity=PerRow())"]
        QUANT_TYPE --> INT8["Int8WeightOnlyConfig(...)"]
    end
    
    subgraph "Model Loading"
        INT4 --> FROM_PRETRAINED["AutoModelForCausalLM.from_pretrained()"]
        FP8 --> FROM_PRETRAINED
        INT8 --> FROM_PRETRAINED
        
        FROM_PRETRAINED --> ARGS["model_id, quantization_config, device_map"]
        ARGS --> LOADED["Model with quantized weights"]
    end
    
    subgraph "Serving Options"
        LOADED --> TRANSFORMERS["Direct transformers.generate()"]
        LOADED --> VLLM["vLLM serving"]
    end
```

Sources: [benchmarks/quantization/create_quantized_model.py:20-26](), [benchmarks/quantization/utils.py:11-22]()

The integration relies on `TorchAoConfig` [benchmarks/quantization/create_quantized_model.py:20]() which translates string-based or object-based recipes into TorchAO quantization commands during HuggingFace model loading.

For details, see [vLLM Integration](#9.3).

## Distributed Training Examples

TorchAO supports distributed training workflows using FSDP2, Tensor Parallelism (TP), and DDP. This enables training or fine-tuning quantized models at scale.

Title: FSDP2 + TorchAO Integration

```mermaid
graph TB
    subgraph "Model Setup"
        MODEL["nn.Module"] --> QUANTIZE["quantize_(model, config)"]
        QUANTIZE --> QMODEL["Model with AffineQuantizedTensor weights"]
    end
    
    subgraph "FSDP2 Wrapping"
        QMODEL --> FULLY_SHARD["fully_shard(model, mesh=DeviceMesh)"]
        FULLY_SHARD --> SHARDED["Sharded quantized model"]
    end
    
    subgraph "Training Loop"
        SHARDED --> FORWARD["forward pass"]
        FORWARD --> ALL_GATHER["All-gather shards"]
        ALL_GATHER --> COMPUTE["Compute on full tensor"]
        COMPUTE --> BACKWARD["backward pass"]
    end
```

Sources: [benchmarks/quantization/eval_accuracy_and_perf_of_flux.sh:8-27]()

Distributed examples include scaling Flux models with FP8 rowwise quantization [benchmarks/quantization/eval_accuracy_and_perf_of_flux.sh:8-13]() and MXFP8 [benchmarks/quantization/eval_accuracy_and_perf_of_flux.sh:16-19](). These workflows typically involve `torchrun` and multi-GPU configurations.

For details, see [Distributed Training Examples](#9.4).

## Computer Vision Integration (SAM2)

TorchAO also provides specialized optimizations for vision models like Segment Anything Model 2 (SAM2). These optimizations include `fast` (compiled) and `furious` (float16) modes to reduce latency and memory footprint for mask generation [examples/sam2_amg_server/server.py:23-28]().

| Optimization Mode | mIoU | Avg. Latency (ms) | Max Memory (MiB) |
|-------------------|------|-------------------|------------------|
| Baseline | 1.0 | 863 | 4013 |
| AO Optimized | 0.999 | 586 | 3257 |
| Fast + Furious | 0.981 | 120 | 13616 |

Sources: [examples/sam2_amg_server/README.md:50-57]()

The SAM2 server implementation [examples/sam2_amg_server/server.py:42-46]() utilizes `torch.compile` and TorchAO's image predictor [torchao/_models/sam2/sam2_image_predictor.py:19]() to achieve significant speedups in real-world server environments.

---

