> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/8-advanced-topics | 抓取: 2026-09-03 | DeepWiki SSR 快照

# Advanced Topics

Relevant source files

- EVAL.md [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1]

- pyproject.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/pyproject.toml]

- requirements.txt [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/requirements.txt]

- scripts/get_baseline_time_single_problem.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/get_baseline_time_single_problem.py]

- scripts/inspect_triton.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/inspect_triton.py]

- src/kernelbench/profile.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py]

- src/kernelbench/prompt_constructor_toml.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/prompt_constructor_toml.py]

- src/kernelbench/timing.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py]

- src/kernelbench/unit_tests/test_eval_timing.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py]

- src/kernelbench/utils.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/utils.py]

This page covers advanced features for power users and developers extending KernelBench. Topics include integrating custom CUDA kernels with inline compilation, static validation to detect malformed or adversarial code, profiling tools for performance analysis, and testing infrastructure for debugging generated kernels.

For basic usage of KernelBench's evaluation system, see Kernel Evaluation System [/ScalingIntelligence/KernelBench/2.1-kernel-evaluation-system]. For standard timing and metrics, see Timing and Profiling [/ScalingIntelligence/KernelBench/2.5-timing-and-profiling] and Evaluation Metrics [/ScalingIntelligence/KernelBench/7.1-evaluation-metrics].

## Custom CUDA Kernel Integration

KernelBench supports backends that require inline compilation of CUDA C++ code, particularly ThunderKittens which uses template-heavy C++ with custom primitives. The system uses `torch.utils.cpp_extension.load_inline` to dynamically compile and load kernels at runtime.

### Inline Compilation Workflow

```

Sources: src/kernelbench/eval.py262-350 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L262-L350] EVAL.md1-57 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L1-L57]

### ThunderKittens Example Pattern

ThunderKittens kernels use a specific pattern with template instantiation and custom primitives from the `kittens::` namespace:

| | Component | Purpose | Example
| CUDA Headers | Include kernel utilities | `#include <cuda.h>`, `#include <kittens.cuh>`
| Template Function | Define parameterized kernel | `template<int BLOCK_M, int BLOCK_N>`
| Kernel Launch Wrapper | Python-callable interface | `void launch_kernel(torch::Tensor...)`
| Build Parameters | Compilation flags | `extra_cuda_cflags=["-std=c++17"]`

The `load_inline` call in kernelbench/eval.pyNaN-NaN [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/kernelbench/eval.py#LNaN-LNaN] handles:

- Extracting kernel source from `ModelNew` class

- Setting CUDA architecture flags via `TORCH_CUDA_ARCH_LIST`

- Managing build directories and caching

- Error handling for compilation failures

Key Implementation Details:

```

Sources: src/kernelbench/eval.py262-350 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L262-L350] requirements.txt14-26 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/requirements.txt#L14-L26]

### Build Caching Strategy

The compilation cache at `~/.torch/extensions` stores compiled binaries indexed by source code hash. This provides:

- Compilation avoidance when the same kernel is evaluated multiple times

- Architecture-specific binaries via `TORCH_CUDA_ARCH_LIST` environment variable

- Persistent storage across Python sessions

Users can manually clear the cache when testing compiler flag changes or debugging build issues. Set `build_dir=None` in evaluation functions to use the default cache location.

Sources: src/kernelbench/eval.py262-350 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L262-L350] src/kernelbench/utils.py41-50 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/utils.py#L41-L50]

## Static Validation

Static validation detects common errors and adversarial patterns in generated kernel code before execution. The system uses `kernel_static_checker.py` with regex-based rules to flag suspicious constructs.

### Validation Architecture

```

Sources: EVAL.md42-43 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L42-L43]

### Common Anti-Patterns Detected

The static checker identifies several categories of problematic code:

| | Pattern | Detection | Risk | Example Regex
| Cached computation reuse | Global variable access | High - correctness | `torch\\..*\\.cache`
| Stream manipulation | Non-default CUDA streams | High - timing | `torch\\.cuda\\.Stream`
| Input modification | In-place tensor ops | High - correctness | `\\*=`, `\\.fill_\\(`
| Hardcoded values | Magic numbers | Medium - generality | Shape values in kernel config
| Missing synchronization | Async operations | Medium - timing | `async=True` without `synchronize()`

The checker returns a structured result with:

- `is_valid: bool` - whether the code passes all rules

- `violations: List[Dict]` - each violation with rule name, line number, and description

- `severity: str` - "error", "warning", or "info"

Sources: EVAL.md42-44 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L42-L44] src/kernelbench/unit_tests/test_eval_adversarial.py1-50 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_adversarial.py#L1-L50]

### Adversarial Test Cases

The unit test suite at src/unit_tests/test_kernels/ [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/unit_tests/test_kernels/] contains example kernels exhibiting known reward hacking behaviors:

```

Each test case verifies that either:

- The static checker rejects the code, OR

- The evaluation system detects correctness failures, OR

- Suspicious speedups (>2x) trigger manual review

Sources: EVAL.md45-51 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L45-L51] src/kernelbench/unit_tests/test_eval_adversarial.py1-50 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_adversarial.py#L1-L50]

### Integration with Evaluation Pipeline

Static validation is an optional pre-evaluation filter. When enabled:

- Generated code passes through `kernel_static_checker.check_kernel(code, backend)`

- If validation fails, the kernel is marked as "failed_static_check"

- Violations are logged to evaluation results JSON

- The kernel does not proceed to compilation or timing

This saves GPU time by rejecting obviously problematic code before expensive compilation and execution steps.

Sources: EVAL.md42-44 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L42-L44]

## Profiling and Debugging

KernelBench provides multiple profiling tools for performance analysis and debugging, supporting both high-level PyTorch profiling and low-level hardware counter analysis.

### Profiling Tool Landscape

```

Sources: src/kernelbench/timing.py1-512 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L1-L512] src/kernelbench/profile.py1-439 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py#L1-L439] scripts/inspect_triton.py1-175 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/inspect_triton.py#L1-L175]

### Timing Method Comparison

KernelBench implements four distinct timing approaches, each with specific tradeoffs:

| | Method | Implementation | Precision | Use Case | Limitations
| cuda_event | `torch.cuda.Event()` | Device-side, ms | Cold cache measurement | Assumes current stream
| do_bench | Triton `testing.do_bench()` | Adaptive trials | Automated benchmarking | No explicit trial control
| do_bench_impl | Custom Triton-style | User-controlled | Transparent timing | More complex setup
| host_time | `time.perf_counter()` | CPU wall-clock | E2E latency | Includes overhead
| nsight_python_time | Nsight hardware counter | GPU HW counter, ns | Ground truth timing | Requires sudo/admin

Implementation Example - cuda_event:

The `cuda_event` method at src/kernelbench/timing.py91-171 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L91-L171] implements cold cache timing:

- Warmup phase: Run kernel `num_warmup` times to populate instruction cache

- Cache clearing: Thrash L2 cache with 256MB dummy tensor before each trial

- Event recording: Record start/end events on current CUDA stream

- Synchronization: Block until all GPU work completes

- Time extraction: Compute elapsed time via `start_event.elapsed_time(end_event)`

Sources: src/kernelbench/timing.py15-172 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L15-L172]

### L2 Cache Management

Cold cache timing requires explicit L2 cache clearing between trials to ensure consistent measurements:

```

Cache sizes vary by architecture:

- A100: 40MB L2

- H100: 50MB L2

- H200: 90MB L2

- RTX 4090: 72MB L2

- L40S: 48MB L2

The 256MB thrash tensor exceeds all cache sizes, ensuring complete eviction. Triton's `do_bench` uses a similar approach via `triton.runtime.driver.active.clear_cache()`.

Sources: src/kernelbench/timing.py16-43 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/timing.py#L16-L43]

### Nsight Compute Integration

The `profile.py` module provides hardware-level profiling via NVIDIA Nsight Compute (ncu):

```

Key Features:

- Hardware counters: Access to 100+ metrics beyond simple timing

- Multi-kernel aggregation: Combines metrics when PyTorch ops launch multiple CUDA kernels

- Requires ncu CLI: Must have Nsight Compute installed and in PATH

- Elevated privileges: Hardware counter access typically requires sudo

Common Metrics:

- `gpu__time_duration.sum`: Total GPU execution time (nanoseconds)

- `sm__cycles_elapsed.sum`: Total SM cycles across all SMs

- `sm__cycles_active.avg`: Average active cycles per SM (occupancy indicator)

- `smsp__inst_executed_pipe_tensor_op_hmma.sum`: Tensor core operations

Sources: src/kernelbench/profile.py66-152 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py#L66-L152] EVAL.md39-40 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L39-L40]

### inspect_triton.py - Torch Compile Analysis

The `inspect_triton.py` script analyzes kernels generated by `torch.compile`:

Capabilities:

- Triton code extraction: Captures generated Triton code from torch.compile(backend="inductor")

- Profiler integration: Uses `torch.profiler` to generate flamegraphs and timing breakdowns

- Side-by-side comparison: Profiles both eager and compiled versions of the same model

Usage Pattern:

```

The generated trace files can be viewed in Chrome's `chrome://tracing` viewer for detailed timeline analysis.

Sources: scripts/inspect_triton.py32-175 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/inspect_triton.py#L32-L175] EVAL.md39-40 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L39-L40]

### Profiling KernelBench Models

The high-level function `profile_kernelbench_model_with_nsight()` handles the full workflow for profiling generated kernels:

- Load input functions: Extract `get_inputs()` and `get_init_inputs()` from model source

- Compile model: Use backend-specific loading (`load_custom_model_with_tempfile` for Triton/TileLang/CuTe)

- Instantiate model: Create model instance with init_inputs

- Profile forward pass: Wrap forward() in closure and pass to `profile_with_nsight()`

- Cleanup: Remove temporary files and release GPU memory

Sources: src/kernelbench/profile.py154-308 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py#L154-L308]

## Testing and Debugging

KernelBench includes comprehensive test infrastructure for validating timing methods, catching adversarial patterns, and debugging generated kernels.

### Test Organization

```

Sources: src/kernelbench/unit_tests/test_eval_timing.py1-160 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py#L1-L160] EVAL.md45-51 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L45-L51]

### Timing Test Scaffold

The timing test suite uses a common scaffold pattern at src/kernelbench/unit_tests/test_eval_timing.py27-77 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py#L27-L77]:

Test Configuration:

```
`M = 2048, N = 2048, K = 2048
num_warmup = 5
num_trials = 100
device = "cuda:5" # configurable
`

Validation Checks:

- Result type: Must be `list[float]`

- All positive: No negative or zero timings

- Reasonable range: No outliers >10x mean

- Consistency: Standard deviation within expected bounds

Test Execution:

```

Sources: src/kernelbench/unit_tests/test_eval_timing.py27-84 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py#L27-L84]

### Running All Timing Tests

The `run_all_timing_tests()` function executes all available timing methods:

```

When `nsight-python` is installed and `ncu` is in PATH, the extended test suite includes:

```

Each test outputs statistics for comparison:

```
`Timing stats
{
"mean": 1.23,
"std": 0.045,
"min": 1.18,
"max": 1.35,
"num_trials": 100,
"hardware": "NVIDIA L40S",
"device": "cuda:5"
}
`

Sources: src/kernelbench/unit_tests/test_eval_timing.py80-136 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py#L80-L136]

### Adversarial Test Methodology

The adversarial test suite at `test_eval_adversarial.py` validates that evaluation correctly handles exploit attempts:

Test Categories:

| | Exploit Type | Detection Method | Expected Behavior
| Cache reuse | Static checker or runtime | Correctness failure or flagged suspicious
| Input modification | Correctness check | torch.allclose fails
| Stream manipulation | Speedup anomaly | >2x speedup triggers investigation
| NaN pattern copying | Correctness check | Fails on non-NaN inputs

Test Pattern:

```

Sources: EVAL.md45-52 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/EVAL.md?plain=1#L45-L52]

### Debugging Generated Kernels

When debugging evaluation failures:

- Enable verbose logging: Set `verbose=True` in evaluation functions

- Check compilation errors: Inspect build logs in `~/.torch/extensions/`

- Test with reference inputs: Use fixed seeds and small tensor sizes

- Compare timing methods: Cross-validate with multiple timing approaches

- Profile with NCU: Use `profile_kernelbench_model_with_nsight()` for hardware metrics

- Inspect intermediate results: Save outputs from warmup phase for comparison

Key Debug Flags:

- `TORCH_USE_CUDA_DSA=1`: Enable CUDA device-side assertions

- `TORCH_LOGS="+dynamo,+inductor"`: Verbose torch.compile logging

- `CUDA_LAUNCH_BLOCKING=1`: Synchronous kernel launches for easier debugging

Sources: src/kernelbench/eval.py262-350 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/eval.py#L262-L350] src/kernelbench/profile.py248-262 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/profile.py#L248-L262]

### Best Practices for Test Development

When adding new tests:

- Use pytest fixtures for GPU device selection and cleanup

- Skip tests gracefully when hardware unavailable (`pytest.skip()`)

- Test multiple backends when applicable (CUDA, Triton, etc.)

- Validate both success and failure cases

- Compare against known-good baselines

- Document expected behavior in test docstrings

Sources: src/kernelbench/unit_tests/test_eval_timing.py1-160 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/unit_tests/test_eval_timing.py#L1-L160]

DismissRefresh this wiki

