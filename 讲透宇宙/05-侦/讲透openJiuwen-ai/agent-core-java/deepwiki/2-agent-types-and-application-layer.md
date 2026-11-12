<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-core-java · page 2 Agent Types and Application Layer · fetched 2026-11-02 -->

# Agent Types and Application Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java](src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java)
- [src/main/java/com/openjiuwen/core/application/llm/LlmEventHandler.java](src/main/java/com/openjiuwen/core/application/llm/LlmEventHandler.java)
- [src/main/java/com/openjiuwen/core/application/llm/TaskInterruptionState.java](src/main/java/com/openjiuwen/core/application/llm/TaskInterruptionState.java)
- [src/main/java/com/openjiuwen/core/application/schema/AgentMemoryConfig.java](src/main/java/com/openjiuwen/core/application/schema/AgentMemoryConfig.java)
- [src/main/java/com/openjiuwen/core/application/schema/DefaultResponse.java](src/main/java/com/openjiuwen/core/application/schema/DefaultResponse.java)
- [src/main/java/com/openjiuwen/core/application/schema/LlmAgentConfig.java](src/main/java/com/openjiuwen/core/application/schema/LlmAgentConfig.java)
- [src/main/java/com/openjiuwen/core/application/schema/PluginSchema.java](src/main/java/com/openjiuwen/core/application/schema/PluginSchema.java)
- [src/main/java/com/openjiuwen/core/application/schema/WorkflowAgentConfig.java](src/main/java/com/openjiuwen/core/application/schema/WorkflowAgentConfig.java)
- [src/main/java/com/openjiuwen/core/application/schema/WorkflowSchema.java](src/main/java/com/openjiuwen/core/application/schema/WorkflowSchema.java)
- [src/main/java/com/openjiuwen/core/application/workflow/WorkflowAgent.java](src/main/java/com/openjiuwen/core/application/workflow/WorkflowAgent.java)
- [src/main/java/com/openjiuwen/core/application/workflow/WorkflowEventHandler.java](src/main/java/com/openjiuwen/core/application/workflow/WorkflowEventHandler.java)
- [src/main/java/com/openjiuwen/core/common/exception/StatusCode.java](src/main/java/com/openjiuwen/core/common/exception/StatusCode.java)
- [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java](src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java)
- [src/main/java/com/openjiuwen/core/singleagent/skills/SkillUtil.java](src/main/java/com/openjiuwen/core/singleagent/skills/SkillUtil.java)

</details>



This page provides a high-level overview of the different agent architectures supported by the `agent-core-java` framework. The framework categorizes agents into two primary paradigms: autonomous reasoning agents based on the **ReAct** (Reasoning + Action) pattern and structured agents based on **Workflows**. These implementations reside primarily in the `com.openjiuwen.core.application` and `com.openjiuwen.core.singleagent` packages.

## Core Agent Paradigms

The framework supports three main types of agents, each suited for different levels of autonomy and structure:

| Agent Type | Class | Description |
| :--- | :--- | :--- |
| **ReAct Agent** | `ReActAgent` | An autonomous agent that uses a reasoning loop to decide which tools to call until a goal is reached. |
| **Workflow Agent** | `WorkflowAgent` | A structured agent that executes predefined Pregel graphs, using intent detection to route user requests. |
| **LLM Agent** | `LlmAgent` | A facade for legacy compatibility that combines ReAct-style reasoning with managed application-layer features. |

### From Natural Language to Agent Entities
The following diagram illustrates how user intent and configuration files map to specific code entities within the application layer.

**Intent Mapping to Code Entities**
```mermaid
graph TD
    User["User Natural Language Input"] -- "Handled by" --> Controller["EventHandler (e.g., WorkflowEventHandler)"]
    
    subgraph "Application Layer Space"
        Controller -- "Intent Detection" --> Intent["WorkflowIntent"]
        Intent -- "Triggers" --> WAgent["WorkflowAgent"]
        WAgent -- "Uses" --> WSchema["WorkflowSchema"]
    end

    subgraph "Single Agent Space"
        RAgent["ReActAgent"] -- "Configured by" --> ACard["AgentCard"]
        RAgent -- "Reasoning" --> LLM["Model (LLM Client)"]
        RAgent -- "Execution" --> AMgr["AbilityManager"]
    end

    Controller -.-> [src/main/java/com/openjiuwen/core/application/workflow/WorkflowEventHandler.java:65-65]()
    WAgent -.-> [src/main/java/com/openjiuwen/core/application/workflow/WorkflowAgent.java:46-46]()
    RAgent -.-> [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81-81]()
    ACard -.-> [src/main/java/com/openjiuwen/core/singleagent/schema/AgentCard.java:1-1]()
```
**Sources:** [src/main/java/com/openjiuwen/core/application/workflow/WorkflowEventHandler.java:65-86](), [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81-112]()

---

## ReAct Agents
The `ReActAgent` is the primary implementation of the "Reasoning and Acting" paradigm [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81](). It operates by maintaining a `ContextEngine` to manage conversation history and a `SystemPromptBuilder` to construct complex instructions for the LLM [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:97-99]().

Key features include:
*   **Skill Discovery:** Dynamically loads tools and workflows via the `AbilityManager` [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:111]().
*   **AgentRails:** Provides lifecycle hooks to intercept and validate agent inputs and outputs [src/main/java/com/openjiuwen/core/singleagent/rail/Rails.java:1-1]().
*   **Tool Interruption:** Supports Human-in-the-loop (HITL) via `ToolInterruptHandler` [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:110]().

For a deep dive into the reasoning loop and configuration, see **[ReActAgent](#2.1)**.

**Sources:** [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81-151]()

---

## Workflow and LLM Agents
`WorkflowAgent` and `LlmAgent` represent the application-layer abstractions designed for complex business logic and legacy system integration.

### WorkflowAgent
Instead of a free-form reasoning loop, the `WorkflowAgent` relies on a `WorkflowEventHandler` to detect user intent and execute specific graphs [src/main/java/com/openjiuwen/core/application/workflow/WorkflowEventHandler.java:65-80](). It is highly structured and uses `WorkflowSchema` to define entry and exit points [src/main/java/com/openjiuwen/core/application/schema/WorkflowAgentConfig.java:62-69]().

### LlmAgent
The `LlmAgent` serves as a backward-compatible facade [src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java:47](). It uses an `LlmEventHandler` to manage a ReAct-style flow while benefiting from application-layer features like `LongTermMemory` and unified `AbilityManager` synchronization [src/main/java/com/openjiuwen/core/application/llm/LlmEventHandler.java:75-95]().

For details on intent detection and task resumption, see **[WorkflowAgent](#2.2)**.

**Sources:** [src/main/java/com/openjiuwen/core/application/workflow/WorkflowAgent.java:46-59](), [src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java:47-66]()

---

## Multi-Agent Systems
The framework allows individual agents to be composed into teams. In this mode, agents can act as tools for other agents (`AgentAsTool`) or communicate through a hierarchical structure managed by a `BaseTeam` runtime.

**Agent Communication Flow**
```mermaid
graph LR
    subgraph "Team Runtime"
        Leader["CommunicableAgent (Leader)"]
        WorkerA["ReActAgent (Worker A)"]
        WorkerB["WorkflowAgent (Worker B)"]
    end

    Leader -- "Handoff / Tool Call" --> WorkerA
    Leader -- "Delegation" --> WorkerB
    WorkerA -- "Response" --> Leader
    WorkerB -- "Status Update" --> Leader

    Leader -.-> [src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java:137-149]()
    WorkerA -.-> [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81-81]()
```

For handoff patterns and the A2A (Agent-to-Agent) protocol, see **[Multi-Agent Systems](#2.3)**.

**Sources:** [src/main/java/com/openjiuwen/core/application/llm/LlmAgent.java:137-149](), [src/main/java/com/openjiuwen/core/singleagent/agents/ReActAgent.java:81-81]()

---

