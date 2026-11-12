<!-- source: DeepWiki mcp.deepwiki.com · repo onnx/onnx · page 5 Testing ONNX Models and Backends · fetched 2026-10-21 -->

# Testing ONNX Models and Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/Changelog.md](docs/Changelog.md)
- [docs/Operators.md](docs/Operators.md)
- [docs/TestCoverage-ml.md](docs/TestCoverage-ml.md)
- [docs/TestCoverage.md](docs/TestCoverage.md)
- [onnx/backend/base.py](onnx/backend/base.py)
- [onnx/backend/test/case/node/cast.py](onnx/backend/test/case/node/cast.py)
- [onnx/backend/test/case/node/castlike.py](onnx/backend/test/case/node/castlike.py)
- [onnx/backend/test/report/__init__.py](onnx/backend/test/report/__init__.py)
- [onnx/backend/test/report/coverage.py](onnx/backend/test/report/coverage.py)
- [onnx/backend/test/runner/__init__.py](onnx/backend/test/runner/__init__.py)
- [onnx/backend/test/stat_coverage.py](onnx/backend/test/stat_coverage.py)
- [onnx/defs/controlflow/defs.cc](onnx/defs/controlflow/defs.cc)
- [onnx/defs/controlflow/old.cc](onnx/defs/controlflow/old.cc)
- [onnx/defs/math/defs.cc](onnx/defs/math/defs.cc)
- [onnx/defs/math/old.cc](onnx/defs/math/old.cc)
- [onnx/defs/nn/defs.cc](onnx/defs/nn/defs.cc)
- [onnx/defs/nn/old.cc](onnx/defs/nn/old.cc)
- [onnx/defs/operator_sets.h](onnx/defs/operator_sets.h)
- [onnx/defs/reduction/defs.cc](onnx/defs/reduction/defs.cc)
- [onnx/defs/rnn/defs.cc](onnx/defs/rnn/defs.cc)
- [onnx/defs/rnn/old.cc](onnx/defs/rnn/old.cc)
- [onnx/defs/tensor/defs.cc](onnx/defs/tensor/defs.cc)
- [onnx/defs/tensor/old.cc](onnx/defs/tensor/old.cc)
- [onnx/test/shape_inference_test.py](onnx/test/shape_inference_test.py)
- [onnx/test/test_backend_test.py](onnx/test/test_backend_test.py)

</details>



This page describes the testing infrastructure for ONNX models and backend implementations. It explains how to run tests against ONNX backends, how to implement a backend that can run these tests, and how to create new tests for ONNX operators and models.

For details on the reference implementation of ONNX operators, see [Reference Evaluator](#5.3).

## Overview

ONNX provides a comprehensive testing framework to ensure consistency and compatibility across different backend implementations. This framework includes:

1. Node tests for verifying individual operator implementations
2. Model tests for validating end-to-end model execution
3. A backend testing system to verify that implementations correctly follow the ONNX specification

```mermaid
flowchart TD
    subgraph "ONNX Backend Test Framework"
        BackendTest["BackendTest class"] --> Runner["Runner"]
        Runner --> TestCases["Test Cases"]
        TestCases --> NodeTests["Node Tests"]
        TestCases --> ModelTests["Model Tests"]
        NodeTests --> expect["expect() function"]
        ModelTests --> download["Download model"]
    end

    subgraph "Backend Implementation"
        Backend["Backend (abstract)"] --> BackendRep["BackendRep"]
        Backend --> is_compatible["is_compatible()"]
        Backend --> prepare["prepare()"]
        Backend --> run_model["run_model()"]
        Backend --> run_node["run_node()"]
    end

    subgraph "Test Execution"
        Runner --> BackendImpl["Backend Implementation"]
        BackendImpl --> TestExecution["Test Execution"]
        TestExecution --> ResultComparison["Result Comparison"]
        ResultComparison --> TestReport["Test Report"]
    end

    Backend -.-> BackendImpl
```

Sources: [onnx/backend/test/runner/__init__.py:60-73](). [onnx/backend/base.py:69-79]().

## Backend Testing Architecture

The ONNX backend testing system centers around the abstract `Backend` class in [onnx/backend/base.py:58-148]() and the `Runner` class in [onnx/backend/test/runner/__init__.py:61-532]() that orchestrates test execution.

### Backend Abstract Class Structure

```mermaid
classDiagram
    class Backend {
        <<abstract>>
        +prepare(model, device, **kwargs)$ BackendRep
        +run_model(model, inputs, device, **kwargs)$ tuple
        +run_node(node, inputs, device, **kwargs)$ tuple
        +supports_device(device)$ bool
        +is_compatible(model, device, **kwargs)$ bool
    }
    
    class BackendRep {
        <<abstract>>
        +run(inputs, **kwargs) namedtupledict
    }
    
    class Device {
        +type DeviceType
        +device_id int
        +__init__(device)
    }
    
    class DeviceType {
        +CPU _Type
        +CUDA _Type
    }
    
    Backend --> BackendRep : creates via prepare()
    Backend ..> Device : uses
    Device --> DeviceType : contains
```

### Runner and Test Organization

```mermaid
classDiagram
    class Runner {
        -backend type[Backend]
        -_parent_module str
        -_include_patterns set[Pattern]
        -_exclude_patterns set[Pattern]
        -_xfail_patterns set[Pattern]
        -_test_items dict[str, dict[str, TestItem]]
        -_test_kwargs dict
        +__init__(backend, parent_module, test_kwargs)
        +include(pattern) Runner
        +exclude(pattern) Runner
        +xfail(pattern) Runner
        +enable_report() Runner
        +_add_model_test(model_test, kind)
        +test_cases dict
        +test_suite unittest.TestSuite
        +tests list
    }
    
    class TestItem {
        +func Callable
        +proto ModelProto
        +name str
    }
    
    class TestCase {
        +model_name str
        +model ModelProto
        +data_sets list
        +kind str
        +rtol float
        +atol float
    }
    
    Runner --> TestItem : organizes
    Runner --> Backend : uses
    TestItem --> TestCase : references
```

Sources: [onnx/backend/base.py:19-148](), [onnx/backend/test/runner/__init__.py:61-532](), [onnx/backend/test/runner/item.py:1-20]().

## Implementing a Backend

To create an ONNX backend that can be tested with the ONNX test framework, you must implement the `Backend` interface. Here's the minimal requirements:

1. Implement the `prepare()` method, which converts an ONNX model into a form that can be executed.
2. Implement the `BackendRep` class with a `run()` method that executes the prepared model.

### Basic Backend Implementation

The basic structure of a backend implementation includes:

```python
class MyBackendRep(onnx.backend.base.BackendRep):
    def __init__(self, model):
        self.model = model  # Store the prepared model
        
    def run(self, inputs, **kwargs):
        # Execute the model with the given inputs
        # Return a tuple of output values
        return outputs

class MyBackend(onnx.backend.base.Backend):
    @classmethod
    def prepare(cls, model, device='CPU', **kwargs):
        # Convert the ONNX model to your backend's format
        prepared_model = convert_model(model)
        return MyBackendRep(prepared_model)
        
    @classmethod
    def supports_device(cls, device):
        # Report which devices your backend supports
        return device == 'CPU'  # For example
```

For a real example, see the `ReferenceEvaluatorBackend` implementation:

Sources: [onnx/test/test_backend_reference.py:26-90]().

## Running Backend Tests

The `BackendTest` class manages the test cases and handles their execution against a backend implementation:

```python
import onnx.backend.test

# Create a BackendTest instance with your backend
backend_test = onnx.backend.test.BackendTest(MyBackend, __name__)

# You can customize which tests to run
backend_test.include('test_relu')  # Only run tests matching this pattern
backend_test.exclude('test_conv')  # Skip tests matching this pattern

# Update the global namespace with the test cases
globals().update(backend_test.test_cases)
```

Sources: [onnx/test/test_backend_reference.py:93-105](). [onnx/test/test_backend_test.py:115-127]().

## Test Types and Data Management

The ONNX test framework organizes tests into multiple categories, each serving different validation purposes.

### Test Categories

```mermaid
flowchart LR
    LoadTests["load_model_tests(kind)"] --> NodeTests["kind='node'"]
    LoadTests --> RealTests["kind='real'"]
    LoadTests --> SimpleTests["kind='simple'"]
    LoadTests --> PyTorchConv["kind='pytorch-converted'"]
    LoadTests --> PyTorchOp["kind='pytorch-operator'"]
    
    NodeTests --> NodeDesc["Individual operator tests<br/>~150+ operators<br/>Inline test data"]
    RealTests --> RealDesc["Production models<br/>ResNet, BERT, etc.<br/>External data"]
    SimpleTests --> SimpleDesc["Basic model patterns<br/>Small graph structures<br/>Local test data"]
    PyTorchConv --> PyTorchConvDesc["PyTorch exported models<br/>Validation against PyTorch"]
    PyTorchOp --> PyTorchOpDesc["PyTorch operator tests<br/>Cross-framework checks"]
```

### Node Tests

Node tests are defined using the `expect()` function in [onnx/backend/test/case/node/__init__.py:240-380](). Each test creates a minimal ONNX graph containing a single operator:

```python
def expect(
    node: onnx.NodeProto,
    inputs: Sequence[np.ndarray],
    outputs: Sequence[np.ndarray],
    name: str,
    **kwargs
) -> None:
    # Creates test case files in test_data/node/
    # Saves input_*.pb and output_*.pb files
```

The test data is stored in the `test_data/node/test_<name>/` directory structure with:
- `model.onnx` - The operator wrapped in a minimal graph
- `test_data_set_0/input_*.pb` - Input tensors as protobuf
- `test_data_set_0/output_*.pb` - Expected output tensors

### Model Tests

Model tests validate end-to-end execution. The `load_model_tests()` function in [onnx/backend/test/loader.py:1-250]() discovers tests from:

1. **Local test data** - Stored in `test_data/` directories
2. **Remote models** - Downloaded from URLs (with retry logic in [onnx/backend/test/runner/__init__.py:40-58]())
3. **Generated data** - Created on-the-fly for parameterized tests

Test data formats:
- **NPZ files** - Compressed NumPy arrays (`.npz`)
- **Protobuf files** - Serialized `TensorProto` messages (`.pb`)

Sources: [onnx/backend/test/loader.py:30-250](), [onnx/backend/test/case/node/__init__.py:240-380](), [onnx/backend/test/runner/__init__.py:81-94]().

## Test Case Execution Flow

The test execution flow involves test discovery, data preparation, backend execution, and result validation. The `Runner` class orchestrates this entire process.

### Test Execution Sequence

```mermaid
sequenceDiagram
    participant Loader as "load_model_tests"
    participant Runner as "Runner"
    participant Backend as "Backend.prepare()"
    participant BackendRep as "BackendRep.run()"
    participant Validator as "assert_similar_outputs"
    
    Loader->>Runner: load_model_tests(kind)
    Note over Loader: Loads node/real/simple/pytorch tests
    Runner->>Runner: _add_model_test(rt, category)
    Note over Runner: Stores in _test_items dict
    
    loop For each test execution
        Runner->>Runner: _get_test_case(name)
        Runner->>Backend: prepare(model, device, **kwargs)
        Backend-->>Runner: BackendRep
        
        alt Has test data (model tests)
            Runner->>Runner: Download/load test data from NPZ or PB files
            Runner->>BackendRep: run(inputs)
            BackendRep-->>Runner: outputs (namedtupledict)
        else Node test with inline data
            Runner->>BackendRep: run(inputs)
            BackendRep-->>Runner: outputs
        end
        
        Runner->>Validator: assert_similar_outputs(ref_outputs, outputs, rtol, atol)
        Validator-->>Runner: Pass/Fail/Skip
    end
```

Sources: [onnx/backend/test/runner/__init__.py:81-94](), [onnx/backend/test/runner/__init__.py:218-280](), [onnx/backend/test/loader.py:1-250]().

## Test Coverage Reporting

ONNX provides comprehensive test coverage tracking through two primary modules: static coverage analysis and dynamic coverage reporting.

### Static Coverage Analysis

The `stat_coverage.py` module analyzes test cases against the operator schema registry to identify gaps:

```mermaid
flowchart TD
    Schemas["defs.get_all_schemas()"] --> StatCoverage["stat_coverage.py"]
    TestSnippets["collect_snippets()"] --> StatCoverage
    ModelTests["load_model_tests()"] --> StatCoverage
    
    StatCoverage --> Analysis["Coverage Analysis"]
    Analysis --> CoveredOps["Covered Operators"]
    Analysis --> NoCoverOps["Uncovered Operators"]
    Analysis --> ModelCoverage["Model Test Coverage"]
    
    CoveredOps --> MarkdownReport["TestCoverage.md"]
    NoCoverOps --> MarkdownReport
    ModelCoverage --> MarkdownReport
```

The generated report shows:
- Node test coverage (e.g., "187/199 operators covered")
- Model test coverage by category
- Detailed test case listings for each operator
- Uncovered operators requiring new tests

### Dynamic Coverage Reporting

The `Coverage` class in [onnx/backend/test/report/coverage.py:20-261]() tracks runtime execution:

```python
class Coverage:
    - _all_schemas: list[OpSchema]
    - _node_test_data: dict[str, NodeCoverage]  # operator -> coverage info
    - _model_test_data: list[ModelCoverage]
    
    + update_node_test(test_name, node)
    + update_model_test(test_name, model_name)
    + report_text() -> str
    + report_xlsx(writer, ort_coverage)
    + report_csv(writer)  # For backend scoreboard
```

The coverage system generates:
1. **Text reports** - Human-readable summaries with tables
2. **CSV files** - Machine-readable data for the [ONNX Backend Scoreboard](https://onnx.ai/backend-scoreboard)
3. **XLSX spreadsheets** - Detailed coverage with attribute and type tracking

Sources: [onnx/backend/test/stat_coverage.py:1-262](), [onnx/backend/test/report/coverage.py:20-261](), [onnx/backend/test/case/__init__.py:1-100]().

## Reference Evaluator as a Backend

The `ReferenceEvaluator` provides a pure Python implementation of ONNX operators and can be used as a backend for testing. This is useful for:

1. Testing the ONNX specification itself
2. Providing a reference implementation to compare with other backends
3. Debugging operator implementations

```mermaid
flowchart TD
    subgraph "ReferenceEvaluator as Backend"
        RefEval["ReferenceEvaluator"] --> RefBackendRep["ReferenceEvaluatorBackendRep"]
        RefBackendRep --> run["run()"]
        RefEval --> OpRun["OpRun"]
        OpRun --> OpRunBinary["OpRunBinary"]
        OpRun --> OpRunUnary["OpRunUnary"]
        RefEval --> OnnxNode["ONNX Node/Model"]
    end
    
    subgraph "Backend Test System"
        BackendTest["BackendTest"] --> RefBackend["ReferenceEvaluatorBackend"]
        RefBackend --> prepare["prepare()"]
        prepare --> RefBackendRep
        BackendTest --> TestCases["Test Cases"]
    end
    
    RefBackend --> RefEval
```

The `ReferenceEvaluatorBackend` wraps the `ReferenceEvaluator` to provide a backend implementation that can be used with the ONNX test framework.

Sources: [onnx/test/test_backend_reference.py:26-90](). [onnx/reference/reference_evaluator.py:33-201]().

## Creating Custom Tests

You can create custom test cases for operators or models:

### Creating Node Tests

Node tests are created by defining test functions in [onnx/backend/test/case/node/](). Each operator has its own test file (e.g., `cast.py`, `add.py`):

```python
# In onnx/backend/test/case/node/add.py
import numpy as np
import onnx
from onnx.backend.test.case.node import expect

class Add(Base):
    @staticmethod
    def export_add() -> None:
        node = onnx.helper.make_node(
            'Add',
            inputs=['x', 'y'],
            outputs=['sum'],
        )
        
        x = np.random.randn(3, 4, 5).astype(np.float32)
        y = np.random.randn(3, 4, 5).astype(np.float32)
        
        expect(node, inputs=[x, y], outputs=[x + y], name='test_add')
    
    @staticmethod
    def export_add_broadcast() -> None:
        node = onnx.helper.make_node(
            'Add',
            inputs=['x', 'y'],
            outputs=['sum'],
        )
        
        x = np.random.randn(3, 4, 5).astype(np.float32)
        y = np.random.randn(5).astype(np.float32)  # Broadcasting
        
        expect(node, inputs=[x, y], outputs=[x + y], name='test_add_bcast')
```

The `expect()` function in [onnx/backend/test/case/node/__init__.py:240-380]() creates the test artifacts:

1. Wraps the node in a minimal `GraphProto` and `ModelProto`
2. Serializes inputs/outputs to `.pb` files in `test_data/node/test_<name>/`
3. Registers the test for discovery by `load_model_tests()`

Sources: [onnx/backend/test/case/node/__init__.py:240-380](), [onnx/backend/test/case/node/add.py:1-50](), [onnx/backend/test/case/base.py:1-50]().

### Creating Model Tests

For model tests, you typically need to:

1. Create or download an ONNX model
2. Create test data (inputs and expected outputs)
3. Register the model as a test case

## Detailed Test Execution Workflow

The `Runner` class manages the complete test lifecycle from discovery through execution to result validation.

### Test Discovery and Organization

```mermaid
flowchart TD
    Init["Runner.__init__(backend, parent_module)"] --> LoadNode["load_model_tests(kind='node')"]
    Init --> LoadReal["load_model_tests(kind='real')"]
    Init --> LoadSimple["load_model_tests(kind='simple')"]
    Init --> LoadPyTorch["load_model_tests(kind='pytorch-*')"]
    
    LoadNode --> AddTest1["_add_model_test(rt, 'Node')"]
    LoadReal --> AddTest2["_add_model_test(rt, 'Real')"]
    LoadSimple --> AddTest3["_add_model_test(rt, 'Simple')"]
    
    AddTest1 --> TestItems["_test_items: dict[category, dict[name, TestItem]]"]
    AddTest2 --> TestItems
    AddTest3 --> TestItems
    
    TestItems --> ApplyFilters["Apply include/exclude/xfail patterns"]
    ApplyFilters --> GenerateTestCases["Generate unittest.TestCase classes"]
```

### Test Execution with Error Handling

```mermaid
flowchart TD
    Start["Test Function Invocation"] --> CheckXFail["Check if test in _xfail_patterns"]
    CheckXFail -->|Yes| ExpectFail["Mark as expected failure"]
    CheckXFail -->|No| Proceed["Proceed with test"]
    
    Proceed --> CheckDevice["backend.supports_device(device)"]
    CheckDevice -->|False| SkipDevice["Raise BackendIsNotSupposedToImplementIt"]
    CheckDevice -->|True| CheckCompat["backend.is_compatible(model, device)"]
    
    CheckCompat -->|False| SkipIncompat["Raise BackendIsNotSupposedToImplementIt"]
    CheckCompat -->|True| Prepare["backend_rep = backend.prepare(model, device)"]
    
    Prepare --> LoadData["Load test data (NPZ/PB)"]
    LoadData --> Execute["outputs = backend_rep.run(inputs)"]
    Execute --> Validate["assert_similar_outputs(ref, outputs, rtol, atol)"]
    
    Validate -->|Pass| Success["Test Pass"]
    Validate -->|Fail| Failure["Test Failure with diff"]
    
    SkipDevice --> SkipResult["Test Skipped"]
    SkipIncompat --> SkipResult
    ExpectFail --> TryRun["Run test anyway"]
    TryRun -->|Fails| ExpectedFail["Expected Failure (passes)"]
    TryRun -->|Passes| UnexpectedPass["Unexpected Pass (fails)"]
```

### Output Comparison Logic

The `assert_similar_outputs` function in [onnx/backend/test/runner/__init__.py:500-532]() performs detailed output validation:

```python
def assert_similar_outputs(
    ref_outputs: Sequence[Any],
    outputs: Sequence[Any],
    rtol: float,
    atol: float
) -> None:
    # Handles multiple output types:
    # - np.ndarray: use np.testing.assert_allclose with rtol/atol
    # - list: recursively compare elements
    # - dict: compare keys and values
    # - SparseTensorProto: compare indices, values, shape
```

Sources: [onnx/backend/test/runner/__init__.py:81-94](), [onnx/backend/test/runner/__init__.py:115-280](), [onnx/backend/test/runner/__init__.py:500-532]().

## Testing Reference Evaluator

The `ReferenceEvaluator` is a pure Python implementation of the ONNX specification. It's used as a reference implementation for operator behaviors and can be used as a backend for testing.

When implementing a new operator or working on operator compatibility, the Reference Evaluator is an essential tool for verifying correctness.

```python
# Example of using ReferenceEvaluator directly
import onnx
import numpy as np
from onnx.reference import ReferenceEvaluator

# Create or load a model
model = onnx.load("model.onnx")

# Create an evaluator
ref = ReferenceEvaluator(model)

# Run the model
inputs = {"X": np.array([1, 2, 3], dtype=np.float32)}
outputs = ref.run(None, inputs)
```

Sources: [onnx/reference/reference_evaluator.py:33-201](). [onnx/test/reference_evaluator_test.py:1-500]().

## Conclusion

The ONNX testing framework provides a comprehensive system for ensuring that backend implementations correctly follow the ONNX specification. By implementing the Backend interface and running the provided tests, you can verify that your backend correctly handles ONNX models and operators.

The framework includes tools for tracking test coverage, creating new tests, and comparing results across different backends. The Reference Evaluator provides a reference implementation that can be used as a baseline for comparison.

---

