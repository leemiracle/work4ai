<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/litgpt · page 10 Extensions · fetched 2026-10-21 -->

# Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [extensions/thunder/README.md](extensions/thunder/README.md)
- [extensions/thunder/strategies/thunder_ddp.py](extensions/thunder/strategies/thunder_ddp.py)
- [extensions/thunder/strategies/thunder_fsdp.py](extensions/thunder/strategies/thunder_fsdp.py)
- [extensions/thunder/unsloth/executor.py](extensions/thunder/unsloth/executor.py)
- [extensions/xla/README.md](extensions/xla/README.md)

</details>



LitGPT provides optional extensions to enhance performance and hardware compatibility beyond standard PyTorch eager execution. These extensions focus on two primary areas: the **Thunder** source-to-source compiler for optimized training on NVIDIA GPUs, and **XLA** support for running workloads on Google Cloud TPUs.

### Extension Ecosystem Overview

The following diagram illustrates how extensions integrate with the core LitGPT components:

```mermaid
graph TD
    subgraph "Core LitGPT"
        [litgpt.model.GPT] --> [Fabric]
    end

    subgraph "Thunder Extension"
        [ThunderFSDPStrategy] -- "wraps" --> [Fabric]
        [ThunderDDPStrategy] -- "wraps" --> [Fabric]
        [unsloth_ex] -- "optimizes" --> [litgpt.model.LLaMAMLP]
    end

    subgraph "XLA Extension"
        [xla/generate/base.py] -- "uses" --> [torch_xla]
        [xla/finetune/adapter.py] -- "uses" --> [torch_xla]
        [torch_xla] -- "targets" --> [TPU_Hardware]
    end

    [Fabric] -.-> [ThunderFSDPStrategy]
    [Fabric] -.-> [torch_xla]
```

**Sources:**
- [extensions/thunder/strategies/thunder_fsdp.py:47-61]()
- [extensions/thunder/unsloth/executor.py:161-169]()
- [extensions/xla/README.md:3-8]()

---

## Thunder Extension

[Lightning Thunder](https://github.com/Lightning-AI/lightning-thunder) is a source-to-source compiler that optimizes PyTorch programs. In LitGPT, this extension allows for significant speedups during pretraining and fine-tuning by compiling the `GPT` model into optimized "traces" that utilize high-performance kernels.

### Key Features
- **JIT Compilation**: Models are transformed into optimized Python traces using `thunder.jit()` [extensions/thunder/README.md:16-28]().
- **Distributed Strategies**: Custom Fabric strategies `ThunderFSDPStrategy` [extensions/thunder/strategies/thunder_fsdp.py:47]() and `ThunderDDPStrategy` [extensions/thunder/strategies/thunder_ddp.py:36]() provide integration for sharded and replicated data parallel training.
- **Unsloth Integration**: The extension includes a specialized `OperatorExecutor` for **Unsloth** kernels, providing optimized implementations for RoPE, SwiGLU, and Cross Entropy loss [extensions/thunder/unsloth/executor.py:24-50]().

For detailed usage instructions and optimization traces, see [Thunder Extension](#10.1).

**Sources:**
- [extensions/thunder/README.md:1-42]()
- [extensions/thunder/strategies/thunder_fsdp.py:1-102]()
- [extensions/thunder/unsloth/executor.py:1-234]()

---

## XLA Extension

The XLA extension enables LitGPT to run on **Google Cloud TPUs** (Tensor Processing Units) via the `torch_xla` backend. This is essential for large-scale training where TPU pods offer a cost-effective alternative to GPU clusters.

### Key Features
- **TPU Support**: Utilizes the PjRT runtime and `Fabric` to target TPU v4 and newer hardware [extensions/xla/README.md:3-13]().
- **Custom Recipes**: Provides standalone scripts for inference and fine-tuning (e.g., `xla/generate/base.py`, `xla/finetune/adapter.py`) that are optimized for XLA's graph compilation requirements [extensions/xla/README.md:93-111]().
- **Memory Management**: Implements `reduce_cpu_memory_usage_during_load` to handle limited TPU VM host RAM when loading large models like Falcon-40B [extensions/xla/README.md:135-137]().

For setup guides and performance benchmarks on TPU pods, see [XLA Extension](#10.2).

**Sources:**
- [extensions/xla/README.md:1-153]()

---

### Comparison of Extensions

| Feature | Thunder Extension | XLA Extension |
| :--- | :--- | :--- |
| **Primary Target** | NVIDIA GPUs (CUDA) | Google Cloud TPUs |
| **Execution Mode** | Compiled (JIT) | Graph-based (XLA) |
| **Distributed** | `ThunderFSDP`, `ThunderDDP` | `torch_xla.distributed.fsdp` |
| **Optimizations** | Unsloth Kernels, nvFusion | XLA Graph Compilation |
| **Primary Use Case** | Maximum GPU Throughput | Cost-efficient TPU Training |

**Sources:**
- [extensions/thunder/README.md:1-7]()
- [extensions/thunder/unsloth/executor.py:24-25]()
- [extensions/xla/README.md:3-4]()
- [extensions/xla/README.md:151-153]()

---

