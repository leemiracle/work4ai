<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CryptoNets · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DataPreprocess/GetCIFAR.cs](DataPreprocess/GetCIFAR.cs)
- [HE Wrapper/RawMatrix.cs](HE Wrapper/RawMatrix.cs)
- [NeuralNetworks/LLConvReader.cs](NeuralNetworks/LLConvReader.cs)
- [README.md](README.md)

</details>



This document provides a comprehensive overview of the CryptoNets system architecture, covering the three core architectural components and their interactions. CryptoNets enables privacy-preserving neural network inference using homomorphic encryption through a layered architecture that abstracts cryptographic operations while maintaining computational efficiency.

For information about specific neural network implementations and their performance characteristics, see [Neural Network Implementations](#3). For usage instructions and command-line parameters, see [Usage and Examples](#4).

## Core Architectural Components

The CryptoNets system is built around three fundamental architectural layers that work together to enable homomorphic encryption-based neural network inference:

### Three-Layer Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        CryptoNets["CryptoNets.exe<br/>Original MNIST"]
        LowLatency["LowLatencyCryptoNets.exe<br/>LoLa Variants"]
        CifarCrypto["CifarCryptoNets.exe<br/>CIFAR-10 LoLa"]
        Caltech101["Caltech101.exe<br/>CalTech-101 LoLa"]
        BasicExample["BasicExample.exe<br/>HE Operations Demo"]
    end
    
    subgraph "Neural Network Framework Layer"
        BaseLayer["BaseLayer<br/>Abstract Base"]
        LLConvReader["LLConvReader<br/>Input Processing"]
        LLPoolLayer["LLPoolLayer<br/>Convolution + Pooling"]
        LLDenseLayer["LLDenseLayer<br/>Fully Connected"]
        SquareActivation["SquareActivation<br/>f(x) = x²"]
        TimingLayer["TimingLayer<br/>Performance Measurement"]
        EncryptLayer["EncryptLayer<br/>Data Encryption"]
    end
    
    subgraph "HE Wrapper Layer"
        IFactory["IFactory<br/>Factory Interface"]
        RawFactory["RawFactory<br/>Plaintext Operations"]
        EncryptedSealBfvFactory["EncryptedSealBfvFactory<br/>Encrypted Operations"]
        RawMatrix["RawMatrix<br/>Plaintext Matrix Ops"]
        EncryptedSealBfvMatrix["EncryptedSealBfvMatrix<br/>Encrypted Matrix Ops"]
        RawVector["RawVector<br/>Plaintext Vector Ops"]
        EncryptedSealBfvVector["EncryptedSealBfvVector<br/>Encrypted Vector Ops"]
    end
    
    subgraph "External Dependencies"
        SEAL["Microsoft SEAL 3.2<br/>BFV Encryption Scheme"]
        MathNet["MathNet.Numerics<br/>Linear Algebra"]
    end
    
    %% Application dependencies
    CryptoNets --> BaseLayer
    LowLatency --> BaseLayer
    CifarCrypto --> BaseLayer
    Caltech101 --> BaseLayer
    BasicExample --> IFactory
    
    %% Neural network layer dependencies
    BaseLayer --> IFactory
    LLConvReader --> IFactory
    LLPoolLayer --> IFactory
    LLDenseLayer --> IFactory
    SquareActivation --> IFactory
    TimingLayer --> IFactory
    EncryptLayer --> IFactory
    
    %% HE wrapper internal structure
    IFactory --> RawFactory
    IFactory --> EncryptedSealBfvFactory
    RawFactory --> RawMatrix
    RawFactory --> RawVector
    EncryptedSealBfvFactory --> EncryptedSealBfvMatrix
    EncryptedSealBfvFactory --> EncryptedSealBfvVector
    
    %% External dependencies
    EncryptedSealBfvFactory --> SEAL
    RawMatrix --> MathNet
    RawVector --> MathNet
```

Sources: [README.md:14-17](), [HE Wrapper/RawMatrix.cs:12-13](), [NeuralNetworks/LLConvReader.cs:12]()

## Component 1: Homomorphic Encryption Wrapper

The HE Wrapper provides a unified interface for matrix and vector operations that can operate on both plaintext and encrypted data. This abstraction allows the neural network layers to be encryption-agnostic.

### Factory Pattern Implementation

```mermaid
graph TB
    subgraph "Factory Interface"
        IFactory["IFactory<br/>Abstract Factory"]
    end
    
    subgraph "Concrete Factories"
        RawFactory["RawFactory<br/>Plaintext Implementation"]
        EncryptedSealBfvFactory["EncryptedSealBfvFactory<br/>SEAL BFV Implementation"]
    end
    
    subgraph "Matrix/Vector Types"
        IMatrix["IMatrix Interface"]
        IVector["IVector Interface"]
        RawMatrix["RawMatrix<br/>MathNet.Numerics backend"]
        RawVector["RawVector<br/>MathNet.Numerics backend"]
        EncryptedSealBfvMatrix["EncryptedSealBfvMatrix<br/>SEAL Ciphertext backend"]
        EncryptedSealBfvVector["EncryptedSealBfvVector<br/>SEAL Ciphertext backend"]
    end
    
    IFactory --> RawFactory
    IFactory --> EncryptedSealBfvFactory
    
    RawFactory --> RawMatrix
    RawFactory --> RawVector
    EncryptedSealBfvFactory --> EncryptedSealBfvMatrix
    EncryptedSealBfvFactory --> EncryptedSealBfvVector
    
    RawMatrix --> IMatrix
    RawVector --> IVector
    EncryptedSealBfvMatrix --> IMatrix
    EncryptedSealBfvVector --> IVector
```

The `RawMatrix` class implements core matrix operations using `MathNet.Numerics.LinearAlgebra` as the computational backend. Key operations include:

| Operation | Method | Purpose |
|-----------|--------|---------|
| Matrix-Vector Multiplication | `Mul(IVector v, IComputationEnvironment env)` | Core neural network computation |
| Element-wise Multiplication | `ElementWiseMultiply(IMatrix m, IComputationEnvironment env)` | Activation functions |
| Matrix Addition | `Add(IMatrix m, IComputationEnvironment env)` | Bias addition |
| Matrix Interleaving | `Interleave(int shift, IComputationEnvironment env)` | Convolution operations |

Sources: [HE Wrapper/RawMatrix.cs:12-174](), [README.md:15]()

## Component 2: Neural Network Framework

The neural network framework provides layer implementations that operate transparently on both encrypted and plaintext data through the HE Wrapper interface.

### Layer Hierarchy and Specialization

```mermaid
graph TB
    subgraph "Base Framework"
        BaseLayer["BaseLayer<br/>Abstract base class"]
        IInputLayer["IInputLayer<br/>Input layer interface"]
        INetwork["INetwork<br/>Network interface"]
    end
    
    subgraph "Input/Output Layers"
        LLConvReader["LLConvReader<br/>Convolution input reader<br/>TSV file processing"]
        EncryptLayer["EncryptLayer<br/>Data encryption layer"]
        TimingLayer["TimingLayer<br/>Performance measurement"]
    end
    
    subgraph "Computation Layers"
        LLPoolLayer["LLPoolLayer<br/>Convolution + Pooling<br/>Bias support"]
        LLVectorizeLayer["LLVectorizeLayer<br/>Tensor flattening"]
        LLDenseLayer["LLDenseLayer<br/>Fully connected layer"]
        SquareActivation["SquareActivation<br/>x² activation function"]
    end
    
    BaseLayer --> LLConvReader
    BaseLayer --> EncryptLayer
    BaseLayer --> TimingLayer
    BaseLayer --> LLPoolLayer
    BaseLayer --> LLVectorizeLayer
    BaseLayer --> LLDenseLayer
    BaseLayer --> SquareActivation
    
    IInputLayer --> LLConvReader
    INetwork --> BaseLayer
```

The `LLConvReader` class demonstrates the framework's approach to input processing, supporting both sparse and dense data formats while handling convolution-specific data layout:

- **Sparse Format**: `label:dimension:index:value` pairs from TSV files
- **Dense Format**: Tab-separated values with configurable label column
- **Convolution Mapping**: Transforms input vectors into convolution matrices using `ConvolutionEngine`

Sources: [NeuralNetworks/LLConvReader.cs:12-164](), [README.md:16]()

## Component 3: Application Implementations

The application layer contains specific neural network implementations that combine the HE Wrapper and Neural Network Framework to solve different classification problems.

### Application Architecture and Data Flow

```mermaid
graph LR
    subgraph "Data Sources"
        MNIST_TSV["mnist-test.tsv<br/>28x28 grayscale"]
        CIFAR_TSV["cifar-test.tsv<br/>32x32 RGB"]
        CALTECH_TSV["cal_test.tsv<br/>AlexNet features"]
        PretrainedWeights["CifarWeight.csv<br/>CifarBias.csv"]
    end
    
    subgraph "Applications"
        CryptoNetsExe["CryptoNets.exe<br/>Original architecture"]
        LowLatencyExe["LowLatencyCryptoNets.exe<br/>LoLa variants"]
        CifarCryptoExe["CifarCryptoNets.exe<br/>76.31% accuracy"]
        Caltech101Exe["Caltech101.exe<br/>156-234s inference"]
    end
    
    subgraph "Network Variants"
        LoLa["LoLa<br/>Base variant"]
        LoLaDense["LoLaDense<br/>Dense layers"]
        LoLaSmall["LoLaSmall<br/>Compact model"]
        LoLaLarge["LoLaLarge<br/>High capacity"]
    end
    
    MNIST_TSV --> CryptoNetsExe
    MNIST_TSV --> LowLatencyExe
    CIFAR_TSV --> CifarCryptoExe
    PretrainedWeights --> CifarCryptoExe
    CALTECH_TSV --> Caltech101Exe
    
    LowLatencyExe --> LoLa
    LowLatencyExe --> LoLaDense
    LowLatencyExe --> LoLaSmall
    LowLatencyExe --> LoLaLarge
```

### Performance Characteristics

| Application | Dataset | Inference Time | Accuracy | Key Features |
|-------------|---------|----------------|----------|--------------|
| `CryptoNets.exe` | MNIST | ~27 seconds | 98.7% | Original architecture, SEAL 3.2 |
| `LowLatencyCryptoNets.exe` | MNIST | ~2000ms | High | Multiple LoLa variants |
| `CifarCryptoNets.exe` | CIFAR-10 | ~740 seconds | 76.31% | Color image classification |
| `Caltech101.exe` | CalTech-101 | 156-234 seconds | Varies | Object recognition |

Sources: [README.md:19-21](), [README.md:136-139](), [README.md:148-171]()

## System Execution Flow

The system follows a consistent execution pattern across all applications, with mode selection determining whether operations occur on plaintext or encrypted data.

### Execution Mode Selection

```mermaid
graph TB
    subgraph "Initialization"
        AppStart["Application Start"]
        ParseArgs["Parse Command Line Args<br/>-e flag for encryption"]
        CreateFactory["Create Factory Instance"]
    end
    
    subgraph "Factory Selection"
        CheckEncrypted{"Encryption Mode?"}
        RawFactoryCreate["RawFactory.GetInstance()<br/>Plaintext operations"]
        EncryptedFactoryCreate["EncryptedSealBfvFactory.GetInstance()<br/>Generate SEAL keys"]
    end
    
    subgraph "Data Processing"
        LoadData["Load TSV Data<br/>LLConvReader"]
        ProcessLayers["Execute Layer Chain<br/>BaseLayer.Apply()"]
        OutputResults["Display Results<br/>Accuracy metrics"]
    end
    
    AppStart --> ParseArgs
    ParseArgs --> CreateFactory
    CreateFactory --> CheckEncrypted
    
    CheckEncrypted -->|No encryption| RawFactoryCreate
    CheckEncrypted -->|Use encryption| EncryptedFactoryCreate
    
    RawFactoryCreate --> LoadData
    EncryptedFactoryCreate --> LoadData
    
    LoadData --> ProcessLayers
    ProcessLayers --> OutputResults
```

### Layer Execution Chain

The neural network layers execute in a pipeline, with each layer's output becoming the next layer's input:

1. **`LLConvReader`**: Reads TSV data and converts to convolution format
2. **`EncryptLayer`** (encrypted mode only): Encrypts input data
3. **`LLPoolLayer`**: Applies convolution and pooling operations  
4. **`SquareActivation`**: Applies polynomial activation function
5. **`LLDenseLayer`**: Performs fully connected layer computation
6. **`TimingLayer`**: Records performance metrics

Sources: [README.md:82-104](), [README.md:117-132](), [DataPreprocess/GetCIFAR.cs:32-53]()

## Data Preprocessing Integration

The system includes a comprehensive data preprocessing pipeline implemented in `DataPreprocess.exe` that prepares datasets for the neural network applications.

### Preprocessing Pipeline Architecture

```mermaid
graph LR
    subgraph "Raw Data Sources"
        MNIST_Binary["MNIST Binary Files<br/>IDX format"]
        CIFAR_Binary["cifar-10-binary.tar.gz<br/>Binary batch files"]
        CALTECH_Images["CalTech-101 Images<br/>JPEG format"]
    end
    
    subgraph "Preprocessing Components"
        GetMNIST["GetMNIST.cs<br/>IDX to TSV conversion"]
        GetCIFAR["GetCIFAR.cs<br/>Binary to TSV conversion"]
        GetCAL["GetCAL.cs<br/>AlexNet feature extraction"]
    end
    
    subgraph "ML.NET Pipeline"
        ImageAnalytics["ImageAnalytics<br/>Image loading"]
        AlexNetONNX["AlexNet ONNX Model<br/>Feature extraction"]
        MLContext["Microsoft.ML<br/>Pipeline execution"]
    end
    
    subgraph "Output Data"
        MNIST_TSV["mnist-test.tsv<br/>Normalized pixel values"]
        CIFAR_TSV["cifar-test.tsv<br/>RGB channel data"]
        CALTECH_TSV["cal_test.tsv<br/>4096D feature vectors"]
        PretrainedParams["CifarWeight.csv<br/>CifarBias.csv<br/>Network parameters"]
    end
    
    MNIST_Binary --> GetMNIST
    CIFAR_Binary --> GetCIFAR
    CALTECH_Images --> GetCAL
    
    GetMNIST --> MNIST_TSV
    GetCIFAR --> CIFAR_TSV
    GetCAL --> ImageAnalytics
    
    ImageAnalytics --> AlexNetONNX
    AlexNetONNX --> MLContext
    MLContext --> CALTECH_TSV
    MLContext --> PretrainedParams
```

The `GetCIFAR` class exemplifies the preprocessing approach, reading binary data and converting it to the TSV format expected by the neural network layers. The conversion process handles the CIFAR-10 data layout where each record contains a label byte followed by 3072 bytes (32×32×3 RGB values).

Sources: [DataPreprocess/GetCIFAR.cs:14-54](), [README.md:50-52]()

---

