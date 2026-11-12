<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RepDL · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/mnist_trainig.py](examples/mnist_trainig.py)
- [repdl/ops.py](repdl/ops.py)

</details>



This guide provides practical instructions for extending RepDL with custom operations, autograd functions, and neural network layers. The focus is on maintaining RepDL's reproducibility guarantees while adding new functionality to the framework.

**Scope**: This document covers the development workflow for extending RepDL. For information about using existing RepDL components, see [API Reference](#4). For details about backend implementation internals, see [Backend Implementation](#5).

**Prerequisites**: Before extending RepDL, you should be familiar with:
- PyTorch's autograd system and `torch.autograd.Function`
- C++ and/or CUDA programming for backend implementations
- pybind11 for Python-C++ bindings
- The reproducibility principles explained in [Reproducibility Principles](#6.4)

---

## Extension Architecture

RepDL follows a four-layer extension pattern where new functionality flows from low-level operations through progressively higher abstraction layers:

```mermaid
graph TB
    subgraph "Layer 1: Operation Definition"
        OPS["repdl/ops.py<br/>Python dispatcher interface"]
    end
    
    subgraph "Layer 2: Backend Implementation"
        CPU_IMPL["backend/cpu/*.cpp<br/>C++ implementation"]
        CUDA_IMPL["backend/cuda/*.cu<br/>CUDA kernel"]
    end
    
    subgraph "Layer 3: Binding Registration"
        CPU_BIND["backend/cpu/bind.cpp<br/>pybind11 module"]
        CUDA_BIND["backend/cuda/bind.cpp<br/>pybind11 module"]
    end
    
    subgraph "Layer 4: High-Level APIs"
        FUNC["repdl/func.py<br/>Autograd functions"]
        FUNCTIONAL["repdl/nn/functional.py<br/>Stateless operations"]
        MODULES["repdl/nn/*.py<br/>Stateful modules"]
    end
    
    OPS -->|"defines interface"| CPU_IMPL
    OPS -->|"defines interface"| CUDA_IMPL
    CPU_IMPL -->|"implemented in"| CPU_BIND
    CUDA_IMPL -->|"implemented in"| CUDA_BIND
    CPU_BIND -->|"used by"| FUNC
    CUDA_BIND -->|"used by"| FUNC
    FUNC -->|"used by"| FUNCTIONAL
    FUNC -->|"used by"| MODULES
    FUNCTIONAL -->|"used by"| MODULES
```

**Key Principle**: All computational operations must flow through `repdl.ops` to reach reproducible backend implementations. Direct use of PyTorch operations bypasses the reproducibility guarantees.

**Sources**: [README.md:47-52](), [repdl/ops.py:1-158]()

---

## Development Workflow

The typical workflow for adding new functionality follows these steps:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Ops as "repdl/ops.py"
    participant CPUImpl as "backend/cpu/*.cpp"
    participant CUDAImpl as "backend/cuda/*.cu"
    participant CPUBind as "backend/cpu/bind.cpp"
    participant CUDABind as "backend/cuda/bind.cpp"
    participant Func as "repdl/func.py"
    participant NN as "repdl/nn/*.py"
    
    Dev->>Ops: "1. Define operation signature"
    Note over Ops: "def custom_op(input, ...):<br/>    if input.is_cuda:<br/>        return cuda.custom_op(...)<br/>    else:<br/>        return cpu.custom_op(...)"
    
    Dev->>CPUImpl: "2a. Implement CPU version"
    Note over CPUImpl: "torch::Tensor custom_op(<br/>    const torch::Tensor& input, ...)"
    
    Dev->>CUDAImpl: "2b. Implement CUDA version"
    Note over CUDAImpl: "__global__ void custom_op_kernel(...)<br/>torch::Tensor custom_op(...)"
    
    Dev->>CPUBind: "3a. Register CPU binding"
    Note over CPUBind: "m.def('custom_op', &custom_op, ...)"
    
    Dev->>CUDABind: "3b. Register CUDA binding"
    Note over CUDABind: "m.def('custom_op', &custom_op, ...)"
    
    Dev->>Func: "4a. Create autograd function"
    Note over Func: "class CustomOpFunction(<br/>    torch.autograd.Function):<br/>    @staticmethod<br/>    def forward(ctx, input, ...):<br/>        return repdl.ops.custom_op(...)"
    
    Dev->>NN: "4b. Create module wrapper"
    Note over NN: "class CustomLayer(torch.nn.Module):<br/>    def forward(self, input):<br/>        return CustomOpFunction.apply(...)"
```

**Critical Requirements**:
1. **Dual Implementation**: Both CPU and CUDA backends must be implemented for each operation
2. **Device Routing**: The `repdl.ops` dispatcher must check `tensor.is_cuda` to route correctly
3. **Identical Interfaces**: CPU and CUDA implementations must have matching function signatures
4. **Reproducibility**: All implementations must follow the principles in [Reproducibility Principles](#6.4)

**Sources**: [README.md:47-52](), [repdl/ops.py:12-26]()

---

## Operation Dispatcher Pattern

The `repdl.ops` module implements a consistent pattern for device-aware operation dispatch. Understanding this pattern is essential for adding custom operations.

### Dispatcher Structure

Every operation in [repdl/ops.py]() follows this template:

| Component | Responsibility | Example |
|-----------|---------------|---------|
| Function signature | Python interface with type hints | `def conv2d(input: torch.Tensor, weight: torch.Tensor, ...)` |
| Device check | Determine backend based on tensor location | `if input.is_cuda:` |
| CUDA dispatch | Route CUDA tensors to CUDA backend | `return cuda.conv2d(...)` |
| CPU dispatch | Route CPU tensors to CPU backend | `return cpu.conv2d(...)` |

### Example: Matrix Multiplication

The `mm` operation demonstrates the standard pattern:

[repdl/ops.py:106-112]()

```python
def mm(
    input: torch.Tensor, mat2: torch.Tensor, transA: bool = False, transB: bool = False
) -> torch.Tensor:
    if input.is_cuda:
        return cuda.mm(input, mat2, transA, transB)
    else:
        return cpu.mm(input, mat2, transA, transB)
```

**Key Observations**:
- The dispatcher is device-agnostic - it doesn't care which GPU model or CPU architecture
- Parameters are passed identically to both backends
- The backend modules (`cpu` and `cuda`) are imported at the module level [repdl/ops.py:8-9]()

### Special Cases

Some operations have different dispatch logic:

**Division Operation**: [repdl/ops.py:98-103]()
- Falls back to PyTorch's `div` for CPU tensors or tensor-tensor division
- Only uses custom logic for CUDA scalar division to ensure reproducibility

**Square Root Operation**: [repdl/ops.py:122-123]()
- Uses dtype promotion to `float64` for correctly rounded results
- No separate backend implementation needed

**Sources**: [repdl/ops.py:8-158]()

---

## File Organization

When extending RepDL, you'll work with files across multiple directories. Understanding the organization helps locate where changes should be made:

```mermaid
graph TB
    subgraph "repdl/ (Python Package)"
        INIT["__init__.py<br/>Package exports"]
        OPS_PY["ops.py<br/>Operation dispatchers"]
        FUNC_PY["func.py<br/>Autograd functions"]
        OPTIM_PY["optim.py<br/>Optimizers"]
        UTILS_PY["utils.py<br/>Utilities"]
        
        subgraph "repdl/nn/"
            NN_INIT["__init__.py<br/>Module exports"]
            NN_FUNC["functional.py<br/>Stateless functions"]
            NN_BN["batchnorm.py<br/>BatchNorm layers"]
            NN_CONV["conv.py<br/>Convolution layers"]
            NN_LIN["linear.py<br/>Linear layers"]
            NN_LOSS["loss.py<br/>Loss functions"]
        end
        
        subgraph "repdl/backend/"
            BACKEND_INIT["__init__.py<br/>Backend loader"]
        end
    end
    
    subgraph "backend/ (Native Code)"
        subgraph "backend/cpu/"
            CPU_BIND["bind.cpp<br/>pybind11 bindings"]
            CPU_CONV["conv.cpp<br/>Convolution impl"]
            CPU_MM["mm.cpp<br/>MatMul impl"]
            CPU_OTHER["*.cpp<br/>Other operations"]
        end
        
        subgraph "backend/cuda/"
            CUDA_BIND["bind.cpp<br/>pybind11 bindings"]
            CUDA_CONV["conv.cu<br/>Convolution kernels"]
            CUDA_MM["mm.cu<br/>MatMul kernels"]
            CUDA_OTHER["*.cu<br/>Other kernels"]
        end
    end
    
    OPS_PY -.->|"imports"| BACKEND_INIT
    BACKEND_INIT -.->|"loads"| CPU_BIND
    BACKEND_INIT -.->|"loads"| CUDA_BIND
    
    FUNC_PY -->|"calls"| OPS_PY
    NN_FUNC -->|"calls"| FUNC_PY
    NN_BN -->|"calls"| FUNC_PY
    NN_CONV -->|"calls"| OPS_PY
    NN_LIN -->|"calls"| OPS_PY
    NN_LOSS -->|"calls"| OPS_PY
```

### Directory Structure

| Directory | Purpose | File Types | Build Process |
|-----------|---------|------------|---------------|
| `repdl/` | Python package root | `.py` | No build required |
| `repdl/nn/` | Neural network modules | `.py` | No build required |
| `backend/cpu/` | CPU implementations | `.cpp`, `.h` | Compiled with `pip install` |
| `backend/cuda/` | CUDA implementations | `.cu`, `.cuh` | Compiled with `pip install` |

**Sources**: [repdl/ops.py:1-10]()

---

## Testing Reproducibility

After implementing a custom operation, autograd function, or layer, you must verify that it produces bitwise identical results across devices.

### Verification Workflow

```mermaid
graph LR
    IMPL["Implement<br/>Operation"] --> CPU_TEST["Test on CPU"]
    CPU_TEST --> CUDA_TEST["Test on CUDA"]
    CUDA_TEST --> HASH_CPU["Compute hash<br/>on CPU"]
    HASH_CPU --> HASH_CUDA["Compute hash<br/>on CUDA"]
    HASH_CUDA --> COMPARE{"Hashes<br/>identical?"}
    COMPARE -->|"Yes"| SUCCESS["Reproducible"]
    COMPARE -->|"No"| DEBUG["Debug<br/>implementation"]
    DEBUG --> IMPL
```

### Hash Verification Example

Use `repdl.utils.get_hash` to verify reproducibility as shown in [examples/mnist_trainig.py:67-83]():

```python
# Before training
initial_hash = repdl.utils.get_hash(model)
print(f"Hash of the initial model: {initial_hash}")

# ... training loop ...

# After training
final_hash = repdl.utils.get_hash(model)
print(f"Hash of the trained model: {final_hash}")
```

### Testing Strategy

| Test Case | Purpose | Expected Result |
|-----------|---------|-----------------|
| CPU-only execution | Verify CPU implementation correctness | Consistent hash across multiple runs |
| CUDA-only execution | Verify CUDA implementation correctness | Consistent hash across multiple runs |
| Cross-device comparison | Verify CPU-CUDA equivalence | Identical hashes between CPU and CUDA |
| Multiple GPU models | Verify device independence | Identical hashes on V100, A100, etc. |

### Debugging Non-Reproducibility

If hashes differ across devices, check:

1. **Floating-point operation order**: Ensure operations execute in a fixed sequence
2. **Reduction operations**: Sum/mean operations are particularly sensitive to order
3. **Fast math flags**: Disable compiler optimizations that violate IEEE-754
4. **Atomic operations**: CUDA atomics may have non-deterministic ordering

See [Reproducibility Principles](#6.4) for detailed guidance on maintaining reproducibility.

**Sources**: [examples/mnist_trainig.py:67-83](), [README.md:34-39]()

---

## Build System Integration

When adding backend implementations, the build system automatically compiles them during `pip install`.

### Build Configuration

The build process is configured in `setup.py` (not shown in provided files) and follows these steps:

1. **Compilation**: C++ files in `backend/cpu/` are compiled with OpenMP support
2. **CUDA Compilation**: `.cu` files in `backend/cuda/` are compiled if CUDA is available
3. **Binding**: pybind11 creates Python modules from the compiled libraries
4. **Installation**: Modules are installed into `repdl.backend.cpu` and `repdl.backend.cuda`

### Adding New Backend Files

When you add new `.cpp` or `.cu` files:

1. Create the implementation file in `backend/cpu/` or `backend/cuda/`
2. Add the function to the corresponding `bind.cpp` file
3. Run `pip install .` to rebuild

**Note**: The binding files [backend/cpu/bind.cpp]() and [backend/cuda/bind.cpp]() are referenced in the README but not provided in the file list. These files use pybind11's `PYBIND11_MODULE` macro to expose C++/CUDA functions to Python.

**Sources**: [README.md:23-27](), [README.md:49]()

---

## Common Extension Patterns

### Pattern 1: Simple Element-wise Operation

For operations that apply independently to each element:

1. **Dispatcher**: Check device and route [repdl/ops.py:122-123]()
2. **Backend**: May not need separate implementation if using dtype promotion
3. **Integration**: Can be called directly from higher-level code

Example: `sqrt` operation uses dtype promotion for reproducibility without custom backends.

### Pattern 2: Reduction Operation

For operations that aggregate values (sum, mean):

1. **Dispatcher**: Must route to reproducible backend [repdl/ops.py:126-157]()
2. **Backend**: Implement fixed-order reduction algorithms
3. **Variants**: Separate functions for different dimensionalities (`sum1d`, `sum2d_dim0`, etc.)

Example: Multiple `sum*` operations handle different tensor shapes.

### Pattern 3: Matrix Operations

For linear algebra operations:

1. **Dispatcher**: Route matrix multiplications [repdl/ops.py:106-112]()
2. **Backend**: Use reproducible BLAS libraries or custom kernels
3. **Parameters**: Include transpose flags for flexibility

Example: `mm` operation supports `transA` and `transB` flags.

### Pattern 4: Convolution Operations

For spatial operations with multiple outputs:

1. **Forward Dispatcher**: Route forward pass [repdl/ops.py:12-26]()
2. **Gradient Dispatchers**: Separate functions for input/weight gradients [repdl/ops.py:29-88]()
3. **Backend**: Implement im2col or direct convolution algorithms
4. **Parameters**: Handle stride, padding, groups

Example: `conv2d` has three separate dispatchers for forward, input gradient, and kernel gradient.

**Sources**: [repdl/ops.py:12-158]()

---

## Environment Setup for Development

Before implementing extensions, configure your development environment:

### Required Environment Variables

Set these variables as shown in [examples/mnist_trainig.py:42-43]():

```python
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
torch.use_deterministic_algorithms(True)
```

| Variable | Value | Purpose |
|----------|-------|---------|
| `CUBLAS_WORKSPACE_CONFIG` | `:4096:8` or `:16:8` | Allocates workspace for deterministic cuBLAS operations |
| `torch.use_deterministic_algorithms` | `True` | Forces PyTorch to use deterministic algorithms where possible |

### Development Tools

Ensure you have:
- C++ compiler with C++14 support (GCC 7+, Clang 5+, MSVC 2017+)
- CUDA Toolkit 11.0+ (for CUDA backend development)
- OpenMP support (for CPU parallelization)
- pybind11 (automatically installed as dependency)

### Testing Environment

For thorough reproducibility testing:
1. Access to both CPU and CUDA-capable systems
2. Multiple GPU models if possible (e.g., V100, A100)
3. Clean Python environment (consider using `venv` or `conda`)

**Sources**: [examples/mnist_trainig.py:41-43](), [README.md:21]()

---

This development guide provides the foundation for extending RepDL. The following sub-sections provide detailed instructions for specific extension types:

- [Adding Custom Operations](#6.1): Step-by-step guide for implementing new operations in the backend
- [Adding Custom Autograd Functions](#6.2): Creating differentiable functions using `torch.autograd.Function`
- [Adding Custom Layers](#6.3): Building PyTorch-compatible modules that use RepDL operations
- [Reproducibility Principles](#6.4): Deep dive into maintaining bitwise reproducibility

---

