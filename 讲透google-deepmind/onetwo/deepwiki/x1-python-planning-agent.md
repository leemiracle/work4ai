<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/onetwo · extra page Python Planning Agent · fetched 2026-10-26 -->

# Python Planning Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [onetwo/agents/python_planning.py](onetwo/agents/python_planning.py)
- [onetwo/agents/python_planning_test.py](onetwo/agents/python_planning_test.py)

</details>



This document covers the Python Planning Agent implementation, a sophisticated strategy that iteratively generates and executes Python code blocks to solve complex problems using available tools. The agent employs a step-by-step approach where each iteration involves prompting an LLM to generate Python code, executing that code in a sandboxed environment, and using the results to inform the next step.

For information about the underlying Python execution environment, see [Python Tool Environment](#4.2). For details about the ReAct agent alternative, see [ReAct Agent](#4.1.1).

## Purpose and Architecture

The Python Planning Agent implements a code-generation strategy where an LLM iteratively writes Python programs that can call predefined tools to gather information and perform computations. This approach is inspired by research like ViperGPT and AdaPlanner, enabling complex multi-step reasoning through code execution.

### Core Architecture

```mermaid
graph TB
    User[User Input] --> PythonPlanningAgent["PythonPlanningAgent"]
    PythonPlanningAgent --> PythonPlanningState["PythonPlanningState"]
    PythonPlanningState --> PromptTemplate["Prompt Template"]
    
    subgraph "Prompt Templates"
        PythonPlanningPromptJ2["PythonPlanningPromptJ2"]
        PythonPlanningPromptComposable["PythonPlanningPromptComposable"]
    end
    
    PromptTemplate --> LLM["LLM (generate_text/chat)"]
    LLM --> ParseCode["_parse_llm_reply_code()"]
    ParseCode --> PythonToolUseEnvironment["PythonToolUseEnvironment"]
    
    subgraph "Execution Environment"
        PythonSandbox["Python Sandbox"]
        Tools["Tool Registry"]
    end
    
    PythonToolUseEnvironment --> PythonSandbox
    PythonToolUseEnvironment --> Tools
    PythonSandbox --> PythonPlanningStep["PythonPlanningStep"]
    PythonPlanningStep --> PythonPlanningState
    
    PythonPlanningState --> IsFinished{"is_finished or max_steps?"}
    IsFinished -->|No| PromptTemplate
    IsFinished -->|Yes| Output["extract_output()"]
```

Sources: [onetwo/agents/python_planning.py:487-675]()

## State Representation

The agent maintains its state through a sequence of executed steps, each containing the generated code and execution results.

### State Structure

```mermaid
classDiagram
    class PythonPlanningState {
        +str inputs
        +list~PythonPlanningStep~ updates
        +initialize_state()
    }
    
    class PythonPlanningStep {
        +bool is_finished
        +str code
        +str result
        +ExecutionStatus execution_status
    }
    
    class ExecutionStatus {
        <<enumeration>>
        SUCCESS
        EXECUTION_ERROR
        PROGRAM_ERROR
        SANDBOX_ERROR
        SANDBOX_TIMEOUT
    }
    
    PythonPlanningState --> PythonPlanningStep : "contains sequence of"
    PythonPlanningStep --> ExecutionStatus : "has status"
```

The `PythonPlanningState` is defined as an alias: `UpdateListState[str, PythonPlanningStep]`, representing the input question and a chronological sequence of execution steps.

Sources: [onetwo/agents/python_planning.py:68-91]()

## Prompt Templates

The agent supports two prompt template implementations that format the state and tools for LLM consumption.

### Template Hierarchy

```mermaid
graph TB
    PythonPlanningPromptProtocol["PythonPlanningPromptProtocol"]
    
    PythonPlanningPromptJ2["PythonPlanningPromptJ2"]
    PythonPlanningPromptComposable["PythonPlanningPromptComposable"]
    
    PythonPlanningPromptProtocol --> PythonPlanningPromptJ2
    PythonPlanningPromptProtocol --> PythonPlanningPromptComposable
    
    JinjaTemplateWithCallbacks["JinjaTemplateWithCallbacks"] --> PythonPlanningPromptJ2
    
    subgraph "Template Features"
        DEFAULT_PYTHON_PLANNING_PROMPT_TEXT["DEFAULT_PYTHON_PLANNING_PROMPT_TEXT"]
        DEFAULT_PYTHON_PLANNING_INSTRUCTION["DEFAULT_PYTHON_PLANNING_INSTRUCTION"]
        DEFAULT_PYTHON_PLANNING_EXEMPLARS["DEFAULT_PYTHON_PLANNING_EXEMPLARS"]
    end
    
    PythonPlanningPromptJ2 --> DEFAULT_PYTHON_PLANNING_PROMPT_TEXT
    PythonPlanningPromptJ2 --> DEFAULT_PYTHON_PLANNING_INSTRUCTION
    PythonPlanningPromptComposable --> DEFAULT_PYTHON_PLANNING_INSTRUCTION
```

### Prompt Components

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Instruction | Task description and rules | `DEFAULT_PYTHON_PLANNING_INSTRUCTION` |
| Tool Descriptions | Available functions and examples | Rendered from `Tool` objects |
| Exemplars | Few-shot examples | `DEFAULT_PYTHON_PLANNING_EXEMPLARS` |
| Current State | Question and previous steps | Rendered from `PythonPlanningState` |
| Code Fence | Prompt for next code block | Triple backticks with stop sequence |

Sources: [onetwo/agents/python_planning.py:185-483]()

## Execution Flow

The agent follows a structured execution loop that continues until completion or maximum steps are reached.

### Step Execution Process

```mermaid
sequenceDiagram
    participant Agent as "PythonPlanningAgent"
    participant Prompt as "Prompt Template"
    participant LLM as "Language Model"
    participant Parser as "_parse_llm_reply_code"
    participant Env as "PythonToolUseEnvironment"
    participant Sandbox as "Python Sandbox"
    
    Agent->>+Prompt: render(exemplars, state, tools)
    Prompt->>+LLM: generate_text(stop=['```'])
    LLM-->>-Prompt: raw_code_response
    Prompt-->>-Agent: llm_reply
    
    Agent->>+Parser: _parse_llm_reply_code(llm_reply)
    Parser-->>-Agent: cleaned_code
    
    Agent->>+Env: run_code(sandbox_state, cleaned_code)
    Env->>+Sandbox: execute(code)
    Sandbox-->>-Env: SandboxResult
    Env-->>-Agent: CodeExecutionResult
    
    Agent->>Agent: create PythonPlanningStep
    Agent->>Agent: check is_finished or irrecoverable_error
```

### Code Parsing Logic

The `_parse_llm_reply_code` function handles various code fence formats that different models may produce:

| Input Format | Parsed Output | Notes |
|--------------|---------------|-------|
| `print("hello")` | `print("hello")` | Plain code |
| `\`\`\`python\nprint("hello")\`\`\`` | `print("hello")` | Python fence |
| `\`\`\`tool_code\nprint("hello")\`\`\`` | `print("hello")` | Tool code fence |
| `python\nprint("hello")` | `print("hello")` | First line identifier |

Sources: [onetwo/agents/python_planning.py:153-183](), [onetwo/agents/python_planning.py:568-648]()

## Tool Integration

The agent integrates with the Python Tool Use Environment to provide access to external tools through Python function calls.

### Tool Configuration

```mermaid
graph LR
    PythonPlanningAgent --> PythonToolUseEnvironmentConfig["environment_config"]
    PythonToolUseEnvironmentConfig --> Tools["tools: list[Tool]"]
    
    subgraph "Tool Definition"
        Tool["Tool"]
        Tool --> name["name: str"]
        Tool --> function["function: Callable"]
        Tool --> description["description: str"]
        Tool --> example["example: str"]
        Tool --> irrecoverable_error_types["irrecoverable_error_types"]
    end
    
    Tools --> Tool
    
    subgraph "Error Handling"
        ExecutionError["Execution Error"]
        ExecutionError --> Recoverable["Recoverable → Retry"]
        ExecutionError --> Irrecoverable["Irrecoverable → Finish"]
    end
```

### Error Recovery Mechanism

The agent implements sophisticated error handling:

1. **Recoverable Errors**: Standard Python exceptions prompt the LLM to fix the code
2. **Irrecoverable Errors**: Specific exception types defined in `Tool.irrecoverable_error_types` cause immediate termination
3. **System Errors**: Sandbox timeouts and system failures automatically finish execution

Sources: [onetwo/agents/python_planning.py:605-647]()

## Default Exemplars

The system includes pre-built examples demonstrating the agent's capabilities:

### Exemplar Structure

```mermaid
graph TB
    Exemplar["DEFAULT_PYTHON_PLANNING_EXEMPLARS[0]"]
    Exemplar --> Question["'How much taller is Everest than Mount Fuji?'"]
    
    Question --> Step1["Step 1: Search for heights"]
    Step1 --> Code1["search('how tall is Everest?')\nsearch('how tall is Mount Fuji?')"]
    Code1 --> Result1["'Everest: 8,849m, Mount Fuji: 3,776m'"]
    
    Result1 --> Step2["Step 2: Extract numbers"]
    Step2 --> Code2["firstnumber(height1)\nfirstnumber(height2)"]
    Code2 --> Result2["'5073'"]
    
    Result2 --> Step3["Step 3: Final answer"]
    Step3 --> Code3["print('Everest is 5,073 meters taller than Mount Fuji.')\nexit()"]
    Code3 --> Finished["is_finished: True"]
```

Sources: [onetwo/agents/python_planning.py:256-292]()

## Configuration and Usage

### Basic Agent Setup

```python
# Basic configuration
agent = PythonPlanningAgent(
    prompt=PythonPlanningPromptJ2(),
    exemplars=DEFAULT_PYTHON_PLANNING_EXEMPLARS,
    environment_config=PythonToolUseEnvironmentConfig(tools=[...]),
    max_steps=10
)

# Execute agent
result = await agent(inputs="What is the population of Tokyo?")
```

### Agent Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `prompt` | `PythonPlanningPromptProtocol` | `PythonPlanningPromptJ2()` | Template for LLM prompts |
| `exemplars` | `list[PythonPlanningState]` | `[]` | Few-shot examples |
| `environment_config` | `PythonToolUseEnvironmentConfig` | `PythonToolUseEnvironmentConfig()` | Tool and sandbox settings |
| `max_steps` | `int` | `10` | Maximum execution steps |

### Termination Conditions

The agent stops execution when:

1. **Explicit Exit**: Code calls `exit()` function ([onetwo/agents/python_planning.py:646]())
2. **Max Steps**: Reaches `max_steps` limit ([onetwo/agents/python_planning.py:657-659]())
3. **Irrecoverable Error**: Tool raises configured exception type ([onetwo/agents/python_planning.py:632-640]())
4. **System Error**: Sandbox timeout or critical failure ([onetwo/agents/python_planning.py:635-640]())

Sources: [onetwo/agents/python_planning.py:487-675](), [onetwo/agents/python_planning_test.py:315-553]()

---

