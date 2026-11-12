<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/workflow-use · page 5 Workflow Execution · fetched 2026-10-30 -->

# Workflow Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [workflows/.gitignore](workflows/.gitignore)
- [workflows/cli.py](workflows/cli.py)
- [workflows/workflow_use/recorder/recorder.py](workflows/workflow_use/recorder/recorder.py)
- [workflows/workflow_use/schema/views.py](workflows/workflow_use/schema/views.py)
- [workflows/workflow_use/storage/__init__.py](workflows/workflow_use/storage/__init__.py)
- [workflows/workflow_use/workflow/semantic_executor.py](workflows/workflow_use/workflow/semantic_executor.py)
- [workflows/workflow_use/workflow/semantic_extractor.py](workflows/workflow_use/workflow/semantic_extractor.py)
- [workflows/workflow_use/workflow/service.py](workflows/workflow_use/workflow/service.py)

</details>



This document covers the runtime execution of workflows, including the core execution engine, different execution strategies, error handling, and browser automation integration. For information about creating workflows, see [Workflow Builder](#4). For details about the workflow definition schema, see [Workflow Definition Schema](#2.1).

## Overview

Workflow execution is handled by the `Workflow` class, which orchestrates the execution of workflow steps through different strategies depending on the step type and execution mode. The system supports three primary execution modes:

- **Standard Execution**: Combines deterministic browser actions with AI-powered agent steps and fallback mechanisms
- **Semantic Execution**: Uses semantic text mapping for deterministic execution without AI dependencies
- **Tool Execution**: Exposes workflows as LangChain tools for integration with AI agents

### Execution Architecture

```mermaid
graph TB
    subgraph "Execution Modes"
        STANDARD["Workflow.run()"]
        SEMANTIC["Workflow.run_with_no_ai()"]
        TOOL["Workflow.run_as_tool()"]
    end
    
    subgraph "Core Engine"
        WORKFLOW["Workflow"]
        CONTEXT["Context Management"]
        PLACEHOLDER["Placeholder Resolution"]
    end
    
    subgraph "Step Executors"
        DETERMINISTIC["DeterministicWorkflowStep"]
        AGENTIC["AgenticWorkflowStep"]
        CONTROLLER["WorkflowController"]
        SEMANTIC_EXEC["SemanticWorkflowExecutor"]
        AGENT["Agent"]
    end
    
    subgraph "Browser Layer"
        BROWSER["Browser"]
        SEMANTIC_EXT["SemanticExtractor"]
        PAGE["Page"]
    end
    
    STANDARD --> WORKFLOW
    SEMANTIC --> WORKFLOW
    TOOL --> WORKFLOW
    
    WORKFLOW --> CONTEXT
    WORKFLOW --> PLACEHOLDER
    
    DETERMINISTIC --> CONTROLLER
    AGENTIC --> AGENT
    SEMANTIC --> SEMANTIC_EXEC
    
    CONTROLLER --> BROWSER
    SEMANTIC_EXEC --> SEMANTIC_EXT
    AGENT --> BROWSER
    
    SEMANTIC_EXT --> PAGE
    CONTROLLER --> PAGE
```

**Sources:** [workflows/workflow_use/workflow/service.py:40-816](), [workflows/workflow_use/workflow/semantic_executor.py:25-1094]()

## Execution Modes

### Standard Execution Mode

The standard execution mode (`Workflow.run()`) supports both deterministic and agentic workflow steps with AI-powered fallback mechanisms.

```mermaid
flowchart TD
    START["workflow.run(inputs)"] --> VALIDATE["_validate_inputs()"]
    VALIDATE --> INIT_CONTEXT["Initialize context"]
    INIT_CONTEXT --> BROWSER_START["browser.start()"]
    BROWSER_START --> STEP_LOOP["For each step"]
    
    STEP_LOOP --> RESOLVE["_resolve_placeholders()"]
    RESOLVE --> CHECK_TYPE["Check step type"]
    
    CHECK_TYPE -->|DeterministicWorkflowStep| DET_EXEC["_run_deterministic_step()"]
    CHECK_TYPE -->|AgenticWorkflowStep| AGENT_EXEC["_run_agent_step()"]
    
    DET_EXEC --> CONTROLLER_ACT["controller.act()"]
    CONTROLLER_ACT --> WAIT_ELEMENT["Wait for next element"]
    
    AGENT_EXEC --> AGENT_RUN["Agent.run()"]
    AGENT_RUN --> AGENT_RESULT["AgentHistoryList"]
    
    WAIT_ELEMENT --> STORE_OUTPUT["_store_output()"]
    AGENT_RESULT --> STORE_OUTPUT
    
    STORE_OUTPUT --> NEXT_STEP["Next step?"]
    NEXT_STEP -->|Yes| STEP_LOOP
    NEXT_STEP -->|No| OUTPUT_MODEL["Convert to output_model?"]
    
    OUTPUT_MODEL -->|Yes| CONVERT["_convert_results_to_output_model()"]
    OUTPUT_MODEL -->|No| RETURN_RESULTS["Return WorkflowRunOutput"]
    CONVERT --> RETURN_RESULTS
    
    RETURN_RESULTS --> CLEANUP["Browser cleanup"]
```

**Sources:** [workflows/workflow_use/workflow/service.py:548-612](), [workflows/workflow_use/workflow/service.py:108-147](), [workflows/workflow_use/workflow/service.py:193-216]()

### Semantic Execution Mode  

The semantic execution mode (`Workflow.run_with_no_ai()`) uses `SemanticWorkflowExecutor` to execute workflows without AI dependencies by mapping visible text to browser elements.

```mermaid
flowchart TD
    START["workflow.run_with_no_ai(inputs)"] --> VALIDATE["_validate_inputs()"]
    VALIDATE --> INIT_CONTEXT["Initialize context"]
    INIT_CONTEXT --> BROWSER_START["browser.start()"]
    BROWSER_START --> SEMANTIC_INIT["SemanticWorkflowExecutor(browser)"]
    
    SEMANTIC_INIT --> STEP_LOOP["For each step"]
    STEP_LOOP --> RESOLVE["_resolve_placeholders()"]
    RESOLVE --> CHECK_AGENT["step.type == 'agent'?"]
    
    CHECK_AGENT -->|Yes| ERROR["Raise Exception: Agent steps not supported"]
    CHECK_AGENT -->|No| SEMANTIC_EXEC["semantic_executor.execute_step()"]
    
    SEMANTIC_EXEC --> REFRESH_MAP["_refresh_semantic_mapping()"]
    REFRESH_MAP --> EXTRACT["SemanticExtractor.extract_semantic_mapping()"]
    EXTRACT --> FIND_ELEMENT["Find element by target_text"]
    FIND_ELEMENT --> EXECUTE_ACTION["Execute browser action"]
    
    EXECUTE_ACTION --> STORE_OUTPUT["_store_output()"]
    STORE_OUTPUT --> NEXT_STEP["Next step?"]
    NEXT_STEP -->|Yes| STEP_LOOP
    NEXT_STEP -->|No| RETURN_RESULTS["Return WorkflowRunOutput"]
```

**Sources:** [workflows/workflow_use/workflow/service.py:716-790](), [workflows/workflow_use/workflow/semantic_executor.py:1071-1093]()

### Tool Execution Mode

Workflows can be exposed as LangChain tools using `Workflow.as_tool()` and executed via `Workflow.run_as_tool()`.

**Sources:** [workflows/workflow_use/workflow/service.py:680-715](), [workflows/workflow_use/workflow/service.py:792-815]()

## Core Execution Engine

### Workflow Class

The `Workflow` class serves as the main orchestrator for workflow execution. It manages browser sessions, step execution, context variables, and output generation.

| Component | Purpose |
|-----------|---------|
| `workflow_schema` | Parsed workflow definition |
| `controller` | Handles deterministic browser actions |
| `browser` | Browser automation instance |
| `context` | Runtime variables and state |
| `inputs_def` | Input schema validation |

**Sources:** [workflows/workflow_use/workflow/service.py:40-83]()

### Context Management and Placeholder Resolution

The execution engine maintains a context dictionary for storing variables and supports placeholder resolution using Python format syntax.

```mermaid
graph LR
    INPUT["inputs: {'name': 'John'}"] --> CONTEXT["context: {'name': 'John'}"]
    STEP["Step: input 'Hello {name}'"] --> RESOLVE["_resolve_placeholders()"]
    RESOLVE --> CONTEXT
    RESOLVE --> RESOLVED["Resolved: 'Hello John'"]
```

The `_resolve_placeholders()` method recursively processes workflow steps to replace `{variable}` placeholders with values from the context dictionary.

**Sources:** [workflows/workflow_use/workflow/service.py:305-357](), [workflows/workflow_use/workflow/service.py:292-303]()

### Output Storage and Variable Extraction

Steps can declare an `output` field to store execution results in the context for use by subsequent steps. The `_store_output()` method handles different result types.

**Sources:** [workflows/workflow_use/workflow/service.py:359-401]()

## Step Execution Strategies

### Deterministic Step Execution

Deterministic steps are executed through the `WorkflowController` which handles browser actions like navigation, clicking, input, and extraction.

```mermaid
flowchart TD
    STEP["DeterministicWorkflowStep"] --> CREATE_MODEL["registry.create_action_model()"]
    CREATE_MODEL --> ACTION_MODEL["ActionModel(**params)"]
    ACTION_MODEL --> CONTROLLER_ACT["controller.act(action_model, browser)"]
    CONTROLLER_ACT --> WAIT_NEXT["Wait for next element (if exists)"]
    WAIT_NEXT --> RESULT["ActionResult"]
```

The execution includes automatic waiting for the next step's target element to ensure page readiness.

**Sources:** [workflows/workflow_use/workflow/service.py:108-147]()

### Agentic Step Execution

Agentic steps create an AI agent with contextual information about surrounding workflow steps.

```mermaid
flowchart TD
    AGENT_STEP["AgenticWorkflowStep"] --> FORMAT_CONTEXT["_format_agent_step_context()"]
    FORMAT_CONTEXT --> PREV_STEPS["Previous 2 steps context"]
    FORMAT_CONTEXT --> CURRENT_STEP["Current step task"]
    FORMAT_CONTEXT --> NEXT_STEPS["Next 2 steps context"]
    
    PREV_STEPS --> AGENT_CREATE["Agent(task, message_context, llm, browser)"]
    CURRENT_STEP --> AGENT_CREATE
    NEXT_STEPS --> AGENT_CREATE
    
    AGENT_CREATE --> AGENT_RUN["agent.run()"]
    AGENT_RUN --> HISTORY["AgentHistoryList"]
```

**Sources:** [workflows/workflow_use/workflow/service.py:149-191](), [workflows/workflow_use/workflow/service.py:193-216]()

### Semantic Step Execution

The `SemanticWorkflowExecutor` provides AI-free execution by mapping visible text to browser elements using the `SemanticExtractor`.

```mermaid
flowchart TD
    SEMANTIC_STEP["WorkflowStep"] --> REFRESH["_refresh_semantic_mapping()"]
    REFRESH --> EXTRACT["SemanticExtractor.extract_semantic_mapping()"]
    EXTRACT --> MAPPING["{'Submit': {'selectors': '#submit-btn'}}"]
    
    MAPPING --> FIND["_find_element_by_text(target_text)"]
    FIND --> SELECTOR["CSS selector"]
    SELECTOR --> EXECUTE["Execute browser action"]
    
    EXECUTE --> VERIFICATION["Verification & retry logic"]
    VERIFICATION --> RESULT["ActionResult"]
```

The semantic executor supports multiple fallback strategies:
1. Direct selector matching (ID/name attributes)
2. Semantic text mapping 
3. Hierarchical context matching
4. Fuzzy text matching with word overlap

**Sources:** [workflows/workflow_use/workflow/semantic_executor.py:25-40](), [workflows/workflow_use/workflow/semantic_executor.py:41-53](), [workflows/workflow_use/workflow/semantic_executor.py:54-174]()

## Error Recovery and Self-Healing

### Verification and Retry Logic

The semantic executor includes sophisticated verification and retry mechanisms to handle dynamic web applications.

```mermaid
flowchart TD
    EXECUTE["Execute step"] --> VALIDATE["Detect form validation errors"]
    VALIDATE --> VERIFY["Verification method"]
    VERIFY --> SUCCESS{"Success?"}
    
    SUCCESS -->|Yes| RESET["Reset failure counters"]
    SUCCESS -->|No| CHECK_RETRIES{"Retries left?"}
    
    CHECK_RETRIES -->|Yes| REFRESH["Refresh semantic mapping"]
    REFRESH --> DELAY["Wait 1 second"]
    DELAY --> EXECUTE
    
    CHECK_RETRIES -->|No| CHECK_LIMITS["Check failure limits"]
    CHECK_LIMITS --> GLOBAL_LIMIT{"Global failures < max?"}
    GLOBAL_LIMIT -->|No| GLOBAL_ERROR["Raise global failure error"]
    GLOBAL_LIMIT -->|Yes| CONSEC_LIMIT{"Consecutive failures < max?"}
    CONSEC_LIMIT -->|No| CONSEC_ERROR["Raise consecutive failure error"]
    CONSEC_LIMIT -->|Yes| INCREMENT["Increment failure counters"]
    INCREMENT --> THROW["Throw exception"]
```

**Sources:** [workflows/workflow_use/workflow/semantic_executor.py:1105-1230]()

### Failure Detection and Recovery

The system tracks multiple types of failures:

| Failure Type | Counter | Purpose |
|-------------|---------|---------|
| `global_failure_count` | Total failures across workflow | Detect systematic issues |
| `consecutive_failures` | Sequential step failures | Detect form/page issues |
| `consecutive_verification_failures` | Sequential verification failures | Detect expectation mismatches |

**Sources:** [workflows/workflow_use/workflow/semantic_executor.py:28-39]()

### Element Resolution Strategies

The semantic executor uses multiple strategies to find elements when the primary selector fails:

1. **Hierarchical selectors**: More specific DOM paths with positional information
2. **Fallback selectors**: Simpler selectors as backup
3. **XPath selectors**: Text-based XPath expressions
4. **Direct attribute matching**: ID and name attribute selectors

**Sources:** [workflows/workflow_use/workflow/semantic_executor.py:304-334](), [workflows/workflow_use/workflow/semantic_executor.py:176-255]()

## Input/Output Processing

### Input Validation

Workflow inputs are validated against the schema definition using dynamically generated Pydantic models.

```mermaid
graph TD
    SCHEMA["WorkflowInputSchemaDefinition"] --> BUILD["_build_input_model()"]
    BUILD --> PYDANTIC["Dynamic Pydantic Model"]
    INPUTS["Runtime inputs"] --> VALIDATE["_validate_inputs()"]
    VALIDATE --> PYDANTIC
    PYDANTIC --> CONTEXT["Context initialization"]
```

**Sources:** [workflows/workflow_use/workflow/service.py:292-303](), [workflows/workflow_use/workflow/service.py:618-678]()

### Structured Output Generation

When an `output_model` is specified, the workflow results are converted to structured output using LLM processing.

```mermaid
flowchart TD
    RESULTS["List[ActionResult | AgentHistoryList]"] --> EXTRACT["Extract content"]
    EXTRACT --> FILTER["Filter extracted_content"]
    FILTER --> COMBINE["Combine all extracted texts"]
    COMBINE --> LLM["LLM with_structured_output()"]
    LLM --> STRUCTURED["Structured output model"]
```

**Sources:** [workflows/workflow_use/workflow/service.py:458-507]()

## Browser Session Management

The workflow execution engine manages browser sessions with automatic lifecycle handling:

- Browser startup before execution
- Session persistence across steps
- Optional cleanup at completion
- Keep-alive settings for agent integration

**Sources:** [workflows/workflow_use/workflow/service.py:69-77](), [workflows/workflow_use/workflow/service.py:576-611]()

---

