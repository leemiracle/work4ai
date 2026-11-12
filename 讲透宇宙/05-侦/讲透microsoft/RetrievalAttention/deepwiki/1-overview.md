<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [Transparency_FAQ.md](Transparency_FAQ.md)

</details>



This document provides an overview of RetroInfer, a novel system for accelerating long-context Large Language Model (LLM) inference through vector storage optimization and GPU-CPU co-execution. This page covers the system's core concepts, architecture, and performance characteristics.

For detailed setup instructions, see [Setup and Installation](#4). For specific usage examples and testing procedures, see [Usage Examples](#5). For technical implementation details of the attention mechanisms, see [Attention Mechanisms](#2).

## What is RetroInfer?

RetroInfer is a research system that **rethinks the KV cache as vector storage** to accelerate long-context LLM inference. The system exploits the inherent sparsity of attention mechanisms and introduces two key innovations:

- **Wave Index**: An attention-aware vector index that enables efficient retrieval of critical tokens from the KV cache
- **Wave Buffer**: A coordination system that manages KV cache placement and overlaps computation with data transfer across GPU and CPU

The system achieves 4.5x–10.5x improvements in decoding throughput over FlashAttention without accuracy loss, making it particularly effective for long-context scenarios (~120K tokens).

## Core System Architecture

### RetroInfer Components and Data Flow

```mermaid
flowchart TD
    Input["Long Context Input<br/>~120K tokens"]
    
    subgraph "Attention Hub"
        AttentionHub["attention_hub"]
        FlashAttn["flash_attn_with_kvcache"]
        RetroInferAttn["retroinfer_cache"]
    end
    
    subgraph "RetroInfer Core"
        WaveIndex["wave_index<br/>Attention-aware Vector Index"]
        WaveBuffer["wave_buffer<br/>GPU-CPU Coordination"]
        KVCache["KV Cache<br/>Vector Storage"]
    end
    
    subgraph "Hardware Layer"
        GPU["GPU Compute<br/>~25GB Memory"]
        CPU["CPU Storage<br/>~67GB Memory"]
    end
    
    subgraph "Model Integration"
        LlamaModel["LlamaModel"]
        QwenModel["QwenModel"]
    end
    
    Input --> AttentionHub
    AttentionHub --> FlashAttn
    AttentionHub --> RetroInferAttn
    RetroInferAttn --> WaveIndex
    WaveIndex --> KVCache
    WaveBuffer --> KVCache
    WaveBuffer --> GPU
    WaveBuffer --> CPU
    LlamaModel --> WaveIndex
    QwenModel --> WaveIndex
    
    Output["Generated Tokens<br/>4.5x-10.5x Throughput"]
    KVCache --> Output
```

Sources: [README.md:1-129](), [Transparency_FAQ.md:1-22]()

### Key Configuration Parameters

RetroInfer operates with two primary configuration parameters that control its behavior:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `retrieval_budget_ratio` | 0.018 | Ratio of tokens retrieved from KV cache to total input tokens |
| `attention_estimate_ratio` | 0.232 | Ratio of clusters estimated in attention mechanism to total clusters |

Sources: [README.md:79-80](), [README.md:91-92]()

## Supported Models and Configurations

### Model Support Matrix

```mermaid
flowchart LR
    subgraph "Model Types"
        Llama31["llama-3.1-8b"]
        Llama3["llama-3-8b-1048k"]
        Qwen7["qwen2.5-7b"]
        Qwen72["qwen2.5-72b"]
    end
    
    subgraph "Configuration Files"
        Model2Path["model2path.json"]
        Model2MaxLen["model2maxlen.json"]
        Dataset2Prompt["dataset2prompt.json"]
    end
    
    subgraph "Attention Types"
        RetroInfer["RetroInfer"]
        FlashAttn["Full_Flash_Attn"]
    end
    
    subgraph "Data Types"
        BF16["bf16"]
        FP16["fp16"]
    end
    
    Llama31 --> Model2Path
    Llama3 --> Model2Path
    Qwen7 --> Model2Path
    Qwen72 --> Model2Path
    
    Model2Path --> RetroInfer
    Model2Path --> FlashAttn
    Model2MaxLen --> RetroInfer
    Dataset2Prompt --> RetroInfer
    
    RetroInfer --> BF16
    RetroInfer --> FP16
    FlashAttn --> BF16
    FlashAttn --> FP16
```

Sources: [README.md:73-74](), [README.md:78-79](), [README.md:89-90](), [README.md:93]()

## Performance Characteristics

### Throughput Improvements

RetroInfer delivers significant performance improvements across different scenarios:

- **Decoding Throughput**: 4.5x–10.5x improvement over FlashAttention
- **Memory Usage**: ~25GB GPU memory, ~67GB CPU memory for batch size 4
- **Context Length**: Optimized for ~120K token contexts
- **Accuracy**: Almost no change compared to full attention

### Hardware Requirements

The system is designed for GPU-CPU co-execution with specific hardware characteristics:

- **GPU**: Requires CUDA 12.4 compatibility
- **CPU**: Utilizes CPU memory for extended KV cache storage
- **Multi-GPU**: Automatic model splitting across visible GPUs
- **NUMA**: Optimized for multi-NUMA node configurations

Sources: [README.md:3-4](), [README.md:42](), [README.md:96](), [Transparency_FAQ.md:4]()

## Evaluation and Benchmarking

### Supported Benchmarks

RetroInfer has been evaluated on multiple benchmark systems:

| Benchmark | Tasks | Purpose |
|-----------|-------|---------|
| RULER | `niah_single_1/2/3`, `niah_multikey_1/2/3`, `vt`, `qa_1/2` | Synthetic evaluation tasks |
| LongBench | Various real-world tasks | Real-world scenario evaluation |
| Throughput | Custom scripts | Performance measurement |

### Evaluation Tasks

```mermaid
flowchart TD
    subgraph "RULER Tasks"
        NIAH["Needle in Haystack<br/>niah_single_1/2/3<br/>niah_multikey_1/2/3"]
        VT["Variable Tracking<br/>vt"]
        QA["Question Answering<br/>qa_1, qa_2"]
    end
    
    subgraph "LongBench Tasks"
        MultiDoc["Multi-document QA"]
        SingleDoc["Single-document QA"]
        CodeComp["Code Completion"]
        FewShot["Few-shot Learning"]
    end
    
    subgraph "Evaluation Scripts"
        RulerRun["ruler_run.sh"]
        LongBenchRun["longbench_run.sh"]
        ThroughputRun["run.sh"]
    end
    
    NIAH --> RulerRun
    VT --> RulerRun
    QA --> RulerRun
    MultiDoc --> LongBenchRun
    SingleDoc --> LongBenchRun
    CodeComp --> LongBenchRun
    FewShot --> LongBenchRun
    
    RulerRun --> Results["Accuracy Results<br/>Almost no change"]
    LongBenchRun --> Results
    ThroughputRun --> PerfResults["Performance Results<br/>4.5x-10.5x improvement"]
```

Sources: [README.md:61-81](), [README.md:82-94](), [README.md:95-104](), [Transparency_FAQ.md:12-14]()

## Integration Points

### Development Environment

RetroInfer integrates with the following components:

- **CUDA Environment**: Requires CUDA 12.4.1 with cuDNN support
- **Python Environment**: Python 3.10.16 with conda management
- **Dependencies**: flash-attn, flashinfer-python, custom RetroInfer kernels
- **Build System**: CUTLASS integration for kernel compilation

### Testing and Validation

The system provides multiple entry points for testing:

- **Simple Test**: `simple_test.py` for basic functionality verification
- **Benchmark Evaluation**: Integrated with RULER and LongBench frameworks
- **Throughput Testing**: NUMA-aware performance measurement scripts

Sources: [README.md:7-35](), [README.md:37-55]()

---

