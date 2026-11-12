<!-- source: DeepWiki mcp.deepwiki.com · repo SWE-agent/SWE-agent · page 9 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/_footer.md](docs/_footer.md)
- [docs/assets/navigation_cards.css](docs/assets/navigation_cards.css)
- [docs/dev/contribute.md](docs/dev/contribute.md)
- [docs/dev/formatting_conflicts.md](docs/dev/formatting_conflicts.md)
- [docs/installation/index.md](docs/installation/index.md)
- [docs/usage/index.md](docs/usage/index.md)
- [mlc_config.json](mlc_config.json)

</details>



This document covers the development workflow, testing infrastructure, and quality assurance systems for the SWE-agent codebase. It provides an overview of the testing framework, evaluation systems, and development tools that ensure code quality and system reliability.

For detailed information about specific testing approaches, see [Testing Framework](#9.1). For documentation generation and maintenance, see [Documentation System](#9.2). For continuous integration and deployment processes, see [CI/CD and Deployment](#9.3).

## Overview

The SWE-agent development ecosystem consists of three main components:

1. **Testing Framework** - Comprehensive test suite using pytest with specialized fixtures and mock systems
2. **Evaluation System** - Automated evaluation against SWE-bench datasets with continuous submission capabilities  
3. **Quality Assurance** - Pre-commit hooks, linting, type checking, and CI/CD pipeline integration

## Testing Architecture

The testing system is built around pytest and provides specialized fixtures for testing agent behavior, environment interactions, and tool parsing.

```mermaid
graph TB
    subgraph "Test Infrastructure"
        PyTest["pytest Framework"]
        Fixtures["Test Fixtures"]
        Mocks["Mock Systems"]
        Configs["Test Configurations"]
    end
    
    subgraph "Agent Testing"
        AgentTests["test_agent.py"]
        AgentFixtures["Agent Fixtures"]
        MockModels["Mock Models"]
        ParseTests["Parser Tests"]
    end
    
    subgraph "Execution Testing"
        SingleTests["test_run_single.py"]
        BatchTests["test_run_batch.py"]
        InstanceTests["test_batch_instance.py"]
        IntegrationTests["Integration Tests"]
    end
    
    subgraph "Evaluation System"
        SWEBenchHook["SweBenchEvaluate"]
        EvalPipeline["Evaluation Pipeline"]
        ResultMerger["Result Consolidation"]
        ContinuousEval["Continuous Evaluation"]
    end
    
    PyTest --> AgentTests
    PyTest --> SingleTests
    PyTest --> BatchTests
    
    Fixtures --> AgentFixtures
    Fixtures --> MockModels
    
    AgentTests --> ParseTests
    SingleTests --> IntegrationTests
    BatchTests --> InstanceTests
    
    SWEBenchHook --> EvalPipeline
    EvalPipeline --> ResultMerger
    ResultMerger --> ContinuousEval
    
    MockModels --> AgentTests
    Configs --> AgentTests
```

**Sources:** [tests/test_agent.py:1-263](), [tests/test_run_single.py:1-126](), [tests/test_run_batch.py:1-111](), [tests/test_batch_instance.py:1-44]()

## Test Fixture System

The testing framework provides specialized fixtures for different testing scenarios:

| Fixture Type | Purpose | Key Classes |
|-------------|---------|-------------|
| Agent Configurations | Different parsing and model configurations | `DefaultAgentConfig`, `InstantEmptySubmitModelConfig` |
| Mock Models | Predictable model responses for testing | `PredeterminedTestModel`, `InstantEmptySubmitModelConfig` |
| Parser Fixtures | Testing different command parsing strategies | `Identity`, `ThoughtActionParser`, `FunctionCallingParser` |
| Environment Fixtures | Controlled environment for testing | `SWEEnv`, `DummyRuntime` |

```mermaid
graph LR
    subgraph "Configuration Fixtures"
        IdentityConfig["identity_agent_config"]
        ThoughtActionConfig["thought_action_agent_config"] 
        FunctionCallingConfig["function_calling_agent_config"]
        DefaultConfig["default_agent_config"]
    end
    
    subgraph "Agent Fixtures"
        TestAgent["test_agent"]
        DefaultAgent["default_agent"]
        ThoughtActionAgent["thought_action_agent"]
        FunctionCallingAgent["function_calling_agent"]
    end
    
    subgraph "Mock Systems"
        PredeterminedModel["PredeterminedTestModel"]
        InstantSubmit["InstantEmptySubmitModelConfig"]
        DummyEnv["dummy_env"]
        MockRuntime["DummyRuntime"]
    end
    
    IdentityConfig --> TestAgent
    ThoughtActionConfig --> ThoughtActionAgent
    FunctionCallingConfig --> FunctionCallingAgent
    DefaultConfig --> DefaultAgent
    
    TestAgent --> PredeterminedModel
    DefaultAgent --> InstantSubmit
    
    TestAgent --> DummyEnv
    DummyEnv --> MockRuntime
```

**Sources:** [tests/test_agent.py:20-78](), [tests/test_run_single.py:32-44]()

## Evaluation and Benchmarking

The `SweBenchEvaluate` hook provides automated evaluation against SWE-bench datasets with support for continuous submission and result tracking.

### Key Components

- **`SweBenchEvaluate`** - Main evaluation hook class
- **Continuous Evaluation** - Automatic submission at configurable intervals
- **Result Consolidation** - Merging predictions from multiple runs
- **SB-CLI Integration** - Direct integration with SWE-bench evaluation CLI

```mermaid
sequenceDiagram
    participant RunBatch as "RunBatch Orchestrator"
    participant Hook as "SweBenchEvaluate Hook"
    participant Merger as "merge_predictions"
    participant SBCLI as "sb-cli submit"
    participant Report as "Results Report"
    
    RunBatch->>Hook: "on_instance_completed(result)"
    Hook->>Hook: "Check evaluation_interval"
    
    alt "Continuous evaluation triggered"
        Hook->>Merger: "merge_predictions(output_dir, tmppreds.json)"
        Hook->>SBCLI: "Popen(sb-cli submit tmppreds.json)"
        Note over SBCLI: "Background submission"
    end
    
    RunBatch->>Hook: "on_end()"
    Hook->>SBCLI: "subprocess.run(sb-cli submit preds.json)"
    SBCLI->>Report: "Generate results.json"
    Hook->>Hook: "move_sb_cli_report()"
```

**Sources:** [sweagent/run/hooks/swe_bench_evaluate.py:1-114]()

## Test Categories and Exit Conditions

The testing framework validates various agent behaviors and exit conditions:

### Exit Status Testing

| Test Type | Purpose | Expected Behavior |
|-----------|---------|-------------------|
| `test_exit_cost` | Cost limit reached | `exit_cost` status |
| `test_exit_context` | Context limit exceeded | `exit_context` status |
| `test_exit_model_error` | Model runtime errors | `exit_environment_error` status |
| `test_exit_format` | Invalid command format | `exit_format` status |
| `test_exit_blocklist` | Blocked commands used | `exit_format` status |

### Agent Behavior Testing

- **Step-by-step execution** - Validates agent history and message handling
- **Tool calling** - Tests function calling parser with structured responses
- **Submission handling** - Tests automatic submission detection and processing
- **Error handling** - Validates graceful error recovery and reporting

**Sources:** [tests/test_agent.py:80-263]()

## Integration Testing

### Single Run Testing

Tests individual agent execution with various configurations:
- Repository sources (local, GitHub)
- Problem statement sources (GitHub issues, local files, text)
- Output format validation (trajectory, predictions, patches)

### Batch Processing Testing

Validates batch execution capabilities:
- Instance loading from different sources
- Parallel execution coordination
- Progress tracking and reporting
- Exception handling and recovery

**Sources:** [tests/test_run_single.py:82-126](), [tests/test_run_batch.py:8-89]()

## Mock and Test Infrastructure

### Mock Model System

The `PredeterminedTestModel` provides controlled responses for testing:
- Predictable command sequences
- Error condition simulation
- Cost and context limit testing

### Environment Mocking

- **`DummyRuntime`** - Simulated command execution
- **`RuntimeRaisesFirst`** - Error condition testing
- **Mock state injection** - Controlled environment state

```mermaid
graph TB
    subgraph "Mock Infrastructure"
        PredeterminedModel["PredeterminedTestModel"]
        DummyRuntime["DummyRuntime"]
        MockState["Mock State Injection"]
    end
    
    subgraph "Test Scenarios"
        ExitTests["Exit Condition Tests"]
        ParserTests["Parser Function Tests"]
        SubmissionTests["Submission Tests"]
        ErrorTests["Error Handling Tests"]
    end
    
    subgraph "Validation"
        TrajectoryCheck["Trajectory Validation"]
        MessageCheck["Message History Check"]
        StatusCheck["Exit Status Check"]
        OutputCheck["Output Format Check"]
    end
    
    PredeterminedModel --> ExitTests
    DummyRuntime --> ParserTests
    MockState --> SubmissionTests
    
    ExitTests --> StatusCheck
    ParserTests --> TrajectoryCheck
    SubmissionTests --> MessageCheck
    ErrorTests --> OutputCheck
```

**Sources:** [tests/test_agent.py:130-263]()

---

