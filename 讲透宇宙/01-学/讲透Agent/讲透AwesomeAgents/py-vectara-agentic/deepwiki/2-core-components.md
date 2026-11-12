<!-- source: DeepWiki mcp.deepwiki.com · repo vectara/py-vectara-agentic · page 2 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vectara_agentic/agent.py](vectara_agentic/agent.py)
- [vectara_agentic/tools.py](vectara_agentic/tools.py)

</details>



This document covers the fundamental building blocks of the vectara-agentic system, explaining how the main classes and interfaces work together to create a flexible AI agent framework. For detailed information about agent types and lifecycle management, see [Agent System](#2.1). For comprehensive tool creation patterns, see [Tool Factory System](#2.2). For workflow orchestration capabilities, see [Workflow Engine](#2.3).

The core components form a modular architecture where agents coordinate tool execution through factory patterns, with extensive configuration management and LLM provider abstraction.

## Architecture Overview

The vectara-agentic system is built around several key components that work together to provide a complete agentic framework:

```mermaid
graph TB
    subgraph "Core Agent Layer"
        Agent["Agent<br/>Central Orchestrator"]
        AgentConfig["AgentConfig<br/>Configuration Management"]
        Memory["ChatMemoryBuffer<br/>Conversation History"]
    end
    
    subgraph "Tool Creation Layer"
        VectaraToolFactory["VectaraToolFactory<br/>Vectara-specific Tools"]
        ToolsFactory["ToolsFactory<br/>Generic Tool Creation"]
        VectaraTool["VectaraTool<br/>Tool Wrapper"]
    end
    
    subgraph "LLM Provider Layer"
        LLMUtils["get_llm()<br/>Provider Abstraction"]
        OpenAI["OpenAI Provider"]
        Anthropic["Anthropic Provider"]
        Gemini["Gemini Provider"]
    end
    
    subgraph "Execution Engine"
        BaseAgent["BaseAgent<br/>LlamaIndex Agent Types"]
        AgentRunner["AgentRunner<br/>Execution Runtime"]
        CallbackManager["CallbackManager<br/>Event Handling"]
    end
    
    Agent --> AgentConfig
    Agent --> Memory
    Agent --> VectaraToolFactory
    Agent --> ToolsFactory
    Agent --> LLMUtils
    Agent --> BaseAgent
    
    VectaraToolFactory --> VectaraTool
    ToolsFactory --> VectaraTool
    LLMUtils --> OpenAI
    LLMUtils --> Anthropic
    LLMUtils --> Gemini
    
    BaseAgent --> AgentRunner
    Agent --> CallbackManager
```

**Sources:** [vectara_agentic/agent.py:194-298](), [vectara_agentic/tools.py:68-780]()

## Agent as Central Orchestrator

The `Agent` class serves as the primary interface and orchestrator for the entire system. It manages tool execution, LLM interactions, memory, and configuration switching.

```mermaid
graph LR
    subgraph "Agent Initialization"
        AgentInit["Agent.__init__()"]
        ConfigValidation["Tool Validation"]
        MemorySetup["ChatMemoryBuffer Setup"]
        AgentCreation["_create_agent()"]
    end
    
    subgraph "Agent Types"
        ReActAgent["ReActAgent"]
        OpenAIAgent["OpenAIAgent"] 
        FunctionCallingAgent["FunctionCallingAgent"]
        LLMCompilerAgent["LLMCompilerAgentWorker"]
        LATSAgent["LATSAgentWorker"]
    end
    
    subgraph "Execution Methods"
        Chat["chat() / achat()"]
        StreamChat["stream_chat() / astream_chat()"]
        Run["run() for workflows"]
    end
    
    AgentInit --> ConfigValidation
    ConfigValidation --> MemorySetup
    MemorySetup --> AgentCreation
    
    AgentCreation --> ReActAgent
    AgentCreation --> OpenAIAgent
    AgentCreation --> FunctionCallingAgent
    AgentCreation --> LLMCompilerAgent
    AgentCreation --> LATSAgent
    
    Chat --> ReActAgent
    StreamChat --> OpenAIAgent
    Run --> FunctionCallingAgent
```

The `Agent` class provides several creation patterns:

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `Agent.from_tools()` | Create agent from tool list | `tools`, `agent_config`, `topic` |
| `Agent.from_corpus()` | Create agent from Vectara corpus | `vectara_corpus_key`, `data_description` |
| `Agent.__init__()` | Direct instantiation | Full parameter control |

**Sources:** [vectara_agentic/agent.py:199-298](), [vectara_agentic/agent.py:630-686](), [vectara_agentic/agent.py:688-853]()

## Tool Factory Pattern

The system uses a factory pattern to create and manage tools. Two main factories handle different tool categories:

```mermaid
graph TB
    subgraph "VectaraToolFactory Methods"
        CreateRAG["create_rag_tool()<br/>RAG with Summarization"]
        CreateSearch["create_search_tool()<br/>Document Retrieval"]
    end
    
    subgraph "ToolsFactory Methods"  
        StandardTools["standard_tools()<br/>Text Processing"]
        GuardrailTools["guardrail_tools()<br/>Content Safety"]
        FinancialTools["financial_tools()<br/>Yahoo Finance"]
        LegalTools["legal_tools()<br/>Legal Analysis"]
        DatabaseTools["database_tools()<br/>SQL Interface"]
        LlamaIndexTools["get_llama_index_tools()<br/>External Integrations"]
    end
    
    subgraph "Tool Outputs"
        VectaraTool1["VectaraTool<br/>RAG Tool"]
        VectaraTool2["VectaraTool<br/>Search Tool"] 
        VectaraTool3["VectaraTool<br/>Standard Tool"]
        VectaraTool4["VectaraTool<br/>External Tool"]
    end
    
    CreateRAG --> VectaraTool1
    CreateSearch --> VectaraTool2
    StandardTools --> VectaraTool3
    LlamaIndexTools --> VectaraTool4
```

### VectaraToolFactory

The `VectaraToolFactory` specializes in creating tools that interact with the Vectara platform:

- **RAG Tools**: Created via `create_rag_tool()` for retrieval-augmented generation
- **Search Tools**: Created via `create_search_tool()` for document retrieval
- **Dynamic Function Generation**: Tools are created with dynamically generated functions that handle Vectara API calls

### ToolsFactory  

The `ToolsFactory` handles general-purpose tool creation:

- **Standard Tools**: Text processing tools like `summarize_text`, `rephrase_text`, `critique_text`
- **Domain-Specific Tools**: Financial, legal, and database tools
- **External Integrations**: LlamaIndex hub tools for various APIs

**Sources:** [vectara_agentic/tools.py:68-569](), [vectara_agentic/tools.py:571-780]()

## Configuration Management

The system uses `AgentConfig` to manage all configuration aspects, with support for fallback configurations and environment variable integration.

```mermaid
graph LR
    subgraph "Configuration Sources"
        EnvVars["Environment Variables"]
        ConfigParams["Constructor Parameters"] 
        Defaults["Default Values"]
    end
    
    subgraph "AgentConfig Properties"
        AgentType["agent_type: AgentType"]
        MainLLM["main_llm_provider: ModelProvider"]
        ToolLLM["tool_llm_provider: ModelProvider"]
        MaxSteps["max_reasoning_steps: int"]
        Observability["observability_config: dict"]
    end
    
    subgraph "Runtime Behavior"
        PrimaryConfig["Primary Configuration"]
        FallbackConfig["Fallback Configuration"]
        ConfigSwitching["Automatic Switching"]
    end
    
    EnvVars --> AgentType
    ConfigParams --> MainLLM
    Defaults --> ToolLLM
    
    AgentType --> PrimaryConfig
    MainLLM --> FallbackConfig
    PrimaryConfig --> ConfigSwitching
    FallbackConfig --> ConfigSwitching
```

**Sources:** [vectara_agentic/agent.py:246-247](), [vectara_agentic/agent.py:343-349]()

## LLM Provider Integration

The system abstracts LLM provider differences through a unified interface:

```mermaid
graph TB
    subgraph "LLM Role System"
        MainRole["LLMRole.MAIN<br/>Primary Agent LLM"]
        ToolRole["LLMRole.TOOL<br/>Tool Execution LLM"]
    end
    
    subgraph "Provider Support"
        OpenAIProvider["ModelProvider.OPENAI"]
        AnthropicProvider["ModelProvider.ANTHROPIC"] 
        GeminiProvider["ModelProvider.GEMINI"]
        OtherProviders["Together, Groq, Cohere, etc."]
    end
    
    subgraph "Special Handling"
        GeminiSanitization["_sanitize_tools_for_gemini()<br/>Remove Default Parameters"]
        TokenCounting["TokenCountingHandler<br/>Usage Tracking"]
        CallbackIntegration["Callback Manager Integration"]
    end
    
    MainRole --> OpenAIProvider
    ToolRole --> AnthropicProvider
    MainRole --> GeminiProvider
    
    GeminiProvider --> GeminiSanitization
    OpenAIProvider --> TokenCounting
    AnthropicProvider --> CallbackIntegration
```

The system includes special handling for provider-specific requirements, such as Gemini's tool parameter restrictions handled by `_sanitize_tools_for_gemini()`.

**Sources:** [vectara_agentic/agent.py:358-413](), [vectara_agentic/agent.py:253](), [vectara_agentic/agent.py:304-311]()

## Data Flow and Tool Execution

The following diagram shows how user queries flow through the system:

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant ToolFactory
    participant VectaraTool
    participant VectaraAPI
    participant LLM
    
    User->>Agent: "chat() or achat()"
    Agent->>Agent: "_get_current_agent()"
    Agent->>LLM: "Generate reasoning plan"
    LLM-->>Agent: "Tool calls needed"
    
    loop For each tool call
        Agent->>VectaraTool: "Execute tool function"
        VectaraTool->>VectaraAPI: "Query with filters"
        VectaraAPI-->>VectaraTool: "Search results"
        VectaraTool->>LLM: "Summarize results (if RAG)"
        LLM-->>VectaraTool: "Processed output"
        VectaraTool-->>Agent: "ToolOutput object"
    end
    
    Agent->>LLM: "Generate final response"
    LLM-->>Agent: "AgentResponse"
    Agent-->>User: "Final answer"
```

**Sources:** [vectara_agentic/agent.py:953-994](), [vectara_agentic/tools.py:167-263](), [vectara_agentic/tools.py:416-549]()

## Error Handling and Fallbacks

The system includes robust error handling with automatic configuration switching:

```mermaid
graph LR
    subgraph "Error Detection"
        LLMFailure["LLM Call Failure"]
        ToolFailure["Tool Execution Failure"]
        ValidationFailure["Input Validation Failure"]
    end
    
    subgraph "Recovery Mechanisms"
        ConfigSwitch["_switch_agent_config()"]
        RetryLogic["Retry with Backoff"]
        FallbackAgent["Fallback Agent Config"]
    end
    
    subgraph "Error Reporting"
        AgentResponse["AgentResponse with Error"]
        CallbackNotification["Callback Notifications"]
        VerboseLogging["Verbose Error Messages"]
    end
    
    LLMFailure --> ConfigSwitch
    ToolFailure --> RetryLogic
    ValidationFailure --> AgentResponse
    
    ConfigSwitch --> FallbackAgent
    RetryLogic --> CallbackNotification
    FallbackAgent --> VerboseLogging
```

The system attempts up to 4 retries (2 with primary config, 2 with fallback) before returning an error response.

**Sources:** [vectara_agentic/agent.py:963-994](), [vectara_agentic/agent.py:855-863]()

## Serialization and Persistence

The `Agent` class supports serialization for persistence and deployment:

| Method | Purpose | Format |
|--------|---------|--------|
| `dumps()` | Serialize to JSON string | JSON with pickled functions |
| `loads()` | Deserialize from JSON | Reconstructs full agent |
| `to_dict()` | Convert to dictionary | Includes tool schemas |
| `from_dict()` | Create from dictionary | Handles schema reconstruction |

The serialization system handles complex cases like Pydantic model schemas and function pickling for complete state preservation.

**Sources:** [vectara_agentic/agent.py:1124-1297]()

---

