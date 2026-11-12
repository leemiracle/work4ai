> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/6-configuration-and-execution | 抓取: 2026-09-03 | DeepWiki SSR 快照

# Configuration and Execution

Relevant source files

- .gitignore [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/.gitignore]

- README.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1]

- scripts/eval_from_generations.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py]

- scripts/generate_and_eval_single_sample.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py]

- scripts/generate_and_eval_single_sample_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py]

- scripts/generate_baseline_time_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time_modal.py]

- scripts/generate_samples.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py]

- scripts/run_and_check.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py]

This document describes the configuration system used throughout KernelBench and the two execution environments (local GPU and Modal cloud). It explains how to configure evaluation parameters, select backends and precision, and parallelize workloads across GPUs.

For information about prompt construction parameters, see Prompt Engineering [/ScalingIntelligence/KernelBench/4-prompt-engineering]. For details on timing and profiling configuration, see Timing and Profiling [/ScalingIntelligence/KernelBench/2.5-timing-and-profiling]. For batch evaluation workflows, see Batch Evaluation [/ScalingIntelligence/KernelBench/3.2-batch-evaluation].

## Overview

KernelBench uses a pydra-based configuration system that provides type-safe, command-line-driven configuration across all scripts. The system supports two execution modes:

- Local execution: Uses multiprocessing to parallelize across local GPUs

- Modal execution: Deploys to Modal's cloud platform for scalable, heterogeneous GPU access

All major scripts (`generate_and_eval_single_sample.py`, `eval_from_generations.py`, `generate_samples.py`, `run_and_check.py`) follow the same configuration pattern, making it easy to transfer knowledge between workflows.

## Configuration Architecture

```

Sources: scripts/eval_from_generations.py84-153 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L84-L153] scripts/generate_samples.py32-93 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L32-L93] scripts/run_and_check.py85-127 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py#L85-L127] scripts/generate_and_eval_single_sample.py30-92 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L30-L92]

## Configuration Classes

KernelBench provides three primary configuration classes that extend `pydra.Config`:

### EvalConfig

Used by `eval_from_generations.py` for batch evaluation of generated kernels.

Key Parameters:

| | Parameter | Type | Default | Description
| `run_name` | str | REQUIRED | Name of the run directory containing generated kernels
| `dataset_src` | str | REQUIRED | "huggingface" or "local"
| `level` | int | REQUIRED | Problem level (1, 2, or 3)
| `subset` | tuple | (None, None) | (start_id, end_id) to evaluate a subset of problems
| `problem_ids` | list | None | Specific problem IDs to evaluate (overrides subset)
| `eval_mode` | str | "local" | "local" for local GPUs, "modal" for cloud
| `gpu` | str | "A10G" | GPU type for Modal (L40S, H100, A100, L4, T4, A10G)
| `gpu_arch` | list | ["Ada"] | CUDA architecture targets (Ada, Hopper, Ampere, Turing)
| `backend` | str | "cuda" | Backend DSL (cuda, triton, cute, tilelang, thunderkittens)
| `precision` | str | "fp32" | Tensor precision (fp32, fp16, bf16)
| `num_correct_trials` | int | 5 | Number of correctness validation trials
| `num_perf_trials` | int | 100 | Number of performance measurement trials
| `timeout` | int | 180 | Timeout per sample in seconds
| `timing_method` | str | "cuda_event" | Timing method (cuda_event, do_bench, host_time, nsight)
| `num_gpu_devices` | int | 1 | Number of parallel GPUs (local) or containers (Modal)
| `build_cache` | bool | False | Pre-compile kernels on CPU before GPU evaluation
| `num_cpu_workers` | int | 20 | Number of CPU workers for build cache

Sources: scripts/eval_from_generations.py84-153 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L84-L153]

### GenerationConfig

Used by `generate_samples.py` for batch kernel generation.

Key Parameters:

| | Parameter | Type | Default | Description
| `run_name` | str | REQUIRED | Name for this generation run
| `dataset_src` | str | REQUIRED | "huggingface" or "local"
| `level` | int | REQUIRED | Problem level (1, 2, or 3)
| `subset` | tuple | (None, None) | (start_id, end_id) to generate subset
| `backend` | str | "cuda" | Target backend DSL
| `precision` | str | "fp32" | Tensor precision
| `prompt_option` | str | "one_shot" | Prompting strategy (zero_shot, one_shot, few_shot)
| `include_hardware_info` | bool | False | Inject GPU specs into prompt
| `hardware_gpu_name` | str | None | GPU name for hardware-aware prompting
| `custom_prompt_key` | str | None | Custom prompt template key
| `server_type` | str | None | LLM server preset (deepseek, google, openai, anthropic)
| `model_name` | str | None | Model name for inference
| `max_tokens` | int | None | Maximum generation tokens
| `temperature` | float | 0.0 | Sampling temperature
| `is_reasoning_model` | bool | False | Enable for o1, o3, Gemini thinking models
| `reasoning_effort` | str | "low" | Effort level for reasoning models (low, medium, high)
| `num_workers` | int | 64 | Parallel API query workers
| `num_samples` | int | 1 | Samples per problem (for pass@k analysis)
| `check_kernel` | bool | True | Enable static code validation

Sources: scripts/generate_samples.py32-93 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L32-L93]

### ScriptConfig

Used by `run_and_check.py` for testing single kernel/reference pairs.

Key Parameters:

| | Parameter | Type | Default | Description
| `ref_origin` | str | REQUIRED | "local" or "kernelbench"
| `ref_arch_src_path` | str | "" | Path to reference file (if ref_origin=local)
| `dataset_src` | str | "huggingface" | Dataset source (if ref_origin=kernelbench)
| `level` | int | "" | Problem level (if ref_origin=kernelbench)
| `problem_id` | int | "" | Problem ID (if ref_origin=kernelbench)
| `kernel_src_path` | str | "" | Path to kernel solution file
| `eval_mode` | str | "local" | "local" or "modal"
| `gpu` | str | "L40S" | GPU type for Modal
| `gpu_arch` | list | ["Ada"] | CUDA architecture targets
| `backend` | str | "cuda" | Backend DSL
| `precision` | str | "fp32" | Tensor precision
| `num_correct_trials` | int | 5 | Correctness validation trials
| `num_perf_trials` | int | 100 | Performance measurement trials
| `timeout` | int | 300 | Timeout in seconds
| `timing_method` | str | "cuda_event" | Timing method
| `build_dir_prefix` | str | "" | Custom build directory
| `check_kernel` | bool | True | Enable static validation

Sources: scripts/run_and_check.py85-127 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py#L85-L127]

## GPU Architecture Configuration

The `gpu_arch` parameter controls which CUDA architectures the kernel is compiled for by setting the `TORCH_CUDA_ARCH_LIST` environment variable.

### Architecture Mapping

```

Usage:

```

The function sets `TORCH_CUDA_ARCH_LIST` which PyTorch uses during kernel compilation via `torch.utils.cpp_extension.load_inline()`.

Modal GPU Architecture Mapping:

```

Sources: kernelbench/utils.py46-63 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/kernelbench/utils.py#L46-L63] scripts/eval_from_generations.py54 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L54-L54] scripts/run_and_check.py16-25 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py#L16-L25]

## Backend and Precision Configuration

KernelBench supports five GPU kernel DSLs with varying precision constraints:

### Backend Configurations

| | Backend | Default Precision | Supported Precisions | Special Requirements
| `cuda` | fp32 | fp32, fp16, bf16 | None
| `triton` | fp32 | fp32, fp16, bf16 | None
| `cute` | fp32 | fp32, fp16, bf16 | None
| `tilelang` | fp16 (forced) | fp16 | `hardware_gpu_name` required for prompting
| `thunderkittens` | bf16 (forced) | bf16, fp16 | H100 GPU recommended, `THUNDERKITTENS_ROOT` env var

### Backend Validation and Auto-Configuration

The system automatically validates backend selections and applies constraints:

```

TileLang Requirements:

- Forced to fp16 precision

- Requires `hardware_gpu_name` parameter when using `include_hardware_info=True`

- GPU name used for hardware-specific prompt construction

ThunderKittens Requirements:

- Forced to bf16 precision

- Requires `THUNDERKITTENS_ROOT` environment variable pointing to ThunderKittens installation

- Recommends H100 GPU (auto-configured in Modal mode)

- Modal setup includes cloning ThunderKittens repo in container image

Sources: scripts/generate_samples.py237-247 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L237-L247] scripts/generate_and_eval_single_sample.py177-190 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L177-L190] scripts/eval_from_generations.py784-787 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L784-L787]

## Execution Mode: Local vs Modal

```

Sources: scripts/eval_from_generations.py789-800 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L789-L800] scripts/eval_from_generations.py584-586 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L584-L586] scripts/eval_from_generations.py439-568 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L439-L568]

### Local Execution

Requirements:

- CUDA-capable GPU(s) available locally

- PyTorch with CUDA support installed

- Direct hardware access

Setup:

```

Configuration Example:

```

Parallelization:

- Uses `multiprocessing.Pool` with `num_gpu_devices` workers

- Each worker assigned to specific GPU via `torch.device(f"cuda:{i%num_gpu_devices}")`

- Work distributed in batches matching pool size

- Timeout enforced per batch via `Pool.apply_async().get(timeout=config.timeout)`

Sources: scripts/eval_from_generations.py589-707 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L589-L707] scripts/eval_from_generations.py789-799 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L789-L799]

### Modal Execution

Requirements:

- Modal account and authentication (`modal token new`)

- No local GPU required

- Network connectivity for Modal API

Setup:

```

Configuration Example:

```

Modal Image Configuration:

The Modal container image is pre-configured with all dependencies:

```

GPU Attachment and Retry Logic:

Modal includes sophisticated error handling for GPU allocation:

```

Retry Configuration:

```

GPU Corruption Handling:

If a GPU enters a corrupted state during evaluation (CUDA errors, illegal memory access), the container is retired:

```

Sources: scripts/eval_from_generations.py65-81 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L65-L81] scripts/eval_from_generations.py165-253 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L165-L253] scripts/eval_from_generations.py439-568 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L439-L568]

### Execution Mode Comparison

| | Feature | Local | Modal
| GPU Hardware | Must own/access GPUs | Cloud GPUs on-demand
| Setup Complexity | CUDA installation required | Modal token only
| Parallelization | Limited by local GPUs | Virtually unlimited containers
| GPU Types | Fixed hardware | L40S, H100, A100, L4, T4, A10G
| Heterogeneous GPUs | Not supported | Supported
| Cost | Hardware depreciation | Per-second usage
| Isolation | Process-level | Container-level
| Error Recovery | Process restart | Container replacement
| Development Speed | Faster iteration | Network latency
| Reproducibility | Environment dependent | Consistent Docker images

When to Use Local:

- Rapid prototyping and debugging

- Limited evaluation workloads

- Specific hardware requirements not available on Modal

- No network connectivity or Modal access

When to Use Modal:

- Large-scale evaluation campaigns

- Heterogeneous GPU testing (comparing L40S vs H100 vs A100)

- No local GPU access

- Desire for isolated, reproducible environments

- Parallel evaluation across many GPUs

Sources: scripts/eval_from_generations.py584-707 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L584-L707] scripts/eval_from_generations.py439-568 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L439-L568]

## Parallel Execution Strategies

### Local Multiprocessing

Local execution uses Python's `multiprocessing.Pool` to parallelize across GPUs:

```

Implementation:

The batch evaluation loop processes work in chunks matching the GPU count:

```

Device Assignment:

Each worker gets a specific GPU via modulo assignment:

```

Timeout Handling:

Timeouts are enforced at the batch level with per-sample remaining time calculation:

```

Sources: scripts/eval_from_generations.py570-707 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L570-L707]

### Modal Async Futures

Modal execution uses `.spawn()` to create parallel futures across cloud containers:

```

Implementation:

Modal batch evaluation spawns tasks in parallel:

```

Dynamic GPU Selection:

Modal allows per-call GPU specification via `.with_options()`:

```

GPU Attachment Wait:

Each container waits for GPU attachment with progressive backoff:

```

Error Handling:

Modal has two-level error catching:

- Inner catch (inside `evaluate_single_sample_modal`): Handles CUDA errors and marks GPU as corrupted

- Outer catch (in `future.get()`): Handles Modal infrastructure failures

```

Sources: scripts/eval_from_generations.py439-568 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L439-L568] scripts/eval_from_generations.py176-253 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L176-L253]

## Build Cache Optimization

For local evaluation, KernelBench supports pre-compiling kernels on CPU before GPU evaluation:

### Build Cache Flow

```

Configuration:

```

Implementation:

```

Build Directory:

Cached builds are stored in:

```
`cache/
└── {run_name}/
└── {problem_id}/
└── {sample_id}/
├── *.so (compiled shared objects)
└── *.o (object files)
`

Benefits:

- Parallelizes compilation across CPU cores (typically more than GPU count)

- Reduces GPU idle time during evaluation

- Allows retrying failed evaluations without recompilation

- Particularly useful for large batches (100+ samples)

Trade-offs:

- Requires additional disk space for cached builds

- Only beneficial for batch evaluation (single samples compile fast enough)

- Not supported for Modal execution (containers handle compilation internally)

Sources: scripts/eval_from_generations.py842-845 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L842-L845] scripts/eval_from_generations.py128-137 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L128-L137]

## Command-Line Usage Examples

### Single Sample Generation + Evaluation

```

### Batch Generation

```

### Batch Evaluation

```

### Testing Single Kernel

```

Sources: scripts/generate_and_eval_single_sample.py1-281 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L1-L281] scripts/generate_samples.py1-354 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L1-L354] scripts/eval_from_generations.py1-948 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L1-L948] scripts/run_and_check.py1-395 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py#L1-L395]

## Configuration File Format

KernelBench uses pydra's YAML format for saving configuration. Generated runs automatically save their config:

```

This config can be loaded for reproducibility or modified for follow-up runs.

Sources: scripts/generate_samples.py291 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L291-L291]

## Summary

The KernelBench configuration system provides:

- Unified Configuration: Pydra-based config classes (`EvalConfig`, `GenerationConfig`, `ScriptConfig`) with type safety and command-line parsing

- Dual Execution Modes: Local multiprocessing for owned GPUs, Modal cloud for scalable heterogeneous evaluation

- Backend Flexibility: Five GPU DSLs (CUDA, Triton, CuTe, TileLang, ThunderKittens) with automatic precision constraints

- GPU Architecture Control: `gpu_arch` parameter sets compilation targets via `TORCH_CUDA_ARCH_LIST`

- Parallel Execution: Multiprocessing pools (local) or async futures (Modal) with sophisticated error handling

- Build Optimization: Optional CPU-based build cache for faster batch evaluation

The system is designed for both rapid prototyping (single samples, local execution) and large-scale evaluation campaigns (batches, Modal execution, heterogeneous GPUs).

DismissRefresh this wiki

