> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/7-analysis-and-metrics | 抓取: 2026-09-03 | DeepWiki SSR 快照

# Analysis and Metrics

Relevant source files

- .gitignore [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/.gitignore]

- EVAL.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1]

- requirements.txt [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/requirements.txt]

- scripts/benchmark_eval_analysis.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py]

- scripts/eval_from_generations.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py]

- scripts/generate_baseline_time.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py]

- scripts/generate_baseline_time_modal.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time_modal.py]

- scripts/inspect_baseline.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/inspect_baseline.py]

- scripts/run_and_check.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py]

- src/kernelbench/dataset.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py]

- src/kernelbench/profile.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py]

This document describes KernelBench's evaluation methodology and performance metrics system. It covers how generated kernels are validated for correctness, measured for performance, compared against baselines, and scored using aggregate metrics. For information about the evaluation pipeline that produces these metrics, see Kernel Evaluation System [/ScalingIntelligence/KernelBench/2.1-kernel-evaluation-system]. For profiling tools and debugging, see Profiling and Debugging [/ScalingIntelligence/KernelBench/8.3-profiling-and-debugging].

## Evaluation Methodology

KernelBench evaluates generated kernels through a two-phase process: correctness validation followed by performance measurement.

### Correctness Validation Flow

```

Sources: src/kernelbench/eval.py200-350 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L200-L350]

The correctness validation uses `torch.allclose` with configurable tolerances to compare outputs. Each trial uses different random inputs generated with different seeds to ensure the kernel works correctly across multiple input patterns. All trials must pass for the kernel to be considered correct.

### Performance Measurement Flow

```

Sources: src/kernelbench/timing.py1-200 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L1-L200] scripts/eval_from_generations.py315-328 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L315-L328]

Performance is only measured for kernels that pass correctness validation. The system supports multiple timing methods (see Timing and Profiling [/ScalingIntelligence/KernelBench/2.5-timing-and-profiling]) and includes warmup iterations and L2 cache clearing to ensure consistent measurements.

## Core Result Structure

### KernelExecResult Dataclass

The `KernelExecResult` dataclass encapsulates all evaluation outcomes:

```

Sources: src/kernelbench/eval.py50-60 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L50-L60]

This structure flows through the evaluation pipeline and is serialized to JSON in evaluation result files.

### Result Storage Format

```

Sources: scripts/eval_from_generations.py722-756 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L722-L756] scripts/eval_from_generations.py958-964 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L958-L964]

Evaluation results are stored in the `runs/{run_name}/` directory as JSON files. The `add_to_eval_results_file()` function appends results as they complete, enabling resumable evaluation.

## Aggregate Metrics

### Compilation and Correctness Rates

| | Metric | Formula | Description
| `compilation_rate` | `compiled_count / total_count` | Percentage of kernels that compiled successfully
| `correctness_rate` | `correct_count / total_count` | Percentage of kernels that are both compiled and correct

Sources: scripts/benchmark_eval_analysis.py149-152 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L149-L152]

These basic success rates provide a high-level view of model performance. Note that correctness requires compilation, so `correctness_rate ≤ compilation_rate`.

### Speedup Calculation

Speedup is computed by comparing generated kernel runtime against baseline reference runtime:

```

Sources: scripts/run_and_check.py385-389 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/run_and_check.py#L385-L389]

Speedup values greater than 1.0 indicate the generated kernel is faster than the baseline. The system flags suspiciously high speedups (>2.0x) for potential reward hacking (see Static Validation [/ScalingIntelligence/KernelBench/8.2-static-validation]).

### Geometric Mean Speedup

The geometric mean speedup aggregates performance across problems:

```

Sources: src/kernelbench/score.py1-30 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/score.py#L1-L30]

The geometric mean is preferred over arithmetic mean because it:

- Is less sensitive to outliers (one very fast kernel doesn't dominate)

- Properly handles ratios and proportional changes

- Gives equal weight to speedups and slowdowns (2x faster and 2x slower cancel out)

### fast_p Score

The `fast_p` metric captures both correctness and performance in a single score:

```

Definition: `fast_p` is the percentage of problems where the kernel is both correct AND achieves speedup ≥ p.

Sources: src/kernelbench/score.py40-60 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/score.py#L40-L60] scripts/benchmark_eval_analysis.py205-209 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L205-L209]

Common threshold values:

| | Threshold (p) | Meaning
| 0.0 | Correctness rate (no speedup requirement)
| 0.5 | At least 50% of baseline speed
| 0.8 | At least 80% of baseline speed
| 1.0 | At least as fast as baseline
| 1.5 | 1.5x faster than baseline
| 2.0 | 2x faster than baseline

Sources: scripts/benchmark_eval_analysis.py205 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L205-L205]

The `fast_p` metric is the primary performance metric for KernelBench because it:

- Penalizes incorrect kernels (they contribute 0 to the score)

- Requires both correctness and performance

- Provides interpretable thresholds aligned with real deployment requirements

- Is robust to outliers (unlike geometric mean)

### pass@k Metrics

The `pass@k` metric measures the probability that at least one of k generated samples is correct:

```

Sources: scripts/eval_from_generations.py853-861 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L853-L861]

This formula is an unbiased estimator from the paper "Evaluating Large Language Models Trained on Code" [https://arxiv.org/abs/2107.03374]. It estimates the probability without requiring actual sampling of k combinations.

Typical k values: [1, 5, 10, 20, 100]

Sources: scripts/eval_from_generations.py149 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L149-L149]

Pass@k Calculation Flow:

```

Sources: scripts/eval_from_generations.py864-970 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L864-L970]

Pass@k is automatically calculated when `num_samples_per_problem > 1` in the evaluation configuration.

## Baseline Performance System

Baseline timings provide reference performance for speedup calculation. KernelBench supports multiple baseline variants to account for different optimization levels.

### Baseline Variants

| | Baseline | Description | Typical Use Case
| `baseline_time_torch.json` | PyTorch eager mode | Comparing against unoptimized PyTorch
| `baseline_time_torch_compile_inductor_default.json` | `torch.compile(mode="default")` | Comparing against default torch.compile
| `baseline_time_torch_compile_inductor_max-autotune.json` | `torch.compile(mode="max-autotune")` | Comparing against aggressive compilation
| `baseline_time_torch_compile_cudagraphs.json` | `torch.compile(backend="cudagraphs")` | Comparing against CUDA graphs

Sources: scripts/generate_baseline_time.py186-204 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L186-L204]

### Baseline Generation

Baseline generation can run locally or on Modal for specific hardware:

```

Sources: scripts/generate_baseline_time.py113-148 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L113-L148] scripts/generate_baseline_time_modal.py197-253 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time_modal.py#L197-L253]

Local generation:

```

Modal generation (for specific hardware):

```

Sources: scripts/generate_baseline_time_modal.py256-287 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time_modal.py#L256-L287]

### Baseline Storage Structure

```

Baseline files are organized by level and indexed by problem name (filename). Each entry contains timing statistics from multiple trials.

Sources: scripts/generate_baseline_time.py143-147 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L143-L147]

## Results Analysis

### Analysis Script: benchmark_eval_analysis.py

The `benchmark_eval_analysis.py` script computes aggregate metrics from evaluation results:

```

Sources: scripts/benchmark_eval_analysis.py18-31 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L18-L31]

### Analysis Flow

```

Sources: scripts/benchmark_eval_analysis.py70-284 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L70-L284]

### Analysis Output

The analysis script produces formatted output with multiple sections:

Example output:

```
`────────────────────────────────────────────────────────────────────────────────
Eval Summary for my_experiment
────────────────────────────────────────────────────────────────────────────────
Total test cases with Eval Results: 100 out of 100
Successfully compiled: 95
Functionally correct: 85

Success rates:
Compilation rate: 95.0%
Correctness rate: 85.0%

Speedup Metrics:
Geometric mean of speedup for correct samples: 1.234

Fast_p Results:
+-------------------------+-----------------+
| Speedup Threshold (p) | Fast_p Score |
+=========================+=================+
| 0.0 | 0.85 |
| 0.5 | 0.82 |
| 0.8 | 0.78 |
| 1.0 | 0.65 |
| 1.5 | 0.42 |
| 2.0 | 0.23 |
+-------------------------+-----------------+

Pass@k Correctness Metrics:
[If available, shows pass@k results]
`

Sources: scripts/benchmark_eval_analysis.py143-241 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L143-L241]

### JSON Output Format

When `output_file` is specified, results are saved as JSON:

```

Sources: scripts/benchmark_eval_analysis.py243-263 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L243-L263]

This JSON format enables programmatic analysis and integration with leaderboards or other tooling.

### Custom Path Overrides

For external integrations (e.g., leaderboards), the analysis script supports path overrides:

```

Sources: scripts/benchmark_eval_analysis.py43-46 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L43-L46] scripts/benchmark_eval_analysis.py80-98 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L80-L98]

## Timing Statistics Collection

All timing measurements collect the following statistics:

| | Statistic | Description
| `mean` | Average execution time across trials
| `std` | Standard deviation of execution times
| `min` | Minimum execution time observed
| `max` | Maximum execution time observed
| `median` | Median execution time

Sources: src/kernelbench/timing.py100-120 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L100-L120]

The `mean` value is used as the primary runtime metric for speedup calculations and comparisons.

## Metric Interpretation Guidelines

### When to Use Each Metric

| | Metric | Use Case | Key Consideration
| `correctness_rate` | Baseline model capability | Does the model generate working code?
| `compilation_rate` | Syntax and API correctness | Can the code compile?
| `geometric_mean_speedup` | Overall performance improvement | How much faster on average? (only correct kernels)
| `fast_p[1.0]` | Primary benchmark metric | What fraction achieve ≥1x speedup AND correct?
| `fast_p[1.5]` | High-performance threshold | What fraction achieve ≥1.5x speedup AND correct?
| `pass@k[10]` | Sample efficiency | How many samples needed for success?

Sources: scripts/benchmark_eval_analysis.py143-241 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py#L143-L241] EVAL.md1-57 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L1-L57]

### Suspicious Results

Speedups greater than 2.0x are flagged as potentially suspicious and should be manually verified. The evaluation system includes adversarial tests to detect common reward hacking patterns:

- Reusing cached computations from the reference

- Modifying inputs to cheat correctness checks

- Moving computation to non-default CUDA streams

Sources: EVAL.md6-17 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L6-L17] scripts/eval_from_generations.py535-541 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/eval_from_generations.py#L535-L541]

For details on adversarial testing, see Testing and Debugging [/ScalingIntelligence/KernelBench/8.4-testing-and-debugging].

## Profiling Integration

While the standard evaluation flow focuses on correctness and timing metrics, KernelBench also supports hardware-level profiling using NVIDIA Nsight Compute. Profiling provides detailed metrics like SM cycles, tensor core utilization, and memory bandwidth.

For profiling capabilities, see Profiling and Debugging [/ScalingIntelligence/KernelBench/8.3-profiling-and-debugging].

Sources: src/kernelbench/profile.py1-439 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py#L1-L439]

DismissRefresh this wiki

