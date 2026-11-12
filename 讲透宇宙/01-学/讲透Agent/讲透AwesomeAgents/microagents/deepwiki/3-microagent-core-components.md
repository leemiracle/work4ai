<!-- source: DeepWiki mcp.deepwiki.com · repo aymenfurter/microagents · page 3 MicroAgent Core Components · fetched 2026-10-26 -->

# MicroAgent Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/agent_evaluation.py](agents/agent_evaluation.py)
- [agents/agent_similarity.py](agents/agent_similarity.py)
- [agents/microagent.py](agents/microagent.py)

</details>



This page documents the core components of the MicroAgent system, which form the foundation of the agent's functionality. The MicroAgent components handle response generation, agent evaluation, prompt evolution, and related functionality that enables microagents to process user queries and generate appropriate responses. For information about the overall system architecture, see [System Architecture](#2).

## MicroAgent Class Overview

The `MicroAgent` class serves as the central component in the microagents system. It encapsulates the behavior of small, purpose-driven agents that interact with the OpenAI API to process requests and generate responses.

```mermaid
classDiagram
    class MicroAgent {
        +String dynamic_prompt
        +String purpose
        +Array purpose_embedding
        +Int depth
        +Int max_depth
        +Int usage_count
        +Boolean working_agent
        +Int evolve_count
        +Int number_of_code_executions
        +String current_status
        +Dict active_agents
        +String last_input
        +String last_output
        +String last_conversation
        +Boolean stopped
        +Boolean is_prime
        +Boolean stop_execution
        +respond(input_text, evolve_count)
        +update_status(status)
        +update_active_agents(calling_agent, called_agent)
        +set_agent_as_working()
        +get_children()
        +is_working_agent()
        +set_agent_deleted()
        +check_for_stopped()
        +stop()
        +reset()
    }
    
    MicroAgent *-- "1" AgentEvaluator : uses
    MicroAgent *-- "1" CodeExecution : uses
    MicroAgent *-- "1" AgentResponse : uses
    MicroAgent *-- "1" AgentSimilarity : uses
    MicroAgent *-- "1" PromptEvolution : uses
    MicroAgent *-- "1" ResponseExtraction : uses
    MicroAgent *-- "1" ResponseHandler : uses
    
    class AgentEvaluator {
        +evaluate(input_text, prompt, output)
    }
    
    class CodeExecution {
        +execute_code()
    }
    
    class AgentResponse {
        +generate_response()
    }
    
    class AgentSimilarity {
        +get_embedding()
        +calculate_similarity_threshold()
        +find_closest_agent()
    }
    
    class PromptEvolution {
        +evolve_prompt()
    }
    
    class ResponseExtraction {
        +extract_response()
    }
    
    class ResponseHandler {
        +respond()
    }
```

Sources: [agents/microagent.py:17-138]()

## MicroAgent Initialization and Dependencies

The `MicroAgent` class is initialized with various parameters and dependencies that determine its behavior:

```mermaid
graph TD
    subgraph "MicroAgent Constructor"
        A["MicroAgent.__init__"] --> B["Set basic properties"]
        B --> C["Set ID"]
        C --> D["Initialize components"]
    end
    
    subgraph "Basic Properties"
        B --> B1["dynamic_prompt"]
        B --> B2["purpose"]
        B --> B3["depth"]
        B --> B4["max_depth"]
        B --> B5["agent_lifecycle"]
        B --> B6["openai_wrapper"]
    end
    
    subgraph "Component Initialization"
        D --> D1["agent_evaluator"]
        D --> D2["code_executor"]
        D --> D3["agent_responder"]
        D --> D4["agent_similarity"]
        D --> D5["prompt_evolver"]
        D --> D6["response_extractor"]
        D --> D7["response_handler"]
    end
```

The MicroAgent constructor initializes:
1. Basic agent properties (purpose, depth, etc.)
2. Relationships (parent, prime agent status)
3. State tracking variables (usage count, status)
4. Core component instances that provide the agent's functionality

Sources: [agents/microagent.py:23-68]()

## Core Components and Their Functions

### 1. ResponseHandler

The `ResponseHandler` is the primary interface for generating responses to user inputs. It coordinates the response generation process, including evaluation, potential prompt evolution, and delegation to other agents when necessary.

When the `MicroAgent.respond()` method is called, it delegates to the `ResponseHandler.respond()` method, which manages the complete response generation flow.

Sources: [agents/microagent.py:114-118]()

### 2. AgentEvaluator

The `AgentEvaluator` assesses the quality of agent responses using OpenAI's model. It provides a critical feedback mechanism that helps determine if responses meet quality standards.

```mermaid
sequenceDiagram
    participant Agent as MicroAgent
    participant Evaluator as AgentEvaluator
    participant OpenAI as OpenAIWrapper
    
    Agent->>Evaluator: evaluate(input_text, prompt, output)
    Evaluator->>Evaluator: format evaluation prompt
    Evaluator->>OpenAI: chat_completion(evaluation_prompt)
    OpenAI-->>Evaluator: response
    Evaluator->>Evaluator: analyze score (1-5)
    Evaluator-->>Agent: True/False (pass/fail)
```

The evaluator uses a specific evaluation prompt template (`AGENT_EVALUATION_PROMPT`) to request a 1-5 score from the LLM, considering scores of 4-5 as passing and others as failing.

Sources: [agents/agent_evaluation.py:7-30]()

### 3. AgentSimilarity

The `AgentSimilarity` component calculates embeddings and similarity scores between agent purposes, enabling:
1. Finding similar agents for potential reuse
2. Avoiding duplication of agent functionality
3. Maintaining diversity among agents

```mermaid
classDiagram
    class AgentSimilarity {
        +OpenAIAPIWrapper openai_wrapper
        +List~Agent~ agents
        +get_embedding(text)
        +calculate_similarity_threshold()
        +find_closest_agent(purpose_embedding)
    }
    
    class Agent {
        +String purpose
        +Array purpose_embedding
    }
    
    AgentSimilarity --> "many" Agent : analyzes
```

The component uses cosine similarity between embedding vectors to determine how closely related agent purposes are.

Sources: [agents/agent_similarity.py:15-93]()

### 4. PromptEvolution

The `PromptEvolution` component helps improve prompts when responses don't meet quality standards. It uses the OpenAI API to generate improved prompts based on feedback from failed responses.

### 5. ResponseExtraction

The `ResponseExtraction` component parses and extracts structured information from the LLM's responses, making it easier to process and use the outputs.

### 6. AgentResponse

The `AgentResponse` component handles the actual generation of responses by interfacing with the OpenAI API. It's responsible for:
1. Formatting the prompt with the user's input
2. Sending requests to the API
3. Processing the raw responses
4. Handling special cases like code execution or agent delegation

### 7. CodeExecution

The `CodeExecution` component enables agents to execute code snippets included in responses, providing computational capabilities beyond text generation.

## Component Interaction Flow

The following diagram illustrates how these components interact during the response generation process:

```mermaid
graph TD
    subgraph "Response Generation Flow"
        A["User Input"] --> B["MicroAgent.respond()"]
        B --> C["ResponseHandler.respond()"]
        C --> D{"Response quality sufficient?"}
        D -->|"Yes"| E["Return Response"]
        D -->|"No"| F["PromptEvolution.evolve_prompt()"]
        F --> G["Try again with improved prompt"]
        G --> C
    end
    
    subgraph "Response Handler Process"
        C --> C1["AgentResponse.generate_response()"]
        C1 --> C2{"Contains code?"}
        C2 -->|"Yes"| C3["CodeExecution.execute_code()"]
        C2 -->|"No"| C4{"Contains agent delegation?"}
        C4 -->|"Yes"| C5["Create and run child agent"]
        C3 --> C6["Continue processing"]
        C4 -->|"No"| C6
        C5 --> C6
        C6 --> D
    end
    
    subgraph "Evaluation Process"
        D --> D1["AgentEvaluator.evaluate()"]
        D1 --> D2["OpenAI API call"]
        D2 --> D3["Score assessment"]
        D3 --> D
    end
```

Sources: [agents/microagent.py:114-118](), [agents/agent_evaluation.py:15-30]()

## Agent State Management

MicroAgent includes capabilities for tracking and managing agent state:

1. **Status Updates**: The `update_status()` method maintains the current status of the agent, which can be used for monitoring and debugging.

2. **Active Agent Tracking**: The `update_active_agents()` method maintains a record of agent delegation, tracking which agents have delegated to others.

3. **Agent Lifecycle Control**: Methods like `set_agent_as_working()`, `set_agent_deleted()`, and `stop()` control the agent's lifecycle.

4. **Stop Checking**: The `check_for_stopped()` method verifies if the agent has been stopped, raising an exception if so to halt processing.

Sources: [agents/microagent.py:70-130]()

## Agent Similarity Calculation

The similarity mechanism is crucial for agent reuse and specialization:

```mermaid
sequenceDiagram
    participant Consumer as "Consumer"
    participant AS as "AgentSimilarity"
    participant OpenAI as "OpenAIWrapper"
    
    Consumer->>AS: find_closest_agent(purpose_embedding)
    loop For each agent
        alt Agent has no embedding
            AS->>OpenAI: get_embedding(agent.purpose)
            OpenAI-->>AS: purpose_embedding
        end
        AS->>AS: Calculate cosine similarity
        AS->>AS: Track highest similarity
    end
    AS-->>Consumer: closest_agent, similarity_score
```

The similarity threshold calculation works by:
1. Collecting embeddings for all agents
2. Computing pairwise similarities
3. Finding the 98th percentile of similarity scores
4. Using this as a threshold to determine if a new agent is needed

For smaller agent collections (<250 agents), a fixed high threshold (0.999) is used to encourage agent creation.

Sources: [agents/agent_similarity.py:45-66](), [agents/agent_similarity.py:69-93]()

## MicroAgent Response Process

When a user request comes in, the complete response process follows this flow:

```mermaid
graph TD
    A["User Input"] --> B["MicroAgent.respond()"]
    B --> C["ResponseHandler.respond()"]
    C --> D["AgentResponse.generate_response()"]
    D --> E["OpenAIWrapper.chat_completion()"]
    E --> F["Process LLM Response"]
    F --> G{"Response contains code?"}
    G -->|"Yes"| H["CodeExecution.execute_code()"]
    G -->|"No"| I{"Response indicates agent delegation?"}
    I -->|"Yes"| J["Create child agent or find similar existing agent"]
    I -->|"No"| K["Process standard text response"]
    H --> L["Combine code outputs with response"]
    J --> M["Get delegated agent response"]
    K --> N["Final Response"]
    L --> N
    M --> N
    N --> O["AgentEvaluator.evaluate()"]
    O --> P{"Evaluation passes?"}
    P -->|"Yes"| Q["Return Response to User"]
    P -->|"No"| R["PromptEvolution.evolve_prompt()"]
    R --> S["Try again with improved prompt"]
    S --> C
```

This process demonstrates how the various components work together to generate, evaluate, and potentially improve responses to user inputs.

Sources: [agents/microagent.py:114-118]()

---

