<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/inference-benchmarker · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/benchmark.rs](src/benchmark.rs)
- [src/lib.rs](src/lib.rs)
- [src/scheduler.rs](src/scheduler.rs)

</details>



This document covers the internal design and implementation of the inference-benchmarker's core Rust components. It details the main architectural patterns, key data structures, and execution flow that orchestrate LLM inference benchmarking operations.

For information about command-line usage and configuration options, see [CLI Interface](#3.1). For details about deployment methods, see [Deployment Options](#4).

## Architectural Overview

The inference-benchmarker follows a modular, event-driven architecture built around three primary orchestration layers: the main coordinator in `lib.rs`, the benchmark controller in `benchmark.rs`, and the execution scheduler in `scheduler.rs`.

### Core Component Hierarchy

```mermaid
graph TD
    RunConfiguration["RunConfiguration<br/>(lib.rs)"] --> LibRun["run()<br/>(lib.rs:57)"]
    LibRun --> BenchmarkNew["Benchmark::new()<br/>(benchmark.rs:125)"]
    BenchmarkNew --> BenchmarkRun["Benchmark::run()<br/>(benchmark.rs:148)"]
    
    BenchmarkRun --> Warmup["warmup()<br/>(benchmark.rs:218)"]
    BenchmarkRun --> RunThroughput["run_throughput()<br/>(benchmark.rs:272)"]
    BenchmarkRun --> RunSweep["run_sweep()<br/>(benchmark.rs:326)"]
    BenchmarkRun --> RunRates["run_rates()<br/>(benchmark.rs:354)"]
    
    Warmup --> SchedulerNew["Scheduler::new()<br/>(scheduler.rs:37)"]
    RunThroughput --> SchedulerNew
    RunSweep --> SchedulerNew
    RunRates --> SchedulerNew
    
    SchedulerNew --> SchedulerRun["Scheduler::run()<br/>(scheduler.rs:89)"]
    SchedulerRun --> ExecutorRun["Executor::run()<br/>(executors module)"]
    
    subgraph "Event System"
        EventBus["mpsc::UnboundedSender<Event>"]
        StopSender["broadcast::Sender<()>"]
    end
    
    LibRun -.-> EventBus
    BenchmarkRun -.-> EventBus
    SchedulerRun -.-> StopSender
```

**Sources:** [src/lib.rs:57-232](), [src/benchmark.rs:125-414](), [src/scheduler.rs:37-152]()

## Core Data Structures and Configuration

The system's behavior is controlled through several key configuration structures that flow through the execution pipeline.

### Primary Configuration Types

| Structure | Location | Purpose |
|-----------|----------|---------|
| `RunConfiguration` | [src/lib.rs:35-55]() | Top-level execution parameters from CLI |
| `BenchmarkConfig` | [src/benchmark.rs:60-79]() | Validated benchmark execution settings |
| `ExecutorConfig` | Referenced in scheduler | Low-level executor parameters |

### Configuration Flow and Transformation

```mermaid
graph LR
    CLI["CLI Arguments"] --> RunConfiguration["RunConfiguration<br/>{url, api_key, tokenizer_name,<br/>max_vus, duration, benchmark_kind}"]
    
    RunConfiguration --> ProfileApplication["apply_profile()<br/>(profiles.rs)"]
    ProfileApplication --> TokenizerInit["Tokenizer::from_pretrained()<br/>(lib.rs:81)"]
    TokenizerInit --> BackendInit["OpenAITextGenerationBackend::try_new()<br/>(lib.rs:88)"]
    
    RunConfiguration --> BenchmarkConfig["BenchmarkConfig<br/>{max_vus, duration, benchmark_kind,<br/>warmup_duration, rates, num_rates}"]
    BenchmarkConfig --> ConfigValidation["config.validate()<br/>(benchmark.rs:82)"]
    
    subgraph "Benchmark Types"
        Throughput["BenchmarkKind::Throughput"]
        Sweep["BenchmarkKind::Sweep"] 
        Rate["BenchmarkKind::Rate"]
    end
    
    ConfigValidation --> Throughput
    ConfigValidation --> Sweep
    ConfigValidation --> Rate
```

**Sources:** [src/lib.rs:35-116](), [src/benchmark.rs:60-117]()

## Event-Driven Communication System

The architecture uses an event bus pattern to coordinate between components and provide real-time progress updates.

### Event Types and Flow

```mermaid
graph TD
    subgraph "Event Producers"
        LibRun["lib.rs::run()"]
        BenchmarkMethods["Benchmark methods<br/>(warmup, run_throughput, etc.)"]
        SchedulerProgress["Scheduler progress handler<br/>(scheduler.rs:100)"]
    end
    
    subgraph "Event Types"
        BenchmarkStart["Event::BenchmarkStart<br/>{id, scheduler_type, progress}"]
        BenchmarkProgress["Event::BenchmarkProgress<br/>{successful_requests, failed_requests}"]
        BenchmarkEnd["Event::BenchmarkEnd<br/>{results, request_throughput}"]
        Message["Event::Message<br/>{message, timestamp, level}"]
        BenchmarkReportEnd["Event::BenchmarkReportEnd<br/>{file_path}"]
        BenchmarkError["Event::BenchmarkError<br/>{error_message}"]
    end
    
    subgraph "Event Consumers"
        UIThread["UI Thread<br/>(app.rs - Console UI)"]
        ProgressHandlers["Progress Handlers<br/>(benchmark.rs:185)"]
    end
    
    LibRun --> Message
    BenchmarkMethods --> BenchmarkStart
    BenchmarkMethods --> BenchmarkEnd
    BenchmarkMethods --> Message
    SchedulerProgress --> BenchmarkProgress
    LibRun --> BenchmarkReportEnd
    LibRun --> BenchmarkError
    
    BenchmarkStart --> UIThread
    BenchmarkProgress --> UIThread
    BenchmarkEnd --> UIThread
    Message --> UIThread
    BenchmarkReportEnd --> UIThread
    BenchmarkError --> UIThread
    
    BenchmarkProgress --> ProgressHandlers
```

**Sources:** [src/benchmark.rs:22-45](), [src/benchmark.rs:185-216](), [src/lib.rs:117-156]()

## Execution Flow Architecture

The system orchestrates benchmark execution through a hierarchical delegation pattern where each layer has specific responsibilities.

### Main Execution Pipeline

```mermaid
sequenceDiagram
    participant Main as "main.rs"
    participant Lib as "lib.rs::run()"
    participant Bench as "Benchmark"
    participant Sched as "Scheduler" 
    participant Exec as "Executor"
    participant Backend as "TextGenerationBackend"
    
    Main->>Lib: "run(RunConfiguration)"
    Lib->>Lib: "apply_profile() & validate"
    Lib->>Lib: "Tokenizer::from_pretrained()"
    Lib->>Lib: "OpenAITextGenerationBackend::try_new()"
    
    Lib->>Bench: "Benchmark::new(config, backend, requests)"
    Lib->>Bench: "benchmark.run()"
    
    Bench->>Bench: "warmup()"
    Bench->>Sched: "Scheduler::new(warmup_config)"
    Sched->>Exec: "executor.run()"
    Exec->>Backend: "generate_text(request)"
    Backend-->>Exec: "TextGenerationResponse"
    Exec-->>Sched: "aggregated_response"
    Sched-->>Bench: "BenchmarkResults"
    
    alt "BenchmarkKind::Throughput"
        Bench->>Bench: "run_throughput()"
    else "BenchmarkKind::Sweep"
        Bench->>Bench: "run_throughput() + run_rate(multiple)"
    else "BenchmarkKind::Rate"
        Bench->>Bench: "run_rates()"
    end
    
    Bench-->>Lib: "BenchmarkReport"
    Lib->>Lib: "BenchmarkReportWriter::try_new()"
    Lib-->>Main: "Result<()>"
```

**Sources:** [src/lib.rs:57-232](), [src/benchmark.rs:148-176](), [src/scheduler.rs:89-147]()

## Scheduler and Executor Architecture

The scheduler acts as an intermediary between high-level benchmark configuration and low-level execution strategies.

### Executor Type Mapping

| Benchmark Type | Executor Type | Configuration | Purpose |
|----------------|---------------|---------------|---------|
| Warmup | `ExecutorType::ConstantVUs` | `max_vus: 1` | Server prewarming |
| Throughput | `ExecutorType::ConstantVUs` | `max_vus: config.max_vus` | Maximum capacity testing |
| Rate/Sweep | `ExecutorType::ConstantArrivalRate` | `rate: specified_rate` | Controlled load testing |

### Scheduler Component Relationships

```mermaid
graph TD
    subgraph "Scheduler Core (scheduler.rs)"
        SchedulerStruct["Scheduler<br/>{id, executor, requests_generator,<br/>results, progress_tx, stop_sender}"]
        SchedulerNew["Scheduler::new()<br/>(scheduler.rs:37)"]
        SchedulerRun["Scheduler::run()<br/>(scheduler.rs:89)"]
    end
    
    subgraph "Executor Types"
        ConstantVUs["ConstantVUsExecutor<br/>(executors.rs)"]
        ConstantArrivalRate["ConstantArrivalRateExecutor<br/>(executors.rs)"]
    end
    
    subgraph "Request Generation"
        TextRequestGenerator["TextRequestGenerator trait<br/>(requests.rs)"]
        ConversationGenerator["ConversationTextRequestGenerator<br/>(requests.rs)"]
    end
    
    subgraph "Backend Communication"
        TextGenerationBackend["TextGenerationBackend trait<br/>(requests.rs)"]
        OpenAIBackend["OpenAITextGenerationBackend<br/>(requests.rs)"]
    end
    
    subgraph "Results Collection"
        BenchmarkResults["BenchmarkResults<br/>(results.rs)"]
        SchedulerProgress["SchedulerProgress<br/>{progress, requests_throughput,<br/>successful_requests, failed_requests}"]
    end
    
    SchedulerNew --> ConstantVUs
    SchedulerNew --> ConstantArrivalRate
    SchedulerStruct --> TextRequestGenerator
    SchedulerStruct --> TextGenerationBackend
    SchedulerRun --> BenchmarkResults
    SchedulerRun --> SchedulerProgress
    
    TextRequestGenerator --> ConversationGenerator
    TextGenerationBackend --> OpenAIBackend
```

**Sources:** [src/scheduler.rs:20-87](), [src/scheduler.rs:89-152]()

## Result Processing and Aggregation Flow

The system collects and processes benchmark results through a structured pipeline that handles real-time aggregation and final report generation.

### Results Processing Architecture

```mermaid
graph LR
    subgraph "Response Collection"
        TextGenResponse["TextGenerationAggregatedResponse<br/>(requests.rs)"]
        UnboundedChannel["UnboundedSender/Receiver<br/>(scheduler.rs:93)"]
    end
    
    subgraph "Results Aggregation"
        BenchmarkResults["BenchmarkResults::add_response()<br/>(results.rs)"]
        ProgressCalculation["SchedulerProgress calculation<br/>(scheduler.rs:122)"]
    end
    
    subgraph "Report Generation"
        BenchmarkReport["BenchmarkReport<br/>(results.rs)"]
        ReportWriter["BenchmarkReportWriter<br/>(writers.rs)"]
        JSONOutput["JSON file output<br/>(lib.rs:192)"]
        StdoutOutput["stdout display<br/>(lib.rs:224)"]
    end
    
    TextGenResponse --> UnboundedChannel
    UnboundedChannel --> BenchmarkResults
    BenchmarkResults --> ProgressCalculation
    ProgressCalculation --> EventBus["Event Bus<br/>(Event::BenchmarkProgress)"]
    
    BenchmarkResults --> BenchmarkReport
    BenchmarkReport --> ReportWriter
    ReportWriter --> JSONOutput
    ReportWriter --> StdoutOutput
```

**Sources:** [src/scheduler.rs:92-131](), [src/lib.rs:188-230](), [src/benchmark.rs:254-268]()

The core architecture demonstrates a clean separation of concerns with well-defined interfaces between components, enabling flexible benchmark execution strategies while maintaining comprehensive result collection and real-time progress monitoring.

---

