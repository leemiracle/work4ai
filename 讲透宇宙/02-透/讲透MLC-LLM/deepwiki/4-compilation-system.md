> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/4-compilation-system](https://deepwiki.com/mlc-ai/mlc-llm/4-compilation-system)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Compilation System

  Relevant source files 
 - [docs/compilation/compile_models.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst)
 - [docs/compilation/convert_weights.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/convert_weights.rst)
 - [docs/deploy/cli.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst)
 - [docs/deploy/ios.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst)
 - [docs/deploy/mlc_chat_config.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/mlc_chat_config.rst)
 - [docs/index.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst)
 - [python/mlc_llm/compiler_pass/attach_softmax_with_temperature.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/compiler_pass/attach_softmax_with_temperature.py)
 - [python/mlc_llm/compiler_pass/fuse_add_norm.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/compiler_pass/fuse_add_norm.py)
 - [python/mlc_llm/conversation_template/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/conversation_template/__init__.py)
 - [python/mlc_llm/conversation_template/ministral3.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/conversation_template/ministral3.py)
 - [python/mlc_llm/interface/compile.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/compile.py)
 - [python/mlc_llm/interface/gen_config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/gen_config.py)
 - [python/mlc_llm/model/ministral3/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/ministral3/__init__.py)
 - [python/mlc_llm/model/ministral3/ministral3_loader.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/ministral3/ministral3_loader.py)
 - [python/mlc_llm/model/ministral3/ministral3_model.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/ministral3/ministral3_model.py)
 - [python/mlc_llm/model/model.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/model.py)
 - [python/mlc_llm/model/model_preset.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/model_preset.py)
 - [python/mlc_llm/model/vision/image_processing.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/vision/image_processing.py)
 - [python/mlc_llm/nn/rnn_state.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/nn/rnn_state.py)
 - [python/mlc_llm/op/batch_spec_verify.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/op/batch_spec_verify.py)
 - [python/mlc_llm/op/moe_matmul.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/op/moe_matmul.py)
 - [python/mlc_llm/op/moe_misc.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/op/moe_misc.py)
 - [python/mlc_llm/op/top_p_pivot.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/op/top_p_pivot.py)
 - [python/mlc_llm/quantization/block_scale_quantization.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/quantization/block_scale_quantization.py)
 - [python/mlc_llm/quantization/quantization.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/quantization/quantization.py)
 
  The MLC LLM Compilation System is a high-performance transformation pipeline that converts Large Language Models (LLMs) from standard formats (like Hugging Face PyTorch/Safetensors) into optimized, deployable artifacts. It leverages **TVM Unity** as its core compiler backend to perform graph-level and operator-level optimizations across diverse hardware targets including NVIDIA/AMD GPUs, Apple Metal, Vulkan, and WebGPU.

 
## 1. High-Level Workflow

 The compilation process is structured into a three-step pipeline that bridges the gap between raw model weights and an executable engine.

 
```

```

 
 - **`convert_weight`**: Extracts parameters from source formats and applies quantization (e.g., `q4f16_1`).
 - **`gen_config`**: Generates `mlc-chat-config.json`, which defines the conversation template, sliding window sizes, and hardware-specific settings like `prefill_chunk_size`. [python/mlc_llm/interface/gen_config.py90-146](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/gen_config.py#L90-L146)
 - **`compile`**: The core entry point that invokes the TVM compilation pipeline to produce the binary model library. [python/mlc_llm/interface/compile.py108-209](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/compile.py#L108-L209)
 
 Sources: [docs/compilation/compile_models.rst6-30](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L6-L30) [python/mlc_llm/interface/compile.py1-244](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/compile.py#L1-L244)

 
## 2. The `compile` Entrypoint

 The `compile` command orchestrates the transformation of a model defined in `nn.Module` (via `mlc_llm.model`) into an optimized `IRModule`. It uses the `CompileArgs` dataclass to manage inputs such as target device, optimization flags, and model overrides.

 
```

```

 Key components of the compilation call:

 
 - **Model Registry**: Models must be registered in the `MODELS` dictionary, mapping names to their `nn.Module` implementations (e.g., `LlamaForCausalLM`). [python/mlc_llm/model/model.py133-187](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/model.py#L133-L187)
 - **Quantization Registry**: Defines the bit-depth and algorithm (e.g., `GroupQuantize`, `BlockScaleQuantize`). [python/mlc_llm/quantization/quantization.py31-201](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/quantization/quantization.py#L31-L201)
 - **Target Detection**: Automatically detects the local GPU (CUDA, ROCm, Metal) if not explicitly provided.
 
 Sources: [python/mlc_llm/interface/compile.py27-60](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/compile.py#L27-L60) [python/mlc_llm/model/model.py87-123](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/model/model.py#L87-L123)

 
## 3. TVM Unity Pipeline

 The heart of the system is the `_mlc_llm_pipeline`, a multi-phase optimization sequence registered in TVM. It handles everything from high-level graph fusion to low-level kernel dispatch.

 
| Phase | Description | Key Passes |
|---|---|---|
| Phase 0 | Preparation | AttachSoftmaxWithTemperature, AttachGPUSamplingFunc, DispatchKVCacheCreation. |
| Phase 1 | Graph Optimizations | FuseDequantizeTranspose, BLASDispatch, FuseAddRMSNorm. |
| Phase 2 | TIR Lowering | LegalizeOps, FuseOps, AnnotateTIROpPattern. |
| Phase 3 | TIR Optimizations | FuseDequantizeMatmulEwise, DeadCodeElimination. |
| Phase 4 | Hardware Tuning | ApplyDefaultSchedule (DLight), LowBatchGemvSpecialize. |
| Phase 5 | Runtime Finalization | StaticPlanBlockMemory, RewriteCUDAGraph, VMShapeLower. |

 For details on specific passes, see [Compiler Pass Pipeline](https://deepwiki.com/mlc-ai/mlc-llm/4.2-compiler-pass-pipeline).

 Sources: [python/mlc_llm/compiler_pass/pipeline.py101-207](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/compiler_pass/pipeline.py#L101-L207) [python/mlc_llm/interface/compile.py168-202](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/compile.py#L168-L202)

 
## 4. Deployment Artifacts

 A successful compilation produces a structured directory (often under `dist/`) containing:

 
 - **Model Library**: A shared library (`.so`, `.dll`, `.dylib`) or `.wasm` file containing the compiled executable code for the model's `prefill`, `decode`, and `verify` functions. [docs/compilation/compile_models.rst119-121](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L119-L121)
 - **Weights**: Quantized parameters, typically stored as `.safetensors` files. [docs/compilation/compile_models.rst88-90](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L88-L90)
 - **Configuration**: `mlc-chat-config.json` which the runtime uses to initialize the engine, KV cache, and tokenizer. [python/mlc_llm/interface/gen_config.py128-146](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/gen_config.py#L128-L146)
 
 For details on how these are bundled for mobile or web, see [Packaging and Distribution](https://deepwiki.com/mlc-ai/mlc-llm/4.5-packaging-and-distribution).

 Sources: [docs/compilation/compile_models.rst6-14](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L6-L14) [python/mlc_llm/interface/gen_config.py1-20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/gen_config.py#L1-L20)

 
## Child Pages

 
 - [Model Configuration and Quantization](https://deepwiki.com/mlc-ai/mlc-llm/4.1-model-configuration-and-quantization) — Details on the `MODELS` and `QUANTIZATION` registries and `gen_config`.
 - [Compiler Pass Pipeline](https://deepwiki.com/mlc-ai/mlc-llm/4.2-compiler-pass-pipeline) — Deep dive into the `_mlc_llm_pipeline` and individual optimization passes.
 - [KV Cache and Neural Network Operators](https://deepwiki.com/mlc-ai/mlc-llm/4.3-kv-cache-and-neural-network-operators) — Technical details on `PagedKVCache` and specialized TIR operators.
 - [Model Architectures](https://deepwiki.com/mlc-ai/mlc-llm/4.4-model-architectures) — How to define new model architectures using the `nn.Module` frontend.
 - [Packaging and Distribution](https://deepwiki.com/mlc-ai/mlc-llm/4.5-packaging-and-distribution) — Platform-specific bundling for iOS, Android, and JIT compilation policies.
