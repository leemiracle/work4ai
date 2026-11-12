<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Model-Optimizer · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/TOOLING.md](.agents/TOOLING.md)
- [.agents/review-guidelines/technical-blog.md](.agents/review-guidelines/technical-blog.md)
- [.coderabbit.yaml](.coderabbit.yaml)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [.github/actions/pr-merge-base/action.yml](.github/actions/pr-merge-base/action.yml)
- [.github/workflows/bump_uv_lock.yml](.github/workflows/bump_uv_lock.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)
- [.github/workflows/claude_review.yml](.github/workflows/claude_review.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE_HEADER](LICENSE_HEADER)
- [README.md](README.md)
- [docs/source/_ext/modelopt_autodoc_pydantic.py](docs/source/_ext/modelopt_autodoc_pydantic.py)
- [docs/source/_static/announcements.css](docs/source/_static/announcements.css)
- [docs/source/_static/announcements.js](docs/source/_static/announcements.js)
- [docs/source/_static/custom.css](docs/source/_static/custom.css)
- [docs/source/announcements/assets/autoquantize-qwen35-mmlu-effective-bits.png](docs/source/announcements/assets/autoquantize-qwen35-mmlu-effective-bits.png)
- [docs/source/announcements/autoquantize.rst](docs/source/announcements/autoquantize.rst)
- [docs/source/announcements/dspark-vs-domino.rst](docs/source/announcements/dspark-vs-domino.rst)
- [docs/source/announcements/github-pages-announcements.rst](docs/source/announcements/github-pages-announcements.rst)
- [docs/source/conf.py](docs/source/conf.py)
- [docs/source/deployment/2_onnxruntime.rst](docs/source/deployment/2_onnxruntime.rst)
- [docs/source/getting_started/1_overview.rst](docs/source/getting_started/1_overview.rst)
- [docs/source/getting_started/2_installation.rst](docs/source/getting_started/2_installation.rst)
- [docs/source/getting_started/_installation_for_Linux.rst](docs/source/getting_started/_installation_for_Linux.rst)
- [docs/source/getting_started/windows/_installation_for_Windows.rst](docs/source/getting_started/windows/_installation_for_Windows.rst)
- [docs/source/getting_started/windows/_installation_standalone.rst](docs/source/getting_started/windows/_installation_standalone.rst)
- [docs/source/getting_started/windows/_installation_with_olive.rst](docs/source/getting_started/windows/_installation_with_olive.rst)
- [docs/source/guides/0_support_matrix.rst](docs/source/guides/0_support_matrix.rst)
- [docs/source/guides/windows_guides/_ONNX_PTQ_guide.rst](docs/source/guides/windows_guides/_ONNX_PTQ_guide.rst)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/support/2_faqs.rst](docs/source/support/2_faqs.rst)
- [examples/diffusers/requirements.txt](examples/diffusers/requirements.txt)
- [examples/windows/README.md](examples/windows/README.md)
- [examples/windows/onnx_ptq/genai_llm/README.md](examples/windows/onnx_ptq/genai_llm/README.md)
- [examples/windows/onnx_ptq/genai_llm/quantize.py](examples/windows/onnx_ptq/genai_llm/quantize.py)
- [examples/windows/onnx_ptq/sam2/README.md](examples/windows/onnx_ptq/sam2/README.md)
- [examples/windows/torch_onnx/diffusers/README.md](examples/windows/torch_onnx/diffusers/README.md)
- [examples/windows/torch_onnx/diffusers/type_update_trt_custom_ops.py](examples/windows/torch_onnx/diffusers/type_update_trt_custom_ops.py)
- [modelopt/onnx/quantization/extensions.py](modelopt/onnx/quantization/extensions.py)
- [tests/examples/diffusers/test_cache_diffusion.py](tests/examples/diffusers/test_cache_diffusion.py)
- [tests/examples/gpt-oss/test_gpt_oss_qat.py](tests/examples/gpt-oss/test_gpt_oss_qat.py)
- [uv.lock](uv.lock)

</details>



This page provides installation instructions and basic usage examples to help you quickly start using NVIDIA Model Optimizer (ModelOpt). It covers installation methods, quickstart workflows for common optimization techniques, and basic API patterns for both Linux and Windows environments.

---

## Installation and Environment Setup

ModelOpt can be installed via `pip` from PyPI, from source, or used within pre-configured NVIDIA Docker containers.

### Installation Options

The following diagram illustrates the decision flow for choosing an installation method based on your environment and requirements.

**Installation Decision Flow**
```mermaid
graph TD
    "START"["Choose Installation Method"] --> "LINUX"["Linux"]
    "START"["Choose Installation Method"] --> "WINDOWS"["Windows"]
    
    "LINUX" --> "DOCKER"["Docker Recommended"]
    "LINUX" --> "PIP_LOCAL"["Local PIP/Conda"]
    
    "DOCKER" --> "TRTLLM_IMG"["nvcr.io/nvidia/tensorrt-llm/release"]
    "DOCKER" --> "PYTORCH_IMG"["nvcr.io/nvidia/pytorch"]
    "DOCKER" --> "NEMO_IMG"["nvcr.io/nvidia/nemo"]
    
    "PIP_LOCAL" --> "PIP_ALL"["pip install nvidia-modelopt[all]"]
    
    "WINDOWS" --> "WIN_PIP"["pip install nvidia-modelopt[onnx]"]
    
    "TRTLLM_IMG" --> "UPGRADE"["pip install -U nvidia-modelopt[all]"]
    "PYTORCH_IMG" --> "UPGRADE"
    "NEMO_IMG" --> "UPGRADE"
    "UPGRADE" --> "VERIFY"["python -c import modelopt"]
    "PIP_ALL" --> "VERIFY"
    "WIN_PIP" --> "VERIFY"
```
Sources: [docs/source/getting_started/_installation_for_Linux.rst:31-56](), [pyproject.toml:54-74](), [pyproject.toml:136]()

### Method 1: Install from PyPI (Linux)

Install the package with all dependencies for a complete experience:

```bash
pip install -U "nvidia-modelopt[all]"
```

If you require only specific modules to minimize the dependency footprint, use partial extras defined in `pyproject.toml`:

| Extra | Module / Use Case | Key Dependencies |
|-------|-------------------|------------------|
| `[onnx]` | `modelopt.onnx`, `modelopt.torch._deploy` | `onnx`, `onnxruntime-gpu`, `onnx-graphsurgeon` |
| `[hf]` | HuggingFace (Transformers, Diffusers) | `transformers`, `diffusers`, `accelerate` |
| `[puzzletron]` | `modelopt.torch.puzzletron` | `hydra-core`, `pandas`, `typeguard` |
| `[all]` | Full suite | All of the above |

**System Requirements:**
* **OS:** Linux (x86_64, aarch64) [docs/source/getting_started/_installation_for_Linux.rst:11-13]()
* **Python:** >=3.10, <3.15 [docs/source/getting_started/_installation_for_Linux.rst:15](), [uv.lock:3]()
* **PyTorch:** >=2.8 [docs/source/getting_started/_installation_for_Linux.rst:19]()
* **CUDA:** 12.x or 13.x [docs/source/getting_started/_installation_for_Linux.rst:17]()

Sources: [docs/source/getting_started/_installation_for_Linux.rst:10-26](), [pyproject.toml:54-96](), [uv.lock:1-3]()

### Method 2: Windows Installation

For Windows environments, ModelOpt primarily supports ONNX-based workflows via the `[onnx]` extra.

**Standalone Installation:**
```bash
pip install "nvidia-modelopt[onnx]"
```

For Windows ONNX Runtime usage, ModelOpt pins `onnxruntime-gpu` to compatible versions to ensure local RTX GPU support.

Sources: [pyproject.toml:64-70](), [docs/source/getting_started/_installation_for_Linux.rst:136](), [examples/windows/onnx_ptq/genai_llm/README.md:12-19]()

### Method 3: Docker Containers (Recommended for Linux)

NVIDIA provides pre-configured containers where ModelOpt is pre-installed. It is recommended to upgrade to the latest version inside the container using `pip install -U`.

*   **TensorRT-LLM:** `nvcr.io/nvidia/tensorrt-llm/release:<version>` [docs/source/getting_started/_installation_for_Linux.rst:35]()
*   **PyTorch:** `nvcr.io/nvidia/pytorch:<version>-py3` [docs/source/getting_started/_installation_for_Linux.rst:51]()
*   **NeMo:** `nvcr.io/nvidia/nemo:<version>` [docs/source/getting_started/_installation_for_Linux.rst:53]()

```bash
export PIP_CONSTRAINT=""
pip install -U "nvidia-modelopt[all]"
```

Sources: [docs/source/getting_started/_installation_for_Linux.rst:31-54]()

---

## Core API Namespace Mapping

ModelOpt's functionality is partitioned into namespaces that align with the underlying framework and optimization technique. The package initialization in `modelopt/torch/__init__.py` exposes these sub-packages.

**Code Entity Mapping: Optimization Namespaces**
```mermaid
graph LR
    subgraph "modelopt.torch"
        "torch_quant"["modelopt.torch.quantization"]
        "torch_prune"["modelopt.torch.prune"]
        "torch_distill"["modelopt.torch.distill"]
        "torch_spec"["modelopt.torch.speculative"]
        "torch_sparse"["modelopt.torch.sparsity"]
        "torch_nas"["modelopt.torch.nas"]
    end

    subgraph "modelopt.onnx"
        "onnx_quant"["modelopt.onnx.quantization"]
        "onnx_autocast"["modelopt.onnx.autocast"]
    end

    "torch_quant" --> "mtq_api"["mtq.quantize()"]
    "torch_prune" --> "mtp_api"["mtp.prune()"]
    "torch_spec" --> "mtsp_api"["mtsp.convert()"]
    "onnx_quant" --> "moq_api"["quantize()"]
```
Sources: [modelopt/torch/__init__.py:26-36](), [README.md:18-25]()

| Namespace | Role | Primary Use Case |
|-----------|------|------------------|
| `modelopt.torch.quantization` | PTQ/QAT for PyTorch | Quantizing LLMs/VLMs for TensorRT-LLM [README.md:25]() |
| `modelopt.torch.prune` | Model Pruning | Reducing model width/depth (Minitron) [README.md:18]() |
| `modelopt.torch.speculative` | Speculative Decoding | Training/Converting EAGLE or Medusa heads [README.md:18]() |
| `modelopt.torch.sparsity` | Sparsity | 2:4 structured sparsity [README.md:18]() |
| `modelopt.onnx.quantization` | ONNX Quantization | Quantizing ONNX graphs for TensorRT/ORT [examples/windows/onnx_ptq/genai_llm/README.md:12-19]() |

Sources: [modelopt/torch/__init__.py:26-36](), [README.md:18-22]()

---

## Quickstart: Post-Training Quantization (PTQ)

PTQ is the standard workflow for compressing models without retraining. The process typically involves three steps: `quantize` (inserting quantizers), `calibrate` (collecting statistics), and `export`.

### Basic PyTorch PTQ Workflow

The following example demonstrates a standard Hugging Face model quantization flow using `modelopt.torch.quantization` (aliased as `mtq`).

```python
import modelopt.torch.quantization as mtq
from transformers import AutoModelForCausalLM

# 1. Load model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B", device_map="auto")

# 2. Apply quantization mode (e.g., FP8)
# This replaces standard layers with quantized versions using a recipe
model = mtq.quantize(model, mtq.FP8_DEFAULT_CFG)

# 3. Calibrate
# Use a representative dataset to find optimal scaling factors
def calibration_loop(model):
    for batch in dataloader:
        model(batch)

mtq.calibrate(model, calibration_loop)

# 4. Export for deployment
from modelopt.torch.export import export_hf_checkpoint
export_hf_checkpoint(model, "./quantized_llama")
```

Sources: [README.md:22-25](), [modelopt/torch/__init__.py:32](), [examples/windows/onnx_ptq/genai_llm/quantize.py:29]()

---

## Accelerated Quantization with Triton Kernels

ModelOpt includes optimized kernels implemented with the Triton language that accelerate quantization operations by approximately 40% compared to default implementations. These are particularly beneficial for **AWQ** and **Quantization-aware Training (QAT)** workflows.

**Requirements for Triton Kernels:**
*   **Hardware:** CUDA device with compute capability >= 8.9 (e.g., RTX 40 series, RTX 6000 Ada, L40, H100) [docs/source/getting_started/_installation_for_Linux.rst:147]().
*   **Software:** `pip install triton` [docs/source/getting_started/_installation_for_Linux.rst:148]().

The optimized kernels are used automatically when compatible hardware and the `triton` package are detected.

Sources: [docs/source/getting_started/_installation_for_Linux.rst:138-151]()

---

## Verification and Testing

ModelOpt uses `nox` and `pytest` for its testing framework. The `noxfile.py` defines sessions for various environments, including CPU-only unit tests and specialized GPU sessions for Megatron or TensorRT-LLM.

| Test Suite | Command | Context |
|------------|---------|---------|
| Unit Tests | `nox -s unit` | General logic across Python versions |
| GPU Tests | `nox -s gpu` | Quantization kernels and GPU logic |
| Megatron | `nox -s gpu_megatron` | Distributed training/pruning in NeMo containers |
| TensorRT-LLM | `nox -s gpu_trtllm` | Export and deployment in TRT-LLM containers |

Sources: [noxfile.py:18-24](), [noxfile.py:69-150](), [CONTRIBUTING.md:24-31]()

### Manual Verification
To check if ModelOpt is correctly installed and its version is compatible with your environment:
```python
import modelopt.torch
print("ModelOpt initialized successfully")
```
Note that `modelopt.torch` performs version checks for `torch` and `transformers` at import time and will issue warnings if versions are outside the tested range.

Sources: [docs/source/getting_started/_installation_for_Linux.rst:153-156](), [modelopt/torch/__init__.py:43-69]()

---

