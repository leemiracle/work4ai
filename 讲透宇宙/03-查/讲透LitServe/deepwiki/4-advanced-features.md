<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/LitServe · page 4 Advanced Features · fetched 2026-10-21 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/litserve/server.py](src/litserve/server.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/e2e/test_e2e.py](tests/e2e/test_e2e.py)

</details>



This document covers advanced capabilities in LitServe for production deployments and specialized use cases. These features extend beyond basic model serving to provide enterprise-grade functionality including dynamic batching, hardware optimization, monitoring, and protocol integrations.

For basic server setup and configuration, see [Core Concepts](#2). For API specifications and OpenAI compatibility, see [API Specifications](#3).

## Hardware Acceleration & Device Management

LitServe provides comprehensive hardware acceleration support with automatic device detection and manual configuration options. The system supports CPU, CUDA (NVIDIA GPUs), and MPS (Apple Metal Performance Shaders) accelerators.

### Device Detection and Configuration

The `_Connector` class handles accelerator and device management through the LitServer initialization:

```mermaid
graph TB
    subgraph "Device Configuration Flow"
        LitServer["LitServer.__init__()"]
        Connector["_Connector(accelerator, devices)"]
        DeviceList["self.devices"]
        WorkerConfig["self.inference_workers_config"]
    end
    
    subgraph "Accelerator Types"
        Auto["auto - Auto-detect"]
        CPU["cpu - Force CPU"]
        CUDA["cuda - NVIDIA GPUs"] 
        MPS["mps - Apple Metal"]
    end
    
    subgraph "Device Allocation"
        SingleDevice["Single device: ['cuda:0']"]
        MultiDevice["Multi device: ['cuda:0', 'cuda:1']"]
        WorkersPerDevice["workers_per_device multiplication"]
    end
    
    LitServer --> Connector
    Connector --> DeviceList
    DeviceList --> WorkerConfig
    
    Auto --> Connector
    CPU --> Connector
    CUDA --> Connector
    MPS --> Connector
    
    DeviceList --> SingleDevice
    DeviceList --> MultiDevice
    WorkersPerDevice --> WorkerConfig
```

**Hardware Configuration Options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `accelerator` | `Literal["cpu", "cuda", "mps", "auto"]` | `"auto"` | Hardware type for inference |
| `devices` | `Union[int, Literal["auto"]]` | `"auto"` | Number of devices to use |
| `workers_per_device` | `int` | `1` | Worker processes per device |

The device identification logic creates device strings using the `device_identifiers` method [src/litserve/server.py:867-870]():

```python
def device_identifiers(self, accelerator, device):
    if isinstance(device, Sequence):
        return [f"{accelerator}:{el}" for el in device]
    return [f"{accelerator}:{device}"]
```

### Worker Process Architecture

Each device spawns multiple worker processes based on the `workers_per_device` configuration. The worker allocation is calculated in the constructor [src/litserve/server.py:790]():

```python
self.inference_workers_config = self.devices * self.workers_per_device
```

Workers are launched using multiprocessing with proper device assignment [src/litserve/server.py:804-827]():

```mermaid
sequenceDiagram
    participant Server as "LitServer"
    participant Manager as "mp.Manager"
    participant Worker as "inference_worker" 
    participant Device as "Hardware Device"
    
    Server->>Manager: Create worker queue
    Server->>Manager: Set worker status tracking
    loop For each device × workers_per_device
        Server->>Worker: spawn process(device_id, worker_id)
        Worker->>Device: Initialize on assigned device
        Worker->>Manager: Report WorkerSetupStatus.READY
    end
    Server->>Server: verify_worker_status()
```

Sources: [src/litserve/server.py:794-827](), [src/litserve/server.py:1026-1031]()

## Batching Strategies

LitServe implements sophisticated batching strategies through the `LitAPI` configuration and processing loops. Batching improves throughput by processing multiple requests simultaneously.

### Batch Configuration

Batching behavior is controlled through `LitAPI` parameters that are validated by the `_LitAPIConnector`:

```mermaid
graph LR
    subgraph "Batch Configuration"
        MaxBatchSize["max_batch_size"]
        BatchTimeout["batch_timeout"] 
        RequestTimeout["request_timeout"]
    end
    
    subgraph "Validation Logic"
        Connector["_LitAPIConnector.set_request_timeout()"]
        ValidationCheck["batch_timeout < request_timeout"]
    end
    
    subgraph "Processing Loops"
        SingleLoop["SingleLoop - No batching"]
        BatchedLoop["BatchedLoop - Static batching"]
        StreamingLoop["StreamingLoop - Stream + batch"]
    end
    
    MaxBatchSize --> Connector
    BatchTimeout --> Connector
    RequestTimeout --> Connector
    
    Connector --> ValidationCheck
    ValidationCheck --> SingleLoop
    ValidationCheck --> BatchedLoop
    ValidationCheck --> StreamingLoop
```

The timeout validation ensures batch timeouts don't exceed request timeouts [src/litserve/server.py:244-246]():

```python
if lit_api.batch_timeout > timeout and timeout not in (False, -1):
    raise ValueError("batch_timeout must be less than request_timeout")
```

### Dynamic Batching Implementation

Dynamic batching allows the system to accumulate requests up to `max_batch_size` or until `batch_timeout` expires, whichever comes first. This optimizes both latency and throughput based on request patterns.

**Batching Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_batch_size` | `int` | `1` | Maximum requests per batch |
| `batch_timeout` | `float` | `0.0` | Max wait time to fill batch (seconds) |
| `request_timeout` | `float` | `30.0` | Overall request timeout |

Sources: [src/litserve/server.py:240-246](), [src/litserve/server.py:215-257]()

## Callbacks and Middleware

LitServe provides a comprehensive callback and middleware system for cross-cutting concerns like logging, monitoring, authentication, and request preprocessing.

### Callback System Architecture

The `CallbackRunner` manages lifecycle events throughout request processing:

```mermaid
graph TD
    subgraph "Callback Events"
        OnServerStart["EventTypes.ON_SERVER_START"]
        OnRequest["EventTypes.ON_REQUEST"] 
        OnResponse["EventTypes.ON_RESPONSE"]
        OnServerEnd["EventTypes.ON_SERVER_END"]
    end
    
    subgraph "Callback Registration"
        CallbackRunner["CallbackRunner(callbacks)"]
        TriggerEvent["trigger_event(event_type, **kwargs)"]
    end
    
    subgraph "Event Context"
        ActiveRequests["active_requests count"]
        LitServerRef["litserver instance"]
        RequestData["request payload"]
    end
    
    OnServerStart --> CallbackRunner
    OnRequest --> CallbackRunner  
    OnResponse --> CallbackRunner
    OnServerEnd --> CallbackRunner
    
    CallbackRunner --> TriggerEvent
    TriggerEvent --> ActiveRequests
    TriggerEvent --> LitServerRef
    TriggerEvent --> RequestData
```

Callbacks are triggered at key points in the request lifecycle [src/litserve/server.py:287-291]():

```python
self.server._callback_runner.trigger_event(
    EventTypes.ON_REQUEST.value,
    active_requests=self.server.active_requests,
    litserver=self.server,
)
```

### Middleware Integration

LitServe integrates with FastAPI's middleware system, supporting both built-in and custom middleware:

**Built-in Middleware:**
- `GZipMiddleware` - Response compression (disabled for streaming)
- `MaxSizeMiddleware` - Request size limiting  
- `RequestCountMiddleware` - Active request tracking

**Middleware Registration:**

```mermaid
flowchart LR
    subgraph "Middleware Configuration"
        MiddlewareList["middlewares: List[Union[Callable, tuple]]"]
        TupleFormat["(Middleware, kwargs)"]
        CallableFormat["Middleware class"]
    end
    
    subgraph "Registration Process" 
        RegisterMiddleware["_register_middleware()"]
        AddMiddleware["app.add_middleware()"]
    end
    
    subgraph "Built-in Middleware"
        GZip["GZipMiddleware"]
        MaxSize["MaxSizeMiddleware"] 
        RequestCount["RequestCountMiddleware"]
    end
    
    MiddlewareList --> RegisterMiddleware
    TupleFormat --> RegisterMiddleware
    CallableFormat --> RegisterMiddleware
    RegisterMiddleware --> AddMiddleware
    
    GZip --> AddMiddleware
    MaxSize --> AddMiddleware
    RequestCount --> AddMiddleware
```

The middleware registration logic handles both formats [src/litserve/server.py:1002-1008]():

```python
def _register_middleware(self):
    for middleware in self.middlewares:
        if isinstance(middleware, tuple):
            middleware, kwargs = middleware
            self.app.add_middleware(middleware, **kwargs)
        elif callable(middleware):
            self.app.add_middleware(middleware)
```

Sources: [src/litserve/server.py:1002-1008](), [src/litserve/server.py:756-760](), [src/litserve/callbacks/base.py]()

## Logging and Monitoring

LitServe provides comprehensive logging and monitoring capabilities through structured logging, configurable log levels, and request tracking.

### Logging Configuration

The logging system supports multiple output formats and handlers through the `configure_logging` function:

```mermaid
graph TB
    subgraph "Logging Configuration"
        ConfigureLogging["configure_logging()"]
        LogLevel["level: Union[str, int]"]
        LogFormat["format: str"]
        UseRich["use_rich: bool"]
    end
    
    subgraph "Handler Types"
        StreamHandler["StreamHandler (default)"]
        RichHandler["RichHandler (rich=True)"]
        CustomHandler["Custom handlers via add_log_handler()"]
    end
    
    subgraph "Library Logger Setup"
        LibraryLogger["logging.getLogger('litserve')"]
        HandlerConfig["handler configuration"]
        LoggerLevel["logger.setLevel(level)"]
    end
    
    ConfigureLogging --> LogLevel
    ConfigureLogging --> LogFormat
    ConfigureLogging --> UseRich
    
    UseRich --> StreamHandler
    UseRich --> RichHandler
    
    ConfigureLogging --> LibraryLogger
    LibraryLogger --> HandlerConfig
    LibraryLogger --> LoggerLevel
    HandlerConfig --> StreamHandler
    HandlerConfig --> RichHandler
    HandlerConfig --> CustomHandler
```

**Logging Levels and Configuration:**

| Level | Usage | Description |
|-------|-------|-------------|
| `"critical"` | Production errors | Only severe errors |
| `"error"` | Error conditions | Error conditions |
| `"warning"` | Production default | Warning messages |
| `"info"` | Development default | General information |
| `"debug"` | Development/troubleshooting | Detailed debugging |
| `"trace"` | Verbose troubleshooting | Very verbose output |

The rich logging integration provides enhanced formatting [src/litserve/utils.py:167-178]():

```python
if use_rich:
    try:
        from rich.logging import RichHandler
        from rich.traceback import install
        
        install(show_locals=True)
        handler = RichHandler(rich_tracebacks=True, show_time=True, show_path=True)
    except ImportError:
        logger.warning("Rich is not installed, using default logging")
        handler = _get_default_handler(stream, format)
```

### Request Tracking and Monitoring

LitServe provides built-in request tracking through the `track_requests` configuration:

```mermaid
sequenceDiagram
    participant Client as "HTTP Client"
    participant Middleware as "RequestCountMiddleware"
    participant Counter as "mp.Value('i', 0)"
    participant Server as "LitServer"
    participant Callback as "CallbackRunner"
    
    Client->>Middleware: HTTP Request
    Middleware->>Counter: Increment active_counter
    Middleware->>Server: Forward request
    Server->>Callback: trigger_event(ON_REQUEST, active_requests=sum(counters))
    Note over Server: Process request
    Server->>Callback: trigger_event(ON_RESPONSE)
    Server->>Middleware: Response ready
    Middleware->>Counter: Decrement active_counter
    Middleware->>Client: HTTP Response
```

The active request counting is implemented using multiprocessing-safe counters [src/litserve/server.py:896-899]():

```python
@property
def active_requests(self):
    if self.track_requests and self.active_counters:
        return sum(counter.value for counter in self.active_counters)
    return None
```

Sources: [src/litserve/utils.py:143-183](), [src/litserve/server.py:896-899](), [src/litserve/server.py:1353-1355]()

## Transport Layer

LitServe implements a sophisticated transport layer for inter-process communication between HTTP servers and inference workers, supporting both multiprocessing queues and ZeroMQ for high-throughput scenarios.

### Transport Configuration

The transport system is configured through `TransportConfig` and supports two backends:

```mermaid
graph TB
    subgraph "Transport Selection"
        FastQueue["fast_queue: bool"]
        Platform["sys.platform check"]
        TransportConfig["TransportConfig"]
    end
    
    subgraph "Transport Types"
        MPTransport["Multiprocessing Queue"]
        ZMQTransport["ZeroMQ (fast_queue=True)"]
    end
    
    subgraph "Configuration"
        Manager["mp.Manager()"]
        NumConsumers["num_consumers (API servers)"]
        RequestQueues["Request queues per LitAPI"]
    end
    
    FastQueue --> TransportConfig
    Platform --> TransportConfig
    TransportConfig --> MPTransport
    TransportConfig --> ZMQTransport
    
    TransportConfig --> Manager
    TransportConfig --> NumConsumers
    Manager --> RequestQueues
```

The transport selection logic considers platform compatibility [src/litserve/server.py:743-745]():

```python
if sys.platform == "win32" and fast_queue:
    warnings.warn("ZMQ is not supported on Windows with LitServe. Disabling ZMQ.")
    fast_queue = False
```

### Message Flow Architecture

The transport layer handles bidirectional communication between API servers and workers:

```mermaid
sequenceDiagram
    participant API as "FastAPI Server"
    participant RequestQ as "Request Queue"
    participant Worker as "Inference Worker"
    participant Transport as "MessageTransport" 
    participant ResponseBuffer as "Response Buffer"
    
    API->>RequestQ: put(response_queue_id, uid, timestamp, payload)
    Worker->>RequestQ: get() request
    Worker->>Worker: process_request()
    Worker->>Transport: send(uid, response, status)
    
    par Response Handling
        Transport->>ResponseBuffer: areceive(consumer_id)
        ResponseBuffer->>ResponseBuffer: response_buffer[uid] = response
        ResponseBuffer->>API: event.set()
    and Streaming Response
        Transport->>ResponseBuffer: areceive(consumer_id) 
        ResponseBuffer->>ResponseBuffer: stream_buffer.append(chunk)
        ResponseBuffer->>API: event.set()
    end
```

The response buffer handling supports both regular and streaming responses [src/litserve/server.py:127-139]():

```python
async def response_queue_to_buffer(
    transport: MessageTransport,
    response_buffer: Dict[str, Union[Tuple[deque, asyncio.Event], asyncio.Event]],
    consumer_id: int,
    litapi_connector: "_LitAPIConnector",
):
    mixed_streaming = (
        len(litapi_connector.lit_apis) > 1
        and litapi_connector.any_stream()
        and not all(api.stream for api in litapi_connector)
    )
```

Sources: [src/litserve/server.py:790-791](), [src/litserve/server.py:127-176](), [src/litserve/transport/factory.py]()

## MCP Integration

Model Context Protocol (MCP) integration enables LitServe to work seamlessly with AI agent frameworks and tool ecosystems. MCP provides a standardized way for language models to interact with external tools and data sources.

### MCP Server Architecture

The MCP integration is implemented through the `_LitMCPServerConnector` when the MCP package is available:

```mermaid
graph TB
    subgraph "MCP Integration Check"
        MCPAvailable["_MCP_AVAILABLE = is_package_installed('mcp')"]
        ImportMCP["from litserve.mcp import _LitMCPServerConnector"]
    end
    
    subgraph "LitAPI MCP Configuration"
        LitAPIMCP["lit_api.mcp: MCPServer"]
        ToolEndpoint["mcp.as_tool(): ToolEndpointType"]
        MCPTools["litapi_connector.get_mcp_tools()"]
    end
    
    subgraph "Server Integration"
        MCPConnector["_LitMCPServerConnector()"]
        ConnectMCP["connect_mcp_server(tools, app)"]
        Lifespan["mcp_server.lifespan(app)"]
    end
    
    MCPAvailable --> ImportMCP
    LitAPIMCP --> ToolEndpoint
    ToolEndpoint --> MCPTools
    MCPTools --> MCPConnector
    MCPConnector --> ConnectMCP
    ConnectMCP --> Lifespan
```

### MCP Tool Registration

Each `LitAPI` instance can expose MCP tools through the `mcp` attribute. The tools are collected and registered with the MCP server [src/litserve/server.py:258-263]():

```python
def get_mcp_tools(self) -> List["ToolEndpointType"]:
    mcp_tools = []
    for lit_api in self.lit_apis:
        if lit_api.mcp:
            mcp_tools.append(lit_api.mcp.as_tool())
    return mcp_tools
```

### MCP Lifecycle Management

The MCP server is integrated into the FastAPI application lifecycle [src/litserve/server.py:853-856]():

```python
if _MCP_AVAILABLE:
    async with self.mcp_server.lifespan(app):
        yield
else:
    yield
```

This integration allows AI agents and clients that support MCP to discover and interact with LitServe-hosted models as tools within their workflows.

Sources: [src/litserve/server.py:63](), [src/litserve/server.py:258-263](), [src/litserve/server.py:853-856](), [src/litserve/server.py:1365-1369]()

---

