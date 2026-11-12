<!-- source: DeepWiki mcp.deepwiki.com · repo mikekelly/AgentK · page 3 Agents · fetched 2026-10-26 -->

# Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [agents/hermes.py](agents/hermes.py)
- [utils.py](utils.py)

</details>



This page provides an overview of the agent system in AgentK, explaining how agents are structured, loaded, and interact with each other. For information on specific agents such as Hermes or AgentSmith, see their dedicated pages ([Hermes: Orchestrator](#3.1), [AgentSmith: Agent Creator](#3.2), etc.). For information on creating new agents, see the [Creating New Agents](#7.1) guide.

## What are Agents in AgentK?

Agents in AgentK form the cognitive components of its modular, self-evolving architecture. Each agent is a specialized entity with specific capabilities and responsibilities, implemented as a Python module with a defined interface. Together, these agents collaborate to solve problems and complete tasks, dynamically creating new agents when needed.

```mermaid
graph TD
    User(("User"))
    
    subgraph "AgentK System"
        Kernel["Agent Kernel"]
        Agents["Agent Registry"]
        Tools["Tool Registry"]
        
        subgraph "Agent Instances"
            Hermes["hermes<br>Orchestrator"]
            AgentSmith["agent_smith<br>Agent Creator"]
            ToolMaker["tool_maker<br>Tool Creator"]
            WebResearcher["web_researcher<br>Knowledge Gatherer"]
            TaskAgents["Task-Specific Agents"]
        end
    end
    
    User <--> Hermes
    Kernel --> Hermes
    Kernel --> Agents
    Agents --> AgentSmith
    Agents --> ToolMaker
    Agents --> WebResearcher
    Agents --> TaskAgents
    AgentSmith -->|creates| TaskAgents
    
    Agents -.->|registers| AgentSmith
    Agents -.->|registers| ToolMaker
    Agents -.->|registers| WebResearcher
    Agents -.->|registers| TaskAgents
```

Diagram: Agent System Overview

Sources: [README.md:15-27](), [utils.py:56-99]()

## Agent Architecture

Each agent in AgentK is typically implemented as a LangGraph workflow following the ReAct (Reasoning and Action) pattern. This architecture allows agents to alternate between reasoning about problems and taking actions through tools.

```mermaid
graph TD
    Start(["Start Agent"]) --> Init["Initialize State"]
    Init --> Reasoning["Reasoning Phase<br>Analyze situation & plan"]
    Reasoning --> ToolCheck{"Need to use tools?"}
    ToolCheck -->|"Yes"| ToolExecution["Tool Execution Phase<br>Perform actions"]
    ToolExecution --> Reasoning
    ToolCheck -->|"No"| Response["Response Phase<br>Return results"]
    Response --> End(["End Agent"])
    
    subgraph "Agent Module Components"
        SystemPrompt["System Prompt<br>Defines agent role & capabilities"]
        ToolDefinitions["Tool Definitions<br>Tools available to agent"]
        WorkflowDefinition["Workflow Definition<br>LangGraph state machine"]
        EntryFunction["Entry Function<br>Agent's callable interface"]
    end
```

Diagram: Typical Agent Implementation Structure

Sources: [agents/hermes.py:10-120]()

Most agents follow a standard structure:
1. A system prompt defining the agent's role and capabilities
2. A set of tools available to the agent
3. A LangGraph workflow defining the agent's behavior
4. An entry function that serves as the callable interface

## Agent Registry and Loading

The AgentK system maintains a registry of available agents, allowing dynamic discovery, loading, and invocation of agent functionality. Agents are stored as Python files in the `agents/` directory and loaded on demand.

```mermaid
sequenceDiagram
    participant "AgentK System" as System
    participant "utils.py" as Utils
    participant "File System" as FS
    participant "Agent Module" as Agent
    
    System->>Utils: list_agents()
    Utils->>FS: Read agents directory
    FS-->>Utils: Return .py files
    Utils-->>System: Return agent names
    
    System->>Utils: all_agents()
    Utils->>Utils: list_agents()
    
    loop For each agent
        Utils->>Utils: load_module("agents/{agent}.py")
        Utils->>Agent: Import module
        Agent-->>Utils: Return agent function
        Utils->>Agent: Extract docstring
        Agent-->>Utils: Return docstring
    end
    
    Utils-->>System: Return {agent: docstring} dictionary
```

Diagram: Agent Loading Process

Sources: [utils.py:56-130]()

The key utility functions for agent management include:

| Function | Purpose | Location |
|----------|---------|----------|
| `list_agents()` | Lists all agent files in the agents directory | [utils.py:87-99]() |
| `all_agents()` | Loads all agent modules and extracts docstrings | [utils.py:56-70]() |
| `load_module()` | Dynamically loads a Python module from a file | [utils.py:113-130]() |
| `list_broken_agents()` | Identifies agents that fail to load properly | [utils.py:72-85]() |

## Core Kernel Agents

AgentK's architecture is built around a minimal "kernel" of four core agents that enable the system to bootstrap itself and grow its capabilities:

```mermaid
graph TD
    subgraph "Kernel Agents"
        Hermes["hermes<br>Orchestration & User Interaction"]
        AgentSmith["agent_smith<br>Agent Creation & Management"]
        ToolMaker["tool_maker<br>Tool Creation & Testing"]
        WebResearcher["web_researcher<br>Knowledge Acquisition"]
    end
    
    subgraph "AgentK System"
        TaskAgents["Task-Specific Agents"]
        Tools["System Tools"]
        Knowledge["Knowledge Base"]
    end
    
    Hermes -->|"coordinates"| AgentSmith
    Hermes -->|"coordinates"| ToolMaker
    Hermes -->|"coordinates"| WebResearcher
    Hermes -->|"assigns tasks to"| TaskAgents
    
    AgentSmith -->|"creates & maintains"| TaskAgents
    ToolMaker -->|"creates & maintains"| Tools
    WebResearcher -->|"gathers & updates"| Knowledge
    
    TaskAgents -->|"use"| Tools
    TaskAgents -->|"leverage"| Knowledge
```

Diagram: Core Kernel Agent Relationships

Sources: [README.md:22-27](), [agents/hermes.py:13-29]()

Each kernel agent has a specific role:

1. **Hermes**: The orchestrator that interacts with humans, plans tasks, and coordinates other agents
2. **AgentSmith**: Creates and manages other agents, ensuring they have necessary tools
3. **ToolMaker**: Develops tools needed by agents to interact with the system and external world
4. **WebResearcher**: Gathers knowledge from online sources to support agent operations

For detailed information on each kernel agent, see their dedicated wiki pages ([Hermes: Orchestrator](#3.1), [AgentSmith: Agent Creator](#3.2), [ToolMaker: Tool Creator](#3.3), [WebResearcher: Knowledge Gatherer](#3.4)).

## Agent Interaction Patterns

Agents in AgentK collaborate through an orchestration pattern, with Hermes coordinating tasks and delegating to specialized agents. This interaction typically follows a hierarchical structure.

```mermaid
sequenceDiagram
    actor User
    participant Hermes
    participant SpecializedAgent
    participant AgentSmith
    participant NewAgent
    
    User->>Hermes: Submit task/goal
    Hermes->>Hermes: Analyze task requirements
    
    alt Existing agent can handle task
        Hermes->>SpecializedAgent: Assign task
        SpecializedAgent->>SpecializedAgent: Process task
        SpecializedAgent-->>Hermes: Return results
    else New agent needed
        Hermes->>AgentSmith: Request new agent creation
        AgentSmith->>AgentSmith: Design & implement new agent
        AgentSmith-->>Hermes: Confirm agent creation
        Hermes->>NewAgent: Assign task
        NewAgent->>NewAgent: Process task
        NewAgent-->>Hermes: Return results
    end
    
    Hermes->>User: Present results
```

Diagram: Agent Interaction Flow

Sources: [agents/hermes.py:30-36](), [README.md:5]()

Key aspects of agent interaction:

1. **Task Orchestration**: Hermes acts as the central coordinator, breaking down user goals into subtasks
2. **Task Assignment**: Tasks are assigned to specialized agents based on their capabilities
3. **Agent Creation**: When no existing agent can handle a task, AgentSmith creates a new specialized agent
4. **Result Aggregation**: Results from various agents are collected and synthesized by Hermes

The interaction is facilitated by specific tools:
- `list_available_agents`: Returns a list of all available agents and their capabilities
- `assign_agent_to_task`: Delegates a specific task to an agent and returns the results

Sources: [agents/hermes.py:10-11](), [agents/hermes.py:46]()

## The Agent Implementation Pattern

Agents in AgentK typically follow the LangGraph ReAct pattern, with a standard structure for their implementation. The example below shows the implementation pattern from the Hermes agent:

```mermaid
graph TD
    Entry["Entry Function (hermes)"]
    
    subgraph "State Graph Components"
        Initialize["Initialize MessagesState<br>with System Prompt"]
        HumanInput["feedback_and_wait_on_human_input<br>Get user input"]
        ExitCheck["check_for_exit<br>Check for exit command"]
        Reasoning["reasoning<br>Agent thinks about task"]
        ToolCheck["check_for_tool_calls<br>Check if tools needed"]
        ToolExecution["ToolNode<br>Execute requested tools"]
    end
    
    Entry --> Initialize
    Initialize --> HumanInput
    HumanInput --> ExitCheck
    ExitCheck -->|"continue"| Reasoning
    ExitCheck -->|"exit"| End(["End"])
    Reasoning --> ToolCheck
    ToolCheck -->|"tool calls present"| ToolExecution
    ToolCheck -->|"no tool calls"| HumanInput
    ToolExecution --> Reasoning
```

Diagram: LangGraph Agent Implementation Pattern

Sources: [agents/hermes.py:46-110]()

The implementation typically includes:

1. **System Prompt**: Defines the agent's role, capabilities, and operating instructions
2. **Tool Definitions**: Lists the tools available to the agent
3. **State Handler Functions**: Process different states in the agent's workflow
4. **Workflow Definition**: Defines the state graph using LangGraph's StateGraph
5. **Entry Function**: Provides the callable interface for the agent

This pattern enables agents to:
- Reason about problems and plan solutions
- Use tools to interact with the system and external world
- Maintain conversation context and state
- Operate autonomously within their domain of expertise

## Conclusion

Agents form the cognitive core of AgentK, working collaboratively to achieve user goals through specialized capabilities and dynamic creation of new agents. The modular agent architecture, centered around a minimal kernel, allows the system to continuously evolve and extend its capabilities. The LangGraph ReAct pattern provides a consistent implementation approach across agents, enabling reasoning, tool usage, and effective task completion.

For details on individual agents, see their dedicated wiki pages. For information on creating new agents, see the [Creating New Agents](#7.1) guide.

Sources: [README.md:5-28](), [agents/hermes.py:1-120](), [utils.py:56-130]()

---

