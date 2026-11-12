<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-runtime-java · page 4 Hosting, Lifecycle and Concurrency · fetched 2026-11-02 -->

# Hosting, Lifecycle and Concurrency

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuation.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuation.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedAgentRuntime.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedAgentRuntime.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationCoordinatorState.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationCoordinatorState.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/SerialQueryStreamObserver.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/SerialQueryStreamObserver.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuationTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuationTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedAssemblyTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedAssemblyTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedCallbackContractTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedCallbackContractTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedLifecycleTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedLifecycleTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedPushJourneyTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedPushJourneyTest.java)

</details>



This page provides a high-level overview of how `agent-runtime-java` manages multi-tenant hosted agent runtimes, their lifecycle phases, and the concurrency/admission control mechanisms in place. It serves as a parent page, linking to more detailed child pages for each topic.

## Hosted Multi-Agent Runtimes

The `agent-runtime-java` can host multiple agent instances within a single application. This multi-tenancy is managed by components like `HostedRuntimeAssembler` and `HostedAgentRuntime`. Each hosted agent operates with its own isolated set of resources, including a dedicated `TaskStore` [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedAssemblyTest.java:101-101] and SDK request handler [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedAssemblyTest.java:102-102]. The `HostedRuntimeCatalog` acts as a registry for these active agent runtimes, allowing for dynamic resolution of agent instances via `HostedIngressResolver` [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:118-121] based on incoming requests. Per-agent Redis isolation is achieved through `ScopedRuntimeRedisClient` [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java:68-70], ensuring data separation. Legacy facades are provided for compatibility, but the core assembly process directly uses the specific agent's dependencies.

For details, see [Hosted Multi-Agent Runtimes](#4.1).

### Hosted Runtime Assembly Diagram

```mermaid
graph TD
    A[HostedAgentDefinitions] --> B{HostedRuntimeAssembler.assemble()};
    B --> C{ScopedRuntimeRedisClient};
    C --> D[TaskStore (per-agent)];
    D --> E[MainEventBus (per-agent)];
    E --> F[A2AAgentExecutor (per-agent)];
    F --> G[A2AEnabledServeOrchestrator (per-agent)];
    G --> H[RequestHandler (SDK, per-agent)];
    H --> I[HostedAgentRuntime];
    I --> J[HostedRuntimeCatalog.publish()];
    J --> K[HostedIngressResolver];

    subgraph "Per-Agent Isolated Components"
        D
        E
        F
        G
        H
    end

    subgraph "Shared Components"
        A
        B
        C
        J
        K
    end
```
Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java:67-85]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java:92-130]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:118-121]()
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/hosting/HostedAssemblyTest.java:101-102]()

## Agent Lifecycle Management

The lifecycle of hosted agents is managed through distinct phases: initialization and shutdown. The `HostedLifecycleCoordinator` orchestrates these phases [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:63-99] for all registered agents. During initialization, `AgentHandler` instances are started [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:101-111], and `init hooks` are executed [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:84-86]. The system tracks agent readiness via `DefaultAgentReadiness` [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:92-92]. During shutdown, active streams are cancelled by `ActiveStreamRegistry` [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:130-130], interrupt handlers are invoked, and resources are cleaned up in a controlled manner [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:118-159].

For details, see [Agent Lifecycle Management](#4.2).

### Agent Lifecycle Flow

```mermaid
graph TD
    A[Application Startup] --> B{HostedLifecycleCoordinator.runInitPhase()};
    B --> C[Shared Lifecycles Prepare/Start];
    C --> D[HostedRuntimeAssembler.assemble() for each agent];
    D --> E[AgentLifecycleHooks.onInit()];
    E --> F[Start AgentHandler.start() for each agent];
    F --> G[HostedRuntimeCatalog.publish()];
    G --> H[DefaultAgentReadiness.markAgentLoaded(true)];
    H --> I[Application Running];
    I --> J{HostedLifecycleCoordinator.runShutdownPhase()};
    J --> K[HostedRuntimeCatalog.close()];
    K --> L[DefaultAgentReadiness.markShuttingDown()];
    L --> M[A2ATaskContinuation.shutdown() for each agent];
    M --> N[A2AEnabledServeOrchestrator.stopDispatching() for each agent];
    N --> O[ActiveStreamRegistry.cancelAll() for each agent];
    O --> P[Wait for ActiveStreamRegistry.awaitDrain()];
    P --> Q[AgentLifecycleHooks.onShutdown()];
    Q --> R[Stop AgentHandler.stop() for each agent];
    R --> S[Cleanup HostedRuntimeAssembler resources];
    S --> T[Shared Lifecycles Stop];
    T --> U[HostedResources.close()];
    U --> V[DefaultAgentReadiness.markProcessDown()];
    V --> W[Application Shutdown];
```
Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:63-99]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:101-111]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:118-159]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:130-130]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:92-92]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedLifecycleCoordinator.java:84-86]()

## Concurrency, Thread Pools and Admission

Concurrency within the runtime is managed by dedicated thread pools and admission control mechanisms. `A2AExecutionResources` provides shared executors for various tasks, including agent execution and event processing [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/A2AAutoConfiguration.java:9-9]. `VirtualThreadSupport` can be leveraged for efficient task handling. The `QuerySsePumpExecutor` is responsible for streaming query results. `TaskAdmissionGate` and `TaskAdmissionListener` control the flow of incoming tasks, preventing system overload [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java:117-118]. The `A2ATaskContinuation` component handles retries with exponential backoff for tasks that are temporarily rejected by the admission gate [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuation.java:40-46]. `ActiveTaskQuery` provides insights into currently running tasks.

For details, see [Concurrency, Thread Pools and Admission](#4.3).

### Task Admission and Execution Flow

```mermaid
graph TD
    A[Incoming ServeRequest] --> B{A2AAgentExecutor.execute()};
    B --> C{TaskAdmissionGate.tryAdmit()};
    C -- Admitted --> D[Agent Execution Thread Pool];
    C -- Rejected (Transient) --> E[A2ATaskContinuation.submit()];
    E -- Retries with Backoff --> C;
    C -- Rejected (Persistent) --> F[Error Response];
    D --> G[AgentHandler.serve() / query()];
    G --> H[QuerySsePumpExecutor (for streaming)];
    H --> I[QueryChunk Stream];
    D --> J[TaskAdmissionListener.onAdmitted() / onRejected()];
    J --> K[Metrics / Logging];
    subgraph "Concurrency Control"
        C
        E
        J
    end
    subgraph "Execution Resources"
        D
        H
    end
```
Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/hosting/HostedRuntimeAssembler.java:117-118]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/A2ATaskContinuation.java:40-46]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/A2AAutoConfiguration.java:9-9]()

## Auto-Configuration and Properties

The `agent-runtime-java` leverages Spring Boot's auto-configuration to simplify setup. `A2AAutoConfiguration` and `HostedRuntimeAutoConfiguration` are key auto-configuration classes that define and configure the necessary beans for A2A protocol handling and multi-agent hosting [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:73-76]. Configuration properties are managed through `A2AProperties`, `ServiceProperties`, `QueryProperties`, and `LifecycleProperties`, allowing fine-grained control over various aspects of the runtime, such as push notifications, callback hosts, and shutdown timeouts [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:131-133]. These properties are bound from `application.properties` or `application.yml` files.

For details, see [Auto-Configuration and Properties](#4.4).

Sources:
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:73-76]()
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/autoconfigure/HostedRuntimeAutoConfiguration.java:131-133]()

---

