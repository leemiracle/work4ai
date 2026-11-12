<!-- source: DeepWiki mcp.deepwiki.com · repo ivy-llc/ivy · page 4 Core Functional API · fetched 2026-10-21 -->

# Core Functional API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ivy/data_classes/array/elementwise.py](ivy/data_classes/array/elementwise.py)
- [ivy/data_classes/container/elementwise.py](ivy/data_classes/container/elementwise.py)
- [ivy/functional/backends/jax/elementwise.py](ivy/functional/backends/jax/elementwise.py)
- [ivy/functional/backends/jax/general.py](ivy/functional/backends/jax/general.py)
- [ivy/functional/backends/mxnet/elementwise.py](ivy/functional/backends/mxnet/elementwise.py)
- [ivy/functional/backends/mxnet/general.py](ivy/functional/backends/mxnet/general.py)
- [ivy/functional/backends/numpy/elementwise.py](ivy/functional/backends/numpy/elementwise.py)
- [ivy/functional/backends/numpy/general.py](ivy/functional/backends/numpy/general.py)
- [ivy/functional/backends/paddle/elementwise.py](ivy/functional/backends/paddle/elementwise.py)
- [ivy/functional/backends/paddle/general.py](ivy/functional/backends/paddle/general.py)
- [ivy/functional/backends/tensorflow/elementwise.py](ivy/functional/backends/tensorflow/elementwise.py)
- [ivy/functional/backends/tensorflow/general.py](ivy/functional/backends/tensorflow/general.py)
- [ivy/functional/backends/torch/elementwise.py](ivy/functional/backends/torch/elementwise.py)
- [ivy/functional/backends/torch/general.py](ivy/functional/backends/torch/general.py)
- [ivy/functional/ivy/elementwise.py](ivy/functional/ivy/elementwise.py)
- [ivy/functional/ivy/general.py](ivy/functional/ivy/general.py)
- [ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py](ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py)
- [ivy_tests/test_ivy/test_functional/test_core/test_general.py](ivy_tests/test_ivy/test_functional/test_core/test_general.py)

</details>



The Core Functional API is the heart of the Ivy framework, providing a comprehensive set of framework-agnostic mathematical operations that serve as the foundation for building higher-level functionality. This API is designed to work consistently across different machine learning frameworks by abstracting away backend-specific implementations while maintaining a unified interface.

## Overview

The Core Functional API provides fundamental operations that work with arrays across different ML frameworks. It includes categories such as elementwise functions, linear algebra operations, array creation utilities, data type handling, array manipulation, and neural network layers.

```mermaid
graph TD
    subgraph "Core Functional API Overview"
        CoreAPI["Core Functional API"]
        CoreAPI --> General["General Functions"]
        CoreAPI --> Elementwise["Elementwise Functions"]
        CoreAPI --> LinearAlgebra["Linear Algebra"]
        CoreAPI --> Creation["Array Creation"]
        CoreAPI --> DataType["Data Type System"]
        CoreAPI --> Manipulation["Array Manipulation"]
        CoreAPI --> NNLayers["Neural Network Layers"]
    end
    
    General --> |"includes"| Utils["Utility Functions"]
    General --> |"includes"| TypeConv["Type Conversion"]
    General --> |"includes"| DeviceHandling["Device Handling"]
    
    Elementwise --> |"includes"| Math["Mathematical Operations"]
    Elementwise --> |"includes"| Logic["Logical Operations"]
    Elementwise --> |"includes"| Comparison["Comparison Operations"]
    
    LinearAlgebra --> |"includes"| MatrixOps["Matrix Operations"]
    LinearAlgebra --> |"includes"| Decomp["Matrix Decompositions"]
    
    Creation --> |"includes"| ArrayConstr["Array Construction"]
    
    DataType --> |"includes"| TypeInfer["Type Inference"]
    DataType --> |"includes"| TypeProm["Type Promotion"]
    
    Manipulation --> |"includes"| Reshape["Reshape Operations"]
    Manipulation --> |"includes"| Concat["Concatenation Operations"]
    
    NNLayers --> |"includes"| Linear["Linear Layers"]
    NNLayers --> |"includes"| Conv["Convolutional Layers"]
    NNLayers --> |"includes"| Activ["Activation Functions"]
```

Sources:
- [ivy/functional/ivy/general.py:1-1346](ivy/functional/ivy/general.py:1-1346)
- [ivy/functional/ivy/elementwise.py:1-500](ivy/functional/ivy/elementwise.py:1-500)

## Function Execution Flow

When you call a function from the Core Functional API, it goes through several layers of processing before the actual computation is performed:

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant IvyAPI as "Ivy API Function"
    participant Wrappers as "Function Wrappers"
    participant Backend as "Backend Implementation"
    participant Native as "Native Framework"
    
    User->>IvyAPI: Call function (e.g., ivy.abs(x))
    IvyAPI->>Wrappers: Pass through wrapper stack
    Note over Wrappers: @handle_exceptions
    Note over Wrappers: @handle_nestable
    Note over Wrappers: @handle_array_like_without_promotion 
    Note over Wrappers: @inputs_to_native_arrays
    Note over Wrappers: @handle_array_function
    Note over Wrappers: @handle_out_argument
    Note over Wrappers: @handle_device
    Wrappers->>Backend: Dispatch to current backend
    Backend->>Native: Execute native operation
    Native->>Backend: Return native result
    Backend->>Wrappers: Convert to ivy.Array
    Wrappers->>IvyAPI: Apply post-processing
    IvyAPI->>User: Return result
```

Sources:
- [ivy/functional/ivy/general.py:633-678](ivy/functional/ivy/general.py:633-678)
- [ivy/functional/ivy/elementwise.py:25-125](ivy/functional/ivy/elementwise.py:25-125)

## Function Categories

### General Functions

General functions provide utilities for array checking, conversions, mode settings, and special operations.

Key functions include:
- Array type checking: `is_array`, `is_native_array`
- Conversion functions: `to_numpy`, `to_scalar`, `to_list`
- Array comparison: `array_equal`, `all_equal`
- Vector operations: `clip_vector_norm`, `clip_matrix_norm`
- Data encoding: `fourier_encode`

```mermaid
classDiagram
    class GeneralFunctions {
        <<Interface>>
        +is_array(x, exclusive) bool
        +is_native_array(x, exclusive) bool
        +to_numpy(x, copy) ndarray
        +to_scalar(x) Number
        +to_list(x) list
        +array_equal(x0, x1) bool
        +all_equal(*xs, equality_matrix) bool
        +clip_vector_norm(x, max_norm, p) Array
        +clip_matrix_norm(x, max_norm, p) Array
        +fourier_encode(x, max_freq, num_bands) Array
    }
```

Sources:
- [ivy/functional/ivy/general.py:280-347](ivy/functional/ivy/general.py:280-347)
- [ivy/functional/ivy/general.py:633-778](ivy/functional/ivy/general.py:633-778)
- [ivy/functional/ivy/general.py:971-1069](ivy/functional/ivy/general.py:971-1069)
- [ivy/functional/ivy/general.py:1157-1307](ivy/functional/ivy/general.py:1157-1307)

### Elementwise Functions

Elementwise functions perform operations on individual elements of arrays, such as mathematical operations, comparisons, and bitwise manipulations.

Key functions include:
- Basic arithmetic: `add`, `subtract`, `multiply`, `divide` 
- Mathematical functions: `abs`, `exp`, `log`, `cos`, `sin`
- Comparison operations: `equal`, `greater`, `less`
- Rounding operations: `floor`, `ceil`

```mermaid
classDiagram
    class ElementwiseFunctions {
        <<Interface>>
        +abs(x, out) Array
        +add(x1, x2, alpha, out) Array
        +ceil(x, out) Array
        +cos(x, out) Array
        +divide(x1, x2, out) Array
        +equal(x1, x2, out) Array
        +exp(x, out) Array
        +floor(x, out) Array
        +greater(x1, x2, out) Array
        +less(x1, x2, out) Array
    }
```

Sources:
- [ivy/functional/ivy/elementwise.py:25-144](ivy/functional/ivy/elementwise.py:25-144)
- [ivy/functional/ivy/elementwise.py:347-494](ivy/functional/ivy/elementwise.py:347-494)
- [ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py:164-201](ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py:164-201)

## Backend System Integration

The Core Functional API is implemented across multiple backends, allowing seamless switching between different frameworks:

```mermaid
graph TD
    API["Core Functional API\n(ivy/functional/ivy/)"]
    
    subgraph "Backend Implementations"
        TF["TensorFlow Backend\n(ivy/functional/backends/tensorflow/)"]
        PT["PyTorch Backend\n(ivy/functional/backends/torch/)"]
        JX["JAX Backend\n(ivy/functional/backends/jax/)"]
        NP["NumPy Backend\n(ivy/functional/backends/numpy/)"]
        PD["Paddle Backend\n(ivy/functional/backends/paddle/)"]
    end
    
    API --> FunctionDef["Function Definition\n(e.g., elementwise.abs)"]
    FunctionDef --> BackendCall["Backend Call\n(current_backend(x).abs(x))"]
    
    BackendCall --> BackendSelection["Backend Selection\nBased on:"]
    BackendSelection --> InputType["Input Type"]
    BackendSelection --> CurrentBackend["Current Backend Setting"]
    
    BackendSelection --> |"If TensorFlow"| TF
    BackendSelection --> |"If PyTorch"| PT
    BackendSelection --> |"If JAX"| JX
    BackendSelection --> |"If NumPy"| NP
    BackendSelection --> |"If Paddle"| PD
    
    TF --> TFImpl["TensorFlow Implementation\n(tf.abs)"]
    PT --> PTImpl["PyTorch Implementation\n(torch.abs)"]
    JX --> JXImpl["JAX Implementation\n(jnp.absolute)"]
    NP --> NPImpl["NumPy Implementation\n(np.absolute)"]
    PD --> PDImpl["Paddle Implementation\n(paddle.abs)"]
```

Sources:
- [ivy/functional/ivy/elementwise.py:125](ivy/functional/ivy/elementwise.py:125)
- [ivy/functional/backends/tensorflow/elementwise.py:12-23](ivy/functional/backends/tensorflow/elementwise.py:12-23)
- [ivy/functional/backends/torch/elementwise.py:17-42](ivy/functional/backends/torch/elementwise.py:17-42)
- [ivy/functional/backends/jax/elementwise.py:19-28](ivy/functional/backends/jax/elementwise.py:19-28)
- [ivy/functional/backends/numpy/elementwise.py:12-22](ivy/functional/backends/numpy/elementwise.py:12-22)

## Function Wrapping System

Ivy uses a sophisticated function wrapping system to handle common concerns such as type conversion, device placement, and error handling:

```mermaid
graph TD
    FunctionCall["Function Call"]
    
    subgraph "Function Wrapper Stack"
        handle_exceptions["@handle_exceptions\nHandle errors uniformly"]
        handle_backend_invalid["@handle_backend_invalid\nCheck backend compatibility"]
        handle_nestable["@handle_nestable\nEnable container inputs"]
        handle_array_like["@handle_array_like_without_promotion\nConvert array-like inputs"]
        to_native_arrays["@to_native_arrays_and_back\nConvert to native backend arrays"]
        handle_out_argument["@handle_out_argument\nManage output array reuse"]
        handle_device["@handle_device\nPlace computation on device"]
    end
    
    FunctionCall --> handle_exceptions
    handle_exceptions --> handle_backend_invalid
    handle_backend_invalid --> handle_nestable
    handle_nestable --> handle_array_like
    handle_array_like --> to_native_arrays
    to_native_arrays --> handle_out_argument
    handle_out_argument --> handle_device
    handle_device --> BackendFunction["Backend-specific implementation"]
    BackendFunction --> Result["Return Result"]
```

Sources:
- [ivy/functional/ivy/elementwise.py:25-36](ivy/functional/ivy/elementwise.py:25-36)
- [ivy/functional/ivy/general.py:633-638](ivy/functional/ivy/general.py:633-638)
- [ivy/func_wrapper.py](ivy/func_wrapper.py)

## Array Classes and Method Bindings

The Core Functional API functions are also available as methods on array classes, making them more convenient to use in object-oriented style:

```mermaid
classDiagram
    class Array {
        +dtype
        +shape
        +device
        +abs() Array
        +add(other) Array
        +cos() Array
        +equal(other) Array
        +exp() Array
        ...
    }
    
    class Container {
        +abs() Container
        +add(other) Container
        +cos() Container
        +equal(other) Container
        +exp() Container
        ...
    }
    
    Array --> "_ArrayWithElementwise" : inherits methods
    Container --> "_ContainerWithElementwise" : inherits methods
```

Sources:
- [ivy/data_classes/array/elementwise.py:11-42](ivy/data_classes/array/elementwise.py:11-42)
- [ivy/data_classes/container/elementwise.py:9-52](ivy/data_classes/container/elementwise.py:9-52)

## Example Usage Patterns

Here are some typical usage patterns for the Core Functional API:

### Direct Function Calls

```python
# Using Core API functions directly
x = ivy.array([1.0, -2.0, 3.0])
y = ivy.array([2.0, 3.0, 4.0])

# Elementwise operations
abs_x = ivy.abs(x)                  # [1.0, 2.0, 3.0]
sum_xy = ivy.add(x, y)              # [3.0, 1.0, 7.0]
exp_x = ivy.exp(x)                  # [2.72, 0.14, 20.09]

# With out argument
result = ivy.zeros_like(x)
ivy.abs(x, out=result)              # result now contains [1.0, 2.0, 3.0]
```

### Method-Style Usage

```python
# Using methods on ivy.Array objects
x = ivy.array([1.0, -2.0, 3.0])
y = ivy.array([2.0, 3.0, 4.0])

# Elementwise operations as methods
abs_x = x.abs()                     # [1.0, 2.0, 3.0]
sum_xy = x.add(y)                   # [3.0, 1.0, 7.0]
exp_x = x.exp()                     # [2.72, 0.14, 20.09]
```

### Backend Switching

```python
# Switching backends
ivy.set_backend("torch")
x_torch = ivy.array([1.0, -2.0, 3.0])  # Creates a torch tensor internally

ivy.set_backend("tensorflow")
x_tf = ivy.array([1.0, -2.0, 3.0])     # Creates a tensorflow tensor internally

# Same API works across backends
abs_torch = ivy.abs(x_torch)  # Uses torch.abs internally
abs_tf = ivy.abs(x_tf)        # Uses tf.abs internally
```

Sources:
- [ivy/functional/ivy/elementwise.py:97-123](ivy/functional/ivy/elementwise.py:97-123)
- [ivy/functional/ivy/elementwise.py:463-492](ivy/functional/ivy/elementwise.py:463-492)
- [ivy/data_classes/array/elementwise.py:11-42](ivy/data_classes/array/elementwise.py:11-42)

## Performance and Optimization

The Core Functional API is designed to minimize overhead while providing a consistent interface across backends:

1. **Direct Backend Dispatching**: Core functions immediately delegate to the current backend implementation
2. **Native Array Handling**: Input arrays are converted to the appropriate backend's native format once, then processed
3. **Memory Reuse**: The `out` parameter allows reusing existing memory for outputs
4. **Function Caching**: Common function calls can be cached to avoid redundant computation

## Testing and Verification

The Core API functions are extensively tested across all supported backends to ensure consistent behavior:

```mermaid
graph TD
    TestFile["Test Files\n(ivy_tests/test_ivy/test_functional/test_core/)"]
    
    TestFile --> ElementwiseTests["Elementwise Function Tests"]
    TestFile --> GeneralTests["General Function Tests"]
    
    ElementwiseTests --> TestFunction["test_function Helper"]
    GeneralTests --> TestFunction
    
    TestFunction --> BackendCheck["Verify across all backends"]
    
    BackendCheck --> TorchTest["Test with PyTorch"]
    BackendCheck --> TFTest["Test with TensorFlow"]
    BackendCheck --> JAXTest["Test with JAX"]
    BackendCheck --> NumPyTest["Test with NumPy"]
    
    TorchTest --> CompareResults["Compare Results\nAcross Backends"]
    TFTest --> CompareResults
    JAXTest --> CompareResults
    NumPyTest --> CompareResults
    
    CompareResults --> AssertAllClose["Assert Values\nMatch Within Tolerance"]
```

Sources:
- [ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py:164-201](ivy_tests/test_ivy/test_functional/test_core/test_elementwise.py:164-201)
- [ivy_tests/test_ivy/test_functional/test_core/test_general.py:377-407](ivy_tests/test_ivy/test_functional/test_core/test_general.py:377-407)

## Extending the Core API

When adding new functions to the Core API, you need to:

1. Define the function in the appropriate file in `ivy/functional/ivy/`
2. Implement backend-specific versions in each `ivy/functional/backends/*/` directory
3. Add appropriate function wrappers (decorators)
4. Add test cases to verify behavior across backends
5. Optionally add the function to array and container classes

This ensures that new functionality maintains the same level of framework-agnostic compatibility as existing functions.

---

