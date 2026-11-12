<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/NeuronBlocks · page 8 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Contributing.md](Contributing.md)
- [SECURITY.md](SECURITY.md)
- [autotest/tools/get_results.py](autotest/tools/get_results.py)

</details>



This document provides comprehensive guidance for developing, extending, and contributing to the NeuronBlocks toolkit. It covers the development ecosystem, contribution workflows, custom block creation, quality assurance processes, and security considerations.

For specific information about using existing blocks and models, see [Block Reference](#6). For examples of implementing different NLP tasks, see [Model Examples](#5).

## Development Ecosystem Overview

The NeuronBlocks development ecosystem is designed to support collaborative contributions while maintaining code quality and consistency. The framework provides structured processes for extending functionality through custom blocks and pre-configured models.

### Development Components

```mermaid
graph TB
    subgraph "Contribution Areas"
        ModelZoo["Model Zoo Contributions<br/>JSON Configuration Files"]
        BlockZoo["Block Zoo Contributions<br/>Neural Network Components"] 
        CoreFramework["Core Framework<br/>Base Classes & Utilities"]
    end
    
    subgraph "Development Tools" 
        RegisterScript["register_block.py<br/>Block Registration"]
        AutoTest["autotest/<br/>Quality Assurance"]
        BaseClasses["BaseLayer.py<br/>Foundation Classes"]
    end
    
    subgraph "Quality Gates"
        CLA["Contributor License Agreement<br/>Legal Compliance"]
        CodeReview["Pull Request Review<br/>Code Quality"]
        AutomatedTest["Automated Testing<br/>Functionality Verification"] 
    end
    
    subgraph "Documentation"
        ContribGuide["Contributing.md<br/>Contribution Guidelines"]
        SecurityPolicy["SECURITY.md<br/>Security Policies"]
        ExampleConfigs["model_zoo/<br/>Reference Implementations"]
    end
    
    ModelZoo --> RegisterScript
    BlockZoo --> RegisterScript  
    RegisterScript --> AutoTest
    AutoTest --> AutomatedTest
    
    ContribGuide --> CLA
    CLA --> CodeReview
    CodeReview --> AutomatedTest
    
    BaseClasses --> BlockZoo
    ExampleConfigs --> ModelZoo
    SecurityPolicy --> CodeReview
```

Sources: [Contributing.md:1-82](), [autotest/tools/get_results.py:1-51](), [SECURITY.md:1-42]()

### Contribution Workflow

The development process follows Microsoft's open source contribution model with specific adaptations for NeuronBlocks' modular architecture.

```mermaid
flowchart TD
    Start["Developer Identifies<br/>Enhancement Need"] --> Fork["Fork Repository<br/>Create Feature Branch"]
    Fork --> ContribType{"Contribution Type?"}
    
    ContribType -->|Model| ModelDev["Develop Model Configuration<br/>JSON Files in model_zoo/"]
    ContribType -->|Block| BlockDev["Implement Block Classes<br/>Configuration + Logic"]
    ContribType -->|Core| CoreDev["Modify Core Framework<br/>Base Classes or Utilities"]
    
    ModelDev --> Validate["Test Configuration<br/>Against Reference Tasks"]
    BlockDev --> Register["Run register_block.py<br/>Auto-register New Block"]  
    CoreDev --> CoreTest["Comprehensive Testing<br/>All Dependent Components"]
    
    Register --> BlockTest["Implement Block Tests<br/>Verify Functionality"]
    Validate --> DocUpdate["Update Documentation<br/>Usage Examples"]
    BlockTest --> DocUpdate
    CoreTest --> DocUpdate
    
    DocUpdate --> AutoTest["Run autotest/<br/>Quality Verification"]
    AutoTest --> TestPass{"All Tests Pass?"}
    
    TestPass -->|No| Debug["Debug Issues<br/>Fix Problems"]
    Debug --> AutoTest
    TestPass -->|Yes| PR["Create Pull Request<br/>Include Test Results"]
    
    PR --> CLA["Sign Contributor<br/>License Agreement"]
    CLA --> Review["Microsoft Team<br/>Code Review"]
    Review --> Merge["Merge to Main<br/>Integration Complete"]
```

Sources: [Contributing.md:4-11](), [Contributing.md:74-82]()

## Block Development Process

Creating custom blocks follows a structured three-step process that ensures consistency and integration with the existing framework.

### Block Architecture Components

```mermaid
graph TB
    subgraph "Block Implementation Requirements"
        ConfigClass["Configuration Class<br/>Inherits BaseLayer Config"]
        BlockClass["Block Class<br/>Inherits BaseLayer Block"] 
        Registration["Block Registration<br/>register_block.py"]
    end
    
    subgraph "Configuration Class Methods"
        DefaultMethod["default()<br/>Define Default Hyperparameters"]
        DeclareMethod["declare()<br/>Define Input/Output Specifications"]
        InferenceMethod["inference()<br/>Calculate Output Dimensions"]
        VerifyMethod["verify()<br/>Validate Configuration"]
    end
    
    subgraph "Block Class Methods"
        InitMethod["__init__()<br/>Initialize Block Attributes"]
        ForwardMethod["forward()<br/>Tensor Operation Logic"]
        Additional["Additional Methods<br/>Block-specific Functions"]
    end
    
    subgraph "Base Framework"
        BaseConfig["BaseLayer Configuration<br/>block_zoo/BaseLayer.py"]
        BaseBlock["BaseLayer Block<br/>block_zoo/BaseLayer.py"]
        Registry["Block Registry<br/>Auto-discovery System"]
    end
    
    ConfigClass --> DefaultMethod
    ConfigClass --> DeclareMethod
    ConfigClass --> InferenceMethod
    ConfigClass --> VerifyMethod
    
    BlockClass --> InitMethod
    BlockClass --> ForwardMethod
    BlockClass --> Additional
    
    BaseConfig --> ConfigClass
    BaseBlock --> BlockClass
    Registration --> Registry
    
    ConfigClass --> Registration
    BlockClass --> Registration
```

Sources: [Contributing.md:24-79]()

### Block Development Steps

| Step | Component | Requirements | Purpose |
|------|-----------|-------------|----------|
| 1 | Configuration Class | Inherit from BaseLayer, implement required methods | Define block behavior and validation |
| 2 | Block Implementation | Inherit from BaseLayer, implement `__init__` and `forward` | Implement tensor operations and logic |
| 3 | Registration | Run `register_block.py --block_name=new_block_name` | Auto-register for framework discovery |

The configuration class methods serve specific purposes:

- **`default()`**: Defines default hyperparameters read from JSON configuration files
- **`declare()`**: Specifies input ranks and number of inputs the block accepts  
- **`inference()`**: Calculates output dimensions based on input specifications
- **`verify()`**: Performs validation checks during model definition

Sources: [Contributing.md:27-60]()

## Quality Assurance Framework

The autotest system provides comprehensive quality assurance for contributions, ensuring functionality and performance standards are maintained.

### Automated Testing Pipeline

```mermaid
graph LR
    subgraph "Test Execution Environment"
        GPUTest["GPU Testing<br/>Training Pipeline"]
        CPUTest["CPU Testing<br/>Inference Pipeline"] 
        TestTasks["Reference Tasks<br/>Benchmark Datasets"]
    end
    
    subgraph "Test Coverage Areas"
        EnglishText["english_text_matching<br/>English NLP Tasks"]
        ChineseText["chinese_text_matching<br/>Chinese NLP Tasks"] 
        QuestionPairs["quora_question_pairs<br/>Question Similarity"]
        KnowledgeDist["knowledge_distillation<br/>Model Compression"]
    end
    
    subgraph "Results Processing"
        LogParsing["get_results.py<br/>Log File Analysis"]
        MetricCalc["calculate_AUC.py<br/>Performance Metrics"]
        Comparison["contrast_results.txt<br/>Performance Comparison"]
    end
    
    subgraph "Quality Gates"
        AccuracyThresh["Accuracy Thresholds<br/>Performance Baselines"]
        RegressionCheck["Regression Detection<br/>Performance Degradation"]
        TestStatus["Pass/Fail Status<br/>Contribution Approval"]
    end
    
    GPUTest --> EnglishText
    GPUTest --> ChineseText
    GPUTest --> QuestionPairs
    CPUTest --> EnglishText
    CPUTest --> ChineseText
    CPUTest --> QuestionPairs
    TestTasks --> KnowledgeDist
    
    EnglishText --> LogParsing
    ChineseText --> LogParsing
    QuestionPairs --> LogParsing
    KnowledgeDist --> MetricCalc
    
    LogParsing --> Comparison
    MetricCalc --> Comparison
    Comparison --> AccuracyThresh
    AccuracyThresh --> RegressionCheck
    RegressionCheck --> TestStatus
```

Sources: [autotest/tools/get_results.py:4-50]()

### Test Result Analysis

The automated testing system processes results from multiple task configurations and compares them against established baselines:

| Task | Baseline Performance | Test Environment | Metric |
|------|---------------------|------------------|---------|
| English Text Matching | 0.96655 | GPU/CPU | Accuracy |
| Chinese Text Matching | 0.70001 | GPU/CPU | Accuracy |
| Quora Question Pairs | 0.72596 | GPU/CPU | Accuracy |
| Knowledge Distillation | 0.66329 | CPU | AUC |

The testing framework extracts performance metrics from log files and generates comparison reports in `contrast_results.txt` to detect performance regressions.

Sources: [autotest/tools/get_results.py:7-50]()

## Security Considerations

NeuronBlocks follows Microsoft's comprehensive security policies and coordinated vulnerability disclosure principles.

### Security Reporting Process

```mermaid
flowchart TD
    Discovery["Security Vulnerability<br/>Discovered"] --> Assessment["Assess Vulnerability<br/>Against Microsoft Definition"]
    Assessment --> Private["Report Privately<br/>Do NOT Use GitHub Issues"]
    
    Private --> MSRC["Microsoft Security<br/>Response Center (MSRC)"]
    Private --> Email["secure@microsoft.com<br/>Direct Email Reporting"]
    
    MSRC --> Response["24-Hour Response<br/>Acknowledgment"]
    Email --> Response
    
    Response --> Investigation["Security Team<br/>Investigation Process"]
    Investigation --> Disclosure["Coordinated<br/>Vulnerability Disclosure"]
    
    subgraph "Required Information"
        IssueType["Issue Type<br/>Buffer Overflow, Injection, etc."]
        SourceFiles["Affected Source Files<br/>Full Paths"]
        Location["Source Code Location<br/>Tag/Branch/Commit"]
        Reproduction["Reproduction Steps<br/>Configuration Requirements"]
        Impact["Security Impact<br/>Exploitation Scenarios"]
    end
    
    Discovery --> IssueType
    IssueType --> SourceFiles
    SourceFiles --> Location
    Location --> Reproduction
    Reproduction --> Impact
    Impact --> Private
```

Sources: [SECURITY.md:9-40]()

### Security Best Practices

- **Never report security vulnerabilities through public GitHub issues**
- **Encrypt sensitive communications** using Microsoft's PGP key when possible
- **Provide comprehensive details** including proof-of-concept code and impact analysis
- **Follow coordinated disclosure** principles to protect users during remediation

The security framework emphasizes protecting user data and maintaining system integrity while supporting the open-source development model.

Sources: [SECURITY.md:11-39]()

---

