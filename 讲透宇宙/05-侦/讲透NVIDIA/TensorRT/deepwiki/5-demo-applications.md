<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT · page 5 Demo Applications · fetched 2026-10-26 -->

# Demo Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CHANGELOG.md](CHANGELOG.md)
- [demo/BERT/README.md](demo/BERT/README.md)
- [demo/BERT/builder.py](demo/BERT/builder.py)
- [demo/BERT/builder_varseqlen.py](demo/BERT/builder_varseqlen.py)
- [demo/BERT/infer_c/bert_infer.h](demo/BERT/infer_c/bert_infer.h)
- [demo/BERT/inference.ipynb](demo/BERT/inference.ipynb)
- [demo/BERT/inference.py](demo/BERT/inference.py)
- [demo/BERT/inference_varseqlen.py](demo/BERT/inference_varseqlen.py)
- [demo/BERT/perf.py](demo/BERT/perf.py)
- [demo/BERT/perf_varseqlen.py](demo/BERT/perf_varseqlen.py)
- [demo/BERT/scripts/download_model.sh](demo/BERT/scripts/download_model.sh)
- [demo/BERT/scripts/download_squad.sh](demo/BERT/scripts/download_squad.sh)
- [demo/BERT/scripts/inference_benchmark.sh](demo/BERT/scripts/inference_benchmark.sh)
- [demo/BERT/scripts/inference_benchmark_megatron.sh](demo/BERT/scripts/inference_benchmark_megatron.sh)
- [demo/Diffusion/README.md](demo/Diffusion/README.md)
- [demo/Diffusion/demo_img2img_flux.py](demo/Diffusion/demo_img2img_flux.py)
- [demo/Diffusion/demo_txt2img_flux.py](demo/Diffusion/demo_txt2img_flux.py)
- [demo/Diffusion/requirements.txt](demo/Diffusion/requirements.txt)
- [samples/sampleINT8API/sampleINT8API.cpp](samples/sampleINT8API/sampleINT8API.cpp)

</details>



This section covers the TensorRT demo applications and sample infrastructure that demonstrate TensorRT acceleration across various AI workloads. These applications serve as reference implementations showing how to integrate TensorRT with different model types, frameworks, and deployment scenarios.

For information about the core TensorRT API used by these demos, see [Core API](#3). For details about the plugin system utilized by many demos, see [Plugin System](#4).

## Sample Infrastructure Architecture

The TensorRT sample infrastructure provides a comprehensive framework for building, configuring, and executing TensorRT engines across different demo applications. The architecture is built around several key components that handle engine management, configuration parsing, inference execution, and performance reporting.

### Sample Infrastructure Components

```mermaid
graph TD
    subgraph "Sample Infrastructure Core"
        SampleEngines["sampleEngines.cpp<br/>LazilyDeserializedEngine<br/>modelToNetwork()"]
        SampleOptions["sampleOptions.cpp<br/>BuildOptions<br/>InferenceOptions"]
        SampleInference["sampleInference.cpp<br/>InferenceEnvironment<br/>setUpInference()"]
        SampleReporting["sampleReporting.cpp<br/>Profiler<br/>printPerformanceReport()"]
    end
    
    subgraph "Configuration System"
        BuildOpts["BuildOptions<br/>Memory pools, Precision<br/>Optimization profiles"]
        InfOpts["InferenceOptions<br/>Batch size, Streams<br/>Input shapes"]
        RepOpts["ReportingOptions<br/>Performance metrics<br/>Output formats"]
    end
    
    subgraph "Execution Framework"
        InfEnvStd["InferenceEnvironmentStd<br/>Standard TensorRT runtime"]
        InfEnvSafe["InferenceEnvironmentSafe<br/>Safe TensorRT runtime"]
        BindingsStd["BindingsStd<br/>Memory management"]
        BindingsSafe["BindingsSafe<br/>Safe memory management"]
    end
    
    SampleOptions --> BuildOpts
    SampleOptions --> InfOpts
    SampleOptions --> RepOpts
    
    SampleEngines --> InfEnvStd
    SampleEngines --> InfEnvSafe
    
    SampleInference --> BindingsStd
    SampleInference --> BindingsSafe
    
    InfEnvStd --> BindingsStd
    InfEnvSafe --> BindingsSafe
```

Sources: [samples/common/sampleEngines.cpp:108-177](), [samples/common/sampleOptions.cpp:369-396](), [samples/common/sampleInference.cpp:407-418](), [samples/common/sampleReporting.cpp:324-347]()

### Engine Management System

The engine management system provides lazy deserialization and runtime configuration capabilities through the `LazilyDeserializedEngine` class and related utilities.

```mermaid
graph TB
    subgraph "Engine Lifecycle"
        ModelLoad["modelToNetwork()<br/>ONNX parsing<br/>Network definition"]
        EngineDeser["LazilyDeserializedEngine<br/>get()<br/>Lazy deserialization"]
        RuntimeCreate["createRuntime()<br/>Plugin loading<br/>DLA configuration"]
    end
    
    subgraph "Model Format Support"
        ONNX["ONNX Models<br/>nvonnxparser::IONNXParser<br/>parseFromFile()"]
        Calibration["INT8 Calibration<br/>RndInt8Calibrator<br/>readCalibrationCache()"]
        VCPlugins["VC Plugin Libraries<br/>getUsedVCPluginLibraries()"]
    end
    
    subgraph "Runtime Configuration"
        DLACore["DLA Core Selection<br/>setDLACore()<br/>checkDLASafe()"]
        MemoryMgmt["Memory Management<br/>setTempfileControlFlags()<br/>setTemporaryDirectory()"]
        PluginRegistry["Plugin Registry<br/>loadLibrary()<br/>Dynamic plugins"]
    end
    
    ModelLoad --> EngineDeser
    EngineDeser --> RuntimeCreate
    
    ONNX --> ModelLoad
    Calibration --> ModelLoad
    VCPlugins --> ModelLoad
    
    RuntimeCreate --> DLACore
    RuntimeCreate --> MemoryMgmt
    RuntimeCreate --> PluginRegistry
```

Sources: [samples/common/sampleEngines.cpp:239-297](), [samples/common/sampleEngines.cpp:302-398](), [samples/common/sampleEngines.cpp:108-177]()

## Configuration and Options System

The configuration system provides comprehensive control over build and inference parameters through structured option classes that parse command-line arguments and validate configuration settings.

### Build and Inference Configuration

```mermaid
graph LR
    subgraph "BuildOptions Structure"
        BuildCore["BuildOptions<br/>Precision settings<br/>Memory pools"]
        BuildPrec["Precision Control<br/>fp16, bf16, int8<br/>precisionConstraints"]
        BuildMem["Memory Configuration<br/>workspace, dlaSRAM<br/>dlaLocalDRAM"]
        BuildOpt["Optimization Settings<br/>optProfiles<br/>builderOptimizationLevel"]
    end
    
    subgraph "InferenceOptions Structure"
        InfCore["InferenceOptions<br/>Runtime parameters<br/>Execution control"]
        InfShapes["Shape Configuration<br/>shapes, batch<br/>optProfileIndex"]
        InfExec["Execution Settings<br/>infStreams, iterations<br/>memoryAllocationStrategy"]
        InfData["Data Management<br/>inputs, skipTransfers<br/>useManaged"]
    end
    
    subgraph "ReportingOptions Structure"
        RepCore["ReportingOptions<br/>Output and profiling<br/>Performance metrics"]
        RepPerf["Performance Reporting<br/>profile, exportProfile<br/>percentiles"]
        RepOutput["Output Control<br/>output, exportOutput<br/>dumpRawBindings"]
        RepLayer["Layer Information<br/>layerInfo, exportLayerInfo<br/>optProfileInfo"]
    end
    
    BuildCore --> BuildPrec
    BuildCore --> BuildMem
    BuildCore --> BuildOpt
    
    InfCore --> InfShapes
    InfCore --> InfExec
    InfCore --> InfData
    
    RepCore --> RepPerf
    RepCore --> RepOutput
    RepCore --> RepLayer
```

Sources: [samples/common/sampleOptions.cpp:498-514](), [samples/common/sampleOptions.cpp:570-584](), [samples/common/sampleOptions.cpp:696-767]()

### Option Parsing and Validation

The option parsing system handles complex command-line argument processing with type conversion, validation, and error handling capabilities.

```mermaid
graph TD
    subgraph "Argument Processing"
        ArgParse["Arguments map<br/>Command-line parsing<br/>Flag validation"]
        TypeConv["stringToValue<br/>Type conversion<br/>Unit multipliers"]
        Validation["validateNonEmpty<br/>Range checking<br/>Format validation"]
    end
    
    subgraph "Shape Processing"
        ShapesParse["getShapesBuild()<br/>Profile shapes<br/>Dynamic dimensions"]
        ShapesValid["processShapes()<br/>Min/Opt/Max validation<br/>Broadcasting"]
        ProfileMgmt["getOptimizationProfiles()<br/>Multiple profiles<br/>Index validation"]
    end
    
    subgraph "Format Handling"
        IOFormats["IOFormat parsing<br/>DataType + TensorFormats<br/>Broadcast logic"]
        LayerTypes["LayerPrecisions<br/>LayerOutputTypes<br/>Layer-specific config"]
        DeviceTypes["LayerDeviceTypes<br/>GPU/DLA selection<br/>Per-layer assignment"]
    end
    
    ArgParse --> TypeConv
    TypeConv --> Validation
    
    ShapesParse --> ShapesValid
    ShapesValid --> ProfileMgmt
    
    IOFormats --> LayerTypes
    LayerTypes --> DeviceTypes
```

Sources: [samples/common/sampleOptions.cpp:91-132](), [samples/common/sampleOptions.cpp:473-477](), [samples/common/sampleOptions.cpp:570-612]()

## Inference Execution Framework

The inference execution framework provides both standard and safe runtime environments with comprehensive memory management, context handling, and execution control.

### Inference Environment Setup

```mermaid
graph TB
    subgraph "Environment Types"
        StdEnv["InferenceEnvironmentStd<br/>Standard TensorRT runtime<br/>ICudaEngine + IExecutionContext"]
        SafeEnv["InferenceEnvironmentSafe<br/>Safe TensorRT runtime<br/>ITRTGraph + Safe interfaces"]
    end
    
    subgraph "Setup Process"
        EnvSetup["setUpInference()<br/>Environment initialization<br/>Memory allocation"]
        CtxCreate["Context Creation<br/>createExecutionContext()<br/>setOptimizationProfileAsync()"]
        MemAlloc["Memory Allocation<br/>allocateContextMemory()<br/>Memory strategies"]
        BindSetup["Binding Setup<br/>FillBindingClosure<br/>Tensor configuration"]
    end
    
    subgraph "Memory Strategies"
        StaticMem["Static Memory<br/>Pre-allocated buffers<br/>Fixed memory usage"]
        ProfileMem["Profile Memory<br/>getDeviceMemorySizeForProfile()<br/>Current profile sizing"]
        RuntimeMem["Runtime Memory<br/>updateDeviceMemorySizeForShapes()<br/>Dynamic sizing"]
    end
    
    StdEnv --> EnvSetup
    SafeEnv --> EnvSetup
    
    EnvSetup --> CtxCreate
    CtxCreate --> MemAlloc
    MemAlloc --> BindSetup
    
    MemAlloc --> StaticMem
    MemAlloc --> ProfileMem
    MemAlloc --> RuntimeMem
```

Sources: [samples/common/sampleInference.cpp:525-808](), [samples/common/sampleInference.cpp:342-385](), [samples/common/sampleInference.cpp:234-322]()

### Binding and Memory Management

```mermaid
graph LR
    subgraph "Binding System"
        TensorInfo["TensorInfo<br/>Tensor metadata<br/>Dimensions and types"]
        BindingsStd["BindingsStd<br/>Standard memory management<br/>addBinding()"]
        BindingsSafe["BindingsSafe<br/>Safe memory management<br/>TypedArray creation"]
    end
    
    subgraph "Memory Types"
        DeviceMem["Device Memory<br/>GPU allocations<br/>CUDA memory management"]
        ManagedMem["Managed Memory<br/>Unified memory<br/>Integrated GPU support"]
        HostMem["Host Memory<br/>CPU allocations<br/>Data transfer buffers"]
    end
    
    subgraph "Tensor Management"
        InputTensors["Input Tensor Setup<br/>Shape validation<br/>Data loading"]
        OutputTensors["Output Tensor Setup<br/>Dynamic allocation<br/>OutputAllocator"]
        ShapeTensors["Shape Tensor Handling<br/>Shape inference IO<br/>setTensorAddress()"]
    end
    
    TensorInfo --> BindingsStd
    TensorInfo --> BindingsSafe
    
    BindingsStd --> DeviceMem
    BindingsStd --> ManagedMem
    BindingsSafe --> HostMem
    
    InputTensors --> TensorInfo
    OutputTensors --> TensorInfo
    ShapeTensors --> TensorInfo
```

Sources: [samples/common/sampleInference.cpp:235-322](), [samples/common/sampleInference.cpp:676-808](), [samples/common/sampleInference.cpp:421-523]()

## Performance Reporting System

The performance reporting system provides comprehensive analysis of inference performance with detailed metrics, profiling capabilities, and export functionality.

### Performance Metrics and Analysis

```mermaid
graph TD
    subgraph "Performance Collection"
        InfTrace["InferenceTrace<br/>Timing data collection<br/>H2D, Compute, D2H"]
        InfTime["InferenceTime<br/>Latency calculations<br/>End-to-end timing"]
        Profiler["Profiler class<br/>Layer-level profiling<br/>reportLayerTime()"]
    end
    
    subgraph "Statistical Analysis"
        PerfResult["PerformanceResult<br/>Statistical metrics<br/>Min/Max/Mean/Median"]
        Percentiles["Percentile Calculation<br/>findPercentile()<br/>Custom percentiles"]
        CoeffVar["Coefficient of Variance<br/>findCoeffOfVariance()<br/>Stability metrics"]
    end
    
    subgraph "Reporting Output"
        ConsoleReport["Console Reporting<br/>printPerformanceReport()<br/>Performance summary"]
        JSONExport["JSON Export<br/>exportJSONTrace()<br/>exportJSONProfile()"]
        LayerInfo["Layer Information<br/>printLayerInfo()<br/>getLayerInformation()"]
    end
    
    InfTrace --> PerfResult
    InfTime --> PerfResult
    Profiler --> PerfResult
    
    PerfResult --> Percentiles
    PerfResult --> CoeffVar
    
    PerfResult --> ConsoleReport
    PerfResult --> JSONExport
    Profiler --> LayerInfo
```

Sources: [samples/common/sampleReporting.cpp:211-230](), [samples/common/sampleReporting.cpp:47-109](), [samples/common/sampleReporting.cpp:379-443]()

### Output and Debug Capabilities

The reporting system includes comprehensive output dumping, debug tensor analysis, and performance warning systems to help developers optimize their TensorRT applications.

```mermaid
graph LR
    subgraph "Output Management"
        OutputDump["dumpOutputs()<br/>Tensor value printing<br/>Formatted output"]
        RawBindings["dumpRawBindingsToFiles()<br/>Binary data export<br/>File-based output"]
        JSONOutput["exportJSONOutput()<br/>Structured data export<br/>JSON formatting"]
    end
    
    subgraph "Performance Warnings"
        EnqueueWarn["Enqueue Time Warnings<br/>GPU under-utilization<br/>CUDA Graph suggestions"]
        TransferWarn["Data Transfer Warnings<br/>H2D/D2H bottlenecks<br/>noDataTransfers advice"]
        StabilityWarn["Stability Warnings<br/>GPU compute variance<br/>Clock frequency advice"]
    end
    
    subgraph "Debug Features"
        DebugTensors["Debug Tensor Writing<br/>DebugTensorWriter<br/>setTensorDebugState()"]
        LayerProfiling["Layer Profiling<br/>Per-layer timing<br/>Auxiliary stream warnings"]
        OptProfileInfo["Optimization Profiles<br/>Profile shape information<br/>Min/Opt/Max display"]
    end
    
    OutputDump --> RawBindings
    RawBindings --> JSONOutput
    
    EnqueueWarn --> TransferWarn
    TransferWarn --> StabilityWarn
    
    DebugTensors --> LayerProfiling
    LayerProfiling --> OptProfileInfo
```

Sources: [samples/common/sampleReporting.cpp:466-503](), [samples/common/sampleReporting.cpp:275-316](), [samples/common/sampleReporting.cpp:546-610]()

## Common Utilities and Support

The sample infrastructure includes extensive utility functions for data handling, memory management, timing, and cross-platform compatibility that support all demo applications.

### Data Processing and Memory Utilities

```mermaid
graph TB
    subgraph "Data Type Support"
        TypeSizes["getNbBytes()<br/>Size calculation per type<br/>FP32/FP16/INT8/etc"]
        DataConv["Type Conversion<br/>swapEndianness()<br/>Cross-platform support"]
        BufferOps["Buffer Operations<br/>fillBuffer()<br/>dumpBuffer()"]
    end
    
    subgraph "Memory Management"
        CudaMalloc["safeCudaMalloc()<br/>Safe GPU allocation<br/>Error handling"]
        HostMemory["HostMemory classes<br/>TypedHostMemory<br/>Type-safe allocations"]
        StreamMgmt["Stream Management<br/>makeCudaStream()<br/>RAII stream handling"]
    end
    
    subgraph "File Operations"
        FileLoad["loadFromFile()<br/>Binary data loading<br/>Size validation"]
        PPMRead["PPM/PGM Reading<br/>Image format support<br/>readPPMFile()"]
        ASCIIFiles["ASCII File I/O<br/>readASCIIFile()<br/>writeASCIIFile()"]
    end
    
    TypeSizes --> DataConv
    DataConv --> BufferOps
    
    CudaMalloc --> HostMemory
    HostMemory --> StreamMgmt
    
    FileLoad --> PPMRead
    PPMRead --> ASCIIFiles
```

Sources: [samples/common/common.h:556-584](), [samples/common/common.h:236-284](), [samples/common/common.h:348-421]()

The demo applications leverage this comprehensive sample infrastructure to provide robust, performant, and easy-to-use examples of TensorRT integration across various AI workloads and deployment scenarios.

---

