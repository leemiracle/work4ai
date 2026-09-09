> 来源: [https://deepwiki.com/xorbitsai/inference/3-llm-serving-system](https://deepwiki.com/xorbitsai/inference/3-llm-serving-system)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# LLM Serving System

  Relevant source files 
 - [.github/workflows/python.yaml](https://github.com/xorbitsai/inference/blob/d97e0970/.github/workflows/python.yaml)
 - [doc/source/getting_started/installation.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/installation.rst)
 - [doc/source/models/builtin/llm/index.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/models/builtin/llm/index.rst)
 - [doc/source/user_guide/backends.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/backends.rst)
 - [xinference/model/llm/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/__init__.py)
 - [xinference/model/llm/llm_family.json](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.json)
 - [xinference/model/llm/llm_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py)
 - [xinference/model/llm/reasoning_parser.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/reasoning_parser.py)
 - [xinference/model/llm/sglang/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/sglang/core.py)
 - [xinference/model/llm/tests/test_llm_family.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/tests/test_llm_family.py)
 - [xinference/model/llm/tests/test_utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/tests/test_utils.py)
 - [xinference/model/llm/transformers/chatglm.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/transformers/chatglm.py)
 - [xinference/model/llm/transformers/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/transformers/core.py)
 - [xinference/model/llm/utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/utils.py)
 - [xinference/model/llm/vllm/core.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/vllm/core.py)
 
  
## Purpose and Scope

 The LLM Serving System is the core infrastructure in Xinference that manages the definition, registration, loading, and execution of Large Language Models. It provides a unified interface for serving LLMs across multiple backend engines (vLLM, SGLang, Transformers, llama.cpp, MLX) while abstracting the complexity of model formats, quantization schemes, and hardware acceleration.

 This document covers:

 
 - Model family definitions and specifications.
 - Backend engine architecture and selection logic.
 - Model format support (PyTorch, GGUF, GPTQ, AWQ, MLX, etc.).
 - Model launch and execution flow.
 - Chat, tool calling, and reasoning capabilities.
 
 For API-level details on how clients interact with models, see [RESTful API](https://deepwiki.com/xorbitsai/inference/5-restful-api). For distributed deployment across workers, see [Model Actor Framework](https://deepwiki.com/xorbitsai/inference/2.2-model-actor-framework).

 
## System Architecture Overview

 The LLM Serving System consists of three major layers: the **Model Registry**, the **Engine Selection System**, and the **Runtime Execution Layer**.

 
```

```

 **Sources:** `xinference/model/llm/__init__.py:26-127`(), `xinference/model/llm/llm_family.py:169-195`()

 
## Model Family System

 
### LLMFamilyV2 Data Structure

 The `LLMFamilyV2` class defines a complete model family with all its variants. Each family contains metadata and a list of specifications for different formats and quantizations.

 
```

```

 **Key Fields:**

 
 - `model_ability`: Specifies capabilities like `generate`, `chat`, `tools`, `vision`, `audio`, `reasoning` [xinference/model/llm/llm_family.py174-186](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L174-L186).
 - `model_specs`: Multiple specifications for the same model in different formats (PyTorch, GGUF, etc.) [xinference/model/llm/llm_family.py190](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L190-L190).
 - `chat_template`: Jinja2 template for formatting conversation history [xinference/model/llm/llm_family.py191](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L191-L191).
 - `reasoning_start_tag` / `reasoning_end_tag`: Tags for parsing reasoning content (e.g., `<thought>`) [xinference/model/llm/llm_family.py195-196](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/llm_family.py#L195-L196).
 
 For details on how models are defined, see [Model Family Definitions](https://deepwiki.com/xorbitsai/inference/3.1-model-family-definitions).

 **Sources:** `xinference/model/llm/llm_family.py:73-200`(), `xinference/model/llm/llm_family.json:1-91`()

 
## Backend Engines and Selection

 Xinference supports a variety of specialized backends. The system automatically matches a model request to the best available engine based on format, quantization, and hardware.

 
### Engine Compatibility Matrix

 
| Engine | Supported Formats | Key Features |
|---|---|---|
| vLLM | pytorch, gptq, awq, fp8, bnb, ggufv2 | PagedAttention, Continuous Batching |
| SGLang | pytorch, gptq, awq | RadixAttention, Fast KV Cache Reuse |
| Transformers | pytorch, gptq, awq, bnb, fp4 | Default fallback, widest architecture support |
| llama.cpp | ggufv2 | CPU/GPU offloading via xllamacpp |
| MLX | mlx | Optimized for Apple Silicon Unified Memory |

 For detailed engine documentation, see [Backend Engines](https://deepwiki.com/xorbitsai/inference/3.2-backend-engines). For the matching logic, see [Engine Selection and Matching](https://deepwiki.com/xorbitsai/inference/3.3-engine-selection-and-matching).

 **Sources:** `doc/source/getting_started/installation.rst:38-153`(), `doc/source/user_guide/backends.rst:9-194`(), `xinference/model/llm/__init__.py:64-70`()

 
## Continuous Batching and Scheduling

 High-throughput serving is achieved through the `BatchScheduler` and engine-specific continuous batching implementations.

 
 - **vLLM/SGLang**: Native support for continuous batching and PagedAttention [doc/source/user_guide/backends.rst125-130](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/backends.rst#L125-L130).
 - **Transformers**: Uses a `BatchScheduler` to manage prefill and decode phases for non-native batching engines [xinference/model/llm/transformers/core.py95](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/transformers/core.py#L95-L95).
 
 For details, see [Continuous Batching and Scheduling](https://deepwiki.com/xorbitsai/inference/3.4-continuous-batching-and-scheduling).

 
## Reasoning and Tool Calling

 Xinference provides specialized parsing for advanced LLM features:

 
 - **ReasoningParser**: Extracts "thinking" or "chain-of-thought" content between specific tags (e.g., `<thought>` or `[THINK]`) [xinference/model/llm/utils.py56](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/utils.py#L56-L56).
 - **Tool Calling**: Supports function calling through specific `tool_parsers` (e.g., `Glm4ToolParser`) and chat template normalization `[xinference/model/llm/utils.py:57]`, [xinference/model/llm/utils.py192](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/utils.py#L192-L192).
 
 For details, see [Reasoning and Tool Calling](https://deepwiki.com/xorbitsai/inference/3.5-reasoning-and-tool-calling).

 **Sources:** `xinference/model/llm/utils.py:56-91`(), `xinference/model/llm/utils.py:145-208`()

 
## Distributed Inference

 For large models exceeding a single GPU's memory, Xinference supports distributed inference:

 
 - **Tensor Parallelism**: Supported by vLLM and SGLang `[xinference/model/llm/vllm/core.py:94]`, [xinference/model/llm/sglang/core.py55](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/llm/sglang/core.py#L55-L55).
 - **Multi-Worker Execution**: Coordination across multiple Xinference workers for massive scale.
 
 For details, see [Distributed Inference and Multi-Worker](https://deepwiki.com/xorbitsai/inference/3.6-distributed-inference-and-multi-worker).

 **Sources:** `xinference/model/llm/vllm/core.py:91-103`(), `xinference/model/llm/sglang/core.py:52-65`()

 
## Custom Model Registration

 Users can register custom models via the REST API or Python client. The `register_llm` function persists the model definition to disk if requested, allowing it to survive supervisor restarts.

 
```

```

 **Sources:** `xinference/model/llm/__init__.py:26`(), `xinference/model/llm/llm_family.py:210-296`()
