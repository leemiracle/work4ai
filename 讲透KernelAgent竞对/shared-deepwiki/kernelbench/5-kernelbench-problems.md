> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/5-kernelbench-problems | 抓取: 2026-09-03 | DeepWiki SSR 快照

# KernelBench Problems

Relevant source files

- KernelBench/level1/97_ScaledDotProductAttention.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/KernelBench/level1/97_ScaledDotProductAttention.py]

- results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json]

- results/timing/H100_PCIe_LambdaLabs/baseline_time_torch_compile_inductor_default.json [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch_compile_inductor_default.json]

- scripts/benchmark_eval_analysis.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/benchmark_eval_analysis.py]

- scripts/generate_baseline_time.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py]

- scripts/inspect_baseline.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/inspect_baseline.py]

- src/kernelbench/dataset.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py]

This page documents the 200 benchmark problems that comprise the KernelBench dataset. For information about how to load and access these problems programmatically, see Dataset Management [/ScalingIntelligence/KernelBench/2.3-dataset-management]. For details about how problems are evaluated, see Kernel Evaluation System [/ScalingIntelligence/KernelBench/2.1-kernel-evaluation-system].

## Overview

KernelBench consists of 200 GPU kernel optimization problems organized into three hierarchical levels by complexity:

- Level 1: 100 atomic kernel operations (matrix operations, activations, normalizations, convolutions, etc.)

- Level 2: ~100 composite operations (fused multi-operator patterns)

- Level 3: 50 complete neural network architectures (MLPs, CNNs, RNNs, Transformers)

Each problem is a self-contained PyTorch program that defines a reference implementation to be optimized. Problems are stored as Python files in `KernelBench/level{1,2,3}/` directories and can also be accessed via HuggingFace datasets.

## Problem Structure

Every KernelBench problem follows a standardized structure defined by the `Problem` dataclass:

```

Sources: src/kernelbench/dataset.py29-64 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L29-L64] KernelBench/level1/97_ScaledDotProductAttention.py1-25 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/KernelBench/level1/97_ScaledDotProductAttention.py#L1-L25]

### Problem File Format

Each problem file contains:

| | Component | Description | Example
| `Model` class | `torch.nn.Module` implementing the operation | `class Model(nn.Module): ...`
| `get_inputs()` | Function returning random input tensors | `def get_inputs(): return [Q, K, V]`
| `get_init_inputs()` | Function returning model initialization args | `def get_init_inputs(): return []`
| Constants | Problem size parameters | `batch_size = 32`, `num_heads = 32`

Sources: KernelBench/level1/97_ScaledDotProductAttention.py1-25 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/KernelBench/level1/97_ScaledDotProductAttention.py#L1-L25]

### Naming Convention

Problems follow a strict naming convention: `{problem_id}_{descriptive_name}.py`

Examples:

- `1_Square_matrix_multiplication_.py` (Level 1, problem 1)

- `97_ScaledDotProductAttention.py` (Level 1, problem 97)

- `1_Conv2D_ReLU_BiasAdd.py` (Level 2, problem 1)

The `problem_id` is 1-indexed within each level and serves as the primary identifier for accessing problems programmatically.

Sources: src/kernelbench/dataset.py232-261 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L232-L261]

## Dataset Access

Problems are accessed through the dataset abstraction layer, which supports both local filesystem and HuggingFace backends:

```

Sources: src/kernelbench/dataset.py83-458 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L83-L458]

### Basic Usage

```

Sources: src/kernelbench/dataset.py403-458 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L403-L458]

## Level Distribution

The following table shows the distribution of problems across levels and categories:

| | Level | Count | Complexity | Categories
| Level 1 | 100 | Atomic kernels | Matrix ops (18), Activations (14), Norms (8), Pooling (6), Reductions (7), Convolutions (34), Losses (7), Misc (6)
| Level 2 | ~100 | Fused operations | Conv+Activation, Matmul+Norm, Multi-op chains (2-6 ops)
| Level 3 | 50 | Complete models | MLPs (3), CNNs (26), Transformers (7), RNNs (10), Specialized (4)

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1]

## Problem Categories

### Level 1 Categories

```

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1]

### Level 2 Categories

Level 2 problems combine 2-6 Level 1 operations into fusion patterns commonly found in neural networks:

| | Fusion Pattern | Example Problem | Operations
| Conv + Activation | `1_Conv2D_ReLU_BiasAdd.py` | Conv2d → ReLU → BiasAdd
| Matmul + Norm | `33_Gemm_Scale_BatchNorm.py` | Gemm → Scale → BatchNorm
| Attention Component | `66_Matmul_Dropout_Softmax.py` | Matmul → Dropout → Softmax
| Complex Chain | `7_Conv3d_ReLU_LeakyReLU_GELU_Sigmoid_BiasAdd.py` | Conv3d → ReLU → LeakyReLU → GELU → Sigmoid → BiasAdd

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1]

### Level 3 Categories

Level 3 problems are complete neural network architectures:

```

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1]

## Representative Subsets

For quick iteration and testing, KernelBench provides curated representative subsets:

```

Sources: src/kernelbench/dataset.py153-172 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L153-L172] src/kernelbench/dataset.py508-557 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L508-L557]

Access representative subsets:

```

Sources: src/kernelbench/dataset.py559-581 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L559-L581]

## Problem Complexity Metrics

The following table shows baseline performance characteristics on NVIDIA H100 PCIe:

| | Level | Median Runtime (Eager) | Runtime Range | Complexity
| Level 1 | 6.95 ms | 1.54 - 24.1 ms | Single operation
| Level 2 | 5.01 ms | 0.91 - 20.6 ms | 2-6 fused operations
| Level 3 | 7.13 ms | 1.27 - 56.9 ms | Full forward pass

Note: Runtimes shown are for PyTorch eager execution baseline on H100 PCIe. Actual performance varies significantly by problem, with convolutions and LSTM operations taking longest.

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1]

## Problem Identification

Each problem has a unique identifier across the dataset:

```

Sources: src/kernelbench/dataset.py29-64 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L29-L64] src/kernelbench/dataset.py70-76 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L70-L76]

The `hash` property computes an MD5 hash of the code with comments and whitespace removed, enabling:

- Deduplication across dataset versions

- Tracking problem identity when formatting changes

- Comparing local vs HuggingFace versions

Sources: src/kernelbench/dataset.py53-63 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L53-L63]

## Baseline Performance Data

KernelBench provides pre-computed baseline timings for reference PyTorch implementations across different hardware and compilation modes. These baselines are used for speedup calculations during evaluation.

Baseline timing files are organized by hardware and mode:

```
`results/timing/{hardware}/
├── baseline_time_torch.json # PyTorch Eager
├── baseline_time_torch_compile_inductor_default.json # torch.compile default
├── baseline_time_torch_compile_inductor_max-autotune.json
└── baseline_time_torch_compile_cudagraphs.json
`

Each baseline file contains timing statistics for all problems in all levels:

```

Sources: results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json1 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/results/timing/H100_PCIe_LambdaLabs/baseline_time_torch.json#L1-L1] scripts/generate_baseline_time.py1-268 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L1-L268]

To generate baselines for new hardware:

```

Sources: scripts/generate_baseline_time.py113-148 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L113-L148] scripts/generate_baseline_time.py173-205 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/generate_baseline_time.py#L173-L205]

## Dataset Access Patterns

The dataset API provides flexible access patterns for different use cases:

| | Pattern | Method | Example Use Case
| Full dataset | `construct_kernelbench_dataset(level)` | Complete benchmarking
| Specific problems | `subset(problem_ids=[1,3,5])` | Targeted testing
| ID range | `subset(id_range=(1, 10))` | Sequential subset
| Random sample | `sample(n=10, seed=42)` | Statistical sampling
| Representative | `get_representative_subset()` | Quick iteration

Sources: src/kernelbench/dataset.py117-172 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L117-L172]

### Filtering Examples

```

Sources: src/kernelbench/dataset.py117-151 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L117-L151]

## Problem Hash and Versioning

The `Problem.hash` property enables tracking problem identity across versions:

```

Sources: src/kernelbench/dataset.py53-76 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/dataset.py#L53-L76]

This enables verification that local and HuggingFace versions of a problem are functionally identical, even if formatting differs.

DismissRefresh this wiki

