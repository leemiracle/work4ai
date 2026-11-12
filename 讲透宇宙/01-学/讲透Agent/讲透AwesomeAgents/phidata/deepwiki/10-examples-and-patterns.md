<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · page 10 Examples and Patterns · fetched 2026-10-26 -->

# Examples and Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookbook/01_demo/README.md](cookbook/01_demo/README.md)
- [cookbook/01_demo/TEST_LOG.md](cookbook/01_demo/TEST_LOG.md)
- [cookbook/01_demo/config.yaml](cookbook/01_demo/config.yaml)
- [cookbook/01_demo/run.py](cookbook/01_demo/run.py)
- [cookbook/03_teams/02_modes/broadcast/04_structured_debate.py](cookbook/03_teams/02_modes/broadcast/04_structured_debate.py)
- [cookbook/05_agent_os/16_agui/openui/README.md](cookbook/05_agent_os/16_agui/openui/README.md)
- [cookbook/07_knowledge/01_getting_started/README.md](cookbook/07_knowledge/01_getting_started/README.md)
- [cookbook/07_knowledge/README.md](cookbook/07_knowledge/README.md)
- [cookbook/10_reasoning/README.md](cookbook/10_reasoning/README.md)
- [cookbook/90_models/azure/claude/README.md](cookbook/90_models/azure/claude/README.md)
- [cookbook/90_models/cohere/retry.py](cookbook/90_models/cohere/retry.py)
- [cookbook/90_models/cometapi/README.md](cookbook/90_models/cometapi/README.md)
- [cookbook/91_tools/mcp/github.py](cookbook/91_tools/mcp/github.py)
- [cookbook/91_tools/mcp/mcp_toolbox_demo/README.md](cookbook/91_tools/mcp/mcp_toolbox_demo/README.md)

</details>



This page provides high-level overviews of concrete cookbook examples and architectural patterns for building with Agno. It bridges the gap between conceptual framework components and production-ready implementations by referencing the `cookbook/` directory.

For detailed, step-by-step guides, refer to the child pages linked in each section.

---

## 10.1. Basic Agent Examples

Basic patterns focus on single-agent capabilities including tool usage, structured data extraction, persistent conversation history, guardrails, and multimodal inputs. These examples demonstrate the core `Agent` class and its primary configuration parameters.

For details, see [Basic Agent Examples](#10.1).

**Sources:** [cookbook/01_demo/README.md:13-16]()

---

## 10.2. Team and Collaboration Examples

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
Sources: [cookbook/01_demo/README.md:76-82]()

For details, see [Team and Collaboration Examples](#10.2).

**Sources:** [cookbook/01_demo/README.md:76-82]()

---

## 10.3. Workflow Orchestration Examples

Workflows are used for predictable, multi-step processes where the order of execution, loops, conditional branching, and data flow must be strictly controlled, as demonstrated in `cookbook/04_workflows`.

- **Sequential Pipelines:** Sequentially execute steps using container types like `Steps` and `Step` [cookbook/91_tools/mcp/mcp_toolbox_demo/README.md:122-123]().
- **Human-in-the-Loop (HITL):** Requiring user confirmation via approval gates (`requires_confirmation`) before executing sensitive tasks [cookbook/91_tools/mcp/mcp_toolbox_demo/README.md:108-113]().
- **State Propagation:** Managing progress through discrete steps while passing `RunContext` and session state between them [cookbook/91_tools/mcp/mcp_toolbox_demo/README.md:124]().

For details, see [Workflow Orchestration Examples](#10.3).

**Sources:** [cookbook/91_tools/mcp/mcp_toolbox_demo/README.md:108-131]()

---

## 10.4. Model-Specific Examples

Agno is model-agnostic and provides deep integrations for provider-specific features across major LLM vendors under `cookbook/90_models`, including Claude thinking modes and skills, Gemini grounding, OpenAI reasoning models, and DeepSeek thinking capabilities.

For details, see [Model-Specific Examples](#10.4).

**Sources:** [cookbook/90_models/cometapi/README.md:1-4]()

---

## 10.5. Knowledge and RAG Examples

Retrieval-Augmented Generation (RAG) patterns allow agents to search through large document sets, leveraging the `Knowledge` class, vector database integrations, hybrid search strategies, chunking options, and remote content loaders from `cookbook/07_knowledge`.

- **Hybrid Search:** Combining vector similarity with keyword search using `SearchType.hybrid` and embedders like `OpenAIEmbedder` [cookbook/07_knowledge/README.md:26-33]().
- **Agentic Retrieval:** Allowing the agent to decide when to search the knowledge base using `search_knowledge=True` [cookbook/07_knowledge/README.md:37-42]().

For details, see [Knowledge and RAG Examples](#10.5).

**Sources:** [cookbook/07_knowledge/README.md:20-45]()

---

## 10.6. AgentOS Deployment Examples

`AgentOS` provides the runtime to serve agents, teams, and workflows as production-grade APIs with custom endpoints, authentication, WebSocket streaming, and lifespan management.

### Natural Language Space to Code Entity Space: AgentOS Architecture
This diagram maps abstract deployment concepts to the actual codebase classes and initialization files used in production setups like `cookbook/01_demo/run.py`.

```mermaid
graph TD
    ClientApp["Client UI / os.agno.com"] --> FastAPIApp["FastAPI app (app = agent_os.get_app())"]
    FastAPIApp --> OSInstance["AgentOS(name=\"Demo AgentOS\", agents=_agents, db=get_db())"]
    OSInstance --> LifespanFn["@asynccontextmanager lifespan(app)"]
    LifespanFn --> RegAgents["Registered Agents List [_agents]"]
    RegAgents --> LocalWiki["Agent(name=\"local_wiki\")"]
    RegAgents --> CodeSearch["Agent(name=\"code_search\")"]
    OSInstance --> DBBackend["SqliteDb / get_db()"]
```
Sources: [cookbook/01_demo/run.py:25-71]()

For details, see [AgentOS Deployment Examples](#10.6).

**Sources:** [cookbook/01_demo/run.py:25-71]()

---

## 10.7. Learning Machine Examples

The `LearningMachine` system enables agents to learn from every interaction through coordinated learning stores, user profile extraction, persistent memory, session context, and the Curator from `cookbook/08_learning`.

For details, see [Learning Machine Examples](#10.7).

**Sources:** [cookbook/01_demo/TEST_LOG.md:25-26]()

---

## 10.8. Data Labeling Examples

The data labeling cookbook covers automated text, image, audio, and video classification, structured extraction, pairwise preference evaluation, rejection sampling, inter-annotator agreement calculation, safety labeling, and scale-out evaluation pipelines.

For details, see [Data Labeling Examples](#10.8).

**Sources:** [cookbook/01_demo/TEST_LOG.md:93]()

---

