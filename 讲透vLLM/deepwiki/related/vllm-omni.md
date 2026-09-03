# vllm-omni

> 来源: https://deepwiki.com/vllm-project/vllm-omni 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [README.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1)
  * [docker/Dockerfile.ci](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docker/Dockerfile.ci)
  * [docker/Dockerfile.cuda](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docker/Dockerfile.cuda)
  * [docker/Dockerfile.rocm](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docker/Dockerfile.rocm)
  * [docker/Dockerfile.xpu](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docker/Dockerfile.xpu)
  * [docs/.nav.yml](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/.nav.yml)
  * [docs/README.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/README.md?plain=1)
  * [docs/configuration/README.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/configuration/README.md?plain=1)
  * [docs/contributing/ci/test_examples/l4_functionality_tests.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/contributing/ci/test_examples/l4_functionality_tests.inc.md?plain=1)
  * [docs/contributing/model/adding_diffusion_model.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/contributing/model/adding_diffusion_model.md?plain=1)
  * [docs/design/architecture_overview.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/architecture_overview.md?plain=1)
  * [docs/design/feature/omni_async_output_materialization.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/feature/omni_async_output_materialization.md?plain=1)
  * [docs/design/figures/dlo/dlo_pipeline.gif](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/figures/dlo/dlo_pipeline.gif)
  * [docs/design/index.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/index.md?plain=1)
  * [docs/features/README.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/features/README.md?plain=1)
  * [docs/features/pd_disaggregation.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/features/pd_disaggregation.md?plain=1)
  * [docs/getting_started/installation/README.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/README.md?plain=1)
  * [docs/getting_started/installation/gpu.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu.md?plain=1)
  * [docs/getting_started/installation/gpu/cuda.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu/cuda.inc.md?plain=1)
  * [docs/getting_started/installation/gpu/musa.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu/musa.inc.md?plain=1)
  * [docs/getting_started/installation/gpu/rocm.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu/rocm.inc.md?plain=1)
  * [docs/getting_started/installation/gpu/xpu.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu/xpu.inc.md?plain=1)
  * [docs/getting_started/quickstart.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/quickstart.md?plain=1)
  * [docs/mkdocs/hooks/generate_api_readme.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/mkdocs/hooks/generate_api_readme.py)
  * [docs/source/architecture/omni-modality-model-architecture.png](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/source/architecture/omni-modality-model-architecture.png)
  * [docs/source/architecture/qwen3-omni-async-output-step-gap.svg](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/source/architecture/qwen3-omni-async-output-step-gap.svg)
  * [docs/user_guide/diffusion/startup_and_loading.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/user_guide/diffusion/startup_and_loading.md?plain=1)
  * [examples/online_serving/text_to_image/run_curl_text_to_image.sh](https://github.com/vllm-project/vllm-omni/blob/10906e3a/examples/online_serving/text_to_image/run_curl_text_to_image.sh)
  * [mkdocs.yml](https://github.com/vllm-project/vllm-omni/blob/10906e3a/mkdocs.yml)
  * [pyproject.toml](https://github.com/vllm-project/vllm-omni/blob/10906e3a/pyproject.toml)
  * [vllm_omni/__init__.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/__init__.py)
  * [vllm_omni/entrypoints/__init__.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/entrypoints/__init__.py)
  * [vllm_omni/entrypoints/openai/__init__.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/entrypoints/openai/__init__.py)
  * [vllm_omni/version.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/version.py)

vLLM-Omni is a high-performance framework designed to extend [vLLM](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vLLM) for **omni-modality** model inference and serving [pyproject.toml10-12](https://github.com/vllm-project/vllm-omni/blob/10906e3a/pyproject.toml#L10-L12) While the original vLLM focuses on text-based autoregressive (AR) tasks, vLLM-Omni introduces support for non-autoregressive architectures like **Diffusion Transformers (DiT)** and manages complex, multi-stage pipelines for heterogeneous outputs such as audio, image, video, and robot actions [README.md31-39](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L31-L39)

### Key Goals and Capabilities

  * **Omni-modality Support** : Native processing of text, image, video, audio, and action data [README.md31-32](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L31-L32)
  * **Architectural Flexibility** : Extends vLLM to support both AR and parallel generation models (e.g., DiT) [README.md33](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L33-L33)
  * **High Throughput** : Leverages vLLM's efficient KV cache management while adding pipelined stage execution to overlap computations [README.md43-45](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L43-L45)
  * **Fully Disaggregated** : Utilizes `OmniConnector` for disaggregated serving, allowing dynamic resource allocation across different model stages [README.md46-47](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L46-L47)
  * **Production Ready** : Provides an OpenAI-compatible API server supporting chat, speech (TTS), image/video generation, and robot-policy serving [README.md19-55](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L19-L55)
  * **Broad Model Coverage** : Supports popular open-source models including Qwen3-Omni, MiniCPM-o 4.5, Cosmos3, FLUX, Wan2.2, and GR00T-N1.7 [README.md58-62](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L58-L62)

### Extending vLLM

vLLM-Omni acts as a superset of vLLM. It maintains interface compatibility, allowing users to use the familiar `vllm serve` command with an added `--omni` flag to enable the multi-stage engine [docs/getting_started/quickstart.mdNaN-NaN](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/quickstart.md?plain=1#LNaN-LNaN) It integrates with vLLM's core by providing optimized model runners and schedulers that handle multimodal payloads, and it registers its models via entry points so they are available in vLLM subprocesses [pyproject.toml156-157](https://github.com/vllm-project/vllm-omni/blob/10906e3a/pyproject.toml#L156-L157)

## System High-Level Architecture

The following diagram illustrates how the core engine manages the lifecycle of a request across heterogeneous stages (AR and Diffusion) and how these relate to specific code entities.

**Diagram: Request Flow and Code Entity Mapping**

**Sources:** [vllm_omni/entrypoints/omni.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/entrypoints/omni.py) [vllm_omni/engine/async_omni_engine.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/engine/async_omni_engine.py) [vllm_omni/engine/orchestrator.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/engine/orchestrator.py) [vllm_omni/engine/stage_engine_core_client.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/engine/stage_engine_core_client.py)

## Model Execution Patterns

vLLM-Omni categorizes models into three representative patterns to handle diverse multimodal workflows [README.md58-62](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L58-L62)

Pattern| Description| Examples  
---|---|---  
**AR-Main**|  Primary execution is autoregressive (text/audio codes).| Qwen3-TTS, VoxCPM2, CosyVoice3 [README.md60](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L60-L60)  
**DiT-Main**|  Primary execution uses Diffusion Transformers.| FLUX, Wan2.2, Qwen-Image, HunyuanVideo [README.md61](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L61-L61)  
**AR + DiT**|  Hybrid pipelines (e.g., AR for reasoning, DiT for generation).| Qwen3-Omni, MiniCPM-o 4.5, BAGEL [README.md59](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L59-L59)  
  
**Diagram: Stage Abstraction and Module Mapping**

**Sources:** [vllm_omni/config/pipeline_registry.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/config/pipeline_registry.py) [vllm_omni/model_executor/models/registry.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/model_executor/models/registry.py) [vllm_omni/diffusion/registry.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/diffusion/registry.py) [vllm_omni/diffusion/engine.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/diffusion/engine.py) [vllm_omni/diffusion/worker.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/diffusion/worker.py)

## Navigation

For detailed technical information, refer to the following sections:

  * **[Getting Started](/vllm-project/vllm-omni/1.1-getting-started)** : Installation for CUDA, ROCm, XPU, and NPU backends. Includes quickstart for offline and online inference [docs/getting_started/quickstart.mdNaN-NaN](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/quickstart.md?plain=1#LNaN-LNaN)
  * **[Architecture Overview](/vllm-project/vllm-omni/1.2-architecture-overview)** : Deep dive into the multi-stage pipeline abstraction, the three representative model patterns (DiT-main, AR-main, AR+DiT), and the core orchestrator logic [docs/design/architecture_overview.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/architecture_overview.md?plain=1)
  * **Core Engine** : Details on `AsyncOmni` entrypoints, the `Orchestrator` request routing, and stage configuration YAML schemas.
  * **AR (Autoregressive) Module** : Overview of the AR execution path, including GPU model runners and schedulers for models like Qwen3-Omni and various TTS engines.
  * **Diffusion Module** : Internal architecture of `DiffusionEngine`, step-wise execution, attention backends, and caching acceleration like TeaCache and Cache-DiT [docs/design/index.md70-72](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/index.md?plain=1#L70-L72)
  * **Distributed Infrastructure** : How inter-stage connectors handle KV transfer and disaggregated prefill-decode routing [README.md46-47](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L46-L47)
  * **OpenAI-Compatible API Server** : Documentation for FastAPI endpoints covering Chat, Speech (TTS), Image, Video, and Robot Policy (OpenPI) [README.mdNaN-NaN](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#LNaN-LNaN)
  * **Quantization** : Support for both AR and Diffusion quantization methods including FP8, MXFP8, GGUF, and AutoRound [docs/design/index.md38-40](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/index.md?plain=1#L38-L40)

**Sources:** [README.md1-100](https://github.com/vllm-project/vllm-omni/blob/10906e3a/README.md?plain=1#L1-L100) [docs/getting_started/quickstart.md1-119](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/quickstart.md?plain=1#L1-L119) [docs/design/index.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/design/index.md?plain=1) [docs/getting_started/installation/gpu/cuda.inc.md](https://github.com/vllm-project/vllm-omni/blob/10906e3a/docs/getting_started/installation/gpu/cuda.inc.md?plain=1) [vllm_omni/entrypoints/openai/__init__.py](https://github.com/vllm-project/vllm-omni/blob/10906e3a/vllm_omni/entrypoints/openai/__init__.py)
