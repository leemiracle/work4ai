<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/docs · page 2 openJiuwen Product Overview · fetched 2026-11-02 -->

# openJiuwen Product Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [en/Product Overview.md](en/Product Overview.md)

</details>



As an open-source AI Agent platform, openJiuwen provides flexible, powerful, and easy-to-use capabilities for AI Agent development and execution [en/Product Overview.md:5-5](). It enables developers to construct AI Agents, orchestrate multi-agent collaboration, and build robust, production-grade agentic systems [en/Product Overview.md:5-5](). 

This parent page summarizes openJiuwen's core product vision, application scenarios, advantages, high-level architecture, and modular ecosystem. Detailed deep-dives are available in the respective child pages.

---

## 2.1 Layered System Architecture

openJiuwen adopts a comprehensive layered architecture designed to cover the complete lifecycle of AI Agents, from development and execution to deployment, operations, and maintenance [en/Product Overview.md:36-38](). The overall system is divided into five core layers: **DeepAgents**, **Agent Studio**, **Agent Framework**, **Agent Distributed Runtime**, and **Agent System Service** [en/Product Overview.md:38-44]().

### Architecture Mapping to Code Entities

The following diagram bridges the natural language architecture concepts to concrete code components and modules in the repository:

```mermaid
graph TD
    subclass1 ["NaturalLanguageLayer"]
    subclass2 ["CodeEntitySpace"]

    subclass1 -->| "DeepAgents Layer" | subclass2
    subclass1 -->| "Agent Framework Layer" | subclass2

    subclass2 --> A["jiuwenswarm"]
    subclass2 --> B["jiuwensymbiosis"]
    subclass2 --> C["deepsearch"]
    subclass2 --> D["agent-core"]
    subclass2 --> E["ReActAgent"]
    subclass2 --> F["WorkflowAgent"]

    A -->|"Implements swarm logic"| D
    B -->|"Implements symbiosis logic"| D
    C -->|"Implements search workflows"| D
    E -->|"Core execution loop"| D
    F -->|"Graph engine workflows"| D
```
*Figure 2.1: Mapping architectural layers to repository code entities.*

For a granular breakdown of the five layers, see [Layered System Architecture](#2.1).

**Sources:**
- `en/Product Overview.md:36-47`

---

## 2.2 Repository / Module Ecosystem

openJiuwen adopts a modular repository design to build the AI Agent development ecosystem layer by layer [en/Product Overview.md:50-50](). Each repository can evolve independently or be combined to handle the complete workflow—from agent applications and skill distribution to visual orchestration and framework execution [en/Product Overview.md:50-50](). Key modules include `jiuwenswarm`, `jiuwensymbiosis`, `deepsearch`, `skillhub`, `agent-studio`, `agent-gateway`, `agent-core`, `agent-core-java`, `agent-memory`, `agent-runtime`, `agent-runtime-java`, and `agent-protocol`.

For detailed descriptions of each module and repository, see [Repository / Module Ecosystem](#2.2).

**Sources:**
- `en/Product Overview.md:48-51`

---

## 2.3 Agent Types and Execution Engine

The platform supports sophisticated agent execution mechanics, notably featuring `ReActAgent` (driven by the Thought→Action→Observation loop) and `WorkflowAgent` [en/Product Overview.md:42-42](). These are powered by a hybrid batch-stream graph engine, robust state management, and comprehensive observability subsystems.

### Agent Execution Flow

```mermaid
graph TD
    subgraph "Execution Engine Space"
    Start([Start]) --> ReAct["ReActAgent.execute()"]
    ReAct --> Thought["Thought Generation"]
    Thought --> Action["Action Invocation"]
    Action --> Observation["Observation Parsing"]
    Observation -->| "Not Finished" | Thought
    Observation -->| "Finished" | End([End])
    end
```
*Figure 2.2: ReActAgent execution loop linking conceptual steps to execution routines.*

For deep technical insights into agent types, execution engines, and graph workflows, see [Agent Types and Execution Engine](#2.3).

**Sources:**
- `en/Product Overview.md:41-43`

---

## 2.4 Application Scenarios and LLM Support

openJiuwen powers diverse use cases across both consumer (ToC) and enterprise (ToB) domains [en/Product Overview.md:7-25](). 

### Overview of Supported Scenarios

| Category | Scenario | Description |
| :--- | :--- | :--- |
| **Consumer (ToC)** | Chat Assistant | Natural language conversational support and user engagement [en/Product Overview.md:15-15]. |
| **Consumer (ToC)** | Text Generation | Automated article writing, copywriting, and press releases [en/Product Overview.md:16-16]. |
| **Consumer (ToC)** | Intelligent Assistant | Task planning, schedule management, and information retrieval [en/Product Overview.md:17-17]. |
| **Enterprise (ToB)** | Financial Industry | Multi-level intent routing, intelligent task allocation, and dynamic scheduling [en/Product Overview.md:23-23]. |
| **Enterprise (ToB)** | Healthcare | Medical record summarisation, imaging screening, and diagnostic support [en/Product Overview.md:24-24]. |

The platform integrates smoothly with leading foundational LLMs such as Pangu, Qwen, and DeepSeek. For full scenario breakdowns and model integration guidelines, see [Application Scenarios and LLM Support](#2.4).

**Sources:**
- `en/Product Overview.md:7-25`

---

