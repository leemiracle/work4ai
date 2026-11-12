<!-- source: DeepWiki mcp.deepwiki.com · repo camel-ai/owl · page 2 Architecture · fetched 2026-10-29 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [README_ja.md](README_ja.md)
- [README_zh.md](README_zh.md)
- [owl/assets/owl-favicon.ico](owl/assets/owl-favicon.ico)
- [owl/utils/enhanced_role_playing.py](owl/utils/enhanced_role_playing.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [uv.lock](uv.lock)

</details>



This document describes the overall system architecture of the OWL (Optimized Workforce Learning) framework, including its core components, design patterns, and integration points. The OWL framework is a multi-agent collaboration system built on top of the CAMEL-AI foundation that enables sophisticated task automation through role-playing agent societies.

For information about specific toolkit implementations, see [Toolkits](#5). For deployment and setup details, see [Installation & Setup](#3). For user interface components, see [User Interfaces](#4).

## System Overview

The OWL framework follows a layered architecture pattern with clear separation between user interfaces, orchestration logic, model integration, and external services.

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI1["webapp.py"]
        UI2["webapp_zh.py"] 
        UI3["webapp_jp.py"]
        UI4["CLI Scripts"]
    end
    
    subgraph "Orchestration Layer"
        ORP["OwlRolePlaying"]
        OGARP["OwlGAIARolePlaying"]
        RS["run_society()"]
        ARS["arun_society()"]
    end
    
    subgraph "Agent Layer"
        UA["ChatAgent (User)"]
        AA["ChatAgent (Assistant)"]
        BM["BaseMessage"]
        CAR["ChatAgentResponse"]
    end
    
    subgraph "Toolkit Layer"
        DPT["DocumentProcessingToolkit"]
        BT["BrowserToolkit"]
        ST["SearchToolkit"]
        CET["CodeExecutionToolkit"]
        MCPT["MCPToolkit"]
    end
    
    subgraph "Model Integration"
        MF["ModelFactory"]
        MPT["ModelPlatformType"]
        MT["ModelType"]
    end
    
    subgraph "External Dependencies"
        CAMEL["camel-ai[owl]"]
        GRADIO["gradio"]
        MCP["MCP Servers"]
        APIS["External APIs"]
    end
    
    UI1 --> ORP
    UI2 --> ORP
    UI3 --> ORP
    UI4 --> ORP
    
    ORP --> UA
    ORP --> AA
    OGARP --> UA
    OGARP --> AA
    
    RS --> ORP
    ARS --> ORP
    
    UA --> BM
    AA --> BM
    UA --> CAR
    AA --> CAR
    
    AA --> DPT
    AA --> BT
    AA --> ST
    AA --> CET
    AA --> MCPT
    
    ORP --> MF
    MF --> MPT
    MF --> MT
    
    ORP --> CAMEL
    UI1 --> GRADIO
    MCPT --> MCP
    BT --> APIS
```

**Sources:** [owl/utils/enhanced_role_playing.py:1-572](), [pyproject.toml:1-71](), [owl/utils/__init__.py:15-33]()

## Core Components

The OWL framework is built around several key architectural components that work together to provide multi-agent task automation capabilities.

### Primary Classes and Their Responsibilities

| Class | File Location | Primary Responsibility |
|-------|---------------|------------------------|
| `OwlRolePlaying` | [owl/utils/enhanced_role_playing.py:31-354]() | Main orchestration class for agent societies |
| `OwlGAIARolePlaying` | [owl/utils/enhanced_role_playing.py:355-441]() | Specialized role-playing for GAIA benchmarks |
| `DocumentProcessingToolkit` | Referenced in [owl/utils/__init__.py:23]() | Document processing capabilities |
| `run_society` | [owl/utils/enhanced_role_playing.py:442-504]() | Synchronous society execution |
| `arun_society` | [owl/utils/enhanced_role_playing.py:507-571]() | Asynchronous society execution |

### Component Interaction Diagram

```mermaid
graph LR
    subgraph "Core Architecture"
        ORP["OwlRolePlaying"]
        INIT["_init_agents()"]
        STEP["step()"]
        ASTEP["astep()"]
        SYSMSG["_construct_gaia_sys_msgs()"]
    end
    
    subgraph "Agent Management"
        UA["user_agent: ChatAgent"]
        AA["assistant_agent: ChatAgent"]
        USM["user_sys_msg"]
        ASM["assistant_sys_msg"]
    end
    
    subgraph "Message Processing"
        BM["BaseMessage"]
        CAR["ChatAgentResponse"]
        RMSG["_reduce_message_options()"]
    end
    
    ORP --> INIT
    ORP --> STEP
    ORP --> ASTEP
    ORP --> SYSMSG
    
    INIT --> UA
    INIT --> AA
    SYSMSG --> USM
    SYSMSG --> ASM
    
    STEP --> CAR
    ASTEP --> CAR
    STEP --> BM
    ASTEP --> BM
```

**Sources:** [owl/utils/enhanced_role_playing.py:31-67](), [owl/utils/enhanced_role_playing.py:68-122](), [owl/utils/enhanced_role_playing.py:143-214]()

## Agent Architecture

The OWL framework implements a sophisticated two-agent role-playing system where agents collaborate to solve complex tasks through structured conversations.

### Agent Initialization Pattern

```mermaid
sequenceDiagram
    participant C as "Constructor"
    participant CSM as "_construct_gaia_sys_msgs()"
    participant IA as "_init_agents()"
    participant UA as "user_agent"
    participant AA as "assistant_agent"
    
    C->>CSM: Create system messages
    CSM->>C: Return user_sys_msg, assistant_sys_msg
    C->>IA: Initialize agents with system messages
    IA->>UA: Create ChatAgent with user system message
    IA->>AA: Create ChatAgent with assistant system message
    IA->>C: Agents ready
```

The `OwlRolePlaying` class constructor follows this initialization pattern:

1. **System Message Construction**: [owl/utils/enhanced_role_playing.py:143-214]() - Creates specialized system prompts for user and assistant roles
2. **Agent Initialization**: [owl/utils/enhanced_role_playing.py:68-122]() - Instantiates `ChatAgent` objects with appropriate configurations
3. **Model Assignment**: [owl/utils/enhanced_role_playing.py:92-101]() - Assigns LLM models to agents based on configuration

### Role-Playing Execution Flow

```mermaid
graph TD
    subgraph "Execution Cycle"
        START["init_chat()"]
        USTEP["user_agent.step()"]
        CHECK1{"TASK_DONE?"}
        MODIFY1["Modify user message"]
        ASTEP["assistant_agent.step()"]
        CHECK2{"Terminated?"}
        MODIFY2["Modify assistant message"]
        NEXT["Next iteration"]
    end
    
    START --> USTEP
    USTEP --> CHECK1
    CHECK1 -->|No| MODIFY1
    CHECK1 -->|Yes| MODIFY1
    MODIFY1 --> ASTEP
    ASTEP --> CHECK2
    CHECK2 -->|No| MODIFY2
    CHECK2 -->|Yes| END["Return final answer"]
    MODIFY2 --> NEXT
    NEXT --> USTEP
    
    subgraph "Message Modifications"
        AUX["Add auxiliary_information"]
        TOOL["Add tool usage instructions"]
        FINAL["Add final answer request"]
    end
    
    MODIFY1 --> AUX
    MODIFY1 --> TOOL
    MODIFY1 --> FINAL
```

The execution flow is managed by the `step` method at [owl/utils/enhanced_role_playing.py:216-284]() and its async counterpart `astep` at [owl/utils/enhanced_role_playing.py:286-352]().

**Sources:** [owl/utils/enhanced_role_playing.py:216-284](), [owl/utils/enhanced_role_playing.py:286-352](), [owl/utils/enhanced_role_playing.py:442-504]()

## Dependency Architecture

The OWL framework is built on a carefully orchestrated set of dependencies that provide different layers of functionality.

### Core Dependencies

```mermaid
graph TB
    subgraph "Foundation Layer"
        CAMEL["camel-ai[owl]==0.2.57"]
        PYTHON["Python >=3.10,<3.13"]
    end
    
    subgraph "UI Layer"
        GRADIO["gradio>=3.50.2"]
        DOCX2MD["docx2markdown>=0.1.1"]
        XMLTODICT["xmltodict>=0.14.2"]
    end
    
    subgraph "Integration Layer"
        MCP_ARXIV["mcp-simple-arxiv==0.2.2"]
        MCP_FETCH["mcp-server-fetch==2025.1.17"]
        FIRECRAWL["firecrawl>=2.5.3"]
        MISTRAL["mistralai>=1.7.0"]
    end
    
    subgraph "Optional Dependencies"
        OWL_DEPS["camel-ai[owl] extras"]
        ANTHROPIC["anthropic"]
        PLAYWRIGHT["playwright"]
        PANDAS["pandas, pandasai"]
        CV["opencv-python"]
    end
    
    CAMEL --> PYTHON
    GRADIO --> UI_LAYER["UI Components"]
    MCP_ARXIV --> INTEGRATION["External Services"]
    MCP_FETCH --> INTEGRATION
    FIRECRAWL --> INTEGRATION
    
    OWL_DEPS --> ANTHROPIC
    OWL_DEPS --> PLAYWRIGHT
    OWL_DEPS --> PANDAS
    OWL_DEPS --> CV
```

The dependency structure is defined in [pyproject.toml:23-32]() for core dependencies and [requirements.txt:1-7]() for the simplified requirement set.

### Model Integration Architecture

```mermaid
graph LR
    subgraph "Model Abstraction"
        MF["ModelFactory"]
        MPT["ModelPlatformType"]
        MT["ModelType"]
        MCD["model_config_dict"]
    end
    
    subgraph "Platform Support"
        OPENAI["OpenAI Models"]
        ANTHROPIC["Anthropic Models"]
        QWEN["Qwen Models"]
        DEEPSEEK["DeepSeek Models"]
        OTHERS["Other Platforms"]
    end
    
    subgraph "Agent Integration"
        UA_MODEL["user_agent.model"]
        AA_MODEL["assistant_agent.model"] 
        CONFIG["Agent Configuration"]
    end
    
    MF --> MPT
    MF --> MT
    MF --> MCD
    
    MPT --> OPENAI
    MPT --> ANTHROPIC
    MPT --> QWEN
    MPT --> DEEPSEEK
    MPT --> OTHERS
    
    MF --> UA_MODEL
    MF --> AA_MODEL
    CONFIG --> UA_MODEL
    CONFIG --> AA_MODEL
```

**Sources:** [pyproject.toml:23-32](), [requirements.txt:1-7](), [owl/utils/enhanced_role_playing.py:92-107]()

## Execution Flow

The OWL framework processes tasks through a structured execution pipeline that coordinates agent interactions and manages external tool integration.

### Society Execution Pipeline

```mermaid
flowchart TD
    subgraph "Initialization"
        CONSTRUCT["construct_society()"]
        INIT_CHAT["society.init_chat()"]
        SETUP_MSG["Setup initial message"]
    end
    
    subgraph "Main Loop"
        ROUND_START["Round start"]
        SOCIETY_STEP["society.step(input_msg)"]
        GET_RESPONSES["Get assistant_response, user_response"]
        COUNT_TOKENS["Count tokens"]
        RECORD_TOOLS["Record tool_calls"]
        UPDATE_HISTORY["Update chat_history"]
        CHECK_TERM{"Terminated or TASK_DONE?"}
    end
    
    subgraph "Completion"
        EXTRACT_ANSWER["Extract final answer"]
        COMPILE_TOKENS["Compile token_info"]
        RETURN_RESULTS["Return answer, chat_history, token_info"]
    end
    
    CONSTRUCT --> INIT_CHAT
    INIT_CHAT --> SETUP_MSG
    SETUP_MSG --> ROUND_START
    ROUND_START --> SOCIETY_STEP
    SOCIETY_STEP --> GET_RESPONSES
    GET_RESPONSES --> COUNT_TOKENS
    COUNT_TOKENS --> RECORD_TOOLS
    RECORD_TOOLS --> UPDATE_HISTORY
    UPDATE_HISTORY --> CHECK_TERM
    CHECK_TERM -->|No| ROUND_START
    CHECK_TERM -->|Yes| EXTRACT_ANSWER
    EXTRACT_ANSWER --> COMPILE_TOKENS
    COMPILE_TOKENS --> RETURN_RESULTS
```

The main execution functions `run_society` and `arun_society` implement this pipeline:

- **Token Tracking**: [owl/utils/enhanced_role_playing.py:456-463]() - Accumulates token usage across rounds
- **Tool Call Recording**: [owl/utils/enhanced_role_playing.py:465-469]() - Captures tool invocations for history
- **Termination Logic**: [owl/utils/enhanced_role_playing.py:489-494]() - Checks for completion conditions
- **Result Compilation**: [owl/utils/enhanced_role_playing.py:498-503]() - Formats final output

### Message Processing Flow

```mermaid
graph TD
    subgraph "User Agent Processing"
        USER_INPUT["Input message"]
        USER_STEP["user_agent.step()"]
        USER_MSG["Extract user_msg"]
        MODIFY_USER["Modify user message"]
    end
    
    subgraph "Assistant Agent Processing"  
        ASST_STEP["assistant_agent.step()"]
        ASST_MSG["Extract assistant_msg"]
        MODIFY_ASST["Modify assistant message"]
        TOOL_CALLS["Process tool_calls"]
    end
    
    subgraph "Message Modifications"
        ADD_AUX["Add auxiliary_information"]
        ADD_TOOLS["Add tool instructions"]
        ADD_NEXT["Add next instruction prompt"]
        CHECK_FINAL["Check for final answer"]
    end
    
    USER_INPUT --> USER_STEP
    USER_STEP --> USER_MSG
    USER_MSG --> MODIFY_USER
    MODIFY_USER --> ADD_AUX
    MODIFY_USER --> ADD_TOOLS
    
    MODIFY_USER --> ASST_STEP
    ASST_STEP --> ASST_MSG
    ASST_STEP --> TOOL_CALLS
    ASST_MSG --> MODIFY_ASST
    MODIFY_ASST --> ADD_NEXT
    MODIFY_ASST --> CHECK_FINAL
```

The message processing is handled by the `step` method which:

1. **Processes User Response**: [owl/utils/enhanced_role_playing.py:219-229]() - Gets user agent's response and extracts messages
2. **Modifies User Message**: [owl/utils/enhanced_role_playing.py:233-246]() - Adds contextual information and tool usage instructions  
3. **Processes Assistant Response**: [owl/utils/enhanced_role_playing.py:249-261]() - Gets assistant agent's response and tool calls
4. **Modifies Assistant Message**: [owl/utils/enhanced_role_playing.py:264-270]() - Adds instructions for next steps

**Sources:** [owl/utils/enhanced_role_playing.py:216-284](), [owl/utils/enhanced_role_playing.py:442-504](), [owl/utils/enhanced_role_playing.py:507-571]()

---

