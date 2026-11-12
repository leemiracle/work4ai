<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/onetwo · extra page ReAct Agent · fetched 2026-10-26 -->

# ReAct Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [onetwo/agents/react.py](onetwo/agents/react.py)
- [onetwo/agents/react_test.py](onetwo/agents/react_test.py)

</details>



This document covers the ReAct (Reasoning and Acting) agent implementation in OneTwo, which enables multi-step reasoning and tool use through a thought-action-observation cycle. The ReAct agent allows LLMs to interleave reasoning steps with tool execution to solve complex problems that require external information or computation.

For information about the Python Tool Environment that ReAct agents use for tool execution, see [Python Tool Environment](#4.2). For broader agent evaluation techniques, see [Agent Evaluation](#5.2).

## Overview

The ReAct agent implements the strategy described in the [ReAct paper](https://arxiv.org/abs/2210.03629), generalized to work within OneTwo's agent framework. The strategy follows a structured cycle where the LLM alternates between:

1. **Thought**: Reasoning about the current situation and next steps
2. **Action**: Executing a specific tool or function call  
3. **Observation**: Receiving and processing the results

This cycle continues until the agent reaches a final answer or exceeds the maximum number of steps.

**ReAct Execution Flow**

```mermaid
flowchart TD
    A["ReActAgent.initialize_state()"] --> B["ReActState with inputs"]
    B --> C["ReActAgent._sample_single_next_step()"]
    C --> D["prompt() - Generate LLM response"]
    D --> E["parse() - Extract thought/action"]
    E --> F{Has Action?}
    
    F -->|Yes| G["environment.run_tool()"]
    F -->|No| H["Create ReActStep with thought only"]
    
    G --> I["Create ReActStep with observation"]
    H --> J{is_finished?}
    I --> J
    
    J -->|No| K{Max steps reached?}
    K -->|No| C
    K -->|Yes| L["Force finish - prompt for final answer"]
    
    J -->|Yes| M["extract_output() - Return final answer"]
    L --> M
    
    style A fill:#e1f5fe
    style M fill:#e8f5e8
    style G fill:#fff3e0
```

Sources: [onetwo/agents/react.py:15-32](), [onetwo/agents/react.py:770-846]()

## Core Components

### ReActStep

The `ReActStep` class represents a single step in the ReAct execution cycle, containing the thought, action, and observation for that step.

```mermaid
classDiagram
    class ReActStep {
        +bool is_finished
        +str|ChunkList thought
        +FunctionCall|None action
        +Any observation
        +ArgumentFormat|None fmt
        +render_action() str|ChunkList
        +render_observation() str|ChunkList
    }
    
    class FunctionCall {
        +str function_name
        +tuple args
        +dict kwargs
    }
    
    class ArgumentFormat {
        <<enumeration>>
        PYTHON
        MARKDOWN
    }
    
    ReActStep --> FunctionCall : contains
    ReActStep --> ArgumentFormat : uses
```

Key attributes:
- `is_finished`: Indicates if this is the final step
- `thought`: The reasoning output from the LLM
- `action`: The tool call to execute (if any)
- `observation`: The result of executing the action
- `fmt`: The format used for rendering the action

Sources: [onetwo/agents/react.py:54-96]()

### ReActState

`ReActState` represents the complete state of a ReAct agent execution, containing the original inputs and all steps performed so far.

```mermaid
classDiagram
    class ReActState {
        +str|ChunkList inputs
        +List~ReActStep~ updates
    }
    
    class UpdateListState~I,U~ {
        +I inputs
        +List~U~ updates
    }
    
    ReActState --|> UpdateListState : extends
    ReActState *-- ReActStep : contains many
```

The state follows an append-only pattern where new steps are added to the `updates` list as the agent progresses.

Sources: [onetwo/agents/react.py:98-100]()

### ReActAgent

The main `ReActAgent` class orchestrates the entire ReAct execution process.

```mermaid
classDiagram
    class ReActAgent {
        +ReActPromptProtocol prompt
        +ReActParseProtocol parse
        +List~ReActState~ exemplars
        +PythonToolUseEnvironmentConfig environment_config
        +int max_steps
        +str stop_prefix
        
        +initialize_state() ReActState
        +start_environment() PythonToolUseEnvironment
        +_sample_single_next_step() ReActStep
        +is_finished() bool
        +extract_output() str
    }
    
    class SingleSampleAgent~I,O,S,U,E~ {
        <<abstract>>
    }
    
    ReActAgent --|> SingleSampleAgent : extends
    ReActAgent --> ReActPromptProtocol : uses
    ReActAgent --> ReActParseProtocol : uses
    ReActAgent --> PythonToolUseEnvironment : manages
```

Key configuration:
- `prompt`: Template for generating LLM prompts
- `parse`: Function for parsing LLM responses  
- `exemplars`: Few-shot examples to include in prompts
- `max_steps`: Maximum number of ReAct iterations (default: 10)

Sources: [onetwo/agents/react.py:677-716]()

## Prompt System

The ReAct agent uses a sophisticated prompt system with two main implementations.

### Prompt Templates

**ReAct Prompt Components**

```mermaid
flowchart TD
    A["ReActPromptProtocol"] --> B["ReActPromptJ2<br/>(Jinja2 Template)"]
    A --> C["ReActPromptComposable<br/>(Composable Functions)"]
    
    B --> D["DEFAULT_REACT_PROMPT_TEXT"]
    C --> E["_build_tools_description()"]
    C --> F["_build_react_fewshots()"]
    C --> G["_build_question()"]
    C --> H["_build_current_state()"]
    
    D --> I["Tool Descriptions"]
    D --> J["Few-shot Examples"]
    D --> K["Current Question"]
    D --> L["Current State"]
    
    E --> I
    F --> J
    G --> K
    H --> L
    
    style B fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#f3e5f5
```

Both implementations generate prompts containing:
1. **Tool descriptions**: Available tools and their usage
2. **Few-shot exemplars**: Example ReAct conversations
3. **Current question**: The user's input
4. **Current state**: Steps completed so far

Sources: [onetwo/agents/react.py:306-343](), [onetwo/agents/react.py:387-554](), [onetwo/agents/react.py:102-167]()

### Response Parsing

The `react_parse` function extracts structured information from LLM responses:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `\[Thought\]:?` | Extract reasoning | `[Thought]: I need to search for information` |
| `\[Act\]:?` | Extract action | `[Act]: search("query")` |
| `\[Finish\]:?` | Extract final answer | `[Finish]: The answer is 42` |

The parser handles various formats and gracefully degrades when parsing fails.

Sources: [onetwo/agents/react.py:580-675]()

## Tool Integration

The ReAct agent integrates with OneTwo's tool system through the `PythonToolUseEnvironment`.

**Tool Execution Flow**

```mermaid
sequenceDiagram
    participant Agent as ReActAgent
    participant Env as PythonToolUseEnvironment
    participant Tool as Tool Function
    
    Agent->>Agent: parse() extracts FunctionCall
    Agent->>Env: run_tool(tool_name, args, kwargs)
    Env->>Tool: Execute with arguments
    Tool-->>Env: Return result
    Env-->>Agent: Observation
    Agent->>Agent: Create ReActStep with observation
```

The environment provides access to tools like:
- **Python execution**: For calculations and data processing
- **Search functions**: For retrieving external information  
- **Finish tool**: For returning final answers

Sources: [onetwo/agents/react.py:834-846]()

## Default Exemplars

The agent comes with built-in few-shot examples demonstrating common patterns:

| Exemplar | Demonstrates | Tools Used |
|----------|-------------|------------|
| Height comparison | Multi-step calculation | Search, Python, Finish |
| String reversal | Text processing | Search, Python, Finish |

These exemplars are stored in `REACT_FEWSHOTS` and show complete ReAct conversations from question to final answer.

**Exemplar Structure**

```mermaid
graph TD
    A["default_react_exemplars()"] --> B["exemplar_subtract<br/>Height comparison"]
    A --> C["exemplar_reverse<br/>String reversal"]
    
    B --> D["ReActStep 1:<br/>Search Everest height"]
    B --> E["ReActStep 2:<br/>Search K2 height"]
    B --> F["ReActStep 3:<br/>Calculate difference"]
    B --> G["ReActStep 4:<br/>Finish with answer"]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#fff3e0
```

Sources: [onetwo/agents/react.py:170-303]()

## Usage Example

```python
import onetwo as ot
from onetwo.agents import react
from onetwo.stdlib.tool_use import python_tool_use

# Configure the agent
agent = react.ReActAgent(
    exemplars=react.REACT_FEWSHOTS,
    max_steps=10,
    environment_config=python_tool_use.PythonToolUseEnvironmentConfig()
)

# Execute the agent
question = "What is the square root of 144?"
result = ot.run(agent(inputs=question))
print(result)  # "12"
```

The agent will automatically:
1. Generate a thought about using Python for calculation
2. Execute `Python("144 ** 0.5")` 
3. Observe the result `12.0`
4. Finish with the final answer

Sources: [onetwo/agents/react_test.py:385-456]()

## Configuration Options

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `prompt` | `ReActPromptProtocol` | `ReActPromptJ2()` | Template for LLM prompts |
| `parse` | `ReActParseProtocol` | `react_parse` | Response parsing function |
| `exemplars` | `list[ReActState]` | `[]` | Few-shot examples |
| `environment_config` | `PythonToolUseEnvironmentConfig` | Default config | Available tools |
| `max_steps` | `int` | `10` | Maximum ReAct iterations |
| `stop_prefix` | `str` | `''` | Prefix for stop sequences |

The agent automatically handles:
- **Force finishing**: When max steps are reached or empty responses occur
- **Error handling**: Tool execution failures are captured as observations
- **State serialization**: Complete execution history is preserved

Sources: [onetwo/agents/react.py:705-718](), [onetwo/agents/react.py:794-809]()

---

