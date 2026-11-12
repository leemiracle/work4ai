<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agents-from-scratch · page 7 Evaluation System · fetched 2026-10-26 -->

# Evaluation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [notebooks/evaluation.ipynb](notebooks/evaluation.ipynb)

</details>



## Purpose and Scope

This document describes the evaluation system for the email assistant agent, including test dataset structure, evaluation methodologies, and integration with LangSmith for tracking results. The system supports both traditional pytest-based testing and LangSmith's dataset evaluation API, enabling comprehensive assessment of agent behavior across triage decisions, tool calling accuracy, and response quality.

For detailed information about the pytest testing framework implementation, see [Testing Framework](#7.1). For information about LLM-based evaluation methodologies, see [LLM-as-Judge Evaluation](#7.2).

**Sources:** [README.md:92-166](), [notebooks/evaluation.ipynb:1-584]()

---

## Evaluation Architecture Overview

The evaluation system operates on multiple layers to assess different aspects of the email assistant's behavior. Tests range from unit-level evaluations (triage classification, tool call verification) to end-to-end integration tests (complete email response quality).

### System Components Diagram

```mermaid
graph TB
    subgraph "Test Data Layer"
        EmailDataset["email_dataset.py<br/>Test Cases"]
        EmailInputs["email_inputs<br/>List[str]"]
        TriageOutputs["triage_outputs_list<br/>List[str]"]
        ExpectedTools["expected_tool_calls<br/>List[List[str]]"]
        ResponseCriteria["response_criteria_list<br/>List[str]"]
        
        EmailDataset --> EmailInputs
        EmailDataset --> TriageOutputs
        EmailDataset --> ExpectedTools
        EmailDataset --> ResponseCriteria
    end
    
    subgraph "Test Execution Layer"
        Pytest["pytest Framework<br/>@pytest.mark.langsmith"]
        LSEvaluate["LangSmith evaluate API<br/>client.evaluate()"]
        
        TestFunctions["Test Functions<br/>test_email_dataset_tool_calls<br/>test_response_criteria_evaluation"]
        TargetFunctions["Target Functions<br/>target_email_assistant"]
    end
    
    subgraph "Agent Under Test"
        EmailAssistant["email_assistant.invoke()"]
        TriageRouter["triage_router node"]
        ResponseAgent["response_agent node"]
    end
    
    subgraph "Evaluation Methods"
        DirectEval["Direct Evaluation<br/>assert statements<br/>exact match"]
        LLMJudge["LLM-as-Judge<br/>CriteriaGrade<br/>GPT-4 evaluator"]
    end
    
    subgraph "Results Collection"
        LSProject["LangSmith Project<br/>LANGSMITH_TEST_SUITE"]
        LSDataset["LangSmith Dataset<br/>examples + experiments"]
        Traces["Execution Traces"]
        Metrics["Performance Metrics<br/>latency, tokens, pass/fail"]
    end
    
    EmailInputs --> TestFunctions
    EmailInputs --> TargetFunctions
    TriageOutputs --> DirectEval
    ExpectedTools --> DirectEval
    ResponseCriteria --> LLMJudge
    
    TestFunctions --> Pytest
    TargetFunctions --> LSEvaluate
    
    Pytest --> EmailAssistant
    LSEvaluate --> EmailAssistant
    
    EmailAssistant --> TriageRouter
    EmailAssistant --> ResponseAgent
    
    TriageRouter --> DirectEval
    ResponseAgent --> DirectEval
    ResponseAgent --> LLMJudge
    
    DirectEval --> LSProject
    LLMJudge --> LSProject
    LSEvaluate --> LSDataset
    
    Pytest -.-> Traces
    LSEvaluate -.-> Traces
    
    LSProject --> Metrics
    LSDataset --> Metrics
```

**Sources:** [notebooks/evaluation.ipynb:10-53](), [notebooks/evaluation.ipynb:187-346]()

---

## Test Dataset Structure

The test dataset is defined in `eval/email_dataset.py` and provides comprehensive test cases covering diverse email scenarios. Each test case includes multiple dimensions for evaluation.

### Dataset Components

| Component | Variable Name | Type | Purpose |
|-----------|--------------|------|---------|
| Input Emails | `email_inputs` | `List[str]` | Collection of diverse email examples for testing |
| Triage Classifications | `triage_outputs_list` | `List[str]` | Ground truth for triage decisions (`Respond`, `Notify`, `Ignore`) |
| Expected Tool Calls | `expected_tool_calls` | `List[List[str]]` | Tools that should be invoked for each email |
| Response Criteria | `response_criteria_list` | `List[str]` | Success criteria for evaluating response quality |

**Sources:** [notebooks/evaluation.ipynb:60-93]()

### Dataset Structure Example

```mermaid
graph LR
    subgraph "Test Case 0"
        Input0["email_inputs[0]<br/>'Meeting request email'"]
        Triage0["triage_outputs_list[0]<br/>'Respond'"]
        Tools0["expected_tool_calls[0]<br/>['check_calendar',<br/>'schedule_meeting',<br/>'write_email']"]
        Criteria0["response_criteria_list[0]<br/>'Should check availability<br/>and propose times'"]
    end
    
    subgraph "Test Case 3"
        Input3["email_inputs[3]<br/>'Follow-up question'"]
        Triage3["triage_outputs_list[3]<br/>'Respond'"]
        Tools3["expected_tool_calls[3]<br/>['Question', 'write_email']"]
        Criteria3["response_criteria_list[3]<br/>'Should ask clarifying<br/>question if needed'"]
    end
    
    Input0 --> Triage0
    Triage0 --> Tools0
    Tools0 --> Criteria0
    
    Input3 --> Triage3
    Triage3 --> Tools3
    Tools3 --> Criteria3
```

**Sources:** [notebooks/evaluation.ipynb:74-93]()

### Structured Dataset for LangSmith

For LangSmith evaluate API, the dataset is structured as a list of examples with explicit input/output pairs:

```python
examples_triage = [
    {
        "inputs": {"email_input": email_input_1},
        "outputs": {"classification": triage_output_1},  # Becomes reference_output
    },
    ...
]
```

This structure is used in [notebooks/evaluation.ipynb:196-262]() to create datasets via `client.create_dataset()`.

**Sources:** [notebooks/evaluation.ipynb:196-262]()

---

## Evaluation Approaches

The system supports two complementary evaluation approaches, each with distinct advantages and use cases.

### Comparison of Evaluation Methods

| Aspect | Pytest Integration | LangSmith Datasets |
|--------|-------------------|-------------------|
| **Primary Use Case** | Complex evaluations requiring custom logic per test | Standardized evaluations across shared datasets |
| **Test Definition** | Python test functions with `@pytest.mark.langsmith` | Dataset + target function + evaluators |
| **Collaboration** | Individual developer workflows | Team-based dataset curation |
| **Test Data** | Parametrized via `@pytest.mark.parametrize` | Centralized LangSmith dataset |
| **Execution** | Command-line pytest | `client.evaluate()` API |
| **Best For** | Tool call verification, specific edge cases | Triage classification, standardized metrics |

**Sources:** [notebooks/evaluation.ipynb:39-53]()

### Evaluation Flow Diagram

```mermaid
flowchart TD
    Start["Test Case Definition<br/>email_dataset.py"]
    
    subgraph "Pytest Path"
        PytestTest["Test Function<br/>test_email_dataset_tool_calls"]
        PytestRun["pytest execution<br/>@pytest.mark.langsmith"]
        PytestAgent["Invoke agent<br/>email_assistant.invoke()"]
        PytestExtract["Extract tool calls<br/>extract_tool_calls()"]
        PytestAssert["Assert validation<br/>len(missing_calls) == 0"]
        PytestLog["Log outputs<br/>t.log_outputs()"]
    end
    
    subgraph "LangSmith Path"
        LSDataset["Create dataset<br/>client.create_dataset()"]
        LSTarget["Target function<br/>target_email_assistant()"]
        LSEval["Evaluator function<br/>classification_evaluator()"]
        LSRun["Run evaluation<br/>client.evaluate()"]
        LSCompare["Compare outputs<br/>vs reference_outputs"]
    end
    
    subgraph "Results"
        LSProject["LangSmith Project<br/>Test traces & metrics"]
        LSExperiment["LangSmith Experiment<br/>Dataset results"]
    end
    
    Start --> PytestTest
    Start --> LSDataset
    
    PytestTest --> PytestRun
    PytestRun --> PytestAgent
    PytestAgent --> PytestExtract
    PytestExtract --> PytestAssert
    PytestAssert --> PytestLog
    PytestLog --> LSProject
    
    LSDataset --> LSTarget
    LSTarget --> LSEval
    LSEval --> LSRun
    LSRun --> LSCompare
    LSCompare --> LSExperiment
    
    LSProject --> Metrics["Performance Analysis<br/>Pass rates, latency, tokens"]
    LSExperiment --> Metrics
```

**Sources:** [notebooks/evaluation.ipynb:99-168](), [notebooks/evaluation.ipynb:187-346]()

---

## Integration with LangSmith

All evaluation runs integrate with LangSmith for tracing, metrics collection, and result visualization. This integration provides observability into agent execution and enables performance comparison across implementations.

### LangSmith Integration Components

```mermaid
graph TB
    subgraph "Test Execution"
        PytestTests["Pytest Tests<br/>@pytest.mark.langsmith"]
        EvaluateAPI["evaluate() API<br/>client.evaluate()"]
    end
    
    subgraph "LangSmith Backend"
        TestSuite["Test Suite Project<br/>LANGSMITH_TEST_SUITE env var"]
        Dataset["Dataset Project<br/>dataset_name parameter"]
        
        Traces["Execution Traces<br/>LLM calls, tool invocations"]
        FeedbackStats["Feedback Stats<br/>Pass/fail counts"]
        PerfMetrics["Performance Metrics<br/>latency_p50, latency_p99,<br/>total_tokens"]
    end
    
    subgraph "Results Visualization"
        UI["LangSmith UI<br/>Datasets & Experiments"]
        ProjectView["Project View<br/>Trace inspection"]
        Comparison["Experiment Comparison<br/>Multi-agent analysis"]
    end
    
    PytestTests --> TestSuite
    EvaluateAPI --> Dataset
    
    TestSuite --> Traces
    Dataset --> Traces
    
    Traces --> FeedbackStats
    Traces --> PerfMetrics
    
    TestSuite --> UI
    Dataset --> UI
    
    UI --> ProjectView
    UI --> Comparison
    
    FeedbackStats --> Comparison
    PerfMetrics --> Comparison
```

**Sources:** [notebooks/evaluation.ipynb:160-180](), [notebooks/evaluation.ipynb:523-547]()

### Environment Configuration

Tests are configured via environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `LANGSMITH_TEST_SUITE` | Project name for pytest results | `"Email assistant: Test Tools For Interrupt"` |
| `LANGSMITH_EXPERIMENT` | Experiment identifier | `"email_assistant"` |
| `LANGSMITH_PROJECT` | Default project for traces | `"interrupt-workshop"` |
| `LANGSMITH_API_KEY` | Authentication | Required |
| `LANGSMITH_TRACING` | Enable tracing | `"true"` |

**Sources:** [README.md:24-45](), [notebooks/evaluation.ipynb:160-180]()

---

## Evaluation Metrics and Results

The evaluation system collects multiple types of metrics to assess agent performance comprehensively.

### Metrics Collection

```mermaid
graph TB
    subgraph "Test Execution"
        AgentRun["Agent Execution<br/>email_assistant.invoke()"]
    end
    
    subgraph "Captured Metrics"
        Correctness["Correctness Metrics<br/>Pass/fail assertions"]
        Performance["Performance Metrics<br/>Latency, token usage"]
        Behavior["Behavior Metrics<br/>Tool calls, classifications"]
        Quality["Quality Metrics<br/>LLM-as-judge scores"]
    end
    
    subgraph "Metric Details"
        PassFail["Pass/Fail<br/>assert statements<br/>evaluator return values"]
        LatencyP50["latency_p50<br/>Median response time"]
        LatencyP99["latency_p99<br/>99th percentile latency"]
        TotalTokens["total_tokens<br/>Cumulative token usage"]
        ExtractedTools["extracted_tool_calls<br/>List of invoked tools"]
        MissingCalls["missing_calls<br/>Expected but not invoked"]
        CriteriaGrade["CriteriaGrade<br/>grade: bool<br/>justification: str"]
    end
    
    AgentRun --> Correctness
    AgentRun --> Performance
    AgentRun --> Behavior
    AgentRun --> Quality
    
    Correctness --> PassFail
    Performance --> LatencyP50
    Performance --> LatencyP99
    Performance --> TotalTokens
    Behavior --> ExtractedTools
    Behavior --> MissingCalls
    Quality --> CriteriaGrade
```

**Sources:** [notebooks/evaluation.ipynb:128-153](), [notebooks/evaluation.ipynb:529-547]()

### Results Access via API

Results can be programmatically accessed using the LangSmith client:

```python
# Access experiment results
experiment_results = client.read_project(
    project_name=experiment_name, 
    include_stats=True
)

# Available metrics:
# - experiment_results.latency_p50
# - experiment_results.latency_p99
# - experiment_results.total_tokens
# - experiment_results.feedback_stats
```

This code pattern is demonstrated in [notebooks/evaluation.ipynb:529-547]().

**Sources:** [notebooks/evaluation.ipynb:523-547]()

---

## Running Evaluations

### Running Tests with Pytest

Tests can be executed via the command line with environment variables:

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test suite
LANGSMITH_TEST_SUITE='Email assistant: Test Tools' pytest notebooks/test_tools.py

# Run response evaluation
LANGSMITH_TEST_SUITE='Email assistant: Test Full Response' \
LANGSMITH_EXPERIMENT='email_assistant' \
pytest tests/test_response.py --agent-module email_assistant
```

**Sources:** [README.md:132-166](), [notebooks/evaluation.ipynb:164-168]()

### Running Tests with LangSmith evaluate API

Dataset-based evaluation uses the LangSmith client:

```python
experiment_results = client.evaluate(
    target_email_assistant,           # Target function
    data=dataset_name,                # Dataset name
    evaluators=[classification_evaluator],  # List of evaluators
    experiment_prefix="E-mail assistant workflow",
    max_concurrency=2,
)
```

This pattern is shown in [notebooks/evaluation.ipynb:325-346]().

**Sources:** [notebooks/evaluation.ipynb:317-346]()

---

## Test Case Categories

The evaluation system tests multiple aspects of agent behavior through different test categories:

| Test Category | Evaluated Component | Key Assertions | Files |
|--------------|-------------------|----------------|-------|
| **Triage Classification** | `triage_router` node | Classification matches ground truth | `notebooks/evaluation.ipynb` |
| **Tool Call Verification** | Tool execution | Expected tools invoked, no missing calls | `notebooks/test_tools.py`, `tests/test_response.py` |
| **Response Quality** | Complete agent output | LLM-as-judge evaluation against criteria | `tests/test_response.py` |
| **Notebook Validation** | Educational materials | All notebooks execute without errors | `tests/test_notebooks.py` |

**Sources:** [README.md:132-166](), [notebooks/evaluation.ipynb:60-72]()

---

## Key Functions and Classes

### Test Data Access

- `email_inputs`: List of test email strings from [eval/email_dataset.py]()
- `triage_outputs_list`: Ground truth classifications from [eval/email_dataset.py]()
- `expected_tool_calls`: Expected tool invocations from [eval/email_dataset.py]()
- `response_criteria_list`: Success criteria strings from [eval/email_dataset.py]()
- `examples_triage`: Structured dataset for LangSmith from [eval/email_dataset.py]()

### Utility Functions

- `extract_tool_calls(messages)`: Extracts tool call names from message list in [email_assistant/utils.py]()
- `format_messages_string(messages)`: Formats messages for display/evaluation in [email_assistant/utils.py]()

### Evaluation Functions

- `classification_evaluator(outputs, reference_outputs)`: Exact match evaluator in [notebooks/evaluation.ipynb:307-310]()
- `target_email_assistant(inputs)`: Target function wrapper in [notebooks/evaluation.ipynb:279-283]()

### LangSmith Client Operations

- `client.create_dataset()`: Creates evaluation dataset in [notebooks/evaluation.ipynb:216-222]()
- `client.evaluate()`: Runs evaluation experiment in [notebooks/evaluation.ipynb:334-346]()
- `client.read_project()`: Retrieves experiment results in [notebooks/evaluation.ipynb:542]()

**Sources:** [notebooks/evaluation.ipynb:74-153](), [notebooks/evaluation.ipynb:196-283](), [notebooks/evaluation.ipynb:307-346]()

---

## Further Reading

For detailed information about specific evaluation subsystems:

- **[Testing Framework](#7.1)**: Pytest integration, parametrization, tool call extraction, and logging to LangSmith projects
- **[LLM-as-Judge Evaluation](#7.2)**: CriteriaGrade schema, response quality assessment, and GPT-4 evaluator configuration

---

