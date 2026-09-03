# ONNX Export

> 来源: DeepWiki pytorch/pytorch (Last indexed: 2 September 2026, commit 580b06)

Relevant source files: aten/src/ATen/native/{Activation,BinaryOps,Correlation,Integration,TensorCompare,TensorFactories}.cpp, torch/_refs/__init__.py, torch/_refs/nn/functional/__init__.py, test/export/test_export_opinfo.py 等。

PyTorch provides capabilities to export models to the Open Neural Network Exchange (ONNX) format, enabling interoperability with various inference engines and hardware accelerators. The ecosystem currently supports two primary export paths: the legacy **TorchScript-based exporter** and the modern **`torch.export`-based exporter**.

## Overview of Exporter Architectures

The ONNX export infrastructure has evolved from a tracing/scripting approach to a graph-capture approach based on PyTorch 2.0 technologies.

| Feature | TorchScript Exporter (Legacy) | `torch.export` Exporter (Modern) |
|---|---|---|
| **Core Technology** | TorchScript (JIT) | `torch.export` / TorchDynamo |
| **Graph Capture** | Tracing or Scripting | FX Graph (ExportedProgram) |
| **Operator Mapping** | `symbolic_opset*.py` | `torchlib` / `onnxscript` |
| **Decompositions** | Limited / Manual | High (via Core ATen Ops) |
| **Entry Point** | `torch.onnx.export(..., dynamo=False)` | `torch.onnx.export(..., dynamo=True)` |

### High-Level Export Flow

The following diagram illustrates how PyTorch entities are transformed into ONNX IR across the different pipelines.

**Sources:** test/dynamo/test_repros.py:223-234, test/export/test_export_opinfo.py:109-115

---

## TorchScript ONNX Exporter (Legacy)

The legacy exporter operates by either tracing a sample execution or compiling the model into TorchScript IR. It relies on a large collection of "symbolic" functions that manually map PyTorch operators to ONNX operators.

- **Symbolic Registry:** Operators are mapped via version-specific files such as `symbolic_opset10.py` through `symbolic_opset20.py`.
- **Symbolic Helper:** A utility library `symbolic_helper.py` provides functions for manipulating TorchScript nodes and types during the conversion process.
- **Operator Dispatch:** The C++ backend dispatches PyTorch ops to these Python symbolic functions to construct the ONNX graph.

## torch.export-based ONNX Exporter (Modern)

The modern exporter (often referred to as the "Dynamo-based" or "FX" exporter) is built on top of the PyTorch 2.0 compilation stack. It uses `torch.export` to produce a stable FX graph which is then lowered to ONNX using `onnxscript`.

### The Three-Step Pipeline

1. **Graph Capture:** Capturing the model using `torch.export.export` to produce an `ExportedProgram`. This involves `FakeTensorMode` for shape and metadata propagation (test/export/test_export_opinfo.py:86-90)
2. **Decomposition:** Transforming complex ATen operators into simpler Core ATen operators via FX passes to ensure compatibility with ONNX schemas.
3. **ONNX Conversion:** Mapping the simplified FX graph to ONNX IR nodes using `torchlib` and `onnxscript`.

### Core Components

- **ATen Decompositions**: Many operators are decomposed into simpler primitives defined in `torch._refs` (torch/_refs/__init__.py:60-327) and `torch._refs.nn.functional` (torch/_refs/nn/functional/__init__.py:29-70)
- **Operator Mapping**: Maps ATen operators (e.g., `aten.add`, `aten.relu`) to ONNX equivalents (aten/src/ATen/native/BinaryOps.cpp:151-182, Activation.cpp:87-187)
- **Symbolic Shapes**: The exporter leverages the `ShapeEnv` and `SymInt` infrastructure to handle dynamic dimensions during the export process.

## Verification and Testing Infrastructure

### Key Verification Tools

- **OpInfo Integration**: Systematic testing of operators using the `OpInfo` framework (test/test_ops.py:204-218), driving coverage across dtypes and devices
- **Fake Device Simulation**: Testing export logic for different devices (like CUDA) on CPU-only machines using `FakeTensor` (test/export/test_export_opinfo.py:151-164)
- **Reference Implementations**: Using Python-based reference implementations in `torch._refs` to validate the behavior of ATen operators before they are lowered to ONNX

**Sources:** test/export/test_export_opinfo.py:83-125, torch/_refs/__init__.py:1-60, aten/src/ATen/native/Activation.cpp:1-187
