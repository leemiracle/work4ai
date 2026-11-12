<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CryptoNets · page 5 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [HE Wrapper Tests/HE Wrapper Tests.csproj](HE Wrapper Tests/HE Wrapper Tests.csproj)
- [NeuralNetworksTest/NeuralNetworksTest.csproj](NeuralNetworksTest/NeuralNetworksTest.csproj)

</details>



This document provides essential information for developers working on the CryptoNets codebase, covering the testing framework architecture, build configurations, and project structure. It details the MSTest-based test suites and their dependencies across the neural network and homomorphic encryption components.

For information about using the applications, see [Usage and Examples](#4). For details about the specific testing framework implementation, see [Testing Framework](#5.1).

## Testing Architecture Overview

The CryptoNets repository implements a comprehensive testing strategy using two primary test projects that validate both the neural network implementations and the homomorphic encryption wrapper functionality.

### Test Project Structure

```mermaid
graph TB
    subgraph "Test Projects"
        NeuralNetTest["NeuralNetworksTest<br/>Main Test Suite"]
        HEWrapperTest["HE Wrapper Tests<br/>Encryption Tests"]
    end
    
    subgraph "Test Classes"
        LayersTest["LayersTest.cs<br/>Unit Tests"]
        CaltechTests["CaltechTests.cs<br/>Integration Tests"]
        TestNetwork["TestNetwork.cs<br/>Architecture Tests"]
        FakeLayer["FakeLayer.cs<br/>Mock Layer"]
        
        BasicOps["BasicOperations.cs<br/>HE Operations"]
        BasicRawOps["BasicRawOperations.cs<br/>Raw HE Tests"]
        BudgetAnalysis["BudgetAnalysis.cs<br/>Encryption Budget"]
    end
    
    subgraph "Projects Under Test"
        NeuralNetworks["NeuralNetworks<br/>Core Framework"]
        HEWrapper["HE Wrapper<br/>Encryption Layer"]
        CryptoNets["CryptoNets<br/>Original Implementation"]
        LowLatency["LowLatencyCryptoNets<br/>LoLa Variants"]
        Caltech101["Caltech101<br/>CalTech Implementation"]
    end
    
    NeuralNetTest --> LayersTest
    NeuralNetTest --> CaltechTests
    NeuralNetTest --> TestNetwork
    NeuralNetTest --> FakeLayer
    
    HEWrapperTest --> BasicOps
    HEWrapperTest --> BasicRawOps
    HEWrapperTest --> BudgetAnalysis
    
    LayersTest --> NeuralNetworks
    CaltechTests --> Caltech101
    TestNetwork --> CryptoNets
    TestNetwork --> LowLatency
    
    BasicOps --> HEWrapper
    BasicRawOps --> HEWrapper
    BudgetAnalysis --> HEWrapper
```

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:82-86](), [HE Wrapper Tests/HE Wrapper Tests.csproj:81-84](), [NeuralNetworksTest/NeuralNetworksTest.csproj:92-111](), [HE Wrapper Tests/HE Wrapper Tests.csproj:90-93]()

### Build Configuration Matrix

The test projects support multiple build configurations to accommodate different development and deployment scenarios:

| Configuration | Platform | Target Directory | Purpose |
|---------------|----------|------------------|---------|
| Debug | AnyCPU | `bin\Debug\` | Development testing |
| Release | AnyCPU | `bin\Release\` | Performance validation |
| Debug | x64 | `..\bin\x64\Debug\` | 64-bit debugging |
| Release | x64 | `..\bin\x64\Release\` | Production testing |

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:24-58](), [HE Wrapper Tests/HE Wrapper Tests.csproj:24-58]()

## Framework Dependencies

Both test projects utilize a consistent set of dependencies for mathematical operations, testing infrastructure, and homomorphic encryption:

### Core Testing Dependencies

```mermaid
graph LR
    subgraph "Testing Framework"
        MSTestFramework["Microsoft.VisualStudio.TestPlatform.TestFramework<br/>Version 14.0.0.0"]
        MSTestAdapter["MSTest.TestAdapter<br/>Version 1.4.0"]
    end
    
    subgraph "Mathematical Libraries"
        MathNet["MathNet.Numerics<br/>Version 4.8.1.0"]
        MathNetText["MathNet.Numerics.Data.Text<br/>Version 4.0.0.0"]
        MathNetMKL["MathNet.Numerics.MKL.Win-x64<br/>Version 2.3.0"]
    end
    
    subgraph "Encryption Libraries"
        SEALNet["SEALNet / SEALNET<br/>Microsoft SEAL 3.2.0"]
    end
    
    subgraph "System Libraries"
        SystemCore["System.Core"]
        SystemNumerics["System.Numerics"]
        SystemSerialization["System.Runtime.Serialization"]
    end
    
    MSTestFramework --> MSTestAdapter
    MathNet --> MathNetText
    MathNet --> MathNetMKL
```

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:60-79](), [HE Wrapper Tests/HE Wrapper Tests.csproj:60-78]()

### Target Framework and Platform Requirements

Both test projects target `.NET Framework 4.6.2` and require specific platform configurations:

- **Target Framework:** `v4.6.2`
- **Supported Platforms:** AnyCPU, x64
- **Project Type:** Unit Test Library
- **Visual Studio Compatibility:** 15.0+

The x64 platform requirement is particularly important for the Microsoft SEAL homomorphic encryption library integration.

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:12-22](), [HE Wrapper Tests/HE Wrapper Tests.csproj:12-22]()

## Project Reference Architecture

### NeuralNetworksTest Dependencies

The main test project references all primary application projects to enable comprehensive integration testing:

```mermaid
graph TB
    NeuralNetworksTest["NeuralNetworksTest<br/>{D72F29C5-0854-4AD1-9BD0-D91F4D520FF3}"]
    
    subgraph "Referenced Projects"
        Caltech101Proj["{21CBCF79-9ACB-407A-8CD4-392DDCF9AF2A}<br/>Caltech101"]
        CryptoNetsProj["{736d8cb8-353d-4e07-9770-7e34f7f41be1}<br/>CryptoNets"]  
        LowLatencyProj["{fa3ec7c0-907c-4369-acc0-1493c2fde3f3}<br/>LowLatencyCryptoNets"]
        NeuralNetworksProj["{ea13024b-33c1-4659-83f7-99d87031c5df}<br/>NeuralNetworks"]
        HEWrapperProj["{23ab097c-fd1f-451b-b5dc-875e09e5699a}<br/>HE Wrapper"]
    end
    
    NeuralNetworksTest --> Caltech101Proj
    NeuralNetworksTest --> CryptoNetsProj
    NeuralNetworksTest --> LowLatencyProj
    NeuralNetworksTest --> NeuralNetworksProj
    NeuralNetworksTest --> HEWrapperProj
```

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:92-111]()

### HE Wrapper Tests Dependencies

The HE Wrapper test project maintains a focused scope, testing only the homomorphic encryption functionality:

```mermaid
graph TB
    HEWrapperTests["HE Wrapper Tests<br/>{F2D7CEB5-466E-42E9-A6D7-C9EA7E4F1FAB}"]
    
    HEWrapperProj["{23ab097c-fd1f-451b-b5dc-875e09e5699a}<br/>HE Wrapper"]
    
    HEWrapperTests --> HEWrapperProj
```

**Sources:** [HE Wrapper Tests/HE Wrapper Tests.csproj:90-93]()

## Development Environment Setup

### Required NuGet Packages

Developers must ensure the following NuGet packages are properly restored before building:

| Package | Version | Purpose |
|---------|---------|---------|
| `MSTest.TestFramework` | 1.4.0 | Unit testing framework |
| `MSTest.TestAdapter` | 1.4.0 | Test discovery and execution |
| `MathNet.Numerics` | 4.8.1 | Mathematical computations |
| `MathNet.Numerics.Data.Text` | 4.0.0 | Data I/O operations |
| `MathNet.Numerics.MKL.Win-x64` | 2.3.0 | Intel MKL optimization |
| `Microsoft.Research.SEALNet` | 3.2.0 | Homomorphic encryption |

### Build Targets and Validation

The project includes automatic validation for missing NuGet packages and required build targets:

- **MathNet MKL Target:** `..\packages\MathNet.Numerics.MKL.Win-x64.2.3.0\build\MathNet.Numerics.MKL.Win-x64.targets`
- **MSTest Adapter Targets:** `..\packages\MSTest.TestAdapter.1.4.0\build\net45\MSTest.TestAdapter.targets`
- **SEAL Target:** `..\packages\Microsoft.Research.SEALNet.3.2.0\build\Microsoft.Research.SEALNet.targets`

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:115-124](), [HE Wrapper Tests/HE Wrapper Tests.csproj:97-108]()

## Code Analysis and Quality

Both test projects are configured with `MinimumRecommendedRules.ruleset` for code analysis, ensuring consistent code quality standards across the development team.

**Sources:** [NeuralNetworksTest/NeuralNetworksTest.csproj:48-57](), [HE Wrapper Tests/HE Wrapper Tests.csproj:48-57]()

---

