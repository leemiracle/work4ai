<!-- source: DeepWiki mcp.deepwiki.com · repo Maximilian-Winter/llama-cpp-agent · page 3 Core Framework · fetched 2026-10-26 -->

# Core Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/llama_cpp_agent/function_calling.py](src/llama_cpp_agent/function_calling.py)
- [src/llama_cpp_agent/function_calling_agent.py](src/llama_cpp_agent/function_calling_agent.py)
- [src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py](src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py)
- [src/llama_cpp_agent/llm_agent.py](src/llama_cpp_agent/llm_agent.py)
- [src/llama_cpp_agent/messages_formatter.py](src/llama_cpp_agent/messages_formatter.py)

</details>



This document covers the fundamental components and architecture of the llama-cpp-agent framework, including the central agent orchestrator, specialized agent types, message processing pipeline, and output handling systems. For information about specific LLM provider implementations, see [Provider System](#4). For memory system integration, see [Memory System](#5). For detailed tool and function calling capabilities, see [Tools and Function Calling](#6).

## Core Architecture Overview

The Core Framework centers around the `LlamaCppAgent` class as the primary orchestrator, with specialized agent types for specific use cases and a comprehensive message processing pipeline.

### Framework Components Diagram

```mermaid
graph TB
    subgraph "Core Agent Layer"
        LCA["LlamaCppAgent<br/>(Central Orchestrator)"]
        FCA["FunctionCallingAgent<br/>(Tool Execution)"]
        SOA["StructuredOutputAgent<br/>(Data Generation)"]
    end
    
    subgraph "Message Processing"
        MF["MessagesFormatter<br/>(Chat Templates)"]
        SPM["SystemPromptModule<br/>(Dynamic Context)"]
        CH["ChatHistory<br/>(Conversation State)"]
    end
    
    subgraph "Output Processing"
        SOS["LlmStructuredOutputSettings<br/>(Output Configuration)"]
        GBNF["GBNF Grammar Generator<br/>(Parsing Constraints)"]
        OP["Output Parser<br/>(Response Processing)"]
    end
    
    subgraph "Function System"
        LFT["LlamaCppFunctionTool<br/>(Tool Wrapper)"]
        FC["Function Calling<br/>(Execution Engine)"]
    end
    
    subgraph "Provider Interface"
        PA["LlmProvider<br/>(Abstraction Layer)"]
        SS["LlmSamplingSettings<br/>(Generation Control)"]
    end
    
    LCA --> MF
    LCA --> SPM
    LCA --> CH
    LCA --> SOS
    LCA --> PA
    LCA --> SS
    
    FCA --> LCA
    FCA --> LFT
    FCA --> FC
    
    SOA --> LCA
    SOA --> GBNF
    
    SOS --> GBNF
    SOS --> OP
    
    style LCA fill:#e1f5fe
    style FCA fill:#f3e5f5
    style SOA fill:#f3e5f5
```

**Sources:** [src/llama_cpp_agent/llm_agent.py:70-662](), [src/llama_cpp_agent/function_calling_agent.py:89-301](), [src/llama_cpp_agent/messages_formatter.py:41-134]()

## LlamaCppAgent - Central Orchestrator

The `LlamaCppAgent` class serves as the primary interface for all agent interactions, handling chat responses, text generation, and structured output coordination.

### Core Agent Architecture

```mermaid
graph LR
    subgraph "LlamaCppAgent Internal Flow"
        Init["__init__<br/>(Initialization)"]
        GCR["get_chat_response<br/>(Main Interface)"]
        GTR["get_text_response<br/>(Raw Generation)"]
        GTC["get_text_completion<br/>(Provider Call)"]
        GRRC["get_response_role_and_completion<br/>(Message Processing)"]
    end
    
    subgraph "Key Attributes"
        Provider["provider: LlmProvider"]
        MsgFmt["messages_formatter: MessagesFormatter"]
        ChatHist["chat_history: ChatHistory"]
        SysPrompt["system_prompt: str"]
        LastResp["last_response: str"]
    end
    
    subgraph "Configuration"
        DebugOut["debug_output: bool"]
        AddToolsDocs["add_tools_and_structures_documentation_to_system_prompt: bool"]
    end
    
    Init --> Provider
    Init --> MsgFmt
    Init --> ChatHist
    Init --> SysPrompt
    
    GCR --> GRRC
    GRRC --> GTR
    GTR --> GTC
    GTC --> Provider
    
    GCR --> LastResp
```

**Sources:** [src/llama_cpp_agent/llm_agent.py:75-117](), [src/llama_cpp_agent/llm_agent.py:237-382]()

### Key Methods and Responsibilities

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `get_chat_response` | Primary chat interface | `message`, `structured_output_settings`, `llm_sampling_settings` |
| `get_text_response` | Raw text generation | `prompt`, `structured_output_settings`, `streaming_callback` |
| `add_message` | Chat history management | `message`, `role` |
| `get_text_completion` | Direct provider interaction | `prompt`, `structured_output_settings`, `llm_samplings_settings` |

**Sources:** [src/llama_cpp_agent/llm_agent.py:137-235](), [src/llama_cpp_agent/llm_agent.py:237-382](), [src/llama_cpp_agent/llm_agent.py:118-135](), [src/llama_cpp_agent/llm_agent.py:384-395]()

## Specialized Agent Types

### FunctionCallingAgent

The `FunctionCallingAgent` extends the core framework to provide autonomous tool execution capabilities through structured function calling.

```mermaid
graph TB
    subgraph "FunctionCallingAgent Architecture"
        FCA_Init["__init__<br/>(Setup Tools & Settings)"]
        GenResp["generate_response<br/>(Main Loop)"]
        InternGet["intern_get_response<br/>(LLM Interaction)"]
        ToolExec["Tool Execution<br/>(Function Calls)"]
    end
    
    subgraph "Tool Management"
        LCFTools["llama_cpp_tools: List[LlamaCppFunctionTool]"]
        StructOut["structured_output_settings: LlmStructuredOutputSettings"]
        SendMsg["send_message_to_user_callback: Callable"]
    end
    
    subgraph "Built-in Tools"
        SendMsgTool["send_message<br/>(User Communication)"]
        ReadFile["read_text_file<br/>(File Reading)"]
        WriteFile["write_text_file<br/>(File Writing)"]
    end
    
    FCA_Init --> LCFTools
    FCA_Init --> StructOut
    FCA_Init --> SendMsg
    
    GenResp --> InternGet
    InternGet --> ToolExec
    ToolExec --> GenResp
    
    LCFTools --> SendMsgTool
    LCFTools --> ReadFile
    LCFTools --> WriteFile
```

**Sources:** [src/llama_cpp_agent/function_calling_agent.py:128-199](), [src/llama_cpp_agent/function_calling_agent.py:223-288](), [src/llama_cpp_agent/function_calling_agent.py:20-87]()

### StructuredOutputAgent

While not explicitly implemented as a separate class, structured output functionality is integrated into the core framework through `LlmStructuredOutputSettings` and GBNF grammar generation.

## Message Processing Pipeline

The message formatting system handles conversion between conversation formats and model-specific chat templates.

### Message Formatter Architecture

```mermaid
graph LR
    subgraph "MessagesFormatter Components"
        MF_Init["MessagesFormatter<br/>__init__"]
        FormatConv["format_conversation<br/>(Main Interface)"]
        FormatSys["_format_system_message"]
        FormatUser["_format_user_message"]
        FormatAsst["_format_assistant_message"]
        FormatTool["_format_tool_message"]
    end
    
    subgraph "Configuration"
        PrePrompt["pre_prompt: str"]
        PromptMarkers["prompt_markers: Dict[Roles, PromptMarkers]"]
        StopSeqs["default_stop_sequences: List[str]"]
        BOSToken["bos_token: str"]
        EOSToken["eos_token: str"]
    end
    
    subgraph "Predefined Formatters"
        CHATML["chatml_formatter"]
        Mixtral["mixtral_formatter"]
        Llama3["llama_3_formatter"]
        Phi3["phi_3_chat_formatter"]
    end
    
    MF_Init --> PrePrompt
    MF_Init --> PromptMarkers
    MF_Init --> StopSeqs
    
    FormatConv --> FormatSys
    FormatConv --> FormatUser
    FormatConv --> FormatAsst
    FormatConv --> FormatTool
    
    CHATML --> MF_Init
    Mixtral --> MF_Init
    Llama3 --> MF_Init
    Phi3 --> MF_Init
```

**Sources:** [src/llama_cpp_agent/messages_formatter.py:41-134](), [src/llama_cpp_agent/messages_formatter.py:433-454](), [src/llama_cpp_agent/messages_formatter.py:151-177]()

### System Prompt Modules

Dynamic system prompt management through modular components that can be positioned and configured independently.

```mermaid
graph TB
    subgraph "SystemPromptModule Structure"
        SPM_Init["SystemPromptModule<br/>__init__"]
        SetContent["set_content<br/>(Content Management)"]
        GetFormatted["get_formatted_content<br/>(XML Formatting)"]
    end
    
    subgraph "Module Configuration"
        SectionName["section_name: str"]
        Prefix["prefix: str"]
        Suffix["suffix: str"]
        Content["content: str"]
        Position["position: SystemPromptModulePosition"]
    end
    
    subgraph "Position Types"
        AfterSys["after_system_instructions"]
        AtEnd["at_end"]
    end
    
    SPM_Init --> SectionName
    SPM_Init --> Position
    SetContent --> Content
    GetFormatted --> Prefix
    GetFormatted --> Suffix
    
    Position --> AfterSys
    Position --> AtEnd
```

**Sources:** [src/llama_cpp_agent/llm_agent.py:27-46](), [src/llama_cpp_agent/llm_agent.py:444-636]()

## Output Processing System

The framework provides sophisticated structured output capabilities through GBNF grammar generation and parsing.

### GBNF Grammar Generation Pipeline

```mermaid
graph TB
    subgraph "Grammar Generation Flow"
        PydModels["Pydantic Models<br/>(Input Specifications)"]
        GenGrammar["generate_gbnf_grammar_from_pydantic_models<br/>(Main Generator)"]
        GenDocumentation["generate_text_documentation<br/>(Human-Readable Docs)"]
        MapTypes["map_pydantic_type_to_gbnf<br/>(Type Mapping)"]
        GetPrimitive["get_primitive_grammar<br/>(Base Rules)"]
    end
    
    subgraph "Data Type Support"
        BasicTypes["STRING, BOOLEAN, INTEGER, FLOAT"]
        ComplexTypes["OBJECT, ARRAY, ENUM"]
        SpecialTypes["TRIPLE_QUOTED_STRING, MARKDOWN_CODE_BLOCK"]
        CustomTypes["CUSTOM_CLASS, CUSTOM_DICT, SET"]
    end
    
    subgraph "Output Configuration"
        OuterObj["outer_object_name: str"]
        ListOutputs["list_of_outputs: bool"]
        InnerThoughts["add_inner_thoughts: bool"]
        Heartbeat["add_request_heartbeat: bool"]
    end
    
    PydModels --> GenGrammar
    GenGrammar --> MapTypes
    GenGrammar --> GetPrimitive
    GenGrammar --> GenDocumentation
    
    MapTypes --> BasicTypes
    MapTypes --> ComplexTypes
    MapTypes --> SpecialTypes
    MapTypes --> CustomTypes
    
    GenGrammar --> OuterObj
    GenGrammar --> ListOutputs
    GenGrammar --> InnerThoughts
    GenGrammar --> Heartbeat
```

**Sources:** [src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py:664-776](), [src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py:70-104](), [src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py:778-845]()

### Function Tool Integration

The `LlamaCppFunctionTool` class provides a unified interface for different function calling approaches.

```mermaid
graph LR
    subgraph "LlamaCppFunctionTool Creation"
        PydanticModel["Pydantic BaseModel<br/>(Structured Input)"]
        PythonFunc["Python Callable<br/>(Function)"]
        OpenAITool["OpenAI Tool Schema<br/>(Dictionary)"]
        LlamaIndexTool["LlamaIndex Tool<br/>(External Tool)"]
    end
    
    subgraph "Tool Processing"
        CreateDynamic["create_dynamic_model_from_function<br/>(Function → Model)"]
        CreateFromDict["create_dynamic_models_from_dictionaries<br/>(Schema → Model)"]
        AddRunMethod["add_run_method_to_dynamic_model<br/>(Add Execution)"]
    end
    
    subgraph "LlamaCppFunctionTool Instance"
        ToolInit["__init__<br/>(Setup)"]
        ModelAttr["model: Type[BaseModel]"]
        CallMethod["__call__<br/>(Execution)"]
        ToOpenAI["to_openai_tool<br/>(Export)"]
    end
    
    PydanticModel --> ToolInit
    PythonFunc --> CreateDynamic
    OpenAITool --> CreateFromDict
    LlamaIndexTool --> CreateFromDict
    
    CreateDynamic --> AddRunMethod
    CreateFromDict --> AddRunMethod
    AddRunMethod --> ModelAttr
    
    ToolInit --> ModelAttr
    ModelAttr --> CallMethod
    ToolInit --> ToOpenAI
```

**Sources:** [src/llama_cpp_agent/function_calling.py:142-180](), [src/llama_cpp_agent/function_calling.py:202-230](), [src/llama_cpp_agent/function_calling.py:248-255]()

## Integration and Data Flow

The complete framework integration shows how all components work together for a typical interaction.

### Complete Framework Data Flow

```mermaid
graph TB
    subgraph "User Interaction Layer"
        UserInput["User Input<br/>(Natural Language)"]
        AgentResponse["Agent Response<br/>(Generated Output)"]
    end
    
    subgraph "LlamaCppAgent Processing"
        AddMsg["add_message<br/>(Chat History)"]
        GetChatResp["get_chat_response<br/>(Main Processing)"]
        GetRoleComp["get_response_role_and_completion<br/>(Message Pipeline)"]
    end
    
    subgraph "Message Processing"
        FormatConv["format_conversation<br/>(Template Application)"]
        SysPrmMods["System Prompt Modules<br/>(Dynamic Context)"]
        StructDocGen["Structured Output Documentation<br/>(Auto-Generated)"]
    end
    
    subgraph "LLM Provider Interaction"
        CreateComp["create_completion<br/>(Provider Call)"]
        SampSettings["LlmSamplingSettings<br/>(Generation Config)"]
        StructSettings["LlmStructuredOutputSettings<br/>(Output Config)"]
    end
    
    subgraph "Response Processing"
        HandleStructOut["handle_structured_output<br/>(Parse Response)"]
        FuncExecution["Function Execution<br/>(Tool Calls)"]
        StreamCallback["Streaming Callback<br/>(Real-time Output)"]
    end
    
    UserInput --> AddMsg
    AddMsg --> GetChatResp
    GetChatResp --> GetRoleComp
    GetRoleComp --> FormatConv
    FormatConv --> SysPrmMods
    SysPrmMods --> StructDocGen
    StructDocGen --> CreateComp
    
    CreateComp --> SampSettings
    CreateComp --> StructSettings
    CreateComp --> HandleStructOut
    HandleStructOut --> FuncExecution
    HandleStructOut --> StreamCallback
    
    FuncExecution --> GetChatResp
    StreamCallback --> AgentResponse
    HandleStructOut --> AgentResponse
```

**Sources:** [src/llama_cpp_agent/llm_agent.py:237-382](), [src/llama_cpp_agent/llm_agent.py:397-655](), [src/llama_cpp_agent/function_calling_agent.py:223-288]()

### Framework Configuration Options

| Component | Configuration Class | Key Settings |
|-----------|-------------------|--------------|
| Agent | `LlamaCppAgent.__init__` | `provider`, `system_prompt`, `messages_formatter_type`, `debug_output` |
| Message Formatting | `MessagesFormatter` | `prompt_markers`, `default_stop_sequences`, `bos_token`, `eos_token` |
| Structured Output | `LlmStructuredOutputSettings` | `output_type`, `add_thoughts_and_reasoning_field`, `function_calling_name_field_name` |
| Function Calling | `FunctionCallingAgent` | `llama_cpp_function_tools`, `allow_parallel_function_calling`, `system_prompt` |
| System Prompts | `SystemPromptModule` | `section_name`, `position`, `prefix`, `suffix` |

**Sources:** [src/llama_cpp_agent/llm_agent.py:75-117](), [src/llama_cpp_agent/messages_formatter.py:42-61](), [src/llama_cpp_agent/function_calling_agent.py:128-199](), [src/llama_cpp_agent/llm_agent.py:32-46]()

---

