# Platform Support

> 来源: https://deepwiki.com/vllm-project/vllm/10-platform-support 抓取日期: 2026-09-02
> 章节: 第 10 章 平台支持

---

Relevant source files

  * [.buildkite/hardware_tests/cpu.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/hardware_tests/cpu.yaml)
  * [.buildkite/hardware_tests/intel.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/hardware_tests/intel.yaml)
  * [.buildkite/scripts/hardware_ci/run-cpu-distributed-smoke-test.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-cpu-distributed-smoke-test.sh)
  * [.buildkite/scripts/hardware_ci/run-cpu-test-arm.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-cpu-test-arm.sh)
  * [.buildkite/scripts/hardware_ci/run-cpu-test.sh](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-cpu-test.sh)
  * [csrc/cpu/utils.cpp](https://github.com/vllm-project/vllm/blob/185cada3/csrc/cpu/utils.cpp)
  * [docs/configuration/conserving_memory.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/configuration/conserving_memory.md?plain=1)
  * [docs/design/endpoint_plugins.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/endpoint_plugins.md?plain=1)
  * [docs/design/plugin_system.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/plugin_system.md?plain=1)
  * [docs/usage/reproducibility.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/usage/reproducibility.md?plain=1)
  * [docs/usage/v1_guide.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/usage/v1_guide.md?plain=1)
  * [tests/kernels/mamba/test_cpu_short_conv.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/mamba/test_cpu_short_conv.py)
  * [tests/model_executor/test_cpu_unquantized_gemm_dispatch.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/model_executor/test_cpu_unquantized_gemm_dispatch.py)
  * [tests/plugins/vllm_add_dummy_endpoint_plugin/setup.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/plugins/vllm_add_dummy_endpoint_plugin/setup.py)
  * [tests/plugins/vllm_add_dummy_endpoint_plugin/vllm_add_dummy_endpoint_plugin/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/plugins/vllm_add_dummy_endpoint_plugin/vllm_add_dummy_endpoint_plugin/__init__.py)
  * [tests/plugins_tests/test_endpoint_plugins.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/plugins_tests/test_endpoint_plugins.py)
  * [tests/test_fxgraphcache_pickle_patch.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_fxgraphcache_pickle_patch.py)
  * [tests/test_zen_cpu_platform_detection.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/test_zen_cpu_platform_detection.py)
  * [tests/v1/attention/test_kv_head_stride_canonicalization.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/attention/test_kv_head_stride_canonicalization.py)
  * [tests/v1/worker/test_xpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/worker/test_xpu_model_runner.py)
  * [vllm/platforms/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/__init__.py)
  * [vllm/platforms/cpu.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py)
  * [vllm/platforms/cuda.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py)
  * [vllm/platforms/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/interface.py)
  * [vllm/platforms/rocm.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py)
  * [vllm/platforms/tpu.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/tpu.py)
  * [vllm/platforms/xpu.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py)
  * [vllm/platforms/zen_cpu.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/zen_cpu.py)
  * [vllm/plugins/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/plugins/__init__.py)
  * [vllm/plugins/endpoint_plugins/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/plugins/endpoint_plugins/__init__.py)
  * [vllm/plugins/endpoint_plugins/interface.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/plugins/endpoint_plugins/interface.py)
  * [vllm/plugins/io_processors/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/plugins/io_processors/__init__.py)
  * [vllm/utils/cpu_resource_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/cpu_resource_utils.py)
  * [vllm/utils/ompmultiprocessing.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/ompmultiprocessing.py)
  * [vllm/v1/worker/cpu_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py)
  * [vllm/v1/worker/xpu_model_runner.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/xpu_model_runner.py)
  * [vllm/v1/worker/xpu_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/xpu_worker.py)

## Purpose and Scope

This document describes vLLM's platform abstraction layer, which enables cross-platform execution on NVIDIA GPUs (CUDA), AMD GPUs (ROCm), Intel GPUs (XPU), CPUs, and TPUs. The platform layer provides a unified interface for hardware detection, device capability queries, attention backend selection, and platform-specific configuration adjustments.

For attention backend implementations, see [Attention Backends](/vllm-project/vllm/8-attention-backends). For distributed execution and communication backends, see [Distributed Execution](/vllm-project/vllm/9-distributed-execution).

* * *

## Platform Abstraction Architecture

### Platform Detection and Initialization

vLLM detects the hardware platform at module load time by examining environment variables and library availability. The detection follows a priority order and initializes the corresponding platform singleton.

**Platform Discovery and Entity Mapping**

**Sources:** [vllm/platforms/interface.py67-76](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/interface.py#L67-L76) [vllm/platforms/rocm.py127-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L127-L156) [vllm/platforms/rocm.py199-214](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L199-L214) [vllm/platforms/xpu.py103-112](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py#L103-L112) [vllm/platforms/cpu.py43-49](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L43-L49) [vllm/platforms/tpu.py9-20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/tpu.py#L9-L20) [vllm/platforms/cuda.py22-26](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L22-L26) [vllm/platforms/__init__.py35-203](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/__init__.py#L35-L203)

* * *

### Platform Interface

The `Platform` base class defined in `vllm/platforms/interface.py` defines the interface that all platform implementations must provide. Key responsibilities include device management, configuration validation, and backend selection.

**Platform Class Hierarchy**

**Sources:** [vllm/platforms/interface.py134-210](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/interface.py#L134-L210) [vllm/platforms/cuda.py11-29](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L11-L29) [vllm/platforms/rocm.py66-82](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L66-L82) [vllm/platforms/xpu.py103-112](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py#L103-L112) [vllm/platforms/cpu.py43-49](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L43-L49) [vllm/utils/cpu_resource_utils.py15-16](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/cpu_resource_utils.py#L15-L16)

* * *

### Device Capability Detection

Each platform provides methods to query hardware capabilities, which inform backend selection and configuration validation. Capabilities are often represented as a `DeviceCapability` named tuple containing `major` and `minor` versions.

Platform| Capability Representation| Detection Method| Key Attributes  
---|---|---|---  
**CUDA**| `DeviceCapability(major, minor)`| NVML API via `import_pynvml` [vllm/platforms/cuda.py49-50](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L49-L50)| SM version (e.g., 8.0, 9.0, 10.0)  
**ROCm**| `DeviceCapability(major, minor)`| GCN arch parsing: `_get_gcn_arch` [vllm/platforms/rocm.py199-214](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L199-L214)| GCN family (gfx942, gfx11, etc.)  
**XPU**| `None`| `get_device_capability` returns `None`| Device name queries via `torch.xpu`  
**CPU**| `None`| `get_cpu_architecture` [vllm/platforms/cpu.py51-71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L51-L71)| `CpuArchEnum` (X86, ARM, POWERPC, RISC-V, etc.)  
**TPU**|  Not defined| External package| TPU version from `tpu_inference` [vllm/platforms/tpu.py9-20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/tpu.py#L9-L20)  
  
**Sources:** [vllm/platforms/interface.py89-132](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/interface.py#L89-L132) [vllm/platforms/cuda.py25-50](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L25-L50) [vllm/platforms/rocm.py199-214](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L199-L214) [vllm/platforms/cpu.py51-71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L51-L71) [vllm/platforms/tpu.py9-20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/tpu.py#L9-L20)

* * *

## Platform-Specific Implementations

### Platform Abstraction Layer

For details, see [Platform Abstraction Layer](/vllm-project/vllm/10.1-platform-abstraction-layer). The `Platform` interface provides the blueprint for hardware-specific logic, ensuring that components like the `AttentionSelector` or `Worker` can interact with different accelerators through a common API. vLLM also supports a plugin system for registering out-of-tree (OOT) platforms via the `vllm.platform_plugins` entry point [docs/design/plugin_system.md50-51](https://github.com/vllm-project/vllm/blob/185cada3/docs/design/plugin_system.md?plain=1#L50-L51)

### CUDA Platform

For details, see [CUDA Platform](/vllm-project/vllm/10.2-cuda-platform). The CUDA platform supports NVIDIA GPUs. It utilizes `pynvml` for hardware discovery without initializing the CUDA context prematurely [vllm/platforms/cuda.py3-5](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L3-L5) It handles backend priorities via `_get_backend_priorities`, favoring `FLASHINFER` or `FLASHMLA` on Blackwell (SM 10.0) and `FLASH_ATTN` on older architectures [vllm/platforms/cuda.py83-163](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L83-L163)

### ROCm Platform

For details, see [ROCm Platform](/vllm-project/vllm/10.3-rocm-platform). The ROCm platform supports AMD GPUs. It parses GCN architecture strings (e.g., `gfx942` for MI300X) using `amdsmi` to determine capabilities [vllm/platforms/rocm.py178-189](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L178-L189) It handles environment variable synchronization between `HIP_VISIBLE_DEVICES` and `CUDA_VISIBLE_DEVICES` [vllm/platforms/rocm.py127-156](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/rocm.py#L127-L156)

### XPU, CPU, and TPU Platforms

For details, see [XPU, CPU, and TPU Platforms](/vllm-project/vllm/10.4-xpu-cpu-and-tpu-platforms).

  * **XPU** : Supports Intel GPUs. It routes attention backends based on `AttentionSelectorConfig` [vllm/platforms/xpu.py142-194](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py#L142-L194) and provides memory information via `get_mem_info_wrapper` which wraps the underlying C++ implementation `torch.ops._C_cache_ops.getMemoryInfo` [vllm/platforms/xpu.py31-97](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py#L31-L97)
  * **CPU** : Supports multiple architectures (x86, ARM, PowerPC, RISC-V, S390X). It implements NUMA-aware memory allocation via `get_memory_node_info` [vllm/platforms/cpu.py123-125](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L123-L125) and `init_cpu_memory_env` in C++ [vllm/v1/worker/cpu_worker.py71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py#L71-L71) It utilizes the `Gloo` distributed backend [vllm/platforms/cpu.py48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L48-L48)
  * **TPU** : Integrates with the `tpu_inference` library for execution on Google TPUs [vllm/platforms/tpu.py9-20](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/tpu.py#L9-L20)

* * *

## Attention Backend Selection

The platform layer is central to selecting the optimal attention backend. Each platform implementation provides `get_attn_backend_cls` or defines priorities in `_get_backend_priorities`.

**Attention Backend Selection Logic**

**Sources:** [vllm/platforms/cuda.py83-163](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cuda.py#L83-L163) [vllm/platforms/cpu.py83-119](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L83-L119) [vllm/platforms/xpu.py142-194](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/xpu.py#L142-L194)

* * *

## CPU Performance and Resource Management

The CPU platform includes specialized logic for managing CPU core affinity and memory locality across various architectures including x86_64, aarch64, and riscv64.

  * **Architecture Support** : Supported dtypes vary by architecture. BF16 on ARM requires `hw.optional.arm.FEAT_BF16` [vllm/platforms/cpu.py60-68](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L60-L68)
  * **Config Validation** : The CPU platform adjusts `VllmConfig` at runtime, such as setting `block_size=16` for MLA kernels [vllm/platforms/cpu.py167-174](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L167-L174)
  * **OMP and NUMA** : Memory is strictly bound or interleaved across NUMA nodes using `init_cpu_memory_env` [vllm/v1/worker/cpu_worker.py71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py#L71-L71) On Linux, vLLM checks for `libtcmalloc` and `libiomp` (for x86) in `LD_PRELOAD` to ensure performance [vllm/v1/worker/cpu_worker.py138-151](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py#L138-L151)
  * **Worker Initialization** : `CPUWorker` binds to memory nodes based on the allowed CPU list and calculates requested memory based on `gpu_memory_utilization` [vllm/v1/worker/cpu_worker.py45-77](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py#L45-L77)
  * **CI and Hardware Testing** : Hardware-specific tests for CPU are defined in Buildkite configurations, covering kernel tests, distributed tests (PP+TP, DP+TP), and multimodal model tests [ .buildkite/hardware_tests/cpu.yaml4-140](https://github.com/vllm-project/vllm/blob/185cada3/ .buildkite/hardware_tests/cpu.yaml#L4-L140)

**Sources:** [vllm/platforms/cpu.py51-71](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L51-L71) [vllm/platforms/cpu.py143-189](https://github.com/vllm-project/vllm/blob/185cada3/vllm/platforms/cpu.py#L143-L189) [vllm/v1/worker/cpu_worker.py33-97](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/cpu_worker.py#L33-L97) [.buildkite/hardware_tests/cpu.yaml1-140](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/hardware_tests/cpu.yaml#L1-L140) [.buildkite/scripts/hardware_ci/run-cpu-test-arm.sh1-102](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/scripts/hardware_ci/run-cpu-test-arm.sh#L1-L102)
