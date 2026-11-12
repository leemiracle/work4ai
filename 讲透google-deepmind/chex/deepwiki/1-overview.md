<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/chex · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [chex/__init__.py](chex/__init__.py)
- [docs/api.rst](docs/api.rst)

</details>



This document provides a high-level introduction to the Chex library, its architecture, and its primary capabilities. Chex is a testing and debugging utility library designed specifically for JAX code, providing robust assertions, dataclass support, and testing infrastructure.

For installation instructions and basic usage examples, see [Getting Started](#2). For detailed documentation of specific subsystems, see [Assertion System](#3), [Dataclass System](#4), [Type System](#5), [Testing Infrastructure](#6), and [Utilities](#7).

**Sources:** [chex/__init__.py:1-213](), [README.md:1-474]()

## What is Chex?

Chex is a library that addresses three fundamental challenges when working with JAX:

1. **Validation and Instrumentation**: JAX's type system cannot express array shapes, ranks, or dtypes. Chex provides 40+ assertion functions to validate these properties both statically and at runtime.

2. **JAX-Compatible Data Structures**: Standard Python dataclasses are incompatible with JAX transformations. Chex provides `@chex.dataclass` decorator that registers dataclasses as JAX PyTrees while maintaining compatibility with dm-tree.

3. **Testing Across Execution Modes**: JAX code behaves differently under `jax.jit`, `jax.pmap`, and eager execution. Chex provides testing variants that automatically run tests across all these modes, plus debugging tools like `fake_jit` and `fake_pmap` to simplify development.

**Sources:** [README.md:9-16](), [chex/__init__.py:15]()

## Core Capabilities

### Assertion System (179.37 Combined Importance)

The assertion system is Chex's most important feature, divided into:

- **Static Assertions**: Validate array metadata without requiring concrete values (e.g., `assert_shape`, `assert_rank`, `assert_type`)
- **Value Assertions**: Check actual array values, enabled inside JIT-compiled functions via `@chexify` decorator (e.g., `assert_tree_all_finite`, `assert_trees_all_close`)
- **Tree Assertions**: Validate JAX PyTree structures and their contents (e.g., `assert_trees_all_equal_shapes`, `assert_tree_is_on_device`)
- **JAX-Specific Assertions**: Monitor JAX behavior like tracing frequency (`assert_max_traces`) and device availability

For detailed coverage, see [Assertion System](#3).

**Sources:** [chex/__init__.py:17-68](), [README.md:86-231]()

### Dataclass System (76.76 Combined Importance)

The `@chex.dataclass` decorator extends Python's standard dataclasses with JAX compatibility:

```python
@chex.dataclass
class Parameters:
  x: chex.ArrayDevice
  y: chex.ArrayDevice

# Works with JAX transformations
jax.tree_util.tree_map(lambda x: 2.0 * x, parameters)

# Compatible with dm-tree
tree.flatten(parameters)
```

For implementation details, see [Dataclass System](#4).

**Sources:** [chex/__init__.py:73-75](), [README.md:33-85]()

### Testing Infrastructure (47.06 Importance for fake.py)

Chex provides two complementary testing approaches:

- **Fake Transformations**: Replace expensive JAX transformations with simpler equivalents for debugging (`fake_jit`, `fake_pmap`, `set_n_cpu_devices`)
- **Test Variants**: Automatically run the same test across multiple JAX execution contexts (`@variants` decorator with `with_jit`, `with_pmap`, `with_device` options)

For comprehensive documentation, see [Testing Infrastructure](#6).

**Sources:** [chex/__init__.py:77-101](), [README.md:237-408]()

## Module Architecture

### Public API Entry Point

The entire Chex public API is aggregated in [chex/__init__.py:1-213](), which imports and re-exports functionality from internal `_src` modules. The module exposes 100 public symbols organized into seven categories:

| Category | Symbol Count | Key Exports |
|----------|--------------|-------------|
| Assertions | 40 | `assert_shape`, `assert_rank`, `assert_tree_all_finite` |
| Chexify | 4 | `chexify`, `ChexifyChecks`, `block_until_chexify_assertions_complete` |
| Dataclasses | 3 | `dataclass`, `mappable_dataclass`, `register_dataclass_type_with_jax_tree_util` |
| Type Definitions | 14 | `Array`, `ArrayTree`, `ArrayDevice`, `Scalar`, `Shape` |
| Testing | 8 | `fake_jit`, `fake_pmap`, `variants`, `TestCase`, `params_product` |
| Utilities | 4 | `Dimensions`, `restrict_backends`, `disable_asserts`, `enable_asserts` |
| Warnings | 4 | `warn_deprecated_function`, `create_deprecated_function_alias` |

**Sources:** [chex/__init__.py:110-200]()

### Module Dependency Graph

```mermaid
graph TB
    subgraph "Public API Layer"
        INIT["chex/__init__.py<br/>Aggregates all public exports"]
    end
    
    subgraph "Core Assertion System"
        ASSERTS["chex/_src/asserts.py<br/>40+ assertion functions<br/>assert_shape, assert_rank, etc"]
        ASSERT_INT["chex/_src/asserts_internal.py<br/>@chex_assertion decorator<br/>Tracer detection utilities"]
        CHEXIFY["chex/_src/asserts_chexify.py<br/>@chexify decorator<br/>JIT-compatible value assertions"]
        
        ASSERTS --> ASSERT_INT
        CHEXIFY --> ASSERT_INT
    end
    
    subgraph "Data Structure System"
        DATACLASS["chex/_src/dataclass.py<br/>@dataclass decorator<br/>PyTree registration"]
        PYTYPES["chex/_src/pytypes.py<br/>Array, ArrayTree, Scalar<br/>Type aliases for JAX/NumPy"]
        
        DATACLASS --> PYTYPES
    end
    
    subgraph "Testing Infrastructure"
        FAKE["chex/_src/fake.py<br/>fake_jit, fake_pmap<br/>set_n_cpu_devices"]
        VARIANTS["chex/_src/variants.py<br/>@variants decorator<br/>TestCase base class"]
    end
    
    subgraph "Utilities"
        DIMENSIONS["chex/_src/dimensions.py<br/>Dimensions class<br/>Named shape specs"]
        RESTRICT["chex/_src/restrict_backends.py<br/>restrict_backends context manager"]
        WARNINGS["chex/_src/warnings.py<br/>Deprecation utilities"]
    end
    
    INIT --> ASSERTS
    INIT --> CHEXIFY
    INIT --> DATACLASS
    INIT --> PYTYPES
    INIT --> FAKE
    INIT --> VARIANTS
    INIT --> DIMENSIONS
    INIT --> RESTRICT
    INIT --> WARNINGS
    
    ASSERTS -.->|"uses types from"| PYTYPES
    FAKE -.->|"intercepts"| JAX["JAX Library<br/>jax.jit, jax.pmap"]
    DATACLASS -.->|"registers with"| JAX_TREE["jax.tree_util"]
    CHEXIFY -.->|"integrates with"| CHECKIFY["jax.checkify"]
```

**Sources:** [chex/__init__.py:1-213]()

## Core Subsystems

### 1. Assertion System Architecture

The assertion system operates in three layers:

```mermaid
graph TB
    subgraph "User-Facing API Layer"
        STATIC_API["Static Assertions<br/>assert_shape, assert_rank<br/>assert_equal_shape, assert_type"]
        VALUE_API["Value Assertions<br/>assert_tree_all_finite<br/>assert_trees_all_equal<br/>assert_numerical_grads"]
        DEVICE_API["Device Assertions<br/>assert_gpu_available<br/>assert_tree_is_on_device"]
        TRACE_API["Tracing Assertions<br/>assert_max_traces<br/>clear_trace_counter"]
    end
    
    subgraph "Internal Infrastructure Layer"
        WRAPPER["@chex_assertion decorator<br/>asserts_internal.py<br/>Unified error handling"]
        GLOBAL_STATE["Global State Management<br/>DISABLE_ASSERTIONS flag<br/>TRACE_COUNTER<br/>CHEXIFY_STORAGE"]
        HELPERS["Helper Functions<br/>has_tracers()<br/>is_traceable()<br/>format_shape_matcher()"]
    end
    
    subgraph "JIT Integration Layer"
        CHEXIFY_DEC["@chexify decorator<br/>asserts_chexify.py<br/>Wraps jit/pmap functions"]
        CHECKS_CONFIG["ChexifyChecks enum<br/>user, nan, index, div, float"]
        ASYNC["Async Error Handling<br/>block_until_chexify_assertions_complete()"]
    end
    
    STATIC_API --> WRAPPER
    VALUE_API --> WRAPPER
    DEVICE_API --> WRAPPER
    TRACE_API --> GLOBAL_STATE
    
    WRAPPER --> GLOBAL_STATE
    WRAPPER --> HELPERS
    
    VALUE_API -.->|"requires"| CHEXIFY_DEC
    CHEXIFY_DEC --> CHECKS_CONFIG
    CHEXIFY_DEC --> ASYNC
    CHEXIFY_DEC -.->|"uses"| JAX_CHECKIFY["jax.checkify API"]
```

**Key Components:**

- **`chex/_src/asserts.py`**: Contains all 40+ user-facing assertion functions
- **`chex/_src/asserts_internal.py`**: Provides `@chex_assertion` decorator that unifies all assertions with common error handling, tracer detection, and global state management
- **`chex/_src/asserts_chexify.py`**: Implements `@chexify` decorator that integrates with `jax.checkify` to enable value assertions inside JIT-compiled code

**Sources:** [chex/__init__.py:17-68](), [README.md:159-194]()

### 2. Data Structure System

```mermaid
graph LR
    subgraph "Type System"
        PYTYPES["chex/_src/pytypes.py<br/>Type Aliases"]
        ARRAY["Array, ArrayDevice<br/>ArrayNumpy, ArraySharded"]
        TREE["ArrayTree<br/>ArrayDeviceTree"]
        SCALAR["Scalar, Numeric"]
        META["Shape, Device<br/>PyTreeDef, ArrayDType"]
        
        PYTYPES --> ARRAY
        PYTYPES --> TREE
        PYTYPES --> SCALAR
        PYTYPES --> META
    end
    
    subgraph "Dataclass Implementation"
        DC["chex/_src/dataclass.py"]
        DC_DEC["@dataclass decorator<br/>Wraps @dataclasses.dataclass"]
        MAPPABLE["@mappable_dataclass<br/>Implements Mapping interface"]
        REGISTER["register_dataclass_type_with_jax_tree_util()<br/>Manual PyTree registration"]
        METHODS["Utility Methods<br/>from_tuple(), to_tuple()<br/>replace()"]
        
        DC --> DC_DEC
        DC --> MAPPABLE
        DC --> REGISTER
        DC --> METHODS
    end
    
    ARRAY -.->|"type hints for"| DC_DEC
    DC_DEC --> PYTREE_REG["JAX PyTree<br/>Registration"]
    MAPPABLE --> COLLECTIONS["collections.abc.Mapping<br/>dm-tree compatibility"]
```

**Key Components:**

- **`chex/_src/pytypes.py`**: Defines comprehensive type aliases for arrays, trees, scalars, and metadata
- **`chex/_src/dataclass.py`**: Provides `@dataclass` decorator that automatically registers dataclasses as JAX PyTrees and optionally exposes them as `Mapping` instances

**Sources:** [chex/__init__.py:73-75,81-95](), [README.md:33-85]()

### 3. Testing Infrastructure System

```mermaid
graph TB
    subgraph "Fake Transformations"
        FAKE_MODULE["chex/_src/fake.py"]
        FAKE_JIT["fake_jit()<br/>Replace jax.jit with identity"]
        FAKE_PMAP["fake_pmap()<br/>Replace jax.pmap with jax.vmap"]
        FAKE_BOTH["fake_pmap_and_jit()<br/>Combined replacement"]
        SET_DEVICES["set_n_cpu_devices(n)<br/>Simulate multi-device on CPU"]
        
        FAKE_MODULE --> FAKE_JIT
        FAKE_MODULE --> FAKE_PMAP
        FAKE_MODULE --> FAKE_BOTH
        FAKE_MODULE --> SET_DEVICES
    end
    
    subgraph "Test Variants Framework"
        VAR_MODULE["chex/_src/variants.py"]
        TESTCASE["TestCase<br/>Base class for variant tests"]
        VARIANTS["@variants decorator<br/>Generates test variants"]
        TYPES["ChexVariantType enum<br/>with_jit, without_jit<br/>with_device, with_pmap"]
        PARAMS["params_product()<br/>Cartesian product of params"]
        
        VAR_MODULE --> TESTCASE
        VAR_MODULE --> VARIANTS
        VAR_MODULE --> TYPES
        VAR_MODULE --> PARAMS
    end
    
    VARIANTS --> TESTCASE
    TESTCASE -.->|"can use"| FAKE_JIT
    TESTCASE -.->|"can use"| FAKE_PMAP
    SET_DEVICES -.->|"enables"| FAKE_PMAP
```

**Key Components:**

- **`chex/_src/fake.py`**: Provides debugging utilities that replace expensive JAX transformations with simpler equivalents
- **`chex/_src/variants.py`**: Implements test variant framework that automatically generates and runs tests across different JAX execution contexts

**Sources:** [chex/__init__.py:77-101](), [README.md:237-408]()

## Usage Pattern Overview

The following diagram illustrates how user code interacts with Chex's primary APIs:

```mermaid
graph TB
    subgraph "User Code"
        USER_FN["User Function"]
        USER_CLASS["User Dataclass"]
        USER_TEST["User Test"]
    end
    
    subgraph "Chex Decorators"
        CHEXIFY_USE["@chexify<br/>Enable value assertions in JIT"]
        DC_USE["@chex.dataclass<br/>JAX-compatible dataclass"]
        VARIANTS_USE["@chex.variants<br/>Run test across modes"]
        MAX_TRACES["@assert_max_traces<br/>Limit retracing"]
    end
    
    subgraph "Chex Function Calls"
        ASSERT_CALLS["assert_shape(arr, (2, 3))<br/>assert_rank(arr, 2)<br/>assert_tree_all_finite(tree)"]
        FAKE_CALLS["with fake_jit():<br/>    jitted_fn(...)<br/>with fake_pmap():<br/>    pmapped_fn(...)"]
        TYPE_HINTS["x: chex.Array<br/>tree: chex.ArrayTree<br/>shape: chex.Shape"]
    end
    
    subgraph "JAX Runtime Integration"
        JAX_OPS["jax.jit(fn)<br/>jax.pmap(fn)<br/>jax.tree_util.tree_map"]
        CHECKIFY_INT["jax.checkify<br/>Runtime error checking"]
        PYTREE_INT["PyTree Registration<br/>Flatten/unflatten"]
    end
    
    USER_FN --> CHEXIFY_USE
    USER_FN --> MAX_TRACES
    USER_CLASS --> DC_USE
    USER_TEST --> VARIANTS_USE
    
    USER_FN --> ASSERT_CALLS
    USER_TEST --> FAKE_CALLS
    USER_FN --> TYPE_HINTS
    
    CHEXIFY_USE -.->|"integrates with"| CHECKIFY_INT
    DC_USE -.->|"registers with"| PYTREE_INT
    VARIANTS_USE -.->|"wraps"| JAX_OPS
    FAKE_CALLS -.->|"intercepts"| JAX_OPS
    ASSERT_CALLS -.->|"validates"| JAX_OPS
```

**Common Patterns:**

1. **Assertion Pattern**: Call assertion functions directly in code to validate array properties
2. **Chexify Pattern**: Wrap JIT-compiled functions with `@chexify` to enable value assertions
3. **Dataclass Pattern**: Use `@chex.dataclass` decorator to create JAX-compatible dataclasses
4. **Testing Pattern**: Inherit from `chex.TestCase` and use `@chex.variants` to test across execution modes
5. **Debugging Pattern**: Use `fake_jit()` or `fake_pmap()` context managers to simplify debugging

**Sources:** [README.md:52-307](), [chex/__init__.py:1-213]()

## Key Design Patterns

### 1. Decorator-Based API

Chex uses decorators extensively to modify behavior:

- `@chex.dataclass`: Extends dataclass with PyTree registration
- `@chexify`: Enables value assertions in JIT context
- `@variants`: Generates test variants
- `@assert_max_traces`: Monitors function retracing

**Sources:** [chex/__init__.py:70-75,97-102]()

### 2. Context Manager Pattern

Debugging utilities use context managers for temporary state changes:

- `fake_jit()`: Temporarily disables JIT compilation
- `fake_pmap()`: Replaces pmap with vmap
- `restrict_backends()`: Restricts JAX to specific backends

**Sources:** [chex/__init__.py:77-80,96]()

### 3. Global State Management

Assertions support global configuration via module-level state:

- `disable_asserts()` / `enable_asserts()`: Toggle all assertions
- `clear_trace_counter()`: Reset trace counter for `assert_max_traces`
- `CHEXIFY_STORAGE`: Stores checkified function versions

**Sources:** [chex/__init__.py:66-67]()

### 4. Type Alias System

Chex provides descriptive type aliases for better code documentation:

- `Array`, `ArrayDevice`, `ArrayNumpy`: Different array types
- `ArrayTree`, `ArrayDeviceTree`: Nested structures
- `Scalar`, `Numeric`, `Shape`: Metadata types

**Sources:** [chex/__init__.py:81-95]()

## Project Statistics

| Metric | Value |
|--------|-------|
| Current Version | 0.1.91 |
| Public API Symbols | 100 |
| Assertion Functions | 40+ |
| Test Variant Types | 5 |
| Core Modules | 10 |
| External Dependencies | JAX, NumPy, dm-tree |

**Sources:** [chex/__init__.py:108,110-200]()

## Next Steps

- For installation and quick start examples, see [Getting Started](#2)
- For detailed assertion documentation, see [Assertion System](#3)
- For dataclass usage patterns, see [Dataclass System](#4)
- For testing utilities, see [Testing Infrastructure](#6)
- For complete API reference, see [API Reference](#9)

---

