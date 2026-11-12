<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/psi · page 7 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Sources/Imaging/Test.Psi.Imaging.Windows/AverageColorTests.cs](Sources/Imaging/Test.Psi.Imaging.Windows/AverageColorTests.cs)
- [Sources/Kinect/Test.Psi.Kinect.Windows.x64/MeshTests.cs](Sources/Kinect/Test.Psi.Kinect.Windows.x64/MeshTests.cs)
- [Sources/Media/Microsoft.Psi.Media.Windows.x64/MediaSource.cs](Sources/Media/Microsoft.Psi.Media.Windows.x64/MediaSource.cs)
- [Sources/RealSense/Microsoft.Psi.RealSense.Windows.x64/RealSenseSensor.cs](Sources/RealSense/Microsoft.Psi.RealSense.Windows.x64/RealSenseSensor.cs)
- [Sources/Runtime/Test.Psi/CommonTester.cs](Sources/Runtime/Test.Psi/CommonTester.cs)
- [Sources/Runtime/Test.Psi/IntervalTests.cs](Sources/Runtime/Test.Psi/IntervalTests.cs)
- [Sources/Runtime/Test.Psi/JoinTests.cs](Sources/Runtime/Test.Psi/JoinTests.cs)
- [Sources/Runtime/Test.Psi/PipelineTest.cs](Sources/Runtime/Test.Psi/PipelineTest.cs)
- [Sources/Visualization/Microsoft.Psi.Visualization.Windows/PluginMap.cs](Sources/Visualization/Microsoft.Psi.Visualization.Windows/PluginMap.cs)

</details>



This page covers the development workflows, testing frameworks, and testing practices used in the Microsoft Psi framework. It provides an overview of how components are developed, tested, and integrated into the platform.

For information about specific build system configuration and NuGet packaging, see [Build System and Configuration](#7.2). For contributing guidelines and submission processes, see [Contributing to Psi](#7.3).

## Testing Infrastructure

The Psi framework employs a comprehensive testing infrastructure built on MSTest, with specialized testing patterns for stream processing components, pipeline management, and multimodal data handling.

### Core Testing Framework Architecture

```mermaid
graph TB
    subgraph "MSTest Infrastructure"
        TestClass["[TestClass]<br/>Test Class Attributes"]
        TestMethod["[TestMethod]<br/>Individual Test Methods"]
        Timeout["[Timeout(60000)]<br/>Test Timeout Management"]
    end
    
    subgraph "Psi Testing Patterns"
        PipelineTest["PipelineTest<br/>Core Pipeline Testing"]
        ComponentTest["Component Testing<br/>ISourceComponent/IConsumerComponent"]
        IntervalTest["IntervalTests<br/>Time Interval Operations"]
        JoinTest["JoinTests<br/>Stream Join Operations"]
    end
    
    subgraph "Domain-Specific Tests"
        ImagingTest["AverageColorTests<br/>Imaging Operations"]
        KinectTest["MeshTests<br/>Kinect Integration"]
        VisualizationTest["PluginMap<br/>Plugin Discovery"]
    end
    
    subgraph "Test Utilities"
        Generators["Generators.Sequence<br/>Test Data Generation"]
        Pipeline["Pipeline.Create<br/>Test Pipeline Creation"]
        Observable["ToObservable<br/>Result Collection"]
    end
    
    TestClass --> PipelineTest
    TestMethod --> ComponentTest
    Timeout --> IntervalTest
    
    PipelineTest --> Generators
    ComponentTest --> Pipeline
    IntervalTest --> Observable
    
    PipelineTest --> ImagingTest
    ComponentTest --> KinectTest
    IntervalTest --> VisualizationTest
```

Sources: [Sources/Runtime/Test.Psi/PipelineTest.cs:18-19](), [Sources/Runtime/Test.Psi/CommonTester.cs:14-15](), [Sources/Runtime/Test.Psi/IntervalTests.cs:10-11]()

### Pipeline Testing Patterns

The framework provides specialized patterns for testing pipeline components and their interactions:

```mermaid
graph LR
    subgraph "Pipeline Creation"
        CreatePipeline["Pipeline.Create('name')<br/>Test Pipeline Instance"]
        Subpipeline["Subpipeline.Create<br/>Nested Pipeline Testing"]
    end
    
    subgraph "Component Testing"
        SourceComponent["ISourceComponent<br/>Start/Stop Lifecycle"]
        Processor["Processor&lt;T,U&gt;<br/>Stream Processing"]
        Generator["Generator<br/>Data Generation"]
    end
    
    subgraph "Data Flow Testing"
        Generators["Generators.Sequence<br/>Test Data Streams"]
        PipeTo["PipeTo Operations<br/>Stream Connections"]
        Connectors["Connector&lt;T&gt;<br/>Pipeline Bridging"]
    end
    
    subgraph "Verification"
        DoOperator["Do() Operator<br/>Side Effect Testing"]
        ToObservable["ToObservable<br/>Result Collection"]
        AutoResetEvent["AutoResetEvent<br/>Synchronization"]
    end
    
    CreatePipeline --> SourceComponent
    Subpipeline --> Processor
    SourceComponent --> Generators
    Processor --> PipeTo
    Generator --> Connectors
    
    Generators --> DoOperator
    PipeTo --> ToObservable
    Connectors --> AutoResetEvent
```

Sources: [Sources/Runtime/Test.Psi/PipelineTest.cs:25-40](), [Sources/Runtime/Test.Psi/PipelineTest.cs:90-105]()

## Development Workflows

### Component Development and Testing Cycle

The typical development workflow involves creating components, writing tests, and verifying integration with the pipeline system:

| Phase | Activities | Key Classes | Test Patterns |
|-------|------------|-------------|---------------|
| **Component Design** | Interface definition, data flow planning | `ISourceComponent`, `IConsumerComponent` | Mock data generation |
| **Implementation** | Core logic, emitter/receiver setup | `Emitter<T>`, `Receiver<T>` | Unit testing with `Generators.Sequence` |
| **Pipeline Integration** | Connection testing, timing verification | `Pipeline`, `Subpipeline` | Integration testing with real data flows |
| **Performance Testing** | Latency, throughput measurement | `GeneratorWithLatency` | Load testing with artificial delays |
| **Finalization Testing** | Resource cleanup, shutdown behavior | Component lifecycle | Shutdown sequence verification |

### Test Data Generation Patterns

The framework provides several utilities for generating test data and controlling timing:

```mermaid
graph TB
    subgraph "Data Generators"
        Sequence["Generators.Sequence<br/>Fixed sequences with timing"]
        Range["Generators.Range<br/>Numeric ranges"]
        Repeat["Generators.Repeat<br/>Repeating values"]
        Timer["Timers.Timer<br/>Periodic events"]
    end
    
    subgraph "Timing Control"
        TimeSpan["TimeSpan.FromTicks<br/>Precise timing control"]
        DateTime["DateTime.UtcNow<br/>Real-time testing"]
        ReplayDescriptor["ReplayDescriptor<br/>Replay time simulation"]
    end
    
    subgraph "Synchronization"
        AutoResetEvent["AutoResetEvent<br/>Thread synchronization"]
        ManualResetEvent["ManualResetEvent<br/>Manual control"]
        WaitOne["WaitOne(timeout)<br/>Timeout handling"]
    end
    
    Sequence --> TimeSpan
    Range --> DateTime
    Repeat --> ReplayDescriptor
    Timer --> AutoResetEvent
    
    TimeSpan --> ManualResetEvent
    DateTime --> WaitOne
```

Sources: [Sources/Runtime/Test.Psi/PipelineTest.cs:29](), [Sources/Runtime/Test.Psi/PipelineTest.cs:496-500](), [Sources/Runtime/Test.Psi/JoinTests.cs:28-29]()

## Component Testing Patterns

### Lifecycle Testing

Components must properly handle start, stop, and disposal operations:

```mermaid
graph LR
    subgraph "Component Lifecycle"
        Start["Start(notifyCompletionTime)<br/>Component initialization"]
        Running["Running State<br/>Data processing"]
        Stop["Stop(finalTime, notifyCompleted)<br/>Graceful shutdown"]
        Dispose["Dispose()<br/>Resource cleanup"]
    end
    
    subgraph "Test Verification"
        NotifyCompletion["notifyCompletionTime(DateTime.MaxValue)<br/>Infinite source indication"]
        FinalTime["finalOriginatingTime<br/>Last message timestamp"]
        NotifyCompleted["notifyCompleted()<br/>Shutdown confirmation"]
        ResourceCheck["Resource disposal check<br/>Memory leak prevention"]
    end
    
    Start --> NotifyCompletion
    Running --> FinalTime
    Stop --> NotifyCompleted
    Dispose --> ResourceCheck
```

Sources: [Sources/RealSense/Microsoft.Psi.RealSense.Windows.x64/RealSenseSensor.cs:60-89](), [Sources/Media/Microsoft.Psi.Media.Windows.x64/MediaSource.cs:60-97]()

### Stream Processing Testing

Testing stream processing components involves verifying correct data transformation and timing:

```mermaid
graph TB
    subgraph "Input Setup"
        TestData["Test data sequences<br/>Generators.Sequence"]
        Timing["Precise timing<br/>TimeSpan intervals"]
        Pipeline["Test pipeline<br/>Pipeline.Create"]
    end
    
    subgraph "Processing Component"
        Receiver["Receiver&lt;T&gt;<br/>Input stream"]
        Processor["Processing Logic<br/>Data transformation"]
        Emitter["Emitter&lt;U&gt;<br/>Output stream"]
    end
    
    subgraph "Verification"
        Collector["Result collection<br/>ToObservable()"]
        Assertion["Test assertions<br/>Assert.AreEqual"]
        Timing2["Timing verification<br/>OriginatingTime checks"]
    end
    
    TestData --> Receiver
    Timing --> Processor
    Pipeline --> Emitter
    
    Receiver --> Collector
    Processor --> Assertion
    Emitter --> Timing2
```

Sources: [Sources/Runtime/Test.Psi/JoinTests.cs:104-118](), [Sources/Imaging/Test.Psi.Imaging.Windows/AverageColorTests.cs:52-66]()

## Plugin System Testing

The plugin discovery and loading system requires testing for dynamic component loading:

### Plugin Discovery Testing

```mermaid
graph LR
    subgraph "Assembly Discovery"
        PluginMap["PluginMap<br/>Plugin registry"]
        LoadAssembly["Assembly.LoadFrom<br/>Dynamic loading"]
        GetTypes["assembly.GetTypes<br/>Type discovery"]
    end
    
    subgraph "Attribute Scanning"
        VisualizationObject["VisualizationObjectAttribute<br/>Visualizer components"]
        StreamAdapter["StreamAdapterAttribute<br/>Data adapters"]
        Summarizer["SummarizerAttribute<br/>Data summarizers"]
        StreamReader["StreamReaderAttribute<br/>File readers"]
    end
    
    subgraph "Error Handling"
        ReflectionException["ReflectionTypeLoadException<br/>Missing dependencies"]
        VisualizationLogWriter["VisualizationLogWriter<br/>Error logging"]
        ErrorDisplay["Error dialog display<br/>User notification"]
    end
    
    PluginMap --> LoadAssembly
    LoadAssembly --> GetTypes
    GetTypes --> VisualizationObject
    
    VisualizationObject --> StreamAdapter
    StreamAdapter --> Summarizer
    Summarizer --> StreamReader
    
    GetTypes --> ReflectionException
    ReflectionException --> VisualizationLogWriter
    VisualizationLogWriter --> ErrorDisplay
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/PluginMap.cs:129-243](), [Sources/Visualization/Microsoft.Psi.Visualization.Windows/PluginMap.cs:245-277]()

### Default Assembly Search

The plugin system searches a predefined set of assemblies for components:

| Assembly | Purpose | Components |
|----------|---------|------------|
| `Microsoft.Psi.dll` | Core runtime | Pipeline, operators, serialization |
| `Microsoft.Psi.Audio.dll` | Audio processing | Audio sources, processors |
| `Microsoft.Psi.Data.dll` | Data persistence | PsiStore, importers/exporters |
| `Microsoft.Psi.Visualization.Windows.dll` | Visualization | Visualizers, UI components |

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/PluginMap.cs:25-31]()

## Integration Testing Approaches

### Multi-Component Integration

Integration tests verify that multiple components work together correctly in realistic scenarios:

```mermaid
graph TB
    subgraph "Sensor Integration"
        SensorCapture["Sensor data capture<br/>KinectSensor, RealSenseSensor"]
        DataFlow["Multi-modal streams<br/>RGB, Depth, Audio"]
        Processing["Real-time processing<br/>Computer vision pipeline"]
    end
    
    subgraph "Pipeline Integration"
        MainPipeline["Main pipeline<br/>Sensor coordination"]
        Subpipelines["Processing subpipelines<br/>Parallel processing"]
        Connectors["Stream connectors<br/>Data routing"]
    end
    
    subgraph "Output Integration"
        PsiStore["Data persistence<br/>PsiStore serialization"]
        Visualization["Real-time visualization<br/>PsiStudio integration"]
        Export["Data export<br/>Format conversion"]
    end
    
    SensorCapture --> MainPipeline
    DataFlow --> Subpipelines
    Processing --> Connectors
    
    MainPipeline --> PsiStore
    Subpipelines --> Visualization
    Connectors --> Export
```

Sources: [Sources/Kinect/Test.Psi.Kinect.Windows.x64/MeshTests.cs:30-37](), [Sources/Kinect/Test.Psi.Kinect.Windows.x64/MeshTests.cs:49-52]()

### Performance and Stress Testing

The framework includes patterns for testing component performance under load:

- **Latency Testing**: Using `GeneratorWithLatency` to simulate processing delays
- **Throughput Testing**: High-frequency data generation with `Timers.Timer`
- **Memory Testing**: Resource allocation patterns and cleanup verification
- **Shutdown Testing**: Graceful termination under various conditions

Sources: [Sources/Runtime/Test.Psi/PipelineTest.cs:464-487](), [Sources/Runtime/Test.Psi/PipelineTest.cs:577-595]()

---

