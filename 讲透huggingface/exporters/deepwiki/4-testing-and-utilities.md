<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/exporters · page 4 Testing and Utilities · fetched 2026-10-26 -->

# Testing and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/exporters/utils/logging.py](src/exporters/utils/logging.py)
- [tests/test_coreml.py](tests/test_coreml.py)
- [tests/testing_utils.py](tests/testing_utils.py)

</details>



This section provides an overview of the verification mechanisms and shared infrastructure within the `exporters` repository. The codebase relies on a comprehensive integration test suite to ensure model parity between PyTorch and Core ML, supported by utility modules for logging and environment-specific test gating.

## Integration Test Suite

The primary testing logic resides in `tests/test_coreml.py`, which validates the end-to-end export pipeline. It utilizes a centralized registry of models, such as `PYTORCH_EXPORT_MODELS`, to parameterize tests across various architectures and tasks [tests/test_coreml.py:67-83]().

The suite manages complex lifecycles, including:
*   **Model Parameterization**: The `_get_models_to_test` function dynamically generates test cases based on supported features registered in the `FeaturesManager` [tests/test_coreml.py:100-113]().
*   **Export Lifecycle**: The `_coreml_export` method handles the full flow from model loading to `validate_model_outputs`, including specialized handling for Seq2Seq architectures where encoder and decoder are exported separately [tests/test_coreml.py:128-180]().
*   **Configuration Validation**: Dedicated unit tests verify that `CoreMLConfig` correctly calculates flexible shapes and sequence length constraints [tests/test_coreml.py:40-65]().

For a deep dive into how to run, extend, and interpret these tests, see [Integration Test Suite](#4.1).

### Test Suite Relationship
The diagram below illustrates how the test suite interacts with the core library entities to perform validation.

Model Validation Flow
```mermaid
graph TD
    subgraph "Test Space"
        ["test_pytorch_export"] --> ["_coreml_export"]
        ["PYTORCH_EXPORT_MODELS"] --> ["_get_models_to_test"]
        ["_get_models_to_test"] -- "parameterizes" --> ["test_pytorch_export"]
    end

    subgraph "Code Entity Space"
        ["_coreml_export"] -- "calls" --> ["FeaturesManager.get_model_class_for_feature"]
        ["_coreml_export"] -- "calls" --> ["exporters.coreml.export"]
        ["_coreml_export"] -- "calls" --> ["validate_model_outputs"]
    end
```
**Sources:** [tests/test_coreml.py:100-189]()

## Utility Modules

The repository includes shared utilities to maintain consistency with the Hugging Face ecosystem and handle hardware-specific requirements of Core ML.

*   **Logging**: A dedicated logging module in `src/exporters/utils/logging.py` provides standardized verbosity control (e.g., `set_verbosity_info`, `get_logger`), adapted from the `transformers` library to ensure a familiar developer experience [src/exporters/utils/logging.py:110-180]().
*   **Testing Helpers**: Because Core ML validation requires specific environments, `tests/testing_utils.py` provides decorators like `@require_coreml` and `@require_macos` [tests/testing_utils.py:38-43](). These utilities check for the presence of `coremltools` and verify that the host OS is macOS 12.0 or higher [tests/testing_utils.py:21-30]().

For detailed documentation on these modules, see [Utility Modules](#4.2).

### Environment Gating Utilities
The following diagram maps the natural language requirement of "Environment Gating" to the specific code entities responsible for enforcement.

Hardware and Software Requirements Mapping
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Check CoreML Installation"
        "Verify macOS Version"
        "Skip Incompatible Tests"
    end

    subgraph "Code Entity Space"
        "Check CoreML Installation" --> ["is_coreml_available"]
        "Verify macOS Version" --> ["is_macos_available"]
        "Skip Incompatible Tests" --> ["require_coreml"]
        "Skip Incompatible Tests" --> ["require_macos"]
    end

    ["is_coreml_available"] --> ["importlib.util.find_spec"]
    ["is_macos_available"] --> ["coremltools.models.utils._is_macos"]
```
**Sources:** [tests/testing_utils.py:21-43]()

## Summary Table of Key Utilities

| Component | File Path | Primary Responsibility |
| :--- | :--- | :--- |
| **Test Suite** | `tests/test_coreml.py` | Integration tests for all supported model types and tasks [tests/test_coreml.py:1-190](). |
| **Logging** | `src/exporters/utils/logging.py` | Library-wide logging configuration and verbosity levels [src/exporters/utils/logging.py:16-42](). |
| **Environment Check** | `tests/testing_utils.py` | Detection of `coremltools` and macOS system version [tests/testing_utils.py:21-36](). |
| **Test Decorators** | `tests/testing_utils.py` | `unittest` skip decorators for hardware-dependent tests [tests/testing_utils.py:38-43](). |

**Sources:** [tests/test_coreml.py:1-190](), [src/exporters/utils/logging.py:16-42](), [tests/testing_utils.py:21-43]()

---

