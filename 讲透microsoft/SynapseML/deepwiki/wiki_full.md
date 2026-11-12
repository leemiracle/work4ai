# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [website/src/pages/index.js](website/src/pages/index.js)

</details>



This document provides a high-level introduction to SynapseML, explaining its purpose, architecture, and core capabilities. For detailed information about specific subsystems, refer to the linked pages throughout this document.

SynapseML is an open-source library that simplifies the creation of massively scalable machine learning pipelines on Apache Spark. It provides simple, composable, and distributed APIs for a wide variety of ML tasks including text analytics, vision, anomaly detection, deep learning, and traditional machine learning algorithms.

**Scope**: This page covers the overall architecture, component structure, and high-level capabilities. For platform-specific deployment details, see [Deployment](#8). For build and testing infrastructure, see [Development Infrastructure](#3). For specific ML capabilities, see [AI Services Integration](#6).

## What is SynapseML

SynapseML (previously known as MMLSpark) is built on the Apache Spark distributed computing framework and shares the same API as SparkML/MLLib, allowing seamless integration into existing Spark workflows. It enables users to build scalable and intelligent systems that can train and evaluate models on single-node, multi-node, and elastically resizable clusters.

**Key characteristics**:

- **Distributed**: Scales ML workloads across Spark clusters
- **Multi-language**: Supports Python, R, Scala, Java, and .NET
- **SparkML-compatible**: Extends the `PipelineStage` API
- **Cloud-native**: Integrates with Azure services and runs on multiple platforms

**Requirements**: Scala 2.12, Spark 3.4+, Python 3.8+

Sources: [README.md:1-10]()

## Modular Architecture

SynapseML is organized into six independent modules, each providing specialized ML capabilities. All modules share common infrastructure for HTTP communication, logging, secret management, and platform detection.

### High-Level Module Structure

```mermaid
graph TB
    subgraph "Core Modules"
        Core["core<br/>com.microsoft.azure.synapse.ml.core"]
        Cognitive["cognitive<br/>com.microsoft.azure.synapse.ml.cognitive"]
        DeepLearning["deep-learning<br/>com.microsoft.azure.synapse.ml.onnx<br/>com.microsoft.azure.synapse.ml.train"]
        LightGBM["lightgbm<br/>com.microsoft.azure.synapse.ml.lightgbm"]
        VW["vw<br/>com.microsoft.azure.synapse.ml.vw"]
        OpenCV["opencv<br/>com.microsoft.azure.synapse.ml.opencv"]
    end
    
    subgraph "Shared Infrastructure"
        Logging["SynapseMLLogging"]
        HTTP["HTTPClient<br/>AsyncHTTPClient"]
        Secrets["Secrets Object"]
        Platform["Platform Detection"]
        Params["GlobalParams<br/>ServiceParam"]
    end
    
    subgraph "Spark ML Extension"
        PipelineStage["PipelineStage"]
        Transformer["Transformer"]
        Estimator["Estimator"]
        Evaluator["Evaluator"]
    end
    
    Core --> Logging
    Core --> HTTP
    Core --> Secrets
    Core --> Platform
    
    Cognitive --> HTTP
    Cognitive --> Secrets
    Cognitive --> Params
    
    DeepLearning --> HTTP
    LightGBM --> Logging
    VW --> Logging
    OpenCV --> Core
    
    Core --> PipelineStage
    Cognitive --> Transformer
    DeepLearning --> Transformer
    LightGBM --> Estimator
    VW --> Estimator
    OpenCV --> Transformer
```

Sources: [README.md:1-10]()

### Module Descriptions

| Module | Package | Purpose | Key Components |
|--------|---------|---------|----------------|
| **core** | `com.microsoft.azure.synapse.ml.core` | Foundational infrastructure, HTTP clients, logging, parameter management | `SynapseMLLogging`, `HTTPClient`, `GlobalParams`, `ServiceParam` |
| **cognitive** | `com.microsoft.azure.synapse.ml.cognitive` | Azure AI Services integration (OpenAI, Cognitive Services, AI Foundry) | `OpenAIPrompt`, `OpenAIChatCompletion`, `OpenAIEmbedding`, `CognitiveServiceBase` |
| **deep-learning** | `com.microsoft.azure.synapse.ml.onnx`, `com.microsoft.azure.synapse.ml.train` | ONNX model inference, Horovod distributed training, PyTorch Lightning | `ONNXModel`, `DeepTextClassifier`, `DeepVisionClassifier` |
| **lightgbm** | `com.microsoft.azure.synapse.ml.lightgbm` | LightGBM gradient boosting algorithms | `LightGBMRegressor`, `LightGBMClassifier`, `LightGBMRanker` |
| **vw** | `com.microsoft.azure.synapse.ml.vw` | Vowpal Wabbit online learning and contextual bandits | `VowpalWabbitClassifier`, `VowpalWabbitRegressor`, `VowpalWabbitContextualBandit` |
| **opencv** | `com.microsoft.azure.synapse.ml.opencv` | Image transformations and computer vision utilities | `ImageTransformer`, `ImageFeaturizer` |

Sources: [README.md:47-64]()

## Component Architecture with Code Entities

The following diagram shows how core components relate to each other using actual class names and file structures from the codebase:

```mermaid
graph TB
    subgraph "AI Service Implementations"
        OpenAIPrompt["OpenAIPrompt<br/>cognitive/src/.../OpenAIPrompt.scala"]
        OpenAIChat["OpenAIChatCompletion<br/>cognitive/src/.../OpenAIChatCompletion.scala"]
        OpenAIEmbed["OpenAIEmbedding<br/>cognitive/src/.../OpenAIEmbedding.scala"]
        CognitiveBase["CognitiveServiceBase<br/>cognitive/src/.../CognitiveServiceBase.scala"]
    end
    
    subgraph "Traditional ML"
        LGBMRegressor["LightGBMRegressor<br/>lightgbm/src/.../LightGBMRegressor.scala"]
        LGBMClassifier["LightGBMClassifier<br/>lightgbm/src/.../LightGBMClassifier.scala"]
        VWClassifier["VowpalWabbitClassifier<br/>vw/src/.../VowpalWabbitClassifier.scala"]
        IsolationForest["IsolationForest<br/>core/src/.../IsolationForest.scala"]
    end
    
    subgraph "Deep Learning"
        ONNXModel["ONNXModel<br/>deep-learning/src/.../ONNXModel.scala"]
        DeepText["DeepTextClassifier<br/>deep-learning/src/.../DeepTextClassifier.py"]
        DeepVision["DeepVisionClassifier<br/>deep-learning/src/.../DeepVisionClassifier.py"]
    end
    
    subgraph "Core Infrastructure"
        HTTPClient["HTTPClient<br/>core/src/.../HTTPClient.scala"]
        AsyncHTTP["AsyncHTTPClient<br/>core/src/.../AsyncHTTPClient.scala"]
        SMLLogging["SynapseMLLogging<br/>core/src/.../SynapseMLLogging.scala"]
        SecretsObj["Secrets<br/>core/src/.../Secrets.scala"]
        PlatformMod["Platform<br/>core/src/.../Platform.scala"]
    end
    
    subgraph "Custom Data Sources"
        ImageFormat["ImageFileFormat<br/>core/src/.../ImageFileFormat.scala"]
        BinaryFormat["BinaryFileFormat<br/>core/src/.../BinaryFileFormat.scala"]
        HTTPSource["HTTPSource<br/>core/src/.../HTTPSource.scala"]
        HTTPSink["HTTPSink<br/>core/src/.../HTTPSink.scala"]
    end
    
    OpenAIPrompt --> OpenAIChat
    OpenAIChat --> CognitiveBase
    OpenAIEmbed --> CognitiveBase
    CognitiveBase --> HTTPClient
    CognitiveBase --> SecretsObj
    
    LGBMRegressor --> SMLLogging
    VWClassifier --> SMLLogging
    
    ONNXModel --> HTTPClient
    DeepText --> ONNXModel
    DeepVision --> ONNXModel
    
    HTTPClient --> AsyncHTTP
    CognitiveBase --> SMLLogging
    
    SecretsObj --> PlatformMod
    SMLLogging --> PlatformMod
    
    HTTPSource --> HTTPClient
    HTTPSink --> HTTPClient
```

Sources: [README.md:47-64]()

## Spark ML Integration

SynapseML extends Apache Spark's ML library by implementing standard SparkML interfaces. All SynapseML components are `PipelineStage` implementations that can be composed into Spark ML pipelines.

### PipelineStage Hierarchy

```mermaid
graph TB
    PipelineStage["PipelineStage<br/>Spark ML Base Interface"]
    
    Transformer["Transformer<br/>Transform DataFrames"]
    Estimator["Estimator<br/>Fit models from data"]
    Model["Model<br/>Fitted transformers"]
    Evaluator["Evaluator<br/>Compute metrics"]
    
    PipelineStage --> Transformer
    PipelineStage --> Estimator
    Estimator --> Model
    Model --> Transformer
    PipelineStage --> Evaluator
    
    subgraph "SynapseML Transformers"
        OpenAITrans["OpenAIChatCompletion"]
        ONNXTrans["ONNXModel"]
        ImageTrans["ImageTransformer"]
        VWFeaturizer["VowpalWabbitFeaturizer"]
    end
    
    subgraph "SynapseML Estimators"
        LGBMEst["LightGBMClassifier"]
        VWEst["VowpalWabbitClassifier"]
        IsoForest["IsolationForest"]
        DeepTextEst["DeepTextClassifier"]
    end
    
    Transformer --> OpenAITrans
    Transformer --> ONNXTrans
    Transformer --> ImageTrans
    Transformer --> VWFeaturizer
    
    Estimator --> LGBMEst
    Estimator --> VWEst
    Estimator --> IsoForest
    Estimator --> DeepTextEst
```

### Custom Spark Extensions

SynapseML also extends Spark with custom data sources for specialized workloads:

| Extension | Type | Purpose | Key Classes |
|-----------|------|---------|-------------|
| **Image File Format** | `FileFormat` | Distributed image loading with retry logic | `ImageFileFormat` |
| **Binary File Format** | `FileFormat` | Binary file loading with zip archive support | `BinaryFileFormat` |
| **HTTP Source** | Streaming Source | Structured streaming from HTTP endpoints | `HTTPSource`, `HTTPSourceProvider` |
| **HTTP Sink** | Streaming Sink | Structured streaming to HTTP endpoints | `HTTPSink`, `HTTPSinkProvider` |

Sources: [README.md:5-7]()

## Platform Support

SynapseML runs on multiple Spark platforms with platform-aware detection and adaptation. The `Platform` module automatically detects the execution environment and adjusts behavior accordingly.

### Supported Platforms

```mermaid
graph LR
    subgraph "Distribution Channels"
        Maven["Maven Repository<br/>mmlspark.azureedge.net"]
        PyPI["PyPI<br/>synapseml package"]
        Docker["Docker Registry<br/>mcr.microsoft.com/mmlspark"]
    end
    
    subgraph "Execution Platforms"
        Synapse["Azure Synapse<br/>Spark 3.3/3.4/3.5"]
        Fabric["Microsoft Fabric<br/>Pre-installed"]
        Databricks["Databricks<br/>Community/Standard/Premium"]
        HDInsight["Azure HDInsight<br/>Apache Livy"]
        Local["Local Spark<br/>spark-submit/pyspark"]
    end
    
    subgraph "Platform Detection"
        PlatformPy["platform.py<br/>current_platform()"]
        FabricDetect["is_on_fabric()"]
        SynapseDetect["is_on_synapse()"]
        DBDetect["is_on_databricks()"]
    end
    
    Maven --> Synapse
    Maven --> Databricks
    Maven --> HDInsight
    Maven --> Local
    PyPI --> Local
    Docker --> Local
    
    Fabric --> FabricDetect
    Synapse --> SynapseDetect
    Databricks --> DBDetect
    
    FabricDetect --> PlatformPy
    SynapseDetect --> PlatformPy
    DBDetect --> PlatformPy
```

**Platform-specific features**:
- **Fabric**: Pre-installed, uses Fabric telemetry, token library integration
- **Synapse**: Livy batch submission, mssparkutils integration
- **Databricks**: DBUtils secrets integration, GPU/RAPIDS support
- **Local**: Standalone Python deployment via PyPI

For detailed deployment instructions, see [Installation and Distribution](#8.1).

Sources: [README.md:70-260]()

## Language Support

SynapseML supports five languages through auto-generated bindings from Scala implementations:

| Language | Binding Generation | Import Path | Documentation |
|----------|-------------------|-------------|---------------|
| **Scala** | Native implementation | `com.microsoft.azure.synapse.ml.*` | ScalaDoc |
| **Python** | SparkML wrapper generation | `synapse.ml.*` | Sphinx |
| **R** | Automated R wrapper generation | `synapseml` package | RDoc |
| **Java** | Direct Scala interop | `com.microsoft.azure.synapse.ml.*` | JavaDoc |
| **.NET/C#** | Spark .NET bindings | `Synapse.ML.*` | XML docs |

**Example usage across languages**:

```python
# Python
from synapse.ml.lightgbm import LightGBMClassifier
model = LightGBMClassifier(numLeaves=31, numIterations=100)
```

```scala
// Scala
import com.microsoft.azure.synapse.ml.lightgbm.LightGBMClassifier
val model = new LightGBMClassifier().setNumLeaves(31).setNumIterations(100)
```

```r
# R
library(synapseml)
model <- ml_light_gbm_classifier(num_leaves=31, num_iterations=100)
```

For details on wrapper generation, see [Multi-Language SDK Generation](#3.3).

Sources: [README.md:7-9](), [website/src/pages/index.js:115-122]()

## Key Capabilities

SynapseML provides functionality across several ML domains:

### AI Services

| Capability | Components | Use Cases |
|------------|------------|-----------|
| **Azure OpenAI** | `OpenAIPrompt`, `OpenAIChatCompletion`, `OpenAIEmbedding` | LLM inference, chat applications, embeddings |
| **Cognitive Services** | `TextSentiment`, `ComputerVision`, `FaceAPI` | Text analytics, image analysis, face detection |
| **LangChain** | `LangchainTransformer` | Distributed LangChain execution |

See [OpenAI Integration](#6.1) and [Azure Cognitive Services](#6.2) for details.

### Traditional ML

| Capability | Components | Use Cases |
|------------|------------|-----------|
| **LightGBM** | `LightGBMClassifier`, `LightGBMRegressor`, `LightGBMRanker` | Gradient boosting for tabular data |
| **Vowpal Wabbit** | `VowpalWabbitClassifier`, `VowpalWabbitContextualBandit` | Online learning, reinforcement learning |
| **Anomaly Detection** | `IsolationForest` | Outlier detection |

See [LightGBM Integration](#6.5) and [Vowpal Wabbit Integration](#6.6) for details.

### Deep Learning

| Capability | Components | Use Cases |
|------------|------------|-----------|
| **ONNX** | `ONNXModel` | Distributed model inference |
| **PyTorch Lightning** | `DeepTextClassifier`, `DeepVisionClassifier` | Transfer learning, fine-tuning |
| **Horovod** | Distributed training integration | Multi-node deep learning |

See [Deep Learning Integration](#6.4) for details.

### Computer Vision

| Capability | Components | Use Cases |
|------------|------------|-----------|
| **Image Processing** | `ImageTransformer` | Resize, crop, normalize |
| **Image Loading** | `ImageFileFormat` | Distributed image reading |

See [OpenCV Integration](#6.4) for details.

### HTTP Integration

| Capability | Components | Use Cases |
|------------|------------|-----------|
| **HTTP Transformers** | `HTTPTransformer`, Cognitive Services APIs | Microservice orchestration |
| **Streaming** | `HTTPSource`, `HTTPSink` | Real-time HTTP data processing |
| **Serving** | Model serving capabilities | Deploy models as REST APIs |

See [HTTP Client System](#5.2) for details.

Sources: [README.md:47-64](), [website/src/pages/index.js:14-85]()

## Build and Distribution

SynapseML uses an SBT-based build system with modular project structure. The build produces multiple artifact types:

| Artifact Type | Format | Distribution Channel | Versions |
|--------------|--------|---------------------|----------|
| **JARs** | Signed JAR files | Maven Central, mmlspark.azureedge.net | 1.1.0 (Spark 3.5), 1.0.15 (Spark 3.4), 0.11.4 (Spark 3.3) |
| **Python Wheel** | `.whl` package | PyPI (`synapseml`) | Matches JAR versions |
| **Docker Images** | Container images | mcr.microsoft.com/mmlspark/release | demo, minimal, developer |
| **R Package** | R package | Automated generation | synapse.ml |
| **Documentation** | HTML sites | GitHub Pages, Blob Storage | API docs, website |

**Maven coordinates**: `com.microsoft.azure:synapseml_2.12:1.1.0`

**PyPI package**: `pip install synapseml`

For build system details, see [Build System](#3.2). For release process, see [CI/CD Pipeline](#3.1).

Sources: [README.md:175-224]()

## Testing Infrastructure

SynapseML employs comprehensive testing across multiple dimensions:

| Test Type | Coverage | Execution Environment |
|-----------|----------|----------------------|
| **Unit Tests** | Scala, Python, R | Local Spark |
| **Fuzzing Tests** | All PipelineStages | Automated discovery |
| **E2E Synapse** | Production scenarios | Azure Synapse Spark pools |
| **E2E Databricks** | GPU/CPU workloads | Databricks clusters (CPU, GPU, RAPIDS) |
| **Website Tests** | Documentation code blocks | pytest-codeblocks |
| **Security Scans** | CodeQL, OSSF Scorecards | GitHub Actions |

For testing details, see [Testing Infrastructure](#4).

Sources: [README.md:11-18]()

## Getting Started

To start using SynapseML:

1. **Choose a platform**: Synapse, Fabric, Databricks, or local Spark
2. **Install SynapseML**: Follow platform-specific instructions in [Installation and Distribution](#8.1)
3. **Import the library**: `from synapse.ml.* import *` (Python) or `import com.microsoft.azure.synapse.ml.*` (Scala)
4. **Build pipelines**: Compose SynapseML components with SparkML stages
5. **Scale**: Run on single-node or multi-node clusters

**Next steps**:
- For installation instructions: See [Deployment](#8)
- For example notebooks: See [Example Notebooks](#7.3)
- For API documentation: See [API Reference](https://mmlspark.blob.core.windows.net/docs/1.1.0/scala/index.html)
- For contributing: See [CONTRIBUTING.md:1-81]()

Sources: [README.md:66-270](), [website/src/pages/index.js:158-430]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



## Purpose and Scope

This document describes the overall architecture and design principles of SynapseML. It explains how the system is organized into modular components, how it integrates with Apache Spark, and how it adapts to different deployment environments.

For detailed information about specific subsystems:
- Module-specific implementation details: see [System Components](#2.1)
- Spark integration patterns: see [Integration with Spark](#2.2)
- Platform-specific behavior: see [Platform Detection and Adaptation](#2.3)
- Build and release infrastructure: see [Development Infrastructure](#3)
- Testing strategies: see [Testing Infrastructure](#4)

---

## Core Design Principles

SynapseML is designed around several fundamental architectural principles that guide all implementation decisions:

### Built on Apache Spark

SynapseML is built as a native extension to Apache Spark, leveraging Spark's distributed computing capabilities. The library requires Spark 3.4+ and Scala 2.12.17, as specified in [build.sbt:10-13](). All components are designed to operate on Spark DataFrames and RDDs, enabling seamless scalability from single-node to large cluster deployments.

### SparkML Pipeline Compatibility

All machine learning components implement Spark's `PipelineStage` interface, making them fully compatible with SparkML pipelines. This allows SynapseML transformers and estimators to be chained together with native Spark components. The library follows Spark's `MLReadable` and `MLWritable` interfaces for model serialization and persistence.

### Multi-Language Support

While implemented primarily in Scala, SynapseML automatically generates bindings for Python (PySpark), R (SparklyR), and .NET. This wrapper generation mechanism ensures consistent APIs across all supported languages. The build system produces language-specific artifacts that are published to appropriate repositories (Maven Central for JVM, PyPI for Python, NuGet for .NET).

### Platform Adaptation

SynapseML includes platform detection mechanisms that allow it to adapt behavior based on the execution environment (Azure Synapse Analytics, Microsoft Fabric, Databricks, standalone Spark). This enables seamless deployment across different platforms without code changes.

Sources: [README.md:1-10](), [build.sbt:10-13](), [CONTRIBUTING.md:36-43]()

---

## Modular Component Architecture

SynapseML is organized into six core modules, each providing specialized functionality. This modular design allows users to include only the components they need and enables independent development and testing of each module.

### Module Structure

```mermaid
graph TB
    subgraph "Core Module"
        CoreLib["synapseml-core<br/>com.microsoft.azure.synapse.ml.core"]
        CoreInfra["HTTP Clients<br/>Logging<br/>Secret Management<br/>Parameters"]
        CoreFormats["Custom FileFormats<br/>ImageFileFormat<br/>BinaryFileFormat"]
        CoreML["Core ML Components<br/>IsolationForest<br/>Featurizers"]
    end
    
    subgraph "Cognitive Module"
        CogLib["synapseml-cognitive<br/>com.microsoft.azure.synapse.ml.cognitive"]
        OpenAI["OpenAI Services<br/>OpenAIChatCompletion<br/>OpenAIEmbedding<br/>OpenAIPrompt"]
        AzureAI["Azure Cognitive Services<br/>Vision, Text, Speech, Form"]
        LangChain["LangchainTransformer"]
    end
    
    subgraph "Deep Learning Module"
        DLLib["synapseml-deep-learning<br/>com.microsoft.azure.synapse.ml.onnx"]
        ONNX["ONNXModel<br/>Distributed Inference"]
        Horovod["Horovod Integration<br/>Distributed Training"]
        PTL["PyTorch Lightning<br/>DeepTextClassifier<br/>DeepVisionClassifier"]
    end
    
    subgraph "LightGBM Module"
        LGBMLib["synapseml-lightgbm<br/>com.microsoft.azure.synapse.ml.lightgbm"]
        LGBMEst["LightGBMClassifier<br/>LightGBMRegressor<br/>LightGBMRanker"]
    end
    
    subgraph "Vowpal Wabbit Module"
        VWLib["synapseml-vw<br/>com.microsoft.azure.synapse.ml.vw"]
        VWEst["VowpalWabbitClassifier<br/>VowpalWabbitRegressor<br/>VowpalWabbitContextualBandit"]
    end
    
    subgraph "OpenCV Module"
        CVLib["synapseml-opencv<br/>com.microsoft.azure.synapse.ml.opencv"]
        CVOps["Image Transformations<br/>SuperpixelTransformer<br/>ImageFeaturizer"]
    end
    
    CogLib --> CoreLib
    DLLib --> CoreLib
    DLLib --> CVLib
    LGBMLib --> CoreLib
    VWLib --> CoreLib
    CVLib --> CoreLib
    
    CoreLib --> CoreInfra
    CoreLib --> CoreFormats
    CoreLib --> CoreML
    
    CogLib --> OpenAI
    CogLib --> AzureAI
    CogLib --> LangChain
    
    DLLib --> ONNX
    DLLib --> Horovod
    DLLib --> PTL
    
    LGBMLib --> LGBMEst
    VWLib --> VWEst
    CVLib --> CVOps
```

**Module Dependencies and Maven Coordinates**

This diagram shows the module organization as defined in the SBT build configuration, including Maven group IDs and artifact names used for distribution.

Sources: [build.sbt:267-324](), [README.md:181-223]()

---

### Module Descriptions

| Module | Artifact Name | Primary Dependencies | Description |
|--------|--------------|---------------------|-------------|
| **core** | `synapseml-core` | `spark-core`, `spark-mllib`, `spark-avro` | Foundational infrastructure including HTTP clients, logging, parameter management, secret handling, and core ML algorithms like Isolation Forest |
| **cognitive** | `synapseml-cognitive` | `core`, `client-sdk` (Speech SDK) | Azure OpenAI and Cognitive Services integrations, including chat completion, embeddings, vision, text analytics, and speech services |
| **deep-learning** | `synapseml-deep-learning` | `core`, `opencv`, `onnxruntime_gpu`, `onnx-protobuf` | ONNX model inference, Horovod distributed training, and PyTorch Lightning-based classifiers |
| **lightgbm** | `synapseml-lightgbm` | `core`, `lightgbmlib` | LightGBM gradient boosting implementations for classification, regression, and ranking |
| **vw** | `synapseml-vw` | `core`, `vw-jni` | Vowpal Wabbit online learning algorithms including contextual bandits |
| **opencv** | `synapseml-opencv` | `core`, `opencv` | Computer vision operations and image transformations |

Sources: [build.sbt:267-324]()

---

## Build System Architecture

SynapseML uses SBT (Scala Build Tool) as its primary build system, with a sophisticated multi-stage build process that produces artifacts for multiple languages and platforms.

### SBT Project Structure

```mermaid
graph TB
    subgraph "Root Aggregator Project"
        RootSBT["root<br/>(aggregates all modules)"]
    end
    
    subgraph "Module Projects"
        CoreSBT["core project<br/>file: core/"]
        DeepLearningSBT["deepLearning project<br/>file: deep-learning/"]
        CognitiveSBT["cognitive project<br/>file: cognitive/"]
        VWSBT["vw project<br/>file: vw/"]
        LightGBMSBT["lightgbm project<br/>file: lightgbm/"]
        OpenCVSBT["opencv project<br/>file: opencv/"]
    end
    
    subgraph "Build Plugins"
        CodegenPlugin["CodegenPlugin<br/>(auto-generates wrappers)"]
        PublishPlugin["PublishPlugin<br/>(manages secrets)"]
        UnidocPlugin["ScalaUnidocPlugin<br/>(generates API docs)"]
        BuildInfoPlugin["BuildInfoPlugin<br/>(version info)"]
    end
    
    subgraph "Build Tasks"
        Compile["compile<br/>(Scala compilation)"]
        Test["test<br/>(ScalaTest execution)"]
        Package["packagePython<br/>(Python wheel generation)"]
        Publish["publishBlob<br/>publishDocs<br/>publishPypi"]
        Codegen["codegen<br/>(wrapper generation)"]
    end
    
    RootSBT --> CoreSBT
    RootSBT --> DeepLearningSBT
    RootSBT --> CognitiveSBT
    RootSBT --> VWSBT
    RootSBT --> LightGBMSBT
    RootSBT --> OpenCVSBT
    
    CoreSBT --> BuildInfoPlugin
    RootSBT --> UnidocPlugin
    
    CoreSBT -.->|enables| Compile
    CoreSBT -.->|enables| Test
    CoreSBT -.->|enables| Package
    CoreSBT -.->|enables| Codegen
    
    RootSBT -.->|enables| Publish
    PublishPlugin -.->|provides| Publish
```

**SBT Multi-Module Project Configuration**

This diagram illustrates how the root SBT project aggregates six module projects, each with independent compilation and testing capabilities.

Sources: [build.sbt:267-344]()

---

### Build Configuration

The build system is configured with several key settings defined in [build.sbt:1-264]():

**Version and Scala Configuration:**
```
sparkVersion = "3.5.0"
scalaVersion = "2.12.17"
organization = "com.microsoft.azure"
```

**Dependency Management:**
- Core dependencies include `spark-core`, `spark-mllib`, and `spark-avro` with compile scope
- Test dependencies include `scalatest` and `spark-tags`
- Module-specific dependencies are declared in each module's configuration
- Dependency exclusions prevent version conflicts (e.g., excluding `protobuf-java` from transitive dependencies)

**Custom Build Tasks:**
- `getDatasetsTask`: Downloads test datasets from Azure Blob Storage
- `packageSynapseML`: Aggregates all Python modules into a single wheel
- `publishPypi`: Publishes Python package to PyPI using Twine
- `publishDocs`: Generates and uploads Scala and Python API documentation
- `generatePythonDoc`: Uses Sphinx to generate Python API documentation
- `convertNotebooks`: Converts Jupyter notebooks to markdown for website

**POM Post-Processing:**
The build includes custom POM transformation logic [build.sbt:50-70]() that removes scoped dependencies and excludes certain artifacts from the published Maven POM to ensure clean dependency resolution.

Sources: [build.sbt:1-368]()

---

## Distribution and Artifact Pipeline

SynapseML artifacts are built and distributed through multiple channels to support different deployment scenarios.

### Artifact Generation Flow

```mermaid
graph LR
    subgraph "Source Code"
        ScalaSource["Scala Source Code<br/>.scala files"]
    end
    
    subgraph "Compilation Stage"
        SBTCompile["sbt compile<br/>Scala → JVM bytecode"]
        Codegen["sbt codegen<br/>Generate wrappers"]
    end
    
    subgraph "Language Bindings"
        PythonGen["Python Wrappers<br/>.py files"]
        RGen["R Wrappers<br/>.R files"]
        DotNetGen[".NET Wrappers<br/>.cs files"]
    end
    
    subgraph "Packaging"
        JARPackage["JAR Packaging<br/>sbt publishLocalSigned"]
        PythonPackage["Python Wheel<br/>setup.py bdist_wheel"]
        RPackage["R Package<br/>DESCRIPTION + NAMESPACE"]
        DocsPackage["API Docs<br/>ScalaUnidoc + Sphinx"]
    end
    
    subgraph "Signing"
        ESRP["ESRP Signing<br/>(JARs only)"]
        PGP["PGP Signing<br/>(Maven artifacts)"]
    end
    
    subgraph "Distribution Channels"
        Maven["Maven Central<br/>com.microsoft.azure:synapseml_2.12"]
        PyPI["PyPI<br/>pynapseml package"]
        AzureBlob["Azure Blob Storage<br/>mmlspark.blob.core.windows.net"]
        Docker["Docker Registry<br/>mcr.microsoft.com/mmlspark"]
    end
    
    ScalaSource --> SBTCompile
    SBTCompile --> Codegen
    
    Codegen --> PythonGen
    Codegen --> RGen
    Codegen --> DotNetGen
    
    SBTCompile --> JARPackage
    PythonGen --> PythonPackage
    RGen --> RPackage
    
    JARPackage --> ESRP
    JARPackage --> PGP
    
    ESRP --> Maven
    PGP --> Maven
    PythonPackage --> PyPI
    JARPackage --> AzureBlob
    PythonPackage --> AzureBlob
    RPackage --> AzureBlob
    DocsPackage --> AzureBlob
    
    JARPackage --> Docker
```

**Artifact Build and Distribution Pipeline**

This diagram shows how source code is compiled, wrapped for multiple languages, packaged, signed, and distributed to various channels.

Sources: [build.sbt:132-220](), [pipeline.yaml:87-134](), [tools/esrp/prepare_jar.py:1-80]()

---

### Distribution Channels

**Maven Central** ([README.md:176-183]())
- Primary distribution for JVM (Scala/Java) users
- Maven coordinates: `com.microsoft.azure:synapseml_2.12:1.1.0`
- Includes signed JARs with PGP signatures
- Published via Sonatype OSSRH with ESRP signing process

**PyPI** ([README.md:191-203]())
- Python package: `pip install synapseml`
- Contains unified wheel with all modules
- Generated from aggregated Python wrappers [build.sbt:132-185]()
- Published using Twine with API token authentication

**Azure Blob Storage** ([README.md:106-113]())
- Custom Maven repository: `https://mmlspark.azureedge.net/maven`
- Houses documentation, notebooks, and build artifacts
- Used for snapshot versions and internal testing
- Accessed via Azure CLI for publishing

**Docker Images** ([README.md:242-254]())
- Published to Microsoft Container Registry (MCR)
- Three variants: demo, minimal, release
- Include pre-configured Jupyter environments
- Based on Apache Spark base images

Sources: [README.md:70-260](), [sonatype.sbt:1-46](), [project/Secrets.scala:1-194]()

---

## Integration Points

### Spark SQL and DataFrames

SynapseML operates primarily on Spark DataFrames, leveraging Spark SQL's catalyst optimizer for query planning. All transformers and estimators accept DataFrames as input and produce DataFrames as output, maintaining compatibility with the broader Spark ecosystem.

### SparkML Pipeline API

Components implement the following core interfaces:
- `Transformer`: Implements `transform(dataset: DataFrame): DataFrame`
- `Estimator`: Implements `fit(dataset: DataFrame): Model`
- `Model`: Extends `Transformer` with learned parameters
- `MLWritable`/`MLReadable`: For model serialization

### Custom Data Sources

SynapseML extends Spark's data source API with custom implementations:
- `ImageFileFormat`: Reads image files into DataFrame format with retry logic
- `BinaryFileFormat`: Handles binary files with zip support
- `HTTPSource`/`HTTPSink`: Enables HTTP-based structured streaming

### Structured Streaming

The library provides streaming-compatible transformers and sources that integrate with Spark's continuous processing model, enabling real-time ML inference on streaming data.

Sources: [CONTRIBUTING.md:36-43]()

---

## Deployment Configuration

SynapseML adapts its configuration based on the target platform. Each deployment scenario requires specific Spark configuration parameters.

### Platform-Specific Configuration

**Microsoft Fabric** ([README.md:96-113]())
```
spark.jars.packages: com.microsoft.azure:synapseml_2.12:<version>
spark.jars.repositories: https://mmlspark.azureedge.net/maven
spark.jars.excludes: org.scala-lang:scala-reflect,...
spark.yarn.user.classpath.first: true
```

**Azure Synapse Analytics** ([README.md:118-172]())
- Spark 3.3, 3.4, and 3.5 pools supported
- Different SynapseML versions per Spark version
- Configured via notebook `%%configure` magic or pool-level settings

**Databricks** ([README.md:174-189]())
- Installed via Maven coordinates in cluster libraries
- Minimum: Spark 3.2 and Scala 2.12
- DBR 10.1+ recommended to avoid Netty conflicts

**Standalone Spark** ([README.md:191-214]())
- Via `spark-shell --packages` or `pyspark --packages`
- Or programmatically: `spark.jars.packages` in SparkSession builder

Sources: [README.md:70-260]()

---

## Secret and Credential Management

SynapseML implements a centralized secret management system defined in [project/Secrets.scala:1-194]() that abstracts credential retrieval across different environments.

### Secret Retrieval Architecture

```mermaid
graph TB
    subgraph "Secret Sources"
        EnvVars["Environment Variables<br/>(CI/CD Pipeline)"]
        AzureKV["Azure Key Vault<br/>mmlspark-keys"]
        LocalCache["Local File Cache<br/>.cache/ directory"]
    end
    
    subgraph "Secrets Object"
        SecretManager["Secrets.scala<br/>getSecret() method"]
        Priority["Priority Logic:<br/>1. Env Var<br/>2. Cache<br/>3. Key Vault"]
    end
    
    subgraph "Build System"
        SBTPublish["sbt publishBlob<br/>publishPypi<br/>publishLocalSigned"]
        PGPFiles["PGP Key Files<br/>.cache/pgp-private.asc<br/>.cache/pgp-public.asc"]
    end
    
    subgraph "Credentials"
        NexusCreds["Maven Central<br/>nexus-un, nexus-pw"]
        PGPCreds["PGP Signing<br/>pgp-pw, pgp-public, pgp-private"]
        PyPICreds["PyPI Publishing<br/>pypi-api-token"]
        ADOCreds["ADO Feed<br/>ado-feed-token"]
    end
    
    EnvVars --> SecretManager
    AzureKV --> SecretManager
    LocalCache --> SecretManager
    
    SecretManager --> Priority
    Priority --> SBTPublish
    
    SBTPublish --> NexusCreds
    SBTPublish --> PGPCreds
    SBTPublish --> PyPICreds
    SBTPublish --> ADOCreds
    
    PGPCreds --> PGPFiles
```

**Build-Time Secret Management Flow**

The secret management system prioritizes environment variables (set by CI/CD), then falls back to local cache (for PGP keys), and finally queries Azure Key Vault if neither is available.

Sources: [project/Secrets.scala:1-194](), [sonatype.sbt:29-46]()

---

### Secret Lifecycle

**Discovery Phase** ([project/Secrets.scala:130-138]()):
1. Check for environment variable (e.g., `NEXUS-UN`, `PGP-PW`)
2. If not found, check local cache file in `.cache/` directory
3. If not found, execute Azure CLI command to fetch from Key Vault
4. Cache the secret locally for subsequent builds

**PGP Key Handling** ([project/Secrets.scala:96-108]()):
- PGP keys are stored as Base64-encoded strings in Key Vault
- Decoded and written to `.cache/pgp-private.asc` and `.cache/pgp-public.asc`
- These files are referenced by the SBT PGP plugin for JAR signing

**Publishing Control** ([project/Secrets.scala:17-19]()):
- Publishing is gated by `SYNAPSEML_ENABLE_PUBLISH` environment variable
- If `false`, secret retrieval is skipped and warnings are logged
- This prevents accidental publishing during local development

Sources: [project/Secrets.scala:1-194]()

---

## Conda Environment Management

The development and CI/CD pipeline uses Conda for consistent Python environment management across different platforms.

### Environment Specification

The [environment.yml:1-58]() file defines all dependencies:

**Python and Core Tools:**
- Python 3.11.8
- PySpark 3.5.0
- PyArrow 10.0.1
- Pandas 2.0.3

**Machine Learning Frameworks:**
- PyTorch 2.1.0 and TorchVision 0.16.0
- Horovod (compiled from specific commit)
- PyTorch Lightning 1.5.0
- Transformers 4.49.0

**Development Tools:**
- Sphinx for documentation generation
- pytest and pytest-cov for testing
- Black for code formatting
- Jupyter for notebooks

**Azure Integration:**
- azure-storage-blob for blob storage access
- MLflow for experiment tracking

Sources: [environment.yml:1-58]()

---

### Conda Environment Caching

The CI/CD pipeline implements aggressive caching of the Conda environment to reduce build times, as configured in [templates/conda.yml:1-42]():

**Cache Strategy:**
- Cache key: `'conda | "$(Agent.OS)" | environment.yml'`
- Cached directory: `/usr/share/miniconda/envs` (stored in `CONDA_CACHE_DIR`)
- Cache restored before environment creation
- 30-minute timeout with automatic retry

**Disk Space Management:**
The pipeline includes a cleanup step that removes unused SDKs (Android, Google Cloud) to free disk space before creating the Conda environment, addressing common disk space issues on Azure DevOps agents.

Sources: [templates/conda.yml:1-42](), [pipeline.yaml:60-94]()

---

## CI/CD Integration Architecture

The Azure DevOps pipeline orchestrates all build, test, and release activities through a series of jobs defined in [pipeline.yaml:1-773]().

### Pipeline Job Structure

```mermaid
graph TB
    subgraph "Trigger Events"
        GitPush["Git Push to master/spark3.3/spark3.5"]
        PullRequest["Pull Request"]
        Schedule["Daily Cron: 0 0 * * *"]
    end
    
    subgraph "Preparation Jobs"
        Style["Style Job<br/>scalastyle + black"]
        CondaCache["BuildAndCacheCondaEnv<br/>Conda environment setup"]
    end
    
    subgraph "Build and Publish"
        Publish["Publish Job<br/>sbt packagePython<br/>publishBlob<br/>publishDocs"]
    end
    
    subgraph "Testing Jobs"
        UnitTests["UnitTests Job<br/>30+ test packages<br/>Matrix strategy"]
        PythonTests["PythonTests Job<br/>7 packages<br/>Matrix strategy"]
        RTests["RTests Job<br/>6 packages<br/>Matrix strategy"]
        WebsiteTests["WebsiteSamplesTests<br/>pytest-codeblocks"]
    end
    
    subgraph "E2E Testing"
        E2E["E2E Job<br/>databricks-cpu<br/>databricks-gpu"]
    end
    
    subgraph "Documentation"
        Website["WebsiteAutoDeployment<br/>Docusaurus build<br/>GitHub Pages deploy"]
    end
    
    subgraph "Release"
        Release["Release Job<br/>PyPI publish<br/>Maven Central (ESRP)<br/>GitHub Release"]
    end
    
    GitPush --> Style
    PullRequest --> Style
    Schedule --> Style
    
    Style --> CondaCache
    Style --> Publish
    Style --> UnitTests
    Style --> PythonTests
    Style --> RTests
    Style --> WebsiteTests
    Style --> E2E
    Style --> Website
    
    Publish --> Release
    
    Release -.->|"Conditional:<br/>master + tag v*"| PyPI["PyPI"]
    Release -.->|"Conditional:<br/>master + tag v*"| MavenCentral["Maven Central"]
```

**Azure DevOps Pipeline Job Dependencies**

This diagram shows the pipeline's job structure, including conditional release logic that only triggers for tagged commits on master.

Sources: [pipeline.yaml:1-773]()

---

### Key Pipeline Jobs

**Style Job** ([pipeline.yaml:66-84]()):
- Runs Scala style check via `sbt scalastyle test:scalastyle`
- Runs Python style check via Black formatter
- Gates all other jobs (fails fast on style violations)

**Publish Job** ([pipeline.yaml:87-134]()):
- Generates all artifacts: JARs, Python wheels, R packages, documentation
- Uploads notebooks to Azure Blob Storage
- Publishes badges (version info) to blob storage
- Runs on every commit (not just releases)

**UnitTests Job** ([pipeline.yaml:614-772]()):
- Matrix strategy with 30+ test packages
- Each package runs independently in parallel
- Includes retry logic for flaky tests (Azure Cognitive Services)
- Generates code coverage reports for Codecov

**E2E Job** ([pipeline.yaml:138-181]()):
- Tests on Databricks CPU and GPU clusters
- Executes notebooks as Python scripts
- Provisions ephemeral test clusters
- 120-minute timeout per test run

**Release Job** ([pipeline.yaml:259-353]()):
- Only executes when: `master` branch + Git tag starting with `v`
- Publishes Python wheel to PyPI using Twine
- Signs JARs with ESRP and publishes to Maven Central
- Creates GitHub release with CHANGELOG

Sources: [pipeline.yaml:1-773]()

---

## Version Management and Branching

SynapseML uses a multi-branch strategy to support different Spark versions:

**Active Branches:**
- `master`: Spark 3.5 (current development)
- `spark3.3`: Spark 3.3 support
- `spark3.5`: Spark 3.5 support (may be redundant with master)

**Version Determination:**
Versions are determined dynamically using the `sbt-dynver` plugin, which generates versions from Git tags and commit hashes. Snapshot versions follow the pattern: `<version>-<commits>-<hash>`.

**Release Process:**
1. Tag a commit on `master` with format `v1.x.x`
2. Pipeline detects the tag and triggers Release job
3. CHANGELOG is auto-generated using `git-chglog`
4. Artifacts are signed and published to all channels
5. GitHub Release is created as draft for manual verification

Sources: [pipeline.yaml:4-43](), [pipeline.yaml:265-283](), [sonatype.sbt:45-46]()

---

# Page: System Components

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



This page details the modular structure of SynapseML, including the core, cognitive, deep learning, LightGBM, VW, and OpenCV modules. SynapseML is organized as a collection of SBT projects that compile into separate JAR artifacts but work together to provide machine learning capabilities at scale. For information on how these modules extend Apache Spark's functionality, see [Integration with Spark](#2.2).

## Module Architecture

SynapseML is structured as six distinct SBT modules, each providing specialized machine learning capabilities. The modules are defined in `build.sbt` and can be used independently or together.

### SBT Module Structure

```mermaid
graph TB
    root["root module<br/>(aggregator)"]
    
    core["core module<br/>synapseml-core<br/>Base functionality"]
    deepLearning["deepLearning module<br/>synapseml-deep-learning<br/>ONNX + PyTorch"]
    cognitive["cognitive module<br/>synapseml-cognitive<br/>Azure AI Services"]
    lightgbm["lightgbm module<br/>synapseml-lightgbm<br/>Gradient Boosting"]
    vw["vw module<br/>synapseml-vw<br/>Vowpal Wabbit"]
    opencv["opencv module<br/>synapseml-opencv<br/>Computer Vision"]
    
    root --> core
    root --> deepLearning
    root --> cognitive
    root --> lightgbm
    root --> vw
    root --> opencv
    
    deepLearning -.->|depends on| core
    deepLearning -.->|depends on| opencv
    cognitive -.->|depends on| core
    lightgbm -.->|depends on| core
    vw -.->|depends on| core
    opencv -.->|depends on| core
```

**Module Dependency Structure**

| Module | Artifact Name | Dependencies | Purpose |
|--------|--------------|--------------|---------|
| `core` | `synapseml-core` | Spark 3.5.0, spray-json, httpcomponents | Foundational infrastructure, HTTP clients, logging, file formats |
| `deepLearning` | `synapseml-deep-learning` | `core`, `opencv`, ONNX, pytorch_lightning | ONNX inference, Horovod training, PyTorch integration |
| `cognitive` | `synapseml-cognitive` | `core`, Azure Speech SDK | OpenAI, Azure Cognitive Services, LangChain |
| `lightgbm` | `synapseml-lightgbm` | `core`, lightgbmlib 3.3.510 | LightGBM classification, regression, ranking |
| `vw` | `synapseml-vw` | `core`, vw-jni 9.3.0 | Vowpal Wabbit classifiers, regressors, contextual bandits |
| `opencv` | `synapseml-opencv` | `core`, opencv 3.2.0-1 | OpenCV-based image transformations |

Sources: [build.sbt:267-324](), [build.sbt:326-344]()

## Core Module (`synapseml-core`)

The `core` module provides foundational infrastructure that all other SynapseML modules depend on. It contains shared utilities, HTTP clients, logging systems, and Spark integrations.

### Package Structure

The core module is organized under `com.microsoft.azure.synapse.ml` with the following key packages:

```mermaid
graph TB
    core["com.microsoft.azure.synapse.ml.core"]
    io["com.microsoft.azure.synapse.ml.io"]
    logging["com.microsoft.azure.synapse.ml.logging"]
    stages["com.microsoft.azure.synapse.ml.stages"]
    featurize["com.microsoft.azure.synapse.ml.featurize"]
    
    core --> schema["schema<br/>DatasetExtensions"]
    core --> env["env<br/>FileUtilities"]
    
    io --> http["http<br/>HTTPTransformer,<br/>SharedSingleton"]
    io --> image["image<br/>ImageFileFormat"]
    io --> binary["binary<br/>BinaryFileFormat"]
    
    logging --> SynapseMLLogging["SynapseMLLogging trait<br/>Platform-aware telemetry"]
    
    stages --> Lambda["Lambda<br/>UDFTransformer"]
    stages --> FixedMiniBatchTransformer["FixedMiniBatchTransformer<br/>Batching utilities"]
```

### Core Dependencies

The core module depends on:
- **Apache Spark 3.5.0**: `spark-core`, `spark-mllib`, `spark-avro` (excludes older protobuf)
- **HTTP Libraries**: Apache HttpComponents Client5 5.1.3, httpmime 4.5.13
- **JSON Processing**: spray-json 1.3.5
- **Isolation Forest**: LinkedIn isolation-forest 3.0.5
- **Testing**: ScalaTest 3.2.14, GlobalMentor hadoop-bare-naked-local-fs

Sources: [build.sbt:23-43](), [build.sbt:267-280]()

### Core Functionality

The core module provides several critical systems:

#### HTTP Client Infrastructure

Enables distributed HTTP communication for calling external APIs at scale:
- `HTTPTransformer`: Base class for HTTP-based transformers
- `SharedSingleton`: Connection pooling for efficient HTTP communication
- Support for both synchronous and asynchronous HTTP patterns

#### Custom Spark Data Sources

Extended file format support for ML workloads:
- `ImageFileFormat`: Reads images into Spark DataFrames with retry logic
- `BinaryFileFormat`: Reads binary files with zip archive support
- Patched implementations to handle flakiness in distributed file systems

#### Spark ML Extensions

Enhanced pipeline components:
- `Lambda` and `UDFTransformer`: Apply arbitrary functions as pipeline stages
- `FixedMiniBatchTransformer`: Batch DataFrame rows for efficient processing
- `DatasetExtensions`: Additional DataFrame operations

Sources: [build.sbt:267-280](), [README.md:5-9]()

### Testing Infrastructure

The core module includes comprehensive testing utilities used across all modules:

```mermaid
graph TB
    TestBase["TestBase trait<br/>Common test utilities"]
    
    TestBase --> SparkSession["Spark session<br/>management"]
    TestBase --> DataComparison["DataFrame comparison<br/>utilities"]
    TestBase --> FileHandling["Test file path<br/>resolution"]
    
    TestBase --> Retry["Retry mechanisms<br/>for flaky tests"]
    TestBase --> Secrets["Secret loading<br/>from KeyVault"]
```

The testing framework supports:
- Automatic Spark session management for tests
- DataFrame comparison with configurable tolerance
- Test dataset loading from `datasetDir` build setting
- Integration with Azure Key Vault for test secrets

Sources: [build.sbt:72-89](), [pipeline.yaml:614-772]()

## Cognitive Module (`synapseml-cognitive`)

The `cognitive` module provides Spark integrations for Azure AI Services, OpenAI, and other cloud-based AI APIs. It depends on the `core` module and adds the Azure Speech SDK.

### Dependencies

```scala
libraryDependencies += "com.microsoft.cognitiveservices.speech" % "client-sdk" % "1.24.1"
```

The module also includes Hadoop dependencies for Azure blob storage access during testing.

Sources: [build.sbt:308-317]()

### Package Structure

The cognitive module is organized under `com.microsoft.azure.synapse.ml.services`:

```mermaid
graph TB
    services["com.microsoft.azure.synapse.ml.services"]
    
    services --> openai["openai<br/>OpenAIChatCompletion<br/>OpenAIEmbedding<br/>OpenAIPrompt"]
    services --> text["text<br/>TextAnalytics<br/>LanguageDetector<br/>EntityDetector"]
    services --> speech["speech<br/>SpeechToText<br/>SpeechToTextSDK<br/>TextToSpeech"]
    services --> vision["vision<br/>AnalyzeImage<br/>RecognizeText<br/>DescribeImage"]
    services --> anomaly["anomaly<br/>DetectAnomalies<br/>DetectLastAnomaly"]
    services --> search["search<br/>AzureSearchWriter<br/>AddDocuments"]
    services --> form["form<br/>AnalyzeDocument<br/>AnalyzeLayout"]
    services --> translate["translate<br/>Translate<br/>Transliterate"]
    services --> bing["bing<br/>BingImageSearch"]
    services --> face["face<br/>DetectFace<br/>FindSimilarFace"]
```

### OpenAI Integration

The OpenAI package provides transformers for leveraging OpenAI and Azure OpenAI services:

**Core Classes:**
- `OpenAIChatCompletion`: Chat completion with streaming support
- `OpenAIEmbedding`: Text embedding generation
- `OpenAIPrompt`: Template-based prompt construction with multimodal support
- `OpenAIDefaults`: Global parameter defaults

**Key Features:**
- Support for both OpenAI API and Azure OpenAI endpoints
- Streaming responses with Server-Sent Events (SSE)
- Multimodal inputs (text + images)
- Response format specification (JSON schema)
- Token usage tracking and rate limiting

Sources: [pipeline.yaml:645-650](), [README.md:52-53]()

### Azure Cognitive Services

The cognitive module includes wrappers for multiple Azure Cognitive Services APIs:

#### Text Analytics
- `LanguageDetector`: Detect language from text
- `EntityDetector`, `NER`, `PII`: Named entity recognition
- `TextSentiment`: Sentiment analysis
- `KeyPhraseExtractor`: Extract key phrases
- `AnalyzeHealthText`: Medical text analysis

#### Speech Services
- `SpeechToText`: REST API-based speech recognition
- `SpeechToTextSDK`: SDK-based speech recognition with websockets
- `TextToSpeech`: Text-to-speech synthesis
- `ConversationTranscription`: Multi-speaker transcription
- `SpeakerEmotionInference`: Emotion detection from speech

#### Computer Vision
- `AnalyzeImage`: Image content analysis
- `RecognizeText`: OCR text extraction
- `DescribeImage`: Generate image captions
- `TagImage`: Automatic image tagging
- `RecognizeDomainSpecificContent`: Celebrity/landmark recognition

#### Other Services
- Anomaly Detection (`DetectAnomalies`, `SimpleDetectAnomalies`)
- Form Recognizer (`AnalyzeDocument`, `AnalyzeLayout`)
- Translator (`Translate`, `Transliterate`, `DetectLanguage`)
- Bing Search (`BingImageSearch`)
- Face API (`DetectFace`, `VerifyFaces`, `FindSimilarFace`)

Sources: [pipeline.yaml:639-671](), [README.md:52-53]()

### LangChain Integration

The cognitive module includes `LangchainTransformer` for distributed execution of LangChain chains:

- Executes LangChain chains across Spark DataFrame rows
- Supports question answering, summarization, and custom chains
- Integrates with vector stores and retrievers

Sources: [README.md:58-59]()

### Service Architecture

All cognitive services extend common base classes:

```mermaid
graph TB
    CognitiveServiceBase["CognitiveServiceBase<br/>Abstract base class"]
    HasServiceParams["HasServiceParams<br/>Parameter management trait"]
    
    CognitiveServiceBase --> HasCognitiveServiceInput["HasCognitiveServiceInput<br/>Input column handling"]
    CognitiveServiceBase --> HasInternalJsonOutputParser["HasInternalJsonOutputParser<br/>Response parsing"]
    CognitiveServiceBase --> HasSetLocation["HasSetLocation<br/>Region configuration"]
    
    HasServiceParams --> ServiceParam["ServiceParam[T]<br/>Scalar or column values"]
    
    CognitiveServiceBase -.->|extends| OpenAIServicesBase
    CognitiveServiceBase -.->|extends| TextAnalyticsBase
    CognitiveServiceBase -.->|extends| SpeechServicesBase
```

Common patterns:
- `ServiceParam[T]` allows parameters to be either fixed values or DataFrame columns
- `HasInternalJsonOutputParser` standardizes JSON response parsing
- `HasSetLocation` manages Azure region configuration
- `HasCognitiveServiceInput` handles input column mapping

Sources: [build.sbt:308-317](), [pipeline.yaml:639-671]()

## Deep Learning Module (`synapseml-deep-learning`)

The `deepLearning` module provides distributed deep learning capabilities through ONNX Runtime and PyTorch Lightning integration. It depends on both `core` and `opencv` modules.

### Dependencies

```scala
libraryDependencies ++= Seq(
  "com.microsoft.azure" % "onnx-protobuf_2.12" % "0.9.3",
  "com.microsoft.onnxruntime" % "onnxruntime_gpu" % "1.8.1"
)
```

Python dependencies include PyTorch 2.1.0, torchvision 0.16.0, Horovod, and pytorch_lightning 1.5.0.

Sources: [build.sbt:282-292](), [environment.yml:36-42]()

### Package Structure

```mermaid
graph TB
    deeplearning["com.microsoft.azure.synapse.ml.onnx"]
    
    deeplearning --> onnx["ONNXModel<br/>Distributed ONNX inference"]
    deeplearning --> imagefeaturizer["ImageFeaturizer<br/>Pre-trained model features"]
```

### ONNX Integration

The module provides `ONNXModel` for distributed inference of ONNX models:

**Key Features:**
- Hardware-accelerated inference (CPU/GPU)
- Distributed model execution across Spark cluster
- Support for models exported from PyTorch, TensorFlow, scikit-learn
- Automatic batching and model broadcasting

### PyTorch Lightning Integration

Through Python APIs, the module supports:
- `DeepVisionClassifier`: Image classification with transfer learning
- `DeepTextClassifier`: Text classification with transformer models
- Horovod-based distributed training
- Integration with Petastorm for efficient data loading

The training pipeline uses `pytorch_lightning.LightningModule` and Horovod's `hvd.DistributedOptimizer` for data-parallel training across Spark workers.

Sources: [build.sbt:282-292](), [environment.yml:36-42](), [deep-learning/src/test/python/synapsemltest/dl/conftest.py:1-110]()

## LightGBM Module (`synapseml-lightgbm`)

The `lightgbm` module provides distributed gradient boosting through Microsoft's LightGBM library. It depends on the `core` module.

### Dependencies

```scala
libraryDependencies += ("com.microsoft.ml.lightgbm" % "lightgbmlib" % "3.3.510")
```

Sources: [build.sbt:294-299]()

### Components

The LightGBM module provides three main estimators:

**LightGBM Estimators:**
- `LightGBMClassifier`: Binary and multiclass classification
- `LightGBMRegressor`: Regression tasks
- `LightGBMRanker`: Learning to rank

**Key Features:**
- Native integration with Spark MLlib pipelines
- Distributed training across Spark executors
- Support for categorical features
- Early stopping and cross-validation
- Model persistence and loading

### Pipeline Testing

The module is tested across 6 parallel test splits in the CI pipeline to ensure comprehensive coverage:

```
lightgbm.split1, lightgbm.split2, lightgbm.split3,
lightgbm.split4, lightgbm.split5, lightgbm.split6
```

Sources: [build.sbt:294-299](), [pipeline.yaml:697-714](), [README.md:52-54]()

## Vowpal Wabbit Module (`synapseml-vw`)

The `vw` module integrates Vowpal Wabbit for fast online learning and contextual bandit algorithms. It depends on the `core` module.

### Dependencies

```scala
libraryDependencies += ("com.github.vowpalwabbit" % "vw-jni" % "9.3.0")
```

Sources: [build.sbt:301-306]()

### Components

```mermaid
graph TB
    vw["com.microsoft.azure.synapse.ml.vw"]
    
    vw --> VowpalWabbitClassifier["VowpalWabbitClassifier<br/>Classification"]
    vw --> VowpalWabbitRegressor["VowpalWabbitRegressor<br/>Regression"]
    vw --> VowpalWabbitContextualBandit["VowpalWabbitContextualBandit<br/>Reinforcement learning"]
    vw --> VowpalWabbitFeaturizer["VowpalWabbitFeaturizer<br/>Feature hashing"]
```

**Key Features:**
- Online learning with single-pass training
- Support for large feature spaces through hashing
- Contextual bandit algorithms for recommendation systems
- Integration with Spark ML feature transformers
- Efficient handling of sparse data

Sources: [build.sbt:301-306](), [pipeline.yaml:726](), [README.md:52-54]()

## OpenCV Module (`synapseml-opencv`)

The `opencv` module provides computer vision transformations using OpenCV. It depends on the `core` module.

### Dependencies

```scala
libraryDependencies += ("org.openpnp" % "opencv" % "3.2.0-1")
```

Sources: [build.sbt:319-324]()

### Components

The OpenCV module provides image transformation pipeline stages:

**Image Transformations:**
- Resizing and scaling
- Color space conversions
- Image filtering and enhancement
- Geometric transformations
- Feature detection and extraction

**Integration:**
- Works with `ImageFileFormat` from core module
- Produces Spark DataFrames with image columns
- Compatible with deep learning module for preprocessing

The module enables building preprocessing pipelines for computer vision tasks within Spark ML pipelines.

Sources: [build.sbt:319-324](), [pipeline.yaml:461](), [pipeline.yaml:715-716]()

## Build and Publishing Infrastructure

The modular structure is supported by SBT build configuration and multi-language SDK generation.

### Publishing Artifacts

Each module publishes its own Maven artifact:

| Module | Maven Coordinates |
|--------|------------------|
| Core | `com.microsoft.azure:synapseml-core_2.12:VERSION` |
| Deep Learning | `com.microsoft.azure:synapseml-deep-learning_2.12:VERSION` |
| Cognitive | `com.microsoft.azure:synapseml-cognitive_2.12:VERSION` |
| LightGBM | `com.microsoft.azure:synapseml-lightgbm_2.12:VERSION` |
| VW | `com.microsoft.azure:synapseml-vw_2.12:VERSION` |
| OpenCV | `com.microsoft.azure:synapseml-opencv_2.12:VERSION` |

The `root` module aggregates all submodules and publishes a combined artifact:
- `com.microsoft.azure:synapseml_2.12:VERSION`

### Multi-Language SDK Generation

SynapseML automatically generates Python and R bindings from Scala implementations:

```mermaid
graph LR
    scala["Scala Source<br/>.scala files"]
    
    scala --> codegen["CodegenPlugin<br/>SBT task"]
    
    codegen --> python["Python SDK<br/>synapse.ml.*"]
    codegen --> r["R SDK<br/>sparkR wrappers"]
    
    python --> pypi["PyPI<br/>synapseml package"]
    r --> cran["R Package<br/>synapse.ml"]
```

The code generation process:
1. `CodegenPlugin` scans compiled Scala classes
2. Generates Python wrappers with proper type hints
3. Generates R wrappers for SparkR
4. Packages Python code into wheel (`.whl`) files
5. Publishes to PyPI and R package repositories

**SBT Tasks:**
- `packagePython`: Generate Python bindings for a module
- `packageSynapseML`: Combine all modules into single Python wheel
- `publishPypi`: Upload to PyPI
- `publishR`: Package and publish R bindings

Sources: [build.sbt:132-197](), [build.sbt:250-264]()

### Testing Strategy by Module

The CI pipeline tests each module independently:

**Python Tests** (7 parallel jobs):
- `core`, `deepLearning` (split into HuggingFace and non-HF), `lightgbm`, `opencv`, `vw`, `cognitive`

**R Tests** (6 parallel jobs):
- `core`, `deep-learning`, `lightgbm`, `opencv`, `vw`, `cognitive`

**Scala Unit Tests** (30+ parallel jobs):
- Each module's packages tested separately (e.g., `services.openai`, `services.text`, `lightgbm.split1`)

**E2E Tests** (Databricks + Synapse):
- All modules tested together in notebook-based integration tests

Sources: [pipeline.yaml:357-519](), [pipeline.yaml:614-772](), [pipeline.yaml:138-182]()

### Secrets Management for Testing

Build and test infrastructure uses Azure Key Vault for secret management:

```mermaid
graph TB
    Secrets["Secrets object<br/>project/Secrets.scala"]
    
    Secrets --> KeyVault["Azure Key Vault<br/>mmlspark-keys"]
    Secrets --> EnvVars["Environment Variables<br/>CI Pipeline"]
    Secrets --> LocalCache["Local Cache<br/>.cache/ directory"]
    
    KeyVault --> AzCLI["Azure CLI<br/>az keyvault secret show"]
    
    Secrets --> Publishing["Publishing Credentials<br/>Nexus, PyPI, PGP"]
    Secrets --> Testing["Test API Keys<br/>Azure services"]
```

The `Secrets` object manages:
- **Publishing credentials**: Nexus (Maven), PyPI tokens, PGP signing keys
- **Test secrets**: API keys for Azure Cognitive Services, OpenAI
- **Caching**: Secrets cached locally in `.cache/` directory to reduce Key Vault calls

**Secret Loading Priority:**
1. Environment variables (set by CI pipeline)
2. Local cache files (for developer machines)
3. Azure Key Vault (fetched via `az` CLI)

Sources: [project/Secrets.scala:1-194](), [pipeline.yaml:95](), [templates/kv.yml:1-7]()

## HTTP Communication Architecture

The HTTP communication layer is a critical component that enables SynapseML to interact with various AI services.

```mermaid
graph TD
    Client["HTTP Client System"] --> RESTClient["RESTClient"]
    Client --> AsyncHTTP["AsyncHTTP"]
    
    RESTClient --> HTTPEntity["HTTP Entity Generation"]
    RESTClient --> ResponseParsing["Response Parsing"]
    RESTClient --> RetryLogic["Retry Logic"]
    
    HTTPEntity --> PrepareEntity["prepareEntity Method"]
    ResponseParsing --> OutputParser["OutputParser Trait"]
    ResponseParsing --> JsonOutputParser["HasInternalJsonOutputParser"]
    
    AsyncHTTP --> InputFunc["inputFunc Method"]
    AsyncHTTP --> ProcessResponse["processResponse Method"]
    
    RetryLogic --> Backoff["Exponential Backoff"]
    RetryLogic --> ErrorHandling["Error Handling"]
```

The HTTP communication architecture consists of:

1. **RESTClient** - Handles synchronous HTTP requests with error handling and retries
2. **AsyncHTTP** - Manages asynchronous HTTP communication for streaming services
3. **Entity Generation** - Creates HTTP request bodies from Spark DataFrame rows
4. **Response Parsing** - Converts HTTP responses back into Spark-compatible formats

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:161-176](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeakerEmotionInference.scala:43-58]()

## Parameter Management System

SynapseML implements a sophisticated parameter management system that allows transformers to handle both scalar values and DataFrame columns as inputs.

```mermaid
graph TD
    ServiceParams["HasServiceParams Trait"] --> ServiceParam["ServiceParam Class"]
    ServiceParams --> SetScalarParam["setScalarParam Method"]
    ServiceParams --> SetVectorParam["setVectorParam Method"]
    ServiceParams --> GetValue["getValue Method"]
    
    ServiceParam --> LeftRight["Left/Right Type Union"]
    ServiceParam --> IsRequired["isRequired Flag"]
    
    SetScalarParam --> Left["Left Value (Scalar)"]
    SetVectorParam --> Right["Right Value (Column Name)"]
    
    GetValue --> ExtractScalar["Extract Scalar Value"]
    GetValue --> ExtractFromRow["Extract From DataFrame Row"]
```

This system allows:

1. API transformers to accept either fixed values or column references
2. Automatic extraction of values from DataFrame rows during transformation
3. Type-safe parameter handling with validation

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeakerEmotionInference.scala:104-135]()

## Component Relationships and Data Flow

This diagram illustrates how data flows through SynapseML components in a typical ML pipeline:

```mermaid
graph LR
    Data["Input DataFrame"] --> SparkPipeline["SparkML Pipeline"]
    SparkPipeline --> Transformers["SynapseML Transformers"]
    
    Transformers --> CoreComponents["Core Components"]
    Transformers --> AIServices["AI Service Integrations"]
    
    CoreComponents --> HTTP["HTTP Client"]
    CoreComponents --> ParamManagement["Parameter Management"]
    CoreComponents --> Logging["Logging"]
    
    HTTP --> ExternalServices["External AI Services"]
    ExternalServices --> ResponseData["Service Responses"]
    ResponseData --> ResponseParsing["Response Parsing"]
    ResponseParsing --> TransformedData["Transformed DataFrame"]
    
    AIServices --> OpenAI["OpenAI"]
    AIServices --> Cognitive["Cognitive Services"]
    AIServices --> LGBM["LightGBM"]
    AIServices --> VW["Vowpal Wabbit"]
    AIServices --> LangChain["LangChain"]
```

Sources: [README.md:5-59](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:34-291](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:139-487]()

## Common Architecture Patterns

SynapseML employs several common architectural patterns across its components:

1. **Transformer Pattern**: Components extend Spark's Transformer interface, implementing a `transform` method that converts input DataFrames to output DataFrames
   
2. **Service Parameter Pattern**: Service parameters can be specified as either fixed values or column references using the `ServiceParam` class

3. **Error Handling Pattern**: Most services include an error column option to capture and report service-specific errors

4. **Binding Generation Pattern**: Language bindings for Python and R are automatically generated from Scala code

5. **Pipeline Composition Pattern**: Components are designed to be composed in SparkML pipelines

Sources: [CONTRIBUTING.md:35-40](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:21-32](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:27-136]()

## Conclusion

SynapseML's modular architecture provides a flexible and extensible framework for large-scale machine learning on Apache Spark. The system components are designed to work together seamlessly, enabling integration with various AI services while maintaining a consistent API surface. This design allows users to leverage advanced AI capabilities within familiar Spark pipelines, simplifying the development of scalable machine learning applications.

---

# Page: Integration with Spark

# Integration with Spark

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala)
- [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala](core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala)
- [core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala](core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala)
- [start](start)
- [tools/docker/demo/Dockerfile](tools/docker/demo/Dockerfile)
- [tools/docker/demo/README.md](tools/docker/demo/README.md)
- [tools/docker/demo/init_notebook.py](tools/docker/demo/init_notebook.py)
- [tools/docker/minimal/Dockerfile](tools/docker/minimal/Dockerfile)
- [tools/tests/run_r_tests.R](tools/tests/run_r_tests.R)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala)

</details>



This document explains how SynapseML integrates with Apache Spark, describing the core architectural patterns and mechanisms that enable SynapseML to extend Spark's machine learning capabilities while maintaining compatibility with the Spark ML ecosystem.

## Overview

SynapseML (previously known as MMLSpark) extends Apache Spark's machine learning capabilities by providing additional algorithms, transformers, and integrations with external AI services. It's built directly on top of Apache Spark and shares the same API as SparkML/MLLib, allowing users to seamlessly embed SynapseML models into existing Apache Spark workflows.

The integration follows Spark's design principles and extends its core components like `Estimator`, `Transformer`, `Model`, and `Pipeline` to provide a consistent experience for users familiar with Spark ML.

```mermaid
graph TD
    subgraph "Apache Spark Ecosystem"
        SparkCore["Spark Core"] --> SparkSQL["Spark SQL"]
        SparkCore --> SparkStreaming["Spark Streaming"]
        SparkCore --> SparkMLlib["Spark MLlib"]
        SparkSQL --> DataFrame["DataFrame/Dataset API"]
        DataFrame --> SparkML["Spark ML"]
    end
    
    subgraph "SynapseML"
        SynML["SynapseML Library"] --> MLExt["ML Extensions"]
        SynML --> AIServices["AI Service Integrations"]
        SynML --> CoreUtils["Core Utilities"]
        
        MLExt --> LightGBM["LightGBM"]
        MLExt --> VW["Vowpal Wabbit"]
        MLExt --> IsolationForest["Isolation Forest"]
        MLExt --> ONNX["ONNX"]
        
        AIServices --> CogServices["Azure Cognitive Services"]
        AIServices --> OpenAI["OpenAI Integration"]
        AIServices --> HTTP["HTTP on Spark"]
    end
    
    SparkML -.-> MLExt
    DataFrame -.-> SynML
```

Sources: [README.md:5-9](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:27-34]()

## Core Integration Mechanisms

SynapseML integrates with Spark through several key mechanisms:

### 1. Extension of Spark ML Base Classes

SynapseML components extend Spark ML's base classes to maintain API compatibility. For example:

- `LightGBMClassifier` extends Spark's `ProbabilisticClassifier`
- `LightGBMRegressor` extends Spark's `BaseRegressor`
- `LightGBMRanker` extends Spark's `Ranker`

This inheritance ensures that SynapseML's models function as proper Spark ML pipeline components with consistent APIs.

```mermaid
classDiagram
    class Estimator {
        +fit(dataset): Model
        +copy(extra): Estimator
    }
    
    class Model {
        +transform(dataset): DataFrame
        +copy(extra): Model
    }
    
    class ProbabilisticClassifier {
        +predict(features): Double
        +predictProbability(features): Vector
        +predictRaw(features): Vector
    }
    
    class BaseRegressor {
        +predict(features): Double
    }
    
    class Ranker {
        +predict(features): Double
    }
    
    class LightGBMBase {
        +train(dataset): TrainedModel
        +getTrainParams(): BaseTrainParams
        +getModel(): TrainedModel
    }
    
    class LightGBMClassifier {
        +fit(dataset): LightGBMClassificationModel
        +getTrainParams(): BaseTrainParams
        +getModel(): LightGBMClassificationModel
    }
    
    class LightGBMClassificationModel {
        +transform(dataset): DataFrame
        +predict(features): Double
        +predictProbability(features): Vector
        +predictRaw(features): Vector
        +saveNativeModel(filename, overwrite): void
    }
    
    class LightGBMRegressor {
        +fit(dataset): LightGBMRegressionModel
        +getTrainParams(): BaseTrainParams
        +getModel(): LightGBMRegressionModel
    }
    
    class LightGBMRegressionModel {
        +transform(dataset): DataFrame
        +predict(features): Double
        +saveNativeModel(filename, overwrite): void
    }
    
    Estimator <|-- ProbabilisticClassifier
    Estimator <|-- BaseRegressor
    Estimator <|-- Ranker
    
    Model <|-- LightGBMClassificationModel
    Model <|-- LightGBMRegressionModel
    
    LightGBMBase <|-- LightGBMClassifier
    LightGBMBase <|-- LightGBMRegressor
    
    ProbabilisticClassifier <|-- LightGBMClassifier
    BaseRegressor <|-- LightGBMRegressor
    
    LightGBMClassifier ..> LightGBMClassificationModel: produces
    LightGBMRegressor ..> LightGBMRegressionModel: produces
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:27-30](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:39-41](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:26-28]()

### 2. DataFrame/Dataset API Integration

SynapseML components work directly with Spark's DataFrame/Dataset API:

- Models take DataFrames as input and produce DataFrames as output
- Transformers process data using DataFrame operations
- SynapseML leverages Spark SQL for data manipulation and preprocessing

This enables seamless integration with existing Spark data processing pipelines.

```mermaid
sequenceDiagram
    participant User
    participant SparkSession
    participant DataFrame
    participant LightGBMClassifier
    participant LightGBMModel
    
    User->>SparkSession: Create SparkSession
    User->>SparkSession: Read data
    SparkSession-->>User: DataFrame
    User->>LightGBMClassifier: create classifier
    User->>LightGBMClassifier: fit(DataFrame)
    LightGBMClassifier->>DataFrame: Prepare data
    LightGBMClassifier->>DataFrame: Distribute training
    LightGBMClassifier-->>User: LightGBMModel
    User->>LightGBMModel: transform(DataFrame)
    LightGBMModel->>DataFrame: Apply predictions
    LightGBMModel-->>User: Result DataFrame
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:109-144](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:118-163]()

### 3. Pipeline Integration

SynapseML components are designed to be used in Spark ML pipelines:

- Components implement the `PipelineStage` interface 
- Models can be saved and loaded as part of a pipeline
- Components support parameter passing through the Spark ML params system

```mermaid
graph TD
    subgraph "Spark ML Pipeline"
        DataLoader["DataFrame Loading"] --> FeatureTransformer["Feature Transformation"]
        FeatureTransformer --> SynapseMLModel["SynapseML Model"]
        SynapseMLModel --> Evaluation["Model Evaluation"]
    end
    
    subgraph "SynapseML Component"
        MLParams["ML Params"] --> LGBMParams["LightGBM Params"]
        LGBMParams --> LGBMModel["LightGBM Model"]
        LGBMModel --> Inference["Inference"]
    end
    
    SynapseMLModel -.-> LGBMModel
```

Sources: [CONTRIBUTING.md:38-40](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:488-503]()

## Distributed Computing Integration

SynapseML tightly integrates with Spark's distributed computing capabilities to enable scalable machine learning:

### 1. Distributed Training

SynapseML algorithms like LightGBM leverage Spark's distributed computing for training:

- Data is partitioned across worker nodes
- Workers communicate via a network layer for distributed algorithm execution
- Training happens in parallel across multiple Spark executors

```mermaid
graph TD
    subgraph "Driver"
        TrainMethod["train() method"] --> PrepareData["Prepare Dataframe"]
        PrepareData --> DetermineExecutors["Determine # of Tasks"]
        DetermineExecutors --> NetworkManager["Create Network Manager"]
        NetworkManager --> ExecuteMap["Execute mapPartitions"]
        ExecuteMap --> CreateResult["Create Model"]
    end
    
    subgraph "Executors"
        Task1["Task 1"] --> InitLib1["Initialize Native Lib"]
        Task1 --> PrepareRows1["Prepare Rows"]
        Task1 --> CreateDataset1["Create LightGBM Dataset"]
        Task1 --> Train1["Train LightGBM Booster"]
        
        Task2["Task 2"] --> InitLib2["Initialize Native Lib"]
        Task2 --> PrepareRows2["Prepare Rows"]
        Task2 --> CreateDataset2["Create LightGBM Dataset"]
        Task2 --> Train2["Train LightGBM Booster"]
        
        TaskN["Task N"] --> InitLibN["Initialize Native Lib"]
        TaskN --> PrepareRowsN["Prepare Rows"]
        TaskN --> CreateDatasetN["Create LightGBM Dataset"]
        TaskN --> TrainN["Train LightGBM Booster"]
    end
    
    ExecuteMap -.-> Task1
    ExecuteMap -.-> Task2
    ExecuteMap -.-> TaskN
    
    Train1 <-.-> Train2
    Train2 <-.-> TrainN
    Train1 <-.-> TrainN
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:581-606]()

### 2. Distributed Data Processing

SynapseML uses Spark's distributed data processing capabilities:

- Algorithms process data in parallel across partitions
- RDD and DataFrame operations are used for distributed preprocessing
- Data aggregation is handled using Spark's distributed computing primitives

### 3. Barrier Execution Mode

SynapseML supports Spark's barrier execution mode for synchronous distributed computing:

- Enables algorithms that require synchronized communication between workers
- Used for distributed training of models like LightGBM
- Configurable to optimize performance based on the cluster environment

```scala
if (getUseBarrierExecutionMode)
  dataframe.rdd.barrier().mapPartitions(mapPartitionsFunc).collect()
else
  dataframe.mapPartitions(mapPartitionsFunc)(encoder).collect()
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:620-623]()

## Parameter System Integration

SynapseML integrates with Spark ML's parameter system to provide a consistent interface:

### 1. Parameter Definition

SynapseML components use Spark ML's parameter definition system:

- Parameters are defined using Spark's `Param`, `BooleanParam`, `IntParam`, etc.
- Default values are set using `setDefault`
- Parameters are exposed through getter and setter methods

```mermaid
classDiagram
    class Params {
        +set(param, value): this.type
        +get(param): Any
        +getOrDefault(param): Any
    }
    
    class HasFeaturesCol {
        +featuresCol: Param[String]
        +getFeaturesCol(): String
        +setFeaturesCol(value): this.type
    }
    
    class HasLabelCol {
        +labelCol: Param[String]
        +getLabelCol(): String
        +setLabelCol(value): this.type
    }
    
    class LightGBMParams {
        +numIterations: IntParam
        +learningRate: DoubleParam
        +getNumIterations(): Int
        +setNumIterations(value): this.type
        +getLearningRate(): Double
        +setLearningRate(value): this.type
    }
    
    class LightGBMClassifier {
        +isUnbalance: BooleanParam
        +getIsUnbalance(): Boolean
        +setIsUnbalance(value): this.type
    }
    
    Params <|-- HasFeaturesCol
    Params <|-- HasLabelCol
    Params <|-- LightGBMParams
    LightGBMParams <|-- LightGBMClassifier
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:488-503](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:37-41]()

### 2. Parameter Passing

Parameters are passed to native libraries and underlying algorithms:

- SynapseML converts Spark ML parameters to format required by underlying implementations
- Parameter validation and transformation is handled during this process
- Sensible defaults are provided while allowing customization

## Serialization and Persistence Integration

SynapseML integrates with Spark's serialization and persistence mechanisms:

### 1. Model Persistence

SynapseML models can be saved and loaded like standard Spark ML models:

- Models implement `MLWritable` and `MLReadable` interfaces
- Models can be saved to disk or cloud storage
- Models can be reloaded for inference or continued training

### 2. Native Model Integration

SynapseML provides native model persistence in addition to Spark's serialization:

- Native models (e.g., LightGBM boosters) can be saved in their native format
- Native models can be loaded for use with non-Spark applications
- Native model representations can be extracted directly from SynapseML models

```scala
// Save a native LightGBM model
lightGBMModel.saveNativeModel("model.txt", overwrite = true)

// Load a native LightGBM model from file
val model = LightGBMClassificationModel.loadNativeModelFromFile("model.txt")

// Load a native LightGBM model from string
val modelString = getLightGBMModelString()
val model = LightGBMClassificationModel.loadNativeModelFromString(modelString)
```

Sources: [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMModelMethods.scala:95-109](), [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:196-211]()

## Python Integration

SynapseML provides Python bindings that integrate with PySpark:

### 1. PySpark API Integration

SynapseML's Python API follows the same patterns as PySpark ML:

- Python classes mirror their Scala counterparts
- Python models provide the same APIs as PySpark models
- Parameters can be set and accessed using the same method names

### 2. Python-Specific Extensions

Some Python-specific extensions are provided to improve usability:

- Native type conversions between Python and Scala
- Python-friendly model interfaces
- Additional utility methods for Python users

```python
# Get feature importances
importances = model.getFeatureImportances("split")

# Get SHAP values for a feature vector
shap_values = model.getFeatureShaps(feature_vector)

# Get and set model properties
model.setPredictDisableShapeCheck(True)
best_iteration = model.getBoosterBestIteration()
```

Sources: [lightgbm/src/main/python/synapse/ml/lightgbm/mixin.py:9-93]()

## Example Usage

Here's how SynapseML components are used with Spark:

```scala
// Create a SynapseML classifier integrated with Spark ML pipeline
val pipeline = new Pipeline().setStages(Array(
  new VectorAssembler()
    .setInputCols(featureCols)
    .setOutputCol("features"),
    
  new LightGBMClassifier()
    .setFeaturesCol("features")
    .setLabelCol("label")
    .setPredictionCol("prediction")
    .setNumIterations(100)
    .setLearningRate(0.1)
))

// Train the model using Spark DataFrame
val model = pipeline.fit(trainData)

// Use the model for predictions
val predictions = model.transform(testData)

// Evaluate the model using Spark ML evaluator
val evaluator = new BinaryClassificationEvaluator()
  .setLabelCol("label")
  .setPredictionCol("prediction")
  
val accuracy = evaluator.evaluate(predictions)
```

SynapseML models can be used in existing Spark ML workflows, combined with standard Spark ML components, and evaluated using standard Spark ML evaluators.

## Best Practices

When integrating SynapseML with Spark applications, consider these best practices:

1. **Data Preparation**: Use Spark's DataFrame transformations for data preparation before passing to SynapseML models
2. **Parameter Tuning**: Use Spark ML's cross-validation and parameter grid search with SynapseML models
3. **Pipeline Construction**: Combine SynapseML and Spark ML components in a single pipeline for streamlined workflows
4. **Distributed Computing Configuration**: Configure SynapseML's distributed computing parameters based on your cluster setup
5. **Model Persistence**: Save both the Spark ML pipeline and native models for maximum flexibility

## Conclusion

SynapseML's integration with Spark provides a seamless extension to Spark's machine learning capabilities. By following Spark's design patterns and extending its core components, SynapseML enables users to leverage advanced machine learning algorithms and AI services within their existing Spark workflows, combining the scalability of Spark with the capabilities of specialized ML libraries.

---

# Page: Platform Detection and Adaptation

# Platform Detection and Adaptation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py](cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py](cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/test_simple.py](cognitive/src/test/python/synapsemltest/services/test_simple.py)
- [core/src/main/python/synapse/ml/core/init_spark.py](core/src/main/python/synapse/ml/core/init_spark.py)
- [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py](core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py)
- [core/src/main/python/synapse/ml/core/logging/__init__.py](core/src/main/python/synapse/ml/core/logging/__init__.py)
- [core/src/main/python/synapse/ml/core/platform/Platform.py](core/src/main/python/synapse/ml/core/platform/Platform.py)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/python/synapsemltest/core/test_logging.py](core/src/test/python/synapsemltest/core/test_logging.py)
- [core/src/test/python/synapsemltest/core/test_template.py](core/src/test/python/synapsemltest/core/test_template.py)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [docs/Get Started/Set up Cognitive Services.ipynb](docs/Get Started/Set up Cognitive Services.ipynb)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



## Purpose and Scope

This document describes SynapseML's platform detection and adaptation system, which enables the library to automatically detect the execution environment (Azure Synapse, Microsoft Fabric, Databricks, etc.) and adapt its behavior accordingly. This system provides a unified API while handling platform-specific requirements for logging, authentication, secret management, and service endpoints.

For information about secret management APIs that use this system, see [Secret Management](#5.4). For logging implementations that adapt based on platform, see [Logging System](#5.1).

## Overview

Platform detection allows SynapseML components to automatically configure themselves based on where they are running. The system performs detection once at module initialization and caches the result. Components query the detected platform to make runtime decisions about authentication methods, logging destinations, service endpoints, and other platform-specific behaviors.

## Platform Detection Mechanism

### Detection Logic Flow

```mermaid
graph TD
    Start["Platform Detection Start"]
    CheckTridentContext{"File exists?<br/>/home/trusted-service-user/<br/>.trident-context"}
    CheckAzureService{"Environment Variable<br/>AZURE_SERVICE ==<br/>Microsoft.ProjectArcadia?"}
    CheckSparkConfig{"Spark Config<br/>spark.cluster.type<br/>== 'synapse'?"}
    CheckDBFS{"Directory exists?<br/>/dbfs"}
    CheckBinder{"Environment Variable<br/>BINDER_LAUNCH_HOST<br/>exists?"}
    CheckFabricURL{"Environment Variable<br/>MSNOTEBOOKUTILS_SPARK_<br/>TRIDENT_PBIHOST contains<br/>fabric.microsoft.com?"}
    
    ReturnSynapseInternal["Return:<br/>PLATFORM_SYNAPSE_INTERNAL"]
    ReturnSynapse["Return:<br/>PLATFORM_SYNAPSE"]
    ReturnDatabricks["Return:<br/>PLATFORM_DATABRICKS"]
    ReturnBinder["Return:<br/>PLATFORM_BINDER"]
    ReturnFabricPython["Return:<br/>PLATFORM_FABRIC_PYTHON"]
    ReturnUnknown["Return:<br/>PLATFORM_UNKNOWN"]
    
    Start --> CheckTridentContext
    CheckTridentContext -->|Yes| ReturnSynapseInternal
    CheckTridentContext -->|No| CheckAzureService
    CheckAzureService -->|Yes| CheckSparkConfig
    CheckAzureService -->|No| CheckDBFS
    CheckSparkConfig -->|Yes| ReturnSynapse
    CheckSparkConfig -->|No| ReturnSynapseInternal
    CheckDBFS -->|Yes| ReturnDatabricks
    CheckDBFS -->|No| CheckBinder
    CheckBinder -->|Yes| ReturnBinder
    CheckBinder -->|No| CheckFabricURL
    CheckFabricURL -->|Yes| ReturnFabricPython
    CheckFabricURL -->|No| ReturnUnknown
```

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:17-34](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:17-30]()

### Python Implementation

The Python platform detection is implemented in the `Platform` module with the following constants and functions:

| Constant | Value | Description |
|----------|-------|-------------|
| `PLATFORM_SYNAPSE_INTERNAL` | `"synapse_internal"` | Microsoft Fabric environment |
| `PLATFORM_SYNAPSE` | `"synapse"` | Azure Synapse Analytics |
| `PLATFORM_FABRIC_PYTHON` | `"fabric_python_env"` | Fabric Python environment |
| `PLATFORM_DATABRICKS` | `"databricks"` | Databricks platform |
| `PLATFORM_BINDER` | `"binder"` | Binder notebook environment |
| `PLATFORM_UNKNOWN` | `"unknown"` | Unknown/unsupported platform |

The `current_platform()` function performs the detection [core/src/main/python/synapse/ml/core/platform/Platform.py:17-34]():

1. Checks if `AZURE_SERVICE` environment variable equals `"Microsoft.ProjectArcadia"` and verifies Spark configuration
2. Checks if `/dbfs` directory exists (Databricks marker)
3. Checks if `BINDER_LAUNCH_HOST` environment variable exists
4. Checks if `MSNOTEBOOKUTILS_SPARK_TRIDENT_PBIHOST` contains `"fabric.microsoft.com"`

Helper functions provide boolean checks for specific platforms:
- `running_on_synapse_internal()`
- `running_on_synapse()`
- `running_on_databricks()`
- `running_on_fabric_python()`
- `running_on_binder()`

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:1-104]()

### Scala Implementation

The Scala implementation in `PlatformDetails` object provides equivalent functionality:

| Constant | Value | Description |
|----------|-------|-------------|
| `PlatformSynapseInternal` | `"synapse_internal"` | Microsoft Fabric environment |
| `PlatformSynapse` | `"synapse"` | Azure Synapse Analytics |
| `PlatformDatabricks` | `"databricks"` | Databricks platform |
| `PlatformBinder` | `"binder"` | Binder notebook environment |
| `PlatformUnknown` | `"unknown"` | Unknown/unsupported platform |

The `currentPlatform()` method performs detection with caching via `lazy val CurrentPlatform` [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:17-30]():

1. Checks if `/home/trusted-service-user/.trident-context` file exists (Fabric marker)
2. Checks `AZURE_SERVICE` environment variable and calls `defineSynapsePlatform()`
3. Checks if `/dbfs` directory exists (Databricks marker)
4. Checks if `BINDER_LAUNCH_HOST` environment variable exists

The `defineSynapsePlatform()` method distinguishes between Synapse and Synapse Internal by examining the `spark.cluster.type` configuration [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:32-40]().

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:1-48]()

## Supported Platforms

### Platform Characteristics

```mermaid
graph LR
    subgraph "Microsoft Fabric"
        FabricInternal["Synapse Internal<br/>(Fabric Runtime)"]
        FabricPython["Fabric Python Env"]
    end
    
    subgraph "Azure Synapse"
        Synapse["Synapse Analytics<br/>(Dedicated Pools)"]
    end
    
    subgraph "Databricks"
        DB["Databricks<br/>(CPU/GPU Clusters)"]
    end
    
    subgraph "Other"
        Binder["Binder<br/>(Notebook Environment)"]
        Unknown["Unknown Platform<br/>(Standalone/Local)"]
    end
    
    FabricInternal -.->|"Has .trident-context file<br/>Has Spark config"| TridentContext["/home/trusted-service-user/<br/>.trident-context"]
    FabricPython -.->|"Has env variable"| FabricEnv["MSNOTEBOOKUTILS_SPARK_<br/>TRIDENT_PBIHOST"]
    Synapse -.->|"Has env variable<br/>spark.cluster.type=synapse"| AzureService["AZURE_SERVICE=<br/>Microsoft.ProjectArcadia"]
    DB -.->|"Has directory"| DBFSDir["/dbfs"]
    Binder -.->|"Has env variable"| BinderEnv["BINDER_LAUNCH_HOST"]
```

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:6-14](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:9-15]()

### Detection Priority

Platform detection follows a specific priority order to handle overlapping markers:

1. **Synapse Internal / Fabric** (highest priority) - Detected by `.trident-context` file
2. **Synapse** - Detected by `AZURE_SERVICE` environment variable and Spark configuration
3. **Databricks** - Detected by `/dbfs` directory
4. **Binder** - Detected by `BINDER_LAUNCH_HOST` environment variable
5. **Fabric Python Environment** - Detected by `MSNOTEBOOKUTILS_SPARK_TRIDENT_PBIHOST` containing `fabric.microsoft.com`
6. **Unknown** (lowest priority) - Default when no markers match

This priority ensures that the most specific platform is detected when multiple markers are present.

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:17-34](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:17-30]()

## Platform-Specific Adaptations

### Logging Adaptation

The logging system selects different logger implementations based on the detected platform:

```mermaid
graph TB
    LoggerInit["SynapseMLLogger<br/>Initialization"]
    GetEnvLogger["_get_environment_logger()"]
    
    CheckSynapseInternal{"running_on_synapse_internal()<br/>or<br/>running_on_fabric_python()?"}
    CheckSynapse{"running_on_synapse()?"}
    
    MDSLogger["MDS Logger<br/>(get_mds_logger)<br/>from synapse.ml.pymds"]
    StandardLogger1["Python Standard Logger<br/>logging.getLogger(__name__)"]
    StandardLogger2["Python Standard Logger<br/>logging.getLogger(__name__)"]
    
    FabricContext["Load Fabric Context<br/>from Hadoop Configuration"]
    CertifiedEvents["Report to<br/>Certified Events<br/>(Fabric Telemetry)"]
    
    LoggerInit --> GetEnvLogger
    GetEnvLogger --> CheckSynapseInternal
    CheckSynapseInternal -->|Yes| MDSLogger
    CheckSynapseInternal -->|No| CheckSynapse
    CheckSynapse -->|Yes| StandardLogger1
    CheckSynapse -->|No| StandardLogger2
    
    MDSLogger --> FabricContext
    FabricContext --> CertifiedEvents
```

**Python Logging Implementation** [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:85-101]():

- **Synapse Internal / Fabric Python**: Uses MDS logger from `synapse.ml.pymds.synapse_logger` with custom formatter
- **Synapse**: Uses standard Python logger configured with specified log level
- **Other Platforms**: Uses standard Python logger configured with specified log level

**Scala Logging Implementation** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140]():

- **Fabric**: Asynchronously logs to Certified Events for telemetry via `CertifiedEventClient.logToCertifiedEvents()`
- **All Platforms**: Logs JSON-formatted messages with scrubbed content (SAS tokens removed)

The logging system also collects platform-specific metadata from Hadoop configuration when running on Fabric:

| Configuration Key | Logged Field | Description |
|-------------------|--------------|-------------|
| `trident.artifact.id` | `artifactId` | Fabric artifact identifier |
| `trident.workspace.id` | `workspaceId` | Fabric workspace identifier |
| `trident.capacity.id` | `capacityId` | Fabric capacity identifier |
| `trident.artifact.workspace.id` | `artifactWorkspaceId` | Artifact workspace identifier |
| `trident.lakehouse.id` | `lakehouseId` | Lakehouse identifier |
| `trident.activity.id` | `livyId` | Activity/Livy session identifier |
| `trident.artifact.type` | `artifactType` | Type of artifact |
| `trident.tenant.id` | `tenantId` | Tenant identifier |

**Sources:** [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:85-122](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:50-92](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:1-36]()

### Secret Management Adaptation

The `find_secret()` function adapts to each platform's secret management system:

```mermaid
graph TD
    FindSecret["find_secret(secret_name, keyvault)"]
    
    CheckSynapse{"running_on_synapse()?"}
    CheckSynapseInternal{"running_on_synapse_internal()?"}
    CheckDatabricks{"running_on_databricks()?"}
    
    SynapseGetSecret["notebookutils.mssparkutils<br/>.credentials.getSecret<br/>(keyvault, secret_name)"]
    SynapseInternalGetSecret["notebookutils.mssparkutils<br/>.credentials.getSecret<br/>(keyVaultURL, secret_name)<br/>keyVaultURL = https://{keyvault}<br/>.vault.azure.net/"]
    DatabricksGetSecret["dbutils.secrets.get<br/>(scope=keyvault,<br/>key=secret_name)"]
    ErrorNotSupported["Raise RuntimeError<br/>Platform not supported"]
    
    FindSecret --> CheckSynapse
    CheckSynapse -->|Yes| SynapseGetSecret
    CheckSynapse -->|No| CheckSynapseInternal
    CheckSynapseInternal -->|Yes| SynapseInternalGetSecret
    CheckSynapseInternal -->|No| CheckDatabricks
    CheckDatabricks -->|Yes| DatabricksGetSecret
    CheckDatabricks -->|No| ErrorNotSupported
```

**Platform-Specific Secret Retrieval** [core/src/main/python/synapse/ml/core/platform/Platform.py:57-92]():

- **Synapse**: Uses `notebookutils.mssparkutils.credentials.getSecret(keyvault, secret_name)` with linked service
- **Synapse Internal / Fabric**: Uses `notebookutils.mssparkutils.credentials.getSecret(keyVaultURL, secret_name)` with full URL
- **Databricks**: Uses `dbutils.secrets.get(scope=keyvault, key=secret_name)` with secret scopes
- **Other Platforms**: Raises `RuntimeError` with detailed setup instructions

The error message provides platform-specific guidance for secret configuration, including links to documentation.

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:57-92]()

### Token Management Adaptation

Token retrieval for authentication is platform-specific, particularly for Fabric:

```mermaid
graph TB
    subgraph "Fabric Token Management"
        FabricClient["FabricClient"]
        GetMLWorkloadHeader["getMLWorkloadAADAuthHeader"]
        GetCognitiveHeader["getCognitiveMWCTokenAuthHeader"]
        
        TokenLibrary["TokenLibrary<br/>(Scala Reflection)"]
        GetAccessToken["getAccessToken('ml')"]
        GetMwcToken["getSparkMwcToken<br/>(workspaceId, artifactId,<br/>2, 'SparkCore')"]
        
        TridentTokenLib["com.microsoft.azure.trident<br/>.tokenlibrary.TokenLibrary<br/>(Fabric Runtime)"]
    end
    
    FabricClient --> GetMLWorkloadHeader
    FabricClient --> GetCognitiveHeader
    GetMLWorkloadHeader --> TokenLibrary
    GetCognitiveHeader --> TokenLibrary
    TokenLibrary --> GetAccessToken
    TokenLibrary --> GetMwcToken
    GetAccessToken --> TridentTokenLib
    GetMwcToken --> TridentTokenLib
```

**Token Library Implementation** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:9-51]():

The `TokenLibrary` object uses Scala reflection to dynamically invoke methods from the Fabric runtime's token library:

- **`getMLWorkloadAADAuthHeader`**: Returns `"Bearer " + getAccessToken("ml")` for ML workload authentication
- **`getCognitiveMwcTokenAuthHeader`**: Returns `"MwcToken " + getSparkMwcToken(...)` for Cognitive Services authentication

These tokens are used by `FabricClient` to authenticate requests to Fabric ML workload endpoints and Cognitive Services.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:1-52](), [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:194-198]()

### Service Endpoint Adaptation

Service endpoints are automatically configured based on platform, particularly for Fabric:

```mermaid
graph TB
    subgraph "Fabric Endpoint Configuration"
        ReadContextFile["Read .trident-context and<br/>spark-defaults.conf"]
        ExtractContext["Extract Context:<br/>- capacityId<br/>- workspaceId<br/>- artifactId<br/>- pbiEnv"]
        
        DetermineMLHost{"Workspace PE<br/>Enabled?"}
        
        PublicHost["Public ML Workload Host<br/>From lakehouse.tokenservice.endpoint"]
        PEHost["Private Endpoint Host<br/>https://{workspaceId}.z{prefix}<br/>.{envMark}c.fabric.microsoft.com"]
        
        BuildEndpoints["Build Workload Endpoints:<br/>- MLWorkloadEndpointML<br/>- MLWorkloadEndpointLLMPlugin<br/>- MLWorkloadEndpointAutomatic<br/>- MLWorkloadEndpointRegistry<br/>- MLWorkloadEndpointAdmin<br/>- MLWorkloadEndpointCognitive<br/>- MLWorkloadEndpointOpenAI"]
    end
    
    ReadContextFile --> ExtractContext
    ExtractContext --> DetermineMLHost
    DetermineMLHost -->|No| PublicHost
    DetermineMLHost -->|Yes| PEHost
    PublicHost --> BuildEndpoints
    PEHost --> BuildEndpoints
```

**Fabric Client Endpoint Configuration** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:23-38]():

The `FabricClient` object reads Fabric context from multiple sources:
- `/home/trusted-service-user/.trident-context` - Key-value pairs
- `/opt/spark/conf/spark-defaults.conf` - Spark configuration
- `/opt/health-agent/conf/cluster-info.json` - Cluster metadata

Key lazy values:
- `CapacityID`: Fabric capacity identifier
- `WorkspaceID`: Workspace identifier
- `ArtifactID`: Artifact identifier
- `PbiEnv`: Environment (public, daily, dxt, msit, edog)
- `MLWorkloadHost`: ML workload host URL (public or PE-enabled)
- `WorkspacePeEnabled`: Whether workspace uses private endpoints

Endpoint construction [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:185-188]():
```
{MLWorkloadHost}/webapi/capacities/{CapacityID}/workloads/ML/{EndpointType}/Automatic/workspaceid/{WorkspaceID}/
```

**LangChain Transformer Endpoint Defaults** [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:133-141]():

When running on Synapse Internal (Fabric), the `LangchainTransformer` automatically sets the OpenAI URL to Fabric's ML workload endpoint:
```python
if running_on_synapse_internal():
    from synapse.ml.fabric.service_discovery import get_fabric_env_config
    self._setDefault(
        url=get_fabric_env_config().fabric_env_config.ml_workload_endpoint
        + "cognitive/openai"
    )
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:1-200](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:133-141]()

### Telemetry Adaptation

Certified Events telemetry is only enabled on Fabric:

```mermaid
graph LR
    LogBase["logBase(info, featureName)"]
    CheckFeatureName{"featureName<br/>is defined?"}
    CheckFabric{"runningOnFabric()?"}
    
    AsyncLog["Asynchronous Future:<br/>logToCertifiedEvents<br/>(libraryName, featureName)"]
    
    BuildPayload["Build JSON Payload:<br/>- timestamp<br/>- feature_name<br/>- activity_name<br/>- attributes"]
    
    PostToEndpoint["POST to FabricClient<br/>.MLWorkloadEndpointAdmin<br/>/telemetry"]
    
    LogJSON["Log JSON to<br/>standard logging"]
    
    LogBase --> CheckFeatureName
    CheckFeatureName -->|Yes| CheckFabric
    CheckFeatureName -->|No| LogJSON
    CheckFabric -->|Yes| AsyncLog
    CheckFabric -->|No| LogJSON
    AsyncLog --> BuildPayload
    BuildPayload --> PostToEndpoint
    PostToEndpoint --> LogJSON
```

**Certified Events Implementation** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:13-34]():

The `CertifiedEventClient` checks `runningOnFabric` before sending telemetry. The payload includes:
- `timestamp`: Current epoch second
- `feature_name`: Library name (e.g., "SynapseML")
- `activity_name`: Feature being used
- `attributes`: Empty object for future extensibility

The telemetry is posted to `{MLWorkloadEndpointAdmin}/telemetry` endpoint with appropriate authentication headers.

**Python Telemetry** [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:146-153]():

Python logging also supports telemetry reporting:
```python
if feature_name is not None and running_on_synapse_internal():
    from synapse.ml.fabric.telemetry_utils import report_usage_telemetry
    
    report_usage_telemetry(
        feature_name=self.library_name,
        activity_name=feature_name,
        attributes={},
    )
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:1-36](), [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:145-154](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140]()

## Platform Context Information

### Fabric Context Extraction

When running on Fabric (Synapse Internal), the system extracts rich context information:

```mermaid
graph TD
    subgraph "Context Files"
        TridentContext[".trident-context<br/>Key=Value pairs"]
        SparkDefaults["spark-defaults.conf<br/>Spark configurations"]
        ClusterInfo["cluster-info.json<br/>Cluster metadata"]
    end
    
    subgraph "Extracted Fields"
        ArtifactId["trident.artifact.id"]
        WorkspaceId["trident.workspace.id /<br/>trident.artifact.workspace.id"]
        CapacityId["trident.capacity.id"]
        ActivityId["trident.activity.id"]
        LakehouseId["trident.lakehouse.id"]
        ArtifactType["trident.artifact.type"]
        TenantId["trident.tenant.id"]
        PbiEnv["spark.trident.pbienv"]
        PbiHost["spark.trident.pbiHost"]
        WorkspacePE["workspace-pe-enabled"]
    end
    
    subgraph "Usage"
        LoggingMetadata["Logging Metadata<br/>(Hadoop Conf Entries)"]
        EndpointConstruction["Endpoint URL Construction"]
        TokenRetrieval["Token Retrieval Parameters"]
    end
    
    TridentContext --> ArtifactId
    TridentContext --> WorkspaceId
    TridentContext --> CapacityId
    TridentContext --> ActivityId
    TridentContext --> LakehouseId
    TridentContext --> ArtifactType
    TridentContext --> TenantId
    SparkDefaults --> PbiEnv
    SparkDefaults --> PbiHost
    ClusterInfo --> WorkspacePE
    
    ArtifactId --> LoggingMetadata
    WorkspaceId --> LoggingMetadata
    CapacityId --> LoggingMetadata
    ActivityId --> LoggingMetadata
    LakehouseId --> LoggingMetadata
    ArtifactType --> LoggingMetadata
    TenantId --> LoggingMetadata
    
    WorkspaceId --> EndpointConstruction
    CapacityId --> EndpointConstruction
    PbiEnv --> EndpointConstruction
    WorkspacePE --> EndpointConstruction
    
    WorkspaceId --> TokenRetrieval
    ArtifactId --> TokenRetrieval
```

**Context File Parsing** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:90-138]():

- **`.trident-context`**: Parsed as simple key=value pairs, ignoring lines with multiple `=` signs
- **`spark-defaults.conf`**: Parsed as space-separated key-value pairs, ignoring comment lines starting with `#`
- **`cluster-info.json`**: Parsed as JSON to extract `cluster_metadata` object

**Python Context Access** [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:104-121]():

The `get_hadoop_conf_entries()` method retrieves context from Fabric's internal utilities:
```python
if running_on_synapse_internal():
    from synapse.ml.internal_utils.session_utils import get_fabric_context
    
    return {
        "artifactId": get_fabric_context().get("trident.artifact.id"),
        "workspaceId": get_fabric_context().get("trident.workspace.id"),
        # ... other fields
    }
```

This context is automatically included in all log entries for correlation and debugging.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:51-143](), [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:103-122]()

## Usage Patterns

### Component Integration Pattern

SynapseML components typically follow this pattern for platform adaptation:

```mermaid
graph TB
    ComponentInit["Component Initialization"]
    CheckPlatform["Check Platform via<br/>running_on_synapse_internal()<br/>or current_platform()"]
    
    SetDefaults["Set Platform-Specific<br/>Defaults"]
    ConfigureLogger["Configure Logger<br/>(MDS or Standard)"]
    SetEndpoints["Set Service Endpoints<br/>(Fabric or Azure)"]
    ConfigureAuth["Configure Authentication<br/>(Token or Key)"]
    
    ComponentRun["Component Execution"]
    LoadSecrets["Load Secrets via<br/>find_secret()"]
    LogActivity["Log Activity with<br/>Platform Context"]
    CallServices["Call Services with<br/>Platform-Specific Config"]
    
    ComponentInit --> CheckPlatform
    CheckPlatform --> SetDefaults
    SetDefaults --> ConfigureLogger
    ConfigureLogger --> SetEndpoints
    SetEndpoints --> ConfigureAuth
    ConfigureAuth --> ComponentRun
    ComponentRun --> LoadSecrets
    LoadSecrets --> LogActivity
    LogActivity --> CallServices
```

**Example: VowpalWabbit Logging** [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:109-110]():

```scala
class VowpalWabbitContextualBandit(override val uid: String)
  extends Predictor[Row, VowpalWabbitContextualBandit, VowpalWabbitContextualBanditModel]
    with SynapseMLLogging {
  logClass(FeatureNames.VowpalWabbit)
  // Component automatically logs to appropriate platform logger
}
```

The `SynapseMLLogging` trait automatically:
1. Detects the platform via `PlatformDetails.CurrentPlatform`
2. Includes platform context in log entries
3. Sends telemetry to Certified Events on Fabric
4. Scrubs sensitive information (SAS tokens) from logs

**Example: LangChain with Fabric Defaults** [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:133-151]():

```python
class LangchainTransformer(...):
    def __init__(self, ...):
        self.running_on_synapse_internal = running_on_synapse_internal()
        if running_on_synapse_internal():
            from synapse.ml.fabric.service_discovery import get_fabric_env_config
            
            self._setDefault(
                url=get_fabric_env_config().fabric_env_config.ml_workload_endpoint
                + "cognitive/openai"
            )
```

This pattern allows components to work seamlessly across platforms without user configuration when running on supported platforms.

**Sources:** [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:105-110](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:113-152]()

### Display Helper Function

The `materializing_display()` function adapts display behavior based on platform [core/src/main/python/synapse/ml/core/platform/Platform.py:95-103]():

```python
def materializing_display(data):
    if running_on_synapse() or running_on_synapse_internal():
        from notebookutils.visualization import display
        
        if isinstance(data, DataFrame):
            data.collect()  # Materialize before display
        display(data)
    else:
        print(data)
```

This ensures optimal display behavior on Synapse/Fabric (using native visualization) vs. other platforms (using print).

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:95-103]()

## Summary

The platform detection and adaptation system provides:

1. **Automatic Platform Detection**: Single detection at module load with caching for performance
2. **Transparent Adaptation**: Components automatically configure themselves without user intervention
3. **Consistent API**: Users write the same code across all platforms
4. **Platform-Specific Optimization**: Leverages platform-native capabilities (logging, secrets, endpoints)
5. **Graceful Degradation**: Falls back to standard behavior on unknown platforms

The system is designed for extensibility - new platforms can be added by:
1. Adding detection logic to `current_platform()` / `currentPlatform()`
2. Adding platform-specific constants
3. Updating adaptation logic in logging, secrets, and token management
4. Testing the new platform configuration

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala]()

---

# Page: Development Infrastructure

# Development Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



This page provides an overview of the development infrastructure for the SynapseML project, covering the build system, CI/CD pipeline, secrets management, and package publishing mechanisms. For information about testing infrastructure specifically, see [Testing Infrastructure](#4).

## Overview

The SynapseML development infrastructure consists of a set of tools, configurations, and automated processes that enable efficient development, testing, and deployment of the library. This infrastructure is designed to support multiple programming languages (Scala, Python, R) and multiple deployment targets (Maven, PyPI, Docker).

```mermaid
flowchart TD
    subgraph "Development Infrastructure"
        Build["Build System (SBT)"]
        CI["CI/CD Pipeline (Azure DevOps)"]
        Secrets["Secrets Management"]
        Publishing["Package Publishing"]
        SDKGen["SDK Generation"]
        WebDeploy["Website Auto-Deployment"]
        
        Build --> CI
        Secrets --> CI
        Secrets --> Publishing
        Build --> Publishing
        Build --> SDKGen
        CI --> WebDeploy
        CI --> Publishing
    end
```

Sources: [pipeline.yaml:1-744](), [build.sbt:1-368]()

## Project Structure

SynapseML is organized as a multi-module SBT project with several subprojects, each focusing on a specific area of functionality.

```mermaid
flowchart TD
    subgraph "SynapseML Project Structure"
        Root["root (synapseml)"]
        Core["core"]
        DeepLearning["deep-learning"]
        Cognitive["cognitive"]
        LightGBM["lightgbm"]
        VW["vw (Vowpal Wabbit)"]
        OpenCV["opencv"]
        
        Root --> Core
        Root --> DeepLearning
        Root --> Cognitive
        Root --> LightGBM
        Root --> VW
        Root --> OpenCV
        DeepLearning --> Core
        DeepLearning --> OpenCV
        Cognitive --> Core
        LightGBM --> Core
        VW --> Core
        OpenCV --> Core
    end
```

Sources: [build.sbt:269-344]()

## Build System

SynapseML uses SBT (Scala Build Tool) as its primary build system. The build configuration includes dependency management, multi-project setup, cross-compilation, and custom tasks for packaging and publishing.

### Key SBT Tasks

| Task                | Description                                                     |
|---------------------|-----------------------------------------------------------------|
| `setup`             | Set up library for IntelliJ development                         |
| `getDatasets`       | Download datasets used for testing                             |
| `packagePython`     | Package Python code                                            |
| `packageSynapseML`  | Package all projects into SynapseML                            |
| `publishPypi`       | Publish Python wheel to PyPI                                   |
| `publishDocs`       | Publish documentation for Scala and Python                     |
| `publishBadges`     | Publish badges to SynapseML blob storage                       |
| `uploadNotebooks`   | Upload notebooks to blob storage                               |
| `convertNotebooks`  | Convert notebooks to markdown for website display              |
| `testWebsiteDocs`   | Test code blocks in website documentation                      |

Sources: [build.sbt:74-367]()

## Conda Environment

The project uses Conda to manage development and testing environments, ensuring consistent dependencies across development machines and CI/CD pipelines.

```mermaid
flowchart TD
    subgraph "Conda Environment Management"
        ENV["environment.yml"]
        CACHE["Conda Cache"]
        ACTIVATE["Activate Environment"]
        
        ENV --> |"conda env create"| CACHE
        CACHE --> |"source activate synapseml"| ACTIVATE
        ACTIVATE --> |"Run Tasks"| TASKS["SBT Tasks"]
    end
```

Sources: [templates/conda.yml:1-30](), [pipeline.yaml:65-89]()

## CI/CD Pipeline

SynapseML uses Azure DevOps pipelines for continuous integration and deployment. The pipeline is defined in `pipeline.yaml` and consists of several jobs that build, test, and publish the library.

### Pipeline Jobs Structure

```mermaid
flowchart TD
    subgraph "Azure DevOps Pipeline"
        TRIGGER["Triggers (master, PR, schedule)"]
        
        subgraph "Build Jobs"
            STYLE["Style"]
            CONDA["BuildAndCacheCondaEnv"]
        end
        
        subgraph "Test Jobs"
            UNIT["UnitTests"]
            PYTHON["PythonTests"]
            R["RTests"]
            E2E["E2E Tests"]
            WEBSITE["WebsiteSamplesTests"]
        end
        
        subgraph "Publish Jobs"
            PUBLISH["Publish"]
            WEBSITEDEPLOY["WebsiteAutoDeployment"]
        end
        
        subgraph "Release Jobs"
            RELEASE["Release"]
        end
        
        TRIGGER --> STYLE
        TRIGGER --> CONDA
        STYLE --> UNIT
        STYLE --> PYTHON
        STYLE --> R
        STYLE --> E2E
        STYLE --> WEBSITE
        CONDA --> UNIT
        CONDA --> PYTHON
        CONDA --> R
        CONDA --> E2E
        CONDA --> WEBSITE
        UNIT --> PUBLISH
        PYTHON --> PUBLISH
        R --> PUBLISH
        E2E --> PUBLISH
        WEBSITE --> PUBLISH
        PUBLISH --> WEBSITEDEPLOY
        PUBLISH --> RELEASE
    end
```

Sources: [pipeline.yaml:4-57](), [pipeline.yaml:65-589]()

### Build and Style Check

The pipeline begins with style checking for both Scala and Python code, ensuring code quality and consistency.

```mermaid
flowchart TD
    subgraph "Style Checks"
        SCALASTYLE["Scala Style Check (scalastyle)"]
        BLACKSTYLE["Python Style Check (black)"]
    end
```

Sources: [pipeline.yaml:66-84]()

### Test Jobs

The pipeline includes several test jobs that run different types of tests for different components of the library:

1. **Unit Tests**: Tests for individual Scala components
2. **Python Tests**: Tests for Python API
3. **R Tests**: Tests for R API
4. **E2E Tests**: End-to-end tests on Databricks and Synapse
5. **Website Tests**: Tests for code samples in documentation

Sources: [pipeline.yaml:356-542](), [pipeline.yaml:138-180]()

## Secrets Management

SynapseML uses Azure Key Vault to securely store and retrieve secrets needed for building, testing, and publishing.

```mermaid
flowchart TD
    subgraph "Secrets Management"
        KV["Azure Key Vault (mmlspark-keys)"]
        
        subgraph "Environment Variables"
            NEXUS["NEXUS-UN/NEXUS-PW"]
            PGP["PGP-PRIVATE/PGP-PUBLIC/PGP-PW"]
            PYPI["PYPI-API-TOKEN"]
            ADO["ADO-FEED-TOKEN"]
        end
        
        subgraph "Secret Storage"
            CACHE["Local Cache (.cache)"]
        end
        
        KV --> NEXUS
        KV --> PGP
        KV --> PYPI
        KV --> ADO
        
        NEXUS --> CACHE
        PGP --> CACHE
        PYPI --> CACHE
        ADO --> CACHE
    end
```

Sources: [project/Secrets.scala:1-194](), [templates/kv.yml:1-7]()

The `Secrets` object provides methods to retrieve secrets either from environment variables (set by the CI/CD pipeline) or from Azure Key Vault. It also caches secrets locally to avoid repeated API calls.

## Package Publishing

SynapseML is published to several repositories:

1. **Maven Central**: For Scala/Java artifacts
2. **PyPI**: For Python package
3. **Azure DevOps Feed**: For internal distribution

### Maven Publishing Flow

```mermaid
flowchart TD
    subgraph "Maven Publishing"
        SBT["SBT publishLocalSigned"]
        PGP["PGP Signing"]
        ESRP["ESRP Signing"]
        MAVENCENTRAL["Maven Central"]
        
        SBT --> PGP
        PGP --> |"prepare_jar.py"| ESRP
        ESRP --> MAVENCENTRAL
    end
```

Sources: [pipeline.yaml:323-352](), [tools/esrp/prepare_jar.py:1-80](), [sonatype.sbt:1-46]()

### Python Publishing Flow

```mermaid
flowchart TD
    subgraph "Python Publishing"
        PACKAGE["packageSynapseML"]
        WHEEL["Generate Wheel"]
        PYPI["PyPI"]
        
        PACKAGE --> WHEEL
        WHEEL --> |"twine upload"| PYPI
    end
```

Sources: [build.sbt:134-187](), [build.sbt:189-198](), [pipeline.yaml:309-322]()

## SDK Generation

SynapseML automatically generates Python and R SDKs from the Scala codebase. This functionality is implemented through a custom SBT plugin (`CodegenPlugin`), which is referenced in the CI/CD pipeline but not included in the provided files.

The SDK generation involves:
1. Generating Python and R code from Scala classes
2. Packaging the generated code into respective formats
3. Running tests on the generated APIs

Sources: [build.sbt:122-131](), [pipeline.yaml:462-464]()

## Website Auto-Deployment

SynapseML uses automated website deployment as part of its CI/CD pipeline. The website is built using Docusaurus and deployed to GitHub Pages.

```mermaid
flowchart TD
    subgraph "Website Deployment"
        CONVERT["Convert Notebooks to Markdown"]
        YARN["Yarn Install and Build"]
        DEPLOY["Yarn Deploy to GitHub Pages"]
        
        CONVERT --> YARN
        YARN --> DEPLOY
    end
```

Sources: [pipeline.yaml:546-589](), [build.sbt:355-359]()

The pipeline:
1. Converts Jupyter notebooks to Markdown files
2. Builds the Docusaurus website using Yarn
3. Deploys the built website to GitHub Pages

## Docker Environments

While currently commented out in the pipeline, SynapseML includes support for building and publishing Docker images:

1. **Demo Image**: Full-featured image with all dependencies
2. **Minimal Image**: Lightweight image with core dependencies
3. **Release Image**: Official release image

Sources: [pipeline.yaml:183-257]()

The Docker images are built and published to Microsoft Container Registry (MCR) when triggered by specific conditions, such as tags on the master branch.

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



This document details the continuous integration and deployment pipeline for SynapseML. It covers the Azure DevOps pipeline configuration, build jobs, test execution, and publication processes that enable reliable code delivery. For information on the build system configuration, see [Build System](#3.2), and for details on SDK generation, refer to [SDK Generation](#3.3).

## Pipeline Overview

The SynapseML CI/CD pipeline is implemented using Azure DevOps Pipelines with additional validation through GitHub Actions. The pipeline supports multiple trigger types, provides automated testing across multiple languages, and handles the publication of artifacts to various destinations.

### Pipeline Diagram

```mermaid
flowchart TD
    subgraph "Triggers"
        PR["Pull Request"]
        MasterPush["Push to Master/Release Branch"]
        Schedule["Daily Schedule"]
    end
    
    subgraph "Pipeline Stages"
        Build["Build Stage"]
        Test["Test Stage"]
        Publish["Publish Stage"]
        Release["Release Stage"]
    end
    
    subgraph "Tests"
        Style["Style Checks"]
        PythonTests["Python Tests"]
        RTests["R Tests"]
        UnitTests["Unit Tests"]
        E2ETests["E2E Tests"]
        WebsiteTests["Website Tests"]
    end
    
    subgraph "Publication"
        PyPI["PyPI"]
        Maven["Maven Central"]
        Blob["Azure Blob"]
        DocSite["Documentation Site"]
        GitHubRelease["GitHub Release"]
    end
    
    PR --> Build
    MasterPush --> Build
    Schedule --> Build
    
    Build --> Test
    Test --> Publish
    Publish --> Release
    
    Test --> Style
    Test --> PythonTests
    Test --> RTests
    Test --> UnitTests
    Test --> E2ETests
    Test --> WebsiteTests
    
    Release --> PyPI
    Release --> Maven
    Release --> Blob
    Release --> DocSite
    Release --> GitHubRelease
```

Sources: [pipeline.yaml:1-35](), [pipeline.yaml:36-64]()

## Pipeline Configuration

The pipeline is defined in `pipeline.yaml` and uses a variety of Azure DevOps features including parameterization, conditions, and parallel job execution.

### Trigger Configuration

The pipeline is triggered by:
1. Pull requests to master, spark3.3, and spark3.5 branches
2. Direct pushes to these branches
3. Daily scheduled runs at midnight

```mermaid
flowchart LR
    subgraph "Pipeline Triggers"
        PR["PR Trigger" <br> "- master branch" <br> "- spark3.3 branch" <br> "- spark3.5 branch"]
        Push["Push Trigger" <br> "- master branch" <br> "- spark3.3 branch" <br> "- spark3.5 branch"]
        Schedule["Schedule Trigger" <br> "- Daily at midnight"]
    end
    
    subgraph "Exclusions"
        DocFiles["Documentation Files" <br> "- README.md" <br> "- CONTRIBUTORS.md" <br> "- SECURITY.md" <br> "- docs/Reference/*.md"]
    end
    
    PR --> Pipeline["Azure DevOps Pipeline"]
    Push --> Pipeline
    Schedule --> Pipeline
    
    DocFiles -. "excluded from" .-> PR
    DocFiles -. "excluded from" .-> Push
```

Sources: [pipeline.yaml:1-35]()

### Pipeline Parameters and Variables

The pipeline supports customizable behavior through parameters and variables:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `runSynapseExtensionE2ETests` | Run Synapse Extension E2E Tests | `true` |
| `SYNAPSE_ENVIRONMENT` | Synapse Extension E2E Test Environment | `weekly` |

| Variable | Description | Value |
|----------|-------------|-------|
| `runTests` | Controls whether tests are executed | `True` |
| `CONDA_CACHE_DIR` | Directory for Conda environment cache | `/usr/share/miniconda/envs` |
| `UBUNTU_VERSION` | Ubuntu version for build agents | `ubuntu-22.04` |
| `isMaster` | Indicates if build is from master branch | Dynamically set |

Sources: [pipeline.yaml:44-63]()

## Pipeline Jobs

The pipeline is organized into multiple job types that handle different aspects of the build, test, and release process. Jobs are structured to run in parallel when possible to improve pipeline efficiency.

### Style Check Job

The Style job runs code style checks for both Scala and Python code:

```mermaid
flowchart TD
    Style["Style Job"]
    ScalaStyleCheck["Scala Style Check<br>sbt scalastyle test:scalastyle"]
    PythonStyleCheck["Python Style Check<br>black --check"]
    
    Style --> ScalaStyleCheck
    Style --> PythonStyleCheck
```

Sources: [pipeline.yaml:65-84]()

### Test Jobs

Multiple test jobs are configured to validate different components of the codebase:

1. **UnitTests**: Tests core functionality and services
2. **PythonTests**: Tests Python SDK functionality
3. **RTests**: Tests R SDK functionality
4. **E2E**: End-to-end tests on Databricks and Synapse
5. **WebsiteSamplesTests**: Tests website example code

Test jobs use the following common pattern:
1. Set up environment (Conda, Key Vault access)
2. Run tests with retry logic
3. Publish test results
4. Generate and upload code coverage reports

```mermaid
flowchart TD
    subgraph "Test Jobs Structure"
        TestJob["Test Job"]
        Setup["Environment Setup<br>- Conda<br>- Key Vault"]
        RunTests["Run Tests<br>with Retries"]
        PublishResults["Publish Test Results"]
        Coverage["Generate Coverage"]
        
        TestJob --> Setup
        Setup --> RunTests
        RunTests --> PublishResults
        PublishResults --> Coverage
    end
    
    subgraph "Unit Tests Matrix"
        Core["core"]
        Services["services.*"]
        Explainers["explainers.*"]
        LightGBM["lightgbm.*"]
        IO["io.*"]
    end
```

Sources: [pipeline.yaml:356-432](), [pipeline.yaml:425-496](), [pipeline.yaml:592-743]()

### Publication Job

The Publish job handles artifact creation and uploading:

```mermaid
flowchart TD
    Publish["Publish Job"]
    
    Auth["Maven Authentication"]
    PackagePython["Package Python<br>sbt packagePython"]
    UploadNotebooks["Upload Notebooks<br>sbt uploadNotebooks"]
    PublishBlob["Publish to Blob<br>sbt publishBlob"]
    PublishDocs["Publish Docs<br>sbt publishDocs"]
    PublishR["Publish R<br>sbt publishR"]
    PublishPython["Publish Python<br>sbt publishPython"]
    PublishLocal["Publish Local<br>sbt publishLocalSigned"]
    PublishBadges["Publish Badges<br>sbt publishBadges"]
    
    Publish --> Auth
    Auth --> PackagePython
    PackagePython --> UploadNotebooks
    UploadNotebooks --> PublishBlob
    PublishBlob --> PublishDocs
    PublishDocs --> PublishR
    PublishR --> PublishPython
    PublishPython --> PublishLocal
    PublishLocal --> PublishBadges
```

Sources: [pipeline.yaml:87-135]()

### Release Job

The Release job is triggered when a Git tag with format "v*" is present on the master branch:

```mermaid
flowchart TD
    Release["Release Job"]
    GetTag["Get Git Tag"]
    GenerateChangelog["Generate Changelog"]
    CreateGitHubRelease["Create GitHub Release"]
    PublishPyPI["Publish to PyPI<br>sbt publishPypi"]
    PublishMaven["Publish to Maven<br>ESRP Release"]
    
    Release --> GetTag
    GetTag --> |"if tag starts with 'v'"| GenerateChangelog
    GenerateChangelog --> CreateGitHubRelease
    CreateGitHubRelease --> PublishPyPI
    PublishPyPI --> PublishMaven
```

Sources: [pipeline.yaml:258-352]()

### Website Auto-Deployment

A specialized job handles website documentation auto-deployment:

```mermaid
flowchart TD
    WebsiteDeploy["Website Auto-Deployment Job"]
    ConvertNotebooks["Convert Notebooks to Markdown<br>sbt convertNotebooks"]
    YarnInstall["Yarn Install"]
    YarnBuild["Yarn Build"]
    GitConfig["Git Configuration"]
    YarnDeploy["Yarn Deploy"]
    
    WebsiteDeploy --> ConvertNotebooks
    ConvertNotebooks --> YarnInstall
    YarnInstall --> YarnBuild
    YarnBuild --> |"if master branch"| GitConfig
    GitConfig --> YarnDeploy
```

Sources: [pipeline.yaml:546-589]()

## Secrets Management

The pipeline uses Azure Key Vault to securely store and retrieve secrets needed for building, testing, and publishing.

```mermaid
flowchart TD
    subgraph "Azure Pipeline"
        AzureTask["Azure Key Vault Task"]
    end
    
    subgraph "KeyVault"
        KeyVault["Azure Key Vault<br>mmlspark-keys"]
        Secrets["Secrets<br>- nexus-un<br>- nexus-pw<br>- pgp-private<br>- pgp-public<br>- pgp-pw<br>- pypi-api-token"]
    end
    
    subgraph "Secrets Usage"
        BuildSystem["Build System<br>project/Secrets.scala"]
        PublishPyPI["Publish to PyPI"]
        PublishMaven["Publish to Maven"]
        SignArtifacts["Sign Artifacts"]
    end
    
    AzureTask --> KeyVault
    KeyVault --> Secrets
    Secrets --> BuildSystem
    BuildSystem --> PublishPyPI
    BuildSystem --> PublishMaven
    BuildSystem --> SignArtifacts
```

The `Secrets` scala object provides an interface for accessing and managing these secrets. It handles:
1. Fetching secrets from Azure Key Vault
2. Caching secrets locally for reuse
3. Providing helper methods for secret management

Sources: [project/Secrets.scala:1-194](), [templates/kv.yml:1-7](), [pipeline.yaml:302-323]()

## Build Environment Configuration

The pipeline uses Conda environments for consistent build and test environments:

```mermaid
flowchart TD
    CondaTemplate["conda.yml Template"]
    AddPathStep["Add Conda to PATH"]
    FixPermissions["Fix Directory Permissions"]
    CacheTask["Cache Conda Environment"]
    CreateEnv["Create Conda Environment<br>from environment.yml"]
    CleanupSpace["Free up Space"]
    
    CondaTemplate --> AddPathStep
    AddPathStep --> FixPermissions
    FixPermissions --> CacheTask
    CacheTask --> |"if cache miss"| CreateEnv
    CreateEnv --> CleanupSpace
```

The Conda environment caching mechanism improves pipeline performance by reusing previously created environments.

Sources: [templates/conda.yml:1-30](), [pipeline.yaml:498-504]()

## Additional Quality Gates

Beyond the main Azure DevOps pipeline, SynapseML uses GitHub Actions for additional validation:

### Security Scanning

```mermaid
flowchart TD
    subgraph "GitHub Actions"
        CodeQL["CodeQL Analysis<br>.github/workflows/codeql.yml"]
        Scorecards["Supply Chain Scorecards<br>.github/workflows/scorecards.yml"]
        DeadLinks["Check Dead Links<br>.github/workflows/check-dead-links.yml"]
    end
    
    subgraph "Security Checks"
        JavaScript["JavaScript Analysis"]
        Python["Python Analysis"]
        BranchProtection["Branch Protection"]
        DependencyCheck["Dependency Check"]
        WebsiteLinks["Website Link Validation"]
    end
    
    CodeQL --> JavaScript
    CodeQL --> Python
    Scorecards --> BranchProtection
    Scorecards --> DependencyCheck
    DeadLinks --> WebsiteLinks
```

These GitHub Actions workflows run on:
- Pushes to the master branch
- Pull requests to the master branch
- Scheduled runs (weekly for Scorecards)

Sources: [.github/workflows/codeql.yml:1-79](), [.github/workflows/scorecards.yml:1-73](), [.github/workflows/check-dead-links.yml:1-27]()

## ACR Cleanup

A separate pipeline exists for Azure Container Registry maintenance:

```mermaid
flowchart TD
    ACRCleanup["ACR Cleanup Pipeline<br>.pipelines/clean-acr.yml"]
    WeeklySchedule["Weekly Schedule<br>Sundays at 1:00 AM"]
    AzureCLI["Azure CLI Task"]
    CleanupScript["Python Cleanup Script<br>tools/acr/clean-acr.py"]
    
    ACRCleanup --> WeeklySchedule
    WeeklySchedule --> AzureCLI
    AzureCLI --> CleanupScript
    CleanupScript --> |"Exports and removes"| ContainerImages["Container Images"]
```

This pipeline runs weekly to clean up the Azure Container Registry by exporting images to blob storage and then removing them from the registry.

Sources: [.pipelines/clean-acr.yml:1-30](), [tools/acr/clean-acr.py:1-87]()

## Summary

The SynapseML CI/CD pipeline provides comprehensive validation, testing, and publication capabilities. It ensures code quality through style checks, multiple test suites, and security scanning. The pipeline also automates the publication process to multiple channels including PyPI, Maven Central, and documentation sites.

The pipeline is designed to be flexible and maintainable, with modular components and reusable templates. This structure allows for easy updates and extensions as the project evolves.

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



## Purpose and Scope

This document describes the SBT-based build system that compiles, packages, and publishes SynapseML artifacts. The build system manages a multi-module Scala project structure, handles cross-platform dependencies, defines custom build tasks for artifact generation, and integrates with the publishing pipeline.

For information about the CI/CD orchestration that invokes these build tasks, see [CI/CD Pipeline](#3.1). For details on how Python, R, and .NET bindings are generated from Scala code, see [Multi-Language SDK Generation](#3.3). For information about how the resulting artifacts are distributed, see [Installation and Distribution](#8.1).

## Project Structure

SynapseML uses a modular SBT project structure with six core modules that can be compiled and tested independently. The root project aggregates all modules and provides cross-cutting tasks.

```mermaid
graph TB
    root["Root Project<br/>(synapseml)"]
    core["Core Module<br/>(synapseml-core)"]
    dl["Deep Learning<br/>(synapseml-deep-learning)"]
    cognitive["Cognitive<br/>(synapseml-cognitive)"]
    lgbm["LightGBM<br/>(synapseml-lightgbm)"]
    vw["Vowpal Wabbit<br/>(synapseml-vw)"]
    opencv["OpenCV<br/>(synapseml-opencv)"]
    
    root -->|aggregates| core
    root -->|aggregates| dl
    root -->|aggregates| cognitive
    root -->|aggregates| lgbm
    root -->|aggregates| vw
    root -->|aggregates| opencv
    
    dl -->|depends on| core
    dl -->|depends on| opencv
    cognitive -->|depends on| core
    lgbm -->|depends on| core
    vw -->|depends on| core
    opencv -->|depends on| core
    
    root -.->|defines| tasks["Custom Tasks:<br/>packageSynapseML<br/>publishPypi<br/>publishDocs<br/>uploadNotebooks"]
```

**Project Definitions:**

The project structure is defined in [build.sbt:267-344]():

- **core** ([build.sbt:267-280]()): Base module with `synapseml-core` artifact name, includes BuildInfo plugin for metadata
- **deepLearning** ([build.sbt:282-292]()): Depends on core and opencv, includes ONNX and GPU support
- **lightgbm** ([build.sbt:294-299]()): Microsoft LightGBM gradient boosting integration
- **vw** ([build.sbt:301-306]()): Vowpal Wabbit online learning integration
- **cognitive** ([build.sbt:308-317]()): Azure Cognitive Services wrappers, includes speech SDK
- **opencv** ([build.sbt:319-324]()): Image processing with OpenCV bindings
- **root** ([build.sbt:326-344]()): Aggregates all modules, provides unified tasks, disables CodegenPlugin

Sources: [build.sbt:267-344]()

## Build Configuration

### Version and Scala Configuration

The build system targets Spark 3.5.0 and Scala 2.12.17:

| Configuration | Value |
|---------------|-------|
| Spark Version | `3.5.0` ([build.sbt:10]()) |
| Scala Version | `2.12.17` ([build.sbt:13]()) |
| Organization | `com.microsoft.azure` ([build.sbt:12]()) |
| Scala Major | `2.12` ([build.sbt:15]()) |

### Dependency Management

Dependencies are organized into core Spark dependencies and extra utilities. Exclusions prevent conflicts with Spark's bundled libraries.

**Exclusion Rules** ([build.sbt:17-21]()):
- `spark-tags` - Test dependency conflicts
- `scalatest` - Test framework conflicts  
- `breeze` - Scala numerical library conflicts

**Core Dependencies** ([build.sbt:23-30]()):
```scala
spark-core, spark-mllib, spark-avro (compile scope)
spark-tags (test scope only)
hadoop-bare-naked-local-fs, scalatest (test scope)
```

**Extra Dependencies** ([build.sbt:31-42]()):
- HTTP clients: `httpclient5`, `httpmime`
- Serialization: `spray-json`
- Utilities: `commons-lang`, `jsch`
- ML: `isolation-forest_3.5.0` (with extensive exclusions to prevent version conflicts)

All extra dependencies apply the exclusion rules via `.map(d => d excludeAll (excludes: _*))` ([build.sbt:42]()).

Sources: [build.sbt:10-43]()

### Common Settings

All projects share common settings defined in [build.sbt:250-264]():

```mermaid
graph LR
    settings["Common Settings"]
    
    settings --> test["Test Configuration"]
    settings --> assembly["Assembly Strategy"]
    settings --> pom["POM Processing"]
    
    test --> a1["logBuffered = false"]
    test --> a2["parallelExecution = false"]
    test --> a3["publishArtifact = true"]
    
    assembly --> b1["test := {}"]
    assembly --> b2["MergeStrategy.discard<br/>for META-INF"]
    assembly --> b3["includeScala = false"]
    
    pom --> c1["pomPostProcess"]
    pom --> c2["Remove scoped deps"]
    pom --> c3["Remove omitted deps"]
```

**Key Settings:**
- **Test Configuration**: Serial execution, buffered logging disabled, test artifacts published
- **Assembly Strategy**: Discards META-INF to avoid conflicts, excludes Scala runtime
- **POM Customization**: Custom function `pomPostFunc` ([build.sbt:50-68]()) removes dependencies with scope tags and omitted dependencies from published POM files

Sources: [build.sbt:250-264](), [build.sbt:45-68]()

## Custom Build Tasks

The build system defines numerous custom SBT tasks for specialized operations. These tasks orchestrate artifact generation, documentation, and publishing.

```mermaid
graph TB
    subgraph "Data Management"
        getDatasetsTask["getDatasetsTask"]
        datasetDir["datasetDir setting"]
    end
    
    subgraph "Artifact Generation"
        packageSynapseML["packageSynapseML"]
        genBuildInfo["genBuildInfo"]
    end
    
    subgraph "Documentation"
        generatePythonDoc["generatePythonDoc"]
        publishDocs["publishDocs"]
        convertNotebooks["convertNotebooks"]
        uploadNotebooks["uploadNotebooks"]
    end
    
    subgraph "Publishing"
        publishPypi["publishPypi"]
        publishBadges["publishBadges"]
    end
    
    subgraph "Testing"
        setupTask["setupTask"]
        testWebsiteDocs["testWebsiteDocs"]
    end
    
    getDatasetsTask --> setupTask
    packageSynapseML --> publishPypi
    generatePythonDoc --> publishDocs
    
    style getDatasetsTask fill:#f9f9f9
    style packageSynapseML fill:#f9f9f9
    style publishPypi fill:#f9f9f9
    style publishDocs fill:#f9f9f9
```

### Dataset Management

**getDatasetsTask** ([build.sbt:72-89]()):
- Downloads test dataset (`datasets-2023-04-03.tgz`) from Azure Blob Storage
- URL: `https://mmlspark.blob.core.windows.net/installers/$datasetName`
- Extracts to `target/datasets/` directory
- Idempotent: only downloads if not already present
- **datasetDir** setting ([build.sbt:75-79]()): Computed relative to artifact path, used by BuildInfo

### Build Information Generation

**genBuildInfo** ([build.sbt:91-105]()):
- Generates `target/Build.md` with documentation links and artifact information
- Includes versioned URLs to Scala and Python documentation
- Combines output from `blobArtifactInfo` task
- Uploaded as build summary via `##vso[task.uploadsummary]` ([pipeline.yaml:115]())

### Python Packaging

**packageSynapseML** ([build.sbt:132-185]()):
- Orchestrates complete Python package creation
- Task sequence ([build.sbt:176-179]()):
  1. `packagePython` for all modules (in compile scope)
  2. `mergePyCode` to consolidate Python files
- Generates `setup.py` dynamically ([build.sbt:134-174]()) with:
  - Package name: `synapseml`
  - Version: Pythonized from SBT version
  - Namespace packages: `synapse.ml.*`
  - Classifiers for PyPI
- Builds wheel using `packagePythonWheelCmd` ([build.sbt:184]())
- Output: `${name}-${pythonizedVersion}-py2.py3-none-any.whl` in `target/generated/package/python/`

**publishPypi** ([build.sbt:187-197]()):
- Depends on `packageSynapseML`
- Uses `twine upload` with `--skip-existing` flag
- Authenticates with `__token__` username and `PYPI-API-TOKEN` secret
- Only executes when `SYNAPSEML_ENABLE_PUBLISH=true` (via Secrets validation)

### Documentation Generation

**generatePythonDoc** ([build.sbt:120-129]()):
- Installs pip packages for all modules
- Merges Python code to unified directory (`target/generated/src/python/synapse/`)
- Creates `__init__.py` files for package structure
- Runs `sphinx-apidoc` to generate RST files
- Builds HTML docs with `sphinx-build` to `target/generated/doc/pyspark/`

**publishDocs** ([build.sbt:199-220]()):
- Sequential execution: `generatePythonDoc` → `unidoc` (Scala docs)
- Copies Scala docs from `target/unidoc` to `target/generated/doc/scala/`
- Creates index.html with links to both pyspark/ and scala/
- Uploads to Azure Blob Storage with `uploadToBlob` function
- Blob container: `docs`, path: `${version}/`

**convertNotebooks** ([build.sbt:355-359]()):
- Installs docgen tool from `tools/docgen` as editable package
- Runs `tools/docgen/docgen/__main__.py` to convert Jupyter notebooks to Markdown
- Used by website build process (see [Documentation System](#7))

**uploadNotebooks** ([build.sbt:243-248]()):
- Uploads `docs/` folder to Azure Blob Storage
- Blob container: `docs`, path: `${version}/`
- Notebooks become available for consumption by documentation system

### Publishing Utilities

**publishBadges** ([build.sbt:222-241]()):
- Generates SVG badges using shields.io API
- Uploads to Blob Storage with cache-control headers for immediate updates
- Example: `master_version3.svg` with current version
- Only runs on master branch: `condition: and(succeeded(), eq(variables.isMaster, true))` ([pipeline.yaml:133]())

### Setup and Testing

**setupTask** ([build.sbt:346-353]()):
- Convenience task for IntelliJ/IDE setup
- Compiles all projects in both Compile and Test configurations
- Downloads test datasets via `getDatasetsTask`
- Invoked during local development setup

**testWebsiteDocs** ([build.sbt:361-367]()):
- Tests code blocks in `website/docs/documentation/` Markdown files
- Runs `website/doctest.py` with current version as argument
- Used by CI/CD pipeline to validate documentation examples

Sources: [build.sbt:72-367]()

## Task Execution Flow

The following diagram shows how tasks are invoked during the CI/CD pipeline:

```mermaid
graph TB
    subgraph "Style Job"
        style_sbt["sbt scalastyle"]
        style_black["black --check"]
    end
    
    subgraph "Publish Job"
        pub_package["sbt packagePython<br/>uploadNotebooks"]
        pub_publish["sbt publishBlob<br/>publishDocs<br/>publishR<br/>publishPython"]
        pub_buildinfo["sbt genBuildInfo"]
        pub_signed["sbt publishLocalSigned"]
        pub_esrp["python prepare_jar.py"]
        pub_badges["sbt publishBadges"]
    end
    
    subgraph "E2E Job"
        e2e_test["sbt testOnly<br/>(TEST-CLASS)"]
    end
    
    subgraph "Unit Tests"
        unit_setup["sbt setup"]
        unit_test["sbt coverage testOnly"]
        unit_coverage["sbt coverageReport"]
    end
    
    subgraph "Python Tests"
        py_deps["sbt getDatasets<br/>installPipPackage<br/>publishM2"]
        py_test["sbt testPython"]
        py_coverage["sbt coverageReport"]
    end
    
    subgraph "R Tests"
        r_setup["sbt setup codegen<br/>publishM2"]
        r_test["sbt testR"]
        r_coverage["sbt coverageReport"]
    end
    
    subgraph "Website Tests"
        web_setup["sbt setup"]
        web_test["sbt testWebsiteDocs"]
        web_coverage["sbt coverageReport"]
    end
    
    subgraph "Website Deploy"
        web_convert["sbt convertNotebooks"]
        web_build["yarn build"]
        web_deploy["yarn deploy"]
    end
    
    subgraph "Release Job"
        rel_pypi["sbt publishPypi"]
        rel_maven["sbt publishLocalSigned<br/>prepare_jar.py"]
        rel_esrp["ESRP Release"]
    end
    
    pub_package --> pub_publish
    pub_publish --> pub_buildinfo
    pub_buildinfo --> pub_signed
    pub_signed --> pub_esrp
    
    py_deps --> py_test
    py_test --> py_coverage
    
    r_setup --> r_test
    r_test --> r_coverage
    
    unit_setup --> unit_test
    unit_test --> unit_coverage
    
    web_setup --> web_test
    web_test --> web_coverage
    
    web_convert --> web_build
    web_build --> web_deploy
    
    style pub_package fill:#f9f9f9
    style e2e_test fill:#f9f9f9
    style unit_test fill:#f9f9f9
    style py_test fill:#f9f9f9
    style r_test fill:#f9f9f9
```

Sources: [pipeline.yaml:87-773](), [build.sbt:72-367]()

## Secret Management for Publishing

The build system integrates with Azure Key Vault to securely manage publishing credentials. Secrets are cached locally to reduce Key Vault queries and improve build performance.

```mermaid
graph TB
    env["Environment Variables"]
    kv["Azure Key Vault<br/>(mmlspark-keys)"]
    cache["Local Cache<br/>(.cache/)"]
    
    subgraph "Secret Loading Priority"
        p1["1. Check Environment"]
        p2["2. Check Local Cache"]
        p3["3. Fetch from KeyVault"]
    end
    
    subgraph "Publishing Secrets"
        nexus["nexus-un / nexus-pw<br/>(Maven Central)"]
        pgp["pgp-private / pgp-public / pgp-pw<br/>(JAR Signing)"]
        pypi["pypi-api-token<br/>(PyPI)"]
        ado["ado-feed-token<br/>(Azure DevOps)"]
    end
    
    env --> p1
    cache --> p2
    kv --> p3
    
    p1 --> nexus
    p1 --> pgp
    p1 --> pypi
    p1 --> ado
    
    p2 --> nexus
    p2 --> pgp
    p2 --> pypi
    p2 --> ado
    
    p3 --> nexus
    p3 --> pgp
    p3 --> pypi
    p3 --> ado
    
    p3 -.->|cache for reuse| cache
```

### Secret Configuration

The `Secrets` object ([project/Secrets.scala:13-194]()) provides a centralized secret management system:

**Environment Variables** ([project/Secrets.scala:179-193]()):
- `NEXUS-UN` / `NEXUS-PW`: Maven Central / Sonatype credentials
- `PGP-PRIVATE` / `PGP-PUBLIC` / `PGP-PW`: PGP signing keys and passphrase
- `PYPI-API-TOKEN`: PyPI upload token
- `ADO-FEED-TOKEN`: Azure DevOps feed authentication
- `SYNAPSEML_ENABLE_PUBLISH`: Master switch to enable publishing operations ([project/Secrets.scala:17-19]())

**Key Vault Integration** ([project/Secrets.scala:50-65]()):
- Vault name: `mmlspark-keys` ([project/Secrets.scala:14]())
- Subscription: `e342c2c0-f844-4b18-9208-52c8c234c30e` ([project/Secrets.scala:15]())
- Uses `az keyvault secret show` command via `exec` helper ([project/Secrets.scala:21-35]())
- Parses JSON response to extract secret value
- Falls back to empty string if Key Vault unavailable

**Caching Strategy** ([project/Secrets.scala:67-143]()):
- Cache directory: `.cache/` in project root ([project/Secrets.scala:67-74]())
- Priority order ([project/Secrets.scala:130-138]()):
  1. Environment variable (set by CI/CD pipeline from Key Vault task)
  2. Local cached file (avoids Key Vault queries during development)
  3. Fetch from Key Vault (and cache result)
- PGP secrets are Base64-encoded and decoded before use ([project/Secrets.scala:140-142]())
- PGP files created as `.asc` files in cache ([project/Secrets.scala:96-108]())
- `refreshCachedSecrets()` ([project/Secrets.scala:147-150]()): Force re-fetch all secrets (used when Key Vault values change)

**Publishing Control** ([project/Secrets.scala:152-166]()):
- `getSecret`: Returns empty string if `SYNAPSEML_ENABLE_PUBLISH != true`
- `getPgpSecretFile`: Returns empty File if publishing disabled
- Prevents accidental secret fetches during normal builds

### PGP Signing Configuration

JAR signing uses PGP keys for Maven Central requirements ([sonatype.sbt:34-36]()):

```scala
pgpPassphrase := Some(Secrets.pgpPassword.toCharArray)
pgpSecretRing := Secrets.pgpPrivateFile  // .cache/pgp-private.asc
pgpPublicRing := Secrets.pgpPublicFile   // .cache/pgp-public.asc
```

The `publishLocalSigned` task signs all JARs before publishing. For releases, an additional ESRP (Enterprise Software Release Process) signing step occurs ([pipeline.yaml:339-353]()) via the `tools/esrp/prepare_jar.py` script.

Sources: [project/Secrets.scala:13-194](), [sonatype.sbt:29-46](), [pipeline.yaml:304-353]()

## Publishing Configuration

SynapseML publishes artifacts to two destinations based on configuration:

```mermaid
graph LR
    build["SBT Build"]
    
    subgraph "Conditional Publishing"
        check["Check Secrets.publishToFeed"]
        ado["Azure DevOps Feed<br/>(SynapseML_PublicPackages)"]
        sonatype["Sonatype OSSRH<br/>(Maven Central)"]
    end
    
    subgraph "Additional Channels"
        pypi["PyPI<br/>(synapseml package)"]
        blob["Azure Blob Storage<br/>(docs, badges)"]
    end
    
    build --> check
    check -->|true| ado
    check -->|false| sonatype
    
    build --> pypi
    build --> blob
```

### Maven Publishing

**Sonatype / Maven Central** ([sonatype.sbt:1-46]()):
- Project hosting: GitHub (Azure/SynapseML) ([sonatype.sbt:3-4]())
- Developers: 6 core maintainers defined ([sonatype.sbt:12-25]())
- License: MIT ([sonatype.sbt:27]())
- Credentials: Nexus username/password from Key Vault ([sonatype.sbt:29-32]())
- Bundle publishing: `sonatypePublishToBundle.value` ([sonatype.sbt:42]())
- Snapshot versioning: `dynverSonatypeSnapshots := true` ([sonatype.sbt:45]())
- Version separator: `-` instead of `+` ([sonatype.sbt:46]())

**Azure DevOps Feed** ([sonatype.sbt:38-40](), [build.sbt:339-342]()):
- Feed URL: `https://msdata.pkgs.visualstudio.com/A365/_packaging/SynapseML_PublicPackages/maven/v1`
- Credentials: ADO feed token from Key Vault
- Used when `Secrets.publishToFeed == true`
- Enables internal Microsoft consumption before Maven Central release

**POM Customization** ([build.sbt:50-68]()):
The `pomPostFunc` transforms the POM XML to:
- Remove `<extraDependencyAttributes>` elements
- Comment out dependencies with `<scope>` tags (test, provided, etc.)
- Comment out excluded dependencies (`spark-core`, `spark-mllib`, `org.scala-lang`)
- Preserves groupId, artifactId, version as XML comments for traceability

### Python Publishing

**PyPI** ([build.sbt:187-197]()):
- Package name: `synapseml`
- Uses `twine upload` with `__token__` authentication
- `--skip-existing` flag prevents re-upload errors
- Conditional on `SYNAPSEML_ENABLE_PUBLISH=true` and version tag
- Invoked by Release job: ([pipeline.yaml:309-323]())

### ESRP Signing for Release

For official releases (master branch + version tag), JARs undergo ESRP signing:

**Preparation** ([tools/esrp/prepare_jar.py:1-80]()):
- Flattens Ivy local repository structure: `~/.ivy2/local/com.microsoft.azure/`
- Moves all JARs to second-level folders (removes nested structure)
- Renames JARs to include full version: `{name}_2.12-{version}{suffix}`
- Example: `synapseml-core_2.12.jar` → `synapseml-core_2.12-1.0.0.jar`

**ESRP Release Task** ([pipeline.yaml:339-353]()):
- Service connection: `SynapseML-ESRP-Service-Connection`
- Key vault: `esrp-kv-ame`
- Content type: `maven`
- Folder: `/home/vsts/.ivy2/local/com.microsoft.azure/`
- Owners/Approvers: Microsoft email addresses
- Main publisher: `synapseml`
- Only runs when: `and(eq(variables.isMaster, true), startsWith(variables['tag'], 'v'))`

Sources: [sonatype.sbt:1-46](), [build.sbt:50-68](), [build.sbt:187-197](), [tools/esrp/prepare_jar.py:1-80](), [pipeline.yaml:309-353]()

## Build Artifacts

The build system produces multiple artifact types for different consumption scenarios:

| Artifact Type | Task | Output Location | Description |
|---------------|------|-----------------|-------------|
| **Scala JARs** | `publishLocalSigned` | `~/.ivy2/local/com.microsoft.azure/` | Signed JARs for Maven |
| **Python Wheel** | `packageSynapseML` | `target/generated/package/python/` | Universal wheel (py2.py3-none-any) |
| **Python Docs** | `generatePythonDoc` | `target/generated/doc/pyspark/` | Sphinx HTML documentation |
| **Scala Docs** | `unidoc` | `target/unidoc/` → `target/generated/doc/scala/` | ScalaUnidoc API docs |
| **R Package** | `publishR` | Uploaded to Blob Storage | R bindings package |
| **Notebooks** | `uploadNotebooks` | Azure Blob Storage (`docs` container) | Example Jupyter notebooks |
| **Badges** | `publishBadges` | Azure Blob Storage (`icons` container) | Version badges (SVG) |
| **Build Info** | `genBuildInfo` | `target/Build.md` | Version and documentation links |

### Artifact Publishing Flow

```mermaid
graph TB
    subgraph "Compilation"
        compile["sbt compile"]
        test["sbt test"]
    end
    
    subgraph "Local Publishing"
        m2["publishM2<br/>(local Maven)"]
        signed["publishLocalSigned<br/>(with PGP)"]
    end
    
    subgraph "Remote Publishing"
        blob["publishBlob<br/>(Azure Storage)"]
        docs["publishDocs<br/>(Sphinx + ScalaUnidoc)"]
        python["publishPython<br/>(pip package)"]
        r["publishR<br/>(R package)"]
    end
    
    subgraph "Release Publishing"
        pypi["publishPypi<br/>(PyPI)"]
        esrp["ESRP Release<br/>(Maven Central)"]
    end
    
    compile --> test
    test --> m2
    test --> signed
    
    signed --> blob
    signed --> docs
    signed --> python
    signed --> r
    
    python --> pypi
    signed --> esrp
    
    pypi -.->|conditional:<br/>master + tag| final["Published Artifacts"]
    esrp -.->|conditional:<br/>master + tag| final
```

### Artifact Naming Conventions

**JARs:**
- Pattern: `{artifact-name}_2.12-{version}.jar`
- Example: `synapseml-core_2.12-1.0.4.jar`
- Includes source JARs: `{artifact-name}_2.12-{version}-sources.jar`
- Includes doc JARs: `{artifact-name}_2.12-{version}-javadoc.jar`

**Python Wheel:**
- Pattern: `synapseml-{version}-py2.py3-none-any.whl`
- Version conversion: `1.0.4` → `1.0.4` (no transformation needed)
- Universal wheel: compatible with Python 2 and 3, any platform

**Documentation:**
- Scala: `https://mmlspark.blob.core.windows.net/docs/{version}/scala/index.html`
- Python: `https://mmlspark.blob.core.windows.net/docs/{version}/pyspark/index.html`

Sources: [build.sbt:132-241](), [pipeline.yaml:87-353]()

## Integration with CI/CD Pipeline

The build system is invoked at multiple points in the CI/CD pipeline. The pipeline uses Azure DevOps tasks that call SBT commands.

### Build Triggers

**Pipeline Triggers** ([pipeline.yaml:4-43]()):
- **PR/Push**: Triggers on master, spark3.3, spark3.5 branches
- **Excluded Paths**: README, contributor docs, CODEOWNERS (non-code changes)
- **Scheduled**: Daily midnight build (cron: `0 0 * * *`)
- **Manual**: Parameters for Synapse E2E tests

### Environment Setup

**Conda Environment** ([templates/conda.yml:1-42]()):
- Cached at: `/usr/share/miniconda/envs` ([pipeline.yaml:60]())
- Cache key: `conda | "$(Agent.OS)" | environment.yml`
- Restored from cache if environment.yml unchanged
- Created with: `conda env create -f environment.yml` with 30-minute timeout and retry
- Includes Python 3.11.8, R 4.1.1, PyTorch 2.1.0, and all test dependencies ([environment.yml:1-58]())
- Pre-cleans disk space by removing Android and Google Cloud SDKs ([templates/conda.yml:18-28]())

**Key Vault Access** ([templates/kv.yml:1-7]()):
- Task: `AzureKeyVault@2`
- Vault: `mmlspark-keys`
- Loads all secrets as pipeline variables
- Used by Publish, E2E, Python/R/Unit test jobs

### Job-Specific Build Invocations

**Style Job** ([pipeline.yaml:66-84]()):
```bash
sbt scalastyle test:scalastyle
black --diff --color . && black --check -q .
```

**Publish Job** ([pipeline.yaml:87-135]()):
```bash
sbt packagePython uploadNotebooks
sbt -DskipCodegen=true publishBlob publishDocs publishR publishPython
sbt genBuildInfo
sbt -DskipCodegen=true publishLocalSigned
python tools/esrp/prepare_jar.py
sbt publishBadges  # conditional: master only
```

**Unit Tests Job** ([pipeline.yaml:614-772]()):
```bash
sbt setup
sbt coverage "testOnly com.microsoft.azure.synapse.ml.{PACKAGE}.**"
sbt coverageReport
```

**Python Tests Job** ([pipeline.yaml:357-443]()):
```bash
sbt coverage getDatasets installPipPackage publishM2
sbt {FLAGS} "project {PACKAGE}" coverage testPython
sbt coverageReport
```

**R Tests Job** ([pipeline.yaml:446-518]()):
```bash
sbt setup
sbt codegen
sbt publishM2
sbt -DskipCodegen=true "project {PACKAGE}" coverage testR
sbt coverageReport
```

**E2E Tests Job** ([pipeline.yaml:138-181]()):
```bash
sbt "testOnly {TEST-CLASS}"
```
Where TEST-CLASS is one of:
- `com.microsoft.azure.synapse.ml.nbtest.DatabricksCPUTests`
- `com.microsoft.azure.synapse.ml.nbtest.DatabricksGPUTests`

**Website Jobs** ([pipeline.yaml:528-611]()):
```bash
# Test samples
sbt setup
sbt coverage testWebsiteDocs
sbt coverageReport

# Deploy
sbt convertNotebooks
yarn install && cd website && yarn && yarn build
GIT_USER="${GH_NAME}" yarn deploy  # master only
```

**Release Job** ([pipeline.yaml:259-353]()):
```bash
sbt publishPypi  # conditional: master + tag
sbt publishLocalSigned  # conditional: master + tag
python tools/esrp/prepare_jar.py
# ESRP Release task
```

Sources: [pipeline.yaml:4-773](), [templates/conda.yml:1-42](), [templates/kv.yml:1-7](), [environment.yml:1-58]()

## Build Performance Optimizations

The build system includes several optimizations for faster builds:

**Ivy Cache** (commented out):
- Lines like `#- template: templates/ivy_cache.yml` appear throughout ([pipeline.yaml:92](), [160](), [384](), [534](), [728]())
- Previously cached Ivy dependencies, currently disabled
- Would cache `~/.ivy2/cache/` to speed up dependency resolution

**Conda Cache** ([templates/conda.yml:7-16]()):
- Caches entire Conda environment directory
- Key based on OS and environment.yml hash
- Restores in ~1 minute vs 20+ minutes to create
- Cache hit variable: `CONDA_CACHE_RESTORED`

**Parallel Test Execution**:
- Unit tests run with 30+ parallel test packages ([pipeline.yaml:621-726]())
- Python tests split into 7 packages ([pipeline.yaml:365-382]())
- R tests split into 6 packages ([pipeline.yaml:454-465]())
- LightGBM split into 6 test suites due to execution time ([pipeline.yaml:697-714]())

**Retry Mechanisms**:
- SBT setup: 3 retries with 5-minute timeout each ([pipeline.yaml:742]())
- Conda creation: 2 attempts with 30-minute timeout ([templates/conda.yml:32]())
- Python tests: 3 attempts ([pipeline.yaml:425-427]())
- R tests: 3 retry attempts ([pipeline.yaml:492]())
- Flaky test packages: automatic retry on failure ([pipeline.yaml:755]())

**Skip Codegen**:
- `-DskipCodegen=true` flag used in Publish and R tests ([pipeline.yaml:113](), [116](), [502]())
- Skips regeneration of Python/R wrappers when not needed
- Reduces build time by several minutes

Sources: [pipeline.yaml:66-773](), [templates/conda.yml:1-42]()

---

# Page: Multi-Language SDK Generation

# SDK Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala)
- [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala](core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala)
- [core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala](core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [start](start)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/docker/demo/Dockerfile](tools/docker/demo/Dockerfile)
- [tools/docker/demo/README.md](tools/docker/demo/README.md)
- [tools/docker/demo/init_notebook.py](tools/docker/demo/init_notebook.py)
- [tools/docker/minimal/Dockerfile](tools/docker/minimal/Dockerfile)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)
- [tools/tests/run_r_tests.R](tools/tests/run_r_tests.R)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala)

</details>



This document describes the automated SDK generation system in SynapseML, which creates Python and R bindings from the core Scala code. The system enables developers to maintain a single codebase while providing consistent APIs across multiple programming languages.

## Purpose and Scope

The SDK generation system is responsible for:
- Automatically generating Python and R code from Scala classes
- Creating tests for the generated code
- Building and packaging the SDKs for distribution
- Ensuring consistency between the Scala, Python, and R APIs

This system is a critical part of the SynapseML build infrastructure, allowing the project to be used seamlessly in different languages.

Sources: [project/CodegenPlugin.scala:25-30]()

## Architecture Overview

The SDK generation system is implemented as an SBT plugin (`CodegenPlugin`) that integrates with the SynapseML build process. It consists of several key components that handle different aspects of code generation, testing, packaging, and publishing.

### SDK Generation System Architecture

```mermaid
graph TD
    subgraph "SDK Generation System"
        CodegenPlugin["CodegenPlugin"] --> PythonGen["Python SDK Generation"]
        CodegenPlugin --> RGen["R SDK Generation"]
        
        PythonGen --> PyCodegen["pyCodegen Task"]
        PythonGen --> PyTestgen["pyTestgen Task"]
        PythonGen --> PyPackage["packagePython Task"]
        PythonGen --> PyPublish["publishPython Task"]
        
        RGen --> RCodegen["rCodeGen Task"]
        RGen --> RTestgen["rTestGen Task"]
        RGen --> RPackage["packageR Task"]
        RGen --> RPublish["publishR Task"]
        
        PyCodegen --> PyOutput["Python Source Code"]
        PyTestgen --> PyTestOutput["Python Test Code"]
        RCodegen --> ROutput["R Source Code"]
        RTestgen --> RTestOutput["R Test Code"]
    end
    
    ScalaCode["Scala Source Code"] --> CodegenPlugin
    PyOutput --> PyWheel["Python Wheel Package"]
    ROutput --> RPackageZip["R Package ZIP"]
    
    PyWheel --> BlobStorage["Azure Blob Storage"]
    RPackageZip --> BlobStorage
```

Sources: [project/CodegenPlugin.scala:25-307](), [project/build.scala:1-165]()

## CodegenPlugin Implementation

The `CodegenPlugin` is implemented as an SBT AutoPlugin that provides tasks for generating Python and R code from Scala classes. It uses a configuration case class `CodegenConfig` to manage generation parameters.

### CodegenConfig Parameters

| Parameter | Description |
|-----------|-------------|
| name | Project name |
| jarName | Optional JAR name for codegen |
| topDir | Top directory path |
| targetDir | Target directory path |
| version | Version string |
| pythonizedVersion | Python-compatible version string |
| rVersion | R version string |
| packageName | Package namespace |

Sources: [project/CodegenPlugin.scala:16-23]()

### Key Tasks in CodegenPlugin

The plugin defines several SBT tasks for different aspects of SDK generation:

| Task | Description | Implementation |
|------|-------------|----------------|
| codegen | Generate code from Scala | [project/CodegenPlugin.scala:190-203]() |
| pyCodegen | Generate Python code | [project/CodegenPlugin.scala:114-121]() |
| pyTestgen | Generate Python tests | [project/CodegenPlugin.scala:123-130]() |
| packagePython | Package Python SDK | [project/CodegenPlugin.scala:231-242]() |
| publishPython | Publish Python wheel | [project/CodegenPlugin.scala:254-262]() |
| rCodeGen | Generate R code | [project/CodegenPlugin.scala:132-139]() |
| rTestGen | Generate R tests | [project/CodegenPlugin.scala:141-148]() |
| packageR | Generate roxygen docs and package R | [project/CodegenPlugin.scala:213-222]() |
| publishR | Publish R package | [project/CodegenPlugin.scala:224-230]() |

Sources: [project/CodegenPlugin.scala:42-74](), [project/CodegenPlugin.scala:114-262]()

## Code Generation Process

### Generation Process Flow

```mermaid
sequenceDiagram
    participant Scala as "Scala Source Code"
    participant Plugin as "CodegenPlugin"
    participant Py as "Python SDK"
    participant R as "R SDK"
    participant Test as "Test Generation"
    participant Pkg as "Package Build"
    
    Scala->>Plugin: SBT compile task
    Plugin->>Py: pyCodegen task
    Plugin->>R: rCodeGen task
    Plugin->>Test: testgen task
    
    Py->>Test: pyTestgen task
    R->>Test: rTestGen task
    
    Py->>Pkg: packagePython task
    R->>Pkg: packageR task
    
    Pkg->>Pkg: publishPython/publishR task
```

Sources: [project/CodegenPlugin.scala:114-148](), [project/CodegenPlugin.scala:213-262]()

### Python SDK Generation

The Python SDK generation process transforms Scala classes and their parameters into equivalent Python classes. The `pyCodegen` task runs the `PyCodegen` class which extracts metadata from the compiled Scala classes and generates Python code.

Key components in Python generation:
- Class translation from Scala to Python
- Parameter conversion between languages
- Type mapping between Scala and Python types
- Documentation generation from Scala docs

Sources: [project/CodegenPlugin.scala:114-121](), [project/CodegenPlugin.scala:231-262]()

### R SDK Generation

Similarly, the R SDK generation process transforms Scala classes and their parameters into equivalent R functions and classes. The `rCodeGen` task runs the `RCodegen` class to extract metadata and generate R code.

Key components in R generation:
- Function generation from Scala classes
- Parameter mapping from Scala to R
- Documentation generation with roxygen2
- Building R package structure

Sources: [project/CodegenPlugin.scala:132-139](), [project/CodegenPlugin.scala:213-230]()

## Test Generation System

An important part of the SDK generation process is the automatic generation of tests for the Python and R bindings. This ensures that the generated SDKs work as expected and maintain compatibility with the core Scala implementation.

### Test Generation Architecture

```mermaid
graph TD
    subgraph "Test Generation System"
        FuzzingBase["Fuzzing.scala"] --> PyTestFuzzing["PyTestFuzzing Trait"]
        FuzzingBase --> RTestFuzzing["RTestFuzzing Trait"]
        
        PyTestFuzzing --> PyTestGen["PyTestGen.scala"]
        RTestFuzzing --> RTestGen["RTestGen.scala"]
        
        PyTestGen --> PyTests["Python Tests"]
        RTestGen --> RTests["R Tests"]
        
        TestObj["TestObject Class"] --> PyTestFuzzing
        TestObj --> RTestFuzzing
    end
    
    MLModel["ML Pipeline Stage"] --> TestObj
    PyTests --> TestFramework["Test Framework"]
    RTests --> TestFramework
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:36-622](), [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/PyTestGen.scala:1-67]()

### Fuzzing-Based Test Generation

The test generation system uses a technique called "fuzzing" to generate comprehensive tests for the SDK. The `Fuzzing.scala` file defines several traits that implement different aspects of test generation:

- `PyTestFuzzing`: Generates Python tests 
- `RTestFuzzing`: Generates R tests
- `SerializationFuzzing`: Tests serialization/deserialization
- `ExperimentFuzzing`: Tests ML experiments
- `GetterSetterFuzzing`: Tests getter/setter methods

These traits use introspection to analyze the parameters and behavior of the Scala classes and generate equivalent tests for Python and R.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:64-122](), [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:233-416]()

### Python Test Generation

Python test generation is implemented in the `PyTestFuzzing` trait and is executed by the `PyTestGen.scala` script. The process involves:

1. Generating test models and datasets
2. Creating Python test cases for instantiation and usage
3. Testing model serialization and MLflow integration
4. Validating model correspondence between Scala and Python

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:64-230](), [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/PyTestGen.scala:18-67]()

### R Test Generation

R test generation follows a similar pattern in the `RTestFuzzing` trait:

1. Generating test models and datasets
2. Creating R test cases with testthat format
3. Testing model correspondence between Scala and R
4. Validating model functionality

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:233-422]()

## Package Building and Publishing

After code and test generation, the SDKs need to be packaged and published. The CodegenPlugin handles this process.

### Python Packaging

The Python SDK is packaged as a wheel using the standard Python packaging tools. The `packagePython` task:

1. Ensures the code is generated
2. Sets up the package directory structure
3. Runs the Python `setup.py bdist_wheel` command
4. Creates a universal wheel package

The `publishPython` task then uploads this wheel to Azure Blob Storage.

Sources: [project/CodegenPlugin.scala:231-262](), [project/build.scala:77-83]()

### R Packaging

The R SDK packaging process involves:

1. Generating roxygen2 documentation
2. Creating the R package directory structure
3. Zipping the package
4. Publishing to storage (via the `publishR` task)

Sources: [project/CodegenPlugin.scala:213-230]()

## Integration with Build System

The SDK generation is integrated into the SynapseML build system. The tasks are designed to be composable with other SBT tasks, allowing for smooth integration into the CI/CD pipeline.

### Versioning

The system handles version normalization between Scala, Python, and R:

- Python version normalization via `pythonizedVersion` (converts '-' to '.dev1')
- R version handling specifically for CRAN compliance

Sources: [project/build.scala:26-31]()

### Conda Environment Integration

The SDK generation tasks integrate with the CondaPlugin to ensure that the correct Python/R environment is available for building and testing:

```mermaid
graph LR
    CodegenPlugin --> CondaPlugin["CondaPlugin"]
    CondaPlugin --> CondaEnv["Conda Environment"]
    CodegenPlugin --> Commands["Python/R Commands"]
    CondaEnv --> Commands
    Commands --> SDKs["Generated SDKs"]
```

Sources: [project/CodegenPlugin.scala:29](), [project/CodegenPlugin.scala:92-96]()

## Conclusion

The SDK Generation system in SynapseML provides a powerful mechanism for maintaining a consistent API across multiple programming languages. By automatically generating Python and R bindings from the core Scala code, it ensures that users of different languages have access to the same functionality while maintaining a single source of truth in the codebase.

The system's integration with testing, packaging, and publishing makes it a comprehensive solution for multi-language library development. The fuzzing-based test generation further ensures robust cross-language compatibility.

Sources: [project/CodegenPlugin.scala:25-307](), [core/src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:604-630]()

---

# Page: Security and Code Quality

# Security and Code Quality

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check-dead-links.yml](.github/workflows/check-dead-links.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [.github/workflows/scorecards.yml](.github/workflows/scorecards.yml)
- [.gitignore](.gitignore)
- [.pipelines/clean-acr.yml](.pipelines/clean-acr.yml)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [docs/Deploy Models/Quickstart - Deploying a Classifier.ipynb](docs/Deploy Models/Quickstart - Deploying a Classifier.ipynb)
- [docs/Explore Algorithms/Deep Learning/Distributed Training.md](docs/Explore Algorithms/Deep Learning/Distributed Training.md)
- [docs/Explore Algorithms/Hyperparameter Tuning/Quickstart - Random Search.ipynb](docs/Explore Algorithms/Hyperparameter Tuning/Quickstart - Random Search.ipynb)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/acr/clean-acr.py](tools/acr/clean-acr.py)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



This document details the security practices and code quality measures implemented in the SynapseML project. It covers the automated security scanning tools, code quality checks, vulnerability management processes, and best practices for maintaining high standards of code quality and security throughout the development lifecycle.

For information about the CI/CD pipeline implementation, see [CI/CD Pipeline](#3.1). For build system details, see [Build System](#3.2).

## 1. Security Scanning Framework

SynapseML employs multiple automated security scanning tools to identify and mitigate potential vulnerabilities in the codebase.

```mermaid
flowchart TD
    subgraph "Security Scanning Framework"
        CodeQL["CodeQL Analysis"]
        Scorecards["OSSF Scorecards"]
        SecretDetection["Secret Detection"]
        DependencyCheck["Dependency Scanning"]
        
        CodeQL --> VulnerabilityDashboard["GitHub Security Dashboard"]
        Scorecards --> VulnerabilityDashboard
        SecretDetection --> VulnerabilityDashboard
        DependencyCheck --> VulnerabilityDashboard
    end
    
    subgraph "Security Governance"
        SecurityPolicies["Security Policies"]
        VulnerabilityManagement["Vulnerability Management"]
        
        VulnerabilityDashboard --> VulnerabilityManagement
        SecurityPolicies --> VulnerabilityManagement
    end
    
    subgraph "Developer Workflow"
        PullRequest["Pull Requests"]
        CodeReview["Code Review"]
        
        PullRequest --> SecurityChecks["Security Checks"]
        SecurityChecks --> CodeReview
    end
    
    VulnerabilityManagement --> SecurityChecks
```

Sources: [.github/workflows/scorecards.yml:1-72](), [.github/workflows/codeql.yml:1-78]()

### 1.1 CodeQL Analysis

SynapseML uses GitHub's CodeQL to perform static code analysis for identifying security vulnerabilities and code quality issues:

- **Languages analyzed**: JavaScript and Python
- **Execution frequency**: Runs on pushes to master, pull requests to master, and weekly on a schedule
- **Configuration**: Defined in the CodeQL workflow file, which sets up the CodeQL engine and performs analysis steps

The analysis results are uploaded to GitHub's code scanning dashboard, where they can be reviewed and addressed by the development team.

Sources: [.github/workflows/codeql.yml:1-78]()

### 1.2 OSSF Scorecards

The project leverages the Open Source Security Foundation (OSSF) Scorecards to assess security posture against industry best practices:

- **Scans for**: Branch protection rules, maintained status, dependency update practices, code review processes
- **Publishing results**: Results are published to the OpenSSF API and made available through a badge for public transparency
- **Execution frequency**: Weekly on Sundays and on pushes to the master branch

Scorecards evaluates numerous security criteria and provides an overall security score for the project.

Sources: [.github/workflows/scorecards.yml:1-72]()

### 1.3 Dependency Scanning

The project monitors dependencies for security vulnerabilities through automated scanning. When vulnerabilities are detected, they are reported and addressed based on severity level.

## 2. Code Quality Framework

SynapseML maintains code quality through a combination of automated tools, review processes, and standardized practices.

```mermaid
flowchart TD
    subgraph "Code Quality Tooling"
        StyleChecks["Style Checkers"]
        UnitTests["Unit Tests"]
        IntegrationTests["Integration Tests"]
        E2ETests["End-to-End Tests"]
        
        StyleChecks --> BuildJobs["Build Jobs"]
        UnitTests --> TestJobs["Test Jobs"]
        IntegrationTests --> TestJobs
        E2ETests --> TestJobs
    end
    
    subgraph "Quality Gates"
        PRValidation["PR Validation"]
        DocValidation["Documentation Validation"]
        
        BuildJobs --> PRValidation
        TestJobs --> PRValidation
        LinkChecker["Dead Link Checker"] --> DocValidation
    end
    
    subgraph "Code Reviews"
        PeerReview["Peer Review Process"]
        QualityMetrics["Quality Metrics Tracking"]
        
        PRValidation --> PeerReview
        DocValidation --> PeerReview
        PeerReview --> QualityMetrics
    end
    
    QualityMetrics --> ContinuousImprovement["Continuous Improvement"]
```

Sources: [.github/workflows/check-dead-links.yml:1-27]()

### 2.1 Automated Code Style Enforcement

The project enforces consistent code style through automated checks in the CI pipeline:

- **Style checkers**: Applied to all code submissions
- **Linting rules**: Tailored for different languages (Python, Scala, R)
- **Enforcement**: Style checks must pass before code can be merged

### 2.2 Comprehensive Testing Strategy

The testing strategy includes various levels of testing to ensure code quality:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Verify interactions between components
- **End-to-end tests**: Test complete workflows
- **Fuzzing tests**: For robustness of APIs and SDK generation

These tests run as part of the CI/CD pipeline on pull requests and periodic schedules.

### 2.3 Documentation Quality

Documentation quality is maintained through:

- **Dead link checking**: Automated scanning of documentation for broken links
- **Example validation**: Regular verification that example notebooks are functional
- **Consistency reviews**: Ensuring documentation matches implemented functionality

Sources: [.github/workflows/check-dead-links.yml:1-27]()

## 3. Security Process Integration

SynapseML integrates security and code quality processes into the development workflow through GitHub and Azure DevOps.

```mermaid
flowchart TD
    subgraph "GitHub"
        Issues["GitHub Issues"]
        PullRequests["Pull Requests"]
        SecurityScans["Security Scans"]
        
        Issues --> PullRequests
        PullRequests --> SecurityScans
    end
    
    subgraph "Azure DevOps"
        WorkItems["ADO Work Items"]
        Pipelines["ADO Pipelines"]
        SecurityTasks["Security Tasks"]
        
        WorkItems --> Pipelines
        SecurityScans --> SecurityTasks
    end
    
    subgraph "Integration Workflows"
        IssueSynchronization["Issue Synchronization"]
        PRWorkItemAssociation["PR-WorkItem Association"]
        
        Issues --> IssueSynchronization
        IssueSynchronization --> WorkItems
        PullRequests --> PRWorkItemAssociation
        PRWorkItemAssociation --> WorkItems
    end
    
    AzureKeyVault["Azure Key Vault"] --> Pipelines
    SecurityTasks --> ReleaseDecisions["Release Decisions"]
```

Sources: [.github/workflows/ado-pr-to-workitem.yml:1-24](), [.github/workflows/ado-integration.yml:1-24]()

### 3.1 GitHub and Azure DevOps Integration

The project synchronizes work tracking between GitHub and Azure DevOps:

- **Issue synchronization**: GitHub issues are synchronized with Azure DevOps work items
- **Pull request integration**: Pull requests are linked to Azure DevOps work items
- **Status tracking**: Work item status is updated based on GitHub activities

This integration ensures traceability between code changes and work items, providing a comprehensive view of development activities and security-related tasks.

Sources: [.github/workflows/ado-pr-to-workitem.yml:1-24](), [.github/workflows/ado-integration.yml:1-24]()

### 3.2 Secure Secret Management

SynapseML manages secrets securely using Azure Key Vault:

- **Secrets storage**: All API keys, tokens, and sensitive configuration values are stored in Azure Key Vault
- **Access control**: Access to secrets is controlled through Azure Active Directory authentication
- **CI/CD integration**: Pipelines retrieve secrets securely during build and deployment processes

This approach prevents secrets from being exposed in the codebase or logs.

## 4. Container Registry Security

SynapseML maintains security in its container infrastructure through regular cleanup and verification processes.

```mermaid
flowchart TD
    subgraph "Container Registry Management"
        ACR["Azure Container Registry"]
        BlobStorage["Azure Blob Storage"]
        KeyVault["Azure Key Vault"]
        
        KeyVault --> ConnectionStrings["Connection Strings"]
        ConnectionStrings --> CleanupScript["ACR Cleanup Script"]
        
        CleanupScript --> ListRepositories["List ACR Repositories"]
        ListRepositories --> BackupImages["Backup Images to Blob"]
        BackupImages --> VerifyBackup["Verify Backup Success"]
        VerifyBackup --> DeleteFromACR["Delete from ACR"]
        
        ACR --> ListRepositories
        BackupImages --> BlobStorage
        DeleteFromACR --> ACR
    end
    
    subgraph "Automation"
        PipelineScheduler["Weekly Cleanup Schedule"]
        ErrorHandling["Error Handling & Retry"]
        
        PipelineScheduler --> CleanupScript
        CleanupScript --> ErrorHandling
    end
```

Sources: [.pipelines/clean-acr.yml:1-30](), [tools/acr/clean-acr.py:1-87]()

### 4.1 Container Registry Cleanup

The project implements regular cleanup of the Azure Container Registry (ACR) to maintain security and performance:

- **Backup process**: Images are backed up to Azure Blob Storage before deletion
- **Verification**: Backup success is verified before deletion from ACR
- **Automation**: Process runs on a weekly schedule
- **Error handling**: Includes retry logic for resiliency

This process maintains a clean container registry while ensuring images are properly preserved.

Sources: [.pipelines/clean-acr.yml:1-30](), [tools/acr/clean-acr.py:1-87]()

## 5. Contributor Guidelines

Contributors to SynapseML are expected to follow security and code quality best practices:

1. **Security review**: Include security considerations in code reviews
2. **Test coverage**: Maintain or improve test coverage with new contributions
3. **Documentation**: Update documentation to reflect changes
4. **Dependency management**: Carefully evaluate new dependencies for security implications
5. **Secret handling**: Never commit secrets or credentials to the repository

By following these guidelines, contributors help maintain the project's security and code quality standards.

## 6. Continuous Monitoring and Improvement

SynapseML employs continuous monitoring and improvement processes:

- **Vulnerability monitoring**: Ongoing monitoring for new vulnerabilities in dependencies
- **Security patch management**: Prompt application of security patches
- **Process refinement**: Regular review and improvement of security and code quality processes
- **Training**: Keeping the development team informed about security best practices

These processes ensure that security and code quality remain priorities throughout the project lifecycle.

---

# Page: Azure DevOps Integration

# Azure DevOps Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ado-integration.yml](.github/workflows/ado-integration.yml)
- [.github/workflows/ado-pr-to-workitem.yml](.github/workflows/ado-pr-to-workitem.yml)

</details>



## Purpose and Scope

This document describes the GitHub to Azure DevOps work item synchronization system that automatically creates and updates work items in Azure Boards based on GitHub issues and pull requests. This integration allows the development team to track work in Azure DevOps while working in GitHub.

This system is distinct from the CI/CD Pipeline ([3.1](#3.1)), which handles build, test, and deployment automation. The Azure DevOps Integration focuses solely on work item tracking and synchronization.

---

## System Overview

The Azure DevOps integration consists of two GitHub Actions workflows that maintain bidirectional synchronization between GitHub and Azure DevOps work items. When developers create or modify issues and pull requests in GitHub, corresponding work items are automatically created or updated in Azure Boards within the `msdata/A365` project.

### Integration Architecture

```mermaid
graph TB
    subgraph "GitHub"
        Issues["GitHub Issues"]
        PullRequests["GitHub Pull Requests"]
    end
    
    subgraph "GitHub Actions Workflows"
        IssueWorkflow["ado-integration.yml<br/>Issue Sync Workflow"]
        PRWorkflow["ado-pr-to-workitem.yml<br/>PR Sync Workflow"]
    end
    
    subgraph "Third-Party Actions"
        IssueAction["mhamilton723/github-actions-issue-to-work-item@master"]
        PRAction["danhellem/github-actions-pr-to-work-item@master"]
    end
    
    subgraph "Azure DevOps"
        ADOOrg["Organization: msdata"]
        ADOProject["Project: A365"]
        WorkItems["Work Items (Tasks)"]
    end
    
    subgraph "Secrets Management"
        ADOToken["ADO_PERSONAL_ACCESS_TOKEN"]
        GHToken["GH_PERSONAL_ACCESS_TOKEN"]
        AreaPath["ADO_AREA_PATH"]
    end
    
    Issues --> IssueWorkflow
    PullRequests --> PRWorkflow
    
    IssueWorkflow --> IssueAction
    PRWorkflow --> PRAction
    
    IssueAction --> ADOToken
    IssueAction --> GHToken
    IssueAction --> AreaPath
    
    PRAction --> ADOToken
    PRAction --> GHToken
    PRAction --> AreaPath
    
    IssueAction --> ADOOrg
    PRAction --> ADOOrg
    
    ADOOrg --> ADOProject
    ADOProject --> WorkItems
```

**Sources:** [.github/workflows/ado-integration.yml:1-24](), [.github/workflows/ado-pr-to-workitem.yml:1-24]()

---

## Issue Synchronization

The issue synchronization workflow (`ado-integration.yml`) monitors GitHub issue events and creates or updates corresponding Azure DevOps work items. This workflow uses the `mhamilton723/github-actions-issue-to-work-item` action.

### Trigger Configuration

The workflow is triggered by the following GitHub issue events:

| Event Type | Description | ADO Action |
|------------|-------------|------------|
| `opened` | New issue created | Creates new work item in "To Do" state |
| `edited` | Issue title/description modified | Updates work item details |
| `deleted` | Issue deleted | Deletes corresponding work item |
| `closed` | Issue closed | Moves work item to "Done" state |
| `reopened` | Closed issue reopened | Moves work item to "In Progress" state |
| `labeled` | Label added to issue | Updates work item tags |
| `unlabeled` | Label removed from issue | Updates work item tags |
| `assigned` | User assigned to issue | Updates work item assignment |

**Sources:** [.github/workflows/ado-integration.yml:4-6]()

### State Mapping

```mermaid
stateDiagram-v2
    [*] --> ToDo: Issue Opened
    ToDo --> InProgress: Issue Reopened/Assigned
    InProgress --> Done: Issue Closed
    Done --> InProgress: Issue Reopened
    
    note right of ToDo
        ado_new_state: "To Do"
    end note
    
    note right of InProgress
        ado_active_state: "In Progress"
    end note
    
    note right of Done
        ado_close_state: "Done"
    end note
```

**Sources:** [.github/workflows/ado-integration.yml:20-22]()

### Workflow Configuration

The issue synchronization workflow is defined in [.github/workflows/ado-integration.yml:1-24]() with the following parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `ado_organization` | `msdata` | Azure DevOps organization name |
| `ado_project` | `A365` | Azure DevOps project name |
| `ado_wit` | `Task` | Work item type to create |
| `ado_new_state` | `To Do` | Initial state for new work items |
| `ado_active_state` | `In Progress` | State for active/reopened items |
| `ado_close_state` | `Done` | State for closed items |
| `ado_bypassrules` | `true` | Bypass Azure DevOps validation rules |

**Sources:** [.github/workflows/ado-integration.yml:16-23]()

---

## Pull Request Synchronization

The pull request synchronization workflow (`ado-pr-to-workitem.yml`) tracks pull requests targeting the `master` branch and creates corresponding Azure DevOps work items. This workflow uses the `danhellem/github-actions-pr-to-work-item` action.

### Trigger Configuration

The workflow is triggered by pull request events on the `master` branch:

```mermaid
graph LR
    PROpened["PR Opened"] --> CreateWorkItem["Create Work Item<br/>State: In Progress"]
    PREdited["PR Edited"] --> UpdateWorkItem["Update Work Item<br/>Details"]
    PRClosed["PR Closed"] --> CloseWorkItem["Close Work Item<br/>State: Done"]
```

**Sources:** [.github/workflows/ado-pr-to-workitem.yml:4-7]()

### Workflow Details

The workflow configuration in [.github/workflows/ado-pr-to-workitem.yml:1-24]() specifies:

```yaml
on:
  pull_request_target:
    types: [opened, edited, closed]
    branches:
      - master
```

Key differences from issue synchronization:

1. **Trigger Type**: Uses `pull_request_target` instead of `pull_request` for security reasons (allows access to secrets in PRs from forks)
2. **Branch Filter**: Only processes PRs targeting the `master` branch
3. **State Model**: Simpler state transitions (no "To Do" state, PRs start as "In Progress")
4. **Debug Mode**: Enables debug logging with `debug: true`

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `ado_organization` | `msdata` | Azure DevOps organization |
| `ado_project` | `A365` | Target project |
| `ado_wit` | `Task` | Work item type |
| `ado_active_state` | `In Progress` | State for open PRs |
| `ado_close_state` | `Done` | State for merged/closed PRs |
| `debug` | `true` | Enable verbose logging |

**Sources:** [.github/workflows/ado-pr-to-workitem.yml:3-23]()

---

## Authentication and Security

Both workflows require secure authentication to both GitHub and Azure DevOps APIs. The authentication mechanism uses GitHub Secrets to store sensitive tokens.

### Required Secrets

```mermaid
graph TB
    subgraph "GitHub Secrets"
        ADOToken["ADO_PERSONAL_ACCESS_TOKEN<br/>Azure DevOps PAT"]
        GHToken["GH_PERSONAL_ACCESS_TOKEN<br/>GitHub PAT"]
        AreaPath["ADO_AREA_PATH<br/>Azure DevOps Area Path"]
    end
    
    subgraph "Workflow Environments"
        IssueEnv["Issue Workflow Environment"]
        PREnv["PR Workflow Environment"]
    end
    
    subgraph "External APIs"
        GitHubAPI["GitHub API<br/>Issue/PR Operations"]
        ADOAPI["Azure DevOps API<br/>Work Item Operations"]
    end
    
    ADOToken --> IssueEnv
    ADOToken --> PREnv
    GHToken --> IssueEnv
    GHToken --> PREnv
    AreaPath --> IssueEnv
    AreaPath --> PREnv
    
    IssueEnv --> GitHubAPI
    IssueEnv --> ADOAPI
    PREnv --> GitHubAPI
    PREnv --> ADOAPI
```

### Secret Configuration

The workflows reference secrets in their environment variables:

**Issue Workflow:**
```yaml
env:
  ado_token: "${{ secrets.ADO_PERSONAL_ACCESS_TOKEN }}"
  github_token: "${{ secrets.GH_PERSONAL_ACCESS_TOKEN }}"
  ado_area_path: '${{ secrets.ADO_AREA_PATH }}'
```

**PR Workflow:**
```yaml
env:
  ado_token: '${{ secrets.ADO_PERSONAL_ACCESS_TOKEN }}'
  github_token: '${{ secrets.GH_PERSONAL_ACCESS_TOKEN }}'
  ado_area_path: '${{ secrets.ADO_AREA_PATH }}'
```

#### Token Requirements

| Secret | Permissions Required | Purpose |
|--------|---------------------|---------|
| `ADO_PERSONAL_ACCESS_TOKEN` | Work Items (Read, Write, Delete) | Create, update, and manage Azure DevOps work items |
| `GH_PERSONAL_ACCESS_TOKEN` | repo (Full control) | Read issue/PR metadata and update GitHub objects |
| `ADO_AREA_PATH` | N/A (configuration value) | Specify Azure DevOps area path for work item organization |

**Sources:** [.github/workflows/ado-integration.yml:14-18](), [.github/workflows/ado-pr-to-workitem.yml:15-22]()

---

## Workflow Execution Details

### Issue Sync Execution Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant Action as Issue Sync Action
    participant ADO as Azure DevOps
    
    Dev->>GH: Create/Edit Issue
    GH->>Action: Trigger ado-integration.yml
    Action->>GH: Fetch Issue Details
    Action->>ADO: Authenticate with PAT
    Action->>ADO: Check for Existing Work Item
    
    alt Work Item Does Not Exist
        Action->>ADO: Create New Task (To Do)
    else Work Item Exists
        Action->>ADO: Update Task Details
    end
    
    Action->>GH: Add Work Item Link to Issue
    ADO-->>Dev: Work Item Available in A365 Project
```

### PR Sync Execution Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant Action as PR Sync Action
    participant ADO as Azure DevOps
    
    Dev->>GH: Create PR to Master
    GH->>Action: Trigger ado-pr-to-workitem.yml
    Action->>GH: Fetch PR Details
    Action->>ADO: Authenticate with PAT
    Action->>ADO: Create Task (In Progress)
    Action->>GH: Link Work Item to PR
    
    Dev->>GH: Merge PR
    GH->>Action: Trigger on PR Closed
    Action->>ADO: Update Task State (Done)
```

**Sources:** [.github/workflows/ado-integration.yml:9-24](), [.github/workflows/ado-pr-to-workitem.yml:10-24]()

---

## Third-Party Actions

Both workflows depend on community-maintained GitHub Actions for the actual synchronization logic. These actions handle the API interactions with Azure DevOps.

### Issue Sync Action

**Action:** `mhamilton723/github-actions-issue-to-work-item@master`

This action is referenced at [.github/workflows/ado-integration.yml:12]() and provides:
- Bidirectional synchronization between GitHub issues and Azure DevOps work items
- Label and assignment synchronization
- State management based on issue lifecycle events
- Support for the `ado_bypassrules` parameter to skip Azure DevOps validation

### PR Sync Action

**Action:** `danhellem/github-actions-pr-to-work-item@master`

This action is referenced at [.github/workflows/ado-pr-to-workitem.yml:13]() and provides:
- Pull request to work item synchronization
- Debug logging capabilities
- Support for `pull_request_target` trigger type
- Simplified state management for PR workflows

### Action Maintenance

Both actions are pinned to the `@master` branch rather than specific version tags. This approach ensures the workflows receive bug fixes automatically but may introduce breaking changes without notice.

**Sources:** [.github/workflows/ado-integration.yml:12](), [.github/workflows/ado-pr-to-workitem.yml:13]()

---

## Configuration Summary

The following table summarizes the complete configuration for both synchronization workflows:

| Configuration Aspect | Issue Sync | PR Sync |
|---------------------|------------|---------|
| **Workflow File** | `.github/workflows/ado-integration.yml` | `.github/workflows/ado-pr-to-workitem.yml` |
| **Trigger Events** | Issue events (8 types) | PR events (3 types) |
| **Branch Filter** | None | `master` only |
| **Trigger Type** | `issues` | `pull_request_target` |
| **Third-Party Action** | `mhamilton723/github-actions-issue-to-work-item@master` | `danhellem/github-actions-pr-to-work-item@master` |
| **ADO Organization** | `msdata` | `msdata` |
| **ADO Project** | `A365` | `A365` |
| **Work Item Type** | `Task` | `Task` |
| **Initial State** | `To Do` | `In Progress` |
| **Active State** | `In Progress` | `In Progress` |
| **Close State** | `Done` | `Done` |
| **Bypass Rules** | `true` | Not specified |
| **Debug Mode** | Not specified | `true` |

**Sources:** [.github/workflows/ado-integration.yml:1-24](), [.github/workflows/ado-pr-to-workitem.yml:1-24]()

---

## Integration with Development Workflow

The Azure DevOps integration complements the CI/CD Pipeline ([3.1](#3.1)) by providing work tracking capabilities without interfering with automated builds and tests.

### Workflow Relationship

```mermaid
graph TB
    subgraph "Developer Actions"
        CreateIssue["Create GitHub Issue"]
        CreatePR["Create Pull Request"]
    end
    
    subgraph "ADO Integration (This System)"
        SyncIssue["Sync to Azure Boards<br/>ado-integration.yml"]
        SyncPR["Sync to Azure Boards<br/>ado-pr-to-workitem.yml"]
    end
    
    subgraph "CI/CD Pipeline (3.1)"
        BuildPipeline["Azure DevOps Build Pipeline<br/>Run Tests, Build Artifacts"]
    end
    
    subgraph "Tracking System"
        WorkItems["Azure Boards Work Items"]
    end
    
    CreateIssue --> SyncIssue
    CreatePR --> SyncPR
    CreatePR --> BuildPipeline
    
    SyncIssue --> WorkItems
    SyncPR --> WorkItems
    
    BuildPipeline -.->|Status Updates| CreatePR
```

The ADO integration runs independently of the build pipeline, ensuring that work item tracking continues even if builds fail. This separation of concerns allows project managers to track development progress in Azure Boards while engineers work in GitHub.

**Sources:** [.github/workflows/ado-integration.yml:1-24](), [.github/workflows/ado-pr-to-workitem.yml:1-24]()

---

# Page: Resource Management

# Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/check-dead-links.yml](.github/workflows/check-dead-links.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [.github/workflows/scorecards.yml](.github/workflows/scorecards.yml)
- [.pipelines/clean-acr.yml](.pipelines/clean-acr.yml)
- [docs/Deploy Models/Quickstart - Deploying a Classifier.ipynb](docs/Deploy Models/Quickstart - Deploying a Classifier.ipynb)
- [docs/Explore Algorithms/Deep Learning/Distributed Training.md](docs/Explore Algorithms/Deep Learning/Distributed Training.md)
- [docs/Explore Algorithms/Hyperparameter Tuning/Quickstart - Random Search.ipynb](docs/Explore Algorithms/Hyperparameter Tuning/Quickstart - Random Search.ipynb)
- [tools/acr/clean-acr.py](tools/acr/clean-acr.py)
- [tools/misc/get-stats](tools/misc/get-stats)
- [tools/misc/get-stats.js](tools/misc/get-stats.js)
- [tools/misc/mmlspark.svg](tools/misc/mmlspark.svg)

</details>



## Purpose and Scope

This document describes the automated resource management systems in SynapseML that handle infrastructure cleanup and telemetry collection. These systems run on scheduled intervals to maintain cost efficiency and track project metrics. The page covers two primary systems:

1. **ACR Image Backup and Cleanup** - Automated backup and deletion of Azure Container Registry images
2. **Statistics Collection** - Periodic collection of repository metrics from GitHub and Docker Hub

For information about the CI/CD pipeline infrastructure, see [CI/CD Pipeline](#3.1). For security scanning and code quality, see [Security and Code Quality](#3.4).

## Resource Management Overview

The SynapseML project implements automated resource management to control costs and maintain visibility into project health. These systems run independently as scheduled workflows and operate without manual intervention.

```mermaid
graph TB
    subgraph "Scheduled Triggers"
        WeeklyCron["Weekly Cron<br/>Sunday 1:00 AM UTC"]
        CustomSchedule["Custom Schedule<br/>Configurable"]
    end
    
    subgraph "Resource Management Systems"
        ACRCleanup["ACR Cleanup Pipeline<br/>.pipelines/clean-acr.yml"]
        StatsCollection["Statistics Collection<br/>tools/misc/get-stats"]
    end
    
    subgraph "Infrastructure Services"
        AzureCLI["Azure CLI<br/>az acr, az storage"]
        KeyVault["Azure Key Vault<br/>mmlspark-keys"]
        BlobStorage["Azure Blob Storage<br/>mmlspark account"]
    end
    
    subgraph "Target Resources"
        ACR["Azure Container Registry<br/>mmlsparkmcr"]
        GitHub["GitHub API<br/>Repository Metrics"]
        DockerHub["Docker Hub API<br/>microsoft/mmlspark"]
    end
    
    subgraph "Storage Destinations"
        ACRBackup["Blob Container: acrbackup<br/>.tar archives"]
        StatsLog["Blob Container: stats<br/>log file"]
    end
    
    WeeklyCron --> ACRCleanup
    CustomSchedule --> StatsCollection
    
    ACRCleanup --> AzureCLI
    ACRCleanup --> KeyVault
    
    AzureCLI --> ACR
    AzureCLI --> BlobStorage
    
    ACR --> ACRBackup
    
    StatsCollection --> GitHub
    StatsCollection --> DockerHub
    StatsCollection --> BlobStorage
    
    BlobStorage --> StatsLog
    
    KeyVault -.->|"Provides credentials"| AzureCLI
```

**Sources:** [.pipelines/clean-acr.yml:1-29](), [tools/misc/get-stats:1-57]()

## ACR Image Backup and Cleanup

### Purpose

The ACR cleanup system addresses the cost accumulation from storing Docker images in Azure Container Registry. Over time, the registry accumulates multiple versions of container images from CI/CD builds. The cleanup system:

- Exports all ACR images to cheaper Azure Blob Storage as `.tar` archives
- Deletes images from ACR after successful backup
- Prevents data loss through verification before deletion
- Runs weekly to maintain cost efficiency

### Pipeline Configuration

The cleanup pipeline is defined in [.pipelines/clean-acr.yml:1-29]() and runs on a weekly schedule:

| Configuration | Value |
|--------------|-------|
| **Schedule** | `0 1 * * 0` (Sunday 1:00 AM UTC) |
| **Trigger Mode** | `always: true` |
| **Branch** | `master` |
| **VM Image** | `ubuntu-latest` |
| **Azure Subscription** | `SynapseML Build` |
| **Service Connection** | `synapseml-clean-acr` |

**Sources:** [.pipelines/clean-acr.yml:2-20]()

### ACR Cleanup Workflow

```mermaid
graph TB
    Pipeline["Azure DevOps Pipeline<br/>clean-acr.yml"]
    AzureCLI["AzureCLI@2 Task"]
    InstallDeps["Install Dependencies<br/>azure-storage-blob<br/>azure-identity<br/>azure-keyvault-secrets"]
    
    Script["Python Script<br/>tools/acr/clean-acr.py"]
    
    subgraph "Script Execution Flow"
        GetSecret["Get Connection String<br/>from Key Vault"]
        ListRepos["List ACR Repositories<br/>az acr repository list"]
        
        LoopRepos["For Each Repository"]
        ListTags["List Tags<br/>az acr repository show-tags"]
        
        LoopTags["For Each Tag"]
        CheckBackup["Check if Backup Exists<br/>BlobClient.exists()"]
        
        ExportImage["Export to Blob<br/>az acr pipeline-run create"]
        VerifyBackup["Verify Backup Exists"]
        DeleteImage["Delete from ACR<br/>az acr repository delete"]
    end
    
    Pipeline --> AzureCLI
    AzureCLI --> InstallDeps
    InstallDeps --> Script
    
    Script --> GetSecret
    GetSecret --> ListRepos
    ListRepos --> LoopRepos
    LoopRepos --> ListTags
    ListTags --> LoopTags
    
    LoopTags --> CheckBackup
    CheckBackup -->|"Not exists"| ExportImage
    CheckBackup -->|"Exists"| LoopTags
    
    ExportImage --> VerifyBackup
    VerifyBackup --> DeleteImage
    DeleteImage --> LoopTags
```

**Sources:** [.pipelines/clean-acr.yml:16-28](), [tools/acr/clean-acr.py:1-87]()

### Implementation Details

The cleanup script `tools/acr/clean-acr.py` implements the following logic:

#### Configuration Variables

```python
acr = "mmlsparkmcr"
container = "acrbackup"
rg = "marhamil-mmlspark"
pipeline = "mmlsparkacrexport3"
```

**Sources:** [tools/acr/clean-acr.py:25-28]()

#### Key Vault Integration

The script retrieves the storage connection string from Azure Key Vault:

```python
keyvaultName = sys.argv[1]  # "mmlspark-keys"
secretName = sys.argv[2]    # "clean-acr-connection-string"
kvUri = f"https://{keyvaultName}.vault.azure.net"
kvClient = SecretClient(vault_url=kvUri, credential=DefaultAzureCredential())
conn_string = kvClient.get_secret(secretName).value
```

**Sources:** [tools/acr/clean-acr.py:30-34]()

#### Backup and Deletion Process

The script processes each repository and tag:

1. **List repositories:** Uses `az acr repository list -n {acr}` to enumerate all repositories
2. **List tags:** Uses `az acr repository show-tags` with `--orderby time_desc` to get tags
3. **Check backup:** Constructs blob name as `{repo}/{tag}.tar` and verifies existence
4. **Export image:** If backup doesn't exist, creates ACR pipeline-run to export
5. **Verify backup:** Confirms blob exists after export
6. **Delete image:** Removes image from ACR using `az acr repository delete`

**Sources:** [tools/acr/clean-acr.py:53-87]()

#### Retry Mechanism

The script includes a custom retry function for Azure CLI commands:

| Parameter | Behavior |
|-----------|----------|
| **Initial Delay** | 5 seconds |
| **Delay Multiplier** | 3x after each failure |
| **Max Attempts** | 5 |
| **Command Output** | Printed to console |

The retry function is defined at [tools/acr/clean-acr.py:37-48]() and used for both export and delete operations.

**Sources:** [tools/acr/clean-acr.py:37-48](), [tools/acr/clean-acr.py:73](), [tools/acr/clean-acr.py:85]()

## Statistics Collection

### Purpose

The statistics collection system tracks project health metrics over time by periodically querying public APIs and storing results in Azure Blob Storage. This provides historical data for:

- Community engagement tracking (stars, forks, watchers)
- Contribution metrics (contributors, pull requests, issues)
- Distribution usage (Docker pulls, tags)

### Collected Metrics

The system collects the following metrics:

#### GitHub Metrics

| Metric | API Endpoint | Description |
|--------|-------------|-------------|
| **Stars** | `/repos/Microsoft/SynapseML` | Repository star count |
| **Watchers** | `/repos/Microsoft/SynapseML` | Subscriber count |
| **Forks** | `/repos/Microsoft/SynapseML` | Fork count |
| **Open Issues/PRs** | `/repos/Microsoft/SynapseML` | Combined open count |
| **Contributors** | `/repos/Microsoft/SynapseML/contributors` | List of contributor logins |
| **Pull Requests** | `/repos/Microsoft/SynapseML/pulls` | Open PR numbers |
| **Issues** | `/repos/Microsoft/SynapseML/issues` | Open issue numbers (excluding PRs) |

**Sources:** [tools/misc/get-stats:34-43]()

#### Docker Hub Metrics

| Metric | API Endpoint | Description |
|--------|-------------|-------------|
| **Pulls** | `/v2/repositories/microsoft/mmlspark/` | Total image pull count |
| **Stars** | `/v2/repositories/microsoft/mmlspark/` | Repository star count |
| **Tags** | `/v2/repositories/microsoft/mmlspark/tags/` | List of available tags |

**Sources:** [tools/misc/get-stats:45-47]()

### Statistics Collection Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        GitHubAPI["GitHub API<br/>api.github.com"]
        DockerAPI["Docker Hub API<br/>hub.docker.com/v2"]
    end
    
    subgraph "Collection Scripts"
        BashScript["Bash Script<br/>tools/misc/get-stats"]
        JSScript["JavaScript Script<br/>tools/misc/get-stats.js"]
    end
    
    subgraph "API Client Utilities"
        jget["jget function<br/>curl + jq"]
        jget_paged["jget_paged function<br/>Paginated queries"]
        httpsGet["https.get<br/>Node.js"]
        ghAPI["github module<br/>Node.js"]
    end
    
    subgraph "Storage"
        TempFile["Temporary File<br/>/tmp/get-stats-$$"]
        BlobUpload["Azure Blob Upload<br/>az storage blob upload"]
        StatsBlob["Blob: stats/log<br/>Append-only log"]
    end
    
    BashScript --> jget
    BashScript --> jget_paged
    JSScript --> httpsGet
    JSScript --> ghAPI
    
    jget --> GitHubAPI
    jget_paged --> GitHubAPI
    httpsGet --> DockerAPI
    ghAPI --> GitHubAPI
    
    BashScript --> TempFile
    TempFile --> BlobUpload
    BlobUpload --> StatsBlob
    
    JSScript --> StatsBlob
```

**Sources:** [tools/misc/get-stats:1-57](), [tools/misc/get-stats.js:1-64]()

### Bash Implementation

The bash script at [tools/misc/get-stats:1-57]() provides a lightweight implementation:

#### Helper Functions

The script defines two utility functions for API queries:

**`jget`** - Simple JSON query:
```bash
jget() { local url="$1"; shift; curl -s "$url" | jq -r "$@"; }
```

**`jget_paged`** - Paginated query handling:
- Follows `Link` headers for pagination
- Continues until no `next` relation found
- Aggregates results with `jq -sr "add"`

**Sources:** [tools/misc/get-stats:10-22]()

#### Data Collection Process

The script collects data in a structured format:

1. **Timestamp:** UTC timestamp in `YYYY-MM-DD HH:MM` format
2. **GitHub section:** Repository stats, contributors list, PRs list, issues list
3. **Docker section:** Pull count, star count, tags list

Output format example:
```
=========================
2024-01-15 03:00
github:
  stars: 5000
  watchers: 150
  forks: 800
  issues_pulls: 25
  contributors: 120 => user1, user2, ...
  pulls: 10 => #123, #124, ...
  issues: 15 => #100, #101, ...
docker:
  pulls: 100000
  stars: 50
  tags: 15 => latest, v1.0.0, ...
```

**Sources:** [tools/misc/get-stats:26-48]()

#### Storage Upload

The script uploads results using Azure CLI:
- **Upload type:** `--type append` for append-only log
- **Account:** `mmlspark`
- **Container:** `stats`
- **Blob name:** `log`

**Sources:** [tools/misc/get-stats:51-54]()

### JavaScript Implementation

The JavaScript implementation at [tools/misc/get-stats.js:1-64]() provides similar functionality with the `github` npm module:

#### Module Configuration

```javascript
let az = require("azure-storage");
let ghAPI = require("github");
let repo = {owner: "Azure", repo: "mmlspark"};
let repo_pg = Object.assign({}, repo, {per_page: 100});
```

**Sources:** [tools/misc/get-stats.js:4-17]()

#### Pagination Handling

The script implements recursive pagination:

```javascript
let getPaged = (state, combine) => r =>
  !gh.hasNextPage(r) ? Promise.resolve(combine(state, r.data))
  : gh.getNextPage(r).then(getPaged(combine(state, r.data), combine));
```

**Sources:** [tools/misc/get-stats.js:25-27]()

#### Data Aggregation

The script uses `Promise.all` to collect all metrics concurrently:

1. Repository metadata via `gh.repos.get()`
2. Issues and PRs via `gh.issues.getForRepo()` with filtering
3. Contributors via `gh.repos.getContributors()`
4. Docker stats via HTTPS API calls

**Sources:** [tools/misc/get-stats.js:54-61]()

## Resource Management Integration

Both resource management systems integrate with the development infrastructure:

| System | Trigger | Frequency | Storage | Dependencies |
|--------|---------|-----------|---------|--------------|
| **ACR Cleanup** | Azure DevOps cron | Weekly (Sunday 1 AM) | Blob: acrbackup | Azure CLI, Python, Key Vault |
| **Statistics** | Custom scheduler | Configurable | Blob: stats/log | Bash/Node.js, jq, Azure CLI |

These systems operate independently and require:
- Azure service connection with appropriate permissions
- Key Vault access for secrets
- Blob storage write permissions
- API access to external services (GitHub, Docker Hub)

**Sources:** [.pipelines/clean-acr.yml:2-8](), [tools/misc/get-stats:51-54](), [tools/misc/get-stats.js:60-61]()

---

# Page: Testing Infrastructure

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



## Purpose and Scope

This document describes the comprehensive testing infrastructure used in the SynapseML project, including unit tests, component fuzzing, and end-to-end testing orchestration. For details on platform-specific E2E testing, see [Synapse E2E Testing](#4.2) and [Databricks E2E Testing](#4.3). For information on the CI/CD pipeline orchestration, see [CI/CD Pipeline](#3.1).

The testing infrastructure ensures code quality through multiple layers of validation: unit tests across three language bindings (Scala, Python, R), automated fuzzing of all ML components, and integration tests on actual cloud platforms.

## Testing Strategy Overview

SynapseML employs a multi-layered testing strategy designed to validate functionality at different scales and across multiple execution environments. The strategy balances comprehensive coverage with efficient execution through parallelization and selective test execution.

### Test Type Matrix

The testing infrastructure organizes tests into distinct categories, each serving a specific validation purpose:

| Test Type | Languages | Execution Environment | Purpose |
|-----------|-----------|----------------------|---------|
| Unit Tests | Scala, Python, R | Local Spark | Validate individual components |
| Fuzzing Tests | Scala | Local Spark | Auto-test all PipelineStages |
| Notebook Tests | Python | Local Spark | Validate documentation examples |
| E2E Tests | Python | Synapse, Databricks | Integration testing on cloud platforms |
| Style Tests | Scala, Python | Build Agent | Code quality enforcement |

Sources: [pipeline.yaml:59-772]()

## Unit Testing Infrastructure

### Parallel Test Execution

Unit tests execute in parallel across multiple job matrices to minimize total runtime. The pipeline defines separate job matrices for Scala unit tests (30+ packages), Python tests (7 packages), and R tests (6 packages).

```mermaid
graph TB
    subgraph "Unit Test Orchestration"
        Pipeline["Azure DevOps Pipeline"]
        
        subgraph "Scala Tests"
            ScalaJob["UnitTests Job"]
            ScalaMatrix["Matrix: 30+ packages"]
            ScalaExec["sbt coverage testOnly"]
        end
        
        subgraph "Python Tests"
            PythonJob["PythonTests Job"]
            PythonMatrix["Matrix: 7 packages"]
            PythonExec["sbt testPython"]
        end
        
        subgraph "R Tests"
            RJob["RTests Job"]
            RMatrix["Matrix: 6 packages"]
            RExec["sbt testR"]
        end
        
        subgraph "Quality Gates"
            Coverage["Code Coverage"]
            Codecov["Codecov Upload"]
            TestResults["PublishTestResults"]
        end
    end
    
    Pipeline --> ScalaJob
    Pipeline --> PythonJob
    Pipeline --> RJob
    
    ScalaJob --> ScalaMatrix
    ScalaMatrix --> ScalaExec
    
    PythonJob --> PythonMatrix
    PythonMatrix --> PythonExec
    
    RJob --> RMatrix
    RMatrix --> RExec
    
    ScalaExec --> Coverage
    PythonExec --> Coverage
    RExec --> Coverage
    
    Coverage --> Codecov
    ScalaExec --> TestResults
    PythonExec --> TestResults
    RExec --> TestResults
```

Sources: [pipeline.yaml:357-518](), [pipeline.yaml:614-772]()

### Scala Unit Tests

Scala unit tests execute through the `sbt` build system using ScalaTest framework. Tests are organized by module package and execute with code coverage enabled via `scoverage`. The pipeline defines 30+ test packages in a matrix strategy.

**Key Test Packages:**
- `core`, `automl`, `causal`, `onnx` - Core functionality
- `services.openai`, `services.aifoundry`, `services.language` - AI service integrations
- `lightgbm.split1` through `lightgbm.split6` - LightGBM module (split due to size)
- `explainers.split1` through `explainers.split3` - Model explainability

Tests marked with `FLAKY: "true"` automatically retry once on failure to handle non-deterministic test behavior.

Sources: [pipeline.yaml:614-772](), [build.sbt:250-264]()

### Python Unit Tests

Python tests execute through `sbt testPython`, which invokes `pytest` on the generated Python bindings. The test infrastructure supports sub-path filtering to enable targeted test execution and parallel execution across modules.

**Test Configuration:**
- Uses `publishM2` to make JARs available to PySpark
- Supports `pythonSubTestPath` and `pythonIgnoreTestPath` flags for selective execution
- Automatic retry (up to 3 attempts) on failure
- Timeout: 40 minutes per package

The pipeline splits deep learning tests into Hugging Face (`hf`) and non-Hugging Face (`nohf`) subsets to manage execution time.

Sources: [pipeline.yaml:357-443](), [build.sbt:250-264]()

### R Unit Tests

R tests validate the auto-generated R wrapper functionality using the `testthat` framework. Tests execute through `sbt testR` after downloading a specific Spark distribution.

**R Test Execution:**
1. Download Spark 3.5.0 with Hadoop 3
2. Publish artifacts to local M2 repository
3. Execute R tests via `sbt testR`
4. Generate coverage report

Sources: [pipeline.yaml:446-518]()

## Component Fuzzing Framework

The fuzzing framework automatically discovers and tests all `PipelineStage` implementations in the codebase, ensuring comprehensive validation of serialization, fitting, and language binding generation.

### Fuzzing Architecture

```mermaid
graph TB
    subgraph "Auto-Discovery System"
        JarLoader["JarLoadingUtils"]
        ServiceLoader["Java ServiceLoader"]
        PipelineStages["instantiateServices<PipelineStage>"]
    end
    
    subgraph "Fuzzer Types"
        SerializationFuzzing["SerializationFuzzing"]
        ExperimentFuzzing["ExperimentFuzzing"]
        PyTestFuzzing["PyTestFuzzing"]
        RTestFuzzing["RTestFuzzing"]
    end
    
    subgraph "Validation Tests"
        SerializationTest["Serialization Test:<br/>MLWritable stages"]
        FitTransformTest["Fit/Transform Test:<br/>Estimators & Transformers"]
        PythonTest["Python Binding Test:<br/>Generated wrappers"]
        RTest["R Binding Test:<br/>Generated wrappers"]
    end
    
    subgraph "Test Execution"
        FuzzingTest["FuzzingTest.scala"]
        Exemptions["Exemption Lists"]
        ClassMapping["Class to Fuzzer Mapping"]
    end
    
    JarLoader --> ServiceLoader
    ServiceLoader --> PipelineStages
    PipelineStages --> SerializationFuzzing
    PipelineStages --> ExperimentFuzzing
    PipelineStages --> PyTestFuzzing
    PipelineStages --> RTestFuzzing
    
    SerializationFuzzing --> SerializationTest
    ExperimentFuzzing --> FitTransformTest
    PyTestFuzzing --> PythonTest
    RTestFuzzing --> RTest
    
    FuzzingTest --> ClassMapping
    FuzzingTest --> Exemptions
    ClassMapping --> SerializationTest
    ClassMapping --> FitTransformTest
    ClassMapping --> PythonTest
    ClassMapping --> RTest
```

Sources: [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:1-438]()

### Fuzzing Test Types

The fuzzing framework validates four critical aspects of each `PipelineStage`:

**1. Serialization Testing**

Verifies that all stages implementing `MLWritable` can be saved and loaded correctly. The test discovers all applicable stages and ensures each has a corresponding `SerializationFuzzing` implementation.

```scala
test("Verify all stages can be serialized") {
  val exemptions: Set[String] = Set(/* ... */)
  val applicableStages = pipelineStages.filter(t => !exemptions(t.getClass.getName))
  // Verify each stage has a SerializationFuzzing implementation
}
```

**2. Fit/Transform Testing**

Validates that `Estimator` and `Transformer` stages can be successfully fitted and transformed. Each stage must have an `ExperimentFuzzing` implementation that provides test data and validates output.

**3. Python Binding Testing**

Ensures auto-generated Python wrappers correctly expose Scala functionality. Uses `PyTestFuzzing` implementations to validate parameter passing and return values.

**4. R Binding Testing**

Validates auto-generated R wrapper functionality through `RTestFuzzing` implementations.

Sources: [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:98-273]()

### Auto-Discovery Mechanism

The fuzzing framework uses `JarLoadingUtils.instantiateServices[T]()` to dynamically discover all implementations of a given trait or class at runtime. This ensures new components are automatically tested without manual registration.

**Discovery Process:**
1. Scan classpath for implementations of `PipelineStage`
2. Instantiate each discovered class
3. Match against fuzzing implementations
4. Report classes without fuzzers as test failures

Sources: [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:422-437]()

## Notebook and Website Testing

The testing infrastructure converts Jupyter notebooks into executable Python scripts and validates that all code blocks execute successfully. This ensures documentation examples remain functional.

### Notebook Conversion Pipeline

```mermaid
graph LR
    subgraph "Notebook Processing"
        DocsDir["docs/ Directory"]
        NotebooksDir["generated-notebooks/"]
        Conversion["nbconvert to Python"]
        Preamble["Insert Preamble"]
    end
    
    subgraph "Test Execution"
        WebsiteTests["WebsiteSamplesTests"]
        PytestCodeblocks["pytest-codeblocks"]
        TestResults["XML Test Results"]
    end
    
    DocsDir --> NotebooksDir
    NotebooksDir --> Conversion
    Conversion --> Preamble
    Preamble --> WebsiteTests
    WebsiteTests --> PytestCodeblocks
    PytestCodeblocks --> TestResults
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala:82-122](), [pipeline.yaml:528-564]()

### Notebook Test Process

**Conversion Steps:**

1. **Collection**: Recursively find all `.ipynb` files in the `docs/` directory
2. **Normalization**: Copy to `generated-notebooks/` with sanitized names (remove spaces, special chars)
3. **Conversion**: Use `jupyter nbconvert --to python` to convert to `.py` files
4. **Preamble Injection**: Insert test environment setup code at line 2

The preamble ensures magic commands like `%pip install` work in Synapse scheduled jobs by setting up the IPython environment.

**Test Execution:**

The `WebsiteSamplesTests` job executes converted notebooks using `sbt testWebsiteDocs`, which calls `pytest-codeblocks` to validate code blocks. Tests timeout after 30 minutes.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala:22-42](), [build.sbt:361-367]()

## Test Environment Management

### Conda Environment Setup

The testing infrastructure uses a shared Conda environment defined in `environment.yml` with caching to minimize setup time. The environment includes all dependencies needed for testing across Scala, Python, and R.

**Environment Cache Strategy:**

```mermaid
graph TB
    Pipeline["Pipeline Task"]
    CacheCheck{"Cache Hit?"}
    RestoreCache["Restore from Cache"]
    CreateEnv["conda env create"]
    CleanCache["conda clean --all"]
    DiskCleanup["Remove unused SDKs"]
    
    Pipeline --> DiskCleanup
    DiskCleanup --> CacheCheck
    CacheCheck -->|Yes| RestoreCache
    CacheCheck -->|No| CreateEnv
    CreateEnv --> CleanCache
    RestoreCache --> Pipeline
    CleanCache --> Pipeline
```

**Cache Key**: `conda | "$(Agent.OS)" | environment.yml`

The cache is restored before environment creation and includes a disk cleanup step that removes unused Android and Google Cloud SDKs to free space on the build agent.

Sources: [templates/conda.yml:1-42](), [environment.yml:1-58]()

### Key Dependencies

The test environment includes:
- **Python**: 3.11.8 with PySpark 3.5.0
- **R**: 4.1.1 with SparklyR 1.8.1
- **ML Libraries**: PyTorch 2.1.0, Horovod, transformers 4.49.0, LangChain 0.0.152
- **Testing**: pytest, pytest-cov, pytest-codeblocks
- **Code Quality**: black 22.3.0, coverage

Sources: [environment.yml:1-58]()

### Secret Management for Tests

Test secrets are retrieved from Azure Key Vault using the `Secrets` object in Scala or the `find_secret()` function in Python. The pipeline uses Azure CLI authentication to access secrets.

**Secret Retrieval Architecture:**

```mermaid
graph TB
    subgraph "Secret Sources"
        KeyVault["Azure Key Vault<br/>mmlspark-build-keys"]
        EnvVars["Environment Variables"]
        Cache["Local File Cache"]
    end
    
    subgraph "Secret Consumers"
        ScalaTests["Scala Tests"]
        PythonTests["Python Tests"]
        E2ETests["E2E Tests"]
    end
    
    subgraph "Retrieval Logic"
        AzureCLI["az keyvault secret show"]
        SecretsObject["Secrets.scala"]
        FindSecret["find_secret()"]
    end
    
    KeyVault --> AzureCLI
    AzureCLI --> SecretsObject
    AzureCLI --> FindSecret
    
    EnvVars --> SecretsObject
    Cache --> SecretsObject
    
    SecretsObject --> ScalaTests
    FindSecret --> PythonTests
    SecretsObject --> E2ETests
    FindSecret --> E2ETests
```

**Common Secrets:**
- `cognitive-api-key` - Azure AI Services authentication
- `openai-api-key-2` - Azure OpenAI authentication  
- `azure-search-key` - Azure Cognitive Search
- `adb-token` - Databricks workspace token
- `nexus-un`, `nexus-pw` - Maven Central publishing
- `pgp-private`, `pgp-public`, `pgp-pw` - JAR signing

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala:12-79](), [templates/kv.yml:1-7]()

### Test Dataset Management

Test datasets are downloaded and cached locally using the `getDatasetsTask` SBT task. The task downloads a compressed archive from Azure Blob Storage and extracts it to a local directory.

**Dataset Location**: `target/datasets/datasets-2023-04-03/`

The dataset directory is exposed to tests via the `datasetDir` BuildInfo key, making it accessible in test code as `BuildInfo.datasetDir`.

Sources: [build.sbt:72-89]()

## Code Coverage and Quality Reporting

### Coverage Collection

Code coverage is collected using `scoverage` for Scala code. The `coverage` SBT setting enables instrumentation during test execution, and `coverageReport` generates the final report.

**Coverage Workflow:**

1. Execute tests with `sbt coverage testOnly`
2. Generate report with `sbt coverageReport`
3. Upload to Codecov using `codecov` CLI
4. Display summary in Azure DevOps

The pipeline retries the Codecov upload task once on failure to handle transient network issues.

Sources: [pipeline.yaml:434-442](), [templates/codecov.yml:1-12]()

### Test Result Publishing

All test jobs publish results using the `PublishTestResults@2` Azure DevOps task. This provides:
- Test result visualization in the pipeline UI
- Failure trend analysis
- Test duration tracking
- Flaky test detection

**Test Result Patterns:**
- Scala: `**/test-reports/TEST-*.xml`
- Python: `**/python-test-*.xml`
- R: `**/r-test-*.xml`
- Website: `**/website-test-result.xml`

Sources: [pipeline.yaml:176-181](), [pipeline.yaml:428-433](), [pipeline.yaml:503-508]()

## Retry Mechanisms and Reliability

### Automatic Retry Configuration

The testing infrastructure implements retry mechanisms at multiple levels to handle transient failures:

**Task-Level Retries:**
- Most Azure CLI tasks: `retryCountOnTaskFailure: 1`
- Critical setup tasks: `retryCountOnTaskFailure: 3`
- Conda environment creation: Retry on failure with 30-minute timeout

**Test-Level Retries:**
- Python tests: Up to 3 retry attempts via `sbt` command chaining
- R tests: `retryCountOnTaskFailure: 3`
- Flaky tests: Single automatic retry when `FLAKY: "true"`

Sources: [pipeline.yaml:399-427](), [pipeline.yaml:491-502]()

### Flaky Test Handling

Tests marked as flaky in the pipeline matrix execute with automatic retry logic. The test command runs twice on first failure before reporting actual failure.

**Flaky Test Execution:**

```bash
(timeout 30m sbt coverage "testOnly com.microsoft.azure.synapse.ml.$(PACKAGE).**") ||
(${FLAKY:-false} && timeout 30m sbt coverage "testOnly com.microsoft.azure.synapse.ml.$(PACKAGE).**")
```

**Flaky Packages:**
- All Azure AI Services packages (`services.openai`, `services.language`, etc.)
- LightGBM splits 1-6
- IO operations (`io.split1`, `io.split2`)

Sources: [pipeline.yaml:754-755]()

### Timeout Configuration

Test jobs have configured timeouts to prevent indefinite hanging:

| Job Type | Timeout | Cancel Timeout |
|----------|---------|----------------|
| Unit Tests | 80 minutes | 1 minute |
| Python Tests | 120 minutes | 0 minutes |
| R Tests | 60 minutes | 0 minutes |
| E2E Tests | 120 minutes | 0 minutes |
| Website Tests | 30 minutes (task) | 0 minutes |

Sources: [pipeline.yaml:358-360](), [pipeline.yaml:447-449](), [pipeline.yaml:616-618]()

## Parallel Test Execution Strategy

The pipeline maximizes test throughput by executing independent test suites in parallel. The Azure DevOps strategy matrix creates multiple concurrent jobs for each test category.

**Concurrency Model:**

```mermaid
graph TB
    subgraph "Parallel Execution"
        Trigger["Pipeline Trigger"]
        
        subgraph "Independent Jobs"
            Style["Style Check"]
            Publish["Build & Publish"]
            Website["Website Deployment"]
        end
        
        subgraph "Unit Test Matrix"
            UT1["Unit Test: core"]
            UT2["Unit Test: openai"]
            UT3["Unit Test: lightgbm.split1"]
            UTN["... 30+ packages"]
        end
        
        subgraph "Python Test Matrix"
            PT1["Python: core"]
            PT2["Python: deepLearning hf"]
            PT3["Python: cognitive"]
            PTN["... 7 packages"]
        end
        
        subgraph "R Test Matrix"
            RT1["R: core"]
            RT2["R: lightgbm"]
            RTN["... 6 packages"]
        end
    end
    
    Trigger --> Style
    Trigger --> Publish
    Trigger --> Website
    
    Trigger --> UT1
    Trigger --> UT2
    Trigger --> UT3
    Trigger --> UTN
    
    Trigger --> PT1
    Trigger --> PT2
    Trigger --> PT3
    Trigger --> PTN
    
    Trigger --> RT1
    Trigger --> RT2
    Trigger --> RTN
```

The pipeline does not define explicit dependencies between these job families, allowing Azure DevOps to schedule them concurrently based on agent availability.

Sources: [pipeline.yaml:59-772]()

---

# Page: Testing Strategy

# Testing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



## Purpose and Scope

This document describes the overall testing strategy for SynapseML, including test categorization, execution orchestration, environment management, and quality gates. It covers the multi-layered testing approach that ensures code quality across Scala, Python, and R implementations on multiple target platforms.

For details on Synapse-specific E2E testing, see [Synapse E2E Testing](#4.2). For Databricks-specific E2E testing, see [Databricks E2E Testing](#4.3). For the automated fuzzing framework, see [Component Fuzzing](#4.4).

## Overview

SynapseML implements a comprehensive multi-layered testing strategy orchestrated through Azure DevOps pipelines. The testing approach includes:

- **Unit tests** for 30+ Scala packages, 7 Python packages, and 6 R packages
- **End-to-end (E2E) tests** on Synapse and Databricks environments
- **Documentation tests** that validate code blocks in website documentation
- **Style checks** for code quality across all languages
- **Fuzzing tests** for serialization and language binding validation
- **Code coverage tracking** integrated with Codecov.io

The strategy emphasizes reliability through automated retry mechanisms, flaky test isolation, and parallel execution across multiple test matrices.

Sources: [pipeline.yaml:1-773](), [build.sbt:1-368]()

## Test Categorization

### Test Job Architecture

```mermaid
graph TB
    subgraph "Pipeline Jobs"
        Style["Style Job<br/>Scala/Python Checks"]
        UnitTests["UnitTests Job<br/>30+ Package Matrix"]
        PythonTests["PythonTests Job<br/>7 Package Matrix"]
        RTests["RTests Job<br/>6 Package Matrix"]
        E2E["E2E Job<br/>Platform Matrix"]
        WebsiteTests["WebsiteSamplesTests Job<br/>Doc Validation"]
        Publish["Publish Job<br/>Artifact Generation"]
    end
    
    subgraph "Test Execution Flow"
        Setup["Setup Phase<br/>conda, datasets, secrets"]
        Execute["Execute Phase<br/>sbt/pytest/timeout"]
        Report["Report Phase<br/>PublishTestResults"]
        Coverage["Coverage Phase<br/>coverageReport, codecov"]
    end
    
    Style --> Setup
    UnitTests --> Setup
    PythonTests --> Setup
    RTests --> Setup
    E2E --> Setup
    WebsiteTests --> Setup
    
    Setup --> Execute
    Execute --> Report
    Report --> Coverage
    
    Publish -.->|"parallel"| Style
    Publish -.->|"parallel"| UnitTests
    
    style Setup fill:#f9f9f9
    style Execute fill:#f9f9f9
    style Report fill:#f9f9f9
    style Coverage fill:#f9f9f9
```

Sources: [pipeline.yaml:65-773]()

### Unit Test Matrix

The `UnitTests` job executes Scala tests across 30+ package configurations using a matrix strategy. Each package runs in an isolated job with dedicated timeout and retry settings.

| Package Category | Package Name | Flaky Flag | Special Requirements |
|-----------------|--------------|------------|---------------------|
| Core | `core`, `automl`, `causal`, `onnx` | No | Standard setup |
| Services | `services.openai`, `services.vision`, `services.speech` | Yes | Retry enabled |
| ML Algorithms | `lightgbm.split1-6`, `vw`, `isolationforest` | Yes (LGBM) | Split for speed |
| Media | `opencv`, `image` | No | - |
| Data I/O | `io.split1-2` | Yes | Azure storage access |
| Explainability | `explainers.split1-3` | No | Split for speed |
| Audio/Video | `services.search.split1-2`, `services.speech` | Yes | FFmpeg required |

Sources: [pipeline.yaml:614-727]()

### Python Test Matrix

Python tests execute across 7 package-level configurations, with sub-path filtering for deep learning tests:

```mermaid
graph LR
    subgraph "PythonTests Matrix"
        Core["core"]
        DL_HF["deepLearning/hf"]
        DL_NoHF["deepLearning/no-hf"]
        LightGBM["lightgbm"]
        OpenCV["opencv"]
        VW["vw"]
        Cognitive["cognitive"]
    end
    
    subgraph "Test Execution"
        InstallDeps["installPipPackage<br/>publishM2"]
        RunTests["sbt testPython<br/>with flags"]
        Results["python-test-*.xml"]
    end
    
    Core --> InstallDeps
    DL_HF --> InstallDeps
    DL_NoHF --> InstallDeps
    LightGBM --> InstallDeps
    OpenCV --> InstallDeps
    VW --> InstallDeps
    Cognitive --> InstallDeps
    
    InstallDeps --> RunTests
    RunTests --> Results
```

Sources: [pipeline.yaml:357-444]()

**Python Test Configuration:**

- **Test path filtering**: Uses `-DpythonSubTestPath` and `-DpythonIgnoreTestPath` flags [pipeline.yaml:414-424]()
- **Retry mechanism**: Triple retry with explicit command repetition [pipeline.yaml:425-427]()
- **Deep learning split**: Separates Hugging Face tests from other DL tests to reduce runtime [pipeline.yaml:368-374]()

### R Test Matrix

R tests execute across 6 packages with Spark environment setup:

```scala
strategy:
  matrix:
    core:        PACKAGE: "core"
    deep-learning: PACKAGE: "deepLearning"
    lightgbm:    PACKAGE: "lightgbm"
    opencv:      PACKAGE: "opencv"
    vw:          PACKAGE: "vw"
    cognitive:   PACKAGE: "cognitive"
```

Sources: [pipeline.yaml:446-518]()

### E2E Test Matrix

End-to-end tests validate notebook execution on actual cloud platforms:

```mermaid
graph TB
    subgraph "E2E Test Targets"
        DB_CPU["databricks-cpu<br/>DatabricksCPUTests"]
        DB_GPU["databricks-gpu<br/>DatabricksGPUTests"]
        DB_RAPIDS["databricks-rapids<br/>DatabricksRapidsTests<br/>(disabled)"]
        Synapse["synapse<br/>SynapseTests<br/>(disabled)"]
        SynInternal["synapse-internal<br/>SynapseExtensionsTests<br/>(conditional)"]
    end
    
    subgraph "Test Execution"
        PublishArtifacts["Publish Artifacts<br/>to Blob Storage"]
        RunE2E["sbt testOnly<br/>TEST-CLASS"]
        PublishResults["PublishTestResults"]
    end
    
    DB_CPU --> PublishArtifacts
    DB_GPU --> PublishArtifacts
    
    PublishArtifacts --> RunE2E
    RunE2E --> PublishResults
```

Sources: [pipeline.yaml:138-182]()

## Test Execution Strategy

### Retry Mechanisms

SynapseML implements multiple retry strategies to handle transient failures:

**1. Task-level retries:**
```yaml
retryCountOnTaskFailure: 1  # Azure CLI tasks
retryCountOnTaskFailure: 3  # R tests, critical setup
```

**2. Command-level retries:**
```bash
# Triple retry with explicit command repetition
(sbt testPython) || (sbt testPython) || (sbt testPython)
```

**3. Flaky test isolation:**
```bash
# Unit tests with flaky flag
(timeout 30m sbt coverage "testOnly ...") ||
(${FLAKY:-false} && timeout 30m sbt coverage "testOnly ...")
```

Sources: [pipeline.yaml:401-402](), [pipeline.yaml:754-755]()

### Flaky Test Handling

Tests marked with `FLAKY: "true"` in the matrix receive special treatment:

```yaml
openai:
  PACKAGE: "services.openai"
  FLAKY: "true"  # Retry on failure
```

When a flaky test fails, the conditional `${FLAKY:-false}` allows one retry attempt. This prevents legitimate transient failures (network issues, rate limits) from blocking the pipeline while still catching real regressions.

Sources: [pipeline.yaml:645-671]()

### Timeout Configuration

| Test Type | Timeout | Cancel Timeout | Rationale |
|-----------|---------|----------------|-----------|
| Unit Tests | 80 minutes | 1 minute | Long-running ML tests |
| Python Tests | 120 minutes | 0 (disabled) | Includes model training |
| R Tests | 60 minutes | 0 (disabled) | R environment setup overhead |
| E2E Tests | 120 minutes | 0 (disabled) | Cluster provisioning time |
| Website Tests | 30 minutes | 0 (disabled) | Lightweight doc validation |

Sources: [pipeline.yaml:358-359](), [pipeline.yaml:447-448](), [pipeline.yaml:616-617]()

### Parallel Execution Strategy

```mermaid
graph TB
    subgraph "Pipeline Stages"
        Stage1["Stage 1: Independent Jobs<br/>Style, Publish, BuildAndCacheCondaEnv"]
        Stage2["Stage 2: Parallel Test Matrices<br/>UnitTests, PythonTests, RTests, E2E"]
        Stage3["Stage 3: Deployment<br/>WebsiteAutoDeployment, Release"]
    end
    
    subgraph "Matrix Parallelization"
        UT["UnitTests<br/>30+ parallel jobs"]
        PT["PythonTests<br/>7 parallel jobs"]
        RT["RTests<br/>6 parallel jobs"]
        E2E_P["E2E<br/>2-4 parallel jobs"]
    end
    
    Stage1 --> Stage2
    Stage2 --> UT
    Stage2 --> PT
    Stage2 --> RT
    Stage2 --> E2E_P
    UT --> Stage3
    PT --> Stage3
    RT --> Stage3
    E2E_P --> Stage3
```

The pipeline exploits Azure DevOps matrix strategies to parallelize test execution. Each matrix job runs independently on a separate VM, maximizing throughput while maintaining isolation.

Sources: [pipeline.yaml:143-158](), [pipeline.yaml:363-382](), [pipeline.yaml:620-726]()

## Environment Management

### Conda Environment Setup

SynapseML uses a cached Conda environment to speed up test execution. The caching strategy reduces environment creation time from ~30 minutes to seconds on cache hits.

**Conda Template Workflow:**

```mermaid
graph LR
    PrependPath["Prepend conda to PATH"]
    FixPerms["Fix directory permissions<br/>chown CONDA_CACHE_DIR"]
    CheckCache["Cache@2 task<br/>key: conda + OS + environment.yml"]
    
    CacheHit{{"Cache Hit?"}}
    CreateEnv["Create conda env<br/>timeout 30m with retry"]
    CleanUp["conda clean --all<br/>pip cache purge"]
    
    PrependPath --> FixPerms
    FixPerms --> CheckCache
    CheckCache --> CacheHit
    CacheHit -->|"Yes"| Done["Use cached env"]
    CacheHit -->|"No"| CreateEnv
    CreateEnv --> CleanUp
    CleanUp --> Done
```

Sources: [templates/conda.yml:1-42]()

**Environment Definition:**

The `environment.yml` file defines dependencies for all test types:

- **Python base**: 3.11.8 with PySpark 3.5.0
- **R support**: r-base 4.1.1, r-sparklyr 1.8.1
- **Test frameworks**: pytest, pytest-cov, pytest-codeblocks
- **ML libraries**: torch 2.1.0, transformers 4.49.0, horovod (from git)
- **Documentation**: sphinx 5.0.2, nbconvert, jupyter

Sources: [environment.yml:1-58]()

### Test Dataset Management

The `getDatasetsTask` ensures test datasets are available before test execution:

```scala
val getDatasetsTask = TaskKey[Unit]("getDatasets", "download datasets used for testing")
val datasetName = "datasets-2023-04-03.tgz"
val datasetUrl = new URI(s"https://mmlspark.blob.core.windows.net/installers/$datasetName").toURL

getDatasetsTask := {
  val d = datasetDir.value.getParentFile
  val f = new File(d, datasetName)
  if (!d.exists()) d.mkdirs()
  if (!f.exists()) {
    FileUtils.copyURLToFile(datasetUrl, f)
    UnzipUtils.unzip(f, d)
  }
}
```

The `setup` task depends on `getDatasetsTask`, ensuring datasets are downloaded during test preparation. Datasets are versioned and cached locally to avoid repeated downloads.

Sources: [build.sbt:72-89](), [build.sbt:346-353]()

### Secret Management for Tests

Tests requiring Azure service credentials use the Key Vault template to retrieve secrets:

```yaml
# templates/kv.yml
- task: AzureKeyVault@2
  retryCountOnTaskFailure: 3
  inputs:
    azureSubscription: 'SynapseML Build'
    keyVaultName: mmlspark-keys
```

The `Secrets.scala` implementation provides environment variable fallback:

```scala
private def findAndCacheSecret(env_var: String, name: String, suffix: String = ""): String = {
  val secret = sys.env.getOrElse(env_var, getSecretFromCacheOrKeyvault(name))
  // Cache for future use
}
```

**Secret Priority Order:**
1. Environment variable (loaded by Key Vault task)
2. Local cache file
3. Direct Key Vault fetch (with caching)

Sources: [templates/kv.yml:1-7](), [project/Secrets.scala:130-138]()

## Test Execution Implementation

### Unit Test Execution

Unit tests run through SBT with coverage tracking:

```bash
export SBT_OPTS="-XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled -Xss2M -Duser.timezone=GMT"
(timeout 30m sbt coverage "testOnly com.microsoft.azure.synapse.ml.$(PACKAGE).**") ||
(${FLAKY:-false} && timeout 30m sbt coverage "testOnly com.microsoft.azure.synapse.ml.$(PACKAGE).**")
```

**Key aspects:**
- **JVM options**: Configured for test stability (garbage collection, stack size, timezone)
- **Package filtering**: `testOnly` with package glob pattern
- **Coverage tracking**: `coverage` command enables Scoverage instrumentation
- **Timeout enforcement**: Shell-level timeout with retries

Sources: [pipeline.yaml:752-755]()

### Python Test Execution

Python tests use a specialized SBT task with dynamic filtering:

```bash
IGNORE_TEST_PATH_FLAG=""
TEST_SUB_PATH_FLAG=""
if [ -n "$(IGNORE_TEST_PATH)" ]; then
  IGNORE_TEST_PATH_FLAG="-DpythonIgnoreTestPath=$(IGNORE_TEST_PATH)"
fi
if [ -n "$(TEST_SUB_PATH)" ]; then
  TEST_SUB_PATH_FLAG="-DpythonSubTestPath=$(TEST_SUB_PATH)"
fi

(sbt $IGNORE_TEST_PATH_FLAG $TEST_SUB_PATH_FLAG "project $(PACKAGE)" coverage testPython) || \
(sbt $IGNORE_TEST_PATH_FLAG $TEST_SUB_PATH_FLAG "project $(PACKAGE)" coverage testPython) || \
(sbt $IGNORE_TEST_PATH_FLAG $TEST_SUB_PATH_FLAG "project $(PACKAGE)" coverage testPython)
```

**Dynamic filtering example:**
- Package: `deepLearning`
- Sub-path: `hf` → runs only `deep-learning/src/test/python/**/hf/**/*.py`
- Ignore path: `hf` → excludes `hf` subdirectory from tests

Sources: [pipeline.yaml:407-427]()

### R Test Execution

R tests require Spark binary installation before execution:

```bash
# Prepare Spark environment
SPARK_VERSION=3.5.0
HADOOP_VERSION=3
wget https://mmlspark.blob.core.windows.net/installers/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Run R tests
export SBT_OPTS="-Xms2G -Xmx4G -XX:+UseConcMarkSweepGC ..."
timeout 20m sbt -DskipCodegen=true "project $(PACKAGE)" coverage testR
```

R tests use higher memory limits (`-Xmx4G`) due to R's memory overhead. The `-DskipCodegen=true` flag skips code generation since it was already performed during the prepare step.

Sources: [pipeline.yaml:486-502]()

### Website Documentation Tests

Documentation tests validate code blocks in markdown files using `pytest-codeblocks`:

```python
# website/doctest.py execution
python website/doctest.py <version>
```

The `testWebsiteDocs` task in SBT orchestrates this:

```scala
val testWebsiteDocs = TaskKey[Unit]("testWebsiteDocs",
  "test code blocks inside markdowns under folder website/docs/documentation")
testWebsiteDocs := {
  runCmd(
    Seq("python", s"${join(baseDirectory.value, "website/doctest.py")}", version.value)
  )
}
```

Sources: [build.sbt:361-367](), [pipeline.yaml:546-548]()

## Quality Gates and Reporting

### Test Result Publishing

All test jobs publish results using the `PublishTestResults@2` task:

```yaml
- task: PublishTestResults@2
  displayName: 'Publish Test Results'
  inputs:
    testResultsFiles: '**/test-reports/TEST-*.xml'  # Scala/Java tests
    testResultsFiles: '**/python-test-*.xml'        # Python tests
    testResultsFiles: '**/r-test-*.xml'             # R tests
    failTaskOnFailedTests: true
  condition: succeededOrFailed()
```

The `condition: succeededOrFailed()` ensures results are published even when tests fail, allowing developers to see detailed failure information.

Sources: [pipeline.yaml:176-181](), [pipeline.yaml:428-433](), [pipeline.yaml:503-508](), [pipeline.yaml:756-761]()

### Code Coverage Tracking

```mermaid
graph LR
    Tests["Test Execution<br/>sbt coverage test"]
    Report["Generate Report<br/>sbt coverageReport"]
    Upload["Upload to Codecov<br/>codecov CLI"]
    
    Tests --> Report
    Report --> Upload
    
    subgraph "Coverage Artifacts"
        Scoverage["target/scala-2.12/scoverage-report/"]
        XML["target/scala-2.12/coverage-reports/cobertura.xml"]
    end
    
    Report --> Scoverage
    Report --> XML
    XML --> Upload
```

**Coverage workflow:**

1. **Instrumentation**: `sbt coverage` enables Scoverage instrumentation before tests
2. **Test execution**: Instrumented code records line coverage
3. **Report generation**: `sbt coverageReport` generates Cobertura XML [pipeline.yaml:441](), [pipeline.yaml:516](), [pipeline.yaml:769]()
4. **Upload**: Codecov CLI uploads coverage data [templates/codecov.yml:1-12]()

**Codecov template:**
```yaml
- bash: |
    curl -Os https://cli.codecov.io/latest/linux/codecov
    chmod +x codecov
    ./codecov --verbose upload-process -t $(codecov-token) --dir .
  retryCountOnTaskFailure: 1
  displayName: Upload Coverage Report To Codecov.io
  condition: succeededOrFailed()
```

Sources: [templates/codecov.yml:1-12](), [pipeline.yaml:434-443]()

### Style Checks

The `Style` job enforces code quality standards before other tests run:

**Scala style check:**
```bash
sbt scalastyle test:scalastyle
```

**Python style check:**
```bash
source activate synapseml
black --diff --color . && black --check -q .
```

Style checks have no retry mechanism and must pass cleanly. The `black` formatter validates Python code with `--check` flag (fails on formatting violations) and `--diff` flag (shows violations).

Sources: [pipeline.yaml:66-85]()

## Test Configuration Files

### Build Configuration for Tests

```scala
// build.sbt test settings
val settings = Seq(
  Test / scalastyleConfig := (ThisBuild / baseDirectory).value / "scalastyle-test-config.xml",
  Test / logBuffered := false,          // Stream test logs immediately
  Test / parallelExecution := false,    // Sequential test execution within SBT
  Test / publishArtifact := true,       // Publish test JARs
  // ...
)
```

**Key test settings:**
- **No parallel execution**: Tests within a single SBT project run sequentially to avoid resource conflicts
- **Unbuffered logs**: Test output streams immediately for better debugging
- **Test artifact publishing**: Test classes are published for use in other modules

Sources: [build.sbt:250-264]()

### Python Test Fixtures

Python tests use pytest fixtures for dataset setup:

```python
# deep-learning/src/test/python/synapsemltest/dl/conftest.py
@pytest.fixture(scope="module")
def get_data_path():
    if not os.path.exists(join(dataset_dir, "jpg", delimiter, "train")):
        _download_dataset()
    train_folder = dataset_dir + "jpg" + delimiter + "train"
    test_folder = dataset_dir + "jpg" + delimiter + "test"
    return train_folder, test_folder
```

The `scope="module"` ensures datasets are downloaded once per test module, not per test function. The fixture checks for existing data before downloading to avoid redundant work.

Sources: [deep-learning/src/test/python/synapsemltest/dl/conftest.py:73-79]()

## Continuous Integration Triggers

### Trigger Configuration

```yaml
trigger:
  branches:
    include: [master, spark3.3, spark3.5]
  paths:
    exclude: [README.md, CONTRIBUTORS.md, SECURITY.md, docs/Reference/**, CODEOWNERS]

pr:
  branches:
    include: [master, spark3.3, spark3.5]
  paths:
    exclude: [README.md, CONTRIBUTORS.md, SECURITY.md, docs/Reference/**, CODEOWNERS]

schedules:
  - cron: "0 0 * * *"  # Daily midnight build
    displayName: Daily midnight build
    always: true
    branches:
      include: [master]
```

**Trigger behavior:**
- **Push triggers**: Run on commits to main branches (excluding documentation changes)
- **PR triggers**: Run on pull requests to main branches (same exclusions)
- **Scheduled triggers**: Daily builds on master regardless of commits (`always: true`)

Sources: [pipeline.yaml:4-42]()

### Conditional Test Execution

```yaml
parameters:
  - name: runSynapseExtensionE2ETests
    displayName: Run Synapse Extension E2E Tests
    type: boolean
    default: true
  - name: SYNAPSE_ENVIRONMENT
    displayName: Synapse Extension E2E Test Environment
    type: string
    default: weekly
    values: [dev, daily, weekly]
```

Pipeline parameters allow manual control of expensive E2E tests. The `runSynapseExtensionE2ETests` parameter gates Synapse internal tests, while `SYNAPSE_ENVIRONMENT` selects the test environment.

Sources: [pipeline.yaml:44-56]()

## Test Isolation and Cleanup

### Disk Space Management

The Conda template includes disk space cleanup to prevent out-of-disk errors:

```bash
echo "Removing unused pre-installed SDKs..."
sudo rm -rf /usr/local/lib/android || true
sudo rm -rf /usr/lib/google-cloud-sdk || true
```

This frees ~10-15 GB by removing unused Android and Google Cloud SDKs that come pre-installed on Azure DevOps VMs.

Sources: [templates/conda.yml:18-28]()

### Test Artifact Exclusions

The `.gitignore` file excludes test artifacts from version control:

```gitignore
# Notebook Test Files
/notebooks/**/*.py     # Generated from .ipynb
/notebooks/**/*.txt

# Test outputs
/TestResults
.coverage
coverage.xml
htmlcov

# R output
*.Rout
.Rhistory

# pytest
.pytest_cache/
```

Sources: [.gitignore:54-84]()

## Summary

The SynapseML testing strategy implements a robust, multi-layered approach that balances comprehensiveness with execution speed:

- **30+ parallel unit test jobs** across Scala packages with package-specific retry policies
- **13 parallel Python/R test jobs** with sub-path filtering for fine-grained control
- **2-4 E2E test jobs** validating real-world platform integrations
- **Automatic retry mechanisms** handling transient failures without manual intervention
- **Cached Conda environments** reducing setup time from 30 minutes to seconds
- **Comprehensive coverage tracking** integrated with Codecov.io for continuous quality monitoring

This strategy ensures high code quality while maintaining fast feedback cycles for developers.

---

# Page: Synapse E2E Testing

# Notebook Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)

</details>



This page documents the automated testing system for Jupyter notebooks in SynapseML. The system executes example notebooks across different platforms (Azure Databricks and Azure Synapse Analytics) to ensure that code examples remain functional as the library evolves. This is a critical part of SynapseML's testing infrastructure as it validates real-world usage patterns beyond unit tests.

## Testing Architecture

The notebook testing system is divided into two main components that handle testing on different platforms:

```mermaid
graph TD
    subgraph "Notebook Testing System"
        NTS["Notebook Testing Infrastructure"]
        DT["Databricks Testing"]
        ST["Synapse Testing"]
        
        NTS --> DT
        NTS --> ST
    end
    
    subgraph "Databricks Components"
        DU["DatabricksUtilities"]
        DH["DatabricksTestHelper"]
        DCPUT["DatabricksCPUTests"]
        DGPUT["DatabricksGPUTests"]
        DRAPIDST["DatabricksRapidsTests"]
        
        DT --> DU
        DT --> DH
        DH --> DCPUT
        DH --> DGPUT
        DH --> DRAPIDST
    end
    
    subgraph "Synapse Components"
        SU["SynapseUtilities"]
        ST1["SynapseTests"]
        STC["SynapseTestCleanup"]
        
        ST --> SU
        ST --> ST1
        ST --> STC
    end
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala]()

## Notebook Categories

Notebooks are categorized based on their resource requirements and testing environment:

| Category | Description | Testing Environment | 
|----------|-------------|---------------------|
| CPU Notebooks | General notebooks not requiring GPU acceleration | Databricks Standard Clusters, Synapse Pools |
| GPU Notebooks | Deep learning notebooks requiring GPU (e.g., Fine-tune, Phi Model) | Databricks GPU Clusters |
| RAPIDS Notebooks | Notebooks using NVIDIA RAPIDS acceleration | Databricks GPU Clusters with RAPIDS |

```mermaid
graph TD
    AN["All Notebooks"] --> Filter["Filtering Logic"]
    
    Filter --> CPU["CPU Notebooks"]
    Filter --> GPU["GPU Notebooks"]
    Filter --> RAPIDS["RAPIDS Notebooks"]
    
    CPU --> CPUE["Exclusion Rules:
    - No Fine-tune
    - No GPU
    - No Phi Model
    - No Language Model
    - No Audiobooks
    - etc."]
    
    GPU --> GPUE["Selection Rules:
    - Contains Fine-tune
    - Contains Phi Model"]
    
    RAPIDS --> RAPIDSE["Selection Rules:
    - Contains GPU"]
    
    CPUE --> FCPU["Final CPU Notebooks"]
    GPUE --> FGPU["Final GPU Notebooks"]
    RAPIDSE --> FRAPIDS["Final RAPIDS Notebooks"]
    
    FCPU --> CPUC["Run on CPU Cluster"]
    FGPU --> GPUC["Run on GPU Cluster"]
    FRAPIDS --> RAPIDSC["Run on RAPIDS Cluster"]
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:108-122](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:47-64]()

## Databricks Testing System

The Databricks testing system uses the Databricks REST API to manage clusters, upload notebooks, and execute notebook jobs.

### Configuration Parameters

```mermaid
graph TD
    subgraph "Databricks Testing Configuration"
        Region["Region = eastus"]
        Pool["PoolName = synapseml-build-13.3"]
        GPUPool["GpuPoolName = synapseml-build-13.3-gpu"]
        Runtime["AdbRuntime = 13.3.x-scala2.12"]
        GPURuntime["AdbGpuRuntime = 13.3.x-gpu-ml-scala2.12"]
        Workers["NumWorkers = 5"]
        Termination["AutoTerminationMinutes = 15"]
        Timeout["TimeoutInMillis = 50 * 60 * 1000"]
        SynapseMLDir["Folder = /SynapseMLBuild/build_${version}"]
    end
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:34-53](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:100]()

### Workflow

The Databricks testing workflow follows these steps:

```mermaid
sequenceDiagram
    participant TC as "Test Class"
    participant DU as "DatabricksUtilities"
    participant API as "Databricks API"
    participant C as "Databricks Cluster"
    
    TC->>DU: createClusterInPool(name, runtime, workers, poolId)
    DU->>API: POST /api/2.0/clusters/create
    API-->>DU: Return cluster_id
    
    TC->>DU: installLibraries(clusterId, libraries)
    DU->>API: POST /api/2.0/libraries/install
    API->>C: Install libraries
    
    Note over TC,DU: Check cluster is active
    TC->>DU: isClusterActive(clusterId)
    DU->>API: GET /api/2.0/clusters/get
    API-->>DU: Return cluster state
    
    Note over TC,DU: Check libraries installed
    TC->>DU: areLibrariesInstalled(clusterId)
    DU->>API: GET /api/2.0/libraries/cluster-status
    API-->>DU: Return installation status
    
    loop Each notebook
        TC->>DU: runNotebook(clusterId, notebookFile)
        DU->>DU: workspaceMkDir(folderPath)
        DU->>API: POST /api/2.0/workspace/mkdirs
        
        DU->>DU: uploadNotebook(file, destination)
        DU->>API: POST /api/2.0/workspace/import
        
        DU->>DU: submitRun(clusterId, notebookPath)
        DU->>API: POST /api/2.0/jobs/runs/submit
        API-->>DU: Return run_id
        
        DU->>DU: monitorJob(runId, timeout)
        loop Until complete or timeout
            DU->>API: GET /api/2.0/jobs/runs/get
            API-->>DU: Return run status
        end
    end
    
    TC->>DU: afterAllHelper(clusterId, clusterName)
    DU->>DU: Cancel all jobs
    loop For each job
        DU->>API: POST /api/2.0/jobs/runs/cancel
    end
    DU->>API: POST /api/2.0/clusters/permanent-delete
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:198-265](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:367-378](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:307-365](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksTestHelper.scala:439-479]()

### Key Components

1. **DatabricksUtilities**: Core utility class providing methods for interacting with the Databricks REST API:
   - Cluster management (`createClusterInPool`, `isClusterActive`, `terminateCluster`)
   - Library management (`installLibraries`, `areLibrariesInstalled`)
   - Workspace operations (`workspaceMkDir`, `uploadNotebook`)
   - Job execution (`submitRun`, `monitorJob`, `cancelRun`)

2. **DatabricksTestHelper**: Abstract class with common testing functionality:
   - `databricksTestHelper`: Main method for executing notebooks
   - Uses retries for resilience against transient errors
   - Handles parallel notebook execution

3. **Test Implementations**:
   - `DatabricksCPUTests`: Tests for CPU notebooks (standard ML)
   - `DatabricksGPUTests`: Tests for GPU notebooks (deep learning)
   - `DatabricksRapidsTests`: Tests for RAPIDS-enabled notebooks

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksTestHelper.scala:431-480](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala]()

## Synapse Testing System

The Synapse testing system uses the Synapse REST API to manage Spark pools and execute notebooks via Livy batches.

### Workflow

The Synapse testing workflow follows these steps:

```mermaid
sequenceDiagram
    participant ST as "SynapseTests"
    participant SU as "SynapseUtilities"
    participant API as "Synapse API"
    participant SP as "Spark Pool"
    
    Note over ST,SU: Clean up old resources
    ST->>SU: tryDeleteOldSparkPools()
    
    Note over ST,SU: Create test resources
    ST->>SU: createSparkPools(count)
    SU->>API: Create Apache Spark pools
    API-->>SU: Return pool names
    
    loop Each notebook+pool pair
        ST->>SU: uploadAndSubmitNotebook(poolName, file)
        SU->>API: Upload notebook
        
        SU->>API: Submit Livy batch
        API->>SP: Execute notebook
        
        SU-->>ST: Return LivyBatch object
        
        ST->>ST: Monitor batch execution
        loop Until complete or timeout
            ST->>API: Check batch status
            API-->>ST: Return status
        end
    end
    
    Note over ST,SU: Cleanup
    ST->>SU: Delete all Spark pools
    SU->>API: Delete pool requests
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:44-113]()

### Key Components

1. **SynapseUtilities**: Provides methods for interacting with Synapse APIs:
   - Spark pool management
   - Notebook upload
   - Livy batch submission and monitoring

2. **SynapseTests**: Main test class for Synapse notebook testing:
   - Creates Spark pools for testing
   - Selects notebooks to test
   - Submits notebooks as Livy batches
   - Monitors execution and cleans up resources

3. **SynapseTestCleanup**: Utility class for cleaning up old Spark pools.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala]()

## Required Dependencies

Both testing systems depend on specific library packages:

### Python Packages

The following Python packages are installed on the test clusters:

```
nltk, bs4, plotly, Pillow, onnxmltools, lightgbm, mlflow, openai,
langchain, pdf2image, pdfminer.six, sqlparse, raiwidgets,
interpret-community, numpy, unstructured, pytesseract
```

### GPU-Specific Packages

For GPU tests, additional packages are installed:

```
pytorch-lightning, torchvision, transformers, jinja2, petastorm,
protobuf, accelerate
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:56-73](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:84-93](), [environment.yml]()

## Integration with CI/CD Pipeline

The notebook testing system is integrated with SynapseML's CI/CD pipeline and runs as part of the test phase. This ensures that changes to the library don't break example notebooks.

```mermaid
graph TD
    subgraph "CI/CD Pipeline"
        Build["Build Jobs"]
        UnitTests["Unit Tests"]
        NBTests["Notebook Tests"]
        Publish["Publish Jobs"]
        
        Build --> UnitTests
        UnitTests --> NBTests
        NBTests --> Publish
    end
    
    subgraph "Notebook Tests"
        NBSelect["Select Notebooks"]
        DBNBTest["Databricks Tests"]
        SynapseNBTest["Synapse Tests"]
        Results["Test Results"]
        
        NBSelect --> DBNBTest
        NBSelect --> SynapseNBTest
        DBNBTest --> Results
        SynapseNBTest --> Results
    end
    
    subgraph "Databricks Tests"
        CPUTests["CPU Tests"]
        GPUTests["GPU Tests"]
        RapidsTests["RAPIDS Tests"]
    end
    
    DBNBTest --> CPUTests
    DBNBTest --> GPUTests
    DBNBTest --> RapidsTests
```

## Error Handling and Retries

Both testing systems implement robust error handling and retry mechanisms:

1. **Cluster/Pool Availability**:
   - Retry cluster status checks with exponential backoff
   - Maximum retries configurable per test class

2. **Library Installation**:
   - Check for library installation status
   - Report detailed errors for failed installations

3. **Job Monitoring**:
   - Timeout configuration for long-running notebooks
   - Detailed error reporting with run page URLs
   - Handling of various failure states

4. **Resource Cleanup**:
   - Job cancellation on test completion or failure
   - Cluster/pool deletion after tests

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:307-365](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksTestHelper.scala:442-446](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:88-96]()

## Example: Deep Learning Notebook Testing

To illustrate how notebooks are tested, let's examine how a deep learning vision classifier notebook is tested:

1. The notebook [docs/Explore Algorithms/Deep Learning/Quickstart - Fine-tune a Vision Classifier.ipynb]() is categorized as a GPU notebook because it contains "Fine-tune" in its path.

2. `DatabricksGPUTests` creates a dedicated GPU cluster with specific configurations:
   - Uses the GPU-optimized runtime (`AdbGpuRuntime`)
   - Installs deep learning libraries (`GPULibraries`)
   - Creates the cluster in the GPU instance pool (`GpuPoolId`)

3. The notebook is executed with appropriate GPU resources, and the test monitors for successful completion.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](), [docs/Explore Algorithms/Deep Learning/Quickstart - Fine-tune a Vision Classifier.ipynb](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py]()

## Common Issues and Troubleshooting

1. **Timeout Errors**:
   - Notebooks that run longer than the configured timeout (`TimeoutInMillis = 50 * 60 * 1000`) will fail with a timeout exception
   - This is handled by the `monitorJob` method which tracks the execution time and reports detailed information including the run URL

2. **Library Installation Failures**:
   - The testing infrastructure detects failed library installations and reports detailed errors
   - Common causes include incompatible library versions or network connectivity issues

3. **Resource Constraints**:
   - Tests may fail if the Azure subscription has insufficient quota for the required resources
   - The cleanup process ensures resources are released even if tests fail

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:307-365](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:297-305]()

## Summary

The notebook testing system is a critical component of SynapseML's quality assurance process. It ensures that example notebooks remain functional as the library evolves by automatically testing them on both Databricks and Synapse platforms. The system handles different types of workloads (CPU, GPU, RAPIDS) and provides robust error handling and reporting.

---

# Page: Databricks E2E Testing

# Databricks E2E Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala)
- [deep-learning/src/main/python/horovod_installation.sh](deep-learning/src/main/python/horovod_installation.sh)
- [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py)
- [docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb](docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb)

</details>



## Purpose and Scope

This document describes the end-to-end (E2E) testing infrastructure for executing SynapseML notebooks on Databricks clusters. The system provisions ephemeral Databricks clusters, installs required libraries, executes Jupyter notebooks as tests, and monitors job completion with automatic cleanup.

For Synapse-specific E2E testing, see [Synapse E2E Testing](#4.2). For unit testing strategies, see [Testing Strategy](#4.1).

## System Architecture

The Databricks E2E testing system consists of utilities for cluster lifecycle management, library installation, notebook execution, and job monitoring through the Databricks REST API.

```mermaid
graph TB
    subgraph "Test Classes"
        CPUTests["DatabricksCPUTests<br/>5 concurrent notebooks"]
        GPUTests["DatabricksGPUTests<br/>1 concurrent notebook"]
        RapidsTests["DatabricksRapidsTests<br/>4 concurrent notebooks"]
    end
    
    subgraph "Core Framework"
        TestHelper["DatabricksTestHelper<br/>databricksTestHelper()"]
        Utils["DatabricksUtilities<br/>REST API Wrappers"]
        State["DatabricksState<br/>JobIdsToCancel buffer"]
    end
    
    subgraph "Cluster Management"
        CreateCluster["createClusterInPool()"]
        InstallLibs["installLibraries()"]
        MonitorCluster["isClusterActive()"]
        DeleteCluster["permanentDeleteCluster()"]
    end
    
    subgraph "Notebook Execution"
        Upload["uploadNotebook()"]
        Submit["submitRun()"]
        Monitor["monitorJob()"]
        Cancel["cancelRun()"]
    end
    
    subgraph "External Services"
        ADBAPI["Databricks REST API<br/>eastus.azuredatabricks.net"]
        Pools["Instance Pools<br/>synapseml-build-14.3<br/>synapseml-build-14.3-gpu"]
        DBFS["DBFS Workspace<br/>/SynapseMLBuild/"]
    end
    
    CPUTests --> TestHelper
    GPUTests --> TestHelper
    RapidsTests --> TestHelper
    
    TestHelper --> Utils
    TestHelper --> State
    
    Utils --> CreateCluster
    Utils --> InstallLibs
    Utils --> Upload
    Utils --> Submit
    
    CreateCluster --> ADBAPI
    InstallLibs --> ADBAPI
    Upload --> ADBAPI
    Submit --> ADBAPI
    
    MonitorCluster --> ADBAPI
    Monitor --> ADBAPI
    Cancel --> ADBAPI
    DeleteCluster --> ADBAPI
    
    CreateCluster --> Pools
    Upload --> DBFS
    
    Submit --> Monitor
    Monitor --> State
    State --> Cancel
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:1-488](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:1-26](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:1-20](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:1-20]()

## Test Suite Organization

The Databricks E2E testing system organizes notebooks into three test suites based on hardware requirements and execution characteristics.

| Test Suite | Class | Cluster Type | Runtime | Workers | Concurrency | Notebooks |
|------------|-------|--------------|---------|---------|-------------|-----------|
| CPU | `DatabricksCPUTests` | CPU Pool | `14.3.x-scala2.12` | 5 | 5 | Most notebooks |
| GPU | `DatabricksGPUTests` | GPU Pool | `14.3.x-gpu-ml-scala2.12` | 2 | 1 | Fine-tune, Phi Model |
| RAPIDS | `DatabricksRapidsTests` | GPU Pool | `14.3.x-gpu-ml-scala2.12` | 1 | 4 | GPU-prefixed notebooks |

### Notebook Classification

```mermaid
graph LR
    AllNotebooks["ParallelizableNotebooks<br/>docs/**/*.ipynb"]
    
    CPUFilter["filterNot()"]
    GPUFilter["filter()"]
    RapidsFilter["filter()"]
    
    CPUNotebooks["CPUNotebooks<br/>~108 notebooks"]
    GPUNotebooks["GPUNotebooks<br/>Fine-tune + Phi Model"]
    RapidsNotebooks["RapidsNotebooks<br/>GPU prefix"]
    
    AllNotebooks --> CPUFilter
    AllNotebooks --> GPUFilter
    AllNotebooks --> RapidsFilter
    
    CPUFilter --> CPUNotebooks
    GPUFilter --> GPUNotebooks
    RapidsFilter --> RapidsNotebooks
    
    Exclusions["Excluded:<br/>- Fine-tune<br/>- GPU<br/>- Phi Model<br/>- Language Model<br/>- Multivariate Anomaly<br/>- Audiobooks<br/>- Art<br/>- Explanation Dashboard<br/>- Isolation Forests<br/>- Snow Leopard Detection"]
    
    CPUFilter -.-> Exclusions
```

The notebook classification logic filters the full set of notebooks discovered from the `docs/` directory:

- **CPUNotebooks**: All notebooks except those requiring GPU or excluded for specific reasons [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:108-118]()
- **GPUNotebooks**: Notebooks containing "Fine-tune" or "Phi Model" in their path [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:120-122]()
- **RapidsNotebooks**: Notebooks containing "GPU" in their path [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:124]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:102-124]()

## Cluster Configuration and Management

### Cluster Specifications

The system uses pre-configured instance pools to provision clusters with specific configurations:

```scala
// Configuration Constants
val PoolName = "synapseml-build-14.3"
val GpuPoolName = "synapseml-build-14.3-gpu"
val AdbRuntime = "14.3.x-scala2.12"
val AdbGpuRuntime = "14.3.x-gpu-ml-scala2.12"
val NumWorkers = 5
val AutoTerminationMinutes = 15
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:33-41]()

### Cluster Creation Process

```mermaid
graph TB
    CreateRequest["createClusterInPool()<br/>clusterName, sparkVersion, poolId"]
    
    BuildJSON["Build JSON Payload<br/>- spark_version<br/>- num_workers<br/>- instance_pool_id<br/>- spark_conf<br/>- spark_env_vars<br/>- init_scripts"]
    
    POST["POST clusters/create<br/>Databricks API"]
    
    GetClusterId["Extract cluster_id<br/>from response"]
    
    WaitActive["tryWithRetries()<br/>60*20 attempts<br/>1s intervals"]
    
    CheckActive["isClusterActive()<br/>GET clusters/get"]
    
    StateCheck{{"state == RUNNING"}}
    
    Ready["Cluster Ready"]
    
    CreateRequest --> BuildJSON
    BuildJSON --> POST
    POST --> GetClusterId
    GetClusterId --> WaitActive
    WaitActive --> CheckActive
    CheckActive --> StateCheck
    StateCheck -->|Yes| Ready
    StateCheck -->|No| WaitActive
```

The `createClusterInPool` method constructs a cluster configuration JSON and submits it to the Databricks API. For RAPIDS tests, it includes init scripts that install CUDA dependencies and NCCL [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:200-233]().

**CPU Cluster Creation:**
```scala
val clusterId: String = createClusterInPool(
  ClusterName, 
  AdbRuntime, 
  NumWorkers, 
  PoolId, 
  memory = Some("7g")
)
```
[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:12]()

**GPU Cluster Creation:**
```scala
val clusterId: String = createClusterInPool(
  GPUClusterName, 
  AdbGpuRuntime, 
  2, 
  GpuPoolId
)
```
[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:10]()

**RAPIDS Cluster Creation (with init scripts):**
```scala
val clusterId: String = createClusterInPool(
  GPUClusterName, 
  AdbGpuRuntime, 
  1, 
  GpuPoolId, 
  RapidsInitScripts
)
```
[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:10]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:200-233](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:290-295]()

## Library Installation

### Library Definitions

The system defines three library configurations for different cluster types:

**Standard Libraries (CPU):**
```scala
val Libraries: String = (
  List(Map("maven" -> Map(
    "coordinates" -> PackageMavenCoordinate, 
    "repo" -> PackageRepository
  ))) ++
  PipPackages.map(p => Map("pypi" -> Map("package" -> p)))
).toJson.compactPrint
```

The `PipPackages` list includes:
- `nltk`, `bs4`, `plotly`, `Pillow`
- `onnxmltools==1.7.0`
- `lightgbm`
- `mlflow==2.21.3`
- `openai==0.28.1`
- `langchain==0.0.331`
- `pdf2image`, `pdfminer.six`, `sqlparse`
- `interpret-community`
- `numpy==1.26.4`
- `unstructured==0.10.24`
- `pytesseract`

[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:56-81]()

**GPU Libraries:**
```scala
val GPULibraries: String = List(
  Map("maven" -> Map("coordinates" -> PackageMavenCoordinate, "repo" -> PackageRepository)),
  Map("pypi" -> Map("package" -> "pytorch-lightning==1.5.0")),
  Map("pypi" -> Map("package" -> "torchvision==0.15.1")),
  Map("pypi" -> Map("package" -> "transformers==4.49.0")),
  Map("pypi" -> Map("package" -> "jinja2==3.1.6")),
  Map("pypi" -> Map("package" -> "petastorm==0.12.1")),
  Map("pypi" -> Map("package" -> "protobuf==5.29.4")),
  Map("pypi" -> Map("package" -> "accelerate==0.26.0"))
).toJson.compactPrint
```
[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:84-93]()

### Installation Process

```mermaid
graph TB
    Install["installLibraries()<br/>clusterId, libraries"]
    
    BuildJSON["Build JSON:<br/>{cluster_id, libraries}"]
    
    POST["POST libraries/install"]
    
    WaitInstall["tryWithRetries()<br/>60*6 attempts<br/>1s intervals"]
    
    CheckStatus["areLibrariesInstalled()<br/>GET libraries/cluster-status"]
    
    ParseStatus["Parse library_statuses"]
    
    CheckFailed{{"status == FAILED"}}
    CheckAll{{"all status == INSTALLED"}}
    
    ThrowError["throw RuntimeException<br/>Library Installation Failure"]
    
    Ready["Libraries Ready"]
    
    Install --> BuildJSON
    BuildJSON --> POST
    POST --> WaitInstall
    WaitInstall --> CheckStatus
    CheckStatus --> ParseStatus
    ParseStatus --> CheckFailed
    CheckFailed -->|Yes| ThrowError
    CheckFailed -->|No| CheckAll
    CheckAll -->|Yes| Ready
    CheckAll -->|No| WaitInstall
```

The library installation system:
1. Sends a `libraries/install` POST request with the cluster ID and library specifications
2. Polls the `libraries/cluster-status` endpoint to verify installation completion
3. Checks for `FAILED` status and throws an exception with error details if found
4. Waits until all libraries have `INSTALLED` status

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:235-306]()

## Notebook Execution Pipeline

### Execution Workflow

```mermaid
graph TB
    Upload["uploadNotebook()<br/>file, destination"]
    
    Encode["Base64 encode<br/>notebook content"]
    
    POST1["POST workspace/import<br/>format: JUPYTER"]
    
    Submit["submitRun()<br/>clusterId, notebookPath"]
    
    BuildRunJSON["Build JSON:<br/>- existing_cluster_id<br/>- timeout_seconds<br/>- notebook_task.notebook_path"]
    
    POST2["POST jobs/runs/submit"]
    
    ExtractRunId["Extract run_id"]
    
    TrackJob["DatabricksState.JobIdsToCancel<br/>append(runId)"]
    
    Monitor["monitorJob()<br/>runId, timeout, interval"]
    
    Poll["getRunStatuses()<br/>GET jobs/runs/get"]
    
    CheckState{{"life_cycle_state"}}
    
    GetURL["getRunUrlAndNBName()<br/>run_page_url"]
    
    Success["Log success"]
    Failure["throw RuntimeException<br/>with run URL"]
    Timeout["throw TimeoutException<br/>50 min timeout"]
    
    Upload --> Encode
    Encode --> POST1
    POST1 --> Submit
    Submit --> BuildRunJSON
    BuildRunJSON --> POST2
    POST2 --> ExtractRunId
    ExtractRunId --> TrackJob
    TrackJob --> Monitor
    Monitor --> Poll
    Poll --> CheckState
    CheckState -->|TERMINATED + SUCCESS| GetURL
    CheckState -->|TERMINATED + other| GetURL
    CheckState -->|INTERNAL_ERROR| GetURL
    CheckState -->|timeout| Timeout
    GetURL --> Success
    GetURL --> Failure
```

The notebook execution process involves several steps:

1. **Upload**: Notebook is base64-encoded and uploaded to DBFS workspace via `workspace/import` [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:163-177]()

2. **Submit**: A job run is created with `jobs/runs/submit`, specifying the cluster and notebook path [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:274-288]()

3. **Track**: The run ID is added to `DatabricksState.JobIdsToCancel` for cleanup if the test suite fails [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:428-430]()

4. **Monitor**: The `monitorJob` method polls the run status every 10 seconds with jitter to avoid overwhelming the API [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:328-366]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:163-177](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:274-288](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:328-366](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:368-380]()

### Parallel Execution Model

The `databricksTestHelper` method orchestrates parallel notebook execution:

```mermaid
graph TB
    Helper["databricksTestHelper()<br/>clusterId, libraries, notebooks, maxConcurrency"]
    
    CheckCluster["Check cluster active<br/>60*20 retries"]
    
    InstallLibs["Install libraries<br/>60*6 retries"]
    
    CreatePool["Executors.newFixedThreadPool(maxConcurrency)"]
    
    CreateFutures["notebooks.map { notebook =><br/>Future { retry { runNotebook } } }"]
    
    ZipWithNB["futures.zip(notebooks)"]
    
    CreateTests["foreach { (future, notebook) =><br/>test(notebook.getName) { Await.result(future) } }"]
    
    Await["Await.result(future, TimeoutInMillis)"]
    
    Helper --> CheckCluster
    CheckCluster --> InstallLibs
    InstallLibs --> CreatePool
    CreatePool --> CreateFutures
    CreateFutures --> ZipWithNB
    ZipWithNB --> CreateTests
    CreateTests --> Await
```

Each test class specifies a different concurrency level:
- **CPU Tests**: 5 concurrent notebooks [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:14]()
- **GPU Tests**: 1 concurrent notebook [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:12]()
- **RAPIDS Tests**: 4 concurrent notebooks [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:12]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:436-471]()

## Monitoring and Error Handling

### Job Monitoring State Machine

```mermaid
stateDiagram-v2
    [*] --> NotStarted
    
    NotStarted --> PENDING: Job submitted
    NotStarted --> INTERNAL_ERROR: API error
    
    PENDING --> RUNNING: Execution starts
    PENDING --> INTERNAL_ERROR: Cluster failure
    
    RUNNING --> TERMINATING: Completion/cancellation
    RUNNING --> INTERNAL_ERROR: Runtime error
    
    TERMINATING --> SUCCESS: result_state check
    TERMINATING --> FAILED: result_state check
    TERMINATING --> CANCELED: result_state check
    
    SUCCESS --> [*]: Test passes
    FAILED --> [*]: Throw RuntimeException
    CANCELED --> [*]: Throw RuntimeException
    INTERNAL_ERROR --> [*]: Throw RuntimeException
    
    NotStarted --> Timeout: 50 minutes
    PENDING --> Timeout: 50 minutes
    RUNNING --> Timeout: 50 minutes
    Timeout --> [*]: Throw TimeoutException
```

The monitoring system tracks two state dimensions:
1. **life_cycle_state**: `PENDING`, `RUNNING`, `TERMINATING`, `TERMINATED`, `INTERNAL_ERROR`
2. **result_state** (when `TERMINATED`): `SUCCESS`, `FAILED`, `CANCELED`

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:308-366]()

### Retry and Error Handling

The system implements multiple retry strategies:

**API Request Retries:**
```scala
def databricksGet(path: String, apiVersion: String = "2.0"): JsValue = {
  val request = new HttpGet(baseURL(apiVersion) + path)
  request.addHeader("Authorization", AuthValue)
  val random = new Random()
  RESTHelpers.sendAndParseJson(request, backoffs = List.fill(3) {
    1000 + random.nextInt(1000)
  })
}
```
Uses jittered backoff with 3 retries at 1000-2000ms intervals [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:126-133]()

**Notebook Execution Retries:**
```scala
retry(retries, { () =>
  runNotebook(clusterId, notebook)
})
```
Default retry configuration: single retry after 15 seconds [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:461-463]()

**Error Message Construction:**
When a job fails, the system provides detailed error information:
```scala
case Some(state) =>
  throw new RuntimeException(s"Notebook $nbName failed with state $state. " +
    s"For more information check the run page: \n$url\n")
```
[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:355-357]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:126-141](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:328-366]()

## Test Helper Framework

### DatabricksTestHelper Class Structure

```mermaid
classDiagram
    class TestBase {
        <<trait>>
    }
    
    class DatabricksTestHelper {
        <<abstract>>
        +databricksTestHelper(clusterId, libraries, notebooks, maxConcurrency, retries)
        #afterAllHelper(clusterId, clusterName)
    }
    
    class DatabricksCPUTests {
        +clusterId: String
        +afterAll()
    }
    
    class DatabricksGPUTests {
        +clusterId: String
        +afterAll()
    }
    
    class DatabricksRapidsTests {
        +clusterId: String
        +afterAll()
    }
    
    class DatabricksUtilities {
        <<object>>
        +createClusterInPool()
        +installLibraries()
        +uploadNotebook()
        +submitRun()
        +monitorJob()
        +permanentDeleteCluster()
        +cancelRun()
        +listActiveJobs()
    }
    
    class DatabricksState {
        <<object>>
        +JobIdsToCancel: ListBuffer~Long~
    }
    
    class DatabricksNotebookRun {
        +runId: Long
        +notebookName: String
        +monitor(logLevel: Int)
    }
    
    TestBase <|-- DatabricksTestHelper
    DatabricksTestHelper <|-- DatabricksCPUTests
    DatabricksTestHelper <|-- DatabricksGPUTests
    DatabricksTestHelper <|-- DatabricksRapidsTests
    DatabricksTestHelper ..> DatabricksUtilities
    DatabricksTestHelper ..> DatabricksState
    DatabricksUtilities ..> DatabricksNotebookRun
```

### Test Execution Flow

Each test class follows a standard pattern:

**Setup Phase:**
```scala
val clusterId: String = createClusterInPool(ClusterName, AdbRuntime, NumWorkers, PoolId)
```

**Test Phase:**
```scala
databricksTestHelper(clusterId, Libraries, CPUNotebooks, 5)
```

**Cleanup Phase:**
```scala
protected override def afterAll(): Unit = {
  afterAllHelper(clusterId, ClusterName)
  super.afterAll()
}
```

The `afterAllHelper` method performs cleanup:
1. Cancels all tracked jobs via `DatabricksState.JobIdsToCancel`
2. Permanently deletes the cluster via `permanentDeleteCluster`

[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:474-480]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:432-481](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:10-19]()

## Authentication and Configuration

### Authentication Mechanism

The system uses token-based authentication with the Databricks API:

```scala
lazy val Token: String = sys.env.getOrElse("MML_ADB_TOKEN", Secrets.AdbToken)
lazy val AuthValue: String = "Basic " + BaseEncoding.base64()
  .encode(("token:" + Token).getBytes("UTF-8"))
```

All API requests include the authorization header:
```scala
request.addHeader("Authorization", AuthValue)
```

[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:43-45](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:128]()

### Regional Configuration

The base URL is constructed from a regional constant:
```scala
val Region = "eastus"
def baseURL(apiVersion: String): String = 
  s"https://$Region.azuredatabricks.net/api/$apiVersion/"
```

[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:34](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:76]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:33-76]()

## Deep Learning Integration

For GPU and RAPIDS tests, the system manages specialized deep learning library installations:

### Horovod Installation Script

The RAPIDS clusters use an initialization script that installs Horovod with NCCL support for distributed training:

```bash
# Install prerequisite libraries
pip install pytorch-lightning==1.5.0
pip install torchvision==0.15.1
pip install transformers==4.49.0
pip install petastorm>=0.12.1
pip install protobuf==5.29.4

# Install CUDA and NCCL dependencies
apt-get install --allow-downgrades --no-install-recommends -y \
  cuda-nvml-dev-11-0=11.0.167-1 \
  cuda-nvcc-11-0=11.0.221-1 \
  cuda-cudart-dev-11-0=11.0.221-1 \
  cuda-libraries-dev-11-0=11.0.3-1 \
  libnccl-dev=2.10.3-1+cuda11.0 \
  libcusparse-dev-11-0=11.1.1.245-1

# Build and install Horovod from source
git clone --recursive https://github.com/horovod/horovod.git
HOROVOD_GPU_ALLREDUCE=NCCL HOROVOD_CUDA_HOME=/usr/local/cuda-11/ \
HOROVOD_WITH_PYTORCH=1 HOROVOD_WITHOUT_MXNET=1 \
python setup.py bdist_wheel
```

[deep-learning/src/main/python/horovod_installation.sh:1-48]()

### Deep Learning Test Examples

The GPU notebooks validate models like:
- **DeepTextClassifier**: Fine-tunes transformer models (BERT, DistilBERT) for text classification using Horovod [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:27-289]()
- **DeepVisionClassifier**: Fine-tunes vision models (ResNet, VGG, Inception, ViT) for image classification [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:31-269]()

Both classifiers extend `TorchEstimator` from Horovod for distributed training and use PyTorch Lightning for model definition [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:29-177](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:30-234]().

**Sources:** [deep-learning/src/main/python/horovod_installation.sh:1-48](), [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:1-289](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:1-269]()

## Workspace Organization

### Directory Structure

Notebooks are uploaded to a versioned workspace directory:

```scala
val Folder = s"/SynapseMLBuild/build_${BuildInfo.version}"
```

During execution, the system:
1. Creates the directory structure: `workspaceMkDir(folderToCreate)`
2. Uploads the notebook: `uploadNotebook(notebookFile, destination)`
3. Maintains the relative path structure from `docs/` to preserve organization

[core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:53](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:368-380]()

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:53](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:157-198](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:368-380]()

---

# Page: Component Fuzzing

# Component Fuzzing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)

</details>



Component Fuzzing is an automated testing framework that validates all SynapseML `PipelineStage` implementations. The framework uses reflection and service discovery to find all pipeline components in the codebase and systematically tests them for serialization correctness, cross-language compatibility, and interface compliance.

## Overview

The `FuzzingTest` class automatically discovers and validates pipeline components through several mechanisms:

| Test Type | Purpose | Key Validation |
|-----------|---------|----------------|
| Serialization | Save/load model persistence | MLWritable/MLReadable compliance |
| Experiment | Fit/transform workflows | Estimator/Transformer behavior |
| Python | Cross-language bindings | Python SDK compatibility |
| R | Cross-language bindings | R SDK compatibility |
| Interface | Trait implementation | HasInputCol, HasOutputCol, etc. |
| Logging | Telemetry integration | SynapseMLLogging usage |

The framework uses `JarLoadingUtils.instantiateServices[T]()` to dynamically discover all implementations of specific traits, then validates each discovered component against a set of requirements.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:19-34]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:422-436]()

## Component Discovery and Test Execution

```mermaid
graph TB
    subgraph "FuzzingTest Class"
        FT["FuzzingTest"] --> LoadPS["JarLoadingUtils.instantiateServices[PipelineStage]()"]
        FT --> LoadReaders["JarLoadingUtils.instantiateServices[MLReadable]()"]
        FT --> LoadEF["JarLoadingUtils.instantiateServices[ExperimentFuzzing]()"]
        FT --> LoadSF["JarLoadingUtils.instantiateServices[SerializationFuzzing]()"]
        FT --> LoadPTF["JarLoadingUtils.instantiateServices[PyTestFuzzing]()"]
        FT --> LoadRTF["JarLoadingUtils.instantiateServices[RTestFuzzing]()"]
    end
    
    subgraph "Discovered Components"
        LoadPS --> PS["pipelineStages: List[PipelineStage]"]
        LoadReaders --> Readers["readers: List[MLReadable]"]
        LoadEF --> EF["experimentFuzzers"]
        LoadSF --> SF["serializationFuzzers"]
        LoadPTF --> PTF["pytestFuzzers"]
        LoadRTF --> RTF["rtestFuzzers"]
    end
    
    subgraph "Test Methods"
        PS --> ExpTest["test: Verify stage fitting and transforming"]
        PS --> SerTest["test: Verify all stages can be serialized"]
        PS --> PyTest["test: Verify all stages can be tested in python"]
        PS --> RTest["test: Verify all stages can be tested in R"]
        PS --> NamingTest["test: Verify pipeline stage values match param names"]
        PS --> MixinTest["test: Verify correct use of mixins"]
        PS --> LogTest["test: Verify correct use of logging APIs"]
    end
```

The `FuzzingTest` class uses lazy evaluation to discover components at runtime, matching each `PipelineStage` implementation with its corresponding fuzzing test implementation using reflection.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:422-436]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:28-34]()

## Test Validation Categories

### Stage Fitting and Transforming

The test `"Verify stage fitting and transforming"` ensures that each `PipelineStage` has a corresponding `ExperimentFuzzing` implementation. It validates that:

1. Every applicable `PipelineStage` can be matched to an `ExperimentFuzzing[_]` instance
2. The fuzzing implementation exercises the component's fit/transform workflow
3. The component produces valid output DataFrames

The test uses reflection to extract the generic type parameter from each fuzzer's `experimentTestObjects()` method to map fuzzers to stages.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:36-96]()

### Serialization Compliance

The test `"Verify all stages can be serialized"` validates that all `PipelineStage with MLWritable` implementations have corresponding `SerializationFuzzing` tests. This ensures components can be:

1. Saved to disk using Spark's MLWriter interface
2. Loaded back using the component's MLReadable companion object
3. Used identically after deserialization

Components exempt from this test are typically base classes or abstract implementations not meant to be directly serialized.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:98-158]()

### Python SDK Compatibility

The test `"Verify all stages can be tested in python"` checks that Python wrappers exist and function correctly for each `PipelineStage`. The `PyTestFuzzing` interface generates Python test files that validate:

- Component initialization from Python
- Parameter setting via Python API
- Serialization round-trips through Python SDK

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:160-212]()

### R SDK Compatibility

The test `"Verify all stages can be tested in R"` validates R wrapper functionality through `RTestFuzzing` implementations. Similar to Python, this ensures the R SDK can properly interact with the underlying Scala components.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:220-272]()

## Interface and Convention Validation

### Parameter Naming Validation

The test `"Verify all pipeline stage values match their param names"` uses reflection to ensure that `Param[_]` field names match the parameter's logical name. For example, a field `val inputCol` must have `param.name == "inputCol"`.

This validation prevents inconsistencies between the Scala field name and the parameter's public API name.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:288-308]()

### Mixin Trait Enforcement

The test `"Verify correct use of mixins"` validates that components with specific parameter names implement the corresponding trait:

| Parameter Name | Required Trait |
|----------------|----------------|
| inputCol | `HasInputCol` |
| outputCol | `HasOutputCol` |
| labelCol | `HasLabelCol` |
| featuresCol | `HasFeaturesCol` |

This ensures consistent interfaces across the codebase and enables polymorphic usage of components.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:310-368]()

### Logging API Validation

The test `"Verify correct use of logging APIs"` ensures all `PipelineStage` implementations:

1. Extend the `SynapseMLLogging` trait
2. Call `logClass()` in their constructor

The framework checks `SynapseMLLogging.LoggedClasses` to verify that each component registered itself during instantiation.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:370-389]()

### Authentication Interface Validation

The test `"Verify all classes extending HasSubscriptionKey also extend HasAADToken"` enforces that Azure AI service components support both subscription key and Azure AD token authentication methods.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:391-410]()

## Exemption System

The fuzzing framework maintains explicit exemption lists for components that cannot comply with standard validation rules. Each test maintains its own `exemptions: Set[String]` containing fully-qualified class names.

### Common Exemption Patterns

```mermaid
graph TB
    subgraph "Exemption Categories"
        BaseClass["Abstract Base Classes"] --> Examples1["TestEstimatorBase<br/>StandardParamTest"]
        Models["Pre-trained Models"] --> Examples2["LightGBMClassificationModel<br/>VowpalWabbitRegressionModel"]
        Legacy["Legacy Components"] --> Examples3["TextAnalyze<br/>DocumentTranslator"]
        Special["Special Purpose"] --> Examples4["BestModel<br/>TuneHyperparameters"]
    end
    
    subgraph "Test Types with Exemptions"
        ExpTest["Experiment Fuzzing"] --> ExpExempt["exemptions: Set[String]"]
        SerTest["Serialization Fuzzing"] --> SerExempt["exemptions: Set[String]"]
        PyTest["Python Fuzzing"] --> PyExempt["exemptions: Set[String]"]
        RTest["R Fuzzing"] --> RExempt["exemptions: Set[String]"]
    end
```

Exemptions typically apply to:
- Abstract base classes used only for testing
- Models that are generated by estimators (not directly instantiable)
- Components with non-standard serialization requirements
- Legacy components being phased out

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:37-80]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:99-140]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:161-198]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:221-259]()

## Test Execution Flow

```mermaid
graph TB
    subgraph "Test Initialization"
        FT["FuzzingTest class loads"] --> LS["Lazy val: spark session starts"]
        LS --> LP["Lazy val: pipelineStages = JarLoadingUtils.instantiateServices[PipelineStage]()"]
        LP --> LR["Lazy val: readers = JarLoadingUtils.instantiateServices[MLReadable]()"]
        LR --> LF["Lazy val: *Fuzzers = JarLoadingUtils.instantiateServices[*Fuzzing]()"]
    end
    
    subgraph "Test Assertions"
        Test1["test: Assert things have been loaded"] --> Check1["assert serializationFuzzers.nonEmpty"]
        Test1 --> Check2["assert pipelineStages.nonEmpty"]
        Test1 --> Check3["assert readers.nonEmpty"]
    end
    
    subgraph "Validation Tests"
        Check3 --> VT1["test: Verify stage fitting and transforming"]
        Check3 --> VT2["test: Verify all stages can be serialized"]
        Check3 --> VT3["test: Verify all stages can be tested in python"]
        Check3 --> VT4["test: Verify all stages can be tested in R"]
        Check3 --> VT5["test: Verify pipeline stage values match param names"]
        Check3 --> VT6["test: Verify correct use of mixins"]
        Check3 --> VT7["test: Verify correct use of logging APIs"]
    end
```

The test suite uses lazy evaluation to defer expensive operations until needed. The `spark` session triggers initialization, which cascades to component discovery. Each test method filters `pipelineStages` by exemptions and validates that required fuzzers exist.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:28-34]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala:422-436]()

## Implementation Details

### TestObject Structure

The `TestObject` class is a fundamental building block that provides test data for different types of fuzzing tests:

```scala
class TestObject[S <: PipelineStage](
  val stage: S,
  fitDFArg: => DataFrame,
  transDFArg: => DataFrame,
  validateDFArg: => Option[DataFrame]
) {
  lazy val fitDF: DataFrame = fitDFArg
  lazy val transDF: DataFrame = transDFArg
  lazy val validateDF: Option[DataFrame] = validateDFArg
  
  // Convenience constructors
  def this(stage: S, df: => DataFrame) = { this(stage, df, df, None) }
  def this(stage: S, fitDF: => DataFrame, transDF: => DataFrame) = {
    this(stage, fitDF, transDF, None)
  }
}
```

This class encapsulates:
- The pipeline stage to test
- DataFrames for fitting the stage
- DataFrames for transforming
- Optional DataFrames for validation

The lazy evaluation of DataFrames prevents unnecessary computation during test setup.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:35-52]()

### Fuzzing Trait

The `Fuzzing` trait combines all types of fuzzing into a comprehensive testing interface:

```scala
trait Fuzzing[S <: PipelineStage with MLWritable] extends SerializationFuzzing[S]
  with ExperimentFuzzing[S] with PyTestFuzzing[S]
  with RTestFuzzing[S] with GetterSetterFuzzing[S] {

  def testObjects(): Seq[TestObject[S]]
  
  def pyTestObjects(): Seq[TestObject[S]] = testObjects()
  def rTestObjects(): Seq[TestObject[S]] = testObjects()
  def serializationTestObjects(): Seq[TestObject[S]] = testObjects()
  def experimentTestObjects(): Seq[TestObject[S]] = testObjects()
  def getterSetterTestObject(): TestObject[S] = testObjects().head
}
```

This trait simplifies the implementation of comprehensive tests by allowing test classes to provide a single set of test objects that can be used for all types of fuzzing tests.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala:604-630]()

## Summary

The Fuzzing Tests framework in SynapseML provides a comprehensive testing solution that ensures:

1. Pipeline stages work correctly in all supported languages (Scala, Python, R)
2. Components can be properly serialized and deserialized
3. Parameter handling follows consistent patterns
4. Interface implementations adhere to expected standards
5. Naming conventions are consistently applied

By automating these tests and integrating them with the SDK generation process, SynapseML maintains high quality and consistency across its multi-language ecosystem.

Sources:
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala]()
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/Fuzzing.scala]()
- [project/CodegenPlugin.scala]()

---

# Page: Core Functionality

# Core Functionality

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



## Purpose and Scope

This document covers the shared infrastructure and utilities that form the foundation of SynapseML. These components provide cross-cutting concerns used by all higher-level modules including AI services, machine learning algorithms, and data processing components. The core functionality includes platform-aware logging, HTTP communication infrastructure, parameter management, secret retrieval, and custom Spark data sources.

For information about specific ML services that use these core utilities, see [AI Services Integration](#6). For deployment platform configurations, see [Deployment](#8).

---

## System Architecture

The core functionality is organized around five major subsystems that provide essential services to all SynapseML components:

```mermaid
graph TB
    subgraph "Core Infrastructure"
        Logging["SynapseMLLogging<br/>Trait & Object"]
        HTTP["HTTPClient System<br/>Async/Sync Implementations"]
        Params["Parameter Management<br/>Global & Service Params"]
        Secrets["Secret Management<br/>TokenLibrary"]
        DataSources["Custom Data Sources<br/>FileFormat Extensions"]
    end
    
    subgraph "Platform Detection"
        PlatformDetails["PlatformDetails<br/>currentPlatform()"]
        FabricClient["FabricClient<br/>Workload Endpoints"]
    end
    
    subgraph "Supporting Components"
        Scrubber["SASScrubber<br/>Token Filtering"]
        CertifiedEvents["CertifiedEventClient<br/>Fabric Telemetry"]
        TokenLib["TokenLibrary<br/>Reflection-based Auth"]
        HandlingUtils["HandlingUtils<br/>Retry Logic"]
    end
    
    subgraph "External Dependencies"
        Spark["Apache Spark<br/>Session & Context"]
        Azure["Azure Services<br/>Key Vault, Blob, etc"]
        Fabric["Microsoft Fabric<br/>Trident Runtime"]
    end
    
    Logging --> PlatformDetails
    Logging --> Scrubber
    Logging --> CertifiedEvents
    
    HTTP --> HandlingUtils
    HTTP --> Spark
    
    CertifiedEvents --> FabricClient
    FabricClient --> TokenLib
    FabricClient --> PlatformDetails
    
    Secrets --> TokenLib
    Secrets --> Azure
    Secrets --> Fabric
    
    PlatformDetails --> Spark
    TokenLib --> Fabric
    
    DataSources --> Spark
    
    style Logging fill:#f9f9f9
    style HTTP fill:#f9f9f9
    style PlatformDetails fill:#f9f9f9
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](), [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala]()

---

## Logging System

### Overview

The logging system provides platform-aware telemetry with automatic sensitive information scrubbing and optional integration with Microsoft Fabric's certified events system. It consists of the `SynapseMLLogging` trait for component instrumentation and supporting utilities for platform detection and data sanitization.

### Core Components

```mermaid
graph TB
    subgraph "Public API"
        Trait["SynapseMLLogging Trait<br/>uid: String"]
        Object["SynapseMLLogging Object<br/>Singleton Utilities"]
    end
    
    subgraph "Implementation"
        logBase["logBase(methodName, numCols,<br/>executionSeconds, featureName)"]
        logVerb["logVerb[T](verb, f, columns)"]
        logFit["logFit[T](f, columns)"]
        logTransform["logTransform[T](f, columns)"]
        logClass["logClass(featureName)"]
    end
    
    subgraph "Data Collection"
        getPayload["getPayload()<br/>RequiredLogFields"]
        getHadoopConfEntries["getHadoopConfEntries()<br/>Fabric Context"]
    end
    
    subgraph "Sanitization"
        Scrubber["SASScrubber.scrub()<br/>Regex Pattern Matching"]
    end
    
    subgraph "Platform-Specific"
        CertifiedEvents["logToCertifiedEvents()<br/>Fabric Only"]
        PlatformDetails["PlatformDetails.runningOnFabric()"]
    end
    
    Trait --> logFit
    Trait --> logTransform
    Trait --> logClass
    
    logFit --> logVerb
    logTransform --> logVerb
    logClass --> logBase
    
    logVerb --> logBase
    logBase --> getPayload
    logBase --> CertifiedEvents
    
    getPayload --> getHadoopConfEntries
    
    Object --> Scrubber
    Object --> getHadoopConfEntries
    
    CertifiedEvents --> PlatformDetails
    
    style Trait fill:#f9f9f9
    style Scrubber fill:#f9f9f9
    style CertifiedEvents fill:#f9f9f9
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:19-172](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:1-25]()

### SynapseMLLogging Trait

Components that want logging capabilities mix in the `SynapseMLLogging` trait, which requires a `uid: String` field and provides instrumented execution methods:

| Method | Purpose | Logged Fields |
|--------|---------|---------------|
| `logClass(featureName)` | Log component instantiation | className, uid, featureName |
| `logFit[T](f, columns)` | Wrap estimator fitting | executionSeconds, numCols |
| `logTransform[T](f, columns)` | Wrap transformer execution | executionSeconds, numCols |
| `logVerb[T](verb, f, columns)` | Generic verb logging | verb, executionSeconds, numCols |

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:94-172]()

### Log Payload Structure

Every log entry contains:

```
RequiredLogFields:
- modelUid: String          // Component instance identifier
- className: String         // Fully qualified class name
- method: String            // Method being executed (fit, transform, etc)
- libraryVersion: String    // BuildInfo.version
- libraryName: "SynapseML"
- protocolVersion: "0.0.1"

Optional Fields:
- dfInfo: JSON              // {"input": {"numCols": N}}
- executionSeconds: Double  // Execution time
- errorType: String         // Exception class name
- errorMessage: String      // Exception message

Fabric Context (when available):
- artifactId, workspaceId, capacityId, tenantId, lakehouseId, livyId, artifactType
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:19-47](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:98-113]()

### Hadoop Configuration Extraction

The system extracts Fabric-specific identifiers from Hadoop configuration when running in Microsoft Fabric:

```
HadoopKeysToLog:
trident.artifact.id       -> artifactId
trident.workspace.id      -> workspaceId
trident.capacity.id       -> capacityId
trident.artifact.workspace.id -> artifactWorkspaceId
trident.lakehouse.id      -> lakehouseId
trident.activity.id       -> livyId
trident.artifact.type     -> artifactType
trident.tenant.id         -> tenantId
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:52-73]()

### SASScrubber: Sensitive Data Filtering

The `SASScrubber` removes Shared Access Signature (SAS) tokens from log messages using regex pattern matching:

```
Pattern: (?i)sig=[a-z0-9%]{43,63}%3d
Replacement: sig=####
```

This pattern matches URL-encoded Azure Blob Storage SAS signatures (43-63 characters of base64, ending with `%3d` which is URL-encoded `=`).

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:19-24](), [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala:10-33]()

### Platform Detection

The `PlatformDetails` object identifies the execution environment:

| Platform | Detection Method | Constant |
|----------|-----------------|----------|
| Fabric | File exists: `/home/trusted-service-user/.trident-context` | `PlatformSynapseInternal` |
| Synapse | `AZURE_SERVICE == "Microsoft.ProjectArcadia"` + cluster type check | `PlatformSynapse` |
| Databricks | Directory exists: `/dbfs` | `PlatformDatabricks` |
| Binder | Environment variable: `BINDER_LAUNCH_HOST` | `PlatformBinder` |
| Unknown | None of the above | `PlatformUnknown` |

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:8-47]()

### Fabric Certified Events

When running on Microsoft Fabric, the system sends telemetry to the Fabric certified events endpoint:

```mermaid
graph LR
    Component["SynapseML Component<br/>logClass(featureName)"] --> logBase["logBase()<br/>Async Future"]
    logBase --> CertifiedEventClient["CertifiedEventClient<br/>logToCertifiedEvents()"]
    CertifiedEventClient --> Check["runningOnFabric()<br/>Platform Check"]
    Check -->|true| Build["Build Payload<br/>timestamp, feature_name, activity_name"]
    Build --> Post["FabricClient.usagePost()<br/>MLWorkloadEndpointAdmin/telemetry"]
    Check -->|false| Skip["Skip Telemetry"]
    
    style CertifiedEventClient fill:#f9f9f9
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:13-35](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140]()

### Usage Example

```scala
class MyEstimator extends Estimator with SynapseMLLogging {
  val uid: String = Identifiable.randomUID("MyEstimator")
  
  logClass(FeatureNames.MyFeature)  // Log instantiation
  
  override def fit(dataset: Dataset[_]): MyModel = {
    logFit({
      // Training logic here
      new MyModel(uid)
    }, dataset.columns.length)
  }
}
```

**Sources:** Examples from [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala:29-30](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:22-23]()

---

## HTTP Client System

### Overview

The HTTP client infrastructure provides robust, distributed HTTP request handling with connection pooling, configurable timeouts, retry logic with backoff, and both asynchronous and synchronous execution modes. All HTTP-based services in SynapseML (OpenAI, Cognitive Services, etc.) use this infrastructure.

### Client Architecture

```mermaid
graph TB
    subgraph "Client Hierarchy"
        BaseClient["BaseClient[Client, RequestType, ResponseType]<br/>Abstract Base"]
        HTTPClient["HTTPClient Trait<br/>CloseableHttpClient"]
        AsyncClient["AsyncClient<br/>Future-based Execution"]
        SingleThreaded["SingleThreadedClient<br/>Synchronous Execution"]
    end
    
    subgraph "Concrete Implementations"
        AsyncHTTP["AsyncHTTPClient<br/>handler, concurrency, timeout"]
        SingleHTTP["SingleThreadedHTTPClient<br/>handler, requestTimeout"]
    end
    
    subgraph "Handler Functions"
        Handler["Handler Trait<br/>handle(client, request)"]
        HandlingUtils["HandlingUtils Object<br/>basic(), advanced()"]
    end
    
    subgraph "Infrastructure"
        ConnectionPool["PoolingHttpClientConnectionManager<br/>MaxTotal=Int.MaxValue"]
        RequestConfig["RequestConfig<br/>Timeouts"]
        InternalClient["HttpClientBuilder<br/>Apache HTTP Client"]
    end
    
    subgraph "Request Processing"
        RequestWithContext["RequestWithContext<br/>(HTTPRequestData, context)"]
        ResponseWithContext["ResponseWithContext<br/>(HTTPResponseData, context)"]
    end
    
    BaseClient --> HTTPClient
    HTTPClient --> AsyncClient
    HTTPClient --> SingleThreaded
    
    AsyncClient --> AsyncHTTP
    SingleThreaded --> SingleHTTP
    
    AsyncHTTP --> Handler
    SingleHTTP --> Handler
    
    Handler --> HandlingUtils
    
    HTTPClient --> ConnectionPool
    HTTPClient --> RequestConfig
    HTTPClient --> InternalClient
    
    AsyncHTTP --> RequestWithContext
    AsyncHTTP --> ResponseWithContext
    
    style HTTPClient fill:#f9f9f9
    style HandlingUtils fill:#f9f9f9
    style ConnectionPool fill:#f9f9f9
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:21-203]()

### HTTPClient Trait

The `HTTPClient` trait provides the foundation for all HTTP communication:

| Component | Type | Purpose |
|-----------|------|---------|
| `internalClient` | `CloseableHttpClient` | Apache HTTP client with pooling |
| `connectionManager` | `PoolingHttpClientConnectionManager` | Connection reuse across requests |
| `requestConfig` | `RequestConfig` | Timeout configuration |
| `requestTimeout` | `Int` | Milliseconds for connect, request, socket timeouts |

**Configuration:**
- `setDefaultMaxPerRoute(Int.MaxValue)` - Spark handles threading limits
- `setMaxTotal(Int.MaxValue)` - No artificial connection limit
- All three timeout types use the same `requestTimeout` value

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:27-63]()

### Retry Logic and Error Handling

The `HandlingUtils.sendWithRetries` method implements sophisticated retry behavior:

```mermaid
graph TD
    Start["client.execute(request)"] --> Check["Check Status Code"]
    
    Check -->|"200, 201, 202"| Success["Return Response"]
    Check -->|429| RateLimit["Extract Retry-After Header"]
    Check -->|"Other 4xx"| NoRetry["Return Response<br/>Don't Retry"]
    Check -->|"5xx or IOException"| Retry["Retry Logic"]
    
    RateLimit --> Sleep["Thread.sleep(header * 1000)"]
    Sleep --> RecurseNoDecrement["sendWithRetries()<br/>Same retriesLeft"]
    
    Retry --> CheckRetries{"retriesLeft.isEmpty?"}
    CheckRetries -->|true| Throw["Throw Exception"]
    CheckRetries -->|false| SleepBackoff["Thread.sleep(retriesLeft.head)"]
    SleepBackoff --> RecurseDecrement["sendWithRetries()<br/>retriesLeft.tail"]
    
    style RateLimit fill:#f9f9f9
    style Retry fill:#f9f9f9
```

**Retry Behavior:**
- **429 (Rate Limited):** Wait for `Retry-After` seconds, retry without decrementing retry count
- **5xx errors:** Sleep for specified duration, retry with decremented count
- **4xx errors:** No retry (except 429)
- **IOException:** Retry with backoff
- **extraCodesToRetry:** Optional parameter for custom retry codes

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:74-146]()

### Handler Functions

`HandlingUtils` provides two handler factories:

| Handler | Retry Times | Logging | UDF Available |
|---------|-------------|---------|---------------|
| `basic()` | None | No | Yes: `basicUDF` |
| `advanced(retryTimes*)` | Configurable array | Yes (debug & message) | Yes: `advancedUDF(retryTimes*)` |

The `advanced` handler logs:
- Debug: Full request payload (POST body or URI)
- Info: Completion time in milliseconds

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:148-182]()

### Async vs Sync Execution

**AsyncHTTPClient:**
```
Parameters:
- handler: HandlerFunc               // basic or advanced
- concurrency: Int                   // Max parallel requests
- timeout: Duration                  // Overall operation timeout
- requestTimeout: Int                // Per-request timeout
- implicit ec: ExecutionContext      // Thread pool

Usage: Batched requests with Future-based execution
```

**SingleThreadedHTTPClient:**
```
Parameters:
- handler: HandlerFunc               // basic or advanced  
- requestTimeout: Int                // Per-request timeout

Usage: Sequential request processing, simpler lifecycle
```

Both implement `blocking {}` around the handler to signal potential blocking operations to the execution context.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:184-202]()

### Integration with SynapseML Components

HTTP clients are used by:
- **OpenAI Services:** Chat, completion, embedding endpoints
- **Cognitive Services:** Vision, text, speech APIs
- **Azure AI Foundry:** Model endpoint invocation
- **Custom HTTP transformers:** Distributed HTTP serving

Example instantiation pattern:
```scala
val handler = HandlingUtils.advanced(100, 500, 1000)  // Retry at 100ms, 500ms, 1s
val client = new AsyncHTTPClient(
  handler, 
  concurrency = 10,
  timeout = Duration(300, SECONDS),
  requestTimeout = 60000
)(ExecutionContext.global)
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:1-203]()

---

## Parameter Management

### Overview

SynapseML provides a parameter management system that enables global defaults for service configurations while allowing per-instance overrides. This is particularly important for services like OpenAI where parameters like `deployment_name` or `temperature` may be shared across multiple components.

### System Components

```mermaid
graph TB
    subgraph "Parameter Types"
        ServiceParam["ServiceParam[T]<br/>Column or Scalar Value"]
        GlobalParams["GlobalParams Object<br/>Shared Defaults"]
        OpenAIDefaults["OpenAIDefaults Object<br/>Static Setters"]
    end
    
    subgraph "Resolution Flow"
        GetValue["getValue(row)"] --> CheckLocal{"Local Param Set?"}
        CheckLocal -->|Yes| ReturnLocal["Return Local Value"]
        CheckLocal -->|No| CheckGlobal{"Global Default Set?"}
        CheckGlobal -->|Yes| ReturnGlobal["Return Global Value"]
        CheckGlobal -->|No| ReturnDefault["Return Param Default"]
    end
    
    subgraph "Usage Pattern"
        ComponentInit["Component Initialization"] --> SetGlobal["Set Global Defaults<br/>Optional"]
        SetGlobal --> CreateInstance["Create Component Instance"]
        CreateInstance --> SetLocal["Set Local Params<br/>Overrides"]
        SetLocal --> Execute["Execute Transform/Fit"]
    end
    
    ServiceParam --> GetValue
    GlobalParams --> CheckGlobal
    
    style ServiceParam fill:#f9f9f9
    style GlobalParams fill:#f9f9f9
```

**Note:** Specific implementation files for `ServiceParam` and `GlobalParams` were not included in the provided file list, but these concepts are referenced in the OpenAI and Cognitive Services implementations.

### ServiceParam Pattern

The `ServiceParam[T]` class enables parameters to be specified as either:
1. **Column name** (String): Extract value from DataFrame column
2. **Scalar value** (T): Use same value for all rows

This pattern is used extensively in cognitive services and OpenAI integrations to allow batch processing with row-specific or shared parameter values.

---

## Secret Management

### Overview

SynapseML provides platform-agnostic secret retrieval that adapts to the execution environment. The system uses the `TokenLibrary` for Microsoft Fabric authentication and can integrate with Azure Key Vault, Databricks secrets, or other credential stores.

### FabricClient and TokenLibrary

```mermaid
graph TB
    subgraph "FabricClient Object"
        Context["Lazy Initialization<br/>Read Fabric Context Files"]
        ContextFile["/home/trusted-service-user/<br/>.trident-context"]
        SparkConf["/opt/spark/conf/<br/>spark-defaults.conf"]
        ClusterInfo["/opt/health-agent/conf/<br/>cluster-info.json"]
        
        Properties["Extracted Properties<br/>CapacityID, WorkspaceID, ArtifactID"]
        Endpoints["ML Workload Endpoints<br/>ML, LLMPlugin, Automatic, Registry, Admin"]
    end
    
    subgraph "TokenLibrary Reflection"
        GetAccessToken["getAccessToken()<br/>ML Workload Token"]
        GetMwcToken["getSparkMwcToken()<br/>Cognitive Services Token"]
        Reflection["Scala Reflection API<br/>com.microsoft.azure.trident.tokenlibrary"]
    end
    
    subgraph "Token Headers"
        AADHeader["getMLWorkloadAADAuthHeader()<br/>Bearer + Access Token"]
        MwcHeader["getCognitiveMwcTokenAuthHeader()<br/>MwcToken + Workspace Token"]
    end
    
    Context --> ContextFile
    Context --> SparkConf
    Context --> ClusterInfo
    
    ContextFile --> Properties
    SparkConf --> Properties
    ClusterInfo --> Properties
    
    Properties --> Endpoints
    
    GetAccessToken --> Reflection
    GetMwcToken --> Reflection
    
    GetAccessToken --> AADHeader
    GetMwcToken --> MwcHeader
    
    AADHeader --> Endpoints
    MwcHeader --> Endpoints
    
    style TokenLibrary fill:#f9f9f9
    style FabricClient fill:#f9f9f9
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:1-200](), [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:1-52]()

### Fabric Context Extraction

The `FabricClient` reads configuration from multiple sources:

**File: `.trident-context`**
```
Format: key=value pairs
Example:
trident.capacity.id=<guid>
trident.workspace.id=<guid>
trident.artifact.id=<guid>
```

**File: `spark-defaults.conf`**
```
Format: key value pairs (space-separated)
Example:
spark.trident.pbienv public
trident.lakehouse.tokenservice.endpoint https://...
```

**File: `cluster-info.json`**
```
JSON containing cluster metadata:
{
  "cluster_metadata": {
    "workspace-pe-enabled": "true|false",
    ...
  }
}
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:51-143]()

### Workload Endpoint Construction

FabricClient constructs ML workload endpoints based on environment and private endpoint status:

| Endpoint Type | Path Suffix |
|--------------|-------------|
| `MLWorkloadEndpointML` | `/webapi/capacities/{capacityId}/workloads/ML/ML/Automatic/workspaceid/{workspaceId}/` |
| `MLWorkloadEndpointLLMPlugin` | `/workloads/ML/LlmPlugin/...` |
| `MLWorkloadEndpointAutomatic` | `/workloads/ML/Automatic/...` |
| `MLWorkloadEndpointRegistry` | `/workloads/ML/Registry/...` |
| `MLWorkloadEndpointAdmin` | `/workloads/ML/MLAdmin/...` |
| `MLWorkloadEndpointCognitive` | `{ML endpoint}cognitive/` |
| `MLWorkloadEndpointOpenAI` | `{ML endpoint}cognitive/openai/` |

**Private Endpoint Hosts:**
When `workspace-pe-enabled == true`, hosts are constructed as:
```
https://{cleanedWorkspaceId}.z{first2Chars}.{envMark}c.fabric.microsoft.com
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:23-189]()

### TokenLibrary Reflection

The `TokenLibrary` uses Scala reflection to invoke methods from the Fabric runtime's `com.microsoft.azure.trident.tokenlibrary.TokenLibrary` object:

**getAccessToken:**
```scala
// Invokes: TokenLibrary.getAccessToken("ml")
// Returns: JWT token for ML workload authentication
```

**getSparkMwcToken:**
```scala
// Invokes: TokenLibrary.getMwcToken(workspaceId, artifactId, 2, "SparkCore")
// Parameters: workspace, artifact, version (2), service name
// Returns: MWC token for Cognitive Services
```

This approach allows SynapseML to work with the Fabric runtime without compile-time dependencies on Trident libraries.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:9-51]()

### Authentication Headers

Two authentication patterns are supported:

| Header Type | Format | Usage |
|-------------|--------|-------|
| AAD (Azure AD) | `Bearer {token}` | ML workload endpoints, general Azure resources |
| MWC (Microsoft Workload Context) | `MwcToken {token}` | Cognitive Services through Fabric proxy |

Both are constructed with unique request IDs and workload resource monikers for telemetry correlation.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:145-152](), [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:47-51]()

---

## Custom Spark Data Sources

### Overview

SynapseML extends Apache Spark's data source API with custom `FileFormat` implementations that provide enhanced capabilities for reading images, binary files, and HTTP streams. These formats include retry mechanisms, zip archive support, and workarounds for known Spark issues.

### Data Source Types

| Format | Purpose | Key Features |
|--------|---------|--------------|
| ImageFileFormat | Read images as DataFrames | Retry on flaky image decoding, origin tracking |
| BinaryFileFormat | Read binary files | Zip archive support, recursive directory traversal |
| HTTPSource | Distributed HTTP server | Structured streaming source for serving models |
| HTTPSink | HTTP client streaming | Structured streaming sink for writing via HTTP |

**Note:** Specific implementation files for these custom formats were not included in the provided file list, but they are referenced in the system documentation and form part of the core I/O functionality.

### Image File Format

The custom image format addresses flakiness in Spark's built-in image decoder by implementing retry logic and better error handling. It supports common image formats (JPEG, PNG, etc.) and preserves file origin metadata for downstream processing.

### Binary File Format with Zip Support

Extends Spark's binary file reading to transparently handle zip archives, allowing datasets distributed as compressed files to be read without manual extraction. This is particularly useful for model artifacts and pre-processed feature sets.

### HTTP Sources and Sinks

These components enable SynapseML models to be deployed as distributed HTTP endpoints or to write results via HTTP in streaming contexts, integrating machine learning pipelines with web services and APIs.

---

## Usage Patterns Across SynapseML

The core infrastructure is used consistently across all SynapseML components:

```mermaid
graph TB
    subgraph "Example: VowpalWabbitClassifier"
        VWClass["VowpalWabbitClassifier<br/>class"] --> MixinLog["with SynapseMLLogging"]
        MixinLog --> Constructor["Constructor<br/>logClass(FeatureNames.VowpalWabbit)"]
        Constructor --> Fit["fit(dataset)<br/>logFit({...}, columns.length)"]
    end
    
    subgraph "Example: OpenAIChatCompletion"
        OpenAIClass["OpenAIChatCompletion<br/>class"] --> MixinLog2["with SynapseMLLogging"]
        MixinLog2 --> Constructor2["Constructor<br/>logClass(FeatureNames.OpenAI)"]
        Constructor2 --> Transform["transform(dataset)<br/>Uses AsyncHTTPClient"]
        Transform --> HTTPHandler["HandlingUtils.advanced(100, 500, 1000)"]
    end
    
    subgraph "Example: CertifiedEventClient"
        Service["Fabric-based Service"] --> CheckPlatform["PlatformDetails.runningOnFabric()"]
        CheckPlatform -->|true| BuildPayload["Build Telemetry Payload"]
        BuildPayload --> GetToken["TokenLibrary.getAccessToken()"]
        GetToken --> SendTelemetry["FabricClient.usagePost()"]
    end
    
    style MixinLog fill:#f9f9f9
    style HTTPHandler fill:#f9f9f9
    style CheckPlatform fill:#f9f9f9
```

**Sources:** [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala:29-30](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:22-23](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala:28-29]()

---

## Summary

The core functionality provides battle-tested infrastructure for:

1. **Observability:** Platform-aware logging with automatic sanitization and optional Fabric telemetry
2. **Reliability:** HTTP retry logic with exponential backoff and rate limit handling
3. **Portability:** Platform detection and authentication abstraction
4. **Performance:** Connection pooling and async execution for HTTP-heavy workloads
5. **Security:** Automatic scrubbing of SAS tokens and secrets from logs

All higher-level SynapseML components depend on these core utilities, ensuring consistent behavior across different deployment environments (Synapse, Fabric, Databricks, standalone Spark) and providing unified telemetry for debugging and monitoring.

---

# Page: Logging System

# Logging System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py](cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py](cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/test_simple.py](cognitive/src/test/python/synapsemltest/services/test_simple.py)
- [core/src/main/python/synapse/ml/core/init_spark.py](core/src/main/python/synapse/ml/core/init_spark.py)
- [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py](core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py)
- [core/src/main/python/synapse/ml/core/logging/__init__.py](core/src/main/python/synapse/ml/core/logging/__init__.py)
- [core/src/main/python/synapse/ml/core/platform/Platform.py](core/src/main/python/synapse/ml/core/platform/Platform.py)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/python/synapsemltest/core/test_logging.py](core/src/test/python/synapsemltest/core/test_logging.py)
- [core/src/test/python/synapsemltest/core/test_template.py](core/src/test/python/synapsemltest/core/test_template.py)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [docs/Get Started/Set up Cognitive Services.ipynb](docs/Get Started/Set up Cognitive Services.ipynb)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



The Logging System in SynapseML provides a platform-aware framework for recording operations, events, and errors across the library. It implements decorator-based method execution tracking, structured logging with timing metrics, and platform-specific telemetry integration. The system includes security measures to scrub sensitive information from logs.

For information about the HTTP communication infrastructure, see [HTTP Client System](#5.2). For parameter management, see [Parameter Management](#5.3). For platform detection details, see [Platform Detection and Adaptation](#2.3).

## Overview and Architecture

The SynapseML Logging System provides both Scala and Python implementations that share a common structured logging format. The system adapts to the execution platform (Fabric, Synapse, Databricks) and provides method decorators for automatic execution tracking and timing.

**Architecture Diagram: Logging System Components**

```mermaid
flowchart TD
    subgraph Scala["Scala Implementation"]
        SynapseMLLoggingTrait["SynapseMLLogging trait<br/>core/logging/SynapseMLLogging.scala"]
        SynapseMLLoggingObject["SynapseMLLogging object<br/>Singleton utilities"]
    end
    
    subgraph Python["Python Implementation"]
        SynapseMLLogger["SynapseMLLogger class<br/>core/logging/SynapseMLLogger.py"]
        Decorators["@log_verb, @log_verb_static<br/>Method decorators"]
    end
    
    subgraph SharedInfra["Shared Infrastructure"]
        PlatformDetails["PlatformDetails<br/>Platform detection"]
        SASScrubber["SASScrubber<br/>Token scrubbing"]
        CertifiedEvents["CertifiedEventClient<br/>Fabric telemetry"]
    end
    
    subgraph LogOutput["Log Output"]
        SparkLogger["Spark Logging<br/>Standard output"]
        MDSLogger["MDS Logger<br/>Fabric/Synapse"]
        JSONLogs["JSON structured logs"]
    end
    
    SynapseMLLoggingTrait --> PlatformDetails
    SynapseMLLogger --> PlatformDetails
    
    SynapseMLLoggingObject --> SASScrubber
    SynapseMLLogger --> SASScrubber
    
    SynapseMLLoggingTrait --> CertifiedEvents
    SynapseMLLogger --> CertifiedEvents
    
    SynapseMLLoggingTrait --> SparkLogger
    SynapseMLLogger --> MDSLogger
    
    SparkLogger --> JSONLogs
    MDSLogger --> JSONLogs
    
    Decorators --> SynapseMLLogger
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala]().

## Core Components

### Scala Implementation

The Scala logging system consists of two primary components:

**SynapseMLLogging Object**: A singleton that provides utility functions and maintains global state:
- `LoggedClasses`: Set of all logged class names [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:63]()
- `HadoopKeysToLog`: Map of Hadoop configuration keys to extract [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:52-61]()
- `getHadoopConfEntries()`: Extracts environment metadata from Spark context [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:65-73]()
- `logMessage()`: Logs messages with SAS token scrubbing [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:87-89]()

**SynapseMLLogging Trait**: Mixed into components that need logging capabilities:
- `logClass(featureName)`: Log component initialization [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:148-150]()
- `logFit[T](f, columns)`: Wrap and time model training [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:152-154]()
- `logTransform[T](f, columns)`: Wrap and time data transformation [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:156-158]()
- `logVerb[T](verb, f, columns)`: Generic operation logging with timing [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:160-171]()

**Class Structure Diagram**

```mermaid
classDiagram
    class SynapseMLLogging_Object {
        +LoggedClasses Set~String~
        +HadoopKeysToLog Map~String, String~
        +getHadoopConfEntries() Map
        +logExternalInfo(uid, className, methodName, extraFields)
        +logMessage(message)
        +logDebug(msg)
    }
    
    class SynapseMLLogging_Trait {
        +uid String
        +getPayload(methodName, numCols, executionSeconds, exception) Map
        +logBase(methodName, numCols, executionSeconds, featureName)
        +logErrorBase(methodName, e)
        +logClass(featureName)
        +logFit~T~(f, columns) T
        +logTransform~T~(f, columns) T
        +logVerb~T~(verb, f, columns) T
    }
    
    class RequiredLogFields {
        +uid String
        +className String
        +method String
        +toMap() Map
    }
    
    class RequiredErrorFields {
        +errorType String
        +errorMessage String
        +toMap() Map
    }
    
    SynapseMLLogging_Object --> RequiredLogFields
    SynapseMLLogging_Trait --> RequiredLogFields
    SynapseMLLogging_Trait --> RequiredErrorFields
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:50-92](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:94-172]().

### Python Implementation

The Python logging system provides the `SynapseMLLogger` class with decorator support for automatic method tracking.

**SynapseMLLogger Class**: Main logging class for Python components [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:28-298]()

Key attributes:
- `library_name`: Library name (defaults to "SynapseML") [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:39]()
- `library_version`: Library version extracted from package [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:40-42]()
- `uid`: Unique identifier for the logger instance [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:43]()
- `logger`: Platform-specific logger instance [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:36-38]()
- `is_executor`: Boolean indicating if running on executor [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:44]()

Key methods:
- `_get_environment_logger()`: Returns platform-specific logger (MDS logger for Fabric/Synapse) [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:85-101]()
- `get_hadoop_conf_entries()`: Extracts Fabric context information [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:104-121]()
- `log_message(message)`: Simple message logging [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:156-157]()
- `log_class(feature_name)`: Log class initialization [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:282-283]()

**Python Class Structure Diagram**

```mermaid
classDiagram
    class SynapseMLLogger {
        +library_name str
        +library_version str
        +uid str
        +logger logging.Logger
        +is_executor bool
        +_get_environment_logger(log_level) Logger
        +get_hadoop_conf_entries() dict
        +get_required_log_fields(uid, class_name, method) dict
        +_get_payload(class_name, method_name, num_cols, execution_sec, exception) dict
        +_log_base(class_name, method_name, num_cols, execution_sec, feature_name, custom_log_dict)
        +_log_base_dict(info, feature_name)
        +_log_error_base(class_name, method_name, e)
        +log_message(message)
        +log_class(feature_name)
        +log_verb(method_name, feature_name) decorator
        +log_verb_static(method_name, feature_name, custom_log_function) decorator
        +get_column_number(args, kwargs) int
    }
    
    class CustomFormatter {
        +format(record) str
    }
    
    class Platform {
        +running_on_synapse_internal() bool
        +running_on_synapse() bool
        +running_on_fabric_python() bool
    }
    
    SynapseMLLogger --> CustomFormatter
    SynapseMLLogger --> Platform
```

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:28-298]().

## Decorators for Method Execution Tracking

The Python implementation provides two decorator patterns for automatic method execution tracking with timing metrics.

### Instance Method Decorator: log_verb()

The `log_verb()` decorator is used for classes that inherit from `SynapseMLLogger` [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192-220]().

```python
class SampleTransformer(SynapseMLLogger):
    def __init__(self):
        super().__init__(log_level=logging.DEBUG)
        self.log_class("SampleTransformer")
    
    @SynapseMLLogger.log_transform()
    def transform(self, df):
        # transformation logic
        return result
    
    @SynapseMLLogger.log_fit()
    def fit(self, df):
        # fitting logic
        return result
```

**Decorator Execution Flow**

```mermaid
sequenceDiagram
    participant Client
    participant Decorator as "@log_verb()"
    participant Method as "transform()"
    participant Logger as "self._log_base()"
    
    Client->>Decorator: Call decorated method
    Decorator->>Decorator: Start timing (time.perf_counter)
    Decorator->>Method: Execute method
    Method-->>Decorator: Return result
    Decorator->>Decorator: Calculate execution time
    Decorator->>Decorator: Extract column count from args
    Decorator->>Logger: Log with timing and column count
    Logger->>Logger: Build payload with metadata
    Logger->>Logger: Log JSON to output
    Decorator-->>Client: Return result
    
    Note over Decorator,Logger: On exception: log error and re-raise
```

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192-220](). [core/src/test/python/synapsemltest/core/test_logging.py:16-36]().

### Static Method Decorator: log_verb_static()

The `log_verb_static()` decorator is used for classes that don't inherit from `SynapseMLLogger` but have a `_logger` attribute [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:223-280]().

```python
class NoInheritTransformer:
    def __init__(self):
        self._logger = SynapseMLLogger(log_level=logging.DEBUG)
    
    @SynapseMLLogger.log_verb_static(method_name="transform")
    def transform(self, df):
        return result
    
    @SynapseMLLogger.log_verb_static(
        custom_log_function=custom_logging_function
    )
    def custom_method(self, df):
        return result
```

**Custom Logging Functions**: The `log_verb_static()` decorator accepts an optional `custom_log_function` parameter that receives the method result and can return additional fields to log [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:226-227]().

```python
def custom_logging_function(self, results, *args, **kwargs):
    return {
        "args": f"Arguments: {args}",
        "result": str(results)
    }
```

**Key Decorator Features**:
- Automatic execution timing using `time.perf_counter()` [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:196](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:244]()
- Column count extraction from DataFrame arguments [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:205](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:264]()
- Automatic exception logging and re-raising [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:210-216](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:270-276]()
- Rounding execution time to 3 significant digits [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:199-201]()
- Optional feature name for Fabric telemetry [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192]()

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192-298](). [core/src/test/python/synapsemltest/core/test_logging.py:38-112]().

## Log Structure and Fields

Every log entry includes a standardized set of fields in JSON format to ensure consistent logging across Scala and Python implementations.

### Required Fields

**Core Fields** (always present):
- `modelUid`: Unique identifier for the component instance [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:24]()
- `className`: Fully qualified class name [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:25]()
- `method`: Method name that generated the log [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:26]()
- `libraryVersion`: SynapseML version from BuildInfo [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:27]()
- `libraryName`: Always "SynapseML" [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:28]()
- `protocolVersion`: Logging protocol version ("0.0.1") [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:29](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:16]()

**Execution Metadata** (when available):
- `executionSeconds`: Execution time in seconds [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:108]()
- `dfInfo.input.numCols`: Number of columns in input DataFrame [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:105-107]()
- `isExecutor`: Boolean indicating executor vs driver [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:184]()

**Error Fields** (on exceptions):
- `errorType`: Exception class name [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:34-35]()
- `errorMessage`: Exception message [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:34-35](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:160-161]()

### Platform-Specific Context Fields

When running on Microsoft Fabric or Synapse, additional context fields are extracted from Hadoop configuration:

| Field Name | Hadoop Config Key | Description |
|------------|-------------------|-------------|
| `artifactId` | `trident.artifact.id` | Fabric artifact ID |
| `workspaceId` | `trident.artifact.workspace.id` or `trident.workspace.id` | Workspace identifier |
| `capacityId` | `trident.capacity.id` | Capacity identifier |
| `artifactWorkspaceId` | `trident.artifact.workspace.id` | Artifact workspace ID |
| `livyId` | `trident.activity.id` | Livy activity ID |
| `artifactType` | `trident.artifact.type` | Type of artifact |
| `tenantId` | `trident.tenant.id` | Azure tenant ID |
| `lakehouseId` | `trident.lakehouse.id` | Lakehouse ID |

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:52-73](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:104-121]().

### Example Log Entry

```json
{
  "modelUid": "VowpalWabbitClassifier_a1b2c3d4",
  "className": "com.microsoft.azure.synapse.ml.vw.VowpalWabbitClassifier",
  "method": "fit",
  "libraryVersion": "1.0.0",
  "libraryName": "SynapseML",
  "protocolVersion": "0.0.1",
  "executionSeconds": "12.456",
  "dfInfo": {"input": {"numCols": "15"}},
  "workspaceId": "12345678-1234-1234-1234-123456789012",
  "capacityId": "87654321-4321-4321-4321-210987654321"
}
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:98-113](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:163-185]().

## Platform-Aware Logger Selection

The logging system adapts its output mechanism based on the detected execution platform. This enables integration with platform-specific logging infrastructure.

**Platform Detection Flow**

```mermaid
flowchart TD
    Start["_get_environment_logger()"] --> CheckFabricPython{"running_on_fabric_python()"}
    Start2["currentPlatform()"] --> CheckTridentFile{"/.trident-context<br/>file exists?"}
    
    CheckFabricPython -->|"Yes"| MDSLogger["get_mds_logger()<br/>synapse.ml.pymds.synapse_logger"]
    CheckFabricPython -->|"No"| CheckSynapseInternal{"running_on_synapse_internal()"}
    CheckSynapseInternal -->|"Yes"| MDSLogger
    CheckSynapseInternal -->|"No"| CheckSynapse{"running_on_synapse()"}
    CheckSynapse -->|"Yes"| StandardLogger["logging.getLogger(__name__)<br/>Standard Python logger"]
    CheckSynapse -->|"No"| StandardLogger
    
    CheckTridentFile -->|"Yes"| FabricPlatform["PLATFORM_SYNAPSE_INTERNAL<br/>Fabric environment"]
    CheckTridentFile -->|"No"| CheckAzureService{"AZURE_SERVICE env var<br/>== Microsoft.ProjectArcadia?"}
    CheckAzureService -->|"Yes"| CheckClusterType{"spark.cluster.type"}
    CheckClusterType -->|"synapse"| SynapsePlatform["PLATFORM_SYNAPSE"]
    CheckClusterType -->|"other"| FabricPlatform
    CheckAzureService -->|"No"| CheckDBFS{"/dbfs directory<br/>exists?"}
    CheckDBFS -->|"Yes"| DatabricksPlatform["PLATFORM_DATABRICKS"]
    CheckDBFS -->|"No"| CheckBinder{"BINDER_LAUNCH_HOST<br/>env var exists?"}
    CheckBinder -->|"Yes"| BinderPlatform["PLATFORM_BINDER"]
    CheckBinder -->|"No"| UnknownPlatform["PLATFORM_UNKNOWN"]
```

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:85-101](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:17-47](). [core/src/main/python/synapse/ml/core/platform/Platform.py:17-54]().

### Logger Types by Platform

| Platform | Python Logger | Scala Logger | Special Features |
|----------|--------------|--------------|------------------|
| Fabric (Synapse Internal) | MDS Logger via `synapse.ml.pymds.synapse_logger.get_mds_logger()` [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:87-93]() | Spark Logger | Hadoop config extraction, certified events |
| Synapse | Standard Python `logging.getLogger()` [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:94-97]() | Spark Logger | Basic structured logging |
| Databricks | Standard Python `logging.getLogger()` [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:98-101]() | Spark Logger | No special features |
| Other | Standard Python `logging.getLogger()` | Spark Logger | No special features |

The MDS Logger used on Fabric includes a custom formatter that outputs only the message content without timestamp prefixes [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:19-25]().

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:85-101](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:8-47]().

## Fabric Telemetry Integration

When running on Microsoft Fabric, the logging system sends certified events for usage telemetry tracking.

### Certified Events Mechanism

Certified events are sent asynchronously when a `featureName` is provided to logging methods [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:128-136]().

**Scala Implementation**:
```scala
protected def logBase(info: Map[String, String], featureName: Option[String]): Unit = {
  if (featureName.isDefined) {
    Future {
      logToCertifiedEvents(info("libraryName"), featureName.get)
    }.failed.map {
      case e: Exception => logErrorBase("certifiedEventLogging", e)
    }
  }
  logInfo(info.toJson.compactPrint)
}
```

**Python Implementation**:
```python
def _log_base_dict(self, info: Dict[str, str], feature_name: Optional[str] = None):
    if feature_name is not None and running_on_synapse_internal():
        from synapse.ml.fabric.telemetry_utils import report_usage_telemetry
        report_usage_telemetry(
            feature_name=self.library_name,
            activity_name=feature_name,
            attributes={},
        )
    self.logger.info(json.dumps(info))
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:145-154]().

**Certified Event Flow Diagram**

```mermaid
sequenceDiagram
    participant Component as "ML Component"
    participant Logging as "SynapseMLLogging.logBase()"
    participant Platform as "PlatformDetails.runningOnFabric()"
    participant Events as "CertifiedEventClient.logToCertifiedEvents()"
    participant FabricClient as "FabricClient.usagePost()"
    participant Endpoint as "MLWorkloadEndpointAdmin/telemetry"
    
    Component->>Logging: logClass("VowpalWabbit")
    Logging->>Platform: Check if running on Fabric
    Platform-->>Logging: true
    
    Logging->>Logging: Create Future (async)
    Note over Logging: Continues without blocking
    
    par Async Telemetry
        Logging->>Events: logToCertifiedEvents("SynapseML", "VowpalWabbit")
        Events->>Events: Construct JSON payload<br/>{timestamp, feature_name, activity_name, attributes}
        Events->>FabricClient: usagePost(uri, payload)
        FabricClient->>Endpoint: POST with auth headers
        Endpoint-->>FabricClient: Response
    end
    
    Logging->>Logging: logInfo(JSON payload)
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:13-35](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140]().

### Certified Event Payload

The certified event payload sent to Fabric includes [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:24-30]():
- `timestamp`: Unix epoch timestamp in seconds
- `feature_name`: Library name ("SynapseML")
- `activity_name`: Feature name being logged
- `attributes`: Empty object (reserved for future use)

The endpoint is constructed as: `${FabricClient.MLWorkloadEndpointAdmin}/telemetry` [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:16-18]()

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:13-35](). [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:18](). [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:36]().

## Security: Sensitive Information Scrubbing

The logging system automatically scrubs sensitive information before writing to logs to prevent credential leakage.

### SASScrubber Implementation

The `SASScrubber` object removes Shared Access Signature (SAS) tokens from Azure Storage URLs [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:19-24]().

**Pattern Matching**: Uses regex pattern `(?i)sig=[a-z0-9%]{43,63}%3d` to detect SAS signature parameters [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:21]()

**Replacement**: All matched signatures are replaced with `sig=####` [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:22]()

**Example Transformation**:
```
Before: https://storage.blob.core.windows.net/container/file.zip?sv=2020-10-02&sig=k2N3nSvLtiDH5xfYAwklSfyiuJ42aG8T8hLCNWdtNXk%3D
After:  https://storage.blob.core.windows.net/container/file.zip?sv=2020-10-02&sig=####
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:19-24](). [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala:10-34]().

**Scrubber Integration Diagram**

```mermaid
flowchart TD
    LogCall["logMessage(message)"] --> Scrub["SASScrubber.scrub(message)"]
    Scrub --> RegexMatch{"Regex match<br/>sig=[a-z0-9%]{43,63}%3d"}
    RegexMatch -->|"Match found"| Replace["Replace with sig=####"]
    RegexMatch -->|"No match"| NoChange["Return original message"]
    Replace --> LogOutput["logInfo(scrubbed)"]
    NoChange --> LogOutput
    
    LogOutput --> SparkLogger["Spark Logging Output"]
```

The scrubber is automatically applied in:
- `SynapseMLLogging.logMessage()` [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:87-89]()
- `SynapseMLLogging.logDebug()` [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:91]()
- `HandlingUtils.advanced()` for HTTP request logging [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:156]()

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:8-24](). [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:87-91]().

## Usage Patterns

### Scala: Mixing in SynapseMLLogging Trait

Scala components integrate logging by mixing in the `SynapseMLLogging` trait:

```scala
class VowpalWabbitRegressor(override val uid: String)
  extends BaseRegressor[Row, VowpalWabbitRegressor, VowpalWabbitRegressionModel]
    with VowpalWabbitBaseSpark
    with ComplexParamsWritable 
    with SynapseMLLogging {  // Mix in trait
  
  logClass(FeatureNames.VowpalWabbit)  // Log initialization
  
  override def train(dataset: Dataset[_]): VowpalWabbitRegressionModel = {
    logFit({
      val model = new VowpalWabbitRegressionModel(uid)
        .setFeaturesCol(getFeaturesCol)
        .setPredictionCol(getPredictionCol)
      trainInternal(dataset, model)
    }, dataset.columns.length)
  }
}
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:19-38]().

### Python: Inheriting from SynapseMLLogger

Python components can inherit from `SynapseMLLogger`:

```python
class SampleTransformer(SynapseMLLogger):
    def __init__(self):
        super().__init__(log_level=logging.DEBUG)
        self.log_class("SampleTransformer")
    
    @SynapseMLLogger.log_transform()
    def transform(self, df):
        # transformation logic
        return result
    
    @SynapseMLLogger.log_fit()
    def fit(self, df):
        # fitting logic  
        return result
```

Sources: [core/src/test/python/synapsemltest/core/test_logging.py:16-27]().

### Python: Using _logger Attribute

For classes that can't inherit, use the `_logger` attribute pattern:

```python
class NoInheritTransformer:
    def __init__(self):
        self._logger = SynapseMLLogger(log_level=logging.DEBUG)
    
    @SynapseMLLogger.log_verb_static(method_name="transform")
    def transform(self, df):
        return result
```

Sources: [core/src/test/python/synapsemltest/core/test_logging.py:38-48]().

**Execution Flow with Logging**

```mermaid
sequenceDiagram
    participant Client
    participant Component as "ML Component<br/>(with SynapseMLLogging)"
    participant LogMethod as "logFit() / logTransform()"
    participant Operation as "Actual Operation"
    participant Logger as "Logger Output"
    
    Client->>Component: Call fit(dataset)
    Component->>LogMethod: logFit({ operation }, columns)
    LogMethod->>LogMethod: System.nanoTime() - start
    LogMethod->>Operation: Execute operation
    
    alt Success
        Operation-->>LogMethod: Return result
        LogMethod->>LogMethod: Calculate execution time
        LogMethod->>LogMethod: Build log payload
        LogMethod->>Logger: logInfo(JSON payload)
        LogMethod-->>Component: Return result
        Component-->>Client: Return model
    else Exception
        Operation-->>LogMethod: Throw exception
        LogMethod->>LogMethod: Build error payload
        LogMethod->>Logger: logError(JSON payload, exception)
        LogMethod-->>Component: Re-throw exception
        Component-->>Client: Propagate exception
    end
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:160-171](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192-220]().

### Standard Logging Methods

| Language | Method | Purpose | Timing | Error Handling |
|----------|--------|---------|--------|----------------|
| Scala | `logClass(featureName)` | Log initialization | No | No |
| Scala | `logFit[T](f, columns)` | Log training | Yes | Yes |
| Scala | `logTransform[T](f, columns)` | Log transformation | Yes | Yes |
| Scala | `logVerb[T](verb, f, columns)` | Generic operation | Yes | Yes |
| Scala | `logErrorBase(method, e)` | Log exception | No | N/A |
| Python | `log_class(feature_name)` | Log initialization | No | No |
| Python | `@log_transform()` | Decorator for transform | Yes | Yes |
| Python | `@log_fit()` | Decorator for fit | Yes | Yes |
| Python | `@log_verb(method_name, feature_name)` | Generic decorator | Yes | Yes |
| Python | `@log_verb_static(...)` | Static decorator | Yes | Yes |

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:148-171](). [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:192-290]().

## Integration with External Systems

### HTTP Client Logging

The logging system is used by the HTTP client system to log request/response information and timings:

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant Handler as HandlingUtils
    participant Logging as SynapseMLLogging
    participant Request as HTTP Request
    participant API as External API
    
    Client->>Handler: advanced(retryTimes)(client, request)
    Handler->>Logging: logDebug("sending...")
    Handler->>Logging: Record start time
    Handler->>Request: Send request with retries
    Request->>API: HTTP Request
    API-->>Request: HTTP Response
    Request-->>Handler: Return response
    Handler->>Logging: logMessage("finished sending... took Xms")
    Handler->>Handler: convertAndClose(response)
    Handler-->>Client: Return response data
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:147-168]().

### Implementation in Vowpal Wabbit Components

The logging system is extensively used in Vowpal Wabbit components to track model training and inference:

```mermaid
flowchart TD
    subgraph "Vowpal Wabbit Components with Logging"
        VWContextualBandit["VowpalWabbitContextualBandit"]
        VWClassifier["VowpalWabbitClassifier"]
        VWRegressor["VowpalWabbitRegressor"]
        VWGeneric["VowpalWabbitGeneric"]
        VWFeaturizer["VowpalWabbitFeaturizer"]
    end
    
    SynapseMLLogging["SynapseMLLogging"] --> |"mixed into"| VWContextualBandit
    SynapseMLLogging --> |"mixed into"| VWClassifier
    SynapseMLLogging --> |"mixed into"| VWRegressor
    SynapseMLLogging --> |"mixed into"| VWGeneric
    SynapseMLLogging --> |"mixed into"| VWFeaturizer
    
    FeatureNames["FeatureNames.VowpalWabbit"] --> |"used by"| VWContextualBandit
    FeatureNames --> |"used by"| VWClassifier
    FeatureNames --> |"used by"| VWRegressor
    FeatureNames --> |"used by"| VWGeneric
    FeatureNames --> |"used by"| VWFeaturizer
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:105-111](). [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala:25-31](). [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:19-24](). [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitGeneric.scala:19-25](). [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala:25-30]().

## Summary

The SynapseML Logging System provides:

1. **Structured Logging**: Consistent logging format with standard fields across all components
2. **Performance Metrics**: Automatic timing of key operations like model training and inference
3. **Security**: Scrubbing of sensitive information such as SAS tokens
4. **Platform Integration**: Special handling for different environments (Fabric, Synapse, Databricks)
5. **Usage Tracking**: Integration with Fabric's certified events for telemetry
6. **Error Handling**: Standardized error logging with automatic exception information capture

This system enables comprehensive monitoring, debugging, and usage analysis while ensuring that sensitive information is properly protected.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala]().

---

# Page: HTTP Client System

# HTTP Client System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



## Purpose and Scope

The HTTP Client System provides a robust, distributed HTTP communication layer for SynapseML components. It handles HTTP requests and responses within Spark executors, with features including connection pooling, configurable timeouts, automatic retry logic, and support for both synchronous and asynchronous execution patterns. This system is primarily used by the Cognitive Services module for communicating with Azure AI services, but is available as general infrastructure for any HTTP-based integration.

For information about the logging system that integrates with HTTP clients, see [Logging System](#5.1). For details on how Cognitive Services uses this infrastructure, see [Azure Cognitive Services](#6.2).

## Architecture Overview

```mermaid
graph TB
    subgraph "Client Interfaces"
        Handler["Handler trait<br/>handle()"]
        HTTPClient["HTTPClient trait<br/>AutoCloseable"]
    end
    
    subgraph "Connection Management"
        ConnectionManager["PoolingHttpClientConnectionManager<br/>MaxPerRoute: Int.MaxValue"]
        RequestConfig["RequestConfig<br/>connect/socket/request timeouts"]
        InternalClient["CloseableHttpClient<br/>Apache HttpClient"]
    end
    
    subgraph "Request Processing"
        HandlingUtils["HandlingUtils object"]
        SendWithRetries["sendWithRetries()<br/>Retry array"]
        AdvancedHandler["advanced()<br/>Configurable retries"]
        BasicHandler["basic()<br/>Single attempt"]
    end
    
    subgraph "Client Implementations"
        AsyncHTTPClient["AsyncHTTPClient<br/>concurrency: Int<br/>timeout: Duration"]
        SingleThreadedHTTPClient["SingleThreadedHTTPClient<br/>Sequential execution"]
    end
    
    subgraph "UDF Integration"
        AdvancedUDF["advancedUDF()<br/>UserDefinedFunction"]
        BasicUDF["basicUDF<br/>UserDefinedFunction"]
    end
    
    subgraph "Data Types"
        RequestData["HTTPRequestData<br/>toHTTPCore()"]
        ResponseData["HTTPResponseData<br/>from CloseableHttpResponse"]
    end
    
    Handler --> HTTPClient
    HTTPClient --> ConnectionManager
    HTTPClient --> RequestConfig
    HTTPClient --> InternalClient
    HTTPClient --> AsyncHTTPClient
    HTTPClient --> SingleThreadedHTTPClient
    
    HandlingUtils --> SendWithRetries
    HandlingUtils --> AdvancedHandler
    HandlingUtils --> BasicHandler
    
    AdvancedHandler --> AdvancedUDF
    BasicHandler --> BasicUDF
    
    AsyncHTTPClient --> HandlingUtils
    SingleThreadedHTTPClient --> HandlingUtils
    
    RequestData --> SendWithRetries
    SendWithRetries --> ResponseData
    
    style HTTPClient fill:#f9f9f9
    style HandlingUtils fill:#f9f9f9
```

**HTTP Client System Architecture**: The system is organized around the `Handler` and `HTTPClient` abstractions. `HTTPClient` manages connection pooling and request configuration, while `HandlingUtils` provides the retry logic. Two client implementations support different execution patterns, and UDF wrappers enable usage in Spark DataFrames.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:1-203]()

## Core Components

### Handler Trait

The `Handler` trait defines the contract for HTTP request handling:

```scala
trait Handler {
  def handle(client: CloseableHttpClient, request: HTTPRequestData): HTTPResponseData
}
```

This simple interface allows different retry strategies and error handling policies to be composed with the core HTTP client functionality.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:21-25]()

### HTTPClient Trait

The `HTTPClient` trait provides the foundation for all HTTP client implementations:

| Component | Description | Configuration |
|-----------|-------------|---------------|
| `requestTimeout` | Timeout for all HTTP operations | Connect, connection request, and socket timeouts |
| `requestConfig` | Apache HttpClient request configuration | Built from `requestTimeout` parameter |
| `connectionManager` | Connection pool manager | `MaxPerRoute: Int.MaxValue`, `MaxTotal: Int.MaxValue` |
| `internalClient` | Underlying Apache HttpClient | Created with connection manager and request config |

The trait extends `BaseClient`, `AutoCloseable`, and `Handler`, providing lifecycle management and the core `handle()` method. The connection pool is configured to allow unlimited connections per route, as Spark handles threading limits at the executor level.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:27-63]()

### Connection Management

Connection pooling is implemented using Apache HttpClient's `PoolingHttpClientConnectionManager`:

- **Max connections per route**: `Int.MaxValue` - Spark controls parallelism at the executor level
- **Max total connections**: `Int.MaxValue` - No artificial limit imposed
- **Timeout configuration**: Unified timeout for connect, connection request, and socket operations
- **Resource cleanup**: `close()` method releases the internal HTTP client

The `sendRequestWithContext()` method wraps requests with contextual information, handling optional requests and propagating context through the request-response cycle.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:42-61]()

## Retry and Error Handling

### HandlingUtils Object

```mermaid
graph TB
    SendWithRetries["sendWithRetries()<br/>request + retry array"]
    
    subgraph "Status Code Handling"
        Code200["200/201/202<br/>Success"]
        Code429["429 Rate Limit<br/>Retry-After header"]
        Code4xx["4xx Client Error<br/>No retry"]
        Code5xx["5xx Server Error<br/>Retry"]
        ExtraCodes["Extra codes to retry<br/>Configurable"]
    end
    
    subgraph "Error Handling"
        IOException["IOException<br/>Connection errors"]
        KeepTrying["keepTrying()<br/>Sleep and retry"]
    end
    
    subgraph "Response Processing"
        ConvertAndClose["convertAndClose()<br/>HTTPResponseData"]
        ReleaseConnection["releaseConnection()"]
    end
    
    SendWithRetries --> Code200
    SendWithRetries --> Code429
    SendWithRetries --> Code4xx
    SendWithRetries --> Code5xx
    SendWithRetries --> ExtraCodes
    SendWithRetries --> IOException
    
    Code200 --> ConvertAndClose
    Code429 --> KeepTrying
    Code5xx --> KeepTrying
    ExtraCodes --> KeepTrying
    IOException --> KeepTrying
    
    KeepTrying --> SendWithRetries
    ConvertAndClose --> ReleaseConnection
    
    style SendWithRetries fill:#f9f9f9
```

**Retry Logic Flow**: The retry mechanism evaluates HTTP status codes and exceptions to determine whether to retry. Rate limiting (429) has special handling with `Retry-After` headers.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:65-182]()

### Retry Logic Implementation

The `sendWithRetries()` method implements sophisticated retry logic:

| Status Code | Behavior | Notes |
|-------------|----------|-------|
| 200, 201, 202 | Success - no retry | Request completed successfully |
| 429 | Retry with delay | Respects `Retry-After` header; doesn't count against retry budget |
| 4xx (except 429) | No retry | Client errors typically can't be fixed by retrying |
| 5xx | Retry with delay | Server errors may be transient |
| IOException | Retry with delay | Connection errors may be transient |

The retry array `retriesLeft: Array[Int]` specifies sleep durations in milliseconds between attempts. For example, `Array(100, 500, 1000)` retries up to 3 times with increasing delays.

**Special handling for 429**: When rate-limited, the system reads the `Retry-After` response header and sleeps for that duration. Importantly, 429 responses do not consume a retry attempt from the retry array, allowing the system to handle sustained rate limiting gracefully.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:86-146]()

### Handler Functions

`HandlingUtils` provides two main handler functions:

**`advanced(retryTimes: Int*)`** - Full-featured handler with:
- Configurable retry delays
- Debug logging of requests and responses
- Performance timing (logs milliseconds taken)
- Exception handling (returns null on failure)
- Connection release

**`basic()`** - Minimal handler with:
- Single attempt (no retries)
- No logging
- Connection release
- Immediate exception propagation

Both handlers convert the `CloseableHttpResponse` to `HTTPResponseData` and properly release connections.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:148-182]()

### Logging Integration

The retry system integrates with the SynapseML logging infrastructure:

```scala
SynapseMLLogging.logDebug(s"sending $message")
val start = System.currentTimeMillis()
val resp = sendWithRetries(client, req, retryTimes.toArray)
SynapseMLLogging.logMessage(
  s"finished sending to ${req.getURI} took (${System.currentTimeMillis() - start}ms)")
```

This provides:
- Debug-level logging of request payloads
- Performance metrics for each request
- Warning logs for error responses (non-2xx status codes)
- Error logs for connection failures
- Automatic scrubbing of sensitive information (SAS tokens)

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:156-161](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:87-92]()

## Client Implementations

### AsyncHTTPClient

```mermaid
graph LR
    AsyncClient["AsyncHTTPClient<br/>extends AsyncClient"]
    
    subgraph "Configuration"
        Handler["handler: HandlerFunc<br/>Retry strategy"]
        Concurrency["concurrency: Int<br/>Thread pool size"]
        Timeout["timeout: Duration<br/>Overall timeout"]
        RequestTimeout["requestTimeout: Int<br/>HTTP timeout"]
        EC["ExecutionContext<br/>Thread management"]
    end
    
    subgraph "Execution"
        BlockingHandle["handle() with blocking<br/>Prevents starvation"]
        HandlerExecution["Execute handler function<br/>With retry logic"]
    end
    
    AsyncClient --> Handler
    AsyncClient --> Concurrency
    AsyncClient --> Timeout
    AsyncClient --> RequestTimeout
    AsyncClient --> EC
    
    Handler --> BlockingHandle
    BlockingHandle --> HandlerExecution
    
    style AsyncClient fill:#f9f9f9
```

**AsyncHTTPClient Architecture**: Extends `AsyncClient` base class with HTTP-specific functionality, using an `ExecutionContext` for parallel request handling.

The `AsyncHTTPClient` is designed for high-throughput scenarios where multiple HTTP requests can be processed concurrently:

- **Constructor parameters**: 
  - `handler: HandlerFunc` - The retry strategy to use (typically `HandlingUtils.advanced()`)
  - `concurrency: Int` - Maximum number of concurrent requests
  - `timeout: Duration` - Overall timeout for the operation
  - `requestTimeout: Int` - Timeout for individual HTTP requests
  - `ec: ExecutionContext` - Thread pool for async execution

- **Blocking wrapper**: The `handle()` method wraps the handler with `blocking` to inform the execution context that this is a blocking operation, preventing thread pool starvation

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:184-194]()

### SingleThreadedHTTPClient

The `SingleThreadedHTTPClient` provides a simpler execution model for sequential processing:

- **Constructor parameters**:
  - `handler: HandlerFunc` - The retry strategy to use
  - `requestTimeout: Int` - Timeout for HTTP requests

- **Execution model**: Extends `SingleThreadedClient` base class, processing requests sequentially without concurrency management

- **Use case**: Suitable for scenarios where requests must be processed in order or where the overhead of thread management is unnecessary

Both implementations use the `blocking` wrapper around the handler to properly signal to the execution context that HTTP I/O is occurring.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:196-202]()

## UDF Support

The HTTP client system provides User-Defined Functions for use in Spark DataFrame transformations:

### Handler UDFs

```mermaid
graph TB
    DataFrame["Spark DataFrame<br/>with request data"]
    
    subgraph "UDF Functions"
        AdvancedUDF["advancedUDF(retryTimes: Int*)<br/>Returns UDF"]
        BasicUDF["basicUDF<br/>Returns UDF"]
    end
    
    subgraph "Handler Functions"
        Advanced["advanced(retryTimes: Int*)<br/>HandlerFunc"]
        Basic["basic()<br/>HandlerFunc"]
    end
    
    subgraph "Execution"
        UDFUtils["UDFUtils.oldUdf()<br/>StringType output"]
        HTTPExecution["HTTP request execution<br/>with retry logic"]
    end
    
    DataFrame --> AdvancedUDF
    DataFrame --> BasicUDF
    
    AdvancedUDF --> Advanced
    BasicUDF --> Basic
    
    Advanced --> UDFUtils
    Basic --> UDFUtils
    
    UDFUtils --> HTTPExecution
    
    style AdvancedUDF fill:#f9f9f9
    style BasicUDF fill:#f9f9f9
```

**UDF Integration**: Handler functions are wrapped as UDFs for DataFrame operations, returning string-serialized HTTP responses.

### UDF Implementations

**`advancedUDF(retryTimes: Int*): UserDefinedFunction`**
- Wraps the `advanced()` handler as a UDF
- Takes variable retry times as parameters
- Returns `StringType` (serialized `HTTPResponseData`)
- Suitable for production workloads requiring resilience

**`basicUDF: UserDefinedFunction`**
- Wraps the `basic()` handler as a UDF
- No retry logic
- Returns `StringType` (serialized `HTTPResponseData`)
- Suitable for testing or simple use cases

Both UDFs use `UDFUtils.oldUdf()` for backward compatibility with older Spark versions.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:171-182]()

## Integration Points

### Cognitive Services Integration

The HTTP Client System is the primary communication layer for Azure Cognitive Services:

```mermaid
graph TB
    subgraph "Cognitive Services Base"
        CognitiveBase["CognitiveServiceBase<br/>Abstract class"]
        HTTPHandler["Handler function<br/>Configured with retries"]
    end
    
    subgraph "HTTP Client"
        AsyncClient["AsyncHTTPClient<br/>Parallel execution"]
        ConnectionPool["Connection pooling"]
        RetryLogic["Retry with exponential backoff"]
    end
    
    subgraph "Service Implementations"
        OpenAI["OpenAI Services<br/>Chat, Completion, Embedding"]
        TextAnalytics["Text Analytics"]
        Vision["Computer Vision"]
    end
    
    subgraph "Supporting Systems"
        SecretMgmt["Secret Management<br/>API keys"]
        Logging["SynapseML Logging<br/>Telemetry"]
    end
    
    CognitiveBase --> HTTPHandler
    HTTPHandler --> AsyncClient
    AsyncClient --> ConnectionPool
    AsyncClient --> RetryLogic
    
    OpenAI --> CognitiveBase
    TextAnalytics --> CognitiveBase
    Vision --> CognitiveBase
    
    CognitiveBase --> SecretMgmt
    AsyncClient --> Logging
    
    style CognitiveBase fill:#f9f9f9
    style AsyncClient fill:#f9f9f9
```

**Cognitive Services Integration**: All Azure AI service wrappers use the HTTP Client System through `CognitiveServiceBase`.

Sources: Files referenced in high-level diagrams showing Cognitive Services → HTTPClients relationship

### Fabric Client Integration

The Fabric platform client uses HTTP utilities for workload endpoint communication:

- **RESTUtils trait**: Provides `usagePost()` method for HTTP POST requests
- **Token authentication**: Integrates with `TokenLibrary` for bearer token management
- **Workload endpoints**: Uses HTTP client for ML workload API calls
- **Header management**: Configures Authorization, RequestId, Content-Type headers

The `FabricClient.usagePost()` method demonstrates the integration pattern, posting JSON payloads to Fabric workload endpoints with authentication and request tracking.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:190-192]()

### Usage Patterns

The HTTP Client System is typically instantiated with one of these patterns:

**Pattern 1: Async with custom retries**
```scala
new AsyncHTTPClient(
  handler = HandlingUtils.advanced(100, 500, 1000),
  concurrency = 10,
  timeout = Duration(60, "seconds"),
  requestTimeout = 30000
)(ExecutionContext.global)
```

**Pattern 2: Single-threaded with default handler**
```scala
new SingleThreadedHTTPClient(
  handler = HandlingUtils.basic,
  requestTimeout = 30000
)
```

**Pattern 3: UDF for DataFrame operations**
```scala
df.withColumn("response", 
  HandlingUtils.advancedUDF(100, 500, 1000)($"request"))
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:184-202]()

### Request and Response Data Types

The system uses specific data types for HTTP operations:

- **`HTTPRequestData`**: Wraps HTTP request information with a `toHTTPCore()` method that converts to Apache HttpClient's request types (`HttpPost`, `HttpGet`, etc.)

- **`HTTPResponseData`**: Constructed from `CloseableHttpResponse`, providing access to status code, headers, and response body

- **`RequestWithContext`**: Pairs an optional `HTTPRequestData` with context information for tracking requests through the pipeline

- **`ResponseWithContext`**: Pairs an optional `HTTPResponseData` with context information, preserving request tracking

The `sendRequestWithContext()` method demonstrates this pattern, mapping requests to responses while preserving context.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:57-61]()

## Performance Considerations

### Connection Pooling Strategy

The connection pool configuration prioritizes horizontal scalability:

- **No artificial limits**: `Int.MaxValue` for both per-route and total connections
- **Spark-managed parallelism**: Relies on Spark's executor and partition management rather than HTTP connection limits
- **Trade-off**: Higher memory usage in exchange for eliminating connection pool contention

This design is appropriate for distributed Spark workloads where executor-level parallelism is already constrained by cluster resources.

### Timeout Configuration

All timeouts share a single value (`requestTimeout`):
- **Connect timeout**: Time to establish TCP connection
- **Connection request timeout**: Time to obtain connection from pool
- **Socket timeout**: Time waiting for data after connection established

This simplified configuration ensures consistent behavior but may not be optimal for all scenarios (e.g., slow initial connection but fast data transfer).

### Retry Budget

The retry array design provides flexibility:
- **Exponential backoff**: `Array(100, 500, 1000, 2000)` - increasing delays
- **Fixed retry**: `Array(1000, 1000, 1000)` - consistent delays  
- **Rate limit handling**: 429 responses don't consume retry attempts

The `advanced()` handler logs timing information, enabling performance monitoring and retry strategy tuning.

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:34-51](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala:87-146]()

---

# Page: Parameter Management

# Parameter Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py](cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py)
- [cognitive/src/main/python/synapse/ml/services/openai/__init__.py](cognitive/src/main/python/synapse/ml/services/openai/__init__.py)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala)
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py](cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala)
- [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](docs/Explore Algorithms/OpenAI/OpenAI.ipynb)

</details>



This page documents the parameter management systems in SynapseML, providing an overview of how parameters are defined, accessed, and shared across the library. The parameter management system enables configuration of model behavior, API endpoint settings, and processing options throughout the library.

For information about HTTP client configuration specifically, see [HTTP Client System](#5.2).

## Overview of Parameter Management in SynapseML

SynapseML builds upon Apache Spark's parameter system and extends it with global parameter capabilities, default parameter management, and specialized parameter trait hierarchies for different components. This allows for flexible configuration both at the instance level and globally across multiple components.

```mermaid
graph TB
    subgraph "SynapseML Parameter Management"
        GlobalParams["GlobalParams System"] --> GlobalKeys["Global Parameter Keys"]
        GlobalParams --> GlobalStorage["Global Parameter Storage"]
        
        ParameterTraits["Parameter Traits"] --> SparkParams["Apache Spark Params"]
        ParameterTraits --> MLParams["SynapseML Parameter Traits"]
        
        DefaultSystems["Default Parameter Systems"] --> OpenAIDefaults["OpenAIDefaults"]
        DefaultSystems --> HTTPDefaults["HTTP Defaults (URLKey)"]
        
        ModelParams["Model-Specific Parameters"] --> LightGBMParams["LightGBM Parameters"]
        ModelParams --> ServicesParams["AI Services Parameters"]
        
        GlobalParams -.-> DefaultSystems
        ParameterTraits -.-> ModelParams
    end
    
    style GlobalParams stroke-width:3px
    style ParameterTraits stroke-width:3px
```

Sources:
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala]()

## Global Parameter System

The Global Parameter System provides a mechanism to share parameters across different components and classes, allowing for centralized configuration that affects multiple parts of the system.

### Architecture of Global Parameter System

```mermaid
classDiagram
    class GlobalParams {
        -Map~GlobalKey, Any~ GlobalParams
        -Map~Any, GlobalKey~ ParamToKeyMap
        +setGlobalParam(key, value)
        +getGlobalParam(key)
        +resetGlobalParam(key)
        +getParam(param)
        +registerParam(param, key)
    }
    
    class GlobalKey {
        <<trait>>
    }
    
    class HasGlobalParams {
        <<trait>>
        +transferGlobalParamsToParamMap()
    }
    
    class ConcreteKey {
        <<case object>>
    }
    
    class Component {
        +param: Param
        +getParam()
        +setParam(value)
    }
    
    GlobalKey <|-- ConcreteKey
    GlobalParams -- GlobalKey : uses
    HasGlobalParams -- GlobalParams : uses
    Component --|> HasGlobalParams
    Component -- GlobalParams : registers parameters
```

Sources:
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala]()
- [core/src/test/scala/com/microsoft/azure/synapse/ml/param/GlobalParamsSuite.scala]()

### Key Components

1. **GlobalParams object**: Central storage for global parameters
   - Uses two mutable maps:
     - `GlobalParams`: Maps `GlobalKey[_]` to parameter values
     - `ParamToKeyMap`: Maps parameter objects to their global keys

2. **GlobalKey trait**: Marker trait for defining parameter keys
   - Concrete implementations are typically case objects
   - Example: `URLKey` for HTTP endpoint URLs

3. **HasGlobalParams trait**: Interface for components that use global parameters
   - Provides `transferGlobalParamsToParamMap()` to copy global parameters to component parameters

### Core Methods

| Method | Description |
|--------|------------|
| `GlobalParams.setGlobalParam[T](key: GlobalKey[T], value: T)` | Sets a global parameter value |
| `GlobalParams.getGlobalParam[T](key: GlobalKey[T]): Option[T]` | Gets a global parameter value |
| `GlobalParams.resetGlobalParam[T](key: GlobalKey[T])` | Removes a global parameter |
| `GlobalParams.registerParam[T](p: Param[T], key: GlobalKey[T])` | Associates a parameter with a global key |
| `HasGlobalParams.transferGlobalParamsToParamMap()` | Transfers global parameters to component parameters |

Sources:
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:16-42]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:44-56]()

### Example Usage

```scala
// Define a global key
case object MyParameterKey extends GlobalKey[Double]

// Create a component with a parameter
class MyComponent extends HasGlobalParams {
  val myParam = new DoubleParam(this, "myParam", "My parameter")
  
  // Register the parameter with the global key
  GlobalParams.registerParam(myParam, MyParameterKey)
  
  def getMyParam: Double = $(myParam)
  def setMyParam(v: Double): this.type = set(myParam, v)
}

// Set a global parameter value
GlobalParams.setGlobalParam(MyParameterKey, 42.0)

// Create a component instance and transfer global parameters
val component = new MyComponent()
component.transferGlobalParamsToParamMap()
assert(component.getMyParam == 42.0)
```

Sources:
- [core/src/test/scala/com/microsoft/azure/synapse/ml/param/GlobalParamsSuite.scala:11-30]()
- [core/src/test/scala/com/microsoft/azure/synapse/ml/param/GlobalParamsSuite.scala:36-47]()

## Default Parameter Systems

SynapseML implements specialized default parameter systems for different components, using the global parameter system as a foundation. These systems provide convenient ways to configure common parameters across multiple instances.

### OpenAI Default Parameters

The `OpenAIDefaults` object provides static methods for managing default parameters for OpenAI services.

```mermaid
graph TB
    subgraph "OpenAI Parameter Management"
        OpenAIDefaults["OpenAIDefaults"] --> setDeploy["setDeploymentName()"]
        OpenAIDefaults --> setKey["setSubscriptionKey()"]
        OpenAIDefaults --> setTemp["setTemperature()"]
        OpenAIDefaults --> setURL["setURL()"]
        OpenAIDefaults --> getDeploy["getDeploymentName()"]
        OpenAIDefaults --> getKey["getSubscriptionKey()"]
        OpenAIDefaults --> getTemp["getTemperature()"]
        OpenAIDefaults --> getURL["getURL()"]
        OpenAIDefaults --> resetDeploy["resetDeploymentName()"]
        OpenAIDefaults --> resetKey["resetSubscriptionKey()"]
        OpenAIDefaults --> resetTemp["resetTemperature()"]
        OpenAIDefaults --> resetURL["resetURL()"]
        
        OpenAIDefaults -- uses --> GlobalParams["GlobalParams"]
        GlobalParams -- stores --> OpenAIKeys["OpenAI Parameter Keys"]
        
        OpenAIModels["OpenAI Models"] -- read --> GlobalParams
        
        OpenAIKeys --> DeployKey["OpenAIDeploymentNameKey"]
        OpenAIKeys --> SubKey["OpenAISubscriptionKey"]
        OpenAIKeys --> TempKey["OpenAITemperatureKey"]
        OpenAIKeys --> URLKey["URLKey"]
    end
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala:10-66]()
- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py:20-61]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala:35-45]()

OpenAIDefaults provides methods for:

| Method | Description |
|--------|------------|
| `setDeploymentName(v: String)` | Sets the default OpenAI deployment name |
| `getDeploymentName: Option[String]` | Gets the default OpenAI deployment name |
| `resetDeploymentName()` | Resets the default OpenAI deployment name |
| `setSubscriptionKey(v: String)` | Sets the default OpenAI subscription key |
| `getSubscriptionKey: Option[String]` | Gets the default OpenAI subscription key |
| `resetSubscriptionKey()` | Resets the default OpenAI subscription key |
| `setTemperature(v: Double)` | Sets the default OpenAI temperature |
| `getTemperature: Option[Double]` | Gets the default OpenAI temperature |
| `resetTemperature()` | Resets the default OpenAI temperature |
| `setURL(v: String)` | Sets the default OpenAI endpoint URL |
| `getURL: Option[String]` | Gets the default OpenAI endpoint URL |
| `resetURL()` | Resets the default OpenAI endpoint URL |

Usage example:

```scala
// Set default parameters
OpenAIDefaults.setDeploymentName("gpt-35-turbo")
OpenAIDefaults.setSubscriptionKey("your-subscription-key")
OpenAIDefaults.setTemperature(0.7)
OpenAIDefaults.setURL("https://your-endpoint.openai.azure.com/")

// Create OpenAI model without explicitly setting parameters
val model = new OpenAIChatCompletion()
  .setMaxTokens(200)
  .setOutputCol("out")
  .setMessagesCol("prompt")

// The model will use the default parameters
```

Sources:
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala:35-45]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala:74-87]()
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py:86-101]()

### URL Parameter Management

The `URLKey` object is a global key used for managing HTTP endpoint URLs across the system.

```scala
case object URLKey extends GlobalKey[String]

trait HasURL extends Params {
  val url: Param[String] = new Param[String](this, "url", "Url of the service")
  
  GlobalParams.registerParam(url, URLKey)
  
  def getUrl: String = $(url)
  def setUrl(value: String): this.type = set(url, value)
}
```

Sources:
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPTransformer.scala:79-93]()

## Specialized Parameter Hierarchies

SynapseML implements specialized parameter hierarchies for different components, allowing for modular parameter definition and composition.

### LightGBM Parameter System

LightGBM has an extensive parameter system with specialized traits for different aspects of the model.

```mermaid
graph TB
    subgraph "LightGBM Parameter Hierarchy"
        LightGBMParams["LightGBMParams"] --> LightGBMExecutionParams["LightGBMExecutionParams"]
        LightGBMParams --> LightGBMDatasetParams["LightGBMDatasetParams"]
        LightGBMParams --> LightGBMLearnerParams["LightGBMLearnerParams"]
        LightGBMParams --> LightGBMBinParams["LightGBMBinParams"]
        LightGBMParams --> LightGBMFractionParams["LightGBMFractionParams"]
        LightGBMParams --> LightGBMSlotParams["LightGBMSlotParams"]
        LightGBMParams --> LightGBMDartParams["LightGBMDartParams"]
        LightGBMParams --> LightGBMPredictionParams["LightGBMPredictionParams"]
        LightGBMParams --> LightGBMObjectiveParams["LightGBMObjectiveParams"]
        LightGBMParams --> LightGBMSeedParams["LightGBMSeedParams"]
        LightGBMParams --> LightGBMCategoricalParams["LightGBMCategoricalParams"]
        
        LightGBMBase["LightGBMBase"] --> LightGBMParams
        
        LightGBMClassifier["LightGBMClassifier"] --> LightGBMBase
        LightGBMRegressor["LightGBMRegressor"] --> LightGBMBase
        LightGBMRanker["LightGBMRanker"] --> LightGBMBase
    end
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:488-504]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:27-34]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:27-30]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:39-42]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:26-29]()

Key parameter traits:

| Trait | Description |
|-------|------------|
| `LightGBMExecutionParams` | Parameters for controlling execution, like parallelism and timeout |
| `LightGBMDatasetParams` | Parameters for dataset handling, like sparse data support |
| `LightGBMLearnerParams` | Parameters for learning process, like early stopping |
| `LightGBMBinParams` | Parameters for histogram bin construction |
| `LightGBMFractionParams` | Parameters for data/feature fractions and bagging |
| `LightGBMSlotParams` | Parameters for feature slots |
| `LightGBMDartParams` | Parameters for DART (Dropouts meet Multiple Additive Regression Trees) |
| `LightGBMPredictionParams` | Parameters for prediction behavior |
| `LightGBMObjectiveParams` | Parameters for objective functions |
| `LightGBMSeedParams` | Parameters for random seeds and determinism |
| `LightGBMCategoricalParams` | Parameters for categorical feature handling |

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:16-159]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:163-183]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:187-227]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:231-241]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:245-275]()

### Parameter Management in LightGBM Models

LightGBM models use a complex parameter management system to handle the wide variety of parameters needed for different aspects of the model.

```mermaid
flowchart TB
    subgraph "LightGBM Parameter Flow"
        MLParams("ML Parameters\nUser-configured")
        TrainParams("Training Parameters\nCompiled from traits")
        NativeParams("Native Parameters\nPassthrough to LightGBM")
        
        MLParams --> |getTrainParams| TrainParams
        TrainParams --> |toString| NativeParams
        TrainParams --> |addCustomTrainParams| CustomParams("Custom Parameters\nModel-specific adjustments")
        CustomParams --> NativeParams
        
        NativeParams --> LightGBMBooster("LightGBMBooster\nNative library")
    end
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:146-216]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:240-288]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:396-447]()

Key parameter handling methods in `LightGBMBase`:

1. `getTrainParams`: Collects parameters from various traits into a single `BaseTrainParams` object
2. `addCustomTrainParams`: Allows model-specific parameter customization
3. `getGeneralParams`, `getDatasetParams`, etc.: Specialized methods for different parameter categories
4. `getDatasetCreationParams`: Formats parameters for native LightGBM dataset creation

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:249-287]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:294-359]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:374-386]()

## Python Integration

SynapseML provides Python wrappers for its parameter management systems, allowing for consistent parameter handling between Scala and Python.

### OpenAI Defaults in Python

The `OpenAIDefaults` Python class provides the same functionality as its Scala counterpart:

```python
class OpenAIDefaults:
    def set_deployment_name(self, name)
    def get_deployment_name(self)
    def reset_deployment_name(self)
    def set_subscription_key(self, key)
    def get_subscription_key(self)
    def reset_subscription_key(self)
    def set_temperature(self, temp)
    def get_temperature(self)
    def reset_temperature(self)
    def set_URL(self, URL)
    def get_URL(self)
    def reset_URL(self)
```

Sources:
- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py:20-61]()
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py:17-52]()

### LightGBM Model Parameters in Python

The `LightGBMModelMixin` in Python provides access to model parameters and methods:

```python
class LightGBMModelMixin:
    def saveNativeModel(self, filename, overwrite=True)
    def getNativeModel(self)
    def getFeatureImportances(self, importance_type="split")
    def getFeatureShaps(self, vector)
    def getBoosterBestIteration(self)
    def getBoosterNumTotalIterations(self)
    def getBoosterNumTotalModel(self)
    def getBoosterNumFeatures(self)
    def setPredictDisableShapeCheck(self, value=None)
```

Sources:
- [lightgbm/src/main/python/synapse/ml/lightgbm/mixin.py:9-93]()

## Best Practices

When working with parameters in SynapseML, consider the following best practices:

1. **Global vs. Local Parameter Settings**
   - Use global parameters when you want consistent settings across multiple instances
   - Use local parameters (instance-specific) for customization
   - Be aware that instance parameters override global parameters

2. **Parameter Hierarchy**
   - Understand the parameter inheritance hierarchy for your model
   - Specialized parameters are grouped into meaningful traits
   - These traits are combined in the final model classes

3. **Default Parameters**
   - Use default parameter systems like `OpenAIDefaults` to set common configurations
   - Reset global parameters when no longer needed to avoid unexpected behavior
   - Check available default parameters before setting them explicitly

4. **Parameter Conversion**
   - Be aware of parameter conversion between different layers (e.g., Spark ML to native LightGBM)
   - Use the appropriate parameter format for your context
   - Check the parameter validation logic to ensure valid values

5. **Python-Scala Interoperability**
   - Use the same parameter names and meanings in both languages
   - Be aware of slight naming differences (camelCase in Scala, snake_case in Python)
   - Global parameters set in one language are available in the other

Sources:
- [core/src/test/scala/com/microsoft/azure/synapse/ml/param/GlobalParamsSuite.scala:36-47]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala:90-105]()
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py:54-67]()

## Parameter Management Implementation Details

### GlobalParams Implementation

The `GlobalParams` object uses two mutable maps to manage parameters:

1. `ParamToKeyMap`: Maps Spark ML parameter objects to their global keys
2. `GlobalParams`: Maps global keys to their values

When a parameter is registered with a global key using `registerParam`, the association is stored in `ParamToKeyMap`. When a global parameter is set using `setGlobalParam`, the value is stored in `GlobalParams` map.

The `HasGlobalParams` trait provides a method `transferGlobalParamsToParamMap()` that checks if any parameters are not set locally, and if so, tries to look up their values from the global parameter system.

Sources:
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:13-42]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:44-56]()

### OpenAIDefaults Implementation

The `OpenAIDefaults` object provides static methods for managing OpenAI parameters. Each parameter has a corresponding global key, and the methods simply delegate to the GlobalParams system:

```scala
def setDeploymentName(v: String): Unit = {
  GlobalParams.setGlobalParam(OpenAIDeploymentNameKey, Left(v))
}

def getDeploymentName: Option[String] = {
  extractLeft(GlobalParams.getGlobalParam(OpenAIDeploymentNameKey))
}

def resetDeploymentName(): Unit = {
  GlobalParams.resetGlobalParam(OpenAIDeploymentNameKey)
}
```

The `extractLeft` helper method handles the Either type returned by GlobalParams:

```scala
private def extractLeft[T](optEither: Option[Either[T, String]]): Option[T] = {
  optEither match {
    case Some(Left(v)) => Some(v)
    case _ => None
  }
}
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala:10-66]()

### LightGBM Parameter Handling

LightGBM models collect parameters from various traits and compile them into a single `BaseTrainParams` object using methods like `getTrainParams` and `addCustomTrainParams`. These parameters are then passed to the native LightGBM library.

The parameter flow is:

1. User sets parameters on the model instance (`setNumIterations`, `setLearningRate`, etc.)
2. `train` method calls `getTrainParams` to collect parameters from various traits
3. `addCustomTrainParams` allows model-specific parameter adjustments
4. Parameters are compiled into a string representation using `toString`
5. Parameters are passed to the native LightGBM library

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:36-65]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:396-447]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:43-57]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:60-74]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:51-66]()

---

# Page: Secret Management

# Secret Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py](cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py](cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/test_simple.py](cognitive/src/test/python/synapsemltest/services/test_simple.py)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/main/python/synapse/ml/core/init_spark.py](core/src/main/python/synapse/ml/core/init_spark.py)
- [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py](core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py)
- [core/src/main/python/synapse/ml/core/logging/__init__.py](core/src/main/python/synapse/ml/core/logging/__init__.py)
- [core/src/main/python/synapse/ml/core/platform/Platform.py](core/src/main/python/synapse/ml/core/platform/Platform.py)
- [core/src/test/python/synapsemltest/core/test_logging.py](core/src/test/python/synapsemltest/core/test_logging.py)
- [core/src/test/python/synapsemltest/core/test_template.py](core/src/test/python/synapsemltest/core/test_template.py)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [docs/Get Started/Set up Cognitive Services.ipynb](docs/Get Started/Set up Cognitive Services.ipynb)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)

</details>



## Purpose and Scope

The Secret Management system provides a platform-agnostic interface for retrieving secrets from various credential stores across different execution environments (Synapse, Fabric, Databricks, and local). This system abstracts the complexity of accessing secrets from Azure Key Vault, Databricks Secret Scopes, and other platform-specific credential stores, enabling code to run seamlessly across different deployment targets without modification.

For information about platform detection and adaptation, see [Platform Detection and Adaptation](#2.3). For HTTP client authentication, see [HTTP Client System](#5.2).

## Architecture Overview

The secret management system consists of two main components: a Python function for production use (`find_secret()`) and a Scala utility for testing (`Secrets` object). The system detects the execution platform and routes secret retrieval requests to the appropriate platform-specific API.

### Secret Retrieval Flow

```mermaid
flowchart TD
    UserCode["User Code / Notebook"]
    FindSecret["find_secret(secret_name, keyvault)"]
    PlatformDetect["current_platform()"]
    
    SynapseRoute["Synapse Path"]
    SynapseIntRoute["Synapse Internal Path"]
    DatabricksRoute["Databricks Path"]
    ErrorRoute["Unknown Platform"]
    
    MSSpark["mssparkutils.credentials.getSecret()"]
    KeyVaultURL["KeyVault URL Construction"]
    DBUtils["dbutils.secrets.get()"]
    ErrorMsg["RuntimeError with Instructions"]
    
    UserCode --> FindSecret
    FindSecret --> PlatformDetect
    
    PlatformDetect -->|"PLATFORM_SYNAPSE"| SynapseRoute
    PlatformDetect -->|"PLATFORM_SYNAPSE_INTERNAL"| SynapseIntRoute
    PlatformDetect -->|"PLATFORM_DATABRICKS"| DatabricksRoute
    PlatformDetect -->|"PLATFORM_UNKNOWN"| ErrorRoute
    
    SynapseRoute --> MSSpark
    SynapseIntRoute --> KeyVaultURL
    KeyVaultURL --> MSSpark
    DatabricksRoute --> DBUtils
    ErrorRoute --> ErrorMsg
    
    MSSpark --> SecretValue["Secret Value"]
    DBUtils --> SecretValue
```

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:57-93]()

### Integration Points in the Codebase

```mermaid
flowchart LR
    subgraph "Platform Module"
        Platform["Platform.py"]
        FindSecret["find_secret()"]
        CurrentPlatform["current_platform()"]
    end
    
    subgraph "Test Infrastructure"
        SecretsScala["Secrets.scala"]
        GetSecret["getSecret()"]
        AzCLI["az keyvault secret show"]
    end
    
    subgraph "Usage Locations"
        Notebooks["Example Notebooks<br/>*.ipynb"]
        TestFiles["Test Files<br/>*Test*.py, *Suite.scala"]
        Transformers["Service Transformers<br/>LangchainTransform.py"]
    end
    
    subgraph "External Services"
        KeyVault["Azure Key Vault<br/>mmlspark-build-keys"]
        DBSecrets["Databricks Secret Scopes"]
        SynapseLinked["Synapse Linked Services"]
    end
    
    Platform --> FindSecret
    Platform --> CurrentPlatform
    FindSecret --> KeyVault
    FindSecret --> DBSecrets
    FindSecret --> SynapseLinked
    
    SecretsScala --> GetSecret
    GetSecret --> AzCLI
    AzCLI --> KeyVault
    
    Notebooks --> FindSecret
    TestFiles --> GetSecret
    Transformers --> FindSecret
```

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py](), [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala]()

## The `find_secret()` Function

The `find_secret()` function is the primary interface for secret retrieval in production code. It accepts two parameters and returns the secret value as a string.

### Function Signature

```python
def find_secret(secret_name: str, keyvault: str) -> str
```

| Parameter | Description |
|-----------|-------------|
| `secret_name` | The name of the secret to retrieve |
| `keyvault` | The name of the Azure Key Vault (for Azure platforms) or the Databricks secret scope name (for Databricks) |

### Implementation Details

The function is implemented in [core/src/main/python/synapse/ml/core/platform/Platform.py:57-93](). It performs the following steps:

1. **Platform Detection**: Calls `current_platform()` to determine the execution environment
2. **Routing**: Routes to the appropriate platform-specific implementation
3. **Error Handling**: Wraps all operations in a try-catch block that provides detailed error messages

### Platform-Specific Implementations

| Platform | API Used | Key Vault Specification |
|----------|----------|------------------------|
| **Synapse** (`PLATFORM_SYNAPSE`) | `notebookutils.mssparkutils.credentials.getSecret(keyvault, secret_name)` | Key vault name directly |
| **Synapse Internal** (`PLATFORM_SYNAPSE_INTERNAL`) | `notebookutils.mssparkutils.credentials.getSecret(keyVaultURL, secret_name)` | Constructs URL: `https://{keyvault}.vault.azure.net/` |
| **Databricks** (`PLATFORM_DATABRICKS`) | `dbutils.secrets.get(scope=keyvault, key=secret_name)` | Secret scope name |
| **Fabric Python** (`PLATFORM_FABRIC_PYTHON`) | Not supported (raises error) | N/A |
| **Unknown** | Not supported (raises error) | N/A |

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:57-76]()

## Test Infrastructure

For testing purposes, SynapseML provides a Scala-based secret retrieval system that uses the Azure CLI to access Key Vault directly.

### The `Secrets` Object

The `Secrets` object in [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala]() provides a test-specific secret retrieval mechanism. It is used exclusively in Scala tests and is not available to end users.

```mermaid
flowchart TD
    TestCode["Test Code"]
    SecretsObj["Secrets Object"]
    GetSecret["getSecret(secretName)"]
    ExecAzCLI["exec('az keyvault secret show...')"]
    ParseJSON["JSON Parsing"]
    
    TestCode --> SecretsObj
    SecretsObj --> GetSecret
    GetSecret --> ExecAzCLI
    ExecAzCLI --> ParseJSON
    ParseJSON --> SecretValue["Secret Value"]
    
    subgraph "Lazy Val Secrets"
        CogKey["CognitiveApiKey"]
        OpenAIKey["OpenAIApiKey"]
        AIFoundryKey["AIFoundryApiKey"]
        AdbToken["AdbToken"]
        Others["16+ other secrets"]
    end
    
    GetSecret --> CogKey
    GetSecret --> OpenAIKey
    GetSecret --> AIFoundryKey
    GetSecret --> AdbToken
    GetSecret --> Others
```

### Key Features

1. **Azure CLI Integration**: Uses `az keyvault secret show` command [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala:40-47]()
2. **Lazy Evaluation**: Secrets are defined as lazy vals, fetched only when needed
3. **Pre-defined Secrets**: Common secrets are exposed as properties (e.g., `CognitiveApiKey`, `OpenAIApiKey`)
4. **Subscription Management**: Automatically sets the Azure subscription via `AccountString` lazy val

### Common Test Secrets

| Secret Property | Key Vault Secret Name | Purpose |
|----------------|----------------------|---------|
| `CognitiveApiKey` | `cognitive-api-key` | Azure AI Services authentication |
| `OpenAIApiKey` | `openai-api-key-2` | Azure OpenAI authentication |
| `AIFoundryApiKey` | `synapseml-ai-foundry-resource-key` | Azure AI Foundry authentication |
| `AdbToken` | `adb-token` | Azure Databricks token |
| `BingSearchKey` | `bing-search-key` | Bing Search API |
| `AzureSearchKey` | `azure-search-key` | Azure Cognitive Search |

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala:44-79]()

## Error Handling and Messaging

The secret management system provides comprehensive error messages to guide users when secret retrieval fails.

### Error Message Structure

When `find_secret()` fails, it raises a `RuntimeError` with a detailed message that includes:

1. The secret name and keyvault that failed
2. Platform-specific setup instructions
3. Security best practices
4. Links to documentation

### Example Error Message

```
Could not find {secret_name} in keyvault {keyvault}. 
If you are trying to use the mmlspark-build-keys keyvault, you cant! 
You need to make your own keyvault with secrets or replace this call with a string. 
Make sure your notebook has access to a keyvault named {keyvault} which contains a secret named {secret_name}. 
On synapse, use a linked service keyvault, 
on databricks use their secrets management sdk, 
on fabric make sure your azure identity can access your azure keyvault. 
If you want to avoid making a keyvault, replace this call to find secret with your secret as a string 
like my_secret = 'jdiej38dnal.....'. Note that this has security implications for publishing and sharing notebooks! 
Please see the documentation for more information. 
https://microsoft.github.io/SynapseML/docs/Get%20Started/Set%20up%20Cognitive%20Services/
```

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:77-92]()

## Usage Patterns

### Pattern 1: Notebook Usage

The most common usage pattern is in example notebooks for authenticating with Azure services:

```python
from synapse.ml.core.platform import find_secret

openai_key = find_secret(
    secret_name="openai-api-key-2", 
    keyvault="mmlspark-build-keys"
)
cognitive_key = find_secret(
    secret_name="ai-services-api-key",
    keyvault="mmlspark-build-keys"
)
```

**Sources:** [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb:142-163](), [docs/Explore Algorithms/OpenAI/Langchain.ipynb:164-174]()

### Pattern 2: Test Code Usage (Scala)

In Scala tests, the `Secrets` object is used directly:

```scala
import com.microsoft.azure.synapse.ml.Secrets

val cognitiveKey = Secrets.CognitiveApiKey
val openAIKey = Secrets.OpenAIApiKey
val synapseToken = Secrets.getAccessToken("https://dev.azuresynapse.net/")
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:137-138](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala:6-7]()

### Pattern 3: Test Code Usage (Python)

Python tests use subprocess to call Azure CLI directly:

```python
import subprocess
import json

secretJson = subprocess.check_output(
    "az keyvault secret show --vault-name mmlspark-build-keys --name openai-api-key-2",
    shell=True,
)
openai_api_key = json.loads(secretJson)["value"]
```

**Sources:** [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:20-24]()

### Pattern 4: Documentation and User Guidance

Documentation notebooks demonstrate the pattern and provide instructions for users to replace with their own secrets:

```python
# Replace the call to find_secret with your key as a python string
ai_services_key = find_secret(
    secret_name="ai-services-api-key", keyvault="mmlspark-build-keys"
)  # Replace this line with a string like: ai_services_key = "your-key-here"
```

**Sources:** [docs/Get Started/Set up Cognitive Services.ipynb:182-184]()

## Platform Configuration

### Constants and Detection Logic

The platform detection system uses specific constants and environment checks defined in [core/src/main/python/synapse/ml/core/platform/Platform.py:6-34]():

| Platform Constant | Detection Method |
|------------------|------------------|
| `PLATFORM_SYNAPSE_INTERNAL` | `os.environ.get("AZURE_SERVICE") == "Microsoft.ProjectArcadia"` and `spark.cluster.type != "synapse"` |
| `PLATFORM_SYNAPSE` | `os.environ.get("AZURE_SERVICE") == "Microsoft.ProjectArcadia"` and `spark.cluster.type == "synapse"` |
| `PLATFORM_DATABRICKS` | `"dbfs" in os.listdir("/")` |
| `PLATFORM_FABRIC_PYTHON` | `"fabric.microsoft.com" in os.environ.get("MSNOTEBOOKUTILS_SPARK_TRIDENT_PBIHOST")` |
| `PLATFORM_BINDER` | `os.environ.get("BINDER_LAUNCH_HOST") is not None` |
| `PLATFORM_UNKNOWN` | Default fallback |

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:17-34]()

## Setup and Configuration

SynapseML provides detailed setup instructions for configuring secret management on different platforms. The primary documentation for this is located in the "Set up Cognitive Services" notebook.

### Setup Overview by Platform

```mermaid
flowchart TD
    Setup["Secret Management Setup"]
    
    subgraph "Azure Key Vault"
        CreateKV["Create Key Vault"]
        AddSecrets["Add Secrets"]
        SetPerms["Set Permissions"]
    end
    
    subgraph "Synapse Setup"
        LinkedSvc["Create Linked Service"]
        AssignRole["Assign Key Vault Administrator Role"]
    end
    
    subgraph "Databricks Setup"
        CreateScope["Create Secret Scope<br/>databricks#secrets/createScope"]
        ConfigDNS["Configure DNS Name + Resource ID"]
    end
    
    subgraph "Fabric Setup"
        FabricIAM["Configure Azure Identity"]
        FabricKVAccess["Grant Key Vault Access"]
    end
    
    Setup --> CreateKV
    CreateKV --> AddSecrets
    AddSecrets --> SetPerms
    
    SetPerms --> LinkedSvc
    LinkedSvc --> AssignRole
    
    SetPerms --> CreateScope
    CreateScope --> ConfigDNS
    
    SetPerms --> FabricIAM
    FabricIAM --> FabricKVAccess
```

**Sources:** [docs/Get Started/Set up Cognitive Services.ipynb:72-160]()

### Key Vault Creation

1. Create an Azure Key Vault via the Azure Portal
2. Navigate to Access control (IAM) and assign yourself the **Key Vault Administrator Role**
3. Go to Secrets → Generate/Import and create secrets with their values

### Platform-Specific Configuration

**Synapse:**
- Create a linked service to the Key Vault in Synapse Studio (Manage → External connections → Linked services)
- Assign the **Key Vault Administrator** role to the Synapse Workspace managed identity
- Reference the linked service name as the `keyvault` parameter in `find_secret()`

**Databricks:**
- Navigate to `https://<databricks-instance>#secrets/createScope`
- Set Permission model to "Vault access policy" in Azure Key Vault
- Configure DNS Name (Vault URI) and Resource ID from the Key Vault properties
- Reference the scope name as the `keyvault` parameter in `find_secret()`

**Fabric:**
- Assign the Fabric/Power BI Service Account the **Key Vault Administrator** role
- Ensure the Azure identity running the notebook has access to the Key Vault

**Sources:** [docs/Get Started/Set up Cognitive Services.ipynb:88-160]()

## Security Considerations

The secret management system implements several security best practices:

1. **No Hardcoded Secrets**: The system enforces retrieval from secure stores rather than embedding secrets in code
2. **Runtime Retrieval**: Secrets are fetched at runtime, not stored in notebooks or source files
3. **Platform Isolation**: Test secrets (via `Secrets` object) are isolated from production code paths
4. **Error Guidance**: Error messages guide users to secure alternatives rather than insecure workarounds
5. **Documentation Warnings**: All examples include warnings about security implications of hardcoded strings

**Sources:** [core/src/main/python/synapse/ml/core/platform/Platform.py:77-92](), [docs/Get Started/Set up Cognitive Services.ipynb:79-82]()

---

# Page: Custom Spark Data Sources

# Custom Spark Data Sources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala)
- [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala](core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala)
- [core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala](core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala)
- [start](start)
- [tools/docker/demo/Dockerfile](tools/docker/demo/Dockerfile)
- [tools/docker/demo/README.md](tools/docker/demo/README.md)
- [tools/docker/demo/init_notebook.py](tools/docker/demo/init_notebook.py)
- [tools/docker/minimal/Dockerfile](tools/docker/minimal/Dockerfile)
- [tools/tests/run_r_tests.R](tools/tests/run_r_tests.R)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala)

</details>



## Purpose and Scope

This document describes SynapseML's custom Spark data source implementations that extend Apache Spark's FileFormat API to support specialized binary data types. These custom data sources provide efficient distributed reading and writing of image files and binary data with advanced features like retry mechanisms, zip file inspection, and subsampling.

For HTTP-based streaming data sources and sinks, see [Custom HTTP Sources](#5.5.1) (note: this is conceptually related but implemented separately as streaming sources). For general I/O utilities and storage access patterns, see [Core Infrastructure](#5).

---

## Overview

SynapseML implements two primary custom FileFormat classes that integrate with Spark's DataSource V2 API:

| FileFormat Class | Short Name | Primary Use Case | Key Features |
|-----------------|------------|------------------|--------------|
| `PatchedImageFileFormat` | `patchedImage` | Image file reading/writing | JVM threading bug retry logic, origin path tracking |
| `BinaryFileFormat` | `binary` | Binary file reading/writing | Zip inspection, subsampling, configurable seed |

Both implementations extend Spark's `TextBasedFileFormat` and provide custom `RecordReader` and `OutputWriter` implementations for handling specialized data formats that Spark's built-in readers cannot efficiently process.

Sources: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:1-160](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:1-251]()

---

## Architecture and Class Hierarchy

```mermaid
graph TB
    subgraph "Spark DataSource API"
        FileFormat["FileFormat<br/>(Spark Interface)"]
        TextBasedFileFormat["TextBasedFileFormat<br/>(Spark Abstract Class)"]
        DataSourceRegister["DataSourceRegister<br/>(Spark Interface)"]
        RecordReader["RecordReader[K,V]<br/>(Hadoop Interface)"]
        OutputWriter["OutputWriter<br/>(Spark Class)"]
    end
    
    subgraph "SynapseML Image Support"
        PatchedImageFileFormat["PatchedImageFileFormat<br/>shortName: patchedImage"]
        ImageRecordReader["Implicit via buildReader<br/>catchFlakiness retry"]
        ImageOutputWriter["ImageOutputWriter<br/>Writes BufferedImage"]
    end
    
    subgraph "SynapseML Binary Support"
        BinaryFileFormat["BinaryFileFormat<br/>shortName: binary"]
        BinaryRecordReader["BinaryRecordReader<br/>subsample, inspectZip"]
        BinaryOutputWriter["BinaryOutputWriter<br/>Writes raw bytes"]
        HadoopFileReader["HadoopFileReader<br/>Iterator wrapper"]
        ZipIterator["ZipIterator<br/>Inspects zip contents"]
    end
    
    subgraph "Schema Definitions"
        ImageSchema["ImageSchema.imageSchema<br/>origin, height, width, nChannels, mode, data"]
        BinaryFileSchema["BinaryFileSchema.Schema<br/>path, bytes"]
    end
    
    FileFormat --> TextBasedFileFormat
    TextBasedFileFormat --> PatchedImageFileFormat
    TextBasedFileFormat --> BinaryFileFormat
    DataSourceRegister --> PatchedImageFileFormat
    DataSourceRegister --> BinaryFileFormat
    
    PatchedImageFileFormat --> ImageRecordReader
    PatchedImageFileFormat --> ImageOutputWriter
    PatchedImageFileFormat --> ImageSchema
    
    BinaryFileFormat --> BinaryRecordReader
    BinaryFileFormat --> BinaryOutputWriter
    BinaryFileFormat --> BinaryFileSchema
    BinaryRecordReader --> HadoopFileReader
    HadoopFileReader --> ZipIterator
    
    RecordReader -.implements.-> BinaryRecordReader
    OutputWriter -.extends.-> ImageOutputWriter
    OutputWriter -.extends.-> BinaryOutputWriter
```

**Data Source Registration and Usage**

Both FileFormats are registered via `DataSourceRegister.shortName()`, allowing usage like:
- `spark.read.format("patchedImage").load(path)`
- `spark.read.format("binary").option("inspectZip", "true").load(path)`

Sources: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:26-28](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:111-118]()

---

## Patched Image File Format

### Purpose and Design

The `PatchedImageFileFormat` addresses a critical JVM threading bug in `ImageIO.read()` that causes intermittent `NullPointerException`s during concurrent image decoding. This implementation wraps image reading in a retry mechanism with exponential backoff.

```mermaid
graph LR
    subgraph "Read Flow"
        PartitionedFile["PartitionedFile<br/>from Spark"]
        buildReader["buildReader()<br/>returns (file => Iterator[InternalRow])"]
        catchFlakiness["catchFlakiness(times=5)<br/>retry on NPE"]
        ImageSchemaDecode["ImageSchema.decode()<br/>origin, bytes"]
        InternalRow["InternalRow<br/>image struct"]
    end
    
    subgraph "Write Flow"
        DataFrame["DataFrame<br/>with image column"]
        ImageOutputWriter["ImageOutputWriter<br/>imageCol, pathCol"]
        ImageUtilsToBufferedImage["ImageUtils.toBufferedImage()<br/>imgRow => BufferedImage"]
        ImageIOWrite["ImageIO.write()<br/>codec from extension"]
        HDFSOutput["HDFS/Azure Blob<br/>output file"]
    end
    
    PartitionedFile --> buildReader
    buildReader --> catchFlakiness
    catchFlakiness --> ImageSchemaDecode
    ImageSchemaDecode --> InternalRow
    
    DataFrame --> ImageOutputWriter
    ImageOutputWriter --> ImageUtilsToBufferedImage
    ImageUtilsToBufferedImage --> ImageIOWrite
    ImageIOWrite --> HDFSOutput
```

### Retry Logic Implementation

The `catchFlakiness` method [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:66-77]() implements tail-recursive retry logic:

```scala
@annotation.tailrec
private def catchFlakiness[T](times: Int)(f: => Option[T]): Option[T] = {
  Try { f } match {
    case Success(x) => x
    case Failure(exception: NullPointerException) if times >= 1 =>
      logWarning("caught null pointer exception due to jvm bug", exception)
      catchFlakiness(times - 1)(f)
    case _ => None
  }
}
```

This wraps the `ImageSchema.decode()` call [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:110-111]() to retry up to 5 times before giving up.

### Schema Verification

The format enforces strict schema validation [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:30-40]():

**Expected Schema Structure:**
- `origin: String` - file path
- `height: Int` - image height
- `width: Int` - image width  
- `nChannels: Int` - number of color channels
- `mode: Int` - color mode constant
- `data: Binary` - raw image bytes
- `filenames: String` - (optional) for writing

### Image Output Writer

The `ImageOutputWriter` [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:131-159]() handles writing images back to disk:

1. Extracts image struct from row via `imageCol` index
2. Converts to `BufferedImage` using `ImageUtils.toBufferedImage()`
3. Derives codec from file extension (jpg, png, etc.)
4. Writes using `ImageIO.write()` to HDFS/Azure Blob

Sources: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:1-160]()

---

## Binary File Format

### Purpose and Design

The `BinaryFileFormat` provides efficient reading of arbitrary binary files with two key features:
1. **Subsampling**: Random sampling of files based on a probability threshold
2. **Zip Inspection**: Automatic extraction and processing of files within zip archives

```mermaid
graph TB
    subgraph "Configuration Options"
        subsample["subsample: Double<br/>default: 1.0<br/>range: 0.0-1.0"]
        inspectZip["inspectZip: Boolean<br/>default: false"]
        seed["seed: Long<br/>default: 0<br/>for reproducible sampling"]
    end
    
    subgraph "BinaryRecordReader Flow"
        initialize["initialize()<br/>FileSplit => InputStream"]
        checkZip{"Is .zip and<br/>inspectZip=true?"}
        createZipIterator["ZipIterator<br/>extracts zip entries"]
        directRead["IOUtils.toByteArray()<br/>read entire file"]
        subsampleCheck{"random() <= subsample?"}
        yieldRecord["yield (filename, bytes)"]
        skipRecord["skip file"]
    end
    
    subgraph "Output Schema"
        BinaryFileSchema["BinaryFileSchema.Schema<br/>value: struct<br/>- path: String<br/>- bytes: Binary"]
    end
    
    subsample --> BinaryRecordReader
    inspectZip --> BinaryRecordReader
    seed --> BinaryRecordReader
    
    initialize --> checkZip
    checkZip -->|Yes| createZipIterator
    checkZip -->|No| directRead
    
    createZipIterator --> subsampleCheck
    directRead --> subsampleCheck
    subsampleCheck -->|Pass| yieldRecord
    subsampleCheck -->|Fail| skipRecord
    
    yieldRecord --> BinaryFileSchema
```

### BinaryRecordReader Implementation

The `BinaryRecordReader` [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:33-108]() implements Hadoop's `RecordReader` interface with custom initialization:

**Key State Variables:**
- `inputStream: InputStream` - file input stream
- `filename: String` - current file path
- `recordValue: Array[Byte]` - current file bytes
- `zipIterator: ZipIterator` - for zip file processing (if enabled)
- `rng: Random` - seeded random generator for subsampling

**Initialization Process** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:62-76]():
1. Extract `FileSplit` with file path and configuration
2. Open `InputStream` from filesystem
3. Seed RNG with `filename.hashCode ^ seed` for reproducibility
4. If file extension is `.zip` and `inspectZip=true`, create `ZipIterator`

### Zip File Inspection

When `inspectZip=true`, the `ZipIterator` [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:73-74]() provides iteration over zip archive contents:

```scala
if (inspectZip && FilenameUtils.getExtension(filename) == "zip") {
    zipIterator = new ZipIterator(inputStream, filename, rng, subsample)
}
```

The `ZipIterator` is defined in `com.microsoft.azure.synapse.ml.core.env.StreamUtilities` and yields `(filename, bytes)` tuples for each entry in the zip file that passes the subsample check.

### nextKeyValue Logic

The `nextKeyValue()` method [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:83-107]() implements the record iteration logic:

| Condition | Action | Result |
|-----------|--------|--------|
| `done == true` | Return `false` | No more records |
| `zipIterator != null && hasNext` | Get next zip entry | Yield entry as record |
| `zipIterator != null && !hasNext` | Mark as done | No more zip entries |
| Regular file + subsample pass | Read entire file | Yield file as record |
| Regular file + subsample fail | Mark as done | Skip file |

### Binary Output Writer

The `BinaryOutputWriter` [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:216-242]() writes binary data to files:

1. Extracts `bytes: Binary` from row via `bytesCol` index
2. Extracts `filename: String` from row via `pathCol` index
3. Constructs output path in parent directory
4. Writes raw bytes using `IOUtils.write()`

**Configuration Options:**
- `bytesCol: String` - column containing binary data (default: "bytes")
- `pathCol: String` - column containing output filename (default: "path")

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:1-251]()

---

## Integration with Spark DataFrames

### Reading Data

Both FileFormats integrate seamlessly with Spark's DataFrame API through the `buildReader` method:

```mermaid
graph LR
    subgraph "Spark Execution"
        LogicalPlan["LogicalPlan<br/>DataFrameReader.load()"]
        PhysicalPlan["PhysicalPlan<br/>FileSourceScanExec"]
        TaskExecution["Task Execution<br/>PartitionedFile => Iterator[InternalRow]"]
    end
    
    subgraph "FileFormat Contract"
        inferSchema["inferSchema()<br/>returns StructType"]
        buildReader["buildReader()<br/>returns function"]
        PartitionedFileToRows["(PartitionedFile) => Iterator[InternalRow]<br/>executed on executors"]
    end
    
    subgraph "Custom Implementation"
        BroadcastConf["Broadcast hadoopConf<br/>SerializableConfiguration"]
        RecordReader["RecordReader or<br/>custom iteration"]
        SchemaConversion["Convert to InternalRow<br/>ExpressionEncoder"]
    end
    
    LogicalPlan --> inferSchema
    inferSchema --> PhysicalPlan
    PhysicalPlan --> buildReader
    buildReader --> TaskExecution
    TaskExecution --> PartitionedFileToRows
    
    PartitionedFileToRows --> BroadcastConf
    PartitionedFileToRows --> RecordReader
    RecordReader --> SchemaConversion
```

**Key Implementation Details:**

1. **Schema Inference** [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:119-124]():
   - `BinaryFileFormat` returns fixed `BinaryFileSchema.Schema`
   - `PatchedImageFileFormat` returns `ImageSchema.imageSchema` with optional filenames column

2. **Broadcast Configuration**: Both formats broadcast Hadoop configuration to avoid serialization overhead [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:90-91]()

3. **Task Cleanup**: Binary format registers task completion listeners for resource cleanup [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:166]()

### Writing Data

The `prepareWrite` method configures output writing:

```mermaid
graph TB
    subgraph "Write Configuration"
        prepareWrite["prepareWrite()<br/>Job, options, dataSchema"]
        verifySchema["verifySchema()<br/>validate structure"]
        OutputWriterFactory["OutputWriterFactory<br/>newInstance per task"]
    end
    
    subgraph "Per-Task Execution"
        TaskAttemptContext["TaskAttemptContext<br/>Hadoop context"]
        OutputWriter["OutputWriter.write(row)<br/>for each output row"]
        FileSystem["FileSystem<br/>HDFS/Azure Blob"]
    end
    
    prepareWrite --> verifySchema
    verifySchema --> OutputWriterFactory
    OutputWriterFactory --> TaskAttemptContext
    TaskAttemptContext --> OutputWriter
    OutputWriter --> FileSystem
```

**Output Options:**

| Format | Options | Description |
|--------|---------|-------------|
| `patchedImage` | `imageCol`, `pathCol` | Column names for image data and output paths |
| `binary` | `bytesCol`, `pathCol` | Column names for binary data and output paths |

Both writers follow the pattern:
1. Extract data from specified columns using field indices
2. Construct output path in parent directory (non-temp location)
3. Write to filesystem using appropriate encoder (ImageIO vs raw bytes)
4. Close resources in `close()` method

Sources: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:42-63](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:126-146]()

---

## Usage in SynapseML Components

### Vowpal Wabbit Model Storage

The `BinaryFileFormat` is used by Vowpal Wabbit to save trained models [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala:71-80]():

```scala
def saveNativeModel(path: String): Unit = {
  val session = SparkSession.builder().getOrCreate()
  val f = new java.io.File(path)
  
  session.createDataFrame(Seq(PathAndData(f.getName, getModel)))
    .write.mode("overwrite")
    .format(classOf[BinaryFileFormat].getName)
    .save(f.getPath)
}
```

This stores the native VW model bytes as a binary file that can be distributed and loaded across cluster nodes.

### Docker Environment Configuration

Docker images configure Azure Blob filesystem support for reading/writing files [tools/docker/demo/init_notebook.py:5-38]():

```python
"spark.hadoop.fs.AbstractFileSystem.wasb.impl": "org.apache.hadoop.fs.azure.Wasb",
"spark.hadoop.fs.wasbs.impl": "org.apache.hadoop.fs.azure.NativeAzureFileSystem",
```

This allows the custom FileFormats to transparently read from Azure Blob Storage paths in addition to HDFS.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala:71-80](), [tools/docker/demo/init_notebook.py:5-38]()

---

## Testing Infrastructure

### Image Format Tests

Tests verify the retry mechanism and proper handling of image decoding failures. The `catchFlakiness` method is tested by intentionally triggering `NullPointerException`s and verifying retry behavior.

### Binary Format Tests

The test suite validates:
- **Subsampling**: Files are randomly sampled according to configured probability
- **Zip Inspection**: Zip archives are properly expanded and individual entries processed
- **Reproducibility**: Given the same seed, the same files are sampled across runs

### HTTP Source Integration Tests

The `DistributedHTTPSuite` [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala:161-410]() validates integration with HTTP streaming sources, testing:
- Request handling and response generation
- Latency measurement and performance assertions
- Concurrent client requests
- State management via `SharedSingleton`

Key test utilities include:
- `waitForServer()` - waits for streaming query to become active [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala:34-43]()
- `sendFileRequest()` - sends image files and measures latency [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala:112-123]()
- `assertLatency()` - validates median latency below cutoff [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala:146-156]()

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala:1-411]()

---

## Configuration Reference

### BinaryFileFormat Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `subsample` | Double | 1.0 | Probability of including each file (0.0-1.0) |
| `inspectZip` | Boolean | false | Whether to expand and process zip file contents |
| `seed` | Long | 0 | Random seed for reproducible subsampling |
| `bytesCol` | String | "bytes" | Column name for binary data when writing |
| `pathCol` | String | "path" | Column name for file paths when writing |

### PatchedImageFileFormat Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dropInvalid` | Boolean | false | Whether to drop images that fail to decode |
| `imageCol` | String | "image" | Column name for image data when writing |
| `pathCol` | String | "filenames" | Column name for file paths when writing |

### Read Examples

```scala
// Read binary files with subsampling
val binaryDF = spark.read
  .format("binary")
  .option("subsample", "0.1")
  .option("seed", "42")
  .load("wasbs://container@account.blob.core.windows.net/data/*.bin")

// Read zip archives and expand contents
val zipDF = spark.read
  .format("binary")
  .option("inspectZip", "true")
  .load("hdfs:///data/archives/*.zip")

// Read images with invalid handling
val imageDF = spark.read
  .format("patchedImage")
  .option("dropInvalid", "true")
  .load("s3a://bucket/images/")
```

### Write Examples

```scala
// Write binary data
binaryDF.write
  .format("binary")
  .option("bytesCol", "data")
  .option("pathCol", "filename")
  .save("hdfs:///output/")

// Write images
imageDF.write
  .format("patchedImage")
  .option("imageCol", "image")
  .option("pathCol", "filenames")
  .save("wasbs://container@account.blob.core.windows.net/images/")
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:159-162](), [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:93]()

---

## Performance Considerations

### Image Decoding Retry Overhead

The retry mechanism in `PatchedImageFileFormat` adds minimal overhead (typically <1% of total decode time) but prevents rare catastrophic failures. The tail-recursive implementation avoids stack overflow issues.

### Binary File Subsampling

Subsampling is performed probabilistically per file, not per record, making it highly efficient:
- Decision made once per `PartitionedFile` 
- No bytes read if file fails subsample check (except for metadata)
- RNG seeded deterministically for reproducibility

### Zip File Processing

When `inspectZip=true`, memory overhead is proportional to the largest individual entry in the zip file, not the entire archive. The `ZipIterator` streams entries sequentially, allowing processing of large archives without loading everything into memory.

### Partitioning Strategy

Both FileFormats set `isSplitable = false` [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:113-115](), meaning each file is processed as a single unit. For optimal parallelism:
- Distribute input files across many smaller files rather than few large files
- Each file becomes a single partition
- Zip file inspection can yield multiple records per partition

Sources: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:66-77](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:33-108]()

---

# Page: AI Services Integration

# AI Services Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py](cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py)
- [cognitive/src/main/python/synapse/ml/services/openai/__init__.py](cognitive/src/main/python/synapse/ml/services/openai/__init__.py)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala)
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py](cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala)
- [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](docs/Explore Algorithms/OpenAI/OpenAI.ipynb)

</details>



## Purpose and Scope

This document describes the AI services integration layer in SynapseML, which provides unified Spark DataFrame interfaces to external AI services and distributed ML algorithms. The integration layer abstracts HTTP communication, authentication, parameter management, and platform-specific behaviors to enable scalable processing of AI workloads on Apache Spark.

This page covers the common architecture and patterns shared across all AI service integrations. For details on specific services:
- OpenAI services (chat, completion, embedding, prompting) - see [OpenAI Integration](#6.1)
- Legacy Azure Cognitive Services (vision, text analytics) - see [Azure Cognitive Services](#6.2)  
- LangChain distributed execution - see [LangChain Integration](#6.3)
- Deep learning with ONNX and Horovod - see [Deep Learning Integration](#6.4)
- LightGBM gradient boosting - see [LightGBM Integration](#6.5)
- Vowpal Wabbit online learning - see [Vowpal Wabbit Integration](#6.6)

For deployment and platform-specific configurations, see [Deployment](#8).

---

## Architecture Overview

### Foundation: CognitiveServicesBase

All AI service integrations extend from `CognitiveServicesBase`, which provides the foundational infrastructure for HTTP-based service calls distributed across Spark executors.

**Class Hierarchy**

```mermaid
graph TB
    CognitiveServicesBaseNoHandler["CognitiveServicesBaseNoHandler"]
    CognitiveServicesBase["CognitiveServicesBase"]
    OpenAIServicesBase["OpenAIServicesBase"]
    
    OpenAIChatCompletion["OpenAIChatCompletion"]
    OpenAICompletion["OpenAICompletion"]
    OpenAIEmbedding["OpenAIEmbedding"]
    OpenAIResponses["OpenAIResponses"]
    OpenAIPrompt["OpenAIPrompt"]
    AIFoundryChatCompletion["AIFoundryChatCompletion"]
    
    CognitiveServicesBaseNoHandler --> CognitiveServicesBase
    CognitiveServicesBase --> OpenAIServicesBase
    
    OpenAIServicesBase --> OpenAIChatCompletion
    OpenAIServicesBase --> OpenAICompletion
    OpenAIServicesBase --> OpenAIEmbedding
    OpenAIServicesBase --> OpenAIResponses
    
    OpenAIChatCompletion --> AIFoundryChatCompletion
    
    OpenAIPrompt["OpenAIPrompt<br/>(Transformer)"]
    
    style CognitiveServicesBase fill:#e6e6ff
    style OpenAIServicesBase fill:#cce5ff
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:542-615](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:412-427]()

### Core Responsibilities

`CognitiveServicesBase` provides:

| Responsibility | Implementation | Key Classes/Traits |
|----------------|----------------|-------------------|
| HTTP Request Construction | `inputFunc()` creates `HttpRequestBase` per row | `HasCognitiveServiceInput` |
| Authentication | Subscription key, AAD token, or custom auth headers | `HasSubscriptionKey`, `HasAADToken`, `HasCustomAuthHeader` |
| URL Management | URL construction with path and query parameters | `HasURL`, `HasUrlPath`, `HasAPIVersion` |
| Response Parsing | JSON parsing to Spark DataTypes | `HasInternalJsonOutputParser` |
| Error Handling | Error column for failed requests | `HasErrorCol` |
| Concurrency Control | Parallel HTTP requests across partitions | `ConcurrencyParams` |
| Platform Adaptation | Platform-specific endpoints and tokens | Platform detection via `PlatformDetails` |

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:1-615]()

### Parameter Management System

Services use `ServiceParam[T]` to support both scalar values and column references:

```mermaid
graph LR
    ServiceParam["ServiceParam[T]<br/>Either[T, String]"]
    Scalar["Scalar Value<br/>Left(value: T)"]
    Column["Column Reference<br/>Right(colName: String)"]
    
    ServiceParam --> Scalar
    ServiceParam --> Column
    
    Scalar --> RowValue["Per-row: Same value"]
    Column --> RowValue["Per-row: Column value"]
```

Example from `HasOpenAITextParams`:
- `temperature: ServiceParam[Double]` can be set as `.setTemperature(0.7)` (scalar) or `.setTemperatureCol("temp_col")` (column)
- At runtime, `getValue(row, temperature)` extracts the appropriate value per row

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:34-131](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:19-352]()

---

## Service Categories

### Generative AI Services

**OpenAI and Azure OpenAI**

```mermaid
graph TB
    subgraph "OpenAI Service Classes"
        OpenAIChatCompletion["OpenAIChatCompletion<br/>Chat Completions API"]
        OpenAICompletion["OpenAICompletion<br/>Legacy Completions API"]
        OpenAIResponses["OpenAIResponses<br/>Responses API (2025-04-01-preview)"]
        OpenAIEmbedding["OpenAIEmbedding<br/>Embeddings API"]
        OpenAIPrompt["OpenAIPrompt<br/>High-level prompt templating"]
    end
    
    subgraph "AI Foundry"
        AIFoundryChatCompletion["AIFoundryChatCompletion<br/>AI Foundry Chat API"]
    end
    
    subgraph "Supporting Components"
        OpenAIDefaults["OpenAIDefaults<br/>Global parameter defaults"]
        HasOpenAITextParams["HasOpenAITextParams<br/>Shared text generation params"]
        HasMessagesInput["HasMessagesInput<br/>Message-based input"]
        HasPromptInputs["HasPromptInputs<br/>Prompt-based input"]
    end
    
    OpenAIChatCompletion --> HasOpenAITextParams
    OpenAIChatCompletion --> HasMessagesInput
    OpenAICompletion --> HasOpenAITextParams
    OpenAICompletion --> HasPromptInputs
    OpenAIResponses --> HasOpenAITextParams
    OpenAIResponses --> HasMessagesInput
    
    AIFoundryChatCompletion -.extends.-> OpenAIChatCompletion
    
    OpenAIPrompt --> OpenAIChatCompletion
    OpenAIPrompt --> OpenAICompletion
    OpenAIPrompt --> OpenAIResponses
    
    OpenAIDefaults -.provides defaults to.-> OpenAIChatCompletion
    OpenAIDefaults -.provides defaults to.-> OpenAICompletion
    OpenAIDefaults -.provides defaults to.-> OpenAIEmbedding
```

**Service Comparison**

| Service | API Type | Primary Use Case | Input Format | Output Schema |
|---------|----------|------------------|--------------|---------------|
| `OpenAIChatCompletion` | Chat Completions | Multi-turn conversations | `messagesCol` (Array of messages) | `ChatModelResponse` |
| `OpenAIResponses` | Responses (preview) | Multimodal with files/images | `messagesCol` (Array of composite messages) | `ResponsesModelResponse` |
| `OpenAICompletion` | Completions (legacy) | Simple text completion | `promptCol` or `batchPromptCol` | `CompletionResponse` |
| `OpenAIEmbedding` | Embeddings | Vector generation | `textCol` | `Vector` (MLlib) |
| `OpenAIPrompt` | High-level wrapper | Prompt templating with post-processing | Template string with column interpolation | Configurable (CSV, JSON, regex, text) |
| `AIFoundryChatCompletion` | AI Foundry Chat | Foundry model endpoints | `messagesCol` + `model` param | `ChatModelResponse` |

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:1-171](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala:1-71](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:1-198](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala:1-100](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:1-573](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala:1-66]()

**Key Parameters** (from `HasOpenAITextParams`)

| Parameter | Type | Description | Payload Name |
|-----------|------|-------------|--------------|
| `deploymentName` | `ServiceParam[String]` | Azure OpenAI deployment name | - |
| `maxTokens` | `ServiceParam[Int]` | Maximum tokens to generate | `max_tokens` |
| `temperature` | `ServiceParam[Double]` | Sampling temperature (0-2) | `temperature` |
| `topP` | `ServiceParam[Double]` | Nucleus sampling (0-1) | `top_p` |
| `seed` | `ServiceParam[Int]` | Deterministic sampling seed | `seed` |
| `verbosity` | `ServiceParam[String]` | Response verbosity hint | `verbosity` |
| `reasoningEffort` | `ServiceParam[String]` | Reasoning effort level | `reasoning_effort` |
| `responseFormat` | `ServiceParam[Map[String, Any]]` | Response format (text, json_object, json_schema) | `response_format` |

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:112-353](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:21-93]()

### Traditional Machine Learning

Services for gradient boosting and online learning are documented separately:
- **LightGBM**: Distributed gradient boosted decision trees - see [LightGBM Integration](#6.5)
- **Vowpal Wabbit**: Fast online learning and contextual bandits - see [Vowpal Wabbit Integration](#6.6)

### Deep Learning

ONNX model inference and Horovod distributed training are covered in [Deep Learning Integration](#6.4).

---

## Global Parameter Defaults

### OpenAIDefaults System

`OpenAIDefaults` provides static methods to set global default values for OpenAI parameters, reducing boilerplate when creating multiple transformers.

**Supported Global Parameters**

```mermaid
graph LR
    subgraph "Global Keys"
        OpenAIDeploymentNameKey
        OpenAIEmbeddingDeploymentNameKey
        OpenAISubscriptionKey
        OpenAIApiVersion
        OpenAITemperatureKey
        OpenAISeedKey
        OpenAITopPKey
        OpenAIVerbosityKey
        OpenAIReasoningEffortKey
        URLKey
        AIFoundryModel
    end
    
    subgraph "GlobalParams Registry"
        ParamToKeyMap["ParamToKeyMap<br/>Maps params to keys"]
        GlobalParamsMap["GlobalParams Map<br/>Stores values"]
    end
    
    OpenAIDeploymentNameKey --> GlobalParamsMap
    OpenAISubscriptionKey --> GlobalParamsMap
    OpenAITemperatureKey --> GlobalParamsMap
    
    ServiceParam["ServiceParam instances"] --> ParamToKeyMap
    ParamToKeyMap --> GlobalParamsMap
```

**Usage Pattern**

```scala
// Set global defaults (Scala)
OpenAIDefaults.setDeploymentName("gpt-4")
OpenAIDefaults.setSubscriptionKey(apiKey)
OpenAIDefaults.setTemperature(0.0)
OpenAIDefaults.setSeed(42)

// Transformers automatically pick up defaults
val completion = new OpenAIChatCompletion()
  .setMessagesCol("messages")
  .setOutputCol("out")
// deploymentName, subscriptionKey, temperature, seed inherited from defaults
```

**Python API**

The Python wrapper provides equivalent methods:

```python
# Python
from synapse.ml.services.openai.OpenAIDefaults import OpenAIDefaults

defaults = OpenAIDefaults()
defaults.set_deployment_name("gpt-4")
defaults.set_subscription_key(api_key)
defaults.set_temperature(0.0)
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala:1-154](), [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py:1-131](), [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:1-57]()

### Global Parameter Registration

Services register their parameters with global keys:

```scala
// From OpenAI.scala
val deploymentName = new ServiceParam[String](...)
GlobalParams.registerParam(deploymentName, OpenAIDeploymentNameKey)

val temperature = new ServiceParam[Double](...)
GlobalParams.registerParam(temperature, OpenAITemperatureKey)
```

The `HasGlobalParams` trait transfers global values to instance parameters before transformation:

```scala
// From HasGlobalParams
private[ml] def transferGlobalParamsToParamMap(): Unit = {
  this.params
    .filter(p => !this.isSet(p))
    .foreach { p =>
      GlobalParams.getParam(p).foreach { v =>
        set(p.asInstanceOf[Param[Any]], v)
      }
    }
}
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:54-73,134-169,286-294](), [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:12-56]()

---

## Authentication and Authorization

### Authentication Methods

```mermaid
graph TB
    Request["HTTP Request"]
    
    subgraph "Authentication Options"
        SubscriptionKey["Subscription Key<br/>HasSubscriptionKey"]
        AADToken["AAD Token<br/>HasAADToken"]
        CustomAuthHeader["Custom Auth Header<br/>HasCustomAuthHeader"]
        FabricToken["Fabric Platform Token<br/>PlatformDetails + FabricClient"]
    end
    
    Request --> SubscriptionKey
    Request --> AADToken
    Request --> CustomAuthHeader
    Request --> FabricToken
    
    SubscriptionKey --> Header1["Header: Ocp-Apim-Subscription-Key<br/>or api-key"]
    AADToken --> Header2["Header: Authorization Bearer"]
    CustomAuthHeader --> Header3["Header: Authorization (custom)"]
    FabricToken --> Header4["Header: Authorization Bearer<br/>(auto-injected)"]
```

**Priority Order** (from `getHeaders()` in `HasCognitiveServiceInput`):

1. **Subscription Key**: If `subscriptionKey` is set, uses `Ocp-Apim-Subscription-Key` or `api-key` header (service-specific)
2. **AAD Token**: If `AADToken` is set, uses `Authorization: Bearer <token>` header
3. **Custom Auth Header**: If `CustomAuthHeader` is set, uses custom `Authorization` header value
4. **Fabric Auto-injection**: On Microsoft Fabric platform, automatically injects token from `FabricClient.getCognitiveMWCTokenAuthHeader()`

**Example Authentication Setup**

```scala
// Subscription key
val completion = new OpenAIChatCompletion()
  .setSubscriptionKey("your-api-key")
  .setCustomServiceName("your-openai-service")

// AAD token
val completion = new OpenAIChatCompletion()
  .setAADToken("eyJ0eXAiOiJKV1QiLCJhbGc...")
  .setCustomServiceName("your-openai-service")

// On Fabric - automatic
val completion = new OpenAIChatCompletion()
  .setCustomServiceName("your-openai-service")
  // Token auto-injected
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:133-195,311-429]()

### Custom Headers

Services support custom HTTP headers via `HasCustomHeaders` for scenarios requiring additional metadata:

```scala
completion.setCustomHeaders(Map(
  "X-ModelType" -> "gpt-4-turbo-chat-completions",
  "X-Custom-Metadata" -> "value"
))
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:197-212,373-415]()

---

## Request Construction and Execution Flow

### DataFrame to HTTP Request Pipeline

```mermaid
graph TB
    DataFrame["Input DataFrame"]
    InternalTransformer["getInternalTransformer(schema)"]
    
    DynamicCol["Add dynamic param column<br/>struct(vectorParams...)"]
    SimpleHTTP["SimpleHTTPTransformer"]
    DropCol["Drop dynamic column"]
    
    InputParser["HTTPInputParser<br/>inputFunc(schema)"]
    OutputParser["HTTPOutputParser<br/>getInternalOutputParser(schema)"]
    
    PerRow["Per Row Processing"]
    PrepareURL["prepareUrl(row)"]
    PrepareEntity["prepareEntity(row)"]
    AddHeaders["addHeaders(req, row)"]
    HTTPRequest["HttpRequestBase"]
    
    HTTPClient["HTTP Client<br/>handlingFunc()"]
    Response["HTTPResponseData"]
    ParseJSON["Parse JSON to Row"]
    
    DataFrame --> InternalTransformer
    InternalTransformer --> DynamicCol
    DynamicCol --> SimpleHTTP
    SimpleHTTP --> InputParser
    InputParser --> PerRow
    
    PerRow --> PrepareURL
    PerRow --> PrepareEntity
    PerRow --> AddHeaders
    PrepareURL --> HTTPRequest
    PrepareEntity --> HTTPRequest
    AddHeaders --> HTTPRequest
    
    HTTPRequest --> HTTPClient
    HTTPClient --> Response
    Response --> OutputParser
    OutputParser --> ParseJSON
    
    SimpleHTTP --> DropCol
    ParseJSON --> DropCol
    DropCol --> OutputDF["Output DataFrame"]
    
    style SimpleHTTP fill:#e6e6ff
    style InputParser fill:#cce5ff
    style OutputParser fill:#cce5ff
```

**Key Methods in Request Construction**

| Method | Purpose | Returns | Example |
|--------|---------|---------|---------|
| `prepareUrlRoot(row)` | Constructs base URL + path | `String` | `"https://service.openai.azure.com/openai/deployments/gpt-4/chat/completions"` |
| `prepareUrl(row)` | Adds query parameters | `String` | `prepareUrlRoot + "?api-version=2024-02-01"` |
| `prepareEntity(row)` | Creates request body | `Option[AbstractHttpEntity]` | `StringEntity(jsonPayload)` |
| `prepareMethod()` | HTTP method | `HttpRequestBase` | `HttpPost()` |
| `addHeaders(req, row)` | Adds auth + custom headers | `Unit` (mutates req) | Adds `api-key`, `Content-Type`, etc. |

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:329-454,558-598]()

### OpenAI-Specific Request Construction

For `OpenAIChatCompletion`, the entity preparation process:

```scala
override protected def prepareEntity: Row => Option[AbstractHttpEntity] = { r =>
  lazy val optionalParams: Map[String, Any] = getOptionalParams(r)
  val messages = r.getAs[Seq[Row]](getMessagesCol)
  Some(getStringEntity(messages, optionalParams))
}

private[openai] def getStringEntity(messages: Seq[Row], optionalParams: Map[String, Any]): StringEntity = {
  val mappedMessages = encodeMessagesToMap(messages)
    .map(_.filter { case (_, value) => value != null })
  val fullPayload = optionalParams.updated("messages", mappedMessages)
  new StringEntity(fullPayload.toJson.compactPrint, ContentType.APPLICATION_JSON)
}
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:118-152]()

---

## Response Processing and Schema Management

### Response Data Types

Each service defines a case class for its response schema, which is automatically converted to Spark `StructType`:

**OpenAI Response Schemas**

```mermaid
graph TB
    subgraph "Chat Completions"
        ChatModelResponse["ChatModelResponse"]
        ChatUsage["ChatUsage"]
        OpenAIChatChoice["OpenAIChatChoice"]
        OpenAIMessage["OpenAIMessage"]
        
        ChatModelResponse --> ChatUsage
        ChatModelResponse --> OpenAIChatChoice
        OpenAIChatChoice --> OpenAIMessage
    end
    
    subgraph "Completions (Legacy)"
        CompletionResponse["CompletionResponse"]
        OpenAIChoice["OpenAIChoice"]
        OpenAILogProbs["OpenAILogProbs"]
        
        CompletionResponse --> OpenAIChoice
        OpenAIChoice --> OpenAILogProbs
    end
    
    subgraph "Embeddings"
        EmbeddingResponse["EmbeddingResponse"]
        EmbeddingObject["EmbeddingObject"]
        Vector["MLlib Vector"]
        
        EmbeddingResponse --> EmbeddingObject
        EmbeddingObject --> Vector
    end
    
    subgraph "Responses API"
        ResponsesModelResponse["ResponsesModelResponse"]
        OpenAIResponsesChoice["OpenAIResponsesChoice"]
        ResponsesOutputContentComponent["ResponsesOutputContentComponent"]
        
        ResponsesModelResponse --> OpenAIResponsesChoice
        OpenAIResponsesChoice --> ResponsesOutputContentComponent
    end
```

**Schema Definitions** (from `OpenAISchemas.scala`):

```scala
case class ChatModelResponse(
  id: String,
  `object`: String,
  created: String,
  model: String,
  choices: Seq[OpenAIChatChoice],
  system_fingerprint: Option[String],
  usage: Option[ChatUsage]
)

case class OpenAIChatChoice(
  message: OpenAIMessage,
  index: Long,
  finish_reason: String
)

case class OpenAIMessage(
  role: String,
  content: String,
  name: Option[String] = None
)
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala:1-80]()

### JSON Parsing and Output Transformation

Services use `JSONOutputParser` to convert HTTP responses to Spark Rows:

```scala
// From OpenAIChatCompletion
override protected def getInternalOutputParser(schema: StructType): HTTPOutputParser = {
  new JSONOutputParser().setDataType(responseDataType)
}

override def responseDataType: DataType = ChatModelResponse.schema
```

For `OpenAIEmbedding`, a post-processing function converts the response to MLlib `Vector`:

```scala
override protected def getInternalOutputParser(schema: StructType): JSONOutputParser = {
  def responseToVector(r: Row) =
    if (r == null) None
    else Some(Vectors.dense(r.getAs[Seq[Row]]("data").head.getAs[Seq[Double]]("embedding").toArray))

  new JSONOutputParser()
    .setDataType(EmbeddingResponse.schema)
    .setPostProcessFunc[Row, Option[Vector]](responseToVector, VectorType)
}
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:457-464](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala:49-59]()

---

## OpenAIPrompt: High-Level Templating

### Purpose

`OpenAIPrompt` provides a unified interface for prompt templating, multimodal input handling, and response post-processing. It internally delegates to appropriate service classes (`OpenAIChatCompletion`, `OpenAICompletion`, `OpenAIResponses`, or `AIFoundryChatCompletion`) based on configuration.

### Architecture

```mermaid
graph TB
    OpenAIPrompt["OpenAIPrompt"]
    
    subgraph "Configuration Parameters"
        promptTemplate["promptTemplate<br/>String interpolation"]
        columnTypes["columnTypes<br/>Map[colName -> 'text'|'path']"]
        apiType["apiType<br/>'chat_completions'|'responses'"]
        postProcessing["postProcessing<br/>'csv'|'json'|'regex'"]
        systemPrompt["systemPrompt"]
    end
    
    subgraph "Service Selection"
        hasAIFoundryModel["hasAIFoundryModel?"]
        isLegacyModel["isLegacyModel?"]
        apiTypeCheck["apiType?"]
    end
    
    subgraph "Delegated Services"
        AIFoundryChatCompletion
        OpenAICompletion
        OpenAIChatCompletion
        OpenAIResponses
    end
    
    subgraph "Post-Processing"
        PassThroughParser
        DelimiterParser
        JsonParser
        RegexParser
    end
    
    OpenAIPrompt --> promptTemplate
    OpenAIPrompt --> columnTypes
    OpenAIPrompt --> apiType
    OpenAIPrompt --> postProcessing
    
    OpenAIPrompt --> hasAIFoundryModel
    hasAIFoundryModel -->|Yes| AIFoundryChatCompletion
    hasAIFoundryModel -->|No| isLegacyModel
    isLegacyModel -->|Yes| OpenAICompletion
    isLegacyModel -->|No| apiTypeCheck
    apiTypeCheck -->|"responses"| OpenAIResponses
    apiTypeCheck -->|"chat_completions"| OpenAIChatCompletion
    
    OpenAIChatCompletion --> PassThroughParser
    OpenAIChatCompletion --> DelimiterParser
    OpenAIChatCompletion --> JsonParser
    OpenAIChatCompletion --> RegexParser
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:39-573]()

### Prompt Templating

Supports string interpolation with column references:

```scala
val prompt = new OpenAIPrompt()
  .setPromptTemplate("Give me a comma separated list of 5 {category}, starting with {text}")
  .setOutputCol("result")

// For DataFrame with columns: text, category
// Generates prompts like: "Give me a comma separated list of 5 fruits, starting with apple"
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:58-63,289-291]()

### Multimodal Input Handling

`columnTypes` parameter specifies which columns contain file paths for multimodal inputs:

```scala
val prompt = new OpenAIPrompt()
  .setPromptTemplate("Describe this image: {imagePath}")
  .setColumnType("imagePath", "path")  // Marks column as file path
  .setApiType("responses")  // Required for multimodal
```

For path columns, `OpenAIPrompt`:
1. Replaces `{columnName}` with placeholder text in template
2. Reads file contents using `BinaryFileReader`
3. Encodes as base64 for images or includes text content
4. Constructs `OpenAICompositeMessage` with content parts

**Path Column Processing Flow**

```mermaid
graph LR
    Template["Template with {filePath}"]
    Placeholder["Replace with placeholder<br/>applyPathPlaceholders()"]
    CreateMessages["createMessagesForRow()"]
    
    ReadFile["Read file bytes<br/>BinaryFileReader"]
    DetectType["Detect MIME type<br/>categorizeFileType()"]
    
    subgraph "File Type Handlers"
        TextHandler["Text: Include content"]
        ImageHandler["Image: Base64 data URL"]
        FileHandler["File: Base64 with metadata"]
    end
    
    CompositeMessage["OpenAICompositeMessage<br/>Seq[Map[String,String]]"]
    
    Template --> Placeholder
    Placeholder --> CreateMessages
    CreateMessages --> ReadFile
    ReadFile --> DetectType
    
    DetectType --> TextHandler
    DetectType --> ImageHandler
    DetectType --> FileHandler
    
    TextHandler --> CompositeMessage
    ImageHandler --> CompositeMessage
    FileHandler --> CompositeMessage
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:130-155,194-448]()

### Post-Processing Parsers

Parse service responses into structured formats:

| Parser | Configuration | Output Type | Example |
|--------|--------------|-------------|---------|
| `PassThroughParser` | `postProcessing=""` | `StringType` | Raw text response |
| `DelimiterParser` | `postProcessing="csv"`, `delimiter=","` | `ArrayType(StringType)` | `["apple", "orange", "banana"]` |
| `JsonParser` | `postProcessing="json"`, `jsonSchema="..."` | DDL schema | Structured data |
| `RegexParser` | `postProcessing="regex"`, `regex="..."`, `regexGroup=0` | `StringType` | Extracted pattern |

**JSON Schema Example**

```scala
prompt.setPostProcessingOptions(Map(
  "jsonSchema" -> "name STRING, age INT, city STRING"
))
// Output: Row(name="John", age=30, city="Seattle")
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:535-573]()

---

## Platform-Specific Adaptations

### Platform Detection

Services detect the execution platform to adapt endpoints, authentication, and telemetry:

```scala
// From CognitiveServicesBase constructor
if (PlatformDetails.runningOnFabric()) {
  setDefaultInternalEndpoint(FabricClient.MLWorkloadEndpointML)
}

// From OpenAIServicesBase
override protected def getInternalTransformer(schema: StructType): PipelineModel = {
  if (PlatformDetails.runningOnFabric() && usingDefaultOpenAIEndpoint) {
    assertModelStatus(getDeploymentName)  // Check model availability on Fabric
  }
  super.getInternalTransformer(schema)
}
```

**Platform-Specific Behaviors**

| Platform | Endpoint Default | Authentication | Special Handling |
|----------|-----------------|----------------|------------------|
| **Microsoft Fabric** | `FabricClient.MLWorkloadEndpointML + "/cognitive/openai/"` | Auto-injected token from `FabricClient.getCognitiveMWCTokenAuthHeader()` | Model status validation |
| **Synapse Analytics** | Custom service name required | Subscription key or AAD token | - |
| **Databricks** | Custom service name required | Subscription key or AAD token | - |
| **Standalone** | Custom service name required | Subscription key or AAD token | - |

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:554-556](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:416-425](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:363-371]()

### Fabric Model Status Validation

On Fabric, when using the default internal endpoint, services validate that the requested deployment/model is available:

```scala
private def usingDefaultOpenAIEndpoint(): Boolean = {
  getUrl == FabricClient.MLWorkloadEndpointML + "/cognitive/openai/"
}

override protected def getInternalTransformer(schema: StructType): PipelineModel = {
  if (PlatformDetails.runningOnFabric() && usingDefaultOpenAIEndpoint) {
    assertModelStatus(getDeploymentName)  // Throws if model unavailable
  }
  super.getInternalTransformer(schema)
}
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:416-425]()

For more details on platform integration, see [Platform Detection and Adaptation](#2.3) and [Microsoft Fabric Deployment](#8.4).

---

## Integration with Core Infrastructure

### HTTP Client Infrastructure

AI services leverage the shared HTTP client system for connection pooling, retry logic, and timeout management. See [HTTP Client System](#5.2) for details on:
- `SimpleHTTPTransformer` for request execution
- Connection pooling via `PoolingHttpClientConnectionManager`
- Retry mechanisms in `HandlingUtils`
- Async vs. sync client selection

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:584-593]()

### Logging and Telemetry

Services use `SynapseMLLogging` for platform-aware telemetry:

```scala
class OpenAIChatCompletion(override val uid: String) extends OpenAIServicesBase(uid)
  with ... with SynapseMLLogging {
  logClass(FeatureNames.AiServices.OpenAI)
  
  override def transform(dataset: Dataset[_]): DataFrame = {
    transferGlobalParamsToParamMap()
    logTransform[DataFrame](
      getInternalTransformer(dataset.schema).transform(dataset),
      dataset.columns.length
    )
  }
}
```

See [Logging System](#5.1) for logging infrastructure details.

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:6,97-100]()

### Secret Management

Services integrate with the platform-agnostic secret retrieval system:

```scala
// From test code showing secret usage
val key = find_secret(
  secret_name="openai-api-key-2",
  keyvault="mmlspark-build-keys"
)

completion.setSubscriptionKey(key)
```

See [Secret Management](#5.4) for the `Secrets` object and `getSecret()` method.

**Sources:** [docs/Explore Algorithms/OpenAI/OpenAI.ipynb:69-72]()

---

## Error Handling and Content Filtering

### Error Column Pattern

All services provide an error column (via `HasErrorCol`) that captures HTTP errors, JSON parsing failures, and service-specific errors:

```scala
val completion = new OpenAIChatCompletion()
  .setErrorCol("error")
  .setOutputCol("result")

// Output schema includes both result and error columns
// Row(result=..., error=null) for success
// Row(result=null, error=Row(message=..., ...)) for failure
```

### RAI Content Filtering

OpenAI services implement `HasRAIContentFilter` to detect and handle content filtered by Azure's Responsible AI systems:

```scala
trait HasRAIContentFilter {
  private[openai] def isContentFiltered(outputRow: Row): Boolean
  private[openai] def getFilterReason(outputRow: Row): String
}

// In OpenAIChatCompletion
override private[openai] def isContentFiltered(outputRow: Row): Boolean = {
  val result = ChatModelResponse.makeFromRowConverter(outputRow)
  val firstChoice = result.choices.head
  Option(firstChoice.message.content).isEmpty  // Null content indicates filtering
}

override private[openai] def getFilterReason(outputRow: Row): String = {
  val result = ChatModelResponse.makeFromRowConverter(outputRow)
  result.choices.head.finish_reason  // e.g., "content_filter"
}
```

When content is filtered, `OpenAIPrompt.addRAIErrors()` moves the filter reason into the error column.

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:355-369](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:159-168](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:200-216]()

---

## Response Format Handling

### Response Format Types

OpenAI services support multiple response formats:

| Format Type | String Value | Map Representation | Use Case |
|-------------|-------------|-------------------|----------|
| Text | `"text"` | `Map("type" -> "text")` | Plain text responses |
| JSON Object | `"json_object"` | `Map("type" -> "json_object")` | Freeform JSON |
| JSON Schema | - | `Map("type" -> "json_schema", "json_schema" -> Map(...))` | Structured JSON with schema validation |

### API-Specific Handling

**Chat Completions API** (`OpenAIChatCompletion`):
- Supports `text`, `json_object`, and `json_schema`
- `responseFormat` parameter maps to `response_format` in payload
- Schema structure: `{"type": "json_schema", "json_schema": {"name": "...", "schema": {...}}}`

**Responses API** (`OpenAIResponses`):
- Supports `text`, `json_object`, and `json_schema`
- Wraps format in `text.format` structure: `{"text": {"format": {...}}}`
- Verbosity parameter merges into same `text` object: `{"text": {"format": {...}, "verbosity": "high"}}`

**Validation and Normalization**

`ResponseFormatUtils` (not shown in files but referenced) normalizes input formats:

```scala
def setResponseFormat(value: Map[String, Any]): this.type = {
  val normalized = ResponseFormatUtils.normalize(value)
  // For chat_completions:
  val payload = if (normalized.get("type").exists(_ == "json_schema")) {
    Map("type" -> "json_schema", "json_schema" -> Map(...))
  } else normalized
  setScalarParam(responseFormat, payload)
}
```

**Rejection of Bare "json_schema" String**

Both APIs reject `setResponseFormat("json_schema")` to prevent ambiguity:

```scala
def setResponseFormat(value: String): this.type = {
  if (value.trim.equalsIgnoreCase("json_schema")) {
    throw new IllegalArgumentException(
      "Use a Map for 'json_schema' or pass an inner JSON Schema map.")
  }
  // ... handle "text" or "json_object"
}
```

**Sources:** [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:22-69](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:40-88](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala:398-404](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala:90-121]()

---

## Summary

The AI Services Integration layer provides:

1. **Unified Spark Interface**: All services extend `CognitiveServicesBase` for consistent DataFrame transformation APIs
2. **Flexible Parameter Management**: `ServiceParam[T]` supports both scalar values and per-row column references
3. **Global Defaults**: `OpenAIDefaults` reduces boilerplate for common configurations
4. **Multi-Modal Authentication**: Subscription keys, AAD tokens, custom headers, and platform auto-injection
5. **Platform Adaptation**: Automatic endpoint and token selection for Fabric, Synapse, Databricks
6. **Response Processing**: Strongly-typed schemas with JSON parsing and optional post-processing
7. **High-Level Abstractions**: `OpenAIPrompt` for templating, multimodal input, and structured output parsing
8. **Error Handling**: Error columns and RAI content filtering support

For implementation details on specific services, refer to the child pages listed at the beginning of this document.

---

# Page: OpenAI Integration

# OpenAI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py](cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py)
- [cognitive/src/main/python/synapse/ml/services/openai/__init__.py](cognitive/src/main/python/synapse/ml/services/openai/__init__.py)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala)
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala](cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala)
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py](cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbeddingsSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponsesSuite.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala)
- [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](docs/Explore Algorithms/OpenAI/OpenAI.ipynb)

</details>



This page documents SynapseML's integration with OpenAI services, which enables users to leverage OpenAI models within Apache Spark workflows. The integration supports text completion, chat completion, embeddings generation, and prompt engineering capabilities through a consistent, Spark-friendly API. For information about other AI service integrations, see [Azure Cognitive Services](#6.2) or [LangChain Integration](#6.3).

## Architecture Overview

The OpenAI integration in SynapseML is built on a modular architecture that extends the core HTTP client system to communicate with OpenAI's API endpoints. It provides Spark transformers for various OpenAI capabilities that seamlessly work within Spark ML pipelines.

**OpenAI Integration Architecture**

```mermaid
graph TD
    subgraph "SynapseML OpenAI Integration"
        OpenAIBase["OpenAIServicesBase"]
        OpenAIComp["OpenAICompletion<br/>(Legacy Models)"]
        OpenAIChat["OpenAIChatCompletion<br/>(GPT-4, GPT-3.5)"]
        OpenAIResp["OpenAIResponses<br/>(Reasoning Models)"]
        OpenAIEmbed["OpenAIEmbedding"]
        OpenAIPrompt["OpenAIPrompt<br/>(High-Level API)"]
        AIFoundry["AIFoundryChatCompletion<br/>(AI Foundry Models)"]
        OpenAIDefaults["OpenAIDefaults<br/>(Global Parameters)"]
        
        OpenAIBase --> OpenAIComp
        OpenAIBase --> OpenAIChat
        OpenAIBase --> OpenAIResp
        OpenAIBase --> OpenAIEmbed
        OpenAIChat --> AIFoundry
        OpenAIPrompt --> OpenAIComp
        OpenAIPrompt --> OpenAIChat
        OpenAIPrompt --> OpenAIResp
        OpenAIDefaults -.- OpenAIComp
        OpenAIDefaults -.- OpenAIChat
        OpenAIDefaults -.- OpenAIResp
        OpenAIDefaults -.- OpenAIEmbed
        OpenAIDefaults -.- OpenAIPrompt
        OpenAIDefaults -.- AIFoundry
    end
    
    subgraph "Core Infrastructure"
        CogServBase["CognitiveServicesBase"]
        HTTPClient["HTTP Client System"]
        ParamSystem["ServiceParam + GlobalParams"]
        
        CogServBase --> HTTPClient
        CogServBase --> ParamSystem
        OpenAIBase --> CogServBase
    end
    
    subgraph "Authentication"
        SubKey["Subscription Key"]
        AADToken["AAD Token"]
        CustomAuth["Custom Auth Header"]
        FabricAuth["Fabric Token<br/>(Auto-detected)"]
        
        SubKey --> OpenAIBase
        AADToken --> OpenAIBase
        CustomAuth --> OpenAIBase
        FabricAuth --> OpenAIBase
    end
    
    subgraph "OpenAI API Endpoints"
        TextComp["/completions"]
        ChatComp["/chat/completions"]
        RespAPI["/responses"]
        EmbedAPI["/embeddings"]
        FoundryAPI["/models/chat/completions"]
        
        OpenAIComp --> TextComp
        OpenAIChat --> ChatComp
        OpenAIResp --> RespAPI
        OpenAIEmbed --> EmbedAPI
        AIFoundry --> FoundryAPI
    end
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:412-427]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala:21-71]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:97-171]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:93-210]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala:25-99]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:39-533]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala:48-64]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala:11-153]()

## Class Hierarchy and Parameter System

The OpenAI integration is built on a well-structured class hierarchy with a robust parameter system that enables consistent parameter handling across different services.

**OpenAI Class Hierarchy**

```mermaid
classDiagram
    class CognitiveServicesBase {
        +transform(dataset: Dataset): DataFrame
        #getInternalTransformer(schema: StructType): PipelineModel
        #prepareEntity(r: Row): Option[AbstractHttpEntity]
        #prepareUrlRoot(row: Row): String
    }
    
    class HasOpenAISharedParams {
        +deploymentName: ServiceParam~String~
        +user: ServiceParam~String~
        +getDeploymentName(): String
        +setDeploymentName(v: String)
    }
    
    class HasOpenAITextParams {
        +maxTokens: ServiceParam~Int~
        +temperature: ServiceParam~Double~
        +topP: ServiceParam~Double~
        +stop: ServiceParam~String~
        +n: ServiceParam~Int~
        +logProbs: ServiceParam~Int~
        +presencePenalty: ServiceParam~Double~
        +frequencyPenalty: ServiceParam~Double~
        +seed: ServiceParam~Int~
        +verbosity: ServiceParam~String~
        +reasoningEffort: ServiceParam~String~
    }
    
    class HasOpenAITextParamsExtended {
        +responseFormat: ServiceParam~Map[String, Any]~
        +setResponseFormat(value: Map): this.type
        +setResponseFormat(value: String): this.type
        +getResponseFormatType(): String
    }
    
    class HasOpenAIEmbeddingParams {
        +dimensions: ServiceParam~Int~
        +getDimensions(): Int
        +setDimensions(value: Int): this.type
    }
    
    class HasPromptInputs {
        +prompt: ServiceParam~String~
        +batchPrompt: ServiceParam~Seq[String]~
    }
    
    class HasMessagesInput {
        +messagesCol: Param~String~
        +getMessagesCol(): String
        +setMessagesCol(v: String): this.type
    }
    
    class OpenAIServicesBase {
        +timeout: Double = 360.0
        #assertModelStatus(deploymentName: String): Unit
        #usingDefaultOpenAIEndpoint(): Boolean
    }
    
    class OpenAICompletion {
        +apiVersion: "2024-02-01"
        +prepareUrlRoot: Row =&gt; String
        +responseDataType: CompletionResponse.schema
    }
    
    class OpenAIChatCompletion {
        +apiVersion: "2025-04-01-preview"
        +prepareUrlRoot: Row =&gt; String
        +responseDataType: ChatModelResponse.schema
        +getStringEntity(messages, optionalParams): StringEntity
    }
    
    class OpenAIResponses {
        +apiVersion: "2025-04-01-preview"
        +prepareUrlRoot: Row =&gt; String
        +responseDataType: ResponsesModelResponse.schema
        +getOptionalParams(r: Row): Map[String, Any]
    }
    
    class OpenAIEmbedding {
        +apiVersion: "2025-04-01-preview"
        +text: ServiceParam~String~
        +prepareUrlRoot: Row =&gt; String
        +getInternalOutputParser(): JSONOutputParser
    }
    
    class AIFoundryChatCompletion {
        +model: ServiceParam~String~
        +prepareUrlRoot: Row =&gt; String
        +internalServiceType: "foundry"
    }
    
    class OpenAIPrompt {
        +promptTemplate: Param~String~
        +systemPrompt: Param~String~
        +postProcessing: Param~String~
        +apiType: Param~String~
        +columnTypes: Map~String, String~
        +transform(dataset: Dataset): DataFrame
    }
    
    CognitiveServicesBase <|-- OpenAIServicesBase
    HasOpenAISharedParams <|-- OpenAIServicesBase
    
    OpenAIServicesBase <|-- OpenAICompletion
    HasOpenAITextParams <|-- OpenAICompletion
    HasPromptInputs <|-- OpenAICompletion
    
    OpenAIServicesBase <|-- OpenAIChatCompletion
    HasOpenAITextParams <|-- OpenAIChatCompletion
    HasOpenAITextParamsExtended <|-- OpenAIChatCompletion
    HasMessagesInput <|-- OpenAIChatCompletion
    
    OpenAIServicesBase <|-- OpenAIResponses
    HasOpenAITextParams <|-- OpenAIResponses
    HasMessagesInput <|-- OpenAIResponses
    
    OpenAIServicesBase <|-- OpenAIEmbedding
    HasOpenAIEmbeddingParams <|-- OpenAIEmbedding
    
    OpenAIChatCompletion <|-- AIFoundryChatCompletion
    HasOpenAITextParamsExtended <|-- AIFoundryChatCompletion
    
    OpenAIPrompt ..> OpenAICompletion
    OpenAIPrompt ..> OpenAIChatCompletion
    OpenAIPrompt ..> OpenAIResponses
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:19-427]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:34-615]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala:21-71]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:21-171]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:23-210]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala:25-99]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala:18-64]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:39-533]()

## Core Components

### OpenAIServicesBase

`OpenAIServicesBase` is the foundation class for all OpenAI services in SynapseML. It extends `CognitiveServicesBase` and handles:

- Communication with OpenAI API endpoints
- Authentication with OpenAI services
- Default parameter settings
- Integration with Azure Fabric when running in that environment

```scala
abstract class OpenAIServicesBase(override val uid: String) extends CognitiveServicesBase(uid: String)
  with HasOpenAISharedParams with OpenAIFabricSetting {
  setDefault(timeout -> 360.0)
  // ...
}
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:304-318]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:496-565]()

### Parameter System

The OpenAI integration uses a sophisticated parameter system built on `ServiceParam[T]` that enables:

1. **Type-safe parameters** with compile-time validation
2. **Dynamic parameter binding** - Parameters can reference DataFrame columns or constant values
3. **Global parameter defaults** through `OpenAIDefaults` and `GlobalParams`
4. **API-specific parameter handling** - Different parameters for different model types

**Key Parameter Traits:**

| Trait | Parameters | Description |
|-------|-----------|-------------|
| `HasOpenAISharedParams` | `deploymentName`, `user` | Common parameters for all OpenAI services |
| `HasOpenAITextParams` | `maxTokens`, `temperature`, `topP`, `stop`, `n`, `logProbs`, `presencePenalty`, `frequencyPenalty`, `bestOf`, `echo`, `cacheLevel`, `seed`, `verbosity`, `reasoningEffort` | Parameters for text generation models |
| `HasOpenAITextParamsExtended` | Extends `HasOpenAITextParams` with `responseFormat` | Chat and Responses API with structured outputs |
| `HasOpenAIEmbeddingParams` | `dimensions` | Parameters for embedding models |
| `HasPromptInputs` | `prompt`, `batchPrompt` | Single or batch prompt inputs for legacy models |
| `HasMessagesInput` | `messagesCol` | Chat message arrays for chat/responses models |

**New Parameters in Recent Versions:**

- **`seed`** (Int): Enables deterministic sampling for reproducible results
- **`verbosity`** (String): Controls output verbosity for reasoning models (accepts "low", "medium", "high", or custom strings)
- **`reasoningEffort`** (String): Controls reasoning depth for o1/o3 models (accepts "minimal", "low", "medium", "high", or custom strings)
- **`responseFormat`** (Map[String, Any]): Structured output format including `json_schema` for strict JSON outputs

**ServiceParam Value Binding:**

`ServiceParam[T]` supports dual binding:
```scala
// Bind to a constant value
transformer.setTemperature(0.7)

// Bind to a DataFrame column
transformer.setTemperatureCol("temperature_column")
```

Internally, `ServiceParam[T]` is represented as `Either[T, String]` where `Left(value)` is a constant and `Right(columnName)` is a column reference.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:57-353]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:34-131]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:21-93]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:39-89]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:10-57]()

### Authentication Mechanisms

The integration supports multiple authentication methods:

| Authentication Method | Description | How to Use |
|-----------------|-------------|-----------|
| Subscription Key | Azure OpenAI API key | `setSubscriptionKey(key)` |
| AAD Token | Azure Active Directory token | `setAADToken(token)` |
| Custom Auth Header | Custom authorization header | `setCustomAuthHeader(header)` |
| Fabric Authentication | Automatic in Azure Fabric | Automatic when running in Fabric |

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:132-194]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:10-51]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:54-86]()

## OpenAI Services

### OpenAICompletion

The `OpenAICompletion` class provides integration with OpenAI's legacy text completion API for models like `text-davinci-003`. This class is primarily maintained for backward compatibility with older models.

**Key Features:**
- Single prompt completions via `setPromptCol()` or `setPrompt()`
- Batch prompt completions via `setBatchPromptCol()` or `setBatchPrompt()`
- Default API version: `2024-02-01`
- Endpoint: `/openai/deployments/{deploymentName}/completions`

**Response Schema:**
The transformer returns `CompletionResponse` with fields: `id`, `object`, `created`, `model`, `choices` (containing `text`, `index`, `logprobs`, `finish_reason`).

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletion.scala:21-71]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:112-353]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala:10-27]()

### OpenAIChatCompletion

`OpenAIChatCompletion` integrates with OpenAI's Chat Completions API for models like GPT-4 and GPT-3.5-turbo. This is the primary API for modern OpenAI models.

**Key Features:**
- Chat messages with roles (`system`, `user`, `assistant`) via `setMessagesCol()`
- Response format control including `json_object` and `json_schema`
- Support for new parameters: `seed`, `verbosity`, `reasoningEffort`
- Default API version: `2025-04-01-preview`
- Endpoint: `/openai/deployments/{deploymentName}/chat/completions`

**Message Schema:**
Messages must be an array of `OpenAIMessage(role: String, content: String, name: Option[String])`. For example:
```scala
Seq(
  OpenAIMessage("system", "You are a helpful assistant"),
  OpenAIMessage("user", "What is Apache Spark?")
)
```

**Response Schema:**
Returns `ChatModelResponse` with fields: `id`, `object`, `created`, `model`, `choices` (containing `message`, `finish_reason`), `system_fingerprint`, `usage`.

**Content Filtering:**
The transformer implements `HasRAIContentFilter` trait to detect and handle content filtered by Azure's Responsible AI system. Filtered content is captured in the error column.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:97-171]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:21-93,355-410]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala:38-59]()

### OpenAIResponses

`OpenAIResponses` is a new transformer for the OpenAI Responses API, designed for reasoning models (o1, o3 series) and advanced multimodal scenarios.

**Key Features:**
- Endpoint: `/openai/responses` (deployment-agnostic)
- Supports multimodal inputs with content parts (text, images, files)
- Model-specific parameter handling: GPT-5 models disable sampling parameters (`temperature`, `top_p`, `seed`)
- Nested parameter structure: `text.verbosity`, `text.format`, `reasoning.effort`
- Default API version: `2025-04-01-preview`

**Parameter Transformations:**

The `getOptionalParams()` method performs sophisticated parameter transformations:

1. **Model parameter**: Converts `deploymentName` to `model` parameter
2. **Text verbosity**: Nests `verbosity` under `text.verbosity`
3. **Response format**: Nests `responseFormat` under `text.format`
4. **Reasoning effort**: Converts `reasoningEffort` to `reasoning.effort`
5. **Sampling parameters**: Removes `temperature`, `top_p`, `seed` for GPT-5 models

**Message Content Format:**

Messages must use content parts with type `input_text`, `input_image`, or `input_file`:
```scala
Seq(
  Map("type" -> "input_text", "text" -> "Describe this image"),
  Map("type" -> "input_image", "image_url" -> "data:image/png;base64,...")
)
```

**Response Schema:**
Returns `ResponsesModelResponse` with fields: `id`, `object`, `created_at`, `model`, `output` (array of `OpenAIResponsesChoice` with `content` parts and `status`), `system_fingerprint`, `usage`.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:93-210]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:371-410]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala:60-74]()

### OpenAIEmbedding

`OpenAIEmbedding` provides integration with OpenAI's embeddings API for converting text to dense vectors.

**Key Features:**
- Text input via `setTextCol()` or `setText()`
- Optional `dimensions` parameter for embedding size
- Returns embeddings as Spark `Vector` type for ML pipelines
- Default API version: `2025-04-01-preview`
- Endpoint: `/openai/deployments/{deploymentName}/embeddings`

**Embedding-Specific Deployment:**

The transformer uses a dedicated global parameter `OpenAIEmbeddingDeploymentNameKey` for embedding models. This allows you to set a default embedding deployment separate from text generation deployments:

```scala
OpenAIDefaults.setEmbeddingDeploymentName("text-embedding-ada-002")
```

If no embedding-specific deployment is set, it falls back to the instance `deploymentName` parameter.

**Response Processing:**

The transformer uses a custom output parser that extracts the embedding vector from the API response and converts it to Spark's `VectorType`:
```scala
def responseToVector(r: Row) =
  if (r == null) None
  else Some(Vectors.dense(r.getAs[Seq[Row]]("data").head.getAs[Seq[Double]]("embedding").toArray))
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIEmbedding.scala:25-99]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:55,87-103]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAISchemas.scala:28-36]()

### AIFoundryChatCompletion

`AIFoundryChatCompletion` extends `OpenAIChatCompletion` to support Azure AI Foundry models (formerly Azure AI Studio models).

**Key Differences from OpenAIChatCompletion:**
- Endpoint: `/models/chat/completions` (deployment-agnostic)
- Requires `model` parameter instead of `deploymentName`
- Service name pattern: `{name}.services.ai.azure.com`
- Internal service type: `foundry`

**Usage:**
```scala
new AIFoundryChatCompletion()
  .setCustomServiceName("my-ai-foundry")  // Sets URL to https://my-ai-foundry.services.ai.azure.com/
  .setModel("Llama-3.3-70B-Instruct")
  .setSubscriptionKey(apiKey)
  .setMessagesCol("messages")
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala:48-64]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/aifoundry/AIFoundryChatCompletion.scala:18-44]()

## OpenAIPrompt: High-Level Abstraction

`OpenAIPrompt` provides a higher-level abstraction focused on prompt engineering. It automatically handles differences between completion, chat, and responses models, providing a consistent interface regardless of the underlying API.

### Key Features

1. **Template-based prompting**: Define prompts with variable placeholders using `{columnName}` syntax
2. **Post-processing options**: Parse structured responses (CSV, JSON, regex)
3. **System prompt customization**: Configure system behavior for chat models
4. **Automatic model selection**: Detects and uses appropriate API based on deployment name
5. **Multimodal support**: Handle text and file inputs (images, PDFs) with column type annotations
6. **API type selection**: Choose between `chat_completions` and `responses` APIs
7. **Response format options**: Support `json_object` and `json_schema` for structured outputs

**OpenAIPrompt Processing Flow**

```mermaid
flowchart TD
    A["Input DataFrame"] --> B["OpenAIPrompt.transform()"]
    
    subgraph "Processing Pipeline"
        B --> C["applyPathPlaceholders()<br/>(Replace file columns)"]
        C --> D["Functions.template()<br/>(Interpolate {columnName})"]
        
        D --> E{"Model Type<br/>Detection"}
        
        E -->|"Legacy Model<br/>(davinci, etc.)"| F["OpenAICompletion"]
        E -->|"Chat Model<br/>(gpt-4, etc.)"| G["OpenAIChatCompletion"]
        E -->|"Responses API<br/>(apiType=responses)"| H["OpenAIResponses"]
        E -->|"AI Foundry<br/>(model parameter)"| I["AIFoundryChatCompletion"]
        
        F --> J["getOutputMessageText()<br/>(Extract text)"]
        G --> J
        H --> J
        I --> J
        
        J --> K["OutputParser.parse()"]
        K -->|"csv"| L["DelimiterParser"]
        K -->|"json"| M["JsonParser"]
        K -->|"regex"| N["RegexParser"]
        K -->|""| O["PassThroughParser"]
    end
    
    L --> P["Output DataFrame"]
    M --> P
    N --> P
    O --> P
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:39-533]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:272-327]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:456-505]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:535-573]()

### Template Engine

The template engine uses SynapseML's `Functions.template()` to interpolate column values into prompt strings:

```scala
setPromptTemplate("Translate from English to French: {text}")
```

Variables in curly braces `{columnName}` are replaced with values from the corresponding DataFrame columns.

**File Path Handling:**

For columns containing file paths, use `setColumnType()` to mark them as `"path"`:
```scala
setColumnType("imagePath", "path")
setPromptTemplate("Describe this image: {imagePath}")
```

Path columns are replaced with placeholder text in the template, then the actual file content is loaded and attached as multimodal content parts.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:130-155]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:194-198]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:272-327]()

### Multimodal Support

`OpenAIPrompt` supports multimodal inputs through the `columnTypes` parameter. When you mark a column as type `"path"`, the transformer:

1. Replaces `{columnName}` in the template with an attachment placeholder
2. Loads the file from the path at transformation time
3. Detects the file type (image, text, PDF, audio)
4. Constructs appropriate content parts for the API

**Supported File Types:**

| File Type | Extensions | Content Part Type | Notes |
|-----------|-----------|-------------------|-------|
| Text | `.md`, `.csv`, `.tsv`, `.json`, `.xml` | `input_text` or `text` | Content embedded inline |
| Image | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` | `input_image` or `image_url` | Base64 encoded |
| PDF | `.pdf` | `input_file` | Base64 encoded |
| Audio | `.mp3`, `.wav` | Not supported | Throws exception |

**API-Specific Formatting:**

The `apiType` parameter controls how multimodal content is formatted:

- **`chat_completions`**: Only supports text files (embedded inline)
- **`responses`**: Supports images and PDFs with `input_text`, `input_image`, `input_file` types

**Example:**
```scala
new OpenAIPrompt()
  .setApiType("responses")
  .setColumnType("pdfPath", "path")
  .setPromptTemplate("Summarize this document: {pdfPath}")
  .setDeploymentName("gpt-4o")
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:130-155]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:185-198]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:348-447]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:329-346]()

### Post-Processing

The post-processing system provides structured parsing of LLM responses:

| Post-Processing | Description | Configuration | Output Type |
|-----------------|-------------|---------------|-------------|
| `csv` | Parse delimiter-separated values | `setPostProcessingOptions(Map("delimiter" -> ","))` | `Array[String]` |
| `json` | Parse JSON with schema | `setPostProcessingOptions(Map("jsonSchema" -> "field1 TYPE, ..."))` | `Struct` |
| `regex` | Extract with regex | `setPostProcessingOptions(Map("regex" -> "...", "regexGroup" -> "0"))` | `String` |
| None (default) | Return raw text | Default | `String` |

**Automatic Post-Processing Detection:**

If you call `setPostProcessingOptions()` without explicitly setting `postProcessing`, it's automatically inferred:
- `delimiter` key → `csv`
- `jsonSchema` key → `json`
- `regex` key → `regex`

**JSON Schema Cleaning:**

The `JsonParser` automatically removes code fence markers from LLM responses:
```scala
// Handles responses like:
// ```json
// {"name": "John"}
// ```
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:65-103]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:495-505]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:535-573]()

### Model Selection Logic

The `getOpenAIChatService()` method implements the model selection logic:

```scala
private def getOpenAIChatService: OpenAIServicesBase with HasTextOutput = {
  val completion: OpenAIServicesBase with HasTextOutput =
    if (hasAIFoundryModel) {
      new AIFoundryChatCompletion()
    }
    else if (legacyModels.contains(getDeploymentName)) {
      new OpenAICompletion()
    }
    else {
      getApiType match {
        case "responses" => new OpenAIResponses()
        case "chat_completions" | _ => new OpenAIChatCompletion()
      }
    }
  // ...
}
```

**Selection Rules:**
1. If `model` parameter is set → `AIFoundryChatCompletion`
2. If `deploymentName` in legacy model list → `OpenAICompletion`
3. If `apiType` is `"responses"` → `OpenAIResponses`
4. Otherwise → `OpenAIChatCompletion` (default)

Legacy models: `ada`, `babbage`, `curie`, `davinci`, `text-ada-001`, `text-babbage-001`, `text-curie-001`, `text-davinci-002`, `text-davinci-003`, `code-cushman-001`, `code-davinci-002`.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:449-479]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:452-454]()

## Global Parameter Configuration with OpenAIDefaults

`OpenAIDefaults` provides a mechanism for setting global default values for commonly used parameters across multiple OpenAI service instances. This is especially useful in notebooks or applications where multiple OpenAI calls are made with the same configuration.

### Configurable Parameters

| Parameter | Type | Description | Method |
|-----------|------|-------------|--------|
| Deployment Name | String | OpenAI model deployment name | `OpenAIDefaults.setDeploymentName(name)` |
| Embedding Deployment Name | String | Separate deployment for embeddings | `OpenAIDefaults.setEmbeddingDeploymentName(name)` |
| Subscription Key | String | OpenAI API key | `OpenAIDefaults.setSubscriptionKey(key)` |
| Temperature | Double | Controls randomness (0.0-2.0) | `OpenAIDefaults.setTemperature(value)` |
| Top P | Double | Nucleus sampling (0.0-1.0) | `OpenAIDefaults.setTopP(value)` |
| Seed | Int | Deterministic sampling seed | `OpenAIDefaults.setSeed(value)` |
| Verbosity | String | Output verbosity hint | `OpenAIDefaults.setVerbosity(value)` |
| Reasoning Effort | String | Reasoning depth hint | `OpenAIDefaults.setReasoningEffort(value)` |
| URL | String | Base URL for OpenAI API | `OpenAIDefaults.setURL(url)` |
| API Version | String | API version string | `OpenAIDefaults.setApiVersion(version)` |
| Model | String | AI Foundry model name | `OpenAIDefaults.setModel(name)` |

**Parameter Validation:**

The `setTemperature()` and `setTopP()` methods validate ranges:
```scala
def setTemperature(v: Double): Unit = {
  require(v >= 0.0 && v <= 2.0, s"Temperature must be between 0.0 and 2.0, got: $v")
  GlobalParams.setGlobalParam(OpenAITemperatureKey, Left(v))
}

def setTopP(v: Double): Unit = {
  require(v >= 0.0 && v <= 1.0, s"TopP must be between 0.0 and 1.0, got: $v")
  GlobalParams.setGlobalParam(OpenAITopPKey, Left(v))
}
```

### Usage

In Scala:
```scala
// Set global defaults
OpenAIDefaults.setDeploymentName("gpt-4")
OpenAIDefaults.setEmbeddingDeploymentName("text-embedding-ada-002")
OpenAIDefaults.setSubscriptionKey("your-key")
OpenAIDefaults.setTemperature(0.0)  // Deterministic
OpenAIDefaults.setSeed(42)
OpenAIDefaults.setURL("https://your-endpoint.openai.azure.com/")

// Create transformer (will use global defaults)
val prompt = new OpenAIPrompt()
  .setPromptTemplate("Summarize this: {text}")
  .setOutputCol("summary")

// Get current values
val currentTemp = OpenAIDefaults.getTemperature  // Option[Double]

// Reset to no default
OpenAIDefaults.resetTemperature()
```

In Python:
```python
# Set global defaults
defaults = OpenAIDefaults()
defaults.set_deployment_name("gpt-4")
defaults.set_embedding_deployment_name("text-embedding-ada-002")
defaults.set_subscription_key("your-key")
defaults.set_temperature(0.0)  # Deterministic
defaults.set_seed(42)
defaults.set_URL("https://your-endpoint.openai.azure.com/")

# Create transformer (will use global defaults)
prompt = OpenAIPrompt() \
  .setPromptTemplate("Summarize this: {text}") \
  .setOutputCol("summary")

# Get current values
current_temp = defaults.get_temperature()  # Returns value or None

# Reset to no default
defaults.reset_temperature()
```

### Global Parameter Mechanism

`OpenAIDefaults` is a wrapper around the core `GlobalParams` system:

```scala
object OpenAIDefaults {
  def setDeploymentName(v: String): Unit = {
    GlobalParams.setGlobalParam(OpenAIDeploymentNameKey, Left(v))
  }
  
  def getDeploymentName: Option[String] = {
    extractLeft(GlobalParams.getGlobalParam(OpenAIDeploymentNameKey))
  }
  // ...
}
```

Each parameter is registered with a `GlobalKey` instance:
- `OpenAIDeploymentNameKey`
- `OpenAIEmbeddingDeploymentNameKey`
- `OpenAITemperatureKey`
- `OpenAISeedKey`
- `OpenAITopPKey`
- `OpenAIVerbosityKey`
- `OpenAIReasoningEffortKey`
- `OpenAISubscriptionKey`
- `OpenAIApiVersion`
- `URLKey`
- `AIFoundryModel`

When a transformer's `transform()` method is called, it invokes `transferGlobalParamsToParamMap()` which automatically fills in unset parameters with global defaults.

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaults.scala:11-153]()
- [cognitive/src/main/python/synapse/ml/services/openai/OpenAIDefaults.py:19-131]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:54-110]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/param/GlobalParams.scala:10-57]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIDefaultsSuite.scala:35-182]()
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py:20-170]()

## Request Flow and Fabric Integration

The OpenAI integration follows a detailed processing flow for requests and has special integration with Azure Fabric environments.

```mermaid
sequenceDiagram
    participant App as Application
    participant Transformer as OpenAI Transformer
    participant HTTP as HTTP Client
    participant Fabric as Fabric Integration
    participant OpenAI as OpenAI API
    
    App->>Transformer: transform(DataFrame)
    Note over Transformer: transferGlobalParamsToParamMap()
    
    Transformer->>Transformer: Check if running in Fabric
    
    alt Running in Fabric
        Transformer->>Fabric: Get AAD token
        Fabric-->>Transformer: Return token
    end
    
    Transformer->>HTTP: Prepare HTTP request
    
    alt Authentication method
        alt Subscription Key
            Transformer->>HTTP: Add Ocp-Apim-Subscription-Key header
        else AAD Token
            Transformer->>HTTP: Add Authorization: Bearer header
        else Custom Auth
            Transformer->>HTTP: Add custom Authorization header
        end
    end
    
    HTTP->>OpenAI: Send request to OpenAI API
    OpenAI-->>HTTP: Return response
    
    HTTP->>Transformer: Process response
    Transformer->>App: Return transformed DataFrame
```

### Fabric Integration

When running in Azure Fabric environments, the OpenAI integration automatically:

1. Detects the Fabric runtime environment
2. Uses appropriate authentication tokens
3. Sets default endpoints based on the Fabric configuration
4. Manages workspace and capacity IDs for proper routing

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAI.scala:304-318]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:309-564]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:14-151]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:10-51]()

## Common Usage Examples

### Text Completion (Legacy Models)

```scala
// Using legacy completion models
val completion = new OpenAICompletion()
  .setDeploymentName("text-davinci-003")
  .setCustomServiceName("your-openai-service")
  .setSubscriptionKey("your-api-key")
  .setPromptCol("prompt")
  .setMaxTokens(200)
  .setTemperature(0.7)
  .setOutputCol("completion")

// Transform DataFrame with prompts column
val result = completion.transform(df)
```

### Chat Completion

```scala
// Import for OpenAIMessage
import com.microsoft.azure.synapse.ml.services.openai.OpenAIMessage

// Create DataFrame with messages
val messagesDF = Seq(
  Seq(
    OpenAIMessage("system", "You are a helpful assistant"),
    OpenAIMessage("user", "What is Apache Spark?")
  )
).toDF("messages")

// Create chat completion transformer
val chatCompletion = new OpenAIChatCompletion()
  .setDeploymentName("gpt-4")
  .setCustomServiceName("your-openai-service")
  .setSubscriptionKey("your-api-key")
  .setMessagesCol("messages")
  .setMaxTokens(1000)
  .setTemperature(0)
  .setOutputCol("response")

// Transform DataFrame
val result = chatCompletion.transform(messagesDF)
```

### Embeddings

```scala
// Create DataFrame with text
val textDF = Seq("Apache Spark is a data processing framework").toDF("text")

// Create embedding transformer
val embedding = new OpenAIEmbedding()
  .setDeploymentName("text-embedding-ada-002")
  .setCustomServiceName("your-openai-service")
  .setSubscriptionKey("your-api-key")
  .setTextCol("text")
  .setOutputCol("embedding")

// Transform DataFrame
val result = embedding.transform(textDF)
```

### Prompt Engineering

```scala
// Create DataFrame with input data
val df = Seq(
  ("apple", "fruits"),
  ("mercedes", "cars"),
  ("cake", "dishes")
).toDF("text", "category")

// Create prompt transformer
val prompt = new OpenAIPrompt()
  .setDeploymentName("gpt-35-turbo")
  .setCustomServiceName("your-openai-service")
  .setSubscriptionKey("your-api-key")
  .setPromptTemplate("Generate a list of 5 {category} similar to {text}, comma separated:")
  .setPostProcessing("csv")
  .setOutputCol("result")

// Transform DataFrame
val result = prompt.transform(df)
```

Sources:
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAICompletionSuite.scala:34-91]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala:17-245]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPromptSuite.scala:24-159]()

## Advanced Features

### Response Format Options

Modern OpenAI models support structured output formats through the `responseFormat` parameter.

**Supported Formats:**

| Format | Description | Usage |
|--------|-------------|-------|
| `text` | Plain text (default) | `setResponseFormat("text")` |
| `json_object` | Unstructured JSON object | `setResponseFormat("json_object")` |
| `json_schema` | Strict JSON with schema validation | `setResponseFormat(schemaMap)` |

**JSON Object Format:**

For GPT-4 and compatible models:
```scala
val chatCompletion = new OpenAIChatCompletion()
  .setDeploymentName("gpt-4")
  .setResponseFormat("json_object")  // Forces JSON output
```

**JSON Schema Format:**

For strict schema validation with GPT-4 and newer:
```scala
val schemaMap: Map[String, Any] = Map(
  "type" -> "json_schema",
  "json_schema" -> Map(
    "name" -> "answer_schema",
    "strict" -> true,
    "schema" -> Map(
      "type" -> "object",
      "properties" -> Map(
        "answer" -> Map("type" -> "string"),
        "confidence" -> Map("type" -> "number")
      ),
      "required" -> Seq("answer"),
      "additionalProperties" -> false
    )
  )
)

val chatCompletion = new OpenAIChatCompletion()
  .setDeploymentName("gpt-4")
  .setResponseFormat(schemaMap)
```

**Response Format Normalization:**

The `ResponseFormatUtils.normalize()` helper handles various input formats:
- Bare string: `"json_object"` → `Map("type" -> "json_object")`
- Flattened schema: `Map("type" -> "json_schema", "name" -> "...", "schema" -> ...)` → Nested structure
- Nested schema: Preserved as-is

**API-Specific Formatting:**

- **Chat Completions**: Uses `response_format` parameter with nested `json_schema` structure
- **Responses API**: Uses `text.format` parameter with flattened structure

**OpenAIPrompt Integration:**

`OpenAIPrompt` supports both `responseFormat` for API-level control and `postProcessing` for client-side parsing:

```scala
// API-level JSON enforcement + client-side parsing
val prompt = new OpenAIPrompt()
  .setPromptTemplate("Convert this to JSON: {text}")
  .setResponseFormat("json_object")  // API enforces JSON
  .setPostProcessing("json")  // Parse and validate
  .setPostProcessingOptions(Map("jsonSchema" -> "name STRING, age INT, city STRING"))
```

**Rejection of Bare "json_schema" String:**

Both `OpenAIChatCompletion` and `OpenAIPrompt` reject the bare string `"json_schema"` to prevent errors:
```scala
// This throws IllegalArgumentException:
transformer.setResponseFormat("json_schema")

// Use a Map instead:
transformer.setResponseFormat(Map("type" -> "json_schema", ...))
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletion.scala:21-93]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIResponses.scala:39-72]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:65-103]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala:153-194,348-404]()
- [cognitive/src/test/python/synapsemltest/services/openai/test_OpenAIDefaults.py:172-234]()

### Error Handling

The OpenAI integration provides robust error handling:

1. **Error Column**: All transformers include an error column that captures API errors
2. **RAI Filtering**: Automatically handles content filtered by Responsible AI systems
3. **Null Handling**: Properly handles null inputs and outputs

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIPrompt.scala:129-146]()
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/SimpleHTTPTransformer.scala:23-70]()
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/openai/OpenAIChatCompletionSuite.scala:142-152]()

### Authentication Options

The integration supports multiple authentication methods:

```scala
// Using subscription key (Azure OpenAI)
transformer.setSubscriptionKey("your-key")

// Using AAD token
transformer.setAADToken("your-token")

// Using custom authentication header
transformer.setCustomAuthHeader("your-auth-header")

// Set a custom service name (Azure OpenAI)
transformer.setCustomServiceName("your-openai-service")

// Set a custom URL root for direct API access
transformer.setCustomUrlRoot("https://api.openai.com/v1/")
```

Sources:
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:134-194]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:215-232]()
- [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServiceBase.scala:282-347]()

---

# Page: Azure Cognitive Services

# Azure Cognitive Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tools/gateway/setup-gateway.sh](tools/gateway/setup-gateway.sh)

</details>



This page documents SynapseML's integration with Azure Cognitive Services, a collection of pre-trained AI models provided as REST APIs. These integrations enable distributed processing of images, text, speech, and time-series data using Spark DataFrames.

**Note**: Azure Cognitive Services represents the legacy generation of Microsoft's AI services. For newer AI capabilities, including large language models and advanced embeddings, see the [OpenAI Integration](#6.1) page. For LangChain integration, see [LangChain Integration](#6.3).

## Overview

The Azure Cognitive Services integration in SynapseML provides Spark `Transformer` implementations that wrap Azure's REST APIs. Each service is accessible through a Spark-native interface that handles:
- Authentication via subscription keys or Azure AD tokens
- Distributed HTTP request batching and retry logic
- Serialization and deserialization of API payloads
- Error handling and logging

All cognitive services transformers extend from [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala]() and use the HTTP client infrastructure documented in section 5.2.

## Architecture Overview

Azure Cognitive Services integration in SynapseML follows a consistent pattern where each service is wrapped as a Spark transformer that handles authentication, request formation, serialization/deserialization, and error handling.

### Class Hierarchy and Architecture

The following diagram shows the core class hierarchy for Azure Cognitive Services integration:

```mermaid
graph TB
    subgraph "Core Infrastructure"
        CognitiveServicesBase["CognitiveServicesBase<br/>(abstract base)"]
        HasServiceParams["HasServiceParams"]
        HasCognitiveServiceInput["HasCognitiveServiceInput"]
        HasInternalJsonOutputParser["HasInternalJsonOutputParser"]
    end
    
    subgraph "Service-Specific Base Classes"
        TextAnalyticsBase["TextAnalyticsBase"]
        SpeechSDKBase["SpeechSDKBase"]
        AnomalyDetectorBase["AnomalyDetectorBase"]
        VisionBase["VisionBase"]
        SearchBase["SearchBase"]
    end
    
    subgraph "Concrete Service Implementations"
        LanguageDetector["LanguageDetector"]
        TextSentiment["TextSentiment"]
        EntityDetector["EntityDetector"]
        KeyPhraseExtractor["KeyPhraseExtractor"]
        NER["NER"]
        PII["PII"]
        AnalyzeHealthText["AnalyzeHealthText"]
        
        SpeechToTextSDK["SpeechToTextSDK"]
        TextToSpeech["TextToSpeech"]
        ConversationTranscription["ConversationTranscription"]
        
        DetectLastAnomaly["DetectLastAnomaly"]
        DetectAnomalies["DetectAnomalies"]
        SimpleDetectAnomalies["SimpleDetectAnomalies"]
        
        AnalyzeImage["AnalyzeImage"]
        RecognizeText["RecognizeText"]
        DescribeImage["DescribeImage"]
        
        AddDocuments["AddDocuments"]
        AzureSearchWriter["AzureSearchWriter"]
    end
    
    CognitiveServicesBase --> TextAnalyticsBase
    CognitiveServicesBase --> SpeechSDKBase
    CognitiveServicesBase --> AnomalyDetectorBase
    CognitiveServicesBase --> VisionBase
    CognitiveServicesBase --> SearchBase
    
    HasServiceParams --> CognitiveServicesBase
    HasCognitiveServiceInput --> CognitiveServicesBase
    HasInternalJsonOutputParser --> CognitiveServicesBase
    
    TextAnalyticsBase --> LanguageDetector
    TextAnalyticsBase --> TextSentiment
    TextAnalyticsBase --> EntityDetector
    TextAnalyticsBase --> KeyPhraseExtractor
    TextAnalyticsBase --> NER
    TextAnalyticsBase --> PII
    TextAnalyticsBase --> AnalyzeHealthText
    
    SpeechSDKBase --> SpeechToTextSDK
    SpeechSDKBase --> TextToSpeech
    SpeechSDKBase --> ConversationTranscription
    
    AnomalyDetectorBase --> DetectLastAnomaly
    AnomalyDetectorBase --> DetectAnomalies
    AnomalyDetectorBase --> SimpleDetectAnomalies
    
    VisionBase --> AnalyzeImage
    VisionBase --> RecognizeText
    VisionBase --> DescribeImage
    
    SearchBase --> AddDocuments
    SearchBase --> AzureSearchWriter
```

**Key Classes**:
- `CognitiveServicesBase`: Abstract base providing HTTP client integration, authentication, and retry logic
- `HasServiceParams`: Trait for subscription key, AAD token, and location parameters
- `TextAnalyticsBase`: Base for all text analytics services
- `SpeechSDKBase`: Base for speech services using Azure Speech SDK
- `AnomalyDetectorBase`: Base for anomaly detection services
- `VisionBase`: Base for computer vision services
- `SearchBase`: Base for Azure AI Search integration

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalytics.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDK.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnomalyDetector.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/vision/AnalyzeImage.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/search/AzureSearch.scala]()

### Authentication and Configuration

The following diagram shows how authentication and service configuration flow through the system:

```mermaid
graph LR
    subgraph "Authentication Sources"
        SubKey["Subscription Key"]
        AADToken["Azure AD Token"]
        KeyVault["Azure Key Vault"]
    end
    
    subgraph "Configuration Methods"
        setSubscriptionKey["setSubscriptionKey()"]
        setAADToken["setAADToken()"]
        setSubscriptionKeyCol["setSubscriptionKeyCol()"]
        setLocation["setLocation()"]
        setCustomServiceName["setCustomServiceName()"]
        setUrl["setUrl()"]
    end
    
    subgraph "Service Configuration"
        HasServiceParams["HasServiceParams trait"]
        HasSetLocation["HasSetLocation trait"]
        HasSubscriptionKey["HasSubscriptionKey trait"]
        HasAADToken["HasAADToken trait"]
    end
    
    subgraph "HTTP Execution"
        HTTPTransformer["HTTPTransformer"]
        RequestHandling["Request Handling<br/>(retry + batching)"]
        AzureAPI["Azure Cognitive<br/>Services API"]
    end
    
    SubKey --> setSubscriptionKey
    AADToken --> setAADToken
    KeyVault --> setSubscriptionKeyCol
    
    setSubscriptionKey --> HasSubscriptionKey
    setAADToken --> HasAADToken
    setLocation --> HasSetLocation
    setCustomServiceName --> HasServiceParams
    setUrl --> HasServiceParams
    setSubscriptionKeyCol --> HasSubscriptionKey
    
    HasSubscriptionKey --> HTTPTransformer
    HasAADToken --> HTTPTransformer
    HasServiceParams --> HTTPTransformer
    HasSetLocation --> HTTPTransformer
    
    HTTPTransformer --> RequestHandling
    RequestHandling --> AzureAPI
```

**Authentication Methods**:

1. **Subscription Key**: Set via `setSubscriptionKey(key)` or `setSubscriptionKeyCol(colName)` for per-row keys
2. **Azure AD Token**: Set via `setAADToken(token)` for AAD-based authentication
3. **Key Vault Integration**: Use column-based keys retrieved from Azure Key Vault (see section 5.4)

**Configuration Parameters**:

| Parameter | Method | Description |
|-----------|--------|-------------|
| Subscription Key | `setSubscriptionKey()` | API subscription key |
| AAD Token | `setAADToken()` | Azure AD authentication token |
| Location | `setLocation()` | Azure region (e.g., "eastus") |
| Custom Service Name | `setCustomServiceName()` | Custom domain name for private endpoints |
| URL | `setUrl()` | Full custom endpoint URL |

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnamolyDetectionSuite.scala:90-105](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:48-51]()

## Supported Services

SynapseML provides `Transformer` implementations for the following Azure Cognitive Services:

| Service Category | Transformer Classes | Key Methods | Description |
|------------------|---------------------|-------------|-------------|
| **Text Analytics** | `LanguageDetector`<br/>`EntityDetector`<br/>`TextSentiment`<br/>`KeyPhraseExtractor`<br/>`NER`<br/>`PII`<br/>`AnalyzeHealthText` | `setTextCol()`<br/>`setLanguageCol()`<br/>`setOutputCol()` | Language detection, entity extraction, sentiment analysis, key phrase extraction, named entity recognition, PII detection and redaction, healthcare text analysis |
| **Computer Vision** | `AnalyzeImage`<br/>`RecognizeText`<br/>`DescribeImage`<br/>`GenerateThumbnails`<br/>`RecognizeDomainSpecificContent` | `setImageUrlCol()`<br/>`setImageBytesCol()`<br/>`setOutputCol()` | Image analysis, OCR, image description, thumbnail generation, celebrity/landmark recognition |
| **Speech Services** | `SpeechToTextSDK`<br/>`TextToSpeech`<br/>`ConversationTranscription`<br/>`SpeakerEmotionInference` | `setAudioDataCol()`<br/>`setOutputFileCol()`<br/>`setLanguage()` | Speech-to-text transcription, text-to-speech synthesis, multi-speaker conversation transcription, emotion inference |
| **Anomaly Detection** | `DetectLastAnomaly`<br/>`DetectAnomalies`<br/>`SimpleDetectAnomalies` | `setGranularity()`<br/>`setSensitivity()`<br/>`setOutputCol()` | Time series anomaly detection for single points, entire series, or grouped data |
| **Azure AI Search** | `AddDocuments`<br/>`AzureSearchWriter`<br/>`SearchIndex` | `write()`<br/>`setIndexName()`<br/>`setKeyCol()` | Document indexing, vector search, schema inference, index management |

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalytics.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/vision/AnalyzeImage.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDK.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnomalyDetector.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/search/AzureSearch.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:1-371](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:1-487](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnamolyDetectionSuite.scala:1-251]()

### Text Analytics

The `TextAnalyticsBase` class provides the foundation for all text analytics services. Each concrete implementation extends this base and provides specific NLP capabilities.

#### Text Analytics Pipeline

```mermaid
graph LR
    DataFrame["Input DataFrame<br/>(text column)"]
    LanguageDetector["LanguageDetector"]
    TextSentiment["TextSentiment"]
    KeyPhraseExtractor["KeyPhraseExtractor"]
    NER["NER"]
    PII["PII"]
    Output["Output DataFrame<br/>(with analysis results)"]
    
    DataFrame --> LanguageDetector
    LanguageDetector --> TextSentiment
    TextSentiment --> KeyPhraseExtractor
    KeyPhraseExtractor --> NER
    NER --> PII
    PII --> Output
```

**Available Transformers**:

| Class | Purpose | Key Output Fields |
|-------|---------|-------------------|
| `LanguageDetector` | Detects input text language | `language`, `score` |
| `TextSentiment` | Analyzes sentiment | `sentiment`, `positive`, `neutral`, `negative` |
| `EntityDetector` | Extracts general entities | `entities` (array of entity objects) |
| `KeyPhraseExtractor` | Extracts key phrases | `keyPhrases` (array of strings) |
| `NER` | Named entity recognition | `entities` with categories (Person, Location, etc.) |
| `PII` | Detects PII and redacts | `redactedText`, `entities` |
| `AnalyzeHealthText` | Healthcare entity extraction | `entities`, `relations` |

**Configuration Example**:

The following shows a typical configuration for `TextSentiment`:

```scala
import com.microsoft.azure.synapse.ml.services.text.TextSentiment

val sentiment = new TextSentiment()
  .setSubscriptionKey(cognitiveKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setLanguageCol("language")
  .setOutputCol("sentiment")
  .setErrorCol("error")

val results = sentiment.transform(inputDF)
```

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalytics.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:1-371](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:122-128]()

### Computer Vision

The `VisionBase` class provides image analysis capabilities through Azure Computer Vision API.

#### Computer Vision Services Flow

```mermaid
graph TB
    subgraph "Input Sources"
        ImageURL["Image URL"]
        ImageBytes["Image Bytes"]
        BinaryFileDF["BinaryFileDataFrame"]
    end
    
    subgraph "Vision Transformers"
        AnalyzeImage["AnalyzeImage"]
        RecognizeText["RecognizeText<br/>(OCR)"]
        DescribeImage["DescribeImage"]
        GenerateThumbnails["GenerateThumbnails"]
        RecognizeDomainSpecificContent["RecognizeDomainSpecificContent<br/>(celebrities/landmarks)"]
    end
    
    subgraph "Output Results"
        ImageAnalysis["tags, objects,<br/>categories, brands"]
        TextExtraction["recognized text,<br/>bounding boxes"]
        Descriptions["captions, descriptions"]
        Thumbnails["thumbnail images"]
        DomainResults["celebrity/landmark<br/>identification"]
    end
    
    ImageURL --> AnalyzeImage
    ImageURL --> RecognizeText
    ImageURL --> DescribeImage
    ImageURL --> GenerateThumbnails
    ImageURL --> RecognizeDomainSpecificContent
    
    ImageBytes --> AnalyzeImage
    ImageBytes --> RecognizeText
    ImageBytes --> DescribeImage
    
    BinaryFileDF --> AnalyzeImage
    
    AnalyzeImage --> ImageAnalysis
    RecognizeText --> TextExtraction
    DescribeImage --> Descriptions
    GenerateThumbnails --> Thumbnails
    RecognizeDomainSpecificContent --> DomainResults
```

**Configuration Example**:

```scala
import com.microsoft.azure.synapse.ml.services.vision.AnalyzeImage

val vision = new AnalyzeImage()
  .setSubscriptionKey(visionKey)
  .setLocation("eastus")
  .setImageUrlCol("url")
  .setOutputCol("analysis")
  .setVisualFeatures(Array(
    "Categories", "Tags", "Description", 
    "Objects", "Brands", "Color", "Adult"
  ))

val imageAnalysis = vision.transform(imageDF)
```

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/vision/AnalyzeImage.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/vision/VisionBase.scala]()

### Speech Services

The `SpeechSDKBase` class integrates with Azure Speech SDK for audio processing.

#### Speech Services Architecture

```mermaid
graph TB
    subgraph "Audio Input Formats"
        AudioBinary["Binary Audio Data"]
        AudioURL["Audio File URL"]
        StreamingURL["Streaming Media URL<br/>(m3u8, HLS)"]
    end
    
    subgraph "Speech Transformers"
        SpeechToTextSDK["SpeechToTextSDK"]
        TextToSpeech["TextToSpeech"]
        ConversationTranscription["ConversationTranscription"]
        SpeakerEmotionInference["SpeakerEmotionInference"]
    end
    
    subgraph "Configuration"
        setAudioDataCol["setAudioDataCol()"]
        setLanguage["setLanguage()"]
        setFormat["setFormat()"]
        setProfanity["setProfanity()"]
        setOutputFileCol["setOutputFileCol()"]
        setExtraFfmpegArgs["setExtraFfmpegArgs()"]
    end
    
    subgraph "Output"
        TranscriptionText["Transcription Text"]
        AudioFile["Audio File Path"]
        SpeakerDiarization["Speaker Diarization"]
        EmotionalSSML["SSML with Emotions"]
    end
    
    AudioBinary --> setAudioDataCol
    AudioURL --> setAudioDataCol
    StreamingURL --> setAudioDataCol
    
    setAudioDataCol --> SpeechToTextSDK
    setAudioDataCol --> ConversationTranscription
    setLanguage --> SpeechToTextSDK
    setFormat --> SpeechToTextSDK
    setProfanity --> SpeechToTextSDK
    setExtraFfmpegArgs --> SpeechToTextSDK
    
    SpeechToTextSDK --> TranscriptionText
    TextToSpeech --> AudioFile
    ConversationTranscription --> SpeakerDiarization
    SpeakerEmotionInference --> EmotionalSSML
```

**Key Features**:
- `SpeechToTextSDK`: Transcribes audio with custom models via `setEndpointId()`
- `TextToSpeech`: Synthesizes speech with voice selection via `setVoiceName()`
- `ConversationTranscription`: Multi-speaker diarization with speaker IDs
- `SpeakerEmotionInference`: Generates emotion-tagged SSML from text

**Streaming Media Support**:

For streaming URLs (HLS, m3u8), use `setExtraFfmpegArgs()` to control ffmpeg behavior:

```scala
val speechToText = new SpeechToTextSDK()
  .setSubscriptionKey(speechKey)
  .setLocation("eastus")
  .setAudioDataCol("audioUrl")
  .setExtraFfmpegArgs(Array("-t", "60"))  // Process first 60 seconds
  .setOutputCol("transcription")
```

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDK.scala](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechSDKBase.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:225-232](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:250-261](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/TextToSpeechSuite.scala:1-72]()


### Anomaly Detection

The `AnomalyDetectorBase` class provides time series anomaly detection using Azure's Anomaly Detector service.

#### Anomaly Detection Workflow

```mermaid
graph TB
    subgraph "Input Data Structure"
        TimeSeriesDF["Time Series DataFrame"]
        TimestampCol["timestamp column"]
        ValueCol["value column"]
        GroupCol["group column (optional)"]
    end
    
    subgraph "Anomaly Transformers"
        DetectLastAnomaly["DetectLastAnomaly"]
        DetectAnomalies["DetectAnomalies"]
        SimpleDetectAnomalies["SimpleDetectAnomalies"]
    end
    
    subgraph "Configuration Parameters"
        setGranularity["setGranularity()<br/>(hourly, daily, etc.)"]
        setSensitivity["setSensitivity()<br/>(0-99)"]
        setCustomInterval["setCustomInterval()"]
        setTimestampCol["setTimestampCol()"]
        setValueCol["setValueCol()"]
        setGroupCol["setGroupCol()"]
    end
    
    subgraph "Output Fields"
        IsAnomaly["isAnomaly (boolean)"]
        ExpectedValue["expectedValue"]
        UpperMargin["upperMargin"]
        LowerMargin["lowerMargin"]
        IsPositiveAnomaly["isPositiveAnomaly"]
        IsNegativeAnomaly["isNegativeAnomaly"]
    end
    
    TimeSeriesDF --> DetectLastAnomaly
    TimeSeriesDF --> DetectAnomalies
    TimeSeriesDF --> SimpleDetectAnomalies
    
    setGranularity --> DetectAnomalies
    setSensitivity --> DetectAnomalies
    setTimestampCol --> DetectAnomalies
    setValueCol --> DetectAnomalies
    setGroupCol --> SimpleDetectAnomalies
    
    DetectLastAnomaly --> IsAnomaly
    DetectAnomalies --> IsAnomaly
    DetectAnomalies --> ExpectedValue
    DetectAnomalies --> UpperMargin
    DetectAnomalies --> IsPositiveAnomaly
    SimpleDetectAnomalies --> IsAnomaly
```

**Configuration Example**:

```scala
import com.microsoft.azure.synapse.ml.services.anomaly.DetectAnomalies

val anomalyDetector = new DetectAnomalies()
  .setSubscriptionKey(anomalyKey)
  .setLocation("westus2")
  .setTimestampCol("timestamp")
  .setValueCol("value")
  .setGranularity("hourly")
  .setSensitivity(95)
  .setOutputCol("anomalies")

val results = anomalyDetector.transform(timeSeriesDF)
```

**Use Cases**:
- `DetectLastAnomaly`: Real-time monitoring of the most recent data point
- `DetectAnomalies`: Batch analysis of historical time series
- `SimpleDetectAnomalies`: Group-wise anomaly detection for multiple time series

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnomalyDetector.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnamolyDetectionSuite.scala:1-251](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnamolyDetectionSuite.scala:90-105]()

### Azure AI Search

The `SearchBase` class and `AzureSearchWriter` enable integration with Azure AI Search (formerly Azure Cognitive Search) for document indexing and vector search.

#### Azure Search Integration Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        DataFrame["Spark DataFrame"]
        Documents["Document Collections"]
        Vectors["Vector Embeddings"]
    end
    
    subgraph "Search Components"
        AddDocuments["AddDocuments<br/>(Transformer)"]
        AzureSearchWriter["AzureSearchWriter<br/>(DataFrameWriter)"]
        SearchIndex["SearchIndex<br/>(Index Management)"]
    end
    
    subgraph "Index Operations"
        CreateIndex["Create Index"]
        UpdateDocuments["Update Documents"]
        DeleteDocuments["Delete Documents"]
        UploadDocuments["Upload Documents"]
    end
    
    subgraph "Azure AI Search Service"
        SearchService["Azure AI Search"]
        VectorIndex["Vector Index"]
        FullTextIndex["Full-Text Index"]
    end
    
    DataFrame --> AddDocuments
    DataFrame --> AzureSearchWriter
    Documents --> AzureSearchWriter
    Vectors --> AzureSearchWriter
    
    AzureSearchWriter --> CreateIndex
    AddDocuments --> UpdateDocuments
    AddDocuments --> UploadDocuments
    
    CreateIndex --> SearchService
    UpdateDocuments --> SearchService
    UploadDocuments --> SearchService
    
    SearchService --> VectorIndex
    SearchService --> FullTextIndex
    
    SearchIndex --> CreateIndex
```

**Key Components**:

| Component | Purpose | Usage |
|-----------|---------|-------|
| `AddDocuments` | Transformer for adding/updating documents | `new AddDocuments().setActionCol("indexAction")` |
| `AzureSearchWriter` | DataFrame writer for batch indexing | `df.write.format("com.microsoft.azure.synapse.ml.services.search").mode("append")` |
| `SearchIndex` | Index schema management | `new SearchIndex().createIfNoneExists(serviceName, indexName, schema)` |

**Vector Search Configuration**:

```scala
import com.microsoft.azure.synapse.ml.services.search.AzureSearchWriter

val vectorCols = """[
  {"name": "contentVector", "dimension": 1536},
  {"name": "titleVector", "dimension": 1536}
]"""

AzureSearchWriter.write(
  df,
  Map(
    "subscriptionKey" -> searchKey,
    "serviceName" -> serviceName,
    "indexName" -> indexName,
    "keyCol" -> "id",
    "vectorCols" -> vectorCols
  )
)
```

**Schema Inference**:

The writer automatically infers schema from DataFrame structure, mapping Spark types to Azure Search field types. Vector columns must be explicitly configured via the `vectorCols` parameter.

Sources: [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/search/AzureSearch.scala](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:1-707](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:525-532](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:675-706]()

## Usage Patterns

### Basic Transformer Pattern

All Cognitive Services transformers follow the Spark `Transformer` pattern:

1. Instantiate the transformer class
2. Configure authentication (subscription key or AAD token)
3. Set input/output column names
4. Call `transform()` on a DataFrame

**Example with `TextSentiment`**:

```scala
import com.microsoft.azure.synapse.ml.services.text.TextSentiment
import org.apache.spark.sql.functions.col

// Create input DataFrame
val textDF = Seq(
  ("en", "This is a great product!"),
  ("en", "I am very disappointed.")
).toDF("language", "text")

// Configure transformer
val sentiment = new TextSentiment()
  .setSubscriptionKey(cognitiveServicesKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setLanguageCol("language")
  .setOutputCol("sentiment")
  .setErrorCol("error")

// Transform DataFrame
val results = sentiment.transform(textDF)
  .select("text", "sentiment.document.sentiment", "sentiment.document.confidenceScores")

results.show()
```

The output DataFrame includes the original columns plus new columns for results and errors (if `setErrorCol()` was called).

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:122-128](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalytics.scala]()

### Authentication Patterns

**Static Subscription Key**:

```scala
val transformer = new LanguageDetector()
  .setSubscriptionKey(cognitiveKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setOutputCol("language")
```

**Per-Row Subscription Keys** (from DataFrame column):

```scala
val transformer = new TextSentiment()
  .setSubscriptionKeyCol("apiKey")  // Column name containing keys
  .setLocation("eastus")
  .setTextCol("text")
  .setOutputCol("sentiment")
```

This is useful when processing data from multiple cognitive services accounts or when keys are stored per-tenant.

**Azure AD Token Authentication**:

```scala
val transformer = new DetectAnomalies()
  .setAADToken(azureAdToken)
  .setLocation("westus2")
  .setTimestampCol("ts")
  .setValueCol("value")
  .setOutputCol("anomalies")
```

**Custom Endpoints**:

For private endpoints or custom domains:

```scala
val transformer = new TextSentiment()
  .setSubscriptionKey(key)
  .setUrl("https://my-custom-endpoint.cognitiveservices.azure.com/")
  .setTextCol("text")
  .setOutputCol("sentiment")
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:48-51](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/AnamolyDetectionSuite.scala:91-98](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala]()

### Input Data Types

Different services accept different input formats:

**Text Services** (columns containing strings):

```scala
val df = Seq(
  "Hello world",
  "Azure Cognitive Services are great"
).toDF("text")

new KeyPhraseExtractor()
  .setTextCol("text")
  .transform(df)
```

**Vision Services** (image URLs or binary data):

```scala
// From URLs
val imageUrls = Seq(
  "https://example.com/image1.jpg",
  "https://example.com/image2.jpg"
).toDF("imageUrl")

new AnalyzeImage()
  .setImageUrlCol("imageUrl")
  .transform(imageUrls)

// From binary data (using BinaryFileDataFrame)
val images = spark.read.format("binaryFile")
  .load("path/to/images/*.jpg")

new AnalyzeImage()
  .setImageBytesCol("content")
  .transform(images)
```

**Speech Services** (audio URLs, binary data, or streaming):

```scala
// Audio file URL
val audioUrl = Seq("https://example.com/audio.wav").toDF("audioUrl")

new SpeechToTextSDK()
  .setAudioDataCol("audioUrl")
  .transform(audioUrl)

// Streaming media (HLS)
val streamUrl = Seq("http://stream.example.com/live.m3u8").toDF("streamUrl")

new SpeechToTextSDK()
  .setAudioDataCol("streamUrl")
  .setExtraFfmpegArgs(Array("-t", "60"))  // Process 60 seconds
  .transform(streamUrl)
```

**Anomaly Detection** (time series with timestamp and value):

```scala
val timeSeries = Seq(
  ("2023-01-01T00:00:00Z", 10.5),
  ("2023-01-01T01:00:00Z", 12.3),
  ("2023-01-01T02:00:00Z", 45.7)  // Anomaly
).toDF("timestamp", "value")

new DetectAnomalies()
  .setTimestampCol("timestamp")
  .setValueCol("value")
  .transform(timeSeries)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:225-232](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:250-261](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/vision/AnalyzeImage.scala]()

### Batching Strategies

Azure Cognitive Services APIs have rate limits and quota constraints. SynapseML provides batching mechanisms to optimize throughput.

**Automatic Internal Batching**:

Most transformers automatically batch requests internally. Control batch size via `setConcurrency()`:

```scala
val sentiment = new TextSentiment()
  .setSubscriptionKey(key)
  .setConcurrency(10)  // Process 10 concurrent requests
  .setTextCol("text")
  .setOutputCol("sentiment")
```

**DataFrame-Level Batching with `FixedMiniBatchTransformer`**:

For explicit control over batch boundaries:

```scala
import com.microsoft.azure.synapse.ml.stages.FixedMiniBatchTransformer

// Create mini-batches of 10 rows each
val batchedDF = new FixedMiniBatchTransformer()
  .setBatchSize(10)
  .transform(inputDF)

// Process batches
val results = new TextSentiment()
  .setSubscriptionKey(key)
  .setTextCol("text")
  .setOutputCol("sentiment")
  .transform(batchedDF)
  .withColumn("result", explode(col("sentiment")))
```

**Coalescing Partitions**:

Reduce partition count to increase batch sizes:

```scala
val results = textAnalyzer.transform(largeDF.coalesce(10))
```

This is useful when you have many small partitions and want to increase effective batch sizes.

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:148-155](), [core/src/main/scala/com/microsoft/azure/synapse/ml/stages/MiniBatchTransformer.scala]()

### Error Handling

Use `setErrorCol()` to capture errors without failing the entire job:

```scala
import org.apache.spark.sql.functions.col

val sentiment = new TextSentiment()
  .setSubscriptionKey(key)
  .setLocation("eastus")
  .setTextCol("text")
  .setOutputCol("sentiment")
  .setErrorCol("error")  // Capture errors here

val results = sentiment.transform(inputDF)

// Separate successful and failed rows
val successful = results.filter(col("error").isNull)
val failed = results.filter(col("error").isNotNull)

// Inspect errors
failed.select("text", "error.message", "error.statusCode").show()
```

**Error Structure**:

The error column contains:
- `message`: Error message text
- `statusCode`: HTTP status code (e.g., 429 for rate limiting, 401 for auth failure)
- `error`: Full error response from the API

**Retry Logic**:

The HTTP client infrastructure (see section 5.2) automatically retries transient failures (5xx errors, timeouts). Configure retry behavior via:

```scala
val transformer = new TextSentiment()
  .setSubscriptionKey(key)
  .setBackoffs(Array(100, 500, 1000))  // Retry with backoffs in ms
  .setMaxRetries(3)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/TextToSpeechSuite.scala:38-42](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala]()

## Multi-Service Pipeline Examples

### Speech-to-Text with Text Analytics

Transcribe audio and analyze the resulting text:

```mermaid
graph LR
    AudioFiles["Audio Files<br/>(WAV, MP3)"]
    SpeechToTextSDK["SpeechToTextSDK"]
    TranscribedText["Transcribed Text"]
    LanguageDetector["LanguageDetector"]
    TextSentiment["TextSentiment"]
    KeyPhraseExtractor["KeyPhraseExtractor"]
    Results["Analysis Results"]
    
    AudioFiles --> SpeechToTextSDK
    SpeechToTextSDK --> TranscribedText
    TranscribedText --> LanguageDetector
    LanguageDetector --> TextSentiment
    TextSentiment --> KeyPhraseExtractor
    KeyPhraseExtractor --> Results
```

**Implementation**:

```scala
// Step 1: Transcribe audio
val transcription = new SpeechToTextSDK()
  .setSubscriptionKey(speechKey)
  .setLocation("eastus")
  .setAudioDataCol("audioUrl")
  .setOutputCol("transcription")
  .transform(audioDF)
  .select("audioUrl", "transcription.DisplayText")
  .withColumnRenamed("DisplayText", "text")

// Step 2: Detect language
val withLanguage = new LanguageDetector()
  .setSubscriptionKey(textKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setOutputCol("language")
  .transform(transcription)

// Step 3: Analyze sentiment
val withSentiment = new TextSentiment()
  .setSubscriptionKey(textKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setLanguageCol("language")
  .setOutputCol("sentiment")
  .transform(withLanguage)

// Step 4: Extract key phrases
val results = new KeyPhraseExtractor()
  .setSubscriptionKey(textKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setLanguageCol("language")
  .setOutputCol("keyPhrases")
  .transform(withSentiment)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:286-304]()

### Image Analysis with Search Indexing

Analyze images and index results for search:

```mermaid
graph LR
    ImageURLs["Image URLs"]
    AnalyzeImage["AnalyzeImage"]
    ImageAnalysis["tags, objects,<br/>descriptions"]
    FlattenResults["Flatten Results"]
    AzureSearchWriter["AzureSearchWriter"]
    SearchIndex["Azure Search Index"]
    
    ImageURLs --> AnalyzeImage
    AnalyzeImage --> ImageAnalysis
    ImageAnalysis --> FlattenResults
    FlattenResults --> AzureSearchWriter
    AzureSearchWriter --> SearchIndex
```

**Implementation**:

```scala
import org.apache.spark.sql.functions._

// Step 1: Analyze images
val analyzed = new AnalyzeImage()
  .setSubscriptionKey(visionKey)
  .setLocation("eastus")
  .setImageUrlCol("url")
  .setOutputCol("analysis")
  .setVisualFeatures(Array("Tags", "Description", "Objects"))
  .transform(imageDF)

// Step 2: Flatten results
val flattened = analyzed
  .select(
    col("url").as("id"),
    col("url"),
    col("analysis.description.captions")(0)("text").as("description"),
    col("analysis.tags.name").as("tags")
  )

// Step 3: Index in Azure Search
AzureSearchWriter.write(
  flattened,
  Map(
    "subscriptionKey" -> searchKey,
    "serviceName" -> searchServiceName,
    "indexName" -> "image-index",
    "keyCol" -> "id"
  )
)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:448-475]()

### OpenAI Embeddings with Vector Search

Generate embeddings using OpenAI and store in Azure Search (see section 6.1 for OpenAI details):

```mermaid
graph LR
    TextData["Text Documents"]
    OpenAIEmbedding["OpenAIEmbedding"]
    VectorEmbeddings["Vector Embeddings<br/>(1536 dimensions)"]
    AzureSearchWriter["AzureSearchWriter"]
    VectorIndex["Vector Search Index"]
    
    TextData --> OpenAIEmbedding
    OpenAIEmbedding --> VectorEmbeddings
    VectorEmbeddings --> AzureSearchWriter
    AzureSearchWriter --> VectorIndex
```

**Implementation**:

```scala
// Step 1: Generate embeddings (requires OpenAI key)
val embeddings = new OpenAIEmbedding()
  .setSubscriptionKey(openaiKey)
  .setDeploymentName("text-embedding-ada-002")
  .setTextCol("text")
  .setOutputCol("embedding")
  .transform(textDF)

// Step 2: Index with vector search
val vectorConfig = """[
  {"name": "embedding", "dimension": 1536}
]"""

AzureSearchWriter.write(
  embeddings,
  Map(
    "subscriptionKey" -> searchKey,
    "serviceName" -> searchServiceName,
    "indexName" -> "vector-index",
    "keyCol" -> "id",
    "vectorCols" -> vectorConfig
  )
)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:675-706]()

## Advanced Configuration

### Custom Endpoints and Private Links

For private endpoints or custom domains:

```scala
// Option 1: Custom service name
new TextSentiment()
  .setSubscriptionKey(key)
  .setLocation("eastus")
  .setCustomServiceName("my-text-analytics")  // Resolves to my-text-analytics.cognitiveservices.azure.com
  .setTextCol("text")
  .setOutputCol("sentiment")

// Option 2: Full custom URL
new TextSentiment()
  .setSubscriptionKey(key)
  .setUrl("https://my-private-endpoint.privatelink.cognitiveservices.azure.com/")
  .setTextCol("text")
  .setOutputCol("sentiment")
```

### Custom Models and Endpoints

**Speech Services with Custom Models**:

```scala
val speechToText = new SpeechToTextSDK()
  .setSubscriptionKey(customSpeechKey)
  .setLocation("eastus")
  .setEndpointId("custom-model-endpoint-id")  // Your custom speech model
  .setAudioDataCol("audio")
  .setOutputCol("transcription")
```

**Computer Vision with Custom Models**:

```scala
val customVision = new AnalyzeImage()
  .setSubscriptionKey(customVisionKey)
  .setUrl("https://my-custom-vision.cognitiveservices.azure.com/")
  .setImageUrlCol("imageUrl")
  .setOutputCol("analysis")
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:152-155](), [cognitive/src/main/scala/com/microsoft/azure/synapse/ml/services/CognitiveServicesBase.scala]()

### Output File Handling

**Saving Generated Audio Files**:

```scala
val textToSpeech = new TextToSpeech()
  .setSubscriptionKey(speechKey)
  .setLocation("eastus")
  .setTextCol("text")
  .setVoiceName("en-US-JennyNeural")
  .setOutputFileCol("audioPath")  // Save to file system

val results = textToSpeech.transform(textDF)
// Results include "audioPath" column with file paths
```

**Saving Transcription Results**:

```scala
val speechToText = new SpeechToTextSDK()
  .setSubscriptionKey(speechKey)
  .setLocation("eastus")
  .setAudioDataCol("audioUrl")
  .setRecordAudioData(true)  // Save processed audio
  .setRecordedFileNameCol("processedAudio")
  .setOutputCol("transcription")
```

### Vector Search Schema Configuration

Configure multiple vector columns with different dimensions:

```scala
val vectorSchema = """[
  {"name": "titleVector", "dimension": 1536, "type": "Collection(Edm.Single)"},
  {"name": "contentVector", "dimension": 1536, "type": "Collection(Edm.Single)"},
  {"name": "smallVector", "dimension": 384, "type": "Collection(Edm.Single)"}
]"""

AzureSearchWriter.write(
  df,
  Map(
    "subscriptionKey" -> searchKey,
    "serviceName" -> serviceName,
    "indexName" -> indexName,
    "keyCol" -> "id",
    "vectorCols" -> vectorSchema,
    "vectorFilterable" -> "true"  // Enable filtering on vectors
  )
)
```

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/search/SearchWriterSuite.scala:525-532]()

## Performance Considerations

- Use batching for better throughput when processing large datasets
- Consider record size limits when batching
- Set appropriate timeout values for larger files or complex operations
- For streaming media, use the `setExtraFfmpegArgs` parameter to limit processing time
- Use the record functions for audio data to save processed files

Sources: [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/speech/SpeechToTextSDKSuite.scala:270-279](), [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/text/TextAnalyticsSuite.scala:148-155]()

---

# Page: LangChain Integration

# LangChain Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py](cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py](cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py)
- [cognitive/src/test/python/synapsemltest/services/test_simple.py](cognitive/src/test/python/synapsemltest/services/test_simple.py)
- [core/src/main/python/synapse/ml/core/init_spark.py](core/src/main/python/synapse/ml/core/init_spark.py)
- [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py](core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py)
- [core/src/main/python/synapse/ml/core/logging/__init__.py](core/src/main/python/synapse/ml/core/logging/__init__.py)
- [core/src/main/python/synapse/ml/core/platform/Platform.py](core/src/main/python/synapse/ml/core/platform/Platform.py)
- [core/src/test/python/synapsemltest/core/test_logging.py](core/src/test/python/synapsemltest/core/test_logging.py)
- [core/src/test/python/synapsemltest/core/test_template.py](core/src/test/python/synapsemltest/core/test_template.py)
- [docs/Get Started/Set up Cognitive Services.ipynb](docs/Get Started/Set up Cognitive Services.ipynb)

</details>



## Purpose and Scope

The LangChain Integration provides a Spark-native transformer that enables distributed execution of [LangChain](https://python.langchain.com/) chains across large datasets using Apache Spark DataFrames. This integration allows users to apply pre-configured LangChain chains (such as prompt templates, LLM chains, and agents) to each row of a DataFrame in parallel, leveraging Spark's distributed computing capabilities.

This page covers the `LangchainTransformer` implementation, its architecture, platform integration, and usage patterns. For Azure OpenAI services integration without LangChain, see [OpenAI Integration](#6.1). For general cognitive services, see [Azure Cognitive Services](#6.2).

## Architecture Overview

The LangChain integration is built around a single transformer class that wraps LangChain chains and executes them as Spark UDFs. The transformer handles platform-specific configuration, error management, and serialization.

```mermaid
graph TB
    subgraph "User Code Space"
        UserChain["LangChain Chain<br/>(LLMChain, Agents, etc)"]
        UserDF["Input DataFrame<br/>with inputCol"]
    end
    
    subgraph "LangchainTransformer"
        Params["Parameters<br/>chain, inputCol, outputCol<br/>subscriptionKey, url"]
        UDF["_transform() UDF<br/>udfFunction()"]
        ErrorHandler["Error Handler<br/>openai.error.*"]
    end
    
    subgraph "Platform Integration"
        PlatformCheck["running_on_synapse_internal()"]
        FabricConfig["get_fabric_env_config()<br/>fabric_env_config"]
        OpenAISetup["OpenAI API Setup<br/>api_type, api_key, api_base"]
    end
    
    subgraph "Execution"
        SparkExecutor["Spark Executors<br/>Parallel Processing"]
        ChainRun["chain.run(x)<br/>Per-Row Execution"]
    end
    
    subgraph "Output"
        ResultDF["Output DataFrame<br/>outputCol + errorCol"]
    end
    
    UserChain --> Params
    UserDF --> UDF
    Params --> UDF
    
    UDF --> PlatformCheck
    PlatformCheck -->|"Fabric"| FabricConfig
    PlatformCheck -->|"Non-Fabric"| OpenAISetup
    
    UDF --> SparkExecutor
    SparkExecutor --> ChainRun
    ChainRun --> ErrorHandler
    
    ErrorHandler --> ResultDF
    
    style UDF fill:#f9f9f9
    style SparkExecutor fill:#f9f9f9
    style PlatformCheck fill:#f9f9f9
```

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:1-296]()

## Core Components

### LangchainTransformer Class

The `LangchainTransformer` class is the primary interface for LangChain integration. It extends Spark ML's `Transformer` base class and implements parameter management for chain configuration.

```mermaid
graph LR
    subgraph "Class Hierarchy"
        Transformer["pyspark.ml.Transformer"]
        HasInputCol["HasInputCol"]
        HasOutputCol["HasOutputCol"]
        DefaultParamsReadable["DefaultParamsReadable"]
        DefaultParamsWritable["DefaultParamsWritable"]
        
        LangchainTransformer["LangchainTransformer"]
    end
    
    Transformer --> LangchainTransformer
    HasInputCol --> LangchainTransformer
    HasOutputCol --> LangchainTransformer
    DefaultParamsReadable --> LangchainTransformer
    DefaultParamsWritable --> LangchainTransformer
```

**Key Parameters:**
- `chain`: The LangChain chain object to execute [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:125-129]()
- `inputCol`: Column name containing input data [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:195-199]()
- `outputCol`: Column name for chain results [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:201-205]()
- `subscriptionKey`: Azure OpenAI API key [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:130]()
- `url`: Azure OpenAI API base URL [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:131]()
- `apiVersion`: OpenAI API version (default: "2022-12-01") [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:52]()
- `errorCol`: Column name for error messages [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:134]()

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:110-219]()

### Transform Execution Flow

The `_transform()` method implements the core execution logic using a Spark UDF that applies the chain to each row:

```mermaid
graph TB
    Start["_transform(dataset)"] --> DefineSchema["Define UDF Schema<br/>StructType(result, error_message)"]
    DefineSchema --> CreateUDF["Create UDF<br/>udfFunction(x)"]
    
    subgraph "UDF Execution Per Row"
        CheckPlatform["Check Platform<br/>running_on_synapse_internal"]
        CheckPlatform -->|"True & no url"| FabricInit["OpenAIPrerun<br/>init_personalized_session()"]
        CheckPlatform -->|"False or url set"| StandardInit["Set openai.api_type<br/>api_key, api_base, api_version"]
        
        FabricInit --> RunChain["self.getChain().run(x)"]
        StandardInit --> RunChain
        
        RunChain -->|"Success"| ReturnResult["return (result, '')"]
        RunChain -->|"Exception"| CatchError["Catch openai.error.*"]
        CatchError --> FormatError["Format error message"]
        FormatError --> ReturnError["return ('', error_message)"]
    end
    
    CreateUDF --> ApplyUDF["dataset.withColumn(temp_col_name, udfFunction(inCol))"]
    ApplyUDF --> ExtractColumns["Extract result and error columns"]
    ExtractColumns --> DropTemp["Drop temporary column"]
    DropTemp --> Return["Return DataFrame"]
    
    style RunChain fill:#f9f9f9
    style CatchError fill:#f9f9f9
```

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:220-284]()

## Usage Patterns

### Basic Usage

A typical usage pattern involves creating a LangChain chain and wrapping it with `LangchainTransformer`:

| Step | Component | Description |
|------|-----------|-------------|
| 1 | Create LLM | Initialize `AzureChatOpenAI` or similar LangChain LLM |
| 2 | Create Prompt | Define `PromptTemplate` with input variables |
| 3 | Create Chain | Build `LLMChain(llm=llm, prompt=prompt)` |
| 4 | Create Transformer | Initialize `LangchainTransformer()` with parameters |
| 5 | Transform | Call `transformer.transform(dataframe)` |

**Example from test suite:**
The test creates a simple copy chain that repeats input text:
- LLM: `AzureChatOpenAI` with deployment "gpt-4o" [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:38-43]()
- Prompt: `PromptTemplate` with variable "technology" [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:50-53]()
- Chain: `LLMChain(llm=llm, prompt=copy_prompt)` [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:55]()
- Transformer: Configured with inputCol="technology", outputCol="copied_technology" [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:56-63]()

Sources: [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:37-69]()

### Parameter Configuration

```mermaid
graph LR
    subgraph "Required Parameters"
        ReqInputCol["inputCol<br/>setInputCol(name)"]
        ReqOutputCol["outputCol<br/>setOutputCol(name)"]
        ReqChain["chain<br/>setChain(chain)"]
    end
    
    subgraph "Authentication (Non-Fabric)"
        AuthKey["subscriptionKey<br/>setSubscriptionKey(key)"]
        AuthUrl["url<br/>setUrl(url)"]
    end
    
    subgraph "Optional Parameters"
        OptApiVer["apiVersion<br/>setApiVersion(version)"]
        OptErrorCol["errorCol<br/>setErrorCol(name)"]
    end
    
    ReqInputCol --> Transform["transform()"]
    ReqOutputCol --> Transform
    ReqChain --> Transform
    
    AuthKey --> Transform
    AuthUrl --> Transform
    
    OptApiVer --> Transform
    OptErrorCol --> Transform
```

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:168-218]()

## Platform Integration

### Platform Detection and Configuration

The transformer adapts its behavior based on the execution environment using the platform detection system:

```mermaid
graph TB
    Init["__init__()"] --> CheckPlatform["running_on_synapse_internal()"]
    
    CheckPlatform -->|"True"| GetFabricConfig["get_fabric_env_config()"]
    GetFabricConfig --> SetFabricURL["_setDefault(url=<br/>fabric_env_config.ml_workload_endpoint<br/>+ 'cognitive/openai')"]
    
    CheckPlatform -->|"False"| NoDefault["No default URL"]
    
    SetFabricURL --> StoreFlag["self.running_on_synapse_internal = True"]
    NoDefault --> StoreFlag2["self.running_on_synapse_internal = False"]
    
    subgraph "Transform-time Behavior"
        TransformCheck["Check running_on_synapse_internal<br/>and not self.isSet(self.url)"]
        TransformCheck -->|"True"| UseFabric["OpenAIPrerun<br/>init_personalized_session()"]
        TransformCheck -->|"False"| UseStandard["Set openai.api_* manually"]
    end
    
    StoreFlag --> TransformCheck
    StoreFlag2 --> TransformCheck
```

**Platform-Specific Behavior:**

| Platform | URL Configuration | Authentication |
|----------|------------------|----------------|
| Fabric (Synapse Internal) | Auto-configured from `fabric_env_config.ml_workload_endpoint` | Handled by `OpenAIPrerun.init_personalized_session()` |
| Non-Fabric | User-provided via `setUrl()` | User-provided via `setSubscriptionKey()` |

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:133-142](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:238-246](), [core/src/main/python/synapse/ml/core/platform/Platform.py:37-54]()

### OpenAI API Configuration

The UDF execution sets up OpenAI API parameters differently based on the platform:

**Fabric (Internal) Path:**
1. Detect `running_on_synapse_internal == True` and URL not explicitly set
2. Import `OpenAIPrerun` from `synapse.ml.fabric.prerun.openai_prerun`
3. Call `OpenAIPrerun(api_base=self.getUrl()).init_personalized_session(None)`

**Standard Path:**
1. Set `openai.api_type = "azure"`
2. Set `openai.api_key = self.getSubscriptionKey()`
3. Set `openai.api_base = self.getUrl()`
4. Set `openai.api_version = self.getApiVersion()`

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:238-246]()

## Save/Load Mechanism

### Serialization Architecture

The transformer implements custom save/load logic to handle LangChain chain serialization:

```mermaid
graph TB
    subgraph "Save Process"
        SaveCall["transformer.save(path)"] --> Writer["write()<br/>LangchainTransformerParamsWriter"]
        Writer --> SaveImpl["saveImpl(path)"]
        SaveImpl --> CheckMemory["Check chain.memory"]
        CheckMemory -->|"Not None"| ThrowError["Raise NotImplementedError<br/>'Memory saving not supported'"]
        CheckMemory -->|"None"| SerializeChain["_chain_serializer(chain)<br/>json.dumps(chain.dict())"]
        SerializeChain --> SaveMetadata["DefaultParamsWriter.saveMetadata()"]
    end
    
    subgraph "Load Process"
        LoadCall["LangchainTransformer.load(path)"] --> Reader["read()<br/>LangchainTransformerParamsReader"]
        Reader --> LoadMeta["loadMetadata(path)"]
        LoadMeta --> DeserializeChain["load_chain_from_config(<br/>json.loads(chain_str))"]
        DeserializeChain --> SetParams["getAndSetParams()"]
        SetParams --> ReturnInstance["Return instance"]
    end
```

**Limitations:**
- Chains with memory cannot be saved [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:59-64]()
- Only chains that support `chain.dict()` serialization are compatible

**Custom Writer/Reader Classes:**
- `LangchainTransformerParamsWriter`: Extends `DefaultParamsWriter` with chain serialization [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:56-82]()
- `LangchainTransformerParamsReader`: Extends `DefaultParamsReader` with chain deserialization [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:84-107]()

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:56-107](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:286-295]()

## Error Handling

### Error Capture Mechanism

The transformer captures errors at execution time and stores them in the error column rather than failing the entire job:

```mermaid
graph TB
    UDFExec["UDF Execution<br/>udfFunction(x)"] --> TryBlock["Try: chain.run(x)"]
    
    TryBlock -->|"Success"| SuccessReturn["return (result, '')"]
    TryBlock -->|"Exception"| CatchBlock["except tuple(error_messages.keys())"]
    
    subgraph "Error Message Mapping"
        ErrorDict["error_messages dict"]
        ErrorDict -.->|"Timeout"| TimeoutMsg["'OpenAI API request timed out...'"]
        ErrorDict -.->|"APIError"| APIMsg["'OpenAI API returned an API Error...'"]
        ErrorDict -.->|"APIConnectionError"| ConnMsg["'Failed to connect, check network...'"]
        ErrorDict -.->|"InvalidRequestError"| InvalidMsg["'Request was invalid...'"]
        ErrorDict -.->|"AuthenticationError"| AuthMsg["'Not authorized, check API key...'"]
        ErrorDict -.->|"PermissionError"| PermMsg["'Not permitted, check permissions...'"]
        ErrorDict -.->|"RateLimitError"| RateMsg["'Exceeded rate limit...'"]
    end
    
    CatchBlock --> FormatMsg["error_message = error_messages[type(e)].format(e)"]
    FormatMsg --> ErrorReturn["return ('', error_message)"]
    
    SuccessReturn --> OutputDF["DataFrame with<br/>outputCol + errorCol"]
    ErrorReturn --> OutputDF
```

**Error Handling Features:**
- Different error messages for OpenAI API versions (< 1.0.0 vs >= 1.0.0) [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:249-262]()
- Detailed error messages with troubleshooting guidance [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:250-258]()
- Empty result with populated error message on failure [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:268-269]()
- Allows partial dataset processing (successful rows return results, failed rows return errors)

**Test Coverage:**
The test suite validates error handling with content filter violations [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:115-127]()

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:248-271](), [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:104-127]()

## Output Schema

The transformer returns a DataFrame with the original columns plus the output and error columns:

| Column Type | Column Name | Data Type | Content |
|-------------|-------------|-----------|---------|
| Original | (unchanged) | (unchanged) | Input DataFrame columns |
| Output | `outputCol` (configurable) | StringType | Chain execution result or empty string on error |
| Error | `errorCol` (default: "errorCol") | StringType | Error message or empty string on success |

The output schema is defined as a `StructType` with two fields: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:226-231]()
- "result": StringType, nullable=True
- "error_message": StringType, nullable=True

These are then extracted into separate columns via column projection [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:279-283]()

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:226-284]()

## Dependencies and Integration Points

### External Dependencies

The transformer integrates with several external libraries and internal SynapseML components:

```mermaid
graph LR
    subgraph "External Libraries"
        LangChain["langchain<br/>LLMChain, PromptTemplate"]
        OpenAI["openai<br/>API Client"]
        Packaging["packaging<br/>version"]
    end
    
    subgraph "Spark"
        PySparkML["pyspark.ml<br/>Transformer, Param"]
        PySparkSQL["pyspark.sql.functions<br/>udf, col"]
    end
    
    subgraph "SynapseML Core"
        Platform["core.platform.Platform<br/>running_on_synapse_internal()"]
    end
    
    subgraph "Fabric Integration (Conditional)"
        ServiceDiscovery["fabric.service_discovery<br/>get_fabric_env_config()"]
        OpenAIPrerun["fabric.prerun.openai_prerun<br/>OpenAIPrerun"]
    end
    
    LangchainTransformer --> LangChain
    LangchainTransformer --> OpenAI
    LangchainTransformer --> Packaging
    LangchainTransformer --> PySparkML
    LangchainTransformer --> PySparkSQL
    LangchainTransformer --> Platform
    
    LangchainTransformer -.->|"if Fabric"| ServiceDiscovery
    LangchainTransformer -.->|"if Fabric"| OpenAIPrerun
```

**Key Integration Points:**
1. **LangChain Core**: Uses `chain.run()` for execution and `chain.dict()` for serialization [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:33](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:265]()
2. **OpenAI Client**: Configures Azure OpenAI via module-level settings [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:243-246]()
3. **Platform Detection**: Uses `running_on_synapse_internal()` to detect Fabric environments [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:50]()
4. **Fabric Services**: Conditionally imports Fabric-specific modules when running on internal Synapse [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:136-141](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:239-241]()

Sources: [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:31-50](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:133-142](), [cognitive/src/main/python/synapse/ml/services/langchain/LangchainTransform.py:235-246]()

## Testing and Validation

The test suite validates the transformer's core functionality across different scenarios:

**Test Structure:**
- Test class: `LangchainTransformTest` [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:16]()
- Setup: Configures OpenAI credentials from Azure Key Vault [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:20-32]()
- Test DataFrame: Simple 3-row dataset with "technology" column [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:66-68]()

**Test Cases:**

| Test Method | Validation | Lines |
|-------------|------------|-------|
| `test_langchainTransform` | Basic transformation with successful output | [96-102]() |
| `test_langchainTransformErrorHandling` | Error column populated on content filter violations | [115-127]() |
| `test_save_load` (skipped) | Serialization/deserialization of transformer | [129-141]() |

**Assertions:**
- Output contains input text (case-insensitive) [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:92-94]()
- Error column contains expected error text on filtered content [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:111-113]()

Sources: [cognitive/src/test/python/synapsemltest/services/langchain/test_LangchainTransform.py:1-145]()

---

# Page: Deep Learning Integration

# Deep Learning Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala)
- [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala](core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala)
- [core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala](core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala)
- [deep-learning/src/main/python/horovod_installation.sh](deep-learning/src/main/python/horovod_installation.sh)
- [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py)
- [docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb](docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb)
- [start](start)
- [tools/docker/demo/Dockerfile](tools/docker/demo/Dockerfile)
- [tools/docker/demo/README.md](tools/docker/demo/README.md)
- [tools/docker/demo/init_notebook.py](tools/docker/demo/init_notebook.py)
- [tools/docker/minimal/Dockerfile](tools/docker/minimal/Dockerfile)
- [tools/tests/run_r_tests.R](tools/tests/run_r_tests.R)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala)

</details>



The deep learning integration in SynapseML provides distributed training capabilities for neural network models using Horovod and PyTorch Lightning. This system enables large-scale fine-tuning of pre-trained models for text and vision classification tasks, leveraging Apache Spark for distributed data processing and Horovod for distributed training across multiple GPUs.

This page covers the deep learning components specifically. For traditional ML algorithms like LightGBM, see [LightGBM Integration](#6.5). For Vowpal Wabbit online learning, see [Vowpal Wabbit Integration](#6.6). For ONNX model inference without distributed training, ONNX capabilities are included in this module but not extensively covered in the provided files.

## Architecture Overview

The deep learning integration consists of two primary components: text classifiers and vision classifiers, both built on top of Horovod's distributed training framework and PyTorch Lightning's modular training system.

```mermaid
graph TB
    subgraph "User API Layer"
        DeepTextClassifier["DeepTextClassifier<br/>(TorchEstimator)"]
        DeepVisionClassifier["DeepVisionClassifier<br/>(TorchEstimator)"]
    end
    
    subgraph "PyTorch Lightning Models"
        LitDeepTextModel["LitDeepTextModel<br/>(pl.LightningModule)"]
        LitDeepVisionModel["LitDeepVisionModel<br/>(pl.LightningModule)"]
    end
    
    subgraph "Model Sources"
        HuggingFace["HuggingFace Transformers<br/>AutoModelForSequenceClassification"]
        TorchVision["TorchVision Models<br/>resnet, vgg, efficientnet, etc."]
    end
    
    subgraph "Distributed Training"
        Horovod["Horovod<br/>horovod.spark.lightning"]
        SparkBackend["SparkBackend<br/>Process Management"]
    end
    
    subgraph "Data Processing"
        Tokenizer["AutoTokenizer<br/>Text Encoding"]
        Transform["torchvision.transforms<br/>Image Augmentation"]
        Petastorm["Petastorm<br/>Spark DataFrame to PyTorch"]
    end
    
    subgraph "Trained Models"
        DeepTextModel["DeepTextModel"]
        DeepVisionModel["DeepVisionModel"]
    end
    
    DeepTextClassifier --> LitDeepTextModel
    DeepVisionClassifier --> LitDeepVisionModel
    
    LitDeepTextModel --> HuggingFace
    LitDeepVisionModel --> TorchVision
    
    DeepTextClassifier --> Horovod
    DeepVisionClassifier --> Horovod
    Horovod --> SparkBackend
    
    DeepTextClassifier --> Tokenizer
    DeepVisionClassifier --> Transform
    
    Horovod --> Petastorm
    
    DeepTextClassifier --> DeepTextModel
    DeepVisionClassifier --> DeepVisionModel
```

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:1-289](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:1-269](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:1-177](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:1-234]()

## Horovod Distributed Training Framework

SynapseML's deep learning components use **Horovod** as the distributed training backend, specifically the `horovod.spark.lightning.TorchEstimator` class. This integration enables data-parallel training across multiple Spark executors, with each executor potentially utilizing multiple GPUs.

### Key Components

| Component | Class | Purpose |
|-----------|-------|---------|
| Estimator | `TorchEstimator` | Base class for distributed training, handles data distribution and model synchronization |
| Backend | `SparkBackend` | Manages Spark executor processes for Horovod training |
| Data Converter | Petastorm | Converts Spark DataFrames to PyTorch tensors for training |
| Model | `pl.LightningModule` | PyTorch Lightning module defining model architecture and training logic |

### Installation

Horovod requires specific compilation with NCCL support for GPU training. The installation script demonstrates the required dependencies:

```bash
# Install PyTorch ecosystem
pip install pytorch-lightning==1.5.0
pip install torchvision==0.15.1
pip install transformers==4.49.0
pip install petastorm>=0.12.1

# Install CUDA and NCCL libraries
apt-get install --allow-downgrades --no-install-recommends -y \
    cuda-nvml-dev-11-0=11.0.167-1 \
    cuda-nvcc-11-0=11.0.221-1 \
    libnccl-dev=2.10.3-1+cuda11.0

# Compile Horovod with NCCL
HOROVOD_GPU_ALLREDUCE=NCCL HOROVOD_CUDA_HOME=/usr/local/cuda-11/ \
HOROVOD_WITH_PYTORCH=1 python setup.py bdist_wheel
```

**Sources**: [deep-learning/src/main/python/horovod_installation.sh:1-48]()

### Backend Configuration

The `get_or_create_backend` utility function manages the Spark backend configuration for Horovod:

```python
def get_or_create_backend(backend, num_proc, verbose, use_gpu):
    """Creates or retrieves existing SparkBackend for distributed training."""
    # Implementation creates SparkBackend with appropriate GPU/CPU configuration
```

Both `DeepTextClassifier` and `DeepVisionClassifier` override the default backend creation to ensure proper GPU configuration.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:226-229](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:217-221]()

## Text Classification with DeepTextClassifier

### Class Hierarchy

```mermaid
graph LR
    TorchEstimator["horovod.spark.lightning<br/>TorchEstimator"]
    TextPredictionParams["TextPredictionParams<br/>(Mixin)"]
    DeepTextClassifier["DeepTextClassifier"]
    LitDeepTextModel["LitDeepTextModel<br/>(pl.LightningModule)"]
    DeepTextModel["DeepTextModel<br/>(Trained Model)"]
    
    TorchEstimator --> DeepTextClassifier
    TextPredictionParams --> DeepTextClassifier
    DeepTextClassifier --> LitDeepTextModel
    DeepTextClassifier --> DeepTextModel
```

### Parameters

The `DeepTextClassifier` provides the following key parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `checkpoint` | String | Required | HuggingFace model checkpoint (e.g., "bert-base-uncased") |
| `num_classes` | Int | Required | Number of target classes for classification |
| `text_col` | String | "text" | Input column containing text data |
| `label_col` | String | "label" | Input column containing integer labels |
| `additional_layers_to_train` | Int | 3 | Number of final layers to fine-tune (0 = only classifier head) |
| `train_from_scratch` | Boolean | True | If False, freezes base model and only trains specified layers |
| `learning_rate` | Float | Auto (5e-5 for BERT) | Learning rate for optimizer |
| `optimizer_name` | String | "adam" | Optimizer function name from `torch.optim` |
| `loss_name` | String | "cross_entropy" | Loss function name from `torch.nn.functional` |
| `max_token_len` | Int | 128 | Maximum sequence length for tokenization |
| `tokenizer` | AutoTokenizer | Auto | HuggingFace tokenizer (auto-loaded from checkpoint) |

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:27-65]()

### Text Processing Pipeline

The text classification pipeline performs the following transformations on input DataFrames:

```mermaid
graph LR
    InputDF["Spark DataFrame<br/>text, label columns"]
    Tokenization["Tokenization<br/>AutoTokenizer.from_pretrained"]
    Encoding["Encoding<br/>padding, truncation, attention_mask"]
    TensorConversion["Tensor Conversion<br/>torch.tensor"]
    Petastorm["Petastorm Reader<br/>Spark to PyTorch"]
    Training["Distributed Training<br/>Horovod + PyTorch Lightning"]
    
    InputDF --> Tokenization
    Tokenization --> Encoding
    Encoding --> TensorConversion
    TensorConversion --> Petastorm
    Petastorm --> Training
```

The transformation function (`_encoding_text`) in `DeepTextClassifier._update_transformation_fn()` handles tokenization:

```python
def _encoding_text(row):
    text = row[text_col]
    label = row[label_col]
    encoding = tokenizer(
        text,
        max_length=max_token_len,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors="pt",
    )
    input_ids = encoding["input_ids"].flatten().numpy()
    attention_mask = encoding["attention_mask"].flatten().numpy()
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": torch.tensor(label, dtype=int),
    }
```

This transformation is applied using Petastorm's `transformation_fn` mechanism, which converts each row before feeding to the model.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:231-267]()

### LitDeepTextModel Architecture

The `LitDeepTextModel` class encapsulates the PyTorch Lightning training logic:

```mermaid
graph TB
    subgraph "LitDeepTextModel Initialization"
        CheckParams["_check_params<br/>Load AutoModelForSequenceClassification"]
        ValidateLoss["Validate loss_name in F.__dict__"]
        ValidateOptim["Validate optimizer_name in optim.__dict__"]
        SetLR["_update_learning_rate<br/>Default 5e-5 for BERT"]
    end
    
    subgraph "configure_optimizers"
        FreezeLayers["Freeze base_model parameters"]
        FineTune["_fine_tune_layers<br/>Unfreeze last N layers"]
        CreateOptim["Create optimizer with tunable params"]
    end
    
    subgraph "Training Steps"
        TrainingStep["training_step<br/>Forward pass + loss calculation"]
        ValidationStep["validation_step<br/>Validation loss"]
        LogMetrics["Log train_loss, val_loss"]
    end
    
    CheckParams --> ValidateLoss
    ValidateLoss --> ValidateOptim
    ValidateOptim --> SetLR
    
    FreezeLayers --> FineTune
    FineTune --> CreateOptim
    
    TrainingStep --> LogMetrics
    ValidationStep --> LogMetrics
```

The fine-tuning logic selectively unfreezes layers:

```python
def _fine_tune_layers(self):
    if self.additional_layers_to_train < 0:
        raise ValueError("additional_layers_to_train has to be non-negative")
    
    children = list(self.model.base_model.children())
    added_layer, cur_layer = 0, -1
    while added_layer < self.additional_layers_to_train and -cur_layer < len(children):
        tunable = False
        for p in children[cur_layer].parameters():
            p.requires_grad = True
            tunable = True
        if tunable:
            added_layer += 1
        cur_layer -= 1
```

This iterates backwards through the model's layers, unfreezing the last `additional_layers_to_train` layers that contain trainable parameters.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:29-177]()

### Supported Models

The `DeepTextClassifier` supports any HuggingFace checkpoint compatible with `AutoModelForSequenceClassification`, including:

- **BERT variants**: `bert-base-uncased`, `bert-large-cased`, `distilbert-base-uncased`
- **RoBERTa**: `roberta-base`, `roberta-large`
- **ALBERT**: `albert-base-v2`, `albert-large-v2`
- **ELECTRA**: `google/electra-small-discriminator`, `google/electra-base-discriminator`
- **DeBERTa**: `microsoft/deberta-base`, `microsoft/deberta-large`

The implementation enforces `transformers==4.49.0` for compatibility.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:14-24](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:88]()

## Vision Classification with DeepVisionClassifier

### Class Hierarchy

```mermaid
graph LR
    TorchEstimator["horovod.spark.lightning<br/>TorchEstimator"]
    VisionPredictionParams["VisionPredictionParams<br/>(Mixin)"]
    DeepVisionClassifier["DeepVisionClassifier"]
    LitDeepVisionModel["LitDeepVisionModel<br/>(pl.LightningModule)"]
    DeepVisionModel["DeepVisionModel<br/>(Trained Model)"]
    
    TorchEstimator --> DeepVisionClassifier
    VisionPredictionParams --> DeepVisionClassifier
    DeepVisionClassifier --> LitDeepVisionModel
    DeepVisionClassifier --> DeepVisionModel
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backbone` | String | Required | TorchVision model name (e.g., "resnet50", "efficientnet_b0") |
| `num_classes` | Int | Required | Number of target classes for classification |
| `image_col` | String | "image" | Input column containing image paths |
| `label_col` | String | "label" | Input column containing integer labels |
| `additional_layers_to_train` | Int | 0 | Number of final layers to fine-tune (0-3) |
| `optimizer_name` | String | "adam" | Optimizer function name |
| `loss_name` | String | "cross_entropy" | Loss function name |
| `dropout_aux` | Float | 0.7 | Dropout for GoogLeNet InceptionAux modules |
| `transform_fn` | Compose | Auto | TorchVision transforms pipeline |

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:32-66]()

### Image Processing Pipeline

```mermaid
graph LR
    ImagePath["Image File Path<br/>from DataFrame"]
    LoadImage["PIL.Image.open<br/>Convert to RGB"]
    Transforms["torchvision.transforms<br/>Resize, Crop, Normalize"]
    ToTensor["ToTensor<br/>Convert to torch.Tensor"]
    Petastorm["Petastorm Reader"]
    Training["Distributed Training"]
    
    ImagePath --> LoadImage
    LoadImage --> Transforms
    Transforms --> ToTensor
    ToTensor --> Petastorm
    Petastorm --> Training
```

The default transformation pipeline:

```python
transform = transforms.Compose([
    transforms.RandomResizedCrop(crop_size),  # 224x224 or 299x299 for Inception
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def _transform_row(row):
    path = row[image_col]
    label = row[label_col]
    image = Image.open(path).convert("RGB")
    image = transform(image).numpy()
    return {image_col: image, label_col: label}
```

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:223-250]()

### LitDeepVisionModel Architecture

The `LitDeepVisionModel` handles model initialization and layer-specific modifications:

#### Model Initialization and Classifier Head Replacement

```python
# Load pre-trained model
self.model = models.__dict__[self.backbone](pretrained=True)

# Freeze all parameters initially
for p in self.model.parameters():
    p.requires_grad = False

# Replace classifier head based on architecture
if backbone.startswith("resnet"):
    self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
elif backbone.startswith("efficientnet"):
    num_ftrs = self.model.classifier[-1].in_features
    self.model.classifier = nn.Linear(num_ftrs, num_classes)
elif backbone.startswith("vit"):
    num_ftrs = self.model.heads.head.in_features
    self.model.heads.head = nn.Linear(num_ftrs, num_classes)
# ... additional architectures
```

Each architecture family has a specific way to access and replace the final classification layer. The implementation handles 15+ architecture families.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:62-120]()

#### Fine-Tuning Strategy

```python
def _fine_tune_layers(self):
    children = list(self.model.children())
    added_layer, cur_layer = 0, -1
    while added_layer < self.additional_layers_to_train and -cur_layer < len(children):
        tunable = False
        for p in children[cur_layer].parameters():
            p.requires_grad = True
            tunable = True
        if tunable:
            added_layer += 1
        cur_layer -= 1
```

This method unfreezes the last N layers working backwards through the model architecture.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:176-189]()

#### Special Handling for Inception Models

Inception v3 models have auxiliary classifiers that require special handling during training:

```python
def _step(self, batch, validation):
    inputs = {"x": batch[self.image_col].reshape(self.input_shape)}
    label = batch[self.label_col]
    output = self(**inputs)
    
    if self.backbone.startswith("inception") and not validation:
        loss1 = self.loss_fn(output.logits, label.long())
        loss2 = self.loss_fn(output.aux_logits, label.long())
        loss = loss1 + 0.4 * loss2
    else:
        loss = self.loss_fn(output, label.long())
    return loss
```

During training, Inception models return both main and auxiliary outputs, and the total loss is a weighted combination.

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:205-217]()

### Supported Backbones

The `DeepVisionClassifier` supports all TorchVision models (version >= 0.14.1):

| Family | Examples | Input Size |
|--------|----------|------------|
| ResNet | `resnet18`, `resnet34`, `resnet50`, `resnet101`, `resnet152` | 224x224 |
| EfficientNet | `efficientnet_b0` through `efficientnet_b7` | 224x224 |
| Vision Transformer | `vit_b_16`, `vit_b_32`, `vit_l_16` | 224x224 |
| MobileNet | `mobilenet_v2`, `mobilenet_v3_small`, `mobilenet_v3_large` | 224x224 |
| ConvNeXt | `convnext_tiny`, `convnext_small`, `convnext_base` | 224x224 |
| VGG | `vgg11`, `vgg13`, `vgg16`, `vgg19` | 224x224 |
| Inception | `inception_v3` | 299x299 |
| DenseNet | `densenet121`, `densenet161`, `densenet169` | 224x224 |

The implementation includes a retry mechanism for downloading pre-trained weights to handle transient network failures:

```python
def _retry_download(self, func, times_left):
    try:
        return func()
    except URLError as e:
        if times_left == 0:
            raise e
        else:
            time.sleep(1)
            return self._retry_download(func, times_left - 1)

self.model = self._retry_download(
    lambda: models.__dict__[self.backbone](pretrained=True), 5
)
```

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:135-153]()

## Testing Infrastructure

### Test Environment Configuration

```mermaid
graph TB
    subgraph "Databricks Cluster Types"
        CPUCluster["CPU Cluster<br/>synapseml-build-14.3<br/>NumWorkers: 5"]
        GPUCluster["GPU Cluster<br/>synapseml-build-14.3-gpu<br/>NumWorkers: 2<br/>Runtime: 14.3.x-gpu-ml"]
        RapidsCluster["RAPIDS Cluster<br/>GPU + Init Scripts<br/>NumWorkers: 1"]
    end
    
    subgraph "Library Installation"
        MavenLibs["Maven: synapseml_2.12"]
        PipPackages["PyPI: pytorch-lightning==1.5.0<br/>torchvision==0.15.1<br/>transformers==4.49.0<br/>petastorm==0.12.1<br/>protobuf==5.29.4"]
    end
    
    subgraph "Test Execution"
        NotebookUpload["Upload Notebooks to Workspace"]
        JobSubmission["Submit Run via REST API"]
        Monitor["Monitor Job Status<br/>TimeoutInMillis: 50min"]
        Cleanup["Permanent Delete Cluster"]
    end
    
    CPUCluster --> MavenLibs
    GPUCluster --> MavenLibs
    GPUCluster --> PipPackages
    RapidsCluster --> PipPackages
    
    MavenLibs --> NotebookUpload
    PipPackages --> NotebookUpload
    NotebookUpload --> JobSubmission
    JobSubmission --> Monitor
    Monitor --> Cleanup
```

### Test Classes

| Test Class | Cluster Type | Notebooks | Concurrency |
|------------|--------------|-----------|-------------|
| `DatabricksCPUTests` | CPU Pool (5 workers) | `CPUNotebooks` (excludes GPU/Fine-tune) | 5 parallel |
| `DatabricksGPUTests` | GPU Pool (2 workers) | `GPUNotebooks` (Fine-tune, Phi Model) | 1 sequential |
| `DatabricksRapidsTests` | GPU Pool (1 worker) + Init Scripts | `RapidsNotebooks` (contains "GPU") | 4 parallel |

**Sources**: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:10-25](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:8-19](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:8-19]()

### GPU Libraries Configuration

The GPU test clusters install specific library versions:

```scala
val GPULibraries: String = List(
  Map("maven" -> Map("coordinates" -> PackageMavenCoordinate, "repo" -> PackageRepository)),
  Map("pypi" -> Map("package" -> "pytorch-lightning==1.5.0")),
  Map("pypi" -> Map("package" -> "torchvision==0.15.1")),
  Map("pypi" -> Map("package" -> "transformers==4.49.0")),
  Map("pypi" -> Map("package" -> "jinja2==3.1.6")),
  Map("pypi" -> Map("package" -> "petastorm==0.12.1")),
  Map("pypi" -> Map("package" -> "protobuf==5.29.4")),
  Map("pypi" -> Map("package" -> "accelerate==0.26.0"))
).toJson.compactPrint
```

**Sources**: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:84-93]()

### Notebook Filtering Logic

The test framework categorizes notebooks based on naming patterns:

```scala
val CPUNotebooks: Seq[File] = ParallelizableNotebooks
  .filterNot(_.getAbsolutePath.contains("Fine-tune"))
  .filterNot(_.getAbsolutePath.contains("GPU"))
  .filterNot(_.getAbsolutePath.contains("Phi Model"))
  .filterNot(_.getAbsolutePath.contains("Language Model"))
  // ... additional exclusions

val GPUNotebooks: Seq[File] = ParallelizableNotebooks.filter { file =>
  file.getAbsolutePath.contains("Fine-tune") || file.getAbsolutePath.contains("Phi Model")
}

val RapidsNotebooks: Seq[File] = ParallelizableNotebooks.filter(
  _.getAbsolutePath.contains("GPU")
)
```

**Sources**: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:108-124]()

### Test Execution Flow

```mermaid
sequenceDiagram
    participant Test as Test Suite
    participant DB as Databricks API
    participant Cluster as Spark Cluster
    participant Notebook as Jupyter Notebook
    
    Test->>DB: createClusterInPool(clusterName, runtime, poolId)
    DB-->>Test: clusterId
    
    Test->>DB: installLibraries(clusterId, libraries)
    Test->>DB: isClusterActive(clusterId)?
    DB-->>Test: "RUNNING"
    
    Test->>DB: areLibrariesInstalled(clusterId)?
    DB-->>Test: All "INSTALLED"
    
    loop For each notebook
        Test->>DB: uploadNotebook(file, destination)
        Test->>DB: submitRun(clusterId, notebookPath)
        DB-->>Test: runId
        
        loop Until completion or timeout
            Test->>DB: getRunStatuses(runId)
            DB-->>Test: life_cycle_state, result_state
        end
    end
    
    Test->>DB: permanentDeleteCluster(clusterId)
```

**Sources**: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:436-481]()

### Retry and Error Handling

The test framework includes retry logic for library installation and cluster readiness:

```scala
tryWithRetries(Seq.fill(60 * 20)(1000).toArray) { () =>
  assert(isClusterActive(clusterId))
}

installLibraries(clusterId, libraries)
tryWithRetries(Seq.fill(60 * 6)(1000).toArray) { () =>
  assert(areLibrariesInstalled(clusterId))
}
```

Library installation failures are detected and surfaced:

```scala
if (libraryStatuses.exists(_.select[String]("status") == "FAILED")) {
  val error = libraryStatuses.filter(_.select[String]("status") == "FAILED").toJson.compactPrint
  throw new RuntimeException(s"Library Installation Failure: $error")
}
```

**Sources**: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:442-452](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:297-306]()

## Docker Environment Support

### Container Images

SynapseML provides Docker images for local development and testing:

| Image Type | Base | Components |
|------------|------|------------|
| `demo` | Ubuntu 20.04 | Spark 3.5.0, Jupyter, SynapseML, OpenMPI |
| `minimal` | Ubuntu 20.04 | Spark 3.5.0, Jupyter, minimal dependencies |
| `developer` | Ubuntu 20.04 | Full development environment with all tools |

**Sources**: [tools/docker/demo/Dockerfile:1-71](), [tools/docker/minimal/Dockerfile:1-52]()

### Spark Configuration for Deep Learning

The demo container includes an initialization script that configures Spark for SynapseML:

```python
synapseMLConf = pyspark.SparkConf().setAll([
    ("spark.hadoop.fs.wasb.impl", "org.apache.hadoop.fs.azure.NativeAzureFileSystem"),
    ("spark.jars.packages", 
     "com.microsoft.azure:synapseml_2.12:" + os.getenv("SYNAPSEML_VERSION", "1.1.0") +
     ",org.apache.hadoop:hadoop-azure:2.7.0,org.apache.hadoop:hadoop-common:2.7.0"),
    ("spark.jars.repositories", "https://mmlspark.azureedge.net/maven,...")
])

spark = (
    SparkSession.builder.master("local[*]")
    .appName("SynapseML Docker App")
    .config(conf=synapseMLConf)
    .getOrCreate()
)
```

This configuration:
- Enables Azure Blob Storage access
- Downloads SynapseML JARs from Maven repository
- Configures Hadoop Azure dependencies

**Sources**: [tools/docker/demo/init_notebook.py:1-47]()

### Container Usage

```bash
# Build image
docker build . -f tools/docker/demo/Dockerfile -t synapseml

# Run with Jupyter and Spark UI exposed
docker run -p4040:4040 -p8888:8888 -ti synapseml jupyter notebook ./
```

Access points:
- Jupyter Notebook: `http://localhost:8888`
- Spark UI: `http://localhost:4040`

**Sources**: [tools/docker/demo/README.md:1-30]()

## Custom Data Sources for Deep Learning

### Patched Image File Format

SynapseML includes a custom Spark data source for reading images with retry logic to handle JVM multi-threading bugs:

```scala
class PatchedImageFileFormat extends ImageFileFormat {
  override def shortName(): String = "patchedImage"
  
  @annotation.tailrec
  private def catchFlakiness[T](times: Int)(f: => Option[T]): Option[T] = {
    Try { f } match {
      case Success(x) => x
      case Failure(exception: NullPointerException) if times >= 1 =>
        logWarning("caught null pointer exception due to jvm bug", exception)
        catchFlakiness(times - 1)(f)
      case _ => None
    }
  }
  
  // Retry image decoding up to 5 times
  val resultOpt = catchFlakiness(5)(
    ImageSchema.decode(origin.toString(), bytes)
  )
}
```

This addresses flakiness in `javax.imageio.ImageIO` when called from multiple threads simultaneously.

**Sources**: [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala:26-129]()

### Binary File Format with Zip Support

The `BinaryFileFormat` enables reading binary files and supports automatic extraction of zip archives:

```scala
class BinaryRecordReader(val subsample: Double, val inspectZip: Boolean, val seed: Long) {
  override def initialize(inputSplit: InputSplit, context: TaskAttemptContext): Unit = {
    // ...
    if (inspectZip && FilenameUtils.getExtension(filename) == "zip") {
      zipIterator = new ZipIterator(inputStream, filename, rng, subsample)
    }
  }
  
  override def nextKeyValue(): Boolean = {
    if (zipIterator != null) {
      if (zipIterator.hasNext) {
        val (fn, barr) = zipIterator.next
        filename = fn
        recordValue = barr
        true
      } else false
    } else {
      // Read entire file as bytes
      recordValue = IOUtils.toByteArray(inputStream)
      true
    }
  }
}
```

This is particularly useful for datasets distributed as zip archives containing multiple files.

**Sources**: [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala:33-108]()

## Version Compatibility Matrix

| Component | Version | Notes |
|-----------|---------|-------|
| PyTorch Lightning | 1.5.0 | Fixed version for compatibility |
| TorchVision | 0.15.1 | Requires >= 0.14.1 |
| Transformers | 4.49.0 | Exact version required |
| Horovod | 0.28.1 | Built with NCCL for GPU |
| Petastorm | >= 0.12.1 | Spark DataFrame to PyTorch conversion |
| Protobuf | 5.29.4 | Required by Petastorm |
| Accelerate | 0.26.0 | HuggingFace optimization library |
| CUDA | 11.0 | For GPU training |
| NCCL | 2.10.3 | GPU collective operations |

**Sources**: [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:16-24](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:19-27](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:84-93](), [deep-learning/src/main/python/horovod_installation.sh:9-14]()

---

# Page: LightGBM Integration

# LightGBM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



This page documents the integration of Microsoft's LightGBM (Light Gradient Boosting Machine) framework with Apache Spark in the SynapseML library. LightGBM is a high-performance gradient boosting framework that uses tree-based learning algorithms and is designed for distributed training.

## Overview

SynapseML provides a comprehensive integration with LightGBM, enabling efficient training of gradient boosting models on distributed Spark datasets. The integration offers three main model types:

- Classification (binary and multiclass)
- Regression 
- Ranking

The implementation bridges the gap between Spark's distributed computing capabilities and LightGBM's efficient gradient boosting algorithm by handling data conversion, distributed training coordination, and seamless integration with Spark ML pipelines.

```mermaid
graph TD
    subgraph "SynapseML LightGBM Integration"
        Spark["Apache Spark"] --> SynapseMLCore["SynapseML Core"]
        SynapseMLCore --> LightGBMIntegration["LightGBM Integration"]
        
        LightGBMIntegration --> LightGBMNative["Native LightGBM Library"]
        LightGBMIntegration --> Models["ML Models"]
        
        Models --> Classifier["LightGBMClassifier"]
        Models --> Regressor["LightGBMRegressor"]
        Models --> Ranker["LightGBMRanker"]
        
        LightGBMIntegration --> DataHandling["Dataset Handling"]
        LightGBMIntegration --> Training["Training Infrastructure"]
        
        DataHandling --> DataPrep["Data Preparation"]
        DataHandling --> DataTransfer["Data Transfer Modes"]
        
        Training --> DistributedTraining["Distributed Training"]
        Training --> EarlyStop["Early Stopping"]
        Training --> Performance["Performance Monitoring"]
    end
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala]()

## Architecture

The LightGBM integration in SynapseML follows a layered architecture that connects Spark's distributed computing with LightGBM's native implementation:

```mermaid
graph TD
    subgraph "User API Layer"
        Classifier["LightGBMClassifier"]
        Regressor["LightGBMRegressor"] 
        Ranker["LightGBMRanker"]
    end

    subgraph "Base Layer"
        Base["LightGBMBase"]
        Params["LightGBMParams"]
    end

    subgraph "Model Layer"
        ClassifierModel["LightGBMClassificationModel"]
        RegressorModel["LightGBMRegressionModel"]
        RankerModel["LightGBMRankerModel"]
        ModelParams["LightGBMModelParams"]
        ModelMethods["LightGBMModelMethods"]
    end

    subgraph "Native Integration Layer"
        Booster["LightGBMBooster"]
        Dataset["LightGBMDataset"]
        NativeUtils["SwigUtils/NativeLoader"]
    end
    
    Classifier --> Base
    Regressor --> Base 
    Ranker --> Base
    
    Classifier --> ClassifierModel
    Regressor --> RegressorModel
    Ranker --> RankerModel
    
    ClassifierModel --> ModelParams
    RegressorModel --> ModelParams
    RankerModel --> ModelParams
    
    ClassifierModel --> ModelMethods
    RegressorModel --> ModelMethods
    RankerModel --> ModelMethods
    
    Base --> Booster
    ModelParams --> Booster
    
    Base --> Dataset
    Booster --> NativeUtils
    Dataset --> NativeUtils
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/booster/LightGBMBooster.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMModelMethods.scala]()

## Training Process

The training process for LightGBM models in SynapseML involves several stages to handle distributed training efficiently:

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant Estimator as "LightGBM Estimator"
    participant Base as "LightGBM Base"
    participant Executor as "Spark Executors"
    participant Native as "Native LightGBM"
    
    User->>Estimator: fit(dataset)
    Estimator->>Base: train(dataset)
    
    Base->>Base: prepareDataframe
    Base->>Base: determineNumTasks
    
    Base->>Executor: executeTraining
    
    Executor->>Executor: initializeNativeLibrary
    Executor->>Executor: createTrainingContext
    
    Executor->>Native: map partitions to training tasks
    
    par Executor Tasks
        Native->>Native: Dataset creation
        Native->>Native: Booster creation
        Native->>Native: Training iterations
    end
    
    Native-->>Executor: Return booster
    Executor-->>Base: Return model
    Base-->>Estimator: Return trained model
    Estimator-->>User: Return trained model
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:36-64]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:396-447]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:569-604]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/TrainUtils.scala]()

### Training Data Flow

The following diagram illustrates how data flows through the system during training:

```mermaid
graph TD
    subgraph "Data Preparation"
        DF["Spark DataFrame"] --> PrepDF["Prepared DataFrame"]
        PrepDF --> DataPartitions["Data Partitions"]
    end
    
    subgraph "Per Executor Processing"
        DataPartitions --> ColumnStats["Column Statistics"]
        DataPartitions --> RowStats["Row Statistics"]
        
        ColumnStats --> Features["Feature Data"]
        RowStats --> RefData["Reference Dataset"]
        
        Features --> SparseMat["Sparse Matrix Format"]
        Features --> DenseMat["Dense Matrix Format"]
        
        RefData --> LGBMDataset["LightGBM Dataset"]
        SparseMat --> LGBMDataset
        DenseMat --> LGBMDataset
    end
    
    subgraph "Distributed Training"
        LGBMDataset --> Network["Network Communication"]
        Network --> Booster["LightGBM Booster"]
        
        Booster --> Training["Training Iterations"]
        Training --> EarlyStopping["Early Stopping Check"]
        
        EarlyStopping --> TrainedBooster["Trained Booster"]
    end
    
    TrainedBooster --> ModelConversion["Convert to ML Model"]
    ModelConversion --> FinalModel["Final LightGBM Model"]
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMBase.scala:109-144]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/dataset/DatasetAggregator.scala]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/TrainUtils.scala:98-135]()

## Model Types

### LightGBM Classifier

The `LightGBMClassifier` implements binary and multiclass classification models. It extends Spark's `ProbabilisticClassifier` and supports both raw predictions and probability outputs.

Key features:
- Binary classification (default)
- Multiclass classification
- Class probability estimation
- Handling of unbalanced datasets
- Support for feature importance and SHAP values

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala]()

### LightGBM Regressor

The `LightGBMRegressor` implements regression models with various loss functions. It extends Spark's `BaseRegressor`.

Key features:
- Multiple objective functions (L1, L2, Huber, Quantile, etc.)
- Alpha parameter for Huber loss and Quantile regression
- Tweedie regression support
- Feature importance and SHAP values

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala]()

### LightGBM Ranker

The `LightGBMRanker` implements learning-to-rank models. It extends Spark's `Ranker`.

Key features:
- Support for group-based ranking
- NDCG and MAP optimization
- Position-based evaluation
- Feature importance and SHAP values

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala]()

## Parameters and Configuration

The LightGBM integration offers a wide range of parameters for customizing model behavior. These parameters are organized into several categories:

### General Parameters

These parameters control the general behavior of LightGBM models.

| Parameter | Description | Default |
|-----------|-------------|---------|
| numIterations | Number of boosting iterations | 100 |
| learningRate | Learning rate or shrinkage rate | 0.1 |
| numLeaves | Maximum number of leaves in each tree | 31 |
| maxDepth | Maximum depth of each tree | -1 (no limit) |
| objective | Learning objective | Classification: "binary", Regression: "regression" |
| metric | Evaluation metric | "" (uses default for objective) |
| earlyStoppingRound | Early stopping round | 0 (disabled) |
| parallelism | Tree learner parallelism | "data_parallel" |

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:505-537]()

### Execution Parameters

These parameters control how the model executes in the distributed environment.

| Parameter | Description | Default |
|-----------|-------------|---------|
| dataTransferMode | How data is transferred to LightGBM | "streaming" |
| useSingleDatasetMode | Use single dataset per executor | true |
| numTasks | Number of tasks for distributed training | 0 (auto) |
| numThreads | Number of threads for LightGBM | 0 (auto) |
| useBarrierExecutionMode | Use barrier execution mode | false |
| timeout | Timeout in seconds | 1200 |

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:16-158]()

### Dataset Parameters

These parameters control how datasets are handled.

| Parameter | Description | Default |
|-----------|-------------|---------|
| maxBin | Maximum number of bins for features | 255 |
| binSampleCount | Number of samples for bin construction | 200000 |
| minDataInLeaf | Minimum number of data in one leaf | 20 |
| categoricalSlotIndexes | Indexes of categorical features | [] |
| categoricalSlotNames | Names of categorical features | [] |

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:231-296]()

### Model-Specific Parameters

Each model type has additional parameters:

#### Classification
- `isUnbalance`: Handle unbalanced datasets (boolean)

#### Regression
- `alpha`: Parameter for Huber loss and Quantile regression
- `tweedieVariancePower`: Control variance of Tweedie distribution

#### Ranking
- `maxPosition`: Position to optimize NDCG at
- `evalAt`: Positions for NDCG and MAP evaluation
- `labelGain`: Relevance gain for each label

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:37-41]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:49-58]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:36-49]()

## Feature Importance and Interpretability

LightGBM models in SynapseML provide built-in support for feature importance and SHAP (SHapley Additive exPlanations) values for model interpretability.

### Feature Importance

Feature importance can be obtained using the `getFeatureImportances` method with two types:
- `split`: Number of times a feature is used in a model
- `gain`: Total gains of splits that use the feature

```mermaid
graph TD
    Model["LightGBMModel"] -->|"getFeatureImportances('split')"| SplitImportance["Split Importance"]
    Model -->|"getFeatureImportances('gain')"| GainImportance["Gain Importance"]
    
    SplitImportance --> UsageAnalysis["Feature Usage Analysis"]
    GainImportance --> ImpactAnalysis["Feature Impact Analysis"]
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMModelMethods.scala:14-21]()

### SHAP Values

SHAP values can be calculated for individual predictions using:
- During prediction with `setFeaturesShapCol`
- Programmatically with `getFeatureShaps` or `featuresShap`

SHAP values explain how each feature contributes to pushing the prediction higher or lower from the base (average) value.

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMModelMethods.scala:22-50]()
- [lightgbm/src/main/python/synapse/ml/lightgbm/mixin.py:29-49]()

## Performance Optimizations

SynapseML's LightGBM integration includes several optimization strategies to improve performance:

### Data Transfer Modes

Two primary data transfer modes are available:
- `streaming`: Stream data to LightGBM (default, recommended for large datasets)
- `bulk`: Legacy mode for data transfer

### Matrix Representation

Data can be represented in different formats:
- `auto`: Automatically determine based on data sparsity
- `sparse`: Use sparse matrix format (CSR)
- `dense`: Use dense matrix format

### Dataset Mode

- `useSingleDatasetMode`: When enabled (default), creates a single native dataset per executor to reduce memory and communication overhead

### Parallelism and Threading

- `numThreads`: Controls the number of threads used by LightGBM
- `parallelism`: Controls the tree learning algorithm parallelism ("data_parallel" or "voting_parallel")

```mermaid
graph TD
    Performance["Performance Optimizations"] --> DataTransfer["Data Transfer Mode"]
    Performance --> MatrixFormat["Matrix Format"]
    Performance --> ExecutorMode["Executor Mode"]
    Performance --> Threading["Threading Model"]
    
    DataTransfer --> Streaming["streaming"]
    DataTransfer --> Bulk["bulk"]
    
    MatrixFormat --> Auto["auto"]
    MatrixFormat --> Sparse["sparse"]
    MatrixFormat --> Dense["dense"]
    
    ExecutorMode --> SingleDS["Single Dataset Mode"]
    ExecutorMode --> MultiDS["Multiple Dataset Mode"]
    
    Threading --> ThreadPool["Thread Pool Size"]
    Threading --> TreeParallelism["Tree Parallelism Type"]
```

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:86-110]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/params/LightGBMParams.scala:139-158]()

## Example Usage

To use LightGBM models in SynapseML, you create an estimator, configure it with parameters, and fit it to your data. The resulting model can then be used for predictions.

Here's a conceptual flow for using LightGBM in SynapseML:

```mermaid
graph LR
    Data["Spark DataFrame"] --> Prep["Data Preparation"]
    Prep --> Features["Feature Vector"]
    
    Features --> Estimator["LightGBM Estimator"]
    Estimator --> |"fit()"| Model["LightGBM Model"]
    
    NewData["New Data"] --> Model
    Model --> |"transform()"| Predictions["Predictions"]
    
    Model --> |"getFeatureImportances()"| Importances["Feature Importances"]
    Model --> |"getFeatureShaps()"| SHAP["SHAP Values"]
```

LightGBM models can be used like any other Spark ML model in a Pipeline, making them easy to integrate into existing workflows.

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:26-89]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:39-92]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:26-120]()

## Saving and Loading Models

LightGBM models in SynapseML can be saved and loaded in two ways:

1. **Spark ML Model Format**: Standard Spark ML model persistence
   - `model.write().overwrite().save(path)`
   - `LightGBMClassificationModel.load(path)`

2. **Native LightGBM Format**: Save just the LightGBM booster
   - `model.saveNativeModel(path)`
   - `LightGBMClassificationModel.loadNativeModelFromFile(path)`
   - `LightGBMClassificationModel.loadNativeModelFromString(modelString)`

The native format allows for interoperability with other LightGBM implementations.

Sources:
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMClassifier.scala:196-211]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRegressor.scala:136-150]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMRanker.scala:167-182]()
- [lightgbm/src/main/scala/com/microsoft/azure/synapse/ml/lightgbm/LightGBMModelMethods.scala:95-109]()

## Performance Measurement

SynapseML's LightGBM integration includes built-in performance measurement capabilities to help understand and optimize training time:

- Total time measurement
- Component-level timing:
  - Column statistics
  - Row statistics
  - Training iterations
  - Data preparation
  - Network communication
  - Dataset creation

These measurements can help identify bottlenecks in the training process and guide optimization efforts.

Sources:
- [lightgbm/src/test/scala/com/microsoft/azure/synapse/ml/lightgbm/split1/VerifyLightGBMCommon.scala:147-200]()

## Python API

SynapseML provides a Python API for LightGBM integration that mirrors the Scala API. It includes additional methods for model interaction:

- `saveNativeModel`: Save the booster in string format
- `getNativeModel`: Get the native model serialized representation
- `getFeatureImportances`: Get feature importances
- `getFeatureShaps`: Get SHAP values for a feature vector
- `getBoosterBestIteration`: Get the best iteration from early stopping
- `setPredictDisableShapeCheck`: Control shape checking during prediction

Sources:
- [lightgbm/src/main/python/synapse/ml/lightgbm/mixin.py]()

---

# Page: Vowpal Wabbit Integration

# Vowpal Wabbit Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



This page documents the integration of Vowpal Wabbit (VW) within SynapseML. Vowpal Wabbit is a fast, efficient machine learning library that excels in online learning, sparse data, and large-scale problems. The SynapseML integration wraps Vowpal Wabbit's functionality and exposes it as Spark ML pipeline stages, enabling the use of Vowpal Wabbit's algorithms in distributed big data scenarios.

Sources: [README.md:47-53](), [README.md:306-307]()

## Architecture Overview

The Vowpal Wabbit integration in SynapseML is designed to bridge Spark's distributed computing capabilities with Vowpal Wabbit's efficient learning algorithms. The integration follows a layered architecture that exposes Vowpal Wabbit functionality as standard Spark ML components while handling the complexities of distributed execution and integration with the broader SynapseML ecosystem.

```mermaid
flowchart TD
    subgraph "SynapseML Vowpal Wabbit Integration"
        Base["VowpalWabbitBaseSpark
        VowpalWabbitBaseModel"]
        subgraph "Core Components"
            Classifier["VowpalWabbitClassifier
            VowpalWabbitClassificationModel"]
            Regressor["VowpalWabbitRegressor
            VowpalWabbitRegressionModel"]
            ContextualBandit["VowpalWabbitContextualBandit
            VowpalWabbitContextualBanditModel"]
            Generic["VowpalWabbitGeneric
            VowpalWabbitGenericModel"]
        end
        subgraph "Utility Components"
            Featurizer["VowpalWabbitFeaturizer"]
            VectorZipper["VectorZipper"]
            CSETransformer["VowpalWabbitCSETransformer"]
            DSJsonTransformer["VowpalWabbitDSJsonTransformer"]
        end
        subgraph "Native VW"
            VWNative["org.vowpalwabbit.spark.*"]
        end
        
        Base --> Classifier
        Base --> Regressor
        Base --> ContextualBandit
        Base --> Generic
        
        Classifier --> VWNative
        Regressor --> VWNative
        ContextualBandit --> VWNative
        Generic --> VWNative
        Featurizer --- Core Components
    end
    
    SparkML["Apache Spark ML APIs"] --> Base
    SynapseMLLogging["SynapseML Logging System"] --> Base
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitGeneric.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala]()

## Core Components

The Vowpal Wabbit integration provides several core components that extend Spark ML's basic abstractions for machine learning. Each component is designed to support specific learning tasks while maintaining compatibility with Spark ML pipelines.

```mermaid
classDiagram
    class SparkMLInterfaces {
        Predictor
        ProbabilisticClassifier
        RegressionModel
        Estimator
        Model
    }
    
    class VowpalWabbitBaseSpark {
        +getHashSeed()
        +getNumBits()
        +getPassThroughArgs()
        +trainInternal()
    }
    
    class VowpalWabbitBaseModelSpark {
        +vw: VowpalWabbitNative
        +transformImplInternal()
        +predict()
    }
    
    class VowpalWabbitClassifier {
        +setLabelConversion()
        +setNumClasses()
        +train()
    }
    
    class VowpalWabbitRegressor {
        +train()
    }
    
    class VowpalWabbitContextualBandit {
        +setSharedCol()
        +setAdditionalSharedFeatures()
        +setProbabilityCol()
        +setChosenActionCol()
        +setEpsilon()
        +train()
    }
    
    class VowpalWabbitGeneric {
        +setInputCol()
        +train()
        +fit()
    }
    
    SparkMLInterfaces <|-- VowpalWabbitClassifier
    SparkMLInterfaces <|-- VowpalWabbitRegressor
    SparkMLInterfaces <|-- VowpalWabbitContextualBandit
    SparkMLInterfaces <|-- VowpalWabbitGeneric
    
    VowpalWabbitBaseSpark <|-- VowpalWabbitClassifier
    VowpalWabbitBaseSpark <|-- VowpalWabbitRegressor
    VowpalWabbitBaseSpark <|-- VowpalWabbitContextualBandit
    VowpalWabbitBaseSpark <|-- VowpalWabbitGeneric
    
    VowpalWabbitBaseModelSpark <|-- VowpalWabbitClassificationModel
    VowpalWabbitBaseModelSpark <|-- VowpalWabbitRegressionModel
    VowpalWabbitBaseModelSpark <|-- VowpalWabbitContextualBanditModel
    VowpalWabbitBaseModelSpark <|-- VowpalWabbitGenericModel
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala:25-87](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:19-41](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:105-170](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitGeneric.scala:19-81]()

### Classification and Regression

The Vowpal Wabbit integration offers two standard supervised learning components:

1. **VowpalWabbitClassifier**: Implements classification algorithms for both binary and multi-class classification tasks.
   - Supports label conversion between Spark ML style (0/1) and VW style (-1/1)
   - Handles multi-class classification through the `numClasses` parameter
   - Produces probability distributions and raw predictions following Spark ML conventions

2. **VowpalWabbitRegressor**: Implements regression algorithms for predicting continuous values.
   - Follows the standard Spark ML regressor interface
   - Leverages VW's optimization algorithms for efficient regression

Both components maintain compatibility with Spark ML pipelines and can be used interchangeably with other Spark ML estimators and transformers.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala]()

### Contextual Bandit

The `VowpalWabbitContextualBandit` component implements contextual bandit algorithms, which are particularly useful for personalization, recommendation, and online learning scenarios. This component:

- Supports exploration strategies (e.g., epsilon-greedy via the `epsilon` parameter)
- Handles shared features across actions
- Processes contextual data to make action selections
- Tracks important metrics like IPS (Inverse Propensity Scoring) and SNIPS (Stabilized Normalized IPS)

The contextual bandit implementation follows Vowpal Wabbit's action-dependent features approach (`cb_explore_adf`), which allows for different feature sets per action.

```mermaid
sequenceDiagram
    participant Client
    participant VWContextualBandit as "VowpalWabbitContextualBandit"
    participant VWNative as "VowpalWabbitNative"
    participant Metrics as "ContextualBanditMetrics"
    
    Client->>VWContextualBandit: fit(dataset)
    VWContextualBandit->>VWContextualBandit: transformSchema()
    VWContextualBandit->>VWContextualBandit: trainFromRows()
    
    loop For each row in dataset
        VWContextualBandit->>VWNative: prepareMultilineExample()
        VWContextualBandit->>VWNative: learn(examples)
        VWNative-->>VWContextualBandit: prediction
        VWContextualBandit->>Metrics: addExample(loggedProb, cost, evalProb)
    end
    
    VWContextualBandit->>Client: VowpalWabbitContextualBanditModel
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:105-308]()

### Generic Interface

The `VowpalWabbitGeneric` component provides a lower-level interface that accepts VW-style examples (e.g., "0 |a b c") directly. This is useful for:

- Users familiar with Vowpal Wabbit's native format
- Legacy applications that already generate VW-formatted data
- Advanced use cases that require fine-grained control over the input format

This component maintains the same pipeline compatibility as the other Vowpal Wabbit components while offering more flexibility in input formatting.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitGeneric.scala:19-132]()

## Utility Components

The Vowpal Wabbit integration includes several utility components that enhance the core functionality:

### Featurization

The `VowpalWabbitFeaturizer` component implements Vowpal Wabbit's feature hashing technique for Spark ML pipelines. This component:

- Converts various Spark SQL data types (strings, numerics, arrays, etc.) into hashed feature vectors
- Supports namespace prefixing and feature ordering
- Offers configurable hash sizes and collision handling
- Enables efficient handling of high-cardinality categorical features

The featurizer uses the same hashing algorithm as native VW, ensuring compatibility between the Spark and native implementations.

```mermaid
flowchart TD
    subgraph "VowpalWabbitFeaturizer"
        Input["Input Data
        (Various Types)"]
        TypeSpecificFeaturizers["Type-Specific Featurizers"]
        Hashing["Feature Hashing"]
        Output["Sparse Vector Output"]
        
        Input --> TypeSpecificFeaturizers
        TypeSpecificFeaturizers --> Hashing
        Hashing --> Output
        
        subgraph "Available Featurizers"
            NumericFeaturizer["NumericFeaturizer"]
            StringFeaturizer["StringFeaturizer"]
            StringSplitFeaturizer["StringSplitFeaturizer"]
            VectorFeaturizer["VectorFeaturizer"]
            MapFeaturizer["MapFeaturizer"]
            StructFeaturizer["StructFeaturizer"]
            SeqFeaturizer["SeqFeaturizer"]
        end
    end
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala:25-231]()

### Vector Zipper

The `VectorZipper` utility combines multiple input columns into a sequence in the output column. This is particularly useful for preparing data for multi-line formats required by some Vowpal Wabbit algorithms, such as contextual bandits with action-dependent features.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala:21-42]()

### Evaluation and Transformation Utilities

Two additional components facilitate working with Vowpal Wabbit in real-world scenarios:

1. **VowpalWabbitCSETransformer**: Emits continuous success experimentation metrics for contextual bandit predictions. It calculates important offline policy evaluation metrics like SNIPS, IPS, and Cressie-Read interval estimates.

2. **VowpalWabbitDSJsonTransformer**: Transforms Decision Service JSON data into a format suitable for Vowpal Wabbit processing, extracting rewards, probabilities, and action indices.

These components enable more sophisticated workflows like offline policy evaluation and integration with existing decision service infrastructures.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala]()

## Usage Patterns

The Vowpal Wabbit components in SynapseML follow standard Spark ML usage patterns. Here's an overview of common usage patterns:

### Classification Example

```
// Create a VowpalWabbitClassifier
val classifier = new VowpalWabbitClassifier()
  .setFeaturesCol("features")
  .setLabelCol("label")
  .setPredictionCol("prediction")
  .setPassThroughArgs("--loss_function logistic")

// Train the model
val model = classifier.fit(trainingData)

// Make predictions
val predictions = model.transform(testData)
```

### Contextual Bandit Example

```
// Create a VowpalWabbitContextualBandit
val bandit = new VowpalWabbitContextualBandit()
  .setFeaturesCol("actionFeatures")
  .setSharedCol("sharedFeatures")
  .setChosenActionCol("action")
  .setProbabilityCol("probability")
  .setLabelCol("cost")
  .setPassThroughArgs("--cb_explore_adf --epsilon 0.1")

// Train the model
val model = bandit.fit(trainingData)

// Get action probabilities for new contexts
val predictions = model.transform(newContexts)
```

### Using the Featurizer

```
// Create a VowpalWabbitFeaturizer
val featurizer = new VowpalWabbitFeaturizer()
  .setInputCols(Array("userFeatures", "itemFeatures"))
  .setOutputCol("features")
  .setNumBits(18)
  .setStringSplitInputCols(Array("userFeatures"))

// Apply featurization
val featurizedData = featurizer.transform(rawData)
```

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala]()

## Integration with SynapseML

The Vowpal Wabbit integration is fully integrated with the broader SynapseML ecosystem. All Vowpal Wabbit components:

1. **Implement Logging**: Use SynapseML's unified logging system to track usage, errors, and performance metrics.

2. **Support Cross-Language APIs**: Available in Python, Scala, and R through SynapseML's automatic binding generation.

3. **Provide Deployment Options**: Can be deployed in various environments supported by SynapseML, including Azure Synapse, Databricks, and standalone Spark clusters.

4. **Integrate with Pipelines**: Work seamlessly with other SynapseML and Spark ML components in pipeline scenarios.

```mermaid
flowchart LR
    subgraph "Platform Integrations"
        AzureSynapse["Azure Synapse"]
        MSFabric["Microsoft Fabric"]
        Databricks["Databricks"]
        Standalone["Standalone Spark"]
    end
    
    subgraph "Language Bindings"
        PySpark["PySpark (Python)"]
        ScalaAPI["Scala API"]
        RAPI["R API"]
    end
    
    subgraph "VW Components"
        VWClassifier["VowpalWabbitClassifier"]
        VWRegressor["VowpalWabbitRegressor"]
        VWContextualBandit["VowpalWabbitContextualBandit"]
        VWFeaturizer["VowpalWabbitFeaturizer"]
    end
    
    VW["Vowpal Wabbit Native"] --> VW Components
    
    VW Components --> SynapseMLLogging["SynapseML Logging"]
    
    VW Components --> Language Bindings
    Language Bindings --> Platform Integrations
```

Sources: [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](), [README.md:70-85]()

## Performance Considerations

When using Vowpal Wabbit within SynapseML, consider the following performance factors:

1. **Hash Size**: The `numBits` parameter controls the size of the feature hash space. Larger values reduce collisions but increase memory usage.

2. **Example Format**: For large datasets, using the VowpalWabbitFeaturizer can be more efficient than string-based example formats.

3. **Parallel Processing**: The contextual bandit implementation supports parallel model fitting via the `parallelism` parameter.

4. **Memory Management**: The integration manages memory efficiently by reusing example objects through the `ExampleStack` class.

5. **Native Performance**: Vowpal Wabbit's core algorithms run as native code, providing high performance regardless of the Spark integration layer.

Sources: [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:27-51](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala:35-46]()

## Summary

The Vowpal Wabbit integration in SynapseML provides a comprehensive set of components for leveraging Vowpal Wabbit's powerful learning algorithms within Spark ML pipelines. From standard classification and regression to advanced contextual bandit algorithms, these components combine the efficiency of Vowpal Wabbit with the scalability of Apache Spark. 

The integration is designed to be flexible, supporting various data formats and learning scenarios while maintaining compatibility with the broader SynapseML ecosystem. This makes it a valuable tool for large-scale machine learning applications, particularly those involving online learning, personalization, and sparse data processing.

Sources: [README.md:47-53](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw]()

---

# Page: Documentation System

# Documentation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb](docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb)
- [website/docusaurus.config.js](website/docusaurus.config.js)
- [website/package.json](website/package.json)
- [website/src/theme/CodeSnippet/index.js](website/src/theme/CodeSnippet/index.js)
- [website/src/theme/NotFound/index.js](website/src/theme/NotFound/index.js)
- [website/src/theme/SampleSnippet/index.js](website/src/theme/SampleSnippet/index.js)
- [website/yarn.lock](website/yarn.lock)

</details>



## Purpose and Scope

The Documentation System encompasses the infrastructure, build processes, and deployment mechanisms that generate and serve the SynapseML public-facing documentation website. This includes the Docusaurus-based site, API documentation generation, notebook examples, and search integration. For information about testing documentation quality, see [Testing Infrastructure](#4). For CI/CD pipeline integration, see [CI/CD Pipeline](#3.1).

## Overview

The documentation system transforms multiple content sources (Jupyter notebooks, markdown files, source code) into a unified, versioned website hosted on GitHub Pages at `https://microsoft.github.io/SynapseML/`. It uses Docusaurus 2.4.1 as the static site generator, Algolia for search, and Azure Blob Storage for hosting API documentation artifacts.

**Key Characteristics:**
- Multi-version support (0.9.4, 0.10.0, 1.1.0)
- Internationalization ready with locale dropdown
- Dark mode default theme
- Math rendering via KaTeX
- 160+ URL redirects for backward compatibility
- Google Analytics integration (tracking ID: G-RWPE0183E8)

Sources: [website/docusaurus.config.js:1-480](), [website/package.json:1-65]()

## Content Sources and Flow

```mermaid
graph TB
    subgraph "Content Sources"
        Notebooks["Jupyter Notebooks<br/>docs/**/*.ipynb"]
        Markdown["Markdown Files<br/>docs/**/*.md"]
        ScalaSrc["Scala Source<br/>core/src/main/scala/**/*.scala"]
        PythonSrc["Python Source<br/>core/src/main/python/**/*.py"]
    end
    
    subgraph "Build Tools"
        Docusaurus["Docusaurus 2.4.1<br/>docusaurus build"]
        Sphinx["Sphinx<br/>Python API Docs"]
        ScalaUnidoc["ScalaUnidoc<br/>Scala API Docs"]
        NotebookConv["Notebook Processing<br/>ipynb → md/py"]
    end
    
    subgraph "Generated Artifacts"
        StaticSite["Static Website<br/>website/build/"]
        PythonDocs["Python API HTML<br/>mmlspark.blob.../pyspark/"]
        ScalaDocs["Scala API HTML<br/>mmlspark.blob.../scala/"]
    end
    
    subgraph "Deployment Targets"
        GitHubPages["GitHub Pages<br/>microsoft.github.io/SynapseML/"]
        BlobStorage["Azure Blob Storage<br/>docs/ container"]
    end
    
    Notebooks --> NotebookConv
    NotebookConv --> Docusaurus
    Markdown --> Docusaurus
    
    ScalaSrc --> ScalaUnidoc
    PythonSrc --> Sphinx
    
    Docusaurus --> StaticSite
    ScalaUnidoc --> ScalaDocs
    Sphinx --> PythonDocs
    
    StaticSite --> GitHubPages
    ScalaDocs --> BlobStorage
    PythonDocs --> BlobStorage
    
    BlobStorage -.->|"External Links"| GitHubPages
```

**Content Processing Pipeline:**

1. **Jupyter Notebooks**: Serve dual purposes as both executable examples and documentation pages. Notebooks are converted to markdown during the build process and integrated into Docusaurus.

2. **Markdown Documentation**: Authored in `docs/` directory, organized by topic (Get Started, Explore Algorithms, etc.), processed directly by Docusaurus with remark-math and rehype-katex for mathematical notation.

3. **API Documentation**: Generated separately from source code annotations. Scala API uses ScalaUnidoc, Python API uses Sphinx. These are uploaded to Azure Blob Storage and linked from the main site via external URLs.

Sources: [website/docusaurus.config.js:135-158](), Diagram 5 from high-level architecture

## Docusaurus Configuration

The primary configuration resides in `docusaurus.config.js`, which defines the site structure, plugins, and integrations.

### Core Configuration

| Property | Value | Purpose |
|----------|-------|---------|
| `title` | "SynapseML" | Site title |
| `url` | "https://microsoft.github.io" | Base domain |
| `baseUrl` | "/SynapseML/" | Path prefix |
| `organizationName` | "microsoft" | GitHub org |
| `projectName` | "SynapseML" | GitHub repo |
| `trailingSlash` | `true` | URL formatting |
| `version` | "1.1.0" | Current version |

Sources: [website/docusaurus.config.js:6-17]()

### Theme Configuration

The site uses a custom Prism theme configuration with separate light/dark modes:

```javascript
prism: {
    theme: require('./src/plugins/prism_themes/github'),
    darkTheme: require('./src/plugins/prism_themes/monokai'),
    additionalLanguages: ['csharp', 'powershell'],
}
```

**Default Mode**: Dark mode (`colorMode.defaultMode: 'dark'`)

**Supported Languages**: JavaScript, Python, Scala, C#, PowerShell, YAML (via custom themes)

Sources: [website/docusaurus.config.js:26-32]()

### Algolia Search Integration

```mermaid
graph LR
    subgraph "Search Configuration"
        AlgoliaConfig["algolia config<br/>docusaurus.config.js:124-129"]
        AppID["appId: GBW8AA15RD"]
        APIKey["apiKey: 70a680..."]
        IndexName["indexName: synapseML"]
        ContextSearch["contextualSearch: true"]
    end
    
    subgraph "Website Components"
        Navbar["Navbar Search Box"]
        SearchResults["Search Results Page"]
    end
    
    subgraph "Algolia Service"
        Crawler["Algolia Crawler"]
        Index["Search Index"]
    end
    
    AlgoliaConfig --> AppID
    AlgoliaConfig --> APIKey
    AlgoliaConfig --> IndexName
    AlgoliaConfig --> ContextSearch
    
    AppID --> Navbar
    APIKey --> Navbar
    IndexName --> Navbar
    
    Navbar --> Index
    Index --> SearchResults
    Crawler --> Index
```

**Configuration Details**:
- **App ID**: `GBW8AA15RD`
- **Index Name**: `synapseML`
- **Contextual Search**: Enabled to scope results by documentation version
- **Theme Integration**: Search box appears in navbar via `@docusaurus/theme-search-algolia` plugin

Sources: [website/docusaurus.config.js:124-129](), [website/package.json:22]()

## Navigation and Versioning

### Navbar Structure

The navbar configuration defines the primary navigation structure:

```javascript
navbar: {
    items: [
        {to: 'docs/Overview', label: 'Docs', position: 'left'},
        {to: 'blog', label: 'Blog', position: 'left'},
        {to: 'videos', label: 'Videos', position: 'left'},
        {
            type: 'docsVersionDropdown',
            position: 'right',
        },
        {
            type: 'localeDropdown',
            position: 'right',
        },
        {
            label: 'Developer Docs',
            position: 'right',
            items: [
                {
                    label: 'Python',
                    href: `https://mmlspark.blob.core.windows.net/docs/${version}/pyspark/index.html`,
                },
                {
                    label: 'Scala',
                    href: `https://mmlspark.blob.core.windows.net/docs/${version}/scala/com/microsoft/azure/synapse/ml/index.html`,
                }
            ]
        },
        // GitHub link icon
    ],
}
```

**Key Features**:
- **Version Dropdown**: Automatically populated from `versions.json` file
- **Locale Dropdown**: Prepared for internationalization (i18n)
- **External API Links**: Point to version-specific API docs on Azure Blob Storage
- **GitHub Icon**: Links to source repository

Sources: [website/docusaurus.config.js:35-74]()

### Version Management

The documentation supports multiple versions with version-specific documentation:

**Current Versions**:
- 1.1.0 (latest)
- 0.10.0
- 0.9.4

**Version-Specific Resources**:
- Each version has separate API documentation URLs
- Sidebars can differ between versions
- Content is duplicated and frozen for each version

Sources: [website/docusaurus.config.js:4](), [website/docusaurus.config.js:59-63]()

## URL Redirect System

The documentation system maintains extensive backward compatibility through a redirect plugin configuration with 160+ redirect rules.

### Redirect Categories

```mermaid
graph TB
    subgraph "Redirect Patterns"
        VersionRedirects["Version Migrations<br/>0.9.4, 0.10.0, 0.11.0 → current"]
        PathReorg["Path Reorganization<br/>features/ → Explore Algorithms/"]
        ServiceRenames["Service Renames<br/>CognitiveServices → AI Services"]
        DocsRestructure["Documentation Restructure<br/>documentation/ → Quick Examples/"]
    end
    
    subgraph "Plugin Configuration"
        RedirectPlugin["@docusaurus/plugin-client-redirects"]
        RedirectsArray["redirects: [...]<br/>163 rules"]
    end
    
    subgraph "Implementation"
        FromPaths["from: old URL pattern"]
        ToPaths["to: new URL pattern"]
        ClientSideRedirect["Client-side redirect<br/>via JavaScript"]
    end
    
    VersionRedirects --> RedirectsArray
    PathReorg --> RedirectsArray
    ServiceRenames --> RedirectsArray
    DocsRestructure --> RedirectsArray
    
    RedirectPlugin --> RedirectsArray
    RedirectsArray --> FromPaths
    RedirectsArray --> ToPaths
    FromPaths --> ClientSideRedirect
    ToPaths --> ClientSideRedirect
```

**Example Redirect Rules**:

| From | To | Reason |
|------|-----|--------|
| `/docs/about/` | `/docs/Overview/` | Documentation restructure |
| `/docs/features/cognitive_services/CognitiveServices%20-%20Overview/` | `/docs/Explore Algorithms/AI Services/Overview/` | Path reorganization + service rename |
| `/docs/getting_started/installation/` | `/docs/Get Started/Install SynapseML/` | Space-normalized paths |
| `/docs/0.9.4/features/lightgbm/LightGBM%20-%20Overview/` | `/docs/Explore Algorithms/LightGBM/Overview/` | Version migration |

Sources: [website/docusaurus.config.js:159-478]()

### Redirect Implementation

The `@docusaurus/plugin-client-redirects` plugin generates HTML files at old URLs that immediately redirect to new locations using JavaScript. This approach:
- Maintains SEO value from old URLs
- Works without server-side configuration
- Supports complex pattern matching
- Handles percentage-encoded URLs

Sources: [website/docusaurus.config.js:160-478](), [website/package.json:19]()

## Custom React Components

The website extends Docusaurus with custom React components for enhanced code presentation.

### CodeSnippet Component

```mermaid
graph TB
    subgraph "Component: CodeSnippet"
        ComponentFile["website/src/theme/CodeSnippet/index.js"]
        Props["Props:<br/>lang, snippet"]
        UseColorMode["useColorMode hook<br/>Dark/Light theme detection"]
        PrismTheme["Prism Theme Selection<br/>monokai (dark) / github (light)"]
        HighlightComponent["prism-react-renderer<br/>Highlight component"]
    end
    
    subgraph "Rendering"
        PreElement["<pre> with syntax highlighting"]
        TokenMapping["Token-by-token rendering"]
        Styles["styles.module.css<br/>custom styling"]
    end
    
    ComponentFile --> Props
    Props --> UseColorMode
    UseColorMode --> PrismTheme
    PrismTheme --> HighlightComponent
    HighlightComponent --> TokenMapping
    TokenMapping --> PreElement
    PreElement --> Styles
```

**Implementation Details**:

The component handles theme-aware syntax highlighting with server-side rendering (SSR) compatibility:

```javascript
const [mounted, setMounted] = useState(false);
useEffect(() => {
    setMounted(true);
}, []);

const {isDarkTheme} = useColorMode();
const lightModeTheme = prism.theme || monokai;
const darkModeTheme = prism.darkTheme || lightModeTheme;
const prismTheme = isDarkTheme ? darkModeTheme : lightModeTheme;
```

**Key Features**:
- **SSR Compatibility**: Uses `mounted` state to force re-render after hydration, preventing theme flash
- **Theme Switching**: Dynamically selects Prism theme based on color mode
- **Language Support**: Accepts `lang` prop for syntax highlighting (defaults to YAML)
- **Token-Level Rendering**: Uses `getLineProps` and `getTokenProps` for fine-grained styling

Sources: [website/src/theme/CodeSnippet/index.js:1-58]()

### SampleSnippet Component

An enhanced code snippet component with copy functionality and optional "Read more" link:

**Component Structure**:
```javascript
function SampleSnippet(props) {
  const { lang = "python", config, copyBit, further } = props;
  
  const handleCopyCode = () => {
    copy(copySnippet);
    setShowCopied(true);
    setTimeout(() => setShowCopied(false), 2000);
  };
  
  // Returns Highlight component with:
  // - Copy button (shows "Copied" for 2 seconds)
  // - Optional "Read more" link
  // - Same theme-aware rendering as CodeSnippet
}
```

**Features**:
- **Copy Button**: Uses `copy-text-to-clipboard` library with visual feedback
- **Customizable Copy Text**: `copyBit` prop can differ from displayed `config`
- **Further Reading Link**: Optional `further` prop adds navigation button
- **Internationalization**: Uses `@docusaurus/Translate` for button labels
- **Styling**: Custom CSS classes via `styles.module.css`

Sources: [website/src/theme/SampleSnippet/index.js:1-119]()

### NotFound Component (404 Page)

Custom 404 page with user-friendly messaging:

```javascript
function NotFound() {
  return (
    <Layout title="Page Not Found">
      <div className="container margin-vert--xl">
        <div className="row">
          <div className={classnames("col col--6 col--offset-3", styles.notFoundContainer)}>
            <h1 className="hero__title">Sorry! Page Not Found</h1>
            <p>We have been doing some work on our website, chances are that 
               the page you're looking for is <a href="./docs/Overview/">in the new docs section</a>.</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
```

**Purpose**: Guides users to the new documentation structure after recent reorganization

Sources: [website/src/theme/NotFound/index.js:1-30]()

## Build Dependencies

### Core Dependencies

The website relies on several key npm packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `@docusaurus/core` | ^2.4.1 | Static site generator core |
| `@docusaurus/preset-classic` | ^2.4.1 | Default theme and plugins |
| `@docusaurus/plugin-client-redirects` | ^2.4.1 | URL redirect handling |
| `@docusaurus/theme-search-algolia` | ^2.4.1 | Algolia search integration |
| `react` | ^16.8.4 | UI framework |
| `react-dom` | ^16.8.4 | React rendering |
| `remark-math` | 3 | Markdown math support |
| `rehype-katex` | 4 | Math rendering (LaTeX) |
| `react-player` | ^2.11.0 | Video playback (for Videos page) |

Sources: [website/package.json:17-38]()

### Security Resolutions

The package.json includes security resolutions to override vulnerable transitive dependencies:

```javascript
"resolutions": {
    "@docusaurus/core/**/set-value": "^4.0.1",
    "@docusaurus/**/trim": "^0.0.3",
    "@docusaurus/**/glob-parent": "^5.1.2",
    "@docusaurus/**/ansi-html-community": "^0.0.8",
    "@docusaurus/**/immer": "^9.0.6",
    "@docusaurus/**/browserslist": "^4.16.5",
    "@docusaurus/**/nth-check": "^2.0.1",
    // ...
}
```

These resolutions ensure that vulnerable versions of indirect dependencies are replaced with patched versions.

Sources: [website/package.json:39-52]()

## Build and Deployment Scripts

### NPM Scripts

```javascript
"scripts": {
    "start": "docusaurus start",        // Development server
    "build": "docusaurus build",        // Production build
    "swizzle": "docusaurus swizzle",    // Component customization
    "deploy": "docusaurus deploy",      // GitHub Pages deployment
    "clear": "docusaurus clear",        // Clear cache
    "serve": "docusaurus serve",        // Serve production build
    "audit:fix": "npx yarn-audit-fix"   // Security audit fix
}
```

**Development Workflow**:
1. `yarn start` - Launches development server with hot reload at `http://localhost:3000`
2. `yarn build` - Generates static site in `website/build/` directory
3. `yarn serve` - Serves production build locally for testing
4. `yarn deploy` - Deploys to GitHub Pages

Sources: [website/package.json:8-16]()

### Build Configuration

The Docusaurus preset configures the build process:

```javascript
presets: [
    [
        '@docusaurus/preset-classic',
        {
            docs: {
                sidebarPath: require.resolve('./sidebars.js'),
                remarkPlugins: [math],
                rehypePlugins: [katex],
            },
            theme: {
                customCss: require.resolve('./src/css/custom.css'),
            },
            gtag: {
                trackingID: 'G-RWPE0183E8',
                anonymizeIP: true,
            },
            blog: {
                feedOptions: {
                    type: 'all',
                },
            },
        },
    ],
]
```

**Configuration Elements**:
- **Sidebar**: Generated from `sidebars.js` configuration file
- **Math Support**: `remark-math` processes `$...$` syntax, `rehype-katex` renders to HTML
- **Custom CSS**: Site-wide styles from `src/css/custom.css`
- **Analytics**: Google Analytics 4 with anonymized IPs
- **Blog RSS**: Generates RSS, Atom, and JSON feeds

Sources: [website/docusaurus.config.js:135-158]()

## Footer Configuration

The footer provides navigation and community links:

```javascript
footer: {
    style: 'dark',
    links: [
        {
            title: 'Docs',
            items: [
                {label: 'Installation', to: 'docs/Get%20Started/Install%20SynapseML'},
                {label: 'Getting Started', to: 'docs/Get%20Started/Quickstart%20-%20Your%20First%20Models'},
                {label: 'Python API Reference', to: 'https://mmlspark.blob.core.windows.net/docs/1.0.13/pyspark/index.html'},
                {label: 'Scala API Reference', to: 'https://mmlspark.blob.core.windows.net/docs/1.1.0/scala/index.html'},
            ],
        },
        {
            title: 'More',
            items: [
                {label: 'Blog', to: 'blog'},
                {label: 'Videos', to: 'videos'},
            ],
        },
        {
            title: 'Community',
            items: [
                {label: 'GitHub', href: 'https://github.com/microsoft/SynapseML'},
            ],
        },
    ],
    copyright: `Copyright © ${new Date().getFullYear()} Microsoft.`,
}
```

**Notable Features**:
- External links to version-specific API documentation on Azure Blob Storage
- Links to different documentation versions (note Python link still points to 1.0.13)
- GitHub repository link for community engagement

Sources: [website/docusaurus.config.js:75-123]()

## Math Rendering Integration

The documentation system supports mathematical notation using KaTeX:

### Configuration

```javascript
// In docusaurus.config.js
stylesheets: [
    {
        href: "https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css",
        integrity: "sha384-Um5gpz1odJg5Z4HAmzPtgZKdTBHZdw8S29IecapCSB31ligYPhHQZMIlWLYQGVoc",
        crossorigin: "anonymous",
    },
],

// In preset configuration
docs: {
    remarkPlugins: [math],
    rehypePlugins: [katex],
}
```

**Processing Pipeline**:
1. `remark-math` (version 3) parses LaTeX syntax in markdown (`$inline$` and `$$block$$`)
2. `rehype-katex` (version 4) converts parsed math to HTML with KaTeX classes
3. KaTeX CSS stylesheet styles the rendered math

**Usage in Documentation**:
```markdown
Inline math: $E = mc^2$

Block math:
$$
\frac{\partial f}{\partial x} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$
```

Sources: [website/docusaurus.config.js:18-24](), [website/docusaurus.config.js:141-142](), [website/package.json:35-36]()

## Announcement Bar

The site includes a persistent announcement bar encouraging GitHub stars:

```javascript
announcementBar: {
    id: 'announcementBar-1', // Increment on change
    content: `⭐️ If you like SynapseML, consider giving it a star on 
              <a target="_blank" rel="noopener noreferrer" 
              href="https://github.com/Microsoft/SynapseML">GitHub</a> ⭐`,
}
```

**Purpose**: Drive community engagement through GitHub stars
**Dismissible**: Users can close the bar; dismissed state persists via `id` versioning

Sources: [website/docusaurus.config.js:130-133]()

## Example Notebooks as Documentation

Jupyter notebooks serve as both executable examples and documentation content. The provided example demonstrates the standard notebook structure:

### Notebook Structure Pattern

```python
# 1. Header with visual branding
<img width="200" src="https://mmlspark.blob.core.windows.net/graphics/..." />

# 2. Title and description
# Binary Classification with VowpalWabbit on Criteo Dataset

# 3. Step-by-step code with explanations
## SparkML Vector input
#### Read dataset
# Code cells with actual implementation

# 4. Results and metrics display
from synapse.ml.train import ComputeModelStatistics
metrics = ComputeModelStatistics(...)
display(metrics)
```

**Key Characteristics**:
- Markdown cells provide narrative structure
- Code cells are executable in Synapse/Databricks environments
- `display()` function shows interactive dataframes
- External resources (images, datasets) hosted on Azure Blob Storage
- Self-contained examples with all necessary imports

**Integration with Website**:
- Notebooks are converted to markdown pages during build
- Code blocks become syntax-highlighted examples
- Output is preserved or re-generated during testing
- Notebooks also serve as E2E tests (see [Synapse E2E Testing](#4.2) and [Databricks E2E Testing](#4.3))

Sources: [docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb:1-191]()

## Deployment Architecture

```mermaid
graph TB
    subgraph "Build Process"
        LocalBuild["Local Build<br/>yarn build"]
        CIBuild["CI Build<br/>Azure Pipeline"]
        BuildOutput["build/ directory<br/>Static HTML/JS/CSS"]
    end
    
    subgraph "Deployment Targets"
        GitHubPages["GitHub Pages<br/>microsoft.github.io/SynapseML"]
        GHPagesConfig["gh-pages branch<br/>CNAME: custom domain"]
    end
    
    subgraph "API Documentation Deployment"
        SphinxBuild["Sphinx Build<br/>Python API"]
        ScalaUnidocBuild["ScalaUnidoc Build<br/>Scala API"]
        BlobUpload["Azure Blob Storage Upload<br/>docs/ container"]
        VersionedDocs["Versioned Docs<br/>docs/1.1.0/pyspark/<br/>docs/1.1.0/scala/"]
    end
    
    subgraph "CDN and Access"
        BlobCDN["Azure CDN<br/>mmlspark.blob.core.windows.net"]
        ExternalLinks["External Links<br/>from main site"]
    end
    
    LocalBuild --> BuildOutput
    CIBuild --> BuildOutput
    BuildOutput --> GitHubPages
    GitHubPages --> GHPagesConfig
    
    SphinxBuild --> BlobUpload
    ScalaUnidocBuild --> BlobUpload
    BlobUpload --> VersionedDocs
    VersionedDocs --> BlobCDN
    BlobCDN --> ExternalLinks
    ExternalLinks --> GitHubPages
```

### GitHub Pages Deployment

**Deployment Command**: `docusaurus deploy`

**Process**:
1. Builds static site to `build/` directory
2. Creates/updates `gh-pages` branch in repository
3. Pushes static files to `gh-pages` branch
4. GitHub Pages serves from `gh-pages` branch at configured URL

**Configuration**:
- **Organization Name**: `microsoft`
- **Project Name**: `SynapseML`
- **Base URL**: `/SynapseML/`
- **Trailing Slash**: Enabled for consistent URLs

Sources: [website/docusaurus.config.js:6-14]()

### API Documentation Deployment

API documentation is deployed separately to Azure Blob Storage:

**Storage Structure**:
```
mmlspark.blob.core.windows.net/docs/
├── 1.1.0/
│   ├── pyspark/
│   │   └── index.html
│   └── scala/
│       └── com/microsoft/azure/synapse/ml/index.html
├── 0.10.0/
│   ├── pyspark/
│   └── scala/
└── ...
```

**Access Pattern**:
- Python API: `https://mmlspark.blob.core.windows.net/docs/{version}/pyspark/index.html`
- Scala API: `https://mmlspark.blob.core.windows.net/docs/{version}/scala/com/microsoft/azure/synapse/ml/index.html`

**Integration**: Main website links to these external docs via navbar "Developer Docs" dropdown

Sources: [website/docusaurus.config.js:54-66]()

## Quality Assurance

### Dead Link Checking

The CI/CD pipeline includes dead link validation:

**Tool**: `wget --spider --recursive` or similar link checker
**Scope**: Validates all internal links and external references
**Timing**: Runs as part of website build in CI pipeline

For details on the testing infrastructure, see [Testing Infrastructure](#4).

### Code Block Testing

Jupyter notebooks undergo automated testing:

**Tool**: `pytest-codeblocks` (Python)
**Process**:
1. Extract code blocks from notebook cells
2. Execute code in isolated environment
3. Validate output and check for errors
4. Report test failures

**Integration**: Code blocks in website documentation are derived from tested notebooks, ensuring accuracy

For details on notebook testing, see [Synapse E2E Testing](#4.2) and [Website Code Tests](#4.1).

Sources: Diagram 4 from high-level architecture, [Testing Infrastructure](#4)

---

**Related Pages**:
- [Website Architecture](#7.1) - Detailed technical architecture of Docusaurus site
- [Homepage and Components](#7.2) - React components and homepage design
- [Example Notebooks](#7.3) - Notebook system and conversion pipeline
- [CI/CD Pipeline](#3.1) - Integration of documentation builds in CI/CD
- [Testing Infrastructure](#4) - Quality assurance for documentation

---

# Page: Website Architecture

# Website Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb](docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb)
- [website/docusaurus.config.js](website/docusaurus.config.js)
- [website/package.json](website/package.json)
- [website/src/theme/CodeSnippet/index.js](website/src/theme/CodeSnippet/index.js)
- [website/src/theme/NotFound/index.js](website/src/theme/NotFound/index.js)
- [website/src/theme/SampleSnippet/index.js](website/src/theme/SampleSnippet/index.js)
- [website/yarn.lock](website/yarn.lock)

</details>



This page documents the technical architecture of the SynapseML documentation website, including the Docusaurus build system, versioning strategy, search integration, and deployment pipeline.

## Technology Stack

The SynapseML website is built on **Docusaurus v2.4.1**, a React-based static site generator optimized for technical documentation. The core technology stack includes:

| Component | Technology | Version |
|-----------|-----------|---------|
| Static Site Generator | Docusaurus | 2.4.1 |
| UI Framework | React | 16.8.4 |
| Syntax Highlighting | Prism React Renderer | - |
| Math Rendering | KaTeX | 0.13.11 |
| Search | Algolia DocSearch | - |
| Package Manager | Yarn | - |
| Build Tool | Node.js | 16.18.1+ |

The site is hosted on **GitHub Pages** at `https://microsoft.github.io/SynapseML/`.

Sources: [website/package.json:1-65](), [website/docusaurus.config.js:1-25]()

## Architecture Overview

**Docusaurus Architecture Diagram**

```mermaid
graph TB
    subgraph "Input Sources"
        DocusaurusConfig["docusaurus.config.js"]
        SidebarsConfig["sidebars.js"]
        PackageJSON["package.json"]
        MarkdownDocs["Markdown Docs"]
        JupyterNotebooks["Jupyter Notebooks (.ipynb)"]
        ReactPages["React Pages (.js)"]
        CustomCSS["src/css/custom.css"]
    end
    
    subgraph "Docusaurus Build System"
        PresetClassic["@docusaurus/preset-classic"]
        PluginDocs["Plugin: Docs"]
        PluginBlog["Plugin: Blog"]
        PluginRedirects["Plugin: Client Redirects"]
        PluginGtag["Plugin: Google Analytics"]
        RemarkMath["remark-math plugin"]
        RehypeKatex["rehype-katex plugin"]
    end
    
    subgraph "Theme System"
        ThemeClassic["@docusaurus/theme-classic"]
        ThemeAlgolia["@docusaurus/theme-search-algolia"]
        CustomComponents["Custom React Components"]
        PrismThemes["Custom Prism Themes"]
    end
    
    subgraph "Output"
        StaticHTML["Static HTML"]
        JavaScriptBundles["JavaScript Bundles"]
        CSSBundles["CSS Bundles"]
        Assets["Static Assets"]
    end
    
    DocusaurusConfig --> PresetClassic
    SidebarsConfig --> PluginDocs
    PackageJSON --> PresetClassic
    MarkdownDocs --> PluginDocs
    JupyterNotebooks --> PluginDocs
    ReactPages --> PresetClassic
    CustomCSS --> ThemeClassic
    
    PresetClassic --> PluginDocs
    PresetClassic --> PluginBlog
    PresetClassic --> PluginGtag
    PluginDocs --> RemarkMath
    RemarkMath --> RehypeKatex
    
    ThemeClassic --> CustomComponents
    ThemeClassic --> PrismThemes
    
    PluginDocs --> StaticHTML
    PluginBlog --> StaticHTML
    PluginRedirects --> StaticHTML
    ThemeClassic --> CSSBundles
    ThemeAlgolia --> JavaScriptBundles
    CustomComponents --> JavaScriptBundles
    
    StaticHTML --> GitHubPages["GitHub Pages Deployment"]
    JavaScriptBundles --> GitHubPages
    CSSBundles --> GitHubPages
    Assets --> GitHubPages
```

Sources: [website/docusaurus.config.js:135-158](), [website/package.json:17-38]()

## Build System

The build system uses npm/yarn scripts defined in `package.json` to orchestrate the Docusaurus build pipeline.

**Build Scripts**

| Script | Command | Purpose |
|--------|---------|---------|
| `start` | `docusaurus start` | Starts local development server with hot reload |
| `build` | `docusaurus build` | Produces optimized production build |
| `serve` | `docusaurus serve` | Serves production build locally for testing |
| `deploy` | `docusaurus deploy` | Deploys to GitHub Pages |
| `clear` | `docusaurus clear` | Clears build cache and temp files |
| `swizzle` | `docusaurus swizzle` | Ejects theme components for customization |

**Build Process Flow**

```mermaid
flowchart TD
    Start["npm run build"] --> LoadConfig["Load docusaurus.config.js"]
    LoadConfig --> ProcessContent["Process Content"]
    
    ProcessContent --> ParseMarkdown["Parse Markdown/MDX"]
    ProcessContent --> ParseNotebooks["Parse Jupyter Notebooks"]
    ProcessContent --> ParseReact["Parse React Pages"]
    
    ParseMarkdown --> ApplyPlugins["Apply Plugins"]
    ParseNotebooks --> ApplyPlugins
    ParseReact --> ApplyPlugins
    
    ApplyPlugins --> RemarkMath["remark-math: Parse LaTeX"]
    ApplyPlugins --> RehypeKatex["rehype-katex: Render Math"]
    ApplyPlugins --> GenerateRoutes["Generate Routes"]
    
    RemarkMath --> RehypeKatex
    RehypeKatex --> GenerateRoutes
    
    GenerateRoutes --> BuildTheme["Build Theme + Components"]
    BuildTheme --> Webpack["Webpack Bundling"]
    
    Webpack --> OptimizeJS["Optimize JavaScript"]
    Webpack --> OptimizeCSS["Optimize CSS"]
    Webpack --> CopyAssets["Copy Static Assets"]
    
    OptimizeJS --> Output["build/ directory"]
    OptimizeCSS --> Output
    CopyAssets --> Output
    
    Output --> ValidateLinks["Validate Internal Links"]
    ValidateLinks --> Complete["Build Complete"]
```

The build outputs a fully static site in the `build/` directory with:
- Pre-rendered HTML for all pages (SEO-optimized)
- Code-split JavaScript bundles
- Optimized CSS files
- Copied static assets (images, fonts, etc.)

Sources: [website/package.json:8-16](), [website/docusaurus.config.js:1-6]()

## Configuration Architecture

**docusaurus.config.js Structure**

The main configuration file exports a JavaScript object with the following structure:

```mermaid
graph TB
    subgraph "docusaurus.config.js"
        Root["module.exports"]
        
        Root --> Metadata["Site Metadata"]
        Root --> CustomFields["customFields"]
        Root --> Stylesheets["stylesheets"]
        Root --> ThemeConfig["themeConfig"]
        Root --> Presets["presets"]
        Root --> Plugins["plugins"]
        
        Metadata --> Title["title: 'SynapseML'"]
        Metadata --> URL["url: 'https://microsoft.github.io'"]
        Metadata --> BaseURL["baseUrl: '/SynapseML/'"]
        Metadata --> OrgName["organizationName: 'microsoft'"]
        
        CustomFields --> Version["version: '1.1.0'"]
        
        Stylesheets --> KatexCSS["KaTeX CDN Stylesheet"]
        
        ThemeConfig --> Prism["prism: { theme, darkTheme }"]
        ThemeConfig --> Navbar["navbar: { items, logo }"]
        ThemeConfig --> Footer["footer: { links, copyright }"]
        ThemeConfig --> Algolia["algolia: { appId, apiKey, indexName }"]
        ThemeConfig --> AnnouncementBar["announcementBar"]
        
        Presets --> PresetClassic["@docusaurus/preset-classic"]
        PresetClassic --> DocsConfig["docs: { sidebarPath, plugins }"]
        PresetClassic --> BlogConfig["blog: { feedOptions }"]
        PresetClassic --> GtagConfig["gtag: { trackingID }"]
        
        Plugins --> RedirectPlugin["@docusaurus/plugin-client-redirects"]
        RedirectPlugin --> RedirectRules["redirects: [ {...}, {...}, ... ]"]
    end
```

Key configuration sections:

**Site Metadata** ([website/docusaurus.config.js:6-14]()):
- `title`: "SynapseML"
- `tagline`: "Simple and Distributed Machine Learning"
- `url`: Base URL for GitHub Pages
- `baseUrl`: "/SynapseML/"
- `organizationName`: "microsoft"
- `projectName`: "SynapseML"

**Theme Configuration** ([website/docusaurus.config.js:25-134]()):
- `prism`: Custom syntax highlighting themes for light/dark modes
- `colorMode`: Default to dark theme
- `navbar`: Navigation bar with version dropdown, locale selector, and external API docs links
- `footer`: Links to documentation, community resources
- `algolia`: Search integration configuration
- `announcementBar`: Site-wide announcement banner

**Presets** ([website/docusaurus.config.js:135-158]()):
The `@docusaurus/preset-classic` bundle includes:
- Docs plugin with `remark-math` and `rehype-katex` for LaTeX rendering
- Blog plugin with RSS/Atom feed generation
- Google Analytics (`gtag`) for tracking
- Custom CSS from `src/css/custom.css`

**Plugins** ([website/docusaurus.config.js:159-479]()):
- `@docusaurus/plugin-client-redirects`: Manages 100+ URL redirects for backward compatibility

Sources: [website/docusaurus.config.js:1-480]()

## Versioning System

The website supports multiple documentation versions corresponding to SynapseML releases. Version management is handled through Docusaurus's built-in versioning system.

**Version Configuration**

The current version is defined in [website/docusaurus.config.js:4]():
```javascript
let version = "1.1.0";
```

This version variable is used throughout the configuration:
- Custom fields exposed to React components ([website/docusaurus.config.js:15-17]())
- External API documentation links ([website/docusaurus.config.js:59-64]())

**Version Dropdown**

The navbar includes a version dropdown ([website/docusaurus.config.js:45-48]()) configured with:
```javascript
{
    type: 'docsVersionDropdown',
    position: 'right',
}
```

This allows users to switch between:
- Latest version (1.1.0)
- Previous versions (0.9.4, 0.10.0, etc.)

**Versioned API Documentation**

External API documentation is versioned and hosted on Azure Blob Storage:
- **Python API**: `https://mmlspark.blob.core.windows.net/docs/${version}/pyspark/index.html`
- **Scala API**: `https://mmlspark.blob.core.windows.net/docs/${version}/scala/com/microsoft/azure/synapse/ml/index.html`

These links are dynamically generated based on the current version.

**Version-Specific Content**

Each documentation version maintains:
- Separate sidebar configuration
- Version-specific markdown/notebook files
- Independent build artifacts

The versioning system ensures users can access documentation matching their installed SynapseML version.

Sources: [website/docusaurus.config.js:4](), [website/docusaurus.config.js:15-17](), [website/docusaurus.config.js:45-65]()

## Search Integration

The website uses **Algolia DocSearch** for full-text search across all documentation pages.

**Algolia Configuration**

Configuration in [website/docusaurus.config.js:124-129]():

```javascript
algolia: {
    appId: 'GBW8AA15RD',
    apiKey: '70a6807005c645678741ab941bb89ed8',
    indexName: 'synapseML',
    contextualSearch: true,
}
```

**Search Architecture**

```mermaid
graph LR
    subgraph "Search System"
        UserQuery["User Search Query"] --> AlgoliaWidget["Algolia Search Widget"]
        AlgoliaWidget --> AlgoliaAPI["Algolia API"]
        
        AlgoliaAPI --> SearchIndex["Search Index: 'synapseML'"]
        SearchIndex --> Results["Search Results"]
        
        Results --> Ranking["Relevance Ranking"]
        Ranking --> Display["Display in UI"]
        
        subgraph "Index Population"
            DocusaurusBuild["Docusaurus Build"] --> Crawler["Algolia Crawler"]
            Crawler --> SearchIndex
        end
        
        ContextualSearch["contextualSearch: true"] --> AlgoliaAPI
    end
```

**Search Features**:
- **Contextual search**: Results scoped to current documentation version
- **Full-text indexing**: All markdown, notebook content, and code snippets
- **Ranking algorithm**: Prioritizes title matches, then heading matches, then body content
- **Instant results**: Search-as-you-type with debouncing
- **Keyboard navigation**: Full keyboard support for accessibility

The Algolia index is automatically updated when new content is deployed to GitHub Pages via the Algolia crawler.

Sources: [website/docusaurus.config.js:124-129](), [website/package.json:22]()

## Theme and Custom Components

The website extends the default Docusaurus theme with custom React components for enhanced code display and user experience.

**Custom Theme Components**

```mermaid
graph TB
    subgraph "Theme System"
        DocusaurusTheme["@docusaurus/theme-classic"]
        
        DocusaurusTheme --> SwizzledComponents["Swizzled Components"]
        
        SwizzledComponents --> CodeSnippet["CodeSnippet Component"]
        SwizzledComponents --> SampleSnippet["SampleSnippet Component"]
        SwizzledComponents --> NotFoundPage["NotFound Component"]
        
        CodeSnippet --> PrismReact["prism-react-renderer"]
        SampleSnippet --> PrismReact
        SampleSnippet --> CopyToClipboard["copy-text-to-clipboard"]
        
        PrismReact --> CustomPrismThemes["Custom Prism Themes"]
        CustomPrismThemes --> MonokaiTheme["src/plugins/prism_themes/monokai"]
        CustomPrismThemes --> GithubTheme["src/plugins/prism_themes/github"]
        
        ColorMode["useColorMode hook"] --> CodeSnippet
        ColorMode --> SampleSnippet
    end
```

**CodeSnippet Component** ([website/src/theme/CodeSnippet/index.js:1-57]()):

This component renders syntax-highlighted code blocks with theme awareness:

```javascript
function CodeSnippet(props) {
  const { isDarkTheme } = useColorMode();
  const prismTheme = isDarkTheme ? darkModeTheme : lightModeTheme;
  
  return (
    <Highlight theme={prismTheme} code={snippet} language={lang}>
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <pre className={className} style={style}>
          {/* Render code tokens */}
        </pre>
      )}
    </Highlight>
  );
}
```

Key features:
- Automatic light/dark theme switching based on `useColorMode()` hook
- Uses `prism-react-renderer` for syntax highlighting
- Supports multiple languages (Python, Scala, JavaScript, etc.)
- Server-side rendering safe with `mounted` state

**SampleSnippet Component** ([website/src/theme/SampleSnippet/index.js:1-118]()):

Enhanced code snippet with interactive features:

```javascript
function SampleSnippet(props) {
  const [showCopied, setShowCopied] = useState(false);
  
  const handleCopyCode = () => {
    copy(copySnippet);
    setShowCopied(true);
    setTimeout(() => setShowCopied(false), 2000);
  };
  
  return (
    <Highlight theme={prismTheme} code={config} language={lang}>
      {/* Code rendering */}
      <button onClick={handleCopyCode}>
        {showCopied ? "Copied" : "Copy"}
      </button>
      {further && <Link to={further}>Read more</Link>}
    </Highlight>
  );
}
```

Key features:
- Copy-to-clipboard functionality with visual feedback
- Optional "Read more" links to detailed documentation
- Same theme awareness as CodeSnippet
- Used on homepage for installation instructions

**NotFound Component** ([website/src/theme/NotFound/index.js:1-30]()):

Custom 404 page that provides helpful navigation:

```javascript
function NotFound() {
  return (
    <Layout title="Page Not Found">
      <h1>Sorry! Page Not Found</h1>
      <p>Chances are that the page you're looking for is 
         <a href="./docs/Overview/">in the new docs section</a>.</p>
    </Layout>
  );
}
```

This component is particularly useful given the extensive redirect system (100+ redirects) for legacy URLs.

**Custom Prism Themes**:
- **Light mode**: GitHub theme (`src/plugins/prism_themes/github`)
- **Dark mode**: Monokai theme (`src/plugins/prism_themes/monokai`)
- Additional language support configured in [website/docusaurus.config.js:26-30]()

Sources: [website/src/theme/CodeSnippet/index.js:1-57](), [website/src/theme/SampleSnippet/index.js:1-118](), [website/src/theme/NotFound/index.js:1-30](), [website/docusaurus.config.js:26-30]()

## Deployment Pipeline

The website deploys to **GitHub Pages** using Docusaurus's built-in deployment command.

**Deployment Flow**

```mermaid
flowchart TB
    subgraph "Local Development"
        LocalChanges["Code Changes"] --> CommitPush["git push to main"]
    end
    
    subgraph "GitHub Actions / Manual Deploy"
        CommitPush --> RunBuild["npm run build"]
        RunBuild --> DocusaurusBuild["docusaurus build"]
        
        DocusaurusBuild --> GenerateStatic["Generate Static Files"]
        GenerateStatic --> BuildDir["build/ directory"]
        
        BuildDir --> DeployCommand["npm run deploy"]
        DeployCommand --> DocusaurusDeploy["docusaurus deploy"]
        
        DocusaurusDeploy --> GitOperations["Git Operations"]
        GitOperations --> CheckoutGHPages["git checkout gh-pages"]
        CheckoutGHPages --> CopyBuild["Copy build/ to gh-pages"]
        CopyBuild --> CommitGHPages["git commit + push gh-pages"]
    end
    
    subgraph "GitHub Pages"
        CommitGHPages --> GHPagesServe["GitHub Pages Server"]
        GHPagesServe --> LiveSite["https://microsoft.github.io/SynapseML/"]
    end
    
    subgraph "Post-Deployment"
        LiveSite --> AlgoliaCrawl["Algolia Crawler Updates Search Index"]
        LiveSite --> CDN["CDN Distribution"]
    end
```

**Deployment Configuration**

The site is configured for GitHub Pages deployment in [website/docusaurus.config.js:9-13]():

```javascript
url: 'https://microsoft.github.io',
baseUrl: '/SynapseML/',
organizationName: 'microsoft',
projectName: 'SynapseML',
trailingSlash: true,
```

Key deployment settings:
- **URL**: `https://microsoft.github.io`
- **Base URL**: `/SynapseML/` (project path)
- **Organization**: `microsoft`
- **Project**: `SynapseML`
- **Trailing Slash**: Required for GitHub Pages compatibility

**Static Site Characteristics**:
- Fully pre-rendered HTML (no server-side rendering required)
- Optimized JavaScript bundles with code-splitting
- Optimized CSS with minification
- Asset optimization (images, fonts)
- Service worker for offline support (optional)

**Deployment Triggers**:
1. Manual deployment via `npm run deploy`
2. Automated CI/CD pipeline deployment (via Azure DevOps or GitHub Actions)

After deployment, the Algolia crawler automatically indexes the new content for search.

Sources: [website/docusaurus.config.js:9-14](), [website/package.json:12]()

## Content Pipeline

Docusaurus processes multiple content types through a unified pipeline that converts them into static HTML pages.

**Content Processing Flow**

```mermaid
flowchart TD
    subgraph "Content Sources"
        Markdown[".md Files"]
        MDX[".mdx Files"]
        Notebooks[".ipynb Files"]
        ReactPages[".js React Pages"]
    end
    
    subgraph "Parsing Stage"
        Markdown --> MDXParser["MDX Parser"]
        MDX --> MDXParser
        Notebooks --> NotebookPlugin["Notebook Plugin"]
        ReactPages --> ReactCompiler["React Compiler"]
        
        NotebookPlugin --> ConvertToMD["Convert to Markdown"]
        ConvertToMD --> MDXParser
    end
    
    subgraph "Plugin Processing"
        MDXParser --> RemarkPlugins["Remark Plugins"]
        RemarkPlugins --> RemarkMath["remark-math: Parse LaTeX"]
        RemarkMath --> RehypePlugins["Rehype Plugins"]
        RehypePlugins --> RehypeKatex["rehype-katex: Render Math"]
    end
    
    subgraph "Component Rendering"
        RehypeKatex --> ReactComponents["Generate React Components"]
        ReactCompiler --> ReactComponents
        
        ReactComponents --> CustomComponents["Import Custom Components"]
        CustomComponents --> CodeSnippet["<CodeSnippet />"]
        CustomComponents --> SampleSnippet["<SampleSnippet />"]
    end
    
    subgraph "Static Generation"
        ReactComponents --> SSR["Server-Side Rendering"]
        SSR --> HTML["Static HTML"]
        SSR --> Hydration["Client-Side Hydration"]
    end
    
    HTML --> OutputFiles["build/ Output"]
    Hydration --> OutputFiles
```

**Markdown/MDX Processing**:

Standard markdown and MDX files are processed through:
1. **remark-math** plugin ([website/docusaurus.config.js:141]()): Parses LaTeX math expressions (e.g., `$f(x) = x^2$`)
2. **rehype-katex** plugin ([website/docusaurus.config.js:142]()): Renders LaTeX using KaTeX library
3. MDX component imports: Allows embedding React components in markdown

**Jupyter Notebook Processing**:

Jupyter notebooks (.ipynb) are automatically:
1. Converted to markdown format
2. Code cells rendered as syntax-highlighted code blocks
3. Output cells preserved as images or text
4. Frontmatter metadata extracted for page metadata

**React Page Processing**:

React pages in `src/pages/` are:
1. Compiled as standard React components
2. Server-side rendered for initial page load
3. Hydrated on client-side for interactivity

**External API Documentation**:

Python and Scala API documentation is:
- Generated separately using Sphinx and Scaladoc
- Uploaded to Azure Blob Storage
- Linked from navbar ([website/docusaurus.config.js:54-66]())

Sources: [website/docusaurus.config.js:139-143](), [website/docusaurus.config.js:18-24]()

## Redirect Management

The website maintains backward compatibility with legacy URLs through a comprehensive redirect system using the `@docusaurus/plugin-client-redirects` plugin.

**Redirect Configuration**

Configured in [website/docusaurus.config.js:160-479](), the redirect system handles 100+ URL mappings:

```javascript
{
  '@docusaurus/plugin-client-redirects',
  {
    redirects: [
      {
        to: '/docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks/',
        from: '/docs/features/cognitive_services/CognitiveServices%20-%20Create%20Audiobooks/',
      },
      {
        to: '/docs/Overview/',
        from: '/docs/about/',
      },
      // ... 100+ more redirects
    ],
  },
}
```

**Redirect Categories**:

1. **Documentation reorganization**: Old feature paths → New algorithm exploration paths
2. **Version migration**: 0.9.4, 0.10.0, 0.11.0 paths → Current version paths
3. **Naming changes**: "CognitiveServices" → "AI Services", "about" → "Overview"
4. **URL encoding fixes**: Spaces and special characters in URLs

**Redirect Implementation**:

The plugin generates client-side redirects that:
1. Match the `from` URL pattern
2. Perform instant browser redirect to `to` URL
3. Preserve query parameters and hash fragments
4. Work with static hosting (no server-side redirects required)

This extensive redirect system ensures:
- External links continue to work
- Search engine indexed pages redirect properly
- Bookmarks from old documentation remain functional
- Smooth migration path for users upgrading SynapseML versions

Sources: [website/docusaurus.config.js:160-479](), [website/package.json:19]()

## Dependencies and Package Management

The website uses Yarn for deterministic dependency management with lockfile-based resolution.

**Core Dependencies**

Key packages from [website/package.json:17-38]():

| Package | Version | Purpose |
|---------|---------|---------|
| `@docusaurus/core` | 2.4.1 | Core Docusaurus framework |
| `@docusaurus/preset-classic` | 2.4.1 | Classic documentation preset |
| `@docusaurus/theme-classic` | 2.4.1 | Default theme |
| `@docusaurus/theme-search-algolia` | 2.4.1 | Algolia search integration |
| `@docusaurus/plugin-client-redirects` | 2.4.1 | Client-side redirects |
| `react` | 16.8.4 | React library |
| `react-dom` | 16.8.4 | React DOM rendering |
| `remark-math` | 3 | LaTeX math parsing |
| `rehype-katex` | 4 | KaTeX math rendering |
| `prism-react-renderer` | - | Syntax highlighting |

**Security Resolutions**

The package includes security resolutions for vulnerable dependencies ([website/package.json:39-52]()):

```javascript
"resolutions": {
  "@docusaurus/core/**/set-value": "^4.0.1",
  "@docusaurus/**/trim": "^0.0.3",
  "@docusaurus/**/ansi-html-community": "^0.0.8",
  "@docusaurus/**/browserslist": "^4.16.5",
  "node-fetch": "^2.6.7",
  "minimatch": "^3.0.5",
  // ...
}
```

These resolutions override transitive dependencies to patch known security vulnerabilities.

**Dependency Lockfile**

The `yarn.lock` file ([website/yarn.lock:1-40000+]()) contains exact version pins for all dependencies and their transitive dependencies, ensuring:
- Reproducible builds across environments
- Protection against supply chain attacks
- Consistent behavior in CI/CD pipelines

Sources: [website/package.json:17-52](), [website/yarn.lock:1-100]()

## Versioning System

The website supports multiple versions of documentation corresponding to different SynapseML releases. This functionality is configured in `docusaurus.config.js`:

- Version dropdown in the navigation bar allows users to switch between versions
- Current version is defined as `1.0.11` in the configuration
- API documentation links point to versioned documentation

This versioning system ensures users can access documentation specific to their installed SynapseML version.

Sources: [website/docusaurus.config.js:4-4](), [website/docusaurus.config.js:45-52](), [tools/docker/demo/Dockerfile:3-3]()

## Redirects Management

The website uses the `@docusaurus/plugin-client-redirects` plugin to manage URL redirects from old documentation paths to new ones. This ensures that links from external sources or bookmarks continue to work even after documentation reorganization.

The redirects are configured in the `docusaurus.config.js` file with numerous mappings for legacy URLs.

Sources: [website/docusaurus.config.js:159-477]()

## Conclusion

The SynapseML website is designed as a comprehensive documentation platform built on modern web technologies. Its modular architecture, organized content structure, and custom components provide an effective user experience for both beginners and advanced users of the SynapseML library.

For information about the SynapseML library itself, refer to the [Overview](1) page. For details on the CI/CD infrastructure that builds and deploys the website, see the [CI/CD Pipeline](3.1) page.

---

# Page: Homepage and Components

# Homepage and Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/src/pages/index.js](website/src/pages/index.js)

</details>



## Purpose and Scope

This document describes the SynapseML website homepage implementation, including its React component structure, content organization, and the various sections that present SynapseML capabilities and installation instructions to visitors. The homepage serves as the primary entry point for users and showcases code examples, key features, and platform-specific installation guides.

For the overall website architecture and build process, see [Website Architecture](#7.1). For example notebooks that provide deeper technical content, see [Example Notebooks](#7.3).

---

## Homepage Structure Overview

The homepage is implemented as a React component in [website/src/pages/index.js:158-433]() and consists of five main sections that render sequentially from top to bottom.

```mermaid
graph TB
    HomePage["Home() Component<br/>(index.js:158)"]
    
    subgraph "Page Sections (Render Order)"
        HeroBanner["Hero Banner<br/>Title + Logo + CTA<br/>(index.js:167-193)"]
        Announcement["Announcement Banner<br/>MMLSpark Rename Notice<br/>(index.js:196-204)"]
        CodeSnippets["Code Snippet Showcase<br/>Tabbed Examples<br/>(index.js:206-230)"]
        Features["Features Grid<br/>4 Key Features<br/>(index.js:231-241)"]
        Installation["Installation Section<br/>7 Platform Options<br/>(index.js:242-427)"]
    end
    
    subgraph "Data Sources"
        SnippetsArray["snippets[]<br/>(index.js:14-85)"]
        FeaturesArray["features[]<br/>(index.js:87-137)"]
    end
    
    subgraph "Docusaurus Framework"
        Layout["Layout Component<br/>@theme/Layout"]
        SiteConfig["siteConfig<br/>useDocusaurusContext()"]
        BaseUrl["useBaseUrl()<br/>Asset Resolution"]
    end
    
    HomePage --> Layout
    HomePage --> SiteConfig
    HomePage --> BaseUrl
    
    Layout --> HeroBanner
    Layout --> Announcement
    Layout --> CodeSnippets
    Layout --> Features
    Layout --> Installation
    
    SnippetsArray --> CodeSnippets
    FeaturesArray --> Features
    
    SiteConfig --> HeroBanner
```

**Sources:** [website/src/pages/index.js:1-433]()

---

## React Component Hierarchy

The homepage uses a combination of custom and Docusaurus-provided React components organized in a hierarchical structure.

```mermaid
graph TB
    Home["Home<br/>(index.js:158)"]
    Layout["Layout<br/>Docusaurus @theme/Layout"]
    
    subgraph "Custom Components"
        Feature["Feature<br/>(index.js:139-156)"]
        CodeSnippet["CodeSnippet<br/>@site/src/theme/CodeSnippet"]
        SampleSnippet["SampleSnippet<br/>@site/src/theme/SampleSnippet"]
    end
    
    subgraph "Docusaurus Components"
        Tabs["Tabs<br/>@theme/Tabs"]
        TabItem["TabItem<br/>@theme/TabItem"]
        Link["Link<br/>@docusaurus/Link"]
    end
    
    Home --> Layout
    Layout --> Feature
    Layout --> Tabs
    
    Tabs --> TabItem
    TabItem --> SampleSnippet
    TabItem --> CodeSnippet
    
    SampleSnippet --> CodeSnippet
    Feature --> Link
```

**Component Responsibilities:**

| Component | Purpose | Location |
|-----------|---------|----------|
| `Home` | Root homepage component | [index.js:158-433]() |
| `Layout` | Docusaurus page wrapper with header/footer | Imported at [index.js:3]() |
| `Feature` | Renders individual feature cards with icon and description | [index.js:139-156]() |
| `CodeSnippet` | Displays formatted code with syntax highlighting | Imported at [index.js:8]() |
| `SampleSnippet` | Wraps code snippets with "Further Reading" links | Imported at [index.js:9]() |
| `Tabs` | Container for tabbed interface | Imported at [index.js:10]() |
| `TabItem` | Individual tab content | Imported at [index.js:11]() |

**Sources:** [website/src/pages/index.js:1-12](), [website/src/pages/index.js:139-156]()

---

## Hero Banner Section

The hero banner is the first visible section, presenting the SynapseML branding and primary call-to-action.

```mermaid
graph LR
    HeroBanner["hero section<br/>(index.js:167)"]
    
    subgraph "Left Column (col--5)"
        Title["h1: siteConfig.title<br/>'SynapseML'"]
        Tagline["p: siteConfig.tagline<br/>'Simple and Distributed ML'"]
        GetStartedBtn["Link Button<br/>'Get Started'"]
    end
    
    subgraph "Right Column (col--5)"
        Logo["Logo SVG<br/>img/logo.svg"]
    end
    
    subgraph "Configuration"
        Context["useDocusaurusContext()"]
        SiteConfig["siteConfig object"]
    end
    
    HeroBanner --> Title
    HeroBanner --> Tagline
    HeroBanner --> GetStartedBtn
    HeroBanner --> Logo
    
    Context --> SiteConfig
    SiteConfig --> Title
    SiteConfig --> Tagline
    
    GetStartedBtn -.->|navigates to| InstallDocs["docs/Get Started/Install SynapseML"]
    Logo -.->|resolved by| UseBaseUrl["useBaseUrl('img/logo.svg')"]
```

The hero banner uses a two-column Bootstrap grid layout ([index.js:169-191]()):
- **Left column**: Title, tagline, and "Get Started" button
- **Right column**: SynapseML logo image

The button links to the installation documentation using [index.js:179]() with the path `"docs/Get%20Started/Install%20SynapseML"`.

**Sources:** [website/src/pages/index.js:167-193]()

---

## Code Snippet Showcase

The code snippet showcase demonstrates SynapseML capabilities through five tabbed Python examples, each highlighting a different module.

```mermaid
graph TB
    SnippetsSection["Code Snippets Section<br/>(index.js:209-227)"]
    
    subgraph "Data Structure: snippets[] (index.js:14-85)"
        Snippet1["Cognitive Services<br/>TextSentiment<br/>(index.js:16-28)"]
        Snippet2["Deep Learning<br/>ONNXModel<br/>(index.js:31-41)"]
        Snippet3["Responsible AI<br/>TabularSHAP<br/>(index.js:44-55)"]
        Snippet4["LightGBM<br/>LightGBMRegressor<br/>(index.js:58-69)"]
        Snippet5["OpenCV<br/>ImageTransformer<br/>(index.js:72-84)"]
    end
    
    subgraph "Rendering Components"
        TabsComponent["Tabs<br/>defaultValue: 'Cognitive Services'"]
        TabItemComponents["TabItem (x5)<br/>One per snippet"]
        SampleSnippetComponents["SampleSnippet<br/>Renders code + link"]
    end
    
    SnippetsSection --> TabsComponent
    
    Snippet1 --> TabItemComponents
    Snippet2 --> TabItemComponents
    Snippet3 --> TabItemComponents
    Snippet4 --> TabItemComponents
    Snippet5 --> TabItemComponents
    
    TabsComponent --> TabItemComponents
    TabItemComponents --> SampleSnippetComponents
    
    SampleSnippetComponents -.->|props| SnippetProps["label, further, config"]
```

Each snippet object in the array ([index.js:14-85]()) contains three properties:

| Property | Type | Purpose | Example |
|----------|------|---------|---------|
| `label` | String | Tab display name | `"Cognitive Services"` |
| `further` | String | Link to detailed documentation | `"docs/Explore%20Algorithms/AI%20Services/Overview#text-analytics-sample"` |
| `config` | String | Python code example | Multi-line code string |

The `SampleSnippet` component wraps each code example and adds a "Further Reading" link that navigates to the documentation specified in the `further` property ([index.js:219-222]()).

**Example Snippet Structure:**

The Cognitive Services example ([index.js:16-28]()) demonstrates the `TextSentiment` transformer:
```python
from synapse.ml.cognitive import *

sentiment_df = (TextSentiment()
    .setTextCol("text")
    .setLocation("eastus")
    .setSubscriptionKey(key)
    .setOutputCol("sentiment")
    .setErrorCol("error")
    .setLanguageCol("language")
    .transform(input_df))
```

**Sources:** [website/src/pages/index.js:14-85](), [website/src/pages/index.js:209-227]()

---

## Features Section

The features section presents four key value propositions of SynapseML in a responsive grid layout.

```mermaid
graph TB
    FeaturesSection["Features Section<br/>(index.js:231-241)"]
    
    subgraph "Data Structure: features[] (index.js:87-137)"
        Feature1["Simple<br/>img/simple.svg<br/>'Quick creation in few lines'"]
        Feature2["Scalable<br/>img/scalable.svg<br/>'Scale to hundreds of machines'"]
        Feature3["Multilingual<br/>img/multilingual.svg<br/>'Python, Scala, R, Java, .NET, C#'"]
        Feature4["Open<br/>img/open_source.svg<br/>'Open Source, any Spark 3 infra'"]
    end
    
    subgraph "Rendering"
        FeatureComponent["Feature Component<br/>(index.js:139-156)"]
        GridRow["Bootstrap Row<br/>4 col--6 columns"]
    end
    
    FeaturesSection --> GridRow
    
    Feature1 --> FeatureComponent
    Feature2 --> FeatureComponent
    Feature3 --> FeatureComponent
    Feature4 --> FeatureComponent
    
    GridRow --> FeatureComponent
    
    FeatureComponent -.->|renders| FeatureElements["Image + Title + Description"]
```

The `Feature` component ([index.js:139-156]()) is a functional React component that accepts three props:

```javascript
function Feature({ imageUrl, title, description })
```

Each feature object in the array contains:

| Feature | Image | Key Message |
|---------|-------|-------------|
| **Simple** | `img/simple.svg` | "Quickly create, train, and use distributed machine learning tools in only a few lines of code" |
| **Scalable** | `img/scalable.svg` | "Scale ML workloads to hundreds of machines on your Apache Spark cluster" |
| **Multilingual** | `img/multilingual.svg` | "Use SynapseML from any Spark compatible language including Python, Scala, R, Java, .NET and C#" |
| **Open** | `img/open_source.svg` | "Open Source and can be installed and used on any Spark 3 infrastructure" |

The features are rendered in a responsive grid using Bootstrap classes `col col--6` ([index.js:142]()), creating a 2x2 layout on larger screens that collapses to single column on mobile devices.

**Sources:** [website/src/pages/index.js:87-137](), [website/src/pages/index.js:139-156](), [website/src/pages/index.js:231-241]()

---

## Installation Section

The installation section provides platform-specific installation instructions through a tabbed interface supporting seven different deployment scenarios.

```mermaid
graph TB
    InstallSection["Installation Section<br/>(index.js:242-427)"]
    
    subgraph "Platform Tabs"
        Synapse["Synapse Tab<br/>Spark 3.5 & 3.4<br/>(index.js:263-295)"]
        Fabric["Fabric Tab<br/>Pre-installed<br/>(index.js:296-312)"]
        SparkPkg["Spark Packages Tab<br/>spark-submit<br/>(index.js:313-330)"]
        Databricks["Databricks Tab<br/>Maven coordinates<br/>(index.js:331-373)"]
        Docker["Docker Tab<br/>mcr.microsoft.com<br/>(index.js:374-395)"]
        Python["Python Tab<br/>pip + pyspark<br/>(index.js:396-414)"]
        SBT["SBT Tab<br/>build.sbt config<br/>(index.js:415-423)"]
    end
    
    subgraph "Rendering Components"
        TabsWrapper["Tabs Component<br/>defaultValue: 'Fabric'"]
        TabItems["TabItem (x7)<br/>One per platform"]
        CodeSnippets["CodeSnippet Components<br/>Syntax highlighting"]
    end
    
    InstallSection --> TabsWrapper
    
    TabsWrapper --> Synapse
    TabsWrapper --> Fabric
    TabsWrapper --> SparkPkg
    TabsWrapper --> Databricks
    TabsWrapper --> Docker
    TabsWrapper --> Python
    TabsWrapper --> SBT
    
    Synapse --> TabItems
    Fabric --> TabItems
    SparkPkg --> TabItems
    Databricks --> TabItems
    Docker --> TabItems
    Python --> TabItems
    SBT --> TabItems
    
    TabItems --> CodeSnippets
```

### Platform-Specific Configuration Details

#### Synapse Configuration

The Synapse tab ([index.js:263-295]()) provides two separate configurations:

**Spark 3.5 Pools** ([index.js:265-279]()):
- Package: `com.microsoft.azure:synapseml_2.12:1.1.0`
- Repository: `https://mmlspark.azureedge.net/maven`
- Configuration applied via `%%configure -f` magic command
- Includes JAR excludes and classpath settings

**Spark 3.4 Pools** ([index.js:280-294]()):
- Package: `com.microsoft.azure:synapseml_2.12:1.0.15`
- Same repository and configuration pattern

#### Fabric Configuration

The Fabric tab ([index.js:296-312]()) notes that SynapseML is pre-installed but provides configuration for overriding the version:
- Uses template placeholder: `[THE_SYNAPSEML_VERSION_YOU_WANT]`
- Same configuration structure as Synapse

#### Databricks Configuration

The Databricks tab ([index.js:331-373]()) provides:
- **Spark 3.5**: `com.microsoft.azure:synapseml_2.12:1.1.0` ([index.js:346-349]())
- **Spark 3.4**: `com.microsoft.azure:synapseml_2.12:1.0.15` ([index.js:350-354]())
- Maven resolver: `https://mmlspark.azureedge.net/maven` ([index.js:356-359]())
- Example notebooks archive: `https://mmlspark.blob.core.windows.net/dbcs/SynapseMLExamplesv1.1.0.dbc` ([index.js:369-372]())

#### Docker Configuration

The Docker tab ([index.js:374-395]()) provides:
- Container run command: `docker run -it -p 8888:8888 -e ACCEPT_EULA=yes mcr.microsoft.com/mmlspark/release` ([index.js:377-379]())
- Jupyter accessible at `http://localhost:8888` ([index.js:383]())
- EULA command: `docker run -it -p 8888:8888 mcr.microsoft.com/mmlspark/release eula` ([index.js:391-393]())

#### Python Standalone Configuration

The Python tab ([index.js:396-414]()) demonstrates:
1. Install PySpark: `pip install pyspark` ([index.js:399-401]())
2. Configure SparkSession with packages ([index.js:405-411]():
   ```python
   import pyspark
   spark = (pyspark.sql.SparkSession.builder.appName("MyApp")
           .config("spark.jars.packages", "com.microsoft.azure:synapseml_2.12:1.1.0")
           .config("spark.jars.repositories", "https://mmlspark.azureedge.net/maven")
           .getOrCreate())
   import synapse.ml
   ```

#### SBT Configuration

The SBT tab ([index.js:415-423]()) provides `build.sbt` configuration:
```scala
resolvers += "SynapseML" at "https://mmlspark.azureedge.net/maven"
libraryDependencies += "com.microsoft.azure" %% "synapseml_2.12" % "1.1.0"
```

**Sources:** [website/src/pages/index.js:242-427]()

---

## Version Management Strategy

The installation instructions embed specific version numbers directly in the code examples, requiring manual updates when new versions are released.

| Spark Version | SynapseML Version | Scala Version | Context |
|---------------|-------------------|---------------|---------|
| 3.5.x | 1.1.0 | 2.12 | Current recommended version |
| 3.4.x | 1.0.15 | 2.12 | Legacy support version |

The homepage uses consistent version patterns across all platform tabs:
- **Maven coordinates**: `com.microsoft.azure:synapseml_2.12:{version}`
- **Maven repository**: `https://mmlspark.azureedge.net/maven` (all platforms)
- **Docker tag**: `mcr.microsoft.com/mmlspark/release` (no version specified, uses latest)

Comments in the code snippets ([index.js:317](), [index.js:408](), [index.js:420]()) remind users to select the appropriate version based on their Spark version.

**Sources:** [website/src/pages/index.js:263-423]()

---

## Styling and CSS Modules

The homepage uses CSS modules for scoped styling, imported at [index.js:7]():

```javascript
import styles from "./index.module.css";
```

The styles object provides classnames applied throughout the component:

| CSS Class | Applied To | Purpose |
|-----------|-----------|---------|
| `styles.heroBanner` | Hero header section | Banner background and layout |
| `styles.heroImg` | Logo image | Logo sizing and positioning |
| `styles.buttons` | Button container | CTA button spacing |
| `styles.getStarted` | Get Started button | Button styling override |
| `styles.announcement` | Announcement banner | Banner background |
| `styles.announcementDark` | Announcement banner | Dark theme styling |
| `styles.announcementInner` | Announcement content | Content padding and alignment |
| `styles.configSnippets` | Snippets section | Section spacing |
| `styles.configSnippet` | Individual snippet | Snippet container styling |
| `styles.features` | Features section | Grid section spacing |
| `styles.feature` | Individual feature | Feature card styling |
| `styles.featureImage` | Feature icons | Icon sizing and spacing |
| `styles.pitch` | Installation section | Section text styling |

The component also uses the `classnames` utility ([index.js:2]()) and its alias `clsx` ([index.js:12]()) for conditional and combined class application, particularly in [index.js:142](), [index.js:167](), and [index.js:196]().

**Sources:** [website/src/pages/index.js:1-12](), [website/src/pages/index.js:142](), [website/src/pages/index.js:167](), [website/src/pages/index.js:196]()

---

## Metadata and SEO

The `Layout` component wraps the entire page and provides metadata for search engines and social media ([index.js:162-166]()):

```javascript
<Layout
  title={`${siteConfig.title}`}
  description="Simple and Distributed Machine Learning"
  keywords={["SynapseML", "Machine Learning"]}
>
```

This configuration sets:
- **Page title**: Derived from site configuration
- **Meta description**: "Simple and Distributed Machine Learning"
- **Keywords**: `["SynapseML", "Machine Learning"]`

The Docusaurus Layout component automatically generates appropriate `<meta>` tags for SEO, Open Graph, and Twitter Cards based on these props.

**Sources:** [website/src/pages/index.js:162-166]()

---

## Responsive Design Considerations

The homepage implements responsive layouts using Bootstrap's grid system:

1. **Hero Banner** ([index.js:169-191]()): Two-column layout with offset
   - Desktop: Side-by-side title/logo layout
   - Mobile: Stacked vertical layout (automatic via Bootstrap)

2. **Features Grid** ([index.js:234-238]()): Four features in `col--6` columns
   - Desktop/Tablet: 2x2 grid
   - Mobile: Single column stack

3. **Code Snippets and Installation**: Full-width containers
   - Tabs remain functional across all screen sizes
   - Code blocks scroll horizontally when needed

The `col--5`, `col--6`, and `col--offset-1` Bootstrap classes handle responsive breakpoints automatically.

**Sources:** [website/src/pages/index.js:169-238]()

---

# Page: Example Notebooks

# Example Notebooks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb](docs/Explore Algorithms/Vowpal Wabbit/Quickstart - Classification using VW-native Format.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)
- [website/docusaurus.config.js](website/docusaurus.config.js)
- [website/package.json](website/package.json)
- [website/src/theme/CodeSnippet/index.js](website/src/theme/CodeSnippet/index.js)
- [website/src/theme/NotFound/index.js](website/src/theme/NotFound/index.js)
- [website/src/theme/SampleSnippet/index.js](website/src/theme/SampleSnippet/index.js)
- [website/yarn.lock](website/yarn.lock)

</details>



Example notebooks in SynapseML provide practical demonstrations of how to use the library's features across various machine learning and AI scenarios. These notebooks serve as hands-on tutorials to help users understand implementation patterns and best practices for using SynapseML.

For information about installing SynapseML in your environment, please see [Install SynapseML](#2.2).

## Organization of Example Notebooks

SynapseML example notebooks are organized into categories based on functionality and service integration:

```mermaid
graph TD
    root["Example Notebooks"]
    aiServices["AI Services"]
    openai["OpenAI"]
    anomaly["Anomaly Detection"]
    class["Classification"]
    deep["Deep Learning"]
    causal["Causal Inference"]
    
    root --> aiServices
    root --> openai
    root --> anomaly
    root --> class
    root --> deep
    root --> causal
    
    aiServices --> ai1["Document QA with PDFs"]
    aiServices --> ai2["Advanced Usage (Async/Batching)"]
    aiServices --> ai3["Create Audiobooks"]
    aiServices --> ai4["Multivariate Anomaly Detection"]
    
    openai --> o1["Azure OpenAI Basics"]
    openai --> o2["LangChain Integration"]
    openai --> o3["Embeddings & Vector Search"]
    openai --> o4["Form Understanding & Search"]
    
    anomaly --> an1["Isolation Forests"]
    
    class --> c1["SparkML vs SynapseML"]
    
    deep --> d1["ONNX Model Inference"]
    
    causal --> ca1["Measure Causal Effects"]
```

Sources: [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](), [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](), [docs/Explore Algorithms/AI Services/Overview.ipynb](), [docs/Explore Algorithms/Anomaly Detection/Quickstart - Isolation Forests.ipynb](), [docs/Explore Algorithms/OpenAI/Langchain.ipynb]()

## Key Notebook Categories

### AI Services Notebooks

These notebooks demonstrate integration with Azure AI Services for tasks like language understanding, computer vision, and document intelligence.

Key examples include:
- **Document QA with PDFs** - Builds a question-answering system using PDF content
- **Advanced Usage** - Demonstrates async processing, batching, and multi-key scenarios
- **Create Audiobooks** - Shows text-to-speech capabilities

```mermaid
flowchart TD
    subgraph "AI Services Integration"
        Data["Input Data"] --> FormRecognizer["AnalyzeDocument<br>AnalyzeInvoices"]
        FormRecognizer --> ProcessedData["Extracted Content"]
        ProcessedData --> TextSplitter["PageSplitter"]
        TextSplitter --> Chunks["Document Chunks"]
        Chunks --> Search["Azure Cognitive Search"]
        Query["User Query"] --> Embedding["Embedding Generation"]
        Embedding --> VectorSearch["Vector Search"]
        VectorSearch --> RetrievedChunks["Retrieved Context"]
        RetrievedChunks --> QAGenerator["Question Answering"]
        QAGenerator --> Answer["Generated Answer"]
    end
```

Sources: [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](), [docs/Explore Algorithms/AI Services/Advanced Usage - Async, Batching, and Multi-Key.ipynb]()

### OpenAI Notebooks

These notebooks demonstrate how to use Azure OpenAI models with SynapseML for text generation, embeddings, and language model applications.

Key examples include:
- **OpenAI Basics** - Shows fundamental OpenAI integration
- **LangChain** - Demonstrates using the LangchainTransformer for complex workflows
- **Embeddings** - Shows how to generate and use embeddings

```mermaid
flowchart LR
    subgraph "OpenAI Integration"
        direction LR
        InputDF["Spark DataFrame<br>with text"] --> Transformer["OpenAIEmbedding<br>OpenAIChatCompletion"]
        Transformer --> OutputDF["DataFrame with<br>embeddings/completions"]
        
        BatchInput["Batch Data"] --> MiniBatcher["FixedMiniBatchTransformer"]
        MiniBatcher --> BatchTransformer["OpenAI Transformer"]
        BatchTransformer --> BatchOutput["Processed Results"]
        
        LCInput["Input Data"] --> LCTransformer["LangchainTransformer"]
        Chain["LangChain Chain"] --> LCTransformer
        LCTransformer --> LCOutput["Chain Results"]
    end
```

Sources: [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](), [docs/Explore Algorithms/OpenAI/Langchain.ipynb](), [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb]()

### Anomaly Detection Notebooks

These notebooks show how to implement anomaly detection using SynapseML.

Key examples include:
- **Isolation Forests** - Demonstrates multivariate anomaly detection

```mermaid
flowchart TD
    subgraph "Anomaly Detection"
        Data["Time Series Data"] --> TrainTest["Train/Test Split"]
        TrainTest --> ModelTraining["IsolationForest Training"]
        ModelTraining --> ScoredData["Anomaly Scores"]
        ScoredData --> Visualization["Anomaly Visualization"]
    end
```

Sources: [docs/Explore Algorithms/Anomaly Detection/Quickstart - Isolation Forests.ipynb]()

## Common Code Patterns

### Platform Detection and Secret Management

Example notebooks use the `Platform` module to detect the runtime environment and securely access API keys:

```python
from synapse.ml.core.platform import find_secret, current_platform

# Get the current platform (Synapse, Databricks, Fabric, etc.)
platform = current_platform()

# Securely retrieve API keys
service_key = find_secret(
    secret_name="ai-services-api-key", keyvault="your-keyvault-name"
)
```

Sources: [core/src/main/python/synapse/ml/core/platform/Platform.py:17-92]()

### Transformer Configuration

Notebooks consistently demonstrate the fluent API for configuring transformers:

```python
# OpenAI embedding example
embedding = (
    OpenAIEmbedding()
    .setSubscriptionKey(key)
    .setDeploymentName(deployment_name_embeddings)
    .setCustomServiceName(service_name)
    .setTextCol("prompt")
    .setErrorCol("error")
    .setOutputCol("embeddings")
)

result_df = embedding.transform(df)
```

Sources: [docs/Explore Algorithms/OpenAI/OpenAI.ipynb:194-206]()

### Asynchronous Processing

Many notebooks demonstrate how to improve throughput using asynchronous processing:

```python
# Set concurrency level for parallel requests
analyzer = (
    AnalyzeImage()
    .setLocation(service_loc)
    .setSubscriptionKey(service_key)
    .setVisualFeatures(["Categories", "Description"])
    .setConcurrency(3)  # Process 3 requests in parallel
)
```

Sources: [docs/Explore Algorithms/AI Services/Advanced Usage - Async, Batching, and Multi-Key.ipynb:244-257]()

### Request Batching

Notebooks show how to batch requests for improved efficiency:

```python
# Batch processing example
sentiment = (
    AnalyzeText()
    .setKind("SentimentAnalysis")
    .setTextCol("text")
    .setSubscriptionKey(service_key)
    .setOutputCol("sentiment")
    .setBatchSize(10)  # Process 10 texts in a single API call
)
```

Sources: [docs/Explore Algorithms/AI Services/Advanced Usage - Async, Batching, and Multi-Key.ipynb:316-327]()

### Logging and Telemetry

Advanced examples utilize SynapseML's logging system:

```python
from synapse.ml.core.logging.SynapseMLLogger import SynapseMLLogger

class MyTransformer(SynapseMLLogger):
    def __init__(self):
        super().__init__()
        
    @SynapseMLLogger.log_transform()
    def transform(self, df):
        # Transform logic here
        return result_df
```

Sources: [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py:185-216](), [core/src/test/python/synapsemltest/core/test_logging.py:16-35]()

## Platform Integration Architecture

SynapseML example notebooks are designed to work across different platforms, with built-in utilities to handle platform-specific functionality:

```mermaid
graph TD
    subgraph "Platform Integration"
        Notebook["Example Notebook"] --> Platform["Platform.py"]
        Platform --> ENV["Environment Detection"]
        ENV --> E1["Synapse"]
        ENV --> E2["Databricks"]
        ENV --> E3["Fabric"]
        ENV --> E4["Local/Binder"]
        
        Notebook --> Logger["SynapseMLLogger.py"]
        Logger --> L1["Standard Logging"]
        Logger --> L2["Platform-specific Logging"]
        
        Notebook --> SecretMgmt["Secret Management"]
        SecretMgmt --> S1["Azure KeyVault"]
        SecretMgmt --> S2["Databricks Secrets"]
        SecretMgmt --> S3["Local Keys"]
        
        Notebook --> Transformers["SynapseML Transformers"]
        Transformers --> AI["AI Services Integration"]
        Transformers --> OpenAI["OpenAI Integration"]
        Transformers --> MLAlgos["ML Algorithms"]
    end
```

Sources: [core/src/main/python/synapse/ml/core/platform/Platform.py](), [core/src/main/python/synapse/ml/core/logging/SynapseMLLogger.py]()

## Example Notebook Workflow

SynapseML example notebooks typically follow this workflow pattern:

```mermaid
flowchart TD
    subgraph "Example Notebook Workflow"
        direction TB
        I["1. Import Libraries"] --> S["2. Setup Environment"]
        S --> D["3. Load/Create Data"]
        D --> C["4. Configure Transformers"]
        C --> A["5. Apply Transformers"]
        A --> V["6. Visualize/Analyze Results"]
        
        S1["Platform Detection"] --> S
        S2["API Key Retrieval"] --> S
        S3["Service Configuration"] --> S
        
        D1["Local Data"] --> D
        D2["Remote Storage"] --> D
        D3["Generated Data"] --> D
        
        C1["Set Parameters"] --> C
        C2["Connect Services"] --> C
        
        A1["Single Transform"] --> A
        A2["Pipeline"] --> A
        
        V1["Display DataFrame"] --> V
        V2["Export Results"] --> V
    end
```

Sources: [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](), [docs/Explore Algorithms/OpenAI/OpenAI.ipynb](), [docs/Explore Algorithms/OpenAI/Langchain.ipynb]()

## Running Example Notebooks

To run SynapseML example notebooks:

1. Set up a computing environment (Fabric, Synapse, Databricks, etc.)
2. Install SynapseML if needed (see [Install SynapseML](#2.2))
3. Set up required service resources (Azure OpenAI, Azure AI Services, etc.)
4. Import the notebook to your environment
5. Provide API keys (directly or through key vault)
6. Execute the notebook cells sequentially

### Environment-Specific Considerations

The example notebooks use the `Platform.py` module to handle environment-specific requirements:

```python
# Platform detection example
from synapse.ml.core.platform import running_on_synapse, running_on_databricks

if running_on_synapse():
    # Synapse-specific code
elif running_on_databricks():
    # Databricks-specific code
else:
    # Generic handling
```

Sources: [core/src/main/python/synapse/ml/core/platform/Platform.py:37-54]()

## Conclusion

SynapseML example notebooks provide practical demonstrations of the library's capabilities, showing users how to integrate with various services and implement machine learning workflows at scale. They serve as both learning resources and code templates for developing your own solutions.

For specific examples, explore the notebooks in the [SynapseML GitHub repository](https://github.com/microsoft/SynapseML).

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of SynapseML deployment options, artifact distribution channels, and platform-specific configuration patterns. It covers the high-level deployment architecture and common configuration approaches across all supported platforms.

For detailed platform-specific instructions, see:
- [Installation and Distribution](#8.1) - artifact repositories and version management
- [Docker Environments](#8.2) - containerized deployments
- [Azure Synapse Deployment](#8.3) - Synapse Analytics Spark pools
- [Microsoft Fabric Deployment](#8.4) - Fabric notebooks and workloads
- [Databricks Deployment](#8.5) - Databricks clusters
- [Standalone and Other Platforms](#8.6) - Python standalone, spark-submit, SBT, HDInsight

For information about the build and release pipeline that produces deployment artifacts, see [CI/CD Pipeline](#3.1).

## Deployment Architecture

SynapseML supports deployment to multiple platforms through a centralized artifact distribution model. Artifacts are published to standard repositories (Maven, PyPI, Docker) and consumed by target platforms using platform-specific configuration mechanisms.

```mermaid
graph TB
    subgraph "Artifact Repositories"
        Maven["Maven Repository<br/>mmlspark.azureedge.net/maven"]
        PyPI["PyPI Registry<br/>synapseml package"]
        Docker["Docker Registry<br/>mcr.microsoft.com/mmlspark/release"]
    end
    
    subgraph "Configuration Mechanisms"
        JarsPackages["spark.jars.packages<br/>Maven coordinates"]
        PipInstall["pip install synapseml"]
        DockerRun["docker run"]
    end
    
    subgraph "Target Platforms"
        Synapse["Azure Synapse<br/>%%configure magic"]
        Fabric["Microsoft Fabric<br/>%%configure magic"]
        Databricks["Databricks<br/>Library installation"]
        Standalone["Python Standalone<br/>SparkSession.builder"]
        SparkSubmit["spark-submit<br/>--packages flag"]
        HDInsight["HDInsight/Livy<br/>%%configure magic"]
    end
    
    Maven --> JarsPackages
    PyPI --> PipInstall
    Docker --> DockerRun
    
    JarsPackages --> Synapse
    JarsPackages --> Fabric
    JarsPackages --> Databricks
    JarsPackages --> Standalone
    JarsPackages --> SparkSubmit
    JarsPackages --> HDInsight
    
    PipInstall --> Standalone
    DockerRun --> Standalone
```

**Deployment Architecture Flow**

Sources: [README.md:70-266]()

## Artifact Distribution Channels

SynapseML artifacts are distributed through four primary channels:

| Channel | Endpoint | Artifact Type | Primary Use Case |
|---------|----------|---------------|------------------|
| Maven | `https://mmlspark.azureedge.net/maven` | JAR files with dependencies | Spark cluster deployments |
| PyPI | `https://pypi.org/project/synapseml/` | Python wheel | Standalone Python installations |
| Docker | `mcr.microsoft.com/mmlspark/release` | Container images | Local development and evaluation |
| Blob Storage | `mmlspark.blob.core.windows.net` | API docs, notebooks, archives | Documentation and examples |

### Maven Coordinates

The primary distribution mechanism uses Maven coordinates in the format:

```
com.microsoft.azure:synapseml_2.12:<version>
```

Current stable version: `1.1.0`

Version-specific coordinates for different Spark versions:
- **Spark 3.5**: `com.microsoft.azure:synapseml_2.12:1.1.0`
- **Spark 3.4**: `com.microsoft.azure:synapseml_2.12:1.0.15`
- **Spark 3.3**: `com.microsoft.azure:synapseml_2.12:0.11.4-spark3.3`

Sources: [README.md:9, 106, 129, 145, 161, 181, 200, 211, 222, 236]()

### Docker Images

Docker images are published to Microsoft Container Registry:

```bash
docker run -it -p 8888:8888 -e ACCEPT_EULA=yes mcr.microsoft.com/mmlspark/release jupyter notebook
```

The image includes:
- Pre-configured Jupyter notebook server
- SynapseML with all dependencies
- Example notebooks at `/notebooks`

Sources: [README.md:242-254]()

## Common Configuration Parameters

All Spark-based deployments share a common set of configuration parameters:

```mermaid
graph LR
    subgraph "spark.jars Configuration"
        packages["spark.jars.packages<br/>Maven coordinates"]
        repos["spark.jars.repositories<br/>Custom Maven repo"]
        excludes["spark.jars.excludes<br/>Conflict resolution"]
    end
    
    subgraph "Spark Execution Config"
        classpath["spark.yarn.user.classpath.first<br/>true"]
        parquet["spark.sql.parquet.enableVectorizedReader<br/>false"]
    end
    
    packages --> repos
    packages --> excludes
    excludes --> classpath
    classpath --> parquet
```

**Configuration Parameter Dependencies**

### Required Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `spark.jars.packages` | `com.microsoft.azure:synapseml_2.12:<version>` | Specifies SynapseML Maven artifact |
| `spark.jars.repositories` | `https://mmlspark.azureedge.net/maven` | Custom Maven repository location |
| `spark.jars.excludes` | See exclusion list below | Prevents dependency conflicts |
| `spark.yarn.user.classpath.first` | `true` | Prioritizes user classpath over system |
| `spark.sql.parquet.enableVectorizedReader` | `false` | Disables vectorized reader for compatibility |

### Standard Exclusion List

```
org.scala-lang:scala-reflect
org.apache.spark:spark-tags_2.12
org.scalactic:scalactic_2.12
org.scalatest:scalatest_2.12
com.fasterxml.jackson.core:jackson-databind
```

These exclusions prevent conflicts with Spark's built-in dependencies, particularly in Livy-based environments (Synapse, HDInsight).

Sources: [README.md:103-113, 124-136, 140-152, 156-168, 232-240]()

## Platform Configuration Formats

Different platforms use different mechanisms to apply Spark configuration:

```mermaid
graph TB
    subgraph "Notebook Environments"
        ConfigMagic["%%configure -f magic<br/>JSON configuration"]
    end
    
    subgraph "Cluster Installation"
        LibraryUI["Library UI<br/>Maven coordinates"]
        PoolConfig["Pool Configuration<br/>Spark properties"]
    end
    
    subgraph "Command Line"
        SparkShell["spark-shell --packages"]
        PySpark["pyspark --packages"]
        Submit["spark-submit --packages"]
    end
    
    subgraph "Programmatic"
        BuilderConfig["SparkSession.builder<br/>.config()"]
        SBTDeps["build.sbt<br/>libraryDependencies"]
    end
    
    ConfigMagic --> |"Synapse, Fabric, Livy"| SparkCluster["Spark Cluster"]
    LibraryUI --> |"Databricks"| SparkCluster
    PoolConfig --> |"Synapse"| SparkCluster
    SparkShell --> SparkCluster
    PySpark --> SparkCluster
    Submit --> SparkCluster
    BuilderConfig --> |"Python Standalone"| SparkCluster
    SBTDeps --> |"Scala Build"| SparkCluster
```

**Platform Configuration Mechanism Mapping**

### Notebook Magic Configuration

Used by Azure Synapse, Microsoft Fabric, and HDInsight/Livy:

```json
%%configure -f
{
  "name": "synapseml",
  "conf": {
      "spark.jars.packages": "com.microsoft.azure:synapseml_2.12:1.1.0",
      "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
      "spark.jars.excludes": "<exclusion-list>",
      "spark.yarn.user.classpath.first": "true",
      "spark.sql.parquet.enableVectorizedReader": "false"
  }
}
```

The `-f` flag forces session recreation with new configuration.

Sources: [README.md:101-113, 124-136, 140-152, 156-168, 232-240]()

### Databricks Library Installation

Databricks uses a library installation UI with Maven coordinates:

```
Coordinates: com.microsoft.azure:synapseml_2.12:1.1.0
Repository: https://mmlspark.azureedge.net/maven
```

The library must be attached to target clusters. Databricks manages dependency resolution automatically.

Sources: [README.md:174-189]()

### Python Standalone Configuration

For standalone Python installations with PySpark:

```python
import pyspark
spark = pyspark.sql.SparkSession.builder.appName("MyApp") \
            .config("spark.jars.packages", "com.microsoft.azure:synapseml_2.12:1.1.0") \
            .getOrCreate()
import synapse.ml
```

Sources: [README.md:191-203]()

### Command Line Packages

For spark-submit, spark-shell, or pyspark:

```bash
spark-shell --packages com.microsoft.azure:synapseml_2.12:1.1.0
pyspark --packages com.microsoft.azure:synapseml_2.12:1.1.0
spark-submit --packages com.microsoft.azure:synapseml_2.12:1.1.0 MyApp.jar
```

Sources: [README.md:205-214]()

### SBT Build Configuration

For Scala applications built with SBT:

```scala
libraryDependencies += "com.microsoft.azure" % "synapseml_2.12" % "1.1.0"
```

Sources: [README.md:216-224]()

## Version Management and Compatibility

SynapseML versions are tied to specific Spark and Scala versions:

| SynapseML Version | Spark Version | Scala Version | Notes |
|-------------------|---------------|---------------|-------|
| 1.1.0 | 3.5.x | 2.12 | Latest stable release |
| 1.0.15 | 3.4.x | 2.12 | Spark 3.4 compatible |
| 0.11.4-spark3.3 | 3.3.x | 2.12 | Spark 3.3 compatible |

### Minimum Requirements

- **Scala**: 2.12
- **Spark**: 3.4+ (3.3 supported with legacy version)
- **Python**: 3.8+

Sources: [README.md:9, 129, 145, 161]()

## Platform-Specific Considerations

### Microsoft Fabric

Fabric has SynapseML **pre-installed**. Configuration is only needed to change the default version.

Sources: [README.md:96-113]()

### Databricks Compatibility

- Minimum Spark 3.2, Scala 2.12
- Recommended: DBR 10.1 or later to avoid Netty dependency issues
- GPU support available for deep learning workloads

Sources: [README.md:174-189]()

### Livy Environments

Livy 0.5 requires specific package exclusions due to dependency conflicts. The standard exclusion list addresses these issues.

Sources: [README.md:225-240]()

## Deployment Verification

After deployment, verify the installation:

```python
import synapse.ml
from synapse.ml.core import __spark_package_version__
print(__spark_package_version__)
```

For Scala:

```scala
import com.microsoft.azure.synapse.ml.core.spark.BuildInfo
println(BuildInfo.version)
```

Sources: [README.md:197-203]()

## Platform Detection System

SynapseML includes platform detection capabilities that adapt behavior based on the execution environment. This system is documented in [Platform Detection and Adaptation](#2.3) and affects logging, telemetry, and credential management.

The deployment configuration does not need to specify the platform explicitly - detection happens automatically at runtime based on environment variables and available APIs (e.g., `mssparkutils`, `dbutils`).

Sources: Referenced from architectural diagrams

## Release and Snapshot Versions

Release versions follow semantic versioning (e.g., `1.1.0`). Development snapshots are available for testing new features before official releases. Snapshot versions end with `.devN` suffix.

Snapshot artifacts are published to the same Maven repository but should not be used in production deployments.

Sources: [README.md:14, CONTRIBUTING.md:74-77]()

## Additional Resources

- **Example notebooks**: Available at `https://mmlspark.blob.core.windows.net/dbcs/SynapseMLExamplesv1.1.0.dbc` for Databricks
- **API Documentation**: Hosted at `mmlspark.blob.core.windows.net/docs/<version>/`
- **Docker EULA**: View with `docker run -it -p 8888:8888 mcr.microsoft.com/mmlspark/release eula`

Sources: [README.md:189, 254]()

---

# Page: Installation and Distribution

# Installation and Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [build.sbt](build.sbt)
- [deep-learning/src/test/python/synapsemltest/dl/conftest.py](deep-learning/src/test/python/synapsemltest/dl/conftest.py)
- [environment.yml](environment.yml)
- [pipeline.yaml](pipeline.yaml)
- [project/PublishPlugin.scala](project/PublishPlugin.scala)
- [project/Secrets.scala](project/Secrets.scala)
- [sonatype.sbt](sonatype.sbt)
- [templates/codecov.yml](templates/codecov.yml)
- [templates/conda.yml](templates/conda.yml)
- [templates/kv.yml](templates/kv.yml)
- [tools/esrp/prepare_jar.py](tools/esrp/prepare_jar.py)

</details>



This document describes how SynapseML artifacts are packaged, published, and distributed to end users. It covers the artifact distribution channels (Maven, PyPI, Docker), version management strategies, and the publishing pipeline that creates and deploys these artifacts.

For platform-specific deployment instructions, see:
- [Azure Synapse Deployment](#8.3)
- [Microsoft Fabric Deployment](#8.4)
- [Databricks Deployment](#8.5)
- [Docker Environments](#8.2)
- [Standalone and Other Platforms](#8.6)

For information about the CI/CD pipeline that produces these artifacts, see [CI/CD Pipeline](#3.1).

---

## Distribution Channels

SynapseML distributes artifacts through four primary channels, each serving different platform requirements and use cases.

### Distribution Channel Overview

```mermaid
graph TB
    subgraph "Build Artifacts"
        ScalaJARs["Scala JARs<br/>Signed with ESRP"]
        PythonWheel["Python Wheel<br/>synapseml-VERSION.whl"]
        RPackage["R Package<br/>synapse.ml"]
        Docs["Documentation<br/>Scala + Python"]
    end
    
    subgraph "Distribution Channels"
        Maven["Maven Repository<br/>mmlspark.azureedge.net/maven"]
        MavenCentral["Maven Central<br/>oss.sonatype.org"]
        PyPI["PyPI<br/>pypi.org/project/synapseml"]
        BlobStorage["Azure Blob Storage<br/>mmlspark.blob.core.windows.net"]
    end
    
    subgraph "Consumers"
        Synapse["Azure Synapse<br/>spark.jars.packages"]
        Fabric["Microsoft Fabric<br/>Pre-installed"]
        Databricks["Databricks<br/>Maven Coordinates"]
        Python["Python pip install<br/>+ pyspark"]
        SparkSubmit["spark-submit<br/>--packages"]
    end
    
    ScalaJARs --> Maven
    ScalaJARs --> MavenCentral
    PythonWheel --> PyPI
    PythonWheel --> BlobStorage
    RPackage --> BlobStorage
    Docs --> BlobStorage
    
    Maven --> Synapse
    Maven --> Fabric
    Maven --> Databricks
    Maven --> SparkSubmit
    MavenCentral --> Databricks
    MavenCentral --> SparkSubmit
    PyPI --> Python
    BlobStorage --> Synapse
    BlobStorage --> Databricks
```

Sources: [README.md:70-266](), [pipeline.yaml:87-135](), [build.sbt:265]()

### Maven Artifacts

Maven artifacts are the primary distribution method for Spark-based platforms. These artifacts consist of signed JAR files containing compiled Scala code and auto-generated Python/R wrappers.

**Maven Coordinates:**
- Group ID: `com.microsoft.azure`
- Artifact ID: `synapseml_2.12` (for Scala 2.12)
- Version: `1.1.0` (latest stable), or snapshot versions like `1.1.1-SNAPSHOT`

**Repositories:**
1. **Primary Repository**: `https://mmlspark.azureedge.net/maven` - Azure-hosted repository for all releases
2. **Maven Central**: `https://oss.sonatype.org` - Public Maven Central for official releases
3. **Azure DevOps Feed**: `msdata.pkgs.visualstudio.com/.../SynapseML_PublicPackages` - Internal Microsoft feed

The Maven artifacts exclude certain dependencies to avoid conflicts with Spark's built-in libraries:
- `org.scala-lang:scala-reflect`
- `org.apache.spark:spark-tags_2.12`
- `org.scalactic:scalactic_2.12`
- `org.scalatest:scalatest_2.12`
- `com.fasterxml.jackson.core:jackson-databind`

Sources: [README.md:106-108](), [README.md:129-131](), [README.md:181-183](), [build.sbt:17-21](), [build.sbt:47-48](), [sonatype.sbt:1-46]()

### PyPI Package

The `synapseml` Python package is distributed through PyPI, enabling standalone Python installations without requiring pre-existing Spark infrastructure.

**Package Details:**
- Package name: `synapseml`
- Version format: Python-compatible (e.g., `1.1.0` becomes `1.1.0` in PyPI)
- Dependencies: Requires `pyspark` to be installed separately
- Installation: `pip install synapseml`

The Python wheel contains:
- Auto-generated Python wrappers for all Scala classes
- Namespace package structure: `synapse.ml.*`
- License and README files

The package is built using the `packageSynapseML` task and published via the `publishPypi` task.

Sources: [README.md:191-203](), [build.sbt:132-185](), [build.sbt:187-197](), [pipeline.yaml:309-323]()

### Docker Images

Docker images are published to Microsoft Container Registry (MCR) but are currently disabled in the pipeline (commented out in pipeline.yaml).

**Image Types (when enabled):**
1. **Demo Image**: `mcr.microsoft.com/mmlspark/build-demo:VERSION` - Full environment with Jupyter
2. **Minimal Image**: `mcr.microsoft.com/mmlspark/build-minimal:VERSION` - Minimal runtime
3. **Release Image**: `mcr.microsoft.com/mmlspark/release:VERSION` and `latest` - Tagged releases

Sources: [pipeline.yaml:184-257](), [README.md:242-254]()

### Azure Blob Storage

Azure Blob Storage hosts supplementary artifacts that don't fit into standard package managers:

| Container | Contents | Purpose |
|-----------|----------|---------|
| `docs/` | API documentation (Scala, Python) | Version-specific documentation |
| `docs/` | Jupyter notebooks (`.ipynb`, converted `.py`) | Example notebooks and tutorials |
| `installers/` | Datasets for testing | Test data (e.g., `datasets-2023-04-03.tgz`) |
| `icons/` | Badges and graphics | Website badges, version indicators |

Sources: [build.sbt:199-220](), [build.sbt:222-241](), [build.sbt:243-248](), [build.sbt:72-89]()

---

## Version Management

SynapseML uses a structured versioning scheme that adapts to different distribution channels and Spark versions.

### Version Format Structure

```mermaid
graph LR
    subgraph "Base Version"
        SBT["build.sbt<br/>version setting"]
    end
    
    subgraph "Maven Version"
        MavenStable["Stable: 1.1.0"]
        MavenSnapshot["Snapshot: 1.1.1-SNAPSHOT"]
        MavenSpark33["Spark 3.3: 0.11.4-spark3.3"]
    end
    
    subgraph "Python Version"
        PyPIVersion["PyPI: 1.1.0<br/>pythonizedVersion function"]
    end
    
    subgraph "Version Tags"
        GitTag["Git Tag: v1.1.0<br/>triggers release"]
    end
    
    SBT --> MavenStable
    SBT --> MavenSnapshot
    SBT --> MavenSpark33
    SBT --> PyPIVersion
    GitTag --> MavenStable
    GitTag --> PyPIVersion
```

Sources: [build.sbt:10-15](), [README.md:14](), [pipeline.yaml:266-267]()

### Version Requirements

SynapseML enforces specific version requirements across its technology stack:

| Component | Required Version | Location |
|-----------|------------------|----------|
| Scala | 2.12.17 | [build.sbt:13]() |
| Spark | 3.5.0 (variable: `sparkVersion`) | [build.sbt:10]() |
| Python | 3.11.8 | [environment.yml:6]() |
| R | 4.1.1 | [environment.yml:9]() |

**Spark Version Compatibility:**
- Spark 3.5 Pools: `synapseml_2.12:1.1.0`
- Spark 3.4 Pools: `synapseml_2.12:1.0.15`
- Spark 3.3 Pools: `synapseml_2.12:0.11.4-spark3.3`

Sources: [README.md:9](), [README.md:122-168](), [build.sbt:10-15](), [environment.yml:6-11]()

### Snapshot Versions

Development versions follow the pattern `X.Y.Z-SNAPSHOT` and are published to the Azure Maven repository on every commit to master. The `dynverSeparator` setting in `sonatype.sbt` uses `-` as the separator.

Sources: [sonatype.sbt:45-46](), [pipeline.yaml:63]()

---

## Publishing Pipeline

The publishing pipeline transforms source code into distributable artifacts through a multi-stage process involving compilation, packaging, signing, and deployment.

### Publishing Pipeline Flow

```mermaid
graph TB
    subgraph "Trigger Conditions"
        MasterBranch["master branch push"]
        GitTag["Git tag: v*"]
    end
    
    subgraph "Publish Job"
        Compile["SBT Compile<br/>sbt publishM2"]
        PackagePython["Package Python<br/>sbt packagePython"]
        UploadNotebooks["Upload Notebooks<br/>sbt uploadNotebooks"]
        PublishBlob["Publish to Blob<br/>sbt publishBlob"]
        PublishDocs["Publish Docs<br/>sbt publishDocs"]
        PublishR["Publish R<br/>sbt publishR"]
        SignJARs["Sign JARs Locally<br/>sbt publishLocalSigned"]
        PrepareESRP["Prepare for ESRP<br/>tools/esrp/prepare_jar.py"]
    end
    
    subgraph "Release Job"
        CheckTag["Check Git Tag"]
        PyPIPublish["PyPI Release<br/>sbt publishPypi"]
        MavenSign["Sign for Maven<br/>sbt publishLocalSigned"]
        ESRPRelease["ESRP Release<br/>Maven Central"]
    end
    
    subgraph "Artifacts"
        BlobArtifacts["Azure Blob<br/>Notebooks, Docs, R"]
        PyPIArtifact["PyPI<br/>synapseml package"]
        MavenArtifact["Maven Central<br/>Signed JARs"]
    end
    
    MasterBranch --> Compile
    Compile --> PackagePython
    PackagePython --> UploadNotebooks
    UploadNotebooks --> PublishBlob
    PublishBlob --> PublishDocs
    PublishDocs --> PublishR
    PublishR --> SignJARs
    SignJARs --> PrepareESRP
    
    PrepareESRP --> BlobArtifacts
    
    GitTag --> CheckTag
    CheckTag --> PyPIPublish
    CheckTag --> MavenSign
    MavenSign --> ESRPRelease
    
    PyPIPublish --> PyPIArtifact
    ESRPRelease --> MavenArtifact
```

Sources: [pipeline.yaml:87-135](), [pipeline.yaml:259-353]()

### Publish Job Tasks

The `Publish` job runs on every build and generates all artifacts, storing them in Azure Blob Storage and the internal Maven feed.

**Task Sequence:**

1. **Environment Setup**
   - Authenticate with Azure DevOps Maven feed
   - Activate conda environment `synapseml`
   - Install build dependencies (graphviz, doxygen)

2. **Python Packaging** (`sbt packagePython uploadNotebooks`)
   - Auto-generates Python wrappers from Scala code
   - Creates wheel file structure
   - Uploads example notebooks to blob storage

3. **Artifact Publishing** (`sbt publishBlob publishDocs publishR publishPython`)
   - `publishBlob`: Uploads artifacts to Azure Blob Storage
   - `publishDocs`: Generates and uploads Scala/Python API docs
   - `publishR`: Packages and uploads R bindings
   - `publishPython`: Prepares Python wheel (not pushed to PyPI yet)

4. **Local Signing** (`sbt publishLocalSigned`)
   - Signs JARs with PGP keys
   - Stores signed artifacts in `~/.ivy2/local/com.microsoft.azure/`

5. **ESRP Preparation** (`python tools/esrp/prepare_jar.py`)
   - Flattens directory structure
   - Renames JARs to include version numbers
   - Prepares for Enterprise Software Release Process (ESRP)

Sources: [pipeline.yaml:92-135](), [build.sbt:132-185](), [build.sbt:199-220](), [tools/esrp/prepare_jar.py:1-80]()

### Release Job Tasks

The `Release` job only runs when a git tag starting with `v` is pushed to the master branch, triggering public releases.

**Conditional Execution:**
```yaml
condition: and(eq(variables.isMaster, true), startsWith(variables['tag'], 'v'))
```

**Task Sequence:**

1. **PyPI Publication** (`sbt publishPypi`)
   - Packages the complete `synapseml` wheel
   - Uses Twine to upload to PyPI with API token authentication
   - Skips existing versions to enable idempotency

2. **Maven Central Publication**
   - Re-signs JARs locally
   - Runs ESRP preparation script
   - Invokes ESRP Release task with Maven content type
   - Requires approval from designated approvers
   - Publishes to Maven Central via Sonatype

**ESRP Configuration:**
- Service Connection: `SynapseML-ESRP-Service-Connection`
- Key Vault: `esrp-kv-ame`
- Owners: `zhoubo@microsoft.com, marcozo@microsoft.com, romanbat@microsoft.com`
- Approvers: `romanbat@microsoft.com, markus.weimer@microsoft.com, negust@microsoft.com`

Sources: [pipeline.yaml:259-353](), [build.sbt:187-197]()

---

## Secret Management for Publishing

Publishing requires authentication credentials stored in Azure Key Vault and accessed via environment variables or cached files.

### Secret Architecture

```mermaid
graph TB
    subgraph "Secret Sources"
        KeyVault["Azure Key Vault<br/>mmlspark-keys"]
        EnvVars["Environment Variables<br/>CI/CD Pipeline"]
        LocalCache[".cache/ Directory<br/>Local Development"]
    end
    
    subgraph "Secret Types"
        PGPKeys["PGP Keys<br/>pgp-private, pgp-public"]
        Passwords["Passwords<br/>nexus-pw, pgp-pw"]
        Tokens["API Tokens<br/>pypi-api-token, ado-feed-token"]
    end
    
    subgraph "Secret Consumers"
        SBTPublish["SBT Publishing<br/>sonatype.sbt"]
        PyPIUpload["PyPI Upload<br/>Twine"]
        MavenAuth["Maven Authentication<br/>Azure DevOps Feed"]
        JARSigning["JAR Signing<br/>PGP"]
    end
    
    KeyVault --> LocalCache
    EnvVars --> SBTPublish
    EnvVars --> PyPIUpload
    LocalCache --> SBTPublish
    
    PGPKeys --> JARSigning
    Passwords --> SBTPublish
    Tokens --> PyPIUpload
    Tokens --> MavenAuth
    
    JARSigning --> SBTPublish
```

Sources: [project/Secrets.scala:1-194](), [pipeline.yaml:95-123](), [sonatype.sbt:29-36]()

### Secret Retrieval Strategy

The `Secrets` object implements a three-tier priority system for retrieving credentials:

1. **Environment Variables** (highest priority): Used by CI/CD pipeline
2. **Local Cache** (`.cache/` directory): Used for PGP ring files in development
3. **Azure Key Vault** (fallback): Direct fetch via Azure CLI

**Key Secret Names:**

| Secret Name | Environment Variable | Purpose |
|-------------|---------------------|---------|
| `pgp-private` | `PGP-PRIVATE` | Private PGP key for JAR signing |
| `pgp-public` | `PGP-PUBLIC` | Public PGP key for JAR signing |
| `pgp-pw` | `PGP-PW` | Passphrase for PGP keys |
| `nexus-un` | `NEXUS-UN` | Sonatype Nexus username |
| `nexus-pw` | `NEXUS-PW` | Sonatype Nexus password |
| `pypi-api-token` | `PYPI-API-TOKEN` | PyPI API token for uploads |
| `ado-feed-token` | `ADO-FEED-TOKEN` | Azure DevOps feed token |

**Publishing Enable Flag:**
Publishing tasks only run when `SYNAPSEML_ENABLE_PUBLISH=true` is set in the environment.

Sources: [project/Secrets.scala:13-194](), [pipeline.yaml:118-124](), [pipeline.yaml:314-323]()

---

## Installation Methods Overview

SynapseML can be installed through multiple methods depending on the target platform. Below is a summary with links to detailed platform-specific documentation.

### Installation Methods by Platform

| Platform | Installation Method | Artifact Source | Details |
|----------|---------------------|-----------------|---------|
| **Microsoft Fabric** | Pre-installed or `%%configure` magic | Maven | [Fabric Deployment](#8.4) |
| **Azure Synapse** | `%%configure` magic in notebook | Maven | [Synapse Deployment](#8.3) |
| **Databricks** | Maven library coordinates | Maven Central | [Databricks Deployment](#8.5) |
| **Python Standalone** | `pip install synapseml` | PyPI | [Standalone Platforms](#8.6) |
| **Spark Submit** | `--packages` flag | Maven | [Standalone Platforms](#8.6) |
| **SBT** | `libraryDependencies +=` | Maven Central | [Standalone Platforms](#8.6) |
| **Apache Livy** | `%%configure` magic | Maven | [Standalone Platforms](#8.6) |
| **Docker** | Pre-built images | MCR | [Docker Environments](#8.2) |
| **R** | `sparklyr` + Maven | Maven | [Standalone Platforms](#8.6) |

Sources: [README.md:70-266]()

### Common Configuration Parameters

Most Spark-based platforms require similar configuration parameters when installing SynapseML:

**Required Spark Configuration:**
```scala
spark.jars.packages = "com.microsoft.azure:synapseml_2.12:1.1.0"
spark.jars.repositories = "https://mmlspark.azureedge.net/maven"
```

**Common Exclusions:**
```scala
spark.jars.excludes = "org.scala-lang:scala-reflect,org.apache.spark:spark-tags_2.12,org.scalactic:scalactic_2.12,org.scalatest:scalatest_2.12,com.fasterxml.jackson.core:jackson-databind"
```

**Additional Configurations:**
```scala
spark.yarn.user.classpath.first = "true"  // Prioritize user classpath
spark.sql.parquet.enableVectorizedReader = "false"  // Compatibility setting
```

Sources: [README.md:102-113](), [README.md:126-136]()

### Build Information Publication

The pipeline publishes build metadata and documentation links to `target/Build.md` during the `genBuildInfo` task. This file contains:
- Scala API documentation URL
- Python API documentation URL  
- Version-specific documentation paths

The `publishBadges` task creates SVG badges indicating the current master version and uploads them to blob storage with no-cache headers.

Sources: [build.sbt:91-105](), [build.sbt:222-241]()

---

## Dependency Management

SynapseML carefully manages its dependencies to avoid conflicts with Spark's built-in libraries and to maintain compatibility across different Spark versions.

### Core Dependencies

**Spark Dependencies:**
- `spark-core`, `spark-mllib`, `spark-avro`: Version matches `sparkVersion` variable
- `spark-tags`: Test scope only
- All Spark dependencies exclude `com.google.protobuf:protobuf-java` to avoid version conflicts

**Additional Dependencies:**
```scala
commons-lang:commons-lang:2.6
org.scalactic:scalactic:3.2.14
io.spray:spray-json:1.3.5
com.jcraft:jsch:0.1.54
org.apache.httpcomponents.client5:httpclient5:5.1.3
org.apache.httpcomponents:httpmime:4.5.13
com.linkedin.isolation-forest:isolation-forest_3.5.0:3.0.5
```

**Module-Specific Dependencies:**
- **Deep Learning**: `onnx-protobuf`, `onnxruntime_gpu`, `hadoop-common`, `hadoop-azure`
- **LightGBM**: `lightgbmlib:3.3.510`
- **Vowpal Wabbit**: `vw-jni:9.3.0`
- **Cognitive Services**: `client-sdk:1.24.1`
- **OpenCV**: `opencv:3.2.0-1`

All extra dependencies have global exclusion rules applied to prevent conflicts with Spark.

Sources: [build.sbt:17-43](), [build.sbt:267-324]()

### POM Transformation

The build process transforms the Maven POM file to remove scoped dependencies and omitted dependencies, adding XML comments to explain their exclusion. This is handled by the `pomPostFunc` function.

**Omitted Dependencies:**
- `spark-core_2.12`
- `spark-mllib_2.12`
- `org.scala-lang` packages

These are assumed to be provided by the Spark runtime environment.

Sources: [build.sbt:45-70]()

---

## Conda Environment

The project uses Conda for reproducible development and CI/CD environments. The environment is defined in `environment.yml` and cached in Azure Pipelines to speed up builds.

### Conda Environment Configuration

**Channels:**
- `conda-forge`
- `default`

**Key Conda Packages:**
- Python 3.11.8
- R base 4.1.1 with sparklyr
- CMake ≤ 3.27

**Key Pip Packages:**
- PySpark 3.5.0
- PyArrow 10.0.1
- PyTorch 2.1.0 + TorchVision 0.16.0
- Transformers 4.49.0
- Horovod (from git commit)
- LangChain 0.0.152
- Testing frameworks (pytest, pytest-cov, pytest-codeblocks)
- Documentation tools (Sphinx, nbconvert)
- Publishing tools (Twine, azure-storage-blob)

**Caching Strategy:**
The CI/CD pipeline caches the conda environment at `$(CONDA_CACHE_DIR)` (`/usr/share/miniconda/envs`) using a cache key based on the OS and `environment.yml` hash. This dramatically reduces build times by avoiding repeated environment creation.

**Disk Space Management:**
The pipeline includes a cleanup step that removes unused SDKs (`/usr/local/lib/android`, `/usr/lib/google-cloud-sdk`) to free disk space before creating the conda environment.

Sources: [environment.yml:1-58](), [templates/conda.yml:1-42](), [pipeline.yaml:60]()

---

## Summary

SynapseML's distribution strategy supports multiple platforms through carefully orchestrated publishing to Maven repositories, PyPI, and Azure Blob Storage. The build system uses SBT to compile Scala code, auto-generate language bindings, and package artifacts. The CI/CD pipeline publishes snapshots on every commit and official releases when git tags are pushed. Version management accommodates different Spark versions while maintaining a consistent versioning scheme. Secret management via Azure Key Vault enables secure publishing operations, and conda environments ensure reproducible builds across development and CI/CD environments.

---

# Page: Docker Environments

# Docker Environments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala)
- [core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala](core/src/main/scala/org/apache/spark/ml/source/image/PatchedImageFileFormat.scala)
- [core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala](core/src/main/scala/org/apache/spark/sql/execution/streaming/continuous/HTTPSinkV2.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/codegen/RTestGen.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala)
- [start](start)
- [tools/docker/demo/Dockerfile](tools/docker/demo/Dockerfile)
- [tools/docker/demo/README.md](tools/docker/demo/README.md)
- [tools/docker/demo/init_notebook.py](tools/docker/demo/init_notebook.py)
- [tools/docker/minimal/Dockerfile](tools/docker/minimal/Dockerfile)
- [tools/tests/run_r_tests.R](tools/tests/run_r_tests.R)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitBaseModel.scala)

</details>



This document describes the Docker container images provided by SynapseML for local development, experimentation, and notebook execution. These containerized environments bundle Apache Spark, SynapseML, Jupyter Notebook, and all required dependencies into portable images that can run on any Docker-compatible system.

For information about deploying to other platforms, see [Installation and Distribution](#8.1) for general artifact distribution, [Azure Synapse Deployment](#8.3) for Synapse-specific instructions, or [Standalone and Other Platforms](#8.6) for alternative deployment options.

## Overview

SynapseML provides pre-configured Docker images that enable users to experiment with SynapseML capabilities without manual environment setup. The repository currently maintains two primary Docker image variants:

| Image Type | Path | Purpose |
|------------|------|---------|
| **demo** | `tools/docker/demo/Dockerfile` | Full-featured image with Jupyter Notebook and example notebooks for interactive exploration |
| **minimal** | `tools/docker/minimal/Dockerfile` | Lightweight image with core dependencies only, suitable as a base for custom environments |

Both images are based on Ubuntu 20.04 and include Apache Spark, Python, Java, and the SynapseML library configured for immediate use.

Sources: [tools/docker/demo/Dockerfile:1-71](), [tools/docker/minimal/Dockerfile:1-52]()

## Docker Image Architecture

```mermaid
graph TB
    subgraph "Base Image"
        Ubuntu["Ubuntu 20.04<br/>mcr.microsoft.com/oss/mirror/docker.io/library/ubuntu:20.04"]
    end
    
    subgraph "System Dependencies"
        JavaRuntime["OpenJDK 11<br/>/usr/lib/jvm/java-1.11.0-openjdk-amd64"]
        OpenMPI["OpenMPI 3.x<br/>openmpi-bin package"]
        SystemTools["System Tools<br/>curl, wget, bzip2"]
    end
    
    subgraph "Python Environment"
        Miniconda["Miniconda 3<br/>/usr/local"]
        Python3["Python 3.x<br/>conda-installed"]
        PySpark["PySpark Package<br/>conda-installed"]
        Jupyter["Jupyter Notebook<br/>conda-installed"]
    end
    
    subgraph "Apache Spark"
        SparkBinary["Spark 3.5.0 + Hadoop 3<br/>/opt/spark"]
        SparkHome["SPARK_HOME=/opt/spark"]
        SparkPath["PATH includes spark/bin"]
    end
    
    subgraph "SynapseML Integration"
        InitScript["init_notebook.py<br/>~/.ipython/profile_default/startup/"]
        SparkPackages["spark.jars.packages<br/>com.microsoft.azure:synapseml_2.12"]
        AzureStorage["Azure Storage JARs<br/>hadoop-azure, azure-storage"]
    end
    
    subgraph "Demo-Specific"
        ExampleNotebooks["Example Notebooks<br/>docs/ directory"]
        JupyterConfig["Jupyter Config<br/>~/.jupyter/jupyter_notebook_config.py"]
        Ports["Exposed Ports<br/>8888, 4040"]
    end
    
    Ubuntu --> SystemTools
    SystemTools --> JavaRuntime
    SystemTools --> OpenMPI
    SystemTools --> Miniconda
    
    Miniconda --> Python3
    Python3 --> PySpark
    Python3 --> Jupyter
    
    SparkBinary --> SparkHome
    SparkHome --> SparkPath
    
    InitScript --> SparkPackages
    SparkPackages --> AzureStorage
    
    Jupyter --> JupyterConfig
    JupyterConfig --> Ports
    ExampleNotebooks --> Ports
```

Sources: [tools/docker/demo/Dockerfile:1-71](), [tools/docker/minimal/Dockerfile:1-52]()

## Demo Docker Image

The demo image provides a complete interactive environment with Jupyter Notebook and example notebooks.

### Build Arguments and Environment Variables

The demo Dockerfile accepts build arguments and sets environment variables that control versions and paths:

| Variable | Type | Default Value | Description |
|----------|------|---------------|-------------|
| `SYNAPSEML_VERSION` | Build Arg | `1.1.0` | Version of SynapseML to install |
| `DEBIAN_FRONTEND` | Build Arg | `noninteractive` | Prevents apt-get prompts during build |
| `SPARK_VERSION` | Environment | `3.5.0` | Apache Spark version |
| `HADOOP_VERSION` | Environment | `3` | Hadoop major version |
| `JAVA_HOME` | Environment | `/usr/lib/jvm/java-1.11.0-openjdk-amd64` | Java installation path |
| `SPARK_HOME` | Environment | `/opt/spark` | Spark installation path |
| `PYTHONPATH` | Environment | `$SPARK_HOME/python/:$SPARK_HOME/python/lib/py4j*:$PYTHON_PATH` | Python import paths |

Sources: [tools/docker/demo/Dockerfile:3-43]()

### Image Construction Process

```mermaid
graph LR
    subgraph "Stage 1: System Setup"
        S1["apt-get update"] --> S2["Install Java, curl, wget, bzip2, openmpi"]
        S2 --> S3["apt-get upgrade & clean"]
    end
    
    subgraph "Stage 2: Miniconda"
        S3 --> M1["Download Miniconda installer"]
        M1 --> M2["Install to /usr/local"]
        M2 --> M3["conda install python=3 jupyter pyspark"]
        M3 --> M4["conda clean --all"]
    end
    
    subgraph "Stage 3: Spark"
        M4 --> SP1["Download spark-3.5.0-bin-hadoop3.tgz"]
        SP1 --> SP2["Extract to /opt/spark"]
        SP2 --> SP3["Set SPARK_HOME environment"]
    end
    
    subgraph "Stage 4: Cleanup"
        SP3 --> C1["apt-get remove curl, wget, bzip2"]
        C1 --> C2["Clean apt cache"]
    end
    
    subgraph "Stage 5: Jupyter"
        C2 --> J1["jupyter-notebook --generate-config"]
        J1 --> J2["Configure token-free access"]
        J2 --> J3["Set IP to 0.0.0.0"]
        J3 --> J4["Allow root execution"]
    end
    
    subgraph "Stage 6: Demo Content"
        J4 --> D1["Copy init_notebook.py"]
        D1 --> D2["Copy docs directory"]
        D2 --> D3["EXPOSE 8888, 4040"]
    end
```

Sources: [tools/docker/demo/Dockerfile:11-71]()

### Jupyter Notebook Configuration

The demo image configures Jupyter Notebook for immediate use without authentication in a containerized environment:

**Configuration file**: `~/.jupyter/jupyter_notebook_config.py`

```
c.NotebookApp.token = ''              # Disable authentication token
c.NotebookApp.ip = '0.0.0.0'         # Listen on all interfaces
c.NotebookApp.allow_root = True      # Allow running as root user
```

Sources: [tools/docker/demo/Dockerfile:54-59]()

### Exposed Ports

The demo image exposes two ports for web access:

- **Port 8888**: Jupyter Notebook web interface
- **Port 4040**: Spark UI for monitoring running applications

Sources: [tools/docker/demo/Dockerfile:66-70]()

## Minimal Docker Image

The minimal image provides a bare-bones Spark + SynapseML environment without Jupyter configuration or example notebooks. It follows the same construction process as the demo image through Stage 4 (Cleanup), then stops without adding Jupyter configuration or example content.

### Key Differences from Demo Image

| Feature | Demo Image | Minimal Image |
|---------|-----------|---------------|
| Jupyter Config | Configured, token-free | Basic installation only |
| Startup Script | `init_notebook.py` included | Not included |
| Example Notebooks | `docs/` directory copied | Not included |
| Exposed Ports | 8888, 4040 | None declared |
| Working Directory | `docs` | Root directory |

The minimal image is suitable for:
- Custom Dockerfile base image (`FROM synapseml-minimal`)
- Non-interactive batch processing
- CI/CD pipeline execution environments
- Resource-constrained deployments

Sources: [tools/docker/minimal/Dockerfile:1-52]()

## Jupyter Initialization Script

### Purpose and Location

The file `init_notebook.py` is automatically executed when Jupyter starts, creating a pre-configured `SparkSession` with SynapseML and Azure storage dependencies.

**Installation path**: `~/.ipython/profile_default/startup/init_notebook.py`

This directory is IPython's startup script location, ensuring execution before any user notebooks run.

Sources: [tools/docker/demo/Dockerfile:62](), [tools/docker/demo/init_notebook.py:1-47]()

### Spark Configuration

```mermaid
graph TB
    subgraph "SparkConf Configuration"
        Conf["pyspark.SparkConf()"]
        
        WASB1["spark.hadoop.fs.AbstractFileSystem.wasb.impl<br/>org.apache.hadoop.fs.azure.Wasb"]
        WASB2["spark.hadoop.fs.AbstractFileSystem.wasbs.impl<br/>org.apache.hadoop.fs.azure.Wasbs"]
        WASB3["spark.hadoop.fs.wasb.impl<br/>org.apache.hadoop.fs.azure.NativeAzureFileSystem"]
        WASB4["spark.hadoop.fs.wasbs.impl<br/>org.apache.hadoop.fs.azure.NativeAzureFileSystem"]
        WASB5["spark.hadoop.fs.viewfs.overload.scheme.target.wasb.impl<br/>org.apache.hadoop.fs.azure.NativeAzureFileSystem"]
        
        Packages["spark.jars.packages<br/>com.microsoft.azure:synapseml_2.12:${SYNAPSEML_VERSION}<br/>org.apache.hadoop:hadoop-azure:2.7.0<br/>org.apache.hadoop:hadoop-common:2.7.0<br/>com.microsoft.azure:azure-storage:2.0.0"]
        
        Repos["spark.jars.repositories<br/>https://mmlspark.azureedge.net/maven<br/>https://mvnrepository.com/artifact/..."]
    end
    
    subgraph "SparkSession Creation"
        Builder["SparkSession.builder"]
        Master["master('local[*]')"]
        AppName["appName('SynapseML Docker App')"]
        Config["config(conf=syanpseMLConf)"]
        Create["getOrCreate()"]
    end
    
    Conf --> WASB1
    Conf --> WASB2
    Conf --> WASB3
    Conf --> WASB4
    Conf --> WASB5
    Conf --> Packages
    Conf --> Repos
    
    Conf --> Builder
    Builder --> Master
    Master --> AppName
    AppName --> Config
    Config --> Create
    
    Create --> SparkVar["spark variable"]
    Create --> SCVar["sc variable (SparkContext)"]
```

Sources: [tools/docker/demo/init_notebook.py:5-46]()

### Azure Storage Integration

The initialization script configures Hadoop FileSystem implementations for Azure Storage access:

**WASB (Windows Azure Storage Blob) Protocol Support:**
- `wasb://` - Non-SSL Azure Blob access
- `wasbs://` - SSL-encrypted Azure Blob access

This configuration enables notebooks to read/write data directly from Azure Blob Storage using paths like:
```
wasbs://container@account.blob.core.windows.net/path/to/data
```

Sources: [tools/docker/demo/init_notebook.py:8-26]()

### Maven Package Resolution

The script dynamically resolves the SynapseML version from the `SYNAPSEML_VERSION` environment variable:

```python
"spark.jars.packages",
"com.microsoft.azure:synapseml_2.12:" + os.getenv("SYNAPSEML_VERSION", "1.1.0") + 
",org.apache.hadoop:hadoop-azure:2.7.0,org.apache.hadoop:hadoop-common:2.7.0,com.microsoft.azure:azure-storage:2.0.0"
```

Maven repositories are configured to fetch artifacts from:
1. Primary: `https://mmlspark.azureedge.net/maven`
2. Fallback: `https://mvnrepository.com/artifact/`

Sources: [tools/docker/demo/init_notebook.py:28-36]()

## Building Docker Images

### Demo Image Build Commands

**Build from current repository state:**
```bash
docker build . -f tools/docker/demo/Dockerfile -t synapseml
```

**Build specific version:**
```bash
docker build . \
  --build-arg SYNAPSEML_VERSION=1.1.0 \
  -f tools/docker/demo/Dockerfile \
  -t synapseml:1.1.0
```

The build argument `SYNAPSEML_VERSION` controls which version of SynapseML is downloaded from Maven during the initialization script execution.

Sources: [tools/docker/demo/README.md:5-21]()

### Minimal Image Build

```bash
docker build . -f tools/docker/minimal/Dockerfile -t synapseml-minimal
```

The minimal image can be versioned similarly using the `SYNAPSEML_VERSION` build argument.

Sources: [tools/docker/minimal/Dockerfile:1-52]()

## Running Docker Containers

### Demo Image Execution

**Start Jupyter Notebook server:**
```bash
docker run -p 4040:4040 -p 8888:8888 -ti synapseml jupyter notebook ./
```

**Port mappings:**
- `-p 8888:8888` - Maps Jupyter Notebook interface to localhost:8888
- `-p 4040:4040` - Maps Spark UI to localhost:4040

**Access points:**
- Jupyter Notebook: `http://localhost:8888`
- Spark UI: `http://localhost:4040`

The Jupyter interface provides token-free access to all example notebooks in the `docs/` directory, with a pre-configured Spark session available as the `spark` variable.

Sources: [tools/docker/demo/README.md:23-29]()

### Container Environment Details

When the container starts, the following environment is available:

```mermaid
graph LR
    subgraph "Available in Notebook"
        SparkSession["spark<br/>SparkSession object"]
        SparkContext["sc<br/>SparkContext object"]
        SynapseML["SynapseML Library<br/>com.microsoft.azure.synapseml.*"]
    end
    
    subgraph "File System"
        WorkDir["Working Directory<br/>/docs"]
        Notebooks["Example Notebooks<br/>*.ipynb files"]
        Spark["Spark Installation<br/>/opt/spark"]
    end
    
    subgraph "Network"
        Port8888["localhost:8888<br/>Jupyter UI"]
        Port4040["localhost:4040<br/>Spark UI"]
    end
    
    SparkSession --> SynapseML
    SparkContext --> SynapseML
    WorkDir --> Notebooks
    Notebooks --> SparkSession
```

Sources: [tools/docker/demo/init_notebook.py:40-46](), [tools/docker/demo/Dockerfile:64]()

## Version Configuration

### Environment Version Matrix

The Docker images support specific versions configured at build time:

| Component | Version | Configuration Method |
|-----------|---------|---------------------|
| Ubuntu | 20.04 | Base image |
| Java | OpenJDK 11 | apt-get package |
| Python | 3.x (latest from conda) | Conda package |
| Apache Spark | 3.5.0 | Environment variable `SPARK_VERSION` |
| Hadoop | 3.x | Environment variable `HADOOP_VERSION` |
| SynapseML | Configurable | Build argument `SYNAPSEML_VERSION` |
| OpenMPI | 3.x | apt-get package |

Sources: [tools/docker/demo/Dockerfile:3-9](), [start:3-7]()

### Binder Compatibility

The `start` script in the repository root defines versions for Binder (mybinder.org) compatibility:

```bash
export OPENMPI_VERSION="3.1.2"
export SPARK_VERSION="3.5.0"
export HADOOP_VERSION="3.3"
export SYNAPSEML_VERSION="1.1.0"  # Binder compatibility version
```

This script ensures consistent versioning across Docker and Binder deployments.

Sources: [start:1-10]()

## Use Cases

### Local Development

The Docker images support local development workflows:

1. **Interactive Exploration**: Use the demo image to experiment with SynapseML features in Jupyter
2. **Notebook Testing**: Test notebooks locally before deploying to cloud platforms
3. **Environment Reproducibility**: Ensure consistent behavior across developer machines

### CI/CD Integration

The minimal image serves as a base for automated testing:

```dockerfile
FROM synapseml-minimal:latest
COPY tests/ /tests/
RUN python -m pytest /tests/
```

### Custom Environment Base

Both images can be extended for specific use cases:

```dockerfile
FROM synapseml:1.1.0
RUN pip install additional-package
COPY custom-notebooks/ /notebooks/
```

Sources: [tools/docker/demo/README.md:1-3]()

## Related Infrastructure

The Docker environments interact with other SynapseML testing and deployment systems:

- **Testing Infrastructure**: Docker containers can execute the same notebooks used in E2E testing (see [Testing Strategy](#4.1))
- **HTTP Services**: The HTTP server/sink functionality is available in Docker for local REST API testing (see [Custom Spark Data Sources](#5.5))
- **Binary File Formats**: Custom file formats like `BinaryFileFormat` work within containers (see [Custom Spark Data Sources](#5.5))
- **Platform Detection**: The Docker environment is detected as a standalone platform by `Platform.current_platform()` (see [Platform Detection and Adaptation](#2.3))

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/io/split2/DistributedHTTPSuite.scala](), [core/src/main/scala/com/microsoft/azure/synapse/ml/io/binary/BinaryFileFormat.scala]()

---

# Page: Azure Synapse Deployment

# Azure Synapse Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/form/FormOntologyLearnerSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionSchemas.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionUtilities.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseExtension/SynapseExtensionsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala)
- [docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Create Audiobooks.ipynb)
- [docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb](docs/Explore Algorithms/AI Services/Quickstart - Document Question and Answering with PDFs.ipynb)
- [docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb](docs/Explore Algorithms/Deep Learning/Quickstart - Chat Completion with Azure AI Foundry Model.ipynb)
- [docs/Explore Algorithms/OpenAI/Langchain.ipynb](docs/Explore Algorithms/OpenAI/Langchain.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding and GPU based KNN.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - OpenAI Embedding.ipynb)
- [docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb](docs/Explore Algorithms/OpenAI/Quickstart - Understand and Search Forms.ipynb)
- [docs/Get Started/Install SynapseML.md](docs/Get Started/Install SynapseML.md)
- [src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala](src/test/scala/com/microsoft/azure/synapse/ml/core/test/fuzzing/FuzzingTest.scala)

</details>



## Purpose and Scope

This document describes how to deploy and use SynapseML in Azure Synapse Analytics environments. It covers notebook-level and pool-level installation, Spark configuration requirements, Livy batch execution for automated workflows, and resource management strategies.

For deployment to other platforms, see [Microsoft Fabric Deployment](#8.4), [Databricks Deployment](#8.5), or [Standalone and Other Platforms](#8.6). For general installation instructions across all platforms, see [Installation and Distribution](#8.1).

## Installation Methods

### Notebook-Level Installation

SynapseML can be installed at the notebook level using the `%%configure` magic command in the first cell. This approach allows version control per notebook without affecting the entire Spark pool.

**Configuration Cell Structure:**

```python
%%configure -f
{
  "name": "synapseml",
  "conf": {
      "spark.jars.packages": "com.microsoft.azure:synapseml_2.12:<version>",
      "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
      "spark.jars.excludes": "org.scala-lang:scala-reflect,org.apache.spark:spark-tags_2.12,org.scalactic:scalactic_2.12,org.scalatest:scalatest_2.12,com.fasterxml.jackson.core:jackson-databind",
      "spark.yarn.user.classpath.first": "true",
      "spark.sql.parquet.enableVectorizedReader": "false"
  }
}
```

**Version-Specific Configurations:**

| Spark Version | SynapseML Version | Configuration |
|---------------|-------------------|---------------|
| 3.5 | 1.1.0 | `synapseml_2.12:1.1.0` |
| 3.4 | 1.0.15 | `synapseml_2.12:1.0.15` |
| 3.3 | 0.11.4-spark3.3 | `synapseml_2.12:0.11.4-spark3.3` |

Sources: [README.md:118-168](), [docs/Get Started/Install SynapseML.md:25-72]()

### Pool-Level Installation

For consistent library availability across all notebooks in a Spark pool, add the configuration properties to the pool's Apache Spark configuration settings. This eliminates the need for per-notebook configuration cells.

```mermaid
graph TB
    subgraph "Installation Scope"
        NotebookLevel["Notebook-Level Installation<br/>%%configure magic"]
        PoolLevel["Pool-Level Installation<br/>Spark pool configuration"]
    end
    
    subgraph "Configuration Properties"
        JarPackages["spark.jars.packages<br/>Maven coordinates"]
        JarRepos["spark.jars.repositories<br/>https://mmlspark.azureedge.net/maven"]
        JarExcludes["spark.jars.excludes<br/>Conflict resolution"]
        ClasspathFirst["spark.yarn.user.classpath.first<br/>true"]
        ParquetReader["spark.sql.parquet.enableVectorizedReader<br/>false"]
    end
    
    subgraph "Maven Resolution"
        MavenRepo["Maven Repository<br/>mmlspark.azureedge.net"]
        ArtifactDownload["Artifact Download<br/>JAR files"]
        DependencyTree["Dependency Resolution<br/>Transitive dependencies"]
    end
    
    NotebookLevel --> JarPackages
    PoolLevel --> JarPackages
    
    JarPackages --> MavenRepo
    JarRepos --> MavenRepo
    JarExcludes --> DependencyTree
    
    MavenRepo --> ArtifactDownload
    ArtifactDownload --> DependencyTree
    
    ClasspathFirst -.->|Override| DependencyTree
    ParquetReader -.->|Compatibility| DependencyTree
```

Sources: [README.md:172](), [docs/Get Started/Install SynapseML.md:152-166]()

## Configuration Parameters

### Maven Coordinates

The `spark.jars.packages` parameter specifies the Maven coordinates for SynapseML:

```
com.microsoft.azure:synapseml_2.12:<version>
```

- **Group ID**: `com.microsoft.azure`
- **Artifact ID**: `synapseml_2.12` (Scala 2.12 build)
- **Version**: Matches Spark version (1.1.0 for Spark 3.5, 1.0.15 for Spark 3.4)

Sources: [README.md:129,145,161]()

### Dependency Exclusions

The `spark.jars.excludes` parameter prevents JAR conflicts by excluding specific artifacts that conflict with Synapse's built-in libraries:

| Excluded Artifact | Reason |
|-------------------|--------|
| `scala-reflect` | Conflicts with Spark's Scala runtime |
| `spark-tags_2.12` | Conflicts with Spark core |
| `scalactic_2.12`, `scalatest_2.12` | Test dependencies, not needed at runtime |
| `jackson-databind` | Version conflicts with Synapse's Jackson |

Sources: [README.md:131,147,163](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:201-205]()

### Classpath Priority

`spark.yarn.user.classpath.first: "true"` ensures user-provided JARs (SynapseML) take precedence over system JARs. This is critical for overriding Synapse's pre-installed versions or resolving version conflicts.

Sources: [README.md:132,148,164]()

### Parquet Vectorized Reader

`spark.sql.parquet.enableVectorizedReader: "false"` disables vectorized Parquet reading for compatibility with certain SynapseML operations.

Sources: [README.md:133,149,165]()

## Spark Pool Requirements

### Supported Spark Versions

SynapseML requires:
- **Spark**: 3.4 or higher (3.5 recommended)
- **Scala**: 2.12
- **Python**: 3.8+

Sources: [README.md:9]()

### Pool Configuration for E2E Testing

The E2E testing infrastructure creates Spark pools with specific configurations:

```scala
// Pool properties
val PoolNodeSize: String = "Small"
val PoolLocation: String = "eastus2"
val SparkVersion: String = "3.5"

// Auto-scaling configuration
"autoScale": {
  "enabled": "true",
  "maxNodeCount": "10",
  "minNodeCount": "3"
}

// Dynamic executor allocation
"dynamicExecutorAllocation": {
  "enabled": "true",
  "maxExecutors": "8",
  "minExecutors": "2"
}
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:145-146,276]()

## Livy Batch Execution Architecture

SynapseML's automated testing and deployment leverage Apache Livy for batch job submission. This architecture enables distributed execution of notebooks as Python scripts.

```mermaid
graph TB
    subgraph "Notebook Preparation"
        Notebooks["Jupyter Notebooks<br/>*.ipynb"]
        Conversion["nbconvert<br/>jupyter nbconvert --to python"]
        PythonScripts["Python Scripts<br/>*.py"]
        Preamble["NotebookPreamble<br/>Platform detection code"]
    end
    
    subgraph "Azure Storage"
        LocalScript["Local Python File"]
        AzCLI["az storage fs file upload"]
        BlobStorage["Azure Blob Storage<br/>abfss://synapse@mmlsparkbuildsynapse"]
        ScriptPath["Script Path<br/>build_X.X.X/scripts/notebook.py"]
    end
    
    subgraph "Livy Batch Submission"
        LivyPayload["Livy Payload JSON<br/>file, name, resources, conf"]
        LivyAPI["Livy API<br/>POST /livyApi/.../batches"]
        BatchCreation["Batch Creation<br/>Returns batch ID"]
    end
    
    subgraph "Spark Pool Execution"
        PoolSelection["Spark Pool<br/>Small nodes, eastus2"]
        DriverMemory["Driver: 28g memory, 4 cores"]
        ExecutorConfig["Executors: 28g memory, 4 cores, count=2"]
        SparkConf["Spark Configuration<br/>spark.jars.packages<br/>spark.jars.excludes"]
    end
    
    subgraph "Job Monitoring"
        StatusPolling["Status Polling<br/>GET /batches/{id}"]
        LivyBatchData["LivyBatchData<br/>id, state, appId, log"]
        StateCheck["State Check<br/>queued/running/success/error"]
    end
    
    Notebooks --> Conversion
    Conversion --> PythonScripts
    Preamble --> PythonScripts
    PythonScripts --> LocalScript
    
    LocalScript --> AzCLI
    AzCLI --> BlobStorage
    BlobStorage --> ScriptPath
    
    ScriptPath --> LivyPayload
    LivyPayload --> LivyAPI
    LivyAPI --> BatchCreation
    
    BatchCreation --> PoolSelection
    PoolSelection --> DriverMemory
    PoolSelection --> ExecutorConfig
    PoolSelection --> SparkConf
    
    BatchCreation --> StatusPolling
    StatusPolling --> LivyBatchData
    LivyBatchData --> StateCheck
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:188-236](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala:82-122]()

### Livy Batch Submission Process

The `SynapseUtilities.uploadAndSubmitNotebook` function orchestrates the submission:

1. **Upload to Azure Blob Storage**: Scripts are uploaded to `abfss://synapse@mmlsparkbuildsynapse.dfs.core.windows.net/build_{version}/scripts/{filename}`

2. **Construct Livy Payload**:
```json
{
  "file": "abfss://...",
  "name": "notebook_name",
  "driverMemory": "28g",
  "driverCores": 4,
  "executorMemory": "28g",
  "executorCores": 4,
  "numExecutors": 2,
  "conf": {
    "spark.jars.packages": "...",
    "spark.jars.repositories": "...",
    "spark.jars.excludes": "...",
    "spark.yarn.user.classpath.first": "true"
  }
}
```

3. **Submit to Livy API**:
```
POST https://mmlsparkbuildtest.dev.azuresynapse.net/livyApi/versions/2019-11-01-preview/sparkPools/{poolName}/batches
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:188-236]()

### Job Monitoring

The `LivyBatch.monitor()` method polls job status asynchronously:

```scala
case class LivyBatchData(
  id: Int,
  state: String,
  appId: Option[String],
  log: Option[Seq[String]]
)
```

**State Transitions:**
- `queued` → `running` → `success` (successful completion)
- `queued` → `running` → `dead`/`error`/`killed` (failure states)

The monitoring loop polls every 15 seconds and times out after 30 minutes.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:28-106]()

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "User Layer"
        SynapseNotebook["Synapse Notebook<br/>%%configure cell"]
        JupyterNB["Jupyter Notebook<br/>*.ipynb"]
    end
    
    subgraph "SynapseML Test Infrastructure"
        SynapseTests["SynapseTests<br/>Test orchestration"]
        SynapseUtilities["SynapseUtilities<br/>createSparkPools()<br/>uploadAndSubmitNotebook()<br/>deleteSparkPool()"]
        SharedNotebookUtils["SharedNotebookE2ETestUtilities<br/>generateNotebooks()<br/>insertTextInFile()"]
    end
    
    subgraph "Azure Management APIs"
        ARMToken["ARM Token<br/>management.azure.com"]
        SynapseToken["Synapse Token<br/>dev.azuresynapse.net"]
        ManagementAPI["Management API<br/>Pool CRUD operations"]
        LivyAPI["Livy API<br/>Batch submission/monitoring"]
    end
    
    subgraph "Azure Resources"
        SparkPool["Spark Pool<br/>tcTIMESTAMP<br/>Auto-pause: 10min"]
        BlobStorage["Blob Storage<br/>mmlsparkbuildsynapse/synapse"]
        KeyVault["Azure Key Vault<br/>mmlspark-build-keys<br/>Secrets management"]
    end
    
    subgraph "Maven Infrastructure"
        MavenRepo["Maven Repository<br/>mmlspark.azureedge.net"]
        JARs["SynapseML JARs<br/>synapseml_2.12-X.X.X.jar"]
    end
    
    SynapseNotebook --> SparkPool
    JupyterNB --> SharedNotebookUtils
    
    SynapseTests --> SynapseUtilities
    SharedNotebookUtils --> BlobStorage
    
    SynapseUtilities --> ARMToken
    SynapseUtilities --> SynapseToken
    
    ARMToken --> ManagementAPI
    SynapseToken --> LivyAPI
    
    ManagementAPI --> SparkPool
    LivyAPI --> SparkPool
    
    SynapseUtilities --> BlobStorage
    SparkPool --> BlobStorage
    SparkPool --> MavenRepo
    MavenRepo --> JARs
    
    SynapseUtilities --> KeyVault
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:133-348](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:48-220]()

## Resource Management

### Spark Pool Lifecycle

**Pool Creation:**
The testing infrastructure creates pools with timestamp-based names (`tc{milliseconds}`) to ensure uniqueness:

```scala
val ClusterPrefix = "tc"
val triggerTime = Calendar.getInstance().getTimeInMillis.toString
val bigDataPoolName = s"$ClusterPrefix$triggerTime"
```

Pool properties include:
- **Auto-pause**: 10 minutes of inactivity
- **Auto-scale**: 3-10 nodes
- **Session-level packages**: Enabled
- **Spark version**: 3.5

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:151,318-337]()

### Cleanup Strategies

**Automated Cleanup:**
The `tryDeleteOldSparkPools()` function removes pools older than 24 hours to prevent resource accumulation:

```scala
val dayAgoTsInMillis = Calendar.getInstance().getTimeInMillis - 24 * 60 * 60 * 1000

// Query pools with filter
val getBigDataPoolsUri = s"""
  $ManagementUrlRoot/resources?api-version=2021-04-01&
  $$filter=substringof(name, '$WorkspaceName/$ClusterPrefix') and
  resourceType eq 'Microsoft.Synapse/workspaces/bigDataPools'
""".stripMargin
```

Pools are identified by:
1. Name prefix (`tc`)
2. Creation timestamp in tags
3. Age comparison

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:283-316]()

**Test Cleanup:**
After test completion, pools are deleted if they were created by the test:

```scala
protected override def afterAll(): Unit = {
  existingPoolNameOpt match {
    case Some(pool) =>
      println(s"Existing pool '$pool' was used; skipping deletion.")
    case None =>
      val poolsToDelete = sparkPools.distinct.filter(_.startsWith(ClusterPrefix))
      poolsToDelete.map(pool => Try(deleteSparkPool(pool)))
  }
  super.afterAll()
}
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:200-219]()

### Job Monitoring and Retry Logic

**Retry Mechanism:**
Failed jobs are automatically retried up to 5 times with exponential backoff plus jitter:

```scala
@tailrec
private def retryBatch(maxRetries: Int, delayMillis: Long, attempt: Int = 1)(block: => LivyBatch): LivyBatch = {
  val livyBatch = block
  livyBatch.isSuccess match {
    case true => livyBatch
    case false if attempt < maxRetries =>
      val jitter = scala.util.Random.nextInt(5000)
      Thread.sleep(delayMillis + jitter)
      retryBatch(maxRetries, delayMillis, attempt + 1)(block)
    case false => livyBatch
  }
}
```

**Status Monitoring:**
Jobs are monitored with 15-second polling intervals:

```scala
@tailrec
private def pollLivyUrl(lastStatus: Option[String] = None): LivyBatch = {
  val newData = sendAndParseJson(getStatusRequest).convertTo[LivyBatchData]
  if (newData.state == "success") {
    LivyBatch(newData, runName, sparkPool, startTime)
  } else if (Set("dead", "error", "killed")(newData.state.toLowerCase)) {
    LivyBatch(newData, runName, sparkPool, startTime)
  } else {
    Thread.sleep(15000)
    pollLivyUrl(Some(newData.state))
  }
}
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:138-149,161](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:63-82]()

## Authentication and Token Management

### Token Acquisition

SynapseML's Synapse deployment uses two types of tokens:

**ARM Token (Azure Resource Manager):**
```scala
lazy val ArmToken: String = getAccessToken("https://management.azure.com/")
```
Used for management plane operations (creating/deleting pools).

**Synapse Token:**
```scala
lazy val SynapseToken: String = getAccessToken("https://dev.azuresynapse.net/")
```
Used for data plane operations (Livy API calls).

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:137-138]()

### Secret Management

Secrets are retrieved from Azure Key Vault using the Azure CLI:

```scala
def getSecret(secretName: String): String = {
  println(s"[info] fetching secret: $secretName from $AccountString")
  val secretJson = exec(s"az keyvault secret show --vault-name $KvName --name $secretName")
  secretJson.parseJson.asJsObject().fields("value").convertTo[String]
}
```

Key secrets:
- `openai-api-key-2`: OpenAI service key
- `ai-services-api-key`: Azure AI Services key
- `azure-search-key`: Cognitive Search key

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/Secrets.scala:44-79]()

### Platform Detection

Notebooks detect the Synapse environment using the notebook preamble:

```python
from synapse.ml.core.platform import running_on_synapse

if running_on_synapse():
    from IPython import get_ipython
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    from synapse.ml.core.platform import materializing_display as display
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.getOrCreate()
```

This ensures compatibility with Synapse-specific APIs like `mssparkutils`.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SharedNotebookE2ETestUtilities.scala:22-42]()

## Notebook Execution Flow

```mermaid
sequenceDiagram
    participant Test as SynapseTests
    participant Utils as SynapseUtilities
    participant Storage as Azure Blob Storage
    participant Livy as Livy API
    participant Pool as Spark Pool
    participant Monitor as Job Monitor
    
    Test->>Utils: generateNotebooks()
    Utils->>Storage: Upload .py file<br/>az storage fs file upload
    Storage-->>Utils: Script URL
    
    Test->>Utils: createSparkPools(count)
    Utils->>Pool: Create pool tc{timestamp}
    Pool-->>Utils: Pool name
    
    Test->>Utils: uploadAndSubmitNotebook(pool, file)
    Utils->>Livy: POST /batches<br/>Livy payload with config
    Livy-->>Utils: Batch ID
    
    Utils->>Monitor: monitor()
    loop Every 15 seconds
        Monitor->>Livy: GET /batches/{id}
        Livy-->>Monitor: LivyBatchData(state)
        alt state == "success"
            Monitor-->>Test: Success
        else state in ["dead","error","killed"]
            Monitor-->>Test: Failure
        else state in ["queued","running"]
            Monitor->>Monitor: Continue polling
        end
    end
    
    Test->>Utils: deleteSparkPool(name)
    Utils->>Pool: DELETE pool
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:98-198](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:188-236]()

## Best Practices

### Version Selection

Choose the SynapseML version that matches your Spark pool version:
- **Spark 3.5**: Use `synapseml_2.12:1.1.0`
- **Spark 3.4**: Use `synapseml_2.12:1.0.15`
- **Spark 3.3**: Use `synapseml_2.12:0.11.4-spark3.3`

Mismatched versions may cause binary compatibility issues.

### Configuration Order

Always place the `%%configure` cell as the **first cell** in your notebook. The `-f` flag forces session restart to apply configuration changes.

### Pool-Level vs Notebook-Level

**Use pool-level installation when:**
- All notebooks in the pool use the same SynapseML version
- You want to reduce notebook startup time
- You need consistent library availability

**Use notebook-level installation when:**
- Different notebooks require different versions
- You're testing new SynapseML releases
- You want version control per notebook

### Resource Optimization

**For production workloads:**
- Enable auto-pause with appropriate timeout (10-15 minutes)
- Configure auto-scale based on workload patterns
- Use dynamic executor allocation for variable workloads

**For development:**
- Use smaller node sizes ("Small") for cost efficiency
- Set lower minimum node counts
- Implement aggressive auto-pause policies

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:238-279]()

## Troubleshooting

### Common Issues

**JAR Conflicts:**
If you encounter `NoClassDefFoundError` or `NoSuchMethodError`, ensure `spark.yarn.user.classpath.first` is set to `true` and all conflicting dependencies are excluded.

**Livy Timeout:**
Batch submissions may timeout if the pool is cold-starting. The default timeout is 30 minutes. Monitor job status at:
```
https://web-staging.azuresynapse.net/en-us/monitoring/sparkapplication/{runName}
```

**Dependency Resolution Failures:**
Verify that `spark.jars.repositories` includes `https://mmlspark.azureedge.net/maven`. Network issues may prevent Maven artifact download.

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseUtilities.scala:97-104](), [README.md:131-133]()

---

# Page: Microsoft Fabric Deployment

# Microsoft Fabric Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_template.yaml](.github/ISSUE_TEMPLATE/bug_report_template.yaml)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/io/http/HTTPClients.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala)
- [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala](core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/logging/LoggingScrubberTests.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VectorZipper.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitCSETransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitDSJsonTransformer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala)
- [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala](vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala)

</details>



## Purpose and Scope

This document explains how SynapseML is deployed and integrated with Microsoft Fabric, including pre-installation details, environment detection mechanisms, token management for authentication, workload endpoint resolution, and telemetry integration. For deployment on other platforms, see [Azure Synapse Deployment](#8.3), [Databricks Deployment](#8.5), and [Standalone and Other Platforms](#8.6). For general installation and distribution mechanisms, see [Installation and Distribution](#8.1).

## Pre-Installation and Version Management

SynapseML comes pre-installed in Microsoft Fabric notebooks. Users can optionally override the default version by placing a configuration cell at the beginning of their notebook:

```bash
%%configure -f
{
  "name": "synapseml",
  "conf": {
      "spark.jars.packages": "com.microsoft.azure:synapseml_2.12:<VERSION>",
      "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
      "spark.jars.excludes": "org.scala-lang:scala-reflect,org.apache.spark:spark-tags_2.12,org.scalactic:scalactic_2.12,org.scalatest:scalatest_2.12,com.fasterxml.jackson.core:jackson-databind",
      "spark.yarn.user.classpath.first": "true",
      "spark.sql.parquet.enableVectorizedReader": "false"
  }
}
```

The `%%configure -f` magic command reconfigures the Spark session with the specified SynapseML version and Maven coordinates. The `-f` flag forces a session restart to apply the new configuration.

**Sources:** [README.md:96-113]()

## Platform Detection

SynapseML automatically detects when it is running in Microsoft Fabric using a multi-layered detection mechanism. This detection enables platform-specific behavior for authentication, telemetry, and endpoint resolution.

### Detection Flow Diagram

```mermaid
flowchart TD
    Start["currentPlatform()"] --> CheckTrident["Check file exists:<br/>/home/trusted-service-user/<br/>.trident-context"]
    CheckTrident -->|Exists| FabricDetected["Return:<br/>PlatformSynapseInternal"]
    CheckTrident -->|Not Exists| CheckAzureService["Check env var:<br/>AZURE_SERVICE"]
    CheckAzureService -->|"== Microsoft.ProjectArcadia"| CheckSparkCluster["Get SparkSession<br/>spark.cluster.type"]
    CheckAzureService -->|Other| CheckDBFS["Check /dbfs exists"]
    CheckSparkCluster -->|"== synapse"| SynapseDetected["Return:<br/>PlatformSynapse"]
    CheckSparkCluster -->|Other| FabricDetected
    CheckDBFS -->|Exists| DatabricksDetected["Return:<br/>PlatformDatabricks"]
    CheckDBFS -->|Not Exists| CheckBinder["Check env var:<br/>BINDER_LAUNCH_HOST"]
    CheckBinder -->|Exists| BinderDetected["Return:<br/>PlatformBinder"]
    CheckBinder -->|Not Exists| UnknownDetected["Return:<br/>PlatformUnknown"]
```

The detection logic prioritizes the presence of the Trident context file, which is unique to Microsoft Fabric environments. The constant `PlatformSynapseInternal` is used internally to refer to Fabric, distinguishing it from regular Azure Synapse (`PlatformSynapse`).

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:17-47]()

### Platform Detection Usage

Components throughout SynapseML use the `runningOnFabric()` helper method to conditionally enable Fabric-specific features:

```scala
def runningOnFabric(): Boolean = CurrentPlatform == PlatformSynapseInternal
```

This is used primarily for:
- Enabling certified event telemetry
- Using Fabric-specific token acquisition
- Resolving Fabric workload endpoints

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/PlatformDetails.scala:42-46]()

## Fabric Environment Configuration

When running in Fabric, SynapseML reads configuration from multiple sources to identify the execution context and construct appropriate service endpoints.

### Configuration Sources Diagram

```mermaid
flowchart LR
    subgraph "Configuration Files"
        ContextFile["/.trident-context<br/>Key-value pairs"]
        SparkConf["/opt/spark/conf/<br/>spark-defaults.conf"]
        ClusterInfo["/opt/health-agent/conf/<br/>cluster-info.json"]
    end
    
    subgraph "FabricClient"
        ReadContext["readFabricContextFile()"]
        ReadSparkConf["readFabricSparkConfFile()"]
        ReadClusterMeta["readClusterMetadata()"]
        FabricContext["FabricContext Map"]
    end
    
    subgraph "Extracted Properties"
        CapacityID["CapacityID"]
        WorkspaceID["WorkspaceID"]
        ArtifactID["ArtifactID"]
        PbiEnv["PbiEnv<br/>(public/daily/dxt/msit)"]
        WorkspacePE["WorkspacePeEnabled"]
    end
    
    ContextFile --> ReadContext
    SparkConf --> ReadSparkConf
    ClusterInfo --> ReadClusterMeta
    
    ReadContext --> FabricContext
    ReadSparkConf --> FabricContext
    ReadClusterMeta --> WorkspacePE
    
    FabricContext --> CapacityID
    FabricContext --> WorkspaceID
    FabricContext --> ArtifactID
    FabricContext --> PbiEnv
```

### Key Configuration Properties

| Property | Source Key | Description |
|----------|------------|-------------|
| **CapacityID** | `trident.capacity.id` | Unique identifier for the Fabric capacity |
| **WorkspaceID** | `trident.artifact.workspace.id` or `trident.workspace.id` | Workspace containing the notebook/artifact |
| **ArtifactID** | `trident.artifact.id` | Current artifact (notebook) identifier |
| **PbiEnv** | `spark.trident.pbienv` | Environment: `public`, `daily`, `dxt`, `msit` (defaults to `public`) |
| **WorkspacePeEnabled** | `workspace-pe-enabled` (from cluster metadata) | Whether private endpoints are enabled |

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:23-29, 51-143]()

### Configuration File Parsing

The `FabricClient` object lazily loads configuration on first access using Scala `lazy val` initialization:

- **Trident Context**: Parsed as simple `key=value` pairs from [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:90-106]()
- **Spark Configuration**: Parsed from Spark defaults file, filtering comment lines [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:108-124]()
- **Cluster Metadata**: Parsed as JSON to extract private endpoint settings [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:126-138]()

## Token Management and Authentication

SynapseML requires authentication tokens to access Fabric ML workload services and Azure Cognitive Services. Token acquisition uses reflection to access the Fabric-provided TokenLibrary without creating a compile-time dependency.

### Token Acquisition Architecture

```mermaid
flowchart TD
    subgraph "SynapseML Components"
        CognitiveService["Cognitive Services<br/>Integration"]
        FabricClient["FabricClient.scala<br/>API Requests"]
        LoggingSystem["CertifiedEventClient<br/>Telemetry"]
    end
    
    subgraph "TokenLibrary Wrapper"
        TokenLib["TokenLibrary.scala"]
        GetAccessToken["getAccessToken()<br/>Reflection-based"]
        GetMwcToken["getSparkMwcToken()<br/>Reflection-based"]
    end
    
    subgraph "Fabric TokenLibrary"
        TridentTokenLib["com.microsoft.azure.trident<br/>.tokenlibrary.TokenLibrary"]
        GetAccessTokenMethod["getAccessToken(String)<br/>Returns AAD token"]
        GetMwcTokenMethod["getMwcToken(String, String,<br/>Integer, String)<br/>Returns MWC token"]
    end
    
    CognitiveService --> TokenLib
    FabricClient --> TokenLib
    LoggingSystem --> TokenLib
    
    TokenLib --> GetAccessToken
    TokenLib --> GetMwcToken
    
    GetAccessToken -->|"Reflect & Invoke<br/>with resource: ml"| TridentTokenLib
    GetMwcToken -->|"Reflect & Invoke<br/>with workspaceId, artifactId,<br/>2, SparkCore"| TridentTokenLib
    
    TridentTokenLib --> GetAccessTokenMethod
    TridentTokenLib --> GetMwcTokenMethod
    
    GetAccessTokenMethod --> AADToken["AAD Bearer Token"]
    GetMwcTokenMethod --> MWCToken["MWC Token"]
```

### Token Types and Usage

| Token Type | Method | Format | Usage |
|------------|--------|--------|-------|
| **AAD Token** | `getMLWorkloadAADAuthHeader()` | `Bearer <token>` | ML Workload API requests, telemetry |
| **MWC Token** | `getCognitiveMWCTokenAuthHeader()` | `MwcToken <token>` | Cognitive Services requests |

The AAD token is obtained by calling `TokenLibrary.getAccessToken("ml")`, which requests an Azure Active Directory token for the ML resource. The MWC (Managed Workspace Container) token is obtained for specific workspace and artifact IDs, used primarily for cognitive services integration.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:9-51](), [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:194-198]()

### Reflection-Based Token Acquisition

Since the Fabric TokenLibrary is not available in all environments, SynapseML uses reflection to avoid compile-time dependencies:

```scala
val objectName = "com.microsoft.azure.trident.tokenlibrary.TokenLibrary"
val mirror = currentMirror
val module = mirror.staticModule(objectName)
val obj = mirror.reflectModule(module).instance
val methodMirror = mirror.reflect(obj).reflectMethod(selectedMethodSymbol.asMethod)
methodMirror("ml").asInstanceOf[String]
```

This pattern allows SynapseML to work in non-Fabric environments (where TokenLibrary doesn't exist) while leveraging it when available.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/TokenLibrary.scala:10-27]()

## Workload Endpoints

SynapseML constructs ML workload endpoints dynamically based on the detected Fabric environment configuration. These endpoints provide access to ML services, cognitive services, and telemetry infrastructure.

### Endpoint Resolution Flow

```mermaid
flowchart TD
    Start["MLWorkloadEndpoint<br/>Resolution"] --> CheckPE["WorkspacePeEnabled?"]
    
    CheckPE -->|True| ConstructPE["Construct PE Host:<br/>https://{cleanedWsId}.z{prefix}<br/>.{envMark}c.fabric.microsoft.com"]
    CheckPE -->|False| ExtractHost["Extract from:<br/>trident.lakehouse.tokenservice.endpoint"]
    
    ConstructPE --> BuildEndpoint["Build Endpoint Path:<br/>{host}/webapi/capacities/<br/>{capacityId}/workloads/ML/<br/>{type}/Automatic/workspaceid/<br/>{workspaceId}/"]
    ExtractHost --> BuildEndpoint
    
    BuildEndpoint --> TypeML["MLWorkloadEndpointML"]
    BuildEndpoint --> TypeLLM["MLWorkloadEndpointLLMPlugin"]
    BuildEndpoint --> TypeAuto["MLWorkloadEndpointAutomatic"]
    BuildEndpoint --> TypeRegistry["MLWorkloadEndpointRegistry"]
    BuildEndpoint --> TypeAdmin["MLWorkloadEndpointAdmin"]
    
    TypeML --> CognitiveEndpoint["MLWorkloadEndpointCognitive:<br/>{ML}/cognitive/"]
    CognitiveEndpoint --> OpenAIEndpoint["MLWorkloadEndpointOpenAI:<br/>{ML}/cognitive/openai/"]
```

### Endpoint Types and Structure

The following endpoint types are constructed by `FabricClient`:

| Constant | Endpoint Type | Path Suffix | Purpose |
|----------|---------------|-------------|---------|
| `MLWorkloadEndpointML` | `ML` | Base ML workload | General ML operations |
| `MLWorkloadEndpointLLMPlugin` | `LlmPlugin` | LLM plugin | Language model services |
| `MLWorkloadEndpointAutomatic` | `Automatic` | Automatic ML | AutoML services |
| `MLWorkloadEndpointRegistry` | `Registry` | Model registry | Model management |
| `MLWorkloadEndpointAdmin` | `MLAdmin` | Admin operations | Telemetry, administration |
| `MLWorkloadEndpointCognitive` | N/A | `{ML}/cognitive/` | Cognitive Services proxy |
| `MLWorkloadEndpointOpenAI` | N/A | `{ML}/cognitive/openai/` | OpenAI Services proxy |

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:14-38, 185-188]()

### Private Endpoint Support

When `WorkspacePeEnabled` is true (read from cluster metadata), Fabric uses workspace-specific private endpoints instead of shared public endpoints. The private endpoint host is constructed using the workspace ID:

```scala
val cleanedWsId = wsId.toLowerCase.replace("-", "")
val envMark = PbiEnv match {
  case "daily" | "dxt" | "msit" => s"$PbiEnv-"
  case _ => ""
}
s"https://${cleanedWsId}.z${cleanedWsId.take(2)}.${envMark}c.fabric.microsoft.com"
```

This ensures network traffic stays within private network boundaries for workspaces with private endpoint enabled.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:78-88, 140-143]()

## Telemetry and Certified Events

SynapseML integrates with Fabric's certified events telemetry system to log usage metrics. This provides visibility into feature adoption and helps track usage for capacity billing and analytics.

### Telemetry Architecture

```mermaid
flowchart TD
    subgraph "SynapseML Components"
        VWClassifier["VowpalWabbitClassifier<br/>logClass()"]
        VWRegressor["VowpalWabbitRegressor<br/>logClass()"]
        VWContextual["VowpalWabbitContextualBandit<br/>logClass()"]
        VWFeaturizer["VowpalWabbitFeaturizer<br/>logClass()"]
        OtherComponents["Other ML Components<br/>with SynapseMLLogging trait"]
    end
    
    subgraph "SynapseMLLogging"
        LogClass["logClass(featureName)"]
        LogBase["logBase()"]
        FutureCall["Future block<br/>(async execution)"]
    end
    
    subgraph "CertifiedEventClient"
        LogToCE["logToCertifiedEvents()"]
        CheckFabric["runningOnFabric()?"]
        BuildPayload["Build JSON payload:<br/>timestamp, feature_name,<br/>activity_name, attributes"]
        PostTelemetry["FabricClient.usagePost()"]
    end
    
    subgraph "FabricClient HTTP"
        GetHeaders["getHeaders()<br/>Authorization, RequestId"]
        UsagePost["usagePost(url, body)"]
        MLAdminEndpoint["MLWorkloadEndpointAdmin<br/>/telemetry"]
    end
    
    VWClassifier --> LogClass
    VWRegressor --> LogClass
    VWContextual --> LogClass
    VWFeaturizer --> LogClass
    OtherComponents --> LogClass
    
    LogClass --> LogBase
    LogBase --> FutureCall
    FutureCall --> LogToCE
    
    LogToCE --> CheckFabric
    CheckFabric -->|True| BuildPayload
    CheckFabric -->|False| Skip["Skip telemetry"]
    BuildPayload --> PostTelemetry
    
    PostTelemetry --> UsagePost
    UsagePost --> GetHeaders
    GetHeaders --> MLAdminEndpoint
```

### Certified Event Payload

Each telemetry event includes:

- **Timestamp**: Unix epoch seconds from `Instant.now().getEpochSecond`
- **Feature Name**: The library name (e.g., "SynapseML")
- **Activity Name**: The specific feature or component (e.g., "VowpalWabbit")
- **Attributes**: Empty object (extensible for future metadata)

Example payload:
```json
{
  "timestamp": 1234567890,
  "feature_name": "SynapseML",
  "activity_name": "VowpalWabbit",
  "attributes": {}
}
```

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/fabric/CertifiedEventClient.scala:13-35]()

### Asynchronous Logging

Telemetry is logged asynchronously to avoid blocking ML operations. The `logBase()` method wraps the telemetry call in a Scala `Future`:

```scala
if (featureName.isDefined) {
  Future {
    logToCertifiedEvents(
      info("libraryName"),
      featureName.get
    )
  }.failed.map {
    case e: Exception => logErrorBase("certifiedEventLogging", e)
  }
}
```

Errors in telemetry logging are caught and logged locally but don't propagate to user code, ensuring telemetry failures don't affect ML workload execution.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:127-140]()

### Feature Name Constants

Components that use certified events telemetry reference feature names from the `FeatureNames` object:

```scala
logClass(FeatureNames.VowpalWabbit)
```

This ensures consistent naming across the codebase for telemetry aggregation and reporting.

**Sources:** [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitClassifier.scala:30](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitRegressor.scala:23](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitContextualBandit.scala:110](), [vw/src/main/scala/com/microsoft/azure/synapse/ml/vw/VowpalWabbitFeaturizer.scala:29]()

## HTTP Request Infrastructure

All communication with Fabric workload endpoints uses the shared HTTP client infrastructure with platform-aware headers and authentication.

### Request Headers

The `FabricClient.getHeaders()` method constructs standard headers for all ML workload requests:

| Header | Value | Purpose |
|--------|-------|---------|
| `Authorization` | `Bearer <AAD_token>` | Authentication via Azure AD |
| `RequestId` | `UUID.randomUUID()` | Request correlation/tracing |
| `Content-Type` | `application/json` | Request body format |
| `x-ms-workload-resource-moniker` | `UUID.randomUUID()` | Workload resource tracking |

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:145-152]()

### RESTUtils Integration

`FabricClient` extends `RESTUtils` trait which provides the `usagePost()` method for making HTTP POST requests:

```scala
def usagePost(url: String, body: String): JsValue = {
  usagePost(url, body, getHeaders)
}
```

This method handles JSON serialization, HTTP communication, and response parsing, with authentication headers automatically included.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/fabric/FabricClient.scala:13, 190-192]()

## Platform-Aware Logging

The logging system integrates Fabric-specific metadata when running in Fabric environments. The `SynapseMLLogging` trait collects Hadoop configuration entries that contain Fabric workspace and capacity information.

### Hadoop Configuration Keys

```scala
val HadoopKeysToLog: mutable.Map[String, String] = mutable.Map(
  "trident.artifact.id" -> "artifactId",
  "trident.workspace.id" -> "workspaceId",
  "trident.capacity.id" -> "capacityId",
  "trident.artifact.workspace.id" -> "artifactWorkspaceId",
  "trident.lakehouse.id" -> "lakehouseId",
  "trident.activity.id" -> "livyId",
  "trident.artifact.type" -> "artifactType",
  "trident.tenant.id" -> "tenantId"
)
```

These properties are automatically included in structured log messages, enabling correlation of log entries with specific Fabric resources.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:52-62]()

### Log Message Structure

Each log entry includes standard fields:
- `modelUid`: Unique identifier for the component instance
- `className`: Fully qualified class name
- `method`: Operation being performed (e.g., "fit", "transform")
- `libraryVersion`: SynapseML version
- `libraryName`: Always "SynapseML"
- `protocolVersion`: Logging schema version
- Plus any Fabric-specific metadata from Hadoop configuration

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:19-32, 98-113]()

### SAS Token Scrubbing

All log messages are scrubbed to remove Shared Access Signature (SAS) tokens before logging. The `SASScrubber` uses regex pattern matching to replace SAS signatures with a placeholder:

```scala
val pattern = new Regex("(?i)sig=[a-z0-9%]{43,63}%3d")
pattern replaceAllIn(message, "sig=####")
```

This prevents accidental logging of sensitive credentials in telemetry or application logs.

**Sources:** [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/common/Scrubber.scala:19-24](), [core/src/main/scala/com/microsoft/azure/synapse/ml/logging/SynapseMLLogging.scala:87-91]()

## Summary

Microsoft Fabric deployment of SynapseML is characterized by:

1. **Zero-Configuration**: SynapseML is pre-installed, requiring no manual package installation
2. **Automatic Detection**: Platform detection via Trident context file enables Fabric-specific behavior
3. **Seamless Authentication**: Reflection-based token acquisition provides transparent access to Fabric services
4. **Dynamic Endpoint Resolution**: Workload endpoints adapt to environment (public/daily/dxt/msit) and private endpoint settings
5. **Integrated Telemetry**: Certified events track feature usage without impacting performance
6. **Secure Logging**: Automatic scrubbing of sensitive credentials from all log output

This integration allows data scientists to focus on ML workloads without worrying about infrastructure configuration, while providing the Fabric platform with visibility into library usage and performance metrics.

---

# Page: Databricks Deployment

# Databricks Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala](cognitive/src/test/scala/com/microsoft/azure/synapse/ml/services/anomaly/MultivariateAnamolyDetectionSuite.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala)
- [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala](core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala)
- [deep-learning/src/main/python/horovod_installation.sh](deep-learning/src/main/python/horovod_installation.sh)
- [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py](deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py)
- [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py](deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py)
- [docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb](docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb)

</details>



## Purpose and Scope

This document describes how to deploy and configure SynapseML on Databricks clusters, including installation methods, cluster configurations, library dependencies, and testing infrastructure. For general installation information across all platforms, see [Installation and Distribution](#8.1). For Azure Synapse-specific deployment, see [Azure Synapse Deployment](#8.3). For Microsoft Fabric deployment, see [Microsoft Fabric Deployment](#8.4).

## Installation Overview

SynapseML integrates with Databricks through Maven coordinate-based library installation. The system supports three primary cluster types: CPU clusters for general workloads, GPU clusters for deep learning training, and RAPIDS-enabled GPU clusters for accelerated DataFrame operations.

### Basic Installation via Maven Coordinates

```python
# Maven coordinates for SynapseML
com.microsoft.azure:synapseml_2.12:1.1.0

# Maven repository
https://mmlspark.azureedge.net/maven
```

**Sources:** [README.md:174-189]()

### Cluster Configuration Cell

The `%%configure` magic is not used on Databricks. Instead, libraries are installed at the cluster level through the Databricks UI using Maven coordinates.

## Cluster Configuration Architecture

### Cluster Types and Runtimes

```mermaid
graph TB
    subgraph "Cluster Configurations"
        CPUCluster["CPU Cluster<br/>synapseml-build-14.3"]
        GPUCluster["GPU Cluster<br/>synapseml-build-14.3-gpu"]
        RAPIDSCluster["RAPIDS Cluster<br/>synapseml-build-14.3-gpu + init scripts"]
    end
    
    subgraph "Runtime Versions"
        CPURuntime["DBR 14.3.x-scala2.12<br/>Spark 3.5"]
        GPURuntime["DBR 14.3.x-gpu-ml-scala2.12<br/>Spark 3.5 + ML"]
    end
    
    subgraph "Instance Pools"
        CPUPool["CPU Pool<br/>PoolId"]
        GPUPool["GPU Pool<br/>GpuPoolId"]
    end
    
    subgraph "Library Sets"
        StandardLibs["Standard Libraries<br/>Maven + PyPI packages"]
        GPULibs["GPU Libraries<br/>pytorch-lightning<br/>torchvision<br/>transformers"]
        RAPIDSInit["RAPIDS Init Scripts<br/>init-rapidsml-cuda-11.8.sh"]
    end
    
    CPUCluster --> CPURuntime
    CPUCluster --> CPUPool
    CPUCluster --> StandardLibs
    
    GPUCluster --> GPURuntime
    GPUCluster --> GPUPool
    GPUCluster --> GPULibs
    
    RAPIDSCluster --> GPURuntime
    RAPIDSCluster --> GPUPool
    RAPIDSCluster --> GPULibs
    RAPIDSCluster --> RAPIDSInit
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:34-51]()

### Cluster Creation Parameters

| Parameter | CPU Cluster | GPU Cluster | RAPIDS Cluster |
|-----------|-------------|-------------|----------------|
| Runtime | `14.3.x-scala2.12` | `14.3.x-gpu-ml-scala2.12` | `14.3.x-gpu-ml-scala2.12` |
| Pool Name | `synapseml-build-14.3` | `synapseml-build-14.3-gpu` | `synapseml-build-14.3-gpu` |
| Num Workers | 5 | 2 | 1 |
| Auto-termination | 15 minutes | 15 minutes | 15 minutes |
| Init Scripts | None | None | `/InitScripts/init-rapidsml-cuda-11.8.sh` |
| Memory Config | Optional: 7g | Default | Default |

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:34-51](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:12](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:10](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:10]()

## Library Dependencies

### Core Library Dependencies

The `Libraries` constant defines the standard package set for CPU clusters:

```mermaid
graph LR
    subgraph "Maven Libraries"
        MavenCoord["com.microsoft.azure:synapseml_2.12:VERSION<br/>Repository: mmlspark.azureedge.net/maven"]
    end
    
    subgraph "PyPI Packages - Core"
        nltk["nltk"]
        bs4["bs4"]
        plotly["plotly"]
        Pillow["Pillow"]
    end
    
    subgraph "PyPI Packages - ML"
        onnxmltools["onnxmltools==1.7.0"]
        lightgbm["lightgbm"]
        mlflow["mlflow==2.21.3"]
        openai["openai==0.28.1"]
        langchain["langchain==0.0.331"]
    end
    
    subgraph "PyPI Packages - Document Processing"
        pdf2image["pdf2image"]
        pdfminer["pdfminer.six"]
        sqlparse["sqlparse"]
        unstructured["unstructured==0.10.24"]
        pytesseract["pytesseract"]
    end
    
    subgraph "PyPI Packages - Interpretability"
        interpret["interpret-community"]
        numpy["numpy==1.26.4"]
    end
    
    MavenCoord --> SynapseMLJAR["SynapseML JAR"]
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:56-74](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:78-82]()

### GPU-Specific Library Dependencies

The `GPULibraries` constant defines additional packages for GPU and deep learning workloads:

```json
[
  {
    "maven": {
      "coordinates": "com.microsoft.azure:synapseml_2.12:VERSION",
      "repo": "https://mmlspark.azureedge.net/maven"
    }
  },
  {
    "pypi": {
      "package": "pytorch-lightning==1.5.0"
    }
  },
  {
    "pypi": {
      "package": "torchvision==0.15.1"
    }
  },
  {
    "pypi": {
      "package": "transformers==4.49.0"
    }
  },
  {
    "pypi": {
      "package": "jinja2==3.1.6"
    }
  },
  {
    "pypi": {
      "package": "petastorm==0.12.1"
    }
  },
  {
    "pypi": {
      "package": "protobuf==5.29.4"
    }
  },
  {
    "pypi": {
      "package": "accelerate==0.26.0"
    }
  }
]
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:84-93]()

### RAPIDS Configuration

RAPIDS clusters require initialization scripts for CUDA setup:

```mermaid
graph LR
    InitScript["/InitScripts/init-rapidsml-cuda-11.8.sh"]
    
    InitScript --> SetupRAPIDSML["Configure RAPIDS ML<br/>CUDA 11.8 environment"]
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:95-97]()

## Databricks REST API Integration

### API Client Architecture

```mermaid
graph TB
    subgraph "Authentication"
        Token["Databricks Token<br/>env: MML_ADB_TOKEN"]
        AuthValue["Authorization Header<br/>Basic base64(token:TOKEN)"]
    end
    
    subgraph "API Endpoints"
        ClustersAPI["Clusters API<br/>/api/2.0/clusters/*"]
        LibrariesAPI["Libraries API<br/>/api/2.0/libraries/*"]
        WorkspaceAPI["Workspace API<br/>/api/2.0/workspace/*"]
        JobsAPI["Jobs API<br/>/api/2.0/jobs/*"]
        PoolsAPI["Instance Pools API<br/>/api/2.0/instance-pools/*"]
        DBFSAPI["DBFS API<br/>/api/2.0/dbfs/*"]
    end
    
    subgraph "DatabricksUtilities Functions"
        databricksGet["databricksGet()<br/>GET requests"]
        databricksPost["databricksPost()<br/>POST requests"]
    end
    
    subgraph "Operations"
        ClusterOps["createClusterInPool()<br/>terminateCluster()<br/>restartCluster()<br/>isClusterActive()"]
        LibraryOps["installLibraries()<br/>uninstallLibraries()<br/>areLibrariesInstalled()<br/>listInstalledLibraries()"]
        WorkspaceOps["workspaceMkDir()<br/>uploadNotebook()<br/>workspaceRmDir()"]
        JobOps["submitRun()<br/>monitorJob()<br/>cancelRun()<br/>listActiveJobs()"]
    end
    
    Token --> AuthValue
    AuthValue --> databricksGet
    AuthValue --> databricksPost
    
    databricksGet --> ClustersAPI
    databricksGet --> LibrariesAPI
    databricksGet --> WorkspaceAPI
    databricksGet --> JobsAPI
    databricksGet --> PoolsAPI
    
    databricksPost --> ClustersAPI
    databricksPost --> LibrariesAPI
    databricksPost --> WorkspaceAPI
    databricksPost --> JobsAPI
    databricksPost --> DBFSAPI
    
    ClustersAPI --> ClusterOps
    LibrariesAPI --> LibraryOps
    WorkspaceAPI --> WorkspaceOps
    JobsAPI --> JobOps
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:43-46](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:76](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:126-141]()

### Key API Functions

The `DatabricksUtilities` object provides the following key functions for cluster and job management:

| Function | Purpose | API Endpoint |
|----------|---------|--------------|
| `getPoolIdByName()` | Retrieve instance pool ID | `instance-pools/list` |
| `createClusterInPool()` | Create cluster in instance pool | `clusters/create` |
| `isClusterActive()` | Check cluster status | `clusters/get` |
| `installLibraries()` | Install libraries on cluster | `libraries/install` |
| `areLibrariesInstalled()` | Check library installation status | `libraries/cluster-status` |
| `uploadNotebook()` | Upload notebook to workspace | `workspace/import` |
| `submitRun()` | Submit notebook job run | `jobs/runs/submit` |
| `monitorJob()` | Monitor job execution | `jobs/runs/get` |
| `terminateCluster()` | Terminate cluster | `clusters/delete` |
| `permanentDeleteCluster()` | Permanently delete cluster | `clusters/permanent-delete` |

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:143-426]()

## Testing Infrastructure

### Test Suite Architecture

```mermaid
graph TB
    subgraph "Test Base Classes"
        DatabricksTestHelper["DatabricksTestHelper<br/>Abstract base class"]
    end
    
    subgraph "Test Implementations"
        DatabricksCPUTests["DatabricksCPUTests<br/>CPU cluster testing"]
        DatabricksGPUTests["DatabricksGPUTests<br/>GPU cluster testing"]
        DatabricksRapidsTests["DatabricksRapidsTests<br/>RAPIDS cluster testing"]
    end
    
    subgraph "Test Execution Flow"
        CreateCluster["createClusterInPool()"]
        WaitActive["isClusterActive() + retry"]
        InstallLibs["installLibraries()"]
        WaitLibs["areLibrariesInstalled() + retry"]
        RunNotebooks["runNotebook() parallel"]
        MonitorJobs["monitorJob() per notebook"]
        Cleanup["afterAllHelper()"]
    end
    
    subgraph "Notebook Collections"
        CPUNotebooks["CPUNotebooks<br/>~40+ notebooks"]
        GPUNotebooks["GPUNotebooks<br/>Fine-tune + Phi Model"]
        RapidsNotebooks["RapidsNotebooks<br/>GPU-accelerated notebooks"]
    end
    
    DatabricksTestHelper --> DatabricksCPUTests
    DatabricksTestHelper --> DatabricksGPUTests
    DatabricksTestHelper --> DatabricksRapidsTests
    
    DatabricksCPUTests --> CreateCluster
    DatabricksGPUTests --> CreateCluster
    DatabricksRapidsTests --> CreateCluster
    
    CreateCluster --> WaitActive
    WaitActive --> InstallLibs
    InstallLibs --> WaitLibs
    WaitLibs --> RunNotebooks
    RunNotebooks --> MonitorJobs
    MonitorJobs --> Cleanup
    
    DatabricksCPUTests --> CPUNotebooks
    DatabricksGPUTests --> GPUNotebooks
    DatabricksRapidsTests --> RapidsNotebooks
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:432-487](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:1-25](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:1-19](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:1-19]()

### Test Helper Methods

The `databricksTestHelper()` method orchestrates the complete test workflow:

```scala
def databricksTestHelper(
  clusterId: String,
  libraries: String,
  notebooks: Seq[File],
  maxConcurrency: Int,
  retries: List[Int] = List(1000 * 15)
): Unit
```

**Test Workflow:**
1. Wait for cluster to become active (up to 20 minutes, polling every 1 second)
2. Install libraries on cluster
3. Wait for library installation (up to 6 minutes, polling every 1 second)
4. Execute notebooks in parallel with configurable concurrency
5. Monitor each notebook run with timeout of 50 minutes
6. Retry failed notebooks based on retry configuration

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:436-472]()

### Notebook Categorization

The test system categorizes notebooks based on their resource requirements:

```mermaid
graph TB
    AllNotebooks["All .ipynb files<br/>from docs/ directory"]
    
    AllNotebooks --> CPUFilter["CPU Filter<br/>Exclude: Fine-tune, GPU, Phi Model,<br/>Language Model, Multivariate Anomaly,<br/>Audiobooks, Art, Explanation Dashboard,<br/>Isolation Forests, Snow Leopard"]
    AllNotebooks --> GPUFilter["GPU Filter<br/>Include: Fine-tune, Phi Model"]
    AllNotebooks --> RAPIDSFilter["RAPIDS Filter<br/>Include: GPU keyword"]
    
    CPUFilter --> CPUNotebooks["CPUNotebooks<br/>Max Concurrency: 5"]
    GPUFilter --> GPUNotebooks["GPUNotebooks<br/>Max Concurrency: 1"]
    RAPIDSFilter --> RapidsNotebooks["RapidsNotebooks<br/>Max Concurrency: 4"]
```

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:102-124]()

### Job Monitoring

The `monitorJob()` function tracks notebook execution:

```mermaid
graph LR
    Start["Start Monitoring"]
    CheckStatus["getRunStatuses()<br/>life_cycle_state"]
    
    Start --> CheckStatus
    
    CheckStatus -->|TERMINATED + SUCCESS| Success["Log Success"]
    CheckStatus -->|TERMINATED + other| Failure["Throw RuntimeException"]
    CheckStatus -->|INTERNAL_ERROR| Error["Throw RuntimeException"]
    CheckStatus -->|Timeout| Timeout["Throw TimeoutException"]
    CheckStatus -->|Running| Sleep["Sleep 10s + jitter"]
    
    Sleep --> CheckStatus
```

Parameters:
- **Timeout:** 50 minutes (`TimeoutInMillis`)
- **Polling Interval:** 10 seconds + random jitter (0-1000ms)
- **Log Level:** Configurable (0=minimal, 1=normal, 2=verbose)

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:100](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:328-366]()

## Deep Learning Configuration

### Horovod Installation for GPU Clusters

Deep learning models using `DeepTextClassifier` and `DeepVisionClassifier` require Horovod with NCCL support. The installation script handles CUDA setup:

```mermaid
graph TB
    Prerequisites["Install Prerequisites<br/>pytorch-lightning==1.5.0<br/>torchvision==0.15.1<br/>transformers==4.49.0<br/>petastorm>=0.12.1<br/>protobuf==5.29.4"]
    
    CUDAKey["Update CUDA Signing Keys<br/>Remove outdated key<br/>Install cuda-keyring"]
    
    NVMLRepo["Install NVIDIA ML Repository<br/>Ubuntu 20.04 packages"]
    
    CUDAPackages["Install CUDA 11.0 Packages<br/>cuda-nvml-dev-11-0<br/>cuda-nvcc-11-0<br/>cuda-cudart-dev-11-0<br/>cuda-libraries-dev-11-0<br/>libnccl-dev=2.10.3-1+cuda11.0<br/>libcusparse-dev-11-0"]
    
    HorovodBuild["Build Horovod from Source<br/>Commit: 1d217b59949986d025f6db93c49943fb6b6cc78f<br/>HOROVOD_GPU_ALLREDUCE=NCCL<br/>HOROVOD_CUDA_HOME=/usr/local/cuda-11/<br/>HOROVOD_WITH_PYTORCH=1<br/>HOROVOD_WITHOUT_MXNET=1"]
    
    HorovodInstall["Install Horovod Wheel<br/>horovod-0.28.1-cp38-cp38-linux_x86_64.whl"]
    
    Prerequisites --> CUDAKey
    CUDAKey --> NVMLRepo
    NVMLRepo --> CUDAPackages
    CUDAPackages --> HorovodBuild
    HorovodBuild --> HorovodInstall
```

**Sources:** [deep-learning/src/main/python/horovod_installation.sh:1-48]()

### Deep Learning Model Requirements

Both `DeepTextClassifier` and `DeepVisionClassifier` have specific version requirements:

| Component | Required Version | Purpose |
|-----------|------------------|---------|
| `horovod` | 0.28.1 | Distributed training framework |
| `pytorch-lightning` | 1.5.0 | Training orchestration |
| `torchvision` | 0.15.1 | Vision model backbones |
| `transformers` | 4.49.0 | Text model backbones |
| `petastorm` | 0.12.1+ | Spark-to-PyTorch data conversion |
| `protobuf` | 5.29.4 | Serialization |
| `accelerate` | 0.26.0 | Model optimization |

**Sources:** [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:10-24](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:18-28](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:12-26](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:15-27]()

### Deep Learning Model Architecture

```mermaid
graph TB
    subgraph "Text Classification Pipeline"
        DeepTextClassifier["DeepTextClassifier<br/>TorchEstimator"]
        LitDeepTextModel["LitDeepTextModel<br/>pl.LightningModule"]
        AutoModelForSeq["AutoModelForSequenceClassification<br/>from transformers"]
        AutoTokenizer["AutoTokenizer<br/>from transformers"]
    end
    
    subgraph "Vision Classification Pipeline"
        DeepVisionClassifier["DeepVisionClassifier<br/>TorchEstimator"]
        LitDeepVisionModel["LitDeepVisionModel<br/>pl.LightningModule"]
        TorchvisionModels["torchvision.models<br/>Various backbones"]
    end
    
    subgraph "Training Backend"
        HorovodBackend["Horovod SparkBackend<br/>get_or_create_backend()"]
    end
    
    DeepTextClassifier --> LitDeepTextModel
    LitDeepTextModel --> AutoModelForSeq
    DeepTextClassifier --> AutoTokenizer
    DeepTextClassifier --> HorovodBackend
    
    DeepVisionClassifier --> LitDeepVisionModel
    LitDeepVisionModel --> TorchvisionModels
    DeepVisionClassifier --> HorovodBackend
```

**Sources:** [deep-learning/src/main/python/synapse/ml/dl/DeepTextClassifier.py:27-289](), [deep-learning/src/main/python/synapse/ml/dl/DeepVisionClassifier.py:31-269](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:29-177](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepVisionModel.py:30-234]()

## Example Notebooks and Workspace Setup

### Notebook Import Process

```mermaid
graph LR
    LocalNotebook["Local .ipynb File"]
    Base64Encode["Base64 Encode Content"]
    WorkspaceMkDir["workspaceMkDir()<br/>Create folder structure"]
    UploadNotebook["uploadNotebook()<br/>POST workspace/import"]
    WorkspacePath["Workspace Path<br/>/SynapseMLBuild/build_VERSION/..."]
    
    LocalNotebook --> Base64Encode
    Base64Encode --> WorkspaceMkDir
    WorkspaceMkDir --> UploadNotebook
    UploadNotebook --> WorkspacePath
```

**Notebook Upload Parameters:**
- **Content:** Base64-encoded notebook file
- **Path:** `/SynapseMLBuild/build_{version}/{relative_path}/{notebook_name}`
- **Format:** `JUPYTER`
- **Overwrite:** `true`

**Sources:** [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:53](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:163-177](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:368-380]()

### Example: CyberML Notebook Configuration

The CyberML anomalous access detection notebook demonstrates platform-specific configuration:

```python
from synapse.ml.core.platform import running_on_databricks, running_on_synapse

if running_on_databricks():
    spark.sparkContext.setCheckpointDir("dbfs:/checkpoint_path/")
else:
    spark.sparkContext.setCheckpointDir("./tmp/checkpoint_path/")
```

**Sources:** [docs/Explore Algorithms/Other Algorithms/Quickstart - Anomalous Access Detection.ipynb:97-102]()

## Installation Instructions for End Users

### Step 1: Create Library in Databricks

1. Navigate to the Databricks workspace
2. Go to **Workspace** → **Shared** → **Create** → **Library**
3. Select **Maven** as the library source
4. Enter coordinates:
   ```
   com.microsoft.azure:synapseml_2.12:1.1.0
   ```
5. Enter repository:
   ```
   https://mmlspark.azureedge.net/maven
   ```
6. Click **Create**

### Step 2: Attach Library to Cluster

1. Select the created library
2. Click **Install**
3. Select target cluster(s)
4. Wait for installation to complete (status: **Installed**)

### Step 3: Verify Installation

```python
import synapse.ml
print(synapse.ml.__version__)
```

### Step 4: Import Example Notebooks

Import the example notebook archive to get started:

```
https://mmlspark.blob.core.windows.net/dbcs/SynapseMLExamplesv1.1.0.dbc
```

1. Navigate to **Workspace** → **Users** → **Your User**
2. Click dropdown → **Import**
3. Select **URL** and paste the archive URL
4. Click **Import**

**Sources:** [README.md:176-189]()

## Cluster Requirements and Compatibility

### Minimum Requirements

| Component | Minimum Version |
|-----------|----------------|
| Spark | 3.2 |
| Scala | 2.12 |
| Databricks Runtime | 10.1+ (for Netty compatibility) |
| Python | 3.8+ |

### Recommended Configurations

**CPU Clusters:**
- Runtime: DBR 14.3 LTS
- Worker Memory: 7GB+ for large models
- Workers: 5+ for parallel notebook execution

**GPU Clusters:**
- Runtime: DBR 14.3 ML GPU
- GPU Type: NVIDIA with CUDA 11.0+
- Workers: 2+ for distributed training
- Init Scripts: Not required for standard workloads

**RAPIDS Clusters:**
- Runtime: DBR 14.3 ML GPU  
- GPU Type: NVIDIA with CUDA 11.8
- Workers: 1-4 (RAPIDS handles parallelism differently)
- Init Scripts: `/InitScripts/init-rapidsml-cuda-11.8.sh` required

**Sources:** [README.md:185-186](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:34-51]()

## Troubleshooting

### Common Issues

**Netty Dependency Conflicts:**
- Use DBR 10.1 or later
- SynapseML includes specific Netty version exclusions

**Library Installation Failures:**
- Check that the Maven repository URL is correct: `https://mmlspark.azureedge.net/maven`
- Verify cluster has internet access
- Review library status logs for specific error messages

**GPU/RAPIDS Setup Issues:**
- Ensure GPU runtime is selected (not CPU runtime)
- Verify init scripts are properly configured for RAPIDS
- Check CUDA version compatibility

**Notebook Execution Timeouts:**
- Default timeout is 50 minutes per notebook
- Large model training may require timeout adjustment
- Monitor cluster resource utilization

**Sources:** [README.md:185-186](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksUtilities.scala:100]()

---

# Page: Standalone and Other Platforms

# Standalone and Other Platforms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



This page covers deployment options for SynapseML outside of the major cloud platforms (Fabric, Synapse, Databricks). These include Python standalone installations, spark-submit command-line usage, SBT builds, Apache Livy/HDInsight, R language bindings, and building from source. For cloud platform deployments, see pages 8.3, 8.4, and 8.5.

## Overview of Standalone Deployment Options

SynapseML supports several deployment scenarios beyond managed cloud platforms, enabling usage in local development environments, custom Spark clusters, and build systems.

```mermaid
graph TB
    subgraph "Standalone Deployment Options"
        Python["Python Standalone<br/>pip install pyspark"]
        SparkSubmit["spark-submit<br/>--packages option"]
        SBT["SBT Build<br/>libraryDependencies"]
        Livy["Apache Livy<br/>%%configure magic"]
        R["R Language<br/>SparkR wrappers"]
        Source["Build from Source<br/>SBT compile"]
    end
    
    Python --> |"Local Spark Session"| LocalSpark["pyspark.sql.SparkSession"]
    SparkSubmit --> |"Command Line"| CommandLine["spark-shell, pyspark"]
    SBT --> |"Scala Project"| ScalaApp["Spark Application"]
    Livy --> |"Jupyter Notebook"| HDInsight["HDInsight Cluster"]
    R --> |"R Environment"| RSession["SparkR Session"]
    Source --> |"Development"| DevEnv["IDE Integration"]
```

Sources: [README.md:72-92]()

## Python Standalone Deployment

Python standalone deployment enables SynapseML usage in local Python environments without requiring a managed cloud platform. This approach is suitable for development, testing, and small-scale workloads.

### Installation Process

The Python standalone deployment requires two steps:

1. **Install PySpark**: `pip install pyspark`
2. **Configure SynapseML packages** when creating the SparkSession

```mermaid
graph LR
    subgraph "Python Standalone Setup"
        PipInstall["pip install pyspark"] --> CreateSession["Create SparkSession"]
        CreateSession --> ConfigPackages["config spark.jars.packages"]
        ConfigPackages --> ImportSynapse["import synapse.ml"]
        ImportSynapse --> UseAPIs["Use SynapseML APIs"]
    end
```

### SparkSession Configuration

The key configuration parameter is `spark.jars.packages`, which tells Spark to download SynapseML from Maven at runtime:

```python
import pyspark
spark = pyspark.sql.SparkSession.builder.appName("MyApp") \
            .config("spark.jars.packages", "com.microsoft.azure:synapseml_2.12:1.1.0") \
            .getOrCreate()
import synapse.ml
```

This configuration triggers Maven dependency resolution through the `pyspark.sql.SparkSession.builder` API, downloading SynapseML JARs and their dependencies automatically.

Sources: [README.md:191-203]()

### Use Cases

Python standalone deployment is appropriate for:

| Use Case | Description |
|----------|-------------|
| Local Development | Test SynapseML code on a development machine |
| CI/CD Testing | Run unit tests in automated pipelines |
| Small Datasets | Process data that fits on a single machine |
| Prototyping | Experiment with SynapseML APIs before cloud deployment |

Sources: [README.md:191-203]()

## spark-submit Deployment

The `spark-submit` command provides a standard way to deploy SynapseML to existing Spark clusters. This method uses the `--packages` option to automatically download and include SynapseML dependencies.

### Command-Line Usage

SynapseML can be added to any Spark application using the `--packages` flag:

```bash
spark-shell --packages com.microsoft.azure:synapseml_2.12:1.1.0
pyspark --packages com.microsoft.azure:synapseml_2.12:1.1.0
spark-submit --packages com.microsoft.azure:synapseml_2.12:1.1.0 MyApp.jar
```

```mermaid
graph TB
    subgraph "spark-submit Deployment Flow"
        Command["spark-submit --packages"] --> |"Maven Resolution"| Download["Download from<br/>mmlspark.azureedge.net/maven"]
        Download --> |"Extract JARs"| Classpath["Add to Spark Classpath"]
        Classpath --> |"Launch"| App["Application Execution"]
    end
    
    subgraph "Supported Commands"
        SparkShell["spark-shell<br/>(Scala REPL)"]
        PySpark["pyspark<br/>(Python REPL)"]
        SparkSubmit["spark-submit<br/>(Application JAR)"]
    end
    
    SparkShell --> Command
    PySpark --> Command
    SparkSubmit --> Command
```

Sources: [README.md:205-214]()

### Package Resolution

When using `--packages`, Spark performs the following steps:

1. **Parse Maven coordinates**: `com.microsoft.azure:synapseml_2.12:1.1.0`
2. **Resolve dependencies**: Download transitive dependencies from Maven repositories
3. **Add to classpath**: Include all JARs in the Spark driver and executor classpaths

The Maven repository URL is configured by default but can be overridden with `--repositories`:

```bash
spark-submit --packages com.microsoft.azure:synapseml_2.12:1.1.0 \
             --repositories https://mmlspark.azureedge.net/maven \
             MyApp.jar
```

Sources: [README.md:205-214]()

### Application Deployment

For submitting pre-built Spark applications (JAR files), use `spark-submit` with the `--packages` option:

```bash
spark-submit \
  --packages com.microsoft.azure:synapseml_2.12:1.1.0 \
  --class com.example.MyMLApp \
  myapp.jar
```

This deployment method is commonly used in production environments where applications are packaged as JAR files and deployed to existing Spark clusters.

Sources: [README.md:205-214]()

## SBT Deployment

For Scala developers building Spark applications with SBT (Simple Build Tool), SynapseML can be included as a library dependency in the project's `build.sbt` file.

### build.sbt Configuration

Add SynapseML as a library dependency in your `build.sbt`:

```scala
libraryDependencies += "com.microsoft.azure" % "synapseml_2.12" % "1.1.0"
```

```mermaid
graph TB
    subgraph "SBT Build Process"
        BuildSBT["build.sbt<br/>libraryDependencies"] --> SBTResolve["SBT Dependency<br/>Resolution"]
        SBTResolve --> |"Download JARs"| LocalCache["~/.ivy2/cache"]
        LocalCache --> Compile["sbt compile"]
        Compile --> Package["sbt package"]
        Package --> JAR["Application JAR"]
    end
    
    subgraph "SBT Commands"
        SBTCompile["sbt compile"]
        SBTTest["sbt test"]
        SBTPackage["sbt package"]
        SBTRun["sbt run"]
    end
```

Sources: [README.md:216-223]()

### Maven Repository Configuration

By default, SBT uses Maven Central and standard Scala repositories. For SynapseML, the custom Maven repository is already configured in the artifact metadata, so no additional resolver configuration is typically needed. However, if needed, you can explicitly add the repository:

```scala
resolvers += "SynapseML" at "https://mmlspark.azureedge.net/maven"
```

### Project Structure

A typical SBT project using SynapseML has this structure:

```
myproject/
├── build.sbt                    # Project configuration
├── project/
│   └── build.properties         # SBT version
└── src/
    └── main/
        └── scala/
            └── MyApp.scala      # Spark application code
```

Sources: [README.md:216-223]()

### Build and Package

To build a Scala application with SynapseML:

1. **Compile**: `sbt compile` - Compiles Scala sources
2. **Test**: `sbt test` - Runs test suites
3. **Package**: `sbt package` - Creates application JAR
4. **Run**: `sbt run` - Executes the main class locally

The resulting JAR can be deployed using `spark-submit` as described in the previous section.

Sources: [README.md:216-223]()

## Apache Livy and HDInsight

Apache Livy provides a REST interface for Spark clusters and is used in Azure HDInsight for running Spark jobs. SynapseML can be installed in Livy-based notebooks using the `%%configure` magic command.

### Configuration Magic

To install SynapseML in a Jupyter notebook served by Apache Livy:

```bash
%%configure -f
{
    "name": "synapseml",
    "conf": {
        "spark.jars.packages": "com.microsoft.azure:synapseml_2.12:1.1.0",
        "spark.jars.excludes": "org.scala-lang:scala-reflect,org.apache.spark:spark-tags_2.12,org.scalactic:scalactic_2.12,org.scalatest:scalatest_2.12,com.fasterxml.jackson.core:jackson-databind"
    }
}
```

```mermaid
graph TB
    subgraph "Apache Livy Deployment"
        JupyterNB["Jupyter Notebook"] --> ConfigureMagic["%%configure -f magic"]
        ConfigureMagic --> |"REST API"| LivyServer["Livy Server"]
        LivyServer --> |"Create Session"| SparkSession["Spark Session<br/>with SynapseML"]
        SparkSession --> ExecuteCode["Execute Notebook<br/>Cells"]
    end
    
    subgraph "Livy Session Lifecycle"
        CreateSession["Create Session<br/>POST /sessions"]
        SubmitCode["Submit Code<br/>POST /sessions/:id/statements"]
        GetResults["Get Results<br/>GET /sessions/:id/statements/:id"]
        DeleteSession["Delete Session<br/>DELETE /sessions/:id"]
        
        CreateSession --> SubmitCode
        SubmitCode --> GetResults
        GetResults --> DeleteSession
    end
```

Sources: [README.md:225-240]()

### Session Management

**Important**: A new Spark session must be started after executing the `%%configure` cell. The `-f` flag forces the creation of a new session with the specified configuration.

### HDInsight-Specific Considerations

When using HDInsight, certain packages must be excluded to avoid conflicts with the pre-installed libraries. The `spark.jars.excludes` configuration addresses compatibility issues with Livy 0.5.

| Excluded Package | Reason |
|-----------------|---------|
| `org.scala-lang:scala-reflect` | Conflicts with cluster Scala version |
| `org.apache.spark:spark-tags_2.12` | Already present in cluster |
| `org.scalactic:scalactic_2.12` | Testing library not needed at runtime |
| `org.scalatest:scalatest_2.12` | Testing library not needed at runtime |
| `com.fasterxml.jackson.core:jackson-databind` | Version conflicts with cluster Jackson |

Sources: [README.md:225-240]()

### Livy REST API Integration

Livy exposes Spark functionality through REST endpoints. The `%%configure` magic translates to Livy API calls:

1. **Session Creation**: `POST /sessions` with configuration JSON
2. **Code Execution**: `POST /sessions/{sessionId}/statements` with code
3. **Result Retrieval**: `GET /sessions/{sessionId}/statements/{statementId}`

Sources: [README.md:225-240]()

## R Language Deployment

SynapseML provides R language bindings through auto-generated SparkR wrappers, enabling R developers to use SynapseML algorithms in their workflows.

### R Setup

To use SynapseML from R, follow the instructions in the R Setup documentation. The R bindings are generated automatically from the Scala implementations, providing a consistent API across languages.

```mermaid
graph LR
    subgraph "R Binding Generation"
        ScalaCode["Scala PipelineStage"] --> Codegen["Wrapper Generation"]
        Codegen --> RWrapper["R S4 Class"]
        RWrapper --> SparkR["SparkR Backend"]
    end
    
    subgraph "R Usage"
        RScript["R Script"] --> LoadLibrary["library(synapseml)"]
        LoadLibrary --> CreateModel["Create Model Objects"]
        CreateModel --> FitTransform["Fit/Transform"]
    end
```

Sources: [README.md:256-260]()

### Current Status

The R bindings are under active development. Some custom wrappers may be missing for specialized functionality. For the most complete experience, Python or Scala APIs are recommended.

| Feature | Status |
|---------|--------|
| Core Transformers | Supported |
| LightGBM | Supported |
| Cognitive Services | Supported |
| Deep Learning | Partial Support |
| Custom Wrappers | In Development |

Sources: [README.md:256-260]()

## Building from Source

For developers contributing to SynapseML or requiring customized builds, the project can be built from source using SBT.

### Development Setup

SynapseML uses a modular build infrastructure that supports platform-independent development. The build system integrates with IntelliJ IDEA and SBT for development workflows.

```mermaid
graph TB
    subgraph "Build from Source Process"
        Clone["git clone"] --> Setup["Development Setup"]
        Setup --> SBTCompile["sbt compile"]
        SBTCompile --> SBTTest["sbt test"]
        SBTTest --> SBTPackage["sbt package"]
        
        subgraph "Build Outputs"
            JARs["JAR Files<br/>target/scala-2.12/"]
            PythonWheel["Python Wheel<br/>pip/dist/"]
            RPkg["R Package<br/>R/"]
        end
        
        SBTPackage --> JARs
        SBTPackage --> PythonWheel
        SBTPackage --> RPkg
    end
```

Sources: [README.md:262-270]()

### Build System Architecture

The SynapseML build system uses SBT with multiple sub-projects:

- **core**: Core functionality and utilities
- **cognitive**: Azure Cognitive Services integration
- **deep-learning**: Deep learning components (ONNX, Horovod)
- **lightgbm**: LightGBM integration
- **vw**: Vowpal Wabbit integration
- **opencv**: OpenCV integration

Each sub-project can be built independently or as part of the full build.

Sources: [README.md:262-270]()

### Developer Documentation

Detailed instructions for development setup, including IDE configuration and build commands, are available in the Developer Setup documentation. This includes:

- Platform-independent setup instructions
- IntelliJ IDEA integration
- SBT configuration
- Testing procedures
- Code generation for Python/R bindings

For issues during development setup, contact the SynapseML support team.

Sources: [README.md:262-270]()

## Deployment Comparison

The following table compares the different standalone deployment options:

| Deployment Method | Use Case | Installation Complexity | Platform Independence | Best For |
|-------------------|----------|------------------------|-----------------------|----------|
| Python Standalone | Local development, testing | Low | High | Quick prototyping |
| spark-submit | Production clusters, automation | Low | High | Existing Spark infrastructure |
| SBT | Scala application development | Medium | High | Custom Spark applications |
| Apache Livy / HDInsight | Notebook-based workflows | Medium | Medium | Interactive analysis on HDInsight |
| R | R language developers | Medium | Medium | R-based data science workflows |
| Build from Source | Contributing, customization | High | High | Development and contributions |

Sources: [README.md:191-270]()

## Version Management

### Maven Coordinates Format

All standalone deployments use Maven coordinates to specify SynapseML:

```
com.microsoft.azure:synapseml_2.12:1.1.0
       ^                  ^        ^    ^
       |                  |        |    |
    Group ID          Artifact  Scala  Version
                                Version
```

### Current Versions

| SynapseML Version | Spark Version | Scala Version | Status |
|-------------------|---------------|---------------|--------|
| 1.1.0 | 3.5+ | 2.12 | Latest Stable |
| 1.0.15 | 3.4 | 2.12 | Stable |
| 0.11.4-spark3.3 | 3.3 | 2.12 | Legacy |

Sources: [README.md:9-18]()

## Maven Repository Configuration

All standalone deployments resolve dependencies from the SynapseML Maven repository:

**Repository URL**: `https://mmlspark.azureedge.net/maven`

This repository is automatically configured in the artifact metadata for most deployment scenarios. For manual configuration:

- **spark-submit**: Use `--repositories` flag
- **SBT**: Add to `resolvers` in `build.sbt`
- **Maven**: Add `<repository>` to `pom.xml`

Sources: [README.md:107, 182, 222]()

## Deployment Architecture

The following diagram illustrates how SynapseML components interact with cloud platforms and underlying infrastructure:

```mermaid
graph TD
    subgraph "Cloud Deployment Architecture"
        subgraph "User Interface"
            Notebook["Notebook Environment"]
        end
        
        subgraph "SynapseML Framework"
            Core["Core Components"]
            AI["AI Services Integration"]
            DL["Deep Learning"]
            HTTP["HTTP Client System"]
        end
        
        subgraph "Execution Environment"
            Spark["Apache Spark"]
            GPU["GPU Acceleration"]
            CPURes["CPU Resources"]
            Storage["Cloud Storage"]
        end
        
        Notebook --> Core
        Notebook --> AI
        Notebook --> DL
        
        Core --> Spark
        AI --> HTTP
        AI --> Spark
        DL --> GPU
        DL --> Spark
        
        Spark --> CPURes
        Spark --> Storage
    end
```

Sources: [README.md:47-65]()

## Testing Cloud Deployments

SynapseML includes a comprehensive testing infrastructure to ensure proper functionality across different cloud platforms.

### Databricks Testing

The framework includes utilities for testing on Databricks clusters, supporting both CPU and GPU tests:

- `DatabricksCPUTests`: Tests on standard Databricks clusters
- `DatabricksGPUTests`: Tests on GPU-enabled clusters
- `DatabricksRapidsTests`: Tests for RAPIDS acceleration on GPU clusters

### Azure Synapse Testing

Synapse-specific tests are implemented in `SynapseTests` which:
- Creates temporary Spark pools for testing
- Uploads and executes notebooks
- Manages Livy batch execution
- Cleans up resources after testing

```mermaid
graph TD
    subgraph "Cloud Deployment Testing Infrastructure"
        subgraph "Databricks Testing"
            DCPU["DatabricksCPUTests"]
            DGPU["DatabricksGPUTests"]
            DRapids["DatabricksRapidsTests"]
        end
        
        subgraph "Synapse Testing"
            ST["SynapseTests"]
            SP["SparkPool Creation"]
            LB["Livy Batch Execution"]
            NB["Notebook Testing"]
        end
        
        DCPU --> |"Tests on CPU Clusters"| DBTest["Databricks Test Runner"]
        DGPU --> |"Tests on GPU Clusters"| DBTest
        DRapids --> |"Tests with RAPIDS"| DBTest
        
        ST --> SP
        SP --> LB
        LB --> NB
    end
```

Sources: [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksCPUTests.scala:1-26](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksGPUTests.scala:1-19](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/DatabricksRapidsTests.scala:1-20](), [core/src/test/scala/com/microsoft/azure/synapse/ml/nbtest/SynapseTests.scala:1-113]()

## Troubleshooting Cloud Deployments

Common issues when deploying SynapseML to cloud environments and their solutions:

### Dependency Conflicts

SynapseML requires specific versions of dependencies. Common issues include:

- **Netty dependency issues**: Use the exclusion pattern in the configuration to avoid conflicts
- **Transformers version mismatch**: Ensure you're using the correct version (4.49.0 for current SynapseML)
- **Horovod compatibility**: Version 0.28.1 is required for deep learning features

### Platform-Specific Issues

| Platform | Common Issue | Solution |
|----------|--------------|----------|
| Databricks | Netty dependency conflicts | Use DBR 10.1+ or add exclusions |
| Synapse | Package not found | Check spark.jars.repositories setting |
| Fabric | Version conflicts | Ensure proper exclusions in configuration |
| All | Memory issues with large models | Increase executor memory allocation |

Sources: [README.md:147-150](), [deep-learning/src/main/python/synapse/ml/dl/LitDeepTextModel.py:17-26](), [environment.yml:1-56]()