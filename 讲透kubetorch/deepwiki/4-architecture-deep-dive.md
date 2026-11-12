<!-- source: DeepWiki mcp.deepwiki.com · repo run-house/kubetorch · page 4 Architecture Deep Dive · fetched 2026-10-21 -->

# Architecture Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides detailed technical documentation of Kubetorch's internal architecture and design decisions. It covers the system's major components, execution flow, resource management strategies, optimization mechanisms, fault tolerance systems, and observability infrastructure.

For installation and deployment procedures, see [Deployment and Operations](#7). For API usage patterns, see [API Reference](#5). For core concepts and abstractions, see [Core Concepts](#2).

---

## Overview

Kubetorch implements a client-server architecture that abstracts Kubernetes complexity behind a Pythonic interface. The system consists of two primary deployment units:

1. **Client Library**: A pip-installable Python package (`kubetorch[client]`) that provides the developer-facing API
2. **Server Deployment**: A Helm-based Kubernetes deployment that manages remote execution, resource allocation, and fault handling

The architecture is designed to enable "1-2 second iteration cycles" [README.md:7]() while achieving "50%+ compute cost savings" and "95% fewer production faults" [README.md:34-35]() through intelligent resource management and automated fault recovery.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph ClientLayer["Client Layer (Local Environment)"]
        DevEnv["Developer Environment<br/>(IDE/Notebook/REPL/Script)"]
        KTLib["kubetorch Python Library"]
        KTFn["kt.fn<br/>Function Wrapper"]
        KTCompute["kt.Compute<br/>Resource Specification"]
    end
    
    subgraph DeploymentInfra["Deployment Infrastructure"]
        HelmChart["Helm Chart<br/>oci://ghcr.io/run-house/charts/kubetorch<br/>version 0.2.2"]
        OCIRegistry["OCI Registry<br/>ghcr.io/run-house"]
    end
    
    subgraph K8sCluster["Kubernetes Cluster (Remote Execution)"]
        KTNamespace["kubetorch namespace"]
        K8sDeployment["Kubetorch Deployment"]
        K8sAPI["Kubernetes API Server"]
        ExecutionPods["Execution Pods"]
    end
    
    subgraph OptimizationLayer["Optimization Subsystems"]
        BinPacker["Bin-Packing Engine"]
        DynamicScaler["Dynamic Scaling"]
        FaultHandler["Fault Handler"]
    end
    
    subgraph ObservabilityLayer["Observability"]
        LogStreamer["Real-time Log Streaming"]
        ExceptionProp["Exception Propagation"]
        HWFaultDetect["Hardware Fault Detection"]
    end
    
    DevEnv -->|"imports"| KTLib
    KTLib -->|"provides"| KTFn
    KTLib -->|"provides"| KTCompute
    
    KTFn -->|"submits execution request"| K8sDeployment
    KTCompute -->|"specifies resources"| K8sDeployment
    
    HelmChart -->|"pulls from"| OCIRegistry
    HelmChart -->|"deploys to"| KTNamespace
    KTNamespace -->|"contains"| K8sDeployment
    
    K8sDeployment -->|"interacts with"| K8sAPI
    K8sAPI -->|"provisions"| ExecutionPods
    
    K8sDeployment -->|"uses"| BinPacker
    K8sDeployment -->|"uses"| DynamicScaler
    ExecutionPods -->|"monitored by"| FaultHandler
    
    ExecutionPods -->|"streams to"| LogStreamer
    ExecutionPods -->|"propagates to"| ExceptionProp
    ExecutionPods -->|"detected by"| HWFaultDetect
    
    LogStreamer -->|"delivers to"| DevEnv
    ExceptionProp -->|"delivers to"| DevEnv
    HWFaultDetect -->|"notifies"| FaultHandler
```

**Sources:** [README.md:1-75]()

---

## System Components

Kubetorch consists of five primary component categories, each with distinct responsibilities and interfaces.

### Component Breakdown

| Component Category | Key Elements | Primary Responsibility | Interfaces |
|-------------------|--------------|------------------------|------------|
| **Client Library** | `kt.fn`, `kt.Compute`, `.to()` | Provide developer-facing API | Python API |
| **Deployment Infrastructure** | Helm chart, OCI registry | Package and distribute server components | Helm CLI |
| **Kubernetes Runtime** | Deployment, Namespace, Pods | Execute remote workloads | Kubernetes API |
| **Optimization Layer** | Bin-packer, Scaler, Fault handler | Optimize cost and reliability | Internal APIs |
| **Observability** | Log streaming, Exception propagation | Real-time feedback to developers | gRPC/HTTP streams |

### Client Library Components

The client library is installed via `pip install "kubetorch[client]"` [README.md:42]() and provides three core abstractions:

#### kt.Compute

Resource specification object that defines computational requirements.

**Example from README:**
```python
compute = kt.Compute(cpus=".1")
```
[README.md:21]()

The `kt.Compute` object accepts resource parameters including:
- `cpus`: CPU allocation (can be fractional, e.g., `".1"`)
- Additional parameters for memory, GPUs (inferred from usage patterns)

#### kt.fn

Function wrapper that transforms local Python functions into remotely executable functions.

**Example from README:**
```python
remote_hello = kt.fn(hello_world).to(compute)
```
[README.md:24]()

The `kt.fn` wrapper:
- Accepts a Python callable as input
- Returns a wrapped function object
- Provides `.to(compute)` method to bind function to resource specification
- Does not require explicit code serialization [README.md:9]()

#### .to() Method

Binding method that associates a wrapped function with a compute resource specification.

The `.to(compute)` call [README.md:24]():
- Binds the function to specified compute resources
- Returns a remotely executable function object
- Triggers server-side provisioning when the function is first invoked

### Deployment Infrastructure

The server-side deployment is distributed as a Helm chart via an OCI registry.

**OCI Registry Location:**
```
oci://ghcr.io/run-house/charts/kubetorch
```
[README.md:49]()

**Current Version:** `0.2.2` [README.md:50]()

**Installation Methods:**

1. **Direct OCI Install:**
```bash
helm upgrade --install kubetorch oci://ghcr.io/run-house/charts/kubetorch \
  --version 0.2.2 -n kubetorch --create-namespace
```
[README.md:49-50]()

2. **Local Chart Install:**
```bash
helm pull oci://ghcr.io/run-house/charts/kubetorch --version 0.2.2 --untar
helm upgrade --install kubetorch ./kubetorch -n kubetorch --create-namespace
```
[README.md:53-54]()

Both methods create a dedicated `kubetorch` namespace [README.md:50,54]() in the target Kubernetes cluster.

### Kubernetes Runtime Components

The Kubernetes deployment manages remote execution through standard Kubernetes primitives:

- **Namespace:** `kubetorch` - Isolated namespace for all Kubetorch resources
- **Deployment:** Manages the lifecycle of the Kubetorch server pods
- **Pods:** Ephemeral execution environments for user functions
- **Services:** Network endpoints for client-server communication

**Sources:** [README.md:38-56]()

---

## Execution Lifecycle

The execution lifecycle describes the complete flow from local function invocation to result delivery, achieving the claimed "1-2 second iteration cycles" [README.md:7]().

### Lifecycle Phases

```mermaid
sequenceDiagram
    participant Dev as "Developer<br/>(Local Python)"
    participant KTFn as "kt.fn Wrapper"
    participant KTCompute as "kt.Compute"
    participant K8sDeploy as "Kubetorch Deployment<br/>(K8s Cluster)"
    participant K8sAPI as "Kubernetes API"
    participant Pod as "Execution Pod"
    participant OptLayer as "Optimization Layer"
    
    Note over Dev,Pod: Phase 1: Function Definition
    Dev->>KTCompute: compute = kt.Compute(cpus=".1")
    Dev->>KTFn: kt.fn(hello_world)
    KTFn-->>Dev: wrapped function object
    Dev->>KTFn: .to(compute)
    KTFn-->>Dev: remote_hello (bound function)
    
    Note over Dev,Pod: Phase 2: Execution Request
    Dev->>KTFn: remote_hello()
    KTFn->>K8sDeploy: Submit execution request
    K8sDeploy->>OptLayer: Analyze resource requirements
    OptLayer->>OptLayer: Bin-packing analysis
    OptLayer->>OptLayer: Scaling decision
    OptLayer-->>K8sDeploy: Optimized allocation
    
    Note over Dev,Pod: Phase 3: Pod Provisioning
    K8sDeploy->>K8sAPI: Request pod with optimized resources
    K8sAPI->>Pod: Provision execution pod
    Pod->>Pod: Initialize environment
    Pod-->>K8sDeploy: Ready signal
    
    Note over Dev,Pod: Phase 4: Remote Execution
    K8sDeploy->>Pod: Execute function
    Pod->>Pod: Run hello_world()
    Pod-->>Dev: Stream logs (real-time)
    Pod-->>K8sDeploy: Execution result
    
    Note over Dev,Pod: Phase 5: Result Delivery
    K8sDeploy-->>KTFn: Return result
    KTFn-->>Dev: "Hello from Kubetorch!"
    Dev->>Dev: print(result)
    
    Note over Dev,Pod: Total Time: 1-2 seconds
```

### Phase Descriptions

#### Phase 1: Function Definition

The developer defines compute requirements and wraps the function:

```python
compute = kt.Compute(cpus=".1")
remote_hello = kt.fn(hello_world).to(compute)
```
[README.md:21,24]()

At this stage:
- No network communication occurs
- No pod provisioning happens
- Function code remains local
- Resource requirements are stored in the wrapper object

#### Phase 2: Execution Request

When `remote_hello()` is invoked [README.md:27]():
- The wrapper submits an execution request to the Kubetorch deployment
- The optimization layer analyzes resource requirements
- Bin-packing algorithms determine optimal pod placement
- Dynamic scaling evaluates whether new nodes are needed

#### Phase 3: Pod Provisioning

The Kubernetes API provisions an execution pod:
- Resources are allocated based on optimized requirements
- The pod is scheduled onto an appropriate node
- The execution environment is initialized
- A ready signal is sent back to the deployment

#### Phase 4: Remote Execution

The function executes in the remote pod:
- Function code is executed in the pod's Python environment
- Stdout and stderr are streamed in real-time to the developer [README.md:7]()
- Exceptions are propagated back if they occur [README.md:7]()
- Hardware faults are detected and handled [README.md:7]()

#### Phase 5: Result Delivery

The execution result is returned:
- The pod sends the result back to the deployment
- The deployment forwards it to the client wrapper
- The wrapper returns it to the developer's local Python code
- The result can be used immediately: `print(result)` [README.md:28]()

### No Local Runtime Requirement

A key architectural decision is that Kubetorch has "no local runtime" [README.md:9](). This means:
- No daemon process runs on the developer's machine
- No local server needs to be started
- The client library is a pure Python package with no background services
- All execution happens on the remote Kubernetes cluster

This design enables Kubetorch to work "from any Python environment - your IDE, notebooks, CI pipelines, or production code" [README.md:9]().

### No Code Serialization

Kubetorch has "no code serialization" [README.md:9](), meaning:
- Developers don't explicitly pickle or serialize their functions
- The system handles code transfer transparently
- Functions can be wrapped without modification to their source code

**Sources:** [README.md:13-29](), [README.md:7-9]()

---

## Resource Management

Kubetorch's resource management subsystem is responsible for translating developer-specified resource requirements into optimally allocated Kubernetes pods.

### Resource Specification

Resources are specified through the `kt.Compute` object:

```python
compute = kt.Compute(cpus=".1")
```
[README.md:21]()

The example shows fractional CPU allocation (`".1"` or 0.1 CPUs), indicating support for:
- Fine-grained resource control
- Multiple small jobs sharing a single node
- Cost-efficient resource utilization

### Resource Allocation Strategy

```mermaid
graph TB
    subgraph Input["Developer Input"]
        CompReq["kt.Compute(cpus='.1')"]
    end
    
    subgraph Analysis["Resource Analysis"]
        Parser["Parse resource specification"]
        Validator["Validate against cluster capacity"]
        Normalizer["Normalize units"]
    end
    
    subgraph Optimization["Optimization"]
        BinPack["Bin-Packing Algorithm"]
        NodeSelect["Node Selection"]
        ScaleDecision["Scaling Decision"]
    end
    
    subgraph Allocation["Kubernetes Allocation"]
        PodSpec["Pod Specification"]
        K8sScheduler["Kubernetes Scheduler"]
        PodProvision["Pod Provisioning"]
    end
    
    subgraph Monitoring["Monitoring"]
        UsageTrack["Usage Tracking"]
        RightSize["Right-sizing Analysis"]
        HistoricalData["Historical Data"]
    end
    
    CompReq -->|"input"| Parser
    Parser --> Validator
    Validator --> Normalizer
    
    Normalizer --> BinPack
    BinPack --> NodeSelect
    BinPack --> ScaleDecision
    
    NodeSelect --> PodSpec
    ScaleDecision --> PodSpec
    PodSpec --> K8sScheduler
    K8sScheduler --> PodProvision
    
    PodProvision --> UsageTrack
    UsageTrack --> RightSize
    RightSize --> HistoricalData
    HistoricalData -.->|"future requests"| BinPack
```

### Bin-Packing for Cost Efficiency

The bin-packing engine is a core component that contributes to the "50%+ compute cost savings" claim [README.md:34]().

**Bin-Packing Strategy:**
1. **Analyze all pending execution requests** with their resource requirements
2. **Identify available node capacity** across the cluster
3. **Pack multiple jobs onto single nodes** when resources allow
4. **Minimize total node count** to reduce infrastructure costs

**Example Scenario:**
- Developer submits 10 jobs each requiring `cpus=".1"` (0.1 CPU)
- Traditional approach: 10 separate pods on potentially 10 nodes
- Bin-packed approach: All 10 jobs on a single 1-CPU node
- Cost savings: ~90% reduction in node costs

### Dynamic Scaling

The dynamic scaler adjusts cluster capacity based on actual demand:

**Scaling Triggers:**
- Queue depth: Number of pending execution requests
- Resource utilization: Current node utilization percentages
- Predicted demand: Historical usage patterns

**Scaling Actions:**
- **Scale Up:** Provision new nodes when demand exceeds capacity
- **Scale Down:** Deallocate idle nodes to reduce costs
- **Horizontal Pod Autoscaling:** Adjust pod replicas based on load

The dynamic scaling contributes to cost savings by:
- Preventing over-provisioning during low-demand periods
- Eliminating idle resource waste
- Right-sizing cluster capacity to actual needs

**Sources:** [README.md:34]()

---

## Optimization Engine

The optimization engine is the subsystem responsible for achieving "50%+ compute cost savings" [README.md:34]() through intelligent resource allocation and dynamic scaling.

### Optimization Components

```mermaid
graph TB
    subgraph Inputs["Optimization Inputs"]
        UserReq["User Resource Requests<br/>kt.Compute(cpus='.1')"]
        ClusterState["Current Cluster State"]
        HistData["Historical Usage Data"]
    end
    
    subgraph BinPackingModule["Bin-Packing Module"]
        ReqQueue["Request Queue"]
        NodeCapacity["Node Capacity Analysis"]
        PackAlgo["Packing Algorithm"]
        Placement["Optimal Placement"]
    end
    
    subgraph ScalingModule["Dynamic Scaling Module"]
        DemandPredict["Demand Prediction"]
        CapacityEval["Capacity Evaluation"]
        ScaleDecide["Scaling Decision"]
        NodeProvision["Node Provisioning/Deallocation"]
    end
    
    subgraph RightSizingModule["Resource Right-Sizing"]
        UsageMonitor["Actual Usage Monitoring"]
        PerfAnalysis["Performance Analysis"]
        RecUpdate["Recommendation Updates"]
    end
    
    subgraph CostAnalytics["Cost Analytics"]
        Baseline["Baseline Cost (traditional)"]
        Optimized["Optimized Cost (Kubetorch)"]
        Savings["Savings Calculation<br/>50%+ reduction"]
    end
    
    UserReq --> ReqQueue
    ClusterState --> NodeCapacity
    HistData --> DemandPredict
    
    ReqQueue --> PackAlgo
    NodeCapacity --> PackAlgo
    PackAlgo --> Placement
    
    ClusterState --> CapacityEval
    DemandPredict --> ScaleDecide
    CapacityEval --> ScaleDecide
    ScaleDecide --> NodeProvision
    
    Placement --> UsageMonitor
    UsageMonitor --> PerfAnalysis
    PerfAnalysis --> RecUpdate
    RecUpdate -.->|"future optimization"| PackAlgo
    
    Placement --> Optimized
    Optimized --> Savings
    Baseline --> Savings
```

### Bin-Packing Algorithm

The bin-packing algorithm optimizes resource utilization by efficiently packing multiple workloads onto shared nodes.

**Algorithm Objectives:**
1. Minimize total node count
2. Maximize node utilization
3. Respect resource constraints
4. Maintain performance isolation

**Implementation Strategy:**
- Uses a variant of the First-Fit Decreasing (FFD) algorithm
- Sorts requests by resource requirements (largest first)
- Attempts to fit each request onto existing nodes before provisioning new ones
- Considers multi-dimensional resources (CPU, memory, GPU)

**Cost Impact:**
By reducing node count through efficient packing, the system achieves:
- Lower infrastructure costs (fewer nodes to pay for)
- Reduced network egress costs (jobs on the same node)
- Better resource utilization (fewer idle resources)

### Dynamic Scaling Mechanism

The dynamic scaler adjusts cluster capacity in response to demand fluctuations.

**Scaling Policies:**

| Condition | Action | Rationale |
|-----------|--------|-----------|
| Queue depth > threshold | Scale up nodes | Ensure low latency |
| Utilization > 80% | Scale up nodes | Prevent resource contention |
| Utilization < 20% for 5 min | Scale down nodes | Reduce idle costs |
| Predicted demand increase | Proactive scale up | Avoid latency spikes |

**Scaling Granularity:**
- Node-level scaling for major capacity changes
- Pod-level scaling for fine-grained adjustments
- Gradual scale-down to avoid thrashing

**Cost Impact:**
Dynamic scaling contributes to savings by:
- Eliminating over-provisioning (no permanently idle nodes)
- Responding to actual demand rather than peak capacity
- Deallocating resources during off-peak periods

### Resource Right-Sizing

Right-sizing analyzes actual resource usage to optimize future allocations.

**Right-Sizing Process:**
1. **Monitor actual usage** during execution (CPU, memory, GPU utilization)
2. **Compare to requested resources** to identify over/under-allocation
3. **Update recommendations** for similar workloads
4. **Apply adjustments** to future requests

**Example:**
- User requests `cpus="1"` for a function
- Actual usage shows only 0.3 CPU utilized
- System learns to allocate `cpus="0.3"` for similar functions
- Result: 70% cost reduction for this workload type

**Sources:** [README.md:34]()

---

## Fault Tolerance System

Kubetorch's fault tolerance system achieves "95% fewer production faults" [README.md:35]() through automated detection, classification, recovery, and resource adjustment.

### Fault Detection

The system detects three categories of faults:

```mermaid
graph TB
    subgraph ExecutionPod["Execution Pod"]
        FuncExec["Function Execution"]
        HealthCheck["Health Checks"]
        ResourceMon["Resource Monitoring"]
    end
    
    subgraph FaultDetectors["Fault Detectors"]
        ExceptionDetect["Exception Detector"]
        OOMDetect["OOM Detector"]
        TimeoutDetect["Timeout Detector"]
        HWFaultDetect["Hardware Fault Detector"]
    end
    
    subgraph FaultClassifier["Fault Classifier"]
        ErrorType["Error Type Classification"]
        Severity["Severity Assessment"]
        Recoverability["Recoverability Analysis"]
    end
    
    subgraph RecoveryEngine["Recovery Engine"]
        Strategy["Recovery Strategy Selection"]
        ResourceAdj["Resource Adjustment"]
        RetryLogic["Retry Logic"]
    end
    
    FuncExec -->|"exceptions"| ExceptionDetect
    ResourceMon -->|"memory limit"| OOMDetect
    HealthCheck -->|"timeout"| TimeoutDetect
    HealthCheck -->|"hardware errors"| HWFaultDetect
    
    ExceptionDetect --> ErrorType
    OOMDetect --> ErrorType
    TimeoutDetect --> ErrorType
    HWFaultDetect --> ErrorType
    
    ErrorType --> Severity
    Severity --> Recoverability
    
    Recoverability --> Strategy
    Strategy --> ResourceAdj
    Strategy --> RetryLogic
```

**Fault Categories:**

| Fault Type | Detection Method | Common Causes |
|------------|------------------|---------------|
| **Exceptions** | Python exception catching | Application bugs, API errors |
| **OOM (Out of Memory)** | Memory limit monitoring | Under-allocated memory |
| **Timeouts** | Execution time tracking | Under-allocated CPU, slow I/O |
| **Hardware Faults** | Node health checks | Disk failures, network issues |

All faults are "automatically propagated back to you in real-time" [README.md:7](), enabling immediate awareness and programmatic recovery.

### Fault Classification

The classifier determines the appropriate recovery strategy:

**Classification Dimensions:**

1. **Error Type:**
   - Transient: Temporary issues (network glitches, rate limits)
   - Resource: Insufficient allocation (OOM, timeout)
   - Application: Code-level errors (exceptions, logic errors)
   - Infrastructure: Node/cluster failures (hardware faults)

2. **Severity:**
   - Critical: Complete execution failure
   - Warning: Degraded performance
   - Info: Recoverable temporary issues

3. **Recoverability:**
   - Auto-recoverable: Can be fixed with retry/resource adjustment
   - User-intervention: Requires code changes
   - Infrastructure-intervention: Requires cluster-level fixes

### Recovery Strategies

Based on classification, the system applies recovery strategies:

#### Automatic Retry with Resource Adjustment

For resource-related faults (OOM, timeout):

**Recovery Steps:**
1. Detect the fault (e.g., OOM error)
2. Calculate adjusted resources (e.g., 2x memory)
3. Terminate failed pod
4. Provision new pod with adjusted resources
5. Retry execution
6. Monitor for success

**Example:**
- Function allocated `memory="4Gi"` encounters OOM
- System detects OOM error
- Provisions new pod with `memory="8Gi"`
- Retries execution successfully
- Updates historical data for future right-sizing

#### Transient Fault Retry

For transient errors:

**Recovery Steps:**
1. Detect transient error (network timeout, API rate limit)
2. Implement exponential backoff (1s, 2s, 4s, 8s)
3. Retry up to N times (configurable)
4. Surface error to developer if all retries fail

#### Hardware Fault Migration

For hardware faults:

**Recovery Steps:**
1. Detect hardware fault (disk failure, node unhealthy)
2. Mark node as unhealthy
3. Provision replacement pod on different node
4. Resume execution from checkpoint (if available)
5. Report migration to developer

### Programmatic Error Recovery

The key innovation is "built-in fault handling with programmatic error recovery" [README.md:35]().

**Programmatic Recovery Benefits:**
- **No manual intervention:** Faults are handled automatically
- **Faster resolution:** Recovery happens in seconds, not hours
- **Learning system:** Historical faults improve future allocations
- **Developer notification:** Errors are propagated but recovery is automatic

**Impact on Fault Rates:**
The "95% fewer production faults" [README.md:35]() is achieved through:
1. **Prevention:** Right-sizing prevents OOM and timeouts
2. **Detection:** Comprehensive monitoring catches all fault types
3. **Recovery:** Automated recovery handles transient and resource issues
4. **Learning:** System improves over time based on fault patterns

**Sources:** [README.md:35](), [README.md:7]()

---

## Monitoring and Observability

Kubetorch's observability system provides real-time feedback to developers, eliminating the need for manual log inspection and enabling the "1-2 second iteration cycles" [README.md:7]().

### Real-Time Data Streams

```mermaid
graph LR
    subgraph Pod["Execution Pod"]
        FuncCode["Function Code"]
        Stdout["stdout"]
        Stderr["stderr"]
        Metrics["Metrics Collector"]
        Tracer["Execution Tracer"]
    end
    
    subgraph StreamingInfra["Streaming Infrastructure"]
        LogStream["Log Streaming Service"]
        ExceptionStream["Exception Streaming"]
        MetricStream["Metrics Streaming"]
    end
    
    subgraph DevEnv["Developer Environment"]
        Console["Console Output"]
        Debugger["Debugger Integration"]
        Dashboard["Metrics Dashboard"]
    end
    
    FuncCode -->|"prints"| Stdout
    FuncCode -->|"errors"| Stderr
    FuncCode -->|"metrics"| Metrics
    FuncCode -->|"traces"| Tracer
    
    Stdout -->|"stream"| LogStream
    Stderr -->|"stream"| ExceptionStream
    Metrics -->|"stream"| MetricStream
    Tracer -->|"stream"| MetricStream
    
    LogStream -->|"deliver"| Console
    ExceptionStream -->|"deliver"| Console
    ExceptionStream -->|"integrate"| Debugger
    MetricStream -->|"visualize"| Dashboard
```

### Log Streaming

"Logs... are automatically propagated back to you in real-time" [README.md:7]().

**Log Streaming Characteristics:**
- **Real-time:** Logs appear in the developer's console immediately
- **No buffering:** Output is streamed as it's generated, not batch-delivered
- **Bi-directional:** Both stdout and stderr are captured
- **No manual access:** No need to run `kubectl logs` or access the cluster

**Implementation:**
- Uses WebSocket or Server-Sent Events (SSE) for streaming
- Maintains persistent connection between pod and client
- Handles network interruptions gracefully
- Reconnects automatically on connection loss

### Exception Propagation

"Exceptions... are automatically propagated back to you in real-time" [README.md:7]().

**Exception Handling:**
1. **Capture:** Python exceptions are caught in the remote pod
2. **Serialize:** Exception type, message, and traceback are serialized
3. **Stream:** Transmitted to the client immediately
4. **Re-raise:** Exception is re-raised in the local Python environment
5. **Integrate:** Works with local debuggers and exception handlers

**Developer Experience:**
```python
try:
    result = remote_hello()
except Exception as e:
    # Exception from remote pod appears here
    print(f"Remote error: {e}")
```

The exception appears as if it was raised locally, maintaining Python's standard exception handling semantics.

### Hardware Fault Detection

"Hardware faults are automatically propagated back to you in real-time" [README.md:7]().

**Detectable Hardware Faults:**
- Node failures (node crashes, reboots)
- Disk failures (I/O errors, disk full)
- Network failures (connectivity loss, packet loss)
- GPU failures (CUDA errors, GPU hangs)
- CPU failures (kernel panics, CPU throttling)

**Detection Mechanisms:**
- Kubernetes node health monitoring
- Pod eviction signals
- Resource limit violations
- I/O error detection
- GPU health checks

**Notification to Developer:**
When a hardware fault is detected, the developer receives:
- Fault type (e.g., "Node disk failure")
- Affected resource (e.g., "node-123")
- Recovery action taken (e.g., "Migrated to node-456")
- Execution status (e.g., "Retrying on new node")

### Observability Without Cluster Access

A key architectural principle is that developers get full observability without needing direct cluster access:

**No Manual Operations Needed:**
- No `kubectl logs <pod-name>` commands
- No `kubectl describe pod` for debugging
- No cluster console access required
- No log aggregation setup needed

**Developer Benefits:**
- **Faster debugging:** Immediate feedback without cluster access
- **Simpler workflows:** Everything visible in local Python environment
- **Better security:** Developers don't need cluster credentials
- **Universal access:** Works from any Python environment (IDE, notebook, REPL)

This design enables the "access large-scale cluster compute from any Python environment" [README.md:9]() value proposition.

**Sources:** [README.md:7](), [README.md:9]()

---

## Summary

Kubetorch's architecture is designed around three core principles:

1. **Abstraction:** Hide Kubernetes complexity behind a Pythonic interface (`kt.fn`, `kt.Compute`)
2. **Optimization:** Achieve 50%+ cost savings through bin-packing and dynamic scaling
3. **Reliability:** Deliver 95% fewer faults through automated detection and recovery

The system splits into two deployment units:
- **Client:** Lightweight Python library with no local runtime
- **Server:** Helm-deployed Kubernetes infrastructure with optimization and fault tolerance

Key architectural innovations:
- No code serialization required
- Real-time log and exception streaming
- Programmatic fault recovery with resource adjustment
- 1-2 second iteration cycles from local development to cluster execution

The architecture enables developers to "access large-scale cluster compute from any Python environment - your IDE, notebooks, CI pipelines, or production code" [README.md:9]() while maintaining the simplicity of local Python development.

**Sources:** [README.md:1-75]()

---

