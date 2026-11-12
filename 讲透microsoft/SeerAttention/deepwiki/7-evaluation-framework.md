<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/SeerAttention · page 7 Evaluation Framework · fetched 2026-10-26 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eval/README.md](eval/README.md)
- [eval/efficiency/benchmark_sparse_attn.py](eval/efficiency/benchmark_sparse_attn.py)
- [eval/reasoning_tasks/README.md](eval/reasoning_tasks/README.md)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

The Evaluation Framework provides a comprehensive system for benchmarking SeerAttention models across three dimensions: **accuracy** (reasoning and long-context tasks), **efficiency** (computational performance), and **sparsity characteristics** (pattern analysis). The framework supports parallel execution across multiple GPUs, multiple execution backends, and automatic result aggregation.

This page provides an overview of the evaluation infrastructure, execution pipelines, and result management. For detailed information about specific evaluation types, see:
- [Reasoning Tasks Evaluation](#7.1) - AIME, MATH, GPQA, LiveCodeBench benchmarks
- [Long-Context Benchmarks](#7.2) - PG19, LongBench, RULER evaluations
- [Efficiency Benchmarks](#7.3) - Timing and memory profiling
- [Running Evaluations](#7.4) - Practical guide to executing evaluations

For information about the models being evaluated, see [Model Implementations](#4). For training metrics during self-distillation, see [Training and Distillation](#5).

## Evaluation Categories

The framework organizes evaluations into three primary categories, each testing different aspects of SeerAttention's performance.

### Evaluation Category Structure

```mermaid
graph TB
    EvalFramework["Evaluation Framework"]
    
    subgraph Reasoning["Reasoning Tasks"]
        AIME24["AIME24<br/>64 samples/query<br/>pass@1 metric"]
        AIME25["AIME25<br/>64 samples/query<br/>pass@1 metric"]
        MATH500["MATH500<br/>8 samples/query<br/>pass@1 metric"]
        GPQA["GPQA-Diamond<br/>16 samples/query<br/>pass@1 metric"]
        LiveCode["LiveCodeBench<br/>Code generation<br/>execution accuracy"]
    end
    
    subgraph LongContext["Long-Context Tasks"]
        PG19["PG19 Perplexity<br/>TopK sparsity (nz_ratio)<br/>8k-131k sequences<br/>density: 1.0-0.1"]
        LongBench["LongBench Suite<br/>Threshold=2e-3<br/>12 retrieval/QA tasks<br/>context bins: 0-4k, 4-8k, 8k+"]
        RULER["RULER Benchmark<br/>Threshold=5e-4<br/>13 retrieval subtasks<br/>seq: 4k-128k"]
    end
    
    subgraph Efficiency["Efficiency Benchmarks"]
        PrefillTime["Prefill Timing<br/>block_sparse_attention<br/>vs FlashAttention-2"]
        DecodeTime["Decode Timing<br/>flash_decode_leftpad<br/>token generation speed"]
        MemoryUsage["Memory Profiling<br/>KV cache size<br/>GPU memory"]
        SparsityProfile["Sparsity Analysis<br/>activated blocks<br/>quantile statistics"]
    end
    
    EvalFramework --> Reasoning
    EvalFramework --> LongContext
    EvalFramework --> Efficiency
```

**Sources:** [eval/README.md:1-102](), [eval/reasoning_tasks/README.md:1-54]()

### Evaluation Metrics by Category

| Category | Benchmarks | Primary Metrics | Sparsity Control | Sequence Lengths |
|----------|-----------|----------------|------------------|------------------|
| **Reasoning** | AIME24/25, MATH500, GPQA-Diamond | pass@1 accuracy | `token_budget`: 1k-8k | Variable (task-dependent) |
| **Long-Context** | PG19 | Perplexity | `top_k` (nz_ratio): 0.1-1.0 | 8k-131k tokens |
| **Long-Context** | LongBench | Accuracy per task | `threshold`: 2e-3 | 0-4k, 4-8k, 8k+ bins |
| **Long-Context** | RULER | Accuracy per subtask | `threshold`: 5e-4 | 4k, 8k, 16k, 32k, 64k, 128k |
| **Efficiency** | Custom timing | ms per forward pass | Configurable | 8k-131k tokens |

**Sources:** [eval/README.md:5-98](), [eval/reasoning_tasks/README.md:12-54]()

## Evaluation Infrastructure

The framework uses a parallel orchestration system to coordinate evaluation across multiple GPUs and manage computational resources efficiently.

### Execution Pipeline

```mermaid
graph LR
    TaskConfig["Task Configuration<br/>task_name, model_path<br/>samples_per_query<br/>token_budget/threshold"]
    
    Orchestrator["Parallel Orchestrator<br/>parallel_run_vllm.py<br/>parallel_run_hf.py"]
    
    subgraph Backend["Execution Backend Selection"]
        CheckBackend{"Backend<br/>Type?"}
        VLLMBackend["vLLM Engine<br/>High throughput<br/>PagedAttention<br/>Dense baseline"]
        HFBackend["HuggingFace Transformers<br/>Custom attention hooks<br/>Sparsity support<br/>AttnGates integration"]
    end
    
    subgraph GPUAlloc["GPU Allocation"]
        GPUManager["GPU Manager<br/>CUDA_VISIBLE_DEVICES<br/>Dynamic assignment"]
        MultiGPU["Multi-GPU Pool<br/>Parallel task execution"]
    end
    
    subgraph Execution["Model Execution"]
        LoadModel["Load Model<br/>base + AttnGates"]
        ConfigSparsity["Configure Sparsity<br/>method, threshold/budget"]
        RunInference["Run Inference<br/>Generate completions"]
        CollectMetrics["Collect Metrics<br/>accuracy, timing, sparsity"]
    end
    
    subgraph Storage["Result Storage"]
        PerRunFiles["Per-Run Files<br/>completions.jsonl<br/>sparsity_info.json<br/>other_info.json"]
        Aggregation["Aggregation Script<br/>Average across runs<br/>Confidence intervals"]
        SummaryReports["Summary Reports<br/>Tables by model<br/>Tables by budget"]
    end
    
    TaskConfig --> Orchestrator
    Orchestrator --> CheckBackend
    CheckBackend -->|"vLLM"| VLLMBackend
    CheckBackend -->|"HF"| HFBackend
    
    Orchestrator --> GPUManager
    GPUManager --> MultiGPU
    
    VLLMBackend --> LoadModel
    HFBackend --> LoadModel
    MultiGPU --> LoadModel
    
    LoadModel --> ConfigSparsity
    ConfigSparsity --> RunInference
    RunInference --> CollectMetrics
    
    CollectMetrics --> PerRunFiles
    PerRunFiles --> Aggregation
    Aggregation --> SummaryReports
```

**Sources:** [eval/README.md:1-102](), [eval/reasoning_tasks/README.md:1-10]()

### Backend Comparison

| Feature | vLLM Backend | HuggingFace Backend |
|---------|-------------|---------------------|
| **Primary Use** | Dense baseline comparisons | Sparse attention evaluation |
| **Attention Support** | Standard FlashAttention-2 | Custom sparse attention kernels |
| **AttnGates** | Not supported | Full support |
| **Throughput** | High (PagedAttention) | Moderate (custom kernels) |
| **Sparsity Profiling** | No | Yes (`sparsity_info.json`) |
| **Scripts** | `parallel_run_vllm.py` | `parallel_run_hf.py` |

**Sources:** [eval/reasoning_tasks/README.md:1-10]()

## Result Storage and Aggregation

### Per-Run Output Files

Each evaluation run produces three standardized JSON files:

```mermaid
graph TD
    EvalRun["Evaluation Run<br/>Single model + config"]
    
    subgraph OutputFiles["Output Files"]
        Completions["completions.jsonl<br/>Line-delimited JSON<br/>query, completion, metrics"]
        SparsityInfo["sparsity_info.json<br/>Activated block counts<br/>Sparsity percentages<br/>Quantile statistics"]
        OtherInfo["other_info.json<br/>Timing information<br/>Memory usage<br/>GPU utilization"]
    end
    
    subgraph FileContents["File Contents"]
        CompletionFields["Completions Fields:<br/>• task_id<br/>• query<br/>• generated_text<br/>• is_correct<br/>• generation_time"]
        
        SparsityFields["Sparsity Fields:<br/>• per_layer_sparsity<br/>• overall_sparsity<br/>• activated_blocks<br/>• quantile_analysis"]
        
        OtherFields["Other Fields:<br/>• total_time_ms<br/>• tokens_per_second<br/>• peak_memory_gb<br/>• gpu_utilization"]
    end
    
    EvalRun --> Completions
    EvalRun --> SparsityInfo
    EvalRun --> OtherInfo
    
    Completions -.-> CompletionFields
    SparsityInfo -.-> SparsityFields
    OtherInfo -.-> OtherFields
```

**Sources:** [eval/README.md:1-102]()

### Aggregation Process

Results from multiple runs are aggregated to compute final metrics:

| Metric Type | Aggregation Method | Output Format |
|------------|-------------------|---------------|
| **Reasoning Accuracy** | pass@1 = (correct samples) / (total samples) | Percentage per task |
| **Perplexity** | Average across sequences | PPL per sequence length |
| **Timing** | Mean ± std across runs | ms ± std |
| **Sparsity** | Median across layers/runs | Percentage ± quantiles |

**Sources:** [eval/README.md:1-102]()

## Efficiency Benchmarking Infrastructure

The framework includes dedicated infrastructure for measuring computational efficiency of sparse attention kernels.

### Benchmark Script Architecture

```mermaid
graph TB
    BenchmarkScript["benchmark_sparse_attn.py<br/>Main benchmark script"]
    
    subgraph Config["Configuration Parameters"]
        ArgParser["parse_args()<br/>--seq_len<br/>--sparsity (list)<br/>--batch_size<br/>--num_heads<br/>--head_dim<br/>--block_size"]
    end
    
    subgraph TensorInit["Tensor Initialization"]
        GetTensors["get_tensors()<br/>Initialize Q, K, V<br/>dtype=float16<br/>device=cuda"]
    end
    
    subgraph MaskGen["Mask Generation"]
        GenMask["generate_base_sparsity_mask()<br/>nrow, ncol from seq_len<br/>Apply sparsity density<br/>Random block selection<br/>Causal masking support"]
    end
    
    subgraph Benchmark["Benchmark Execution"]
        RunBenchmark["run_benchmark()<br/>Warmup phase (10 iters)<br/>Timing phase (epoch iters)<br/>CUDA synchronization"]
        
        SparseKernel["block_sparse_attention()<br/>Custom sparse kernel<br/>Block-level masking"]
        
        DenseKernel["flash_attn_func_offical()<br/>FlashAttention-2<br/>Dense baseline"]
    end
    
    subgraph Results["Result Computation"]
        CalcTime["Calculate time per iter<br/>total_time * 1000 / epoch"]
        CalcSpeedup["Calculate speedup<br/>dense_time / sparse_time"]
        PrintTable["tabulate()<br/>Method, Time (ms), Speedup"]
    end
    
    BenchmarkScript --> ArgParser
    ArgParser --> GetTensors
    GetTensors --> GenMask
    
    GenMask --> RunBenchmark
    RunBenchmark --> SparseKernel
    RunBenchmark --> DenseKernel
    
    SparseKernel --> CalcTime
    DenseKernel --> CalcTime
    CalcTime --> CalcSpeedup
    CalcSpeedup --> PrintTable
```

**Sources:** [eval/efficiency/benchmark_sparse_attn.py:1-125]()

### Key Functions in Efficiency Benchmarking

The `benchmark_sparse_attn.py` script provides the following core functions:

- **`get_tensors()`** [eval/efficiency/benchmark_sparse_attn.py:10-14]() - Initializes Q, K, V tensors with specified dimensions and dtype
- **`run_benchmark()`** [eval/efficiency/benchmark_sparse_attn.py:17-27]() - Executes warmup phase, measures timing with CUDA synchronization
- **`generate_base_sparsity_mask()`** [eval/efficiency/benchmark_sparse_attn.py:30-58]() - Creates block-sparse masks with configurable density and causal masking
- **`benchmark()`** [eval/efficiency/benchmark_sparse_attn.py:61-89]() - Main benchmark coordinator comparing sparse vs dense attention

### Example Benchmark Results

The script produces tabulated output comparing sparse attention at different sparsity levels against FlashAttention-2:

```
Method (Sparsity)              Time (ms)    Speedup
block_sparse_attn (0.50)       X.XX ms      Y.YYx
block_sparse_attn (0.70)       X.XX ms      Y.YYx
FlashAttention-2 (full)        X.XX ms      -
```

**Sources:** [eval/efficiency/benchmark_sparse_attn.py:112-122]()

## Configuration and Dependencies

### Required Dependencies

The evaluation framework requires the following key dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `transformers` | 4.51.0 | Model loading and inference |
| `accelerate` | Latest | Multi-GPU management |
| `deepspeed` | 0.16.3 | Distributed training/evaluation |
| `triton` | 3.0.0 | Custom kernel compilation |
| `tabulate` | Latest | Result table formatting |
| `sympy` | Latest | Math task evaluation |
| `psutil` | Latest | System resource monitoring |

**Sources:** [requirements.txt:1-21]()

### Evaluation Task Configuration

Each evaluation task requires configuration parameters:

```mermaid
graph LR
    TaskDef["Task Definition"]
    
    subgraph Required["Required Parameters"]
        TaskName["task_name<br/>e.g., 'aime24', 'pg19'"]
        ModelPath["model_path<br/>HF Hub path or local"]
        SampleCount["samples_per_query<br/>1-64 depending on task"]
    end
    
    subgraph Sparsity["Sparsity Configuration"]
        Method["sparsity_method<br/>'threshold', 'token_budget', 'top_k'"]
        ThresholdVal["threshold<br/>2e-3 to 5e-4"]
        BudgetVal["token_budget<br/>1k to 8k"]
        TopKVal["top_k (nz_ratio)<br/>0.1 to 1.0"]
    end
    
    subgraph Compute["Compute Resources"]
        BatchSize["batch_size<br/>Conservative for 80GB"]
        NumGPUs["num_gpus<br/>Parallel execution"]
        Backend["backend<br/>'vllm' or 'hf'"]
    end
    
    TaskDef --> Required
    TaskDef --> Sparsity
    TaskDef --> Compute
    
    Method -.->|"if threshold"| ThresholdVal
    Method -.->|"if token_budget"| BudgetVal
    Method -.->|"if top_k"| TopKVal
```

**Sources:** [eval/reasoning_tasks/README.md:1-10](), [eval/README.md:52-98]()

## Summary

The Evaluation Framework provides comprehensive benchmarking infrastructure across three key dimensions:

1. **Reasoning Tasks** - Measures accuracy on mathematical and general reasoning with pass@1 metrics using token budget sparsity
2. **Long-Context Tasks** - Evaluates perplexity and retrieval accuracy across varying context lengths using threshold or top-k sparsity  
3. **Efficiency Benchmarks** - Profiles computational performance, comparing sparse kernel execution time against dense baselines

The parallel orchestration system (`parallel_run_vllm.py`, `parallel_run_hf.py`) coordinates evaluation across multiple GPUs, with automatic result aggregation and summary report generation. Results are stored in standardized JSON formats (`completions.jsonl`, `sparsity_info.json`, `other_info.json`) for reproducibility and analysis.

For detailed information about running specific evaluations, see the sub-pages listed at the beginning of this document.

**Sources:** [eval/README.md:1-102](), [eval/reasoning_tasks/README.md:1-54](), [eval/efficiency/benchmark_sparse_attn.py:1-125]()

---

