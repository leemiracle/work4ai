<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CryptoNets · page 6 Data Reference · fetched 2026-10-26 -->

# Data Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CifarCryptoNet/CifarBias.csv](CifarCryptoNet/CifarBias.csv)
- [CifarCryptoNet/CifarWeight.csv](CifarCryptoNet/CifarWeight.csv)
- [DataPreprocess/cal_test.tsv](DataPreprocess/cal_test.tsv)
- [DataPreprocess/cal_train.tsv](DataPreprocess/cal_train.tsv)

</details>



This page provides reference documentation for data files, model parameters, and file formats used throughout the CryptoNets system. It covers the structure and purpose of pre-trained neural network parameters, processed dataset files, and their relationships within the overall data processing pipeline.

For information about using these data files with specific neural network implementations, see [Neural Network Parameters](#6.1). For details about dataset preprocessing and conversion processes, see [Dataset Formats](#6.2).

## Data File Overview

The CryptoNets system uses several categories of data files to support privacy-preserving neural network inference:

- **Pre-trained Model Parameters**: CSV files containing weights and biases for trained neural networks
- **Processed Dataset Files**: TSV files containing preprocessed training and test data
- **Raw Dataset Sources**: Binary format datasets that are converted during preprocessing

## Data File Architecture

```mermaid
graph TB
    subgraph "Raw Data Sources"
        MNIST_Raw["MNIST Binary Files"]
        CIFAR_Raw["CIFAR-10 Binary Files"] 
        CAL_Raw["CalTech-101 Images"]
    end
    
    subgraph "Preprocessing Pipeline"
        DataPreprocess["DataPreprocess.exe"]
        GetMNIST["GetMNIST.cs"]
        GetCIFAR["GetCIFAR.cs"]
        GetCAL["GetCAL.cs"]
    end
    
    subgraph "Processed Data Files"
        subgraph "Model Parameters"
            CifarWeight["CifarWeight.csv<br/>Pre-trained Weights"]
            CifarBias["CifarBias.csv<br/>Layer Biases"]
        end
        
        subgraph "Dataset Files"
            MNIST_TSV["mnist-test.tsv"]
            CIFAR_TSV["cifar-test.tsv"]
            CAL_Train["cal_train.tsv<br/>1829 training samples"]
            CAL_Test["cal_test.tsv<br/>1010 test samples"]
        end
    end
    
    subgraph "Neural Network Applications"
        CryptoNets_App["CryptoNets.exe"]
        LowLatency_App["LowLatencyCryptoNets.exe"]
        CifarCrypto_App["CifarCryptoNets.exe"]
        Caltech_App["Caltech101.exe"]
    end
    
    MNIST_Raw --> GetMNIST
    CIFAR_Raw --> GetCIFAR
    CAL_Raw --> GetCAL
    
    GetMNIST --> DataPreprocess
    GetCIFAR --> DataPreprocess
    GetCAL --> DataPreprocess
    
    DataPreprocess --> MNIST_TSV
    DataPreprocess --> CIFAR_TSV
    DataPreprocess --> CAL_Train
    DataPreprocess --> CAL_Test
    DataPreprocess --> CifarWeight
    DataPreprocess --> CifarBias
    
    MNIST_TSV --> CryptoNets_App
    MNIST_TSV --> LowLatency_App
    CIFAR_TSV --> CifarCrypto_App
    CAL_Train --> Caltech_App
    CAL_Test --> Caltech_App
    CifarWeight --> CifarCrypto_App
    CifarBias --> CifarCrypto_App
```

**Sources**: [CifarCryptoNet/CifarBias.csv:1-4](), [CifarCryptoNet/CifarWeight.csv:1-1](), [DataPreprocess/cal_train.tsv:1-1829](), [DataPreprocess/cal_test.tsv:1-1010]()

## Pre-trained Model Parameters

### CIFAR-10 Neural Network Parameters

The CIFAR-10 CryptoNets implementation uses pre-trained parameters stored in CSV format:

| File | Purpose | Structure | Size |
|------|---------|-----------|------|
| `CifarWeight.csv` | Neural network weights | Single row of comma-separated values | ~21MB |
| `CifarBias.csv` | Layer bias parameters | 4 rows representing different layers | ~500 bytes |

#### Weight File Structure

The `CifarWeight.csv` file contains weights for the Low-Latency CryptoNets architecture in a flattened format:

```mermaid
graph LR
    subgraph "CifarWeight.csv Structure"
        WeightFile["CifarWeight.csv"]
        Row1["Row 1: All network weights<br/>Comma-separated values<br/>~4.2M parameters"]
    end
    
    subgraph "Layer Weight Mapping"
        ConvWeights["Convolutional Layer Weights"]
        DenseWeights["Dense Layer Weights"]
        PoolWeights["Pooling Layer Parameters"]
    end
    
    WeightFile --> Row1
    Row1 --> ConvWeights
    Row1 --> DenseWeights  
    Row1 --> PoolWeights
```

**Sources**: [CifarCryptoNet/CifarWeight.csv:1-1]()

#### Bias File Structure

The `CifarBias.csv` file contains bias parameters organized by network layer:

```mermaid
graph TB
    subgraph "CifarBias.csv Structure"
        BiasFile["CifarBias.csv"]
        Row1["Row 1: Layer 1 Biases<br/>83 values"]
        Row2["Row 2: Layer 2 Biases<br/>109 values"] 
        Row3["Row 3: Output Layer Biases<br/>10 values"]
        Row4["Row 4: Empty"]
    end
    
    BiasFile --> Row1
    BiasFile --> Row2
    BiasFile --> Row3
    BiasFile --> Row4
```

**Sources**: [CifarCryptoNet/CifarBias.csv:1-4]()

## Dataset File Formats

### CalTech-101 Dataset Files

The CalTech-101 dataset is processed into tab-separated value (TSV) format for use with the homomorphic encryption neural networks:

| File | Records | Purpose | Format |
|------|---------|---------|--------|
| `cal_train.tsv` | 1,829 | Training data | `<image_path>\t<class_id>` |
| `cal_test.tsv` | 1,010 | Test data | `<image_path>\t<class_id>` |

#### CalTech-101 TSV Format Specification

```mermaid
graph LR
    subgraph "TSV File Structure"
        TSVFile["cal_train.tsv / cal_test.tsv"]
        Format["Line Format:<br/>image_path\\tclass_id"]
        Example["accordion/image_0001.jpg\\t1"]
    end
    
    subgraph "Class Mapping"
        Classes["101 Object Classes<br/>1: accordion<br/>2: airplanes<br/>3: anchor<br/>...<br/>101: yin_yang"]
    end
    
    TSVFile --> Format
    Format --> Example
    Example --> Classes
```

**Sources**: [DataPreprocess/cal_train.tsv:1-1829](), [DataPreprocess/cal_test.tsv:1-1010]()

#### Class Distribution

The CalTech-101 dataset contains images organized into 101 object categories, with consistent naming conventions:

- **Training set**: 20 images per class (1,829 total after filtering)
- **Test set**: 10 images per class (1,010 total)
- **Image paths**: Format `<category>/<filename>.jpg`
- **Class IDs**: Sequential integers from 1 to 101

### Dataset Loading Pipeline

```mermaid
graph TB
    subgraph "Data Loading Process"
        TSVFile["Dataset TSV Files"]
        Parser["TSV Line Parser"]
        ImagePath["Extract Image Path"]
        ClassLabel["Extract Class Label"]
        Loader["Data Loader"]
    end
    
    subgraph "Neural Network Input"
        InputLayer["Network Input Layer"]
        EncryptLayer["EncryptLayer"]
        Processing["HE Processing Pipeline"]
    end
    
    TSVFile --> Parser
    Parser --> ImagePath
    Parser --> ClassLabel
    ImagePath --> Loader
    ClassLabel --> Loader
    Loader --> InputLayer
    InputLayer --> EncryptLayer
    EncryptLayer --> Processing
```

**Sources**: [DataPreprocess/cal_train.tsv:1-10](), [DataPreprocess/cal_test.tsv:1-10]()

## File Format Specifications

### CSV Parameter Files

- **Encoding**: UTF-8 text
- **Delimiter**: Comma (`,`)
- **Decimal format**: Standard floating-point notation
- **Line endings**: Platform-specific (`\r\n` on Windows)
- **Header**: None (data starts immediately)

### TSV Dataset Files  

- **Encoding**: UTF-8 text
- **Delimiter**: Tab character (`\t`)
- **Line format**: `<string>\t<integer>`
- **Line endings**: Platform-specific
- **Header**: None (data starts immediately)

## Data File Dependencies

The relationship between data files and neural network applications follows a specific dependency pattern:

| Application | Required Data Files | Purpose |
|-------------|-------------------|---------|
| `CifarCryptoNets.exe` | `CifarWeight.csv`, `CifarBias.csv`, `cifar-test.tsv` | CIFAR-10 inference with pre-trained model |
| `Caltech101.exe` | `cal_train.tsv`, `cal_test.tsv` | CalTech-101 classification |
| `CryptoNets.exe` | `mnist-test.tsv` | Original MNIST CryptoNets |
| `LowLatencyCryptoNets.exe` | `mnist-test.tsv` | Optimized MNIST inference |

**Sources**: [CifarCryptoNet/CifarBias.csv:1-4](), [CifarCryptoNet/CifarWeight.csv:1-1](), [DataPreprocess/cal_train.tsv:1-1829](), [DataPreprocess/cal_test.tsv:1-1010]()

---

