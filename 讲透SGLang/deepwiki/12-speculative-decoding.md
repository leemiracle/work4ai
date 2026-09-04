> 来源: [https://deepwiki.com/sgl-project/sglang/12-speculative-decoding](https://deepwiki.com/sgl-project/sglang/12-speculative-decoding)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Speculative Decoding

  Relevant source files 
 - [python/sglang/srt/batch_overlap/two_batch_overlap.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/batch_overlap/two_batch_overlap.py)
 - [python/sglang/srt/managers/scheduler_components/dp_attn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_components/dp_attn.py)
 - [python/sglang/srt/mem_cache/allocation_sizing.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/allocation_sizing.py)
 - [python/sglang/srt/model_executor/forward_batch_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/forward_batch_info.py)
 - [python/sglang/srt/model_executor/runner/decode_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/runner/decode_cuda_graph_runner.py)
 - [python/sglang/srt/model_executor/runner/prefill_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/runner/prefill_cuda_graph_runner.py)
 - [python/sglang/srt/speculative/base_spec_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/base_spec_worker.py)
 - [python/sglang/srt/speculative/cpp_ngram/ngram_corpus.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/cpp_ngram/ngram_corpus.py)
 - [python/sglang/srt/speculative/dflash_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/dflash_info.py)
 - [python/sglang/srt/speculative/dflash_info_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/dflash_info_v2.py)
 - [python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py)
 - [python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py)
 - [python/sglang/srt/speculative/eagle_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_info.py)
 - [python/sglang/srt/speculative/eagle_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_utils.py)
 - [python/sglang/srt/speculative/eagle_worker_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py)
 - [python/sglang/srt/speculative/external_corpus_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/external_corpus_manager.py)
 - [python/sglang/srt/speculative/frozen_kv_mtp_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/frozen_kv_mtp_cuda_graph_runner.py)
 - [python/sglang/srt/speculative/frozen_kv_mtp_worker_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/frozen_kv_mtp_worker_v2.py)
 - [python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py)
 - [python/sglang/srt/speculative/multi_layer_eagle_worker_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_worker_v2.py)
 - [python/sglang/srt/speculative/ngram_info.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/ngram_info.py)
 - [python/sglang/srt/speculative/ngram_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/ngram_worker.py)
 - [python/sglang/srt/speculative/spec_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/spec_utils.py)
 - [python/sglang/srt/speculative/standalone_worker_v2.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/standalone_worker_v2.py)
 - [test/registered/unit/spec/test_ngram_corpus.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/spec/test_ngram_corpus.py)
 
  Speculative decoding is an inference optimization technique that accelerates token generation by using a smaller, faster draft model (or heuristic) to propose multiple candidate tokens in parallel, which are then efficiently verified by the larger target model in a single forward pass. This approach can significantly reduce end-to-end latency while maintaining output quality identical to standard autoregressive decoding.

 SGLang provides a high-performance implementation of speculative decoding, primarily focusing on the **EAGLE** (Enhanced Approximate Global Learning for Efficient generation) family of algorithms (EAGLE, EAGLE2, EAGLE3), **Multi-Layer EAGLE**, **DFlash**, **DSpark**, and **N-gram** based speculation.

 **Sources:** [python/sglang/srt/speculative/eagle_worker_v2.py141-155](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L141-L155) [python/sglang/srt/speculative/spec_info.py31-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/spec_info.py#L31-L45) [python/sglang/srt/speculative/ngram_worker.py92-99](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/ngram_worker.py#L92-L99)

 
## Architecture and Key Components

 Speculative decoding in SGLang is implemented through a dual-worker architecture where a draft worker (or n-gram worker) generates candidate tokens and the target worker verifies them. The system integrates tightly with the scheduler and uses CUDA graphs for optimal performance.

 
### Component Overview

 Title: Speculative Decoding Dataflow and Entity Mapping

 
```

```

 **Sources:** [python/sglang/srt/speculative/eagle_worker_v2.py128-144](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L128-L144) [python/sglang/srt/speculative/eagle_worker_v2.py167-176](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L167-L176) [python/sglang/srt/speculative/spec_info.py31-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/spec_info.py#L31-L45)

 
### EagleDraftWorker Class Structure

 The `EagleDraftWorker` class (and its multi-layer variant `MultiLayerEagleDraftWorker`) coordinates the draft-verify cycle. It manages its own `draft_worker` instance of `TpModelWorker` while sharing memory pools with the `target_worker`. It handles specialized logic for different EAGLE versions, including the top-k chain fast path and tree-based sampling.

 **Sources:** [python/sglang/srt/speculative/eagle_worker_v2.py129-185](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L129-L185) [python/sglang/srt/speculative/multi_layer_eagle_worker_v2.py110-185](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_worker_v2.py#L110-L185) [python/sglang/srt/speculative/eagle_worker_v2.py190-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L190-L205)

 
## Supported Algorithms

 SGLang supports multiple speculative decoding algorithms, defined in `SpeculativeAlgorithm`:

 
| Algorithm | Description | Key Features |
|---|---|---|
| EAGLE | EAGLE v1/v2 | Tree-based speculation, learned feature prediction python/sglang/srt/speculative/spec_info.py101-105 |
| EAGLE3 | EAGLE v3 | Optimized for newer architectures, supports auxiliary hidden states python/sglang/srt/speculative/spec_info.py107-108 |
| FROZEN_KV_MTP | Frozen KV MTP | Speculation with frozen KV cache for multi-token prediction python/sglang/srt/speculative/spec_info.py110-111 |
| NGRAM | N-Gram Speculation | Uses NgramCorpus for proposal from CPU-side token streams python/sglang/srt/speculative/ngram_worker.py111-120 |
| DFLASH | DFlash | Distilled Flash speculation using mask-token-id based draft generation python/sglang/srt/speculative/spec_info.py113-114 |
| DSPARK | DSpark | Advanced speculation algorithm supporting ragged verification layouts python/sglang/srt/speculative/spec_info.py116-117 |

 
### EAGLE Algorithm and Architecture

 EAGLE uses a learned draft model that predicts the next feature vector. SGLang supports version-specific optimizations and adaptive speculative decoding managed via `AdaptiveController` to dynamically adjust speculation parameters based on runtime acceptance rates.

 For details, see [EAGLE Algorithm and Architecture](https://deepwiki.com/sgl-project/sglang/12.1-eagle-algorithm-and-architecture).

 **Sources:** [python/sglang/srt/speculative/eagle_worker_v2.py56-59](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L56-L59) [python/sglang/srt/speculative/eagle_worker_v2.py141-155](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L141-L155)

 
### Draft and Verification Flow

 The process involves generating a tree of candidate tokens followed by a single "tree-attention" forward pass in the target model. This uses specialized `ForwardMode` types like `DRAFT_EXTEND_V2` and `TARGET_VERIFY`. Verification logic utilizes `EagleVerifyInput` to manage tree metadata such as `retrieve_index`, `retrieve_next_token`, and `retrieve_next_sibling`.

 For details, see [Draft and Verification Flow](https://deepwiki.com/sgl-project/sglang/12.2-draft-and-verification-flow).

 **Sources:** [python/sglang/srt/speculative/eagle_info.py16-32](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_info.py#L16-L32) [python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py90-91](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py#L90-L91)

 
### Integration with Scheduling

 Speculative decoding integrates with the scheduler through the `ScheduleBatch`. The worker implementations interact with the scheduler's results processing, and the `NGRAMWorker` specifically tracks request IDs via `_prev_decode_rids` to manage corpus state.

 For details, see [Integration with Scheduling](https://deepwiki.com/sgl-project/sglang/12.3-integration-with-scheduling).

 **Sources:** [python/sglang/srt/speculative/ngram_worker.py104-108](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/ngram_worker.py#L104-L108) [python/sglang/srt/speculative/eagle_worker_v2.py190-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L190-L205)

 
## Memory Management

 A critical optimization is the management of KV cache slots and hidden state pools.

 
 - **KV Pool Allocation**: Draft workers obtain `req_to_token_pool` and `token_to_kv_pool_allocator` from the `target_worker` during `alloc_memory_pool`. [python/sglang/srt/speculative/eagle_worker_v2.py190-205](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_worker_v2.py#L190-L205)
 - **Shared Pools**: The `NGRAMWorker` also retrieves target pools post-initialization to ensure synchronization. [python/sglang/srt/speculative/ngram_worker.py71-78](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/ngram_worker.py#L71-L78)
 - **Hidden States Pool**: Multi-Layer EAGLE utilize a persistent buffer set where `hidden_states` are shared across MTP draft steps. [python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py104-130](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py#L104-L130)
 - **KV Loc Management**: Utility functions like `per_step_draft_out_cache_loc` are used to manage the physical layout of the draft cache. [python/sglang/srt/speculative/eagle_utils.py60-81](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_utils.py#L60-L81)
 
 
## CUDA Graph Optimization

 SGLang uses specialized CUDA Graph runners to minimize host-side overhead during the proposal and extension phases.

 Title: CUDA Graph Runners for Speculation

 
```

```

 These runners inherit from `DecodeCudaGraphRunner` and override `capture_one_shape` and `replay` for speculative semantics. The `EagleDraftInputBuffers`, `EagleDraftExtendInputBuffers`, and `MultiLayerEagleDraftExtendInputBuffers` classes define the static memory layout for tensors like `input_ids`, `req_pool_indices`, `out_cache_loc`, and `hidden_states`.

 **Sources:** [python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py76-90](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py#L76-L90) [python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py73-87](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py#L73-L87) [python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py132-147](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py#L132-L147) [python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py56-74](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_cuda_graph_runner.py#L56-L74) [python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py55-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/eagle_draft_extend_cuda_graph_runner.py#L55-L70) [python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py104-130](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/speculative/multi_layer_eagle_draft_extend_cuda_graph_runner.py#L104-L130)
