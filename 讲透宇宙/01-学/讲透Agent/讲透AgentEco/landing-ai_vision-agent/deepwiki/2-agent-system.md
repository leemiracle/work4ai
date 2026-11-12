<!-- source: DeepWiki mcp.deepwiki.com · repo landing-ai/vision-agent · page 2 Agent System · fetched 2026-10-27 -->

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/chat/app.py](examples/chat/app.py)
- [vision_agent/agent/__init__.py](vision_agent/agent/__init__.py)
- [vision_agent/agent/agent.py](vision_agent/agent/agent.py)
- [vision_agent/agent/vision_agent_coder_v2.py](vision_agent/agent/vision_agent_coder_v2.py)
- [vision_agent/agent/vision_agent_prompts_v2.py](vision_agent/agent/vision_agent_prompts_v2.py)
- [vision_agent/agent/vision_agent_v2.py](vision_agent/agent/vision_agent_v2.py)

</details>



The Agent System is the core orchestration layer of the vision-agent framework. It manages the interaction between users, language models, code generation, and vision tools to create solutions for computer vision tasks. This document explains the architecture and components of the agent system, how they interact, and the workflow from user input to generated code execution.

For information on the available vision tools, see [Vision Tools](#3). For details on code execution, see [Code Execution System](#4).

## Architecture Overview

The Agent System is built around abstract base classes that define the core interfaces, with concrete implementations that provide the actual functionality. 

```mermaid
classDiagram
    class Agent {
        <<abstract>>
        +__call__(input, media) str
        +log_progress(data) None
    }
    
    class AgentCoder {
        <<abstract>>
        +generate_code(chat, max_steps, code_interpreter) CodeContext
        +generate_code_from_plan(chat, plan_context, code_interpreter) CodeContext
    }
    
    class AgentPlanner {
        <<abstract>>
        +generate_plan(chat, max_steps, code_interpreter) PlanContext
    }
    
    class VisionAgentV2 {
        -LMM agent
        -AgentCoder coder
        -bool hil
        -bool verbose
        +__call__(input, media) str
        +chat(chat, code_interpreter) List[AgentMessage]
    }
    
    class VisionAgentCoderV2 {
        -AgentPlanner planner
        -LMM coder
        -LMM tester
        -LMM debugger
        +generate_code(chat, max_steps, code_interpreter) CodeContext
        +generate_code_from_plan(chat, plan_context, code_interpreter) CodeContext
    }
    
    class VisionAgentPlannerV2 {
        -LMM planner
        -LMM summarizer
        -LMM critic
        +generate_plan(chat, max_steps, code_interpreter) PlanContext
    }
    
    Agent <|-- AgentCoder
    Agent <|-- AgentPlanner
    AgentCoder <|-- VisionAgentCoderV2
    AgentPlanner <|-- VisionAgentPlannerV2
    Agent <|-- VisionAgentV2
    VisionAgentV2 o-- VisionAgentCoderV2
    VisionAgentCoderV2 o-- VisionAgentPlannerV2
```

**Sources:**
- [vision_agent/agent/agent.py:16-61]()
- [vision_agent/agent/__init__.py:1-4]()
- [vision_agent/agent/vision_agent_v2.py:159-296]()
- [vision_agent/agent/vision_agent_coder_v2.py:291-509]()

## Core Components

### Agent Base Classes

The agent system is built on three key abstract base classes:

1. **Agent**: The root interface for all agents, defining the core method `__call__` for processing input.

2. **AgentCoder**: Extends Agent with code generation capabilities, defining methods for generating code from chat history or from a plan.

3. **AgentPlanner**: Extends Agent with planning capabilities, defining methods for generating execution plans.

Each of these abstract classes defines the interface contract that concrete implementations must adhere to.

**Sources:**
- [vision_agent/agent/agent.py:16-61]()

### VisionAgentV2

The `VisionAgentV2` class is the main entry point for user interaction with the system. It orchestrates the code generation process by:

1. Processing user input (text + images/videos)
2. Delegating to specialized components for planning and code generation
3. Managing the conversation flow
4. Executing generated code and returning results

```mermaid
flowchart TD
    User([User]) -->|"Prompt + Media"| VACall["VisionAgentV2.__call__()"]
    VACall -->|"Convert to AgentMessage"| VAChat["VisionAgentV2.chat()"]
    
    subgraph "VisionAgentV2.chat() Workflow"
        PrepareChat["Prepare Chat Context"]
        CheckInteraction["Check for Interaction"]
        RunConversation["Run Conversation with LLM"]
        ExtractAction["Extract Action"]
        RunAction["Run Action"]
        RunFinalConversation["Generate Final Response"]
    end
    
    VAChat --> PrepareChat
    PrepareChat --> CheckInteraction
    
    CheckInteraction -->|"Ongoing Interaction"| RunAction
    CheckInteraction -->|"No Interaction"| RunConversation
    
    RunConversation --> ExtractAction
    ExtractAction --> RunAction
    
    RunAction -->|"Completed Action"| RunFinalConversation
    RunAction -->|"Needs User Input"| ReturnInteraction["Return Interaction Request"]
    
    RunFinalConversation --> ReturnChat["Return Updated Chat"]
    ReturnInteraction --> User
    ReturnChat --> User
```

Key functionalities:
- Manages the conversation state
- Processes user messages and media
- Delegates to the coder agent for code generation
- Supports human-in-the-loop interaction when clarification is needed
- Uses callbacks to provide real-time updates during code generation

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:159-296]()
- [vision_agent/agent/vision_agent_prompts_v2.py:1-86]()

### VisionAgentCoderV2

The `VisionAgentCoderV2` class is responsible for generating, testing, and debugging vision code. It:

1. Uses a planner to generate a plan for solving the vision task
2. Generates code based on the plan
3. Tests the generated code using a code interpreter
4. Debugs and fixes code when there are issues

```mermaid
flowchart TB
    Input["Chat History + Media"] --> GenerateCode["generate_code()"]
    Plan["Plan Context"] --> GenerateCodeFromPlan["generate_code_from_plan()"]
    
    subgraph "Code Generation Process"
        GenPlan["Generate Plan"]
        RetrieveTools["Retrieve Relevant Tools"]
        WriteCode["Write Code"]
        TestCode["Test & Debug Code"]
        FormatResult["Format Result"]
    end
    
    GenerateCode --> GenPlan
    GenPlan -->|"Plan Context"| RetrieveTools
    GenerateCodeFromPlan --> RetrieveTools
    
    RetrieveTools --> WriteCode
    WriteCode --> TestCode
    TestCode -->|"Success"| FormatResult
    TestCode -->|"Failure"| DebugLoop["Debug Loop"]
    DebugLoop --> TestCode
    
    FormatResult --> CodeContext["Code Context"]
```

Key functionalities:
- Plan generation delegation to VisionAgentPlannerV2
- Tool recommendation and retrieval
- Code generation with language models
- Test generation and execution
- Automated debugging and fixing

**Sources:**
- [vision_agent/agent/vision_agent_coder_v2.py:291-509]()
- [vision_agent/agent/vision_agent_coder_v2.py:45-289]()

## Interaction and Execution Flow

The agent system processes requests through a series of well-defined steps:

```mermaid
sequenceDiagram
    participant User
    participant VisionAgentV2
    participant VisionAgentCoderV2
    participant VisionAgentPlannerV2
    participant CodeInterpreter
    participant LLM
    
    User->>VisionAgentV2: Prompt + Media
    
    VisionAgentV2->>LLM: Determine action
    LLM->>VisionAgentV2: Action decision
    
    alt generate_or_edit_vision_code
        VisionAgentV2->>VisionAgentCoderV2: generate_code(chat)
        VisionAgentCoderV2->>VisionAgentPlannerV2: generate_plan(chat)
        VisionAgentPlannerV2->>LLM: Request plan generation
        LLM->>VisionAgentPlannerV2: Plan
        
        VisionAgentCoderV2->>LLM: Generate code
        LLM->>VisionAgentCoderV2: Code
        
        VisionAgentCoderV2->>LLM: Generate test
        LLM->>VisionAgentCoderV2: Test
        
        VisionAgentCoderV2->>CodeInterpreter: Execute code & test
        CodeInterpreter->>VisionAgentCoderV2: Execution result
        
        alt Code execution failed
            VisionAgentCoderV2->>LLM: Debug and fix code
            LLM->>VisionAgentCoderV2: Fixed code
            VisionAgentCoderV2->>CodeInterpreter: Re-execute code
            CodeInterpreter->>VisionAgentCoderV2: Execution result
        end
        
        VisionAgentCoderV2->>VisionAgentV2: CodeContext
    else edit_code
        VisionAgentV2->>VisionAgentCoderV2: generate_code_from_plan
        VisionAgentCoderV2->>LLM: Generate code
        LLM->>VisionAgentCoderV2: Code
        VisionAgentCoderV2->>CodeInterpreter: Execute code
        CodeInterpreter->>VisionAgentCoderV2: Execution result
        VisionAgentCoderV2->>VisionAgentV2: CodeContext
    end
    
    VisionAgentV2->>LLM: Generate final response
    LLM->>VisionAgentV2: Response
    
    VisionAgentV2->>User: Response + Generated Code
```

This sequence shows how the different components interact to process a user request, generate code, test it, and return the result.

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:229-291]()
- [vision_agent/agent/vision_agent_coder_v2.py:377-422]()
- [vision_agent/agent/vision_agent_coder_v2.py:424-506]()

## Human-in-the-Loop Interaction

The agent system supports human-in-the-loop (HIL) interactions, where the agent can pause execution to request additional input from the user.

```mermaid
flowchart TD
    Start["Process User Request"] --> ShouldInteract{"Needs User\nClarification?"}
    
    ShouldInteract -->|"Yes"| CreateInteraction["Create Interaction\nContext"]
    ShouldInteract -->|"No"| ContinueExecution["Continue Normal\nExecution"]
    
    CreateInteraction --> ReturnInteraction["Return Interaction\nRequest to User"]
    ReturnInteraction --> UserResponse["User Provides\nAdditional Information"]
    UserResponse --> ResumeExecution["Resume Execution\nWith New Information"]
    
    ResumeExecution --> ContinueExecution
    ContinueExecution --> Complete["Complete Request\nand Return Results"]
```

This interaction model allows the agent to:
1. Identify when it needs additional information
2. Formulate specific questions for the user
3. Pause execution while waiting for a response
4. Resume execution with the new information

The HIL mode is enabled through the `hil` parameter in the agent constructors and is especially useful for complex vision tasks where the agent might need clarification about the user's intent.

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:165-187]()
- [vision_agent/agent/vision_agent_v2.py:92-97]()
- [vision_agent/agent/vision_agent_coder_v2.py:294-324]()
- [examples/chat/app.py:48-61]()

## Code Structure and Key Methods

The Agent System's functionality is distributed across several key methods:

| Class | Method | Purpose |
|-------|--------|---------|
| VisionAgentV2 | __call__() | Entry point for processing string input and media |
| VisionAgentV2 | chat() | Main processing method for conversational interaction |
| VisionAgentCoderV2 | generate_code() | Generate code from chat history, including planning |
| VisionAgentCoderV2 | generate_code_from_plan() | Generate code from a predefined plan |
| - | write_code() | Function to generate initial code using LLM |
| - | write_test() | Function to generate test code using LLM |
| - | test_code() | Function to test and debug code until it works |
| - | debug_code() | Function to fix issues found during testing |

These methods form the backbone of the agent system's functionality and represent the key processing steps in the workflow.

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:206-227]()
- [vision_agent/agent/vision_agent_v2.py:229-291]()
- [vision_agent/agent/vision_agent_coder_v2.py:377-422]()
- [vision_agent/agent/vision_agent_coder_v2.py:424-506]()
- [vision_agent/agent/vision_agent_coder_v2.py:64-86]()
- [vision_agent/agent/vision_agent_coder_v2.py:89-113]()
- [vision_agent/agent/vision_agent_coder_v2.py:195-258]()
- [vision_agent/agent/vision_agent_coder_v2.py:116-192]()

## Communication and Callback Mechanism

The agent system uses a callback mechanism to provide real-time updates during code generation and execution. This is especially useful for web applications or UIs that need to show progress to the user.

```mermaid
flowchart LR
    subgraph "Agent System"
        VA2["VisionAgentV2"]
        VAC2["VisionAgentCoderV2"]
        VAP2["VisionAgentPlannerV2"]
    end
    
    subgraph "Client Application"
        Callback["update_callback"]
        UI["User Interface"]
    end
    
    VA2 -->|"Register"| Callback
    VA2 -->|"Forward"| VAC2
    VAC2 -->|"Forward"| VAP2
    
    VAP2 -->|"Progress Update"| Callback
    VAC2 -->|"Code Generation Update"| Callback
    VA2 -->|"Conversation Update"| Callback
    
    Callback -->|"Update"| UI
```

The update_callback function is:
1. Initialized in the VisionAgentV2 constructor
2. Passed to the constituent components
3. Called at various stages with progress updates
4. Used to update UIs or log progress

In the example chat application, this callback mechanism is used to send WebSocket updates to connected clients, providing a real-time view of the agent's progress.

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:165-187]()
- [vision_agent/agent/vision_agent_v2.py:294-295]()
- [vision_agent/agent/vision_agent_coder_v2.py:294-324]()
- [vision_agent/agent/vision_agent_coder_v2.py:493-505]()
- [examples/chat/app.py:33-45]()

## Integration with Other Components

The Agent System integrates with several other components of the vision-agent framework:

```mermaid
flowchart TB
    subgraph "Agent System"
        VA2["VisionAgentV2"]
        VAC2["VisionAgentCoderV2"]
        VAP2["VisionAgentPlannerV2"]
    end
    
    subgraph "Language Model Module"
        LMM["LMM Interface"]
        OAILMM["OpenAILMM"]
        ANLMM["AnthropicLMM"]
    end
    
    subgraph "Code Execution"
        CI["CodeInterpreter"]
        LCI["LocalCodeInterpreter"]
    end
    
    subgraph "Vision Tools"
        TOOLS["TOOLS Registry"]
        TR["Tool Recommender"]
    end
    
    VA2 -->|"Uses"| LMM
    VAC2 -->|"Uses"| LMM
    VAP2 -->|"Uses"| LMM
    
    VA2 -->|"Uses"| CI
    VAC2 -->|"Uses"| CI
    VAP2 -->|"Uses"| CI
    
    VAC2 -->|"Recommends"| TR
    TR -->|"Queries"| TOOLS
    
    CI -->|"Imports"| TOOLS
```

Key integration points:
1. **Language Models**: Used for planning, code generation, testing, and debugging
2. **Code Interpreter**: Used to safely execute and test generated code
3. **Tool Recommender**: Used to find relevant vision tools for a given task
4. **Tools Registry**: Provides access to the vision tools used in generated code

These integrations allow the Agent System to leverage specialized components while maintaining a clean separation of concerns.

**Sources:**
- [vision_agent/agent/vision_agent_v2.py:165-187]()
- [vision_agent/agent/vision_agent_coder_v2.py:294-324]()
- [vision_agent/agent/vision_agent_coder_v2.py:51-61]()
- [vision_agent/agent/vision_agent_v2.py:254-258]()

---

