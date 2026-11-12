<!-- source: DeepWiki mcp.deepwiki.com · repo crewAIInc/crewAI · page 12 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/edge/ar/concepts/agents.mdx](docs/edge/ar/concepts/agents.mdx)
- [docs/edge/ar/concepts/flows.mdx](docs/edge/ar/concepts/flows.mdx)
- [docs/edge/ar/concepts/llms.mdx](docs/edge/ar/concepts/llms.mdx)
- [docs/edge/ar/concepts/memory.mdx](docs/edge/ar/concepts/memory.mdx)
- [docs/edge/ar/concepts/tools.mdx](docs/edge/ar/concepts/tools.mdx)

</details>



This page provides definitions for codebase-specific terms, jargon, and domain concepts used throughout the CrewAI framework. It serves as a technical reference for onboarding engineers to understand how natural language concepts map to specific code entities.

## Core Orchestration Terms

### Crew
The primary container for orchestrating role-playing autonomous AI agents. A `Crew` represents a collaborative group that works together to achieve a set of tasks using a specific process (sequential or hierarchical) [docs/edge/ar/concepts/agents.mdx:10-17](). It manages global configurations like `max_rpm`, `memory`, and `manager_llm` [docs/edge/ar/concepts/agents.mdx:40-69]().

### Flow
The enterprise-grade, event-driven architecture for building multi-agent systems. Unlike the autonomous nature of Crews, `Flows` provide granular control through state management and decorators like `@start`, `@listen`, and `@router` [docs/edge/ar/concepts/flows.mdx:10-13](). Flows are designed for production-ready state persistence and complex logic branching [docs/edge/ar/concepts/flows.mdx:18-20]().

### Agent
An autonomous unit programmed to perform tasks, make decisions, and communicate with other agents. Configured with a `role`, `goal`, and `backstory` to shape its behavior [docs/edge/ar/concepts/agents.mdx:10-17](). Agents can be assigned specific `tools`, `knowledge_sources`, and custom `llm` configurations [docs/edge/ar/concepts/agents.mdx:40-69]() [docs/edge/ar/concepts/agents.mdx:40-69]().

### Task
A specific assignment to be completed by an agent. Tasks define the `description`, `expected_output`, and can include `guardrails` for validation [docs/edge/ar/concepts/tools.mdx:92-95](). They can be executed synchronously or asynchronously.

### Process
The strategy used by a `Crew` to execute tasks.
*   **Sequential**: Tasks are executed one after another in the order they are defined.
*   **Hierarchical**: Tasks are assigned to agents based on roles, often managed by a `manager_llm` or `manager_agent`.

## Technical Concepts & Code Entities

### Knowledge System
A system that allows agents to access external information sources during task execution. It supports various formats including `StringKnowledgeSource`, `TextFileKnowledgeSource`, `PDFKnowledgeSource`, `CSVKnowledgeSource`, and `JSONKnowledgeSource`. It uses an internal RAG client abstraction for vector stores like `ChromaDB` or `Qdrant`.

### Memory (Unified)
A unified system (`Memory` class) that handles short-term, long-term, and entity memory. It uses an LLM to infer scope and importance, storing data in vector databases [docs/edge/ar/concepts/memory.mdx:10-12](). It supports hierarchical scopes similar to a filesystem (e.g., `/project/alpha`) [docs/edge/ar/concepts/memory.mdx:161-180]().

### LLM Abstraction
The interface for interacting with Large Language Models. CrewAI uses a unified `LLM` class that routes to providers like OpenAI, Anthropic, Google (Gemini), Azure, and AWS Bedrock [docs/edge/ar/concepts/llms.mdx:10-11](). It supports parameters like `temperature`, `max_tokens`, and `response_format` [docs/edge/ar/concepts/llms.mdx:82-93]().

### Tool
A callable function or skill that an agent can use to perform actions, such as `SerperDevTool` for search or `FileReadTool` for disk operations [docs/edge/ar/concepts/tools.mdx:57-62](). Tools are distinct from Skills; tools provide actions, while skills provide instructions [docs/edge/ar/concepts/tools.mdx:13-15]().

### Checkpointing
A feature that saves a snapshot of the execution state (configuration, memory, task progress) so that Crews or Flows can resume after failure or be forked into new branches. Supported providers include `JsonProvider` and `SqliteProvider`.

## Mapping: Natural Language to Code Space

The following diagrams illustrate how high-level concepts map to specific classes and files within the repository.

### Diagram 1: Crew Execution Hierarchy
This diagram shows the relationship between the conceptual "Crew" and the actual code entities that manage execution.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        ["The Team (Crew)"]
        ["The Assignment (Task)"]
        ["The Worker (Agent)"]
    end

    subgraph "CodeEntitySpace"
        ["CrewClass (crewai.Crew)"]
        ["TaskClass (crewai.Task)"]
        ["AgentClass (crewai.Agent)"]
        ["ProcessEnum (crewai.Process)"]
        ["CheckpointConfig (crewai.state.CheckpointConfig)"]
        
        ["CrewClass"] -->|executes| ["ProcessEnum"]
        ["CrewClass"] -->|contains| ["TaskClass"]
        ["TaskClass"] -->|assigned_to| ["AgentClass"]
        ["CrewClass"] -->|persists_via| ["CheckpointConfig"]
    end
```
**Sources:** [docs/edge/ar/concepts/agents.mdx:10-17](), [docs/edge/ar/concepts/tools.mdx:92-95](), [docs/edge/ar/concepts/agents.mdx:40-44]().

### Diagram 2: Flow Event Topology
This diagram bridges the concept of "Workflow Steps" to the event-driven decorators in the `Flow` system.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        ["Starting Point"]
        ["Wait for Step 1"]
        ["Conditional Routing"]
        ["State Data"]
    end

    subgraph "CodeEntitySpace"
        ["@start (crewai.flow.start)"]
        ["@listen (crewai.flow.listen)"]
        ["@router (crewai.flow.router)"]
        ["BaseModel (pydantic.BaseModel)"]
        
        ["Starting Point"] --> ["@start"]
        ["Wait for Step 1"] --> ["@listen"]
        ["Conditional Routing"] --> ["@router"]
        ["State Data"] --> ["BaseModel"]
    end
```
**Sources:** [docs/edge/ar/concepts/flows.mdx:100-112](), [docs/edge/ar/concepts/flows.mdx:185-190](), [docs/edge/ar/concepts/flows.mdx:188-194]().

## Summary Table of Key Terms

| Term | Code Entity | Definition |
| :--- | :--- | :--- |
| **AMP** | N/A | Agent Management Platform - the enterprise suite for managed deployment, tracing, and security. |
| **RAG** | `crewai.rag` | Retrieval-Augmented Generation infrastructure used in Knowledge and Memory. |
| **Skill** | `SKILL.md` | Filesystem-based instructions and domain expertise injected into agents [docs/edge/ar/concepts/tools.mdx:13-15](). |
| **State** | `Flow.state` | A thread-safe dictionary or Pydantic model that persists data across Flow steps [docs/edge/ar/concepts/flows.mdx:55-55](), [docs/edge/ar/concepts/flows.mdx:74-74](). |
| **Kickoff** | `.kickoff()` | The primary method used to start the execution of a `Crew` or a `Flow` [docs/edge/ar/concepts/flows.mdx:81-81](), [docs/edge/ar/concepts/tools.mdx:114-114](). |
| **Guardrail** | `Task.guardrail` | A callable function used to validate or sanitize task outputs before proceeding. |
| **A2A** | N/A | Agent-to-Agent delegation protocol for remote collaboration. |
| **Telemetry** | N/A | Usage tracking system that can be configured via `OTEL_SDK_DISABLED`.

**Sources:** [docs/edge/ar/concepts/tools.mdx:13-15](), [docs/edge/ar/concepts/flows.mdx:55-55](), [docs/edge/ar/concepts/flows.mdx:74-74](), [docs/edge/ar/concepts/flows.mdx:81-81](), [docs/edge/ar/concepts/tools.mdx:114-114]().