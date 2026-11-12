<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/UFO · page 2 System Architecture Overview · fetched 2026-10-26 -->

# System Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [assets/orchestrator.png](assets/orchestrator.png)
- [assets/task_constellation.png](assets/task_constellation.png)
- [documents/docs/choose_path.md](documents/docs/choose_path.md)
- [documents/docs/galaxy/overview.md](documents/docs/galaxy/overview.md)
- [documents/docs/getting_started/quick_start_galaxy.md](documents/docs/getting_started/quick_start_galaxy.md)
- [documents/docs/img/aip_new.png](documents/docs/img/aip_new.png)
- [documents/docs/img/decomposition.png](documents/docs/img/decomposition.png)
- [documents/docs/index.md](documents/docs/index.md)
- [documents/docs/infrastructure/agents/agent_types.md](documents/docs/infrastructure/agents/agent_types.md)
- [documents/docs/infrastructure/agents/overview.md](documents/docs/infrastructure/agents/overview.md)
- [documents/docs/infrastructure/agents/server_client_architecture.md](documents/docs/infrastructure/agents/server_client_architecture.md)
- [documents/docs/infrastructure/modules/context.md](documents/docs/infrastructure/modules/context.md)
- [documents/docs/infrastructure/modules/dispatcher.md](documents/docs/infrastructure/modules/dispatcher.md)
- [documents/docs/infrastructure/modules/overview.md](documents/docs/infrastructure/modules/overview.md)
- [documents/docs/infrastructure/modules/platform_sessions.md](documents/docs/infrastructure/modules/platform_sessions.md)
- [documents/docs/infrastructure/modules/round.md](documents/docs/infrastructure/modules/round.md)
- [documents/docs/infrastructure/modules/session.md](documents/docs/infrastructure/modules/session.md)
- [documents/docs/infrastructure/modules/session_pool.md](documents/docs/infrastructure/modules/session_pool.md)
- [documents/docs/ufo2/app_agent/commands.md](documents/docs/ufo2/app_agent/commands.md)
- [documents/docs/ufo2/app_agent/overview.md](documents/docs/ufo2/app_agent/overview.md)
- [documents/docs/ufo2/app_agent/state.md](documents/docs/ufo2/app_agent/state.md)
- [documents/docs/ufo2/app_agent/strategy.md](documents/docs/ufo2/app_agent/strategy.md)
- [documents/docs/ufo2/core_features/hybrid_actions.md](documents/docs/ufo2/core_features/hybrid_actions.md)
- [documents/docs/ufo2/host_agent/commands.md](documents/docs/ufo2/host_agent/commands.md)
- [documents/docs/ufo2/host_agent/overview.md](documents/docs/ufo2/host_agent/overview.md)
- [documents/docs/ufo2/host_agent/state.md](documents/docs/ufo2/host_agent/state.md)
- [documents/docs/ufo2/host_agent/strategy.md](documents/docs/ufo2/host_agent/strategy.md)
- [documents/docs/ufo2/overview.md](documents/docs/ufo2/overview.md)
- [documents/mkdocs.yml](documents/mkdocs.yml)
- [galaxy/README.md](galaxy/README.md)
- [galaxy/README_ZH.md](galaxy/README_ZH.md)
- [ufo/README.md](ufo/README.md)
- [ufo/README_ZH.md](ufo/README_ZH.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the UFO³ system architecture, explaining how the two-tier framework operates and how its major components interact. It covers the architectural layers from user request to task execution across heterogeneous devices.

**Scope of this document:**
- Two-tier architecture: Galaxy orchestration layer and UFO² device agent layer
- Agent hierarchy and processing pipeline
- Session and round lifecycle management
- Agent Interaction Protocol (AIP) communication layer
- Data flow from natural language to device execution

**Related pages:**
- For detailed information on UFO² agent processing, see [Agent Processing System](#3.1)
- For Galaxy-specific orchestration details, see [Galaxy Architecture](#4.1)
- For AIP protocol details, see [Agent Interaction Protocol](#5)
- For configuration management, see [Configuration System](#6)

---

## Two-Tier Architecture

UFO³ employs a **hierarchical two-tier architecture** that separates global orchestration from local execution, enabling scalable cross-device automation while maintaining operational independence of device agents.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Tier 1: Galaxy Orchestration Layer"
        GalaxyClient["GalaxyClient<br/>(galaxy/client/galaxy_client.py)"]
        ConstellationAgent["ConstellationAgent<br/>(galaxy/agents/constellation_agent.py)"]
        TaskOrchestrator["TaskConstellationOrchestrator<br/>(galaxy/orchestrator/constellation_orchestrator.py)"]
        TaskConstellation["TaskConstellation<br/>(galaxy/constellation/task_constellation.py)"]
        DeviceManager["ConstellationDeviceManager<br/>(galaxy/client/constellation_client.py)"]
        
        GalaxyClient --> ConstellationAgent
        ConstellationAgent --> TaskConstellation
        TaskOrchestrator --> TaskConstellation
        GalaxyClient --> TaskOrchestrator
        TaskOrchestrator --> DeviceManager
    end
    
    subgraph "AIP Communication Layer"
        AIPProtocol["WebSocket Protocol<br/>(aip/messages.py)"]
        style AIPProtocol fill:#fff,stroke:#333,stroke-width:3px
    end
    
    subgraph "Tier 2: Device Agent Layer"
        subgraph "Windows Device"
            UFOServer["UFOWebSocketHandler<br/>(ufo/module/web_server.py)"]
            HostAgent["HostAgent<br/>(ufo/agents/agent/host_agent.py)"]
            AppAgent["AppAgent<br/>(ufo/agents/agent/app_agent.py)"]
            Session["Session<br/>(ufo/module/sessions/session.py)"]
            
            UFOServer --> Session
            Session --> HostAgent
            HostAgent --> AppAgent
        end
        
        subgraph "Linux Device"
            LinuxServer["Linux WebSocket Server"]
            LinuxAgent["LinuxAgent"]
            MCPServers["MCP Servers"]
            
            LinuxServer --> LinuxAgent
            LinuxAgent --> MCPServers
        end
    end
    
    DeviceManager <--> AIPProtocol
    AIPProtocol <--> UFOServer
    AIPProtocol <--> LinuxServer
```

**Sources:**
- [README.md:125-154]()
- [galaxy/README.md:27-57]()
- [documents/docs/index.md:81-109]()

### Tier 1: Galaxy Orchestration Layer

The **Galaxy layer** provides multi-device orchestration capabilities through LLM-driven task decomposition and DAG-based scheduling:

| Component | Class/Module | Responsibility |
|-----------|--------------|----------------|
| **GalaxyClient** | `galaxy.client.galaxy_client.GalaxyClient` | Entry point for multi-device sessions, manages ConstellationClient and session lifecycle [galaxy/README.md:180-186]() |
| **ConstellationAgent** | `galaxy.agents.constellation_agent.ConstellationAgent` | LLM-driven agent that decomposes user requests into DAG structures (Creation mode) and adapts DAGs based on execution feedback (Editing mode) [galaxy/README.md:66-71]() |
| **TaskConstellation** | `galaxy.constellation.task_constellation.TaskConstellation` | Dynamic DAG data structure with TaskStars (nodes) and TaskStarLines (edges) representing distributed workflow [galaxy/README.md:82-92]() |
| **TaskOrchestrator** | `galaxy.orchestrator.constellation_orchestrator.TaskConstellationOrchestrator` | Asynchronous execution engine that schedules ready tasks, dispatches to devices, and manages completion events [galaxy/README.md:144-147]() |
| **DeviceManager** | `galaxy.client.constellation_client.ConstellationDeviceManager` | Maintains device registry (AgentProfile), manages WebSocket connections, routes tasks, monitors heartbeats [documents/docs/galaxy/overview.md:44-51]() |

**Sources:**
- [galaxy/README.md:170-201]()
- [documents/docs/galaxy/overview.md:32-89]()

### Tier 2: Device Agent Layer

The **device agent layer** executes tasks locally on individual devices using platform-specific automation capabilities:

| Component | Class/Module | Responsibility |
|-----------|--------------|----------------|
| **Session** | `ufo.module.sessions.session.Session` | Manages multi-round user interaction lifecycle on a single device [ufo/README.md:76-80]() |
| **BaseRound** | `ufo.module.basic.BaseRound` | Encapsulates a single user request with step-by-step agent processing [ufo/README.md:142-147]() |
| **HostAgent** | `ufo.agents.agent.host_agent.HostAgent` | Desktop-level orchestrator that analyzes environment and spawns AppAgents [ufo/README.md:76-80]() |
| **AppAgent** | `ufo.agents.agent.app_agent.AppAgent` | Application-specific agent that executes fine-grained actions within apps [documents/docs/ufo2/app_agent/overview.md:1-22]() |
| **ProcessorTemplate** | `ufo.agents.processors.core.processor_framework.ProcessorTemplate` | Abstract base for agent processing pipeline with middleware support [documents/docs/ufo2/app_agent/overview.md:105-121]() |

**Sources:**
- [documents/docs/ufo2/overview.md:52-64]()
- [documents/docs/ufo2/app_agent/overview.md:9-22]()

---

## UFO² Desktop AgentOS Architecture

UFO² implements a **hierarchical multi-agent system** with state machines, processing pipelines, and hybrid GUI/API execution capabilities.

### Session and Round Lifecycle

```mermaid
graph LR
    subgraph "Session Lifecycle"
        SessionFactory["SessionFactory<br/>(ufo/module/sessions/session_factory.py)"]
        Session["Session/FollowerSession/FromFileSession<br/>(ufo/module/sessions/)"]
        Context["Context<br/>(ufo/module/context.py)"]
        
        SessionFactory -->|creates| Session
        Session -->|manages| Context
    end
    
    subgraph "Round Execution"
        BaseRound["BaseRound<br/>(ufo/module/basic.py)"]
        HostAgent["HostAgent"]
        AppAgent["AppAgent"]
        State["AgentState<br/>(ufo/agents/states/)"]
        
        Session -->|creates rounds| BaseRound
        BaseRound -->|starts with| HostAgent
        HostAgent -->|spawns| AppAgent
        BaseRound -->|manages| State
    end
    
    subgraph "Processing Pipeline"
        Processor["ProcessorTemplate<br/>(processor_framework.py)"]
        Strategy["ProcessingStrategy"]
        Middleware["Middleware Chain"]
        
        HostAgent -->|uses| Processor
        AppAgent -->|uses| Processor
        Processor -->|executes| Strategy
        Processor -->|applies| Middleware
    end
```

**Sources:**
- [documents/docs/ufo2/overview.md:42-49]()
- [documents/docs/ufo2/app_agent/overview.md:56-83]()

### Agent Hierarchy and State Machines

UFO² agents follow a **finite state machine** pattern for robust workflow control:

```mermaid
graph TB
    subgraph "HostAgent FSM"
        H_Continue["ContinueHostAgentState"]
        H_Assign["AssignHostAgentState"]
        H_Finish["FinishHostAgentState"]
        H_Pending["PendingHostAgentState"]
        H_Confirm["ConfirmHostAgentState"]
        
        H_Continue -->|"status=ASSIGN"| H_Assign
        H_Continue -->|"status=FINISH"| H_Finish
        H_Continue -->|"status=PENDING"| H_Pending
        H_Assign -->|"creates AppAgent"| A_Continue
    end
    
    subgraph "AppAgent FSM"
        A_Continue["CONTINUE<br/>(ufo2/app_agent/state.md)"]
        A_Finish["FINISH<br/>(ufo2/app_agent/state.md)"]
        A_Screenshot["SCREENSHOT<br/>(ufo2/app_agent/state.md)"]
        A_Confirm["CONFIRM<br/>(ufo2/app_agent/state.md)"]
        A_Pending["PENDING<br/>(ufo2/app_agent/state.md)"]
        
        A_Continue -->|"status=FINISH"| A_Finish
        A_Continue -->|"status=SCREENSHOT"| A_Screenshot
        A_Continue -->|"status=CONFIRM"| A_Confirm
        A_Continue -->|"status=PENDING"| A_Pending
        A_Screenshot -->|"re-annotate"| A_Continue
        A_Finish -->|"subtask done"| H_Continue
    end
```

**Key State Transitions:**

| State | Agent | Trigger | Action | Next State |
|-------|-------|---------|--------|------------|
| `CONTINUE` | HostAgent | Desktop analysis needed | Executes `HostAgentProcessor.process()` | `ASSIGN` or `FINISH` |
| `ASSIGN` | HostAgent | Application selected | Calls `create_subagent()` | AppAgent's `CONTINUE` |
| `CONTINUE` | AppAgent | Action execution needed | Executes `AppAgentProcessor.process()` | `FINISH`, `CONFIRM`, or `SCREENSHOT` |
| `FINISH` | AppAgent | Subtask completed | Returns to HostAgent | HostAgent's `CONTINUE` |
| `CONFIRM` | AppAgent | Safety check required | Prompts user confirmation | `CONTINUE` or `FINISH` |

**Sources:**
- [documents/docs/ufo2/app_agent/overview.md:91-103]()
- [documents/docs/ufo2/host_agent/overview.md:52-64]()

### Processing Pipeline Architecture

Both HostAgent and AppAgent utilize the **ProcessorTemplate pattern** with a four-phase pipeline:

```mermaid
graph LR
    subgraph "Processor Framework"
        ProcessorTemplate["ProcessorTemplate"]
        ProcessingContext["ProcessingContext"]
        
        ProcessorTemplate -->|creates| ProcessingContext
    end
    
    subgraph "Four-Phase Pipeline"
        Phase1["DATA_COLLECTION<br/>Screenshot + UI Tree"]
        Phase2["LLM_INTERACTION<br/>Prompt + Parse Response"]
        Phase3["ACTION_EXECUTION<br/>GUI/API Action"]
        Phase4["MEMORY_UPDATE<br/>History + Blackboard"]
        
        Phase1 --> Phase2
        Phase2 --> Phase3
        Phase3 --> Phase4
    end
```

**AppAgent Processor:**
- Class: `ufo.agents.processors.app_agent_processor.AppAgentProcessor`
- Phases defined in: [documents/docs/ufo2/app_agent/overview.md:105-121]()

**Sources:**
- [documents/docs/ufo2/app_agent/overview.md:105-121]()
- [documents/docs/ufo2/host_agent/overview.md:52-64]()

---

## Galaxy Orchestration Layer

The Galaxy layer provides **LLM-driven multi-device orchestration** through dynamic DAG decomposition and event-driven scheduling.

### ConstellationAgent: LLM-Driven Planning

```mermaid
graph TB
    subgraph "ConstellationAgent FSM"
        START["START State<br/>Creation Mode"]
        CONTINUE["CONTINUE State<br/>Editing Mode"]
        FINISH["FINISH State"]
        FAIL["FAIL State"]
        
        START -->|"Initial DAG created"| CONTINUE
        CONTINUE -->|"Task completed event"| CONTINUE
        CONTINUE -->|"All tasks done"| FINISH
        CONTINUE -->|"Unrecoverable error"| FAIL
    end
```

**ConstellationAgent** operates in two modes:

| Mode | Purpose | Input | Output |
|------|---------|-------|--------|
| **Creation** | Initial task decomposition | User request + device capabilities | New `TaskConstellation` DAG [documents/docs/galaxy/overview.md:128-130]() |
| **Editing** | Runtime adaptation | Task results + current DAG | `ConstellationEditor` commands to modify DAG [documents/docs/galaxy/overview.md:131-132]() |

**Sources:**
- [galaxy/README.md:66-92]()
- [documents/docs/galaxy/overview.md:118-132]()

### TaskConstellation: Dynamic DAG Structure

The **TaskConstellation** represents the distributed workflow as a directed acyclic graph:

```mermaid
graph TB
    subgraph "TaskConstellation Data Structure"
        TC["TaskConstellation"]
        TaskStars["TaskStars<br/>(Nodes)"]
        TaskStarLines["TaskStarLines<br/>(Edges)"]
        
        TC -->|contains| TaskStars
        TC -->|contains| TaskStarLines
    end
```

**DAG Invariants**:
1. **Acyclicity**: No cycles in dependency graph [documents/docs/galaxy/overview.md:28]()
2. **Safety Guarantees**: Formal invariants ensuring DAG consistency [galaxy/README.md:51-53]()

**Sources:**
- [galaxy/README.md:66-74]()
- [documents/docs/galaxy/overview.md:93-116]()

---

## Agent Interaction Protocol (AIP)

AIP provides **WebSocket-based bidirectional communication** between Galaxy orchestrator and device agents with automatic reconnection and fault tolerance.

### Protocol Stack

```mermaid
graph TB
    subgraph "AIP Protocol Stack"
        RegistrationProtocol["RegistrationProtocol"]
        TaskProtocol["TaskExecutionProtocol"]
        HeartbeatProtocol["HeartbeatProtocol"]
        DeviceInfoProtocol["DeviceInfoProtocol"]
    end
```

**Sources:**
- [galaxy/README.md:115-127]()
- [documents/docs/galaxy/overview.md:71-85]()

---

## Data Flow and Execution Path

### End-to-End Request Flow (Galaxy Mode)

```mermaid
sequenceDiagram
    participant User
    participant GalaxyClient
    participant ConstellationAgent
    participant TaskOrchestrator
    participant DeviceManager
    participant UFOServer
    
    User->>GalaxyClient: User Request
    GalaxyClient->>ConstellationAgent: Synthesize DAG
    ConstellationAgent-->>GalaxyClient: TaskConstellation
    GalaxyClient->>TaskOrchestrator: Execute DAG
    TaskOrchestrator->>DeviceManager: Dispatch TaskStar
    DeviceManager->>UFOServer: AIP Message (Task Assignment)
```

**Sources:**
- [documents/docs/galaxy/overview.md:60-69]()
- [galaxy/README.md:193-201]()

### Local Execution Flow (UFO² Standalone)

```mermaid
sequenceDiagram
    participant User
    participant Session
    participant HostAgent
    participant AppAgent
    participant Puppeteer
    
    User->>Session: Task Request
    Session->>HostAgent: Analyze Goal
    HostAgent->>AppAgent: Delegate Subtask
    AppAgent->>Puppeteer: Execute Actions (GUI/API)
```

**Sources:**
- [documents/docs/ufo2/overview.md:42-64]()
- [documents/docs/ufo2/app_agent/overview.md:64-83]()

---

## Configuration System

UFO³ uses a **modular YAML-based configuration** system.

| File | Purpose |
|------|---------|
| `config/ufo/agents.yaml` | LLM configuration for Host/App agents [ufo/README.md:127-130]() |
| `config/galaxy/agent.yaml` | LLM configuration for ConstellationAgent [galaxy/README.md:233-239]() |
| `config/galaxy/devices.yaml` | Device registry and capabilities [galaxy/README.md:302-310]() |

**Sources:**
- [ufo/README.md:120-130]()
- [galaxy/README.md:222-239]()
- [documents/docs/getting_started/quick_start_galaxy.md:40-58]()

---

