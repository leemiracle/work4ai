> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/1-overview | 抓取: 2026-09-03 | DeepWiki SSR 快照

# Overview

Relevant source files

- EVAL.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1]

- README.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1]

- requirements.txt [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/requirements.txt]

- scripts/generate_and_eval_single_sample.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py]

- scripts/generate_and_eval_single_sample_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py]

- scripts/generate_samples.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py]

- src/kernelbench/profile.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py]

## Purpose and Scope

KernelBench is a benchmark framework for evaluating large language models' (LLMs) ability to generate efficient GPU kernels from PyTorch operator specifications. This document provides a high-level introduction to KernelBench's architecture, components, and workflows.

For detailed information on specific subsystems:

- Dataset structure and problem hierarchy: see Dataset Management [/ScalingIntelligence/KernelBench/2.3-dataset-management] and KernelBench Problems [/ScalingIntelligence/KernelBench/5-kernelbench-problems]

- Kernel evaluation methodology: see Kernel Evaluation System [/ScalingIntelligence/KernelBench/2.1-kernel-evaluation-system] and Evaluation Metrics [/ScalingIntelligence/KernelBench/7.1-evaluation-metrics]

- LLM integration and generation: see LLM Integration [/ScalingIntelligence/KernelBench/2.2-llm-integration] and Generating Kernels with LLMs [/ScalingIntelligence/KernelBench/3.1-generating-kernels-with-llms]

- Supported backends and DSLs: see Backend Support [/ScalingIntelligence/KernelBench/2.4-backend-support]

Sources: README.md1-177 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L1-L177]

## The Benchmark Task

KernelBench frames the problem as a code transpilation task: given a PyTorch operator implementation (reference architecture), an LLM must generate an optimized GPU kernel in one of five supported domain-specific languages (DSLs).

```

Evaluation Criteria:

- Correctness: Generated kernels must produce outputs matching PyTorch reference (via `torch.allclose`)

- Performance: Kernel runtime is compared against PyTorch eager or `torch.compile` baselines to compute speedup

The benchmark consists of 200 problems organized into three complexity levels:

- Level 1 (100 problems): Single-kernel operators (matrix multiplication, activations, normalization, convolutions)

- Level 2 (~100 problems): Fused operation patterns (Conv+ReLU+Bias, Matmul+BatchNorm+GELU)

- Level 3 (50 problems): Full model architectures (ResNet, GPT blocks, LSTM, U-Net)

Sources: README.md18-31 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L18-L31] README.md34-61 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L34-L61]

## System Architecture

The following diagram shows how the major components interact in the KernelBench system:

```

Key architectural decisions:

- 
Unified Dataset Abstraction: The `BaseDataset` interface provides a consistent API for accessing problems regardless of storage location (HuggingFace or local filesystem)

- 
Pluggable Backend System: Five GPU kernel DSLs are supported through a backend parameter (`cuda`, `triton`, `cute`, `tilelang`, `thunderkittens`)

- 
Dual Execution Modes: Evaluation can run on local GPUs (via multiprocessing) or Modal cloud infrastructure (via serverless containers)

- 
Modular Prompt Construction: TOML-based templates enable customization of prompts for different backends, shot configurations, and hardware contexts

Sources: README.md63-78 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L63-L78] scripts/generate_and_eval_single_sample.py1-281 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L1-L281] scripts/generate_samples.py1-354 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L1-L354]

## Core Configuration Classes

KernelBench uses pydra-based configuration dataclasses to manage system parameters. The main configuration classes map directly to workflow stages:

```

`EvalConfig` (Single Sample Workflow):

- Dataset Selection: `dataset_src` (huggingface/local), `dataset_name`, `level`, `problem_id`

- Evaluation Environment: `eval_mode` (local/modal), `gpu_arch` (Ada/Hopper/Ampere), `precision` (fp32/fp16/bf16)

- LLM Integration: `server_type`, `model_name`, `max_tokens`, `temperature`

- Backend & Timing: `backend` (cuda/triton/cute/tilelang/thunderkittens), `timing_method` (cuda_event/do_bench/host_time/nsight)

- Prompt Configuration: `prompt_option` (zero_shot/one_shot/few_shot), `include_hardware_info`, `custom_prompt_key`

`GenerationConfig` (Batch Generation Workflow):

- Extends `EvalConfig` fields with batch-specific parameters

- Run Management: `run_name` (output directory), `runs_dir` (parent directory)

- Parallelization: `num_workers` (thread pool size), `api_query_interval` (rate limiting)

- Sample Generation: `num_samples` (per problem, for pass@k analysis), `subset` (problem ID range)

Sources: scripts/generate_and_eval_single_sample.py30-92 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L30-L92] scripts/generate_samples.py32-94 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L32-L94]

## Primary Workflows

KernelBench provides three main user workflows, each implemented as a standalone script:

```

### Workflow 1: Single Sample (`generate_and_eval_single_sample.py`)

Purpose: Quick experimentation and debugging on a single problem

Key Functions:

- `construct_kernelbench_dataset()` - Load dataset

- `get_prompt_for_backend()` - Build prompt from TOML templates

- `create_inference_server_from_presets()` - Create LLM client

- `extract_first_code()` - Parse generated code from LLM response

- `validate_kernel_static()` - Optional static validation

- `eval_kernel_against_ref()` - Correctness and performance testing

Example Command:

```

### Workflow 2: Batch Generation (`generate_samples.py`)

Purpose: Generate multiple kernel samples across problems for benchmarking

Key Components:

- `generate_sample_single()` - Core generation logic per (problem, sample) pair

- `maybe_multithread()` - Parallel API calls with configurable workers

- File-based storage: `runs/{run_name}/level_{level}_problem_{pid}_sample_{sid}_kernel.py`

Features:

- Configurable sampling: `num_samples` per problem for pass@k analysis

- Subset execution: `subset=(start, end)` for problem ID ranges

- Duplicate detection: Skips existing kernel files

- Static validation: Optional `check_kernel=True`

### Workflow 3: Batch Evaluation (`eval_from_generations.py`)

Purpose: Evaluate generated kernels from batch generation runs

Key Features:

- Multi-GPU parallelization via `multiprocessing.Pool`

- Optional build cache: Pre-compile kernels on CPUs before GPU evaluation

- Results persistence: `eval_results.json` with per-sample outcomes

Related Workflows:

- Baseline Generation: See Generating Baseline Timings [/ScalingIntelligence/KernelBench/3.4-generating-baseline-timings]

- Results Analysis: See Results Analysis [/ScalingIntelligence/KernelBench/7.3-results-analysis]

Sources: scripts/generate_and_eval_single_sample.py94-281 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L94-L281] scripts/generate_samples.py202-353 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L202-L353] README.md104-147 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L104-L147]

## Backend Support Matrix

KernelBench supports five GPU kernel domain-specific languages (DSLs), each with specific precision and compilation requirements:

| | Backend | Language | Default Precision | Architecture Support | Compilation Method
| `cuda` | C++/CUDA | fp32 | All | `torch.utils.cpp_extension.load_inline()`
| `triton` | Python (Triton) | fp32 | All | `@triton.jit` decorator
| `cute` | C++ (CUTLASS) | fp32 | Ampere+ | CUTLASS DSL templates
| `tilelang` | Python | fp16 (enforced) | All | TileLang compiler
| `thunderkittens` | C++ (TK primitives) | bf16 | Hopper+ | `torch.utils.cpp_extension.load_inline()`

Backend-Specific Considerations:

CUDA Backend:

- Direct CUDA kernel compilation via PyTorch's extension loader

- Full control over memory hierarchy and thread scheduling

- Requires `torch.utils.cpp_extension.load_inline()` with proper compiler flags

Triton Backend:

- Python-based GPU programming with automatic optimization

- Kernels decorated with `@triton.jit`

- Block-level programming model

CuTe Backend:

- NVIDIA CUTLASS library integration

- Template-based abstractions for tensor operations

- Requires Ampere architecture or newer

TileLang Backend:

- Enforces `fp16` precision automatically

- Requires `hardware_gpu_name` parameter for hardware-specific optimization

- Python-based tile programming

ThunderKittens Backend:

- Specialized for Hopper architecture (H100)

- Uses `bf16` precision by default

- Requires `THUNDERKITTENS_ROOT` environment variable pointing to library installation

Sources: scripts/generate_and_eval_single_sample.py177-190 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L177-L190] README.md117-124 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L117-L124] scripts/generate_and_eval_single_sample_modal.py28-29 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py#L28-L29]

## Execution Environments

```

### Local Execution

Characteristics:

- Requires local CUDA-capable GPU

- Uses Python's `multiprocessing.Pool` for multi-GPU parallelization

- Direct hardware access for timing measurements

- Immediate result availability

Configuration:

```

GPU Architecture Mapping:

- Controlled via `set_gpu_arch()` utility function

- Sets `TORCH_CUDA_ARCH_LIST` environment variable for compilation

### Modal Cloud Execution

Characteristics:

- Serverless GPU containers on Modal infrastructure

- Heterogeneous GPU fleet: L40S, H100, A100, T4, L4, A10G

- Containerized environment with CUDA 12.8 and all dependencies

- Async parallel execution via `spawn()` futures

Modal Image Configuration:

```

GPU Selection:

```

Usage:

```

Sources: scripts/generate_and_eval_single_sample_modal.py92-134 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py#L92-L134] README.md99-101 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L99-L101]

## Evaluation Methodology

The `eval_kernel_against_ref()` function is the core evaluation primitive, implementing a two-phase validation process:

### Phase 1: Correctness Validation

Process:

- Generate `n_correctness` (default: 5-10) random input tensors with different seeds

- Execute reference PyTorch model: `ref_output = ref_model(*inputs)`

- Execute generated kernel: `gen_output = custom_model(*inputs)`

- Compare outputs: `torch.allclose(ref_output, gen_output, rtol=..., atol=...)`

- All trials must pass for kernel to be considered correct

### Phase 2: Performance Measurement

Timing Methods (via `timing_method` parameter):

| | Method | Description | Use Case
| `cuda_event` | Device-side timing with L2 cache clearing | Most accurate, default choice
| `do_bench` | Triton's adaptive benchmark (warmup=25ms, rep=100ms) | Triton kernels
| `host_time` | CPU wall-clock E2E latency | Host-device transfer overhead
| `nsight` | Hardware counters via `nsight-python` | Profiling, not default eval

Process:

- Warmup phase: `num_warmup` iterations

- L2 cache clearing (256MB thrash tensor) before each trial

- Run `n_perf_trials` (default: 100) timing measurements

- Compute statistics: mean, std, min, max

- Calculate speedup: `baseline_time / generated_time`

### Key Evaluation Functions

```

Suspicious Result Detection:

- Speedups >2x trigger warnings

- Adversarial test suite: `test_eval_adversarial.py`

- Known exploits: cached computation reuse, input modification, non-default CUDA streams

Sources: README.md34-61 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L34-L61] EVAL.md1-57 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L1-L57] scripts/generate_and_eval_single_sample.py258-268 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L258-L268]

## Performance Metrics

KernelBench defines specialized metrics that capture both correctness and performance:

### Primary Metric: `fast_p`

Definition: Fraction of problems where generated kernel is both correct AND achieves speedup ≥ p

Common Thresholds:

- `fast_0`: Correctness rate (speedup ≥ 0)

- `fast_1`: Faster than PyTorch baseline (speedup ≥ 1)

- `fast_2`: At least 2× faster than baseline (speedup ≥ 2)

Calculation:

```

### Secondary Metric: `pass@k`

Definition: Probability that at least 1 of k generated samples is correct

Use Case: Multi-sample generation with best-of-k selection

Common Values: k ∈ {1, 5, 10, 20, 100}

### Supporting Metrics

- Compilation Rate: % of kernels that compile successfully

- Correctness Rate: % of compiled kernels that are correct

- Geometric Mean Speedup: Geometric average of speedups across correct kernels only

Analysis Script:

```

Sources: README.md44-61 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L44-L61] README.md139-147 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L139-L147]

## Getting Started

### Installation

```

### Quick Start: Single Problem

```

### Batch Benchmarking

```

### Modal Cloud Setup

```

Sources: README.md80-147 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L80-L147]

## Repository Structure

```
`KernelBench/
├── KernelBench/ # Dataset files (levels 1-3)
│ ├── level1/
│ ├── level2/
│ └── level3/
├── src/kernelbench/ # Core library code
│ ├── dataset.py # BaseDataset, construct_kernelbench_dataset()
│ ├── eval.py # eval_kernel_against_ref()
│ ├── timing.py # cuda_event_timing(), do_bench_timing()
│ ├── prompt_constructor_toml.py # get_prompt_for_backend()
│ ├── kernel_static_checker.py # validate_kernel_static()
│ ├── utils.py # Helper functions
│ └── prompts/ # TOML templates and examples
├── scripts/ # User-facing workflow scripts
│ ├── generate_and_eval_single_sample.py
│ ├── generate_samples.py
│ ├── eval_from_generations.py
│ ├── benchmark_eval_analysis.py
│ └── generate_baseline_time.py
├── results/ # Baseline timing data
│ └── timing/ # Per-hardware baseline times
├── runs/ # Generated kernels and results
│ └── {run_name}/
│ ├── level_X_problem_Y_sample_Z_kernel.py
│ └── eval_results.json
└── pyproject.toml # Dependencies and configuration
`

Sources: README.md63-78 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L63-L78]

DismissRefresh this wiki

