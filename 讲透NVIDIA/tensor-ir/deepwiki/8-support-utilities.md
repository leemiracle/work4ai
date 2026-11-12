<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/tensor-ir · page 8 Support Utilities · fetched 2026-10-26 -->

# Support Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/tensor_ir/Utils/Utils.h](include/tensor_ir/Utils/Utils.h)
- [lib/Utils/Utils.cpp](lib/Utils/Utils.cpp)

</details>



The support utilities layer provides shared infrastructural code used across the TensorIR compiler passes, lowering pipelines, and runtime modules. It encompasses tensor descriptor manipulation, shape and stride math, layout attribute queries, and macro-based error propagation mechanics.

For deep technical details on specific components, refer to the child pages:
- [Utils Library](#8.1)
- [Status and Error Handling](#8.2)

```mermaid
graph TD
  SupportLayer[""Support Utilities Layer""]
  SupportLayer --> UtilsLib[""Utils Library (include/tensor_ir/Utils/Utils.h)""]
  SupportLayer --> SupportLib[""Status & Error Handling (include/tensor_ir/Support)""]
  UtilsLib --> StrideFn[""getStrideFromGraph()""]
  UtilsLib --> AlignFn[""getAlignmentFromGraph()""]
  UtilsLib --> Desc[""TensorDescriptor struct""]
  SupportLib --> Macros[""MLIR_ASSIGN_OR_RETURN()""]
  SupportLib --> StatusCheck[""MLIR_RETURN_IF_ERROR()""]
```
Sources: `include/tensor_ir/Utils/Utils.h:1-136`, `lib/Utils/Utils.cpp:1-102`

---

## 8.1 Utils Library

The Utils library provides core helper functions and data structures for interacting with graph inputs and outputs, querying memory alignment, deriving tensor strides, and parsing layout configurations. These utilities are defined in `include/tensor_ir/Utils/Utils.h` and implemented in `lib/Utils/Utils.cpp`.

Key capabilities provided by the Utils library include:
- **Graph Stride and Alignment Queries**: Extracting physical layouts, strides, and memory alignment constraints from `GraphOp` signatures via `getStrideFromGraph` and `getAlignmentFromGraph` [include/tensor_ir/Utils/Utils.h:88-91](), [lib/Utils/Utils.cpp:58-158]().
- **Tensor Descriptors**: Encapsulating per-dimension sizes, strides, dynamic dimension handling, alignment, and TMA (Tensor Memory Accelerator) access constraints in the `TensorDescriptor` struct [include/tensor_ir/Utils/Utils.h:134-136]().
- **Multi-Output Layout Helpers**: Resolving ABI-ordered result layouts and physical output views using `getResultLayouts`, `getResultViews`, and `deriveResultFixedTileSizes` [include/tensor_ir/Utils/Utils.h:107-123]().

For detailed information on shape and stride math, environment variable parsing, and implementation details, see [Utils Library](#8.1).

Sources: `include/tensor_ir/Utils/Utils.h:1-254`, `lib/Utils/Utils.cpp:1-534`

---

## 8.2 Status and Error Handling

TensorIR uses robust error handling macros and status propagation primitives to manage fallible operations across MLIR passes and runtime layers. Rather than relying solely on exceptions, operations return status or failure indicators integrated cleanly with MLIR's `LogicalResult` and `FailureOr<T>` constructs.

Important error handling features include:
- **Error Propagation Macros**: `MLIR_RETURN_IF_ERROR` and `MLIR_ASSIGN_OR_RETURN` (supporting arity dispatch and custom error messages) for simplifying control flow when calling fallible functions [include/tensor_ir/Utils/Utils.h:32-85]().
- **Diagnostics Conversion**: Interfacing between low-level compiler status codes and MLIR diagnostic engines (`emitError`) at API boundaries.

For detailed information on `Status`/`StatusOr` semantics and diagnostic translation pipelines, see [Status and Error Handling](#8.2).

Sources: `include/tensor_ir/Utils/Utils.h:32-85`

---

