> 来源: [https://deepwiki.com/sgl-project/sglang/14-environment-and-configuration](https://deepwiki.com/sgl-project/sglang/14-environment-and-configuration)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Environment and Configuration

  Relevant source files 
 - [3rdparty/amd/wheel/sglang/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/3rdparty/amd/wheel/sglang/pyproject.toml)
 - [benchmark/deepseek_v3/README.md](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/deepseek_v3/README.md?plain=1)
 - [docker/Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/Dockerfile)
 - [docker/xeon.Dockerfile](https://github.com/sgl-project/sglang/blob/94183a8d/docker/xeon.Dockerfile)
 - [python/pyproject.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject.toml)
 - [python/pyproject_cpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_cpu.toml)
 - [python/pyproject_npu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_npu.toml)
 - [python/pyproject_other.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_other.toml)
 - [python/pyproject_xpu.toml](https://github.com/sgl-project/sglang/blob/94183a8d/python/pyproject_xpu.toml)
 - [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/engine.py)
 - [python/sglang/srt/entrypoints/http_server.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/entrypoints/http_server.py)
 - [python/sglang/srt/environ.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py)
 - [python/sglang/srt/managers/data_parallel_controller.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/data_parallel_controller.py)
 - [python/sglang/srt/managers/detokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/detokenizer_manager.py)
 - [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/io_struct.py)
 - [python/sglang/srt/managers/multi_tokenizer_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/multi_tokenizer_mixin.py)
 - [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/schedule_batch.py)
 - [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler.py)
 - [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tokenizer_manager.py)
 - [python/sglang/srt/managers/tp_worker.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/tp_worker.py)
 - [python/sglang/srt/mem_cache/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/mem_cache/common.py)
 - [python/sglang/srt/model_executor/model_runner.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py)
 - [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py)
 - [python/sglang/srt/utils/common.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py)
 - [python/sglang/version.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/version.py)
 - [scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_download_flashinfer_jit_cache.sh)
 - [scripts/ci/cuda/ci_install_dependency.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/cuda/ci_install_dependency.sh)
 - [scripts/ci/utils/install_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_protoc.sh)
 - [scripts/ci/utils/install_rust_protoc.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rust_protoc.sh)
 - [scripts/ci/utils/install_rustup.sh](https://github.com/sgl-project/sglang/blob/94183a8d/scripts/ci/utils/install_rustup.sh)
 - [sgl-model-gateway/rust-toolchain.toml](https://github.com/sgl-project/sglang/blob/94183a8d/sgl-model-gateway/rust-toolchain.toml)
 - [test/registered/unit/tools/test_get_version_tag.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/tools/test_get_version_tag.py)
 
  This page documents SGLang's environment variable system and hardware platform detection mechanisms. It covers the `Envs` singleton for centralized environment variable management, platform detection utilities, and configuration patterns used throughout the codebase.

 For model-specific configuration and loading, see [Model Configuration and Loading](https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading). For server runtime configuration via `ServerArgs`, see [Server Configuration (ServerArgs)](https://deepwiki.com/sgl-project/sglang/3.2-server-configuration-(serverargs)).

 
---

 
## Environment Variable Management System

 SGLang uses a centralized environment variable system implemented in `environ.py` to provide type-safe, validated access to configuration options. The system uses descriptor-based fields to enforce type checking and provide default values.

 
### EnvField Descriptor Architecture

 The system is built on the `EnvField` base class, which handles the interaction with `os.environ` and provides a context manager for temporary overrides [python/sglang/srt/environ.py40-49](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L40-L49)

 Title: EnvField Class Hierarchy and Lifecycle

 
```

```

 Sources: [python/sglang/srt/environ.py40-198](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L40-L198) [python/sglang/srt/environ.py242-827](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L242-L827)

 
### Type Conversion and Validation

 Each `EnvField` subclass implements type-specific parsing. The `get()` method automatically handles cases where variables are not set (returning defaults) or explicitly set to `None` [python/sglang/srt/environ.py62-81](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L62-L81)

 
| Type | Parse Implementation | Valid Values | Example |
|---|---|---|---|
| EnvBool | python/sglang/srt/environ.py139-146 | "true", "1", "yes", "y" (case-insensitive) or "false", "0", "no", "n" | SGLANG_USE_MODELSCOPE="true" |
| EnvInt | python/sglang/srt/environ.py149-154 | Any valid integer string | SGLANG_PREFETCH_BLOCK_SIZE_MB="16" |
| EnvFloat | python/sglang/srt/environ.py192-197 | Any valid float string | SGLANG_LOG_SCHEDULER_STATUS_INTERVAL="60.0" |
| EnvStr | python/sglang/srt/environ.py124-125 | Any string value | SGLANG_TORCH_COMPILE_LOG_LEVEL="DEBUG" |
| EnvTuple | python/sglang/srt/environ.py119-120 | Comma-separated values | SGLANG_DISABLED_MODEL_ARCHS="arch1,arch2" |
| EnvJSON | python/sglang/srt/environ.py129-135 | JSON string or path to JSON file | SGLANG_REASONING_PARSER_CONFIG='{"key": "val"}' |

 Sources: [python/sglang/srt/environ.py118-197](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L118-L197)

 
### Safety Features and Alias Support

 To prevent common errors, `EnvField` implements `__bool__` and `__len__` to raise `RuntimeError` if a developer attempts to use the descriptor object directly in a conditional statement without calling `.get()` [python/sglang/srt/environ.py107-116](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L107-L116)

 Additionally, the system supports deprecated aliases via `_DeprecatedEnvFallback`, allowing for smooth migrations between environment variable names while emitting warnings [python/sglang/srt/environ.py156-181](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L156-L181) For example, `SGLANG_DSA_FUSE_TOPK` falls back to `SGLANG_NSA_FUSE_TOPK` [python/sglang/srt/environ.py359](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L359-L359)

 For details, see [Environment Variables System](https://deepwiki.com/sgl-project/sglang/14.1-environment-variables-system).

 
---

 
## Hardware and Platform Detection

 SGLang supports multiple hardware platforms (NVIDIA CUDA, AMD ROCm/HIP, Huawei NPU, Intel XPU, Moore Threads MUSA, Apple Silicon MPS, and CPU) through a unified detection system. Platform-specific code paths are selected at runtime based on detection functions centralized in `sglang/srt/utils/common.py`.

 
### Platform Detection Utilities

 The framework detects hardware capabilities to enable specific optimizations like FlashInfer, DeepGEMM, or specialized attention backends. Detection relies on `torch` properties and specialized platform modules.

 Title: Hardware Platform and Backend Detection Logic

 
```

```

 Sources: [python/sglang/srt/utils/common.py131-230](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/utils/common.py#L131-L230) [python/sglang/srt/server_args.py72-106](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L72-L106) [python/sglang/srt/model_executor/model_runner.py169](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L169-L169)

 
### Platform-Specific Dispatch

 The codebase uses module-level flags and runtime checks to select platform-specific implementations. For example, `ModelRunner` uses `current_platform` to configure attention backends and memory pools [python/sglang/srt/model_executor/model_runner.py110-129](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/model_executor/model_runner.py#L110-L129) Similarly, `ServerArgs` performs validation on quantization choices based on the detected hardware, such as checking for `is_sm90_supported` for certain FP8 modes [python/sglang/srt/server_args.py96-98](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L96-L98)

 For details, see [Hardware Detection and Platform Configuration](https://deepwiki.com/sgl-project/sglang/14.2-hardware-detection-and-platform-configuration).

 
---

 
## Configuration Categories

 The `Envs` class organizes environment variables into functional categories [python/sglang/srt/environ.py242](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L242-L242)

 
### Model and File Download

 
| Variable | Type | Default | Purpose |
|---|---|---|---|
| SGLANG_USE_MODELSCOPE | EnvBool | False | Use ModelScope instead of HuggingFace for model downloads python/sglang/srt/environ.py249 |
| SGLANG_SORT_WEIGHT_FILES | EnvInt | 0 | Controls weight-file ordering for load-time I/O optimization python/sglang/srt/environ.py257 |
| SGLANG_PREFETCH_BLOCK_SIZE_MB | EnvInt | 16 | Block size for prefetching checkpoint reads python/sglang/srt/environ.py259 |

 
### Performance Tuning and Backend Selection

 
| Variable | Type | Default | Purpose |
|---|---|---|---|
| SGLANG_USE_AITER | EnvBool | False | Enable Aiter kernel support for ROCm python/sglang/srt/environ.py298 |
| SGLANG_ENABLE_JIT_DEEPGEMM | EnvBool | True | Enable JIT compilation for DeepGEMM kernels python/sglang/srt/environ.py299 |
| SGLANG_FLASHINFER_FORCE_BACKEND | EnvStr | None | Force a specific FlashInfer backend (e.g., "fa2") python/sglang/srt/environ.py318 |
| SGLANG_USE_CUDAGRAPH_FOR_PAGED_ATTENTION | EnvBool | True | Enable CUDA graphs for paged attention kernels python/sglang/srt/environ.py330 |

 Sources: [python/sglang/srt/environ.py242-334](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L242-L334)

 
---

 
## Configuration Best Practices

 
### Accessing Environment Variables

 **Always use the `envs` singleton with `.get()`:**

 
```

```

 **Never access the descriptor directly in boolean context:**

 
```

```

 Sources: [python/sglang/srt/environ.py107-116](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L107-L116)

 
### Temporary Overrides for Testing

 Use the `override()` context manager for temporary changes in unit tests. This ensures that the environment is restored even if the test fails [python/sglang/srt/environ.py90-101](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/environ.py#L90-L101)

 
---

 
## Child Pages

 
 - [Environment Variables System](https://deepwiki.com/sgl-project/sglang/14.1-environment-variables-system) — Document Envs singleton, EnvField classes, and environment variable configuration.
 - [Hardware Detection and Platform Configuration](https://deepwiki.com/sgl-project/sglang/14.2-hardware-detection-and-platform-configuration) — Explain platform detection (is_cuda, is_hip, is_npu), capability checks, and runtime dispatch.
