> 来源: [https://deepwiki.com/sgl-project/sglang/19-advanced-features](https://deepwiki.com/sgl-project/sglang/19-advanced-features)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Advanced Features

  Relevant source files 
 - [python/sglang/srt/constrained/base_grammar_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/base_grammar_backend.py)
 - [python/sglang/srt/constrained/grammar_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/grammar_manager.py)
 - [python/sglang/srt/constrained/llguidance_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/llguidance_backend.py)
 - [python/sglang/srt/constrained/outlines_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/outlines_backend.py)
 - [python/sglang/srt/constrained/reasoner_grammar_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/reasoner_grammar_backend.py)
 - [python/sglang/srt/constrained/xgrammar_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/xgrammar_backend.py)
 - [python/sglang/srt/layers/moe/moe_runner/triton.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/moe/moe_runner/triton.py)
 - [python/sglang/srt/lora/backend/ascend_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/ascend_backend.py)
 - [python/sglang/srt/lora/backend/base_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/base_backend.py)
 - [python/sglang/srt/lora/backend/chunked_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/chunked_backend.py)
 - [python/sglang/srt/lora/backend/torch_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/torch_backend.py)
 - [python/sglang/srt/lora/backend/triton_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/triton_backend.py)
 - [python/sglang/srt/lora/layers.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/layers.py)
 - [python/sglang/srt/lora/lora.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora.py)
 - [python/sglang/srt/lora/lora_config.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_config.py)
 - [python/sglang/srt/lora/lora_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py)
 - [python/sglang/srt/lora/lora_moe_runners.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_moe_runners.py)
 - [python/sglang/srt/lora/mem_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/mem_pool.py)
 - [python/sglang/srt/lora/torch_ops/__init__.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/torch_ops/__init__.py)
 - [python/sglang/srt/lora/torch_ops/graph_lora_ops.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/torch_ops/graph_lora_ops.py)
 - [python/sglang/srt/lora/torch_ops/lora_ops.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/torch_ops/lora_ops.py)
 - [python/sglang/srt/lora/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/utils.py)
 - [test/manual/lora/test_lora_ops.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/lora/test_lora_ops.py)
 - [test/manual/lora/test_torch_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/lora/test_torch_backend.py)
 - [test/registered/unit/constrained/test_base_grammar_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_base_grammar_backend.py)
 - [test/registered/unit/constrained/test_grammar_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_grammar_manager.py)
 - [test/registered/unit/constrained/test_llguidance_batched_mask.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_llguidance_batched_mask.py)
 - [test/registered/unit/constrained/test_reasoner_grammar_backend.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_reasoner_grammar_backend.py)
 - [test/registered/unit/constrained/test_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/constrained/test_utils.py)
 
  
## Purpose and Scope

 This document covers advanced features and capabilities in SGLang that extend beyond basic text generation. These features enable production deployments, multi-tenant serving, structured output generation, and robust monitoring workflows.

 For basic model configuration and loading, see [Model Configuration and Loading](https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading). For parallelism and distributed execution, see [Distributed Execution Strategies](https://deepwiki.com/sgl-project/sglang/6-distributed-execution-strategies). For multimodal capabilities, see [Multimodal and Vision-Language Models](https://deepwiki.com/sgl-project/sglang/18-multimodal-and-vision-language-models).

 
## Overview

 SGLang provides seven major categories of advanced features:

 
| Feature Category | Key Capabilities | Primary Use Cases |
|---|---|---|
| LoRA Adapter Support (LoRA Adapter Support) | Multi-tenant serving with dynamic adapter loading, memory pooling, and MoE integration | Serving multiple fine-tuned models from a single base model |
| Constrained Output (Constrained and Structured Output) | JSON schema, regex, EBNF grammar enforcement via xgrammar, outlines, or llguidance | Structured API responses, function calling, data extraction |
| Observability (Observability and Monitoring) | Prometheus metrics, request tracing, and performance monitoring | Production monitoring, debugging, performance analysis |
| Session Management (Session Management) | Stateful multi-turn conversations with context persistence | Chatbots, interactive applications, prefix caching |
| Function Calling (Function Calling and Tool Use) | Tool use, model-specific detectors, and reasoning parsing | Agentic workflows and tool integration |
| Diffusion LLM (Diffusion LLM (DLLM) Support) | Support for discrete diffusion models (LLaDA, SDAR) | Masked language modeling and denoising generation |
| RL Integration (RL Integration and Advanced Engine Features) | Engine sleep/wake, weight refit, and partial rollouts | Reinforcement Learning from Human Feedback (RLHF) and online training |

 
## Architecture Integration

 The following diagram shows how these advanced features integrate with SGLang's core architecture and specific code entities:

 Title: Advanced Features Integration Map

 
```

```

 **Sources:**

 
 - [python/sglang/srt/lora/lora_manager.py65-117](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L65-L117)
 - [python/sglang/srt/lora/mem_pool.py131-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/mem_pool.py#L131-L198)
 - [python/sglang/srt/constrained/grammar_manager.py26-40](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/grammar_manager.py#L26-L40)
 - [python/sglang/srt/constrained/xgrammar_backend.py73-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/xgrammar_backend.py#L73-L83)
 
 
## Configuration Interface

 Advanced features are configured through `ServerArgs` parameters. Key configuration options include:

 
| Parameter | Type | Default | Description |
|---|---|---|---|
| lora_paths | List[LoRARef] | None | Paths to LoRA adapters to load |
| max_loras_per_batch | int | 8 | Max adapters in a single forward pass |
| lora_backend | str | "triton" | Backend for LoRA kernels (triton, csgmv, torch_native) |
| grammar_backend | str | "xgrammar" | Constrained decoding engine |
| enable_metrics | bool | False | Enable Prometheus metrics |

 **Sources:**

 
 - [python/sglang/srt/lora/lora_manager.py70-79](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L70-L79)
 - [python/sglang/srt/lora/lora_manager.py101-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L101-L107)
 - [python/sglang/srt/constrained/grammar_manager.py28-32](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/grammar_manager.py#L28-L32)
 
 
## Feature-Specific Implementation Details

 
### LoRA Adapter Support

 The `LoRAManager` [python/sglang/srt/lora/lora_manager.py65-124](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L65-L124) handles the lifecycle of adapters, integrating techniques from S-LoRA and Punica [python/sglang/srt/lora/lora_manager.py15-16](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L15-L16) It uses a `LoRAMemoryPool` [python/sglang/srt/lora/mem_pool.py131-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/mem_pool.py#L131-L198) to manage pre-allocated GPU buffers for LoRA weights. The system supports specialized LoRA-aware MoE buffers via `init_cuda_graph_batch_info` [python/sglang/srt/lora/lora_manager.py126-139](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L126-L139) For MoE models, it utilizes `LoRAHooks` to inject deltas at projection points [python/sglang/srt/lora/lora_moe_runners.py195-203](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_moe_runners.py#L195-L203) It also supports embedding LoRA via `VocabParallelEmbeddingWithLoRA` [python/sglang/srt/lora/layers.py84-131](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/layers.py#L84-L131)

 
### Constrained and Structured Output

 SGLang supports multiple backends for grammar-constrained generation via the `GrammarManager` [python/sglang/srt/constrained/grammar_manager.py26-61](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/grammar_manager.py#L26-L61) The `BaseGrammarBackend` provides the foundation for backends like `XGrammar` [python/sglang/srt/constrained/xgrammar_backend.py73-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/xgrammar_backend.py#L73-L83) The system also includes a `ReasonerGrammarObject` [python/sglang/srt/constrained/reasoner_grammar_backend.py35-72](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/reasoner_grammar_backend.py#L35-L72) to manage phases for reasoning models (e.g., DeepSeek R1), allowing strict token filtering during "thinking" phases and grammar enforcement during "generation" phases [python/sglang/srt/constrained/reasoner_grammar_backend.py83-118](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/reasoner_grammar_backend.py#L83-L118)

 
### Observability and Monitoring

 Performance monitoring includes `GrammarStats` [python/sglang/srt/constrained/base_grammar_backend.py39-49](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/base_grammar_backend.py#L39-L49) to track compilation and tree traversal times for constrained decoding. The `GrammarManager` handles asynchronous grammar compilation and synchronization across Data Parallel (DP) and Pipeline Parallel (PP) groups [python/sglang/srt/constrained/grammar_manager.py48-54](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/grammar_manager.py#L48-L54)

 
### Function Calling and Tool Use

 The system handles complex agentic workflows using model-specific tool call parsers and reasoning detectors via `ReasoningParser` [python/sglang/srt/parser/reasoning_parser.py23-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/parser/reasoning_parser.py#L23-L25) These components parse model outputs to identify structured tool invocations and separate reasoning chains from final responses.

 
### RL Integration

 For Reinforcement Learning, SGLang supports weight refitting and partial rollouts. This allows for efficient online inference during RLHF training loops. The engine supports deterministic sampling via `sampling_seed` and provides hooks for post-training framework integrations like verl or slime.

 
## Code Entity Mapping

 The following diagram bridges the conceptual "Natural Language" space of features to the specific "Code Entity" space within the repository:

 Title: Conceptual to Code Entity Mapping

 
```

```

 **Sources:**

 
 - [python/sglang/srt/lora/lora_manager.py65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_manager.py#L65-L65)
 - [python/sglang/srt/lora/mem_pool.py131](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/mem_pool.py#L131-L131)
 - [python/sglang/srt/constrained/base_grammar_backend.py202](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/base_grammar_backend.py#L202-L202)
 - [python/sglang/srt/constrained/reasoner_grammar_backend.py35](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/reasoner_grammar_backend.py#L35-L35)
 - [python/sglang/srt/lora/lora_moe_runners.py195](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_moe_runners.py#L195-L195)
 - [python/sglang/srt/lora/backend/triton_backend.py26](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/triton_backend.py#L26-L26)
 
 
## Performance Considerations

 
 - **LoRA Overhead**: SGLang uses specialized backends like `TritonLoRABackend` [python/sglang/srt/lora/backend/triton_backend.py26-36](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/triton_backend.py#L26-L36) and `TorchNativeLoRABackend` [python/sglang/srt/lora/backend/torch_backend.py34-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/torch_backend.py#L34-L43) to minimize the overhead of multi-adapter serving.
 - **MoE LoRA Alignment**: For MoE models, SGLang uses rank-aware block configurations [python/sglang/srt/lora/lora_moe_runners.py43-60](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_moe_runners.py#L43-L60) and a CPU-based fallback `_naive_moe_lora_align_block_size` [python/sglang/srt/lora/lora_moe_runners.py66-146](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/lora_moe_runners.py#L66-L146) for small batches to align tokens with their respective experts and LoRA adapters.
 - **CUDA Graphs**: LoRA operations are integrated with CUDA graphs via `init_cuda_graph_batch_info` [python/sglang/srt/lora/backend/triton_backend.py159-180](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/triton_backend.py#L159-L180)
 - **Constrained Decoding**: Backends implement `fill_vocab_mask` [python/sglang/srt/constrained/xgrammar_backend.py119-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/xgrammar_backend.py#L119-L120) and `apply_vocab_mask` [python/sglang/srt/constrained/xgrammar_backend.py126-143](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/constrained/xgrammar_backend.py#L126-L143) to efficiently apply bitmasks to the logits during generation.
 
 For details, see:

 
 - [LoRA Adapter Support](https://deepwiki.com/sgl-project/sglang/19.1-lora-adapter-support)
 - [Constrained and Structured Output](https://deepwiki.com/sgl-project/sglang/19.2-constrained-and-structured-output)
 - [Observability and Monitoring](https://deepwiki.com/sgl-project/sglang/19.3-observability-and-monitoring)
 - [Session Management](https://deepwiki.com/sgl-project/sglang/19.4-session-management)
 - [Function Calling and Tool Use](https://deepwiki.com/sgl-project/sglang/19.5-function-calling-and-tool-use)
 - [Diffusion LLM (DLLM) Support](https://deepwiki.com/sgl-project/sglang/19.6-diffusion-llm-(dllm)-support)
 - [RL Integration and Advanced Engine Features](https://deepwiki.com/sgl-project/sglang/19.7-rl-integration-and-advanced-engine-features)
