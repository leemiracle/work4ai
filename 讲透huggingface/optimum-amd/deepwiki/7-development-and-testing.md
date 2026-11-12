<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-amd · page 7 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test_ryzenai_modeling.yaml](.github/workflows/test_ryzenai_modeling.yaml)
- [.github/workflows/test_ryzenai_nightly.yaml](.github/workflows/test_ryzenai_nightly.yaml)
- [.github/workflows/test_ryzenai_prequantized_model.yaml](.github/workflows/test_ryzenai_prequantized_model.yaml)
- [conftest.py](conftest.py)
- [tests/ryzenai/test_modeling.py](tests/ryzenai/test_modeling.py)
- [utils/ryzenai/notification_service.py](utils/ryzenai/notification_service.py)

</details>



This document covers the comprehensive development and testing infrastructure for optimum-amd, including the testing framework, CI/CD pipelines, performance validation systems, and automated reporting mechanisms. The focus is on the technical implementation details of how tests are organized, executed, and validated across different AMD hardware targets.

For information about specific testing of individual components, see [Testing Framework](#7.1), [CI/CD Workflows](#7.2), [Docker Environments](#7.3), and [Documentation System](#7.4).

## Testing Framework Architecture

The testing infrastructure is built around pytest with custom mixins and utilities specifically designed for AMD hardware validation. The framework supports multiple test categories, performance baseline validation, and automated artifact collection.

```mermaid
graph TD
    subgraph "Test Organization"
        TestFiles["tests/ryzenai/test_modeling.py<br/>tests/ryzenai/test_quantization.py"]
        ConfTest["conftest.py<br/>pytest configuration"]
        TestUtils["tests/ryzenai/testing_utils.py<br/>RyzenAITestCaseMixin"]
    end
    
    subgraph "Test Categories"
        PreQuantTest["@pytest.mark.prequantized_model_test<br/>Pre-quantized model validation"]
        QuantTest["@pytest.mark.quant_test<br/>Quantization workflow tests"]
        SlowTest["@slow decorator<br/>Long-running integration tests"]
    end
    
    subgraph "Test Execution"
        ParamTest["@parameterized.expand<br/>Model-specific test cases"]
        BaselineValidation["operators_baseline.json<br/>Performance regression detection"]
        ArtifactCollection["Test artifacts and logs<br/>Failure reporting"]
    end
    
    subgraph "Hardware Validation"
        IPUTests["VitisAIExecutionProvider<br/>RyzenAI NPU validation"]
        CPUTests["CPUExecutionProvider<br/>Baseline comparison"]
        OpValidation["DPU/CPU operator counting<br/>Performance metrics"]
    end
    
    TestFiles --> TestUtils
    ConfTest --> TestFiles
    TestUtils --> PreQuantTest
    TestUtils --> QuantTest
    ParamTest --> IPUTests
    ParamTest --> CPUTests
    BaselineValidation --> OpValidation
    IPUTests --> ArtifactCollection
    CPUTests --> ArtifactCollection
    
    style TestUtils fill:#e1f5fe
    style BaselineValidation fill:#fff3e0
    style ArtifactCollection fill:#f3e5f5
```

**Sources:** [tests/ryzenai/test_modeling.py:1-280](), [conftest.py:1-17]()

## Test Categories and Execution Patterns

The testing system uses pytest markers to organize tests into distinct categories, each targeting different aspects of the AMD hardware integration.

| Test Marker | Purpose | Execution Context | Validation Method |
|-------------|---------|-------------------|-------------------|
| `prequantized_model_test` | Validates pre-quantized ONNX models | RyzenAI NPU vs CPU comparison | Numerical accuracy + operator baselines |
| `quant_test` | Tests quantization workflows | End-to-end quantization pipeline | Model output validation |
| `slow` | Long-running integration tests | Pipeline interface testing | Functional correctness |

```mermaid
graph LR
    subgraph "Test Execution Flow"
        A["load_model_and_input()<br/>Model preparation"]
        B["prepare_outputs()<br/>IPU vs CPU execution"]
        C["Numerical Comparison<br/>np.allclose(atol=1e-4)"]
        D["Operator Validation<br/>get_ops() vs get_baseline_ops()"]
        E["Artifact Collection<br/>gc.collect()"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    subgraph "Model Classes Tested"
        F["RyzenAIModelForImageClassification"]
        G["RyzenAIModelForObjectDetection"]
        H["RyzenAIModelForSemanticSegmentation"]
        I["RyzenAIModelForImageToImage"]
        J["RyzenAIModelForCustomTasks"]
    end
    
    B --> F
    B --> G
    B --> H
    B --> I
    B --> J
    
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

**Sources:** [tests/ryzenai/test_modeling.py:46-61](), [tests/ryzenai/test_modeling.py:100-114]()

## CI/CD Pipeline Architecture

The continuous integration system uses GitHub Actions with specialized workflows for different testing scenarios, including pull request validation, nightly regression testing, and performance monitoring.

```mermaid
graph TD
    subgraph "GitHub Actions Workflows"
        A["test_ryzenai_modeling.yaml<br/>PR and push triggers"]
        B["test_ryzenai_prequantized_model.yaml<br/>Pre-quantized validation"]
        C["test_ryzenai_nightly.yaml<br/>Scheduled regression tests"]
    end
    
    subgraph "Workflow Execution"
        D["huggingface/hf-workflows/.github/workflows/ryzenai_ci.yaml<br/>Shared CI template"]
        E["pytest_marker parameter<br/>Test category selection"]
        F["test_file parameter<br/>Specific test execution"]
    end
    
    subgraph "Nightly Testing Components"
        G["run_tests_prequantized_models<br/>Model validation job"]
        H["run_tests_quantization<br/>Quantization workflow job"]
        I["send_results<br/>Notification job"]
    end
    
    subgraph "Artifacts and Reporting"
        J["Test artifacts collection<br/>./reports/ directory"]
        K["notification_service.py<br/>Slack integration"]
        L["Failure table artifacts<br/>prev_ci_results"]
    end
    
    A --> D
    B --> D
    C --> G
    C --> H
    D --> E
    D --> F
    
    G --> J
    H --> J
    I --> K
    K --> L
    
    style D fill:#e1f5fe
    style K fill:#f3e5f5
    style L fill:#fff3e0
```

**Sources:** [.github/workflows/test_ryzenai_modeling.yaml:1-30](), [.github/workflows/test_ryzenai_nightly.yaml:1-65]()

## Performance Baseline Validation System

The testing framework includes a sophisticated baseline validation system that tracks operator distribution and performance metrics to detect regressions in model optimization.

```mermaid
graph TD
    subgraph "Baseline System Components"
        A["operators_baseline.json<br/>Performance baselines"]
        B["get_baseline_ops()<br/>Baseline retrieval"]
        C["get_ops()<br/>Current metrics collection"]
        D["Operator Comparison<br/>baseline_ops vs current_ops"]
    end
    
    subgraph "Operator Categories"
        E["all: Total operators"]
        F["dpu: DPU-accelerated ops"]
        G["cpu: CPU fallback ops"]
    end
    
    subgraph "Validation Logic"
        H["assertEqual(baseline_ops['all'], current_ops['all'])<br/>Total operator validation"]
        I["assertEqual(baseline_ops['dpu'], current_ops['dpu'])<br/>DPU operator validation"]
        J["Regression Detection<br/>Performance degradation alerts"]
    end
    
    A --> B
    C --> D
    B --> D
    D --> H
    D --> I
    
    E --> H
    F --> I
    G --> D
    
    H --> J
    I --> J
    
    style A fill:#fff3e0
    style J fill:#f3e5f5
```

**Sources:** [tests/ryzenai/test_modeling.py:109-114](), [utils/ryzenai/notification_service.py:222-226]()

## Notification and Reporting System

The automated notification system provides comprehensive test result reporting through Slack integration, including detailed failure analysis and performance regression tracking.

```mermaid
graph TD
    subgraph "Notification Service Components"
        A["notification_service.py<br/>Main orchestration"]
        B["Message class<br/>Slack payload generation"]
        C["WebClient<br/>slack_sdk integration"]
    end
    
    subgraph "Data Processing"
        D["retrieve_available_artifacts()<br/>Test artifact discovery"]
        E["handle_test_results()<br/>Parse test statistics"]
        F["handle_stacktraces()<br/>Error trace processing"]
        G["infer_model_id()<br/>Model identification"]
    end
    
    subgraph "Report Generation"
        H["category_failures property<br/>Summary statistics"]
        I["model_failures property<br/>Detailed failure analysis"]
        J["extract_operator_values()<br/>Performance regression data"]
        K["prepare_model_failure_sections()<br/>Slack block formatting"]
    end
    
    subgraph "Slack Integration"
        L["chat_postMessage()<br/>Main notification"]
        M["post_reply()<br/>Detailed failure threads"]
        N["CI_SLACK_BOT_TOKEN<br/>Authentication"]
        O["CI_SLACK_CHANNEL_ID<br/>Target channel"]
    end
    
    A --> B
    A --> D
    D --> E
    D --> F
    E --> G
    
    B --> H
    B --> I
    I --> J
    J --> K
    
    B --> L
    B --> M
    C --> L
    C --> M
    
    N --> C
    O --> C
    
    style B fill:#e1f5fe
    style J fill:#fff3e0
    style L fill:#f3e5f5
```

**Sources:** [utils/ryzenai/notification_service.py:126-506](), [.github/workflows/test_ryzenai_nightly.yaml:44-56]()

## Test Execution Environment Configuration

The testing system includes environment-specific configurations and utilities that ensure consistent behavior across different execution contexts.

```mermaid
graph LR
    subgraph "Environment Variables"
        A["XLNX_ENABLE_CACHE=0<br/>Disable caching"]
        B["XLNX_USE_SHARED_CONTEXT=1<br/>Shared context mode"]
        C["DEFAULT_CACHE_DIR<br/>Artifact storage"]
    end
    
    subgraph "Test Utilities"
        D["RyzenAITestCaseMixin<br/>Common test functionality"]
        E["DummyInputGenerator<br/>Test input generation"]
        F["load_model_and_input()<br/>Model loading helper"]
    end
    
    subgraph "Model Validation"
        G["assertIsInstance(model.model, onnxruntime.InferenceSession)"]
        H["assertListEqual(model.providers, ['VitisAIExecutionProvider', 'CPUExecutionProvider'])"]
        I["assertTrue(np.allclose(outputs_ipu.logits, outputs_cpu.logits, atol=1e-4))"]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> F
    E --> F
    F --> G
    F --> H
    F --> I
    
    style D fill:#e1f5fe
    style I fill:#e8f5e8
```

**Sources:** [tests/ryzenai/test_modeling.py:69-75](), [tests/ryzenai/test_modeling.py:46-61](), [tests/ryzenai/test_modeling.py:107-108]()

---

