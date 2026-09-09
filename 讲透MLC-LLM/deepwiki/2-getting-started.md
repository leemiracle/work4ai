> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/2-getting-started](https://deepwiki.com/mlc-ai/mlc-llm/2-getting-started)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Getting Started

  Relevant source files 
 - [docs/_static/img/project-workflow.svg](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/_static/img/project-workflow.svg)
 - [docs/community/guideline.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/community/guideline.rst)
 - [docs/compilation/compile_models.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst)
 - [docs/compilation/convert_weights.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/convert_weights.rst)
 - [docs/compilation/define_new_models.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/define_new_models.rst)
 - [docs/deploy/cli.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst)
 - [docs/deploy/ios.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst)
 - [docs/deploy/mlc_chat_config.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/mlc_chat_config.rst)
 - [docs/deploy/python_engine.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/python_engine.rst)
 - [docs/get_started/introduction.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/introduction.rst)
 - [docs/get_started/quick_start.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/quick_start.rst)
 - [docs/index.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst)
 - [examples/python/sample_mlc_engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/examples/python/sample_mlc_engine.py)
 - [python/mlc_llm/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/__init__.py)
 - [python/mlc_llm/cli/delivery.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/delivery.py)
 - [python/mlc_llm/support/auto_config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/support/auto_config.py)
 - [python/mlc_llm/support/constants.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/support/constants.py)
 - [python/mlc_llm/support/download_cache.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/support/download_cache.py)
 - [python/mlc_llm/testing/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/testing/__init__.py)
 - [python/mlc_llm/testing/pytest_utils.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/testing/pytest_utils.py)
 - [tests/python/serve/test_serve_engine_rnn.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/tests/python/serve/test_serve_engine_rnn.py)
 
  
## Purpose and Scope

 This page provides a technical guide for installing and using MLC LLM. It covers the installation of prebuilt nightly wheels, verification of the environment, and running initial inferences using the `MLCEngine` Python API and CLI tools. This guide also points to specialized workflows for mobile (Android/iOS) and Web deployment.

 Sources: [docs/index.rst9-30](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst#L9-L30) [docs/get_started/quick_start.rst4-10](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/quick_start.rst#L4-L10)

 
---

 
## Installation

 MLC LLM is distributed via `pip` as prebuilt nightly wheels. The installation requires two main components: the `mlc-llm` package (runtime and CLI) and the `mlc-ai` package (TVM Unity compiler backend).

 
### Recommended Environment

 It is highly recommended to use an isolated `conda` environment to manage dependencies.

 
```

```

 
### Installing Prebuilt Wheels

 Select the command corresponding to your operating system and hardware accelerator:

 
| Platform | Command |
|---|---|
| Linux (CUDA 12.1) | pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly-cu121 mlc-ai-nightly-cu121 |
| macOS (Metal) | pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly-cpu mlc-ai-nightly-cpu |
| Windows (Vulkan) | pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly-cpu mlc-ai-nightly-cpu |

 
### Verification

 Verify the installation by checking the package path and the CLI help message:

 
```

```

 If the command `mlc_llm` is not found, use `python -m mlc_llm --help`.

 Sources: [docs/get_started/introduction.rst17-31](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/introduction.rst#L17-L31) [docs/compilation/compile_models.rst43-70](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L43-L70) [docs/deploy/cli.rst12-23](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L12-L23)

 
---

 
## First Inference with MLCEngine

 The `MLCEngine` class provides a high-performance Python interface that is synchronous and aligns with the OpenAI API protocol. For concurrent request batching, `AsyncMLCEngine` is used.

 
### Basic Python Inference

 This example demonstrates running a 4-bit quantized Llama-3 model. MLC LLM will automatically download the weights from Hugging Face and JIT-compile the model library if it is not found in the local cache.

 
```

```

 
### Data Flow and Component Interaction

 The following diagram maps the Python API calls to the underlying C++ entities and data structures.

 **MLCEngine to C++ Core Mapping**

 
```

```

 Sources: [docs/get_started/introduction.rst93-118](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/introduction.rst#L93-L118) [docs/deploy/python_engine.rst35-63](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/python_engine.rst#L35-L63) [python/mlc_llm/serve/engine.py1-50](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine.py#L1-L50) [python/mlc_llm/chat_module.py1-100](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/chat_module.py#L1-L100)

 
---

 
## Running the Chat CLI

 The Chat CLI is a convenient tool for interactive testing. It supports multi-GPU execution via tensor parallelism.

 
```

```

 
### CLI Execution Logic

 When running `mlc_llm chat`, the system undergoes three phases:

 
 - **Weight Download**: Fetches pre-quantized weights from Hugging Face and stores them in `~/.cache/mlc_llm`.
 - **JIT Compilation**: Uses TVM to generate the binary model library (`.so` or `.dylib`).
 - **Runtime Initialization**: Launches the `JSONFFIEngine` to handle the interactive loop.
 
 Sources: [docs/get_started/introduction.rst32-70](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/get_started/introduction.rst#L32-L70) [docs/deploy/cli.rst25-64](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L25-L64) [python/mlc_llm/support/constants.py26-46](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/support/constants.py#L26-L46)

 
---

 
## Platform-Specific Guides

 MLC LLM supports a wide range of deployment targets beyond the standard Python/CLI environment.

 
### Mobile Deployment

 
 - **iOS**: Requires Xcode, Rust (for tokenizers), and CMake. Use the `mlc_llm package` command to generate the `libmlc_llm.a` and model libraries.
 - **Android**: Requires Android NDK and Rust. The workflow involves generating an APK that bundles the model library or downloads weights at runtime.
 
 
### Web Deployment

 
 - **WebGPU**: Models are compiled to WASM and WebGPU shaders. The runtime is delivered via the `WebLLM` package, which consumes `.wasm` libraries and quantized weights.
 
 
### REST Serving

 The `mlc_llm serve` command launches a FastAPI server that provides OpenAI-compatible endpoints.

 
```

```

 **Deployment Pipeline Diagram**

 
```

```

 Sources: [docs/deploy/ios.rst54-95](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L54-L95) [docs/deploy/rest.rst1-20](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/rest.rst#L1-L20) [docs/deploy/cli.rst1-10](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L1-L10) [docs/compilation/compile_models.rst1-29](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L1-L29)
