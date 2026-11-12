<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-LLM · page 24 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/constraints.txt](examples/constraints.txt)
- [tensorrt_llm/_torch/models/modeling_speculative.py](tensorrt_llm/_torch/models/modeling_speculative.py)
- [tensorrt_llm/_torch/modules/fused_moe/communication/deep_ep.py](tensorrt_llm/_torch/modules/fused_moe/communication/deep_ep.py)
- [tensorrt_llm/_torch/modules/fused_moe/communication/deep_ep_low_latency.py](tensorrt_llm/_torch/modules/fused_moe/communication/deep_ep_low_latency.py)
- [tensorrt_llm/_torch/modules/fused_moe/configurable_moe.py](tensorrt_llm/_torch/modules/fused_moe/configurable_moe.py)
- [tensorrt_llm/_torch/modules/fused_moe/create_moe.py](tensorrt_llm/_torch/modules/fused_moe/create_moe.py)
- [tensorrt_llm/_torch/modules/fused_moe/fused_moe_cute_dsl.py](tensorrt_llm/_torch/modules/fused_moe/fused_moe_cute_dsl.py)
- [tensorrt_llm/_torch/modules/fused_moe/fused_moe_cutlass.py](tensorrt_llm/_torch/modules/fused_moe/fused_moe_cutlass.py)
- [tensorrt_llm/_torch/modules/fused_moe/fused_moe_deepgemm.py](tensorrt_llm/_torch/modules/fused_moe/fused_moe_deepgemm.py)
- [tensorrt_llm/_torch/modules/fused_moe/fused_moe_triton.py](tensorrt_llm/_torch/modules/fused_moe/fused_moe_triton.py)
- [tensorrt_llm/_torch/modules/fused_moe/fused_moe_trtllm_gen.py](tensorrt_llm/_torch/modules/fused_moe/fused_moe_trtllm_gen.py)
- [tensorrt_llm/_torch/modules/fused_moe/interface.py](tensorrt_llm/_torch/modules/fused_moe/interface.py)
- [tensorrt_llm/_torch/modules/fused_moe/moe_scheduler.py](tensorrt_llm/_torch/modules/fused_moe/moe_scheduler.py)
- [tensorrt_llm/_torch/modules/fused_moe/quantization.py](tensorrt_llm/_torch/modules/fused_moe/quantization.py)
- [tensorrt_llm/_torch/pyexecutor/_util.py](tensorrt_llm/_torch/pyexecutor/_util.py)
- [tensorrt_llm/_torch/pyexecutor/llm_request.py](tensorrt_llm/_torch/pyexecutor/llm_request.py)
- [tensorrt_llm/_torch/pyexecutor/model_engine.py](tensorrt_llm/_torch/pyexecutor/model_engine.py)
- [tensorrt_llm/_torch/pyexecutor/py_executor.py](tensorrt_llm/_torch/pyexecutor/py_executor.py)
- [tensorrt_llm/_torch/pyexecutor/py_executor_creator.py](tensorrt_llm/_torch/pyexecutor/py_executor_creator.py)
- [tensorrt_llm/_torch/pyexecutor/resource_manager.py](tensorrt_llm/_torch/pyexecutor/resource_manager.py)
- [tensorrt_llm/_torch/speculative/__init__.py](tensorrt_llm/_torch/speculative/__init__.py)
- [tensorrt_llm/_torch/speculative/drafter.py](tensorrt_llm/_torch/speculative/drafter.py)
- [tensorrt_llm/_torch/speculative/eagle3.py](tensorrt_llm/_torch/speculative/eagle3.py)
- [tensorrt_llm/_torch/speculative/interface.py](tensorrt_llm/_torch/speculative/interface.py)
- [tensorrt_llm/_torch/speculative/model_drafter.py](tensorrt_llm/_torch/speculative/model_drafter.py)
- [tensorrt_llm/_torch/speculative/mtp.py](tensorrt_llm/_torch/speculative/mtp.py)
- [tensorrt_llm/_torch/speculative/ngram.py](tensorrt_llm/_torch/speculative/ngram.py)
- [tensorrt_llm/_torch/speculative/utils.py](tensorrt_llm/_torch/speculative/utils.py)
- [tensorrt_llm/commands/serve.py](tensorrt_llm/commands/serve.py)
- [tensorrt_llm/disaggregated_params.py](tensorrt_llm/disaggregated_params.py)
- [tensorrt_llm/llmapi/disagg_utils.py](tensorrt_llm/llmapi/disagg_utils.py)
- [tensorrt_llm/llmapi/llm_args.py](tensorrt_llm/llmapi/llm_args.py)
- [tensorrt_llm/serve/chat_tokenization.py](tensorrt_llm/serve/chat_tokenization.py)
- [tensorrt_llm/serve/conversation_id.py](tensorrt_llm/serve/conversation_id.py)
- [tensorrt_llm/serve/openai_client.py](tensorrt_llm/serve/openai_client.py)
- [tensorrt_llm/serve/openai_disagg_server.py](tensorrt_llm/serve/openai_disagg_server.py)
- [tensorrt_llm/serve/openai_disagg_service.py](tensorrt_llm/serve/openai_disagg_service.py)
- [tensorrt_llm/serve/perf_metrics.py](tensorrt_llm/serve/perf_metrics.py)
- [tensorrt_llm/serve/router.py](tensorrt_llm/serve/router.py)
- [tensorrt_llm/serve/router_utils.py](tensorrt_llm/serve/router_utils.py)
- [tensorrt_llm/version.py](tensorrt_llm/version.py)
- [tests/integration/defs/disaggregated/test_ad_disagg.py](tests/integration/defs/disaggregated/test_ad_disagg.py)
- [tests/integration/defs/disaggregated/test_ad_disagg_trtllm_serve.py](tests/integration/defs/disaggregated/test_ad_disagg_trtllm_serve.py)
- [tests/integration/defs/disaggregated/test_disaggregated_etcd.py](tests/integration/defs/disaggregated/test_disaggregated_etcd.py)
- [tests/integration/defs/disaggregated/test_disaggregated_single_gpu.py](tests/integration/defs/disaggregated/test_disaggregated_single_gpu.py)
- [tests/integration/defs/disaggregated/test_workers.py](tests/integration/defs/disaggregated/test_workers.py)
- [tests/microbenchmarks/bench_moe/utils.py](tests/microbenchmarks/bench_moe/utils.py)
- [tests/unittest/_torch/executor/test_benchmark_disagg.py](tests/unittest/_torch/executor/test_benchmark_disagg.py)
- [tests/unittest/_torch/executor/test_disagg_fill_gate_stall_bound.py](tests/unittest/_torch/executor/test_disagg_fill_gate_stall_bound.py)
- [tests/unittest/_torch/executor/test_py_executor.py](tests/unittest/_torch/executor/test_py_executor.py)
- [tests/unittest/_torch/executor/test_seq_slot_sizing.py](tests/unittest/_torch/executor/test_seq_slot_sizing.py)
- [tests/unittest/_torch/modules/moe/moe_test_utils.py](tests/unittest/_torch/modules/moe/moe_test_utils.py)
- [tests/unittest/_torch/modules/moe/quantize_utils.py](tests/unittest/_torch/modules/moe/quantize_utils.py)
- [tests/unittest/_torch/modules/moe/test_moe_backend.py](tests/unittest/_torch/modules/moe/test_moe_backend.py)
- [tests/unittest/_torch/modules/moe/test_moe_module.py](tests/unittest/_torch/modules/moe/test_moe_module.py)
- [tests/unittest/_torch/modules/test_fused_moe.py](tests/unittest/_torch/modules/test_fused_moe.py)
- [tests/unittest/_torch/speculative/test_eagle3.py](tests/unittest/_torch/speculative/test_eagle3.py)
- [tests/unittest/api_stability/references/llm.yaml](tests/unittest/api_stability/references/llm.yaml)
- [tests/unittest/api_stability/references/trtllm_serve_cli.yaml](tests/unittest/api_stability/references/trtllm_serve_cli.yaml)
- [tests/unittest/disaggregated/test_coordinator_worker.py](tests/unittest/disaggregated/test_coordinator_worker.py)
- [tests/unittest/disaggregated/test_disagg_internal_auth.py](tests/unittest/disaggregated/test_disagg_internal_auth.py)
- [tests/unittest/disaggregated/test_disagg_openai_client.py](tests/unittest/disaggregated/test_disagg_openai_client.py)
- [tests/unittest/disaggregated/test_disagg_utils.py](tests/unittest/disaggregated/test_disagg_utils.py)
- [tests/unittest/disaggregated/test_disaggregated_params.py](tests/unittest/disaggregated/test_disaggregated_params.py)
- [tests/unittest/disaggregated/test_openai_disagg_server.py](tests/unittest/disaggregated/test_openai_disagg_server.py)
- [tests/unittest/disaggregated/test_openai_disagg_service.py](tests/unittest/disaggregated/test_openai_disagg_service.py)
- [tests/unittest/disaggregated/test_router.py](tests/unittest/disaggregated/test_router.py)
- [tests/unittest/llmapi/test_llm_args.py](tests/unittest/llmapi/test_llm_args.py)

</details>



This glossary defines codebase-specific terms, jargon, and domain concepts used throughout the TensorRT-LLM project. It serves as a technical reference for engineers to understand the mapping between high-level LLM serving concepts and their specific implementations in the code.

## Core System Entities

The following diagram illustrates the relationship between the high-level API used by users and the internal execution engines.

### API to Runtime Mapping
```mermaid
graph TD
    [UserScript] -->|calls| [LLM_Class]
    [LLM_Class] -->|dispatches| [Gen_Exec]
    [Gen_Exec] -->|PyTorchBackend| [Py_Exec]
    [Py_Exec] -->|orchestrates| [Torch_Engine]
    [LLM_Class] -->|TRTBackend| [TRT_Engine]

    subgraph "NaturalLanguageSpace"
        [UserScript]
    end

    subgraph "LLM_API_Layer"
        [LLM_Class] ["LLM (tensorrt_llm/llmapi/llm.py)"]
    end

    subgraph "Executor_Layer"
        [Gen_Exec] ["GenerationExecutor (tensorrt_llm/executor/executor.py)"]
        [Py_Exec] ["PyExecutor (tensorrt_llm/_torch/pyexecutor/py_executor.py)"]
    end

    subgraph "Model_Engines"
        [TRT_Engine] ["TRT-LLM C++ Runtime"]
        [Torch_Engine] ["PyTorchModelEngine (tensorrt_llm/_torch/pyexecutor/model_engine.py)"]
    end
```
Sources: [tensorrt_llm/_torch/pyexecutor/py_executor.py:71-71](), [tensorrt_llm/_torch/pyexecutor/model_engine.py:89-91](), [tensorrt_llm/_torch/pyexecutor/py_executor_creator.py:47-49]()

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **LLM** | The main entry point for the Python API, supporting both TensorRT and PyTorch backends. | [tensorrt_llm/commands/serve.py:29-29]() |
| **PyExecutor** | A Python-based request orchestrator that manages the lifecycle of LLM requests, including scheduling and resource allocation for the PyTorch backend. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:71-71]() |
| **ModelEngine** | An abstract base class defining the interface for model forward passes and warmups in the PyTorch execution path. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:12-15]() |
| **ScheduledRequests** | A container holding the set of requests selected by the scheduler for the current execution iteration. | [tensorrt_llm/_torch/pyexecutor/scheduler.py:99-99]() |
| **LlmRequest** | Internal data structure representing a single generation request throughout its lifecycle in the Python executor. | [tensorrt_llm/_torch/pyexecutor/llm_request.py:7-10]() |

Sources: [tensorrt_llm/_torch/pyexecutor/py_executor.py:71-71](), [tensorrt_llm/_torch/pyexecutor/model_engine.py:12-15](), [tensorrt_llm/_torch/pyexecutor/llm_request.py:7-10]()

---

## Memory and Resource Management

TensorRT-LLM uses a sophisticated resource management system to handle KV caches and PEFT adapters across distributed ranks.

### Resource Manager Architecture
```mermaid
graph LR
    [RM] ["ResourceManager (tensorrt_llm/_torch/pyexecutor/resource_manager.py)"]
    [KV_MGR] ["KVCacheManagerV2"]
    [PEFT_MGR] ["PeftCacheManager"]
    [SEQ_MGR] ["SeqSlotManager"]
    [GPU_MEM] ["GPU VRAM"]
    [Pinned_MEM] ["Host Pinned Memory"]

    [RM] --> [KV_MGR]
    [RM] --> [PEFT_MGR]
    [RM] --> [SEQ_MGR]
    [KV_MGR] -->|allocates| [GPU_MEM]
    [PEFT_MGR] -->|manages| [GPU_MEM]

    subgraph "ResourceManager_Entity"
        [RM]
        [KV_MGR]
        [PEFT_MGR]
        [SEQ_MGR]
    end

    subgraph "Hardware_Resources"
        [GPU_MEM]
        [Pinned_MEM]
    end
```
Sources: [tensorrt_llm/_torch/pyexecutor/resource_manager.py:99-105](), [tensorrt_llm/_torch/pyexecutor/_util.py:127-131]()

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **KV Cache Manager** | Manages the allocation of paged KV cache blocks. Supports V1 (static) and V2 (dynamic/unified) implementations. | [tensorrt_llm/_torch/pyexecutor/resource_manager.py:60-60](), [tensorrt_llm/_torch/pyexecutor/resource_manager.py:99-101]() |
| **KVCacheManagerV2** | A Python implementation of the KV cache manager that supports per-layer buffer sizes and unified pools. | [tensorrt_llm/_torch/pyexecutor/kv_cache_manager_v2.py:77-77]() |
| **In-flight Batching** | A technique where new requests are added to the batch as soon as others finish, rather than waiting for the entire batch to complete. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:35-35]() |
| **PeftCacheManager** | Manages the loading and eviction of LoRA adapters in GPU memory. | [tensorrt_llm/_torch/pyexecutor/resource_manager.py:103-103]() |
| **SeqSlotManager** | Manages unique slots for sequences in a batch, used for indexing into various state buffers. | [tensorrt_llm/_torch/pyexecutor/resource_manager.py:104-104]() |
| **KvCacheConnector** | Interface for connecting KV cache management to external storage or network transfers for prefix caching. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:68-68]() |

Sources: [tensorrt_llm/_torch/pyexecutor/resource_manager.py:60-104](), [tensorrt_llm/_torch/pyexecutor/kv_cache_manager_v2.py:77-77](), [tensorrt_llm/_torch/pyexecutor/py_executor.py:35-68]()

---

## Speculative Decoding Concepts

Speculative decoding accelerates inference by using a smaller "draft" model or specialized modules to predict multiple tokens, which are then verified in parallel by the "target" model.

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Drafter** | The component responsible for generating candidate tokens (e.g., `EagleDrafter`, `MTPDrafter`). | [tensorrt_llm/_torch/pyexecutor/py_executor.py:64-64]() |
| **SpeculationGate** | Logic that determines whether to accept or reject tokens produced by a drafter. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:66-66]() |
| **MTP** | Multi-Token Prediction speculative decoding where the model predicts multiple tokens at once using specialized modules. | [tensorrt_llm/_torch/speculative/mtp.py:1-20]() |
| **EAGLE3** | A high-performance speculative decoding architecture utilizing specialized drafters and resource managers. | [tensorrt_llm/_torch/speculative/eagle3.py:77-77]() |
| **SpecMetadata** | Metadata structure passed through the model to coordinate speculative execution across layers. | [tensorrt_llm/_torch/speculative/interface.py:20-20]() |
| **Rejection Sampling** | A method used in speculative decoding to verify draft tokens against the target model's probability distribution. | [tensorrt_llm/_torch/speculative/interface.py:53-60]() |

Sources: [tensorrt_llm/_torch/pyexecutor/py_executor.py:64-66](), [tensorrt_llm/_torch/speculative/mtp.py:1-20](), [tensorrt_llm/_torch/speculative/eagle3.py:77-77](), [tensorrt_llm/_torch/speculative/interface.py:20-60]()

---

## Attention and Kernel Optimization

### Attention Backend Dispatch
The codebase uses a pluggable attention backend system to support different hardware and performance requirements.

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **AttentionBackend** | Abstract interface for attention implementations (TRT-LLM kernels, FlashInfer, Vanilla PyTorch). | [tensorrt_llm/_torch/attention_backend/interface.py:48-49]() |
| **CUDAGraphRunner** | Utility for capturing and replaying PyTorch operations as CUDA graphs to reduce CPU overhead. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:87-89]() |
| **AutoTuner** | A system that profiles different kernel configurations and selects the fastest one for the current hardware. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:53-53]() |
| **XQA** | Cross-Query Attention kernels optimized for specific hardware generations (e.g., Ampere, Hopper). | [tensorrt_llm/_torch/attention_backend/trtllm.py:32-33]() |
| **FlashInfer** | A high-performance attention library integrated as an optional backend. | [tensorrt_llm/_torch/speculative/interface.py:34-34]() |
| **MLA** | Multi-head Latent Attention, a memory-efficient attention mechanism used in models like DeepSeek-V3. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:85-85]() |

Sources: [tensorrt_llm/_torch/attention_backend/interface.py:48-49](), [tensorrt_llm/_torch/pyexecutor/model_engine.py:53-89](), [tensorrt_llm/_torch/attention_backend/trtllm.py:32-33](), [tensorrt_llm/_torch/speculative/interface.py:34-34]()

---

## Distributed Serving Jargon

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Disaggregated Serving** | Separating the "Context" (Prefill) phase and "Generation" (Decode) phase onto different GPU clusters. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:22-22]() |
| **KV Cache Transceiver** | Handles the transfer of KV cache data across the network in disaggregated serving setups using NIXL/UCX. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:79-80]() |
| **DWDP** | Distributed Weight Data Parallelism, a technique for high-performance inference on NVL72 architectures that offloads weights across peer GPUs via P2P NVLink. | [README.md:37-38](), [tensorrt_llm/_torch/pyexecutor/py_executor.py:69-69]() |
| **CP (Context Parallelism)** | Sharding the context length dimension across multiple GPUs. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:47-47]() |
| **PP (Pipeline Parallelism)** | Distributing model layers across multiple GPUs in a sequence. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:91-91]() |
| **EP (Expert Parallelism)** | Sharding the experts in an MoE model across multiple GPUs. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:68-69]() |

Sources: [tensorrt_llm/_torch/pyexecutor/py_executor.py:22-91](), [README.md:37-38](), [tensorrt_llm/_torch/pyexecutor/model_engine.py:68-69]()

---

## Model Architecture Concepts

Specific architectural terms used within the model implementations.

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **MoE (Mixture of Experts)** | A model architecture where only a subset of parameters (experts) is active for each input token. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:68-69]() |
| **RoPE** | Rotary Positional Embedding, a method for encoding positional information. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:92-92]() |
| **NVFP4** | A 4-bit floating point quantization format supported on Blackwell GPUs. | [tensorrt_llm/_torch/pyexecutor/resource_manager.py:134-134]() |
| **EPLB** | Expert Parallel Load Balancing, a strategy to distribute expert workloads evenly across GPUs. | [tensorrt_llm/_torch/pyexecutor/model_engine.py:68-69]() |

Sources: [tensorrt_llm/_torch/pyexecutor/model_engine.py:68-92](), [tensorrt_llm/_torch/pyexecutor/resource_manager.py:134-134]()

---

## Testing and CI/CD Infrastructure

### Test Configuration to Hardware Mapping
```mermaid
graph TD
    [H100] ["H100 (tests/integration/test_lists/test-db/l0_h100.yml)"]
    [B200] ["B200 (tests/integration/test_lists/test-db/l0_b200.yml)"]
    [A10] ["A10 (tests/integration/test_lists/test-db/l0_a10.yml)"]
    [Pytest] ["Pytest Orchestrator"]
    [MPI] ["MPI Session (tensorrt_llm/llmapi/mpi_session.py)"]
    [Accuracy_Harness] ["LlmapiAccuracyTestHarness"]
    [E2E_Tests] ["test_e2e.py"]

    [H100] -->|determines_capability| [Pytest]
    [B200] -->|determines_capability| [Pytest]
    [A10] -->|filters_tests| [Pytest]
    [Pytest] -->|executes| [Accuracy_Harness]
    [Pytest] -->|executes| [E2E_Tests]
    [Accuracy_Harness] -->|launches_multi-gpu| [MPI]
```
Sources: [tensorrt_llm/llmapi/llm_args.py:1-50](), [tensorrt_llm/_torch/pyexecutor/py_executor.py:31-33]()

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **MPI Session** | Manages multi-process execution for distributed inference, often used in multi-GPU tests. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:31-33]() |
| **Accuracy Harness** | Framework for running and validating model accuracy against standard benchmarks. | [tensorrt_llm/_torch/pyexecutor/py_executor.py:49-49]() |

Sources: [tensorrt_llm/_torch/pyexecutor/py_executor.py:31-49]()