> 来源: [https://deepwiki.com/mozilla-ai/llamafile/12-localscore-benchmarking](https://deepwiki.com/mozilla-ai/llamafile/12-localscore-benchmarking)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# LocalScore Benchmarking

  Relevant source files 
 - [localscore/README.md](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1)
 - [localscore/ascii_digits.h](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/ascii_digits.h)
 - [localscore/cmd.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp)
 - [localscore/cmd.h](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.h)
 - [localscore/localscore.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp)
 - [localscore/system.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp)
 - [localscore/utils.h](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/utils.h)
 
  LocalScore is an open-source benchmarking tool integrated into the llamafile ecosystem, designed to measure the performance of Large Language Models (LLMs) on specific hardware configurations [localscore/README.md1-3](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L1-L3) It provides standardized metrics for prompt processing and text generation, enabling users to evaluate their hardware's efficiency and optionally contribute to a global public database at [localscore.ai](https://localscore.ai) [localscore/README.md5-6](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L5-L6)

 
### Overview of Capabilities

 LocalScore automates the process of loading a model, performing a warmup run to stabilize hardware states, and executing multiple iterations of inference to gather statistically significant performance data [localscore/localscore.cpp134-174](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L134-L174)

 
 - **Standardized Metrics**: Measures Prompt Processing (TPS), Generation Speed (TPS), and Time to First Token (TTFT) [localscore/README.md26-30](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L26-L30)
 - **Hardware Detection**: Automatically identifies CPU architectures, GPU models, RAM capacity, and OS kernel details [localscore/system.cpp178-205](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L178-L205)
 - **Multi-Backend Support**: Leverages llamafile's compute backends, supporting CPU, NVIDIA (CUDA), AMD (ROCm), and Apple Silicon (Metal) [localscore/README.md20-21](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L20-L21)
 - **Result Submission**: Provides an optional pipeline to submit JSON-formatted benchmark results to a central leaderboard [localscore/localscore.cpp176-220](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L176-L220)
 
 
### High-Level Architecture

 The benchmarking system is built as a specialized CLI wrapper around the `llama.cpp` and `llamafile` core libraries. It uses a `cmd_params` structure to manage benchmark-specific configurations like repetition counts and output formats [localscore/cmd.h10-38](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.h#L10-L38)

 
#### System Entity Mapping

 The following diagram illustrates how LocalScore components map to specific code entities and how they interact with the underlying llamafile infrastructure.

 **LocalScore System Components**

 
```

```

 Sources: [localscore/localscore.cpp134-174](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L134-L174) [localscore/cmd.cpp34-68](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L34-L68) [localscore/system.cpp178-195](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L178-L195) [localscore/cmd.h10-38](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.h#L10-L38)

 
### Benchmark Metrics and Scoring

 LocalScore evaluates hardware using a composite "LocalScore" value. This score is calculated as the geometric mean of three primary metrics: Prompt Tokens Per Second (TPS), Generation TPS, and the inverse of Time to First Token (TTFT) [localscore/README.md32-34](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L32-L34)

 The tool supports various execution modes to ensure reliability:

 
 - **Standard**: Single run for quick checks [localscore/cmd.cpp27](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L27-L27)
 - **Extended**: 4 repetitions (`--extended`) [localscore/cmd.cpp136-137](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L136-L137)
 - **Long**: 16 repetitions (`--long`) [localscore/cmd.cpp138-139](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L138-L139)
 
 The utility functions in `utils.h` provide the mathematical foundation for these calculations, including `utils::avg` for mean performance and `utils::stdev` for measuring variance across repetitions [localscore/utils.h61-79](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/utils.h#L61-L79)

 For detailed information on the scoring formula, statistical methods, and output formats (CSV, JSON, Markdown), see **[Benchmark Metrics and Scoring](https://deepwiki.com/mozilla-ai/llamafile/12.1-benchmark-metrics-and-scoring)**.

 Sources: [localscore/README.md32-34](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L32-L34) [localscore/utils.h61-79](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/utils.h#L61-L79) [localscore/cmd.cpp136-144](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L136-L144)

 
### Hardware Detection and Result Submission

 Before running tests, LocalScore performs deep inspection of the host system. It uses `cpuid` on x86_64 systems to identify CPU manufacturers and models [localscore/system.cpp21-56](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L21-L56) and queries system-specific APIs (like `sysctlbyname` on macOS or `/proc/cpuinfo` on Linux) to determine core counts and architecture features [localscore/system.cpp74-124](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L74-L124)

 **Hardware Data Flow**

 
```

```

 Sources: [localscore/system.cpp21-56](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L21-L56) [localscore/system.cpp169-177](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/system.cpp#L169-L177) [localscore/localscore.cpp204-208](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L204-L208)

 Users can choose to submit these results to the public database. The submission process includes a privacy-conscious sanitization step using `utils::sanitize_string` that ensures only non-personally identifiable information (CPU/GPU specs, RAM, and performance) is uploaded [localscore/localscore.cpp176-186](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L176-L186) [localscore/README.md149-157](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L149-L157) [localscore/utils.h168-175](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/utils.h#L168-L175)

 For details on GPU backend selection, power sampling, and the submission API, see **[Hardware Detection and Result Submission](https://deepwiki.com/mozilla-ai/llamafile/12.2-hardware-detection-and-result-submission)**.

 
### Execution Modes

 LocalScore can be executed in several ways depending on the user's environment:

 
 - **Standalone**: Running the `localscore` binary with a GGUF model path via `-m` or `--model` [localscore/README.md61-62](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L61-L62)
 - **Llamafile Integration**: Using the `--bench` flag on any llamafile (v0.9.2+) [localscore/README.md71-83](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L71-L83)
 - **Direct Build**: Building from source within the llamafile repository using the standard build instructions [localscore/README.md45](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L45-L45)
 
 The tool also provides visual feedback using ASCII art for scores and logos [localscore/ascii_digits.h18-60](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/ascii_digits.h#L18-L60) and supports terminal colorization based on environment variables [localscore/utils.h189-202](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/utils.h#L189-L202)

 Sources: [localscore/README.md47-107](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/README.md?plain=1#L47-L107) [localscore/localscore.cpp130-132](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/localscore.cpp#L130-L132) [localscore/cmd.cpp70-155](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/cmd.cpp#L70-L155) [localscore/ascii_digits.h54-60](https://github.com/mozilla-ai/llamafile/blob/43551265/localscore/ascii_digits.h#L54-L60)
