<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RPG-ZeroRepo · extra page Workflow Types and Error Handling · fetched 2026-10-26 -->

# Workflow Types and Error Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [configs/trae_config.yaml](configs/trae_config.yaml)
- [configs/zerorepo_config.yaml](configs/zerorepo_config.yaml)

</details>



## Purpose and Scope

This page documents the workflow execution system used during Phase 3 code generation, specifically focusing on the five workflow types that the TRAE agent executes and the error handling mechanisms that enable automatic recovery from failures. This page covers the iterative loop mechanics, error classification, retry logic, and state persistence.

For information about the overall TDD workflow and test-code generation cycle, see [Test-Driven Development Workflow](#3.3.1). For information about the TRAE agent's tools and capabilities, see [TRAE Agent](#6.2).

**Sources:** [README.md:284-351](), [configs/zerorepo_config.yaml:53-72]()

---

## Workflow Type Overview

The code generation phase uses five distinct workflow types, each designed to handle a specific stage or failure mode in the TDD loop. Each workflow type determines what instructions are sent to the TRAE agent and what success criteria are evaluated.

### Workflow Type Definitions

| Workflow Type | Purpose | Trigger Condition | Success Criteria |
|---------------|---------|-------------------|------------------|
| `TEST_DEVELOPMENT` | Generate initial test file from requirements | First iteration of a task batch | Test file created, syntactically valid |
| `CODE_INCREMENTAL` | Implement code to satisfy interface skeleton | First iteration after successful test generation | Code implements required units, passes tests |
| `TEST_FIX` | Repair broken or invalid test code | Test execution fails with test errors (syntax, import, assertion logic errors) | Tests execute without test-side errors |
| `CODE_BUG_FIX` | Fix implementation bugs revealed by tests | Tests execute but fail due to incorrect implementation behavior | Tests pass |
| `ENV_SETUP` | Install dependencies or fix environment issues | Import errors, missing packages detected | Environment issue resolved |

The workflow type selection is deterministic based on the current state of the iteration and the error classification from the previous attempt.

**Sources:** [README.md:316-324](), [configs/zerorepo_config.yaml:63-71]()

---

## Workflow State Machine

The following diagram shows how workflow types transition based on execution results.

**Diagram: Workflow Type State Machine**

```mermaid
stateDiagram-v2
    [*] --> TEST_DEVELOPMENT: "Start new task batch"
    
    TEST_DEVELOPMENT --> CODE_INCREMENTAL: "Test generation successful"
    TEST_DEVELOPMENT --> TEST_FIX: "Test has errors"
    TEST_DEVELOPMENT --> ENV_SETUP: "Import/dependency error"
    TEST_DEVELOPMENT --> [*]: "Max test retries exceeded"
    
    CODE_INCREMENTAL --> [*]: "Tests pass (SUCCESS)"
    CODE_INCREMENTAL --> CODE_BUG_FIX: "Tests fail (implementation bug)"
    CODE_INCREMENTAL --> ENV_SETUP: "Import/dependency error"
    CODE_INCREMENTAL --> [*]: "Max code retries exceeded"
    
    TEST_FIX --> CODE_INCREMENTAL: "Test errors resolved"
    TEST_FIX --> TEST_FIX: "Test still has errors"
    TEST_FIX --> [*]: "Max test retries exceeded"
    
    CODE_BUG_FIX --> [*]: "Tests pass (SUCCESS)"
    CODE_BUG_FIX --> CODE_BUG_FIX: "Tests still fail"
    CODE_BUG_FIX --> TEST_FIX: "Fix broke tests"
    CODE_BUG_FIX --> [*]: "Max code retries exceeded"
    
    ENV_SETUP --> TEST_DEVELOPMENT: "Environment fixed, retry test gen"
    ENV_SETUP --> CODE_INCREMENTAL: "Environment fixed, retry code gen"
    ENV_SETUP --> ENV_SETUP: "Environment issue persists"
    ENV_SETUP --> [*]: "Max env retries exceeded"
    
    note right of TEST_DEVELOPMENT
        Workflow: Generate test file
        Agent receives: task skeleton,
        feature descriptions, examples
    end note
    
    note right of CODE_INCREMENTAL
        Workflow: Implement skeleton
        Agent receives: interface code,
        test file, failing test output
    end note
    
    note right of TEST_FIX
        Workflow: Fix test errors
        Agent receives: test file,
        error traceback, lint output
    end note
    
    note right of CODE_BUG_FIX
        Workflow: Fix implementation
        Agent receives: code file,
        test failures, assertions
    end note
    
    note right of ENV_SETUP
        Workflow: Fix environment
        Agent receives: error message,
        requirements.txt, setup.py
    end note
```

**Sources:** [README.md:291-313](), [configs/zerorepo_config.yaml:69-70]()

---

## Error Detection and Classification

After each TRAE agent execution, the system analyzes the pytest output and execution logs to classify the result into one of three error categories or success.

### Error Classification Logic

**Diagram: Error Classification Decision Tree**

```mermaid
graph TD
    Start["pytest execution completed"]
    
    Start --> CheckExit{"Exit code?"}
    CheckExit -->|"0"| Success["SUCCESS: All tests passed"]
    CheckExit -->|"!= 0"| ParseOutput["Parse pytest output"]
    
    ParseOutput --> CheckImport{"Import errors<br/>or ModuleNotFoundError?"}
    CheckImport -->|"Yes"| ENV["ENV_ERROR:<br/>Missing dependencies"]
    CheckImport -->|"No"| CheckSyntax
    
    CheckSyntax{"Syntax errors<br/>in test file?"}
    CheckSyntax -->|"Yes"| TestErr["TEST_ERROR:<br/>Test code invalid"]
    CheckSyntax -->|"No"| CheckTestFail
    
    CheckTestFail{"Test failures<br/>assertion errors?"}
    CheckTestFail -->|"Yes"| CheckLocation{"Failure in<br/>test code?"}
    CheckTestFail -->|"No"| CheckCollection
    
    CheckLocation -->|"Yes"| TestErr
    CheckLocation -->|"No"| CodeErr["CODE_ERROR:<br/>Implementation bug"]
    
    CheckCollection{"Collection errors?"}
    CheckCollection -->|"Yes"| TestErr
    CheckCollection -->|"No"| UnknownErr["UNKNOWN_ERROR:<br/>Unexpected failure"]
    
    style Success fill:#d4edda
    style ENV fill:#fff3cd
    style TestErr fill:#f8d7da
    style CodeErr fill:#f8d7da
    style UnknownErr fill:#f8d7da
```

### Error Type Characteristics

| Error Type | Detection Pattern | Example Scenario | Next Workflow |
|------------|------------------|------------------|---------------|
| `ENV_ERROR` | `ModuleNotFoundError`, `ImportError` in traceback | Missing `numpy`, `pytest-mock` not installed | `ENV_SETUP` |
| `TEST_ERROR` | Syntax error in `test_*.py`, collection failure, fixture error | Invalid test syntax, undefined fixture, malformed assertion | `TEST_FIX` |
| `CODE_ERROR` | Assertion failure, attribute error in source code | Function returns wrong value, method not implemented | `CODE_BUG_FIX` |
| `SUCCESS` | Exit code 0, all tests passed | Implementation correct | Task complete |

**Sources:** [README.md:295-312](), [configs/trae_config.yaml:1-28]()

---

## Retry Mechanism Configuration

The retry system has three configurable limits to prevent infinite loops while allowing reasonable recovery attempts.

### Retry Parameters

**Configuration in `zerorepo_config.yaml`:**

```yaml
code_generation:
  trae_agent:
    max_iterations: 5              # Total iteration budget per task batch
    max_retries_per_workflow: 3    # Max consecutive retries for same workflow type
    workflow_timeout: 1800          # Timeout per workflow execution (seconds)
    max_retries: 3                  # Global retry limit for agent failures
    retry_delay: 5                  # Wait time between retries (seconds)
```

### Retry Logic Behavior

**Diagram: Retry Decision Logic**

```mermaid
graph TB
    ExecuteWorkflow["Execute workflow in Docker"]
    
    ExecuteWorkflow --> CheckTimeout{"Execution time<br/>> workflow_timeout?"}
    CheckTimeout -->|"Yes"| TimeoutKill["Kill container"]
    TimeoutKill --> RecordTimeout["Record timeout failure"]
    RecordTimeout --> CheckGlobalRetry
    
    CheckTimeout -->|"No"| CheckAgentError{"Agent crashed<br/>or exception?"}
    CheckAgentError -->|"Yes"| CheckGlobalRetry{"global_retries<br/>< max_retries?"}
    CheckGlobalRetry -->|"Yes"| WaitRetry["Wait retry_delay seconds"]
    WaitRetry --> IncrGlobal["Increment global_retries"]
    IncrGlobal --> ExecuteWorkflow
    CheckGlobalRetry -->|"No"| FailTask["Mark task as FAILED"]
    
    CheckAgentError -->|"No"| ClassifyError["Classify error from pytest"]
    ClassifyError --> DetermineNext["Determine next workflow type"]
    
    DetermineNext --> CheckWorkflowRetry{"workflow_retries[type]<br/>< max_retries_per_workflow?"}
    CheckWorkflowRetry -->|"Yes"| CheckIterLimit{"total_iterations<br/>< max_iterations?"}
    CheckIterLimit -->|"Yes"| IncrWorkflow["Increment workflow_retries[type]"]
    IncrWorkflow --> IncrIter["Increment total_iterations"]
    IncrIter --> ExecuteWorkflow
    
    CheckIterLimit -->|"No"| IterExhaust["Mark task as EXHAUSTED"]
    CheckWorkflowRetry -->|"No"| RetryExhaust["Mark workflow as STUCK"]
    
    ClassifyError --> Success{"Result = SUCCESS?"}
    Success -->|"Yes"| TaskComplete["Mark task as COMPLETE"]
    
    style TaskComplete fill:#d4edda
    style FailTask fill:#f8d7da
    style IterExhaust fill:#f8d7da
    style RetryExhaust fill:#f8d7da
```

### Retry Counter Management

The system maintains three separate retry counters per task batch:

1. **`total_iterations`**: Increments on every workflow execution (limit: `max_iterations`)
2. **`workflow_retries[workflow_type]`**: Tracks consecutive attempts for each workflow type (limit: `max_retries_per_workflow`)
3. **`global_retries`**: Tracks agent-level failures like crashes or network errors (limit: `max_retries`)

When a workflow type changes (e.g., `TEST_FIX` → `CODE_INCREMENTAL`), the `workflow_retries` counter for the new type starts fresh, but `total_iterations` continues incrementing.

**Sources:** [configs/zerorepo_config.yaml:63-71]()

---

## Iteration State Persistence

All iteration state is persisted to enable resume capability and post-execution analysis.

### State Files

| File | Location | Content | Updated When |
|------|----------|---------|--------------|
| `iteration_state.json` | `checkpoints/` | Current iteration number, workflow type, retry counts for active batch | After each workflow execution |
| `execution_history.json` | `checkpoints/` | Flat list of all workflow executions with timestamps, results, errors | After each workflow execution |
| `batch_trajectory.json` | `checkpoints/` | Per-batch execution records grouped by batch ID, includes commit SHAs | After batch completion |
| `task_manager_state.json` | `checkpoints/` | Overall task progress: completed, failed, current task | After batch completion or failure |

### Iteration State Schema

```json
// iteration_state.json example
{
  "task_id": "src_io_persistence_serialization.py_HighScoreBinarySerializer",
  "batch_id": "io.input_persistence",
  "current_iteration": 3,
  "total_iterations": 3,
  "current_workflow": "CODE_BUG_FIX",
  "workflow_retries": {
    "TEST_DEVELOPMENT": 0,
    "CODE_INCREMENTAL": 1,
    "TEST_FIX": 0,
    "CODE_BUG_FIX": 2,
    "ENV_SETUP": 0
  },
  "global_retries": 0,
  "last_error_type": "CODE_ERROR",
  "last_error_message": "AssertionError: Expected 8 bytes, got 10",
  "test_patch_path": "results/test_gen_1770643795/test_gen_1770643795.patch",
  "code_patch_path": "results/code_gen_1770644020/code_gen_1770644020.patch",
  "last_commit_sha": "a3f2e1d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4",
  "started_at": "2026-02-09T13:45:12",
  "last_updated": "2026-02-09T13:52:30"
}
```

**Sources:** [README.md:395-399](), [configs/zerorepo_config.yaml:63-71]()

---

## Failure Modes and Recovery

### Task Completion States

When a task batch completes (successfully or not), it is marked with one of the following states in `task_manager_state.json`:

| State | Meaning | Recovery Action |
|-------|---------|-----------------|
| `COMPLETE` | All tests pass, batch succeeded | None needed, proceed to next batch |
| `FAILED` | Agent crashed or non-recoverable error | Manual intervention required, or skip with `--skip-failed` |
| `EXHAUSTED` | Hit `max_iterations` limit without success | Review task complexity, increase limits, or manual completion |
| `STUCK` | Hit `max_retries_per_workflow` for a workflow type | Review error patterns, may indicate task specification issue |
| `TIMEOUT` | Hit `workflow_timeout` on execution | Review task scope, increase timeout, or check for infinite loops |

### Task Manager State Update

**Diagram: Task State Tracking**

```mermaid
graph LR
    Pending["Task: PENDING<br/>(in planned_batches_dict)"]
    
    Pending --> Executing["Task: EXECUTING<br/>(in current_task)"]
    
    Executing --> Success{"Result?"}
    
    Success -->|"SUCCESS"| Complete["Task: COMPLETE<br/>(added to completed_tasks)"]
    Success -->|"FAILED"| Failed["Task: FAILED<br/>(added to failed_tasks)"]
    Success -->|"EXHAUSTED"| Exhausted["Task: EXHAUSTED<br/>(added to failed_tasks)"]
    Success -->|"STUCK"| Stuck["Task: STUCK<br/>(added to failed_tasks)"]
    Success -->|"TIMEOUT"| Timeout["Task: TIMEOUT<br/>(added to failed_tasks)"]
    
    Complete --> UpdateManager["Update task_manager_state.json"]
    Failed --> UpdateManager
    Exhausted --> UpdateManager
    Stuck --> UpdateManager
    Timeout --> UpdateManager
    
    UpdateManager --> NextTask{"More tasks?"}
    NextTask -->|"Yes"| Pending
    NextTask -->|"No"| Done["code_generation: true"]
    
    style Complete fill:#d4edda
    style Failed fill:#f8d7da
    style Exhausted fill:#f8d7da
    style Stuck fill:#f8d7da
    style Timeout fill:#f8d7da
```

### Resume Behavior

When resuming with `--resume`:

1. System reads `task_manager_state.json` to determine completion status
2. Skips all batches in `completed_tasks` array
3. Loads `iteration_state.json` for the `current_task` if it exists (partial completion)
4. Retries tasks in `failed_tasks` if `--retry-failed` flag is set
5. Continues from next pending batch otherwise

**Sources:** [README.md:354-380](), [configs/zerorepo_config.yaml:63-71]()

---

## Timeout and Resource Management

### Workflow Timeout Enforcement

The `workflow_timeout` parameter (default: 1800 seconds / 30 minutes) prevents runaway executions. When a timeout occurs:

1. Docker container is forcibly stopped via `docker stop`
2. Partial results are discarded (no patch files saved)
3. Timeout is recorded in `execution_history.json`
4. Retry logic determines if another attempt should be made

### Container Lifecycle

**Diagram: Docker Container Management Per Workflow**

```mermaid
sequenceDiagram
    participant ICG as "IterativeCodeGenerator"
    participant Docker as "Docker API"
    participant Container as "python-azure-pytest:3.12"
    participant TRAE as "trae_agent process"
    
    ICG->>Docker: "docker run --name zerorepo_2<br/>-v workspace:/tare_workspace"
    Docker->>Container: Start container
    Container->>TRAE: Launch agent with task.txt
    
    par Execution
        TRAE->>TRAE: Generate patch (test or code)
        and Timeout Monitor
        ICG->>ICG: Wait up to workflow_timeout
    end
    
    alt Normal Completion
        TRAE->>Container: Write patch file, exit 0
        Container->>Docker: Container exits
        Docker->>ICG: Return exit code, copy patch
        ICG->>ICG: Classify result
    else Timeout
        ICG->>Docker: "docker stop -t 10 zerorepo_2"
        Docker->>Container: SIGTERM → SIGKILL
        Container->>Docker: Forcibly stopped
        Docker->>ICG: Return timeout error
        ICG->>ICG: Record TIMEOUT failure
    else Agent Crash
        TRAE->>Container: Unhandled exception, exit 1
        Container->>Docker: Container exits with error
        Docker->>ICG: Return error code
        ICG->>ICG: Increment global_retries
    end
    
    ICG->>Docker: "docker rm zerorepo_2"
    Docker->>Docker: Clean up container
```

**Sources:** [configs/zerorepo_config.yaml:54-61](), [configs/trae_config.yaml:1-28]()

---

## Best Practices for Configuration

### Recommended Parameter Tuning

| Scenario | Recommended Settings | Rationale |
|----------|---------------------|-----------|
| **Simple utility functions** | `max_iterations: 3`<br/>`max_retries_per_workflow: 2` | Straightforward tasks should converge quickly |
| **Complex algorithms** | `max_iterations: 7`<br/>`max_retries_per_workflow: 3`<br/>`workflow_timeout: 2400` | More iteration budget for complex logic |
| **Large file batches** | `workflow_timeout: 3600` | Large files take longer to generate and test |
| **Network-dependent tests** | `max_retries: 5`<br/>`retry_delay: 10` | Allow recovery from transient network issues |
| **Resource-constrained environments** | `workflow_timeout: 900`<br/>Reduce parallel batches | Prevent OOM or disk exhaustion |

### Common Failure Patterns

| Pattern | Symptom | Solution |
|---------|---------|----------|
| **Flapping between `TEST_FIX` and `CODE_BUG_FIX`** | `workflow_retries` maxed for both | Test and implementation have incompatible assumptions; review task specification |
| **Repeated `ENV_ERROR`** | Multiple `ENV_SETUP` attempts fail | Missing system dependencies or incompatible package versions; check Dockerfile |
| **All batches hit `TIMEOUT`** | Every task times out | Model too slow, tasks too complex, or infinite loops; reduce task scope or increase timeout |
| **High `global_retries` count** | Frequent agent crashes | LLM API issues, container stability problems, or memory exhaustion |

**Sources:** [configs/zerorepo_config.yaml:63-71](), [README.md:291-351]()

---

