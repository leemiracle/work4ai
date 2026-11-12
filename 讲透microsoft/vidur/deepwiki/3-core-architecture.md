<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/vidur · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vidur/config/config.py](vidur/config/config.py)
- [vidur/request_generator/synthetic_request_generator.py](vidur/request_generator/synthetic_request_generator.py)
- [vidur/simulator.py](vidur/simulator.py)

</details>



This document provides an architectural overview of Vidur's core simulation framework, focusing on the primary components and their relationships. It covers the main orchestration layer, event-driven simulation engine, configuration system, and component interaction patterns.

For information about specific scheduling algorithms and resource management, see [Scheduling and Resource Management](#6). For details about performance modeling and prediction systems, see [Performance Modeling](#7). For comprehensive metrics collection and analysis capabilities, see [Metrics and Analysis](#8).

## System Overview

Vidur implements a discrete event simulation architecture designed to model large language model (LLM) inference systems at scale. The system is built around a central `Simulator` class that orchestrates multiple subsystems through an event-driven execution model.

### Primary System Components

```mermaid
graph TB
    subgraph "Core Simulation Engine"
        A[Simulator] --> B["Event Queue<br/>(heapq)"]
        A --> C[Cluster]
        A --> D["BaseGlobalScheduler<br/>Registry"]
    end
    
    subgraph "Configuration Management"
        E[SimulationConfig] --> F[ClusterConfig]
        E --> G[RequestGeneratorConfig]  
        E --> H[ExecutionTimePredictorConfig]
        E --> I[MetricsConfig]
        F --> J[ReplicaConfig]
        F --> K[GlobalSchedulerConfig]
        F --> L[ReplicaSchedulerConfig]
    end
    
    subgraph "Request Generation"
        M[RequestGeneratorRegistry] --> N[SyntheticRequestGenerator]
        M --> O[TraceRequestGenerator]
        N --> P[RequestLengthGeneratorRegistry]
        N --> Q[RequestIntervalGeneratorRegistry]
    end
    
    subgraph "Performance & Execution"
        R[ExecutionTimePredictor] --> S[LinearRegressionPredictor]
        R --> T[RandomForestPredictor]
        U[MetricsStore] --> V[DataSeries]
        U --> W[CDFSketch]
    end
    
    A --> E
    E --> A
    A --> M
    A --> R
    A --> U
    
    style A fill:#f9f9f9
    style E fill:#f9f9f9
    style M fill:#f9f9f9
    style U fill:#f9f9f9
```

**Sources:** [vidur/simulator.py:17-49](), [vidur/config/config.py:627-656]()

## Core Simulation Engine

The simulation engine centers around the `Simulator` class, which implements a discrete event simulation model using a priority queue for event scheduling and processing.

### Event-Driven Architecture

```mermaid
graph TD
    subgraph "Event Processing Loop"
        A["`_event_queue
        (heapq)`"] --> B["`heappop()
        Get Next Event`"]
        B --> C["`_set_time()
        Update Simulation Time`"]
        C --> D["`event.handle_event()
        Process Event`"]
        D --> E["`_add_events()
        Schedule New Events`"]
        E --> A
    end
    
    subgraph "Event Types"
        F[RequestArrivalEvent] --> D
        G[BatchScheduleEvent] --> D
        H[BatchCompletionEvent] --> D
        I[MemoryReclamationEvent] --> D
    end
    
    subgraph "Event Handlers"
        D --> J[BaseGlobalScheduler]
        D --> K[MetricsStore]
        J --> L["`New Events
        Generation`"]
        K --> M["`Metrics
        Recording`"]
    end
    
    subgraph "Termination Conditions"
        N["`_time > _time_limit`"] --> O["`_terminate = True`"]
        P["`_event_queue empty`"] --> Q["`Simulation End`"]
        R["`scheduler.is_empty()`"] --> Q
    end
    
    C --> N
    A --> P
    J --> R
    O --> Q
    
    style A fill:#f9f9f9
    style D fill:#f9f9f9
```

The simulation engine executes through a main event loop in the `run()` method:

- **Event Queue Management**: Uses Python's `heapq` for efficient priority queue operations [vidur/simulator.py:27,64-68]()
- **Time Progression**: Simulation time advances only when processing events [vidur/simulator.py:66,109-116]()
- **Event Generation**: Each event handler can spawn new events, maintaining the simulation flow [vidur/simulator.py:67-68,99-102]()
- **Termination Logic**: Simulation ends when the event queue is empty, time limit is reached, or scheduler reports completion [vidur/simulator.py:64,78,111-115]()

**Sources:** [vidur/simulator.py:59-81](), [vidur/simulator.py:96-116]()

## Configuration Architecture

Vidur implements a sophisticated hierarchical configuration system that supports both programmatic configuration and comprehensive CLI argument generation.

### Configuration Hierarchy

```mermaid
graph TD
    subgraph "Top-Level Configuration"
        A[SimulationConfig] --> B[ClusterConfig]
        A --> C[BaseRequestGeneratorConfig]
        A --> D[BaseExecutionTimePredictorConfig] 
        A --> E[MetricsConfig]
    end
    
    subgraph "Cluster Configuration"
        B --> F[ReplicaConfig]
        B --> G[BaseGlobalSchedulerConfig]
        B --> H[BaseReplicaSchedulerConfig]
        F --> I["`model_name
        tensor_parallel_size
        num_pipeline_stages`"]
        F --> J[BaseModelConfig]
        F --> K[BaseDeviceSKUConfig]
        F --> L[BaseNodeSKUConfig]
    end
    
    subgraph "Request Generation"
        C --> M[SyntheticRequestGeneratorConfig]
        C --> N[TraceRequestGeneratorConfig]
        M --> O[BaseRequestLengthGeneratorConfig]
        M --> P[BaseRequestIntervalGeneratorConfig]
        O --> Q["`FixedRequestLengthGeneratorConfig
        UniformRequestLengthGeneratorConfig
        ZipfRequestLengthGeneratorConfig`"]
        P --> R["`PoissonRequestIntervalGeneratorConfig
        GammaRequestIntervalGeneratorConfig
        TraceRequestIntervalGeneratorConfig`"]
    end
    
    subgraph "Scheduler Configuration"
        H --> S["`VllmSchedulerConfig
        SarathiSchedulerConfig
        LightllmSchedulerConfig`"]
        G --> T["`RandomGlobalSchedulerConfig
        RoundRobinGlobalSchedulerConfig
        LORGlobalSchedulerConfig`"]
    end
    
    style A fill:#f9f9f9
    style B fill:#f9f9f9
    style C fill:#f9f9f9
```

### Polymorphic Configuration System

The configuration system uses `BasePolyConfig` to enable runtime type selection through the `_type` field injection mechanism:

```mermaid
graph LR
    subgraph "Configuration Selection"
        A["`BasePolyConfig
        get_type()`"] --> B["`_type field
        injection`"]
        B --> C["`Registry lookup
        at runtime`"]
        C --> D["`Subclass
        instantiation`"]
    end
    
    subgraph "Registry Examples"
        E[GlobalSchedulerRegistry] --> F["`RandomGlobalScheduler
        RoundRobinGlobalScheduler
        LORGlobalScheduler`"]
        G[RequestGeneratorRegistry] --> H["`SyntheticRequestGenerator
        TraceRequestGenerator`"]
    end
    
    C --> E
    C --> G
    
    style A fill:#f9f9f9
    style C fill:#f9f9f9
```

**Sources:** [vidur/config/config.py:8](), [vidur/config/config.py:468-491](), [vidur/config/config.py:255-329]()

## Component Initialization and Orchestration

The `Simulator` class orchestrates component initialization through dependency injection and registry patterns:

### Component Initialization Flow

```mermaid
graph TD
    subgraph "Simulator Initialization"
        A["`Simulator.__init__()
        config: SimulationConfig`"] --> B["`Cluster()
        Initialization`"]
        A --> C["`MetricsStore()
        Initialization`"]
        A --> D["`RequestGeneratorRegistry.get()
        Factory Pattern`"]
        A --> E["`GlobalSchedulerRegistry.get()
        Factory Pattern`"]
    end
    
    subgraph "Registry-Based Factory Pattern"
        F["`RequestGeneratorRegistry`"] --> G["`SyntheticRequestGenerator
        TraceRequestGenerator`"]
        H["`GlobalSchedulerRegistry`"] --> I["`RandomGlobalScheduler
        RoundRobinGlobalScheduler
        LORGlobalScheduler`"]
    end
    
    subgraph "Configuration Resolution"
        J["`config.request_generator_config
        .get_type()`"] --> K["`Type-based
        Selection`"]
        K --> L["`Instance
        Creation`"]
    end
    
    D --> F
    E --> H
    F --> J
    H --> J
    J --> G
    J --> I
    
    style A fill:#f9f9f9
    style F fill:#f9f9f9
    style H fill:#f9f9f9
```

Key initialization patterns:

- **Registry Pattern**: Component types are resolved through registry lookups using `get_type()` methods [vidur/simulator.py:38-46]()
- **Dependency Injection**: The `Simulator` injects dependencies (scheduler, metrics store) into components during creation
- **Configuration Propagation**: Nested configurations are passed down to appropriate subsystems [vidur/simulator.py:32-36]()

**Sources:** [vidur/simulator.py:18-49](), [vidur/request_generator/synthetic_request_generator.py:16-29]()

## Event Processing and State Management  

The simulation maintains state through event processing and component interaction:

### State Flow and Event Handling

```mermaid
graph TD
    subgraph "Event Processing Pipeline"
        A["`BaseEvent
        handle_event()`"] --> B["`Scheduler
        Processing`"]
        A --> C["`MetricsStore
        Recording`"]
        B --> D["`New Events
        Generation`"]
        C --> E["`Performance
        Tracking`"]
    end
    
    subgraph "State Management"
        F["`Simulator._time
        Current Time`"] --> G["`Event._time
        Event Timestamp`"]
        H["`Scheduler State
        Pending Requests`"] --> I["`Replica State
        Active Batches`"]
        J["`MetricsStore
        Historical Data`"] --> K["`DataSeries
        CDFSketch`"]
    end
    
    subgraph "Output Generation"
        L["`_write_output()
        atexit handler`"] --> M["`JSON Trace
        _event_trace`"]
        L --> N["`Chrome Trace
        _event_chrome_trace`"]
        L --> O["`Metrics Plots
        metric_store.plot()`"]
    end
    
    A --> F
    D --> A
    E --> J
    C --> L
    
    style A fill:#f9f9f9
    style F fill:#f9f9f9
    style J fill:#f9f9f9
```

The simulation manages multiple state dimensions:

- **Temporal State**: Simulation time progresses through event timestamps [vidur/simulator.py:66,109-110]()
- **Request State**: Tracking requests from arrival through completion via events and scheduler state
- **Resource State**: GPU memory, batch scheduling, and utilization managed by cluster components
- **Metrics State**: Continuous collection of performance data through the `MetricsStore` [vidur/simulator.py:37]()

**Sources:** [vidur/simulator.py:64-81](), [vidur/simulator.py:82-94](), [vidur/simulator.py:117-128]()

## Request Generation Integration

The request generation subsystem integrates with the core simulation through event scheduling:

### Request Generation Flow

```mermaid
graph TD
    subgraph "Request Generation"
        A["`_init_event_queue()
        Simulator Startup`"] --> B["`request_generator
        .generate()`"]
        B --> C["`Request Objects
        arrived_at timestamps`"]
        C --> D["`RequestArrivalEvent
        Creation`"]
        D --> E["`heappush()
        Event Scheduling`"]
    end
    
    subgraph "Synthetic Generation"
        F[SyntheticRequestGenerator] --> G["`RequestLengthGeneratorRegistry
        Prefill/Decode Tokens`"]
        F --> H["`RequestIntervalGeneratorRegistry
        Inter-arrival Times`"]
        G --> I["`FixedRequestLengthGenerator
        UniformRequestLengthGenerator
        ZipfRequestLengthGenerator`"]
        H --> J["`PoissonRequestIntervalGenerator
        GammaRequestIntervalGenerator
        TraceRequestIntervalGenerator`"]
    end
    
    subgraph "Request Properties"
        K["`Request Entity
        arrived_at
        num_prefill_tokens
        num_decode_tokens`"] --> L["`RequestArrivalEvent
        Event Wrapper`"]
    end
    
    B --> F
    C --> K
    K --> L
    L --> D
    
    style A fill:#f9f9f9
    style B fill:#f9f9f9
    style K fill:#f9f9f9
```

The request generation system demonstrates the modular architecture:

- **Pluggable Generators**: Registry pattern allows different request generation strategies [vidur/simulator.py:38-41]()
- **Statistical Modeling**: Support for various probability distributions for realistic workload modeling [vidur/request_generator/synthetic_request_generator.py:21-28]()
- **Event Integration**: Generated requests are converted to `RequestArrivalEvent` objects for event queue processing [vidur/simulator.py:104-107]()

**Sources:** [vidur/simulator.py:103-108](), [vidur/request_generator/synthetic_request_generator.py:52-82]()

---

