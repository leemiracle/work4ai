<!-- source: DeepWiki mcp.deepwiki.com · repo agno-agi/agno · extra page Workflow Step Types · fetched 2026-11-09 -->

# Workflow Step Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookbook/04_workflows/03_loop_execution/loop_iterative_accumulation.py](cookbook/04_workflows/03_loop_execution/loop_iterative_accumulation.py)
- [cookbook/04_workflows/08_human_in_the_loop/condition/02_condition_on_error.py](cookbook/04_workflows/08_human_in_the_loop/condition/02_condition_on_error.py)
- [libs/agno/agno/run/workflow.py](libs/agno/agno/run/workflow.py)
- [libs/agno/agno/workflow/condition.py](libs/agno/agno/workflow/condition.py)
- [libs/agno/agno/workflow/loop.py](libs/agno/agno/workflow/loop.py)
- [libs/agno/agno/workflow/parallel.py](libs/agno/agno/workflow/parallel.py)
- [libs/agno/agno/workflow/router.py](libs/agno/agno/workflow/router.py)
- [libs/agno/agno/workflow/step.py](libs/agno/agno/workflow/step.py)
- [libs/agno/agno/workflow/steps.py](libs/agno/agno/workflow/steps.py)
- [libs/agno/agno/workflow/types.py](libs/agno/agno/workflow/types.py)
- [libs/agno/agno/workflow/workflow.py](libs/agno/agno/workflow/workflow.py)
- [libs/agno/tests/integration/workflows/test_condition_steps.py](libs/agno/tests/integration/workflows/test_condition_steps.py)
- [libs/agno/tests/integration/workflows/test_loop_steps.py](libs/agno/tests/integration/workflows/test_loop_steps.py)
- [libs/agno/tests/integration/workflows/test_parallel_steps.py](libs/agno/tests/integration/workflows/test_parallel_steps.py)
- [libs/agno/tests/integration/workflows/test_router_steps.py](libs/agno/tests/integration/workflows/test_router_steps.py)
- [libs/agno/tests/unit/workflow/test_media_aggregation.py](libs/agno/tests/unit/workflow/test_media_aggregation.py)
- [libs/agno/tests/unit/workflow/test_parallel_run_context_isolation.py](libs/agno/tests/unit/workflow/test_parallel_run_context_isolation.py)
- [libs/agno/tests/unit/workflow/test_previous_content_values.py](libs/agno/tests/unit/workflow/test_previous_content_values.py)
- [libs/agno/tests/unit/workflow/test_step_output_content_roundtrip.py](libs/agno/tests/unit/workflow/test_step_output_content_roundtrip.py)

</details>



This document details the workflow step types available in the Agno framework for composing multi-step orchestration pipelines. These types serve as building blocks for workflows, enabling sequential execution, parallel processing, conditional logic, iteration, and dynamic routing.

For information about workflow execution and context propagation, see **2.3.2 Step Execution and Context**. For Human-in-the-Loop (HITL) workflows, see **2.3.3 Human-in-the-Loop (HITL) Workflows**.

Sources: [libs/agno/agno/workflow/workflow.py:168-193]()

---

## Step Type Overview

The framework provides six step types organized into basic and container categories. Each type is mapped to a `StepType` enum and handled by specific classes within the `agno.workflow` module.

| Step Type | Category | Purpose | Execution Model |
|-----------|----------|---------|-----------------|
| `Step` | Basic | Single unit of work with agent, team, or function executor | Sequential |
| `Steps` | Container | Sequential pipeline of steps | Sequential |
| `Parallel` | Container | Concurrent execution of independent steps | Parallel (`ThreadPoolExecutor`) |
| `Loop` | Container | Iteration over steps with end condition | Sequential with repetition |
| `Condition` | Container | Conditional branching (if/else) | Conditional |
| `Router` | Container | Dynamic step selection | Conditional |

### Code Entity Mapping

The following diagram associates the logical step types with their corresponding implementation classes and enum identifiers.

**Diagram: Step Implementation Registry Mapping**
```mermaid
graph TB
    StepType["StepTypeEnum<br/>libs/agno/agno/workflow/types.py"]
    
    subgraph "Implementation Classes"
    StepClass["Step<br/>agno.workflow.step.Step"]
    StepsClass["Steps<br/>agno.workflow.steps.Steps"]
    ParallelClass["Parallel<br/>agno.workflow.parallel.Parallel"]
    LoopClass["Loop<br/>agno.workflow.loop.Loop"]
    ConditionClass["Condition<br/>agno.workflow.condition.Condition"]
    RouterClass["Router<br/>agno.workflow.router.Router"]
    end

    StepType -- "STEP" --> StepClass
    StepType -- "STEPS" --> StepsClass
    StepType -- "PARALLEL" --> ParallelClass
    StepType -- "LOOP" --> LoopClass
    StepType -- "CONDITION" --> ConditionClass
    StepType -- "ROUTER" --> RouterClass

    Mapping["STEP_TYPE_MAPPING<br/>libs/agno/agno/workflow/workflow.py"]
    Mapping -.-> StepType
```

Sources: [libs/agno/agno/workflow/workflow.py:186-193](), [libs/agno/agno/workflow/types.py:80-90]()

---

## Step (Basic Building Block)

The `Step` class is the atomic unit of work in an Agno workflow. It encapsulates an executor and manages its lifecycle, including retries and Human-in-the-Loop (HITL) requirements.

### Executor Types

A `Step` must have exactly one executor assigned during initialization:

| Executor | Field | Code Entity | Description |
|----------|-------|-------------|-------------|
| Agent | `agent` | `agno.agent.Agent` | Individual AI agent with tools and memory |
| Team | `team` | `agno.team.Team` | Orchestrated group of agents |
| Function | `executor` | `StepExecutor` | Callable Python function or coroutine |
| Workflow | `workflow` | `agno.workflow.Workflow` | Nested workflow support |

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | 3 | Retries on execution failure |
| `skip_on_failure` | `bool` | False | Continue workflow if this step fails |
| `strict_input_validation` | `bool` | False | Raise error on missing required inputs |

### HITL Configuration

The `Step` class supports extensive HITL controls configured via a `HumanReview` object:
- `requires_confirmation`: Pauses for user approval before running.
- `requires_user_input`: Pauses to collect data defined in `user_input_schema`.
- `requires_output_review`: Pauses after execution for verification of `StepOutput`.
- `on_error`: Can be set to `OnError.pause` to allow manual recovery via HITL.

Sources: [libs/agno/agno/workflow/step.py:1-203](), [libs/agno/agno/workflow/types.py:64-107]()

---

## Steps (Sequential Container)

The `Steps` class manages a pipeline of `WorkflowSteps` executed in order.

### Execution Flow

When `Steps` are executed, the workflow iterates through the list. The output of each step is merged into the `StepInput` for the next step, enabling data flow through the pipeline. This is handled by helper methods that normalize various inputs (Agents, Teams, Callables) into `Step` objects.

**Diagram: Sequential Steps Pipeline Execution Flow**
```mermaid
graph TD
    S_Start["StartSequentialPipeline"] --> S_Prep["prepare_steps()"]
    S_Prep --> S_Loop["ForInnerStepInSteps"]
    S_Loop --> S_Run["step.execute(current_input)"]
    S_Run --> S_Update["UpdateCurrentInputWithStepOutput"]
    S_Update --> S_CheckStop{"step_output.stop?"}
    S_CheckStop -- "Yes" --> S_End["BreakAndReturnResults"]
    S_CheckStop -- "No" --> S_Loop
```

Sources: [libs/agno/agno/workflow/steps.py:40-178]()

---

## Parallel (Concurrent Execution Container)

The `Parallel` class enables concurrent execution of independent steps using a `ThreadPoolExecutor`.

### Concurrency and Context

To ensure thread safety and data integrity, `Parallel` performs the following operations:
1. **Context Propagation:** Uses `copy_context().run()` to ensure `ContextVar` values (like tracing or logging IDs) are available in worker threads.
2. **State Merging:** After all steps complete, it uses `merge_parallel_session_states` to reconcile updates to the `session_state` from different threads.

### HITL Guard

`Parallel` steps cannot contain steps that require HITL pauses (like `requires_confirmation` or `requires_user_input`) because execution is non-blocking across threads, making session suspension and resumption ambiguous.

Sources: [libs/agno/agno/workflow/parallel.py:47-96](), [libs/agno/agno/workflow/parallel.py:1-25]()

---

## Loop (Iteration Container)

The `Loop` class repeats a sequence of steps until an `end_condition` is met or `max_iterations` is reached.

### End Condition Evaluation

The `end_condition` can be a Python callable or a Common Expression Language (CEL) string.
- **forward_iteration_output:** If `True`, the output of iteration $N$ is passed as input to iteration $N+1$.
- **Iteration Review:** Loops support `requires_iteration_review` which pauses the workflow after each iteration for user feedback.

Sources: [libs/agno/agno/workflow/loop.py:43-106](), [libs/agno/agno/workflow/loop.py:165-180]()

---

## Condition (Conditional Branching)

The `Condition` class provides if/else logic based on an evaluator.

### Branching Logic
- **Evaluator:** A boolean, callable, or CEL expression that determines the path.
- **Branches:** Executes `steps` if true, and `else_steps` if false.
- **CEL Variables:** CEL expressions have access to `input`, `previous_step_content`, `previous_step_outputs`, `additional_data`, and `session_state`.

Sources: [libs/agno/agno/workflow/condition.py:55-146]()

---

## Router (Dynamic Selection)

The `Router` dynamically selects which step(s) from its `choices` to execute based on input or user interaction.

### Selection Mechanisms
1. **Programmatic:** A `selector` function returns the list of steps to run.
2. **CEL Expression:** A string expression that resolves to the name of one of the `choices`.
3. **Human-Driven:** If `requires_user_input` is True, the workflow pauses and presents the `choices` to the user for manual selection.
4. **Multiple Selections:** If `allow_multiple_selections` is True in `HumanReview`, the user can pick multiple routes to execute.

Sources: [libs/agno/agno/workflow/router.py:50-130]()

---

## Common Execution Events

All step types emit standardized events during execution to provide observability via `WorkflowRunEvent`.

| Event Type | Emitted By | Description |
|------------|------------|-------------|
| `StepStarted` | `Step` | Emitted when any step begins execution |
| `StepCompleted` | `Step` | Emitted when a step finishes successfully |
| `StepExecutorPaused` | `Step` | Emitted when an Agent/Team inside a step pauses for HITL |
| `LoopIterationStarted` | `Loop` | Emitted at the start of each loop iteration |
| `ParallelExecutionStarted` | `Parallel` | Emitted when a parallel block begins |
| `ConditionExecutionStarted`| `Condition` | Emitted when a condition evaluation begins |
| `RouterExecutionStarted` | `Router` | Emitted when routing logic starts |

Sources: [libs/agno/agno/run/workflow.py:39-83]()

---

