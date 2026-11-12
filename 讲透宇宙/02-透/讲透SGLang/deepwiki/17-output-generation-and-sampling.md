> 来源: [https://deepwiki.com/sgl-project/sglang/17-output-generation-and-sampling](https://deepwiki.com/sgl-project/sglang/17-output-generation-and-sampling)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Output Generation and Sampling

  Relevant source files 
 - [experimental/sgl-router/src/policies/kv_events/wire.rs](https://github.com/sgl-project/sglang/blob/94183a8d/experimental/sgl-router/src/policies/kv_events/wire.rs)
 - [python/sglang/bench_one_batch_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/bench_one_batch_server.py)
 - [python/sglang/benchmark/datasets/speed_bench.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/benchmark/datasets/speed_bench.py)
 - [python/sglang/benchmark/offline_throughput.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/benchmark/offline_throughput.py)
 - [python/sglang/benchmark/one_batch_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/benchmark/one_batch_server.py)
 - [python/sglang/srt/disaggregation/kv_events.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/kv_events.py)
 - [python/sglang/srt/entrypoints/openai/serving_tokenize.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/openai/serving_tokenize.py)
 - [python/sglang/srt/layers/logits_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py)
 - [python/sglang/srt/layers/logprob_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logprob_processor.py)
 - [python/sglang/srt/layers/logsumexp.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logsumexp.py)
 - [python/sglang/srt/layers/sampler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py)
 - [python/sglang/srt/lora/backend/lmhead_mixing.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/lora/backend/lmhead_mixing.py)
 - [python/sglang/srt/managers/scheduler_components/kv_events_publisher.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/kv_events_publisher.py)
 - [python/sglang/srt/sampling/custom_logit_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/custom_logit_processor.py)
 - [python/sglang/srt/sampling/penaltylib/min_new_tokens.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/penaltylib/min_new_tokens.py)
 - [python/sglang/srt/sampling/sampling_batch_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_batch_info.py)
 - [python/sglang/srt/sampling/sampling_params.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py)
 - [python/sglang/test/gpt_oss_common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/test/gpt_oss_common.py)
 - [test/manual/perf/test_bench_one_batch_1gpu.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/perf/test_bench_one_batch_1gpu.py)
 - [test/manual/test_logprobs.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/test_logprobs.py)
 - [test/manual/test_schedule_policy.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/test_schedule_policy.py)
 - [test/registered/core/test_hidden_states.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/core/test_hidden_states.py)
 - [test/registered/core/test_request_queue_validation.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/core/test_request_queue_validation.py)
 - [test/registered/core/test_srt_endpoint.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/core/test_srt_endpoint.py)
 - [test/registered/core/test_srt_engine.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/core/test_srt_engine.py)
 - [test/registered/lora/test_lora_hf_sgl_logprob_diff.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/lora/test_lora_hf_sgl_logprob_diff.py)
 - [test/registered/lora/test_lora_moe_tp_logprob_diff.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/lora/test_lora_moe_tp_logprob_diff.py)
 - [test/registered/unit/disaggregation/test_kv_events.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_kv_events.py)
 - [test/registered/unit/layers/test_logprob_chunk_stitching.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/test_logprob_chunk_stitching.py)
 - [test/registered/unit/layers/test_logprob_fast_input.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/test_logprob_fast_input.py)
 - [test/registered/unit/sampling/test_custom_logit_processor.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/sampling/test_custom_logit_processor.py)
 - [test/registered/unit/sampling/test_penaltylib.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/sampling/test_penaltylib.py)
 - [test/registered/unit/sampling/test_sampling_batch_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/sampling/test_sampling_batch_info.py)
 - [test/registered/unit/sampling/test_sampling_params.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/sampling/test_sampling_params.py)
 
  
## Purpose and Scope

 This document covers the token sampling system in SGLang, which determines how next tokens are selected from model logits during text generation. This includes sampling parameter configuration, logits processing, various sampling algorithms (greedy, top-k, top-p, min-p), penalty mechanisms (frequency, presence, repetition), and multi-backend support (FlashInfer, PyTorch, Ascend, Aiter).

 For details on specific sub-topics, see:

 
 - [Sampling Parameters and Configuration](https://deepwiki.com/sgl-project/sglang/17.1-sampling-parameters-and-configuration) — Document sampling parameters (temperature, top_p, top_k, etc.) and `SamplingParams` class. [python/sglang/srt/sampling/sampling_params.py45-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L45-L150)
 - [Logits Processing Pipeline](https://deepwiki.com/sgl-project/sglang/17.2-logits-processing-pipeline) — Explain `LogitsProcessor`, logprob computation, and logits modification. [python/sglang/srt/layers/logits_processor.py14-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L14-L150)
 - [Sampling Algorithms](https://deepwiki.com/sgl-project/sglang/17.3-sampling-algorithms) — Document top-k, top-p, min-p, temperature sampling, and greedy decoding. [python/sglang/srt/layers/sampler.py126-187](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L126-L187)
 - [Penalties and Constraints](https://deepwiki.com/sgl-project/sglang/17.4-penalties-and-constraints) — Explain frequency/presence penalties, repetition penalties, and length constraints. [python/sglang/srt/sampling/sampling_params.py66-69](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L66-L69)
 
 For information about:

 
 - Request lifecycle and batch scheduling, see [Request Processing Pipeline](https://deepwiki.com/sgl-project/sglang/4-request-processing-pipeline).
 - Constrained decoding (JSON schema, regex, EBNF), see [Constrained and Structured Output](https://deepwiki.com/sgl-project/sglang/19.2-constrained-and-structured-output).
 - Model execution and logits computation, see [Model Execution and Forward Pass](https://deepwiki.com/sgl-project/sglang/4.3-model-execution-and-forward-pass).
 
 
## Overview

 The sampling system in SGLang converts model logits into next token selections through a multi-stage pipeline. The process begins with user-defined `SamplingParams` [python/sglang/srt/sampling/sampling_params.py45-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L45-L150) which are aggregated into a `SamplingBatchInfo` object [python/sglang/srt/sampling/sampling_batch_info.py29-75](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_batch_info.py#L29-L75) by the scheduler. During the model forward pass, raw logits are managed via `LogitsProcessorOutput` [python/sglang/srt/layers/logits_processor.py99-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L99-L156) which are then processed by the `Sampler` to select the next tokens based on the configured algorithms and backends [python/sglang/srt/layers/sampler.py97-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L97-L120)

 
### High-Level Sampling Architecture

 The following diagram illustrates the flow from request configuration to token selection, bridging the high-level logic to the specific code entities involved.

 Title: "Sampling Data Flow and Code Entities"

 
```

```

 **Sources**: [python/sglang/srt/sampling/sampling_params.py45-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L45-L150) [python/sglang/srt/layers/sampler.py71-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L71-L120) [python/sglang/srt/layers/logits_processor.py99-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L99-L156)

 
## Sampling Components and Backends

 SGLang supports multiple hardware backends for sampling, ensuring optimized performance across different accelerators.

 
### Backend Support Table

 
| Backend | Platform | Implementation | Features |
|---|---|---|---|
| flashinfer | NVIDIA CUDA | flashinfer kernels | High-performance fused sampling (top-k, top-p, min-p) python/sglang/srt/layers/sampler.py30-38 |
| aiter | AMD ROCm | aiter kernels | Optimized greedy sampling for HIP/ROCm python/sglang/srt/layers/sampler.py48-57 |
| pytorch | General | Native PyTorch ops | Cross-platform compatibility using torch.argmax or torch.multinomial python/sglang/srt/layers/sampler.py133-141 |
| ascend | Huawei NPU | torch_npu kernels | Optimized for Ascend hardware via _forward_ascend_backend python/sglang/srt/layers/sampler.py165-173 |

 
### Logic Execution Flow

 The `Sampler.forward` method acts as the central dispatcher [python/sglang/srt/layers/sampler.py97-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L97-L120) It handles greedy decoding optimizations, applies custom logit processors [python/sglang/srt/layers/sampler.py88-95](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L88-L95) and routes the sampling request to the appropriate backend-specific implementation.

 Title: "Sampler Dispatch Logic"

 
```

```

 **Sources**: [python/sglang/srt/layers/sampler.py88-187](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L88-L187) [python/sglang/srt/layers/sampler.py48-57](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L48-L57)

 
## Deterministic Sampling and RL Integration

 SGLang provides specific optimizations for Reinforcement Learning (RL) on-policy workloads and deterministic inference.

 
 - **Deterministic Inference**: When enabled via `enable_deterministic`, the sampler uses position-based seeds and `murmur_hash32` to ensure reproducible token selection [python/sglang/srt/layers/sampler.py79-81](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L79-L81) [python/sglang/srt/layers/sampler.py117-118](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L117-L118)
 - **RL On-Policy Mode**: In this mode, the system uses `log_softmax` to compute logprobs to match trainer implementations exactly [python/sglang/srt/layers/sampler.py82-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L82-L83) It also handles `bfloat16` precision for logits as required by many RL pipelines [python/sglang/srt/layers/sampler.py155-163](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L155-L163)
 - **Synchronization**: For Tensor Parallel (TP) deployments, token IDs can be synchronized across the device group using `SYNC_TOKEN_IDS_ACROSS_TP` to maintain consistency [python/sglang/srt/layers/sampler.py64-65](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L64-L65)
 
 **Sources**: [python/sglang/srt/layers/sampler.py64-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L64-L83) [python/sglang/srt/layers/sampler.py155-163](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L155-L163)

 
## Disaggregation and KV Events

 In disaggregated prefill-decode architectures, the sampling system interacts with the KV cache event system to coordinate state across replicas.

 
 - **KV Event Publishing**: The `SchedulerKvEventsPublisher` emits metrics and cache events (like `BlockStored` or `BlockRemoved`) to notify other components (e.g., routers or decode instances) about the state of the KV cache [python/sglang/srt/managers/scheduler_components/kv_events_publisher.py45-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/kv_events_publisher.py#L45-L107)
 - **Event Metadata**: Events include `block_hashes`, `token_ids`, and `medium` (GPU, CPU, DISK, or EXTERNAL) to facilitate efficient prefix-aware routing [python/sglang/srt/disaggregation/kv_events.py112-134](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/kv_events.py#L112-L134)
 
 Title: "KV Event Propagation Space"

 
```

```

 **Sources**: [python/sglang/srt/managers/scheduler_components/kv_events_publisher.py79-107](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/kv_events_publisher.py#L79-L107) [python/sglang/srt/disaggregation/kv_events.py112-140](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/kv_events.py#L112-L140)

 
## Sub-Topic Overviews

 
### Sampling Parameters and Configuration

 The `SamplingParams` class defines the generation constraints for each request [python/sglang/srt/sampling/sampling_params.py45-83](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L45-L83) It includes standard LLM parameters like `temperature`, `top_p`, and `top_k`, as well as SGLang-specific options for logit bias and structured output via EBNF or JSON schema [python/sglang/srt/sampling/sampling_params.py71-80](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L71-L80) For details, see [Sampling Parameters and Configuration](https://deepwiki.com/sgl-project/sglang/17.1-sampling-parameters-and-configuration).

 
### Logits Processing Pipeline

 Before a token is sampled, raw logits are managed by the `LogitsProcessor` [python/sglang/srt/layers/logits_processor.py14-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L14-L150) This pipeline handles logprob computation for both input and output tokens, top-k logprob retrieval, and integration with speculative decoding via EAGLE hidden state capture [python/sglang/srt/layers/logits_processor.py99-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L99-L156) It also supports custom logit processors for controlling specific model behaviors [python/sglang/srt/sampling/sampling_batch_info.py144-154](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_batch_info.py#L144-L154) For details, see [Logits Processing Pipeline](https://deepwiki.com/sgl-project/sglang/17.2-logits-processing-pipeline).

 
### Sampling Algorithms

 SGLang implements various selection strategies. While greedy decoding is optimized via `argmax` or `aiter` [python/sglang/srt/layers/sampler.py130-141](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L130-L141) stochastic sampling uses multinomial distributions. Advanced techniques like `min_p` sampling and `top_k`/`top_p` renormalization are supported via `flashinfer` and `sgl_kernel` [python/sglang/srt/layers/sampler.py30-38](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L30-L38) For details, see [Sampling Algorithms](https://deepwiki.com/sgl-project/sglang/17.3-sampling-algorithms).

 
### Penalties and Constraints

 To prevent repetitive or infinite generation, SGLang applies several penalties. These include `frequency_penalty`, `presence_penalty`, and `repetition_penalty` [python/sglang/srt/sampling/sampling_params.py66-68](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L66-L68) Length constraints like `max_new_tokens` and `min_new_tokens` are enforced to control output volume [python/sglang/srt/sampling/sampling_params.py54-69](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L54-L69) Repetition penalties are managed by a `BatchedPenalizerOrchestrator` [python/sglang/srt/sampling/sampling_batch_info.py181-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_batch_info.py#L181-L188) For details, see [Penalties and Constraints](https://deepwiki.com/sgl-project/sglang/17.4-penalties-and-constraints).

 **Sources**: [python/sglang/srt/sampling/sampling_params.py45-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_params.py#L45-L150) [python/sglang/srt/layers/sampler.py88-187](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/sampler.py#L88-L187) [python/sglang/srt/layers/logits_processor.py99-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/logits_processor.py#L99-L156) [python/sglang/srt/sampling/sampling_batch_info.py181-188](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/sampling/sampling_batch_info.py#L181-L188)
