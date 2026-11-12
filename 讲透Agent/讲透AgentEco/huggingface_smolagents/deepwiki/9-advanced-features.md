<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smolagents · page 9 Advanced Features · fetched 2026-10-27 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/en/conceptual_guides/intro_agents.md](docs/source/en/conceptual_guides/intro_agents.md)
- [docs/source/en/examples/rag.md](docs/source/en/examples/rag.md)
- [docs/source/en/examples/text_to_sql.md](docs/source/en/examples/text_to_sql.md)
- [docs/source/en/tutorials/building_good_agents.md](docs/source/en/tutorials/building_good_agents.md)
- [docs/source/en/tutorials/tools.md](docs/source/en/tutorials/tools.md)
- [src/smolagents/agents.py](src/smolagents/agents.py)
- [tests/test_agents.py](tests/test_agents.py)

</details>



This page documents advanced capabilities of `smolagents` that extend beyond basic agent creation and execution. These features enable complex workflows including multi-agent coordination, strategic planning, robust error recovery, agent sharing, and human-in-the-loop patterns.

For basic agent setup and usage, see [Getting Started](#2). For core agent concepts, see [Key Concepts](#2.3). For detailed agent implementation, see [Agent Framework](#3).

## Overview

Advanced features in `smolagents` are implemented primarily in the `MultiStepAgent` base class [src/smolagents/agents.py:268-292]() and its subclasses `CodeAgent` [src/smolagents/agents.py:900-928]() and `ToolCallingAgent` [src/smolagents/agents.py:1181-1205](). These features are configured through initialization parameters and accessed through specific agent methods:

| Feature | Configuration Parameter | Primary Methods | Covered in Section |
|---------|------------------------|-----------------|-------------------|
| Multi-Agent Systems | `managed_agents` | `__call__()` | [Multi-Agent Systems](#9.1) |
| Planning Strategy | `planning_interval` | `_generate_planning_step()` | [Planning Intervals & Strategy](#9.2) |
| Error Handling | `final_answer_checks` | `_validate_final_answer()` | [Error Handling & Recovery](#9.3) |
| Persistence | N/A | `save()`, `from_folder()`, `push_to_hub()`, `from_hub()` | [Agent Persistence & Hub Integration](#9.4) |
| Human-in-the-Loop | `step_callbacks` | `_finalize_step()` | [Human-in-the-Loop Workflows](#9.5) |

**Sources:** [src/smolagents/agents.py:268-353]()

## Architecture Overview

**`MultiStepAgent` advanced configuration and method relationships**

```mermaid
graph TB
    subgraph "Init_Parameters_[MultiStepAgent.__init__]"
        MA["managed_agents<br/>(list[MultiStepAgent])"]
        PI["planning_interval<br/>(int | None)"]
        SC["step_callbacks<br/>(list | dict[Type[MemoryStep], Callable])"]
        FAC["final_answer_checks<br/>(list[Callable])"]
        RFR["return_full_result<br/>(bool)"]
    end

    subgraph "MultiStepAgent_Core_Methods"
        Init["__init__()"]
        Run["run()"]
        RunStream["_run_stream()"]
        StepStream["_step_stream()"]
        Finalize["_finalize_step()"]
        Interrupt["interrupt()"]
    end

    subgraph "Advanced_Dispatch_Methods"
        Call["__call__(task)<br/>Managed agent entry point"]
        Plan["_generate_planning_step()<br/>Strategic plan generation"]
        Validate["_validate_final_answer()<br/>Run final_answer_checks"]
        MaxSteps["_handle_max_steps_reached()<br/>Fallback answer on timeout"]
    end

    subgraph "Persistence_Methods"
        Save["save() / from_folder()"]
        PushHub["push_to_hub() / from_hub()"]
    end

    MA --> Init
    PI --> Init
    SC --> Init
    FAC --> Init
    RFR --> Init

    Init --> Run
    Run --> RunStream
    RunStream --> StepStream
    StepStream --> Finalize
    Interrupt -.->|"sets interrupt_switch=True"| RunStream

    RunStream -->|"if planning_interval"| Plan
    RunStream -->|"on final answer"| Validate
    RunStream -->|"if max_steps exceeded"| MaxSteps
    Finalize -->|"step_callbacks.callback(step)"| SC

    MA --> Call
    Init --> Save
    Init --> PushHub
```

**Sources:** [src/smolagents/agents.py:268-353](), [src/smolagents/agents.py:436-638](), [src/smolagents/agents.py:754-756]()

## Feature Interaction Patterns

**How advanced features interact inside `_run_stream()`**

```mermaid
sequenceDiagram
    participant User
    participant Agent as "MultiStepAgent._run_stream()"
    participant PlanStep as "_generate_planning_step()"
    participant StepStream as "_step_stream()"
    participant Registry as "CallbackRegistry.callback()"
    participant Checks as "final_answer_checks"
    participant Sub as "ManagedAgent.__call__()"

    User->>Agent: "run(task, stream=False)"
    Agent->>Agent: "reset memory, set interrupt_switch=False"

    loop "each step (step_number <= max_steps)"
        alt "planning_interval set and step matches"
            Agent->>PlanStep: "_generate_planning_step(task, is_first_step)"
            PlanStep-->>Agent: "yields PlanningStep"
            Agent->>Registry: "callback(planning_step, agent=self)"
        end

        Agent->>StepStream: "_step_stream(action_step)"

        alt "CodeAgent or ToolCallingAgent calls managed agent"
            StepStream->>Sub: "__call__(subtask, additional_args)"
            Sub-->>StepStream: "wrapped report string"
        end

        StepStream-->>Agent: "yields ActionOutput(is_final_answer=True/False)"

        alt "is_final_answer=True"
            Agent->>Checks: "check(final_answer, memory, agent)"
            alt "check fails"
                Checks-->>Agent: "raise AgentError"
                Note over Agent: "recorded in action_step.error, loop continues"
            else "all checks pass"
                Agent-->>User: "return final answer"
            end
        end

        Agent->>Registry: "callback(action_step, agent=self)"
    end

    alt "max_steps exceeded"
        Agent->>Agent: "_handle_max_steps_reached(task)"
        Agent-->>User: "return fallback answer"
    end
```

**Sources:** [src/smolagents/agents.py:540-611](), [src/smolagents/agents.py:613-637](), [src/smolagents/agents.py:868-886]()

## Return Value Options

Agents support two return modes controlled by `return_full_result` [src/smolagents/agents.py:313]():

```mermaid
graph LR
    Run["agent.run(task)"]
    
    subgraph "return_full_result=False_(default)"
        SimpleOutput["Returns final answer only<br/>Any type"]
    end
    
    subgraph "return_full_result=True"
        RunResult["RunResult object"]
        Output["output: final answer"]
        State["state: 'success' or 'max_steps_error'"]
        Steps["steps: list of memory steps"]
        Tokens["token_usage: TokenUsage or None"]
        Timing["timing: Timing object"]
        
        RunResult --> Output
        RunResult --> State
        RunResult --> Steps
        RunResult --> Tokens
        RunResult --> Timing
    end
    
    Run -->|default| SimpleOutput
    Run -->|for debugging| RunResult
```

The `RunResult` class [src/smolagents/agents.py:196-209]() provides comprehensive execution metadata:

- **`output`**: The final answer from the agent (same as default return) [src/smolagents/agents.py:211]().
- **`state`**: Either `"success"` or `"max_steps_error"` indicating completion status [src/smolagents/agents.py:212]().
- **`steps`**: Full memory history as dictionaries (via `memory.get_full_steps()`) [src/smolagents/agents.py:213]().
- **`token_usage`**: Total tokens consumed if model provides usage data [src/smolagents/agents.py:214]().
- **`timing`**: Execution start time, end time, and duration [src/smolagents/agents.py:215]().

**Sources:** [src/smolagents/agents.py:195-254](), [src/smolagents/agents.py:505-536]()

## Configuration Best Practices

| Use Case | Recommended Configuration |
|----------|--------------------------|
| Simple single-task | No advanced features needed |
| Complex multi-step task | `planning_interval=3`, `max_steps=30` |
| Delegation to specialists | `managed_agents=[specialist1, specialist2]` |
| Quality assurance | `final_answer_checks=[validator_func]` |
| Per-step type callbacks | `step_callbacks={ActionStep: [cb1], PlanningStep: [cb2]}` |
| Post-run inspection | `return_full_result=True` to get `RunResult` |
| Sharing with community | Use `push_to_hub()` after development |
| Graceful stop | Call `agent.interrupt()` to set `interrupt_switch=True` |
| Multi-turn dialogue | Call `agent.run(next_task, reset=False)` |

**Sources:** [src/smolagents/agents.py:294-336](), [src/smolagents/agents.py:754-756](), [tests/test_agents.py:484-496](), [tests/test_agents.py:664-738]()

## Agent State Management

**Runtime attributes and their lifecycle within `MultiStepAgent`**

```mermaid
graph TB
    subgraph "Instance_Attributes_[MultiStepAgent]"
        Memory["self.memory<br/>(AgentMemory)<br/>Conversation history, all MemoryStep objects"]
        State["self.state<br/>(dict)<br/>Runtime variables shared with executor"]
        StepNum["self.step_number<br/>(int)<br/>Monotonic counter per _run_stream()"]
        Task["self.task<br/>(str | None)<br/>Set by run(), used in system prompt"]
        ISwitch["self.interrupt_switch<br/>(bool)<br/>Set True by interrupt()"]
        Monitor["self.monitor<br/>(Monitor)<br/>Token / timing metrics"]
    end

    subgraph "Reset_Behavior_[run(reset=...)]"
        ResetTrue["reset=True<br/>memory.reset()<br/>monitor.reset()"]
        ResetFalse["reset=False<br/>Memory preserved<br/>Continuation run"]
    end

    subgraph "Interrupt_Mechanism"
        IntMethod["interrupt()<br/>Sets interrupt_switch=True"]
        Check["_run_stream() checks interrupt_switch<br/>Raises AgentError('Agent interrupted.')"]
    end

    Memory -.->|"cleared by"| ResetTrue
    Memory -.->|"preserved by"| ResetFalse
    State -.->|"sent via send_variables()"| PythonExecutor["LocalPythonExecutor / RemotePythonExecutor"]
    ISwitch -.->|"read by"| Check
    IntMethod -.->|"writes"| ISwitch
```

Key behaviors:

- **`self.state`**: For `CodeAgent`, variables placed here are accessible inside code execution steps by name [src/smolagents/agents.py:331-353]().
- **`self.interrupt_switch`**: Set to `False` at the start of every `run()` call [src/smolagents/agents.py:540-548](). Can be set to `True` from another thread via `interrupt()` to stop execution gracefully at the next iteration boundary [src/smolagents/agents.py:754-756]().
- **`reset=False`**: Allows multi-turn conversations where memory from prior `run()` calls is visible in subsequent calls, enabling stateful dialogue [src/smolagents/agents.py:436-492]().

**Sources:** [src/smolagents/agents.py:331-353](), [src/smolagents/agents.py:436-492](), [src/smolagents/agents.py:540-548](), [src/smolagents/agents.py:754-756](), [tests/test_agents.py:484-496]()

## Advanced Initialization Parameters

Beyond basic `tools` and `model`, `MultiStepAgent` accepts parameters for advanced workflows:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `managed_agents` | `list[MultiStepAgent]` | `None` | Sub-agents callable as tools; each must have `name` and `description` [src/smolagents/agents.py:294](). |
| `planning_interval` | `int \| None` | `None` | Run a planning step every N action steps [src/smolagents/agents.py:302](). |
| `step_callbacks` | `list[Callable] \| dict` | `None` | Hooks invoked by `_finalize_step()` after each step [src/smolagents/agents.py:304](). |
| `final_answer_checks` | `list[Callable]` | `None` | Validators receiving `(final_answer, memory, agent)` [src/smolagents/agents.py:307](). |
| `return_full_result` | `bool` | `False` | Return `RunResult` instead of raw output from `run()` [src/smolagents/agents.py:313](). |
| `provide_run_summary` | `bool` | `False` | Append memory summary to managed agent output [src/smolagents/agents.py:318](). |

**`step_callbacks` registration detail:** When passed as a `list`, all callbacks are registered only for `ActionStep`. When passed as a `dict`, keys are `MemoryStep` subclasses (`ActionStep`, `PlanningStep`, etc.) [src/smolagents/agents.py:416-434](). Internally these are stored in a `CallbackRegistry` instance at `self.step_callbacks` [src/smolagents/agents.py:348]().

**Sources:** [src/smolagents/agents.py:294-353](), [src/smolagents/agents.py:416-434]()

---

This overview introduces the major advanced features. Each subsection provides detailed implementation guidance for its respective feature.

- [Multi-Agent Systems](#9.1) — Explains the `ManagedAgent` wrapper, hierarchical task delegation, and orchestration.
- [Planning Intervals & Strategy](#9.2) — Documents the `planning_interval` parameter and `PlanningStep` logic.
- [Error Handling & Recovery](#9.3) — Details the `AgentError` hierarchy and `final_answer_checks`.
- [Agent Persistence & Hub Integration](#9.4) — Covers `push_to_hub`, `save`, and serialization workflows.
- [Human-in-the-Loop Workflows](#9.5) — Explains `UserInputTool` and step-based interruption patterns.

---

