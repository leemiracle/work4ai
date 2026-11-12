<!-- source: DeepWiki mcp.deepwiki.com · repo intel/neural-compressor · page 5 Framework Adaptors · fetched 2026-10-21 -->

# Framework Adaptors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/add_new_adaptor.md](docs/source/add_new_adaptor.md)
- [docs/source/add_new_data_type.md](docs/source/add_new_data_type.md)
- [docs/source/calibration.md](docs/source/calibration.md)
- [docs/source/examples_readme.md](docs/source/examples_readme.md)
- [docs/source/framework_yaml.md](docs/source/framework_yaml.md)
- [docs/source/infrastructure.md](docs/source/infrastructure.md)
- [docs/source/mixed_precision.md](docs/source/mixed_precision.md)
- [docs/source/publication_list.md](docs/source/publication_list.md)
- [docs/source/quantization.md](docs/source/quantization.md)
- [docs/source/quantization_mixed_precision.md](docs/source/quantization_mixed_precision.md)
- [examples/README.md](examples/README.md)
- [neural_compressor/benchmark.py](neural_compressor/benchmark.py)
- [neural_compressor/config.py](neural_compressor/config.py)
- [neural_compressor/mix_precision.py](neural_compressor/mix_precision.py)
- [neural_compressor/model/model.py](neural_compressor/model/model.py)
- [neural_compressor/quantization.py](neural_compressor/quantization.py)
- [neural_compressor/training.py](neural_compressor/training.py)
- [neural_compressor/utils/utility.py](neural_compressor/utils/utility.py)
- [test/adaptor/pytorch_adaptor/test_adaptor_security.py](test/adaptor/pytorch_adaptor/test_adaptor_security.py)

</details>



## Purpose and Scope

Framework Adaptors serve as the abstraction layer between Intel® Neural Compressor's tuning strategies and native framework quantization APIs. This document covers the overall adaptor architecture, the common APIs that all adaptors implement, and the framework capability system. For detailed information about specific framework implementations, see [PyTorch Adaptor](#5.1), [TensorFlow Adaptor](#5.2), and [ONNX Runtime Adaptor](#5.3).

The adaptor layer enables Neural Compressor to support multiple deep learning frameworks (TensorFlow, PyTorch, ONNX Runtime) and their extensions (IPEX, ITEX, TensorRT) through a unified interface. Each adaptor translates framework-agnostic tuning configurations into framework-specific quantization operations.

## Adaptor Architecture Overview

### Position in System Architecture

Framework Adaptors occupy a critical position in the Neural Compressor architecture, bridging the high-level tuning strategies with low-level framework implementations:

```mermaid
graph TB
    subgraph "Configuration Layer"
        UserConfig["User Configuration<br/>PostTrainingQuantConfig<br/>QuantizationAwareTrainingConfig"]
    end
    
    subgraph "Strategy Layer"
        Strategy["Strategy<br/>BasicStrategy, MSEStrategy, etc."]
        TuningSpace["TuningSpace<br/>Build from capability"]
        TuningConfig["Tuning Configuration<br/>tune_cfg dict"]
    end
    
    subgraph "Adaptor Layer"
        AdaptorFactory["FRAMEWORKS Registry<br/>neural_compressor.adaptor"]
        PyTorchAdaptor["PyTorchAdaptor"]
        TensorFlowAdaptor["TensorFlowAdaptor"]
        ONNXAdaptor["ONNXRTAdaptor"]
        
        AdaptorFactory --> PyTorchAdaptor
        AdaptorFactory --> TensorFlowAdaptor
        AdaptorFactory --> ONNXAdaptor
    end
    
    subgraph "Framework Layer"
        PyTorchFramework["torch.quantization<br/>IPEX APIs"]
        TFFramework["TensorFlow Graph APIs<br/>ITEX APIs"]
        ONNXFramework["ONNX Runtime APIs<br/>Multiple Execution Providers"]
    end
    
    UserConfig --> Strategy
    Strategy --> TuningSpace
    TuningSpace -.query_fw_capability.-> PyTorchAdaptor
    TuningSpace -.query_fw_capability.-> TensorFlowAdaptor
    TuningSpace -.query_fw_capability.-> ONNXAdaptor
    
    Strategy --> TuningConfig
    TuningConfig -.quantize.-> PyTorchAdaptor
    TuningConfig -.quantize.-> TensorFlowAdaptor
    TuningConfig -.quantize.-> ONNXAdaptor
    
    PyTorchAdaptor --> PyTorchFramework
    TensorFlowAdaptor --> TFFramework
    ONNXAdaptor --> ONNXFramework
```

**Sources:** [neural_compressor/quantization.py:158-200](), [docs/source/add_new_adaptor.md:20-42]()

### Adaptor Lifecycle

The adaptor follows a well-defined lifecycle during the quantization process:

```mermaid
sequenceDiagram
    participant User
    participant QuantizationAPI as quantization.fit()
    participant Strategy
    participant Adaptor
    participant Framework
    
    User->>QuantizationAPI: Call with model, config, dataloader
    QuantizationAPI->>Strategy: Initialize strategy with config
    
    Note over Strategy,Adaptor: Phase 1: Capability Query
    Strategy->>Adaptor: query_fw_capability(model)
    Adaptor->>Adaptor: Parse framework YAML
    Adaptor->>Framework: Inspect model structure
    Adaptor-->>Strategy: Return capability dict<br/>{opwise, optypewise}
    Strategy->>Strategy: Build TuningSpace from capability
    
    Note over Strategy,Adaptor: Phase 2: Iterative Tuning
    loop For each tuning iteration
        Strategy->>Strategy: Generate next tune_cfg
        Strategy->>Adaptor: quantize(tune_cfg, model, dataloader)
        Adaptor->>Framework: Insert observers/fake_quant
        Adaptor->>Framework: Run calibration
        Adaptor->>Framework: Convert to quantized model
        Adaptor-->>Strategy: Return quantized model
        Strategy->>Strategy: Evaluate accuracy
    end
    
    Strategy-->>QuantizationAPI: Return best quantized model
    QuantizationAPI-->>User: Return optimized model
```

**Sources:** [neural_compressor/quantization.py:33-241](), [docs/source/add_new_adaptor.md:20-43]()

## Framework Support Matrix

Neural Compressor supports multiple frameworks through dedicated adaptors. The framework detection and adaptor selection happens automatically:

| Framework | Adaptor Class | Backend Options | Model Detection |
|-----------|--------------|-----------------|-----------------|
| PyTorch | `PyTorchAdaptor` | `default` (Eager/FX), `ipex` | `torch.nn.Module`, `torch.fx.GraphModule`, `torch.jit.RecursiveScriptModule` |
| TensorFlow | `TensorflowAdaptor` | `default`, `itex` | `tf.Graph`, GraphDef, SavedModel, Keras Model |
| ONNX Runtime | `ONNXRTAdaptor` | `default`, `onnxrt_trt_ep`, `onnxrt_cuda_ep`, `onnxrt_dnnl_ep`, `onnxrt_dml_ep` | ONNX ModelProto, `.onnx` file path |

**Sources:** [neural_compressor/model/model.py:51-63](), [neural_compressor/model/model.py:66-147]()

### Adaptor Registry and Factory

The `FRAMEWORKS` registry maps framework names to adaptor classes:

```mermaid
graph LR
    subgraph "Adaptor Registry"
        Registry["FRAMEWORKS dict<br/>in neural_compressor.adaptor"]
    end
    
    subgraph "Framework Keys"
        TFKey["'tensorflow'<br/>'tensorflow_itex'<br/>'tensorflow_qat'"]
        PTKey["'pytorch'<br/>'pytorch_ipex'<br/>'pytorch_fx'"]
        ONNXKey["'onnxruntime'<br/>'onnxrt_qlinearops'<br/>'onnxrt_qdq'"]
    end
    
    subgraph "Adaptor Classes"
        TFAdaptor["TensorflowAdaptor"]
        PTAdaptor["PyTorchAdaptor"]
        IPEXAdaptor["PyTorchIPEXAdaptor"]
        ONNXAdaptor["ONNXRTAdaptor"]
    end
    
    TFKey --> Registry
    PTKey --> Registry
    ONNXKey --> Registry
    
    Registry --> TFAdaptor
    Registry --> PTAdaptor
    Registry --> IPEXAdaptor
    Registry --> ONNXAdaptor
```

The framework is automatically detected using `get_model_fwk_name()` which inspects the model object type and attempts to load it with each framework's APIs.

**Sources:** [neural_compressor/model/model.py:66-147](), [neural_compressor/benchmark.py:162-178]()

## Core Adaptor APIs

Every adaptor must implement a standard interface. The key methods are:

### 1. query_fw_capability

Returns the quantization capabilities of the framework for a given model.

**Method Signature:**
```python
def query_fw_capability(self, model) -> dict
```

**Return Format:**
```python
{
    'opwise': {
        ('layer1.0.conv1', 'Conv2d'): [
            {
                'weight': {
                    'dtype': ['int8'],
                    'scheme': ['sym'],
                    'granularity': ['per_channel'],
                    'algorithm': ['minmax']
                },
                'activation': {
                    'dtype': ['uint8'],
                    'scheme': ['asym'],
                    'granularity': ['per_tensor'],
                    'algorithm': ['minmax', 'kl']
                }
            },
            {'weight': {'dtype': ['fp32']}, 'activation': {'dtype': ['fp32']}},
            {'weight': {'dtype': ['bf16']}, 'activation': {'dtype': ['bf16']}}
        ],
        # ... other ops
    },
    'optypewise': {
        'Conv2d': {
            'weight': {
                'dtype': ['int8'],
                'scheme': ['sym'],
                'granularity': ['per_channel'],
                'algorithm': ['minmax']
            },
            'activation': {
                'dtype': ['uint8'],
                'scheme': ['asym'],
                'granularity': ['per_tensor'],
                'algorithm': ['minmax', 'kl']
            }
        },
        # ... other op types
    }
}
```

The capability dictionary has two sections:
- **opwise**: Per-operator instance capabilities (keyed by `(op_name, op_type)` tuple)
- **optypewise**: Per-operator type capabilities (keyed by op type string)

Each capability lists possible configurations including data types, quantization schemes (symmetric/asymmetric), granularity (per-channel/per-tensor), and calibration algorithms (minmax/kl/percentile).

**Sources:** [docs/source/add_new_adaptor.md:46-105]()

### 2. quantize

Applies quantization to the model based on the tuning configuration.

**Method Signature:**
```python
def quantize(self, tune_cfg, model, dataloader, q_func=None) -> BaseModel
```

**Parameters:**
- `tune_cfg`: Dictionary mapping operators to their quantization configuration
- `model`: The model to quantize (BaseModel wrapper)
- `dataloader`: Calibration data loader
- `q_func`: Optional training function for QAT mode

**Tuning Configuration Format:**
```python
tune_cfg = {
    'op': {
        ('conv1', 'Conv2d'): {
            'weight': {
                'dtype': 'int8',
                'scheme': 'sym',
                'granularity': 'per_channel',
                'algorithm': 'minmax'
            },
            'activation': {
                'dtype': 'uint8',
                'scheme': 'asym',
                'granularity': 'per_tensor',
                'algorithm': 'kl'
            }
        },
        # ... configurations for other ops
    },
    'calib_iteration': 100,
    'calib_sampling_size': 100
}
```

The `quantize` method:
1. Parses the `tune_cfg` to determine which operators to quantize and how
2. Inserts observers or fake quantization nodes in the model
3. Runs calibration using the provided dataloader
4. Converts the model to use quantized operators
5. Returns the quantized model

**Sources:** [docs/source/add_new_adaptor.md:46-51](), [neural_compressor/quantization.py:43-241]()

### 3. evaluate

Evaluates the model using the provided evaluation function or dataloader.

**Method Signature:**
```python
def evaluate(self, model, dataloader, postprocess, metrics, measurer, iteration, tensorboard, fp32_baseline)
```

This method wraps the user's evaluation function and measures accuracy and performance metrics.

**Sources:** [neural_compressor/benchmark.py:140-213]()

## Framework Capability System

### Framework YAML Files

Each framework defines its capabilities in a YAML file that specifies:
- Supported operator types for each precision
- Quantization schemes (symmetric/asymmetric)
- Granularity options (per-channel/per-tensor)
- Calibration algorithms (minmax/kl/percentile)

```mermaid
graph TB
    subgraph "YAML Configuration"
        YAMLFile["Framework YAML<br/>e.g. pytorch_cpu.yaml"]
        
        YAMLFile --> Precisions["Precisions<br/>int8, uint8, bf16, fp32"]
        YAMLFile --> OpTypes["Op Types<br/>Conv2d, Linear, etc."]
        YAMLFile --> Capabilities["Capabilities<br/>per op type"]
        
        Capabilities --> WeightConfig["Weight Config<br/>dtype, scheme, granularity, algorithm"]
        Capabilities --> ActivationConfig["Activation Config<br/>dtype, scheme, granularity, algorithm"]
    end
    
    subgraph "Adaptor Parsing"
        QueryBackendCapability["QueryBackendCapability<br/>Base class"]
        PyTorchQuery["PyTorchQuery"]
        TFQuery["TensorflowQuery"]
        ONNXQuery["ONNXQuery"]
        
        QueryBackendCapability --> PyTorchQuery
        QueryBackendCapability --> TFQuery
        QueryBackendCapability --> ONNXQuery
    end
    
    YAMLFile --> PyTorchQuery
    YAMLFile --> TFQuery
    YAMLFile --> ONNXQuery
    
    PyTorchQuery --> AdaptorCapability["Adaptor capability dict"]
    TFQuery --> AdaptorCapability
    ONNXQuery --> AdaptorCapability
```

**Example YAML structure:**

```yaml
version:
  name: ['1.13.0', '2.0.0']

precisions:
  names: int8, uint8, bf16, fp32

ops:
  int8: ['Conv2d', 'Linear', 'LSTM']
  fp32: ['*']

capabilities:
  int8:
    Conv2d:
      weight:
        dtype: ['int8']
        scheme: ['sym']
        granularity: ['per_channel', 'per_tensor']
        algorithm: ['minmax']
      activation:
        dtype: ['uint8']
        scheme: ['asym', 'sym']
        granularity: ['per_tensor']
        algorithm: ['minmax', 'kl']
```

**Sources:** [docs/source/framework_yaml.md:1-194](), [docs/source/add_new_adaptor.md:52-54]()

### Capability Query Flow

```mermaid
sequenceDiagram
    participant Strategy
    participant Adaptor
    participant YAMLParser as QueryBackendCapability
    participant ModelInspector as Model Inspector
    participant FrameworkYAML as Framework YAML
    
    Strategy->>Adaptor: query_fw_capability(model)
    
    Adaptor->>YAMLParser: Load framework YAML
    YAMLParser->>FrameworkYAML: Read YAML file
    FrameworkYAML-->>YAMLParser: Return parsed config
    YAMLParser-->>Adaptor: Return framework capabilities
    
    Adaptor->>ModelInspector: Iterate over model graph
    
    loop For each operator in model
        ModelInspector->>ModelInspector: Get op name and type
        ModelInspector->>YAMLParser: Query capability for op type
        YAMLParser-->>ModelInspector: Return op type capability
        ModelInspector->>Adaptor: Add to opwise capability
    end
    
    Adaptor->>Adaptor: Build final capability dict<br/>{opwise, optypewise}
    Adaptor-->>Strategy: Return capability
```

**Sources:** [docs/source/add_new_adaptor.md:20-43]()

## Quantization Process Flow

The quantization process varies by approach (PTQ, QAT, dynamic) but follows a general pattern:

### Post-Training Static Quantization (PTQ)

```mermaid
graph TB
    subgraph "Input"
        Model["FP32 Model"]
        TuneCfg["Tuning Config<br/>tune_cfg"]
        Dataloader["Calibration<br/>Dataloader"]
    end
    
    subgraph "Phase 1: Observer Insertion"
        ParseCfg["Parse tune_cfg"]
        InsertObservers["Insert Observers<br/>or FakeQuantize modules"]
    end
    
    subgraph "Phase 2: Calibration"
        RunCalib["Run calibration<br/>forward passes"]
        CollectStats["Collect min/max<br/>statistics"]
        CalcScale["Calculate scales<br/>and zero points"]
    end
    
    subgraph "Phase 3: Conversion"
        Convert["Convert to<br/>quantized operators"]
        OptimizeGraph["Apply graph<br/>optimizations"]
    end
    
    subgraph "Output"
        QuantModel["INT8 Quantized Model"]
    end
    
    Model --> ParseCfg
    TuneCfg --> ParseCfg
    ParseCfg --> InsertObservers
    
    InsertObservers --> RunCalib
    Dataloader --> RunCalib
    RunCalib --> CollectStats
    CollectStats --> CalcScale
    
    CalcScale --> Convert
    Convert --> OptimizeGraph
    OptimizeGraph --> QuantModel
```

**PyTorch PTQ Example Flow:**
1. Parse `tune_cfg` to identify ops to quantize
2. Insert `torch.quantization.observer` modules or `FakeQuantize` modules
3. Run calibration using dataloader
4. Compute quantization parameters from collected statistics
5. Convert to quantized operators using `torch.quantization.convert`
6. Apply backend-specific optimizations (e.g., operator fusion)

**TensorFlow PTQ Example Flow:**
1. Parse `tune_cfg` and build quantization config
2. Insert `QuantizeV2` and `Dequantize` ops in graph
3. Insert calibration nodes to collect min/max values
4. Run calibration on dataloader
5. Freeze calibration values and optimize graph
6. Fuse quantization ops with compute ops

**Sources:** [docs/source/quantization.md:94-117](), [docs/source/add_new_adaptor.md:107-134]()

### Quantization-Aware Training (QAT)

For QAT, the adaptor inserts fake quantization nodes during training:

```mermaid
graph TB
    subgraph "Preparation Phase"
        FP32Model["FP32 Model"]
        InsertFakeQuant["Insert FakeQuantize<br/>modules"]
        PreparedModel["Prepared Model<br/>with fake quant"]
    end
    
    subgraph "Training Phase"
        TrainLoop["Training Loop<br/>provided by user"]
        FakeQuantForward["Forward: FakeQuantize<br/>simulates quantization"]
        Backward["Backward: Gradients<br/>flow through"]
        UpdateWeights["Update weights<br/>aware of quantization"]
    end
    
    subgraph "Conversion Phase"
        ConvertModel["Convert fake quant<br/>to real quantization"]
        QuantizedModel["INT8 Model"]
    end
    
    FP32Model --> InsertFakeQuant
    InsertFakeQuant --> PreparedModel
    PreparedModel --> TrainLoop
    TrainLoop --> FakeQuantForward
    FakeQuantForward --> Backward
    Backward --> UpdateWeights
    UpdateWeights -.iterate.-> TrainLoop
    UpdateWeights --> ConvertModel
    ConvertModel --> QuantizedModel
```

**Sources:** [docs/source/quantization.md:114-117](), [neural_compressor/training.py:38-194]()

## Backend Selection and Configuration

### Backend Configuration

Different backends are specified via the `backend` parameter in the configuration:

```python
# PyTorch Default (Eager/FX mode)
conf = PostTrainingQuantConfig(backend='default')

# PyTorch IPEX
conf = PostTrainingQuantConfig(backend='ipex')

# TensorFlow ITEX
conf = PostTrainingQuantConfig(backend='itex')

# ONNX Runtime with different execution providers
conf = PostTrainingQuantConfig(backend='onnxrt_cuda_ep')  # CUDA
conf = PostTrainingQuantConfig(backend='onnxrt_dnnl_ep')  # DNNL
conf = PostTrainingQuantConfig(backend='onnxrt_trt_ep')   # TensorRT
```

**Sources:** [neural_compressor/config.py:261-357]()

### Backend-Specific Information

Adaptors receive backend-specific configuration through `framework_specific_info`:

```mermaid
graph LR
    subgraph "Configuration"
        Config["BenchmarkConfig or<br/>QuantizationConfig"]
    end
    
    subgraph "Framework Specific Info"
        FSI["framework_specific_info<br/>dict"]
        
        FSI --> Device["device: cpu/gpu/hpu"]
        FSI --> Backend["backend: default/ipex/itex"]
        FSI --> Approach["approach: static/dynamic/qat"]
        FSI --> Format["format: default/QDQ/QLinear"]
    end
    
    subgraph "Framework-Specific Fields"
        TFFields["TensorFlow:<br/>inputs, outputs, recipes"]
        PTFields["PyTorch:<br/>q_dataloader, workspace_path"]
        ONNXFields["ONNX Runtime:<br/>graph_optimization"]
    end
    
    Config --> FSI
    FSI --> TFFields
    FSI --> PTFields
    FSI --> ONNXFields
```

**Example for PyTorch:**
```python
framework_specific_info = {
    'device': 'cpu',
    'approach': 'post_training_static_quant',
    'random_seed': 1978,
    'backend': 'ipex',
    'format': 'default',
    'workspace_path': './nc_workspace',
    'q_dataloader': None
}
```

**Example for ONNX Runtime:**
```python
framework_specific_info = {
    'device': 'gpu',
    'backend': 'onnxrt_cuda_ep',
    'workspace_path': './nc_workspace',
    'graph_optimization': {
        'level': 'ENABLE_EXTENDED',
        'disabled_optimizers': []
    }
}
```

**Sources:** [neural_compressor/benchmark.py:155-175](), [neural_compressor/training.py:95-106]()

## Adaptor Initialization and Registration

### Adaptor Factory Pattern

The adaptor selection happens through the `FRAMEWORKS` registry:

```python
from neural_compressor.adaptor import FRAMEWORKS

# Framework detection from model
framework = get_model_fwk_name(model)  # Returns 'pytorch', 'tensorflow', 'onnxruntime'

# Adaptor instantiation
adaptor = FRAMEWORKS[framework](framework_specific_info)
```

The registry maps framework strings to adaptor classes and handles backend variants:

- `'pytorch'` → `PyTorchAdaptor` (Eager mode)
- `'pytorch_ipex'` → `PyTorchIPEXAdaptor`
- `'pytorch_fx'` → `PyTorchFXAdaptor`
- `'tensorflow'` → `TensorflowAdaptor`
- `'tensorflow_itex'` → `TensorflowAdaptor` (with ITEX backend)
- `'onnxruntime'` → `ONNXRTAdaptor`

**Sources:** [neural_compressor/benchmark.py:162-178](), [neural_compressor/model/model.py:51-63]()

### Model Wrapping

Before being passed to adaptors, raw models are wrapped in Neural Compressor's `Model` class:

```python
from neural_compressor.model import Model

wrapped_model = Model(raw_model, conf=config)
```

The `Model` wrapper:
- Provides a unified interface across frameworks
- Stores framework-specific metadata (input/output names, etc.)
- Manages model serialization and deserialization

**Sources:** [neural_compressor/model/model.py:150-253](), [neural_compressor/quantization.py:149]()

## Summary

Framework Adaptors serve as the critical abstraction layer that enables Neural Compressor to support multiple deep learning frameworks through a unified interface. Key characteristics:

1. **Standardized API**: All adaptors implement `query_fw_capability()` and `quantize()` methods
2. **Framework-Specific Logic**: Each adaptor handles the nuances of its target framework
3. **Backend Flexibility**: Single frameworks can have multiple backend implementations (e.g., PyTorch with default/IPEX/FX)
4. **Capability-Driven**: Adaptors declare what quantization configurations are possible through capability dictionaries
5. **Configuration Translation**: Adaptors translate framework-agnostic tuning configurations into framework-specific operations

The adaptor layer allows Neural Compressor's strategies to remain framework-agnostic while still leveraging the native quantization capabilities of each framework.

**Sources:** [docs/source/add_new_adaptor.md:1-134](), [neural_compressor/quantization.py:1-242](), [neural_compressor/benchmark.py:1-448]()

---

