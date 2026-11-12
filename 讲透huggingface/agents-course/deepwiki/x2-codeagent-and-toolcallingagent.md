<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/agents-course · extra page CodeAgent and ToolCallingAgent · fetched 2026-10-26 -->

# CodeAgent and ToolCallingAgent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [units/en/unit2/smolagents/code_agents.mdx](units/en/unit2/smolagents/code_agents.mdx)
- [units/en/unit2/smolagents/final_quiz.mdx](units/en/unit2/smolagents/final_quiz.mdx)
- [units/en/unit2/smolagents/introduction.mdx](units/en/unit2/smolagents/introduction.mdx)
- [units/en/unit2/smolagents/multi_agent_systems.mdx](units/en/unit2/smolagents/multi_agent_systems.mdx)
- [units/en/unit2/smolagents/quiz1.mdx](units/en/unit2/smolagents/quiz1.mdx)
- [units/en/unit2/smolagents/quiz2.mdx](units/en/unit2/smolagents/quiz2.mdx)
- [units/en/unit2/smolagents/retrieval_agents.mdx](units/en/unit2/smolagents/retrieval_agents.mdx)
- [units/en/unit2/smolagents/tool_calling_agents.mdx](units/en/unit2/smolagents/tool_calling_agents.mdx)
- [units/en/unit2/smolagents/tools.mdx](units/en/unit2/smolagents/tools.mdx)
- [units/en/unit2/smolagents/vision_agents.mdx](units/en/unit2/smolagents/vision_agents.mdx)
- [units/en/unit2/smolagents/why_use_smolagents.mdx](units/en/unit2/smolagents/why_use_smolagents.mdx)

</details>



This document covers the two primary agent types in the smolagents framework: `CodeAgent` and `ToolCallingAgent`. These agents represent different approaches to structuring tool calls - through executable Python code versus JSON specifications. Both inherit from the same `MultiStepAgent` base class but handle action execution differently.

For information about tool creation and sharing mechanisms, see section 3.1.2. For multi-agent system orchestration, see section 3.1.2.

## Agent Architecture Overview

Both `CodeAgent` and `ToolCallingAgent` inherit from `MultiStepAgent` and share the same foundational architecture, differing primarily in how they structure and execute actions.

### Shared Architecture Components

```mermaid
graph TB
    subgraph "MultiStepAgent Base Class"
        MSA["MultiStepAgent"]
        MSA --> Logs["LogsContainer"]
        MSA --> MaxSteps["max_steps"]
        MSA --> Planning["planning_interval"]
        
        Logs --> SPS["SystemPromptStep"]
        Logs --> TS["TaskStep"]
        Logs --> AS["ActionStep[]"]
    end
    
    subgraph "Agent Implementations"
        MSA --> CA["CodeAgent"]
        MSA --> TCA["ToolCallingAgent"]
        
        CA --> PE["PythonExecutor"]
        CA --> AuthImports["additional_authorized_imports"]
        
        TCA --> JsonParser["JSON_Tool_Parser"]
        TCA --> ToolCaller["Tool_Caller"]
    end
    
    subgraph "Common Components"
        Tools["Tool[]"] --> CA
        Tools --> TCA
        Model["InferenceClientModel"] --> CA
        Model --> TCA
    end
```

Both agent types share the same logging system, step management, and tool registration mechanisms while implementing different action execution strategies.

Sources: [units/en/unit2/smolagents/code_agents.mdx:37-45](), [units/en/unit2/smolagents/tool_calling_agents.mdx:42-45]()

### Action Structure Comparison

```mermaid
graph LR
    subgraph "CodeAgent Actions"
        CA_Input["User Query"] --> CA_LLM["LLM Generation"]
        CA_LLM --> CA_Code["Python Code"]
        CA_Code --> CA_Exec["Direct Execution"]
        CA_Exec --> CA_Result["Tool Results"]
    end
    
    subgraph "ToolCallingAgent Actions"
        TCA_Input["User Query"] --> TCA_LLM["LLM Generation"]
        TCA_LLM --> TCA_JSON["JSON Structure"]
        TCA_JSON --> TCA_Parse["Parse & Execute"]
        TCA_Parse --> TCA_Result["Tool Results"]
    end
    
    subgraph "Example Outputs"
        CA_Code --> CodeExample["web_search('Batman party music')"]
        TCA_JSON --> JsonExample["{'name': 'web_search', 'arguments': 'Batman party music'}"]
    end
```

The fundamental difference lies in action representation: `CodeAgent` generates executable Python while `ToolCallingAgent` generates structured JSON that requires parsing.

Sources: [units/en/unit2/smolagents/code_agents.mdx:22-33](), [units/en/unit2/smolagents/tool_calling_agents.mdx:16-33]()

## CodeAgent Implementation

`CodeAgent` is the primary agent type in smolagents, generating Python code to perform actions. This approach provides more expressive and composable tool interactions compared to JSON-based alternatives.

### Code Generation and Execution

```mermaid
graph TB
    subgraph "CodeAgent Execution Flow"
        Query["User Query"] --> SystemPrompt["System Prompt + Tools"]
        SystemPrompt --> LLM["InferenceClientModel"]
        LLM --> CodeGen["Python Code Generation"]
        CodeGen --> ParseCode["Parse Code Action"]
        ParseCode --> PythonExec["PythonExecutor"]
        PythonExec --> Results["Execution Results"]
        Results --> ActionStep["ActionStep Logging"]
    end
    
    subgraph "Security Layer"
        PythonExec --> ImportCheck["authorized_imports_check"]
        ImportCheck --> Sandbox["Secure Code Execution"]
        Sandbox --> ToolCall["Tool Function Calls"]
    end
    
    subgraph "Tool Integration"
        DuckTool["DuckDuckGoSearchTool"] --> ToolCall
        CustomTool["@tool functions"] --> ToolCall
        ToolClass["Tool subclasses"] --> ToolCall
    end
```

The `CodeAgent` generates Python code that directly calls tool functions, enabling complex operations like loops and variable management.

Sources: [units/en/unit2/smolagents/code_agents.mdx:35-55](), [units/en/unit2/smolagents/code_agents.mdx:160-162]()

### Example Code Generation

The following demonstrates typical `CodeAgent` output patterns:

| Task Type | Generated Code Example |
|-----------|------------------------|
| Simple Search | `results = web_search(query="Batman party music")` |
| Multiple Queries | `for query in ["catering", "decorations"]: print(web_search(query))` |
| Data Processing | `import pandas as pd; df = pd.DataFrame(results); df.head()` |
| Complex Logic | `if weather == "rainy": venue = indoor_venues() else: venue = outdoor_venues()` |

Sources: [units/en/unit2/smolagents/code_agents.mdx:104-108](), [units/en/unit2/smolagents/code_agents.mdx:168-186]()

## ToolCallingAgent Implementation

`ToolCallingAgent` uses the built-in tool-calling capabilities of LLM providers, generating JSON structures that specify tool names and arguments. This approach aligns with standard API patterns from OpenAI, Anthropic, and similar providers.

### JSON-Based Tool Calling

```mermaid
graph TB
    subgraph "ToolCallingAgent Execution Flow"
        Query["User Query"] --> SystemPrompt["System Prompt + Tool Schemas"]
        SystemPrompt --> LLM["InferenceClientModel"]
        LLM --> JsonGen["JSON Tool Call Generation"]
        JsonGen --> ParseJson["Parse JSON Structure"]
        ParseJson --> ToolExec["Tool Execution"]
        ToolExec --> Results["Tool Results"]
        Results --> ActionStep["ActionStep Logging"]
    end
    
    subgraph "Tool Call Structure"
        JsonGen --> ToolCall["{'name': 'tool_name', 'arguments': {...}}"]
        ToolCall --> ToolRegistry["Tool Registry Lookup"]
        ToolRegistry --> FunctionCall["Function Invocation"]
    end
    
    subgraph "Provider Integration"
        LLM --> OpenAI["OpenAI API"]
        LLM --> Anthropic["Anthropic API"]
        LLM --> HF["Hugging Face API"]
    end
```

The `ToolCallingAgent` leverages native tool-calling capabilities of language model providers, generating structured JSON that gets parsed and executed.

Sources: [units/en/unit2/smolagents/tool_calling_agents.mdx:14-45]()

### Execution Trace Comparison

| Agent Type | Execution Output | Description |
|------------|------------------|-------------|
| `CodeAgent` | `Executing parsed code: web_search(query="Batman music")` | Direct Python code execution |
| `ToolCallingAgent` | `Calling tool: 'web_search' with arguments: {'query': "Batman music"}` | JSON structure parsing and tool invocation |

Sources: [units/en/unit2/smolagents/tool_calling_agents.mdx:59-66]()

## Shared Execution Workflow

Both agent types implement the same ReAct (Reasoning, Acting, Observing) pattern through the inherited `MultiStepAgent` architecture.

### Common ReAct Cycle

```mermaid
graph TB
    subgraph "Shared MultiStepAgent Workflow"
        Start["agent.run()"] --> WM["write_memory_to_messages()"]
        WM --> MC["model_completion"]
        MC --> Parse["parse_action"]
        Parse --> Execute["execute_action"]
        Execute --> Log["log_results_ActionStep"]
        Log --> Callbacks["step_callbacks"]
        Callbacks --> Check{"max_steps_reached?"}
        Check -->|No| WM
        Check -->|Yes| End["final_answer"]
    end
    
    subgraph "Agent-Specific Parsing"
        Parse --> CodeParse["CodeAgent: parse_code_action"]
        Parse --> JsonParse["ToolCallingAgent: parse_json_tools"]
    end
    
    subgraph "Agent-Specific Execution"
        Execute --> CodeExec["CodeAgent: PythonExecutor"]
        Execute --> JsonExec["ToolCallingAgent: Tool.forward()"]
    end
```

The workflow remains identical, with differences only in action parsing and execution methods.

Sources: [units/en/unit2/smolagents/code_agents.mdx:42-55](), [units/en/unit2/smolagents/tool_calling_agents.mdx:42-45]()

### Memory Management System

```mermaid
graph TB
    subgraph "LogsContainer Structure"
        LC["LogsContainer"] --> SPS["SystemPromptStep"]
        LC --> TS["TaskStep"]
        LC --> AS1["ActionStep_1"]
        LC --> ASN["ActionStep_n"]
        
        SPS --> SPContent["system_prompt + tool_descriptions"]
        TS --> TSContent["user_query + task_images"]
        AS1 --> ASContent["action + observations + observations_images"]
    end
    
    subgraph "Context Building"
        SPContent --> Messages["chat_messages[]"]
        TSContent --> Messages
        ASContent --> Messages
        Messages --> ModelInput["Model Context Window"]
    end
```

Both agent types use the same memory management and context building mechanisms through the shared `LogsContainer` system.

Sources: [units/en/unit2/smolagents/vision_agents.mdx:103-109](), [units/en/unit2/smolagents/code_agents.mdx:42-55]()

## Multi-Agent Orchestration

### Agent Composition Patterns

Multi-agent systems in smolagents enable task distribution across specialized agents, improving modularity and reducing token usage per agent.

```mermaid
graph TB
    subgraph "Multi-Agent Architecture"
        MA[ManagerAgent] --> WA[WebAgent]
        MA --> CA[CodeAgent_specialized]
        MA --> RA[RetrievalAgent]
        
        MA --> MAC[managed_agents_list]
        MAC --> Delegation[task_delegation]
    end
    
    subgraph "Agent Specialization"
        WA --> WST[WebSearchTool]
        WA --> VWT[VisitWebpageTool]
        
        CA --> PI[plotting_imports]
        CA --> DA[data_analysis_tools]
        
        RA --> RT[retrieval_tools]
        RA --> VDB[vector_database_access]
    end
    
    subgraph "Coordination"
        Delegation --> Sub_Tasks[specialized_subtasks]
        Sub_Tasks --> Results_Aggregation[manager_synthesis]
        Results_Aggregation --> Final_Output[coordinated_response]
    end
```

Manager agents coordinate specialized sub-agents, each with focused toolsets and capabilities.

Sources: [units/en/unit2/smolagents/multi_agent_systems.mdx:226-314]()

### Memory Separation Benefits

```mermaid
graph LR
    subgraph "Single Agent Limitations"
        SA[Single_Agent] --> LM[Large_Memory]
        LM --> TC[Token_Consumption]
        LM --> CM[Context_Mixing]
        CM --> Performance_Degradation
    end
    
    subgraph "Multi-Agent Benefits"
        MA[Manager_Agent] --> SM1[Separate_Memory_1]
        WA[Web_Agent] --> SM2[Separate_Memory_2] 
        CA[Code_Agent] --> SM3[Separate_Memory_3]
        
        SM1 --> RT[Reduced_Tokens]
        SM2 --> FS[Focused_Specialization]
        SM3 --> IP[Improved_Performance]
    end
```

Separating agent memories reduces token counts and allows each agent to maintain focused context for their specialized tasks.

Sources: [units/en/unit2/smolagents/multi_agent_systems.mdx:228-231]()

## Advanced Capabilities

### Vision Integration

The `CodeAgent` supports vision-language models for processing images alongside text instructions, enabling multimodal agent capabilities.

```mermaid
graph TB
    subgraph "Vision Workflow"
        TI[task_images] --> TS[TaskStep]
        SC[save_screenshot] --> AS[ActionStep]
        AS --> OI[observations_images]
        
        TS --> MM[multimodal_messages]
        OI --> MM
        MM --> VLM[Vision_Language_Model]
        VLM --> VC[visual_code_generation]
    end
    
    subgraph "Dynamic Image Capture"
        SC --> SCB[step_callbacks]
        SCB --> SS[screenshot_save]
        SS --> IC[image_copy]
        IC --> Memory[agent_memory]
    end
    
    subgraph "Browser Automation"
        VC --> HAT[helium_automation_tools]
        HAT --> WN[web_navigation]
        WN --> VI[visual_inspection]
        VI --> SC
    end
```

Vision agents can process initial images and dynamically capture screenshots during web browsing or other visual tasks.

Sources: [units/en/unit2/smolagents/vision_agents.mdx:154-176]()

### Security and Code Execution

```mermaid
graph TB
    subgraph "Code Security"
        CG[generated_code] --> AI[authorized_imports_check]
        AI --> BL[blocked_imports_list]
        AI --> AL[additional_authorized_imports]
        
        AL --> SE[secure_execution]
        SE --> CS[code_sandbox]
        CS --> RL[resource_limits]
    end
    
    subgraph "Import Control"
        BL --> Restricted["sys, os, subprocess, etc"]
        AL --> Allowed["datetime, pandas, plotly, etc"]
        Allowed --> User_Specified[user_authorized_list]
    end
```

The execution environment restricts dangerous imports while allowing user-specified safe modules for specialized tasks.

Sources: [units/en/unit2/smolagents/code_agents.mdx:160-162]()

### Hub Integration and Sharing

```mermaid
graph LR
    subgraph "Agent Sharing"
        CA[CodeAgent] --> PTH[push_to_hub]
        PTH --> HR[hub_repository]
        HR --> AS[agent_space]
        
        FH[from_hub] --> LA[loaded_agent]
        LA --> TRC[trust_remote_code]
    end
    
    subgraph "Tool Sharing"
        TC[Tool_Class] --> PTH2[push_to_hub]
        PTH2 --> TR[tool_repository]
        
        LT[load_tool] --> TI[tool_import]
        TI --> AU[agent_usage]
    end
```

Agents and tools can be shared via Hugging Face Hub, enabling community reuse and collaboration.

Sources: [units/en/unit2/smolagents/code_agents.mdx:194-213]()

The `CodeAgent` architecture provides a flexible foundation for building sophisticated AI agents that can reason, plan, and execute complex tasks through code generation and tool orchestration. Its integration with the broader smolagents ecosystem enables rapid prototyping and deployment of capable agent systems.

---

