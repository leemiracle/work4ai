<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-runtime-java · page 5 HTTP Query and Probe APIs · fetched 2026-11-02 -->

# HTTP Query and Probe APIs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryIngressSupport.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryIngressSupport.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryMvcController.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryMvcController.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryWebFluxController.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryWebFluxController.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/security/AuthorizationDeniedExceptionHandler.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/security/AuthorizationDeniedExceptionHandler.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/query/QueryMvcControllerTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/query/QueryMvcControllerTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/query/QueryWebFluxControllerTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/query/QueryWebFluxControllerTest.java)

</details>



This page provides a high-level overview of the non-A2A HTTP endpoints exposed by the `agent-runtime-java` application. These APIs are primarily used for direct interaction with agents, managing conversations, and monitoring the application's health and active tasks.

The HTTP surface includes:
*   `/v1/query` and `/v1/query/reactive` for querying agents, supporting both synchronous and Server-Sent Events (SSE) streaming responses.
*   `/v1/reset` for resetting agent conversations.
*   `/health` and `/readiness` for application health and readiness checks.
*   `/active-tasks` for probing currently active agent tasks.

For detailed information on each of these topics, please refer to their respective child pages.

## Query Endpoints (MVC and WebFlux)

The `agent-runtime-java` provides HTTP endpoints for querying agents, supporting both traditional Spring MVC and reactive WebFlux paradigms. These endpoints handle incoming `QueryRequest` objects, validate them, and orchestrate the agent's response, which can be either a single `QueryResponse` or a stream of `QueryChunk` objects via Server-Sent Events (SSE).

The primary entry points are `QueryMvcController` for the MVC stack and `QueryWebFluxController` for the WebFlux stack. Both controllers leverage `QueryIngressSupport` for common logic such as request validation, header binding, and error handling. They also integrate with `HostedIngressResolver` to support multi-tenant agent hosting.

For details on how these controllers process requests, handle streaming, and map `QueryChunk` objects, see [Query Endpoints (MVC and WebFlux)](#5.1).

```mermaid
graph TD
    subgraph "HTTP Query Endpoints"
        Client[("HTTP Client")] -->|POST /v1/query| QueryMvcController
        Client -->|POST /v1/query/reactive| QueryWebFluxController
    end

    QueryMvcController --> QueryIngressSupport
    QueryWebFluxController --> QueryIngressSupport

    QueryIngressSupport -->|Validates & Builds| ServeRequest[("ServeRequest (DTO)")]
    QueryIngressSupport -->|Error Responses| ErrorBody[("JSON Error Body")]

    QueryMvcController -->|Uses| ServeOrchestrator[("ServeOrchestrator (SPI)")]
    QueryWebFluxController -->|Uses| ServeOrchestrator

    ServeOrchestrator -->|query() or streamQuery()| AgentHandler[("AgentHandler (SPI)")]

    AgentHandler -->|Returns| QueryResponse[("QueryResponse (DTO)")]
    AgentHandler -->|Streams| QueryChunk[("QueryChunk (DTO)")]

    QueryMvcController -->|Synchronous| QueryResponse
    QueryMvcController -->|Streaming (SSE)| SseEmitter[("SseEmitter")]
    QueryWebFluxController -->|Synchronous (Mono)| QueryResponse
    QueryWebFluxController -->|Streaming (Flux)| ServerSentEvent[("Flux<ServerSentEvent<String>>")]

    QueryMvcController -- "ConditionalOnWebApplication(SERVLET)"
    QueryWebFluxController -- "ConditionalOnClass(reactor.core.publisher.Flux)"

    style QueryMvcController fill:#ace,stroke:#333,stroke-width:2px
    style QueryWebFluxController fill:#ace,stroke:#333,stroke-width:2px
    style QueryIngressSupport fill:#f9f,stroke:#333,stroke-width:2px
    style ServeOrchestrator fill:#afa,stroke:#333,stroke-width:2px
    style AgentHandler fill:#afa,stroke:#333,stroke-width:2px
    style ServeRequest fill:#fcc,stroke:#333,stroke-width:2px
    style QueryResponse fill:#fcc,stroke:#333,stroke-width:2px
    style QueryChunk fill:#fcc,stroke:#333,stroke-width:2px
```
Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryMvcController.java:52-55]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryMvcController.java:104-140]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryWebFluxController.java:41-44]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryWebFluxController.java:77-124]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryIngressSupport.java:43-57]()

## Reset Conversation and Health Probes

Beyond querying, the application exposes endpoints for managing conversation state and monitoring its operational status. The `ResetConversationMvcController` provides an API to reset the state of a specific conversation, which is crucial for managing agent interactions and resource cleanup. This controller also uses `HostedIngressResolver` for multi-tenant environments.

For operational monitoring, the `HealthController` provides standard Spring Boot health and readiness endpoints. These endpoints indicate the application's ability to serve requests and its current operational state, which is vital for deployment and scaling in containerized environments. Additionally, the `ActiveTaskController` allows for probing currently active agent tasks, providing insights into ongoing operations.

For a deeper dive into conversation reset mechanisms, health checks, readiness states, and active task monitoring, refer to [Reset Conversation and Health Probes](#5.2).

```mermaid
graph TD
    subgraph "Management & Monitoring Endpoints"
        User[("User/System")] -->|POST /v1/reset| ResetConversationMvcController
        MonitoringSystem[("Monitoring System")] -->|GET /health| HealthController
        MonitoringSystem -->|GET /readiness| HealthController
        MonitoringSystem -->|GET /active-tasks| ActiveTaskController
    end

    ResetConversationMvcController -->|Calls| ServeOrchestrator[("ServeOrchestrator.resetConversation()")]
    ResetConversationMvcController -- "ConditionalOnWebApplication(SERVLET)"

    HealthController -->|Checks| AgentReadiness[("AgentReadiness (SPI)")]
    HealthController -->|Checks| InternalComponents[("Internal Components")]

    ActiveTaskController -->|Queries| ActiveTaskRegistry[("ActiveTaskRegistry")]

    style ResetConversationMvcController fill:#ace,stroke:#333,stroke-width:2px
    style HealthController fill:#ace,stroke:#333,stroke-width:2px
    style ActiveTaskController fill:#ace,stroke:#333,stroke-width:2px
    style ServeOrchestrator fill:#afa,stroke:#333,stroke-width:2px
    style AgentReadiness fill:#afa,stroke:#333,stroke-width:2px
```
Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryMvcController.java:101-104]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/query/QueryWebFluxController.java:84-87]()

---

