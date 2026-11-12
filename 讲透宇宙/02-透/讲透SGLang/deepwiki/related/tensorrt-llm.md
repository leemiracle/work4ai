> 来源: [https://deepwiki.com/NVIDIA/TensorRT-LLM](https://deepwiki.com/NVIDIA/TensorRT-LLM)
> 关联理由: NVIDIA 官方推理引擎（性能对标）

# Overview

  Relevant source files 
 - [README.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1)
 - [docker/Dockerfile.user](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docker/Dockerfile.user)
 - [docker/develop.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docker/develop.md?plain=1)
 - [docker/release.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docker/release.md?plain=1)
 - [docs/requirements.txt](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/requirements.txt)
 - [docs/source/_static/custom.css](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/_static/custom.css)
 - [docs/source/_static/switcher.json](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/_static/switcher.json)
 - [docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md?plain=1)
 - [docs/source/conf.py](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/conf.py)
 - [docs/source/deployment-guide/deployment-guide-for-deepseek-r1-on-trtllm.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/deployment-guide/deployment-guide-for-deepseek-r1-on-trtllm.md?plain=1)
 - [docs/source/deployment-guide/deployment-guide-for-glm-5-on-trtllm.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/deployment-guide/deployment-guide-for-glm-5-on-trtllm.md?plain=1)
 - [docs/source/deployment-guide/deployment-guide-for-gpt-oss-on-trtllm.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/deployment-guide/deployment-guide-for-gpt-oss-on-trtllm.md?plain=1)
 - [docs/source/deployment-guide/deployment-guide-for-llama3.3-70b-on-trtllm.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/deployment-guide/deployment-guide-for-llama3.3-70b-on-trtllm.md?plain=1)
 - [docs/source/deployment-guide/deployment-guide-for-llama4-scout-on-trtllm.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/deployment-guide/deployment-guide-for-llama4-scout-on-trtllm.md?plain=1)
 - [docs/source/helper.py](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/helper.py)
 - [docs/source/index.rst](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/index.rst)
 - [docs/source/installation/containers.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/installation/containers.md?plain=1)
 - [docs/source/quick-start-guide.md](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/quick-start-guide.md?plain=1)
 - [examples/constraints.txt](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/examples/constraints.txt)
 - [examples/llm-api/llm_mgmn_llm_distributed.sh](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/examples/llm-api/llm_mgmn_llm_distributed.sh)
 - [examples/llm-api/llm_mgmn_trtllm_bench.sh](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/examples/llm-api/llm_mgmn_trtllm_bench.sh)
 - [examples/llm-api/llm_mgmn_trtllm_serve.sh](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/examples/llm-api/llm_mgmn_trtllm_serve.sh)
 - [scripts/cuda_driver_stub.py](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/scripts/cuda_driver_stub.py)
 - [tensorrt_llm/llmapi/__init__.py](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py)
 - [tensorrt_llm/version.py](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/version.py)
 - [tests/unittest/api_stability/references_committed/llm.yaml](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml)
 
  
## Purpose and Scope

 This page provides a comprehensive introduction to TensorRT-LLM, NVIDIA's advanced open-source library designed to accelerate and optimize inference for Large Language Models (LLMs) and Visual Generation models on NVIDIA GPUs. It covers the purpose, system architecture, core components, execution flow, and key features of the codebase.

 Detailed technical explanations are included with references to the code entities and implementation files. While this page serves as a leaf overview, it summarizes the major subsystems and links to related documentation scattered across the codebase.

 **Sources:** [README.md1-16](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L1-L16) [tensorrt_llm/version.py1-15](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/version.py#L1-L15)

 
---

 
## What is TensorRT-LLM?

 TensorRT-LLM (version 1.3.0rc25) is a modular inference acceleration framework that optimizes large-scale neural models, particularly LLMs and visual generation models [tensorrt_llm/version.py15](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/version.py#L15-L15) It targets NVIDIA GPUs and incorporates optimized kernels, a efficient runtime, and a pythonic framework that enables customization and extension [README.md3-7](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L3-L7)

 Key qualities:

 
 - **High-level LLM API:** A unified Python interface (LLM class) simplifies model loading, configuration, token generation, and multi-GPU distributed inference [tensorrt_llm/llmapi/llm.py16-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L16-L67) [tensorrt_llm/llmapi/__init__.py36-41](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L36-L41)
 - **In-Flight Batching and Scheduling:** Dynamically manages and merges generation requests for efficient GPU utilization, supporting complex scheduling strategies like overlap scheduler [tensorrt_llm/llmapi/llm_args.py58-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm_args.py#L58-L67) [tensorrt_llm/llmapi/__init__.py68-70](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L68-L70)
 - **Advanced Quantization Support:** Supports emerging formats including NVIDIA FP8 (Hopper, Blackwell) and NVFP4 (Blackwell), with methods like AWQ and SmoothQuant [tensorrt_llm/llmapi/llm_utils.py30](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm_utils.py#L30-L30) [tensorrt_llm/llmapi/__init__.py62-64](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L62-L64)
 - **Speculative Decoding Algorithms:** Implements multiple techniques including EAGLE 3, Multi-Token Prediction (MTP), and NGram (Prompt Lookup) decoding to accelerate generation [tensorrt_llm/llmapi/llm_args.py43-57](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm_args.py#L43-L57) [tensorrt_llm/llmapi/__init__.py55-59](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L55-L59)
 - **Disaggregated Serving:** Separates context prefill and token generation phases across different GPUs, optimized for high-performance setups like NVL72 [tensorrt_llm/llmapi/__init__.py3](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L3-L3) [tensorrt_llm/llmapi/__init__.py44-46](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L44-L46) [README.md76-77](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L76-L77)
 - **Visual Generation:** Provides a unified inference stack for diffusion models such as FLUX, Wan, and LTX2, supporting image and video synthesis [README.md93](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L93-L93) [tensorrt_llm/llmapi/__init__.py99](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L99-L99)
 
 **Sources:** [README.md1-93](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L1-L93) [tensorrt_llm/version.py15](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/version.py#L15-L15) [tensorrt_llm/llmapi/llm.py16-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L16-L67) [tensorrt_llm/llmapi/__init__.py1-100](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L1-L100)

 
---

 
## System Architecture Layers

 TensorRT-LLM is architected as a layered system from high-level user APIs through runtime components down to GPU kernels and devices.

 
### Architecture Layer Diagram

 
```

```

 **Sources:** [tensorrt_llm/llmapi/llm.py40-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L40-L67) [tensorrt_llm/llmapi/__init__.py9-29](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L9-L29) [README.md37-38](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L37-L38) [docs/source/quick-start-guide.md13-20](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/docs/source/quick-start-guide.md?plain=1#L13-L20)

 
---

 
## Core Subsystems

 The codebase is organized into logical subsystems that handle specific aspects of the inference pipeline:

 
| Subsystem | Purpose | Key Components |
|---|---|---|
| LLM API | High-level entry point for LLM inference | LLM, AsyncLLM, TorchLlmArgs, SamplingParams tensorrt_llm/llmapi/llm.py16-67 tensorrt_llm/llmapi/__init__.py37-43 |
| Serving | OpenAI-compatible API and disaggregated serving | OpenAIServer, trtllm-serve, DisaggregatedParams tensorrt_llm/llmapi/__init__.py44-46 docs/source/quick-start-guide.md13-20 |
| Quantization | Low-precision optimization (FP8, NVFP4, INT4/8) | QuantConfig, QuantAlgo, CalibConfig tensorrt_llm/llmapi/__init__.py62-64 tensorrt_llm/llmapi/llm_utils.py30 |
| Distributed | Multi-GPU communication and parallelism | MpiCommSession, AttentionDpConfig, moe_expert_parallel_size tensorrt_llm/llmapi/__init__.py66 tensorrt_llm/llmapi/__init__.py84 tests/unittest/api_stability/references_committed/llm.yaml43-45 |
| Speculative Decoding | Performance acceleration via draft-verify | Eagle3DecodingConfig, MTPDecodingConfig, NGramDecodingConfig tensorrt_llm/llmapi/__init__.py55-59 tensorrt_llm/llmapi/__init__.py72 |

 **Sources:** [tensorrt_llm/llmapi/llm.py16-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L16-L67) [tensorrt_llm/llmapi/__init__.py1-100](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L1-L100) [tests/unittest/api_stability/references_committed/llm.yaml1-142](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml#L1-L142)

 
---

 
## LLM Request Flow

 This diagram bridges the user-level API down to the internal entities handling token generation:

 
```

```

 
 - **LLM Entry:** Users initialize the LLM class, which manages the lifecycle of the model and executor [tensorrt_llm/llmapi/llm.py70-121](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L70-L121) [tests/unittest/api_stability/references_committed/llm.yaml2-97](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml#L2-L97)
 - **Scheduler:** The in-flight batcher dynamically manages the mix of context (prefill) and generation (decode) phases [tensorrt_llm/llmapi/__init__.py60-61](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L60-L61) [tensorrt_llm/llmapi/__init__.py68-70](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L68-L70)
 - **KV Cache Manager:** Manages GPU memory for paged attention, supporting features like BlockReuseConfig [tensorrt_llm/llmapi/__init__.py47-48](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L47-L48) [tensorrt_llm/llmapi/__init__.py50](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L50-L50)
 - **Sampler:** Handles token selection based on SamplingParams, supporting greedy, beam search, and random sampling [tensorrt_llm/llmapi/__init__.py42-43](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L42-L43) [tests/unittest/api_stability/references_committed/llm.yaml104-107](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml#L104-L107)
 
 **Sources:** [tensorrt_llm/llmapi/llm.py70-121](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L70-L121) [tensorrt_llm/llmapi/__init__.py1-100](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L1-L100) [tests/unittest/api_stability/references_committed/llm.yaml1-142](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml#L1-L142)

 
---

 
## Key Optimization Features

 TensorRT-LLM integrates multiple advanced techniques to maximize throughput and reduce latency:

 
| Category | Features |
|---|---|
| Parallelism | Tensor (TP), Pipeline (PP), Expert (EP), and Context Parallelism (CP); Distributed Weight Data Parallelism (DWDP) tests/unittest/api_stability/references_committed/llm.yaml21-45 README.md37-38 |
| Quantization | FP8, NVFP4 (Blackwell), INT4/8, AWQ, SmoothQuant, Block-scale quantization tensorrt_llm/llmapi/__init__.py62-64 docs/source/deployment-guide/deployment-guide-for-gpt-oss-on-trtllm.md26-29 |
| Decoding | Speculative Decoding (EAGLE 3, MTP, NGram), Guided Decoding (xgrammar, llguidance), Beam Search tensorrt_llm/llmapi/__init__.py55-59 tests/unittest/api_stability/references_committed/llm.yaml57-63 |
| Memory | Paged KV Cache, KV Cache Reuse, KV Cache Transfer (NIXL/UCX), Disaggregated Cache tensorrt_llm/llmapi/__init__.py47-50 tensorrt_llm/llmapi/__init__.py71 |
| Visual Gen | Diffusion Transformers (FLUX, Wan, LTX2), Video generation pipelines README.md93 docs/source/quick-start-guide.md105-114 |

 **Sources:** [README.md37-93](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L37-L93) [tensorrt_llm/llmapi/__init__.py1-100](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L1-L100) [tests/unittest/api_stability/references_committed/llm.yaml1-142](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tests/unittest/api_stability/references_committed/llm.yaml#L1-L142)

 
---

 
## External Dependencies

 The framework relies on a specific software stack for optimal performance:

 
| Dependency | Version | Role |
|---|---|---|
| Python | 3.10 / 3.12 | Primary language README.md9-10 |
| CUDA | 13.2.1 | GPU acceleration README.md11 |
| PyTorch | 2.12.0 | Model definition and runtime README.md12 |
| TensorRT-LLM | 1.3.0rc25 | Current release tensorrt_llm/version.py15 examples/constraints.txt1 |

 **Sources:** [README.md9-13](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L9-L13) [tensorrt_llm/version.py15](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/version.py#L15-L15) [examples/constraints.txt1](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/examples/constraints.txt#L1-L1)

 
---

 
# Summary

 TensorRT-LLM is a comprehensive framework offering highly optimized inference for large-scale language and visual models. Its layered architecture organizes functionality from user-facing APIs through a flexible runtime and advanced GPU kernels. Key innovations include advanced quantization (NVFP4/FP8), speculative decoding (EAGLE 3, MTP), disaggregated serving, and native support for the latest model architectures including DeepSeek-V3/V4/R1, Llama 3.3/4, and FLUX.

 **Sources:** [README.md3-5](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/README.md?plain=1#L3-L5) [tensorrt_llm/llmapi/llm.py16-67](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/llm.py#L16-L67) [tensorrt_llm/llmapi/__init__.py1-100](https://github.com/NVIDIA/TensorRT-LLM/blob/f946837a/tensorrt_llm/llmapi/__init__.py#L1-L100)
