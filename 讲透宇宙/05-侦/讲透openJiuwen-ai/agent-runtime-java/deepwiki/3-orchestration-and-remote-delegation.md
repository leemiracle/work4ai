<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-runtime-java · page 3 Orchestration and Remote Delegation · fetched 2026-11-02 -->

# Orchestration and Remote Delegation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClient.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClient.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/reset/ResetIngressSupport.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/controller/reset/ResetIngressSupport.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestrator.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestrator.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/DefaultServeOrchestrator.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/DefaultServeOrchestrator.java)
- [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationBatchCoordinator.java](service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationBatchCoordinator.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClientClassLoaderTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClientClassLoaderTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClientStreamingLifecycleTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/controller/a2a/client/A2ARemoteAgentClientStreamingLifecycleTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/it/MultiTurnEchoHandler.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/it/MultiTurnEchoHandler.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestratorTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestratorTest.java)
- [service/agent-service-app/src/test/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationBatchCoordinatorTest.java](service/agent-service-app/src/test/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationBatchCoordinatorTest.java)
- [service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/paths/AgentServicePaths.java](service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/paths/AgentServicePaths.java)
- [service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/spi/ServeOrchestrator.java](service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/spi/ServeOrchestrator.java)

</details>



The orchestration layer acts as the core coordination engine of `agent-runtime-java`, bridging local agent execution with distributed Agent-to-Agent (A2A) protocol delegations. It handles ingress request lifecycles, manages task continuation loops, fans out parallel remote tool invocations, and maps execution states back to the unified `ServeOrchestrator` interface.

For full technical details, refer to the child pages:
- [A2AEnabledServeOrchestrator and Interrupt/Resume](#3.1)
- [Remote Invocation Batch Coordination](#3.2)
- [Remote Agent Client, Catalog and Discovery](#3.3)

Sources: [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestrator.java:32-51](), [service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/spi/ServeOrchestrator.java:10-15]()

---

## 3.1 A2AEnabledServeOrchestrator and Interrupt/Resume

The `A2AEnabledServeOrchestrator` implements `ServeOrchestrator` to provide an interrupt-resume execution loop [service/agent-service-app/src/main/java/com/openjiuwen.service.app.orchestrator.A2AEnabledServeOrchestrator.java:32-52](). When an agent encounter an `a2a_delegate` interrupt, the orchestrator suspends local execution, delegates the batch to remote agents via the batch coordinator, and drives conversation continuation upon receiving responses.

Task-scoped resources managed by `AgentHandler#prepareTask` and `AgentHandler#completeTask` span across multiple iteration loops in this orchestrator, ensuring thread-local and session state consistency across remote roundtrips.

For details, see [A2AEnabledServeOrchestrator and Interrupt/Resume](#3.1).

Sources: [service/agent-service-app/src/main/java/com/openjiuwen.service.app.orchestrator.A2AEnabledServeOrchestrator.java:32-52]()

---

## 3.2 Remote Invocation Batch Coordination

The `RemoteInvocationBatchCoordinator` manages fan-out and fan-in workflows for parallel tool-call batches directed at remote agents [service/agent-service-app/src/main/java/com/openjiuwen.service.app.orchestrator.RemoteInvocationBatchCoordinator.java:50-58](). It coordinates shadow tasks persisted in an A2A `TaskStore`, enforces global concurrency limits via a bounded dispatcher, and utilizes `RemoteInvocationBatchMapper` to translate Core tool payloads into remote agent execution structures.

Completed tool results are aggregated into a single batch resolution structure, feeding back into the orchestrator's resume cycle via a serial stream observer.

For details, see [Remote Invocation Batch Coordination](#3.2).

Sources: [service/agent-service-app/src/main/java/com/openjiuwen.service.app.orchestrator.RemoteInvocationBatchCoordinator.java:50-58]()

---

## 3.3 Remote Agent Client, Catalog and Discovery

The `A2ARemoteAgentClient` serves as the primary implementation of `RemoteAgentCaller`, leveraging the official A2A SDK client builder and JSON-RPC transport layers [service/agent-service-app/src/main/java/com/openjiuwen.service.app.controller.a2a.client.A2ARemoteAgentClient.java:74-91](). It handles outbound retry logic with exponential backoffs, transport mapping, and asynchronous outcome observation.

Discovery and routing are supported by agent card registries, allowing runtime lookup of remote targets, capability gating, and context header propagation across network boundaries.

For details, see [Remote Agent Client, Catalog and Discovery](#3.3).

Sources: [service/agent-service-app/src/main/java/com/openjiuwen.service.app.controller.a2a.client.A2ARemoteAgentClient.java:74-91]()

---

## Orchestration Architecture Overview

The following diagram bridges the natural language conceptual space to the actual code entities involved in orchestration and remote delegation.

```mermaid
graph TD
    sub0["Natural Language Space"] --> |"Inbound Routing"| sub1["Code Entity Space"]
    
    sub "Code Entity Space" {
        SO["ServeOrchestrator"] --> AO["A2AEnabledServeOrchestrator"]
        AO --> BC["RemoteInvocationBatchCoordinator"]
        BC --> RAC["A2ARemoteAgentClient"]
        RAC --> SDK["org.a2aproject.sdk.client.Client"]
    }

    sub "Natural Language Space Description" {
        NL1["Inbound Query Handling"]
        NL2["Interrupt/Resume Loop"]
        NL3["Batch Fan-Out/Fan-In"]
        NL4["JSON-RPC Transport"]
    }
```
Sources: [service/agent-service-spec/src/main/java/com/openjiuwen/service/spec/spi/ServeOrchestrator.java:15-45](), [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/A2AEnabledServeOrchestrator.java:52-150](), [service/agent-service-app/src/main/java/com/openjiuwen/service/app/orchestrator/RemoteInvocationBatchCoordinator.java:59-140](), [service/agent-service-app/src/main/java/com/openjiuwen.service.app.controller.a2a.client.A2ARemoteAgentClient.java:74-95]()

---

