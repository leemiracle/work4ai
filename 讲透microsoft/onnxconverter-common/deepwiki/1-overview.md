<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/onnxconverter-common · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [onnxconverter_common/__init__.py](onnxconverter_common/__init__.py)
- [setup.py](setup.py)

</details>



## Purpose and Scope

The onnxconverter-common package is a comprehensive toolkit for converting and optimizing ONNX (Open Neural Network Exchange) models. It provides common functions and utilities used by various ONNX converters, enabling different converters to work together for handling models from mixed frameworks (such as a scikit-learn pipeline embedding a XGBoost model).

This page introduces the core components and architecture of onnxconverter-common. For detailed information about specific subsystems, refer to these dedicated pages:
- For optimization capabilities, see [ONNX Optimization System](#2)
- For precision conversion, see [Data Type Conversion](#3)
- For graph representation, see [Model Representation](#4)
- For utilities that help construct ONNX graphs, see [Graph Construction Utilities](#5)

Sources: [onnxconverter_common/__init__.py:6-10](), [README.md:5-6]()

## System Architecture Overview

The onnxconverter-common package consists of several key subsystems that collectively provide a robust framework for ONNX model conversion and optimization.

```mermaid
graph TD
    subgraph "onnxconverter_common Package"
        A["Model Optimization"] --> A1["optimizer.py: Graph Optimization"]
        A --> A2["Constant Folding"]
        
        B["Data Type Conversion"] --> B1["float16.py: FP32→FP16 Conversion"]
        B --> B2["auto_mixed_precision.py: Mixed Precision"]
        
        C["Graph Representation"] --> C1["topology.py: Model Graph Representation"]
        C --> C2["container.py: Model Components"]
        
        D["ONNX Operations"] --> D1["onnx_ops.py: ONNX Operator Application"]
        
        E["Graph Construction"] --> E1["onnx_fx.py: Python Function→ONNX Graph"]
    end
```

This diagram illustrates the main components of the package and how they relate to the core functionalities.

Sources: [onnxconverter_common/__init__.py:18-32]()

## Core Components and Functionality

### Model Optimization

The optimization subsystem provides techniques to improve model performance:

```mermaid
flowchart TD
    A["ONNX Model"] --> B["optimize_onnx/optimize_onnx_model"]
    B --> C["Graph Optimizations"]
    B --> D["Constant Folding"]
    B --> E["Mixed Precision"]
    
    C --> C1["Remove Identity Nodes"]
    C --> C2["Fuse Operations"]
    C --> C3["Optimize Transposes"]
    
    D --> D1["Identify Constants"]
    D --> D2["Compute Values"]
    D --> D3["Replace with Constants"]
    
    E --> E1["Identify Conversion Points"]
    E --> E2["Maintain Accuracy"]
    E --> E3["Balance Performance"]
    
    C --> F["Optimized ONNX Model"]
    D --> F
    E --> F
```

Sources: [onnxconverter_common/__init__.py:30]()

### Data Type Conversion

The package provides robust tools for converting between different precision formats:

```mermaid
flowchart TD
    A["ONNX Model\nFloat32"] --> B["convert_float_to_float16"]
    B --> C{"keep_io_types?"}
    
    C -->|"true"| D["Convert Internal Ops to FP16\nKeep I/O as FP32"]
    C -->|"false"| E["Convert Everything to FP16"]
    
    D --> F["Insert Cast Ops at I/O"]
    
    F --> G["Final Model"]
    E --> G
    
    subgraph "Block List Mechanism"
        H["DEFAULT_OP_BLOCK_LIST"]
        I["User Block List"]
        J["Protected Nodes"]
    end
    
    H --> B
    I --> B
    B --> J
```

Sources: [onnxconverter_common/__init__.py:29]()

### Model Representation

The model representation components provide abstractions for working with ONNX computational graphs:

```mermaid
graph TD
    A["ONNX Model"] --> B["Topology"]
    B --> C["Scopes"]
    B --> D["Variables"]
    B --> E["Operators"]
    
    C --> C1["Nested Scopes"]
    C --> C2["Variable Management"]
    
    D --> D1["Input Variables"]
    D --> D2["Output Variables"]
    D --> D3["Intermediate Variables"]
    
    E --> E1["Operator Instances"]
    E --> E2["Operator Domains"]
```

Sources: [onnxconverter_common/__init__.py:22]()

## Typical Data Flow

The following diagram illustrates the typical flow of data through the system:

```mermaid
flowchart LR
    A["Input Model"] --> B{"Format?"}
    B -->|"ONNX"| C["ONNX Model"]
    B -->|"Python Function"| D["onnx_fx.py"]
    D --> C
    
    C --> E["topology.py"]
    E --> F["Graph Representation"]
    
    F --> G{"Optimization"}
    G --> H["optimizer.py"]
    G --> I["Constant Folding"]
    G --> J["auto_mixed_precision.py"]
    
    H --> K["Optimized Graph"]
    I --> K
    J --> K
    
    K --> L["float16.py"]
    L --> M["Final ONNX Model"]
```

This diagram shows how models flow through the system - from input (either as ONNX models or Python functions) through graph representation, optimization, and potentially precision conversion to produce the final optimized ONNX model.

Sources: [onnxconverter_common/__init__.py:6-32]()

## Key Functions and Classes

The table below lists the key functions and classes exported by the package:

| Function/Class | Description | Module |
|----------------|-------------|--------|
| `optimize_onnx`, `optimize_onnx_graph`, `optimize_onnx_model` | Functions for optimizing ONNX models | optimizer |
| `convert_float_to_float16`, `convert_tensor_float_to_float16` | Functions for converting models to float16 precision | float16 |
| `auto_convert_mixed_precision` | Function for automatic mixed precision conversion | auto_mixed_precision |
| `Topology`, `Scope`, `Variable`, `Operator` | Classes for representing ONNX computational graphs | topology |
| Various ONNX operations | Functions for applying ONNX operators | onnx_ops |
| `Container` | Class for storing model components during conversion | container |

Sources: [onnxconverter_common/__init__.py:18-32]()

## Integration with the ONNX Ecosystem

onnxconverter-common is designed to serve as a foundation for various ONNX converters:

```mermaid
graph TD
    A["AI Framework Models"] --> A1["Scikit-learn Models"]
    A --> A2["XGBoost Models"]
    A --> A3["LightGBM Models"]
    A --> A4["Other ML Models"]
    
    B["ONNX Converters"] --> B1["sklearn-onnx"]
    B --> B2["keras2onnx"]
    B --> B3["onnxmltools"]
    B --> B4["tf2onnx"]
    
    C["onnxconverter-common"]
    
    A1 --> B1
    A2 --> B3
    A3 --> B3
    A4 --> B3
    
    B1 --> C
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> D["Optimized ONNX Models"]
    
    D --> E["ONNX Runtime"]
    D --> F["Other ONNX-compatible Runtimes"]
```

This diagram shows how onnxconverter-common fits into the broader ONNX ecosystem, providing a common foundation for various converters that transform models from different AI frameworks into optimized ONNX models ready for deployment.

Sources: [README.md:5-6]()

## Version and Compatibility Information

The current version of onnxconverter-common is 1.16.0, with the following details:

| Attribute | Value |
|-----------|-------|
| Version | 1.16.0 |
| Author | Microsoft |
| Producer | OnnxMLTools |
| Domain | onnxconverter-common |

The package is compatible with Python 3.5 and above.

Sources: [onnxconverter_common/__init__.py:11-16](), [setup.py:52-54]()

## Summary

The onnxconverter-common package provides essential tools and utilities for:

1. Optimizing ONNX models to improve performance
2. Converting between different precision formats
3. Representing and manipulating ONNX computational graphs
4. Constructing and modifying ONNX graphs

As a fundamental component in the ONNX ecosystem, it enables the efficient conversion and optimization of models from various AI frameworks to ONNX format.

Sources: [onnxconverter_common/__init__.py:6-10](), [README.md:5-6](), [setup.py:36]()

---

