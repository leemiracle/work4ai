<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · page 11 Examples and Patterns · fetched 2026-11-09 -->

# Examples and Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookbook/00_quickstart/README.md](cookbook/00_quickstart/README.md)
- [cookbook/00_quickstart/TEST_LOG.md](cookbook/00_quickstart/TEST_LOG.md)
- [cookbook/00_quickstart/agent_search_over_knowledge.py](cookbook/00_quickstart/agent_search_over_knowledge.py)
- [cookbook/00_quickstart/agent_with_guardrails.py](cookbook/00_quickstart/agent_with_guardrails.py)
- [cookbook/00_quickstart/agent_with_memory.py](cookbook/00_quickstart/agent_with_memory.py)
- [cookbook/00_quickstart/agent_with_state_management.py](cookbook/00_quickstart/agent_with_state_management.py)
- [cookbook/00_quickstart/agent_with_storage.py](cookbook/00_quickstart/agent_with_storage.py)
- [cookbook/00_quickstart/agent_with_structured_output.py](cookbook/00_quickstart/agent_with_structured_output.py)
- [cookbook/00_quickstart/agent_with_tools.py](cookbook/00_quickstart/agent_with_tools.py)
- [cookbook/00_quickstart/agent_with_typed_input_output.py](cookbook/00_quickstart/agent_with_typed_input_output.py)

</details>



This page provides high-level overviews of concrete cookbook examples and architectural patterns for building with Agno. It bridges the gap between conceptual framework components and production-ready implementations by referencing the `cookbook/` directory.

For detailed, step-by-step guides, refer to the child pages linked in each section.

---

## 11.1. Basic Agent Examples

Basic patterns focus on single-agent capabilities including live tool usage (such as Yahoo Finance), structured data extraction with Pydantic (`output_schema`), persistent conversation history (`db`), user-level preferences (`memory_manager`), runtime state management (`session_state`), guardrails (`pre_hooks`), and multimodal inputs. These examples demonstrate the core `Agent` class and its primary configuration parameters.

For details, see [Basic Agent Examples](#11.1).

**Sources:** [cookbook/00_quickstart/README.md:1-68]()

---

## 11.2. Team and Collaboration Examples

Multi-agent patterns demonstrate how to coordinate specialized agents to solve complex tasks. This involves shared context, asynchronous execution flows, delegation logic, and collaborative reasoning patterns from `cookbook/03_teams`.

### Natural Language Space to Code Entity Space: Team Coordination
The following diagram bridges natural language concepts (such as user requests and specialized expert roles) to concrete Agno code entities like `Team`, `Agent`, and specific tool classes.

```mermaid
graph TD
    UserRequest["User Request: "Analyze Market Position""] --> TeamEntity["Team(name=\"analyst_team\")"]
    TeamEntity --> Leader["Lead Coordinator Agent"]
    Leader --> BullAgent["Agent(name=\"bull_agent\")"]
    Leader --> BearAgent["Agent(name=\"bear_agent\")"]
    BullAgent --> ToolInst1["YFinanceTools()"]
    BearAgent --> ToolInst2["YFinanceTools()"]
    BullAgent -- "Bull Case RunOutput" --> TeamEntity
    BearAgent -- "Bear Case RunOutput" --> TeamEntity
    TeamEntity --> FinalSynthesis["Synthesized RunOutput"]
```
Sources: [cookbook/00_quickstart/README.md:76-82]()

For details, see [Team and Collaboration Examples](#11.2).

**Sources:** [cookbook/00_quickstart/README.md:76-82]()

---

## 11.3. Workflow Orchestration Examples

Workflows are used for predictable, multi-step processes where the order of execution, loops, conditional branching, and data flow must be strictly controlled, as demonstrated in `cookbook/04_workflows`.

- **Sequential Pipelines:** Sequentially execute steps using container types like `Steps` and `Step` [cookbook/00_quickstart/README.md:81-82]().
- **Human-in-the-Loop (HITL):** Requiring user confirmation via approval gates before executing sensitive tasks [cookbook/00_quickstart/README.md:74]().
- **State Propagation:** Managing progress through discrete steps while passing `RunContext` and session state between them [cookbook/00_quickstart/agent_with_state_management.py:40-60]().

For details, see [Workflow Orchestration Examples](#11.3).

**Sources:** [cookbook/00_quickstart/README.md:79-82]()

---

## 11.4. Model-Specific Examples

Agno is model-agnostic and provides deep integrations for provider-specific features across major LLM vendors under `cookbook/90_models`, including Claude thinking modes and skills, Gemini grounding, OpenAI reasoning models, and DeepSeek thinking capabilities.

For details, see [Model-Specific Examples](#11.4).

**Sources:** [cookbook/00_quickstart/README.md:140-156]()

---

## 11.5. Knowledge and RAG Examples

Retrieval-Augmented Generation (RAG) patterns allow agents to search through large document sets, leveraging the `Knowledge` class, vector database integrations (such as `ChromaDb`), hybrid search strategies (`SearchType.hybrid`), chunking options, and remote content loaders from `cookbook/07_knowledge`.

- **Hybrid Search:** Combining vector similarity with keyword search using `SearchType.hybrid` and embedders like `GeminiEmbedder` [cookbook/00_quickstart/agent_search_over_knowledge.py:35-54]().
- **Agentic Retrieval:** Allowing the agent to decide when to search the knowledge base using `search_knowledge=True` [cookbook/00_quickstart/agent_search_over_knowledge.py:87-95]().

For details, see [Knowledge and RAG Examples](#11.5).

**Sources:** [cookbook/00_quickstart/agent_search_over_knowledge.py:1-54]()

---

## 11.6. AgentOS Deployment Examples

`AgentOS` provides the runtime to serve agents, teams, and workflows as production-grade APIs with custom endpoints, authentication, WebSocket streaming, and lifespan management.

### Natural Language Space to Code Entity Space: AgentOS Architecture
This diagram maps abstract deployment concepts to the actual codebase classes and initialization files used in production setups like `cookbook/00_quickstart/run.py`.

```mermaid
graph TD
    ClientApp["Client UI / os.agno.com"] --> FastAPIApp["FastAPI app (app = agent_os.get_app())"]
    FastAPIApp --> OSInstance["AgentOS(name=\"Quickstart AgentOS\", agents=_agents, db=agent_db)"]
    OSInstance --> LifespanFn["@asynccontextmanager lifespan(app)"]
    LifespanFn --> RegAgents["Registered Agents List [_agents]"]
    RegAgents --> AgentKnowledge["Agent(name=\"Agent with Knowledge\")"]
    RegAgents --> AgentTools["Agent(name=\"Agent with Tools\")"]
    OSInstance --> DBBackend["SqliteDb / agent_db"]
```
Sources: [cookbook/00_quickstart/README.md:85-88]()

For details, see [AgentOS Deployment Examples](#11.6).

**Sources:** [cookbook/00_quickstart/README.md:83-88]()

---

## 11.7. Learning Machine Examples

The `LearningMachine` system enables agents to learn from every interaction through coordinated learning stores, user profile extraction, persistent memory, session context, and the Curator from `cookbook/08_learning`.

For details, see [Learning Machine Examples](#11.7).

**Sources:** [cookbook/00_quickstart/README.md:67]()

---

## 11.8. Data Labeling Examples

The data labeling cookbook covers automated text, image, audio, and video classification, structured extraction, pairwise preference evaluation, rejection sampling, inter-annotator agreement calculation, safety labeling, and scale-out evaluation pipelines.

For details, see [Data Labeling Examples](#11.8).

**Sources:** [cookbook/00_quickstart/TEST_LOG.md:1-25]()

---

