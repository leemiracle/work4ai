<!-- source: DeepWiki mcp.deepwiki.com · repo rohitg00/agentmemory · page 7 Observability & Health · fetched 2026-10-30 -->

# Observability & Health

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/auth.ts](src/auth.ts)
- [src/eval/metrics-store.ts](src/eval/metrics-store.ts)
- [src/functions/dedup.ts](src/functions/dedup.ts)
- [src/health/monitor.ts](src/health/monitor.ts)
- [src/health/thresholds.ts](src/health/thresholds.ts)
- [src/viewer/favicon.svg](src/viewer/favicon.svg)
- [src/viewer/server.ts](src/viewer/server.ts)
- [test/health-thresholds.test.ts](test/health-thresholds.test.ts)
- [test/viewer-security.test.ts](test/viewer-security.test.ts)

</details>



The Observability and Health subsystem provides a multi-layered monitoring stack designed to ensure the reliability of memory operations and the availability of the agentic state. This system encompasses real-time telemetry, automated health snapshots, self-healing thresholds, and a visual dashboard for auditing the memory pipeline.

## System Architecture

The observability stack bridges the gap between low-level system metrics and high-level memory lifecycle events. It operates through three primary mechanisms:

1.  **Telemetry & Metrics**: Active tracking of counters and histograms for pipeline performance, managed by the `MetricsStore` [src/eval/metrics-store.ts:5-10]() and initialized via `initMetrics`.
2.  **Health Monitoring**: Periodic snapshots of system vitals (CPU, Memory, KV latency) and event loop performance [src/health/monitor.ts:21-47]().
3.  **Visual Inspection**: A dedicated viewer server providing a thick-client dashboard for real-time state inspection, typically hosted via `startViewerServer` [src/viewer/server.ts:196-202]().

### Observability Data Flow

The following diagram illustrates how natural language operations (like searching or summarizing) are translated into observable telemetry and health signals within the codebase.

**Diagram: From Operations to Observability**
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        ["'Search for recent refactors'"]
        ["'Summarize this session'"]
    end

    subgraph "Code_Entity_Space"
        direction TB
        [mem::smart-search] --> [HybridSearch]
        [mem::summarize] --> [ResilientProvider]
        
        [HybridSearch] -- "record latency" --> [MetricsStore.record]
        [ResilientProvider] -- "track circuit state" --> [CircuitBreaker]
        [mem::summarize] -- "track quality" --> [MetricsStore.record]
    end

    subgraph "Monitoring_&_Health"
        [MetricsStore.record] --> [KV.metrics]
        [collectHealth] -- "probe" --> [KV.health]
        [KV.health] --> [HealthSnapshot]
        [evaluateHealth] -- "status" --> [HealthSnapshot]
    end

    [HealthSnapshot] -- "broadcast" --> [mem-live_WebSocket]
    [mem-live_WebSocket] --> [Viewer_Dashboard]
```
**Sources:** [src/health/monitor.ts:87-93](), [src/eval/metrics-store.ts:11-47](), [src/health/thresholds.ts:23-81]()

---

## Health Monitoring & Self-Healing

The health system utilizes a tri-state model (`healthy`, `degraded`, `critical`) to evaluate the system's ability to process memories [src/health/thresholds.ts:23-26](). This evaluation is performed by the `registerHealthMonitor` function, which runs every 30 seconds [src/health/monitor.ts:97-99]().

### Health Snapshot Components
A `HealthSnapshot` aggregates data from multiple sources to provide a unified view of system integrity:
*   **Process Vitals**: CPU usage percentage and memory heap/RSS distribution [src/health/monitor.ts:22-33]().
*   **Memory Severity**: Evaluation logic handles edge cases where heap is tight but RSS is below the floor (`memoryRssFloorBytes`, default 512MB), avoiding false "critical" alerts for small processes [src/health/thresholds.ts:62-77]().
*   **Event Loop Lag**: Measured via `setImmediate` to detect blocking operations [src/health/monitor.ts:35-37]().
*   **KV Connectivity**: A periodic probe that performs a write/read cycle on the `KV.health` namespace to measure storage latency [src/health/monitor.ts:49-64]().

For a deep dive into the health evaluation logic and threshold configurations, see **[Telemetry, Metrics & Health Monitoring](#7.1)**.

---

## Telemetry & Metrics

The system uses the `MetricsStore` to track internal performance and quality. Metrics are persisted to the KV store under the `KV.metrics` namespace [src/eval/metrics-store.ts:46](). 

| Metric Field | Code Identifier | Purpose |
| :--- | :--- | :--- |
| `avgLatencyMs` | `FunctionMetrics.avgLatencyMs` | Moving average of function execution time [src/eval/metrics-store.ts:31]() |
| `avgQualityScore` | `FunctionMetrics.avgQualityScore` | Average LLM output quality (0.0-1.0) [src/eval/metrics-store.ts:39-41]() |
| `totalCalls` | `FunctionMetrics.totalCalls` | Cumulative count of function invocations [src/eval/metrics-store.ts:30]() |
| `failureCount` | `FunctionMetrics.failureCount` | Total failed executions [src/eval/metrics-store.ts:35]() |

For details on how these metrics are exported and the specific counters used in OpenTelemetry, see **[Telemetry, Metrics & Health Monitoring](#7.1)**.

---

## Visual Dashboard (The Viewer)

The viewer server creates a proxy that serves a specialized "thick-client" dashboard. It implements strict security measures including a Host header allowlist to prevent DNS rebinding [src/viewer/server.ts:43-51]() and timing-safe Bearer token validation for inbound requests [src/viewer/server.ts:122-130]().

**Diagram: Viewer Architecture & Code Links**
```mermaid
graph LR
    subgraph "Browser_Dashboard"
        [index.html]
    end

    subgraph "Viewer_Server_Port_3113"
        [startViewerServer]
        [renderViewerDocument]
        [requireInboundBearer]
    end

    subgraph "Core_API_&_State"
        [REST_API_Port_3111]
        [StateKV]
        [DedupMap]
    end

    [index.html] -- "GET /" --> [startViewerServer]
    [startViewerServer] -- "Load Template" --> [renderViewerDocument]
    [index.html] -- "API Proxy + Bearer" --> [requireInboundBearer]
    [requireInboundBearer] -- "timingSafeCompare" --> [startViewerServer]
    [startViewerServer] -- "Forward" --> [REST_API_Port_3111]
    [REST_API_Port_3111] -- "Query" --> [StateKV]
    [REST_API_Port_3111] -- "Check Duplicates" --> [DedupMap]
```
**Sources:** [src/viewer/server.ts:196-202](), [src/viewer/server.ts:122-130](), [src/functions/dedup.ts:11-41](), [src/eval/metrics-store.ts:49-54]()

### Key Dashboard Features
*   **Audit Log**: Real-time stream of operations. The viewer shell is rendered via `renderViewerDocument` [src/viewer/server.ts:10]().
*   **Health Status**: Visual display of the latest `HealthSnapshot` retrieved via `getLatestHealth` [src/health/monitor.ts:107-111]().
*   **Deduplication Stats**: Visibility into the `DedupMap` size and SHA-256 hash collisions [src/functions/dedup.ts:54-57]().
*   **Security Hardening**: CSP with nonces for scripts and strict `img-src 'self'` policies [src/auth.ts:16-30](), [test/viewer-security.test.ts:12-23]().

For implementation details and WebSocket streaming specifications, see **[Web Viewer & Dashboard](#7.2)**.

---
**Sources:**
*   `src/health/monitor.ts`: Implementation of health snapshot collection and periodic monitoring.
*   `src/health/thresholds.ts`: Tri-state health evaluation logic and threshold defaults.
*   `src/eval/metrics-store.ts`: Persistence and calculation of function performance metrics.
*   `src/viewer/server.ts`: Viewer server implementation, proxy logic, and security allowlists.
*   `src/functions/dedup.ts`: Deduplication tracking and SHA-256 hashing logic.
*   `src/auth.ts`: Security primitives for the viewer, including CSP and nonces.
*   `test/viewer-security.test.ts`: Verification of CSP and DNS rebinding protections.

---

