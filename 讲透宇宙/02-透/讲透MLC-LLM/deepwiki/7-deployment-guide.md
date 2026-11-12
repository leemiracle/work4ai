> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/7-deployment-guide](https://deepwiki.com/mlc-ai/mlc-llm/7-deployment-guide)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Deployment Guide

  Relevant source files 
 - [.gitmodules](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/.gitmodules)
 - [CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/CMakeLists.txt)
 - [android/MLCChat/mlc-package-config.json](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/MLCChat/mlc-package-config.json)
 - [android/mlc4j/CMakeLists.txt](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt)
 - [android/mlc4j/prepare_libs.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/prepare_libs.py)
 - [android/mlc4j/src/cpp/tvm_runtime.h](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/src/cpp/tvm_runtime.h)
 - [docs/community/faq.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/community/faq.rst)
 - [docs/compilation/compile_models.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst)
 - [docs/compilation/convert_weights.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/convert_weights.rst)
 - [docs/deploy/android.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/android.rst)
 - [docs/deploy/cli.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst)
 - [docs/deploy/ios.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst)
 - [docs/deploy/mlc_chat_config.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/mlc_chat_config.rst)
 - [docs/index.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst)
 - [docs/install/gpu.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/install/gpu.rst)
 - [docs/install/mlc_llm.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/install/mlc_llm.rst)
 - [docs/install/tvm.rst](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/install/tvm.rst)
 - [ios/MLCSwift/Package.swift](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Package.swift)
 - [ios/MLCSwift/Sources/ObjC/LLMEngine.mm](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm)
 - [python/mlc_llm/base.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/base.py)
 - [python/mlc_llm/cli/package.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/package.py)
 - [web/Makefile](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/Makefile)
 - [web/emcc/mlc_wasm_runtime.cc](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/emcc/mlc_wasm_runtime.cc)
 
  This page is the high-level entry point for deploying MLC LLM across its supported runtime targets. It summarizes the deployment modes, the shared artifact model required by all targets, and points to the platform-specific sub-pages.

 MLC LLM serves as a machine learning compiler and high-performance deployment engine, enabling native execution of AI models on a variety of hardware [docs/index.rst9-11](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst#L9-L11)

 
---

 
## Supported Deployment Targets

 MLC LLM runs the same compiled model artifacts on a wide range of hardware and environments. The target determines which GPU backend and binary format are used.

 
| Target | OS | Backend | Output Format |
|---|---|---|---|
| cuda | Linux, Windows | NVIDIA CUDA | .so |
| rocm | Linux, Windows | AMD ROCm | .so |
| vulkan | Linux, Windows | Vulkan | .so / .dll |
| metal | macOS | Metal | .so / .dylib |
| iphone | iOS / iPadOS | Metal (Apple A-series) | .tar / .a (static lib) |
| android | Android | OpenCL / Vulkan | .so / .a (static lib) |
| webgpu | Browser | WebGPU + WASM | .wasm |

 Sources: [docs/install/tvm.rst141-158](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/install/tvm.rst#L141-L158) [docs/compilation/compile_models.rst111-180](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L111-L180)

 
---

 
## Required Artifacts

 Every deployment target consumes three artifact types produced by the [Compilation System](https://deepwiki.com/mlc-ai/mlc-llm/4-compilation-system).

 **Deployment artifact structure (example: `dist/` directory)**

 
```
dist/
├── libs/
│   └── RedPajama-INCITE-Chat-3B-v1-q4f16_1-cuda.so   # Model library (kernels)
└── RedPajama-INCITE-Chat-3B-v1-q4f16_1-MLC/
    ├── mlc-chat-config.json                            # Chat/Generation config
    ├── tensor-cache.json                               # Weight shard index
    ├── params_shard_0.bin                              # Quantized weights
    ├── params_shard_1.bin
    ├── tokenizer.json                                  # HuggingFace/SentencePiece
    └── tokenizer_config.json
```

 
| Artifact | Produced by | Description |
|---|---|---|
| Model library (.so/.a/.wasm) | mlc_llm compile | Compiled inference logic and kernels for a specific platform docs/compilation/compile_models.rst9-14 |
| mlc-chat-config.json | mlc_llm gen_config | Metadata (context window, prefill chunk size) and conversation templates docs/compilation/compile_models.rst95-102 |
| Weight shards (params_shard_*.bin) | mlc_llm convert_weight | Quantized model weights in MLC-compatible format docs/compilation/convert_weights.rst6-9 |

 Sources: [docs/compilation/compile_models.rst6-14](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L6-L14) [docs/compilation/convert_weights.rst112-124](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/convert_weights.rst#L112-L124)

 
---

 
## Deployment Modes Overview

 The diagram below maps each deployment mode to its entry point and the underlying engine component it uses.

 **Deployment modes and their code-level entry points**

 
```

```

 Sources: [docs/deploy/cli.rst1-23](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L1-L23) [docs/deploy/ios.rst71-95](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L71-L95) [docs/deploy/android.rst138-165](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/android.rst#L138-L165)

 
---

 
## Compilation-to-Deployment Pipeline

 The following diagram shows how platform-specific compilation feeds into each deployment channel.

 **From source model to runtime: tools and targets**

 
```

```

 
> **Note:** For Python API usage, if `model_lib` is not specified, the system triggers JIT compilation via `jit.py` [docs/compilation/compile_models.rst20-21](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L20-L21)

 Sources: [docs/compilation/compile_models.rst88-121](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/compilation/compile_models.rst#L88-L121) [docs/deploy/ios.rst54-81](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L54-L81) [docs/deploy/android.rst121-149](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/android.rst#L121-L149)

 
---

 
## Sub-page Index

 
| Sub-page | Scope |
|---|---|
| Command-Line Tools | Full reference for convert_weight, gen_config, compile, chat, serve, and package docs/compilation/compile_models.rst54-57 |
| Server Deployment | REST API setup via mlc_llm serve, speculative decoding, and OpenAI-compatible client integration docs/index.rst38 |
| Mobile Deployment | Android (NDK, mlc4j) and iOS (MLCSwift, prepare_libs.sh) build workflows docs/deploy/ios.rst1-12 docs/deploy/android.rst1-24 |
| Web Deployment | WebGPU/WASM compilation using emcc and WebLLM integration docs/index.rst37 |

 
---

 
## Platform-Specific Notes

 
### Desktop / Server (Linux, macOS, Windows)

 
 - **Interactive Chat**: Use `mlc_llm chat` for terminal sessions [docs/deploy/cli.rst29-35](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L29-L35)
 - **REST API**: Use `mlc_llm serve` for OpenAI-compatible endpoints.
 - **Multi-GPU**: Enable tensor parallelism via `--overrides "tensor_parallel_shards=N"` [docs/deploy/cli.rst58-62](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L58-L62)
 
 
### iOS and Android

 
 - **Packaging**: Use `mlc_llm package` to bundle models and runtimes into static libraries (`.a`) [docs/deploy/ios.rst73-79](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L73-L79) [docs/deploy/android.rst140-146](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/android.rst#L140-L146)
 - **Config**: Mobile apps use `mlc-package-config.json` to define the `model_list` and VRAM estimations [docs/deploy/ios.rst57-64](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L57-L64) [android/MLCChat/mlc-package-config.json1-51](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/MLCChat/mlc-package-config.json#L1-L51)
 - **Integration**: iOS uses `MLCSwift` and `LLMEngine.mm` [ios/MLCSwift/Sources/ObjC/LLMEngine.mm1-10](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/ios/MLCSwift/Sources/ObjC/LLMEngine.mm#L1-L10); Android uses `mlc4j` with JNI bindings [android/mlc4j/CMakeLists.txt49-51](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/mlc4j/CMakeLists.txt#L49-L51)
 
 
### Web Browser

 
 - **WASM**: Models are compiled to WASM modules using `emcc` [web/Makefile1-10](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/web/Makefile#L1-L10)
 - **Runtime**: Consumed by the `WebLLM` package via WebGPU [docs/index.rst37](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/index.rst#L37-L37)
 
 Sources: [docs/deploy/cli.rst58-62](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/cli.rst#L58-L62) [docs/deploy/ios.rst73-79](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/ios.rst#L73-L79) [docs/deploy/android.rst140-146](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/docs/deploy/android.rst#L140-L146) [android/MLCChat/mlc-package-config.json1-51](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/android/MLCChat/mlc-package-config.json#L1-L51)
