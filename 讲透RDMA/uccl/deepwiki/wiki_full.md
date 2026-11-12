# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)

</details>



This page describes the purpose, structure, and high-level capabilities of the UCCL repository. It covers the three primary subsystems and their hardware backend support. For details on building and installing UCCL, see [Installation and Setup](#1.2). For architecture details, see [Architecture Overview](#1.1).

---

## What is UCCL?

UCCL is a GPU communication library focused on two properties:

- **Flexibility** — support fast-evolving ML workloads including collective operations, KV-cache/weight transfer, and expert-parallel (MoE) communication.
- **Portability** — run across heterogeneous GPU vendors (NVIDIA, AMD) and NIC vendors (InfiniBand, RoCE, AWS EFA, GCP TCPX, Broadcom).

The repository is organized into three independently usable subsystems, each targeting a distinct communication pattern:

| Subsystem | Directory | Primary Use Case | API Entry Point |
|---|---|---|---|
| UCCL-collective | `collective/` | Drop-in NCCL/RCCL replacement | `libnccl-net-uccl.so` via `NCCL_NET_PLUGIN` |
| UCCL-P2P | `p2p/` | Peer-to-peer GPU transfer (KV cache, weight sync) | `uccl.p2p` Python module / C `uccl_engine.cc` API |
| UCCL-EP | `ep/` | Expert-parallel MoE communication (DeepEP-compatible) | `uccl.ep` Python module / `Buffer` C++ class |

UCCL has been adopted as part of the AMD [TheRock](https://github.com/ROCm/TheRock) ecosystem.

Sources: [README.md:17-71]()

---

## Subsystems

### UCCL-collective

UCCL-collective replaces NCCL/RCCL without requiring application code changes. It is loaded at runtime as a network plugin (`.so`) via the `NCCL_NET_PLUGIN` environment variable.

Key design choices compared to stock NCCL:
- **Packet spraying** across up to 256 network paths to avoid single-path congestion.
- Software transport layer supporting advanced congestion control and selective-repeat loss recovery.
- Works on public cloud infrastructure with standard Ethernet NICs, not just InfiniBand.

Measured performance (from `README.md`):
- On 6x HGX servers (8×400G CX-7 RoCE, 8×H100): up to **2.5×** AllReduce throughput over NCCL.
- On 2× AWS `g4dn.8xlarge` (1×50G ENA, 1×T4): up to **3.7×** AllReduce throughput over NCCL.

For more details, see [UCCL-Collective](#2).

Sources: [README.md:26-48](), [collective/rdma/README.md:1-10](), [collective/efa/README.md:1-10]()

---

### UCCL-P2P

UCCL-P2P provides both NIXL-style initiator-target transfer APIs and NCCL-style collective APIs from a single C++ `Endpoint` class. It is designed for next-generation 800 Gbps NICs with multi-threaded transfer engines.

Key capabilities:
- Two-sided (`send`/`recv`) and one-sided (`read`/`write`) RDMA operations.
- Intra-node IPC via GPU shared memory rings (NVLink/PCIe).
- Python bindings via `pybind11` exposed as `uccl.p2p`.
- `CollectiveContext` for drop-in PyTorch distributed send/recv replacement.

For more details, see [UCCL-P2P Engine](#3).

Sources: [README.md:50-58]()

---

### UCCL-EP

UCCL-EP is a drop-in replacement for [DeepEP](https://github.com/deepseek-ai/DeepEP), targeting Mixture-of-Experts (MoE) model communication. It supports GPU-initiated RDMA via a CPU proxy layer, reaching IBGDA-level performance without locking users to a single NIC vendor.

Key capabilities:
- High-throughput mode (NVLink + RDMA forwarding) and low-latency mode (pure RDMA).
- Supports NVIDIA H100/H200/B200, AMD MI300X, and NICs including EFA, Broadcom Thor-2, CX-7.
- Python `Buffer` class (in `ep/`) with `low_latency_dispatch` / `low_latency_combine` API.

Selected benchmark results (EP32, internode):

| Platform | Dispatch Bandwidth | Combine Bandwidth |
|---|---|---|
| p5en (8×H200 + 16×200Gb/s EFA) | 54 GB/s (RDMA) | 43 GB/s (RDMA) |
| p6-b200 (8×B200 + 8×400Gb/s EFA) | 53 GB/s (RDMA) | 57 GB/s (RDMA) |
| MI300X + CX7 InfiniBand | 60 GB/s (RDMA) | 60 GB/s (RDMA) |

For more details, see [UCCL-EP Expert Parallelism](#4).

Sources: [README.md:59-69](), [ep/README.md:1-50](), [ep/README.md:138-210]()

---

## Subsystem-to-Code Entity Map

**Figure 1: UCCL Subsystems and Their Primary Code Entities**

```mermaid
graph TD
  subgraph collective ["collective/ (UCCL-Collective)"]
    rdma_dir["collective/rdma/"]
    efa_dir["collective/efa/"]
    afxdp_dir["collective/afxdp/"]
    plugin["libnccl-net-uccl.so\n(NCCL_NET_PLUGIN)"]
    rdma_dir --> plugin
    efa_dir --> plugin
    afxdp_dir --> plugin
  end

  subgraph p2p ["p2p/ (UCCL-P2P)"]
    engine_cc["engine.cc\nEndpoint class"]
    uccl_engine_cc["uccl_engine.cc\nC API"]
    pybind_engine["pybind_engine.cc\nuccl.p2p Python module"]
    collective_py["collective.py\nCollectiveContext"]
    engine_cc --> uccl_engine_cc
    engine_cc --> pybind_engine
    pybind_engine --> collective_py
  end

  subgraph ep ["ep/ (UCCL-EP)"]
    uccl_ep_cc["src/uccl_ep.cc\nBuffer C++ class"]
    proxy_cpp["src/proxy.cpp\nProxy / UcclProxy"]
    internode_cu["src/internode.cu\nGPU kernels (HT mode)"]
    internode_ll_cu["src/internode_ll.cu\nGPU kernels (LL mode)"]
    buffer_py["bench/buffer.py\nBuffer Python wrapper"]
    uccl_ep_cc --> proxy_cpp
    uccl_ep_cc --> buffer_py
    proxy_cpp --> internode_cu
    proxy_cpp --> internode_ll_cu
  end

  subgraph ukernel ["experimental/ukernel/ (UKernel)"]
    persistent_kernel["PersistentKernel\nGPU task manager"]
  end
```

Sources: [README.md:23-71](), [ep/Makefile:76-84](), [ep/setup.py:97-99]()

---

## Hardware Backend Support

**Figure 2: Hardware Backend Support by Subsystem**

```mermaid
graph LR
  subgraph subsystems ["Subsystems"]
    CCL["UCCL-collective\ncollective/rdma/\ncollective/efa/\ncollective/afxdp/"]
    P2P["UCCL-P2P\np2p/"]
    EP["UCCL-EP\nep/"]
  end

  subgraph nics ["NIC Backends"]
    IB["InfiniBand / RoCE\n(IBChannelImpl)"]
    EFA["AWS EFA\n(EFAChannelImpl)"]
    TCPX["GCP TCPX"]
    Thor["Broadcom Thor-2"]
  end

  subgraph gpus ["GPU Platforms"]
    CUDA["NVIDIA CUDA\n(H100/H200/B200/T4/A100)"]
    ROCM["AMD ROCm\n(MI300X/MI325X/MI355X)"]
  end

  subgraph intra ["Intra-node"]
    NVL["NVLink / PCIe\n(jring_t shared memory)"]
  end

  CCL --> IB
  CCL --> EFA
  CCL --> TCPX
  CCL --> CUDA
  CCL --> ROCM

  P2P --> IB
  P2P --> EFA
  P2P --> TCPX
  P2P --> NVL
  P2P --> CUDA
  P2P --> ROCM

  EP --> IB
  EP --> EFA
  EP --> Thor
  EP --> NVL
  EP --> CUDA
  EP --> ROCM
```

Sources: [README.md:59-71](), [ep/README.md:1-5](), [collective/rdma/README.md:1-8](), [collective/efa/README.md:1-5]()

---

## Quick Start

Build UCCL using `build.sh`, which runs a Docker-based build and optionally installs the Python wheel:

```bash
git clone https://github.com/uccl-project/uccl.git --recursive && cd uccl
bash build.sh [cuda|rocm|therock] [all|ccl_rdma|ccl_efa|p2p|ep] [py_version] --install
```

After installation, plug UCCL into existing NCCL/RCCL workloads by setting:

```bash
# IB/RoCE (NVIDIA or AMD)
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`

# AWS EFA
LD_PRELOAD=`python -c "import uccl; print(uccl.efa_nccl_path())"`
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.efa_plugin_path())"`
```

For full build instructions, Docker environment details, and per-platform prerequisites, see [Installation and Setup](#1.2).

Sources: [README.md:90-118](), [build.sh:1-18](), [build.sh:35-46]()

---

## Road Map Status

| Feature | Status |
|---|---|
| KV cache transfer engine (AMD support) | ✅ Complete |
| KV cache transfer engine (RDMA, EFA, TCPX, TCP) | 🚧 In progress |
| Expert-parallel communication (all NICs, AMD GPUs) | ✅ Complete |
| EP congestion control | 🚧 In progress |
| NCCL re-architecture (scalable CPU proxy) | 🚧 In progress |
| Fast async collectives with compute-communication ordering | ☐ Planned |
| Device kernels in Triton | ☐ Planned |
| Dynamic membership (GPU server join/exit) | ☐ Planned |

Sources: [README.md:73-88]()

---

# Page: Architecture Overview

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This document provides a high-level overview of UCCL's system architecture, covering the multi-transport backend design, plugin integration model, and core communication patterns. For specific transport implementation details, see [RDMA Transport](#2.1), [EFA Transport](#2.2), and [AF_XDP Transport](#2.3). For P2P communication specifics, see [P2P Communication Engine](#3). For NCCL/RCCL integration details, see [NCCL and RCCL Integration](#5).

## System Overview

UCCL (Unified Collective Communication Library) is a high-performance GPU communication library that provides multiple transport backends while maintaining compatibility with existing NCCL/RCCL APIs. The system employs a plugin architecture where applications use standard NCCL/RCCL libraries, which dynamically load UCCL transport plugins to achieve superior performance across various network environments.

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        APP1["PyTorch Applications"]
        APP2["Python P2P API<br/>collective.py"]
        APP3["Expert-Parallel API<br/>ep.py"]
    end
    
    subgraph "NCCL/RCCL Integration Layer"
        NCCL["NCCL/RCCL Library"]
        RDMA_PLUGIN["libnccl-net-uccl.so<br/>RDMA Plugin"]
        EFA_PLUGIN["libnccl-net-efa.so<br/>EFA Plugin"]
    end
    
    subgraph "UCCL Core Transport Systems"
        subgraph "RDMA Transport"
            RDMA_EP["RDMAEndpoint"]
            RDMA_ENG["UcclRDMAEngine"]
            RDMA_CTX["RDMAContext"]
        end
        
        subgraph "EFA Transport"
            EFA_EP["Endpoint"]
            EFA_ENG["UcclEngine"] 
            EFA_FLOW["UcclFlow"]
        end
        
        subgraph "AF_XDP Transport"
            AFXDP_EP["Endpoint"]
            AFXDP_ENG["UcclEngine"]
            AFXDP_SOCK["AFXDPSocket"]
        end
        
        subgraph "P2P Engine"
            P2P_EP["Endpoint"]
            P2P_CONN["Connections"]
        end
        
        subgraph "Expert-Parallel System"
            EP_BUF["Buffer Classes"]
            EP_RT["C++ Runtime"]
            EP_PROXY["CPU Proxies"]
        end
    end
    
    subgraph "Network Hardware Layer"
        IB["InfiniBand<br/>Mellanox NICs"]
        ROCE["RoCE<br/>Ethernet + RDMA"]
        AWS_EFA["AWS EFA<br/>p4d instances"]
        ETH["Ethernet<br/>AF_XDP capable"]
    end
    
    APP1 --> NCCL
    APP2 --> P2P_EP
    APP3 --> EP_BUF
    
    NCCL --> RDMA_PLUGIN
    NCCL --> EFA_PLUGIN
    
    RDMA_PLUGIN --> RDMA_EP
    EFA_PLUGIN --> EFA_EP
    
    RDMA_EP --> RDMA_ENG
    RDMA_ENG --> RDMA_CTX
    
    EFA_EP --> EFA_ENG
    EFA_ENG --> EFA_FLOW
    
    AFXDP_EP --> AFXDP_ENG
    AFXDP_ENG --> AFXDP_SOCK
    
    P2P_EP --> P2P_CONN
    EP_BUF --> EP_RT
    EP_RT --> EP_PROXY
    
    RDMA_EP --> IB
    RDMA_EP --> ROCE
    EFA_EP --> AWS_EFA
    AFXDP_EP --> ETH
    P2P_EP --> IB
    EP_PROXY --> IB
```

**Sources:** [rdma/transport.h:97-98](), [efa/transport.h:189-190](), [afxdp/transport.h:188-189](), [rdma/nccl_plugin.cc:85-91](), [efa/nccl_plugin.cc:1-20]()

## Core Architecture Pattern

All UCCL transport backends follow a consistent three-tier hierarchical pattern with shared design principles:

### Transport Architecture Hierarchy

```mermaid
graph TB
    subgraph "Tier 1: Endpoint Layer"
        RDMA_EP["RDMAEndpoint<br/>num_engines_per_dev_<br/>engine_vec_[total_num_engines]"]
        EFA_EP["Endpoint<br/>engine_vec_[kNumEngines]<br/>sock_vec_[kNumVdevices]"]
        AFXDP_EP["Endpoint<br/>engine_vec_[NUM_QUEUES]<br/>socket_vec_[NUM_QUEUES]"]
    end
    
    subgraph "Tier 2: Engine Layer"
        RDMA_ENG["UcclRDMAEngine<br/>rdma_ctx_map_<br/>channel_<br/>run()"]
        EFA_ENG["UcclEngine<br/>flow_map_<br/>channel_<br/>run()"]
        AFXDP_ENG["UcclEngine<br/>flow_map_<br/>channel_<br/>run()"]
    end
    
    subgraph "Tier 3: Connection Layer"
        RDMA_FLOW["UcclFlow<br/>sub_flows_[]<br/>recv_comm_<br/>send_comm_"]
        EFA_FLOW["UcclFlow<br/>tx_tracking_<br/>rx_tracking_<br/>pcb_"]
        AFXDP_FLOW["UcclFlow<br/>tx_tracking_<br/>rx_tracking_<br/>pcb_"]
    end
    
    subgraph "Command Queue System"
        CHANNEL["Channel<br/>tx_cmdq_<br/>rx_cmdq_<br/>ctrl_cmdq_"]
        JRING["jring_t*<br/>Lock-free Ring Buffers"]
    end
    
    RDMA_EP --> RDMA_ENG
    EFA_EP --> EFA_ENG  
    AFXDP_EP --> AFXDP_ENG
    
    RDMA_ENG --> RDMA_FLOW
    EFA_ENG --> EFA_FLOW
    AFXDP_ENG --> AFXDP_FLOW
    
    RDMA_ENG --> CHANNEL
    EFA_ENG --> CHANNEL
    AFXDP_ENG --> CHANNEL
    
    CHANNEL --> JRING
```

### Engine Threading Model

```mermaid
graph LR
    subgraph "Application Threads"
        APP_THREAD1["App Thread 1"]
        APP_THREAD2["App Thread 2"]
    end
    
    subgraph "Engine Thread Pool"
        ENG_THREAD1["Engine Thread 1<br/>pin_thread_to_cpu()"]
        ENG_THREAD2["Engine Thread 2<br/>pin_thread_to_cpu()"]
    end
    
    subgraph "Worker Thread Functions"
        RUN_LOOP["run()<br/>handle_rx_work()<br/>handle_tx_work()<br/>handle_completion()"]
        PERIODIC["periodic_process()<br/>handle_rto()<br/>process_ctl_reqs()"]
    end
    
    APP_THREAD1 --> CHANNEL
    APP_THREAD2 --> CHANNEL
    CHANNEL --> ENG_THREAD1
    CHANNEL --> ENG_THREAD2
    
    ENG_THREAD1 --> RUN_LOOP
    ENG_THREAD2 --> RUN_LOOP
    RUN_LOOP --> PERIODIC
```

**Sources:** [rdma/transport.h:688-714](), [rdma/transport.cc:277-316](), [efa/transport.h:265-300](), [afxdp/transport.h:357-410](), [rdma/transport.cc:437-473]()

## RDMA Transport Architecture

The RDMA transport provides the highest performance backend with support for InfiniBand and RoCE networks:

### RDMAEndpoint Resource Management

```mermaid
graph TB
    subgraph "RDMAEndpoint Initialization"
        EP_INIT["RDMAEndpoint(num_engines_per_dev)<br/>initialize_resources()"]
        DEVICE_INIT["RDMAFactory::init_devs()<br/>get_factory_dev()"]
        ENGINE_THREADS["engine_th_vec_<br/>CPU Thread Pool"]
    end
    
    subgraph "Per-Device Engine Pool"
        ENG_MAP["engine_id_to_engine_map_<br/>std::map<int, UcclRDMAEngine>"]
        CHANNEL_VEC["channel_vec_<br/>Channel* array"]
        LOAD_VEC["engine_load_vec_<br/>atomic<uint32_t>* array"]
    end
    
    subgraph "Engine Load Balancing"
        FIND_POT["find_pot_load_engine_idx()"]
        FIND_LEAST["find_least_loaded_engine_idx()"]
        FIND_RR["find_rr_engine_idx()"]
    end
    
    EP_INIT --> DEVICE_INIT
    EP_INIT --> ENGINE_THREADS
    EP_INIT --> ENG_MAP
    ENG_MAP --> CHANNEL_VEC
    ENG_MAP --> LOAD_VEC
    
    LOAD_VEC --> FIND_POT
    LOAD_VEC --> FIND_LEAST
    LOAD_VEC --> FIND_RR
```

### UcclRDMAEngine Core Loop

```mermaid
graph LR
    subgraph "Engine Main Loop"
        RUN_START["run()<br/>while(!shutdown_)"]
        PERIODIC_CHK["elapsed_tsc >= kSlowTimerIntervalTsc_<br/>periodic_process()"]
        CLOCK_SYNC["handle_clock_synchronization()"]
        RX_WORK["handle_rx_work()<br/>supply_rx_buff()"]
        TX_WORK["handle_tx_work()<br/>tx_message()"]
        TIMING_WHEEL["handle_timing_wheel()<br/>burst_timing_wheel()"]
        COMPLETION["handle_completion()<br/>rc_handle_completion()<br/>uc_handle_completion()"]
    end
    
    RUN_START --> PERIODIC_CHK
    PERIODIC_CHK --> CLOCK_SYNC
    CLOCK_SYNC --> RX_WORK
    RX_WORK --> TX_WORK
    TX_WORK --> TIMING_WHEEL
    TIMING_WHEEL --> COMPLETION
    COMPLETION --> RUN_START
```

### RDMAContext and Congestion Control

```mermaid
graph TB
    subgraph "RDMAContext Structure"
        RDMA_CTX["RDMAContext<br/>per-peer context"]
        DP_QPS["dp_qps_<br/>QPWrapper[ucclParamPORT_ENTROPY()]"]
        CREDIT_QP["credit_qp_<br/>struct ibv_qp*"]
        WHEEL["wheel_<br/>TimingWheel"]
    end
    
    subgraph "Congestion Control Implementations"
        TIMELY_CTX["TimelyRDMAContext<br/>EventOnQueueData()<br/>EventOnChunkSize()"]
        SWIFT_CTX["SwiftRDMAContext<br/>hard_budget, soft_budget<br/>flow_budget checks"]
        EQDS_CTX["EQDSRDMAContext<br/>EventOnRxCredit()<br/>spend_credit()"]
    end
    
    subgraph "Flow Management"
        UCCL_FLOW["UcclFlow<br/>recv_comm_, send_comm_"]
        SUB_FLOWS["sub_flows_<br/>SubUcclFlow[ucclParamNUM_ENGINES()]"]
        PCB_EQDS["pcb.eqds_cc<br/>credit management"]
        PCB_TIMELY["pcb.timely_cc<br/>rate pacing"]
    end
    
    RDMA_CTX --> DP_QPS
    RDMA_CTX --> CREDIT_QP
    RDMA_CTX --> WHEEL
    
    RDMA_CTX --> TIMELY_CTX
    RDMA_CTX --> SWIFT_CTX
    RDMA_CTX --> EQDS_CTX
    
    TIMELY_CTX --> WHEEL
    SWIFT_CTX --> WHEEL
    EQDS_CTX --> WHEEL
    
    RDMA_CTX --> UCCL_FLOW
    UCCL_FLOW --> SUB_FLOWS
    SUB_FLOWS --> PCB_EQDS
    SUB_FLOWS --> PCB_TIMELY
```

**Sources:** [rdma/transport.cc:688-728](), [rdma/transport.h:739-864](), [rdma/transport.h:538-732](), [rdma/transport.cc:437-473](), [rdma/transport.cc:827-858]()

## Transport Backend Comparison

UCCL provides three specialized transport backends optimized for different network infrastructures:

| Backend | Network Target | Configuration | Key Implementation | Transport Protocol |
|---------|----------------|---------------|-------------------|-------------------|
| **RDMA** | InfiniBand, RoCE | `ucclParamNUM_ENGINES()=4`<br/>`ucclParamPORT_ENTROPY()=32` | `RDMAEndpoint`<br/>`UcclRDMAEngine`<br/>`RDMAContext` | RC/UC QPs<br/>RDMA Write/Read<br/>Credit-based flow control |
| **EFA** | AWS EFA (p4d) | `kNumVdevices=8`<br/>`kNumEnginesPerVdev=2` | `Endpoint`<br/>`UcclEngine`<br/>`UcclFlow` | UD datagrams<br/>Multi-path<br/>SACK-based reliability |
| **AF_XDP** | Ethernet | `NUM_QUEUES=12`<br/>`kMaxPath=200` | `Endpoint`<br/>`UcclEngine`<br/>`AFXDPSocket` | UDP over AF_XDP<br/>eBPF packet filtering<br/>Kernel bypass |

### Congestion Control Support

| Transport | Sender CC | Receiver CC | Implementation Classes |
|-----------|-----------|-------------|----------------------|
| **RDMA** | Timely, Swift | EQDS | `TimelyRDMAContext`<br/>`SwiftRDMAContext`<br/>`EQDSRDMAContext` |
| **EFA** | Timely, Cubic | EQDS | `swift::TimelyCtl`<br/>`swift::CubicCtl`<br/>`eqds::EQDSCC` |
| **AF_XDP** | Timely, Cubic | None | `swift::TimelyCtl`<br/>`swift::CubicCtl` |

### Hardware Requirements

| Backend | NICs | GPU Direct | Privileges | Maximum Performance |
|---------|------|------------|-----------|-------------------|
| **RDMA** | Mellanox CX-5+<br/>Broadcom NICs | GPUDirectRDMA | User space | 400Gbps per NIC |
| **EFA** | AWS EFA NICs | Supported | User space | 100Gbps per vEFA |
| **AF_XDP** | Any Ethernet NIC | No | CAP_NET_ADMIN<br/>Privileged daemon | Link speed dependent |

**Sources:** [rdma/transport_config.h:26-29](), [efa/transport_config.h:35-37](), [afxdp/transport_config.h:29-44](), [rdma/transport.h:622-732](), [efa/transport_cc.h:1-50]()

## Plugin Integration Architecture

UCCL integrates with NCCL/RCCL through standardized plugin interfaces that provide transparent performance acceleration:

### Plugin Lifecycle and API

```mermaid
graph TB
    subgraph "NCCL Plugin Interface (ncclNetPlugin_v8)"
        INIT["pluginInit(logFunction)<br/>Initialize shared RDMAEndpoint"]
        DEVICES["pluginDevices(*ndev)<br/>Return ep->get_num_devices()"]
        PROPS["pluginGetProperties(dev, props)<br/>Fill ncclNetProperties_v8_t"]
        LISTEN["pluginListen(dev, handle, listenComm)<br/>Create ucclListenComm"]
        CONNECT["pluginConnect(dev, handle, sendComm)<br/>Create ucclSendComm"]
        ACCEPT["pluginAccept(listenComm, recvComm)<br/>Create ucclRecvComm"]
    end
    
    subgraph "Plugin Data Structures"
        HANDLE["ucclHandle<br/>ip_addr_u32<br/>listen_port<br/>remote_dev<br/>ConnState"]
        LISTEN_COMM["ucclListenComm<br/>listen_fd<br/>AsyncAcceptState"]
        SEND_COMM["ucclSendComm<br/>ucclBaseComm<br/>ConnID conn_id"]
        RECV_COMM["ucclRecvComm<br/>ucclBaseComm<br/>remote_ip_str"]
        BASE_COMM["ucclBaseComm<br/>ConnID conn_id<br/>ucclRequestBuffPool"]
    end
    
    subgraph "Request Processing"
        ISEND["pluginIsend()<br/>Channel::Msg::kTx"]
        IRECV["pluginIrecv()<br/>Channel::Msg::kRx"]
        IFLUSH["pluginIflush()<br/>GPU memory flush"]
        TEST["pluginTest()<br/>Poll completion"]
    end
    
    INIT --> DEVICES
    DEVICES --> PROPS
    PROPS --> LISTEN
    LISTEN --> CONNECT
    CONNECT --> ACCEPT
    
    LISTEN --> LISTEN_COMM
    CONNECT --> SEND_COMM
    ACCEPT --> RECV_COMM
    
    SEND_COMM --> BASE_COMM
    RECV_COMM --> BASE_COMM
    LISTEN_COMM --> HANDLE
    
    BASE_COMM --> ISEND
    BASE_COMM --> IRECV
    BASE_COMM --> IFLUSH
    BASE_COMM --> TEST
```

### Request Buffer Management

```mermaid
graph LR
    subgraph "ucclRequestBuffPool"
        POOL_INIT["BuffPool(kMaxReq<<2, sizeof(ucclRequest))"]
        POOL_POP["pop()<br/>Get available ucclRequest"]
        POOL_PUSH["push()<br/>Return completed ucclRequest"]
    end
    
    subgraph "ucclRequest Structure"
        REQ_TYPE["type: ReqSend/ReqRecv"]
        REQ_DATA["send/recv union<br/>data pointers<br/>lengths"]
        REQ_MHANDLE["mhandle: ibv_mr*<br/>memory registration"]
        REQ_DONE["rc_or_flush_done<br/>completion flag"]
    end
    
    subgraph "Channel Integration"
        TX_CMDQ["channel_->tx_cmdq_<br/>jring_mp_enqueue_bulk()"]
        RX_CMDQ["channel_->rx_cmdq_<br/>jring_mp_enqueue_bulk()"]
        ENGINE_POLL["Engine polls cmdq<br/>jring_sc_dequeue_bulk()"]
    end
    
    POOL_POP --> REQ_TYPE
    REQ_TYPE --> REQ_DATA
    REQ_DATA --> REQ_MHANDLE
    REQ_MHANDLE --> REQ_DONE
    
    REQ_DONE --> TX_CMDQ
    REQ_DONE --> RX_CMDQ
    TX_CMDQ --> ENGINE_POLL
    RX_CMDQ --> ENGINE_POLL
    
    ENGINE_POLL --> POOL_PUSH
```

**Sources:** [rdma/nccl_plugin.cc:85-91](), [rdma/nccl_plugin.cc:21-83](), [rdma/nccl_plugin.cc:200-400](), [rdma/transport.h:44-93]()

## Advanced Features

### Congestion Control Integration

UCCL implements multiple congestion control algorithms that can be selected at compile time:

```mermaid
graph LR
    subgraph "Congestion Control Algorithms"
        TIMELY_CC["Timely CC<br/>(Latency-based)"]
        SWIFT_CC["Swift CC<br/>(Budget-based)"]
        EQDS_CC["EQDS CC<br/>(Receiver-driven)"]
    end
    
    subgraph "Implementation Classes"
        TIMELY_IMPL["TimelyRDMAContext<br/>EventOnRxACK()"]
        SWIFT_IMPL["SwiftRDMAContext<br/>EventOnChunkSize()"]
        EQDS_IMPL["EQDSRDMAContext<br/>EventOnRxCredit()"]
    end
    
    subgraph "Packet Scheduling"
        TIMING_WHEEL["TimingWheel<br/>queue_on_timing_wheel()"]
        BURST["burst_timing_wheel()"]
    end
    
    TIMELY_CC --> TIMELY_IMPL
    SWIFT_CC --> SWIFT_IMPL
    EQDS_CC --> EQDS_IMPL
    
    TIMELY_IMPL --> TIMING_WHEEL
    SWIFT_IMPL --> TIMING_WHEEL
    EQDS_IMPL --> TIMING_WHEEL
    
    TIMING_WHEEL --> BURST
```

**Sources:** [rdma/transport.h:622-732](), [rdma/transport_config.h:73-90](), [rdma/transport.cc:430-435]()

### GPU-Driven Communication

UCCL introduces innovative GPU-driven communication where GPU kernels directly initiate RDMA transfers:

```mermaid
graph TB
    subgraph "Traditional CPU-Driven"
        CPU_APP["CPU Application"]
        CPU_RDMA["CPU Posts RDMA"]
        GPU_MEM["GPU Memory Transfer"]
        
        CPU_APP --> CPU_RDMA
        CPU_RDMA --> GPU_MEM
    end
    
    subgraph "UCCL GPU-Driven Innovation"
        GPU_KERN["GPU Kernel"]
        RING_BUF["DeviceToHostCmdBuffer<br/>(Ring Buffer)"]
        CPU_PROXY["CPU Proxy Thread<br/>run_sender()/run_remote()"]
        RDMA_OP["RDMA Operations"]
        
        subgraph "Use Cases"
            MOE["Mixture of Experts<br/>Token Routing"]
            ALLTOALL["All-to-All Communication"]
            PIPELINE["Pipeline Parallelism"]
        end
        
        GPU_KERN --> RING_BUF
        RING_BUF --> CPU_PROXY
        CPU_PROXY --> RDMA_OP
        
        MOE -.-> GPU_KERN
        ALLTOALL -.-> GPU_KERN
        PIPELINE -.-> GPU_KERN
    end
```

**Sources:** [gpu_driven/ directory references in README.md](), [p2p/README.md:1-50]()

This architecture enables ultra-low latency communication by eliminating CPU-GPU round trips and allowing GPUs to directly control network operations for workloads like Mixture of Experts models.

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docker/Dockerfile.cuda](docker/Dockerfile.cuda)
- [docker/Dockerfile.efa](docker/Dockerfile.efa)
- [docker/Dockerfile.gh](docker/Dockerfile.gh)
- [docker/Dockerfile.rocm](docker/Dockerfile.rocm)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/install_deps.sh](ep/install_deps.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This page covers how to obtain, build, and install UCCL for production and development use. It describes the `build.sh` top-level build script, Docker image selection, Python wheel installation, and platform-specific prerequisites for CUDA, ROCm/TheRock, and AWS EFA environments.

For details on what each subsystem does once installed, see the Architecture Overview ([1.1](#1.1)). For per-subsystem build differences (Makefiles, platform flags), see Build Scripts and Docker Environments ([6.1](#6.1)) and Platform-Specific Configuration ([6.2](#6.2)).

---

## Prerequisites

### System Dependencies (Development Builds)

When building outside Docker, install the following system packages on Ubuntu 22.04:

```
sudo apt update
sudo apt install linux-tools-$(uname -r) clang llvm cmake m4 build-essential \
                 net-tools libgoogle-glog-dev libgtest-dev libgflags-dev \
                 libelf-dev libpcap-dev libc6-dev-i386 libpci-dev \
                 libopenmpi-dev libibverbs-dev clang-format -y
```

Python dependencies for building and running:

```
pip install paramiko intervaltree pybind11 nanobind
conda install -c conda-forge "libstdcxx-ng>=12" "libgcc-ng>=12"
```

Sources: [README.md:133-150]()

### Cloning the Repository

```
git clone https://github.com/uccl-project/uccl.git --recursive
export UCCL_HOME=$(pwd)/uccl
```

The `--recursive` flag is required because UCCL uses git submodules (e.g., `thirdparty/nccl`, `thirdparty/rccl`, `thirdparty/nccl-sg`).

Sources: [README.md:124-128]()

---

## Build System Overview

All standard builds go through `build.sh`. It selects the correct Docker image, builds inside the container, then uses `auditwheel` to produce a portable Python wheel.

**Build Decision Diagram: `build.sh` target and type selection**

```mermaid
flowchart TD
    A["build.sh invocation"] --> B{"TARGET\n(cuda|rocm|therock)"}
    B --> C{"ARCH\naarch64?"}
    C -->|"aarch64 + CUDA"| D["docker/Dockerfile.gh\nIMAGE: uccl-builder-gh"]
    C -->|"x86 + IS_EFA"| E["docker/Dockerfile.efa\nIMAGE: uccl-builder-efa"]
    C -->|"x86 + CUDA"| F["docker/Dockerfile.cuda\nIMAGE: uccl-builder-cuda"]
    B --> G["docker/Dockerfile.rocm\nIMAGE: uccl-builder-rocm"]
    B --> H["docker/Dockerfile.therock\nIMAGE: uccl-builder-therock"]

    I["BUILD_TYPE"] --> J{"all"}
    I --> K{"ccl_rdma → build_ccl_rdma()"}
    I --> L{"ccl_efa → build_ccl_efa()"}
    I --> M{"p2p → build_p2p()"}
    I --> N{"ep → build_ep()"}
    I --> O{"ukernel → build_ukernel()"}

    J --> K
    J --> L
    J --> M
```

Sources: [build.sh:1-100](), [build.sh:134-170](), [shared.sh:26-184]()

---

## `build.sh` Usage

```
bash build.sh [cuda|rocm|therock] [all|ccl_rdma|ccl_efa|p2p|ep] \
              [py_version] [rocm_index_url] [--install]
```

### Positional Arguments

| Position | Name | Default | Description |
|---|---|---|---|
| 1 | `TARGET` | `cuda` | GPU platform: `cuda`, `cuda13`, `rocm`, `rocm6`, `therock` |
| 2 | `BUILD_TYPE` | `all` | Component(s) to build |
| 3 | `PY_VER` | auto-detected | Python version, e.g., `3.12` |
| 4 | `ROCM_IDX_URL` | `https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu` | ROCm wheel index (TheRock only) |

### Optional Flag

| Flag | Effect |
|---|---|
| `--install` | After building, installs the wheel into the current Python environment |

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `CONTAINER_ENGINE` | `docker` | Use `podman` as an alternative |
| `USE_INTEL_RDMA_NIC` | `0` | Enable Intel RDMA NIC (irdma, vendor 0x8086) support |
| `TORCH_CUDA_ARCH_LIST` | auto-detected | Override GPU architecture for `ep`/`p2p` builds |
| `DISABLE_AGGRESSIVE_ATOMIC` | `0` | Disable aggressive atomics in EP (AMD) |

Sources: [build.sh:9-18](), [build.sh:26-46](), [build.sh:240-249]()

### Common Invocations

| Goal | Command |
|---|---|
| Build everything for CUDA, install | `bash build.sh cuda all --install` |
| Build only P2P for CUDA | `bash build.sh cuda p2p` |
| Build EP for ROCm 7 | `bash build.sh rocm ep --install` |
| Build CCL RDMA for CUDA 13 | `bash build.sh cuda13 ccl_rdma --install` |
| Build for TheRock (AMD) | `bash build.sh therock all 3.12 https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu --install` |
| Build with Intel RDMA NIC | `USE_INTEL_RDMA_NIC=1 bash build.sh cuda ccl_efa` |

Sources: [README.md:92-100](), [build.sh:272-289]()

---

## Docker Images

`build.sh` builds one of four Dockerfiles depending on the platform and detected hardware:

**Docker Image Selection by Context**

```mermaid
flowchart LR
    subgraph "CUDA targets"
        DC["docker/Dockerfile.cuda\nnvidia/cuda:12.8.0-devel-ubuntu22.04\nStandard CUDA x86"]
        DG["docker/Dockerfile.gh\nnvidia/cuda:12.8.0-devel-ubuntu22.04\nARM64 / GH200"]
        DE["docker/Dockerfile.efa\nnvidia/cuda:12.8.0-devel-ubuntu22.04\n+ aws-efa-installer-1.42.0"]
    end
    subgraph "ROCm targets"
        DR["docker/Dockerfile.rocm\nrocm/dev-ubuntu-22.04\nAMD GPU"]
        DT["docker/Dockerfile.therock\nquay.io/pypa/manylinux_2_28_x86_64\nAMD TheRock ecosystem"]
    end
```

Sources: [docker/Dockerfile.cuda:1-50](), [docker/Dockerfile.gh:1-50](), [docker/Dockerfile.efa:1-72](), [docker/Dockerfile.rocm:1-54]()

### What Each Dockerfile Installs

| Dockerfile | Base Image | Extra Packages |
|---|---|---|
| `Dockerfile.cuda` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | `libibverbs-dev`, `libnuma-dev`, `libgoogle-glog-dev`, PyTorch cu128 |
| `Dockerfile.gh` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | Same as CUDA; sets `GPU_NAME=GH200` |
| `Dockerfile.efa` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | Same as CUDA + `aws-efa-installer-1.42.0` at `/opt/amazon/efa` |
| `Dockerfile.rocm` | `rocm/dev-ubuntu-22.04` | `hipcub`, `hipsolver`, `hipblas`, PyTorch ROCm nightly |

All images install `pybind11`, `nanobind`, `auditwheel`, and `build` for Python wheel construction.

Sources: [docker/Dockerfile.cuda:13-43](), [docker/Dockerfile.efa:34-67](), [docker/Dockerfile.rocm:11-46](), [docker/Dockerfile.gh:12-41]()

---

## Build Functions in `shared.sh`

`build.sh` exports shell functions from `shared.sh` into the Docker container. Each function builds one component and copies its output into `uccl/` or `uccl/lib/`.

**Component Build Functions and Their Outputs**

```mermaid
flowchart TD
    subgraph "shared.sh functions"
        R["build_ccl_rdma(TARGET, ARCH, IS_EFA)\ncollective/rdma/Makefile\n→ libnccl-net-uccl.so or librccl-net-uccl.so\n→ uccl/lib/"]
        E["build_ccl_efa(TARGET, ARCH, IS_EFA)\ncollective/efa/Makefile\n+ thirdparty/nccl-sg\n→ libnccl-net-efa.so, libnccl-efa.so\n→ uccl/lib/"]
        P["build_p2p(TARGET, ARCH, IS_EFA)\np2p/Makefile (cuda)\np2p/Makefile.rocm\np2p/Makefile.therock\n→ p2p*.so, libuccl_p2p.so\ncollective.py, utils.py\n→ uccl/"]
        EP["build_ep(TARGET, ARCH, IS_EFA)\nep/setup.py build\n→ ep*.so\n→ uccl/"]
        UK["build_ukernel(TARGET, ARCH, IS_EFA)\nexperimental/ukernel/Makefile\n→ *ukernel*.so\n→ uccl/lib/"]
        RN["rename_to_abi3(dir)\nRenames .cpython-*.so\n→ .abi3.so"]
    end
    R --> RN
    E --> RN
    P --> RN
    EP --> RN
    UK --> RN
```

Sources: [shared.sh:26-184]()

---

## Python Wheel Installation

After `build.sh` runs, the wheel is written to `wheelhouse-{TARGET}/`. Install it with:

```
pip install wheelhouse-cuda/uccl-*.whl
```

For TheRock/ROCm, provide the index URL and extra:

```
pip install --extra-index-url https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu \
    wheelhouse-therock/uccl-0.0.1.post4-py3-none-manylinux_2_28_x86_64.whl[rocm]
```

The `--install` flag on `build.sh` automates this step, using `uv pip` when available in a virtual environment, falling back to `pip` otherwise.

Sources: [build.sh:397-424](), [README.md:102-103]()

### What the Wheel Contains

The `uccl` Python package is assembled by `setup.py` and includes:

| Path in wheel | Content |
|---|---|
| `uccl/lib/libnccl-net-uccl.so` | NCCL plugin for IB/RoCE |
| `uccl/lib/librccl-net-uccl.so` | RCCL plugin for IB/RoCE |
| `uccl/lib/libnccl-net-efa.so` | NCCL plugin for EFA |
| `uccl/lib/libnccl-efa.so` | Custom NCCL for EFA |
| `uccl/lib/libuccl_p2p.so` | P2P C shared library |
| `uccl/p2p*.abi3.so` | P2P Python extension (nanobind) |
| `uccl/ep*.abi3.so` | EP Python extension (pybind11) |
| `uccl/collective.py` | CollectiveContext Python API |
| `uccl/utils.py` | Shared utilities |

The `uccl/__init__.py` exposes path helpers: `nccl_plugin_path()`, `rccl_plugin_path()`, `efa_plugin_path()`, `efa_nccl_path()`. It also detects EFA at import time via `has_efa()`, which checks `/sys/class/infiniband/` for `rdmap*` entries.

Sources: [setup.py:33-64](), [uccl/__init__.py:1-53]()

---

## Platform-Specific Notes

### CUDA (NVIDIA)

- Default target is CUDA 12.8 from `nvidia/cuda:12.8.0-devel-ubuntu22.04`.
- Use `cuda13` as target for CUDA 13.0.
- The `ep` build auto-detects compute capability via `nvidia-smi --query-gpu=compute_cap`. Override with `TORCH_CUDA_ARCH_LIST=9.0`.
- GH200 (ARM64) is detected by checking both `uname -m == aarch64` and `GH200` in `nvidia-smi` GPU name output. The `docker/Dockerfile.gh` handles this case.

Sources: [build.sh:65-100](), [ep/setup.py:126-165](), [docker/Dockerfile.gh:49]()

### ROCm (AMD)

- Default is ROCm 7.1 from `rocm/dev-ubuntu-22.04`.
- Use `rocm6` as target for ROCm 6.4.3.
- AMD GPU architecture is auto-detected via `amd-smi static --asic --json`. Override with `TORCH_CUDA_ARCH_LIST=gfx942`.
- `build_rccl_nccl_header()` runs first to generate `nccl.h` from the RCCL source tree, since ROCm does not ship `nccl.h` separately.
- ROCm builds skip EFA (`ccl_efa`) and ARM64 builds.

Sources: [build.sh:73-100](), [shared.sh:16-24](), [docker/Dockerfile.rocm:39-40]()

### TheRock (AMD)

TheRock is AMD's Python-packaged ROCm distribution. Key differences from standard ROCm:

- Uses a manylinux base image rather than `rocm/dev-ubuntu-22.04`.
- Installs `rocm[libraries,devel]` from the provided PyPI index.
- At build time, emits `uccl/_rocm_init.py` that calls `rocm_sdk.initialize_process()` at import time.
- Wheel filename gets a `+rocm{version}` local version suffix.

Sources: [build.sh:255-320](), [uccl/__init__.py:4-10]()

### AWS EFA

EFA builds apply when `/sys/class/infiniband/` contains `rdmap*` devices, or when `docker/Dockerfile.efa` is used explicitly.

- The EFA installer is fetched during Docker image build: `aws-efa-installer-1.42.0` installs to `/opt/amazon/efa`.
- `ep/setup.py` detects EFA via `EFA_HOME` (default `/opt/amazon/efa`) and adds `-DEFA` flags.
- `ep/Makefile` does the same via `EFA_HOME` and `EFA_CFLAGS`/`EFA_LDFLAGS`.
- On EFA hosts at runtime, `uccl/__init__.py` skips loading `p2p` and `collective` modules (EFA uses its own plugin path).

Sources: [docker/Dockerfile.efa:46-57](), [ep/setup.py:117-179](), [ep/Makefile:5-13](), [uccl/__init__.py:12-27]()

---

## EP-Specific Installation

UCCL-EP can be built independently of the full wheel build, which is useful on bare-metal machines with CUDA or ROCm already installed.

### Step 1: Install dependencies

```
cd ep
./install_deps.sh
```

`install_deps.sh` detects the CUDA version via `nvcc --version`, constructs the correct PyTorch wheel suffix (e.g., `cu128`), installs PyTorch, and configures `CXXFLAGS`/`LDFLAGS` to point at the Torch headers and libraries.

Sources: [ep/install_deps.sh:1-84]()

### Step 2: Build and install

```
cd ep
python setup.py install
```

Or via `make`:

```
make -j install
```

The `CustomInstall` class in `ep/setup.py` copies the resulting `.so` into the `uccl` package directory in `site-packages`.

Sources: [ep/setup.py:17-43](), [ep/Makefile:114-117]()

### Step 3: Verify

```
python -c "import torch; import uccl.ep"
```

Common issues:
- `CUDA error: invalid device function` — GPU arch detection failed. Set `TORCH_CUDA_ARCH_LIST=<arch>` explicitly (e.g., `gfx942` for MI300X, `9.0` for H100).
- Compilation errors — run `python setup.py clean` then rebuild.

Sources: [ep/README.md:44-51]()

---

## Setting Environment Variables After Installation

Once installed, set the appropriate environment variable before launching PyTorch applications:

| Scenario | Variable and Value |
|---|---|
| NCCL over IB/RoCE (NVIDIA, x86 or GH200) | `NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.nccl_plugin_path())")` |
| RCCL over IB/RoCE (AMD, x86) | `NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.rccl_plugin_path())")` |
| NCCL over EFA (p4d, p4de) | `LD_PRELOAD=$(python -c "import uccl; print(uccl.efa_nccl_path())")` and `NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.efa_plugin_path())")` |

Sources: [README.md:105-117](), [uccl/__init__.py:32-53]()

For EP-specific environment variables (`UCCL_IB_GID_INDEX`, `UCCL_SOCKET_IFNAME`, flow control knobs), see Configuration and Tuning ([7.3](#7.3)).

---

## Rocky Linux 9 Compatibility

The build container runs Ubuntu 22.04 (glibc 2.35). Rocky Linux 9.x ships glibc 2.34. `build.sh` detects Rocky Linux and retags the wheel to `manylinux_2_34` after `auditwheel repair` by setting `UCCL_WHEEL_PLAT`. This does not rebuild against 2.34 symbols — it only changes the platform tag.

Sources: [build.sh:103-119](), [build.sh:330-353]()

---

# Page: UCCL-Collective

# UCCL-Collective

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



## Purpose and Scope

UCCL-Collective is a high-performance collective communication library that serves as a drop-in replacement for NCCL (NVIDIA Collective Communications Library) and RCCL (ROCm Collective Communications Library). It provides transparent integration with existing PyTorch applications through the NCCL/RCCL plugin mechanism, requiring no application code changes.

This document covers the architecture, plugin integration mechanism, and transport backend overview of UCCL-Collective. For detailed information about specific transport implementations, see:
- RDMA/InfiniBand backend: [#2.2](#2.2)
- AWS EFA backend: [#2.3](#2.3)
- AF_XDP backend for non-RDMA NICs: [#2.4](#2.4)

For point-to-point communication APIs, see [UCCL-P2P Engine](#3). For expert-parallel communication for MoE models, see [UCCL-EP Expert Parallelism](#4).

**Sources**: [README.md:17-48]()

## Architecture Overview

UCCL-Collective consists of three primary components: a plugin layer that interfaces with NCCL/RCCL, a collective operations layer, and multiple transport backends. Each transport backend is optimized for specific network hardware and deployment environments.

```mermaid
graph TB
    subgraph "Application Layer"
        PYTORCH["PyTorch Application<br/>(torch.distributed)"]
    end
    
    subgraph "NCCL/RCCL Layer"
        NCCL_LIB["NCCL/RCCL Library<br/>(libnccl.so / librccl.so)"]
        PLUGIN_API["NCCL Plugin API<br/>(ncclNet_v* interface)"]
    end
    
    subgraph "UCCL-Collective Plugin Layer"
        NCCL_PLUGIN["libnccl-net-uccl.so"]
        RCCL_PLUGIN["librccl-net-uccl.so"]
        EFA_PLUGIN["libnccl-net-efa.so"]
    end
    
    subgraph "Collective Operations"
        ALLREDUCE["AllReduce"]
        ALLGATHER["AllGather"]
        REDUCESCATTER["ReduceScatter"]
        BROADCAST["Broadcast"]
    end
    
    subgraph "Transport Backends"
        RDMA_BACKEND["RDMA Transport<br/>collective/rdma/<br/>IB/RoCE NICs"]
        EFA_BACKEND["EFA Transport<br/>collective/efa/<br/>AWS EFA NICs"]
        AFXDP_BACKEND["AF_XDP Transport<br/>collective/afxdp/<br/>ENA/VirtIO NICs"]
    end
    
    subgraph "Hardware Layer"
        IB_NIC["InfiniBand/RoCE NICs<br/>(CX7, Thor2)"]
        EFA_NIC["AWS EFA NICs<br/>(p4d, p4de, p5)"]
        ENA_NIC["Non-RDMA NICs<br/>(ENA, VirtIO)"]
    end
    
    PYTORCH --> NCCL_LIB
    NCCL_LIB --> PLUGIN_API
    PLUGIN_API --> NCCL_PLUGIN
    PLUGIN_API --> RCCL_PLUGIN
    PLUGIN_API --> EFA_PLUGIN
    
    NCCL_PLUGIN --> ALLREDUCE
    NCCL_PLUGIN --> ALLGATHER
    NCCL_PLUGIN --> REDUCESCATTER
    NCCL_PLUGIN --> BROADCAST
    
    RCCL_PLUGIN --> ALLREDUCE
    RCCL_PLUGIN --> ALLGATHER
    RCCL_PLUGIN --> REDUCESCATTER
    RCCL_PLUGIN --> BROADCAST
    
    EFA_PLUGIN --> ALLREDUCE
    EFA_PLUGIN --> ALLGATHER
    EFA_PLUGIN --> REDUCESCATTER
    EFA_PLUGIN --> BROADCAST
    
    ALLREDUCE --> RDMA_BACKEND
    ALLREDUCE --> EFA_BACKEND
    ALLREDUCE --> AFXDP_BACKEND
    
    ALLGATHER --> RDMA_BACKEND
    ALLGATHER --> EFA_BACKEND
    ALLGATHER --> AFXDP_BACKEND
    
    REDUCESCATTER --> RDMA_BACKEND
    REDUCESCATTER --> EFA_BACKEND
    REDUCESCATTER --> AFXDP_BACKEND
    
    BROADCAST --> RDMA_BACKEND
    BROADCAST --> EFA_BACKEND
    BROADCAST --> AFXDP_BACKEND
    
    RDMA_BACKEND --> IB_NIC
    EFA_BACKEND --> EFA_NIC
    AFXDP_BACKEND --> ENA_NIC
```

**Sources**: [README.md:25-48](), [build.sh:53-115](), [uccl/__init__.py:33-54]()

## Plugin Integration Mechanism

UCCL-Collective integrates with NCCL/RCCL through the plugin API, which allows custom network transport implementations to be loaded at runtime. Applications use UCCL-Collective by setting environment variables that point to the appropriate plugin shared library.

### Plugin Libraries

UCCL-Collective provides three plugin shared libraries:

| Plugin Library | Target API | GPU Platform | Network Type | Build Output |
|----------------|------------|--------------|--------------|--------------|
| `libnccl-net-uccl.so` | NCCL | NVIDIA CUDA | RDMA (IB/RoCE) | [collective/rdma/]() |
| `librccl-net-uccl.so` | RCCL | AMD ROCm | RDMA (IB/RoCE) | [collective/rdma/]() |
| `libnccl-net-efa.so` | NCCL | NVIDIA CUDA | AWS EFA | [collective/efa/]() |

### Environment Variable Configuration

The plugin mechanism is activated through environment variables:

```bash
# NCCL over IB/RoCE on x86 or GH200 ARM hosts
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`

# RCCL over IB/RoCE on x86 hosts  
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.rccl_plugin_path())"`

# NCCL over AWS EFA NICs (p4d and p4de)
LD_PRELOAD=`python -c "import uccl; print(uccl.efa_nccl_path())"`
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.efa_plugin_path())"`
```

The Python helper functions return absolute paths to the installed plugin libraries:

```python
# uccl/__init__.py implementation
def nccl_plugin_path():
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    return os.path.join(lib_dir, "libnccl-net-uccl.so")

def rccl_plugin_path():
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    return os.path.join(lib_dir, "librccl-net-uccl.so")
```

**Sources**: [README.md:103-114](), [uccl/__init__.py:33-54]()

## Transport Backend Architecture

UCCL-Collective supports three transport backends, each optimized for different network hardware and deployment scenarios. The build system compiles the appropriate backend based on the target platform.

### Transport Backend Selection Matrix

| Backend | Network Hardware | Use Case | Platform Support |
|---------|------------------|----------|------------------|
| RDMA | InfiniBand, RoCE | High-performance clusters with RDMA NICs | CUDA (x86, ARM), ROCm (x86) |
| EFA | AWS EFA | AWS p4d/p4de instances | CUDA (x86 only) |
| AF_XDP | ENA, VirtIO | Cloud instances without RDMA | CUDA, ROCm |

### Build System Integration

The build system provides modular compilation of transport backends through the `build.sh` script:

```bash
# Build all backends
./build.sh [cuda|rocm|therock] all

# Build specific backend
./build.sh cuda ccl_rdma     # RDMA backend only
./build.sh cuda ccl_efa      # EFA backend only
```

```mermaid
graph LR
    subgraph "Build Script (build.sh)"
        DETECT["Platform Detection<br/>TARGET=[cuda|rocm|therock]"]
        BUILD_TYPE["Build Type Selection<br/>BUILD_TYPE=[all|ccl_rdma|ccl_efa]"]
    end
    
    subgraph "Build Functions"
        BUILD_RDMA["build_ccl_rdma()<br/>lines 53-90"]
        BUILD_EFA["build_ccl_efa()<br/>lines 92-115"]
    end
    
    subgraph "Build Outputs"
        RDMA_SO["libnccl-net-uccl.so<br/>librccl-net-uccl.so"]
        EFA_SO["libnccl-net-efa.so"]
        EFA_NCCL["libnccl-efa.so<br/>(custom NCCL)"]
    end
    
    subgraph "Installation (setup.py)"
        PACKAGE_DATA["package_data<br/>lib/*.so"]
        WHEEL["uccl-*.whl"]
    end
    
    DETECT --> BUILD_TYPE
    BUILD_TYPE --> BUILD_RDMA
    BUILD_TYPE --> BUILD_EFA
    
    BUILD_RDMA --> RDMA_SO
    BUILD_EFA --> EFA_SO
    BUILD_EFA --> EFA_NCCL
    
    RDMA_SO --> PACKAGE_DATA
    EFA_SO --> PACKAGE_DATA
    EFA_NCCL --> PACKAGE_DATA
    PACKAGE_DATA --> WHEEL
```

**Sources**: [build.sh:1-437](), [setup.py:18-48]()

### RDMA Backend Overview

The RDMA backend implements packet spraying across multiple network paths to avoid single-path congestion. It supports both NVIDIA (NCCL) and AMD (RCCL) GPUs with InfiniBand and RoCE NICs.

**Key Features**:
- Packet spraying with up to 256 paths
- Latency-based and receiver-driven congestion control
- Selective repeat loss recovery
- Support for Broadcom Thor-2 and NVIDIA ConnectX-7 NICs

**Build Process**:
- CUDA target: `make -j$(nproc)` in [collective/rdma/]()
- ROCm target: `make -j$(nproc) -f Makefile.rocm` in [collective/rdma/]()

**Sources**: [README.md:39-47](), [build.sh:53-90]()

### EFA Backend Overview

The EFA backend is optimized for AWS EFA NICs on p4d and p4de instances. It requires a custom NCCL build with scatter-gather support.

**Key Features**:
- Optimized for AWS network topology
- Custom NCCL with scatter-gather operations
- Support for p4d.24xlarge, p4de.24xlarge instances

**Build Process**:
```bash
# Build EFA plugin
cd collective/efa && make clean && make -j$(nproc)

# Build custom NCCL with scatter-gather support
cd thirdparty/nccl-sg
make src.build -j$(nproc) NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90"
```

**Build Outputs**:
- `libnccl-net-efa.so` - EFA plugin
- `libnccl-efa.so` - Custom NCCL library

**Sources**: [build.sh:92-115](), [README.md:156]()

### AF_XDP Backend Overview

The AF_XDP backend uses eBPF-based packet filtering for non-RDMA NICs such as AWS ENA and IBM VirtIO. This enables efficient collective operations on cloud instances without specialized RDMA hardware.

**Key Features**:
- eBPF packet filtering for fast packet processing
- Support for AWS ENA NICs (g4dn instances)
- Support for IBM VirtIO NICs
- Optimized for legacy Ethernet networks

**Target Use Cases**:
- AWS g4dn.8xlarge instances (1x50G ENA + 1xT4 GPU)
- Public cloud deployments without RDMA support

**Sources**: [README.md:159]()

## Performance Characteristics

UCCL-Collective demonstrates significant performance improvements over NCCL/RCCL in various deployment scenarios:

### AllReduce Performance

| Configuration | Hardware | UCCL-Collective Speedup |
|---------------|----------|------------------------|
| 6 HGX servers (2 racks) | 8x400G CX-7 RoCE, 8xH100 | Up to **2.5x** vs NCCL |
| 2 AWS g4dn.8xlarge | 1x50G ENA, 1xT4 | Up to **3.7x** vs NCCL |

The performance improvements come from:
1. **Packet spraying**: Leveraging multiple network paths (up to 256) to avoid congestion
2. **Advanced congestion control**: Latency-based and receiver-driven mechanisms
3. **Efficient loss recovery**: Selective repeat instead of full retransmission
4. **Extensible software transport**: Fast implementation without hardware limitations

**Sources**: [README.md:30-34]()

## Build and Deployment Workflow

The complete build and deployment workflow for UCCL-Collective involves platform detection, Docker-based compilation, and Python wheel packaging.

```mermaid
graph TB
    subgraph "Build Phase"
        START["./build.sh cuda ccl_rdma"]
        DOCKER_BUILD["Build Docker Image<br/>uccl-builder-cuda"]
        COMPILE["Compile in Container<br/>make -j in collective/rdma/"]
        COPY["Copy .so to uccl/lib/"]
    end
    
    subgraph "Package Phase"
        PY_BUILD["python -m build"]
        AUDIT["auditwheel repair<br/>Bundle dependencies"]
        WHEEL_OUT["wheelhouse-cuda/<br/>uccl-*.whl"]
    end
    
    subgraph "Install Phase"
        PIP_INSTALL["pip install uccl-*.whl"]
        LIB_LOCATION["~/.local/lib/python*/site-packages/uccl/lib/"]
        PLUGIN_SO["libnccl-net-uccl.so<br/>librccl-net-uccl.so"]
    end
    
    subgraph "Runtime Phase"
        SET_ENV["NCCL_NET_PLUGIN=<br/>uccl.nccl_plugin_path()"]
        RUN_APP["Run PyTorch application<br/>torch.distributed"]
    end
    
    START --> DOCKER_BUILD
    DOCKER_BUILD --> COMPILE
    COMPILE --> COPY
    COPY --> PY_BUILD
    PY_BUILD --> AUDIT
    AUDIT --> WHEEL_OUT
    WHEEL_OUT --> PIP_INSTALL
    PIP_INSTALL --> LIB_LOCATION
    LIB_LOCATION --> PLUGIN_SO
    PLUGIN_SO --> SET_ENV
    SET_ENV --> RUN_APP
```

### Platform-Specific Build Commands

The build system automatically detects the platform and compiles appropriate backends:

```bash
# CUDA with RDMA backend
./build.sh cuda ccl_rdma

# ROCm with RDMA backend  
./build.sh rocm ccl_rdma

# CUDA with EFA backend (AWS only)
./build.sh cuda ccl_efa

# Build all backends
./build.sh cuda all
```

### Docker-Based Compilation

All compilation occurs inside Docker containers to ensure reproducibility:

- **uccl-builder-cuda**: CUDA 12.3+ toolchain for NVIDIA GPUs
- **uccl-builder-rocm**: ROCm 7.0+ toolchain for AMD GPUs
- **uccl-builder-gh**: CUDA on ARM for Grace Hopper systems
- **uccl-builder-efa**: CUDA with EFA support for AWS
- **uccl-builder-therock**: manylinux + TheRock ROCm packaging

**Sources**: [build.sh:194-268](), [build_and_install.sh:1-40]()

## Integration with NCCL/RCCL API

UCCL-Collective implements the NCCL plugin interface (`ncclNet_v*`), providing transparent integration with existing NCCL/RCCL-based applications. No application code changes are required.

### Supported Collective Operations

| Operation | NCCL Function | Description |
|-----------|---------------|-------------|
| AllReduce | `ncclAllReduce` | Reduce across all ranks, broadcast result |
| AllGather | `ncclAllGather` | Gather data from all ranks to all ranks |
| ReduceScatter | `ncclReduceScatter` | Reduce and scatter result chunks |
| Broadcast | `ncclBroadcast` | Send data from one rank to all ranks |

### Plugin Interface Implementation

The plugin libraries expose the NCCL network plugin API, which NCCL/RCCL loads dynamically at runtime:

```mermaid
graph LR
    subgraph "NCCL/RCCL Runtime"
        INIT["ncclCommInitRank()"]
        LOAD_PLUGIN["Load NCCL_NET_PLUGIN<br/>.so file"]
        PLUGIN_INIT["ncclNetPlugin_v*_init()"]
    end
    
    subgraph "UCCL Plugin (libnccl-net-uccl.so)"
        NET_INIT["ncclNet_v*_init()"]
        NET_DEVICES["ncclNetDevices()"]
        NET_LISTEN["ncclNetListen()"]
        NET_CONNECT["ncclNetConnect()"]
        NET_SEND["ncclNetIsend()"]
        NET_RECV["ncclNetIrecv()"]
    end
    
    subgraph "Transport Implementation"
        RDMA_SEND["RDMA post_send()"]
        RDMA_RECV["RDMA post_recv()"]
        PACKET_SPRAY["Packet Spraying<br/>256 paths"]
        CONGESTION["Congestion Control"]
    end
    
    INIT --> LOAD_PLUGIN
    LOAD_PLUGIN --> PLUGIN_INIT
    PLUGIN_INIT --> NET_INIT
    NET_INIT --> NET_DEVICES
    NET_DEVICES --> NET_LISTEN
    NET_LISTEN --> NET_CONNECT
    NET_CONNECT --> NET_SEND
    NET_CONNECT --> NET_RECV
    
    NET_SEND --> RDMA_SEND
    NET_RECV --> RDMA_RECV
    RDMA_SEND --> PACKET_SPRAY
    RDMA_RECV --> PACKET_SPRAY
    PACKET_SPRAY --> CONGESTION
```

**Sources**: [README.md:103-116]()

## Configuration and Tuning

UCCL-Collective behavior is controlled through environment variables that configure transport parameters, topology detection, and performance tuning.

### Common Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `NCCL_NET_PLUGIN` | Path to plugin .so | - | `/path/to/libnccl-net-uccl.so` |
| `LD_PRELOAD` | Preload custom NCCL (EFA only) | - | `/path/to/libnccl-efa.so` |
| `NCCL_DEBUG` | NCCL debug level | `WARN` | `INFO`, `TRACE` |
| `NCCL_IB_DISABLE` | Disable built-in IB transport | `0` | `1` |

For detailed configuration of specific backends, see:
- RDMA backend tuning: [#2.2](#2.2)
- EFA backend configuration: [#2.3](#2.3)
- AF_XDP backend setup: [#2.4](#2.4)

For integration patterns with PyTorch applications, see [PyTorch Integration Patterns](#6.2).

**Sources**: [README.md:103-116]()

## Code Organization

The UCCL-Collective codebase is organized into transport-specific directories under `collective/`:

```
collective/
├── rdma/              # RDMA transport for IB/RoCE
│   ├── Makefile       # CUDA build
│   ├── Makefile.rocm  # ROCm build
│   └── Makefile.therock # TheRock build
├── efa/               # EFA transport for AWS
│   └── Makefile
└── afxdp/             # AF_XDP transport for non-RDMA
    └── Makefile
```

Build outputs are packaged into the `uccl` Python module:

```
uccl/
├── __init__.py        # Plugin path helpers
└── lib/
    ├── libnccl-net-uccl.so    # NCCL plugin (RDMA)
    ├── librccl-net-uccl.so    # RCCL plugin (RDMA)
    ├── libnccl-net-efa.so     # NCCL plugin (EFA)
    └── libnccl-efa.so         # Custom NCCL (EFA)
```

**Sources**: [setup.py:26-37](), [build.sh:53-115]()

---

# Page: Collective Operations and Plugin Architecture

# Collective Operations and Plugin Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [scripts/node_ips/amd.txt](scripts/node_ips/amd.txt)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



## Purpose and Scope

This page covers how UCCL-collective integrates with the NCCL and RCCL runtime through the net plugin interface, which collective operations are exposed, and the mechanism by which plugin libraries are located and loaded at runtime. It also documents the Python path-helper API and EFA host detection logic.

For RDMA/InfiniBand backend internals, see [2.2](#2.2). For EFA-specific configuration, see [2.3](#2.3). For AF_XDP, see [2.4](#2.4). For step-by-step integration instructions in a live application, see [7.1](#7.1).

---

## NCCL/RCCL Net Plugin Interface

Both NCCL (NVIDIA) and RCCL (AMD) expose a _net plugin_ interface: a dynamically-loaded shared library that NCCL calls for all actual data transfer. When `NCCL_NET_PLUGIN` is set, NCCL bypasses its built-in transport and delegates send/receive operations to the named library. UCCL-collective uses this mechanism exclusively — no changes to application code are needed.

UCCL produces four distinct shared library files, placed in `uccl/lib/` inside the installed Python package:

| Library file | Transport backend | GPU stack |
|---|---|---|
| `libnccl-net-uccl.so` | InfiniBand / RoCE | CUDA (NVIDIA) |
| `librccl-net-uccl.so` | InfiniBand / RoCE | ROCm (AMD) |
| `libnccl-net-efa.so` | AWS EFA | CUDA |
| `libnccl-efa.so` | Modified NCCL for EFA (`thirdparty/nccl-sg`) | CUDA |

These files are copied into `uccl/lib/` by `build_ccl_rdma()` and `build_ccl_efa()` in `shared.sh`.

Sources: [shared.sh:26-97](), [uccl/__init__.py:32-53](), [collective/rdma/README.md:1-30](), [collective/efa/README.md:74-83]()

---

## Plugin Loading

**Plugin loading flow (diagram):**

```mermaid
flowchart TD
    A["Application\n(PyTorch / nccl-tests)"]
    B["NCCL / RCCL runtime"]
    C["NCCL_NET_PLUGIN\nenvironment variable"]
    D["libnccl-net-uccl.so\n(collective/rdma)"]
    E["librccl-net-uccl.so\n(collective/rdma Makefile.rocm)"]
    F["libnccl-net-efa.so\n(collective/efa)"]
    G["LD_PRELOAD\nlibnccl-efa.so\n(thirdparty/nccl-sg)"]
    H["IB / RoCE NIC"]
    I["AWS EFA NIC"]

    A --> B
    B --> C
    C -->|"CUDA + IB/RoCE"| D
    C -->|"ROCm + IB/RoCE"| E
    C -->|"CUDA + EFA"| F
    F --> G
    D --> H
    E --> H
    F --> I
    G --> I
```

Sources: [README.md:105-116](), [collective/efa/README.md:74-83]()

### Loading for IB/RoCE (CUDA)

```bash
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`
```

### Loading for IB/RoCE (ROCm)

```bash
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.rccl_plugin_path())"`
```

### Loading for AWS EFA

The EFA backend requires two libraries: a patched NCCL (`libnccl-efa.so`) that understands EFA QP semantics, and the actual plugin (`libnccl-net-efa.so`).

```bash
LD_PRELOAD=`python -c "import uccl; print(uccl.efa_nccl_path())"`
NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.efa_plugin_path())"`
NCCL_PROTO=Simple
```

> `NCCL_PROTO=Simple` is required for EFA. The `LL` and `LL128` protocols are not yet supported.

Sources: [README.md:105-116](), [collective/efa/README.md:74-83]()

---

## Python Path Helper API

The `uccl` package exposes four functions in `uccl/__init__.py` that return the absolute path to each plugin shared library. All four resolve paths relative to the installed package location using `os.path.dirname(os.path.abspath(__file__))`.

**Python API to library file mapping (diagram):**

```mermaid
flowchart LR
    subgraph "uccl/__init__.py"
        FN1["nccl_plugin_path()"]
        FN2["rccl_plugin_path()"]
        FN3["efa_plugin_path()"]
        FN4["efa_nccl_path()"]
    end

    subgraph "uccl/lib/"
        SO1["libnccl-net-uccl.so"]
        SO2["librccl-net-uccl.so"]
        SO3["libnccl-net-efa.so"]
        SO4["libnccl-efa.so"]
    end

    FN1 --> SO1
    FN2 --> SO2
    FN3 --> SO3
    FN4 --> SO4
```

| Function | Returns | Built by |
|---|---|---|
| `nccl_plugin_path()` | `uccl/lib/libnccl-net-uccl.so` | `build_ccl_rdma()` in `shared.sh` |
| `rccl_plugin_path()` | `uccl/lib/librccl-net-uccl.so` | `build_ccl_rdma()` in `shared.sh` |
| `efa_plugin_path()` | `uccl/lib/libnccl-net-efa.so` | `build_ccl_efa()` in `shared.sh` |
| `efa_nccl_path()` | `uccl/lib/libnccl-efa.so` | `build_ccl_efa()` in `shared.sh` |

Sources: [uccl/__init__.py:32-53](), [shared.sh:26-97]()

---

## EFA Host Detection

At import time, `uccl/__init__.py` calls `has_efa()`, which inspects `/sys/class/infiniband/` and returns `True` if any subdirectory name contains the string `rdmap` (the naming convention for EFA RDMA interfaces).

```python
# uccl/__init__.py
def has_efa():
    infiniband = Path("/sys/class/infiniband/")
    try:
        if infiniband.is_dir():
            return any("rdmap" in child.name for child in infiniband.iterdir())
        return False
    except (OSError, PermissionError):
        return False
is_efa = has_efa()
```

The result is stored in the module-level `is_efa` boolean. When `is_efa` is `True`, the automatic imports of `uccl.p2p` and `uccl.collective` are skipped [uccl/__init__.py:22-27](), because EFA hosts require the full EFA setup path and the P2P extension is not loaded in that configuration.

Sources: [uccl/__init__.py:12-27]()

---

## Supported Collective Operations

UCCL-collective acts as a transport-layer replacement for the NCCL/RCCL plugin interface. The collective algorithm selection (ring-allreduce, tree-allreduce, etc.) remains NCCL's responsibility. UCCL handles only the actual data movement between ranks.

Operations exercising the UCCL transport include:

| Operation | Notes |
|---|---|
| `AllReduce` | Primary target; validated via `run_nccl_test.sh` / `run_rccl_test.sh` |
| `AllToAll` | Tested via nccl-tests with the `--op alltoall` flag |
| Other NCCL collectives | Pass through transparently as NCCL controls algorithm selection |

Performance highlights from the README (no code changes required in the application):

- **2.5×** improvement over NCCL for AllReduce on 6× HGX H100 servers with 8×400G RoCE NICs
- **3.7×** improvement over NCCL on 2× AWS `g4dn.8xlarge` with 50G ENA NICs

Sources: [README.md:29-48](), [collective/rdma/README.md:23-28]()

---

## Transport Layer Design

UCCL-collective's transport design differs from the stock NCCL transport in a few key ways:

**Packet spraying.** Where NCCL uses one or a small number of network paths for a large transfer, UCCL fans traffic across many QPs simultaneously. This avoids concentrating load on a single congested path.

| Feature | Default value (NVIDIA) | Default value (AMD) |
|---|---|---|
| Paths per engine (`UCCL_PORT_ENTROPY`) | 32 | 256 |
| Engines per device (`UCCL_NUM_ENGINES`) | 4 | 1 |
| Max chunk per WQE (`UCCL_CHUNK_SIZE_KB`) | 64 KB | 128 KB |
| Connection mode (`UCCL_RCMODE`) | 0 (UC) | 1 (RC for Broadcom) |

Additional transport capabilities:
- Latency-based and receiver-driven congestion control
- Selective repeat for loss recovery
- Both Unreliable Connection (UC) and Reliable Connection (RC) modes

Sources: [collective/rdma/README.md:162-181]()

---

## Build Artifacts and Source Directories

**How plugin .so files are built and placed (diagram):**

```mermaid
flowchart TD
    subgraph "shared.sh"
        B1["build_ccl_rdma()"]
        B2["build_ccl_efa()"]
    end

    subgraph "Source directories"
        S1["collective/rdma/\n(Makefile / Makefile.rocm / Makefile.therock)"]
        S2["collective/efa/\n(Makefile)"]
        S3["thirdparty/nccl-sg/\n(patched NCCL for EFA)"]
    end

    subgraph "uccl/lib/ (installed package)"
        O1["libnccl-net-uccl.so"]
        O2["librccl-net-uccl.so"]
        O3["libnccl-net-efa.so"]
        O4["libnccl-efa.so"]
    end

    B1 --> S1
    B2 --> S2
    B2 --> S3

    S1 -->|"CUDA build"| O1
    S1 -->|"ROCm build"| O2
    S2 --> O3
    S3 --> O4
```

The `build_ccl_rdma()` function in `shared.sh` selects the correct Makefile variant based on `$TARGET`:

- `cuda*` → `collective/rdma/Makefile`, produces `libnccl-net-uccl.so`
- `rocm*` → `collective/rdma/Makefile.rocm`, produces `librccl-net-uccl.so`
- `therock` → `collective/rdma/Makefile.therock`, produces `librccl-net-uccl.so`

The `build_ccl_efa()` function additionally builds `thirdparty/nccl-sg` (a patched NCCL) and copies its `libnccl.so` as `libnccl-efa.so` [shared.sh:69-97]().

Sources: [shared.sh:26-97](), [build.sh:272-288]()

---

## Key Environment Variables

These variables are read by the UCCL plugin at startup via the `UCCL_PARAM()` macro in the collective/rdma C++ source. They do not require recompilation.

| Variable | Description | Default |
|---|---|---|
| `NCCL_NET_PLUGIN` | Path to the UCCL plugin `.so`; set by the user | — |
| `UCCL_IB_HCA` | Restrict to specific IB device names | auto-detect |
| `UCCL_SOCKET_IFNAME` | Control NIC for bootstrapping | auto-detect |
| `UCCL_NUM_ENGINES` | Engines per GPU device | 4 (NVIDIA) / 1 (AMD) |
| `UCCL_PORT_ENTROPY` | QP paths per engine (packet spraying width) | 32 (NVIDIA) / 256 (AMD) |
| `UCCL_CHUNK_SIZE_KB` | Max data per work queue entry | 64 (NVIDIA) / 128 (AMD) |
| `UCCL_RCMODE` | Use RC QPs instead of UC | 1 (Broadcom), 0 (others) |
| `UCCL_PIN_TO_NUMA` | Pin proxy threads to GPU-local NUMA node | 1 |
| `NCCL_PROTO` | NCCL protocol (EFA requires `Simple`) | — |

For `UCCL_IB_GID_INDEX` used in EP and P2P contexts, see [7.3](#7.3).

Sources: [collective/rdma/README.md:162-181](), [collective/efa/README.md:74-83]()

---

# Page: RDMA/InfiniBand Backend

# RDMA/InfiniBand Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [p2p/rdma/providers/efa/rdma_channel_impl_efa.cc](p2p/rdma/providers/efa/rdma_channel_impl_efa.cc)
- [p2p/rdma/providers/efa/rdma_device_selection_efa.h](p2p/rdma/providers/efa/rdma_device_selection_efa.h)
- [p2p/rdma/providers/ib/rdma_channel_impl_ib.cc](p2p/rdma/providers/ib/rdma_channel_impl_ib.cc)
- [p2p/rdma/providers/ib/rdma_device_selection_ib.h](p2p/rdma/providers/ib/rdma_device_selection_ib.h)
- [p2p/rdma/rdma_channel.h](p2p/rdma/rdma_channel.h)
- [p2p/rdma/rdma_channel_group.h](p2p/rdma/rdma_channel_group.h)
- [p2p/rdma/rdma_channel_impl.h](p2p/rdma/rdma_channel_impl.h)
- [p2p/rdma/rdma_context.h](p2p/rdma/rdma_context.h)
- [p2p/rdma/rdma_device.h](p2p/rdma/rdma_device.h)
- [p2p/rdma/tests/Makefile](p2p/rdma/tests/Makefile)
- [scripts/node_ips/amd.txt](scripts/node_ips/amd.txt)

</details>



## Purpose and Scope

This document describes the RDMA/InfiniBand transport backend for UCCL-Collective, which serves as a drop-in replacement for the default NCCL/RCCL network transports. The RDMA backend implements a software-based transport layer that provides packet spraying, advanced congestion control, and efficient loss recovery for InfiniBand and RoCE (RDMA over Converged Ethernet) networks.

For information about the collective operations API and plugin architecture, see [Collective Operations and Plugin Architecture](#2.1). For AWS EFA-specific transport, see [EFA Backend](#2.3). For non-RDMA NICs, see [AF_XDP Backend](#2.4).

## Architecture Overview

The RDMA backend implements the NCCL/RCCL plugin interface to provide transparent integration with existing PyTorch applications. Unlike the default NCCL RDMA transport which uses one or a few network paths, the UCCL RDMA backend employs software-based packet spraying across up to 256 paths to avoid single-path congestion and improve bandwidth utilization.

**RDMA Backend System Architecture**

```mermaid
graph TB
    subgraph "Application Layer"
        APP["PyTorch Application<br/>torch.distributed"]
    end
    
    subgraph "NCCL/RCCL Core"
        NCCL_CORE["NCCL/RCCL Library<br/>Collective algorithms"]
        NET_API["Network Plugin API<br/>ncclNet_v8_t"]
    end
    
    subgraph "UCCL RDMA Plugin"
        PLUGIN_INIT["Plugin Initialization<br/>ncclNetPlugin_v8()"]
        DEVICE_MGR["Device Management<br/>getDevices/getProperties"]
        CONN_MGR["Connection Management<br/>listen/connect/accept"]
        COMM_OPS["Communication Operations<br/>regMr/send/recv/irecv"]
        
        subgraph "Transport Engine"
            PKT_SPRAY["Packet Spraying Engine<br/>256-way path diversity"]
            CC_ENGINE["Congestion Control<br/>Latency-based + Receiver-driven"]
            LOSS_REC["Loss Recovery<br/>Selective repeat"]
        end
        
        subgraph "RDMA Operations"
            QP_MGR["Queue Pair Manager<br/>RC/UC/UD QPs"]
            CQ_POLL["Completion Queue Polling"]
            MR_CACHE["Memory Region Cache"]
            WR_POST["Work Request Posting<br/>Send/Recv/RDMA Write"]
        end
    end
    
    subgraph "Hardware Layer"
        IB_VERBS["libibverbs<br/>RDMA Verbs API"]
        NIC_HARDWARE["InfiniBand/RoCE NIC<br/>CX-7, Thor-2, etc."]
    end
    
    APP --> NCCL_CORE
    NCCL_CORE --> NET_API
    NET_API --> PLUGIN_INIT
    PLUGIN_INIT --> DEVICE_MGR
    PLUGIN_INIT --> CONN_MGR
    PLUGIN_INIT --> COMM_OPS
    
    COMM_OPS --> PKT_SPRAY
    COMM_OPS --> CC_ENGINE
    COMM_OPS --> LOSS_REC
    
    PKT_SPRAY --> QP_MGR
    CC_ENGINE --> CQ_POLL
    LOSS_REC --> WR_POST
    
    QP_MGR --> IB_VERBS
    CQ_POLL --> IB_VERBS
    MR_CACHE --> IB_VERBS
    WR_POST --> IB_VERBS
    
    IB_VERBS --> NIC_HARDWARE
```

Sources: [README.md:39-47](), [build.sh:53-90]()

### Plugin Architecture

The RDMA backend is built as a shared library that implements the NCCL plugin interface:
- **CUDA builds**: `libnccl-net-uccl.so` for NVIDIA GPUs
- **ROCm builds**: `librccl-net-uccl.so` for AMD GPUs

The plugin is loaded by NCCL/RCCL at runtime through the `NCCL_NET_PLUGIN` environment variable, providing a complete replacement for the default network transport without requiring application code changes.

**Plugin Build Variants**

| Target Platform | Plugin Library | Makefile | Supported NICs |
|----------------|---------------|----------|----------------|
| CUDA x86_64 | `libnccl-net-uccl.so` | `Makefile` | InfiniBand, RoCE (Broadcom, NVIDIA) |
| CUDA ARM (GH200) | `libnccl-net-uccl.so` | `Makefile` | InfiniBand, RoCE |
| ROCm x86_64 | `librccl-net-uccl.so` | `Makefile.rocm` | InfiniBand, RoCE (Broadcom) |
| TheRock (ROCm via Python) | `librccl-net-uccl.so` | `Makefile.therock` | InfiniBand, RoCE |

Sources: [build.sh:53-90](), [uccl/__init__.py:33-42](), [README.md:105-109]()

## NCCL Plugin Interface Implementation

The RDMA backend implements the `ncclNet_v8_t` plugin interface, which defines the network operations required by NCCL/RCCL:

**Plugin Interface Diagram**

```mermaid
graph LR
    subgraph "Plugin Entry Point"
        ENTRY["ncclNetPlugin_v8()"]
    end
    
    subgraph "Device Operations"
        GET_DEV["getDevices()<br/>Enumerate RDMA devices"]
        GET_PROPS["getProperties()<br/>Query device capabilities"]
    end
    
    subgraph "Connection Establishment"
        LISTEN["listen()<br/>Create listening endpoint"]
        CONNECT["connect()<br/>Initiate connection"]
        ACCEPT["accept()<br/>Accept incoming connection"]
    end
    
    subgraph "Memory Operations"
        REG_MR["regMr()<br/>Register memory region"]
        REG_MR_DMR["regMrDmaBuf()<br/>Register DMA buffer"]
        DEREG_MR["deregMr()<br/>Deregister memory"]
    end
    
    subgraph "Communication Operations"
        ISEND["isend()<br/>Async send"]
        IRECV["irecv()<br/>Async receive"]
        IFLUSH["iflush()<br/>Flush operations"]
        TEST["test()<br/>Check completion"]
    end
    
    subgraph "Collective Operations"
        COLL_INIT["collNetSupport()<br/>Query collective support"]
        COLL_REG["collRegMr()<br/>Register for collectives"]
        COLL_SENDRECV["collSend/collRecv<br/>Collective communication"]
    end
    
    ENTRY --> GET_DEV
    ENTRY --> GET_PROPS
    ENTRY --> LISTEN
    ENTRY --> CONNECT
    ENTRY --> ACCEPT
    ENTRY --> REG_MR
    ENTRY --> REG_MR_DMR
    ENTRY --> DEREG_MR
    ENTRY --> ISEND
    ENTRY --> IRECV
    ENTRY --> IFLUSH
    ENTRY --> TEST
    ENTRY --> COLL_INIT
    ENTRY --> COLL_REG
    ENTRY --> COLL_SENDRECV
```

Sources: [README.md:25-26](), [build.sh:62-70]()

### Device Enumeration and Management

The plugin discovers available RDMA devices through the `libibverbs` API and reports their capabilities to NCCL/RCCL:

- **Device Discovery**: Enumerates all InfiniBand and RoCE adapters on the system
- **Port State Checking**: Filters for active ports with ACTIVE state
- **Capability Reporting**: Reports maximum message size, memory registration capabilities, and supported queue pair types
- **Multi-Port Support**: Handles systems with multiple RDMA ports per node

### Connection Establishment

Connection establishment follows the NCCL plugin model:

1. **Listen Phase**: Receiver creates a listening endpoint with a unique identifier
2. **Connect Phase**: Sender initiates connection using the receiver's identifier
3. **Accept Phase**: Receiver accepts the connection and establishes Queue Pairs
4. **QP Exchange**: Both sides exchange Queue Pair numbers and other connection parameters

Sources: [README.md:44-47]()

## Packet Spraying Transport

The core innovation of the RDMA backend is its software-based packet spraying mechanism, which splits data across multiple network paths to avoid congestion and improve bandwidth utilization.

**Packet Spraying Architecture**

```mermaid
graph TB
    subgraph "Sender Side"
        SEND_BUF["Send Buffer<br/>Large message"]
        CHUNKER["Data Chunker<br/>Split into packets"]
        SPRAY_ENG["Spraying Engine<br/>256-way distribution"]
        
        subgraph "Queue Pairs"
            QP0["QP 0"]
            QP1["QP 1"]
            QP2["..."]
            QP255["QP 255"]
        end
    end
    
    subgraph "Network Fabric"
        PATHS["Multiple Network Paths<br/>ECMP routing"]
    end
    
    subgraph "Receiver Side"
        subgraph "Completion Queues"
            CQ0["CQ 0"]
            CQ1["CQ 1"]
            CQ2["..."]
            CQ255["CQ 255"]
        end
        
        REORDER["Reordering Engine<br/>Reassemble packets"]
        RECV_BUF["Receive Buffer<br/>Complete message"]
    end
    
    SEND_BUF --> CHUNKER
    CHUNKER --> SPRAY_ENG
    SPRAY_ENG --> QP0
    SPRAY_ENG --> QP1
    SPRAY_ENG --> QP2
    SPRAY_ENG --> QP255
    
    QP0 --> PATHS
    QP1 --> PATHS
    QP2 --> PATHS
    QP255 --> PATHS
    
    PATHS --> CQ0
    PATHS --> CQ1
    PATHS --> CQ2
    PATHS --> CQ255
    
    CQ0 --> REORDER
    CQ1 --> REORDER
    CQ2 --> REORDER
    CQ255 --> REORDER
    
    REORDER --> RECV_BUF
```

Sources: [README.md:44-47]()

### Multi-Path Benefits

Packet spraying provides several advantages over single-path RDMA transports:

**Performance Benefits**

| Feature | Single-Path RDMA | UCCL Packet Spraying |
|---------|------------------|---------------------|
| Path Diversity | 1-4 paths | Up to 256 paths |
| Congestion Avoidance | Limited | Extensive |
| Bandwidth Utilization | 60-80% | 90-95% |
| Loss Recovery | Entire flow retransmit | Selective packet retransmit |
| Latency Sensitivity | High variance | Low variance |

- **Congestion Avoidance**: By spreading traffic across many paths, the system avoids overloading any single path
- **Load Balancing**: Network switches use ECMP (Equal-Cost Multi-Path) routing to distribute packets
- **Failure Resilience**: If one path experiences congestion or packet loss, other paths continue unaffected
- **Better Utilization**: Achieves higher aggregate bandwidth by using the full network fabric

Sources: [README.md:44-47]()

### Packet Format and Sequencing

Each packet includes:
- **Sequence Number**: For reordering at the receiver
- **Message ID**: To associate packets with the correct message
- **Offset**: Position within the original message
- **Length**: Number of bytes in this packet
- **Flags**: Control information (e.g., last packet marker)

## Congestion Control

The RDMA backend implements advanced congestion control mechanisms to maintain high throughput while avoiding network congestion.

**Congestion Control Components**

```mermaid
graph TB
    subgraph "Congestion Detection"
        LAT_MON["Latency Monitor<br/>Track RTT per path"]
        LOSS_DET["Loss Detector<br/>Sequence gap detection"]
        CQ_MON["CQ Monitor<br/>Completion queue depth"]
    end
    
    subgraph "Control Algorithms"
        LAT_CC["Latency-Based CC<br/>RTT threshold adaptation"]
        RECV_CC["Receiver-Driven CC<br/>Credit-based flow control"]
        RATE_CTRL["Rate Controller<br/>Per-path rate limiting"]
    end
    
    subgraph "Actions"
        PATH_SEL["Path Selection<br/>Avoid congested paths"]
        RATE_ADJ["Rate Adjustment<br/>Reduce send rate"]
        RETRANS["Retransmission<br/>Selective repeat"]
    end
    
    LAT_MON --> LAT_CC
    LOSS_DET --> RECV_CC
    CQ_MON --> RATE_CTRL
    
    LAT_CC --> PATH_SEL
    RECV_CC --> RATE_ADJ
    RATE_CTRL --> RATE_ADJ
    
    PATH_SEL --> RETRANS
    RATE_ADJ --> RETRANS
```

Sources: [README.md:47]()

### Latency-Based Congestion Control

The system monitors round-trip time (RTT) for each network path and adjusts sending behavior:

- **RTT Measurement**: Uses RDMA completion timestamps to measure path latency
- **Baseline Tracking**: Maintains minimum RTT baseline for each path
- **Threshold Detection**: Identifies congestion when RTT exceeds baseline by configurable factor
- **Path Avoidance**: Temporarily avoids congested paths for new packets
- **Gradual Recovery**: Slowly reintroduces previously congested paths

### Receiver-Driven Flow Control

The receiver provides backpressure to prevent buffer overflow:

- **Credit System**: Receiver grants send credits to sender
- **Buffer Monitoring**: Tracks available receive buffer space
- **Credit Updates**: Sends credit updates via ACK packets
- **Send Rate Limiting**: Sender respects credit limits per path
- **Deadlock Avoidance**: Reserves credits for control messages

### Loss Recovery

Selective repeat protocol provides efficient loss recovery:

- **Gap Detection**: Receiver detects sequence number gaps
- **Selective NACK**: Requests retransmission of specific packets only
- **Fast Retransmit**: Retransmits on triple duplicate ACK
- **Timeout Retransmit**: Fallback retransmission on timer expiry
- **Out-of-Order Delivery**: Delivers in-order data to application while recovering losses

Sources: [README.md:47]()

## RDMA Operations and Memory Management

The plugin manages RDMA resources including Queue Pairs, Completion Queues, and Memory Regions.

**RDMA Resource Management**

```mermaid
graph TB
    subgraph "Memory Registration"
        APP_BUF["Application Buffer<br/>GPU or CPU memory"]
        REG_API["regMr() API"]
        MR_CACHE["Memory Region Cache<br/>LRU eviction"]
        IBV_REG["ibv_reg_mr()<br/>Pin and register"]
    end
    
    subgraph "Queue Pair Management"
        QP_POOL["QP Pool<br/>Pre-allocated QPs"]
        QP_ATTR["QP Attributes<br/>RC/UC/UD type"]
        QP_STATE["QP State Machine<br/>RESET->INIT->RTR->RTS"]
    end
    
    subgraph "Work Request Posting"
        WR_BUILDER["Work Request Builder"]
        SGE_LIST["Scatter-Gather List"]
        SEND_WR["ibv_post_send()<br/>Send/RDMA Write"]
        RECV_WR["ibv_post_recv()<br/>Receive buffers"]
    end
    
    subgraph "Completion Processing"
        CQ_POLL_LOOP["CQ Polling Loop<br/>ibv_poll_cq()"]
        WC_PROCESS["Work Completion Handler"]
        ERROR_HANDLE["Error Handler<br/>Retry/Report"]
    end
    
    APP_BUF --> REG_API
    REG_API --> MR_CACHE
    MR_CACHE --> IBV_REG
    
    IBV_REG --> QP_POOL
    QP_POOL --> QP_ATTR
    QP_ATTR --> QP_STATE
    
    QP_STATE --> WR_BUILDER
    WR_BUILDER --> SGE_LIST
    SGE_LIST --> SEND_WR
    SGE_LIST --> RECV_WR
    
    SEND_WR --> CQ_POLL_LOOP
    RECV_WR --> CQ_POLL_LOOP
    CQ_POLL_LOOP --> WC_PROCESS
    WC_PROCESS --> ERROR_HANDLE
```

Sources: [build.sh:53-90]()

### Memory Registration Strategy

Memory registration is expensive, so the plugin employs caching:

1. **Registration Cache**: Maintains cache of recently used memory registrations
2. **LRU Eviction**: Removes least recently used entries when cache is full
3. **GPU Memory Support**: Handles both GPU device memory and pinned host memory
4. **DMA-BUF Support**: Supports DMA-BUF registration for direct GPU access
5. **Deregistration**: Properly cleans up memory regions on deallocation

### Queue Pair Types

The plugin supports multiple QP types depending on requirements:

- **RC (Reliable Connection)**: For reliable, in-order delivery with flow control
- **UC (Unreliable Connection)**: For lower latency when reliability is handled in software
- **UD (Unreliable Datagram)**: For packet-spraying with software-based reliability

### Work Request Management

Efficient work request posting is critical for performance:

- **Batch Posting**: Posts multiple work requests in a single system call
- **Doorbell Optimization**: Minimizes doorbell rings to NIC
- **Inline Data**: Uses inline data for small messages to avoid memory registration
- **Scatter-Gather**: Supports non-contiguous buffer transfers
- **Work Request Pool**: Pre-allocates work request structures

Sources: [README.md:44-47]()

## Build and Configuration

The RDMA backend is built as part of the UCCL build system using Docker-based environments for reproducibility.

**Build Process for RDMA Backend**

```mermaid
graph LR
    subgraph "Source Files"
        SRC["collective/rdma/<br/>C/C++ sources"]
        MAKEFILE["Makefile variants<br/>Makefile/Makefile.rocm/Makefile.therock"]
    end
    
    subgraph "Build Environment"
        DOCKER["Docker Image<br/>uccl-builder-*"]
        TOOLCHAIN["Toolchain<br/>gcc/nvcc/hipcc"]
        DEPS["Dependencies<br/>libibverbs, CUDA/ROCm"]
    end
    
    subgraph "Compilation"
        COMPILE["Compile Sources<br/>-O3 -march=native"]
        LINK["Link Libraries<br/>libibverbs -lpthread"]
    end
    
    subgraph "Outputs"
        NCCL_SO["libnccl-net-uccl.so"]
        RCCL_SO["librccl-net-uccl.so"]
    end
    
    SRC --> COMPILE
    MAKEFILE --> COMPILE
    DOCKER --> TOOLCHAIN
    TOOLCHAIN --> COMPILE
    DEPS --> LINK
    COMPILE --> LINK
    LINK --> NCCL_SO
    LINK --> RCCL_SO
```

Sources: [build.sh:53-90](), [build.sh:193-268]()

### Build Script Usage

The `build.sh` script handles building the RDMA backend:

```bash
# Build for CUDA platform
./build.sh cuda ccl_rdma

# Build for ROCm platform
./build.sh rocm ccl_rdma

# Build for TheRock (Python-packaged ROCm)
./build.sh therock ccl_rdma
```

The `build_ccl_rdma()` function in [build.sh:53-90]() handles platform-specific compilation:

1. **CUDA Target**: Uses `Makefile` with `nvcc` compiler, produces `libnccl-net-uccl.so`
2. **ROCm Target**: Uses `Makefile.rocm` with `hipcc` compiler, produces `librccl-net-uccl.so`
3. **TheRock Target**: Uses `Makefile.therock` with TheRock SDK paths, produces `librccl-net-uccl.so`
4. **RCCL Header**: ROCm builds require building RCCL first to obtain `nccl.h` header

Sources: [build.sh:53-90]()

### Installation and Usage

After building, the plugin is packaged into the UCCL Python wheel and can be used by setting environment variables:

```bash
# For NCCL on NVIDIA GPUs
export NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.nccl_plugin_path())")

# For RCCL on AMD GPUs
export NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.rccl_plugin_path())")
```

The plugin path functions [uccl/__init__.py:33-42]() return the absolute path to the installed `.so` files in the `uccl/lib/` directory.

Sources: [uccl/__init__.py:33-42](), [README.md:105-109](), [setup.py:27-36]()

### Configuration Parameters

The RDMA backend can be tuned through environment variables:

| Variable | Purpose | Default | Range |
|----------|---------|---------|-------|
| `NCCL_IB_HCA` | Specify InfiniBand adapters | All detected | Comma-separated list |
| `NCCL_IB_DISABLE` | Disable InfiniBand | 0 | 0/1 |
| `NCCL_IB_GID_INDEX` | GID index for RoCE | 0 | 0-N |
| `NCCL_IB_QPS_PER_CONNECTION` | Queue pairs per connection | 256 | 1-256 |
| `NCCL_PROTO` | NCCL protocol | LL,LL128,Simple | Comma-separated |

These variables control the behavior of packet spraying, number of queue pairs, and protocol selection. The `NCCL_IB_QPS_PER_CONNECTION` variable directly controls the number of paths used for packet spraying.

Sources: [README.md:103-116]()

### Performance Validation

The RDMA backend provides significant performance improvements:

**Performance Comparison with Default NCCL**

Based on [README.md:30-33]():
- **6 HGX servers** (8x400G CX-7 RoCE + 8xH100): Up to **2.5x** faster for AllReduce
- **2 AWS g4dn.8xlarge** (1x50G ENA + 1xT4): Up to **3.7x** faster for AllReduce

These improvements come from:
1. Packet spraying across 256 paths vs single-path operation
2. Advanced congestion control avoiding bottlenecks
3. Efficient loss recovery with selective retransmission
4. Better network fabric utilization

Sources: [README.md:30-33]()

## Platform Support Matrix

The RDMA backend supports multiple GPU and NIC combinations:

| GPU Platform | Architecture | NIC Support | Build Target |
|-------------|--------------|-------------|--------------|
| NVIDIA CUDA | x86_64 | InfiniBand (CX-7), RoCE (Broadcom Thor-2) | `cuda` |
| NVIDIA CUDA | ARM64 (GH200) | InfiniBand, RoCE | `cuda` |
| AMD ROCm | x86_64 | InfiniBand, RoCE (Broadcom Thor-2) | `rocm` |
| AMD ROCm (TheRock) | x86_64 | InfiniBand, RoCE | `therock` |

The backend does not support:
- AMD GPUs on ARM architecture (no ROCm toolchain)
- AWS EFA NICs (use [EFA Backend](#2.3) instead)

Sources: [build.sh:31-34](), [README.md:179-185]()

---

# Page: EFA Backend

# EFA Transport

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [scripts/node_ips/amd.txt](scripts/node_ips/amd.txt)

</details>



## Purpose and Scope

The EFA Transport provides a high-performance network transport implementation for AWS Elastic Fabric Adapter (EFA) hardware within the UCCL communication library. This transport enables reliable UDP communication with custom congestion control algorithms and integrates with NCCL for collective operations in distributed machine learning workloads.

For RDMA transport implementation, see [RDMA Transport](#2.1). For AF_XDP transport, see [AF_XDP Transport](#2.3).

## Architecture Overview

The EFA Transport implements a multi-layered architecture built on AWS EFA hardware capabilities, providing application-level reliability over UDP with sophisticated congestion control.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        NCCL["NCCL Operations"]
        APP["Application Code"]
    end
    
    subgraph "EFA Transport Core"
        EP["Endpoint"]
        UE["UcclEngine"]
        UF["UcclFlow"]
        CH["Channel"]
    end
    
    subgraph "Network Layer"
        ES["EFASocket"] 
        EF["EFAFactory"]
        ED["EFADevice"]
    end
    
    subgraph "AWS Infrastructure"
        EFA_HW["EFA Hardware"]
        IBV["InfiniBand Verbs"]
    end
    
    NCCL --> EP
    APP --> EP
    EP --> UE
    UE --> UF
    UF --> CH
    UE --> ES
    ES --> EF
    EF --> ED
    ED --> IBV
    IBV --> EFA_HW
```

Sources: [efa/transport.h:834-900](), [efa/util_efa.h:276-306]()

### Component Interaction Flow

```mermaid
graph LR
    subgraph "Message Processing Pipeline"
        APP_MSG["Application Message"] --> TX_PREP["tx_prepare_messages()"]
        TX_PREP --> TX_TRACK["TXTracking::append()"]
        TX_TRACK --> TX_TRANS["transmit_pending_packets()"]
        TX_TRANS --> POST_SEND["EFASocket::post_send_wr()"]
    end
    
    subgraph "Receive Processing Pipeline" 
        POLL_RX["poll_recv_cq()"] --> RX_MSG["rx_messages()"]
        RX_MSG --> RX_CONSUME["RXTracking::consume()"]
        RX_CONSUME --> COPY_APP["try_copy_msgbuf_to_appbuf()"]
    end
```

Sources: [efa/transport.cc:602-654](), [efa/transport.cc:514-600]()

## Core Components

### Endpoint Class

The `Endpoint` class serves as the primary application-facing interface, managing multiple engines and providing connection establishment capabilities.

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `engine_vec_` | Collection of UcclEngine instances | `initialize_engine_by_gpu_idx()` |
| `channel_vec_` | Communication channels per engine | `uccl_connect()`, `uccl_accept()` |
| `ctx_pool_` | Thread-safe polling context pool | `uccl_send_async()`, `uccl_recv_async()` |

Sources: [efa/transport.h:834-900]()

### UcclEngine Class

The `UcclEngine` handles packet processing, flow management, and periodic maintenance tasks.

```mermaid
graph TB
    subgraph "UcclEngine Operations"
        RUN["run()"] --> PROC_RX["process_rx_msg()"]
        RUN --> PROC_CTL["process_ctl_reqs()"] 
        RUN --> PERIODIC["periodic_process()"]
        PERIODIC --> HANDLE_RTO["handle_rto()"]
    end
    
    subgraph "Flow Management"
        FLOW_MAP["active_flows_map_"] --> UF1["UcclFlow 1"]
        FLOW_MAP --> UF2["UcclFlow 2"] 
        FLOW_MAP --> UFN["UcclFlow N"]
    end
```

Sources: [efa/transport.h:721-823](), [efa/transport.cc:757-773]()

### UcclFlow Class

Individual connections are managed by `UcclFlow` instances, which handle reliable transmission, congestion control, and packet ordering.

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `TXTracking tx_tracking_` | Outbound packet management | Maintains unacked/unsent packet chains |
| `RXTracking rx_tracking_` | Inbound packet reassembly | Out-of-order packet handling with SACK |
| `swift::Pcb pcb_` | Protocol control block | Sequence numbers, RTO timers |
| Congestion Control | Rate limiting | `CubicCtl`, `TimelyCtl`, `EQDSCC` |

Sources: [efa/transport.h:392-715]()

## Socket and Device Management

### EFAFactory and EFADevice

The factory pattern manages EFA device initialization and socket creation with proper resource allocation.

```mermaid
graph TB
    subgraph "Device Initialization"
        INIT["EFAFactory::Init()"] --> INIT_DEV["InitDev()"]
        INIT_DEV --> IBV_OPEN["ibv_open_device()"]
        IBV_OPEN --> CREATE_PD["ibv_alloc_pd()"]
        CREATE_PD --> EFA_DEV["EFADevice"]
    end
    
    subgraph "Socket Creation"
        CREATE_SOCK["CreateSocket()"] --> EFA_SOCK["EFASocket()"]
        EFA_SOCK --> CREATE_QP["create_qp()"]
        CREATE_QP --> QP_LIST["qp_list_[kMaxSrcDstQP]"]
    end
    
    EFA_DEV --> CREATE_SOCK
```

Sources: [efa/util_efa.cc:108-258](), [efa/util_efa.cc:309-392]()

### Queue Pair Management

EFA transport uses multiple queue pairs for parallel data transmission and control traffic separation.

| QP Type | Configuration | Purpose |
|---------|---------------|---------|
| Data QPs | `qp_list_[kMaxSrcDstQP]` | Primary data transmission |
| Control QPs | `ctrl_qp_list_[kMaxSrcDstQPCtrl]` | ACK and control packets |
| Credit QPs | Via `CreditQPContext` | EQDS congestion control |

Sources: [efa/util_efa.h:315-353](), [efa/transport_config.h:95-115]()

## Flow Management and Reliability

### Transmission Tracking

The `TXTracking` class manages outbound packet state with three key pointers for efficient packet lifecycle management.

```mermaid
graph LR
    subgraph "TXTracking Packet Chain"
        OLDEST_UNACKED["oldest_unacked_msgbuf_"] --> OLDEST_UNSENT["oldest_unsent_msgbuf_"]
        OLDEST_UNSENT --> LAST["last_msgbuf_"]
    end
    
    subgraph "State Transitions"
        APPEND["append()"] --> GET_UNSENT["get_and_update_oldest_unsent()"]
        GET_UNSENT --> RECEIVE_ACKS["receive_acks()"]
    end
```

Sources: [efa/transport.h:202-289](), [efa/transport.cc:9-51]()

### Reception and Reassembly

The `RXTracking` class handles out-of-order packet delivery using sequence number comparisons and SACK bitmaps.

```mermaid
graph TB
    subgraph "Packet Reception Flow"
        RX_PKT["Received Packet"] --> SEQ_CHECK{"seqno vs expected?"}
        SEQ_CHECK -->|"In Order"| PUSH_APP["push_inorder_msgbuf_to_app()"]
        SEQ_CHECK -->|"Out of Order"| REASS_Q["reass_q_.insert()"]
        REASS_Q --> UPDATE_SACK["pcb_->sack_bitmap_bit_set()"]
        UPDATE_SACK --> PUSH_APP
    end
```

Sources: [efa/transport.cc:139-227]()

## Congestion Control Integration

### Multi-Algorithm Support

EFA transport supports multiple congestion control algorithms configured at compile time through `transport_config.h`.

| Algorithm | Type | Configuration |
|-----------|------|---------------|
| Cubic | Loss-based | `kSenderCCType = SenderCCType::kCubic` |
| Timely | Delay-based | `kSenderCCType = SenderCCType::kTimely` |
| EQDS | Receiver-driven | `kReceiverCCType = ReceiverCCType::kEQDS` |

Sources: [efa/transport_config.h:15-31]()

### EQDS Implementation

The receiver-driven EQDS congestion control uses credit-based flow control with dedicated packet types.

```mermaid
graph TB
    subgraph "EQDS Credit Flow"
        SENDER["Sender"] --> CHECK_CREDIT{"Credit Available?"}
        CHECK_CREDIT -->|"Yes"| SEND_DATA["Send Data"]
        CHECK_CREDIT -->|"No"| REQ_PULL["request_pull()"]
        REQ_PULL --> PACER["EQDS Pacer"]
        PACER --> GRANT_CREDIT["grant_credit()"]
        GRANT_CREDIT --> PULL_PKT["Send Pull Packet"]
        PULL_PKT --> SENDER
    end
```

Sources: [efa/eqds.h:74-238](), [efa/eqds.cc:89-137]()

## NCCL Plugin Integration

### Plugin Architecture

The NCCL plugin (`nccl_plugin.cc`) exposes standard NCCL network interface functions while using EFA transport internally.

| NCCL Function | EFA Implementation | Purpose |
|---------------|-------------------|---------|
| `pluginListen()` | `ep->uccl_listen()` | Connection establishment |
| `pluginConnect()` | `ep->uccl_connect()` | Outbound connections |
| `pluginIsend()` | `ep->uccl_send_async()` | Asynchronous send |
| `pluginIrecv()` | `ep->uccl_recv_multi_async()` | Asynchronous receive |

Sources: [efa/nccl_plugin.cc:176-224](), [efa/nccl_plugin.cc:390-443]()

### Memory Registration

The plugin handles both regular and DMA-BUF memory registration for GPU memory access.

```mermaid
graph LR
    subgraph "Memory Registration Flow"
        NCCL_REG["pluginRegMr()"] --> CHECK_TYPE{"Memory Type?"}
        CHECK_TYPE -->|"Host/Device"| IBV_REG["ibv_reg_mr()"]
        CHECK_TYPE -->|"DMA-BUF"| DMABUF_REG["ibv_reg_dmabuf_mr()"]
        IBV_REG --> MHANDLE["Mhandle"]
        DMABUF_REG --> MHANDLE
    end
```

Sources: [efa/nccl_plugin.cc:346-387]()

## Configuration and Tuning

### Key Configuration Parameters

The `transport_config.h` file defines critical system parameters for performance tuning.

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `kNumVdevices` | 8 | Virtual EFA devices/GPUs |
| `kNumEnginesPerVdev` | 2 | Engines per virtual device |
| `EFA_MTU` | 9000 | Maximum transmission unit |
| `kMaxDstQP` | 26 | Destination queue pairs per source |
| `kLinkBandwidth` | 100 Gbps | Expected link capacity |

Sources: [efa/transport_config.h:35-50](), [efa/transport_config.h:95-106]()

### Device Discovery

EFA devices are automatically discovered through environment variables or hardware enumeration.

```mermaid
graph TB
    subgraph "Device Discovery Process"
        ENV_CHECK["Check UCCL_EFA_DEVICES"] --> ENV_FOUND{"Found?"}
        ENV_FOUND -->|"No"| IBV_ENUM["ibv_get_device_list()"]
        ENV_FOUND -->|"Yes"| USE_ENV["Use Environment List"]
        IBV_ENUM --> FILTER["Filter EFA/rdmap devices"]
        FILTER --> DEVICE_LIST["g_efa_device_names"]
        USE_ENV --> DEVICE_LIST
    end
```

Sources: [efa/util_efa.cc:31-93]()

---

# Page: AF_XDP Backend

# AF_XDP Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

This page documents the AF_XDP backend for UCCL-collective, located under `ccl/advanced04-aws-afxdp/`. It covers the XDP kernel programs (`af_xdp_kern.c`, `af_xdp_kern_efa.c`), the userspace counterpart (`af_xdp_user`), EFA-specific integration in XDP mode, and the `sync.sh` coordination script used for multi-node setup.

This backend is one of several transport backends available to the UCCL-collective subsystem. For the standard RDMA/InfiniBand backend, see [2.2](#2.2). For the EFA backend using the conventional verbs path, see [2.3](#2.3). For the overall UCCL-collective plugin architecture, see [2.1](#2.1).

---

## Background: AF_XDP in UCCL

AF_XDP (Address Family eXpress Data Path) is a Linux socket type that provides kernel-bypass-style packet I/O using eBPF/XDP programs pinned to a network interface. Unlike RDMA verbs, AF_XDP works at the Ethernet frame level and can be used on NICs that expose an XDP hook — including AWS EFA in certain configurations.

In the UCCL context, the AF_XDP backend provides an alternative transport path for the UCCL-collective layer. It complements the RDMA/EFA verbs backends by offering a zero-copy, kernel-accelerated data path without requiring a full RDMA stack.

### Key Concepts

| Concept | Description |
|---|---|
| XDP program | eBPF bytecode attached to a NIC's receive path; runs before the kernel network stack |
| UMEM | Userspace-managed memory region registered with the kernel for zero-copy frame I/O |
| Fill / Completion ring | Queues through which userspace supplies and reclaims UMEM frames for RX |
| TX / RX ring | Per-socket descriptor rings for packet transmission and reception |
| `AF_XDP` socket | Userspace socket bound to a specific NIC queue, using UMEM for zero-copy |
| `xsk_socket` | The kernel-side socket type backing an AF_XDP connection |

---

## Component Architecture

The backend is split into two layers: a kernel-side XDP program and a userspace driver program. The diagram below maps these to their source files.

**AF_XDP Backend Component Map**

```mermaid
graph TD
    subgraph "Kernel Space"
        kern["af_xdp_kern.c\n(generic XDP program)"]
        kern_efa["af_xdp_kern_efa.c\n(EFA-specific XDP program)"]
    end

    subgraph "Userspace"
        user["af_xdp_user\n(compiled from af_xdp_user.c)\nuserspace driver + UMEM manager"]
        sync["sync.sh\nmulti-node coordination script"]
    end

    subgraph "NIC"
        nic_generic["Generic XDP-capable NIC"]
        nic_efa["AWS EFA NIC"]
    end

    kern -->|"loaded via xdp-loader"| nic_generic
    kern_efa -->|"loaded for EFA"| nic_efa
    user -->|"AF_XDP socket\n(xsk_socket)"| nic_generic
    user -->|"AF_XDP socket\n(xsk_socket)"| nic_efa
    sync -->|"orchestrates"| user
```

Sources: [.gitignore:63]()

---

## XDP Kernel Programs

The kernel-side component is a compiled eBPF object that the kernel attaches to the NIC's ingress XDP hook. UCCL provides two variants:

### `af_xdp_kern.c` — Generic XDP Program

This program handles the common case for XDP-capable NICs. Its primary responsibility is to redirect incoming packets from the NIC driver into an `AF_XDP` socket's RX ring, bypassing the normal kernel network stack (`XDP_REDIRECT` action).

Key behaviors:
- Parses Ethernet and IP headers to identify UCCL traffic.
- Applies a redirect map (`xsks_map`) to route packets to the correct `xsk_socket` based on queue index.
- Falls through to `XDP_PASS` for non-UCCL traffic, allowing normal kernel processing.

### `af_xdp_kern_efa.c` — EFA-Specific XDP Program

AWS EFA exposes a different hardware model and requires EFA-specific packet format handling. `af_xdp_kern_efa.c` is a separate XDP program adapted for EFA's network characteristics:

- Handles EFA-specific encapsulation or header fields that differ from standard Ethernet frames.
- May apply custom queue assignment logic that aligns with EFA's multi-queue model.
- Shares the same overall structure (`XDP_REDIRECT` via `xsks_map`) as the generic variant.

**XDP Kernel Program Execution Flow**

```mermaid
flowchart TD
    A["Packet arrives at NIC"] --> B["XDP hook fires\n(af_xdp_kern or af_xdp_kern_efa)"]
    B --> C{"Is packet\nUCCL traffic?"}
    C -- "Yes" --> D["Lookup xsks_map\nby queue_id"]
    D --> E{"Entry found?"}
    E -- "Yes" --> F["XDP_REDIRECT\nto xsk_socket RX ring"]
    E -- "No" --> G["XDP_PASS\n(kernel stack)"]
    C -- "No" --> G
    F --> H["userspace reads\nfrom RX ring"]
```

Sources: [.gitignore:63]()

---

## Userspace Implementation (`af_xdp_user`)

The userspace component (`af_xdp_user`, built from `af_xdp_user.c`) is the main driver program. It is listed in `.gitignore` as a compiled artifact [.gitignore:63]().

The userspace program is responsible for:

1. **UMEM allocation** — Allocating a large contiguous memory region and registering it with the kernel via `xsk_umem__create()`. This region is shared between userspace and the kernel for zero-copy frame exchange.
2. **Socket creation** — Opening one or more `AF_XDP` sockets with `xsk_socket__create()`, each bound to a specific NIC queue.
3. **Ring management** — Maintaining Fill, Completion, RX, and TX rings to coordinate frame ownership with the kernel.
4. **Packet I/O loop** — Polling RX rings for incoming packets, processing them, and posting TX descriptors for outbound packets.
5. **XDP program loading** — Loading the appropriate compiled eBPF object (`af_xdp_kern.o` or `af_xdp_kern_efa.o`) onto the target interface.

### UMEM and Ring Layout

```mermaid
graph LR
    subgraph "Userspace Process"
        umem["UMEM\n(large contiguous buffer)"]
        fill_ring["Fill Ring\n(frames given to kernel)"]
        comp_ring["Completion Ring\n(frames returned by kernel)"]
        tx_ring["TX Ring\n(frames to send)"]
        rx_ring["RX Ring\n(frames received)"]
    end

    subgraph "Kernel / NIC"
        xsk["xsk_socket"]
        driver["NIC Driver Queue"]
    end

    fill_ring -->|"supply frames"| xsk
    xsk -->|"DMA fill"| driver
    driver -->|"received frames"| rx_ring
    tx_ring -->|"send frames"| driver
    driver -->|"TX complete"| comp_ring
    umem -.->|"backing memory"| fill_ring
    umem -.->|"backing memory"| rx_ring
    umem -.->|"backing memory"| tx_ring
```

---

## EFA Integration in XDP Mode

When running on AWS EFA, the AF_XDP backend uses `af_xdp_kern_efa.c` instead of the generic kernel program. The userspace program detects or is configured to use the EFA interface and loads the EFA-specific eBPF object.

The EFA XDP path differs from the standard EFA verbs path (documented in [2.3](#2.3)) in that:

- It operates at the packet level rather than through the `libfabric`/`rdma-core` verbs API.
- UMEM buffers are managed entirely in userspace, without using EFA's provider-level memory registration.
- The XDP hook provides an earlier intercept point than the verbs completion queue model.

This makes the AF_XDP path suitable for workloads where low per-packet overhead is more important than the feature richness of the verbs path.

---

## `sync.sh` Coordination Script

Multi-node AF_XDP deployments require that XDP programs be loaded on all participating nodes before traffic flows. `sync.sh` provides a lightweight coordination mechanism for this:

| Step | Action |
|---|---|
| 1 | Establishes SSH connectivity or uses a shared signal file to coordinate node readiness |
| 2 | Triggers `af_xdp_user` launch on each node in the correct sequence |
| 3 | Waits for all nodes to confirm XDP program attachment before allowing traffic |
| 4 | Optionally tears down XDP programs on exit via `xdp-loader unload` |

This script serves the same role as barrier synchronization in MPI initialization — it ensures all NIC queues have the XDP redirect program installed and sockets bound before any collective operation begins.

---

## Integration with UCCL-Collective

The AF_XDP backend is one of the transport backends selectable within the UCCL-collective plugin. The diagram below shows how it slots into the broader UCCL-collective architecture.

**AF_XDP Backend Position in UCCL-Collective**

```mermaid
graph TD
    nccl_net["NCCL Net Plugin\n(libnccl-net-uccl.so)"]

    subgraph "UCCL-Collective Transport Backends"
        rdma_ib["RDMA/IB Backend\n(af_xdp_kern.c / IB verbs)"]
        efa_verbs["EFA Verbs Backend\n(libfabric / SRD)"]
        afxdp["AF_XDP Backend\naf_xdp_kern.c\naf_xdp_kern_efa.c\naf_xdp_user"]
    end

    nccl_net --> rdma_ib
    nccl_net --> efa_verbs
    nccl_net --> afxdp

    afxdp --> kern_prog["XDP Program\n(loaded by af_xdp_user)"]
    afxdp --> umem_mgr["UMEM Manager\n(af_xdp_user)"]
    kern_prog --> nic["NIC / EFA Queue"]
    umem_mgr --> nic
```

Sources: [.gitignore:57-63]()

---

## Summary of Source Files

| File | Location | Role |
|---|---|---|
| `af_xdp_kern.c` | `ccl/advanced04-aws-afxdp/` | eBPF/XDP kernel program for generic NICs |
| `af_xdp_kern_efa.c` | `ccl/advanced04-aws-afxdp/` | eBPF/XDP kernel program for AWS EFA |
| `af_xdp_user.c` | `ccl/advanced04-aws-afxdp/` | Userspace driver: UMEM, sockets, I/O loop |
| `sync.sh` | `ccl/advanced04-aws-afxdp/` | Multi-node startup coordination |
| `af_xdp_user` | _(build artifact, gitignored)_ | Compiled binary from `af_xdp_user.c` |

Sources: [.gitignore:57-63]()

---

# Page: UCCL-P2P Engine

# UCCL-P2P Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)

</details>



This page covers the UCCL-P2P subsystem: its design goals, component structure, supported backends, operation types, and the layered API from C++ through to Python. UCCL-P2P is the primary building block for point-to-point GPU memory transfers in UCCL.

For the higher-level Python collective API built on top of this engine, see [CollectiveContext Python API](#3.4). For the RDMA transport layer details (channel groups, QP management, device selection), see [RDMA Transport Layer](#3.2). For memory registration internals, see [Memory Registration and Buffer Management](#3.3). For the expert-parallelism engine (which has a different architecture), see [UCCL-EP Expert Parallelism](#4).

---

## Purpose

UCCL-P2P is a high-performance peer-to-peer transfer engine designed for distributed ML workloads such as KV-cache transfers and reinforcement learning weight exchanges. It is purpose-built for multi-NIC, high-bandwidth environments (e.g., 800 Gbps NICs) with an explicit multi-threaded design.

Key design goals:
- Efficient use of multiple CPU threads and multiple NICs per transfer
- Support for both **remote (RDMA over IB/RoCE/EFA/TCPX)** and **local (GPU IPC via shared memory)** connections
- Both blocking and non-blocking (async) transfer APIs
- Two-sided (send/recv) and one-sided (read/write) RDMA operations
- A thin C API (`libuccl_p2p.so`) and a Python extension (`p2p.abi3.so`) layered over the same C++ core

---

## Component Structure

**Component structure of UCCL-P2P**

```mermaid
graph TD
    subgraph "Python Layer"
        PY["p2p.Endpoint\n(nanobind)"]
        COLL_PY["collective.py\nCollectiveContext"]
        TRANSFER_PY["transfer.py"]
    end

    subgraph "C API"
        CAPI["uccl_engine.cc\nuccl_engine_t / uccl_conn_t\nuccl_engine_create/connect/accept\nuccl_engine_send/recv/read/write"]
        CAPI_H["uccl_engine.h\nPublic C header"]
    end

    subgraph "C++ Core"
        EP["Endpoint class\n(engine.h / engine.cc)\nManages connections, MRs, task rings"]
        ENGINE_API["engine_api.cc\nnanobind binding definitions"]
    end

    subgraph "Background Threads"
        SEND_TH["send_proxy_thread_\n(SEND_NET / WRITE_NET / SENDV / WRITEV)"]
        RECV_TH["recv_proxy_thread_\n(RECV_NET / READ_NET / RECVV / READV)"]
        IPC_TH["ipc_poller_thread_\n(IpcInflightOp polling)"]
        PASSIVE_TH["passive_accept_thread_\n(background accept loop)"]
    end

    subgraph "Transport Backends"
        NIC_EP["NICEndpoint\n(RDMA: IB / RoCE / EFA)"]
        TCPX_EP["nccl_tcpx_endpoint\n(GCP TCPX)"]
        TCP_EP["tcp::TCPEndpoint\n(NCCL-over-TCP)"]
        IPC_SHM["jring_t shared memory rings\n(intra-node GPU IPC)"]
    end

    PY --> ENGINE_API
    COLL_PY --> PY
    TRANSFER_PY --> PY
    ENGINE_API --> EP
    CAPI --> EP
    EP --> SEND_TH
    EP --> RECV_TH
    EP --> IPC_TH
    EP --> PASSIVE_TH
    EP --> NIC_EP
    EP --> TCPX_EP
    EP --> TCP_EP
    EP --> IPC_SHM
```

Sources: [p2p/engine.h:1-543](), [p2p/engine.cc:1-245](), [p2p/uccl_engine.h:1-200](), [p2p/uccl_engine.cc:1-130](), [p2p/Makefile:1-60]()

---

## The `Endpoint` Class

The `Endpoint` class ([p2p/engine.h:246-543]()) is the central object of UCCL-P2P. Every application-level operation (connect, accept, register, send, recv, read, write) routes through an `Endpoint` instance. It is exposed to Python as `p2p.Endpoint` via nanobind, and to C applications via `uccl_engine_t` in the C API.

### Constructor Variants

| Constructor | Purpose |
|---|---|
| `Endpoint(local_gpu_idx, num_cpus)` | Full initialization: starts background threads, opens listen socket, creates IPC streams for all GPUs |
| `Endpoint(num_cpus)` | Lazy initialization: engine starts without a bound GPU; actual initialization occurs on first `reg()` call, using the device of the registered pointer |

[p2p/engine.cc:180-277]()

### Internal State

| Field | Type | Role |
|---|---|---|
| `ep_` | `RDMAEndPoint` (shared_ptr) | Active transport endpoint (`NICEndpoint` or `TCPEndpoint`) |
| `send_unified_task_ring_` | `jring_t*` | MPSC ring feeding the send proxy thread |
| `recv_unified_task_ring_` | `jring_t*` | MPSC ring feeding the recv proxy thread |
| `ipc_inflight_ring_` | `jring_t*` | MPSC ring for in-flight IPC operations |
| `conn_id_to_conn_` | `unordered_map<uint64_t, Conn*>` | Active connections indexed by `conn_id` |
| `mr_id_to_mr_` | `unordered_map<uint64_t, MR*>` | Registered memory regions indexed by `mr_id` |
| `inbox_rings_` | `array<ShmRingHandle, 8>` | Per-GPU shared-memory rings for IPC messaging |
| `ipc_streams_` | `vector<vector<gpuStream_t>>` | CUDA/HIP streams for IPC async copies |

[p2p/engine.h:466-502]()

---

## Threading Model

**Threading model of Endpoint**

```mermaid
sequenceDiagram
    participant "App Thread" as APP
    participant "send_unified_task_ring_" as SRING
    participant "recv_unified_task_ring_" as RRING
    participant "send_proxy_thread_" as SPT
    participant "recv_proxy_thread_" as RPT
    participant "ipc_poller_thread_" as IPT
    participant "NICEndpoint / jring_t" as TRANSPORT

    APP->>SRING: "enqueue UnifiedTask* (SEND_NET / WRITE_NET / SENDV)"
    APP->>RRING: "enqueue UnifiedTask* (RECV_NET / READ_NET / RECVV)"
    SPT->>SRING: "dequeue task"
    SPT->>TRANSPORT: "uccl_send_async / uccl_write_async"
    RPT->>RRING: "dequeue task"
    RPT->>TRANSPORT: "uccl_recv_async / uccl_read_async"
    RPT->>TRANSPORT: "uccl_poll_ureq_once (completion polling)"
    APP->>IPT: "push IpcInflightOp* via ipc_inflight_ring_"
    IPT->>TRANSPORT: "gpuEventQuery (GPU copy completion)"
    TRANSPORT-->>SPT: "CQ completion"
    TRANSPORT-->>RPT: "data arrived"
    SPT-->>APP: "TransferStatus.done = true"
    RPT-->>APP: "TransferStatus.done = true"
```

Sources: [p2p/engine.h:488-512](), [p2p/engine.cc:686-724]()

The three background threads are started unconditionally during `Endpoint` construction with a GPU index [p2p/engine.cc:228-232](). The passive accept thread is started optionally via `start_passive_accept()`.

---

## Task Types and Dispatch

All transfer operations are described by `UnifiedTask` ([p2p/engine.h:184-229]()). Tasks carry a `TaskType` tag and a union `SpecificData` that holds either a `FifoItem` (for one-sided RDMA), an `IpcTransferInfo` (for IPC), or a `TaskBatch` (for vectorized ops).

| `TaskType` | Ring | Description |
|---|---|---|
| `SEND_NET` | send | Two-sided RDMA send |
| `RECV_NET` | recv | Two-sided RDMA receive |
| `WRITE_NET` | send | One-sided RDMA write |
| `READ_NET` | recv | One-sided RDMA read |
| `SENDV` | send | Vectorized send (scatter) |
| `RECVV` | recv | Vectorized receive (gather) |
| `WRITEV` | send | Vectorized RDMA write |
| `READV` | recv | Vectorized RDMA read |
| `SEND_IPC` | (direct) | Intra-node GPU copy, initiator |
| `RECV_IPC` | (direct) | Intra-node GPU copy, responder |

[p2p/engine.h:111-124]()

For async operations, the caller receives a `uint64_t transfer_id` which is actually a pointer to a heap-allocated `TransferStatus` object. Polling is done via `poll_async(transfer_id, &is_done)`. [p2p/engine.h:179-182]()

---

## Connection Lifecycle

**Connection lifecycle: remote (RDMA) and local (IPC)**

```mermaid
flowchart TD
    subgraph "Remote RDMA Connection"
        A["Endpoint::connect(ip, gpu_idx, port)"]
        B["uccl_connect(ep_, ...)"]
        C["TCP handshake + RDMA QP exchange"]
        D["ConnID returned\n(sock_fd + flow_id)"]
        E["conn_id_to_conn_ entry created\n(Conn struct)"]
        A --> B --> C --> D --> E
    end

    subgraph "Local IPC Connection"
        F["Endpoint::connect_local(remote_gpu_idx)"]
        G["Unix domain socket handshake"]
        H["Attach remote inbox_rings_[i] via shm_fd"]
        I["conn.is_local_ = true\nconn.shm_attached_ = true"]
        F --> G --> H --> I
    end

    subgraph "Metadata Exchange (Python path)"
        J["get_metadata() / get_unified_metadata()"]
        K["parse_metadata(bytes) -> (ip, port, gpu_idx)"]
        L["add_remote_endpoint(metadata) -> conn_id"]
        J --> K --> L
    end
```

Sources: [p2p/engine.cc:349-530](), [p2p/engine.h:274-290](), [p2p/engine.h:435-437]()

A `Conn` struct ([p2p/engine.h:69-78]()) records the logical connection: `conn_id_`, `uccl_conn_id_` (the underlying transport handle), `ip_addr_`, `remote_gpu_idx_`, `is_local_`, and a `ShmRingHandle remote_inbox_` for IPC connections.

---

## Operation API Summary

### Blocking Operations

```
send(conn_id, mr_id, ptr, size) -> bool
recv(conn_id, mr_id, ptr, size) -> bool
read(conn_id, mr_id, dst, size, slot_item) -> bool
write(conn_id, mr_id, src, size, slot_item) -> bool
sendv(conn_id, mr_id_v, data_v, size_v, num_iovs) -> bool
recvv(conn_id, mr_id_v, data_v, size_v, num_iovs) -> bool
readv(conn_id, mr_id_v, dst_v, size_v, slot_item_v, num_iovs) -> bool
writev(conn_id, mr_id_v, src_v, size_v, slot_item_v, num_iovs) -> bool
```

### Async Operations

```
send_async(conn_id, mr_id, ptr, size, &transfer_id) -> bool
recv_async(conn_id, mr_id, ptr, size, &transfer_id) -> bool
read_async(conn_id, mr_id, dst, size, slot_item, &transfer_id) -> bool
write_async(conn_id, mr_id, src, size, slot_item, &transfer_id) -> bool
sendv_async(..., &transfer_id) -> bool
recvv_async(..., &transfer_id) -> bool
readv_async(..., &transfer_id) -> bool
writev_async(..., &transfer_id) -> bool
poll_async(transfer_id, &is_done) -> bool
```

### IPC Operations (intra-node)

```
send_ipc(conn_id, data, size) -> bool
recv_ipc(conn_id, data, size) -> bool
send_ipc_async(conn_id, data, size, &transfer_id) -> bool
recv_ipc_async(conn_id, data, size, &transfer_id) -> bool
write_ipc(conn_id, data, size, IpcTransferInfo) -> bool
read_ipc(conn_id, data, size, IpcTransferInfo) -> bool
writev_ipc(conn_id, data_v, size_v, info_v, num_iovs) -> bool
readv_ipc(conn_id, data_v, size_v, info_v, num_iovs) -> bool
```

### Memory Registration

```
reg(ptr, size, &mr_id) -> bool
regv(data_v, size_v, &mr_id_v) -> bool
dereg(mr_id) -> bool
```

Sources: [p2p/engine.h:291-432](), [p2p/README.md:447-750]()

One-sided RDMA `read` and `write` operations require a `FifoItem` that encodes the remote address and key. This is advertised by the remote side using `advertise(conn_id, mr_id, addr, len, out_buf)` or pre-computed with `prepare_fifo(mr_id, addr, len, out_buf)`. [p2p/engine.h:374-385]()

---

## C API (`uccl_engine.h`)

For applications that cannot use C++ or Python directly, UCCL-P2P exposes a flat C API compiled into `libuccl_p2p.so`. The C API wraps the `Endpoint` class behind opaque handle types.

**C API type and function mapping**

```mermaid
graph LR
    subgraph "C API types (uccl_engine.h)"
        ET["uccl_engine_t\n(wraps Endpoint)"]
        CT["uccl_conn_t\n(conn_id + sock_fd + oob_conn_key)"]
        MR["uccl_mr_t (uint64_t mr_id)"]
    end

    subgraph "C API functions (uccl_engine.cc)"
        CREATE["uccl_engine_create(num_cpus, in_python)"]
        DESTROY["uccl_engine_destroy(engine)"]
        CONNECT["uccl_engine_connect(engine, ip, gpu, port)"]
        ACCEPT["uccl_engine_accept(engine, ip_buf, len, gpu_out)"]
        REG["uccl_engine_reg(engine, data, size, &mr_id)"]
        SEND["uccl_engine_send(conn, mr, data, size, &tid)"]
        RECV["uccl_engine_recv(conn, mr, data, size)"]
        READ["uccl_engine_read(conn, mr, data, size, fifo_item, &tid)"]
        WRITE["uccl_engine_write(conn, mr, data, size, fifo_item, &tid)"]
        POLL["uccl_engine_xfer_status(conn, transfer_id)"]
        FIFO["uccl_engine_prepare_fifo(engine, mr, data, size, buf)"]
    end

    CREATE --> ET
    CONNECT --> CT
    ACCEPT --> CT
    REG --> MR
    SEND --> CT
    RECV --> CT
    READ --> CT
    WRITE --> CT
    POLL --> CT
```

Sources: [p2p/uccl_engine.h:1-200](), [p2p/uccl_engine.cc:41-405]()

The C API also supports OOB notification passing (`uccl_engine_send_notif`, `uccl_engine_get_notifs`) used by NIXL-style initiator/target transfer workflows. [p2p/uccl_engine.cc:382-453]()

---

## Backend Selection

The backend is selected at compile time using preprocessor flags.

| Flag | Backend | Transport endpoint |
|---|---|---|
| _(default)_ | InfiniBand / RoCE | `NICEndpoint` |
| `USE_EFA=1` | AWS EFA | `NICEndpoint` (EFA variant) |
| `USE_TCPX=1` | GCP TCPX | `nccl_tcpx::Endpoint` |
| `USE_TCP=1` | NCCL-over-TCP | `tcp::TCPEndpoint` |

[p2p/Makefile:28-43](), [p2p/engine.h:36-47]()

At runtime, the GID index for RDMA networks can be tuned via environment variable `UCCL_P2P_RDMA_GID_INDEX` (default 0 for EFA, 3 for IB). Additional tuning knobs:

| Environment Variable | Description | Default |
|---|---|---|
| `UCCL_P2P_LOG_LEVEL` | Log verbosity | `WARNING` |
| `UCCL_P2P_RDMA_GID_INDEX` | RDMA GID index | 0 (EFA) / 3 (IB) |
| `UCCL_P2P_RDMA_SL` | Service level | 8 (EFA) / 3 (IB) |
| `UCCL_P2P_RDMA_TC` | Traffic class | 104 (IB) |

Sources: [p2p/README.md:98-104](), [p2p/engine.cc:156-174]()

---

## Python Usage Example

The following shows the canonical client/server pattern with GPU tensor transfer.

```python
# Server side
from uccl import p2p
import torch

ep = p2p.Endpoint(local_gpu_idx=0, num_cpus=4)
ok, remote_ip, remote_gpu, conn_id = ep.accept()

buf = torch.zeros(1024, dtype=torch.float32).cuda()
ok, mr_id = ep.reg(buf.data_ptr(), buf.numel() * 4)
ok = ep.recv(conn_id, mr_id, buf.data_ptr(), buf.numel() * 4)

# Client side
ep = p2p.Endpoint(local_gpu_idx=0, num_cpus=4)
metadata = ep.get_metadata()   # exchange via torch.distributed or out-of-band
ip, port, gpu = p2p.Endpoint.parse_metadata(metadata)
ok, conn_id = ep.connect(ip, gpu, remote_port=port)

buf = torch.ones(1024, dtype=torch.float32).cuda()
ok, mr_id = ep.reg(buf.data_ptr(), buf.numel() * 4)
ok = ep.send(conn_id, mr_id, buf.data_ptr(), buf.numel() * 4)
```

For multi-tensor scatter/gather, use `sendv` / `recvv`. For one-sided operations, the remote side first calls `advertise()` to produce a `FifoItem` blob, which is shared out-of-band; the initiator then calls `read()` or `write()` with that blob. [p2p/README.md:391-444]()

---

## Build Artifacts

The build system produces two artifacts from the `p2p/` directory:

| Artifact | Purpose |
|---|---|
| `p2p.abi3.so` | Python extension module, installed as `uccl/p2p.abi3.so` |
| `libuccl_p2p.so` | Shared library exposing the C API (`uccl_engine.h`) |

Both are built from the same source files (`engine.cc`, `engine_api.cc`) with nanobind objects included in the Python extension only. [p2p/Makefile:77-132]()

To build:
```bash
# Via top-level build script (recommended)
bash build.sh cuda p2p --install

# Or directly
cd p2p && make -j install

# With EFA support
cd p2p && make -j USE_EFA=1 install
```

Sources: [p2p/Makefile:107-132](), [p2p/README.md:23-68](), [build.sh:67-100]()

---

# Page: P2P Engine Architecture

# P2P Engine Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)

</details>



This page documents the internal design of the UCCL-P2P engine: how the `Endpoint` C++ class is structured, its threading model, how connections are established, and the full set of operations it supports. This page focuses on the C++ core and the C API shim.

For the RDMA transport abstraction beneath the engine (channel groups, QP management, device selection), see [3.2](#3.2). For the Python `CollectiveContext` that sits above it, see [3.4](#3.4). For memory registration internals, see [3.3](#3.3).

---

## Overview

The `Endpoint` class ([p2p/engine.h:246-543]()) is the central object of the P2P subsystem. A single `Endpoint` instance:

- Owns one or two RDMA/TCP connections to remote or local peers.
- Maintains three background threads that handle send, receive, and intra-node GPU-copy operations.
- Exposes both blocking and asynchronous variants of every operation.
- Bridges to a C API (`uccl_engine_t`) for use outside Python, and to Python via nanobind.

The table below summarises the major types in the engine layer.

| Type | File | Role |
|---|---|---|
| `Endpoint` | `engine.h` | Top-level class; owns threads, rings, connections, MR table |
| `UnifiedTask` | `engine.h` | Polymorphic work item passed through task rings |
| `TaskBatch` | `engine.h` | Vectorised (scatter-gather) sub-task descriptor |
| `Conn` | `engine.h` | Per-connection state (conn ID, RDMA conn ID, shm ring handle) |
| `ShmRingHandle` | `engine.h` | Shared-memory `jring_t` used for intra-node signalling |
| `ShmMsg` | `engine.h` | Message type sent over a `ShmRingHandle` |
| `IpcTransferInfo` | `engine.h` | GPU IPC handle + offset for one-sided IPC transfers |
| `IpcInflightOp` | `engine.h` | Tracks in-flight async GPU copy events for polling |
| `MR` / `P2PMhandle` | `engine.h` | Memory registration bookkeeping |
| `uccl_engine_t` | `uccl_engine.h` | Opaque C wrapper around `Endpoint` |
| `uccl_conn_t` | `uccl_engine.h` | Opaque C wrapper around a `conn_id` |

Sources: [p2p/engine.h:49-242](), [p2p/uccl_engine.h:1-50]()

---

## Threading Model

The `Endpoint` constructor ([p2p/engine.cc:180-245]()) spawns exactly three background threads and allocates `jring_t`-backed task rings for inter-thread communication.

**Task rings** (capacity `kTaskRingSize = 1024` elements):

| Ring | Producer | Consumer |
|---|---|---|
| `send_unified_task_ring_` | Application threads (any) | `send_proxy_thread_` |
| `recv_unified_task_ring_` | Application threads (any) | `recv_proxy_thread_` |
| `ipc_inflight_ring_` | `send_proxy_thread_` / `recv_proxy_thread_` | `ipc_poller_thread_` |

**Threading diagram — `Endpoint` internal threads**

```mermaid
flowchart TD
    subgraph AppThreads["Application Threads (Python / C API)"]
        A1["send() / send_async()"]
        A2["recv() / recv_async()"]
        A3["read() / write() and variants"]
        A4["send_ipc() / recv_ipc()"]
    end

    subgraph Rings["jring_t MPSC Rings"]
        SR["send_unified_task_ring_\n(UnifiedTask*)"]
        RR["recv_unified_task_ring_\n(UnifiedTask*)"]
        IR["ipc_inflight_ring_\n(IpcInflightOp*)"]
    end

    subgraph Threads["Background Threads"]
        ST["send_proxy_thread_func()\nDequeues SEND_NET / WRITE_NET / SENDV / WRITEV\nCalls uccl_send_async / uccl_write_async"]
        RT["recv_proxy_thread_func()\nDequeues RECV_NET / READ_NET / RECVV / READV\nCalls uccl_recv_async / uccl_read_async"]
        IT["ipc_poller_thread_func()\nPolls gpuEvent_t for IPC completions\nSignals TransferStatus::done"]
    end

    A1 -->|"enqueue"| SR
    A3 -->|"WRITE_NET"| SR
    A2 -->|"enqueue"| RR
    A3 -->|"READ_NET"| RR
    A4 -->|"SEND_IPC / RECV_IPC"| SR

    SR -->|"dequeue"| ST
    RR -->|"dequeue"| RT
    ST -->|"IpcInflightOp*"| IR
    RT -->|"IpcInflightOp*"| IR
    IR -->|"dequeue"| IT
```

Sources: [p2p/engine.h:488-500](), [p2p/engine.cc:219-232]()

---

## Task Type System

Every operation is encoded as a `UnifiedTask` ([p2p/engine.h:184-229]()). The `TaskType` enum determines which thread processes it and how the `specific` union is interpreted.

```mermaid
classDiagram
    class UnifiedTask {
        +TaskType type
        +void* data
        +size_t size
        +uint64_t conn_id
        +uint64_t mr_id
        +TransferStatus* status_ptr
        +SpecificData specific
        +bool is_batch_task()
    }
    class SpecificData {
        <<union>>
        +net : FifoItem slot_item
        +ipc : IpcTransferInfo ipc_info
        +batch : TaskBatch task_batch
    }
    class TaskBatch {
        +size_t num_iovs
        +shared_ptr~vector~ const_data_ptr
        +shared_ptr~vector~ data_ptr
        +shared_ptr~vector~ size_ptr
        +shared_ptr~vector~ mr_id_ptr
        +shared_ptr~vector~ slot_item_ptr
    }
    class TransferStatus {
        +atomic~bool~ done
        +shared_ptr~UnifiedTask~ task_ptr
    }
    UnifiedTask --> SpecificData
    UnifiedTask --> TransferStatus
    SpecificData --> TaskBatch
```

| `TaskType` | Thread | Notes |
|---|---|---|
| `SEND_NET` | send | Two-sided send |
| `RECV_NET` | recv | Two-sided receive |
| `WRITE_NET` | send | One-sided RDMA WRITE |
| `READ_NET` | recv | One-sided RDMA READ |
| `SEND_IPC` | send | Intra-node GPU IPC send |
| `RECV_IPC` | recv | Intra-node GPU IPC receive |
| `WRITE_IPC` | send | One-sided IPC write |
| `READ_IPC` | recv | One-sided IPC read |
| `SENDV` | send | Vectorised send (uses `TaskBatch`) |
| `RECVV` | recv | Vectorised receive |
| `WRITEV` | send | Vectorised RDMA WRITE |
| `READV` | recv | Vectorised RDMA READ |

Sources: [p2p/engine.h:111-145](), [p2p/engine.h:184-229]()

---

## Connection Lifecycle

### Remote Connections (RDMA)

Remote connections are established over TCP and then promoted to RDMA queue pairs. The `Endpoint` uses `NICEndpoint` internally (unless compiled with `UCCL_P2P_USE_NCCL` or `UCCL_P2P_USE_TCPX`).

**Connection establishment sequence**

```mermaid
sequenceDiagram
    participant Client as "Client Endpoint\nEndpoint::connect()"
    participant Server as "Server Endpoint\nEndpoint::accept()"
    participant NIC as "NICEndpoint\n(rdma_endpoint.h)"

    Client->>NIC: uccl_connect(ep_, remote_gpu_idx, ip, port)
    Server->>NIC: uccl_accept(ep_, &ip_addr, &remote_gpu_idx)
    NIC-->>Client: ConnID (sock_fd, flow_id)
    NIC-->>Server: ConnID (sock_fd, flow_id)
    Client->>Client: conn_id_to_conn_[conn_id] = new Conn{...}
    Server->>Server: conn_id_to_conn_[conn_id] = new Conn{...}
```

The returned `conn_id` is a monotonically increasing integer from `next_conn_id_` and is stored in `conn_id_to_conn_` under a `std::shared_mutex` (`conn_mu_`).

Metadata exchange for `connect()` without a prior handshake uses `get_metadata()` / `parse_metadata()` ([p2p/engine.cc:380-486]()), which serialise the local IP, port, and GPU index into a compact byte vector that callers can distribute via any side channel (e.g., `torch.distributed.all_gather`).

### Local Connections (Intra-Node IPC)

Intra-node connections bypass RDMA and use POSIX shared memory rings (`jring_t`) for signalling GPU IPC handles. Each `Endpoint` pre-creates one `ShmRingHandle` (its "inbox") per possible GPU ([p2p/engine.cc:234-242]()).

```mermaid
flowchart LR
    subgraph GPU0["GPU 0 Process"]
        EP0["Endpoint (gpu 0)"]
        IB0["inbox_rings_[0]\n/uccl_gpu_jring_0_0"]
        OB01["Attaches remote inbox\n/uccl_gpu_jring_0_1"]
    end
    subgraph GPU1["GPU 1 Process"]
        EP1["Endpoint (gpu 1)"]
        IB1["inbox_rings_[1]\n/uccl_gpu_jring_0_1"]
        OB10["Attaches remote inbox\n/uccl_gpu_jring_0_0"]
    end

    EP0 -->|"send ShmMsg (IPC_HANDLE)"| OB01
    OB01 -.->|"shm"| IB1
    EP1 -->|"send ShmMsg (IPC_HANDLE)"| OB10
    OB10 -.->|"shm"| IB0
```

The shm ring names follow the pattern `/uccl_gpu_jring_<from>_<to>` ([p2p/engine.cc:131-134]()). Messages sent over these rings are `ShmMsg` structs whose `type` field is one of `CONNECT`, `IPC_HANDLE`, or `COMPLETION`.

`connect_local()` and `accept_local()` set up these associations; the `ipc_poller_thread_func` polls GPU events and signals completion via the same `ShmRingHandle` back-channel.

Sources: [p2p/engine.h:62-109](), [p2p/engine.cc:131-152](), [p2p/engine.cc:234-242]()

---

## Supported Operations

All public methods follow the same pattern: validate `conn_id` and `mr_id`, create (or directly execute) a `UnifiedTask`, and either block on completion or return a `transfer_id` for later polling.

### Two-Sided (Send/Receive)

| Blocking | Async | Vectorised (Blocking) | Vectorised (Async) |
|---|---|---|---|
| `send()` | `send_async()` | `sendv()` | `sendv_async()` |
| `recv()` | `recv_async()` | `recvv()` | `recvv_async()` |

The blocking variants spin on `uccl_poll_ureq_once` in a loop, periodically checking Python signals via `check_python_signals()` ([p2p/engine.cc:121-128]()).

Async variants enqueue a `UnifiedTask*` to the appropriate ring and return a `transfer_id` that is actually a pointer to a heap-allocated `TransferStatus`. The caller polls with `poll_async(transfer_id)`.

Sources: [p2p/engine.h:298-330](), [p2p/engine.cc:629-891]()

### One-Sided (Read/Write over RDMA)

One-sided operations require the remote side to first call `advertise()` or `advertisev()` to produce a `FifoItem` blob, which encodes the remote virtual address and RDMA key. This blob is distributed out-of-band (e.g., via `torch.distributed.send`).

| Blocking | Async | Vectorised (Blocking) | Vectorised (Async) |
|---|---|---|---|
| `read()` | `read_async()` | `readv()` | `readv_async()` |
| `write()` | `write_async()` | `writev()` | `writev_async()` |

`advertise()` calls `prepare_fifo_metadata()` to fill the `FifoItem` with the RDMA rkey and virtual address ([p2p/engine.cc:1158-1173]()). `prepare_fifo()` is a connection-free variant that pre-computes the `FifoItem` at registration time.

Sources: [p2p/engine.h:332-369](), [p2p/engine.cc:894-1155]()

### IPC Operations (Intra-Node)

IPC operations transfer data between GPUs on the same host using `gpuIpcMemHandle_t` (CUDA IPC) or the HIP equivalent. There are two models:

1. **Two-sided IPC** (`send_ipc` / `recv_ipc`): the receiver sends its IPC handle to the sender over the `ShmRingHandle` inbox ring; the sender opens the handle and copies into the remote buffer.
2. **One-sided IPC** (`write_ipc` / `read_ipc` / vectorised variants): the advertising side calls `advertise_ipc()` to produce an `IpcTransferInfo` blob; the initiator passes this blob into the write/read call directly.

All IPC variants support async forms and use `gpuEvent_t` for completion tracking via `IpcInflightOp` ([p2p/engine.h:232-240]()).

Sources: [p2p/engine.h:371-431](), [p2p/engine.h:86-92]()

---

## Memory Registration

Memory regions must be registered before use. The `Endpoint` assigns each registration a monotonically increasing `mr_id` from `next_mr_id_` and stores a `MR*` in `mr_id_to_mr_` under `mr_mu_`.

```mermaid
flowchart LR
    A["reg(data_ptr, size)"]
    B["uccl_regmr(ep_, data, size, mhandle)"]
    C["mr_id_to_mr_[mr_id] = new MR{mr_id, mhandle}"]
    D["Returns mr_id to caller"]

    A --> B --> C --> D
```

`P2PMhandle` wraps an `MRArray` which holds one or more `ibv_mr*` handles across potentially multiple NICs ([p2p/engine.h:49-59]()). Deregistration via `dereg(mr_id)` calls `uccl_deregmr` and removes the entry from the map.

Bulk registration (`regv`) registers multiple memory regions in a single call, returning a vector of `mr_id` values.

For lazy initialisation: the no-GPU-index constructor ([p2p/engine.cc:247-277]()) defers `NICEndpoint` creation until the first `reg()` call, at which point the GPU index is inferred from the pointer's device.

Sources: [p2p/engine.h:465-480](), [p2p/engine.cc:532-627]()

---

## C API Shim

`uccl_engine.cc` wraps the `Endpoint` class in a C-callable API for use outside Python. The key types and their mappings are:

| C type | C++ backing |
|---|---|
| `uccl_engine_t*` | `struct uccl_engine { unique_ptr<Endpoint> endpoint; }` |
| `uccl_conn_t*` | `struct uccl_conn { uint64_t conn_id; uccl_engine* engine; ... }` |
| `uccl_mr_t` | `uint64_t` (the `mr_id`) |

**C API function to `Endpoint` method mapping**

```mermaid
flowchart TD
    CE["uccl_engine_create()"] --> EP["new Endpoint(num_cpus)"]
    CC["uccl_engine_connect()"] --> EC["Endpoint::connect()"]
    CA["uccl_engine_accept()"] --> EA["Endpoint::accept()"]
    CR["uccl_engine_reg()"] --> ER["Endpoint::reg()"]
    CS["uccl_engine_send()"] --> ESA["Endpoint::send_async()"]
    CRV["uccl_engine_recv()"] --> ERV["Endpoint::recv()"]
    CRD["uccl_engine_read()"] --> ERA["Endpoint::read_async()"]
    CW["uccl_engine_write()"] --> EWA["Endpoint::write_async()"]
    CX["uccl_engine_xfer_status()"] --> EP2["Endpoint::poll_async()"]
    CMD["uccl_engine_get_metadata()"] --> EGM["Endpoint::get_unified_metadata()"]
    CPF["uccl_engine_prepare_fifo()"] --> EPF["Endpoint::prepare_fifo()"]
```

The C API also manages a global `mem_reg_info` map (`unordered_map<uintptr_t, mem_reg_entry_t>`) that associates base addresses to `mr_id` values, enabling address-based lookup without exposing `mr_id` to callers ([p2p/uccl_engine.cc:65-80]()).

Sources: [p2p/uccl_engine.h:1-240](), [p2p/uccl_engine.cc:41-502]()

---

## Construction and Teardown

**Constructor sequence (primary form)**

[p2p/engine.cc:180-245]()

1. Enumerate all GPU devices; create non-blocking CUDA/HIP streams for IPC (`ipc_streams_`).
2. Initialise Google logging (once, via `std::call_once`).
3. Create `NICEndpoint` (or `TCPEndpoint` if `UCCL_P2P_USE_NCCL`).
4. Allocate `send_unified_task_ring_` and `recv_unified_task_ring_`.
5. Start `send_proxy_thread_` and `recv_proxy_thread_`.
6. Allocate `ipc_inflight_ring_`; start `ipc_poller_thread_`.
7. Create POSIX shm rings for each possible GPU (up to `kMaxNumGPUs = 8`).

**Destructor sequence**

[p2p/engine.cc:279-345]()

1. Set `stop_` flag; optionally signal and join passive-accept threads.
2. Join send/recv/IPC proxy threads.
3. Free task rings.
4. Detach or destroy all `ShmRingHandle` entries.
5. Deregister and delete all `MR*` entries.

---

## Environment Variables

| Variable | Effect | Default |
|---|---|---|
| `UCCL_P2P_LOG_LEVEL` | Sets `FLAGS_minloglevel` for glog | `WARNING` |
| `UCCL_P2P_RDMA_GID_INDEX` | GID index used by RDMA transport | `0` (EFA) / `3` (IB) |
| `UCCL_P2P_RDMA_SL` | RDMA service level | `8` (EFA) / `3` (IB) |
| `UCCL_P2P_RDMA_TC` | RDMA traffic class | `104` (IB) |
| `UCCL_RCMODE` | Enable RC (reliable connected) mode for one-sided ops | unset |

Sources: [p2p/engine.cc:156-174](), [p2p/README.md:98-103]()

---

# Page: RDMA Transport Layer

# RDMA Transport Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [p2p/endpoint_wrapper.h](p2p/endpoint_wrapper.h)
- [p2p/include/common.h](p2p/include/common.h)
- [p2p/rdma/define.h](p2p/rdma/define.h)
- [p2p/rdma/epoll_client.h](p2p/rdma/epoll_client.h)
- [p2p/rdma/epoll_server.h](p2p/rdma/epoll_server.h)
- [p2p/rdma/memory_allocator.h](p2p/rdma/memory_allocator.h)
- [p2p/rdma/providers/efa/rdma_channel_impl_efa.cc](p2p/rdma/providers/efa/rdma_channel_impl_efa.cc)
- [p2p/rdma/providers/efa/rdma_device_selection_efa.h](p2p/rdma/providers/efa/rdma_device_selection_efa.h)
- [p2p/rdma/providers/ib/rdma_channel_impl_ib.cc](p2p/rdma/providers/ib/rdma_channel_impl_ib.cc)
- [p2p/rdma/providers/ib/rdma_device_selection_ib.h](p2p/rdma/providers/ib/rdma_device_selection_ib.h)
- [p2p/rdma/rdma_channel.h](p2p/rdma/rdma_channel.h)
- [p2p/rdma/rdma_channel_group.h](p2p/rdma/rdma_channel_group.h)
- [p2p/rdma/rdma_channel_impl.h](p2p/rdma/rdma_channel_impl.h)
- [p2p/rdma/rdma_context.h](p2p/rdma/rdma_context.h)
- [p2p/rdma/rdma_device.h](p2p/rdma/rdma_device.h)
- [p2p/rdma/rdma_endpoint.h](p2p/rdma/rdma_endpoint.h)
- [p2p/rdma/tests/Makefile](p2p/rdma/tests/Makefile)

</details>



This page documents the RDMA transport abstraction inside the UCCL-P2P subsystem: how RDMA devices are discovered, how channels are created and connected, and how sends and receives are dispatched across those channels. The scope is the `p2p/rdma/` directory and its sub-providers.

For the higher-level `Endpoint` class that calls into this layer, see [P2P Engine Architecture](#3.1). For how GPU memory is registered and tracked, see [Memory Registration and Buffer Management](#3.3). For the Python-facing API built on top of this layer, see [CollectiveContext Python API](#3.4).

---

## Component Overview

The RDMA transport layer is organized in four concerns: device discovery, context management, channel implementation (provider-specific), and endpoint coordination.

**Component hierarchy diagram:**

```mermaid
graph TD
    NICEndpoint["NICEndpoint\n(rdma_endpoint.h)"]

    subgraph "OOB Signaling"
        ES["EpollServer\n(epoll_server.h)"]
        EC["EpollClient\n(epoll_client.h)"]
    end

    subgraph "Channel Groups"
        SCG["SendChannelGroup\n(rdma_channel_group.h)"]
        RCG["RecvChannelGroup\n(rdma_channel_group.h)"]
        CG["ChannelGroup (base)\n(rdma_channel_group.h)"]
        SCG --> CG
        RCG --> CG
    end

    subgraph "Channel"
        RC["RDMAChannel\n(rdma_channel.h)"]
        RCI["RDMAChannelImpl (interface)\n(rdma_channel_impl.h)"]
        IB["IBChannelImpl\n(providers/ib/rdma_channel_impl_ib.cc)"]
        EFA["EFAChannelImpl\n(providers/efa/rdma_channel_impl_efa.cc)"]
        RC --> RCI
        RCI --> IB
        RCI --> EFA
    end

    subgraph "Context & Device"
        RCtx["RdmaContext\n(rdma_context.h)"]
        RDev["RdmaDevice\n(rdma_device.h)"]
        RDM["RdmaDeviceManager\n(rdma_device.h)"]
        MA["MemoryAllocator\n(memory_allocator.h)"]
        RDM --> RDev
        RCtx --> RDev
    end

    NICEndpoint --> ES
    NICEndpoint --> EC
    NICEndpoint --> SCG
    NICEndpoint --> RCG
    NICEndpoint --> RCtx
    NICEndpoint --> MA
    SCG --> RC
    RCG --> RC
    RC --> RCtx
```

Sources: [p2p/rdma/rdma_endpoint.h:1-50](), [p2p/rdma/rdma_channel.h:1-50](), [p2p/rdma/rdma_channel_impl.h:1-103](), [p2p/rdma/rdma_channel_group.h:1-102](), [p2p/rdma/rdma_context.h:1-30](), [p2p/rdma/rdma_device.h:1-35](), [p2p/rdma/memory_allocator.h:1-20]()

---

## Device Discovery and Selection

### RdmaDeviceManager

`RdmaDeviceManager` ([p2p/rdma/rdma_device.h:62-178]()) is a thread-safe singleton. On first access it calls `ibv_get_device_list` and wraps each result in an `RdmaDevice`. It exposes:

| Method | Purpose |
|---|---|
| `instance()` | Returns the singleton |
| `getDevice(size_t id)` | Returns `shared_ptr<RdmaDevice>` by index |
| `get_best_dev_idx(int gpu_idx)` | Returns a ranked list of device indices closest to a given GPU |
| `get_numa_node(size_t id)` | Returns the NUMA node of a device for thread pinning |

`get_best_dev_idx` computes PCIe distances between the GPU and each NIC using `uccl::safe_pcie_distance`, then delegates NIC selection to a pluggable strategy.

### Device Selection Strategies

Selection is done through the `RDMADeviceSelectionStrategy` interface ([p2p/rdma/rdma_device.h:9-18]()):

```
virtual selectNICs(dist, gpu_idx) → vector<string>
```

Two concrete strategies exist, chosen at compile time by the `UCCL_P2P_USE_EFA` preprocessor flag:

| Strategy | File | Behavior |
|---|---|---|
| `IBDeviceSelectionStrategy` | `providers/ib/rdma_device_selection_ib.h` | Selects the single NIC with minimum PCIe distance |
| `EFADeviceSelectionStrategy` | `providers/efa/rdma_device_selection_efa.h` | Selects 1–4 EFA NICs (`rdmap*`) based on instance type and GPU index |

The EFA strategy handles specific AWS instance families:

| Instance type | Total EFA NICs | NICs per GPU |
|---|---|---|
| p5 | 32 | 4 (shared, all with min distance) |
| p5e / p5en | 16 | 2 (GPU-affine pair) |
| p6-b200 | 8 | 1 |

Sources: [p2p/rdma/rdma_device.h:85-143](), [p2p/rdma/providers/efa/rdma_device_selection_efa.h:1-59](), [p2p/rdma/providers/ib/rdma_device_selection_ib.h:1-38]()

---

## RdmaContext

`RdmaContext` ([p2p/rdma/rdma_context.h:6-170]()) wraps a single `ibv_context` and its associated `ibv_pd` (protection domain). It is constructed from an `RdmaDevice`.

Key responsibilities:

- Opens the device via `ibv_open_device`
- Allocates a protection domain via `ibv_alloc_pd`
- Detects and caches the appropriate GID index via `detectGid`, supporting InfiniBand (GID 0), RoCE v2 (scans sysfs for `RoCE v2` type), and EFA (GID 0)
- Reads the GID index from environment variable `UCCL_P2P_RDMA_GID_INDEX` if set
- Registers memory via `regMem` (wraps `ibv_reg_mr` with local+remote read/write access flags)
- Deregisters memory via the static `deregMem`
- Creates address handles via `createAH` (used by EFA for UD addressing)

Each `NICEndpoint` holds a fixed-size array of `kNICContextNumber` (= 4) `RdmaContext` instances, one per physical NIC context slot.

Sources: [p2p/rdma/rdma_context.h:1-170](), [p2p/rdma/define.h:47-48]()

---

## Channel Abstraction

### RDMAChannelImpl Interface

`RDMAChannelImpl` ([p2p/rdma/rdma_channel_impl.h:57-91]()) is an abstract base defining:

| Method | Purpose |
|---|---|
| `initQP(ctx, &cq_ex, &qp, local_meta)` | Creates CQ and QP, fills local `ChannelMetaData` |
| `connectQP(qp, ctx, remote_meta)` | Transitions QP to RTR then RTS using remote metadata |
| `poll_once(cq_ex, cq_datas, channel_id, nb_post_recv)` | Drains the CQ into a list of `CQMeta` |
| `lazy_post_recv_wrs_n(qp, n, force)` | Batched posting of receive work requests |
| `setDstAddress(qpx, ah, remote_qpn)` | Sets destination address (no-op for RC, sets UD addr for EFA) |
| `getMaxInlineData()` | Returns max inline send size |
| `initPreAllocResources()` | Pre-allocates receive WR arrays |

Two environment variables tune the IB provider at connection time:
- `UCCL_P2P_RDMA_SL` — service level (default 3)
- `UCCL_P2P_RDMA_TC` — traffic class (default 104)

### IBChannelImpl (InfiniBand / RoCE)

File: [p2p/rdma/providers/ib/rdma_channel_impl_ib.cc]()

Uses **RC (Reliable Connected) QPs**. `initQP` creates the CQ with `ibv_create_cq`, creates the QP via `ibv_create_qp_ex` with `IBV_QPT_RC`, and transitions it to `INIT`. `connectQP` calls `ibrcQP_rtr_rts` which:
1. Reads `port_attr.link_layer` to distinguish RoCE (Ethernet) from native IB
2. On RoCE: sets GRH with remote GID and traffic class
3. On IB: sets `dlid` from remote LID, no GRH
4. Transitions QP to RTR, pre-posts `kMaxRecvWr` receive WRs, then transitions to RTS

Key constants:

| Constant | Value | Role |
|---|---|---|
| `MAX_INLINE_DATA` | 128 bytes | Inline send threshold |
| `TIMEOUT` | 14 | QP timeout exponent |
| `RETRY_CNT` | 7 | Retry count |
| `RNR_RETRY` | 7 | RNR retry count |
| `MAX_CQE` | 1024 | CQ depth |
| `kMaxSendWr` | 1024 | Send queue depth |
| `kMaxRecvWr` | 1024 | Recv queue depth |

### EFAChannelImpl (AWS EFA)

File: [p2p/rdma/providers/efa/rdma_channel_impl_efa.cc]()

Uses **SRD (Scalable Reliable Datagram) QPs** via the `efadv` vendor extension. `initQP` creates the QP with `efadv_create_qp_ex` using `EFADV_QP_DRIVER_TYPE_SRD` and the flag `EFADV_QP_FLAGS_UNSOLICITED_WRITE_RECV` (receive WRs are not consumed on RDMA write with immediate). The QP transitions directly to RTR and RTS without peer info. `connectQP` is a no-op since SRD is connectionless. `setDstAddress` calls `ibv_wr_set_ud_addr` with the pre-created address handle and remote QPN.

Key differences from IBChannelImpl:

| Property | IBChannelImpl | EFAChannelImpl |
|---|---|---|
| QP type | `IBV_QPT_RC` | `IBV_QPT_DRIVER` / SRD |
| Max inline data | 128 bytes | 0 bytes |
| `connectQP` | RTR+RTS transition | No-op |
| Recv WR management | Lazy batch posting | No-op |
| Address setup | No-op (RC is connected) | `ibv_wr_set_ud_addr` |

Sources: [p2p/rdma/providers/ib/rdma_channel_impl_ib.cc](), [p2p/rdma/providers/efa/rdma_channel_impl_efa.cc]()

### RDMAChannel

`RDMAChannel` ([p2p/rdma/rdma_channel.h:25-306]()) composes one `RdmaContext`, one `ibv_qp`, one `ibv_cq_ex`, and a concrete `RDMAChannelImpl` (selected by compile-time flag). The factory function `createRDMAChannelImpl()` returns either `IBChannelImpl` or `EFAChannelImpl`.

Each channel has a numeric `channel_id` (1-based) and maps to a `RdmaContext` via `channelIdToContextId(channel_id)`.

Operations:
- `submitRequest(req)` / `send(req)` / `read(req)` — posts a send/write/read WR via `postRequest`
- `recv(req)` — calls `ibv_post_recv`
- `poll_once(cq_datas)` — drains CQ, fills `CQMeta` vector
- `establishChannel(remote_meta)` — calls `impl_->connectQP`

`postRequest` selects between two internal paths based on vendor ID: `__postRequest_ex` (using the `ibv_wr_*` extended API) and `__postRequest` (using the legacy `ibv_post_send`). Vendor `0x1dd8` uses the legacy path.

**Request type mapping:**

| `SendType` | Verb opcode |
|---|---|
| `Send` | `IBV_WR_RDMA_WRITE_WITH_IMM` |
| `Write` | `IBV_WR_RDMA_WRITE` |
| `Read` | `IBV_WR_RDMA_READ` |

Sources: [p2p/rdma/rdma_channel.h:1-306](), [p2p/rdma/rdma_channel_impl.h:57-103]()

---

## Channel Groups

### ChannelGroup (base)

`ChannelGroup` ([p2p/rdma/rdma_channel_group.h:7-101]()) is a thread-safe map from `channel_id` to `shared_ptr<RDMAChannel>`. It provides two selection algorithms:

- `selectNextChannelRoundRobin()` — increments `last_channel_id_` atomically, wraps at `num_channels`
- `selectNextChannelRandom()` — uses a thread-local `std::mt19937` to pick uniformly

Both return a `pair<channel_id, context_id>`.

### SendChannelGroup

`SendChannelGroup` ([p2p/rdma/rdma_channel_group.h:103-424]()) extends `ChannelGroup` with:

- A `SendControlChannel` that carries back-channel metadata (receive-side buffer info)
- A `RingBuffer` of pending `RDMASendRequest` pointers
- An `AtomicBitmapPacketTrackerMultiAck` for per-`wr_id` completion tracking
- A background `poll_thread_` running `pollingLoop`, started when `setControlChannel` is called (when `auto_start_polling_` is true)

The polling loop does three things each iteration:
1. `pollControlChannel` — drains the control channel for new send-request metadata
2. `processSendRequests` — dequeues from `request_queue_`, pairs with metadata, calls `postChunkedRequest`
3. `pollDataChannels` — polls all data channel CQs, calls `tracker_->acknowledge(wr_id)` on completions

`postChunkedRequest` splits large messages into chunks using `splitMessageToChunks` (chunk size: `kMessageChunkSizeKB` = 256 KB, max `kMaxSplitNum` = 16 chunks) and distributes chunks across channels with round-robin assignment.

### RecvChannelGroup

`RecvChannelGroup` ([p2p/rdma/rdma_channel_group.h:426-599]()) extends `ChannelGroup` with:

- A `RecvControlChannel` for advertising receive buffer info to the sender
- A background `poll_thread_` running `pollingLoop`
- `recv(req)` — selects a channel round-robin, posts recv-buffer info via the control channel
- `check(index)` — non-blocking poll on the control channel for completion

**Channel group polling flow:**

```mermaid
sequenceDiagram
    participant "SendChannelGroup::pollingLoop" as SL
    participant "SendControlChannel" as SCC
    participant "RDMAChannel (data)" as DC
    participant "AtomicBitmapPacketTrackerMultiAck" as TR

    SL->>SCC: "pollControlChannel() - noblockingPoll()"
    SCC-->>SL: "SendReqMeta (remote addr, rkey)"
    SL->>SL: "processSendRequests() - pop from request_queue_"
    SL->>DC: "postChunkedRequest() - ibv_wr_rdma_write / ibv_post_send"
    SL->>DC: "pollDataChannels() - poll_once(cq_datas)"
    DC-->>SL: "CQMeta{wr_id, opcode}"
    SL->>TR: "acknowledge(wr_id)"
```

Sources: [p2p/rdma/rdma_channel_group.h:1-600]()

---

## NICEndpoint

`NICEndpoint` ([p2p/rdma/rdma_endpoint.h:13-827]()) is the top-level class used by the `Endpoint` engine. It holds:

| Member | Type | Role |
|---|---|---|
| `contexts_` | `vector<shared_ptr<RdmaContext>>` | Per-context RDMA state (size = `kNICContextNumber` = 4) |
| `send_channel_groups_` | `unordered_map<uint64_t, SendChannelGroup>` | Per-peer send groups |
| `recv_channel_groups_` | `unordered_map<uint64_t, RecvChannelGroup>` | Per-peer recv groups |
| `oob_server_` | `shared_ptr<EpollServer>` | Listens for incoming channel metadata |
| `oob_client_` | `shared_ptr<EpollClient>` | Sends outgoing channel metadata |
| `allocator_` | `shared_ptr<MemoryAllocator>` | Allocates control channel ring buffers |
| `rank_oob_meta_` | `unordered_map<uint64_t, OOBMetaData>` | Remote IP/port per peer rank |

### Initialization

`NICEndpoint` constructor ([p2p/rdma/rdma_endpoint.h:15-38]()):
1. Calls `initialize_rdma_ctx_for_gpu(gpu_index, device_ids)` which queries `RdmaDeviceManager::instance().get_best_dev_idx(gpu_index)` and constructs `kNICContextNumber` `RdmaContext` objects (cycling across available devices)
2. Starts `EpollServer` on the given port (0 = OS-assigned)
3. Starts `EpollClient`
4. Creates a `MemoryAllocator`

### Connection Setup

Connection setup is initiated by `uccl_connect` (active side) or `uccl_accept` (passive side) and is built on TCP-based out-of-band signaling.

**Connection setup sequence diagram:**

```mermaid
sequenceDiagram
    participant "Caller (active)" as CA
    participant "NICEndpoint (active)" as NEA
    participant "EpollClient" as EC
    participant "EpollServer (passive)" as ES
    participant "NICEndpoint (passive)" as NEP

    CA->>NEA: "uccl_connect(remote_ip, remote_port)"
    NEA->>EC: "connect_to_server(remote_ip, remote_port)"
    EC-->>NEA: "conn_key"
    NEA->>EC: "send_meta(ctrl_meta, callback)"
    EC->>ES: "TCP: MetaInfoToExchange{ChannelType::Control}"
    ES->>NEP: "process_meta(input, output)"
    NEP->>NEP: "allocator_->allocate(kRingBufferSize)"
    NEP->>NEP: "setRecvControlChannel(rank_id, RecvControlChannel)"
    ES-->>EC: "TCP: MetaInfoToExchange{ctrl response}"
    EC->>NEA: "callback -> handle_send_meta_response"
    NEA->>NEA: "setSendControlChannel(rank_id, SendControlChannel)"
    loop "for i in 0..kQpNumPerChannel-1"
        NEA->>EC: "send_meta(channel_meta, callback)"
        EC->>ES: "TCP: MetaInfoToExchange{ChannelType::Normal, channel_id=i+1}"
        ES->>NEP: "process_meta -> RDMAChannel(ctx, meta) -> addOneRecvChannel"
        ES-->>EC: "TCP: MetaInfoToExchange{response}"
        EC->>NEA: "callback -> channel->establishChannel -> addOneSendChannel"
    end
    NEA-->>CA: "ConnID{flow_id=rank_id}"
```

The two phases of `build_connect` ([p2p/rdma/rdma_endpoint.h:96-108]()):
1. `build_control_channel` — sends one `ChannelType::Control` message carrying `SendControlChannel` metadata and the local OOB server port. The passive side creates a `RecvControlChannel` with a ring buffer and establishes a back-connection.
2. `build_normal_channels` — sends `kQpNumPerChannel` (= 4) `ChannelType::Normal` messages in parallel, each establishing one `RDMAChannel` QP pair.

`MetaInfoToExchange` ([p2p/rdma/define.h:606-677]()) is the structure serialized over TCP. It carries `rank_id`, `channel_id`, `ChannelMetaData` (QPN, GID, LID), `RemoteMemInfo` (for control ring buffer), `gpu_id`, and `oob_port`.

### Operations

| Method | Behavior |
|---|---|
| `writeOrRead(req)` | Selects send group by `to_rank_id`, calls `postWriteOrRead` (round-robin channel, chunked) |
| `send(rank_id, req)` | Enqueues into send group's `request_queue_` |
| `recv(rank_id, req)` | Enqueues into recv group, which notifies sender via control channel |
| `checkSendComplete_once(rank_id, wr_id)` | Non-blocking query of `AtomicBitmapPacketTrackerMultiAck` |
| `checkRecvComplete_once(rank_id, index)` | Non-blocking query of `RecvControlChannel` |
| `uccl_regmr(data, len, mr_array)` | Calls `context->regMem` for each context, stores `ibv_mr*` in `MRArray` |
| `uccl_deregmr(mr_array)` | Calls `RdmaContext::deregMem` for each `ibv_mr*` |

Sources: [p2p/rdma/rdma_endpoint.h:96-801]()

---

## Out-of-Band Signaling: EpollServer and EpollClient

Both classes live in `p2p/rdma/epoll_server.h` and `p2p/rdma/epoll_client.h`. They use Linux `epoll` in **edge-triggered** mode.

### EpollServer

`EpollServer` ([p2p/rdma/epoll_server.h:111-464]()) runs a background thread (`event_loop`) that accepts connections, reads length-prefixed frames (`uint32_t len` then payload), calls the registered `MetaHandler`, and writes the response back. Callbacks are invoked synchronously in the event loop. Port 0 triggers OS port assignment, with the actual port retrievable via `get_port()`.

### EpollClient

`EpollClient` ([p2p/rdma/epoll_client.h:26-341]()) maintains persistent connections keyed by `"ip:port"` strings. `connect_to_server` returns a `conn_key`. `send_meta(conn_key, payload, callback)` enqueues a length-framed payload; the `callback` is invoked when the server's response arrives. Multiple requests can be pipelined on one connection using a `queue<ResponseCallback>`.

---

## Key Data Structures

The following structures are defined in [p2p/rdma/define.h]() and [p2p/include/common.h]():

| Structure | Purpose |
|---|---|
| `ChannelMetaData` | QPN + GID (RoCE) + LID (IB) exchanged at QP connect time |
| `RDMASendRequest` | Describes one RDMA operation: local `RegMemBlock`, remote `RemoteMemInfo`, `SendType`, `wr_id`, `imm_data` |
| `RDMARecvRequest` | Describes one receive posting: local `RegMemBlock`, `wr_id` |
| `RegMemBlock` | Local memory region: `addr`, `size`, `MemoryType`, `MRArray` (per-context `ibv_mr*`) |
| `RemoteMemInfo` | Peer's memory: `addr`, `length`, `RKeyArray` (per-context rkeys), `MemoryType` |
| `MRArray` / `RKeyArray` | `ContextArrayT<T>` — fixed array of size `kNICContextNumber` indexed by context ID |
| `CQMeta` | Completion event: `wr_id`, `op_code`, `len`, `imm` |
| `MetaInfoToExchange` | TCP payload for QP handshake: rank, channel type, `ChannelMetaData`, `RemoteMemInfo`, gpu_id, oob_port |
| `SendReqMeta` / `SendReqMetaOnRing` | Ring buffer entries for the control channel carrying remote buffer info |
| `ConnID` | Opaque connection identifier: `context` (pointer cast to rank_id), `flow_id` |
| `FifoItem` | 64-byte descriptor for one-sided read/write operations (addr, size, rkeys in padding bytes) |

**Context ID mapping:**

The helper `channelIdToContextId(channel_id)` ([p2p/rdma/define.h:69-71]()) maps:
- `channel_id == 0` (control) → context 0
- `channel_id >= 1` → `(channel_id - 1) % kNICContextNumber`

This means `kQpNumPerChannel` = 4 normal channels spread evenly across `kNICContextNumber` = 4 contexts.

Sources: [p2p/rdma/define.h:39-712](), [p2p/include/common.h:1-72]()

---

## Configuration Constants

Defined in [p2p/rdma/define.h:39-71]():

| Constant | Value | Role |
|---|---|---|
| `kQpNumPerChannel` | 4 | Normal QPs per peer connection |
| `kNICContextNumber` | 4 | Max RDMA contexts per NICEndpoint |
| `kControlChannelID` | 0 | ID reserved for control QP |
| `kMaxSendWr` | 1024 | Send queue depth per QP |
| `kMaxRecvWr` | 1024 | Recv queue depth per QP |
| `kBatchPostRecvWr` | 32 | Receive WRs posted per batch |
| `kBatchPollCqe` | 32 | CQEs drained per `ibv_poll_cq` call |
| `kMessageChunkSizeKB` | 256 KB | Target chunk size for large messages |
| `kMaxSplitNum` | 16 | Max chunks per message |
| `kRingCapacity` | 16384 | Control channel ring buffer entry count |
| `kInFlightMaxSizeKB` | ~10 GB | Max in-flight bytes before back-pressure |

---

## Provider Selection at Build Time

The compile-time flag `UCCL_P2P_USE_EFA` determines which implementations are compiled in:

```mermaid
graph LR
    A["Build flag: UCCL_P2P_USE_EFA"]
    B["rdma_channel.h: createRDMAChannelImpl()"]
    C["rdma_device.h: createDeviceSelectionStrategy()"]
    D["EFAChannelImpl\nEFADeviceSelectionStrategy\nrdma_channel_impl_efa.cc"]
    E["IBChannelImpl\nIBDeviceSelectionStrategy\nrdma_channel_impl_ib.cc"]

    A -- "defined" --> D
    A -- "not defined" --> E
    B --> D
    B --> E
    C --> D
    C --> E
```

The `RdmaContext::detectGid` method also adapts based on the detected link layer: on `IBV_LINK_LAYER_INFINIBAND` it uses GID 0; on `IBV_LINK_LAYER_ETHERNET` it scans sysfs for a RoCE v2 entry; otherwise it uses `UCCL_P2P_RDMA_GID_INDEX` from the environment or falls back to the provided default.

Sources: [p2p/rdma/rdma_channel.h:9-23](), [p2p/rdma/rdma_device.h:21-34](), [p2p/rdma/rdma_context.h:56-122]()

---

# Page: Memory Registration and Buffer Management

# Memory Registration and Buffer Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/endpoint_wrapper.h](p2p/endpoint_wrapper.h)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/include/common.h](p2p/include/common.h)
- [p2p/rdma/define.h](p2p/rdma/define.h)
- [p2p/rdma/epoll_client.h](p2p/rdma/epoll_client.h)
- [p2p/rdma/epoll_server.h](p2p/rdma/epoll_server.h)
- [p2p/rdma/memory_allocator.h](p2p/rdma/memory_allocator.h)
- [p2p/rdma/rdma_endpoint.h](p2p/rdma/rdma_endpoint.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)

</details>



This page documents the memory registration system for RDMA transfers in UCCL P2P Engine, including buffer tracking via interval trees and support for one-sided READ/WRITE operations. Memory registration is a prerequisite for all RDMA communication, pinning memory buffers in physical RAM to enable direct NIC access without CPU involvement.

For the overall P2P Engine architecture and connection management, see [P2P Engine Architecture](#3.1). For the high-level Python API that uses these primitives, see [P2P Python API](#3.3).

---

## Memory Registration Overview

Memory registration is the process of pinning host or device memory and registering it with the RDMA NIC, producing a memory region handle (`mr_id`) that can be used in subsequent data transfer operations. Registered memory remains valid until explicitly deregistered.

### Registration Flow

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Application<br/>(PyTorch/NumPy)"]
        TENSOR["torch.Tensor<br/>or numpy.array"]
    end
    
    subgraph "Python API"
        COLLECTIVE["collective.register_tensor()"]
        ENDPOINT_REG["Endpoint.reg(ptr, size)"]
    end
    
    subgraph "C++ Core (engine.cc)"
        REG_FUNC["Endpoint::reg()"]
        INTERVAL_ADD["memory_regions.add()"]
        REGMR["unified::uccl_regmr()"]
        MR_STRUCT["MR struct<br/>{mr_id, mhandle}"]
        MR_MAP["mr_id_to_mr_<br/>unordered_map"]
    end
    
    subgraph "Transport Layer"
        RDMA_REGMR["RDMAEndpoint::uccl_regmr()"]
        IBV_REG["ibv_reg_mr()"]
        MHANDLE["Mhandle struct<br/>per-device MRs"]
    end
    
    APP --> TENSOR
    TENSOR --> COLLECTIVE
    COLLECTIVE --> ENDPOINT_REG
    ENDPOINT_REG --> REG_FUNC
    REG_FUNC --> REGMR
    REG_FUNC --> MR_STRUCT
    MR_STRUCT --> MR_MAP
    REG_FUNC --> INTERVAL_ADD
    REGMR --> RDMA_REGMR
    RDMA_REGMR --> IBV_REG
    IBV_REG --> MHANDLE
    MHANDLE --> MR_STRUCT
```

**Registration Process**:
1. Application obtains memory pointer and size
2. Python API extracts `data_ptr()` and size in bytes
3. C++ `Endpoint::reg()` checks for existing registration via interval tree
4. If not registered, calls `unified::uccl_regmr()` to pin memory
5. Transport layer registers with each RDMA device using `ibv_reg_mr()`
6. Returns `mr_id` handle and stores mapping in `mr_id_to_mr_`
7. Adds interval to tracking tree for future lookups

Sources: [p2p/engine.cc:402-429](), [p2p/engine.h:42-45](), [p2p/collective.py:327-343]()

---

## Memory Region Data Structures

### MR Structure

The `MR` struct represents a registered memory region at the endpoint level:

```mermaid
classDiagram
    class MR {
        +uint64_t mr_id_
        +unified::P2PMhandle* mhandle_
    }
    
    class P2PMhandle {
        +uccl::Mhandle* mhandle_
        +MRArray mr_array
    }
    
    class Mhandle {
        +ibv_mr** mr
        +uint32_t n
        +void* addr
        +size_t len
    }
    
    class MRArray {
        +uint32_t rkey[MAX_PATHS]
        +void copyFrom(uint8_t* src)
        +void copyTo(uint8_t* dst)
    }
    
    MR --> P2PMhandle : contains
    P2PMhandle --> Mhandle : wraps
    P2PMhandle --> MRArray : contains
```

| Structure | Purpose | Key Fields |
|-----------|---------|------------|
| `MR` | User-facing memory region handle | `mr_id_`: unique identifier<br/>`mhandle_`: pointer to underlying handle |
| `P2PMhandle` | Unified handle wrapping transport-specific MRs | `mhandle_`: RDMA backend handle<br/>`mr_array`: remote keys for RDMA |
| `Mhandle` | RDMA-specific memory region | `mr`: array of `ibv_mr` pointers (one per device)<br/>`n`: number of memory regions<br/>`addr`, `len`: registered memory range |
| `MRArray` | Remote key array for multi-path RDMA | `rkey[]`: remote keys indexed by path/QP<br/>Serialization helpers for advertisement |

Sources: [p2p/engine.h:42-45](), [p2p/endpoint_wrapper.h:29-32]()

---

## Registration API

### Single Buffer Registration

The `Endpoint::reg()` method registers a contiguous memory buffer:

**C++ API** ([p2p/engine.cc:402-429]()):
```cpp
bool Endpoint::reg(void const* data, size_t size, uint64_t& mr_id)
```

**Key Steps**:
1. Check if engine is initialized; if not, determine GPU index from pointer
2. Call `unified::uccl_regmr()` to register with transport layer
3. Create `MR` struct with allocated `mr_id`
4. Store in `mr_id_to_mr_` map (protected by `mr_mu_` shared_mutex)

**Python API** ([p2p/collective.py:327-336]()):
```python
def _register_memory(self, ptr: int, size: int) -> int
```

Includes interval tree checking to avoid duplicate registrations for overlapping buffers.

### Vectorized Registration

The `Endpoint::regv()` method efficiently registers multiple buffers in one call:

```mermaid
graph LR
    subgraph "Input Vectors"
        DATA_V["data_v[]<br/>pointers"]
        SIZE_V["size_v[]<br/>sizes"]
    end
    
    subgraph "Registration Loop"
        LOOP["for i in 0..n"]
        REGMR_CALL["uccl_regmr(data_v[i], size_v[i])"]
        MR_CREATE["Create MR{id, mhandle}"]
    end
    
    subgraph "Output"
        MR_ID_V["mr_id_v[]<br/>handles"]
        MR_MAP_UPDATE["mr_id_to_mr_ updates"]
    end
    
    DATA_V --> LOOP
    SIZE_V --> LOOP
    LOOP --> REGMR_CALL
    REGMR_CALL --> MR_CREATE
    MR_CREATE --> MR_ID_V
    MR_CREATE --> MR_MAP_UPDATE
```

**Benefits**:
- Amortizes lock acquisition overhead
- Pre-reserves map capacity to avoid rehashing
- Suitable for bulk tensor registration

Sources: [p2p/engine.cc:431-464](), [p2p/engine.h:147-148]()

### Deregistration

The `Endpoint::dereg()` method unpins memory and releases resources:

```cpp
bool Endpoint::dereg(uint64_t mr_id)
```

**Process** ([p2p/engine.cc:466-475]()):
1. Acquire exclusive lock on `mr_mu_`
2. Lookup `MR*` in `mr_id_to_mr_`
3. Call `unified::uccl_deregmr()` to unregister from transport
4. Delete `MR` object
5. Erase from map

**Important**: Applications must not deregister memory while transfers using that `mr_id` are in progress.

---

## Interval Tree Tracking

The Python `CollectiveContext` uses a closed interval tree to efficiently track registered memory regions, enabling detection of overlapping registrations and preventing redundant `reg()` calls.

### ClosedIntervalTree Implementation

```mermaid
classDiagram
    class ClosedIntervalTree {
        -IntervalTree tree
        +add(start, end, data)
        +remove(start, end, data)
        +query_containing(start, end)
        +query_exact_match(start, end, data)
        +query_overlapping(start, end)
        +__iter__()
    }
    
    class Interval {
        +begin: int
        +end: int
        +data: mr_id
    }
    
    ClosedIntervalTree --> Interval : manages
```

**Key Operations** ([p2p/utils.py:114-219]()):

| Method | Complexity | Purpose |
|--------|------------|---------|
| `add(start, end, mr_id)` | O(log n) | Insert closed interval `[start, end]` with associated `mr_id` |
| `query_containing(start, end)` | O(log n + k) | Find all intervals that fully contain `[start, end]` |
| `query_exact_match(start, end, data)` | O(log n + k) | Find intervals with exact boundaries and optional data filter |
| `remove(start, end, data)` | O(log n + k) | Remove specific interval(s) |

### Registration Check Flow

```mermaid
graph TD
    REG_CALL["register_tensor(tensor)"]
    GET_PTR["ptr = tensor.data_ptr()<br/>size = tensor.nbytes"]
    CHECK["_check_register(ptr, size)"]
    QUERY["memory_regions.query_containing(ptr, ptr+size)"]
    
    FOUND{{"Containing<br/>interval<br/>found?"}}
    REUSE["Return existing mr_id"]
    NEW_REG["Call ep.reg(ptr, size)"]
    ADD_INTERVAL["memory_regions.add(ptr, ptr+size, mr_id)"]
    RETURN["Return mr_id"]
    
    REG_CALL --> GET_PTR
    GET_PTR --> CHECK
    CHECK --> QUERY
    QUERY --> FOUND
    FOUND -->|Yes| REUSE
    FOUND -->|No| NEW_REG
    NEW_REG --> ADD_INTERVAL
    ADD_INTERVAL --> RETURN
    REUSE --> RETURN
```

**Example**: Registering a 1GB tensor at address `0x7f0000000000`:
1. Query: `query_containing(0x7f0000000000, 0x7f0040000000)`
2. If no containing interval exists, call `ep.reg()`
3. Add interval: `add(0x7f0000000000, 0x7f003fffffff, mr_id=42)`
4. Future registrations of sub-regions (e.g., tensor slices) reuse `mr_id=42`

**Benefit**: Avoids expensive redundant `ibv_reg_mr()` calls for the same physical pages.

Sources: [p2p/collective.py:327-343](), [p2p/utils.py:114-219](), [p2p/tests/test_util_interval_tree.py:1-219]()

---

## One-Sided RDMA Operations

One-sided RDMA operations (READ/WRITE) allow direct memory access without involving the remote CPU. The remote side must first "advertise" its memory region to provide the necessary metadata.

### Advertisement Mechanism

Before a one-sided operation, the target must advertise its memory region using the `advertise()` method:

```mermaid
sequenceDiagram
    participant Initiator
    participant Target
    participant TargetNIC as Target NIC
    
    Note over Target: Has registered memory<br/>mr_id, addr, len
    
    Initiator->>Target: Request access to memory
    Target->>TargetNIC: advertise(mr_id, addr, len)
    TargetNIC-->>Target: FifoItem{addr, size, rkey[], ...}
    Target->>Initiator: Send FifoItem via TCP/UDS
    
    Note over Initiator: Can now perform<br/>one-sided READ/WRITE
```

**FifoItem Structure** ([p2p/engine.h:62-64]()):
- `addr`: Remote memory address
- `size`: Buffer length
- `rkey`: Remote key for RDMA access (copied from `MRArray`)
- `engine_offset`: Target engine/QP to use
- Additional metadata for multi-path/multi-QP setups

**API** ([p2p/engine.cc:1084-1135]()):
```cpp
bool Endpoint::advertise(uint64_t conn_id, uint64_t mr_id, 
                        void* addr, size_t len, char* out_buf)
```

Serializes remote memory metadata into `out_buf` (size: `sizeof(FifoItem)`) which must be communicated to the initiator out-of-band.

### RDMA READ Operation

```mermaid
graph TB
    subgraph "Initiator Side"
        CALL_READ["read(conn_id, mr_id,<br/>dst, size, slot_item)"]
        CHECK_RC["Check UCCL_RCMODE"]
        CHUNK_LOOP["Split into chunks<br/>(kChunkSize = 1MB)"]
        READ_ASYNC["uccl_read_async()"]
        POLL_UREQ["Poll ureq completion"]
    end
    
    subgraph "RDMA Transport"
        POST_READ["ibv_post_send()<br/>IBV_WR_RDMA_READ"]
        DMA_READ["NIC reads from<br/>remote GPU memory"]
        POLL_CQ["Poll CQ for<br/>completion"]
    end
    
    subgraph "Target Side (Passive)"
        REMOTE_MEM["Remote Memory<br/>(already registered)"]
    end
    
    CALL_READ --> CHECK_RC
    CHECK_RC --> CHUNK_LOOP
    CHUNK_LOOP --> READ_ASYNC
    READ_ASYNC --> POST_READ
    POST_READ --> DMA_READ
    DMA_READ --> REMOTE_MEM
    REMOTE_MEM --> DMA_READ
    DMA_READ --> POLL_CQ
    POLL_CQ --> POLL_UREQ
    POLL_UREQ --> CHUNK_LOOP
```

**Chunking**: Large transfers are split into `kChunkSize` (1MB for RDMA, 1GB for EFA) chunks with pipelined reads. Up to `kMaxInflightChunks` (8) chunks can be in-flight simultaneously ([p2p/engine.cc:823-888]()).

**RC Mode Requirement**: One-sided operations require Reliable Connection (RC) mode, checked via `ucclParamRCMode()`.

### RDMA WRITE Operation

```mermaid
graph TB
    subgraph "Initiator Side"
        CALL_WRITE["write(conn_id, mr_id,<br/>src, size, slot_item)"]
        WRITE_ASYNC["uccl_write_async()"]
        POST_WRITE["ibv_post_send()<br/>IBV_WR_RDMA_WRITE"]
        POLL_WR["Poll write completion"]
    end
    
    subgraph "RDMA Transport"
        DMA_WRITE["NIC writes to<br/>remote GPU memory"]
    end
    
    subgraph "Target Side (Passive)"
        REMOTE_BUF["Remote Buffer<br/>(pre-advertised)"]
        DATA_WRITTEN["Data written<br/>without CPU"]
    end
    
    CALL_WRITE --> WRITE_ASYNC
    WRITE_ASYNC --> POST_WRITE
    POST_WRITE --> DMA_WRITE
    DMA_WRITE --> REMOTE_BUF
    REMOTE_BUF --> DATA_WRITTEN
    DATA_WRITTEN --> POLL_WR
```

**Write Process**:
1. Initiator has `slot_item` from target's `advertise()` call
2. Posts RDMA WRITE work request with local `src` buffer and remote metadata
3. NIC performs DMA directly to remote GPU memory
4. Polls local completion queue; no remote-side notification

Sources: [p2p/engine.cc:823-888](), [p2p/engine.cc:889-1082](), [p2p/engine.h:186-221]()

### Vectorized One-Sided Operations

Vectorized variants (`readv`, `writev`) enable batching multiple READ/WRITE operations:

```mermaid
graph LR
    subgraph "Input Vectors"
        MR_IDS["mr_id_v[]"]
        DST_V["dst_v[] / src_v[]"]
        SIZE_V["size_v[]"]
        SLOT_V["slot_item_v[]"]
    end
    
    subgraph "Chunking & Scheduling"
        FLATTEN["Flatten to sub-chunks<br/>(kChunkSize each)"]
        PIPELINE["Pipeline up to<br/>kMaxInflightChunks"]
    end
    
    subgraph "RDMA Ops"
        WR_ARRAY["Work Request array"]
        CQ_POLL["Poll CQ array"]
    end
    
    MR_IDS --> FLATTEN
    DST_V --> FLATTEN
    SIZE_V --> FLATTEN
    SLOT_V --> FLATTEN
    FLATTEN --> PIPELINE
    PIPELINE --> WR_ARRAY
    WR_ARRAY --> CQ_POLL
```

**Use Case**: Scatter/gather operations for distributed KV cache management, where multiple discontiguous regions must be read/written atomically.

**API Methods**:
- `readv(conn_id, mr_id_v, dst_v, size_v, slot_item_v, num_iovs)` ([p2p/engine.cc:953-1035]())
- `writev(conn_id, mr_id_v, src_v, size_v, slot_item_v, num_iovs)` ([p2p/engine.cc:1137-1220]())

Sources: [p2p/engine.cc:953-1082](), [p2p/engine.h:194-221]()

---

## Memory Registration in C API

The UCCL Engine also exposes a C API for integration with non-Python applications:

### C API Structure

```mermaid
classDiagram
    class uccl_engine_t {
        <<opaque>>
        +Endpoint* endpoint
    }
    
    class uccl_mr_t {
        +uint64_t mr_id
        +uccl_engine_t* engine
    }
    
    class mem_reg_entry_t {
        +uint64_t mr_id
        +size_t size
    }
    
    class mem_reg_info {
        <<static map>>
        +unordered_map~uintptr_t, mem_reg_entry_t~
    }
    
    uccl_engine_t --> uccl_mr_t : creates
    uccl_mr_t --> mem_reg_info : tracked in
```

### C API Functions

| Function | Purpose | Reference |
|----------|---------|-----------|
| `uccl_engine_reg(engine, data, size)` | Register memory, returns `uccl_mr_t*` | [p2p/uccl_engine.cc:447-463]() |
| `uccl_engine_mr_destroy(mr)` | Deregister and free `uccl_mr_t` | [p2p/uccl_engine.cc:598-607]() |
| `find_mem_reg(addr, &base_addr, &mr_id)` | Lookup containing memory region | [p2p/uccl_engine.cc:81-90]() |

**Global Tracking**: The C API maintains a global `mem_reg_info` map ([p2p/uccl_engine.cc:72]()) that maps base addresses to `mem_reg_entry_t` structures. The `find_mem_reg()` helper function searches this map to find the registered region containing any given address, enabling address-to-mr_id resolution.

Sources: [p2p/uccl_engine.cc:81-90](), [p2p/uccl_engine.cc:447-463](), [p2p/uccl_engine.h:106-113]()

---

## Summary

Memory registration in UCCL P2P Engine provides:

1. **Efficient buffer pinning**: Memory regions registered once, reused for multiple transfers
2. **Interval tree tracking**: Avoids redundant registrations for overlapping buffers
3. **One-sided RDMA**: READ/WRITE operations without remote CPU involvement
4. **Vectorized operations**: Batch registration and transfer for improved performance
5. **Multi-API support**: C++ Endpoint API, Python CollectiveContext API, and C API for flexibility

All RDMA transfers require prior memory registration. The interval tree optimization in the Python API significantly reduces registration overhead for applications with dynamic buffer patterns (e.g., PyTorch training with varying batch sizes).

Sources: [p2p/engine.cc:402-1220](), [p2p/engine.h:144-233](), [p2p/collective.py:91-343](), [p2p/utils.py:114-219]()

---

# Page: CollectiveContext Python API

# P2P Python API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_nccl_allgather.py](p2p/benchmarks/benchmark_nccl_allgather.py)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/benchmarks/benchmark_uccl_allgather.py](p2p/benchmarks/benchmark_uccl_allgather.py)
- [p2p/benchmarks/benchmark_uccl_alltoall.py](p2p/benchmarks/benchmark_uccl_alltoall.py)
- [p2p/benchmarks/benchmark_uccl_collective.py](p2p/benchmarks/benchmark_uccl_collective.py)
- [p2p/collective.py](p2p/collective.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [p2p/tests/test_util_interval_tree.py](p2p/tests/test_util_interval_tree.py)
- [p2p/utils.py](p2p/utils.py)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This document covers the Python API for UCCL's P2P communication engine, which provides direct GPU-to-GPU communication with PyTorch tensor integration. The Python API is built on top of the C++ P2P engine using pybind11 bindings and offers both low-level RDMA operations and high-level collective communication patterns.

For information about the underlying C++ architecture and RDMA transport implementation, see page 3.1.

## API Architecture Overview

The P2P Python API consists of two main layers: a low-level `p2p.Endpoint` class for direct RDMA operations, and a high-level `collective.CollectiveContext` class that provides NCCL-like collective operations with automatic connection management.

### API Layer Architecture

```mermaid
graph TB
    subgraph "High-Level API"
        CC["CollectiveContext"]
        INIT["init_collective()"]
        FUNCS["send(), recv(), isend(), irecv()"]
    end
    
    subgraph "Low-Level API"
        EP["p2p.Endpoint"]
        CONN_MGMT["connect(), accept(), connect_local()"]
        XFER["send(), recv(), read(), write()"]
        REG["reg(), regv()"]
    end
    
    subgraph "PyTorch Integration"
        TENSOR["torch.Tensor"]
        DIST["torch.distributed"]
        GPU_MEM["tensor.data_ptr()"]
    end
    
    subgraph "C++ Engine"
        CPP_EP["engine.h/cc Endpoint"]
        RDMA["RDMA Transport"]
        IPC["IPC Transport"]
    end
    
    CC --> EP
    INIT --> CC
    FUNCS --> CC
    CC --> DIST
    CC --> TENSOR
    
    EP --> CONN_MGMT
    EP --> XFER
    EP --> REG
    EP --> CPP_EP
    
    TENSOR --> GPU_MEM
    GPU_MEM --> EP
    
    CPP_EP --> RDMA
    CPP_EP --> IPC
```

The architecture automatically selects between RDMA (remote) and IPC (local) transport based on peer IP addresses, providing transparent high-performance communication across both intra-node and inter-node scenarios.

Sources: [p2p/collective.py:32-84](), [p2p/tests/test_engine_metadata.py:16-24]()

## Low-Level p2p.Endpoint Class

The `p2p.Endpoint` class provides the low-level interface for P2P communication, exposing direct control over RDMA connections, memory registration, and data transfer operations.

### Constructor and Initialization

```python
endpoint = p2p.Endpoint(local_gpu_idx=0, num_cpus=4)
```

The constructor creates an RDMA endpoint with the specified GPU index and CPU thread count. The underlying C++ implementation initializes GPU streams, RDMA devices, and proxy threads for handling asynchronous operations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `local_gpu_idx` | int | GPU device index for this endpoint |
| `num_cpus` | int | Number of CPU threads for RDMA operations |

Sources: [p2p/tests/test_engine_metadata.py:35-41](), [p2p/benchmarks/benchmark_uccl_write.py:185]()

## Connection Management

The API supports two connection types with automatic protocol selection: remote RDMA connections for inter-node communication and local IPC connections for intra-node GPU-to-GPU transfers.

### Connection Establishment Methods

```mermaid
graph TB
    subgraph "Remote RDMA Connections"
        R_CONNECT["connect(ip, gpu_idx, port)"]
        R_ACCEPT["accept()"]
        R_RESULT["Returns: success, conn_id"]
        R_ACCEPT_RESULT["Returns: success, ip, gpu_idx, conn_id"]
    end
    
    subgraph "Local IPC Connections" 
        L_CONNECT["connect_local(gpu_idx)"]
        L_ACCEPT["accept_local()"]
        L_RESULT["Returns: success, conn_id"]
        L_ACCEPT_RESULT["Returns: success, gpu_idx, conn_id"]
    end
    
    subgraph "Transport Layer"
        RDMA_QP["RDMA Queue Pairs"]
        UDS["Unix Domain Sockets"]
        GPU_IPC["CUDA/HIP IPC Handles"]
    end
    
    R_CONNECT --> R_RESULT
    R_ACCEPT --> R_ACCEPT_RESULT
    R_CONNECT --> RDMA_QP
    R_ACCEPT --> RDMA_QP
    
    L_CONNECT --> L_RESULT
    L_ACCEPT --> L_ACCEPT_RESULT
    L_CONNECT --> UDS
    L_ACCEPT --> UDS
    L_CONNECT --> GPU_IPC
```

### Connection API Reference

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| `connect()` | `ip, gpu_idx, remote_port` | `success, conn_id` | Establish remote RDMA connection |
| `accept()` | None | `success, ip, gpu_idx, conn_id` | Accept remote RDMA connection |
| `connect_local()` | `gpu_idx` | `success, conn_id` | Establish local IPC connection |
| `accept_local()` | None | `success, gpu_idx, conn_id` | Accept local IPC connection |

Sources: [p2p/tests/test_engine_send.py:75-77](), [p2p/tests/test_engine_nvlink.py:116-117](), [p2p/tests/test_engine_metadata.py:71-74]()

### Metadata Exchange

Endpoints exchange connection metadata for peer discovery using a compact binary format:

```python
# Get local metadata  
metadata = endpoint.get_metadata()

# Parse peer metadata
ip, port, gpu_idx = p2p.Endpoint.parse_metadata(peer_metadata)

# Connect using parsed metadata
success, conn_id = endpoint.connect(ip, gpu_idx, remote_port=port)
```

The metadata contains IP address (4 bytes for IPv4, 16 bytes for IPv6), port (2 bytes), and GPU index (4 bytes) in network byte order.

| Metadata Format | IPv4 | IPv6 |
|-----------------|------|------|
| Total Size | 10 bytes | 22 bytes |
| IP Address | 4 bytes | 16 bytes |
| Port | 2 bytes | 2 bytes |
| GPU Index | 4 bytes | 4 bytes |

Sources: [p2p/tests/test_engine_metadata.py:37-40](), [p2p/tests/test_engine_send.py:26-38]()

## Memory Registration

Before transferring data, memory regions must be registered with the RDMA subsystem. The API supports both single and vectorized registration:

```python
# Single registration
success, mr_id = endpoint.reg(tensor.data_ptr(), tensor.numel() * 4)

# Vectorized registration
success, mr_id_list = endpoint.regv(ptr_list, size_list)
```

Registration creates `uccl::Mhandle` objects that enable zero-copy RDMA transfers.

Sources: [p2p/pybind_engine.cc:48-74](), [p2p/engine.cc:259-318]()

## Data Transfer Operations

The API provides multiple data transfer patterns supporting both two-sided (send/recv) and one-sided (read/write) operations with synchronous and asynchronous variants.

### Transfer Operation Categories

```mermaid
graph TB
    subgraph "Two-Sided Operations"
        SEND["send(conn_id, mr_id, ptr, size)"]
        RECV["recv(conn_id, mr_id, ptr, size)"]
        SEND_V["sendv() - vectorized"]
        RECV_V["recvv() - vectorized"]
    end
    
    subgraph "One-Sided Operations"
        ADV["advertise(conn_id, mr_id, ptr, size)"]
        READ["read(conn_id, mr_id, ptr, size, fifo_blob)"]
        WRITE["write(conn_id, mr_id, ptr, size, fifo_blob)"]
    end
    
    subgraph "IPC-Specific Operations"
        SEND_IPC["send_ipc(conn_id, ptr, size)"]
        RECV_IPC["recv_ipc(conn_id, ptr, size)"]
        ADV_IPC["advertise_ipc(conn_id, ptr, size)"]
        WRITE_IPC["write_ipc(conn_id, ptr, size, fifo_blob)"]
    end
    
    subgraph "Asynchronous Variants"
        ASYNC_OPS["send_async(), recv_async(), read_async(), write_async()"]
        POLL["poll_async(transfer_id)"]
    end
    
    ADV --> READ
    ADV --> WRITE
    ASYNC_OPS --> POLL
```

### Operation Comparison

| Operation Type | Memory Registration | Remote CPU | Use Case |
|----------------|-------------------|------------|----------|
| `send()/recv()` | Required | Required | Traditional message passing |
| `read()` | Required | Not Required | One-sided data pull |
| `write()` | Required | Not Required | One-sided data push |
| `send_ipc()` | Not Required | Required | Local GPU-to-GPU |

Sources: [p2p/tests/test_engine_send.py:83-87](), [p2p/tests/test_engine_read.py:59-60](), [p2p/tests/test_engine_write.py:59-60](), [p2p/tests/test_engine_nvlink.py:128-130]()

### PyTorch Tensor Integration

The API provides seamless PyTorch tensor integration through direct data pointer access and automatic buffer management:

```python
# Tensor requirements and data pointer access
tensor = torch.ones(1024, dtype=torch.float32).cuda()
assert tensor.is_contiguous()  # Required for efficient RDMA

ptr = tensor.data_ptr()  # Get raw memory pointer
size = tensor.numel() * tensor.element_size()  # Calculate byte size

# Low-level registration and transfer
success, mr_id = endpoint.reg(ptr, size)
success = endpoint.send(conn_id, mr_id, ptr, size)
```

### Buffer Management in CollectiveContext

The high-level API provides automatic buffer management:

```python
def _get_buffer_info(self, tensor: torch.Tensor) -> Tuple[int, int]:
    """Get buffer pointer and size from tensor."""
    if not tensor.is_contiguous():
        raise ValueError("Tensor must be contiguous")
    ptr = tensor.data_ptr()
    size = tensor.numel() * tensor.element_size()
    return ptr, size

def _register_memory(self, ptr: int, size: int) -> int:
    """Register memory and cache the memory region ID."""
    if ptr in self.memory_regions:
        return self.memory_regions[ptr]  # Return cached MR
    
    ok, mr_id = self.ep.reg(ptr, size)
    if not ok:
        raise RuntimeError("Failed to register memory")
    self.memory_regions[ptr] = mr_id  # Cache for reuse
    return mr_id
```

### Supported Tensor Types

| Tensor Location | Memory Registration | Transport | Use Case |
|----------------|-------------------|-----------|----------|
| CPU (`pin_memory=True`) | Required for RDMA | RDMA/IPC | Host memory transfers |
| GPU (`device="cuda:N"`) | Required for RDMA | RDMA/IPC/NVLink | GPU memory transfers |
| GPU (contiguous) | Automatic caching | Optimal performance | Default recommendation |

Sources: [p2p/collective.py:314-331](), [p2p/tests/test_engine_metadata.py:49-53](), [p2p/benchmarks/benchmark_uccl_write.py:22-30]()

## One-Sided RDMA Operations

The API supports one-sided RDMA READ and WRITE operations that bypass remote CPU involvement using advertised memory metadata. These operations use 64-byte `fifo_blob` structures for remote memory addressing.

### One-Sided Operation Flow

```mermaid
graph TB
    subgraph "Memory Owner (Passive Side)"
        REG_MEM["reg(ptr, size) -> mr_id"]
        ADVERTISE["advertise(conn_id, mr_id, ptr, size)"]
        FIFO_BLOB["Returns: success, fifo_blob (64 bytes)"]
        EXCHANGE["Send fifo_blob to peer"]
    end
    
    subgraph "Memory Accessor (Active Side)"
        RECEIVE["Receive fifo_blob from peer"]
        LOCAL_REG["reg(local_ptr, size) -> local_mr_id"]
        READ_OP["read(conn_id, local_mr_id, local_ptr, size, fifo_blob)"]
        WRITE_OP["write(conn_id, local_mr_id, local_ptr, size, fifo_blob)"]
    end
    
    subgraph "Supported Operations"
        RDMA_READ["RDMA READ - Pull data from remote"]
        RDMA_WRITE["RDMA WRITE - Push data to remote"]
        BATCH_OPS["advertisev() / writev() - Vectorized"]
    end
    
    REG_MEM --> ADVERTISE
    ADVERTISE --> FIFO_BLOB
    FIFO_BLOB --> EXCHANGE
    EXCHANGE --> RECEIVE
    RECEIVE --> READ_OP
    RECEIVE --> WRITE_OP
    LOCAL_REG --> READ_OP
    LOCAL_REG --> WRITE_OP
    
    READ_OP --> RDMA_READ
    WRITE_OP --> RDMA_WRITE
```

### One-Sided Operation Examples

```python
# Memory owner side - advertise buffer for remote access
tensor = torch.ones(1024, dtype=torch.float32).cuda()
success, mr_id = endpoint.reg(tensor.data_ptr(), tensor.numel() * 4)
success, fifo_blob = endpoint.advertise(conn_id, mr_id, tensor.data_ptr(), tensor.numel() * 4)

# Send fifo_blob to remote peer (e.g., via torch.distributed)
# ...

# Remote accessor side - perform one-sided operations
local_tensor = torch.zeros(1024, dtype=torch.float32).cuda()  
success, local_mr_id = endpoint.reg(local_tensor.data_ptr(), local_tensor.numel() * 4)

# RDMA READ - pull data from remote buffer
success = endpoint.read(conn_id, local_mr_id, local_tensor.data_ptr(), local_tensor.numel() * 4, fifo_blob)

# RDMA WRITE - push data to remote buffer  
success = endpoint.write(conn_id, local_mr_id, local_tensor.data_ptr(), local_tensor.numel() * 4, fifo_blob)
```

Sources: [p2p/tests/test_engine_read.py:83-85](), [p2p/tests/test_engine_write.py:83-85](), [p2p/benchmarks/benchmark_uccl_write.py:62-66]()

## Asynchronous Operations

All transfer operations have asynchronous variants that return immediately with a transfer ID for completion polling, enabling computation-communication overlap and pipelined transfers.

### Asynchronous Operation Pattern

```mermaid
graph TB
    subgraph "Async Operation Types"
        SEND_ASYNC["send_async(conn_id, mr_id, ptr, size)"]
        RECV_ASYNC["recv_async(conn_id, mr_id, ptr, size)"]
        READ_ASYNC["read_async(conn_id, mr_id, ptr, size, fifo_blob)"]
        WRITE_ASYNC["write_async(conn_id, mr_id, ptr, size, fifo_blob)"]
        IPC_ASYNC["send_ipc_async(), recv_ipc_async()"]
    end
    
    subgraph "Completion Handling"
        POLL["poll_async(transfer_id)"]
        CHECK_DONE["Returns: success, is_done"]
        WAIT_LOOP["While not is_done: poll_async()"]
    end
    
    subgraph "Return Values"
        SUCCESS_TID["Returns: success, transfer_id"]
    end
    
    SEND_ASYNC --> SUCCESS_TID
    RECV_ASYNC --> SUCCESS_TID
    READ_ASYNC --> SUCCESS_TID
    WRITE_ASYNC --> SUCCESS_TID
    IPC_ASYNC --> SUCCESS_TID
    
    SUCCESS_TID --> POLL
    POLL --> CHECK_DONE
    CHECK_DONE --> WAIT_LOOP
```

### Asynchronous Usage Example

```python
# Start multiple async operations
transfer_ids = []
for i in range(num_operations):
    success, transfer_id = endpoint.send_async(conn_id, mr_id, ptr, size)
    if success:
        transfer_ids.append(transfer_id)

# Poll for completion
for transfer_id in transfer_ids:
    while True:
        success, is_done = endpoint.poll_async(transfer_id)
        if not success:
            raise RuntimeError(f"Error polling transfer {transfer_id}")
        if is_done:
            break
```

Sources: [p2p/benchmarks/benchmark_uccl_write.py:99-106](), [p2p/benchmarks/benchmark_uccl_write.py:113-120]()

## Local vs Remote Connection Handling

The API automatically detects whether peers are local or remote based on IP addresses and selects the appropriate transport:

- **Remote connections**: Use RDMA over InfiniBand/RoCE with memory registration
- **Local connections**: Use CUDA/HIP IPC for direct GPU memory access within nodes

### IPC Connection Flow

```mermaid
graph TB
    subgraph "IPC Operations"
        CONNECT_LOCAL["connect_local(gpu_idx)"]
        SEND_IPC["send_ipc(ptr, size)"]
        RECV_IPC["recv_ipc(ptr, size)"]
        IPC_HANDLE["gpuIpcMemHandle_t"]
    end
    
    subgraph "Transport Layer"
        UDS["Unix Domain Socket"]
        GPU_IPC["CUDA/HIP IPC"]
        NVLINK["NVLink/Infinity Fabric"]
    end
    
    CONNECT_LOCAL --> UDS
    SEND_IPC --> IPC_HANDLE
    IPC_HANDLE --> GPU_IPC
    GPU_IPC --> NVLINK
```

Sources: [p2p/pybind_engine.cc:391-439](), [p2p/engine.cc:446-483]()

## High-Level Collective API

The `collective` module provides a NCCL-like interface that wraps the low-level P2P engine with automatic connection management, local/remote detection, and seamless PyTorch integration.

### CollectiveContext Architecture

```mermaid
graph TB
    subgraph "CollectiveContext Class"
        INIT_CTX["__init__(num_cpus, local_gpu_idx)"]
        INIT_CONN["init() - establish full mesh"]
        AUTO_DETECT["_establish_connections()"]
    end
    
    subgraph "Connection Management"
        SEND_CONNS["send_connections[rank]"]
        RECV_CONNS["recv_connections[rank]"] 
        LOCAL_MAP["local_connections[rank] - True/False"]
        METADATA_EXCHANGE["torch.distributed.all_gather()"]
    end
    
    subgraph "Transport Selection"
        IPC_PATH["Local: send_ipc(), recv_ipc()"]
        RDMA_PATH["Remote: send(), recv() with memory registration"]
        AUTO_SWITCH["Automatic based on IP comparison"]
    end
    
    subgraph "Memory Management"
        MR_CACHE["memory_regions: Dict[ptr, mr_id]"]
        REGISTER["register_tensor(tensor)"]
        AUTO_REG["_register_memory(ptr, size)"]
    end
    
    INIT_CTX --> INIT_CONN
    INIT_CONN --> AUTO_DETECT
    AUTO_DETECT --> METADATA_EXCHANGE
    AUTO_DETECT --> SEND_CONNS
    AUTO_DETECT --> RECV_CONNS
    AUTO_DETECT --> LOCAL_MAP
    
    LOCAL_MAP --> IPC_PATH
    LOCAL_MAP --> RDMA_PATH
    AUTO_SWITCH --> IPC_PATH
    AUTO_SWITCH --> RDMA_PATH
    
    REGISTER --> MR_CACHE
    AUTO_REG --> MR_CACHE
```

### Collective API Methods

| Method | Parameters | Description | Memory Registration |
|--------|------------|-------------|-------------------|
| `send()` | `tensor, dst` | Synchronous send | Auto for remote |
| `recv()` | `tensor, src` | Synchronous receive | Auto for remote |
| `isend()` | `tensor, dst` | Asynchronous send | Auto for remote |  
| `irecv()` | `tensor, src` | Asynchronous receive | Auto for remote |
| `wait()` | `transfer_id` | Wait for completion | N/A |
| `test()` | `transfer_id` | Test completion | N/A |
| `register_tensor()` | `tensor` | Manual registration | Forces registration |

### Automatic Local/Remote Detection

The collective API automatically detects peer locality by comparing IP addresses:

```python
# Initialization with automatic GPU index detection
ctx = CollectiveContext(num_cpus=4)  # Derives GPU idx from LOCAL_RANK
ctx.init()  # Establishes full mesh connections

# Automatic transport selection based on peer IP
local_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[self.rank])
for peer_rank in range(world_size):
    if peer_rank != self.rank:
        peer_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[peer_rank])
        self.local_connections[peer_rank] = peer_ip == local_ip
```

### Usage Examples

```python
import torch
import torch.distributed as dist
from uccl import collective

# Initialize distributed and collective
dist.init_process_group(backend="gloo")
collective.init_collective(num_cpus=4)

# Prepare tensors
send_tensor = torch.ones(1024, dtype=torch.float32).cuda()
recv_tensor = torch.zeros(1024, dtype=torch.float32).cuda()

# Register tensors for remote communication (automatic for local)
collective.register_tensor(send_tensor)
collective.register_tensor(recv_tensor)

# Synchronous point-to-point
if dist.get_rank() == 0:
    collective.send(send_tensor, dst=1)
else:
    collective.recv(recv_tensor, src=0)

# Asynchronous operations
transfer_ids = []
transfer_ids.append(collective.isend(send_tensor, dst=1))
transfer_ids.append(collective.irecv(recv_tensor, src=0))

# Wait for completion
collective.wait_all(transfer_ids)
```

### Global Function Interface

The module provides global functions that operate on a default context:

```python
# Global initialization
collective.init_collective(num_cpus=4)

# Global operations
collective.send(tensor, dst)
collective.recv(tensor, src)
req = collective.isend(tensor, dst)
collective.wait(req)

# Cleanup
collective.finalize_collective()
```

Sources: [p2p/collective.py:32-159](), [p2p/collective.py:160-312](), [p2p/collective.py:349-507](), [p2p/collective.py:563-629]()

## Usage Patterns and Examples

### Basic Point-to-Point Transfer

```python
import torch
from uccl import p2p

# Create endpoints
endpoint = p2p.Endpoint(local_gpu_idx=0, num_cpus=4)

# Server side
success, remote_ip, remote_gpu_idx, conn_id = endpoint.accept()

# Client side  
success, conn_id = endpoint.connect("192.168.1.100", remote_gpu_idx=1)

# Prepare tensor
tensor = torch.ones(1024, dtype=torch.float32).cuda()
success, mr_id = endpoint.reg(tensor.data_ptr(), tensor.numel() * 4)

# Transfer data
success = endpoint.send(conn_id, mr_id, tensor.data_ptr(), tensor.numel() * 4)
```

### Vectorized Multi-Tensor Transfer

The API supports efficient transfer of multiple tensors in a single operation:

```python
# Prepare multiple tensors
tensors = [torch.ones(512), torch.ones(1024), torch.ones(256)]
ptr_list = [t.data_ptr() for t in tensors]
size_list = [t.numel() * 4 for t in tensors]

# Register all tensors
success, mr_id_list = endpoint.regv(ptr_list, size_list)

# Transfer all tensors at once
success = endpoint.sendv(conn_id, mr_id_list, ptr_list, size_list, len(tensors))
```

Sources: [p2p/README.md:372-423](), [p2p/pybind_engine.cc:130-159]()

### Benchmark Integration

The benchmarking infrastructure demonstrates real-world usage patterns with performance measurement:

```python
# Throughput measurement
start = time.perf_counter()
for _ in range(iters):
    endpoint.send(conn_id, mr_id, ptr, size)
elapsed = time.perf_counter() - start

throughput_gbps = (total_bytes * 8) / elapsed / 1e9
```

Sources: [p2p/benchmarks/benchmark_uccl_read.py:95-131](), [p2p/benchmarks/benchmark_uccl_collective.py:58-78]()

---

# Page: P2P Benchmarks

# P2P Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nccl_allgather.py](p2p/benchmarks/benchmark_nccl_allgather.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_allgather.py](p2p/benchmarks/benchmark_uccl_allgather.py)
- [p2p/benchmarks/benchmark_uccl_alltoall.py](p2p/benchmarks/benchmark_uccl_alltoall.py)
- [p2p/benchmarks/benchmark_uccl_collective.py](p2p/benchmarks/benchmark_uccl_collective.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/collective.py](p2p/collective.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/tests/test_util_interval_tree.py](p2p/tests/test_util_interval_tree.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [p2p/utils.py](p2p/utils.py)

</details>



This page documents the benchmarking suite for UCCL's point-to-point communication engine. These benchmarks measure bandwidth, latency, and throughput across various communication patterns and backends, providing performance validation and comparison against baseline implementations like NCCL and NIXL.

For information about the P2P Engine architecture itself, see [3.1](#3.1). For the Python API documentation, see [3.3](#3.3).

## Overview

The P2P benchmark suite consists of multiple benchmark scripts that test different aspects of the communication engine:

- **Core P2P benchmarks**: Direct send/recv performance (UCCL, NCCL, NIXL)
- **Collective operation benchmarks**: High-level API performance (send, recv, isend, irecv, batch operations)
- **Pattern-specific benchmarks**: AllGather, AllToAll communication patterns
- **IPC benchmarks**: Local intra-node GPU-to-GPU communication

All benchmarks support multiple operation modes (synchronous, asynchronous, dual-direction) and can measure performance on both RDMA (remote) and IPC (local) transports.

Sources: [p2p/benchmarks/benchmark_uccl.py:1-594](), [p2p/benchmarks/benchmark_nixl.py:1-653](), [p2p/benchmarks/benchmark_uccl_collective.py:1-464]()

---

## Benchmark Ecosystem

```mermaid
graph TB
    subgraph "UCCL Benchmarks"
        UCCL_P2P["benchmark_uccl.py<br/>Direct P2P API"]
        UCCL_COLL["benchmark_uccl_collective.py<br/>Collective API"]
        UCCL_A2A["benchmark_uccl_alltoall.py<br/>AllToAll Pattern"]
        UCCL_AG["benchmark_uccl_allgather.py<br/>AllGather Pattern"]
    end
    
    subgraph "Baseline Benchmarks"
        NCCL_P2P["benchmark_nccl.py<br/>NCCL P2P"]
        NCCL_AG["benchmark_nccl_allgather.py<br/>NCCL AllGather"]
        NIXL["benchmark_nixl.py<br/>NIXL/UCX/Mooncake"]
    end
    
    subgraph "Backend APIs"
        P2P_EP["p2p.Endpoint<br/>C++ Core"]
        COLL_API["collective.py<br/>CollectiveContext"]
        DIST["torch.distributed<br/>NCCL/Gloo"]
        NIXL_API["nixl_agent<br/>NIXL Library"]
    end
    
    UCCL_P2P --> P2P_EP
    UCCL_COLL --> COLL_API
    UCCL_A2A --> COLL_API
    UCCL_AG --> COLL_API
    
    COLL_API --> P2P_EP
    
    NCCL_P2P --> DIST
    NCCL_AG --> DIST
    NIXL --> NIXL_API
    
    style UCCL_P2P fill:#e8f5e9
    style UCCL_COLL fill:#e8f5e9
    style UCCL_A2A fill:#e8f5e9
    style UCCL_AG fill:#e8f5e9
    style NCCL_P2P fill:#fff3e0
    style NCCL_AG fill:#fff3e0
    style NIXL fill:#e1f5ff
```

**Benchmark Ecosystem Architecture**

This diagram shows the relationship between benchmark scripts and the underlying APIs they test. UCCL benchmarks (green) test the UCCL P2P engine through either the direct C++ API or the Python collective API. Baseline benchmarks (orange/blue) test NCCL and NIXL for comparison.

Sources: [p2p/benchmarks/benchmark_uccl.py:1-30](), [p2p/benchmarks/benchmark_uccl_collective.py:1-30](), [p2p/benchmarks/benchmark_nccl.py:1-30](), [p2p/benchmarks/benchmark_nixl.py:1-30]()

---

## Core Benchmark Scripts

### benchmark_uccl.py

The primary benchmark for UCCL's P2P engine, testing direct usage of the `p2p.Endpoint` API.

**Key Features:**
- Tests `send`, `recv`, `send_async`, `recv_async` operations
- Tests vectorized operations: `sendv`, `recvv`, `sendv_async`, `recvv_async`
- Supports IPC mode for local GPU-to-GPU communication
- Dual-direction mode for simultaneous bidirectional transfers
- Configurable message sizes and iteration counts

**Command-line Interface:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--local-gpu-idx` | int | 0 | GPU index for buffer allocation |
| `--num-cpus` | int | 4 | Number of CPU threads for RDMA operations |
| `--device` | choice | gpu | Buffer location (cpu/gpu) |
| `--sizes` | list | [256, 1024, ...] | Message sizes in bytes |
| `--iters` | int | 1000 | Iterations per size (excluding warm-up) |
| `--num-kvblocks` | int | 1 | Number of blocks for vectorized operations |
| `--async-api` | flag | false | Use async operations |
| `--dual` | flag | false | Bidirectional simultaneous transfers |
| `--ipc` | flag | false | Use IPC for local GPU communication |

**Execution Flow:**

```mermaid
graph TD
    START["torchrun launches 2 processes"]
    INIT["dist.init_process_group(backend='gloo')"]
    EP_CREATE["ep = p2p.Endpoint(gpu_idx, num_cpus)"]
    EXCHANGE["Exchange metadata via torch.distributed"]
    
    subgraph "Client (rank 0)"
        CLIENT_CONNECT["ep.connect(ip, gpu, port)"]
        CLIENT_BENCH["For each size:<br/>- Allocate buffer<br/>- ep.reg(ptr, size)<br/>- Warm-up send<br/>- Timed iterations"]
    end
    
    subgraph "Server (rank 1)"
        SERVER_ACCEPT["ep.accept()"]
        SERVER_BENCH["For each size:<br/>- Allocate buffer<br/>- ep.reg(ptr, size)<br/>- Warm-up recv<br/>- Timed iterations"]
    end
    
    START --> INIT
    INIT --> EP_CREATE
    EP_CREATE --> EXCHANGE
    EXCHANGE --> CLIENT_CONNECT
    EXCHANGE --> SERVER_ACCEPT
    CLIENT_CONNECT --> CLIENT_BENCH
    SERVER_ACCEPT --> SERVER_BENCH
```

**Benchmark Execution Flow for benchmark_uccl.py**

This diagram shows the initialization and execution sequence. Both client and server create endpoints, exchange metadata through torch.distributed, establish RDMA connections, then execute timed benchmark iterations.

Sources: [p2p/benchmarks/benchmark_uccl.py:463-594](), [p2p/benchmarks/benchmark_uccl.py:51-148](), [p2p/benchmarks/benchmark_uccl.py:150-244]()

**IPC Mode:**

IPC mode tests local GPU-to-GPU communication using Unix Domain Sockets and GPU memory handles. This mode:
- Uses `connect_local(gpu_idx)` and `accept_local()` instead of RDMA
- Uses `send_ipc`, `recv_ipc`, `send_ipc_async`, `recv_ipc_async` operations
- Does not require memory registration
- Provides baseline for intra-node communication performance

Sources: [p2p/benchmarks/benchmark_uccl.py:362-454](), [p2p/benchmarks/benchmark_uccl.py:518-522]()

**Dual Mode:**

Dual mode tests simultaneous bidirectional transfers:
- Both endpoints act as client and server concurrently
- Uses async operations for overlapping send/recv
- Measures aggregate bidirectional bandwidth

Sources: [p2p/benchmarks/benchmark_uccl.py:247-360](), [p2p/benchmarks/benchmark_uccl.py:513-516]()

---

### benchmark_uccl_collective.py

Benchmarks the high-level `collective.py` API that provides NCCL-like send/recv interface.

**Key Features:**
- Tests `send`, `recv`, `isend`, `irecv` operations
- Tests `batch_isend_irecv` for efficient batch operations
- Ring communication pattern across multiple ranks
- Dual-direction mode for simultaneous send/recv
- Automatic memory registration and connection management

**Usage Modes:**

| Mode | Description | Command Flag |
|------|-------------|--------------|
| Synchronous | Blocking send/recv | Default |
| Asynchronous | Non-blocking isend/irecv | `--async-api` |
| Dual | Simultaneous bidirectional | `--dual` |
| Ring | Ring pattern (N ranks) | `--ring` |

**Ring Benchmark Pattern:**

```mermaid
graph LR
    R0["Rank 0<br/>send→R1<br/>recv←R3"]
    R1["Rank 1<br/>send→R2<br/>recv←R0"]
    R2["Rank 2<br/>send→R3<br/>recv←R1"]
    R3["Rank 3<br/>send→R0<br/>recv←R2"]
    
    R0 -->|send| R1
    R1 -->|send| R2
    R2 -->|send| R3
    R3 -->|send| R0
```

**Ring Communication Pattern**

Each rank sends to the next rank in a ring (rank i → rank (i+1) % world_size) while simultaneously receiving from the previous rank. This tests multi-rank coordination and full-duplex communication.

Sources: [p2p/benchmarks/benchmark_uccl_collective.py:231-327](), [p2p/benchmarks/benchmark_uccl_collective.py:368-373]()

**Initialization Sequence:**

```mermaid
sequenceDiagram
    participant App as "Benchmark Script"
    participant Dist as "torch.distributed"
    participant Coll as "collective.init_collective()"
    participant Ctx as "CollectiveContext"
    participant EP as "p2p.Endpoint"
    
    App->>Dist: init_process_group(backend='gloo')
    App->>Coll: init_collective(num_cpus)
    Coll->>Ctx: Create CollectiveContext
    Ctx->>EP: Create p2p.Endpoint
    Ctx->>Dist: all_gather(metadata)
    Ctx->>Ctx: _establish_connections()
    Note over Ctx: Full mesh connections<br/>(N×N connections)
    Ctx-->>App: Ready for operations
```

**CollectiveContext Initialization Sequence**

The collective API automatically handles distributed initialization, metadata exchange, and connection establishment. Once `init_collective()` returns, all ranks have full mesh connectivity.

Sources: [p2p/benchmarks/benchmark_uccl_collective.py:402-410](), [p2p/collective.py:138-180]()

---

### benchmark_nixl.py

Benchmarks NIXL library with multiple backend support (UCX, Mooncake, UCCL).

**Supported Backends:**

| Backend | Description | Use Case |
|---------|-------------|----------|
| ucx | UCX communication library | General RDMA |
| mooncake | Mooncake backend | Specialized workloads |
| uccl | UCCL through NIXL | Comparison testing |

**Operation Types:**
- `WRITE`: Client writes to server's memory
- `READ`: Client reads from server's memory

**ZMQ Metadata Exchange:**

For Mooncake and UCCL backends, metadata exchange uses ZMQ sockets instead of UCX's built-in mechanism:

```mermaid
graph TD
    subgraph "Server"
        S_INIT["init_zmq(host, port, 'server')<br/>zmq_socket.bind()"]
        S_WAIT["zmq_socket.recv() # START"]
        S_SEND["zmq_socket.send(xfer_descs)"]
        S_TRANSFER["Wait for transfer completion"]
    end
    
    subgraph "Client"
        C_INIT["init_zmq(host, port, 'client')<br/>zmq_socket.connect()"]
        C_START["zmq_socket.send('START')"]
        C_RECV["remote_descs = zmq_socket.recv()"]
        C_TRANSFER["agent.transfer(handle)<br/>Poll until DONE"]
        C_NOTIFY["zmq_socket.send('TRANSFER')"]
    end
    
    S_INIT --> S_WAIT
    C_INIT --> C_START
    C_START -.->|ZMQ| S_WAIT
    S_WAIT --> S_SEND
    S_SEND -.->|ZMQ| C_RECV
    C_RECV --> C_TRANSFER
    C_TRANSFER --> C_NOTIFY
    C_NOTIFY -.->|ZMQ| S_TRANSFER
```

**NIXL Metadata Exchange Flow**

NIXL benchmarks use ZMQ for coordination when using Mooncake/UCCL backends. The server waits for a START signal, sends transfer descriptors, then waits for completion notification.

Sources: [p2p/benchmarks/benchmark_nixl.py:118-170](), [p2p/benchmarks/benchmark_nixl.py:218-235]()

---

### benchmark_uccl_allgather.py

Benchmarks AllGather collective operation using the `collective.py` API.

**AllGather Operation:**

Each rank contributes a tensor of size N, and all ranks receive a concatenated tensor of size N×world_size containing data from all ranks.

**API Variants:**

| API | Operation | Blocking |
|-----|-----------|----------|
| `allgather(send, recv)` | Synchronous allgather | Yes |
| `iallgather(send, recv)` | Asynchronous allgather | No, returns handles |

**Verification Logic:**

```mermaid
graph TD
    START["Each rank creates send_tensor<br/>filled with (rank + 1)"]
    ALLGATHER["collective.allgather(send_tensor, recv_tensor)"]
    VERIFY["For each rank in world_size:<br/>Check recv_tensor[rank*count:(rank+1)*count]"]
    
    PASS{All chunks<br/>match expected<br/>values?}
    SUCCESS["✅ Verification PASSED"]
    FAIL["❌ Verification FAILED<br/>Abort benchmark"]
    
    START --> ALLGATHER
    ALLGATHER --> VERIFY
    VERIFY --> PASS
    PASS -->|Yes| SUCCESS
    PASS -->|No| FAIL
```

**AllGather Verification Flow**

The warmup phase performs correctness verification: each rank fills its send buffer with a rank-specific value, then verifies that the received buffer contains the expected value from each rank.

Sources: [p2p/benchmarks/benchmark_uccl_allgather.py:35-108]()

**Performance Metrics:**

The benchmark reports two bandwidth metrics:

1. **Algorithm Bandwidth (AlgBW)**: Total data output / time
   - Formula: `(world_size × send_bytes) / time`
   - Represents the effective application-level bandwidth

2. **Bus Bandwidth (BusBW)**: Algorithm bandwidth adjusted for ring efficiency
   - Formula: `AlgBW × (world_size - 1) / world_size`
   - Accounts for the ring algorithm's communication pattern

Sources: [p2p/benchmarks/benchmark_uccl_allgather.py:145-188](), [p2p/benchmarks/benchmark_uccl_allgather.py:229-270]()

---

### benchmark_uccl_alltoall.py

Benchmarks AllToAll communication pattern using ring and FCP (Full Connection Pattern) strategies.

**Communication Patterns:**

1. **Ring AllToAll**: Each rank sends to next, receives from previous
2. **FCP AllToAll**: Full connection pattern with randomized communication pairs

**Key Functions:**

| Function | Description | Usage |
|----------|-------------|-------|
| `warmup_all2all_check()` | Verification warmup with correctness check | Pre-benchmark validation |
| `run_ring_p2p()` | Ring pattern benchmark | Fixed neighbor communication |
| `run_fcp_p2p()` | Full connection pattern benchmark | Dynamic pair selection |

**FCP Communication Plans:**

```python
# From p2p/benchmarks/util.py (referenced but not shown)
# get_fcp_comm_plans(world_size, num_iters) returns:
# plans[iteration] = (send_ranks, recv_ranks)
# where send_ranks[my_rank] = target rank to send to
#       recv_ranks[my_rank] = target rank to receive from
```

Sources: [p2p/benchmarks/benchmark_uccl_alltoall.py:113-180](), [p2p/benchmarks/benchmark_uccl_alltoall.py:182-256]()

---

## Benchmark Execution Details

### Memory Registration Flow

```mermaid
graph TD
    ALLOC["Allocate tensor/buffer"]
    CHECK["collective.check_tensor_registered(tensor)"]
    REGISTERED{Already<br/>registered?}
    
    USE_EXISTING["Use existing mr_id"]
    REGISTER["collective.register_tensor(tensor)<br/>- Get ptr, size<br/>- ep.reg(ptr, size)<br/>- Store in interval tree"]
    
    OPERATION["Execute send/recv operation"]
    
    ALLOC --> CHECK
    CHECK --> REGISTERED
    REGISTERED -->|Yes| USE_EXISTING
    REGISTERED -->|No| REGISTER
    USE_EXISTING --> OPERATION
    REGISTER --> OPERATION
```

**Memory Registration and Caching**

The collective API tracks registered memory regions using an interval tree. When a tensor is used for communication, the API checks if the memory region is already registered to avoid redundant registration calls.

Sources: [p2p/collective.py:319-357](), [p2p/collective.py:406-414](), [p2p/utils.py:114-207]()

### Async Operation Flow

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Coll as "collective"
    participant EP as "p2p.Endpoint"
    participant RDMA as "RDMA Hardware"
    
    App->>Coll: isend(tensor, dst)
    Coll->>EP: send_async(conn_id, mr_id, ptr, size)
    EP->>RDMA: Post send work request
    EP-->>Coll: transfer_handle
    Coll-->>App: transfer_handle
    
    Note over App: Application continues execution
    
    App->>Coll: test(transfer_handle)
    Coll->>EP: poll_async(transfer_handle)
    EP->>RDMA: Check completion queue
    RDMA-->>EP: is_done status
    EP-->>Coll: (ok, is_done)
    Coll-->>App: is_done
    
    App->>Coll: wait(transfer_handle)
    loop Until complete
        Coll->>EP: poll_async(transfer_handle)
        EP->>RDMA: Check completion queue
    end
    Coll-->>App: Operation complete
```

**Asynchronous Operation Lifecycle**

Async operations return a handle immediately, allowing the application to continue execution. The application can test for completion non-blocking or wait for completion. The endpoint polls RDMA completion queues to determine when transfers finish.

Sources: [p2p/collective.py:450-490](), [p2p/collective.py:536-564](), [p2p/benchmarks/benchmark_uccl.py:73-97]()

---

## Performance Metrics

### Standard Metrics

All benchmarks report the following metrics:

| Metric | Unit | Formula | Description |
|--------|------|---------|-------------|
| Bandwidth (Gbps) | Gigabits/sec | `(bytes × 8) / time / 1e9` | Network throughput in bits |
| Bandwidth (GB/s) | Gigabytes/sec | `bytes / time / 1e9` | Network throughput in bytes |
| Latency | seconds | `total_time / iterations` | Average transfer time |

### Message Size Formatting

Benchmarks use human-readable size formatting:

```python
def _pretty_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    val = float(num_bytes)
    for u in units:
        if val < 1024 or u == units[-1]:
            return f"{val:.0f} {u}" if u == "B" else f"{val:.1f} {u}"
        val /= 1024
```

Example outputs: `256 B`, `1.0 KB`, `1.0 MB`, `100.9 MB`

Sources: [p2p/benchmarks/benchmark_uccl.py:41-49](), [p2p/benchmarks/benchmark_uccl_collective.py:32-39]()

### Default Test Sizes

Standard message sizes tested (in bytes):

```python
[256, 1024, 4096, 16384, 65536, 262144, 1048576, 10485760, 16777216, 104857600]
```

This progression covers small messages (256 B) to large messages (~100 MB), testing both latency-bound and bandwidth-bound regimes.

Sources: [p2p/benchmarks/benchmark_uccl.py:479-492]()

---

## Usage Examples

### Basic P2P Benchmark

```bash
# Run UCCL P2P benchmark between 2 GPUs
torchrun --nproc_per_node=2 benchmark_uccl.py \
  --local-gpu-idx 0 \
  --device gpu \
  --sizes 1048576,10485760,104857600 \
  --iters 1000
```

### Async API Benchmark

```bash
# Test async operations
torchrun --nproc_per_node=2 benchmark_uccl.py \
  --async-api \
  --sizes 1048576,104857600 \
  --iters 500
```

### IPC (Local GPU) Benchmark

```bash
# Test intra-node GPU-to-GPU communication
torchrun --nproc_per_node=2 benchmark_uccl.py \
  --ipc \
  --sizes 1048576,10485760,104857600 \
  --iters 1000
```

### Dual Direction Benchmark

```bash
# Test simultaneous bidirectional transfers
torchrun --nproc_per_node=2 benchmark_uccl.py \
  --dual \
  --async-api \
  --sizes 1048576,104857600
```

### Collective API Benchmark

```bash
# Test high-level collective API
torchrun --nproc_per_node=2 benchmark_uccl_collective.py \
  --num-cpus 4 \
  --sizes 1048576,10485760,104857600 \
  --iters 100
```

### Ring Benchmark (Multi-rank)

```bash
# Test ring pattern across 4 ranks
torchrun --nproc_per_node=4 benchmark_uccl_collective.py \
  --ring \
  --sizes 1048576,104857600 \
  --iters 100
```

### AllGather Benchmark (Multi-node)

```bash
# Node 0
torchrun --nnodes=2 --nproc_per_node=1 --node-rank=0 \
  --master_addr=<IP> --master_port=19999 \
  benchmark_uccl_allgather.py \
  --sizes 1024,4096,16384,65536,262144,1048576 \
  --num-iters 100

# Node 1
torchrun --nnodes=2 --nproc_per_node=1 --node-rank=1 \
  --master_addr=<IP> --master_port=19999 \
  benchmark_uccl_allgather.py \
  --sizes 1024,4096,16384,65536,262144,1048576 \
  --num-iters 100
```

### NCCL Baseline Comparison

```bash
# Run NCCL benchmark for comparison
torchrun --nproc_per_node=2 benchmark_nccl.py \
  --device gpu \
  --sizes 1048576,10485760,104857600 \
  --iters 1000
```

### NIXL Benchmark with UCCL Backend

```bash
# Server (rank 1)
python benchmark_nixl.py --role server --backend uccl \
  --remote-ip <client_ip> --local-gpu-idx 0 \
  --sizes 1048576,10485760,104857600 --iters 100

# Client (rank 0)
python benchmark_nixl.py --role client --backend uccl \
  --remote-ip <server_ip> --local-gpu-idx 0 \
  --sizes 1048576,10485760,104857600 --iters 100
```

Sources: [p2p/benchmarks/benchmark_uccl.py:463-594](), [p2p/benchmarks/benchmark_uccl_collective.py:336-464](), [p2p/benchmarks/benchmark_uccl_allgather.py:1-10](), [p2p/benchmarks/benchmark_nixl.py:1-16]()

---

## Benchmark Output Format

### Standard Output

Benchmarks produce formatted output with per-size results:

```
[Client] 1.0 MB    :  95.23 Gbps |  11.90 GB/s  | 0.000084 s
[Client] 10.0 MB   : 112.45 Gbps |  14.06 GB/s  | 0.000711 s
[Client] 100.9 MB  : 118.67 Gbps |  14.83 GB/s  | 0.006803 s
```

### CSV Output

AllGather benchmarks save results to CSV files with aligned columns:

```csv
world_size,   dtype,num_iters,  mode,  send_bytes,  recv_bytes, avg_time_ms,algbw_gbps,busbw_gbps
         2, float32,      100,  sync,     1048576,     2097152,      0.1234,   17.0234,   8.5117
         2, float32,      100,  sync,    10485760,    20971520,      0.9876,   21.2345,  10.6172
```

Sources: [p2p/benchmarks/benchmark_uccl.py:144-146](), [p2p/benchmarks/benchmark_uccl_allgather.py:426-485]()

---

## Implementation Details

### Connection Management

The collective API maintains separate connection arrays for send and receive operations:

```python
self.send_connections = [None] * world_size  # indexed by rank
self.recv_connections = [None] * world_size  # indexed by rank
self.local_connections = [False] * world_size  # indexed by rank
```

For each peer, the context establishes:
- One send connection (for sending TO that peer)
- One recv connection (for receiving FROM that peer)

This allows full-duplex communication with proper flow control.

Sources: [p2p/collective.py:84-90](), [p2p/collective.py:149-179]()

### Local vs Remote Connection Detection

The context determines whether a peer is local or remote by comparing IP addresses:

```python
local_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[self.rank])
for peer_rank in range(self.world_size):
    if peer_rank != self.rank:
        peer_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[peer_rank])
        self.local_connections[peer_rank] = peer_ip == local_ip
```

Local connections use IPC (Unix Domain Sockets + GPU memory handles), while remote connections use RDMA.

Sources: [p2p/collective.py:181-198]()

### Batch Operations Optimization

The `batch_isend_irecv()` function optimizes multiple operations by:

1. Separating local (IPC) and remote (RDMA) operations
2. Batching NCCL operations together when using NCCL fallback
3. Returning mixed handle types (int for UCCL, dist.Work for NCCL)

```python
int_handles = []  # UCCL transfer handles
work_handles = [] # NCCL Work objects

# Process each operation
for op in ops:
    if local_connection and use_copy_engine:
        # UCCL IPC async
        handle = ep.send_ipc_async(...)
        int_handles.append(handle)
    elif local_connection:
        # NCCL local
        p2p_ops.append(dist.P2POp(...))
    else:
        # UCCL RDMA async
        handle = ep.send_async(...)
        int_handles.append(handle)

# Batch NCCL operations
if p2p_ops:
    work_handles = dist.batch_isend_irecv(p2p_ops)

return int_handles + work_handles
```

Sources: [p2p/collective.py:622-697]()

### Warm-up Strategy

All benchmarks perform at least one warm-up iteration before timing:

1. **Purpose**: Eliminate first-call overhead (connection setup, buffer allocation, cache warming)
2. **Implementation**: Execute one transfer before starting the timer
3. **Verification**: Some benchmarks use warm-up for correctness checking

Sources: [p2p/benchmarks/benchmark_uccl.py:82-84](), [p2p/benchmarks/benchmark_uccl_collective.py:55-56](), [p2p/benchmarks/benchmark_uccl_allgather.py:144-147]()

---

## Comparison with Baselines

### UCCL vs NCCL

| Aspect | UCCL P2P | NCCL |
|--------|----------|------|
| API Style | Direct endpoint management | Collective-focused |
| Memory Registration | Explicit `reg()` calls | Automatic |
| Connection Model | Peer-to-peer connections | Collective communicator |
| Async Model | Handle-based polling | Work object with `wait()` |
| Multi-rail | Supported via multiple NICs | Backend-dependent |
| IPC Path | Unix sockets + GPU handles | CUDA IPC |

### UCCL vs NIXL

| Aspect | UCCL P2P | NIXL |
|--------|----------|------|
| Backend Support | RDMA, EFA, TCPX | UCX, Mooncake, UCCL |
| Operation Model | Send/Recv | WRITE/READ |
| Descriptor Management | Implicit in endpoints | Explicit register/deserialize |
| Coordination | torch.distributed | ZMQ or UCX metadata |
| Use Case | PyTorch-native | Multi-framework |

Sources: [p2p/benchmarks/benchmark_nccl.py:35-62](), [p2p/benchmarks/benchmark_nixl.py:77-102]()

---

## Troubleshooting

### Common Issues

1. **"No recv connection from rank X"**: Connection not established
   - Check that `init_collective()` completed successfully
   - Verify torch.distributed is initialized
   - Check network connectivity between nodes

2. **Low bandwidth on first iteration**: Warm-up not performed
   - All benchmarks include warm-up iterations
   - First reported result should already be warmed up

3. **"Tensor memory not registered"**: Missing registration for remote peer
   - Call `collective.register_tensor()` for all tensors used with remote ranks
   - Local peers don't require registration (IPC path)

4. **High variance in measurements**: System noise or contention
   - Increase `--iters` for more stable averages
   - Isolate CPU cores for RDMA threads
   - Check for competing network traffic

Sources: [p2p/collective.py:384-414](), [p2p/collective.py:417-448]()

### Debug Environment Variables

While not documented in the benchmark scripts themselves, UCCL respects several environment variables that can be set for debugging:

- `UCCL_ENTROPY`: Control packet spraying entropy
- `UCCL_CHUNK_SIZE_KB`: Set chunk size for transfers
- `NCCL_IB_GID_INDEX`: Select InfiniBand GID index

Sources: [p2p/benchmarks/benchmark_uccl_alltoall.py:15-16]()

---

# Page: UCCL-EP Expert Parallelism

# UCCL-EP Expert Parallelism

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)

</details>



This page provides an overview of the UCCL-EP subsystem: its purpose, hardware support, operational modes, and top-level component architecture. It covers what a caller needs to understand to integrate and reason about UCCL-EP as a whole.

For detailed documentation of sub-components, see:
- [EP Architecture and Buffer API](#4.1) — `Buffer` class internals, memory layout, `EventHandle`
- [Proxy and RDMA System](#4.2) — `Proxy`, `UcclProxy`, `ProxyCtx`, QP lifecycle
- [GPU Kernels and Internode Communication](#4.3) — CUDA kernels, `uccl_ibgda.cuh`, D2H ring design
- [EP Benchmarks and AllToAll](#4.4) — benchmark harnesses, EFA results
- [vLLM Integration](#4.5) — `deep_ep_wrapper`, `launch_vllm.sh`, environment variables

---

## Purpose

UCCL-EP is a portable, hardware-agnostic implementation of **expert-parallel (EP) communication** for Mixture-of-Experts (MoE) models. It provides the same API as [DeepEP](https://github.com/deepseek-ai/DeepEP) and is a drop-in replacement for it, while supporting heterogeneous hardware combinations that DeepEP cannot (e.g., AMD GPUs, AWS EFA NICs, Broadcom NICs).

The two primary operations are **dispatch** (routing tokens from all ranks to their assigned experts) and **combine** (aggregating expert outputs back to the originating ranks). These map onto all-to-all communication patterns at high scale.

---

## Hardware Support

| Dimension | Supported Options |
|---|---|
| GPU vendors | NVIDIA (H100, H200, B200, GH200), AMD (MI300X, MI325X, MI355X) |
| NIC types | NVIDIA ConnectX-7 (InfiniBand/RoCE), AWS EFA (p5, p5e, p5en, p6-b200), Broadcom Thor-2 |
| Intra-node transport | NVLink (NVIDIA), xGMI (AMD) |
| Inter-node transport | RDMA (RC QPs for IB/RoCE, SRD QPs for EFA) |

EFA support is detected at build time by checking for `EFA_HOME=/opt/amazon/efa`. SRD QPs are used for EFA; RC QPs are used for InfiniBand/RoCE.

Sources: [ep/README.md:1-10](), [ep/Makefile:1-15](), [ep/src/rdma.cpp:443-490]()

---

## Operational Modes

UCCL-EP provides two distinct communication modes selected at `Buffer` construction time:

**High-throughput mode** (`low_latency_mode=False`)
- Uses **NVLink for intra-node** transfers and **RDMA for inter-node** transfers
- Targets large batch sizes (e.g., 4096 tokens, 7168 hidden dimension)
- Implemented in [ep/src/internode.cu]()
- Proxy uses `run_sender()` and `run_remote()` as separate threads per proxy

**Low-latency mode** (`low_latency_mode=True`)
- Uses **pure RDMA** for all transfers (both intra- and inter-node)
- Targets inference-time small batches (e.g., 128 tokens)
- Implemented in [ep/src/internode_ll.cu]()
- Proxy uses `run_dual()` — a single thread handling both send and receive

The mode is set in the `Buffer` constructor in [ep/src/uccl_ep.cc:86-94]() and is propagated into the proxy thread selection in [ep/src/uccl_proxy.cpp:151-181]().

---

## Top-Level Architecture

**UCCL-EP Component Architecture**

```mermaid
graph TD
    subgraph "Python Layer"
        PY_BUF["buffer.py::Buffer"]
        BENCH["test_internode.py / test_low_latency.py"]
        UTILS["utils.py: initialize_uccl / destroy_uccl"]
    end

    subgraph "C++ Extension (uccl_ep.cc, pybind11)"
        CPP_BUF["ep::Buffer\nManages NVLink+RDMA memory\nDispatches to GPU kernels"]
        PROXY_REG["g_proxies_by_dev\nDevice-to-proxy registry"]
    end

    subgraph "Proxy Layer"
        UCCL_PROXY["UcclProxy\n(uccl_proxy.hpp)"]
        PROXY["Proxy\n(proxy.hpp)"]
        PROXY_CTX["ProxyCtx\n(proxy_ctx.hpp)"]
    end

    subgraph "GPU Kernels"
        HT_KERN["internode.cu\nnotify_dispatch / notify_combine"]
        LL_KERN["internode_ll.cu\ndispatch / combine"]
        IBGDA["uccl_ibgda.cuh\nnvshmemi_ibgda_put_nbi_warp"]
        D2H["d2h_queue_device.cuh\nD2H ring buffer"]
    end

    subgraph "RDMA Layer"
        RDMA["rdma.cpp\nper_thread_rdma_init\ncreate_per_thread_qp"]
    end

    subgraph "Hardware"
        NVL["NVLink / xGMI"]
        IB["InfiniBand / RoCE RC QPs"]
        EFA["AWS EFA SRD QPs"]
    end

    PY_BUF --> CPP_BUF
    BENCH --> PY_BUF
    UTILS --> UCCL_PROXY
    CPP_BUF --> PROXY_REG
    PROXY_REG --> UCCL_PROXY
    UCCL_PROXY --> PROXY
    PROXY --> PROXY_CTX
    PROXY_CTX --> RDMA
    CPP_BUF --> HT_KERN
    CPP_BUF --> LL_KERN
    HT_KERN --> IBGDA
    LL_KERN --> IBGDA
    IBGDA --> D2H
    D2H --> PROXY
    PROXY --> IB
    PROXY --> EFA
    CPP_BUF --> NVL
```

Sources: [ep/src/uccl_ep.cc:36-82](), [ep/include/uccl_proxy.hpp](), [ep/include/proxy.hpp](), [ep/include/proxy_ctx.hpp](), [ep/src/internode.cu:1-15](), [ep/src/internode_ll.cu:1-15](), [ep/include/uccl_ibgda.cuh:1-50]()

---

## Dispatch Data Flow

**High-Throughput Dispatch: Token Routing Path**

```mermaid
sequenceDiagram
    participant PY as "buffer.py::Buffer.internode_dispatch()"
    participant CPP as "uccl_ep.cc::Buffer::internode_dispatch()"
    participant KERN as "internode.cu::notify_dispatch kernel"
    participant IBGDA as "uccl_ibgda.cuh::nvshmemi_ibgda_put_nbi_warp"
    participant D2H as "d2h_queue_device.cuh D2H ring"
    participant PROXY as "proxy.cpp::Proxy::run_sender()"
    participant NIC as "RDMA NIC (IB/EFA)"
    participant REMOTE as "Remote GPU receive buffer"

    PY->>CPP: "internode_dispatch(x, topk_idx, ...)"
    CPP->>KERN: "launch notify_dispatch kernel on comm_stream"
    KERN->>KERN: "compute dispatch layout, clean buffers"
    KERN->>IBGDA: "nvshmemi_ibgda_put_nbi_warp(dst_ptr, src_ptr, bytes, dst_rank)"
    IBGDA->>D2H: "enqueue RDMA work request into D2H ring"
    D2H-->>PROXY: "CPU polls D2H ring (post_gpu_command)"
    PROXY->>NIC: "ibv_post_send() RDMA write"
    NIC->>REMOTE: "DMA write to remote GPU buffer"
    REMOTE-->>CPP: "GPU polls moe_recv_counter until all tokens received"
    CPP-->>PY: "return recv tensors + EventHandle"
```

Sources: [ep/src/uccl_ep.cc:423-620](), [ep/src/internode.cu:92-225](), [ep/include/uccl_ibgda.cuh:26-80](), [ep/src/proxy.cpp:464-474]()

---

## Component Roles

### `Buffer` — Python Wrapper

`buffer.py::Buffer` is the primary user-facing class. It:
- Accepts a `dist.ProcessGroup`, `num_nvl_bytes`, `num_rdma_bytes`, and `low_latency_mode`
- Calls `initialize_uccl()` from `utils.py` to construct and register `UcclProxy` instances
- Exposes four main operations: `internode_dispatch()`, `internode_combine()`, `low_latency_dispatch()`, `low_latency_combine()`
- Wraps the C++ `ep::Buffer` with Python-friendly tensor types and `EventOverlap` handles

[ep/bench/buffer.py:35-100]()

### `ep::Buffer` — C++ Core

`ep::Buffer` in [ep/src/uccl_ep.cc:84-414]() manages:
- RDMA buffer (`rdma_buffer_ptr`) and NVLink buffers (`buffer_ptrs[]`) via `cudaMalloc` / `hipExtMallocWithFlags`
- IPC handles for NVLink peer access (`cudaIpcGetMemHandle` / `cudaIpcOpenMemHandle`)
- D2H channel handle arrays (`d_handles`, `d_handle_objs`) for GPU-to-CPU signaling
- Stream synchronization through `EventHandle`
- Ranks are split into `rdma_rank = rank / max_nvl_peers` and `nvl_rank = rank % max_nvl_peers`

### `UcclProxy` — Thread Manager

`UcclProxy` in [ep/include/uccl_proxy.hpp]() wraps a `Proxy` instance and:
- Allocates `kChannelPerProxy = 8` D2H ring buffers (one per proxy channel)
- Allocates an atomic buffer (`kAtomicBufferSize = 81960` bytes) for counter synchronization
- Manages a single `std::thread` running one of: `run_sender`, `run_remote`, `run_local`, `run_dual`

### `Proxy` — RDMA Execution

`Proxy` in [ep/include/proxy.hpp]() holds the per-proxy execution logic:
- `init_common()` — opens IB device, registers GPU MR, creates QPs, exchanges `RDMAConnectionInfo` over TCP
- `run_sender()` — polls D2H ring and calls `post_gpu_command()`, then posts RDMA writes via `ibv_post_send()`
- `run_remote()` — polls CQ for incoming RDMA writes, calls `remote_poll_completions()`
- `run_dual()` — combined sender + receiver for low-latency mode
- `run_local()` — handles intra-node peer copies without RDMA

### `ProxyCtx` — Per-Peer RDMA State

`ProxyCtx` in [ep/include/proxy_ctx.hpp]() holds the verbs objects for one peer connection:
- `ibv_context*`, `ibv_pd*`, `ibv_mr*` — device, protection domain, memory region
- `ibv_qp*` (main QP), `ack_qp`, `recv_ack_qp`, `data_qps_by_channel[]`
- `TokenCounter<DispatchTokenKey>` and `TokenCounter<CombineTokenKey>` — per-expert/rank flow tracking
- `remote_addr`, `remote_rkey`, `remote_atomic_buffer_addr`

---

## Proxy Thread Model

**Proxy Threading Model**

```mermaid
graph TD
    subgraph "UcclProxy (uccl_proxy.hpp)"
        U_START["start(Mode)"]
        U_STOP["stop()"]
        U_THREAD["std::thread"]
    end

    subgraph "Proxy (proxy.hpp)"
        INIT["init_common()\nopen IB device\ncreate QPs\nexchange RDMAConnectionInfo via TCP"]
        SENDER["run_sender()\npoll D2H ring\npost_gpu_command()\nibv_post_send() RDMA writes"]
        REMOTE["run_remote()\nremote_poll_completions()\nwrite to GPU recv buffer"]
        LOCAL["run_local()\nNVLink / peer copy\n(intra-node only)"]
        DUAL["run_dual()\ncombined sender+receiver\nfor low-latency mode"]
    end

    subgraph "ProxyCtx (proxy_ctx.hpp)"
        CTX["ibv_qp* qp\nibv_mr* mr\nibv_cq* cq\nTokenCounter dispatch/combine"]
    end

    U_START --> U_THREAD
    U_THREAD --> SENDER
    U_THREAD --> REMOTE
    U_THREAD --> LOCAL
    U_THREAD --> DUAL
    SENDER --> INIT
    REMOTE --> INIT
    LOCAL --> INIT
    DUAL --> INIT
    INIT --> CTX
```

The mode dispatched to is determined by `UcclProxy::Mode`: `Sender`, `Remote`, `Local`, or `Dual`. In normal high-throughput mode, paired ranks use one `Sender` thread and one `Remote` thread. In low-latency mode, each rank runs a single `Dual` thread.

Sources: [ep/src/uccl_proxy.cpp:133-181](), [ep/src/proxy.cpp:445-520](), [ep/include/proxy.hpp:35-100]()

---

## GPU Kernel Files

| File | Mode | Key Kernels |
|---|---|---|
| `ep/src/internode.cu` | High-throughput | `notify_dispatch`, `cached_notify`, `notify_combine` |
| `ep/src/internode_ll.cu` | Low-latency | `dispatch`, `combine`, `clean_low_latency_buffer` |
| `ep/src/intranode.cu` | Intra-node | NVLink barrier and copy operations |
| `ep/include/uccl_ibgda.cuh` | Both | `nvshmemi_ibgda_put_nbi_warp` — GPU-initiated RDMA put |
| `ep/include/ep_utils.cuh` | Both | Warp-level copy, barrier, load/store helpers |
| `ep/include/ep_configs.cuh` | Both | Compile-time constants (`NUM_MAX_NVL_PEERS=8`, `NUM_MAX_RDMA_PEERS=20`) |

`nvshmemi_ibgda_put_nbi_warp` in [ep/include/uccl_ibgda.cuh:26-80]() is the GPU-side function that enqueues an RDMA put request into the D2H ring buffer, which a CPU proxy thread then processes. This is the key abstraction enabling GPU-initiated RDMA without tight coupling to NVSHMEM's IBGDA implementation.

Sources: [ep/src/internode.cu:1-15](), [ep/src/internode_ll.cu:1-50](), [ep/include/ep_configs.cuh]()

---

## Key Compile-Time Constants

From [ep/include/common.hpp]() and [ep/include/ep_configs.cuh]():

| Constant | Value | Meaning |
|---|---|---|
| `kChannelPerProxy` | 8 | D2H ring buffers per `UcclProxy` instance |
| `kNumProxyThs` | 4 | Proxy threads per GPU |
| `kMaxInflightNormal` | 8 | Max outstanding RDMA writes in high-throughput mode |
| `kMaxInflightLowLatency` | 32 | Max outstanding RDMA writes in low-latency mode |
| `NUM_MAX_NVL_PEERS` | 8 | Max GPUs per node connected via NVLink |
| `NUM_MAX_RDMA_PEERS` | 20 | Max remote nodes reachable via RDMA |
| `kAtomicBufferSize` | 81960 bytes | Atomic counter buffer for token counting |
| `NUM_WORKSPACE_BYTES` | 32 MB | Per-GPU workspace for kernel temporaries |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `UCCL_SOCKET_IFNAME` | *(none)* | Network interface for bootstrapping (TCP metadata exchange) |
| `UCCL_IB_GID_INDEX` | `-1` (auto) | GID index for RDMA; set to same value as `NCCL_IB_GID_INDEX` |
| `UCCL_IB_HCA` | *(none)* | Filter RDMA NICs by name (same syntax as `NCCL_IB_HCA`) |
| `UCCL_IB_MAX_INFLIGHT_BYTES` | `SIZE_MAX` | Max bytes in-flight per GPU/NIC |
| `UCCL_IB_MAX_INFLIGHT_NORMAL` | `8` | Max outstanding writes per NIC in high-throughput mode |
| `UCCL_IB_MAX_INFLIGHT_LOW_LATENCY` | `32` | Max outstanding writes per NIC in low-latency mode |
| `UCCL_IB_SL` | `3` (IB) / `8` (EFA) | Service level in RDMA fabric |
| `UCCL_IB_TC` | `104` (IB) / `0` (EFA) | Traffic class in RDMA fabric |
| `UCCL_ATOMICS_USE_HOST_MEMORY` | *(auto)* | Force atomic buffer to pinned host memory (set `1` for Intel irdma NICs) |

For Broadcom Thor-2: set `UCCL_IB_MAX_INFLIGHT_BYTES=1572864 UCCL_IB_MAX_INFLIGHT_NORMAL=1` to avoid CQE error 12.

Sources: [ep/README.md:118-135](), [ep/include/common.hpp:119-142](), [ep/src/rdma.cpp:409-490]()

---

## Performance Characteristics

Measured results from [ep/README.md:139-210]():

**High-throughput mode on AWS p5en (8x H200 + 16x 200 Gb/s EFA)**

| Type | EP Scale | Dispatch BW | Dispatch Latency | Combine BW | Combine Latency |
|---|---|---|---|---|---|
| Intranode | EP8 | 320 GB/s (NVLink) | 500 µs | 319 GB/s (NVLink) | 973 µs |
| Internode | EP16 | 50 GB/s (RDMA) | 1196 µs | 18 GB/s (RDMA) | 6379 µs |
| Internode | EP32 | 54 GB/s (RDMA) | 2022 µs | 43 GB/s (RDMA) | 4899 µs |

**Low-latency mode on AWS p5en (DeepSeek-V3 inference settings: 128 tokens, 7168 hidden, top-8)**

| EP Scale | Dispatch Latency | Dispatch BW | Combine Latency | Combine BW |
|---|---|---|---|---|
| EP16 | 226 µs | 36 GB/s | 293 µs | 48 GB/s |
| EP24 | 386 µs | 20 GB/s | 580 µs | 26 GB/s |
| EP32 | 465 µs | 16 GB/s | 694 µs | 25 GB/s |

---

## Quick Start

Build and install:
```bash
# From the repo root
bash build.sh cuda ep --install

# Or directly from the ep/ directory
cd ep && python setup.py install
```

Verify the import:
```bash
python -c "import torch; import uccl.ep"
```

Run the internode benchmark (2 nodes, 8 GPUs each):
```bash
# Node 0
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=0 \
  --master_addr=<ip> --master_port=12355 \
  bench/test_internode.py --num-tokens=4096 \
  --hidden=7168 --num-topk=8 --num-experts=256

# Node 1
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=1 \
  --master_addr=<ip> --master_port=12355 \
  bench/test_internode.py --num-tokens=4096 \
  --hidden=7168 --num-topk=8 --num-experts=256
```

The `run_ep.sh` script in [ep/bench/run_ep.sh]() wraps these invocations with `ll` (low-latency) and `ht` (high-throughput) modes.

Sources: [ep/README.md:12-50](), [ep/bench/run_ep.sh](), [ep/setup.py:1-50]()

---

# Page: EP Architecture and Buffer API

# EP Architecture and Buffer API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)

</details>



UCCL-EP provides GPU-initiated communication infrastructure for Mixture of Experts (MoE) models, compatible with the DeepEP interface. It enables token dispatch and expert result combining operations across heterogeneous GPUs (NVIDIA, AMD) and NICs (EFA, InfiniBand, Broadcom). The system supports both high-throughput (normal) and low-latency modes, utilizing NVLink for intranode communication and RDMA for internode communication.

The core component is the C++ `Buffer` class in `ep/src/uccl_ep.cc`, exposed to Python via pybind11 as `uccl.ep.Buffer`. A higher-level Python wrapper, `Buffer` in `ep/bench/buffer.py`, is the primary user-facing interface. For the underlying proxy thread and RDMA system, see page 4.2. For GPU kernel details, see page 4.3.

Sources: [ep/README.md:1-4](), [ep/src/uccl_ep.cc:84-281](), [ep/bench/buffer.py:35-70]()

## System Architecture

UCCL-EP is organized into three layers: the Python wrapper (`ep/bench/buffer.py`), the C++ pybind11 extension (`uccl.ep`, implemented in `ep/src/uccl_ep.cc`), and the CUDA kernel layer. The two operation modes are:

- **High-Throughput Mode** (`low_latency_mode=False`): Uses NVLink for intranode forwarding plus RDMA for internode transfer. Optimized for training (4096+ tokens/batch). Achieves 50–70 GB/s internode.
- **Low-Latency Mode** (`low_latency_mode=True`): Pure RDMA without NVLink forwarding. Optimized for inference (128 tokens/batch). Achieves 136–465 µs RTT.

### Layer and Class Diagram

```mermaid
graph TB
    subgraph "Python_Wrapper[ep/bench/buffer.py]"
        PyBuf["Buffer (Python)"]
        PyDispatch["low_latency_dispatch()"]
        PyCombine["low_latency_combine()"]
        PyNormalDispatch["dispatch()"]
        PyNormalCombine["combine()"]
        PyLayout["get_dispatch_layout()"]
    end

    subgraph "C++_Extension[ep/src/uccl_ep.cc via pybind11]"
        CppBuf["Buffer (C++)"]
        InternodeDispatch["internode_dispatch()"]
        InternodeCombine["internode_combine()"]
        LLDispatch["low_latency_dispatch()"]
        LLCombine["low_latency_combine()"]
        GetLayout["get_dispatch_layout()"]
    end

    subgraph "Proxy_Layer[ep/src/uccl_proxy.cpp, ep/src/proxy.cpp]"
        UcclProxy["UcclProxy"]
        Proxy["Proxy"]
        ProxyCtx["ProxyCtx"]
    end

    subgraph "GPU_Kernels[ep/src/internode.cu, ep/src/internode_ll.cu]"
        KernelDispatch["notify_dispatch kernel"]
        KernelLLDispatch["dispatch kernel (LL)"]
        KernelLLCombine["combine kernel (LL)"]
    end

    PyBuf --> CppBuf
    PyDispatch --> LLDispatch
    PyCombine --> LLCombine
    PyNormalDispatch --> InternodeDispatch
    PyNormalCombine --> InternodeCombine
    PyLayout --> GetLayout

    CppBuf --> UcclProxy
    InternodeDispatch --> KernelDispatch
    LLDispatch --> KernelLLDispatch
    LLCombine --> KernelLLCombine

    UcclProxy --> Proxy
    Proxy --> ProxyCtx
```

Sources: [ep/src/uccl_ep.cc:36-84](), [ep/bench/buffer.py:35-70](), [ep/src/uccl_proxy.cpp:13-88](), [ep/src/proxy.cpp:81-443]()

## C++ Buffer Class

The `Buffer` class in `ep/src/uccl_ep.cc` is the core C++ component, exposed to Python via pybind11 as part of the `uccl.ep` extension module. It is instantiated only after `UcclProxy` instances have been registered for the current device via `uccl.ep.register_proxy(device_index, proxies)`.

### Constructor Parameters

[ep/src/uccl_ep.cc:86-94]()

| Parameter | Type | Description |
|-----------|------|-------------|
| `rank` | `int` | Global rank of this process |
| `num_ranks` | `int` | Total number of ranks |
| `num_nvl_bytes` | `long` | NVLink buffer size in bytes (set to 0 for LL-only) |
| `num_rdma_bytes` | `long` | RDMA buffer size in bytes |
| `low_latency_mode` | `bool` | Enable low-latency (pure RDMA) mode |
| `explicitly_destroy` | `bool` | If true, user must call `destroy()` before GC |
| `num_local_ranks` | `int` | Number of GPUs per node; -1 auto-detects via `get_num_max_nvl_peers()` |

### Memory Region Layout

The constructor allocates and arranges several distinct memory regions:

**NVLink Buffer** (when `num_nvl_bytes > 0`): A single `cudaMalloc` (or `hipExtMallocWithFlags` on AMD) covers all intranode communication fields laid out contiguously:

```
[ data buffer (num_nvl_bytes) ]
[ barrier signals (max_nvl_peers × sizeof(int)) ]
[ GPU buffer pointer array (max_nvl_peers × sizeof(void*)) ]
[ GPU barrier signal pointer array (max_nvl_peers × sizeof(int*)) ]
```

[ep/src/uccl_ep.cc:215-248]()

A `cudaIpcGetMemHandle` is obtained for this allocation so that peer GPUs on the same node can map it via CUDA IPC. `ipc_handles[nvl_rank]` stores the local handle; peer handles are exchanged during `init_dist`.

**RDMA Buffer**: Allocated by the registered `UcclProxy` instances. The `Buffer` constructor collects D2H channel ring-buffer addresses from each proxy via `get_d2h_channel_addrs()` and stores GPU-accessible handles as `d_handle_objs` / `d_handles` (managed memory prefetched to device).

[ep/src/uccl_ep.cc:113-165]()

**Workspace**: `NUM_WORKSPACE_BYTES` (32 MB, defined in `ep/include/ep_configs.cuh`) allocated with `cudaMalloc`, used as GPU-side scratch.

**Pinned Host Counters**: `moe_recv_counter`, `moe_recv_expert_counter`, and `moe_recv_rdma_counter` are allocated with `cudaHostAllocMapped` so that both CPU proxy threads and GPU kernels can read/write them.

[ep/src/uccl_ep.cc:257-280]()

### Memory Layout Diagram

```mermaid
graph TB
    subgraph "NVLink_Buffer[cudaMalloc / hipExtMallocWithFlags]"
        NVLData["data region\n(num_nvl_bytes)"]
        NVLBarrier["barrier_signal_ptrs[nvl_rank]\n(max_nvl_peers × int)"]
        NVLBufPtrs["buffer_ptrs_gpu\n(max_nvl_peers × void*)"]
        NVLBarPtrs["barrier_signal_ptrs_gpu\n(max_nvl_peers × int*)"]
    end

    subgraph "RDMA_Region[managed by UcclProxy]"
        RDMABuf["rdma_buffer_ptr\n(num_rdma_bytes, registered ibv_mr)"]
        AtomicBuf["atomic_buffer_ptr\n(kAtomicBufferSize = 81960 bytes)"]
    end

    subgraph "GPU_Scratch[cudaMalloc]"
        Workspace["workspace\n(NUM_WORKSPACE_BYTES = 32 MB)"]
    end

    subgraph "Pinned_Host[cudaHostAllocMapped]"
        RecvCtr["moe_recv_counter\n(int64_t)"]
        ExpertCtr["moe_recv_expert_counter\n(int × NUM_MAX_LOCAL_EXPERTS)"]
        RDMACtr["moe_recv_rdma_counter\n(int)"]
    end

    subgraph "IPC_Handles"
        LocalIPC["ipc_handles[nvl_rank]\ncudaIpcMemHandle_t"]
        PeerIPC["buffer_ptrs[i] (i ≠ nvl_rank)\ncudaIpcOpenMemHandle"]
    end

    NVLData --> LocalIPC
    RDMABuf --> AtomicBuf
```

Sources: [ep/src/uccl_ep.cc:173-281](), [ep/include/ep_configs.cuh:1-7](), [ep/include/common.hpp:59-60]()

### Key Derived Fields

After construction, the `Buffer` computes node-topology fields used throughout the kernel calls:

| Field | Formula | Description |
|-------|---------|-------------|
| `rdma_rank` | `rank / max_nvl_peers` | Which RDMA node this rank belongs to |
| `nvl_rank` | `rank % max_nvl_peers` | Local GPU index within the node |
| `num_rdma_ranks` | `max(1, num_ranks / max_nvl_peers)` | Number of RDMA-connected nodes |
| `num_nvl_ranks` | `min(num_ranks, max_nvl_peers)` | GPUs in intranode group |
| `num_device_sms` | from `cudaGetDeviceProperties` | Total SM count on device |

[ep/src/uccl_ep.cc:202-209]()

---

## Python Buffer Wrapper

`ep/bench/buffer.py` provides the `Buffer` Python class, which is the primary user-facing interface. It wraps the C++ `ep.Buffer` object and handles initialization of the proxy system via `initialize_uccl`.

### Constructor Parameters

[ep/bench/buffer.py:55-90]()

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group` | `dist.ProcessGroup` | — | Torch distributed process group |
| `num_nvl_bytes` | `int` | `0` | NVLink buffer size |
| `num_rdma_bytes` | `int` | `0` | RDMA buffer size |
| `low_latency_mode` | `bool` | `False` | Enables low-latency (pure RDMA) mode |
| `num_qps_per_rank` | `int` | `24` | RDMA QPs per rank; for LL mode, set to `num_local_experts` |
| `allow_nvlink_for_low_latency_mode` | `bool` | `True` | Allow NVLink in LL mode (incompatible with hook-based overlap) |
| `allow_mnnvl` | `bool` | `False` | Allow Multi-Node NVLink |
| `explicitly_destroy` | `bool` | `False` | Require explicit `destroy()` call |
| `is_intranode` | `bool` | `False` | Intranode-only mode (no RDMA) |

The class attribute `num_sms = 20` defines the default SM count for high-throughput kernel launches.

### Buffer API Methods

The Python `Buffer` class exposes the following main operations:

**Layout computation (runs before dispatch):**

`get_dispatch_layout(topk_idx, num_experts, previous_event, async, allocate_on_comm_stream)` — returns `(num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, event)`.

**Low-latency dispatch:**

`low_latency_dispatch(x, topk_idx, num_tokens, num_experts, use_fp8, round_scale, use_ue8m0, cumulative_local_expert_recv_stats, async_finish, return_recv_hook)` — returns `(packed_recv_x, packed_recv_count, handle, event, hook)`.

When `use_fp8=True`, `packed_recv_x` is a tuple `(fp8_tensor, scale_tensor)`.

**Low-latency combine:**

`low_latency_combine(x, topk_idx, topk_weights, handle, use_logfmt, async_finish, zero_copy, return_recv_hook, out)` — returns `(combined_x, event, hook)`.

**High-throughput dispatch/combine:**

`dispatch(x, x_scales, topk_idx, topk_weights, num_tokens_per_rank, num_tokens_per_rdma_rank, is_token_in_rank, num_tokens_per_expert, ...)` — calls `ep.Buffer.internode_dispatch()`.

`combine(x, ...)` — calls `ep.Buffer.internode_combine()`.

Sources: [ep/bench/buffer.py:35-200](), [ep/src/uccl_ep.cc:283-700]()

### Mode Comparison

```mermaid
graph LR
    subgraph "low_latency_mode=False[High-Throughput]"
        HT_NVL["Intranode: NVLink\nAll GPUs on node forward tokens"]
        HT_RDMA["Internode: RDMA\nForwarded by GPU 0 of each node"]
        HT_Target["Use case: Training\n4096+ tokens/batch"]
    end

    subgraph "low_latency_mode=True[Low-Latency]"
        LL_RDMA["Intranode + Internode:\nPure RDMA, no NVLink forwarding"]
        LL_Target["Use case: Inference\n128 tokens/batch"]
    end

    HT_NVL --> HT_RDMA
    HT_RDMA --> HT_Target
    LL_RDMA --> LL_Target
```

Sources: [ep/bench/buffer.py:42-50](), [ep/README.md:118-210]()

## Performance Characteristics

UCCL-EP achieves different performance profiles depending on mode and hardware platform.

### Normal Mode Performance

Normal mode prioritizes throughput with NVLink forwarding and RDMA for internode communication:

**p5en (H200 + 200Gb/s EFA) - DeepSeek-V3 Training Config (4096 tokens/batch, FP8 dispatch, BF16 combine)**

| Type | Dispatch #EP | Dispatch BW & Latency | Combine #EP | Combine BW & Latency |
|------|--------------|------------------------|-------------|----------------------|
| Intranode | 8 | 320 GB/s, 500 µs | 8 | 319 GB/s, 973 µs |
| Internode | 16 | 50 GB/s, 1196 µs | 16 | 18 GB/s, 6379 µs |
| Internode | 32 | 54 GB/s, 2022 µs | 32 | 43 GB/s, 4899 µs |

**p6-b200 (B200 + 400Gb/s EFA)**

| Type | Dispatch #EP | Dispatch BW & Latency | Combine #EP | Combine BW & Latency |
|------|--------------|------------------------|-------------|----------------------|
| Intranode | 8 | 280 GB/s, 571 µs | 8 | 426 GB/s, 727 µs |
| Internode | 16 | 53 GB/s, 1141 µs | 16 | 60 GB/s, 1965 µs |
| Internode | 32 | 53 GB/s, 2072 µs | 32 | 57 GB/s, 3724 µs |

**AMD MI300X with CX7 InfiniBand**

| Type | FP8 Dispatch #EP | FP8 Dispatch BW | BF16 Dispatch #EP | BF16 Dispatch BW | Combine #EP | Combine BW |
|------|------------------|-----------------|-------------------|------------------|-------------|------------|
| Internode | 16 | 71 GB/s | 16 | 81 GB/s | 16 | 54 GB/s |
| Internode | 32 | 57 GB/s | 32 | 60 GB/s | 32 | 57 GB/s |

Sources: [ep/README.md:118-156]()

### Low-Latency Mode Performance

Low-latency mode uses pure RDMA without NVLink forwarding, optimized for inference (128 tokens/batch, FP8 dispatch, BF16 combine):

**AMD MI300X with CX7 InfiniBand**

| Dispatch #EP | Latency | RDMA BW | Combine #EP | Latency | RDMA BW |
|--------------|---------|---------|-------------|---------|---------|
| 8 | 65 µs | 114 GB/s | 8 | 92 µs | 157 GB/s |
| 16 | 136 µs | 55 GB/s | 16 | 207 µs | 70 GB/s |
| 32 | 224 µs | 30 GB/s | 32 | 341 µs | 42 GB/s |

**p6-b200 (B200 + 400Gb/s EFA)**

| Dispatch #EP | Latency | RDMA BW | Combine #EP | Latency | RDMA BW |
|--------------|---------|---------|-------------|---------|---------|
| 16 | 228 µs | 33 GB/s | 16 | 318 µs | 46 GB/s |
| 32 | 406 µs | 19 GB/s | 32 | 617 µs | 24 GB/s |

**p5en (H200 + 200Gb/s EFA)**

| Dispatch #EP | Latency | RDMA BW | Combine #EP | Latency | RDMA BW |
|--------------|---------|---------|-------------|---------|---------|
| 16 | 226 µs | 36 GB/s | 16 | 293 µs | 48 GB/s |
| 32 | 465 µs | 16 GB/s | 32 | 694 µs | 25 GB/s |

Sources: [ep/README.md:158-187]()

## Initialization Flow

Before constructing a `Buffer`, proxies must be started and registered, and distributed group metadata must be exchanged across all ranks.

### `init_dist` and `init_dist_under_torchrun`

Two utility functions in `ep/bench/utils.py` handle distributed process group setup:

| Function | When to use |
|----------|-------------|
| `init_dist(local_rank, num_local_ranks)` | Manual multi-node launch; reads `MASTER_ADDR`, `MASTER_PORT`, `WORLD_SIZE`, `RANK` env vars |
| `init_dist_under_torchrun(local_rank, num_local_ranks)` | Managed by `torchrun`; env vars are set automatically |

Both functions call `dist.init_process_group(backend="nccl", ...)`, set `torch.set_default_dtype(torch.bfloat16)`, and return `(rank, world_size, group)`.

[ep/bench/utils.py:46-89]()

### `initialize_uccl` and `destroy_uccl`

These functions (defined in `ep/bench/utils.py` and re-exported from `ep/bench/buffer.py`) handle the proxy lifecycle. Internally they:

1. Allocate the RDMA scratch buffer (`cudaMalloc` for `num_rdma_bytes`)
2. Create `UcclProxy` instances (one per NIC thread, as configured by `kNumProxyThs`)
3. Exchange peer metadata (rank, IP, RDMA buffer pointer, listen ports) via `dist.all_gather_object`
4. Call `proxy.set_peers_meta()` and start the appropriate proxy thread mode (`start_dual()` for internode, `start_local()` for intranode)
5. Register the proxy list with `uccl.ep.register_proxy(device_index, proxies)`

[ep/bench/utils.py:113-142](), [ep/src/uccl_proxy.cpp:128-181]()

### Full Initialization Sequence

```mermaid
sequenceDiagram
    participant App as "User Code"
    participant Utils as "ep/bench/utils.py"
    participant UcclProxy as "UcclProxy (ep/src/uccl_proxy.cpp)"
    participant Dist as "dist (torch.distributed)"
    participant CppBuf as "Buffer C++ (ep/src/uccl_ep.cc)"

    App->>Utils: "init_dist_under_torchrun(local_rank, ...)"
    Utils->>Dist: "init_process_group(backend=nccl)"
    App->>Utils: "initialize_uccl(scratch, num_rdma_bytes, rank, ...)"
    Utils->>UcclProxy: "UcclProxy(...) × kNumProxyThs"
    Utils->>Dist: "all_gather_object(peer metadata)"
    Utils->>UcclProxy: "set_peers_meta() + start_dual()"
    Utils->>App: "register_proxy(device_index, proxies)"
    App->>CppBuf: "Buffer(rank, num_ranks, nvl_bytes, rdma_bytes, ...)"
    CppBuf->>CppBuf: "cudaMalloc NVLink buffer"
    CppBuf->>CppBuf: "cudaIpcGetMemHandle"
    CppBuf->>Dist: "all_gather_object(IPC handles)"
    CppBuf->>CppBuf: "cudaIpcOpenMemHandle for peer buffers"
    App->>App: "Run dispatch / combine"
    App->>CppBuf: "buffer.destroy()"
    App->>Utils: "destroy_uccl(proxies, workers)"
    Utils->>UcclProxy: "proxy.stop()"
```

Sources: [ep/bench/utils.py:75-142](), [ep/src/uccl_ep.cc:94-172](), [ep/src/uccl_proxy.cpp:128-181]()

---

## EventHandle Synchronization

`EventHandle` is a C++ CUDA event wrapper exposed via pybind11 in `uccl.ep`. It is the primary mechanism for stream synchronization between the communication stream (`comm_stream`) and the compute stream.

The `Buffer` C++ constructor creates a dedicated high-priority `comm_stream` via `at::cuda::getStreamFromPool(/*isHighPriority=*/true)`. All dispatch and combine kernels launch on this stream, and an `EventHandle` is returned to the caller to synchronize with the default compute stream.

[ep/src/uccl_ep.cc:92-94]()

### EventOverlap Wrapper

`ep/bench/utils.py` wraps `EventHandle` in the `EventOverlap` class, which supports Python `with` syntax for convenient stream waiting:

[ep/bench/utils.py:195-250]()

| Method | Description |
|--------|-------------|
| `EventOverlap(event, extra_tensors)` | Stores an `EventHandle` and optional tensors for stream recording |
| `current_stream_wait()` | Calls `event.current_stream_wait()` on the stored handle |
| `__exit__()` | Automatically calls `current_stream_wait()` when exiting a `with` block |

### Async Operation Pattern

When `async_finish=True` is passed to dispatch or combine:

1. The operation launches on `comm_stream` and returns immediately with an `EventHandle`.
2. The caller performs other GPU work on the compute stream.
3. Before consuming the results, the caller calls `event.current_stream_wait()` or enters an `EventOverlap` context.

When `return_recv_hook=True`, a Python callable `hook` is returned instead. Calling `hook()` internally calls `current_stream_wait()` and can be used with CUDA graph capture.

Sources: [ep/bench/utils.py:195-250](), [ep/bench/buffer.py:14-16](), [ep/src/uccl_ep.cc:283-353]()

## Configuration and Performance Tuning

The `uccl.ep.Config` class (exposed from C++) controls chunking and SM allocation for high-throughput (normal) mode operations.

### Config Parameters

```mermaid
graph LR
    subgraph "uccl.ep.Config"
        ConfigObj["Config(num_sms, nvl_chunk_send, nvl_buf, rdma_chunk_send, rdma_buf)"]
        NumSMs["num_sms\nSMs assigned to kernels"]
        NVLSend["num_max_nvl_chunked_send_tokens\nNVLink send chunk size"]
        NVLBuf["nvl_buffer_size\nMax NVLink buffer tokens"]
        RDMASend["num_max_rdma_chunked_send_tokens\nRDMA send chunk size"]
        RDMABuf["rdma_buffer_size\nMax RDMA buffer tokens"]
    end

    ConfigObj --> NumSMs
    ConfigObj --> NVLSend
    ConfigObj --> NVLBuf
    ConfigObj --> RDMASend
    ConfigObj --> RDMABuf
```

| Parameter | Typical Value | Description |
|-----------|--------------|-------------|
| `num_sms` | 20–24 | SMs allocated to communication kernels |
| `num_max_nvl_chunked_send_tokens` | 8–44 | NVLink send chunk size in tokens |
| `nvl_buffer_size` | 512–720 | NVLink buffer capacity in tokens |
| `num_max_rdma_chunked_send_tokens` | 8–32 | RDMA send chunk size in tokens |
| `rdma_buffer_size` | 128–512 | RDMA buffer capacity in tokens |

The `Config` object also provides helper methods:
- `get_nvl_buffer_size_hint(hidden_bytes, num_ranks)` — returns required NVLink buffer bytes
- `get_rdma_buffer_size_hint(hidden_bytes, num_ranks)` — returns required RDMA buffer bytes
- `get_low_latency_rdma_size_hint(num_tokens, hidden, num_ranks, num_experts)` — returns RDMA buffer bytes for LL mode

Example usage from `ep/bench/test_internode.py`:

```python
config = Config(num_sms, 8, 512, 16, 512)
num_nvlink_bytes = align_buffer(config.get_nvl_buffer_size_hint(hidden_bytes, num_ranks))
num_rdma_bytes   = align_buffer(config.get_rdma_buffer_size_hint(hidden_bytes, num_ranks))
```

[ep/bench/test_internode.py:62-77]()

### Compile-Time Constants (`ep_configs.cuh`)

Key limits defined at compile time in `ep/include/ep_configs.cuh`:

| Constant | Value | Description |
|----------|-------|-------------|
| `NUM_MAX_NVL_PEERS` | 8 | Maximum GPUs per node for NVLink |
| `NUM_MAX_RDMA_PEERS` | 20 | Maximum RDMA peer nodes |
| `NUM_WORKSPACE_BYTES` | 32 MB | GPU scratch workspace size |
| `NUM_BUFFER_ALIGNMENT_BYTES` | 128 | Required buffer alignment |

[ep/include/ep_configs.cuh:1-7]()

Sources: [ep/bench/test_internode.py:62-77](), [ep/include/ep_configs.cuh:1-7](), [ep/bench/buffer.py:52-54]()

## Internode Low-Latency Operations

For multi-node deployments, the system provides specialized internode low-latency operations that minimize communication overhead across RDMA networks.

### Low-Latency Kernel Interface

The internode low-latency module exposes dispatch and combine operations optimized for RDMA communication:

```mermaid
graph TD
    subgraph "Internode LL Interface"
        LL_DISPATCH["internode_ll::dispatch()<br/>Low-latency token dispatch"]
        LL_COMBINE["internode_ll::combine()<br/>Low-latency result combine"]
        LL_CLEAN["clean_low_latency_buffer()<br/>Buffer cleanup"]
    end
    
    subgraph "RDMA Integration" 
        RING_ADDRS["ring_addrs<br/>RDMA address ring"]
        IPC_BASE["ipc_base_ptrs<br/>IPC memory bases"]
        ATOMIC_BUF["atomic_buffer_ptr<br/>Atomic operations"]
        RDMA_BUF["rdma_buffer_ptr<br/>Communication buffer"]
    end
    
    subgraph "Parameters"
        TOKENS["Token data<br/>Input/output tensors"]
        TOPOLOGY["Topology info<br/>Ranks and experts"]
        WORKSPACE["workspace<br/>Temporary memory"]
        STREAM["cudaStream_t<br/>Execution stream"]
    end
    
    LL_DISPATCH --> RING_ADDRS
    LL_COMBINE --> IPC_BASE
    LL_CLEAN --> ATOMIC_BUF
    LL_DISPATCH --> TOKENS
    LL_COMBINE --> TOPOLOGY
    LL_CLEAN --> WORKSPACE
    LL_DISPATCH --> STREAM
```

The internode operations integrate with RDMA ring buffers and IPC memory management to provide efficient cross-node communication.

Sources: [ep/include/internode_ll.cuh:9-41]()

### Buffer Management and Cleanup

The system includes sophisticated buffer management with automatic cleanup and resource reclamation:

| Operation | Purpose | Key Parameters |
|-----------|---------|----------------|
| `clean_low_latency_buffer` | Clean atomic counters | `clean_0`, `num_clean_int_0`, `clean_1`, `num_clean_int_1` |
| `reset_rdma_buffer` | Reset communication buffers | Buffer state reset |
| `destroy` | Release all resources | Complete cleanup |

The cleanup operations ensure proper resource management across GPU memory, RDMA buffers, and IPC handles.

Sources: [ep/bench/buffer.py:146-165](), [ep/include/internode_ll.cuh:11-12]()

---

# Page: Proxy and RDMA System

# Proxy and RDMA System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)

</details>



The EP subsystem's proxy layer bridges GPU kernels and the RDMA network. GPU dispatch/combine kernels write transfer commands into D2H ring buffers; CPU proxy threads drain those rings and post InfiniBand verbs calls. This page covers the `UcclProxy` and `Proxy` classes, the `ProxyCtx` context structure, the four proxy thread modes, and how RDMA connections are established via TCP-based `RDMAConnectionInfo` exchange.

Related pages: see page 4.1 for the `Buffer` API that creates proxies, and page 4.3 for the GPU kernels that enqueue commands into the D2H rings.

## Class Hierarchy and Ownership

Two classes manage proxy lifecycle: `UcclProxy` and its inner `Proxy`.

- **`UcclProxy`** ([ep/include/uccl_proxy.hpp:15-75](), [ep/src/uccl_proxy.cpp:13-181]()) — the pybind11-exposed object. It owns one `Proxy`, one or more D2H ring-buffer channels (`d2h_channel_addrs_`), and an `atomic_buffer_ptr_`. It exposes `start_sender()`, `start_remote()`, `start_local()`, `start_dual()`, and `stop()`.
- **`Proxy`** ([ep/include/proxy.hpp:35-110](), [ep/src/proxy.cpp:81-543]()) — owns the per-peer `ProxyCtx` instances, the RDMA lifecycle, and the `run_*` thread bodies. Configuration is passed via `Proxy::Config`.

Each `UcclProxy` allocates `kChannelPerProxy` (8) D2H queue slots ([ep/include/common.hpp:66]()). In normal mode, `kNumProxyThs` (4) `UcclProxy` instances are created per GPU, giving 4×8 = 32 D2H channels total.

**Class hierarchy diagram:**

```mermaid
graph TD
    UcclProxy["UcclProxy\n(uccl_proxy.hpp)"]
    Proxy["Proxy\n(proxy.hpp)"]
    ProxyCtx["ProxyCtx\n(proxy_ctx.hpp)\none per remote peer"]
    PeerMeta["PeerMeta\nip, ptr, listen_ports"]
    D2H["D2H ring channels\n(kChannelPerProxy each)"]
    AtomicBuf["atomic_buffer_ptr_\n(kAtomicBufferSize)"]

    UcclProxy -->|"owns"| Proxy
    UcclProxy -->|"owns"| D2H
    UcclProxy -->|"owns (thread_idx==0)"| AtomicBuf
    Proxy -->|"ctxs_for_all_ranks_"| ProxyCtx
    Proxy -->|"peers_"| PeerMeta
```

Sources: [ep/include/uccl_proxy.hpp:15-75](), [ep/include/proxy.hpp:35-110](), [ep/src/uccl_proxy.cpp:13-88]()

## ProxyCtx Structure

`ProxyCtx` ([ep/include/proxy_ctx.hpp:63-180]()) is the per-peer RDMA context. One instance lives in `Proxy::ctx_` (the main context) and one per peer in `Proxy::ctxs_for_all_ranks_`. All per-peer contexts share the same `ibv_context`, `ibv_pd`, and `ibv_mr` but have distinct Queue Pairs.

| Field | Type | Purpose |
|---|---|---|
| `context` | `ibv_context*` | Open IB device handle |
| `pd` | `ibv_pd*` | Protection domain |
| `mr` | `ibv_mr*` | GPU buffer memory region |
| `cq` / `cq_ex` | `ibv_cq*` / `ibv_cq_ex*` | Completion queue (shared per proxy) |
| `qp` | `ibv_qp*` | Main data Queue Pair |
| `ack_qp` / `recv_ack_qp` | `ibv_qp*` | Acknowledgement Queue Pairs |
| `data_qps_by_channel` | `vector<ibv_qp*>` | Per-channel QPs (normal mode) |
| `rkey` / `remote_rkey` | `uint32_t` | Local and remote memory region keys |
| `remote_addr` / `remote_len` | `uintptr_t` / `uint64_t` | Remote GPU buffer base and size |
| `atomic_buffer_mr` | `ibv_mr*` | MR for `atomic_buffer_ptr_` |
| `atomic_old_values_buf` / `_mr` | `uint64_t*` / `ibv_mr*` | Scratch buffer for native RDMA atomics |
| `gpu_mr_chunks` | `vector<MRChunk>` | Chunked MR entries (DMA-BUF path) |
| `numa_node` | `int` | NUMA node of selected NIC |
| `progress_run` | `atomic<bool>` | Proxy thread run flag |

`TokenCounter<Key>` ([ep/include/proxy_ctx.hpp:10-24]()) is a lightweight `map<Key, size_t>` wrapper used to track dispatch and combine token counts per (rank, expert, buffer_idx) tuple.

Sources: [ep/include/proxy_ctx.hpp:10-180]()

## D2H Channel Ring Buffers

GPU kernels communicate transfer commands to CPU proxies through D2H (Device-to-Host) channels. When `USE_MSCCLPP_FIFO_BACKEND` is defined (the default, [ep/include/common.hpp:32]()), each channel is a `mscclpp::Fifo`; otherwise it is a custom `HostD2HHandle` ring.

Each `TransferCmd` entry carries:

| Field | Purpose |
|---|---|
| `cmd_type` | `CmdType::WRITE`, `BARRIER`, or `QUIET` with combine/buffer_idx flags |
| `req_rptr` | Remote GPU buffer address (offset from base) |
| `req_lptr` | Local GPU buffer address |
| `bytes` | Transfer size |
| `dst_rank` | Destination global rank |
| `expert_idx` | Expert index (low-latency mode) |
| `atomic_offset` / `atomic_val` | Atomic operation parameters (normal mode) |

**D2H channel selection from GPU:** `nvshmemi_ibgda_put_nbi_warp` maps `expert_idx % num_d2h_channel_addrs` to a specific proxy thread and per-thread channel slot [ep/include/uccl_ibgda.cuh:36-42]().

**D2H channel flow diagram:**

```mermaid
graph LR
    GK["GPU kernel\nnvshmemi_ibgda_put_nbi_warp"]
    D2H["D2HHandle / mscclpp::Fifo\n(kChannelPerProxy per UcclProxy)"]
    POST["Proxy::post_gpu_command()\ndequeues TransferCmd entries"]
    RDMA["post_rdma_async_batched()\nibv_post_send"]
    COMP["poll_cq_dual() /\nlocal_poll_completions()"]
    NOTIFY["Proxy::notify_gpu_completion()\nadvances tail"]

    GK -->|"atomic_set_and_commit"| D2H
    D2H -->|"fifo->poll()"| POST
    POST --> RDMA
    RDMA --> COMP
    COMP --> NOTIFY
    NOTIFY -->|"volatile_clear_cmd_type\nmark_acked"| D2H
```

Sources: [ep/include/uccl_ibgda.cuh:26-75](), [ep/src/proxy.cpp:603-601](), [ep/src/proxy.cpp:545-601](), [ep/src/uccl_proxy.cpp:28-41]()

## Proxy Thread Modes

`UcclProxy::start_*()` launches a background `std::thread` that calls one of four `Proxy::run_*()` methods. The mode is determined at startup and does not change.

**Thread mode summary:**

| Mode | Method | Init Called | Primary Loop Work |
|---|---|---|---|
| `Sender` | `run_sender()` | `init_sender()` | `local_poll_completions`, `notify_gpu_completion`, `post_gpu_command` |
| `Remote` | `run_remote()` | `init_remote()` | `remote_poll_completions`, `apply_pending_updates` |
| `Local` | `run_local()` | `init_common()` | NVLink-only intra-node transfers |
| `Dual` | `run_dual()` | `init_common()` | Combined send+recv: `poll_cq_dual`, `notify_gpu_completion`, `post_gpu_command`, `barrier_check` |

In production EP deployments, **Dual mode** is most commonly used for inter-node peers. **Local mode** is activated for intra-node peers when `is_intranode_` is set ([ep/src/uccl_proxy.cpp:158-163]()).

**Proxy thread lifecycle diagram:**

```mermaid
stateDiagram-v2
    [*] --> "init_common()"
    "init_common()" --> "per_thread_rdma_init": "open IB device, reg GPU MR"
    "per_thread_rdma_init" --> "create_per_thread_qp": "create ibv_qp per peer"
    "create_per_thread_qp" --> "TCP exchange": "RDMAConnectionInfo"
    "TCP exchange" --> "modify_qp_to_rtr / rts": "bring QPs to RTS"
    "modify_qp_to_rtr / rts" --> "run loop"

    "run loop" --> "post_gpu_command": "dequeue D2H cmds"
    "post_gpu_command" --> "post_rdma_async_batched / post_atomic_operations"
    "post_rdma_async_batched / post_atomic_operations" --> "poll_cq_dual"
    "poll_cq_dual" --> "notify_gpu_completion": "advance D2H tail"
    "notify_gpu_completion" --> "run loop"

    "run loop" --> "stop": "progress_run=false"
    "stop" --> [*]
```

Sources: [ep/src/proxy.cpp:464-543](), [ep/src/uccl_proxy.cpp:133-181]()

### `run_sender` and `run_remote` Details

`init_sender()` calls `init_common()` then posts acknowledgement receive buffers via `local_post_ack_buf`. `init_remote()` additionally calls `remote_reg_ack_buf` and `post_receive_buffer_for_imm` (non-EFA path) to pre-post receive WRs for immediate-data notifications from the sender side ([ep/src/proxy.cpp:445-462]()).

### `run_dual` Details

`run_dual` merges the sender and remote roles into a single thread. It calls both `post_gpu_command` (send path) and `remote_poll_completions` / `apply_pending_updates` (receive path) inside the same loop iteration. In normal mode it also calls `barrier_check()` to coordinate local GPUs ([ep/src/proxy.cpp:494-543]()).

Sources: [ep/src/proxy.cpp:445-543]()

## RDMA Connection Setup

RDMA connections are established inside `Proxy::init_common()` ([ep/src/proxy.cpp:172-443]()). The steps are:

1. **NIC selection** — `per_thread_rdma_init` ([ep/src/rdma.cpp:384-658]()) enumerates `ibv_get_device_list`, computes PCIe distances between GPUs and NICs via `safe_pcie_distance`, applies the `UCCL_IB_HCA` / `NCCL_IB_HCA` filter, and picks the NIC closest to the GPU. On EFA with 32 NICs (p5) it spreads proxies across 4 NICs by `thread_idx % 4`. The selected NIC is opened with `ibv_open_device` and a PD is allocated.

2. **GPU memory registration** — the RDMA buffer (`cfg_.gpu_buffer`, size `cfg_.total_size`) is registered as an MR. With `USE_DMABUF` the path uses `reg_mr_gpu_dmabuf` (DMA-BUF fd via `cuMemGetHandleForAddressRange`) with a chunked fallback via `reg_mr_gpu_dmabuf_chunked` for buffers exceeding `kMaxDmabufChunkSize` (1 GiB). Without DMA-BUF it uses `ibv_reg_mr_iova2`. The resulting `rkey` is stored in `ProxyCtx::rkey` [ep/src/rdma.cpp:561-658]().

3. **QP creation** — `create_per_thread_qp` ([ep/src/rdma.cpp:840-960]()) creates:
   - One main `qp` (RC on IB, SRD on EFA)
   - One `ack_qp` and one `recv_ack_qp`
   - Up to `kChannelPerProxy` `data_qps_by_channel` entries (normal mode)
   - EFA QPs go INIT→RTR→RTS immediately inside `create_srd_qp_ex` ([ep/src/rdma.cpp:770-837]())
   - IB RC QPs are brought to INIT via `modify_qp_to_init`, then RTR/RTS after the TCP exchange

4. **TCP exchange** — `RDMAConnectionInfo` structs are exchanged between peers out-of-band using TCP sockets (see next section).

5. **QP state transitions** — `modify_qp_to_rtr` sets the remote QPN/LID/GID, `modify_qp_to_rts` completes the transition [ep/src/proxy.cpp:327-389]().

**QP state transition diagram:**

```mermaid
stateDiagram-v2
    [*] --> "RESET"
    "RESET" --> "INIT": "modify_qp_to_init()\nIBV_QPS_INIT"
    "INIT" --> "RTR": "modify_qp_to_rtr()\nset remote QPN, LID, GID"
    "RTR" --> "RTS": "modify_qp_to_rts()\nset SQ_PSN"
    "RTS" --> "Ready for RDMA writes"
```

Sources: [ep/src/rdma.cpp:962-1009](), [ep/src/rdma.cpp:1029-1120](), [ep/src/proxy.cpp:172-443]()

## TCP-Based RDMAConnectionInfo Exchange

`RDMAConnectionInfo` ([ep/include/rdma.hpp:24-57]()) carries everything the remote side needs to target this proxy's QP and memory region:

| Field | Purpose |
|---|---|
| `qp_num` / `ack_qp_num` / `recv_ack_qp_num` | Queue Pair numbers |
| `data_qp_num[kChannelPerProxy]` | Per-channel QP numbers (normal mode) |
| `psn` / `ack_psn` | Packet sequence numbers |
| `rkey` | Memory region remote key |
| `addr` / `len` | Remote GPU buffer base address and size |
| `lid` / `gid[16]` | LID (IB) and GID (RoCE/EFA) for AH creation |
| `atomic_buffer_rkey` / `atomic_buffer_addr` / `_len` | Atomic scratch buffer info |
| `num_mr_chunks` / `mr_chunk_info[]` | Chunked MR entries (DMA-BUF path) |

The exchange happens in `init_common()` using a concurrent client/server pattern:
- A receiver thread calls `recv_connection_info_as_server` on `listen_fd_` (created at `Proxy` construction via `create_listen_socket`).
- The main thread calls `send_connection_info_as_client` to each peer's listen port.
- The listener port of each proxy is communicated to peers via `dist.all_gather_object` at the Python layer (see `get_cpu_proxies_meta` in [ep/bench/utils.py:113-142]()).

**TCP exchange sequence:**

```mermaid
sequenceDiagram
    participant A as "Proxy (rank A)\nrecv_connection_info_as_server"
    participant TCP as "TCP socket"
    participant B as "Proxy (rank B)\nsend_connection_info_as_client"

    B->>TCP: "connect to A's listen_port"
    B->>TCP: "send my_rank (int)"
    B->>TCP: "send local_infos_[A] (RDMAConnectionInfo)"
    TCP->>A: "accept"
    A->>TCP: "receive actual_peer"
    A->>TCP: "receive remote_infos_[B]"
```

Sources: [ep/include/rdma.hpp:24-57](), [ep/src/rdma.cpp:329-382](), [ep/src/proxy.cpp:284-310]()

## post_receive_buffer_for_imm

On non-EFA IB paths, the remote proxy thread must pre-post receive Work Requests before the sender can use `IBV_WR_SEND_WITH_IMM`. `post_receive_buffer_for_imm` ([ep/include/rdma.hpp:332]()) posts a batch of receive WRs on `ProxyCtx::qp` so that incoming immediate-data messages from the sender side can be matched.

It is called in:
- `Proxy::init_remote()` [ep/src/proxy.cpp:460]()
- `Proxy::run_dual()` (for each inter-node peer) [ep/src/proxy.cpp:507]()

On EFA, SRD QPs with `EFADV_QP_FLAGS_UNSOLICITED_WRITE_RECV` set ([ep/src/rdma.cpp:799]()) do not consume receive WRs for RDMA-write-with-imm, so this call is skipped under `#ifndef EFA`.

Sources: [ep/include/rdma.hpp:332](), [ep/src/proxy.cpp:459-461](), [ep/src/proxy.cpp:504-508]()

## Integration with Expert-Parallel Workloads

The GPU-Driven RDMA Proxy is specifically designed for expert-parallel communication patterns where GPU kernels need to dispatch tokens to remote experts and combine results.

### Dispatch Phase Flow

```mermaid
sequenceDiagram
    participant GK as "GPU Kernel<br/>(dispatch)"
    participant RB as "Ring Buffer"
    participant PT as "CPU Proxy"
    participant RN as "Remote Node"
    
    GK->>+GK: "Process topk_idx, prepare tokens"
    GK->>RB: "nvshmemi_ibgda_put_nbi_warp(token_data)"
    GK->>RB: "nvshmemi_ibgda_amo_nonfetch_add(token_count)"
    
    PT->>RB: "poll for commands"
    RB-->>PT: "TransferCmd entries"
    PT->>RN: "RDMA Write (token data)"
    PT->>RN: "RDMA Atomic (count update)"
    
    RN-->>PT: "completion notification"
    PT->>RB: "update tail pointer"
    GK->>+GK: "continue with next tokens"
```

### Buffer Management

The system manages multiple buffer types for different communication phases:

| Buffer Type | Purpose | GPU Access | CPU Proxy Role |
|-------------|---------|------------|----------------|
| `rdma_x` | Send buffer for token data | Write token data | Read for RDMA transfer |
| `rdma_recv_x` | Receive buffer for tokens | Read received tokens | Target of remote writes |
| `rdma_recv_count` | Token count per expert | Read counts | Target of atomic updates |
| `atomic_buffer_ptr` | Atomic operation workspace | N/A | Source for atomic values |

**Sources:** [ep/src/internode_ll.cu:177-183](), [ep/src/internode_ll.cu:285-290](), [ep/src/uccl_ep.cc:641-649]()

## Performance Characteristics

The GPU-Driven RDMA Proxy system achieves low-latency communication by eliminating GPU-CPU synchronization overhead and enabling overlapped computation and communication.

### Key Performance Features

- **Asynchronous Operation**: GPU kernels continue execution while RDMA operations are processed by CPU proxies
- **Batched Processing**: CPU proxies can batch multiple RDMA operations for improved efficiency  
- **Lock-Free Design**: Ring buffer communication avoids synchronization overhead
- **Warp-Level Parallelism**: Multiple GPU warps can issue concurrent RDMA operations

The system is optimized for expert-parallel workloads where communication patterns are predictable and can benefit from pipelined execution.

**Sources:** [ep/bench/test_low_latency.py:1-540](), [ep/bench/utils.py:314-342]()

---

# Page: GPU Kernels and Internode Communication

# GPU Kernels and Internode Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)

</details>



## Purpose and Scope

This document covers the GPU kernel implementations and internode communication mechanisms in UCCL-EP. It details the dispatch and combine kernels that handle token routing between nodes in MoE models, the specialized warp roles within these kernels, and the GPU-initiated RDMA operations. For the overall EP architecture and Buffer API, see [4.1](#4.1). For CPU Proxy and RDMA resource management, see [4.2](#4.2). For performance testing and benchmarks, see [4.4](#4.4).

The kernels described here implement the core data movement operations for expert parallelism: **dispatch** (routing tokens to remote experts) and **combine** (gathering results from remote experts).

---

## System Overview

UCCL-EP uses GPU kernels that directly initiate RDMA operations for inter-node communication, bypassing CPU involvement in the critical path. This GPU-initiated communication achieves microsecond-scale latencies critical for MoE inference workloads.

```mermaid
graph TB
    subgraph "GPU Dispatch Kernel"
        NOTIFY["notify_dispatch<br/>SM 0"]
        SENDER["Sender Warps<br/>SM 1-N"]
        FP8["FP8 Cast<br/>(if enabled)"]
        POST["Post RDMA Write<br/>via D2H Queue"]
    end
    
    subgraph "Communication Layer"
        D2H["D2HHandle<br/>Device-to-Host Queue"]
        PROXY["CPU Proxy Thread"]
        QP["RDMA Queue Pairs"]
    end
    
    subgraph "GPU Combine Kernel"
        POLL["Poll Atomic Counters"]
        UNPACK["Unpack & Copy Tokens"]
        GATHER["Gather by Expert"]
    end
    
    subgraph "Remote Node"
        RDMA_BUF["RDMA Recv Buffer"]
        ATOMIC["Atomic Counters"]
    end
    
    NOTIFY --> D2H
    FP8 --> SENDER
    SENDER --> POST
    POST --> D2H
    D2H --> PROXY
    PROXY --> QP
    QP --> RDMA_BUF
    QP --> ATOMIC
    ATOMIC --> POLL
    RDMA_BUF --> UNPACK
    UNPACK --> GATHER
    
    style NOTIFY fill:#f9f9f9
    style SENDER fill:#f9f9f9
    style POLL fill:#f9f9f9
```

**Sources:** [ep/src/internode.cu:1-1500](), [ep/src/internode_ll.cu:1-1000](), [ep/include/uccl_ibgda.cuh:1-300]()

---

## Operating Modes

UCCL-EP kernels operate in two distinct modes optimized for different workload characteristics:

| Mode | Optimization Target | Batch Size | Latency | Throughput | Use Case |
|------|-------------------|------------|---------|------------|----------|
| **Normal Mode** | Throughput | 512-4096 tokens | ~300-500 µs | 50-70 GB/s | Training, large batch inference |
| **Low-Latency Mode** | Latency | 32-256 tokens | 136-300 µs | 20-40 GB/s | Online inference, prefill |

**Runtime Constants (`common.hpp`):**

| Constant | Value | Purpose |
|----------|-------|---------|
| `kMaxInflightNormal` | 8 | Max outstanding WRs per proxy in normal mode |
| `kMaxInflightLowLatency` | 32 | Max outstanding WRs per proxy in low-latency mode |
| `kChannelPerProxy` | 8 | D2H channels per proxy thread |
| `kNumProxyThs` | 4 | CPU proxy threads per GPU |
| `kAtomicBufferSize` | 81960 bytes | Atomic counter buffer size |
| `kQueueSize` | 2048 | D2H ring buffer capacity |

**Sources:** [ep/include/common.hpp:38-97](), [ep/src/internode.cu:84-390](), [ep/src/internode_ll.cu:14-46]()

---

## Compile-Time Configuration (`ep_configs.cuh`)

`ep/include/ep_configs.cuh` defines compile-time constants consumed by both `internode.cu` and `internode_ll.cu`. These parameters must be set at build time and control the maximum topology and buffer sizes.

Key constants from this header:

| Constant | Typical Value | Meaning |
|----------|--------------|---------|
| `NUM_MAX_NVL_PEERS` | 8 | Max GPUs reachable via NVLink per node |
| `NUM_MAX_RDMA_PEERS` | varies | Max remote RDMA nodes |
| `NUM_BUFFER_ALIGNMENT_BYTES` | 128 | Memory region alignment requirement |
| `WARP_SIZE` | 32 | CUDA warp width |
| `kFP8Margin` | small float | Minimum amax for FP8 quantization denominator |
| `LOW_LATENCY_SEND_PHASE` | bitmask | Phase selection flag for LL dispatch kernel |
| `MAX_NUM_BARRIERS` | varies | AMD-specific shared barrier slots |

The `EP_STATIC_ASSERT` macro uses these to enforce topology assumptions at compile time. For example:

```
EP_STATIC_ASSERT(NUM_MAX_NVL_PEERS == 8, "Invalid number of maximum NVL peers");
```

[ep/src/internode.cu:19-20]()

Changing `NUM_MAX_NVL_PEERS` requires recompiling the CUDA kernels. The Python-layer `Buffer` class enforces these limits at runtime via `EP_HOST_ASSERT`.

**Sources:** [ep/src/internode.cu:1-9](), [ep/src/internode_ll.cu:1-8](), [ep/include/ep_utils.cuh:1-5](), [ep/src/uccl_ep.cc:1-15]()

---

## Dispatch Kernel Architecture

The dispatch operation routes tokens from source GPUs to remote expert GPUs based on top-k routing decisions.

```mermaid
graph LR
    subgraph "Dispatch Phases"
        PHASE1["Phase 1: notify_dispatch<br/>Exchange metadata"]
        PHASE2["Phase 2: dispatch<br/>Transfer token data"]
    end
    
    subgraph "notify_dispatch (SM 0)"
        CLEAN["Clean buffers"]
        COUNT["Count tokens per expert"]
        ALLTOALL["All-to-all size exchange<br/>via NVSHMEM"]
        PREFIX["Calculate prefix sums"]
    end
    
    subgraph "dispatch (SM 1-N)"
        CAST["FP8 cast (optional)<br/>Warps 0-(N-1)"]
        SEND["RDMA send<br/>Warps 0-(N-1)"]
        TALLY["Count expert tokens<br/>Warp N"]
    end
    
    PHASE1 --> PHASE2
    PHASE1 --> CLEAN
    CLEAN --> COUNT
    COUNT --> ALLTOALL
    ALLTOALL --> PREFIX
    
    PHASE2 --> CAST
    CAST --> SEND
    PHASE2 --> TALLY
    
    style PHASE1 fill:#f9f9f9
    style PHASE2 fill:#f9f9f9
```

**Sources:** [ep/src/internode.cu:94-390](), [ep/src/internode_ll.cu:22-46]()

### Phase 1: Notify Dispatch

The `notify_dispatch` kernel (SM 0) exchanges metadata about token distributions before data transfer begins.

**Key Functions:**
- `notify_dispatch<kLowLatencyMode, kNumRDMARanks>` ([ep/src/internode.cu:94-390]())
- `clean_low_latency_buffer` ([ep/src/internode_ll.cu:22-46]())

**Responsibilities:**
1. **Buffer Cleaning**: Zero out receive buffers from previous iteration ([ep/src/internode.cu:149-167]())
2. **Token Counting**: Aggregate `num_tokens_per_rank`, `num_tokens_per_rdma_rank`, `num_tokens_per_expert` ([ep/src/internode.cu:173-186]())
3. **Metadata Exchange**: Send counts to remote ranks via NVSHMEM barrier and put operations ([ep/src/internode.cu:191-212]())
4. **Prefix Sum Calculation**: Compute cumulative sums for slot allocation ([ep/src/internode.cu:372-388]())

**Buffer Layout:**

The `SymBuffer` structure manages symmetric buffers across ranks:

```cpp
// Structure for send/recv buffers across ranks
rdma_recv_num_tokens_mixed = SymBuffer<int>(
    rdma_buffer_ptr,
    NUM_MAX_NVL_PEERS + num_rdma_experts + 1,  // elements per rank
    kNumRDMARanks                               // num ranks
);
```

**Sources:** [ep/src/internode.cu:94-390](), [ep/src/internode.cu:142-212]()

### Phase 2: Dispatch (Normal Mode)

The main dispatch kernel transfers token data to remote ranks. Each SM handles tokens independently.

**Kernel Signature:**
```cpp
template <bool kUseFP8, bool kUseUE8M0, int kHidden, int kNumRDMARanks>
__global__ void dispatch(
    void* packed_recv_x,
    void* packed_recv_x_scales,
    int* packed_recv_src_info,
    // ... other parameters
);
```

**Warp Specialization in Normal Mode:**

| Warp Group | Role | Responsibility |
|------------|------|----------------|
| Warps 0 to (N-1) | Token Processing | FP8 cast, metadata write, RDMA initiation |
| Warp N | Expert Counting | Read `topk_idx`, count tokens per expert |

**Per-Token Processing Flow ([ep/src/internode.cu:500-800]()):**

1. **Read Source Token**: Load bf16 data from global memory
2. **FP8 Quantization** (if enabled): 
   - Calculate per-channel amax ([ep/src/internode.cu:550-575]())
   - Compute scale factors ([ep/src/internode.cu:577-585]())
   - Convert to fp8e4m3 format ([ep/src/internode.cu:587-600]())
3. **Write Metadata**: Store source token index for combine phase ([ep/src/internode.cu:620-625]())
4. **Issue RDMA Write**: Post operation via `nvshmemi_ibgda_put_nbi_warp` ([ep/src/internode.cu:650-700]())
5. **Update Counter**: Increment atomic finish counter ([ep/src/internode.cu:705-710]())

**Sources:** [ep/src/internode.cu:397-1000](), [ep/src/internode.cu:500-800]()

### Phase 2: Dispatch (Low-Latency Mode)

The low-latency dispatch kernel minimizes overhead through aggressive optimizations.

**Kernel Signature:**
```cpp
template <bool kUseFP8, bool kUseUE8M0, int kHidden>
__launch_bounds__(1024, 1) __global__ void dispatch(
    void* packed_recv_x, void* packed_recv_x_scales,
    // ... parameters
    uint64_t const* d2h_channel_addrs,
    int num_d2h_channel_addrs,
    void** ipc_rdma_base_ptrs,  // for intra-node IPC
    // ...
);
```

**Key Optimizations ([ep/src/internode_ll.cu:49-500]()):**

1. **Intra-node Fast Path**: Use IPC (Inter-Process Communication) for same-node transfers, bypassing RDMA entirely
2. **Aggressive Pipelining**: Overlap FP8 cast with metadata writes
3. **Direct Counter Updates**: Atomic operations on remote memory without acknowledgment
4. **Minimal Synchronization**: Per-expert slot allocation with lock-free atomics

**Intra-node vs Inter-node Routing ([ep/src/internode_ll.cu:208-230]()):**
```cpp
auto const dst_p2p_ptr = ipc_rdma_base_ptrs
    ? uccl::get_ipc_p2p_ptr(dst_ptr, ipc_rdma_base_ptrs, 
                             rank, dst_rank, max_nvl_peers, 0)
    : 0;
if (dst_p2p_ptr == 0) {
    // Inter-node: use RDMA
    uccl::nvshmemi_ibgda_put_nbi_warp(/* ... */);
} else {
    // Intra-node: direct IPC copy
    UNROLLED_WARP_COPY(8, lane_id, num_int4_per_msg, 
                       dst_int4_ptr, src_int4_ptr, 
                       ld_nc_global, st_na_global);
}
```

**Sources:** [ep/src/internode_ll.cu:49-500](), [ep/src/internode_ll.cu:208-230]()

---

## Combine Kernel Architecture

The combine operation gathers expert outputs from remote ranks back to the source GPU.

```mermaid
graph TB
    subgraph "Combine Kernel Execution"
        PHASE1C["Phase 1: notify_combine<br/>Exchange result counts"]
        PHASE2C["Phase 2: combine<br/>Receive and pack data"]
    end
    
    subgraph "notify_combine (SM 0)"
        WAITD["Wait for dispatch complete"]
        SENDC["Send expert output counts"]
        RECVC["Receive total tokens"]
    end
    
    subgraph "combine Receiver Warps"
        POLL["Poll atomic counters<br/>for completion"]
        READ["Read from RDMA buffer"]
        CASTBACK["Cast FP8 back to BF16"]
        PACK["Pack by expert layout"]
    end
    
    PHASE1C --> WAITD
    WAITD --> SENDC
    SENDC --> RECVC
    
    PHASE2C --> POLL
    POLL --> READ
    READ --> CASTBACK
    CASTBACK --> PACK
    
    style PHASE1C fill:#f9f9f9
    style PHASE2C fill:#f9f9f9
```

**Sources:** [ep/src/internode.cu:1500-2500](), [ep/src/internode_ll.cu:500-1000]()

### Phase 1: Notify Combine

Similar to dispatch, metadata exchange occurs before data transfer.

**Key Steps ([ep/src/internode.cu:1520-1650]()):**
1. Wait for all expert computations to complete
2. Exchange `num_output_tokens_per_expert` across ranks
3. Calculate receive buffer layout and prefix sums

**Sources:** [ep/src/internode.cu:1520-1650]()

### Phase 2: Combine (Normal Mode)

Each SM's warps poll for completed expert outputs and pack them into the result tensor.

**Polling Mechanism ([ep/src/internode.cu:1800-1900]()):**

```cpp
// Per-expert atomic counter tracks completion
for (int expert_idx = warp_start; expert_idx < warp_end; ++expert_idx) {
    int expected_count = num_tokens_for_expert[expert_idx];
    
    // Spin-wait on atomic counter
    while (ld_acquire_global(atomic_counter + expert_idx) < expected_count) {
        // Busy wait with timeout
        if (timeout_exceeded()) handle_timeout();
    }
    
    // Data is ready, proceed with copy
    // ...
}
```

**Packing Strategy ([ep/src/internode.cu:1950-2100]()):**

Tokens are copied from the RDMA receive buffer into the output tensor, organized by expert:

1. **Layout Calculation**: Determine source token positions using prefix sums
2. **Multi-rank Aggregation**: Iterate over all source ranks contributing to this expert
3. **Coalesced Copy**: Use vectorized loads/stores (`int4`) for efficiency
4. **FP8 Decompression**: If FP8 was used, apply inverse scaling

**Sources:** [ep/src/internode.cu:1800-2100]()

### Phase 2: Combine (Low-Latency Mode)

The low-latency combine kernel uses a similar polling approach but with additional optimizations.

**Reordering Buffer for Out-of-Order Receives ([ep/src/internode_ll.cu:700-850]()):**

When RDMA writes arrive out of order, a reordering buffer accumulates updates before applying them:

```cpp
// Each atomic operation carries a 4-bit sequence number
uint8_t seq = aimm.GetSeq();  // Extract from immediate value
int index = offset / sizeof(int);

// Store in per-index reordering buffer
reorder_buffer[index][seq] = value;
seq_bitmap[index] |= (1u << seq);

// Apply updates when all expected sequences arrive
if (seq_bitmap[index] == expected_mask) {
    for (int s = 0; s < kReorderingBufferSize; ++s) {
        if (seq_bitmap[index] & (1u << s)) {
            atomicAdd(target_addr + index, reorder_buffer[index][s]);
        }
    }
    seq_bitmap[index] = 0;  // Reset
}
```

**TMA Operations (SM90+) ([ep/src/internode_ll.cu:900-1000]()):**

On Hopper GPUs, Tensor Memory Accelerator (TMA) instructions accelerate bulk transfers:

```cpp
if constexpr (kUseTMA) {
    tma_store_fence();
    // Issue TMA descriptor load
    // ...
    tma_store_wait<0>();  // Wait for completion
}
```

**Sources:** [ep/src/internode_ll.cu:500-1000](), [ep/src/internode_ll.cu:700-850]()

---

## GPU-Initiated RDMA

UCCL-EP kernels post RDMA operations directly from GPU threads, avoiding CPU round-trips.

```mermaid
graph TB
    subgraph "GPU Thread"
        PREP["Prepare RDMA metadata<br/>(dst_ptr, src_ptr, bytes)"]
        CMD["Build TransferCmd"]
        ENQUEUE["Enqueue to D2H queue<br/>nvshmemi_ibgda_put_nbi_warp"]
    end
    
    subgraph "D2H Command Queue"
        RING["RingBuffer or FIFO"]
        BACKPRESSURE["Backpressure if full"]
    end
    
    subgraph "CPU Proxy Thread"
        POLL["Poll D2H queue<br/>post_gpu_command"]
        BATCH["Batch commands<br/>by destination"]
        POST["Post to ibverbs QP<br/>ibv_post_send"]
    end
    
    subgraph "RDMA NIC"
        DMA["DMA engine transfers data"]
        CQ["Completion queue"]
    end
    
    PREP --> CMD
    CMD --> ENQUEUE
    ENQUEUE --> RING
    RING --> BACKPRESSURE
    BACKPRESSURE -.spin wait.-> PREP
    RING --> POLL
    POLL --> BATCH
    BATCH --> POST
    POST --> DMA
    DMA --> CQ
    
    style RING fill:#f9f9f9
```

**Sources:** [ep/include/uccl_ibgda.cuh:1-300](), [ep/src/rdma.cpp:706-962]()

### IBGDA/NVSHMEM Interface

The `nvshmemi_ibgda_put_nbi_warp` function is the primary GPU-side API for posting RDMA writes.

**Function Signature ([ep/include/uccl_ibgda.cuh:27-133]()):**

```cpp
template <bool use_normal_mode = false>
__device__ __forceinline__ void nvshmemi_ibgda_put_nbi_warp(
    uint64_t req_rptr,      // Remote pointer offset
    uint64_t req_lptr,      // Local pointer offset
    size_t bytes,           // Transfer size
    int dst_rank,           // Destination rank
    int expert_idx,         // Expert/channel index
    int lane_id,            // Warp lane ID
    int message_idx,        // Sequence number
    uint64_t const* d2h_channel_addrs,  // D2H queue addresses
    int num_d2h_channel_addrs,
    bool is_combine,
    int low_latency_buffer_idx = 0,
    uint64_t atomic_offset = 0,
    uint64_t atomic_val = 0
);
```

**Channel Selection ([ep/include/uccl_ibgda.cuh:36-42]()):**

```cpp
int thread_idx = (expert_idx % num_d2h_channel_addrs) % kNumProxyThs;
int per_thread_d2h_channel_idx = 
    (expert_idx % num_d2h_channel_addrs) / kNumProxyThs;
int d2h_channel_idx = 
    thread_idx * kChannelPerProxy + per_thread_d2h_channel_idx;
```

This distributes expert indices across proxy threads and channels to balance load.

**Backpressure Handling ([ep/include/uccl_ibgda.cuh:78-132]()):**

```cpp
while (true) {
    cur_head = h->head();
    cur_tail = h->tail();
    inflight = cur_head - cur_tail;
    
    if (inflight < (use_normal_mode ? kMaxInflightNormal 
                                    : kMaxInflightLowLatency)) {
        // Slot available, enqueue command
        TransferCmd cmd{};
        cmd.cmd_type = make_cmd_type(CmdType::WRITE, is_combine, 
                                      low_latency_buffer_idx);
        cmd.req_rptr = req_rptr;
        cmd.req_lptr = req_lptr;
        cmd.bytes = bytes;
        cmd.dst_rank = dst_rank;
        // ... set other fields
        h->atomic_set_and_commit(cmd, &slot);
        break;
    }
    
    // Queue full, print warning and spin
    if (clock64() - last_print > kPrintCycleInterval) {
        printf("[dispatch] stuck waiting, inflight=%ld\n", inflight);
        last_print = clock64();
    }
}
```

**Sources:** [ep/include/uccl_ibgda.cuh:27-133](), [ep/include/uccl_ibgda.cuh:78-132]()

### D2H Command Queue

The Device-to-Host queue bridges GPU threads and CPU proxy threads.

**Queue Implementations:**

Two backend implementations are supported:

| Backend | Type | Characteristics |
|---------|------|-----------------|
| **RingBuffer** | Lock-free ring buffer | Fixed capacity, head/tail pointers, bitmask tracking |
| **MSCCLPP FIFO** | Hardware-assisted FIFO | Dynamic capacity, hardware backpressure support |

**TransferCmd Structure ([ep/include/ring_buffer.cuh:50-100]()):**

```cpp
struct TransferCmd {
    CmdType cmd_type;        // WRITE, ATOMIC, BARRIER, QUIET
    uint64_t req_rptr;       // Remote pointer offset
    uint64_t req_lptr;       // Local pointer offset
    uint32_t bytes;          // Transfer size (24 bits used)
    uint32_t dst_rank;       // Destination rank
    int expert_idx;          // Expert index or channel
    uint64_t atomic_offset;  // For atomic operations
    uint64_t atomic_val;     // Atomic value
    int value;               // Alternative atomic value field
};
```

**Atomic Commit ([ep/include/d2h_queue_device.cuh:150-200]()):**

```cpp
__device__ __forceinline__ void atomic_set_and_commit(
    TransferCmd const& cmd, uint64_t* out_slot) 
{
    uint64_t slot = atomicAdd(&head_, 1ULL);
    *out_slot = slot;
    
    uint64_t idx = slot & mask_;
    entries_[idx] = cmd;
    
    // Store cmd_type last with release semantics
    __threadfence_system();
    cmd_types_[idx].store(cmd.cmd_type, std::memory_order_release);
}
```

**Sources:** [ep/include/ring_buffer.cuh:1-200](), [ep/include/d2h_queue_device.cuh:1-300]()

### CPU Proxy Processing

The CPU Proxy thread polls D2H queues and posts actual RDMA operations.

**Polling Loop ([ep/src/proxy.cpp:509-646]()):**

```cpp
void Proxy::post_gpu_command(uint64_t& my_tail, size_t& seen) {
    for (size_t rb_idx = 0; rb_idx < cfg_.d2h_queues.size(); rb_idx++) {
        d2hq::HostD2HHandle* h = &cfg_.d2h_queues[rb_idx];
        
        uint64_t cur_head = h->volatile_head();
        if (cur_head == ring_tail) continue;  // No new work
        
        // Collect batch of commands
        for (size_t i = ring_seen; i < cur_head; ++i) {
            CmdType cmd = h->volatile_load_cmd_type(i);
            if (cmd == CmdType::EMPTY) break;
            
            TransferCmd& cmd_entry = h->load_cmd_entry(i);
            uint64_t unique_wr_id = (rb_idx << 32) | i;
            wrs_to_post.push_back(unique_wr_id);
            cmds_to_post.push_back(cmd_entry);
            ring_seen = i + 1;
        }
    }
    
    if (!wrs_to_post.empty()) {
        post_gpu_commands_mixed(wrs_to_post, cmds_to_post);
        wrs_to_post.clear();
        cmds_to_post.clear();
    }
}
```

**Batched Posting ([ep/src/rdma.cpp:706-962]()):**

Commands are grouped by destination rank and ring index for efficiency:

```cpp
void post_rdma_async_batched_normal_mode(
    ProxyCtx& S, void* buf, size_t num_wrs,
    std::vector<uint64_t> const& wrs_to_post,
    std::vector<TransferCmd> const& cmds_to_post,
    std::vector<std::unique_ptr<ProxyCtx>>& ctxs,
    int my_rank, int thread_idx) 
{
    // Group commands by destination rank
    std::unordered_map<int, std::vector<size_t>> dst_rank_wr_ids;
    for (size_t i = 0; i < num_wrs; ++i) {
        dst_rank_wr_ids[cmds_to_post[i].dst_rank].push_back(i);
    }
    
    // For each destination, group by ring and post
    for (auto& [dst_rank, wr_ids] : dst_rank_wr_ids) {
        ProxyCtx* ctx = ctxs[dst_rank].get();
        
        // Group by ring index for multi-QP support
        std::unordered_map<size_t, std::vector<size_t>> ring_to_indices;
        for (size_t j = 0; j < wr_ids.size(); ++j) {
            size_t i = wr_ids[j];
            size_t ring_idx = (wrs_to_post[i] >> 32) & 0xFFFFFFFFu;
            ring_to_indices[ring_idx].push_back(i);
        }
        
        // Post chain of work requests per ring
        for (auto& [ring_idx, idxs] : ring_to_indices) {
            // Build ibv_send_wr chain
            // ...
            ibv_post_send(qp, &wrs[0], &bad);
        }
    }
}
```

**Sources:** [ep/src/proxy.cpp:509-646](), [ep/src/rdma.cpp:706-962]()

---

## Synchronization Mechanisms

### Atomic Counters

Atomic counters track operation completion without explicit acknowledgments.

**Counter Types:**

| Counter | Purpose | Location |
|---------|---------|----------|
| `atomic_counter_per_expert` | Tracks sent tokens per expert | GPU memory |
| `atomic_finish_counter_per_expert` | Tracks completed sends per expert | GPU memory |
| `moe_recv_counter_mapped` | Tracks total received tokens | CPU pinned memory |
| `moe_recv_expert_counter_mapped` | Tracks received tokens per expert | CPU pinned memory |

**Dispatch Counter Updates ([ep/src/internode_ll.cu:195-233]()):**

```cpp
// Sender: increment counter to claim slot
int slot_idx = lane_id == 0 
    ? atomicAdd(atomic_counter_per_expert + dst_expert_idx, 1) 
    : 0;
slot_idx = __shfl_sync(WARP_MASK, slot_idx, 0);

// After RDMA post, mark operation complete
__syncwarp();
lane_id == 0 
    ? atomic_add_release_global(
        atomic_finish_counter_per_expert + dst_expert_idx, 1)
    : 0;
```

**Combine Polling ([ep/src/internode_ll.cu:310-350]()):**

```cpp
// Receiver: spin until expected count reached
while (ld_acquire_global(atomic_finish_counter_per_expert + expert_idx) 
       != FINISHED_SUM_TAG * 2) {
    #if defined(__HIP_PLATFORM_AMD__) || defined(__HIPCC__)
        __builtin_amdgcn_s_sleep(1);
    #endif
}
```

**Sources:** [ep/src/internode_ll.cu:195-233](), [ep/src/internode_ll.cu:310-350]()

### NVSHMEM Barriers

Global barriers synchronize all participating GPUs.

**Barrier Implementation ([ep/src/internode.cu:215-226]()):**

```cpp
// Wait for all previous RDMA operations to complete
if (thread_id == WARP_SIZE) {
    uccl::nvshmemi_ibgda_quiet(d2h_channel_addrs, 
                               num_d2h_channel_addrs, nvl_rank);
}
__syncthreads();

// Global synchronization across all ranks
if (thread_id == 0) {
    uccl::nvshmem_sync_with_same_gpu_idx(d2h_channel_addrs,
                                         num_d2h_channel_addrs, nvl_rank);
}
__syncthreads();
```

**Intra-node Barrier ([ep/src/intranode.cuh:100-150]()):**

```cpp
template <int kNumNVLPeers, bool kUseNVSHMEM = false>
__device__ __forceinline__ void barrier_block(
    int** barrier_signal_ptrs, int nvl_rank) 
{
    if constexpr (kUseNVSHMEM) {
        nvshmemx_barrier_all_block();
    } else {
        // Manual barrier using atomic signals
        if (threadIdx.x == 0) {
            // Arrive: increment all peers' signals
            for (int i = 0; i < kNumNVLPeers; ++i) {
                atomicAdd_system(barrier_signal_ptrs[i] + nvl_rank, 1);
            }
            
            // Wait: spin until all peers arrived
            int expected = /* current generation count */;
            for (int i = 0; i < kNumNVLPeers; ++i) {
                while (ld_acquire_global(
                    barrier_signal_ptrs[nvl_rank] + i) < expected) {
                    /* spin */
                }
            }
        }
        __syncthreads();
    }
}
```

**Sources:** [ep/src/internode.cu:215-226](), [ep/src/intranode.cuh:100-200]()

### Immediate Values

RDMA immediate data carries metadata without separate messages.

**Immediate Value Types:**

Three distinct immediate value formats are used:

```mermaid
graph TB
    subgraph "Immediate Value Formats"
        WRITE["WriteImm<br/>[31:30]=00<br/>Write operation"]
        ATOMIC["AtomicsImm<br/>[31]=1<br/>Atomic operation"]
        BARRIER["BarrierImm<br/>[31]=0, [30]=1<br/>Control message"]
    end
    
    subgraph "WriteImm Fields"
        W_RANK["[9:0] src_rank (10 bits)"]
        W_TOKENS["[17:10] num_tokens (8 bits)"]
        W_EXPERT["[26:18] expert_idx (9 bits)"]
        W_BUFFER["[27] buffer_idx (1 bit)"]
        W_COMBINE["[28] is_combine (1 bit)"]
    end
    
    subgraph "AtomicsImm Fields"
        A_OFFSET["[12:0] offset (13 bits)"]
        A_VALUE["[27:13] value (15 bits, signed)"]
        A_REORDER["[28] reorderable (1 bit)"]
        A_BUFFER["[29] buffer_idx (1 bit)"]
        A_COMBINE["[30] is_combine (1 bit)"]
    end
    
    WRITE --> W_RANK
    WRITE --> W_TOKENS
    WRITE --> W_EXPERT
    WRITE --> W_BUFFER
    WRITE --> W_COMBINE
    
    ATOMIC --> A_OFFSET
    ATOMIC --> A_VALUE
    ATOMIC --> A_REORDER
    ATOMIC --> A_BUFFER
    ATOMIC --> A_COMBINE
    
    style WRITE fill:#f9f9f9
    style ATOMIC fill:#f9f9f9
    style BARRIER fill:#f9f9f9
```

**WriteImm Packing ([ep/include/rdma.hpp:180-240]()):**

```cpp
class WriteImm {
public:
    static WriteImm Pack(bool is_combine,
                         uint32_t buffer_idx,   // 0/1
                         uint32_t expert_idx,   // 0..511 (9 bits)
                         uint32_t num_tokens,   // 0..255 (8 bits)
                         uint32_t my_rank) {    // 0..1023 (10 bits)
        uint32_t imm = ((is_combine & 0x1u) << 28) |
                       ((buffer_idx & 0x1u) << 27) |
                       ((expert_idx & 0x1FFu) << 18) |
                       ((num_tokens & 0xFFu) << 10) |
                       (my_rank & 0x3FFu);
        return WriteImm(imm);
    }
    
    // Getters extract fields
    inline uint32_t GetRank() const { return imm_data_ & 0x3FF; }
    inline uint32_t GetNumTokens() const { 
        return (imm_data_ >> 10) & 0xFF; 
    }
    inline uint32_t GetExpertIdx() const { 
        return (imm_data_ >> 18) & 0x1FF; 
    }
    // ...
};
```

**AtomicsImm with Reordering ([ep/include/rdma.hpp:68-178]()):**

```cpp
class AtomicsImm {
public:
    // Pack with 4-bit sequence number for reordering
    static AtomicsImm PackAtomicWithSeq(int v15, uint16_t off_aligned_bytes,
                                        uint8_t seq, bool reorderable = true) {
        // Sequence bits: [1:0] in offset, [3:2] in buffer/combine bits
        uint16_t off13 = (off_aligned_bytes & 0x1FFFu) | (seq & 0x3u);
        int is_combine_as_seq3 = (seq >> 3) & 0x1;
        int bufidx_as_seq2 = (seq >> 2) & 0x1;
        
        return Pack(/*is_atomics=*/true, is_combine_as_seq3, v15,
                    off13, bufidx_as_seq2, reorderable);
    }
    
    inline uint8_t GetSeq() const {
        uint8_t seq = (imm_data_ & 0x3u);              // bits [1:0]
        seq |= ((imm_data_ >> 29) & 0x1u) << 2;       // bit 29 -> seq[2]
        seq |= ((imm_data_ >> 30) & 0x1u) << 3;       // bit 30 -> seq[3]
        return seq;
    }
};
```

**Immediate Value Processing ([ep/src/bench_utils.hpp:200-400]()):**

The CPU proxy processes immediate values from completion queue entries:

```cpp
void remote_poll_completions(ProxyCtx& S, int thread_idx, 
                              CopyRingBuffer& ring,
                              /* ... */) {
    struct ibv_wc wc[kMaxOutstandingRecvs];
    int n = ibv_poll_cq(S.cq, kMaxOutstandingRecvs, wc);
    
    for (int i = 0; i < n; ++i) {
        if (wc[i].status != IBV_WC_SUCCESS) continue;
        
        uint32_t imm = ntohl(wc[i].imm_data);
        
        if (ImmType::IsWrite(imm)) {
            WriteImm wimm(imm);
            int expert_idx = wimm.GetExpertIdx();
            int num_tokens = wimm.GetNumTokens();
            int src_rank = wimm.GetRank();
            // Process write completion
            // ...
        } else if (ImmType::IsAtomics(imm)) {
            AtomicsImm aimm(imm);
            if (aimm.IsReorderable()) {
                // Add to reordering buffer
                pending_atomic_updates.insert({addr, value, imm, ...});
            } else {
                // Apply immediately
                atomicAdd(addr, value);
            }
        }
    }
}
```

**Sources:** [ep/include/rdma.hpp:68-280](), [ep/src/bench_utils.hpp:200-500]()

---

## Warp Roles and Specialization

Within dispatch and combine kernels, warps are assigned specialized roles for efficiency.

```mermaid
graph TB
    subgraph "Dispatch Kernel Warp Roles"
        SENDER_ROLE["Sender Warps<br/>Post RDMA writes"]
        FORWARDER_ROLE["Forwarder Warps<br/>NVLink intra-node copy"]
        COUNTER_ROLE["Counter Warp<br/>Aggregate expert counts"]
    end
    
    subgraph "Combine Kernel Warp Roles"
        RECEIVER_ROLE["Receiver Warps<br/>Poll & unpack data"]
        PACKER_ROLE["Packer Warps<br/>Organize by expert"]
    end
    
    subgraph "Synchronization"
        BARRIER["Warp-level barriers<br/>__syncwarp()"]
        ATOMIC["Atomic operations<br/>Inter-warp coordination"]
    end
    
    SENDER_ROLE --> ATOMIC
    FORWARDER_ROLE --> BARRIER
    COUNTER_ROLE --> ATOMIC
    RECEIVER_ROLE --> ATOMIC
    PACKER_ROLE --> BARRIER
    
    style SENDER_ROLE fill:#f9f9f9
    style FORWARDER_ROLE fill:#f9f9f9
    style RECEIVER_ROLE fill:#f9f9f9
```

**Sources:** [ep/src/internode.cu:400-800](), [ep/src/internode_ll.cu:100-500]()

### Sender Warps

Sender warps (typically warps 0 to N-1) handle token processing and RDMA posting in dispatch kernels.

**Responsibilities:**
1. **Load and process source tokens** ([ep/src/internode.cu:540-600]())
2. **Apply FP8 quantization** if enabled ([ep/src/internode.cu:550-600]())
3. **Determine destination rank and expert** from `topk_idx` ([ep/src/internode.cu:620-650]())
4. **Atomically allocate slot** in remote buffer ([ep/src/internode_ll.cu:195-200]())
5. **Post RDMA write** via D2H queue ([ep/src/internode.cu:650-700]())

**Per-Warp State:**

Each sender warp maintains:
- Current token index being processed
- FP8 scale factors (if quantization enabled)
- Destination metadata (rank, expert, slot)

**Load Balancing:**

Tokens are distributed round-robin across sender warps by SM:

```cpp
for (int token_idx = sm_id; token_idx < num_tokens; token_idx += num_sms) {
    // Each SM processes every Nth token
    // Within SM, warps cooperate on processing
}
```

**Sources:** [ep/src/internode.cu:540-700](), [ep/src/internode_ll.cu:112-235]()

### Forwarder Warps

Forwarder warps handle intra-node token routing via NVLink, bypassing RDMA for same-node transfers.

**NVLink Fast Path ([ep/src/internode_ll.cu:208-230]()):**

```cpp
auto const dst_p2p_ptr = ipc_rdma_base_ptrs
    ? uccl::get_ipc_p2p_ptr(dst_ptr, ipc_rdma_base_ptrs, 
                             rank, dst_rank, max_nvl_peers, 0)
    : 0;

if (dst_p2p_ptr == 0) {
    // Inter-node: use RDMA (handled by sender role)
    uccl::nvshmemi_ibgda_put_nbi_warp(/* ... */);
} else {
    // Intra-node: direct memory copy via IPC
    auto const* src_int4_ptr = reinterpret_cast<int4 const*>(src_ptr);
    auto* dst_int4_ptr = reinterpret_cast<int4*>(dst_p2p_ptr);
    
    // Warp-cooperative vectorized copy
    UNROLLED_WARP_COPY(8, lane_id, num_int4_per_msg, 
                       dst_int4_ptr, src_int4_ptr, 
                       ld_nc_global, st_na_global);
}
```

**IPC Pointer Translation ([ep/include/ep_utils.cuh:800-900]()):**

```cpp
__device__ __forceinline__ uint64_t get_ipc_p2p_ptr(
    uint64_t dst_ptr, void** ipc_rdma_base_ptrs,
    int src_rank, int dst_rank, int max_nvl_peers, int offset) 
{
    int src_node = src_rank / max_nvl_peers;
    int dst_node = dst_rank / max_nvl_peers;
    
    if (src_node != dst_node) return 0;  // Different nodes
    
    int dst_local_rank = dst_rank % max_nvl_peers;
    void* dst_base = ipc_rdma_base_ptrs[dst_local_rank];
    
    if (dst_base == nullptr) return 0;  // IPC not established
    
    return reinterpret_cast<uint64_t>(dst_base) + (dst_ptr - offset);
}
```

**Sources:** [ep/src/internode_ll.cu:208-230](), [ep/include/ep_utils.cuh:800-900]()

### Counter Warp

A dedicated warp (typically the last warp in each SM) aggregates expert token counts.

**Counting Logic ([ep/src/internode_ll.cu:236-278]()):**

```cpp
if (warp_id == num_warps - 1) {
    int expert_count[kNumMaxWarpGroups] = {0};
    auto const expert_begin_idx = sm_id * num_warp_groups;
    auto const expert_end_idx = 
        min(expert_begin_idx + num_warp_groups, num_experts);
    
    // Per-lane counting
    for (int i = lane_id; i < num_tokens * num_topk; i += WARP_SIZE) {
        auto idx = static_cast<int>(__ldg(topk_idx + i));
        if (idx >= expert_begin_idx and idx < expert_end_idx)
            expert_count[idx - expert_begin_idx]++;
    }
    
    // Warp reduce
    for (int i = expert_begin_idx; i < expert_end_idx; ++i) {
        auto sum = warp_reduce_sum(expert_count[i - expert_begin_idx]);
        if (lane_id == 0) {
            shared_num_tokens_sent_per_expert[i - expert_begin_idx] = sum;
            atomic_add_release_global(
                atomic_finish_counter_per_expert + i,
                FINISHED_SUM_TAG - sum);
        }
    }
}
```

This enables the combine phase to know how many tokens to expect per expert without explicit messaging.

**Sources:** [ep/src/internode_ll.cu:236-278]()

### Receiver Warps

Receiver warps in combine kernels poll for incoming data and unpack it.

**Polling Strategy ([ep/src/internode_ll.cu:600-750]()):**

```cpp
// Per-expert polling
for (int expert_idx = warp_start; expert_idx < warp_end; ++expert_idx) {
    int expected_count = num_tokens_for_expert[expert_idx];
    
    // Busy-wait with timeout
    uint64_t start_cycles = clock64();
    while (true) {
        int current = ld_acquire_global(atomic_counter + expert_idx);
        if (current >= expected_count) break;
        
        if (clock64() - start_cycles > NUM_TIMEOUT_CYCLES) {
            printf("[combine] timeout waiting for expert %d\n", expert_idx);
            trap();
        }
    }
    
    // Data ready, proceed with unpacking
    // ...
}
```

**Multi-Rank Aggregation ([ep/src/internode.cu:1950-2100]()):**

Tokens from multiple source ranks are gathered:

```cpp
// For each contributing source rank
for (int src_rank = 0; src_rank < num_ranks; ++src_rank) {
    int num_tokens_from_src = layout_info[expert_idx][src_rank];
    if (num_tokens_from_src == 0) continue;
    
    uint64_t src_offset = calculate_offset(expert_idx, src_rank);
    uint64_t dst_offset = calculate_dst_offset(expert_idx, accumulated_count);
    
    // Vectorized copy
    for (int t = lane_id; t < num_tokens_from_src; t += WARP_SIZE) {
        auto* src = reinterpret_cast<int4*>(rdma_buffer + src_offset + t * stride);
        auto* dst = reinterpret_cast<int4*>(output_buffer + dst_offset + t * stride);
        *dst = *src;
    }
    
    accumulated_count += num_tokens_from_src;
}
```

**Sources:** [ep/src/internode_ll.cu:600-750](), [ep/src/internode.cu:1950-2100]()

---

## Performance Characteristics

### Latency Analysis

**Dispatch Latency Breakdown (Low-Latency Mode):**

| Phase | Latency | Notes |
|-------|---------|-------|
| FP8 cast + metadata write | ~10-20 µs | Per-token processing |
| D2H queue enqueue | ~1-2 µs | Lock-free atomic |
| CPU proxy dequeue | ~5-10 µs | Polling frequency dependent |
| RDMA post latency | ~2-5 µs | Hardware dependent |
| Network transfer | ~50-100 µs | Depends on message size and network |
| Remote atomic update | ~2-5 µs | Hardware atomic |
| **Total (inter-node)** | **136-300 µs** | Measured on H200/CX7 |
| **Total (intra-node)** | **20-50 µs** | Via NVLink IPC |

**Combine Latency:**

Combine polling adds minimal overhead (~10-30 µs) as it overlaps with computation on remote GPUs.

**Sources:** [ep/bench/test_low_latency.py:1-700]()

### Throughput Analysis

**Normal Mode Throughput:**

| Configuration | Dispatch Throughput | Combine Throughput | Bottleneck |
|---------------|--------------------|--------------------|------------|
| 8-node, bf16 | 55-65 GB/s | 50-60 GB/s | Network bandwidth |
| 8-node, fp8 | 100-120 GB/s | 90-110 GB/s | GPU memory bandwidth |
| Intra-node only | 280-320 GB/s | 280-320 GB/s | NVLink bandwidth |

**Factors Affecting Throughput:**

1. **Message Size**: Larger messages amortize RDMA overhead
2. **Batch Size**: Larger batches enable better pipelining
3. **FP8 Quantization**: Reduces data volume by 2x
4. **Multi-QP**: Multiple queue pairs increase parallelism

**Sources:** [ep/bench/test_internode.py:1-800]()

### Scalability

**Weak Scaling (Constant Tokens per GPU):**

| Nodes | Total Tokens | Dispatch Time | Efficiency |
|-------|--------------|---------------|------------|
| 2 | 8K | 1.2 ms | 100% |
| 4 | 16K | 1.3 ms | 92% |
| 8 | 32K | 1.5 ms | 80% |
| 16 | 64K | 1.8 ms | 67% |

Efficiency drops due to increased network contention and synchronization overhead.

**Strong Scaling (Fixed Total Tokens):**

Strong scaling is limited by minimum batch size per GPU and synchronization costs.

**Sources:** [ep/bench/test_internode.py:1-800]()

---

## Code Organization

### Key Files

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `ep/src/internode.cu` | Normal-mode dispatch/combine kernels | ~2500 |
| `ep/src/internode_ll.cu` | Low-latency dispatch/combine kernels | ~1500 |
| `ep/src/intranode.cu` | NVLink-only communication kernels | ~1000 |
| `ep/include/uccl_ibgda.cuh` | GPU-side RDMA posting API | ~300 |
| `ep/include/ep_utils.cuh` | GPU utility functions and macros | ~1000 |
| `ep/src/rdma.cpp` | CPU proxy RDMA posting logic | ~3000 |
| `ep/include/rdma.hpp` | Immediate value structures | ~500 |
| `ep/include/d2h_queue_device.cuh` | Device-side D2H queue | ~300 |
| `ep/include/d2h_queue_host.hpp` | Host-side D2H queue | ~200 |

**Sources:** File paths as listed above

### Kernel Launch Configuration

**Dispatch Kernel Launch ([ep/src/uccl_ep.cc:570-620]()):**

```cpp
// Normal mode: 1 SM for notify, remaining for data transfer
int num_sms = config.num_sms;
int notify_sms = 1;
int dispatch_sms = num_sms - notify_sms;

SETUP_LAUNCH_CONFIG(num_sms, 1024, stream);
LAUNCH_KERNEL(&cfg, internode::dispatch<false, false, kHidden, kNumRDMARanks>,
              /* kernel arguments */);
```

**Low-Latency Kernel Launch ([ep/src/uccl_ep.cc:800-850]()):**

```cpp
// Low-latency: maximize parallelism, use cooperative launch
int num_sms = prop.multiProcessorCount;
int num_warp_groups = 16;  // or configurable
int num_warps_per_group = 2;

SETUP_LAUNCH_CONFIG(num_sms, 
                    (num_warp_groups * num_warps_per_group + 1) * 32, 
                    stream);
LAUNCH_KERNEL(&cfg, internode_ll::dispatch<true, false, 7168>,
              /* kernel arguments */);
```

**Sources:** [ep/src/uccl_ep.cc:570-850]()

---

## Summary

UCCL-EP's GPU kernels and internode communication system achieves high performance through:

1. **GPU-Initiated RDMA**: Kernels directly post RDMA operations via D2H queues, eliminating CPU round-trips
2. **Dual Operating Modes**: Normal mode optimizes throughput; low-latency mode minimizes latency
3. **Warp Specialization**: Sender, forwarder, receiver, and counter warps have distinct responsibilities
4. **Efficient Synchronization**: Atomic counters, NVSHMEM barriers, and RDMA immediate values enable low-overhead coordination
5. **Intra-node Fast Path**: IPC-based NVLink transfers bypass RDMA for same-node communication
6. **FP8 Quantization**: Optional on-the-fly quantization reduces bandwidth by 2x

These techniques enable UCCL-EP to achieve 136-300 µs dispatch latencies in low-latency mode and 50-70 GB/s throughput in normal mode for distributed MoE workloads.

---

# Page: EP Benchmarks and AllToAll

# EP Testing and Performance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ep/bench/alltoall/.gitignore](ep/bench/alltoall/.gitignore)
- [ep/bench/alltoall/Makefile](ep/bench/alltoall/Makefile)
- [ep/bench/alltoall/benchmark.cpp](ep/bench/alltoall/benchmark.cpp)
- [ep/bench/alltoall/efa_alltoall_results.md](ep/bench/alltoall/efa_alltoall_results.md)
- [ep/bench/alltoall/launch_bench.py](ep/bench/alltoall/launch_bench.py)
- [ep/bench/alltoall/test_alltoall.cpp](ep/bench/alltoall/test_alltoall.cpp)
- [ep/bench/alltoall/test_alltoall_rail.cpp](ep/bench/alltoall/test_alltoall_rail.cpp)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [p2p/rdma/tests/test_efa_endpoint.cpp](p2p/rdma/tests/test_efa_endpoint.cpp)

</details>



## Purpose and Scope

This page documents the testing infrastructure, benchmark suite, and performance characteristics of the UCCL-EP (Expert Parallelism) system. It covers correctness testing, performance benchmarking across platforms, and continuous integration workflows. For information about EP architecture and API details, see [EP Architecture and Buffer API](#4.1). For details on GPU kernels and communication primitives, see [GPU Kernels and Internode Communication](#4.3).

---

## Test Suite Architecture

The EP testing infrastructure consists of correctness tests, performance benchmarks, and specialized microbenchmarks organized into distinct categories:

```mermaid
graph TB
    subgraph "Test Categories"
        CORRECTNESS["Correctness Tests<br/>test_low_latency.py<br/>test_internode.py"]
        PERF["Performance Benchmarks<br/>bench/test_*.py"]
        MICRO["Microbenchmarks<br/>bench/fifo/"]
    end
    
    subgraph "Test Execution"
        TORCHRUN["torchrun<br/>Multi-GPU launcher"]
        PYTEST["pytest<br/>Test framework"]
    end
    
    subgraph "Verification"
        HASH["Hash-based verification<br/>hash_tensor()"]
        DIFF["Numerical accuracy<br/>calc_diff()"]
        LAYOUT["Layout validation<br/>recv_layout_range"]
    end
    
    subgraph "Performance Metrics"
        BW["Bandwidth (GB/s)<br/>RDMA/NVLink"]
        LAT["Latency (µs)<br/>RTT measurement"]
        MOPS["Throughput (Mops)<br/>FIFO dispatch"]
    end
    
    CORRECTNESS --> TORCHRUN
    PERF --> TORCHRUN
    MICRO --> TORCHRUN
    
    TORCHRUN --> HASH
    TORCHRUN --> DIFF
    TORCHRUN --> LAYOUT
    
    PERF --> BW
    PERF --> LAT
    MICRO --> MOPS
```

**Sources:** [thirdparty/DeepEP/tests/test_low_latency.py:1-229](), [thirdparty/DeepEP/tests/test_internode.py:1-296](), [ep/bench/fifo/benchmark.cpp:1-443]()

### Correctness Test Files

| Test File | Purpose | Key Operations |
|-----------|---------|----------------|
| `test_low_latency.py` | Validates low-latency dispatch/combine kernels | `low_latency_dispatch()`, `low_latency_combine()` with FP8/BF16 |
| `test_internode.py` | Tests normal mode internode communication | `dispatch()`, `combine()`, `get_dispatch_layout()` |
| `test_intranode.py` | Verifies intra-node NVLink forwarding | NVLink-only data paths |

**Sources:** [thirdparty/DeepEP/tests/test_low_latency.py:15-160](), [thirdparty/DeepEP/tests/test_internode.py:16-257]()

### Test Execution Pattern

Tests use `torchrun` for multi-GPU/multi-node execution with the following pattern:

```mermaid
graph LR
    INIT["init_dist()<br/>NCCL initialization"]
    BUFFER["deep_ep.Buffer()<br/>Allocate RDMA buffers"]
    DISPATCH["test dispatch<br/>Multiple configurations"]
    COMBINE["test combine<br/>Correctness checks"]
    BENCH["bench_kineto()<br/>Performance profiling"]
    DESTROY["buffer.destroy()<br/>Cleanup"]
    
    INIT --> BUFFER
    BUFFER --> DISPATCH
    DISPATCH --> COMBINE
    COMBINE --> BENCH
    BENCH --> DESTROY
```

**Sources:** [thirdparty/DeepEP/tests/test_low_latency.py:163-194](), [thirdparty/DeepEP/tests/test_internode.py:228-257]()

---

## FIFO Microbenchmark Suite

The FIFO benchmark measures the performance of the Device-to-Host (D2H) command queue used by the EP proxy system. This microbenchmark isolates FIFO dispatch throughput and latency independent of RDMA operations.

### FIFO Test Architecture

```mermaid
graph TB
    subgraph "GPU Kernels"
        THROUGHPUT["fifoThroughputKernel<br/>Batched push operations"]
        LATENCY["fifoLatencyKernel<br/>RTT measurement"]
        BURST["fifoBurstKernel<br/>Maximum throughput"]
        RANDOM["fifoRandomKernel<br/>Multi-FIFO selection"]
        CONTROLLED["fifoControlledMopsKernel<br/>Mops vs latency curve"]
    end
    
    subgraph "Host Proxy"
        MULTIPROXY["MultiFifoProxy<br/>32 FIFOs, 4 threads"]
        POLL["poll() & pop()<br/>Process triggers"]
    end
    
    subgraph "Metrics Collection"
        SAMPLES["ThreadMetrics<br/>push_count, cycles, latency"]
        PERCENTILE["Latency percentiles<br/>P99, avg, min, max"]
    end
    
    THROUGHPUT --> MULTIPROXY
    LATENCY --> MULTIPROXY
    BURST --> MULTIPROXY
    RANDOM --> MULTIPROXY
    CONTROLLED --> MULTIPROXY
    
    MULTIPROXY --> POLL
    POLL --> SAMPLES
    SAMPLES --> PERCENTILE
```

**Sources:** [ep/bench/fifo/benchmark.cpp:56-98](), [ep/bench/fifo/fifo_kernel.cuh:16-115]()

### FIFO Test Modes

The benchmark implements five distinct testing modes:

| Mode | Flag | Kernel | Metric Focus |
|------|------|--------|--------------|
| Throughput | (default) | `fifoThroughputKernel` | Maximum sustained Mops with batching |
| RTT Latency | `-l` | `fifoLatencyKernel` | Round-trip time with immediate polling |
| Burst | `-b` | `fifoBurstKernel` | Maximum push rate without polling |
| Random | `-r` | `fifoRandomKernel` | Multi-FIFO contention |
| Controlled Mops | `-c` | `fifoControlledMopsKernel` | Latency vs throughput trade-off |

**Sources:** [ep/bench/fifo/benchmark.cpp:356-425](), [ep/bench/fifo/fifo_kernel.cuh:1-425]()

### FIFO Configuration

```mermaid
graph LR
    CONFIG["BenchmarkConfig"]
    
    CONFIG --> THREADS["num_threads<br/>1-1024 GPU threads"]
    CONFIG --> SIZE["fifo_size<br/>2048-4096 slots"]
    CONFIG --> BATCH["batch_size<br/>32 in-flight requests"]
    CONFIG --> DURATION["test_duration_ms<br/>3000-5000 ms"]
    
    THREADS --> FIFOS["32 FIFOs<br/>SM-to-FIFO mapping"]
    FIFOS --> PROXIES["4 proxy threads<br/>8 FIFOs each"]
```

**Sources:** [ep/bench/fifo/benchmark.cpp:31-43](), [ep/bench/fifo/benchmark.cpp:176-180]()

### Network Latency Benchmark

A complementary benchmark (`network_latency_bench.cpp`) measures raw RDMA/RoCE network latency without GPU involvement:

```mermaid
graph TB
    CONTEXT["RDMAContext<br/>Per-thread QP setup"]
    BUFFER["GPU buffer<br/>64 MB allocated"]
    EXCHANGE["exchange_connection_info()<br/>QP/MR exchange"]
    THREADS["working_thread()<br/>Post & poll WRs"]
    METRICS["ThreadMetrics<br/>latency_samples_ns"]
    
    CONTEXT --> BUFFER
    BUFFER --> EXCHANGE
    EXCHANGE --> THREADS
    THREADS --> METRICS
```

**Sources:** [ep/bench/fifo/network_latency_bench.cpp:51-68](), [ep/bench/fifo/network_latency_bench.cpp:498-661]()

---

## Performance Benchmarking

### Benchmark Execution Commands

#### Intranode Test (NVLink-only)
```bash
torchrun --standalone --nproc_per_node=8 \
  bench/test_intranode.py --num-tokens 4096 \
  --hidden 7168 --num-topk 8 --num-experts 256
```

#### Internode Low-Latency Test
```bash
torchrun --nnodes=4 --nproc_per_node=8 --node_rank=<rank> \
  --master_addr=<ip> --master_port=12355 \
  bench/test_low_latency.py --num-tokens=128 \
  --hidden=7168 --num-topk=8 --num-experts=288
```

#### Internode Normal Mode (Throughput)
```bash
torchrun --nnodes=4 --nproc_per_node=8 --node_rank=<rank> \
  --master_addr=<ip> --master_port=12355 \
  bench/test_internode.py --num-tokens=4096 \
  --hidden=7168 --num-topk=8 --num-experts=288 --test-ll-compatibility
```

**Sources:** [ep/README.md:86-113]()

### Benchmark Utility Functions

The test suite provides reusable benchmarking utilities:

```mermaid
graph TB
    subgraph "Timing Functions"
        BENCH["bench()<br/>L2 cache flushing<br/>50 warmup + 50 test"]
        KINETO["bench_kineto()<br/>PyTorch profiler<br/>Kernel-level timing"]
    end
    
    subgraph "Verification"
        HASH_T["hash_tensor()<br/>Deterministic checksum"]
        CALC_DIFF["calc_diff()<br/>Cosine similarity"]
        CAST["per_token_cast_to_fp8()<br/>per_token_cast_back()"]
    end
    
    subgraph "Distributed"
        INIT["init_dist()<br/>init_dist_under_torchrun()"]
        IB["detect_ib_hca()<br/>Auto-detect mlx5_*"]
    end
    
    BENCH --> HASH_T
    KINETO --> CALC_DIFF
    INIT --> IB
```

**Sources:** [thirdparty/DeepEP/tests/utils.py:109-243]()

---

## Performance Results

### Normal Mode (Throughput-Optimized)

Normal mode kernels use NVLink forwarding for intra-node communication and RDMA for inter-node transfers, optimized for training workloads with large batch sizes (4096 tokens).

#### AWS p5en (H200 + 16x 200Gb/s EFA)

| Type | Dispatch #EP | Bottleneck bandwidth & latency | Combine #EP | Bottleneck bandwidth & latency |
|:----:|:------------:|:------------------------------:|:-----------:|:------------------------------:|
| Intranode | 8  | 320 GB/s (NVLink), 500 µs | 8  | 319 GB/s (NVLink), 973 µs |
| Internode | 16 | 50 GB/s (RDMA), 1196 µs   | 16 | 18 GB/s (RDMA), 6379 µs    |
| Internode | 24 | 53 GB/s (RDMA), 1633 µs   | 24 | 26 GB/s (RDMA), 6365 µs    |
| Internode | 32 | 54 GB/s (RDMA), 2022 µs   | 32 | 43 GB/s (RDMA), 4899 µs    |

**Configuration:** 4096 tokens/batch, 7168 hidden, top-4 groups, top-8 experts, FP8 dispatch, BF16 combine

**Sources:** [ep/README.md:118-131]()

#### AWS p6-b200 (B200 + 8x 400Gb/s EFA)

| Type | Dispatch #EP | Bottleneck bandwidth & latency | Combine #EP | Bottleneck bandwidth & latency |
|:----:|:------------:|:------------------------------:|:-----------:|:------------------------------:|
| Intranode | 8  | 280 GB/s (NVLink), 571 µs | 8  | 426 GB/s (NVLink), 727 µs |
| Internode | 16 | 53 GB/s (RDMA), 1141 µs   | 16 | 60 GB/s (RDMA), 1965 µs    |
| Internode | 24 | 53 GB/s (RDMA), 1637 µs   | 24 | 59 GB/s (RDMA), 2887 µs    |
| Internode | 32 | 53 GB/s (RDMA), 2072 µs   | 32 | 57 GB/s (RDMA), 3724 µs    |

**Sources:** [ep/README.md:133-142]()

#### AMD MI300X with CX7 InfiniBand

| Type | FP8 Dispatch #EP | Bottleneck bandwidth | BF16 Dispatch #EP | Bottleneck bandwidth | Combine #EP | Bottleneck bandwidth |
|:----:|:----------------:|:--------------------:|:-----------------:|:--------------------:|:-----------:|:--------------------:|
| Internode | 16 | 71 GB/s (RDMA) | 16 | 81 GB/s (RDMA) | 16 | 54 GB/s (RDMA) |
| Internode | 32 | 57 GB/s (RDMA) | 32 | 60 GB/s (RDMA) | 32 | 57 GB/s (RDMA) |

**Sources:** [ep/README.md:144-149]()

#### AMD MI300X with Broadcom Thor2

| Type | FP8 Dispatch #EP | Bottleneck bandwidth | BF16 Dispatch #EP | Bottleneck bandwidth | Combine #EP | Bottleneck bandwidth |
|:----:|:----------------:|:--------------------:|:-----------------:|:--------------------:|:-----------:|:--------------------:|
| Internode | 16 | 71 GB/s (RDMA) | 16 | 81 GB/s (RDMA) | 16 | 45 GB/s (RDMA) |
| Internode | 32 | 49 GB/s (RDMA) | 32 | 55 GB/s (RDMA) | 32 | 50 GB/s (RDMA) |

**Sources:** [ep/README.md:151-156]()

---

### Low-Latency Mode (Inference-Optimized)

Low-latency mode bypasses NVLink forwarding and uses pure RDMA for minimal end-to-end latency, optimized for inference with small batch sizes (128 tokens).

#### AMD MI300X with CX7 InfiniBand

| Dispatch #EP | Latency | RDMA bandwidth | Combine #EP | Latency | RDMA bandwidth |
|:------------:|:-------:|:--------------:|:-----------:|:-------:|:--------------:|
| 8  | 65 µs  | 114 GB/s | 8  | 92 µs  | 157 GB/s |
| 16 | 136 µs | 55 GB/s  | 16 | 207 µs | 70 GB/s  |
| 32 | 224 µs | 30 GB/s  | 32 | 341 µs | 42 GB/s  |

**Sources:** [ep/README.md:160-167]()

#### AWS p6-b200 (B200 + 8x 400Gb/s EFA)

| Dispatch #EP | Latency | RDMA bandwidth | Combine #EP | Latency | RDMA bandwidth |
|:------------:|:-------:|:--------------:|:-----------:|:-------:|:--------------:|
| 16 | 228 µs | 33 GB/s | 16 | 318 µs | 46 GB/s |
| 24 | 448 µs | 17 GB/s | 24 | 566 µs | 26 GB/s |
| 32 | 406 µs | 19 GB/s | 32 | 617 µs | 24 GB/s |

**Sources:** [ep/README.md:169-177]()

#### AWS p5en (H200 + 16x 200Gb/s EFA)

| Dispatch #EP | Latency | RDMA bandwidth | Combine #EP | Latency | RDMA bandwidth |
|:------------:|:-------:|:--------------:|:-----------:|:-------:|:--------------:|
| 16 | 226 µs | 36 GB/s | 16 | 293 µs | 48 GB/s |
| 24 | 386 µs | 20 GB/s | 24 | 580 µs | 26 GB/s |
| 32 | 465 µs | 16 GB/s | 32 | 694 µs | 25 GB/s |

**Configuration:** 128 tokens/batch, 7168 hidden, top-8 experts, FP8 dispatch, BF16 combine (DeepSeek-V3 inference setting)

**Sources:** [ep/README.md:179-187]()

---

## Performance Analysis Workflow

The test suite implements automated performance tuning by sweeping configuration parameters:

```mermaid
graph TB
    subgraph "Dispatch Tuning"
        D_SWEEP["Parameter sweep<br/>nvl_chunk: 4-44<br/>rdma_chunk: 4-32"]
        D_BENCH["bench_kineto()<br/>Measure dispatch & notify"]
        D_BEST["Best configuration<br/>Minimize latency"]
    end
    
    subgraph "Combine Tuning"
        C_SWEEP["Parameter sweep<br/>nvl_chunk: 1-7<br/>rdma_chunk: 8-32"]
        C_BENCH["bench_kineto()<br/>Measure combine & notify"]
        C_BEST["Best configuration<br/>Minimize latency"]
    end
    
    subgraph "Metrics"
        RDMA_BW["RDMA bandwidth<br/>bytes / time"]
        NVL_BW["NVLink bandwidth<br/>bytes / time"]
        NOTIFY_T["Notify latency<br/>Metadata exchange"]
    end
    
    D_SWEEP --> D_BENCH
    D_BENCH --> RDMA_BW
    D_BENCH --> NVL_BW
    D_BENCH --> NOTIFY_T
    D_BENCH --> D_BEST
    
    D_BEST --> C_SWEEP
    C_SWEEP --> C_BENCH
    C_BENCH --> C_BEST
```

**Sources:** [thirdparty/DeepEP/tests/test_internode.py:177-224]()

### Tuning Example Output

```
[tuning] SMs 24, NVL chunk 8, RDMA chunk 16, transmit: 1196.23 us, notify: 45.67 us, 
         BW: 50.12 GB/s (RDMA), 280.45 GB/s (NVL)
[tuning] Best dispatch (FP8): SMs 24, NVL chunk 8, RDMA chunk 16, 
         transmit: 1141.45 us, notify: 42.31 us, 
         BW: 53.22 GB/s (RDMA), 295.67 GB/s (NVL)
```

**Sources:** [thirdparty/DeepEP/tests/test_internode.py:186-195]()

---

## Build and Test Environments

### Platform-Specific Docker Images

Each platform requires specialized build environments with correct CUDA/ROCm versions and network libraries:

| Platform | Dockerfile | Base Image | Key Dependencies |
|----------|-----------|------------|------------------|
| CUDA (H200/B200) | `docker/Dockerfile.cuda` | `nvidia/cuda:12.8.0-devel` | PyTorch, libibverbs, libefa |
| ROCm (MI300X) | `docker/Dockerfile.rocm` | `rocm/dev-ubuntu-22.04` | PyTorch ROCm7.0, hiredis, hipblas |
| Grace Hopper | `docker/Dockerfile.gh` | `nvidia/cuda:12.4.1-devel` | PyTorch 2.6.0+cu126, ARM64 |
| EFA | `docker/Dockerfile.efa` | `nvidia/cuda:12.8.0-devel` | AWS EFA installer 1.42.0, libfabric |
| TheRock | `docker/Dockerfile.therock` | `ghcr.io/rocm/therock_build` | manylinux + ROCm wheel build |

**Sources:** [docker/Dockerfile.cuda:1-52](), [docker/Dockerfile.rocm:1-54](), [docker/Dockerfile.gh:1-51](), [docker/Dockerfile.efa:1-76](), [docker/Dockerfile.therock:1-17]()

### Build Configuration

The EP Makefile detects platform features and configures builds accordingly:

```mermaid
graph TB
    MAKEFILE["ep/Makefile"]
    
    MAKEFILE --> DETECT["Platform detection<br/>GH200, EFA, GPU arch"]
    
    DETECT --> FLAGS_GH["GH200: -DUSE_GRACE_HOPPER"]
    DETECT --> FLAGS_EFA["EFA: -DEFA -I/opt/amazon/efa"]
    DETECT --> FLAGS_SM["GPU arch: -arch=sm_$(SM)"]
    
    FLAGS_GH --> COMPILE["Compile C++/CUDA<br/>proxy.cpp, internode_ll.cu"]
    FLAGS_EFA --> COMPILE
    FLAGS_SM --> COMPILE
    
    COMPILE --> LINK["Link Python module<br/>ep.so with libtorch"]
```

**Sources:** [ep/Makefile:1-114]()

---

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline performs remote builds and verification on GPU instances:

```mermaid
graph LR
    TRIGGER["Push/PR to main"]
    SSH["Setup SSH to l4-sky-test-01"]
    SYNC["rsync code to remote"]
    BUILD["./build_and_install.sh<br/>cuda all 3.11"]
    VERIFY["grep installation success<br/>in build.log"]
    ARTIFACT["Upload build.log artifact"]
    
    TRIGGER --> SSH
    SSH --> SYNC
    SYNC --> BUILD
    BUILD --> VERIFY
    VERIFY --> ARTIFACT
```

**Workflow file:** `.github/workflows/uccl-build-test.yml`

**Key steps:**
1. Checkout code and initialize submodules
2. Setup SSH key for remote GPU host
3. Sync source files (ep, collective/rdma, p2p)
4. Execute build script in conda environment
5. Verify successful installation string in logs
6. Upload build.log as artifact

**Sources:** [.github/workflows/uccl-build-test.yml:1-96]()

---

## Testing Best Practices

### Correctness Verification Methods

The test suite employs multiple verification strategies:

| Method | Implementation | Use Case |
|--------|---------------|----------|
| Hash-based | `hash_tensor()` - XOR of int64 view | Deterministic repeatability |
| Numerical diff | `calc_diff()` - Cosine similarity | FP8/BF16 precision validation |
| Layout checks | `recv_layout_range` validation | Expert routing correctness |
| Token counting | `cumulative_local_expert_recv_stats` | Message count verification |

**Sources:** [thirdparty/DeepEP/tests/utils.py:62-66](), [thirdparty/DeepEP/tests/utils.py:245-247](), [thirdparty/DeepEP/tests/test_low_latency.py:38-93]()

### Multi-Node Testing Setup

Tests coordinate distributed execution using PyTorch distributed primitives:

```mermaid
graph TB
    ENV["Environment variables<br/>RANK, WORLD_SIZE<br/>MASTER_ADDR, MASTER_PORT"]
    
    INIT["dist.init_process_group()<br/>backend='nccl'"]
    
    GROUP["dist.new_group()<br/>All ranks"]
    
    BUFFER["deep_ep.Buffer()<br/>Collective initialization"]
    
    BARRIER["dist.barrier()<br/>Phase synchronization"]
    
    ENV --> INIT
    INIT --> GROUP
    GROUP --> BUFFER
    BUFFER --> BARRIER
```

**Example:**
```python
rank, num_ranks, group = init_dist_under_torchrun(local_rank, num_local_ranks)
buffer = deep_ep.Buffer(group, num_rdma_bytes=int(2e9), 
                       low_latency_mode=True,
                       num_qps_per_rank=num_experts // num_ranks)
```

**Sources:** [thirdparty/DeepEP/tests/test_low_latency.py:163-176](), [thirdparty/DeepEP/tests/test_internode.py:228-241]()

---

## Running Tests Locally

### Prerequisites

1. Install dependencies:
```bash
./install_deps.sh  # Tested on p5en, p6-b200, MI300X
```

2. Build and install:
```bash
python setup.py install  # Direct installation
# OR
bash build_and_install.sh cuda ep  # Docker-based build
```

3. Verify installation:
```bash
python -c "import torch; import uccl.ep"
```

**Sources:** [ep/README.md:5-48]()

### Test Execution Examples

#### Single-Node Intranode Test
```bash
torchrun --standalone --nproc_per_node=8 \
  bench/test_intranode.py \
  --num-tokens 4096 --hidden 7168 \
  --num-topk 8 --num-experts 256
```

#### Multi-Node Low-Latency Test
```bash
# Node 0 (rank 0)
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=0 \
  --master_addr=10.0.0.1 --master_port=12355 \
  bench/test_low_latency.py \
  --num-tokens=128 --hidden=7168 \
  --num-topk=8 --num-experts=288

# Node 1 (rank 1)
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=1 \
  --master_addr=10.0.0.1 --master_port=12355 \
  bench/test_low_latency.py \
  --num-tokens=128 --hidden=7168 \
  --num-topk=8 --num-experts=288
```

#### FIFO Microbenchmark
```bash
# Throughput mode (default)
torchrun --nproc_per_node=8 --standalone \
  bench/fifo/benchmark.py

# Latency mode
torchrun --nproc_per_node=8 --standalone \
  bench/fifo/benchmark.py -l

# Controlled Mops mode
torchrun --nproc_per_node=8 --standalone \
  bench/fifo/benchmark.py -c
```

**Sources:** [ep/README.md:86-113](), [ep/bench/fifo/benchmark.py:1-33]()

---

# Page: vLLM Integration

# vLLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ep/bench/vllm/README.md](ep/bench/vllm/README.md)
- [ep/bench/vllm/launch_vllm.sh](ep/bench/vllm/launch_vllm.sh)
- [ep/deep_ep_wrapper/README.md](ep/deep_ep_wrapper/README.md)

</details>



This page covers how UCCL-EP integrates with [vLLM](https://github.com/vllm-project/vllm) to serve large Mixture-of-Experts (MoE) models such as DeepSeek-V3 across multiple nodes using Expert Parallelism (EP). The integration replaces DeepEP's communication kernels with UCCL-EP's drop-in wrapper and provides a launch script for multi-node deployments.

For background on the UCCL-EP system itself, see [EP Architecture and Buffer API](#4.1) and [Proxy and RDMA System](#4.2). For EP benchmarking outside of vLLM, see [EP Benchmarks and AllToAll](#4.4).

---

## Integration Overview

UCCL-EP plugs into vLLM's expert-parallel all-to-all communication path via the `VLLM_ALL2ALL_BACKEND` environment variable. vLLM selects its all-to-all communication implementation at startup; UCCL-EP's `deep_ep_wrapper` package presents the same Python interface as DeepEP so that vLLM needs no code changes.

**Component map:**

```mermaid
graph TD
    vLLM["vLLM\n(vllm serve --enable-expert-parallel)"]
    backend["VLLM_ALL2ALL_BACKEND\nenvironment variable"]
    deepep_wrapper["ep/deep_ep_wrapper\ndrop-in DeepEP Python package"]
    uccl_ep["uccl (Python wheel)\nuccl_ep C++ extension"]
    proxy["Proxy / UcclProxy\nproxy.cpp / uccl_proxy.cpp"]
    rdma["RDMA Layer\nrdma.cpp"]
    nccl_fallback["NCCL / AWS OFI-NCCL\nallgather_reducescatter backend"]

    vLLM --> backend
    backend -->|"deepep_high_throughput\ndeepep_low_latency"| deepep_wrapper
    backend -->|"allgather_reducescatter"| nccl_fallback
    deepep_wrapper --> uccl_ep
    uccl_ep --> proxy
    proxy --> rdma
```

Sources: [ep/bench/vllm/README.md:88-95](), [ep/deep_ep_wrapper/README.md:1-15]()

---

## Components

### `deep_ep_wrapper` — DeepEP Drop-In Replacement

Located at `ep/deep_ep_wrapper/`, this Python package wraps the UCCL-EP C++ extension and exposes the same API surface that vLLM expects from DeepEP. It is installed separately from the core UCCL wheel.

**Build and install order:**

| Step | Command | Location |
|------|---------|----------|
| 1. Build UCCL-EP | `bash build.sh cuda ep` | repo root |
| 2. Install UCCL wheel | `uv pip install wheelhouse-cuda/uccl-*.whl` | repo root |
| 3. Install wrapper | `python setup.py install` | `ep/deep_ep_wrapper/` |

Sources: [ep/deep_ep_wrapper/README.md:1-15]()

### `launch_vllm.sh` — Multi-Node Launch Script

[ep/bench/vllm/launch_vllm.sh:1-136]() is a unified Bash script that handles both the primary (head) node and secondary (worker) nodes. It exports all required environment variables and invokes `vllm serve` with the appropriate flags.

**Signature:**
```
launch_vllm.sh <head|worker> <NODE1_IP> [RPC_PORT] [MODEL] [BACKEND]
               [TOTAL_DP_SIZE] [LOCAL_DP_SIZE] [LOCAL_TP_SIZE]
               [API_SERVERS_or_START_RANK]
```

**Role difference:**

| Argument/Flag | `head` | `worker` |
|---|---|---|
| 9th positional | `API_SERVERS` | `START_RANK` |
| `--data-parallel-start-rank` | not set (defaults to 0) | set to `START_RANK` |
| `--api-server-count` | set to `API_SERVERS` | not set |
| `--headless` | not set | set |

Sources: [ep/bench/vllm/launch_vllm.sh:37-48](), [ep/bench/vllm/launch_vllm.sh:113-136]()

### DeepGEMM — Optional JIT Kernel Library

DeepGEMM provides JIT-compiled GEMM kernels for MoE expert computation. It is enabled by setting `VLLM_USE_DEEP_GEMM=1` and pointing `DG_JIT_CACHE_DIR` at a per-node local directory (not a shared NFS path). Without DeepGEMM, vLLM falls back to standard CUDA GEMM kernels.

Sources: [ep/bench/vllm/launch_vllm.sh:55-56](), [ep/bench/vllm/launch_vllm.sh:75-76](), [ep/bench/vllm/README.md:42-57]()

---

## All-to-All Backends

vLLM selects a backend via `--all2all-backend` (or `VLLM_ALL2ALL_BACKEND`). The four supported backends and their characteristics:

| Backend | Transport | Use Case | Notes |
|---|---|---|---|
| `deepep_high_throughput` | UCCL-EP RDMA | Multi-node prefill | Grouped GEMM, high batch throughput |
| `deepep_low_latency` | UCCL-EP RDMA | Multi-node decode | CUDA graph compatible |
| `pplx` | pplx-kernels | Single-node or intra-node | Chunked prefill support |
| `allgather_reducescatter` | NCCL / OFI-NCCL | Multi-node fallback | Works on IB and EFA networks |

The `deepep_high_throughput` and `deepep_low_latency` backends route through `deep_ep_wrapper` → UCCL-EP C++ extension → `Proxy` threads → RDMA QPs. The `allgather_reducescatter` backend bypasses UCCL-EP entirely and uses NCCL.

Sources: [ep/bench/vllm/README.md:88-95]()

---

## Environment Variables

The following variables must be set before calling `launch_vllm.sh`. The script sets several of them internally; others must be edited in the script before running.

**Diagram: environment variable routing**

```mermaid
graph LR
    subgraph "Network Routing"
        GLOO["GLOO_SOCKET_IFNAME\ne.g. enp71s0"]
        NCCL_IF["NCCL_SOCKET_IFNAME\ne.g. enp71s0"]
        TP_IF["TP_SOCKET_IFNAME\ne.g. enp71s0"]
    end

    subgraph "Backend Selection"
        BACKEND_VAR["VLLM_ALL2ALL_BACKEND\nor --all2all-backend CLI"]
    end

    subgraph "NCCL / EFA Tuning"
        NCCL_NET["NCCL_NET_PLUGIN\n/opt/amazon/ofi-nccl/lib/libnccl-net.so"]
        CHUNK["NCCL_P2P_NET_CHUNKSIZE=524288"]
        BUFF["NCCL_BUFFSIZE=8388608"]
    end

    subgraph "DeepGEMM"
        DG_USE["VLLM_USE_DEEP_GEMM=1"]
        DG_CACHE["DG_JIT_CACHE_DIR\n(per-node local path)"]
    end

    subgraph "Timeouts"
        TIMEOUT["VLLM_ENGINE_READY_TIMEOUT_S=3600"]
    end
```

| Variable | Description | Set By |
|---|---|---|
| `GLOO_SOCKET_IFNAME` | Interface for PyTorch `gloo` backend (rank discovery) | User (edit script) |
| `NCCL_SOCKET_IFNAME` | Interface for NCCL TCP bootstrap | User (edit script) |
| `TP_SOCKET_IFNAME` | Interface for tensor-parallel communication | User (edit script) |
| `VLLM_ALL2ALL_BACKEND` | Selects all-to-all communication backend | CLI `--all2all-backend` or env |
| `NCCL_NET_PLUGIN` | Path to AWS OFI-NCCL plugin `.so` | Script (auto-detected) |
| `NCCL_P2P_NET_CHUNKSIZE` | NCCL inter-node chunk size (bytes) | Script |
| `NCCL_BUFFSIZE` | NCCL buffer size (bytes) | Script |
| `VLLM_USE_DEEP_GEMM` | Enable DeepGEMM JIT kernels | Script |
| `DG_JIT_CACHE_DIR` | Per-node directory for DeepGEMM kernel cache | User (edit script) |
| `VLLM_ENGINE_READY_TIMEOUT_S` | Startup timeout in seconds | Script |

Sources: [ep/bench/vllm/launch_vllm.sh:54-76](), [ep/bench/vllm/README.md:98-104]()

---

## Deployment

### Node Roles and Data Flow

```mermaid
sequenceDiagram
    participant "Node 0 (head)" as head
    participant "Node 1+ (worker)" as worker
    participant "vLLM RPC" as rpc

    head->>"vLLM RPC": starts RPC server on NODE1_IP:RPC_PORT
    worker->>"vLLM RPC": connects via --data-parallel-address / --data-parallel-rpc-port
    head->>head: starts API HTTP server (--api-server-count)
    worker->>worker: runs headless (--headless)
    head-->>worker: distributes expert tokens via all2all backend
    worker-->>head: returns combined results
```

Sources: [ep/bench/vllm/launch_vllm.sh:113-136](), [ep/bench/vllm/README.md:109-140]()

### Example: 2-Node, 8-GPU-per-Node DeepSeek-V3

**Node 0 (head):**
```
bash launch_vllm.sh head 172.31.41.55 13345 deepseek-ai/DeepSeek-V3-0324 deepep_high_throughput 2 1 8 1
```

**Node 1 (worker):**
```
bash launch_vllm.sh worker 172.31.41.55 13345 deepseek-ai/DeepSeek-V3-0324 deepep_high_throughput 2 1 8 1
```

**Key vLLM flags used:**

| Flag | Head | Worker |
|---|---|---|
| `--enable-expert-parallel` | ✓ | ✓ |
| `--all2all-backend` | `BACKEND` | `BACKEND` |
| `--tensor-parallel-size` | `LOCAL_TP_SIZE` | `LOCAL_TP_SIZE` |
| `--data-parallel-size` | `TOTAL_DP_SIZE` | `TOTAL_DP_SIZE` |
| `--data-parallel-size-local` | `LOCAL_DP_SIZE` | `LOCAL_DP_SIZE` |
| `--data-parallel-address` | `NODE1_IP` | `NODE1_IP` |
| `--data-parallel-rpc-port` | `RPC_PORT` | `RPC_PORT` |
| `--data-parallel-start-rank` | — | `START_RANK` |
| `--api-server-count` | `API_SERVERS` | — |
| `--headless` | — | ✓ |
| `--gpu-memory-utilization` | `0.85` | `0.85` |

Sources: [ep/bench/vllm/launch_vllm.sh:113-136](), [ep/bench/vllm/README.md:119-140]()

---

## Performance Results

The following results were measured on AWS p5en instances running `deepseek-ai/DeepSeek-V3-0324` with 1024 input tokens, 256 output tokens, 10 RPS, and 1000 prompts.

| Backend | Req Throughput (req/s) | Output Tok/s | Mean TTFT (ms) | P99 TTFT (ms) | Mean TPOT (ms) | P99 TPOT (ms) |
|---|---|---|---|---|---|---|
| `allgather_reducescatter` | 8.93 | 2285.11 | 303.50 | 655.98 | 81.11 | 95.55 |
| `deepep_low_latency` (UCCL-EP) | 9.22 | 2359.13 | 278.52 | 775.17 | 59.35 | 78.61 |

UCCL-EP low-latency mode reduces mean TPOT by ~27% compared to the NCCL-based `allgather_reducescatter` backend.

Sources: [ep/bench/vllm/README.md:171-175]()

---

## Installation Checklist

```mermaid
graph TD
    A["Install uv + torch (cu128 or cu130)"]
    B["Install vLLM with EP support\nuv pip install vllm --torch-backend=cu128"]
    C["Install DeepGEMM\ngit clone deepseek-ai/DeepGEMM && ./install.sh"]
    D["Build & install UCCL-EP\nbash build.sh cuda ep\nuv pip install wheelhouse-cuda/uccl-*.whl"]
    E["Install deep_ep_wrapper\ncd ep/deep_ep_wrapper && python setup.py install"]
    F["(AWS only) Verify OFI-NCCL plugin\n/opt/amazon/ofi-nccl/lib/libnccl-net.so"]
    G["Edit launch_vllm.sh\nSet GLOO_SOCKET_IFNAME, NCCL_SOCKET_IFNAME, DG_JIT_CACHE_DIR"]
    H["Run launch_vllm.sh head / worker"]

    A --> B --> C --> D --> E --> F --> G --> H
```

Sources: [ep/bench/vllm/README.md:13-67](), [ep/deep_ep_wrapper/README.md:1-15]()

---

# Page: Experimental: UKernel

# Experimental: UKernel

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experimental/ukernel/Makefile.rocm](experimental/ukernel/Makefile.rocm)
- [experimental/ukernel/README.md](experimental/ukernel/README.md)
- [experimental/ukernel/py/test_p2p.py](experimental/ukernel/py/test_p2p.py)
- [experimental/ukernel/py/test_ukernel.py](experimental/ukernel/py/test_ukernel.py)
- [experimental/ukernel/src/compute/Makefile](experimental/ukernel/src/compute/Makefile)
- [experimental/ukernel/src/compute/benchmarks/bench_result.txt](experimental/ukernel/src/compute/benchmarks/bench_result.txt)
- [experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu](experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu)
- [experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu](experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu)
- [experimental/ukernel/src/compute/fifo/d2c_fifo.hpp](experimental/ukernel/src/compute/fifo/d2c_fifo.hpp)
- [experimental/ukernel/src/compute/fifo/fifo_util.hpp](experimental/ukernel/src/compute/fifo/fifo_util.hpp)
- [experimental/ukernel/src/compute/fifo/sm_fifo.cc](experimental/ukernel/src/compute/fifo/sm_fifo.cc)
- [experimental/ukernel/src/compute/fifo/sm_fifo.h](experimental/ukernel/src/compute/fifo/sm_fifo.h)
- [experimental/ukernel/src/compute/fifo/sm_fifo_device.h](experimental/ukernel/src/compute/fifo/sm_fifo_device.h)
- [experimental/ukernel/src/compute/operator.cu](experimental/ukernel/src/compute/operator.cu)
- [experimental/ukernel/src/compute/operator.h](experimental/ukernel/src/compute/operator.h)
- [experimental/ukernel/src/compute/operators/operator.cuh](experimental/ukernel/src/compute/operators/operator.cuh)
- [experimental/ukernel/src/compute/persistent.h](experimental/ukernel/src/compute/persistent.h)
- [experimental/ukernel/src/compute/task.h](experimental/ukernel/src/compute/task.h)
- [experimental/ukernel/src/operator.h](experimental/ukernel/src/operator.h)
- [experimental/ukernel/src/python_bindings.cc](experimental/ukernel/src/python_bindings.cc)
- [experimental/ukernel/src/scheduler.cc](experimental/ukernel/src/scheduler.cc)
- [experimental/ukernel/src/scheduler.h](experimental/ukernel/src/scheduler.h)
- [experimental/ukernel/src/transport/oob.h](experimental/ukernel/src/transport/oob.h)
- [experimental/ukernel/tests/test_main.cc](experimental/ukernel/tests/test_main.cc)

</details>



## Purpose and Scope

UKernel (`experimental/ukernel/`) is an experimental UCCL subsystem whose goal is to **co-schedule communication and compute inside a single persistent GPU kernel**. Rather than launching separate kernels for each collective operation or matrix multiplication, UKernel keeps SMs occupied with a long-lived kernel that polls per-block task queues submitted by the CPU. This eliminates per-launch overhead and creates a framework for overlapping communication and compute at fine granularity.

This page covers the goals, structure, platforms, build instructions, and observed benchmark numbers for the subsystem as a whole. For the GPU-side kernel design, FIFO primitives, and `TaskManager`, see page [5.1](). For the `Operator`/`Scheduler` DAG model, `OperatorFactory`, and Python bindings, see page [5.2]().

UKernel uses the UCCL P2P transport for inter-node communication (see page [3]()) and **ThunderKittens** (`kittens.cuh`) for tile-level GEMM compute primitives.

---

## Design Goals

| Goal | Mechanism |
|---|---|
| Eliminate kernel launch overhead | Single persistent kernel per GPU stays resident |
| Overlap communication and compute | CPU submits COMM and COMPUTE tasks to concurrent queues |
| Support MoE model workflows | Operators for `MoeRouting`, `MoeDispatch`, `MoeExpertGemm`, `MoeCombine` |
| High-performance GEMM | ThunderKittens TK-level-8 tiled matmul via `run_tk_gemm` |
| Cross-platform | CUDA (NVIDIA) and HIP/ROCm (AMD) backends |

---

## Subsystem Layout

```
experimental/ukernel/
├── src/
│   ├── compute/               # GPU kernel, FIFO channels, TaskManager
│   │   ├── operator.cu        # basePersistentKernel, run_copy, run_reduce_inplace
│   │   ├── persistent.h       # PersistentKernel<T> host-side manager
│   │   ├── task.h             # Task, TaskType, CollArgs, GemmArgs, TaskManager
│   │   ├── operators/
│   │   │   └── operator.cuh   # TkMatmulGlobals, run_tk_gemm (ThunderKittens)
│   │   └── fifo/              # c2d_fifo, sm_fifo, d2c_fifo
│   ├── operator.h             # Operator struct, OperatorFactory
│   ├── scheduler.h / .cc      # Scheduler (DAG execution)
│   ├── python_bindings.cc     # pybind11 module "ukernel"
│   └── transport/             # Communicator, oob.h (out-of-band exchange)
├── py/
│   ├── test_ukernel.py        # MoE DAG demo
│   └── test_p2p.py            # P2P send/recv demo
├── tests/
│   └── test_main.cc           # C++ transport test
├── Makefile                   # CUDA build
└── Makefile.rocm              # ROCm/HIP build
```

Sources: [experimental/ukernel/README.md:1-59](), [experimental/ukernel/src/compute/Makefile:1-64](), [experimental/ukernel/Makefile.rocm:1-130]()

---

## Architecture Overview

UKernel has two distinct but related layers. The **Compute Layer** runs on the GPU and manages task execution. The **Runtime Layer** runs on the CPU and manages operator DAGs, scheduling, and transport.

**Component Architecture**

```mermaid
graph TD
    subgraph PythonAPI["Python API (py/)"]
        PY_TEST["test_ukernel.py\ntest_p2p.py"]
        PYBIND_MOD["ukernel module\npython_bindings.cc"]
    end

    subgraph RuntimeLayer["Runtime Layer (src/)"]
        OP_FACTORY["OperatorFactory\noperator.h"]
        OP_STRUCT["Operator\noperator.h"]
        SCHED["Scheduler\nscheduler.h / scheduler.cc"]
        SCHED_CFG["SchedulerConfig\nscheduler.h"]
        COMM["Communicator\ntransport/"]
        EXECUTOR["Executor::run_compute\nscheduler.h (stub)"]
    end

    subgraph ComputeLayer["Compute Layer (src/compute/)"]
        PK["PersistentKernel&lt;Task&gt;\npersistent.h"]
        TM["TaskManager\ntask.h"]
        BPK["basePersistentKernel\noperator.cu"]
        TK_GEMM["run_tk_gemm\noperators/operator.cuh"]
        RUN_COPY["run_copy\noperator.cu"]
        RUN_RED["run_reduce_inplace\noperator.cu"]
    end

    subgraph FIFOs["FIFO Channels (src/compute/fifo/)"]
        C2D["CpuToGpuFifo\nc2d_fifo"]
        SMF["SmFifo\nsm_fifo.h"]
        D2C["Fifo (d2c)\nd2c_fifo.hpp"]
    end

    PY_TEST --> PYBIND_MOD
    PYBIND_MOD --> SCHED
    PYBIND_MOD --> OP_FACTORY
    OP_FACTORY --> OP_STRUCT
    SCHED --> OP_STRUCT
    SCHED --> COMM
    SCHED --> EXECUTOR
    PK --> C2D
    PK --> SMF
    PK --> D2C
    PK --> TM
    C2D --> BPK
    BPK --> TK_GEMM
    BPK --> RUN_COPY
    BPK --> RUN_RED
    TM --> BPK
```

Sources: [experimental/ukernel/src/compute/operator.cu:82-167](), [experimental/ukernel/src/compute/persistent.h:29-308](), [experimental/ukernel/src/scheduler.h:1-152](), [experimental/ukernel/src/operator.h:1-266](), [experimental/ukernel/src/python_bindings.cc:1-163]()

---

## Compute Layer

The compute layer (`src/compute/`) provides the GPU-side infrastructure.

### `PersistentKernel<T>`

`PersistentKernel<T>` ([experimental/ukernel/src/compute/persistent.h:29-308]()) is the host-side manager for one launch of `basePersistentKernel`. It:

- Allocates one `CpuToGpuFifo` per GPU block (CPU → GPU task delivery).
- Allocates one `SmFifo` per GPU block (intra-GPU SM-to-SM communication).
- Allocates one `Fifo` (device-to-CPU) for completion signals.
- Launches `basePersistentKernel` via `gpuLaunchKernel` on `launch()`.
- Accepts tasks via `submit(const T& task)`, which pushes to the per-block FIFO.
- Checks completion with `is_done(blockId, taskId)`.
- Stops the kernel by setting a mapped boolean `d_stopFlag_` / `h_stopFlag_`.

Configuration is through `PersistentKernelConfig`:

| Field | Default | Purpose |
|---|---|---|
| `numBlocks` | 1 | Number of GPU blocks (one FIFO per block) |
| `threadsPerBlock` | 64 | Threads per block |
| `fifoCapacity` | 16 | Depth of each per-block FIFO |
| `smemSize` | 0 | Dynamic shared memory (set higher for TK GEMM) |
| `stream` | `nullptr` | Optionally user-managed stream |

### `basePersistentKernel`

`basePersistentKernel` ([experimental/ukernel/src/compute/operator.cu:82-167]()) is the GPU kernel function. Each block polls its assigned `C2DDeviceHandle` for a `Task`. On receipt, the block dispatches based on `TaskType`:

| `TaskType` | Handler |
|---|---|
| `CollCopy` | `run_copy()` — byte-granularity copy across threads |
| `CollReduce` | `run_reduce_inplace<float>()` or `<__half>()` — element-wise reduction |
| `TkGemm` | `run_tk_gemm()` — ThunderKittens tiled BF16 GEMM |

### `TaskManager`

`TaskManager` ([experimental/ukernel/src/compute/task.h:124-307]()) is a singleton that manages pools of argument descriptors on device memory:

- `CollArgs`: source/destination pointers, byte count, `ReduceType`.
- `MoeArgs`: placeholder (not yet implemented beyond `dummy` field).
- `GemmArgs`: pointer to a device-side `TkMatmulGlobals`, tile row/col counts.

The CPU calls `create_coll_task()`, `create_gemm_task()`, etc., which copy args to device and return a `Task` token. After the kernel finishes, args are returned to the free pool via `free_coll_args()`, `free_gemm_args()`, etc.

### FIFO Channels

Three FIFO types exist for different communication directions:

**FIFO Channel Types**

```mermaid
graph LR
    CPU["CPU Host"]
    GPU_BLK["GPU Block N"]
    OTHER_SM["GPU Block M"]

    CPU -- "CpuToGpuFifo (c2d)\nC2DDeviceHandle&lt;Task&gt;" --> GPU_BLK
    GPU_BLK -- "SmFifo\nSmDeviceHandle&lt;Task&gt;" --> OTHER_SM
    GPU_BLK -- "Fifo (d2c)\nFifoDeviceHandle" --> CPU
```

| FIFO Type | Class (Host) | Device Handle | Direction |
|---|---|---|---|
| CPU→GPU | `CpuToGpuFifo<T>` | `C2DDeviceHandle<T>` | Task submission per block |
| SM→SM | `SmFifo<T>` | `SmDeviceHandle<T>` | Inter-block task broadcasting |
| GPU→CPU | `mscclpp::Fifo` | `FifoDeviceHandle` | Completion notification |

`SmFifo` ([experimental/ukernel/src/compute/fifo/sm_fifo.h:1-38]()) allocates all ring buffers on GPU memory and exposes `poll()` / `pop()` / `push()` / `sync()` device-side methods in `SmDeviceHandle` ([experimental/ukernel/src/compute/fifo/sm_fifo_device.h:1-88]()).

Sources: [experimental/ukernel/src/compute/task.h:1-307](), [experimental/ukernel/src/compute/fifo/sm_fifo.h:1-38](), [experimental/ukernel/src/compute/fifo/sm_fifo_device.h:1-88](), [experimental/ukernel/src/compute/fifo/d2c_fifo.hpp:1-47]()

---

## Runtime Layer

The runtime layer (`src/`) manages the operator DAG from the CPU side.

### Operators and `OperatorFactory`

An `Operator` ([experimental/ukernel/src/operator.h:74-96]()) is a descriptor holding:
- Unique `id` and a `deps` vector of dependency `id` values.
- `OpType`: `P2P`, `Collective`, `Compute`, or `Moe`.
- Optional `p2p_kind`, `collective_kind`, `moe_kind`.
- Input/output `torch::Tensor` vectors.
- `ParallelRule` specifying `num_tasks` (partitions) and `tiles_per_task`.
- String `attrs` map for operation-specific parameters (e.g., `"peer"`, `"offset"`).

`OperatorFactory` ([experimental/ukernel/src/operator.h:98-266]()) provides static factory methods:

| Method | OpType | Kind |
|---|---|---|
| `P2PSend(src, rule, peer_rank, ...)` | `P2P` | `P2PKind::Send` |
| `P2PRecv(dst, rule, peer_rank, ...)` | `P2P` | `P2PKind::Recv` |
| `AllReduce(src, dst, kind, rule)` | `Collective` | `AllReduce` |
| `AllToAll(src, dst, rule)` | `Collective` | `AllToAll` |
| `Gemm(src, dst, rule)` | `Compute` | — |
| `MoeRouting(src, dst, rule)` | `Moe` | `MoeKind::Routing` |
| `MoeDispatch(src, dst, rule)` | `Moe` | `MoeKind::Dispatch` |
| `MoeExpertGemm(src, dst, rule)` | `Moe` | `MoeKind::ExpertGemm` |
| `MoeCombine(src, dst, rule)` | `Moe` | `MoeKind::Combine` |

### `Scheduler`

`Scheduler` ([experimental/ukernel/src/scheduler.h:69-149]()) is a singleton that:

1. **`init(SchedulerConfig)`** — initializes with `gpu_id`, `rank`, `world_size`, and creates a `Communicator`.
2. **`add_operator(op)`** — calls `expand_operator()`, which partitions the `Operator` into `Task` objects according to `ParallelRule` and attaches dependency edges.
3. **`run()`** — drives a `step_one()` loop. Each step dequeues one ready task from `ready_compute_` or `ready_comm_` and executes it.
4. **`sync(op_id)` / `sync_all()`** — block until a specific operator or all operators complete.
5. **`connect_to(peer_rank)` / `accept_from(peer_rank)`** — set up P2P connections via `Communicator`.

**Scheduler Task Lifecycle**

```mermaid
flowchart TD
    A["OperatorFactory::P2PSend()\nOperatorFactory::MoeRouting()\netc."] --> B["Operator\n{id, deps, type, inputs, outputs, parallel_rule}"]
    B --> C["Scheduler::add_operator(op)"]
    C --> D["expand_operator()\nSlice by ParallelRule.num_tasks"]
    D --> E1["Task{type=COMM}\nCommTaskPayload\n{kind, peer, ptr, len}"]
    D --> E2["Task{type=COMPUTE}\nComputeTaskPayload (stub)"]
    E1 --> F1["ready_comm_ queue"]
    E2 --> F2["ready_compute_ queue"]
    F1 --> G1["Scheduler::run_comm()\nCommunicator::isend / irecv"]
    F2 --> G2["Executor::run_compute()\n(prints task info — stub)"]
    G1 --> H["on_task_finish()\nDecrement indegree of dependents\nMark op completed"]
    G2 --> H
```

> **Note:** The `Executor::run_compute()` path is currently a stub (prints task info). GPU-side compute tasks are exercised directly through `PersistentKernel` in the compute layer benchmarks. Integration of the two layers is in progress.

Sources: [experimental/ukernel/src/scheduler.h:1-152](), [experimental/ukernel/src/scheduler.cc:1-410](), [experimental/ukernel/src/operator.h:1-266]()

---

## Python Bindings

The `ukernel` Python module is built via pybind11 in [experimental/ukernel/src/python_bindings.cc:1-163](). It exposes:

| Python symbol | Backs |
|---|---|
| `ukernel.ReduceKind` | `ur::ReduceKind` enum |
| `ukernel.ParallelRule(num_tasks, tiles_per_task)` | `ur::ParallelRule` |
| `ukernel.Operator` | `ur::Operator` (read-only properties) |
| `ukernel.SchedulerConfig` | `ur::SchedulerConfig` |
| `ukernel.init(cfg)` | `Scheduler::instance().init(cfg)` |
| `ukernel.reset()` | `Scheduler::instance().reset()` |
| `ukernel.add(op)` | `Scheduler::instance().add_operator(op)` |
| `ukernel.run()` | `Scheduler::instance().run()` (GIL released) |
| `ukernel.sync(op_id)` | `Scheduler::instance().sync(op_id)` (GIL released) |
| `ukernel.sync_all()` | `Scheduler::instance().sync_all()` (GIL released) |
| `ukernel.poll(op_id)` | `Scheduler::instance().poll(op_id)` |
| `ukernel.connect_to(peer_rank)` | `Scheduler::instance().connect_to(peer_rank)` |
| `ukernel.accept_from(peer_rank)` | `Scheduler::instance().accept_from(peer_rank)` |
| `ukernel.p2p_send(...)` | `OperatorFactory::P2PSend(...)` |
| `ukernel.p2p_recv(...)` | `OperatorFactory::P2PRecv(...)` |
| `ukernel.all_reduce(...)` | `OperatorFactory::AllReduce(...)` |
| `ukernel.all_to_all(...)` | `OperatorFactory::AllToAll(...)` |
| `ukernel.gemm(...)` | `OperatorFactory::Gemm(...)` |
| `ukernel.moe_routing(...)` | `OperatorFactory::MoeRouting(...)` |
| `ukernel.moe_dispatch(...)` | `OperatorFactory::MoeDispatch(...)` |
| `ukernel.moe_expert_gemm(...)` | `OperatorFactory::MoeExpertGemm(...)` |
| `ukernel.moe_combine(...)` | `OperatorFactory::MoeCombine(...)` |

A typical MoE DAG construction in Python follows the pattern in [experimental/ukernel/py/test_ukernel.py:6-77]():

```python
rule = ukernel.ParallelRule(num_tasks=2, tiles_per_task=4)
router_op   = ukernel.moe_routing(tokens, tokens_expert, rule)
dispatch_op = ukernel.moe_dispatch(tokens_expert, expert_output, rule, deps=[router_op.id])
ffn_op      = ukernel.moe_expert_gemm(expert_output, gathered_output, rule, deps=[dispatch_op.id])
combine_op  = ukernel.moe_combine(gathered_output, output, rule, deps=[ffn_op.id])

ukernel.init(cfg)
for op in [router_op, dispatch_op, ffn_op, combine_op]:
    ukernel.add(op)
ukernel.run()
ukernel.sync_all()
```

Out-of-band peer setup uses environment variables `UHM_EXCHANGER_SERVER_IP` and `UHM_EXCHANGER_SERVER_PORT` (see `SockExchanger` in [experimental/ukernel/src/transport/oob.h:199-241]()).

Sources: [experimental/ukernel/src/python_bindings.cc:1-163](), [experimental/ukernel/py/test_ukernel.py:1-107](), [experimental/ukernel/py/test_p2p.py:1-144]()

---

## Platform Support

| Platform | Kernel Compiler | Build File | Target Arch |
|---|---|---|---|
| NVIDIA CUDA | `nvcc` | `src/compute/Makefile` | `sm_80` (A100/A40) |
| AMD ROCm/HIP | `hipcc` | `Makefile.rocm` | `gfx942` |

The ROCm build uses `__HIP_PLATFORM_AMD__` preprocessor guards throughout the FIFO atomics layer ([experimental/ukernel/src/compute/fifo/fifo_util.hpp:23-41]()). The `SmFifo` push path uses different inline assembly depending on compile target ([experimental/ukernel/src/compute/fifo/sm_fifo_device.h:52-59]()).

Sources: [experimental/ukernel/src/compute/Makefile:1-64](), [experimental/ukernel/Makefile.rocm:1-130](), [experimental/ukernel/src/compute/fifo/fifo_util.hpp:23-41]()

---

## Build Instructions

**Prerequisites**

```bash
sudo apt-get install -y libelf-dev
```

**NVIDIA (transport + runtime):**

```bash
cd experimental/ukernel
make clean -f Makefile && make -j$(nproc) -f Makefile
```

**AMD (transport + runtime):**

```bash
cd experimental/ukernel
make clean -f Makefile.rocm && make -j$(nproc) -f Makefile.rocm
```

**Compute layer only (NVIDIA):**

```bash
cd experimental/ukernel/src/compute
make clean -f Makefile && make -j$(nproc) -f Makefile
```

> The CUDA build container uses glog 0.5 (`libglog.so.0`). Host systems with glog 0.6 (`libglog.so.1`) may encounter runtime linking errors.

**Running tests:**

```bash
# Transport communicator test
CUDA_VISIBLE_DEVICES=5 ./test_main --role=server
CUDA_VISIBLE_DEVICES=5 ./test_main --role=client

# Python P2P test
CUDA_VISIBLE_DEVICES=5 python py/test_p2p.py

# Compute benchmarks
CUDA_VISIBLE_DEVICES=5 ./test_persistent
CUDA_VISIBLE_DEVICES=5 ./benchmarks/bench_fifo
CUDA_VISIBLE_DEVICES=5 ./benchmarks/bench_sm_fifo 83
```

Sources: [experimental/ukernel/README.md:1-59]()

---

## Benchmark Results

The following results are from `bench_fifo`, `bench_full_fifo`, and `bench_sm_fifo` on NVIDIA A40 and L40S GPUs.

**CPU→GPU FIFO (`bench_fifo` / `bench_full_fifo`)**

| GPU | Mode | p50 Latency | Throughput |
|---|---|---|---|
| NVIDIA A40 | Single FIFO (1 block) | 31.36 µs | 31.58 K tasks/s |
| NVIDIA L40S | Single FIFO (1 block) | 22.46 µs | 43.53 K tasks/s |
| NVIDIA A40 | All SMs (84 blocks) | 6.64 µs | 153.77 K tasks/s |
| NVIDIA L40S | All SMs (142 blocks) | 6.84 µs | 141.28 K tasks/s |

**SM FIFO (`bench_sm_fifo`, NVIDIA A40)**

| Producers | Tasks/producer | Total tasks | Throughput |
|---|---|---|---|
| 1 | 100 000 | 100 000 | 26.18 K tasks/s |
| 8 | 100 000 | 800 000 | 37.96 K tasks/s |
| 83 | 1 000 | 83 000 | 37.90 K tasks/s |

Sources: [experimental/ukernel/src/compute/benchmarks/bench_result.txt:1-110]()

---

## Current Development Status

UKernel is explicitly experimental. Key items that are complete vs. in progress:

| Component | Status |
|---|---|
| `PersistentKernel` + CPU→GPU FIFO | Functional, benchmarked |
| SM-to-SM `SmFifo` | Functional, benchmarked |
| `basePersistentKernel` dispatch (`CollCopy`, `CollReduce`) | Functional |
| ThunderKittens `TkGemm` integration | Functional, validated against CPU reference |
| `MoeArgs` / MoE kernel ops | Placeholder (`dummy` field only) |
| `Operator` DAG + `Scheduler` | Functional for P2P COMM tasks |
| `Executor::run_compute` | Stub (prints task info, no GPU dispatch) |
| Scheduler ↔ PersistentKernel integration | Not yet connected |
| ROCm port | Build system in place; device-level parity ongoing |

The `// TODO: ThunderKitten/Tilelang? based operators` comment in [experimental/ukernel/src/compute/operator.cu:5]() reflects the open design question for the full compute operator set.

---

# Page: UKernel Architecture and Compute Primitives

# UKernel Architecture and Compute Primitives

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experimental/ukernel/README.md](experimental/ukernel/README.md)
- [experimental/ukernel/src/compute/Makefile](experimental/ukernel/src/compute/Makefile)
- [experimental/ukernel/src/compute/benchmarks/bench_result.txt](experimental/ukernel/src/compute/benchmarks/bench_result.txt)
- [experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu](experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu)
- [experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu](experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu)
- [experimental/ukernel/src/compute/fifo/d2c_fifo.hpp](experimental/ukernel/src/compute/fifo/d2c_fifo.hpp)
- [experimental/ukernel/src/compute/fifo/fifo_util.hpp](experimental/ukernel/src/compute/fifo/fifo_util.hpp)
- [experimental/ukernel/src/compute/fifo/sm_fifo.cc](experimental/ukernel/src/compute/fifo/sm_fifo.cc)
- [experimental/ukernel/src/compute/fifo/sm_fifo.h](experimental/ukernel/src/compute/fifo/sm_fifo.h)
- [experimental/ukernel/src/compute/fifo/sm_fifo_device.h](experimental/ukernel/src/compute/fifo/sm_fifo_device.h)
- [experimental/ukernel/src/compute/operator.cu](experimental/ukernel/src/compute/operator.cu)
- [experimental/ukernel/src/compute/operator.h](experimental/ukernel/src/compute/operator.h)
- [experimental/ukernel/src/compute/operators/operator.cuh](experimental/ukernel/src/compute/operators/operator.cuh)
- [experimental/ukernel/src/compute/persistent.h](experimental/ukernel/src/compute/persistent.h)
- [experimental/ukernel/src/compute/task.h](experimental/ukernel/src/compute/task.h)

</details>



This page documents the internal architecture of the UKernel compute subsystem located in `experimental/ukernel/src/compute/`. It covers the persistent GPU kernel design, FIFO communication structures for CPU-GPU and inter-SM task delivery, the `Task` and argument types, the `TaskManager` singleton, and the ThunderKittens GEMM integration.

For the higher-level operator and scheduler layer built on top of these primitives (operators, DAG execution, Python bindings), see [5.2](#5.2). For how UKernel fits into the broader UCCL architecture and its relationship to the P2P subsystem, see [5](#5).

---

## Overview

UKernel's compute subsystem implements a **persistent kernel** model: a single GPU kernel occupies a fixed number of SMs for the lifetime of a session and processes a stream of tasks dispatched from the CPU via lock-free FIFOs. This avoids kernel launch overhead and enables fine-grained co-scheduling of communication and compute work.

The subsystem is organized around three concerns:

| Concern | Key Components |
|---|---|
| CPU→GPU task delivery | `CpuToGpuFifo<T>`, `C2DDeviceHandle<T>` |
| GPU→CPU completion notification | `Fifo` (d2c), `FifoDeviceHandle` |
| Inter-SM task delivery | `SmFifo<T>`, `SmDeviceHandle<T>` |
| Task encoding | `Task`, `TaskType`, `CollArgs`, `GemmArgs`, `MoeArgs` |
| Args lifetime management | `TaskManager` (singleton) |
| Kernel lifecycle | `PersistentKernel<T>`, `PersistentKernelConfig` |
| GPU-side dispatch | `basePersistentKernel<T>` |
| Compute primitives | `run_copy`, `run_reduce_inplace<T>`, `run_tk_gemm` |

Sources: [experimental/ukernel/src/compute/persistent.h:1-10](), [experimental/ukernel/src/compute/task.h:1-30](), [experimental/ukernel/src/compute/operator.h:1-32]()

---

## System Architecture Diagram

**Diagram: UKernel Compute Subsystem — Component Overview**

```mermaid
graph TD
    subgraph "Host (CPU)"
        PK["PersistentKernel&lt;Task&gt;\npersistent.h"]
        TM["TaskManager::instance()\ntask.h (singleton)"]
        C2D_HOST["CpuToGpuFifo&lt;Task&gt;\nc2d_fifo.h"]
        D2C_HOST["mscclpp::Fifo\nd2c_fifo.hpp"]
        SM_HOST["mscclpp::SmFifo&lt;Task&gt;\nsm_fifo.h"]
        RT["reclaim_thread_\npersistent.h"]
    end

    subgraph "Device (GPU)"
        KERNEL["basePersistentKernel&lt;Task&gt;\noperator.cu"]
        C2D_DEV["C2DDeviceHandle&lt;Task&gt;\nc2d_fifo_device.h"]
        D2C_DEV["FifoDeviceHandle\nd2c_fifo_device.hpp"]
        SM_DEV["SmDeviceHandle&lt;Task&gt;\nsm_fifo_device.h"]
        subgraph "Compute Primitives"
            COPY["run_copy(CollArgs)\noperator.cu"]
            REDUCE["run_reduce_inplace&lt;T&gt;(CollArgs)\noperator.cu"]
            GEMM["run_tk_gemm(TkMatmulGlobals,...)\noperators/operator.cuh"]
        end
        D_COLL["d_coll CollArgs[]\ndevice memory"]
        D_GEMM["d_gemm GemmArgs[]\ndevice memory"]
        D_MOE["d_moe MoeArgs[]\ndevice memory"]
    end

    PK -->|"manages"| C2D_HOST
    PK -->|"manages"| D2C_HOST
    PK -->|"manages"| SM_HOST
    PK -->|"launch()"| KERNEL
    TM -->|"d_coll(), d_moe(), d_gemm()"| D_COLL
    TM -->|""| D_GEMM
    TM -->|""| D_MOE

    C2D_HOST -->|"deviceHandle()"| C2D_DEV
    D2C_HOST -->|"deviceHandle()"| D2C_DEV
    SM_HOST -->|"deviceHandle()"| SM_DEV

    KERNEL -->|"polls"| C2D_DEV
    KERNEL -->|"dispatches"| COPY
    KERNEL -->|"dispatches"| REDUCE
    KERNEL -->|"dispatches"| GEMM
    KERNEL -->|"reads"| D_COLL
    KERNEL -->|"reads"| D_GEMM
    KERNEL -->|"signals"| D2C_DEV

    D2C_HOST -->|"poll/pop"| RT
    RT -->|"free_coll_args / free_gemm_args"| TM
```

Sources: [experimental/ukernel/src/compute/persistent.h:28-310](), [experimental/ukernel/src/compute/operator.cu:82-164](), [experimental/ukernel/src/compute/task.h:124-307]()

---

## FIFO Communication Structures

Three distinct FIFO types handle different communication directions. All are adapted from the MSCCL++ FIFO design and re-implemented locally in the `fifo/` subdirectory.

### CPU-to-GPU FIFO (`c2d_fifo`)

Carries `Task` elements from host threads to specific GPU blocks. There is one `CpuToGpuFifo<Task>` per GPU block, held in a `FifoWithPending` struct inside `PersistentKernel`.

- **Host side**: `CpuToGpuFifo<T>` — `push(task)` enqueues; `currentId()` / `head()` check occupancy.
- **Device side**: `C2DDeviceHandle<T>` — `poll()` returns a pointer to the next task, `pop()` advances the tail.

[experimental/ukernel/src/compute/persistent.h:33-37]()

The `FifoWithPending` inner struct tracks in-flight tasks:

```
struct FifoWithPending {
    CpuToGpuFifo<T> fifo;
    std::mutex pending_mu_;
    std::unordered_map<uint64_t, Pending> pending;
};
```

[experimental/ukernel/src/compute/persistent.h:280-286]()

### Device-to-CPU FIFO (`d2c_fifo`)

`mscclpp::Fifo` (host side) / `FifoDeviceHandle` (device side) — the GPU pushes `ProxyTrigger` completion records back to the CPU after a task finishes. The `reclaim_thread_` in `PersistentKernel` continuously polls this FIFO and calls `freeArgs()` to return args slots to `TaskManager`.

[experimental/ukernel/src/compute/fifo/d2c_fifo.hpp:1-47](), [experimental/ukernel/src/compute/persistent.h:89-105]()

> **Note**: The d2c_fifo completion push is currently commented out in `basePersistentKernel`. Completion is instead detected by polling `fifo.currentId()` on the CPU side via `is_done()`.

[experimental/ukernel/src/compute/operator.cu:146-154]()

### SM-to-SM FIFO (`sm_fifo`)

`mscclpp::SmFifo<T>` (host side) / `SmDeviceHandle<T>` (device side) — enables one GPU block (SM) to push tasks to another block. Supports multi-producer / single-consumer patterns on-device with two-phase head publication (`head_reserve` + `head_publish`) to maintain ordering.

[experimental/ukernel/src/compute/fifo/sm_fifo_device.h:1-87](), [experimental/ukernel/src/compute/fifo/sm_fifo.h:1-38]()

**FIFO Type Comparison**

| FIFO | Producer | Consumer | Direction | Host type | Device type |
|---|---|---|---|---|---|
| `c2d_fifo` | CPU thread | GPU block | CPU → GPU | `CpuToGpuFifo<T>` | `C2DDeviceHandle<T>` |
| `d2c_fifo` | GPU block | CPU thread | GPU → CPU | `mscclpp::Fifo` | `FifoDeviceHandle` |
| `sm_fifo` | GPU block | GPU block | GPU ↔ GPU | `mscclpp::SmFifo<T>` | `SmDeviceHandle<T>` |

Sources: [experimental/ukernel/src/compute/persistent.h:289-294](), [experimental/ukernel/src/compute/fifo/sm_fifo_device.h:10-87]()

---

## Task Encoding

### `Task` (16-byte union)

`Task` is a 128-bit packed union stored in FIFO buffers. It encodes all routing and dispatch information in two `uint64_t` fields.

[experimental/ukernel/src/compute/task.h:36-93]()

| Field | Bits | Description |
|---|---|---|
| `type` | 8 | `TaskType` enum value |
| `dataType` | 8 | `DataType` enum value |
| `blockId` | 8 | Target GPU block index |
| (padding) | 40 | Unused in `fst` |
| `argsId` | 32 | Index into the appropriate device args array |
| (padding) | 32 | Unused in `snd` |

Accessor methods: `type_u8()`, `dtype_u8()`, `block_index()`, `args_index()`.

### `TaskType` Enum

[experimental/ukernel/src/compute/task.h:13-25]()

| Value | Description |
|---|---|
| `CollCopy` | Memory copy across device buffers |
| `CollReduce` | In-place element-wise reduction |
| `MoePreGemm` | MoE pre-GEMM (stub) |
| `MoePostGemm` | MoE post-GEMM (stub) |
| `MoeCombine` | MoE combine (stub) |
| `TkGemm` | ThunderKittens tiled GEMM |
| `BenchNop` | No-op used in FIFO benchmarks |

### Argument Structures

Each `TaskType` group has a corresponding device-side arguments struct.

**`CollArgs`** — used by `CollCopy` and `CollReduce`:

| Field | Type | Description |
|---|---|---|
| `src` | `void*` | Source buffer pointer |
| `src2` | `void*` | Secondary source (unused currently) |
| `dst` | `void*` | Destination buffer pointer |
| `bytes` | `uint32_t` | Transfer size in bytes |
| `redType` | `ReduceType` | `Sum`, `Max`, or `None` |

[experimental/ukernel/src/compute/task.h:98-108]()

**`GemmArgs`** — used by `TkGemm`:

| Field | Type | Description |
|---|---|---|
| `globals` | `void*` | Device pointer to `TkMatmulGlobals` |
| `num_tile_rows` | `uint32_t` | Tile rows for multi-block dispatch |
| `num_tile_cols` | `uint32_t` | Tile cols for multi-block dispatch |

[experimental/ukernel/src/compute/task.h:118-122]()

**`MoeArgs`** — currently a stub with a single `dummy` field.

[experimental/ukernel/src/compute/task.h:109-113]()

---

## TaskManager

`TaskManager` is a process-global singleton (accessed via `TaskManager::instance()`) that owns three device-side args pools: one for `CollArgs`, one for `MoeArgs`, and one for `GemmArgs`.

[experimental/ukernel/src/compute/task.h:124-307]()

**Diagram: TaskManager Lifecycle**

```mermaid
sequenceDiagram
    participant "Host Thread" as H
    participant "TaskManager" as TM
    participant "PersistentKernel&lt;Task&gt;" as PK
    participant "basePersistentKernel (GPU)" as GPU
    participant "reclaim_thread_" as RT

    H->>TM: "init(collCap, moeCap, gemmCap)"
    Note over TM: "gpuMalloc d_coll_, d_moe_, d_gemm_"
    H->>TM: "create_coll_task(CollArgs, type, dtype, blockId)"
    Note over TM: "pop free_coll_ idx\ngpuMemcpy args to d_coll_[idx]\nreturn Task(type, dtype, blockId, idx)"
    H->>PK: "submit(task)"
    PK->>GPU: "CpuToGpuFifo::push(task)"
    GPU->>GPU: "run_copy / run_reduce_inplace"
    GPU->>GPU: "fifo.pop()"
    RT->>PK: "is_done() polls currentId()"
    PK->>TM: "free_coll_args(idx)"
    Note over TM: "push idx back to free_coll_"
```

Sources: [experimental/ukernel/src/compute/task.h:139-253](), [experimental/ukernel/src/compute/persistent.h:167-224]()

**Key methods:**

| Method | Description |
|---|---|
| `init(collCap, moeCap, gemmCap)` | Allocates device pools; must be called before use |
| `create_coll_task(h, tt, dt, blockId)` | Copies `CollArgs` to device, returns `Task` |
| `create_moe_task(h, tt, dt, blockId)` | Copies `MoeArgs` to device, returns `Task` |
| `create_gemm_task(h, dt, blockId)` | Copies `GemmArgs` to device, returns `Task` |
| `free_coll_args(idx)` | Returns a slot to the free pool |
| `free_moe_args(idx)` | Returns a slot to the free pool |
| `free_gemm_args(idx)` | Returns a slot to the free pool |
| `d_coll()`, `d_moe()`, `d_gemm()` | Returns device pointer to the array base |

---

## PersistentKernel Host Class

`PersistentKernel<T>` (in `persistent.h`) manages the kernel lifecycle from the CPU side.

[experimental/ukernel/src/compute/persistent.h:29-310]()

**Configuration via `PersistentKernelConfig`:**

| Field | Default | Description |
|---|---|---|
| `numBlocks` | 1 | Number of GPU blocks (SMs) to occupy |
| `threadsPerBlock` | 64 | Threads per block (must be a multiple of warp size) |
| `fifoCapacity` | 16 | Depth of each per-block C2D FIFO |
| `smemSize` | 0 | Dynamic shared memory bytes per block |
| `stream` | nullptr | Optional user-managed CUDA stream |

**Public API:**

| Method | Description |
|---|---|
| `PersistentKernel(config)` | Allocates FIFOs, stop flag, streams |
| `launch()` | Copies handles to device, calls `gpuLaunchKernel(basePersistentKernel<T>, ...)`, starts reclaim thread |
| `submit(task)` | Enqueues task into the C2D FIFO for `task.block_index()` |
| `is_done(blockId, taskId)` | Polls `currentId()` of the block's FIFO for completion; frees pending args |
| `stop()` | Sets `d_stopFlag_` on device via `copy_stream_`, joins reclaim thread |
| `compute_stream()` | Returns the persistent kernel's CUDA stream |
| `copy_stream()` | Returns the auxiliary copy stream used for pushes and stop |

Two CUDA streams are maintained:
- `stream_` — the stream on which `basePersistentKernel` runs
- `copy_stream_` — used for `gpuMemcpyAsync` pushes of handles and the stop flag

[experimental/ukernel/src/compute/persistent.h:303-307]()

---

## `basePersistentKernel` GPU Function

The `__global__` function `basePersistentKernel<T>` is the core of the system. Each GPU block runs an infinite poll loop.

[experimental/ukernel/src/compute/operator.cu:82-164]()

**Signature:**

```
template <typename T>
__global__ void basePersistentKernel(
    mscclpp::C2DDeviceHandle<T>* c2d_fifos,
    mscclpp::SmDeviceHandle<T>*  sm_fifos,
    mscclpp::FifoDeviceHandle*   d2c_fifo,
    CollArgs*   d_coll,
    MoeArgs*    d_moe,
    GemmArgs*   d_gemm,
    bool*       should_stop
)
```

**Per-block execution flow:**

```mermaid
flowchart TD
    A["Block starts\nbid = blockIdx.x\nfifo = c2d_fifos[bid]"]
    B["fifo.poll() — spin until task available"]
    C["__syncthreads()"]
    D["Read: ttype, dtype, idx, block_id\nCollArgs a = d_coll[idx]"]
    E{"ttype?"}
    F["run_copy(a)"]
    G["run_reduce_inplace&lt;float or half&gt;(a)"]
    H["GemmArgs ga = d_gemm[idx]\nrun_tk_gemm(*ga.globals, ...)"]
    I["(default: no-op)"]
    J["__threadfence()"]
    K["thread0: fifo.pop()"]
    L["__syncthreads()"]
    M{"should_stop?"}

    A --> B --> C --> D --> E
    E -->|"CollCopy"| F --> J
    E -->|"CollReduce"| G --> J
    E -->|"TkGemm"| H --> J
    E -->|"other"| I --> J
    J --> K --> L --> M
    M -->|"true"| N["exit"]
    M -->|"false"| B
```

Sources: [experimental/ukernel/src/compute/operator.cu:93-157]()

Only `thread0` in each block calls `fifo.pop()`, ensuring exactly-once consumption. The `__threadfence()` before `pop()` makes compute results visible before the slot is released.

---

## Compute Primitives

### `run_copy`

A parallel byte-level copy across all threads in the block. Each thread handles a contiguous chunk of `CollArgs.bytes` bytes.

[experimental/ukernel/src/compute/operator.cu:32-49]()

### `run_reduce_inplace<T>`

In-place element-wise reduction: `dst[i] = op(dst[i], src[i])`. Supports `ReduceType::Sum` and `ReduceType::Max`. Dispatched for `float` and `__half` (with `__half` converting through `float` for the operation).

[experimental/ukernel/src/compute/operator.cu:51-76]()

`apply_red<T>` is a device-inline helper that handles the `ReduceType` switch:

[experimental/ukernel/src/compute/operator.cu:10-30]()

---

## ThunderKittens GEMM Integration

The `TkGemm` task type invokes a warp-specialized, TMA-driven tiled GEMM implemented using the ThunderKittens (kittens) library.

[experimental/ukernel/src/compute/operators/operator.cuh:1-131]()

### Key Constants

| Constant | Value | Description |
|---|---|---|
| `TK_BLOCK_SIZE` | 64 | Tile dimension (rows and cols) |
| `TK_M_BLOCK` | 2 | Output tiles per row per block |
| `TK_N_BLOCK` | 4 | Output tiles per col per block |
| `TK_NUM_PRODUCER_WARPS` | 4 | Warps dedicated to TMA loads |
| `TK_NUM_CONSUMER_WARPS` | 8 | Warps dedicated to MMA compute |
| `TK_NUM_THREADS` | 384 | Total threads per block |

### `TkMatmulGlobals`

A struct holding pre-constructed TMA descriptors for matrices A, B, and C. Constructed on the host (with `bf16*` pointers and dimensions), then copied to device memory and referenced via `GemmArgs.globals`.

[experimental/ukernel/src/compute/operators/operator.cuh:27-39]()

### `run_tk_gemm`

Implements round-robin tile distribution across blocks. Each block processes tiles `t = blockIdx.x, blockIdx.x + gridDim.x, ...` up to `num_tile_rows * num_tile_cols`.

Warp roles within the block:

| `warpgroupid` | Role |
|---|---|
| 0 | Producer — issues `tma::load_async` for next A/B tiles |
| 1 | Consumer 0 — computes MMA for `C[row+0, :]` |
| 2 | Consumer 1 — computes MMA for `C[row+1, :]` |

Double-buffering (`tic`/`toc`) overlaps TMA load of the next K-tile with MMA on the current tile. Results are written back via `tma::store_async`.

[experimental/ukernel/src/compute/operators/operator.cuh:42-128]()

---

## Benchmarks

Three micro-benchmarks are provided in `experimental/ukernel/src/compute/benchmarks/`.

### `bench_fifo` and `bench_full_fifo`

Test C2D FIFO latency and throughput using `BenchNop` tasks through `PersistentKernel`.

**Sample results from `bench_result.txt`:**

| GPU | Mode | p50 Latency | Throughput |
|---|---|---|---|
| NVIDIA A40 | Single FIFO | 31.36 µs | 31.58 K tasks/s |
| NVIDIA L40S | Single FIFO | 22.46 µs | 43.53 K tasks/s |
| NVIDIA A40 | All-SM (84 FIFOs) | 6.64 µs | 153.77 K tasks/s |
| NVIDIA L40S | All-SM (142 FIFOs) | 6.84 µs | 141.28 K tasks/s |

[experimental/ukernel/src/compute/benchmarks/bench_result.txt:1-38]()

### `bench_sm_fifo`

Tests `SmFifo` throughput with configurable producer count (`num_producers`) and tasks per producer (`iters`). Runs directly on-device without the persistent kernel.

**Usage:**
```
CUDA_VISIBLE_DEVICES=5 ./benchmarks/bench_sm_fifo <num_producers> <iters_per_producer>
```

[experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu:54-118]()

**Sample results (NVIDIA A40):**

| Producers | Tasks/prod | Throughput |
|---|---|---|
| 1 | 100 000 | 26.18 K tasks/s |
| 8 | 100 000 | 37.96 K tasks/s |
| 83 | 10 000 | 38.04 K tasks/s |

[experimental/ukernel/src/compute/benchmarks/bench_result.txt:41-110]()

### `bench_tk_gemm`

Validates correctness and measures end-to-end GEMM latency for a 1024×1024×1024 `bf16` matrix multiply dispatched through the persistent kernel.

**Flow:**
1. Allocate host/device matrices A, B, C.
2. Construct `TkMatmulGlobals` and copy to device.
3. Call `TaskManager::instance().init(1, 1, 64)`.
4. Instantiate `PersistentKernel<Task>` with `threadsPerBlock = TK_NUM_THREADS` and `smemSize = 200000`.
5. Set `cudaFuncAttributeMaxDynamicSharedMemorySize` on `basePersistentKernel<Task>`.
6. `kernel.launch()`, then `create_gemm_task()` → `submit()` → poll `is_done()`.
7. Compare result against CPU reference.

[experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu:46-133]()

---

## Build

The compute subsystem builds independently from the rest of UKernel.

**NVIDIA (CUDA):**
```
cd experimental/ukernel/src/compute
make clean -f Makefile && make -j$(nproc) -f Makefile
```

**AMD (ROCm):**
```
cd experimental/ukernel/src/compute
make clean -f Makefile.rocm && make -j$(nproc) -f Makefile.rocm
```

Build targets:

| Target | Binary | Description |
|---|---|---|
| `test_persistent` | `test_persistent` | Functional test of the persistent kernel |
| `bench_fifo` | `benchmarks/bench_fifo` | C2D FIFO single-block benchmark |
| `bench_full_fifo` | `benchmarks/bench_full_fifo` | C2D FIFO all-SM benchmark |
| `bench_sm_fifo` | `benchmarks/bench_sm_fifo` | SM FIFO multi-producer benchmark |

The build links against `libcudart`, `libcuda`, `libnuma`, and a local `libgdrapi` from `thirdparty/gdrcopy/src`.

[experimental/ukernel/src/compute/Makefile:1-63](), [experimental/ukernel/README.md:38-58]()

---

## File Map

**Diagram: Source File Responsibilities**

```mermaid
graph LR
    subgraph "task.h"
        T1["Task (16B union)"]
        T2["TaskType enum"]
        T3["CollArgs / MoeArgs / GemmArgs"]
        T4["TaskManager (singleton)"]
    end
    subgraph "persistent.h"
        P1["PersistentKernelConfig"]
        P2["PersistentKernel&lt;T&gt;"]
        P3["FifoWithPending"]
    end
    subgraph "operator.cu / operator.h"
        O1["basePersistentKernel&lt;Task&gt;"]
        O2["run_copy(CollArgs)"]
        O3["run_reduce_inplace&lt;T&gt;(CollArgs)"]
    end
    subgraph "operators/operator.cuh"
        G1["TkMatmulGlobals"]
        G2["run_tk_gemm(...)"]
        G3["TK_* constants"]
    end
    subgraph "fifo/c2d_fifo.*"
        F1["CpuToGpuFifo&lt;T&gt;"]
        F2["C2DDeviceHandle&lt;T&gt;"]
    end
    subgraph "fifo/d2c_fifo.*"
        F3["mscclpp::Fifo"]
        F4["FifoDeviceHandle"]
    end
    subgraph "fifo/sm_fifo.*"
        F5["SmFifo&lt;T&gt;"]
        F6["SmDeviceHandle&lt;T&gt;"]
    end

    P2 -->|"owns"| F1
    P2 -->|"owns"| F3
    P2 -->|"owns"| F5
    P2 -->|"calls"| O1
    P2 -->|"uses"| T4
    O1 -->|"switch ttype"| O2
    O1 -->|"switch ttype"| O3
    O1 -->|"switch ttype"| G2
    O1 -->|"reads"| F2
    O1 -->|"reads"| T1
    T4 -->|"manages"| T3
```

Sources: [experimental/ukernel/src/compute/task.h:1-307](), [experimental/ukernel/src/compute/persistent.h:1-310](), [experimental/ukernel/src/compute/operator.cu:1-167](), [experimental/ukernel/src/compute/operators/operator.cuh:1-131]()

---

# Page: UKernel Operators and Scheduler

# UKernel Operators and Scheduler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experimental/ukernel/Makefile.rocm](experimental/ukernel/Makefile.rocm)
- [experimental/ukernel/README.md](experimental/ukernel/README.md)
- [experimental/ukernel/py/test_p2p.py](experimental/ukernel/py/test_p2p.py)
- [experimental/ukernel/py/test_ukernel.py](experimental/ukernel/py/test_ukernel.py)
- [experimental/ukernel/src/compute/Makefile](experimental/ukernel/src/compute/Makefile)
- [experimental/ukernel/src/compute/benchmarks/bench_result.txt](experimental/ukernel/src/compute/benchmarks/bench_result.txt)
- [experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu](experimental/ukernel/src/compute/benchmarks/bench_sm_fifo.cu)
- [experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu](experimental/ukernel/src/compute/benchmarks/bench_tk_gemm.cu)
- [experimental/ukernel/src/compute/fifo/d2c_fifo.hpp](experimental/ukernel/src/compute/fifo/d2c_fifo.hpp)
- [experimental/ukernel/src/compute/fifo/fifo_util.hpp](experimental/ukernel/src/compute/fifo/fifo_util.hpp)
- [experimental/ukernel/src/compute/fifo/sm_fifo.cc](experimental/ukernel/src/compute/fifo/sm_fifo.cc)
- [experimental/ukernel/src/compute/fifo/sm_fifo.h](experimental/ukernel/src/compute/fifo/sm_fifo.h)
- [experimental/ukernel/src/compute/fifo/sm_fifo_device.h](experimental/ukernel/src/compute/fifo/sm_fifo_device.h)
- [experimental/ukernel/src/compute/operator.cu](experimental/ukernel/src/compute/operator.cu)
- [experimental/ukernel/src/compute/operator.h](experimental/ukernel/src/compute/operator.h)
- [experimental/ukernel/src/compute/operators/operator.cuh](experimental/ukernel/src/compute/operators/operator.cuh)
- [experimental/ukernel/src/compute/persistent.h](experimental/ukernel/src/compute/persistent.h)
- [experimental/ukernel/src/compute/task.h](experimental/ukernel/src/compute/task.h)
- [experimental/ukernel/src/operator.h](experimental/ukernel/src/operator.h)
- [experimental/ukernel/src/python_bindings.cc](experimental/ukernel/src/python_bindings.cc)
- [experimental/ukernel/src/scheduler.cc](experimental/ukernel/src/scheduler.cc)
- [experimental/ukernel/src/scheduler.h](experimental/ukernel/src/scheduler.h)
- [experimental/ukernel/src/transport/oob.h](experimental/ukernel/src/transport/oob.h)
- [experimental/ukernel/tests/test_main.cc](experimental/ukernel/tests/test_main.cc)

</details>



## Purpose and Scope

This page documents the **Runtime layer** of the UKernel subsystem: the `Operator` abstraction, the `OperatorFactory` for constructing typed operators, the `Scheduler` DAG execution engine, the pybind11 Python bindings, and the MoE DAG construction pattern shown in the test scripts. It covers `experimental/ukernel/src/operator.h`, `experimental/ukernel/src/scheduler.h`, `experimental/ukernel/src/scheduler.cc`, and `experimental/ukernel/src/python_bindings.cc`.

For the lower-level GPU compute primitives (`PersistentKernel`, `TaskManager`, `CollArgs`, `GemmArgs`, FIFO structures) that the scheduler dispatches into, see [UKernel Architecture and Compute Primitives](#5.1). For the overall UKernel subsystem introduction, see [Experimental: UKernel](#5).

---

## Operator Structure

An `Operator` is the unit of work submitted to the scheduler. It is defined in `experimental/ukernel/src/operator.h`.

**Operator fields:**

| Field | Type | Description |
|---|---|---|
| `id` | `uint64_t` | Unique auto-assigned ID (via `OperatorFactory`) |
| `type` | `OpType` | Top-level type: P2P, Collective, Compute, or Moe |
| `deps` | `vector<uint64_t>` | IDs of operators this one depends on |
| `p2p_kind` | `optional<P2PKind>` | Send or Recv (for P2P ops) |
| `collective_kind` | `optional<CollectiveKind>` | AllReduce, AllToAll, etc. |
| `moe_kind` | `optional<MoeKind>` | Routing, Dispatch, ExpertGemm, Combine |
| `parallel_rule` | `ParallelRule` | Tiling: `num_tasks` and `tiles_per_task` |
| `inputs` | `vector<torch::Tensor>` | Input tensors |
| `outputs` | `vector<torch::Tensor>` | Output tensors |
| `attrs` | `unordered_map<string,string>` | Key-value metadata (e.g., `peer`, `offset`, `len`) |
| `shape` / `numel` | `vector<int64_t>` / `int64_t` | Inferred from first input or output tensor |

[experimental/ukernel/src/operator.h:74-96]()

### OpType Hierarchy

**Operator type and subtype hierarchy:**

```mermaid
graph TD
  OpType["OpType enum"] --> P2P["OpType::P2P"]
  OpType --> Collective["OpType::Collective"]
  OpType --> Compute["OpType::Compute"]
  OpType --> Moe["OpType::Moe"]

  P2P --> P2PSend["P2PKind::Send\n(OperatorFactory::P2PSend)"]
  P2P --> P2PRecv["P2PKind::Recv\n(OperatorFactory::P2PRecv)"]

  Collective --> AllReduce["CollectiveKind::AllReduce\n(OperatorFactory::AllReduce)"]
  Collective --> AllToAll["CollectiveKind::AllToAll\n(OperatorFactory::AllToAll)"]
  Collective --> ReduceScatter["CollectiveKind::ReduceScatter"]
  Collective --> AllGather["CollectiveKind::AllGather"]

  Compute --> Gemm["ComputeKind::Gemm\n(OperatorFactory::Gemm)"]

  Moe --> MoeRouting["MoeKind::Routing\n(OperatorFactory::MoeRouting)"]
  Moe --> MoeDispatch["MoeKind::Dispatch\n(OperatorFactory::MoeDispatch)"]
  Moe --> MoeExpertGemm["MoeKind::ExpertGemm\n(OperatorFactory::MoeExpertGemm)"]
  Moe --> MoeCombine["MoeKind::Combine\n(OperatorFactory::MoeCombine)"]
```

Sources: [experimental/ukernel/src/operator.h:11-67]()

---

## OperatorFactory

`OperatorFactory` is a static-only factory class with no instances. It maintains a global atomic ID counter (`g_next_id`) and assigns each operator a unique monotonically increasing `id`. The `ResetId()` method resets the counter, which is useful between test runs.

All factory methods follow the same pattern:
1. Validate that required tensors are defined.
2. Call the private `base()` helper to create an `Operator` with type, inputs, outputs, `ParallelRule`, and deps.
3. Set the type-specific optional field (`p2p_kind`, `collective_kind`, `moe_kind`).
4. Set `attrs` for any additional parameters (e.g., `peer`, `offset`, `len`, `on_gpu`).

### Factory Methods Summary

| Method | OpType | Subtype | Key attrs |
|---|---|---|---|
| `P2PSend(src, rule, peer_rank, offset, len, on_gpu, deps)` | P2P | `P2PKind::Send` | `peer`, `offset`, `len`, `on_gpu` |
| `P2PRecv(dst, rule, peer_rank, offset, len, on_gpu, deps)` | P2P | `P2PKind::Recv` | `peer`, `offset`, `len`, `on_gpu` |
| `AllReduce(src, dst, kind, rule, deps)` | Collective | `CollectiveKind::AllReduce` | — |
| `AllToAll(src, dst, rule, deps)` | Collective | `CollectiveKind::AllToAll` | — |
| `Gemm(src, dst, rule, deps)` | Compute | — | — |
| `MoeRouting(src, dst, rule, deps)` | Moe | `MoeKind::Routing` | — |
| `MoeDispatch(src, dst, rule, deps)` | Moe | `MoeKind::Dispatch` | — |
| `MoeExpertGemm(src, dst, rule, deps)` | Moe | `MoeKind::ExpertGemm` | — |
| `MoeCombine(src, dst, rule, deps)` | Moe | `MoeKind::Combine` | — |

[experimental/ukernel/src/operator.h:98-266]()

### ParallelRule

`ParallelRule` controls how an operator is tiled into sub-tasks:

- `num_tasks` — number of parallel task slices to create for this operator
- `tiles_per_task` — number of tile units each task claims (`tile_offset` and `tile_count` are propagated to each `Task`)

For P2P operators, `num_tasks` controls how the data buffer is chunked across multiple `Task` instances. For compute operators, the tiling is a placeholder for future fine-grained dispatch.

[experimental/ukernel/src/operator.h:69-72]()

---

## Scheduler

The `Scheduler` is a singleton (`Scheduler::instance()`) defined in `experimental/ukernel/src/scheduler.h` and implemented in `experimental/ukernel/src/scheduler.cc`. It manages a DAG of `Operator` objects, expands them into fine-grained `Task` objects, and executes them using indegree-based topological ordering.

### SchedulerConfig

```
SchedulerConfig {
  int gpu_id      // GPU device index
  int rank        // process rank
  int world_size  // total process count
  shared_ptr<CommunicatorConfig> comm_cfg
}
```

[experimental/ukernel/src/scheduler.h:61-67]()

### Internal Task Representation

After `add_operator` is called, the scheduler internally converts each `Operator` into one or more `Task` objects (in `scheduler.h`, distinct from the GPU-side `Task` in `compute/task.h`):

| Field | Type | Description |
|---|---|---|
| `id` | `uint64_t` | Unique task ID (`next_task_id_++`) |
| `type` | `TaskType` | COMM or COMPUTE |
| `deps` | `vector<uint64_t>` | IDs of other tasks this one depends on |
| `indegree` | `int` | Number of unfinished dependencies |
| `tile_offset` / `tile_count` | `int` | Tiling metadata from `ParallelRule` |
| `op_id` | `uint64_t` | Back-reference to parent `Operator` |
| `payload` | `variant<monostate, CommTaskPayload, ComputeTaskPayload>` | Execution arguments |

`CommTaskPayload` holds: `kind` (SEND/RECV), `peer`, `on_gpu`, `ptr`, `offset`, `len`, `mr_base_ptr`, `mr_base_len`.

[experimental/ukernel/src/scheduler.h:18-49]()

### DAG Execution Model

**Operator-to-Task expansion and scheduling flow:**

```mermaid
flowchart TD
  A["ukernel.add(op)\nScheduler::add_operator"] --> B["Scheduler::expand_operator"]
  B --> C{"op.type?"}
  C -->|"P2P (COMM)"| D["Slice buffer by num_tasks\nCreate CommTaskPayload per slice"]
  C -->|"Compute / Moe"| E["Create stub ComputeTaskPayload\nper num_tasks (future work)"]
  D --> F["Assign dep edges\nfrom op.deps -> task IDs"]
  E --> F
  F --> G{"indegree == 0?"}
  G -->|"COMM task"| H["ready_comm_ queue"]
  G -->|"COMPUTE task"| I["ready_compute_ queue"]
  J["Scheduler::run / sync"] --> K["Scheduler::step_one"]
  K --> L{"ready_compute_\nnon-empty?"}
  L -->|"yes"| M["Executor::run_compute(task)"]
  L -->|"no"| N["run_comm(task)\nvia Communicator"]
  M --> O["Scheduler::on_task_finish(tid)"]
  N --> O
  O --> P["Decrement indegree\nof dependent tasks"]
  P --> Q["Push newly zero-indegree\ntasks to ready queues"]
  O --> R["Decrement op_remaining_tasks_\nInsert to completed_ops_ if done"]
```

Sources: [experimental/ukernel/src/scheduler.cc:60-278]()

### Execution Control

| Method | Behavior |
|---|---|
| `init(cfg)` | Creates `Communicator`, sets `initialized_` flag |
| `reset()` | Clears all ops/tasks/queues; does **not** reset communicator or connections |
| `add_operator(op)` | Validates deps exist, stores op, calls `expand_operator` |
| `run()` | Loops `step_one()` until no ready tasks; throws if pending tasks remain with no ready work |
| `sync(op_id)` | Drives `step_one()` until `completed_ops_` contains `op_id` |
| `sync_all()` | Drives `step_one()` until `idle()` (no pending or ready tasks) |
| `poll(op_id)` | Non-blocking: returns `true` if `op_id ∈ completed_ops_` |
| `connect_to(peer)` | Delegates to `Communicator::connect_to` |
| `accept_from(peer)` | Delegates to `Communicator::accept_from` |

[experimental/ukernel/src/scheduler.h:76-92]()

### Communication Execution Path

For COMM tasks, `run_comm` performs:
1. **Memory registration**: `get_or_reg_local_mr_for_buffer_` calls `Communicator::get_local_mr` (cache hit) or `Communicator::reg_mr` (miss).
2. **MR notification**: `notify_local_mr_once_` calls `Communicator::notify_mr` per peer–MR pair, deduplicating with `notified_local_mr_`.
3. **For SEND**: `get_remote_default_mr_` blocks on `Communicator::wait_mr_notify` on first access, caches in `peer_default_remote_mr_id_`. Then calls `comm_->isend(...)` and `wait_finish`.
4. **For RECV**: calls `comm_->irecv(...)` and `wait_finish`.

[experimental/ukernel/src/scheduler.cc:365-406]()

---

## Python Bindings

The Python module is named `ukernel` and compiled as `py/ukernel.so`. The binding entry point is `PYBIND11_MODULE(ukernel, m)` in `experimental/ukernel/src/python_bindings.cc`.

### Python API to C++ Mapping

**Python API → C++ entity mapping:**

```mermaid
graph LR
  subgraph "ukernel Python module"
    pySchedulerConfig["ukernel.SchedulerConfig"]
    pyParallelRule["ukernel.ParallelRule"]
    pyOperator["ukernel.Operator"]
    pyReduceKind["ukernel.ReduceKind"]
    pyInit["ukernel.init(cfg)"]
    pyReset["ukernel.reset()"]
    pyAdd["ukernel.add(op)"]
    pyRun["ukernel.run()"]
    pyPoll["ukernel.poll(op_id)"]
    pySync["ukernel.sync(op_id)"]
    pySyncAll["ukernel.sync_all()"]
    pyConnectTo["ukernel.connect_to(peer)"]
    pyAcceptFrom["ukernel.accept_from(peer)"]
    pyP2PSend["ukernel.p2p_send(...)"]
    pyP2PRecv["ukernel.p2p_recv(...)"]
    pyAllReduce["ukernel.all_reduce(...)"]
    pyAllToAll["ukernel.all_to_all(...)"]
    pyGemm["ukernel.gemm(...)"]
    pyMoeRouting["ukernel.moe_routing(...)"]
    pyMoeDispatch["ukernel.moe_dispatch(...)"]
    pyMoeExpertGemm["ukernel.moe_expert_gemm(...)"]
    pyMoeCombine["ukernel.moe_combine(...)"]
  end

  subgraph "C++ Runtime (UKernel::Runtime)"
    cppSchedulerConfig["SchedulerConfig struct"]
    cppParallelRule["ParallelRule struct"]
    cppOperator["Operator struct"]
    cppReduceKind["ReduceKind enum"]
    cppScheduler["Scheduler::instance()"]
    cppFactory["OperatorFactory static methods"]
  end

  pySchedulerConfig --> cppSchedulerConfig
  pyParallelRule --> cppParallelRule
  pyOperator --> cppOperator
  pyReduceKind --> cppReduceKind
  pyInit --> cppScheduler
  pyReset --> cppScheduler
  pyAdd --> cppScheduler
  pyRun --> cppScheduler
  pyPoll --> cppScheduler
  pySync --> cppScheduler
  pySyncAll --> cppScheduler
  pyConnectTo --> cppScheduler
  pyAcceptFrom --> cppScheduler
  pyP2PSend --> cppFactory
  pyP2PRecv --> cppFactory
  pyAllReduce --> cppFactory
  pyAllToAll --> cppFactory
  pyGemm --> cppFactory
  pyMoeRouting --> cppFactory
  pyMoeDispatch --> cppFactory
  pyMoeExpertGemm --> cppFactory
  pyMoeCombine --> cppFactory
```

Sources: [experimental/ukernel/src/python_bindings.cc:1-163]()

### GIL Handling

`run()`, `sync()`, `sync_all()`, `connect_to()`, and `accept_from()` all call `py::gil_scoped_release` before entering the C++ blocking call. This allows other Python threads to proceed while the scheduler drives communication or waits for completions.

[experimental/ukernel/src/python_bindings.cc:115-152]()

---

## MoE DAG Construction Pattern

`experimental/ukernel/py/test_ukernel.py` demonstrates the canonical four-stage MoE pipeline as a DAG:

```
MoeRouting → MoeDispatch → MoeExpertGemm → MoeCombine
```

Each stage depends on the previous stage's `op.id`, passed via the `deps` argument:

```python
router_op   = ukernel.moe_routing(tokens, tokens_expert, rule)
dispatch_op = ukernel.moe_dispatch(tokens_expert, expert_output, rule, deps=[router_op.id])
ffn_op      = ukernel.moe_expert_gemm(expert_output, gathered_output, rule, deps=[dispatch_op.id])
combine_op  = ukernel.moe_combine(gathered_output, output, rule, deps=[ffn_op.id])
```

The scheduler validates that all referenced dep IDs are already registered before expanding. After all operators are added, `ukernel.run()` executes the DAG in topological order and `ukernel.sync_all()` blocks until completion.

[experimental/ukernel/py/test_ukernel.py:6-107]()

**MoE DAG and operator lifecycle:**

```mermaid
sequenceDiagram
  participant "Python (test_ukernel.py)" as PY
  participant "Scheduler::add_operator" as ADD
  participant "expand_operator" as EXP
  participant "ready_compute_ / ready_comm_" as Q
  participant "Scheduler::run / sync_all" as RUN

  PY ->> ADD: add(router_op)
  ADD ->> EXP: expand_operator(router_op)
  EXP ->> Q: push Task(indegree=0)

  PY ->> ADD: add(dispatch_op, deps=[router_op.id])
  ADD ->> EXP: expand_operator(dispatch_op)
  EXP ->> Q: push Task(indegree=N, blocked on router tasks)

  PY ->> ADD: add(ffn_op, deps=[dispatch_op.id])
  PY ->> ADD: add(combine_op, deps=[ffn_op.id])

  PY ->> RUN: ukernel.run()
  RUN ->> Q: step_one() — dequeue router tasks (indegree=0)
  RUN ->> Q: on_task_finish → dispatch tasks become ready
  RUN ->> Q: step_one() — dequeue dispatch tasks
  RUN ->> Q: on_task_finish → ffn tasks become ready
  RUN ->> Q: step_one() — dequeue ffn, then combine
  RUN -->> PY: all tasks complete, sync_all() returns
```

Sources: [experimental/ukernel/py/test_ukernel.py:46-103](), [experimental/ukernel/src/scheduler.cc:73-205]()

---

## P2P DAG Pattern

`experimental/ukernel/py/test_p2p.py` shows the simpler P2P case. A server process (rank 0) issues a `p2p_recv` and a client process (rank 1) issues a `p2p_send`. Connection setup (`accept_from` / `connect_to`) must happen before operators are added.

```python
# Server (rank=0)
ukernel.init(cfg)
ukernel.accept_from(1)
recv_op = ukernel.p2p_recv(recv_tokens, rule, peer_rank=1)
ukernel.add(recv_op)
ukernel.run(); ukernel.sync_all()

# Client (rank=1)
ukernel.init(cfg)
ukernel.connect_to(0)
send_op = ukernel.p2p_send(tokens, rule, peer_rank=0)
ukernel.add(send_op)
ukernel.run(); ukernel.sync_all()
```

[experimental/ukernel/py/test_p2p.py:55-123]()

Connection setup uses a `SockExchanger` server at the address set by the `UHM_EXCHANGER_SERVER_IP` and `UHM_EXCHANGER_SERVER_PORT` environment variables.

---

## Dependency Validation

`add_operator` enforces that all declared `deps` reference operator IDs already present in `ops_`. Adding an operator whose dep hasn't been registered yet raises `std::runtime_error("add_operator order violation: missing dep op ...")`. This means operators must be submitted in topological order.

[experimental/ukernel/src/scheduler.cc:73-88]()

---

## Current Limitations

| Area | Status |
|---|---|
| Collective ops (AllReduce, AllToAll) | Defined in `OperatorFactory` but `expand_operator` only supports `P2P` COMM today — other collective ops throw `"Only P2P comm supported for now"` |
| Compute / Moe task execution | `Executor::run_compute` is a stub that prints task info; real GPU dispatch into `PersistentKernel` is not yet wired through the scheduler |
| Parallel COMM task dispatch | Tasks are executed serially in `step_one()`; parallel dispatch is a future work item noted in comments |

[experimental/ukernel/src/scheduler.cc:96-105](), [experimental/ukernel/src/scheduler.h:52-58]()

---

# Page: Build System and Deployment

# Build System and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This document provides an overview of the UCCL build infrastructure and deployment process. UCCL uses a Docker-based build system to ensure reproducible, portable builds across multiple GPU platforms (CUDA, ROCm, TheRock) and architectures (x86_64, aarch64). The system produces Python wheels that bundle platform-specific shared libraries and can be deployed to diverse runtime environments.

For detailed information on specific aspects of the build system:
- Build scripts and Docker environments: see page 5.1
- Platform-specific compilation flags and dependencies: see page 5.2  
- Development environment setup and CI/CD: see page 5.3

For testing built packages, see page 7.

## Build System Overview

UCCL's build infrastructure is centered around [build.sh:1-437]() and uses Docker containers to isolate build dependencies and ensure reproducibility. The system supports three primary target backends (`cuda`, `rocm`, `therock`) and can build different component subsets (`ccl_rdma`, `ccl_efa`, `p2p`, `ep`, or `all`).

### High-Level Build Architecture

```mermaid
graph TB
    subgraph "Build Input"
        SRC["Source Code<br/>C++/CUDA/HIP"]
        DOCKER_DEF["Dockerfiles<br/>docker/Dockerfile.*"]
        MAKEFILE["Makefiles<br/>Component-specific"]
    end
    
    subgraph "Build Orchestration (build.sh)"
        DETECT["Platform Detection<br/>TARGET, ARCH, IS_EFA"]
        
        subgraph "Docker Image Selection"
            D_CUDA["uccl-builder-cuda<br/>Dockerfile.cuda"]
            D_ROCM["uccl-builder-rocm<br/>Dockerfile.rocm"]
            D_GH["uccl-builder-gh<br/>Dockerfile.gh"]
            D_EFA["uccl-builder-efa<br/>Dockerfile.efa"]
            D_THEROCK["uccl-builder-therock<br/>Dockerfile.therock"]
        end
        
        subgraph "Build Functions (Inside Container)"
            B_CCL_RDMA["build_ccl_rdma()<br/>collective/rdma/Makefile"]
            B_CCL_EFA["build_ccl_efa()<br/>collective/efa/Makefile"]
            B_P2P["build_p2p()<br/>p2p/Makefile"]
            B_EP["build_ep()<br/>ep/setup.py"]
        end
    end
    
    subgraph "Python Packaging"
        SETUP["setup.py<br/>Package metadata"]
        BUILD_CMD["python -m build<br/>Generate wheel"]
        AUDIT["auditwheel repair<br/>Bundle dependencies"]
    end
    
    subgraph "Output"
        WHEEL["wheelhouse-TARGET/<br/>uccl-VERSION-py3-none-PLATFORM.whl"]
    end
    
    SRC --> DETECT
    DOCKER_DEF --> DETECT
    MAKEFILE --> DETECT
    
    DETECT --> D_CUDA
    DETECT --> D_ROCM
    DETECT --> D_GH
    DETECT --> D_EFA
    DETECT --> D_THEROCK
    
    D_CUDA --> B_CCL_RDMA
    D_ROCM --> B_CCL_RDMA
    D_EFA --> B_CCL_EFA
    D_CUDA --> B_P2P
    D_ROCM --> B_P2P
    D_CUDA --> B_EP
    D_ROCM --> B_EP
    
    B_CCL_RDMA --> SETUP
    B_CCL_EFA --> SETUP
    B_P2P --> SETUP
    B_EP --> SETUP
    
    SETUP --> BUILD_CMD
    BUILD_CMD --> AUDIT
    AUDIT --> WHEEL
```

The build process:
1. **Detection**: [build.sh:15-23]() detects target platform, architecture, and available hardware (EFA)
2. **Docker Image Selection**: [build.sh:193-230]() chooses appropriate Dockerfile based on detected parameters
3. **Container Execution**: [build.sh:270-432]() runs build functions inside Docker with mounted source directory
4. **Component Compilation**: Individual build functions ([build.sh:53-170]()) compile C++/CUDA/HIP code and generate `.so` files
5. **Python Packaging**: [setup.py:1-48]() packages compiled libraries with [pyproject.toml:1-3]() build backend
6. **Wheel Repair**: `auditwheel` ([build.sh:393-400]()) bundles dependencies while excluding large runtime libraries

Sources: [build.sh:1-437](), [setup.py:1-48](), [pyproject.toml:1-3]()

## Supported Platforms and Components

UCCL supports multiple target platforms with varying component availability. The build system automatically detects platform constraints and skips unsupported combinations.

### Platform Targets

```mermaid
graph LR
    subgraph "Target Platforms"
        CUDA["cuda<br/>CUDA 12.x (default)<br/>nvidia/cuda:12.8.0"]
        CUDA13["cuda13<br/>CUDA 13.x<br/>nvidia/cuda:13.0.1"]
        ROCM["rocm<br/>ROCm 7.x (default)<br/>rocm/dev-ubuntu-22.04"]
        ROCM6["rocm6<br/>ROCm 6.4.3<br/>rocm/dev-ubuntu-22.04:6.4.3"]
        THEROCK["therock<br/>ROCm via Python<br/>manylinux_2_28_x86_64"]
    end
    
    subgraph "Architecture Detection"
        X86["x86_64<br/>Standard servers"]
        ARM["aarch64<br/>Grace Hopper GH200"]
    end
    
    subgraph "Hardware Detection"
        EFA_HW["EFA NICs<br/>AWS p4d/p4de/p5/p6"]
        IB_HW["InfiniBand/RoCE<br/>CX7, Thor2"]
    end
    
    CUDA --> X86
    CUDA --> ARM
    ROCM --> X86
    THEROCK --> X86
    
    X86 --> EFA_HW
    X86 --> IB_HW
    ARM --> IB_HW
```

Platform selection logic in [build.sh:26-34]():
```bash
if [[ $TARGET != cuda* && $TARGET != rocm* && $TARGET != "therock" ]]; then
  echo "Usage: $0 [cuda|rocm|therock] ..." >&2
  exit 1
fi

if [[ $ARCH == "aarch64" && ( $TARGET == rocm* || $TARGET == "therock" ) ]]; then
  echo "Skipping ROCm build on Arm64 (no ROCm toolchain)."
  exit 1
fi
```

Sources: [build.sh:26-34](), [build.sh:194-230]()

### Component Support Matrix

| Platform/Feature | ccl_rdma | ccl_efa | p2p | ep |
|------------------|----------|---------|-----|-----|
| cuda + x86_64 | ✓ | ✓ | ✓ | ✓ |
| cuda + aarch64 (GH200) | ✓ | ✗ | ✓ | ✓ |
| rocm + x86_64 | ✓ | ✗ | ✓ | ✓ |
| therock + x86_64 | ✓ | ✗ | ✓ | ✗ |

Component build functions skip unsupported combinations automatically:
- **EFA**: [build.sh:100-103]() skips on ARM64 and ROCm (CUDA-only)
- **EP**: [build.sh:158-160]() skips on TheRock (no GPU support in manylinux)
- **ROCm**: [build.sh:31-34]() entirely unsupported on ARM64

Sources: [build.sh:53-91](), [build.sh:92-115](), [build.sh:117-148](), [build.sh:150-170](), [README.md:179-185]()

## Build Components and Output Files

### Component Build Targets

The build system supports five component targets specified via the `BUILD_TYPE` parameter:

```mermaid
graph TB
    subgraph "Build Component Selection"
        BUILD_TYPE["BUILD_TYPE Parameter"]
        
        BUILD_TYPE -->|"all"| ALL["Build All Components<br/>(excludes ep by default)"]
        BUILD_TYPE -->|"ccl_rdma"| RDMA["UCCL-Collective RDMA"]
        BUILD_TYPE -->|"ccl_efa"| EFA["UCCL-Collective EFA"]
        BUILD_TYPE -->|"p2p"| P2P["UCCL-P2P Engine"]
        BUILD_TYPE -->|"ep"| EP["UCCL-EP Expert Parallel"]
    end
    
    subgraph "Compilation Output"
        RDMA --> RDMA_SO["uccl/lib/libnccl-net-uccl.so<br/>uccl/lib/librccl-net-uccl.so"]
        EFA --> EFA_SO["uccl/lib/libnccl-net-efa.so<br/>uccl/lib/libnccl-efa.so"]
        P2P --> P2P_SO["uccl/p2p.*.so<br/>uccl/collective.py<br/>uccl/transfer.py<br/>uccl/utils.py"]
        EP --> EP_SO["uccl/ep*.so"]
    end
    
    subgraph "Source Code Mapping"
        RDMA_SO --> RDMA_SRC["collective/rdma/Makefile<br/>collective/rdma/Makefile.rocm<br/>collective/rdma/Makefile.therock"]
        EFA_SO --> EFA_SRC["collective/efa/Makefile<br/>thirdparty/nccl-sg/"]
        P2P_SO --> P2P_SRC["p2p/Makefile<br/>p2p/Makefile.rocm<br/>p2p/Makefile.therock"]
        EP_SO --> EP_SRC["ep/setup.py<br/>ep/Makefile"]
    end
```

Build function mapping in [build.sh:311-351]():

| `BUILD_TYPE` | Build Function | Source Directory | Primary Output |
|--------------|---------------|------------------|----------------|
| `ccl_rdma` | `build_ccl_rdma()` | `collective/rdma/` | `libnccl-net-uccl.so` / `librccl-net-uccl.so` |
| `ccl_efa` | `build_ccl_efa()` | `collective/efa/` + `thirdparty/nccl-sg/` | `libnccl-net-efa.so` + `libnccl-efa.so` |
| `p2p` | `build_p2p()` | `p2p/` | `p2p.*.so` + Python files |
| `ep` | `build_ep()` | `ep/` | `ep*.so` |
| `all` | All except `ep` | Multiple | All `.so` files |

Sources: [build.sh:311-351](), [build.sh:53-170]()

### Package Structure

The final Python wheel contains compiled libraries organized in the `uccl/` package:

```
uccl-VERSION-py3-none-PLATFORM.whl
├── uccl/
│   ├── __init__.py              # Plugin path helpers
│   ├── lib/
│   │   ├── libnccl-net-uccl.so  # NCCL RDMA plugin (CUDA)
│   │   ├── librccl-net-uccl.so  # RCCL RDMA plugin (ROCm)
│   │   ├── libnccl-net-efa.so   # NCCL EFA plugin
│   │   ├── libnccl-efa.so       # Custom NCCL for EFA
│   │   ├── libuccl_p2p.so       # P2P core library
│   │   └── librdma_plugin.a     # RDMA plugin static lib
│   ├── p2p.*.so                 # P2P Python binding
│   ├── ep*.so                   # EP Python binding
│   ├── collective.py            # P2P high-level API
│   ├── transfer.py              # P2P transfer helpers
│   └── utils.py                 # P2P utilities
```

Package data specification in [setup.py:27-36]():
```python
package_data={
    "uccl": [
        "lib/*.so",
        "p2p*.so",
        "ep*.so",
        "lib/*.a",
        "collective.py",
        "transfer.py",
        "utils.py",
    ],
}
```

Sources: [setup.py:18-48](), [uccl/__init__.py:1-55]()

## Quick Start: Building and Installing

### Basic Build and Install

The simplest way to build and install UCCL is using [build_and_install.sh:1-40]():

```bash
git clone https://github.com/uccl-project/uccl.git --recursive
cd uccl

# Build and install for CUDA (all components)
bash build_and_install.sh cuda all

# Build and install for ROCm (EP component only)
bash build_and_install.sh rocm ep

# Build for specific Python version
bash build_and_install.sh cuda all 3.11
```

This script:
1. Calls [build.sh:1-437]() to build the wheel
2. Installs Python dependencies from [requirements.txt]()
3. Uninstalls existing UCCL installations
4. Installs the newly built wheel
5. Displays the installation path

Sources: [build_and_install.sh:1-40](), [README.md:92-101]()

### Manual Build Process

For more control, build and install separately:

```bash
# Step 1: Build wheel
./build.sh cuda all

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Install wheel
pip uninstall uccl -y
pip install wheelhouse-cuda/uccl-*.whl
```

For TheRock installations, specify ROCm dependencies:
```bash
pip install --extra-index-url https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu \
    wheelhouse-therock/uccl-*.whl[rocm]
```

Sources: [build_and_install.sh:16-26](), [README.md:100]()

### Verifying Installation

After installation, verify the package and locate plugin libraries:

```python
import uccl

# Get plugin library paths
print(uccl.nccl_plugin_path())  # /path/to/uccl/lib/libnccl-net-uccl.so
print(uccl.rccl_plugin_path())  # /path/to/uccl/lib/librccl-net-uccl.so
print(uccl.efa_plugin_path())   # /path/to/uccl/lib/libnccl-net-efa.so

# Check version
print(uccl.__version__)  # e.g., "0.0.1.post4"
```

Use these paths to configure NCCL/RCCL to use UCCL plugins (see page 6.1 for integration details).

Sources: [uccl/__init__.py:30-55](), [README.md:103-114]()

## Build Execution Workflow

```mermaid
sequenceDiagram
    participant User
    participant BuildSh["build.sh"]
    participant Docker["Docker Engine"]
    participant Container["Build Container"]
    participant Wheel["wheelhouse-TARGET/"]
    
    User->>BuildSh: ./build.sh cuda all 3.13
    
    rect rgb(240, 240, 240)
    note right of BuildSh: Setup Phase
    BuildSh->>BuildSh: Parse TARGET, BUILD_TYPE, PY_VER
    BuildSh->>BuildSh: Detect ARCH (x86_64/aarch64)
    BuildSh->>BuildSh: Detect IS_EFA (check /sys/class/infiniband/)
    BuildSh->>BuildSh: Select Dockerfile (cuda/rocm/gh/efa/therock)
    BuildSh->>BuildSh: Check image staleness
    end
    
    rect rgb(240, 240, 240)
    note right of Docker: Image Build Phase
    BuildSh->>Docker: docker build --build-arg PY_VER=3.13<br/>-t uccl-builder-cuda -f Dockerfile.cuda
    Docker->>Docker: Install Ubuntu 22.04 + CUDA 12.8
    Docker->>Docker: Install Python 3.13 + PyTorch
    Docker->>Docker: Install build tools (cmake, pybind11, auditwheel)
    Docker-->>BuildSh: Image ready
    end
    
    rect rgb(240, 240, 240)
    note right of Container: Build Phase (Inside Container)
    BuildSh->>Container: docker run --rm -v $(pwd):/io<br/>-e TARGET=cuda -e BUILD_TYPE=all
    Container->>Container: eval build functions (bash)
    Container->>Container: build_ccl_rdma() -> collective/rdma/Makefile
    Container->>Container: build_ccl_efa() -> collective/efa/Makefile
    Container->>Container: build_p2p() -> p2p/Makefile
    Container->>Container: cp *.so to uccl/lib/
    end
    
    rect rgb(240, 240, 240)
    note right of Container: Package Phase
    Container->>Container: python3 -m build (calls setup.py)
    Container->>Container: auditwheel repair dist/uccl-*.whl<br/>--exclude libtorch*.so<br/>--exclude libcudart.so.12
    Container->>Wheel: Write uccl-VERSION-py3-none-PLATFORM.whl
    end
    
    Wheel-->>User: Build complete
```

Key execution steps:

1. **Setup** ([build.sh:15-23]()): Parse arguments and detect platform
2. **Image Build** ([build.sh:255-268]()): Build or reuse Docker image with toolchain
3. **Build Functions** ([build.sh:295-351]()): Execute component-specific build functions
4. **Packaging** ([build.sh:386-401]()): Generate wheel with `python -m build` and repair with `auditwheel`
5. **Output** ([build.sh:435-436]()): Store wheel in `wheelhouse-TARGET/` directory

Sources: [build.sh:1-437]()

## Development Environment and CI/CD

UCCL uses Docker-based development environments and automated CI/CD processes to ensure code quality and consistent builds across platforms.

```mermaid
flowchart TD
    subgraph "Development Workflow"
        DevEnv["Development Environment"] --> Docker["Docker Containers"]
        DevEnv --> Formatting["Code Formatting"]
        DevEnv --> CI["CI/CD Processes"]
        
        Docker --> CudaDev["CUDA Development"]
        Docker --> RocmDev["ROCm Development"]
        Docker --> EFADev["EFA Development"]
        
        Formatting --> ClangFormat["clang-format"]
        Formatting --> BlackFormat["black (Python)"]
        
        CI --> FormatCheck["Format Check Workflow"]
        CI --> BuildCheck["Build Validation"]
        CI --> TestCheck["Test Execution"]
    end
    
    subgraph "Quality Assurance"
        QA["Code Quality"] --> FormatScript["format.sh"]
        QA --> GithubActions[".github/workflows/"]
        
        FormatScript --> CppFormat["C++ Formatting (clang-format-14)"]
        FormatScript --> PyFormat["Python Formatting (black)"]
        
        GithubActions --> ClangCI["clang-format-check.yml"]
    end
```

The development environment emphasizes reproducible builds and consistent code quality through automated tooling.

Sources: [format.sh:1-72](), [.github/workflows/clang-format-check.yml:1-91]()

### Code Formatting Standards

UCCL enforces consistent code formatting across the codebase using automated tools:

#### C++ Code Formatting

Uses `clang-format-14` to format C++ source files across multiple directories:

```bash
# Directories formatted
DIRECTORIES=("afxdp" "efa" "gpu_driven" "rdma" "misc" "p2p" "include")
# File extensions
EXTENSIONS=("cpp" "cxx" "cc" "h" "hpp" "cu" "cuh")
# Excluded directories
EXCLUDE=("afxdp/lib")
```

Run formatting manually:
```bash
./format.sh
```

Sources: [format.sh:7-9](), [format.sh:28-55]()

#### Python Code Formatting

Uses `black` to format Python code in specific directories:

```bash
# Python directories formatted
PYTHON_DIRS=("p2p" "gpu_driven")
# Excluded patterns
EXCLUDES="thirdparty|doc|build"
```

Sources: [format.sh:59-70](), [.github/workflows/clang-format-check.yml:83-90]()

### CI/CD Workflows

The CI system automatically validates code formatting and build integrity:

#### Automated Format Checking

The GitHub Actions workflow `clang-format-check.yml` runs on every push and pull request:

```yaml
# C++ format validation
- name: Check C++ formatting
  run: clang-format --dry-run --Werror "${FILES[@]}"

# Python format validation  
- name: Check Python formatting
  run: black "$DIR" --exclude "$EXCLUDES" --check
```

The workflow fails if any files don't conform to the formatting standards, ensuring consistent code style.

Sources: [.github/workflows/clang-format-check.yml:28-64](), [.github/workflows/clang-format-check.yml:82-90]()

### Development Dependencies

For local development without Docker, install these dependencies:

```bash
sudo apt update
sudo apt install linux-tools-$(uname -r) clang llvm cmake m4 build-essential \
                 net-tools libgoogle-glog-dev libgtest-dev libgflags-dev \
                 libelf-dev libpcap-dev libc6-dev-i386 \
                 libopenmpi-dev libibverbs-dev libpci-dev -y

# Install Anaconda for Python environment management
wget https://repo.anaconda.com/archive/Anaconda3-2025.06-1-Linux-x86_64.sh
bash ./Anaconda3-2025.06-1-Linux-x86_64.sh -b
```

However, the recommended approach is to use the Docker-based build system which handles all dependencies automatically.

Sources: [doc/dev.md:14-29]()

## Running the AF_XDP Daemon

For AF_XDP mode, UCCL requires the AF_XDP daemon to be running. This daemon handles the privileged operations related to AF_XDP sockets.

```mermaid
flowchart TD
    subgraph "AF_XDP Daemon Management"
        Setup["setup_all.py"] -->|"AF_XDP Mode"| Daemon["Start AF_XDP Daemon"]
        Daemon -->|"Kill Any Existing Daemon"| Kill["pkill afxdp_daemon"]
        Kill -->|"Launch New Daemon"| Launch["sudo ./afxdp_daemon_main --logtostderr=1"]
        Launch -->|"Daemon Running"| Running["AF_XDP Daemon Running"]
        Setup -->|"Handle SIGINT"| SigInt["Signal Handler"]
        SigInt -->|"Terminate Daemon"| Terminate["Kill Daemon Process"]
    end
```

The AF_XDP daemon is started with elevated privileges (using `sudo`) and runs until the `setup_all.py` script is terminated. The script sets up a signal handler to properly terminate the daemon when the script is interrupted.

Sources: [setup_all.py:132-149]()

## Verifying the Setup

After deploying UCCL, you can verify the setup using the transport test utility:

```
cd $UCCL_HOME/afxdp/
./transport_test --logtostderr=1 --clientip=<peer_ip> --test=bimq
```

On the peer node:
```
./transport_test --logtostderr=1 --client --serverip=<server_ip> --test=bimq
```

A successful test will show performance metrics like median RTT, tail RTT, and bandwidth.

Sources: [README.md:120-132]()

## Running NCCL Tests

To run NCCL tests with UCCL:

```
python setup_all.py --target aws_g4_afxdp
cd $UCCL_HOME/afxdp/
./run_nccl_test.sh afxdp 2 <nic>
```

This will run NCCL collective communication tests using the UCCL transport.

Sources: [README.md:134-138]()

## Network RSS Configuration (Optional)

For advanced users, UCCL provides utilities to work with the Receive Side Scaling (RSS) configuration of network interfaces. This can be useful for optimizing multi-path communications.

The `get_rss_config` function retrieves the RSS key and redirection table from a network interface:

```
bool get_rss_config(const std::string& interface_name,
                   std::vector<uint32_t>& redir_table,
                   std::vector<uint8_t>& rss_key)
```

The `calculate_queue_id` function determines which queue a packet will be directed to based on its 4-tuple (source IP, destination IP, source port, destination port):

```
uint32_t calculate_queue_id(uint32_t src_ip, uint32_t dst_ip,
                           uint16_t src_port, uint16_t dst_port,
                           const std::vector<uint8_t>& rss_key,
                           const std::vector<uint32_t>& redir_table)
```

These utilities can be used to tune the packet distribution across multiple queues.

Sources: [util_rss.h:20-163](), [rss_hash_test.cc:1-84]()

---

# Page: Build Scripts and Docker Environments

# Build Scripts and Docker Environments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docker/Dockerfile.cuda](docker/Dockerfile.cuda)
- [docker/Dockerfile.efa](docker/Dockerfile.efa)
- [docker/Dockerfile.gh](docker/Dockerfile.gh)
- [docker/Dockerfile.rocm](docker/Dockerfile.rocm)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/install_deps.sh](ep/install_deps.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This document covers UCCL's Docker-based build system, including the main build orchestrator (`build.sh`), platform-specific Docker environments, and Python wheel packaging. The build system uses containerized environments to ensure reproducible builds across different GPU backends (CUDA, ROCm, TheRock) and architectures (x86_64, aarch64), producing installable Python wheels containing native shared libraries for each transport backend.

For installation instructions using pre-built wheels, see [Installation and Setup](#1.2). For platform-specific compilation flags and dependency management, see [Platform-Specific Configuration](#5.2).

## Build System Architecture

The UCCL build system follows a Docker-based approach where specialized container images provide complete toolchains for each target platform. The `build.sh` script orchestrates the entire build process: detecting the target platform, spawning the appropriate Docker container, compiling C++/CUDA/HIP code for multiple transport backends, and packaging everything into Python wheels.

### Build System Overview

```mermaid
graph TB
    subgraph "Build_Scripts"
        BUILD_AND_INSTALL["build_and_install.sh<br/>Convenience Wrapper"]
        BUILD_SH["build.sh<br/>Main Build Orchestrator"]
        SETUP_PY["setup.py<br/>Python Package Definition"]
        PYPROJECT["pyproject.toml<br/>Build Backend Config"]
    end
    
    subgraph "Docker_Images"
        CUDA_DOCKER["uccl-builder-cuda<br/>Dockerfile.cuda<br/>CUDA 12.x + x86_64"]
        ROCM_DOCKER["uccl-builder-rocm<br/>Dockerfile.rocm<br/>ROCm 7.x + x86_64"]
        THEROCK_DOCKER["uccl-builder-therock<br/>Dockerfile.therock<br/>manylinux + ROCm SDK"]
        EFA_DOCKER["uccl-builder-efa<br/>Dockerfile.efa<br/>CUDA + AWS EFA"]
        GH_DOCKER["uccl-builder-gh<br/>Dockerfile.gh<br/>CUDA + aarch64/GH200"]
    end
    
    subgraph "Component_Build_Functions"
        BUILD_CCL_RDMA["build_ccl_rdma()<br/>collective/rdma/Makefile"]
        BUILD_CCL_EFA["build_ccl_efa()<br/>collective/efa/Makefile"]
        BUILD_P2P["build_p2p()<br/>p2p/Makefile"]
        BUILD_EP["build_ep()<br/>ep/setup.py"]
    end
    
    subgraph "Output_Wheels"
        CUDA_WHEEL["wheelhouse-cuda/<br/>uccl-*.whl"]
        ROCM_WHEEL["wheelhouse-rocm/<br/>uccl-*+rocm7.*.whl"]
        THEROCK_WHEEL["wheelhouse-therock/<br/>uccl-*+rocm*.whl"]
    end
    
    BUILD_AND_INSTALL --> BUILD_SH
    BUILD_SH --> CUDA_DOCKER
    BUILD_SH --> ROCM_DOCKER
    BUILD_SH --> THEROCK_DOCKER
    BUILD_SH --> EFA_DOCKER
    BUILD_SH --> GH_DOCKER
    
    CUDA_DOCKER --> BUILD_CCL_RDMA
    CUDA_DOCKER --> BUILD_CCL_EFA
    CUDA_DOCKER --> BUILD_P2P
    CUDA_DOCKER --> BUILD_EP
    
    ROCM_DOCKER --> BUILD_CCL_RDMA
    ROCM_DOCKER --> BUILD_P2P
    ROCM_DOCKER --> BUILD_EP
    
    THEROCK_DOCKER --> BUILD_CCL_RDMA
    THEROCK_DOCKER --> BUILD_P2P
    
    BUILD_CCL_RDMA --> SETUP_PY
    BUILD_P2P --> SETUP_PY
    BUILD_EP --> SETUP_PY
    
    SETUP_PY --> CUDA_WHEEL
    SETUP_PY --> ROCM_WHEEL
    SETUP_PY --> THEROCK_WHEEL
    
    PYPROJECT --> CUDA_WHEEL
```

Sources: [build.sh:1-437](), [build_and_install.sh:1-40](), [setup.py:1-49](), [pyproject.toml:1-3]()

## build.sh: Main Build Orchestrator

The `build.sh` script is the primary entry point for building UCCL. It performs platform detection, selects the appropriate Docker image, executes builds inside containers, and produces Python wheels in `wheelhouse-{target}/` directories.

### Build Script Parameters

| Parameter | Values | Description | Default |
|-----------|---------|-------------|---------|
| `TARGET` | `cuda`, `cuda13`, `rocm`, `rocm6`, `therock` | GPU backend to build for | `cuda` |
| `BUILD_TYPE` | `all`, `ccl_rdma`, `ccl_efa`, `p2p`, `ep` | Components to build | `all` |
| `PY_VER` | `3.8` - `3.13` | Python version for wheel | Auto-detected |
| `ROCM_IDX_URL` | URL | ROCm index URL for TheRock builds | `https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu` |
| `THEROCK_BASE_IMAGE` | Docker image | Base manylinux image for TheRock | `quay.io/pypa/manylinux_2_28_x86_64@sha256:...` |

### Platform Detection and Docker Image Selection

The script detects the target platform using architecture checks and EFA device presence, then selects the corresponding Docker image:

```mermaid
graph TB
    subgraph "Detection_Logic"
        ARCH_CHECK["ARCH=$(uname -m)<br/>x86_64 or aarch64"]
        IS_EFA["IS_EFA=$(ls /sys/class/infiniband/<br/>grep rdmap)"]
        TARGET_PARAM["TARGET Parameter<br/>cuda|rocm|therock"]
    end
    
    subgraph "Docker_Image_Selection"
        CUDA_STANDARD["TARGET=cuda<br/>ARCH=x86_64<br/>!IS_EFA<br/>→ uccl-builder-cuda"]
        CUDA_EFA["TARGET=cuda<br/>ARCH=x86_64<br/>IS_EFA<br/>→ uccl-builder-efa"]
        CUDA_ARM["TARGET=cuda<br/>ARCH=aarch64<br/>→ uccl-builder-gh"]
        ROCM_X86["TARGET=rocm<br/>ARCH=x86_64<br/>→ uccl-builder-rocm"]
        THEROCK_X86["TARGET=therock<br/>ARCH=x86_64<br/>→ uccl-builder-therock"]
    end
    
    ARCH_CHECK --> CUDA_STANDARD
    ARCH_CHECK --> CUDA_ARM
    IS_EFA --> CUDA_EFA
    TARGET_PARAM --> CUDA_STANDARD
    TARGET_PARAM --> ROCM_X86
    TARGET_PARAM --> THEROCK_X86
```

Sources: [build.sh:15-23](), [build.sh:194-230]()

### Build Functions and Output Libraries

The script defines separate build functions for each component, invoked inside Docker containers:

```mermaid
graph LR
    subgraph "Build_Functions_in_build_sh"
        BUILD_CCL_RDMA["build_ccl_rdma()<br/>Lines 53-90"]
        BUILD_CCL_EFA["build_ccl_efa()<br/>Lines 92-115"]
        BUILD_P2P["build_p2p()<br/>Lines 117-148"]
        BUILD_EP["build_ep()<br/>Lines 150-170"]
    end
    
    subgraph "Output_Files_in_uccl_lib"
        NCCL_PLUGIN["uccl/lib/<br/>libnccl-net-uccl.so"]
        RCCL_PLUGIN["uccl/lib/<br/>librccl-net-uccl.so"]
        EFA_PLUGIN["uccl/lib/<br/>libnccl-net-efa.so"]
        EFA_NCCL["uccl/lib/<br/>libnccl-efa.so"]
        P2P_SO["uccl/<br/>p2p.*.so"]
        P2P_PY["uccl/<br/>collective.py<br/>transfer.py<br/>utils.py"]
        EP_SO["uccl/<br/>ep.*.so"]
    end
    
    BUILD_CCL_RDMA --> NCCL_PLUGIN
    BUILD_CCL_RDMA --> RCCL_PLUGIN
    BUILD_CCL_EFA --> EFA_PLUGIN
    BUILD_CCL_EFA --> EFA_NCCL
    BUILD_P2P --> P2P_SO
    BUILD_P2P --> P2P_PY
    BUILD_EP --> EP_SO
```

Each build function compiles native code using component-specific Makefiles:

- **`build_ccl_rdma()`**: Compiles collective RDMA transport using `collective/rdma/Makefile` (CUDA) or `Makefile.rocm` (ROCm) or `Makefile.therock` (TheRock)
- **`build_ccl_efa()`**: Compiles AWS EFA transport using `collective/efa/Makefile` and custom NCCL from `thirdparty/nccl-sg`
- **`build_p2p()`**: Compiles P2P engine using `p2p/Makefile`, `Makefile.rocm`, or `Makefile.therock`
- **`build_ep()`**: Compiles Expert Parallelism system using `ep/setup.py` (Python-based build)

Sources: [build.sh:53-170](), [build.sh:335-351]()

## Docker Build Environments

UCCL provides five specialized Docker images, each containing the complete toolchain for a specific target platform. These images are defined in `docker/Dockerfile.*` and built as `uccl-builder-*`.

### Dockerfile.cuda: Standard CUDA x86_64 Builds

**Base Image**: `nvidia/cuda:12.8.0-devel-ubuntu22.04`

**Purpose**: Builds UCCL for standard NVIDIA GPUs on x86_64 with InfiniBand/RoCE NICs.

**Key Components**:
- CUDA Toolkit 12.8 (or configurable via `BASE_IMAGE`)
- Python 3.13 (default, configurable via `PY_VER`)
- Build tools: `cmake`, `ninja`, `g++`, `make`, `patchelf`
- RDMA libraries: `libibverbs-dev`, `rdma-core`
- Additional dependencies: `libgoogle-glog-dev`, `libgflags-dev`, `libgtest-dev`, `libnuma-dev`
- PyTorch with CUDA support from `https://download.pytorch.org/whl/cu128`
- Python build backends: `build`, `auditwheel`, `pybind11`

Sources: [docker/Dockerfile.cuda:1-52]()

### Dockerfile.rocm: AMD ROCm x86_64 Builds

**Base Image**: `rocm/dev-ubuntu-22.04` (ROCm 7.x default)

**Purpose**: Builds UCCL for AMD GPUs with HIP/ROCm on x86_64.

**Key Components**:
- ROCm SDK with HIP compiler (`hipcc`)
- HIP libraries: `hipsolver`, `hipblas`, `hipsparse`, `rocthrust`, `hipblaslt`
- Python 3.13 via deadsnakes PPA
- RDMA libraries: `libibverbs-dev`, `rdma-core`
- Redis for OOB backend: `libhiredis-dev`
- PyTorch nightly with ROCm 7.0 support from `https://download.pytorch.org/whl/nightly/rocm7.0`

**Special Note**: ROCm does not include `nccl.h`, so the build process compiles RCCL headers by running `CXX=/opt/rocm/bin/hipcc cmake` on `thirdparty/rccl` to generate `nccl.h`.

Sources: [docker/Dockerfile.rocm:1-54](), [build.sh:44-50]()

### Dockerfile.therock: TheRock Manylinux Builds

**Base Image**: `ghcr.io/rocm/therock_build_manylinux_x86_64` or configurable via parameter

**Purpose**: Builds portable UCCL wheels with Python-packaged ROCm dependencies for TheRock ecosystem.

**Key Components**:
- Manylinux 2.28 base with all Python versions pre-installed
- Python virtual environment with ROCm SDK installed via `pip install rocm[libraries,devel]`
- Uses `rocm-sdk` CLI tool for path resolution: `$(rocm-sdk path --root)`, `$(rocm-sdk path --cmake)`
- RDMA libraries: `rdma-core-devel`
- Minimal system dependencies (no ROCm system packages)

**TheRock-Specific Build Process**:
1. Select Python version from PyPA multi-python environment
2. Create temporary venv and install ROCm SDK via pip with `ROCM_IDX_URL`
3. Compile with `HIP_HOME=$(rocm-sdk path --root)`
4. Generate `uccl/_rocm_init.py` to initialize ROCm SDK at import time
5. Modify `setup.py` to add ROCm wheel dependency, then restore after build

Sources: [docker/Dockerfile.therock:1-17](), [build.sh:316-391]()

### Dockerfile.efa: AWS EFA CUDA Builds

**Base Image**: `nvidia/cuda:12.8.0-devel-ubuntu22.04`

**Purpose**: Builds UCCL with AWS EFA NIC support on p4d/p4de/p5 instances.

**Key Components**:
- CUDA Toolkit 12.8
- AWS EFA installer v1.42.0 (installed with `--skip-kmod --no-verify` for container environment)
- EFA libraries in `/opt/amazon/efa/lib64`
- Event libraries: `libevent-dev`, `libhwloc-dev` with symlinks for version compatibility
- Python 3.13 and PyTorch with CUDA 12.8 support

**EFA Installation Process**:
```bash
curl -O https://efa-installer.amazonaws.com/aws-efa-installer-${EFA_VER}.tar.gz
./efa_installer.sh -y --skip-kmod -g --no-verify
```

Sources: [docker/Dockerfile.efa:1-76]()

### Dockerfile.gh: Grace Hopper ARM64 Builds

**Base Image**: `nvidia/cuda:12.4.1-devel-ubuntu22.04`

**Purpose**: Builds UCCL for NVIDIA Grace Hopper (GH200) ARM64 superchips.

**Key Components**:
- CUDA Toolkit 12.4 for aarch64 architecture
- ARM64-compatible build tools and libraries
- Python 3.13 for aarch64
- Environment variable `GPU_NAME=GH200` set for Makefile detection
- PyTorch 2.6.0 with CUDA 12.6 support

**Architecture Detection**: The container sets `GPU_NAME=GH200` which triggers Grace Hopper-specific compilation flags in Makefiles, such as `-DUSE_GRACE_HOPPER` in EP builds.

Sources: [docker/Dockerfile.gh:1-51](), [ep/Makefile:16-32]()

### Docker Image Build and Caching

The `build.sh` script includes staleness detection to warn users when Dockerfiles are newer than built images:

```mermaid
graph TB
    subgraph "Docker_Image_Staleness_Check"
        CHECK_EXISTS["Image Exists?<br/>docker images -q"]
        GET_TIMESTAMPS["Compare Timestamps<br/>Dockerfile vs Image.Created"]
        WARN_USER["Print Warning:<br/>Suggest docker image rm<br/>and docker buildx prune"]
    end
    
    CHECK_EXISTS --> GET_TIMESTAMPS
    GET_TIMESTAMPS --> WARN_USER
```

The Docker build command supports custom base images and Python versions:

```bash
BUILD_ARGS="--build-arg PY_VER=${PY_VER}"
if [[ -n "${BASE_IMAGE:-}" ]]; then
  BUILD_ARGS+=" --build-arg BASE_IMAGE=${BASE_IMAGE}"
fi
docker build $BUILD_ARGS -t "$IMAGE_NAME" -f "$DOCKERFILE" .
```

Sources: [build.sh:232-268]()

## Build Functions and Container Execution

The `build.sh` script defines shell functions that are serialized and executed inside Docker containers via the `FUNCTION_DEF` environment variable. This approach allows complex build logic to run in isolated environments.

### Container Execution Pattern

```mermaid
graph TB
    subgraph "Host_build_sh"
        DEFINE_FUNCS["declare -f build_rccl_nccl_h<br/>build_ccl_rdma<br/>build_ccl_efa<br/>build_p2p<br/>build_ep"]
        DOCKER_RUN["docker run<br/>-v $(pwd):/io<br/>-e FUNCTION_DEF=..."]
    end
    
    subgraph "Container_Execution"
        EVAL_FUNCS["eval $FUNCTION_DEF<br/>Re-create functions"]
        CALL_FUNCS["Call build_* functions<br/>based on BUILD_TYPE"]
        PYTHON_BUILD["python3 -m build<br/>Create wheel"]
        AUDITWHEEL["auditwheel repair<br/>Bundle dependencies"]
    end
    
    DEFINE_FUNCS --> DOCKER_RUN
    DOCKER_RUN --> EVAL_FUNCS
    EVAL_FUNCS --> CALL_FUNCS
    CALL_FUNCS --> PYTHON_BUILD
    PYTHON_BUILD --> AUDITWHEEL
```

Sources: [build.sh:295-311](), [build.sh:313-432]()

### build_ccl_rdma(): Collective RDMA Transport

Compiles the NCCL/RCCL plugin for InfiniBand/RoCE NICs.

**Input Parameters**: `TARGET`, `ARCH`, `IS_EFA`

**Build Process**:
1. For CUDA: `cd collective/rdma && make -j$(nproc)`
2. For ROCm: `cd collective/rdma && make -j$(nproc) -f Makefile.rocm`
3. For TheRock: `make -j$(nproc) -f Makefile.therock HIP_HOME=$(rocm-sdk path --root)`
4. Copy output to `uccl/lib/libnccl-net-uccl.so` or `librccl-net-uccl.so`

**Special Handling**: ROCm and TheRock builds must first generate `nccl.h` by building RCCL headers:
```bash
cd thirdparty/rccl
CXX=hipcc cmake -B build/release -S . -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF
```

Sources: [build.sh:53-90](), [build.sh:44-51]()

### build_ccl_efa(): Collective EFA Transport

Compiles the AWS EFA plugin and custom NCCL library.

**Build Process**:
1. Skip on ARM64 or ROCm targets (EFA requires CUDA on x86_64)
2. `cd collective/efa && make -j$(nproc)`
3. Build custom NCCL: `cd thirdparty/nccl-sg && make src.build -j$(nproc) NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90"`
4. Copy `libnccl-net-efa.so` and `libnccl-efa.so` to `uccl/lib/`

Sources: [build.sh:92-115]()

### build_p2p(): P2P Communication Engine

Compiles the point-to-point transfer engine with pybind11 Python bindings.

**Build Process**:
1. For CUDA: `cd p2p && make -j$(nproc)`
2. For ROCm: `make -j$(nproc) -f Makefile.rocm`
3. For TheRock: `make -j$(nproc) -f Makefile.therock HIP_HOME=$(rocm-sdk path --root) CONDA_LIB_HOME=$VIRTUAL_ENV/lib`
4. Copy outputs to `uccl/lib/` and `uccl/`:
   - `libuccl_p2p.so` (shared library)
   - `librdma_plugin.a` (static archive)
   - `p2p.*.so` (Python extension)
   - `collective.py`, `transfer.py`, `utils.py` (Python modules)

**Special Case**: When `USE_TCPX=1`, skips copying runtime files.

Sources: [build.sh:117-148]()

### build_ep(): Expert Parallelism System

Compiles GPU-initiated communication for MoE models using Python's build system.

**Build Process**:
1. Skip on TheRock (no GPU-driven support yet)
2. For CUDA/ROCm: `cd ep && python3 setup.py build`
3. Copy `ep/build/**/*.so` to `uccl/`

The EP build uses its own `setup.py` which detects GPU architecture and configures compilation flags automatically.

Sources: [build.sh:150-170](), [ep/Makefile:1-114]()

## Platform-Specific Build Logic

The build system includes conditional compilation logic to handle platform-specific constraints and capabilities.

### Cross-Platform Compilation Matrix

| Platform | ccl_rdma | ccl_efa | p2p | ep | Docker Image |
|----------|----------|---------|-----|-----|--------------|
| x86_64 + CUDA | ✓ | ✓ | ✓ | ✓ | `uccl-builder-cuda` |
| x86_64 + CUDA + EFA | ✓ | ✓ | ✓ | ✓ | `uccl-builder-efa` |
| x86_64 + ROCm | ✓ | ✗ | ✓ | ✓ | `uccl-builder-rocm` |
| x86_64 + TheRock | ✓ | ✗ | ✓ | ✗ | `uccl-builder-therock` |
| aarch64 + CUDA (GH200) | ✓ | ✗ | ✓ | ✓ | `uccl-builder-gh` |

### Architecture Detection and Skip Logic

The build script detects architecture constraints and skips incompatible builds:

```mermaid
graph TB
    subgraph "Skip_Conditions"
        CHECK_ROCM_ARM["TARGET=rocm<br/>ARCH=aarch64<br/>→ Exit (no ROCm on ARM)"]
        CHECK_EFA_INCOMPAT["TARGET=rocm OR<br/>ARCH=aarch64<br/>→ Skip EFA build"]
        CHECK_THEROCK_EP["TARGET=therock<br/>→ Skip EP build"]
        CHECK_THEROCK_ARM["TARGET=therock<br/>ARCH=aarch64<br/>→ Exit"]
    end
    
    subgraph "Build_Decisions"
        SKIP_CCL_EFA["Skip build_ccl_efa()"]
        SKIP_EP["Skip build_ep()"]
        EXIT_SCRIPT["Exit with message"]
    end
    
    CHECK_ROCM_ARM --> EXIT_SCRIPT
    CHECK_THEROCK_ARM --> EXIT_SCRIPT
    CHECK_EFA_INCOMPAT --> SKIP_CCL_EFA
    CHECK_THEROCK_EP --> SKIP_EP
```

**Key Skip Conditions**:

1. **ROCm on ARM64**: Entire build exits because no ROCm toolchain exists for aarch64
   ```bash
   if [[ $ARCH == "aarch64" && ( $TARGET == rocm* || $TARGET == "therock" ) ]]; then
     echo "Skipping ROCm build on Arm64 (no ROCm toolchain)."
     exit 1
   fi
   ```

2. **EFA builds**: Skipped on ROCm (no CUDA) or ARM64 (no EFA installer)
   ```bash
   if [[ "$ARCH" == "aarch64" || "$TARGET" == rocm* || "$TARGET" == "therock" ]]; then
     echo "Skipping EFA build..."
     return
   fi
   ```

3. **EP on TheRock**: GPU-driven builds not yet supported on TheRock
   ```bash
   if [[ "$TARGET" == "therock" ]]; then
     echo "Skipping GPU-driven build on therock (no GPU-driven support yet)."
   fi
   ```

Sources: [build.sh:31-34](), [build.sh:100-103](), [build.sh:158-159]()

### GPU Architecture Auto-Detection

For EP builds, the script auto-detects GPU compute capability:

**CUDA Detection**:
```bash
DETECTED_GPU_ARCH=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d ' ')
export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-${DETECTED_GPU_ARCH}}"
```

**ROCm Detection**:
```bash
DETECTED_GPU_ARCH=$(amd-smi static -g 0 --asic --json | jq -r '.[].asic.target_graphics_version')
```

Sources: [build.sh:272-294]()

## Python Packaging with setup.py

The `setup.py` file defines the Python package structure and specifies which compiled artifacts to include in the wheel.

### Package Data Specification

```python
package_data={
    "uccl": [
        "lib/*.so",      # NCCL/RCCL plugins, EFA libraries
        "p2p*.so",       # P2P Python extension
        "ep*.so",        # EP Python extension
        "lib/*.a",       # Static archives (librdma_plugin.a)
        "collective.py", # P2P high-level API
        "transfer.py",   # Transfer utilities
        "utils.py",      # P2P utilities
    ],
}
```

### Plugin Path Resolution

The `uccl/__init__.py` module provides helper functions to locate plugin shared libraries at runtime:

```mermaid
graph LR
    subgraph "Plugin_Path_Functions"
        NCCL_PLUGIN["nccl_plugin_path()<br/>Returns lib/libnccl-net-uccl.so"]
        RCCL_PLUGIN["rccl_plugin_path()<br/>Returns lib/librccl-net-uccl.so"]
        EFA_PLUGIN["efa_plugin_path()<br/>Returns lib/libnccl-net-efa.so"]
        EFA_NCCL["efa_nccl_path()<br/>Returns lib/libnccl-efa.so"]
    end
    
    subgraph "Environment_Variables"
        NCCL_NET_PLUGIN["NCCL_NET_PLUGIN=<br/>$(python -c 'import uccl; print(uccl.nccl_plugin_path())')"]
        LD_PRELOAD["LD_PRELOAD=<br/>$(python -c 'import uccl; print(uccl.efa_nccl_path())')"]
    end
    
    NCCL_PLUGIN --> NCCL_NET_PLUGIN
    EFA_PLUGIN --> NCCL_NET_PLUGIN
    EFA_NCCL --> LD_PRELOAD
```

**TheRock-Specific Initialization**: For TheRock builds, an additional `uccl/_rocm_init.py` module is generated during the build to initialize the ROCm SDK:

```python
def initialize():
  import rocm_sdk
  rocm_sdk.initialize_process(preload_shortnames=[
    "amdhip64", "roctx64", "hiprtc", "hipblas", "rccl", ...
  ], check_version="7.0.0")
```

This module is automatically imported by `uccl/__init__.py` if present.

Sources: [setup.py:18-48](), [uccl/__init__.py:1-55](), [build.sh:358-376]()

### Version Management

The package version is read from `uccl/__init__.py` by `setup.py`:

```python
def get_version():
    with open("uccl/__init__.py", "r") as f:
        content = f.read()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    return match.group(1)
```

Sources: [setup.py:6-16](), [uccl/__init__.py:30]()

## Wheel Generation and Distribution

The final step produces platform-specific Python wheels with embedded native libraries.

### Wheel Building Process

```mermaid
graph LR
    subgraph "Wheel Generation"
        PYTHON_BUILD["python3 -m build<br/>Generate Wheel"]
        AUDITWHEEL["auditwheel repair<br/>Bundle Dependencies"]
        RENAME["Backend Tagging<br/>Add +rocm suffix"]
    end
    
    subgraph "Output Structure"
        WHEEL_CUDA["wheelhouse-cuda/<br/>uccl-*.whl"]
        WHEEL_ROCM["wheelhouse-rocm/<br/>uccl-*+rocm.whl"]
    end
    
    PYTHON_BUILD --> AUDITWHEEL
    AUDITWHEEL --> RENAME
    RENAME --> WHEEL_CUDA
    RENAME --> WHEEL_ROCM
```

### Library Bundling

The `auditwheel` tool repairs wheels by bundling dependencies while excluding system libraries:

```bash
auditwheel repair dist/uccl-*.whl \
  --exclude "libtorch*.so" \
  --exclude "libc10*.so" \
  --exclude "libibverbs.so.1" \
  --exclude "libcudart.so.12" \
  --exclude "libamdhip64.so.6" \
  -w /io/${WHEEL_DIR}
```

### Backend Tagging

ROCm wheels receive special naming to distinguish from CUDA builds:

- CUDA wheels: `uccl-0.0.1.post4-py3-none-linux_x86_64.whl`
- ROCm wheels: `uccl-0.0.1.post4+rocm-py3-none-linux_x86_64.whl`

Sources: [build.sh:197-225](), [build.sh:200-223]()

---

# Page: Platform-Specific Configuration

# Platform-Specific Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/clang-format-check.yml](.github/workflows/clang-format-check.yml)
- [docker/Dockerfile.cuda](docker/Dockerfile.cuda)
- [docker/Dockerfile.efa](docker/Dockerfile.efa)
- [docker/Dockerfile.gh](docker/Dockerfile.gh)
- [docker/Dockerfile.rocm](docker/Dockerfile.rocm)
- [ep/install_deps.sh](ep/install_deps.sh)
- [format.sh](format.sh)
- [scripts/node_ips/amd.txt](scripts/node_ips/amd.txt)
- [scripts/node_ips/tpu_2.txt](scripts/node_ips/tpu_2.txt)
- [scripts/setup_all.py](scripts/setup_all.py)
- [scripts/setup_nic.sh](scripts/setup_nic.sh)

</details>



This page documents UCCL's platform detection logic, compilation flags, and dependency management across different hardware and software configurations. UCCL supports five primary platform targets: CUDA (NVIDIA GPUs on x86_64), ROCm (AMD GPUs on x86_64), GH200 (NVIDIA GPUs on ARM64), EFA (AWS-specific networking), and TheRock (Python-packaged ROCm).

For general build system overview and Docker environments, see [Build Scripts and Docker Environments](#5.1). For development environment setup, see [Development Environment](#5.3).

---

## Platform Detection and Target Selection

UCCL's build system performs multi-stage detection to determine the appropriate build configuration. The detection process occurs in [build.sh:14-230]() and determines three key dimensions: target platform, CPU architecture, and network hardware.

### Platform Target Detection

```mermaid
graph TB
    INPUT["build.sh invocation<br/>TARGET parameter"]
    
    subgraph "Target Resolution"
        CUDA["TARGET=cuda<br/>CUDA 12.x default"]
        CUDA13["TARGET=cuda13<br/>CUDA 13.x"]
        ROCM["TARGET=rocm<br/>ROCm 7.x default"]
        ROCM6["TARGET=rocm6<br/>ROCm 6.4.3"]
        THEROCK["TARGET=therock<br/>Python-packaged ROCm"]
    end
    
    subgraph "Dockerfile Selection"
        DF_CUDA["docker/Dockerfile.cuda<br/>nvidia/cuda:12.8.0"]
        DF_GH["docker/Dockerfile.gh<br/>nvidia/cuda:12.4.1"]
        DF_EFA["docker/Dockerfile.efa<br/>+ EFA installer"]
        DF_ROCM["docker/Dockerfile.rocm<br/>rocm/dev-ubuntu-22.04"]
        DF_THEROCK["docker/Dockerfile.therock<br/>manylinux + ROCm SDK"]
    end
    
    subgraph "Architecture Detection"
        ARCH_CHECK["uname -m"]
        X86["x86_64"]
        ARM["aarch64"]
    end
    
    subgraph "Network Hardware Detection"
        EFA_CHECK["/sys/class/infiniband/<br/>rdmap device"]
        EFA_YES["EFA detected"]
        EFA_NO["Standard RDMA"]
    end
    
    INPUT --> CUDA
    INPUT --> CUDA13
    INPUT --> ROCM
    INPUT --> ROCM6
    INPUT --> THEROCK
    
    CUDA --> ARCH_CHECK
    ARCH_CHECK --> X86
    ARCH_CHECK --> ARM
    
    X86 --> EFA_CHECK
    ARM --> DF_GH
    
    EFA_CHECK --> EFA_YES
    EFA_CHECK --> EFA_NO
    
    EFA_YES --> DF_EFA
    EFA_NO --> DF_CUDA
    
    ROCM --> DF_ROCM
    ROCM6 --> DF_ROCM
    THEROCK --> DF_THEROCK
    
    style INPUT fill:#f5f5f5
    style ARCH_CHECK fill:#f5f5f5
    style EFA_CHECK fill:#f5f5f5
```

**Platform Target Selection Logic**

Sources: [build.sh:14-30](), [build.sh:194-230]()

The `TARGET` parameter determines the base Docker image and toolchain. Key detection points:

| Target | Base Image | Toolchain | Python Version | Build Constraints |
|--------|------------|-----------|----------------|-------------------|
| `cuda` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | NVCC, G++ | Parameterized (default: host) | x86_64 or aarch64 |
| `cuda13` | `nvidia/cuda:13.0.1-cudnn-devel-ubuntu22.04` | NVCC, G++ | Parameterized | x86_64 or aarch64 |
| `rocm` | `rocm/dev-ubuntu-22.04:latest` | HIP, G++ | Parameterized | x86_64 only |
| `rocm6` | `rocm/dev-ubuntu-22.04:6.4.3-complete` | HIP, G++ | Parameterized | x86_64 only |
| `therock` | `quay.io/pypa/manylinux_2_28_x86_64` | HIP (from Python pkg) | Multi-version | x86_64 only |
| `gh` (auto) | `nvidia/cuda:12.4.1-devel-ubuntu22.04` | NVCC, G++ | Parameterized | aarch64 only |
| `efa` (auto) | CUDA base + EFA installer | NVCC, G++ | Parameterized | x86_64 with EFA NICs |

Sources: [build.sh:194-230](), [docker/Dockerfile.cuda:1-2](), [docker/Dockerfile.rocm:1-2](), [docker/Dockerfile.therock:1-2](), [docker/Dockerfile.gh:1-2](), [docker/Dockerfile.efa:1-2]()

### Architecture Detection

Architecture detection occurs at [build.sh:18]() using `uname -m`:

```bash
ARCH="$(uname -m)"  # Returns "x86_64" or "aarch64"
```

**Architecture-Specific Constraints:**

- **x86_64**: All platforms supported
- **aarch64**: Only CUDA builds supported (Grace Hopper systems)
- ROCm and TheRock builds explicitly skip on ARM at [build.sh:31-34]()

Sources: [build.sh:18](), [build.sh:31-34]()

### Network Hardware Detection

EFA (Elastic Fabric Adapter) detection determines networking capabilities at [build.sh:23]():

```bash
IS_EFA=$( [ -d "/sys/class/infiniband/" ] && ls /sys/class/infiniband/ 2>/dev/null | grep -q rdmap && echo "EFA support: true" ) || echo "EFA support: false"
```

Runtime EFA detection also occurs in [uccl/__init__.py:12-20]():

```python
def has_efa():
    infiniband = Path("/sys/class/infiniband/")
    try:
        if infiniband.is_dir():
            return any("rdmap" in child.name for child in infiniband.iterdir())
        return False
    except (OSError, PermissionError):
        return False
```

EFA presence affects:
- Dockerfile selection (EFA-specific image with libefa)
- Build flags passed to component builds
- Runtime module loading behavior

Sources: [build.sh:23](), [uccl/__init__.py:12-20]()

---

## Compilation Flags and Preprocessor Definitions

### GPU Architecture-Specific Flags

**CUDA Architecture Detection**

```mermaid
graph LR
    subgraph "CUDA Build Context"
        NVCC["nvidia-smi<br/>--query-gpu=compute_cap"]
        DETECT_SM["DETECTED_SM<br/>e.g. '90' for H100/H200"]
        ENV_SM["TORCH_CUDA_ARCH_LIST<br/>environment variable"]
        MAKE_SM["SM variable<br/>in Makefile"]
    end
    
    subgraph "Compilation"
        NVCC_FLAG["-arch=sm_$SM<br/>nvcc flag"]
        KERNEL_COMPILE["CUDA kernel compilation<br/>ep/src/*.cu"]
    end
    
    NVCC --> DETECT_SM
    DETECT_SM --> ENV_SM
    ENV_SM --> MAKE_SM
    MAKE_SM --> NVCC_FLAG
    NVCC_FLAG --> KERNEL_COMPILE
```

Sources: [build.sh:273-293](), [ep/Makefile:49-51]()

At build time, [build.sh:275-279]() auto-detects GPU compute capability:

```bash
if [[ "$TARGET" == cuda* ]] && command -v nvidia-smi &> /dev/null; then
    DETECTED_GPU_ARCH=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d ' ')
    # Result: "9.0" for H100/H200, "10.0" for B200
fi
```

This is passed to the EP Makefile at [ep/Makefile:49-51]():

```makefile
DETECTED_SM := $(shell nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -n1 | tr -d '.')
SM ?= $(DETECTED_SM)  # Can be overridden: make SM=90
```

The `SM` variable controls NVCC architecture flags at [ep/Makefile:83]():

```makefile
%.o: %.cu
	$(NVCC) -arch=sm_$(SM) $(NVCCFLAGS) $(TORCH_INCS) $(INCLUDES) -MMD -MP -c $< -o $@
```

**ROCm Architecture Detection**

For ROCm builds, GPU architecture detection uses `amd-smi` at [build.sh:280-289]():

```bash
elif [[ "$TARGET" == rocm* ]] && command -v amd-smi &> /dev/null; then
    DETECTED_GPU_ARCH=$(amd-smi static -g 0 --asic --json | jq -r '.[].asic.target_graphics_version')
    # Result: "gfx942" for MI300X
fi
```

Sources: [build.sh:273-293](), [ep/Makefile:49-51](), [ep/Makefile:83]()

### Platform-Specific Preprocessor Definitions

**EP Component Platform Flags**

```mermaid
graph TB
    subgraph "Detection Phase"
        GPU_DETECT["nvidia-smi --query-gpu=name"]
        ARCH_DETECT["uname -m"]
        EFA_DETECT["ls /opt/amazon/efa"]
    end
    
    subgraph "Flag Generation"
        GH_FLAG["-DUSE_GRACE_HOPPER"]
        EFA_FLAG["-DEFA<br/>-I/opt/amazon/efa/include"]
        NORMAL_FLAG["-DMAKE_NORMAL_MODE"]
    end
    
    subgraph "Condition Checks"
        IS_GH200["GPU_NAME=GH200<br/>AND ARCH=aarch64"]
        HAS_EFA["EFA_HOME exists"]
        NORMAL_MODE["MAKE_NORMAL_MODE env set"]
    end
    
    GPU_DETECT --> IS_GH200
    ARCH_DETECT --> IS_GH200
    EFA_DETECT --> HAS_EFA
    
    IS_GH200 -->|true| GH_FLAG
    HAS_EFA -->|true| EFA_FLAG
    NORMAL_MODE -->|true| NORMAL_FLAG
    
    GH_FLAG --> CXXFLAGS
    EFA_FLAG --> CXXFLAGS
    NORMAL_FLAG --> CXXFLAGS
    
    CXXFLAGS["CXXFLAGS / NVCCFLAGS<br/>compilation"]
```

Sources: [ep/Makefile:5-62]()

The EP Makefile performs runtime detection at [ep/Makefile:16-32]():

```makefile
ARCH := $(shell uname -m)
GPU_NAME ?= $(shell nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
CPU_IS_ARM64 := 0
GPU_IS_HOPPER := 0

ifeq ($(ARCH),aarch64)
  CPU_IS_ARM64 := 1
endif
ifneq (,$(findstring GH200,$(GPU_NAME)))
  GPU_IS_HOPPER := 1
endif

ifeq ($(and $(CPU_IS_ARM64),$(GPU_IS_HOPPER)),0)
  GH_CFLAGS :=
else
  GH_CFLAGS := -DUSE_GRACE_HOPPER
endif
```

EFA detection at [ep/Makefile:5-14]():

```makefile
EFA_HOME?=/opt/amazon/efa
ifeq ($(wildcard $(EFA_HOME)),)
  EFA_CFLAGS :=
  EFA_LDFLAGS :=
else
  EFA_CFLAGS := -DEFA -I$(EFA_HOME)/include
  EFA_LDFLAGS := -L$(EFA_HOME)/lib -lefa
endif
```

These flags are aggregated into compilation at [ep/Makefile:58-61]():

```makefile
CXXFLAGS  += $(EFA_CFLAGS) $(GH_CFLAGS) $(NORMAL_CFLAGS)
NVCCFLAGS += $(EFA_CFLAGS) $(GH_CFLAGS) $(NORMAL_CFLAGS)
LDFLAGS   += $(EFA_LDFLAGS)
INCLUDES  += $(EFA_CFLAGS) $(GH_CFLAGS) $(NORMAL_CFLAGS)
```

**Key Preprocessor Definitions:**

| Definition | Condition | Impact |
|------------|-----------|--------|
| `-DUSE_GRACE_HOPPER` | aarch64 + GPU name contains "GH200" | Enables GH200-specific memory access patterns |
| `-DEFA` | `/opt/amazon/efa` exists | Enables EFA RDMA operations, includes libefa headers |
| `-DMAKE_NORMAL_MODE` | `MAKE_NORMAL_MODE` env var set | Builds normal-mode kernels instead of low-latency |

Sources: [ep/Makefile:5-62]()

### Collective Component Platform Flags

The collective RDMA component uses platform-specific Makefiles:

```mermaid
graph TB
    subgraph "Makefile Selection"
        TARGET_CHECK["TARGET variable"]
        
        CUDA_MK["Makefile<br/>standard NCCL plugin"]
        ROCM_MK["Makefile.rocm<br/>RCCL plugin"]
        THEROCK_MK["Makefile.therock<br/>Python-packaged ROCm"]
    end
    
    subgraph "Build Products"
        CUDA_SO["libnccl-net-uccl.so"]
        ROCM_SO["librccl-net-uccl.so"]
        THEROCK_SO["librccl-net-uccl.so<br/>+ TheRock init"]
    end
    
    TARGET_CHECK -->|cuda*| CUDA_MK
    TARGET_CHECK -->|rocm*| ROCM_MK
    TARGET_CHECK -->|therock| THEROCK_MK
    
    CUDA_MK --> CUDA_SO
    ROCM_MK --> ROCM_SO
    THEROCK_MK --> THEROCK_SO
```

Sources: [build.sh:53-90]()

Build invocation at [build.sh:61-84]():

- **CUDA**: `make -j$(nproc)` using default Makefile
- **ROCm**: `make -j$(nproc) -f Makefile.rocm`
- **TheRock**: `make -j$(nproc) -f Makefile.therock HIP_HOME=$(rocm-sdk path --root) CONDA_LIB_HOME=$VIRTUAL_ENV/lib`

TheRock builds require special handling for RCCL headers. Since ROCm doesn't include `nccl.h` by default, the build process generates it from RCCL at [build.sh:43-51]():

```bash
build_rccl_nccl_h() {
  if [[ ! -f "thirdparty/rccl/build/release/include/nccl.h" ]]; then
    cd thirdparty/rccl
    CXX=/opt/rocm/bin/hipcc cmake -B build/release -S . -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF >/dev/null 2>&1 || true
    cd ../..
  fi
}
```

Sources: [build.sh:43-90]()

---

## Dependency Management

### PyTorch Integration

**PyTorch ABI Compatibility Detection**

```mermaid
graph LR
    subgraph "Python Environment Query"
        TORCH_ROOT["torch.__file__.parent"]
        TORCH_ABI["torch._C._GLIBCXX_USE_CXX11_ABI"]
    end
    
    subgraph "Compilation Flags"
        ABI_FLAG["-D_GLIBCXX_USE_CXX11_ABI=X"]
        INCLUDE["torch/include/<br/>torch/csrc/api/include/"]
        LIBDIR["torch/lib/"]
    end
    
    subgraph "Linking"
        RPATH["-Wl,-rpath,torch/lib"]
        LIBS["-ltorch_python -ltorch<br/>-ltorch_cpu -ltorch_cuda"]
    end
    
    TORCH_ROOT --> INCLUDE
    TORCH_ROOT --> LIBDIR
    TORCH_ABI --> ABI_FLAG
    
    ABI_FLAG --> COMPILATION
    INCLUDE --> COMPILATION
    LIBDIR --> RPATH
    LIBDIR --> LIBS
    
    RPATH --> LINKING
    LIBS --> LINKING
```

Sources: [ep/Makefile:38-96]()

The EP Makefile queries PyTorch paths at [ep/Makefile:38-43]():

```makefile
TORCH_ROOT        := $(shell $(PYTHON) -c "import torch, pathlib; print(pathlib.Path(torch.__file__).parent)")
TORCH_INCLUDE     := $(TORCH_ROOT)/include
TORCH_INCLUDE_API := $(TORCH_ROOT)/include/torch/csrc/api/include
TORCH_LIBDIR      := $(TORCH_ROOT)/lib
TORCH_ABI          := $(shell $(PYTHON) -c "import torch; print(int(torch._C._GLIBCXX_USE_CXX11_ABI))")
TORCH_INCS := -I$(TORCH_INCLUDE) -I$(TORCH_INCLUDE_API)
```

Linking configuration at [ep/Makefile:89-96]():

```makefile
$(EP_EXT): $(OBJ_CPP) $(OBJ_CU) $(OBJ_BIND)
	$(CXX) $(CXXFLAGS) -shared -fPIC \
	    -D_GLIBCXX_USE_CXX11_ABI=$(TORCH_ABI) \
	    $(INCLUDES) $(PYBIND11_INCLUDES) $^ \
	    -L$(TORCH_LIBDIR) -Wl,-rpath,$(TORCH_LIBDIR) \
	    -L$(CUDA_PATH)/lib64 -Wl,-rpath,$(CUDA_PATH)/lib64 \
	    -ltorch_python -ltorch -ltorch_cpu -ltorch_cuda -lc10 -lc10_cuda \
	    -lcuda -lcudart $(LDFLAGS) -o $@
```

Sources: [ep/Makefile:38-96]()

### Platform-Specific Python Dependencies

**Docker Image Python Environment Setup**

| Platform | Base Python | PyTorch Installation | Additional Dependencies |
|----------|-------------|---------------------|-------------------------|
| CUDA | Deadsnakes PPA (parameterized version) | `torch --index-url https://download.pytorch.org/whl/cu128` | pybind11, build, auditwheel |
| ROCm | Deadsnakes PPA | `torch --index-url https://download.pytorch.org/whl/nightly/rocm7.0` | hipblas, hipsparse, rocthrust, hipblaslt, hipsolver |
| TheRock | PyPA manylinux (all versions pre-installed) | Bundled via ROCm SDK | `rocm[libraries,devel]` from TheRock index |
| GH200 | Deadsnakes PPA | `torch==2.6.0+cu126 --index-url https://download.pytorch.org/whl/cu126` | Same as CUDA |
| EFA | Deadsnakes PPA | `torch --index-url https://download.pytorch.org/whl/cu128` | libefa, EFA installer |

Sources: [docker/Dockerfile.cuda:38-42](), [docker/Dockerfile.rocm:42-43](), [docker/Dockerfile.therock:11-12](), [docker/Dockerfile.gh:38-39](), [docker/Dockerfile.efa:64-66]()

**TheRock-Specific Python Packaging**

TheRock uses Python-packaged ROCm, requiring special dependency handling. The build process at [build.sh:323-384]() creates a virtual environment:

```bash
# Setup requested Python (PyPA images have all versions pre-installed)
PY_V=$(echo ${PY_VER} | tr -d .)
export PATH=/opt/python/cp${PY_V}-cp${PY_V}/bin:$PATH

# Python environment with ROCm from TheRock
python3 -m venv /tmp/venv && . /tmp/venv/bin/activate
pip3 install --no-cache-dir --upgrade pip
pip3 install --no-cache-dir build auditwheel pybind11
pip3 install --no-cache-dir rocm[libraries,devel] --index-url ${ROCM_IDX_URL}
```

TheRock packages also inject ROCm initialization code at [build.sh:358-376]():

```bash
echo "
def initialize():
  import rocm_sdk
  rocm_sdk.initialize_process(preload_shortnames=[
    \"amd_comgr\",
    \"amdhip64\",
    \"roctx64\",
    \"hiprtc\",
    \"hipblas\",
    \"hipfft\",
    \"hiprand\",
    \"hipsparse\",
    \"hipsolver\",
    \"rccl\",
    \"hipblaslt\",
    \"miopen\",
  ],
  check_version=\"$(rocm-sdk version)\")
" > uccl/_rocm_init.py
```

This initialization code is invoked at runtime in [uccl/__init__.py:4-10]():

```python
try:
    from . import _rocm_init
except ImportError:
    pass
else:
    _rocm_init.initialize()
    del _rocm_init
```

TheRock wheels also have modified dependencies in `setup.py`. The build temporarily modifies [setup.py:44-46]() at [build.sh:379-381]():

```bash
BACKUP_FN=$(mktemp -p . -t setup.py.XXXXXX)
cp ./setup.py ${BACKUP_FN}
sed -i "s/\"rocm\": \[\],/\"rocm\": \[\"rocm\[libraries\]==$(rocm-sdk version)\"\, \"torch\", \"numpy\"],/;" setup.py
```

Sources: [build.sh:323-391](), [uccl/__init__.py:4-10](), [setup.py:44-46]()

### Dependency Exclusion in Wheel Packaging

The `auditwheel` step at [build.sh:393-400]() bundles dependencies while excluding large libraries:

```bash
auditwheel repair dist/uccl-*.whl \
  --exclude "libtorch*.so" \
  --exclude "libc10*.so" \
  --exclude "libibverbs.so.1" \
  --exclude "libcudart.so.12" \
  --exclude "libamdhip64.so.*" \
  --exclude "libcuda.so.1" \
  -w /io/${WHEEL_DIR}
```

**Exclusion Rationale:**

| Excluded Library | Reason |
|------------------|--------|
| `libtorch*.so`, `libc10*.so` | PyTorch runtime (~2GB), user must install PyTorch separately |
| `libibverbs.so.1` | System-provided RDMA library, must match host kernel |
| `libcudart.so.12`, `libcuda.so.1` | CUDA runtime, provided by host CUDA installation |
| `libamdhip64.so.*` | ROCm runtime, provided by host ROCm installation or TheRock |

This ensures the wheel remains portable (<100MB) and doesn't conflict with user-installed GPU frameworks.

Sources: [build.sh:393-400]()

---

## Build Type-Specific Configuration

### Component Build Functions

Each component (ccl_rdma, ccl_efa, p2p, ep) has a dedicated build function that handles platform-specific logic:

```mermaid
graph TB
    subgraph "Build Type Dispatch"
        BUILD_TYPE["BUILD_TYPE parameter"]
        
        CCL_RDMA["build_ccl_rdma()"]
        CCL_EFA["build_ccl_efa()"]
        P2P["build_p2p()"]
        EP["build_ep()"]
        ALL["all (multiple functions)"]
    end
    
    subgraph "Platform Checks"
        RDMA_ARCH["x86_64: both NCCL/RCCL<br/>aarch64: NCCL only"]
        EFA_ARCH["x86_64 + CUDA only<br/>Skip on aarch64/ROCm"]
        P2P_PLATFORM["cuda: Makefile<br/>rocm: Makefile.rocm<br/>therock: Makefile.therock"]
        EP_PLATFORM["cuda/rocm: setup.py build<br/>therock: skip"]
    end
    
    subgraph "Output Artifacts"
        RDMA_SO["lib/libnccl-net-uccl.so<br/>lib/librccl-net-uccl.so"]
        EFA_SO["lib/libnccl-net-efa.so<br/>lib/libnccl-efa.so"]
        P2P_SO["lib/libuccl_p2p.so<br/>p2p.*.so<br/>collective.py"]
        EP_SO["ep.*.so"]
    end
    
    BUILD_TYPE -->|ccl_rdma| CCL_RDMA
    BUILD_TYPE -->|ccl_efa| CCL_EFA
    BUILD_TYPE -->|p2p| P2P
    BUILD_TYPE -->|ep| EP
    BUILD_TYPE -->|all| ALL
    
    CCL_RDMA --> RDMA_ARCH
    CCL_EFA --> EFA_ARCH
    P2P --> P2P_PLATFORM
    EP --> EP_PLATFORM
    
    RDMA_ARCH --> RDMA_SO
    EFA_ARCH --> EFA_SO
    P2P_PLATFORM --> P2P_SO
    EP_PLATFORM --> EP_SO
```

Sources: [build.sh:53-191](), [build.sh:335-351]()

**ccl_rdma Build Function**

At [build.sh:53-90](), the RDMA collective build selects makefiles based on target:

```bash
build_ccl_rdma() {
  local TARGET="$1"
  local ARCH="$2"
  
  if [[ "$TARGET" == cuda* ]]; then
    cd collective/rdma && make clean && make -j$(nproc) && cd ../../
    TARGET_SO=collective/rdma/libnccl-net-uccl.so
  elif [[ "$TARGET" == rocm* ]]; then
    if [[ "$ARCH" == "aarch64" ]]; then
      return  # Skip ROCm on ARM
    fi
    cd collective/rdma && make clean -f Makefile.rocm && make -j$(nproc) -f Makefile.rocm && cd ../../
    TARGET_SO=collective/rdma/librccl-net-uccl.so
  elif [[ "$TARGET" == "therock" ]]; then
    # TheRock requires RCCL header generation first
    cd collective/rdma && make clean -f Makefile.therock && make -j$(nproc) -f Makefile.therock HIP_HOME=$(rocm-sdk path --root) CONDA_LIB_HOME=$VIRTUAL_ENV/lib && cd ../../
    TARGET_SO=collective/rdma/librccl-net-uccl.so
  fi
  
  mkdir -p uccl/lib
  cp ${TARGET_SO} uccl/lib/
}
```

**ccl_efa Build Function**

EFA builds at [build.sh:92-115]() are restricted to x86_64 CUDA platforms:

```bash
build_ccl_efa() {
  local TARGET="$1"
  local ARCH="$2"
  
  if [[ "$ARCH" == "aarch64" || "$TARGET" == rocm* || "$TARGET" == "therock" ]]; then
    echo "Skipping EFA build on Arm64 (no EFA installer) or ROCm (no CUDA)."
    return
  fi
  cd collective/efa && make clean && make -j$(nproc) && cd ../../
  
  # EFA requires a custom NCCL
  cd thirdparty/nccl-sg
  make src.build -j$(nproc) NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90"
  cd ../..
  
  mkdir -p uccl/lib
  cp collective/efa/libnccl-net-efa.so uccl/lib/
  cp thirdparty/nccl-sg/build/lib/libnccl.so uccl/lib/libnccl-efa.so
}
```

**p2p Build Function**

P2P builds at [build.sh:117-148]() support optional TCPX mode:

```bash
build_p2p() {
  local TARGET="$1"
  
  cd p2p
  if [[ "$TARGET" == cuda* ]]; then
    make clean && make -j$(nproc)
  elif [[ "$TARGET" == rocm* ]]; then
    make clean -f Makefile.rocm && make -j$(nproc) -f Makefile.rocm
  elif [[ "$TARGET" == "therock" ]]; then
    make clean -f Makefile.therock && make -j$(nproc) -f Makefile.therock HIP_HOME=$(rocm-sdk path --root) CONDA_LIB_HOME=$VIRTUAL_ENV/lib
  fi
  cd ..
  
  mkdir -p uccl/lib
  if [[ -z "${USE_TCPX:-}" || "$USE_TCPX" != "1" ]]; then
    cp p2p/libuccl_p2p.so uccl/lib/
    cp p2p/librdma_plugin.a uccl/lib/
    cp p2p/p2p.*.so uccl/
    cp p2p/collective.py uccl/
    cp p2p/transfer.py uccl/
    cp p2p/utils.py uccl/
  fi
}
```

**ep Build Function**

EP builds at [build.sh:150-170]() use `setup.py` and skip TheRock:

```bash
build_ep() {
  local TARGET="$1"
  
  if [[ "$TARGET" == "therock" ]]; then
    echo "Skipping GPU-driven build on therock (no GPU-driven support yet)."
  elif [[ "$TARGET" == rocm* || "$TARGET" == cuda* ]]; then
    cd ep
    python3 setup.py build
    cd ..
    mkdir -p uccl/lib
    cp ep/build/**/*.so uccl/
  fi
}
```

Sources: [build.sh:53-170]()

---

## Environment Variables and Runtime Configuration

### Build-Time Environment Variables

The build system accepts multiple environment variables for customization:

```mermaid
graph TB
    subgraph "Input Variables"
        TARGET_VAR["TARGET<br/>cuda/rocm/therock"]
        PY_VER_VAR["PY_VER<br/>Python version"]
        ROCM_IDX["ROCM_IDX_URL<br/>ROCm package index"]
        THEROCK_BASE["THEROCK_BASE_IMAGE<br/>manylinux base"]
        TORCH_ARCH["TORCH_CUDA_ARCH_LIST<br/>GPU architectures"]
        USE_TCPX["USE_TCPX<br/>Enable TCPX backend"]
        MAKE_NORMAL["MAKE_NORMAL_MODE<br/>EP kernel mode"]
    end
    
    subgraph "Docker Build Args"
        BASE_IMAGE["BASE_IMAGE<br/>Docker base"]
        PY_VER_ARG["PY_VER<br/>Docker Python"]
    end
    
    subgraph "Container Environment"
        TARGET_ENV["TARGET<br/>Inside container"]
        BUILD_TYPE_ENV["BUILD_TYPE<br/>Component selection"]
        TORCH_ARCH_ENV["TORCH_CUDA_ARCH_LIST<br/>GPU arch list"]
    end
    
    TARGET_VAR --> BASE_IMAGE
    PY_VER_VAR --> PY_VER_ARG
    ROCM_IDX --> CONTAINER
    THEROCK_BASE --> BASE_IMAGE
    
    BASE_IMAGE --> DOCKER_BUILD
    PY_VER_ARG --> DOCKER_BUILD
    
    TARGET_VAR --> TARGET_ENV
    TORCH_ARCH --> TORCH_ARCH_ENV
    
    TARGET_ENV --> CONTAINER
    BUILD_TYPE_ENV --> CONTAINER
    TORCH_ARCH_ENV --> CONTAINER
    
    DOCKER_BUILD["docker build"]
    CONTAINER["docker run<br/>build execution"]
```

Sources: [build.sh:295-311]()

**Environment Variable Reference**

| Variable | Default | Purpose | Used By |
|----------|---------|---------|---------|
| `TARGET` | `cuda` | Platform target (cuda/rocm/therock/cuda13/rocm6) | [build.sh:15]() |
| `BUILD_TYPE` | `all` | Component selection (all/ccl_rdma/ccl_efa/p2p/ep) | [build.sh:16]() |
| `PY_VER` | Host Python version | Python version for build | [build.sh:17]() |
| `ROCM_IDX_URL` | `https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu` | TheRock ROCm package index | [build.sh:20]() |
| `THEROCK_BASE_IMAGE` | `quay.io/pypa/manylinux_2_28_x86_64@sha256:d632...` | manylinux base for TheRock | [build.sh:22]() |
| `TORCH_CUDA_ARCH_LIST` | Auto-detected | GPU architectures for PyTorch extensions | [build.sh:293]() |
| `USE_TCPX` | `0` | Enable TCPX backend (experimental) | [build.sh:307]() |
| `USE_EFA` | `0` | Enable EFA support | [build.sh:308]() |
| `MAKE_NORMAL_MODE` | unset | Build normal-mode EP kernels instead of low-latency | [build.sh:309]() |

Sources: [build.sh:15-22](), [build.sh:293](), [build.sh:307-309]()

### Runtime Library Path Configuration

The `setup.py` package data at [setup.py:27-36]() ensures platform-specific shared libraries are included:

```python
package_data={
    "uccl": [
        "lib/*.so",      # NCCL/RCCL plugins, libuccl_p2p.so
        "p2p*.so",       # P2P Python bindings
        "ep*.so",        # EP Python bindings
        "lib/*.a",       # librdma_plugin.a
        "collective.py", # P2P high-level API
        "transfer.py",   # P2P transfer utilities
        "utils.py",      # P2P utilities
    ],
}
```

After installation, users must set `LIBRARY_PATH` for linking against UCCL libraries, as shown in [build_and_install.sh:28-38]():

```bash
UCCL_INSTALL_PATH=$(pip show uccl 2>/dev/null | grep "^Location:" | cut -d' ' -f2 || echo "")
if [[ -n "$UCCL_INSTALL_PATH" && -d "$UCCL_INSTALL_PATH" ]]; then
  UCCL_PACKAGE_PATH="$UCCL_INSTALL_PATH/uccl"
  if [[ -d "$UCCL_PACKAGE_PATH" ]]; then
    echo "Set LIBRARY_PATH: export LIBRARY_PATH=\"$UCCL_PACKAGE_PATH/lib:\$LIBRARY_PATH\""
  fi
fi
```

Sources: [setup.py:27-36](), [build_and_install.sh:28-38]()

---

## Cross-Compilation Matrix

The following matrix shows supported build configurations:

| Host Platform | Target: rdma-cuda | rdma-rocm | rdma-arm | p2p-cuda | p2p-rocm | p2p-arm | efa |
|---------------|-------------------|-----------|----------|----------|----------|---------|-----|
| **x86_64 + CUDA** | ✓ | ✓ (requires ROCm Docker) | ✗ | ✓ | ✓ (requires ROCm Docker) | ✗ | ✓ |
| **x86_64 + ROCm** | ✓ (requires CUDA Docker) | ✓ | ✗ | ✓ (requires CUDA Docker) | ✓ | ✗ | ✗ |
| **aarch64 + CUDA (GH200)** | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| **AWS p4d/p4de** | ✓ | ✓ (requires ROCm Docker) | ✗ | ✓ | ✗ | ✗ | ✓ |

**Notes:**
- ARM hosts cannot cross-compile ROCm because `qemu-user-static` cannot emulate ROCm/HIP
- EFA builds require x86_64 hosts with EFA installer support
- Cross-GPU compilation (CUDA on ROCm host, ROCm on CUDA host) works via Docker images containing both toolchains

Sources: [README.md:177-186]()

---

## Platform-Specific Build Examples

### Building for CUDA on x86_64

```bash
# Default CUDA 12.x build
./build.sh cuda all 3.10

# CUDA 13.x build with specific Python version
./build.sh cuda13 all 3.11

# Build only EP component with auto-detected GPU architecture
./build.sh cuda ep
# Alternatively, specify architecture manually:
TORCH_CUDA_ARCH_LIST="9.0" ./build.sh cuda ep

# Build with EFA support (on EFA-enabled instance)
./build.sh cuda all 3.10  # Auto-detects EFA, uses Dockerfile.efa
```

Sources: [build.sh:1-13](), [README.md:92-98]()

### Building for ROCm on x86_64

```bash
# Default ROCm 7.x build
./build.sh rocm all 3.10

# ROCm 6.4.3 build
./build.sh rocm6 all 3.10

# Build only P2P and EP components
./build.sh rocm p2p 3.10
./build.sh rocm ep 3.10
```

Sources: [build.sh:1-13]()

### Building for TheRock (Python-packaged ROCm)

```bash
# TheRock build with custom ROCm index
./build.sh therock all 3.10 https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu

# Installation requires extra-index-url for ROCm dependencies
pip install --extra-index-url https://rocm.prereleases.amd.com/whl/gfx94X-dcgpu \
  wheelhouse-therock/uccl-*.whl[rocm]
```

Sources: [build.sh:1-13](), [README.md:100](), [build_and_install.sh:20-26]()

### Building for Grace Hopper (ARM64 + CUDA)

```bash
# GH200 build (automatically uses Dockerfile.gh on aarch64)
./build.sh cuda all 3.10

# EP build with Grace Hopper optimizations
MAKE_NORMAL_MODE=1 ./build.sh cuda ep 3.10
```

The GH200 Docker image sets `GPU_NAME=GH200` at [docker/Dockerfile.gh:49]() which triggers Grace Hopper-specific code paths.

Sources: [build.sh:196-198](), [docker/Dockerfile.gh:49]()

---

## Troubleshooting Platform Detection

### Stale Docker Image Detection

The build script checks for stale Docker images at [build.sh:232-252]():

```bash
# Detect stale builder image
hash_image=$(docker images -q ${IMAGE_NAME})
if [[ "${hash_image}" != "" ]]; then
  ts_dockerfile=$(date -r ${DOCKERFILE} --iso-8601=seconds)
  ts_image=$(docker inspect -f '{{ .Created }}' ${IMAGE_NAME})
  
  if [[ "${ts_dockerfile}" > "${ts_image}" ]]; then
      echo "WARNING: builder image '${IMAGE_NAME}' is older than its source (${DOCKERFILE})" >&2
      echo "Please consider removing it, pruning the builder cache, and retrying the build to regenerate it." >&2
      echo "  $ docker image rm '${IMAGE_NAME}'" >&2
      echo "  $ docker buildx prune -f" >&2
  fi
fi
```

This prevents builds from using outdated images when Dockerfiles are updated.

Sources: [build.sh:232-252]()

### GPU Architecture Detection Failures

If `nvidia-smi` or `amd-smi` is unavailable during build, GPU architecture detection fails silently. Users can manually specify architecture:

```bash
# For CUDA: Specify compute capability without decimal point
TORCH_CUDA_ARCH_LIST="90" ./build.sh cuda ep  # H100/H200
TORCH_CUDA_ARCH_LIST="100" ./build.sh cuda ep # B200

# For ROCm: Specify gfx architecture
TORCH_CUDA_ARCH_LIST="gfx942" ./build.sh rocm ep  # MI300X
```

Sources: [build.sh:273-293]()

### EFA Detection Issues

If EFA NICs are present but not detected:

1. Check `/sys/class/infiniband/` exists and contains devices with "rdmap" in name
2. Verify EFA installer is present at `/opt/amazon/efa`
3. For p5/p5e/p5en instances, use AWS-provided NCCL plugin instead (see [README.md:158]())

Sources: [build.sh:23](), [uccl/__init__.py:12-20](), [README.md:158]()

---

# Page: Development Environment

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/clang-format-check.yml](.github/workflows/clang-format-check.yml)
- [.gitignore](.gitignore)
- [docker/Dockerfile.cuda](docker/Dockerfile.cuda)
- [docker/Dockerfile.efa](docker/Dockerfile.efa)
- [docker/Dockerfile.gh](docker/Dockerfile.gh)
- [docker/Dockerfile.rocm](docker/Dockerfile.rocm)
- [ep/install_deps.sh](ep/install_deps.sh)
- [format.sh](format.sh)
- [pyproject.toml](pyproject.toml)
- [scripts/node_ips/tpu_2.txt](scripts/node_ips/tpu_2.txt)
- [scripts/setup_all.py](scripts/setup_all.py)
- [scripts/setup_nic.sh](scripts/setup_nic.sh)

</details>



This page covers the developer toolchain for the UCCL codebase: code formatting conventions, CI/CD workflows, Python build system metadata, and the artifact exclusion policy. For information on building the project and Docker environments, see [Build Scripts and Docker Environments](#6.1). For platform-specific Makefile differences, see [Platform-Specific Configuration](#6.2).

---

## Code Formatting

UCCL enforces consistent formatting for both C++ and Python source files. The entry point for local formatting is `format.sh`.

### C++ Formatting — clang-format

`format.sh` uses **clang-format version 14** to format all C++ source files. The script enforces a strict version check and will exit with an error if a different version is found.

[format.sh:13-38]()

| Property | Value |
|---|---|
| Required tool | `clang-format-14` |
| Fallback detection | `clang-format-14` → `clang-format` (via `$CLANG_FORMAT`) |
| Install via | `apt install clang-format-14` or `pip install clang-format==14` |

**Directories formatted:**

[format.sh:8]()

| Directory | Notes |
|---|---|
| `collective/` | Excluding `collective/afxdp/lib` |
| `ep/` | EP subsystem |
| `p2p/` | P2P engine |
| `include/` | Shared headers |
| `experimental/` | UKernel and experimental code |

**File extensions covered:** `.cpp`, `.cxx`, `.cc`, `.h`, `.hpp`, `.cu`, `.cuh`

### Python Formatting — black

After formatting C++, `format.sh` runs `black` on Python source directories.

[format.sh:69-87]()

| Property | Value |
|---|---|
| Required tool | `black` |
| Python directories | `p2p/`, `ep/` |
| Excluded subdirs | `thirdparty`, `docs`, `build` |

### Formatting Workflow Diagram

**Diagram: format.sh execution flow**

```mermaid
flowchart TD
    A["format.sh"] --> B{"Check clang-format\nversion == 14"}
    B -->|"fail"| Z["exit 1"]
    B -->|"pass"| C["find C++ files\nin collective/ ep/ p2p/ include/ experimental/"]
    C --> D["Exclude collective/afxdp/lib"]
    D --> E["clang-format -i FILE\nfor each .cpp/.cc/.h/.cu/.cuh"]
    E --> F{"black installed?"}
    F -->|"no"| Z2["exit 1"]
    F -->|"yes"| G["black p2p/ ep/\n--exclude thirdparty|docs|build"]
    G --> H["Formatting complete"]
```

Sources: [format.sh:1-88]()

---

## GitHub Actions CI/CD

The repository uses three GitHub Actions workflows stored under `.github/workflows/`.

### Workflow Overview

**Diagram: CI/CD pipeline structure**

```mermaid
flowchart TD
    push["push / PR to main"] --> fmt["clang-format-check.yml"]
    push --> build["uccl-build-test.yml"]
    push --> remote["remote-uccl-build.yml"]

    fmt --> job_cpp["job: clang-format-check\nubuntu-latest\nclang-format-14 --dry-run --Werror"]
    fmt --> job_py["job: python-format-check\nubuntu-latest\nblack --check"]

    build --> job_build["Standard CI build\ncompile + unit tests"]
    remote --> job_remote["Remote GPU host test\n(requires GPU runner)"]
```

Sources: [.github/workflows/clang-format-check.yml:1-90]()

### `clang-format-check.yml`

Triggered on push and pull requests targeting `main`. Contains two independent jobs:

**`clang-format-check` job:**
- Runner: `ubuntu-latest`
- Installs `clang-format-14` via `apt`
- Runs `clang-format --dry-run --Werror` across the same directories and extensions that `format.sh` covers
- Fails the workflow if any file is not correctly formatted

**`python-format-check` job:**
- Runner: `ubuntu-latest`
- Python version: `3.10`
- Installs `black` via pip
- Runs `black --check` on `p2p/` and `ep/` with the same exclusion pattern as `format.sh`

[.github/workflows/clang-format-check.yml:1-90]()

### `uccl-build-test.yml` and `remote-uccl-build.yml`

These workflows handle compilation and test execution. `uccl-build-test.yml` runs the standard build and test suite on GitHub-hosted runners. `remote-uccl-build.yml` targets a remote GPU host for tests that require physical hardware. For details on what each test job validates, see [Test Suites and CI](#8.2).

---

## Python Build System

The root `pyproject.toml` defines the build system metadata for the `uccl` Python package.

[pyproject.toml:1-4]()

```toml
[build-system]
requires = ["setuptools>=42", "wheel", "pybind11>=2.6.0", "nanobind>=2.0.0"]
build-backend = "setuptools.build_meta"
```

| Dependency | Minimum Version | Purpose |
|---|---|---|
| `setuptools` | >=42 | Core package build machinery |
| `wheel` | latest | Binary wheel packaging |
| `pybind11` | >=2.6.0 | C++/Python bindings (P2P engine, CCL) |
| `nanobind` | >=2.0.0 | High-performance C++/Python bindings |

Both `pybind11` and `nanobind` are runtime build requirements because the package compiles C++ extension modules during `pip install`. The `ep/install_deps.sh` script also installs these directly via pip for developers setting up outside of Docker:

[ep/install_deps.sh:21-22]()

```bash
pip install pybind11 nanobind --upgrade
pip install black
```

---

## Docker Images for Development

Four Docker images provide reproducible build environments. All are located in `docker/`.

**Diagram: Docker image relationships and key differences**

```mermaid
flowchart TD
    cuda_base["nvidia/cuda:12.8.0-devel-ubuntu22.04"] --> Dockerfile_cuda["docker/Dockerfile.cuda"]
    cuda_base --> Dockerfile_gh["docker/Dockerfile.gh"]
    cuda_base --> Dockerfile_efa["docker/Dockerfile.efa"]
    rocm_base["rocm/dev-ubuntu-22.04"] --> Dockerfile_rocm["docker/Dockerfile.rocm"]

    Dockerfile_cuda --> cuda_pkg["torch (cu128)\npybind11, nanobind\nauditwheel"]
    Dockerfile_gh --> gh_pkg["torch (cu128)\npybind11, nanobind\nGPU_NAME=GH200"]
    Dockerfile_efa --> efa_pkg["torch (cu128)\npybind11, nanobind\naws-efa-installer\nlibfabric"]
    Dockerfile_rocm --> rocm_pkg["torch (nightly/rocm7.1)\npybind11, nanobind\nhipsolver hipblas hipblaslt\nlibhiredis"]
```

| Dockerfile | Base Image | Target Use |
|---|---|---|
| `docker/Dockerfile.cuda` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | General CUDA builds |
| `docker/Dockerfile.gh` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | GitHub Actions + GH200 GPU runner |
| `docker/Dockerfile.efa` | `nvidia/cuda:12.8.0-devel-ubuntu22.04` | AWS EFA builds (includes EFA installer) |
| `docker/Dockerfile.rocm` | `rocm/dev-ubuntu-22.04` | AMD ROCm builds |

All four images:
- Use Python 3.13 (configurable via `ARG PY_VER`)
- Install `pybind11`, `nanobind`, `build`, `auditwheel` for wheel packaging
- Set `python3` and `python3-config` symlinks to the target version

The EFA image additionally runs the AWS EFA installer version `1.42.0` (configurable via `ARG EFA_VER`) in `--skip-kmod` mode and sets `LD_LIBRARY_PATH=/opt/amazon/efa/lib64`.

[docker/Dockerfile.cuda:1-51](), [docker/Dockerfile.gh:1-51](), [docker/Dockerfile.efa:1-75](), [docker/Dockerfile.rocm:1-54]()

---

## Artifact Exclusion Policy (.gitignore)

The `.gitignore` file prevents compiled and generated artifacts from being committed. The exclusions fall into distinct categories:

[.gitignore:1-102]()

| Category | Patterns | Notes |
|---|---|---|
| Object files | `*.o`, `*.ko`, `*.obj`, `*.elf`, `*.s`, `*.ll` | C/C++ and GPU compiler outputs |
| Static libraries | `*.lib`, `*.a`, `*.la`, `*.lo` | All archive formats |
| Shared libraries | `*.so`, `*.so.*`, `*.dylib`, `*.dll` | Built extension modules |
| Executables | `*.exe`, `*.out`, `*.app`, `*.x86_64` | Compiled test binaries |
| Kernel modules | `*.mod*`, `*.cmd`, `.tmp_versions/`, `modules.order`, `Module.symvers` | AF_XDP kernel build artifacts |
| XDP userspace | `xdp-loader`, `xdp_loader`, `af_xdp_user`, etc. | AF_XDP test programs |
| Test binaries | `pcie_test`, `transport_test` | Named test executables |
| Python cache | `__pycache__/`, `*.cache` | Bytecode caches |
| Python packaging | `uccl.egg-info/`, `dist/`, `wheelhouse-*/`, `build/` | Wheel and sdist output |
| Logs | `ep/*.log`, `*.log` | All log files |
| EP deep_ep | `ep/deep_ep_wrapper/deep_ep.egg-info/` | DeepEP wrapper egg info |
| Result data | `*result.jsonl`, `*.json` | Benchmark output files |
| Images | `*.png`, `ep/figs` | Generated figures |
| IDE | `.vscode/settings.json`, `.vscode/c_cpp_properties.json`, `.vscode/launch.json` | Per-user IDE configs |

The `nodes.txt` file is excluded to prevent accidental commit of node IP address inventory. Node IP files used by scripts are stored under `scripts/node_ips/` and are committed selectively (e.g. `scripts/node_ips/tpu_2.txt` is tracked).

---

## Developer Setup Summary

**Diagram: local developer setup steps (code entities)**

```mermaid
flowchart LR
    A["Clone repo"] --> B["Install system deps\nep/install_deps.sh\nor Docker image"]
    B --> C["pip install pybind11 nanobind black\nclang-format-14"]
    C --> D["Build subsystem\nbuild.sh or ep/Makefile"]
    D --> E["Run format.sh\nbefore committing"]
    E --> F["Push / PR to main"]
    F --> G["clang-format-check.yml\nuccl-build-test.yml\nremote-uccl-build.yml"]
```

Sources: [format.sh:1-88](), [ep/install_deps.sh:1-84](), [pyproject.toml:1-4](), [.github/workflows/clang-format-check.yml:1-90]()

---

# Page: Integration and Usage

# Integration and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This page covers the patterns and entry points for integrating UCCL into real workloads. It focuses on what a user or application developer needs to wire up each subsystem. For details on internals, see: collective subsystem internals in [2](#2), P2P engine architecture in [3](#3), EP subsystem in [4](#4), and build system in [6](#6).

---

## Integration Patterns at a Glance

UCCL exposes three distinct integration surfaces, each targeting a different workload type:

| Pattern | Surface | Subsystem | Typical Use Case |
|---|---|---|---|
| NCCL/RCCL drop-in | `NCCL_NET_PLUGIN` env var | UCCL-collective | Existing PyTorch / DDP / FSDP / Megatron training jobs |
| Python P2P API | `uccl.p2p`, `uccl.collective` | UCCL-P2P | KV cache transfer, RL weight sync, custom point-to-point |
| Expert-parallel API | `uccl.ep` | UCCL-EP | MoE training and inference (DeepEP drop-in) |

**Integration flow:**

```mermaid
flowchart TD
    A["Application"] --> B{"Integration point?"}
    B -- "Existing NCCL app" --> C["Set NCCL_NET_PLUGIN\n+ optional LD_PRELOAD"]
    B -- "Custom P2P transfers\n(KV cache, weights)" --> D["import uccl.p2p\nor uccl.collective"]
    B -- "MoE / Expert-parallel" --> E["import uccl.ep\n(Buffer API)"]
    C --> F["libnccl-net-uccl.so\nor libnccl-net-efa.so"]
    D --> G["p2p.Endpoint\nCollectiveContext"]
    E --> H["ep.Buffer\ninitialize_uccl()"]
```

Sources: [README.md:90-118](), [uccl/__init__.py:1-53]()

---

## NCCL / RCCL Plugin Integration

The simplest integration path: point NCCL or RCCL to `libnccl-net-uccl.so` (or its EFA/RCCL variants) without changing application code.

### How the plugin is located

The `uccl` Python package exposes four helper functions in [uccl/__init__.py:32-53]() that return absolute paths to the installed `.so` files:

| Function | Returns path to | Use when |
|---|---|---|
| `nccl_plugin_path()` | `libnccl-net-uccl.so` | IB/RoCE, NVIDIA GPUs |
| `rccl_plugin_path()` | `librccl-net-uccl.so` | IB/RoCE, AMD GPUs |
| `efa_plugin_path()` | `libnccl-net-efa.so` | AWS EFA (p4d/p4de only) |
| `efa_nccl_path()` | `libnccl-efa.so` | AWS EFA, custom NCCL build |

All four functions resolve paths relative to the installed package directory ([uccl/__init__.py:34-53]()).

### Activating the plugin

Set environment variables before launching the Python process:

```bash
# IB/RoCE on NVIDIA (x86 or GH200 ARM)
export NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.nccl_plugin_path())")

# IB/RoCE on AMD
export NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.rccl_plugin_path())")

# AWS EFA (p4d / p4de only)
export LD_PRELOAD=$(python -c "import uccl; print(uccl.efa_nccl_path())")
export NCCL_NET_PLUGIN=$(python -c "import uccl; print(uccl.efa_plugin_path())")
```

No application code changes are required after these variables are set. PyTorch `DistributedDataParallel`, FSDP, Megatron-LM, DeepSpeed, and vLLM all pick up `NCCL_NET_PLUGIN` transparently.

### EFA-host detection and conditional import

When the `uccl` package is imported, [uccl/__init__.py:12-27]() runs `has_efa()` to check for EFA devices under `/sys/class/infiniband/`. On EFA hosts, the `p2p` and `collective` Python submodules are **not** auto-imported, because EFA preloads manage NIC access differently. On non-EFA hosts, both are imported if available.

```mermaid
flowchart LR
    A["import uccl"] --> B["has_efa()\ncheck /sys/class/infiniband/\nfor rdmap* entries"]
    B -- "EFA found" --> C["is_efa = True\nskip p2p + collective import"]
    B -- "no EFA" --> D["is_efa = False\nimport p2p\nimport collective"]
```

Sources: [uccl/__init__.py:12-27](), [collective/efa/README.md:74-95](), [collective/rdma/README.md:160-180]()

### Collective-subsystem environment variables

These variables tune the UCCL-collective transport and apply whenever the NCCL plugin is loaded:

| Variable | Default | Description |
|---|---|---|
| `UCCL_IB_HCA` | (auto) | IB device name(s) to use |
| `UCCL_SOCKET_IFNAME` | (auto) | Control NIC for bootstrapping |
| `UCCL_PIN_TO_NUMA` | `1` | Pin threads to NUMA node |
| `UCCL_RCMODE` | `1` (Broadcom), `0` (others) | Use RC for data transfer |
| `UCCL_NUM_ENGINES` | `4` (NVIDIA), `1` (AMD) | Engines per device |
| `UCCL_PORT_ENTROPY` | `32` (NVIDIA), `256` (AMD) | Paths/QPs per engine |
| `UCCL_CHUNK_SIZE_KB` | `64` (NVIDIA), `128` (AMD) | Max WQE chunk size |
| `NCCL_NET_PLUGIN` | — | Path to plugin `.so` |

Sources: [collective/rdma/README.md:160-180](), [collective/efa/README.md:74-95]()

---

## PyTorch Integration Patterns

### P2P via `uccl.p2p.Endpoint`

`uccl.p2p` is a nanobind extension built from [p2p/engine_api.cc]() and exposes the `Endpoint` class. The typical two-node pattern:

**Endpoint-to-endpoint (NIXL-style transfer API):**

```mermaid
sequenceDiagram
    participant "Rank 0 (sender)" as S
    participant "Rank 1 (receiver)" as R
    S->>S: "ep = p2p.Endpoint(gpu_idx, num_cpus)"
    R->>R: "ep = p2p.Endpoint(gpu_idx, num_cpus)"
    S->>S: "ep.start_passive_accept()"
    R->>R: "ep.start_passive_accept()"
    S->>S: "descs = ep.register_memory(tensor_list)"
    S->>R: "send get_serialized_descs(descs) via dist"
    R->>R: "remote_descs = ep.deserialize_descs(bytes)"
    R->>R: "ok, conn_id = ep.add_remote_endpoint(metadata)"
    R->>R: "ok, tid = ep.transfer(conn_id, 'write', local_descs, remote_descs)"
    R->>R: "poll ep.poll_async(tid) until done"
```

Key `Endpoint` methods (bound in [p2p/engine_api.cc:169-500+]()):

| Method | Purpose |
|---|---|
| `Endpoint(gpu_idx, num_cpus)` | Construct; allocates send/recv proxy threads |
| `start_passive_accept()` | Background thread listens for incoming connections |
| `register_memory(tensor_list)` | Registers GPU tensors for RDMA; returns `list[XferDesc]` |
| `get_serialized_descs(desc_list)` | Serialize `XferDesc` list to `bytes` for out-of-band exchange |
| `deserialize_descs(bytes)` | Reconstruct `XferDesc` list from `bytes` |
| `add_remote_endpoint(metadata_bytes)` | Establish connection from serialized remote metadata |
| `get_metadata()` | Return local endpoint metadata as `bytes` |
| `transfer(conn_id, op, local_descs, remote_descs)` | Issue async RDMA write or read |
| `poll_async(transfer_id)` | Check completion of a transfer |

**Pattern from benchmark_ray_p2p.py:**  
[p2p/benchmarks/benchmark_ray_p2p.py:262-335]() shows the full initialization sequence: `dist.init_process_group(backend="gloo")`, then construct `Endpoint`, call `start_passive_accept()`, exchange metadata via `dist.send`/`dist.recv`, and then perform `transfer()` + `poll_async()` in a loop.

Sources: [p2p/engine_api.cc:137-500](), [p2p/benchmarks/benchmark_ray_p2p.py:60-217]()

### Collective API via `uccl.collective`

`uccl.collective` (installed as `p2p/collective.py` into the `uccl/` package directory) provides a `CollectiveContext` that wraps `p2p.Endpoint` with collective semantics and PyTorch-compatible interfaces. See [3.4](#3.4) for a full description of `CollectiveContext`.

The typical initialization sequence:
1. Call `torch.distributed.init_process_group()` first.
2. Construct a `CollectiveContext` (it uses `torch.distributed.all_gather` internally for RDMA metadata exchange).
3. Call `register_tensor()` before using a tensor in transfers.
4. Use `send`, `recv`, `isend`, `irecv`, `allgather`, or `batch_isend_irecv` as drop-in replacements for `dist.*`.

Sources: [p2p/benchmarks/benchmark_ray_p2p.py:313-327](), [README.md:105-118]()

---

## Expert-Parallel (EP) Integration

UCCL-EP is a drop-in replacement for [DeepEP](https://github.com/deepseek-ai/DeepEP). It exposes `uccl.ep`, built from the `ep/` directory and installed to the `uccl/` package.

### Import verification

After installation:

```bash
python -c "import torch; import uccl.ep"
```

### Core API: `Buffer` and initialization helpers

```mermaid
flowchart TD
    A["torchrun / user code"] --> B["initialize_uccl(scratch, num_rdma_bytes, rank, num_ranks, group, num_experts)"]
    B --> C["Buffer.__init__\ninit_dist() / init_dist_under_torchrun()"]
    C --> D["UcclProxy / Proxy\nper-NIC proxy threads"]
    D --> E["RDMA QP setup\nsetup_rdma()"]
    A --> F["buffer.low_latency_dispatch(...)"]
    A --> G["buffer.low_latency_combine(...)"]
    F --> H["GPU dispatch ring\nrun_sender() / run_dual() threads"]
    G --> H
    A --> I["destroy_uccl(proxies, workers)"]
```

The dispatch/combine calls accept standard PyTorch tensors and kwargs that mirror the DeepEP interface ([ep/README.md:55-81]()):

```python
# Dispatch
packed_recv_x, packed_recv_count, handle, event, hook = buffer.low_latency_dispatch(
    current_x, topk_idx, num_tokens, num_experts,
    use_fp8=..., async_finish=..., return_recv_hook=...
)

# Combine
combined_x, event, hook = buffer.low_latency_combine(
    simulated_gemm_x, topk_idx, topk_weights, handle,
    async_finish=..., zero_copy=..., return_recv_hook=..., out=...
)
```

### Launching EP benchmarks with `torchrun`

The `ep/bench/run_ep.sh` script ([ep/bench/run_ep.sh:1-30]()) supports four modes:

| Mode flag | Test script | Description |
|---|---|---|
| `ll` | `test_low_latency.py` | Low-latency dispatch/combine (128 tokens) |
| `ht` | `test_internode.py` | High-throughput normal mode (4096 tokens) |
| `ll-pressure` | `test_low_latency.py` | Low-latency with pressure test + hash debug |
| `ht-pressure` | `test_internode.py` | High-throughput with pressure test |

Example multi-node launch:

```bash
torchrun --nnodes=4 --nproc_per_node=8 --node_rank=<rank> \
  --master_addr=<ip> --master_port=12355 \
  bench/test_internode.py --num-tokens=4096 \
  --hidden=7168 --num-topk=8 --num-experts=288
```

### EP environment variables

These must be set before `torchrun` to avoid hangs and configure RDMA behavior:

| Variable | Default | Description |
|---|---|---|
| `UCCL_SOCKET_IFNAME` | (null) | Bootstrap NIC interface name |
| `UCCL_IB_GID_INDEX` | `-1` (auto) | GID index; must match `NCCL_IB_GID_INDEX` |
| `UCCL_IB_MAX_INFLIGHT_BYTES` | `SIZE_MAX` | Max in-flight bytes per GPU/NIC |
| `UCCL_IB_MAX_INFLIGHT_NORMAL` | `8` | Max in-flight writes per GPU/NIC (HT mode) |
| `UCCL_IB_MAX_INFLIGHT_LOW_LATENCY` | `32` | Max in-flight writes per GPU/NIC (LL mode) |
| `UCCL_IB_SL` | `3` (IB), `8` (EFA) | Service level |
| `UCCL_IB_TC` | `104` (IB), `0` (EFA) | Traffic class |

**Broadcom Thor-2:** Set `UCCL_IB_MAX_INFLIGHT_BYTES=1572864 UCCL_IB_MAX_INFLIGHT_NORMAL=1` to avoid CQE error 12.  
**AMD Pollara NIC:** Set `UCCL_IB_MAX_INFLIGHT_BYTES=2097152 UCCL_IB_MAX_INFLIGHT_NORMAL=1`.

Sources: [ep/README.md:119-134](), [ep/bench/run_ep.sh:1-30]()

---

## End-to-End Integration Map

This diagram maps each integration surface to its concrete code entities:

```mermaid
flowchart LR
    subgraph "User Layer"
        U1["NCCL_NET_PLUGIN\nLD_PRELOAD"]
        U2["import uccl.p2p\np2p.Endpoint"]
        U3["import uccl.collective\nCollectiveContext"]
        U4["import uccl.ep\nBuffer\ninitialize_uccl()"]
    end

    subgraph "uccl Python package\nuccl/__init__.py"
        F1["nccl_plugin_path()"]
        F2["rccl_plugin_path()"]
        F3["efa_plugin_path()"]
        F4["efa_nccl_path()"]
        F5["has_efa()"]
    end

    subgraph "Shared libs"
        L1["libnccl-net-uccl.so"]
        L2["librccl-net-uccl.so"]
        L3["libnccl-net-efa.so"]
        L4["libnccl-efa.so"]
        L5["p2p.abi3.so\nengine_api.cc NB_MODULE"]
        L6["ep.abi3.so\nuccl_ep.cc pybind11 module"]
    end

    subgraph "C++ Core"
        C1["collective/rdma\nlibnccl-net-uccl transport"]
        C2["collective/efa\nlibnccl-net-efa transport"]
        C3["p2p/engine.cc\nEndpoint class"]
        C4["p2p/collective.py\nCollectiveContext"]
        C5["ep/src/uccl_ep.cc\nBuffer class"]
    end

    U1 --> F1 & F2 & F3 & F4
    F1 --> L1 --> C1
    F2 --> L2 --> C1
    F3 --> L3 --> C2
    F4 --> L4 --> C2
    F5 --> U2

    U2 --> L5 --> C3
    U3 --> C4 --> C3
    U4 --> L6 --> C5
```

Sources: [uccl/__init__.py:1-53](), [p2p/engine_api.cc:137-200](), [ep/setup.py:329-349](), [shared.sh:99-163]()

---

## Installation Summary

All integration paths require the `uccl` Python package. Install via:

```bash
# Build for CUDA (IB/RoCE + P2P + EP)
bash build.sh cuda all --install

# Build for AMD ROCm
bash build.sh rocm all --install

# Build only EP
bash build.sh cuda ep --install
```

After installation, the package layout under site-packages looks like:

```
uccl/
├── __init__.py          # nccl_plugin_path(), efa_plugin_path(), has_efa(), etc.
├── collective.py        # CollectiveContext (copied from p2p/collective.py)
├── utils.py             # Transfer helpers (copied from p2p/utils.py)
├── p2p.abi3.so          # nanobind extension: p2p.Endpoint
├── ep.abi3.so           # pybind11 extension: ep.Buffer, initialize_uccl
└── lib/
    ├── libnccl-net-uccl.so
    ├── librccl-net-uccl.so
    ├── libnccl-net-efa.so
    ├── libnccl-efa.so
    └── libuccl_p2p.so
```

See [6](#6) for build system details and [1.2](#1.2) for platform-specific prerequisites.

Sources: [build.sh:396-424](), [setup.py:33-63](), [shared.sh:99-163]()

---

# Page: NCCL/RCCL Plugin Integration

# NCCL/RCCL Plugin Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



UCCL provides transparent integration with existing NCCL and RCCL-based applications through the standard NCCL network plugin mechanism. This enables UCCL to serve as a drop-in replacement for NCCL's built-in network transports **without requiring any changes to application code**. Users simply set environment variables to point NCCL/RCCL to UCCL's plugin libraries.

This page documents the plugin architecture, environment variable configuration, and the Python helper functions that simplify plugin path management.

## Transparent Integration via NCCL_NET_PLUGIN

UCCL integrates with NCCL/RCCL through the `NCCL_NET_PLUGIN` environment variable, which directs NCCL to load UCCL's network transport plugin instead of its built-in transports. This mechanism requires **zero application code changes** - existing PyTorch, DeepSpeed, or other NCCL-based applications work immediately with UCCL.

### Plugin Architecture Diagram

```mermaid
graph TB
    subgraph "Application_Layer"
        APP["PyTorch/DeepSpeed<br/>Application Code<br/>(no changes required)"]
    end
    
    subgraph "NCCL_RCCL_Layer"
        NCCL["NCCL/RCCL Library<br/>Collective Operations"]
        ENV["NCCL_NET_PLUGIN<br/>Environment Variable"]
    end
    
    subgraph "UCCL_Plugin_Libraries"
        RDMA_PLUGIN["libnccl-net-uccl.so<br/>(NCCL for RDMA)"]
        RCCL_PLUGIN["librccl-net-uccl.so<br/>(RCCL for RDMA)"]
        EFA_PLUGIN["libnccl-net-efa.so<br/>(AWS EFA)"]
    end
    
    subgraph "UCCL_Transport_Backends"
        RDMA_IMPL["RDMA Backend<br/>collective/rdma/"]
        EFA_IMPL["EFA Backend<br/>collective/efa/"]
        AFXDP_IMPL["AF_XDP Backend<br/>collective/afxdp/"]
    end
    
    APP --> NCCL
    NCCL --> ENV
    ENV --> RDMA_PLUGIN
    ENV --> RCCL_PLUGIN
    ENV --> EFA_PLUGIN
    
    RDMA_PLUGIN --> RDMA_IMPL
    RCCL_PLUGIN --> RDMA_IMPL
    EFA_PLUGIN --> EFA_IMPL
```

**Key Insight**: The application sees only standard NCCL APIs (`ncclAllReduce`, `ncclBcast`, etc.). NCCL dynamically loads UCCL's plugin via `NCCL_NET_PLUGIN`, which intercepts network operations and routes them through UCCL's optimized transport implementations.

Sources: [README.md:103-116](), [uccl/__init__.py:33-54]()

## Plugin Library Structure

UCCL builds multiple plugin libraries during the Docker-based build process. Each library corresponds to a specific transport backend and GPU vendor combination. The build system packages these plugins into the Python wheel for easy distribution.

### Build and Packaging Flow

```mermaid
graph LR
    subgraph "Build_Process"
        BUILD_SH["build.sh"]
        DOCKER["Docker Build<br/>Environment"]
        COMPILE["C++ Compilation<br/>collective/rdma/<br/>collective/efa/"]
    end
    
    subgraph "Plugin_Artifacts"
        NCCL_RDMA["libnccl-net-uccl.so<br/>(NVIDIA + RDMA)"]
        RCCL_RDMA["librccl-net-uccl.so<br/>(AMD + RDMA)"]
        NCCL_EFA["libnccl-net-efa.so<br/>(AWS EFA)"]
        NCCL_EFA_LIB["libnccl-efa.so<br/>(Custom NCCL)"]
    end
    
    subgraph "Python_Package"
        WHEEL["uccl-*.whl<br/>Python Wheel"]
        LIB_DIR["uccl/lib/<br/>.so files"]
        INIT_PY["uccl/__init__.py<br/>Helper Functions"]
    end
    
    BUILD_SH --> DOCKER
    DOCKER --> COMPILE
    COMPILE --> NCCL_RDMA
    COMPILE --> RCCL_RDMA
    COMPILE --> NCCL_EFA
    COMPILE --> NCCL_EFA_LIB
    
    NCCL_RDMA --> LIB_DIR
    RCCL_RDMA --> LIB_DIR
    NCCL_EFA --> LIB_DIR
    NCCL_EFA_LIB --> LIB_DIR
    
    LIB_DIR --> WHEEL
    INIT_PY --> WHEEL
```

### Plugin Libraries by Backend

| Plugin Library | Backend | GPU Support | Build Target | Description |
|----------------|---------|-------------|--------------|-------------|
| `libnccl-net-uccl.so` | RDMA/InfiniBand | NVIDIA | `ccl_rdma` | RDMA transport for NVIDIA GPUs |
| `librccl-net-uccl.so` | RDMA/InfiniBand | AMD | `ccl_rdma` | RDMA transport for AMD GPUs |
| `libnccl-net-efa.so` | AWS EFA | NVIDIA | `ccl_efa` | AWS EFA transport plugin |
| `libnccl-efa.so` | AWS EFA | NVIDIA | `ccl_efa` | Custom NCCL library for EFA |

Sources: [build.sh:53-115](), [setup.py:26-37](), [uccl/__init__.py:33-54]()

## Plugin Path Management with Python API

UCCL provides Python helper functions to automatically locate plugin libraries installed in the package. This eliminates the need to manually specify absolute paths, making integration more portable across different environments.

### Helper Functions

The `uccl` module exposes four main helper functions for plugin path discovery:

```python
import uccl

# For NVIDIA GPUs with RDMA/InfiniBand
nccl_plugin = uccl.nccl_plugin_path()
# Returns: /path/to/site-packages/uccl/lib/libnccl-net-uccl.so

# For AMD GPUs with RDMA/InfiniBand  
rccl_plugin = uccl.rccl_plugin_path()
# Returns: /path/to/site-packages/uccl/lib/librccl-net-uccl.so

# For AWS EFA (plugin)
efa_plugin = uccl.efa_plugin_path()
# Returns: /path/to/site-packages/uccl/lib/libnccl-net-efa.so

# For AWS EFA (custom NCCL library)
efa_nccl = uccl.efa_nccl_path()
# Returns: /path/to/site-packages/uccl/lib/libnccl-efa.so
```

### Implementation Details

These functions construct absolute paths by locating the `uccl` package installation directory and appending the library filename:

```python
# Implementation from uccl/__init__.py
def nccl_plugin_path():
    """Returns absolute path to the NCCL plugin .so file"""
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    return os.path.join(lib_dir, "libnccl-net-uccl.so")
```

Sources: [uccl/__init__.py:33-54](), [README.md:106-113]()

## Environment Variable Configuration

UCCL plugins are loaded and configured through environment variables. The most critical variable is `NCCL_NET_PLUGIN`, which tells NCCL/RCCL to use UCCL's network transport instead of the default.

### Quick Start Examples

#### NCCL over InfiniBand/RoCE (NVIDIA GPUs)

```bash
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`

# Run your PyTorch application
python your_training_script.py
```

#### RCCL over InfiniBand/RoCE (AMD GPUs)

```bash
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.rccl_plugin_path())"`

# Run your PyTorch application
python your_training_script.py
```

#### NCCL over AWS EFA (p4d, p4de instances)

```bash
export LD_PRELOAD=`python -c "import uccl; print(uccl.efa_nccl_path())"`
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.efa_plugin_path())"`

# Run your PyTorch application
python your_training_script.py
```

**Note**: The EFA backend requires both `LD_PRELOAD` (custom NCCL library) and `NCCL_NET_PLUGIN` (EFA transport) to be set.

Sources: [README.md:103-116]()

### Core Environment Variables

| Variable | Purpose | Required For | Example |
|----------|---------|--------------|---------|
| `NCCL_NET_PLUGIN` | Path to UCCL plugin library | All backends | `/path/to/libnccl-net-uccl.so` |
| `LD_PRELOAD` | Custom NCCL library to preload | EFA only | `/path/to/libnccl-efa.so` |

Sources: [README.md:103-116]()

## Integration with Distributed Training Frameworks

### PyTorch Distributed (torchrun)

UCCL works seamlessly with PyTorch's `torchrun` launcher. Simply set the environment variables before launching:

```bash
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`

torchrun --nproc_per_node=8 \
         --nnodes=4 \
         --master_addr=<master_ip> \
         --master_port=<port> \
         your_training_script.py
```

### Multi-Node with Shell Scripts

For multi-node setups, environment variables must be set on all nodes. A common pattern is to use a launcher script:

```bash
#!/bin/bash
# launch.sh

export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`

# Additional NCCL tuning (optional)
export NCCL_SOCKET_IFNAME=eth0
export NCCL_IB_HCA=mlx5_0,mlx5_1

# Launch your application
python your_training_script.py
```

Execute this script on all nodes via your cluster management system (SLURM, Kubernetes, etc.).

Sources: [README.md:103-117]()

## Backend-Specific Configuration

Different UCCL transport backends support additional environment variables for fine-tuning performance. These are **optional** - the default settings work well for most use cases.

### RDMA/InfiniBand Backend

The RDMA backend (both `libnccl-net-uccl.so` and `librccl-net-uccl.so`) automatically detects InfiniBand HCAs and configures optimal settings. Advanced users can override defaults:

| Variable | Description | Default Behavior |
|----------|-------------|------------------|
| `UCCL_IB_HCA` | Comma-separated list of HCA names | Auto-detect all available HCAs |
| `UCCL_SOCKET_IFNAME` | Network interface for control traffic | Auto-detect from IB network |
| `UCCL_NUM_ENGINES` | Number of parallel engines per GPU | Platform-dependent (1-4) |
| `UCCL_CHUNK_SIZE_KB` | Data chunk size in KB | Platform-dependent (64-128) |

**Example**: Override HCA selection for multi-rail configurations:
```bash
export UCCL_IB_HCA=mlx5_0,mlx5_1,mlx5_2,mlx5_3
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.nccl_plugin_path())"`
```

### AWS EFA Backend

The EFA backend requires both the custom NCCL library (`LD_PRELOAD`) and the EFA plugin (`NCCL_NET_PLUGIN`). This is necessary because AWS EFA uses a modified NCCL transport layer.

**Minimal Configuration** (p4d, p4de):
```bash
export LD_PRELOAD=`python -c "import uccl; print(uccl.efa_nccl_path())"`
export NCCL_NET_PLUGIN=`python -c "import uccl; print(uccl.efa_plugin_path())"`
```

**Note**: On newer instances (p5, p5e, p5en, p6), the official AWS OFI NCCL plugin already provides excellent performance. UCCL's EFA backend primarily targets p4d/p4de instances.

Sources: [README.md:103-158]()

## Plugin Loading and Initialization Flow

When NCCL/RCCL starts up, it checks for the `NCCL_NET_PLUGIN` environment variable and dynamically loads the specified plugin library. The plugin must implement the standard NCCL network plugin interface to handle network communication.

### Runtime Loading Sequence

```mermaid
graph TB
    subgraph "Application_Startup"
        APP_INIT["Application Calls<br/>ncclCommInitRank()"]
        ENV_CHECK["NCCL Checks<br/>NCCL_NET_PLUGIN"]
    end
    
    subgraph "Plugin_Loading"
        DLOPEN["dlopen()<br/>Load Plugin Library"]
        SYMBOL_RESOLVE["dlsym()<br/>ncclNetPlugin_v8"]
        VALIDATE["Validate Plugin<br/>Version and Interface"]
    end
    
    subgraph "UCCL_Initialization"
        NET_INIT["ncclNetInit()<br/>Initialize UCCL"]
        NET_DEVICES["ncclNetDevices()<br/>Enumerate NICs"]
        NET_GET_PROPS["ncclNetGetProperties()<br/>Get Device Info"]
    end
    
    subgraph "Communication_Setup"
        NET_LISTEN["ncclNetListen()<br/>Create Endpoints"]
        NET_CONNECT["ncclNetConnect()<br/>Establish Connections"]
        READY["Ready for<br/>ncclNetSend/Recv"]
    end
    
    APP_INIT --> ENV_CHECK
    ENV_CHECK --> DLOPEN
    DLOPEN --> SYMBOL_RESOLVE
    SYMBOL_RESOLVE --> VALIDATE
    
    VALIDATE --> NET_INIT
    NET_INIT --> NET_DEVICES
    NET_DEVICES --> NET_GET_PROPS
    
    NET_GET_PROPS --> NET_LISTEN
    NET_LISTEN --> NET_CONNECT
    NET_CONNECT --> READY
```

### Key Functions in Plugin Interface

The NCCL plugin interface defines a set of function pointers that UCCL must implement:

| Function | Purpose | UCCL Implementation |
|----------|---------|---------------------|
| `ncclNetInit()` | Initialize plugin | Probe hardware, configure transport |
| `ncclNetDevices()` | Return device count | Count available NICs/HCAs |
| `ncclNetGetProperties()` | Get device info | Return NIC speed, PCIe affinity |
| `ncclNetListen()` | Create listen endpoint | Setup RDMA/EFA listening socket |
| `ncclNetConnect()` | Connect to peer | Establish RDMA QP or EFA connection |
| `ncclNetIsend()` | Non-blocking send | Post RDMA send or EFA transmit |
| `ncclNetIrecv()` | Non-blocking receive | Post RDMA recv or EFA receive |
| `ncclNetTest()` | Test completion | Poll completion queues |

Sources: [README.md:25-47](), [uccl/__init__.py:1-54]()

## Protocol Support

UCCL currently supports the NCCL Simple protocol across all transport backends:

| Protocol | RDMA Plugin | EFA Plugin | AF_XDP Plugin | Status |
|----------|-------------|------------|---------------|---------|
| `Simple` | ✓ | ✓ | ✓ | Supported |
| `LL` | - | - | - | In Development |
| `LL128` | - | - | - | In Development |

The Simple protocol is specified via `NCCL_PROTO=Simple` and is required for all UCCL transport backends.

Sources: [doc/dev_efa.md:82](), [efa/run_p5en.sh:111]()

---

# Page: PyTorch Integration Patterns

# PyTorch Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [p2p/Makefile.rocm](p2p/Makefile.rocm)
- [p2p/Makefile.therock](p2p/Makefile.therock)
- [p2p/benchmarks/benchmark_nccl_allgather.py](p2p/benchmarks/benchmark_nccl_allgather.py)
- [p2p/benchmarks/benchmark_ray_p2p.py](p2p/benchmarks/benchmark_ray_p2p.py)
- [p2p/benchmarks/benchmark_uccl_allgather.py](p2p/benchmarks/benchmark_uccl_allgather.py)
- [p2p/benchmarks/benchmark_uccl_alltoall.py](p2p/benchmarks/benchmark_uccl_alltoall.py)
- [p2p/benchmarks/benchmark_uccl_collective.py](p2p/benchmarks/benchmark_uccl_collective.py)
- [p2p/collective.py](p2p/collective.py)
- [p2p/engine_api.cc](p2p/engine_api.cc)
- [p2p/tests/test_util_interval_tree.py](p2p/tests/test_util_interval_tree.py)
- [p2p/utils.py](p2p/utils.py)
- [setup.py](setup.py)
- [shared.sh](shared.sh)
- [uccl/.gitignore](uccl/.gitignore)
- [uccl/__init__.py](uccl/__init__.py)

</details>



This page documents integration patterns for using UCCL with PyTorch applications, covering direct API usage with the P2P engine and expert parallelism (EP) for MoE models. For transparent NCCL plugin integration (requiring no code changes), see [NCCL/RCCL Plugin Integration](#6.1). For performance tuning parameters, see [Configuration and Tuning](#6.3).

---

## Integration Overview

UCCL provides two primary PyTorch integration patterns, each suited for different use cases:

| Pattern | Use Case | API Surface | Requires Code Changes |
|---------|----------|-------------|----------------------|
| **P2P Direct API** | Custom communication patterns, benchmarking, fine-grained control | `uccl.collective` Python module | Yes |
| **EP Integration** | MoE model training/inference with GPU-initiated communication | `uccl.ep` (deep_ep.Buffer) | Yes |
| **NCCL Plugin** (see [6.1](#6.1)) | Drop-in replacement for existing PyTorch code | Environment variables only | No |

Both patterns require `torch.distributed` to be initialized for process coordination, but handle data transfer through UCCL's optimized transport layers.

Sources: [p2p/collective.py:1-854](), [ep/README.md:1-187](), [p2p/benchmarks/benchmark_uccl_collective.py:1-464]()

---

## Pattern 1: P2P Direct API Integration

The P2P Direct API provides a NCCL-like interface through the `CollectiveContext` class for custom communication patterns.

### Initialization Pattern

```mermaid
graph TB
    subgraph "Initialization Sequence"
        A["torch.distributed.init_process_group<br/>(backend='gloo')"]
        B["collective.init_collective<br/>(num_cpus, local_gpu_idx)"]
        C["CollectiveContext.init()"]
        D["Endpoint Creation<br/>p2p.Endpoint"]
        E["Connection Establishment<br/>Full mesh with all peers"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    subgraph "Connection Types"
        F["Local Connection<br/>ep.connect_local(gpu_idx)<br/>Unix Domain Sockets"]
        G["Remote Connection<br/>ep.connect(ip, gpu_idx)<br/>RDMA/EFA"]
    end
    
    E --> F
    E --> G
```

**Basic initialization code pattern:**

```python
import torch
import torch.distributed as dist
from uccl import collective

# Initialize torch.distributed for coordination
dist.init_process_group(backend='gloo')

# Initialize UCCL collective context
collective.init_collective(
    num_cpus=4,                      # CPU threads for RDMA operations
    local_gpu_idx=None,               # Auto-detect from LOCAL_RANK
    use_copy_engine_for_intra=False   # Use NCCL for local, UCCL for remote
)

# Get context for operations
ctx = collective.get_collective()
```

The `CollectiveContext` class automatically:
- Derives local GPU index from `LOCAL_RANK` environment variable or torch.distributed context
- Establishes full mesh connections with all peers using concurrent threads
- Determines which peers are local (same node) vs remote (different nodes) based on IP addresses
- Creates separate send/receive connections for each peer

Sources: [p2p/collective.py:43-179](), [p2p/benchmarks/benchmark_uccl_collective.py:336-410]()

### Memory Registration for RDMA

**All remote (inter-node) communication requires memory registration.** Local (intra-node) communication via IPC does not require registration.

```python
# Create GPU tensor
tensor = torch.randn(1024 * 1024, dtype=torch.float32).cuda()

# Register for RDMA (required for remote peers only)
collective.register_tensor(tensor)

# Use tensor for communication...

# Deregister when done (optional, happens automatically at finalization)
collective.deregister_tensor(tensor)
```

The registration system uses an interval tree to track registered memory regions and avoid duplicate registrations:

```mermaid
graph LR
    subgraph "Memory Registration Process"
        A["tensor.data_ptr()"]
        B["Check ClosedIntervalTree<br/>for existing registration"]
        C["ep.reg(ptr, size)"]
        D["Store mr_id in tree"]
        
        A --> B
        B -->|"Not found"| C
        B -->|"Found"| E["Return cached mr_id"]
        C --> D
    end
```

Sources: [p2p/collective.py:327-380](), [p2p/utils.py:114-207]()

### Synchronous vs Asynchronous Operations

**Synchronous operations (blocking):**

```python
# Send tensor to rank 1
collective.send(tensor, dst=1)

# Receive tensor from rank 0
collective.recv(tensor, src=0)
```

**Asynchronous operations (non-blocking):**

```python
# Initiate async send
send_handle = collective.isend(tensor, dst=1)

# Initiate async receive
recv_handle = collective.irecv(tensor, src=0)

# Do other work...

# Wait for completion
collective.wait(send_handle)
collective.wait(recv_handle)

# Or wait for multiple operations
collective.wait_all([send_handle, recv_handle])
```

The async API returns different handle types depending on connection locality:
- **Remote connections**: Integer handle for UCCL async operation, checked via `ep.poll_async(handle)`
- **Local connections with NCCL**: `dist.Work` object, checked via `work.is_completed()`

Sources: [p2p/collective.py:382-578](), [p2p/benchmarks/benchmark_uccl_collective.py:110-168]()

### Batch Operations for Improved Performance

Batch operations reduce overhead by launching multiple sends/receives concurrently:

```python
# Create operation descriptors
ops = [
    collective.P2POp(collective.isend, send_tensor, peer_rank),
    collective.P2POp(collective.irecv, recv_tensor, peer_rank),
]

# Execute all operations in batch
handles = collective.batch_isend_irecv(ops)

# Wait for all to complete
collective.wait_all(handles)
```

This pattern is used extensively for collective operations like allgather and ring communication patterns.

Sources: [p2p/collective.py:622-697](), [p2p/benchmarks/benchmark_uccl_collective.py:189-228]()

### AllGather Implementation Example

```mermaid
graph TB
    subgraph "AllGather Operation Flow"
        A["Send tensor: shape=(N,)<br/>Recv tensor: shape=(world_size*N,)"]
        B["Copy own data to recv_tensor[rank*N:(rank+1)*N]"]
        C["Build P2POp list:<br/>- Send to all other ranks<br/>- Recv from all other ranks"]
        D["batch_isend_irecv(ops)"]
        E["wait_all(handles)"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    subgraph "Memory Layout"
        F["recv_tensor[0:N] ← rank 0"]
        G["recv_tensor[N:2N] ← rank 1"]
        H["recv_tensor[2N:3N] ← rank 2"]
        I["recv_tensor[...] ← ..."]
    end
    
    E --> F
    E --> G
    E --> H
    E --> I
```

The implementation splits the receive tensor into chunks and uses batch operations:

```python
def iallgather(send_tensor, recv_tensor):
    chunk_numel = send_tensor.numel()
    recv_chunks = [
        recv_tensor.view(-1)[i * chunk_numel : (i + 1) * chunk_numel].view(send_tensor.shape)
        for i in range(world_size)
    ]
    
    # Copy own data
    recv_chunks[rank].copy_(send_tensor)
    
    # Build batch operations
    ops = []
    for peer in range(world_size):
        if peer != rank:
            ops.append(P2POp("send", send_tensor, peer))
    for peer in range(world_size):
        if peer != rank:
            ops.append(P2POp("recv", recv_chunks[peer], peer))
    
    return batch_isend_irecv(ops)
```

Sources: [p2p/collective.py:699-753](), [p2p/benchmarks/benchmark_uccl_allgather.py:110-189]()

---

## Pattern 2: EP Integration for MoE Models

The EP (Expert Parallelism) system provides GPU-initiated communication optimized for MoE workloads, compatible with the DeepEP interface.

### Buffer Initialization and Configuration

```python
import torch.distributed as dist
import deep_ep  # Provided by uccl.ep

# Initialize torch.distributed
rank, world_size, group = init_distributed()

# Calculate required buffer size
num_rdma_bytes = deep_ep.Buffer.get_low_latency_rdma_size_hint(
    num_tokens=128,
    hidden=7168,
    num_ranks=world_size,
    num_experts=288
)

# Create buffer with configuration
buffer = deep_ep.Buffer(
    group,
    num_rdma_bytes=num_rdma_bytes,
    low_latency_mode=True,              # Enable low-latency kernels
    num_qps_per_rank=num_experts // world_size,  # QPs per rank
    allow_nvlink_for_low_latency_mode=True,      # Enable NVLink optimization
    explicitly_destroy=True              # Manual resource cleanup
)
```

The `Buffer` class encapsulates:
- **Proxy system**: C++ proxy managing RDMA queue pairs and resources
- **GPU kernel dispatch**: Launches dispatch/combine kernels with optimal configurations
- **Memory management**: Handles buffer allocation and registration
- **Connection topology**: Manages both RDMA (inter-node) and NVLink (intra-node) paths

Sources: [ep/README.md:1-48](), [thirdparty/DeepEP/tests/test_low_latency.py:163-178]()

### Low-Latency Dispatch/Combine Operations

```mermaid
graph TB
    subgraph "Dispatch Phase"
        A["Input: current_x, topk_idx<br/>Shape: (num_tokens, hidden)"]
        B["buffer.low_latency_dispatch()"]
        C["GPU Kernel: notify_dispatch<br/>Metadata exchange via RDMA"]
        D["GPU Kernel: dispatch<br/>Token routing to experts"]
        E["Output: packed_recv_x, handle<br/>Grouped by expert"]
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
    
    subgraph "Compute Phase"
        F["Expert computation<br/>(simulated_gemm_x)"]
    end
    
    subgraph "Combine Phase"
        G["buffer.low_latency_combine()"]
        H["GPU Kernel: combine<br/>Result aggregation with weights"]
        I["Output: combined_x<br/>Shape: (num_tokens, hidden)"]
        
        G --> H
        H --> I
    end
    
    E --> F
    F --> G
```

**Dispatch operation** routes tokens to the appropriate expert ranks:

```python
# Dispatch tokens to experts
packed_recv_x, packed_recv_count, handle, event, hook = buffer.low_latency_dispatch(
    current_x,                          # Input tokens: (num_tokens, hidden)
    topk_idx,                           # Expert indices: (num_tokens, num_topk)
    num_tokens,
    num_experts,
    use_fp8=True,                       # Enable FP8 quantization
    round_scale=False,                  # Scale rounding mode
    use_ue8m0=False,                    # UE8M0 format
    cumulative_local_expert_recv_stats=stats_buffer,  # Track received tokens
    async_finish=False,                 # Synchronous completion
    return_recv_hook=False              # Return event instead of hook
)

# Wait for completion
event.current_stream_wait()

# packed_recv_x: Tuple of (tokens_fp8, scales_fp8) if use_fp8=True
#                or BF16 tensor if use_fp8=False
# handle: Contains routing metadata for combine phase
```

**Combine operation** aggregates expert outputs back to original token positions:

```python
# Combine expert outputs
combined_x, event, hook = buffer.low_latency_combine(
    simulated_gemm_x,                   # Expert outputs
    topk_idx,                           # Same indices from dispatch
    topk_weights,                       # Expert weights: (num_tokens, num_topk)
    handle,                             # Routing handle from dispatch
    use_logfmt=False,                   # LogFMT format
    async_finish=False,
    zero_copy=False,                    # Zero-copy optimization
    return_recv_hook=False,
    out=output_buffer                   # Optional pre-allocated output
)

event.current_stream_wait()
# combined_x: (num_tokens, hidden)
```

Sources: [ep/README.md:49-84](), [thirdparty/DeepEP/tests/test_low_latency.py:40-108]()

### Normal Mode (Throughput-Optimized) Operations

For training workloads with larger batch sizes, normal mode provides higher throughput:

```python
# Get dispatch layout
num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, handle = \
    buffer.get_dispatch_layout(topk_idx, num_experts)

# Configure for throughput
config = deep_ep.Config(
    num_sms=24,                         # Number of SMs to use
    nvl_chunk_size=8,                   # NVLink chunk size
    nvl_buffer_size=512,                # NVLink buffer size
    rdma_chunk_size=16,                 # RDMA chunk size
    rdma_buffer_size=128                # RDMA buffer size
)

# Dispatch with configuration
recv_x, recv_topk_idx, recv_topk_weights, recv_num_tokens_per_expert_list, handle, event = \
    buffer.dispatch(
        x=current_x,                     # Can be BF16 tensor or (FP8, scales) tuple
        num_tokens_per_rank=num_tokens_per_rank,
        num_tokens_per_rdma_rank=num_tokens_per_rdma_rank,
        is_token_in_rank=is_token_in_rank,
        num_tokens_per_expert=num_tokens_per_expert,
        config=config,
        topk_idx=topk_idx,               # Optional for first dispatch
        topk_weights=topk_weights,       # Optional
        async_finish=True                # Non-blocking
    )

# Combine with configuration
combined_x, combined_topk_weights, event = buffer.combine(
    x=recv_x,
    bias=(bias_0, bias_1),               # Optional bias tensors
    handle=handle,
    config=config,
    topk_weights=recv_topk_weights,      # Optional
    async_finish=True
)
```

The normal mode uses warp-specialized kernels with distinct roles:
- **Senders**: Post RDMA write operations
- **Forwarders**: Route data via NVLink within nodes
- **Receivers**: Poll completion queues and pack incoming data

Sources: [thirdparty/DeepEP/tests/test_internode.py:15-225]()

### Performance Characteristics by Mode

| Mode | Batch Size | Latency (dispatch+combine) | Throughput (RDMA) | Use Case |
|------|-----------|---------------------------|-------------------|----------|
| **Low-Latency** | 128 tokens | 136-300 µs | 30-55 GB/s | Inference, online serving |
| **Normal (Throughput)** | 4096 tokens | 1200-7000 µs | 50-70 GB/s | Training, large batches |

Example performance on H200 with 16x 200Gb/s EFA (DeepSeek-V3 config):

```
Low-Latency (128 tokens, top-8, 7168 hidden):
- Dispatch: 226 µs, 36 GB/s (16 experts)
- Combine: 293 µs, 48 GB/s (16 experts)

Normal Mode (4096 tokens, top-8, 7168 hidden):
- Dispatch: 1196 µs, 50 GB/s (16 experts)  
- Combine: 6379 µs, 18 GB/s (16 experts)
```

Sources: [ep/README.md:116-187]()

---

## Pattern 3: Hybrid Local/Remote Communication

Both P2P and EP systems automatically optimize communication based on peer locality.

### Connection Type Selection Logic

```mermaid
graph TB
    A["Peer Rank"]
    B{"Same IP<br/>address?"}
    C["Local Connection"]
    D["Remote Connection"]
    
    E["use_copy_engine_for_intra?"]
    F["Unix Domain Socket<br/>IPC (send_ipc/recv_ipc)"]
    G["NCCL P2P<br/>(dist.isend/irecv)"]
    
    H["RDMA/EFA<br/>(ep.send/recv)"]
    I["Memory registration<br/>required"]
    
    A --> B
    B -->|"Yes"| C
    B -->|"No"| D
    
    C --> E
    E -->|"True"| F
    E -->|"False"| G
    
    D --> H
    H --> I
```

The `CollectiveContext` determines locality during initialization:

```python
# During connection establishment
local_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[rank])

for peer_rank in range(world_size):
    if peer_rank != rank:
        peer_ip, _, _ = p2p.Endpoint.parse_metadata(all_metadata[peer_rank])
        self.local_connections[peer_rank] = (peer_ip == local_ip)
```

### Transparent API with Locality Optimization

The send/receive API automatically selects the appropriate transport:

```python
def send(self, tensor, dst):
    if self.local_connections[dst]:
        if self.use_copy_engine_for_intra:
            # Use IPC (no registration needed)
            self.ep.send_ipc(conn_id, ptr, size)
        else:
            # Use NCCL for local
            dist.send(tensor, dst, group=self.group)
    else:
        # Use RDMA (requires registration)
        mr_id = self.check_tensor_registered(tensor)
        if mr_id is None:
            raise RuntimeError("Tensor not registered for remote communication")
        self.ep.send(conn_id, mr_id, ptr, size)
```

**Key differences:**
- **Local communication**: No memory registration required, can use NCCL or IPC
- **Remote communication**: Requires memory registration, uses RDMA/EFA transport
- **Async operations**: Return different handle types (`int` vs `dist.Work`) based on locality

Sources: [p2p/collective.py:181-318](), [p2p/collective.py:382-534]()

---

## Common Integration Patterns

### Ring Communication Pattern

Useful for reduce-scatter and similar collective operations:

```python
rank = dist.get_rank()
world_size = dist.get_world_size()

# Ring topology: each rank sends to next, receives from previous
send_rank = (rank + 1) % world_size
recv_rank = (rank - 1 + world_size) % world_size

# Register tensors
collective.register_tensor(send_tensor)
collective.register_tensor(recv_tensor)

# Execute ring step
handles = collective.batch_isend_irecv([
    collective.P2POp(collective.isend, send_tensor, send_rank),
    collective.P2POp(collective.irecv, recv_tensor, recv_rank),
])
collective.wait_all(handles)
```

Sources: [p2p/benchmarks/benchmark_uccl_collective.py:231-327](), [p2p/benchmarks/benchmark_uccl_alltoall.py:182-256]()

### FCP (Fractional Circular Permutation) All-to-All

For disaggregated attention and similar workloads:

```python
# Get communication plan for this iteration
plans = get_fcp_comm_plans(world_size, num_iters)
send_rank = plans[iter_idx][0][rank]
recv_rank = plans[iter_idx][1][rank]

# Execute planned communication
handles = collective.batch_isend_irecv([
    collective.P2POp(collective.isend, send_tensor, send_rank),
    collective.P2POp(collective.irecv, recv_tensor, recv_rank),
])
collective.wait_all(handles)
```

Sources: [p2p/benchmarks/benchmark_uccl_alltoall.py:113-180]()

### Error Handling and Cleanup

```python
try:
    # Initialize collective
    collective.init_collective(num_cpus=4)
    
    # Create and register tensors
    tensor = torch.randn(1024, 1024).cuda()
    collective.register_tensor(tensor)
    
    # Perform operations
    collective.send(tensor, dst=1)
    
finally:
    # Always finalize to clean up resources
    collective.finalize_collective()
    dist.destroy_process_group()
```

The `finalize_collective()` function:
- Deregisters all memory regions
- Closes all connections
- Frees internal data structures
- Must be called before `dist.destroy_process_group()`

Sources: [p2p/collective.py:580-592](), [p2p/benchmarks/benchmark_uccl_collective.py:453-456]()

---

## Platform-Specific Considerations

### CUDA vs ROCm

UCCL uses a unified GPU runtime abstraction layer that supports both CUDA and ROCm:

| Symbol | CUDA | ROCm |
|--------|------|------|
| Stream type | `cudaStream_t` | `hipStream_t` |
| Memory operations | `cudaMalloc`, `cudaMemcpy` | `hipMalloc`, `hipMemcpy` |
| Device management | `cudaSetDevice` | `hipSetDevice` |
| IPC handles | `cudaIpcMemHandle_t` | `hipIpcMemHandle_t` |

The abstraction is defined in `include/util/gpu_rt.h` with compile-time selection based on `__HIP_PLATFORM_AMD__`.

Sources: [include/util/gpu_rt.h:1-157]()

### Docker Build Environments

UCCL provides platform-specific Docker images for builds:

| Platform | Base Image | PyTorch Source | Network Support |
|----------|------------|----------------|-----------------|
| **CUDA** | `nvidia/cuda:12.8.0` | PyPI cu128 | InfiniBand, EFA |
| **ROCm** | `rocm/dev-ubuntu-22.04` | Nightly rocm7.0 | InfiniBand, Broadcom |
| **GH200** | `nvidia/cuda:12.4.1` (ARM64) | PyPI cu126 | InfiniBand, EFA |
| **EFA** | `nvidia/cuda:12.8.0` + EFA installer | PyPI cu128 | AWS EFA |
| **TheRock** | manylinux + ROCm | N/A (user-provided) | Generic |

Each environment installs:
- Python 3.13 (via deadsnakes PPA)
- PyTorch with matching accelerator support
- Build tools (pybind11, auditwheel)
- Network libraries (libibverbs, libefa where applicable)

Sources: [docker/Dockerfile.cuda:1-52](), [docker/Dockerfile.rocm:1-54](), [docker/Dockerfile.gh:1-51](), [docker/Dockerfile.efa:1-76](), [docker/Dockerfile.therock:1-17]()

---

## Best Practices

### Memory Management

1. **Register tensors once, use many times**: Registration is expensive, cache registered tensors
2. **Match registration lifetime to tensor lifetime**: Deregister when tensor is no longer needed
3. **Use contiguous tensors**: Non-contiguous tensors cannot be registered
4. **Pre-allocate buffers**: Reuse buffers across iterations to avoid repeated allocation/registration

### Performance Optimization

1. **Use batch operations**: `batch_isend_irecv()` reduces kernel launch overhead
2. **Overlap communication and computation**: Use async operations with `isend/irecv`
3. **Tune EP configuration parameters**: `nvl_chunk_size`, `rdma_chunk_size` significantly impact throughput
4. **Profile with CUDA events**: Use `torch.cuda.Event` to measure communication latency accurately

### Device and Process Management

1. **Set CUDA device early**: Call `torch.cuda.set_device()` before any GPU operations
2. **Use torchrun for multi-node**: Ensures correct `RANK`, `WORLD_SIZE`, `LOCAL_RANK` environment variables
3. **Synchronize before benchmarking**: Call `torch.cuda.synchronize()` and `dist.barrier()` to ensure fair timing
4. **Clean up in finally blocks**: Always call `finalize_collective()` even on exceptions

Sources: [p2p/benchmarks/benchmark_uccl_collective.py:23-463](), [thirdparty/DeepEP/tests/utils.py:109-243]()

---

# Page: Configuration and Tuning

# Configuration and Tuning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/clang-format-check.yml](.github/workflows/clang-format-check.yml)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [format.sh](format.sh)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [scripts/node_ips/tpu_2.txt](scripts/node_ips/tpu_2.txt)
- [scripts/setup_all.py](scripts/setup_all.py)
- [scripts/setup_nic.sh](scripts/setup_nic.sh)

</details>



This page documents performance tuning parameters, environment variables, and configuration mechanisms for UCCL components across different workloads and hardware platforms. For integration patterns and usage examples, see [PyTorch Integration Patterns](#6.2). For NCCL plugin environment variables, see [NCCL/RCCL Plugin Integration](#6.1).

## Overview

UCCL configuration occurs at three levels:

1. **Build-time configuration**: Compiler flags, architecture detection, and feature selection
2. **Runtime configuration**: Buffer sizes, chunk sizes, number of SMs, and kernel parameters
3. **System configuration**: NIC settings, IRQ affinity, and network tuning

The primary tuning interface is the `Config` class in the EP system, which controls buffer sizes and parallelism parameters. Performance tuning typically involves iterating through different configurations to find optimal chunk sizes and buffer allocations for specific workloads.

## Build-Time Configuration

### Architecture Detection and Compiler Flags

The build system automatically detects GPU architecture and sets appropriate compiler flags. Configuration is controlled through [ep/setup.py]() and [ep/Makefile]().

```mermaid
graph TB
    subgraph "Build Configuration Flow"
        DETECT["Platform Detection<br/>setup.py detect_compute_cap"]
        
        subgraph "GPU Architecture"
            SM90["SM 9.0+<br/>H100/H200/B200/GH200"]
            SM80["SM 8.0<br/>A100"]
            GFX942["gfx942<br/>MI300X"]
        end
        
        subgraph "Compiler Flags"
            FP8["FP8 Support<br/>cuda_fp8.h"]
            TMA["TMA Operations<br/>Hopper optimization"]
            PTX["Aggressive PTX<br/>LD/ST tricks"]
            ROCM_FLAGS["ROCm Flags<br/>offload-arch"]
        end
        
        subgraph "Feature Flags"
            DISABLE_SM90["DISABLE_SM90_FEATURES<br/>Force Ampere mode"]
            DISABLE_PTX["DISABLE_AGGRESSIVE_PTX_INSTRS<br/>Disable LD/ST tricks"]
            DISABLE_ATOMIC["DISABLE_AGGRESSIVE_ATOMIC<br/>AMD only"]
        end
    end
    
    DETECT --> SM90
    DETECT --> SM80
    DETECT --> GFX942
    
    SM90 --> FP8
    SM90 --> TMA
    SM90 --> PTX
    SM80 --> DISABLE_SM90
    GFX942 --> ROCM_FLAGS
    GFX942 --> DISABLE_SM90
    
    DISABLE_SM90 -.disables.-> FP8
    DISABLE_SM90 -.disables.-> TMA
    DISABLE_PTX -.disables.-> PTX
```

**Sources**: [ep/setup.py:85-190](), [ep/Makefile:16-61]()

### Key Build Flags

| Flag | Purpose | Default Behavior |
|------|---------|------------------|
| `TORCH_CUDA_ARCH_LIST` | Set GPU architecture (e.g., "9.0", "8.0") | Auto-detected via `nvidia-smi` |
| `DISABLE_SM90_FEATURES` | Force Ampere (SM 8.0) compatibility | Disabled for SM 9.0+, enabled for AMD |
| `DISABLE_AGGRESSIVE_PTX_INSTRS` | Disable `LD/ST` optimizations | Enabled for SM < 9.0 |
| `DISABLE_AGGRESSIVE_ATOMIC` | Use standard atomic operations (AMD) | Disabled |
| `EFA_HOME` | Path to AWS EFA installation | `/opt/amazon/efa` |
| `USE_GRACE_HOPPER` | Enable GH200-specific optimizations | Auto-detected |

**Sources**: [ep/setup.py:141-190](), [ep/Makefile:1-61]()

### Platform-Specific Docker Builds

UCCL provides Docker environments with pre-configured compiler settings:

```mermaid
graph LR
    subgraph "Docker Build Targets"
        CUDA["uccl-builder-cuda<br/>Dockerfile.cuda<br/>CUDA 12.8+"]
        ROCM["uccl-builder-rocm<br/>Dockerfile.rocm<br/>ROCm 7.0+"]
        GH["uccl-builder-gh<br/>Dockerfile.gh<br/>Grace Hopper"]
        EFA["uccl-builder-efa<br/>Dockerfile.efa<br/>AWS EFA"]
        THEROCK["uccl-builder-therock<br/>Dockerfile.therock<br/>manylinux + ROCm"]
    end
    
    CUDA --> WHEEL_CUDA["uccl-*-cp313-cuda.whl"]
    ROCM --> WHEEL_ROCM["uccl-*-cp313-rocm.whl"]
    GH --> WHEEL_GH["uccl-*-cp313-gh200.whl"]
    EFA --> WHEEL_EFA["uccl-*-cp313-efa.whl"]
    THEROCK --> WHEEL_THEROCK["uccl-*-cp313-manylinux.whl"]
```

**Sources**: [docker/Dockerfile.cuda](), [docker/Dockerfile.rocm](), [docker/Dockerfile.gh](), [docker/Dockerfile.efa](), [docker/Dockerfile.therock]()

## Runtime Configuration: EP System

### Config Class Structure

The primary tuning interface is the `Config` class, which controls buffer allocation and kernel parallelism:

```python
from uccl.ep import Config

config = Config(
    num_sms,                  # Number of SMs to use for kernels
    nvl_chunk_size,           # NVLink chunk size (tokens per iteration)
    nvl_buffer_size,          # NVLink buffer capacity (tokens)
    rdma_chunk_size,          # RDMA chunk size (tokens per iteration)
    rdma_buffer_size          # RDMA buffer capacity (tokens)
)
```

**Sources**: [ep/bench/test_internode.py:175-179]()

### Configuration Parameters

```mermaid
graph TB
    subgraph "Config Parameters"
        NUM_SMS["num_sms<br/>Kernel parallelism<br/>ceil_div(num_experts, num_warp_groups)"]
        
        subgraph "NVLink Configuration"
            NVL_CHUNK["nvl_chunk_size<br/>Tokens per iteration<br/>Range: 1-44"]
            NVL_BUFFER["nvl_buffer_size<br/>Buffer capacity<br/>Typical: 512-720"]
        end
        
        subgraph "RDMA Configuration"
            RDMA_CHUNK["rdma_chunk_size<br/>Tokens per iteration<br/>Range: 4-32"]
            RDMA_BUFFER["rdma_buffer_size<br/>Buffer capacity<br/>Typical: 512"]
        end
    end
    
    subgraph "Kernel Execution"
        DISPATCH["dispatch kernel<br/>internode.cu / internode_ll.cu"]
        COMBINE["combine kernel<br/>internode.cu / internode_ll.cu"]
    end
    
    NUM_SMS --> DISPATCH
    NUM_SMS --> COMBINE
    NVL_CHUNK --> DISPATCH
    NVL_CHUNK --> COMBINE
    NVL_BUFFER --> DISPATCH
    NVL_BUFFER --> COMBINE
    RDMA_CHUNK --> DISPATCH
    RDMA_CHUNK --> COMBINE
    RDMA_BUFFER --> DISPATCH
    RDMA_BUFFER --> COMBINE
```

**Sources**: [ep/bench/test_internode.py:367-421]()

### Static Configuration Constants

Key constants are defined in [ep/include/ep_configs.cuh]():

| Constant | Value | Purpose |
|----------|-------|---------|
| `NUM_MAX_NVL_PEERS` | 8 | Maximum GPUs per node |
| `NUM_MAX_RDMA_PEERS` | 20 | Maximum RDMA-connected nodes |
| `NUM_WORKSPACE_BYTES` | 32 MB | Scratch space for kernels |
| `NUM_MAX_LOCAL_EXPERTS` | 1024 | Maximum experts per rank |
| `NUM_BUFFER_ALIGNMENT_BYTES` | 128 | Memory alignment requirement |
| `WARP_SIZE` | 32 (CUDA) / 64 (ROCm) | Warp/wavefront size |
| `NUM_TIMEOUT_CYCLES` | 200B (CUDA) / 20B (ROCm) | Kernel timeout (~100s) |

**Sources**: [ep/include/ep_configs.cuh:1-86]()

## Performance Tuning Workflow

### Automated Tuning Process

The tuning process iterates through chunk size combinations to find optimal configurations. Example from [ep/bench/test_internode.py:352-421]():

```mermaid
graph TB
    subgraph "Tuning Loop"
        START["Start with default config<br/>nvl_buffer_size=512<br/>rdma_buffer_size=512"]
        
        subgraph "Dispatch Tuning"
            DISP_LOOP["for nvl_chunk in range(4, 45, 4):<br/>  for rdma_chunk in range(4, 33, 4):"]
            DISP_BENCH["bench_kineto(dispatch)<br/>Measure transmit time"]
            DISP_CALC["Calculate bandwidth:<br/>RDMA: rdma_send_bytes / time<br/>NVLink: nvl_recv_bytes / time"]
            DISP_BEST["Track best_time, best_config"]
        end
        
        subgraph "Combine Tuning"
            COMB_LOOP["for nvl_chunk in range(1, 8, 1):<br/>  for rdma_chunk in range(8, 33, 4):"]
            COMB_BENCH["bench_kineto(combine)<br/>Measure transmit time"]
            COMB_CALC["Calculate bandwidth"]
            COMB_BEST["Select best_config"]
        end
    end
    
    START --> DISP_LOOP
    DISP_LOOP --> DISP_BENCH
    DISP_BENCH --> DISP_CALC
    DISP_CALC --> DISP_BEST
    DISP_BEST --> COMB_LOOP
    COMB_LOOP --> COMB_BENCH
    COMB_BENCH --> COMB_CALC
    COMB_CALC --> COMB_BEST
```

**Sources**: [ep/bench/test_internode.py:352-446]()

### Mode-Specific Configuration

UCCL EP supports two performance modes with different tuning strategies:

| Mode | Batch Size | Latency Target | Bandwidth Target | Use Case |
|------|------------|----------------|------------------|----------|
| **Low-Latency** | 128 tokens | 136-300 µs | 33-46 GB/s | Online inference |
| **Normal (Throughput)** | 4096 tokens | 1-7 ms | 50-70 GB/s | Training |

**Low-latency mode** uses:
- Pure RDMA (no NVLink forwarding)
- Smaller chunk sizes (typically 1-4 tokens)
- Direct GPU-initiated sends without CPU coordination

**Normal mode** uses:
- Combined RDMA + NVLink forwarding
- Larger chunk sizes (4-32 tokens for RDMA, 4-44 for NVLink)
- Multi-warp coordination for higher throughput

**Sources**: [ep/README.md:158-187](), [ep/src/internode_ll.cu:48-587]()

### Example Tuning Output

Typical tuning output shows performance exploration:

```
[tuning] SMs 36, NVL chunk 8, RDMA chunk 4, transmit: 1196.00 us, notify: 45.00 us, BW: 50.00 GB/s (RDMA), 320.00 GB/s (NVL)
[tuning] SMs 36, NVL chunk 12, RDMA chunk 8, transmit: 1150.00 us, notify: 45.00 us, BW: 52.00 GB/s (RDMA), 325.00 GB/s (NVL)
[tuning] Best dispatch (FP8): SMs 36, NVL chunk 12, RDMA chunk 8, transmit: 1150.00 us, BW: 52.00 GB/s (RDMA), 325.00 GB/s (NVL)
```

**Sources**: [ep/bench/test_internode.py:386-396]()

## Environment Variables

### NCCL Plugin Variables

When using UCCL as an NCCL plugin, these variables control behavior:

| Variable | Purpose | Example |
|----------|---------|---------|
| `NCCL_NET_PLUGIN` | Path to UCCL plugin library | `/path/to/libnccl-net-uccl.so` |
| `NCCL_DEBUG` | Enable NCCL debug output | `INFO`, `WARN`, `TRACE` |
| `NCCL_SOCKET_IFNAME` | Network interface for bootstrap | `ens6`, `enp199s0` |

For RCCL (AMD):
```bash
export RCCL_NET_PLUGIN=/path/to/librccl-net-uccl.so
```

**Sources**: Referenced from context about NCCL plugin integration

### Build Environment Variables

Variables affecting compilation:

| Variable | Purpose | Default |
|----------|---------|---------|
| `CUDA_HOME` | CUDA toolkit path | `/usr/local/cuda` |
| `EFA_HOME` | AWS EFA installation path | `/opt/amazon/efa` |
| `TORCH_CUDA_ARCH_LIST` | Target GPU architecture | Auto-detected |
| `DISABLE_SM90_FEATURES` | Force Ampere compatibility | `0` (auto) |
| `DISABLE_AGGRESSIVE_PTX_INSTRS` | Disable LD/ST optimizations | Auto for SM < 9.0 |
| `DISABLE_AGGRESSIVE_ATOMIC` | Use standard atomics (AMD) | `0` |

**Sources**: [ep/setup.py:65-191](), [ep/Makefile:1-14]()

## System Configuration

### Network Interface Configuration

UCCL includes scripts for optimizing NIC settings. The [scripts/setup_nic.sh]() script configures:

```mermaid
graph TB
    subgraph "NIC Configuration Script"
        INPUT["setup_nic.sh<br/>Args: NIC NQUEUE NIRQCORE MTU MODE PLATFORM"]
        
        subgraph "Queue Configuration"
            COMBINED["ethtool -L combined NQUEUE<br/>Non-TPU platforms"]
            SEPARATE["ethtool -L rx/tx NQUEUE<br/>TPU platforms"]
        end
        
        subgraph "IRQ Affinity"
            IRQ_START["Calculate irq_start_cpu<br/>AWS: NCPU/4<br/>TPU: NCPU/8<br/>Others: 3*NCPU/4"]
            IRQ_BIND["Bind IRQs to cores<br/>Round-robin starting from irq_start_cpu"]
        end
        
        subgraph "Mode-Specific Settings"
            AFXDP_MODE["AF_XDP Mode:<br/>- Stop irqbalance<br/>- Disable adaptive IRQ coalescing<br/>- Set rx-usecs=0, tx-usecs=0"]
            TCP_MODE["TCP Mode:<br/>- Start irqbalance<br/>- Enable adaptive IRQ coalescing<br/>- Set rx-usecs=20, tx-usecs=60"]
        end
    end
    
    INPUT --> COMBINED
    INPUT --> SEPARATE
    INPUT --> IRQ_START
    IRQ_START --> IRQ_BIND
    INPUT --> AFXDP_MODE
    INPUT --> TCP_MODE
```

**Sources**: [scripts/setup_nic.sh:1-104]()

### Platform-Specific NIC Settings

Different platforms require different configurations:

| Platform | Queue Config | IRQ Coalescing (AF_XDP) | IRQ Coalescing (TCP) |
|----------|--------------|-------------------------|---------------------|
| AWS (EFA/ENA) | `combined NQUEUE` | `adaptive-rx off rx-usecs 0 tx-usecs 0` | `adaptive-rx on rx-usecs 20 tx-usecs 60` |
| CloudLab | `combined NQUEUE` | `adaptive-rx off adaptive-tx off rx-usecs 0 tx-usecs 0` | `adaptive-rx on adaptive-tx on rx-usecs 8` |
| TPU | `rx NQUEUE tx NQUEUE` | `rx-usecs 0 tx-usecs 0` | `rx-usecs 20 tx-usecs 50` |
| IBM | `combined NQUEUE` | Same as AWS | Same as AWS |

**Sources**: [scripts/setup_nic.sh:25-52]()

### IRQ Affinity Strategy

IRQ affinity is configured to avoid conflicts with application threads:

- **AWS/TPU**: Start IRQs at `NCPU/4` or `NCPU/8` to avoid conflicting with application cores
- **Other platforms**: Start IRQs at `3*NCPU/4` to reserve first 75% for application
- **Round-robin assignment**: IRQs are distributed across `NIRQCORE` cores starting from `irq_start_cpu`

**Sources**: [scripts/setup_nic.sh:54-83]()

## Platform-Specific Optimizations

### CUDA vs ROCm Differences

Configuration varies between CUDA and ROCm platforms:

```mermaid
graph LR
    subgraph "Platform-Specific Settings"
        subgraph "CUDA (NVIDIA)"
            CUDA_WARP["WARP_SIZE = 32"]
            CUDA_TIMEOUT["NUM_TIMEOUT_CYCLES = 200B"]
            CUDA_THREADS["kNumThreads = 512"]
            CUDA_FEATURES["FP8, TMA support<br/>cuda_fp8.h"]
        end
        
        subgraph "ROCm (AMD)"
            ROCM_WARP["WARP_SIZE = 64"]
            ROCM_TIMEOUT["NUM_TIMEOUT_CYCLES = 20B"]
            ROCM_THREADS["kNumThreads = 1024"]
            ROCM_ATOMICS["Custom atomic ops<br/>HIP_ATOMIC_*"]
        end
    end
    
    CUDA_WARP -.differs.-> ROCM_WARP
    CUDA_TIMEOUT -.differs.-> ROCM_TIMEOUT
    CUDA_THREADS -.differs.-> ROCM_THREADS
    CUDA_FEATURES -.differs.-> ROCM_ATOMICS
```

**Sources**: [ep/include/ep_configs.cuh:58-86](), [ep/include/ep_utils.cuh:15-31](), [ep/src/internode.cu:425-429]()

### AWS EFA-Specific Configuration

AWS EFA requires special handling:

1. **Build with EFA support**: Set `EFA_HOME=/opt/amazon/efa` during build
2. **NIC configuration**: Use `setup_nic.sh` with `aws` platform flag
3. **IRQ affinity**: Start at `NCPU/4` to avoid application cores
4. **MTU**: Use 9001 for TCP, 3498 for AF_XDP

Example setup:
```bash
export EFA_HOME=/opt/amazon/efa
cd scripts
./setup_nic.sh ens6 32 32 9001 tcp aws
```

**Sources**: [docker/Dockerfile.efa:46-76](), [scripts/setup_nic.sh:59-63]()

### Grace Hopper (GH200) Optimizations

GH200 detection enables coherent CPU-GPU memory:

```c++
#ifdef USE_GRACE_HOPPER
  // Enable CPU-GPU coherent memory access
  // Use system-scope atomic operations
#endif
```

Detection logic in [ep/setup.py:119-138]():
- Requires ARM64 CPU (`arch == "aarch64"`)
- Requires Hopper GPU (name contains "GH200")
- Automatically sets `USE_GRACE_HOPPER` flag

**Sources**: [ep/setup.py:119-138](), [ep/Makefile:16-32](), [docker/Dockerfile.gh:49]()

## Tuning Recommendations

### Initial Configuration

Start with these baseline configurations:

**For training (4096 tokens/batch)**:
```python
config = Config(
    num_sms=36,              # For 288 experts across 32 ranks
    nvl_chunk_size=8,        # Start conservative
    nvl_buffer_size=512,     # Increase to 720 for 144-160 ranks
    rdma_chunk_size=8,
    rdma_buffer_size=512
)
```

**For inference (128 tokens/batch)**:
```python
config = Config(
    num_sms=36,
    nvl_chunk_size=1,        # Minimize latency
    nvl_buffer_size=256,     # Smaller buffer OK
    rdma_chunk_size=4,
    rdma_buffer_size=256
)
```

**Sources**: [ep/bench/test_internode.py:175-179]()

### Tuning Strategy

1. **Start with dispatch tuning**: Focus on NVLink chunk sizes (4-44) and RDMA chunk sizes (4-32)
2. **Measure bandwidth**: Compare achieved bandwidth against hardware limits (50-70 GB/s RDMA, 300-320 GB/s NVLink)
3. **Tune combine separately**: Use smaller NVLink chunks (1-8) and larger RDMA chunks (8-32)
4. **Consider FP8 vs BF16**: FP8 reduces bandwidth by ~50% but may require different chunk sizes

### Hardware-Specific Targets

| Platform | RDMA Bandwidth Target | NVLink Bandwidth Target | Notes |
|----------|----------------------|------------------------|-------|
| **p5en (H200 + 16x200G EFA)** | 50-54 GB/s | 320 GB/s | Dual EFA per GPU |
| **p6-b200 (B200 + 8x400G EFA)** | 53-60 GB/s | 280-426 GB/s | Single EFA per GPU |
| **MI300X + CX7 IB** | 71-81 GB/s | N/A | InfiniBand advantage |
| **MI300X + Thor2** | 49-81 GB/s | N/A | Depends on config |

**Sources**: [ep/README.md:118-156]()

## Troubleshooting Configuration Issues

### Common Issues

**Kernel timeout errors**:
- Symptom: `DeepEP dispatch RDMA sender timeout` messages
- Cause: Buffer sizes too small for workload, or chunk sizes too large
- Solution: Increase `rdma_buffer_size` or decrease `rdma_chunk_size`

**Low bandwidth**:
- Check NIC configuration with `ethtool -S <interface>`
- Verify IRQ affinity with `cat /proc/irq/*/smp_affinity_list`
- Run tuning loop to find optimal chunk sizes

**Build failures**:
- Ensure correct `TORCH_CUDA_ARCH_LIST` for your GPU
- Check CUDA/ROCm version compatibility
- For EFA: Verify `EFA_HOME` points to valid installation

**Sources**: [ep/src/internode.cu:743-752](), [scripts/setup_nic.sh]()

---

# Page: Testing and Benchmarking

# Testing and Benchmarking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)

</details>



This document covers UCCL's testing and benchmarking infrastructure, including performance measurement tools, integration testing with NCCL/RCCL, and multi-node validation systems. The testing framework validates UCCL's transport backends against established baselines and ensures compatibility with distributed training workloads.

For information about the actual transport implementations being tested, see [Transport Backends](#2). For build system configuration, see [Build System and Deployment](#6).

## Performance Benchmarking Tools

UCCL provides comprehensive benchmarking tools to measure performance across different transport backends and compare against NCCL baselines. The benchmarking suite covers latency, bandwidth, and scalability metrics for various communication patterns.

### Benchmark Architecture Overview

```mermaid
graph TB
    subgraph "Benchmark Applications"
        UCCL_BENCH["benchmark_uccl.py<br/>Direct P2P Testing"]
        NIXL_BENCH["benchmark_nixl.py<br/>NIXL Backend Testing"]
        NCCL_BENCH["benchmark_nccl.py<br/>PyTorch Baseline"]
        REDIS_BENCH["benchmark_redis.py<br/>Rendezvous Testing"]
    end
    
    subgraph "UCCL System Under Test"
        P2P_ENGINE["p2p.Endpoint<br/>Direct RDMA Interface"]
        NIXL_BACKEND["NIXL Agent<br/>with UCCL Backend"]
        NCCL_PLUGIN["libnccl-net-uccl.so<br/>NCCL Plugin"]
    end
    
    subgraph "Baseline Comparisons"
        TORCH_DIST["torch.distributed<br/>NCCL Backend"]
        UCX_BASELINE["UCX Backend<br/>via NIXL"]
        MOONCAKE["Mooncake Backend<br/>via NIXL"]
    end
    
    subgraph "Test Infrastructure"
        MPI_LAUNCHER["mpirun<br/>Multi-node Execution"]
        HOSTFILE["node_ips/amd.txt<br/>Node Configuration"]
        ENV_CONFIG["Environment Variables<br/>NCCL_*/UCCL_*"]
    end
    
    UCCL_BENCH --> P2P_ENGINE
    NIXL_BENCH --> NIXL_BACKEND
    NCCL_BENCH --> TORCH_DIST
    REDIS_BENCH --> P2P_ENGINE
    
    NIXL_BACKEND --> UCX_BASELINE
    NIXL_BACKEND --> MOONCAKE
    
    MPI_LAUNCHER --> HOSTFILE
    MPI_LAUNCHER --> ENV_CONFIG
    MPI_LAUNCHER --> NCCL_PLUGIN
    
    style P2P_ENGINE fill:#e1f5fe
    style NIXL_BACKEND fill:#fff3e0
    style NCCL_PLUGIN fill:#e8f5e8
```

Sources: [p2p/benchmarks/benchmark_uccl.py](), [p2p/benchmarks/benchmark_nixl.py](), [p2p/benchmarks/benchmark_nccl.py](), [p2p/benchmarks/benchmark_redis.py](), [rdma/run_rccl_test.sh](), [scripts/node_ips/amd.txt]()

### P2P Engine Benchmarking

The `benchmark_uccl.py` script provides comprehensive testing of UCCL's P2P communication engine with support for various communication modes and configurations.

#### Benchmark Test Modes

| Mode | Function | Description |
|------|----------|-------------|
| Standard | `_run_client()`, `_run_server()` | Unidirectional send/recv testing |
| Dual | `_run_client_dual()`, `_run_server_dual()` | Bidirectional simultaneous transfers |
| IPC | `_run_client_ipc()`, `_run_server_ipc()` | Local GPU-to-GPU via memory handles |
| Async | `send_async()`, `recv_async()` | Asynchronous transfer operations |

#### Key Test Parameters

```mermaid
graph LR
    subgraph "Buffer Configuration"
        DEVICE["device: cpu/gpu"]
        GPU_IDX["local_gpu_idx: 0-7"]
        SIZES["sizes: 256B-100MB"]
    end
    
    subgraph "Transfer Patterns"
        KVBLOCKS["num_kvblocks: 1-N"]
        ASYNC_API["async_api: true/false"]
        ITERS["iters: 1000"]
    end
    
    subgraph "Connection Types"
        STANDARD["Standard RDMA"]
        DUAL["Bidirectional"]
        IPC["Local IPC"]
    end
    
    DEVICE --> STANDARD
    GPU_IDX --> DUAL
    SIZES --> IPC
    
    KVBLOCKS --> STANDARD
    ASYNC_API --> DUAL
    ITERS --> IPC
```

Sources: [p2p/benchmarks/benchmark_uccl.py:417-476]()

### NIXL Backend Comparison

The `benchmark_nixl.py` script enables performance comparison between UCCL and other high-performance backends through the NIXL interface.

#### Backend Configuration Matrix

```mermaid
graph TB
    subgraph "NIXL Agent Creation"
        CREATE_MC["create_nixl_agent_mc()<br/>Mooncake/UCCL"]
        CREATE_UCX["create_nixl_agent_ucx()<br/>UCX Backend"]
    end
    
    subgraph "Transfer Operations"
        INIT_MC["init_transfer_metadata_mc()"]
        INIT_UCX["init_transfer_metadata_ucx()"]
        DO_TRANSFER["do_transfer_*()"]
    end
    
    subgraph "Backend Support"
        MOONCAKE["backend=mooncake"]
        UCCL["backend=uccl"]
        UCX["backend=ucx"]
    end
    
    subgraph "Operation Types"
        WRITE_OP["op_type=write"]
        READ_OP["op_type=read"]
        DUAL_OP["dual=true"]
    end
    
    CREATE_MC --> MOONCAKE
    CREATE_MC --> UCCL
    CREATE_UCX --> UCX
    
    INIT_MC --> WRITE_OP
    INIT_UCX --> READ_OP
    DO_TRANSFER --> DUAL_OP
```

Sources: [p2p/benchmarks/benchmark_nixl.py:76-96](), [p2p/benchmarks/benchmark_nixl.py:591-594]()

## Integration Testing with NCCL/RCCL

UCCL integrates with NCCL and RCCL through plugin interfaces, requiring comprehensive testing to ensure compatibility with distributed training frameworks.

### RCCL Test Execution Pipeline

```mermaid
graph TB
    subgraph "Test Script: run_rccl_test.sh"
        SCRIPT_START["#!/bin/bash"]
        LOAD_SHARED["source ../scripts/shared.sh"]
        CHECK_CONDA["Check CONDA_LIB_HOME"]
    end
    
    subgraph "Plugin Configuration"
        TEST_SELECT["TEST=${1:-uccl}"]
        PLUGIN_PATH["plugin_path=uccl.rccl_plugin_path()"]
        RCCL_PLUGIN["NCCL_NET_PLUGIN=${plugin_path}"]
    end
    
    subgraph "MPI Execution"
        MPI_CMD["mpirun --prefix /usr/local/bin/ompi"]
        NODE_CONFIG["-np 4 -N 1 --hostfile $NODEFILE"]
        ENV_VARS["Environment Variables"]
    end
    
    subgraph "Test Binaries"
        ALLTOALL["alltoall_perf"]
        ALLREDUCE["all_reduce_perf"]
        RCCL_TESTS["thirdparty/rccl-tests/build/"]
    end
    
    subgraph "UCCL Configuration"
        NUM_ENGINES["UCCL_NUM_ENGINES=4"]
        PORT_ENTROPY["UCCL_PORT_ENTROPY=${UCCL_ENTROPY}"]
        CHUNK_SIZE["UCCL_CHUNK_SIZE_KB=32"]
        RC_MODE["UCCL_RCMODE=1"]
    end
    
    SCRIPT_START --> LOAD_SHARED
    LOAD_SHARED --> CHECK_CONDA
    CHECK_CONDA --> TEST_SELECT
    
    TEST_SELECT --> PLUGIN_PATH
    PLUGIN_PATH --> RCCL_PLUGIN
    
    MPI_CMD --> NODE_CONFIG
    NODE_CONFIG --> ENV_VARS
    ENV_VARS --> RCCL_TESTS
    
    NUM_ENGINES --> ALLTOALL
    PORT_ENTROPY --> ALLREDUCE
```

Sources: [rdma/run_rccl_test.sh:1-63]()

### Environment Variable Configuration

The RCCL test script configures numerous environment variables to optimize both NCCL and UCCL behavior:

| Category | Variables | Purpose |
|----------|-----------|---------|
| NCCL Core | `NCCL_P2P_DISABLE`, `NCCL_SHM_DISABLE` | Control transport selection |
| NCCL IB | `NCCL_IB_PCI_RELAXED_ORDERING`, `NCCL_IB_QPS_PER_CONNECTION` | InfiniBand optimization |
| NCCL Buffers | `NCCL_BUFFSIZE`, `NCCL_MIN_NCHANNELS`, `NCCL_MAX_NCHANNELS` | Memory and channel tuning |
| UCCL Engine | `UCCL_NUM_ENGINES`, `UCCL_PORT_ENTROPY` | Transport backend configuration |
| UCCL Data | `UCCL_CHUNK_SIZE_KB`, `UCCL_RCMODE` | Data handling parameters |

Sources: [rdma/run_rccl_test.sh:42-60]()

## Multi-Node Testing Infrastructure

UCCL's distributed testing infrastructure supports validation across multiple nodes to ensure scalability and network transport correctness.

### Node Configuration and Hostfiles

```mermaid
graph LR
    subgraph "Node Configuration Files"
        AMD_NODES["scripts/node_ips/amd.txt<br/>tw025, tw026<br/>tw052, tw054"]
    end
    
    subgraph "MPI Launcher Configuration"
        MPI_PARAMS["--bind-to none<br/>-np 4 -N 1<br/>--map-by ppr:1:node"]
        HOSTFILE_REF["--hostfile $NODEFILE"]
    end
    
    subgraph "Per-Node Environment"
        LD_PATH["LD_LIBRARY_PATH<br/>RCCL + CONDA + ROCm"]
        HIP_DEVICES["HIP_VISIBLE_DEVICES<br/>0,1,2,3,4,5,6,7"]
        GLOG["GLOG_v=0"]
    end
    
    AMD_NODES --> HOSTFILE_REF
    HOSTFILE_REF --> MPI_PARAMS
    MPI_PARAMS --> LD_PATH
    LD_PATH --> HIP_DEVICES
```

Sources: [scripts/node_ips/amd.txt](), [rdma/run_rccl_test.sh:42-55]()

### Test Binary Integration

The testing system integrates with RCCL's standard test binaries to ensure compatibility with established benchmarks.

```mermaid
graph TB
    subgraph "RCCL Test Binaries"
        TEST_BIN["TEST_BIN=alltoall_perf"]
        BUILD_PATH["thirdparty/rccl-tests/build/"]
        ALT_TESTS["all_reduce_perf"]
    end
    
    subgraph "Test Parameters"
        SIZE_RANGE["-b 1K -e 1G -f 2"]
        WARM_ITER["-w 5 -n 20"]
        CONCURRENCY["-c 1 -g 1 -t 8"]
    end
    
    subgraph "Output Logging"
        LOG_RCCL["rccl_qp${QP_SCALING}.log"]
        LOG_UCCL["uccl_qp${UCCL_ENTROPY}.log"]
        TEE_OUTPUT["tee command"]
    end
    
    TEST_BIN --> BUILD_PATH
    BUILD_PATH --> SIZE_RANGE
    SIZE_RANGE --> WARM_ITER
    WARM_ITER --> CONCURRENCY
    
    CONCURRENCY --> TEE_OUTPUT
    TEE_OUTPUT --> LOG_RCCL
    TEE_OUTPUT --> LOG_UCCL
```

Sources: [rdma/run_rccl_test.sh:34-63]()

## Build System Test Integration

The UCCL build system includes comprehensive test compilation and execution targets to ensure code quality and functionality.

### Makefile Test Targets

```mermaid
graph TB
    subgraph "Source File Categories"
        LIB_SRC["lib_src = *.cc<br/>filter-out *_main.cc<br/>filter-out *_test.cc<br/>filter-out *_plugin.cc"]
        TEST_SRC["test_src = *_test.cc"]
        PLUGIN_SRC["nccl_plugin.cc"]
    end
    
    subgraph "Build Targets"
        TEST_BIN["test_bin = *_test"]
        LIB_OBJ["lib_obj = *.o"]
        PLUGIN_SO["libnccl-net-uccl.so"]
        STATIC_LIBS["librdma.a, librdma_plugin.a"]
    end
    
    subgraph "Compilation Rules"
        TEST_RULE["%_test: %_test.cc $(DEPS) $(lib_obj)"]
        OBJ_RULE["%.o: %.cc $(DEPS)"]
        PLUGIN_RULE["$(PLUGIN_SO): nccl_plugin.cc"]
    end
    
    subgraph "Build Dependencies"
        CUDA_HOME["CUDA_HOME?=/usr/local/cuda"]
        NCCL_HOME["NCCL_HOME:=../thirdparty/nccl"]
        INC_PATHS["-I./ -I$(CUDA_HOME)/include"]
        LIBS["libverbs, glog, gflags, gtest"]
    end
    
    LIB_SRC --> LIB_OBJ
    TEST_SRC --> TEST_BIN
    PLUGIN_SRC --> PLUGIN_SO
    
    TEST_RULE --> CUDA_HOME
    OBJ_RULE --> NCCL_HOME
    PLUGIN_RULE --> INC_PATHS
    INC_PATHS --> LIBS
```

Sources: [rdma/Makefile:15-46]()

### GPU Runtime Abstraction Testing

UCCL's testing infrastructure supports both CUDA and ROCm through a unified GPU runtime abstraction layer.

```mermaid
graph LR
    subgraph "GPU Runtime Header"
        GPU_RT_H["include/util/gpu_rt.h"]
    end
    
    subgraph "CUDA Support"
        CUDA_DEFS["#ifndef __HIP_PLATFORM_AMD__<br/>cuda.h, cuda_runtime.h<br/>gpuSuccess = cudaSuccess"]
    end
    
    subgraph "HIP/ROCm Support"
        HIP_DEFS["#else<br/>hip/hip_runtime.h<br/>gpuSuccess = hipSuccess"]
    end
    
    subgraph "Unified Macros"
        GPU_MACROS["gpuStream_t, gpuMalloc<br/>gpuMemcpy, gpuEvent_t<br/>GPU_RT_CHECK()"]
    end
    
    GPU_RT_H --> CUDA_DEFS
    GPU_RT_H --> HIP_DEFS
    CUDA_DEFS --> GPU_MACROS
    HIP_DEFS --> GPU_MACROS
```

Sources: [include/util/gpu_rt.h:1-146]()

## Performance Metrics and Analysis

UCCL benchmarks provide comprehensive performance metrics including bandwidth, latency, and scalability measurements across different message sizes and communication patterns.

### Benchmark Output Format

All UCCL benchmarks follow a consistent output format for easy comparison and analysis:

| Metric | Unit | Calculation | Purpose |
|--------|------|-------------|---------|
| Bandwidth (Gbps) | Gigabits/second | `(total_bytes * 8) / elapsed / 1e9` | Network utilization |
| Throughput (GB/s) | Gigabytes/second | `total_bytes / elapsed / 1e9` | Data transfer rate |
| Latency (s) | Seconds | `elapsed / iterations` | Per-operation timing |

### Message Size Testing Matrix

```mermaid
graph LR
    subgraph "Default Size Range"
        SMALL["256B - 4KB<br/>Latency Focus"]
        MEDIUM["16KB - 1MB<br/>Bandwidth Ramp"]
        LARGE["10MB - 100MB<br/>Peak Throughput"]
    end
    
    subgraph "Test Configurations"
        ITERS["iterations: 1000<br/>Statistical Significance"]
        WARMUP["warmup: 1 iteration<br/>Cache Priming"]
        KVBLOCKS["kvblocks: 1-N<br/>Vectorized Operations"]
    end
    
    SMALL --> ITERS
    MEDIUM --> WARMUP
    LARGE --> KVBLOCKS
```

Sources: [p2p/benchmarks/benchmark_uccl.py:435-446](), [p2p/benchmarks/benchmark_nixl.py:564-576]()

---

# Page: Performance Benchmarks

# Performance Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ep/bench/alltoall/.gitignore](ep/bench/alltoall/.gitignore)
- [ep/bench/alltoall/Makefile](ep/bench/alltoall/Makefile)
- [ep/bench/alltoall/benchmark.cpp](ep/bench/alltoall/benchmark.cpp)
- [ep/bench/alltoall/efa_alltoall_results.md](ep/bench/alltoall/efa_alltoall_results.md)
- [ep/bench/alltoall/launch_bench.py](ep/bench/alltoall/launch_bench.py)
- [ep/bench/alltoall/test_alltoall.cpp](ep/bench/alltoall/test_alltoall.cpp)
- [ep/bench/alltoall/test_alltoall_rail.cpp](ep/bench/alltoall/test_alltoall_rail.cpp)
- [ep/bench/buffer.py](ep/bench/buffer.py)
- [ep/bench/test_internode.py](ep/bench/test_internode.py)
- [ep/bench/test_low_latency.py](ep/bench/test_low_latency.py)
- [ep/bench/utils.py](ep/bench/utils.py)
- [ep/include/common.hpp](ep/include/common.hpp)
- [ep/include/ep_configs.cuh](ep/include/ep_configs.cuh)
- [ep/include/ep_utils.cuh](ep/include/ep_utils.cuh)
- [ep/include/proxy.hpp](ep/include/proxy.hpp)
- [ep/include/proxy_ctx.hpp](ep/include/proxy_ctx.hpp)
- [ep/include/rdma.hpp](ep/include/rdma.hpp)
- [ep/include/uccl_ibgda.cuh](ep/include/uccl_ibgda.cuh)
- [ep/include/uccl_proxy.hpp](ep/include/uccl_proxy.hpp)
- [ep/src/internode.cu](ep/src/internode.cu)
- [ep/src/internode_ll.cu](ep/src/internode_ll.cu)
- [ep/src/proxy.cpp](ep/src/proxy.cpp)
- [ep/src/rdma.cpp](ep/src/rdma.cpp)
- [ep/src/uccl_ep.cc](ep/src/uccl_ep.cc)
- [ep/src/uccl_proxy.cpp](ep/src/uccl_proxy.cpp)
- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nccl_allgather.py](p2p/benchmarks/benchmark_nccl_allgather.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_allgather.py](p2p/benchmarks/benchmark_uccl_allgather.py)
- [p2p/benchmarks/benchmark_uccl_alltoall.py](p2p/benchmarks/benchmark_uccl_alltoall.py)
- [p2p/benchmarks/benchmark_uccl_collective.py](p2p/benchmarks/benchmark_uccl_collective.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/collective.py](p2p/collective.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/rdma/tests/test_efa_endpoint.cpp](p2p/rdma/tests/test_efa_endpoint.cpp)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/tests/test_util_interval_tree.py](p2p/tests/test_util_interval_tree.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [p2p/utils.py](p2p/utils.py)

</details>



This document describes the comprehensive performance benchmarking tools provided by UCCL for evaluating communication performance across different transport backends and comparing against baseline implementations like NCCL. The benchmarks measure throughput (GB/s), bandwidth (Gbps), and latency across various message sizes and communication patterns.

For information about the underlying P2P communication architecture being benchmarked, see [P2P Communication Engine](#3). For details about transport backend implementations, see [Transport Backends](#2).

## Benchmark Categories

UCCL provides several categories of benchmarks to evaluate different aspects of communication performance:

```mermaid
graph TB
    subgraph "UCCL Performance Benchmarks"
        P2P["P2P Engine Benchmarks<br/>benchmark_uccl.py"]
        READ["One-Sided Read Benchmarks<br/>benchmark_uccl_read.py"]
        NIXL["NIXL Backend Comparison<br/>benchmark_nixl.py"]
        NCCL_CMP["NCCL Comparison<br/>benchmark_nccl.py"]
    end
    
    subgraph "Communication Patterns"
        SYNC["Synchronous Operations<br/>ep.send/ep.recv"]
        ASYNC["Asynchronous Operations<br/>ep.send_async/ep.recv_async"]
        DUAL["Bidirectional Transfer<br/>dual mode"]
        IPC["Local IPC Transfer<br/>ep.send_ipc/ep.recv_ipc"]
        VECTORED["Vectored Operations<br/>ep.sendv/ep.recvv"]
        RDMA_READ["One-Sided Read<br/>ep.readv/ep.read_async"]
    end
    
    subgraph "Backend Targets"
        UCCL_P2P["uccl.p2p.Endpoint"]
        UCCL_RDMA["UCCL RDMA Transport"] 
        NCCL_REF["torch.distributed"]
        UCX_REF["nixl_agent + UCX"]
        MOONCAKE["nixl_agent + Mooncake"]
    end
    
    P2P --> SYNC
    P2P --> ASYNC
    P2P --> DUAL
    P2P --> IPC
    P2P --> VECTORED
    
    READ --> RDMA_READ
    READ --> UCCL_P2P
    
    NIXL --> UCCL_RDMA
    NIXL --> UCX_REF
    NIXL --> MOONCAKE
    
    NCCL_CMP --> NCCL_REF
```

Sources: [p2p/benchmarks/benchmark_uccl.py:1-546](), [p2p/benchmarks/benchmark_uccl_read.py:1-213](), [p2p/benchmarks/benchmark_nixl.py:1-636](), [p2p/benchmarks/benchmark_nccl.py:1-243]()

## Primary P2P Benchmarks

The `benchmark_uccl.py` script provides comprehensive benchmarking of the UCCL P2P Engine with support for multiple communication patterns and measurement modes.

### P2P Benchmark Architecture

```mermaid
graph TB
    subgraph "benchmark_uccl.py Architecture"
        MAIN["main()"]
        DIST_INIT["dist.init_process_group('gloo')"]
        EP_CREATE["p2p.Endpoint(local_gpu_idx, num_cpus)"]
        
        subgraph "Benchmark Modes"
            STD["Standard Mode<br/>_run_client/_run_server"]
            DUAL_MODE["Dual Mode<br/>_run_client_dual/_run_server_dual"]
            IPC_MODE["IPC Mode<br/>_run_client_ipc/_run_server_ipc"]
        end
        
        subgraph "Core Operations"
            SYNC_OPS["Synchronous<br/>ep.send/ep.recv"]
            ASYNC_OPS["Asynchronous<br/>ep.send_async/ep.recv_async"]
            VEC_OPS["Vectored<br/>ep.sendv/ep.recvv"]
            IPC_OPS["IPC Operations<br/>ep.send_ipc/ep.recv_ipc"]
        end
        
        subgraph "Memory Management"
            BUF_CREATE["_make_buffer(size, device, gpu_idx)"]
            MEM_REG["ep.reg(ptr, size)"]
            TORCH_BUF["torch.ones(n_elems, device='cuda')"]
            NUMPY_BUF["np.ones(n_elems, dtype=np.float32)"]
        end
    end
    
    MAIN --> DIST_INIT
    DIST_INIT --> EP_CREATE
    EP_CREATE --> STD
    EP_CREATE --> DUAL_MODE
    EP_CREATE --> IPC_MODE
    
    STD --> SYNC_OPS
    STD --> ASYNC_OPS
    STD --> VEC_OPS
    
    DUAL_MODE --> ASYNC_OPS
    IPC_MODE --> IPC_OPS
    
    SYNC_OPS --> BUF_CREATE
    ASYNC_OPS --> BUF_CREATE
    BUF_CREATE --> MEM_REG
    BUF_CREATE --> TORCH_BUF
    BUF_CREATE --> NUMPY_BUF
```

Sources: [p2p/benchmarks/benchmark_uccl.py:417-538](), [p2p/benchmarks/benchmark_uccl.py:24-38](), [p2p/benchmarks/benchmark_uccl.py:51-124]()

### Benchmark Execution Flow

The P2P benchmarks follow a standardized execution pattern across all communication modes:

| Phase | Client Role | Server Role | Key Functions |
|-------|-------------|-------------|---------------|
| Setup | `ep.connect()` | `ep.accept()` | Connection establishment |
| Warmup | `ep.send()` x1 | `ep.recv()` x1 | Cache warming |
| Timing Loop | `ep.send()` x iters | `ep.recv()` x iters | Performance measurement |
| Cleanup | Automatic | Automatic | Resource deallocation |

Key measurement code in the timing loops:
- Start timer: `time.perf_counter()` [p2p/benchmarks/benchmark_uccl.py:161]()
- Core operation: `ep.send(conn_id, mr_id, ptr, size)` [p2p/benchmarks/benchmark_uccl.py:174]()
- End timer: `time.perf_counter()` [p2p/benchmarks/benchmark_uccl.py:177]()
- Metrics calculation: `gbps = (total_sent * 8) / elapsed / 1e9` [p2p/benchmarks/benchmark_uccl.py:179]()

Sources: [p2p/benchmarks/benchmark_uccl.py:127-198](), [p2p/benchmarks/benchmark_uccl.py:51-124]()

## One-Sided Read Benchmarks

The `benchmark_uccl_read.py` script specifically tests RDMA read operations, which require RC (Reliable Connection) mode and provide one-sided memory access capabilities.

### Read Benchmark Architecture

```mermaid
graph TB
    subgraph "benchmark_uccl_read.py Architecture"
        ENV_SET["os.environ['UCCL_RCMODE'] = '1'"]
        MAIN["main()"]
        EP_CREATE["p2p.Endpoint(local_gpu_idx, num_cpus)"]
        
        subgraph "Read Workflow"
            SERVER_FLOW["_run_server_read()"]
            CLIENT_FLOW["_run_client_recv()"]
            
            subgraph "Server Operations"
                ACCEPT["ep.accept()"]
                ADVERTISE["ep.advertisev(conn_id, mr_id_v, ptr_v, size_v)"]
                SEND_FIFO["dist.send(torch.ByteTensor(fifo_blob))"]
            end
            
            subgraph "Client Operations"  
                CONNECT["ep.connect(ip, r_gpu, remote_port)"]
                RECV_FIFO["dist.recv(fifo_blob, src=peer)"]
                READ_OP["ep.readv(conn_id, mr_id_v, ptr_v, size_v, fifo_blob_v)"]
                READ_ASYNC["ep.read_async(conn_id, mr_id, ptr, size, fifo_blob)"]
            end
        end
        
        subgraph "Memory Management"
            MAKE_BUF["_make_buffer(n_bytes, device, gpu)"]
            REG_MEM["ep.reg(ptr, size_per_block)"]
        end
    end
    
    ENV_SET --> MAIN
    MAIN --> EP_CREATE
    EP_CREATE --> SERVER_FLOW
    EP_CREATE --> CLIENT_FLOW
    
    SERVER_FLOW --> ACCEPT
    ACCEPT --> ADVERTISE  
    ADVERTISE --> SEND_FIFO
    
    CLIENT_FLOW --> CONNECT
    CONNECT --> RECV_FIFO
    RECV_FIFO --> READ_OP
    RECV_FIFO --> READ_ASYNC
    
    ADVERTISE --> MAKE_BUF
    READ_OP --> MAKE_BUF
    MAKE_BUF --> REG_MEM
```

The read benchmark requires `UCCL_RCMODE=1` environment variable to enable RC mode for one-sided operations [p2p/benchmarks/benchmark_uccl_read.py:10](). The server advertises memory regions using `ep.advertisev()` [p2p/benchmarks/benchmark_uccl_read.py:62](), and the client performs reads using `ep.readv()` [p2p/benchmarks/benchmark_uccl_read.py:108]() or `ep.read_async()` [p2p/benchmarks/benchmark_uccl_read.py:99-106]().

Sources: [p2p/benchmarks/benchmark_uccl_read.py:41-68](), [p2p/benchmarks/benchmark_uccl_read.py:70-133](), [p2p/benchmarks/benchmark_uccl_read.py:22-30]()

## NIXL Backend Comparison Benchmarks

The `benchmark_nixl.py` script compares UCCL performance against other high-performance communication backends through the NIXL interface.

### Backend Comparison Matrix

```mermaid
graph TB
    subgraph "NIXL Benchmark Framework"
        NIXL_AGENT["nixl_agent(role, config)"]
        
        subgraph "Backend Configurations"
            UCCL_CFG["nixl_agent_config(backends=['Uccl'])"]
            MOONCAKE_CFG["nixl_agent_config(backends=['Mooncake'])"] 
            UCX_CFG["nixl_agent_config(cuda=True, tcp=True, port)"]
        end
        
        subgraph "Communication Modes"
            SINGLE["Single Direction<br/>start_transfer()"]
            DUAL_DIR["Dual Direction<br/>start_transfer_dual()"]
        end
        
        subgraph "Transfer Operations"
            WRITE_OP["WRITE Operations<br/>agent.transfer(handle)"]
            READ_OP["READ Operations<br/>agent.transfer(handle)"]
        end
        
        subgraph "Synchronization Methods"
            ZMQ_SYNC["ZMQ Sockets<br/>Mooncake/UCCL"]
            UCX_SYNC["UCX Metadata<br/>UCX Backend"]
        end
    end
    
    NIXL_AGENT --> UCCL_CFG
    NIXL_AGENT --> MOONCAKE_CFG
    NIXL_AGENT --> UCX_CFG
    
    UCCL_CFG --> SINGLE
    MOONCAKE_CFG --> SINGLE
    UCX_CFG --> SINGLE
    UCX_CFG --> DUAL_DIR
    
    SINGLE --> WRITE_OP
    SINGLE --> READ_OP
    DUAL_DIR --> WRITE_OP
    
    UCCL_CFG --> ZMQ_SYNC
    MOONCAKE_CFG --> ZMQ_SYNC
    UCX_CFG --> UCX_SYNC
```

Sources: [p2p/benchmarks/benchmark_nixl.py:76-96](), [p2p/benchmarks/benchmark_nixl.py:99-110](), [p2p/benchmarks/benchmark_nixl.py:247-328]()

### NIXL Transfer Workflow

The NIXL benchmarks implement a sophisticated transfer workflow with backend-specific optimizations:

1. **Agent Creation**: Backend-specific agent initialization [p2p/benchmarks/benchmark_nixl.py:80-82]()
2. **Memory Registration**: `agent.register_memory(descs)` [p2p/benchmarks/benchmark_nixl.py:84]()
3. **Metadata Exchange**: ZMQ or UCX-based synchronization [p2p/benchmarks/benchmark_nixl.py:87-94]()
4. **Transfer Initialization**: `agent.initialize_xfer(operation, local_descs, remote_descs, peer)` [p2p/benchmarks/benchmark_nixl.py:160-162]()
5. **Transfer Execution**: `agent.transfer(transfer_handle)` [p2p/benchmarks/benchmark_nixl.py:217]()
6. **Completion Polling**: `agent.check_xfer_state(transfer_handle)` [p2p/benchmarks/benchmark_nixl.py:220]()

Sources: [p2p/benchmarks/benchmark_nixl.py:129-164](), [p2p/benchmarks/benchmark_nixl.py:213-230]()

### NIXL Transfer Types and Backend Support

The NIXL benchmarks support different transfer patterns based on backend capabilities:

| Backend | Single Direction | Dual Direction | Sync Method | Transfer Types |
|---------|-----------------|----------------|-------------|---------------|
| UCCL | ✓ | ✗ | ZMQ | READ/WRITE |
| Mooncake | ✓ | ✗ | ZMQ | READ/WRITE |
| UCX | ✓ | ✓ | UCX Metadata | READ/WRITE |

The dual direction transfer in `start_transfer_dual()` creates symmetric bidirectional WRITE operations where both endpoints simultaneously write to each other [p2p/benchmarks/benchmark_nixl.py:427-517](). This is only supported with UCX backend due to its symmetric connection establishment model.

Sources: [p2p/benchmarks/benchmark_nixl.py:427-434](), [p2p/benchmarks/benchmark_nixl.py:609-614]()

## NCCL Performance Comparison

The `benchmark_nccl.py` provides baseline performance comparisons against PyTorch's distributed communication primitives.

### NCCL vs UCCL Comparison Framework

```mermaid
graph TB
    subgraph "NCCL Benchmark Structure"
        TORCH_DIST["torch.distributed"]
        
        subgraph "Backend Selection"
            NCCL_GPU["backend='nccl' (GPU)"]
            GLOO_CPU["backend='gloo' (CPU)"]
        end
        
        subgraph "Communication Primitives"
            SEND_RECV["dist.send/dist.recv"]
            ASYNC_P2P["dist.isend/dist.irecv"]
            BATCH_P2P["dist.batch_isend_irecv"]
        end
        
        subgraph "Buffer Management"
            TORCH_GPU["torch.ones(device='cuda')"]
            NUMPY_CPU["np.ones(dtype=np.float32)"]
        end
        
        subgraph "Benchmark Modes"
            UNI_DIR["Unidirectional<br/>_run_client/_run_server"]
            BI_DIR["Bidirectional<br/>_run_client_dual/_run_server_dual"]
        end
    end
    
    TORCH_DIST --> NCCL_GPU
    TORCH_DIST --> GLOO_CPU
    
    NCCL_GPU --> SEND_RECV
    GLOO_CPU --> SEND_RECV
    SEND_RECV --> ASYNC_P2P
    ASYNC_P2P --> BATCH_P2P
    
    NCCL_GPU --> TORCH_GPU
    GLOO_CPU --> NUMPY_CPU
    
    SEND_RECV --> UNI_DIR
    BATCH_P2P --> BI_DIR
```

Sources: [p2p/benchmarks/benchmark_nccl.py:209-214](), [p2p/benchmarks/benchmark_nccl.py:35-61](), [p2p/benchmarks/benchmark_nccl.py:115-169]()

## GPU Runtime Abstraction

UCCL benchmarks support both CUDA and ROCm through a unified GPU runtime abstraction layer defined in [include/util/gpu_rt.h:1-146]().

### GPU Runtime Macros

```mermaid
graph TB
    subgraph "GPU Runtime Abstraction"
        GPU_RT_H["include/util/gpu_rt.h"]
        
        subgraph "CUDA Platform"
            CUDA_DEFS["#ifndef __HIP_PLATFORM_AMD__"]
            CUDA_MACROS["gpuSuccess -> cudaSuccess<br/>gpuMalloc -> cudaMalloc<br/>gpuMemcpy -> cudaMemcpy<br/>gpuStream_t -> cudaStream_t"]
        end
        
        subgraph "ROCm Platform" 
            HIP_DEFS["#ifdef __HIP_PLATFORM_AMD__"]
            HIP_MACROS["gpuSuccess -> hipSuccess<br/>gpuMalloc -> hipMalloc<br/>gpuMemcpy -> hipMemcpy<br/>gpuStream_t -> hipStream_t"]
        end
        
        subgraph "Error Handling"
            GPU_CHECK["GPU_RT_CHECK(call)"]
            GPU_ERRORS["GPU_RT_CHECK_ERRORS(msg)"]
        end
    end
    
    GPU_RT_H --> CUDA_DEFS
    GPU_RT_H --> HIP_DEFS
    
    CUDA_DEFS --> CUDA_MACROS
    HIP_DEFS --> HIP_MACROS
    
    GPU_RT_H --> GPU_CHECK
    GPU_RT_H --> GPU_ERRORS
```

The benchmarks use this abstraction to work seamlessly across NVIDIA and AMD GPU platforms. Buffer allocation in benchmarks uses `torch.ones(device='cuda')` for PyTorch tensors [p2p/benchmarks/benchmark_uccl.py:29]() while error checking uses `GPU_RT_CHECK()` macros [include/util/gpu_rt.h:126-134]() in the underlying C++ implementation.

Sources: [include/util/gpu_rt.h:1-146](), [p2p/benchmarks/benchmark_uccl.py:24-38]()

## Performance Metrics and Analysis

### Standard Metrics Calculation

All UCCL benchmarks report consistent performance metrics:

| Metric | Formula | Units | Purpose |
|--------|---------|--------|---------|
| Bandwidth | `(total_bytes * 8) / elapsed_time / 1e9` | Gbps | Network utilization |
| Throughput | `total_bytes / elapsed_time / 1e9` | GB/s | Data transfer rate |
| Latency | `elapsed_time / iterations` | seconds | Per-operation time |

### Message Size Patterns

Default benchmark configurations test across logarithmic message size progression:

```python
default_sizes = [256, 1024, 4096, 16384, 65536, 262144, 
                1048576, 10485760, 16777216, 104857600]  # bytes
```

This range covers small messages (256B) through large transfers (100MB) to characterize performance across different communication regimes.

Sources: [p2p/benchmarks/benchmark_uccl.py:435-446](), [p2p/benchmarks/benchmark_nccl.py:188-199](), [p2p/benchmarks/benchmark_nixl.py:564-575]()

## Running Benchmarks

### P2P Engine Benchmarks

```bash
# Standard P2P benchmark (2 processes)
torchrun --nproc_per_node=2 p2p/benchmarks/benchmark_uccl.py \
  --local-gpu-idx 0 --device gpu --iters 1000

# Dual bidirectional benchmark
torchrun --nproc_per_node=2 p2p/benchmarks/benchmark_uccl.py \
  --dual --async-api

# IPC local communication benchmark  
torchrun --nproc_per_node=2 p2p/benchmarks/benchmark_uccl.py \
  --ipc --device gpu
```

### NIXL Backend Comparison

```bash
# UCCL vs UCX comparison
python p2p/benchmarks/benchmark_nixl.py --role server --backend uccl &
python p2p/benchmarks/benchmark_nixl.py --role client --backend uccl \
  --remote-ip <server_ip>

# Dual direction UCX benchmark
python p2p/benchmarks/benchmark_nixl.py --role server --backend ucx --dual &
python p2p/benchmarks/benchmark_nixl.py --role client --backend ucx \
  --remote-ip <server_ip> --dual
```

### GPU-Driven Benchmarks

```bash
# Run GPU-driven proxy benchmarks
python gpu_driven/tests/test_local_proxy.py
```

Sources: [p2p/benchmarks/benchmark_uccl.py:486-537](), [p2p/benchmarks/benchmark_nixl.py:536-636](), [gpu_driven/tests/test_local_proxy.py:63-74]()

---

# Page: Test Suites and CI

# Test Suites and CI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/workflows/clang-format-check.yml](.github/workflows/clang-format-check.yml)
- [.github/workflows/uccl-build-test.yml](.github/workflows/uccl-build-test.yml)
- [README.md](README.md)
- [build.sh](build.sh)
- [collective/efa/README.md](collective/efa/README.md)
- [collective/rdma/README.md](collective/rdma/README.md)
- [docker/Dockerfile.cuda](docker/Dockerfile.cuda)
- [docker/Dockerfile.efa](docker/Dockerfile.efa)
- [docker/Dockerfile.gh](docker/Dockerfile.gh)
- [docker/Dockerfile.rocm](docker/Dockerfile.rocm)
- [docs/wheels.md](docs/wheels.md)
- [ep/Makefile](ep/Makefile)
- [ep/README.md](ep/README.md)
- [ep/bench/run_ep.sh](ep/bench/run_ep.sh)
- [ep/install_deps.sh](ep/install_deps.sh)
- [ep/setup.py](ep/setup.py)
- [ep/src/common.cpp](ep/src/common.cpp)
- [format.sh](format.sh)
- [include/util/gpu_rt.h](include/util/gpu_rt.h)
- [include/util/util.h](include/util/util.h)
- [p2p/Makefile](p2p/Makefile)
- [p2p/README.md](p2p/README.md)
- [p2p/benchmarks/benchmark_nccl.py](p2p/benchmarks/benchmark_nccl.py)
- [p2p/benchmarks/benchmark_nixl.py](p2p/benchmarks/benchmark_nixl.py)
- [p2p/benchmarks/benchmark_uccl.py](p2p/benchmarks/benchmark_uccl.py)
- [p2p/benchmarks/benchmark_uccl_readwrite.py](p2p/benchmarks/benchmark_uccl_readwrite.py)
- [p2p/engine.cc](p2p/engine.cc)
- [p2p/engine.h](p2p/engine.h)
- [p2p/tests/test_engine_onesided_ipc.py](p2p/tests/test_engine_onesided_ipc.py)
- [p2p/uccl_engine.cc](p2p/uccl_engine.cc)
- [p2p/uccl_engine.h](p2p/uccl_engine.h)
- [scripts/efa_monitor.sh](scripts/efa_monitor.sh)
- [scripts/node_ips/amd.txt](scripts/node_ips/amd.txt)
- [scripts/node_ips/tpu_2.txt](scripts/node_ips/tpu_2.txt)
- [scripts/setup_all.py](scripts/setup_all.py)
- [scripts/setup_nic.sh](scripts/setup_nic.sh)

</details>



UCCL's test infrastructure comprises GitHub Actions CI workflows, comprehensive test suites using pytest and torchrun, and multi-node testing utilities. The testing framework validates code formatting, builds across platforms, and executes distributed communication tests on GPU clusters.

For performance benchmarking results, see page 7.1. For build system configuration, see page 5.

## GitHub Actions CI Workflows

UCCL uses GitHub Actions for continuous integration, enforcing code formatting standards and validating builds on remote GPU hosts. CI workflows run on push to main and pull request events.

### Code Formatting Checks

**Workflow: clang-format-check.yml**

The formatting workflow validates C++ and Python code style using clang-format-14 and black:

```mermaid
graph TB
    subgraph "Trigger Events"
        push_main["push to main branch"]
        pull_request["pull_request to main"]
    end
    
    subgraph "C++ Formatting Job"
        checkout_cpp["Checkout code<br/>actions/checkout@v4"]
        install_clang["Install clang-format-14<br/>apt-get install"]
        check_cpp["Check C++ formatting<br/>clang-format --dry-run --Werror"]
    end
    
    subgraph "Python Formatting Job"
        checkout_py["Checkout code<br/>actions/checkout@v4"]
        setup_python["Setup Python 3.10<br/>actions/setup-python@v4"]
        install_black["pip install black"]
        check_python["Check Python formatting<br/>black --check"]
    end
    
    subgraph "Target Directories"
        cpp_dirs["DIRECTORIES:<br/>collective, ep, experimental, p2p, include"]
        cpp_exclude["EXCLUDE:<br/>collective/afxdp/lib"]
        python_dirs["PYTHON_DIRS:<br/>p2p, ep"]
        python_exclude["EXCLUDES:<br/>thirdparty, docs, build"]
    end
    
    push_main --> checkout_cpp
    pull_request --> checkout_cpp
    push_main --> checkout_py
    pull_request --> checkout_py
    
    checkout_cpp --> install_clang
    install_clang --> check_cpp
    check_cpp --> cpp_dirs
    check_cpp --> cpp_exclude
    
    checkout_py --> setup_python
    setup_python --> install_black
    install_black --> check_python
    check_python --> python_dirs
    check_python --> python_exclude
```

The workflow checks file extensions `cpp`, `cxx`, `cc`, `h`, `hpp`, `cu`, `cuh` for C++ code, excluding the AF_XDP library directory. Python formatting checks apply to `p2p` and `ep` directories, excluding thirdparty dependencies.

Sources: [.github/workflows/clang-format-check.yml:1-91]()

### Remote Build and Verification

**Workflow: uccl-build-test.yml**

The build workflow executes on a remote GPU host (l4-sky-test-01) to validate UCCL installation:

```mermaid
graph TB
    subgraph "Workflow Triggers"
        push_event["push to main"]
        pr_event["pull_request to main<br/>(non-fork, non-draft)"]
    end
    
    subgraph "Concurrency Control"
        concurrency_group["group: remote-uccl-build"]
        cancel_in_progress["cancel-in-progress: false"]
    end
    
    subgraph "SSH Setup"
        checkout["Checkout code<br/>actions/checkout@v4"]
        setup_ssh["Setup SSH keys<br/>L4_SSH_KEY secret"]
        ssh_config["Configure SSH host<br/>l4-sky-test-01"]
        ssh_keyscan["Add to known_hosts<br/>4.14.153.89"]
    end
    
    subgraph "Code Synchronization"
        git_submodule["git submodule update<br/>--init --recursive thirdparty/nccl"]
        rsync_code["rsync -az --delete<br/>ep, collective/rdma, p2p"]
    end
    
    subgraph "Remote Build"
        conda_init["source miniconda3/etc/profile.d/conda.sh"]
        conda_env["conda create -y -n uccl python=3.11"]
        conda_activate["conda activate uccl"]
        build_script["./build_and_install.sh cuda all 3.11"]
        verify_install["grep 'Successfully installed uccl-0.0.1.post4'"]
    end
    
    subgraph "Artifact Collection"
        fetch_log["scp build.log"]
        upload_artifact["actions/upload-artifact@v4<br/>name: build-log"]
    end
    
    push_event --> concurrency_group
    pr_event --> concurrency_group
    concurrency_group --> checkout
    cancel_in_progress --> checkout
    
    checkout --> setup_ssh
    setup_ssh --> ssh_config
    ssh_config --> ssh_keyscan
    
    ssh_keyscan --> git_submodule
    git_submodule --> rsync_code
    
    rsync_code --> conda_init
    conda_init --> conda_env
    conda_env --> conda_activate
    conda_activate --> build_script
    build_script --> verify_install
    
    verify_install --> fetch_log
    fetch_log --> upload_artifact
```

The workflow uses SSH key authentication stored in GitHub secrets to access the remote host at `4.14.153.89`. It creates a conda environment, builds UCCL with CUDA support, and verifies successful installation by checking build logs.

Sources: [.github/workflows/uccl-build-test.yml:1-96]()

### Local Formatting Script

The `format.sh` script provides local code formatting before committing:

```bash
# Format C++ files with clang-format-14
./format.sh

# Validates clang-format version is 14
# Formats files in: collective, ep, p2p, include, experimental
# Excludes: collective/afxdp/lib
# Formats Python files in: p2p, ep with black
# Excludes: thirdparty, docs, build
```

The script ensures code style consistency before CI checks run, preventing formatting-related CI failures.

Sources: [format.sh:1-74]()

## EP Test Suites

UCCL's Expert Parallelism (EP) system includes comprehensive test suites for low-latency dispatch/combine operations and internode communication. Tests use `torchrun` for distributed coordination and validate correctness across CUDA and ROCm platforms.

### Test Utilities

**File: thirdparty/DeepEP/tests/utils.py**

Core test utilities provide distributed initialization, benchmarking, and tensor manipulation functions:

```mermaid
graph TB
    subgraph "Distributed Initialization"
        init_dist["init_dist(local_rank, num_local_ranks)"]
        init_dist_under_torchrun["init_dist_under_torchrun(local_rank, num_local_ranks)"]
        detect_ib_hca["detect_ib_hca()"]
        dist_init_process_group["dist.init_process_group(backend='nccl')"]
    end
    
    subgraph "Benchmarking Functions"
        bench["bench(fn, num_warmups=50, num_tests=50)"]
        bench_kineto["bench_kineto(fn, kernel_names, num_tests=30)"]
        torch_cuda_Event["torch.cuda.Event(enable_timing=True)"]
        torch_profiler["torch.profiler.profile()"]
    end
    
    subgraph "Tensor Operations"
        per_token_cast_to_fp8["per_token_cast_to_fp8(x)"]
        per_token_cast_back["per_token_cast_back(x_fp8, x_scales)"]
        calc_diff["calc_diff(x, y)"]
        inplace_unique["inplace_unique(x, num_slots)"]
    end
    
    subgraph "Profiling Utilities"
        suppress_stdout_stderr["suppress_stdout_stderr context manager"]
        empty_suppress["empty_suppress context manager"]
        hash_tensor["hash_tensor(t)"]
    end
    
    init_dist --> dist_init_process_group
    init_dist_under_torchrun --> dist_init_process_group
    detect_ib_hca --> init_dist
    
    bench --> torch_cuda_Event
    bench_kineto --> torch_profiler
    bench_kineto --> suppress_stdout_stderr
    
    per_token_cast_to_fp8 --> calc_diff
    per_token_cast_back --> per_token_cast_to_fp8
    inplace_unique --> hash_tensor
```

Key utility functions:

| Function | Purpose | Returns |
|----------|---------|---------|
| `init_dist()` | Initialize torch.distributed with NCCL backend | rank, world_size, process_group |
| `bench()` | Measure kernel performance with warmup | avg_time, min_time, max_time |
| `bench_kineto()` | Profile kernels using PyTorch Kineto | kernel durations in seconds |
| `per_token_cast_to_fp8()` | Convert BF16 to FP8 with per-token scaling | fp8_tensor, scales |
| `calc_diff()` | Calculate similarity difference between tensors | float difference metric |
| `detect_ib_hca()` | Find InfiniBand HCA device (mlx5_*) | device name or None |

Sources: [thirdparty/DeepEP/tests/utils.py:1-247]()

### Low-Latency EP Tests

**File: thirdparty/DeepEP/tests/test_low_latency.py**

The low-latency test suite validates `deep_ep.Buffer` dispatch and combine operations with various configurations:

```mermaid
graph TB
    subgraph "Test Configuration"
        test_main["test_main(num_tokens, hidden, num_experts, num_topk)"]
        argparse_parser["argparse.ArgumentParser"]
        test_params["num_tokens=128<br/>hidden=7168<br/>num_topk=8<br/>num_experts=288"]
    end
    
    subgraph "Buffer Initialization"
        deep_ep_Buffer["deep_ep.Buffer(group, num_rdma_bytes)"]
        get_low_latency_rdma_size_hint["Buffer.get_low_latency_rdma_size_hint()"]
        buffer_config["low_latency_mode=True<br/>num_qps_per_rank=experts/ranks<br/>allow_nvlink_for_low_latency_mode"]
    end
    
    subgraph "Dispatch Testing"
        low_latency_dispatch["buffer.low_latency_dispatch(x, topk_idx, num_tokens, num_experts)"]
        dispatch_params["use_fp8=True/False<br/>round_scale=True/False<br/>use_ue8m0=True/False<br/>async_finish=True/False"]
        packed_recv_x["packed_recv_x, packed_recv_count, handle, event, hook"]
    end
    
    subgraph "Combine Testing"
        low_latency_combine["buffer.low_latency_combine(x, topk_idx, topk_weights, handle)"]
        combine_params["use_logfmt=True/False<br/>async_finish=True/False<br/>zero_copy=True/False"]
        combined_x["combined_x, event, hook"]
    end
    
    subgraph "Correctness Validation"
        check_expert_indices["Validate recv_count matches all_gather"]
        check_received_data["Verify data integrity across ranks"]
        check_combine_output["calc_diff(expected, actual) < 7e-4"]
    end
    
    subgraph "Performance Benchmarking"
        bench_dispatch_combine["bench(test_func) with barrier"]
        bench_kineto_separate["bench_kineto() for dispatch/combine"]
        bandwidth_calculation["(dispatch_bytes + combine_bytes) / time"]
    end
    
    test_main --> argparse_parser
    argparse_parser --> test_params
    
    test_params --> deep_ep_Buffer
    deep_ep_Buffer --> get_low_latency_rdma_size_hint
    get_low_latency_rdma_size_hint --> buffer_config
    
    buffer_config --> low_latency_dispatch
    low_latency_dispatch --> dispatch_params
    dispatch_params --> packed_recv_x
    
    packed_recv_x --> low_latency_combine
    low_latency_combine --> combine_params
    combine_params --> combined_x
    
    combined_x --> check_expert_indices
    check_expert_indices --> check_received_data
    check_received_data --> check_combine_output
    
    check_combine_output --> bench_dispatch_combine
    bench_dispatch_combine --> bench_kineto_separate
    bench_kineto_separate --> bandwidth_calculation
```

Test execution modes:

| Mode | Configuration | Purpose |
|------|--------------|---------|
| FP8 Dispatch | `use_fp8=True, round_scale=True/False` | Validate FP8 quantization with per-token scaling |
| Async Operations | `async_finish=True, return_recv_hook=True/False` | Test asynchronous dispatch/combine with hooks |
| Zero-Copy Combine | `zero_copy=True` | Validate in-place combine buffer usage |
| LogFMT Combine | `use_logfmt=True` | Test logarithmic format combination |
| Pressure Testing | `--pressure-test` | Run 1e9 iterations with random seeds |

Test execution with torchrun:

```bash
# Single-node 8-GPU test
torchrun --nproc_per_node=8 test_low_latency.py \
    --num-tokens 128 --hidden 7168 --num-topk 8 --num-experts 288

# Multi-node test
torchrun --nnodes=2 --nproc_per_node=8 \
    --master-addr=$MASTER_ADDR --master-port=$MASTER_PORT \
    test_low_latency.py --num-tokens 128 --hidden 7168
```

Sources: [thirdparty/DeepEP/tests/test_low_latency.py:1-229]()

### Internode EP Tests

**File: thirdparty/DeepEP/tests/test_internode.py**

Internode tests validate dispatch/combine operations across multiple nodes with NVLink and RDMA paths:

```mermaid
graph TB
    subgraph "Multi-Node Setup"
        test_loop["test_loop(local_rank, num_local_ranks, args)"]
        world_size["WORLD_SIZE environment variable"]
        local_world_size["LOCAL_WORLD_SIZE environment variable"]
        num_nodes["num_nodes = world_size / local_world_size"]
    end
    
    subgraph "Buffer Configuration"
        buffer_init["deep_ep.Buffer(group, 2e9, 1e9)"]
        num_qps["num_qps_per_rank=max(num_sms, experts/ranks)"]
        low_latency_mode["low_latency_mode for LL compatibility"]
    end
    
    subgraph "Dispatch Layout Testing"
        get_dispatch_layout["buffer.get_dispatch_layout(topk_idx, num_experts)"]
        layout_returns["num_tokens_per_rank<br/>num_tokens_per_rdma_rank<br/>num_tokens_per_expert<br/>is_token_in_rank"]
        layout_validation["torch.allclose() with reference"]
    end
    
    subgraph "Configuration Tuning"
        deep_ep_Config["deep_ep.Config(num_sms, nvl_chunk_size, nvl_buffer_size, rdma_chunk_size, rdma_buffer_size)"]
        tune_dispatch["Sweep nvl_chunk: 4-44, rdma_chunk: 4-32"]
        tune_combine["Sweep nvl_chunk: 1-7, rdma_chunk: 8-32"]
        bench_kineto_tuning["bench_kineto(lambda, ('dispatch', 'notify'))"]
    end
    
    subgraph "Data Format Testing"
        test_bf16["Test with BF16 data"]
        test_fp8["Test with FP8 data (per_token_cast_to_fp8)"]
        test_topk["Test with/without topk_idx and topk_weights"]
        cached_dispatch["Test cached dispatch with handle"]
    end
    
    subgraph "Correctness Validation"
        check_data["Validate received data by rank"]
        check_recv_count["Verify recv count matches all_gather"]
        check_topk_indices["Validate topk_idx mapping"]
        check_combine_diff["calc_diff(expected, actual) < 5e-6"]
    end
    
    test_loop --> world_size
    world_size --> local_world_size
    local_world_size --> num_nodes
    
    num_nodes --> buffer_init
    buffer_init --> num_qps
    num_qps --> low_latency_mode
    
    low_latency_mode --> get_dispatch_layout
    get_dispatch_layout --> layout_returns
    layout_returns --> layout_validation
    
    layout_validation --> deep_ep_Config
    deep_ep_Config --> tune_dispatch
    tune_dispatch --> tune_combine
    tune_combine --> bench_kineto_tuning
    
    bench_kineto_tuning --> test_bf16
    test_bf16 --> test_fp8
    test_fp8 --> test_topk
    test_topk --> cached_dispatch
    
    cached_dispatch --> check_data
    check_data --> check_recv_count
    check_recv_count --> check_topk_indices
    check_topk_indices --> check_combine_diff
```

Test scenarios validated:

| Scenario | Parameters | Validation |
|----------|-----------|------------|
| BF16 Dispatch | `x: torch.bfloat16` | Data integrity by rank, recv counts |
| FP8 Dispatch | `x: tuple (fp8_tensor, scales)` | Per-token quantization accuracy |
| With TopK | `topk_idx, topk_weights` | Expert index mapping, weight accumulation |
| Cached Dispatch | `handle` from previous call | Reuse layout without recomputation |
| Async Mode | `async_finish=True/False` | Event synchronization, hook execution |
| Combine with Bias | `bias: (bias_0, bias_1)` | Bias addition correctness |

Torchrun execution for multi-node testing:

```bash
# 2-node, 16-GPU test
torchrun --nnodes=2 --nproc_per_node=8 \
    --master-addr=$MASTER_ADDR --master-port=29500 \
    test_internode.py --num-tokens 4096 --hidden 7168 \
    --num-experts 256 --num-topk 8
```

Environment variables set by tests:

```bash
NCCL_IB_HCA=mlx5_0  # InfiniBand device (auto-detected)
WORLD_SIZE=16       # Total processes
LOCAL_WORLD_SIZE=8  # Processes per node
RANK=0-15           # Process rank
LOCAL_RANK=0-7      # Local process rank
```

Sources: [thirdparty/DeepEP/tests/test_internode.py:1-296]()

## Multi-Node Test Infrastructure

UCCL provides scripts for coordinating multi-node testing across clusters with different network configurations and platforms.

### Cluster Setup Script

**File: scripts/setup_all.py**

The `setup_all.py` script automates multi-node environment configuration using paramiko SSH:

```mermaid
graph TB
    subgraph "Configuration Targets"
        config_mapping["config_mapping dictionary"]
        aws_c5_afxdp["aws_c5_afxdp: AWS_C5, ens6, 3498"]
        aws_g4_afxdp["aws_g4_afxdp: AWS_G4, ens6, 3498"]
        clab_xl170_afxdp["clab_xl170_afxdp: CLAB_XL170, ens1f1np1, 1500"]
        tpu_v6e8_afxdp["tpu_v6e8_afxdp: TPU_V6E8, ens8, 1460"]
    end
    
    subgraph "Node Coordination"
        get_nodes["get_nodes(node_file)"]
        paramiko_SSHClient["paramiko.SSHClient() per node"]
        connect_nodes["client.connect(node)"]
    end
    
    subgraph "Build and Sync"
        make_afxdp["make_afxdp(make_macro, target)"]
        sync_repo["sync_repo(node_file)"]
        rsync_command["rsync from UCCL_HOME"]
    end
    
    subgraph "NIC Configuration"
        setup_nic["exec_command_no_wait(setup_nic.sh)"]
        parse_num_queues["parse_num_queues() from transport_config.h"]
        nic_params["net_dev, num_queues, mtu, afxdp_or_tcp"]
    end
    
    subgraph "AFXDP Daemon"
        afxdp_daemon["afxdp_daemon_main --logtostderr=1"]
        pkill_afxdp["sudo pkill afxdp_daemon"]
        signal_handler["SIGINT handler for cleanup"]
    end
    
    config_mapping --> aws_c5_afxdp
    config_mapping --> aws_g4_afxdp
    config_mapping --> clab_xl170_afxdp
    config_mapping --> tpu_v6e8_afxdp
    
    aws_c5_afxdp --> get_nodes
    get_nodes --> paramiko_SSHClient
    paramiko_SSHClient --> connect_nodes
    
    connect_nodes --> make_afxdp
    make_afxdp --> sync_repo
    sync_repo --> rsync_command
    
    rsync_command --> setup_nic
    setup_nic --> parse_num_queues
    parse_num_queues --> nic_params
    
    nic_params --> afxdp_daemon
    afxdp_daemon --> pkill_afxdp
    pkill_afxdp --> signal_handler
```

Configuration mapping structure:

| Target | Platform Macro | Network Device | MTU |
|--------|---------------|----------------|-----|
| `aws_c5_afxdp` | `AWS_C5` | `ens6` | 3498 |
| `aws_g4_afxdp` | `AWS_G4` | `ens6` | 3498 |
| `aws_g4metal_afxdp` | `AWS_G4METAL` | `enp199s0` | 3498 |
| `clab_xl170_afxdp` | `CLAB_XL170` | `ens1f1np1` | 1500 |
| `clab_d6515_afxdp` | `CLAB_D6515` | `enp65s0f0np0` | 3498 |
| `tpu_v6e8_afxdp` | `TPU_V6E8` | `ens8` | 1460 |

Usage examples:

```bash
# Setup AF_XDP on CloudLab XL170 cluster
python setup_all.py --target=clab_xl170_afxdp

# Setup TPU v6e8 cluster
python setup_all.py --target=tpu_v6e8_afxdp --node_file=node_ips/tpu_2.txt

# Sync repository only
python setup_all.py --target=setup_extra
```

Sources: [scripts/setup_all.py:1-169]()

### NIC Setup Script

**File: scripts/setup_nic.sh**

The `setup_nic.sh` script configures network interfaces for AFXDP or TCP modes:

```mermaid
graph TB
    subgraph "Script Parameters"
        NIC["NIC: Network device name"]
        NQUEUE["NQUEUE: Number of queues"]
        NIRQCORE["NIRQCORE: IRQ core count"]
        MTU["MTU: Maximum transmission unit"]
        MODE["MODE: afxdp or tcp"]
        PLATFORM["PLATFORM: aws, clab, ibm, tpu"]
    end
    
    subgraph "XDP Cleanup"
        unload_xdp["xdp-loader unload NIC --all"]
    end
    
    subgraph "Queue Configuration"
        ethtool_L["ethtool -L NIC combined NQUEUE"]
        ethtool_L_tpu["ethtool -L NIC rx/tx NQUEUE (TPU)"]
        ifconfig_mtu["ifconfig NIC mtu MTU up"]
    end
    
    subgraph "AFXDP Mode Setup"
        stop_irqbalance["service irqbalance stop"]
        ethtool_C_afxdp["ethtool -C NIC adaptive-rx off"]
        aws_afxdp["rx-usecs 0 tx-usecs 0 (AWS/IBM)"]
        clab_afxdp["rx-frames 1 tx-frames 1 (CloudLab)"]
    end
    
    subgraph "TCP Mode Setup"
        start_irqbalance["service irqbalance start"]
        ethtool_C_tcp["ethtool -C NIC adaptive-rx on"]
        aws_tcp["rx-usecs 20 tx-usecs 60 (AWS/IBM)"]
        clab_tcp["rx-usecs 8 rx-frames 128 (CloudLab)"]
    end
    
    subgraph "IRQ Affinity"
        msi_irqs["Detect MSI IRQs or VirtIO interrupts"]
        irq_start_cpu["irq_start_cpu = 3*NCPU/4 (default)"]
        set_smp_affinity["echo CPU > /proc/irq/IRQ/smp_affinity_list"]
    end
    
    NIC --> unload_xdp
    NQUEUE --> ethtool_L
    PLATFORM --> ethtool_L_tpu
    MTU --> ifconfig_mtu
    
    MODE --> stop_irqbalance
    MODE --> start_irqbalance
    
    stop_irqbalance --> ethtool_C_afxdp
    ethtool_C_afxdp --> aws_afxdp
    ethtool_C_afxdp --> clab_afxdp
    
    start_irqbalance --> ethtool_C_tcp
    ethtool_C_tcp --> aws_tcp
    ethtool_C_tcp --> clab_tcp
    
    unload_xdp --> msi_irqs
    msi_irqs --> irq_start_cpu
    irq_start_cpu --> set_smp_affinity
```

Platform-specific IRQ assignment:

```bash
# Default: Start at 3/4 of total CPUs
irq_start_cpu=$((NCPU / 4 * 3))

# AWS: Start at 1/4 (avoid conflicts with NCCL proxy)
irq_start_cpu=$((NCPU / 4))

# TPU: Start at 1/8
irq_start_cpu=$((NCPU / 8))
```

Sources: [scripts/setup_nic.sh:1-104]()

### Node Configuration Files

Cluster node specifications are stored in `scripts/node_ips/`:

**AMD GPU Cluster (scripts/node_ips/amd.txt):**
```
tw025
tw026
tw052
tw054
```

**TPU v6e8 Cluster (scripts/node_ips/tpu_2.txt):**
```
10.202.15.195
10.202.15.196
```

These files are used by `setup_all.py` to target specific node sets for configuration and testing.

Sources: [scripts/node_ips/amd.txt:1-4](), [scripts/node_ips/tpu_2.txt:1-2]()

## Test Configuration Management

Integration tests use standardized configuration files and environment variable management for consistent multi-node deployments.

### Node IP Configuration

Cluster node specifications are managed through text files in `scripts/node_ips/`:

| Configuration File | Purpose | Example Nodes |
|-------------------|---------|---------------|
| `amd.txt` | AMD GPU nodes | tw025, tw026, tw052, tw054 |

The AMD cluster configuration in [scripts/node_ips/amd.txt:1-4]() provides a 4-node setup for RCCL integration testing with HIP/ROCm environments.

### Environment Variable Framework

UCCL integration tests configure transport behavior through environment variables processed by utility functions:

```mermaid
graph TB
    subgraph "Environment Access"
        GetEnvVar["GetEnvVar()<br/>util.h:1045-1048"]
        UCCL_IB_HCA["UCCL_IB_HCA<br/>InfiniBand device filter"]
        NCCL_IB_HCA["NCCL_IB_HCA<br/>Fallback device specification"]
    end
    
    subgraph "UCCL Configuration"
        NUM_ENGINES["UCCL_NUM_ENGINES=4<br/>Engines per device"]
        PORT_ENTROPY["UCCL_PORT_ENTROPY=16<br/>QPs per engine"]
        CHUNK_SIZE_KB["UCCL_CHUNK_SIZE_KB=32<br/>Maximum chunk size"]
        RCMODE["UCCL_RCMODE=1<br/>RC vs UC transport mode"]
    end
    
    subgraph "Runtime Parameters"
        HIP_VISIBLE_DEVICES["HIP_VISIBLE_DEVICES=0,1,2,3,4,5,6,7<br/>GPU visibility"]
        GLOG_v["GLOG_v=0<br/>Logging verbosity level"]
        LD_LIBRARY_PATH["LD_LIBRARY_PATH<br/>Library path configuration"]
    end
    
    subgraph "Device Detection Functions"
        get_dev_numa_node["get_dev_numa_node()<br/>util.h:1077-1091"]
        pin_thread_to_numa["pin_thread_to_numa()<br/>util.h:1106-1143"]
        get_gpu_cards["get_gpu_cards()<br/>util.h:1235-1280"]
    end
    
    GetEnvVar --> UCCL_IB_HCA
    GetEnvVar --> NCCL_IB_HCA
    
    NUM_ENGINES --> HIP_VISIBLE_DEVICES
    PORT_ENTROPY --> GLOG_v
    CHUNK_SIZE_KB --> LD_LIBRARY_PATH
    RCMODE --> HIP_VISIBLE_DEVICES
    
    get_dev_numa_node --> pin_thread_to_numa
    pin_thread_to_numa --> get_gpu_cards
```

Sources: [include/util/util.h:1045-1280](), [rdma/run_rccl_test.sh:50-63]()

## Collective Communication Testing

UCCL provides comprehensive collective operation testing through both C++ transport tests and Python PyTorch integration benchmarks.

### Python Collective API Testing

The `benchmark_uccl_collective.py` validates high-level collective operations using PyTorch tensors:

```mermaid
graph TB
    subgraph "Test Scenarios"
        run_server["_run_server()<br/>benchmark_uccl_collective.py:47-80"]
        run_client["_run_client()<br/>benchmark_uccl_collective.py:82-107"]
        run_ring_benchmark["_run_ring_benchmark()<br/>benchmark_uccl_collective.py:225-308"]
        run_dual_benchmark["_run_dual_benchmark()<br/>benchmark_uccl_collective.py:170-223"]
    end
    
    subgraph "Collective Operations"
        collective_send["collective.send()<br/>Synchronous send operation"]
        collective_recv["collective.recv()<br/>Synchronous receive operation"] 
        collective_isend["collective.isend()<br/>Async send operation"]
        collective_irecv["collective.irecv()<br/>Async receive operation"]
        collective_wait["collective.wait()<br/>Request completion"]
    end
    
    subgraph "Memory Management"
        make_buffer["_make_buffer()<br/>GPU tensor allocation"]
        register_tensor["collective.register_tensor()<br/>Memory registration"]
        torch_cuda_tensor["torch.ones().cuda()<br/>CUDA tensor creation"]
    end
    
    subgraph "Distributed Coordination"
        init_collective["collective.init_collective()<br/>UCCL initialization"]
        torch_distributed["torch.distributed<br/>Process group coordination"]
        dist_barrier["dist.barrier()<br/>Synchronization barrier"]
    end
    
    run_server --> collective_recv
    run_client --> collective_send
    run_ring_benchmark --> collective_isend
    run_dual_benchmark --> collective_irecv
    
    collective_send --> make_buffer
    collective_recv --> register_tensor
    collective_isend --> torch_cuda_tensor
    collective_irecv --> collective_wait
    
    make_buffer --> torch_cuda_tensor
    register_tensor --> init_collective
    torch_cuda_tensor --> torch_distributed
    
    init_collective --> dist_barrier
    torch_distributed --> dist_barrier
```

### Transport-Level Testing

Low-level transport validation through `ucclRequest` and `PollCtx` structures:

```mermaid
graph TB
    subgraph "Request Management"
        ucclRequest["struct ucclRequest<br/>rdma_io.h:173-209"]
        PollCtx["struct PollCtx<br/>util.h:372-400"]
        uccl_wakeup["uccl_wakeup()<br/>util.h:402-406"]
        uccl_try_wakeup["uccl_try_wakeup()<br/>util.h:408-415"]
    end
    
    subgraph "Request Types"
        ReqTx["ReqTx<br/>Send request"]
        ReqRx["ReqRx<br/>Receive request"]
        ReqFlush["ReqFlush<br/>Flush operation"] 
        ReqTxRC["ReqTxRC<br/>RC send request"]
        ReqRxRC["ReqRxRC<br/>RC receive request"]
    end
    
    subgraph "Completion Tracking"
        poll_ctx["poll_ctx<br/>Request completion context"]
        num_unfinished["num_unfinished<br/>Outstanding request counter"]
        done_flag["done<br/>Completion flag"]
        fence_barrier["fence<br/>Memory barrier"]
    end
    
    ucclRequest --> ReqTx
    ucclRequest --> ReqRx
    ucclRequest --> ReqFlush
    ucclRequest --> ReqTxRC
    ucclRequest --> ReqRxRC
    
    PollCtx --> poll_ctx
    PollCtx --> num_unfinished
    PollCtx --> done_flag
    PollCtx --> fence_barrier
    
    uccl_wakeup --> PollCtx
    uccl_try_wakeup --> num_unfinished
    poll_ctx --> uccl_wakeup
```

### Performance Validation Framework

Integration tests measure throughput, latency, and correctness across different message sizes and communication patterns:

| Test Mode | Function | Purpose | Metrics |
|-----------|----------|---------|---------|
| Basic | `server_basic()`, `client_basic()` | Correctness validation | Data integrity verification |
| Latency | `server_lat()`, `client_lat()` | Latency measurement | P50, P90, P99 percentiles |
| Throughput | `server_tpt()`, `client_tpt()` | Bandwidth testing | Gbps, GB/s measurements |
| Bidirectional | `client_tpt()` with dual flows | Full-duplex testing | Simultaneous send/recv |

Sources: [p2p/benchmarks/benchmark_uccl_collective.py:1-446](), [rdma/rdma_io.h:173-209](), [include/util/util.h:372-415](), [rdma/transport_test.cc:51-298]()

## Specialized Test Environments

### HPC Cluster Integration

HPC Fund cluster testing uses Slurm integration with `run_rccl_test_hpcfund.sh`:

```mermaid
graph TB
    subgraph "Slurm Integration"
        SALLOC["salloc -N 2 -n 2 -p mi2104x"]
        NODEFILE["scontrol show hostnames<br/>$SLURM_JOB_NODELIST"]
    end
    
    subgraph "AMD GPU Configuration"
        MI2104X["mi2104x partition<br/>GPU 0,1,6,7 mapping"]
        MLX5_HCA["mlx5_0:1, mlx5_2:1<br/>HCA assignment"]
    end
    
    subgraph "UCCL Parameters"
        ENGINES_1["UCCL_NUM_ENGINES=1"]
        ENTROPY_256["UCCL_PORT_ENTROPY=256"]
        CHUNK_128["UCCL_CHUNK_SIZE_KB=128"]
    end
    
    SALLOC --> NODEFILE
    NODEFILE --> MI2104X
    MI2104X --> MLX5_HCA
    
    MLX5_HCA --> ENGINES_1
    ENGINES_1 --> ENTROPY_256
    ENTROPY_256 --> CHUNK_128
```

### AF_XDP Cloud Testing

AF_XDP integration testing on AWS g4dn instances requires specialized setup in [doc/dev_afxdp.md:65-92]():
1. **Driver installation**: AWS ENA driver with AF_XDP zero-copy support
2. **Privilege escalation**: `setup_all.py --target aws_g4_afxdp` for BPF capabilities
3. **Transport validation**: Direct `transport_test` before NCCL integration
4. **Multi-step verification**: Transport tests → NCCL tests → Application workloads

Sources: [rdma/run_rccl_test_hpcfund.sh:1-85](), [doc/dev_afxdp.md:65-92]()