> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL/2-getting-started](https://deepwiki.com/deepseek-ai/DeepSeek-VL/2-getting-started)
> DeepWiki deepseek-ai/DeepSeek-VL

# Getting Started

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1)
 - [install.sh](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/install.sh)
 - [setup.py](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py)
 
  This page provides an introduction to installing and using DeepEP V2. It covers system requirements, dependency installation, building the library, and first steps for new users. DeepEP V2 features a complete refactoring of Expert Parallelism (EP) with a new **NCCL Gin backend**, replacing the NVSHMEM-based V1 for primary paths [README.md9-14](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L9-L14)

 For detailed build configuration options, see [Installation and Build](https://deepwiki.com/deepseek-ai/DeepEP/2.1-installation-and-build). For complete working examples, see [Quick Start Guide](https://deepwiki.com/deepseek-ai/DeepEP/2.2-quick-start-guide).

 **Sources:** [README.md1-109](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L1-L109)

 
---

 
## Prerequisites and System Requirements

 DeepEP V2 is optimized for modern NVIDIA GPU architectures and high-performance interconnects.

 
### Hardware Requirements

 
| Component | Requirement | Purpose |
|---|---|---|
| GPU Architecture | Hopper (SM90) or compatible | Primary target for V2 kernels README.md65 |
| Intra-node Interconnect | NVLink | High-bandwidth scale-up communication README.md71 |
| Inter-node Network | RDMA (InfiniBand/RoCE) | Scale-out communication README.md72 |

 
### Software Requirements

 
| Component | Version | Notes |
|---|---|---|
| Python | 3.8+ | README.md66 |
| CUDA Toolkit | 12.3+ | Required for SM90 PTX support README.md68 |
| PyTorch | 2.10+ | README.md69 |
| NCCL | 2.30.4+ | Required for the Gin backend README.md70 |

 **Sources:** [README.md63-72](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L63-L72)

 
---

 
## Installation Workflow Overview

 The following diagram shows the V2 installation and setup workflow, mapping steps to specific code entities and environment variables.

 
### Installation and Setup Pipeline

 
```

```

 **Sources:** [README.md74-108](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L74-L108) [setup.py13-127](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L13-L127)

 
---

 
## Core Installation Steps

 
### 1. Install NCCL

 DeepEP V2 relies on NCCL for its Gin backend. It is recommended to install it via pip so the build system can automatically locate it using the `find_pkgs` utility [README.md74-80](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L74-L80) [setup.py95](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L95-L95)

 
```

```

 
### 2. Environment Variables

 The build system and JIT compiler use several persistent environment variables that are captured during installation into `deep_ep/envs.py` [setup.py13-14](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L13-L14) [setup.py78-89](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L78-L89):

 
 - `EP_NCCL_ROOT_DIR`: Path to the NCCL installation for linking.
 - `EP_JIT_CACHE_DIR`: Directory where JIT-compiled kernels are stored.
 - `EP_NUM_TOPK_IDX_BITS`: Bits of `topk_idx.dtype` (32 or 64) [setup.py164](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L164-L164)
 - `EP_NIC_NAME`: The name of the NIC to use for RDMA communication.
 
 
### 3. Build and Install

 DeepEP uses a standard `setup.py` for installation. Note that V2 kernels are header-only and compiled at runtime via JIT, so the installation phase primarily builds the Python bindings (`csrc/python_api.cpp`) and backend wrappers [README.md3-13](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L3-L13) [setup.py100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L100-L100)

 
```

```

 For a detailed step-by-step guide including building from source and NCCL verification, see [Installation and Build](https://deepwiki.com/deepseek-ai/DeepEP/2.1-installation-and-build).

 **Sources:** [README.md88-106](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L88-L106) [setup.py13-100](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L13-L100) [install.sh1-12](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/install.sh#L1-L12)

 
---

 
## First Steps with ElasticBuffer

 In V2, the `ElasticBuffer` is the primary entry point for all EP operations [README.md113-115](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L113-L115) It unifies high-throughput and low-latency modes and handles analytical resource allocation [README.md17-20](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L17-L20)

 
### Component Relationship

 
```

```

 
### Basic Initialization

 Unlike V1, V2 calculates the optimal number of SMs analytically using `get_theoretical_num_sms`, eliminating the need for manual auto-tuning [README.md158-160](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L158-L160)

 
```

```

 For minimal working examples and a guide on handle caching for inference, see [Quick Start Guide](https://deepwiki.com/deepseek-ai/DeepEP/2.2-quick-start-guide).

 **Sources:** [README.md117-163](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L117-L163) [setup.py79-85](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/setup.py#L79-L85)

 
---

 
## Verification

 After installation, you should verify the setup using the provided test suite in `tests/elastic/` [README.md94-101](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L94-L101)

 
```

```

 **Sources:** [README.md94-101](https://github.com/deepseek-ai/DeepEP/blob/01dc3aaa/README.md?plain=1#L94-L101)
