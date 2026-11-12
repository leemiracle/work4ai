<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-agents-python · page 10 Tracing and Observability · fetched 2026-10-26 -->

# Tracing and Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/ja/tracing.md](docs/ja/tracing.md)
- [docs/ko/handoffs.md](docs/ko/handoffs.md)
- [docs/ko/tracing.md](docs/ko/tracing.md)
- [docs/zh/handoffs.md](docs/zh/handoffs.md)
- [docs/zh/tracing.md](docs/zh/tracing.md)
- [src/agents/tracing/__init__.py](src/agents/tracing/__init__.py)
- [src/agents/tracing/create.py](src/agents/tracing/create.py)
- [src/agents/tracing/processors.py](src/agents/tracing/processors.py)
- [src/agents/tracing/provider.py](src/agents/tracing/provider.py)
- [src/agents/tracing/scope.py](src/agents/tracing/scope.py)
- [src/agents/tracing/setup.py](src/agents/tracing/setup.py)
- [src/agents/tracing/util.py](src/agents/tracing/util.py)
- [tests/test_asyncio_progress.py](tests/test_asyncio_progress.py)
- [tests/test_disabled_trace_provider_flush.py](tests/test_disabled_trace_provider_flush.py)
- [tests/test_disabled_trace_provider_shutdown.py](tests/test_disabled_trace_provider_shutdown.py)
- [tests/test_trace_processor.py](tests/test_trace_processor.py)
- [tests/tracing/test_import_side_effects.py](tests/tracing/test_import_side_effects.py)
- [tests/tracing/test_processor_api_key.py](tests/tracing/test_processor_api_key.py)
- [tests/tracing/test_reasoning_export.py](tests/tracing/test_reasoning_export.py)
- [tests/tracing/test_set_api_key_fix.py](tests/tracing/test_set_api_key_fix.py)
- [tests/tracing/test_tracing_env_disable.py](tests/tracing/test_tracing_env_disable.py)

</details>



This page covers the SDK's built-in tracing system for monitoring, debugging, and optimizing agent execution. The tracing system automatically captures comprehensive execution data including LLM generations, tool calls, handoffs, guardrails, and custom events, exporting them to observability backends for visualization and analysis [docs/tracing.md:7-7]().

For information about runtime configuration, see [Configuration and Setup](#12). For details on guardrail validation that produces guardrail spans, see [Safety and Validation](#6). For session persistence that works alongside tracing, see [Session and Memory Management](#8).

## Overview

The tracing system is enabled by default and operates on two core abstractions: **Traces** represent complete end-to-end workflows [docs/tracing.md:21-21](), while **Spans** represent individual timed operations within those workflows [docs/tracing.md:27-27](). The system uses Python `contextvars` via `Scope` to maintain automatic nesting and concurrency support [docs/tracing.md:136-136](), batch processing for efficient export, and supports multiple observability backends through a modular provider-processor-exporter pipeline.

### Tracing System Component Interaction
Title: Tracing System Component Interaction
```mermaid
graph TB
    subgraph "Trace Creation Layer [Code Entity Space]"
        ContextVar[""contextvars.ContextVar<br/>Scope._current_trace<br/>Scope._current_span""]
        TraceFunc[""trace() function<br/>src/agents/tracing/create.py""]
        SpanFuncs[""agent_span()<br/>generation_span()<br/>function_span()<br/>guardrail_span()<br/>handoff_span()""]
    end
    
    subgraph "Provider Layer [Code Entity Space]"
        TraceProvider[""DefaultTraceProvider<br/>src/agents/tracing/provider.py""]
        TraceObject[""TraceImpl<br/>workflow_name<br/>trace_id<br/>group_id""]
        SpanObject[""SpanImpl<br/>span_data<br/>started_at<br/>ended_at""]
    end
    
    subgraph "Processing Layer [Code Entity Space]"
        MultiProcessor[""SynchronousMultiTracingProcessor<br/>Forwards to all registered processors""]
        BatchProcessor[""BatchTraceProcessor<br/>src/agents/tracing/processors.py""]
        Queue[""Internal Queue<br/>_queue""]
    end
    
    subgraph "Export Layer [Code Entity Space]"
        BackendExporter[""BackendSpanExporter<br/>OpenAI Traces API Ingest""]
        ConsoleExporter[""ConsoleSpanExporter<br/>Prints to stdout""]
    end
    
    TraceFunc --> ContextVar
    SpanFuncs --> ContextVar
    ContextVar --> TraceProvider
    TraceProvider --> TraceObject
    TraceProvider --> SpanObject
    TraceObject --> MultiProcessor
    SpanObject --> MultiProcessor
    MultiProcessor --> BatchProcessor
    BatchProcessor --> Queue
    Queue --> BackendExporter
    Queue --> ConsoleExporter
```
Sources: [src/agents/tracing/provider.py:18-45](), [src/agents/tracing/processors.py:44-53](), [src/agents/tracing/processors.py:218-245](), [src/agents/tracing/setup.py:1-20]()

---

## 10.1. Tracing Architecture

The tracing architecture centers around the `TraceProvider` interface, which manages trace and span creation, context propagation, and processor registration [src/agents/tracing/provider.py:8-22](). The active trace and span are tracked using Python `contextvars` in `Scope`, enabling seamless propagation across asynchronous execution boundaries without manual context passing [src/agents/tracing/scope.py:11-20](). Traces can be created via automatic instrumentation during runner execution or manually using the `trace()` context manager [docs/tracing.md:37-37]().

For detailed information on trace lifecycles, span hierarchies, context variables, and automatic versus custom traces, see [Tracing Architecture](#10.1).

Sources: [src/agents/tracing/provider.py:8-22](), [src/agents/tracing/scope.py:11-20](), [docs/tracing.md:37-48]()

---

## 10.2. Span Types and Lifecycle

Spans represent discrete operations with start and end timestamps [docs/tracing.md:27-28](). The SDK defines specific typed data payloads (`SpanData`) for various operations, such as `AgentSpanData` for agent execution, `GenerationSpanData` for LLM completions, `FunctionSpanData` for tool calls, `HandoffSpanData` for agent delegation, and `GuardrailSpanData` for safety validation [src/agents/tracing/span_data.py:22-30](). Developers can also create arbitrary custom spans using `custom_span()` [docs/tracing.md:140-140]().

### Code Execution to Trace Hierarchy Mapping
Title: Code Execution to Trace Hierarchy Mapping
```mermaid
graph TB
    Trace[""Trace: 'Agent workflow'<br/>(from Runner.run)<br/>src/agents/tracing/traces.py""]
    
    AgentSpan[""Span: AgentSpanData<br/>(Agent: 'Support')<br/>src/agents/tracing/span_data.py""]
    GenSpan[""Span: GenerationSpanData<br/>(LLM API Call)""]
    FuncSpan[""Span: FunctionSpanData<br/>(Tool: get_weather)""]
    GuardSpan[""Span: GuardrailSpanData<br/>(Safety Check)""]
    
    Trace --> AgentSpan
    AgentSpan --> GuardSpan
    AgentSpan --> GenSpan
    AgentSpan --> FuncSpan
```
Sources: [docs/tracing.md:31-43](), [src/agents/tracing/create.py:10-50](), [src/agents/tracing/span_data.py:22-40]()

For details on span payloads, state transitions, and manual span construction, see [Span Types and Lifecycle](#10.2).

Sources: [docs/tracing.md:27-32](), [src/agents/tracing/span_data.py:22-40](), [src/agents/tracing/create.py:1-150]()

---

## 10.3. Trace Processors and Export

Trace processors observe trace and span lifecycle events (`on_trace_start`, `on_span_end`, etc.) and route them to exporters [src/agents/tracing/processor_interface.py:1-25](). The default `BatchTraceProcessor` buffers items in an internal queue and flushes them periodically or when batch size limits are reached [src/agents/tracing/processors.py:218-245](). The `BackendSpanExporter` packages and transmits these payloads to the OpenAI Traces ingestion endpoint, while `ConsoleSpanExporter` outputs to stdout [src/agents/tracing/processors.py:28-53](). Custom processors can be registered via `add_trace_processor()` [src/agents/tracing/__init__.py:94-98]().

For details on batching policies, custom trace processors, third-party integrations, and exporter configuration, see [Trace Processors and Export](#10.3).

Sources: [src/agents/tracing/processors.py:28-108](), [src/agents/tracing/processor_interface.py:1-30](), [src/agents/tracing/__init__.py:94-106]()

---

## 10.4. Sensitive Data Handling

Tracing backends may capture sensitive application data, PII, or prompt text during LLM generations and tool executions [docs/tracing.md:144-148](). The SDK provides `RunConfig.trace_include_sensitive_data` to control whether prompt inputs and outputs are recorded [docs/tracing.md:148-148](). Tracing can also be disabled globally via `set_tracing_disabled(True)` or the `OPENAI_AGENTS_DISABLE_TRACING=1` environment variable [docs/tracing.md:9-16](). API keys specific to tracing export can be configured via `set_tracing_export_api_key()` [src/agents/tracing/__init__.py:115-119]().

For details on PII redaction, data filtering policies, and security configurations, see [Sensitive Data Handling](#10.4).

Sources: [docs/tracing.md:144-157](), [src/agents/tracing/__init__.py:108-120](), [src/agents/tracing/config.py:1-18]()

---

## 10.5. Hooks and Lifecycle Events

While tracing passively records execution telemetry, lifecycle hooks (`RunHooks` and `AgentHooks`) allow developers to intercept agent execution and respond to events [docs/tracing.md:127-137](). Hooks expose interception points such as `before_run`, `after_run`, `before_agent`, `after_agent`, `on_tool_call`, `on_handoff`, and `on_error` [docs/tracing.md:127-137](). These integrate closely with tracing to augment monitoring and enforce custom logging logic.

For details on hook signatures, execution ordering, and error interception, see [Hooks and Lifecycle Events](#10.5).

Sources: [docs/tracing.md:127-137](), [src/agents/tracing/create.py:113-123]()

---

