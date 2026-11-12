<!-- source: DeepWiki mcp.deepwiki.com · repo cactus-compute/needle · page 1 Needle: Overview · fetched 2026-10-26 -->

# Needle: Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [assets/banner.svg](assets/banner.svg)
- [assets/benchmarks.svg](assets/benchmarks.svg)
- [assets/deploy.svg](assets/deploy.svg)
- [assets/finetune.svg](assets/finetune.svg)
- [assets/model.svg](assets/model.svg)
- [assets/whistle-benchmarks.svg](assets/whistle-benchmarks.svg)
- [assets/whistle.svg](assets/whistle.svg)
- [llms.txt](llms.txt)

</details>



Needle is a compact foundation model designed for on-device tool calling, device control, and structured extraction across mobiles, wearables, robotics, and microcontrollers [README.md:3-5](), [llms.txt:3](). Built on a **Laddered Simple Attention Network (SAN)** architecture, Needle trades general chat capacity to optimize for exact tool invocation, typed data extraction, and local text embedding at speeds suitable for resource-constrained hardware [README.md:3-11](). 

The project provides a complete vertical stack, including a high-level Python API with automatic tool schema generation, grammar-constrained decoding, local LoRA fine-tuning, the Whistle speech-to-text pipeline, and integration with the hosted Cactus Platform [README.md:7-13](), [README.md:47-60](), [llms.txt:3-4](). Visual architectural references, benchmark assets, and diagrams are housed in the repository's `assets/` directory (such as `assets/banner.svg` and `assets/model.svg`), while `llms.txt` provides an architectural summary tailored for AI coding assistants [README.md:1-12](), [llms.txt:1-5]().

Sources: [README.md:1-12](), [llms.txt:1-5]()

---

## Generations: Needle 2 vs. Needle 3

Needle 3 introduces a **Laddered Simple Attention Network** architecture featuring a Monarch Hadamard MLP, Grouped-Query Attention (GQA) with causal conv taps, an engram n-gram memory read by gather, and multi-lane hyper-connections [README.md:11](). Trained so that every depth from 2 to 20 layers is a deployable subnetwork, Needle 3 achieves high parameter efficiency and calibrated confidence gating [README.md:11](). 

For legacy deployments requiring the previous generation, the Python API supports a generation selector via `generation=2` in `needle.Needle(...)` [README.md:44](), [llms.txt:45]().

**Figure 1: Natural Language Space to Code Entity Space (Inference Flow)**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        [UserQuery]
        [needle.tool_decorator]
    end

    subgraph "CodeEntitySpace"
        [needle.agent.Needle.run] --> [needle.agent.tools.build_schema]
        [needle.agent.Needle.run] --> [needle.agent.Needle._bind]
        [needle.agent.Needle._bind] --> [needle_init]
        [needle.agent.Needle.complete] --> [needle_complete]
    end

    [UserQuery] --> [needle.agent.Needle.run]
    [needle.tool_decorator] --> [needle.agent.tools.build_schema]
    [needle_complete] --> [StructuredJSONToolCall]
```
Sources: [README.md:31-42](), [llms.txt:18-24]()

---

## Whistle Speech-to-Text and Hosted Cactus Platform

In addition to text agents, Needle integrates **Whistle**, an on-device speech-to-text model sharing the same `.cact` container and C++ engine runtime [README.md:47-51](). Whistle supports 16 kHz mono audio inputs in English, German, French, Spanish, Italian, Dutch, and Polish, allowing audio clips to directly trigger tool calls or transcriptions [README.md:51-72]().

The hosted **Cactus Platform** provides cloud infrastructure (`cactuscompute.com/v1`) for dataset generation, remote fine-tuning, and model deployment via the `needle.platform` client interface [llms.txt:5]().

Sources: [README.md:47-72](), [llms.txt:5]()

---

## Major Subsystems

Needle is organized into modular subsystems that manage the complete lifecycle of on-device agent execution, speech processing, and model optimization:

| Subsystem | Primary Responsibility | Key Code Entities |
| :--- | :--- | :--- |
| **Agent API** | High-level interface, tool binding, & structured extraction | `Needle`, `@tool`, `extract()`, `Field` [llms.txt:18-28]() |
| **Model Core** | SAN Architecture & tokenization | `SimpleAttentionNetwork`, `SANTokenizer`, `TransformerConfig` [README.md:11]() |
| **Whistle Speech** | Audio transcription and streaming | `Whistle`, `transcribe()`, `stream()` [README.md:51-60]() |
| **Fine-Tuning** | LoRA training, synthetic data generation, & export | `finetune_local()`, `generate_dataset()`, `Muon` [README.md:64-68]() |
| **Platform & CLI** | CLI routing, hosted training client, & web playground | `needle.cli:main`, `Platform`, `Engine` [llms.txt:5](), [pyproject.toml:31]() |

**Figure 2: Natural Language Space to Code Entity Space (CLI & Execution Mapping)**
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        [CLICommandRun]
        [CLICommandFinetune]
        [CLICommandGenerateData]
        [CLICommandPlayground]
    end

    subgraph "CodeEntitySpace"
        [needle.cli.main] --> [needle.agent.Needle.run]
        [needle.cli.main] --> [needle.model.finetune.finetune_local]
        [needle.cli.main] --> [needle.model.finetune.generate_main]
        [needle.playground.server.Engine] --> [needle.playground.server]
    end

    [CLICommandRun] --> [needle.cli.main]
    [CLICommandFinetune] --> [needle.cli.main]
    [CLICommandGenerateData] --> [needle.cli.main]
    [CLICommandPlayground] --> [needle.cli.main]
```
Sources: [README.md:64-82](), [pyproject.toml:30-31]()

---

## Getting Started and Child Pages

To install the core runtime package:

```sh
pip install cactus-needle
```
Sources: [README.md:23-25](), [llms.txt:10]()

For complete instructions covering optional training extras (`[train]`, `[gpu]`, `[metal]`), setup scripts, engine binary fetching, and initial API usage, see [Getting Started](#1.1). For reference regarding all needle CLI subcommands (`run`, `finetune`, `whistle`, `platform`, etc.), see [CLI Reference](#1.2).

Sources: [README.md:21-86](), [llms.txt:1-15](), [pyproject.toml:1-46]()

---

