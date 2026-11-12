<!-- source: DeepWiki mcp.deepwiki.com · repo intel/intel-extension-for-pytorch · page 3 Core Optimization Features · fetched 2026-10-21 -->

# Core Optimization Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CMakeLists.txt](CMakeLists.txt)
- [intel_extension_for_pytorch/__init__.py](intel_extension_for_pytorch/__init__.py)
- [intel_extension_for_pytorch/frontend.py](intel_extension_for_pytorch/frontend.py)
- [intel_extension_for_pytorch/nn/utils/_model_convert.py](intel_extension_for_pytorch/nn/utils/_model_convert.py)
- [intel_extension_for_pytorch/nn/utils/_parameter_wrapper.py](intel_extension_for_pytorch/nn/utils/_parameter_wrapper.py)
- [intel_extension_for_pytorch/nn/utils/_weight_cast.py](intel_extension_for_pytorch/nn/utils/_weight_cast.py)
- [intel_extension_for_pytorch/nn/utils/_weight_prepack.py](intel_extension_for_pytorch/nn/utils/_weight_prepack.py)
- [intel_extension_for_pytorch/optim/_functional.py](intel_extension_for_pytorch/optim/_functional.py)
- [intel_extension_for_pytorch/optim/_lamb.py](intel_extension_for_pytorch/optim/_lamb.py)
- [intel_extension_for_pytorch/optim/_optimizer_utils.py](intel_extension_for_pytorch/optim/_optimizer_utils.py)
- [intel_extension_for_pytorch/quantization/_quantize.py](intel_extension_for_pytorch/quantization/_quantize.py)
- [intel_extension_for_pytorch/utils/weight_only_quantization.py](intel_extension_for_pytorch/utils/weight_only_quantization.py)
- [setup.py](setup.py)
- [tests/cpu/common_utils.py](tests/cpu/common_utils.py)
- [tests/cpu/test_auto_channels_last.py](tests/cpu/test_auto_channels_last.py)
- [tests/cpu/test_deepspeed.py](tests/cpu/test_deepspeed.py)
- [tests/cpu/test_ipex_optimize.py](tests/cpu/test_ipex_optimize.py)
- [tests/cpu/test_optimizer.py](tests/cpu/test_optimizer.py)
- [tests/cpu/test_weight_cast.py](tests/cpu/test_weight_cast.py)

</details>



This page describes the main performance optimization mechanisms provided by Intel Extension for PyTorch (IPEX). These features are designed to accelerate PyTorch models on Intel CPUs by applying model- and operator-level enhancements, including memory layout changes, operator fusion, mixed precision, and kernel selection. For LLM-specific optimizations, see page [5]. For quantization, see page [4].

## System Overview and Code Mapping

The following diagram shows how the main optimization systems in IPEX are orchestrated by the `ipex.optimize` function, and how these map to code entities:

```mermaid
flowchart TD
    "UserModel[\"torch.nn.Module\"]" --> "ipex.optimize[\"intel_extension_for_pytorch.frontend.optimize\"]"
    "ipex.optimize" --> "WeightPrepack[\"nn.utils._weight_prepack.weight_prepack_with_ipex\"]"
    "ipex.optimize" --> "JITFusion[\"JIT Fusion System\"]"
    "ipex.optimize" --> "DtypeCast[\"nn.utils._weight_cast.weight_dtype_convert_with_ipex\"]"
    "ipex.optimize" --> "OptimizerFusion[\"optim._optimizer_utils.optimizer_fusion\"]"
    "ipex.optimize" --> "ChannelsLast[\"frontend._convert_convNd_deconvNd_weight_memory_format\"]"
    "ipex.optimize" --> "BNFolding[\"torch.fx.experimental.optimization.fuse\"]"
    "ipex.optimize" --> "AutoKernel[\"cpu._auto_kernel_selection._enable_dnnl\"]"
    "ipex.optimize" --> "TorchCompile[\"torch._dynamo.allow_in_graph\"]"
    "WeightPrepack" --> "OptimizedModel[\"IPEX-optimized nn.Module\"]"
    "JITFusion" --> "OptimizedModel"
    "DtypeCast" --> "OptimizedModel"
    "OptimizerFusion" --> "OptimizedOptimizer[\"IPEX-optimized Optimizer\"]"
    "ChannelsLast" --> "OptimizedModel"
    "BNFolding" --> "OptimizedModel"
    "AutoKernel" --> "OptimizedModel"
    "TorchCompile" --> "OptimizedModel"
    "OptimizedModel" -.-> "Training[\"Training Workloads\"]"
    "OptimizedOptimizer" -.-> "Training"
    "OptimizedModel" -.-> "Inference[\"Inference Workloads\"]"
```

Sources:
- [intel_extension_for_pytorch/frontend.py:169-609]()
- [intel_extension_for_pytorch/nn/utils/_weight_prepack.py:20-641]()

## The `ipex.optimize` Function

The `ipex.optimize` function is the main entry point for applying IPEX's core optimizations. It orchestrates model and optimizer transformations for both inference and training, based on user-specified parameters.

### Decision Flow and Code Mapping

```mermaid
flowchart TD
    "Start[\"ipex.optimize(model, dtype, optimizer, ...)\"]" --> "CheckMode[\"model.training?\"]"
    "CheckMode" -->|"True"| "TrainingPath[\"Training Optimizations\"]"
    "CheckMode" -->|"False"| "InferencePath[\"Inference Optimizations\"]"

    "InferencePath" --> "ConvBNFolding[\"conv_bn_folding\"]"
    "InferencePath" --> "LinearBNFolding[\"linear_bn_folding\"]"
    "InferencePath" --> "DropoutReplace[\"replace_dropout_with_identity\"]"
    "InferencePath" --> "DtypeCast[\"_model_convert.convert_model_data_type\"]"
    "InferencePath" --> "WeightPrepack[\"weight_prepack_with_ipex\"]"
    "InferencePath" --> "ChannelsLast[\"_convert_convNd_deconvNd_weight_memory_format\"]"
    "InferencePath" --> "GraphMode[\"graph_mode\"]"

    "TrainingPath" --> "DtypeCastTrain[\"_weight_cast.weight_dtype_convert_with_ipex\"]"
    "TrainingPath" --> "SplitMasterWeight[\"split_master_weight_for_bf16\"]"
    "TrainingPath" --> "FusedOptimizer[\"optimizer_fusion\"]"

    "BothPaths[\"Common Steps\"]" --> "AutoKernel[\"auto_kernel_selection\"]"
    "BothPaths" --> "TorchCompile[\"torch._dynamo.allow_in_graph\"]"
    "BothPaths" --> "Return[\"Return optimized model/optimizer\"]"
    "InferencePath" --> "BothPaths"
    "TrainingPath" --> "BothPaths"
```

#### Key Parameters

| Parameter                      | Description                                                                 |
|---------------------------------|-----------------------------------------------------------------------------|
| `model`                        | PyTorch model to optimize (`torch.nn.Module`)                               |
| `dtype`                        | Target dtype for model parameters (e.g., `torch.bfloat16`, `torch.float16`) |
| `optimizer`                    | PyTorch optimizer for training                                              |
| `level`                        | Optimization level: `"O0"` (none), `"O1"` (all)                             |
| `inplace`                      | Whether to optimize in-place                                                |
| `conv_bn_folding`              | Fold Conv+BatchNorm (inference only)                                        |
| `linear_bn_folding`            | Fold Linear+BatchNorm (inference only)                                      |
| `weights_prepack`              | Enable weight prepacking                                                    |
| `replace_dropout_with_identity`| Replace Dropout with Identity (inference only)                              |
| `optimize_lstm`                | Replace LSTM with IPEX LSTM                                                 |
| `split_master_weight_for_bf16` | Use split master weights for BF16 training                                  |
| `fuse_update_step`             | Use fused parameter update for training                                     |
| `auto_kernel_selection`        | Enable auto kernel selection                                                |
| `sample_input`                 | Sample input for block format selection                                     |
| `graph_mode`                   | Enable graph capture                                                        |
| `concat_linear`                | Enable concatenated linear optimization                                     |

For a full API reference, see [intel_extension_for_pytorch/frontend.py:169-609]().

Sources:
- [intel_extension_for_pytorch/frontend.py:169-609]()
- [tests/cpu/test_ipex_optimize.py:130-588]()

## Weight Prepacking

Weight prepacking is a core optimization that converts model weights to a blocked or channels-last memory layout before execution. This reduces runtime memory format conversions and enables direct use of optimized compute kernels.

### Code Entity Mapping

```mermaid
flowchart TD
    "ipex.optimize" --> "weight_prepack_with_ipex[\"nn.utils._weight_prepack.weight_prepack_with_ipex\"]"
    "weight_prepack_with_ipex" --> "ModuleTypeCheck[\"Check module type\"]"
    "ModuleTypeCheck" -->|"torch.nn.Linear"| "_IPEXLinear[\"_IPEXLinear\"]"
    "ModuleTypeCheck" -->|"torch.nn.Conv2d"| "_IPEXConv2d[\"_IPEXConv2d\"]"
    "ModuleTypeCheck" -->|"torch.nn.Conv3d"| "_IPEXConv3d[\"_IPEXConv3d\"]"
    "ModuleTypeCheck" -->|"torch.nn.Conv1d"| "_IPEXConv1d[\"_IPEXConv1d\"]"
    "ModuleTypeCheck" -->|"torch.nn.ConvTranspose2d"| "_IPEXConvTranspose2d[\"_IPEXConvTranspose2d\"]"
    "ModuleTypeCheck" -->|"torch.nn.ConvTranspose3d"| "_IPEXConvTranspose3d[\"_IPEXConvTranspose3d\"]"
    "_IPEXLinear" --> "BlockedWeights[\"BlockedParameter\"]"
    "_IPEXConv2d" --> "BlockedWeights"
    "_IPEXConv3d" --> "BlockedWeights"
    "_IPEXConv1d" --> "BlockedWeights"
    "_IPEXConvTranspose2d" --> "BlockedWeights"
    "_IPEXConvTranspose3d" --> "BlockedWeights"
    "BlockedWeights" --> "OptimizedLayout[\"Optimized memory layout for kernel\"]"
```

#### Example: Linear Weight Blocking

- Original: `[out_features, in_features]`
- Blocked: `[out_features/16, in_features/64, 16, 64]` (for BF16, on supported CPUs)

This enables efficient vectorization and cache usage.

Sources:
- [intel_extension_for_pytorch/nn/utils/_weight_prepack.py:20-91]()
- [intel_extension_for_pytorch/nn/utils/_weight_prepack.py:469-600]()
- [tests/cpu/test_ipex_optimize.py:368-404]()

## JIT Fusion System

The JIT Fusion system in IPEX identifies and fuses common operator patterns (such as Conv+BN+ReLU) into single, more efficient kernels. This reduces memory bandwidth and kernel launch overhead.

### Fusion Patterns and Code Mapping

```mermaid
flowchart TD
    "JITFusionSystem[\"JIT Fusion System\"]" --> "PatternRecognition[\"Pattern Recognition\"]"
    "PatternRecognition" --> "ConvBNReLU[\"Conv+BatchNorm+ReLU\"]"
    "PatternRecognition" --> "LinearReLU[\"Linear+ReLU\"]"
    "PatternRecognition" --> "ConvEltwise[\"Conv+Eltwise\"]"
    "PatternRecognition" --> "LinearEltwise[\"Linear+Eltwise\"]"
    "PatternRecognition" --> "ConvSum[\"Conv+Sum\"]"
    "PatternRecognition" --> "LinearBN[\"Linear+BatchNorm\"]"
    "PatternRecognition" --> "ConvReshape[\"Conv+Reshape\"]"
    "PatternRecognition" --> "ConvSwish[\"Conv+Swish\"]"
    "ConvBNReLU" --> "FusedKernel[\"Fused Implementation\"]"
    "LinearReLU" --> "FusedKernel"
    "ConvEltwise" --> "FusedKernel"
    "LinearEltwise" --> "FusedKernel"
    "ConvSum" --> "FusedKernel"
    "LinearBN" --> "FusedKernel"
    "ConvReshape" --> "FusedKernel"
    "ConvSwish" --> "FusedKernel"
    "FusedKernel" --> "Benefits[\"Reduced memory, better vectorization, fewer launches\"]"
```

#### Supported Elementwise Fusions

| Operation     | Description         | BF16 Support |
|---------------|---------------------|--------------|
| relu          | ReLU activation     | Yes          |
| sigmoid       | Sigmoid activation  | Yes          |
| tanh          | Tanh activation     | Yes          |
| swish         | Swish/SiLU          | Yes          |
| gelu          | GELU activation     | Yes          |
| hardtanh      | HardTanh            | Yes          |
| hardswish     | HardSwish           | Yes          |
| hardsigmoid   | HardSigmoid         | Yes          |
| leaky_relu    | LeakyReLU           | Yes          |
| elu           | ELU                 | Yes          |
| abs           | Absolute value      | Yes          |
| square        | Square              | Yes          |
| pow           | Power               | Yes          |
| log           | Logarithm           | Yes          |
| sqrt          | Square root         | Yes          |
| exp           | Exponential         | Yes          |

Sources:
- [tests/cpu/test_jit.py:116-191]()

## Mixed Precision Support (BF16/FP16)

IPEX supports mixed precision (BF16/FP16) for both inference and training. This is achieved by casting model weights and, for training, using master weight strategies to maintain numerical stability.

### Mixed Precision Strategies

```mermaid
flowchart TD
    "MixedPrecision" --> "TrainingMode[\"model.training?\"]"
    "TrainingMode" -->|"True"| "MasterWeight[\"Master Weight Strategies\"]"
    "TrainingMode" -->|"False"| "LowPrecisionCast[\"Convert to BF16/FP16\"]"
    "MasterWeight" --> "RegularMaster[\"FP32 master weights\"]"
    "MasterWeight" --> "SplitMaster[\"Split master weight (BF16)\"]"
    "RegularMaster" --> "Flow1[\"Cast model weights to BF16/FP16, keep FP32 master, update in FP32, sync back\"]"
    "SplitMaster" --> "Flow2[\"Split across two BF16 tensors, maintain FP32 precision, less memory\"]"
    "LowPrecisionCast" --> "Modules[\"Convert Linear, Conv, LSTM (inference), Embedding (inference)\"]"
    "Modules" --> "BNRemain[\"BatchNorm stays FP32\"]"
```

- For training, the `split_master_weight_for_bf16` parameter selects between regular and split master weight strategies.
- For inference, supported modules are cast to the target dtype.

Sources:
- [intel_extension_for_pytorch/nn/utils/_weight_cast.py:8-87]()
- [tests/cpu/test_weight_cast.py:56-81]()
- [tests/cpu/test_ipex_optimize.py:203-231]()

## Optimizer Fusion

IPEX provides fused implementations of common optimizers, reducing memory traffic and improving update speed, especially for large models.

### Supported Optimizers and Code Mapping

```mermaid
flowchart TD
    "optimizer_fusion[\"optim._optimizer_utils.optimizer_fusion\"]" --> "SGD[\"torch.optim.SGD\"]"
    "optimizer_fusion" --> "Adagrad[\"torch.optim.Adagrad\"]"
    "optimizer_fusion" --> "Adam[\"torch.optim.Adam\"]"
    "optimizer_fusion" --> "Lamb[\"ipex.optim.Lamb\"]"
    "optimizer_fusion" --> "Lars[\"ipex.optim.Lars\"]"
    "optimizer_fusion" --> "AdamW[\"torch.optim.AdamW\"]"
    "optimizer_fusion" --> "FusedStep[\"Patch .step() to fused kernel\"]"
    "FusedStep" --> "Benefits[\"Reduced memory, vectorized update, cache efficiency\"]"
    "FusedStep" --> "MixedPrecision[\"BF16/FP16: convert grad to FP32, update, sync back\"]"
```

- Fused optimizers are selected and patched in `optim._optimizer_utils.optimizer_fusion`.
- Mixed precision is supported by converting gradients to FP32 for the update step.

Sources:
- [intel_extension_for_pytorch/optim/_optimizer_utils.py:20-49]()
- [intel_extension_for_pytorch/optim/_optimizer_utils.py:360-391]()
- [intel_extension_for_pytorch/optim/_functional.py:473-534]()
- [tests/cpu/test_optimizer.py:84-124]()

## Channels Last Memory Format

IPEX can automatically convert convolution weights to channels last memory format (NHWC for 2D) for improved cache and vectorization efficiency.

```mermaid
flowchart TD
    "AutoChannelsLast[\"frontend._convert_convNd_deconvNd_weight_memory_format\"]" --> "Conv1d[\"Conv1d → channels_last_1d\"]"
    "AutoChannelsLast" --> "Conv2d[\"Conv2d → channels_last\"]"
    "AutoChannelsLast" --> "Conv3d[\"Conv3d → channels_last_3d\"]"
    "AutoChannelsLast" --> "ConvTranspose1d[\"ConvTranspose1d → channels_last_1d\"]"
    "AutoChannelsLast" --> "ConvTranspose2d[\"ConvTranspose2d → channels_last\"]"
    "AutoChannelsLast" --> "ConvTranspose3d[\"ConvTranspose3d → channels_last_3d\"]"
    "Conv1d" --> "Benefits[\"Improved cache, vectorization, reduced memory traffic\"]"
    "Conv2d" --> "Benefits"
    "Conv3d" --> "Benefits"
    "ConvTranspose1d" --> "Benefits"
    "ConvTranspose2d" --> "Benefits"
    "ConvTranspose3d" --> "Benefits"
```

Sources:
- [intel_extension_for_pytorch/frontend.py:95-112]()
- [intel_extension_for_pytorch/frontend.py:605-612]()

## BatchNorm Folding

IPEX can fold BatchNorm layers into preceding Conv or Linear layers during inference, reducing computation and memory accesses.

```mermaid
flowchart TD
    "BatchNormFolding[\"BatchNorm Folding\"]" --> "ConvBN[\"Conv+BatchNorm\"]"
    "BatchNormFolding" --> "LinearBN[\"Linear+BatchNorm\"]"
    "ConvBN" --> "FoldedConv[\"Folded Conv (adjusted weights/bias)\"]"
    "LinearBN" --> "FoldedLinear[\"Folded Linear (adjusted weights/bias)\"]"
    "FoldedConv" --> "Benefits[\"Reduced compute, fewer accesses, smaller model\"]"
    "FoldedLinear" --> "Benefits"
```

Sources:
- [tests/cpu/test_ipex_optimize.py:130-202]()

## Auto Kernel Selection

Auto Kernel Selection dynamically chooses the optimal kernel implementation (oneDNN, TPP, MKL) for operations like Linear and Conv, based on input shape, dtype, and hardware.

```mermaid
flowchart TD
    "AutoKernelSelection[\"auto_kernel_selection\"]" --> "InputFactors[\"Batch size, shape, dtype\"]"
    "InputFactors" --> "KernelLogic[\"Selection logic\"]"
    "KernelLogic" --> "oneDNN[\"oneDNN kernel\"]"
    "KernelLogic" --> "TPP[\"TPP kernel\"]"
    "KernelLogic" --> "MKL[\"MKL GEMM\"]"
    "oneDNN" --> "OptimalKernel[\"Select optimal kernel\"]"
    "TPP" --> "OptimalKernel"
    "MKL" --> "OptimalKernel"
```

Sources:
- [intel_extension_for_pytorch/nn/utils/_weight_prepack.py:53-89]()
- [intel_extension_for_pytorch/frontend.py:401-407]()
- [tests/cpu/test_ipex_optimize.py:486-516]()

## torch.compile Integration

IPEX integrates with PyTorch's `torch.compile` and `torch._dynamo` to enable graph-level optimizations and allow IPEX-optimized modules to participate in graph capture and compilation.

```mermaid
flowchart TD
    "torch.compile" --> "torch._dynamo.allow_in_graph"
    "torch._dynamo.allow_in_graph" --> "_IPEXConv1d"
    "torch._dynamo.allow_in_graph" --> "_IPEXConv2d"
    "torch._dynamo.allow_in_graph" --> "_IPEXConv3d"
    "torch._dynamo.allow_in_graph" --> "_IPEXConvTranspose2d"
    "torch._dynamo.allow_in_graph" --> "_IPEXConvTranspose3d"
    "torch._dynamo.allow_in_graph" --> "_IPEXLinear"
    "torch._dynamo.allow_in_graph" --> "_LSTM"
    "_IPEXConv1d" --> "CompileFlow[\"torch.compile workflow\"]"
    "_IPEXConv2d" --> "CompileFlow"
    "_IPEXConv3d" --> "CompileFlow"
    "_IPEXConvTranspose2d" --> "CompileFlow"
    "_IPEXConvTranspose3d" --> "CompileFlow"
    "_IPEXLinear" --> "CompileFlow"
    "_LSTM" --> "CompileFlow"
    "CompileFlow" --> "GraphCapture[\"Graph capture, fusion, codegen\"]"
```

Sources:
- [intel_extension_for_pytorch/frontend.py:575-590]()

## Summary

IPEX's core optimization features work together to deliver significant performance improvements for both training and inference on Intel hardware. The optimizations focus on:

1. **Memory Layout Optimization**: Weight prepacking and channels last format
2. **Operation Fusion**: JIT fusion and BatchNorm folding
3. **Mixed Precision**: BF16/FP16 support with efficient master weight strategies
4. **Compute Optimization**: Optimized kernels and fusion patterns
5. **Training Efficiency**: Optimizer fusion and split master weight

These optimizations can be easily applied to PyTorch models using the `ipex.optimize()` function, with different configurations available to balance performance and compatibility.

Sources:
- [intel_extension_for_pytorch/frontend.py:169-602]()

---

