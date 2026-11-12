<!-- source: DeepWiki mcp.deepwiki.com · repo aymenfurter/microagents · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/microagent.py](agents/microagent.py)
- [agents/microagent_manager.py](agents/microagent_manager.py)
- [main.py](main.py)

</details>



This document provides a technical overview of the Microagents system architecture, explaining the core components, their interactions, data flow patterns, and the mechanisms that enable dynamic creation and management of specialized AI agents. For details on how agents communicate hierarchically, see [Agent Hierarchy and Communication](#2.1). For information about the complete agent lifecycle, refer to [Agent Lifecycle](#2.2).

## High-Level System Overview

The Microagents system follows a modular architecture designed to dynamically create, manage, and improve purpose-specific AI agents. These agents collaborate to solve complex problems by delegating tasks to specialized sub-agents.

```mermaid
graph TD
    User["User"] -->|"Tasks/Questions"| Interfaces
    
    subgraph "User Interfaces"
        Interfaces --> GradioUI["GradioUI"]
        Interfaces --> TextualUI["CLI Interface"]
    end
    
    GradioUI --> MAM["MicroAgentManager"]
    TextualUI --> MAM
    
    subgraph "Agent Management Layer"
        MAM --> AL["AgentLifecycle"]
        MAM --> APM["AgentPersistenceManager"]
        AL -->|"Creates/Manages"| MA["MicroAgent"]
        APM -->|"Persists"| DB[("agents.db")]
    end
    
    subgraph "Agent Core Components"
        MA --> RH["ResponseHandler"]
        MA --> AE["AgentEvaluator"]
        MA --> PE["PromptEvolution"]
        RH --> AR["AgentResponse"]
        RH --> RE["ResponseExtraction"]
        RH --> PAE["ParallelAgentExecutor"]
    end
    
    subgraph "External Services"
        MA --> OAW["OpenAIWrapper"]
        AR --> OAW
        AE --> OAW
        PE --> OAW
        OAW -->|"API Calls"| OpenAI["OpenAI/Azure API"]
    end
```

Sources: [main.py:67-73](), [agents/microagent_manager.py:11-27](), [agents/microagent.py:17-68]()

## Core Components and Relationships

The system architecture consists of the following key components:

### 1. MicroAgentManager

The central coordinator that manages agent creation, retrieval, and lifecycle. It maintains the agent inventory and provides interfaces for the UI layer.

```mermaid
classDiagram
    class MicroAgentManager {
        -max_agents: int
        -openai_wrapper: OpenAIAPIWrapper
        -agent_persistence: AgentPersistenceManager
        -agent_lifecycle: AgentLifecycle
        +stop_all_agents()
        +cleanup_agents()
        +load_agents()
        +get_agents()
        +create_agents()
        +get_or_create_agent(purpose, depth, sample_input, parent_agent)
        +display_agent_status()
        +display_active_agent_tree()
    }

    class AgentLifecycle {
        -agents: List[MicroAgent]
        -openai_wrapper: OpenAIAPIWrapper
        -persistence_manager: AgentPersistenceManager
        -max_agents: int
        +create_prime_agent()
        +get_or_create_agent()
        +stop_all_agents()
        +cleanup_agents()
        +reset_all_agents()
    }

    class AgentPersistenceManager {
        -db_filename: str
        +save_agent(agent)
        +load_agent(agent_id)
        +load_all_agents()
        +delete_agent(agent_id)
    }

    MicroAgentManager --> AgentLifecycle : uses
    MicroAgentManager --> AgentPersistenceManager : uses
    AgentLifecycle --> AgentPersistenceManager : uses
```

Sources: [agents/microagent_manager.py:11-78]()

### 2. MicroAgent

The core agent class that represents individual AI agents with specific purposes. Each agent can generate responses, execute code, and delegate tasks to other agents.

```mermaid
classDiagram
    class MicroAgent {
        -dynamic_prompt: str
        -purpose: str
        -purpose_embedding: vector
        -depth: int
        -max_depth: int
        -usage_count: int
        -working_agent: bool
        -evolve_count: int
        -current_status: str
        -active_agents: dict
        -stopped: bool
        -is_prime: bool
        -id: str
        +update_status(status)
        +update_active_agents(calling_agent, called_agent)
        +set_agent_as_working()
        +get_children()
        +is_working_agent()
        +set_agent_deleted()
        +check_for_stopped()
        +respond(input_text, evolve_count)
        +stop()
        +reset()
    }

    class ResponseHandler {
        -agent: MicroAgent
        +respond(input_text, evolve_count)
    }

    class AgentEvaluator {
        -openai_wrapper: OpenAIAPIWrapper
        +evaluate_response(response, query)
    }

    class PromptEvolution {
        -openai_wrapper: OpenAIAPIWrapper
        -agent_lifecycle: AgentLifecycle
        +evolve_prompt(original_prompt, input_text, failed_response)
    }

    class AgentResponse {
        -openai_wrapper: OpenAIAPIWrapper
        -agent_lifecycle: AgentLifecycle
        -code_executor: CodeExecution
        -parent_agent: MicroAgent
        +generate_response(query, prompt)
    }

    MicroAgent --> ResponseHandler : uses
    MicroAgent --> AgentEvaluator : uses
    MicroAgent --> PromptEvolution : uses
    MicroAgent --> AgentResponse : uses
```

Sources: [agents/microagent.py:17-138]()

### 3. Integration Layer

The system integrates with external services, primarily OpenAI's API, through the OpenAIWrapper class.

```mermaid
sequenceDiagram
    participant MA as MicroAgent
    participant RH as ResponseHandler
    participant AR as AgentResponse
    participant OAW as OpenAIAPIWrapper
    participant OpenAI as OpenAI/Azure API
    
    MA->>RH: respond(input_text)
    RH->>AR: generate_response(query, prompt)
    AR->>OAW: chat_completion(prompt)
    OAW->>OpenAI: API request
    OpenAI-->>OAW: API response
    OAW-->>AR: Processed response
    AR-->>RH: Response with extracted info
    RH-->>MA: Final response
```

Sources: [main.py:96-98](), [agents/microagent.py:62-68]()

## Request Processing Flow

The system processes user requests through a defined flow that enables dynamic agent creation, delegation, and response generation.

```mermaid
flowchart TD
    Start["User Input"] --> MAM["MicroAgentManager.process_user_input()"]
    MAM --> GetOrCreate["get_or_create_agent('Bootstrap Agent')"]
    GetOrCreate --> MA["MicroAgent.respond()"]
    MA --> RH["ResponseHandler.respond()"]
    RH --> AR["AgentResponse.generate_response()"]
    AR --> OAI["OpenAIWrapper.chat_completion()"]
    OAI --> Response["Process API Response"]
    
    Response --> HasCode{"Contains\nCode?"}
    HasCode -->|"Yes"| ExecCode["Execute Code"]
    ExecCode --> ResultEval["Evaluate Result"]
    
    Response --> HasAgent{"Contains Agent\nInvocation?"}
    HasAgent -->|"Yes"| CreateAgent["Create New Agent"]
    CreateAgent --> DelegateTask["Delegate Task"]
    DelegateTask --> AgentResponse["Get Agent Response"]
    AgentResponse --> ResultEval
    
    HasCode -->|"No"| ResultEval
    HasAgent -->|"No"| ResultEval
    
    ResultEval --> IsGood{"Good\nResponse?"}
    IsGood -->|"No"| EvolvePrompt["Evolve Prompt"]
    EvolvePrompt --> RH
    
    IsGood -->|"Yes"| FinalResult["Return Final Result"]
    FinalResult --> End["End"]
```

Sources: [main.py:75-81](), [agents/microagent.py:114-118]()

## Agent Creation and Management

The system creates and manages agents dynamically based on task requirements, with a focus on agent reuse when appropriate.

```mermaid
sequenceDiagram
    participant User
    participant MAM as MicroAgentManager
    participant AL as AgentLifecycle
    participant AS as AgentSimilarity
    participant MA as MicroAgent
    participant DB as AgentPersistenceManager
    
    User->>MAM: process_user_input(query)
    MAM->>AL: get_or_create_agent(purpose, depth, sample_input)
    AL->>AS: find_similar_agent(purpose, sample_input)
    
    alt Similar agent exists
        AS-->>AL: existing_agent
        AL-->>MAM: existing_agent
    else No similar agent
        AL->>MA: create new MicroAgent(purpose, depth)
        MA-->>AL: new_agent
        AL->>DB: save_agent(new_agent)
        AL-->>MAM: new_agent
    end
    
    MAM-->>User: agent.respond(query)
```

Sources: [agents/microagent_manager.py:53-64](), [main.py:67-73](), [main.py:75-81]()

## Data Persistence

The system persists agents in a SQLite database to enable reuse across sessions.

```mermaid
graph TD
    MAM["MicroAgentManager"] --> APM["AgentPersistenceManager"]
    APM -->|"save_agent()"| DB[("agents.db")]
    APM -->|"load_agent()"| DB
    APM -->|"load_all_agents()"| DB
    APM -->|"delete_agent()"| DB
```

Sources: [agents/microagent_manager.py:31-36]()

## Technical Implementation Details

The MicroAgents system is implemented in Python with key dependencies including:

1. **OpenAI API Integration**: The system communicates with OpenAI/Azure OpenAI APIs through the `OpenAIAPIWrapper` class.

2. **SQLite Database**: Agent persistence is handled through a SQLite database named `agents.db` by default.

3. **User Interfaces**: Two interfaces are available:
   - Gradio-based web interface
   - Command-line interface

4. **Environment Configuration**: System configuration is managed through environment variables, loaded via dotenv.

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| MICROAGENTS_DB_FILENAME | Database filename for agent persistence | agents.db |
| OPENAI_API_KEY | OpenAI API key | - |
| AZURE_OPENAI_API_KEY | Azure OpenAI API key (alternative) | - |

Sources: [main.py:1-8](), [agents/microagent_manager.py:16]()

## Initialization and Startup Process

The system initialization follows these steps:

1. Load environment variables
2. Configure and initialize the OpenAI wrapper
3. Initialize the MicroAgentManager
4. Create the prime agent (Bootstrap Agent)
5. Start the user interface (CLI or Gradio)

```mermaid
sequenceDiagram
    participant Main
    participant OAIWrapper as OpenAIWrapper
    participant MAM as MicroAgentManager
    participant AL as AgentLifecycle
    participant DB as AgentPersistenceManager
    
    Main->>Main: load_dotenv()
    Main->>OAIWrapper: get_configured_openai_wrapper()
    Main->>MAM: initialize_manager(openai_wrapper)
    MAM->>DB: Initialize AgentPersistenceManager
    MAM->>AL: Initialize AgentLifecycle
    MAM->>MAM: load_agents()
    MAM->>MAM: create_agents()
    MAM->>AL: create_prime_agent()
    Main->>Main: Start UI (CLI or Gradio)
```

Sources: [main.py:92-104](), [main.py:67-73]()

## Conclusion

The Microagents system architecture provides a flexible and extensible framework for creating, managing, and improving AI agents. The modular design allows for separation of concerns while enabling powerful agent capabilities like delegation, code execution, and self-improvement through prompt evolution.

The system supports both simple and complex use cases, from answering basic factual questions to solving complex problems that require multi-step reasoning and specialized knowledge.

---

