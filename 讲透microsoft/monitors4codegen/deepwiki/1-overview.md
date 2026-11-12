<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/monitors4codegen · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [tests/monitor_guided_decoding/test_typestate_monitor_rust.py](tests/monitor_guided_decoding/test_typestate_monitor_rust.py)

</details>



This page introduces the monitors4codegen repository, explaining its purpose, core components, and architecture. The repository provides a framework for **Monitor-Guided Decoding (MGD)**, which uses static analysis to constrain language model code generation, and **multilspy**, a cross-platform library for interacting with Language Server Protocol (LSP) servers.

For details on installation and environment setup, see [Getting Started](#2). For in-depth explanations of MGD concepts and monitor implementations, see [Monitor-Guided Decoding](#3) and its subsections. For multilspy usage and API documentation, see [multilspy Library](#4).

## Purpose and Scope

The monitors4codegen repository serves three primary purposes:

1. **Monitor-Guided Decoding Framework**: Provides a mechanism to constrain code generation by language models using static analysis feedback from language servers
2. **multilspy Library**: Offers a unified, language-agnostic interface for querying language servers that implement the Language Server Protocol
3. **Research Artifact**: Includes datasets (PragmaticCode and DotPrompts), evaluation scripts, and experimental results demonstrating MGD's effectiveness

The repository supports code generation for Java, Rust, C#, and Python, and integrates with both HuggingFace transformer models and OpenAI API models.

**Sources**: [README.md:1-14]()

## Core Components

### Monitor-Guided Decoding (MGD)

Monitor-Guided Decoding is a framework that constrains language model token generation to ensure generated code satisfies specific semantic properties. Instead of relying solely on the language model's learned patterns, MGD queries language servers in real-time to determine what tokens are semantically valid at each generation step.

```mermaid
graph TB
    subgraph "MGD Framework Core"
        Monitor["Monitor<br/>(Base Interface)<br/>src/monitors4codegen/monitor_guided_decoding/monitor.py"]
        MonitorFileBuffer["MonitorFileBuffer<br/>(Context Management)"]
        
        subgraph "HuggingFace Path"
            MGDLogitsProcessor["MGDLogitsProcessor<br/>src/.../hf_gen.py"]
            HFTokenizerWrapper["HFTokenizerWrapper<br/>src/.../tokenizer_wrapper.py"]
        end
        
        subgraph "OpenAI Path"
            openai_mgd["openai_mgd function<br/>src/.../openai_gen.py"]
            TikTokenWrapper["TikTokenWrapper<br/>src/.../tokenizer_wrapper.py"]
        end
    end
    
    subgraph "Monitor Implementations"
        DereferencesMonitor["DereferencesMonitor<br/>src/.../monitors/dereferences_monitor.py"]
        NumArgsMonitor["NumArgsMonitor<br/>src/.../monitors/numargs_monitor.py"]
        TypestateMonitor["Typestate Monitor<br/>tests/.../test_typestate_monitor_rust.py"]
        SwitchEnumMonitor["SwitchEnumMonitor<br/>src/.../monitors/switch_enum_monitor.py"]
        ClassInstantiationMonitor["ClassInstantiationMonitor<br/>src/.../monitors/class_instantiation_monitor.py"]
    end
    
    Monitor --> DereferencesMonitor
    Monitor --> NumArgsMonitor
    Monitor --> TypestateMonitor
    Monitor --> SwitchEnumMonitor
    Monitor --> ClassInstantiationMonitor
    
    MonitorFileBuffer --> Monitor
    
    MGDLogitsProcessor --> Monitor
    HFTokenizerWrapper --> MGDLogitsProcessor
    
    openai_mgd --> Monitor
    TikTokenWrapper --> openai_mgd
```

**Key Classes and Functions:**

| Component | Location | Purpose |
|-----------|----------|---------|
| `Monitor` | [src/monitors4codegen/monitor_guided_decoding/monitor.py]() | Base interface defining `maskgen`, `initialize`, and `update` methods |
| `MGDLogitsProcessor` | [src/monitors4codegen/monitor_guided_decoding/hf_gen.py]() | LogitsProcessor for HuggingFace models |
| `openai_mgd` | [src/monitors4codegen/monitor_guided_decoding/openai_gen.py]() | Generation function for OpenAI models |
| `MonitorFileBuffer` | [src/monitors4codegen/monitor_guided_decoding/monitor.py]() | Manages file buffer state during generation |

**Sources**: [README.md:4-22](), [README.md:178-187]()

### multilspy Library

multilspy is a language-agnostic client library that abstracts the complexity of setting up and communicating with language servers. It provides a unified interface for querying static analysis results across different programming languages.

```mermaid
graph TB
    subgraph "API Layer"
        SyncLanguageServer["SyncLanguageServer<br/>(Blocking API)<br/>src/multilspy/language_server.py"]
        LanguageServer["LanguageServer<br/>(Async API)<br/>src/multilspy/language_server.py"]
    end
    
    subgraph "Core Types & Config"
        MultilspyConfig["MultilspyConfig<br/>src/multilspy/multilspy_config.py"]
        MultilspyTypes["multilspy_types module<br/>Position, Range, Location, etc."]
    end
    
    subgraph "Language-Specific Implementations"
        JediServer["JediServer<br/>(Python)<br/>jedi-language-server"]
        EclipseJDTLS["EclipseJDTLS<br/>(Java)<br/>Eclipse JDT.LS"]
        RustAnalyzer["RustAnalyzer<br/>(Rust)<br/>rust-analyzer"]
        OmniSharp["OmniSharp<br/>(C#)<br/>OmniSharp"]
    end
    
    subgraph "LSP Request Methods"
        request_definition["request_definition"]
        request_completions["request_completions"]
        request_references["request_references"]
        request_hover["request_hover"]
        request_document_symbols["request_document_symbols"]
    end
    
    MultilspyConfig --> SyncLanguageServer
    MultilspyConfig --> LanguageServer
    
    SyncLanguageServer --> request_definition
    SyncLanguageServer --> request_completions
    SyncLanguageServer --> request_references
    SyncLanguageServer --> request_hover
    SyncLanguageServer --> request_document_symbols
    
    SyncLanguageServer -.instantiates.-> JediServer
    SyncLanguageServer -.instantiates.-> EclipseJDTLS
    SyncLanguageServer -.instantiates.-> RustAnalyzer
    SyncLanguageServer -.instantiates.-> OmniSharp
```

**Key LSP Request Methods:**

| Method | LSP Operation | Returns |
|--------|---------------|---------|
| `request_definition` | `textDocument/definition` | Symbol definition location |
| `request_references` | `textDocument/references` | All references to a symbol |
| `request_completions` | `textDocument/completion` | Valid completion items at cursor |
| `request_hover` | `textDocument/hover` | Hover information (e.g., signatures) |
| `request_document_symbols` | `textDocument/documentSymbol` | All symbols in a document |

**Sources**: [README.md:109-177](), [pyproject.toml:12-13]()

## Repository Structure

The repository is organized into distinct functional areas:

```mermaid
graph LR
    subgraph "Source Code"
        direction TB
        MGD_src["src/monitors4codegen/<br/>monitor_guided_decoding/"]
        multilspy_src["src/monitors4codegen/<br/>multilspy/"]
        
        MGD_src --> monitors["monitors/<br/>(Monitor implementations)"]
        MGD_src --> monitor_py["monitor.py"]
        MGD_src --> hf_gen["hf_gen.py"]
        MGD_src --> openai_gen["openai_gen.py"]
        
        multilspy_src --> language_server["language_server.py"]
        multilspy_src --> multilspy_config["multilspy_config.py"]
        multilspy_src --> multilspy_types["multilspy_types.py"]
    end
    
    subgraph "Datasets"
        PragmaticCode["datasets/PragmaticCode/<br/>100 Java repositories"]
        DotPrompts["datasets/DotPrompts/<br/>10,538 completion tasks"]
        fileContents["fileContentsByRepo.json"]
        
        PragmaticCode --> fileContents
        PragmaticCode --> DotPrompts
    end
    
    subgraph "Evaluation & Results"
        eval_scripts["evaluation_scripts/<br/>eval_results.py"]
        inference_results["inference_results/<br/>dotprompts_results.csv"]
        results["results/<br/>Report.md, figures, tables"]
        
        inference_results --> eval_scripts
        fileContents --> eval_scripts
        eval_scripts --> results
    end
    
    subgraph "Tests"
        test_mgd["tests/monitor_guided_decoding/"]
        test_multilspy["tests/multilspy/"]
    end
```

**Directory Structure:**

| Path | Contents |
|------|----------|
| `src/monitors4codegen/monitor_guided_decoding/` | MGD framework implementation |
| `src/monitors4codegen/monitor_guided_decoding/monitors/` | Individual monitor implementations |
| `src/monitors4codegen/multilspy/` | multilspy library source |
| `datasets/PragmaticCode/` | Real-world Java repositories dataset |
| `datasets/DotPrompts/` | Code completion benchmark dataset |
| `evaluation_scripts/` | Scripts for computing metrics |
| `inference_results/` | Generated code samples and results |
| `tests/` | Unit tests and integration tests |

**Sources**: [README.md:7-13]()

## How MGD Works: Token-Level Constraint Application

Monitor-Guided Decoding operates at each token generation step, querying language servers to determine valid continuations:

```mermaid
sequenceDiagram
    participant LLM as "Language Model<br/>(HF/OpenAI)"
    participant Processor as "MGDLogitsProcessor or<br/>openai_mgd"
    participant Monitor as "Monitor Instance<br/>(e.g., DereferencesMonitor)"
    participant LSP as "SyncLanguageServer"
    participant LS as "Language Server Process<br/>(Java/Rust/C#/Python)"
    
    Note over LLM,LS: Generation loop for each token
    
    LLM->>Processor: "Compute next token logits"
    Processor->>Monitor: "maskgen(current_tokens)"
    Monitor->>Monitor: "Check if constraint<br/>applies at current position"
    
    alt Constraint Active
        Monitor->>LSP: "request_completions(file, line, col)"
        LSP->>LS: "textDocument/completion (JSON-RPC)"
        LS-->>LSP: "Valid completion items"
        LSP-->>Monitor: "Typed results"
        Monitor->>Monitor: "Compute blacklist:<br/>invalid token IDs"
    else No Constraint
        Monitor->>Monitor: "Return empty blacklist"
    end
    
    Monitor-->>Processor: "Blacklisted token IDs"
    Processor->>Processor: "Set blacklisted logits to -inf"
    Processor-->>LLM: "Modified logits"
    LLM->>LLM: "Sample from valid tokens only"
    LLM-->>Processor: "Selected token"
    Processor->>Monitor: "update(token)"
    Monitor->>LSP: "Append token to buffer"
```

**Generation Flow:**

1. **Language model** computes logits for all vocabulary tokens
2. **MGDLogitsProcessor** or **openai_mgd** calls `Monitor.maskgen()`
3. **Monitor** determines if a constraint applies (e.g., after `.` for member access)
4. If constraint applies:
   - Monitor queries **SyncLanguageServer** with `request_completions()` or similar
   - Language server returns semantically valid completions
   - Monitor converts completions to token IDs, blacklists invalid tokens
5. **Processor** sets blacklisted token logits to `-∞` (HuggingFace) or uses `logit_bias` (OpenAI)
6. **Language model** samples only from valid tokens
7. Selected token is appended to buffer via `Monitor.update()`

**Sources**: [README.md:16-22](), [tests/monitor_guided_decoding/test_typestate_monitor_rust.py:60-110]()

## Supported Languages and Models

### Programming Languages

| Language | Language Server | Monitor Support |
|----------|----------------|-----------------|
| **Java** | Eclipse JDT.LS | DereferencesMonitor, NumArgsMonitor, ClassInstantiationMonitor |
| **Rust** | rust-analyzer | DereferencesMonitor, Typestate Monitor |
| **C#** | OmniSharp | SwitchEnumMonitor, NumArgsMonitor |
| **Python** | Jedi Language Server | DereferencesMonitor (potential) |

### Language Model Backends

| Backend | Integration Class/Function | API |
|---------|---------------------------|-----|
| **HuggingFace Transformers** | `MGDLogitsProcessor` | `LogitsProcessor` interface |
| **OpenAI API** | `openai_mgd` | Custom generation loop with `logit_bias` |

**Tested Models:**
- `bigcode/santacoder` (1.1B parameters)
- `Salesforce/codegen-350M-multi`, `codegen-2B-multi`, `codegen-6B-multi`
- `text-davinci-003` (OpenAI)

**Sources**: [README.md:114-115](), [README.md:86-89](), [README.md:182-187]()

## Key Concepts

### Monitors

A **Monitor** is a stateful object that enforces a specific code property during generation. Each monitor implements three core methods:

```python
class Monitor:
    def maskgen(self, tokens: List[int]) -> List[int]:
        """Returns list of token IDs to blacklist at current position"""
        
    def initialize(self) -> None:
        """Initialize monitor state before generation"""
        
    def update(self, generated_token: int) -> None:
        """Update monitor state after token is generated"""
```

**Monitor Types:**

| Monitor | Property Enforced | Languages |
|---------|------------------|-----------|
| `DereferencesMonitor` | Type-valid member access (`obj.member`) | Java, Rust |
| `NumArgsMonitor` | Correct function argument count | Java, C# |
| `ClassInstantiationMonitor` | Valid class after `new` keyword | Java |
| `SwitchEnumMonitor` | Valid enum constants in switch cases | C# |
| Typestate Monitor | Valid API method call ordering | Rust |

**Sources**: [README.md:180](), [README.md:188-205]()

### MonitorFileBuffer

`MonitorFileBuffer` manages the state of the file being generated, tracking cursor position and coordinating updates with the language server. It provides the context monitors need to query the LSP effectively.

**Sources**: [tests/monitor_guided_decoding/test_typestate_monitor_rust.py:50-59]()

### Joint Monitoring

Multiple monitors can operate simultaneously, with their blacklists combined. This allows enforcing multiple properties at once (e.g., type-valid dereferences AND correct argument counts).

**Sources**: [README.md:204-205]()

## Evaluation and Datasets

### Datasets

```mermaid
graph TD
    PragmaticCode["PragmaticCode Dataset<br/>100 Java repositories<br/>datasets/PragmaticCode/"]
    repos_csv["repos.csv<br/>(Repository list with licenses)"]
    fileContents["fileContentsByRepo.json<br/>(Complete file contents)"]
    
    DotPrompts["DotPrompts Dataset<br/>10,538 completion examples<br/>datasets/DotPrompts/"]
    dataset_csv["dataset.csv<br/>(repo, file, positions)"]
    
    PragmaticCode --> repos_csv
    PragmaticCode --> fileContents
    PragmaticCode --> DotPrompts
    DotPrompts --> dataset_csv
    
    eval_script["eval_results.py<br/>evaluation_scripts/"]
    fileContents --> eval_script
    dataset_csv --> eval_script
    
    results_csv["dotprompts_results.csv<br/>inference_results/"]
    results_csv --> eval_script
    
    eval_script --> metrics["Metrics:<br/>CR, NIM, ISM, PM"]
    metrics --> report["Report.md<br/>results/"]
```

**Evaluation Metrics:**

| Metric | Full Name | Measures |
|--------|-----------|----------|
| **CR** | Compilation Rate | Percentage of generated code that compiles |
| **NIM** | Next-Identifier Match | Exact match of next token with ground truth |
| **ISM** | Identifier-Sequence Match | Ordered subsequence match of identifiers |
| **PM** | Prefix Match | Longest common prefix with ground truth |

**Sources**: [README.md:25-44](), [README.md:46-107]()

## Motivating Example

The README provides a concrete example demonstrating MGD's effectiveness:

**Scenario**: Complete code after `ServerNode.Builder.newServerNode()`
- **Without MGD**: Models hallucinate non-existent methods like `.host()` and `.port()`
- **With MGD**: DereferencesMonitor queries the language server for valid methods on `ServerNode.Builder` type, constrains generation to only valid methods
- **Result**: Generated code compiles and matches ground truth

According to the paper, MGD improves compilation rates by **19-25%** across model scales from 350M to 175B parameters.

**Sources**: [README.md:16-23]()

## Installation

To use monitors4codegen, install via pip:

```bash
pip install https://github.com/microsoft/multilspy/archive/main.zip
pip install -r requirements.txt
```

For detailed setup instructions including virtual environment creation and language server configuration, see [Getting Started](#2).

**Sources**: [README.md:47-64](), [README.md:125-128]()

## Next Steps

- **For installation and setup**: See [Getting Started](#2)
- **For MGD framework details**: See [Monitor-Guided Decoding](#3)
- **For individual monitor documentation**: See [Monitor Implementations](#3.2)
- **For multilspy usage**: See [multilspy Library](#4)
- **For dataset details and evaluation**: See [Datasets and Evaluation](#5)
- **For contributing**: See [Development Guide](#6)

---

