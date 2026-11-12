<!-- source: DeepWiki mcp.deepwiki.com · repo kyegomez/swarms · page 4 Tool System · fetched 2026-10-27 -->

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/examples/agent_stream.md](docs/examples/agent_stream.md)
- [docs/swarms/examples/model_providers.md](docs/swarms/examples/model_providers.md)
- [examples/multi_agent/groupchat/quantum_physics_swarm.py](examples/multi_agent/groupchat/quantum_physics_swarm.py)
- [examples/multi_agent/mixture_of_agents_example.py](examples/multi_agent/mixture_of_agents_example.py)
- [examples/ui/chat.py](examples/ui/chat.py)
- [swarms/prompts/multi_modal_visual_prompts.py](swarms/prompts/multi_modal_visual_prompts.py)
- [swarms/tools/base_tool.py](swarms/tools/base_tool.py)
- [swarms/tools/tool_registry.py](swarms/tools/tool_registry.py)
- [swarms/utils/formatter.py](swarms/utils/formatter.py)
- [swarms/utils/litellm_wrapper.py](swarms/utils/litellm_wrapper.py)

</details>



The Tool System provides a comprehensive framework for extending agent capabilities through function calling and tool integration. It enables agents to execute Python functions, access external APIs, and interact with various services through a unified interface that converts functions to OpenAI-compatible schemas and manages their execution.

For information about integrating tools with specific models, see [Model Integration](#5). For details on agent-tool interaction patterns, see [Core Agent System](#2).

## Architecture Overview

The Tool System consists of three primary layers that work together to provide seamless function calling capabilities:

### Tool System Architecture

```mermaid
graph TB
    subgraph "Tool Definition Layer"
        PythonFunctions["Python Functions"]
        PydanticModels["Pydantic Models"]
        Decorators["@tool_registry Decorator"]
    end
    
    subgraph "Management Layer"
        ToolStorage["ToolStorage"]
        BaseTool["BaseTool"]
        FunctionMap["Function Mapping"]
    end
    
    subgraph "Execution Layer"
        LiteLLM["LiteLLM Wrapper"]
        SchemaConversion["Schema Conversion"]
        ToolExecution["Tool Execution"]
    end
    
    subgraph "Agent Integration"
        Agent["Agent Class"]
        ModelResponse["Model Response"]
        ToolResults["Tool Results"]
    end
    
    PythonFunctions --> Decorators
    PydanticModels --> Decorators
    Decorators --> ToolStorage
    
    ToolStorage --> BaseTool
    BaseTool --> FunctionMap
    
    BaseTool --> SchemaConversion
    SchemaConversion --> LiteLLM
    LiteLLM --> Agent
    
    Agent --> ModelResponse
    ModelResponse --> ToolExecution
    ToolExecution --> ToolResults
    ToolResults --> Agent
```

Sources: [swarms/tools/base_tool.py:69-106](), [swarms/tools/tool_registry.py:30-64](), [swarms/utils/litellm_wrapper.py:83-155]()

## Core Components

### BaseTool Management System

The `BaseTool` class serves as the central orchestrator for tool operations, providing schema conversion, validation, and execution capabilities.

```mermaid
graph LR
    subgraph "BaseTool Core Methods"
        func_to_dict["func_to_dict()"]
        base_model_to_dict["base_model_to_dict()"]
        execute_tool["execute_tool()"]
        dynamic_run["dynamic_run()"]
    end
    
    subgraph "Schema Generation"
        get_openai_function_schema_from_func["get_openai_function_schema_from_func"]
        base_model_to_openai_function["base_model_to_openai_function"]
        function_to_str["function_to_str"]
    end
    
    subgraph "Tool Execution"
        parse_and_execute_json["parse_and_execute_json"]
        function_map["function_map"]
        tool_validation["Tool Validation"]
    end
    
    func_to_dict --> get_openai_function_schema_from_func
    base_model_to_dict --> base_model_to_openai_function
    execute_tool --> parse_and_execute_json
    parse_and_execute_json --> function_map
    dynamic_run --> tool_validation
```

Sources: [swarms/tools/base_tool.py:142-173](), [swarms/tools/base_tool.py:231-315](), [swarms/tools/base_tool.py:527-592]()

| Method | Purpose | Input Type | Output Type |
|--------|---------|------------|-------------|
| `func_to_dict` | Convert function to OpenAI schema | `Callable` | `Dict[str, Any]` |
| `base_model_to_dict` | Convert Pydantic model to schema | `type[BaseModel]` | `Dict[str, Any]` |
| `execute_tool` | Execute tool from JSON response | `str` | `Callable` |
| `dynamic_run` | Auto-detect and process input | `Any` | `str` |

### ToolStorage Registry

The `ToolStorage` class provides a centralized registry for managing tool functions with metadata tracking and concurrent operations.

```mermaid
graph TB
    subgraph "ToolStorage Components"
        tools_dict["_tools: Dict[str, Callable]"]
        settings_dict["_settings: Dict[str, Any]"]
        tool_metadata["ToolMetadata"]
        thread_pool["ThreadPoolExecutor"]
    end
    
    subgraph "Core Operations"
        add_tool["add_tool()"]
        get_tool["get_tool()"]
        add_many_tools["add_many_tools()"]
        list_tools["list_tools()"]
    end
    
    subgraph "Metadata Management"
        ToolStorageSchema["ToolStorageSchema"]
        add_tool_to_log["add_tool_to_log()"]
        time_tracking["Time Tracking"]
    end
    
    add_tool --> tools_dict
    add_tool --> add_tool_to_log
    add_many_tools --> thread_pool
    get_tool --> tools_dict
    list_tools --> ToolStorageSchema
    add_tool_to_log --> tool_metadata
```

Sources: [swarms/tools/tool_registry.py:66-92](), [swarms/tools/tool_registry.py:113-134](), [swarms/tools/tool_registry.py:175-192]()

### Tool Registration Decorator

The `@tool_registry` decorator provides a convenient way to register functions as tools automatically:

```python
@tool_registry(storage)
def example_tool(a: int, b: int) -> int:
    """An example tool that adds two numbers."""
    return a + b
```

Sources: [swarms/tools/tool_registry.py:194-225]()

## Schema Conversion Process

The Tool System converts Python functions and Pydantic models into OpenAI-compatible function calling schemas through a standardized process:

### Function to Schema Conversion Flow

```mermaid
graph TD
    subgraph "Input Types"
        python_func["Python Function"]
        pydantic_model["Pydantic Model"]
        dict_input["Dictionary Input"]
    end
    
    subgraph "Type Detection"
        detect_tool_input_type["detect_tool_input_type()"]
    end
    
    subgraph "Schema Generators"
        get_openai_function_schema_from_func["get_openai_function_schema_from_func"]
        base_model_to_openai_function["base_model_to_openai_function"]
        function_to_str["function_to_str"]
    end
    
    subgraph "Output Format"
        openai_schema["OpenAI Function Schema"]
        schema_validation["Schema Validation"]
    end
    
    python_func --> detect_tool_input_type
    pydantic_model --> detect_tool_input_type
    dict_input --> detect_tool_input_type
    
    detect_tool_input_type --> get_openai_function_schema_from_func
    detect_tool_input_type --> base_model_to_openai_function
    detect_tool_input_type --> function_to_str
    
    get_openai_function_schema_from_func --> openai_schema
    base_model_to_openai_function --> openai_schema
    function_to_str --> openai_schema
    
    openai_schema --> schema_validation
```

Sources: [swarms/tools/base_tool.py:593-619](), [swarms/tools/base_tool.py:620-715]()

The schema conversion process ensures that all tools are represented in a consistent format that LLM providers can understand and execute.

## Tool Execution Pipeline

When an agent receives a tool call from the model, the execution pipeline processes the request through several validation and execution stages:

### Tool Execution Flow

```mermaid
graph TB
    subgraph "Model Response"
        llm_response["LLM Tool Call Response"]
        json_parsing["JSON Parsing"]
        tool_name_extraction["Tool Name Extraction"]
    end
    
    subgraph "Tool Resolution"
        function_map_lookup["Function Map Lookup"]
        tool_validation["Tool Validation"]
        parameter_validation["Parameter Validation"]
    end
    
    subgraph "Execution"
        tool_execution["Tool Execution"]
        error_handling["Error Handling"]
        result_processing["Result Processing"]
    end
    
    subgraph "Response Handling"
        result_formatting["Result Formatting"]
        conversation_update["Conversation Update"]
        agent_response["Agent Response"]
    end
    
    llm_response --> json_parsing
    json_parsing --> tool_name_extraction
    tool_name_extraction --> function_map_lookup
    function_map_lookup --> tool_validation
    tool_validation --> parameter_validation
    parameter_validation --> tool_execution
    tool_execution --> error_handling
    error_handling --> result_processing
    result_processing --> result_formatting
    result_formatting --> conversation_update
    conversation_update --> agent_response
```

Sources: [swarms/tools/base_tool.py:527-592](), [swarms/tools/base_tool.py:716-797](), [swarms/tools/base_tool.py:798-882]()

## LiteLLM Tool Integration

The `LiteLLM` wrapper class provides the bridge between the Tool System and various language model providers, handling tool schema transmission and response processing:

### LiteLLM Tool Configuration

```mermaid
graph LR
    subgraph "Tool Configuration"
        tools_list_dictionary["tools_list_dictionary"]
        tool_choice["tool_choice"]
        parallel_tool_calls["parallel_tool_calls"]
        mcp_call["mcp_call"]
    end
    
    subgraph "Model Integration"
        completion_params["completion() parameters"]
        model_providers["Model Providers"]
        response_processing["Response Processing"]
    end
    
    subgraph "Tool Response Handling"
        output_for_tools["output_for_tools()"]
        tool_calls_extraction["Tool Calls Extraction"]
        function_arguments["Function Arguments"]
    end
    
    tools_list_dictionary --> completion_params
    tool_choice --> completion_params
    parallel_tool_calls --> completion_params
    completion_params --> model_providers
    model_providers --> response_processing
    response_processing --> output_for_tools
    output_for_tools --> tool_calls_extraction
    tool_calls_extraction --> function_arguments
```

Sources: [swarms/utils/litellm_wrapper.py:98-155](), [swarms/utils/litellm_wrapper.py:156-172](), [swarms/utils/litellm_wrapper.py:502-515]()

| Configuration Parameter | Purpose | Default Value |
|------------------------|---------|---------------|
| `tools_list_dictionary` | List of tool schemas | `None` |
| `tool_choice` | Tool selection strategy | `"auto"` |
| `parallel_tool_calls` | Enable concurrent tool execution | `False` |
| `mcp_call` | Model Control Protocol mode | `False` |

## Error Handling and Validation

The Tool System includes comprehensive error handling through custom exception classes that provide detailed error information:

### Exception Hierarchy

```mermaid
graph TB
    BaseToolError["BaseToolError"]
    
    BaseToolError --> ToolValidationError["ToolValidationError"]
    BaseToolError --> ToolExecutionError["ToolExecutionError"]
    BaseToolError --> ToolNotFoundError["ToolNotFoundError"]
    BaseToolError --> FunctionSchemaError["FunctionSchemaError"]
    BaseToolError --> ToolDocumentationError["ToolDocumentationError"]
    BaseToolError --> ToolTypeHintError["ToolTypeHintError"]
    
    ToolValidationError --> input_validation["Input Validation Failures"]
    ToolExecutionError --> execution_failures["Tool Execution Failures"]
    ToolNotFoundError --> missing_tools["Missing Tool Functions"]
    FunctionSchemaError --> schema_conversion_errors["Schema Conversion Errors"]
    ToolDocumentationError --> documentation_issues["Documentation Problems"]
    ToolTypeHintError --> type_hint_problems["Type Hint Issues"]
```

Sources: [swarms/tools/base_tool.py:23-64]()

## Integration with Agent System

The Tool System integrates seamlessly with the Agent class through the `BaseTool` manager, enabling agents to execute functions as part of their conversation flow:

### Agent-Tool Integration

```mermaid
graph TB
    subgraph "Agent Configuration"
        agent_init["Agent.__init__()"]
        base_tool_manager["BaseTool Manager"]
        tools_configuration["Tools Configuration"]
    end
    
    subgraph "Conversation Flow"
        user_input["User Input"]
        llm_processing["LLM Processing"]
        tool_call_detection["Tool Call Detection"]
    end
    
    subgraph "Tool Execution"
        tool_schema_lookup["Tool Schema Lookup"]
        function_execution["Function Execution"]
        result_integration["Result Integration"]
    end
    
    subgraph "Response Generation"
        conversation_update["Conversation Update"]
        final_response["Final Response"]
    end
    
    agent_init --> base_tool_manager
    base_tool_manager --> tools_configuration
    tools_configuration --> user_input
    user_input --> llm_processing
    llm_processing --> tool_call_detection
    tool_call_detection --> tool_schema_lookup
    tool_schema_lookup --> function_execution
    function_execution --> result_integration
    result_integration --> conversation_update
    conversation_update --> final_response
```

Sources: [swarms/utils/litellm_wrapper.py:455-552](), [swarms/tools/base_tool.py:527-592]()

The Tool System provides a robust, scalable foundation for extending agent capabilities through function calling, with comprehensive error handling, validation, and integration across multiple model providers.

---

