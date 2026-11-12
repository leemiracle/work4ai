<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold3 · page 8 Performance Optimization · fetched 2026-10-26 -->

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/known_issues.md](docs/known_issues.md)
- [docs/performance.md](docs/performance.md)

</details>



This page focuses on performance considerations and optimization strategies for running AlphaFold 3. It covers hardware requirements, memory optimization, execution speed improvements, and configuration techniques to maximize throughput and efficiency.

For information about installation procedures, see [Installation Guide](#2).

## Overview of Performance Considerations

AlphaFold 3 has distinct performance profiles for its two main computational phases, executed via `run_alphafold.py`:
1. **Data Pipeline** - CPU-intensive operations for Multiple Sequence Alignment (MSA) generation and template searching using tools like `Jackhmmer` and `Nhmmer` [docs/performance.md:72-83]().
2. **Model Inference** - GPU-intensive structure prediction using JAX-compiled neural networks and diffusion sampling.

Title: Performance Bottlenecks and Optimizations across Code Entities
```mermaid
flowchart TD
    subgraph "Natural_Language_Space"
        DP["Data Pipeline Stage"]
        MI["Model Inference Stage"]
    end
    subgraph "Code_Entity_Space"
        direction LR
        Script["run_alphafold.py"] --> DataPipe["data_pipeline.py"]
        Script --> ModelInf["model_runner.py"]
        DataPipe --> Jack["Jackhmmer/Nhmmer"]
        ModelInf --> Evo["Evoformer & Diffusion"]
    end
    DP --> Script
    MI --> Script
```
Sources: [docs/performance.md:5-17](), [docs/performance.md:72-83]()

## Hardware Configuration

AlphaFold 3 is officially tested and optimized for high-end NVIDIA GPUs. Hardware choices significantly impact the maximum sequence length (tokens) that can be folded and the total runtime. 

For comprehensive details on GPU requirements, compute capabilities, CPU allocation, and verified configurations, see [Hardware Configuration](#8.1).

### GPU-Specific Considerations

For CUDA Capability 7.x GPUs (such as NVIDIA V100), you must add specific XLA flags to prevent numerical issues and residue clashing:

```bash
XLA_FLAGS="--xla_disable_hlo_passes=custom-kernel-fusion-rewriter"
```

This flag is essential as these GPUs produce incorrect outputs without it, characterized by clashing residues and very low ranking scores (often -99 or lower) [docs/known_issues.md:3-8]().

Sources: [docs/known_issues.md:3-8](), [docs/performance.md:400]()

## Memory Management

AlphaFold 3 requires significant GPU memory for large biomolecular structures. Memory strategies vary depending on whether you are prioritizing speed (preallocation) or capacity (unified memory).

For deep technical documentation on memory preallocation, unified memory, XLA memory configuration, and strategies for different GPU sizes, see [Memory Management](#8.2).

### Unified Memory for Larger Inputs

To run structures exceeding token limits or to use GPUs with less memory (e.g., A100 40GB), you can enable unified memory to spill from GPU VRAM to host RAM:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false
TF_FORCE_UNIFIED_MEMORY=true
XLA_CLIENT_MEM_FRACTION=4.0
```

Sources: [docs/performance.md:400]()

## Compilation and Execution

Optimization at the software level involves reducing JAX compilation overhead, leveraging compilation buckets, and maximizing CPU utilization during the data pipeline through database sharding.

For complete coverage of compilation buckets, JAX caching, XLA flags, database sharding scripts (`scripts/shard_databases.sh`), and parallelization strategies, see [Compilation and Execution](#8.3).

### Database Sharding

The runtime of genetic sequence searches (`Jackhmmer`/`Nhmmer`) can be reduced by 10–30× by sharding databases using `seqkit split2` [docs/performance.md:85-102](). This allows the system to utilize many CPU cores in parallel. This technique is also used by the AlphaFold Server to improve throughput [docs/known_issues.md:43-50]().

Title: Sharded Search Logic and File Specs
```mermaid
graph LR
    subgraph "Execution_Flow"
        InputSeq["Input Sequence"] --> Script["run_alphafold.py"]
        Script --> ShardSearch["Jackhmmer/Nhmmer subprocess"]
        ShardSearch --> Shard1["uniprot.fasta-00000-of-00003"]
        ShardSearch --> Shard2["uniprot.fasta-00001-of-00003"]
        ShardSearch --> ShardN["uniprot.fasta-00002-of-00003"]
        Shard1 & Shard2 & ShardN --> Merge["Merge Results"]
        Merge --> MSA["Final MSA Output"]
    end
```

To use sharded databases, provide the file spec (e.g., `uniprot.fasta@3`) and the corresponding Z-values to scale E-values correctly [docs/performance.md:116-141]().

Sources: [docs/performance.md:85-125](), [docs/known_issues.md:43-50]()

## Pipeline Stage Optimization

The `run_alphafold.py` script can be executed in stages to optimize resource utilization. This is particularly useful for splitting CPU-only tasks from GPU tasks [docs/performance.md:5-9]().

### Staged Execution Strategies

1. **Data Pipeline Only**: Launch with `--run_inference=false` [docs/performance.md:21-25](). This generates MSAs and templates, saving them into a JSON file. This can be done on CPU-only clusters.
2. **Inference Only**: Launch with `--run_data_pipeline=false` [docs/performance.md:65-69](). This uses the pre-computed MSAs/templates from the input JSON.
3. **Pre-computing Fixed Chains**: For screens where one chain is constant and others change, compute the fixed chain's MSA once and reuse it in multimer JSONs to avoid redundant searches [docs/performance.md:27-44]().

Title: Code Entity Mapping for Staged Execution
```mermaid
flowchart TD
    subgraph "Natural_Language_Space"
        NL_Data["Data Pipeline Stage"]
        NL_Inf["Inference Stage"]
    end
    subgraph "Code_Entity_Space"
        direction LR
        Runner["run_alphafold.py"] --> DataFlag["--run_data_pipeline=false"]
        Runner --> InfFlag["--run_inference=false"]
        DataFlag --> InferOnly["model_runner.py"]
        InfFlag --> DataOnly["data_pipeline.py"]
    end
    NL_Data --> DataOnly
    NL_Inf --> InferOnly
```

Sources: [docs/performance.md:5-25](), [docs/performance.md:63-69]()

## Summary of Optimization Flags

| Flag | Purpose | Source |
| :--- | :--- | :--- |
| `--run_inference=false` | Run only MSA/Template search (CPU) | [docs/performance.md:21]() |
| `--run_data_pipeline=false` | Run only Model Inference (GPU) | [docs/performance.md:65]() |
| `--jackhmmer_max_parallel_shards` | Parallelize search across DB shards | [docs/performance.md:145]() |
| `--jax_compilation_cache_dir` | Persist compiled kernels to disk | [docs/performance.md:400]() |
| `--flash_attention_implementation` | Choose between `triton`, `cudnn`, or `xla` | [docs/performance.md:400]() |

Sources: [docs/performance.md:21-145](), [docs/performance.md:400]()

---

