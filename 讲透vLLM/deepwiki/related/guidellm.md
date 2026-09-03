# guidellm

> 来源: https://deepwiki.com/vllm-project/guidellm 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.gitignore](https://github.com/vllm-project/guidellm/blob/2e6e4f47/.gitignore)
  * [.pre-commit-config.yaml](https://github.com/vllm-project/guidellm/blob/2e6e4f47/.pre-commit-config.yaml)
  * [README.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1)
  * [docs/guides/geospatial.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/geospatial.md?plain=1)
  * [docs/guides/multimodal/audio.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/audio.md?plain=1)
  * [docs/guides/multimodal/image.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/image.md?plain=1)
  * [docs/guides/multimodal/video.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/video.md?plain=1)
  * [docs/guides/multiturn.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1)
  * [docs/guides/over_saturation_stopping.md](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/over_saturation_stopping.md?plain=1)
  * [pyproject.toml](https://github.com/vllm-project/guidellm/blob/2e6e4f47/pyproject.toml)
  * [src/guidellm/__main__.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py)
  * [src/guidellm/benchmark/__init__.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/__init__.py)
  * [src/guidellm/benchmark/entrypoints.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py)
  * [src/guidellm/benchmark/progress.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/progress.py)
  * [src/guidellm/schemas/base.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/schemas/base.py)
  * [tests/unit/schemas/test_base.py](https://github.com/vllm-project/guidellm/blob/2e6e4f47/tests/unit/schemas/test_base.py)
  * [uv.lock](https://github.com/vllm-project/guidellm/blob/2e6e4f47/uv.lock)

## Purpose and Scope

GuideLLM is an SLO-aware benchmarking and evaluation platform designed for optimizing real-world Large Language Model (LLM) inference. It provides engineering and ML teams with a consistent framework for assessing model behavior, tuning deployments, and planning capacity by simulating production-like workloads against OpenAI-compatible and vLLM-native servers. [README.md9-23](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L9-L23)

This page covers the platform's purpose, key features, high-level architecture, and primary code entities. For setup, see [Getting Started](https://github.com/vllm-project/guidellm/blob/2e6e4f47/Getting Started) For detailed command-line usage, see [Command Line Interface](https://github.com/vllm-project/guidellm/blob/2e6e4f47/Command Line Interface) For in-depth architectural documentation, see [System Overview](https://github.com/vllm-project/guidellm/blob/2e6e4f47/System Overview)

## What is GuideLLM

GuideLLM evaluates how language models perform under real workloads and configurations. It generates workload patterns reflecting production usage and produces detailed reports to help teams understand system behavior, resource needs, and operational limits. [README.md23](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L23-L23)

The platform targets three primary use cases:

Use Case| Description| Key Features  
---|---|---  
**Performance Characterization**|  Measure TTFT, ITL, and throughput under controlled conditions| Captures complete latency and token-level statistics for SLO-driven evaluation. [README.md29](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L29-L29)  
**Capacity Planning**|  Identify maximum safe operating rates and saturation points| Reproducible sweeps and over-saturation detection to identify safe operating ranges. [README.md30](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L30-L30) [docs/guides/over_saturation_stopping.md1-5](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/over_saturation_stopping.md?plain=1#L1-L5)  
**SLO Validation**|  Verify latency and error rate requirements against production-like traffic| Captures full distributions for TTFT, ITL, and end-to-end behavior. [README.md29](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L29-L29)  
  
**Sources:** [README.md8-33](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L8-L33) [README.md35-47](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L35-L47)

## Key Capabilities

GuideLLM provides the following core capabilities:

**Load Generation and Scheduling**

  * Multiple scheduling strategies and profiles: `synchronous`, `concurrent`, `throughput`, `constant`, `poisson`, `sweep`, and `replay`. [src/guidellm/benchmark/entrypoints.py24](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L24-L24) [README.md41](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L41-L41)
  * Multi-process execution for high-throughput load generation via the `Scheduler` and `NonDistributedEnvironment`. [src/guidellm/benchmark/entrypoints.py39-43](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L39-L43)
  * Configurable request timing with warmup and cooldown phases via `TransientPhaseConfig`. [src/guidellm/benchmark/schemas.py26-34](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/schemas.py#L26-L34)

**Data Pipeline**

  * HuggingFace Datasets integration and local file support (JSON, CSV, JSONL, TXT, Parquet). [README.md41](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L41-L41) [docs/guides/multimodal/audio.md30-32](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/audio.md?plain=1#L30-L32)
  * Synthetic data generation via `kind=synthetic_text` with `prompt_tokens`, `output_tokens`, and `turns` for multi-turn support. [docs/guides/multiturn.md61-73](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L61-L73)
  * Multimodal support: text, image, audio, video, and geospatial workloads. [README.md55-58](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L55-L58) [docs/guides/geospatial.md7-12](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/geospatial.md?plain=1#L7-L12)

**Backend Integration**

  * Pluggable backend system via `Backend.create()` factory supporting `openai_http` and vLLM Python backends. [src/guidellm/benchmark/entrypoints.py18](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L18-L18) [src/guidellm/benchmark/entrypoints.py90-91](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L90-L91)
  * Support for various request formats including `/v1/chat/completions`, `/v1/completions`, `/v1/responses`, and `/v1/audio/transcriptions`. [docs/guides/multiturn.md43](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L43-L43) [docs/guides/multimodal/audio.md3-4](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/audio.md?plain=1#L3-L4)
  * Support for server-side conversation history and tool calling. [README.md56-57](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L56-L57) [docs/guides/multiturn.md163-173](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L163-L173)

**Metrics and Reporting**

  * Complete request statistics via `GenerativeRequestStats` and `GenerativeMetrics`. [src/guidellm/benchmark/entrypoints.py26-34](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L26-L34)
  * Latency distributions (TTFT, ITL, E2E) and token-level metrics. [README.md29-33](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L29-L33)
  * Multiple output formats: JSON, CSV, HTML, and console tables. [src/guidellm/benchmark/entrypoints.py20-23](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L20-L23) [docs/guides/multimodal/audio.md119-124](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/audio.md?plain=1#L119-L124)

**Sources:** [README.md26-66](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L26-L66) [src/guidellm/benchmark/entrypoints.py1-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L1-L55) [docs/guides/multiturn.md1-173](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L1-L173) [docs/guides/multimodal/audio.md1-134](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multimodal/audio.md?plain=1#L1-L134)

## High-Level Architecture

The following diagram shows GuideLLM's layered architecture organized by functional responsibility:

The architecture is organized into logical layers:

  1. **Interface Layer** : User-facing entry points through CLI commands [src/guidellm/__main__.py1-6](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L1-L6) and Python API [src/guidellm/benchmark/entrypoints.py53-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L53-L55)
  2. **Orchestration Layer** : Component resolution and benchmark execution via `Benchmarker`. [src/guidellm/benchmark/entrypoints.py19-24](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L19-L24)
  3. **Execution Layer** : Multi-process scheduling and environment management. [src/guidellm/benchmark/entrypoints.py39-44](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L39-L44)
  4. **Data Layer** : Dataset loading via `create_data_loader` [src/guidellm/benchmark/entrypoints.py35-39](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L35-L39) and preprocessing pipeline.
  5. **Backend Layer** : Backend abstraction [src/guidellm/benchmark/entrypoints.py18](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L18-L18) and request/response handling.
  6. **Schema Layer** : Type definitions for requests, responses, and statistics. [src/guidellm/benchmark/schemas.py26-34](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/schemas.py#L26-L34)

**Sources:** [src/guidellm/__main__.py1-7](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L1-L7) [src/guidellm/benchmark/entrypoints.py1-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L1-L55) [src/guidellm/benchmark/schemas.py26-60](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/schemas.py#L26-L60)

## Main Components

### Core Components Mapping

The following diagram maps high-level system concepts to concrete code entities:

### Component Responsibilities

Component| File Location| Primary Responsibility  
---|---|---  
`cli()`| [src/guidellm/__main__.py5-6](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L5-L6)| Top-level CLI entry point  
`Benchmarker`| [src/guidellm/benchmark/entrypoints.py19](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L19-L19)| Core class orchestrating the benchmarking process  
`resolve_backend()`| [src/guidellm/benchmark/entrypoints.py61-120](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L61-L120)| Backend instantiation, validation, and model resolution  
`resolve_tokenizer()`| [src/guidellm/benchmark/entrypoints.py122-158](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L122-L158)| Tokenizer/processor resolution for token counting  
`benchmark_generative_text()`| [src/guidellm/benchmark/entrypoints.py53](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L53-L53)| Primary functional entry point for generative benchmarking  
`GenerativeConsoleBenchmarkerProgress`| [src/guidellm/benchmark/progress.py25](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/progress.py#L25-L25)| Real-time console UI for live metric updates  
`DataLoader`| [src/guidellm/benchmark/entrypoints.py35-36](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L35-L36)| Interface for loading and iterating over datasets  
`resolve_item_from_registry()`| [src/guidellm/benchmark/entrypoints.py163-204](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L163-L204)| Generic utility for resolving components from a `RegistryMixin`  
  
**Sources:** [src/guidellm/__main__.py1-7](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L1-L7) [src/guidellm/benchmark/entrypoints.py53-204](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L53-L204) [src/guidellm/benchmark/progress.py25-29](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/progress.py#L25-L29)

## Configuration and Resolution

GuideLLM uses a layered configuration system to transform user inputs into executable benchmark components:

  1. **Resolution Functions** : Functions like `resolve_backend` and `resolve_tokenizer` convert user-provided arguments into concrete instances, performing validation and model discovery. [src/guidellm/benchmark/entrypoints.py61-158](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L61-L158)
  2. **Registry System** : The `resolve_item_from_registry` function uses `RegistryMixin` to look up classes by string identifiers (e.g., "poisson", "huggingface") and instantiate them with provided keyword arguments. [src/guidellm/benchmark/entrypoints.py163-204](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L163-L204)
  3. **Pydantic Schemas** : Arguments and outputs are validated using Pydantic models like `BenchmarkArgs`, `BackendArgs`, and `ProfileArgs`. [src/guidellm/benchmark/schemas.py26-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/schemas.py#L26-L55)

**Sources:** [src/guidellm/benchmark/entrypoints.py61-204](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L61-L204) [src/guidellm/benchmark/schemas.py26-60](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/schemas.py#L26-L60)

## Summary

GuideLLM provides a comprehensive platform for LLM inference benchmarking with:

  * **Entry Points** : CLI (`guidellm` command) and Python API (`benchmark_generative_text()`). [src/guidellm/__main__.py1-7](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L1-L7) [src/guidellm/benchmark/entrypoints.py53-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L53-L55)
  * **Architecture** : Layered design supporting extensible backends, data pipelines, and scheduling strategies. [src/guidellm/benchmark/entrypoints.py1-55](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L1-L55)
  * **Key Features** : SLO-aware metrics, multimodal support (Audio, Video, Image, Geospatial), and multi-turn conversation simulation. [README.md26-66](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L26-L66) [docs/guides/multiturn.md1-4](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L1-L4)
  * **Data Support** : Seamless integration with HuggingFace, local files, and complex synthetic data generation. [README.md41](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L41-L41) [docs/guides/multiturn.md61-110](https://github.com/vllm-project/guidellm/blob/2e6e4f47/docs/guides/multiturn.md?plain=1#L61-L110)

**Sources:** [README.md8-66](https://github.com/vllm-project/guidellm/blob/2e6e4f47/README.md?plain=1#L8-L66) [src/guidellm/__main__.py1-7](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/__main__.py#L1-L7) [src/guidellm/benchmark/entrypoints.py1-204](https://github.com/vllm-project/guidellm/blob/2e6e4f47/src/guidellm/benchmark/entrypoints.py#L1-L204)
