<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agents-from-scratch · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [langgraph.json](langgraph.json)
- [pyproject.toml](pyproject.toml)
- [src/email_assistant/schemas.py](src/email_assistant/schemas.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to the **agents-from-scratch** repository, a hands-on tutorial for building a production-ready email assistant agent using LangGraph. The repository teaches agent development through progressive implementation, starting from basic ReAct patterns and advancing to human-in-the-loop oversight, memory-enabled learning, and Gmail API integration.

The tutorial is structured as four cumulative stages, each combining an interactive Jupyter notebook for learning and experimentation with production Python modules for deployment. By the final stage, the system demonstrates a fully functional "ambient" agent capable of triaging, responding to, and learning from email interactions with real Gmail and Google Calendar APIs.

For details on the LangGraph framework concepts used throughout (StateGraph, checkpoints, interrupts), see [LangGraph Framework](#2). For environment setup and deployment instructions, see [Development Setup](#8) and [Deployment](#8.1). For the core architecture details, see [Email Assistant Core Architecture](#3).

**Sources**: [README.md:1-6](), [README.md:75-130]()

---

## Repository Organization

The repository follows a **notebook-driven development pattern** where concepts are prototyped interactively before being hardened into production code. Each learning module consists of a paired notebook and Python implementation.

### File Structure Overview

```mermaid
graph TB
    subgraph "Learning Materials"
        NB_101["langgraph_101.ipynb<br/>Framework Fundamentals"]
        NB_Agent["agent.ipynb<br/>Basic Email Assistant"]
        NB_Eval["evaluation.ipynb<br/>Testing & Evaluation"]
        NB_HITL["hitl.ipynb<br/>Human-in-the-Loop"]
        NB_Memory["memory.ipynb<br/>Memory Integration"]
    end
    
    subgraph "Production Implementations"
        Impl_1["email_assistant.py<br/>Basic agent"]
        Impl_2["email_assistant_hitl.py<br/>+ Human oversight"]
        Impl_3["email_assistant_hitl_memory.py<br/>+ Learning from feedback"]
        Impl_4["email_assistant_hitl_memory_gmail.py<br/>+ Gmail/Calendar APIs"]
    end
    
    subgraph "Supporting Systems"
        Tools_Base["tools/base.py<br/>Mock tools for development"]
        Tools_Gmail["tools/gmail/<br/>Production API tools"]
        Dataset["eval/email_dataset.py<br/>Test cases"]
        Tests["tests/run_all_tests.py<br/>Automated testing"]
        Config["langgraph.json<br/>Graph registry"]
    end
    
    subgraph "Deployment Infrastructure"
        LG_Dev["langgraph dev<br/>Local server"]
        LG_Cloud["LangGraph Platform<br/>Cloud hosting"]
        Inbox["Agent Inbox<br/>HITL interface"]
    end
    
    NB_101 -.->|"teaches"| NB_Agent
    NB_Agent -.->|"demonstrates"| Impl_1
    NB_HITL -.->|"demonstrates"| Impl_2
    NB_Memory -.->|"demonstrates"| Impl_3
    
    Impl_1 -->|"extends to"| Impl_2
    Impl_2 -->|"extends to"| Impl_3
    Impl_3 -->|"extends to"| Impl_4
    
    Impl_1 --> Tools_Base
    Impl_4 --> Tools_Gmail
    
    NB_Eval --> Dataset
    Tests --> Dataset
    Tests -.->|"validates"| Impl_4
    
    Config -->|"registers"| Impl_4
    Impl_4 -.->|"deploys to"| LG_Dev
    Impl_4 -.->|"deploys to"| LG_Cloud
    Impl_2 --> Inbox
    Impl_3 --> Inbox
    Impl_4 --> Inbox
```

**Sources**: [README.md:75-130](), [langgraph.json:1-16]()

### Repository Directory Structure

| Directory/File | Purpose |
|----------------|---------|
| `notebooks/` | Interactive Jupyter notebooks for learning and experimentation |
| `src/email_assistant/` | Production Python modules implementing the agent variants |
| `src/email_assistant/tools/` | Tool implementations (mock and Gmail API) |
| `eval/` | Test datasets and evaluation utilities |
| `tests/` | Automated test suite using pytest and LangSmith |
| `langgraph.json` | Graph registry for LangGraph Platform deployment |
| `pyproject.toml` | Python dependencies and package configuration |

**Sources**: [README.md:75-130](), [pyproject.toml:1-66]()

---

## Four-Stage Learning Path

The tutorial progresses through four cumulative implementation stages, each adding new capabilities while preserving all previous features. This design allows learners to understand how production agents evolve from simple prototypes.

### Stage Progression Diagram

```mermaid
graph LR
    subgraph "Stage 1: Foundation"
        S1_NB["agent.ipynb"]
        S1_Code["email_assistant.py"]
        S1_Features["Features:<br/>• Email triage router<br/>• LLM-powered responses<br/>• Mock tool execution<br/>• ReAct pattern"]
    end
    
    subgraph "Stage 2: Safety Controls"
        S2_NB["hitl.ipynb"]
        S2_Code["email_assistant_hitl.py"]
        S2_Features["Added Features:<br/>• Human approval gates<br/>• Interrupt mechanism<br/>• Agent Inbox UI<br/>• Tool call review"]
    end
    
    subgraph "Stage 3: Adaptive Learning"
        S3_NB["memory.ipynb"]
        S3_Code["email_assistant_hitl_memory.py"]
        S3_Features["Added Features:<br/>• User preference storage<br/>• Feedback learning<br/>• LangGraph Store<br/>• Memory-guided behavior"]
    end
    
    subgraph "Stage 4: Production Ready"
        S4_Code["email_assistant_hitl_memory_gmail.py"]
        S4_Features["Added Features:<br/>• Gmail API integration<br/>• Calendar API<br/>• OAuth authentication<br/>• Automated ingestion"]
    end
    
    S1_NB -.->|"teaches"| S1_Code
    S2_NB -.->|"teaches"| S2_Code
    S3_NB -.->|"teaches"| S3_Code
    
    S1_Code ==>|"inherits all"| S2_Code
    S2_Code ==>|"inherits all"| S3_Code
    S3_Code ==>|"inherits all"| S4_Code
    
    S1_Features -.-> S1_Code
    S2_Features -.-> S2_Code
    S3_Features -.-> S3_Code
    S4_Features -.-> S4_Code
```

**Sources**: [README.md:82-130]()

### Feature Accumulation Table

| Stage | Notebook | Production Module | Core Feature Added | Key Concepts |
|-------|----------|------------------|-------------------|--------------|
| **Preface** | `langgraph_101.ipynb` | `langgraph_101.py` | LangGraph fundamentals | StateGraph, nodes, edges, memory |
| **1: Foundation** | `agent.ipynb` | `email_assistant.py` | Email triage + response agent | ReAct pattern, tool calling, routing |
| **Evaluation** | `evaluation.ipynb` | N/A | Testing framework | Pytest, LLM-as-judge, LangSmith evaluate |
| **2: Safety** | `hitl.ipynb` | `email_assistant_hitl.py` | Human approval gates | Interrupts, checkpoints, Agent Inbox |
| **3: Learning** | `memory.ipynb` | `email_assistant_hitl_memory.py` | User preference memory | LangGraph Store, feedback loops |
| **4: Production** | N/A | `email_assistant_hitl_memory_gmail.py` | Gmail/Calendar APIs | OAuth, API integration, cron ingestion |

**Sources**: [README.md:79-130](), [langgraph.json:4-9]()

---

## High-Level Architecture

The email assistant implements a **two-phase workflow**: triage routing followed by agent-based response generation. Both phases leverage LLM decision-making, tool execution, and optional human oversight.

### Core Workflow Architecture

```mermaid
graph TB
    Start["Email Input<br/>(email_input)"]
    
    subgraph "Phase 1: Triage"
        Triage["triage_router()<br/>LLM classification"]
        TRouter["RouterSchema<br/>{reasoning, classification}"]
        TDecision{"classification?"}
    end
    
    subgraph "Phase 2: Response Agent"
        Agent["agent()<br/>Response generation"]
        Tools["get_tools()<br/>Tool registry"]
        ToolExec["tool_node()<br/>Tool execution"]
        HITL["interrupt()<br/>Human review"]
        Memory["update_memory()<br/>Store feedback"]
    end
    
    subgraph "State Management"
        StateClass["State(MessagesState)<br/>{email_input, classification_decision, messages}"]
        Checkpoint["MemorySaver()<br/>Thread state persistence"]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI GPT-4<br/>LLM provider"]
        Gmail["Gmail API<br/>Email operations"]
        Calendar["Calendar API<br/>Scheduling"]
        Store["LangGraph Store<br/>User preferences"]
    end
    
    Start --> StateClass
    StateClass --> Triage
    Triage --> TRouter
    TRouter --> TDecision
    
    TDecision -->|"ignore"| End1["END"]
    TDecision -->|"notify"| HITL
    TDecision -->|"respond"| Agent
    
    Agent --> Tools
    Tools --> ToolExec
    ToolExec -->|"HITL tools"| HITL
    ToolExec -->|"direct tools"| Results["Tool results"]
    
    HITL -->|"feedback"| Memory
    Memory --> Store
    Results --> Agent
    
    Agent -.->|"LLM calls"| OpenAI
    Triage -.->|"LLM calls"| OpenAI
    ToolExec -.->|"send_email_tool"| Gmail
    ToolExec -.->|"schedule_meeting_tool"| Calendar
    
    StateClass --> Checkpoint
```

**Sources**: [src/email_assistant/schemas.py:1-38](), [README.md:82-130]()

### Key Architectural Components

#### State Management: `State` Class

The `State` class extends `MessagesState` to track email processing:

```python
# From schemas.py
class State(MessagesState):
    email_input: dict              # Original email data
    classification_decision: str    # Triage decision (ignore/respond/notify)
    # messages: list[Message]       # Inherited from MessagesState
```

**Sources**: [src/email_assistant/schemas.py:21-24]()

#### Workflow Phases

1. **Triage Phase** (`triage_router` node):
   - Uses LLM with structured output (`RouterSchema`) to classify emails
   - Three outcomes: `ignore`, `notify` (requires human review), `respond` (proceed to agent)
   - Reads from LangGraph Store to apply learned preferences

2. **Agent Phase** (`agent` node):
   - Implements ReAct pattern with `tool_choice="required"`
   - Executes tools via `tool_node` with conditional HITL gating
   - Updates memory based on human feedback

3. **Tool Execution** (`tool_node`):
   - Separates tools into HITL-required vs direct execution
   - HITL tools: `write_email`, `schedule_meeting`, `Question`
   - Direct tools: `check_calendar_availability`, `Done`, `fetch_emails_tool`

**Sources**: [src/email_assistant/schemas.py:5-16](), [README.md:82-130]()

---

## Key Technologies and Dependencies

The system integrates multiple technologies to provide agent capabilities, observability, and deployment infrastructure.

### Technology Stack Diagram

```mermaid
graph TB
    subgraph "Core Framework"
        LangGraph["LangGraph >=1.0.0<br/>StateGraph, interrupts, Store"]
        LangChain["LangChain >=1.0.0<br/>Model abstractions"]
        LangSmith["LangSmith >=0.4.37<br/>Tracing & evaluation"]
    end
    
    subgraph "LLM Provider"
        OpenAI_SDK["langchain-openai >=1.0.0<br/>ChatOpenAI"]
        GPT4["OpenAI API<br/>gpt-4 models"]
    end
    
    subgraph "External APIs"
        Gmail_SDK["google-api-python-client >=2.128.0"]
        Gmail_Auth["google-auth-oauthlib<br/>OAuth 2.0 flow"]
        Gmail_API["Gmail API<br/>Email operations"]
        Calendar_API["Google Calendar API<br/>Meeting scheduling"]
    end
    
    subgraph "Development Tools"
        Jupyter["jupyter >=1.0.0<br/>Interactive notebooks"]
        Pytest["pytest + pytest-xdist<br/>Testing framework"]
        LG_CLI["langgraph-cli >=0.4.0<br/>Local dev server"]
    end
    
    subgraph "Supporting Libraries"
        Pydantic["pydantic (via LangChain)<br/>Schema validation"]
        Rich["rich<br/>Console output"]
        HTML2Text["html2text<br/>Email parsing"]
    end
    
    LangGraph --> LangChain
    LangChain --> OpenAI_SDK
    OpenAI_SDK --> GPT4
    
    Gmail_SDK --> Gmail_Auth
    Gmail_SDK --> Gmail_API
    Gmail_SDK --> Calendar_API
    
    LangGraph -.->|"traces to"| LangSmith
    Pytest -.->|"logs to"| LangSmith
```

**Sources**: [pyproject.toml:6-25]()

### Required Environment Variables

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `OPENAI_API_KEY` | OpenAI API authentication | All implementations |
| `LANGSMITH_API_KEY` | LangSmith tracing and evaluation | All implementations (optional but recommended) |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | All implementations |
| `LANGSMITH_PROJECT` | Project name for trace organization | All implementations |
| Google OAuth credentials | Gmail/Calendar API access | Stage 4 only (`email_assistant_hitl_memory_gmail.py`) |

**Sources**: [README.md:18-45]()

---

## Development and Deployment Workflow

The repository supports both local development and cloud deployment through LangGraph Platform.

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Notebooks["Jupyter Notebooks<br/>Interactive prototyping"]
        Local_Python["Python Scripts<br/>Direct module execution"]
        LG_Dev["langgraph dev<br/>Local server mode"]
    end
    
    subgraph "Testing Pipeline"
        Unit_Tests["tests/run_all_tests.py<br/>Pytest runner"]
        Notebook_Tests["tests/test_notebooks.py<br/>Notebook validation"]
        Dataset["eval/email_dataset.py<br/>Test cases"]
    end
    
    subgraph "Graph Registry"
        LG_JSON["langgraph.json<br/>Graph definitions"]
        Graphs["Registered graphs:<br/>• email_assistant<br/>• email_assistant_hitl<br/>• email_assistant_hitl_memory<br/>• email_assistant_hitl_memory_gmail<br/>• cron"]
    end
    
    subgraph "Deployment Targets"
        LG_Studio["LangGraph Studio<br/>Visual debugging"]
        LG_Server["LangGraph Server<br/>HTTP API"]
        LG_Platform["LangGraph Platform<br/>Cloud hosting"]
    end
    
    subgraph "Human Interface"
        AgentInbox["Agent Inbox<br/>dev.agentinbox.ai<br/>HITL approvals"]
    end
    
    subgraph "Observability"
        LangSmith_Platform["LangSmith Platform<br/>smith.langchain.com<br/>Traces & metrics"]
    end
    
    Notebooks -.->|"develops"| Local_Python
    Local_Python --> LG_JSON
    
    Unit_Tests --> Dataset
    Notebook_Tests --> Notebooks
    
    LG_JSON --> LG_Dev
    LG_JSON --> LG_Studio
    LG_JSON --> LG_Server
    LG_JSON --> LG_Platform
    
    LG_Dev -.->|"HITL"| AgentInbox
    LG_Platform -.->|"HITL"| AgentInbox
    
    LG_Dev -.->|"traces"| LangSmith_Platform
    LG_Platform -.->|"traces"| LangSmith_Platform
    Unit_Tests -.->|"logs"| LangSmith_Platform
```

**Sources**: [README.md:132-166](), [langgraph.json:1-16]()

### Graph Registration via `langgraph.json`

The [langgraph.json:1-16]() file registers five graphs for deployment:

| Graph ID | Module Path | Purpose |
|----------|-------------|---------|
| `langgraph101` | `src/email_assistant/langgraph_101.py:app` | Educational example |
| `email_assistant` | `src/email_assistant/email_assistant.py:email_assistant` | Stage 1: Basic agent |
| `email_assistant_hitl` | `src/email_assistant/email_assistant_hitl.py:email_assistant` | Stage 2: + HITL |
| `email_assistant_hitl_memory` | `src/email_assistant/email_assistant_hitl_memory.py:email_assistant` | Stage 3: + Memory |
| `email_assistant_hitl_memory_gmail` | `src/email_assistant/email_assistant_hitl_memory_gmail.py:email_assistant` | Stage 4: + Gmail |
| `cron` | `src/email_assistant/cron.py:graph` | Automated email ingestion |

**Sources**: [langgraph.json:3-9]()

---

## Next Steps

This overview provides the foundation for understanding the agents-from-scratch repository structure and learning path. To dive deeper into specific components:

- **LangGraph fundamentals**: See [LangGraph Framework](#2) for StateGraph, interrupts, and checkpoints
- **Agent architecture details**: See [Email Assistant Core Architecture](#3) for triage router and agent implementation
- **HITL implementation**: See [Human-in-the-Loop (HITL) Integration](#3.2) for interrupt handling and Agent Inbox
- **Memory system**: See [Memory System](#3.3) for LangGraph Store and preference learning
- **Tool architecture**: See [Tool System](#4) for mock vs production tools
- **Evaluation methodology**: See [Evaluation System](#7) for testing and LLM-as-judge
- **Setup instructions**: See [Development Setup](#8) for environment configuration

**Sources**: [README.md:1-175]()

---

