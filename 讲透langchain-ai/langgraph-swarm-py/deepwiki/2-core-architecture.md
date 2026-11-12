<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langgraph-swarm-py · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [langgraph_swarm/__init__.py](langgraph_swarm/__init__.py)
- [langgraph_swarm/handoff.py](langgraph_swarm/handoff.py)
- [langgraph_swarm/swarm.py](langgraph_swarm/swarm.py)

</details>



## Purpose and Scope

This document provides an overview of the core `langgraph-swarm` library architecture and its primary components. It describes how the library enables multi-agent orchestration through state management, dynamic routing, and agent handoff mechanisms. For detailed implementation specifics, see:
- State schema and routing details: [SwarmState and Agent Routing](#2.1)
- Handoff tool implementation: [Agent Handoff Mechanism](#2.2)
- Persistence and checkpointing: [Memory and State Management](#2.3)

The core library consists of approximately 300 lines of code across two primary modules that build upon LangGraph's `StateGraph` and LangChain's `BaseTool` abstractions.

**Sources:** [langgraph_swarm/__init__.py:1-9](), [langgraph_swarm/swarm.py:1-290](), [langgraph_swarm/handoff.py:1-118]()

## Component Overview

The library provides four main public APIs exported from [langgraph_swarm/__init__.py]():

| Component | Type | Purpose |
|-----------|------|---------|
| `SwarmState` | Class | State schema containing messages and active agent tracking |
| `create_swarm()` | Function | Main entry point to construct multi-agent StateGraph |
| `add_active_agent_router()` | Function | Adds conditional routing from START node based on active_agent |
| `create_handoff_tool()` | Function | Generates tools that enable agent-to-agent transfers |

Additional internal utilities support these core components:

| Component | Type | Purpose |
|-----------|------|---------|
| `_update_state_schema_agent_names()` | Function | Dynamically converts `str` annotations to `Literal` types |
| `get_handoff_destinations()` | Function | Extracts handoff destinations from agent tool metadata |

**Sources:** [langgraph_swarm/__init__.py:1-9](), [langgraph_swarm/swarm.py:13-290](), [langgraph_swarm/handoff.py:43-118]()

## Architecture Diagram

```mermaid
graph TB
    subgraph "External Dependencies"
        LangGraph["LangGraph<br/>StateGraph, Pregel, Command"]
        LangChain["LangChain<br/>BaseTool, Messages"]
    end
    
    subgraph "Public API: langgraph_swarm/__init__.py"
        API["Exported symbols:<br/>SwarmState<br/>create_swarm<br/>add_active_agent_router<br/>create_handoff_tool"]
    end
    
    subgraph "swarm.py"
        SwarmState["SwarmState(MessagesState)<br/>messages: list<br/>active_agent: str | None"]
        create_swarm["create_swarm()<br/>Validates agents<br/>Updates state schema<br/>Builds StateGraph"]
        add_router["add_active_agent_router()<br/>Adds conditional edge from START<br/>Routes to active_agent or default"]
        update_schema["_update_state_schema_agent_names()<br/>Converts str to Literal[agent_names]"]
    end
    
    subgraph "handoff.py"
        create_handoff["create_handoff_tool()<br/>Returns BaseTool that returns Command"]
        get_destinations["get_handoff_destinations()<br/>Inspects ToolNode metadata"]
    end
    
    LangGraph -->|imports| create_swarm
    LangGraph -->|imports| add_router
    LangGraph -->|imports| create_handoff
    LangChain -->|imports| create_handoff
    
    API -->|exports| SwarmState
    API -->|exports| create_swarm
    API -->|exports| add_router
    API -->|exports| create_handoff
    
    create_swarm -->|calls| update_schema
    create_swarm -->|calls| add_router
    create_swarm -->|calls| get_destinations
    create_swarm -->|uses| SwarmState
    add_router -->|reads| SwarmState
    create_handoff -->|updates| SwarmState
```

**Sources:** [langgraph_swarm/__init__.py:1-9](), [langgraph_swarm/swarm.py:1-290](), [langgraph_swarm/handoff.py:1-118]()

## Code Organization

The library follows a simple two-module structure:

```mermaid
graph LR
    init["__init__.py<br/>(10 lines)<br/>Public API"]
    swarm["swarm.py<br/>(290 lines)<br/>State & Orchestration"]
    handoff["handoff.py<br/>(118 lines)<br/>Transfer Tools"]
    
    init -->|imports| swarm
    init -->|imports| handoff
    swarm -->|imports| handoff
```

### Module Responsibilities

**[langgraph_swarm/swarm.py]()**: Core orchestration logic
- `SwarmState` class definition [langgraph_swarm/swarm.py:13-20]()
- `create_swarm()` function that builds the multi-agent graph [langgraph_swarm/swarm.py:170-289]()
- `add_active_agent_router()` for conditional routing [langgraph_swarm/swarm.py:72-167]()
- `_update_state_schema_agent_names()` for dynamic typing [langgraph_swarm/swarm.py:26-69]()

**[langgraph_swarm/handoff.py]()**: Agent transfer mechanisms
- `create_handoff_tool()` that generates transfer tools [langgraph_swarm/handoff.py:43-96]()
- `get_handoff_destinations()` for destination extraction [langgraph_swarm/handoff.py:99-117]()
- Internal utilities for field access and name normalization [langgraph_swarm/handoff.py:13-40]()

**Sources:** [langgraph_swarm/__init__.py:1-9](), [langgraph_swarm/swarm.py:1-290](), [langgraph_swarm/handoff.py:1-118]()

## State Schema Architecture

The `SwarmState` class extends LangGraph's `MessagesState` to track the currently active agent:

```mermaid
graph TB
    MessagesState["MessagesState<br/>(from LangGraph)<br/>messages: list[BaseMessage]"]
    SwarmState["SwarmState<br/>Inherits: MessagesState<br/>Additional field:<br/>active_agent: str | None"]
    UpdatedSchema["Updated Schema<br/>(runtime-generated)<br/>active_agent: Literal['Agent1', 'Agent2', ...] | None"]
    
    MessagesState -->|inherits| SwarmState
    SwarmState -->|transformed by<br/>_update_state_schema_agent_names| UpdatedSchema
```

The `active_agent` field serves two purposes:
1. **Optional initialization**: Users can optionally specify a starting agent [langgraph_swarm/swarm.py:16-19]()
2. **Runtime tracking**: Updated by handoff tools during execution to track which agent is currently active

The dynamic type transformation from `str | None` to `Literal[agent_names] | None` provides IDE autocomplete and type checking while maintaining runtime flexibility. This transformation occurs in `_update_state_schema_agent_names()` [langgraph_swarm/swarm.py:26-69]().

**Sources:** [langgraph_swarm/swarm.py:13-20](), [langgraph_swarm/swarm.py:26-69]()

## Routing System

The routing system uses LangGraph's conditional edges to direct execution based on the `active_agent` state field:

```mermaid
graph LR
    START["START node"]
    route_fn["route_to_active_agent()<br/>Returns state.get('active_agent', default)"]
    AgentA["Agent A node"]
    AgentB["Agent B node"]
    AgentC["Agent C node"]
    
    START -->|"conditional edge"| route_fn
    route_fn -->|"if active_agent=='Agent A'"| AgentA
    route_fn -->|"if active_agent=='Agent B'"| AgentB
    route_fn -->|"if active_agent=='Agent C'"| AgentC
    route_fn -->|"if active_agent is None"| AgentA
```

The `add_active_agent_router()` function [langgraph_swarm/swarm.py:72-167]() implements this by:
1. Validating that `active_agent` exists in the state schema [langgraph_swarm/swarm.py:152-155]()
2. Defining a `route_to_active_agent()` function that reads state [langgraph_swarm/swarm.py:163-164]()
3. Adding a conditional edge from `START` with agent names as the path map [langgraph_swarm/swarm.py:166]()

The router falls back to `default_active_agent` when `active_agent` is `None`, which occurs on the first invocation before any handoffs.

**Sources:** [langgraph_swarm/swarm.py:72-167]()

## Handoff Tool Mechanism

Agent handoffs are implemented as LangChain `BaseTool` instances that return `Command` objects:

```mermaid
sequenceDiagram
    participant LLM as "Agent LLM"
    participant Tool as "transfer_to_agent_b<br/>(handoff tool)"
    participant Cmd as "Command object"
    participant Graph as "StateGraph"
    
    LLM->>Tool: "invoke with tool call ID"
    Tool->>Tool: "Read current state<br/>(InjectedState)"
    Tool->>Cmd: "Create Command(<br/>goto='Agent B',<br/>update={'active_agent': 'Agent B'})"
    Tool->>Graph: "Return Command"
    Graph->>Graph: "Update state.active_agent"
    Graph->>Graph: "Navigate to Agent B node"
```

The `create_handoff_tool()` function [langgraph_swarm/handoff.py:43-96]() generates tools with:
- Tool name: `transfer_to_{normalized_agent_name}` [langgraph_swarm/handoff.py:68]()
- Injected state parameter for reading current messages [langgraph_swarm/handoff.py:78]()
- Injected tool call ID for creating confirmation message [langgraph_swarm/handoff.py:79]()
- Metadata marking the destination agent [langgraph_swarm/handoff.py:95]()

The returned `Command` object [langgraph_swarm/handoff.py:86-93]() instructs the graph to:
1. Navigate to the target agent node via `goto=agent_name`
2. Update the parent graph state via `graph=Command.PARENT`
3. Append a confirmation `ToolMessage` and update `active_agent`

**Sources:** [langgraph_swarm/handoff.py:43-96]()

## Swarm Construction Flow

The `create_swarm()` function [langgraph_swarm/swarm.py:170-289]() orchestrates the construction of a multi-agent graph:

```mermaid
flowchart TD
    Input["Input:<br/>agents: list[Pregel]<br/>default_active_agent: str<br/>state_schema: type"]
    Validate["Validate:<br/>1. active_agent in schema<br/>2. agents list not empty<br/>3. default in agent names"]
    ExtractNames["Extract agent.name<br/>from each Pregel"]
    UpdateSchema["_update_state_schema_agent_names()<br/>str → Literal[names]"]
    CreateBuilder["StateGraph(updated_schema)"]
    AddRouter["add_active_agent_router()<br/>Add START routing"]
    AddNodes["For each agent:<br/>builder.add_node(name, agent,<br/>destinations=handoff_targets)"]
    Output["Return StateGraph<br/>(ready for compile)"]
    
    Input --> Validate
    Validate --> ExtractNames
    ExtractNames --> UpdateSchema
    UpdateSchema --> CreateBuilder
    CreateBuilder --> AddRouter
    AddRouter --> AddNodes
    AddNodes --> Output
```

Key validations performed [langgraph_swarm/swarm.py:255-268]():
1. `active_agent` annotation exists in state schema
2. Agents list is not empty
3. `default_active_agent` exists in the list of agent names

The function also calls `get_handoff_destinations()` [langgraph_swarm/swarm.py:284-286]() to extract handoff targets from each agent's tools, which are registered as valid destinations for the node.

**Sources:** [langgraph_swarm/swarm.py:170-289](), [langgraph_swarm/swarm.py:255-268]()

## Runtime Execution Model

The compiled swarm executes agents in a loop controlled by state and commands:

```mermaid
stateDiagram-v2
    [*] --> LoadState: "invoke() called"
    LoadState --> RouteStart: "Read active_agent from state"
    RouteStart --> ExecuteAgent: "Route to active_agent or default"
    ExecuteAgent --> ProcessLLM: "Agent node executes"
    ProcessLLM --> ToolCall?: "LLM response"
    
    ToolCall? --> RegularTool: "Regular tool invoked"
    ToolCall? --> HandoffTool: "Handoff tool invoked"
    ToolCall? --> FinalResponse: "No tool calls"
    
    RegularTool --> ProcessLLM: "Continue in same agent"
    HandoffTool --> UpdateState: "Command returned"
    UpdateState --> Checkpoint: "Update active_agent"
    Checkpoint --> ExecuteAgent: "Route to new agent"
    
    FinalResponse --> SaveState: "Save checkpoint"
    SaveState --> [*]: "Return to user"
```

The execution flow leverages several LangGraph primitives:
- **Checkpointer**: Persists state after each node execution for conversation continuity (covered in [Memory and State Management](#2.3))
- **Command objects**: Enable both navigation (`goto`) and state updates (`update`) in a single return value [langgraph_swarm/handoff.py:86-93]()
- **Conditional edges**: Route based on current state rather than hardcoded transitions [langgraph_swarm/swarm.py:166]()

When a handoff tool returns a `Command` with `graph=Command.PARENT` [langgraph_swarm/handoff.py:88](), the command updates the parent swarm's state, not the individual agent's state. This is critical for maintaining the `active_agent` field at the swarm level.

**Sources:** [langgraph_swarm/swarm.py:166](), [langgraph_swarm/handoff.py:86-93]()

## Dependency Architecture

The library builds on two primary LangChain ecosystem packages:

```mermaid
graph TB
    subgraph "langgraph-swarm"
        Core["Core Modules<br/>swarm.py<br/>handoff.py"]
    end
    
    subgraph "LangGraph Dependencies"
        StateGraph["StateGraph<br/>Graph builder"]
        Pregel["Pregel<br/>Compiled graph type"]
        Command["Command<br/>Navigation & updates"]
        MessagesState["MessagesState<br/>Base state with messages"]
        START["START<br/>Entry node constant"]
    end
    
    subgraph "LangChain Dependencies"
        BaseTool["BaseTool<br/>Tool abstraction"]
        ToolMessage["ToolMessage<br/>Tool response messages"]
        Annotations["InjectedState<br/>InjectedToolCallId"]
    end
    
    Core -->|imports| StateGraph
    Core -->|imports| Pregel
    Core -->|imports| Command
    Core -->|imports| MessagesState
    Core -->|imports| START
    Core -->|imports| BaseTool
    Core -->|imports| ToolMessage
    Core -->|imports| Annotations
```

**LangGraph imports** [langgraph_swarm/swarm.py:6-7]():
- `StateGraph`: Graph construction API used in `create_swarm()`
- `Pregel`: Type annotation for compiled agents
- `MessagesState`: Base class for `SwarmState`
- `START`: Special node identifier for entry point routing

**LangChain imports** [langgraph_swarm/handoff.py:5-6]():
- `BaseTool`: Base class for all tools including handoff tools
- `ToolMessage`: Message type for tool execution results
- `InjectedState`, `InjectedToolCallId`: Annotations for runtime dependency injection

The library requires no direct LLM dependencies, as agents are provided as pre-compiled `Pregel` objects that already contain their model configurations.

**Sources:** [langgraph_swarm/swarm.py:1-11](), [langgraph_swarm/handoff.py:1-10]()

---

