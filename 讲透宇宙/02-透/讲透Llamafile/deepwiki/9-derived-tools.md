> 来源: [https://deepwiki.com/mozilla-ai/llamafile/9-derived-tools](https://deepwiki.com/mozilla-ai/llamafile/9-derived-tools)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Derived Tools

  Relevant source files 
 - [diffusionfile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/diffusionfile/BUILD.mk)
 - [tests/transcribefile_smoke.sh](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/transcribefile_smoke.sh)
 - [transcribe.cpp.patches/llamafile-files/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribe.cpp.patches/llamafile-files/BUILD.mk)
 - [transcribefile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/BUILD.mk)
 - [transcribefile/main.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp)
 - [whisperfile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk)
 - [whisperfile/whisperfile.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp)
 
  The llamafile framework extends beyond text-based Large Language Models (LLMs). By leveraging the same core technologies—**Cosmopolitan Libc**, **GGML**, and the **Actually Portable Executable (APE)** format—the project provides a family of specialized tools for speech-to-text transcription and image generation.

 These tools share the llamafile philosophy: they are distributed as single-file executables that run on multiple platforms (Linux, macOS, Windows, etc.) with high-performance CPU and GPU acceleration.

 
### Overview of the Tool Family

 
| Tool | Core Engine | Primary Function | Key Features |
|---|---|---|---|
| whisperfile | whisper.cpp | Speech-to-Text | HTTP Server, real-time streaming, CLI. |
| transcribefile | transcribe.cpp | Multi-model Transcription | Supports 16+ model families (Parakeet, Canary, etc.). |
| diffusionfile | stable-diffusion.cpp | Image Generation | CLI-based image generation with GPU support. |

 The relationship between the shared llamafile infrastructure and these derived tools is illustrated below:

 **System Component Relationship**

 
```

```

 Sources: [whisperfile/BUILD.mk100-104](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L100-L104) [transcribefile/BUILD.mk76-80](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/BUILD.mk#L76-L80) [diffusionfile/BUILD.mk76-80](https://github.com/mozilla-ai/llamafile/blob/43551265/diffusionfile/BUILD.mk#L76-L80) [transcribefile/main.cpp27](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L27-L27) [whisperfile/whisperfile.cpp27](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L27-L27)

 
---

 
### Whisperfile

 `whisperfile` is a high-performance speech-to-text tool built on the `whisper.cpp` engine. It provides a suite of executables for different use cases, including a CLI for batch processing, an OpenAI-compatible HTTP server, and real-time microphone streaming.

 
 - **Key Entry Point**: `whisperfile/whisperfile.cpp` [whisperfile/whisperfile.cpp29-48](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L29-L48)
 - **Integration**: It renames the upstream `main()` to `whisper_cli_main()` via `-DWHISPERFILE` and wraps it with llamafile features like `llamafile_check_cpu()` and `cosmo_args()` [whisperfile/whisperfile.cpp25-42](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L25-L42)
 - **Executables**: 
 - `whisperfile`: Standard CLI transcription [whisperfile/BUILD.mk115-125](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L115-L125)
 - `whisper-server`: HTTP API server [whisperfile/BUILD.mk161-171](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L161-L171)
 - `stream`: Real-time microphone transcription [whisperfile/BUILD.mk128-136](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L128-L136)
 - `mic2txt`: Record-then-transcribe utility [whisperfile/BUILD.mk139-147](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L139-L147)
 
 For details, see [Whisperfile](https://deepwiki.com/mozilla-ai/llamafile/9.1-whisperfile).

 
---

 
### Transcribefile

 `transcribefile` is a specialized transcription CLI built on `transcribe.cpp`. Unlike whisperfile, which focuses on the Whisper architecture, transcribefile supports a wide array of modern model families including Parakeet, Canary, Voxtral, and Moonshine.

 
 - **Key Entry Point**: `transcribefile/main.cpp` [transcribefile/main.cpp114-158](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L114-L158)
 - **Model Support**: Supports 16+ families (e.g., `arch/parakeet`, `arch/canary`, `arch/cohere`) by linking against a comprehensive `transcribe.cpp.a` library [transcribe.cpp.patches/llamafile-files/BUILD.mk140-165](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribe.cpp.patches/llamafile-files/BUILD.mk#L140-L165)
 - **GPU Support**: Currently features a runtime-compiled Metal backend for macOS/Apple Silicon, managed by `llamafile_has_metal()` [transcribefile/main.cpp89-112](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L89-L112)
 - **Packaging**: Uses `cosmo_args("/zip/.args", &argv)` to allow bundling GGUF models directly inside the executable using `zipalign` [transcribefile/main.cpp132-134](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L132-L134)
 
 For details, see [Transcribefile](https://deepwiki.com/mozilla-ai/llamafile/9.2-transcribefile).

 
---

 
### Diffusionfile

 `diffusionfile` provides image generation capabilities by integrating `stable-diffusion.cpp`. It allows users to generate images from text prompts using various Stable Diffusion models.

 
 - **Key Entry Point**: `diffusionfile/diffusionfile.cpp` [diffusionfile/diffusionfile.cpp28-43](https://github.com/mozilla-ai/llamafile/blob/43551265/diffusionfile/diffusionfile.cpp#L28-L43)
 - **Integration**: Similar to the transcription tools, it renames the upstream entry point to `diffusion_cli_main()` [diffusionfile/BUILD.mk93-97](https://github.com/mozilla-ai/llamafile/blob/43551265/diffusionfile/BUILD.mk#L93-L97)
 - **Math Compatibility**: Includes a specialized `sd_math_shim.o` to ensure compatibility between llamafile's environment and the requirements of `stable-diffusion.cpp` [diffusionfile/BUILD.mk100](https://github.com/mozilla-ai/llamafile/blob/43551265/diffusionfile/BUILD.mk#L100-L100)
 
 For details, see [Diffusionfile](https://deepwiki.com/mozilla-ai/llamafile/9.3-diffusionfile).

 
---

 
### Shared Implementation Patterns

 All derived tools follow a consistent architectural pattern to maintain portability and feature parity with the main `llamafile` project.

 **Execution Flow for Derived Tools**

 
```

```

 Sources: [transcribefile/main.cpp114-158](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L114-L158) [whisperfile/whisperfile.cpp29-48](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L29-L48) [transcribefile/main.cpp89-112](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L89-L112) [transcribefile/main.cpp134](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L134-L134)

 
#### Common Characteristics

 
 - **Argument Injection**: They all use `cosmo_args()` to read a `.args` file from the embedded ZIP store, enabling "zero-config" executables where the model and parameters are pre-baked [transcribefile/main.cpp134](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L134-L134) [whisperfile/whisperfile.cpp41](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L41-L41)
 - **GPU Runtime Loading**: They utilize the `gpu.a` library and `llamafile/llamafile.o` to handle dynamic loading of GPU backends (CUDA, Metal, ROCm) at runtime [whisperfile/BUILD.mk100-104](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/BUILD.mk#L100-L104) [transcribefile/BUILD.mk76-80](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/BUILD.mk#L76-L80)
 - **Crash Reporting**: They invoke `ShowCrashReports()` to provide symbolized backtraces across different operating systems [transcribefile/main.cpp116](https://github.com/mozilla-ai/llamafile/blob/43551265/transcribefile/main.cpp#L116-L116) [whisperfile/whisperfile.cpp32](https://github.com/mozilla-ai/llamafile/blob/43551265/whisperfile/whisperfile.cpp#L32-L32)
