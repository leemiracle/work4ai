# llm-compressor

> 来源: https://deepwiki.com/vllm-project/llm-compressor 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.coveragerc](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/.coveragerc)
  * [CODE_OF_CONDUCT.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/CODE_OF_CONDUCT.md?plain=1)
  * [CONTRIBUTING.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/CONTRIBUTING.md?plain=1)
  * [LICENSE](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/LICENSE)
  * [Makefile](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/Makefile)
  * [NOTICE](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/NOTICE)
  * [README.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1)
  * [docs/developer-tutorials/add-observer.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/developer-tutorials/add-observer.md?plain=1)
  * [docs/developer-tutorials/index.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/developer-tutorials/index.md?plain=1)
  * [docs/guides/compression_schemes.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/compression_schemes.md?plain=1)
  * [docs/guides/observers.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1)
  * [docs/index.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1)
  * [docs/steps/choosing-dataset.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/steps/choosing-dataset.md?plain=1)
  * [docs/steps/choosing-scheme.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/steps/choosing-scheme.md?plain=1)
  * [docs/steps/why-llmcompressor.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/steps/why-llmcompressor.md?plain=1)
  * [examples/quantization_w8a8_mxfp8/qwen3_example_w8a16_mxfp8.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/examples/quantization_w8a8_mxfp8/qwen3_example_w8a16_mxfp8.py)
  * [examples/quantization_w8a8_mxfp8/qwen3_example_w8a8_mxfp8.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/examples/quantization_w8a8_mxfp8/qwen3_example_w8a8_mxfp8.py)
  * [pyproject.toml](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/pyproject.toml)
  * [setup.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py)
  * [src/llmcompressor/__init__.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/__init__.py)
  * [src/llmcompressor/core/__init__.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/__init__.py)
  * [src/llmcompressor/core/events/event.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/events/event.py)
  * [src/llmcompressor/core/session_functions.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py)
  * [src/llmcompressor/entrypoints/README.md](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/entrypoints/README.md?plain=1)
  * [src/llmcompressor/entrypoints/__init__.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/entrypoints/__init__.py)
  * [tests/examples/__init__.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/tests/examples/__init__.py)
  * [tests/llmcompressor/core/test_session_functions.py](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/tests/llmcompressor/core/test_session_functions.py)

## Purpose and Scope

This document provides an overview of **llm-compressor** , a library for optimizing large language models (LLMs) for deployment with **vLLM**. It provides a comprehensive toolkit for applying state-of-the-art compression algorithms to reduce model size, lower hardware requirements, and improve inference performance. The library is designed to be flexible and easy to use on top of PyTorch and HuggingFace Transformers, allowing for quick experimentation [setup.py91-97](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L91-L97)

Key subsystems detailed in this wiki include:

  * **Core Architecture** : The lifecycle management and execution strategies for compression via sessions and modifiers.
  * **Compression Techniques** : Detailed implementation of quantization (GPTQ, AWQ, AutoRound, SpinQuant) and expert pruning (REAP).
  * **Integration** : How compressed models are served via vLLM and Hugging Face.

**Sources:** [README.md23-29](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L23-L29) [docs/index.md1-4](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L1-L4) [setup.py91-97](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L91-L97)

## What is llm-compressor

`llmcompressor` is an efficient library designed to optimize models for deployment with `vLLM` [README.md23](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L23-L23) It bridges the gap between research-grade compression algorithms and production-ready inference engines.

**Core Characteristics:**

  * **Target Runtime** : Specifically optimized for the `vLLM` inference engine [README.md23](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L23-L23) [docs/index.md3](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L3-L3)
  * **Output Format** : Utilizes the `compressed-tensors` format (safetensors + quantization metadata) for high compatibility [README.md27](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L27-L27) [setup.py140-143](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L140-L143)
  * **Algorithm Breadth** : Supports weight, activation, KV cache, and attention quantization, including GPTQ, AWQ, SmoothQuant, and AutoRound [README.md25](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L25-L25) [README.md88-95](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L88-L95) [docs/index.md34-46](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L34-L46)
  * **Hardware Support** : Targets modern NVIDIA architectures, including support for FP8 (Hopper) and NVFP4/MXFP4 (Blackwell) [docs/index.md52-61](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L52-L61) [README.md75-79](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L75-L79)
  * **Large Model Support** : Leverages disk offloading and distributed strategies (DDP) to handle models that exceed single-node memory [README.md28](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L28-L28) [docs/index.md30-31](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L30-L31)

**Sources:** [README.md23-95](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L23-L95) [docs/index.md1-63](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L1-L63) [setup.py140-143](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L140-L143)

## Core Features and Supported Techniques

### Supported Quantization Schemes

LLM Compressor supports applying multiple formats in a given model, tailored to hardware capabilities [docs/index.md47-52](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L47-L52):

Format| Targets| Compute Capability| Use Case  
---|---|---|---  
**W8A8-FP8**|  Weights and activations| 8.9 (Ada Lovelace+)| High throughput on modern GPUs [docs/index.md57](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L57-L57)  
**W8A8-INT8**|  Weights and activations| 7.5 (Turing+)| Balanced performance and compatibility [docs/index.md56](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L56-L56)  
**W4A16 / W8A16**|  Weights| 7.5 (Turing+)| Optimize for latency on older hardware [docs/index.md55](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L55-L55)  
**NVFP4 / MXFP4**|  Weights and activations| 10.0 (Blackwell)| Maximum compression on latest hardware [docs/index.md59-60](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L59-L60)  
**W4AFP8**|  Weights and activations| 9.0 (Hopper+)| Low-bit weights with dynamic FP8 activations [docs/index.md61](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L61-L61)  
**MXFP8**|  Weights and activations| 10.0 (Blackwell)| Microscale FP8 [docs/index.md58](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L58-L58)  
  
**Sources:** [docs/index.md52-63](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L52-L63) [README.md87-91](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L87-L91) [docs/guides/compression_schemes.md17-88](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/compression_schemes.md?plain=1#L17-L88)

### Supported Algorithms

Algorithm| Description| Use Case  
---|---|---  
**GPTQ**|  Hessian-based weighted quantization with calibration [docs/index.md41](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L41-L41)| High-accuracy 4 and 8 bit weight quantization  
**AWQ**|  Activation-aware weight quantization [docs/index.md42](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L42-L42)| Preserves accuracy for important weights  
**AutoRound**|  Optimizes rounding and clipping via sign-gradient descent [docs/index.md47](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L47-L47)| Broad compatibility and high precision  
**SmoothQuant**|  Outlier handling for W8A8 via activation smoothing [docs/index.md43](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L43-L43)| Improved activation quantization  
**SpinQuant / QuIP**|  Rotation-based transforms to reduce outliers [docs/index.md44-45](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L44-L45)| Improved low-bit accuracy  
**REAP**|  Router-weighted Expert Activation Pruning [README.md80-83](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L80-L83)| Structural expert pruning for MoE models  
  
**Sources:** [README.md80-101](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L80-L101) [docs/index.md38-48](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L38-L48)

## System Architecture

The following diagram bridges the high-level functional requirements to the internal code entities.

**LLM Compressor Component Interaction**

**Sources:** [src/llmcompressor/core/session_functions.py71-178](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py#L71-L178) [src/llmcompressor/core/session.py15](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session.py#L15-L15) [docs/guides/observers.md16-17](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L16-L17) [docs/index.md26-27](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/index.md?plain=1#L26-L27)

## Data Flow: From Model to vLLM

The library transforms a standard Hugging Face model into a compressed format ready for high-throughput serving.

**Compression and Deployment Data Flow**

**Sources:** [src/llmcompressor/core/session_functions.py37-53](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py#L37-L53) [docs/guides/observers.md3-12](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L3-L12) [README.md23-27](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L23-L27)

## Key Implementation Details

### Observer and Calibration System

Observers analyze weight and activation tensors during calibration to compute statistics needed for quantization [docs/guides/observers.md3](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L3-L3) They work in two phases: **Observe** (accumulating statistics via `forward`) and **Compute** (converting statistics into quantization parameters via `get_qparams`) [docs/guides/observers.md5-9](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L5-L9) The library supports DDP synchronization for activation statistics using `sync_activation_stats()` and the `_act_sync_dict` mapping [docs/guides/observers.md24-25](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L24-L25)

**Sources:** [docs/guides/observers.md1-115](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/guides/observers.md?plain=1#L1-L115) [docs/developer-tutorials/add-observer.md1-120](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/docs/developer-tutorials/add-observer.md?plain=1#L1-L120)

### Session and Lifecycle Management

The `CompressionSession` acts as a singleton (or thread-local context) managing the state of compression [src/llmcompressor/core/session_functions.py31-60](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py#L31-L60) The `LifecycleCallbacks` class provides standardized entry points for events such as `batch_start`, `loss_calculated`, and `calibration_end`, which are dispatched to active modifiers [src/llmcompressor/core/session_functions.py71-178](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py#L71-L178)

**Sources:** [src/llmcompressor/core/session_functions.py1-178](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/src/llmcompressor/core/session_functions.py#L1-L178)

### Build and Versioning

The project uses `setuptools_scm` for versioning, supporting `release`, `nightly`, and `dev` build types [setup.py9-14](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L9-L14) Nightly builds use alpha versions (e.g., `*.aYYYYMMDD`) to ensure they are marked as pre-releases on PyPI [setup.py27-33](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L27-L33) The build type is controlled via the `BUILD_TYPE` environment variable [setup.py10](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L10-L10)

**Sources:** [setup.py1-88](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/setup.py#L1-L88) [Makefile8-9](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/Makefile#L8-L9)

## Next Steps

  * [Installation & Setup](/vllm-project/llm-compressor/2-installation-and-setup) — Guide for environment setup and installation.
  * [Core Architecture](/vllm-project/llm-compressor/3-core-architecture) — Deep dive into the `CompressionSession` and `Modifier` systems.
  * [Compression Techniques](/vllm-project/llm-compressor/4-compression-techniques) — Details on specific algorithms like GPTQ, AWQ, and REAP.
  * [vLLM Integration](/vllm-project/llm-compressor/6.1-vllm-integration) — How to serve optimized models.

**Sources:** [README.md102-106](https://github.com/vllm-project/llm-compressor/blob/b7a014f3/README.md?plain=1#L102-L106)
