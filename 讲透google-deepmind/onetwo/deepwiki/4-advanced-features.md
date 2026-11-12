<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/onetwo · page 4 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [onetwo/agents/python_planning.py](onetwo/agents/python_planning.py)
- [onetwo/agents/python_planning_test.py](onetwo/agents/python_planning_test.py)
- [onetwo/agents/react.py](onetwo/agents/react.py)
- [onetwo/agents/react_test.py](onetwo/agents/react_test.py)
- [onetwo/stdlib/reasoning/chain_of_thought.py](onetwo/stdlib/reasoning/chain_of_thought.py)
- [onetwo/stdlib/reasoning/chain_of_thought_test.py](onetwo/stdlib/reasoning/chain_of_thought_test.py)

</details>



This page documents OneTwo's sophisticated prompting strategies, agent frameworks, and composition patterns for complex multi-step reasoning tasks. These features enable the construction of agents that can perform iterative reasoning, execute tools, and compose complex prompting workflows.

For basic prompting and LLM integration, see [Built-in Functions](#3.1). For evaluation of these advanced strategies, see [Agent Evaluation](#5.2).

## Agent Framework Overview

OneTwo provides a unified agent framework that supports multiple reasoning strategies through a common interface. Agents maintain serializable state and can perform stepwise execution with support for stop/restart and parallel trajectory exploration.

```mermaid
graph TB
    subgraph "Agent Base Classes"
        AgentBase["agents_base.Agent<br/>Abstract base interface"]
        SingleSample["agents_base.SingleSampleAgent<br/>Single trajectory agents"]
        UpdateList["agents_base.UpdateListState<br/>Sequential state management"]
    end
    
    subgraph "Concrete Agent Implementations"
        ReactAgent["react.ReActAgent<br/>Thought→Action→Observation"]
        PythonAgent["python_planning.PythonPlanningAgent<br/>Iterative code generation"]
    end
    
    subgraph "State Management"
        ReactState["react.ReActState<br/>UpdateListState[ReActStep]"]
        PythonState["python_planning.PythonPlanningState<br/>UpdateListState[PythonPlanningStep]"]
    end
    
    subgraph "Environment Integration"
        ToolEnv["python_tool_use.PythonToolUseEnvironment<br/>Sandboxed execution context"]
        ToolConfig["python_tool_use.PythonToolUseEnvironmentConfig<br/>Tool registry and settings"]
    end
    
    AgentBase --> SingleSample
    SingleSample --> ReactAgent
    SingleSample --> PythonAgent
    
    ReactAgent --> ReactState
    PythonAgent --> PythonState
    
    UpdateList --> ReactState
    UpdateList --> PythonState
    
    ReactAgent --> ToolEnv
    PythonAgent --> ToolEnv
    ToolEnv --> ToolConfig
```

Sources: [onetwo/agents/agents_base.py](), [onetwo/agents/react.py:678-686](), [onetwo/agents/python_planning.py:486-495]()

## ReAct Agent Strategy

The ReAct (Reasoning and Acting) agent implements the thought-action-observation loop, where the LLM alternates between reasoning about the problem and executing actions through tools.

### ReAct Agent Architecture

```mermaid
graph TB
    subgraph "ReAct Components"
        ReactAgent["react.ReActAgent<br/>Main agent implementation"]
        ReactPrompt["react.ReActPromptProtocol<br/>Prompt template interface"]
        ReactParse["react.ReActParseProtocol<br/>LLM reply parser"]
    end
    
    subgraph "Prompt Implementations"
        PromptJ2["react.ReActPromptJ2<br/>Jinja2 template"]
        PromptComp["react.ReActPromptComposable<br/>Composable template"]
    end
    
    subgraph "State Structure"
        ReactStep["react.ReActStep<br/>thought, action, observation"]
        FunctionCall["llm_tool_use.FunctionCall<br/>function_name, args, kwargs"]
    end
    
    subgraph "Execution Flow"
        StartEnv["start_environment()"]
        SampleStep["_sample_single_next_step()"]
        ParseReply["parse(llm_reply)"]
        RunTool["environment.run_tool()"]
    end
    
    ReactAgent --> ReactPrompt
    ReactAgent --> ReactParse
    ReactPrompt --> PromptJ2
    ReactPrompt --> PromptComp
    
    ReactStep --> FunctionCall
    
    ReactAgent --> StartEnv
    StartEnv --> SampleStep
    SampleStep --> ParseReply
    ParseReply --> RunTool
```

Sources: [onetwo/agents/react.py:677-719](), [onetwo/agents/react.py:306-343](), [onetwo/agents/react.py:770-846]()

### ReAct Execution Flow

The ReAct agent follows a structured execution pattern:

| Phase | Component | Description |
|-------|-----------|-------------|
| **Prompt Generation** | `ReActPromptProtocol.__call__` | Creates prompt with tools, exemplars, and current state |
| **LLM Interaction** | `llm.generate_text` or `llm.chat` | Gets reasoning and action from LLM |
| **Response Parsing** | `react_parse()` | Extracts thought, action, and determines if finished |
| **Tool Execution** | `environment.run_tool()` | Executes the selected action and captures observation |
| **State Update** | `ReActState.updates.append()` | Adds new step to agent state |

The parsing function `react_parse()` at [onetwo/agents/react.py:580-675]() handles multiple formats including `[Thought]:`, `[Act]:`, and `[Finish]:` patterns.

Sources: [onetwo/agents/react.py:770-846](), [onetwo/agents/react.py:580-675]()

## Python Planning Agent Strategy

The Python Planning agent generates and executes Python code iteratively, building up a solution through sequential code blocks with tool function calls.

### Python Planning Architecture

```mermaid
graph TB
    subgraph "Python Planning Components"
        PythonAgent["python_planning.PythonPlanningAgent<br/>Iterative code execution"]
        PythonPrompt["python_planning.PythonPlanningPromptProtocol<br/>Code generation prompt"]
        CodeParser["python_planning._parse_llm_reply_code()<br/>Code fence extraction"]
    end
    
    subgraph "Prompt Templates"
        J2Prompt["python_planning.PythonPlanningPromptJ2<br/>Jinja2 implementation"]
        CompPrompt["python_planning.PythonPlanningPromptComposable<br/>Composable implementation"]
    end
    
    subgraph "Execution Environment"
        Sandbox["python_tool_use.PythonToolUseEnvironment<br/>Code execution sandbox"]
        SandboxState["python_execution.SandboxResult<br/>stdout, final_expression_value"]
        ExitHook["result.exit_hook_called<br/>Completion detection"]
    end
    
    subgraph "State Tracking"
        PythonStep["python_planning.PythonPlanningStep<br/>code, result, execution_status"]
        ExecutionStatus["python_execution.ExecutionStatus<br/>SUCCESS, EXECUTION_ERROR, etc."]
    end
    
    PythonAgent --> PythonPrompt
    PythonAgent --> CodeParser
    PythonPrompt --> J2Prompt
    PythonPrompt --> CompPrompt
    
    PythonAgent --> Sandbox
    Sandbox --> SandboxState
    Sandbox --> ExitHook
    
    PythonStep --> ExecutionStatus
```

Sources: [onetwo/agents/python_planning.py:486-525](), [onetwo/agents/python_planning.py:324-366](), [onetwo/agents/python_planning.py:568-647]()

### Code Generation and Execution

The Python Planning agent operates through these key functions:

1. **Code Generation**: `PythonPlanningPromptProtocol.__call__()` generates the next Python code block
2. **Code Parsing**: `_parse_llm_reply_code()` at [onetwo/agents/python_planning.py:153-182]() extracts code from LLM response, handling various fence formats
3. **Code Execution**: `environment.run_code()` executes code in sandbox with tool access
4. **Result Processing**: `_get_result_str()` at [onetwo/agents/python_planning.py:93-132]() formats execution results for LLM

The agent continues until either `exit()` is called in the code or an irrecoverable error occurs.

Sources: [onetwo/agents/python_planning.py:568-647](), [onetwo/agents/python_planning.py:153-182](), [onetwo/agents/python_planning.py:93-132]()

## Chain of Thought Reasoning

OneTwo provides multiple Chain of Thought implementations for structured reasoning without tool use.

### Chain of Thought Strategy Comparison

```mermaid
graph LR
    subgraph "CoT Implementations"
        J2Simple["chain_of_thought.QACoTPromptJ2<br/>Two-step generation"]
        ChatSimple["chain_of_thought.QACoTPromptChat<br/>Chat-based reasoning"]
        J2Parser["chain_of_thought.QACoTPromptWithAnswerParserJ2<br/>Single call + parsing"]
        ChatParser["chain_of_thought.QACoTPromptWithAnswerParserChat<br/>Chat + parsing"]
    end
    
    subgraph "Output Processing"
        CoTReply["chain_of_thought.CoTReply<br/>reasoning + answer"]
        AnswerParser["chain_of_thought.default_cot_parse_answer<br/>Delimiter-based parsing"]
    end
    
    subgraph "Few-Shot Support"
        Exemplars["chain_of_thought.QACoTExemplar<br/>question + reasoning + answer"]
        MathExemplars["QA_COT_EXEMPLARS_ORIGINAL_MATH_WORD_PROBLEMS<br/>Math word problem examples"]
    end
    
    J2Simple --> CoTReply
    ChatSimple --> CoTReply
    J2Parser --> AnswerParser
    ChatParser --> AnswerParser
    AnswerParser --> CoTReply
    
    Exemplars --> J2Simple
    Exemplars --> ChatSimple
    MathExemplars --> J2Parser
    MathExemplars --> ChatParser
```

Sources: [onetwo/stdlib/reasoning/chain_of_thought.py:105-140](), [onetwo/stdlib/reasoning/chain_of_thought.py:276-311](), [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]()

### CoT Implementation Patterns

| Strategy | Template Calls | Parsing | Use Case |
|----------|---------------|---------|----------|
| `QACoTPromptJ2` | 2 (`reasoning` + `answer`) | Built-in | Clean separation of reasoning/answer |
| `QACoTPromptChat` | 2 (chat messages) | Built-in | Conversational reasoning |
| `QACoTPromptWithAnswerParserJ2` | 1 (`reasoning_and_answer`) | External parser | Single-shot with delimiter parsing |
| `QACoTPromptWithAnswerParserChat` | 1 (chat) | External parser | Chat-based single-shot |

The default answer parser at [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]() handles formats like "The answer is X" with fallback to treating the entire response as the answer.

Sources: [onetwo/stdlib/reasoning/chain_of_thought.py:105-140](), [onetwo/stdlib/reasoning/chain_of_thought.py:410-471](), [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]()

## Composables and Templating

OneTwo supports complex prompt composition through the composables system and multiple templating approaches.

### Template Integration Patterns

```mermaid
graph TB
    subgraph "Templating Systems"
        Jinja2["templating.JinjaTemplate<br/>Jinja2-based templates"]
        Composables["composing.Composable<br/>Functional composition"]
        PromptTemplate["prompt_templating.JinjaTemplateWithCallbacks<br/>LLM callback integration"]
    end
    
    subgraph "Agent Template Usage"
        ReactJ2["react.ReActPromptJ2<br/>DEFAULT_REACT_PROMPT_TEXT"]
        ReactComp["react.ReActPromptComposable<br/>_build_tools_description()"]
        PythonJ2["python_planning.PythonPlanningPromptJ2<br/>DEFAULT_PYTHON_PLANNING_PROMPT_TEXT"]
        PythonComp["python_planning.PythonPlanningPromptComposable<br/>_render_tools()"]
    end
    
    subgraph "Content System Integration"
        Content["content_lib.ChunkList<br/>Multimodal content"]
        Messages["content_lib.Message<br/>Role-based messages"]
        Roles["content_lib.PredefinedRole<br/>USER, MODEL, SYSTEM"]
    end
    
    Jinja2 --> ReactJ2
    Jinja2 --> PythonJ2
    PromptTemplate --> ReactJ2
    PromptTemplate --> PythonJ2
    
    Composables --> ReactComp
    Composables --> PythonComp
    
    Content --> ReactComp
    Content --> PythonComp
    Messages --> Content
    Roles --> Messages
```

Sources: [onetwo/agents/react.py:102-167](), [onetwo/agents/react.py:387-555](), [onetwo/agents/python_planning.py:201-252](), [onetwo/agents/python_planning.py:368-483]()

### Composable Strategy Construction

The composable system enables functional prompt construction:

```python
# Example composable pattern from ReActPromptComposable
e = composables.c(content_lib.ChunkList())
e += self._build_tools_description(tools)
e += self._build_react_fewshots(exemplars, stop_prefix)
e += self._build_question(state, stop_prefix)
e += composables.store('llm_reply', composables.chat(stop=stop_sequences))
```

This pattern is used in [onetwo/agents/react.py:525-555]() and [onetwo/agents/python_planning.py:455-483]() to build complex multi-part prompts.

Sources: [onetwo/agents/react.py:525-555](), [onetwo/agents/python_planning.py:455-483]()

## Tool Environment Integration

All advanced agents integrate with the Python Tool Use Environment for executing actions in a controlled sandbox.

### Environment Architecture

```mermaid
graph TB
    subgraph "Environment Management"
        EnvConfig["python_tool_use.PythonToolUseEnvironmentConfig<br/>tools, sandbox_config"]
        Environment["python_tool_use.PythonToolUseEnvironment<br/>Execution context"]
        ContextManager["start_environment()<br/>Async context manager"]
    end
    
    subgraph "Tool System"
        ToolDef["llm_tool_use.Tool<br/>name, function, description"]
        ToolHandler["run_tool()<br/>Function dispatch"]
        PythonSandbox["python_execution.PythonSandbox<br/>Code execution"]
    end
    
    subgraph "Agent Integration"
        ReactStart["react.ReActAgent.start_environment()"]
        PythonStart["python_planning.PythonPlanningAgent.start_environment()"]
        RunCode["environment.run_code()"]
        RunTool["environment.run_tool()"]
    end
    
    EnvConfig --> Environment
    Environment --> ContextManager
    
    ToolDef --> ToolHandler
    ToolHandler --> PythonSandbox
    
    ReactStart --> ContextManager
    PythonStart --> ContextManager
    Environment --> RunCode
    Environment --> RunTool
```

Sources: [onetwo/agents/react.py:747-768](), [onetwo/agents/python_planning.py:545-566](), [onetwo/stdlib/tool_use/python_tool_use.py]()

### Usage Pattern

Both agent types follow the same environment pattern:

```python
async with agent.start_environment() as env:
    state = await agent.initialize_state(inputs)
    while not agent.is_finished(state):
        next_step = await agent._sample_single_next_step(
            state=state, environment=env
        )
        state = state.append_update(next_step)
    return agent.extract_output(state)
```

This pattern is implemented in the base agent classes and provides consistent tool access across different strategies.

Sources: [onetwo/agents/react.py:747-768](), [onetwo/agents/python_planning.py:545-566]()

# Advanced Features

This page documents OneTwo's sophisticated prompting strategies, agent frameworks, and composition patterns for complex multi-step reasoning tasks. These features enable the construction of agents that can perform iterative reasoning, execute tools, and compose complex prompting workflows.

For basic prompting and LLM integration, see [Built-in Functions](#3.1). For evaluation of these advanced strategies, see [Agent Evaluation](#5.2).

## Agent Framework Overview

OneTwo provides a unified agent framework that supports multiple reasoning strategies through a common interface. Agents maintain serializable state and can perform stepwise execution with support for stop/restart and parallel trajectory exploration.

**Agent Framework Architecture**

```mermaid
graph TB
    subgraph "Agent Base Classes"
        AgentBase["agents_base.Agent<br/>Abstract base interface"]
        SingleSample["agents_base.SingleSampleAgent<br/>Single trajectory agents"]
        UpdateList["agents_base.UpdateListState<br/>Sequential state management"]
    end
    
    subgraph "Concrete Agent Implementations"
        ReactAgent["react.ReActAgent<br/>Thought→Action→Observation"]
        PythonAgent["python_planning.PythonPlanningAgent<br/>Iterative code generation"]
    end
    
    subgraph "State Management"
        ReactState["react.ReActState<br/>UpdateListState[ReActStep]"]
        PythonState["python_planning.PythonPlanningState<br/>UpdateListState[PythonPlanningStep]"]
    end
    
    subgraph "Environment Integration"
        ToolEnv["python_tool_use.PythonToolUseEnvironment<br/>Sandboxed execution context"]
        ToolConfig["python_tool_use.PythonToolUseEnvironmentConfig<br/>Tool registry and settings"]
    end
    
    AgentBase --> SingleSample
    SingleSample --> ReactAgent
    SingleSample --> PythonAgent
    
    ReactAgent --> ReactState
    PythonAgent --> PythonState
    
    UpdateList --> ReactState
    UpdateList --> PythonState
    
    ReactAgent --> ToolEnv
    PythonAgent --> ToolEnv
    ToolEnv --> ToolConfig
```

Sources: [onetwo/agents/agents_base.py](), [onetwo/agents/react.py:678-686](), [onetwo/agents/python_planning.py:486-495]()

## ReAct Agent Strategy

The ReAct (Reasoning and Acting) agent implements the thought-action-observation loop, where the LLM alternates between reasoning about the problem and executing actions through tools.

**ReAct Agent Architecture**

```mermaid
graph TB
    subgraph "ReAct Components"
        ReactAgent["react.ReActAgent<br/>Main agent implementation"]
        ReactPrompt["react.ReActPromptProtocol<br/>Prompt template interface"]
        ReactParse["react.ReActParseProtocol<br/>LLM reply parser"]
    end
    
    subgraph "Prompt Implementations"
        PromptJ2["react.ReActPromptJ2<br/>Jinja2 template"]
        PromptComp["react.ReActPromptComposable<br/>Composable template"]
    end
    
    subgraph "State Structure"
        ReactStep["react.ReActStep<br/>thought, action, observation"]
        FunctionCall["llm_tool_use.FunctionCall<br/>function_name, args, kwargs"]
    end
    
    subgraph "Execution Flow"
        StartEnv["start_environment()"]
        SampleStep["_sample_single_next_step()"]
        ParseReply["parse(llm_reply)"]
        RunTool["environment.run_tool()"]
    end
    
    ReactAgent --> ReactPrompt
    ReactAgent --> ReactParse
    ReactPrompt --> PromptJ2
    ReactPrompt --> PromptComp
    
    ReactStep --> FunctionCall
    
    ReactAgent --> StartEnv
    StartEnv --> SampleStep
    SampleStep --> ParseReply
    ParseReply --> RunTool
```

Sources: [onetwo/agents/react.py:677-719](), [onetwo/agents/react.py:306-343](), [onetwo/agents/react.py:770-846]()

### ReAct Execution Flow

The ReAct agent follows a structured execution pattern:

| Phase | Component | Description |
|-------|-----------|-------------|
| **Prompt Generation** | `ReActPromptProtocol.__call__` | Creates prompt with tools, exemplars, and current state |
| **LLM Interaction** | `llm.generate_text` or `llm.chat` | Gets reasoning and action from LLM |
| **Response Parsing** | `react_parse()` | Extracts thought, action, and determines if finished |
| **Tool Execution** | `environment.run_tool()` | Executes the selected action and captures observation |
| **State Update** | `ReActState.updates.append()` | Adds new step to agent state |

The parsing function `react_parse()` at [onetwo/agents/react.py:580-675]() handles multiple formats including `[Thought]:`, `[Act]:`, and `[Finish]:` patterns.

Sources: [onetwo/agents/react.py:770-846](), [onetwo/agents/react.py:580-675]()

## Python Planning Agent Strategy

The Python Planning agent generates and executes Python code iteratively, building up a solution through sequential code blocks with tool function calls.

**Python Planning Architecture**

```mermaid
graph TB
    subgraph "Python Planning Components"
        PythonAgent["python_planning.PythonPlanningAgent<br/>Iterative code execution"]
        PythonPrompt["python_planning.PythonPlanningPromptProtocol<br/>Code generation prompt"]
        CodeParser["python_planning._parse_llm_reply_code()<br/>Code fence extraction"]
    end
    
    subgraph "Prompt Templates"
        J2Prompt["python_planning.PythonPlanningPromptJ2<br/>Jinja2 implementation"]
        CompPrompt["python_planning.PythonPlanningPromptComposable<br/>Composable implementation"]
    end
    
    subgraph "Execution Environment"
        Sandbox["python_tool_use.PythonToolUseEnvironment<br/>Code execution sandbox"]
        SandboxState["python_execution.SandboxResult<br/>stdout, final_expression_value"]
        ExitHook["result.exit_hook_called<br/>Completion detection"]
    end
    
    subgraph "State Tracking"
        PythonStep["python_planning.PythonPlanningStep<br/>code, result, execution_status"]
        ExecutionStatus["python_execution.ExecutionStatus<br/>SUCCESS, EXECUTION_ERROR, etc."]
    end
    
    PythonAgent --> PythonPrompt
    PythonAgent --> CodeParser
    PythonPrompt --> J2Prompt
    PythonPrompt --> CompPrompt
    
    PythonAgent --> Sandbox
    Sandbox --> SandboxState
    Sandbox --> ExitHook
    
    PythonStep --> ExecutionStatus
```

Sources: [onetwo/agents/python_planning.py:486-525](), [onetwo/agents/python_planning.py:324-366](), [onetwo/agents/python_planning.py:568-647]()

### Code Generation and Execution

The Python Planning agent operates through these key functions:

1. **Code Generation**: `PythonPlanningPromptProtocol.__call__()` generates the next Python code block
2. **Code Parsing**: `_parse_llm_reply_code()` at [onetwo/agents/python_planning.py:153-182]() extracts code from LLM response, handling various fence formats
3. **Code Execution**: `environment.run_code()` executes code in sandbox with tool access
4. **Result Processing**: `_get_result_str()` at [onetwo/agents/python_planning.py:93-132]() formats execution results for LLM

The agent continues until either `exit()` is called in the code or an irrecoverable error occurs.

Sources: [onetwo/agents/python_planning.py:568-647](), [onetwo/agents/python_planning.py:153-182](), [onetwo/agents/python_planning.py:93-132]()

## Chain of Thought Reasoning

OneTwo provides multiple Chain of Thought implementations for structured reasoning without tool use.

**Chain of Thought Strategy Comparison**

```mermaid
graph LR
    subgraph "CoT Implementations"
        J2Simple["chain_of_thought.QACoTPromptJ2<br/>Two-step generation"]
        ChatSimple["chain_of_thought.QACoTPromptChat<br/>Chat-based reasoning"]
        J2Parser["chain_of_thought.QACoTPromptWithAnswerParserJ2<br/>Single call + parsing"]
        ChatParser["chain_of_thought.QACoTPromptWithAnswerParserChat<br/>Chat + parsing"]
    end
    
    subgraph "Output Processing"
        CoTReply["chain_of_thought.CoTReply<br/>reasoning + answer"]
        AnswerParser["chain_of_thought.default_cot_parse_answer<br/>Delimiter-based parsing"]
    end
    
    subgraph "Few-Shot Support"
        Exemplars["chain_of_thought.QACoTExemplar<br/>question + reasoning + answer"]
        MathExemplars["QA_COT_EXEMPLARS_ORIGINAL_MATH_WORD_PROBLEMS<br/>Math word problem examples"]
    end
    
    J2Simple --> CoTReply
    ChatSimple --> CoTReply
    J2Parser --> AnswerParser
    ChatParser --> AnswerParser
    AnswerParser --> CoTReply
    
    Exemplars --> J2Simple
    Exemplars --> ChatSimple
    MathExemplars --> J2Parser
    MathExemplars --> ChatParser
```

Sources: [onetwo/stdlib/reasoning/chain_of_thought.py:105-140](), [onetwo/stdlib/reasoning/chain_of_thought.py:276-311](), [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]()

### CoT Implementation Patterns

| Strategy | Template Calls | Parsing | Use Case |
|----------|---------------|---------|----------|
| `QACoTPromptJ2` | 2 (`reasoning` + `answer`) | Built-in | Clean separation of reasoning/answer |
| `QACoTPromptChat` | 2 (chat messages) | Built-in | Conversational reasoning |
| `QACoTPromptWithAnswerParserJ2` | 1 (`reasoning_and_answer`) | External parser | Single-shot with delimiter parsing |
| `QACoTPromptWithAnswerParserChat` | 1 (chat) | External parser | Chat-based single-shot |

The default answer parser at [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]() handles formats like "The answer is X" with fallback to treating the entire response as the answer.

Sources: [onetwo/stdlib/reasoning/chain_of_thought.py:105-140](), [onetwo/stdlib/reasoning/chain_of_thought.py:410-471](), [onetwo/stdlib/reasoning/chain_of_thought.py:251-273]()

## Composables and Templating

OneTwo supports complex prompt composition through the composables system and multiple templating approaches.

**Template Integration Patterns**

```mermaid
graph TB
    subgraph "Templating Systems"
        Jinja2["templating.JinjaTemplate<br/>Jinja2-based templates"]
        Composables["composing.Composable<br/>Functional composition"]
        PromptTemplate["prompt_templating.JinjaTemplateWithCallbacks<br/>LLM callback integration"]
    end
    
    subgraph "Agent Template Usage"
        ReactJ2["react.ReActPromptJ2<br/>DEFAULT_REACT_PROMPT_TEXT"]
        ReactComp["react.ReActPromptComposable<br/>_build_tools_description()"]
        PythonJ2["python_planning.PythonPlanningPromptJ2<br/>DEFAULT_PYTHON_PLANNING_PROMPT_TEXT"]
        PythonComp["python_planning.PythonPlanningPromptComposable<br/>_render_tools()"]
    end
    
    subgraph "Content System Integration"
        Content["content_lib.ChunkList<br/>Multimodal content"]
        Messages["content_lib.Message<br/>Role-based messages"]
        Roles["content_lib.PredefinedRole<br/>USER, MODEL, SYSTEM"]
    end
    
    Jinja2 --> ReactJ2
    Jinja2 --> PythonJ2
    PromptTemplate --> ReactJ2
    PromptTemplate --> PythonJ2
    
    Composables --> ReactComp
    Composables --> PythonComp
    
    Content --> ReactComp
    Content --> PythonComp
    Messages --> Content
    Roles --> Messages
```

Sources: [onetwo/agents/react.py:102-167](), [onetwo/agents/react.py:387-555](), [onetwo/agents/python_planning.py:201-252](), [onetwo/agents/python_planning.py:368-483]()

### Composable Strategy Construction

The composable system enables functional prompt construction. The pattern involves building up prompts incrementally using the `+=` operator on composable objects, then executing them to get results.

This pattern is used in [onetwo/agents/react.py:525-555]() and [onetwo/agents/python_planning.py:455-483]() to build complex multi-part prompts.

Sources: [onetwo/agents/react.py:525-555](), [onetwo/agents/python_planning.py:455-483]()

## Tool Environment Integration

All advanced agents integrate with the Python Tool Use Environment for executing actions in a controlled sandbox.

**Environment Architecture**

```mermaid
graph TB
    subgraph "Environment Management"
        EnvConfig["python_tool_use.PythonToolUseEnvironmentConfig<br/>tools, sandbox_config"]
        Environment["python_tool_use.PythonToolUseEnvironment<br/>Execution context"]
        ContextManager["start_environment()<br/>Async context manager"]
    end
    
    subgraph "Tool System"
        ToolDef["llm_tool_use.Tool<br/>name, function, description"]
        ToolHandler["run_tool()<br/>Function dispatch"]
        PythonSandbox["python_execution.PythonSandbox<br/>Code execution"]
    end
    
    subgraph "Agent Integration"
        ReactStart["react.ReActAgent.start_environment()"]
        PythonStart["python_planning.PythonPlanningAgent.start_environment()"]
        RunCode["environment.run_code()"]
        RunTool["environment.run_tool()"]
    end
    
    EnvConfig --> Environment
    Environment --> ContextManager
    
    ToolDef --> ToolHandler
    ToolHandler --> PythonSandbox
    
    ReactStart --> ContextManager
    PythonStart --> ContextManager
    Environment --> RunCode
    Environment --> RunTool
```

Sources: [onetwo/agents/react.py:747-768](), [onetwo/agents/python_planning.py:545-566](), [onetwo/stdlib/tool_use/python_tool_use.py]()

### Usage Pattern

Both agent types follow the same environment pattern using async context managers:

```python
async with agent.start_environment() as env:
    state = await agent.initialize_state(inputs)
    while not agent.is_finished(state):
        next_step = await agent._sample_single_next_step(
            state=state, environment=env
        )
        state = state.append_update(next_step)
    return agent.extract_output(state)
```

This pattern is implemented in the base agent classes and provides consistent tool access across different strategies.

Sources: [onetwo/agents/react.py:747-768](), [onetwo/agents/python_planning.py:545-566]()

---

