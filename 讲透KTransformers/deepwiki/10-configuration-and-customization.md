> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/10-configuration-and-customization](https://deepwiki.com/kvcache-ai/ktransformers/10-configuration-and-customization)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Configuration and Customization

  Relevant source files 
 - [doc/assets/DeepSeek-on-KTransformers.png](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/assets/DeepSeek-on-KTransformers.png)
 - [doc/en/Docker.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Docker.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md?plain=1)
 - [doc/en/SFT/injection_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1)
 - [doc/en/deepseek-v2-injection.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1)
 - [doc/en/kt-kernel/kt-kernel_intro.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/kt-kernel_intro.md?plain=1)
 - [doc/en/multi-gpu-tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/multi-gpu-tutorial.md?plain=1)
 
  This document provides a comprehensive reference for configuring KTransformers through YAML injection rules and server parameters. It covers the syntax and semantics of optimization rules, server configuration options for different deployment modes, and the underlying operator injection system that enables modular customization of model behavior.

 For deployment-specific guides, see [Inference Serving](https://deepwiki.com/kvcache-ai/ktransformers/6-inference-serving). For hardware-specific optimizations, see [Hardware Acceleration](https://deepwiki.com/kvcache-ai/ktransformers/7-hardware-acceleration). For model-specific configurations, see [Model Deployment Guides](https://deepwiki.com/kvcache-ai/ktransformers/9-model-deployment-guides).

 
## Purpose and Scope

 This page documents:

 
 - **YAML Optimization Rules**: Syntax for specifying module replacement, device placement, and operator selection.
 - **Server Configuration**: Parameters for `balance_serve`, `local_chat`, and SGLang integration.
 - **Injection Mechanism**: How rules are matched, applied, and extended with custom operators.
 
 
---

 
## YAML Optimization Rules

 YAML injection rules form the core configuration mechanism in KTransformers. Each rule specifies which modules in the model should be replaced with optimized operators, where they should execute (CPU/GPU), and which backend implementation to use.

 
### Rule Structure

 Every YAML rule consists of two primary sections: `match` and `replace`.

 
```

```

 **Sources:** [doc/en/deepseek-v2-injection.md66-161](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L66-L161) [doc/en/SFT/injection_tutorial.md18-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L18-L37)

 
### Match Criteria

 The `match` section identifies which modules to replace using one or both of the following:

 
| Criterion | Type | Description | Example |
|---|---|---|---|
| name | Regex string | Module name pattern in the model hierarchy | "^model\\.layers\\..*\\.self_attn$" |
| class | Python class path | Exact class type match | torch.nn.Linear |

 When both `name` and `class` are specified, modules must satisfy **both** conditions (logical AND). [doc/en/deepseek-v2-injection.md87-149](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L87-L149) [doc/en/SFT/injection_tutorial.md32](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L32-L32)

 
### Replace Specification

 The `replace` section defines the new operator and its configuration:

 
| Field | Required | Description |
|---|---|---|
| class | Yes | Fully-qualified class name of replacement operator |
| device | No | Initial device for module (e.g., "cpu", "cuda:0") |
| kwargs | No | Dictionary of initialization parameters |
| recursive | No | Whether to recursively inject submodules (default: true) |

 **Sources:** [doc/en/deepseek-v2-injection.md87-161](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L87-L161) [doc/en/SFT/injection_tutorial.md33-37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L33-L37)

 
### Device Placement Keywords

 Many operators support different execution strategies for prefill and generation phases [doc/en/deepseek-v2-injection.md99-121](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L99-L121):

 
```

```

 **Common operator backends:**

 
 - **CPU backends**: `KExpertsCPU`, `KLinearCPUInfer` (uses llamafile or AMX) [doc/en/deepseek-v2-injection.md39-40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L39-L40) [doc/en/SFT/injection_tutorial.md67-71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L67-L71)
 - **GPU backends**: `KExpertsMarlin`, `KLinearMarlin`, `KLinearFP8` (uses Marlin or Triton FP8 kernels) [doc/en/deepseek-v2-injection.md39-40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L39-L40) [doc/en/SFT/injection_tutorial.md65-70](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L65-L70)
 - **Torch fallback**: `KExpertsTorch`, `KLinearTorch` (standard PyTorch) [doc/en/SFT/injection_tutorial.md66-69](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L66-L69)
 
 
### Rule Priority and Ordering

 Rules are evaluated in **sequential order** from top to bottom. The **first matching rule** is applied to each module. Subsequent rules that match the same module are ignored [doc/en/multi-gpu-tutorial.md116](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/multi-gpu-tutorial.md?plain=1#L116-L116)

 
```

```

 **Sources:** [doc/en/multi-gpu-tutorial.md88-117](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/multi-gpu-tutorial.md?plain=1#L88-L117)

 
### Recursive Injection Control

 The `recursive` flag controls whether injection continues into submodules. Setting `recursive: False` is essential when replacing modules like `nn.ModuleList` (e.g., MoE experts) with custom wrappers like `KTransformersExperts`, as the wrapper handles all submodules internally [doc/en/deepseek-v2-injection.md106-121](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L106-L121) [doc/en/SFT/injection_tutorial.md103-113](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L103-L113)

 
---

 
## Server Configuration

 KTransformers supports multiple deployment backends, each with specific configuration parameters.

 
### Configuration File Structure

 
```

```

 **Sources:** [doc/en/kt-kernel/kt-kernel_intro.md140-148](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/kt-kernel_intro.md?plain=1#L140-L148) [doc/en/balance-serve.md114-134](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L134)

 
### Common Parameters

 These parameters apply across all deployment modes [doc/en/balance-serve.md114-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L125):

 
| Parameter | Type | Description | Example |
|---|---|---|---|
| --model_path | Path | Local directory containing model config files | /mnt/models/DeepSeek-V3 |
| --gguf_path | Path | Directory containing GGUF quantized weights | /mnt/models/DeepSeek-V3-GGUF/ |
| --optimize_config_path | Path | YAML file with injection rules | ktransformers/optimize/optimize_rules/DeepSeek-V3-Chat-serve.yaml |
| --cpu_infer | Integer | Number of CPU threads for inference | 62 |
| --max_new_tokens | Integer | Maximum output token length | 1024 |

 **Sources:** [doc/en/balance-serve.md114-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L125) [doc/en/Docker.md28](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Docker.md?plain=1#L28-L28)

 
### balance_serve Backend

 The `balance_serve` backend provides multi-concurrency support through asynchronous concurrent scheduling in C++, including continuous batching and chunked prefill.

 **Specific parameters [doc/en/balance-serve.md129-134](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L129-L134):**

 
 - `--backend_type`: Set to `balance_serve`.
 - `--max_batch_size`: Maximum number of requests processed in a single run by the engine.
 - `--chunk_size`: Maximum number of tokens processed in a single run.
 - `--cache_lens`: Total length of KV cache allocated by the scheduler (shared space).
 
 **Sources:** [doc/en/balance-serve.md114-134](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L134)

 
---

 
## Operator Injection System

 The injection system is the core mechanism that transforms standard Transformers models into optimized KTransformers models at load time [doc/en/deepseek-v2-injection.md66-74](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L66-L74)

 
### Injection Flow

 
```

```

 **Sources:** [doc/en/deepseek-v2-injection.md66-74](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L66-L74) [doc/en/SFT/injection_tutorial.md18-40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L18-L40)

 
### Key Operators

 
 - **`KDeepseekV2Attention`**: Optimized MLA operator that absorbs decompression matrices into weights, significantly reducing KV cache size [doc/en/deepseek-v2-injection.md31-32](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L31-L32) [doc/en/SFT/injection_tutorial.md72](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L72-L72)
 - **`KTransformersExperts`**: MoE expert wrapper supporting `KExpertsCPU` (llamafile/AMX) and `KExpertsMarlin` (GPU) backends [doc/en/deepseek-v2-injection.md39-40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L39-L40) [doc/en/SFT/injection_tutorial.md69-71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L69-L71)
 - **`KDeepseekV2Model`**: Top-level model wrapper that manages layer distribution across multiple GPUs via `transfer_map` [doc/en/multi-gpu-tutorial.md16-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/multi-gpu-tutorial.md?plain=1#L16-L26)
 - **`KTransformersLinearLora`**: Specialized operator for fine-tuning that inherits from both `KTransformersLinear` and `LoraLayer` to support LoRA parameters alongside high-performance paths [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md53-56](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L53-L56)
 
 **Sources:** [doc/en/deepseek-v2-injection.md31-40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/deepseek-v2-injection.md?plain=1#L31-L40) [doc/en/multi-gpu-tutorial.md16-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/multi-gpu-tutorial.md?plain=1#L16-L26) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md53-56](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L53-L56)

 For more details on specific configuration areas, see:

 
 - [Optimization Rules (YAML)](https://deepwiki.com/kvcache-ai/ktransformers/10.1-optimization-rules-(yaml))
 - [Server Configuration](https://deepwiki.com/kvcache-ai/ktransformers/10.2-server-configuration)
 - [Operator Injection System](https://deepwiki.com/kvcache-ai/ktransformers/10.3-operator-injection-system)
