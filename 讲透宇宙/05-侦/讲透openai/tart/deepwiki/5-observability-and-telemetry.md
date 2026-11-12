<!-- source: DeepWiki mcp.deepwiki.com · repo openai/tart · page 5 Observability and Telemetry · fetched 2026-10-26 -->

# Observability and Telemetry

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.editorconfig](.editorconfig)
- [Sources/tart/Logging/Logger.swift](Sources/tart/Logging/Logger.swift)
- [Sources/tart/Logging/ProgressObserver.swift](Sources/tart/Logging/ProgressObserver.swift)
- [Sources/tart/Logging/URLSessionLogger.swift](Sources/tart/Logging/URLSessionLogger.swift)
- [Sources/tart/OTel.swift](Sources/tart/OTel.swift)
- [integration-tests/go.mod](integration-tests/go.mod)
- [integration-tests/go.sum](integration-tests/go.sum)
- [integration-tests/opentelemetry_test.go](integration-tests/opentelemetry_test.go)

</details>



Tart incorporates several mechanisms for production monitoring, tracing, and progress reporting. This observability stack allows operators to track VM lifecycle events, diagnose network performance issues, and collect distributed traces across CI/CD pipelines.

The system is built around two primary pillars:
1.  **Distributed Tracing:** Leveraging the OpenTelemetry standard to export execution data to remote collectors.
2.  **Progress Reporting:** A localized logging system that provides real-time feedback for long-running operations like image downloads and uploads.

### OpenTelemetry Integration

Tart uses the `OTel` singleton [Sources/tart/OTel.swift:7-11]() to manage distributed tracing. Tracing is not active by default; it is triggered by the presence of a `TRACEPARENT` environment variable [Sources/tart/OTel.swift:19-21](). When active, Tart exports spans using the OTLP HTTP protocol via `OtlpHttpTraceExporter` [Sources/tart/OTel.swift:33-35]().

The instrumentation captures:
*   **Service Metadata:** The service name is set to `"tart"` and the version is pulled from the `CI.version` [Sources/tart/OTel.swift:25-28]().
*   **Context Propagation:** It supports W3C Trace Context, allowing Tart to participate in parent traces initiated by CI systems like Cirrus CI [integration-tests/opentelemetry_test.go:64-67](), [integration-tests/opentelemetry_test.go:96-99]().
*   **Tag Enrichment:** Attributes can be injected via the `CIRRUS_SENTRY_TAGS` environment variable, which are then mapped to span attributes for correlation [integration-tests/opentelemetry_test.go:91-95]().

For details, see [OpenTelemetry Integration](#5.1).

### Logging and Progress Reporting

For user-facing feedback, Tart utilizes a `Logger` protocol [Sources/tart/Logging/Logger.swift:3-6]() that abstracts the difference between interactive terminals and CI environments.

*   **InteractiveConsoleLogger:** Uses ANSI escape codes like `\u{001B}[J` (erase cursor down) to overwrite the last line, providing a clean progress effect [Sources/tart/Logging/Logger.swift:16-32]().
*   **SimpleConsoleLogger:** Used in CI environments (detected via the `CI` environment variable), printing each update on a new line to preserve history [Sources/tart/Logging/Logger.swift:34-46]().

Progress is tracked via the `ProgressObserver`, which uses Key-Value Observation (KVO) on Foundation `Progress` objects [Sources/tart/Logging/ProgressObserver.swift:3-17](). This is specifically used to monitor disk layer transfers. Additionally, `URLSessionLogger` provides specialized hooks for monitoring `URLSession` task progress during OCI registry interactions by implementing `urlSession(_:task:didSendBodyData:totalBytesSent:totalBytesExpectedToSend:)` [Sources/tart/Logging/URLSessionLogger.swift:3-12]().

For details, see [Logging and Progress Reporting](#5.2).

### Telemetry Architecture

The following diagram illustrates how telemetry flows from the Tart CLI to external collectors and the user's terminal.

**Telemetry Data Flow**
```mermaid
graph TD
    subgraph "Tart Process"
        direction TB
        [RootCommand] --> [OTel.shared]
        [OTel.shared] --> [TracerProviderSdk]
        [RegistryClient] --> [ProgressObserver]
        [RegistryClient] --> [URLSessionLogger]
    end

    subgraph "Code Entities"
        [OTel.shared] -- "initializes" --> [OtlpHttpTraceExporter]
        [ProgressObserver] -- "updates" --> [Logger]
        [URLSessionLogger] -- "updates" --> [Logger]
    end

    [OtlpHttpTraceExporter] -- "OTLP/HTTP" --> [Remote_OTEL_Collector]
    [Logger] -- "ANSI/Stdout" --> [User_Terminal]

    style [OTel.shared] stroke-dasharray: 5 5
```
Sources: [Sources/tart/OTel.swift:7-16](), [Sources/tart/Logging/Logger.swift:3-6](), [Sources/tart/Logging/ProgressObserver.swift:13-17](), [Sources/tart/Logging/URLSessionLogger.swift:3-12]()

### Trace Lifecycle and Propagation

Tart's tracing lifecycle is tied to the command execution. The `OTel.flush()` method ensures that all spans are sent before the process exits, including a `Thread.sleep` to work around known issues in the `opentelemetry-swift` SDK regarding asynchronous flushing [Sources/tart/OTel.swift:48-63]().

**Trace Propagation Mapping**
| Concept | Code Entity / Environment Variable | Purpose |
| :--- | :--- | :--- |
| **Trace Activation** | `TRACEPARENT` | Activates tracing and sets parent context [Sources/tart/OTel.swift:19-21]() |
| **Exporter Endpoint** | `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | Configures where to send OTLP data [Sources/tart/OTel.swift:31-33]() |
| **Metadata** | `CI.version` | Sets the `service.version` resource attribute [Sources/tart/OTel.swift:27-28]() |
| **Custom Tags** | `CIRRUS_SENTRY_TAGS` | Propagated as span attributes for filtering [integration-tests/opentelemetry_test.go:91-95]() |

**Code to System Mapping**
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Trace Context"
        "HTTP Progress"
        "Console Output"
    end

    subgraph "Code Entity Space"
        "Trace Context" -.-> [OTel.swift]
        "HTTP Progress" -.-> [URLSessionLogger.swift]
        "Console Output" -.-> [InteractiveConsoleLogger]
    end

    [OTel.swift] -- "uses" --> [OpenTelemetryApi]
    [URLSessionLogger.swift] -- "observes" --> [URLSessionTask]
    [InteractiveConsoleLogger] -- "implements" --> [Logger]
```
Sources: [Sources/tart/OTel.swift:1-15](), [Sources/tart/Logging/URLSessionLogger.swift:3-10](), [Sources/tart/Logging/Logger.swift:16-19]()

Sources:
* [Sources/tart/OTel.swift:1-64]()
* [Sources/tart/Logging/Logger.swift:1-46]()
* [Sources/tart/Logging/ProgressObserver.swift:1-36]()
* [Sources/tart/Logging/URLSessionLogger.swift:1-17]()
* [integration-tests/opentelemetry_test.go:20-99]()

---

