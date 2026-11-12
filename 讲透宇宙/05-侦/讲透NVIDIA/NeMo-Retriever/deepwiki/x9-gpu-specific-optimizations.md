<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Retriever · extra page GPU-Specific Optimizations · fetched 2026-10-26 -->

# GPU-Specific Optimizations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/huggingface-nightly.yml](.github/workflows/huggingface-nightly.yml)
- [.gitignore](.gitignore)
- [ci/scripts/nightly_build_publish.py](ci/scripts/nightly_build_publish.py)
- [ci/tests/test_huggingface_release_workflow.py](ci/tests/test_huggingface_release_workflow.py)
- [nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml](nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml)
- [nemo_retriever/harness/helm-profiles/all-optional.yaml](nemo_retriever/harness/helm-profiles/all-optional.yaml)
- [nemo_retriever/harness/helm-profiles/audio-video.yaml](nemo_retriever/harness/helm-profiles/audio-video.yaml)
- [nemo_retriever/harness/helm-profiles/core.yaml](nemo_retriever/harness/helm-profiles/core.yaml)
- [nemo_retriever/harness/helm-profiles/no-nims-external.yaml](nemo_retriever/harness/helm-profiles/no-nims-external.yaml)
- [nemo_retriever/harness/helm-profiles/split.yaml](nemo_retriever/harness/helm-profiles/split.yaml)
- [nemo_retriever/pyproject.toml](nemo_retriever/pyproject.toml)
- [nemo_retriever/src/nemo_retriever/harness/helm_manager.py](nemo_retriever/src/nemo_retriever/harness/helm_manager.py)
- [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py](nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py)
- [nemo_retriever/tests/test_harness_helm_manager.py](nemo_retriever/tests/test_harness_helm_manager.py)
- [nemo_retriever/tests/test_nemotron_ocr_v2_nightly.py](nemo_retriever/tests/test_nemotron_ocr_v2_nightly.py)
- [nemo_retriever/uv.lock](nemo_retriever/uv.lock)

</details>



## Purpose and Scope

This document covers hardware-specific configuration tuning for deploying the NeMo Retriever Library on different GPU models. It explains how to use GPU selection, override files, and tunable parameters to optimize throughput and memory usage. Additionally, it documents specialized local model optimizations, such as **TensorRT compilation** for `NemotronOCRV2` and integration with `torch_tensorrt`.

For information about GPU virtualization strategies (time-slicing vs MIG), see [Time-Slicing vs MIG](5.2.1). For general GPU resource management concepts, see [GPU Resource Management](5.2).

---

## GPU Selection and Assignment

### The GPU_ID Environment Variable

NeMo Retriever uses the `GPU_ID` environment variable to control which physical GPU device runs the NIM microservices in Docker Compose environments. By default, all core NIMs share GPU 0.

**Setting GPU_ID in Docker Compose:**

```bash
# Run all NIMs on GPU 0 (default)
GPU_ID=0 docker compose --profile retrieval up

# Run all NIMs on GPU 1
GPU_ID=1 docker compose --profile retrieval up
```

### Multi-GPU Configurations

For advanced features requiring dedicated GPUs (audio, nemotron-parse, VLM), you must manually edit `docker-compose.yaml` to assign different `device_ids` to specific services. This prevents VRAM contention between the core pipeline and advanced NIMs that lack fine-grained memory controls.

```yaml
# Example: Run audio NIM on GPU 1
audio:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            device_ids: ["1"]  # Dedicated GPU for heavy audio processing
            capabilities: [gpu]
```

---

## Local Model Optimizations

When running in `local` mode (GPU-backed inference without remote NIMs), the system applies specific optimizations to the underlying models.

### NemotronOCRV2 TensorRT Compilation

The `NemotronOCRV2` class, used for local optical character recognition, includes a best-effort compilation path using `torch_tensorrt`. This targets the text detector submodule to improve region localization latency.

**Implementation Details:**
- **Trigger:** Enabled via the environment variable `RETRIEVER_ENABLE_TORCH_TRT=true` [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:74-74]().
- **Target:** Compiles the `detector` (RegNetX-8GF backbone) using `torch_tensorrt.compile` [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:91-108]().
- **Precision:** Uses `torch.float16` with a fixed input shape of `(1, 3, 1024, 1024)` [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:96-103]().
- **Fallback:** If compilation fails or `torch_tensorrt` is missing, it falls back to eager PyTorch [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:81-86]().

### Data Flow for Local OCR Optimization

The following diagram illustrates how the `NemotronOCRV2` wrapper manages the lifecycle of the local model and its TensorRT optimization.

**Title: Local OCR Optimization and Execution Flow**
```mermaid
graph TD
    subgraph "Initialization [NemotronOCRV2.__init__]"
        Init["__init__(lang, model_dir)"] --> Load["Load nemotron_ocr.inference.pipeline_v2"]
        Load --> TRT_Check{"RETRIEVER_ENABLE_TORCH_TRT == 'true'?"}
        TRT_Check -- "Yes" --> Compile["_maybe_compile_submodules()"]
        TRT_Check -- "No" --> Ready["Model Ready (Eager)"]
        Compile --> TRT_Compile["torch_tensorrt.compile(detector)"]
        TRT_Compile --> Ready
    end

    subgraph "Execution [NemotronOCRV2.invoke]"
        Input["Input (Tensor/Path/B64)"] --> Conv["_tensor_to_png_b64 (if Tensor)"]
        Conv --> Invoke["self._model.invoke(data)"]
        Invoke --> Output["OCR Results (JSON/Text)"]
    end

    Init -.-> [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:41-73]()
    Compile -.-> [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:78-110]()
    Invoke -.-> [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:177-200]()
```
**Sources:** [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:41-110](), [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:177-200]()

---

## Hardware-Specific Override Files

NeMo Retriever provides Docker Compose override files that adjust batch sizes, memory pools, and concurrency settings for specific GPU models. These files reduce VRAM usage to fit the core pipeline within hardware constraints.

| Override File | Target Hardware | VRAM | Purpose |
|--------------|----------------|------|---------|
| `a10g.yaml` | A10G | 24GB | Minimal core pipeline configuration |
| `a100-40gb.yaml` | A100 40GB | 40GB | Core + limited advanced features |
| `l40s.yaml` | L40S | 48GB | Core + most advanced features |

### Applying Overrides
```bash
# A10G deployment (24GB VRAM)
docker compose -f docker-compose.yaml -f a10g.yaml --profile retrieval up
```

---

## Tunable Parameters

### NIM Batch Size and Memory Pools
Batch size controls concurrency, while memory pools pre-allocate VRAM for Triton.

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `NIM_TRITON_MAX_BATCH_SIZE` | Multiple | 32 | Global batch limit for NIMs |
| `NIM_TRITON_CUDA_MEMORY_POOL_MB` | Multiple | 2048 | VRAM pre-allocation per NIM |

### Threading and Parallelism
OpenMP and CPU thread settings are critical for pre-processing stages.

- `OCR_OMP_NUM_THREADS`: Controls OpenMP parallelism for OCR (Default: 8).
- `PAGE_ELEMENTS_CPU_THREADS_PRE_PROCESSOR`: Parallelism for layout detection pre-processing.

---

## Helm and Managed Service Tuning

In Kubernetes environments, GPU-specific optimizations are managed via Helm values and the NIM Operator.

### GPU Resource Requests
The `HelmServiceManager` class handles the orchestration of these settings in benchmarking and production scenarios [nemo_retriever/src/nemo_retriever/harness/helm_manager.py:13-14]().

**Title: Helm Service Optimization Orchestration**
```mermaid
graph LR
    subgraph "Config Space"
        HarnessConfig["HarnessConfig (preset, helm_set)"]
    end

    subgraph "Execution Space"
        Manager["HelmServiceManager"]
        Upgrade["build_upgrade_command()"]
        Poll["_poll_http_200()"]
    end

    subgraph "Kubernetes Space"
        Chart["nemo-retriever Helm Chart"]
        NimOp["NIM Operator"]
        GpuRes["nvidia.com/gpu limits"]
    end

    HarnessConfig --> Manager
    Manager --> Upgrade
    Upgrade -- "helm upgrade --set" --> Chart
    Chart --> NimOp
    NimOp --> GpuRes
    Manager --> Poll
    Poll -- "Check /v1/health" --> Chart

    Manager -.-> [nemo_retriever/src/nemo_retriever/harness/helm_manager.py:51-51]()
    Upgrade -.-> [nemo_retriever/src/nemo_retriever/harness/helm_manager.py:116-160]()
```
**Sources:** [nemo_retriever/src/nemo_retriever/harness/helm_manager.py:13-160](), [nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml:31-45]()

### Managed GPU Profiles
Standardized profiles (e.g., `dgx_8gpu`) are used in benchmark configurations to ensure consistent resource allocation across large-scale hardware [nemo_retriever/harness/examples/managed-helm-nrl-26.05.yaml:46-48]().

---

## Dependency Requirements for Local Optimization

To utilize local GPU optimizations, the `local` extra must be installed. This includes `torch`, `torchvision`, and the specialized `nemotron-ocr` package [nemo_retriever/pyproject.toml:106-141]().

**Local Optimization Stack:**
- **`torch`**: Version 2.11.0 (CUDA-enabled) [nemo_retriever/pyproject.toml:113]()
- **`nemotron-ocr`**: Version >= 2.0.0.dev0, required for `NemotronOCRV2` [nemo_retriever/pyproject.toml:130]()
- **`vllm`**: Version 0.20.0 for LLM-based optimizations [nemo_retriever/pyproject.toml:137]()
- **`flashinfer`**: Required for high-performance attention kernels [nemo_retriever/pyproject.toml:139-140]()

**Sources:** [nemo_retriever/pyproject.toml:106-141](), [nemo_retriever/src/nemo_retriever/model/local/nemotron_ocr_v2.py:55-65]()

---

