<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/onetwo · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [onetwo/core/content.py](onetwo/core/content.py)
- [onetwo/core/content_test.py](onetwo/core/content_test.py)
- [onetwo/core/executing.py](onetwo/core/executing.py)
- [onetwo/core/executing_test.py](onetwo/core/executing_test.py)
- [onetwo/core/results.py](onetwo/core/results.py)
- [onetwo/core/results_test.py](onetwo/core/results_test.py)

</details>



This document provides an overview of OneTwo's foundational systems that enable asynchronous execution, multimodal content handling, and result tracking. These core components form the execution model that powers all higher-level features in OneTwo.

For information about LLM backends and built-in functions, see [LLM Integration](#3). For advanced prompting strategies and agents, see [Advanced Features](#4). For evaluation and testing systems, see [Evaluation and Testing](#5).

## Overview

OneTwo's core architecture consists of four primary systems that work together to provide a flexible execution framework:

1. **Content System** - Handles multimodal content representation
2. **Execution Framework** - Provides asynchronous execution capabilities  
3. **Results and Tracing** - Tracks execution outcomes and debugging information
4. **Performance Systems** - Optimizes execution through caching and batching

## Core Architecture Components

```mermaid
graph TB
    subgraph "Content Layer"
        Chunk["Chunk<br/>content: ContentType<br/>content_type: str<br/>role: RoleType"]
        ChunkList["ChunkList<br/>chunks: list[Chunk]"]
        Message["Message<br/>role: str | PredefinedRole<br/>content: str | ChunkList"]
    end
    
    subgraph "Execution Layer"
        Executable["Executable[Result]<br/>_aexec() -> Result<br/>_aiterate() -> AsyncIterator"]
        MakeExecutable["make_executable<br/>@decorator"]
        FunctionExecWrapper["FunctionExecWrapper<br/>wrapped: Callable<br/>args: tuple<br/>kwargs: dict"]
    end
    
    subgraph "Results Layer"
        ExecutionResult["ExecutionResult<br/>inputs: dict[str, Any]<br/>outputs: dict[str, Any]<br/>stages: list[ExecutionResult]"]
        EvaluationResult["EvaluationResult<br/>targets: dict[str, Any]<br/>metrics: dict[str, Any]"]
    end
    
    subgraph "Control Flow"
        BatchingRun["batching.run<br/>enable_batching: bool<br/>enable_tracing: bool"]
        SafeStream["safe_stream<br/>iteration_depth: int"]
        SerialParallel["serial(*executables)<br/>parallel(*executables)"]
    end
    
    Chunk --> ChunkList
    ChunkList --> Message
    
    MakeExecutable --> FunctionExecWrapper
    FunctionExecWrapper --> Executable
    
    ExecutionResult --> EvaluationResult
    
    Executable --> BatchingRun
    Executable --> SafeStream
    Executable --> SerialParallel
    
    BatchingRun --> ExecutionResult
    SafeStream --> ExecutionResult
```

Sources: [onetwo/core/content.py:148-602](), [onetwo/core/executing.py:49-52](), [onetwo/core/executing.py:731-847](), [onetwo/core/results.py:76-151]()

## Content System Architecture

The content system provides a unified representation for multimodal data that can include text, images, and other media types.

```mermaid
graph LR
    subgraph "Content Types"
        StrContent["str"]
        BytesContent["bytes"] 
        PILImage["PIL.Image.Image"]
    end
    
    subgraph "Content Processing"
        ContentType["ContentType<br/>Union[str, bytes, PIL.Image.Image]"]
        ContentTypePrefixes["_CONTENT_TYPE_PREFIXES_BY_PYTHON_TYPE<br/>str: ['str', 'ctrl']<br/>bytes: ['image/', 'video/', 'audio/']<br/>pil_image: ['image/']"]
    end
    
    subgraph "Core Classes"
        ChunkClass["Chunk<br/>content: ContentType<br/>content_type: str<br/>role: RoleType<br/>metadata: Any"]
        ChunkListClass["ChunkList<br/>chunks: list[Chunk]<br/>__add__(), __iadd__()<br/>lstrip(), rstrip(), strip()"]
        MessageClass["Message<br/>role: str | PredefinedRole<br/>content: str | ChunkList<br/>create_normalized()"]
    end
    
    StrContent --> ContentType
    BytesContent --> ContentType  
    PILImage --> ContentType
    
    ContentType --> ChunkClass
    ContentTypePrefixes --> ChunkClass
    ChunkClass --> ChunkListClass
    ChunkListClass --> MessageClass
```

Sources: [onetwo/core/content.py:33-108](), [onetwo/core/content.py:148-318](), [onetwo/core/content.py:320-553](), [onetwo/core/content.py:555-602]()

Key features of the content system:

- **Type Safety**: Validates content types against expected formats
- **Multimodal Support**: Handles text, images, and binary data uniformly
- **Role Management**: Associates content with roles (USER, MODEL, SYSTEM)
- **String Operations**: Provides familiar string manipulation methods on multimodal content

For detailed information about content handling, see [Content System](#2.1).

## Execution Framework Architecture

The execution framework enables functions to be converted into asynchronous, composable executables that can be run individually or in complex patterns.

```mermaid
graph TD
    subgraph "Decorator System"
        MakeExecutableDecorator["@make_executable<br/>non_executed_args: Sequence[str]<br/>copy_self: bool<br/>execute_result: bool"]
        FunctionWrapper["FunctionExecWrapper<br/>wrapped: Callable<br/>_arguments: dict[str, Any]<br/>_process_arguments()"]
    end
    
    subgraph "Executable Interface"
        ExecutableBase["Executable[Result]<br/>_aexec() -> Result<br/>_aiterate() -> AsyncIterator[Update]<br/>with_depth(int) -> Executable"]
        ExecutableWithCallback["ExecutableWithCallback<br/>final_value_callback: Callable<br/>_iterate() -> AsyncIterator[Update]"]
    end
    
    subgraph "Execution Patterns"
        SerialExecution["SerialExecutable<br/>serial(*executables)"]
        ParallelExecution["ParallelExecutable<br/>parallel(*executables)<br/>par_iter(executables)"]
        StreamExecution["safe_stream()<br/>stream_updates()<br/>stream_with_callback()"]
    end
    
    MakeExecutableDecorator --> FunctionWrapper
    FunctionWrapper --> ExecutableBase
    ExecutableBase --> ExecutableWithCallback
    
    ExecutableBase --> SerialExecution
    ExecutableBase --> ParallelExecution
    ExecutableBase --> StreamExecution
```

Sources: [onetwo/core/executing.py:511-669](), [onetwo/core/executing.py:731-847](), [onetwo/core/executing.py:675-729]()

Key execution capabilities:

- **Automatic Conversion**: Functions become asynchronous executables via `@make_executable`
- **Argument Processing**: Automatically executes `Executable` arguments before function calls
- **Composition Patterns**: Supports serial and parallel execution of multiple executables
- **Streaming Support**: Enables real-time processing of intermediate results

For detailed information about execution patterns, see [Execution Framework](#2.2).

## Results and Tracing System

The results system captures execution outcomes, debug information, and evaluation metrics in a hierarchical structure.

```mermaid
graph TB
    subgraph "Result Data Structures"
        ExecutionResultClass["ExecutionResult<br/>stage_name: str<br/>inputs: dict[str, Any]<br/>outputs: dict[str, Any]<br/>stages: list[ExecutionResult]<br/>error: str<br/>start_time: float<br/>end_time: float"]
        
        EvaluationResultClass["EvaluationResult<br/>targets: dict[str, Any]<br/>metrics: dict[str, Any]<br/>from_execution_result()<br/>to_compact_record()"]
        
        EvaluationSummary["EvaluationSummary<br/>timing: EvaluationTiming<br/>metrics: dict[str, float]<br/>counters: Counter[str]<br/>results: dict[str, EvaluationResult]"]
    end
    
    subgraph "HTML Rendering"
        HTMLRenderer["HTMLRenderer<br/>levels_to_expand: int<br/>custom_renderers: list<br/>render_object()"]
        HTMLObjectRendering["HTMLObjectRendering<br/>html: str<br/>collapsed_html: str<br/>collapsible: bool"]
    end
    
    subgraph "Output Formatting"
        FormatResult["format_result()<br/>apply_formatting()<br/>get_name_tree()<br/>get_short_values_tree()"]
    end
    
    ExecutionResultClass --> EvaluationResultClass
    EvaluationResultClass --> EvaluationSummary
    
    ExecutionResultClass --> HTMLRenderer
    HTMLRenderer --> HTMLObjectRendering
    
    ExecutionResultClass --> FormatResult
```

Sources: [onetwo/core/results.py:76-252](), [onetwo/core/results.py:362-446](), [onetwo/core/results.py:687-1057]()

Key result tracking features:

- **Hierarchical Structure**: Nested results capture multi-stage execution flows  
- **Debug Information**: Includes timing, inputs, outputs, and error details
- **Evaluation Metrics**: Extends basic results with targets and performance metrics
- **Rich Rendering**: HTML and text formatters for interactive exploration

For detailed information about results and tracing, see [Results and Tracing](#2.3).

## System Integration Flow

This diagram shows how the core components work together during a typical execution:

```mermaid
sequenceDiagram
    participant User
    participant MakeExecutable as "@make_executable"
    participant FunctionWrapper as "FunctionExecWrapper"
    participant BatchingRun as "batching.run"
    participant ExecutionResult as "ExecutionResult"
    
    User->>MakeExecutable: Decorate function
    MakeExecutable->>FunctionWrapper: Create wrapper
    User->>FunctionWrapper: Call with args
    FunctionWrapper->>FunctionWrapper: Process Executable args
    User->>BatchingRun: run(executable)
    BatchingRun->>FunctionWrapper: _aexec()
    FunctionWrapper->>FunctionWrapper: Execute function
    FunctionWrapper->>BatchingRun: Return result
    BatchingRun->>ExecutionResult: Create result
    BatchingRun->>User: Return result + trace
```

Sources: [onetwo/core/executing.py:511-669](), [onetwo/core/executing.py:866-942](), [onetwo/core/batching.py]()

## Performance and Scalability

OneTwo's core architecture includes several performance optimization systems:

| System | Purpose | Key Components |
|--------|---------|----------------|
| **Batching** | Group multiple requests for efficient processing | `@batch_method`, `BatchQueue` |
| **Caching** | Avoid redundant computations | `@cache_method`, `SimpleCache` |
| **Parallel Execution** | Execute independent tasks concurrently | `parallel()`, `par_iter()` |
| **Streaming** | Process results incrementally | `safe_stream()`, `stream_updates()` |

For detailed information about performance optimizations, see [Performance Systems](#2.4).

## Next Steps

The core architecture provides the foundation for all OneTwo functionality. To learn about specific subsystems:

- **Content handling details**: [Content System](#2.1)
- **Execution patterns**: [Execution Framework](#2.2)  
- **Result tracking**: [Results and Tracing](#2.3)
- **Performance optimization**: [Performance Systems](#2.4)
- **LLM integration**: [LLM Integration](#3)
- **Advanced strategies**: [Advanced Features](#4)

Sources: [onetwo/core/content.py](), [onetwo/core/executing.py](), [onetwo/core/results.py]()

---

