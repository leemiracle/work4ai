# vllm-ascend

> 来源: https://deepwiki.com/vllm-project/vllm-ascend 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [README.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1)
  * [README.zh.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.zh.md?plain=1)
  * [benchmarks/README.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/README.md?plain=1)
  * [benchmarks/requirements-bench.txt](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/requirements-bench.txt)
  * [benchmarks/scripts/perf_result_template.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/scripts/perf_result_template.md?plain=1)
  * [benchmarks/scripts/run-performance-benchmarks.sh](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/scripts/run-performance-benchmarks.sh)
  * [benchmarks/tests/latency-tests.json](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/tests/latency-tests.json)
  * [benchmarks/tests/serving-tests.json](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/tests/serving-tests.json)
  * [benchmarks/tests/throughput-tests.json](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/benchmarks/tests/throughput-tests.json)
  * [docs/source/community/contributors.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/contributors.md?plain=1)
  * [docs/source/community/images/issue_label_workflow.png](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/images/issue_label_workflow.png)
  * [docs/source/community/issue-workflow-guidelines.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/issue-workflow-guidelines.md?plain=1)
  * [docs/source/community/versioning_policy.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/versioning_policy.md?plain=1)
  * [docs/source/conf.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/conf.py)
  * [docs/source/developer_guide/evaluation/index.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/developer_guide/evaluation/index.md?plain=1)
  * [docs/source/developer_guide/evaluation/using_evalscope.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/developer_guide/evaluation/using_evalscope.md?plain=1)
  * [docs/source/developer_guide/evaluation/using_lm_eval.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/developer_guide/evaluation/using_lm_eval.md?plain=1)
  * [docs/source/developer_guide/evaluation/using_opencompass.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/developer_guide/evaluation/using_opencompass.md?plain=1)
  * [docs/source/faqs.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1)
  * [docs/source/index.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/index.md?plain=1)
  * [docs/source/installation.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/installation.md?plain=1)
  * [docs/source/user_guide/configuration/additional_config.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/user_guide/configuration/additional_config.md?plain=1)
  * [docs/source/user_guide/release_notes.md](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/user_guide/release_notes.md?plain=1)
  * [pyproject.toml](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/pyproject.toml)
  * [requirements.txt](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/requirements.txt)
  * [tests/ut/test_ascend_config.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/tests/ut/test_ascend_config.py)
  * [tests/ut/test_platform.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/tests/ut/test_platform.py)
  * [tests/ut/test_utils.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/tests/ut/test_utils.py)
  * [vllm_ascend/ascend_config.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_config.py)
  * [vllm_ascend/ascend_forward_context.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py)
  * [vllm_ascend/envs.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/envs.py)
  * [vllm_ascend/platform.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py)
  * [vllm_ascend/utils.py](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/utils.py)

vLLM-Ascend (`vllm-ascend`) is a community-maintained hardware plugin that enables vLLM to run seamlessly on Ascend NPU hardware. It implements the hardware-pluggable interface as defined in vLLM's [[RFC]: Hardware pluggable](https://github.com/vllm-project/vllm/issues/11162), providing a decoupled and modular integration between the vLLM inference system and Ascend NPUs. [README.md51-54](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1#L51-L54)

This plugin supports a variety of popular large language models, including Transformer-based architectures, Mixture-of-Experts (MoE) models, embedding models, and multi-modal LLMs, allowing them to run efficiently on Ascend NPUs without model code modifications. [README.md55-58](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1#L55-L58) To ensure stability and maintain compatibility, vLLM-Ascend releases are version-aligned and tested against specific versions of upstream vLLM. [docs/source/community/versioning_policy.md3-9](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/versioning_policy.md?plain=1#L3-L9) [docs/source/faqs.md107-110](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L107-L110)

For comprehensive details on functionality, hardware support, and system design, please refer to the child pages:

  * [Features and Capabilities](/vllm-project/vllm-ascend/1.1-features-and-capabilities)
  * [Supported Hardware and Models](/vllm-project/vllm-ascend/1.2-supported-hardware-and-models)
  * [System Architecture Overview](/vllm-project/vllm-ascend/1.3-system-architecture-overview)

* * *

## Plugin Registration and Entry Points

vLLM-Ascend plugs into vLLM through the platform plugin system. Its central entry point is the `NPUPlatform` class, declared as an Out-Of-Tree (OOT) platform plugin that vLLM discovers automatically during initialization. [vllm_ascend/platform.py78-79](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L78-L79)

### Platform Registration Flow

**Key points:**

  * `NPUPlatform.pre_register_and_update()` is called early during configuration. It triggers application of global platform patches and registers Ascend-specific quantization methods like "ascend," "compressed-tensors," and "fp8". [vllm_ascend/platform.py88-255](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L88-L255)
  * `NPUPlatform.apply_config_platform_defaults()` handles platform-specific default configurations such as setting maximum graph capture batch sizes adapted for Ascend hardware (A2/A3/950), and disables incompatible features for certain chips (e.g., A5 HDK incompatibilities). [vllm_ascend/platform.py270-302](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L270-L302)
  * Custom environment variables control aspects like device visibility and compilation backends.

**Sources:** [vllm_ascend/platform.py78-302](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L78-L302) [vllm_ascend/utils.py48-52](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/utils.py#L48-L52)

* * *

## Core Architecture

### System Integration Map

### Component Responsibilities

Component| Role and Responsibilities  
---|---  
`NPUPlatform`| Registers the platform plugin, validates and applies Ascend-specific defaults, and provides the custom compiler backend (`AscendCompiler`). [vllm_ascend/platform.py78-181](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L78-L181)  
`AscendConfig`| Handles nested configuration structures specific to Ascend devices, including compilation, fusion, parallelism, and scheduler parameters. [vllm_ascend/ascend_config.py27-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_config.py#L27-L60)  
`NPUWorker`| Manages device initialization, memory profiling, registers custom operators, and manages hardware resource allocation. [docs/source/faqs.md85-87](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L85-L87)  
`NPUModelRunner`| Orchestrates model execution: input preparation, graph capture/replay, and invocation of attention backends and custom operations. [vllm_ascend/platform.py193-198](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L193-L198)  
`AscendForwardContext`| Controls metadata flow and communication strategies (e.g., MoE communication types) during forward passes on Ascend hardware. [vllm_ascend/ascend_forward_context.py57-100](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py#L57-L100)  
  
**Sources:** [vllm_ascend/platform.py78-198](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L78-L198) [vllm_ascend/ascend_config.py27-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_config.py#L27-L60) [vllm_ascend/ascend_forward_context.py57-100](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py#L57-L100)

* * *

## Worker Initialization and Execution Flow

### Initialization Sequence

  * `NPUWorker` applies Ascend-specific patches to extend or replace vLLM core behavior at the worker level. [vllm_ascend/utils.py52-199](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/utils.py#L52-L199)
  * It registers a suite of custom CUDA kernel-like operations tailored for Ascend NPUs (e.g., device printing, fused kernels for Transformers). [vllm_ascend/utils.py58-198](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/utils.py#L58-L198)
  * Memory profiling occurs early in the initialization to determine HBM (High Bandwidth Memory) availability and optimal KV cache sizing, including mitigations for Ascend-specific memory fragmentation and utilization quirks. [docs/source/faqs.md137-144](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L137-L144)
  * During generation, `set_ascend_forward_context()` is invoked to configure run-time aspects like communication protocols (FlashComm1, MC2) and attention metadata construction. [vllm_ascend/ascend_forward_context.py57-100](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py#L57-L100)
  * Weights may be converted to the `FRACTAL_NZ` tensor format for better performance on Ascend devices if enabled. [vllm_ascend/envs.py80-84](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/envs.py#L80-L84)

**Sources:** [vllm_ascend/utils.py52-199](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/utils.py#L52-L199) [vllm_ascend/ascend_forward_context.py57-100](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py#L57-L100) [docs/source/faqs.md137-144](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L137-L144) [vllm_ascend/envs.py80-84](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/envs.py#L80-L84)

* * *

## Hardware and Software Requirements

### Supported Hardware

([docs/source/faqs.md16-22](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L16-L22) [README.md62](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1#L62-L62))

Hardware Series| Support Status| Notes  
---|---|---  
Atlas A2 Training Series| Supported| Production recommended  
Atlas 800I A2 Inference Series| Supported| Production recommended  
Atlas A3 Training Series| Supported| High-performance cards  
Atlas 800I A3 Inference Series| Supported| High-performance cards  
Atlas 300I Duo (310P Series)| Experimental| Early support, stable version v0.10.0rc1  
Atlas A5 Series (Ascend 950)| Supported| High-density inference series  
  
**Sources:** [docs/source/faqs.md16-22](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L16-L22) [README.md62](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1#L62-L62)

### Software Stack

([docs/source/installation.md14-31](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/installation.md?plain=1#L14-L31) [docs/source/community/versioning_policy.md24-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/versioning_policy.md?plain=1#L24-L60))

Software Component| Version/Requirement  
---|---  
Python| >= 3.10, < 3.13  
PyTorch| 2.10.0  
torch-npu| 2.10.0.post4  
CANN (Ascend software)| 9.1.0  
NNAL (Neural Acceleration Library)| 9.1.0 (for libatb.so)  
vLLM| Version aligned with vllm-ascend plugin version (e.g., v0.23.0rc1 with vLLM v0.23.0)  
  
**Sources:** [docs/source/installation.md14-31](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/installation.md?plain=1#L14-L31) [docs/source/faqs.md107-110](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L107-L110) [docs/source/community/versioning_policy.md24-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/versioning_policy.md?plain=1#L24-L60)

* * *

## Configuration and Environment Variables

### Key Environment Variables

([vllm_ascend/envs.py30-103](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/envs.py#L30-L103) [docs/source/faqs.md133-136](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L133-L136))

Environment Variable| Default / Notes| Purpose / Effect  
---|---|---  
`ASCEND_HOME_PATH`| None| Path for Ascend CANN toolkit installation.  
`VLLM_VERSION`| None| Overrides vLLM version to enforce compatibility checks.  
`VLLM_ASCEND_ENABLE_NZ`| 1| Enable conversion of model weights to Fractal NZ format for improved performance.  
`VLLM_ASCEND_ENABLE_FLASHCOMM1`| 0 (Deprecated)| Enable FlashComm V1 optimization for large context and concurrency.  
`SOC_VERSION`| None| Specifies Ascend SOC chip version used during packaging/build.  
  
Users are encouraged to use `--additional-config` in vLLM commands to pass fine-grained Ascend-specific configuration parameters instead of direct environment variables, facilitating future compatibility and cleaner configuration management. For details, see [Additional Configuration](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/Additional Configuration)

**Sources:** [vllm_ascend/envs.py30-103](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/envs.py#L30-L103) [docs/source/faqs.md133-136](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L133-L136) [docs/source/user_guide/configuration/additional_config.md1-43](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/user_guide/configuration/additional_config.md?plain=1#L1-L43)

* * *

This overview lays the foundation for understanding the vLLM-Ascend plugin architecture, its integration with upstream vLLM, and key platform-level details. For deeper technical insights and usage, please refer to the following child pages:

  * [Features and Capabilities](/vllm-project/vllm-ascend/1.1-features-and-capabilities) — Supported attention backends (MLA/SFA/DSA), quantization methods, speculative decoding, distributed execution, and batch scheduling.
  * [Supported Hardware and Models](/vllm-project/vllm-ascend/1.2-supported-hardware-and-models) — Details on Ascend NPU hardware (A2/A3/310P/A5), compatible model architectures, and version compatibility matrices.
  * [System Architecture Overview](/vllm-project/vllm-ascend/1.3-system-architecture-overview) — High-level architecture diagrams and detailed flow of platform, worker, model runner, and patch integrations.

* * *

**Sources:**  
[README.md51-58](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/README.md?plain=1#L51-L58) [vllm_ascend/platform.py78-302](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/platform.py#L78-L302) [vllm_ascend/ascend_config.py27-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_config.py#L27-L60) [vllm_ascend/ascend_forward_context.py57-100](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/vllm_ascend/ascend_forward_context.py#L57-L100) [docs/source/installation.md14-31](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/installation.md?plain=1#L14-L31) [docs/source/faqs.md16-136](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/faqs.md?plain=1#L16-L136) [docs/source/community/versioning_policy.md3-60](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/community/versioning_policy.md?plain=1#L3-L60) [docs/source/user_guide/configuration/additional_config.md1-43](https://github.com/vllm-project/vllm-ascend/blob/2fc76ff0/docs/source/user_guide/configuration/additional_config.md?plain=1#L1-L43)
