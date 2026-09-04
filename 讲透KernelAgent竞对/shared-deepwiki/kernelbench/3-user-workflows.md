> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/3-user-workflows | 抓取: 2026-09-03 | DeepWiki SSR 快照

# User Workflows

Relevant source files

- .gitignore [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/.gitignore]

- README.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1]

- scripts/eval_from_generations.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py]

- scripts/generate_and_eval_single_sample.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py]

- scripts/generate_and_eval_single_sample_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py]

- scripts/generate_baseline_time_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time_modal.py]

- scripts/generate_samples.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py]

- scripts/run_and_check.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py]

## Overview

This page provides step-by-step guides for the main KernelBench workflows: generating GPU kernels with LLMs, evaluating correctness and performance, and analyzing results. The workflows range from quick single-kernel testing to comprehensive batch benchmarking across all 250 problems.

Child Pages:

- 3.1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.1] - Generating Kernels with LLMs: Batch generation using `generate_samples.py`

- 3.2 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.2] - Batch Evaluation: Evaluating multiple kernels with `eval_from_generations.py`

- 3.3 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.3] - Single Kernel Testing: Quick validation with `run_and_check.py`

- 3.4 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.4] - Generating Baseline Timings: Profiling PyTorch reference implementations

## Core Workflows

KernelBench supports four primary workflows, each implemented by dedicated CLI scripts:

| | Workflow | Script | Purpose | Typical Use Case
| Single kernel testing | `run_and_check.py` | Generate and evaluate one kernel | Quick experimentation, debugging
| Batch generation | `generate_samples.py` | Generate kernels for multiple problems | Comprehensive benchmarking
| Batch evaluation | `eval_from_generations.py` | Evaluate previously generated kernels | Separate generation/evaluation phases
| Baseline profiling | `generate_baseline_time.py` | Profile PyTorch reference performance | Establish speedup baselines

Workflow Diagram: Data Flow Through KernelBench

```

Sources: README.md63-76 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L63-L76] README.md91-131 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L91-L131] scripts/generate_samples.py1-359 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L1-L359] scripts/generate_and_eval_single_sample.py1-287 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L1-L287]

## Workflow 1: Single Kernel Testing

The quickest way to test a single problem. Uses `run_and_check.py` or `generate_and_eval_single_sample.py` to generate and evaluate one kernel.

Code-Level Execution Flow

```

Basic Usage

```

Key Configuration Parameters

| | Parameter | Description | Example Values
| `dataset_src` | Dataset source | `huggingface`, `local`
| `level` | Problem difficulty level | `1`, `2`, `3`
| `problem_id` | Specific problem number | `1` to `100` (varies by level)
| `server_type` | LLM provider | `deepseek`, `openai`, `google`
| `backend` | Kernel framework | `cuda`, `triton`, `cute`, `tilelang`
| `precision` | Tensor precision | `fp32`, `fp16`, `bf16`
| `prompt_option` | Prompting strategy | `zero_shot`, `one_shot`, `few_shot`
| `gpu_arch` | Target GPU architecture | `["Ada"]`, `["Hopper"]`, `["Ampere"]`

Using Modal for Cloud GPU Execution

For users without local GPUs, the Modal version executes evaluation remotely:

```

The Modal version uses `@app.cls(image=image)` and `@modal.method()` decorators to execute `eval_kernel_against_ref()` on remote GPU infrastructure. The GPU architecture is automatically mapped via `gpu_arch_mapping` dictionary.

Sources: README.md92-102 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L92-L102] scripts/generate_and_eval_single_sample.py1-287 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L1-L287] scripts/generate_and_eval_single_sample_modal.py1-288 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py#L1-L288]

## Workflow 2: Batch Kernel Generation

Generate kernels for multiple problems in parallel. Uses `generate_samples.py` with `ThreadPoolExecutor` for concurrent LLM API calls. Detailed in 3.1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.1]

Parallel Generation Architecture

```

Basic Usage

```

Advanced Options

```

Resume Interrupted Runs

The script automatically detects existing kernels via `check_kernel_exists()` and skips regeneration:

```

Key Features

- Parallelization: `maybe_multithread()` uses `ThreadPoolExecutor` to query LLM APIs concurrently

- Rate Limiting: `api_query_interval` parameter controls delay between API calls

- Resumability: Checks for existing kernels before generation, enabling interrupted runs to resume

- Multi-sampling: `num_samples` parameter generates multiple kernels per problem for pass@k analysis

- Storage: All kernels saved to `runs/{run_name}/level_{level}_problem_{problem_id}_sample_{sample_id}_kernel.py`

Sources: README.md113-122 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L113-L122] scripts/generate_samples.py1-359 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L1-L359]

## Workflow 3: Batch Evaluation

Evaluate previously generated kernels for correctness and performance. Uses `eval_from_generations.py` with optional compilation caching and parallel GPU execution. Detailed in 3.2 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.2]

Two-Phase Evaluation Architecture

```

Basic Usage

```

With Compilation Caching

Pre-compile kernels in parallel on CPUs before GPU evaluation:

```

Modal Cloud Execution

For distributed evaluation on cloud GPUs:

```

Output Files

The evaluation produces several output files in `runs/{run_name}/`:

| | File | Content
| `eval_results.json` | Per-kernel correctness and performance results
| `pass_at_k.json` | Pass@k metrics for multi-sample runs
| `eval_config.yaml` | Evaluation configuration for reproducibility

Key Configuration Parameters

| | Parameter | Description | Default
| `num_gpu_devices` | Number of parallel GPU workers | 8
| `timeout` | Max seconds per kernel evaluation | 300
| `build_cache` | Pre-compile before evaluation | False
| `num_cpu_workers` | Parallel compilation workers | 16
| `n_correctness` | Number of correctness trials | 5
| `n_trial` | Number of performance trials | 100

Sources: README.md117-122 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L117-L122]

## Workflow 4: Baseline Performance Profiling

Generate baseline timing measurements for PyTorch reference implementations. Uses `generate_baseline_time.py` to profile different PyTorch execution modes. Detailed in 3.4 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/3.4]

Baseline Generation Process

```

Basic Usage

```

Modal Cloud Profiling

For profiling on specific cloud GPUs:

```

Using Custom Baselines in Analysis

Once generated, baselines are used by `benchmark_eval_analysis.py`:

```

Baseline File Format

Each baseline JSON file contains timing statistics per problem:

```

Sources: README.md123-131 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L123-L131]

## Workflow 5: Performance Analysis

Compute aggregate metrics from evaluation results. Uses `benchmark_eval_analysis.py` to calculate correctness rates, geometric mean speedups, and `fast_p` scores. Detailed in 7.3 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/7.3]

Analysis Pipeline

```

Basic Usage

```

Key Metrics Computed

| | Metric | Formula | Interpretation
| Correctness Rate | `correct_count / total_count` | Fraction of kernels passing all correctness checks
| `fast_0` | Correctness rate | Same as correctness (speedup threshold = 0)
| `fast_1` | Fraction with speedup > 1 | Kernels faster than PyTorch baseline
| `fast_2` | Fraction with speedup > 2 | Kernels at least 2x faster
| Geometric Mean | `(∏ speedups)^(1/n)` | Average speedup across correct kernels

Output Format

The analysis script prints a summary table:

```
`Level 1 Analysis for run: my_level1_run
Hardware: L40S
Baseline: baseline_time_torch
----------------------------------------
Total Problems: 100
Correct: 85 (85.0%)
fast_0: 85.0%
fast_1: 72.0%
fast_2: 58.0%
Geometric Mean Speedup: 3.42x
`

Sources: README.md123-128 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L123-L128]

## Common Configuration Patterns

LLM Provider Selection

KernelBench uses `SERVER_PRESETS` dictionary to configure LLM providers:

```

Backend and Precision Selection

Different kernel frameworks require different configurations:

| | Backend | Precision Support | Compilation Method | Example Use Case
| `cuda` | fp32, fp16, bf16 | `torch.utils.cpp_extension.load_inline()` | Raw CUDA kernels
| `triton` | fp32, fp16, bf16 | JIT via `tempfile` | Triton DSL kernels
| `cute` | fp32, fp16, bf16 | CuTe template library | Tensor layout optimization
| `tilelang` | fp16 only | TileLang compiler | Tile-based programming

Execution Mode Selection

```

Sources: scripts/generate_samples.py213-330 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_samples.py#L213-L330] scripts/generate_and_eval_single_sample.py99-241 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample.py#L99-L241] scripts/generate_and_eval_single_sample_modal.py32-93 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_and_eval_single_sample_modal.py#L32-L93]

## Summary of Key Scripts and Their Roles

| | Script | Purpose | Use Case
| `scripts/generate_and_eval_single_sample.py` | Generate and evaluate a single kernel | Quick testing, debugging
| `scripts/generate_and_eval_single_sample_modal.py` | Generate and evaluate a single kernel using Modal | For users without a local GPU
| `scripts/generate_samples.py` | Generate kernels in batch | Comprehensive benchmarking
| `scripts/eval_from_generations.py` | Evaluate previously generated kernels | Separate evaluation phase
| `scripts/benchmark_eval_analysis.py` | Analyze evaluation results | Computing benchmark metrics
| `scripts/generate_baseline_time.py` | Generate baseline timing for comparison | For custom hardware setups

Sources: README.md80-112 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/README.md?plain=1#L80-L112]

DismissRefresh this wiki

