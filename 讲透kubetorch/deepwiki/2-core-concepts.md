<!-- source: DeepWiki mcp.deepwiki.com · repo run-house/kubetorch · page 2 Core Concepts · fetched 2026-10-21 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page explains the fundamental concepts and abstractions in Kubetorch that developers interact with. It covers the core programming model, including `kt.fn` for function wrapping, `kt.Compute` for resource specification, the serverless execution paradigm, and the client-server architecture.

For installation instructions, see [Installation](#3.1). For detailed API documentation, see [API Reference](#5). For advanced usage patterns, see [Advanced Usage](#6).

---

## Overview of Core Abstractions

Kubetorch provides three primary abstractions for distributed computing on Kubernetes:

| Abstraction | Purpose | Example Usage |
|-------------|---------|---------------|
| `kt.fn` | Wraps local Python functions for remote execution | `kt.fn(my_function)` |
| `kt.Compute` | Specifies resource requirements (CPUs, memory, GPUs) | `kt.Compute(cpus="4", memory="16Gi")` |
| `.to()` | Binds a wrapped function to compute resources | `remote_fn = kt.fn(local_fn).to(compute)` |

These abstractions work together to enable a serverless execution model where Kubernetes complexity is hidden behind a Pythonic interface.

### Conceptual Relationship Diagram

```mermaid
graph TB
    LocalFunc["Local Python Function<br/>def hello_world():"]
    ktfn["kt.fn wrapper"]
    WrappedFunc["Wrapped Function<br/>(not yet deployed)"]
    ktCompute["kt.Compute<br/>Resource Specification"]
    toMethod[".to() binding"]
    RemoteFunc["Remote Function<br/>(deployed on K8s)"]
    Invocation["remote_fn()<br/>Function Call"]
    K8sExecution["Kubernetes Pod<br/>Execution"]
    Result["Return Value<br/>(1-2 seconds)"]
    
    LocalFunc -->|"kt.fn()"| ktfn
    ktfn --> WrappedFunc
    ktCompute -->|"defines resources"| toMethod
    WrappedFunc -->|".to(compute)"| toMethod
    toMethod --> RemoteFunc
    RemoteFunc -->|"invoke"| Invocation
    Invocation -->|"submits to cluster"| K8sExecution
    K8sExecution -->|"returns"| Result
    Result -.->|"real-time logs"| Invocation
    
    style ktfn fill:#f9f9f9,stroke:#333,stroke-width:2px
    style ktCompute fill:#f9f9f9,stroke:#333,stroke-width:2px
    style toMethod fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [README.md:13-29]()

---

## Functions (kt.fn)

The `kt.fn` wrapper transforms local Python functions into remotely executable units without requiring explicit code serialization or containerization.

### Function Wrapping Mechanism

```mermaid
graph LR
    subgraph "Developer Code"
        LocalDef["def hello_world():<br/>    return 'Hello'"]
    end
    
    subgraph "kt.fn Wrapper"
        Wrapper["kt.fn(hello_world)"]
        NoSerial["No Code Serialization"]
        NoPickle["No Pickle Required"]
    end
    
    subgraph "Wrapped Result"
        WrappedObj["Function Object<br/>(ready for .to())"]
    end
    
    LocalDef -->|"pass to"| Wrapper
    Wrapper -->|"wraps without"| NoSerial
    Wrapper -->|"wraps without"| NoPickle
    Wrapper --> WrappedObj
```

### Key Characteristics

The `kt.fn` wrapper has the following properties:

- **No Explicit Serialization**: Developers do not need to pickle, serialize, or otherwise package their code manually [README.md:9]()
- **Deferred Deployment**: Wrapping a function with `kt.fn` does not immediately deploy it to Kubernetes. Deployment occurs when `.to()` is called [README.md:24]()
- **Transparent Execution**: Once deployed, calling the remote function feels identical to calling the local version [README.md:27-28]()
- **Real-Time Communication**: Logs and exceptions from remote execution propagate back immediately [README.md:7-8]()

### Usage Pattern

```python
# Local function definition
def hello_world():
    return "Hello from Kubetorch!"

# Wrap with kt.fn
wrapped_fn = kt.fn(hello_world)  # Not yet deployed

# Function remains local until bound to compute
```

**Sources:** [README.md:13-24]()

---

## Compute Resources (kt.Compute)

The `kt.Compute` class specifies resource requirements for remote function execution. It defines the computational resources that Kubernetes will allocate when the function runs.

### Resource Specification

```mermaid
graph TB
    subgraph "kt.Compute Specification"
        ComputeObj["kt.Compute()"]
        CPUs["cpus parameter<br/>e.g., '0.1', '4', '16'"]
        Memory["memory parameter<br/>e.g., '16Gi', '32Gi'"]
        GPUs["GPU specification<br/>(if needed)"]
    end
    
    subgraph "Resource Types"
        SmallJob["Small Jobs<br/>cpus='0.1'"]
        MediumJob["Medium Jobs<br/>cpus='4', memory='16Gi'"]
        MLWorkload["ML Workloads<br/>GPUs, High Memory"]
    end
    
    ComputeObj -->|"accepts"| CPUs
    ComputeObj -->|"accepts"| Memory
    ComputeObj -->|"accepts"| GPUs
    
    CPUs -->|"minimal"| SmallJob
    CPUs -->|"moderate"| MediumJob
    Memory -->|"moderate"| MediumJob
    GPUs -->|"intensive"| MLWorkload
```

### Resource Parameters

| Parameter | Type | Purpose | Example |
|-----------|------|---------|---------|
| `cpus` | String | CPU allocation | `"0.1"`, `"4"`, `"16"` |
| `memory` | String | Memory allocation | `"16Gi"`, `"32Gi"` |
| GPUs | (varies) | GPU requirements | Configuration depends on cluster setup |

### Example Specifications

```python
# Minimal resources for lightweight tasks
small_compute = kt.Compute(cpus="0.1")

# Medium resources for standard ML training
medium_compute = kt.Compute(cpus="4", memory="16Gi")

# Large resources for distributed training
large_compute = kt.Compute(cpus="16", memory="64Gi")
```

The resource specification determines how Kubetorch's bin-packing and optimization systems allocate cluster resources (see [Resource Management](#4.3) and [Optimization Engine](#4.4)).

**Sources:** [README.md:21]()

---

## The Binding Mechanism (.to())

The `.to()` method binds a wrapped function to compute resources, creating a deployed remote function ready for execution on Kubernetes.

### Binding Process Flow

```mermaid
sequenceDiagram
    participant Dev as Developer Code
    participant Wrapper as kt.fn Wrapped Function
    participant Compute as kt.Compute Object
    participant ToMethod as .to() Method
    participant K8sDeploy as K8s Deployment
    participant RemoteFn as Remote Function Handle
    
    Dev->>Wrapper: kt.fn(local_function)
    Note over Wrapper: Function wrapped,<br/>not deployed
    
    Dev->>Compute: kt.Compute(cpus="0.1")
    Note over Compute: Resources defined
    
    Dev->>ToMethod: wrapped_fn.to(compute)
    ToMethod->>K8sDeploy: Deploy with resources
    Note over K8sDeploy: Pod provisioned<br/>on K8s cluster
    
    K8sDeploy->>RemoteFn: Return remote handle
    RemoteFn->>Dev: ready for invocation
    
    Note over Dev,RemoteFn: remote_fn() calls execute on K8s
```

### Two-Stage Deployment Model

Kubetorch uses a two-stage model separating function definition from deployment:

**Stage 1: Function Wrapping**
```python
wrapped_fn = kt.fn(hello_world)  # No deployment yet
```

**Stage 2: Resource Binding and Deployment**
```python
remote_fn = wrapped_fn.to(compute)  # Deployed to K8s
```

This separation allows:
- Functions to be defined once and deployed with different resource configurations
- Resource specifications to be reused across multiple functions
- Lazy deployment that occurs only when `.to()` is called

### Complete Example from Hello World

[README.md:13-29]() demonstrates the full binding pattern:

```python
import kubetorch as kt

def hello_world():
    return "Hello from Kubetorch!"

if __name__ == "__main__":
    # Define compute resources
    compute = kt.Compute(cpus=".1")
    
    # Wrap and bind in one statement
    remote_hello = kt.fn(hello_world).to(compute)
    
    # Execute remotely
    result = remote_hello()  # Runs on K8s cluster
    print(result)  # "Hello from Kubetorch!"
```

**Sources:** [README.md:20-28]()

---

## Serverless Execution Model

Kubetorch implements a serverless paradigm where Kubernetes infrastructure is abstracted away, presenting developers with a simple function-call interface.

### Abstraction Layers

```mermaid
graph TB
    subgraph "Developer Perspective"
        DevCode["Python Code<br/>remote_fn()"]
        LocalLike["Feels Like:<br/>Local Function Call"]
    end
    
    subgraph "Kubetorch Abstraction"
        NoRuntime["No Local Runtime<br/>No Daemon Process"]
        NoSerial["No Code Serialization<br/>No Manual Packaging"]
        AutoLog["Automatic Log<br/>Propagation"]
    end
    
    subgraph "Kubernetes Reality"
        K8sAPI["Kubernetes API"]
        Pods["Pod Provisioning"]
        Resources["Resource Allocation"]
        Execution["Remote Execution"]
    end
    
    DevCode -->|"abstracts via"| NoRuntime
    DevCode -->|"abstracts via"| NoSerial
    DevCode -->|"abstracts via"| AutoLog
    
    NoRuntime -->|"hides"| K8sAPI
    NoSerial -->|"hides"| Pods
    AutoLog -->|"hides"| Resources
    
    K8sAPI --> Execution
    Pods --> Execution
    Resources --> Execution
    Execution -.->|"real-time feedback"| DevCode
```

### Serverless Characteristics

The serverless model provides the following properties:

| Characteristic | Traditional Kubernetes | Kubetorch Serverless |
|----------------|----------------------|---------------------|
| Container Building | Manual Dockerfile creation | Automatic |
| Code Packaging | Manual serialization/packaging | No serialization needed |
| Deployment | Manual YAML files, kubectl commands | Single `.to()` call |
| Iteration Speed | 10+ minutes | 1-2 seconds |
| Log Access | Manual kubectl logs commands | Real-time propagation |
| Environment Support | Limited to containerized environments | Any Python environment |

### No Local Runtime Requirement

Unlike traditional distributed computing frameworks, Kubetorch requires no local daemon or server process [README.md:9](). This enables usage from:

- IDEs (VSCode, PyCharm)
- Jupyter Notebooks
- Python REPL
- CI/CD pipelines
- Production applications
- Any environment with Python installed

### Fast Iteration Cycles

The serverless model enables 1-2 second iteration cycles [README.md:7]() by:

1. Eliminating container rebuild steps
2. Avoiding manual deployment processes
3. Maintaining persistent cluster connections
4. Streaming logs in real-time rather than polling

For more on iteration speed, see [Execution Lifecycle](#4.2).

**Sources:** [README.md:7-9](), [README.md:33]()

---

## Client-Server Architecture

Kubetorch implements a split architecture with a Python client library running locally and a Kubernetes deployment managing remote execution.

### Component Separation

```mermaid
graph TB
    subgraph "Local Environment"
        DevMachine["Developer Machine"]
        PythonCode["Python Code<br/>import kubetorch as kt"]
        ClientLib["Kubetorch Client<br/>(pip package)"]
        ktfnLocal["kt.fn wrapper"]
        ktComputeLocal["kt.Compute spec"]
    end
    
    subgraph "Network Boundary"
        Network["Network<br/>Communication"]
    end
    
    subgraph "Kubernetes Cluster"
        K8sCluster["K8s Cluster"]
        Deployment["Kubetorch Deployment<br/>(Helm chart)"]
        ServerSide["Server Components"]
        Pods["Execution Pods"]
        Resources["Resource Management"]
    end
    
    DevMachine --> PythonCode
    PythonCode -->|"imports"| ClientLib
    ClientLib --> ktfnLocal
    ClientLib --> ktComputeLocal
    
    ktfnLocal -->|"submits requests"| Network
    ktComputeLocal -->|"sends specs"| Network
    
    Network -->|"API calls"| Deployment
    Deployment --> ServerSide
    ServerSide --> Pods
    ServerSide --> Resources
    
    Pods -.->|"logs, results"| Network
    Network -.->|"real-time stream"| ClientLib
```

### Client Responsibilities

The local Python client (`kubetorch[client]` package) handles:

- **Function Wrapping**: Applying `kt.fn` to local functions
- **Resource Specification**: Creating `kt.Compute` objects
- **Request Submission**: Sending execution requests to the cluster
- **Result Reception**: Receiving return values from remote execution
- **Log Streaming**: Displaying real-time logs and exceptions

Installation: `pip install "kubetorch[client]"` [README.md:42]()

### Server Responsibilities

The Kubernetes deployment (Helm chart v0.2.2) handles:

- **Request Processing**: Accepting execution requests from clients
- **Pod Provisioning**: Creating Kubernetes pods for function execution
- **Resource Allocation**: Implementing bin-packing and optimization
- **Execution Management**: Running functions and capturing output
- **Fault Handling**: Detecting and recovering from failures
- **Monitoring**: Tracking execution metrics and cluster state

Installation: See [Helm Installation](#7.2)

### Communication Protocol

The client and server communicate through a network protocol that supports:

- **Bidirectional Communication**: Client sends requests, server streams logs [README.md:7]()
- **Real-Time Updates**: Logs, exceptions, and hardware faults propagate immediately [README.md:7-8]()
- **Result Delivery**: Function return values transmitted back to client [README.md:28]()
- **1-2 Second Latency**: End-to-end request/response cycle [README.md:7]()

### Distribution Model

| Component | Distribution Channel | Version |
|-----------|---------------------|---------|
| Client Library | PyPI (`pip install`) | Follows Python package versioning |
| Server Deployment | OCI Registry (Helm) | v0.2.2 [README.md:50]() |

This split distribution allows independent versioning and deployment of client and server components.

**Sources:** [README.md:39-55]()

---

## Execution Flow: From Local Code to Remote Execution

The following diagram shows the complete execution lifecycle, bridging developer code entities to cluster execution:

```mermaid
sequenceDiagram
    participant Dev as Developer<br/>my_script.py
    participant ktfn as kt.fn(my_function)
    participant ktComp as kt.Compute(cpus="0.1")
    participant Client as Kubetorch Client<br/>(local)
    participant Server as Kubetorch Server<br/>(K8s deployment)
    participant Optimizer as Optimization Layer<br/>(bin-packing)
    participant K8s as Kubernetes API
    participant Pod as Execution Pod
    
    Dev->>ktfn: define function
    Note over ktfn: Function wrapped,<br/>no serialization
    
    Dev->>ktComp: specify resources
    Note over ktComp: Resource requirements<br/>defined
    
    Dev->>ktfn: .to(kt.Compute)
    ktfn->>Client: deployment request
    Client->>Server: submit request
    
    Server->>Optimizer: resource allocation
    Note over Optimizer: Bin-packing analysis
    
    Optimizer->>K8s: optimized request
    K8s->>Pod: provision pod
    
    Pod->>Pod: execute function
    Pod-->>Client: stream logs (real-time)
    Client-->>Dev: display logs
    
    alt Success
        Pod->>Client: return result
        Client->>Dev: deliver result (1-2 sec)
    else Fault
        Pod->>Server: fault signal
        Note over Server: Fault handler triggered
        Server->>K8s: adjusted resources
        K8s->>Pod: retry execution
        Pod->>Client: return result (after recovery)
        Client->>Dev: deliver result + recovery info
    end
```

### Execution Stages

**Stage 1: Function Definition and Wrapping**
- Developer defines local Python function [README.md:16-17]()
- `kt.fn()` wraps function without serialization [README.md:24]()

**Stage 2: Resource Specification**
- Developer creates `kt.Compute` with resource requirements [README.md:21]()

**Stage 3: Binding and Deployment**
- `.to()` method binds function to compute [README.md:24]()
- Client submits deployment request to server

**Stage 4: Optimization and Provisioning**
- Server optimization layer analyzes resource requirements
- Kubernetes provisions pod with allocated resources

**Stage 5: Execution and Monitoring**
- Function executes in remote pod
- Logs stream back to client in real-time [README.md:7]()

**Stage 6: Result Delivery**
- Return value transmitted to client
- Total time: 1-2 seconds [README.md:7]()

### Hello World Execution Trace

Using the example from [README.md:13-29]():

```
my_script.py:
  line 16-17: def hello_world() definition
  line 21:    kt.Compute(cpus=".1") → resource spec
  line 24:    kt.fn(hello_world).to(compute) → deployment
  line 27:    remote_hello() → execution request
  
Kubernetes Cluster:
  Pod created with 0.1 CPU allocation
  Function executes: return "Hello from Kubetorch!"
  
Result:
  line 28:    print(result) → "Hello from Kubetorch!"
  Total time: 1-2 seconds
```

**Sources:** [README.md:13-29](), [README.md:7]()

---

## Summary

The core concepts in Kubetorch provide a clean abstraction over Kubernetes:

- **`kt.fn`** wraps local functions without serialization
- **`kt.Compute`** specifies resource requirements
- **`.to()`** binds functions to compute and deploys to Kubernetes
- **Serverless model** hides infrastructure complexity
- **Client-server architecture** splits concerns between local and remote
- **1-2 second execution** enables rapid iteration

For detailed API documentation, see [kt.fn](#5.1) and [kt.Compute](#5.2). For deployment instructions, see [Getting Started](#3).

---

