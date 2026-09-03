# Testing and CI/CD

> 来源: https://deepwiki.com/vllm-project/vllm/12-testing-and-cicd 抓取日期: 2026-09-02
> 章节: 第 12 章 测试与 CI/CD

---

Relevant source files

  * [.buildkite/test-amd.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml)
  * [.buildkite/test-pipeline.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml)
  * [.buildkite/test_areas/attention.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/attention.yaml)
  * [.buildkite/test_areas/basic_correctness.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/basic_correctness.yaml)
  * [.buildkite/test_areas/benchmarks.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/benchmarks.yaml)
  * [.buildkite/test_areas/distributed.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml)
  * [.buildkite/test_areas/engine.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/engine.yaml)
  * [.buildkite/test_areas/entrypoints.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/entrypoints.yaml)
  * [.buildkite/test_areas/expert_parallelism.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/expert_parallelism.yaml)
  * [.buildkite/test_areas/kernels.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/kernels.yaml)
  * [.buildkite/test_areas/lm_eval.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/lm_eval.yaml)
  * [.buildkite/test_areas/lora.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/lora.yaml)
  * [.buildkite/test_areas/misc.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml)
  * [.buildkite/test_areas/model_executor.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/model_executor.yaml)
  * [.buildkite/test_areas/model_runner_v2.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/model_runner_v2.yaml)
  * [.buildkite/test_areas/models_basic.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/models_basic.yaml)
  * [.buildkite/test_areas/models_distributed.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/models_distributed.yaml)
  * [.buildkite/test_areas/models_language.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/models_language.yaml)
  * [.buildkite/test_areas/models_multimodal.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/models_multimodal.yaml)
  * [.buildkite/test_areas/plugins.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/plugins.yaml)
  * [.buildkite/test_areas/pytorch.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/pytorch.yaml)
  * [.buildkite/test_areas/spec_decode.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/spec_decode.yaml)
  * [.buildkite/test_areas/weight_loading.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/weight_loading.yaml)
  * [examples/pooling/score/colbert_rerank_online.py](https://github.com/vllm-project/vllm/blob/185cada3/examples/pooling/score/colbert_rerank_online.py)
  * [tests/conftest.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/conftest.py)
  * [tests/models/language/generation/test_hybrid.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/language/generation/test_hybrid.py)
  * [tests/models/language/pooling/test_colbert.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/language/pooling/test_colbert.py)
  * [tests/models/multimodal/generation/test_voxtral_realtime.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/models/multimodal/generation/test_voxtral_realtime.py)
  * [tests/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/utils.py)
  * [vllm/model_executor/models/colbert.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/colbert.py)
  * [vllm/model_executor/models/whisper_causal.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/model_executor/models/whisper_causal.py)

This page describes how vLLM is tested and how its continuous integration pipelines are structured. It covers the overall layout of the test infrastructure, the Buildkite CI pipeline organization, hardware-specific testing (including NVIDIA, AMD/ROCm, Intel XPU, and TPU), and the model correctness verification framework.

For details on individual topics, see the child pages:

  * **Test Organization and Infrastructure** — directory layout, test categories, and fixtures: see [Test Organization and Infrastructure](/vllm-project/vllm/12.1-test-organization-and-infrastructure)
  * **Buildkite CI Pipelines** — pipeline generation, test sharding, and pipeline structure: see [Buildkite CI Pipelines](/vllm-project/vllm/12.2-buildkite-ci-pipelines)
  * **Hardware-Specific Testing** — AMD/ROCm, TPU, XPU setup, and hardware-specific overrides: see [Hardware-Specific Testing](/vllm-project/vllm/12.3-hardware-specific-testing)
  * **Model Correctness Validation** — model correctness tests, reference comparisons, and benchmarking tools: see [Model Correctness Validation](/vllm-project/vllm/12.4-model-correctness-validation)

* * *

## Overview

vLLM uses [Buildkite](https://buildkite.com) as its primary CI platform. Each pull request triggers a pipeline that builds Docker images and dispatches parallelized test steps across NVIDIA and AMD GPU pools, as well as CPU, TPU, and XPU environments.

The pipeline configuration is organized into a modular structure to handle the complexity of multi-hardware support [.buildkite/test-pipeline.yaml1-8](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L1-L8):

  * `.buildkite/test_areas/` — Test job definitions for CUDA, CPU, and general logic (e.g., `distributed.yaml`, `entrypoints.yaml`, `engine.yaml`, `kernels.yaml`, `models_multimodal.yaml`).
  * `.buildkite/image_build/` — Docker image building jobs.
  * `.buildkite/hardware_tests/` — Jobs for specific hardware architectures (e.g., Intel, Ascend NPU, Arm).
  * `.buildkite/ci_config.yaml` — Central configuration for the CI pipeline.

Sources: [.buildkite/test-pipeline.yaml1-8](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L1-L8) [.buildkite/test_areas/distributed.yaml1-4](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L1-L4)

* * *

## CI Pipeline Architecture

**Buildkite Pipeline High-Level Flow**

Each test area YAML defines a `group` with multiple `steps`. Steps typically depend on the completion of image builds. For example, the `Distributed` group in [.buildkite/test_areas/distributed.yaml1-4](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L1-L4) depends on `image-build`.

Sources: [.buildkite/test-pipeline.yaml1-8](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L1-L8) [.buildkite/test_areas/distributed.yaml1-4](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L1-L4) [.buildkite/test-amd.yaml1-7](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml#L1-L7)

* * *

## Test Areas and Step Configuration

Test steps are defined with metadata that controls execution environment and triggering logic. The CI uses `source_file_dependencies` to optimize runtimes by only triggering relevant tests when specific directories (e.g., `vllm/distributed`) are modified.

**Test Step Field Reference**

Field| Description  
---|---  
`label`| Display name in Buildkite UI.  
`timeout_in_minutes`| Maximum runtime before the step is killed.  
`commands`| List of shell commands to execute (e.g., `pytest`).  
`source_file_dependencies`| File path prefixes; step runs only if these files change [.buildkite/test_areas/misc.yaml9-19](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L9-L19)  
`device`| Specifies hardware requirements (e.g., `h100`, `h200_18gb`, `mi300_1`, `b200-k8s`) [.buildkite/test_areas/kernels.yaml45](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/kernels.yaml#L45-L45)  
`num_devices`| Number of GPUs/accelerators required (e.g., 2, 4, 8) [.buildkite/test_areas/distributed.yaml9](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L9-L9)  
`parallelism`| Number of parallel jobs for test sharding using `$$BUILDKITE_PARALLEL_JOB` [.buildkite/test_areas/kernels.yaml28](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/kernels.yaml#L28-L28)  
  
**Example step from`.buildkite/test_areas/distributed.yaml`:**

Sources: [.buildkite/test-amd.yaml8-27](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml#L8-L27) [.buildkite/test_areas/distributed.yaml5-16](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L5-L16) [.buildkite/test_areas/misc.yaml5-22](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L5-L22)

* * *

## Hardware-Specific Testing Infrastructure

vLLM supports a wide array of hardware. Testing for non-NVIDIA platforms is managed via dedicated scripts and YAML configurations.

### AMD/ROCm Infrastructure

AMD tests are managed via [.buildkite/test-amd.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml) and specialized runners. The pipeline supports various GPU agents including `MI250`, `MI300`, and `MI355` [.buildkite/test-amd.yaml41-44](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml#L41-L44) It includes specific overrides for `num_gpus`, `num_nodes`, and `mirror_hardwares` to simulate multi-node setups on single hosts [.buildkite/test-amd.yaml18-21](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml#L18-L21)

Sources: [.buildkite/test-amd.yaml1-44](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-amd.yaml#L1-L44)

### Other Platforms

  * **Intel XPU / Ascend NPU / TPU** : Specific configurations are located in `.buildkite/hardware_tests/` (e.g., `intel.yaml`) and referenced in the main pipeline [.buildkite/test-pipeline.yaml5](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L5-L5)
  * **CPU** : Modular YAMLs like [.buildkite/test_areas/misc.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml) define `V1 Others (CPU)` steps using `cpu-small` devices and filtering for `cpu_test` markers [.buildkite/test_areas/misc.yaml97-127](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L97-L127)
  * **Multi-Node** : Simulated on single hosts for distributed tests using `torchrun` with `--nproc-per-node` and `VLLM_TEST_SAME_HOST=1` [.buildkite/test_areas/distributed.yaml118-119](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L118-L119)

Sources: [.buildkite/test-pipeline.yaml5](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L5-L5) [.buildkite/test_areas/misc.yaml97-127](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L97-L127) [.buildkite/test_areas/distributed.yaml99-121](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L99-L121)

* * *

## Test Infrastructure Code Map

The following diagram maps CI components to their corresponding code entities and the `tests/` directory structure:

Sources: [.buildkite/test-pipeline.yaml1-8](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test-pipeline.yaml#L1-L8) [.buildkite/test_areas/distributed.yaml5-16](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L5-L16) [.buildkite/test_areas/distributed.yaml104-135](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L104-L135) [tests/conftest.py85-216](https://github.com/vllm-project/vllm/blob/185cada3/tests/conftest.py#L85-L216) [tests/utils.py205-230](https://github.com/vllm-project/vllm/blob/185cada3/tests/utils.py#L205-L230)

* * *

## Relationship to Other Subsystems

Testing infrastructure bridges the gap between development and deployment:

  * **Distributed Execution** : Tests in [.buildkite/test_areas/distributed.yaml](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml) validate `TP`, `PP`, and `DP` strategies using `torchrun` and custom examples like `examples/features/data_parallel/data_parallel_offline.py` [.buildkite/test_areas/distributed.yaml123-151](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L123-L151)
  * **V1 Engine** : Integration tests for V1 core components, including `AsyncLLM` and `EngineCoreClient`, ensure Data Parallel (DP) and Speculative Decoding correctness [.buildkite/test_areas/distributed.yaml35-56](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L35-L56) [.buildkite/test_areas/misc.yaml41-88](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L41-L88)
  * **Kernel Validation** : Kernels are tested across attention backends and quantization methods, including specialized tests for `DeepSeek V4`, `MLA`, and `MoE` [.buildkite/test_areas/kernels.yaml44-210](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/kernels.yaml#L44-L210)
  * **Model Correctness** : vLLM validates model initialization and generation across a large registry. `evals/gsm8k/test_gsm8k_correctness.py` is used for accuracy evaluation across small and large model configurations [.buildkite/test_areas/lm_eval.yaml5-152](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/lm_eval.yaml#L5-L152)
  * **Serving APIs** : OpenAI-compatible entrypoints are validated for unit and integration correctness via `pytest` [.buildkite/test_areas/entrypoints.yaml5-209](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/entrypoints.yaml#L5-L209)

Sources: [.buildkite/test_areas/distributed.yaml123-151](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L123-L151) [.buildkite/test_areas/distributed.yaml35-56](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/distributed.yaml#L35-L56) [.buildkite/test_areas/misc.yaml41-88](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/misc.yaml#L41-L88) [.buildkite/test_areas/kernels.yaml44-210](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/kernels.yaml#L44-L210) [.buildkite/test_areas/lm_eval.yaml5-152](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/lm_eval.yaml#L5-L152) [.buildkite/test_areas/entrypoints.yaml5-209](https://github.com/vllm-project/vllm/blob/185cada3/.buildkite/test_areas/entrypoints.yaml#L5-L209)
