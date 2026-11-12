<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-agents-python · page 6 Safety and Validation · fetched 2026-10-26 -->

# Safety and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/agent_patterns/README.md](examples/agent_patterns/README.md)
- [examples/agent_patterns/human_in_the_loop.py](examples/agent_patterns/human_in_the_loop.py)
- [examples/agent_patterns/human_in_the_loop_server.py](examples/agent_patterns/human_in_the_loop_server.py)
- [src/agents/guardrail.py](src/agents/guardrail.py)
- [src/agents/run_internal/guardrails.py](src/agents/run_internal/guardrails.py)
- [src/agents/util/_pretty_print.py](src/agents/util/_pretty_print.py)
- [tests/test_guardrails.py](tests/test_guardrails.py)
- [tests/test_human_in_the_loop_server_example.py](tests/test_human_in_the_loop_server_example.py)
- [tests/test_pretty_print.py](tests/test_pretty_print.py)
- [tests/test_tool_guardrails.py](tests/test_tool_guardrails.py)
- [tests/utils/test_pretty_print_and_items.py](tests/utils/test_pretty_print_and_items.py)

</details>



## Purpose and Scope

This page provides a high-level overview of the safety and validation system in the OpenAI Agents SDK. The safety infrastructure enforces runtime compliance, security, and quality policies on agent inputs, final outputs, and function tool interactions. 

As a PARENT page, this document outlines the core concepts and links to detailed child pages for implementation specifics.

Sources: `src/agents/guardrail.py:73-84` [src/agents/guardrail.py:73-84](), `src/agents/run_internal/guardrails.py:31-52` [src/agents/run_internal/guardrails.py:31-52]()

---

## Guardrail Architecture

The guardrail system integrates directly into the execution lifecycle of `Runner` [src/agents/run_internal/guardrails.py:31-52](). Guardrails inspect data at distinct boundaries within agent turns.

| Guardrail Type | Execution Point | Primary Purpose |
|----------------|-----------------|-----------------|
| **Input Guardrails** | Before or concurrently with the agent processing user input [src/agents/guardrail.py:73-77]() | Validate incoming user requests and intercept off-topic or policy-violating queries. |
| **Output Guardrails** | After the agent produces its final response [src/agents/guardrail.py:134-137]() | Ensure final outputs meet quality, safety, or formatting criteria before delivery. |
| **Tool Guardrails** | Before and after function tool execution [tests/test_tool_guardrails.py:88-189]() | Validate tool arguments or inspect tool return payloads. |

For a deep dive into execution points, see [Guardrail Architecture](#6.1).

### Diagram: Guardrail Lifecycle Integration

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        UserQuery[""User Input Request"""]
        AgentOutput[""Final Agent Output"""]
    end

    subgraph "CodeEntitySpace"
        Runner[""Runner.run()""]
        InputCheck[""run_input_guardrails()""]
        AgentCore[""Agent Turn Loop"""]
        OutputCheck[""run_output_guardrails()""]
    end

    UserQuery --> Runner
    Runner --> InputCheck
    InputCheck --> AgentCore
    AgentCore --> OutputCheck
    OutputCheck --> AgentOutput
```

Sources: `src/agents/guardrail.py:73-137` [src/agents/guardrail.py:73-137](), `src/agents/run_internal/guardrails.py:31-175` [src/agents/run_internal/guardrails.py:31-175]()

---

## Input and Output Guardrails

Input and output guardrails are configured via decorators (`@input_guardrail` and `@output_guardrail`) [src/agents/guardrail.py:202-245]() or dataclasses (`InputGuardrail` and `OutputGuardrail`) [src/agents/guardrail.py:72-134](). They receive a `RunContextWrapper`, the current `Agent`, and the target data, returning a `GuardrailFunctionOutput` [src/agents/guardrail.py:19-33]().

### Core Entities

```mermaid
classDiagram
    class GuardrailFunctionOutput {
        +Any output_info
        +bool tripwire_triggered
    }
    class InputGuardrailResult {
        +InputGuardrail guardrail
        +GuardrailFunctionOutput output
    }
    class OutputGuardrailResult {
        +OutputGuardrail guardrail
        +Any agent_output
        +Agent agent
        +GuardrailFunctionOutput output
    }
    class InputGuardrail {
        +Callable guardrail_function
        +bool run_in_parallel
        +run(agent, input, context)
    }
    class OutputGuardrail {
        +Callable guardrail_function
        +run(context, agent, agent_output)
    }
    GuardrailFunctionOutput --* InputGuardrailResult : "[src/agents/guardrail.py:44-45]"
    GuardrailFunctionOutput --* OutputGuardrailResult : "[src/agents/guardrail.py:67-68]"
    InputGuardrail --* InputGuardrailResult : "[src/agents/guardrail.py:39-39]"
    OutputGuardrail --* OutputGuardrailResult : "[src/agents/guardrail.py:52-52]"
```

For decorators, result structures, and examples, see [Input and Output Guardrails](#6.2).

Sources: `src/agents/guardrail.py:19-186` [src/agents/guardrail.py:19-186]()

---

## Tool Guardrails

Tool input and output guardrails specialize in intercepting calls to function tools [tests/test_tool_guardrails.py:88-189](). They operate on tool arguments and execution outputs independently of agent-level guardrails.

* **Tool Input Guardrails**: Validate arguments before a tool executes [tests/test_tool_guardrails.py:91-117]().
* **Tool Output Guardrails**: Inspect and validate return values produced by tool functions [tests/test_tool_guardrails.py:155-181]().

For detailed per-tool validation flows, see [Tool Guardrails](#6.3).

Sources: `tests/test_tool_guardrails.py:88-189` [tests/test_tool_guardrails.py:88-189]()

---

## Guardrail Execution Strategies

Input guardrails support concurrent execution via the `run_in_parallel` configuration parameter [src/agents/guardrail.py:100-103]().

| Strategy | `run_in_parallel` | Description |
|----------|-------------------|-------------|
| **Parallel** | `True` (Default) | Guardrail runs concurrently with the agent turn using `asyncio.create_task` [src/agents/run_internal/guardrails.py:66-69](). Optimizes latency. |
| **Blocking** | `False` | Guardrail completes entirely before the agent starts processing, preventing token consumption if validation fails. |

For synchronization models and performance tradeoffs, see [Guardrail Execution Strategies](#6.4).

Sources: `src/agents/guardrail.py:100-103` [src/agents/guardrail.py:100-103](), `src/agents/run_internal/guardrails.py:66-69` [src/agents/run_internal/guardrails.py:66-69]()

---

## Tripwire Mechanism

When a guardrail function indicates a policy breach by setting `tripwire_triggered=True`, the SDK raises a tripwire exception (`InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered`), halting execution immediately [src/agents/guardrail.py:81-84](), [src/agents/run_internal/guardrails.py:157-158]().

### Diagram: Tripwire Execution Halt

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        UserMsg[""Unsafe User Request"""]
    end

    subgraph "CodeEntitySpace"
        Runner[""Runner.run()""]
        Internal[""run_input_guardrails()""]
        Guard[""InputGuardrail.run()""]
        Result[""GuardrailFunctionOutput(tripwire_triggered=True)""]
        Exc[""InputGuardrailTripwireTriggered""]
    end

    UserMsg --> Runner
    Runner --> Internal
    Internal --> Guard
    Guard --> Result
    Result --> Exc
    Exc --> Runner
```

For exception hierarchy details and recovery patterns, see [Tripwire Mechanism](#6.5).

Sources: `src/agents/guardrail.py:71-84` [src/agents/guardrail.py:71-84](), `src/agents/run_internal/guardrails.py:116-169` [src/agents/run_internal/guardrails.py:116-169]()

---

## Child Pages

* [Guardrail Architecture](#6.1) — Detailed overview of system design, types, and execution points.
* [Input and Output Guardrails](#6.2) — `@input_guardrail` and `@output_guardrail` decorators, result types, and behaviors.
* [Tool Guardrails](#6.3) — `@tool_input_guardrail` and `@tool_output_guardrail` for per-tool validation.
* [Guardrail Execution Strategies](#6.4) — Synchronous vs parallel configuration and performance considerations.
* [Tripwire Mechanism](#6.5) — `is_tripwire` configurations, exceptions, and immediate halt handling.

---

