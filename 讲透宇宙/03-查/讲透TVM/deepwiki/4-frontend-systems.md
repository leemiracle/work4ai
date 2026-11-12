> 来源: [https://deepwiki.com/apache/tvm/4-frontend-systems](https://deepwiki.com/apache/tvm/4-frontend-systems)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Frontend Systems

  Relevant source files 
 - [include/tvm/relax/attrs/image.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/attrs/image.h)
 - [include/tvm/relax/attrs/nn.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/attrs/nn.h)
 - [python/tvm/relax/frontend/onnx/onnx_frontend.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py)
 - [python/tvm/relax/frontend/torch/base_fx_graph_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py)
 - [python/tvm/relax/frontend/torch/exported_program_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py)
 - [python/tvm/relax/frontend/torch/fx_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py)
 - [python/tvm/relax/op/image/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/image/__init__.py)
 - [python/tvm/relax/op/image/image.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/image/image.py)
 - [python/tvm/relax/op/nn/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/nn/__init__.py)
 - [python/tvm/relax/op/nn/nn.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/nn/nn.py)
 - [python/tvm/relax/transform/legalize_ops/image.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/image.py)
 - [python/tvm/relax/transform/legalize_ops/nn.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py)
 - [python/tvm/topi/image/grid_sample.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/image/grid_sample.py)
 - [src/relax/op/image/resize.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/image/resize.cc)
 - [src/relax/op/image/resize.h](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/image/resize.h)
 - [src/relax/op/nn/nn.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/nn/nn.cc)
 - [src/relax/op/nn/nn.h](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/nn/nn.h)
 - [tests/python/relax/test_frontend_from_exported_program.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py)
 - [tests/python/relax/test_frontend_from_fx.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_fx.py)
 - [tests/python/relax/test_frontend_onnx.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_onnx.py)
 - [tests/python/relax/test_op_image.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_op_image.py)
 - [tests/python/relax/test_op_nn.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_op_nn.py)
 - [tests/python/relax/test_transform_legalize_ops_image.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_image.py)
 - [tests/python/relax/test_transform_legalize_ops_nn.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_nn.py)
 - [tests/python/relax/test_tvmscript_parser_op_image.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_tvmscript_parser_op_image.py)
 
  This page provides a high-level overview of TVM's frontend systems responsible for importing models from various deep learning frameworks into TVM's intermediate representations, primarily Relax IR. Frontends are the initial stage of the TVM compilation pipeline, translating framework-specific model formats and operators into TVM's IR form for subsequent optimization and code generation.

 
## Overview

 Frontend systems bridge external machine learning frameworks such as PyTorch, ONNX, TensorFlow, and others with TVM's internal IR. They parse model definitions, extract and convert parameters, and map framework-specific operators to TVM operators, enabling a unified compilation and optimization flow within TVM.

 The frontends aim to support rich model constructs, dynamic shapes, control flow, and symbolic dimension handling, ensuring faithful model representation in Relax IR.

 
### Diagram: High-Level Frontend Flow linking external models to Relax IR

 
```

```

 Sources: [python/tvm/relax/frontend/torch/fx_translator.py20-30](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py#L20-L30) [python/tvm/relax/frontend/torch/exported_program_translator.py21-42](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L21-L42) [python/tvm/relax/frontend/onnx/onnx_frontend.py18-37](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L18-L37)

 
## Subsystems and Their Relationships

 TVM provides several specialized frontends tailored for different model formats and frameworks. Most convert models to Relax IR, serving as a common graphical IR for subsequent compilation passes. The Relax IR may later be lowered to TensorIR (TIR) or S-TIR for low-level code generation.

 Below is an outline of the main frontend subsystems and their relationships to code entities:

 
### Diagram: Key Frontend Systems mapped to Code Entities

 
```

```

 Sources: [python/tvm/relax/frontend/torch/fx_translator.py31-40](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py#L31-L40) [python/tvm/relax/frontend/torch/exported_program_translator.py42-43](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L42-L43) [python/tvm/relax/frontend/onnx/onnx_frontend.py22-37](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L22-L37) [python/tvm/relax/transform/legalize_ops/nn.py31-57](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L57)

 
## Frontend Modules Overview

 
### PyTorch Frontend

 TVM supports PyTorch model import through two main entry points:

 
 - **FX Importer (`from_fx`)**: Translates PyTorch models symbolically traced with `torch.fx.symbolic_trace` into Relax IR [python/tvm/relax/frontend/torch/fx_translator.py31-32](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py#L31-L32)
 - **ExportedProgram Importer (`from_exported_program`)**: Supports importing PyTorch models exported with the PyTorch 2.0+ `torch.export` API [python/tvm/relax/frontend/torch/exported_program_translator.py42-43](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L42-L43) This is the modern path for handling dynamic shapes and complex ATEN decompositions.
 
 Both importers inherit from `BaseFXGraphImporter` [python/tvm/relax/frontend/torch/base_fx_graph_translator.py37-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L37-L52) and use a common infrastructure based on `relax.BlockBuilder` to generate Relax IR.

 For detailed design and usage, see [PyTorch Frontend](https://deepwiki.com/apache/tvm/4.2-pytorch-frontend).

 
### ONNX Frontend

 The ONNX frontend parses ONNX `ModelProto` objects and converts them into equivalent Relax functions via `from_onnx` [python/tvm/relax/frontend/onnx/onnx_frontend.py22-37](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L22-L37) It supports versioned operator converters that map ONNX graph nodes to Relax IR operations.

 Dynamic shape support is achieved by parsing symbolic dimension names into `tvm.tirx.Var` [python/tvm/relax/frontend/onnx/onnx_frontend.py162-177](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L162-L177)

 For comprehensive details, see [ONNX Frontend](https://deepwiki.com/apache/tvm/4.1-onnx-frontend).

 
### Other Model Format Importers

 TVM provides importers for several other popular model formats including TensorFlow Lite, Keras, MXNet, and PaddlePaddle. These importers enable a broad set of models to be compiled with TVM by mapping framework-specific operators to TVM's common operator inventory.

 Refer to [Other Model Format Importers](https://deepwiki.com/apache/tvm/4.3-other-model-format-importers) for implementation details.

 
### Relax nn.Module Frontend

 The Relax `nn.Module` frontend allows defining models directly in TVM using a PyTorch-like Python API. This is particularly useful for LLM development, as it includes specific modules for KV cache management and positional embeddings.

 Details on this frontend's API and usage can be found in [nn.Module Frontend](https://deepwiki.com/apache/tvm/4.4-nn.module-frontend).

 
---

 
## Common Frontend Themes and Concepts

 
### BlockBuilder-based Construction

 All Relax frontends leverage the `relax.BlockBuilder` API [python/tvm/relax/frontend/torch/base_fx_graph_translator.py49](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L49-L49) to incrementally build IR modules. This ensures that the generated IR is structurally valid and allows for immediate emission of dataflow blocks.

 
### Operator Conversion Maps

 Frontend importers maintain `convert_map` dictionaries [python/tvm/relax/frontend/torch/base_fx_graph_translator.py50-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L50-L52) that associate input operator names with specific conversion methods. For example, PyTorch's `sqrt` is mapped to `relax.op.sqrt` while handling integer-to-float promotion [python/tvm/relax/frontend/torch/exported_program_translator.py105-113](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L105-L113)

 
### Dynamic Shape and Symbolic Dimension Support

 Frontends parse symbolic dimension names into TIR variables. The ONNX frontend, for instance, uses `parse_shape_name` to convert complex dimension expressions into `tirx.Expr` [python/tvm/relax/frontend/onnx/onnx_frontend.py162-209](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L162-L209)

 
### Parameter Management

 Frontends provide utilities to detach and bind parameters. The `detach_params` utility [tests/python/relax/test_frontend_onnx.py155](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_onnx.py#L155-L155) allows separating the model graph from its weights, which can then be bound as constants using `relax.transform.BindParams` [tests/python/relax/test_frontend_from_exported_program.py61](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L61-L61)

 
### Type and DataType Conversion

 Frontends provide standardized mapping between framework-specific types and TVM dtypes. The `BaseFXGraphImporter._convert_data_type` method handles the mapping from `torch.dtype` to TVM strings like `"float32"`, `"int64"`, and `"bool"` [python/tvm/relax/frontend/torch/base_fx_graph_translator.py68-111](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L68-L111)

 
---

 
## Available Child Pages

 
 - [ONNX Frontend](https://deepwiki.com/apache/tvm/4.1-onnx-frontend) — ONNX model import covering Relay and Relax paths.
 - [PyTorch Frontend](https://deepwiki.com/apache/tvm/4.2-pytorch-frontend) — PyTorch import via Dynamo and ExportedProgram.
 - [Other Model Format Importers](https://deepwiki.com/apache/tvm/4.3-other-model-format-importers) — Importers for TFLite, Keras, MXNet, etc.
 - [nn.Module Frontend](https://deepwiki.com/apache/tvm/4.4-nn.module-frontend) — Python-native API for defining Relax models.
 
 
---

 
# Sources

 
 - [python/tvm/relax/frontend/torch/fx_translator.py20-120](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py#L20-L120)
 - [python/tvm/relax/frontend/torch/exported_program_translator.py21-124](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L21-L124)
 - [python/tvm/relax/frontend/torch/base_fx_graph_translator.py37-180](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L37-L180)
 - [python/tvm/relax/frontend/onnx/onnx_frontend.py18-209](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/onnx/onnx_frontend.py#L18-L209)
 - [python/tvm/relax/transform/legalize_ops/nn.py31-86](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L86)
 - [tests/python/relax/test_frontend_onnx.py148-168](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_onnx.py#L148-L168)
 - [tests/python/relax/test_frontend_from_exported_program.py50-64](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L50-L64)
