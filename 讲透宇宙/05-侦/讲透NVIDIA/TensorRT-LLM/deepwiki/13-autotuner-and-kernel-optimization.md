<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-LLM · page 13 AutoTuner and Kernel Optimization · fetched 2026-10-26 -->

# AutoTuner and Kernel Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpp/tensorrt_llm/kernels/CMakeLists.txt](cpp/tensorrt_llm/kernels/CMakeLists.txt)
- [cpp/tensorrt_llm/kernels/userbuffers/CMakeLists.txt](cpp/tensorrt_llm/kernels/userbuffers/CMakeLists.txt)
- [cpp/tensorrt_llm/thop/CMakeLists.txt](cpp/tensorrt_llm/thop/CMakeLists.txt)
- [tensorrt_llm/_torch/autotuner.py](tensorrt_llm/_torch/autotuner.py)
- [tensorrt_llm/_torch/custom_ops/cpp_custom_ops.py](tensorrt_llm/_torch/custom_ops/cpp_custom_ops.py)
- [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py](tensorrt_llm/_torch/custom_ops/torch_custom_ops.py)
- [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py](tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py)
- [tensorrt_llm/_torch/model_config.py](tensorrt_llm/_torch/model_config.py)
- [tensorrt_llm/_torch/modules/gated_mlp.py](tensorrt_llm/_torch/modules/gated_mlp.py)
- [tensorrt_llm/_torch/modules/linear.py](tensorrt_llm/_torch/modules/linear.py)
- [tensorrt_llm/_torch/modules/mlp.py](tensorrt_llm/_torch/modules/mlp.py)
- [tensorrt_llm/_torch/peft/lora/layer.py](tensorrt_llm/_torch/peft/lora/layer.py)
- [tensorrt_llm/_torch/utils.py](tensorrt_llm/_torch/utils.py)
- [tensorrt_llm/llmapi/llm_utils.py](tensorrt_llm/llmapi/llm_utils.py)
- [tensorrt_llm/models/modeling_utils.py](tensorrt_llm/models/modeling_utils.py)
- [tests/unittest/_torch/misc/test_autotuner.py](tests/unittest/_torch/misc/test_autotuner.py)
- [tests/unittest/_torch/thop/parallel/test_dense_gemm_act_fusion.py](tests/unittest/_torch/thop/parallel/test_dense_gemm_act_fusion.py)

</details>



## Purpose and Scope

The AutoTuner system provides automatic kernel selection and optimization for compute-intensive operations in TensorRT-LLM. It profiles different kernel implementations (tactics) across various input shapes, caches the best-performing configurations, and automatically selects optimal kernels during inference. This system is critical for achieving peak performance across diverse hardware and workload configurations, particularly for complex operations like Mixture of Experts (MoE), block-scaled quantization, and fused communication kernels.

For details on architecture and caching, see [AutoTuner Architecture](#13.1). For information on integrating custom operations, see [Custom Op Integration and Tunable Runners](#13.2).

## System Architecture

The AutoTuner system consists of three main layers: the tuning orchestration layer (`AutoTuner` singleton), the runner abstraction layer (`TunableRunner` implementations), and the cache persistence layer (`ProfilingCache`).

**AutoTuner Architecture**

```mermaid
graph TB
    subgraph "TuningInterface"
        ["autotune() context manager"] -- "activates" --> [Singleton]
        ["AutoTuner.choose_one()"] -- "requests tactic" --> [Singleton]
    end
    
    subgraph "AutoTunerCore"
        [Singleton] -- "manages" --> ["AutoTuner (tensorrt_llm._torch.autotuner.AutoTuner)"]
        [Singleton] -- "accesses" --> ["ProfilingCache (tensorrt_llm._torch.autotuner.ProfilingCache)"]
        [Singleton] -- "triggers" --> ["_profile_tactics()"]
    end
    
    subgraph "RunnerLayer"
        ["TunableRunner (tensorrt_llm._torch.autotuner.TunableRunner)"] -- "implements" --> [Base]
        [Base] -- "specializes" --> ["GemmRunner (tests/unittest/_torch/misc/test_autotuner.py)"]
        [Base] -- "specializes" --> ["MoERunner (tensorrt_llm._torch.custom_ops.torch_custom_ops.MoERunner)"]
    end
    
    subgraph "Configuration"
        ["TuningConfig (tensorrt_llm._torch.autotuner.TuningConfig)"]
        ["DynamicTensorSpec (tensorrt_llm._torch.autotuner.DynamicTensorSpec)"]
        ["OptimizationProfile (tensorrt_llm._torch.autotuner.OptimizationProfile)"]
    end
    
    [Singleton] -- "profiles" --> [Base]
    ["ProfilingCache"] -- "persists to" --> ["Disk Cache (.autotuner_cache.json)"]
```

**Sources:** [tensorrt_llm/_torch/autotuner.py:11-134](), [tensorrt_llm/_torch/autotuner.py:466-512](), [tests/unittest/_torch/misc/test_autotuner.py:121-137](), [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:67-146]()

## Core Concepts

### Tactics and Profiling

A **tactic** is an identifier representing a specific kernel configuration or implementation [tensorrt_llm/_torch/autotuner.py:191-193](). The AutoTuner profiles each tactic by warming up, running the kernel multiple times with CUDA events for timing, and computing the median latency [tensorrt_llm/_torch/autotuner.py:800-868]().

The tactic value `-1` is often used as a **fallback tactic** in implementations to ensure functional correctness when optimized tactics are unavailable [tests/unittest/_torch/misc/test_autotuner.py:132-134](). To ensure precise timing during profiling, the system can utilize a global timer kernel recorded via `record_global_timer` or simulate delays via `delay_kernel` for testing [tensorrt_llm/_torch/autotuner.py:23-24](), [tests/unittest/_torch/misc/test_autotuner.py:85-100]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:186-203](), [tensorrt_llm/_torch/autotuner.py:800-868](), [tests/unittest/_torch/misc/test_autotuner.py:121-154]()

### Dynamic Tensor Bucketing

The AutoTuner handles dynamic tensor shapes through **bucketing** via `DynamicTensorSpec` [tensorrt_llm/_torch/autotuner.py:48-61]().

```mermaid
graph LR
    subgraph "RuntimeMapping"
        ["Input Tensor (shape=[M, K])"] -- "input to" --> ["map_to_tuning_buckets()"]
        ["map_to_tuning_buckets()"] -- "yields" --> ["Mapped Bucket Value"]
    end
    
    subgraph "TuningPhase"
        ["gen_tuning_buckets()"] -- "defines" --> ["Profile each bucket"]
        ["Profile each bucket"] -- "populates" --> ["Cache: bucket_key → best_tactic"]
    end
    
    ["Mapped Bucket Value"] -- "look up" --> ["Cache: bucket_key → best_tactic"]
```

The `DynamicTensorSpec` specifies the input index, dimension index, and functions for generating and mapping buckets [tensorrt_llm/_torch/autotuner.py:57-60](). For runtime efficiency, `map_to_tuning_buckets` allows mapping a specific input size to a previously tuned bucket (e.g., mapping to the next power of two) [tests/unittest/_torch/misc/test_autotuner.py:143-147](). In MoE scenarios, `get_last_power_of_2_num_tokens_buckets` is commonly used to bucket token counts [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:83-85]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:48-61](), [tests/unittest/_torch/misc/test_autotuner.py:182-207](), [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:83-85]()

### Optimization Profiles

An `OptimizationProfile` represents the shape ranges of all input tensors for a specific tuning case [tensorrt_llm/_torch/autotuner.py:164-168](). Each dimension is either a `StaticDim` (fixed value) or a `DynamicDim` (min/opt/max range) [tensorrt_llm/_torch/autotuner.py:142-156]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:142-181]()

## TunableRunner Interface

To make a kernel tunable, implement the `TunableRunner` abstract base class [tensorrt_llm/_torch/autotuner.py:190-254]().

**TunableRunner Contract**

| Method | Purpose |
|--------|---------|
| `get_valid_tactics()` | Returns list of valid tactic objects for given inputs and profile [tensorrt_llm/_torch/autotuner.py:193-194](). |
| `forward()` | Executes the kernel with a specific `tactic` [tensorrt_llm/_torch/autotuner.py:206-207](). |
| `unique_id()` | Returns a hashable identifier for the runner instance to separate cache entries [tensorrt_llm/_torch/autotuner.py:218-219](). |

**Sources:** [tensorrt_llm/_torch/autotuner.py:190-254](), [tests/unittest/_torch/misc/test_autotuner.py:121-136]()

## Tuning Configuration

The `TuningConfig` class encapsulates tuning parameters, including `dynamic_tensor_specs`, `constraint_specs`, and `distributed_tuning_strategy` [tensorrt_llm/_torch/autotuner.py:78-134]().

**Constraint Specifications:**
`ConstraintSpec` defines shape dependencies, such as inferring one tensor's shape based on the dimensions of others [tensorrt_llm/_torch/autotuner.py:64-74]().

**Pre-hooks:**
The `inputs_pre_hook` modifies input tensors before profiling to match real data distributions [tensorrt_llm/_torch/autotuner.py:134](). This is used extensively in MoE tuning to prepare dummy top-k tensors [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py:83-99]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:64-139](), [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py:83-99]()

## Cache Management

The `ProfilingCache` persists tuning results to a file, typically `.autotuner_cache.json` [tensorrt_llm/_torch/autotuner.py:302](). It uses a combination of operation name, runner ID, and optimization profile as the cache key [tensorrt_llm/_torch/autotuner.py:421-426](). The cache can be cleared via `clear_cache()` or printed for debugging purposes [tests/unittest/_torch/misc/test_autotuner.py:166-172]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:297-464](), [tests/unittest/_torch/misc/test_autotuner.py:166-172]()

## Distributed Tuning Strategies

The AutoTuner supports four strategies for multi-GPU environments via `DistributedTuningStrategy` [tensorrt_llm/_torch/autotuner.py:32-44]():

- `BROADCAST`: Rank 0 tunes and broadcasts results to other ranks [tensorrt_llm/_torch/autotuner.py:41]().
- `INDEPENDENT`: Each rank tunes independently (default for non-communication ops) [tensorrt_llm/_torch/autotuner.py:42]().
- `MERGE`: All ranks participate in tuning and reach a merged result [tensorrt_llm/_torch/autotuner.py:43]().
- `PARALLEL`: All ranks participate in tuning with partial tactics [tensorrt_llm/_torch/autotuner.py:44]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:32-44](), [tensorrt_llm/_torch/autotuner.py:639-751]()

## Kernel and Op Optimization

### MoE Kernel Optimization
For Mixture of Experts (MoE), the AutoTuner handles selection for various backends. The `MoERunner` class wraps the C++ `FusedMoeRunner` and manages tactics for different GEMM stages [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:67-146](). The system prepares dummy `topk` tensors via `prepare_dummy_topk_and_hook` to simulate expert distributions during profiling [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py:83-99](). This mirrors actual load-balanced (`balanced`) or `random` expert distributions to ensure better end-to-end performance [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py:66-68]().

**Sources:** [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:67-151](), [tensorrt_llm/_torch/custom_ops/trtllm_gen_custom_ops.py:32-111]()

### Quantization and Block Scaling
The autotuning system is utilized for `FP8` and `NVFP4` block-scale kernels. For Blackwell (SM100) architectures, the `CuteDSLNVFP4BlackwellRunner` provides specialized tactics for block-scaled GEMMs [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:53-55](). All-reduce operations also utilize autotuning to select optimal strategies for fused RMSNorm and quantization ops, such as `RESIDUAL_RMS_NORM_QUANT_NVFP4` [tensorrt_llm/_torch/custom_ops/cpp_custom_ops.py:46-51]().

**Sources:** [tensorrt_llm/_torch/custom_ops/torch_custom_ops.py:53-55](), [tensorrt_llm/_torch/custom_ops/cpp_custom_ops.py:46-58]()

## Usage Patterns

### Context Manager
The `autotune()` context manager enables tuning mode globally or for specific code blocks [tensorrt_llm/_torch/autotuner.py:256-296]().

```python
from tensorrt_llm._torch.autotuner import autotune

with autotune(tune_mode=True):
    # Operations here will trigger profiling if not in cache
    output = model(input_tensor)
```

### CUDA Graph Integration
When `use_cuda_graph=True` is set in `TuningConfig`, the AutoTuner captures the kernel execution in a CUDA graph for stable timing measurements during profiling [tensorrt_llm/_torch/autotuner.py:136](), [tensorrt_llm/_torch/autotuner.py:800-868]().

**Sources:** [tensorrt_llm/_torch/autotuner.py:136](), [tensorrt_llm/_torch/autotuner.py:800-868]()

---

