<!-- source: DeepWiki mcp.deepwiki.com · repo openai/swarm · page 2 Core Implementation · fetched 2026-10-27 -->

# Core Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [README.md](README.md)

</details>



This document describes the core implementation of the OpenAI Swarm framework, which serves as the foundation for orchestrating AI agents and executing tasks. The core implementation provides essential components for managing agent interactions with the OpenAI API, handling tool calls, and maintaining shared context between agents.

## Architecture Overview

The core implementation consists of a small set of tightly integrated components that work together to provide a flexible framework for agent-based interactions.

```mermaid
flowchart TD
    subgraph "Core Swarm Framework"
        SwarmClass["Swarm Class"]
        Agent["Agent Type"]
        FunctionHandling["Function Handling"]
        ContextVars["Context Variables"]
        Utils["Utility Functions"]
    end

    SwarmClass -->|"orchestrates"| Agent
    SwarmClass -->|"executes"| FunctionHandling
    SwarmClass -->|"maintains"| ContextVars
    SwarmClass -->|"uses"| Utils
    FunctionHandling -->|"updates"| ContextVars
    FunctionHandling -->|"can change"| Agent

    subgraph "External Systems"
        OpenAI["OpenAI API"]
    end

    SwarmClass -->|"calls"| OpenAI
```

Sources: [swarm/core.py:26-292](), [swarm/util.py:1-87]()

## Components

The Swarm implementation is divided into several specialized modules. For detailed technical specifications, please refer to the child pages linked below.

### Swarm Class (core.py)
The `Swarm` class is the primary entry point. It instantiates an `OpenAI` client and manages the `run` loop, which handles the iterative process of getting completions, executing tools, and switching agents. 
- For details, see [Swarm Class (core.py)](#2.1).

Sources: [swarm/core.py:26-30](), [swarm/core.py:139-292]()

### Types and Data Models
Swarm uses Pydantic models to ensure type safety and consistent data structures. The primary models include `Agent`, `Response`, and `Result`.
- For details, see [Types and Data Models](#2.2).

Sources: [swarm/types.py:1-49]()

### Utility Functions
The `util.py` module contains internal helpers for transforming Python code into API-compatible formats, such as converting function signatures into JSON schemas and merging streaming chunks.
- For details, see [Utility Functions](#2.3).

Sources: [swarm/util.py:1-87]()

### REPL and Demo Loop
To facilitate testing and rapid prototyping, Swarm includes a REPL (Read-Eval-Print Loop) in `swarm/repl`. This allows developers to interact with agents in a terminal environment.
- For details, see [REPL and Demo Loop](#2.4).

Sources: [swarm/repl/repl.py:1-105]()

## Execution Flow

The core execution flow is implemented in the `run` method (and its streaming counterpart `run_and_stream`). This flow orchestrates the interaction between agents, the OpenAI API, and function calls.

```mermaid
flowchart TB
    Start["Start run()"] --> InitializeState["Initialize state:\n- active_agent\n- context_variables\n- history"]
    InitializeState --> MaxTurnsCheck["Check if max_turns reached"]
    MaxTurnsCheck -- "Not reached" --> GetCompletion["Get chat completion\nfrom OpenAI API"]
    MaxTurnsCheck -- "Reached" --> ReturnResponse["Return Response"]
    
    GetCompletion --> AddToHistory["Add message to history"]
    AddToHistory --> ToolCallsCheck["Check for tool_calls"]
    
    ToolCallsCheck -- "No tool calls\nor execute_tools=False" --> ReturnResponse
    ToolCallsCheck -- "Has tool calls" --> HandleToolCalls["Handle tool calls"]
    
    HandleToolCalls --> ProcessResults["Process function results"]
    ProcessResults --> UpdateContext["Update context variables"]
    UpdateContext --> AgentSwitchCheck["Check for agent switch"]
    
    AgentSwitchCheck -- "New agent returned" --> UpdateAgent["Update active_agent"]
    AgentSwitchCheck -- "No new agent" --> MaxTurnsCheck
    UpdateAgent --> MaxTurnsCheck
    
    ReturnResponse --> End["End"]
```

Sources: [swarm/core.py:231-292](), [swarm/core.py:139-229]()

## Bridge: Natural Language to Code Entities

The following diagrams map conceptual multi-agent behaviors to specific entities in the codebase.

### Agent Definition Bridge
This diagram shows how natural language instructions and capabilities are mapped to the `Agent` class properties.

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        Direction["'You are a helpful assistant'"]
        Capability["'Can check weather'"]
        Handoff["'Transfer to Sales'"]
    end

    subgraph "Code Entity Space (types.py)"
        AgentObj["Agent (class)"]
        AgentObj -- "instructions" --> Direction
        AgentObj -- "functions" --> Capability
        AgentObj -- "functions" --> Handoff
    end
```

Sources: [swarm/types.py:13-21]()

### Tool Execution Bridge
This diagram shows how a model's intent to use a tool is translated into a Python function call within `core.py`.

```mermaid
flowchart TD
    subgraph "Model Intent (OpenAI API)"
        TC["tool_calls: {name: 'get_weather', args: {...}}"]
    end

    subgraph "Code Execution (core.py)"
        Htc["handle_tool_calls()"]
        Fmap["function_map"]
        Exec["func(**args)"]
    end

    TC --> Htc
    Htc --> Fmap
    Fmap --> Exec
```

Sources: [swarm/core.py:89-137]()

## Integration with OpenAI API

The core implementation is tightly integrated with the OpenAI API, using its chat completions and function calling capabilities:

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant Swarm as "Swarm Class"
    participant OpenAI as "OpenAI API"
    participant Functions as "Agent Functions"
    
    Client->>Swarm: run(agent, messages, ...)
    activate Swarm
    
    loop Until completion or max_turns
        Swarm->>OpenAI: chat.completions.create(...)
        activate OpenAI
        OpenAI-->>Swarm: Completion with tool_calls
        deactivate OpenAI
        
        alt Has tool_calls
            loop For each tool_call
                Swarm->>Functions: Execute function
                activate Functions
                Functions-->>Swarm: Function result
                deactivate Functions
                
                Swarm->>Swarm: handle_function_result()
                
                alt Result is new Agent
                    Swarm->>Swarm: Switch active agent
                end
            end
        end
    end
    
    Swarm-->>Client: Response(messages, agent, context_variables)
    deactivate Swarm
```

Sources: [swarm/core.py:32-69](), [swarm/core.py:231-292]()

---

