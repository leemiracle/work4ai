> 来源: [https://deepwiki.com/mozilla-ai/llamafile/11-debugging-and-diagnostics](https://deepwiki.com/mozilla-ai/llamafile/11-debugging-and-diagnostics)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Debugging and Diagnostics

  Relevant source files 
 - [llamafile/check_cpu.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c)
 - [llamafile/fa_helpers_amd_avx512f.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_helpers_amd_avx512f.cpp)
 - [llamafile/fa_helpers_unsupported.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_helpers_unsupported.cpp)
 - [llamafile/fa_simd_gemm_amd_avx512f.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_simd_gemm_amd_avx512f.cpp)
 - [tests/fa_helpers_test.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/fa_helpers_test.cpp)
 
  
## Purpose and Scope

 This document describes llamafile's debugging and diagnostic infrastructure for detecting, diagnosing, and recovering from runtime errors during model inference. The system provides floating-point exception trapping, computation graph dumping, backtrace generation, and thermal throttling prevention for benchmarking workloads. It also includes early-stage CPU feature verification to prevent illegal instruction crashes and a runtime dispatcher for optimized kernels, including specialized AVX-512F helpers for Flash-Attention.

 For details on specific subsystems, see:

 
 - [Floating-Point Exception Debugging](https://deepwiki.com/mozilla-ai/llamafile/11.1-floating-point-exception-debugging) — FPE trap handling, SIGFPE recovery, and graph dumping.
 - [Performance Monitoring](https://deepwiki.com/mozilla-ai/llamafile/11.2-performance-monitoring) — CPU temperature monitoring and core management.
 
 
---

 
## Overview

 Llamafile implements a comprehensive debugging infrastructure focused on three primary concerns:

 
 - **Numerical Stability**: Detecting and recovering from floating-point exceptions (overflow, underflow, divide-by-zero, invalid operations) during matrix operations.
 - **System Performance**: Monitoring CPU temperature and managing core allocation to prevent thermal throttling during benchmarks.
 - **Hardware Compatibility**: Ensuring the host CPU supports the microarchitecture features (AVX, FMA, etc.) required by the binary at load time, and selecting the most efficient math kernels.
 
 **Key Components:**

 
| Component | File | Purpose |
|---|---|---|
| llamafile_actually_check_cpu() | llamafile/check_cpu.c50-78 | Early CPU feature verification |
| GemmFuncs | llamafile/sgemm.cpp47-139 | Runtime dispatcher for optimized CPU kernels |
| llamafile_fa_simd_gemm_amd_avx512f | llamafile/fa_simd_gemm_amd_avx512f.cpp24-33 | AVX-512F Flash-Attention GEMM helper |
| on_sigfpe() | llamafile/debug.cpp124-194 | SIGFPE signal handler with graph dumping |
| llamafile_trapping_enabled() | llamafile/debug.cpp207-220 | Enable/disable FP exception trapping |
| CoreManager | llamafile/core_manager.cpp | CPU core acquisition and release |
| llamafile_govern() | llamafile/govern.cpp71-85 | Temperature-based throttling |

 
---

 
## Early Hardware Diagnostics

 Before inference begins, llamafile performs a mandatory check of CPU capabilities. This is implemented as a high-priority constructor `llamafile_actually_check_cpu` with priority 101 [llamafile/check_cpu.c50](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c#L50-L50)

 
### CPU Feature Verification

 The system checks for features required at build time (e.g., `__AVX2__`) and compares them against runtime detection macros like `X86_CHECK(AVX2)` [llamafile/check_cpu.c60-62](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c#L60-L62) If a required feature is missing, the process prints a fatal error and exits immediately [llamafile/check_cpu.c34-45](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c#L34-L45) It specifically checks for modern extensions like `AVX512F`, `AVX512VBMI`, and `AVX512_VNNI` if the binary was compiled to require them [llamafile/check_cpu.c69-77](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c#L69-L77)

 
```

```

 **CPU Feature Verification Flow**

 Sources: [llamafile/check_cpu.c30-78](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/check_cpu.c#L30-L78)

 
### Runtime Kernel Selection and Optimization

 Llamafile uses a dispatcher mechanism in `sgemm.cpp` to select the most efficient math kernels based on detected CPU features [llamafile/sgemm.cpp54-139](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp#L54-L139) This includes selecting optimized implementations for `sgemm`, `mixmul`, and Flash-Attention (FA) helpers [llamafile/sgemm.h89-98](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.h#L89-L98)

 For x86_64 systems with AVX-512F, llamafile provides specialized helpers such as `llamafile_fa_simd_gemm_amd_avx512f` which uses 16-lane ZMM registers to achieve roughly 2.7x peak FMA throughput compared to AVX2 [llamafile/fa_simd_gemm_amd_avx512f.cpp4-17](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_simd_gemm_amd_avx512f.cpp#L4-L17) If the CPU lacks these features, the system falls back to `llamafile_fa_simd_gemm_unsupported` which returns `false`, directing the engine to use upstream reference implementations [llamafile/fa_helpers_unsupported.cpp26-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_helpers_unsupported.cpp#L26-L29)

 
```

```

 **Mapping Kernel Dispatcher to Architecture Detection**

 Sources: [llamafile/sgemm.cpp47-139](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp#L47-L139) [llamafile/fa_simd_gemm_amd_avx512f.cpp24-33](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_simd_gemm_amd_avx512f.cpp#L24-L33) [llamafile/fa_helpers_unsupported.cpp4-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/fa_helpers_unsupported.cpp#L4-L29)

 
---

 
## Floating-Point Exception Handling

 The debugging system traps critical floating-point exceptions: `FE_INVALID`, `FE_DIVBYZERO`, and `FE_OVERFLOW` [llamafile/debug.cpp34](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L34-L34) When an exception occurs, the `on_sigfpe()` handler captures the state and, if a `ggml_cgraph` is active, dumps the failing operation to `/tmp/cgraph.txt` [llamafile/debug.cpp168-188](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L168-L188)

 To ensure these optimized kernels are numerically sound, llamafile includes a test suite `tests/fa_helpers_test.cpp` that compares the AVX-512-optimized helpers against reference `ggml-cpu` implementations, validating they are within ULP (Unit in the Last Place) tolerance [tests/fa_helpers_test.cpp18-26](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/fa_helpers_test.cpp#L18-L26)

 
```

```

 **Mapping Debugging Concepts to Code Entities**

 Sources: [llamafile/debug.cpp34-43](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L34-L43) [tests/fa_helpers_test.cpp18-31](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/fa_helpers_test.cpp#L18-L31)

 
---

 
## Performance Monitoring and Governance

 Llamafile includes tools to maintain deterministic performance, particularly during benchmarks.

 
### Core Management

 The `CoreManager` class [llamafile/core_manager.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/core_manager.cpp) provides thread-safe CPU core allocation. It uses a two-phase acquisition strategy: blocking until a minimum number of cores are available (`need`), then optionally taking more if idle (`greed`) [llamafile/core_manager.cpp38-70](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/core_manager.cpp#L38-L70)

 
### Thermal Governance

 The `llamafile_govern()` function [llamafile/govern.cpp71-85](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/govern.cpp#L71-L85) implements a temperature-based pause loop. It reads from a system thermal file (e.g., `/sys/class/hwmon/...`) and pauses execution with exponential backoff if the temperature exceeds `LLAMAFILE_TEMPERATURE_MAX` [llamafile/govern.cpp42-69](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/govern.cpp#L42-L69)

 For details on core allocation logic and thermal monitoring setup, see [Performance Monitoring](https://deepwiki.com/mozilla-ai/llamafile/11.2-performance-monitoring).

 Sources: [llamafile/core_manager.cpp38-84](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/core_manager.cpp#L38-L84) [llamafile/govern.cpp71-85](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/govern.cpp#L71-L85)

 
---

 
## Underflow Visual Warnings

 Underflow exceptions (`FE_UNDERFLOW`) are treated as non-fatal but noteworthy. If the process is running in a terminal, llamafile displays a transient "UNDERFLOW" warning in the top-left corner using ANSI escape sequences [llamafile/debug.cpp35-37](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L35-L37) This warning is automatically cleared by `llamafile_trapping_restore()` after a 2-second delay [llamafile/debug.cpp222-236](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L222-L236)

 Sources: [llamafile/debug.cpp35-37](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L35-L37) [llamafile/debug.cpp131-140](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L131-L140) [llamafile/debug.cpp222-236](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/debug.cpp#L222-L236)
