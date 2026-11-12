<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2-scholarqa-lib · page 6 Monitoring & Tracing · fetched 2026-10-26 -->

# Monitoring & Tracing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/scholarqa/glog.py](api/scholarqa/glog.py)
- [api/scholarqa/trace/event_traces.py](api/scholarqa/trace/event_traces.py)
- [api/scholarqa/utils.py](api/scholarqa/utils.py)

</details>



This document describes the monitoring and tracing capabilities of the ScholarQA system. It covers how to monitor system behavior, track request processing, debug issues, and analyze performance using event traces and structured logging. For information about system deployment, see [Deployment](#7).

## Overview of Monitoring Capabilities

ScholarQA implements a comprehensive monitoring system to track the execution of query processing pipelines, capture performance metrics, and log important events. The monitoring system consists of two main components:

1. **Structured Logging** - Task ID-aware logging with support for both local and Google Cloud environments
2. **Event Tracing** - Detailed traces of each step in the query processing pipeline

```mermaid
flowchart TD
    subgraph "ScholarQA Monitoring System"
        Logging["Structured Logging System"]
        EventTracing["Event Tracing System"]
        
        subgraph "Logging Components"
            TaskIdFormatter["TaskIdAwareLogFormatter"]
            GCloudJson["Google Cloud JSON Format"]
            StdOutErr["StdOut/StdErr Output"]
        end
        
        subgraph "Tracing Components"
            EventTrace["EventTrace Class"]
            TraceWriter["TraceWriter Interface"]
            LocalWriter["LocalWriter"]
            GCSWriter["GCSWriter"]
        end
        
        Logging --> TaskIdFormatter
        Logging --> GCloudJson
        Logging --> StdOutErr
        
        EventTracing --> EventTrace
        EventTracing --> TraceWriter
        TraceWriter --> LocalWriter
        TraceWriter --> GCSWriter
    end
```

Sources: [api/scholarqa/utils.py:27-35](), [api/scholarqa/glog.py:6-29](), [api/scholarqa/trace/event_traces.py:11-84]()

## Structured Logging System

The ScholarQA system uses a structured logging approach that enhances the standard Python logging capabilities with task ID awareness and Google Cloud compatibility.

### Task ID-Aware Logging

Each request in ScholarQA is assigned a unique task ID, which is included in all log messages related to that request. This enables easy correlation of logs across the entire processing pipeline.

```mermaid
sequenceDiagram
    participant User
    participant API as "API Service"
    participant Logger as "TaskIdAwareLogFormatter"
    participant Output as "Log Output"
    
    User->>API: Submit query
    Note over API: Generate task_id
    API->>Logger: Initialize with task_id
    
    loop Processing Steps
        API->>Logger: Log event with regular message
        Logger->>Logger: Format with task_id prefix
        Logger->>Output: Output formatted log
    end
```

Key components:

- **TaskIdAwareLogFormatter**: Extends the standard log formatter to include task IDs in messages
- **init_settings()**: Initializes the logging system with appropriate handlers and formatters

Sources: [api/scholarqa/utils.py:27-35](), [api/scholarqa/utils.py:38-85]()

### Logging Configuration

The logging system can be configured to output logs in different formats:

| Environment Variable | Value | Description |
|----------------------|-------|-------------|
| LOG_FORMAT | "google:json" | Outputs logs in Google Cloud JSON format |
| LOG_FORMAT | (any other or unset) | Outputs logs to stdout/stderr with standard formatting |
| LOG_LEVEL | (e.g., "INFO", "DEBUG") | Sets the logging verbosity level |

Example configuration:

```python
# Initialize logging with custom directory and debug level
log_formatter = init_settings(logs_dir="/path/to/logs", log_level="DEBUG")
```

Sources: [api/scholarqa/utils.py:38-85]()

### Google Cloud Logging

For cloud deployments, ScholarQA supports Google Cloud-compatible JSON logging format:

```mermaid
flowchart TD
    LogEvent["Log Event"] --> GLogFormatter["glog.Formatter"]
    GLogFormatter --> JsonOutput["JSON Output"]
    JsonOutput --> CloudLogging["Google Cloud Logging"]
    
    GLogFormatter --> AddSeverity["Add 'severity' field"]
    GLogFormatter --> FormatMessage["Format with task_id"]
```

The `glog.py` module provides:
- `Formatter`: Extends `jsonlogger.JsonFormatter` to add Google Cloud-specific fields like "severity"
- `Handler`: Stream handler that uses the custom formatter

Sources: [api/scholarqa/glog.py:6-29]()

## Event Tracing System

The event tracing system captures detailed information about each step of query processing, enabling in-depth analysis of system behavior and performance.

### EventTrace Structure

The `EventTrace` class captures:

- **Basic request information**: Task ID, query text, timestamp, user ID
- **Metrics**: Number of retrieved documents, candidates, etc.
- **Cost tracking**: Total cost and per-step costs of LLM calls
- **Step-by-step results**: Outputs of each processing stage

```mermaid
classDiagram
    class EventTrace {
        +String task_id
        +String query
        +String user_id
        +String timestamp
        +int n_retrieval
        +int n_retrieved
        +int n_candidates
        +int n_rerank
        +boolean opt_in
        +float total_cost
        +Dict decomposed_query
        +List candidates
        +List retrieved
        +Dict quotes
        +Dict cluster
        +Dict summary
        +trace_decomposition_event()
        +trace_retrieval_event()
        +trace_rerank_event()
        +trace_quote_event()
        +trace_clustering_event()
        +trace_inline_citation_following_event()
        +trace_summary_event()
        +persist_trace()
    }
```

Sources: [api/scholarqa/trace/event_traces.py:11-84]()

### Tracing Pipeline Events

The event tracing system records detailed information at each step of the RAG pipeline:

```mermaid
flowchart LR
    Query["User Query"] --> Decomposition["Query Decomposition"]
    Decomposition --> Retrieval["Document Retrieval"]
    Retrieval --> Reranking["Document Reranking"]
    Reranking --> QuoteExtraction["Quote Extraction"]
    QuoteExtraction --> Clustering["Quote Clustering"]
    Clustering --> InlineCitation["Inline Citation"]
    InlineCitation --> Summary["Summary Generation"]
    
    DecompTrace["trace_decomposition_event()"] -.-> Decomposition
    RetrievalTrace["trace_retrieval_event()"] -.-> Retrieval
    RerankTrace["trace_rerank_event()"] -.-> Reranking
    QuoteTrace["trace_quote_event()"] -.-> QuoteExtraction
    ClusterTrace["trace_clustering_event()"] -.-> Clustering
    CitationTrace["trace_inline_citation_following_event()"] -.-> InlineCitation
    SummaryTrace["trace_summary_event()"] -.-> Summary
```

Each tracing method captures:
- Input and output data for the step
- LLM model used (when applicable)
- Cost information (when using LLMs)
- Processing metrics

Sources: [api/scholarqa/trace/event_traces.py:38-79]()

### Trace Persistence

Event traces can be persisted either locally or to Google Cloud Storage:

```mermaid
flowchart TD
    EventTrace["EventTrace Object"] -- "persist_trace()" --> Writer["TraceWriter"]
    
    Writer --> LocalWriter["LocalWriter"]
    Writer --> GCSWriter["GCSWriter"]
    
    LocalWriter --> FileSystem["Local File System"]
    GCSWriter --> GCS["Google Cloud Storage"]
```

Configuration is controlled by the `LogsConfig` object which specifies:
- `tracing_mode`: "local" or "gcs"
- `event_trace_loc`: Directory or bucket name
- `log_dir`: Base directory for local logs

Sources: [api/scholarqa/trace/event_traces.py:81-84]()

## Cost Tracking

The ScholarQA system carefully tracks the cost of each LLM call throughout the processing pipeline. This information is captured in the event trace and can be used for billing, optimization, and monitoring purposes.

```mermaid
flowchart TD
    QueryProcess["Query Processing"] --> |"LLM Call"| CostAwareLLMResult["CostAwareLLMResult"]
    CostAwareLLMResult --> |"Get result"| ActualResult["Processing Result"]
    CostAwareLLMResult --> |"Get cost info"| CostInfo["Cost Information"]
    CostInfo --> |"Add to total"| EventTrace["EventTrace.total_cost"]
    
    subgraph "Cost Tracking"
        StepCost1["Decomposition Cost"]
        StepCost2["Quote Extraction Cost"]
        StepCost3["Clustering Cost"]
        StepCost4["Summary Generation Cost"]
        TotalCost["Total Cost"]
        
        StepCost1 --> TotalCost
        StepCost2 --> TotalCost
        StepCost3 --> TotalCost
        StepCost4 --> TotalCost
    end
```

The cost tracking is handled by:
- `CostAwareLLMResult`: Contains both the result of an LLM call and its cost information
- Cost accumulation in the `EventTrace` object for each step and total
- Per-model tracking for multi-step processes

Sources: [api/scholarqa/trace/event_traces.py:38-79]()

## Integration with System Components

The monitoring and tracing system integrates with all major components of ScholarQA:

```mermaid
flowchart TD
    subgraph "API Layer"
        FastAPI["FastAPI Application"]
        StateManager["State Manager"]
    end
    
    subgraph "Core Components"
        ScholarQA["ScholarQA Core"]
        QueryProcessor["Query Processor"]
        Retriever["Document Retriever"]
        Reranker["Document Reranker"]
        Pipeline["Multi-Step QA Pipeline"]
    end
    
    subgraph "Monitoring System"
        Logging["Structured Logging"]
        EventTracing["Event Tracing"]
    end
    
    FastAPI -- "Create task_id" --> StateManager
    FastAPI -- "Initialize" --> Logging
    
    ScholarQA -- "Log events" --> Logging
    ScholarQA -- "Create trace" --> EventTracing
    
    QueryProcessor -- "Trace decomposition" --> EventTracing
    Retriever -- "Trace retrieval" --> EventTracing
    Reranker -- "Trace reranking" --> EventTracing
    Pipeline -- "Trace pipeline steps" --> EventTracing
    
    StateManager -- "Associate logs with task" --> Logging
```

Sources: [api/scholarqa/utils.py:38-85](), [api/scholarqa/trace/event_traces.py:11-84]()

## Best Practices for Monitoring and Debugging

### Effective Trace Analysis

1. **Search by task ID**: When debugging an issue with a specific request, use the task ID to filter logs and access the corresponding event trace
2. **Monitor costs**: Use the cost tracking information to identify expensive operations and optimize prompts
3. **Compare traces**: Compare traces from successful and failed requests to identify differences

### Local vs. Cloud Logging

| Environment | Recommended Configuration |
|-------------|---------------------------|
| Development | Local logging with DEBUG level |
| Testing | Local event traces with INFO level |
| Production | Google Cloud JSON logging with event traces to GCS |

### Setting Up Monitoring Dashboards

For production deployments, consider setting up dashboards that visualize:
- Request volume and latency
- Error rates by component
- LLM costs over time
- Document retrieval metrics

## Troubleshooting Common Issues

| Issue | Monitoring Approach |
|-------|---------------------|
| High latency | Check event traces to identify slow steps |
| Unexpected results | Examine intermediate outputs in event trace |
| High costs | Review cost tracking information per step |
| Missing logs | Verify logging configuration and levels |

Sources: [api/scholarqa/utils.py:38-85](), [api/scholarqa/trace/event_traces.py:11-84]()

---

