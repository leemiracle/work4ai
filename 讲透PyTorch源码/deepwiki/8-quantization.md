# Quantization and Model Optimization

- aten/src/ATen/ParallelThreadPoolNative.cpp
- aten/src/ATen/core/alias_info.h
- aten/src/ATen/core/custom_class.cpp
- aten/src/ATen/core/ivalue.cpp
- aten/src/ATen/core/op_registration/op_registration.cpp
- aten/src/ATen/native/cpu/ReducedPrecisionFloatGemvFastPathKernel.cpp
- aten/src/ATen/native/mkldnn/Conv.h
- aten/src/ATen/native/mkldnn/Linear.h
- aten/src/ATen/native/quantized/cpu/OnednnUtils.h
- aten/src/ATen/native/quantized/cpu/fbgemm_utils.cpp
- aten/src/ATen/native/quantized/cpu/qconv.h
- aten/src/ATen/native/quantized/cpu/qlinear.cpp
- aten/src/ATen/native/quantized/cpu/qlinear.h
- aten/src/ATen/native/quantized/cpu/qlinear_prepack.cpp
- aten/src/ATen/native/quantized/cuda/EmbeddingBag.cu
- aten/src/ATen/native/quantized/qconv_unpack.cpp
- aten/src/ATen/templates/ATenOpList.cpp
- aten/src/ATen/xpu/XPUGeneratorImpl.cpp
- benchmarks/static_runtime/test_static_runtime.cc
- test/quantization/core/test_quantized_op.py
- torch/csrc/api/src/nn/modules/rnn.cpp
- torch/csrc/jit/passes/fixup_trace_scope_blocks.cpp
- torch/csrc/jit/passes/onnx/constant_map.cpp

Eager Mode Quantization
PT2E (PyTorch 2.0 Export) Quantization
TorchInductor

### High-Level Architecture

- Preparation : Inserting observers or fake-quantization modules to collect activation statistics.
- Calibration/Training : Running data through the model to determine quantization parameters like scale and zero-point.
- Conversion : Transforming the model into a quantized representation (e.g., quint8 , qint8 , or float8_e4m3fn ) and fusing operations.

#### Natural Language to Code Entity Mapping

```

```

Sources:
test/quantization/core/test_quantized_op.py 33-43
test/quantization/core/test_quantized_op.py 173-174
aten/src/ATen/native/quantized/qconv_unpack.cpp 51-82

## PT2E Quantization (Post-Training and QAT)

`ExportedProgram`
`torch.export`

- Workflow : It utilizes prepare_pt2e to insert observers and convert_pt2e to transform the graph into a quantized form.
- Backend Integration : The system supports multiple engines such as FBGEMM , QNNPACK , and ONEDNN via the global QEngine context aten/src/ATen/native/quantized/qconv_unpack.cpp 51-82
- Inductor Integration : Quantized graphs are lowered to Inductor, which can perform further fusions. For example, OneDNN support for quantized linear and convolution ops is handled via specialized primitive caches like LinearPrimitiveCache and ConvPrimitiveCache to optimize execution aten/src/ATen/native/quantized/cpu/OnednnUtils.h 51-94
- Advanced Formats : The stack includes specialized support for FP8 (e.g., e4m3fn ) test/quantization/core/test_quantized_op.py 173-185 and Int4 weight-only quantization for CPU aten/src/ATen/native/quantized/cpu/qlinear.h 45-50

PT2E Quantization (Post-Training and QAT)

Sources:
aten/src/ATen/native/quantized/cpu/OnednnUtils.h 51-111
test/quantization/core/test_quantized_op.py 173-185
aten/src/ATen/native/quantized/cpu/qlinear.h 45-50

## Eager Mode Quantization

`nn.Module`

- Key Components : Uses QConfig to define Observers such as PerChannelMinMaxObserver test/quantization/core/test_quantized_op.py 33
- Operator Implementation : Quantized operators are implemented in ATen, utilizing Quantizer objects and PackedParams to handle weights and biases. For example, PackedLinearWeight handles FBGEMM-specific prepacking and execution aten/src/ATen/native/quantized/cpu/qlinear_prepack.cpp 65-136
- Reference Numerics : The stack provides reference implementations like qlinear_ref to ensure correctness across different backends and precision formats test/quantization/core/test_quantized_op.py 117-133

Eager Mode Quantization

Sources:
test/quantization/core/test_quantized_op.py 33
aten/src/ATen/native/quantized/cpu/qlinear_prepack.cpp 65-136
test/quantization/core/test_quantized_op.py 117-133

## Model Optimization and Fusions

- Operator Fusions : The CPU backend supports fused quantized operations like apply_relu , apply_leaky_relu , and apply_tanh for linear and convolution layers via PackedLinearWeightsOnednn and PackedConvWeightsOnednn aten/src/ATen/native/quantized/cpu/OnednnUtils.h 143-160 aten/src/ATen/native/quantized/cpu/OnednnUtils.h 233-237
- Hardware Acceleration : PyTorch leverages libraries like FBGEMM for x86 CPUs to avoid overflows in 8-bit integer multiplications (e.g., using vpmaddubsw instruction logic) test/quantization/core/test_quantized_op.py 79-87
- GPU Quantization : Support extends to CUDA for operations like EmbeddingBag , utilizing specialized kernels like embedding_bag_nbits_rowwise_offsets_kernel for 4-bit and 8-bit rowwise quantization aten/src/ATen/native/quantized/cuda/EmbeddingBag.cu 89-167

### System Entity Mapping: Quantized Execution Stack

```

```

Sources:
aten/src/ATen/native/quantized/cpu/qlinear_prepack.cpp 65-186
aten/src/ATen/native/quantized/cpu/OnednnUtils.h 35-50
aten/src/ATen/native/quantized/cpu/qlinear.cpp 46-59

## Pass Infrastructure and Observability

- Custom Class Registration : Quantized parameters (like prepacked weights) are often stored as custom C++ classes registered via torch::registerCustomClass to ensure they can be serialized and managed by the JIT/Export runtimes aten/src/ATen/core/custom_class.cpp 68-78
- Memory Management : The system provides utilities to create specialized tensors, such as MakeStridedQTensorCPU and MakeEmptyAffineQuantizedChannelsLast3dTensor , to handle memory layout requirements for optimized kernels aten/src/ATen/native/quantized/cpu/fbgemm_utils.cpp 148-193

Sources:
aten/src/ATen/core/custom_class.cpp 68-78
aten/src/ATen/native/quantized/cpu/fbgemm_utils.cpp 148-193

###
