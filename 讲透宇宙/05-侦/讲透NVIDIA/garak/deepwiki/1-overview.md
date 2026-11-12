<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/garak · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [FAQ.md](FAQ.md)
- [PROJECTS.md](PROJECTS.md)
- [README.md](README.md)
- [docs/source/cliref.rst](docs/source/cliref.rst)
- [docs/source/detectors/sysprompt_extraction.rst](docs/source/detectors/sysprompt_extraction.rst)
- [docs/source/probes/agent_breaker.rst](docs/source/probes/agent_breaker.rst)
- [docs/source/probes/goat.rst](docs/source/probes/goat.rst)
- [garak/__init__.py](garak/__init__.py)
- [garak/probes/goat.py](garak/probes/goat.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [tests/test_reqs.py](tests/test_reqs.py)

</details>



This document provides a comprehensive introduction to `garak`, covering its purpose, architecture, and core components. It serves as the entry point for understanding how `garak` operates as an LLM vulnerability scanning framework.

For specific installation instructions, see [Installation & Setup](#1.1). For hands-on usage examples, see [Basic Usage](#1.2). For detailed component documentation, see [Components](#3).

## What is garak

`garak` (**Generative AI Red-teaming & Assessment Kit**) is a security-focused LLM vulnerability scanner designed to probe language models for weaknesses including prompt injection, data leakage, toxicity generation, jailbreaks, hallucination, and other failure modes. The tool operates similarly to traditional security scanners like `nmap` or Metasploit, but targets Large Language Models instead of network infrastructure.

**Core Mission**: `garak` checks if an LLM can be made to fail in ways we don't want, focusing on security vulnerabilities rather than general safety or bias assessment.

Sources: [README.md:1-15](), [pyproject.toml:104-104](), [FAQ.md:10-16]()

## Core Concepts

`garak` operates using four fundamental component types that work together in a coordinated testing pipeline:

| Component | Purpose | Examples |
|-----------|---------|----------|
| **Probes** | Generate test prompts targeting specific vulnerabilities | `dan`, `encoding`, `goat` |
| **Generators** | Interface with LLM APIs and services | `openai`, `huggingface`, `nim` |
| **Detectors** | Analyze LLM responses for vulnerability indicators | `mitigation`, `toxicity`, `always.Pass` |
| **Harnesses** | Orchestrate the testing process and coordinate components | `ProbewiseHarness`, `PxD` |

The testing process involves probes sending carefully crafted prompts through generators to target LLMs, then detectors analyzing the responses to identify potential vulnerabilities.

Sources: [README.md:87-102](), [FAQ.md:16-18](), [garak/probes/goat.py:32-32]()

## System Architecture

### Core Component Relationships

```mermaid
graph TB
    subgraph "CLI Interface"
        MainEntry["garak.__main__:main<br/>Entry Point"]
        CLIArgs["Command Line Arguments<br/>--target_type, --probes, --detectors"]
    end
    
    subgraph "Plugin System"
        PluginMgr["garak._plugins<br/>Discovery & Loading"]
        ProbeBase["garak.probes.base.Probe"]
        DetectorBase["garak.detectors.base.Detector"] 
        GeneratorBase["garak.generators.base.Generator"]
        HarnessBase["garak.harnesses.base.Harness"]
    end
    
    subgraph "Core Components"
        Probes["Probe Implementations<br/>dan, encoding, goat"]
        Detectors["Detector Implementations<br/>mitigation, toxicity"]
        Generators["Generator Implementations<br/>openai, huggingface, nim"]
        Harnesses["Harness Implementations<br/>ProbewiseHarness, PxD"]
    end
    
    subgraph "Configuration"
        ConfigSystem["garak._config<br/>YAML + CLI processing"]
        TransientConfig["_config.transient<br/>Runtime data"]
    end
    
    subgraph "Output Systems"
        Logger["garak.log<br/>Debug logging"]
        Reports["JSONL Reports<br/>garak.XXXX.report.jsonl"]
        HTMLDigest["HTML Analysis<br/>report_digest.html"]
    end
    
    MainEntry --> CLIArgs
    CLIArgs --> ConfigSystem
    CLIArgs --> PluginMgr
    
    PluginMgr --> ProbeBase
    PluginMgr --> DetectorBase
    PluginMgr --> GeneratorBase
    PluginMgr --> HarnessBase
    
    ProbeBase --> Probes
    DetectorBase --> Detectors
    GeneratorBase --> Generators
    HarnessBase --> Harnesses
    
    ConfigSystem --> TransientConfig
    
    Harnesses --> Logger
    Harnesses --> Reports
    Reports --> HTMLDigest
```

This diagram shows how the CLI entry point coordinates plugin discovery and loading, with all components inheriting from well-defined base classes and configuration flowing through the system.

Sources: [pyproject.toml:192-193](), [garak/__init__.py:7-25](), [README.md:87-102](), [garak/probes/goat.py:25-29]()

### Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as "garak CLI"
    participant Config as "_config"
    participant PluginMgr as "garak._plugins" 
    participant Harness as "ProbewiseHarness"
    participant Probe as "Probe Instance"
    participant Generator as "Generator Instance"
    participant LLM as "Target LLM"
    participant Detector as "Detector Instance"
    participant Reporter as "Report System"
    
    User->>CLI: "garak --target_type openai --probes dan"
    CLI->>Config: "Load configuration hierarchy"
    Config-->>CLI: "Merged config"
    CLI->>PluginMgr: "Discover and load plugins"
    PluginMgr-->>CLI: "Plugin instances"
    
    CLI->>Harness: "run(generator, probes, detectors)"
    
    loop "For each probe"
        Harness->>Probe: "probe(generator)"
        Probe->>Probe: "Generate test prompts"
        
        loop "For each prompt attempt"
            Probe->>Generator: "_call_model(prompt)"
            Generator->>LLM: "API call"
            LLM-->>Generator: "Response text"
            Generator-->>Probe: "generations"
            
            loop "For each detector"
                Probe->>Detector: "detect(attempt)"
                Detector-->>Probe: "score (0.0-1.0)"
            end
        end
        
        Probe-->>Harness: "Attempt results"
    end
    
    Harness->>Reporter: "Write JSONL report"
    Harness->>Reporter: "Generate HTML digest"
    Reporter-->>User: "garak.XXXX.report.jsonl"
    Reporter-->>User: "report_digest.html"
```

This sequence shows the complete execution flow from CLI invocation through plugin coordination to final report generation, using actual class and method names from the codebase.

Sources: [README.md:119-131](), [docs/source/cliref.rst:6-31](), [FAQ.md:16-19](), [garak/probes/goat.py:32-85]()

## Key Features

### Comprehensive LLM Support
`garak` supports diverse LLM deployment patterns through its generator system:

- **Cloud APIs**: OpenAI, Anthropic, Cohere, Replicate, Mistral, Boto3 (Bedrock).
- **Local Models**: HuggingFace transformers, Ollama, NVIDIA Riva.
- **Flexible Integration**: REST endpoints, LiteLLM proxy, NIM (NVIDIA Inference Microservices).

### Extensive Vulnerability Coverage  
The probe system includes numerous vulnerability tests across categories:

- **Security**: Prompt injection, jailbreaks (DAN, GOAT, AutoDAN), data leakage.
- **Safety**: Toxicity generation, harmful content (LMRC, RealToxicityPrompts).
- **Reliability**: Hallucination, package supply-chain risks (Python, JS, Rust, etc.).
- **Compliance**: OWASP LLM Top 10, AVID framework integration.

### Production-Ready Features
- **Parallel Execution**: Configurable `parallel_requests` and `parallel_attempts` for faster scans.
- **Rich Configuration**: Hierarchical YAML config system with CLI overrides and `transient` runtime state.
- **Comprehensive Reporting**: JSONL logs, HTML digests, and support for security taxonomies like MISP.
- **Extensible Architecture**: Plugin system for custom probes, detectors, and generators.

Sources: [README.md:34-44](), [pyproject.toml:114-160](), [docs/source/cliref.rst:35-121](), [garak/probes/goat.py:90-102]()

## Plugin Architecture

```mermaid
graph LR
    subgraph "Base Classes"
        ProbeBase["garak.probes.base.Probe<br/>probe()"]
        IterativeProbe["garak.probes.IterativeProbe<br/>_generate_next_attempts()"]
        DetectorBase["garak.detectors.base.Detector<br/>detect()"]
        GeneratorBase["garak.generators.base.Generator<br/>_call_model()"]
    end
    
    subgraph "Probe Modules"
        DanProbes["garak.probes.dan<br/>Dan_11_0"]
        GoatProbes["garak.probes.goat<br/>GOATAttack"]  
        EncodingProbes["garak.probes.encoding<br/>InjectBase64"]
    end
    
    subgraph "Generator Modules" 
        OpenAIGen["garak.generators.openai<br/>OpenAIGenerator"]
        HFGen["garak.generators.huggingface<br/>Model"]
        NimGen["garak.generators.nim<br/>NIM"]
    end
    
    subgraph "Detector Modules"
        MitigationDet["garak.detectors.mitigation<br/>MitigationBypass"]
        JudgeDet["garak.detectors.judge<br/>JailbreakOnlyAdversarial"]
        AlwaysDet["garak.detectors.always<br/>Pass"]
    end
    
    ProbeBase -.-> IterativeProbe
    IterativeProbe -.-> GoatProbes
    ProbeBase -.-> DanProbes
    ProbeBase -.-> EncodingProbes  
    
    GeneratorBase -.-> OpenAIGen
    GeneratorBase -.-> HFGen
    GeneratorBase -.-> NimGen
    
    DetectorBase -.-> MitigationDet
    DetectorBase -.-> JudgeDet
    DetectorBase -.-> AlwaysDet
```

The plugin system uses inheritance from base classes to provide consistent interfaces. Probes like `GOATAttack` utilize specialized base classes like `IterativeProbe` for multi-turn attacks.

Sources: [garak/probes/goat.py:32-32](), [README.md:97-99](), [FAQ.md:72-74]()

## Getting Started

`garak` is installed via pip and operates as a command-line tool:

```bash
# Standard installation
python -m pip install -U garak

# Basic usage examples
export OPENAI_API_KEY="sk-..."
garak --target_type openai --target_name gpt-4 --probes encoding

# List available components
garak --list_probes
garak --list_detectors  
garak --list_generators
```

For detailed installation instructions including development setup, see [Installation & Setup](#1.1). For comprehensive usage examples and configuration options, see [Basic Usage](#1.2).

Sources: [README.md:50-56](), [README.md:89-97](), [docs/source/cliref.rst:1-31]()

---

