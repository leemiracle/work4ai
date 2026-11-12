<!-- source: DeepWiki mcp.deepwiki.com · repo uccl-project/uccl · page 8 Testing and Benchmarking · fetched 2026-11-11 -->

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

