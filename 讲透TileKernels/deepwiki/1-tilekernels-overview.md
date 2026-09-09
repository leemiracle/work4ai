> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/1-tilekernels-overview](https://deepwiki.com/deepseek-ai/TileKernels/1-tilekernels-overview)
> DeepWiki deepseek-ai/TileKernels

# TileKernels Overview

  Relevant source files 
 - [.editorconfig](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/.editorconfig)
 - [.gitignore](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/.gitignore)
 - [LICENSE](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/LICENSE)
 - [README.md](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1)
 - [pyproject.toml](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/pyproject.toml)
 
  TileKernels is a library of high-performance GPU kernels designed for Large Language Model (LLM) operations. These kernels are authored using [TileLang](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/TileLang) a domain-specific language (DSL) that enables writing optimized CUDA kernels directly in Python [README.md1-3](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L1-L3)

 The project focuses on maximizing hardware utilization for compute-intensive and memory-bound operations, targeting modern NVIDIA architectures (SM90/SM100) [README.md4-23](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L4-L23)

 
## Hardware and Software Requirements

 TileKernels is optimized for cutting-edge NVIDIA hardware and requires a modern software stack to support TileLang's JIT compilation and execution.

 
| Requirement | Minimum Version / Specification |
|---|---|
| GPU Architecture | NVIDIA SM90 (Hopper) or SM100 (Blackwell) README.md22 |
| CUDA Toolkit | 13.1 or higher README.md23 |
| Python | 3.10 or higher README.md19 |
| PyTorch | 2.10 or higher README.md20 |
| TileLang | 0.1.9 or higher README.md21 |

 For installation instructions and environment setup, see **[Getting Started: Installation and Configuration](https://deepwiki.com/deepseek-ai/TileKernels/1.1-getting-started:-installation-and-configuration)**.

 
## Core Subsystems

 The library is organized into specialized modules, each targeting a specific component of modern LLM architectures.

 
### 1. Mixture of Experts (MoE) & Gating

 Handles the complex routing logic required for MoE models, including top-k selection, token-to-expert mapping, and fused dispatch/reduction operations [README.md9-10](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L9-L10)

 
 - **Key Directories:** `tile_kernels/moe/` [README.md60](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L60-L60)
 
 
### 2. Quantization

 Provides high-performance casting kernels for low-precision formats (FP8, FP4, E5M6). This module includes fused operations like SwiGLU+Quantization to minimize memory round-trips [README.md11-12](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L11-L12)

 
 - **Key Directories:** `tile_kernels/quant/` [README.md61](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L61-L61)
 
 
### 3. Engram & Manifold HyperConnection (mHC)

 Implements specialized gating and connection mechanisms. Engram features fused RMSNorm and backward passes, while mHC provides Sinkhorn normalization and mix splitting [README.md13-14](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L13-L14)

 
 - **Key Directories:** `tile_kernels/engram/`, `tile_kernels/mhc/` [README.md63-64](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L63-L64)
 
 
### 4. Modeling & Autograd

 The `modeling` layer wraps low-level TileLang kernels into `torch.autograd.Function` objects, allowing them to be used as standard differentiable layers in PyTorch models [README.md15](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L15-L15)

 
 - **Key Directories:** `tile_kernels/modeling/` [README.md65](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L65-L65)
 
 For a detailed breakdown of the file system, see **[Repository Layout and Package Structure](https://deepwiki.com/deepseek-ai/TileKernels/1.2-repository-layout-and-package-structure)**.

 
## System Relationship Diagram

 The following diagram illustrates how TileKernels bridges the gap between high-level PyTorch modeling and low-level GPU hardware via TileLang.

 
### Logic to Code Entity Mapping

 "Entity Mapping: PyTorch to TileLang"

 
```

```

 Sources: [README.md59-68](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L59-L68) [pyproject.toml23-26](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/pyproject.toml#L23-L26)

 
### Data Flow Overview

 "Data Flow: From Model to Hardware"

 
```

```

 Sources: [README.md3-5](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L3-L5) [README.md22](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L22-L22)

 
## Child Pages

 
 - **[Getting Started: Installation and Configuration](https://deepwiki.com/deepseek-ai/TileKernels/1.1-getting-started:-installation-and-configuration)**: Guide on setting up the environment, installing the `tile-kernels` package, and configuring global SM settings.
 - **[Repository Layout and Package Structure](https://deepwiki.com/deepseek-ai/TileKernels/1.2-repository-layout-and-package-structure)**: A deep dive into the directory organization, including the purpose of `testing/`, `torch/` reference implementations, and core kernel directories.
 
 
---

 **Sources:**

 
 - [README.md1-23](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L1-L23)
 - [README.md59-68](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L59-L68)
 - [pyproject.toml1-47](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/pyproject.toml#L1-L47)
