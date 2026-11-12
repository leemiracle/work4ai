<!-- source: DeepWiki mcp.deepwiki.com · repo openai/simple-evals · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [common.py](common.py)
- [types.py](types.py)

</details>



## Purpose and Scope

This document describes the high-level architecture of the simple-evals framework, a lightweight system for evaluating language models across diverse benchmarks. The framework follows a three-tier architecture: command-line interface entrypoints that orchestrate evaluation runs, specialized benchmark implementations that encode evaluation logic, and model samplers that abstract different API interfaces.

**Deprecation Status**: As of July 2025, simple-evals is frozen for new models and results. Only three benchmarks (SimpleQA, BrowseComp, HealthBench) remain actively maintained as reference implementations. However, the core infrastructure (types, samplers, utilities) remains available for reuse.

For detailed information about type definitions and interfaces, see page 3.1. For model samplers, see page 3.2. For the evaluation framework, see page 3.3. For common utilities and result aggregation, see page 3.4.

## High-Level Architecture Overview

The framework is organized into three primary layers:

1. **Entry Points**: Command-line interfaces that orchestrate evaluation runs
2. **Benchmarks**: Specialized evaluation implementations that encode task-specific logic
3. **Samplers**: Model interface abstractions that handle different API patterns

### Three-Tier Architecture Diagram

```mermaid
graph TB
    subgraph CLI["CLI Layer"]
        MainFunc["main() in simple_evals.py"]
        MultiMLLU["run_multilingual_mmlu.py"]
    end
    
    subgraph Benchmarks["Benchmark Layer (Eval subclasses)"]
        MMLUEval["MMLUEval"]
        MathEval["MathEval"]
        GPQAEval["GPQAEval"]
        DropEval["DropEval"]
        MGSMEval["MGSMEval"]
        HumanEvalImpl["HumanEval"]
        SimpleQAEval["SimpleQAEval"]
        BrowseCompEval["BrowseCompEval"]
        HealthBenchEval["HealthBenchEval"]
    end
    
    subgraph Samplers["Sampler Layer (SamplerBase implementations)"]
        ChatSampler["ChatCompletionSampler"]
        ResponsesSampler["ResponsesSampler"]
        OChatSampler["OChatCompletionSampler"]
        ClaudeSampler["ClaudeCompletionSampler"]
    end
    
    subgraph Infrastructure["Core Infrastructure"]
        TypesDef["types.py<br/>(SamplerBase, Eval, EvalResult, SingleEvalResult)"]
        CommonUtils["common.py<br/>(aggregate_results, make_report, normalize_response)"]
    end
    
    subgraph APIs["External APIs"]
        OpenAIAPI["OpenAI API"]
        AnthropicAPI["Anthropic API"]
    end
    
    MainFunc --> MMLUEval
    MainFunc --> MathEval
    MainFunc --> GPQAEval
    MainFunc --> SimpleQAEval
    MainFunc --> BrowseCompEval
    MainFunc --> HealthBenchEval
    MultiMLLU --> MMLUEval
    
    MMLUEval --> ChatSampler
    MMLUEval -.-> ResponsesSampler
    MathEval --> ChatSampler
    SimpleQAEval --> ChatSampler
    
    ChatSampler --> OpenAIAPI
    ResponsesSampler --> OpenAIAPI
    OChatSampler --> OpenAIAPI
    ClaudeSampler --> AnthropicAPI
    
    MMLUEval --> CommonUtils
    MathEval --> CommonUtils
    SimpleQAEval --> CommonUtils
    
    ChatSampler --> TypesDef
    MMLUEval --> TypesDef
```

**Sources**: [types.py:1-67](), [common.py:183-216](), [README.md:1-143]()

The system is centered around the `main()` function in `simple_evals.py`, which orchestrates evaluation runs. Benchmarks implement the `Eval` interface from `types.py` and use `SamplerBase` implementations to query models. All benchmarks can work with any sampler through this common interface, enabling flexible model-benchmark combinations.

## Core Execution Flow

The evaluation pipeline processes data from user commands through model APIs to aggregated results:

### Evaluation Pipeline Data Flow

```mermaid
flowchart TD
    subgraph Input["Input Stage"]
        UserCmd["User Command<br/>(--model, --eval, --examples)"]
        Dataset["Dataset Loading<br/>(CSV/JSONL/Remote)"]
    end
    
    subgraph Processing["Processing Stage"]
        Runner["main() function"]
        BenchmarkImpl["Benchmark.__call__(sampler)"]
        PromptFormat["Prompt Formatting<br/>(format_multichoice_question, etc.)"]
        SamplerCall["sampler(message_list)"]
        APICall["External API<br/>(OpenAI/Anthropic)"]
        Grading["Grading Logic<br/>(regex, LLM-based, or code execution)"]
    end
    
    subgraph Output["Output Stage"]
        SingleResult["SingleEvalResult objects<br/>(score, html, convo, metrics)"]
        Aggregation["aggregate_results()"]
        FinalResult["EvalResult<br/>(score, metrics, htmls, convos)"]
        HTMLReport["HTML Report<br/>(make_report)"]
        JSONOutput["JSON Metrics"]
    end
    
    UserCmd --> Runner
    Dataset --> BenchmarkImpl
    Runner --> BenchmarkImpl
    BenchmarkImpl --> PromptFormat
    PromptFormat --> SamplerCall
    SamplerCall --> APICall
    APICall --> SamplerCall
    SamplerCall --> Grading
    Grading --> SingleResult
    SingleResult --> Aggregation
    Aggregation --> FinalResult
    FinalResult --> HTMLReport
    FinalResult --> JSONOutput
```

**Sources**: [simple_evals.py:22-213](), [common.py:183-216](), [types.py:31-66]()

The `main()` function orchestrates the following steps:
1. Parse command-line arguments (model selection, eval selection, parameters)
2. Initialize `SamplerBase` implementations for specified models
3. Instantiate `Eval` subclasses for benchmarks with configuration
4. For each model-benchmark pair, call `eval_object(sampler)` which returns `EvalResult`
5. Use `make_report()` to generate HTML reports from `EvalResult.htmls`
6. Write metrics to JSON files
7. Aggregate all results into combined output table

## Model Sampler Architecture

The sampler layer provides a uniform interface (`SamplerBase`) to diverse language model APIs, enabling any benchmark to work with any model.

### Sampler Class Hierarchy

```mermaid
classDiagram
    class SamplerBase {
        <<interface from types.py>>
        +__call__(message_list: MessageList) SamplerResponse
    }
    
    class SamplerResponse {
        +response_text: str
        +actual_queried_message_list: MessageList
        +response_metadata: dict
    }
    
    class ChatCompletionSampler {
        +model: str
        +system_message: str
        +temperature: float
        +max_tokens: int
        +__call__(message_list) SamplerResponse
    }
    
    class ResponsesSampler {
        +model: str
        +__call__(message_list) SamplerResponse
        Note: For o3/o4 models, no system prompt support
    }
    
    class OChatCompletionSampler {
        +model: str
        +reasoning_effort: str
        +__call__(message_list) SamplerResponse
        Note: For o1/o3-mini models
    }
    
    class ClaudeCompletionSampler {
        +model: str
        +system_message: str
        +temperature: float
        +max_tokens: int
        +__call__(message_list) SamplerResponse
    }
    
    SamplerBase <|-- ChatCompletionSampler
    SamplerBase <|-- ResponsesSampler
    SamplerBase <|-- OChatCompletionSampler
    SamplerBase <|-- ClaudeCompletionSampler
    
    SamplerBase ..> SamplerResponse
```

**Sources**: [types.py:4-28](), [README.md:87-94]()

### Sampler Implementations

| Sampler Class | Purpose | Key Characteristics | Location |
|---------------|---------|---------------------|----------|
| `ChatCompletionSampler` | GPT-4 family, GPT-3.5 | Supports system messages, standard chat API | sampler/chat_completion_sampler.py |
| `ResponsesSampler` | o3, o4-mini models | Uses Responses API, no system prompt support, `reasoning_model=True` | sampler/responses_sampler.py |
| `OChatCompletionSampler` | o1 series, o3-mini | No system prompt, supports `reasoning_effort` parameter | sampler/o_chat_completion_sampler.py |
| `ClaudeCompletionSampler` | Claude models | Configurable system messages (empty or LMSYS template) | sampler/claude_completion_sampler.py |

All samplers implement `SamplerBase.__call__(message_list: MessageList) -> SamplerResponse` where `MessageList = list[Message]` and `Message = dict[str, Any]` (with keys `role`, `content`).

For detailed sampler documentation, see page 3.2 (Model Samplers), with subsections 3.2.1 (OpenAI Samplers) and 3.2.2 (Claude Sampler).

## Evaluation Framework

Benchmarks implement the `Eval` interface and follow a standardized execution pattern:

### Evaluation Interface Contract

```mermaid
classDiagram
    class Eval {
        <<base class from types.py>>
        +__call__(sampler: SamplerBase) EvalResult
    }
    
    class EvalResult {
        +score: float | None
        +metrics: dict[str, float] | None
        +htmls: list[str]
        +convos: list[MessageList]
        +metadata: dict[str, Any] | None
    }
    
    class SingleEvalResult {
        +score: float | None
        +metrics: dict[str, float]
        +html: str | None
        +convo: MessageList | None
        +example_level_metadata: dict[str, Any] | None
    }
    
    class MMLUEval {
        +__call__(sampler: SamplerBase) EvalResult
        -examples: list
        -num_few_shot: int
    }
    
    class SimpleQAEval {
        +__call__(sampler: SamplerBase) EvalResult
        -examples: list
        -grader_sampler: SamplerBase
    }
    
    Eval <|-- MMLUEval
    Eval <|-- SimpleQAEval
    Eval ..> EvalResult
    EvalResult o-- SingleEvalResult
```

**Sources**: [types.py:59-66](), [types.py:31-56]()

### Standard Evaluation Process

All `Eval` implementations follow this pattern:

1. **Dataset Loading**: Load examples from CSV, JSONL, or remote sources
2. **Prompt Construction**: Format prompts using templates (e.g., `QUERY_TEMPLATE_MULTICHOICE`)
3. **Model Sampling**: Call `sampler(message_list)` which returns `SamplerResponse`
4. **Answer Extraction**: Parse responses using regex patterns (e.g., `ANSWER_PATTERN_MULTICHOICE`)
5. **Grading**: Score responses via:
   - **Self-grading**: Direct comparison to ground truth (MMLU, GPQA, MATH)
   - **LLM-grading**: Use grader model to assess quality (SimpleQA, BrowseComp, HealthBench)
   - **Code execution**: Run test suites (HumanEval)
6. **Result Creation**: Build `SingleEvalResult` for each example
7. **Aggregation**: Combine via `aggregate_results()` into final `EvalResult`

See page 3.3 (Evaluation Framework) for detailed implementation patterns. See page 4 for specific benchmark implementations.

## Results Aggregation and Reporting

The result aggregation pipeline transforms per-example results into comprehensive evaluation reports:

### Aggregation Pipeline

```mermaid
flowchart TB
    subgraph PerExample["Per-Example Results"]
        Example["Dataset Example"]
        Prompt["Formatted Prompt"]
        Response["Model Response"]
        Score["Score Calculation"]
        SingleResult["SingleEvalResult<br/>(score, metrics, html, convo)"]
    end
    
    subgraph Aggregation["Aggregation Layer"]
        Collection["list[SingleEvalResult]"]
        AggFunc["aggregate_results()<br/>from common.py"]
        StatCalc["Statistics Computation<br/>(mean, std, bootstrap_std)"]
        MetricGroup["Metric Grouping<br/>(by category/theme/axis)"]
    end
    
    subgraph Output["Output Generation"]
        EvalResult["EvalResult<br/>(score, metrics, htmls, convos, metadata)"]
        MakeReport["make_report()<br/>from common.py"]
        HTMLOut["HTML Report<br/>(Jinja template rendering)"]
        JSONMetrics["JSON Metrics File"]
        FullJSON["Full Results JSON<br/>(complete trace)"]
    end
    
    Example --> Prompt
    Prompt --> Response
    Response --> Score
    Score --> SingleResult
    SingleResult --> Collection
    Collection --> AggFunc
    AggFunc --> StatCalc
    AggFunc --> MetricGroup
    StatCalc --> EvalResult
    MetricGroup --> EvalResult
    EvalResult --> MakeReport
    MakeReport --> HTMLOut
    EvalResult --> JSONMetrics
    EvalResult --> FullJSON
```

**Sources**: [common.py:183-216](), [common.py:335-343](), [types.py:31-56]()

### Aggregation Functions

The `aggregate_results()` function in `common.py` performs the following:

1. **Metric Collection**: Extract all metrics from each `SingleEvalResult.metrics` dict
2. **Score Aggregation**: Collect `SingleEvalResult.score` values
3. **Statistical Computation**: Calculate statistics via `_compute_stat()`:
   - `mean`: Average score across examples
   - `std`: Standard deviation
   - `bootstrap_std`: Bootstrap confidence intervals
   - `min`, `max`: Range statistics
   - `n_samples`: Number of examples
4. **HTML Consolidation**: Combine `SingleEvalResult.html` snippets
5. **Conversation Logging**: Preserve all `SingleEvalResult.convo` message lists

### Output Formats

| Format | Function | Purpose | File Location |
|--------|----------|---------|---------------|
| HTML Report | `make_report()` | Human-readable results with example-level detail | `/tmp/<model>_<eval>_report.html` |
| JSON Metrics | Direct serialization | Lightweight metrics for programmatic access | `/tmp/<model>_<eval>.json` |
| Full Results JSON | Complete `EvalResult` | Reproducibility, includes all conversations | `/tmp/<model>_<eval>_full.json` |

See page 3.4 (Common Utilities and Result Aggregation) for detailed utility documentation. See page 6.2 (Output Files and Reports) for output file specifications.

## Type System and Data Structures

The framework is built around a core set of type definitions that ensure modularity:

### Core Type Definitions

```mermaid
classDiagram
    class Message {
        <<TypeAlias: dict[str, Any]>>
        Keys: role, content
    }
    
    class MessageList {
        <<TypeAlias: list[Message]>>
    }
    
    class SamplerBase {
        <<Abstract Interface>>
        +__call__(message_list: MessageList) SamplerResponse
    }
    
    class SamplerResponse {
        <<dataclass>>
        +response_text: str
        +actual_queried_message_list: MessageList
        +response_metadata: dict[str, Any]
    }
    
    class SingleEvalResult {
        <<dataclass>>
        +score: float | None
        +metrics: dict[str, float]
        +html: str | None
        +convo: MessageList | None
        +example_level_metadata: dict[str, Any] | None
    }
    
    class EvalResult {
        <<dataclass>>
        +score: float | None
        +metrics: dict[str, float] | None
        +htmls: list[str]
        +convos: list[MessageList]
        +metadata: dict[str, Any] | None
    }
    
    class Eval {
        <<Abstract Interface>>
        +__call__(sampler: SamplerBase) EvalResult
    }
    
    SamplerBase ..> MessageList
    SamplerBase ..> SamplerResponse
    SamplerResponse ..> MessageList
    SingleEvalResult ..> MessageList
    EvalResult ..> MessageList
    Eval ..> SamplerBase
    Eval ..> EvalResult
```

**Sources**: [types.py:1-67]()

All types are defined in `types.py`. The key abstractions are:

- **`Message`**: Dictionary with `role` and `content` keys, representing a single message
- **`MessageList`**: List of messages forming a conversation
- **`SamplerBase`**: Abstract interface for model APIs
- **`SamplerResponse`**: Model output wrapper with response text and metadata
- **`SingleEvalResult`**: Per-example evaluation results
- **`EvalResult`**: Aggregated results across all examples
- **`Eval`**: Abstract interface for benchmark implementations

This type system enables any benchmark (`Eval`) to work with any model (`SamplerBase`) through a uniform interface.

See page 3.1 (Type System and Interfaces) for comprehensive type documentation.

## Common Utilities

The `common.py` module provides shared utilities used across all benchmarks:

### Utility Functions

| Function | Signature | Purpose | Location |
|----------|-----------|---------|----------|
| `format_multichoice_question()` | `(row: dict) -> str` | Format multiple choice questions using template | [common.py:153-154]() |
| `check_equality()` | `(sampler, expr1, expr2) -> bool` | Compare mathematical expressions via LLM | [common.py:157-161]() |
| `aggregate_results()` | `(list[SingleEvalResult], ...) -> EvalResult` | Aggregate per-example results with statistics | [common.py:183-216]() |
| `map_with_progress()` | `(f, xs, num_threads, pbar) -> list` | Parallel processing with progress bar | [common.py:219-234]() |
| `make_report()` | `(eval_result: EvalResult) -> str` | Generate HTML report using Jinja templates | [common.py:335-343]() |
| `normalize_response()` | `(response: str) -> str` | Strip markdown/LaTeX formatting | [common.py:355-374]() |
| `normalize_extracted_answer()` | `(extracted_answer: str) -> str` | Normalize multilingual answer characters | [common.py:377-395]() |

### Prompt Templates

- **`QUERY_TEMPLATE_MULTICHOICE`**: Standard multiple choice question format [common.py:15-24]()
- **`EQUALITY_TEMPLATE`**: Template for mathematical expression comparison [common.py:78-136]()

### Answer Extraction Patterns

- **`ANSWER_PATTERN_MULTICHOICE`**: Regex for "Answer: $LETTER" format [common.py:26]()
- **`ANSWER_PATTERN`**: General answer extraction regex [common.py:27]()
- **`MULTILINGUAL_ANSWER_REGEXES`**: Answer patterns in 15+ languages [common.py:32-75]()

See page 3.4 (Common Utilities and Result Aggregation) for detailed utility documentation.

## Summary

The Simple-Evals architecture provides a modular, extensible framework for evaluating language model performance across diverse tasks. Its key strengths include:

1. A unified interface for interacting with different language models
2. Standardized evaluation processes across tasks
3. Flexible result aggregation and reporting
4. Support for parallel processing of evaluations
5. Easy extension to new models and evaluation tasks

To learn more about specific evaluation tasks, see [Evaluation Tasks](#3), and for details on adding new models, see [Adding New Models](#6.1).

---

